"""Strategies para extraer FAQs desde distintas estructuras de DOM."""

from __future__ import annotations

import re
from typing import Dict, List, Optional

from bs4 import BeautifulSoup, Tag

from .html import ensure_soup
from .text import clean_text

QUESTION_RE = re.compile(r"¿.+\?$")


def _extract_answer_text(body: Tag) -> str:
    """Convierte el contenido del panel a texto plano legible."""
    chunks: List[str] = []

    for paragraph in body.select("p"):
        txt = clean_text(paragraph.get_text(" ", strip=True))
        if txt:
            chunks.append(txt)

    for lst in body.select("ul, ol"):
        items = []
        for li in lst.select(":scope > li"):
            li_txt = clean_text(li.get_text(" ", strip=True))
            if li_txt:
                items.append(f"• {li_txt}")
        if items:
            chunks.append("\n".join(items))

    if not chunks:
        raw = clean_text(body.get_text(" ", strip=True))
        if raw:
            chunks.append(raw)

    return "\n\n".join(chunks).strip()


def extract_faqs_from_nx_accordion(html_or_soup) -> List[Dict[str, str]]:
    """Extrae FAQs del componente `accordion-list` usado en Naranja X."""
    soup = ensure_soup(html_or_soup)
    faqs: List[Dict[str, str]] = []

    roots = soup.select("accordion-list ul.accordion-list")
    if not roots:
        return faqs

    for root in roots:
        for li in root.select(":scope > li"):
            question_node = li.select_one("h3.accordion-label")
            if question_node is None:
                question_node = li.select_one(".accordion__projected-title h3")
            if question_node is None:
                continue

            question = clean_text(question_node.get_text(" ", strip=True))
            if question and QUESTION_RE.search(question) is None:
                question = question or ""

            body = li.select_one(".accordion__body, .accordion__body-container")
            if body is None:
                heading = li.select_one(".accordion__heading")
                if heading:
                    sibling = heading.find_next_sibling()
                    if isinstance(sibling, Tag):
                        body = sibling
            if body is None:
                continue

            answer = _extract_answer_text(body)
            if not answer:
                continue

            faqs.append({"question": question, "answer": answer})

    seen = set()
    unique: List[Dict[str, str]] = []
    for faq in faqs:
        key = (faq["question"], faq["answer"])
        if key not in seen:
            seen.add(key)
            unique.append(faq)
    return unique


def extract_faqs_fallback(html_or_soup) -> List[Dict[str, str]]:
    """Heurística genérica basada en headings/botones con signo de pregunta."""
    soup = ensure_soup(html_or_soup)
    faqs: List[Dict[str, str]] = []
    for node in soup.select("h3,button"):
        question = clean_text(node.get_text(" ", strip=True))
        if not question or "?" not in question:
            continue
        sibling = node.find_next_sibling()
        answer = ""
        if isinstance(sibling, Tag):
            answer = clean_text(sibling.get_text(" ", strip=True))
        if question and answer:
            faqs.append({"question": question, "answer": answer})

    seen = set()
    unique: List[Dict[str, str]] = []
    for faq in faqs:
        key = (faq["question"], faq["answer"])
        if key not in seen:
            seen.add(key)
            unique.append(faq)
    return unique


def extract_faqs(html_or_soup) -> List[Dict[str, str]]:
    """Ejecuta extracción específica y fallback combinados."""
    faqs = extract_faqs_from_nx_accordion(html_or_soup)
    if faqs:
        return faqs
    return extract_faqs_fallback(html_or_soup)
