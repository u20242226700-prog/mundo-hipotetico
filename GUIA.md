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

### Cada 2 días a las 08:00 — formato "¿Por qué…?" (pedido de Daniel el 2026-11-12)
Los días PARES del mes (2, 4, 6…) el video de las 8 a. m. NO es "¿Qué pasaría si…?" sino una **historia que
explica un secreto de ingeniería/ciencia** (referencia: "Why Perfect Railroads Don't Work", @RicksClips3000,
559 K likes). Fórmula analizada con vidIQ:
- **Montaje:** dos rivales (Nico vs. un rival) compiten por algo grande (cruzar un cañón, construir una torre…).
- **Conflicto:** Nico hace algo que parece un error (deja huecos entre los rieles) y su jefe se enoja.
- **Éxito del rival:** el rival lo hace "perfecto", gana al principio y la gente se va con él.
- **La ciencia actúa:** llega el calor, el frío, el viento… se ven los números (termómetro, regla, medidor).
- **Clímax:** lo del rival falla de forma espectacular y lo de Nico funciona → se revela por qué.
- 60–75 s, narración enérgica, cámara cinematográfica (planos muy abiertos, primeros planos de detalles),
  colores cálidos de paisaje, personajes simples y expresivos sobre escenarios con mucha profundidad.
- Ideas: huecos en los rieles (dilatación), juntas en puentes, por qué los aviones tienen ventanas redondas,
  por qué los rascacielos se balancean, por qué las carreteras tienen grietas a propósito, por qué los barcos
  de acero flotan, cables de alta tensión que cuelgan, por qué las represas son curvas, neumáticos con dibujo.
- Dato verificado con fuente en la descripción. Título: "¿Por qué <cosa> tiene <detalle raro>?" o
  "El ingeniero que hizo <cosa rara>… y tenía razón".
- **ESTILO OBLIGATORIO (Daniel, 2026-11-12: "la animación como la del link de YouTube"): 2.5D.**
  Plantilla: `plantillas/porque_ejemplo.py` (ventanas de avión, se apoya en `plantillas/porque_base.py`).
  - Personajes con `figura()`: palito 2D plano, cabeza blanca ovalada grande, extremidades negras, contorno
    grueso, capucha del color de la sudadera (Nico turquesa, rival rojo con pelo en punta, extras grises).
    Expresiones exageradas: neutral, happy, smug, worried, angry, shock (ojos enormes), laugh. Rabia = cara
    morada (`cara=PURP`) + `vapor=True`; susto = `sudor=True`. Poses: idle, point, arms_up, cross, laugh, shock, chin.
  - Mundo con perspectiva REAL: `pista()` (pista que corre hacia el horizonte con `vel`, pasto a rayas,
    montañas, niebla), `hangar2()` (punto de fuga, cerchas, portón al cielo), `cielo2()` (nubes con volumen).
    Para otros temas crea escenarios igual: suelo proyectado por profundidad + niebla + sombras duras.
  - Ciencia = mapa térmico neón (morado→rosa→amarillo) sobre el objeto real (`piel()` + `neon_map()`), con zoom
    de cámara al punto crítico.
  - Utilería de papel con sombra (`pegar()`): periódico con titular, calendario que pasa años, manómetro, etc.
  - **Cortes cada 1–2 s:** cada frase tiene 2 planos (`corte(t, D)`): plano general → primer plano/reacción.
  - Letrero "¿POR QUÉ?" con borde negro, subtítulos amarillos/blancos con borde negro, sin grano
    (`postproceso(..., tono="neutro", bloom=0.22, grano=0, motas=False)`).
- Exporta con `-crf 23` (el grano del realce hace pesados los archivos).
Los días IMPARES sigue el "¿Qué pasaría si…?" normal.

### 18:00 — series de 3 capítulos
Tú eliges la idea y haces todo. Cada serie = 3 videos seguidos de las 6 p. m. (días consecutivos).
- **Duración de cada capítulo: 70–100 s** (pedido de Daniel el 2026-11-12), más largos que los de la mañana. Guion de 20–28 frases, 22–30 planos, con más desarrollo: diálogo de Nico, giros y más escenas. Sigue siendo vertical 1080×1920 (Shorts admite hasta 3 min). Mantener una escena nueva cada 2–4 s para que no baje la retención.
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
- **Referencia de Daniel 2026-11-12 (reel Dfo8Vvlowmh, "10 estilos de animación"):** la misma escena se puede
  contar en estilos muy distintos. Los que se pueden hacer con código aquí: **cómic** (contornos gruesos,
  tramas de puntos, onomatopeyas "¡BOOM!"), **pixel art** (dibujar a 1/8 de resolución y escalar con NEAREST,
  marcador retro), **trazo de luz** (fondo negro, líneas neón con glow que dibujan la trayectoria), **flat**
  (vectores planos, fichas y flechas punteadas), **pizarra** (fondo verde/negro, tiza con trazo irregular).
  Los de CGI, PS2, bloques y figura 3D necesitan Blender (red bloqueada en este chat).
  Uso: el 08:00 impar rota de estilo cada semana (lunes decide), Nico siempre igual de reconocible.
  Idea de formato para probar un domingo o un día flojo: "La misma historia en 5 estilos" con lista
  numerada al costado que avanza, y CTA "Comenta ESTILOS" (pedir una palabra en comentarios sube la interacción).
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
- `text`: descripción con gancho + pregunta + hashtags (ver "Hashtags" abajo)
- **Hashtags (investigado 2026-11-12, pedido de Daniel: "busca hashtags más virales").** Fuente: outliers en
  español de nuestro nicho (videos animados de "¿qué pasaría si?", historias y ciencia, con 7–500x las vistas
  normales del creador). Regla: **5–6 hashtags, al final del texto**, mezcla de 1 de descubrimiento + 2 de
  formato + 2 de tema + la marca. Más de 6 o puros genéricos (#fyp #viral #parati sueltos) no ayudan: TikTok
  clasifica por tema. Los 3 primeros salen encima del título en YouTube, así que ahí van los de más búsqueda.
  - 08:00 "¿Qué pasaría si…?": `#quepasariasi #historiasanimadas #curiosidades #historia #parati #mundohipotetico`
    (cambia #historia por #ciencia, #espacio, #roma, #egipto… según el tema).
  - Días pares "¿Por qué…?": `#sabiasque #datoscuriosos #ciencia #ingenieria #aprendecontiktok #mundohipotetico`
    (+ uno del objeto: #aviones, #trenes, #puentes…).
  - 18:00 series: `#historiasanimadas #animacion #parte1 (2/3) #quepasariasi #fyp #mundohipotetico`
    (#parte1 / #parte2 / #parte3 ayuda a que encuentren la serie completa).
  - YouTube: además agrega `#shorts` como primer hashtag del texto, y en `youtubeData.tags` pon 8–12
    palabras clave sin # (ej.: "que pasaria si", "curiosidades", "animacion", "historia", "datos curiosos").
  - En los estudios de lunes/miércoles/viernes revisa los hashtags de los outliers nuevos
    (`vidiq_instagram_tiktok_outlier_search`, 5 créditos, idioma es) y anota en `estudio.md` si aparece uno
    que se repita en 2+ videos virales; si es del tema del video, úsalo.
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
4. **Outliers (método "pro")**: busca canales de Shorts/videos en español con **menos de 3 meses o pocos videos
   y muchas vistas** en nichos cercanos (qué pasaría si, historias animadas, historia, curiosidades). Si hay
   conector **vidIQ** (conectado el 2026-11-12): `vidiq_outliers` (keyword "qué pasaría si", contentType short,
   language es, publishedWithin thisMonth, maxSubscribers 200000) y `vidiq_trending_videos` (videoFormat short,
   videoTitleLanguage es, sortBy vph). **Presupuesto: plan gratis de 150 créditos/mes, 5 por llamada** → solo
   1 llamada en la corrida de la MAÑANA de lunes, miércoles y viernes (≈13 llamadas/mes). Los demás días, usa lo
   anotado en estudio.md y YouTube directo. Revisa `vidiq_balance` (gratis) antes; si quedan <20, no gastes. Anota qué fórmula repiten (gancho, duración, estilo visual, título, miniatura, ritmo) y
   **adapta la fórmula** al mundo de Nico. Nunca copies guiones, personajes ni videos de otros.
5. Anota en `estudio.md` (fecha, 3–5 hallazgos, decisión del día). Repite lo que funciona, corta lo que no.

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
- @iamakerss (DfIdEa2CRI2): "novato vs pro" en monetización. Novato le pide ideas de nicho a un chat y hace lo
  mismo que todos; pro usa una herramienta de datos (NexLev) para encontrar **canales nuevos que explotan**
  (ej. "Historias de Roma" 2,4 M en 1 mes, "Misterios del mar", "Abuelos y la IA") y copia la **fórmula**
  (formato, ritmo, título, miniatura), no el contenido. Estética: personajes 3D tipo juguete, iluminación de
  ambiente (lámpara cálida vs luz verde de monitores), paneles de UI con brillo. LECCIÓN → ver "Outliers" en el estudio.
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

## Calidad (pedido de Daniel el 2026-11-12: "que no se vean tan sencillos") — OBLIGATORIO
### Historia y guion
- Estructura de cada video: **gancho** (1 s, pregunta absurda o imagen impactante) → **escalada** (cada escena
  sube la apuesta: ventaja → abuso de la ventaja → consecuencia) → **giro** inesperado → **remate** gracioso
  → **loop/pregunta**. Nada de escenas "de relleno": cada frase debe cambiar la situación.
- Nico **habla y reacciona** (2–4 líneas propias tipo "¿Y ahora qué hago?" en burbuja o voz), no solo el narrador.
- Al menos 1 dato real sorprendente por video (en la mañana), dicho de forma graciosa.
- Chistes visuales de fondo (un personaje haciendo algo raro detrás) para que la gente lo vuelva a ver.
### Encuadre y animación
- El personaje principal ocupa **35–60 % de la altura** del cuadro en la mayoría de planos; usa primeros planos
  de cara para las reacciones (al menos 3 por video). Nada de personajes chiquitos en escenarios vacíos.
- Las caras quedan entre y=600 y y=1350 del cuadro final para que el subtítulo (y≈1600) no tape la cara ni el torso.
- Siempre hay algo moviéndose: parpadeo (realce.parpadeo), personajes de fondo animados, partículas, cámara.
- Ángulos variados: plano general → medio → primer plano; picados/contrapicados en momentos dramáticos.
- Multitudes y fondos con **capas** (lejos más claro/difuso, cerca más oscuro y nítido), no cuadritos planos.
- Texturas suaves en suelos/paredes (ruido, vetas, ladrillos) y sombras de contacto.
### Motor de realce (motor/realce.py) — usar en TODOS los episodios
- `realce.aplicar(globals(), [<funciones de personajes>], ambiente=...)` → volumen y luz de contorno.
- En `frame()`: `img = realce.postproceso(img, T, tono=..., rayos=(x, y) si hay sol/foco)` antes de los subtítulos.
- Parpadeo de Nico con `realce.parpadeo(T)` (ver episodio de Roma mejorado como ejemplo).
### Revisión antes de publicar
Mira 6–8 fotogramas a tamaño grande (no solo la hoja pequeña) y corrige si: algo se ve plano o vacío, un
personaje está cortado o muy pequeño, el subtítulo tapa una cara, o una escena dura >4 s sin cambio.
