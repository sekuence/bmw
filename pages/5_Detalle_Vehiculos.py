import streamlit as st

from src import config, detail

st.set_page_config(page_title="Detalle de vehículos", page_icon="🚗", layout="wide")

if not st.session_state.get("cargado"):
    st.warning("Primero sube el archivo de ventas en la página principal (Home).")
    st.page_link("app.py", label="⬅️ Ir a Home")
    st.stop()

ventas = st.session_state["ventas"]
dealers = st.session_state["dealers"]

st.title("🚗 Detalle de vehículos")
st.caption(
    "Aquí ves la BBDD tal cual, vehículo a vehículo -con todas las columnas del Excel "
    "original-, filtrando por lo que te interese. Es el mismo sitio al que te llevan los "
    "botones \"Ver detalle\" del Dashboard y del Ranking."
)

c1, c2, c3, c4 = st.columns(4)
with c1:
    concesionarios = ["(todos)"] + sorted(dealers["concesionario"].tolist())
    concesionario = st.selectbox("Concesión", concesionarios)
with c2:
    marca = st.selectbox("Marca", ["(todas)", "BMW", "MINI"])
with c3:
    meses_sel = st.multiselect("Mes", config.MESES)
with c4:
    metrica_label = st.selectbox("Métrica", ["(todas las ventas)"] + list(config.METRICAS_AJUSTABLES.values()))

codigo_dealer = None
if concesionario != "(todos)":
    codigo_dealer = int(dealers.loc[dealers["concesionario"] == concesionario, "codigo_dealer"].iloc[0])

metrica = None
if metrica_label != "(todas las ventas)":
    metrica = next(k for k, v in config.METRICAS_AJUSTABLES.items() if v == metrica_label)

filtrado = detail.filtrar(
    ventas,
    codigo_dealer=codigo_dealer,
    marca=None if marca == "(todas)" else marca,
    meses=meses_sel or None,
    metrica=metrica,
)

busqueda = st.text_input("Buscar (chasis, matrícula, modelo...)")
if busqueda:
    mask = filtrado.astype(str).apply(lambda col: col.str.contains(busqueda, case=False, na=False))
    filtrado = filtrado[mask.any(axis=1)]

st.caption(f"{len(filtrado):,} vehículos".replace(",", "."))
st.dataframe(filtrado, width="stretch", hide_index=True, height=600)

st.download_button(
    "📥 Descargar esta vista en CSV",
    data=filtrado.to_csv(index=False).encode("utf-8-sig"),
    file_name="detalle_vehiculos.csv",
    mime="text/csv",
)
