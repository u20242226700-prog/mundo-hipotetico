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
- **ESTILO OBLIGATORIO DÍAS PARES (Daniel, 2026-11-12 11:03: "este tipo de animación es el que quiero para los
  días pares", referencia TikTok @finanz_ia 7707039586471431457 — solo el ESTILO, nunca su tema).**
  Análisis vidIQ: personajes chibi de cabeza-esfera (≈40 % de la altura) con extremidades finas tipo palito,
  contorno negro grueso (4–6 px), sombreado cel de 2 tonos con corte duro (nada de degradados suaves), sets en
  3D simple con sombreado plano, presentador en cámara que habla y gesticula, cortes de 0.8–1.6 s, tarjetas
  diagonales con números de paso ("1", "2", "3") que cruzan la pantalla, iconos 2D flotantes (✗ rojas,
  estrellas, etiquetas de precio), subtítulos palabra por palabra amarillos #F8E71C con borde negro,
  empujones de cámara rápidos y sacudidas de 2 cuadros en los golpes, viñeta suave y grano bajo.
  **Cómo hacerlo aquí:** usar el MOTOR 3D clay (ver más abajo) en modo cel:
  `for m in (clay.SKIN, clay.CLOTH, clay.GLOSS, clay.HAIR, clay.STONE, clay.FUR, clay.EYE): m.toon = 1.0; m.spec = min(m.spec, 0.15); m.shin = 200; m.rim = 0.25`
  y `clay.LIGHT["ao"] = 0.25`, `render(..., outline_px=8)`. Nico es el presentador (habla a cámara con lip sync
  y voz Johan), el rival/extras con cabeza blanca (`_face(..., skin=(250,250,250))`). Estructura del guion:
  gancho → pasos numerados con tarjeta diagonal → explicación visual del secreto de ingeniería → remate.
  La plantilla 2.5D anterior (`plantillas/porque_ejemplo.py`) queda solo como respaldo.
- Exporta con `-crf 23` (el grano del realce hace pesados los archivos).
Los días IMPARES sigue el "¿Qué pasaría si…?" normal.

### 18:00 — series de 3 capítulos
Tú eliges la idea y haces todo. Cada serie = 3 videos seguidos de las 6 p. m. (días consecutivos).
- **Duración de cada capítulo: 70–100 s** (pedido de Daniel el 2026-11-12), más largos que los de la mañana. Guion de 20–28 frases, 22–30 planos, con más desarrollo: diálogo de Nico, giros y más escenas. Sigue siendo vertical 1080×1920 (Shorts admite hasta 3 min). Mantener una escena nueva cada 2–4 s para que no baje la retención.
- Capítulo 1: presenta el problema y engancha ("Parte 1/3" visible al inicio). Termina en suspenso.
- Capítulo 2: complica la situación. Termina en suspenso ("¿Cómo sale de esta? Parte 3 mañana").
- Capítulo 3: resolución + pregunta para la próxima serie ("¿Qué le ponemos en la próxima?").
- Recordatorio de 2 s al inicio de los capítulos 2 y 3 ("Antes: …").
- **MECÁNICA OBLIGATORIA "RULETA + EL PÚBLICO ELIGE"** (Daniel, 2026-11-12 11:35: "a esto me refiero con las
  series de las 6, no igual pero con ese funcionamiento"; referencia IG @ruletazombie, solo la mecánica):
  1. **Ruleta en escenario oscuro con reflectores:** al inicio gira una ruleta/tómbola y sale el reto del
     capítulo (amenaza, lugar, objeto o regla). Se ven las opciones posibles como carteles bajo luces
     (ej. "LOBO", "???", "TORMENTA") con un "???" misterioso; la ruleta frena con suspenso y sonido de clics.
  2. **Nico enfrenta lo que salió** con una regla clara del mundo ("la criatura solo ataca en la oscuridad",
     "tiene 3 objetos y 1 noche"). Reglas simples = el público puede razonar y opinar.
  3. **Final con DECISIÓN DEL PÚBLICO:** el capítulo termina en un dilema con 2 opciones numeradas en pantalla
     ("1 · Esconderse en el faro" / "2 · Huir en el bote"), congelado, y Nico/narrador pide:
     "¿Qué haría Nico? Comenta 1 o 2. En la próxima parte verás si elegiste bien."
  4. **El siguiente capítulo revela** qué pasa con la opción MÁS comentada (léela en los comentarios de TikTok
     y YouTube con Metricool/vidIQ antes de escribir el guion) y menciona "la mayoría eligió la 2…".
     Si nadie comentó, elige la opción con más tensión. El capítulo 3 cierra la historia y gira la ruleta
     de la próxima serie como avance.
  5. Texto fijo "CAPÍTULO 1/3" arriba, título de la serie con identidad propia (ej. "LA RULETA DE NICO"),
     paleta oscura con acentos rojos/neón y reflectores, en el estilo vector + cómic elegido.
  6. Descripción: "🎰 Capítulo 1/3 · <serie>\n💬 Comenta 1 o 2 y en la próxima parte verás si elegiste bien"
     + hashtags de series (#parte1…). La pregunta 1/2 es la que más comentarios genera: no la quites nunca.
Ideas de series: **La Ruleta de Nico** (ruletas de entorno/villano/objeto/estilo; la primera serie debería ser esta),
Nico en el apocalipsis zombie, Nico atrapado en un videojuego, Nico encogido en su casa, Nico náufrago,
Nico en Marte, Nico contra una IA malvada, Nico en el Titanic. Ideas de comentarios = prioridad.
Registrar en `historial.md` la serie y el capítulo (ej. "Serie: La Ruleta de Nico · 1/3") para que la siguiente
corrida de la tarde sepa por dónde va. Al terminar una serie, la siguiente arranca al día siguiente.

### IDENTIDAD PROPIA DEL CANAL (Daniel, 2026-11-12 11:41: "quiero que tengas tu temática propia, algo que nos
diferencie… a Nico puedes irle cambiando la ropa a veces")
- **Nico siempre es reconocible:** pelo de grumos marrón, ojos grandes con brillo, cachetes rosados, sonrisa
  roja. Eso NO cambia nunca.
- **"Un mundo, un traje":** Nico se viste según el mundo del episodio (cavernícola, toga romana con laurel,
  astronauta, pirata, vikingo, samurái, faraón, caballero, explorador, chef…). La sudadera turquesa es su
  traje "clásico" para episodios modernos. Hoja de vestuario: `marca/nico_vestuario.png`,
  código: `plantillas/nico_vestuario.py` (función `nico(d, sh, cx, fy, s, traje)`; agrega trajes nuevos ahí).
- **Regla de marca:** en todo traje hay SIEMPRE algo turquesa (#28BACC): tira, broche, fajín, cinturón, placa.
- **Firma de entrada:** Nico llega a cada mundo por el portal turquesa/morado (2 s al inicio) y ya sale vestido
  con el traje de ese mundo (el cambio de ropa ocurre "al cruzar").
- **Frases fijas:** abre con "¿Y si…?" (el gancho del título) y cierra con "Nos vemos en otro mundo hipotético."
  antes de la pregunta para comentar.
- No repetir el mismo traje dos días seguidos; anota el traje en `historial.md`.

### ESTILO VISUAL ELEGIDO POR DANIEL (2026-11-12 11:37): mezcla A + B — "vector plano + cómic"
Daniel dijo que el borrador 3D clay "está horrible" y que siempre salían los mismos dibujos. Se le mostró un
tablero con 3 estilos (A vector plano, B cómic, C siluetas 3D) y eligió **A y B mezclados**. Referencia:
`plantillas/estilos.py` (funciones `plano(ink=False)` = A, `plano(ink=True)` = B).
- Formas vectoriales limpias (polígonos, elipses, rectángulos redondeados), cielos en bandas posterizadas,
  montañas facetadas (cara de luz + cara de sombra), sombras largas proyectadas, grano fino.
- Encima, el acabado cómic: contorno de tinta grueso (borde entre regiones de color, ~6–8 px), trama de
  puntos (halftone) en las zonas de sombra, saturación +35 %, onomatopeyas ("¡ÑAM!", "¡BOOM!") inclinadas.
- Nico en este estilo: cabeza redonda color piel, pelo de grumos marrón, ojos grandes con brillo, cachetes
  rosados, sudadera turquesa con cordones blancos y bolsillo, pantalón azul oscuro.
- El motor clay 3D queda SOLO como respaldo (Daniel no lo quiere como estilo principal). Antes de cada
  video nuevo mira las referencias que mande Daniel y cambia de ambientación/personajes; no repetir los
  mismos dibujos de un video a otro.
- Pendiente: si Daniel activa la red, probar Blender (3D real) mezclado con este acabado cómic.

### MOTOR 3D "clay" (borrador premium del 2026-11-12, pedido de Daniel: "lo mejor de lo mejor")
Investigación (web + outliers vidIQ): lo que más vistas saca en Shorts/Reels son historias animadas con
personajes que se ven 3D, luz "real", actuación y diálogo; la tendencia 2026 es el híbrido 2D–3D.
Sin Blender aquí, así que hay un renderizador propio en numpy: `motor/clay.py` + `motor/personajes.py` +
`motor/escenario.py` (plantilla completa: `plantillas/pizza_edad_piedra.py`).
- Personajes = esferas, elipsoides, cápsulas y cajas con luz principal cálida, relleno frío, luz de borde,
  brillo especular, oclusión ambiental y contorno. La cara va PINTADA sobre la esfera (`Scene.head`), así
  gira bien en 3/4. No girar la cara más de ~30° respecto a cámara (ya está limitado en `nico()`).
- `nico(sc, x, y, z, t, arms=(…), expr=…, mouth=…, look=…, yaw=…, head_yaw=…, squash=…)`: brazos con
  presets ("down", "up", "wave", "hold", "offer", "point", "shrug", "hip", "grind", "think") o tuplas
  (hombro°, codo°, adelante). Expresiones: happy, neutral, nervous, shock, angry, sad.
  `cavernicola()` (5 variantes), `mamut()`, `pizza()`, `caja_pizza()`, `roca()`, `gema()`.
  Para otros temas crea personajes nuevos con el mismo sistema (romanos, vikingos, astronautas…).
- Ubicar en pantalla: `gp(x_pantalla, y_pies, S)` → coords de mundo; `render(sc, S, 0, 0, W, H, luz)`.
  Luz de fogata: `luz_fuego(...)`.
- **Lip sync:** la boca sigue la envolvente de la voz (`boca(k, t)`) cuando habla ese personaje.
- **Voces:** narrador Adrián (soniox). Nico habla con "Johan - Colombiano" (elevenlabs, modelo
  eleven_v3_conversational, voz 4uvQjLPvqApx1dVzpNfM, admite [excited], [nervous]). Cavernícolas/monstruos:
  openai gpt-4o-mini-tts voz "onyx" con `instructions` de actuación. Verifica con audio_transcribe.
  Cada video debe tener al menos 2 frases de diálogo de Nico (no solo narrador).
- Escenario: capas con parallax y desenfoque por profundidad (`valle()`, `componer()`, `cam_pt()`),
  efectos: fuego, humo, olor, portal, chispas, polvo, corazones, texto cómic, tarjetas ✓/✗, líneas de velocidad.
- Cortes cada 2–4 s, empujón de cámara al inicio de cada plano, barrido con desenfoque en los cortes,
  sacudida en impactos, sonido procedural sincronizado (tambores, whoosh, golpes, rugidos).
- Render: ~0.8 s por cuadro (≈18 min un video de 45 s). Probar antes con PREVIEW y BIG.

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
