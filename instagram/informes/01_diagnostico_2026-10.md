# Diagnóstico de @healthyanii (octubre 2026)

**Periodo analizado:** 91 publicaciones del 18 de abril al 15 de octubre de 2026, más métricas diarias del 16 de septiembre al 15 de octubre y la audiencia actual.
**Fuente:** Instagram Graph API (vía Windsor.ai), extraída el 16-10-2026.
> **Actualización:** el [informe 02](02_investigacion_12m_y_nicho.md) amplía el análisis a 12 meses y corrige el punto 3.7: sí hubo carruseles educativos que fueron virales ("Pisada", con 141k de alcance).

**Tablas completas:** [`tablas.md`](tablas.md), que se regenera con `python instagram/analisis.py`.

---

## 1. Foto actual

| | |
|---|---|
| Seguidores | **37.007** |
| Seguidos | 3.932 |
| Publicaciones totales | 1.822 |
| Bio | "Embajadora @asicsfrontrunner · Te convierto en corredor en 90 días · +300 personas ya lo lograron con mi método" |
| Link | healthyani.com/runmind |
| Alcance diario medio (30 d) | **12.247 cuentas** |
| Nuevos seguidores (30 d) | **2.420** (≈83/día, un 6,5 % de crecimiento mensual) |
| Formato | 84 de 91 publicaciones son reels |

## 2. Quién te sigue

- **Mujeres, 58,5 %.** Hombres 30,7 % y sin especificar 10,8 %.
- **Edad: 35–54 años, 64 %.** Por tramos: 35–44 un 34,2 %, 45–54 un 29,8 %, 25–34 solo un 17,9 % y menores de 25 apenas un 2,4 %.
- El segmento más grande es **mujeres de 35 a 44 años (7.647)**, seguido de **mujeres de 45 a 54 (6.049)**.
- **Latinoamérica, 82 %:** Venezuela 19,7 %, México 12,5 %, Argentina 12,4 %, Colombia 10,1 %, Chile 5,3 %. España tiene un 7,9 % y EE. UU. un 6,7 %.
- **Ciudades principales:** Caracas (2.019), Santiago de Chile, Bogotá, CDMX, Lima, Maracaibo y Madrid.

> **Lectura:** tu cliente ideal no es un runner joven y competitivo. Es una **mujer latina de 35 a 55 años que empieza o retoma el ejercicio**, con dolores o miedo a lesionarse. Encaja con la promesa de la bio ("te convierto en corredor en 90 días"), pero no tanto con el contenido de marca y de competición (Mundial, pacer, Majors).

## 3. Hallazgos clave

### 3.1 Creces por descubrimiento, pero tus seguidores apenas te ven
- El **89 % del alcance viene de no seguidores**. El algoritmo te distribuye bien hacia fuera.
- Al día solo llegas a unas **1.342 personas que ya te siguen, un 3,6 % de tu base**.
- Por cada 1.000 cuentas alcanzadas ganas **6,8 seguidores**.
- **Implicación:** el crecimiento depende de los virales. Cuando no hay un viral, el alcance cae a 7–10 mil y el ritmo de seguidores baja. De 95/día en la segunda quincena de septiembre has pasado a 71/día en octubre, y el último viral fue la publicación de postura del 28 de septiembre.

### 3.2 Lo que se vuelve viral es educativo y "guardable"
**Todo tu top 12 es contenido educativo práctico.** Ninguna publicación personal, de marca ni de venta entra en él.

| Fecha | Publicación | Alcance | Guardados | Compartidos |
|---|---|---|---|---|
| 14-ago | Periostitis tibial: 3 ejercicios | **199.220** | 5.005 | 2.368 |
| 02-sep | Plan para correr 30 min sin parar | **161.532** | 5.952 | 2.195 |
| 04-may | Rutina de pliometría | **138.759** | 8.556 | 3.254 |
| 02-jun | Pliometría (republicada) | 108.354 | 6.882 | 2.123 |
| 09-jun | Qué comer antes de correr | 82.418 | 1.622 | 1.505 |
| 03-ago | Tipo de pisada y zapatillas | 76.042 | 2.312 | 1.363 |
| 01-jul | Fuerza para corredores (comenta FUERZA) | 64.452 | 1.931 | 593 |
| 12-ago | 2 gestos para correr más eficiente | 55.777 | 1.188 | 403 |

Mediana de alcance por tema:

| Tema | Publicaciones | Alcance mediano | Guardados / alcance |
|---|---|---|---|
| Técnica de carrera | 10 | **37.104** | 1,3 % |
| Fuerza / ejercicios | 8 | 12.152 | **3,4 %** |
| Lesiones / dolor | 8 | 6.356 | 1,5 % |
| Principiantes / planes | 9 | 5.328 | 0,7 % |
| Personal (viajes, Boston) | 11 | 4.869 | 0,1 % |
| Marca / ASICS / eventos | 14 | **3.510** | 0,1 % |
| Venta directa | 4 | 2.991 | 0,4 % |
| Mentalidad | 5 | 2.144 | 0,6 % |

- **Lo que más se relaciona con el alcance son los guardados (ρ = 0,47) y los compartidos (ρ = 0,42).** Pesan más que el tiempo de visualización (0,29). Un contenido que alguien quiere guardar para hacerlo después ("3 ejercicios", "rutina", "plan") es tu mejor palanca.
- La **marca y los eventos** son tu categoría más numerosa (14 publicaciones) y la que peor rinde: 8,9 s de visualización media y un 51 % de abandono en los primeros 3 segundos. Encaja en tu papel de embajadora, pero no te hace crecer.

### 3.3 El "Comenta PALABRA" funciona como embudo y penaliza el alcance
- El **80 % de tus comentarios (5.262 de 6.535)** llega de publicaciones con "Comenta X". Esos comentarios son leads por DM.
- Esas publicaciones tienen un **alcance mediano de 4.157**, frente a **8.013 con "Sígueme"**. El porcentaje de comentarios se relaciona *negativamente* con el alcance (ρ = −0,25).
- Hay excepciones muy valiosas: **Postura** (45.939 de alcance y 1.006 comentarios), **Fuerza** (64.452 y 1.694) y **30 min sin parar** (161.532 y 453). Tienen en común que **primero entregan un valor enorme en el vídeo y la palabra clave viene después**.
- Los reels que **solo venden** ("Comenta TRANSFORMACIÓN", 662 de alcance; "Comenta CLASE" de mentalidad, 1.995) son los peores de la cuenta.
- **Implicación:** el CTA de comentario debe ir sobre un contenido viral en sí mismo, como un bonus ("si quieres el plan completo, comenta PLAN"), y no ser el motivo del vídeo.

### 3.4 Republicar funciona, pero no con días de diferencia
| Contenido | 1.ª vez | Republicado | Separación |
|---|---|---|---|
| Pliometría | 138.759 | 108.354 → 10.183 | 4 semanas → 6 semanas más |
| Qué comer antes de correr | 82.418 | 5.326 | **2 días** |
| Correr con calor | 37.627 | 3.394 | **1 día** |

- **Implicación:** tus mejores reels pueden repetirse con éxito si pasan unas 4 semanas, mejor con otro gancho o portada. Repetirlos a 1–2 días no aporta nada.

### 3.5 Los primeros 3 segundos marcan la diferencia
| Abandono en los primeros 3 s (skip rate) | Reels | Alcance mediano |
|---|---|---|
| < 40 % | 16 | **12.966** |
| 40–45 % | 22 | 5.228 |
| 45–50 % | 22 | 5.098 |
| > 50 % | 24 | 4.227 |

- En el último trimestre el abandono mediano **empeoró de 43,9 % a 47,9 %**.
- El reel con mejor retención (pisada y zapatillas: 31 % de abandono y 28,5 s de visualización media) es también uno de los que más alcance tienen.

### 3.6 Captions genéricos
- Hay 9 reels cuyo caption es solo "Sígueme @healthyanii para más contenido como este". **No dicen de qué trata el vídeo.**
- Instagram ya usa el texto del caption para la búsqueda y para clasificar el tema. Un caption sin palabras clave ("periostitis", "correr 5 km", "respiración al correr") pierde esa distribución.

### 3.7 Formato y calendario
- **Carruseles:** 7 en 6 meses, todos personales o de marca. Tienen el engagement más alto (12,9 %) pero poco alcance (1.900). **Nunca has probado un carrusel educativo**, que es el formato que más se guarda en Instagram.
- **Días:** lunes, miércoles y sábado tienen la mediana más alta y el domingo la más baja (2.831). La muestra es pequeña, tómalo como tendencia.
- **Hora:** no hay un patrón claro. Casi todo se publica entre las 17 y las 21 UTC (13–17 h en Caracas).
- **Frecuencia:** unas 3,5 publicaciones por semana, un ritmo adecuado.

### 3.8 Evolución entre trimestres
| | Q1 (18 abr – 17 jul) | Q2 (18 jul – 15 oct) |
|---|---|---|
| Publicaciones | 44 | 47 |
| Alcance mediano por publicación | 4.214 | **6.010 (+43 %)** |
| Publicaciones de más de 30.000 de alcance | 5 | **9** |
| Abandono mediano en los primeros 3 s | 43,9 % | 47,9 % (peor) |

El contenido de técnica y lesiones del Q2 funcionó. El problema es la consistencia de los ganchos.

## 4. Recomendaciones (orden de prioridad)

1. **Fórmula 70/20/10.**
   - **70 % educativo guardable:** técnica, lesiones y dolor, fuerza para runners, planes para principiantes.
   - **20 % confianza:** tu historia, alumnas y resultados, Boston.
   - **10 % marca:** ASICS y eventos, mejor integrados en contenido educativo, como hiciste con el reel de la pisada.
2. **Serie de "dolores" para tu audiencia de 35–55 años.** Rodilla, periostitis, fascitis, cadera, lumbar, tobillo, cada uno con "3 ejercicios" en formato guardable. Es la fórmula de tu mayor viral (199.000 de alcance).
3. **CTA de comentario solo en contenido de alto valor** y como bonus al final. Deja de publicar reels que solo sirven para vender.
4. **Banco de republicaciones.** Vuelve a publicar tu top 10 con un gancho nuevo al menos 4 semanas después del original. Ya tienes 10 candidatos.
5. **Ganchos en los primeros 3 s.** Empieza con el problema o el resultado en pantalla ("¿Te duele aquí al correr?") y no con una entrada o un paisaje. Objetivo: abandono por debajo del 40 %.
6. **Captions con palabras clave.** Una frase con el tema concreto antes del "sígueme".
7. **Probar 2 carruseles educativos al mes**, por ejemplo "Plan de 4 semanas para correr 30 min" o "5 errores de principiante".
8. **Recuperar a tus seguidores.** Usa stories diarias con encuestas y cajas de preguntas (son tus seguidores, no los no seguidores, quienes ven las stories) y canales de difusión para que tu base vuelva a interactuar.

## 5. Límites de este análisis y siguientes pasos

- **Faltan las stories.** La API solo las devuelve durante 24 h, así que hay que extraerlas a diario para tener histórico.
- **No hay seguidores ganados por reel**, porque Instagram no ofrece ese dato para reels. El crecimiento se estima a partir de las métricas diarias.
- **No hay conversiones.** Para medir cuántos "Comenta X" acaban en una venta de RUNMIND hace falta cruzarlo con tus datos de DM o CRM.
- La clasificación por tema y CTA es manual (columna `tema` de `data/publicaciones.csv`) y se puede ajustar.

**Siguientes análisis propuestos:**
- Ampliar el histórico a 12 meses.
- Analizar el texto de los comentarios (qué preguntan y qué objeciones aparecen).
- Seguimiento semanal automático.
- Un dashboard visual.
