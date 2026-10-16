"""Outlier multiple: alcance de cada publicación / mediana de las 12 anteriores.

Método del skill ig-audit / ig-viral (github.com/Jakeschincariol/instagram-agent-skill):
el alcance bruto engaña cuando la cuenta crece; lo que se puede copiar es lo que
superó claramente a su propio contexto. > 3x = señal; < 1.5x = un día normal.

Uso:
    python instagram/outliers.py      # escribe informes/outliers.md
"""
from pathlib import Path

import pandas as pd

BASE = Path(__file__).parent
OUT = BASE / "informes" / "outliers.md"
VENTANA = 12


def main() -> None:
    p = pd.read_csv(BASE / "data" / "publicaciones_12m.csv", parse_dates=["fecha"]).sort_values("fecha")
    p["mediana_prev"] = p["alcance"].shift(1).rolling(VENTANA, min_periods=6).median()
    p["multiple"] = (p["alcance"] / p["mediana_prev"]).round(1)
    p["envios_pct"] = p["compartidos"] / p["alcance"]
    p = p.dropna(subset=["multiple"])

    out = ["# Outliers: publicaciones que superaron a su propio contexto\n",
           f"Múltiplo = alcance / mediana de las {VENTANA} publicaciones anteriores. "
           f"{len(p)} publicaciones evaluadas (las 6 primeras no tienen historial suficiente).\n"]

    p["nivel"] = pd.cut(p["multiple"], [0, 1.5, 3, 1e9], labels=["normal (<1,5x)", "bueno (1,5-3x)", "outlier (>3x)"])
    out.append("## Reparto\n\n| nivel | publicaciones |\n|---|---|")
    for k, v in p["nivel"].value_counts().sort_index().items():
        out.append(f"| {k} | {v} |")

    out.append("\n## Tasa de outliers por tema y CTA (temas con ≥ 5 publicaciones)\n")
    g = p.groupby("tema").agg(posts=("multiple", "size"), mediana_x=("multiple", "median"),
                              outliers=("multiple", lambda s: (s > 3).sum()))
    g = g[g["posts"] >= 5].sort_values("mediana_x", ascending=False)
    out.append("| tema | posts | múltiplo mediano | outliers >3x |\n|---|---|---|---|")
    for t, r in g.iterrows():
        out.append(f"| {t} | {r.posts} | {r.mediana_x:.2f}x | {r.outliers} |")
    gc = p.groupby("cta").agg(posts=("multiple", "size"), mediana_x=("multiple", "median"),
                              outliers=("multiple", lambda s: (s > 3).sum()))
    out.append("\n| cta | posts | múltiplo mediano | outliers >3x |\n|---|---|---|---|")
    for t, r in gc.iterrows():
        out.append(f"| {t} | {r.posts} | {r.mediana_x:.2f}x | {r.outliers} |")

    out.append("\n## Todos los outliers (>3x)\n")
    out.append("| fecha | múltiplo | alcance | mediana previa | tema | cta | envíos/alcance | publicación |\n|---|---|---|---|---|---|---|---|")
    for r in p[p["multiple"] > 3].sort_values("multiple", ascending=False).itertuples():
        out.append(f"| {r.fecha:%Y-%m-%d} | **{r.multiple}x** | {r.alcance:,.0f} | {r.mediana_prev:,.0f} | {r.tema} | {r.cta} | "
                   f"{r.envios_pct:.1%} | {r.resumen} |")

    OUT.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"Escrito {OUT}")


if __name__ == "__main__":
    main()
