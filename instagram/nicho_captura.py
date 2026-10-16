"""Convierte la captura bruta del nicho en `data/nicho/captura.tsv` para `viral_ganchos.py`.

Entrada:
- `data/nicho/reels_raw.tsv`: los reels tal como los devolvió Manifold (una fila por reel, a mano o
  desde la API), con `pinned` = 1 para los fijados.
- `data/nicho/transcripciones.tsv`: primera frase hablada de los reels transcritos (`voz` = 0 si no
  hay voz, solo texto en pantalla y música).

Reglas (las mismas para todas las cuentas):
- Fuera: reels fijados (su antigüedad no es comparable) y reels con menos de 7 días (aún suman vistas).
- Mediana de la cuenta = mediana de vistas de sus reels válidos de los últimos 60 días; si hay menos
  de 8, la de sus últimos 12 válidos.
- Gancho = la primera frase hablada si está transcrita; si no, la primera frase del caption que no
  sea la petición de comentario ("Comenta X y te envío…"). Si el caption solo trae esa petición, el
  gancho real está en pantalla y no se ve desde los datos: se marca `gancho_visible` = 0.

Uso:
    python instagram/nicho_captura.py
"""
import re
from pathlib import Path

import pandas as pd

BASE = Path(__file__).parent / "data" / "nicho"
HOY = pd.Timestamp("2026-10-16")
CTA = re.compile(r"^\W*(?:comenta|escribe|escr[ií]beme)\b[^.!?]*[.!?]?\s*", re.IGNORECASE)
NO_ES = {"@dr.gabygo"}  # en inglés: sirve de referencia de formato, no para fórmulas en español


def main() -> None:
    r = pd.read_csv(BASE / "reels_raw.tsv", sep="\t")
    t = pd.read_csv(BASE / "transcripciones.tsv", sep="\t", keep_default_na=False)
    r["fecha"] = pd.to_datetime(r["fecha"])
    r["edad"] = (HOY - r["fecha"]).dt.days
    v = r[(r["pinned"] == 0) & (r["edad"] >= 7)].sort_values("fecha", ascending=False).copy()

    med = {}
    for acc, g in v.groupby("account"):
        w = g[g["edad"] <= 60]
        if len(w) < 8:
            w = g.head(12)
        med[acc] = w["views"].median()
        v.loc[g.index, "en_base"] = g.index.isin(w.index)
    v = v[v["en_base"]].copy()
    v["median"] = v["account"].map(med)

    v["cta_primero"] = v["caption_1"].str.match(CTA).astype(int)
    v["resto"] = v["caption_1"].str.replace(CTA, "", n=1, regex=True).str.strip()
    v = v.merge(t, on="url", how="left")
    hablado = v["voz"].eq("1") | v["voz"].eq(1)
    v["hook"] = v["primera_frase"].where(hablado & v["primera_frase"].ne(""), v["resto"])
    v["gancho_visible"] = (v["hook"].str.len() > 0).astype(int)
    v["hook"] = v["hook"].where(v["gancho_visible"] == 1, v["caption_1"])
    v["fuente_gancho"] = "caption"
    v.loc[hablado, "fuente_gancho"] = "voz"
    v.loc[v["voz"].isin([0, "0"]), "fuente_gancho"] = "caption (sin voz)"
    v["idioma"] = v["account"].map(lambda a: "en" if a in NO_ES else "es")

    cols = ["account", "followers", "median", "views", "hook", "length_s", "cta_primero",
            "gancho_visible", "fuente_gancho", "idioma", "fecha", "url"]
    v["fecha"] = v["fecha"].dt.strftime("%Y-%m-%d")
    v["median"] = v["median"].round().astype(int)
    v[cols].to_csv(BASE / "captura.tsv", sep="\t", index=False)
    print(f"captura.tsv: {len(v)} reels de {v['account'].nunique()} cuentas")
    print(pd.Series(med).round().astype(int).to_string())


if __name__ == "__main__":
    main()
