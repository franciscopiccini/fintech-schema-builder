"""Construcción de grafos JSON-LD para cada tipo de schema soportado."""

from __future__ import annotations

import re
from copy import deepcopy
from datetime import date, timedelta
from typing import Any, Callable, Dict, List, Optional, Tuple

from ..config import (
    DEFAULT_LANGUAGE,
    FINANCIAL_PRODUCT_DEFAULTS,
    FINANCIAL_PRODUCT_ZERO_RATES,
    INSURANCE_AGENCY_DEFAULTS,
    INVESTMENT_OR_DEPOSIT_DEFAULTS,
    LOAN_OR_CREDIT_DEFAULTS,
    OFFER_CATALOGS,
    ORGANIZATIONS,
    PAYMENT_SERVICE_DEFAULTS,
    PRICE_SPEC_DEFAULT,
    WEBPAGE_DEFAULTS,
    default_price_valid_until,
)
from ..models import SchemaContext


def deep_merge(base: Dict[str, Any], overrides: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    result = deepcopy(base)
    if not overrides:
        return result
    for key, value in overrides.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = deepcopy(value)
    return result


def organization_reference(org_key_or_data: Any) -> Dict[str, str]:
    if isinstance(org_key_or_data, dict):
        return {"@id": org_key_or_data.get("@id")}
    return {"@id": ORGANIZATIONS[org_key_or_data]["@id"]}


def resolve_organization(config: Optional[Dict[str, Any]], default_key: str) -> Dict[str, Any]:
    cfg = config or {}
    org_key = cfg.get("org_key") or default_key
    base = deepcopy(ORGANIZATIONS.get(org_key, ORGANIZATIONS[default_key]))
    org_id = cfg.get("id") or cfg.get("@id")
    if org_id:
        matched = next(
            (deepcopy(org) for org in ORGANIZATIONS.values() if org.get("@id") == org_id),
            None,
        )
        if matched:
            base = matched
    for key, value in cfg.items():
        if key in {"org_key", "overrides"}:
            continue
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            base[key].update(value)
        else:
            base[key] = deepcopy(value)
    overrides = cfg.get("overrides")
    if overrides:
        for key, value in overrides.items():
            if isinstance(value, dict) and isinstance(base.get(key), dict):
                base[key].update(value)
            else:
                base[key] = deepcopy(value)
    return base


def append_organization(graph: List[Dict[str, Any]], org_data: Dict[str, Any], added_ids: set):
    org_id = org_data.get("@id")
    if org_id and org_id in added_ids:
        return
    graph.append(org_data)
    if org_id:
        added_ids.add(org_id)


def _faq_entities(faqs: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    entities: List[Dict[str, Any]] = []
    for faq in faqs or []:
        question = faq.get("question", "").strip()
        answer = faq.get("answer", "").strip()
        if not question or not answer:
            continue
        entities.append(
            {
                "@type": "Question",
                "name": question,
                "acceptedAnswer": {"@type": "Answer", "text": answer},
            }
        )
    return entities


def build_faq_page(
    page_url: str,
    faqs: List[Dict[str, str]],
    node_id: str,
    extra: Optional[Dict[str, Any]] = None,
) -> Optional[Dict[str, Any]]:
    entities = _faq_entities(faqs)
    if not entities:
        return None

    node: Dict[str, Any] = {
        "@type": "FAQPage",
        "@id": node_id,
        "inLanguage": DEFAULT_LANGUAGE,
        "mainEntity": entities,
    }
    if extra:
        node.update(extra)
    return node


def build_product_node(
    page_url: str,
    node_id: str,
    name: str,
    image_url: Optional[str],
    aggregate_rating: Optional[Dict[str, Any]],
    description: Optional[str] = None,
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    node: Dict[str, Any] = {"@type": "Product", "@id": node_id, "name": name}
    if image_url:
        node["image"] = image_url
    if aggregate_rating:
        node["aggregateRating"] = deepcopy(aggregate_rating)
    if description:
        node["description"] = description
    if extra:
        node.update(extra)
    return node


def build_offer_node(page_url: str, node_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    node: Dict[str, Any] = {"@type": "Offer", "@id": node_id, "url": data.get("url", page_url)}
    for key, value in data.items():
        if key == "url":
            continue
        node[key] = value
    return node


def build_webpage_node(ctx: SchemaContext, extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    node = deepcopy(WEBPAGE_DEFAULTS)
    node["@id"] = f"{ctx.page_url}#WebPage"
    node["url"] = ctx.page_url
    node["name"] = ctx.name
    if ctx.description:
        node["description"] = ctx.description
    if extra:
        node.update(extra)
    return node


def build_blog_posting_graph(
    ctx: SchemaContext,
    blog_defaults: Optional[Dict[str, Any]] = None,
    **_,
) -> List[Dict[str, Any]]:
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

    return graph


def build_offer_catalog_node(
    page_url: str, catalog_key: str
) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
    catalog = OFFER_CATALOGS.get(catalog_key)
    if not catalog:
        return None, None

    node_id_suffix = re.sub(r"[^0-9A-Za-z]+", "-", catalog["name"]).strip("-") or catalog_key
    node_id = f"{page_url}#OfferCatalog{node_id_suffix}"

    item_list = []
    for idx, item in enumerate(catalog.get("items", []), start=1):
        name = item.get("name")
        url = item.get("url")
        if not name or not url:
            continue
        offer_id = f"{node_id}-Offer{idx}"

        item_id_override = item.get("item_id") or item.get("@id")
        id_suffix = item.get("id_suffix")
        item_type = item.get("item_type", "Product")

        if item_id_override:
            item_offered: Dict[str, Any] = {"@id": item_id_override}
        elif id_suffix and url:
            item_offered = {"@id": f"{url}{id_suffix}"}
        else:
            item_offered = {"@type": item_type, "name": name}
            if url:
                item_offered["url"] = url

        offer_props = item.get("offer", {}) if isinstance(item.get("offer"), dict) else {}
        offer_price = offer_props.get("price", catalog.get("default_price", "0"))
        if offer_price in (None, ""):
            offer_price = "0"
        offer_currency = (
            offer_props.get("priceCurrency")
            or offer_props.get("price_currency")
            or catalog.get("price_currency", "ARS")
        )
        offer_availability = (
            offer_props.get("availability") or catalog.get("availability", "https://schema.org/InStock")
        )
        offer_price_valid_until = (
            offer_props.get("priceValidUntil")
            or offer_props.get("price_valid_until")
            or catalog.get("price_valid_until")
        )
        if not offer_price_valid_until:
            offer_price_valid_until = default_price_valid_until()

        offer_item = {
            "@type": "Offer",
            "@id": offer_id,
            "name": name,
            "price": offer_price,
            "priceCurrency": offer_currency,
            "availability": offer_availability,
            "priceValidUntil": offer_price_valid_until,
            "itemOffered": item_offered,
            "url": url,
        }
        item_list.append(offer_item)

    if not item_list:
        return None, None

    catalog_node: Dict[str, Any] = {
        "@type": "OfferCatalog",
        "@id": node_id,
        "name": catalog["name"],
        "itemListElement": item_list,
    }

    provider_key = catalog.get("provider", "naranja_x")
    provider_org = ORGANIZATIONS.get(provider_key)

    return catalog_node, deepcopy(provider_org) if provider_org else None


def build_payment_card_graph(ctx: SchemaContext, **_) -> List[Dict[str, Any]]:
    graph: List[Dict[str, Any]] = []
    added_orgs: set = set()

    offer_id = f"{ctx.page_url}#Offer"

    payment_card: Dict[str, Any] = {
        "@type": "PaymentCard",
        "@id": f"{ctx.page_url}#PaymentCard",
        "url": ctx.page_url,
        "name": ctx.name,
        "description": ctx.description,
        "areaServed": "AR",
        "provider": [organization_reference("tarjeta_naranja")],
        "mainEntityOfPage": ctx.page_url,
        "offers": {"@id": offer_id},
    }
    if ctx.image_url:
        payment_card["image"] = {"@type": "ImageObject", "@id": f"{ctx.page_url}#PaymentCardImage", "url": ctx.image_url}
    graph.append(payment_card)

    price_valid_until = default_price_valid_until()

    offer = build_offer_node(
        ctx.page_url,
        offer_id,
        {
            "name": ctx.name,
            "price": "0",
            "priceCurrency": "ARS",
            "availability": "https://schema.org/InStock",
            "areaServed": "AR",
            "priceValidUntil": price_valid_until,
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

    faq_page = build_faq_page(ctx.page_url, ctx.faqs, f"{ctx.page_url}#FAQPage")
    if faq_page:
        graph.append(faq_page)

    graph.append(build_webpage_node(ctx))

    append_organization(graph, resolve_organization({}, "tarjeta_naranja"), added_orgs)

    return graph


def build_loan_or_credit_graph(
    ctx: SchemaContext,
    price_spec: Optional[Dict[str, Any]] = None,
    loan_defaults: Optional[Dict[str, Any]] = None,
    **_,
) -> List[Dict[str, Any]]:
    graph: List[Dict[str, Any]] = []
    added_orgs: set = set()

    defaults = deep_merge(LOAN_OR_CREDIT_DEFAULTS, loan_defaults or {})
    amount_cfg = defaults.get("amount", {})
    currency_value = defaults.get("currency") or amount_cfg.get("currency")
    loan_term_cfg = defaults.get("loan_term", {})
    interest_rate_cfg = defaults.get("interest_rate", {})
    apr_cfg = defaults.get("annual_percentage_rate", {})
    repayment_cfg = defaults.get("loan_repayment_form", {})
    loan_type_value = defaults.get("loan_type") or ctx.name

    def _quantitative_node(cfg: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not isinstance(cfg, dict):
            return None
        node: Dict[str, Any] = {"@type": cfg.get("@type", "QuantitativeValue")}
        has_value = False
        for key in ("minValue", "maxValue", "unitText", "value"):
            value = cfg.get(key)
            if value is not None:
                node[key] = value
                if key != "unitText":
                    has_value = True
        return node if has_value or len(node) > 1 else None

    offer_id = f"{ctx.page_url}#Offer"

    loan_node: Dict[str, Any] = {
        "@type": "LoanOrCredit",
        "@id": f"{ctx.page_url}#LoanOrCredit",
        "url": ctx.page_url,
        "name": ctx.name,
        "provider": [
            organization_reference("naranja_digital"),
            organization_reference("tarjeta_naranja"),
        ],
        "mainEntityOfPage": ctx.page_url,
        "offers": {"@id": offer_id},
        "loanType": loan_type_value,
    }

    if currency_value:
        loan_node["currency"] = currency_value

    if isinstance(amount_cfg, dict) and amount_cfg:
        amount_node: Dict[str, Any] = {"@type": "MonetaryAmount"}
        amount_currency = amount_cfg.get("currency", currency_value)
        if amount_currency:
            amount_node["currency"] = amount_currency
        for key in ("minValue", "maxValue"):
            value = amount_cfg.get(key)
            if value is not None:
                amount_node[key] = value
        if len(amount_node) > 1:
            loan_node["amount"] = amount_node

    term_node = _quantitative_node(loan_term_cfg)
    if term_node:
        loan_node["loanTerm"] = term_node

    interest_node = _quantitative_node(interest_rate_cfg)
    if interest_node:
        loan_node["interestRate"] = interest_node

    apr_node = _quantitative_node(apr_cfg)
    if apr_node:
        loan_node["annualPercentageRate"] = apr_node

    if isinstance(repayment_cfg, dict) and repayment_cfg:
        repayment_node: Dict[str, Any] = {"@type": repayment_cfg.get("@type", "RepaymentSpecification")}
        for key in ("name", "description"):
            value = repayment_cfg.get(key)
            if value:
                repayment_node[key] = value
        if len(repayment_node) > 1:
            loan_node["loanRepaymentForm"] = repayment_node

    if ctx.image_url:
        loan_node["image"] = {"@type": "ImageObject", "@id": f"{ctx.page_url}#LoanImage", "url": ctx.image_url}
    graph.append(loan_node)

    offer_price = "0"
    if price_spec and isinstance(price_spec, dict):
        price_candidate = price_spec.get("price")
        if price_candidate not in (None, ""):
            offer_price = str(price_candidate)
    price_valid_until = default_price_valid_until()

    offer = build_offer_node(
        ctx.page_url,
        offer_id,
        {
            "name": ctx.name,
            "priceCurrency": "ARS",
            "areaServed": "AR",
            "availability": "https://schema.org/InStock",
            "priceValidUntil": price_valid_until,
            "price": offer_price,
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

    faq_page = build_faq_page(ctx.page_url, ctx.faqs, f"{ctx.page_url}#FAQPage")
    if faq_page:
        graph.append(faq_page)

    graph.append(build_webpage_node(ctx))

    append_organization(graph, resolve_organization({}, "naranja_digital"), added_orgs)
    append_organization(graph, resolve_organization({}, "tarjeta_naranja"), added_orgs)

    return graph


def build_bank_account_graph(
    ctx: SchemaContext,
    bank_defaults: Optional[Dict[str, Any]] = None,
    **_,
) -> List[Dict[str, Any]]:
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


def build_payment_service_graph(
    ctx: SchemaContext,
    payment_service_defaults: Optional[Dict[str, Any]] = None,
    price_spec: Optional[Dict[str, Any]] = None,
    **_,
) -> List[Dict[str, Any]]:
    graph: List[Dict[str, Any]] = []
    added_orgs: set = set()
    today = date.today()
    next_year_end = date(today.year + 1, 12, 31)

    cfg = deep_merge(PAYMENT_SERVICE_DEFAULTS, payment_service_defaults or {})
    area_served = deepcopy(cfg.get("area_served", {"@type": "Country", "name": "Argentina"}))
    provider = resolve_organization(cfg.get("provider"), PAYMENT_SERVICE_DEFAULTS["provider"]["org_key"])

    service_node: Dict[str, Any] = {
        "@type": "PaymentService",
        "@id": f"{ctx.page_url}#PaymentService",
        "name": ctx.name,
        "description": ctx.description,
        "areaServed": deepcopy(area_served),
        "provider": organization_reference(provider),
        "offers": {"@id": f"{ctx.page_url}#Offer"},
    }
    if ctx.image_url:
        service_node["image"] = ctx.image_url
    graph.append(service_node)

    offer_cfg = cfg.get("offer", {})
    valid_from = offer_cfg.get("valid_from", today.isoformat())
    valid_through = offer_cfg.get("valid_through", next_year_end.isoformat())
    availability_starts = offer_cfg.get("availability_starts", valid_from)
    price_valid_until = offer_cfg.get("price_valid_until") or default_price_valid_until()

    offer = build_offer_node(
        ctx.page_url,
        f"{ctx.page_url}#Offer",
        {
            "priceCurrency": offer_cfg.get("price_currency", "ARS"),
            "areaServed": deepcopy(area_served),
            "validFrom": valid_from,
            "validThrough": valid_through,
            "availabilityStarts": availability_starts,
            "eligibleRegion": offer_cfg.get("eligible_region", "AR"),
            "priceValidUntil": price_valid_until,
            "price": offer_cfg.get("price", "0") or "0",
        },
    )
    graph.append(offer)

    brand_ref = organization_reference(provider)
    brand_ref["@type"] = "Organization"

    product = build_product_node(
        ctx.page_url,
        f"{ctx.page_url}#Product",
        ctx.name,
        ctx.image_url,
        ctx.aggregate_rating,
        description=ctx.description,
        extra={"url": ctx.page_url, "brand": brand_ref, "offers": {"@id": f"{ctx.page_url}#Offer"}},
    )
    graph.append(product)

    faq_page = build_faq_page(ctx.page_url, ctx.faqs, f"{ctx.page_url}#FAQPage")
    if faq_page:
        graph.append(faq_page)

    graph.append(build_webpage_node(ctx))

    append_organization(graph, provider, added_orgs)

    return graph


def build_financial_product_graph(
    ctx: SchemaContext,
    financial_product_defaults: Optional[Dict[str, Any]] = None,
    **_,
) -> List[Dict[str, Any]]:
    graph: List[Dict[str, Any]] = []
    added_orgs: set = set()
    today = date.today()
    defaults = FINANCIAL_PRODUCT_DEFAULTS
    overrides = financial_product_defaults or {}

    area_served = overrides.get("area_served", defaults.get("area_served", "AR"))

    provider_defaults = defaults.get("provider", {})
    provider_overrides = overrides.get("provider", {})
    provider_cfg = deep_merge(provider_defaults, provider_overrides)
    provider = resolve_organization(provider_cfg, provider_defaults.get("org_key", "tarjeta_naranja"))

    rates = overrides.get("rates", FINANCIAL_PRODUCT_ZERO_RATES)
    rate_parts = []
    for code, value in (rates or {}).items():
        if isinstance(value, (int, float)):
            formatted = f"{value:.2f}".rstrip("0").rstrip(".")
        else:
            formatted = str(value)
        if formatted and not formatted.endswith("%"):
            formatted = f"{formatted} %"
        rate_parts.append(f"{code} {formatted}".strip())
    rates_text = ", ".join([p for p in rate_parts if p])

    offer_defaults = defaults.get("offer", {})
    offer_overrides = overrides.get("offer", {})
    valid_from = offer_overrides.get("valid_from")
    if not valid_from:
        offset = offer_defaults.get("valid_from_offset", 0)
        valid_from = (today + timedelta(days=offset)).isoformat()
    valid_through = offer_overrides.get("valid_through")
    if not valid_through:
        offset = offer_defaults.get("valid_through_offset", 30)
        valid_through = (today + timedelta(days=offset)).isoformat()
    price_currency = offer_overrides.get("price_currency", offer_defaults.get("price_currency", "ARS"))
    billing_increment = offer_overrides.get("billing_increment", offer_defaults.get("billing_increment", "1"))
    min_price = offer_overrides.get("min_price", offer_defaults.get("min_price", "0"))
    offer_area_served = offer_overrides.get("area_served", offer_defaults.get("area_served", area_served))
    description_template = offer_overrides.get(
        "description_template", offer_defaults.get("description_template", "Características financieras: {rates_text}.")
    )
    offer_description = offer_overrides.get("description")
    if not offer_description:
        offer_description = description_template.format(rates_text=rates_text)

    identifier = overrides.get("identifier", defaults.get("identifier"))
    if not identifier:
        slug = re.sub(r"[^0-9A-Za-z]+", "-", ctx.name).strip("-")
        identifier = slug or None

    product_defaults = defaults.get("product", {})
    product_overrides = overrides.get("product", {})
    product_id_suffix = product_overrides.get("id_suffix", product_defaults.get("id_suffix", "#Product"))
    product_id = product_overrides.get("id") or f"{ctx.page_url}{product_id_suffix}"
    product_name_value = product_overrides.get("name", product_defaults.get("name", ctx.name))

    faq_id_suffix = overrides.get("faq_id_suffix", defaults.get("faq_id_suffix", "#FAQPage"))
    faq_id = f"{ctx.page_url}{faq_id_suffix}"

    offer_id = f"{ctx.page_url}#Offer"

    financial_product = {
        "@type": "FinancialProduct",
        "@id": f"{ctx.page_url}#FinancialProduct",
        "name": ctx.name,
        "description": ctx.description,
        "areaServed": area_served,
        "provider": organization_reference(provider),
        "offers": {"@id": offer_id},
    }
    if ctx.image_url:
        financial_product["image"] = ctx.image_url
    if identifier:
        financial_product["identifier"] = identifier
    graph.append(financial_product)

    append_organization(graph, provider, added_orgs)

    price_valid_until = default_price_valid_until()

    offer = build_offer_node(
        ctx.page_url,
        offer_id,
        {
            "priceCurrency": price_currency,
            "areaServed": offer_area_served,
            "validFrom": valid_from,
            "validThrough": valid_through,
            "itemOffered": {"@id": product_id},
            "priceValidUntil": price_valid_until,
            "price": min_price,
            "priceSpecification": {
                "@type": "UnitPriceSpecification",
                "billingIncrement": billing_increment,
                "price": min_price,
                "priceCurrency": price_currency,
                "description": offer_description,
            },
        },
    )
    graph.append(offer)

    product = build_product_node(
        ctx.page_url,
        product_id,
        product_name_value,
        ctx.image_url,
        ctx.aggregate_rating,
        description=ctx.description,
        extra={"url": ctx.page_url, "offers": {"@id": offer_id}},
    )
    graph.append(product)

    faq_page = build_faq_page(ctx.page_url, ctx.faqs, faq_id)
    if faq_page:
        graph.append(faq_page)

    graph.append(build_webpage_node(ctx))

    return graph


def build_investment_or_deposit_graph(
    ctx: SchemaContext,
    investment_defaults: Optional[Dict[str, Any]] = None,
    **_,
) -> List[Dict[str, Any]]:
    graph: List[Dict[str, Any]] = []
    added_orgs: set = set()
    today = date.today()
    defaults = INVESTMENT_OR_DEPOSIT_DEFAULTS
    overrides = investment_defaults or {}

    area_served = overrides.get("area_served", defaults.get("area_served", "AR"))

    base_globals = defaults.get("globals", {})
    override_globals = overrides.get("globals", {})
    combined_globals = {**base_globals, **override_globals}

    provider_defaults = defaults.get("provider", {})
    provider_overrides = overrides.get("provider", {})
    provider_cfg = deep_merge(provider_defaults, provider_overrides)
    provider = resolve_organization(provider_cfg, provider_defaults.get("org_key", "naranja_x"))

    investment_defaults_cfg = defaults.get("investment", {})
    investment_overrides = overrides.get("investment", {})

    investment_types = investment_overrides.get("types", investment_defaults_cfg.get("types", ["InvestmentOrDeposit"]))
    if isinstance(investment_types, str):
        investment_types = [investment_types]

    investment_id_suffix = investment_overrides.get("id_suffix", investment_defaults_cfg.get("id_suffix", "#investment"))
    investment_id = investment_overrides.get("id") or f"{ctx.page_url}{investment_id_suffix}"
    investment_alternate_name = investment_overrides.get(
        "alternate_name", investment_defaults_cfg.get("alternate_name")
    )
    investment_service_type = investment_overrides.get("service_type", investment_defaults_cfg.get("service_type"))
    investment_audience = investment_overrides.get("audience", investment_defaults_cfg.get("audience"))

    investment_identifier = overrides.get("identifier", investment_overrides.get("identifier"))
    if not investment_identifier:
        slug = re.sub(r"[^0-9A-Za-z]+", "-", ctx.name).strip("-")
        investment_identifier = slug or None

    interest_rate_defaults = investment_defaults_cfg.get("interest_rate", {})
    interest_rate_overrides = investment_overrides.get("interest_rate", {})
    interest_rate_type = interest_rate_overrides.get("type", interest_rate_defaults.get("type", "QuantitativeValue"))
    interest_rate_unit = interest_rate_overrides.get("unit_text", interest_rate_defaults.get("unit_text", "TNA"))
    default_rate_value = interest_rate_defaults.get("value", combined_globals.get("interest_rate", ""))
    interest_rate_value = interest_rate_overrides.get("value", default_rate_value)

    offer_defaults_cfg = defaults.get("offer", {})
    offer_overrides = overrides.get("offer", {})
    offer_id_suffix = offer_overrides.get("id_suffix", offer_defaults_cfg.get("id_suffix", "#offer"))
    offer_id = offer_overrides.get("id") or f"{ctx.page_url}{offer_id_suffix}"
    offer_price_currency = offer_overrides.get("price_currency", offer_defaults_cfg.get("price_currency", "ARS"))
    offer_area_served = offer_overrides.get("area_served", offer_defaults_cfg.get("area_served", area_served))
    offer_eligible_region = offer_overrides.get(
        "eligible_region", offer_defaults_cfg.get("eligible_region", area_served)
    )
    offer_availability = offer_overrides.get(
        "availability", offer_defaults_cfg.get("availability", "https://schema.org/InStock")
    )

    valid_from = offer_overrides.get("valid_from")
    if not valid_from:
        offset = offer_defaults_cfg.get("valid_from_offset", 0)
        valid_from = (today + timedelta(days=offset)).isoformat()
    valid_through = offer_overrides.get("valid_through")
    if not valid_through:
        offset = offer_defaults_cfg.get("valid_through_offset", 0)
        valid_through = (today + timedelta(days=offset)).isoformat()

    offer_name = offer_overrides.get("name", ctx.name or investment_overrides.get("name", ctx.name))
    offer_duration = offer_overrides.get("eligible_duration", combined_globals.get("duration", "")) or ""

    product_defaults_cfg = defaults.get("product", {})
    product_overrides = overrides.get("product", {})
    product_id_suffix = product_overrides.get("id_suffix", product_defaults_cfg.get("id_suffix", "#product"))
    product_id = product_overrides.get("id") or f"{ctx.page_url}{product_id_suffix}"

    faq_id_suffix = overrides.get("faq_id_suffix", defaults.get("faq_id_suffix", "#FAQPage"))
    faq_id = f"{ctx.page_url}{faq_id_suffix}"

    investment_node: Dict[str, Any] = {
        "@type": investment_types,
        "@id": investment_id,
        "name": ctx.name,
        "description": ctx.description,
        "areaServed": area_served,
        "mainEntityOfPage": ctx.page_url,
        "provider": provider,
        "offers": {"@id": offer_id},
        "interestRate": {
            "@type": interest_rate_type,
            "unitText": interest_rate_unit,
        },
    }

    if investment_alternate_name:
        investment_node["alternateName"] = investment_alternate_name
    if investment_service_type:
        investment_node["serviceType"] = investment_service_type
    if investment_audience:
        investment_node["audience"] = investment_audience
    if ctx.image_url:
        investment_node["image"] = ctx.image_url
    if investment_identifier:
        investment_node["identifier"] = investment_identifier

    if interest_rate_value not in (None, ""):
        investment_node["interestRate"]["value"] = interest_rate_value

    graph.append(investment_node)

    append_organization(graph, provider, added_orgs)

    price_valid_until = default_price_valid_until()

    offer = build_offer_node(
        ctx.page_url,
        offer_id,
        {
            "name": offer_name,
            "priceCurrency": offer_price_currency,
            "areaServed": offer_area_served,
            "eligibleRegion": offer_eligible_region,
            "availability": offer_availability,
            "validFrom": valid_from,
            "validThrough": valid_through,
            "priceValidUntil": price_valid_until,
            "eligibleDuration": offer_duration,
        },
    )
    graph.append(offer)

    product = build_product_node(
        ctx.page_url,
        product_id,
        ctx.name,
        ctx.image_url,
        ctx.aggregate_rating,
        description=ctx.description,
        extra={"url": ctx.page_url, "offers": {"@id": offer_id}},
    )
    graph.append(product)

    faq_page = build_faq_page(ctx.page_url, ctx.faqs, faq_id)
    if faq_page:
        graph.append(faq_page)

    graph.append(build_webpage_node(ctx))

    return graph


def build_insurance_agency_graph(
    ctx: SchemaContext,
    insurance_defaults: Optional[Dict[str, Any]] = None,
    **_,
) -> List[Dict[str, Any]]:
    graph: List[Dict[str, Any]] = []
    added_orgs: set = set()
    today = date.today()
    next_year_end = date(today.year + 1, 12, 31)

    defaults = INSURANCE_AGENCY_DEFAULTS
    overrides = insurance_defaults or {}

    agency_base = defaults.get("agency", {})
    agency_overrides = overrides.get("agency", {})
    agency_identifier = {
        **agency_base.get("identifier", {}),
        **agency_overrides.get("identifier", {}),
    }
    if not agency_identifier.get("propertyID") or not agency_identifier.get("value"):
        agency_identifier = None
    agency_logo = {**agency_base.get("logo", {}), **agency_overrides.get("logo", {})}
    if not agency_logo.get("url") and ctx.image_url:
        agency_logo["url"] = ctx.image_url

    agency_same_as = agency_overrides.get("same_as", agency_base.get("same_as", []))
    if isinstance(agency_same_as, str):
        agency_same_as = [agency_same_as]

    area_served = overrides.get("area_served", agency_base.get("area_served", "AR"))
    addresses = overrides.get("addresses", agency_base.get("addresses"))

    agency_id_suffix = agency_overrides.get("id_suffix", agency_base.get("id_suffix", "#insurance-agency"))
    agency_id = agency_overrides.get("id") or f"{ctx.page_url}{agency_id_suffix}"

    agency_node: Dict[str, Any] = {
        "@type": "InsuranceAgency",
        "@id": agency_id,
        "name": ctx.name,
        "description": ctx.description,
        "areaServed": area_served,
        "url": ctx.page_url,
    }
    if agency_identifier:
        agency_node["identifier"] = agency_identifier
    if agency_logo:
        agency_node["logo"] = agency_logo
    if addresses:
        agency_node["address"] = addresses
    if agency_same_as:
        agency_node["sameAs"] = agency_same_as

    graph.append(agency_node)

    offer_defaults = defaults.get("offer", {})
    offer_overrides = overrides.get("offer", {})
    offer_id_suffix = offer_overrides.get("id_suffix", offer_defaults.get("id_suffix", "#offer"))
    offer_id = offer_overrides.get("id") or f"{ctx.page_url}{offer_id_suffix}"
    offer_name = offer_overrides.get("name", offer_defaults.get("name", ctx.name))
    offer_price_currency = offer_overrides.get("price_currency", offer_defaults.get("price_currency", "ARS"))
    offer_availability = offer_overrides.get("availability", offer_defaults.get("availability", "https://schema.org/InStock"))
    offer_area_served = offer_overrides.get("area_served", offer_defaults.get("area_served", "AR"))
    offer_eligible_region = offer_overrides.get("eligible_region", offer_defaults.get("eligible_region", "AR"))
    offer_price = offer_overrides.get("price", offer_defaults.get("price", "0")) or "0"
    price_valid_until = offer_overrides.get("price_valid_until") or default_price_valid_until()

    offer = build_offer_node(
        ctx.page_url,
        offer_id,
        {
            "name": offer_name,
            "priceCurrency": offer_price_currency,
            "availability": offer_availability,
            "areaServed": offer_area_served,
            "eligibleRegion": offer_eligible_region,
            "priceValidUntil": price_valid_until,
            "price": offer_price,
        },
    )
    graph.append(offer)

    product_defaults = defaults.get("product", {})
    product_overrides = overrides.get("product", {})
    product_id_suffix = product_overrides.get("id_suffix", product_defaults.get("id_suffix", "#producto"))
    product_id = product_overrides.get("id") or f"{ctx.page_url}{product_id_suffix}"

    product = build_product_node(
        ctx.page_url,
        product_id,
        ctx.name,
        ctx.image_url,
        ctx.aggregate_rating,
        description=ctx.description,
        extra={"url": ctx.page_url, "offers": {"@id": offer_id}},
    )
    product_category = product_overrides.get("category", product_defaults.get("category"))
    if product_category:
        product["category"] = product_category
    graph.append(product)

    faq_page = build_faq_page(ctx.page_url, ctx.faqs, f"{ctx.page_url}#FAQPage")
    if faq_page:
        graph.append(faq_page)

    graph.append(build_webpage_node(ctx))

    append_organization(graph, resolve_organization({"@id": agency_id}, "naranja_x"), added_orgs)

    return graph


SCHEMA_BUILDERS: Dict[str, Callable[..., List[Dict[str, Any]]]] = {
    "payment_card": build_payment_card_graph,
    "loan_or_credit": build_loan_or_credit_graph,
    "bank_account": build_bank_account_graph,
    "payment_service": build_payment_service_graph,
    "investment_or_deposit": build_investment_or_deposit_graph,
    "insurance_agency": build_insurance_agency_graph,
    "financial_product": build_financial_product_graph,
    "blog_posting": build_blog_posting_graph,
}
