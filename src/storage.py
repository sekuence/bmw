"""Persistencia local (SQLite) para los datos que NO vienen en el
archivo de ventas: objetivos (los pone Germán a mano cada mes),
mystery shopping (llega en un Excel aparte) y tamaño de mercado
(<6 años, para el % de penetración) que llega en otro Excel aparte.

Los objetivos arrancan precargados con los que ya traía el Excel de
seguimiento original (`data/objetivos_default.csv`), así que aparecen
desde el primer momento sin tener que importar nada -en cuanto llegan
objetivos nuevos de un mes futuro, se actualizan desde la pestaña
"Importar objetivos" o a mano en "Objetivos y datos manuales".

Se guarda en un único archivo data/app.db. Si el día de mañana esto se
hostea online, este módulo es el único que habría que cambiar para
apuntar a una base de datos real (Postgres, etc.) en vez de SQLite.
"""
import sqlite3
from pathlib import Path

import pandas as pd

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "app.db"
OBJETIVOS_DEFAULT_CSV = Path(__file__).resolve().parent.parent / "data" / "objetivos_default.csv"

SCHEMA = """
CREATE TABLE IF NOT EXISTS objetivos (
    codigo_dealer INTEGER NOT NULL,
    marca TEXT NOT NULL,
    metrica TEXT NOT NULL,
    mes TEXT NOT NULL,
    valor REAL NOT NULL,
    PRIMARY KEY (codigo_dealer, marca, metrica, mes)
);

CREATE TABLE IF NOT EXISTS mercado_menos_6_anos (
    codigo_dealer INTEGER NOT NULL,
    marca TEXT NOT NULL,
    mes TEXT NOT NULL,
    valor REAL NOT NULL,
    PRIMARY KEY (codigo_dealer, marca, mes)
);

CREATE TABLE IF NOT EXISTS mystery_shopping (
    codigo_dealer INTEGER NOT NULL,
    marca TEXT NOT NULL,
    semestre TEXT NOT NULL,
    valor REAL NOT NULL,
    PRIMARY KEY (codigo_dealer, marca, semestre)
);

-- Correcciones manuales sobre un valor CALCULADO desde la BBDD (retail,
-- bps, remarketing, bev, wholesale_uc, wholesale_yuc), por si algún mes
-- hay que arreglar algo a mano. Si existe una fila aquí, sustituye al
-- valor calculado para ese concesionario/marca/mes/métrica.
CREATE TABLE IF NOT EXISTS ajustes_manuales (
    codigo_dealer INTEGER NOT NULL,
    marca TEXT NOT NULL,
    metrica TEXT NOT NULL,
    mes TEXT NOT NULL,
    valor REAL NOT NULL,
    PRIMARY KEY (codigo_dealer, marca, metrica, mes)
);
"""


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA)
    _sembrar_objetivos_por_defecto(conn)
    return conn


def _sembrar_objetivos_por_defecto(conn: sqlite3.Connection) -> None:
    """La primera vez que se usa la app (tabla objetivos vacía), precarga
    los objetivos que ya venían en el Excel de seguimiento original -así
    aparecen en el Dashboard sin tener que pasar antes por "Importar
    objetivos". Sólo se ejecuta si la tabla está vacía: en cuanto el
    usuario guarde o importe algo, deja de tocarse."""
    if not OBJETIVOS_DEFAULT_CSV.exists():
        return
    (count,) = conn.execute("SELECT COUNT(*) FROM objetivos").fetchone()
    if count > 0:
        return
    datos = pd.read_csv(OBJETIVOS_DEFAULT_CSV)
    conn.executemany(
        "INSERT OR IGNORE INTO objetivos (codigo_dealer, marca, metrica, mes, valor) VALUES (?, ?, ?, ?, ?)",
        datos[["codigo_dealer", "marca", "metrica", "mes", "valor"]].itertuples(index=False, name=None),
    )
    conn.commit()


def upsert(table: str, keys: dict, valor: float) -> None:
    cols = list(keys.keys()) + ["valor"]
    placeholders = ", ".join("?" for _ in cols)
    col_names = ", ".join(cols)
    conflict_cols = ", ".join(keys.keys())
    sql = (
        f"INSERT INTO {table} ({col_names}) VALUES ({placeholders}) "
        f"ON CONFLICT({conflict_cols}) DO UPDATE SET valor=excluded.valor"
    )
    with get_connection() as conn:
        conn.execute(sql, list(keys.values()) + [valor])


def read_table(table: str) -> pd.DataFrame:
    with get_connection() as conn:
        return pd.read_sql_query(f"SELECT * FROM {table}", conn)


def get_valor(table: str, keys: dict) -> float | None:
    where = " AND ".join(f"{k}=?" for k in keys)
    with get_connection() as conn:
        row = conn.execute(f"SELECT valor FROM {table} WHERE {where}", list(keys.values())).fetchone()
    return row[0] if row else None


def save_dataframe(table: str, df: pd.DataFrame, key_cols: list[str]) -> None:
    """Guarda en bloque un data_editor de Streamlit (una fila = un registro)."""
    for _, row in df.iterrows():
        valor = row.get("valor")
        if pd.isna(valor):
            continue
        keys = {k: row[k] for k in key_cols}
        upsert(table, keys, float(valor))
