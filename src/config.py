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

# Reglas de elegibilidad BPS / MINI NEXT (pestaña "Instrucciones" del Excel
# original): un vehículo marcado BPS/NEXT sólo cuenta si además lleva
# matriculado >= 180 días y tiene >= 6.000 km. Se puede desactivar desde la UI.
BPS_MIN_DIAS_MATRICULADO = 180
BPS_MIN_KM = 6000

# Nombre de la hoja de origen dentro del archivo de ventas.
HOJA_VENTAS = "BBDD"

METRICAS = ["Retail", "BPS/MN", "Remarketing", "BEV"]
