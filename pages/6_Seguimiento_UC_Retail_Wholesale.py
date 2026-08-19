"""Réplica del Excel 'SEGUIMIENTO UC RETAIL & WHOLESALE': un apartado
por cada pestaña original (UC BMW, BPS, BEV, Wholesale, igual para
MINI, y Maestro), separado por marca, con las columnas agrupadas por
mes -igual que en el Excel- en vez de repetir el mes en cada celda."""
import pandas as pd
import streamlit as st

from src import config, metrics, storage

st.set_page_config(page_title="Seguimiento UC Retail & Wholesale", page_icon="🗂️", layout="wide")

if not st.session_state.get("cargado"):
    st.warning("Primero sube el archivo de ventas en la página principal (Home).")
    st.page_link("app.py", label="⬅️ Ir a Home")
    st.stop()

dealers = st.session_state["dealers"]
resumen = st.session_state["resumen"]
ventas = st.session_state["ventas"]

st.title("🗂️ Seguimiento UC Retail & Wholesale")
st.caption(
    "Un apartado por cada pestaña del Excel original, separado por marca (BMW / MINI), con "
    "el mismo desglose mes a mes por concesionario que ya conoces."
)

if config.COLUMNA_CANAL_ACTUAL in ventas.columns:
    st.success(
        "✅ La columna **Canal Actual** está presente: \"Retail origen Remarketing\" se calcula "
        "con ella, y las ventas de BYMYCAR con canal \"…DIRECTO\" ya se están reasignando a "
        "**BMW DIRECTO**."
    )
else:
    st.info(
        "ℹ️ Todavía no hay columna **Canal Actual** en este archivo de ventas. Mientras tanto, "
        "\"Retail origen Remarketing\" se calcula con la columna `Origen` (contiene "
        "\"Remarketing\") y no se reasigna nada a BMW DIRECTO. En cuanto subas un archivo que "
        "ya la traiga, la app cambia sola a la regla nueva."
    )

resumen_ajustado = metrics.aplicar_ajustes(resumen)
objetivos = storage.read_table("objetivos")

MESES_CORTOS = {m: m[:3].capitalize() for m in config.MESES}


def _objetivo_pivot(marca: str, metrica: str) -> dict:
    if objetivos.empty:
        return {}
    sub = objetivos[(objetivos["marca"] == marca) & (objetivos["metrica"] == metrica)]
    return {(int(r["codigo_dealer"]), r["mes"]): r["valor"] for _, r in sub.iterrows()}


def _dealers_de(marca: str, agrupar: bool) -> pd.DataFrame:
    """Devuelve los concesionarios de la marca **en el mismo orden en que
    aparecen en el Excel original** (agrupados por distrito, sin
    reordenar alfabéticamente)."""
    col = "vende_bmw" if marca == "BMW" else "vende_mini"
    d = dealers[dealers[col] == "Si"]
    if agrupar:
        return d[["grupo_propietario"]].drop_duplicates()
    return d


def _resumen_grupo(sub_marca: pd.DataFrame, clave, agrupar: bool, dealers_completo: pd.DataFrame) -> pd.DataFrame:
    if not agrupar:
        return sub_marca[sub_marca["codigo_dealer"] == clave]
    codigos = dealers_completo.loc[dealers_completo["grupo_propietario"] == clave, "codigo_dealer"].astype(int)
    return sub_marca[sub_marca["codigo_dealer"].isin(codigos)]


def _objetivo_grupo(pivot: dict, clave, mes: str, agrupar: bool, dealers_completo: pd.DataFrame) -> float:
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


def _construir(marca: str, agrupar: bool, sub_metricas: list[str], calculo, metrica_objetivo: str | None) -> pd.DataFrame:
    """sub_metricas: nombres de las columnas dentro de cada bloque mensual.
    calculo(g_mes, obj) -> lista de valores en el mismo orden que sub_metricas.
    Mantiene el mismo orden de concesionarios (por distrito) que el Excel
    original."""
    dealers_completo = dealers[dealers["vende_bmw" if marca == "BMW" else "vende_mini"] == "Si"]
    filas_maestro = _dealers_de(marca, agrupar)
    sub_marca = resumen_ajustado[resumen_ajustado["marca"] == marca]
    obj_pivot = _objetivo_pivot(marca, metrica_objetivo) if metrica_objetivo else {}

    etiqueta_id = "Grupo propietario" if agrupar else "Concesionario"
    columnas = pd.MultiIndex.from_tuples(
        [("", "Distrito"), ("", etiqueta_id)] + [(MESES_CORTOS[mes], sm) for mes in config.MESES for sm in sub_metricas]
    )

    filas = []
    for _, d in filas_maestro.iterrows():
        clave = d["grupo_propietario"] if agrupar else int(d["codigo_dealer"])
        fila = [_distrito_de(d, agrupar, dealers_completo), d["grupo_propietario"] if agrupar else d["concesionario"]]
        g = _resumen_grupo(sub_marca, clave, agrupar, dealers_completo)
        for mes in config.MESES:
            g_mes = g[g["mes"] == mes]
            obj = _objetivo_grupo(obj_pivot, clave, mes, agrupar, dealers_completo)
            fila.extend(calculo(g_mes, obj))
        filas.append(fila)

    return pd.DataFrame(filas, columns=columnas)


def tabla_retail_bps(marca: str, agrupar: bool) -> pd.DataFrame:
    def calculo(g_mes, obj):
        re = int(g_mes["retail"].sum())
        bps = int(g_mes["bps"].sum())
        rmk = int(g_mes["remarketing"].sum())
        return [
            obj, re,
            bps, round(bps / re * 100, 1) if re else None,
            rmk, round(rmk / re * 100, 1) if re else None,
        ]
    return _construir(marca, agrupar, ["OBJ", "RE", "BPS", "%BPS", "RMK", "%RMK"], calculo, "Retail")


def tabla_bev(marca: str, agrupar: bool) -> pd.DataFrame:
    def calculo(g_mes, obj):
        re = int(g_mes["retail"].sum())
        bev = int(g_mes["bev"].sum())
        return [obj, bev, round(bev / re * 100, 1) if re else None]
    return _construir(marca, agrupar, ["Objetivo", "BEV", "%BEV"], calculo, "BEV")


def tabla_wholesale(marca: str, agrupar: bool) -> pd.DataFrame:
    def calculo(g_mes, obj):
        return [int(g_mes["wholesale_uc"].sum()), int(g_mes["wholesale_yuc"].sum())]
    return _construir(marca, agrupar, ["UC", "YUC"], calculo, None)


tabs = st.tabs([
    "UC BMW (Retail + BPS)", "BEV BMW", "WHOLESALE BMW",
    "UC MINI (Retail + M-NEXT)", "BEV MINI", "WHOLESALE MINI",
    "MAESTRO",
])

for tab, marca, tipo in [
    (tabs[0], "BMW", "retail_bps"), (tabs[1], "BMW", "bev"), (tabs[2], "BMW", "wholesale"),
    (tabs[3], "MINI", "retail_bps"), (tabs[4], "MINI", "bev"), (tabs[5], "MINI", "wholesale"),
]:
    with tab:
        agrupar = st.checkbox("Agrupar por Grupo Propietario", key=f"agrupar_{marca}_{tipo}")
        if tipo == "wholesale":
            st.caption("Pendiente de los datos que vas a pasar aparte para Wholesale -de momento se calcula UC/YUC desde la BBDD.")
        if tipo == "retail_bps":
            st.dataframe(tabla_retail_bps(marca, agrupar), width="stretch", height=500, hide_index=True)
        elif tipo == "bev":
            st.dataframe(tabla_bev(marca, agrupar), width="stretch", height=500, hide_index=True)
        else:
            st.dataframe(tabla_wholesale(marca, agrupar), width="stretch", height=500, hide_index=True)

with tabs[6]:
    st.caption("Maestro de concesionarios usado por la app (código, nombre, grupo propietario, marcas que vende).")
    st.dataframe(dealers, width="stretch", hide_index=True)
