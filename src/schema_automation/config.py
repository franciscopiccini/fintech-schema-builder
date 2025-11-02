"""Constantes y configuración compartida para la generación de schemas."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Dict, List

# Fechas y rating por defecto -------------------------------------------------

DEFAULT_PRICE_VALIDITY_DAYS = 365


def default_price_valid_until(days: int = DEFAULT_PRICE_VALIDITY_DAYS) -> str:
    """Devuelve una fecha ISO usada como `priceValidUntil` por defecto."""
    return (date.today() + timedelta(days=days)).isoformat()


DEFAULT_AGG_RATING = {
    "@type": "AggregateRating",
    "ratingValue": 4.6,
    "ratingCount": 991000,
    "bestRating": 5,
    "worstRating": 1,
}

DEFAULT_LANGUAGE = "es-AR"

# Organizaciones y direcciones -------------------------------------------------

ORGANIZATIONS: Dict[str, Dict[str, object]] = {
    "tarjeta_naranja": {
        "@type": "Organization",
        "@id": "https://www.naranjax.com/#OrgTarjetaNaranja",
        "name": "Tarjeta Naranja S.A.U.",
        "url": "https://www.naranjax.com/",
        "logo": {
            "@type": "ImageObject",
            "@id": "https://www.naranjax.com/#LogoTarjetaNaranja",
            "url": "https://images.ctfassets.net/yxlyq25bynna/1IxKUBv3dtISflaWQoSIZW/11e239808ff23ee64b26ba44bfcd93a0/Logo_NX.jpeg",
            "contentUrl": "https://images.ctfassets.net/yxlyq25bynna/1IxKUBv3dtISflaWQoSIZW/11e239808ff23ee64b26ba44bfcd93a0/Logo_NX.jpeg",
        },
        "sameAs": [],
        "identifier": {
            "@type": "PropertyValue",
            "propertyID": "CUIT",
            "value": "30-68537634-9",
        },
    },
    "naranja_digital": {
        "@type": "Organization",
        "@id": "https://www.naranjax.com/#OrgNaranjaDigital",
        "name": "Naranja Digital Compañía Financiera S.A.U.",
        "url": "https://www.naranjax.com/",
        "logo": {
            "@type": "ImageObject",
            "@id": "https://www.naranjax.com/#LogoNaranjaDigital",
            "url": "https://images.ctfassets.net/yxlyq25bynna/1IxKUBv3dtISflaWQoSIZW/11e239808ff23ee64b26ba44bfcd93a0/Logo_NX.jpeg",
            "contentUrl": "https://images.ctfassets.net/yxlyq25bynna/1IxKUBv3dtISflaWQoSIZW/11e239808ff23ee64b26ba44bfcd93a0/Logo_NX.jpeg",
        },
        "sameAs": [],
        "identifier": {
            "@type": "PropertyValue",
            "propertyID": "CUIT",
            "value": "30-68537634-9",
        },
    },
    "naranja_x": {
        "@type": "Organization",
        "@id": "https://www.naranjax.com/#OrgNaranjaX",
        "name": "Naranja X",
        "url": "https://www.naranjax.com/",
        "logo": {
            "@type": "ImageObject",
            "@id": "https://www.naranjax.com/#LogoNaranjaX",
            "url": "https://images.ctfassets.net/yxlyq25bynna/1IxKUBv3dtISflaWQoSIZW/11e239808ff23ee64b26ba44bfcd93a0/Logo_NX.jpeg",
            "contentUrl": "https://images.ctfassets.net/yxlyq25bynna/1IxKUBv3dtISflaWQoSIZW/11e239808ff23ee64b26ba44bfcd93a0/Logo_NX.jpeg",
        },
        "sameAs": [
            "https://www.linkedin.com/company/naranja-x/",
            "https://twitter.com/naranjax",
        ],
        "identifier": {
            "@type": "PropertyValue",
            "propertyID": "CUIT",
            "value": "30-68537634-9",
        },
    },
}

NARANJA_X_ADDRESSES: List[Dict[str, object]] = [
    {
        "@type": "PostalAddress",
        "name": "Casa Naranja",
        "streetAddress": "La Tablada 451",
        "addressLocality": "Córdoba",
        "addressRegion": "Córdoba",
        "postalCode": "X5000",
        "addressCountry": "AR",
    },
    {
        "@type": "PostalAddress",
        "name": "Naranja X Buenos Aires",
        "streetAddress": "Leiva 4070",
        "addressLocality": "Ciudad Autónoma de Buenos Aires",
        "addressRegion": "Buenos Aires",
        "postalCode": "C1427BQA",
        "addressCountry": "AR",
    },
]

WEBPAGE_DEFAULTS = {
    "@type": "WebPage",
    "inLanguage": DEFAULT_LANGUAGE,
    "isPartOf": {
        "@type": "WebSite",
        "@id": "https://www.naranjax.com/#website",
    },
    "publisher": {"@id": ORGANIZATIONS["tarjeta_naranja"]["@id"]},
}

# Defaults de productos -------------------------------------------------------

PRICE_SPEC_DEFAULT = {
    "TNA": {"min": 55, "max": 153},
    "TEA": {"min": 71.22, "max": 322.08},
    "CFTEA": {"min": 91.11, "max": 459.39},
}

PAYMENT_SERVICE_DEFAULTS = {
    "area_served": {"@type": "Country", "name": "Argentina"},
    "provider": {
        "org_key": "naranja_x",
    },
    "offer": {
        "price_currency": "ARS",
        "eligible_region": "AR",
    },
}

INSURANCE_AGENCY_DEFAULTS = {
    "agency": {
        "id_suffix": "#insurance-agency",
        "area_served": {"@type": "AdministrativeArea", "name": "Argentina"},
        "addresses": NARANJA_X_ADDRESSES,
        "identifier": {
            "propertyID": "CUIT",
            "value": "30-68537634-9",
        },
        "logo": {
            "id": "https://images.ctfassets.net/yxlyq25bynna/1IxKUBv3dtISflaWQoSIZW/11e239808ff23ee64b26ba44bfcd93a0/Logo_NX.jpeg",
            "url": "https://images.ctfassets.net/yxlyq25bynna/1IxKUBv3dtISflaWQoSIZW/11e239808ff23ee64b26ba44bfcd93a0/Logo_NX.jpeg",
            "contentUrl": "https://images.ctfassets.net/yxlyq25bynna/1IxKUBv3dtISflaWQoSIZW/11e239808ff23ee64b26ba44bfcd93a0/Logo_NX.jpeg",
        },
        "same_as": [],
    },
    "product": {
        "id_suffix": "#producto",
        "category": "Insurance",
    },
    "offer": {
        "id_suffix": "#offer-basica",
        "name": "Cobertura Básica",
        "price_currency": "ARS",
        "availability": "https://schema.org/InStock",
        "area_served": "AR",
        "eligible_region": "AR",
    },
}

FINANCIAL_PRODUCT_ZERO_RATES = {
    "TNA": 0,
    "TEA": 0,
    "CFT": 0,
}

LOAN_OR_CREDIT_DEFAULTS = {
    "amount": {
        "currency": "ARS",
        "minValue": 10000,
        "maxValue": 9000000,
    },
    "currency": "ARS",
    "loan_term": {
        "@type": "QuantitativeValue",
        "maxValue": 48,
        "unitText": "MONTH",
    },
    "interest_rate": {
        "minValue": 55.0,
        "maxValue": 153.0,
        "unitText": "PERCENT",
    },
    "annual_percentage_rate": {
        "minValue": 91.11,
        "maxValue": 459.39,
        "unitText": "PERCENT",
    },
    "loan_repayment_form": {
        "@type": "RepaymentSpecification",
        "name": "Sistema de amortización francés",
        "description": "Cuotas fijas mensuales con interés fijo durante todo el plazo (método francés).",
    },
}

FINANCIAL_PRODUCT_DEFAULTS = {
    "area_served": "AR",
    "provider": {
        "org_key": "tarjeta_naranja",
    },
    "offer": {
        "price_currency": "ARS",
        "billing_increment": "1",
        "min_price": "0",
        "area_served": "AR",
        "valid_from_offset": 0,
        "valid_through_offset": 30,
        "description_template": "Hasta 3 cuotas sin interés. {rates_text}.",
    },
    "product": {
        "id_suffix": "#financial-product",
    },
    "faq_id_suffix": "#FAQPage",
}

INVESTMENT_OR_DEPOSIT_DEFAULTS = {
    "area_served": "AR",
    "globals": {
        "duration": "",
        "interest_rate": "",
    },
    "provider": {
        "org_key": "naranja_x",
        "overrides": {
            "logo": {
                "@type": "ImageObject",
                "@id": "https://www.naranjax.com/#LogoNaranjaXInvestment",
                "url": "https://images.ctfassets.net/yxlyq25bynna/5aunl52F9uDLxXLUC8L7O4/b025683cc1824c386a19c478a5dd46ae/isologo-naranjax.png",
                "contentUrl": "https://images.ctfassets.net/yxlyq25bynna/5aunl52F9uDLxXLUC8L7O4/b025683cc1824c386a19c478a5dd46ae/isologo-naranjax.png",
            }
        },
    },
    "investment": {
        "id_suffix": "#producto",
        "types": ["InvestmentOrDeposit"],
        "alternate_name": "Ahorro por objetivos con TNA",
        "service_type": "Ahorro por objetivos con interés (TNA)",
        "audience": {
            "@type": "Audience",
            "audienceType": "Usuarios de banca minorista en Argentina",
        },
        "interest_rate": {
            "type": "QuantitativeValue",
            "unit_text": "TNA",
        },
    },
    "offer": {
        "id_suffix": "#offer",
        "price_currency": "ARS",
        "area_served": "AR",
        "eligible_region": "AR",
        "availability": "https://schema.org/InStock",
        "valid_from_offset": 0,
        "valid_through_offset": 28,
    },
    "product": {
        "id_suffix": "#product",
    },
    "faq_id_suffix": "#FAQPage",
}

# Catálogos -------------------------------------------------------------------

OFFER_CATALOGS: Dict[str, Dict[str, object]] = {
    "prestamos": {
        "name": "Catálogo de Préstamos",
        "items": [
            {
                "name": "Préstamos para monotributistas",
                "url": "https://www.naranjax.com/prestamos/monotributistas",
                "id_suffix": "#LoanOrCredit",
            },
            {
                "name": "Préstamos express",
                "url": "https://www.naranjax.com/prestamos/express",
                "id_suffix": "#LoanOrCredit",
            },
            {
                "name": "Préstamos para viajes",
                "url": "https://www.naranjax.com/prestamos/viajes",
                "id_suffix": "#LoanOrCredit",
            },
        ],
    },
    "tarjeta_credito": {
        "name": "Catálogo de Tarjetas de Crédito",
        "items": [
            {
                "name": "Tarjeta Naranja X",
                "url": "https://www.naranjax.com/tarjetas-de-credito/tarjeta-naranja",
                "id_suffix": "#PaymentCard",
            },
            {
                "name": "Tarjeta Naranja X Visa",
                "url": "https://www.naranjax.com/tarjetas-de-credito/tarjeta-naranja-visa",
                "id_suffix": "#PaymentCard",
            },
            {
                "name": "Tarjeta Naranja X Mastercard",
                "url": "https://www.naranjax.com/tarjetas-de-credito/tarjeta-naranja-mastercard",
                "id_suffix": "#PaymentCard",
            },
        ],
    },
    "seguros": {
        "name": "Catálogo de Seguros",
        "items": [
            {
                "name": "Seguro de Vida",
                "url": "https://www.naranjax.com/seguros/vida",
                "id_suffix": "#producto",
            },
            {
                "name": "Seguro para Celulares",
                "url": "https://www.naranjax.com/seguros/celulares",
                "id_suffix": "#producto",
            },
            {
                "name": "Seguro para Hogar",
                "url": "https://www.naranjax.com/seguros/hogar",
                "id_suffix": "#producto",
            },
        ],
    },
    "cuenta": {
        "name": "Catálogo de Cuentas",
        "items": [
            {
                "name": "Cuenta Remunerada",
                "url": "https://www.naranjax.com/cuenta-remunerada",
                "id_suffix": "#bankaccount",
            },
            {
                "name": "Cuenta en Dólares",
                "url": "https://www.naranjax.com/cuenta-dolar",
                "id_suffix": "#bankaccount",
            },
            {
                "name": "Caja de Ahorro",
                "url": "https://www.naranjax.com/cuentagratuitauniversal",
                "id_suffix": "#bankaccount",
            },
        ],
    },
}
