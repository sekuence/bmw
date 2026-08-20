import streamlit as st

from src import config, dashboard, detail, guia, ingest, metrics, theme

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

remarketing_disponible = ingest.remarketing_disponible(ventas)
if not remarketing_disponible:
    st.info(
        "ℹ️ \"Retail origen Remarketing\" no está disponible todavía -depende de la columna "
        "**Canal Actual**, que aún no trae el archivo de ventas."
    )

cols = st.columns(len(marcas_disponibles)) if marcas_disponibles else []

for col, marca in zip(cols, marcas_disponibles):
    with col:
        theme.encabezado(marca)
        k = dashboard.kpi_bloque(resumen, codigo_dealer, marca, periodo, mes_referencia, remarketing_disponible)
        meses = k["meses_incluidos"]

        st.caption("Meses incluidos: " + ", ".join(meses))

        if "BYMYCAR" in concesionario.upper():
            directo = metrics.kpis_bymycar_directo(ventas, marca, periodo, mes_referencia)
            with st.container(border=True):
                st.markdown("**🅱️ BMW DIRECTO** (ventas de BYMYCAR con Canal Actual \"…DIRECTO\")")
                if remarketing_disponible:
                    st.caption("No cuentan en el Retail/BPS/BEV de BYMYCAR de arriba -se muestran aparte-.")
                    d1, d2, d3 = st.columns(3)
                    d1.metric("Retail", directo["retail"])
                    d2.metric("BPS/MN", directo["bps"])
                    d3.metric("BEV", directo["bev"])
                else:
                    st.caption("No disponible -depende de la columna Canal Actual, que aún no trae el archivo de ventas.")

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
        st.markdown(theme.semaforo(k["cumple_penetracion_bps"]) + " (mínimo 80%)", unsafe_allow_html=True)
        if k["ventas_bps_necesarias_para_25pct"] > 0:
            st.caption(f"Necesarias ≈ {k['ventas_bps_necesarias_para_25pct']} uds. BPS/MN más para acercarse al objetivo interno de penetración.")
        _boton_detalle(marca, "bps", meses, "BPS / MN")

        st.markdown("**Retail origen Remarketing**")
        if remarketing_disponible:
            r1, r2 = st.columns(2)
            r1.metric("Ventas remarketing", f"{k['remarketing']:.0f}")
            r2.metric("% sobre objetivo retail", f"{k['pct_remarketing']*100:.1f}%" if k["pct_remarketing"] is not None else "—")
            with st.expander("Uds. necesarias para alcanzar cada tramo de % remarketing"):
                for banda in k["bandas_remarketing_necesarias"]:
                    st.write(f"≥ {banda['umbral']*100:.0f}% → faltan **{banda['necesarias']}** uds.")
            _boton_detalle(marca, "remarketing", meses, "Remarketing")
        else:
            st.caption("No disponible -falta la columna Canal Actual en el archivo de ventas.")

        st.markdown("**BEV** (todas las ventas BEV, Retail + Wholesale)")
        e1, e2 = st.columns(2)
        e1.metric("Ventas BEV", f"{k['bev']:.0f}", help=f"Objetivo: {k['objetivo_bev']:.0f}")
        e2.metric("% BEV sobre objetivo retail", f"{k['pct_bev']*100:.1f}%" if k["pct_bev"] is not None else "—")
        with st.expander("Uds. necesarias para alcanzar cada tramo de % BEV"):
            for banda in k["bandas_bev_necesarias"]:
                st.write(f"≥ {banda['umbral']*100:.0f}% → faltan **{banda['necesarias']}** uds.")
        _boton_detalle(marca, "bev", meses, "BEV")

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
            st.markdown(theme.semaforo(k["cumple_mystery_shopping"]) + " (mínimo 90%)", unsafe_allow_html=True)
        else:
            st.caption("Sin dato de mystery shopping para este semestre -añádelo en 'Objetivos y datos manuales'.")

        st.markdown("**💰 Bonificación estimada**")
        bono = k["bonificacion"]
        if bono["total"] is not None:
            bo1, bo2, bo3 = st.columns(3)
            bo1.metric("€ / vehículo (matriz x BEV)", f"{bono['total']:.2f} €", help=f"Base {bono['base']:.0f} € x multiplicador BEV x{bono['multiplicador']:.2f}")
            bo2.metric("Ventas Retail", f"{k['realizado_retail']:.0f}")
            bo3.metric("Total a cobrar", f"{bono['total_a_cobrar']:.0f} €" if bono["total_a_cobrar"] is not None else "—")
            if k["cumple_penetracion_bps"] is False or k["cumple_mystery_shopping"] is False:
                st.warning("⚠️ No cumple algún mínimo (penetración BPS/MN y/o Mystery Shopping) -puede que este importe no aplique.")
        elif not remarketing_disponible:
            st.caption("No se puede calcular todavía -depende de \"Retail origen Remarketing\" (falta la columna Canal Actual).")
        else:
            st.caption("Sin objetivo o sin ventas suficientes para ubicarlo en la matriz de bonificación.")
        with st.expander("📖 Ver guía de bonificación"):
            st.markdown(guia.render(marca), unsafe_allow_html=True)

        st.divider()
        st.markdown("**Evolución mensual**")
        evolucion = dashboard.evolucion_mensual(resumen, codigo_dealer, marca, remarketing_disponible)
        if evolucion.empty:
            st.caption("Todavía no hay ventas cargadas para esta marca.")
        else:
            tab_retail, tab_otros = st.tabs(["Objetivo vs Realizado", "BPS / Remarketing / BEV"])
            with tab_retail:
                st.bar_chart(evolucion[["Objetivo Retail", "Realizado Retail"]], color=theme.paleta(marca, 2), sort=False)
            with tab_otros:
                cols_otros = ["BPS/MN"] + (["Remarketing"] if remarketing_disponible else []) + ["BEV"]
                st.line_chart(evolucion[cols_otros], color=theme.paleta(marca, len(cols_otros)))
