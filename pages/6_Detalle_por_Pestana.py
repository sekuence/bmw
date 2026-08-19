"""Desglose mensual por concesionario, un apartado por cada pestaña del
Excel de seguimiento original (UC BMW/MINI, BPS, BEV, Wholesale,
Maestro...)."""
import pandas as pd
import streamlit as st

from src import config, metrics, storage

st.set_page_config(page_title="Detalle por pestaña", page_icon="🗂️", layout="wide")

if not st.session_state.get("cargado"):
    st.warning("Primero sube el archivo de ventas en la página principal (Home).")
    st.page_link("app.py", label="⬅️ Ir a Home")
    st.stop()

dealers = st.session_state["dealers"]
resumen = st.session_state["resumen"]

st.title("🗂️ Detalle por pestaña")
st.caption(
    "Un apartado por cada pestaña del Excel de seguimiento original, con el mismo desglose "
    "mes a mes por concesionario."
)

resumen_ajustado = metrics.aplicar_ajustes(resumen)
objetivos = storage.read_table("objetivos")


def _objetivo_pivot(marca: str, metrica: str) -> dict:
    if objetivos.empty:
        return {}
    sub = objetivos[(objetivos["marca"] == marca) & (objetivos["metrica"] == metrica)]
    return {(int(r["codigo_dealer"]), r["mes"]): r["valor"] for _, r in sub.iterrows()}


def _dealers_de(marca: str, agrupar: bool) -> pd.DataFrame:
    col = "vende_bmw" if marca == "BMW" else "vende_mini"
    d = dealers[dealers[col] == "Si"]
    if agrupar:
        return d[["grupo_propietario"]].drop_duplicates().sort_values("grupo_propietario")
    return d.sort_values("concesionario")


def _resumen_grupo(sub_marca: pd.DataFrame, codigo_o_grupo, agrupar: bool, dealers_marca_completo: pd.DataFrame) -> pd.DataFrame:
    if not agrupar:
        return sub_marca[sub_marca["codigo_dealer"] == codigo_o_grupo]
    codigos = dealers_marca_completo.loc[dealers_marca_completo["grupo_propietario"] == codigo_o_grupo, "codigo_dealer"].astype(int)
    return sub_marca[sub_marca["codigo_dealer"].isin(codigos)]


def _objetivo_grupo(pivot: dict, codigo_o_grupo, mes: str, agrupar: bool, dealers_marca_completo: pd.DataFrame) -> float:
    if not agrupar:
        return pivot.get((codigo_o_grupo, mes), 0) or 0
    codigos = dealers_marca_completo.loc[dealers_marca_completo["grupo_propietario"] == codigo_o_grupo, "codigo_dealer"].astype(int)
    return sum(pivot.get((c, mes), 0) or 0 for c in codigos)


def tabla_retail_bps(marca: str, agrupar: bool) -> pd.DataFrame:
    dealers_marca_completo = dealers[dealers["vende_bmw" if marca == "BMW" else "vende_mini"] == "Si"]
    filas_maestro = _dealers_de(marca, agrupar)
    sub_marca = resumen_ajustado[resumen_ajustado["marca"] == marca]
    obj_pivot = _objetivo_pivot(marca, "Retail")

    filas = []
    for _, d in filas_maestro.iterrows():
        clave = d["grupo_propietario"] if agrupar else int(d["codigo_dealer"])
        fila = {"Concesionario" if not agrupar else "Grupo propietario": d["grupo_propietario"] if agrupar else d["concesionario"]}
        for mes in config.MESES:
            g = _resumen_grupo(sub_marca, clave, agrupar, dealers_marca_completo)
            g_mes = g[g["mes"] == mes]
            obj = _objetivo_grupo(obj_pivot, clave, mes, agrupar, dealers_marca_completo)
            re = int(g_mes["retail"].sum())
            bps = int(g_mes["bps"].sum())
            rmk = int(g_mes["remarketing"].sum())
            corto = mes[:3]
            fila[f"{corto} OBJ"] = obj
            fila[f"{corto} RE"] = re
            fila[f"{corto} BPS"] = bps
            fila[f"{corto} %BPS"] = round(bps / re * 100, 1) if re else None
            fila[f"{corto} RMK"] = rmk
            fila[f"{corto} %RMK"] = round(rmk / re * 100, 1) if re else None
        filas.append(fila)
    return pd.DataFrame(filas)


def tabla_bev(marca: str, agrupar: bool) -> pd.DataFrame:
    dealers_marca_completo = dealers[dealers["vende_bmw" if marca == "BMW" else "vende_mini"] == "Si"]
    filas_maestro = _dealers_de(marca, agrupar)
    sub_marca = resumen_ajustado[resumen_ajustado["marca"] == marca]
    obj_pivot = _objetivo_pivot(marca, "BEV")

    filas = []
    for _, d in filas_maestro.iterrows():
        clave = d["grupo_propietario"] if agrupar else int(d["codigo_dealer"])
        fila = {"Concesionario" if not agrupar else "Grupo propietario": d["grupo_propietario"] if agrupar else d["concesionario"]}
        for mes in config.MESES:
            g = _resumen_grupo(sub_marca, clave, agrupar, dealers_marca_completo)
            g_mes = g[g["mes"] == mes]
            obj = _objetivo_grupo(obj_pivot, clave, mes, agrupar, dealers_marca_completo)
            re = int(g_mes["retail"].sum())
            bev = int(g_mes["bev"].sum())
            corto = mes[:3]
            fila[f"{corto} Objetivo"] = obj
            fila[f"{corto} BEV"] = bev
            fila[f"{corto} %BEV"] = round(bev / re * 100, 1) if re else None
        filas.append(fila)
    return pd.DataFrame(filas)


def tabla_wholesale(marca: str, agrupar: bool) -> pd.DataFrame:
    dealers_marca_completo = dealers[dealers["vende_bmw" if marca == "BMW" else "vende_mini"] == "Si"]
    filas_maestro = _dealers_de(marca, agrupar)
    sub_marca = resumen_ajustado[resumen_ajustado["marca"] == marca]

    filas = []
    for _, d in filas_maestro.iterrows():
        clave = d["grupo_propietario"] if agrupar else int(d["codigo_dealer"])
        fila = {"Concesionario" if not agrupar else "Grupo propietario": d["grupo_propietario"] if agrupar else d["concesionario"]}
        for mes in config.MESES:
            g = _resumen_grupo(sub_marca, clave, agrupar, dealers_marca_completo)
            g_mes = g[g["mes"] == mes]
            corto = mes[:3]
            fila[f"{corto} UC"] = int(g_mes["wholesale_uc"].sum())
            fila[f"{corto} YUC"] = int(g_mes["wholesale_yuc"].sum())
        filas.append(fila)
    return pd.DataFrame(filas)


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
        if tipo == "retail_bps":
            st.dataframe(tabla_retail_bps(marca, agrupar), width="stretch", hide_index=True, height=500)
        elif tipo == "bev":
            st.dataframe(tabla_bev(marca, agrupar), width="stretch", hide_index=True, height=500)
        else:
            st.dataframe(tabla_wholesale(marca, agrupar), width="stretch", hide_index=True, height=500)

with tabs[6]:
    st.caption("Maestro de concesionarios usado por la app (código, nombre, grupo propietario, marcas que vende).")
    st.dataframe(dealers, width="stretch", hide_index=True)
