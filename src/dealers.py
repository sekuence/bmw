"""Maestro de concesionarios (extraído del Excel original, pestañas
'UC BMW 2026' y 'UC MINI 2026'). Sirve para que el dashboard muestre
todos los concesionarios -incluso los que no tienen ventas ese
periodo- y para mostrar Grupo Propietario.
"""
from pathlib import Path

import pandas as pd

DEALERS_CSV = Path(__file__).resolve().parent.parent / "data" / "dealers.csv"


def load_dealers() -> pd.DataFrame:
    df = pd.read_csv(DEALERS_CSV, dtype={"codigo_dealer": "Int64", "distrito": "Int64"})
    df["concesionario"] = df["concesionario"].str.strip()
    return df


def merge_new_dealers(dealers: pd.DataFrame, ventas: pd.DataFrame) -> pd.DataFrame:
    """Si el archivo de ventas trae concesionarios (código) que no están en el
    maestro local, los añade automáticamente (con grupo propietario en blanco)
    para que no desaparezcan silenciosamente del dashboard."""
    conocidos = set(dealers["codigo_dealer"].dropna().astype(int))
    nuevos = (
        ventas[["codigo_dealer", "concesionario"]]
        .dropna(subset=["codigo_dealer"])
        .drop_duplicates(subset=["codigo_dealer"])
    )
    nuevos = nuevos[~nuevos["codigo_dealer"].astype(int).isin(conocidos)]
    if nuevos.empty:
        return dealers
    nuevos = nuevos.assign(grupo_propietario="(nuevo, revisar)", vende_bmw="Si", vende_mini="Si")
    return pd.concat([dealers, nuevos], ignore_index=True)
