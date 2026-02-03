"""Paquete principal para la automatización de schemas de Naranja X."""

from .infrastructure.http import (
    FetchError,
    PageNotFoundError,
    RateLimitError,
    ServerError,
    clear_cache,
    get_cache_stats,
)
from .service.workflow import build_schema_from_url, generate_schema
from .validation import (
    SchemaValidationError,
    SchemaValidationResult,
    SchemaValidator,
    validate_schema,
)

__all__ = [
    # Workflow
    "build_schema_from_url",
    "generate_schema",
    # Validación
    "SchemaValidationError",
    "SchemaValidationResult",
    "SchemaValidator",
    "validate_schema",
    # HTTP errors
    "FetchError",
    "PageNotFoundError",
    "RateLimitError",
    "ServerError",
    # Cache utilities
    "clear_cache",
    "get_cache_stats",
]
