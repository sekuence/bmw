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
    para que no desaparezcan silenciosamente del dashboard.

    Dos casos que NO cuentan como "nuevo concesionario" -si no, se cuela
    un duplicado fantasma que reaparece en cada subida (p.ej. "AUTOSA"
    duplicado sin código real, visto con datos reales)-:
      a) Código 0 o negativo: eso es "sin Código INT", no un código real.
      b) El nombre (Concesión) ya existe en el maestro con OTRO código:
         es el mismo concesionario con una fila mal grabada, no uno nuevo.
    """
    conocidos = set(dealers["codigo_dealer"].dropna().astype(int))
    nombres_conocidos = set(dealers["concesionario"].str.strip().str.upper())
    nuevos = (
        ventas[["codigo_dealer", "concesionario"]]
        .dropna(subset=["codigo_dealer"])
        .drop_duplicates(subset=["codigo_dealer"])
    )
    nuevos = nuevos[nuevos["codigo_dealer"].astype(int) > 0]
    nuevos = nuevos[~nuevos["codigo_dealer"].astype(int).isin(conocidos)]
    nuevos = nuevos[~nuevos["concesionario"].str.strip().str.upper().isin(nombres_conocidos)]
    if nuevos.empty:
        return dealers
    nuevos = nuevos.assign(grupo_propietario="(nuevo, revisar)", vende_bmw="Si", vende_mini="Si")
    return pd.concat([dealers, nuevos], ignore_index=True)
