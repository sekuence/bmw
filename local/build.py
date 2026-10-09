"""Genera el HTML autocontenido de la versión local (sin servidor) a partir
de la plantilla y del código fuente real de src/*.py -byte a byte, sin
transcribir nada a mano- para que nunca se desincronice de la app de
Streamlit. Ejecutar: python3 local/build.py"""
import base64
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOCAL = ROOT / "local"
TEMPLATE = LOCAL / "app_template.html"
OUTPUT = ROOT / "seguimiento_local.html"


def python_module_tag(vpath: str, content: str) -> str:
    return f'<script type="text/python" data-vpath="{vpath}">\n{content}\n</script>'


def data_file_tag(vpath: str, content_bytes: bytes) -> str:
    b64 = base64.b64encode(content_bytes).decode("ascii")
    return f'<script type="text/plain" data-vpath="{vpath}" data-encoding="base64">\n{b64}\n</script>'


def build() -> None:
    modules = [python_module_tag("src/__init__.py", (ROOT / "src" / "__init__.py").read_text(encoding="utf-8"))]
    for f in sorted((ROOT / "src").glob("*.py")):
        if f.name == "__init__.py":
            continue
        content = (LOCAL / "storage_browser.py").read_text(encoding="utf-8") if f.name == "storage.py" else f.read_text(encoding="utf-8")
        modules.append(python_module_tag(f"src/{f.name}", content))
    modules.append(python_module_tag("browser_views.py", (LOCAL / "browser_views.py").read_text(encoding="utf-8")))

    data_files = [
        data_file_tag("data/dealers.csv", (ROOT / "data" / "dealers.csv").read_bytes()),
        data_file_tag("data/objetivos_default.csv", (ROOT / "data" / "objetivos_default.csv").read_bytes()),
        data_file_tag("data/plantilla_seguimiento.xlsx", (ROOT / "data" / "plantilla_seguimiento.xlsx").read_bytes()),
    ]

    app_js = (LOCAL / "app.js").read_text(encoding="utf-8")

    html = TEMPLATE.read_text(encoding="utf-8")
    html = html.replace("<!--PYTHON_MODULES-->", "\n".join(modules))
    html = html.replace("<!--DATA_FILES-->", "\n".join(data_files))
    html = html.replace("<!--APP_JS-->", app_js)

    OUTPUT.write_text(html, encoding="utf-8")
    print(f"Escrito {OUTPUT} ({OUTPUT.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    build()
