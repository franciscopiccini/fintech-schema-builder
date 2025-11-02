"""Extracción de metadatos básicos de una página HTML."""

from __future__ import annotations

from typing import Dict, Optional
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from .html import ensure_soup


def extract_basic_meta(
    html: str,
    *,
    base_url: Optional[str] = None,
    soup: Optional[BeautifulSoup] = None,
) -> Dict[str, str]:
    """Obtiene título, descripción e imagen preferida de la página."""
    soup = soup or ensure_soup(html)

    def meta(name: Optional[str] = None, prop: Optional[str] = None) -> str:
        if name:
            tag = soup.find("meta", attrs={"name": name})
        elif prop:
            tag = soup.find("meta", attrs={"property": prop})
        else:
            tag = None
        if tag is None:
            return ""
        content = tag.get("content")
        return content.strip() if content else ""

    title = soup.title.string.strip() if soup.title and soup.title.string else ""
    og_title = meta(prop="og:title")
    if og_title:
        title = og_title

    description = meta(name="description") or meta(prop="og:description")
    image = meta(prop="og:image")

    if base_url and image:
        image = urljoin(base_url, image)

    return {"title": title, "description": description, "image": image}
