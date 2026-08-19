"""Agregación de la BBDD limpia a nivel concesionario x marca x mes.

Esta tabla es el equivalente en memoria de las pestañas "feeder" del
Excel original (UC BMW 2026 BPS, BEV BMW 2026, etc.): una fila por
concesionario, con una columna de "realizado" por mes y métrica.
"""
import pandas as pd

from . import config, storage

METRICAS_CALCULADAS = ["retail", "bps", "remarketing", "bev", "wholesale_uc", "wholesale_yuc"]


def build_monthly_summary(ventas: pd.DataFrame) -> pd.DataFrame:
    """A partir del DataFrame de clean_ventas(), devuelve una tabla con
    una fila por (codigo_dealer, marca, mes) y una columna por métrica
    realizada (conteo de vehículos)."""
    if ventas.empty:
        return pd.DataFrame(
            columns=["codigo_dealer", "marca", "mes", "retail", "bps", "remarketing", "bev", "wholesale_uc", "wholesale_yuc"]
        )

    g = ventas.groupby(["codigo_dealer", "marca", "mes"], as_index=False).agg(
        retail=("es_retail", "sum"),
        bps=("es_bps", "sum"),
        remarketing=("es_remarketing", "sum"),
        bev=("es_bev", "sum"),
        wholesale_uc=("es_wholesale", lambda s: int((s & (ventas.loc[s.index, "yuc_uc"] == "UC")).sum())),
        wholesale_yuc=("es_wholesale", lambda s: int((s & (ventas.loc[s.index, "yuc_uc"] == "YUC")).sum())),
    )
    return g


def meses_de_periodo(periodo: str, mes_referencia: str | None = None) -> list[str]:
    """Traduce un periodo del selector (mes suelto, trimestre, semestre,
    acumulado o anual) a la lista de meses que hay que sumar. Replica
    exactamente la lógica de las fórmulas CHOOSE/MATCH del Excel
    original."""
    if periodo in config.MESES:
        return [periodo]
    if periodo in config.TRIMESTRES:
        return config.TRIMESTRES[periodo]
    if periodo == "SEMESTRE 1":
        return config.MESES_S1
    if periodo == "SEMESTRE 2":
        return config.MESES_S2
    if periodo == "ANUAL":
        return config.MESES
    if periodo == "ACUMULADO MES":
        if mes_referencia is None:
            return []
        idx = config.MESES.index(mes_referencia)
        return config.MESES[: idx + 1]
    if periodo == "ACUMULADO MES 2S":
        if mes_referencia is None:
            return []
        idx = config.MESES_S2.index(mes_referencia)
        return config.MESES_S2[: idx + 1]
    raise ValueError(f"Periodo desconocido: {periodo}")


def _ajustes_de(codigo_dealer: int, marca: str) -> dict:
    """{(mes, metrica): valor} de correcciones manuales guardadas, si las hay."""
    ajustes = storage.read_table("ajustes_manuales")
    if ajustes.empty:
        return {}
    ajustes = ajustes[(ajustes["codigo_dealer"] == codigo_dealer) & (ajustes["marca"] == marca)]
    return {(row["mes"], row["metrica"]): row["valor"] for _, row in ajustes.iterrows()}


def kpis_periodo(
    resumen: pd.DataFrame,
    codigo_dealer: int,
    marca: str,
    periodo: str,
    mes_referencia: str | None = None,
) -> dict:
    """Suma las métricas realizadas de un concesionario+marca para el
    periodo pedido. Devuelve conteos, nunca None (0 si no hay ventas).

    Si hay una corrección manual guardada para algún mes/métrica (página
    "Objetivos y datos manuales" > pestaña "Ajustes manuales"), esa
    corrección sustituye al valor calculado de la BBDD para ese mes
    antes de sumar el periodo."""
    meses = meses_de_periodo(periodo, mes_referencia)
    sub = resumen[
        (resumen["codigo_dealer"] == codigo_dealer)
        & (resumen["marca"] == marca)
        & (resumen["mes"].isin(meses))
    ].set_index("mes")

    ajustes = _ajustes_de(codigo_dealer, marca)

    totales = {}
    for metrica in METRICAS_CALCULADAS:
        total = 0
        for mes in meses:
            if (mes, metrica) in ajustes:
                total += ajustes[(mes, metrica)]
            elif mes in sub.index:
                total += sub.loc[mes, metrica]
        totales[metrica] = int(total)

    totales["meses_incluidos"] = meses
    return totales


def ranking_periodo(
    resumen: pd.DataFrame,
    dealers: pd.DataFrame,
    marca: str,
    periodo: str,
    mes_referencia: str | None = None,
) -> pd.DataFrame:
    """Tabla-ranking: una fila por concesionario (de la marca dada) con
    sus KPIs realizados en el periodo, para comparar entre todos."""
    filtro_marca = dealers["vende_bmw" if marca == "BMW" else "vende_mini"] == "Si"
    filas = []
    for _, d in dealers[filtro_marca].iterrows():
        k = kpis_periodo(resumen, int(d["codigo_dealer"]), marca, periodo, mes_referencia)
        filas.append({
            "codigo_dealer": int(d["codigo_dealer"]),
            "concesionario": d["concesionario"],
            "grupo_propietario": d["grupo_propietario"],
            **{key: val for key, val in k.items() if key != "meses_incluidos"},
        })
    out = pd.DataFrame(filas)
    if not out.empty:
        retail_f = out["retail"].astype(float).replace(0, float("nan"))
        out["% bps"] = (out["bps"] / retail_f * 100).round(1)
        out["% remarketing"] = (out["remarketing"] / retail_f * 100).round(1)
        out["% bev"] = (out["bev"] / retail_f * 100).round(1)
        out = out.sort_values("retail", ascending=False).reset_index(drop=True)
    return out
