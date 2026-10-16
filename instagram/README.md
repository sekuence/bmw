# Instagram (@healthyanii)

Carpeta dedicada al análisis y crecimiento de la cuenta de Instagram de Ana Moreno. Es independiente del resto del repositorio.

**Dashboard:** https://claude.ai/artifact/6LfPXMoTNUS54RhWEuPXyn (privado; se genera con `generar_dashboard.py`)

## Estructura

```
instagram/
├── analisis.py               # Tablas de 12 meses → informes/tablas.md
├── importar_windsor.py       # JSON de Windsor (data/raw/) + CSV manuales → data/publicaciones_12m.csv
├── evaluar_experimento.py    # Cruza plan/calendario.csv con los datos → plan/resultados.md
├── generar_dashboard.py      # → dashboard.html
├── outliers.py               # Múltiplo sobre la mediana propia → informes/outliers.md
├── voz.md                    # voice.md para los skills ig-* (borrador, revisar [CONFIRMAR])
├── data/
│   ├── publicaciones_12m.csv           # 191 publicaciones (16-oct-2025 → 15-oct-2026), fuente principal
│   ├── publicaciones.csv               # 18-abr → 15-oct-2026, clasificado a mano
│   ├── publicaciones_2026-01-18_04-17.csv
│   ├── clasificacion_manual.csv        # Tema corregido a mano de las publicaciones importadas desde JSON
│   ├── raw/                            # Exportaciones JSON de Windsor.ai tal cual
│   ├── diario_30d.csv, audiencia_*.csv, perfil.json
├── informes/
│   ├── 01_diagnostico_2026-10.md       # Diagnóstico inicial (6 meses)
│   ├── 02_investigacion_12m_y_nicho.md # 12 meses + qué funciona en el nicho (con fuentes)
│   └── tablas.md
└── plan/
    ├── plan_experimento_4_semanas.md   # Plan 19-oct → 15-nov: 20 publicaciones con guion, gancho y CTA
    ├── calendario.csv                  # El mismo plan en datos; rellenar shortcode/leads al publicar
    └── resultados.md                   # Estado de cada hipótesis (generado)
```

## Skills de Instagram

En `.claude/skills/ig-*` está instalado el paquete [instagram-agent-skill](https://github.com/Jakeschincariol/instagram-agent-skill) (MIT, commit d03c56b). Son 13 skills y no necesitan red. Para usarlos con tu voz: `mkdir -p ~/.claude/instagram && cp instagram/voz.md ~/.claude/instagram/voice.md`.

**Aviso:** `hookscore.py` está calibrado para inglés y no predice el alcance de @healthyanii (validado con 137 reels: ρ = 0,15). Usa sus guías de estructura, pero no su nota.

## Rutina semanal (lunes)

1. Volcar en `data/raw/` el JSON de Windsor con las publicaciones nuevas (los mismos campos que los existentes).
2. Rellenar en `plan/calendario.csv` el `shortcode` de lo publicado y los leads/ventas de la hoja de DM.
3. Ejecutar:
   ```bash
   python instagram/importar_windsor.py
   python instagram/analisis.py
   python instagram/evaluar_experimento.py
   python instagram/generar_dashboard.py
   ```

Solo requiere `pandas`.

## Glosario

- **alcance**: cuentas únicas que vieron la publicación.
- **er_alcance**: (likes + comentarios + guardados + compartidos) / alcance.
- **skip_rate**: % de reproducciones de un reel abandonadas en los primeros 3 segundos.
- **ver_medio_ms**: tiempo medio de visualización del reel, en milisegundos.
