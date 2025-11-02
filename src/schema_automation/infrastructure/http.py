"""Cliente HTTP mínimo para obtener el HTML fuente."""

from __future__ import annotations

import logging
from typing import Tuple

import requests
from w3lib.html import get_base_url

logger = logging.getLogger(__name__)

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; SchemaAutomation/1.0)",
}


def fetch_html(url: str, timeout: int = 25) -> Tuple[str, str, str]:
    """Descarga el HTML de una página y devuelve (html, base_url, final_url)."""
    response = requests.get(url, headers=DEFAULT_HEADERS, timeout=timeout)
    response.raise_for_status()
    html = response.text
    base_url = get_base_url(html, response.url)
    final_url = response.url
    logger.debug("Fetched %s (base=%s)", final_url, base_url)
    return html, base_url, final_url
