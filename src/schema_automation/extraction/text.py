"""Funciones de limpieza de texto provenientes del DOM."""

from __future__ import annotations

import re
import unicodedata
from typing import Optional

from bs4 import Tag

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
