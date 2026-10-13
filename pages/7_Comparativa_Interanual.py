"""Compara los KPIs de este año con los del año pasado: sube aparte el
archivo de ventas del año anterior (mismo formato, hoja BBDD) y se
compara concesionario a concesionario contra el archivo ya cargado en
Home -no sustituye nada, son dos datasets independientes en memoria."""
import streamlit as st

from src import comparativa, config, ingest, metrics

st.set_page_config(page_title="Comparativa interanual", page_icon="📆", layout="wide")

if not st.session_state.get("cargado"):
    st.warning("Primero sube el archivo de ventas de este año en la página principal (Home).")
    st.page_link("app.py", label="⬅️ Ir a Home")
    st.stop()

dealers = st.session_state["dealers"]
resumen_actual = st.session_state["resumen"]

st.title("📆 Comparativa interanual")
st.caption(
    "Sube el archivo de ventas del año pasado (mismo formato, hoja **BBDD**) para comparar "
    "Retail, BPS/MN, Remarketing, BEV y Wholesale concesionario a concesionario frente a este año."
)

archivo_anterior = st.file_uploader("Archivo de ventas del año pasado (.xlsx)", type=["xlsx"], key="uploader_anterior")
if archivo_anterior is not None:
    try:
        raw = ingest.read_bbdd(archivo_anterior)
        ventas_anterior = ingest.clean_ventas(raw)
    except ingest.VentasFileError as exc:
        st.error(str(exc))
    else:
        st.session_state["ventas_anterior"] = ventas_anterior
        st.session_state["resumen_anterior"] = metrics.build_monthly_summary(ventas_anterior)
        st.session_state["cargado_anterior"] = True
        st.success(f"Cargadas {len(ventas_anterior):,} filas de venta del año pasado.".replace(",", "."))

if not st.session_state.get("cargado_anterior"):
    st.info("⬆️ Sube el archivo del año pasado para ver la comparativa.")
    st.stop()

resumen_anterior = st.session_state["resumen_anterior"]

st.divider()

c1, c2, c3, c4 = st.columns([1, 2, 1, 1.3])
with c1:
    marca = st.radio("Marca", ["BMW", "MINI"], horizontal=True, key="comp_marca")
with c2:
    periodo = st.selectbox(
        "Periodo",
        config.MESES + ["TRIMESTRE 1", "TRIMESTRE 2", "TRIMESTRE 3", "TRIMESTRE 4",
                         "SEMESTRE 1", "SEMESTRE 2", "ACUMULADO MES", "ACUMULADO MES 2S", "ANUAL"],
        index=len(config.MESES) + 6,
        key="comp_periodo",
    )
with c3:
    mes_referencia = None
    if periodo == "ACUMULADO MES":
        mes_referencia = st.selectbox("Hasta el mes de", config.MESES, index=6, key="comp_mes_ref")
    elif periodo == "ACUMULADO MES 2S":
        mes_referencia = st.selectbox("Hasta el mes de", config.MESES_S2, index=0, key="comp_mes_ref_2s")
with c4:
    metrica = st.selectbox("Métrica de las tarjetas resumen", list(comparativa.METRICAS_LEGIBLES.keys()), format_func=lambda m: comparativa.METRICAS_LEGIBLES[m], key="comp_metrica")

tabla = comparativa.tabla_comparativa(resumen_actual, resumen_anterior, dealers, marca, periodo, mes_referencia)

st.subheader("Resumen")
totales = comparativa.totales_comparativa(tabla, metrica)
tc1, tc2, tc3 = st.columns(3)
tc1.metric(f"{comparativa.METRICAS_LEGIBLES[metrica]} -este año", totales["actual"])
tc2.metric(f"{comparativa.METRICAS_LEGIBLES[metrica]} -año pasado", totales["anterior"])
pct_txt = f"{totales['var_pct'] * 100:+.1f}%" if totales["var_pct"] is not None else None
tc3.metric("Variación", f"{totales['var_abs']:+d}", pct_txt)

st.divider()
st.subheader("Por concesionario")
cols_mostrar = ["concesionario", "grupo_propietario", f"{metrica}_actual", f"{metrica}_anterior", f"{metrica}_var_abs", f"{metrica}_var_pct"]
tabla_mostrar = tabla[cols_mostrar].rename(columns={
    "concesionario": "Concesionario",
    "grupo_propietario": "Grupo propietario",
    f"{metrica}_actual": "Este año",
    f"{metrica}_anterior": "Año pasado",
    f"{metrica}_var_abs": "Variación",
    f"{metrica}_var_pct": "Variación %",
})
st.dataframe(
    tabla_mostrar,
    width="stretch",
    hide_index=True,
    column_config={"Variación %": st.column_config.NumberColumn(format="%.1f%%")},
)

st.divider()
st.subheader("📥 Descargar comparativa completa")
st.caption("El Excel incluye las 7 métricas (Retail, BPS/MN, Remarketing, BEV, Wholesale UC/YUC, Ventas totales), no sólo la de las tarjetas.")
if st.button("Generar Excel comparativo"):
    st.session_state["comparativa_bytes"] = comparativa.build_workbook(tabla, marca, periodo)
    st.session_state["comparativa_nombre"] = f"Comparativa_{marca}_{periodo.replace(' ', '_')}.xlsx"
    st.success("Listo.")

if "comparativa_bytes" in st.session_state:
    st.download_button(
        "⬇️ Descargar Excel",
        data=st.session_state["comparativa_bytes"],
        file_name=st.session_state.get("comparativa_nombre", "Comparativa.xlsx"),
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
