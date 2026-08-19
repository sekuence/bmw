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
    raw = raw.rename(columns=rename_map)
    return raw


def clean_ventas(raw: pd.DataFrame) -> pd.DataFrame:
    """Limpia la BBDD y añade columnas derivadas de negocio.

    Devuelve una fila por vehículo con:
      codigo_dealer, concesionario, marca, mes, es_retail, es_bps,
      es_remarketing, es_bev, es_wholesale, yuc_uc
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

    motivo = df["Motivo venta"].astype(str).str.strip().str.upper()
    df["es_retail"] = motivo.eq("RETAIL")
    df["es_wholesale"] = ~df["es_retail"]

    # BPS/MN se determina exclusivamente con la columna BPS FISCALGES.
    bps_flag = df["BPS FISCALGES"].astype(str).str.strip().str.upper().isin(["SI", "SÍ", "YES", "TRUE"])
    df["es_bps"] = bps_flag & df["es_retail"]

    origen = df["Origen"].astype(str).str.strip().str.upper()
    df["es_remarketing"] = origen.str.contains("REMARKETING") & df["es_retail"]

    comb = df["COMB"].astype(str).str.strip().str.upper()
    df["es_bev"] = comb.eq("BEV") & df["es_retail"]

    df["yuc_uc"] = df["YUC/UC"].astype(str).str.strip().str.upper()

    cols = [
        "codigo_dealer", "concesionario", "marca", "mes",
        "es_retail", "es_wholesale", "es_bps", "es_remarketing", "es_bev", "yuc_uc",
    ]
    return df[cols].reset_index(drop=True)
