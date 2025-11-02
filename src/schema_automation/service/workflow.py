"""Servicios de orquestación para construir los schemas completos."""

from __future__ import annotations

import logging
import re
from copy import deepcopy
from typing import Any, Dict, Optional

from bs4 import BeautifulSoup, Tag

from ..config import DEFAULT_AGG_RATING
from ..extraction import extract_basic_meta, extract_faqs, extract_flat_text
from ..extraction.html import ensure_soup
from ..infrastructure.http import fetch_html
from ..infrastructure.persistence import as_script_tag, save_outputs
from ..models import ExtractionResult, SchemaContext, SchemaRecord
from ..schema import SCHEMA_BUILDERS, build_offer_catalog_node

logger = logging.getLogger(__name__)


def _schema_type_key(schema_type: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", schema_type).lower().replace("-", "_").strip()


def _select_body_node(soup: BeautifulSoup) -> Optional[Tag]:
    candidates = [
        soup.select_one("article"),
        soup.select_one("main"),
        soup.select_one("[role='main']"),
        soup.body,
    ]
    return next(
        (
            candidate
            for candidate in candidates
            if isinstance(candidate, Tag) and candidate.get_text(strip=True)
        ),
        None,
    )


def build_schema_from_url(
    url: str,
    nombre: str,
    schema_type: str = "payment_card",
    *,
    price_spec: Optional[Dict[str, Any]] = None,
    bank_defaults: Optional[Dict[str, Any]] = None,
    payment_service_defaults: Optional[Dict[str, Any]] = None,
    insurance_defaults: Optional[Dict[str, Any]] = None,
    loan_defaults: Optional[Dict[str, Any]] = None,
    financial_product_defaults: Optional[Dict[str, Any]] = None,
    investment_defaults: Optional[Dict[str, Any]] = None,
    blog_defaults: Optional[Dict[str, Any]] = None,
    offer_catalog_key: Optional[str] = None,
    aggregate_rating: Optional[Dict[str, Any]] = None,
) -> SchemaRecord:
    html, base_url, final_url = fetch_html(url)
    soup = ensure_soup(html)
    meta = extract_basic_meta(html, base_url=base_url, soup=soup)

    faqs = extract_faqs(soup)

    body_node = _select_body_node(soup)
    body_text = extract_flat_text(body_node) if body_node else ""

    image_url = meta.get("image", "") or ""
    description_text = meta.get("description", "") or ""

    agg_source = aggregate_rating if aggregate_rating is not None else DEFAULT_AGG_RATING
    agg_rating = deepcopy(agg_source) if agg_source else None
    if agg_rating is not None:
        agg_rating.setdefault("@type", "AggregateRating")

    key = _schema_type_key(schema_type)
    builder = SCHEMA_BUILDERS.get(key)
    if builder is None:
        raise ValueError(f"schema_type desconocido: {schema_type}")

    context = SchemaContext(
        page_url=final_url,
        name=nombre,
        description=description_text,
        image_url=image_url or None,
        faqs=faqs,
        body_text=body_text or None,
        aggregate_rating=agg_rating,
    )

    graph_nodes = builder(
        context,
        price_spec=price_spec,
        bank_defaults=bank_defaults,
        payment_service_defaults=payment_service_defaults,
        insurance_defaults=insurance_defaults,
        loan_defaults=loan_defaults,
        financial_product_defaults=financial_product_defaults,
        investment_defaults=investment_defaults,
        blog_defaults=blog_defaults,
    )

    if offer_catalog_key:
        catalog_node, provider_org = build_offer_catalog_node(context.page_url, offer_catalog_key)
        if catalog_node:
            graph_nodes.append(catalog_node)
            if provider_org and provider_org.get("@id"):
                existing_ids = {
                    node.get("@id")
                    for node in graph_nodes
                    if isinstance(node, Dict) and node.get("@id")
                }
                if provider_org["@id"] not in existing_ids:
                    graph_nodes.append(provider_org)

    schema_graph = {"@context": "https://schema.org", "@graph": graph_nodes}

    extracted = ExtractionResult(
        title=meta.get("title", ""),
        description=description_text,
        image=image_url,
        faqs=faqs,
        body_text=body_text,
    )

    return SchemaRecord(
        url=final_url,
        name=nombre,
        schema_type=schema_type,
        extracted=extracted,
        schema=schema_graph,
    )


def generate_schema(
    url: str,
    nombre: str,
    schema_type: str = "payment_card",
    *,
    price_spec: Optional[Dict[str, Any]] = None,
    bank_defaults: Optional[Dict[str, Any]] = None,
    payment_service_defaults: Optional[Dict[str, Any]] = None,
    insurance_defaults: Optional[Dict[str, Any]] = None,
    loan_defaults: Optional[Dict[str, Any]] = None,
    financial_product_defaults: Optional[Dict[str, Any]] = None,
    investment_defaults: Optional[Dict[str, Any]] = None,
    blog_defaults: Optional[Dict[str, Any]] = None,
    offer_catalog_key: Optional[str] = None,
    aggregate_rating: Optional[Dict[str, Any]] = None,
    save: bool = False,
    csv_path: str = "extracciones.csv",
    jsonl_path: str = "schemas.jsonl",
    as_script: bool = False,
):
    record = build_schema_from_url(
        url,
        nombre,
        schema_type=schema_type,
        price_spec=price_spec,
        bank_defaults=bank_defaults,
        payment_service_defaults=payment_service_defaults,
        insurance_defaults=insurance_defaults,
        loan_defaults=loan_defaults,
        financial_product_defaults=financial_product_defaults,
        investment_defaults=investment_defaults,
        blog_defaults=blog_defaults,
        offer_catalog_key=offer_catalog_key,
        aggregate_rating=aggregate_rating,
    )

    if save:
        save_outputs(record, csv_path=csv_path, jsonl_path=jsonl_path)
    if as_script:
        return as_script_tag(record.schema)
    return record.to_dict()
