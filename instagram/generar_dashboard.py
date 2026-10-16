"""Genera instagram/dashboard.html: panel de la cuenta + plan del experimento.

Uso (después de importar_windsor.py):
    python instagram/generar_dashboard.py
"""
import html
import sys
from pathlib import Path

import pandas as pd

BASE = Path(__file__).parent
sys.path.insert(0, str(BASE))
import evaluar_experimento as ev  # noqa: E402

DATA = BASE / "data"
OUT = BASE / "dashboard.html"

MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
TEMAS_ES = {
    "fuerza": "Fuerza / rutinas", "opinion": "Opinión / debate", "tecnica": "Técnica",
    "lesiones": "Lesiones / dolor", "principiantes": "Principiantes", "personal": "Personal",
    "nutricion": "Nutrición", "marca": "Marca / eventos", "mentalidad": "Mentalidad",
    "venta": "Venta directa", "ciencia": "Ciencia", "noticia": "Noticias", "educativo": "Caption genérico",
    "perdida_grasa": "Pérdida de grasa", "humor": "Humor", "testimonio": "Testimonio",
}
E = html.escape


def n(x: float) -> str:
    return f"{x:,.0f}".replace(",", ".")


def svg_meses(p: pd.DataFrame) -> str:
    m = p.groupby(p["fecha"].dt.to_period("M"))["alcance"].median()
    w, h, pl, pb, pt = 640, 220, 44, 28, 14
    top = 12000
    bw = (w - pl - 8) / len(m)
    partes = [f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="Alcance mediano por publicación, por mes">']
    for v in (0, 4000, 8000, 12000):
        y = h - pb - (h - pb - pt) * v / top
        partes.append(f'<line x1="{pl}" x2="{w - 4}" y1="{y:.1f}" y2="{y:.1f}" class="grid"/>'
                      f'<text x="{pl - 6}" y="{y + 4:.1f}" class="axis" text-anchor="end">{n(v)}</text>')
    for i, (per, v) in enumerate(m.items()):
        x = pl + i * bw + 3
        bh = (h - pb - pt) * min(v, top) / top
        cls = "bar hi" if v == m.max() else ("bar lo" if per == m.index[-1] else "bar")
        partes.append(f'<rect x="{x:.1f}" y="{h - pb - bh:.1f}" width="{bw - 6:.1f}" height="{bh:.1f}" rx="2" class="{cls}">'
                      f'<title>{MESES[per.month - 1]} {per.year}: {n(v)}</title></rect>')
        partes.append(f'<text x="{x + (bw - 6) / 2:.1f}" y="{h - pb + 16}" class="axis" text-anchor="middle">'
                      f'{MESES[per.month - 1]}</text>')
        if v == m.max() or per == m.index[-1] or i == 0:
            partes.append(f'<text x="{x + (bw - 6) / 2:.1f}" y="{h - pb - bh - 5:.1f}" class="val" '
                          f'text-anchor="middle">{n(v)}</text>')
    partes.append("</svg>")
    return "".join(partes)


def barras_h(filas: list[tuple[str, float, str, str]], maximo: float) -> str:
    """filas: (etiqueta, valor, texto a la derecha, clase)."""
    out = []
    for et, v, txt, cls in filas:
        out.append(f'<div class="hb"><span class="hb-l">{E(et)}</span>'
                   f'<span class="hb-t"><span class="hb-b {cls}" style="width:{100 * v / maximo:.1f}%"></span></span>'
                   f'<span class="hb-v">{E(txt)}</span></div>')
    return "".join(out)


def main() -> None:
    p = pd.read_csv(DATA / "publicaciones_12m.csv", parse_dates=["fecha"])
    d = pd.read_csv(DATA / "diario_30d.csv")
    ge = pd.read_csv(DATA / "audiencia_genero_edad.csv")
    pa = pd.read_csv(DATA / "audiencia_paises.csv")
    df = ev.cargar()
    estados = ev.estados(df)

    reciente = p[p["fecha"] >= p["fecha"].max() - pd.Timedelta(days=89)]
    ant = p[(p["fecha"] >= "2026-01-18") & (p["fecha"] < "2026-04-18")]
    nuevos = d["nuevos_seguidores"].dropna()
    no_seg = d["alcance_no_seguidores"].sum() / (d["alcance_seguidores"].sum() + d["alcance_no_seguidores"].sum())

    kpis = [
        ("Seguidores", "37.007", "1.822 publicaciones"),
        ("Alcance mediano por post", n(reciente["alcance"].median()), f"últimos 90 días · era {n(ant['alcance'].median())} en ene–abr"),
        ("Nuevos seguidores / día", f"{nuevos.mean():.0f}", f"últimos 30 días · {n(nuevos.sum())} en total"),
        ("Alcance de no seguidores", f"{no_seg:.0%}", "creces por descubrimiento; tu base casi no te ve"),
    ]

    temas = (p.groupby("tema")["alcance"].agg(["median", "size"])
             .query("size >= 5 and tema != 'educativo'").sort_values("median", ascending=False))
    filas_t = [(TEMAS_ES.get(t, t), r["median"], f"{n(r['median'])} · {r['size']:.0f} posts",
                "warn" if t in ("mentalidad", "marca", "venta") else ("good" if r["median"] >= 5000 else ""))
               for t, r in temas.iterrows()]

    reels = p[p["tipo"] == "REEL"].copy()
    reels["b"] = pd.cut(reels["skip_rate"], [0, .40, .45, .50, 1], labels=["< 40 %", "40–45 %", "45–50 %", "> 50 %"])
    sk = reels.groupby("b", observed=True)["alcance"].agg(["median", "size"])
    filas_s = [(f"Abandono {b}", r["median"], f"{n(r['median'])} · {r['size']:.0f} reels",
                "good" if b == "< 40 %" else ("warn" if b == "> 50 %" else ""))
               for b, r in sk.iterrows()]

    tot = ge["seguidores"].sum()
    edad = ge.groupby("edad")["seguidores"].sum() / tot
    filas_e = [(e, v, f"{v:.0%}", "good" if e in ("35-44", "45-54") else "") for e, v in edad.items()]
    pa["pct"] = pa["seguidores"] / pa["seguidores"].sum()
    filas_p = [(r.pais, r.pct, f"{r.pct:.0%}", "") for r in pa.head(8).itertuples()]
    mujeres = ge[ge.genero == "F"]["seguidores"].sum() / tot

    top = p.nlargest(10, "alcance")
    filas_top = "".join(
        f'<tr><td class="num">{r.fecha:%d-%m-%y}</td><td><a href="https://www.instagram.com/{"reel" if r.tipo == "REEL" else "p"}/{r.shortcode}/" '
        f'target="_blank" rel="noopener">{E(str(r.resumen))}</a></td><td>{E(TEMAS_ES.get(r.tema, r.tema))}</td>'
        f'<td class="num">{n(r.alcance)}</td><td class="num">{n(r.guardados)}</td><td class="num">{n(r.compartidos)}</td></tr>'
        for r in top.itertuples())

    filas_h = "".join(
        f'<tr><td><span class="chip">{h}</span></td><td><span class="st {"ok" if "✅" in s else ("no" if "❌" in s else "pend")}">'
        f'{E(s.replace("✅ ", "").replace("❌ ", ""))}</span></td><td>{E(det)}</td></tr>'
        for h, s, det in estados)

    semanas = [("Semana 1", "19–24 oct", "Repetir lo que ya ganó + primer test de CTA"),
               ("Semana 2", "26–31 oct", "Pilar +40 y Nueva York (grabar antes de viajar)"),
               ("Semana 3", "2–7 nov", "Post-maratón + A/B con Trial Reels"),
               ("Semana 4", "9–14 nov", "Consolidar y cerrar hipótesis")]
    cortes = ["2026-10-26", "2026-11-02", "2026-11-09", "2099-01-01"]
    df = df.sort_values(["fecha", "id"])
    bloques = []
    ini = "2000-01-01"
    for (sem, rango, foco), fin in zip(semanas, cortes):
        sub = df[(df["fecha"] >= ini) & (df["fecha"] < fin)]
        ini = fin
        cards = []
        for r in sub.itertuples():
            fecha = pd.Timestamp(r.fecha)
            dia = ["lun", "mar", "mié", "jue", "vie", "sáb", "dom"][fecha.dayofweek]
            res = (f'<p class="res">Alcance <b>{n(r.alcance)}</b> · guardados {n(r.guardados)} · compartidos {n(r.compartidos)}</p>'
                   if pd.notna(r.alcance) else "")
            clave = f'<span class="kw">{E(r.palabra_clave)}</span>' if isinstance(r.palabra_clave, str) and r.palabra_clave != "EMOJI" else ""
            cards.append(
                f'<article class="post" data-id="{E(r.id)}">'
                f'<div class="bib"><span class="bib-n">{E(r.id)}</span><span class="bib-d">{dia} {fecha.day}</span></div>'
                f'<div class="post-b"><div class="meta"><span class="fmt">{E(r.formato.replace("_", " ").lower())}</span>'
                f'<span class="chip">{E(r.hipotesis)}</span>{clave}</div>'
                f'<h4>{E(r.titulo)}</h4>'
                f'<p class="hook"><span class="lbl">Gancho</span>{E(r.gancho)}</p>'
                f'<p class="cta"><span class="lbl">CTA</span>{E(r.cta_texto)}</p>{res}'
                f'<label class="done"><input type="checkbox" id="hecho-{E(r.id)}"> Publicado</label></div></article>')
        bloques.append(f'<section class="week"><header><h3>{sem}</h3><span class="rng">{rango}</span>'
                       f'<span class="foco">{E(foco)}</span></header><div class="posts">{"".join(cards)}</div></section>')

    hoy = p["fecha"].max()
    page = PLANTILLA.format(
        actualizado=f"{hoy.day} {MESES[hoy.month - 1]} {hoy.year}",
        kpis="".join(f'<div class="kpi"><span class="k-l">{E(a)}</span><span class="k-v">{E(b)}</span>'
                     f'<span class="k-s">{E(c)}</span></div>' for a, b, c in kpis),
        meses=svg_meses(p),
        temas=barras_h(filas_t, temas["median"].max()),
        skip=barras_h(filas_s, sk["median"].max()),
        edad=barras_h(filas_e, edad.max()),
        paises=barras_h(filas_p, pa["pct"].max()),
        mujeres=f"{mujeres:.0%}",
        top=filas_top, hip=filas_h, semanas="".join(bloques),
    )
    OUT.write_text(page, encoding="utf-8")
    print(f"Escrito {OUT}")


PLANTILLA = """<title>Panel @healthyanii</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700&family=Source+Sans+3:wght@400;600&family=JetBrains+Mono:wght@500&display=swap">
<style>
/* Layout: una columna de lectura; arriba el resumen, luego el porqué, al final el plan semana a semana como dorsales de carrera. */
:root {{
  --bg: #f4f6f7; --surface: #ffffff; --ink: #15212b; --muted: #5a6b78; --line: #dde3e7;
  --accent: #d9482b; --accent-soft: #fbe3dc; --good: #1d7a68; --good-soft: #d8efe9; --warn: #b7791f; --warn-soft: #f7ead2;
  --bar: #9fb3c2;
  --f-display: "Barlow Condensed", "Arial Narrow", sans-serif;
  --f-body: "Source Sans 3", "Segoe UI", system-ui, sans-serif;
  --f-mono: "JetBrains Mono", ui-monospace, "SFMono-Regular", monospace;
}}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{
  --bg: #0f161c; --surface: #17212a; --ink: #e6edf2; --muted: #93a4b1; --line: #26343f;
  --accent: #ff7a5c; --accent-soft: #3a2119; --good: #4cc2a6; --good-soft: #14302a; --warn: #e5ad55; --warn-soft: #33270f;
  --bar: #4d6274; color-scheme: dark; }} }}
:root[data-theme="dark"] {{
  --bg: #0f161c; --surface: #17212a; --ink: #e6edf2; --muted: #93a4b1; --line: #26343f;
  --accent: #ff7a5c; --accent-soft: #3a2119; --good: #4cc2a6; --good-soft: #14302a; --warn: #e5ad55; --warn-soft: #33270f;
  --bar: #4d6274; color-scheme: dark; }}
body {{ background: var(--bg); color: var(--ink); font: 16px/1.5 var(--f-body); }}
.wrap {{ max-width: 1040px; margin: 0 auto; padding-block: 32px 64px;
  padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px));
  display: grid; gap: 40px; }}
.wrap > * {{ min-width: 0; }}
h1, h2, h3, h4 {{ font-family: var(--f-display); text-wrap: balance; margin: 0; line-height: 1.05; }}
h1 {{ font-size: clamp(2.4rem, 6vw, 3.6rem); font-weight: 700; letter-spacing: .01em; }}
h1 span {{ color: var(--accent); }}
h2 {{ font-size: 1.9rem; font-weight: 600; }}
h3 {{ font-size: 1.4rem; font-weight: 600; }}
p {{ margin: 0; }}
.lede {{ color: var(--muted); max-width: 62ch; margin-top: 8px; }}
.eyebrow {{ font: 600 .75rem/1 var(--f-body); letter-spacing: .12em; text-transform: uppercase; color: var(--muted); }}
section > .head {{ display: grid; gap: 6px; margin-bottom: 16px; }}
.kpis {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 12px; }}
.kpi {{ background: var(--surface); border: 1px solid var(--line); border-radius: 6px; padding: 16px; display: grid; gap: 4px; }}
.k-l {{ font-size: .8rem; letter-spacing: .06em; text-transform: uppercase; color: var(--muted); font-weight: 600; }}
.k-v {{ font: 700 2.4rem/1 var(--f-display); font-variant-numeric: tabular-nums; }}
.k-s {{ font-size: .85rem; color: var(--muted); }}
.grid2 {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 32px; }}
.grid2 > div {{ min-width: 0; }}
.chart svg {{ width: 100%; height: auto; display: block; }}
.grid {{ stroke: var(--line); stroke-width: 1; }}
.axis {{ fill: var(--muted); font: 11px var(--f-mono); }}
.val {{ fill: var(--ink); font: 600 11px var(--f-mono); }}
.bar {{ fill: var(--bar); }} .bar.hi {{ fill: var(--good); }} .bar.lo {{ fill: var(--accent); }}
.note {{ font-size: .9rem; color: var(--muted); margin-top: 10px; max-width: 65ch; }}
.note b {{ color: var(--ink); }}
.hb {{ display: grid; grid-template-columns: minmax(96px, 9.5rem) 1fr auto; align-items: center; gap: 10px; padding: 5px 0; font-size: .92rem; }}
.hb-l {{ min-width: 0; overflow-wrap: anywhere; }}
.hb-t {{ height: 10px; background: var(--line); border-radius: 5px; overflow: hidden; }}
.hb-b {{ display: block; height: 100%; background: var(--bar); border-radius: 5px; }}
.hb-b.good {{ background: var(--good); }} .hb-b.warn {{ background: var(--warn); }}
.hb-v {{ font: 12px var(--f-mono); color: var(--muted); font-variant-numeric: tabular-nums; white-space: nowrap; }}
.tbl {{ overflow-x: auto; border: 1px solid var(--line); border-radius: 6px; background: var(--surface); }}
table {{ border-collapse: collapse; width: 100%; font-size: .92rem; min-width: 560px; }}
th, td {{ text-align: left; padding: 9px 12px; border-bottom: 1px solid var(--line); vertical-align: top; }}
th {{ font-size: .75rem; letter-spacing: .08em; text-transform: uppercase; color: var(--muted); font-weight: 600; }}
tr:last-child td {{ border-bottom: 0; }}
td.num, th.num {{ text-align: right; font-family: var(--f-mono); font-size: .85rem; font-variant-numeric: tabular-nums; white-space: nowrap; }}
a {{ color: var(--ink); text-decoration-color: var(--accent); text-underline-offset: 3px; }}
a:focus-visible, input:focus-visible {{ outline: 2px solid var(--accent); outline-offset: 2px; }}
.chip {{ font: 600 .72rem/1 var(--f-mono); padding: 4px 6px; border-radius: 4px; background: var(--accent-soft); color: var(--accent); white-space: nowrap; }}
.st {{ font-size: .8rem; font-weight: 600; padding: 3px 8px; border-radius: 999px; white-space: nowrap; }}
.st.pend {{ background: var(--line); color: var(--muted); }} .st.ok {{ background: var(--good-soft); color: var(--good); }} .st.no {{ background: var(--warn-soft); color: var(--warn); }}
.week {{ display: grid; gap: 12px; }}
.week header {{ display: flex; flex-wrap: wrap; align-items: baseline; gap: 6px 14px; border-top: 2px solid var(--ink); padding-top: 10px; }}
.rng {{ font: 12px var(--f-mono); color: var(--muted); }}
.foco {{ color: var(--muted); font-size: .92rem; }}
.posts {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 12px; }}
.post {{ display: grid; grid-template-columns: 64px 1fr; gap: 12px; background: var(--surface); border: 1px solid var(--line); border-radius: 6px; padding: 14px; }}
.post.is-done {{ border-color: var(--good); }}
.bib {{ align-self: start; display: grid; place-items: center; border: 2px solid var(--ink); border-radius: 4px; padding: 6px 0 4px; position: relative; }}
.bib::before, .bib::after {{ content: ""; position: absolute; top: 4px; width: 5px; height: 5px; border-radius: 50%; border: 1.5px solid var(--muted); }}
.bib::before {{ left: 4px; }} .bib::after {{ right: 4px; }}
.bib-n {{ font: 700 1.7rem/1 var(--f-display); font-variant-numeric: tabular-nums; }}
.bib-d {{ font: 10px var(--f-mono); color: var(--muted); text-transform: uppercase; }}
.post-b {{ min-width: 0; display: grid; gap: 7px; align-content: start; }}
.meta {{ display: flex; flex-wrap: wrap; gap: 6px; align-items: center; }}
.fmt {{ font-size: .72rem; text-transform: uppercase; letter-spacing: .08em; color: var(--muted); font-weight: 600; }}
.kw {{ font: 600 .72rem/1 var(--f-mono); padding: 4px 6px; border-radius: 4px; border: 1px dashed var(--accent); color: var(--accent); }}
.post h4 {{ font-size: 1.2rem; font-weight: 600; }}
.hook, .cta {{ font-size: .9rem; }}
.lbl {{ display: inline-block; min-width: 3.6rem; font-size: .7rem; letter-spacing: .08em; text-transform: uppercase; color: var(--muted); font-weight: 600; }}
.res {{ font-size: .85rem; color: var(--good); }}
.done {{ font-size: .85rem; color: var(--muted); display: inline-flex; gap: 6px; align-items: center; cursor: pointer; }}
.done input {{ accent-color: var(--good); width: 16px; height: 16px; }}
.rules {{ display: grid; gap: 6px; padding-left: 1.1rem; margin: 0; max-width: 70ch; }}
@media (max-width: 480px) {{ .hb {{ grid-template-columns: 1fr auto; }} .hb-t {{ grid-column: 1 / -1; grid-row: 2; }} }}
</style>
<div class="wrap">
  <header>
    <p class="eyebrow">Instagram · datos al {actualizado}</p>
    <h1>@healthyanii <span>en marcha</span></h1>
    <p class="lede">Doce meses de datos de tu cuenta y el plan de 4 semanas para comprobar qué te hace crecer. Las cifras salen de la API de Instagram; el plan está en <code>instagram/plan/</code>.</p>
  </header>

  <section><div class="kpis">{kpis}</div></section>

  <section>
    <div class="head"><p class="eyebrow">Evolución</p><h2>Alcance mediano por publicación, mes a mes</h2></div>
    <div class="chart">{meses}</div>
    <p class="note">El salto llegó al pasar del contenido de mentalidad a <b>técnica, lesiones y fuerza en reel corto</b>. Octubre cae otra vez: más marca y venta y captions genéricos.</p>
  </section>

  <section class="grid2">
    <div>
      <div class="head"><p class="eyebrow">Qué funciona</p><h3>Alcance mediano por tema (12 meses)</h3></div>
      {temas}
      <p class="note">Mentalidad es tu segundo tema más publicado y el que menos alcanza.</p>
    </div>
    <div>
      <div class="head"><p class="eyebrow">Primeros 3 segundos</p><h3>Alcance según el abandono inicial</h3></div>
      {skip}
      <p class="note">Un reel que retiene en los primeros 3 s alcanza <b>5 veces más</b>. 50 de tus 137 reels pierden a más de la mitad ahí.</p>
    </div>
  </section>

  <section class="grid2">
    <div>
      <div class="head"><p class="eyebrow">Audiencia · {mujeres} mujeres</p><h3>Edad de tus seguidores</h3></div>
      {edad}
    </div>
    <div>
      <div class="head"><p class="eyebrow">Audiencia</p><h3>Países principales</h3></div>
      {paises}
    </div>
  </section>

  <section>
    <div class="head"><p class="eyebrow">Referencia</p><h2>Tus 10 publicaciones con más alcance</h2></div>
    <div class="tbl"><table>
      <thead><tr><th>Fecha</th><th>Publicación</th><th>Tema</th><th class="num">Alcance</th><th class="num">Guardados</th><th class="num">Compartidos</th></tr></thead>
      <tbody>{top}</tbody></table></div>
  </section>

  <section>
    <div class="head"><p class="eyebrow">Experimento 19 oct – 15 nov</p><h2>Hipótesis en prueba</h2>
      <p class="lede">H1 dolor + 3 ejercicios · H2 CTA al final vs. primero · H3 carrusel con palabra clave · H4 opinión semanal · H5 republicar virales · H6 pilar +40. El estado se actualiza al regenerar el panel con datos nuevos.</p></div>
    <div class="tbl"><table>
      <thead><tr><th>Hipótesis</th><th>Estado</th><th>Detalle</th></tr></thead>
      <tbody>{hip}</tbody></table></div>
  </section>

  <section>
    <div class="head"><p class="eyebrow">Reglas fijas</p><h2>Cómo publicar durante el experimento</h2></div>
    <ul class="rules">
      <li>Siempre a las 19:00 UTC: 21:00 en España hasta el 25-oct, 20:00 desde el 26-oct; 15:00 en Venezuela.</li>
      <li>Feed lunes, martes, miércoles, viernes y sábado. Jueves y domingo, solo stories.</li>
      <li>Gancho escrito en pantalla en el primer fotograma, subtítulos y entre 20 y 40 segundos.</li>
      <li>El caption empieza con una frase con palabras clave del tema. Nunca solo «Sígueme».</li>
      <li>Responder a todos los comentarios en la primera hora.</li>
    </ul>
  </section>

  <section>
    <div class="head"><p class="eyebrow">Calendario</p><h2>Las 20 publicaciones</h2>
      <p class="lede">Marca cada una al publicarla; la marca se guarda solo en este navegador. Los guiones completos están en <code>plan_experimento_4_semanas.md</code>.</p></div>
    <div style="display:grid;gap:32px">{semanas}</div>
  </section>
</div>
<script>
(function () {{
  document.querySelectorAll(".post").forEach(function (card) {{
    var box = card.querySelector("input[type=checkbox]");
    var key = "healthyanii-" + box.id;
    try {{ box.checked = localStorage.getItem(key) === "1"; }} catch (e) {{}}
    card.classList.toggle("is-done", box.checked);
    box.addEventListener("change", function () {{
      card.classList.toggle("is-done", box.checked);
      try {{ localStorage.setItem(key, box.checked ? "1" : "0"); }} catch (e) {{}}
    }});
  }});
}})();
</script>
"""

if __name__ == "__main__":
    main()
