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
st.caption(
    "Genera un .xlsx con el resumen tipo 'Dealer Dashboard' -más el detalle mensual- para "
    "uno, varios o todos los concesionarios de una marca."
)

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

col_marca = "vende_bmw" if marca == "BMW" else "vende_mini"
concesionarios_marca = dealers[dealers[col_marca] == "Si"].sort_values("concesionario")
opciones = concesionarios_marca["concesionario"].tolist()

todos = st.checkbox("Incluir todos los concesionarios", value=True)
if todos:
    seleccion = opciones
else:
    seleccion = st.multiselect("Concesionarios a incluir", opciones)

codigos = concesionarios_marca.loc[concesionarios_marca["concesionario"].isin(seleccion), "codigo_dealer"].astype(int).tolist()

st.divider()

if not codigos:
    st.info("Elige al menos un concesionario para ver la vista previa y poder generar el Excel.")
else:
    tarjetas = export.resumen_dealers(resumen, dealers, marca, periodo, mes_referencia, codigos=codigos)
    st.subheader(f"Vista previa ({len(tarjetas)} concesionario{'s' if len(tarjetas) != 1 else ''})")

    cols_por_fila = 3
    for i in range(0, len(tarjetas), cols_por_fila):
        cols = st.columns(cols_por_fila)
        for col, t in zip(cols, tarjetas[i:i + cols_por_fila]):
            with col:
                with st.container(border=True):
                    st.markdown(f"**{t['concesionario']}**")
                    st.caption(t["grupo_propietario"])
                    pct = t["pct_cumplimiento"]
                    st.progress(min(pct, 1.0) if pct is not None else 0.0)
                    pct_txt = f"{pct * 100:.0f}%" if pct is not None else "sin objetivo"
                    st.caption(f"Retail: {t['realizado_retail']} / {t['objetivo_retail']} ({pct_txt})")
                    mc1, mc2 = st.columns(2)
                    mc1.metric("BPS/MN", t["bps"])
                    mc2.metric("BEV", t["bev"])

    st.divider()

    if st.button("Generar Excel"):
        contenido = export.build_workbook(resumen, dealers, marca, periodo, mes_referencia, codigos=codigos)
        st.session_state["export_bytes"] = contenido
        st.session_state["export_nombre"] = f"Seguimiento_{marca}_{periodo.replace(' ', '_')}.xlsx"
        st.success("Listo.")

    if "export_bytes" in st.session_state:
        st.download_button(
            "📥 Descargar Excel",
            data=st.session_state["export_bytes"],
            file_name=st.session_state.get("export_nombre", f"Seguimiento_{marca}_{periodo.replace(' ', '_')}.xlsx"),
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
