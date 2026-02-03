"""Punto de entrada de Streamlit para schema-automation."""

import sys
from pathlib import Path

# Agregar src al path para Streamlit Cloud
src_path = Path(__file__).parent / "src"
if src_path.exists() and str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from schema_automation.interfaces.streamlit_app import main

if __name__ == "__main__":
    main()
