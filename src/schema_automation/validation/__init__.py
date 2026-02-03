"""Módulo de validación de schemas JSON-LD."""

from .validator import (
    SchemaValidationError,
    SchemaValidationResult,
    SchemaValidator,
    validate_schema,
)

__all__ = [
    "SchemaValidationError",
    "SchemaValidationResult",
    "SchemaValidator",
    "validate_schema",
]
