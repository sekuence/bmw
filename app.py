"""Punto de entrada de la app. Aquí se sube el archivo de ventas (BBDD)
y se deja preparado en memoria para el resto de páginas (Dashboard,
Objetivos, Ranking, Exportar)."""
from pathlib import Path

import pandas as pd
import streamlit as st

from src import config, dealers as dealers_mod, ingest, metrics

st.set_page_config(page_title="Seguimiento UC Retail & Wholesale", page_icon="📊", layout="wide")

CACHE_PATH = Path(__file__).resolve().parent / "data" / "ventas_cache.parquet"


def _guardar_en_sesion(ventas_limpias: pd.DataFrame):
    dealers = dealers_mod.load_dealers()
    dealers = dealers_mod.merge_new_dealers(dealers, ventas_limpias)
    resumen = metrics.build_monthly_summary(ventas_limpias)

    st.session_state["ventas"] = ventas_limpias
    st.session_state["dealers"] = dealers
    st.session_state["resumen"] = resumen
    st.session_state["cargado"] = True

    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    ventas_limpias.to_parquet(CACHE_PATH, index=False)


st.title("📊 Seguimiento UC Retail & Wholesale")
st.caption(
    "Sube el archivo de ventas (hoja **BBDD**) y el resto de la app -Dashboard por "
    "concesionario, Ranking y Exportar a Excel- se calcula solo, sin tocar nada a mano."
)

with st.sidebar:
    st.header("1. Cargar archivo de ventas")
    archivo = st.file_uploader("Archivo de ventas (.xlsx)", type=["xlsx"])

    if archivo is not None:
        try:
            raw = ingest.read_bbdd(archivo)
            ventas_limpias = ingest.clean_ventas(raw)
        except ingest.VentasFileError as exc:
            st.error(str(exc))
        else:
            _guardar_en_sesion(ventas_limpias)
            st.success(f"Cargadas {len(ventas_limpias):,} filas de venta.".replace(",", "."))
    elif CACHE_PATH.exists() and "cargado" not in st.session_state:
        if st.button("Usar el último archivo cargado en esta app"):
            ventas_limpias = pd.read_parquet(CACHE_PATH)
            _guardar_en_sesion(ventas_limpias)
            st.rerun()

if not st.session_state.get("cargado"):
    st.info("⬅️ Sube el archivo de ventas desde el panel de la izquierda para empezar.")
    st.markdown(
        """
        **¿Qué necesita este archivo?**
        - Debe tener una hoja llamada **`BBDD`** (como en `Cierre_ventas_YTD`).
        - Cada fila = un vehículo vendido, con columnas como `Código INT` (concesionario),
          `Marca`, `Fecha venta mes`, `Motivo venta`, `BPS / NEXT`, `Origen`, `COMB`, `YUC/UC`.

        **¿Qué se calcula automáticamente?**
        Ventas retail, BPS/MN, remarketing y BEV por concesionario y mes.

        **¿Qué se sigue introduciendo a mano?**
        Los objetivos, el mystery shopping y el tamaño de mercado (&lt;6 años) -esos datos no
        vienen en el archivo de ventas-. Se editan en la página **Objetivos y datos manuales**
        y quedan guardados para los próximos meses.
        """
    )
else:
    ventas = st.session_state["ventas"]
    dealers = st.session_state["dealers"]
    resumen = st.session_state["resumen"]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Vehículos vendidos", f"{len(ventas):,}".replace(",", "."))
    c2.metric("Concesionarios con ventas", ventas["codigo_dealer"].nunique())
    meses_presentes = sorted(ventas["mes"].unique(), key=config.MESES.index) if len(ventas) else []
    c3.metric("Meses cubiertos", len(meses_presentes))
    c4.metric("Marcas", ", ".join(sorted(ventas["marca"].unique())))

    if meses_presentes:
        st.caption("Meses detectados en el archivo: " + ", ".join(meses_presentes))

    st.divider()
    st.subheader("Resumen por marca")
    st.dataframe(
        ventas.groupby("marca").agg(
            retail=("es_retail", "sum"),
            bps=("es_bps", "sum"),
            remarketing=("es_remarketing", "sum"),
            bev=("es_bev", "sum"),
            wholesale=("es_wholesale", "sum"),
        ),
        width="stretch",
    )

    st.divider()
    st.page_link("pages/1_Dashboard_Concesionario.py", label="➡️ Ir al Dashboard por concesionario", icon="📈")
    st.page_link("pages/2_Objetivos_y_Datos_Manuales.py", label="➡️ Editar objetivos y datos manuales", icon="🎯")
    st.page_link("pages/3_Ranking.py", label="➡️ Ver ranking de concesionarios", icon="🏆")
    st.page_link("pages/4_Exportar.py", label="➡️ Exportar a Excel", icon="⬇️")
    st.page_link("pages/5_Detalle_Vehiculos.py", label="➡️ Ver detalle de vehículos (como el Excel)", icon="🚗")
    st.page_link("pages/6_Detalle_por_Pestana.py", label="➡️ Ver desglose por pestaña", icon="🗂️")
