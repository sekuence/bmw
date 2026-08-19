import streamlit as st

from src import config, detail, metrics

st.set_page_config(page_title="Ranking de concesionarios", page_icon="🏆", layout="wide")

if not st.session_state.get("cargado"):
    st.warning("Primero sube el archivo de ventas en la página principal (Home).")
    st.page_link("app.py", label="⬅️ Ir a Home")
    st.stop()

dealers = st.session_state["dealers"]
resumen = st.session_state["resumen"]

st.title("🏆 Ranking de concesionarios")

c1, c2, c3 = st.columns([1, 2, 1])
with c1:
    marca = st.radio("Marca", ["BMW", "MINI"], horizontal=True)
with c2:
    periodo = st.selectbox(
        "Periodo",
        config.MESES + ["TRIMESTRE 1", "TRIMESTRE 2", "TRIMESTRE 3", "TRIMESTRE 4",
                         "SEMESTRE 1", "SEMESTRE 2", "ACUMULADO MES", "ACUMULADO MES 2S", "ANUAL"],
        index=len(config.MESES) + 6,
    )
with c3:
    mes_referencia = None
    if periodo == "ACUMULADO MES":
        mes_referencia = st.selectbox("Hasta el mes de", config.MESES, index=6)
    elif periodo == "ACUMULADO MES 2S":
        mes_referencia = st.selectbox("Hasta el mes de", config.MESES_S2, index=0)

tabla = metrics.ranking_periodo(resumen, dealers, marca, periodo, mes_referencia)

if tabla.empty:
    st.info("No hay concesionarios de esta marca en el maestro.")
else:
    st.dataframe(
        tabla,
        width="stretch",
        hide_index=True,
        column_config={
            "% bps": st.column_config.NumberColumn(format="%.1f%%"),
            "% remarketing": st.column_config.NumberColumn(format="%.1f%%"),
            "% bev": st.column_config.NumberColumn(format="%.1f%%"),
        },
    )
    st.bar_chart(tabla.set_index("concesionario")["retail"])

    st.divider()
    st.subheader("🔎 Ver detalle de vehículos")
    d1, d2 = st.columns(2)
    with d1:
        concesionario_detalle = st.selectbox("Concesión", tabla["concesionario"])
    with d2:
        metrica_detalle = st.selectbox("Métrica", list(config.METRICAS_AJUSTABLES.values()))

    codigo_detalle = int(tabla.loc[tabla["concesionario"] == concesionario_detalle, "codigo_dealer"].iloc[0])
    metrica_key = next(k for k, v in config.METRICAS_AJUSTABLES.items() if v == metrica_detalle)
    meses = metrics.meses_de_periodo(periodo, mes_referencia)

    ventas = st.session_state["ventas"]
    filas = detail.filtrar(ventas, codigo_dealer=codigo_detalle, marca=marca, meses=meses, metrica=metrica_key)
    st.caption(f"{len(filas)} vehículos")
    st.dataframe(filas, width="stretch", hide_index=True, height=350)
