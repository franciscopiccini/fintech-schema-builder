"""Helpers para trabajar con BeautifulSoup."""

from __future__ import annotations

from typing import Union

from bs4 import BeautifulSoup


def ensure_soup(html_or_soup: Union[str, BeautifulSoup]) -> BeautifulSoup:
    """Retorna una instancia de BeautifulSoup independientemente del input."""
    if isinstance(html_or_soup, BeautifulSoup):
        return html_or_soup
    return BeautifulSoup(html_or_soup, "lxml")
