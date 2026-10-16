"""Convierte exportaciones JSON de Windsor.ai (conector instagram) a CSV y une el histórico.

Cada JSON en data/raw/ se convierte con una clasificación automática de tema/CTA por
palabras clave. Los CSV ya clasificados a mano (publicaciones*.csv) tienen prioridad:
si un shortcode aparece en ellos, se respeta su clasificación.

Uso:
    python instagram/importar_windsor.py      # escribe data/publicaciones_12m.csv
"""
import json
import re
import unicodedata
from pathlib import Path

import pandas as pd

BASE = Path(__file__).parent
DATA = BASE / "data"
SALIDA = DATA / "publicaciones_12m.csv"

COLUMNAS = ["fecha", "hora_utc", "tipo", "shortcode", "alcance", "vistas", "likes", "comentarios",
            "guardados", "compartidos", "ver_medio_ms", "skip_rate", "cta", "palabra_clave", "tema",
            "resumen"]

# Orden importa: el primer tema que encaje gana.
TEMAS = [
    ("lesiones", r"lesi[oó]n|rodilla|periostitis|fascitis|tibia|dolor|molestia|foam roller"),
    ("marca", r"@asics|#asics|frontrunner|@deporvillage|@onnatribe|test gel|patrocinador"),
    ("noticia", r"r[eé]cord|kipchoge|hist[oó]ric|behobia|nueva york 2025"),
    ("fuerza", r"fuerza|pliometr|core|gym|crossfit"),
    ("nutricion", r"cafe[ií]na|comer|carbohidrat|nutrici|prote[ií]na|suplement"),
    ("principiantes", r"empezar a correr|empieza|comenzar|principiante|caco|5k"),
    ("tecnica", r"zona 2|pisada|t[eé]cnica|estira|calent|ritmo|velocidad|vestirte|recuperaci"),
    ("personal", r"marat[oó]n|meta|venecia|recap|libres|familia"),
    ("mentalidad", r"mente|mental|identidad|sabote|disciplina|dolor emocional|suficiente"),
]


def _sin_tildes(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def clasificar(caption: str) -> tuple[str, str, str]:
    texto = (caption or "").lower()
    tema = next((t for t, rx in TEMAS if re.search(rx, texto)), "otro")
    m = re.search(r"\b(?:comenta|escr[ií]beme)\b(?:\s+la\s+palabra)?\s*[“\"']?"
                  r"([^\s“”\"'.,!]{1,15}(?:\s2)?)",
                  caption or "", flags=re.IGNORECASE)
    clave = _sin_tildes(m.group(1)).upper().strip() if m else ""
    sigue = bool(re.search(r"s[ií]gueme", texto))
    if clave and sigue:
        cta = "comenta+sigueme"
    elif clave:
        cta = "comenta"
    elif sigue:
        cta = "sigueme"
    else:
        cta = "ninguna"
    return tema, cta, clave


def desde_json(ruta: Path) -> pd.DataFrame:
    filas = []
    for r in json.loads(ruta.read_text(encoding="utf-8"))["data"]:
        tema, cta, clave = clasificar(r.get("media_caption"))
        cap = (r.get("media_caption") or "").split("\n")[0][:90]
        tipo = {"CAROUSEL_ALBUM": "CARRUSEL", "REELS": "REEL", "VIDEO": "REEL"}.get(r["media_type"], r["media_type"])
        filas.append({
            "fecha": r["date"], "hora_utc": None, "tipo": tipo,
            "shortcode": r["media_permalink"].rstrip("/").split("/")[-1],
            "alcance": r.get("media_reach"), "vistas": r.get("media_views"),
            "likes": r.get("media_like_count"), "comentarios": r.get("media_comments_count"),
            "guardados": r.get("media_saved"), "compartidos": r.get("media_shares"),
            "ver_medio_ms": r.get("media_reel_avg_watch_time"), "skip_rate": r.get("media_reel_skip_rate"),
            "cta": cta, "palabra_clave": clave, "tema": tema, "resumen": cap,
        })
    return pd.DataFrame(filas, columns=COLUMNAS)


def main() -> None:
    manuales = [pd.read_csv(p) for p in sorted(DATA.glob("publicaciones*.csv")) if p != SALIDA]
    auto = [desde_json(p) for p in sorted((DATA / "raw").glob("*.json"))]
    df = pd.concat(manuales + auto, ignore_index=True)
    df = df.drop_duplicates("shortcode", keep="first").sort_values("fecha")
    manual = DATA / "clasificacion_manual.csv"
    if manual.exists():
        temas = pd.read_csv(manual).set_index("shortcode")["tema"]
        df["tema"] = df["shortcode"].map(temas).fillna(df["tema"])
    df.to_csv(SALIDA, index=False)
    print(f"{len(df)} publicaciones → {SALIDA} ({df['fecha'].min()} a {df['fecha'].max()})")


if __name__ == "__main__":
    main()
