"""Persistencia en disco de los resultados de schema."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Iterable

import pandas as pd

from ..models import SchemaRecord

logger = logging.getLogger(__name__)


def _ensure_parent(path: Path) -> None:
    if not path.parent.exists():
        path.parent.mkdir(parents=True, exist_ok=True)


def save_outputs(
    record: SchemaRecord,
    *,
    csv_path: str = "extracciones.csv",
    jsonl_path: str = "schemas.jsonl",
) -> None:
    """Guarda un registro en CSV y JSONL, acumulando resultados."""
    csv_file = Path(csv_path)
    jsonl_file = Path(jsonl_path)

    _ensure_parent(csv_file)
    _ensure_parent(jsonl_file)

    row = {
        "url": record.url,
        "name": record.name,
        "title": record.extracted.title,
        "description": record.extracted.description,
        "image": record.extracted.image,
        "faqs_count": len(record.extracted.faqs),
        "faqs_json": json.dumps(record.extracted.faqs, ensure_ascii=False),
    }

    try:
        existing = pd.read_csv(csv_file)
    except FileNotFoundError:
        df = pd.DataFrame([row])
    except pd.errors.EmptyDataError:
        df = pd.DataFrame([row])
    except Exception:
        logger.exception("No se pudo leer %s", csv_file)
        raise
    else:
        df = pd.concat([existing, pd.DataFrame([row])], ignore_index=True)

    df.to_csv(csv_file, index=False)

    with jsonl_file.open("a", encoding="utf-8") as fh:
        fh.write(
            json.dumps({"url": record.url, "schema": record.schema}, ensure_ascii=False)
            + "\n"
        )


def as_script_tag(obj: dict, *, indent: int = 2) -> str:
    """Serializa un grafo JSON-LD como etiqueta <script> lista para embeber."""
    payload = json.dumps(obj, ensure_ascii=False, indent=indent)
    return f'<script type="application/ld+json">\n{payload}\n</script>'
