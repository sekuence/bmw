# Plan de experimento: 4 semanas (19 oct – 15 nov 2026)

**Objetivo:** comprobar con tus propios datos qué formatos, temas y CTA te hacen crecer y te dan leads. Así dejas de depender de virales sueltos.
**Base:** [informe 01](../informes/01_diagnostico_2026-10.md) e [investigación 02](../informes/02_investigacion_12m_y_nicho.md).
**Calendario en datos:** [`calendario.csv`](calendario.csv). Cuando publiques, rellena el shortcode y ejecuta `python instagram/evaluar_experimento.py`.

---

## 0. Punto de partida (lo que hay que superar)

| Métrica (últimos 90 días) | Valor actual | Meta del experimento |
|---|---|---|
| Alcance mediano por publicación | 6.010 | **≥ 9.000** |
| Abandono mediano en los primeros 3 s | 47,9 % | **≤ 42 %** |
| Guardados / alcance (mediana) | 0,6 % | **≥ 1,2 %** |
| Compartidos / alcance (mediana) | 0,3 % | **≥ 0,6 %** |
| Nuevos seguidores/día | 71 (octubre) | **≥ 100** |
| Leads (DM por palabra clave) | sin medir | **medir: ≥ 400 en 4 semanas** |

## 1. Las 6 hipótesis que vamos a probar

| # | Hipótesis | Cómo se prueba | Se confirma si… |
|---|---|---|---|
| **H1** | La serie **"dolor + 3 ejercicios"** repite el éxito de la periostitis | 4 reels de una zona del cuerpo cada uno | alcance mediano ≥ 15.000 y guardados ≥ 1,5 % |
| **H2** | En **reels**, la palabra clave **al final** (después del valor) rinde más que el reel construido para pedirla | A/B con Trial Reels con el mismo tema y 2 versiones | la versión con el valor primero tiene ≥ 30 % más de vistas a las 24 h |
| **H3** | Los **carruseles educativos con palabra clave** generan leads sin perder alcance | 4 carruseles con palabra clave | alcance mediano ≥ 4.000 y ≥ 80 comentarios de palabra clave cada uno |
| **H4** | La **opinión/debate** semanal es tu motor de compartidos | 3 reels de opinión | compartidos ≥ 1 % del alcance |
| **H5** | **Republicar** un viral propio pasadas más de 4 semanas, con gancho nuevo, rinde | 3 republicaciones | cada una ≥ 30 % del alcance original |
| **H6** | Un pilar para **corredoras de más de 40** conecta con tu audiencia real (64 % de 35 a 54 años) | 2 reels | alcance ≥ 6.000 y comentarios ≥ 0,5 % del alcance |

**Reglas fijas para que la comparación sea limpia:**
- Publica **siempre entre las 19:00 y las 19:30 UTC**: 21:00 en España hasta el 25 de octubre y 20:00 desde el 26 de octubre (cambio de hora); 15:00 en Venezuela; 14:00 en Colombia, México y Perú.
- Publica **lunes, martes, miércoles, viernes y sábado**. Tus datos muestran que jueves y domingo rinden menos. Esos días son solo de stories.
- **Todos los reels** deben llevar el gancho escrito en pantalla en el primer fotograma, con subtítulos, y durar entre 20 y 40 s.
- **Todos los captions** deben empezar con una frase con palabras clave del tema (para la búsqueda). Nunca solo "Sígueme…".
- **Responde a todos los comentarios durante la primera hora.**

---

## 2. Preparación (17–18 oct, antes de empezar)

1. **Reconectar Instagram en Windsor.ai** dando todos los permisos, para poder analizar el texto de los comentarios (ver la sección 6).
2. **Automatización de DM** (ManyChat o la que uses) con estas palabras clave. Cada una envía su recurso y **pregunta por el objetivo** ("¿Estás empezando o ya corres?"), para poder cualificar el lead:

   | Palabra clave | Recurso que entrega | ¿Existe ya? |
   |---|---|---|
   | PISADA | Guía PDF: cómo saber tu tipo de pisada y elegir zapatilla | La tenías en oct-2025, revísala |
   | CADENCIA | Vídeo o PDF: ejercicio de cadencia con metrónomo | **Crear** |
   | 5K | Plan PDF de 0 a 5K en 8 semanas, imprimible | **Crear** (sale del carrusel 7) |
   | AIRE | Mini guía de respiración al correr | **Crear** |
   | FUERZA | Rutina de fuerza para corredoras (la del reel de julio) | Existe |
   | 40 | Guía: correr después de los 40 | **Crear** |

3. **Hoja de seguimiento de leads** (Google Sheets): fecha, palabra clave, número de DM, cuántos responden a la pregunta, llamadas agendadas y ventas de RUNMIND. **Sin esto no sabremos si el "comenta" vende.**
4. **Grabar en tanda** las publicaciones 6 a 11: viajas a Nueva York y el maratón es el domingo 1 de noviembre. Dos sesiones de grabación:
   - Sesión 1 (sáb 17 oct): reels 1, 4, 5, 6 y 8.
   - Sesión 2 (jue 22 oct): reels 9, 10, 12 y 15 (versiones A y B).
5. **Fijar en el perfil** los 3 posts que mejor presentan tu método: el de periostitis, el de 30 minutos sin parar y el de pliometría.

---

## 3. Calendario y guiones

> **Formato de cada ficha:**
> - **Gancho:** texto en pantalla (TP) + lo primero que dices (V).
> - **Guion:** por segundos.
> - **Caption:** el texto exacto.
> - **CTA:** la llamada a la acción exacta.
> - **Hipótesis:** qué hipótesis se mide con la publicación.

### SEMANA 1 (19–24 oct): repetir lo que ya ganó + primer A/B de CTA

---

#### 1 · Lun 19-oct · REEL · H1 · Rodilla del corredor
- **Gancho:**
  - TP: **"¿Te duele AQUÍ al correr?"** (con una flecha a la rótula).
  - V: "Si te duele alrededor de la rótula al correr o al bajar escaleras, haz estos 3 ejercicios."
  - Visual: plano cerrado de tu dedo señalando la rodilla en el segundo 0.
- **Guion:**
  - 0–3 s: gancho.
  - 3–8 s: "Casi siempre no es la rodilla, es que tu cadera y tu glúteo no la están sosteniendo."
  - 8–15 s: **1. Puente de glúteo a una pierna**, 3×12. TP: "Glúteo".
  - 15–22 s: **2. Abducción de cadera tumbada de lado**, 3×15, lenta. TP: "Glúteo medio".
  - 22–30 s: **3. Bajada excéntrica desde un escalón**, 3×8, bajando en 3 segundos. TP: "Control de rodilla".
  - 30–35 s: "3 veces por semana durante 6 semanas. Si el dolor no mejora o va a peor, ve a un fisio."
  - TP final: "Guárdalo para tu próxima sesión 📌".
- **Caption:**
  > Dolor de rodilla al correr (alrededor de la rótula): 3 ejercicios para fortalecer cadera y glúteo y correr sin molestias.
  >
  > 1️⃣ Puente de glúteo a una pierna, 3x12
  > 2️⃣ Abducción de cadera de lado, 3x15
  > 3️⃣ Bajada excéntrica en escalón, 3x8 (lento)
  >
  > Hazlos 3 veces por semana durante 6 semanas. Si el dolor persiste, consulta con un fisioterapeuta.
  >
  > Sígueme @healthyanii para más ejercicios para correr sin lesiones ‼️
- **CTA:** "Sígueme" en el caption y "Guárdalo" en pantalla. **Sin palabra clave**: es la misma fórmula que el reel de periostitis.

---

#### 2 · Mar 20-oct · CARRUSEL · H3 · Pisada (remake del de 141.000)
- **Slide 1 (portada):** **"Me costó 6 meses de lesión no saber esto"** sobre una foto tuya mirando tus zapatillas.
- **Slide 2:** "Elegí zapatillas porque 'todo el mundo las usaba'… y no eran para mí."
- **Slide 3:** Los 3 tipos de pisada (neutra, pronadora, supinadora), con un dibujo simple de la huella.
- **Slide 4:** Test casero 1: **mira el desgaste de la suela** de tus zapatillas viejas, con una foto.
- **Slide 5:** Test casero 2: **la huella mojada** en un cartón.
- **Slide 6 (aporte basado en la ciencia):** "La ciencia dice que **la comodidad es tu mejor filtro**. Pruébate 3 modelos y quédate con el que no notas."
- **Slide 7:** "Qué buscar según tu pisada" (sin abusar de la marca; si ASICS lo pide, menciona aquí un modelo por tipo).
- **Slide 8 (CTA):** **"Comenta PISADA y te envío la guía completa para saber tu pisada y qué zapatilla elegir 👟"**
- **Caption:**
  > Cuando empecé a correr cometí un error que me costó 6 meses de lesión: elegir zapatillas sin saber cómo piso.
  >
  > En este carrusel te enseño 2 tests caseros para saber tu tipo de pisada y qué mirar al comprar tus próximas zapatillas.
  >
  > 💬 Comenta PISADA y te mando la guía completa.
  > 📌 Guárdalo para tu próxima compra.
- **CTA:** comentar PISADA.

---

#### 3 · Mié 21-oct · REEL · H5 · Republicar "Plan para correr 30 min sin parar" (161.000 el 2-sep)
- **Mismo vídeo** con **portada y texto de pantalla nuevos.**
  - TP nuevo: **"Si hoy no aguantas ni 5 minutos corriendo, guarda esto."**
- **Caption nuevo:**
  > Plan para pasar de no aguantar 5 minutos a correr 30 minutos sin parar, aunque nunca hayas hecho deporte.
  >
  > La clave no es aguantar: es alternar caminar y correr (CACO) e ir subiendo poco a poco.
  >
  > Si estás comprometida déjame un 🙋🏻‍♀️ en comentarios y te mando una sorpresa por DM.
  > Sígueme @healthyanii para más contenido sobre correr 🫶🏻
- **CTA:** el mismo que funcionó (emoji en comentarios + "Sígueme"). Acuérdate de enviar el DM sorpresa a mano o con la automatización.

---

#### 4 · Vie 23-oct · REEL · H2 (control) · Zancada larga = freno
- **Gancho:**
  - TP: **"Este error te frena en CADA paso"**.
  - V: "Si tu pie cae por delante de tu rodilla, estás frenando cada vez que pisas."
  - Visual: cámara lenta lateral de una zancada larga, con una X roja.
- **Guion:**
  - 0–3 s: gancho.
  - 3–10 s: comparación lado a lado (zancada larga frente a pie que cae bajo la cadera).
  - 10–18 s: "Lo arreglas así: **pasos más cortos y más rápidos**."
  - 18–26 s: "Sube tu cadencia un 5 %: si das 160 pasos por minuto, prueba con 168. Usa un metrónomo."
  - 26–32 s: "No lo cambies todo de golpe: 2 o 3 minutos por salida."
  - 32–36 s: **CTA al final.**
- **CTA (solo al final, después del valor):**
  - V y TP: **"Si quieres el ejercicio con metrónomo paso a paso, comenta CADENCIA y te lo mando."**
- **Caption:**
  > Zancada demasiado larga (overstriding): el error de técnica que te frena en cada paso y sobrecarga tus rodillas.
  >
  > Cómo corregirlo: pasos más cortos, el pie cae bajo la cadera y la cadencia sube un 5 %.
  >
  > 💬 Comenta CADENCIA y te envío el ejercicio con metrónomo.
- **Qué mide:** es el **control de H2**, con la palabra clave al final. Se compara con los reels de "comenta" anteriores, en los que la palabra clave era el motivo del vídeo (mediana de 3.844).

---

#### 5 · Sáb 24-oct · REEL · H4 · Opinión: maratón en tu primer año
- **Gancho:**
  - TP: **"Correr un maratón en tu primer año es mala idea"**.
  - V: "Lo digo yo, que he corrido 9 maratones: no corras un maratón en tu primer año corriendo."
  - Visual: hablando a cámara, primer plano.
- **Guion:**
  - 0–3 s: gancho.
  - 3–12 s: "No porque no puedas. Porque tus tendones y huesos se adaptan mucho más lento que tu corazón."
  - 12–20 s: "El corazón mejora en semanas; los tendones tardan meses. Ahí llegan las lesiones."
  - 20–28 s: "Mi recomendación: primer año 5K y 10K; segundo año, media; y después, maratón."
  - 28–33 s: "¿Estás de acuerdo o crees que exagero? Te leo."
- **Caption:**
  > ¿Maratón en tu primer año corriendo? Mi opinión después de 9 maratones y de entrenar a +300 personas.
  >
  > Tu corazón se adapta en semanas, pero tus tendones y huesos tardan meses. Por eso tantas personas se lesionan preparando su primer 42K.
  >
  > 👇 ¿Estás de acuerdo o crees que exagero?
  > 📲 Envíaselo a esa persona que se apuntó a un maratón sin haber corrido un 10K.
- **CTA:** debate en comentarios y **enviar a alguien** (la señal de envíos).

---

### SEMANA 2 (26–31 oct): pilar de más de 40 + Nueva York (todo grabado antes)

---

#### 6 · Lun 26-oct · REEL · H1 · Cintilla iliotibial
- **Gancho:**
  - TP: **"¿Dolor en la parte de FUERA de la rodilla?"** (flecha a la cara lateral).
  - V: "Si te duele la parte de fuera de la rodilla a partir del km 5, probablemente es tu cintilla iliotibial."
- **Guion:**
  - 3–8 s: "Estirarla no sirve de mucho. Lo que funciona es fortalecer tu cadera."
  - 8–15 s: **1. Plancha lateral con elevación de pierna**, 3×8 por lado.
  - 15–22 s: **2. Peso muerto a una pierna**, 3×10.
  - 22–30 s: **3. Bajada lateral desde un escalón**, 3×8, lenta.
  - 30–35 s: "3 veces por semana. Si no mejora en 4 a 6 semanas, ve a un fisio."
  - TP: "Guárdalo 📌".
- **Caption:**
  > Dolor en la parte externa de la rodilla al correr (síndrome de la cintilla iliotibial): 3 ejercicios de cadera para correr sin molestias.
  >
  > [lista de los 3 ejercicios con series]
  >
  > Sígueme @healthyanii para más ejercicios para correr sin lesiones ‼️
- **CTA:** "Sígueme" + "Guárdalo".

---

#### 7 · Mar 27-oct · CARRUSEL · H3 · Plan de 0 a 5K en 8 semanas
- **Slide 1:** **"De 0 a 5K en 8 semanas (aunque hoy no aguantes 1 minuto)"**.
- **Slide 2:** "Las reglas: 3 días por semana, nunca dos días seguidos, ritmo en el que puedas hablar."
- **Slides 3–6:** una tabla por cada 2 semanas:
  - S1–2: 1' corriendo / 2' caminando ×8.
  - S3–4: 3' / 2' ×6.
  - S5–6: 5' / 1' ×5.
  - S7–8: 10' / 1' ×3, para terminar con 30' seguidos.
- **Slide 7:** "Si una semana te cuesta, repítela. No pasa nada."
- **Slide 8 (CTA):** **"Comenta 5K y te mando el plan en PDF para imprimir y pegar en la nevera 🧡"**
- **Caption:**
  > Plan de 8 semanas para correr tus primeros 5K desde cero, con el método CACO (caminar + correr).
  >
  > 💬 Comenta 5K y te envío el plan en PDF.
  > 📲 Envíaselo a la amiga que siempre dice "quiero empezar a correr".
- **CTA:** comentar 5K.

---

#### 8 · Mié 28-oct · REEL · H6 · Más de 40 y quieres empezar a correr
- **Gancho:**
  - TP: **"¿Tienes +40 y quieres empezar a correr? Haz esto primero."**
  - V: "Si tienes más de 40 años y quieres empezar a correr, antes del primer kilómetro haz estas 3 cosas."
- **Guion:**
  - 3–12 s: **1. Fuerza 2 días por semana.** "A partir de los 40 perdemos masa muscular cada año; el músculo es lo que protege tus articulaciones."
  - 12–20 s: **2. Empieza caminando y corriendo (CACO).** "Tu corazón se adapta rápido; tus tendones, no."
  - 20–28 s: **3. Deja 48 h entre carreras al principio.** "La recuperación es parte del entrenamiento."
  - 28–34 s: "Y lo mejor: correr es de lo mejor que puedes hacer por tus huesos."
  - TP: "Envíaselo a quien lo necesite 💌".
- **Caption:**
  > Empezar a correr después de los 40: 3 cosas que debes hacer antes del primer kilómetro, para no lesionarte y disfrutarlo.
  >
  > [lista]
  >
  > Sígueme @healthyanii si quieres empezar a correr con cabeza, a cualquier edad 🫶🏻
- **CTA:** "Sígueme" y "Envíaselo".

---

#### 9 · Vie 30-oct · REEL · Personal + educativo (control de confianza) · Qué como 48 h antes de un maratón
- **Gancho:**
  - TP: **"Lo que como 48 h antes de mi maratón #10 (en Nueva York)"**.
  - V: "Faltan 48 horas para mi maratón número 10 y esto es exactamente lo que voy a comer."
- **Guion:** 3 escenas en Nueva York.
  1. "Más carbohidratos: arroz, pasta, pan; de 8 a 10 g por kilo al día."
  2. "Menos fibra y grasa para no tener problemas de estómago."
  3. "Nada nuevo: solo lo que ya probé en mis tiradas largas."
  - Cierre: "¿Quién más corre el domingo?"
- **Caption:**
  > Carga de carbohidratos antes de un maratón: lo que como las 48 h previas a mi maratón #10 en Nueva York 🗽
  >
  > [3 puntos]
  >
  > ¿Quién más corre el domingo? 👇
- **Qué mide:** si un contenido personal **con información útil** supera la mediana de lo personal (4.120).

---

#### 10 · Sáb 31-oct · REEL · H4 · Opinión: no necesitas un Major
- **Gancho:**
  - TP: **"No necesitas correr un Major para ser corredora de verdad"**.
  - V: "Mañana corro mi quinto World Major y te voy a decir algo que quizá no esperas."
- **Guion:**
  - "Los Majors son increíbles, pero no te hacen más corredora."
  - "Ser corredora es salir un martes con frío cuando nadie te ve."
  - "Tu 5K de barrio vale lo mismo."
  - "¿Estás de acuerdo?"
- **Caption:**
  > Mañana corro el maratón de Nueva York, mi 5ª World Major, y aun así lo pienso: no necesitas un Major para ser corredora de verdad.
  >
  > 👇 ¿Estás de acuerdo?
  > 📲 Envíaselo a quien piensa que su carrera "no cuenta".
- **CTA:** debate y envío.

**Dom 1-nov (maratón de NYC):** solo stories, en directo y con la cuenta atrás. **No publiques en el feed.**

---

### SEMANA 3 (2–7 nov): post-maratón + A/B limpio con Trial Reels

---

#### 11 · Lun 2-nov · REEL · Personal + palabra clave · Maratón #10
- **Gancho:**
  - TP: **"Mi maratón #10 en Nueva York"** con el resultado en pantalla.
  - V: (los primeros 2 s son la llegada a meta, sin hablar).
- **Guion:**
  - Llegada a meta.
  - "Hace 10 años no aguantaba 5 minutos corriendo."
  - 3 momentos de la carrera.
  - "Si yo pude, tú también."
- **Caption:** la historia (como el de Boston) + **"Si quieres que tu primer 21K o 42K se sienta así, comenta META y te cuento cómo trabajamos en RUNMIND."**
- **Qué mide:** si un momento personal de alto impacto genera leads con palabra clave. Se compara con el de Boston: 2.954 de alcance y 98 comentarios.

---

#### 12 · Mar 3-nov · REEL · H1 · Talón y Aquiles
- **Gancho:**
  - TP: **"¿Te duele AQUÍ al correr?"** (flecha al tendón de Aquiles).
  - V: "Si te duele el tendón de Aquiles por la mañana o al empezar a correr, haz estos 3 ejercicios."
- **Guion:**
  - **1. Elevación de talones lenta** con la rodilla estirada, 3×15 (3 s arriba, 3 s abajo).
  - **2. La misma con la rodilla flexionada** (trabaja el sóleo), 3×15.
  - **3. Isométrico de puntillas**, 5×45 s.
  - "El tendón necesita carga, no reposo total. Si duele más de 4 sobre 10, baja la carga y consulta a un fisio."
- **Caption:**
  > Dolor en el tendón de Aquiles al correr: 3 ejercicios de carga progresiva para fortalecerlo.
  >
  > [lista]
  >
  > Sígueme @healthyanii para más ejercicios para correr sin lesiones ‼️
- **CTA:** "Sígueme" + "Guárdalo".

---

#### 13 · Mié 4-nov · CARRUSEL · H3 (control sin palabra clave) · 7 errores en 10 maratones
- **Slide 1:** **"7 errores que cometí en mis 10 maratones (para que tú no los cometas)"**.
- **Slides 2–8:** un error por slide, cada uno con su solución:
  1. Salir demasiado rápido.
  2. Estrenar zapatillas.
  3. No practicar los geles.
  4. Hacer todas las tiradas rápidas.
  5. Saltarme la fuerza.
  6. Dormir mal la semana previa.
  7. No tener plan para el km 30.
- **Slide 9:** "¿Cuál has cometido tú? 👇"
- **Caption:**
  > 7 errores que cometí corriendo 10 maratones y cómo evitarlos en tu próxima carrera.
  >
  > 📌 Guárdalo para tu próximo maratón.
  > 📲 Envíaselo a tu compañera de entrenos.
- **Qué mide:** es el **control sin palabra clave** frente a los carruseles 2, 7 y 17, que sí la llevan. Es el mismo formato que "7 trucos de running" (40.964).

---

#### 14 · Vie 6-nov · REEL · H5 · Republicar "2 gestos para correr más eficiente" (55.777 el 12-ago)
- **Mismo vídeo** con texto de pantalla nuevo:
  - TP nuevo: **"Corre más ligera con solo 2 cambios"**.
- **Caption nuevo:**
  > 2 cambios de técnica para correr más eficiente y cansarte menos: braceo y postura.
  >
  > Sígueme @healthyanii para aprender técnica de carrera ‼️

---

#### 15 · Jue 5-nov (prueba) → Sáb 7-nov (al feed) · REEL · **H2: A/B con Trial Reels** · Respiración
- Graba **2 versiones** con el **mismo contenido** y súbelas el **jueves 5-nov como Trial Reels** (solo las ven no seguidores).
- **Versión A ("comenta" primero):**
  - TP y V: **"Comenta AIRE y te mando mi guía para no quedarte sin aire al correr."**
  - Después, el contenido.
- **Versión B (valor primero):**
  - TP: **"¿Te quedas sin aire a los 5 minutos?"**
  - Contenido:
    1. "Baja el ritmo: tienes que poder hablar."
    2. "Respira por nariz y boca a la vez."
    3. "Sincroniza: 3 pasos inhalas, 2 exhalas."
  - Al final: "Comenta AIRE y te mando la guía."
- **Sábado 7-nov:** compara las **vistas a las 24 h** y **comparte con tus seguidores la que gane**.
- Apunta las dos cifras en `calendario.csv` (filas 15A y 15B).
- **Caption (para las dos):**
  > Cómo respirar al correr para no quedarte sin aire: 3 claves fáciles.
  >
  > 💬 Comenta AIRE y te mando la guía.

---

### SEMANA 4 (9–14 nov): consolidar y cerrar hipótesis

---

#### 16 · Lun 9-nov · REEL · H1 · Dolor lumbar al correr
- **Gancho:**
  - TP: **"¿Te duele la espalda baja cuando corres?"**
  - V: "Si terminas de correr con la zona lumbar cargada, casi siempre es tu core."
- **Guion:**
  - **1. Dead bug**, 3×10.
  - **2. Bird dog**, 3×10 por lado.
  - **3. Plancha lateral**, 3×30 s.
  - "2 o 3 veces por semana, después de correr."
- **Caption:**
  > Dolor lumbar al correr: 3 ejercicios de core para proteger tu espalda baja.
  >
  > [lista]
  >
  > Sígueme @healthyanii ‼️
- **CTA:** "Sígueme" + "Guárdalo".

---

#### 17 · Mar 10-nov · CARRUSEL · H3 · Rutina de fuerza para corredoras (20 min)
- **Slide 1:** **"La rutina de fuerza de 20 minutos que hago 2 veces por semana"**.
- **Slides 2–7:** un ejercicio por slide, con foto y series:
  1. Sentadilla búlgara.
  2. Peso muerto rumano.
  3. Puente de glúteo.
  4. Elevación de talones.
  5. Plancha.
  6. Saltos al cajón (pliometría).
- **Slide 8:** "¿Cuándo hacerla? Los días de rodaje suave, después de correr, o en días sin correr."
- **Slide 9 (CTA):** **"Comenta FUERZA y te envío la rutina completa con vídeos ⚡️"**
- **Caption:**
  > Rutina de fuerza para corredoras: 20 minutos, 2 veces por semana, para correr más rápido y sin lesiones.
  >
  > 💬 Comenta FUERZA y te la mando con vídeos.
  > 📌 Guárdala.
- **CTA:** comentar FUERZA (la palabra clave ya validada: 1.694 comentarios).

---

#### 18 · Mié 11-nov · REEL · H6 · Menopausia y running
- **Gancho:**
  - TP: **"Menopausia y running: 3 cosas que cambian (y qué hacer)"**.
  - V: "Si tienes entre 40 y 55 y notas que correr se siente distinto, no es tu imaginación."
- **Guion:**
  - **1.** "Pierdes músculo más rápido. Respuesta: fuerza 2 o 3 veces por semana con cargas que te cuesten."
  - **2.** "Recuperas más lento. Respuesta: más días suaves y dormir bien."
  - **3.** "Necesitas más proteína. Respuesta: un poco en cada comida."
  - "Habla siempre con tu médico o ginecóloga. Pero no dejes de correr: es de lo mejor que puedes hacer por tus huesos y tu corazón."
- **Caption:**
  > Correr en la perimenopausia y la menopausia: 3 cambios que vas a notar y cómo adaptar tu entrenamiento según la ciencia.
  >
  > 💬 Comenta 40 y te envío mi guía para entrenar después de los 40.
  > 📲 Envíaselo a una amiga que corre.
- **CTA:** comentar 40.
- **Nota:** valida bien este tema. Si quieres más autoridad, invita a una ginecóloga o médica deportiva a un Collab.

---

#### 19 · Vie 13-nov · REEL · H5 · Republicar "Periostitis tibial" (199.220 el 14-ago)
- **Mismo vídeo** con texto de pantalla nuevo:
  - TP nuevo: **"Si te duele la espinilla al correr, no es normal"**.
- **Caption nuevo:**
  > Dolor en la espinilla al correr (periostitis tibial): 3 ejercicios para fortalecer la zona. Suele mejorar en 3 a 6 semanas si eres constante.
  >
  > Sígueme @healthyanii para más ejercicios para correr sin lesiones ‼️

---

#### 20 · Sáb 14-nov · REEL · H4 · Opinión: correr lento
- **Gancho:**
  - TP: **"Correr lento NO es correr mal"**.
  - V: "Los corredores de élite hacen el 80 % de sus kilómetros lentos. ¿Por qué tú no?"
- **Guion:**
  - "La regla 80/20: el 80 % suave, el 20 % fuerte."
  - "Si corres siempre a tope, te estancas y te lesionas."
  - "Correr a 7:30 el km también es correr."
  - "¿Qué ritmo haces tú en tus rodajes? Te leo."
- **Caption:**
  > Correr lento también es correr, y es lo que más te hará mejorar: la regla 80/20 explicada fácil.
  >
  > 👇 ¿A qué ritmo haces tus rodajes?
  > 📲 Envíaselo a quien se avergüenza de su ritmo.
- **CTA:** debate y envío.

---

## 4. Stories (todos los días, también jueves y domingo)

Las stories las ven sobre todo **tus seguidores**, la parte de tu base que ahora casi no te ve. Tres stories al día:

1. **Encuesta o pregunta** del tema del día ("¿Te ha dolido la rodilla corriendo? Sí / No").
2. **Contenido detrás de cámaras o del entrenamiento** de ese día.
3. **"Nuevo reel 👇"** con el sticker de enlace a la publicación del día. Los jueves, una **caja de preguntas** ("¿Qué te duele cuando corres?"), que te da temas para H1.

Cada domingo, repasa en stories las publicaciones de la semana.

## 5. Revisión semanal (cada lunes, 15 min)

1. Exportar los datos de la semana (Windsor o el panel de Instagram).
2. Rellenar en `calendario.csv` el shortcode de cada publicación y los leads de la hoja de DM.
3. Ejecutar `python instagram/evaluar_experimento.py`.
4. **Una sola decisión por semana:** si una hipótesis va claramente por debajo, cambia solo esa en la semana siguiente.

### Al terminar (16-nov): reglas de decisión
- Si se confirma **H1** → la serie de dolores pasa a ser fija, **2 por semana**.
- Si se confirma **H2** → todos los reels con palabra clave pasan a tener el valor primero y el CTA al final.
- Si se confirma **H3** → los carruseles pasan a ser tu canal principal de leads (1 o 2 por semana) y los reels, de crecimiento.
- Si se confirma **H4** → una opinión por semana, fija.
- Si se confirma **H5** → crear un "banco de republicación": tu top 10, cada 6–8 semanas con gancho nuevo.
- Si se confirma **H6** → nuevo pilar mensual de más de 40, y valorar una oferta específica de RUNMIND para este público.
- Lo que no se confirme, **se deja de hacer o se rediseña**. No se repite "por si acaso".

## 6. Lo que necesito de ti

1. **Reconectar Instagram en Windsor.ai** con todos los permisos: el enlace está en el mensaje del chat. Es para leer el texto de los comentarios y sacar las preguntas y objeciones reales.
2. **Datos de DM y ventas.** ¿Qué herramienta usas para "Comenta X" (ManyChat u otra)? Si me compartes la exportación de cuántos DM por palabra clave y cuántas ventas de RUNMIND, puedo medir el embudo completo.
3. **Revisar los guiones de ejercicios** con tu criterio de coach. Ajusta series o ejercicios si con tus alumnas usas otros.
4. **Canva** (opcional). El conector no se pudo conectar en esta sesión; si lo reconectas, puedo diseñarte las plantillas de los carruseles (2, 7, 13 y 17).
