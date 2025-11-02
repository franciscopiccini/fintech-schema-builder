"""Paquete principal para la automatización de schemas de Naranja X."""

from .service.workflow import build_schema_from_url, generate_schema

__all__ = ["build_schema_from_url", "generate_schema"]
