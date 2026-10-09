"""Capa de 'vistas' para la versión HTML local (sin Streamlit): cada
función de aquí hace lo mismo que una página de Streamlit -junta lo
que ya calcula src/- pero devuelve estructuras JSON-serializables
(dict/list) en vez de pintar widgets, para que el JavaScript de
local.html las convierta en HTML. Mantiene todo el estado en memoria
(equivalente a st.session_state) en el dict ESTADO.
"""
import io
import json

import pandas as pd

from src import (
    bonus,
    config,
    dashboard,
    dealers as dealers_mod,
    detail,
    export,
    export_plantilla,
    export_seguimiento,
    guia,
    importer,
    ingest,
    metrics,
    seguimiento,
    storage,
    theme,
)

ESTADO: dict = {"cargado": False}

PERIODOS_COMPLETO = (
    config.MESES
    + ["TRIMESTRE 1", "TRIMESTRE 2", "TRIMESTRE 3", "TRIMESTRE 4",
       "SEMESTRE 1", "SEMESTRE 2", "ACUMULADO MES", "ACUMULADO MES 2S", "ANUAL"]
)


def _limpio(obj):
    """Convierte NaN/NaT/Timestamp/numpy types a algo JSON-serializable,
    recursivamente, para poder devolver cualquier estructura a JS."""
    if isinstance(obj, pd.DataFrame):
        return json.loads(obj.to_json(orient="records", date_format="iso"))
    if isinstance(obj, pd.Series):
        return _limpio(obj.to_dict())
    if isinstance(obj, dict):
        return {str(k): _limpio(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_limpio(v) for v in obj]
    if isinstance(obj, float) and pd.isna(obj):
        return None
    if pd.isna(obj) if not isinstance(obj, (list, dict)) else False:
        return None
    if hasattr(obj, "item"):  # numpy scalar
        return obj.item()
    return obj


def _tabla_multiindex(df: pd.DataFrame) -> dict:
    """Serializa un DataFrame con columnas MultiIndex (nivel0=periodo,
    nivel1=submétrica) a {"columnas": [[nivel0, nivel1], ...], "filas": [[...], ...]}."""
    columnas = [[str(a) if a else "", str(b)] for a, b in df.columns]
    filas = []
    for _, fila in df.iterrows():
        filas.append([None if pd.isna(v) else (v.item() if hasattr(v, "item") else v) for v in fila])
    return {"columnas": columnas, "filas": filas}


# ---------------------------------------------------------------------
# Home: cargar archivo de ventas
# ---------------------------------------------------------------------

def cargar_archivo(nombre: str, contenido: bytes) -> dict:
    try:
        raw = ingest.read_bbdd(io.BytesIO(bytes(contenido)))
        ventas = ingest.clean_ventas(raw)
    except ingest.VentasFileError as exc:
        return {"ok": False, "error": str(exc)}

    dealers = dealers_mod.load_dealers()
    dealers = dealers_mod.merge_new_dealers(dealers, ventas)
    resumen = metrics.build_monthly_summary(ventas)

    ESTADO["ventas"] = ventas
    ESTADO["dealers"] = dealers
    ESTADO["resumen"] = resumen
    ESTADO["cargado"] = True
    ESTADO["remarketing_disponible"] = ingest.remarketing_disponible(ventas)
    ESTADO["nombre_archivo"] = nombre

    return {"ok": True, **resumen_home()}


def resumen_home() -> dict:
    ventas = ESTADO["ventas"]
    meses_presentes = sorted(ventas["mes"].unique(), key=config.MESES.index) if len(ventas) else []
    resumen_marca = ventas.groupby("marca").agg(
        retail=("es_retail", "sum"),
        bps=("es_bps", "sum"),
        remarketing=("es_remarketing", "sum"),
        bev=("es_bev", "sum"),
        wholesale=("es_wholesale", "sum"),
    ) if len(ventas) else pd.DataFrame()
    return {
        "archivo": ESTADO.get("nombre_archivo"),
        "vehiculos": len(ventas),
        "concesionarios": int(ventas["codigo_dealer"].nunique()) if len(ventas) else 0,
        "meses": meses_presentes,
        "marcas": sorted(ventas["marca"].unique()) if len(ventas) else [],
        "remarketing_disponible": ESTADO["remarketing_disponible"],
        "por_marca": _limpio(resumen_marca.reset_index()) if len(resumen_marca) else [],
        "colores": {"BMW": theme.COLOR_BMW, "MINI": theme.COLOR_MINI},
    }


# ---------------------------------------------------------------------
# Dashboard por concesionario
# ---------------------------------------------------------------------

def dashboard_opciones() -> dict:
    dealers = ESTADO["dealers"]
    return {
        "concesionarios": sorted(dealers["concesionario"].tolist()),
        "periodos": PERIODOS_COMPLETO,
        "meses": config.MESES,
        "meses_s2": config.MESES_S2,
    }


def dashboard_datos(concesionario: str, periodo: str, mes_referencia: str | None) -> dict:
    dealers = ESTADO["dealers"]
    resumen = ESTADO["resumen"]
    ventas = ESTADO["ventas"]
    remarketing_disponible = ESTADO["remarketing_disponible"]

    fila = dealers[dealers["concesionario"] == concesionario].iloc[0]
    codigo_dealer = int(fila["codigo_dealer"])
    marcas_disponibles = [m for m, col in (("BMW", "vende_bmw"), ("MINI", "vende_mini")) if fila[col] == "Si"]
    es_bymycar = "BYMYCAR" in concesionario.upper()

    kpis = {}
    evoluciones = {}
    directos = {}
    for marca in marcas_disponibles:
        k = dashboard.kpi_bloque(resumen, codigo_dealer, marca, periodo, mes_referencia, remarketing_disponible)
        k["guia_html"] = guia.render(marca)
        kpis[marca] = _limpio(k)
        evol = dashboard.evolucion_mensual(resumen, codigo_dealer, marca, remarketing_disponible)
        evoluciones[marca] = {
            "meses": list(evol.index.astype(str)),
            "series": {col: _limpio(evol[col].tolist()) for col in evol.columns},
        } if not evol.empty else {"meses": [], "series": {}}
        if es_bymycar:
            directos[marca] = _limpio(metrics.kpis_bymycar_directo(ventas, marca, periodo, mes_referencia))

    return {
        "codigo_dealer": codigo_dealer,
        "grupo_propietario": fila["grupo_propietario"],
        "marcas_disponibles": marcas_disponibles,
        "es_bymycar": es_bymycar,
        "remarketing_disponible": remarketing_disponible,
        "kpis": kpis,
        "evoluciones": evoluciones,
        "directos": directos,
        "colores": {"BMW": theme.COLOR_BMW, "MINI": theme.COLOR_MINI},
    }


def dashboard_detalle(concesionario: str, marca: str, meses: list[str], metrica: str, solo_directo: bool) -> dict:
    dealers = ESTADO["dealers"]
    ventas = ESTADO["ventas"]
    codigo_dealer = int(dealers.loc[dealers["concesionario"] == concesionario, "codigo_dealer"].iloc[0])
    filas = detail.filtrar(ventas, codigo_dealer=codigo_dealer, marca=marca, meses=meses, metrica=metrica, solo_bymycar_directo=solo_directo)
    return _tabla_registros(filas)


def _tabla_registros(df: pd.DataFrame) -> dict:
    return {"columnas": [str(c) for c in df.columns], "filas": _limpio(df)}


# ---------------------------------------------------------------------
# Objetivos y datos manuales
# ---------------------------------------------------------------------

def objetivos_tabla(tabla: str, marca: str, columnas: list[str], col_nombre: str, extra_keys: dict | None = None) -> dict:
    extra_keys = extra_keys or {}
    dealers = ESTADO["dealers"]
    col = "vende_bmw" if marca == "BMW" else "vende_mini"
    dealers_marca = dealers[dealers[col] == "Si"]

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
    return {"columnas": columnas, "col_nombre": col_nombre, "filas": filas}


def objetivos_guardar(tabla: str, marca: str, columnas: list[str], col_nombre: str, filas: list[dict], extra_keys: dict | None = None) -> dict:
    extra_keys = extra_keys or {}
    key_cols = ["codigo_dealer", "marca", *extra_keys.keys(), col_nombre]
    df = pd.DataFrame(filas)
    largo = df.melt(id_vars=["codigo_dealer", "concesionario"], value_vars=columnas, var_name=col_nombre, value_name="valor")
    largo = largo.dropna(subset=["valor"])
    largo["marca"] = marca
    for k, v in extra_keys.items():
        largo[k] = v
    storage.save_dataframe(tabla, largo, key_cols=key_cols)
    return {"ok": True}


def objetivos_ajuste_calculado(marca: str, metrica: str) -> dict:
    dealers = ESTADO["dealers"]
    resumen = ESTADO["resumen"]
    col = "vende_bmw" if marca == "BMW" else "vende_mini"
    dealers_marca = dealers[dealers[col] == "Si"]
    if resumen is None or resumen.empty:
        return {"columnas": [], "filas": []}
    calculado = resumen[resumen["marca"] == marca].pivot_table(
        index="codigo_dealer", columns="mes", values=metrica, fill_value=0
    ).reindex(columns=config.MESES, fill_value=0)
    calculado = calculado.merge(dealers_marca[["codigo_dealer", "concesionario"]], on="codigo_dealer", how="right").fillna(0)
    calculado = calculado.set_index("concesionario")[config.MESES].reset_index()
    return _tabla_registros(calculado)


def importar_seguimiento(contenido: bytes) -> dict:
    try:
        importado = importer.importar_todo(io.BytesIO(bytes(contenido)))
    except importer.SeguimientoFileError as exc:
        return {"ok": False, "error": str(exc)}
    ESTADO["_import_objetivos"] = importado["objetivos"]
    ESTADO["_import_mercado"] = importado["mercado"]
    ESTADO["_import_mys"] = importado["mystery_shopping"]
    resumen_counts = {}
    if not importado["objetivos"].empty:
        resumen_counts["objetivos"] = _limpio(importado["objetivos"].groupby(["marca", "metrica"]).size().reset_index(name="n"))
    if not importado["mercado"].empty:
        resumen_counts["mercado"] = _limpio(importado["mercado"].groupby(["marca"]).size().reset_index(name="n"))
    if not importado["mystery_shopping"].empty:
        resumen_counts["mystery_shopping"] = _limpio(importado["mystery_shopping"].groupby(["marca", "semestre"]).size().reset_index(name="n"))
    return {"ok": True, "resumen": resumen_counts}


def importar_guardar() -> dict:
    objetivos = ESTADO.pop("_import_objetivos", pd.DataFrame())
    mercado = ESTADO.pop("_import_mercado", pd.DataFrame())
    mys = ESTADO.pop("_import_mys", pd.DataFrame())
    if not objetivos.empty:
        storage.save_dataframe("objetivos", objetivos, key_cols=["codigo_dealer", "marca", "metrica", "mes"])
    if not mercado.empty:
        storage.save_dataframe("mercado_menos_6_anos", mercado, key_cols=["codigo_dealer", "marca", "mes"])
    if not mys.empty:
        storage.save_dataframe("mystery_shopping", mys, key_cols=["codigo_dealer", "marca", "semestre"])
    return {"ok": True}


# ---------------------------------------------------------------------
# Ranking
# ---------------------------------------------------------------------

def ranking_tabla(marca: str, periodo: str, mes_referencia: str | None) -> dict:
    dealers = ESTADO["dealers"]
    resumen = ESTADO["resumen"]
    tabla = metrics.ranking_periodo(resumen, dealers, marca, periodo, mes_referencia)
    return _tabla_registros(tabla)


def ranking_detalle(codigo_dealer: int, marca: str, periodo: str, mes_referencia: str | None, metrica: str) -> dict:
    ventas = ESTADO["ventas"]
    meses = metrics.meses_de_periodo(periodo, mes_referencia)
    filas = detail.filtrar(ventas, codigo_dealer=codigo_dealer, marca=marca, meses=meses, metrica=metrica)
    return _tabla_registros(filas)


# ---------------------------------------------------------------------
# Exportar (resumen tipo Dealer Dashboard)
# ---------------------------------------------------------------------

def exportar_generar(marca: str, periodo: str, mes_referencia: str | None) -> bytes:
    dealers = ESTADO["dealers"]
    resumen = ESTADO["resumen"]
    return export.build_workbook(resumen, dealers, marca, periodo, mes_referencia)


# ---------------------------------------------------------------------
# Detalle de vehículos
# ---------------------------------------------------------------------

def detalle_vehiculos(concesionario: str | None, marca: str | None, meses: list[str], metrica: str | None, busqueda: str) -> dict:
    dealers = ESTADO["dealers"]
    ventas = ESTADO["ventas"]
    codigo_dealer = None
    if concesionario and concesionario != "(todos)":
        codigo_dealer = int(dealers.loc[dealers["concesionario"] == concesionario, "codigo_dealer"].iloc[0])
    filtrado = detail.filtrar(
        ventas, codigo_dealer=codigo_dealer, marca=marca if marca and marca != "(todas)" else None,
        meses=meses or None, metrica=metrica if metrica and metrica != "(todas las ventas)" else None,
    )
    if busqueda:
        mask = filtrado.astype(str).apply(lambda col: col.str.contains(busqueda, case=False, na=False))
        filtrado = filtrado[mask.any(axis=1)]
    ESTADO["_detalle_vehiculos_actual"] = filtrado
    return _tabla_registros(filtrado)


def detalle_vehiculos_excel() -> bytes:
    filtrado = ESTADO.get("_detalle_vehiculos_actual", pd.DataFrame())
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as xw:
        filtrado.to_excel(xw, sheet_name="Detalle", index=False)
    return buf.getvalue()


# ---------------------------------------------------------------------
# Seguimiento UC Retail & Wholesale
# ---------------------------------------------------------------------

def seguimiento_preparar(mes_acumulado: str) -> dict:
    resumen = ESTADO["resumen"]
    ventas = ESTADO["ventas"]
    resumen_ajustado = seguimiento.resumen_con_directo(resumen, ventas)
    ESTADO["_seguimiento_resumen_ajustado"] = resumen_ajustado
    ESTADO["_seguimiento_bloques"] = seguimiento.bloques_periodo(mes_acumulado)
    meses_con_datos = sorted(resumen["mes"].unique(), key=config.MESES.index) if not resumen.empty else []
    return {
        "meses": config.MESES,
        "mes_por_defecto": meses_con_datos[-1] if meses_con_datos else config.MESES[0],
        "ordenes_tipos": seguimiento.ORDEN_TIPOS,
        "titulos": {t: {"BMW": seguimiento.TITULOS[t]("BMW"), "MINI": seguimiento.TITULOS[t]("MINI")} for t in seguimiento.ORDEN_TIPOS},
    }


def seguimiento_tabla(marca: str, tipo: str, agrupar: bool) -> dict:
    dealers = ESTADO["dealers"]
    resumen_ajustado = ESTADO["_seguimiento_resumen_ajustado"]
    bloques = ESTADO["_seguimiento_bloques"]
    objetivos = storage.read_table("objetivos")
    mercado = storage.read_table("mercado_menos_6_anos")
    remarketing_disponible = ESTADO["remarketing_disponible"]
    tabla = seguimiento.TABLAS[tipo](dealers, resumen_ajustado, objetivos, mercado, marca, agrupar, bloques, remarketing_disponible)
    return _tabla_multiindex(tabla)


def seguimiento_maestro() -> dict:
    return _tabla_registros(ESTADO["dealers"])


def seguimiento_exportar_completo(agrupados: dict) -> bytes:
    """agrupados: {"BMW_simple": bool, ...} -si cada combinación se ve agrupada por Grupo Propietario-."""
    dealers = ESTADO["dealers"]
    resumen_ajustado = ESTADO["_seguimiento_resumen_ajustado"]
    bloques = ESTADO["_seguimiento_bloques"]
    objetivos = storage.read_table("objetivos")
    mercado = storage.read_table("mercado_menos_6_anos")
    remarketing_disponible = ESTADO["remarketing_disponible"]
    combinaciones = [(marca, tipo) for marca in ("BMW", "MINI") for tipo in seguimiento.ORDEN_TIPOS]
    tablas = {}
    for marca, tipo in combinaciones:
        agrupar = tipo == "grupo" or bool(agrupados.get(f"{marca}_{tipo}", False))
        tablas[(marca, tipo)] = seguimiento.TABLAS[tipo](dealers, resumen_ajustado, objetivos, mercado, marca, agrupar, bloques, remarketing_disponible)
    return export_seguimiento.build_workbook(tablas, seguimiento.TITULOS, dealers)


def seguimiento_plantilla_disponible() -> bool:
    return export_plantilla.plantilla_disponible()


def seguimiento_exportar_plantilla(mes_referencia: str) -> bytes:
    dealers = ESTADO["dealers"]
    resumen_ajustado = ESTADO["_seguimiento_resumen_ajustado"]
    remarketing_disponible = ESTADO["remarketing_disponible"]
    return export_plantilla.rellenar_plantilla(resumen_ajustado, dealers, remarketing_disponible, mes_referencia)
