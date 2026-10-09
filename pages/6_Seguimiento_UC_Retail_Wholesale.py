"""Réplica del Excel 'SEGUIMIENTO UC RETAIL & WHOLESALE': un apartado
por cada pestaña original (UC BMW, BPS, BEV, Wholesale, Grupo
Propietario, Penetración de mercado, igual para MINI, y Maestro),
separado por marca, con las columnas agrupadas por mes -igual que en
el Excel- más los acumulados (Mes, Anual, Semestre 1, Semestre 2) que
trae el Excel original a la derecha del todo."""
import streamlit as st

from src import config, export_plantilla, export_seguimiento, ingest, seguimiento, storage, theme

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

resumen_ajustado = seguimiento.resumen_con_directo(resumen, ventas)
objetivos = storage.read_table("objetivos")
mercado = storage.read_table("mercado_menos_6_anos")

meses_con_datos = sorted(resumen["mes"].unique(), key=config.MESES.index) if not resumen.empty else []
mes_acumulado = st.selectbox(
    "\"Acumulado Mes\" hasta el mes de",
    config.MESES,
    index=config.MESES.index(meses_con_datos[-1]) if meses_con_datos else 0,
    help="Controla hasta qué mes suma la columna 'Acum. Mes' de todas las tablas de abajo.",
)
bloques = seguimiento.bloques_periodo(mes_acumulado)

tabs = st.tabs(
    [seguimiento.TITULOS[t]("BMW") for t in seguimiento.ORDEN_TIPOS]
    + [seguimiento.TITULOS[t]("MINI") for t in seguimiento.ORDEN_TIPOS]
    + ["MAESTRO"]
)

combinaciones = [(marca, tipo) for marca in ("BMW", "MINI") for tipo in seguimiento.ORDEN_TIPOS]

for tab, (marca, tipo) in zip(tabs, combinaciones):
    with tab:
        st.markdown(theme.encabezado(marca), unsafe_allow_html=True)
        agrupar_fijo = tipo == "grupo"
        if agrupar_fijo:
            agrupar = True
        else:
            agrupar = st.checkbox("Agrupar por Grupo Propietario", key=f"agrupar_{marca}_{tipo}")
        if tipo == "wholesale":
            st.caption("Pendiente de los datos que vas a pasar aparte para Wholesale -de momento se calcula UC/YUC desde la BBDD.")
        if tipo == "penetracion" and mercado.empty:
            st.caption("Sin datos de tamaño de mercado <6 años todavía -añádelos en 'Objetivos y datos manuales'.")
        tabla = seguimiento.TABLAS[tipo](dealers, resumen_ajustado, objetivos, mercado, marca, agrupar, bloques, remarketing_disponible)
        st.dataframe(tabla, width="stretch", height=500, hide_index=True)

with tabs[-1]:
    st.caption("Maestro de concesionarios usado por la app (código, nombre, grupo propietario, marcas que vende).")
    st.dataframe(dealers, width="stretch", hide_index=True)

st.divider()
st.subheader("📥 Descargar todo el Seguimiento")
st.caption("Genera un único Excel con todas las pestañas de arriba (BMW y MINI), tal cual las ves aquí.")
if st.button("Generar Excel completo"):
    contenido = export_seguimiento.build_workbook(
        {
            (marca, tipo): seguimiento.TABLAS[tipo](
                dealers, resumen_ajustado, objetivos, mercado, marca,
                tipo == "grupo" or st.session_state.get(f"agrupar_{marca}_{tipo}", False),
                bloques, remarketing_disponible,
            )
            for marca, tipo in combinaciones
        },
        seguimiento.TITULOS,
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

