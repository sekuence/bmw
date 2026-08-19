"""Genera el HTML de las tablas-guía de bonificación (idénticas a las
del Excel original) para pintarlas en el Dashboard con
st.markdown(..., unsafe_allow_html=True)."""
import itertools

from . import bonus, theme

# Colores semánticos de las tablas originales (rojo/amarillo/verde =
# malo/medio/bueno). Son fijos, independientes del azul/naranja de marca.
ROJO = "#F4B6B6"
AMARILLO = "#FCE79E"
VERDE_CLARO = "#C7E5C4"
VERDE = "#8FCB86"


def _agrupar_fila(valores: list[int]) -> list[tuple[int, int]]:
    """[0,250,350,550] -> [(0,1),(250,1),(350,1),(550,1)];
    [250,350,550,550] -> [(250,1),(350,1),(550,2)] -para las celdas
    combinadas de la matriz, igual que en el Excel."""
    return [(valor, len(list(grupo))) for valor, grupo in itertools.groupby(valores)]


def _color_bono(valor: int, maximo: int) -> str:
    if valor == 0:
        return ROJO
    if valor < maximo * 0.5:
        return AMARILLO
    if valor < maximo:
        return VERDE_CLARO
    return VERDE


def _tabla_matriz(marca: str) -> str:
    matriz = bonus.MATRIZ_BONO[marca]
    etiquetas_y = bonus.ETIQUETAS_Y[marca]
    maximo = max(max(fila) for fila in matriz)
    color = theme.color_de(marca)

    filas_html = ""
    for etiqueta_x, fila in zip(bonus.ETIQUETAS_X, matriz):
        celdas = "".join(
            f"<td colspan='{span}' style='background:{_color_bono(valor, maximo)};"
            f"text-align:center;padding:6px;border:1px solid #ccc'>{valor} €</td>"
            for valor, span in _agrupar_fila(fila)
        )
        filas_html += f"<tr><td style='padding:6px;border:1px solid #ccc;font-weight:600'>{etiqueta_x}</td>{celdas}</tr>"

    cabecera_y = "".join(
        f"<th style='padding:6px;border:1px solid #ccc;background:#eee'>{e}</th>" for e in etiquetas_y
    )

    return f"""
    <table style='border-collapse:collapse;width:100%;font-size:0.85rem'>
      <tr>
        <th style='padding:6px;border:1px solid #ccc;background:{color};color:white'>OBJ RETAIL (x)</th>
        <th colspan='{len(etiquetas_y)}' style='padding:6px;border:1px solid #ccc;background:{color};color:white'>
          Ventas Retail Origen Remarketing (y)
        </th>
      </tr>
      <tr><th style='padding:6px;border:1px solid #ccc;background:#eee'></th>{cabecera_y}</tr>
      {filas_html}
    </table>
    """


def _tabla_bev(marca: str) -> str:
    color = theme.color_de(marca)
    filas = "".join(
        f"<td style='padding:6px;border:1px solid #ccc;text-align:center;"
        f"background:{AMARILLO if mult < max(m[2] for m in bonus.BANDAS_BEV_MULT[marca]) else VERDE}'>"
        f"{'≥' if hi is None else f'{lo*100:.0f}% ≤ x <'} {f'{lo*100:.0f}%' if hi is None else f'{hi*100:.0f}%'} → x{mult}</td>"
        for lo, hi, mult in bonus.BANDAS_BEV_MULT[marca]
    )
    return f"""
    <table style='border-collapse:collapse;width:100%;font-size:0.85rem'>
      <tr><th colspan='{len(bonus.BANDAS_BEV_MULT[marca])}' style='padding:6px;border:1px solid #ccc;background:{color};color:white'>
        Multiplicador por Ventas BEV</th></tr>
      <tr>{filas}</tr>
    </table>
    """


def _barra_umbral(etiqueta_baja: str, etiqueta_alta: str) -> str:
    return f"""
    <table style='border-collapse:collapse;width:100%;font-size:0.85rem;text-align:center'>
      <tr>
        <td style='padding:4px'>{etiqueta_baja}</td>
        <td style='padding:4px'>{etiqueta_alta}</td>
      </tr>
      <tr>
        <td style='padding:2px'><div style='height:8px;background:{ROJO};border-radius:4px'></div></td>
        <td style='padding:2px'><div style='height:8px;background:{VERDE};border-radius:4px'></div></td>
      </tr>
    </table>
    """


def render(marca: str) -> str:
    """HTML completo de la guía de bonificación de una marca."""
    return f"""
    <div style='border:1px solid #ccc;border-radius:8px;padding:14px;margin-bottom:14px'>
      <b>Porcentaje mínimo de penetración BPS / MN</b>
      {_barra_umbral(f"&lt; {bonus.UMBRAL_PENETRACION_BPS*100:.0f}%", f"≥ {bonus.UMBRAL_PENETRACION_BPS*100:.0f}%")}
    </div>
    <div style='border:1px solid #ccc;border-radius:8px;padding:14px;margin-bottom:14px'>
      <b>% Cumplimiento Objetivo Ventas Retail / Origen Remarketing</b><br><br>
      {_tabla_matriz(marca)}
    </div>
    <div style='border:1px solid #ccc;border-radius:8px;padding:14px;margin-bottom:14px'>
      {_tabla_bev(marca)}
    </div>
    <div style='border:1px solid #ccc;border-radius:8px;padding:14px'>
      <b>Mystery Shopping</b>
      {_barra_umbral(f"&lt; {bonus.UMBRAL_MYSTERY_SHOPPING:.0f}%", f"≥ {bonus.UMBRAL_MYSTERY_SHOPPING:.0f}%")}
    </div>
    """
