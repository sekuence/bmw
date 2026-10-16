"""Análisis de la cuenta de Instagram @healthyanii.

Lee los CSV de instagram/data/ y escribe las tablas de resultados en
instagram/informes/tablas.md. Uso:

    python instagram/analisis.py
"""
from pathlib import Path

import pandas as pd

BASE = Path(__file__).parent
DATA = BASE / "data"
OUT = BASE / "informes" / "tablas.md"

SEGUIDORES = 37007
CORTE_TRIMESTRE = "2026-07-18"


def cargar_publicaciones() -> pd.DataFrame:
    df = pd.read_csv(DATA / "publicaciones.csv", parse_dates=["fecha"])
    df["interacciones"] = df[["likes", "comentarios", "guardados", "compartidos"]].sum(axis=1)
    df["er_alcance"] = df["interacciones"] / df["alcance"]
    df["guardados_pct"] = df["guardados"] / df["alcance"]
    df["compartidos_pct"] = df["compartidos"] / df["alcance"]
    df["comentarios_pct"] = df["comentarios"] / df["alcance"]
    df["ver_medio_s"] = df["ver_medio_ms"] / 1000
    df["periodo"] = df["fecha"].map(
        lambda d: "Q2 (18 jul-15 oct)" if d >= pd.Timestamp(CORTE_TRIMESTRE) else "Q1 (18 abr-17 jul)"
    )
    df["dia_semana"] = df["fecha"].dt.day_name()
    df["hora_es"] = (df["hora_utc"] + 2) % 24  # CEST
    df["viral"] = df["alcance"] >= 30000
    return df


def resumen(g: pd.core.groupby.DataFrameGroupBy) -> pd.DataFrame:
    return g.agg(
        posts=("alcance", "size"),
        alcance_mediana=("alcance", "median"),
        alcance_medio=("alcance", "mean"),
        er_mediana=("er_alcance", "median"),
        guardados_pct=("guardados_pct", "median"),
        compartidos_pct=("compartidos_pct", "median"),
        comentarios_pct=("comentarios_pct", "median"),
        ver_medio_s=("ver_medio_s", "median"),
        skip_rate=("skip_rate", "median"),
        virales=("viral", "sum"),
    ).round(3)


def md(df: pd.DataFrame) -> str:
    """Tabla markdown sin depender de `tabulate`."""
    cab = [str(df.index.name or "")] + [str(c) for c in df.columns]
    filas = ["| " + " | ".join(cab) + " |", "|" + "---|" * len(cab)]
    for idx, fila in df.iterrows():
        celdas = [str(idx.date() if hasattr(idx, "date") else idx)]
        celdas += ["" if pd.isna(v) else str(v) for v in fila]
        filas.append("| " + " | ".join(celdas) + " |")
    return "\n".join(filas)


def main() -> None:
    p = cargar_publicaciones()
    d = pd.read_csv(DATA / "diario_30d.csv", parse_dates=["fecha"])
    ge = pd.read_csv(DATA / "audiencia_genero_edad.csv")
    pa = pd.read_csv(DATA / "audiencia_paises.csv")

    sec = []
    sec.append("# Tablas de análisis (generadas por analisis.py)\n")

    sec.append("## Por periodo\n")
    sec.append(md(resumen(p.groupby("periodo"))))

    sec.append("\n\n## Por tema\n")
    sec.append(md(resumen(p.groupby("tema")).sort_values("alcance_mediana", ascending=False)))

    sec.append("\n\n## Por tipo de CTA\n")
    sec.append(md(resumen(p.groupby("cta"))))

    sec.append("\n\n## Por formato\n")
    sec.append(md(resumen(p.groupby("tipo"))))

    sec.append("\n\n## Por día de la semana\n")
    sec.append(md(resumen(p.groupby("dia_semana")).sort_values("alcance_mediana", ascending=False)))

    reels = p[p["tipo"] == "REEL"].copy()
    reels["retencion"] = pd.cut(reels["skip_rate"], [0, 0.40, 0.45, 0.50, 1],
                                labels=["<40%", "40-45%", "45-50%", ">50%"])
    sec.append("\n\n## Reels por skip rate (abandono en los primeros 3 s)\n")
    sec.append(md(resumen(reels.groupby("retencion", observed=True))))

    cols = ["fecha", "tema", "cta", "alcance", "er_alcance", "guardados", "compartidos",
            "comentarios", "ver_medio_s", "skip_rate", "resumen"]
    sec.append("\n\n## Top 12 por alcance\n")
    sec.append(md(p.nlargest(12, "alcance")[cols].set_index("fecha").round(3)))
    sec.append("\n\n## Peores 10 por alcance\n")
    sec.append(md(p.nsmallest(10, "alcance")[cols].set_index("fecha").round(3)))

    sec.append("\n\n## Correlación con el alcance (Spearman, solo reels)\n")
    corr = reels[["alcance", "ver_medio_s", "skip_rate", "guardados_pct", "compartidos_pct",
                  "comentarios_pct"]].corr(method="spearman")["alcance"].round(2)
    sec.append(md(corr.to_frame()))

    # Últimos 30 días
    t = d.sum(numeric_only=True)
    sec.append("\n\n## Últimos 30 días (16 sep - 15 oct)\n")
    lineas = {
        "Alcance diario medio": round(d["alcance"].mean()),
        "% alcance de no seguidores": f"{t['alcance_no_seguidores'] / (t['alcance_seguidores'] + t['alcance_no_seguidores']):.1%}",
        "Alcance diario medio en seguidores": round(d["alcance_seguidores"].mean()),
        "% de seguidores alcanzados al día": f"{d['alcance_seguidores'].mean() / SEGUIDORES:.1%}",
        "Nuevos seguidores (29 días con dato)": int(d["nuevos_seguidores"].sum()),
        "Nuevos seguidores / día": round(d["nuevos_seguidores"].dropna().mean(), 1),
        "Nuevos seguidores por cada 1.000 de alcance": round(1000 * d["nuevos_seguidores"].sum() / d["alcance"][:-1].sum(), 2),
        "Interacciones totales": int(t["interacciones"]),
        "Guardados totales": int(t["guardados"]),
        "Compartidos totales": int(t["compartidos"]),
    }
    sec.append("\n".join(f"- **{k}**: {v}" for k, v in lineas.items()))
    s1 = d[d["fecha"] < "2026-10-01"]
    s2 = d[d["fecha"] >= "2026-10-01"]
    sec.append(f"\n- Nuevos seguidores/día 16-30 sep: {s1['nuevos_seguidores'].mean():.1f}  |  "
               f"1-14 oct: {s2['nuevos_seguidores'].dropna().mean():.1f}")

    # Audiencia
    sec.append("\n\n## Audiencia\n")
    total = ge["seguidores"].sum()
    gen = ge.groupby("genero")["seguidores"].sum() / total
    edad = ge.groupby("edad")["seguidores"].sum() / total
    sec.append("Género: " + ", ".join(f"{k} {v:.1%}" for k, v in gen.items()))
    sec.append("\n\nEdad: " + ", ".join(f"{k} {v:.1%}" for k, v in edad.items()))
    pa["pct"] = pa["seguidores"] / pa["seguidores"].sum()
    sec.append("\n\nTop países:\n\n" + md(pa.head(12).set_index("pais").round(3)))
    latam = pa[~pa["pais"].isin(["ES", "US", "DE", "IT", "PT", "FR", "GB", "CA", "AU", "CH", "AE",
                                 "AT", "NL", "MA", "SE", "PL", "NG", "BE", "ZA", "NO", "IE", "RO",
                                 "ID", "TR", "IN"])]["pct"].sum()
    sec.append(f"\n\nLatinoamérica (incl. PR): {latam:.1%}")

    OUT.write_text("\n".join(sec) + "\n", encoding="utf-8")
    print(f"Escrito {OUT}")


if __name__ == "__main__":
    main()
