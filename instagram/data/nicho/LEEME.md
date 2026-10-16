# Captura del nicho (para `viral_ganchos.py`)

## Cómo se rellena ahora (desde el 16-oct)

Con el conector **Manifold** (claude.ai → Conectores), que lee perfiles y reels públicos sin scraper propio:

1. `reels_raw.tsv`: una fila por reel, tal como lo devuelve `instagram_get_reels` (1 crédito por página de 12). Los fijados van con `pinned` = 1. Las colaboraciones publicadas por *otra* cuenta no se apuntan.
2. `transcripciones.tsv`: primera frase hablada de los reels con más múltiplo (`instagram_get_transcript`, 1 crédito). `voz` = 0 si solo hay música y texto.
3. `duracion_propios.tsv`: duración de tus reels (el export de Windsor no la trae).
4. `python instagram/nicho_captura.py` genera `captura.tsv` (mediana por cuenta, gancho y formato) y `python instagram/viral_ganchos.py` el informe.

Para repetirlo en un mes basta con pedir "actualiza el nicho con Manifold": unas 25 páginas y 15 transcripciones, unos 40 créditos.

## Cuentas verificadas (16-oct-2026)

| cuenta | seguidores | por qué está |
|---|---|---|
| [@carlosrojo_running](https://www.instagram.com/carlosrojo_running/) | 247.826 | **Competidor directo**: entrenador de corredores ocupados +35, mismo embudo de "Comenta X" |
| [@claraalvarez.nutricion](https://www.instagram.com/claraalvarez.nutricion/) | 114.214 | Nutricionista de mujeres corredoras: tu misma audiencia |
| [@lacoachpaolafuentes](https://www.instagram.com/lacoachpaolafuentes/) | 195.005 | Coach de running (MX), New Balance: movilidad y fuerza |
| [@valeargandona](https://www.instagram.com/valeargandona/) | 18.208 | Running coach de mujeres (CL), maratoniana: tamaño parecido al tuyo |
| [@imanoloizaga](https://www.instagram.com/imanoloizaga/) | 12.030 | Entrenador nacional, campeón de España de maratón +35 |
| [@daniel_runningtrainer](https://www.instagram.com/daniel_runningtrainer/) | 5.656 | Entrenador y nutricionista, asfalto y trail |
| [@dr.gabygo](https://www.instagram.com/dr.gabygo/) | 182.861 | Fisio y coach (EE. UU., en inglés): solo como referencia de formato |

Descartadas: @mujeresquecorren (no publica reels desde 2023). No se encontraron con certeza los @ de SoyMaratonista (perfil con restricción de edad), David Carné, Vivian Patiño, Elianet Salazar ni Eli Gordón: si los sabes, añádelos.

---

## Captura a mano (si no hay Manifold)

Instagram rechaza las peticiones directas desde el contenedor (error 429) y Windsor.ai solo da datos de tu cuenta. Sin Manifold, esta parte se rellena a mano o desde una sesión con un navegador conectado a tu Chrome.

### Qué apuntar (una fila por reel, separado por tabuladores)

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

## Después

```bash
python instagram/nicho_captura.py   # reels_raw.tsv → captura.tsv
python instagram/viral_ganchos.py   # rellena la sección "El nicho" de informes/03_viralidad_ganchos.md
```
