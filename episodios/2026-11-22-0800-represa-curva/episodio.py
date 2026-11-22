#!/usr/bin/env python3
"""¿Por qué las represas son CURVAS? (formato "¿Por qué…?" de días pares, 2026-11-22 08:00)
Estilo vector + cómic (motor/vc.py). Nico con traje de OBRERO de represa de los años 30 (casco blanco de ala completa
con banda turquesa, camisa caqui, tirantes, cinturón de herramientas turquesa). Rival: Brutus (muro recto). Juez: el
Señor Castor. Dato: la represa en arco manda el empuje del agua a las paredes del cañón; la presión crece con la
profundidad (Hoover: 221 m de alto, ~200 m de grueso en la base y ~14 m arriba)."""
import math, os, sys, subprocess
import numpy as np
from PIL import Image, ImageDraw
from scipy.io import wavfile
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "motor"))
from vc import *

FPS = 30
OUT = sys.argv[1] if len(sys.argv) > 1 else "video.mp4"
VOZ_DIR = os.path.join(HERE, "voz")
VOZ_F = sorted(f for f in os.listdir(VOZ_DIR) if f.endswith("_f.wav"))
VOZ = [wavfile.read(f"{VOZ_DIR}/{f}")[1].astype(np.float32) / 32768 for f in VOZ_F]
SR = 44100; LEAD = 0.1
DURS = [len(v) / SR + LEAD + 0.26 for v in VOZ]
DURS = [len(v) / SR + LEAD + 0.2 for v in VOZ]
DURS[0] += 0.35; DURS[1] += 0.9; DURS[9] += 0.4; DURS[10] += 0.3; DURS[16] += 0.7
CHUNKS = [
    [("¿Por qué", []), ("las represas", ["represas"]), ("son CURVAS…", ["CURVAS…"]), ("y no rectas?", ["rectas?"])],
    [("Nico cruza", []), ("el portal", ["portal"]), ("y cae en un cañón…", ["cañón…"]), ("¡justo en el gran", []), ("concurso", ["concurso"]), ("de represas!", ["represas!"])],
    [("¡Mi muro es", []), ("recto,", ["recto,"]), ("gordo y fuerte!", ["fuerte!"]), ("¡Igualito a mí!", [])],
    [("Uno.", ["Uno."]), ("Nico hace algo", []), ("rarísimo:", ["rarísimo:"]), ("dobla su muro", ["dobla"]), ("como una herradura…", ["herradura…"]), ("¡con la panza", ["panza"]), ("hacia el agua!", ["agua!"])],
    [("¿¡Curvo!?", ["¿¡Curvo!?"]), ("¡Mi familia", []), ("hace represas", ["represas"]), ("hace mil años", ["mil"]), ("y eso está chueco,", ["chueco,"]), ("muchacho!", [])],
    [("Confíe en mí,", []), ("señor Castor.", ["Castor."]), ("La curva", ["curva"]), ("es para cuando", []), ("llegue el agua", ["agua"])],
    [("Nadie le cree.", ["cree."]), ("El muro de Brutus", ["Brutus"]), ("es más grande…", ["grande…"]), ("¡y todos", []), ("le aplauden!", ["aplauden!"])],
    [("Dos.", ["Dos."]), ("Llega la tormenta.", ["tormenta."]), ("El río crece", ["crece"]), ("y el agua empuja", ["empuja"]), ("con miles", ["miles"]), ("de toneladas", ["toneladas"])],
    [("Y entre más hondo,", ["hondo,"]), ("más fuerte", ["fuerte"]), ("aprieta el agua.", []), ("Abajo empuja", ["Abajo"]), ("muchísimo más", []), ("que arriba", ["arriba"])],
    [("El muro recto", ["recto"]), ("recibe todo", []), ("el empujón", ["empujón"]), ("en el centro…", ["centro…"]), ("se dobla…", ["dobla…"]), ("¡y CRAAAC!", ["CRAAAC!"])],
    [("¡Mamá!", ["¡Mamá!"]), ("¡Mi muro", []), ("está sudando!", ["sudando!"])],
    [("Tres.", ["Tres."]), ("En la represa", []), ("de Nico,", ["Nico,"]), ("la curva manda", ["curva"]), ("el empujón", []), ("hacia los lados…", ["lados…"]), ("y la roca", ["roca"]), ("del cañón lo aguanta", ["aguanta"])],
    [("¡Es como", []), ("un arco!", ["arco!"]), ("Entre más empuja", ["empuja"]), ("el agua,", []), ("más se aprieta", ["aprieta"]), ("contra las montañas", ["montañas"])],
    [("Por eso", []), ("la represa Hoover,", ["Hoover,"]), ("de 221 metros", ["221"]), ("de alto,", []), ("mide 200 metros", ["200"]), ("de grueso abajo…", ["abajo…"]), ("y solo 14", ["14"]), ("arriba", ["arriba"])],
    [("Muchacho…", []), ("¡desde hoy eres", []), ("castor honorario!", ["castor", "honorario!"])],
    [("¿Y Brutus?", ["Brutus?"]), ("Con los pedazos", []), ("de su muro…", ["muro…"]), ("abrió un", []), ("parque acuático", ["parque", "acuático"])],
    [("Nos vemos en otro", []), ("mundo hipotético", ["hipotético"]), ("¿Qué otro secreto", ["secreto"]), ("de ingeniería quieres ver?", ["ingeniería"]), ("¡Comenta!", ["¡Comenta!"])],
]
STARTS = np.cumsum([0] + DURS).tolist(); TOTAL = STARTS[-1]
ENV = []
for v in VOZ:
    hop = SR // 60
    e = np.array([np.sqrt(np.mean(v[i:i + hop] ** 2)) for i in range(0, len(v), hop)])
    e = e / (np.percentile(e, 95) + 1e-6); ENV.append(np.convolve(e, np.ones(3) / 3, mode="same"))
def boca(k, t):
    i = int((t - LEAD) * 60)
    return float(np.clip(ENV[k][i] * 1.15 - 0.12, 0, 1)) if 0 <= i < len(ENV[k]) else 0.0

assert len(CHUNKS) == len(VOZ), (len(CHUNKS), len(VOZ))
CAPS = []
for k, (ch, v) in enumerate(zip(CHUNKS, VOZ)):
    dv = len(v) / SR; s0 = STARTS[k] + LEAD
    lens = np.array([len(c[0]) + 4 for c in ch], float); cum = np.concatenate([[0], np.cumsum(lens) / lens.sum()])
    for m, (txt, hl) in enumerate(ch):
        st = STARTS[k] if m == 0 else s0 + cum[m] * dv
        en = STARTS[k + 1] if m == len(ch) - 1 else s0 + cum[m + 1] * dv
        CAPS.append((st, en, txt, hl))

def caption(img, T, y=1660):
    for s, e, txt, hl in CAPS:
        if s <= T < e:
            words = txt.split(); size = 96
            while True:
                f = font(size); sp = f.getlength(" ")
                tot = sum(f.getlength(w) for w in words) + sp * (len(words) - 1)
                if tot <= W - 90 or size < 54: break
                size -= 6
            k = 0.65 + 0.35 * eob((T - s) / 0.14)
            f = font(size * k); sp = f.getlength(" ")
            tot = sum(f.getlength(w) for w in words) + sp * (len(words) - 1)
            d = ImageDraw.Draw(img); x = W / 2 - tot / 2
            for w in words:
                d.text((x, y), w, font=f, fill=(248, 231, 28) if w in hl else (255, 255, 255), anchor="lm", stroke_width=int(11 * k), stroke_fill=INK)
                x += f.getlength(w) + sp
            return

def mix(a, b, k): return tuple(int(lerp(a[i], b[i], k)) for i in range(3))
GLASS = (170, 214, 240)
def portal(dr, x, y, r, t, o=1.0):
    R = r * o
    if R < 4: return
    dr.ell(x, y, R, R * 1.18, (40, 16, 70), nolin=True)
    for k in range(7):
        rr = R * (1 - k * 0.12); a0 = (t * (160 + 30 * k) * (1 if k % 2 else -1)) % 360
        X, Y = dr.cam.p(x, y); rx, ry = dr.cam.s(rr), dr.cam.s(rr * 1.18)
        dr.d.arc([X - rx, Y - ry, X + rx, Y + ry], a0, a0 + 240, fill=(90, 230, 255) if k % 2 == 0 else (190, 110, 255), width=max(3, int(dr.cam.s(R * 0.05))))
        dr.dn.arc([X - rx, Y - ry, X + rx, Y + ry], a0, a0 + 240, fill=255, width=max(3, int(dr.cam.s(R * 0.05))) + 4)

def rayos_fondo(dr, cx, cy, t, c1, c2):
    dr.rrect(-900, -1200, 2000, 3200, 0, c1)
    for k in range(16):
        a = k * math.pi / 8 + t * 0.4
        dr.poly([(cx, cy), (cx + math.cos(a) * 2600, cy + math.sin(a) * 2600), (cx + math.cos(a + 0.2) * 2600, cy + math.sin(a + 0.2) * 2600)], c2)

def persona(dr, x, y, s, t, col, ph=0.0, dizzy=False, run=False):
    S = lambda v: v * s
    b = S(10) * abs(math.sin(t * (14 if run else 2) + ph))
    for sx in (-1, 1):
        a = math.sin(t * 14 + ph) * 0.6 * sx if run else 0
        dr.line([(x + sx * S(25), y - S(160)), (x + sx * S(25) + math.sin(a) * S(140), y - S(10))], (40, 40, 50), S(26))
    dr.rrect(x - S(70), y - S(400) - b, x + S(70), y - S(150) - b, S(40), col, shade=True)
    hx, hy = x, y - S(500) - b
    dr.ell(hx, hy, S(95), S(100), (236, 196, 160) if not dizzy else (200, 226, 170), shade=True)
    for sx in (-1, 1):
        ex = hx + sx * S(35)
        if dizzy:
            dr.ell(ex, hy - S(10), S(22), S(22), (255, 255, 255)); dr.ell(ex, hy - S(10), S(11), S(11), INK); dr.ell(ex, hy - S(10), S(4), S(4), (255, 255, 255))
        else:
            dr.ell(ex, hy - S(10), S(16), S(19), (255, 255, 255)); dr.ell(ex, hy - S(8), S(8), S(10), INK)
    dr.ell(hx, hy + S(50), S(24), S(10 + 12 * (dizzy or run)), (100, 24, 34))
    dr.chord(hx, hy - S(30), S(100), S(90), 180, 360, mix(col, (40, 30, 30), 0.6))

def check(img, x, y, ok, size=1.0):
    d = ImageDraw.Draw(img); r = 70 * size
    d.ellipse([x - r, y - r, x + r, y + r], fill=(80, 200, 110) if ok else (230, 60, 60), outline=INK, width=8)
    if ok: d.line([(x - r * 0.45, y), (x - r * 0.1, y + r * 0.38), (x + r * 0.5, y - r * 0.35)], fill=(255, 255, 255), width=int(18 * size))
    else:
        for s_ in (-1, 1): d.line([(x - r * 0.4, y - s_ * r * 0.4), (x + r * 0.4, y + s_ * r * 0.4)], fill=(255, 255, 255), width=int(18 * size))
# ------------------------------------------------------------ texto / gráficos encima
def burst(img, txt, x, y, size, t, col=(255, 222, 40), ang=-6):
    k = eob(t / 0.22) if t < 0.22 else 1.0
    if k <= 0.02 or t < 0: return
    f = font(size * k)
    lay = Image.new("RGBA", (int(f.getlength(txt) + 140), int(size * k * 1.7)), (0, 0, 0, 0))
    ImageDraw.Draw(lay).text((70, 16), txt, font=f, fill=col + (255,), stroke_width=int(15 * k), stroke_fill=INK)
    lay = lay.rotate(ang, resample=Image.BICUBIC, expand=True)
    img.paste(lay, (int(x - lay.width / 2), int(y - lay.height / 2)), lay)

def cartel(img, t, l1, l2, y=470, c1=(30, 40, 80), c2=(40, 140, 160)):
    k = eob(t / 0.3); d = ImageDraw.Draw(img)
    if k < 0.05: return
    d.rounded_rectangle([120, y, 960, y + 180], radius=30, fill=(250, 246, 236), outline=INK, width=8)
    d.text((540, y + 55), l1, font=font(66 * k + 1), fill=c1, anchor="mm")
    d.text((540, y + 128), l2, font=font(50 * k + 1), fill=c2, anchor="mm")

def tarjeta_paso(img, t, n, label, dur=1.5):
    """Tarjeta diagonal con número de paso que cruza la pantalla."""
    if t < 0 or t > dur: return
    u = t / dur
    x = lerp(-700, 1780, 0.5 - 0.5 * math.cos(math.pi * u)) if u < 0.2 or u > 0.8 else lerp(lerp(-700, 1780, 0.5 - 0.5 * math.cos(math.pi * 0.2)), lerp(-700, 1780, 0.5 - 0.5 * math.cos(math.pi * 0.8)), (u - 0.2) / 0.6)
    lay = Image.new("RGBA", (1100, 300), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle([10, 30, 1090, 270], radius=26, fill=(248, 231, 28, 255), outline=INK + (255,), width=10)
    d.ellipse([40, 45, 250, 255], fill=INK + (255,))
    d.text((145, 150), str(n), font=font(170), fill=(248, 231, 28, 255), anchor="mm")
    d.text((290, 150), label, font=font(92), fill=INK + (255,), anchor="lm")
    lay = lay.rotate(8, resample=Image.BICUBIC, expand=True)
    img.paste(lay, (int(x - lay.width / 2), int(480 - lay.height / 2)), lay)

def nombre(img, t, txt, sub, y=420, col=(186, 40, 44)):
    k = eob(t / 0.3)
    if k < 0.05: return
    d = ImageDraw.Draw(img); x0 = lerp(-600, 60, k)
    d.polygon([(x0, y), (x0 + 640, y), (x0 + 600, y + 110), (x0 - 40, y + 110)], fill=col, outline=INK)
    d.line([(x0, y), (x0 + 640, y), (x0 + 600, y + 110), (x0 - 40, y + 110), (x0, y)], fill=INK, width=8)
    d.text((x0 + 300, y + 55), txt, font=font(76), fill=(255, 255, 255), anchor="mm", stroke_width=6, stroke_fill=INK)
    d.rounded_rectangle([x0 + 20, y + 120, x0 + 560, y + 190], radius=14, fill=(250, 250, 250), outline=INK, width=6)
    d.text((x0 + 290, y + 155), sub, font=font(40), fill=INK, anchor="mm")

def medidor(img, t, val, x=830, y=560, label="BALANCEO"):
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([x - 200, y - 170, x + 200, y + 90], radius=24, fill=(250, 250, 246), outline=INK, width=8)
    for k in range(5):
        a0 = 180 + k * 36
        d.pieslice([x - 160, y - 140, x + 160, y + 180], a0, a0 + 36, fill=[(90, 200, 110), (170, 220, 80), (250, 210, 50), (250, 140, 40), (230, 50, 50)][k], outline=INK, width=4)
    d.pieslice([x - 90, y - 70, x + 90, y + 110], 180, 360, fill=(250, 250, 246), outline=INK, width=4)
    a = math.radians(180 + 180 * clamp(val))
    d.line([(x, y + 20), (x + math.cos(a) * 150, y + 20 + math.sin(a) * 150)], fill=INK, width=12)
    d.ellipse([x - 18, y + 2, x + 18, y + 38], fill=INK)
    d.text((x, y + 66), label, font=font(38), fill=INK, anchor="mm")

def lluvia(img, t, a=1.0, wind=1.0):
    d = ImageDraw.Draw(img)
    for k in range(int(70 * a)):
        ph = (t * 2.2 + k * 0.137) % 1
        x = (k * 131 + t * 300 * wind) % (W + 300) - 150; y = ph * (H + 200) - 100
        d.line([(x, y), (x + 40 * wind, y + 70)], fill=(190, 206, 230), width=4)

def viento(img, t, a=1.0):
    d = ImageDraw.Draw(img)
    for k in range(int(9 * a)):
        ph = (t * 1.4 + k * 0.29) % 1
        y = 300 + (k * 173) % 1200; x = lerp(-500, 1500, ph)
        pts = [(x + j * 30, y + 18 * math.sin(j * 0.6 + t * 8 + k)) for j in range(14)]
        d.line(pts, fill=(240, 246, 255), width=7)

def badge(img, T):
    d = ImageDraw.Draw(img); f = font(36); txt = "¿POR QUÉ…?"
    d.rounded_rectangle([36, 110, 36 + f.getlength(txt) + 44, 170], radius=16, fill=TURQ, outline=INK, width=5)
    d.text((58, 140), txt, font=f, fill=(255, 255, 255), anchor="lm")

def flechas(img, x, y, dirx, col, size=1.0, txt=None):
    d = ImageDraw.Draw(img); L = 150 * size
    x1 = x + dirx * L
    d.line([(x, y), (x1, y)], fill=INK, width=int(30 * size)); d.line([(x, y), (x1, y)], fill=col, width=int(18 * size))
    d.polygon([(x1 + dirx * 50 * size, y), (x1, y - 40 * size), (x1, y + 40 * size)], fill=col, outline=INK)
    if txt: d.text(((x + x1) / 2, y - 60 * size), txt, font=font(46 * size), fill=col, anchor="mm", stroke_width=7, stroke_fill=INK)

def flash(f, t, t0, d=0.15):
    if 0 <= t - t0 < d: f += 255 * (1 - (t - t0) / d)



# ------------------------------------------------------------ escenarios
ROCK = (204, 112, 70); ROCK_D = (160, 80, 52); ROCK_L = (232, 150, 96); CONC = (196, 192, 182); CONC_D = (150, 146, 138)
AGUA = (56, 136, 208); AGUA_D = (36, 96, 170); AGUA_L = (150, 210, 240)
PAS = [(220, 80, 80), (80, 120, 210), (240, 180, 60), (120, 180, 100), (180, 100, 200)]

def cielo(dr, t, storm=0.0, yh=1000):
    day = [(96, 166, 232), (130, 190, 240), (176, 214, 244), (232, 222, 200)]
    st = [(56, 62, 84), (74, 80, 104), (96, 102, 124), (120, 124, 140)]
    for k in range(4):
        dr.rrect(-1200, -1400 + k * 650, 2400, (-1400 + (k + 1) * 650 + 4) if k < 3 else 4000, 0, mix(day[k], st[k], storm), nolin=True)
    if storm < 0.5:
        dr.ell(860, 300, 80, 80, (255, 234, 120))
    for k in range(6):
        x = 1500 - ((k * 520 + t * (40 + 160 * storm)) % 2600)
        c = mix((250, 250, 252), (90, 94, 112), storm)
        for j in range(3): dr.ell(x + j * 95, 220 + (k % 3) * 110 - (j % 2) * 30, 120 + 60 * storm, 56 + 30 * storm, c, nolin=True)

def mesas(dr, yh, storm=0.0):
    far = mix((226, 168, 130), (130, 110, 110), storm); far_d = mix((196, 136, 104), (110, 92, 96), storm)
    for mx, mh, mw in ((-200, 260, 380), (260, 340, 300), (700, 280, 360), (1150, 330, 340)):
        dr.poly([(mx - mw, yh), (mx - mw * 0.6, yh - mh), (mx, yh - mh), (mx, yh)], far, nolin=True)
        dr.poly([(mx, yh - mh), (mx + mw * 0.5, yh - mh), (mx + mw, yh), (mx, yh)], far_d, nolin=True)

def pared(dr, side, g, ytop, ybot, storm=0.0):
    """Pared de cañón vista de frente. side=-1 izquierda (borde interior en x=g), +1 derecha."""
    c, cd, cl = (mix(ROCK, (110, 80, 80), storm), mix(ROCK_D, (80, 60, 64), storm), mix(ROCK_L, (140, 110, 110), storm))
    far = -1400 if side < 0 else 2500
    pts = [(far, ytop - 60), (g - side * 120, ytop - 30), (g - side * 60, ytop + 10), (g, ybot), (far, ybot + 400)]
    dr.poly(pts, c, nolin=False)
    dr.poly([(g - side * 120, ytop - 30), (g - side * 60, ytop + 10), (g, ybot), (g - side * 70, ybot)], cd, nolin=True)
    for k in range(7):
        yy = ytop + 60 + k * (ybot - ytop) / 7
        dr.line([(far, yy + 30), (g - side * (110 - k * 8), yy)], cd, 6, nolin=True)
        dr.line([(far, yy + 42), (g - side * (140 - k * 8), yy + 12)], cl, 3, nolin=True)
    for k in range(4):   # matorrales arriba
        bx = g - side * (220 + k * 170); dr.ell(bx, ytop - 50 - (k % 2) * 10, 46, 26, mix((110, 150, 80), (70, 90, 70), storm), nolin=True)

def muro_frente(dr, g0, g1, yc, ybot, t, curved=False, crack=0.0, leak=0.0, bend=0.0):
    """Muro de represa visto desde río abajo. curved → la cresta se aleja (arco hacia el agua)."""
    n = 24; top = []
    for i in range(n + 1):
        u = i / n; x = lerp(g0, g1, u)
        y = yc - (60 * math.sin(math.pi * u) if curved else 0) + bend * 40 * math.sin(math.pi * u)
        top.append((x, y))
    bot = [(g1 + 20, ybot), (g0 - 20, ybot)]
    dr.poly(top + bot, CONC, shade=False)
    if curved:   # sombreado de la curva: los lados se ven más oscuros
        for i in range(n):
            u = (i + 0.5) / n; k = abs(u - 0.5) * 2
            if k > 0.55:
                x0, x1 = lerp(g0, g1, i / n), lerp(g0, g1, (i + 1) / n)
                dr.poly([(x0, top[i][1]), (x1, top[i + 1][1]), (x1 + 10 * (1 if u > 0.5 else -1), ybot), (x0 + 10 * (1 if u > 0.5 else -1), ybot)], mix(CONC, CONC_D, (k - 0.55) / 0.45 * 0.8), nolin=True)
    for k in range(1, 6):   # juntas horizontales entre bloques
        yy = lerp(yc, ybot, k / 6)
        dr.line([(g0 - 10 * k / 6, yy + (-30 if curved else 0) * (1 - k / 6)), (g1 + 10 * k / 6, yy + (-30 if curved else 0) * (1 - k / 6))], mix(CONC, CONC_D, 0.45), 4, nolin=True)
    for k in range(1, 6):
        xx = lerp(g0, g1, k / 6)
        dr.line([(xx, top[int(k / 6 * n)][1] + 30), (xx + (xx - (g0 + g1) / 2) * 0.05, ybot)], mix(CONC, CONC_D, 0.45), 4, nolin=True)
    dr.line(top, (230, 228, 220), 18)   # pasarela de la cresta
    if crack > 0:
        cx = (g0 + g1) / 2
        for sgn in (-1, 1):
            pts = [(cx, lerp(yc, ybot, 0.25))]
            for j in range(1, 6):
                pts.append((cx + sgn * j * 40 * crack + (18 if j % 2 else -18), lerp(yc, ybot, 0.25) + j * 90 * crack))
            dr.line(pts, INK, 7)
        dr.line([(cx, lerp(yc, ybot, 0.25)), (cx + 10, yc + 4)], INK, 7)
    if leak > 0:
        cx = (g0 + g1) / 2
        for j in range(5):
            sx = cx + (j - 2) * 60; sy = lerp(yc, ybot, 0.35 + 0.08 * (j % 3))
            L = 140 * leak * (0.7 + 0.3 * math.sin(t * 20 + j))
            pts = [(sx + (j - 2) * 0.4 * q * L / 8, sy + (q * L / 8) ** 1.3 * 0.25) for q in range(9)]
            dr.line(pts, AGUA_L, 16 * leak + 2)

def agua_detras(dr, g0, g1, ylevel, ycrest, t):
    dr.poly([(g0 - 200, ylevel), (g1 + 200, ylevel), (g1 + 200, ycrest + 40), (g0 - 200, ycrest + 40)], AGUA, nolin=True)
    for k in range(5):
        yy = ylevel + 12 + k * 8
        dr.line([(g0 - 100 + ((t * 60 + k * 70) % 120), yy), (g1 + 100, yy)], AGUA_L, 3, nolin=True)

def rio_abajo(dr, g0, g1, ybot, flow=0.3, t=0.0, storm=0.0):
    c = mix((210, 176, 130), (120, 104, 96), storm)
    dr.poly([(-1400, ybot), (2500, ybot), (2500, 4000), (-1400, 4000)], c, nolin=True)
    w = lerp(60, 380, flow); cx = (g0 + g1) / 2
    dr.poly([(cx - w, ybot), (cx + w, ybot), (cx + w * 2.2, 2600), (cx - w * 2.2, 2600)], AGUA, nolin=True)
    for k in range(6):
        yy = ybot + 40 + ((t * 120 + k * 120) % 700)
        dr.line([(cx - w * 0.6, yy), (cx - w * 0.2, yy + 10)], AGUA_L, 5, nolin=True)

def escena_frente(dr, t, curved=False, storm=0.0, level=None, crack=0.0, leak=0.0, bend=0.0, g0=270, g1=810, yc=900, ybot=1500, flow=0.3):
    cielo(dr, t, storm, yh=yc - 120); mesas(dr, yc - 100, storm)
    if level is not None: agua_detras(dr, g0, g1, level, yc, t)
    pared(dr, -1, g0, yc - 80, ybot, storm); pared(dr, 1, g1, yc - 80, ybot, storm)
    muro_frente(dr, g0, g1, yc, ybot, t, curved=curved, crack=crack, leak=leak, bend=bend)
    rio_abajo(dr, g0, g1, ybot, flow, t, storm)

def canon_lejos(dr, g0, g1, ytop, ybot, t):
    """Cañón que sigue a lo lejos (cuando no hay muro): paredes difusas y el río que serpentea."""
    dr.poly([(g0 - 50, ytop), (g1 + 50, ytop), (g1 + 50, ybot), (g0 - 50, ybot)], (228, 170, 128), nolin=True)
    for k in range(4):
        yy = lerp(ytop, ybot, k / 4)
        dr.poly([(g0 - 50, yy), (lerp(g0, g1, 0.3), yy + 40), (lerp(g0, g1, 0.25), yy + 140), (g0 - 50, yy + 170)], (210, 140, 100), nolin=True)
        dr.poly([(g1 + 50, yy + 60), (lerp(g0, g1, 0.72), yy + 90), (lerp(g0, g1, 0.78), yy + 190), (g1 + 50, yy + 230)], (196, 128, 92), nolin=True)
    cx = (g0 + g1) / 2
    dr.poly([(cx - 20, ytop + 40), (cx + 20, ytop + 40), (cx + 200, ybot), (cx - 200, ybot)], AGUA, nolin=True)

# ---------- vista de pájaro (planta): el río baja de arriba (agua) hacia abajo
def planta(dr, t, tipo="recto", bend=0.0, crack=0.0, level=1.0, yd=1000, xl=330, xr=750, storm=0.0, arc=None):
    if arc is None: arc = 1.0 if tipo == "curvo" else 0.0
    sand = mix((222, 186, 132), (150, 130, 110), storm)
    dr.rrect(-1400, -1400, 2500, 3400, 0, sand, nolin=True)
    # agua arriba (embalse) y río abajo
    dr.poly([(xl - 40, -1400), (xr + 40, -1400), (xr + 10, yd), (xl - 10, yd)], mix(AGUA_D, AGUA, 0.4 + 0.6 * (1 - level)), nolin=True)
    for k in range(8):
        yy = (k * 160 + t * 50) % 1400 - 400
        if yy < yd - 60: dr.line([(xl + 40 + (k % 3) * 90, yy), (xl + 140 + (k % 3) * 90, yy + 6)], AGUA_L, 5, nolin=True)
    dr.poly([(lerp(xl, xr, 0.42), yd), (lerp(xl, xr, 0.58), yd), (lerp(xl, xr, 0.62), 3400), (lerp(xl, xr, 0.38), 3400)], AGUA, nolin=True)
    # paredes de roca (vistas desde arriba: bloques facetados)
    for side, xe in ((-1, xl), (1, xr)):
        far = -1400 if side < 0 else 2500
        pts = [(far, -1400)]
        for j in range(18):
            yy = -1400 + j * 290
            pts.append((xe + side * (18 if j % 2 else -12) + side * (60 if abs(yy - yd) > 500 else 0), yy))
        pts.append((far, 3800))
        dr.poly(pts, mix(ROCK, (110, 80, 80), storm))
        for j in range(10):
            yy = -1200 + j * 420
            dr.poly([(xe + side * 40, yy), (xe + side * 190, yy + 60), (xe + side * 120, yy + 240), (xe + side * 30, yy + 200)], mix(ROCK_L, (140, 110, 110), storm), nolin=True)
            dr.poly([(xe + side * 260, yy + 120), (xe + side * 420, yy + 160), (xe + side * 380, yy + 330)], mix(ROCK_D, (80, 60, 64), storm), nolin=True)
    # la represa
    n = 30; c_pts = []
    for i in range(n + 1):
        u = i / n; x = lerp(xl - 30, xr + 30, u)
        y = yd - 150 * arc * math.sin(math.pi * u) + bend * 170 * math.sin(math.pi * u)
        c_pts.append((x, y))
    th = 34
    poly = [(x, y - th) for x, y in c_pts] + [(x, y + th) for x, y in c_pts[::-1]]
    if arc > 0.02:   # agua detrás de la curva
        dr.poly([(xl - 10, yd - 20)] + [(x, y - th) for x, y in c_pts] + [(xr + 10, yd - 20)], mix(AGUA_D, AGUA, 0.4), nolin=True)
        dr.poly([(xl - 10, yd + 40)] + [(x, y + th) for x, y in c_pts[::-1]][::-1] + [(xr + 10, yd + 40)], sand, nolin=True)
        dr.poly([(lerp(xl, xr, 0.42), yd - 100), (lerp(xl, xr, 0.58), yd - 100), (lerp(xl, xr, 0.58), yd + 60), (lerp(xl, xr, 0.42), yd + 60)], AGUA, nolin=True)
    dr.poly(poly, CONC)
    dr.line(c_pts, (232, 230, 222), 10, nolin=True)
    if crack > 0:
        cx, cy = c_pts[n // 2]
        for sgn in (-1, 1): dr.line([(cx, cy - th), (cx + sgn * 20, cy - 10), (cx - sgn * 14, cy + 10), (cx + sgn * 10 * crack, cy + th + 30 * crack)], INK, 6)
    return c_pts

# ---------- personajes nuevos
def brutus(dr, x, y, s, t, mouth=0.0, expr="smug", arm_r=30, arm_l=30, flex=False, red=0.0, sweat=False, look=(0, 0)):
    """Brutus: constructor fortachón, camiseta sin mangas, gorra roja al revés, ceja única. Alto ≈ 1060*s."""
    S = lambda v: v * s
    bob = S(6) * math.sin(t * 2.2 + 0.5)
    skin = mix((222, 160, 118), (236, 100, 90), red)
    for sx in (-1, 1):
        dr.rrect(x + sx * S(60) - S(42), y - S(400), x + sx * S(60) + S(42), y - S(30), S(16), (78, 66, 54))
        dr.ell(x + sx * S(70), y - S(24), S(66), S(30), (60, 40, 30))
    dr.rrect(x - S(120), y - S(440), x + S(120), y - S(380), S(10), (50, 40, 34))   # cinturón
    dr.ell(x, y - S(410), S(26), S(22), (200, 200, 210))
    dr.poly([(x - S(200), y - S(880) + bob), (x + S(200), y - S(880) + bob), (x + S(120), y - S(420)), (x - S(120), y - S(420))], skin, shade=True)
    dr.poly([(x - S(130), y - S(870) + bob), (x + S(130), y - S(870) + bob), (x + S(116), y - S(430)), (x - S(116), y - S(430))], (244, 242, 236), shade=True)
    dr.rrect(x - S(118), y - S(640) + bob, x + S(118), y - S(600) + bob, S(4), (200, 50, 50))
    hands = []
    for sx, ang in ((-1, arm_l), (1, arm_r)):
        shx, shy = x + sx * S(190), y - S(840) + bob
        if flex:
            ex, ey = shx + sx * S(170), shy + S(10)
            hx, hy = ex - sx * S(10), ey - S(170)
        else:
            a = math.radians(ang)
            ex, ey = shx + sx * math.sin(a) * S(180), shy + math.cos(a) * S(180)
            hx, hy = ex + sx * math.sin(a) * S(160), ey + math.cos(a) * S(160)
        dr.line([(shx, shy), (ex, ey), (hx, hy)], skin, S(84))
        dr.ell((shx + ex) / 2, (shy + ey) / 2 - S(14), S(62), S(50), skin)   # bíceps
        dr.ell(hx, hy, S(48), S(48), skin); hands.append((hx, hy))
    hx, hy = x, y - S(990) + bob
    dr.rrect(hx - S(56), hy + S(40), hx + S(56), hy + S(130), S(20), skin)   # cuello
    dr.ell(hx, hy - S(10), S(110), S(110), skin, shade=True)
    dr.rrect(hx - S(112), hy - S(10), hx + S(112), hy + S(105), S(40), skin)   # mandíbula cuadrada
    for k in range(14): dr.ell(hx - S(80) + (k % 7) * S(27), hy + S(70) + (k // 7) * S(18), S(3), S(3), (150, 110, 90), nolin=True)
    for sx in (-1, 1):
        ex, ey = hx + sx * S(40), hy - S(6)
        big = 1.4 if expr == "shock" else 1.0
        dr.ell(ex, ey, S(17) * big, S(19) * big, (255, 255, 255))
        dr.ell(ex + look[0] * S(5), ey + look[1] * S(5), S(8), S(10), INK)
    tilt = {"angry": 16, "shock": -16, "smug": 6}.get(expr, 0)
    dr.line([(hx - S(78), hy - S(46) - S(tilt) * 0.6), (hx, hy - S(36) + S(tilt) * 0.4), (hx + S(78), hy - S(46) - S(tilt) * 0.6)], (40, 30, 26), S(16))   # ceja única
    dr.ell(hx, hy + S(26), S(20), S(16), mix(skin, (190, 110, 90), 0.4))
    mo = clamp(mouth)
    if mo > 0.06 or expr == "shock":
        dr.rrect(hx - S(46), hy + S(56), hx + S(46), hy + S(66) + S(46) * max(mo, 0.5 if expr == "shock" else 0), S(14), (100, 24, 34))
        dr.rrect(hx - S(40), hy + S(56), hx + S(40), hy + S(66), S(4), (250, 250, 250), nolin=True)
    elif expr == "smug":
        dr.line([(hx - S(40), hy + S(70)), (hx + S(10), hy + S(74)), (hx + S(44), hy + S(60))], (100, 24, 34), S(8))
    else:
        dr.chord(hx, hy + S(62), S(42), S(26), 0, 180, (100, 24, 34))
    dr.chord(hx, hy - S(44), S(114), S(96), 180, 360, (200, 46, 46))   # gorra roja al revés
    dr.rrect(hx - S(40), hy - S(66), hx + S(150), hy - S(40), S(10), (170, 34, 34))
    if sweat:
        for k in range(3):
            ph = (t * 1.6 + k / 3) % 1
            dr.ell(hx + S(120) + k * S(20), hy - S(20) + ph * S(120), S(14), S(20), (190, 230, 255))
    return dict(hands=hands, head=(hx, hy))

def castor(dr, x, y, s, t, mouth=0.0, expr="angry", arm_r=30, arm_l=30, look=(0, 0), jump=0.0, clip=True, face=1):
    """Señor Castor: juez experto en represas, viejito, gafitas redondas, cejas blancas, moño rojo. Alto ≈ 720*s."""
    S = lambda v: v * s
    y = y - S(jump); bob = S(5) * math.sin(t * 2.8)
    fur = (150, 96, 56); belly = (214, 170, 120); dark = (90, 58, 38)
    tw = math.sin(t * 3) * 6
    dr.poly([(x - face * S(60), y - S(60)), (x - face * S(330), y - S(110) + S(tw)), (x - face * S(360), y - S(10) + S(tw)), (x - face * S(80), y + S(0))], dark)   # cola
    for k in range(4): dr.line([(x - face * S(130 + k * 50), y - S(90)), (x - face * S(150 + k * 50), y - S(10))], (66, 42, 28), S(5), nolin=True)
    for sx in (-1, 1): dr.ell(x + sx * S(70), y - S(16), S(56), S(22), dark)
    dr.ell(x, y - S(250) + bob, S(170), S(230), fur, shade=True)
    dr.ell(x, y - S(220) + bob, S(110), S(160), belly)
    hands = []
    for sx, ang in ((-1, arm_l), (1, arm_r)):
        shx, shy = x + sx * S(130), y - S(380) + bob
        a = math.radians(ang)
        hx, hy = shx + sx * math.sin(a) * S(150), shy + math.cos(a) * S(150)
        dr.line([(shx, shy), (hx, hy)], fur, S(46))
        dr.ell(hx, hy, S(28), S(24), dark); hands.append((hx, hy))
    if clip:
        hx, hy = hands[0]
        dr.rrect(hx - S(70), hy - S(110), hx + S(50), hy + S(40), S(8), (180, 130, 80))
        dr.rrect(hx - S(56), hy - S(96), hx + S(36), hy + S(30), S(4), (250, 250, 246))
        for k in range(4): dr.line([(hx - S(46), hy - S(70) + k * S(26)), (hx + S(24), hy - S(70) + k * S(26))], (120, 120, 140), S(4), nolin=True)
        dr.ell(hx + S(20), hy, S(24), S(20), dark)
    for sx in (-1, 1): dr.poly([(x, y - S(462) + bob), (x + sx * S(44), y - S(484) + bob), (x + sx * S(44), y - S(440) + bob)], (200, 40, 50))
    hx, hy = x, y - S(580) + bob
    for sx in (-1, 1): dr.ell(hx + sx * S(108), hy - S(96), S(30), S(30), fur)
    dr.ell(hx, hy, S(140), S(126), fur, shade=True)
    dr.ell(hx, hy + S(50), S(84), S(60), belly)
    mo = clamp(mouth)
    if mo > 0.06: dr.ell(hx, hy + S(96), S(40), S(12 + 26 * mo), (100, 24, 34))
    dr.rrect(hx - S(30), hy + S(66), hx + S(30), hy + S(126), S(8), (252, 248, 230))   # dientes
    dr.line([(hx, hy + S(68)), (hx, hy + S(124))], INK, S(4), nolin=True)
    dr.ell(hx, hy + S(36), S(30), S(22), (40, 26, 22))
    for sx in (-1, 1):
        ex, ey = hx + sx * S(52), hy - S(24)
        dr.ell(ex, ey, S(22), S(24), (255, 255, 255))
        dr.ell(ex + look[0] * S(6), ey + look[1] * S(6), S(10), S(12), INK)
        X, Y0 = dr.cam.p(ex, ey); r = dr.cam.s(S(34))
        dr.d.ellipse([X - r, Y0 - r, X + r, Y0 + r], outline=INK, width=max(3, int(dr.cam.s(S(7)))))
        tilt = {"angry": 24, "happy": -10, "shock": -20, "proud": -6}.get(expr, 0)
        dr.line([(ex - S(34), ey - S(52) - sx * S(tilt) * 0.5), (ex + S(34), ey - S(52) + sx * S(tilt) * 0.5)], (246, 246, 240), S(16))
    for sx in (-1, 1):   # bigotes
        for k in range(2): dr.line([(hx + sx * S(40), hy + S(46) + k * S(14)), (hx + sx * S(130), hy + S(30) + k * S(30))], (60, 40, 30), S(3), nolin=True)
    return dict(hands=hands, head=(hx, hy))

def medalla(img, x, y, k=1.0):
    d = ImageDraw.Draw(img)
    d.polygon([(x - 50 * k, y - 120 * k), (x - 10 * k, y - 120 * k), (x + 10 * k, y), (x - 30 * k, y)], fill=(200, 40, 50), outline=INK)
    d.polygon([(x + 50 * k, y - 120 * k), (x + 10 * k, y - 120 * k), (x - 10 * k, y), (x + 30 * k, y)], fill=TURQ, outline=INK)
    d.ellipse([x - 60 * k, y - 20 * k, x + 60 * k, y + 100 * k], fill=(246, 200, 60), outline=INK, width=6)
    d.text((x, y + 40 * k), "C", font=font(70 * k + 1), fill=(150, 96, 56), anchor="mm")

def flecha(d, x0, y0, x1, y1, col, w=22):
    a = math.atan2(y1 - y0, x1 - x0); L = w * 2.2
    bx, by = x1 - math.cos(a) * L, y1 - math.sin(a) * L
    d.line([(x0, y0), (bx, by)], fill=INK, width=w + 12); d.line([(x0, y0), (bx, by)], fill=col, width=w)
    p = [(x1, y1), (bx + math.sin(a) * L * 0.8, by - math.cos(a) * L * 0.8), (bx - math.sin(a) * L * 0.8, by + math.cos(a) * L * 0.8)]
    d.polygon(p, fill=col, outline=INK); d.line(p + [p[0]], fill=INK, width=6)

def plano_azul(dr):
    dr.rrect(-600, -400, 1700, 2400, 0, (28, 58, 108), nolin=True)
    for k in range(-2, 16): dr.line([(k * 80, -200), (k * 80, 2200)], (44, 78, 132), 3, nolin=True)
    for k in range(-2, 30): dr.line([(-200, k * 80), (1300, k * 80)], (44, 78, 132), 3, nolin=True)

# ------------------------------------------------------------ planos
SHOTS = []
def shot(fn): SHOTS.append(fn); return fn
def tl(k, frac): return LEAD + len(VOZ[k]) / SR * frac
def D_(cam, bg=(0, 0, 0)): return D(cam, bg)

@shot
def s01(t, D, T):    # gancho: represa curva gigante en el cañón
    u = ease(t / D)
    cam = Cam(540, lerp(980, 1060, u), lerp(1.0, 1.25, u))
    dr = D_(cam); escena_frente(dr, t, curved=True, level=780, yc=860, ybot=1560, g0=200, g1=880, flow=0.2)
    for k in range(3): persona(dr, 470 + k * 60, 830 - 70 * 0, 0.08, t, PAS[k], ph=k)
    f = tinta(dr); img = acabado(f, T)
    burst(img, "¿POR QUÉ?", 540, 380, 150, t - 0.1, ang=-6)
    if t > tl(0, 0.45):
        k = eob((t - tl(0, 0.45)) / 0.3); d = ImageDraw.Draw(img)
        X0, Y0 = cam.p(200, 860); X1, Y1 = cam.p(880, 860); Xm, Ym = cam.p(540, 800)
        d.arc([X0, Ym - 40, X1, Y0 + 120], 190, 190 + 160 * k, fill=(255, 60, 60), width=14)
        d.text((Xm, Ym - 140), "¿CURVA?", font=font(90 * k + 1), fill=(255, 230, 60), anchor="mm", stroke_width=10, stroke_fill=INK)
    return img, 0

@shot
def s02(t, D, T):    # portal → Nico obrero cae en el concurso de represas
    tp = 1.3
    if t < tp:
        cam = Cam(540, 1000, 1.0)
        dr = D_(cam); rayos_fondo(dr, 540, 1000, t, (18, 10, 30), (34, 20, 56))
        portal(dr, 540, 1050, 300, t, ease(t / 0.4))
        walk = clamp((t - 0.3) / (tp - 0.4))
        if walk < 1: nico(dr, 540, 1560 - 30 * walk, 0.6 * (1 - 0.5 * walk), t, arms=(30, 30), expr="happy")
        f = tinta(dr); add_glow(f, 540, 1050, 380, (150, 120, 255), 0.5)
        if t > tp - 0.15: f += 255 * clamp((t - (tp - 0.15)) / 0.15)
        return acabado(f, T), 0
    tt = t - tp
    cam = Cam(540, 1080, lerp(0.95, 1.02, ease(tt / (D - tp))))
    dr = D_(cam); cielo(dr, t, 0, yh=900); mesas(dr, 900); canon_lejos(dr, 200, 880, 860, 1500, t)
    pared(dr, -1, 200, 820, 1500); pared(dr, 1, 880, 820, 1500)
    rio_abajo(dr, 200, 880, 1500, 0.6, t)
    for px in (150, 930): dr.rrect(px - 14, 560, px + 14, 1560, 4, (110, 76, 48))
    for k in range(9):
        bx = 160 + k * 88; by = 600 + 40 * math.sin(k / 8 * math.pi)
        dr.poly([(bx, by), (bx + 78, by + 6), (bx + 40, by + 80)], PAS[k % 5])
    for k in range(5): persona(dr, -20 + k * 270, 2060 + (k % 2) * 30, 0.42, t, PAS[k], ph=k)
    portal(dr, 620, 1150, 220, t, 1 - ease((tt - 0.7) / 0.4))
    land = clamp(tt / 0.35)
    sq = 1 - 0.3 * math.exp(-tt * 7) * math.cos(tt * 20) if land >= 1 else 1.15
    nico(dr, 600, lerp(1050, 1880, land ** 2), 0.68, t, traje="obrero", arms=(140, 140) if land < 1 else (30, 165), elbows=(0, 15), expr="shock" if tt < 0.9 else "happy", squash=sq, look=(-0.3, -0.6))
    f = tinta(dr)
    if tt < 0.2: f += 255 * (1 - tt / 0.2)
    img = acabado(f, T)
    if tt > 0.4: cartel(img, tt - 0.4, "GRAN CONCURSO", "DE REPRESAS · 1931", y=300, c2=(186, 50, 50))
    return img, 0

@shot
def s03(t, D, T):    # Brutus presume su muro recto
    u = ease(t / D)
    cam = Cam(lerp(560, 520, u), 1100, lerp(1.1, 1.2, u))
    dr = D_(cam); escena_frente(dr, t, curved=False, level=None, yc=820, ybot=1450, g0=120, g1=960)
    mo = boca(2, t)
    brutus(dr, 560, 2020, 0.92, t, mouth=mo, expr="smug" if mo < 0.3 else "happy", flex=True, look=(0.3, 0))
    f = tinta(dr); img = acabado(f, T)
    nombre(img, t - 0.1, "BRUTUS", "el muro más gordo del oeste", col=(200, 46, 46))
    if t > tl(2, 0.5): burst(img, "¡RECTO!", 800, 1240, 100, t - tl(2, 0.5), col=(230, 230, 236), ang=8)
    return img, 0

@shot
def s04(t, D, T):    # PASO 1: vista de pájaro: Nico dobla su muro hacia el agua
    k = ease(clamp((t - tl(3, 0.45)) / 1.2))
    cam = Cam(540, lerp(1000, 1040, ease(t / D)), 1.05)
    dr = D_(cam)
    pts = planta(dr, t, arc=k)
    nico(dr, 540, 1000 - 150 * k + 30, 0.30, t, traje="obrero", arms=(150, 150), expr="happy")
    f = tinta(dr); img = acabado(f, T); d = ImageDraw.Draw(img)
    tarjeta_paso(img, t, 1, "EL “ERROR”")
    d.text((540, 300), "AGUA", font=font(70), fill=(255, 255, 255), anchor="mm", stroke_width=9, stroke_fill=INK)
    if t > 1.0:
        flecha(d, 540, 360, 540, 520, AGUA_L, 20)
    if k > 0.3:
        burst(img, "¡HERRADURA!", 560, 1350, 92, t - tl(3, 0.45) - 0.4, col=(255, 230, 60), ang=-5)
    return img, 0

@shot
def s05(t, D, T):    # Señor Castor furioso
    cam = Cam(540, 1150, lerp(1.38, 1.46, ease(t / D)))
    dr = D_(cam); escena_frente(dr, t, curved=True, level=None, yc=860, ybot=1500)
    castor(dr, 540, 1880, 1.2, t, mouth=boca(4, t), expr="angry", arm_r=150 + 18 * math.sin(t * 9), arm_l=40, jump=30 * abs(math.sin(t * 6)) if t < 1.2 else 0)
    f = tinta(dr); img = acabado(f, T)
    burst(img, "¿¡CURVO!?", 540, 370, 130, t - 0.05, col=(255, 90, 70), ang=-6)
    nombre(img, t - 0.15, "SEÑOR CASTOR", "juez experto en represas", y=1400, col=(150, 96, 56))
    return img, 2 * math.sin(t * 40) if t < 1.0 else 0

@shot
def s06(t, D, T):    # Nico: confíe en mí, la curva es para cuando llegue el agua
    cam = Cam(540, 1080, 1.6)
    dr = D_(cam); escena_frente(dr, t, curved=True, level=None, yc=820, ybot=1500)
    mo = boca(5, t)
    nico(dr, 540, 1740, 0.74, t, traje="obrero", arms=(25, 125), elbows=(0, 60), expr="smug" if mo < 0.2 else "happy", mouth=mo, look=(-0.4, 0))
    f = tinta(dr); img = acabado(f, T)
    if t > tl(5, 0.55):   # tarjeta: nube de tormenta
        k = eob((t - tl(5, 0.55)) / 0.3); d = ImageDraw.Draw(img)
        x0, y0 = 610, 330
        d.rounded_rectangle([x0, y0, x0 + 380 * k + 1, y0 + 330 * k + 1], radius=20, fill=(252, 250, 244), outline=INK, width=8)
        d.rectangle([x0 + 8, y0 + 8, x0 + 380 * k - 8, y0 + 80 * k], fill=AGUA_D)
        d.text((x0 + 190 * k, y0 + 44 * k), "TORMENTA", font=font(46 * k + 1), fill=(255, 255, 255), anchor="mm")
        for j in range(3): d.ellipse([x0 + (90 + j * 70) * k - 60 * k, y0 + 160 * k, x0 + (90 + j * 70) * k + 60 * k, y0 + 240 * k], fill=(110, 116, 140), outline=INK, width=5)
        for j in range(4): d.line([(x0 + (100 + j * 60) * k, y0 + 255 * k), (x0 + (85 + j * 60) * k, y0 + 300 * k)], fill=AGUA, width=8)
    return img, 0

@shot
def s07(t, D, T):    # el muro de Brutus es más grande y todos le aplauden
    cam = Cam(540, 1150, 1.0)
    dr = D_(cam); escena_frente(dr, t, curved=False, level=None, yc=760, ybot=1450, g0=120, g1=960)
    brutus(dr, 760, 1900, 0.55, t, expr="happy", flex=True)
    nico(dr, 250, 1930, 0.5, t, traje="obrero", arms=(10, 10), expr="worried", look=(1, 0))
    for k in range(6):
        persona(dr, 400 + k * 120, 2080 + (k % 2) * 30, 0.4, t * (1.6 if k % 2 else 1.3), PAS[k % 5], ph=k, run=False)
    f = tinta(dr); img = acabado(f, T)
    for j in range(3):
        ph = (t * 1.8 + j * 0.33) % 1
        if ph < 0.45: burst(img, "¡CLAP!", 420 + j * 210, 1500 - (j % 2) * 80, 70, ph, col=(255, 255, 255), ang=-8 + j * 6)
    if t > tl(6, 0.35): burst(img, "¡MÁS GRANDE!", 560, 460, 100, t - tl(6, 0.35), col=(255, 120, 110), ang=-5)
    return img, 0

@shot
def s08(t, D, T):    # PASO 2: tormenta, el río crece y empuja
    st = ease(clamp(t / 1.2)); lv = ease(clamp((t - 0.8) / (D - 1.2)))
    cam = Cam(540, lerp(1000, 1040, ease(t / D)), 1.0)
    dr = D_(cam); escena_frente(dr, t, curved=False, storm=st, level=lerp(860, 690, lv), yc=700, ybot=1450, g0=140, g1=940, flow=0.15)
    f = tinta(dr)
    if 1.5 < t < 1.62 or 3.1 < t < 3.2: f += 160
    img = acabado(f, T)
    lluvia(img, t, st, 1.2)
    tarjeta_paso(img, t, 2, "TORMENTA")
    if t > tl(7, 0.65):
        k = eob((t - tl(7, 0.65)) / 0.3); d = ImageDraw.Draw(img)
        for j in range(3): flecha(d, 300 + j * 240, 420, 300 + j * 240, 420 + 200 * k + 10, AGUA_L, 26)
        d.text((540, 340), "¡MILES DE TONELADAS!", font=font(70 * k + 1), fill=(255, 255, 255), anchor="mm", stroke_width=10, stroke_fill=INK)
    return img, 0

@shot
def s09(t, D, T):    # corte: entre más hondo, más empuja
    cam = Cam(540, 960, 1.0)
    dr = D_(cam); plano_azul(dr)
    # agua a la izquierda, muro a la derecha (corte lateral)
    dr.poly([(60, 620), (700, 620), (700, 1420), (60, 1420)], AGUA)
    for k in range(5): dr.line([(80 + ((t * 70 + k * 130) % 560), 640 + k * 6), (160 + ((t * 70 + k * 130) % 560), 640 + k * 6)], AGUA_L, 4, nolin=True)
    dr.poly([(700, 560), (790, 560), (1000, 1420), (700, 1420)], CONC)
    dr.rrect(40, 1420, 1040, 1480, 6, (150, 110, 80))
    f = tinta(dr); img = acabado(f, T); d = ImageDraw.Draw(img)
    for j in range(6):
        tj = 0.3 + j * 0.35
        if t > tj:
            k = eob((t - tj) / 0.3); yy = 680 + j * 140; L = (60 + j * 70) * k + 10
            flecha(d, 680 - L, yy, 690, yy, (255, 140 - j * 18, 60 + j * 10), 14 + j * 3)
    d.text((360, 520), "AGUA", font=font(70), fill=(255, 255, 255), anchor="mm", stroke_width=9, stroke_fill=INK)
    d.text((300, 680), "POQUITO", font=font(44), fill=(255, 255, 255), anchor="mm", stroke_width=7, stroke_fill=INK)
    if t > 2.2: d.text((260, 1360), "¡MUCHÍSIMO!", font=font(60), fill=(255, 230, 60), anchor="mm", stroke_width=9, stroke_fill=INK)
    return img, 0

@shot
def s10(t, D, T):    # vista de pájaro: el muro recto se dobla en el centro → CRAAAC
    b = ease(clamp((t - tl(9, 0.3)) / 1.6)); cr = clamp((t - tl(9, 0.6)) / 0.6)
    cam = Cam(540, 1000, 1.05 + 0.1 * b)
    dr = D_(cam)
    planta(dr, t, "recto", bend=b * 0.7, crack=cr, storm=0.6)
    f = tinta(dr); img = acabado(f, T); d = ImageDraw.Draw(img)
    for j in range(3):
        k = eob(clamp((t - 0.2 - j * 0.15) / 0.3))
        X, Y = cam.p(450 + j * 90, 700)
        flecha(d, X, Y - 10, X, Y + 150 * k + 10, AGUA_L, 24)
    lluvia(img, t, 0.7, 1.2)
    if cr > 0: burst(img, "¡CRAAAC!", 540, 1350, 140, t - tl(9, 0.6), col=(255, 160, 60), ang=-8)
    return img, (4 * math.sin(t * 34) if 0 < cr < 1 or 0.2 < b < 0.95 else 0)

@shot
def s11(t, D, T):    # Brutus en pánico: ¡mi muro está sudando!
    cam = Cam(540, 1080, 1.25)
    lk = ease(clamp(t / 0.8))
    dr = D_(cam); escena_frente(dr, t, curved=False, storm=0.6, level=650, yc=700, ybot=1500, g0=60, g1=1020, crack=1.0, leak=lk, bend=0.6)
    brutus(dr, 540, 2020, 0.95, t, mouth=boca(10, t), expr="shock", arm_r=165, arm_l=165, red=0.3, sweat=True)
    f = tinta(dr); img = acabado(f, T)
    lluvia(img, t, 0.6, 1.2)
    burst(img, "¡GLUB GLUB!", 760, 420, 96, t - 0.3, col=(150, 220, 255), ang=6)
    return img, 2 * math.sin(t * 34)

@shot
def s12(t, D, T):    # PASO 3: la curva manda el empujón a los lados
    cam = Cam(540, 960, 1.05)
    dr = D_(cam)
    pts = planta(dr, t, "curvo", storm=0.3)
    f = tinta(dr); img = acabado(f, T); d = ImageDraw.Draw(img)
    tarjeta_paso(img, t, 3, "LA CURVA")
    k1 = eob(clamp((t - 0.6) / 0.4)); k2 = ease(clamp((t - tl(11, 0.45)) / 1.2))
    for j in (6, 12, 18, 24):
        x, y = pts[j]; X, Y = cam.p(x, y - 40)
        n = (x - 540) / 210
        flecha(d, X - n * 30, Y - 150 * k1 - 5, X, Y, AGUA_L, 18)
    if k2 > 0:
        for sgn in (-1, 1):
            j0 = 15; j1 = 0 if sgn < 0 else 30
            seq = [cam.p(*pts[int(lerp(j0, j1, q / 10))]) for q in range(int(10 * k2) + 1)]
            if len(seq) > 1:
                for a, b in zip(seq[:-1], seq[1:]): d.line([a, b], fill=INK, width=34)
                for a, b in zip(seq[:-1], seq[1:]): d.line([a, b], fill=(255, 150, 50), width=20)
                if k2 > 0.95: flecha(d, seq[-2][0], seq[-2][1], seq[-1][0] + sgn * 120, seq[-1][1] + 20, (255, 150, 50), 22)
    if k2 > 0.9:
        X, Y = cam.p(150, 1050); check(img, X, Y + 150, True, 0.9)
        X, Y = cam.p(930, 1050); check(img, X, Y + 150, True, 0.9)
        d.text((540, 1430), "¡LA ROCA LO AGUANTA!", font=font(64), fill=(255, 255, 255), anchor="mm", stroke_width=9, stroke_fill=INK)
    return img, 0

@shot
def s13(t, D, T):    # Nico: ¡es como un arco!
    cam = Cam(540, 1080, 1.55)
    dr = D_(cam); rayos_fondo(dr, 540, 900, t, (40, 150, 140), (60, 180, 166))
    nico(dr, 540, 1760, 0.74, t, traje="obrero", arms=(25, 170), elbows=(0, -10), expr="happy", mouth=boca(12, t), look=(0.3, -0.4))
    f = tinta(dr); img = acabado(f, T); d = ImageDraw.Draw(img)
    if t > tl(12, 0.1):   # icono de arco de piedra
        k = eob((t - tl(12, 0.1)) / 0.3); cx, cy, R = 800, 520, 170 * k + 1
        for j in range(9):
            a0 = math.pi + j * math.pi / 9; a1 = a0 + math.pi / 9
            pts = [(cx + math.cos(a0) * R, cy + math.sin(a0) * R), (cx + math.cos(a1) * R, cy + math.sin(a1) * R),
                   (cx + math.cos(a1) * R * 0.62, cy + math.sin(a1) * R * 0.62), (cx + math.cos(a0) * R * 0.62, cy + math.sin(a0) * R * 0.62)]
            d.polygon(pts, fill=(196, 176, 150) if j % 2 else (176, 156, 130), outline=INK)
        d.rectangle([cx - R, cy, cx - R * 0.62, cy + R * 0.9], fill=(176, 156, 130), outline=INK, width=5)
        d.rectangle([cx + R * 0.62, cy, cx + R, cy + R * 0.9], fill=(176, 156, 130), outline=INK, width=5)
        if t > tl(12, 0.4): flecha(d, cx, cy - R - 120, cx, cy - R + 10, (255, 150, 50), 16)
    if t > tl(12, 0.45): burst(img, "¡SE APRIETA!", 300, 420, 90, t - tl(12, 0.45), ang=-5)
    return img, 0

@shot
def s14(t, D, T):    # dato: represa Hoover 221 m / 200 m / 14 m
    cam = Cam(540, 960, 1.0)
    dr = D_(cam); plano_azul(dr)
    k = ease(clamp(t / 0.8))
    yb, yt = 1400, lerp(1400, 600, k)
    dr.poly([(60, lerp(1400, 660, k)), (220, lerp(1400, 660, k)), (220, yb), (60, yb)], AGUA)
    dr.poly([(220, yt), (270, yt), (940, yb), (220, yb)], CONC)
    for j in range(1, 6): dr.line([(220, lerp(yt, yb, j / 6)), (270 + (940 - 270) * j / 6, lerp(yt, yb, j / 6))], CONC_D, 4, nolin=True)
    dr.rrect(30, 1400, 1050, 1450, 6, (150, 110, 80))
    f = tinta(dr); img = acabado(f, T); d = ImageDraw.Draw(img)
    d.text((540, 300), "REPRESA HOOVER", font=font(80), fill=(255, 230, 60), anchor="mm", stroke_width=10, stroke_fill=INK)
    d.text((540, 390), "(EE. UU., 1936)", font=font(46), fill=(255, 255, 255), anchor="mm", stroke_width=7, stroke_fill=INK)
    if t > tl(13, 0.2):
        d.line([(1000, 600), (1000, 1400)], fill=(255, 255, 255), width=8)
        for yy in (600, 1400): d.line([(975, yy), (1025, yy)], fill=(255, 255, 255), width=8)
        d.text((975, 1000), "221 m", font=font(56), fill=(255, 255, 255), anchor="rm", stroke_width=8, stroke_fill=INK)
    if t > tl(13, 0.48):
        d.line([(220, 1500), (940, 1500)], fill=(255, 230, 60), width=8)
        d.text((580, 1555), "200 m", font=font(62), fill=(255, 230, 60), anchor="mm", stroke_width=8, stroke_fill=INK)
    if t > tl(13, 0.78):
        d.text((245, 520), "14 m", font=font(62), fill=(130, 240, 150), anchor="mm", stroke_width=8, stroke_fill=INK)
        flecha(d, 245, 555, 245, 600, (130, 240, 150), 12)
    return img, 0

@shot
def s15(t, D, T):    # Castor: ¡castor honorario!
    u = ease(t / D)
    cam = Cam(540, lerp(1150, 1120, u), lerp(1.15, 1.22, u))
    dr = D_(cam); escena_frente(dr, t, curved=True, level=760, yc=820, ybot=1500, flow=0.5)
    castor(dr, 760, 1900, 0.95, t, mouth=boca(14, t), expr="proud" if t < tl(14, 0.4) else "happy", arm_r=150, arm_l=40, clip=False, jump=40 * abs(math.sin(t * 5)) if t > tl(14, 0.4) else 0, look=(-1, 0))
    nico(dr, 300, 1900, 0.62, t, traje="obrero", arms=(20, 150), elbows=(0, 20), expr="happy_eyes", look=(1, 0))
    f = tinta(dr); img = acabado(f, T)
    if t > tl(14, 0.4):
        X, Y = cam.p(300, 1900 - 0.62 * 400); medalla(img, X, Y, eob((t - tl(14, 0.4)) / 0.3))
        burst(img, "¡CASTOR HONORARIO!", 540, 400, 86, t - tl(14, 0.4), ang=-5)
    return img, 0

@shot
def s16(t, D, T):    # remate: Brutus abre un parque acuático con los pedazos de su muro
    cam = Cam(540, 1060, 1.05)
    dr = D_(cam); cielo(dr, t, 0, yh=900); mesas(dr, 900); canon_lejos(dr, 120, 960, 860, 1500, t)
    pared(dr, -1, 120, 820, 1500); pared(dr, 1, 960, 820, 1500)
    rio_abajo(dr, 120, 960, 1500, 0.9, t)
    for (bx, by, w, h, a) in ((180, 1350, 220, 120, 0), (420, 1420, 260, 110, 0), (700, 1330, 240, 130, 0)):
        dr.rrect(bx, by, bx + w, by + h, 10, CONC)
    curva = lambda x: 900 + 420 * ((x - 140) / 800) ** 1.3
    for x in range(160, 900, 120): dr.rrect(x - 10, curva(x), x + 10, 1500, 4, (150, 110, 80))
    dr.line([(x, curva(x)) for x in range(140, 941, 20)], (250, 210, 60), 40)
    dr.line([(x, curva(x) - 8) for x in range(140, 941, 20)], AGUA_L, 14, nolin=True)
    cx = lerp(160, 900, (t / D) ** 1.3); cy = curva(cx)
    persona(dr, cx, cy - 10, 0.3, t, PAS[1], run=True)
    brutus(dr, 760, 2000, 0.55, t, expr="happy", arm_r=120, arm_l=20)
    dr.ell(760, 2000 - 0.55 * 420, 0.55 * 170, 0.55 * 60, (250, 120, 160))   # flotador
    for k in range(3): persona(dr, 120 + k * 160, 1980 + (k % 2) * 30, 0.4, t, PAS[k + 2], ph=k)
    f = tinta(dr); img = acabado(f, T)
    cartel(img, t - 0.3, "PARQUE ACUÁTICO", "BRUTUS · ¡ENTRADA 5 ¢!", y=300, c1=(200, 46, 46), c2=AGUA_D)
    if t > tl(15, 0.6): burst(img, "¡SPLASH!", 300, 900, 100, t - tl(15, 0.6), col=(150, 220, 255), ang=8)
    return img, 0

@shot
def s17(t, D, T):    # cierre + pregunta
    cam = Cam(540, 1000, 1.0)
    dr = D_(cam); rayos_fondo(dr, 540, 1000, -t, (18, 10, 30), (34, 20, 56))
    o = 1 - ease((t - D + 0.9) / 0.7)
    portal(dr, 540, 1080, 330, t, o)
    if t < D - 1.1:
        nico(dr, 540, 1560, 0.55, t, traje="obrero", arms=(150, 30), elbows=(30, 0), expr="happy", mouth=boca(16, t))
    f = tinta(dr); add_glow(f, 540, 1080, 450, (150, 120, 255), 0.5 * o)
    img = acabado(f, T)
    d = ImageDraw.Draw(img)
    if t > tl(16, 0.4):
        k = eob((t - tl(16, 0.4)) / 0.3)
        d.rounded_rectangle([70, 290, 1010, 560], radius=36, fill=(248, 231, 28), outline=INK, width=8)
        d.text((540, 375), "¿QUÉ OTRO SECRETO DE", font=font(56 * k + 1), fill=INK, anchor="mm")
        d.text((540, 470), "INGENIERÍA QUIERES VER?", font=font(56 * k + 1), fill=INK, anchor="mm")
        d.text((540, 640), "¡COMENTA!", font=font(80), fill=(255, 255, 255), anchor="mm", stroke_width=10, stroke_fill=INK)
    return img, 0
# ------------------------------------------------------------ cuadro
def frame(T):
    i = max(j for j in range(len(SHOTS)) if STARTS[j] <= T) if T < TOTAL else len(SHOTS) - 1
    t = T - STARTS[i]
    res, sh = SHOTS[i](t, DURS[i], T)
    img = res if isinstance(res, Image.Image) else acabado(res, T)
    if sh:
        dx, dy = sh * math.sin(T * 63), sh * math.cos(T * 51)
        img = img.transform(img.size, Image.AFFINE, (1, 0, dx, 0, 1, dy), resample=Image.BILINEAR)
    zk = 1 + 0.04 * (1 - ease(t / 0.25))
    if zk > 1.001 and i > 0:
        w2, h2 = int(W / zk), int(H / zk)
        img = img.crop(((W - w2) // 2, (H - h2) // 2, (W - w2) // 2 + w2, (H - h2) // 2 + h2)).resize((W, H), Image.BILINEAR)
    if i > 0 and t < 0.06:
        img = Image.blend(img, Image.new("RGB", (W, H), (255, 255, 255)), 0.5 * (1 - t / 0.06))
    badge(img, T)
    caption(img, T)
    return img


# ------------------------------------------------------------ sonido
def make_audio(path):
    from scipy.signal import butter, sosfilt
    sr = SR; n = int(TOTAL * sr) + sr; out = np.zeros(n)
    rng = np.random.default_rng(11)
    def add(s, sig, g=1.0):
        i0 = int(s * sr); i1 = min(n, i0 + len(sig))
        if 0 <= i0 < n: out[i0:i1] += g * sig[:i1 - i0]
    def seg(d): return np.arange(int(d * sr)) / sr
    hz = lambda m: 440 * 2 ** ((m - 69) / 12)
    noise = rng.standard_normal(n)
    bp = lambda lo, hi: sosfilt(butter(2, [lo, hi], btype="band", fs=sr, output="sos"), noise)
    wh = bp(400, 3500); low = sosfilt(butter(2, 160, btype="low", fs=sr, output="sos"), noise); rain = bp(2000, 8000)
    S_ = STARTS
    def guitarra(t0, t1, vol=1.0, e8=0.18, mel=None):   # punteo del oeste, alegre
        mel = mel or [64, 67, 71, 67, 69, 72, 71, 67, 64, 67, 69, 66, 67, 71, 74, 71]
        bass = [40, 47, 45, 47, 43, 47, 40, 47]
        k = 0; s = t0
        while s < t1:
            x = seg(e8 * 1.6); m = mel[k % len(mel)]
            pl = sum(np.sin(2 * np.pi * hz(m) * h * x) * a for h, a in ((1, 0.6), (2, 0.3), (3, 0.12), (4, 0.05)))
            add(s, vol * 0.05 * pl * np.exp(-x * 9) * (1 - np.exp(-x * 500)))
            if k % 2 == 0:
                xb = seg(e8 * 2); bm = bass[(k // 2) % len(bass)]
                add(s, vol * 0.1 * np.exp(-xb * 5) * np.sin(2 * np.pi * hz(bm) * xb))
            if k % 4 == 2: add(s, vol * 0.05 * wh[:len(x)] * np.exp(-x * 40))
            k += 1; s += e8
    def trueno(t0, g=0.5):
        x = seg(2.2); add(t0, g * low[:len(x)] * np.exp(-x * 1.6) * (1 + 0.6 * np.sin(2 * np.pi * 3 * x)))
    def chorro(t0, d, g=0.12):
        x = seg(d); add(t0, g * bp(300, 2500)[:len(x)] * np.minimum(1, x / 0.2) * np.minimum(1, (d - x) / 0.3))
    guitarra(0, S_[7])
    x = seg(1.2); add(S_[1] + 0.1, 0.12 * np.sin(2 * np.pi * (200 + 600 * x) * x) * np.sin(np.pi * x / 1.2))   # portal
    x = seg(0.5); add(S_[1] + 1.3, 0.5 * np.exp(-x * 9) * np.sin(2 * np.pi * (60 + 40 * np.exp(-x * 20)) * x))   # aterrizaje
    x = seg(0.4); add(S_[2] + 0.3, 0.2 * np.exp(-x * 8) * np.sin(2 * np.pi * 90 * x))   # Brutus flexiona
    for k in range(4): add(S_[3] + 1.0 + k * 0.3, 0.22 * np.exp(-seg(0.14) * 35) * np.sin(2 * np.pi * 1500 * seg(0.14)))   # martillo
    x = seg(0.5); add(S_[4] + 0.1, 0.12 * np.sin(2 * np.pi * (600 + 300 * np.sin(2 * np.pi * 12 * x)) * x) * np.exp(-x * 4))   # castor enojado
    for j in range(10): x = seg(0.06); add(S_[6] + 0.3 + j * 0.27, 0.18 * wh[:len(x)] * np.exp(-x * 60))   # aplausos
    # tormenta (S7..S11): lluvia de fondo + truenos
    x = seg(S_[12] - S_[7]); add(S_[7], 0.06 * rain[:len(x)] * np.minimum(1, x / 1.0) * np.minimum(1, (S_[12] - S_[7] - x) / 1.0))
    trueno(S_[7] + 1.5, 0.45); trueno(S_[7] + 3.1, 0.35); trueno(S_[9] + 0.2, 0.3)
    x = seg(DURS[8]); add(S_[8], 0.07 * np.sin(2 * np.pi * (90 + 50 * x / DURS[8]) * x) * (x / DURS[8]))   # tensión que sube
    t0 = S_[9] + tl(9, 0.3)
    x = seg(1.6); add(t0, 0.16 * np.sin(2 * np.pi * (300 - 180 * x / 1.6 + 25 * np.sin(2 * np.pi * 11 * x)) * x) * np.exp(-x * 0.9))   # crujido
    x = seg(0.8); add(S_[9] + tl(9, 0.6), 0.5 * low[:len(x)] * np.exp(-x * 5)); add(S_[9] + tl(9, 0.6), 0.25 * wh[:len(x)] * np.exp(-x * 9))   # CRAAAC
    chorro(S_[10], DURS[10], 0.14)
    x = seg(1.4); add(S_[11] + tl(11, 0.8), 0.14 * np.exp(-x * 1.2) * (np.sin(2 * np.pi * 523 * x) + np.sin(2 * np.pi * 659 * x) + np.sin(2 * np.pi * 784 * x)) / 3)   # ¡aguanta!
    guitarra(S_[12], TOTAL, 0.8, 0.16, [67, 71, 74, 71, 72, 76, 74, 71, 69, 72, 76, 72, 74, 71, 67, 71])
    x = seg(1.0); add(S_[14] + tl(14, 0.4), 0.12 * np.exp(-x * 2) * (np.sin(2 * np.pi * 784 * x) + np.sin(2 * np.pi * 988 * x) + np.sin(2 * np.pi * 1175 * x)) / 3)   # medalla
    chorro(S_[15] + 0.2, DURS[15] - 0.3, 0.06)
    x = seg(0.6); add(S_[15] + tl(15, 0.6), 0.3 * bp(200, 1500)[:len(x)] * np.exp(-x * 6))   # splash
    for k in range(1, len(S_) - 1):
        x = seg(0.3); add(S_[k] - 0.08, 0.12 * wh[:len(x)] * np.sin(np.pi * x / 0.3))
    for k in (3, 7, 11):   # tarjetas de paso
        x = seg(0.5); add(S_[k] + 0.15, 0.2 * wh[:len(x)] * np.sin(np.pi * x / 0.5)); x = seg(0.2); add(S_[k] + 0.4, 0.2 * np.exp(-x * 20) * np.sin(2 * np.pi * 900 * x))
    out = np.tanh(out * 1.3); out = out / (np.max(np.abs(out)) + 1e-9) * 0.3
    voice = np.zeros(n)
    for k, v in enumerate(VOZ):
        i0 = int((STARTS[k] + LEAD) * sr); i1 = min(n, i0 + len(v)); voice[i0:i1] += v[:i1 - i0] / (np.max(np.abs(v)) + 1e-9)
    voice *= 0.9
    env = np.convolve(np.abs(voice), np.ones(4410) / 4410, mode="same")
    mixx = out * (1 - 0.5 * np.clip(env / 0.05, 0, 1)) + voice
    mixx = mixx[:int(TOTAL * sr)]; tt = np.arange(len(mixx)) / sr
    mixx *= np.clip((TOTAL - tt) / 0.5, 0, 1); mixx = mixx / np.max(np.abs(mixx)) * 0.95
    wavfile.write(path, sr, (mixx * 32767).astype(np.int16))
if __name__ == "__main__":
    if os.environ.get("PREVIEW"):
        ts = [float(x) for x in os.environ["PREVIEW"].split(",")] if os.environ["PREVIEW"] != "all" else [STARTS[k] + DURS[k] * 0.6 for k in range(len(SHOTS))]
        ims = [frame(T).resize((270, 480)) for T in ts]
        sheet = Image.new("RGB", (270 * 6, 480 * ((len(ims) + 5) // 6)))
        for k, im in enumerate(ims): sheet.paste(im, ((k % 6) * 270, (k // 6) * 480))
        sheet.save("sheet.png"); print("TOTAL", round(TOTAL, 2), [round(s, 2) for s in STARTS]); sys.exit()
    if os.environ.get("BIG"):
        for k, T in enumerate(os.environ["BIG"].split(",")): frame(float(T)).save(f"big{k}.png")
        sys.exit()
    make_audio("audio.wav")
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-i", "audio.wav", "-c:v", "libx264", "-preset", "veryfast", "-crf", "26", "-tune", "animation", "-pix_fmt", "yuv420p",
                          "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
    N = int(TOTAL * FPS)
    for k in range(N):
        p.stdin.write(frame(k / FPS).convert("RGB").tobytes())
        if k % 300 == 0: print(f"{k}/{N}", flush=True)
    p.stdin.close(); p.wait(); print("listo", OUT, TOTAL)
