"""Réplica del Excel 'SEGUIMIENTO UC RETAIL & WHOLESALE': un apartado
por cada pestaña original (UC BMW, BPS, BEV, Wholesale, Grupo
Propietario, Penetración de mercado, igual para MINI, y Maestro),
separado por marca, con las columnas agrupadas por mes -igual que en
el Excel- más los acumulados (Mes, Anual, Semestre 1, Semestre 2) que
trae el Excel original a la derecha del todo."""
import pandas as pd
import streamlit as st

from src import config, export_plantilla, export_seguimiento, ingest, metrics, storage, theme

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
    "el mismo desglose mes a mes por concesionario -más los acumulados de la derecha- que ya "
    "conoces."
)

remarketing_disponible = ingest.remarketing_disponible(ventas)
if remarketing_disponible:
    st.success(
        "✅ La columna **Canal Actual** está presente: \"Retail origen Remarketing\" se calcula "
        "con ella, y las ventas de BYMYCAR con canal \"…DIRECTO\" aparecen como la fila "
        "**BMW DIRECTO** en las tablas de BYMYCAR de abajo."
    )
else:
    st.info(
        "ℹ️ Todavía no hay columna **Canal Actual** en este archivo de ventas, así que "
        "\"Retail origen Remarketing\" (columnas RMK / %RMK) no se puede calcular -salen en "
        "blanco- y la fila BMW DIRECTO sale siempre a 0. En cuanto subas un archivo que ya la "
        "traiga, la app cambia sola a la regla nueva."
    )

resumen_ajustado = metrics.aplicar_ajustes(resumen)
# Las ventas "Directo" de BYMYCAR se mezclan aquí como si fueran un
# concesionario más (codigo_dealer=CODIGO_BYMYCAR_DIRECTO) para que
# salgan como una fila extra en las tablas de abajo, no en una pestaña
# aparte.
resumen_ajustado = pd.concat(
    [resumen_ajustado, metrics.build_bymycar_directo_summary(ventas)], ignore_index=True
)
objetivos = storage.read_table("objetivos")
mercado = storage.read_table("mercado_menos_6_anos")

MESES_CORTOS = {m: m[:3].capitalize() for m in config.MESES}

meses_con_datos = sorted(resumen["mes"].unique(), key=config.MESES.index) if not resumen.empty else []
mes_acumulado = st.selectbox(
    "\"Acumulado Mes\" hasta el mes de",
    config.MESES,
    index=config.MESES.index(meses_con_datos[-1]) if meses_con_datos else 0,
    help="Controla hasta qué mes suma la columna 'Acum. Mes' de todas las tablas de abajo.",
)


def _bloques_periodo() -> list[tuple[str, list[str]]]:
    idx = config.MESES.index(mes_acumulado)
    bloques = [(MESES_CORTOS[m], [m]) for m in config.MESES]
    bloques.append(("Acum. Mes", config.MESES[: idx + 1]))
    bloques.append(("Anual", config.MESES))
    bloques.append(("Sem. 1", config.MESES_S1))
    bloques.append(("Sem. 2", config.MESES_S2))
    return bloques


def _objetivo_pivot(marca: str, metrica: str) -> dict:
    if objetivos.empty:
        return {}
    sub = objetivos[(objetivos["marca"] == marca) & (objetivos["metrica"] == metrica)]
    return {(int(r["codigo_dealer"]), r["mes"]): r["valor"] for _, r in sub.iterrows()}


def _mercado_pivot(marca: str) -> dict:
    if mercado.empty:
        return {}
    sub = mercado[mercado["marca"] == marca]
    return {(int(r["codigo_dealer"]), r["mes"]): r["valor"] for _, r in sub.iterrows()}


_FILA_BYMYCAR_DIRECTO = pd.DataFrame([{
    "codigo_dealer": metrics.CODIGO_BYMYCAR_DIRECTO,
    "distrito": pd.NA,
    "concesionario": "BMW DIRECTO",
    "grupo_propietario": "",
}])


def _dealers_de(marca: str, agrupar: bool) -> pd.DataFrame:
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
    return pd.concat([d, _FILA_BYMYCAR_DIRECTO], ignore_index=True)


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


def construir(marca: str, agrupar: bool, sub_metricas: list[str], calculo, pivots: dict[str, dict] | None = None) -> pd.DataFrame:
    """sub_metricas: nombres de las columnas dentro de cada bloque de
    periodo. calculo(g_bloque, **extras) -> lista de valores en el mismo
    orden que sub_metricas, donde `extras` trae un valor (sumado en ese
    bloque) por cada entrada de `pivots` -p.ej. {'obj': ..., 'obj_bev': ...}-.
    Incluye los meses sueltos + Acum. Mes / Anual / Sem. 1 / Sem. 2, y
    mantiene el orden de concesionarios (por distrito) del Excel original."""
    dealers_completo = dealers[dealers["vende_bmw" if marca == "BMW" else "vende_mini"] == "Si"]
    filas_maestro = _dealers_de(marca, agrupar)
    sub_marca = resumen_ajustado[resumen_ajustado["marca"] == marca]
    bloques = _bloques_periodo()
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


def tabla_retail_simple(marca: str, agrupar: bool) -> pd.DataFrame:
    """Equivalente a la pestaña 'UC BMW/MINI 2026' original: sólo
    Objetivo y Realizado de ventas Retail."""
    def calculo(g_bloque, obj):
        return [obj, int(g_bloque["retail"].sum())]
    return construir(marca, agrupar, ["OBJ", "RE"], calculo, {"obj": _objetivo_pivot(marca, "Retail")})


def tabla_retail_bps(marca: str, agrupar: bool) -> pd.DataFrame:
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
    return construir(marca, agrupar, ["OBJ", "RE", "BPS", "%BPS", "RMK", "%RMK"], calculo, {"obj": _objetivo_pivot(marca, "Retail")})


def tabla_bev(marca: str, agrupar: bool) -> pd.DataFrame:
    # %BEV se calcula sobre el Objetivo Retail (igual que en el Excel
    # original), no sobre el Realizado ni sobre el Objetivo BEV.
    def calculo(g_bloque, obj_bev, obj_retail):
        bev = int(g_bloque["bev"].sum())
        return [obj_bev, bev, round(bev / obj_retail * 100, 1) if obj_retail else None]
    return construir(
        marca, agrupar, ["Objetivo", "BEV", "%BEV"], calculo,
        {"obj_bev": _objetivo_pivot(marca, "BEV"), "obj_retail": _objetivo_pivot(marca, "Retail")},
    )


def tabla_wholesale(marca: str, agrupar: bool) -> pd.DataFrame:
    def calculo(g_bloque):
        return [int(g_bloque["wholesale_uc"].sum()), int(g_bloque["wholesale_yuc"].sum())]
    return construir(marca, agrupar, ["UC", "YUC"], calculo)


def tabla_penetracion(marca: str, agrupar: bool) -> pd.DataFrame:
    """Equivalente a 'PENETRACIÓN MERCADO VO BMW/MINI': tamaño de mercado
    <6 años (dato manual) vs ventas Retail realizadas."""
    def calculo(g_bloque, mdo):
        re = int(g_bloque["retail"].sum())
        return [mdo or None, re, round(re / mdo * 100, 1) if mdo else None]
    return construir(marca, agrupar, ["Mdo <6 años", "Vta Retail", "%Penetración"], calculo, {"mdo": _mercado_pivot(marca)})


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

tabs = st.tabs(
    [TITULOS[t]("BMW") for t in ORDEN_TIPOS]
    + [TITULOS[t]("MINI") for t in ORDEN_TIPOS]
    + ["MAESTRO"]
)

combinaciones = [(marca, tipo) for marca in ("BMW", "MINI") for tipo in ORDEN_TIPOS]

for tab, (marca, tipo) in zip(tabs, combinaciones):
    with tab:
        theme.encabezado(marca)
        agrupar_fijo = tipo == "grupo"
        if agrupar_fijo:
            agrupar = True
        else:
            agrupar = st.checkbox("Agrupar por Grupo Propietario", key=f"agrupar_{marca}_{tipo}")
        if tipo == "wholesale":
            st.caption("Pendiente de los datos que vas a pasar aparte para Wholesale -de momento se calcula UC/YUC desde la BBDD.")
        if tipo == "penetracion" and mercado.empty:
            st.caption("Sin datos de tamaño de mercado <6 años todavía -añádelos en 'Objetivos y datos manuales'.")
        st.dataframe(TABLAS[tipo](marca, agrupar), width="stretch", height=500, hide_index=True)

with tabs[-1]:
    st.caption("Maestro de concesionarios usado por la app (código, nombre, grupo propietario, marcas que vende).")
    st.dataframe(dealers, width="stretch", hide_index=True)

st.divider()
st.subheader("📥 Descargar todo el Seguimiento")
st.caption("Genera un único Excel con todas las pestañas de arriba (BMW y MINI), tal cual las ves aquí.")
if st.button("Generar Excel completo"):
    contenido = export_seguimiento.build_workbook(
        {(marca, tipo): TABLAS[tipo](marca, tipo == "grupo" or st.session_state.get(f"agrupar_{marca}_{tipo}", False)) for marca, tipo in combinaciones},
        TITULOS,
        dealers,
    )
    st.session_state["seguimiento_export_bytes"] = contenido
    st.success("Listo.")

if "seguimiento_export_bytes" in st.session_state:
    st.download_button(
        "⬇️ Descargar Seguimiento_completo.xlsx",
        data=st.session_state["seguimiento_export_bytes"],
        file_name="Seguimiento_UC_Retail_Wholesale_completo.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

st.divider()
st.subheader("📥 Descargar en el formato original (tu plantilla)")
st.caption(
    "En vez de generar un Excel desde cero, rellena tu propio archivo de seguimiento "
    "-mismo diseño, logos y agrupación por Distrito- con los datos ya calculados. Los "
    "porcentajes y la vista por Grupo Propietario son fórmulas locales del propio archivo: "
    "Excel las recalcula solas al abrirlo, no hace falta esperar."
)
if not export_plantilla.plantilla_disponible():
    st.info("No hay plantilla cargada todavía en la app.")
else:
    st.caption(
        "Un mes sin archivo de ventas subido se deja en blanco -nunca se rellena con el dato "
        "antiguo que traía la plantilla ni con un 0 engañoso."
    )
    meses_presentes = sorted(ventas["mes"].unique(), key=config.MESES.index) if len(ventas) else []
    mes_por_defecto = meses_presentes[-1] if meses_presentes else config.MESES[0]
    mes_referencia_plantilla = st.selectbox(
        "Hasta el mes de (columnas \"Acumulado Mes\" y \"Dealer Dashboard\" de la plantilla)",
        config.MESES,
        index=config.MESES.index(mes_por_defecto),
    )
    if st.button("Generar Excel con tu plantilla"):
        st.session_state["plantilla_export_bytes"] = export_plantilla.rellenar_plantilla(
            resumen_ajustado, dealers, remarketing_disponible, mes_referencia_plantilla
        )
        st.session_state["plantilla_export_mes"] = mes_referencia_plantilla
        st.success("Listo.")

    if "plantilla_export_bytes" in st.session_state:
        st.download_button(
            "⬇️ Descargar Seguimiento (plantilla original).xlsx",
            data=st.session_state["plantilla_export_bytes"],
            file_name=f"Seguimiento_UC_Retail_Wholesale_{st.session_state.get('plantilla_export_mes', mes_referencia_plantilla)}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
