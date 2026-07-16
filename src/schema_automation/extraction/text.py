"""Funciones de limpieza de texto provenientes del DOM."""

from __future__ import annotations

import re
import unicodedata
from typing import Optional

from bs4 import BeautifulSoup, Tag

WHITESPACE_RE = re.compile(r"\s+")


def clean_text(value: str) -> str:
    """Normaliza espacios y caracteres invisibles en un string."""
    normalized = unicodedata.normalize("NFKC", value or "")
    normalized = normalized.replace("\xa0", " ").replace("\u200b", "")
    normalized = WHITESPACE_RE.sub(" ", normalized)
    return normalized.strip()


def extract_flat_text(body: Optional[Tag]) -> str:
    """Devuelve el texto de un nodo HTML en una sola línea limpia."""
    if body is None:
        return ""

    kill = (
        "script,style,noscript,template,svg,canvas,iframe,"
        "form,button,select,input,textarea,header,footer,nav"
    )
    for el in body.select(kill):
        el.decompose()

    for br in body.find_all(["br", "hr"]):
        br.replace_with(" ")

    return clean_text(body.get_text(" ", strip=True))


def extract_body_text(soup: BeautifulSoup) -> str:
    """Extrae el texto del cuerpo del artículo desde el DOM.

    Las páginas de Naranja X (Angular + Contentful) reparten el contenido en
    varios ``<article class="rich-text">`` — un bloque por sección editada en el
    CMS. Tomar solo el primero (como hacía el selector anterior) devolvía apenas
    la introducción, así que se concatena el texto de todos los bloques en orden
    de documento.

    Se filtra por la clase ``rich-text`` a propósito: es el contenedor exacto de
    contenido del CMS. Otros ``<article>`` de la página (tarjetas de "seguí
    leyendo", relacionados) quedan fuera del ``articleBody``.

    Fallback para estructuras sin ``rich-text``: primer ``<article>``, ``main``,
    ``[role='main']`` y por último ``body``.
    """
    rich_blocks = soup.select("article.rich-text")
    if rich_blocks:
        joined = " ".join(
            text for text in (extract_flat_text(block) for block in rich_blocks) if text
        )
        if joined:
            return joined

    for selector in ("article", "main", "[role='main']"):
        node = soup.select_one(selector)
        if isinstance(node, Tag) and node.get_text(strip=True):
            return extract_flat_text(node)

    return extract_flat_text(soup.body) if soup.body else ""
