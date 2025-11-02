"""Modelos de dominio usados durante la generación de schemas."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class SchemaContext:
    page_url: str
    name: str
    description: Optional[str]
    image_url: Optional[str]
    faqs: List[Dict[str, str]]
    body_text: Optional[str]
    aggregate_rating: Optional[Dict[str, Any]]


@dataclass
class ExtractionResult:
    title: str
    description: str
    image: str
    faqs: List[Dict[str, str]]
    body_text: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "description": self.description,
            "image": self.image,
            "faqs": self.faqs,
            "body_text": self.body_text,
        }


@dataclass
class SchemaRecord:
    url: str
    name: str
    schema_type: str
    extracted: ExtractionResult
    schema: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "url": self.url,
            "name": self.name,
            "schema_type": self.schema_type,
            "extracted": self.extracted.to_dict(),
            "schema": self.schema,
        }
