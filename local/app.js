/* ==========================================================================
   Seguimiento UC Retail & Wholesale — versión local (sin servidor).
   Corre Python (pandas/openpyxl) en el navegador vía Pyodide. Todo el
   código de negocio (src/*.py) es el mismo que usa la app de Streamlit;
   esto sólo es la interfaz que lo llama y pinta el resultado en HTML.
   ========================================================================== */

const MESES = ["ENERO","FEBRERO","MARZO","ABRIL","MAYO","JUNIO","JULIO","AGOSTO","SEPTIEMBRE","OCTUBRE","NOVIEMBRE","DICIEMBRE"];
const MESES_S2 = MESES.slice(6);
const PERIODOS_COMPLETO = [...MESES, "TRIMESTRE 1","TRIMESTRE 2","TRIMESTRE 3","TRIMESTRE 4","SEMESTRE 1","SEMESTRE 2","ACUMULADO MES","ACUMULADO MES 2S","ANUAL"];
const COLOR_BMW = "#0066B1", COLOR_MINI = "#F5811F";
const METRICAS_AJUSTABLES = {
  retail: "Ventas Retail", bps: "BPS / MN", remarketing: "Retail origen Remarketing", bev: "BEV",
  wholesale_uc: "Wholesale UC", wholesale_yuc: "Wholesale YUC", ventas_totales: "Ventas Totales (Retail + Wholesale)",
};

let pyodide = null;
let bv = null;
const APPSTATE = { cargado: false, nombre: null };

/* -------------------------- arranque de Pyodide -------------------------- */

function bootLog(msg) {
  const el = document.getElementById("boot-log");
  if (el) el.textContent = msg;
}

function bootError(err) {
  console.error(err);
  const el = document.getElementById("boot-error");
  if (el) {
    el.textContent = "No se pudo arrancar la app:\n" + (err && err.message ? err.message : String(err)) +
      "\n\nComprueba que tienes conexión a internet (se necesita la primera vez, para cargar el motor Python " +
      "y pandas/openpyxl) y vuelve a abrir el archivo.";
  }
  const spinner = document.querySelector("#boot-screen .spinner");
  if (spinner) spinner.style.display = "none";
}

function base64ToUint8Array(b64) {
  const bin = atob(b64);
  const bytes = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
  return bytes;
}

function writeVirtualFiles() {
  const dirsNeeded = new Set();
  document.querySelectorAll("script[data-vpath]").forEach((el) => {
    const parts = el.dataset.vpath.split("/");
    parts.pop();
    if (parts.length) dirsNeeded.add(parts.join("/"));
  });
  dirsNeeded.forEach((d) => pyodide.FS.mkdirTree("/" + d));
  document.querySelectorAll("script[data-vpath]").forEach((el) => {
    const content = el.dataset.encoding === "base64" ? base64ToUint8Array(el.textContent.trim()) : el.textContent;
    pyodide.FS.writeFile("/" + el.dataset.vpath, content);
  });
}

async function boot() {
  try {
    bootLog("Cargando el motor Python (Pyodide)…");
    pyodide = await loadPyodide();
    bootLog("Cargando pandas…");
    await pyodide.loadPackage(["pandas"]);
    bootLog("Cargando openpyxl (desde PyPI)…");
    await pyodide.loadPackage("micropip");
    const micropip = pyodide.pyimport("micropip");
    await micropip.install("openpyxl");
    bootLog("Preparando los archivos de la app…");
    writeVirtualFiles();
    bootLog("Importando la lógica de la app…");
    await pyodide.runPythonAsync("import sys\nsys.path.insert(0, '/')\nimport browser_views as bv\n");
    bv = pyodide.pyimport("browser_views");

    document.getElementById("boot-screen").style.display = "none";
    document.getElementById("app").classList.add("ready");
    wireNav();
    wireDelegatedEvents();
    goPage("home");
  } catch (err) {
    bootError(err);
  }
}

/* -------------------------- puente JS <-> Python -------------------------- */

function callPy(fnName, ...args) {
  const pyArgs = args.map((a) => {
    if (a === undefined) return null;
    if (a !== null && typeof a === "object") return pyodide.toPy(a);
    return a;
  });
  const fn = bv[fnName];
  const result = fn(...pyArgs);
  if (result && typeof result.toJs === "function") {
    const js = result.toJs({ dict_converter: Object.fromEntries, create_proxies: false });
    if (typeof result.destroy === "function") result.destroy();
    return js;
  }
  return result;
}

function downloadBytes(bytesU8, filename, mime) {
  const blob = new Blob([bytesU8], { type: mime || "application/octet-stream" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 2000);
}

const XLSX_MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet";

/* ------------------------------ utilidades ------------------------------ */

function esc(s) {
  if (s === null || s === undefined) return "";
  return String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}
function fmtNum(x, dec = 0) { return x === null || x === undefined ? "—" : Number(x).toFixed(dec); }
function fmtPct(x, dec = 1) { return x === null || x === undefined ? "—" : Number(x * 100).toFixed(dec) + "%"; }
function colorDe(marca) { return marca === "BMW" ? COLOR_BMW : COLOR_MINI; }
function brandbarHtml(marca, extra) {
  return `<div class="brandbar" style="background:${colorDe(marca)}">${esc(marca)}${extra ? " — " + esc(extra) : ""}</div>`;
}
function badgeHtml(marca) { return `<span class="badge" style="background:${colorDe(marca)}">${esc(marca)}</span>`; }
function semaforoHtml(cumple, etiqueta) {
  if (cumple === null || cumple === undefined) return `<span class="semaforo-none">○ sin dato</span>`;
  return cumple
    ? `<span class="semaforo-ok">● cumple mínimo${etiqueta ? " (" + esc(etiqueta) + ")" : ""}</span>`
    : `<span class="semaforo-bad">● no cumple mínimo${etiqueta ? " (" + esc(etiqueta) + ")" : ""}</span>`;
}
function metricHtml(label, value, help) {
  return `<div class="metric"><div class="label">${esc(label)}</div><div class="value">${esc(value)}</div>${help ? `<div class="help">${esc(help)}</div>` : ""}</div>`;
}
function optionsHtml(values, selected) {
  return values.map((v) => `<option value="${esc(v)}" ${v === selected ? "selected" : ""}>${esc(v)}</option>`).join("");
}
const ESTADO_PERIODO_POR_PREFIJO = {};
function registrarEstadoPeriodo(prefix, estado) { ESTADO_PERIODO_POR_PREFIJO[prefix] = estado; }

function periodoSelectorHtml(idPrefix, periodo, mesRef) {
  const mostrarMes = periodo === "ACUMULADO MES" || periodo === "ACUMULADO MES 2S";
  const lista = periodo === "ACUMULADO MES 2S" ? MESES_S2 : MESES;
  return `
    <div><label>Periodo</label><select id="${idPrefix}-periodo" data-onchange="periodoCambio" data-prefix="${idPrefix}">${optionsHtml(PERIODOS_COMPLETO, periodo)}</select></div>
    <div style="${mostrarMes ? "" : "display:none"}"><label>Hasta el mes de</label><select id="${idPrefix}-mesref" data-onchange="mesRefCambio" data-prefix="${idPrefix}">${optionsHtml(lista, mesRef)}</select></div>
  `;
}
// Importante: estos handlers guardan el valor elegido en el estado ANTES de
// volver a pintar la página -si no, el repintado reconstruye el <select>
// con el valor viejo y se pierde lo que el usuario acaba de elegir.
function periodoCambio(el) {
  const estado = ESTADO_PERIODO_POR_PREFIJO[el.dataset.prefix];
  estado.periodo = el.value;
  rerenderPage();
}
function mesRefCambio(el) {
  const estado = ESTADO_PERIODO_POR_PREFIJO[el.dataset.prefix];
  estado.mesRef = el.value;
  rerenderPage();
}
function leerPeriodo(idPrefix) {
  const periodo = document.getElementById(`${idPrefix}-periodo`).value;
  const mesRefEl = document.getElementById(`${idPrefix}-mesref`);
  const mesRef = mesRefEl ? mesRefEl.value : null;
  return { periodo, mesRef: (periodo === "ACUMULADO MES" || periodo === "ACUMULADO MES 2S") ? mesRef : null };
}

function simpleTableHtml(columnas, filas, opts) {
  opts = opts || {};
  const thead = `<tr>${columnas.map((c) => `<th>${esc(c)}</th>`).join("")}</tr>`;
  const tbody = filas.map((fila) => {
    const esDirecto = opts.directoCol !== undefined && fila[opts.directoCol] === "BMW DIRECTO";
    const tds = columnas.map((c) => `<td>${esc(fila[c])}</td>`).join("");
    return `<tr class="${esDirecto ? "row-directo" : ""}">${tds}</tr>`;
  }).join("");
  return `<div class="tablewrap"><table class="datatable"><thead>${thead}</thead><tbody>${tbody}</tbody></table></div>`;
}

function recordsToColumns(filas) {
  if (!filas.length) return [];
  return Object.keys(filas[0]);
}

function multiIndexTableHtml(tabla) {
  // tabla: {columnas: [[nivel0, nivel1], ...], filas: [[...], ...]}
  const cols = tabla.columnas;
  const groups = [];
  for (const [n0, n1] of cols) {
    if (groups.length && groups[groups.length - 1].n0 === n0 && n0 !== "") groups[groups.length - 1].span++;
    else groups.push({ n0, span: 1, n1s: [] });
    groups[groups.length - 1].n1s.push(n1);
  }
  const row1 = groups.map((g) => `<th colspan="${g.span}">${esc(g.n0)}</th>`).join("");
  const row2 = cols.map(([, n1]) => `<th>${esc(n1)}</th>`).join("");
  const rows = tabla.filas.map((fila) => {
    const esDirecto = fila[1] === "BMW DIRECTO";
    const tds = fila.map((v, i) => {
      const esPct = String(cols[i][1]).startsWith("%");
      const val = v === null || v === undefined ? "" : (esPct ? Number(v).toFixed(1) + "%" : v);
      return `<td>${esc(val)}</td>`;
    }).join("");
    return `<tr class="${esDirecto ? "row-directo" : ""}">${tds}</tr>`;
  }).join("");
  return `<div class="tablewrap"><table class="datatable"><thead><tr>${row1}</tr><tr>${row2}</tr></thead><tbody>${rows}</tbody></table></div>`;
}

function detailModal() {
  let dlg = document.getElementById("detail-modal");
  if (!dlg) {
    dlg = document.createElement("dialog");
    dlg.id = "detail-modal";
    dlg.className = "detail-modal";
    dlg.innerHTML = `<div class="dm-header"><strong id="dm-title"></strong><button class="linklike" data-action="closeModal">Cerrar ✕</button></div><div class="dm-body" id="dm-body"></div>`;
    document.body.appendChild(dlg);
  }
  return dlg;
}

function openDetailTable(title, tabla) {
  const dlg = detailModal();
  document.getElementById("dm-title").textContent = title + ` (${tabla.filas.length} vehículos)`;
  const cols = tabla.columnas;
  document.getElementById("dm-body").innerHTML = simpleTableHtml(cols, tabla.filas);
  dlg.showModal();
}

/* ------------------------------ navegación ------------------------------ */

const PAGES = {
  home: { label: "Home", render: renderHome },
  dashboard: { label: "Dashboard", render: renderDashboard },
  objetivos: { label: "Objetivos", render: renderObjetivos },
  ranking: { label: "Ranking", render: renderRanking },
  exportar: { label: "Exportar", render: renderExportar },
  detalle: { label: "Detalle", render: renderDetalle },
  seguimiento: { label: "Seguimiento", render: renderSeguimiento },
};
let currentPage = "home";

function wireNav() {
  document.querySelectorAll("#sidebar .navbtn").forEach((btn) => {
    btn.addEventListener("click", () => goPage(btn.dataset.page));
  });
}

function goPage(page) {
  if (page !== "home" && !APPSTATE.cargado) return;
  currentPage = page;
  document.querySelectorAll("#sidebar .navbtn").forEach((b) => b.classList.toggle("active", b.dataset.page === page));
  PAGES[page].render();
}

function rerenderPage() { PAGES[currentPage].render(); }

function unlockNav() {
  document.querySelectorAll("#sidebar .navbtn").forEach((b) => { b.disabled = false; });
  document.getElementById("sidebar-filename").textContent = APPSTATE.nombre ? "📄 " + APPSTATE.nombre : "";
}

/* ------------------------------ Home ------------------------------ */

function renderHome() {
  const content = document.getElementById("content");
  content.innerHTML = `
    <h2 class="pagetitle">📊 Seguimiento UC Retail &amp; Wholesale</h2>
    <p class="subtitle">Sube el archivo de ventas (hoja <strong>BBDD</strong>) y el resto de la app se calcula sola, sin tocar nada a mano.
    Todo corre en tu navegador -ni el archivo ni los datos salen de tu ordenador.</p>
    <div class="panel">
      <label>Archivo de ventas (.xlsx)</label>
      <input type="file" id="home-file" accept=".xlsx" data-onchange="homeFileChange">
      <div id="home-status"></div>
    </div>
    <div id="home-resumen"></div>
  `;
  if (APPSTATE.cargado) renderHomeResumen(callPy("resumen_home"));
}

async function homeFileChange(input) {
  const file = input.files[0];
  if (!file) return;
  document.getElementById("home-status").innerHTML = `<div class="alert alert-info">Leyendo ${esc(file.name)}…</div>`;
  const buf = await file.arrayBuffer();
  const bytes = new Uint8Array(buf);
  const r = callPy("cargar_archivo", file.name, bytes);
  if (!r.ok) {
    document.getElementById("home-status").innerHTML = `<div class="alert alert-error">${esc(r.error)}</div>`;
    return;
  }
  APPSTATE.cargado = true;
  APPSTATE.nombre = file.name;
  unlockNav();
  document.getElementById("home-status").innerHTML = `<div class="alert alert-ok">Cargadas ${r.vehiculos.toLocaleString("es-ES")} filas de venta.</div>`;
  renderHomeResumen(r);
}

function renderHomeResumen(r) {
  const porMarca = r.por_marca.map((fm) => `
    <div class="panel">
      ${brandbarHtml(fm.marca)}
      <div class="metricgrid">
        ${metricHtml("Retail", fm.retail)}
        ${metricHtml("BPS/MN", fm.bps)}
        ${metricHtml("Remarketing", fm.remarketing)}
        ${metricHtml("BEV", fm.bev)}
        ${metricHtml("Wholesale", fm.wholesale)}
      </div>
    </div>`).join("");
  document.getElementById("home-resumen").innerHTML = `
    <div class="panel">
      <div class="metricgrid">
        ${metricHtml("Vehículos vendidos", r.vehiculos.toLocaleString("es-ES"))}
        ${metricHtml("Concesionarios con ventas", r.concesionarios)}
        ${metricHtml("Meses cubiertos", r.meses.length)}
        ${metricHtml("Marcas", r.marcas.join(", "))}
      </div>
      <p class="caption">Meses detectados: ${esc(r.meses.join(", "))}</p>
      ${r.remarketing_disponible ? "" : `<div class="alert alert-info">ℹ️ "Retail origen Remarketing" no está disponible todavía -depende de la columna <strong>Canal Actual</strong>, que aún no trae el archivo.</div>`}
    </div>
    <div class="cols2">${porMarca}</div>
  `;
}

/* ------------------------------ Dashboard ------------------------------ */

let dashState = { concesionario: null, periodo: "ACUMULADO MES", mesRef: "JULIO" };
registrarEstadoPeriodo("dash", dashState);

function renderDashboard() {
  const opts = callPy("dashboard_opciones");
  if (!dashState.concesionario) dashState.concesionario = opts.concesionarios[0];
  const content = document.getElementById("content");
  content.innerHTML = `
    <h2 class="pagetitle">📈 Dashboard por concesionario</h2>
    <div class="panel row">
      <div><label>Concesión</label><select id="dash-concesionario" data-onchange="dashCambio">${optionsHtml(opts.concesionarios, dashState.concesionario)}</select></div>
      ${periodoSelectorHtml("dash", dashState.periodo, dashState.mesRef)}
    </div>
    <div id="dash-body"></div>
  `;
  document.getElementById("dash-periodo").value = dashState.periodo;
  renderDashboardBody();
}

function dashCambio() {
  dashState.concesionario = document.getElementById("dash-concesionario").value;
  rerenderPage();
}

function renderDashboardBody() {
  const { periodo, mesRef } = leerPeriodo("dash");
  dashState.periodo = periodo;
  dashState.mesRef = mesRef;
  const d = callPy("dashboard_datos", dashState.concesionario, periodo, mesRef);
  const body = document.getElementById("dash-body");
  body.innerHTML = `
    <p class="caption">Grupo propietario: <strong>${esc(d.grupo_propietario)}</strong> · Código dealer: <code>${d.codigo_dealer}</code></p>
    ${!d.remarketing_disponible ? `<div class="alert alert-info">ℹ️ "Retail origen Remarketing" no disponible -falta la columna Canal Actual.</div>` : ""}
    <div class="cols2" id="dash-marcas"></div>
  `;
  const cols = document.getElementById("dash-marcas");
  cols.innerHTML = d.marcas_disponibles.map((marca) => renderDashboardMarca(marca, d)).join("");
  wireDetailButtons(cols, d);
}

function renderDashboardMarca(marca, d) {
  const k = d.kpis[marca];
  const bono = k.bonificacion;
  let html = brandbarHtml(marca);
  html += `<p class="caption">Meses incluidos: ${esc(k.meses_incluidos.join(", "))}</p>`;

  if (d.es_bymycar) {
    const di = d.directos[marca] || {};
    html += `<div class="panel" style="background:#FFFBEF">
      <strong>🅱️ BMW DIRECTO</strong> <span class="caption">(ventas de BYMYCAR con Canal Actual "…DIRECTO")</span>`;
    if (d.remarketing_disponible) {
      html += `<div class="metricgrid">${metricHtml("Retail", di.retail)}${metricHtml("BPS/MN", di.bps)}${metricHtml("BEV", di.bev)}</div>
        <button class="linklike" data-action="verDetalle" data-marca="${marca}" data-metrica="retail" data-directo="1" data-titulo="BMW DIRECTO · Retail">Ver detalle Retail</button> ·
        <button class="linklike" data-action="verDetalle" data-marca="${marca}" data-metrica="bps" data-directo="1" data-titulo="BMW DIRECTO · BPS/MN">Ver detalle BPS/MN</button> ·
        <button class="linklike" data-action="verDetalle" data-marca="${marca}" data-metrica="bev" data-directo="1" data-titulo="BMW DIRECTO · BEV">Ver detalle BEV</button>`;
    } else {
      html += `<p class="caption">No disponible -depende de la columna Canal Actual.</p>`;
    }
    html += `</div>`;
  }

  html += `<div class="sectiontitle">Objetivo / Realizado Retail</div>
    <div class="metricgrid">
      ${metricHtml("Objetivo Retail", fmtNum(k.objetivo_retail))}
      ${metricHtml("Realizado Retail", fmtNum(k.realizado_retail))}
      ${metricHtml("% Cumplimentación ventas Retail", k.pct_cumplimiento_retail !== null ? fmtPct(k.pct_cumplimiento_retail, 0) : "sin objetivo")}
    </div>
    <button class="linklike" data-action="verDetalle" data-marca="${marca}" data-metrica="retail" data-titulo="Ventas Retail">🔎 Ver detalle</button>`;

  html += `<div class="sectiontitle">BPS / MN</div>
    <div class="metricgrid">
      ${metricHtml("Ventas BPS/MN", fmtNum(k.bps))}
      ${metricHtml("% BPS/MN sobre retail", fmtPct(k.pct_bps))}
    </div>
    <p>${semaforoHtml(k.cumple_penetracion_bps)} (mínimo 80%)</p>
    ${k.ventas_bps_necesarias_para_25pct > 0 ? `<p class="caption">Necesarias ≈ ${k.ventas_bps_necesarias_para_25pct} uds. BPS/MN más para acercarse al objetivo interno de penetración.</p>` : ""}
    <button class="linklike" data-action="verDetalle" data-marca="${marca}" data-metrica="bps" data-titulo="BPS / MN">🔎 Ver detalle</button>`;

  html += `<div class="sectiontitle">Retail origen Remarketing</div>`;
  if (d.remarketing_disponible) {
    html += `<div class="metricgrid">
      ${metricHtml("Ventas remarketing", fmtNum(k.remarketing))}
      ${metricHtml("% sobre objetivo retail", fmtPct(k.pct_remarketing))}
    </div>
    <details><summary class="caption">Uds. necesarias para alcanzar cada tramo de % remarketing</summary>
      ${k.bandas_remarketing_necesarias.map((b) => `<div class="caption">≥ ${fmtPct(b.umbral, 0)} → faltan <strong>${b.necesarias}</strong> uds.</div>`).join("")}
    </details>
    <button class="linklike" data-action="verDetalle" data-marca="${marca}" data-metrica="remarketing" data-titulo="Remarketing">🔎 Ver detalle</button>`;
  } else {
    html += `<p class="caption">No disponible -falta la columna Canal Actual en el archivo de ventas.</p>`;
  }

  html += `<div class="sectiontitle">BEV (todas las ventas BEV, Retail + Wholesale)</div>
    <div class="metricgrid">
      ${metricHtml("Ventas BEV", fmtNum(k.bev), `% BEV se calcula sobre el Objetivo Retail: ${fmtNum(k.objetivo_retail)}`)}
      ${metricHtml("% BEV sobre objetivo retail", fmtPct(k.pct_bev))}
    </div>
    <details><summary class="caption">Uds. necesarias para alcanzar cada tramo de % BEV</summary>
      ${k.bandas_bev_necesarias.map((b) => `<div class="caption">≥ ${fmtPct(b.umbral, 0)} → faltan <strong>${b.necesarias}</strong> uds.</div>`).join("")}
    </details>
    <button class="linklike" data-action="verDetalle" data-marca="${marca}" data-metrica="bev" data-titulo="BEV">🔎 Ver detalle</button>`;

  html += `<div class="sectiontitle">Ventas totales (Retail + Wholesale)</div>
    <div class="metricgrid">${metricHtml("Total vehículos vendidos", k.ventas_totales)}</div>
    <button class="linklike" data-action="verDetalle" data-marca="${marca}" data-metrica="ventas_totales" data-titulo="Ventas Totales">🔎 Ver detalle</button>`;

  html += `<div class="sectiontitle">Penetración de mercado (&lt;6 años)</div>`;
  if (k.mercado_menos_6_anos !== null && k.mercado_menos_6_anos !== undefined) {
    html += `<div class="metricgrid">
      ${metricHtml("Mercado <6 años", fmtNum(k.mercado_menos_6_anos))}
      ${metricHtml("% Penetración", fmtPct(k.pct_penetracion_mercado))}
    </div>`;
  } else {
    html += `<p class="caption">Sin dato de tamaño de mercado para este periodo -añádelo en "Objetivos y datos manuales".</p>`;
  }

  html += `<div class="sectiontitle">Mystery Shopping</div>`;
  if (k.mystery_shopping !== null && k.mystery_shopping !== undefined) {
    html += `<div class="metricgrid">${metricHtml("Puntuación", fmtNum(k.mystery_shopping, 1))}</div><p>${semaforoHtml(k.cumple_mystery_shopping)} (mínimo 90%)</p>`;
  } else {
    html += `<p class="caption">Sin dato de mystery shopping para este semestre -añádelo en "Objetivos y datos manuales".</p>`;
  }

  html += `<div class="sectiontitle">💰 Bonificación estimada</div>`;
  if (bono.total !== null && bono.total !== undefined) {
    html += `<div class="metricgrid">
      ${metricHtml("€ / vehículo (matriz x BEV)", fmtNum(bono.total, 2) + " €", `Base ${fmtNum(bono.base)} € x multiplicador BEV x${fmtNum(bono.multiplicador, 2)}`)}
      ${metricHtml("Ventas Retail + BPS/MN", fmtNum(k.bps))}
      ${metricHtml("Total a cobrar", bono.total_a_cobrar !== null ? fmtNum(bono.total_a_cobrar) + " €" : "—")}
    </div>`;
    if (k.cumple_penetracion_bps === false || k.cumple_mystery_shopping === false) {
      html += `<div class="alert alert-warn">⚠️ No cumple algún mínimo (penetración BPS/MN y/o Mystery Shopping) -puede que este importe no aplique.</div>`;
    }
  } else if (!d.remarketing_disponible) {
    html += `<p class="caption">No se puede calcular todavía -depende de "Retail origen Remarketing" (falta la columna Canal Actual).</p>`;
  } else {
    html += `<p class="caption">Sin objetivo o sin ventas suficientes para ubicarlo en la matriz de bonificación.</p>`;
  }
  html += `<details class="guide"><summary>📖 Ver guía de bonificación</summary>${k.guia_html || ""}</details>`;

  html += `<div class="sectiontitle">Evolución mensual</div>${evolucionChartHtml(d.evoluciones[marca], marca, d.remarketing_disponible)}`;

  return `<div>${html}</div>`;
}

function evolucionChartHtml(evo, marca, remarketingDisponible) {
  if (!evo || !evo.meses || !evo.meses.length) return `<p class="caption">Todavía no hay ventas cargadas para esta marca.</p>`;
  const serieObj = evo.series["Objetivo Retail"] || [];
  const serieReal = evo.series["Realizado Retail"] || [];
  const max1 = Math.max(1, ...serieObj, ...serieReal);
  const colorBase = colorDe(marca);
  const bars1 = evo.meses.map((m, i) => `
    <div class="bar-group">
      <div class="bars">
        <div class="bar" style="height:${(serieObj[i] / max1) * 90}px;background:${colorBase}55" title="Objetivo ${serieObj[i]}"></div>
        <div class="bar" style="height:${(serieReal[i] / max1) * 90}px;background:${colorBase}" title="Realizado ${serieReal[i]}"></div>
      </div>
      <div class="xlabel">${m.slice(0, 3)}</div>
    </div>`).join("");

  const otras = ["BPS/MN"].concat(remarketingDisponible ? ["Remarketing"] : []).concat(["BEV"]);
  const tonos = [colorBase, colorBase + "AA", colorBase + "66"];
  const max2 = Math.max(1, ...otras.flatMap((s) => evo.series[s] || []));
  const bars2 = evo.meses.map((m, i) => `
    <div class="bar-group">
      <div class="bars">
        ${otras.map((s, j) => `<div class="bar" style="height:${((evo.series[s] || [])[i] / max2) * 90}px;background:${tonos[j]}" title="${s} ${(evo.series[s] || [])[i]}"></div>`).join("")}
      </div>
      <div class="xlabel">${m.slice(0, 3)}</div>
    </div>`).join("");

  return `
    <div class="legend"><span><span class="dot" style="background:${colorBase}55"></span>Objetivo</span><span><span class="dot" style="background:${colorBase}"></span>Realizado</span></div>
    <div class="evo-chart">${bars1}</div>
    <div class="legend">${otras.map((s, j) => `<span><span class="dot" style="background:${tonos[j]}"></span>${esc(s)}</span>`).join("")}</div>
    <div class="evo-chart">${bars2}</div>
  `;
}

function wireDetailButtons(container, d) {
  container.querySelectorAll('[data-action="verDetalle"]').forEach((btn) => {
    btn.addEventListener("click", () => {
      const marca = btn.dataset.marca;
      const metrica = btn.dataset.metrica;
      const directo = btn.dataset.directo === "1";
      const meses = d.kpis[marca].meses_incluidos;
      const tabla = callPy("dashboard_detalle", dashState.concesionario, marca, meses, metrica, directo);
      openDetailTable(btn.dataset.titulo, tabla);
    });
  });
}

/* ------------------------------ Objetivos y datos manuales ------------------------------ */

let objState = { tab: "importar", marcaRetail: "BMW", marcaMercado: "BMW", marcaMys: "BMW", marcaAjustes: "BMW", metricaAjustes: "retail" };
let objImportPendiente = false;

function renderObjetivos() {
  const content = document.getElementById("content");
  const tabs = [["importar", "Importar objetivos"], ["retail", "Objetivos Retail"], ["mercado", "Mercado <6 años"], ["mys", "Mystery Shopping"], ["ajustes", "Ajustes manuales"]];
  content.innerHTML = `
    <h2 class="pagetitle">🎯 Objetivos y datos manuales</h2>
    <p class="subtitle">Estos datos no vienen en el archivo de ventas. Se guardan en este navegador (localStorage) y se reutilizan automáticamente en el Dashboard.</p>
    <div class="tabs">${tabs.map(([k, l]) => `<button class="${objState.tab === k ? "active" : ""}" data-action="objTab" data-tab="${k}">${esc(l)}</button>`).join("")}</div>
    <div id="obj-body" class="panel"></div>
  `;
  renderObjetivosBody();
}

function objTab(btn) { objState.tab = btn.dataset.tab; rerenderPage(); }

function renderObjetivosBody() {
  const body = document.getElementById("obj-body");
  if (objState.tab === "importar") { renderObjImportar(body); return; }
  if (objState.tab === "retail") { renderObjTablaSimple(body, "objetivos", objState.marcaRetail, MESES, "mes", "objetivos de retail", { metrica: "Retail" }, "marcaRetail"); return; }
  if (objState.tab === "mercado") { renderObjTablaSimple(body, "mercado_menos_6_anos", objState.marcaMercado, MESES, "mes", "tamaño de mercado <6 años", {}, "marcaMercado"); return; }
  if (objState.tab === "mys") { renderObjTablaSimple(body, "mystery_shopping", objState.marcaMys, ["S1", "S2"], "semestre", "mystery shopping", {}, "marcaMys"); return; }
  if (objState.tab === "ajustes") { renderObjAjustes(body); return; }
}

function marcaRadioHtml(name, selected) {
  return ["BMW", "MINI"].map((m) => `<label style="display:inline-block;margin-right:14px;font-size:13px"><input type="radio" name="${name}" value="${m}" ${m === selected ? "checked" : ""} data-onchange="objMarcaCambio" data-group="${name}"> ${m}</label>`).join("");
}
function objMarcaCambio(input) {
  objState[input.dataset.group] = input.value;
  rerenderPage();
}

function renderObjImportar(body) {
  body.innerHTML = `
    <p class="caption">Si ya tienes el Excel de seguimiento relleno, súbelo aquí y se copia todo de golpe: objetivos de Retail, tamaño de mercado &lt;6 años y mystery shopping.</p>
    <input type="file" accept=".xlsx" data-onchange="objImportFile">
    <div id="obj-import-resultado"></div>
  `;
}

async function objImportFile(input) {
  const file = input.files[0];
  if (!file) return;
  const buf = await file.arrayBuffer();
  const r = callPy("importar_seguimiento", new Uint8Array(buf));
  const div = document.getElementById("obj-import-resultado");
  if (!r.ok) { div.innerHTML = `<div class="alert alert-error">${esc(r.error)}</div>`; return; }
  objImportPendiente = true;
  let html = "";
  if (r.resumen.objetivos) html += `<div class="alert alert-ok">Objetivos: ${r.resumen.objetivos.reduce((a, x) => a + x.n, 0)} valores encontrados.</div>`;
  if (r.resumen.mercado) html += `<div class="alert alert-ok">Mercado &lt;6 años: ${r.resumen.mercado.reduce((a, x) => a + x.n, 0)} valores encontrados.</div>`;
  if (r.resumen.mystery_shopping) html += `<div class="alert alert-ok">Mystery Shopping: ${r.resumen.mystery_shopping.reduce((a, x) => a + x.n, 0)} valores encontrados.</div>`;
  html += `<button class="btn" data-action="objImportGuardar">💾 Guardar todo lo encontrado</button>`;
  div.innerHTML = html;
}

function objImportGuardar() {
  callPy("importar_guardar");
  document.getElementById("obj-import-resultado").innerHTML += `<div class="alert alert-ok">Guardado. Ya se está usando en el Dashboard.</div>`;
}

function renderObjTablaSimple(body, tabla, marca, columnas, colNombre, label, extraKeys, marcaKey) {
  const datos = callPy("objetivos_tabla", tabla, marca, columnas, colNombre, extraKeys);
  body.innerHTML = `
    ${marcaRadioHtml(marcaKey, marca)}
    ${badgeHtml(marca)}
    <div id="obj-editable"></div>
    <button class="btn" style="margin-top:10px" data-action="objGuardar" data-tabla="${tabla}" data-marca="${marca}" data-colnombre="${colNombre}" data-columnas='${esc(JSON.stringify(columnas))}' data-extrakeys='${esc(JSON.stringify(extraKeys))}'>💾 Guardar ${esc(label)} (${marca})</button>
    <span id="obj-guardado-msg"></span>
  `;
  document.getElementById("obj-editable").innerHTML = editableTableHtml(datos);
}

function editableTableHtml(datos) {
  const thead = `<tr><th>Código</th><th>Concesionario</th>${datos.columnas.map((c) => `<th>${esc(c)}</th>`).join("")}</tr>`;
  const tbody = datos.filas.map((fila, i) => `
    <tr>
      <td>${fila.codigo_dealer}</td><td>${esc(fila.concesionario)}</td>
      ${datos.columnas.map((c) => `<td><input type="number" step="any" data-row="${i}" data-col="${esc(c)}" value="${fila[c] ?? ""}"></td>`).join("")}
    </tr>`).join("");
  return `<div class="tablewrap editable-table"><table class="datatable"><thead>${thead}</thead><tbody>${tbody}</tbody></table></div>`;
}

function leerEditableTable(datos) {
  const filas = datos.filas.map((fila, i) => {
    const nueva = { codigo_dealer: fila.codigo_dealer, concesionario: fila.concesionario };
    datos.columnas.forEach((c) => {
      const input = document.querySelector(`#obj-editable input[data-row="${i}"][data-col="${CSS.escape(c)}"]`);
      const v = input && input.value !== "" ? Number(input.value) : null;
      nueva[c] = v;
    });
    return nueva;
  });
  return filas;
}

function objGuardar(btn) {
  const tabla = btn.dataset.tabla, marca = btn.dataset.marca, colNombre = btn.dataset.colnombre;
  const columnas = JSON.parse(btn.dataset.columnas), extraKeys = JSON.parse(btn.dataset.extrakeys);
  const datosActuales = { columnas, filas: leerEditableTableRaw(columnas) };
  const filas = leerEditableTable(datosActuales);
  callPy("objetivos_guardar", tabla, marca, columnas, colNombre, filas, extraKeys);
  document.getElementById("obj-guardado-msg").innerHTML = ` <span class="caption">✅ Guardado.</span>`;
}

function leerEditableTableRaw(columnas) {
  const rows = document.querySelectorAll("#obj-editable tbody tr");
  return Array.from(rows).map((tr) => {
    const codigo = Number(tr.children[0].textContent);
    const concesionario = tr.children[1].textContent;
    const fila = { codigo_dealer: codigo, concesionario };
    columnas.forEach((c) => { fila[c] = null; });
    return fila;
  });
}

function renderObjAjustes(body) {
  body.innerHTML = `
    <p class="caption">Corrige a mano un valor que la app calculó desde la BBDD, para algún mes concreto. Deja en blanco para seguir usando el calculado.</p>
    <div class="row">
      <div>${marcaRadioHtml("marcaAjustes", objState.marcaAjustes)}</div>
      <div><label>Métrica a corregir</label><select data-onchange="objMetricaCambio">${optionsHtml(Object.keys(METRICAS_AJUSTABLES), objState.metricaAjustes).replace(/value="(\w+)">(\w[^<]*)/g, "")}${Object.entries(METRICAS_AJUSTABLES).map(([k, v]) => `<option value="${k}" ${k === objState.metricaAjustes ? "selected" : ""}>${esc(v)}</option>`).join("")}</select></div>
    </div>
    <div id="obj-ajustes-calculado"></div>
    <div class="sectiontitle">Corrección manual</div>
    <div id="obj-editable"></div>
    <button class="btn" style="margin-top:10px" data-action="objGuardar" data-tabla="ajustes_manuales" data-marca="${objState.marcaAjustes}" data-colnombre="mes" data-columnas='${esc(JSON.stringify(MESES))}' data-extrakeys='${esc(JSON.stringify({ metrica: objState.metricaAjustes }))}'>💾 Guardar ajustes (${objState.marcaAjustes})</button>
    <span id="obj-guardado-msg"></span>
  `;
  const calc = callPy("objetivos_ajuste_calculado", objState.marcaAjustes, objState.metricaAjustes);
  document.getElementById("obj-ajustes-calculado").innerHTML = `<p><strong>Valor calculado desde la BBDD:</strong></p>` + simpleTableHtml(["concesionario", ...MESES], calc.filas);
  const datos = callPy("objetivos_tabla", "ajustes_manuales", objState.marcaAjustes, MESES, "mes", { metrica: objState.metricaAjustes });
  document.getElementById("obj-editable").innerHTML = editableTableHtml(datos);
}
function objMetricaCambio(sel) { objState.metricaAjustes = sel.value; rerenderPage(); }

/* ------------------------------ Ranking ------------------------------ */

let rankState = { marca: "BMW", periodo: "ACUMULADO MES", mesRef: "JULIO" };
registrarEstadoPeriodo("rank", rankState);

function renderRanking() {
  const content = document.getElementById("content");
  content.innerHTML = `
    <h2 class="pagetitle">🏆 Ranking de concesionarios</h2>
    <div class="panel row">
      <div>${marcaRadioHtml("rankMarca", rankState.marca)}</div>
      ${periodoSelectorHtml("rank", rankState.periodo, rankState.mesRef)}
    </div>
    <div id="rank-body"></div>
  `;
  document.querySelectorAll('[name="rankMarca"]').forEach((r) => r.addEventListener("change", (e) => { rankState.marca = e.target.value; rerenderPage(); }));
  renderRankingBody();
}

function renderRankingBody() {
  const { periodo, mesRef } = leerPeriodo("rank");
  rankState.periodo = periodo; rankState.mesRef = mesRef;
  const tabla = callPy("ranking_tabla", rankState.marca, periodo, mesRef);
  const body = document.getElementById("rank-body");
  if (!tabla.filas.length) { body.innerHTML = `<p class="caption">No hay concesionarios de esta marca en el maestro.</p>`; return; }
  const cols = ["concesionario", "grupo_propietario", "retail", "bps", "remarketing", "bev", "wholesale_uc", "wholesale_yuc", "% bps", "% remarketing", "% bev"];
  const colsExistentes = cols.filter((c) => tabla.columnas.includes(c));
  body.innerHTML = `
    ${simpleTableHtml(colsExistentes, tabla.filas)}
    <div class="sectiontitle">🔎 Ver detalle de vehículos</div>
    <div class="row">
      <div><label>Concesión</label><select id="rank-detalle-concesion">${optionsHtml(tabla.filas.map((f) => f.concesionario), null)}</select></div>
      <div><label>Métrica</label><select id="rank-detalle-metrica">${optionsHtml(Object.values(METRICAS_AJUSTABLES), null)}</select></div>
      <div style="display:flex;align-items:flex-end"><button class="btn secondary" data-action="rankVerDetalle">Ver</button></div>
    </div>
    <div id="rank-detalle-tabla"></div>
  `;
}

function rankVerDetalle() {
  const concesion = document.getElementById("rank-detalle-concesion").value;
  const metricaLabel = document.getElementById("rank-detalle-metrica").value;
  const metricaKey = Object.entries(METRICAS_AJUSTABLES).find(([, v]) => v === metricaLabel)[0];
  const tabla = callPy("ranking_tabla", rankState.marca, rankState.periodo, rankState.mesRef);
  const fila = tabla.filas.find((f) => f.concesionario === concesion);
  const det = callPy("ranking_detalle", fila.codigo_dealer, rankState.marca, rankState.periodo, rankState.mesRef, metricaKey);
  document.getElementById("rank-detalle-tabla").innerHTML = `<p class="caption">${det.filas.length} vehículos</p>` + simpleTableHtml(det.columnas, det.filas);
}

/* ------------------------------ Exportar ------------------------------ */

let exportState = { marca: "BMW", periodo: "ACUMULADO MES", mesRef: "JULIO" };
registrarEstadoPeriodo("export", exportState);

function renderExportar() {
  const content = document.getElementById("content");
  content.innerHTML = `
    <h2 class="pagetitle">⬇️ Exportar a Excel</h2>
    <p class="subtitle">Genera un .xlsx con el resumen tipo "Dealer Dashboard" para todos los concesionarios de una marca.</p>
    <div class="panel row">
      <div>${marcaRadioHtml("exportMarca", exportState.marca)}</div>
      ${periodoSelectorHtml("export", exportState.periodo, exportState.mesRef)}
    </div>
    <button class="btn" data-action="exportarGenerar">Generar Excel</button>
    <div id="export-status"></div>
  `;
  document.querySelectorAll('[name="exportMarca"]').forEach((r) => r.addEventListener("change", (e) => { exportState.marca = e.target.value; }));
}

function exportarGenerar() {
  const { periodo, mesRef } = leerPeriodo("export");
  exportState.periodo = periodo; exportState.mesRef = mesRef;
  const bytes = callPy("exportar_generar", exportState.marca, periodo, mesRef);
  const nombre = `Seguimiento_${exportState.marca}_${periodo.replace(/ /g, "_")}.xlsx`;
  downloadBytes(bytes, nombre, XLSX_MIME);
  document.getElementById("export-status").innerHTML = `<div class="alert alert-ok">Listo: se ha descargado ${esc(nombre)}.</div>`;
}

/* ------------------------------ Detalle de vehículos ------------------------------ */

function renderDetalle() {
  const dealers = callPy("dashboard_opciones").concesionarios;
  const content = document.getElementById("content");
  content.innerHTML = `
    <h2 class="pagetitle">🚗 Detalle de vehículos</h2>
    <p class="subtitle">La BBDD completa, vehículo a vehículo, filtrable por lo que te interese.</p>
    <div class="panel row">
      <div><label>Concesión</label><select id="det-concesion">${optionsHtml(["(todos)", ...dealers], "(todos)")}</select></div>
      <div><label>Marca</label><select id="det-marca">${optionsHtml(["(todas)", "BMW", "MINI"], "(todas)")}</select></div>
      <div><label>Mes</label><select id="det-mes" multiple size="3">${optionsHtml(MESES, null)}</select></div>
      <div><label>Métrica</label><select id="det-metrica">${optionsHtml(["(todas las ventas)", ...Object.values(METRICAS_AJUSTABLES)], "(todas las ventas)")}</select></div>
    </div>
    <div class="panel">
      <label>Buscar (chasis, matrícula, modelo…)</label>
      <input type="text" id="det-busqueda" placeholder="Escribe para filtrar…">
    </div>
    <button class="btn" data-action="detalleBuscar">Buscar</button>
    <button class="btn secondary" data-action="detalleDescargar">📥 Descargar esta vista en Excel</button>
    <div id="det-resultado"></div>
  `;
  detalleBuscar();
}

function detalleBuscar() {
  const concesion = document.getElementById("det-concesion").value;
  const marca = document.getElementById("det-marca").value;
  const meses = Array.from(document.getElementById("det-mes").selectedOptions).map((o) => o.value);
  const metricaLabel = document.getElementById("det-metrica").value;
  const metricaKey = metricaLabel === "(todas las ventas)" ? null : Object.entries(METRICAS_AJUSTABLES).find(([, v]) => v === metricaLabel)[0];
  const busqueda = document.getElementById("det-busqueda").value;
  const tabla = callPy("detalle_vehiculos", concesion, marca, meses, metricaKey, busqueda);
  document.getElementById("det-resultado").innerHTML = `<p class="caption">${tabla.filas.length.toLocaleString("es-ES")} vehículos</p>` + simpleTableHtml(tabla.columnas, tabla.filas);
}

function detalleDescargar() {
  const bytes = callPy("detalle_vehiculos_excel");
  downloadBytes(bytes, "detalle_vehiculos.xlsx", XLSX_MIME);
}

/* ------------------------------ Seguimiento UC Retail & Wholesale ------------------------------ */

let segState = { mesAcumulado: null, tab: null, agrupar: {}, prep: null };

function renderSeguimiento() {
  const content = document.getElementById("content");
  content.innerHTML = `
    <h2 class="pagetitle">🗂️ Seguimiento UC Retail &amp; Wholesale</h2>
    <p class="subtitle">Un apartado por cada pestaña del Excel original, separado por marca, con el mismo desglose mes a mes.</p>
    <div id="seg-aviso"></div>
    <div class="panel row">
      <div><label>"Acumulado Mes" hasta el mes de</label><select id="seg-mesacum" data-onchange="segMesAcumCambio">${optionsHtml(MESES, segState.mesAcumulado)}</select></div>
    </div>
    <div id="seg-tabs-wrap"></div>
    <div id="seg-tabla"></div>
    <hr>
    <div class="sectiontitle">📥 Descargar todo el Seguimiento</div>
    <p class="caption">Genera un único Excel con todas las pestañas de arriba (BMW y MINI).</p>
    <button class="btn" data-action="segExportarCompleto">Generar Excel completo</button>
    <div id="seg-export-status"></div>
    <hr>
    <div class="sectiontitle">📥 Descargar en el formato original (tu plantilla)</div>
    <div id="seg-plantilla"></div>
  `;
  const d = callPy("resumen_home");
  document.getElementById("seg-aviso").innerHTML = d.remarketing_disponible
    ? `<div class="alert alert-ok">✅ La columna Canal Actual está presente: "Retail origen Remarketing" se calcula con ella, y las ventas de BYMYCAR "…DIRECTO" aparecen como fila BMW DIRECTO.</div>`
    : `<div class="alert alert-info">ℹ️ Todavía no hay columna Canal Actual -"Retail origen Remarketing" sale en blanco y BMW DIRECTO siempre a 0.</div>`;

  const prep = callPy("seguimiento_preparar", segState.mesAcumulado || d.meses[d.meses.length - 1] || MESES[0]);
  segState.mesAcumulado = document.getElementById("seg-mesacum").value || prep.mes_por_defecto;
  document.getElementById("seg-mesacum").value = segState.mesAcumulado;
  segState.prep = prep;
  if (!segState.tab) segState.tab = `BMW__${prep.ordenes_tipos[0]}`;

  const tabsHtml = [];
  for (const marca of ["BMW", "MINI"]) {
    for (const tipo of prep.ordenes_tipos) {
      const key = `${marca}__${tipo}`;
      tabsHtml.push(`<button class="${segState.tab === key ? "active" : ""}" data-action="segTab" data-key="${key}">${esc(prep.titulos[tipo][marca])}</button>`);
    }
  }
  tabsHtml.push(`<button class="${segState.tab === "MAESTRO" ? "active" : ""}" data-action="segTab" data-key="MAESTRO">MAESTRO</button>`);
  document.getElementById("seg-tabs-wrap").innerHTML = `<div class="tabs">${tabsHtml.join("")}</div>`;

  renderSegTabla();
  renderSegPlantilla(d);
}

function segMesAcumCambio() { segState.mesAcumulado = document.getElementById("seg-mesacum").value; rerenderPage(); }
function segTab(btn) { segState.tab = btn.dataset.key; rerenderPage(); }

function renderSegTabla() {
  const wrap = document.getElementById("seg-tabla");
  if (segState.tab === "MAESTRO") {
    const tabla = callPy("seguimiento_maestro");
    wrap.innerHTML = simpleTableHtml(tabla.columnas, tabla.filas);
    return;
  }
  const [marca, tipo] = segState.tab.split("__");
  const agrupadoFijo = tipo === "grupo";
  const agrupar = agrupadoFijo ? true : !!segState.agrupar[segState.tab];
  let html = "";
  if (!agrupadoFijo) {
    html += `<label style="display:inline-block;margin-bottom:8px"><input type="checkbox" data-onchange="segAgruparCambio" ${agrupar ? "checked" : ""}> Agrupar por Grupo Propietario</label>`;
  }
  if (tipo === "wholesale") html += `<p class="caption">Pendiente de los datos que vas a pasar aparte para Wholesale -de momento se calcula UC/YUC desde la BBDD.</p>`;
  const tabla = callPy("seguimiento_tabla", marca, tipo, agrupar);
  html += multiIndexTableHtml(tabla);
  wrap.innerHTML = html;
}
function segAgruparCambio(chk) { segState.agrupar[segState.tab] = chk.checked; renderSegTabla(); }

function segExportarCompleto() {
  const bytes = callPy("seguimiento_exportar_completo", segState.agrupar);
  downloadBytes(bytes, "Seguimiento_UC_Retail_Wholesale_completo.xlsx", XLSX_MIME);
  document.getElementById("seg-export-status").innerHTML = `<div class="alert alert-ok">Listo.</div>`;
}

function renderSegPlantilla(d) {
  const div = document.getElementById("seg-plantilla");
  const disponible = callPy("seguimiento_plantilla_disponible");
  if (!disponible) { div.innerHTML = `<p class="caption">No hay plantilla cargada todavía en la app.</p>`; return; }
  const mesPorDefecto = d.meses.length ? d.meses[d.meses.length - 1] : MESES[0];
  div.innerHTML = `
    <p class="caption">Rellena tu propio archivo de seguimiento -mismo diseño, logos y agrupación por Distrito- con los datos ya calculados.</p>
    <div class="row">
      <div><label>Hasta el mes de</label><select id="seg-plantilla-mes">${optionsHtml(MESES, mesPorDefecto)}</select></div>
      <div style="display:flex;align-items:flex-end"><button class="btn" data-action="segExportarPlantilla">Generar Excel con tu plantilla</button></div>
    </div>
    <div id="seg-plantilla-status"></div>
  `;
}

function segExportarPlantilla() {
  const mes = document.getElementById("seg-plantilla-mes").value;
  const bytes = callPy("seguimiento_exportar_plantilla", mes);
  downloadBytes(bytes, `Seguimiento_UC_Retail_Wholesale_${mes}.xlsx`, XLSX_MIME);
  document.getElementById("seg-plantilla-status").innerHTML = `<div class="alert alert-ok">Listo.</div>`;
}

/* ------------------------------ eventos delegados ------------------------------ */

const ACTIONS = {
  closeModal: () => document.getElementById("detail-modal").close(),
  objTab, objImportGuardar, objGuardar,
  rankVerDetalle, exportarGenerar, detalleBuscar, detalleDescargar,
  segTab, segExportarCompleto, segExportarPlantilla,
};
const ONCHANGE = {
  homeFileChange, dashCambio, periodoCambio, mesRefCambio, rerenderPage, objMarcaCambio, objMetricaCambio,
  objImportFile, segMesAcumCambio, segAgruparCambio,
};

function wireDelegatedEvents() {
  document.getElementById("content").addEventListener("click", (e) => {
    const btn = e.target.closest("[data-action]");
    if (!btn) return;
    const fn = ACTIONS[btn.dataset.action];
    if (fn) fn(btn, e);
  });
  document.getElementById("content").addEventListener("change", (e) => {
    const el = e.target.closest("[data-onchange]");
    if (!el) return;
    const fn = ONCHANGE[el.dataset.onchange];
    if (fn) fn(el, e);
  });
  document.body.addEventListener("click", (e) => {
    const btn = e.target.closest("[data-action]");
    if (!btn || !btn.closest("dialog")) return;
    const fn = ACTIONS[btn.dataset.action];
    if (fn) fn(btn, e);
  });
}

boot();
