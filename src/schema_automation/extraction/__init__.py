"""Utilidades de extracción de contenido desde HTML."""

from .meta import extract_basic_meta
from .text import extract_flat_text
from .faqs import extract_faqs, extract_faqs_from_nx_accordion, extract_faqs_fallback

__all__ = [
    "extract_basic_meta",
    "extract_flat_text",
    "extract_faqs",
    "extract_faqs_from_nx_accordion",
    "extract_faqs_fallback",
]
