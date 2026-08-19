"""Importa los objetivos (columnas OBJ / Objetivo) que ya existen en el
Excel de seguimiento original (`SEGUIMIENTO UC RETAIL & WHOLESALE`),
para no tener que volver a teclearlos a mano concesionario por
concesionario. Sólo lee columnas -no fórmulas ni vínculos externos-,
así que no importa que ese archivo enlace a otros ficheros que no
tenemos."""
import openpyxl
import pandas as pd

from . import config

# (hoja, columna de inicio del primer mes, ancho de cada bloque mensual).
# El primer valor de cada bloque mensual es siempre el objetivo (OBJ /
# Objetivo). Los anchos de bloque están sacados de las fórmulas de la
# pestaña "Dealer Dashboard" del propio Excel original.
_HOJAS_OBJETIVO = {
    ("BMW", "Retail"): ("UC BMW 2026 BPS", 6, 6),
    ("MINI", "Retail"): ("UC MINI 2026 MINI NEXT", 6, 7),
    ("BMW", "BEV"): ("BEV BMW 2026", 6, 3),
    ("MINI", "BEV"): ("BEV MINI 2026", 6, 3),
}


class SeguimientoFileError(ValueError):
    pass


def _leer_hoja_objetivos(wb, hoja: str, col_inicio: int, ancho_bloque: int, marca: str, metrica: str) -> pd.DataFrame:
    if hoja not in wb.sheetnames:
        return pd.DataFrame(columns=["codigo_dealer", "marca", "metrica", "mes", "valor"])

    ws = wb[hoja]
    filas = []
    for fila in ws.iter_rows(min_row=7, max_row=ws.max_row, max_col=col_inicio + 12 * ancho_bloque):
        codigo_dealer = fila[1].value  # columna B
        if not isinstance(codigo_dealer, int):
            continue
        for i, mes in enumerate(config.MESES):
            col = col_inicio + i * ancho_bloque
            if col > len(fila):
                break
            valor = fila[col - 1].value
            if isinstance(valor, (int, float)):
                filas.append({"codigo_dealer": codigo_dealer, "marca": marca, "metrica": metrica, "mes": mes, "valor": float(valor)})
    return pd.DataFrame(filas)


def importar_objetivos(file_obj) -> pd.DataFrame:
    """Lee el Excel de seguimiento original y devuelve un DataFrame largo
    (codigo_dealer, marca, metrica, mes, valor) con todos los objetivos
    encontrados, listo para guardar con storage.save_dataframe."""
    try:
        wb = openpyxl.load_workbook(file_obj, data_only=True, read_only=True)
    except Exception as exc:  # noqa: BLE001
        raise SeguimientoFileError(f"No se pudo abrir el archivo: {exc}") from exc

    partes = [
        _leer_hoja_objetivos(wb, hoja, col_inicio, ancho_bloque, marca, metrica)
        for (marca, metrica), (hoja, col_inicio, ancho_bloque) in _HOJAS_OBJETIVO.items()
    ]
    partes = [p for p in partes if not p.empty]
    if not partes:
        raise SeguimientoFileError(
            "No se encontró ninguna pestaña de objetivos reconocida "
            f"({', '.join(h for h, _, _ in _HOJAS_OBJETIVO.values())})."
        )
    return pd.concat(partes, ignore_index=True)
