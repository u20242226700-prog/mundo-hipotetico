#!/usr/bin/env python3
"""Prueba del formato de días pares: "¿Por qué…?" — ventanas de avión redondas.
Estilo: escenarios cinematográficos con profundidad (cielo, nubes, hangar en perspectiva, mapa de fuerzas),
personajes 2D (Nico vs. Bruno) encima, cámara de cine, posproceso de realce."""
import math, os, sys, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy.io import wavfile

REPO = "/home/claude/mundo-hipotetico"
src = open(f"{REPO}/episodios/2026-11-11-celular-egipto/episodio.py").read().split("\n")
exec("\n".join(src[:357]), globals())          # utilidades + nico() + egipcio() + portal + phone_big
sys.path.insert(0, f"{REPO}/motor"); import realce
OUT = sys.argv[1] if len(sys.argv) > 1 else "porque.mp4"
_NICO = nico
def nico_c(img, *a, **k): _NICO(img, *a, **k)
def bruno(img, *a, **k):
    global HOOD
    old = HOOD; HOOD = (214, 64, 58, 255)
    try: _NICO(img, *a, **k)
    finally: HOOD = old
nico_v = realce.volumen(nico_c, "frio"); bruno_v = realce.volumen(bruno, "frio")

# ------------------------------------------------------------ escenarios
def cielo(t, top=(40, 110, 200), bot=(190, 220, 245), sol=True):
    img = grad(top, bot)
    if sol: glow(img, 1050, 420, 900, (255, 240, 200), 0.7)
    lay = Image.new("RGBA", (WW, WH), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    r = np.random.default_rng(2)
    for k in range(14):
        cx = (r.uniform(-300, WW + 300) - t * (40 + k * 18)) % (WW + 600) - 300
        cy = r.uniform(300, 2000); s = r.uniform(0.6, 1.6) * (0.6 + cy / 2000)
        for j in range(5):
            ox, oy = r.uniform(-140, 140) * s, r.uniform(-40, 40) * s
            rr = r.uniform(70, 140) * s
            d.ellipse([cx + ox - rr, cy + oy - rr * 0.7, cx + ox + rr, cy + oy + rr * 0.7], fill=(255, 255, 255, 150))
    img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(18)))
    return img

def hangar():
    img = grad((40, 46, 60), (90, 96, 110))
    d = ImageDraw.Draw(img)
    vx, vy = WW / 2, 900
    d.polygon([(0, 1500), (WW, 1500), (WW, WH), (0, WH)], fill=(120, 124, 130, 255))
    for k in range(-12, 13):
        d.line([vx + k * 30, 1500, vx + k * 260, WH], fill=(100, 104, 110, 255), width=4)
    for yy in (1560, 1660, 1800, 2000, 2250): d.line([0, yy, WW, yy], fill=(100, 104, 110, 255), width=3)
    for k in range(9):  # vigas del techo
        y = 120 + k * 80
        d.line([0, y + k * 30, WW, y + k * 30], fill=(70, 76, 90, 255), width=10)
    conos = Image.new("RGBA", (WW, WH), (0, 0, 0, 0)); dc = ImageDraw.Draw(conos)
    for x in (260, 648, 1036):
        dc.polygon([(x - 40, 130), (x + 40, 130), (x + 300, 1500), (x - 300, 1500)], fill=(255, 245, 210, 34))
    img.alpha_composite(conos.filter(ImageFilter.GaussianBlur(25)))
    for x in (260, 648, 1036):
        glow(img, x, 140, 220, (255, 245, 210), 0.8)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 1380, WW, 1500], fill=(60, 64, 76, 255))
    f = font(F_BLACK, 70); d.text((60, 1395), "HANGAR 7 · 1952", font=f, fill=(250, 200, 60, 255))
    return img

def avion(img, cx, cy, L, ventanas="redondas", ang=0.0, crack=0.0, alpha=1.0, color=(236, 238, 244)):
    """Avión de perfil (pseudo-3D con degradado de volumen)."""
    W_, H_ = int(L * 1.15), int(L * 0.55)
    lay = Image.new("RGBA", (W_, H_), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    fx0, fy0, fx1, fy1 = L * 0.05, H_ * 0.40, L * 1.05, H_ * 0.64
    hh = fy1 - fy0
    d.polygon([(L * 0.12, fy0 + hh * 0.3), (L * 0.02, H_ * 0.06), (L * 0.14, H_ * 0.06), (L * 0.30, fy0)], fill=(200, 60, 60, 255))
    d.rounded_rectangle([fx0, fy0, fx1, fy1], radius=int(hh / 2), fill=color + (255,))
    d.pieslice([fx1 - hh * 1.4, fy0, fx1 + hh * 0.2, fy1], 270, 90, fill=color + (255,))
    # sombreado de volumen del fuselaje
    arr = np.array(lay).astype(np.float32)
    yy = np.arange(H_)[:, None]
    sh = 1.18 - 0.55 * np.clip((yy - fy0) / hh, 0, 1) ** 1.3
    hl = np.exp(-((yy - (fy0 + hh * 0.25)) / (hh * 0.08)) ** 2) * 60
    m = arr[..., 3] > 0
    arr[..., :3] = np.where(m[..., None], np.clip(arr[..., :3] * sh[..., None] + hl[..., None], 0, 255), arr[..., :3])
    lay = Image.fromarray(arr.astype(np.uint8)); d = ImageDraw.Draw(lay)
    d.line([fx0 + hh * 0.4, fy0 + hh * 0.55, fx1 - hh * 0.3, fy0 + hh * 0.55], fill=(40, 90, 170, 255), width=max(3, int(hh * 0.07)))
    # ala
    d.polygon([(L * 0.45, fy0 + hh * 0.7), (L * 0.62, fy0 + hh * 0.7), (L * 0.42, H_ * 0.98), (L * 0.34, H_ * 0.98)], fill=(170, 176, 190, 255))
    # cabina
    d.chord([fx1 - hh * 1.0, fy0 + hh * 0.12, fx1 - hh * 0.15, fy0 + hh * 0.5], 180, 360, fill=(40, 60, 90, 255))
    n = 12; ws = hh * (0.30 if ventanas == "redondas" else 0.42)
    for k in range(n):
        x = fx0 + hh * 1.2 + k * (L * 0.68 / n); y = fy0 + hh * 0.30
        if ventanas == "redondas":
            d.rounded_rectangle([x, y - ws * 0.05, x + ws, y + ws * 1.15], radius=int(ws * 0.5), fill=(70, 110, 160, 255), outline=(30, 40, 60, 255), width=2)
        else:
            d.rectangle([x, y - ws * 0.1, x + ws * 1.1, y + ws * 0.9], fill=(70, 110, 160, 255), outline=(30, 40, 60, 255), width=2)
            if crack > 0 and k == 6:
                cxk, cyk = x + ws * 1.1, y + ws * 0.9
                pts = [(cxk, cyk)]
                rr = np.random.default_rng(4)
                for j in range(int(2 + crack * 10)):
                    px, py = pts[-1]; pts.append((px + rr.uniform(4, 12) * L / 900, py + rr.uniform(-4, 10) * L / 900))
                d.line(pts, fill=(20, 10, 10, 255), width=max(2, int(L / 400)))
    if ang: lay = lay.rotate(ang, resample=Image.BICUBIC, expand=True)
    if alpha < 1:
        a = np.array(lay); a[..., 3] = (a[..., 3] * alpha).astype(np.uint8); lay = Image.fromarray(a)
    img.alpha_composite(lay, (int(cx - lay.width / 2), int(cy - lay.height / 2)))

_CM = None
def mapa_fuerzas(w, h, forma, presion):
    """Panel con mapa de tensión (azul→amarillo→rojo) alrededor de la ventana."""
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    cx, cy = w / 2, h / 2; a, b = w * 0.22, h * 0.30
    if forma == "cuadrada":
        dx = np.abs(xx - cx) - a; dy = np.abs(yy - cy) - b
        dist = np.sqrt(np.maximum(dx, 0) ** 2 + np.maximum(dy, 0) ** 2) + np.minimum(np.maximum(dx, dy), 0)
        inside = (dx < 0) & (dy < 0)
        corners = [(cx - a, cy - b), (cx + a, cy - b), (cx - a, cy + b), (cx + a, cy + b)]
        cdist = np.min([np.sqrt((xx - px) ** 2 + (yy - py) ** 2) for px, py in corners], axis=0)
        s = 0.25 * np.exp(-np.maximum(dist, 0) / (w * 0.10)) + 1.15 * np.exp(-cdist / (w * 0.045))
    else:
        r = np.sqrt(((xx - cx) / a) ** 2 + ((yy - cy) / b) ** 2)
        inside = r < 1
        s = 0.42 * np.exp(-np.maximum(r - 1, 0) * 3.2)
    s = np.clip(s * presion, 0, 1)
    c1 = np.array([40, 80, 200]); c2 = np.array([250, 220, 60]); c3 = np.array([240, 40, 40])
    col = np.where((s < 0.5)[..., None], c1 + (c2 - c1) * (s / 0.5)[..., None], c2 + (c3 - c2) * ((s - 0.5) / 0.5)[..., None])
    metal = np.array([150, 156, 168])
    col = metal * 0.45 + col * 0.55
    col[inside] = [30, 50, 80]
    img = Image.fromarray(np.clip(col, 0, 255).astype(np.uint8)).convert("RGBA")
    d = ImageDraw.Draw(img)
    if forma == "cuadrada": d.rectangle([cx - a, cy - b, cx + a, cy + b], outline=(20, 20, 30, 255), width=8)
    else: d.ellipse([cx - a, cy - b, cx + a, cy + b], outline=(20, 20, 30, 255), width=8)
    for k in range(0, w, 60): d.ellipse([k + 10, 14, k + 22, 26], fill=(110, 116, 126, 255)); d.ellipse([k + 10, h - 26, k + 22, h - 14], fill=(110, 116, 126, 255))
    m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], radius=40, fill=255)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0)); out.paste(img, (0, 0), m)
    return out

def etiqueta(img, txt, x, y, col, size=56):
    d = ImageDraw.Draw(img); f = font(F_BLACK, size); tw = f.getlength(txt)
    d.rounded_rectangle([x - tw / 2 - 26, y - 10, x + tw / 2 + 26, y + size + 18], radius=18, fill=col + (255,))
    d.text((x - tw / 2, y), txt, font=f, fill=(255, 255, 255, 255))

# ------------------------------------------------------------ planos (13, uno por frase)
SHOTS = []
def shot(fn): SHOTS.append(fn); return fn

@shot
def p1(t, D):  # gancho: ventana redonda gigante, cámara que se aleja
    img = cielo(t * 3)
    k = ease(t / D)
    avion(img, 648, 1150, lerp(5200, 1500, k), "redondas")
    return img, (648, 1150, 1.0 + 0.1 * (1 - k), 0)

@shot
def p2(t, D):  # hangar, dos ingenieros
    img = hangar()
    nico_v(img, 380, 1980, 1.05, "happy", arms="down", look=(1, 0))
    bruno_v(img, 920, 1980, 1.05, "smug", arms="up", phase=t * 2, look=(-1, 0))
    etiqueta(img, "NICO", 380, 1990, (36, 150, 170)); etiqueta(img, "BRUNO", 920, 1990, (190, 50, 50))
    return img, (648, 1500, 1.0 + 0.08 * ease(t / D), 0)

@shot
def p3(t, D):  # avión de Bruno: ventanas cuadradas
    img = hangar()
    avion(img, 648, 1150, 1450, "cuadradas", color=(240, 238, 232))
    bruno_v(img, 1000, 2080, 0.9, "smug", arms="phone_up", phone=False)
    etiqueta(img, "VENTANAS CUADRADAS", 560, 560, (190, 50, 50), 60)
    return img, (lerp(560, 760, ease(t / D)), 1250, 1.05, 0)

@shot
def p4(t, D):  # Nico: redondas, se burlan
    img = hangar()
    avion(img, 648, 1150, 1450, "redondas")
    nico_v(img, 300, 2080, 0.9, "worried", arms="down", look=(1, -1))
    d = ImageDraw.Draw(img); f = font(F_BLACK, 110)
    for k, (x, y) in enumerate([(820, 1750), (980, 1600), (700, 1550)]):
        if t > 0.6 + k * 0.4:
            d.text((x, y + 10 * math.sin(t * 9 + k)), "JA", font=f, fill=(255, 230, 60, 255), stroke_width=8, stroke_fill=(0, 0, 0))
    etiqueta(img, "VENTANAS REDONDAS", 680, 560, (36, 150, 170), 60)
    return img, (648, 1300, 1.05, 0)

@shot
def p5(t, D):  # aerolíneas eligen a Bruno
    img = cielo(t * 3)
    avion(img, lerp(-300, 1500, ease(t / D)), 1050, 1300, "cuadradas", ang=6)
    d = ImageDraw.Draw(img)
    for k in range(3):
        x = 300 + k * 330; y = 1750 + 30 * math.sin(t * 4 + k)
        d.rounded_rectangle([x - 130, y - 70, x + 130, y + 70], radius=16, fill=(250, 250, 240, 255), outline=(30, 30, 40, 255), width=5)
        d.text((x - 90, y - 46), "CONTRATO", font=font(F_BOLD, 40), fill=(30, 30, 40)); d.text((x - 50, y + 4), "✓", font=font(F_BLACK, 60), fill=(40, 160, 70))
    return img, (648, 1300, 1.0, 0)

@shot
def p6(t, D):  # presión: cabina se infla
    img = cielo(t * 3, (20, 50, 120), (110, 160, 220))
    p = 1 + 0.04 * math.sin(t * 5)
    avion(img, 648, 1100, 1500 * p, "cuadradas")
    d = ImageDraw.Draw(img)
    for k in range(10):
        x = 230 + k * 95; s_ = 1 if math.sin(t * 5) > 0 else -1
        d.line([x, 1100 - 150 * s_, x, 1100 - 230 * s_], fill=(255, 255, 255, 220), width=10)
        d.polygon([(x - 18, 1100 - 230 * s_), (x + 18, 1100 - 230 * s_), (x, 1100 - 265 * s_)], fill=(255, 255, 255, 220))
    etiqueta(img, "PRESIÓN ↑ ↓", 648, 1450, (40, 90, 170), 64)
    return img, (648, 1150, 1.0, 0)

@shot
def p7(t, D):  # mapa de fuerzas: esquinas al rojo
    img = grad((18, 22, 34), (30, 36, 52))
    pres = 0.3 + 0.7 * ease(t / (D * 0.6)) + 0.08 * math.sin(t * 6)
    panel = mapa_fuerzas(1000, 1000, "cuadrada", pres)
    img.alpha_composite(panel, (148, 520))
    for (px, py) in [(148 + 280, 520 + 200), (148 + 720, 520 + 200), (148 + 280, 520 + 800), (148 + 720, 520 + 800)]:
        glow(img, px, py, int(220 + 60 * math.sin(t * 8)), (255, 60, 40), 0.5 * pres)
    etiqueta(img, "TENSIÓN EN LAS ESQUINAS", 648, 380, (190, 50, 50), 58)
    return img, (648, 1020, 1.0 + 0.1 * ease(t / D), 0)

@shot
def p8(t, D):  # contador de vuelos
    img = grad((18, 22, 34), (30, 36, 52))
    panel = mapa_fuerzas(1000, 1000, "cuadrada", 1.0)
    img.alpha_composite(panel, (148, 600))
    n = int(lerp(1, 3000, ease(t / D)))
    d = ImageDraw.Draw(img); f = font(F_BLACK, 150)
    txt = f"{n:,}".replace(",", ".") + " vuelos"; tw = f.getlength(txt)
    d.text((648 - tw / 2, 330), txt, font=f, fill=(255, 214, 10), stroke_width=10, stroke_fill=(0, 0, 0))
    return img, (648, 1000, 1.0, 0)

@shot
def p9(t, D):  # ¡grieta!
    img = grad((18, 22, 34), (40, 20, 24))
    panel = mapa_fuerzas(1000, 1000, "cuadrada", 1.0)
    d = ImageDraw.Draw(panel); k = ease(t / (D * 0.7))
    x0, y0 = 500 + 220, 500 + 300
    pts = [(x0, y0)]; r = np.random.default_rng(9)
    for j in range(int(2 + 14 * k)):
        px, py = pts[-1]; pts.append((px + r.uniform(8, 22), py + r.uniform(-6, 20)))
    d.line(pts, fill=(10, 5, 5, 255), width=12)
    img.alpha_composite(panel, (148, 520))
    if t > 0.25:
        img.alpha_composite(Image.new("RGBA", img.size, (255, 0, 0, int(50 + 40 * math.sin(t * 18)))))
    return img, (648 + 260 * k, 1150 + 120 * k, 1.0 + 0.5 * k, 22 * math.exp(-t * 3))

@shot
def p10(t, D):  # aviones de Bruno en tierra
    img = cielo(t, (90, 90, 110), (170, 165, 170), sol=False)
    d = ImageDraw.Draw(img); d.rectangle([0, 1500, WW, WH], fill=(90, 92, 98, 255))
    for k, (x, y, s) in enumerate([(300, 1450, 700), (900, 1520, 820)]):
        avion(img, x, y, s, "cuadradas", crack=1.0)
    d = ImageDraw.Draw(img)
    for x in (300, 900):
        d.line([x - 160, 1220, x + 160, 1700], fill=(220, 30, 30, 255), width=24)
        d.line([x + 160, 1220, x - 160, 1700], fill=(220, 30, 30, 255), width=24)
    bruno_v(img, 648, 1900, 0.8, "scared", arms="down", look=(0, -1))
    return img, (648, 1500, 1.0 + 0.06 * ease(t / D), 0)

@shot
def p11(t, D):  # ventana redonda: fuerza repartida
    img = grad((14, 30, 40), (24, 60, 70))
    pres = 0.6 + 0.4 * ease(t / D) + 0.06 * math.sin(t * 6)
    panel = mapa_fuerzas(1000, 1000, "redonda", pres)
    img.alpha_composite(panel, (148, 520))
    etiqueta(img, "FUERZA REPARTIDA ✓", 648, 380, (36, 150, 120), 60)
    nico_v(img, 1060, 1840, 0.62, "happy", arms="up", phase=t * 3)
    return img, (648, 1150, 1.0 + 0.08 * ease(t / D), 0)

@shot
def p12(t, D):  # hoy: avión moderno volando
    img = cielo(t * 6, (30, 100, 210), (200, 230, 250))
    avion(img, lerp(1500, 300, ease(t / D)), 1050, 1500, "redondas", ang=-4, color=(245, 247, 252))
    for k in range(10):
        x = (k * 230 - t * 900) % (WW + 400) - 200
        ImageDraw.Draw(img).line([x, 900 + k * 40, x + 260, 900 + k * 40], fill=(255, 255, 255, 120), width=5)
    return img, (648, 1100, 1.05, 0)

@shot
def p13(t, D):  # cierre: Nico gana + pregunta
    img = hangar()
    avion(img, 648, 1000, 1300, "redondas")
    nico_v(img, 648, 2050, 1.1, "happy", arms="up", phase=t * 4)
    d = ImageDraw.Draw(img)
    for k in range(40):
        x = (k * 97) % WW; y = (k * 211 + t * 700) % 1500 + 300
        d.rectangle([x, y, x + 18, y + 30], fill=[(255, 214, 10), (60, 200, 255), (255, 80, 120)][k % 3] + (255,))
    return img, (648, 1500, 1.0 + 0.05 * ease(t / D), 0)

# ------------------------------------------------------------ voz y tiempos
VOZ = [wavfile.read(f"voz/v{k:02d}_f.wav")[1].astype(np.float32) / 32768 for k in range(1, 14)]
VSR = 44100; LEAD = 0.12
DURS = [len(v) / VSR + LEAD + 0.30 for v in VOZ]
DURS[0] += 0.3; DURS[8] += 0.4; DURS[-1] += 0.8
STARTS = np.cumsum([0] + DURS).tolist(); TOTAL = STARTS[-1]
CHUNKS = [
    [("¿Por qué las ventanas", []), ("de los aviones", ["aviones"]), ("son REDONDAS?", ["REDONDAS?"])],
    [("Años 50", ["50"]), ("dos ingenieros", []), ("compiten por el avión", []), ("más moderno del mundo", ["moderno"])],
    [("Bruno pone", ["Bruno"]), ("ventanas CUADRADAS", ["CUADRADAS"]), ("grandes y modernas", [])],
    [("Nico las hace", ["Nico"]), ("pequeñas y redondas", ["redondas"]), ("Todos se burlan", ["burlan"])],
    [("Las aerolíneas", []), ("eligen a Bruno", ["Bruno"])],
    [("Pero en cada vuelo", []), ("la cabina se infla", ["infla"]), ("y se desinfla", ["desinfla"])],
    [("En una ventana cuadrada", []), ("la fuerza se acumula", ["fuerza"]), ("en las ESQUINAS", ["ESQUINAS"])],
    [("Vuelo tras vuelo", []), ("el metal se cansa", ["cansa"])],
    [("Hasta que…", []), ("¡GRIETA!", ["¡GRIETA!"])],
    [("Los aviones de Bruno", ["Bruno"]), ("se quedan en tierra", ["tierra"])],
    [("En la redonda", ["redonda"]), ("la fuerza se reparte", ["reparte"]), ("No hay punto débil", ["débil"])],
    [("Por eso hoy", []), ("todas las ventanas", []), ("son redondas", ["redondas"])],
    [("¿Qué otro diseño raro", ["raro"]), ("te explico?", []), ("Coméntalo 👇", ["Coméntalo"])],
]
CAPS = []
for k, (ch, v) in enumerate(zip(CHUNKS, VOZ)):
    dv = len(v) / VSR; s0 = STARTS[k] + LEAD
    lens = np.array([len(c[0]) for c in ch], float); cum = np.concatenate([[0], np.cumsum(lens) / lens.sum()])
    for m, (txt, hl) in enumerate(ch):
        st = STARTS[k] if m == 0 else s0 + cum[m] * dv
        en = STARTS[k + 1] if m == len(ch) - 1 else s0 + cum[m + 1] * dv
        CAPS.append((st, en, txt, hl))

def text_layer(words, size, hl, stroke=10):
    f = font(F_BLACK, size); sp = f.getlength(" ")
    ws = [f.getlength(w) for w in words]; tot = sum(ws) + sp * (len(words) - 1)
    pad = stroke * 2 + 10; a, de = f.getmetrics()
    lay = Image.new("RGBA", (int(tot + pad * 2), a + de + pad * 2), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); x = pad
    for w, wd in zip(words, ws):
        d.text((x, pad), w, font=f, fill=YEL if w in hl else WHITE, stroke_width=stroke, stroke_fill=(0, 0, 0)); x += wd + sp
    return lay

def caption(img, T):
    for s, e, txt, hl in CAPS:
        if s <= T < e:
            words = txt.split(); size = 104
            while True:
                lay = text_layer(words, size, hl)
                if lay.width <= W - 60 or size < 56: break
                size -= 6
            k = 0.6 + 0.4 * eob((T - s) / 0.14)
            lay = lay.resize((max(1, int(lay.width * k)), max(1, int(lay.height * k))), Image.LANCZOS)
            img.alpha_composite(lay, (int(W / 2 - lay.width / 2), int(1620 - lay.height / 2))); return

def camera(world, cx, cy, z, shake, T):
    if shake: cx += shake * math.sin(T * 61); cy += shake * math.cos(T * 47)
    vw, vh = WW / z, WH / z
    x0 = clamp(cx - vw / 2, 0, WW - vw); y0 = clamp(cy - vh / 2, 0, WH - vh)
    return world.resize((W, H), Image.BILINEAR, box=(x0, y0, x0 + vw, y0 + vh))

def frame(T):
    i = max(j for j in range(len(SHOTS)) if STARTS[j] <= T) if T < TOTAL else len(SHOTS) - 1
    t = T - STARTS[i]
    world, (cx, cy, z, sh) = SHOTS[i](t, DURS[i])
    z *= 1 + 0.06 * (1 - ease(t / 0.25))
    img = camera(world, cx, cy, z, sh, T)
    tono = "frio" if i not in (8, 9) else "noche"
    img = realce.postproceso(img, T, tono=tono, rayos=(0.85, -0.05) if i in (0, 4, 5, 11) else None)
    # letrero fijo de formato
    d = ImageDraw.Draw(img); f = font(F_BLACK, 46)
    d.rounded_rectangle([40, 120, 40 + f.getlength("¿POR QUÉ?") + 50, 200], radius=20, fill=(255, 214, 10, 235))
    d.text((65, 132), "¿POR QUÉ?", font=f, fill=(20, 20, 30))
    caption(img, T)
    if i > 0 and t < 0.1:
        img.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(100 * (1 - t / 0.1)))))
    return img.convert("RGB")

def make_audio(path):
    from scipy.signal import butter, sosfilt
    sr = 44100; n = int(TOTAL * sr); tt = np.arange(n) / sr; out = np.zeros(n)
    def add(s, sig):
        i0 = int(s * sr); i1 = min(n, i0 + len(sig))
        if i0 < n: out[i0:i1] += sig[:i1 - i0]
    hz = lambda m: 440 * 2 ** ((m - 69) / 12)
    chords = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]
    b = 60 / 100
    for k in range(int(TOTAL / b)):
        s = k * b; ch = chords[(k // 4) % 4]
        seg = np.arange(int(b * sr)) / sr
        for m in ch: add(s, 0.025 * np.exp(-seg * 1.5) * np.sin(2 * np.pi * hz(m) * seg))
        seg2 = np.arange(int(0.2 * sr)) / sr
        if k % 2 == 0: add(s, 0.3 * np.exp(-seg2 * 18) * np.sin(2 * np.pi * (50 + 80 * np.exp(-seg2 * 30)) * seg2))
        add(s + b / 2, 0.03 * np.sin(2 * np.pi * hz(ch[k % 3] + 24) * seg2) * np.exp(-seg2 * 12))
    noise = np.random.default_rng(1).standard_normal(n)
    wn = sosfilt(butter(2, [500, 4000], btype="band", fs=sr, output="sos"), noise)
    for s in STARTS[1:-1]:
        i0 = max(0, int((s - 0.2) * sr)); i1 = min(n, int((s + 0.2) * sr)); seg = tt[i0:i1] - (s - 0.2)
        out[i0:i1] += 0.4 * np.sin(np.pi * seg / 0.4) ** 2 * wn[i0:i1]
    seg = np.arange(int(0.5 * sr)) / sr  # crack
    add(STARTS[8] + 0.3, 0.6 * np.random.default_rng(2).standard_normal(len(seg)) * np.exp(-seg * 14))
    add(STARTS[8] + 0.3, 0.6 * np.exp(-seg * 6) * np.sin(2 * np.pi * (60 + 50 * np.exp(-seg * 8)) * seg))
    for k in range(4):
        sg = np.arange(int(0.25 * sr)) / sr; add(STARTS[9] + k * 0.5, 0.08 * np.sign(np.sin(2 * np.pi * 740 * sg)))
    out = np.tanh(out); out = out / (np.max(np.abs(out)) + 1e-9) * 0.35
    voice = np.zeros(n)
    for k, v in enumerate(VOZ):
        i0 = int((STARTS[k] + LEAD) * sr); i1 = min(n, i0 + len(v)); voice[i0:i1] += v[:i1 - i0]
    voice = voice / (np.max(np.abs(voice)) + 1e-9) * 0.95
    env = np.convolve(np.abs(voice), np.ones(4410) / 4410, mode="same")
    out = out * (1 - 0.45 * np.clip(env / 0.05, 0, 1)) + voice
    out *= np.clip((TOTAL - tt) / 0.5, 0, 1); out = out / np.max(np.abs(out)) * 0.95
    wavfile.write(path, sr, (out * 32767).astype(np.int16))

if __name__ == "__main__":
    if os.environ.get("PREVIEW"):
        ts = [float(x) for x in os.environ["PREVIEW"].split(",")]
        ims = [frame(T).resize((270, 480)) for T in ts]
        sheet = Image.new("RGB", (270 * 5, 480 * ((len(ims) + 4) // 5)))
        for k, im in enumerate(ims): sheet.paste(im, ((k % 5) * 270, (k // 5) * 480))
        sheet.save("sheet.png"); print("TOTAL", TOTAL, [round(s, 1) for s in STARTS]); sys.exit()
    make_audio("audio.wav")
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-i", "audio.wav", "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p",
                          "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
    for k in range(int(TOTAL * FPS)): p.stdin.write(frame(k / FPS).tobytes())
    p.stdin.close(); p.wait(); print("listo", OUT, TOTAL)
