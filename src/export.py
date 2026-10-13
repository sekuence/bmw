"""Genera el Excel descargable: un resumen por concesionario (equivalente
al bloque del 'Dealer Dashboard' original, pero para todos los
concesionarios a la vez) más el detalle mensual calculado desde la BBDD.
"""
import io

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

from . import dashboard, metrics

FUENTE = "Arial"
HEADER_FILL = PatternFill("solid", fgColor="1F3864")
HEADER_FONT = Font(name=FUENTE, bold=True, color="FFFFFF")
TITLE_FONT = Font(name=FUENTE, bold=True, size=14)
BASE_FONT = Font(name=FUENTE)
PCT_FORMAT = "0.0%"


def _write_header(ws, row, headers):
    for j, h in enumerate(headers, start=1):
        c = ws.cell(row=row, column=j, value=h)
        c.font = HEADER_FONT
        c.fill = HEADER_FILL
        c.alignment = Alignment(horizontal="center", wrap_text=True)


def _autosize(ws, n_cols, width=16):
    for j in range(1, n_cols + 1):
        ws.column_dimensions[get_column_letter(j)].width = width


def _dealers_de_marca(dealers, marca: str, codigos: list[int] | None = None):
    """Concesionarios que venden `marca`, filtrados a `codigos` si se
    da una lista -usado tanto para la vista previa de tarjetas como
    para el propio Excel, así nunca se desincronizan."""
    col = "vende_bmw" if marca == "BMW" else "vende_mini"
    sub = dealers[dealers[col] == "Si"]
    if codigos is not None:
        sub = sub[sub["codigo_dealer"].isin(codigos)]
    return sub.sort_values("concesionario")


def resumen_dealers(resumen, dealers, marca: str, periodo: str, mes_referencia: str | None = None, codigos: list[int] | None = None) -> list[dict]:
    """Un dict por concesionario (de `marca`, filtrado a `codigos` si se
    da) con los KPIs clave -pensado para pintar tarjetas visuales antes
    de generar el Excel, en vez de tener que abrirlo para verlas."""
    filas = []
    for _, d in _dealers_de_marca(dealers, marca, codigos).iterrows():
        codigo = int(d["codigo_dealer"])
        k = dashboard.kpi_bloque(resumen, codigo, marca, periodo, mes_referencia)
        objetivo, realizado = k["objetivo_retail"], k["realizado_retail"]
        filas.append({
            "codigo_dealer": codigo,
            "concesionario": d["concesionario"],
            "grupo_propietario": d["grupo_propietario"],
            "objetivo_retail": objetivo,
            "realizado_retail": realizado,
            "pct_cumplimiento": (realizado / objetivo) if objetivo else None,
            "bps": k["bps"],
            "bev": k["bev"],
        })
    return filas


def build_workbook(resumen, dealers, marca: str, periodo: str, mes_referencia: str | None = None, codigos: list[int] | None = None) -> bytes:
    """codigos: si se da, el Excel sólo incluye esos concesionarios
    (selección manual) -si es None, incluye todos los que venden
    `marca`, igual que antes."""
    wb = Workbook()

    ws = wb.active
    ws.title = "Dashboard concesionarios"
    ws["A1"] = f"Seguimiento UC Retail & Wholesale — {marca} — {periodo}" + (f" ({mes_referencia})" if mes_referencia else "")
    ws["A1"].font = TITLE_FONT

    headers = [
        "Código", "Concesionario", "Grupo propietario",
        "Objetivo Retail", "Realizado Retail", "% Cumplimiento",
        "BPS/MN", "% BPS/MN",
        "Remarketing", "% Remarketing",
        "BEV", "% BEV",
        "Wholesale UC", "Wholesale YUC",
        "Mercado <6 años", "% Penetración",
        "Mystery Shopping",
    ]
    header_row = 3
    _write_header(ws, header_row, headers)

    fila = header_row + 1
    for _, d in _dealers_de_marca(dealers, marca, codigos).iterrows():
        codigo = int(d["codigo_dealer"])
        k = dashboard.kpi_bloque(resumen, codigo, marca, periodo, mes_referencia)
        valores = [
            codigo, d["concesionario"], d["grupo_propietario"],
            k["objetivo_retail"], k["realizado_retail"], None,
            k["bps"], None,
            k["remarketing"], None,
            k["bev"], None,
            k["wholesale_uc"], k["wholesale_yuc"],
            k["mercado_menos_6_anos"], None,
            k["mystery_shopping"],
        ]
        for j, v in enumerate(valores, start=1):
            c = ws.cell(row=fila, column=j, value=v)
            c.font = BASE_FONT

        # % como fórmulas locales (recalculan solas si se edita el valor a mano).
        # %BPS se calcula sobre el Realizado (E), pero %Remarketing y %BEV
        # se calculan sobre el Objetivo (D), no sobre el Realizado -igual
        # que en dashboard.py y en el Excel original-.
        ws.cell(row=fila, column=6, value=f"=IFERROR(E{fila}/D{fila},\"\")").number_format = PCT_FORMAT
        ws.cell(row=fila, column=8, value=f"=IFERROR(G{fila}/E{fila},\"\")").number_format = PCT_FORMAT
        ws.cell(row=fila, column=10, value=f"=IFERROR(I{fila}/D{fila},\"\")").number_format = PCT_FORMAT
        ws.cell(row=fila, column=12, value=f"=IFERROR(K{fila}/D{fila},\"\")").number_format = PCT_FORMAT
        ws.cell(row=fila, column=16, value=f"=IFERROR(E{fila}/O{fila},\"\")").number_format = PCT_FORMAT
        fila += 1

    ws.freeze_panes = ws.cell(row=header_row + 1, column=1)
    _autosize(ws, len(headers))

    # Hoja de detalle mensual (equivalente a las pestañas "feeder" del Excel original)
    ws2 = wb.create_sheet("Detalle mensual")
    detalle = resumen[resumen["marca"] == marca]
    if codigos is not None:
        detalle = detalle[detalle["codigo_dealer"].isin(codigos)]
    detalle = detalle.merge(
        dealers[["codigo_dealer", "concesionario", "grupo_propietario"]], on="codigo_dealer", how="left"
    )
    det_headers = ["codigo_dealer", "concesionario", "grupo_propietario", "mes", "retail", "bps", "remarketing", "bev", "wholesale_uc", "wholesale_yuc"]
    _write_header(ws2, 1, det_headers)
    for i, (_, r) in enumerate(detalle[det_headers].sort_values(["concesionario", "mes"]).iterrows(), start=2):
        for j, col in enumerate(det_headers, start=1):
            ws2.cell(row=i, column=j, value=r[col]).font = BASE_FONT
    _autosize(ws2, len(det_headers))
    ws2.freeze_panes = "A2"

    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()
