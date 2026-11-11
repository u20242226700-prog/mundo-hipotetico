# Mundo Hipotético — guía de producción diaria

Canal de Shorts en español (TikTok **@mundohipotetico** y YouTube) con el personaje fijo **Nico**
(chico caricatura de hoodie turquesa). Todo se hace por código: guion, escenas animadas, voz,
subtítulos, música y efectos. Esta guía es lo que sigue la tarea programada cada día.

## Cuentas y herramientas
- **Metricool** (conector): marca `blogId = 8043911`, zona horaria `America/Bogota`, redes: TikTok + YouTube.
- **Speko** (conector): voz. Voz fija del canal: **Johan – Colombiano**, ElevenLabs,
  `voice = "4uvQjLPvqApx1dVzpNfM"`, `constraints.allowedProviders.tts = ["elevenlabs"]`, `intent.language = "es"`.
  El audio llega como archivo .wav en el resultado de la herramienta; se copia a la carpeta del episodio.
- **Este repo** (público): guarda episodios y sirve el video por link público para Metricool:
  `https://raw.githubusercontent.com/u20242226700-prog/mundo-hipotetico/main/<ruta>/video.mp4`
- Render: Python + PIL + numpy + scipy + ffmpeg (ya instalados). No hay red para instalar paquetes.
  Fuentes: InterDisplay-Black y Poppins (rutas en `episodio.py`).

## Formato que funciona (investigado nov-2026)
- 30–45 s, vertical 1080×1920, 30 fps.
- Gancho en el primer segundo ("¿Qué pasaría si…?"), escena nueva cada ~2 s, cámara siempre en movimiento
  (zoom/pan/sacudida), destello + whoosh en cada corte.
- Subtítulos de 1–3 palabras, grandes, blancos con borde negro, palabra clave en amarillo, con rebote.
- Historias graciosas con personaje fijo > ciencia con gráficos planos (los segundos se quedan en ~1K vistas).
- Final en loop (termina donde empieza) + pregunta para comentar.
- Fuentes de datos van en la descripción, nunca en pantalla.
- Voz acelerada ×1.12 (ffmpeg `atempo=1.12` + `silenceremove` al inicio y final).

## Rotación de contenido (elegir el tema del día)
Revisar `historial.md` para no repetir. Alternar:
1. **"¿Qué pasaría si…?" de época**: Nico lleva algo moderno a otra época (Egipto, Roma, Vikingos,
   Viejo Oeste, Edad Media, Japón feudal, Aztecas, Edad de Piedra…).
2. **La Ruleta de Nico** (serie de 3 días): día 1 gira 3–4 ruletas (entorno: apocalipsis zombie,
   isla desierta, Marte, Titanic…; villano: zombies, dinosaurio, piratas, IA malvada…; objeto: chancla,
   celular al 1 %, cuchara…; estilo visual). Días 2 y 3: Nico resuelve; el 2 termina en suspenso,
   el 3 pide ideas para la próxima ruleta.
3. **Escenarios absurdos**: "¿Qué pasaría si fueras el único humano en la Tierra?", "si los perros hablaran"…
Estilos visuales para rotar (2D posibles aquí): caricatura (actual), cómic con viñetas, pixel art,
pizarra con tiza, boceto con brillo neón, vector plano, línea minimalista.

## Cómo hacer un episodio
1. Crear `episodios/AAAA-MM-DD-slug/` y copiar `episodio.py` del último episodio.
2. La parte de arriba (utilidades, `nico()`, `egipcio()`, escenarios, `portal()`, `phone_big()`,
   cámara, subtítulos, audio) es el **motor**: reutilizarla. Reemplazar los planos `@shot(dur)`,
   `CHUNKS` y los efectos de sonido en `make_audio` para la nueva historia. Se pueden crear
   personajes/escenarios nuevos con el mismo estilo de dibujo (contorno oscuro `OL`, colores planos).
3. Guion: 10–14 frases cortas, una por plano. Sintetizar cada frase con Speko (una llamada por frase),
   guardarlas como `voz/v01.wav…`, pasarlas por:
   `ffmpeg -i vNN.wav -af "atempo=1.12,silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse" -ar 44100 -ac 1 vNN_f.wav`
   La duración de cada plano se ajusta sola a su frase.
4. Previsualizar: `PREVIEW=1,5,10,... python3 episodio.py` → revisar `sheet_eg.png` (personajes visibles,
   subtítulos legibles, nada cortado). Corregir y repetir.
5. Render: `python3 episodio.py video.mp4`. Revisar duración y unos fotogramas con ffmpeg.
6. Borrar temporales (`audio_eg.wav`, `sheet_eg.png`, `voz/vNN.wav` sin `_f`), commit y push.
7. Agregar una línea a `historial.md`.

## Publicar (Metricool)
`createScheduledPost` con `blogId 8043911`, a la mejor hora del día (getBestTimeToPostByNetwork; si no hay
datos, 18:41 hora Bogotá). `info`:
- `providers`: `[{"network":"tiktok"},{"network":"youtube"}]`
- `media`: `[link raw del video]`
- `text`: descripción con gancho + pregunta + hashtags (#Shorts #QuePasariaSi #MundoHipotetico + 2–3 del tema)
- `youtubeData`: `{"title": "<título ≤ 90 car. con emoji>", "type": "short", "privacy": "public", "madeForKids": false, "category": "COMEDY", "tags": [...]}`
- `tiktokData`: `{"title": "<igual>", "privacyOption": "PUBLIC_TO_EVERYONE", "isAigc": true}`
- **`autoPublish: false`** → Daniel recibe la notificación en la app de Metricool y publica con un toque.
  No cambiar a publicación automática sin que Daniel lo pida expresamente.
