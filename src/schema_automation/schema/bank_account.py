"""Builder para schemas de BankAccount."""

from __future__ import annotations

from copy import deepcopy
from datetime import date
from typing import Any, Dict, List, Optional

from ..config import DEFAULT_LANGUAGE, default_price_valid_until
from ..models import SchemaContext
from .base import (
    append_organization,
    build_faq_page,
    build_offer_node,
    build_product_node,
    build_webpage_node,
    organization_reference,
    resolve_organization,
)


def build_bank_account_graph(
    ctx: SchemaContext,
    bank_defaults: Optional[Dict[str, Any]] = None,
    **_,
) -> List[Dict[str, Any]]:
    """Construye el grafo JSON-LD para una cuenta bancaria."""
    graph: List[Dict[str, Any]] = []
    added_orgs: set = set()
    today = date.today()
    next_year_end = date(today.year + 1, 12, 31)

    cfg = bank_defaults or {}
    price_currency = cfg.get("price_currency", "ARS")
    valid_from = cfg.get("valid_from", today.isoformat())
    valid_through = cfg.get("valid_through", next_year_end.isoformat())

    area_served_place = {
        "@type": "Place",
        "name": "Argentina",
        "address": {"@type": "PostalAddress", "addressCountry": "AR"},
    }

    offer_id = f"{ctx.page_url}#Offer"

    bank_account_offer_price = cfg.get("price", "0")
    if bank_account_offer_price in (None, ""):
        bank_account_offer_price = "0"

    bank_account = {
        "@type": "BankAccount",
        "@id": f"{ctx.page_url}#bankaccount",
        "name": ctx.name,
        "description": ctx.description,
        "areaServed": deepcopy(area_served_place),
        "provider": organization_reference("tarjeta_naranja"),
        "offers": {"@id": offer_id},
    }
    graph.append(bank_account)

    price_valid_until = cfg.get("price_valid_until") or valid_through or default_price_valid_until()

    offer = build_offer_node(
        ctx.page_url,
        offer_id,
        {
            "priceCurrency": price_currency,
            "availability": "https://schema.org/InStock",
            "validFrom": valid_from,
            "validThrough": valid_through,
            "areaServed": deepcopy(area_served_place),
            "eligibleRegion": "AR",
            "seller": organization_reference("tarjeta_naranja"),
            "priceValidUntil": price_valid_until,
            "price": bank_account_offer_price,
        },
    )
    graph.append(offer)

    product = build_product_node(
        ctx.page_url,
        f"{ctx.page_url}#Product",
        ctx.name,
        ctx.image_url,
        ctx.aggregate_rating,
        description=ctx.description,
        extra={"url": ctx.page_url, "offers": {"@id": offer_id}},
    )
    graph.append(product)

    faq_page = build_faq_page(
        ctx.page_url,
        ctx.faqs,
        f"{ctx.page_url}#faq",
        extra={
            "url": ctx.page_url,
            "name": f"Preguntas frecuentes sobre {ctx.name}",
            "inLanguage": DEFAULT_LANGUAGE,
        },
    )
    if faq_page:
        graph.append(faq_page)

    graph.append(build_webpage_node(ctx))

    append_organization(graph, resolve_organization({}, "tarjeta_naranja"), added_orgs)

    return graph
