# Captura del nicho (para `viral_ganchos.py`)

Desde el contenedor de Claude no se puede abrir Instagram ni YouTube (la red del entorno lo bloquea), y Windsor.ai solo da datos de tu cuenta. Por eso esta parte se rellena a mano, o desde una sesión con un navegador conectado a tu Chrome.

## Qué apuntar (una fila por reel, separado por tabuladores)

| columna | qué es |
|---|---|
| account | @usuario |
| followers | seguidores del perfil |
| median | **la más importante**: mira las vistas de sus últimos 12 reels y apunta la del medio |
| views | vistas de este reel |
| hook | la primera frase, dicha o escrita, tal cual (con faltas incluidas) |
| on_screen | el primer texto en pantalla, si es distinto |
| length_s | duración en segundos |
| cta | lo que piden al final |
| fecha, url | para poder volver a él |

Por cada cuenta, apunta **sus 3 reels con más vistas y 3 normales** de los últimos 2 meses. Con 6 a 10 cuentas salen entre 40 y 60 filas, que ya sostienen una conclusión. Con menos de 40 el informe lo marca como pista.

Reglas: solo leer, a ritmo humano, nunca con un scraper (Instagram bloquea cuentas por eso). Copiamos la **fórmula** del gancho, nunca el vídeo ni el guion.

## Cuentas propuestas (pendientes de que las valides)

Tamaño entre 4.000 y 370.000 seguidores (hasta 10 veces el tuyo). Cifras de listados de terceros de 2026: **verifica el @ y los seguidores en el perfil**.

**Directas (running en español, coach o entrenadora)**
- SoyMaratonista (AR, ~80k): planes de entrenamiento.
- Prof. Pablo Silguero (AR, ~42k): entrenador de running.
- Maca (MX, ~61k): entrenadora, también embajadora de ASICS.
- Isa Aguilera (AR, ~11k): entrenadora de running y trail, de 5K a maratón.
- Vivian Patiño (CO, ~25k): coach de mujeres.
- Eli Gordón (ES, ~10k): entrenadora, ciencias del deporte.

**Adyacentes (misma audiencia, otro ángulo)**
- Elianet Salazar (MX, ~49k): nutrióloga para corredores.
- Mateo Beltrán (AR): médico y corredor (más de 200k en TikTok).
- Una cuenta de fisio para corredores en español: propón la que veas en tu feed.

**Grandes (solo para ver formatos)**
- David Carné (ES, ~279k): entrenador online de corredores.
- @dr.gabygo (EE. UU., ~179k, en inglés): lesiones de running.

Fuentes: [Modash Argentina](https://www.modash.io/find-influencers/argentina/running), [Modash México](https://www.modash.io/find-influencers/mexico/running), [Heepsy España](https://www.heepsy.com/top-instagram/running/spain), [Heepsy México](https://www.heepsy.com/top-instagram/running/mexico), [Physitrack](https://www.physitrack.com/es/insights/top-physical-therapy-influencers-instagram).

Lo más rápido de todo: tu carpeta de **Guardados** de Instagram. Ya está filtrada por tu criterio.

## Después

```bash
python instagram/viral_ganchos.py   # rellena la sección "El nicho" de informes/03_viralidad_ganchos.md
```
