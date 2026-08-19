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

# --- Regla BYMYCAR / BMW DIRECTO y "Retail origen Remarketing" -------
#
# Pendiente de que la BBDD incorpore la columna "Canal Actual" (todavía
# no está en los archivos de ventas que hemos visto). Cuando exista, la
# app la usa automáticamente:
#
#   1) De las ventas de BYMYCAR MADRID, las que tengan Canal Actual
#      terminado en "_DIRECTO" se reasignan al concesionario ficticio
#      "BMW DIRECTO" (código 12345) -el resto se quedan en BYMYCAR-.
#   2) "Retail origen Remarketing" pasa a ser: todas las ventas Retail
#      CUYO Canal Actual no sea de tipo "_MOBILITY" ni "_LANDING" (antes
#      se usaba `Origen contiene "Remarketing"`, que se mantiene como
#      alternativa mientras no exista la columna Canal Actual).
#
# Los tres patrones de abajo son búsquedas "contiene" (no hace falta
# que coincidan exactas) porque aún no hemos visto valores reales de
# esta columna -ajusta estas constantes en cuanto lleguen los primeros
# datos reales si el texto no encaja.
COLUMNA_CANAL_ACTUAL = "Canal Actual"
PATRON_CANAL_DIRECTO = "DIRECTO"
PATRONES_CANAL_EXCLUIDOS_REMARKETING = ["MOBILITY", "LANDING"]

CONCESIONARIO_BYMYCAR = "BYMYCAR"  # texto a buscar en Concesión (case-insensitive)
CODIGO_BMW_DIRECTO = 12345
NOMBRE_BMW_DIRECTO = "BMW DIRECTO"
