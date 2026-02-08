# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Project Does

Automated Schema.org JSON-LD generation for Naranja X fintech products. Fetches a URL, extracts metadata (title, description, FAQs), and builds structured data graphs for 8 product types. Three interfaces: CLI, Python API, and Streamlit UI. Documentation and comments are in Spanish (Argentine market).

## Commands

```bash
# Install
pip install -e .          # production
pip install -e .[dev]     # with pytest + requests-mock

# Run tests (CI uses Python 3.11)
pytest

# CLI
python -m schema_automation.cli https://www.naranjax.com "Naranja X" --schema-type payment_card --schema-only
python -m schema_automation.cli https://www.naranjax.com "Naranja X" --schema-type payment_card --script

# Streamlit app
streamlit run streamlit_app.py
```

## Architecture

**Pipeline flow:** CLI/Streamlit → `workflow.py` → fetch HTML → extract metadata → build schema graph → validate → output

Key layers:
- **`service/workflow.py`** — Orchestration entry point. `generate_schema()` and `build_schema_from_url()` drive the entire pipeline.
- **`schema/`** — Builder-per-type pattern. Each builder (e.g., `payment_card.py`) returns a `List[Dict]` of JSON-LD `@graph` nodes. All builders are registered in `SCHEMA_BUILDERS` dict in `schema/__init__.py`. Shared helpers live in `base.py` (`deep_merge`, `build_offer_node`, `build_webpage_node`, etc.).
- **`extraction/`** — HTML parsing pipeline: `meta.py` (og: tags), `faqs.py` (accordion-specific + fallback strategies), `text.py` (body text).
- **`infrastructure/http.py`** — HTTP client with tenacity retry (3 attempts, exponential backoff) and requests-cache (15-min TTL, SQLite). Custom error hierarchy: `FetchError` → `PageNotFoundError`, `ServerError`, `RateLimitError`.
- **`infrastructure/persistence.py`** — Outputs to CSV/JSONL and `<script>` tag generation.
- **`validation/validator.py`** — JSON-LD structure validator checking schema.org types, required fields, URL formats.
- **`config.py`** — All hardcoded defaults: organizations, addresses, product specs, offer catalogs. Builders use `deep_merge()` to overlay schema-specific defaults on base config.
- **`models.py`** — Three dataclasses: `SchemaContext` (input), `ExtractionResult` (extracted metadata), `SchemaRecord` (final output).

## Key Patterns

- **Builder registration:** Add new schema types by creating a `build_*_graph(ctx, **kwargs)` function and registering it in `SCHEMA_BUILDERS` in `schema/__init__.py`.
- **JSON-LD IDs:** All nodes use `{page_url}#{NodeType}` format for `@id`. Organization references use `@id` pointers, not inline objects.
- **Config merging:** `deep_merge()` recursively combines base defaults with schema-specific overrides. Defaults are deep-copied to prevent mutation.
- **FAQ extraction:** Two strategies in `faqs.py` — Naranja X accordion-specific extraction and a generic fallback. Both tried in sequence.

## CI

GitHub Actions (`.github/workflows/ci.yml`): runs `pytest` on Python 3.11, triggered on push to `main` and all PRs. No linting or type-checking steps configured.

## Schema Types

`payment_card`, `loan_or_credit`, `bank_account`, `payment_service`, `investment_or_deposit`, `insurance_agency`, `financial_product`, `blog_posting`. Offer catalogs (separate): `prestamos`, `tarjeta_credito`, `seguros`, `cuenta`.
