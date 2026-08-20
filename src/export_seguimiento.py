"""Genera el Excel con TODO el 'Seguimiento UC Retail & Wholesale'
-una hoja por pestaña x marca, tal cual se ve en la página-, no sólo
un resumen suelto (eso ya lo hace export.py)."""
import io
import itertools

import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

FUENTE = "Arial"
HEADER_FILL = PatternFill("solid", fgColor="1F3864")
HEADER_FONT = Font(name=FUENTE, bold=True, color="FFFFFF")
SUBHEADER_FILL = PatternFill("solid", fgColor="D9D9D9")
SUBHEADER_FONT = Font(name=FUENTE, bold=True)
BASE_FONT = Font(name=FUENTE)


_CARACTERES_INVALIDOS = str.maketrans("", "", "[]:*?/\\")


def _nombre_hoja(titulo: str) -> str:
    return titulo.translate(_CARACTERES_INVALIDOS)[:31]


def _escribir_tabla(ws, df: pd.DataFrame) -> None:
    """Escribe un DataFrame con columnas MultiIndex (nivel0=periodo,
    nivel1=submétrica) con cabecera de 2 filas, fusionando las celdas
    repetidas del nivel0 -igual que los bloques de mes del Excel
    original."""
    col = 1
    for nivel0, grupo in itertools.groupby(df.columns, key=lambda c: c[0]):
        span = len(list(grupo))
        c = ws.cell(row=1, column=col, value=nivel0 or None)
        c.font = HEADER_FONT
        c.fill = HEADER_FILL
        c.alignment = Alignment(horizontal="center")
        if span > 1:
            ws.merge_cells(start_row=1, start_column=col, end_row=1, end_column=col + span - 1)
        else:
            ws.merge_cells(start_row=1, start_column=col, end_row=2, end_column=col)
        col += span

    for j, (_, nivel1) in enumerate(df.columns, start=1):
        c = ws.cell(row=2, column=j, value=nivel1)
        c.font = SUBHEADER_FONT
        c.fill = SUBHEADER_FILL
        c.alignment = Alignment(horizontal="center")

    for i, (_, fila) in enumerate(df.iterrows(), start=3):
        for j, valor in enumerate(fila, start=1):
            valor = None if pd.isna(valor) else valor
            ws.cell(row=i, column=j, value=valor).font = BASE_FONT

    ws.freeze_panes = "C3"
    for j in range(1, len(df.columns) + 1):
        ws.column_dimensions[get_column_letter(j)].width = 11


def build_workbook(tablas: dict[tuple[str, str], pd.DataFrame], titulos: dict[str, callable], dealers: pd.DataFrame) -> bytes:
    """tablas: {(marca, tipo): DataFrame} -una por pestaña de la app-.
    titulos: {tipo: función(marca) -> título de la pestaña}."""
    wb = Workbook()
    wb.remove(wb.active)

    nombres_usados = set()
    for (marca, tipo), df in tablas.items():
        nombre = _nombre_hoja(titulos[tipo](marca))
        while nombre in nombres_usados:
            nombre = f"{nombre[:29]}·"
        nombres_usados.add(nombre)
        ws = wb.create_sheet(nombre)
        _escribir_tabla(ws, df)

    ws_maestro = wb.create_sheet("MAESTRO")
    headers = list(dealers.columns)
    for j, h in enumerate(headers, start=1):
        c = ws_maestro.cell(row=1, column=j, value=h)
        c.font = HEADER_FONT
        c.fill = HEADER_FILL
    for i, (_, fila) in enumerate(dealers.iterrows(), start=2):
        for j, valor in enumerate(fila, start=1):
            valor = None if pd.isna(valor) else valor
            ws_maestro.cell(row=i, column=j, value=valor).font = BASE_FONT

    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()
