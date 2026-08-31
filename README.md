# Seguimiento UC Retail & Wholesale — generador automático

App que sustituye el proceso manual de rellenar el Excel
`SEGUIMIENTO UC RETAIL & WHOLESALE` a partir del archivo de ventas
(`Cierre_ventas_YTD...xlsx`, hoja `BBDD`). Subes el archivo de ventas y
la app calcula solo el dashboard por concesionario y periodo, el
ranking entre concesionarios, y genera un Excel descargable.

## Cómo funciona (resumen)

```
Archivo de ventas (BBDD)  →  limpieza + reglas de negocio (src/ingest.py)
                           →  agregados por concesionario/marca/mes (src/metrics.py)
                           →  + objetivos y datos manuales guardados (src/storage.py)
                           →  Dashboard / Ranking / Excel (app.py + pages/)
```

## Ejecutar en local

```bash
pip install -r requirements.txt
streamlit run app.py
```

Abre `http://localhost:8501`, sube el archivo de ventas desde el panel
izquierdo y navega por las páginas del menú lateral.

## Qué se calcula automáticamente desde la BBDD

| Métrica | Regla aplicada sobre la hoja `BBDD` |
|---|---|
| Ventas Retail | `Motivo venta` = "Retail" |
| BPS / MN | `BPS FISCALGES` = "Sí", dentro de las ventas Retail |
| Retail origen Remarketing | Ver más abajo -**sólo** con la columna `Canal Actual`- |
| BEV | `COMB` = "BEV" -**todas** las ventas BEV, Retail + Wholesale- |
| Wholesale UC / YUC | Ventas no-Retail, separadas por `YUC/UC` |

**Concesionario y agrupación temporal:** se usa `Código INT` (código de
concesionario) y `Fecha venta mes` (nombre del mes en español) tal
cual vienen en la BBDD.

**Sobre qué se calculan los porcentajes** (igual que en el Excel
original): **% BPS/MN** es sobre el Realizado de Retail; **% Retail
origen Remarketing** y **% BEV** son sobre el **Objetivo** de Retail,
no sobre el Realizado.

### Regla BYMYCAR / BMW DIRECTO y Remarketing (pendiente de la columna `Canal Actual`)

**"Retail origen Remarketing" sólo se calcula con la columna
`Canal Actual`.** Mientras esa columna no exista en el archivo de
ventas (todavía no existe, pero existirá), la app **no inventa un
valor alternativo**: lo muestra como "no disponible" en el Dashboard y
en blanco en "Seguimiento UC Retail & Wholesale", y la Bonificación
estimada tampoco se puede calcular (depende de ese %).

En cuanto subas un archivo que ya traiga `Canal Actual`, la app la
detecta sola (no hay que tocar nada) y activa:

1. De las ventas de **BYMYCAR**, las que tengan `Canal Actual`
   conteniendo "DIRECTO" dejan de contar en el Retail/BPS/BEV normal
   de BYMYCAR -**no existe un concesionario "BMW DIRECTO" en la BBDD**
   (ni código propio ni ese nombre): sigue siendo BYMYCAR, sólo que esas
   ventas se cuentan aparte-. Se muestran en dos sitios:
   - **Dashboard**: un apartado "BMW DIRECTO" dentro de la vista de BYMYCAR.
   - **Seguimiento UC Retail & Wholesale**: una fila más llamada
     "BMW DIRECTO" al final de cada tabla por concesionario (no en las
     vistas agrupadas por Grupo Propietario, porque no pertenece a
     ningún grupo).
2. **Retail origen Remarketing** = toda venta Retail que cumpla **las
   tres** condiciones:
   a. `Canal Actual` no está vacío ni es un error de fórmula (`#N/D`,
      `#N/A`, `-`, en blanco...) -si está vacío o en error, **no**
      cuenta como remarketing.
   b. `Canal Actual` no es de tipo **MOBILITY, LANDING, DIRECTO o
      DIRECT_SALES** (se busca el patrón dentro del texto, p.ej.
      `rmk_car_mobility` o `rmk_cars_retail_directo` quedan excluidos).
   c. Y, si el archivo trae también la columna **`V o F Formulada`**
      (mismo grupo propietario del concesionario comprador y del
      vendedor -viene ya calculada, la app no la recalcula-), que
      valga **Verdadero**. Si el comprador es de otro grupo, esa venta
      no cuenta como remarketing aunque el canal sea válido. Igual que
      `Canal Actual`, esta columna es opcional: si el archivo no la
      trae todavía, la regla sólo aplica los puntos a) y b).

Los nombres exactos de columna y los patrones de texto están
centralizados en `src/config.py` (`COLUMNA_CANAL_ACTUAL`,
`PATRONES_CANAL_EXCLUIDOS_REMARKETING`, `VALORES_CANAL_VACIO`,
`COLUMNA_MISMO_GRUPO`, `VALORES_MISMO_GRUPO_TRUE`) -ajústalos ahí si el
nombre real de la columna en tu BBDD (p.ej. `V o F Formulada`) acaba
siendo distinto al del archivo de ejemplo que se usó para definir la regla.

## Qué se sigue introduciendo a mano (y por qué)

El Excel original obtiene estos datos de **otros archivos externos**
que llegan cada mes por separado (se puede ver en sus vínculos
externos: `AUTOMATIZACION VENTAS.xlsx`, ficheros de `Penetración de
Mdo_[mes].xlsx`, `MYS VO BMW_MINI.xlsx`, objetivos que pasa Germán a
mano...). No están en la BBDD de ventas, así que **no se pueden
calcular solos**:

- **Objetivos** (Retail y BEV) por concesionario/marca/mes.
- **Mystery Shopping**, por concesionario/marca/semestre.
- **Tamaño de mercado &lt;6 años**, para calcular el % de penetración.

Se introducen en la página **"Objetivos y datos manuales"** y quedan
guardados en `data/app.db` (SQLite) para los próximos meses — no hay
que volver a escribirlos cada vez que subes un archivo de ventas
nuevo.

**Objetivos:** vienen **precargados de fábrica** (`data/objetivos_default.csv`,
extraído del Excel de seguimiento que ya nos pasaste) — no hace falta
importar nada para verlos en el Dashboard. Cuando tengas objetivos
nuevos de un mes futuro, actualízalos desde la pestaña **"Importar
objetivos"** (lee de un tirón las columnas OBJ/Objetivo de
`UC BMW 2026 BPS`, `UC MINI 2026 MINI NEXT`, `BEV BMW 2026` y
`BEV MINI 2026` de un Excel de seguimiento) o a mano en "Objetivos
Retail" / "Objetivos BEV".

Esa misma página tiene una pestaña **"Ajustes manuales"** para corregir
a mano, mes a mes, cualquier valor que la app haya calculado desde la
BBDD (retail, BPS/MN, remarketing, BEV, wholesale UC/YUC) por si algún
mes hace falta arreglar algo puntual. Si dejas la casilla en blanco se
sigue usando el valor calculado; si escribes un número, ese número
manda para ese concesionario/mes.

## Colores de marca y bonificación

Toda la app distingue **BMW (azul) de MINI (naranja)** con la misma
paleta en cabeceras, pestañas y etiquetas -Dashboard, Ranking,
Seguimiento y Objetivos-, igual que en el Excel original.

El **Dashboard por concesionario** incluye además, por marca:

- Semáforo (verde/rojo) de los dos mínimos exigidos: **penetración
  BPS/MN ≥ 80%** y **Mystery Shopping ≥ 90%**.
- **Bonificación estimada**: € por vehículo según la matriz de
  cumplimiento objetivo Retail x % Retail origen Remarketing,
  multiplicado por el multiplicador de % BEV, y ese importe **x el
  número de ventas Retail realizadas = total a cobrar** -con aviso si
  no se cumple alguno de los dos mínimos-. No se puede calcular sin la
  columna `Canal Actual` (depende de "Retail origen Remarketing").
- Un desplegable **"📖 Ver guía de bonificación"** con las 4 tablas de
  referencia (mínimos, matriz de bonificación, multiplicador BEV y
  Mystery Shopping) tal cual las del Excel original.

Estas tablas están centralizadas en `src/bonus.py` -ajústalas ahí si
cambian los importes o los tramos-.

## Ver el detalle vehículo a vehículo (como el Excel)

- **"Detalle de vehículos"**: la BBDD completa, con todas sus columnas
  originales (Chasis, Matrícula, Modelo, Vendedor, precios...),
  filtrable por concesión/marca/mes/métrica y con buscador.
- **"Ver detalle" en el Dashboard y el Ranking**: al lado de cada KPI
  (Retail, BPS/MN, Remarketing, BEV, Wholesale...) hay un botón que abre
  justo los vehículos que componen ese número -el equivalente a hacer
  doble click sobre la cifra en Excel.
- **"Seguimiento UC Retail & Wholesale"**: 13 pestañas -por cada marca:
  UC 2026 (sólo Objetivo/Realizado Retail), UC (Retail + BPS/M-NEXT),
  BEV, Wholesale, Grupo Propietario y Penetración de mercado-, más
  Maestro. Columnas agrupadas por mes (igual que en el Excel, no
  repetidas celda a celda) y, a la derecha del todo, los acumulados
  **Acum. Mes** (con selector de "hasta qué mes"), **Anual**,
  **Semestre 1** y **Semestre 2** -igual que en el Excel original-.
  Los concesionarios salen **en el mismo orden y agrupados por
  distrito** que en el Excel original (columna "Distrito" incluida),
  no alfabéticamente. Un botón **"📥 Descargar todo el Seguimiento"**
  genera un único Excel con las 13 pestañas tal cual se ven en la app,
  con cabecera del color de la marca (azul BMW / naranja MINI), filas
  con bandas, bordes y porcentajes con formato -no es una réplica
  pixel a pixel del Excel original (para eso habría que partir de tu
  archivo como plantilla, ver nota de más abajo), pero se lee como una
  tabla real, no como un volcado de datos.

**Nota:** si en el futuro quieres que la descarga sea *literalmente*
tu archivo de seguimiento original actualizado con los datos nuevos
(mismo diseño exacto, logos incluidos), es posible partiendo de tu
Excel como plantilla, pero con dos peros: hay que subir esa plantilla
cada vez, y al guardarla se rompen los vínculos a los 9 archivos
externos que trae (Motorflash, penetración de mercado, MYS...). No
está implementado todavía -se decidió priorizar la versión actual,
más simple y sin depender de conservar ningún archivo aparte-.

## Estructura del proyecto

```
app.py                          Home: carga del archivo de ventas
pages/
  1_Dashboard_Concesionario.py  Dashboard por concesionario + periodo (equivalente al "Dealer Dashboard"), con gráfico
  2_Objetivos_y_Datos_Manuales.py  Editor de objetivos / mystery shopping / mercado / ajustes / importar
  3_Ranking.py                  Ranking entre todos los concesionarios de una marca + detalle
  4_Exportar.py                 Genera y descarga el Excel de salida
  5_Detalle_Vehiculos.py        BBDD completa filtrable, vehículo a vehículo
  6_Seguimiento_UC_Retail_Wholesale.py  Réplica del Excel original: una pestaña por apartado, separado por marca
src/
  ingest.py     Lectura y limpieza de la BBDD + reglas de negocio (conserva todas las columnas originales)
  metrics.py    Agregados por concesionario/marca/mes + selección de periodo + ajustes manuales
  dashboard.py  KPIs completos (con objetivos, bandas de "ventas necesarias", evolución mensual, etc.)
  detail.py     Filtra la BBDD a nivel de vehículo para el "doble click" sobre un KPI
  importer.py   Importa los objetivos (OBJ) desde el Excel de seguimiento original
  storage.py    Persistencia SQLite de objetivos y datos manuales
  export.py     Generación del Excel descargable (resumen tipo Dealer Dashboard)
  export_seguimiento.py  Generación del Excel completo de "Seguimiento UC Retail & Wholesale" (13 pestañas)
  dealers.py    Maestro de concesionarios (extraído del Excel original)
  config.py     Constantes de negocio (meses, periodos, métricas)
  bonus.py      Matriz de bonificación, mínimos y multiplicador BEV
  guia.py       HTML de las tablas-guía de bonificación
  theme.py      Colores de marca (azul BMW / naranja MINI) para toda la app
data/
  dealers.csv   Maestro de ~52 concesionarios BMW/MINI (código, nombre, grupo propietario)
  app.db        (se crea solo) objetivos y datos manuales
```

## Periodos soportados

Mes suelto, Trimestre 1-4, Semestre 1, Semestre 2, Acumulado Mes (enero
→ mes elegido), Acumulado Mes 2ª mitad (julio → mes elegido) y Anual —
igual que el selector del Excel original.

## Siguientes pasos posibles

- **Hostear online**: esta app ya está lista para
  [Streamlit Community Cloud](https://streamlit.io/cloud) (gratis) —
  solo hay que conectar el repo. Para un uso con más de un usuario a
  la vez conviene cambiar `src/storage.py` de SQLite a una base de
  datos real (Postgres); el resto de la app no cambia.
- **Réplica de más pestañas** del Excel original (Wholesale detallado,
  Grupo Propietario, Penetración con TOP 10, etc.) — no incluidas en
  esta primera versión porque dependen de archivos externos que no
  estaban disponibles al construirla.
- **Autenticación por concesionario**, si cada uno debe ver sólo sus
  propios datos.
