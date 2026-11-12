#!/usr/bin/env python3
"""LA RULETA DE NICO · Capítulo 1/3 — la ruleta cae en PIRATAS.
Estilo vector + cómic (vc.py). Mecánica: ruleta → reto → dilema final 1/2 para comentar."""
import math, os, sys, subprocess
import numpy as np
from PIL import Image, ImageDraw
from scipy.io import wavfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "motor"))
from vc import *

FPS = 30
OUT = sys.argv[1] if len(sys.argv) > 1 else "ruleta_cap1.mp4"
VOZ_DIR = os.environ.get("VOZ_DIR", "voz")
VOZ_F = sorted(os.listdir(VOZ_DIR))
VOZ = [wavfile.read(f"{VOZ_DIR}/{f}")[1].astype(np.float32) / 32768 for f in VOZ_F]
SR = 44100; LEAD = 0.1
DURS = [len(v) / SR + LEAD + 0.32 for v in VOZ]
DURS[2] += 0.5; DURS[3] += 1.1; DURS[5] += 0.6; DURS[19] += 0.6; DURS[21] += 1.6
STARTS = np.cumsum([0] + DURS).tolist(); TOTAL = STARTS[-1]
ENV = []
for v in VOZ:
    hop = SR // 60
    e = np.array([np.sqrt(np.mean(v[i:i + hop] ** 2)) for i in range(0, len(v), hop)])
    e = e / (np.percentile(e, 95) + 1e-6); ENV.append(np.convolve(e, np.ones(3) / 3, mode="same"))
def boca(k, t):
    i = int((t - LEAD) * 60)
    return float(np.clip(ENV[k][i] * 1.15 - 0.12, 0, 1)) if 0 <= i < len(ENV[k]) else 0.0

CHUNKS = [
    [("¡Bienvenidos a", []), ("LA RULETA DE NICO!", ["RULETA", "NICO!"]), ("Capítulo uno", ["uno"])],
    [("La ruleta decide", ["ruleta"]), ("a qué mundo va Nico…", ["mundo"]), ("y no puede decir que no", ["no"])],
    [("Volcán…", ["Volcán…"]), ("tiburones…", ["tiburones…"]), ("piratas…", ["piratas…"]), ("¿y se detiene en…?", [])],
    [("¡PIRATAS!", ["¡PIRATAS!"])],
    [("Ay no…", []), ("yo me mareo", ["mareo"]), ("hasta en una lancha", ["lancha"])],
    [("Nico cruza el portal", ["portal"]), ("y aparece vestido de pirata…", ["pirata…"]), ("en el mar Caribe", ["Caribe"]), ("en el año 1700", ["1700"])],
    [("¡Un polizón!", ["polizón!"]), ("¡Agárrenlo!", ["¡Agárrenlo!"])],
    [("El capitán Barbagris", ["Barbagris"]), ("tiene una sola regla", ["regla"])],
    [("Encuentras mi tesoro", ["tesoro"]), ("antes del amanecer…", ["amanecer…"]), ("o caminas por la tabla", ["tabla"])],
    [("¿Tabla?", ["¿Tabla?"]), ("¿Cuál tabla?", [])],
    [("Esa tabla.", ["tabla."]), ("La que termina justo", []), ("encima de los tiburones", ["tiburones"])],
    [("Nico solo tiene", []), ("tres cosas:", ["tres"]), ("un celular sin señal", ["celular"]), ("una brújula rota…", ["brújula"]), ("y un mapa viejo", ["mapa"])],
    [("Bueno…", []), ("el mapa marca una X", ["X"]), ("en la Isla Calavera", ["Calavera"])],
    [("Pero alguien más", []), ("quiere hablar", ["hablar"])],
    [("¡Mapa falso!", ["falso!"]), ("¡Mapa falso!", ["falso!"]), ("¡Yo sé dónde está!", ["sé"]), ("¡Yo sé!", ["sé!"])],
    [("El loro del capitán", ["loro"]), ("jura que sabe dónde está", []), ("el tesoro de verdad", ["verdad"])],
    [("Ja…", []), ("Ese loro miente", ["miente"]), ("más que yo", [])],
    [("Quedan 6 horas", ["6"]), ("para el amanecer", ["amanecer"])],
    [("Si Nico se equivoca…", ["equivoca…"]), ("termina con los tiburones", ["tiburones"])],
    [("¿Qué hace Nico?", ["Nico?"]), ("1: seguir el mapa", ["1:"]), ("hasta la Isla Calavera", ["Calavera"]), ("2: confiar en el loro", ["2:"])],
    [("Comenta 1 o 2…", ["1", "2…"]), ("¡y en la próxima parte", []), ("verás si elegiste bien!", ["bien!"])],
    [("Nos vemos en otro", []), ("mundo hipotético", ["hipotético"])],
]
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
                d.text((x, y), w, font=f, fill=(255, 214, 10) if w in hl else (255, 255, 255), anchor="lm", stroke_width=int(11 * k), stroke_fill=INK)
                x += f.getlength(w) + sp
            return

# ------------------------------------------------------------ escenarios
def escenario_ruleta(dr, t, luces=1.0):
    dr.rrect(-400, -400, 1480, 2400, 0, (34, 18, 52))
    for k in range(9):   # paneles de la pared
        x = -60 + k * 150
        dr.rrect(x, 200, x + 120, 1250, 20, (44, 24, 66))
    dr.ell(540, 1520, 820, 210, (58, 30, 86))
    dr.ell(540, 1510, 700, 160, (78, 42, 112))
    dr.rrect(-400, 1600, 1480, 2400, 0, (24, 12, 36))
    for sx in (-1, 1):   # telones
        for k in range(5):
            x0 = (540 + sx * 560) + sx * k * 70
            dr.poly([(x0, -100), (x0 + sx * 90, -100), (x0 + sx * 60 + 20 * math.sin(t + k), 1800), (x0 - sx * 10, 1800)], (160, 26, 40) if k % 2 else (130, 18, 32))
    dr.rrect(-400, -100, 1480, 60, 0, (130, 18, 32))
    if luces > 0.5 and dr.cam.z < 1.1:
        dr.text(540, 250, "LA RULETA", 120, (255, 230, 90), stroke=6)
        dr.text(540, 370, "DE NICO", 120, (90, 236, 255), stroke=6)

SEG = [("VOLCÁN", (230, 80, 50)), ("PIRATAS", (40, 186, 204)), ("???", (30, 26, 40)), ("TIBURONES", (60, 110, 200)),
       ("DINOS", (90, 170, 70)), ("ESPACIO", (110, 70, 190)), ("ZOMBIS", (120, 160, 90)), ("HIELO", (170, 220, 240))]
def ruleta(dr, cx, cy, r, ang, t, glow_seg=None):
    dr.ell(cx, cy, r * 1.12, r * 1.12, (60, 40, 30))
    dr.ell(cx, cy, r * 1.06, r * 1.06, (230, 190, 60))
    for i, (name, col) in enumerate(SEG):
        a0 = -90 - 22.5 + i * 45 + ang
        c = col if glow_seg != i or int(t * 8) % 2 else (255, 255, 255)
        dr.pie(cx, cy, r, a0, a0 + 45, c)
    for i, (name, col) in enumerate(SEG):
        a = math.radians(-90 + i * 45 + ang)
        tx, ty = cx + math.cos(a) * r * 0.64, cy + math.sin(a) * r * 0.64
        dr.text(tx, ty, name, 28 if len(name) > 6 else 36, (255, 255, 255), stroke=4)
    for k in range(16):
        a = math.radians(k * 22.5 + ang * 0.0)
        on = (int(t * 10) + k) % 2 == 0
        dr.ell(cx + math.cos(a) * r * 1.09, cy + math.sin(a) * r * 1.09, r * 0.035, r * 0.035, (255, 245, 180) if on else (150, 110, 40), nolin=True)
    dr.ell(cx, cy, r * 0.16, r * 0.16, (230, 190, 60))
    dr.ell(cx, cy, r * 0.08, r * 0.08, TURQ)
    dr.poly([(cx - r * 0.13, cy - r * 1.22), (cx + r * 0.13, cy - r * 1.22), (cx, cy - r * 0.95)], (230, 40, 50))

SPIN_T0, SPIN_T1 = None, None
def ang_ruleta(T):
    t0, t1 = STARTS[1] + 2.4, STARTS[3] + 0.15
    final = -45 - 360 * 5
    if T < t0: return 0.0
    u = clamp((T - t0) / (t1 - t0))
    return final * (1 - (1 - u) ** 3)

def cielo_noche(dr, t):
    for k, c in enumerate([(12, 16, 40), (16, 22, 52), (22, 30, 66), (30, 40, 82)]):
        dr.rrect(-500, -900 + k * 420, 1600, -900 + (k + 1) * 420 + 2, 0, c)
    mar(dr, t, 760)
    rng = np.random.default_rng(4)
    for k in range(60):
        x, y = rng.uniform(-300, 1400), rng.uniform(-500, 700)
        r = rng.uniform(2, 5) * (0.7 + 0.3 * math.sin(t * 3 + k))
        dr.ell(x, y, r, r, (255, 250, 220), nolin=True)
    dr.ell(820, 160, 120, 120, (250, 236, 190), shade=True)
    for (a, b, r) in ((-30, -20, 22), (40, 30, 16), (10, 60, 12)): dr.ell(820 + a, 160 + b, r, r, (230, 214, 168))

def mar(dr, t, y0=760, col=(22, 54, 96)):
    dr.rrect(-500, y0, 1600, 2600, 0, col)
    for k in range(9):
        yy = y0 + 30 + k * k * 9 + k * 30
        off = (t * (30 + k * 12)) % 160
        for j in range(-4, 12):
            x = -300 + j * 160 + off * (1 if k % 2 else -1)
            dr.line([(x, yy), (x + 40, yy - 8 - k), (x + 80, yy)], (60, 110, 160), 5 + k * 0.8)

def cubierta(dr, t, y0=1180):
    dr.poly([(-500, y0), (1600, y0), (1600, 2600), (-500, 2600)], (128, 80, 46))
    for k in range(1, 14):
        yy = y0 + k * k * 6 + k * 18
        dr.line([(-500, yy), (1600, yy)], (100, 60, 36), 5)
    for k in range(-8, 9):
        dr.line([(540 + k * 70, y0), (540 + k * 260, 2600)], (110, 68, 40), 4)
    dr.rrect(-500, y0 - 110, 1600, y0 - 80, 6, (100, 62, 36))
    for k in range(-6, 16):
        dr.rrect(k * 110 - 12, y0 - 110, k * 110 + 12, y0, 4, (100, 62, 36))

def mastil(dr, t, x=150):
    dr.rrect(x - 40, -800, x + 40, 1200, 10, (92, 58, 36), shade=True)
    dr.poly([(x + 40, -400), (x + 520 + 20 * math.sin(t), -320), (x + 500 + 30 * math.sin(t * 1.3), 380), (x + 40, 420)], (236, 226, 200), shade=True)
    dr.ell(x + 280, 0, 90, 80, (40, 34, 40)); dr.ell(x + 250, -20, 20, 22, (236, 226, 200)); dr.ell(x + 310, -20, 20, 22, (236, 226, 200))
    dr.line([(x, -700), (1200, 1100)], (70, 50, 40), 6)

def farol(dr, f, x, y, t):
    dr.rrect(x - 30, y - 50, x + 30, y + 40, 8, (250, 210, 90))
    dr.rrect(x - 36, y - 62, x + 36, y - 46, 4, (60, 50, 40))
    X, Y = dr.cam.p(x, y)
    return (X, Y)

def portal(dr, x, y, r, t, o=1.0):
    R = r * o
    if R < 4: return
    dr.ell(x, y, R, R * 1.18, (40, 16, 70), nolin=True)
    for k in range(7):
        rr = R * (1 - k * 0.12); a0 = (t * (160 + 30 * k) * (1 if k % 2 else -1)) % 360
        X, Y = dr.cam.p(x, y); rx, ry = dr.cam.s(rr), dr.cam.s(rr * 1.18)
        dr.d.arc([X - rx, Y - ry, X + rx, Y + ry], a0, a0 + 240, fill=(90, 230, 255) if k % 2 == 0 else (190, 110, 255), width=max(3, int(dr.cam.s(R * 0.05))))
        dr.dn.arc([X - rx, Y - ry, X + rx, Y + ry], a0, a0 + 240, fill=255, width=max(3, int(dr.cam.s(R * 0.05))) + 4)

# ------------------------------------------------------------ utilería
def celular(dr, x, y, s, t):
    S = lambda v: v * s
    dr.rrect(x - S(70), y - S(130), x + S(70), y + S(130), S(22), (30, 30, 38))
    dr.rrect(x - S(58), y - S(110), x + S(58), y + S(110), S(10), (90, 140, 200))
    for k in range(4): dr.rrect(x - S(40) + k * S(20), y - S(10) - k * S(14), x - S(28) + k * S(20), y + S(30), S(2), (200, 210, 220))
    dr.line([(x - S(48), y - S(60)), (x + S(48), y + S(50))], (230, 50, 50), S(12))
    dr.text(x, y + S(78), "SIN SEÑAL", S(24), (255, 255, 255))

def brujula(dr, x, y, s, t):
    S = lambda v: v * s
    dr.ell(x, y, S(120), S(120), (210, 170, 70), shade=True)
    dr.ell(x, y, S(98), S(98), (246, 238, 214))
    a = t * 9 + math.sin(t * 13) * 2
    dr.poly([(x + math.cos(a) * S(85), y + math.sin(a) * S(85)), (x + math.cos(a + 1.6) * S(12), y + math.sin(a + 1.6) * S(12)), (x + math.cos(a + 3.14) * S(60), y + math.sin(a + 3.14) * S(60)), (x + math.cos(a - 1.6) * S(12), y + math.sin(a - 1.6) * S(12))], (220, 50, 50))
    dr.line([(x - S(60), y - S(80)), (x - S(10), y - S(20)), (x - S(30), y + S(20)), (x + S(40), y + S(90))], INK, S(5))
    dr.text(x, y - S(70), "N", S(30), INK)

def mapa(dr, x, y, s, t, x_glow=1.0, full=True):
    S = lambda v: v * s
    pts = [(x - S(300), y - S(220)), (x - S(200), y - S(240)), (x - S(60), y - S(215)), (x + S(120), y - S(240)), (x + S(300), y - S(210)),
           (x + S(320), y + S(60)), (x + S(290), y + S(230)), (x + S(80), y + S(215)), (x - S(120), y + S(240)), (x - S(310), y + S(210))]
    dr.poly(pts, (236, 214, 160), shade=False)
    if not full: return
    dr.poly([(x - S(230), y + S(60)), (x - S(170), y - S(40)), (x - S(90), y - S(30)), (x - S(60), y + S(70)), (x - S(150), y + S(130))], (150, 190, 110))
    sx, sy = x + S(160), y - S(40)
    dr.ell(sx, sy, S(110), S(95), (210, 200, 180))
    dr.ell(sx - S(38), sy - S(10), S(26), S(30), (60, 50, 50)); dr.ell(sx + S(38), sy - S(10), S(26), S(30), (60, 50, 50))
    dr.poly([(sx - S(10), sy + S(25)), (sx + S(10), sy + S(25)), (sx, sy + S(45))], (60, 50, 50))
    for k in range(9):
        u = k / 8
        px, py = lerp(x - S(140), sx - S(20), u), lerp(y + S(40), sy + S(110), u) + math.sin(u * 6) * S(30)
        dr.ell(px, py, S(9), S(9), (160, 60, 50), nolin=True)
    k = 1 + 0.15 * math.sin(t * 8) * x_glow
    cx, cy = sx + S(10), sy + S(130)
    dr.line([(cx - S(40) * k, cy - S(40) * k), (cx + S(40) * k, cy + S(40) * k)], (220, 30, 40), S(18))
    dr.line([(cx + S(40) * k, cy - S(40) * k), (cx - S(40) * k, cy + S(40) * k)], (220, 30, 40), S(18))
    dr.text(x - S(10), y + S(180), "ISLA CALAVERA", S(40), (110, 60, 40), f=F_SERIF)

def burst(img, txt, x, y, size, t, col=(255, 222, 40), ang=-6):
    k = eob(t / 0.22) if t < 0.22 else 1.0
    if k <= 0.02: return
    f = font(size * k)
    lay = Image.new("RGBA", (int(f.getlength(txt) + 140), int(size * k * 1.7)), (0, 0, 0, 0))
    ImageDraw.Draw(lay).text((70, 16), txt, font=f, fill=col + (255,), stroke_width=int(15 * k), stroke_fill=INK)
    lay = lay.rotate(ang, resample=Image.BICUBIC, expand=True)
    img.paste(lay, (int(x - lay.width / 2), int(y - lay.height / 2)), lay)

def tarjeta_nombre(img, t, nombre, sub):
    k = eob(t / 0.3)
    lay = Image.new("RGBA", (W, 420), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    off = (1 - k) * -W
    d.polygon([(off, 80), (off + W, 20), (off + W, 300), (off, 360)], fill=(230, 40, 50, 255), outline=INK, width=10)
    d.text((off + 70, 120), nombre, font=font(92), fill=(255, 255, 255), stroke_width=8, stroke_fill=INK)
    d.text((off + 76, 236), sub, font=font(46), fill=(255, 222, 60), stroke_width=6, stroke_fill=INK)
    img.paste(lay, (0, 260), lay)

def badge(img, T):
    d = ImageDraw.Draw(img)
    f = font(36)
    d.rounded_rectangle([36, 110, 36 + f.getlength("LA RULETA DE NICO") + 44, 170], radius=16, fill=(230, 40, 50), outline=INK, width=5)
    d.text((58, 140), "LA RULETA DE NICO", font=f, fill=(255, 255, 255), anchor="lm")
    f2 = font(36); txt = "CAPÍTULO 1/3"
    x1 = W - 36; x0 = x1 - f2.getlength(txt) - 44
    d.rounded_rectangle([x0, 110, x1, 170], radius=16, fill=(255, 214, 10), outline=INK, width=5)
    d.text((x0 + 22, 140), txt, font=f2, fill=INK, anchor="lm")

# ------------------------------------------------------------ planos
SHOTS = []
def shot(fn): SHOTS.append(fn); return fn
def tl(k, frac): return LEAD + len(VOZ[k]) / SR * frac   # tiempo local de una fracción de la frase k

@shot
def s01(t, D, T):    # escenario se enciende, Nico saluda
    on = t > 0.35
    cam = Cam(540, 1000, lerp(1.0, 1.06, ease(t / D)))
    dr = D_(cam); escenario_ruleta(dr, t, 1.0 if on else 0.0)
    ruleta(dr, 760, 960, 260, 0, t)
    nico(dr, 300, 1560, 0.62, t, arms=(150, 20), elbows=(30, 0), expr="happy", mouth=0)
    f = tinta(dr)
    if on:
        for x in (300, 760): add_cono(f, x, -50, 1600, 60, 520, (255, 236, 180), 0.32)
        add_glow(f, 540, 300, 380, (255, 120, 200), 0.35)
    else: f *= 0.35
    return f, 0

@shot
def s02(t, D, T):    # Nico nervioso / la ruleta empieza a girar
    if t < D * 0.5:
        cam = Cam(330, 1100, 1.45)
        dr = D_(cam); escenario_ruleta(dr, t)
        nico(dr, 300, 1560, 0.62, t, arms=(25, 25), elbows=(-40, -40), expr="nervous", sweat=True)
        f = tinta(dr); add_cono(f, W / 2, -50, 1900, 100, 900, (255, 236, 180), 0.28)
        return f, 0
    cam = Cam(760, 960, 1.5)
    dr = D_(cam); escenario_ruleta(dr, t); ruleta(dr, 760, 960, 260, ang_ruleta(T), t)
    f = tinta(dr); add_cono(f, W / 2, -50, 1900, 120, 1000, (255, 236, 180), 0.25)
    return f, 0

@shot
def s03(t, D, T):    # gira: volcán… tiburones… piratas…
    cut = t > tl(2, 0.55) and t < tl(2, 0.8)
    if cut:
        cam = Cam(300, 1080, 1.9)
        dr = D_(cam); escenario_ruleta(dr, t)
        nico(dr, 300, 1560, 0.62, t, arms=(20, 20), elbows=(-120, -120), expr="shock", look=(0.8, -0.3))
        f = tinta(dr); add_glow(f, W / 2, H / 2, 600, (255, 200, 120), 0.2)
        return f, 3
    z = 1.5 + 0.3 * ease(t / D)
    cam = Cam(760, 860, z)
    dr = D_(cam); escenario_ruleta(dr, t); ruleta(dr, 760, 960, 260, ang_ruleta(T), t)
    f = tinta(dr); add_glow(f, *cam.p(760, 700), 300, (255, 240, 180), 0.35)
    return f, 2 * math.sin(T * 40)

@shot
def s04(t, D, T):    # ¡PIRATAS!
    cam = Cam(760, 900, 1.65 - 0.1 * eob(t / 0.3))
    dr = D_(cam); escenario_ruleta(dr, t); ruleta(dr, 760, 960, 260, ang_ruleta(T), t, glow_seg=1)
    f = tinta(dr)
    add_glow(f, *cam.p(760, 760), 420, (120, 240, 255), 0.6 * math.exp(-t * 1.5))
    img = acabado(f, T)
    burst(img, "¡PIRATAS!", 540, 460, 170, t, ang=-7)
    d = ImageDraw.Draw(img); rng = np.random.default_rng(int(t * 20))
    for k in range(60):
        ph = (t * 0.9 + k / 60) % 1
        x = (k * 137) % W; y = -50 + ph * 1900
        d.rectangle([x, y, x + 16, y + 26], fill=[(255, 214, 10), (40, 186, 204), (230, 40, 50), (255, 255, 255)][k % 4])
    return img, 14 * math.exp(-t * 5)

@shot
def s05(t, D, T):    # Nico: me mareo hasta en una lancha
    cam = Cam(300, 1080, 1.7)
    dr = D_(cam); escenario_ruleta(dr, t)
    sway = 0.3 * math.sin(t * 3)
    nico(dr, 300 + 8 * math.sin(t * 3), 1560, 0.62, t, arms=(20, 40), elbows=(-130, 0), expr="worried", mouth=boca(4, t), sick=t > 0.6, look=(sway, 0.3))
    f = tinta(dr); add_cono(f, W / 2, -50, 1900, 100, 900, (255, 236, 180), 0.25)
    img = acabado(f, T)
    if t > 0.8:
        d = ImageDraw.Draw(img)
        for k in range(3):
            a = t * 3 + k * 2.1
            x, y = 540 + math.cos(a) * 260, 520 + math.sin(a) * 60
            d.text((x, y), "@", font=font(70), fill=(160, 220, 120), anchor="mm", stroke_width=6, stroke_fill=INK)
    return img, 0

@shot
def s06(t, D, T):    # cruza el portal → aparece vestido de pirata en el barco
    tp = D * 0.42
    if t < tp:
        cam = Cam(540, 1080, 1.15)
        dr = D_(cam); escenario_ruleta(dr, t)
        o = ease(t / 0.5)
        portal(dr, 650, 1240, 230, t, o)
        walk = clamp((t - 0.6) / (tp - 0.8))
        if walk < 1: nico(dr, lerp(300, 650, walk), 1560 - 20 * abs(math.sin(t * 9)), 0.62 * (1 - 0.4 * walk), t, arms=(30, 30), expr="nervous")
        f = tinta(dr); add_glow(f, *cam.p(650, 1240), 330, (150, 120, 255), 0.6 * o)
        if t > tp - 0.15: f += 255 * clamp((t - (tp - 0.15)) / 0.15)
        return f, 0
    tt = t - tp
    cam = Cam(540, 1050, lerp(1.0, 1.08, ease(tt / (D - tp))))
    dr = D_(cam); cielo_noche(dr, t); mar(dr, t); mastil(dr, t, 120); cubierta(dr, t)
    portal(dr, 620, 1100, 200, t, 1 - ease((tt - 1.0) / 0.5))
    land = clamp(tt / 0.35)
    sq = 1 - 0.3 * math.exp(-tt * 7) * math.cos(tt * 20) if land >= 1 else 1.15
    ny = lerp(1000, 1500, land ** 2)
    nico(dr, 620, ny, 0.6, t, traje="pirata", arms=(140, 140) if land < 1 else (40, 160), elbows=(0, 20), expr="shock" if tt < 1.2 else "happy", squash=sq, look=(-0.5, 0))
    f = tinta(dr)
    add_glow(f, *cam.p(820, 160), 300, (255, 240, 200), 0.25)
    if tt < 0.2: f += 255 * (1 - tt / 0.2)
    img = acabado(f, T)
    if tt > 1.0:
        k = eob((tt - 1.0) / 0.3); d = ImageDraw.Draw(img)
        d.rounded_rectangle([140, 470, 940, 640], radius=30, fill=(236, 214, 160), outline=INK, width=8)
        d.text((540, 515), "MAR CARIBE", font=font(70 * k + 1, F_SERIF), fill=(90, 50, 30), anchor="mm")
        d.text((540, 592), "AÑO 1700", font=font(50 * k + 1), fill=(200, 50, 40), anchor="mm")
    return img, 0

@shot
def s07(t, D, T):    # ¡Un polizón! (capitán, contrapicado)
    cam = Cam(560, 1050, 1.05)
    dr = D_(cam); cielo_noche(dr, t); mastil(dr, t, 950); cubierta(dr, t, 1420)
    info = capitan(dr, 560, 1880, 1.05, t, mouth=boca(6, t), expr="angry", arm_r=70 + 20 * math.sin(t * 6), arm_l=20)
    sx, sy = info["shoulder"]; loro(dr, sx + 10, sy + 10, 0.55, t, flap=0.6, face=1)
    f = tinta(dr); add_glow(f, *cam.p(560, 900), 500, (255, 160, 80), 0.25)
    img = acabado(f, T); burst(img, "¡POLIZÓN!", 540, 330, 140, t - 0.2, col=(255, 80, 60), ang=5)
    return img, 6 * math.exp(-t * 3)

@shot
def s08(t, D, T):    # tarjeta: Capitán Barbagris
    cam = Cam(560, 1150, 1.25)
    dr = D_(cam, bg=(30, 40, 80))
    for k in range(14):
        a = k * math.pi / 7 + t * 0.3
        dr.poly([(560, 1150), (560 + math.cos(a) * 2000, 1150 + math.sin(a) * 2000), (560 + math.cos(a + 0.22) * 2000, 1150 + math.sin(a + 0.22) * 2000)], (40, 54, 104))
    info = capitan(dr, 560, 1900, 1.0, t, mouth=0, expr="smug", arm_r=35, arm_l=20)
    sx, sy = info["shoulder"]; loro(dr, sx + 10, sy + 10, 0.52, t, flap=0.0, face=1)
    f = tinta(dr); img = acabado(f, T)
    tarjeta_nombre(img, t, "CAPITÁN BARBAGRIS", "1 regla · 0 piedad")
    return img, 0

@shot
def s09(t, D, T):    # la regla: tesoro antes del amanecer o la tabla
    half = tl(8, 0.62)
    if t < half:
        cam = Cam(600, 1000, 1.35)
        dr = D_(cam); cielo_noche(dr, t); cubierta(dr, t, 1500)
        capitan(dr, 700, 1900, 1.1, t, mouth=boca(8, t), expr="angry", arm_r=90, arm_l=15, look=(-0.8, 0.3))
        nico(dr, 170, 1900, 0.62, t, traje="pirata", arms=(15, 15), expr="nervous", look=(0.8, -0.4), sweat=True)
        f = tinta(dr); add_glow(f, *cam.p(700, 1000), 400, (255, 150, 70), 0.25)
        return f, 0
    cam = Cam(700, 1180, lerp(1.0, 1.15, ease((t - half) / (D - half))))
    dr = D_(cam); cielo_noche(dr, t); mar(dr, t, 1250)
    dr.poly([(-500, 1050), (420, 1050), (440, 2600), (-500, 2600)], (110, 66, 38))
    dr.rrect(380, 1040, 1250, 1090, 8, (160, 110, 64), shade=True)
    for k in range(3):
        x = 700 + 260 * math.sin(t * 0.9 + k * 2.1); aleta(dr, x, 1420 + k * 70, 0.7)
    capitan(dr, 200, 1060, 0.55, t, mouth=boca(8, t), expr="angry", arm_r=80, arm_l=15)
    f = tinta(dr)
    return f, 0

@shot
def s10(t, D, T):    # ¿Tabla? ¿Cuál tabla?
    cam = Cam(540, 1050, 1.6)
    dr = D_(cam); cielo_noche(dr, t); mastil(dr, t, 920); cubierta(dr, t, 1300)
    hy = 0.9 * math.sin(t * 7)
    nico(dr, 540, 1650, 0.62, t, traje="pirata", arms=(60, 60), elbows=(60, 60), expr="worried", mouth=boca(9, t), look=(hy, -0.2))
    f = tinta(dr); img = acabado(f, T)
    d = ImageDraw.Draw(img)
    for k, (x, y) in enumerate(((260, 520), (820, 480))):
        if t > 0.15 + k * 0.25: d.text((x, y), "?", font=font(160), fill=(255, 222, 40), anchor="mm", stroke_width=12, stroke_fill=INK)
    return img, 0

@shot
def s11(t, D, T):    # la tabla sobre los tiburones
    u = ease(t / D)
    cam = Cam(lerp(300, 900, u), lerp(1100, 1350, u), lerp(1.1, 1.3, u))
    dr = D_(cam); cielo_noche(dr, t); mar(dr, t, 1250)
    dr.poly([(-500, 1050), (420, 1050), (440, 2600), (-500, 2600)], (110, 66, 38))
    for k in range(6): dr.line([(-500, 1100 + k * 90), (430, 1100 + k * 90)], (90, 52, 30), 6)
    dr.rrect(380, 1040, 1250, 1090, 8, (160, 110, 64), shade=True)
    for k in range(4):
        x = 850 + 300 * math.sin(t * 1.1 + k * 1.6); aleta(dr, x, 1420 + k * 60, 0.8)
    if t > D * 0.55:
        j = clamp((t - D * 0.55) / 0.5)
        tiburon(dr, 950, 1500 - 380 * math.sin(j * math.pi), 0.75, t, jaw=0.4 + 0.6 * abs(math.sin(t * 10)), face=-1)
    f = tinta(dr)
    img = acabado(f, T)
    if t > D * 0.6: burst(img, "¡CHOMP!", 540, 520, 140, t - D * 0.6, col=(255, 255, 255), ang=-8)
    return img, (8 if D * 0.6 < t < D * 0.8 else 0)

@shot
def s12(t, D, T):    # inventario: celular, brújula, mapa
    cam = Cam(540, 1000, 1.0)
    dr = D_(cam, bg=(20, 30, 60)); cielo_noche(dr, t); cubierta(dr, t, 1300)
    nico(dr, 540, 1900, 0.75, t, traje="pirata", arms=(40, 40), elbows=(-70, -70), expr="worried", look=(0, -0.6))
    for k, (frac, fn) in enumerate(((0.38, celular), (0.6, brujula), (0.85, mapa))):
        x = 210 + k * 330; y = 700
        dr.rrect(x - 145, y - 170, x + 145, y + 170, 30, (34, 40, 70))
        dr.rrect(x - 135, y - 160, x + 135, y + 160, 24, (60, 70, 110))
        if t > tl(11, frac - 0.08):
            k2 = eob((t - tl(11, frac - 0.08)) / 0.25)
            fn(dr, x, y, (0.95 if fn != mapa else 0.4) * k2 + 0.01, t, *(() if fn != mapa else (0.0,)))
    f = tinta(dr)
    img = acabado(f, T)
    d = ImageDraw.Draw(img); d.text((540, 450), "INVENTARIO", font=font(62), fill=(90, 236, 255), anchor="mm", stroke_width=8, stroke_fill=INK)
    return img, 0

@shot
def s13(t, D, T):    # el mapa: X en la Isla Calavera
    cam = Cam(540, 960, lerp(1.25, 1.5, ease(t / D)))
    dr = D_(cam, bg=(40, 26, 20))
    for k in range(6): dr.rrect(-400, 600 + k * 160, 1500, 600 + k * 160 + 150, 0, (70 + k * 4, 46, 30))
    mapa(dr, 540, 900, 1.25, t, 1.0)
    nico(dr, 540, 2300, 0.9, t, traje="pirata", arms=(30, 30), elbows=(-90, -90), expr="happy", mouth=boca(12, t), look=(0, -0.8))
    f = tinta(dr)
    X, Y = cam.p(540 + 1.25 * 170, 900 + 1.25 * 90)
    add_glow(f, X, Y, 140, (255, 60, 40), 0.5 + 0.3 * math.sin(t * 8))
    return f, 0

@shot
def s14(t, D, T):    # alguien más quiere hablar (el loro gira la cabeza)
    cam = Cam(430, 1120, lerp(1.4, 1.9, ease(t / D)))
    dr = D_(cam); cielo_noche(dr, t); mastil(dr, t, 950)
    info = capitan(dr, 560, 1880, 1.05, t, mouth=0, expr="smug", arm_r=30, arm_l=20)
    sx, sy = info["shoulder"]; loro(dr, sx + 10, sy + 10, 0.55, t, look=(0.9 if t > 0.5 else -0.5, 0), face=1)
    f = tinta(dr)
    return f, 0

@shot
def s15(t, D, T):    # ¡Mapa falso! (loro en primer plano)
    cam = Cam(540, 1000, 1.0)
    dr = D_(cam, bg=(230, 60, 60))
    for k in range(18):
        a = k * math.pi / 9 + t
        dr.poly([(540, 1000), (540 + math.cos(a) * 2000, 1000 + math.sin(a) * 2000), (540 + math.cos(a + 0.17) * 2000, 1000 + math.sin(a + 0.17) * 2000)], (250, 110, 70))
    loro(dr, 470, 1500 + 20 * math.sin(t * 14), 2.1, t, mouth=boca(14, t), flap=1.0, look=(0.6, 0), face=1)
    rng = np.random.default_rng(int(t * 6))
    for k in range(8):
        x, y = rng.uniform(100, 980), rng.uniform(300, 1500)
        dr.ell(x, y + (t * 300 % 200), 18, 40, (60, 180, 70))
    f = tinta(dr)
    img = acabado(f, T)
    burst(img, "¡SQUAWK!", 540, 360, 130, t, col=(255, 255, 255), ang=6)
    return img, 7 * abs(math.sin(t * 25)) * boca(14, t)

@shot
def s16(t, D, T):    # el loro vuela al hombro de Nico y le susurra
    cam = Cam(540, 1050, 1.35)
    dr = D_(cam); cielo_noche(dr, t); mastil(dr, t, 950); cubierta(dr, t, 1400)
    info = nico(dr, 540, 1780, 0.66, t, traje="pirata", arms=(15, 15), expr="worried", look=(0.8, -0.6))
    hx, hy = info["head"]
    u = ease(t / 1.0)
    lx, ly = lerp(1100, hx + 160, u), lerp(500, hy - 60, u) - math.sin(u * math.pi) * 200
    loro(dr, lx, ly, 0.5, t, flap=1.0 if u < 1 else 0.0, mouth=0.4 * abs(math.sin(t * 12)) if u >= 1 else 0, face=-1)
    f = tinta(dr); img = acabado(f, T)
    if u >= 1:
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([600, 420, 1020, 560], radius=40, fill=(255, 255, 255), outline=INK, width=6)
        d.text((810, 490), "psst… el tesoro…", font=font(40), fill=INK, anchor="mm")
    return img, 0

@shot
def s17(t, D, T):    # Ja… ese loro miente más que yo
    cam = Cam(560, 900, 1.5)
    dr = D_(cam); cielo_noche(dr, t); mastil(dr, t, 120)
    capitan(dr, 560, 1880, 1.05, t, mouth=boca(16, t), expr="laugh" if t < 0.8 else "smug", arm_r=150, arm_l=20, look=(0.5, 0))
    f = tinta(dr); add_glow(f, *cam.p(560, 1000), 400, (255, 150, 70), 0.25)
    img = acabado(f, T)
    if t < 1.0: burst(img, "¡JA!", 820, 470, 120, t, ang=-10)
    return img, 0

@shot
def s18(t, D, T):    # quedan 6 horas para el amanecer
    cam = Cam(540, 960, 1.0)
    dr = D_(cam, bg=(14, 18, 44)); cielo_noche(dr, t)
    dr.rrect(-400, 1300, 1500, 2400, 0, (16, 40, 72))
    x, y = 540, 980
    dr.rrect(x - 160, y - 330, x + 160, y - 290, 12, (130, 86, 52)); dr.rrect(x - 160, y + 290, x + 160, y + 330, 12, (130, 86, 52))
    dr.poly([(x - 120, y - 290), (x + 120, y - 290), (x + 12, y), (x + 120, y + 290), (x - 120, y + 290), (x - 12, y)], (190, 230, 250))
    k = clamp(t / D)
    dr.poly([(x - 120 * (1 - k * 0.7), y - 290 + 260 * k), (x + 120 * (1 - k * 0.7), y - 290 + 260 * k), (x, y)], (240, 200, 110))
    dr.poly([(x - 120, y + 290), (x + 120, y + 290), (x + 120 * (0.3 + 0.5 * k), y + 290 - 120 * k - 30), (x - 120 * (0.3 + 0.5 * k), y + 290 - 120 * k - 30)], (240, 200, 110))
    dr.line([(x, y), (x, y + 260)], (240, 200, 110), 6)
    f = tinta(dr); img = acabado(f, T)
    secs = int(6 * 3600 - t * 900)
    d = ImageDraw.Draw(img)
    d.text((540, 470), f"{secs // 3600:02d}:{secs % 3600 // 60:02d}:{secs % 60:02d}", font=font(130), fill=(255, 80, 60), anchor="mm", stroke_width=12, stroke_fill=INK)
    return img, 0

@shot
def s19(t, D, T):    # si se equivoca… los tiburones
    cam = Cam(860, 1020, lerp(1.25, 1.45, ease(t / D)))
    dr = D_(cam); cielo_noche(dr, t); mar(dr, t, 1250, (16, 40, 76))
    dr.rrect(380, 1040, 1250, 1090, 8, (160, 110, 64), shade=True)
    wob = math.sin(t * 9) * 12
    nico(dr, 1000, 1040, 0.5, t, traje="pirata", arms=(100 + wob, 100 - wob), expr="shock", look=(0, 1), sweat=True)
    for k in range(4):
        x = 950 + 280 * math.sin(t * 1.4 + k * 1.6); aleta(dr, x, 1420 + k * 60, 0.8)
    f = tinta(dr)
    f[..., 0] += 40 * (0.5 + 0.5 * math.sin(t * 6))
    return f, 3

@shot
def s20(t, D, T):    # dilema: 1 mapa · 2 loro
    cam = Cam(540, 960, 1.0)
    dr = D_(cam, bg=(30, 60, 140))
    dr.poly([(540, -100), (1600, -100), (1600, 2600), (540, 2600)], (40, 130, 70))
    dr.poly([(470, -100), (610, -100), (610, 2600), (470, 2600)], (20, 16, 26))
    o1 = t > tl(19, 0.3); o2 = t > tl(19, 0.7)
    if o1: mapa(dr, 270, 980, 0.62 * eob((t - tl(19, 0.3)) / 0.3) + 0.01, t, 1.0)
    if o2: loro(dr, 810, 1200, 1.0 * eob((t - tl(19, 0.7)) / 0.3) + 0.01, t, flap=0.3, mouth=0.2, face=-1)
    nico(dr, 540, 1560, 0.5, t, traje="pirata", arms=(70, 70), elbows=(60, 60), expr="worried", look=(-0.8 if t < tl(19, 0.6) else 0.8, -0.3))
    f = tinta(dr)
    img = acabado(f, T)
    d = ImageDraw.Draw(img)
    d.text((540, 300), "¿QUÉ HACE NICO?", font=font(92), fill=(255, 222, 40), anchor="mm", stroke_width=12, stroke_fill=INK)
    for ok, x, n, a, b in ((o1, 270, "1", "SEGUIR", "EL MAPA"), (o2, 810, "2", "CONFIAR", "EN EL LORO")):
        if not ok: continue
        d.ellipse([x - 90, 440, x + 90, 620], fill=(255, 255, 255), outline=INK, width=10)
        d.text((x, 532), n, font=font(130), fill=INK, anchor="mm")
        d.text((x, 700), a, font=font(54), fill=(255, 255, 255), anchor="mm", stroke_width=8, stroke_fill=INK)
        d.text((x, 762), b, font=font(54), fill=(255, 255, 255), anchor="mm", stroke_width=8, stroke_fill=INK)
    return img, 0

@shot
def s21(t, D, T):    # comenta 1 o 2
    cam = Cam(540, 1100, 1.25)
    dr = D_(cam, bg=(230, 40, 50))
    for k in range(18):
        a = k * math.pi / 9 - t * 0.6
        dr.poly([(540, 1100), (540 + math.cos(a) * 2000, 1100 + math.sin(a) * 2000), (540 + math.cos(a + 0.17) * 2000, 1100 + math.sin(a + 0.17) * 2000)], (250, 70, 70))
    nico(dr, 540, 1900, 0.72, t, traje="pirata", arms=(100, 170), elbows=(-20, 0), expr="happy", mouth=boca(20, t))
    f = tinta(dr); img = acabado(f, T)
    d = ImageDraw.Draw(img)
    for k, (x, n) in enumerate(((330, "1"), (750, "2"))):
        p = 1 + 0.08 * math.sin(t * 8 + k * 3)
        r = 95 * p
        d.ellipse([x - r, 420 - r, x + r, 420 + r], fill=(255, 214, 10), outline=INK, width=10)
        d.text((x, 420), n, font=font(130 * p), fill=INK, anchor="mm")
    d.text((540, 620), "COMENTA", font=font(84), fill=(255, 255, 255), anchor="mm", stroke_width=10, stroke_fill=INK)
    return img, 0

@shot
def s22(t, D, T):    # nos vemos en otro mundo hipotético + avance
    cam = Cam(540, 1000, 1.0)
    dr = D_(cam, bg=(18, 10, 30)); cielo_noche(dr, t)
    o = 1 - ease((t - D + 1.0) / 0.8)
    portal(dr, 540, 1050, 330, t, o)
    if t < D - 1.2: nico(dr, 540, 1500, 0.5, t, traje="pirata", arms=(150, 20), elbows=(30, 0), expr="happy")
    f = tinta(dr); add_glow(f, *cam.p(540, 1050), 450, (150, 120, 255), 0.5 * o)
    img = acabado(f, T)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([150, 380, 930, 560], radius=36, fill=(255, 214, 10), outline=INK, width=8)
    d.text((540, 440), "CAPÍTULO 2", font=font(70), fill=INK, anchor="mm")
    d.text((540, 510), "MAÑANA · 6 P. M.", font=font(46), fill=(200, 40, 50), anchor="mm")
    return img, 0

def D_(cam, bg=(0, 0, 0)): return D(cam, bg)

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
    badge(img, T)
    caption(img, T)
    return img

# ------------------------------------------------------------ sonido
def make_audio(path):
    from scipy.signal import butter, sosfilt
    sr = SR; n = int(TOTAL * sr) + sr; out = np.zeros(n)
    rng = np.random.default_rng(7)
    def add(s, sig, g=1.0):
        i0 = int(s * sr); i1 = min(n, i0 + len(sig))
        if 0 <= i0 < n: out[i0:i1] += g * sig[:i1 - i0]
    def seg(d): return np.arange(int(d * sr)) / sr
    hz = lambda m: 440 * 2 ** ((m - 69) / 12)
    noise = rng.standard_normal(n)
    bp = lambda lo, hi: sosfilt(butter(2, [lo, hi], btype="band", fs=sr, output="sos"), noise)
    wh = bp(400, 3500); low = sosfilt(butter(2, 180, btype="low", fs=sr, output="sos"), noise)
    t_pir = STARTS[5]
    # A) música de concurso (mayor, 120 bpm) hasta la ruleta
    b = 0.5
    prog = [[60, 64, 67], [65, 69, 72], [67, 71, 74], [60, 64, 67]]
    for k in range(int(t_pir / (b / 2))):
        s = k * b / 2; ch = prog[int(s / 2) % 4]; x = seg(0.22)
        if k % 2 == 0: add(s, 0.05 * np.exp(-x * 10) * np.sign(np.sin(2 * np.pi * hz(ch[k // 2 % 3] + 12) * x)))
        if k % 4 == 0: add(s, 0.2 * np.exp(-x * 18) * np.sin(2 * np.pi * (60 + 80 * np.exp(-x * 30)) * x))
        if k % 4 == 2: add(s, 0.06 * rng.standard_normal(len(x)) * np.exp(-x * 30))
        if k % 2 == 1: add(s, 0.06 * np.exp(-x * 7) * np.sin(2 * np.pi * hz(ch[0] - 12) * x))
    # redoble mientras gira + clics de la ruleta
    t0, t1 = STARTS[1] + 2.4, STARTS[3] + 0.15
    xr = seg(t1 - t0); add(t0, 0.06 * bp(150, 600)[:len(xr)] * (0.6 + 0.4 * np.sin(2 * np.pi * 18 * xr)) * (xr / xr[-1]))
    prev = 0
    for k in range(int((t1 - t0) * FPS)):
        T = t0 + k / FPS; a = ang_ruleta(T)
        if int(a / 22.5) != prev:
            prev = int(a / 22.5); xc = seg(0.03); add(T, 0.25 * np.exp(-xc * 200) * np.sin(2 * np.pi * 2500 * xc))
    x = seg(1.2); add(STARTS[3] + 0.1, 0.35 * np.exp(-x * 3) * (np.sin(2 * np.pi * 523 * x) + np.sin(2 * np.pi * 659 * x) + np.sin(2 * np.pi * 784 * x)) / 3)   # ¡ding!
    x = seg(0.5); add(STARTS[3] + 0.1, 0.5 * np.exp(-x * 8) * np.sin(2 * np.pi * (55 + 50 * np.exp(-x * 20)) * x))
    # B) música pirata (re menor, 6/8 ≈ 100 bpm en corcheas)
    e8 = 0.2
    mel = [62, 65, 69, 74, 72, 69, 70, 69, 65, 67, 65, 62, 64, 65, 67, 69, 70, 72, 74, 72, 69, 65, 64, 62]
    bass = [38, 38, 41, 43, 45, 41, 38, 45]
    tend = STARTS[19]
    k = 0; s = t_pir
    while s < tend:
        x = seg(e8 * 1.5)
        m = mel[k % len(mel)]
        if k % 3 != 2 or k % 6 == 5:
            sq = np.sign(np.sin(2 * np.pi * hz(m) * x)) * 0.5 + np.sin(2 * np.pi * hz(m) * 2 * x) * 0.3
            add(s, 0.035 * sq * np.exp(-x * 4) * (1 - np.exp(-x * 60)))
        if k % 3 == 0:
            bm = bass[(k // 6) % len(bass)]; xb = seg(e8 * 3)
            add(s, 0.09 * np.exp(-xb * 3) * np.sin(2 * np.pi * hz(bm) * xb))
            add(s, 0.16 * np.exp(-x * 20) * np.sin(2 * np.pi * (70 + 60 * np.exp(-x * 25)) * x))
        if k % 6 == 3: add(s, 0.06 * rng.standard_normal(len(x)) * np.exp(-x * 25))
        k += 1; s += e8
    # olas de fondo en el barco
    xw = seg(tend - t_pir); add(t_pir, 0.05 * bp(200, 1200)[:len(xw)] * (0.5 + 0.5 * np.sin(2 * np.pi * 0.18 * xw)))
    # efectos
    S_ = STARTS
    x = seg(1.4); add(S_[5] + 0.2, 0.12 * np.sin(2 * np.pi * (200 + 600 * x) * x) * np.sin(np.pi * x / 1.4))     # portal
    tp = S_[5] + DURS[5] * 0.42; x = seg(0.5); add(tp, 0.5 * np.exp(-x * 9) * np.sin(2 * np.pi * (60 + 40 * np.exp(-x * 20)) * x))
    x = seg(0.4); add(S_[6] + 0.1, 0.4 * np.exp(-x * 8) * np.sin(2 * np.pi * 50 * x))
    x = seg(0.5); add(S_[7] + 0.05, 0.25 * wh[:len(x)] * np.exp(-x * 6))
    x = seg(0.6); add(S_[10] + DURS[10] * 0.6, 0.4 * bp(100, 900)[:len(x)] * np.exp(-x * 5))                          # chomp/splash
    for kk, fr in enumerate((0.38, 0.6, 0.85)):
        x = seg(0.25); add(S_[11] + tl(11, fr - 0.08), 0.18 * np.exp(-x * 12) * np.sin(2 * np.pi * (700 + 300 * kk) * x))   # pop items
    for kk in range(int(DURS[17] / 0.5) + 1):
        x = seg(0.05); add(S_[17] + kk * 0.5, 0.25 * np.exp(-x * 150) * np.sin(2 * np.pi * 1800 * x))              # tic tac
    x = seg(DURS[18]); add(S_[18], 0.3 * low[:len(x)] * (x / x[-1]))
    x = seg(1.2); add(S_[18] + 0.1, 0.18 * np.exp(-x * 2) * (np.sign(np.sin(2 * np.pi * 98 * x)) + np.sign(np.sin(2 * np.pi * 104 * x))) / 2)
    # C) dilema: pulso tenso
    for kk in range(int((S_[21] - S_[19]) / 0.6)):
        x = seg(0.3); add(S_[19] + kk * 0.6, 0.12 * np.exp(-x * 10) * np.sin(2 * np.pi * (55 + 20 * (kk % 2)) * x))
        x = seg(0.08); add(S_[19] + kk * 0.6 + 0.3, 0.05 * np.exp(-x * 60) * np.sin(2 * np.pi * 1200 * x))
    x = seg(1.6); add(S_[21] + 0.2, 0.12 * np.exp(-x * 1.5) * (np.sin(2 * np.pi * 523 * x) + np.sin(2 * np.pi * 784 * x)) / 2)
    out = np.tanh(out * 1.3); out = out / (np.max(np.abs(out)) + 1e-9) * 0.3
    voice = np.zeros(n)
    for k, v in enumerate(VOZ):
        i0 = int((STARTS[k] + LEAD) * sr); i1 = min(n, i0 + len(v)); voice[i0:i1] += v[:i1 - i0] / (np.max(np.abs(v)) + 1e-9)
    voice *= 0.9
    env = np.convolve(np.abs(voice), np.ones(4410) / 4410, mode="same")
    mix = out * (1 - 0.5 * np.clip(env / 0.05, 0, 1)) + voice
    mix = mix[:int(TOTAL * sr)]; tt = np.arange(len(mix)) / sr
    mix *= np.clip((TOTAL - tt) / 0.5, 0, 1); mix = mix / np.max(np.abs(mix)) * 0.95
    wavfile.write(path, sr, (mix * 32767).astype(np.int16))

if __name__ == "__main__":
    if os.environ.get("PREVIEW"):
        ts = [float(x) for x in os.environ["PREVIEW"].split(",")]
        ims = [frame(T).resize((270, 480)) for T in ts]
        sheet = Image.new("RGB", (270 * 6, 480 * ((len(ims) + 5) // 6)))
        for k, im in enumerate(ims): sheet.paste(im, ((k % 6) * 270, (k // 6) * 480))
        sheet.save("sheet.png"); print("TOTAL", round(TOTAL, 2), [round(s, 2) for s in STARTS]); sys.exit()
    if os.environ.get("BIG"):
        frame(float(os.environ["BIG"])).save("big.png"); sys.exit()
    make_audio("audio.wav")
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-i", "audio.wav", "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-pix_fmt", "yuv420p",
                          "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
    N = int(TOTAL * FPS)
    for k in range(N):
        p.stdin.write(frame(k / FPS).convert("RGB").tobytes())
        if k % 300 == 0: print(f"{k}/{N}", flush=True)
    p.stdin.close(); p.wait(); print("listo", OUT, TOTAL)
