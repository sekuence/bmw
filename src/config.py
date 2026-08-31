"""Constantes de negocio compartidas por toda la app.

Estos valores replican los que se usaban en el Excel original
(pestaña "Dealer Dashboard" y "Instrucciones"). Si cambian las reglas
de negocio, este es el único sitio que hay que tocar.
"""

MESES = [
    "ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO",
    "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE",
]

MESES_S1 = MESES[0:6]
MESES_S2 = MESES[6:12]

PERIODOS = [
    *MESES,
    "TRIMESTRE 1", "TRIMESTRE 2", "TRIMESTRE 3", "TRIMESTRE 4",
    "SEMESTRE 1", "SEMESTRE 2",
    "ACUMULADO MES", "ACUMULADO MES 2S",
    "ANUAL",
]

TRIMESTRES = {
    "TRIMESTRE 1": MESES[0:3],
    "TRIMESTRE 2": MESES[3:6],
    "TRIMESTRE 3": MESES[6:9],
    "TRIMESTRE 4": MESES[9:12],
}

MARCAS = ["BMW", "MINI"]

# Nombre de la hoja de origen dentro del archivo de ventas.
HOJA_VENTAS = "BBDD"

METRICAS = ["Retail", "BPS/MN", "Remarketing", "BEV"]

# Métricas calculadas desde la BBDD que se pueden corregir a mano
# (página "Objetivos y datos manuales" > pestaña "Ajustes manuales").
METRICAS_AJUSTABLES = {
    "retail": "Ventas Retail",
    "bps": "BPS / MN",
    "remarketing": "Retail origen Remarketing",
    "bev": "BEV",
    "wholesale_uc": "Wholesale UC",
    "wholesale_yuc": "Wholesale YUC",
    "ventas_totales": "Ventas Totales (Retail + Wholesale)",
}

# Columna de negocio (flag es_*) que identifica los vehículos de cada
# métrica, para poder filtrar el detalle a nivel de chasis. None =
# no se filtra por Retail/Wholesale (ventas totales = todo).
FLAG_DE_METRICA = {
    "retail": "es_retail",
    "bps": "es_bps",
    "remarketing": "es_remarketing",
    "bev": "es_bev",
    "wholesale_uc": None,  # además exige yuc_uc == "UC" y es_wholesale
    "wholesale_yuc": None,  # además exige yuc_uc == "YUC" y es_wholesale
    "ventas_totales": None,
}

# --- Regla BYMYCAR "Directo" y "Retail origen Remarketing" -----------
#
# Pendiente de que la BBDD incorpore la columna "Canal Actual" (todavía
# no está en los archivos de ventas que hemos visto, pero ya vimos un
# ejemplo real -ventas_origen_remarketing_07.xlsx, hoja "2026", columna
# "CANAL"-, de donde salen los valores de abajo). Cuando exista la
# columna en la BBDD, la app la usa automáticamente:
#
#   1) De las ventas de BYMYCAR, las que tengan Canal Actual con
#      "DIRECTO" se cuentan aparte, con la etiqueta "BMW DIRECTO"
#      -NO existe un concesionario con ese nombre ni con código propio
#      en la BBDD: sigue siendo BYMYCAR, sólo que esas ventas no entran
#      en su Retail/BPS/BEV normal, se muestran en un apartado aparte-.
#   2) "Retail origen Remarketing" = ventas Retail cuyo Canal Actual:
#        a) no esté vacío ni sea de error (#N/A, #N/D, "-", etc.),
#        b) no sea de tipo MOBILITY / LANDING / DIRECTO / DIRECT_SALES,
#        c) Y, si existe la columna "V o F Formulada" (mismo grupo
#           comprador/vendedor -pendiente de que la incorpore la
#           BBDD-), que valga Verdadero -si el comprador es de otro
#           grupo, no cuenta como remarketing aunque el canal sea
#           válido-.
#
# Valores reales de Canal Actual vistos (columna CANAL del ejemplo):
# rmk_auction_global, rmk_cars_campaigns, rmk_car_mobility (excluido),
# rmk_cars, rmk_cars_retail_directo (excluido), rmk_cars_landing
# (excluido), rmk_Auction_Paneuropean, rmk_cars_outlet, rmk_auction,
# rmk_direct_sales (excluido). Ajusta estas constantes en cuanto la
# BBDD real traiga esta columna si el texto no encaja exactamente.
COLUMNA_CANAL_ACTUAL = "Canal Actual"
PATRON_CANAL_DIRECTO = "DIRECTO"
PATRONES_CANAL_EXCLUIDOS_REMARKETING = ["MOBILITY", "LANDING", "DIRECTO", "DIRECT_SALES", "DIRECT SALES"]
VALORES_CANAL_VACIO = ["", "NAN", "NONE", "#N/A", "#N/D", "-", "N/A", "N/D"]

# Columna (pendiente, aún no existe en la BBDD) que indica si el
# concesionario comprador y el vendedor pertenecen al mismo grupo
# propietario -viene ya calculada, no hace falta recalcularla-.
# Valores vistos: "VERDADERO" / "FALSO" (booleano en español).
COLUMNA_MISMO_GRUPO = "V o F Formulada"
VALORES_MISMO_GRUPO_TRUE = ["VERDADERO", "TRUE", "SI", "SÍ", "1"]

CONCESIONARIO_BYMYCAR = "BYMYCAR"  # texto a buscar en Concesión (case-insensitive)
ETIQUETA_BYMYCAR_DIRECTO = "BMW DIRECTO"
