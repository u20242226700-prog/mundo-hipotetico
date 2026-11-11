# Mundo Hipotético — guía de producción diaria

Canal de Shorts en español (TikTok **@mundohipotetico** y YouTube) con el personaje fijo **Nico**
(chico caricatura de hoodie turquesa). Todo se hace por código: guion, escenas animadas, voz,
subtítulos, música y efectos. Esta guía es lo que sigue la tarea programada cada día.

## Cuentas y herramientas
- **Metricool** (conector): marca `blogId = 8043911`, zona horaria `America/Bogota`, redes: TikTok + YouTube.
- **Speko** (conector): voz. Voz fija del canal (elegida por Daniel el 2026-11-11): **Adrián** — grave,
  profunda, tono documental. `voice = "Adrian"`, `constraints.allowedProviders.tts = ["soniox"]`, `intent.language = "es"`.
  (Antes: Johan – Colombiano de ElevenLabs; ya no se usa.)
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

## Qué va en cada horario (decidido por Daniel el 2026-11-11)
### 08:00 — video suelto "¿Qué pasaría si…?"
Una historia completa en un solo video, como la de Egipto. Dos familias, alternando:
- **De época:** Nico lleva algo moderno a otra época (Antigua Roma, Vikingos, Viejo Oeste, Edad Media,
  Japón feudal, Aztecas, Edad de Piedra, Grecia, Piratas…).
- **"¿Y si no existiera…?":** el mundo sin algo cotidiano (la goma/el caucho, el plástico, la electricidad,
  internet, los relojes, el papel, el azúcar…) o con una regla cambiada (si los perros hablaran, si
  durmiéramos 1 hora, si la gravedad fuera la mitad…). Mezclar humor con 2–3 datos reales verificados.

### 18:00 — series de 3 capítulos
Tú eliges la idea y haces todo. Cada serie = 3 videos seguidos de las 6 p. m. (días consecutivos).
- Capítulo 1: presenta el problema y engancha ("Parte 1/3" visible al inicio). Termina en suspenso.
- Capítulo 2: complica la situación. Termina en suspenso ("¿Cómo sale de esta? Parte 3 mañana").
- Capítulo 3: resolución + pregunta para la próxima serie ("¿Qué le ponemos en la próxima?").
- Recordatorio de 2 s al inicio de los capítulos 2 y 3 ("Antes: …").
Ideas de series: **La Ruleta de Nico** (ruletas de entorno/villano/objeto/estilo; la primera serie debería ser esta),
Nico en el apocalipsis zombie, Nico atrapado en un videojuego, Nico encogido en su casa, Nico náufrago,
Nico en Marte, Nico contra una IA malvada, Nico en el Titanic. Ideas de comentarios = prioridad.
Registrar en `historial.md` la serie y el capítulo (ej. "Serie: La Ruleta de Nico · 1/3") para que la siguiente
corrida de la tarde sepa por dónde va. Al terminar una serie, la siguiente arranca al día siguiente.

### Estilos visuales para rotar (2D posibles aquí)
Caricatura (actual), cómic con viñetas, pixel art, pizarra con tiza, boceto con brillo neón, vector plano,
línea minimalista. Una serie mantiene el mismo estilo en sus 3 capítulos.

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
`createScheduledPost` con `blogId 8043911`, **dos videos al día: 08:00 y 18:00 hora Bogotá** (lo pidió Daniel). La corrida de la madrugada hace el de las 8 a. m. y la de la tarde el de las 6 p. m.; los dos del mismo día deben ser temas/formatos distintos. `info`:
- `providers`: `[{"network":"tiktok"},{"network":"youtube"}]`
- `media`: `[link raw del video]`
- `text`: descripción con gancho + pregunta + hashtags (#Shorts #QuePasariaSi #MundoHipotetico + 2–3 del tema)
- `youtubeData`: `{"title": "<título ≤ 90 car. con emoji>", "type": "short", "privacy": "public", "madeForKids": false, "category": "COMEDY", "tags": [...]}`
- `tiktokData`: `{"title": "<igual>", "privacyOption": "PUBLIC_TO_EVERYONE", "isAigc": true}`
- **`autoPublish: false`** → Daniel recibe la notificación en la app de Metricool y publica con un toque.
  No cambiar a publicación automática sin que Daniel lo pida expresamente.

## Estudio diario (antes de elegir el tema)
1. **Mis resultados:** con Metricool (getAnalyticsDataByMetrics / getScheduledPosts) revisa vistas, likes,
   comentarios y retención de los últimos videos en TikTok y YouTube. Qué tema/formato/estilo rindió más.
2. **Tendencias:** busca en YouTube Shorts y TikTok (WebSearch y, si hay, el navegador en la nube) qué
   "¿Qué pasaría si…?", historias animadas y series con personaje están explotando esta semana
   (vistas altas en canales pequeños = señal fuerte). TikTok suele pedir login; si no carga, usa YouTube y la web.
3. **Comentarios:** lee los comentarios de los últimos videos; las ideas de la gente son temas prioritarios
   (y para la Ruleta de Nico).
4. Anota en `estudio.md` (fecha, 3–5 hallazgos, decisión del día). Repite lo que funciona, corta lo que no.

## Referencias que pasó Daniel (Instagram) — tenerlas en cuenta siempre
- @martivegara.yt (DfVFhIAvRiZ): animación pixel art tipo videojuego con diálogos de texto, "Día 001…365",
  inventario de 4 pasos arriba. Idea: formato de serie con progreso visible.
- @morrow.studio3d (DfDF_diPhmi): shorts 3D "What if…" hechos 100% con Claude Code; 56 videos ≈ 35 M vistas.
  Gancho fuerte, cada dato con fuente, render local. Cada video escena nueva.
- @liaodaoaii (DfbyRlwhfdv): 6 estilos: explicador caricatura 3D, monigotes, comparaciones visuales
  ("13 cubos de azúcar"), mapas de ruta 3D, motion graphics minimalistas, gráficas animadas.
- @sabodominik_ (DfieBOukW4i): MISMA escena ("¿qué pasaría si pudieras detener el tiempo?") en 7 estilos:
  PS1, Lego, caricatura 2D, terror liminal, Roblox, pixel art 3D, low-poly. Mantener historia, rotar estilo.
- @tonistelk (DfenRsSIOqZ): 10 estilos virales: pixel art, pizarra con tiza, boceto con brillo, PS2, cómic,
  vector plano, línea minimalista, CGI, Lego (+1). 
- Nuevas referencias que mande Daniel: añadirlas aquí con su lección.

## Redes
- Activas: TikTok + YouTube (Shorts). Instagram (Reels) se sumará cuando Daniel cree la cuenta y la
  conecte en Metricool: entonces agregar `{"network":"instagram"}` con `instagramData: {"type":"REEL", "isAiGenerated": true}`.

## Recopilatorio semanal (domingos, YouTube video normal)
- Lo hace una tarea aparte cada domingo. Junta los Shorts publicados de lunes a domingo (según `historial.md`),
  primero las series completas (capítulos 1→3 seguidos) y luego las historias sueltas de la mañana.
- Comando: `python3 compilar.py episodios/recopilatorios/AAAA-MM-DD/video.mp4 "<título>" "episodios/<carpeta>|<título corto>" ...`
  (16:9, 1920×1080, portada con Nico, tarjeta antes de cada historia, cierre pidiendo ideas). Sin voz nueva.
- Ideal 8+ minutos (permite anuncios a mitad de video). Con 14 Shorts sale ~9–10 min.
- Publicar en Metricool solo en YouTube como `"type": "video"` (no short), domingo 16:00 Bogotá,
  `category: "COMEDY"`, título tipo "¿Qué pasaría si…? 🌀 Las 14 historias de la semana de Nico", descripción con
  capítulos (marcas de tiempo) y `autoPublish: false`.
