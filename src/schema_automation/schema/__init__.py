"""Capa de dominio para transformar datos en grafos schema.org."""

from typing import Any, Callable, Dict, List

from .base import (
    append_organization,
    build_faq_page,
    build_offer_node,
    build_product_node,
    build_webpage_node,
    deep_merge,
    organization_reference,
    resolve_organization,
)
from .bank_account import build_bank_account_graph
from .blog import build_blog_posting_graph
from .catalog import build_offer_catalog_node
from .event import build_event_graph
from .financial_product import build_financial_product_graph
from .insurance import build_insurance_agency_graph
from .investment import build_investment_or_deposit_graph
from .loan import build_loan_or_credit_graph
from .payment_card import build_payment_card_graph
from .payment_service import build_payment_service_graph

# Registro de builders por tipo de schema
SCHEMA_BUILDERS: Dict[str, Callable[..., List[Dict[str, Any]]]] = {
    "payment_card": build_payment_card_graph,
    "loan_or_credit": build_loan_or_credit_graph,
    "bank_account": build_bank_account_graph,
    "payment_service": build_payment_service_graph,
    "investment_or_deposit": build_investment_or_deposit_graph,
    "insurance_agency": build_insurance_agency_graph,
    "financial_product": build_financial_product_graph,
    "blog_posting": build_blog_posting_graph,
    "event": build_event_graph,
}

__all__ = [
    "SCHEMA_BUILDERS",
    "append_organization",
    "build_bank_account_graph",
    "build_blog_posting_graph",
    "build_event_graph",
    "build_faq_page",
    "build_financial_product_graph",
    "build_insurance_agency_graph",
    "build_investment_or_deposit_graph",
    "build_loan_or_credit_graph",
    "build_offer_catalog_node",
    "build_offer_node",
    "build_payment_card_graph",
    "build_payment_service_graph",
    "build_product_node",
    "build_webpage_node",
    "deep_merge",
    "organization_reference",
    "resolve_organization",
]
