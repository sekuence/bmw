import pandas as pd
import streamlit as st

from src import config, storage

st.set_page_config(page_title="Objetivos y datos manuales", page_icon="🎯", layout="wide")

if not st.session_state.get("cargado"):
    st.warning("Primero sube el archivo de ventas en la página principal (Home).")
    st.page_link("app.py", label="⬅️ Ir a Home")
    st.stop()

dealers = st.session_state["dealers"]

st.title("🎯 Objetivos y datos manuales")
st.caption(
    "Estos datos no vienen en el archivo de ventas -alguien los pasa a mano cada mes o "
    "trimestre-. Se guardan en esta app y se reutilizan automáticamente en el Dashboard "
    "hasta que los cambies."
)


def _tabla_editable(
    tabla: str,
    marca: str,
    columnas: list[str],
    col_nombre: str,
    dealers_marca: pd.DataFrame,
    label_valor: str,
    extra_keys: dict | None = None,
):
    """extra_keys, p.ej. {'metrica': 'Retail'}, distingue registros que
    comparten tabla (objetivos de Retail vs de BEV)."""
    extra_keys = extra_keys or {}
    key_cols = ["codigo_dealer", "marca", *extra_keys.keys(), col_nombre]

    existentes = storage.read_table(tabla)
    if not existentes.empty:
        existentes = existentes[existentes["marca"] == marca]
        for k, v in extra_keys.items():
            existentes = existentes[existentes[k] == v]

    filas = []
    for _, d in dealers_marca.iterrows():
        fila = {"codigo_dealer": int(d["codigo_dealer"]), "concesionario": d["concesionario"]}
        for c in columnas:
            valor = None
            if not existentes.empty:
                match = existentes[(existentes["codigo_dealer"] == d["codigo_dealer"]) & (existentes[col_nombre] == c)]
                if not match.empty:
                    valor = float(match["valor"].iloc[0])
            fila[c] = valor
        filas.append(fila)
    base = pd.DataFrame(filas)

    editado = st.data_editor(
        base,
        column_config={
            "codigo_dealer": st.column_config.NumberColumn(disabled=True),
            "concesionario": st.column_config.TextColumn(disabled=True),
        },
        hide_index=True,
        width="stretch",
        key=f"editor_{tabla}_{marca}_{'_'.join(extra_keys.values())}",
    )

    if st.button(f"💾 Guardar {label_valor} ({marca})", key=f"guardar_{tabla}_{marca}_{'_'.join(extra_keys.values())}"):
        largo = editado.melt(id_vars=["codigo_dealer", "concesionario"], value_vars=columnas, var_name=col_nombre, value_name="valor")
        largo = largo.dropna(subset=["valor"])
        largo["marca"] = marca
        for k, v in extra_keys.items():
            largo[k] = v
        storage.save_dataframe(tabla, largo, key_cols=key_cols)
        st.success("Guardado.")


tab_retail, tab_bev, tab_mercado, tab_mys = st.tabs(
    ["Objetivos Retail", "Objetivos BEV", "Mercado <6 años", "Mystery Shopping"]
)

with tab_retail:
    marca = st.radio("Marca", ["BMW", "MINI"], horizontal=True, key="marca_retail")
    col = "vende_bmw" if marca == "BMW" else "vende_mini"
    _tabla_editable(
        "objetivos", marca, config.MESES, "mes", dealers[dealers[col] == "Si"],
        "objetivos de retail", extra_keys={"metrica": "Retail"},
    )

with tab_bev:
    marca = st.radio("Marca", ["BMW", "MINI"], horizontal=True, key="marca_bev")
    col = "vende_bmw" if marca == "BMW" else "vende_mini"
    _tabla_editable(
        "objetivos", marca, config.MESES, "mes", dealers[dealers[col] == "Si"],
        "objetivos de BEV", extra_keys={"metrica": "BEV"},
    )

with tab_mercado:
    marca = st.radio("Marca", ["BMW", "MINI"], horizontal=True, key="marca_mercado")
    col = "vende_bmw" if marca == "BMW" else "vende_mini"
    _tabla_editable(
        "mercado_menos_6_anos", marca, config.MESES, "mes", dealers[dealers[col] == "Si"],
        "tamaño de mercado <6 años",
    )

with tab_mys:
    marca = st.radio("Marca", ["BMW", "MINI"], horizontal=True, key="marca_mys")
    col = "vende_bmw" if marca == "BMW" else "vende_mini"
    _tabla_editable(
        "mystery_shopping", marca, ["S1", "S2"], "semestre", dealers[dealers[col] == "Si"],
        "mystery shopping",
    )
