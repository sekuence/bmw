"""KPIs completos de un concesionario+marca+periodo: junta lo calculado
desde la BBDD (metrics.py) con lo introducido a mano (storage.py:
objetivos, mercado <6 años, mystery shopping).

Replica el bloque principal de la pestaña "Dealer Dashboard" del Excel
original, incluidas las bandas de "ventas necesarias para alcanzar tal
% de penetración" (con las mismas fórmulas -y las mismas
inconsistencias numéricas que ya traía el Excel original-, para que
los resultados cuadren con lo que la empresa ya conoce).
"""
import math

import pandas as pd

from . import bonus, config, metrics, storage

BANDAS_REMARKETING = {
    "BMW": [0.18, 0.22, 0.27, 0.32],
    "MINI": [0.15, 0.20, 0.25, 0.30],
}

# (umbral, numerador_para_llegar) -- tal cual estaban en el Excel original.
BANDAS_BEV = {
    "BMW": [(0.06, 0.05), (0.11, 0.10)],
    "MINI": [(0.10, 0.05), (0.15, 0.10)],
}


def _roundup(x: float) -> int:
    return int(math.ceil(round(x, 6)))


def _objetivo_de(codigo_dealer: int, marca: str, metrica: str, meses: list[str]) -> float:
    total = 0.0
    for m in meses:
        v = storage.get_valor("objetivos", {"codigo_dealer": codigo_dealer, "marca": marca, "metrica": metrica, "mes": m})
        total += v or 0
    return total


def _mercado_de(codigo_dealer: int, marca: str, meses: list[str]) -> float | None:
    total, encontrado = 0.0, False
    for m in meses:
        v = storage.get_valor("mercado_menos_6_anos", {"codigo_dealer": codigo_dealer, "marca": marca, "mes": m})
        if v is not None:
            total += v
            encontrado = True
    return total if encontrado else None


def _mystery_shopping_de(codigo_dealer: int, marca: str, meses: list[str]) -> float | None:
    from .config import MESES_S1

    semestres = {"S1" if m in MESES_S1 else "S2" for m in meses}
    if len(semestres) != 1:
        return None  # el mystery shopping es semestral: sólo tiene sentido si el periodo cae en un único semestre
    semestre = semestres.pop()
    return storage.get_valor("mystery_shopping", {"codigo_dealer": codigo_dealer, "marca": marca, "semestre": semestre})


def _bandas_remarketing_necesarias(marca: str, objetivo_retail: float, remarketing: float) -> list[dict]:
    out = []
    ratio = (remarketing / objetivo_retail) if objetivo_retail else None
    for i, t in enumerate(BANDAS_REMARKETING[marca]):
        if not objetivo_retail or (ratio is not None and ratio >= t):
            necesarias = 0
        elif i == 0:
            necesarias = max(0, _roundup((t * objetivo_retail - remarketing) / (1 - t)))
        else:
            necesarias = max(0, _roundup(t * objetivo_retail - remarketing))
        out.append({"umbral": t, "necesarias": necesarias})
    return out


def _bandas_bev_necesarias(marca: str, objetivo_retail: float, bev: float) -> list[dict]:
    out = []
    ratio = (bev / objetivo_retail) if objetivo_retail else None
    for umbral, numerador in BANDAS_BEV[marca]:
        if ratio is not None and ratio >= umbral:
            necesarias = 0
        elif not objetivo_retail:
            necesarias = 0
        else:
            necesarias = max(0, _roundup((numerador * objetivo_retail - bev) / (1 - umbral)))
        out.append({"umbral": umbral, "necesarias": necesarias})
    return out


def kpi_bloque(
    resumen,
    codigo_dealer: int,
    marca: str,
    periodo: str,
    mes_referencia: str | None = None,
    remarketing_disponible: bool = True,
) -> dict:
    meses = metrics.meses_de_periodo(periodo, mes_referencia)
    realizado = metrics.kpis_periodo(resumen, codigo_dealer, marca, periodo, mes_referencia)

    objetivo_retail = _objetivo_de(codigo_dealer, marca, "Retail", meses)
    objetivo_bev = _objetivo_de(codigo_dealer, marca, "BEV", meses)
    mercado = _mercado_de(codigo_dealer, marca, meses)
    mystery = _mystery_shopping_de(codigo_dealer, marca, meses)

    retail = realizado["retail"]
    bps = realizado["bps"]
    bev = realizado["bev"]

    ventas_bps_necesarias = (4 * retail) if bps == 0 else max(0, _roundup(4 * (retail - 1.25 * bps)))

    # %BPS se calcula sobre el Realizado, pero %BEV y %Remarketing se
    # calculan sobre el Objetivo -así están las fórmulas en el Excel
    # original (columna G12), no sobre el Realizado (G13)-.
    pct_cumplimiento_retail = (retail / objetivo_retail) if objetivo_retail else None
    pct_bps = (bps / retail) if retail else None
    pct_bev = (bev / objetivo_retail) if objetivo_retail else None

    # "Retail origen Remarketing" sólo se puede calcular con la columna
    # "Canal Actual" -si no está disponible en el archivo cargado, se
    # deja en None (no se inventa un 0 ni una alternativa).
    if remarketing_disponible:
        remarketing = realizado["remarketing"]
        pct_remarketing = (remarketing / objetivo_retail) if objetivo_retail else None
        bandas_remarketing = _bandas_remarketing_necesarias(marca, objetivo_retail, remarketing)
    else:
        remarketing = None
        pct_remarketing = None
        bandas_remarketing = []

    bono = bonus.calcular(marca, pct_cumplimiento_retail, pct_remarketing, pct_bev)
    if bono["total"] is not None:
        bono["total_a_cobrar"] = round(bono["total"] * retail, 2)
    else:
        bono["total_a_cobrar"] = None

    return {
        "meses_incluidos": meses,
        "objetivo_retail": objetivo_retail,
        "realizado_retail": retail,
        "pct_cumplimiento_retail": pct_cumplimiento_retail,
        "bps": bps,
        "pct_bps": pct_bps,
        "ventas_bps_necesarias_para_25pct": ventas_bps_necesarias,
        "remarketing": remarketing,
        "pct_remarketing": pct_remarketing,
        "bandas_remarketing_necesarias": bandas_remarketing,
        "objetivo_bev": objetivo_bev,
        "bev": bev,
        "pct_bev": pct_bev,
        "bandas_bev_necesarias": _bandas_bev_necesarias(marca, objetivo_retail, bev),
        "wholesale_uc": realizado["wholesale_uc"],
        "wholesale_yuc": realizado["wholesale_yuc"],
        "ventas_totales": realizado["ventas_totales"],
        "mercado_menos_6_anos": mercado,
        "pct_penetracion_mercado": (retail / mercado) if mercado else None,
        "mystery_shopping": mystery,
        "cumple_penetracion_bps": bonus.cumple_penetracion_bps(pct_bps),
        "cumple_mystery_shopping": bonus.cumple_mystery_shopping(mystery),
        "bonificacion": bono,
    }


def evolucion_mensual(resumen: pd.DataFrame, codigo_dealer: int, marca: str, remarketing_disponible: bool = True) -> pd.DataFrame:
    """Serie mes a mes (Objetivo vs Realizado, BPS/MN, Remarketing, BEV)
    para el gráfico del Dashboard. Sólo incluye los meses que ya tienen
    ventas cargadas para ese concesionario+marca."""
    sub = resumen[(resumen["codigo_dealer"] == codigo_dealer) & (resumen["marca"] == marca)]
    meses_con_datos = sorted(sub["mes"].unique(), key=config.MESES.index)

    columnas = ["mes", "Objetivo Retail", "Realizado Retail", "BPS/MN", "BEV"]
    if remarketing_disponible:
        columnas.append("Remarketing")
    if not meses_con_datos:
        return pd.DataFrame(columns=columnas).set_index("mes")

    filas = []
    for mes in meses_con_datos:
        k = metrics.kpis_periodo(resumen, codigo_dealer, marca, mes)
        fila = {
            "mes": mes,
            "Objetivo Retail": _objetivo_de(codigo_dealer, marca, "Retail", [mes]),
            "Realizado Retail": k["retail"],
            "BPS/MN": k["bps"],
            "BEV": k["bev"],
        }
        if remarketing_disponible:
            fila["Remarketing"] = k["remarketing"]
        filas.append(fila)
    out = pd.DataFrame(filas, columns=columnas).set_index("mes")
    # Índice categórico ordenado cronológicamente: st.line_chart no admite
    # sort=False (a diferencia de st.bar_chart), así que sin esto el eje X
    # se reordena alfabéticamente.
    out.index = pd.CategoricalIndex(out.index, categories=meses_con_datos, ordered=True)
    return out
