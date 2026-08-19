"""Colores de marca usados en toda la app, para que BMW y MINI se
distingan de un vistazo -azul BMW / naranja MINI-, igual que en el
Excel original."""
import streamlit as st

COLOR_BMW = "#0066B1"
COLOR_MINI = "#F5811F"

# Varios tonos de cada color de marca, para gráficos con más de una
# serie (p.ej. Objetivo vs Realizado) sin perder la distinción BMW/MINI.
PALETA_BMW = ["#0066B1", "#5B9BD5", "#A9CCE8"]
PALETA_MINI = ["#F5811F", "#F7A85C", "#FBCB98"]


def color_de(marca: str) -> str:
    return COLOR_BMW if marca == "BMW" else COLOR_MINI


def paleta(marca: str, n: int) -> list[str]:
    """n tonos del color de la marca, para pasar a color= en st.bar_chart
    / st.line_chart y que BMW y MINI no compartan la misma paleta."""
    colores = PALETA_BMW if marca == "BMW" else PALETA_MINI
    if n <= len(colores):
        return colores[:n]
    return (colores * ((n // len(colores)) + 1))[:n]


def encabezado(marca: str, extra: str = "") -> None:
    """Cabecera de sección con el color de la marca (fondo azul/naranja)."""
    color = color_de(marca)
    texto_extra = f" — {extra}" if extra else ""
    st.markdown(
        f"<div style='background:{color};color:white;padding:8px 14px;"
        f"border-radius:6px;font-weight:600;font-size:1.15rem;margin-bottom:10px;'>"
        f"{marca}{texto_extra}</div>",
        unsafe_allow_html=True,
    )


def badge(marca: str) -> str:
    """HTML de una etiqueta pequeña con el color de la marca, para insertar
    dentro de otro st.markdown (p.ej. junto a un título de tabla)."""
    color = color_de(marca)
    return (
        f"<span style='background:{color};color:white;padding:2px 10px;"
        f"border-radius:10px;font-size:0.8rem;font-weight:600'>{marca}</span>"
    )


def semaforo(cumple: bool | None) -> str:
    """Punto de color verde/rojo (o gris si no hay dato) para indicadores
    de mínimos (p.ej. % BPS/MN, Mystery Shopping)."""
    if cumple is None:
        return "<span style='color:#999'>○ sin dato</span>"
    color = "#2E7D32" if cumple else "#C62828"
    texto = "cumple mínimo" if cumple else "no cumple mínimo"
    return f"<span style='color:{color};font-weight:600'>● {texto}</span>"
