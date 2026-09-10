"""Guía de bonificación tal cual las tablas de referencia del Excel
original ('Dealer Dashboard'): mínimos de penetración BPS/MN y Mystery
Shopping, matriz de bonificación (% cumplimiento objetivo retail x %
Retail origen Remarketing) y multiplicador por % BEV.
"""
import math

UMBRAL_PENETRACION_BPS = 0.80
UMBRAL_MYSTERY_SHOPPING = 90.0  # Mystery Shopping se introduce como puntuación 0-100

# % cumplimiento del objetivo de ventas Retail (eje X de la matriz de bonificación).
BANDAS_X = [(0.90, 1.00), (1.00, 1.10), (1.10, None)]
ETIQUETAS_X = ["90% ≤ x < 100%", "100% ≤ x < 110%", "x ≥ 110%"]

# % Retail origen Remarketing (eje Y), distinto por marca.
BANDAS_Y = {
    "BMW": [(0.18, 0.22), (0.22, 0.27), (0.27, 0.32), (0.32, None)],
    "MINI": [(0.15, 0.20), (0.20, 0.25), (0.25, 0.30), (0.30, None)],
}
ETIQUETAS_Y = {
    "BMW": ["18% ≤ Y < 22%", "22% ≤ Y < 27%", "27% ≤ Y < 32%", "Y ≥ 32%"],
    "MINI": ["15% ≤ Y < 20%", "20% ≤ Y < 25%", "25% ≤ Y < 30%", "Y ≥ 30%"],
}

# Importe (€) según banda X (fila) y banda Y (columna).
MATRIZ_BONO = {
    "BMW": [
        [0, 250, 350, 550],
        [250, 350, 550, 550],
        [350, 550, 550, 550],
    ],
    "MINI": [
        [0, 150, 200, 350],
        [150, 200, 350, 350],
        [200, 350, 350, 350],
    ],
}

# Multiplicador por % de ventas BEV sobre Retail.
BANDAS_BEV_MULT = {
    "BMW": [(0.06, 0.11, 1.05), (0.11, None, 1.10)],
    "MINI": [(0.10, 0.15, 1.05), (0.15, None, 1.25)],
}


def redondear_pct(valor: float) -> float:
    """Redondea a la unidad porcentual más cercana, con 0,5 hacia arriba
    -para que un 89,91% cuente como 90%-. No se usa round() de Python
    porque redondea los .5 al par más cercano ("banker's rounding"), no
    siempre hacia arriba."""
    return math.floor(valor * 100 + 0.5) / 100


def _indice_banda(valor: float, bandas: list[tuple[float, float | None]]) -> int | None:
    for i, (lo, hi) in enumerate(bandas):
        if valor >= lo and (hi is None or valor < hi):
            return i
    return None


def multiplicador_bev(marca: str, pct_bev: float | None) -> float:
    if pct_bev is None:
        return 1.0
    for lo, hi, mult in BANDAS_BEV_MULT[marca]:
        if pct_bev >= lo and (hi is None or pct_bev < hi):
            return mult
    return 1.0


def calcular(marca: str, pct_cumplimiento_retail: float | None, pct_remarketing: float | None, pct_bev: float | None) -> dict:
    """Bonificación estimada = importe de la matriz x multiplicador BEV.
    Devuelve base=None cuando no hay objetivo o no hay ventas con las que
    calcular el % (no se puede ubicar en la matriz).

    SÓLO el % de cumplimiento Retail (eje X) se redondea a la unidad
    porcentual más cercana -89,91% cuenta como 90% para decidir si el
    concesionario llega al mínimo y puede cobrar-. El % Remarketing
    (eje Y) y el % BEV se comparan EXACTOS, sin redondear -un 26,6% de
    remarketing NO llega al tramo del 27%, se queda en el anterior-.
    `redondeo_aplicado` avisa cuando ese redondeo del eje X cambia el
    resultado (p.ej. hace que SÍ entre en la matriz cuando el % exacto
    no llegaba), para identificarlo fácilmente."""
    if pct_cumplimiento_retail is None or pct_remarketing is None:
        return {"base": None, "multiplicador": 1.0, "total": None, "redondeo_aplicado": False}

    pct_x_redondeado = redondear_pct(pct_cumplimiento_retail)
    ix = _indice_banda(pct_x_redondeado, BANDAS_X)
    iy = _indice_banda(pct_remarketing, BANDAS_Y[marca])
    base = MATRIZ_BONO[marca][ix][iy] if ix is not None and iy is not None else 0
    mult = multiplicador_bev(marca, pct_bev)

    redondeo_aplicado = ix != _indice_banda(pct_cumplimiento_retail, BANDAS_X)

    return {
        "base": base,
        "multiplicador": mult,
        "total": round(base * mult, 2),
        "redondeo_aplicado": redondeo_aplicado,
    }


def cumple_penetracion_bps(pct_bps: float | None) -> bool | None:
    return None if pct_bps is None else pct_bps >= UMBRAL_PENETRACION_BPS


def cumple_mystery_shopping(mystery: float | None) -> bool | None:
    return None if mystery is None else mystery >= UMBRAL_MYSTERY_SHOPPING
