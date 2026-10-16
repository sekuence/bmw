# Instagram (@healthyanii)

Carpeta dedicada al análisis de la cuenta de Instagram de Ana Moreno. Es independiente del resto del repositorio (la app de seguimiento de concesionarios).

## Estructura

```
instagram/
├── README.md
├── analisis.py                 # Genera informes/tablas.md a partir de data/
├── data/
│   ├── perfil.json             # Bio, seguidores, top ciudades
│   ├── publicaciones.csv       # 91 publicaciones (18-abr → 15-oct-2026) con métricas + tema/CTA
│   ├── diario_30d.csv          # Métricas diarias de la cuenta (últimos 30 días)
│   ├── audiencia_genero_edad.csv
│   └── audiencia_paises.csv
└── informes/
    ├── 01_diagnostico_2026-10.md   # Informe principal: hallazgos y recomendaciones
    └── tablas.md                   # Tablas generadas por analisis.py
```

## Uso

```bash
python instagram/analisis.py
```

Solo requiere `pandas`. Los datos se extraen de la Instagram Graph API (vía Windsor.ai). Las columnas `tema`, `cta` y `palabra_clave` de `publicaciones.csv` están clasificadas a mano y se pueden ajustar.

## Glosario de métricas

- **alcance**: cuentas únicas que vieron la publicación.
- **er_alcance**: (likes + comentarios + guardados + compartidos) / alcance.
- **skip_rate**: % de reproducciones de un reel abandonadas en los primeros 3 segundos.
- **ver_medio_ms**: tiempo medio de visualización del reel, en milisegundos.
