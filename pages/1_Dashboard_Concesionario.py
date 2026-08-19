import streamlit as st

from src import config, dashboard, detail

st.set_page_config(page_title="Dashboard por concesionario", page_icon="📈", layout="wide")

if not st.session_state.get("cargado"):
    st.warning("Primero sube el archivo de ventas en la página principal (Home).")
    st.page_link("app.py", label="⬅️ Ir a Home")
    st.stop()

dealers = st.session_state["dealers"]
resumen = st.session_state["resumen"]
ventas = st.session_state["ventas"]

st.title("📈 Dashboard por concesionario")

col_sel1, col_sel2, col_sel3 = st.columns([2, 1, 1])
with col_sel1:
    opciones = dict(zip(dealers["concesionario"], dealers["codigo_dealer"]))
    concesionario = st.selectbox("Concesión", sorted(opciones.keys()))
    codigo_dealer = int(opciones[concesionario])
with col_sel2:
    periodo = st.selectbox(
        "Periodo",
        config.MESES + ["TRIMESTRE 1", "TRIMESTRE 2", "TRIMESTRE 3", "TRIMESTRE 4",
                         "SEMESTRE 1", "SEMESTRE 2", "ACUMULADO MES", "ACUMULADO MES 2S", "ANUAL"],
        index=len(config.MESES) + 6,  # ACUMULADO MES por defecto
    )
with col_sel3:
    mes_referencia = None
    if periodo == "ACUMULADO MES":
        mes_referencia = st.selectbox("Hasta el mes de", config.MESES, index=6)
    elif periodo == "ACUMULADO MES 2S":
        mes_referencia = st.selectbox("Hasta el mes de", config.MESES_S2, index=0)

fila = dealers[dealers["codigo_dealer"] == codigo_dealer].iloc[0]
st.caption(f"Grupo propietario: **{fila['grupo_propietario']}**  ·  Código dealer: `{codigo_dealer}`")

st.divider()


def _boton_detalle(marca: str, metrica: str, meses: list[str], etiqueta: str):
    with st.popover(f"🔎 Ver detalle: {etiqueta}"):
        filas = detail.filtrar(ventas, codigo_dealer=codigo_dealer, marca=marca, meses=meses, metrica=metrica)
        st.caption(f"{len(filas)} vehículos")
        st.dataframe(filas, width="stretch", hide_index=True, height=350)


marcas_disponibles = []
if fila["vende_bmw"] == "Si":
    marcas_disponibles.append("BMW")
if fila["vende_mini"] == "Si":
    marcas_disponibles.append("MINI")

cols = st.columns(len(marcas_disponibles)) if marcas_disponibles else []

for col, marca in zip(cols, marcas_disponibles):
    with col:
        st.subheader(marca)
        k = dashboard.kpi_bloque(resumen, codigo_dealer, marca, periodo, mes_referencia)
        meses = k["meses_incluidos"]

        st.caption("Meses incluidos: " + ", ".join(meses))

        m1, m2 = st.columns(2)
        m1.metric("Objetivo Retail", f"{k['objetivo_retail']:.0f}")
        m2.metric(
            "Realizado Retail",
            f"{k['realizado_retail']:.0f}",
            delta=f"{k['pct_cumplimiento_retail']*100:.0f}% del objetivo" if k["pct_cumplimiento_retail"] is not None else "sin objetivo",
        )
        _boton_detalle(marca, "retail", meses, "Ventas Retail")

        st.markdown("**BPS / MN**")
        b1, b2 = st.columns(2)
        b1.metric("Ventas BPS/MN", f"{k['bps']:.0f}")
        b2.metric("% BPS/MN sobre retail", f"{k['pct_bps']*100:.1f}%" if k["pct_bps"] is not None else "—")
        if k["ventas_bps_necesarias_para_25pct"] > 0:
            st.caption(f"Necesarias ≈ {k['ventas_bps_necesarias_para_25pct']} uds. BPS/MN más para acercarse al objetivo interno de penetración.")
        _boton_detalle(marca, "bps", meses, "BPS / MN")

        st.markdown("**Retail origen Remarketing**")
        r1, r2 = st.columns(2)
        r1.metric("Ventas remarketing", f"{k['remarketing']:.0f}")
        r2.metric("% sobre retail", f"{k['pct_remarketing']*100:.1f}%" if k["pct_remarketing"] is not None else "—")
        with st.expander("Uds. necesarias para alcanzar cada tramo de % remarketing"):
            for banda in k["bandas_remarketing_necesarias"]:
                st.write(f"≥ {banda['umbral']*100:.0f}% → faltan **{banda['necesarias']}** uds.")
        _boton_detalle(marca, "remarketing", meses, "Remarketing")

        st.markdown("**BEV**")
        e1, e2 = st.columns(2)
        e1.metric("Ventas BEV", f"{k['bev']:.0f}", help=f"Objetivo: {k['objetivo_bev']:.0f}")
        e2.metric("% BEV sobre retail", f"{k['pct_bev']*100:.1f}%" if k["pct_bev"] is not None else "—")
        with st.expander("Uds. necesarias para alcanzar cada tramo de % BEV"):
            for banda in k["bandas_bev_necesarias"]:
                st.write(f"≥ {banda['umbral']*100:.0f}% → faltan **{banda['necesarias']}** uds.")
        _boton_detalle(marca, "bev", meses, "BEV")

        st.markdown("**Wholesale**")
        w1, w2 = st.columns(2)
        w1.metric("UC", k["wholesale_uc"])
        w2.metric("YUC", k["wholesale_yuc"])
        _boton_detalle(marca, "wholesale_uc", meses, "Wholesale UC")

        st.markdown("**Ventas totales (Retail + Wholesale)**")
        st.metric("Total vehículos vendidos", k["ventas_totales"])
        _boton_detalle(marca, "ventas_totales", meses, "Ventas Totales")

        st.markdown("**Penetración de mercado (&lt;6 años)**")
        if k["mercado_menos_6_anos"] is not None:
            p1, p2 = st.columns(2)
            p1.metric("Mercado <6 años", f"{k['mercado_menos_6_anos']:.0f}")
            p2.metric("% Penetración", f"{k['pct_penetracion_mercado']*100:.1f}%" if k["pct_penetracion_mercado"] is not None else "—")
        else:
            st.caption("Sin dato de tamaño de mercado para este periodo -añádelo en 'Objetivos y datos manuales'.")

        st.markdown("**Mystery Shopping**")
        if k["mystery_shopping"] is not None:
            st.metric("Puntuación", f"{k['mystery_shopping']:.1f}")
        else:
            st.caption("Sin dato de mystery shopping para este semestre -añádelo en 'Objetivos y datos manuales'.")

        st.divider()
        st.markdown("**Evolución mensual**")
        evolucion = dashboard.evolucion_mensual(resumen, codigo_dealer, marca)
        if evolucion.empty:
            st.caption("Todavía no hay ventas cargadas para esta marca.")
        else:
            tab_retail, tab_otros = st.tabs(["Objetivo vs Realizado", "BPS / Remarketing / BEV"])
            with tab_retail:
                st.bar_chart(evolucion[["Objetivo Retail", "Realizado Retail"]])
            with tab_otros:
                st.line_chart(evolucion[["BPS/MN", "Remarketing", "BEV"]])
