"""Builder para schemas de BlogPosting."""

from __future__ import annotations

import re
from copy import deepcopy
from typing import Any, Dict, List, Optional

from ..config import DEFAULT_LANGUAGE
from ..models import SchemaContext
from .base import (
    append_brand_organization,
    append_organization,
    build_webpage_node,
    organization_reference,
    resolve_organization,
)


def build_blog_posting_graph(
    ctx: SchemaContext,
    blog_defaults: Optional[Dict[str, Any]] = None,
    **_,
) -> List[Dict[str, Any]]:
    """Construye el grafo JSON-LD para un artículo de blog."""
    graph: List[Dict[str, Any]] = []
    added_orgs: set = set()
    cfg = blog_defaults or {}

    author_cfg = cfg.get("author") or {}
    publisher_cfg = cfg.get("publisher") or {}

    author_org = resolve_organization(author_cfg, "naranja_x")
    publisher_org = resolve_organization(publisher_cfg, "naranja_x")

    editor_names = cfg.get("editors") or ["Natalí Ciappini", "Francisco Piccini"]
    editors = [{"@type": "Person", "name": name} for name in editor_names if name]

    article_body = ctx.body_text or ""
    word_count = len(re.findall(r"\w+", article_body)) if article_body else None

    author_ref = organization_reference(author_org)
    author_ref["@type"] = "Organization"
    publisher_ref = organization_reference(publisher_org)
    publisher_ref["@type"] = "Organization"

    blog_posting: Dict[str, Any] = {
        "@type": "BlogPosting",
        "@id": f"{ctx.page_url}#BlogPosting",
        "url": ctx.page_url,
        "headline": cfg.get("headline", ctx.name),
        "description": cfg.get("description", ctx.description),
        "mainEntityOfPage": {"@type": "WebPage", "@id": f"{ctx.page_url}#WebPage"},
        "author": author_ref,
        "publisher": publisher_ref,
        "inLanguage": cfg.get("in_language", DEFAULT_LANGUAGE),
    }

    if editors:
        blog_posting["editor"] = editors
    if ctx.image_url:
        blog_posting["image"] = [ctx.image_url]
    if article_body:
        blog_posting["articleBody"] = article_body
    if word_count:
        blog_posting["wordCount"] = word_count

    date_published = cfg.get("date_published") or cfg.get("datePublished")
    if date_published:
        blog_posting["datePublished"] = date_published
    date_modified = cfg.get("date_modified") or cfg.get("dateModified")
    if date_modified:
        blog_posting["dateModified"] = date_modified

    article_section = cfg.get("article_section") or cfg.get("articleSection")
    if article_section:
        blog_posting["articleSection"] = article_section

    keywords = cfg.get("keywords")
    if keywords:
        blog_posting["keywords"] = keywords

    extra_fields = cfg.get("extra") or {}
    if extra_fields:
        blog_posting.update(deepcopy(extra_fields))

    graph.append(blog_posting)

    webpage_overrides = {
        "publisher": publisher_ref,
        "inLanguage": cfg.get("in_language", DEFAULT_LANGUAGE),
    }
    graph.append(build_webpage_node(ctx, extra=webpage_overrides))

    append_organization(graph, author_org, added_orgs)
    append_organization(graph, publisher_org, added_orgs)
    append_brand_organization(graph, added_orgs)

    return graph
