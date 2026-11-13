#!/usr/bin/env python3
"""LA RULETA DE NICO · Capítulo 2/3 — ganó el 2 (confiar en el loro). La ruleta saca "???" = ¡KRAKEN!
Estilo vector + cómic (vc.py). Dilema final: 1 tirar el celular al mar / 2 apagarlo y remar a oscuras."""
import math, os, sys, subprocess
import numpy as np
from PIL import Image, ImageDraw
from scipy.io import wavfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vc import *

FPS = 30
OUT = sys.argv[1] if len(sys.argv) > 1 else "video.mp4"
VOZ_DIR = os.environ.get("VOZ_DIR", "voz")
VOZ_F = sorted(f for f in os.listdir(VOZ_DIR) if f.endswith(".wav"))
VOZ = [wavfile.read(f"{VOZ_DIR}/{f}")[1].astype(np.float32) / 32768 for f in VOZ_F]
SR = 44100; LEAD = 0.1
DURS = [len(v) / SR + LEAD + 0.26 for v in VOZ]
DURS[7] += 0.9; DURS[9] += 0.6; DURS[18] += 0.6; DURS[20] += 1.6
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
    [("Antes, en", []), ("La Ruleta de Nico:", ["Ruleta"]), ("el capitán Barbagris", ["Barbagris"]), ("le dio hasta el amanecer", ["amanecer"]), ("para encontrar su tesoro…", ["tesoro…"]), ("o caminar por la tabla", ["tabla"])],
    [("Ustedes votaron…", ["votaron…"]), ("y ganó la dos,", ["dos,"]), ("como dijo AndresSalvador:", ["AndresSalvador:"]), ("¡confiar en el loro!", ["loro!"])],
    [("¿En serio?", []), ("¿Le confiaron mi vida…", ["vida…"]), ("a un pájaro?", ["pájaro?"])],
    [("¡Buena elección!", ["elección!"]), ("¡Buena elección!", ["elección!"]), ("¡Síganme, síganme!", ["Síganme,", "síganme!"])],
    [("Nico roba un bote", ["bote"]), ("y sigue al loro", ["loro"]), ("en la oscuridad…", ["oscuridad…"]), ("justo en dirección contraria", ["contraria"]), ("a la Isla Calavera", ["Calavera"])],
    [("¡Mi loro!", ["loro!"]), ("¡Mi bote!", ["bote!"]), ("¡Vuelve aquí, polizón!", ["polizón!"])],
    [("Pero antes de llegar…", []), ("la ruleta vuelve a girar", ["ruleta", "girar"])],
    [("Tiburones…", ["Tiburones…"]), ("hielo…", ["hielo…"]), ("volcán…", ["volcán…"]), ("y se detiene en…", [])],
    [("¿Signos de pregunta?", ["pregunta?"]), ("Eso nunca es bueno…", ["nunca"])],
    [("¡Un kraken!", ["kraken!"]), ("Un pulpo gigante…", ["gigante…"]), ("del tamaño de un barco", ["barco"])],
    [("¡Detalle! ¡Detalle!", ["¡Detalle!"]), ("¡Se me olvidó el kraken!", ["kraken!"])],
    [("¡¿Cómo se te olvida", []), ("un pulpo gigante?!", ["gigante?!"])],
    [("Y el kraken tiene", ["kraken"]), ("una sola regla:", ["regla:"]), ("ataca todo lo que brilla", ["brilla"])],
    [("Y en el bote…", ["bote…"]), ("solo hay una cosa", []), ("que brilla", ["brilla"])],
    [("No, no, no…", []), ("¿y justo AHORA", ["AHORA"]), ("me llega señal?", ["señal?"])],
    [("Un tentáculo", ["tentáculo"]), ("sale del agua…", []), ("y va directo", []), ("hacia el celular", ["celular"])],
    [("¡La cueva!", ["cueva!"]), ("¡El tesoro está", ["tesoro"]), ("en la cueva!", ["cueva!"]), ("¡Rema, rema!", ["¡Rema,", "rema!"])],
    [("La cueva está", []), ("a cien metros…", ["cien"]), ("y quedan cuatro horas", ["cuatro"]), ("para el amanecer", ["amanecer"])],
    [("¿Qué hace Nico?", ["Nico?"]), ("1: tirar el celular", ["1:"]), ("al mar para distraer", []), ("al kraken", ["kraken"]), ("2: apagarlo y remar", ["2:"]), ("a oscuras hasta la cueva", ["cueva"])],
    [("Comenta 1 o 2…", ["1", "2…"]), ("¡y en la próxima parte", []), ("verás si elegiste bien!", ["bien!"])],
    [("Nos vemos en otro", []), ("mundo hipotético", ["hipotético"])],
]
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
    f2 = font(36); txt = "CAPÍTULO 2/3"
    x1 = W - 36; x0 = x1 - f2.getlength(txt) - 44
    d.rounded_rectangle([x0, 110, x1, 170], radius=16, fill=(255, 214, 10), outline=INK, width=5)
    d.text((x0 + 22, 140), txt, font=f2, fill=INK, anchor="lm")


# ------------------------------------------------------------ utilería nueva (cap. 2)
def D_(cam, bg=(0, 0, 0)): return D(cam, bg)

KR = (150, 52, 96); KR_L = (196, 86, 130); KR_S = (240, 176, 196)
def tentaculo(dr, x0, y0, ang0, L, r0, t, ph=0.0, curl=1.0, col=KR):
    """Tentáculo = cadena de círculos que se ondula. ang0 en grados (-90 = arriba). Devuelve la punta."""
    n = 20; x, y = x0, y0; a = math.radians(ang0); step = L / n; pts = []
    for i in range(n):
        u = i / (n - 1); pts.append((x, y, r0 * (1 - 0.82 * u)))
        a += curl * (0.05 + 0.11 * (1 + u * 2) * math.sin(t * 2.2 + ph + u * 3.5))
        x += math.cos(a) * step; y += math.sin(a) * step
    for (px, py, r) in pts: dr.ell(px, py, r, r, col)
    for i, (px, py, r) in enumerate(pts[2:-3]):
        if i % 2 == 0: dr.ell(px - r * 0.45, py + r * 0.2, r * 0.32, r * 0.32, KR_S)
    return pts[-1][:2]

def kraken(dr, x, yw, s, t, rise=1.0, angry=True):
    S = lambda v: v * s
    by = yw + S(250) - S(520) * rise
    for k, (dx, a, L) in enumerate(((-260, -140, 900), (260, -40, 900), (-180, -115, 700), (180, -65, 700))):
        tentaculo(dr, x + S(dx), yw + S(60), a, S(L) * (0.3 + 0.7 * rise), S(70), t, ph=k * 1.7, curl=0.8 if k % 2 else -0.8)
    dr.ell(x, by, S(300), S(380), KR, shade=True)
    for (dx, dy, r) in ((-150, -210, 40), (120, -260, 30), (60, -110, 22), (-60, -300, 26), (180, -150, 20)):
        dr.ell(x + S(dx), by + S(dy), S(r), S(r), KR_L)
    for sx in (-1, 1):
        ex, ey = x + sx * S(120), by + S(110)
        dr.ell(ex, ey, S(80), S(70), (250, 240, 200))
        dr.ell(ex, ey, S(46), S(46), (255, 200, 30))
        dr.rrect(ex - S(10), ey - S(40), ex + S(10), ey + S(40), S(8), INK)
        if angry: dr.poly([(ex - sx * S(100), ey - S(110)), (ex + sx * S(90), ey - S(50)), (ex + sx * S(90), ey - S(80)), (ex - sx * S(100), ey - S(140))], (90, 24, 56))
    return (x, by)

def bote(dr, x, y, s, t):
    S = lambda v: v * s
    dr.poly([(x - S(310), y - S(90)), (x + S(310), y - S(90)), (x + S(230), y + S(60)), (x - S(230), y + S(60))], (126, 74, 42), shade=True)
    for k in range(2): dr.line([(x - S(290 - k * 30), y - S(40) + k * S(45)), (x + S(290 - k * 30), y - S(40) + k * S(45))], (96, 54, 30), S(6))
    dr.rrect(x - S(320), y - S(105), x + S(320), y - S(78), S(10), (90, 52, 28))
    dr.rrect(x - S(60), y - S(10), x + S(60), y + S(14), S(6), TURQ)    # franja turquesa de la marca
    dr.text(x, y + S(2), "NICO", S(22), (255, 255, 255), stroke=3)

def escena_bote(dr, t, x, y, s, sea_y=None, row=0.0, **kw):
    """Nico sentado en el bote: el bote tapa sus piernas y el agua tapa el casco."""
    ns = 0.69 * s
    info = nico(dr, x, y + 70 * s, ns, t, traje="pirata", **kw)
    if row:
        a = math.sin(t * 5) * 0.5
        for sx in (-1, 1):
            dr.line([(x + sx * 150 * s, y - 120 * s), (x + sx * (330 + 60 * a) * s, y + 120 * s)], (150, 100, 56), 16 * s)
    bote(dr, x, y, s, t)
    mar(dr, t, y + 40 * s if sea_y is None else sea_y)
    return info

def isla_cueva(dr, x, y, s, t):
    S = lambda v: v * s
    dr.poly([(x - S(420), y + S(120)), (x - S(330), y - S(180)), (x - S(150), y - S(330)), (x + S(60), y - S(360)), (x + S(260), y - S(260)), (x + S(400), y - S(40)), (x + S(440), y + S(120))], (88, 82, 100), shade=True)
    dr.poly([(x - S(150), y - S(330)), (x + S(60), y - S(360)), (x - S(20), y - S(200))], (120, 114, 130))
    dr.ell(x, y + S(30), S(150), S(130), (24, 16, 30))          # boca de la cueva
    for sx in (-1, 1): dr.ell(x + sx * S(110), y - S(170), S(55), S(60), (24, 16, 30))   # cuencas de calavera
    dr.poly([(x - S(20), y - S(90)), (x + S(20), y - S(90)), (x, y - S(50))], (24, 16, 30))
    for k in range(5): dr.ell(x - S(60) + k * S(30), y + S(110) - (k % 2) * S(12), S(16), S(12), (250, 200, 60))   # oro
    dr.line([(x + S(340), y - S(150)), (x + S(340), y - S(420))], (100, 70, 40), S(12))
    dr.poly([(x + S(340), y - S(420)), (x + S(470), y - S(380)), (x + S(340), y - S(340))], INK)

def celular_on(dr, x, y, s, t):
    S = lambda v: v * s
    dr.rrect(x - S(80), y - S(150), x + S(80), y + S(150), S(24), (30, 30, 38))
    dr.rrect(x - S(68), y - S(130), x + S(68), y + S(130), S(12), (220, 250, 255), nolin=True)
    for k in range(4): dr.rrect(x - S(44) + k * S(24), y - S(70) - k * S(16), x - S(30) + k * S(24), y - S(30), S(2), (40, 200, 90))
    dr.rrect(x - S(62), y + S(0), x + S(62), y + S(80), S(10), (255, 255, 255))
    dr.text(x, y + S(24), "Mamá:", S(22), (40, 120, 220))
    dr.text(x, y + S(56), "¿dónde estás?", S(17), INK)

def barco_lejos(dr, x, y, s, t):
    S = lambda v: v * s
    dr.poly([(x - S(160), y - S(40)), (x + S(160), y - S(40)), (x + S(120), y + S(20)), (x - S(120), y + S(20))], (40, 30, 40))
    dr.line([(x, y - S(40)), (x, y - S(260))], (40, 30, 40), S(8))
    dr.poly([(x + S(6), y - S(250)), (x + S(120), y - S(200)), (x + S(6), y - S(80))], (200, 196, 180))
    dr.ell(x, y - S(80), S(14), S(14), (255, 210, 90), nolin=True)

def sepia(f):
    g = f.mean(axis=2, keepdims=True)
    return np.clip(g * np.array([1.08, 0.92, 0.72], np.float32) * 0.9 + 18, 0, 255)

# ------------------------------------------------------------ planos
SHOTS = []
def shot(fn): SHOTS.append(fn); return fn
def tl(k, frac): return LEAD + len(VOZ[k]) / SR * frac

@shot
def s01(t, D, T):    # "Antes en La Ruleta de Nico…" (recuerdo en sepia)
    p = t / D
    if p < 0.36:
        cam = Cam(600, 1000, 1.35)
        dr = D_(cam); cielo_noche(dr, t); cubierta(dr, t, 1500)
        capitan(dr, 700, 1900, 1.1, t, mouth=0.5 * abs(math.sin(t * 9)), expr="angry", arm_r=90, arm_l=15, look=(-0.8, 0.3))
        nico(dr, 170, 1900, 0.62, t, traje="pirata", arms=(15, 15), expr="nervous", look=(0.8, -0.4), sweat=True)
    elif p < 0.7:
        cam = Cam(760, 1180, 1.1)
        dr = D_(cam); cielo_noche(dr, t); mar(dr, t, 1250)
        dr.poly([(-500, 1050), (420, 1050), (440, 2600), (-500, 2600)], (110, 66, 38))
        dr.rrect(380, 1040, 1250, 1090, 8, (160, 110, 64), shade=True)
        for k in range(4): aleta(dr, 800 + 280 * math.sin(t * 1.2 + k * 1.6), 1420 + k * 60, 0.8)
    else:
        cam = Cam(540, 960, 1.0)
        dr = D_(cam, bg=(30, 60, 140))
        dr.poly([(540, -100), (1600, -100), (1600, 2600), (540, 2600)], (40, 130, 70))
        mapa(dr, 270, 980, 0.62, t, 1.0)
        loro(dr, 810, 1200, 1.0, t, flap=0.3, face=-1)
        nico(dr, 540, 1560, 0.5, t, traje="pirata", arms=(70, 70), elbows=(60, 60), expr="worried")
    f = sepia(tinta(dr)); img = acabado(f, T)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([110, 260, 970, 380], radius=24, fill=(30, 22, 18), outline=(236, 214, 160), width=6)
    d.text((540, 320), "ANTES EN LA RULETA DE NICO…", font=font(50), fill=(236, 214, 160), anchor="mm")
    return img, 0

@shot
def s02(t, D, T):    # los votos: ganó el 2
    cam = Cam(540, 1000, 1.0)
    dr = D_(cam); escenario_ruleta(dr, t, 0.0)
    jump = abs(math.sin(t * 7)) * 40 if t > tl(1, 0.7) else 0
    loro(dr, 540, 1560 - jump, 1.35, t, flap=1.0 if t > tl(1, 0.7) else 0.2, mouth=0.3, face=1)
    f = tinta(dr)
    for x in (270, 810): add_cono(f, x, -50, 1700, 60, 520, (255, 236, 180), 0.25)
    img = acabado(f, T); d = ImageDraw.Draw(img)
    d.text((540, 300), "USTEDES VOTARON", font=font(78), fill=(255, 222, 40), anchor="mm", stroke_width=10, stroke_fill=INK)
    k = ease(t / max(0.1, tl(1, 0.55)))
    for row, (n, lab, pct, col) in enumerate((("1", "MAPA", 0.2, (120, 130, 150)), ("2", "LORO", 0.8, (60, 190, 90)))):
        y = 430 + row * 150
        d.rounded_rectangle([90, y, 990, y + 110], radius=24, fill=(30, 20, 40), outline=INK, width=6)
        w = 760 * pct * k
        if w > 30: d.rounded_rectangle([210, y + 14, 210 + w, y + 96], radius=18, fill=col)
        d.ellipse([104, y + 8, 196, y + 100], fill=(255, 255, 255), outline=INK, width=6)
        d.text((150, y + 55), n, font=font(64), fill=INK, anchor="mm")
        d.text((236, y + 55), lab, font=font(52), fill=(255, 255, 255), anchor="lm", stroke_width=6, stroke_fill=INK)
        d.text((960, y + 55), f"{int(round(pct * 100 * k))}%", font=font(52), fill=(255, 255, 255), anchor="rm", stroke_width=6, stroke_fill=INK)
    if t > tl(1, 0.45):
        kk = eob((t - tl(1, 0.45)) / 0.3)
        d.rounded_rectangle([170, 760, 910, 850], radius=40, fill=(255, 255, 255), outline=INK, width=6)
        d.text((540, 805), "@AndresSalvador: 2", font=font(int(44 * kk) + 1), fill=INK, anchor="mm")
    if t > tl(1, 0.72): burst(img, "¡GANÓ EL 2!", 540, 1010, 120, t - tl(1, 0.72), ang=-6)
    return img, 0

@shot
def s03(t, D, T):    # Nico: ¿le confiaron mi vida a un pájaro?
    cam = Cam(540, 1080, 1.6)
    dr = D_(cam); cielo_noche(dr, t); mastil(dr, t, 950); cubierta(dr, t, 1300)
    info = nico(dr, 540, 1650, 0.62, t, traje="pirata", arms=(60, 60), elbows=(60, 60), expr="worried", mouth=boca(2, t), look=(0.7, -0.2))
    hx, hy = info["head"]
    loro(dr, hx + 210, hy + 200, 0.42, t, face=-1, mouth=0.2, look=(-0.5, 0))
    f = tinta(dr); img = acabado(f, T)
    if t > tl(2, 0.6):
        d = ImageDraw.Draw(img); d.text((900, 520), "?!", font=font(150), fill=(255, 222, 40), anchor="mm", stroke_width=12, stroke_fill=INK)
    return img, 0

@shot
def s04(t, D, T):    # loro: ¡buena elección! ¡síganme!
    cam = Cam(540, 1000, 1.0)
    dr = D_(cam, bg=(60, 170, 90))
    for k in range(18):
        a = k * math.pi / 9 + t
        dr.poly([(540, 1000), (540 + math.cos(a) * 2000, 1000 + math.sin(a) * 2000), (540 + math.cos(a + 0.17) * 2000, 1000 + math.sin(a + 0.17) * 2000)], (110, 210, 120))
    loro(dr, 470, 1500 + 20 * math.sin(t * 14), 2.1, t, mouth=boca(3, t), flap=1.0, look=(0.6, 0), face=1)
    f = tinta(dr); img = acabado(f, T)
    burst(img, "¡SÍGANME!", 540, 360, 130, t - 0.3, col=(255, 255, 255), ang=-6)
    return img, 5 * boca(3, t)

@shot
def s05(t, D, T):    # Nico roba un bote y sigue al loro… al revés de la Isla Calavera
    u = ease(t / D)
    cam = Cam(540, 1000, lerp(1.0, 1.08, u))
    dr = D_(cam); cielo_noche(dr, t)
    barco_lejos(dr, 200, 780, 1.0, t)
    escena_bote(dr, t, lerp(380, 600, u), 1280 + 10 * math.sin(t * 2), 0.95, row=1.0, arms=(50, 50), elbows=(-30, -30), expr="worried", look=(0.8, -0.3))
    loro(dr, lerp(760, 900, u), 860 + 30 * math.sin(t * 4), 0.6, t, flap=1.0, face=1)
    f = tinta(dr); add_glow(f, *cam.p(820, 160), 300, (255, 240, 200), 0.25)
    img = acabado(f, T)
    if t > tl(4, 0.6):
        k = eob((t - tl(4, 0.6)) / 0.3); d = ImageDraw.Draw(img)
        d.polygon([(90, 1460), (190, 1390), (190, 1420), (520, 1420), (520, 1500), (190, 1500), (190, 1530)], fill=(200, 160, 100), outline=INK)
        d.text((355, 1460), "ISLA CALAVERA", font=font(int(34 * k) + 1, F_SERIF), fill=(90, 50, 30), anchor="mm")
        d.text((720, 1460), "→ NICO", font=font(int(40 * k) + 1), fill=(255, 222, 40), anchor="mm", stroke_width=6, stroke_fill=INK)
    return img, 0

@shot
def s06(t, D, T):    # capitán: ¡mi loro! ¡mi bote!
    cam = Cam(560, 1050, 1.05)
    dr = D_(cam); cielo_noche(dr, t); mastil(dr, t, 950); cubierta(dr, t, 1420)
    info = capitan(dr, 560, 1880, 1.05, t, mouth=boca(5, t), expr="angry", arm_r=120 + 30 * math.sin(t * 8), arm_l=60 + 20 * math.sin(t * 7))
    sx, sy = info["shoulder"]
    f = tinta(dr); add_glow(f, *cam.p(560, 900), 500, (255, 160, 80), 0.25)
    img = acabado(f, T)
    burst(img, "¡VUELVE!", 540, 330, 140, t - 0.2, col=(255, 80, 60), ang=5)
    if t > tl(5, 0.2):
        X, Y = cam.p(sx - 30, sy - 110); ImageDraw.Draw(img).text((X, Y), "?", font=font(110), fill=(255, 255, 255), anchor="mm", stroke_width=10, stroke_fill=INK)
    return img, 6 * boca(5, t)

def ang_ruleta(T):
    t0, t1 = STARTS[6] + tl(6, 0.55), STARTS[7] + LEAD + len(VOZ[7]) / SR
    a0, final = -45.0, -90 - 360 * 4
    if T < t0: return a0
    u = clamp((T - t0) / (t1 - t0))
    return a0 + (final - a0) * (1 - (1 - u) ** 3)

@shot
def s07(t, D, T):    # la ruleta vuelve a girar
    cam = Cam(540, lerp(1000, 980, ease(t / D)), lerp(1.0, 1.25, ease(t / D)))
    dr = D_(cam); escenario_ruleta(dr, t); ruleta(dr, 540, 1080, 300, ang_ruleta(T), t)
    f = tinta(dr)
    for x in (300, 780): add_cono(f, x, -50, 1700, 60, 520, (255, 236, 180), 0.3)
    add_glow(f, *cam.p(540, 300), 380, (255, 120, 200), 0.3)
    return f, 0

@shot
def s08(t, D, T):    # tiburones… hielo… volcán… ¿y se detiene en…? → ???
    t1 = LEAD + len(VOZ[7]) / SR
    stop = t >= t1
    cam = Cam(540, 1000, (1.55 + 0.25 * ease(t / t1)) if not stop else 1.8 - 0.12 * eob((t - t1) / 0.3))
    dr = D_(cam); escenario_ruleta(dr, t); ruleta(dr, 540, 1080, 300, ang_ruleta(T), t, glow_seg=2 if stop else None)
    f = tinta(dr)
    add_glow(f, *cam.p(540, 790), 300, (255, 240, 180), 0.35)
    if stop: add_glow(f, *cam.p(540, 860), 420, (200, 120, 255), 0.6 * math.exp(-(t - t1) * 1.5))
    img = acabado(f, T)
    if stop: burst(img, "¿¿???", 540, 430, 180, t - t1, col=(200, 140, 255), ang=-7)
    return img, (14 * math.exp(-(t - t1) * 5) if stop else 2 * math.sin(T * 40))

@shot
def s09(t, D, T):    # Nico en el bote: ¿signos de pregunta?
    cam = Cam(540, 1080, 1.7)
    dr = D_(cam); cielo_noche(dr, t)
    escena_bote(dr, t, 540, 1480, 0.9, arms=(25, 25), elbows=(-40, -40), expr="nervous", mouth=boca(8, t), sweat=True, look=(0.3 * math.sin(t * 4), -0.3))
    f = tinta(dr); img = acabado(f, T)
    d = ImageDraw.Draw(img)
    for k, (x, y) in enumerate(((220, 560), (860, 520), (540, 430))):
        if t > 0.2 + k * 0.25: d.text((x, y + 10 * math.sin(t * 5 + k)), "?", font=font(150), fill=(200, 140, 255), anchor="mm", stroke_width=12, stroke_fill=INK)
    return img, 0

@shot
def s10(t, D, T):    # ¡UN KRAKEN!
    rise = ease(t / 0.9)
    cam = Cam(540, 1000, 1.0 + 0.05 * ease(t / D))
    flash = t > 0.5 and int(t * 6) % 5 == 0
    dr = D_(cam); cielo_noche(dr, t)
    kraken(dr, 560, 1180, 1.15, t, rise)
    mar(dr, t, 1180)
    escena_bote(dr, t, 520, 1560, 0.55, sea_y=1590, arms=(140, 140), elbows=(0, 0), expr="shock", look=(0, -1))
    f = tinta(dr)
    if flash: f = np.clip(f * 1.4 + 40, 0, 255)
    img = acabado(f, T)
    if t > 0.7: burst(img, "¡KRAKEN!", 540, 330, 170, t - 0.7, col=(255, 70, 90), ang=-6)
    return img, (16 * math.exp(-max(0, t - 0.7) * 2) if t > 0.3 else 4)

@shot
def s11(t, D, T):    # loro avergonzado: ¡detalle! ¡se me olvidó el kraken!
    cam = Cam(540, 1000, 1.0)
    dr = D_(cam, bg=(50, 70, 170))
    for k in range(18):
        a = k * math.pi / 9 - t * 0.5
        dr.poly([(540, 1000), (540 + math.cos(a) * 2000, 1000 + math.sin(a) * 2000), (540 + math.cos(a + 0.17) * 2000, 1000 + math.sin(a + 0.17) * 2000)], (70, 96, 200))
    loro(dr, 470, 1500, 2.0, t, mouth=boca(10, t), flap=0.15, look=(-0.8, 0.5), face=1)
    f = tinta(dr); img = acabado(f, T); d = ImageDraw.Draw(img)
    for k in range(3):
        y = 600 + ((t * 300 + k * 140) % 400)
        d.ellipse([700 + k * 60, y, 740 + k * 60, y + 60], fill=(140, 210, 255), outline=INK, width=5)
    burst(img, "¿DETALLE?", 540, 360, 120, t - 0.1, col=(255, 222, 40), ang=7)
    return img, 0

@shot
def s12(t, D, T):    # Nico: ¡¿cómo se te olvida un pulpo gigante?!
    cam = Cam(540, 1080, 1.75)
    dr = D_(cam); cielo_noche(dr, t)
    tentaculo(dr, 800, 1600, -95, 700, 60, t, ph=1.0, curl=0.6)
    escena_bote(dr, t, 520, 1480, 0.9, arms=(110, 110), elbows=(-70, -70), expr="angry", mouth=boca(11, t), look=(-0.6, -0.2))
    f = tinta(dr); f[..., 0] = np.clip(f[..., 0] + 25, 0, 255)
    img = acabado(f, T)
    burst(img, "¡¿CÓMO?!", 540, 420, 140, t - 0.15, col=(255, 90, 60), ang=-8)
    return img, 6 * boca(11, t)

@shot
def s13(t, D, T):    # regla: ataca todo lo que brilla
    cam = Cam(540, 1100, lerp(1.0, 1.12, ease(t / D)))
    dr = D_(cam, bg=(40, 14, 40))
    dr.ell(540, 1150, 620, 520, KR)
    dr.ell(540, 1150, 400, 330, (250, 240, 200))
    dr.ell(540, 1150, 240, 240, (255, 200, 30))
    sl = 50 + 20 * math.sin(t * 3)
    dr.rrect(540 - sl / 2, 960, 540 + sl / 2, 1340, 26, INK)
    dr.poly([(80, 760), (1000, 860), (1000, 760), (80, 640)], (90, 24, 56))
    f = tinta(dr); add_glow(f, *cam.p(540, 1150), 420, (255, 210, 60), 0.35 + 0.15 * math.sin(t * 5))
    img = acabado(f, T); d = ImageDraw.Draw(img)
    k = eob(t / 0.35)
    d.rounded_rectangle([90, 250, 990, 500], radius=30, fill=(230, 40, 50), outline=INK, width=10)
    d.text((540, 320), "REGLA DEL KRAKEN", font=font(int(64 * k) + 1), fill=(255, 255, 255), anchor="mm", stroke_width=8, stroke_fill=INK)
    if t > tl(12, 0.55): d.text((540, 425), "ATACA TODO LO QUE BRILLA", font=font(52), fill=(255, 222, 40), anchor="mm", stroke_width=7, stroke_fill=INK)
    return img, 0

@shot
def s14(t, D, T):    # en el bote solo hay una cosa que brilla (bolsillo)
    cam = Cam(540, 1150, 1.25)
    dr = D_(cam); cielo_noche(dr, t)
    for sx in (-1, 1):
        dr.ell(540 + sx * 160, 880, 70, 60, (250, 240, 200)); dr.ell(540 + sx * 160, 880, 40, 40, (255, 200, 30))
        dr.rrect(540 + sx * 160 - 9, 845, 540 + sx * 160 + 9, 915, 8, INK)
    info = escena_bote(dr, t, 540, 1560, 0.85, arms=(20, 20), elbows=(-50, -50), expr="nervous", look=(0, 1), sweat=True)
    f = tinta(dr) * 0.45
    hx, hy = info["head"]
    for sx in (-1, 1): add_glow(f, *cam.p(540 + sx * 160, 880), 120, (255, 200, 40), 0.55)
    puls = 0.6 + 0.4 * math.sin(t * 10)
    add_glow(f, *cam.p(hx + 60, hy + 300), 200, (180, 240, 255), 0.7 * puls)
    img = acabado(f, T)
    if t > tl(13, 0.6): burst(img, "¡BZZZ!", 760, 1250, 80, t - tl(13, 0.6), col=(180, 240, 255), ang=10)
    return img, 0

@shot
def s15(t, D, T):    # ¿y justo ahora me llega señal?
    cam = Cam(600, 1080, 1.6)
    dr = D_(cam); cielo_noche(dr, t)
    info = escena_bote(dr, t, 470, 1480, 0.9, arms=(30, 70), elbows=(-60, -100), expr="worried", mouth=boca(14, t), look=(0.8, 0.1))
    hx, hy = info["head"]
    celular_on(dr, hx + 250, hy + 40, 0.95, t)
    f = tinta(dr); add_glow(f, *cam.p(hx + 250, hy + 40), 260, (180, 240, 255), 0.55 + 0.2 * math.sin(t * 12))
    img = acabado(f, T)
    if t > tl(14, 0.45): burst(img, "¡DING!", 780, 470, 110, t - tl(14, 0.45), col=(120, 230, 255), ang=8)
    return img, 0

@shot
def s16(t, D, T):    # el tentáculo va directo al celular
    u = ease(t / (D * 0.85))
    cam = Cam(560, 1150, 1.15)
    dr = D_(cam); cielo_noche(dr, t)
    info = escena_bote(dr, t, 380, 1450, 0.8, sea_y=1500, arms=(140, 40), elbows=(0, -90), expr="shock", look=(1, -0.3), sweat=True)
    hx, hy = info["head"]
    px, py = hx + 200, hy + 70
    dr.rrect(px - 40, py - 75, px + 40, py + 75, 12, (220, 250, 255))
    tentaculo(dr, 980, 1650, -120, lerp(250, 1050, u), 85, t * 0.6, ph=0.3, curl=0.55)
    f = tinta(dr)
    add_glow(f, *cam.p(px, py), 200, (180, 240, 255), 0.6)
    f[..., 0] = np.clip(f[..., 0] + 40 * (0.5 + 0.5 * math.sin(t * 6)), 0, 255)
    img = acabado(f, T)
    if t > D * 0.55: burst(img, "¡SHLURP!", 600, 420, 130, t - D * 0.55, col=(240, 140, 190), ang=-6)
    return img, 3 + 6 * u

@shot
def s17(t, D, T):    # loro: ¡la cueva! ¡rema, rema!
    cam = Cam(600, 1050, lerp(1.0, 1.15, ease(t / D)))
    dr = D_(cam); cielo_noche(dr, t)
    isla_cueva(dr, 760, 1060, 1.0, t)
    mar(dr, t, 1160)
    loro(dr, 260, 1050 + 30 * math.sin(t * 5), 0.95, t, flap=1.0, mouth=boca(16, t), face=1)
    f = tinta(dr); add_glow(f, *cam.p(760, 1120), 170, (255, 210, 60), 0.6 + 0.2 * math.sin(t * 6))
    img = acabado(f, T)
    burst(img, "¡LA CUEVA!", 600, 380, 120, t - 0.15, col=(255, 222, 40), ang=-5)
    return img, 0

@shot
def s18(t, D, T):    # 100 metros… 4 horas para el amanecer
    cam = Cam(540, 1050, 1.0)
    dr = D_(cam); cielo_noche(dr, t)
    isla_cueva(dr, 820, 1020, 0.7, t)
    mar(dr, t, 1100)
    for k, (x, a) in enumerate(((600, -95), (430, -80))):
        tentaculo(dr, x, 1380 + k * 80, a, 420, 45, t, ph=k * 2.0, curl=0.9 if k else -0.9)
    escena_bote(dr, t, 230, 1450, 0.55, sea_y=1480, row=1.0, arms=(50, 50), elbows=(-30, -30), expr="nervous", look=(1, -0.2))
    f = tinta(dr); add_glow(f, *cam.p(820, 1060), 120, (255, 210, 60), 0.5)
    img = acabado(f, T); d = ImageDraw.Draw(img)
    for k in range(9):
        x = 330 + k * 50
        d.ellipse([x - 7, 1250 - k * 18 - 7, x + 7, 1250 - k * 18 + 7], fill=(255, 255, 255), outline=INK, width=3)
    d.text((540, 1120), "100 m", font=font(66), fill=(255, 255, 255), anchor="mm", stroke_width=8, stroke_fill=INK)
    secs = int(4 * 3600 - t * 700)
    d.text((540, 380), f"{secs // 3600:02d}:{secs % 3600 // 60:02d}:{secs % 60:02d}", font=font(130), fill=(255, 80, 60), anchor="mm", stroke_width=12, stroke_fill=INK)
    d.text((540, 490), "PARA EL AMANECER", font=font(48), fill=(255, 222, 40), anchor="mm", stroke_width=7, stroke_fill=INK)
    return img, 0

@shot
def s19(t, D, T):    # dilema: 1 tirar el celular · 2 apagar y remar a oscuras
    cam = Cam(540, 960, 1.0)
    dr = D_(cam, bg=(60, 40, 120))
    dr.poly([(540, -100), (1600, -100), (1600, 2600), (540, 2600)], (14, 18, 40))
    dr.poly([(470, -100), (610, -100), (610, 2600), (470, 2600)], (20, 16, 26))
    o1 = t > tl(18, 0.12); o2 = t > tl(18, 0.58)
    if o1:
        k1 = eob((t - tl(18, 0.12)) / 0.3)
        celular_on(dr, 270, 1050 + 40 * math.sin(t * 3), 1.1 * k1 + 0.01, t)
        for j in range(3): dr.line([(150 + j * 120, 1330), (190 + j * 120, 1310), (230 + j * 120, 1330)], (90, 160, 220), 8)
    if o2:
        k2 = eob((t - tl(18, 0.58)) / 0.3)
        dr.line([(700, 1300), (920, 900)], (150, 100, 56), 26 * k2 + 1)
        dr.ell(930, 880, 50 * k2 + 1, 90 * k2 + 1, (150, 100, 56))
        dr.ell(860, 760, 60 * k2 + 1, 60 * k2 + 1, (240, 236, 200))
        dr.ell(885, 745, 50 * k2 + 1, 50 * k2 + 1, (14, 18, 40))
    nico(dr, 540, 1560, 0.5, t, traje="pirata", arms=(70, 70), elbows=(60, 60), expr="worried", look=(-0.8 if t < tl(18, 0.5) else 0.8, -0.3))
    f = tinta(dr)
    if o1: add_glow(f, 270, 1050, 220, (180, 240, 255), 0.5)
    img = acabado(f, T); d = ImageDraw.Draw(img)
    d.text((540, 300), "¿QUÉ HACE NICO?", font=font(92), fill=(255, 222, 40), anchor="mm", stroke_width=12, stroke_fill=INK)
    for ok, x, n, a, b in ((o1, 270, "1", "TIRAR EL", "CELULAR"), (o2, 810, "2", "APAGARLO", "Y REMAR")):
        if not ok: continue
        d.ellipse([x - 90, 440, x + 90, 620], fill=(255, 255, 255), outline=INK, width=10)
        d.text((x, 532), n, font=font(130), fill=INK, anchor="mm")
        d.text((x, 700), a, font=font(54), fill=(255, 255, 255), anchor="mm", stroke_width=8, stroke_fill=INK)
        d.text((x, 762), b, font=font(54), fill=(255, 255, 255), anchor="mm", stroke_width=8, stroke_fill=INK)
    return img, 0

@shot
def s20(t, D, T):    # comenta 1 o 2
    cam = Cam(540, 1100, 1.25)
    dr = D_(cam, bg=(230, 40, 50))
    for k in range(18):
        a = k * math.pi / 9 - t * 0.6
        dr.poly([(540, 1100), (540 + math.cos(a) * 2000, 1100 + math.sin(a) * 2000), (540 + math.cos(a + 0.17) * 2000, 1100 + math.sin(a + 0.17) * 2000)], (250, 70, 70))
    nico(dr, 540, 1900, 0.72, t, traje="pirata", arms=(100, 170), elbows=(-20, 0), expr="happy", mouth=0)
    f = tinta(dr); img = acabado(f, T)
    d = ImageDraw.Draw(img)
    for k, (x, n) in enumerate(((330, "1"), (750, "2"))):
        p = 1 + 0.08 * math.sin(t * 8 + k * 3); r = 95 * p
        d.ellipse([x - r, 420 - r, x + r, 420 + r], fill=(255, 214, 10), outline=INK, width=10)
        d.text((x, 420), n, font=font(130 * p), fill=INK, anchor="mm")
    d.text((540, 620), "COMENTA", font=font(84), fill=(255, 255, 255), anchor="mm", stroke_width=10, stroke_fill=INK)
    return img, 0

@shot
def s21(t, D, T):    # nos vemos en otro mundo hipotético + avance
    cam = Cam(540, 1000, 1.0)
    dr = D_(cam, bg=(18, 10, 30)); cielo_noche(dr, t)
    o = 1 - ease((t - D + 1.0) / 0.8)
    portal(dr, 540, 1050, 330, t, o)
    if t < D - 1.2: nico(dr, 540, 1500, 0.5, t, traje="pirata", arms=(150, 20), elbows=(30, 0), expr="happy")
    f = tinta(dr); add_glow(f, *cam.p(540, 1050), 450, (150, 120, 255), 0.5 * o)
    img = acabado(f, T)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([150, 380, 930, 560], radius=36, fill=(255, 214, 10), outline=INK, width=8)
    d.text((540, 440), "CAPÍTULO 3 · FINAL", font=font(64), fill=INK, anchor="mm")
    d.text((540, 510), "MAÑANA · 6 P. M.", font=font(46), fill=(200, 40, 50), anchor="mm")
    return img, 0

assert len(SHOTS) == len(VOZ), (len(SHOTS), len(VOZ))

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
    S_ = STARTS
    def pirata(s, tend, g=1.0):
        e8 = 0.2
        mel = [62, 65, 69, 74, 72, 69, 70, 69, 65, 67, 65, 62, 64, 65, 67, 69, 70, 72, 74, 72, 69, 65, 64, 62]
        bass = [38, 38, 41, 43, 45, 41, 38, 45]; k = 0
        while s < tend:
            x = seg(e8 * 1.5); m = mel[k % len(mel)]
            if k % 3 != 2 or k % 6 == 5:
                sq = np.sign(np.sin(2 * np.pi * hz(m) * x)) * 0.5 + np.sin(2 * np.pi * hz(m) * 2 * x) * 0.3
                add(s, g * 0.035 * sq * np.exp(-x * 4) * (1 - np.exp(-x * 60)))
            if k % 3 == 0:
                bm = bass[(k // 6) % len(bass)]; xb = seg(e8 * 3)
                add(s, g * 0.09 * np.exp(-xb * 3) * np.sin(2 * np.pi * hz(bm) * xb))
                add(s, g * 0.16 * np.exp(-x * 20) * np.sin(2 * np.pi * (70 + 60 * np.exp(-x * 25)) * x))
            if k % 6 == 3: add(s, g * 0.06 * rng.standard_normal(len(x)) * np.exp(-x * 25))
            k += 1; s += e8
    # A) recuerdo (suave) + música pirata hasta la ruleta
    pirata(0.0, S_[1], 0.6); pirata(S_[1], S_[6], 1.0)
    x = seg(0.6); add(S_[1] + tl(1, 0.72), 0.3 * np.exp(-x * 4) * (np.sin(2 * np.pi * 523 * x) + np.sin(2 * np.pi * 784 * x)) / 2)  # ganó
    xw = seg(S_[6] - S_[4]); add(S_[4], 0.05 * bp(200, 1200)[:len(xw)] * (0.5 + 0.5 * np.sin(2 * np.pi * 0.18 * xw)))
    # B) ruleta: concurso + redoble + clics + ding
    b = 0.5; prog = [[60, 64, 67], [65, 69, 72], [67, 71, 74], [60, 64, 67]]
    for k in range(int((S_[8] - S_[6]) / (b / 2))):
        s = S_[6] + k * b / 2; ch = prog[int(k / 4) % 4]; x = seg(0.22)
        if k % 2 == 0: add(s, 0.05 * np.exp(-x * 10) * np.sign(np.sin(2 * np.pi * hz(ch[k // 2 % 3] + 12) * x)))
        if k % 4 == 0: add(s, 0.2 * np.exp(-x * 18) * np.sin(2 * np.pi * (60 + 80 * np.exp(-x * 30)) * x))
    t0, t1 = S_[6] + tl(6, 0.55), S_[7] + LEAD + len(VOZ[7]) / SR
    xr = seg(t1 - t0); add(t0, 0.06 * bp(150, 600)[:len(xr)] * (0.6 + 0.4 * np.sin(2 * np.pi * 18 * xr)) * (xr / xr[-1]))
    prev = int(ang_ruleta(t0) / 22.5)
    for k in range(int((t1 - t0) * FPS)):
        T = t0 + k / FPS; a = ang_ruleta(T)
        if int(a / 22.5) != prev:
            prev = int(a / 22.5); xc = seg(0.03); add(T, 0.25 * np.exp(-xc * 200) * np.sin(2 * np.pi * 2500 * xc))
    x = seg(1.4); add(t1, 0.3 * np.exp(-x * 2) * (np.sin(2 * np.pi * 311 * x) + np.sin(2 * np.pi * 370 * x) + np.sin(2 * np.pi * 440 * x)) / 3)   # acorde misterioso
    x = seg(0.5); add(t1, 0.5 * np.exp(-x * 8) * np.sin(2 * np.pi * (55 + 50 * np.exp(-x * 20)) * x))
    # C) kraken: dron grave + latido hasta el dilema
    kt0, kt1 = S_[8], S_[18]
    xd = seg(kt1 - kt0); add(kt0, 0.08 * (np.sin(2 * np.pi * 41 * xd) + 0.5 * np.sin(2 * np.pi * 61.7 * xd)) * np.clip(xd / 2, 0, 1))
    add(kt0, 0.05 * bp(200, 1200)[:len(xd)] * (0.5 + 0.5 * np.sin(2 * np.pi * 0.2 * xd)))
    for kk in range(int((kt1 - kt0) / 0.8)):
        for dd in (0, 0.22):
            x = seg(0.25); add(kt0 + kk * 0.8 + dd, 0.18 * np.exp(-x * 14) * np.sin(2 * np.pi * (52 + 20 * np.exp(-x * 30)) * x))
    x = seg(2.2); add(S_[9] + 0.3, 0.4 * low[:len(x)] * np.exp(-x * 1.2))                                   # rugido del kraken
    x = seg(2.0); add(S_[9] + 0.3, 0.16 * np.exp(-x * 1.5) * np.sign(np.sin(2 * np.pi * (70 - 15 * x) * x)))
    x = seg(0.5); add(S_[9] + 0.05, 0.3 * wh[:len(x)] * np.exp(-x * 5))                                     # salpicón
    x = seg(0.3); add(S_[14] + tl(14, 0.45), 0.3 * np.exp(-x * 9) * np.sin(2 * np.pi * 1318 * x))             # ding notificación
    x = seg(0.3); add(S_[14] + tl(14, 0.45) + 0.15, 0.3 * np.exp(-x * 9) * np.sin(2 * np.pi * 1760 * x))
    x = seg(1.2); add(S_[15] + 0.1, 0.3 * bp(100, 700)[:len(x)] * np.sin(np.pi * x / 1.2))                   # tentáculo
    x = seg(0.6); add(S_[15] + DURS[15] * 0.55, 0.35 * bp(300, 2000)[:len(x)] * np.exp(-x * 6))
    for kk in range(int(DURS[17] / 0.5) + 1):
        x = seg(0.05); add(S_[17] + kk * 0.5, 0.25 * np.exp(-x * 150) * np.sin(2 * np.pi * 1800 * x))          # tic tac
    # D) dilema: pulso tenso
    for kk in range(int((S_[20] - S_[18]) / 0.6)):
        x = seg(0.3); add(S_[18] + kk * 0.6, 0.12 * np.exp(-x * 10) * np.sin(2 * np.pi * (55 + 20 * (kk % 2)) * x))
        x = seg(0.08); add(S_[18] + kk * 0.6 + 0.3, 0.05 * np.exp(-x * 60) * np.sin(2 * np.pi * 1200 * x))
    x = seg(1.6); add(S_[20] + 0.2, 0.12 * np.exp(-x * 1.5) * (np.sin(2 * np.pi * 523 * x) + np.sin(2 * np.pi * 784 * x)) / 2)
    for k in range(1, len(S_) - 1):   # whoosh en cada corte
        x = seg(0.25); add(S_[k] - 0.08, 0.06 * wh[:len(x)] * np.sin(np.pi * x / 0.25))
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
        ts = [STARTS[i] + DURS[i] * 0.6 for i in range(len(SHOTS))] if os.environ["PREVIEW"] == "auto" else [float(x) for x in os.environ["PREVIEW"].split(",")]
        ims = [frame(T).resize((270, 480)) for T in ts]
        sheet = Image.new("RGB", (270 * 6, 480 * ((len(ims) + 5) // 6)))
        for k, im in enumerate(ims): sheet.paste(im, ((k % 6) * 270, (k // 6) * 480))
        sheet.save("sheet.png"); print("TOTAL", round(TOTAL, 2), [round(s, 2) for s in STARTS]); sys.exit()
    if os.environ.get("BIG"):
        for k, T in enumerate(os.environ["BIG"].split(",")): frame(float(T)).save(f"big{k}.png")
        sys.exit()
    if os.environ.get("AUDIO"):
        make_audio("audio.wav"); sys.exit()
    if os.environ.get("RANGE"):   # render de un tramo (sin audio) para paralelizar
        a, b = [int(v) for v in os.environ["RANGE"].split(",")]
        p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                              "-c:v", "libx264", "-preset", "veryfast", "-crf", "26", "-tune", "animation", "-pix_fmt", "yuv420p", OUT], stdin=subprocess.PIPE)
        for k in range(a, b):
            p.stdin.write(frame(k / FPS).convert("RGB").tobytes())
            if k % 300 == 0: print(f"{k}/{b}", flush=True)
        p.stdin.close(); p.wait(); print("tramo listo", OUT); sys.exit()
    print("NFRAMES", int(TOTAL * FPS))
