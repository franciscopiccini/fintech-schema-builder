"""Servidor MCP que expone el generador de schemas como herramientas.

Permite usar el proyecto desde cualquier carpeta sin recordar la interfaz del
CLI. Arranca solo, por stdio, y no requiere tener nada levantado: el cliente lo
lanza cuando lo necesita.

Uso directo (sin cliente MCP), util para probar que levanta:

    python mcp_server.py

Registro en Claude Code, desde la carpeta donde se quiera usar:

    claude mcp add schemas -- /ruta/al/.venv/bin/python /ruta/al/mcp_server.py

Para quitarlo:

    claude mcp remove schemas
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional

# El paquete vive en src/; se agrega al path para no depender de que este
# instalado en el entorno que ejecuta este archivo.
sys.path.insert(0, str(Path(__file__).parent / "src"))

# MCPServer se llamaba FastMCP en el SDK 1.x; en 2.x cambio el nombre.
from mcp.server.mcpserver import MCPServer  # noqa: E402

from schema_automation.infrastructure.http import FetchError  # noqa: E402
from schema_automation.models import SchemaContext  # noqa: E402
from schema_automation.schema import SCHEMA_BUILDERS  # noqa: E402
from schema_automation.service.workflow import build_schema_from_url  # noqa: E402
from schema_automation.validation import validate_schema  # noqa: E402

mcp = MCPServer("naranja-x-schemas")

# Señales de que lo descargado no es la pagina pedida sino un error o un muro
# anti-bot. Se comparan en minusculas contra el titulo extraido.
_TITULOS_SOSPECHOSOS = (
    "404", "not found", "error", "403", "forbidden",
    "access denied", "just a moment", "attention required",
)


def _detectar_pagina_equivocada(url_pedida: str, record: Any) -> Optional[str]:
    """Devuelve un aviso si lo descargado no parece ser la pagina pedida.

    Un redirect a /404 o un challenge anti-bot devuelven HTTP 200, asi que el
    pipeline sigue de largo y arma un schema valido del contenido equivocado.
    """
    titulo = (record.extracted.title or "").strip()
    url_final = record.schema.get("@graph", [{}])[0].get("url", "") or ""

    motivos = []
    if any(s in titulo.lower() for s in _TITULOS_SOSPECHOSOS):
        motivos.append(f"el titulo extraido es {titulo!r}")
    if url_final and url_final.rstrip("/") != url_pedida.rstrip("/"):
        motivos.append(f"la pagina redirigio a {url_final}")

    if not motivos:
        return None

    return (
        "No se genero el schema: lo descargado no parece ser la pagina pedida.\n"
        f"  URL pedida: {url_pedida}\n"
        + "".join(f"  - {m}\n" for m in motivos)
        + "\nEl sitio puede estar redirigiendo o bloqueando al cliente HTTP. "
        "Verificar la URL en el browser, y si la pagina existe usar "
        "generar_schema_sin_fetch pasando el contenido a mano."
    )

TIPOS = ", ".join(SCHEMA_BUILDERS)


@mcp.tool()
def generar_schema_desde_url(
    url: str,
    nombre: str,
    schema_type: str = "payment_card",
    validar: bool = True,
) -> str:
    """Genera el JSON-LD de una URL: descarga la pagina, extrae metadata y FAQs.

    Args:
        url: URL de la pagina a procesar.
        nombre: Nombre legible del producto (va al campo `name`).
        schema_type: Uno de: payment_card, loan_or_credit, bank_account,
            payment_service, investment_or_deposit, insurance_agency,
            financial_product, blog_posting, event.
        validar: Si True agrega el resultado de la validacion al output.

    Returns:
        JSON-LD listo para pegar, con el reporte de validacion si se pidio.
    """
    if schema_type not in SCHEMA_BUILDERS:
        return f"schema_type invalido: {schema_type!r}. Validos: {TIPOS}"

    try:
        record = build_schema_from_url(url, nombre, schema_type)
    except FetchError as e:
        # El sitio puede responder con un challenge anti-bot en lugar del HTML.
        return (
            f"No se pudo descargar {url}: {type(e).__name__}: {e}\n"
            "Si la pagina existe en el browser, puede estar bloqueando al "
            "cliente HTTP. En ese caso usar generar_schema_sin_fetch pasando "
            "los datos a mano."
        )
    except Exception as e:
        return f"Error generando el schema: {type(e).__name__}: {e}"

    # El sitio puede redirigir a /404 o servir un challenge anti-bot y devolver
    # 200. Sin este chequeo el pipeline arma un schema perfectamente valido de
    # la pagina de error, con los @id apuntando a la URL equivocada.
    aviso = _detectar_pagina_equivocada(url, record)
    if aviso:
        return aviso

    salida = [json.dumps(record.schema, indent=2, ensure_ascii=False)]

    if validar:
        r = validate_schema(record.schema)
        salida.append(f"\n--- validacion ---\nvalido: {r.is_valid}")
        for e in r.errors:
            salida.append(f"  ERROR {e.path}: {e.message}")
        for w in r.warnings:
            salida.append(f"  warn  {w.path}: {w.message}")

    extracted = record.extracted
    salida.append(
        f"\n--- extraido de la pagina ---\n"
        f"  titulo: {extracted.title!r}\n"
        f"  descripcion: {extracted.description[:120]!r}\n"
        f"  FAQs encontradas: {len(extracted.faqs)}"
    )
    return "\n".join(salida)


@mcp.tool()
def generar_schema_sin_fetch(
    page_url: str,
    nombre: str,
    schema_type: str = "payment_card",
    descripcion: str = "",
    faqs_json: str = "[]",
) -> str:
    """Genera el JSON-LD sin descargar nada, con los datos pasados a mano.

    Sirve cuando la pagina bloquea al cliente HTTP o cuando todavia no existe.

    Args:
        page_url: URL que se usara para construir los @id y el campo url.
        nombre: Nombre legible del producto.
        schema_type: Uno de: payment_card, loan_or_credit, bank_account,
            payment_service, investment_or_deposit, insurance_agency,
            financial_product, blog_posting, event.
        descripcion: Texto para el campo `description`.
        faqs_json: Lista JSON de {"question": "...", "answer": "..."}.

    Returns:
        JSON-LD listo para pegar, con el reporte de validacion.
    """
    if schema_type not in SCHEMA_BUILDERS:
        return f"schema_type invalido: {schema_type!r}. Validos: {TIPOS}"

    try:
        faqs = json.loads(faqs_json)
    except json.JSONDecodeError as e:
        return f"faqs_json no es JSON valido: {e}"

    ctx = SchemaContext(
        page_url=page_url,
        name=nombre,
        description=descripcion or None,
        image_url=None,
        faqs=faqs,
        body_text=None,
        aggregate_rating=None,
    )
    try:
        graph = SCHEMA_BUILDERS[schema_type](ctx)
    except Exception as e:
        return f"Error generando el schema: {type(e).__name__}: {e}"

    doc: Dict[str, Any] = {"@context": "https://schema.org", "@graph": graph}
    r = validate_schema(doc)
    out = [json.dumps(doc, indent=2, ensure_ascii=False),
           f"\n--- validacion ---\nvalido: {r.is_valid}"]
    for e in r.errors:
        out.append(f"  ERROR {e.path}: {e.message}")
    for w in r.warnings:
        out.append(f"  warn  {w.path}: {w.message}")
    return "\n".join(out)


@mcp.tool()
def validar_jsonld(jsonld: str) -> str:
    """Valida un JSON-LD ya existente contra las reglas del proyecto.

    Args:
        jsonld: El documento JSON-LD como texto.

    Returns:
        Reporte de errores y advertencias.
    """
    try:
        doc = json.loads(jsonld)
    except json.JSONDecodeError as e:
        return f"No es JSON valido: {e}"

    r = validate_schema(doc)
    out = [f"valido: {r.is_valid}"]
    for e in r.errors:
        out.append(f"  ERROR {e.path}: {e.message}")
    for w in r.warnings:
        out.append(f"  warn  {w.path}: {w.message}")
    if not r.errors and not r.warnings:
        out.append("  sin errores ni advertencias")
    return "\n".join(out)


@mcp.tool()
def listar_tipos_de_schema() -> str:
    """Lista los tipos de schema que el generador soporta."""
    return "\n".join(f"  {t}" for t in SCHEMA_BUILDERS)


if __name__ == "__main__":
    mcp.run()
