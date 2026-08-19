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
| Retail origen Remarketing | `Origen` contiene "Remarketing", dentro de Retail |
| BEV | `COMB` = "BEV", dentro de Retail |
| Wholesale UC / YUC | Ventas no-Retail, separadas por `YUC/UC` |

**Concesionario y agrupación temporal:** se usa `Código INT` (código de
concesionario) y `Fecha venta mes` (nombre del mes en español) tal
cual vienen en la BBDD.

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

**Objetivos:** no hace falta teclearlos a mano si ya los tienes en el
Excel de seguimiento original — la pestaña **"Importar objetivos"**
lee de un tirón las columnas OBJ/Objetivo de `UC BMW 2026 BPS`,
`UC MINI 2026 MINI NEXT`, `BEV BMW 2026` y `BEV MINI 2026`.

Esa misma página tiene una pestaña **"Ajustes manuales"** para corregir
a mano, mes a mes, cualquier valor que la app haya calculado desde la
BBDD (retail, BPS/MN, remarketing, BEV, wholesale UC/YUC) por si algún
mes hace falta arreglar algo puntual. Si dejas la casilla en blanco se
sigue usando el valor calculado; si escribes un número, ese número
manda para ese concesionario/mes.

## Ver el detalle vehículo a vehículo (como el Excel)

- **"Detalle de vehículos"**: la BBDD completa, con todas sus columnas
  originales (Chasis, Matrícula, Modelo, Vendedor, precios...),
  filtrable por concesión/marca/mes/métrica y con buscador.
- **"Ver detalle" en el Dashboard y el Ranking**: al lado de cada KPI
  (Retail, BPS/MN, Remarketing, BEV, Wholesale...) hay un botón que abre
  justo los vehículos que componen ese número -el equivalente a hacer
  doble click sobre la cifra en Excel.
- **"Detalle por pestaña"**: un apartado por cada pestaña del Excel
  original (UC BMW, BPS, BEV, Wholesale, igual para MINI, y MAESTRO),
  con el desglose mes a mes por concesionario -incluye la opción de
  agrupar por Grupo Propietario.

## Estructura del proyecto

```
app.py                          Home: carga del archivo de ventas
pages/
  1_Dashboard_Concesionario.py  Dashboard por concesionario + periodo (equivalente al "Dealer Dashboard"), con gráfico
  2_Objetivos_y_Datos_Manuales.py  Editor de objetivos / mystery shopping / mercado / ajustes / importar
  3_Ranking.py                  Ranking entre todos los concesionarios de una marca + detalle
  4_Exportar.py                 Genera y descarga el Excel de salida
  5_Detalle_Vehiculos.py        BBDD completa filtrable, vehículo a vehículo
  6_Detalle_por_Pestana.py      Desglose mensual por concesionario, una pestaña por cada apartado del Excel original
src/
  ingest.py     Lectura y limpieza de la BBDD + reglas de negocio (conserva todas las columnas originales)
  metrics.py    Agregados por concesionario/marca/mes + selección de periodo + ajustes manuales
  dashboard.py  KPIs completos (con objetivos, bandas de "ventas necesarias", evolución mensual, etc.)
  detail.py     Filtra la BBDD a nivel de vehículo para el "doble click" sobre un KPI
  importer.py   Importa los objetivos (OBJ) desde el Excel de seguimiento original
  storage.py    Persistencia SQLite de objetivos y datos manuales
  export.py     Generación del Excel descargable
  dealers.py    Maestro de concesionarios (extraído del Excel original)
  config.py     Constantes de negocio (meses, periodos, métricas)
data/
  dealers.csv   Maestro de ~53 concesionarios BMW/MINI (código, nombre, grupo propietario)
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
