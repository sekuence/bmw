"""Lógica de las tablas de 'Seguimiento UC Retail & Wholesale' -un
apartado por cada pestaña del Excel original (UC, UC+BPS/M-NEXT, BEV,
Wholesale, Grupo Propietario, Penetración de mercado)-, separada de
cómo se pinta (pages/6_Seguimiento_UC_Retail_Wholesale.py en la app de
Streamlit, browser_views.py en la versión HTML local): es pandas puro,
reutilizable en las dos.
"""
import pandas as pd

from . import config, metrics

MESES_CORTOS = {m: m[:3].capitalize() for m in config.MESES}

FILA_BYMYCAR_DIRECTO = pd.DataFrame([{
    "codigo_dealer": metrics.CODIGO_BYMYCAR_DIRECTO,
    "distrito": pd.NA,
    "concesionario": "BMW DIRECTO",
    "grupo_propietario": "",
}])


def resumen_con_directo(resumen: pd.DataFrame, ventas: pd.DataFrame) -> pd.DataFrame:
    """resumen con los ajustes manuales ya aplicados + la fila "BMW
    DIRECTO" (codigo_dealer=CODIGO_BYMYCAR_DIRECTO) mezclada como si
    fuera un concesionario más, para que salga como fila extra en las
    tablas de abajo en vez de en una pestaña aparte."""
    ajustado = metrics.aplicar_ajustes(resumen)
    return pd.concat([ajustado, metrics.build_bymycar_directo_summary(ventas)], ignore_index=True)


def bloques_periodo(mes_acumulado: str) -> list[tuple[str, list[str]]]:
    idx = config.MESES.index(mes_acumulado)
    bloques = [(MESES_CORTOS[m], [m]) for m in config.MESES]
    bloques.append(("Acum. Mes", config.MESES[: idx + 1]))
    bloques.append(("Anual", config.MESES))
    bloques.append(("Sem. 1", config.MESES_S1))
    bloques.append(("Sem. 2", config.MESES_S2))
    return bloques


def objetivo_pivot(objetivos: pd.DataFrame, marca: str, metrica: str) -> dict:
    if objetivos.empty:
        return {}
    sub = objetivos[(objetivos["marca"] == marca) & (objetivos["metrica"] == metrica)]
    return {(int(r["codigo_dealer"]), r["mes"]): r["valor"] for _, r in sub.iterrows()}


def mercado_pivot(mercado: pd.DataFrame, marca: str) -> dict:
    if mercado.empty:
        return {}
    sub = mercado[mercado["marca"] == marca]
    return {(int(r["codigo_dealer"]), r["mes"]): r["valor"] for _, r in sub.iterrows()}


def dealers_de(dealers: pd.DataFrame, marca: str, agrupar: bool) -> pd.DataFrame:
    """Devuelve los concesionarios de la marca **en el mismo orden en que
    aparecen en el Excel original** (agrupados por distrito, sin
    reordenar alfabéticamente), más la fila "BMW DIRECTO" al final -las
    ventas de BYMYCAR con Canal Actual "…DIRECTO"- cuando se ve por
    concesionario (no tiene sentido en la vista agrupada por Grupo
    Propietario, porque no pertenece a ningún grupo)."""
    col = "vende_bmw" if marca == "BMW" else "vende_mini"
    d = dealers[dealers[col] == "Si"]
    if agrupar:
        return d[["grupo_propietario"]].drop_duplicates()
    return pd.concat([d, FILA_BYMYCAR_DIRECTO], ignore_index=True)


def _resumen_grupo(sub_marca: pd.DataFrame, clave, agrupar: bool, dealers_completo: pd.DataFrame) -> pd.DataFrame:
    if not agrupar:
        return sub_marca[sub_marca["codigo_dealer"] == clave]
    codigos = dealers_completo.loc[dealers_completo["grupo_propietario"] == clave, "codigo_dealer"].astype(int)
    return sub_marca[sub_marca["codigo_dealer"].isin(codigos)]


def _valor_grupo(pivot: dict, clave, mes: str, agrupar: bool, dealers_completo: pd.DataFrame) -> float:
    if not agrupar:
        return pivot.get((clave, mes), 0) or 0
    codigos = dealers_completo.loc[dealers_completo["grupo_propietario"] == clave, "codigo_dealer"].astype(int)
    return sum(pivot.get((c, mes), 0) or 0 for c in codigos)


def _distrito_de(d, agrupar: bool, dealers_completo: pd.DataFrame) -> str:
    if not agrupar:
        return "" if pd.isna(d["distrito"]) else str(int(d["distrito"]))
    distritos = dealers_completo.loc[dealers_completo["grupo_propietario"] == d["grupo_propietario"], "distrito"].dropna().unique()
    if len(distritos) == 1:
        return str(int(distritos[0]))
    return "Varios" if len(distritos) > 1 else ""


def construir(
    dealers: pd.DataFrame, resumen_ajustado: pd.DataFrame, marca: str, agrupar: bool,
    sub_metricas: list[str], calculo, bloques: list[tuple[str, list[str]]], pivots: dict[str, dict] | None = None,
) -> pd.DataFrame:
    """sub_metricas: nombres de las columnas dentro de cada bloque de
    periodo. calculo(g_bloque, **extras) -> lista de valores en el mismo
    orden que sub_metricas, donde `extras` trae un valor (sumado en ese
    bloque) por cada entrada de `pivots` -p.ej. {'obj': ..., 'obj_bev': ...}-.
    Incluye los meses sueltos + Acum. Mes / Anual / Sem. 1 / Sem. 2, y
    mantiene el orden de concesionarios (por distrito) del Excel original."""
    dealers_completo = dealers[dealers["vende_bmw" if marca == "BMW" else "vende_mini"] == "Si"]
    filas_maestro = dealers_de(dealers, marca, agrupar)
    sub_marca = resumen_ajustado[resumen_ajustado["marca"] == marca]
    pivots = pivots or {}

    etiqueta_id = "Grupo propietario" if agrupar else "Concesionario"
    columnas = pd.MultiIndex.from_tuples(
        [("", "Distrito"), ("", etiqueta_id)] + [(etq, sm) for etq, _ in bloques for sm in sub_metricas]
    )

    filas = []
    for _, d in filas_maestro.iterrows():
        clave = d["grupo_propietario"] if agrupar else int(d["codigo_dealer"])
        fila = [_distrito_de(d, agrupar, dealers_completo), d["grupo_propietario"] if agrupar else d["concesionario"]]
        g = _resumen_grupo(sub_marca, clave, agrupar, dealers_completo)
        for _, meses_bloque in bloques:
            g_bloque = g[g["mes"].isin(meses_bloque)]
            extras = {
                nombre: sum(_valor_grupo(pivot, clave, m, agrupar, dealers_completo) for m in meses_bloque)
                for nombre, pivot in pivots.items()
            }
            fila.extend(calculo(g_bloque, **extras))
        filas.append(fila)

    return pd.DataFrame(filas, columns=columnas)


def tabla_retail_simple(dealers, resumen_ajustado, objetivos, mercado, marca, agrupar, bloques, remarketing_disponible) -> pd.DataFrame:
    """Equivalente a la pestaña 'UC BMW/MINI 2026' original: sólo
    Objetivo y Realizado de ventas Retail."""
    def calculo(g_bloque, obj):
        return [obj, int(g_bloque["retail"].sum())]
    return construir(dealers, resumen_ajustado, marca, agrupar, ["OBJ", "RE"], calculo, bloques, {"obj": objetivo_pivot(objetivos, marca, "Retail")})


def tabla_retail_bps(dealers, resumen_ajustado, objetivos, mercado, marca, agrupar, bloques, remarketing_disponible) -> pd.DataFrame:
    def calculo(g_bloque, obj):
        re = int(g_bloque["retail"].sum())
        bps = int(g_bloque["bps"].sum())
        if remarketing_disponible:
            rmk = int(g_bloque["remarketing"].sum())
            rmk_pct = round(rmk / obj * 100, 1) if obj else None
        else:
            rmk, rmk_pct = None, None
        return [
            obj, re,
            bps, round(bps / re * 100, 1) if re else None,
            rmk, rmk_pct,
        ]
    return construir(dealers, resumen_ajustado, marca, agrupar, ["OBJ", "RE", "BPS", "%BPS", "RMK", "%RMK"], calculo, bloques, {"obj": objetivo_pivot(objetivos, marca, "Retail")})


def tabla_bev(dealers, resumen_ajustado, objetivos, mercado, marca, agrupar, bloques, remarketing_disponible) -> pd.DataFrame:
    # %BEV se calcula sobre el Objetivo Retail (igual que en el Excel
    # original), no sobre el Realizado ni sobre un "objetivo BEV"
    # -no existe, es el mismo objetivo de Retail-.
    def calculo(g_bloque, obj_retail):
        bev = int(g_bloque["bev"].sum())
        return [obj_retail, bev, round(bev / obj_retail * 100, 1) if obj_retail else None]
    return construir(
        dealers, resumen_ajustado, marca, agrupar, ["Objetivo", "BEV", "%BEV"], calculo, bloques,
        {"obj_retail": objetivo_pivot(objetivos, marca, "Retail")},
    )


def tabla_wholesale(dealers, resumen_ajustado, objetivos, mercado, marca, agrupar, bloques, remarketing_disponible) -> pd.DataFrame:
    def calculo(g_bloque):
        return [int(g_bloque["wholesale_uc"].sum()), int(g_bloque["wholesale_yuc"].sum())]
    return construir(dealers, resumen_ajustado, marca, agrupar, ["UC", "YUC"], calculo, bloques)


def tabla_penetracion(dealers, resumen_ajustado, objetivos, mercado, marca, agrupar, bloques, remarketing_disponible) -> pd.DataFrame:
    """Equivalente a 'PENETRACIÓN MERCADO VO BMW/MINI': tamaño de mercado
    <6 años (dato manual) vs ventas Retail realizadas."""
    def calculo(g_bloque, mdo):
        re = int(g_bloque["retail"].sum())
        return [mdo or None, re, round(re / mdo * 100, 1) if mdo else None]
    return construir(dealers, resumen_ajustado, marca, agrupar, ["Mdo <6 años", "Vta Retail", "%Penetración"], calculo, bloques, {"mdo": mercado_pivot(mercado, marca)})


TABLAS = {
    "simple": tabla_retail_simple,
    "retail_bps": tabla_retail_bps,
    "bev": tabla_bev,
    "wholesale": tabla_wholesale,
    "grupo": tabla_retail_simple,
    "penetracion": tabla_penetracion,
}
TITULOS = {
    "simple": lambda marca: f"UC {marca} 2026",
    "retail_bps": lambda marca: f"UC {marca} (Retail + {'BPS' if marca == 'BMW' else 'M-NEXT'})",
    "bev": lambda marca: f"BEV {marca}",
    "wholesale": lambda marca: f"WHOLESALE {marca}",
    "grupo": lambda marca: f"UC {marca} (Grupo Propietario)",
    "penetracion": lambda marca: f"PENETRACIÓN MERCADO {marca}",
}
ORDEN_TIPOS = ["simple", "retail_bps", "bev", "wholesale", "grupo", "penetracion"]
