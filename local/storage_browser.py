"""Persistencia en el navegador (localStorage) para los datos que NO
vienen en el archivo de ventas: objetivos, mystery shopping y tamaño
de mercado <6 años -equivalente browser-only de storage.py (SQLite),
misma API pública (get_valor, upsert, read_table, save_dataframe)
para que dashboard.py, pages, etc. no necesiten saber la diferencia.

Los objetivos arrancan precargados con los que ya traía el Excel de
seguimiento original (data/objetivos_default.csv, escrito en el
sistema de archivos virtual de Pyodide al arrancar), igual que en la
versión SQLite.

Todo se guarda en una única clave de localStorage como JSON -los
datos nunca salen del navegador del usuario."""
import json
from pathlib import Path

import pandas as pd
from js import localStorage

LOCALSTORAGE_KEY = "bmw_seguimiento_datos_v1"
OBJETIVOS_DEFAULT_CSV = Path(__file__).resolve().parent.parent / "data" / "objetivos_default.csv"

_TABLAS = ["objetivos", "mercado_menos_6_anos", "mystery_shopping", "ajustes_manuales"]
_CLAVES = {
    "objetivos": ["codigo_dealer", "marca", "metrica", "mes"],
    "mercado_menos_6_anos": ["codigo_dealer", "marca", "mes"],
    "mystery_shopping": ["codigo_dealer", "marca", "semestre"],
    "ajustes_manuales": ["codigo_dealer", "marca", "metrica", "mes"],
}

_cache: dict | None = None


def _sembrar_objetivos_por_defecto() -> list[dict]:
    if not OBJETIVOS_DEFAULT_CSV.exists():
        return []
    datos = pd.read_csv(OBJETIVOS_DEFAULT_CSV)
    return datos[["codigo_dealer", "marca", "metrica", "mes", "valor"]].to_dict("records")


def _cargar() -> dict:
    global _cache
    if _cache is not None:
        return _cache
    raw = localStorage.getItem(LOCALSTORAGE_KEY)
    if raw:
        _cache = json.loads(raw)
    else:
        _cache = {t: [] for t in _TABLAS}
        _cache["objetivos"] = _sembrar_objetivos_por_defecto()
    for t in _TABLAS:
        _cache.setdefault(t, [])
    return _cache


def _guardar() -> None:
    localStorage.setItem(LOCALSTORAGE_KEY, json.dumps(_cache))


def _coincide(fila: dict, keys: dict, cols_clave: list[str]) -> bool:
    return all(fila.get(c) == keys[c] for c in cols_clave)


def upsert(table: str, keys: dict, valor: float) -> None:
    datos = _cargar()
    filas = datos[table]
    cols_clave = _CLAVES[table]
    for fila in filas:
        if _coincide(fila, keys, cols_clave):
            fila["valor"] = valor
            _guardar()
            return
    nueva = dict(keys)
    nueva["valor"] = valor
    filas.append(nueva)
    _guardar()


def read_table(table: str) -> pd.DataFrame:
    datos = _cargar()
    filas = datos[table]
    cols = _CLAVES[table] + ["valor"]
    if not filas:
        return pd.DataFrame(columns=cols)
    return pd.DataFrame(filas, columns=cols)


def get_valor(table: str, keys: dict) -> float | None:
    datos = _cargar()
    cols_clave = _CLAVES[table]
    for fila in datos[table]:
        if _coincide(fila, keys, cols_clave):
            return fila["valor"]
    return None


def save_dataframe(table: str, df: pd.DataFrame, key_cols: list[str]) -> None:
    """Guarda en bloque una tabla editable (una fila = un registro)."""
    for _, row in df.iterrows():
        valor = row.get("valor")
        if pd.isna(valor):
            continue
        keys = {k: row[k] for k in key_cols}
        upsert(table, keys, float(valor))


def borrar_todo() -> None:
    """Vacía todos los datos manuales guardados en este navegador."""
    global _cache
    _cache = {t: [] for t in _TABLAS}
    _guardar()
