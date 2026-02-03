"""Cliente HTTP con retry, caching y manejo de errores robusto."""

from __future__ import annotations

import logging
from typing import Tuple

import requests
from requests_cache import CachedSession
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)
from w3lib.html import get_base_url

logger = logging.getLogger(__name__)

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; SchemaAutomation/1.0)",
}

# Cache de 15 minutos para evitar requests repetidos
_session = CachedSession(
    "schema_automation_cache",
    expire_after=900,  # 15 minutos
    allowable_codes=[200],
    stale_if_error=True,
)


class FetchError(Exception):
    """Error base para operaciones de fetch."""

    def __init__(self, message: str, url: str, status_code: int | None = None):
        self.url = url
        self.status_code = status_code
        super().__init__(message)


class PageNotFoundError(FetchError):
    """La página solicitada no existe (404)."""

    def __init__(self, url: str):
        super().__init__(f"Página no encontrada: {url}", url, 404)


class ServerError(FetchError):
    """Error del servidor (5xx)."""

    def __init__(self, url: str, status_code: int):
        super().__init__(f"Error del servidor ({status_code}): {url}", url, status_code)


class RateLimitError(FetchError):
    """Límite de tasa excedido (429)."""

    def __init__(self, url: str):
        super().__init__(f"Rate limit excedido: {url}", url, 429)


def _is_retryable_error(exception: BaseException) -> bool:
    """Determina si un error es recuperable mediante retry."""
    if isinstance(exception, requests.exceptions.ConnectionError):
        return True
    if isinstance(exception, requests.exceptions.Timeout):
        return True
    if isinstance(exception, ServerError):
        return True
    if isinstance(exception, RateLimitError):
        return True
    return False


@retry(
    retry=retry_if_exception_type((
        requests.exceptions.ConnectionError,
        requests.exceptions.Timeout,
        ServerError,
        RateLimitError,
    )),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True,
)
def fetch_html(url: str, timeout: int = 25, use_cache: bool = True) -> Tuple[str, str, str]:
    """
    Descarga el HTML de una página con retry automático y caching.

    Args:
        url: URL de la página a descargar.
        timeout: Tiempo máximo de espera en segundos.
        use_cache: Si True, usa el cache para evitar requests repetidos.

    Returns:
        Tupla de (html, base_url, final_url).

    Raises:
        PageNotFoundError: Si la página no existe (404).
        ServerError: Si el servidor devuelve un error 5xx.
        RateLimitError: Si se excede el rate limit (429).
        FetchError: Para otros errores HTTP.
        requests.exceptions.ConnectionError: Si no se puede conectar.
        requests.exceptions.Timeout: Si se excede el timeout.
    """
    session = _session if use_cache else requests

    logger.debug("Fetching URL: %s (cache=%s)", url, use_cache)

    try:
        response = session.get(url, headers=DEFAULT_HEADERS, timeout=timeout)
    except requests.exceptions.ConnectionError as e:
        logger.warning("Connection error for %s: %s", url, e)
        raise
    except requests.exceptions.Timeout as e:
        logger.warning("Timeout for %s: %s", url, e)
        raise

    status_code = response.status_code

    if status_code == 404:
        raise PageNotFoundError(url)
    elif status_code == 429:
        raise RateLimitError(url)
    elif 500 <= status_code < 600:
        raise ServerError(url, status_code)
    elif status_code >= 400:
        raise FetchError(f"HTTP {status_code}: {url}", url, status_code)

    html = response.text
    base_url = get_base_url(html, response.url)
    final_url = response.url

    # Log cache hit/miss info si está disponible
    from_cache = getattr(response, "from_cache", False)
    logger.debug(
        "Fetched %s (base=%s, status=%d, cached=%s)",
        final_url,
        base_url,
        status_code,
        from_cache,
    )

    return html, base_url, final_url


def clear_cache() -> None:
    """Limpia el cache de requests."""
    _session.cache.clear()
    logger.info("HTTP cache cleared")


def get_cache_stats() -> dict:
    """Retorna estadísticas del cache."""
    return {
        "size": len(_session.cache.responses),
        "urls": list(_session.cache.responses.keys())[:10],  # Primeras 10 URLs
    }
