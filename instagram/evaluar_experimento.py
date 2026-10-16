"""Evalúa el experimento de 4 semanas (plan/calendario.csv) contra las metas del plan.

Cruza el calendario (rellena la columna `shortcode` al publicar) con
data/publicaciones_12m.csv (regenerado con importar_windsor.py tras volcar el JSON
nuevo de Windsor en data/raw/). Escribe plan/resultados.md.

Uso:
    python instagram/importar_windsor.py
    python instagram/evaluar_experimento.py
"""
from pathlib import Path

import pandas as pd

BASE = Path(__file__).parent
CAL = BASE / "plan" / "calendario.csv"
PUB = BASE / "data" / "publicaciones_12m.csv"
OUT = BASE / "plan" / "resultados.md"

# Línea base: últimos 90 días antes del experimento (informe 01).
BASE_ALCANCE = 6010
BASE_SKIP = 0.479


def criterio(h: str, g: pd.DataFrame) -> tuple[str, str]:
    """Devuelve (estado, detalle) para la hipótesis h con sus publicaciones g."""
    if g.empty:
        return "pendiente", "sin publicaciones con datos"
    alc = g["alcance"].median()
    if h == "H1":
        ok = alc >= 15000 and g["guardados_pct"].median() >= 0.015
        return _e(ok), f"alcance mediano {alc:,.0f} (meta 15.000) · guardados {g['guardados_pct'].median():.2%} (meta 1,5 %)"
    if h == "H3":
        ok = alc >= 4000 and g["comentarios"].median() >= 80
        return _e(ok), f"alcance mediano {alc:,.0f} (meta 4.000) · comentarios mediana {g['comentarios'].median():.0f} (meta 80)"
    if h == "H4":
        comp = g["compartidos_pct"].median()
        return _e(comp >= 0.01), f"compartidos {comp:.2%} del alcance (meta 1 %) · alcance mediano {alc:,.0f}"
    if h == "H5":
        ratio = (g["alcance"] / g["alcance_original"]).median()
        return _e(ratio >= 0.30), f"alcance = {ratio:.0%} del original (meta 30 %)"
    if h == "H6":
        com = g["comentarios_pct"].median()
        return _e(alc >= 6000 and com >= 0.005), f"alcance mediano {alc:,.0f} (meta 6.000) · comentarios {com:.2%} (meta 0,5 %)"
    return "info", f"alcance mediano {alc:,.0f}"


def _e(ok: bool) -> str:
    return "✅ confirmada" if ok else "❌ no confirmada"


def cargar() -> pd.DataFrame:
    """Calendario cruzado con las métricas de cada publicación ya publicada."""
    cal = pd.read_csv(CAL, dtype=str)
    pub = pd.read_csv(PUB)
    for c in ["guardados", "compartidos", "comentarios"]:
        pub[f"{c}_pct"] = pub[c] / pub["alcance"]
    orig = pub.set_index("shortcode")["alcance"]

    df = cal.merge(pub.drop(columns=["fecha", "tema", "cta", "palabra_clave", "tipo"]),
                   on="shortcode", how="left")
    df["alcance_original"] = df["original_shortcode"].map(orig)
    for c in ["leads_dm", "llamadas", "ventas", "vistas_24h"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def estados(df: pd.DataFrame) -> list[tuple[str, str, str]]:
    """[(hipótesis, estado, detalle)] incluyendo el A/B de H2."""
    publicadas = df[df["alcance"].notna()]
    filas = [(h, *criterio(h, publicadas[publicadas["hipotesis"] == h]))
             for h in ["H1", "H3", "H4", "H5", "H6"]]
    ab = df[df["id"].isin(["15A", "15B"])].set_index("id")["vistas_24h"]
    if ab.notna().all() and len(ab) == 2:
        ganancia = ab["15B"] / ab["15A"] - 1
        filas.insert(1, ("H2", _e(ganancia >= 0.30),
                         f"valor primero {ab['15B']:,.0f} vs comenta primero {ab['15A']:,.0f} vistas 24 h "
                         f"({ganancia:+.0%}, meta +30 %)"))
    else:
        filas.insert(1, ("H2", "pendiente", "rellenar vistas_24h de 15A y 15B"))
    return filas


def main() -> None:
    cal = pd.read_csv(CAL, dtype=str)
    df = cargar()
    publicadas = df[df["alcance"].notna()]
    lineas = ["# Resultados del experimento\n",
              f"Publicaciones con datos: {len(publicadas)} de {len(cal)}\n"]

    if not publicadas.empty:
        lineas.append("## Global vs. línea base\n")
        lineas.append(f"- Alcance mediano: **{publicadas['alcance'].median():,.0f}** (base {BASE_ALCANCE:,}, meta 9.000)")
        reels = publicadas[publicadas["formato"] == "REEL"]
        if reels["skip_rate"].notna().any():
            lineas.append(f"- Skip rate mediano reels: **{reels['skip_rate'].median():.1%}** (base {BASE_SKIP:.1%}, meta ≤ 42 %)")
        lineas.append(f"- Guardados/alcance: **{publicadas['guardados_pct'].median():.2%}** (meta ≥ 1,2 %)")
        lineas.append(f"- Compartidos/alcance: **{publicadas['compartidos_pct'].median():.2%}** (meta ≥ 0,6 %)")
        if df["leads_dm"].notna().any():
            lineas.append(f"- Leads DM: **{df['leads_dm'].sum():.0f}** · llamadas {df['llamadas'].sum():.0f} · "
                          f"ventas {df['ventas'].sum():.0f} (meta ≥ 400 leads)")

    lineas.append("\n## Hipótesis\n")
    lineas.append("| Hipótesis | Estado | Detalle |\n|---|---|---|")
    for h, estado, det in estados(df):
        lineas.append(f"| {h} | {estado} | {det} |")

    lineas.append("\n## Detalle por publicación\n")
    cols = ["id", "fecha", "formato", "hipotesis", "titulo", "alcance", "guardados", "compartidos",
            "comentarios", "skip_rate", "leads_dm"]
    lineas.append("| " + " | ".join(cols) + " |\n|" + "---|" * len(cols))
    for _, r in df[cols].iterrows():
        lineas.append("| " + " | ".join("" if pd.isna(v) else str(v) for v in r) + " |")

    OUT.write_text("\n".join(lineas) + "\n", encoding="utf-8")
    print(f"Escrito {OUT}")


if __name__ == "__main__":
    main()
