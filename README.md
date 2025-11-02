# schema-automation

Herramientas para extraer contenido y generar grafos schema.org para productos y servicios de Naranja X.

## Instalación

```bash
pip install -e .
```

## Uso rápido

```python
from schema_automation.service.workflow import generate_schema

record = generate_schema(
    "https://www.naranjax.com",
    "Naranja X",
    schema_type="payment_card",
)
print(record["schema"])
```

### CLI

```bash
python -m schema_automation.cli https://www.naranjax.com "Naranja X" --schema-type payment_card --script
```

### Streamlit

```bash
streamlit run streamlit_app.py
```

La aplicación permite generar el schema como JSON o como etiqueta `<script>` lista para copiar. Para desplegarla en Streamlit Cloud:

1. Publica este repositorio en GitHub.
2. En Streamlit Cloud crea una app apuntando al archivo `streamlit_app.py` en la rama deseada.
3. Streamlit instalará automáticamente las dependencias listadas en `pyproject.toml`.

## Desarrollo

- Ejecuta `pytest` para correr las pruebas automatizadas.
- Usa `python -m schema_automation.cli --help` para ver las opciones disponibles.
