import streamlit as st

from src import config, export

st.set_page_config(page_title="Exportar a Excel", page_icon="⬇️", layout="wide")

if not st.session_state.get("cargado"):
    st.warning("Primero sube el archivo de ventas en la página principal (Home).")
    st.page_link("app.py", label="⬅️ Ir a Home")
    st.stop()

dealers = st.session_state["dealers"]
resumen = st.session_state["resumen"]

st.title("⬇️ Exportar a Excel")
st.caption("Genera un .xlsx con el resumen tipo 'Dealer Dashboard' para todos los concesionarios de una marca, más el detalle mensual.")

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

if st.button("Generar Excel"):
    contenido = export.build_workbook(resumen, dealers, marca, periodo, mes_referencia)
    st.session_state["export_bytes"] = contenido
    st.success("Listo.")

if "export_bytes" in st.session_state:
    st.download_button(
        "📥 Descargar Excel",
        data=st.session_state["export_bytes"],
        file_name=f"Seguimiento_{marca}_{periodo.replace(' ', '_')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
