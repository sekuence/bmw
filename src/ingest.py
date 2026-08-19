"""Lectura y limpieza del archivo de ventas (la BBDD de vehículos).

La hoja de origen ("BBDD") es la fuente de la verdad: cada fila es un
vehículo de ocasión vendido. A partir de esas columnas derivamos los
flags de negocio (retail, BPS/MN, remarketing, BEV) que después se
agregan por concesionario/mes/marca en metrics.py.
"""
import unicodedata

import pandas as pd

from . import config

# Nombre normalizado -> nombre real esperado en el Excel. La normalización
# (mayúsculas, sin acentos, sin espacios sobrantes) hace que la lectura
# tolere pequeñas variaciones de un mes a otro (p.ej. "Días matriculado "
# con espacio final, o "BPS/NEXT" sin espacios).
REQUIRED_COLUMNS = {
    "codigo int": "Código INT",
    "concesion": "Concesión",
    "marca": "Marca",
    "fecha venta mes": "Fecha venta mes",
    "motivo venta": "Motivo venta",
    "bps fiscalges": "BPS FISCALGES",
    "origen": "Origen",
    "comb": "COMB",
    "yuc/uc": "YUC/UC",
    "chasis": "Chasis",
}


def _normalize(name: str) -> str:
    name = str(name).strip().lower()
    name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    return " ".join(name.split())


def _resolve_columns(columns) -> dict:
    """Devuelve {nombre_normalizado: nombre_real_en_el_excel}."""
    return {_normalize(c): c for c in columns}


class VentasFileError(ValueError):
    pass


def read_bbdd(file_obj) -> pd.DataFrame:
    """Lee la hoja BBDD del archivo de ventas subido y devuelve el
    DataFrame crudo (sin limpiar), o lanza VentasFileError si falta la
    hoja o columnas clave."""
    try:
        xls = pd.ExcelFile(file_obj, engine="openpyxl")
    except Exception as exc:  # noqa: BLE001
        raise VentasFileError(f"No se pudo abrir el archivo: {exc}") from exc

    sheet = next((s for s in xls.sheet_names if _normalize(s) == _normalize(config.HOJA_VENTAS)), None)
    if sheet is None:
        raise VentasFileError(
            f"El archivo no tiene una hoja llamada '{config.HOJA_VENTAS}'. "
            f"Hojas encontradas: {', '.join(xls.sheet_names)}"
        )

    raw = xls.parse(sheet)
    resolved = _resolve_columns(raw.columns)

    faltantes = [real for norm, real in REQUIRED_COLUMNS.items() if norm not in resolved]
    if faltantes:
        raise VentasFileError(
            "Faltan columnas obligatorias en la hoja BBDD: " + ", ".join(faltantes)
        )

    rename_map = {resolved[norm]: real for norm, real in REQUIRED_COLUMNS.items()}
    # "Canal Actual" es opcional -todavía no existe en los archivos de ventas
    # reales, pero en cuanto aparezca la app la detecta y la usa sola.
    canal_actual_norm = _normalize(config.COLUMNA_CANAL_ACTUAL)
    if canal_actual_norm in resolved:
        rename_map[resolved[canal_actual_norm]] = config.COLUMNA_CANAL_ACTUAL
    raw = raw.rename(columns=rename_map)
    return raw


# Columnas de negocio derivadas (se anteponen a todas las de la BBDD).
COLUMNAS_DERIVADAS = [
    "codigo_dealer", "concesionario", "marca", "mes",
    "es_retail", "es_wholesale", "es_bps", "es_remarketing", "es_bev", "yuc_uc",
]


def _reasignar_bymycar_directo(df: pd.DataFrame, canal_actual: pd.Series) -> None:
    """Las ventas de BYMYCAR cuyo Canal Actual sea de tipo "_DIRECTO" se
    reasignan al concesionario ficticio BMW DIRECTO (código 12345); el
    resto se queda en BYMYCAR tal cual. Modifica `df` in place."""
    es_bymycar = df["concesionario"].str.upper().str.contains(config.CONCESIONARIO_BYMYCAR, na=False)
    es_directo = canal_actual.str.contains(config.PATRON_CANAL_DIRECTO, na=False)
    mask = es_bymycar & es_directo
    df.loc[mask, "codigo_dealer"] = config.CODIGO_BMW_DIRECTO
    df.loc[mask, "concesionario"] = config.NOMBRE_BMW_DIRECTO


def clean_ventas(raw: pd.DataFrame) -> pd.DataFrame:
    """Limpia la BBDD y añade columnas derivadas de negocio, pero
    **conserva todas las columnas originales** (Chasis, Matrícula,
    Modelo, Vendedor, precios, fechas...) para poder consultar el
    detalle vehículo a vehículo en la app, tal cual como en el Excel.

    Todas las métricas de negocio (retail, BPS/MN, remarketing, BEV) se
    calculan siempre dentro de `Motivo venta` = "Retail" -salvo
    "ventas totales", que cuenta todo el inventario vendido
    independientemente del motivo-.
    """
    df = raw.dropna(subset=["Chasis"]).copy()

    df["codigo_dealer"] = pd.to_numeric(df["Código INT"], errors="coerce").astype("Int64")
    df = df.dropna(subset=["codigo_dealer"])
    df["codigo_dealer"] = df["codigo_dealer"].astype(int)

    df["concesionario"] = df["Concesión"].astype(str).str.strip()
    df["marca"] = df["Marca"].astype(str).str.strip().str.upper()
    df.loc[df["marca"].isin(["BMWI", "BMW I"]), "marca"] = "BMW"

    df["mes"] = df["Fecha venta mes"].astype(str).str.strip().str.upper()
    df = df[df["mes"].isin(config.MESES)]

    canal_actual = None
    if config.COLUMNA_CANAL_ACTUAL in df.columns:
        canal_actual = df[config.COLUMNA_CANAL_ACTUAL].astype(str).str.strip().str.upper()
        _reasignar_bymycar_directo(df, canal_actual)

    motivo = df["Motivo venta"].astype(str).str.strip().str.upper()
    df["es_retail"] = motivo.eq("RETAIL")
    df["es_wholesale"] = ~df["es_retail"]

    # BPS/MN se determina exclusivamente con la columna BPS FISCALGES,
    # dentro de las ventas Retail.
    bps_flag = df["BPS FISCALGES"].astype(str).str.strip().str.upper().isin(["SI", "SÍ", "YES", "TRUE"])
    df["es_bps"] = bps_flag & df["es_retail"]

    if canal_actual is not None:
        # Retail origen Remarketing = todo Retail salvo los canales
        # "_MOBILITY" / "_LANDING" (ver config.py).
        excluidos = canal_actual.str.contains("|".join(config.PATRONES_CANAL_EXCLUIDOS_REMARKETING), na=False)
        df["es_remarketing"] = df["es_retail"] & ~excluidos
    else:
        # Alternativa mientras no exista la columna "Canal Actual" en la BBDD.
        origen = df["Origen"].astype(str).str.strip().str.upper()
        df["es_remarketing"] = origen.str.contains("REMARKETING") & df["es_retail"]

    # BEV se determina con la columna COMB, dentro de las ventas Retail.
    comb = df["COMB"].astype(str).str.strip().str.upper()
    df["es_bev"] = comb.eq("BEV") & df["es_retail"]

    df["yuc_uc"] = df["YUC/UC"].astype(str).str.strip().str.upper()

    otras_cols = [c for c in raw.columns if c not in COLUMNAS_DERIVADAS]
    out = df[COLUMNAS_DERIVADAS + otras_cols].reset_index(drop=True)
    return _sanear_para_mostrar(out)


def _sanear_para_mostrar(df: pd.DataFrame) -> pd.DataFrame:
    """Deja el DataFrame a prueba de errores al mostrarlo en tablas o
    guardarlo (Streamlit/pyarrow no toleran columnas con tipos
    mezclados, algo habitual en Excels reales: celdas con errores de
    fórmula como #N/A o #NUM! mezcladas con números, fechas como texto
    en unas filas y como número de serie en otras, nombres de columna
    duplicados que pandas convierte en número, etc.)."""
    df = df.copy()
    df.columns = [str(c) for c in df.columns]  # nombres de columna siempre como texto

    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].map(lambda v: v if pd.isna(v) else str(v))

    return df
