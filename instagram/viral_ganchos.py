"""Fórmulas de gancho en español frente al outlier multiple.

El clasificador de `.claude/skills/ig-viral/swipe.py` solo reconoce ganchos en inglés
(con 191 captions en español casi todo sale "sin clasificar"). Aquí se traducen las
fórmulas de `ig-reel/hooks.json` que existen en español y se añade una propia del nicho
("dolor nombrado"). Hace dos cosas:

1. Tus publicaciones: gancho = primera frase del caption (aproximación: no es el texto en
   pantalla ni lo que dices), múltiplo = alcance / mediana de las 12 anteriores.
2. El nicho: si existe `data/nicho/captura.tsv` con filas, múltiplo = vistas / mediana
   de los últimos 12 reels de esa cuenta (mismo método que ig-viral).

Uso:
    python instagram/viral_ganchos.py      # escribe informes/03_viralidad_ganchos.md
"""
import json
import re
import unicodedata
from pathlib import Path

import pandas as pd

BASE = Path(__file__).parent
OUT = BASE / "informes" / "03_viralidad_ganchos.md"
NICHO = BASE / "data" / "nicho" / "captura.tsv"
CAPTIONS = BASE / "data" / "raw" / "captions_2025-10-16_2026-10-15.json"
VENTANA = 12

# (id, nombre, patrón). Se asigna la primera que encaja; el orden importa.
# Los id numéricos son los de ig-reel/hooks.json; "ES" son propias del nicho en español.
FORMULAS = [
    ("ES3", "Pide el comentario primero", r"^(?:comenta|escr[ií]beme|d[eé]jame|escribe)\b"),
    ("1", "Confesión de coste", r"\bme cost[oó]\b|\bperd[ií]\b|\bme lesion"),
    ("3", "Nadie te lo dice", r"\bnadie (?:te|me|nos) (?:dice|dijo|cuenta|cont[oó]|explica|explic[oó]|habl)"),
    ("2", "Orden en negativo", r"^(?:deja de|no (?:hagas|corras|compres|uses|empieces|estires|cometas))\b"),
    ("20", "Permiso", r"\bno (?:necesitas|tienes que|hace falta)\b"),
    ("23", "Estadística", r"\d+\s?%"),
    ("ES1b", "Dolor como condición (si te duele…)", r"^si (?:a ti tambi[eé]n )?(?:te duele|sufres|tienes dolor|te molesta)"),
    ("ES1", "Dolor nombrado (pregunta u otra forma)", r"\bte duele\b|\bdolor\b|\bmolestia|\bperiostitis|\bcintilla|\bfascitis|\btendin"),
    ("22", "Contrarian (todos quieren… pocos)", r"\btodo el mundo\b|\btodos quieren\b|\bmuch[ií]simas? personas\b|\bmuchos\b[^.]*\bpocos\b"),
    ("7", "Error / forma correcta", r"\berror(?:es)?\b|\bmal\b|\bincorrect|\bas[ií] es como deber[ií]as\b|\bc[oó]mo (?:deber[ií]as|tienes que)\b"),
    ("11", "Lista numerada", r"^\d+\s+\w+|\b(?:\d+|dos|tres|cuatro|cinco|seis|siete|diez)\s+(?:ejercicios|trucos|errores|gestos|cosas|claves|consejos|tips|pasos|razones|se[ñn]ales)\b"),
    ("10", "Si te pasa esto, mira", r"^(?:si|cuando)\s+(?:te|tu|tú|tienes|quieres|corres|est[aá]s|eres|tu\s|no)\b"),
    ("ES2", "Causa → consecuencia", r"\bdetermina\b|\bte llevar[aá]\b|\bpuede costarte\b|\best[aá]s dejando\b|\bhar[aá]n? que\b|\bte volver[aá]s\b"),
    ("16", "Pregunta literal", r"^¿"),
    ("9", "La receta (plan/rutina/guía)", r"^(?:as[ií] (?:es como|se)|esta es (?:la|mi)|este es (?:el|mi)|(?:el|la|tu|mi) (?:plan|rutina|gu[ií]a)\b|plan\b|rutina\b|gu[ií]a\b|c[oó]mo\b)"),
    ("18", "Demostración en frío", r"^(?:mira|observa|f[ií]jate)\b"),
    ("26", "Superlativo", r"\b(?:el|la) (?:mejor|peor)\b|\bm[aá]s (?:r[aá]pido|f[aá]cil)\b"),
]
FORMULAS = [(i, n, re.compile(p, re.IGNORECASE)) for i, n, p in FORMULAS]
EMOJI = re.compile(r"[^\w\s¿?¡!.,:;%'\"“”()/-]", re.UNICODE)


def gancho(caption: str) -> str:
    """Primera frase del caption, sin emojis ni hashtags."""
    txt = unicodedata.normalize("NFC", caption or "").strip()
    linea = next((l for l in txt.splitlines() if l.strip(" .")), "")
    linea = EMOJI.sub("", linea.split("#")[0]).strip()
    m = re.match(r"(.+?[.!?…])(\s|$)", linea)
    return (m.group(1) if m else linea)[:160].strip()


def clasificar(h: str) -> tuple[str, str]:
    for fid, nombre, pat in FORMULAS:
        if pat.search(h):
            return fid, nombre
    return "-", "sin clasificar"


def tabla_formulas(d: pd.DataFrame) -> list[str]:
    tercio_alto = d["multiple"].quantile(2 / 3)
    tercio_bajo = d["multiple"].quantile(1 / 3)
    d = d.assign(alto=d["multiple"] >= tercio_alto, bajo=d["multiple"] <= tercio_bajo)
    g = d.groupby(["fid", "formula"]).agg(
        n=("multiple", "size"), mediana_x=("multiple", "median"),
        outliers=("multiple", lambda s: int((s > 3).sum())),
        en_tercio_alto=("alto", "sum"), en_tercio_bajo=("bajo", "sum"),
    ).reset_index().sort_values(["mediana_x", "n"], ascending=False)
    out = ["| fórmula | n | múltiplo mediano | outliers >3x | tercio alto | tercio bajo |",
           "|---|---|---|---|---|---|"]
    for r in g.itertuples():
        nota = "" if r.n >= 5 else " *(n<5)*"
        out.append(f"| {r.fid} · {r.formula}{nota} | {r.n} | {r.mediana_x:.2f}x | {r.outliers} | "
                   f"{int(r.en_tercio_alto)} | {int(r.en_tercio_bajo)} |")
    pal = d["gancho"].str.split().str.len()
    out.append(f"\nLongitud mediana del gancho: **{pal[d['alto']].median():.0f} palabras** en el tercio alto "
               f"y **{pal[d['bajo']].median():.0f}** en el tercio bajo. "
               f"Corte del tercio alto: ≥ {tercio_alto:.1f}x; del bajo: ≤ {tercio_bajo:.1f}x.")
    return out


def propias() -> pd.DataFrame:
    p = pd.read_csv(BASE / "data" / "publicaciones_12m.csv", parse_dates=["fecha"]).sort_values("fecha")
    caps = {re.search(r"/(?:p|reel)/([^/]+)/", c["media_permalink"]).group(1): c.get("media_caption", "")
            for c in json.loads(CAPTIONS.read_text(encoding="utf-8"))["data"]}
    p["gancho"] = p["shortcode"].map(caps).fillna("").map(gancho)
    p["mediana_prev"] = p["alcance"].shift(1).rolling(VENTANA, min_periods=6).median()
    p["multiple"] = p["alcance"] / p["mediana_prev"]
    p = p.dropna(subset=["multiple"])
    p = p[p["gancho"].str.len() > 0]
    p[["fid", "formula"]] = p["gancho"].apply(lambda h: pd.Series(clasificar(h)))
    return p


def nicho() -> pd.DataFrame | None:
    if not NICHO.exists():
        return None
    n = pd.read_csv(NICHO, sep="\t", comment="#").dropna(subset=["views", "median", "hook"])
    if n.empty:
        return None
    n["gancho"] = n["hook"].astype(str).map(lambda h: gancho(h) or h)
    n["multiple"] = n["views"] / n["median"]
    n[["fid", "formula"]] = n["gancho"].apply(lambda h: pd.Series(clasificar(h)))
    return n


def main() -> None:
    p = propias()
    reels = p[p["tipo"] == "REEL"]
    out = ["# Viralidad por fórmula de gancho\n",
           "Generado por `viral_ganchos.py`. Múltiplo = rendimiento frente a la propia mediana "
           "(> 3x es señal, < 1,5x es un día normal). Las fórmulas son las de `ig-reel/hooks.json` "
           "traducidas al español, más **ES1 · Dolor nombrado**, propia del nicho.\n",
           "## 1. Tus publicaciones (12 meses)\n",
           f"**Muestra:** {len(p)} publicaciones con historial ({len(reels)} reels). "
           "**Limitación importante:** el gancho es la primera frase del *caption*, no el texto en pantalla "
           "ni lo que dices en el primer segundo. Sirve para ver patrones de tema y estructura, no para "
           "juzgar la ejecución del gancho.\n",
           "### Todas las publicaciones\n", *tabla_formulas(p),
           "\n### Solo reels\n", *tabla_formulas(reels),
           "\n### Los 15 mayores múltiplos con su gancho\n",
           "| múltiplo | fecha | tipo | fórmula | gancho (1.ª frase del caption) |", "|---|---|---|---|---|"]
    for r in p.sort_values("multiple", ascending=False).head(15).itertuples():
        out.append(f"| **{r.multiple:.1f}x** | {r.fecha:%Y-%m-%d} | {r.tipo} | {r.fid} | {r.gancho} |")

    sc = p[p["fid"] == "-"]
    out += [f"\n### Sin clasificar ({len(sc)} de {len(p)})\n",
            "Los de mayor múltiplo, para leerlos a mano (puede haber una fórmula que no está en la lista):\n",
            "| múltiplo | gancho |", "|---|---|"]
    for r in sc.sort_values("multiple", ascending=False).head(12).itertuples():
        out.append(f"| {r.multiple:.1f}x | {r.gancho} |")

    out += ["\n## 2. Ganchos del plan de 4 semanas, por la misma lente\n",
            "| id | formato | fórmula | múltiplo mediano de esa fórmula en tus reels | gancho |", "|---|---|---|---|---|"]
    med = reels.groupby("fid")["multiple"].agg(["median", "size"])
    cal = pd.read_csv(BASE / "plan" / "calendario.csv", dtype=str)
    for r in cal.itertuples():
        g = gancho(str(r.gancho).split("(")[0]) or str(r.gancho)
        fid, nombre = clasificar(g)
        ref = (f"{med.loc[fid, 'median']:.2f}x (n={int(med.loc[fid, 'size'])})" if fid in med.index else "sin datos")
        out.append(f"| {r.id} | {r.formato} | {fid} · {nombre} | {ref} | {r.gancho} |")

    out.append("\n## 3. El nicho\n")
    n = nicho()
    if n is None:
        out.append("**Pendiente de datos.** Rellena `data/nicho/captura.tsv` (ver `data/nicho/LEEME.md`) y vuelve "
                   "a ejecutar este script. Sin la mediana de cada cuenta no se puede saber qué reel fue viral "
                   "de verdad, así que no se rellena con suposiciones.")
    else:
        out += [f"**Muestra:** {len(n)} reels de {n['account'].nunique()} cuentas. "
                + ("Con menos de 40 reels o 6 cuentas, tómalo como pista, no como conclusión.\n"
                   if len(n) < 40 or n["account"].nunique() < 6 else "\n"),
                *tabla_formulas(n),
                "\n| múltiplo | cuenta | vistas | mediana | fórmula | gancho |", "|---|---|---|---|---|---|"]
        for r in n.sort_values("multiple", ascending=False).itertuples():
            out.append(f"| **{r.multiple:.1f}x** | {r.account} | {r.views:,.0f} | {r.median:,.0f} | {r.fid} | {r.gancho} |")

    OUT.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"Escrito {OUT}")


if __name__ == "__main__":
    main()
