"""Detalle a nivel de vehículo (chasis): filtra la BBDD completa (todas
sus columnas originales, no sólo las derivadas) para el "doble click"
sobre un KPI, o para el apartado de "ver todo como en el Excel"."""
import pandas as pd

from . import config

# Columnas que interesa ver primero en cualquier tabla de detalle
# (si existen en el archivo subido; si falta alguna, se ignora).
COLUMNAS_PRIORITARIAS = [
    "Chasis", "Matrícula", "concesionario", "marca", "mes",
    "Modelo", "Versión", "Motivo venta", "Origen",
    "BPS FISCALGES", "COMB", "YUC/UC",
    "Vendedor", "Km", "Días matriculado", "Días en stock",
    "Fecha venta DUC", "Fecha venta Incadea",
    "Precio venta neto", "Beneficio neto",
]


def ordenar_columnas(df: pd.DataFrame) -> list[str]:
    primero = [c for c in COLUMNAS_PRIORITARIAS if c in df.columns]
    resto = [c for c in df.columns if c not in primero]
    return primero + resto


def filtrar(
    ventas: pd.DataFrame,
    codigo_dealer: int | None = None,
    marca: str | None = None,
    meses: list[str] | None = None,
    metrica: str | None = None,
    solo_bymycar_directo: bool = False,
) -> pd.DataFrame:
    """Devuelve las filas de la BBDD (con TODAS sus columnas) que
    componen un KPI concreto -equivalente a hacer doble click sobre un
    número del dashboard.

    Las ventas de BYMYCAR "Directo" (es_bymycar_directo) quedan FUERA de
    todos los KPIs agregados (metrics.build_monthly_summary las excluye,
    se cuentan aparte) -así que, salvo que se pida explícitamente el
    detalle de "BMW DIRECTO" (`solo_bymycar_directo=True`), aquí se
    excluyen igual en cuanto se filtra por una métrica concreta,
    para que el detalle cuadre con el número de la KPI. Al navegar sin
    métrica (ver toda la BBDD) no se excluyen -ahí se quiere ver todo."""
    df = ventas
    if codigo_dealer is not None:
        df = df[df["codigo_dealer"] == codigo_dealer]
    if marca is not None:
        df = df[df["marca"] == marca]
    if meses:
        df = df[df["mes"].isin(meses)]

    if "es_bymycar_directo" in df.columns:
        if solo_bymycar_directo:
            df = df[df["es_bymycar_directo"]]
        elif metrica is not None:
            df = df[~df["es_bymycar_directo"]]

    if metrica and metrica != "ventas_totales":
        flag = config.FLAG_DE_METRICA.get(metrica)
        if flag is not None:
            df = df[df[flag]]
        elif metrica == "wholesale_uc":
            df = df[df["es_wholesale"] & (df["yuc_uc"] == "UC")]
        elif metrica == "wholesale_yuc":
            df = df[df["es_wholesale"] & (df["yuc_uc"] == "YUC")]

    return df[ordenar_columnas(df)]
