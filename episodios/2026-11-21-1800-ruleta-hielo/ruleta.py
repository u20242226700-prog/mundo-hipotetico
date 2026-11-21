#!/usr/bin/env python3
"""LA RULETA DE NICO · T4: ERA DE HIELO · Capítulo 1/3.
La ruleta decide sola y cae en HIELO. Nico (traje de pieles) llega a un mundo congelado, despierta a Doña Lana
(abuela mamut gruñona, trompa congelada) y hace fuego frotando palitos a cambio de dormir en su cueva. Aparece un
tigre dientes de sable. Dato real: colmillos de hasta 28 cm, pero mordida más débil que la de un león (McHenry et al.
2007, PNAS). Regla: le tiene miedo al fuego. Tormenta: se acaba el fuego. Dilema: 1 cueva oscura / 2 lago congelado."""
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
VOZ_F = sorted(f for f in os.listdir(VOZ_DIR) if f.endswith(".wav"))
VOZ = [wavfile.read(f"{VOZ_DIR}/{f}")[1].astype(np.float32) / 32768 for f in VOZ_F]
SR = 44100; LEAD = 0.08
DURS = [len(v) / SR + LEAD + 0.16 for v in VOZ]
ENV = []
for v in VOZ:
    hop = SR // 60
    e = np.array([np.sqrt(np.mean(v[i:i + hop] ** 2)) for i in range(0, len(v), hop)])
    e = e / (np.percentile(e, 95) + 1e-6); ENV.append(np.convolve(e, np.ones(3) / 3, mode="same"))
def boca(k, t):
    i = int((t - LEAD) * 60)
    return float(np.clip(ENV[k][i] * 1.15 - 0.12, 0, 1)) if 0 <= i < len(ENV[k]) else 0.0

CHUNKS = [
    [("¿Y si la ruleta", ["ruleta"]), ("te manda…", []), ("a la ERA", ["ERA"]), ("DE HIELO?", ["HIELO?"])],
    [("Nueva serie de", ["Nueva"]), ("La Ruleta de Nico.", ["Ruleta"]), ("Esta vez la ruleta", []), ("decide sola…", ["sola…"]), ("gira, gira…", ["gira…"]), ("¡y cae en", []), ("HIELO!", ["HIELO!"])],
    [("Nico cruza", []), ("el portal…", ["portal…"]), ("y aparece en un", []), ("mundo congelado,", ["congelado,"]), ("vestido con pieles", ["pieles"]), ("de la Edad de Hielo", ["Hielo"])],
    [("¡Brrr!", ["¡Brrr!"]), ("¡Hace tanto frío", ["frío"]), ("que se me están", []), ("congelando", ["congelando"]), ("los mocos!", ["mocos!"])],
    [("Dato real:", ["real:"]), ("hace 20.000 años,", ["20.000"]), ("el hielo cubría", ["hielo"]), ("casi un cuarto", ["cuarto"]), ("de toda la tierra", []), ("firme del planeta", ["planeta"])],
    [("¿Quién está", []), ("pisando mi", []), ("cama de nieve?", ["nieve?"])],
    [("¡Un mamut!", ["mamut!"]), ("¡Perdón, perdón,", ["Perdón,"]), ("señora mamut!", [])],
    [("Es Doña Lana,", ["Lana,"]), ("una abuela mamut", ["mamut"]), ("muy gruñona…", ["gruñona…"]), ("que tiene la trompa", ["trompa"]), ("congelada", ["congelada"])],
    [("Si me ayudas", []), ("a hacer fuego,", ["fuego,"]), ("te dejo dormir", []), ("en mi cueva", ["cueva"])],
    [("¡Hecho!", ["¡Hecho!"]), ("Fuego… eh…", ["Fuego…"]), ("¿y cómo se hace", []), ("fuego sin", []), ("encendedor?", ["encendedor?"])],
    [("Nico frota", []), ("dos palitos…", ["palitos…"]), ("por diez minutos…", ["diez"]), ("¡y sale", []), ("una chispa!", ["chispa!"])],
    [("¡Fuego!", ["¡Fuego!"]), ("¡Soy un genio", ["genio"]), ("de las cavernas!", ["cavernas!"])],
    [("Pero en la", []), ("oscuridad…", ["oscuridad…"]), ("se encienden", []), ("dos ojos", ["ojos"]), ("amarillos", ["amarillos"])],
    [("¡Un tigre", ["tigre"]), ("dientes de sable!", ["sable!"]), ("Y no viene solo", []), ("a calentarse", ["calentarse"])],
    [("Mmm…", ["Mmm…"]), ("un mamut", ["mamut"]), ("y un niño…", ["niño…"]), ("cena para dos", ["cena"])],
    [("Dato real:", ["real:"]), ("sus colmillos", ["colmillos"]), ("medían hasta", []), ("28 centímetros…", ["28"]), ("pero mordía", []), ("con menos fuerza", ["menos"]), ("que un león.", ["león."]), ("Los usaba", []), ("como cuchillos,", ["cuchillos,"]), ("con precisión", ["precisión"])],
    [("Regla del tigre:", ["Regla"]), ("le tiene miedo", ["miedo"]), ("al fuego.", ["fuego."]), ("Mientras haya llama,", ["llama,"]), ("no se acerca", [])],
    [("Pero empieza", []), ("una tormenta", ["tormenta"]), ("de nieve…", ["nieve…"]), ("y el fuego", ["fuego"]), ("se hace cada vez", []), ("más chiquito", ["chiquito"])],
    [("¡Nico!", ["¡Nico!"]), ("¡Se nos acabaron", []), ("los palitos!", ["palitos!"])],
    [("¿Qué hace Nico?", ["Nico?"]), ("Uno:", ["Uno:"]), ("meterse en la", []), ("cueva oscura.", ["cueva"]), ("Dos:", ["Dos:"]), ("cruzar el lago", ["lago"]), ("congelado", ["congelado"])],
    [("¿Uno o dos?", ["Uno", "dos?"]), ("Comenta,", ["Comenta,"]), ("y en la próxima parte", []), ("verás si", []), ("elegiste bien.", ["bien."]), ("Nos vemos en otro", []), ("mundo hipotético", ["hipotético"])],
]
RK = 1
DURS[0] += 0.3; DURS[1] += 0.5; DURS[19] += 0.45; DURS[20] += 0.5
STARTS = np.cumsum([0] + DURS).tolist(); TOTAL = STARTS[-1]
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

def portal(dr, x, y, r, t, o=1.0):
    R = r * o
    if R < 4: return
    dr.ell(x, y, R, R * 1.18, (40, 16, 70), nolin=True)
    for k in range(7):
        rr = R * (1 - k * 0.12); a0 = (t * (160 + 30 * k) * (1 if k % 2 else -1)) % 360
        X, Y = dr.cam.p(x, y); rx, ry = dr.cam.s(rr), dr.cam.s(rr * 1.18)
        dr.d.arc([X - rx, Y - ry, X + rx, Y + ry], a0, a0 + 240, fill=(90, 230, 255) if k % 2 == 0 else (190, 110, 255), width=max(3, int(dr.cam.s(R * 0.05))))
        dr.dn.arc([X - rx, Y - ry, X + rx, Y + ry], a0, a0 + 240, fill=255, width=max(3, int(dr.cam.s(R * 0.05))) + 4)

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


def D_(cam, bg=(0, 0, 0)): return D(cam, bg)
def oscuro(f, k=0.3, tint=(0.75, 0.85, 1.25)): return np.clip(f * k * np.array(tint, np.float32), 0, 255)
def rojo(f, a):   # luz de alarma
    return np.clip(f * np.array([1.0 + 0.25 * a, 1 - 0.45 * a, 1 - 0.45 * a], np.float32), 0, 255)
# ------------------------------------------------------------ mundo congelado
SKY = [(96, 132, 196), (126, 162, 214), (164, 196, 230), (200, 222, 242), (226, 238, 248)]
SKY_N = [(14, 18, 44), (22, 28, 62), (32, 40, 82), (44, 54, 100), (58, 70, 116)]
def cielo(dr, y0=-900, y1=1000, night=False):
    pal = SKY_N if night else SKY
    n = len(pal); h = (y1 - y0) / n
    for k, c in enumerate(pal): dr.rrect(-600, y0 + k * h, 1700, y0 + (k + 1) * h + 2, 0, c, nolin=True)
    if night:
        for k in range(30):
            dr.ell((k * 173) % 1500 - 200, y0 + 100 + (k * 97) % int(max(200, (y1 - y0) * 0.7)), 4, 4, (240, 240, 255), nolin=True)

def aurora(dr, t, y=300):
    for k in range(3):
        pts = [(-300 + i * 120, y + k * 60 + 60 * math.sin(i * 0.6 + t * 0.7 + k)) for i in range(16)]
        dr.line(pts, (90, 230, 170) if k != 1 else (150, 120, 240), 26 - k * 6, nolin=True)

def glaciares(dr, y, night=False):
    L = (236, 244, 252) if not night else (120, 136, 170); Sh = (172, 198, 232) if not night else (80, 94, 136)
    for (x, w, h) in ((-120, 620, 560), (420, 700, 700), (980, 640, 520)):
        dr.poly([(x - w / 2, y), (x - w * 0.08, y - h), (x + w * 0.06, y - h * 0.94), (x + w / 2, y)], L, nolin=True)
        dr.poly([(x + w * 0.06, y - h * 0.94), (x + w / 2, y), (x + w * 0.08, y)], Sh, nolin=True)
        dr.poly([(x - w * 0.08, y - h), (x + w * 0.06, y - h * 0.94), (x - w * 0.02, y - h * 0.7)], (255, 255, 255) if not night else (150, 166, 200), nolin=True)

def pino(dr, x, y, s, night=False):
    S = lambda v: v * s
    dr.rrect(x - S(22), y - S(120), x + S(22), y, S(6), (96, 64, 44))
    g = (40, 96, 80) if not night else (24, 50, 54)
    for k in range(3):
        yy = y - S(90) - k * S(150); w = S(190 - k * 45)
        dr.poly([(x - w, yy), (x, yy - S(230)), (x + w, yy)], g)
        dr.poly([(x - w * 0.55, yy - S(110)), (x, yy - S(230)), (x + w * 0.55, yy - S(110)), (x, yy - S(140))], (250, 252, 255) if not night else (150, 166, 200))

def nieve_bg(dr, t, hor=1050, night=False, trees=True, glac=True):
    cielo(dr, -900, hor, night)
    if night: aurora(dr, t, 250)
    if glac: glaciares(dr, hor, night)
    dr.rrect(-600, hor - 30, 1700, hor + 40, 0, (196, 214, 238) if not night else (70, 82, 118), nolin=True)
    dr.rrect(-600, hor, 1700, 2700, 0, (242, 246, 252) if not night else (96, 108, 146))
    for k in range(9):
        dr.ell(-200 + (k * 237) % 1500, hor + 120 + (k * 173) % 1300, 180, 36, (214, 226, 244) if not night else (80, 92, 130), nolin=True)
    if trees:
        pino(dr, 60, hor + 220, 0.95, night); pino(dr, 1030, hor + 260, 1.05, night)
        pino(dr, 300, hor + 40, 0.45, night); pino(dr, 820, hor + 50, 0.5, night)

def copos(img, t, n=40, k=1.0, wind=0.0, big=1.0):
    d = ImageDraw.Draw(img)
    for i in range(n):
        sp = 120 + (i * 37) % 160
        x = ((i * 263) + t * (40 + wind * 900) + 30 * math.sin(t * 1.3 + i)) % (W + 200) - 100
        y = ((i * 151) + t * sp * k) % (H + 100) - 50
        r = (3 + (i % 4) * 2) * big
        if wind > 0.3: d.line([(x, y), (x - wind * 40 * r / 4, y - 6)], fill=(255, 255, 255), width=int(r))
        else: d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255))

def fogata(dr, x, y, s, t, k=1.0):
    """k = tamaño de la llama (0..1)."""
    S = lambda v: v * s
    for a in (-18, 18):
        dr.poly([(x - S(130), y - S(10) + S(a)), (x + S(130), y - S(10) - S(a)), (x + S(130), y + S(22) - S(a)), (x - S(130), y + S(22) + S(a))], (110, 70, 44))
    for kk in range(7): dr.ell(x - S(150) + kk * S(50), y + S(26), S(26), S(18), (130, 130, 140))
    if k <= 0.02: return
    for j, (col, sc) in enumerate((((240, 70, 40), 1.0), ((250, 150, 40), 0.72), ((255, 230, 110), 0.42))):
        h = S(300) * k * sc * (1 + 0.12 * math.sin(t * 13 + j)); w = S(120) * sc * (0.5 + 0.5 * k)
        fl = S(18) * math.sin(t * 9 + j * 2)
        dr.poly([(x - w, y), (x - w * 0.6 + fl, y - h * 0.55), (x - w * 0.2, y - h * 0.4), (x + fl * 1.5, y - h), (x + w * 0.3, y - h * 0.45), (x + w * 0.65 - fl, y - h * 0.6), (x + w, y)], col, nolin=j > 0)

def cueva_boca(dr, x, y, w, h, col=(110, 116, 140), dark=(18, 16, 26)):
    dr.poly([(x - w, y), (x - w * 0.9, y - h * 0.8), (x - w * 0.4, y - h * 1.1), (x + w * 0.4, y - h * 1.08), (x + w * 0.95, y - h * 0.75), (x + w, y)], col)
    dr.poly([(x - w * 0.6, y), (x - w * 0.55, y - h * 0.6), (x - w * 0.15, y - h * 0.8), (x + w * 0.3, y - h * 0.78), (x + w * 0.6, y - h * 0.55), (x + w * 0.62, y)], dark)
    for k in range(6):   # carámbanos
        xx = x - w * 0.5 + k * w * 0.2
        dr.poly([(xx - 16, y - h * 0.78 + (k % 2) * 20), (xx + 16, y - h * 0.78 + (k % 2) * 20), (xx, y - h * 0.62 + (k % 3) * 22)], (210, 236, 250))

def lago(dr, t, y0, y1):
    dr.rrect(-600, y0, 1700, y1, 0, (176, 216, 240))
    for k in range(5): dr.ell(-100 + k * 300, y0 + 60 + (k % 2) * 80, 140, 18, (226, 244, 252), nolin=True)
    for k in range(4):   # grietas
        x = 100 + k * 260; y = y0 + 80 + (k * 70) % max(60, int(y1 - y0 - 120))
        dr.line([(x, y), (x + 50, y + 30), (x + 30, y + 70), (x + 90, y + 100)], (90, 140, 190), 6, nolin=True)

# ------------------------------------------------------------ DOÑA LANA (abuela mamut)
MF = (160, 92, 62); MF_D = (126, 68, 46); MF_L = (190, 120, 82)
def trompa_pts(x0, y0, s, face, curl=0.0, t=0.0, up=0.0):
    pts = [(x0, y0)]; a = math.radians(15 + 10 * math.sin(t * 1.6))
    for i in range(10):
        u = i / 9
        a += math.radians((-14 if up > 0.5 else 9) + curl * 18 * u)
        pts.append((pts[-1][0] + face * math.sin(a) * s * 44, pts[-1][1] + math.cos(a) * s * 44 * (1 - 2 * up * u)))
    return pts

def mamut(dr, x, y, s, t, mouth=0.0, face=1, expr="grumpy", look=(0, 0), frozen=False, up=0.0, sleep=False):
    """(x, y) = suelo. Alto ≈ 1100*s."""
    S = lambda v: v * s
    F = lambda dx: x + face * S(dx)
    by = y - S(470) + S(8) * math.sin(t * 2)
    for k, dx in enumerate((-250, -110, 120, 250)):   # patas
        dr.rrect(F(dx) - S(62), by + S(60), F(dx) + S(62), y, S(40), MF_D if k % 2 else MF)
        for j in range(3): dr.ell(F(dx) - S(34) + j * S(34), y - S(8), S(20), S(14), (236, 226, 206))
    dr.ell(F(-350), by - S(40), S(30), S(60), MF_D)   # colita
    dr.ell(x, by, S(400), S(300), MF, shade=True)
    for k in range(14):   # pelo largo colgando
        xx = -360 + k * 54
        dr.poly([(F(xx), by + S(150)), (F(xx + 30), by + S(290) + S(14) * math.sin(t * 2 + k)), (F(xx + 60), by + S(150))], MF_D)
    dr.ell(F(-60), by - S(250), S(230), S(110), MF_L)   # joroba
    hx, hy = F(300), by - S(150)
    dr.ell(hx - face * S(60), hy + S(10), S(120), S(150), MF_D)   # oreja
    dr.ell(hx, hy, S(220), S(230), MF, shade=True)
    dr.ell(hx + face * S(10), hy - S(210), S(110), S(70), MF_D)   # copete
    dr.ell(hx + face * S(10), hy - S(268), S(58), S(52), MF_D)   # moño de abuela
    dr.rrect(hx + face * S(10) - S(48), hy - S(238), hx + face * S(10) + S(48), hy - S(214), S(8), (220, 60, 80))
    # colmillos curvos
    for sd, off in ((1, 0), (-1, -40)):
        pts = [(hx + face * S(110 + off), hy + S(110))]
        a = 0.2
        for i in range(8):
            a += 0.32
            pts.append((pts[-1][0] + face * math.cos(a) * S(62), pts[-1][1] + math.sin(-a + 1.4) * S(54)))
        dr.line(pts, (250, 244, 226), S(30 - i * 0) if sd > 0 else S(24))
    # trompa
    tp = trompa_pts(hx + face * S(150), hy + S(40), s, face, curl=1.0 if up < 0.5 else 0, t=t, up=up)
    for i in range(len(tp) - 1):
        dr.line([tp[i], tp[i + 1]], MF_L, S(84 - i * 5.5))
    for i in range(1, len(tp) - 1, 2):
        dr.line([(tp[i][0] - S(26 - i * 2), tp[i][1]), (tp[i][0] + S(26 - i * 2), tp[i][1])], MF_D, S(6))
    if frozen:   # hielo en la punta de la trompa
        ex, ey = tp[-1]
        dr.ell(ex, ey, S(52), S(46), (200, 236, 252))
        dr.poly([(ex - S(14), ey + S(30)), (ex + S(14), ey + S(30)), (ex, ey + S(90))], (210, 240, 255))
    # ojos (párpados de abuela) + gafas redondas
    for k, dx in enumerate((60, 150)):
        ex, ey = hx + face * S(dx) - face * S(40), hy - S(60)
        if sleep or (t % 3.1) < 0.12:
            dr.line([(ex - S(28), ey), (ex + S(28), ey)], (40, 24, 20), S(9))
        else:
            big = 1.25 if expr == "shock" else 1.0
            dr.ell(ex, ey, S(32) * big, S(36) * big, (255, 255, 255))
            px, py = ex + (look[0] + face * 0.2) * S(10), ey + look[1] * S(10)
            dr.ell(px, py, S(15), S(18), (30, 20, 20)); dr.ell(px - S(5), py - S(6), S(5), S(5), (255, 255, 255))
            if expr in ("grumpy", "angry"):
                dr.poly([(ex - S(36), ey - S(40) + (S(12) if (dx == 60) == (face > 0) else 0)), (ex + S(36), ey - S(40) + (0 if (dx == 60) == (face > 0) else S(12))), (ex + S(36), ey - S(22)), (ex - S(36), ey - S(22))], MF)
        X, Y = dr.cam.p(ex, ey); r = dr.cam.s(S(48))
        dr.d.ellipse([X - r, Y - r, X + r, Y + r], outline=(60, 40, 30), width=max(3, int(dr.cam.s(S(8)))))
        dr.dn.ellipse([X - r, Y - r, X + r, Y + r], outline=255, width=max(3, int(dr.cam.s(S(8)))) + 4)
    dr.ell(hx + face * S(40), hy + S(40), S(24), S(14), (230, 130, 120))   # cachete
    mo = clamp(mouth)
    mx, my = hx + face * S(70), hy + S(130)
    if mo > 0.06 or expr == "shock":
        mo = max(mo, 0.5 if expr == "shock" else 0)
        dr.ell(mx, my, S(40), S(10 + 26 * mo), (110, 30, 40))
    else:
        dr.line([(mx - S(36), my + S(6)), (mx, my - S(2)), (mx + S(36), my + S(6))], (110, 30, 40), S(8))
    return tp[-1]

# ------------------------------------------------------------ TIGRE DIENTES DE SABLE
TG = (226, 146, 58); TG_D = (190, 108, 40); TG_B = (250, 226, 180); TG_S = (70, 40, 30)
def tigre_cabeza(dr, hx, hy, s, t, mouth=0.0, face=-1, look=(0, 0), expr="smug"):
    S = lambda v: v * s
    mo = clamp(mouth)
    for sx in (-1, 1):   # orejas
        dr.poly([(hx + sx * S(150), hy - S(130)), (hx + sx * S(190), hy - S(250)), (hx + sx * S(70), hy - S(190))], TG)
        dr.poly([(hx + sx * S(150), hy - S(150)), (hx + sx * S(175), hy - S(220)), (hx + sx * S(100), hy - S(185))], (240, 170, 160))
    dr.ell(hx, hy, S(220), S(200), TG, shade=True)
    for sx in (-1, 1):   # cachetes peludos
        dr.poly([(hx + sx * S(150), hy - S(10)), (hx + sx * S(260), hy + S(60)), (hx + sx * S(170), hy + S(80)), (hx + sx * S(230), hy + S(130)), (hx + sx * S(120), hy + S(130))], TG_B)
    for k in range(3): dr.poly([(hx - S(40) + k * S(40), hy - S(200)), (hx - S(20) + k * S(40), hy - S(120)), (hx + k * S(40), hy - S(200))], TG_S)
    for sx in (-1, 1):
        dr.poly([(hx + sx * S(210), hy - S(40)), (hx + sx * S(130), hy - S(20)), (hx + sx * S(205), hy - S(5))], TG_S)
    # hocico + boca
    my = hy + S(80)
    dr.ell(hx, my + S(40) + S(60) * mo, S(80), S(40 + 30 * mo), (120, 30, 40))
    dr.ell(hx, my + S(80) + S(70) * mo, S(90), S(36), TG_B)   # mandíbula
    for sx in (-1, 1):
        dr.ell(hx + sx * S(55), my, S(70), S(55), TG_B)
        dr.poly([(hx + sx * S(30), my + S(20)), (hx + sx * S(52), my + S(200)), (hx + sx * S(74), my + S(30))], (252, 250, 238))   # colmillos de sable
    dr.poly([(hx - S(32), my - S(46)), (hx + S(32), my - S(46)), (hx, my - S(12))], (220, 110, 120))
    for sx in (-1, 1):   # bigotes
        for k in range(2): dr.line([(hx + sx * S(90), my - S(10) + k * S(26)), (hx + sx * S(230), my - S(30) + k * S(40))], (250, 250, 240), S(4), nolin=True)
    for sx in (-1, 1):   # ojos amarillos con pupila de rendija
        ex, ey = hx + sx * S(80), hy - S(50)
        dr.ell(ex, ey, S(44), S(38), (255, 222, 60))
        dr.ell(ex + look[0] * S(12), ey + look[1] * S(8), S(9), S(30), (24, 18, 26))
        lid = S(18) if expr == "smug" else S(4)
        dr.poly([(ex - S(48), ey - S(40)), (ex + S(48), ey - S(40) + sx * S(10) * (1 if expr == "angry" else -0.5)), (ex + S(48), ey - S(38) + lid), (ex - S(48), ey - S(38) + lid)], TG)
    return (hx, hy)

def tigre(dr, x, y, s, t, mouth=0.0, face=-1, look=(0, 0), expr="smug", step=0.0):
    """(x, y) = patas. Alto ≈ 900*s. Cola corta (como el Smilodon real)."""
    S = lambda v: v * s
    F = lambda dx: x + face * S(dx)
    by = y - S(380) - (S(14) * abs(math.sin(step * math.pi)) if step else 0)
    dr.poly([(F(-300), by - S(40)), (F(-400), by - S(110) + S(10) * math.sin(t * 3)), (F(-370), by - S(130)), (F(-280), by - S(80))], TG_D)
    for k, dx in enumerate((-230, -120, 130, 240)):
        sw = S(20) * math.sin(step * 6 + k * 1.7) if step else 0
        dr.rrect(F(dx) - S(48) + sw, by + S(40), F(dx) + S(48) + sw, y, S(32), TG_D if k % 2 else TG)
        dr.ell(F(dx) + sw, y - S(10), S(58), S(26), TG_B)
    dr.ell(x, by, S(340), S(190), TG, shade=True)
    dr.ell(F(40), by + S(90), S(240), S(80), TG_B)
    for k in range(5): dr.poly([(F(-220 + k * 90), by - S(185)), (F(-200 + k * 90), by - S(60)), (F(-170 + k * 90), by - S(180))], TG_S)
    return tigre_cabeza(dr, F(300), by - S(170), s * 0.95, t, mouth, face, look, expr)

def ojos_oscuridad(dr, x, y, s, t, o=1.0):
    S = lambda v: v * s
    blink = (t % 2.4) < 0.12
    for sx in (-1, 1):
        if blink: dr.line([(x + sx * S(80) - S(40), y), (x + sx * S(80) + S(40), y)], (255, 222, 60), S(8), nolin=True)
        else:
            dr.ell(x + sx * S(80), y, S(44) * o, S(36) * o, (255, 222, 60), nolin=True)
            dr.ell(x + sx * S(80), y, S(9) * o, S(30) * o, (24, 18, 26), nolin=True)

def palito(dr, x, y, L, ang, col=(150, 100, 60)):
    a = math.radians(ang)
    dr.line([(x, y), (x + math.cos(a) * L, y + math.sin(a) * L)], col, 18)

def badge(img, T):
    d = ImageDraw.Draw(img)
    f = font(36)
    d.rounded_rectangle([36, 110, 36 + f.getlength("LA RULETA DE NICO") + 44, 170], radius=16, fill=(230, 40, 50), outline=INK, width=5)
    d.text((58, 140), "LA RULETA DE NICO", font=f, fill=(255, 255, 255), anchor="lm")
    txt = "CAPÍTULO 1/3"
    x1 = W - 36; x0 = x1 - f.getlength(txt) - 44
    d.rounded_rectangle([x0, 110, x1, 170], radius=16, fill=(255, 214, 10), outline=INK, width=5)
    d.text((x0 + 22, 140), txt, font=f, fill=INK, anchor="lm")
    if T > STARTS[2]:
        f2 = font(30); t2 = "ERA DE HIELO"
        d.rounded_rectangle([36, 182, 36 + f2.getlength(t2) + 40, 230], radius=14, fill=(170, 220, 245), outline=INK, width=4)
        d.text((56, 206), t2, font=f2, fill=INK, anchor="lm")

SEG_HIELO = 7
def ang_ruleta(T):
    t0, t1 = STARTS[RK] + LEAD + len(VOZ[RK]) / SR * 0.35, STARTS[RK] + LEAD + len(VOZ[RK]) / SR * 0.82
    final = 45 - 360 * 4
    if T < t0: return 0.0
    u = clamp((T - t0) / (t1 - t0))
    return final * (1 - (1 - u) ** 3)

# ------------------------------------------------------------ planos
SHOTS = []
def shot(fn): SHOTS.append(fn); return fn
def tl(k, frac): return LEAD + len(VOZ[k]) / SR * frac
PI = "pieles"

@shot
def s01(t, D, T):    # gancho: Nico en sudadera congelándose, tigre asoma atrás
    u = t / D
    cam = Cam(540, lerp(1000, 1080, ease(u)), lerp(1.0, 1.12, ease(u)))
    dr = D_(cam); nieve_bg(dr, t, hor=1150)
    if u > 0.45: tigre_cabeza(dr, 860, lerp(1500, 1250, ease((u - 0.45) / 0.3)), 0.9, t, mouth=0.3, face=-1, look=(-0.8, 0.2))
    pino(dr, 960, 1700, 0.9)
    nico(dr, 400, 1760, 0.64, t, traje="sudadera", arms=(40 + 8 * math.sin(t * 30), 40 - 8 * math.sin(t * 30)), elbows=(110, 110), expr="nervous" if u < 0.6 else "shock", look=(0.8, -0.3) if u > 0.6 else (0, 0), sweat=False)
    f = tinta(dr); img = acabado(f, T)
    copos(img, t, 40)
    k = eob(t / 0.3); d = ImageDraw.Draw(img)
    d.polygon([(0, 270), (W, 230), (W, 400), (0, 440)], fill=(230, 40, 50), outline=INK, width=8)
    d.text((540, 335), "NUEVA SERIE", font=font(int(84 * k) + 1), fill=(255, 255, 255), anchor="mm", stroke_width=8, stroke_fill=INK)
    burst(img, "¡BRRR!", 330, 620, 120, t - 0.1, col=(170, 230, 255), ang=-8)
    return img, 2 * math.sin(T * 50)

@shot
def s02(t, D, T):    # la ruleta decide sola → HIELO
    stop = T > STARTS[RK] + tl(RK, 0.82)
    cam = Cam(540, 1000, lerp(1.0, 1.12, ease(t / D)))
    dr = D_(cam); escenario_ruleta(dr, t); ruleta(dr, 540, 1080, 300, ang_ruleta(T), t, glow_seg=SEG_HIELO if stop else None)
    f = tinta(dr)
    for x in (300, 780): add_cono(f, x, -50, 1700, 60, 520, (255, 236, 180), 0.3)
    if stop: add_glow(f, 540, 760, 260, (150, 220, 255), 0.5)
    img = acabado(f, T)
    if t < tl(RK, 0.35): burst(img, "¿?", 540, 1500, 130, t, col=(255, 222, 40), ang=-4)
    if stop:
        burst(img, "¡ERA DE HIELO!", 540, 1500, 100, t - tl(RK, 0.82), col=(170, 230, 255), ang=-5)
        copos(img, t, 30)
    return img, (2 * math.sin(T * 40) if not stop else 6 * math.exp(-(t - tl(RK, 0.82)) * 5))

@shot
def s03(t, D, T):    # portal en la nieve → Nico cae vestido con pieles
    u = t / D
    cam = Cam(540, 1050, lerp(1.0, 1.15, ease(u)))
    dr = D_(cam); nieve_bg(dr, t, hor=1100)
    o = 1 - ease((u - 0.65) / 0.3)
    portal(dr, 540, 900, 300, t, max(0.0, o) * min(1, u * 4))
    tt = t - 0.35 * D
    if tt > 0:
        land = clamp(tt / 0.45)
        sq = 1.0 if land < 1 else 1 - 0.18 * math.exp(-(tt - 0.45) * 8) * math.cos((tt - 0.45) * 20)
        nico(dr, 540, lerp(1050, 1780, land ** 2), 0.66, t, traje=PI, arms=(140, 140) if land < 1 else (30, 160), elbows=(0, 15),
             expr="shock" if tt < 0.9 else "happy", squash=sq, look=(0.3, -0.5))
        if land >= 1:   # nube de nieve al caer
            k = clamp((tt - 0.45) / 0.6)
            for j in range(6): dr.ell(540 + (j - 2.5) * 90 * (1 + k), 1780 - 20 * k, 60 * (1 - k) + 5, 40 * (1 - k) + 4, (255, 255, 255), nolin=True)
    f = tinta(dr); add_glow(f, *cam.p(540, 900), 380, (150, 120, 255), 0.45 * max(0, o)); img = acabado(f, T)
    copos(img, t, 30)
    if tt > 0.5: burst(img, "¡PIELES!", 540, 470, 110, tt - 0.5, col=(255, 222, 40), ang=-5)
    return img, (5 * math.exp(-(tt - 0.45) * 6) if tt > 0.45 else 0)

@shot
def s04(t, D, T):    # Nico: ¡brrr! se me congelan los mocos (primer plano, carámbano en la nariz)
    cam = Cam(540, 1080, 1.75)
    dr = D_(cam); nieve_bg(dr, t, hor=1000, trees=False)
    sh = math.sin(t * 40) * 6
    r = nico(dr, 540 + sh * 0.5, 1660, 0.62, t, traje=PI, arms=(40 + sh, 40 - sh), elbows=(110, 110), expr="nervous", mouth=boca(3, t), look=(0, 0.3))
    hx, hy = r["head"]
    if t > tl(3, 0.55):
        k = ease((t - tl(3, 0.55)) / 0.4)
        dr.poly([(hx - 16, hy + 70), (hx + 16, hy + 70), (hx, hy + 70 + 90 * k)], (200, 236, 252))
    f = tinta(dr); img = acabado(f, T)
    copos(img, t, 30, big=1.4)
    burst(img, "¡BRRR!", 780, 520, 130, t - 0.05, col=(170, 230, 255), ang=8)
    if t > tl(3, 0.6): burst(img, "¡MOCOSICLE!", 300, 1380, 70, t - tl(3, 0.6), col=(200, 240, 255), ang=-8)
    return img, 3

@shot
def s05(t, D, T):    # DATO REAL: hace 20.000 años, hielo ≈ 1/4 de la tierra firme
    cam = Cam(540, 1000, 1.0)
    dr = D_(cam, bg=(20, 30, 70))
    for k in range(30): dr.ell((k * 173) % 1100, 500 + (k * 211) % 1400, 4, 4, (240, 240, 255), nolin=True)
    R = 330; cx, cy = 540, 1150
    dr.ell(cx, cy, R, R, (60, 130, 210))
    for (dx, dy, rx, ry) in ((-120, -40, 140, 110), (130, 60, 120, 150), (-40, 190, 90, 70), (160, -150, 110, 70)):
        dr.ell(cx + dx, cy + dy, rx, ry, (110, 170, 90))
    k = ease((t - tl(4, 0.35)) / 0.8)
    ch = R * 0.95 * k
    if ch > 2: dr.chord(cx, cy - R * 0.08, R * 0.98, ch, 180, 360, (245, 250, 255))
    nico(dr, 860, 1720, 0.34, t, traje=PI, arms=(150, 30), elbows=(20, 0), expr="shock", look=(-1, -0.6))
    f = tinta(dr); img = acabado(f, T); d = ImageDraw.Draw(img)
    d.polygon([(0, 290), (W, 240), (W, 400), (0, 450)], fill=(255, 214, 10), outline=INK, width=8)
    d.text((540, 345), "DATO REAL", font=font(76), fill=INK, anchor="mm")
    if t > tl(4, 0.15):
        d.rounded_rectangle([170, 490, 910, 600], radius=26, fill=(255, 255, 255), outline=INK, width=6)
        d.text((540, 545), "HACE 20.000 AÑOS", font=font(58), fill=INK, anchor="mm")
    if t > tl(4, 0.55): burst(img, "≈ 1/4 CON HIELO", 540, 1460, 84, t - tl(4, 0.55), col=(170, 230, 255), ang=-4)
    return img, 0

@shot
def s06(t, D, T):    # la "montaña de nieve" se mueve: Doña Lana despierta
    u = t / D
    cam = Cam(600, 1150, lerp(1.0, 1.12, ease(u)))
    dr = D_(cam); nieve_bg(dr, t, hor=1000, trees=False)
    cueva_boca(dr, 260, 1200, 320, 340)
    ris = ease(u / 0.5)
    mamut(dr, 640, lerp(2050, 1800, ris), 0.62, t, mouth=boca(5, t), face=-1, expr="angry", look=(-0.6, 0.4), frozen=True, sleep=u < 0.15)
    dr.ell(640, 1820, 520, 90 * (1 - ris) + 10, (242, 246, 252))   # nieve que cae de encima
    nico(dr, 260, 1800, 0.42, t, traje=PI, arms=(150, 150), elbows=(10, 10), expr="shock", look=(1, -0.5), sweat=True)
    f = tinta(dr); img = acabado(f, T)
    copos(img, t, 25)
    if u > 0.2: burst(img, "¡¿QUIÉN?!", 760, 480, 120, t - 0.2 * D, col=(255, 160, 120), ang=7)
    return img, 6 * math.exp(-t * 3)

@shot
def s07(t, D, T):    # Nico: ¡un mamut! ¡perdón, perdón!
    cam = Cam(540, 1080, 1.75)
    dr = D_(cam); nieve_bg(dr, t, hor=1000, trees=False)
    shake = math.sin(t * 14) * 25
    nico(dr, 540, 1660, 0.62, t, traje=PI, arms=(70 + shake, 70 - shake), elbows=(70, 70), expr="nervous", mouth=boca(6, t), look=(0.5, -0.3), sweat=True)
    f = tinta(dr); img = acabado(f, T)
    copos(img, t, 20)
    burst(img, "¡PERDÓN!", 540, 500, 120, t - 0.3, col=(255, 222, 40), ang=-6)
    return img, 0

@shot
def s08(t, D, T):    # Es Doña Lana, abuela mamut gruñona con la trompa congelada
    cam = Cam(560, 1150, 1.1)
    dr = D_(cam); nieve_bg(dr, t, hor=1050)
    mamut(dr, 640, 1880, 0.66, t, face=-1, expr="grumpy", look=(-0.5, 0.3), frozen=True)
    nico(dr, 200, 1880, 0.42, t, traje=PI, arms=(20, 60), elbows=(10, 80), expr="worried", look=(1, -0.4))
    f = tinta(dr); img = acabado(f, T)
    copos(img, t, 25)
    tarjeta_nombre(img, t - 0.1, "DOÑA LANA", "abuela mamut · gruñona")
    if t > tl(7, 0.7): burst(img, "¡CONGELADA!", 380, 1450, 74, t - tl(7, 0.7), col=(170, 230, 255), ang=-8)
    return img, 0

@shot
def s09(t, D, T):    # Doña Lana propone el trato (primer plano)
    cam = Cam(600, 1250, 1.45)
    dr = D_(cam); nieve_bg(dr, t, hor=950, trees=False)
    cueva_boca(dr, 180, 1300, 360, 400)
    mamut(dr, 640, 2100, 0.72, t, mouth=boca(8, t), face=-1, expr="grumpy", look=(-0.7, 0.4), frozen=True, up=1.0 if t > tl(8, 0.55) else 0.0)
    f = tinta(dr); img = acabado(f, T)
    copos(img, t, 25)
    if t > tl(8, 0.1): burst(img, "🔥?" if False else "¿FUEGO?", 330, 520, 100, t - tl(8, 0.1), col=(255, 160, 60), ang=-6)
    if t > tl(8, 0.6): burst(img, "= CUEVA", 330, 660, 80, t - tl(8, 0.6), col=(255, 255, 255), ang=-6)
    return img, 0

@shot
def s10(t, D, T):    # Nico: ¡hecho! … ¿cómo se hace fuego sin encendedor?
    cam = Cam(520, 1150, 1.4)
    dr = D_(cam); nieve_bg(dr, t, hor=1050, trees=False)
    conf = t > tl(9, 0.35)
    nico(dr, 520, 1800, 0.66, t, traje=PI, arms=(25, 165) if not conf else (20, 120), elbows=(0, 10) if not conf else (0, 90), expr="smug" if not conf else "worried", mouth=boca(9, t), look=(0.2, -0.2) if not conf else (-0.5, -0.6))
    f = tinta(dr); img = acabado(f, T)
    copos(img, t, 20)
    if not conf: burst(img, "¡HECHO!", 540, 480, 120, t - 0.1, col=(110, 230, 110), ang=-6)
    else:
        burst(img, "¿?", 820, 560, 150, t - tl(9, 0.35), col=(255, 222, 40), ang=8)
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([110, 600, 470, 720], radius=24, fill=(255, 255, 255), outline=INK, width=6)
        d.text((290, 660), "SIN ENCENDEDOR", font=font(38), fill=INK, anchor="mm")
        d.line([(120, 710), (460, 610)], fill=(230, 40, 50), width=14)
    return img, 0

@shot
def s11(t, D, T):    # frota los palitos… 10 minutos… ¡chispa!
    spark = tl(10, 0.78)
    cam = Cam(540, 1500, lerp(1.4, 1.7, ease(t / D)))
    dr = D_(cam); nieve_bg(dr, t, hor=1000, trees=False)
    fogata(dr, 700, 1880, 0.7, t, k=0.0 if t < spark else 0.35 * ease((t - spark) / 0.4))
    rub = math.sin(t * 30) * (0 if t > spark else 1)
    r = nico(dr, 400, 1900, 0.6, t, traje=PI, arms=(25 + 8 * rub, 25 - 8 * rub), elbows=(-85, -85), expr="angry" if t < spark else "shock", look=(0.6, 0.8), sweat=t > tl(10, 0.4))
    hL, hR = r["hands"]
    cxh = (hL[0] + hR[0]) / 2
    dr.rrect(cxh - 110, hL[1] + 150, cxh + 110, hL[1] + 185, 10, (130, 86, 50))
    palito(dr, cxh + 10 * rub, hL[1] - 40, 190, 90)
    mamut(dr, 1020, 1980, 0.4, t, face=-1, expr="grumpy", look=(-0.5, 0.5), frozen=True)
    f = tinta(dr)
    if t > spark: add_glow(f, *cam.p(700, 1840), 200, (255, 180, 60), 0.7)
    img = acabado(f, T); d = ImageDraw.Draw(img)
    if tl(10, 0.3) < t < spark:   # reloj de 10 minutos
        m = int(10 * clamp((t - tl(10, 0.3)) / (spark - tl(10, 0.3))))
        d.ellipse([780, 420, 1000, 640], fill=(255, 255, 255), outline=INK, width=8)
        a = (t - tl(10, 0.3)) * 25
        d.line([(890, 530), (890 + 80 * math.sin(a), 530 - 80 * math.cos(a))], fill=INK, width=10)
        d.text((890, 700), f"{m} MIN", font=font(60), fill=(255, 255, 255), anchor="mm", stroke_width=7, stroke_fill=INK)
    if t > spark: burst(img, "¡CHISPA!", 540, 560, 130, t - spark, col=(255, 200, 60), ang=-6)
    else: burst(img, "RAS RAS", 300, 620, 80, t - 0.1, col=(255, 255, 255), ang=-10)
    return img, (5 * math.exp(-(t - spark) * 6) if t > spark else 0)

@shot
def s12(t, D, T):    # ¡fuego! ¡soy un genio de las cavernas! (anochece)
    u = t / D
    cam = Cam(540, 1250, 1.2)
    dr = D_(cam); nieve_bg(dr, t, hor=1000, night=True, trees=False)
    cueva_boca(dr, 540, 1350, 520, 480, col=(70, 76, 104))
    fogata(dr, 540, 1820, 1.0, t, k=0.9)
    nico(dr, 300, 1860, 0.56, t, traje=PI, arms=(160, 165), elbows=(10, 10), expr="happy", mouth=boca(11, t), look=(0.6, -0.3), squash=1 + 0.05 * math.sin(t * 14))
    mamut(dr, 860, 1900, 0.48, t, face=-1, expr="happy", look=(-0.6, 0.3), frozen=False)
    f = tinta(dr); add_glow(f, *cam.p(540, 1700), 520, (255, 160, 60), 0.55); img = acabado(f, T)
    burst(img, "¡FUEGO!", 540, 520, 140, t - 0.05, col=(255, 160, 40), ang=-6)
    return img, 0

@shot
def s13(t, D, T):    # en la oscuridad… dos ojos amarillos
    u = t / D
    cam = Cam(540, 1100, lerp(1.0, 1.25, ease(u)))
    dr = D_(cam, bg=(8, 10, 22))
    for k in range(8): pino(dr, -100 + k * 180, 1500 + (k % 2) * 60, 0.7, night=True)
    on = t > tl(12, 0.6)
    if on: ojos_oscuridad(dr, 560, 1180, 0.8, t, ease((t - tl(12, 0.6)) / 0.3))
    f = tinta(dr); f = oscuro(f, 0.55)
    if on: add_glow(f, *cam.p(560, 1180), 220, (255, 220, 60), 0.4)
    img = acabado(f, T)
    copos(img, t, 15)
    return img, 0

@shot
def s14(t, D, T):    # ¡un tigre dientes de sable! (sale de la oscuridad)
    u = t / D
    cam = Cam(540, 1100, lerp(1.0, 1.06, ease(u)))
    dr = D_(cam); nieve_bg(dr, t, hor=1000, night=True, trees=False)
    for k in range(4): pino(dr, -100 + k * 400, 1150, 0.8, night=True)
    tigre(dr, lerp(1150, 720, ease(u / 0.6)), 1720, 0.62, t, mouth=0.15, face=-1, look=(-0.8, 0.3), step=t * 1.4 if u < 0.6 else 0)
    fogata(dr, 300, 1900, 0.6, t, 0.8)
    f = tinta(dr); add_glow(f, *cam.p(300, 1800), 360, (255, 160, 60), 0.5); img = acabado(f, T)
    copos(img, t, 20)
    tarjeta_nombre(img, t - 0.15, "SMILODON", "tigre dientes de sable")
    return img, 0

@shot
def s15(t, D, T):    # tigre: mmm… cena para dos (primer plano)
    cam = Cam(540, 1050, 1.0)
    dr = D_(cam); nieve_bg(dr, t, hor=1300, night=True, trees=False)
    tigre_cabeza(dr, 540, 1120, 1.35, t, mouth=boca(14, t) * 0.9, face=-1, look=(-0.4, 0.2) if t < D * 0.5 else (0.4, 0.2), expr="smug")
    f = tinta(dr); add_glow(f, 200, 1900, 500, (255, 150, 60), 0.35); img = acabado(f, T)
    copos(img, t, 15)
    if t > tl(14, 0.7): burst(img, "¿CENA?", 540, 520, 120, t - tl(14, 0.7), col=(255, 120, 80), ang=-6)
    return img, 1 + 2 * boca(14, t)

@shot
def s16(t, D, T):    # DATO REAL: colmillos de 28 cm, mordida más débil que la de un león
    cam = Cam(540, 1000, 1.0)
    dr = D_(cam, bg=(40, 30, 60))
    for k in range(18):
        a = k * math.pi / 9 + t * 0.3
        dr.poly([(540, 1150), (540 + math.cos(a) * 2000, 1150 + math.sin(a) * 2000), (540 + math.cos(a + 0.17) * 2000, 1150 + math.sin(a + 0.17) * 2000)], (56, 42, 80))
    tigre_cabeza(dr, 540, 1050, 1.15, t, mouth=0.25, face=-1, look=(0, 0.4), expr="smug")
    f = tinta(dr); img = acabado(f, T); d = ImageDraw.Draw(img)
    d.polygon([(0, 290), (W, 240), (W, 400), (0, 450)], fill=(255, 214, 10), outline=INK, width=8)
    d.text((540, 345), "DATO REAL", font=font(76), fill=INK, anchor="mm")
    if t > tl(15, 0.12):   # regla junto al colmillo
        X0, Y0 = 760, 1180; X1, Y1 = 760, 1390
        d.line([(X0, Y0), (X1, Y1)], fill=INK, width=18); d.line([(X0, Y0), (X1, Y1)], fill=(255, 222, 40), width=10)
        for k in range(5): d.line([(X0 - 18, Y0 + k * 52), (X0 + 18, Y0 + k * 52)], fill=INK, width=6)
        d.text((900, 1290), "28 cm", font=font(64), fill=(255, 255, 255), anchor="mm", stroke_width=8, stroke_fill=INK)
    if t > tl(15, 0.45):
        d.rounded_rectangle([90, 1480, 990, 1580], radius=26, fill=(255, 255, 255), outline=INK, width=6)
        d.text((540, 1530), "MORDIDA < LEÓN 🦁" if False else "MORDIDA: MENOS QUE UN LEÓN", font=font(48), fill=INK, anchor="mm")
    if t > tl(15, 0.75): burst(img, "¡COMO CUCHILLOS!", 540, 560, 80, t - tl(15, 0.75), col=(255, 120, 80), ang=-5)
    return img, 0

@shot
def s17(t, D, T):    # REGLA: le tiene miedo al fuego
    cam = Cam(540, 1150, 1.15)
    dr = D_(cam); nieve_bg(dr, t, hor=1000, night=True, trees=False)
    back = 0.5 + 0.5 * math.sin(t * 2.2)
    tigre(dr, 880 + 40 * back, 1700, 0.5, t, mouth=0.4 * back, face=-1, look=(-0.8, 0), expr="angry")
    fogata(dr, 560, 1850, 0.85, t, 0.9)
    nico(dr, 230, 1880, 0.45, t, traje=PI, arms=(60, 60), elbows=(60, 60), expr="worried", look=(1, 0), sweat=True)
    f = tinta(dr); add_glow(f, *cam.p(560, 1750), 420, (255, 160, 60), 0.55); img = acabado(f, T); d = ImageDraw.Draw(img)
    d.polygon([(0, 280), (W, 240), (W, 470), (0, 510)], fill=(255, 140, 40), outline=INK, width=8)
    d.text((540, 330), "REGLA DEL TIGRE", font=font(64), fill=INK, anchor="mm")
    d.text((540, 420), "LE TIENE MIEDO AL FUEGO", font=font(48), fill=(255, 255, 255), anchor="mm", stroke_width=6, stroke_fill=INK)
    copos(img, t, 15)
    return img, 0

@shot
def s18(t, D, T):    # tormenta de nieve: el fuego se achica (medidor)
    u = t / D
    cam = Cam(540, 1250, 1.25)
    dr = D_(cam); nieve_bg(dr, t, hor=1000, night=True, trees=False)
    cueva_boca(dr, 540, 1350, 520, 480, col=(70, 76, 104))
    fk = lerp(0.9, 0.25, ease(u))
    fogata(dr, 540, 1820, 1.0, t, fk)
    nico(dr, 280, 1860, 0.5, t, traje=PI, arms=(40 + 6 * math.sin(t * 30), 40 - 6 * math.sin(t * 30)), elbows=(110, 110), expr="worried", look=(0.6, 0.4), sweat=True)
    mamut(dr, 870, 1900, 0.46, t, face=-1, expr="shock", look=(-0.6, 0.4), frozen=True)
    if u > 0.3: ojos_oscuridad(dr, 1000, 1200, 0.4, t)
    f = tinta(dr); add_glow(f, *cam.p(540, 1700), 520 * fk, (255, 160, 60), 0.5 * fk); img = acabado(f, T)
    copos(img, t, 90, k=1.5, wind=0.9, big=1.2)
    d = ImageDraw.Draw(img)   # medidor del fuego
    d.rounded_rectangle([880, 520, 960, 1000], radius=20, fill=(40, 30, 40), outline=INK, width=6)
    hh = 460 * fk
    d.rounded_rectangle([888, 994 - hh, 952, 994], radius=16, fill=(255, 150, 40) if fk > 0.4 else (230, 40, 50))
    d.text((920, 470), "🔥" if False else "FUEGO", font=font(40), fill=(255, 255, 255), anchor="mm", stroke_width=6, stroke_fill=INK)
    burst(img, "¡FIUUU!", 330, 560, 100, t - 0.2, col=(200, 230, 255), ang=-8)
    return img, 3

@shot
def s19(t, D, T):    # Doña Lana: ¡se nos acabaron los palitos!
    cam = Cam(620, 1300, 1.45)
    dr = D_(cam); nieve_bg(dr, t, hor=950, night=True, trees=False)
    fogata(dr, 300, 1900, 0.8, t, 0.15)
    mamut(dr, 680, 2100, 0.72, t, mouth=boca(18, t), face=-1, expr="shock", look=(-0.7, 0.4), frozen=True)
    f = tinta(dr); add_glow(f, *cam.p(300, 1850), 160, (255, 150, 60), 0.4); img = acabado(f, T)
    copos(img, t, 70, k=1.5, wind=0.8)
    burst(img, "¡SIN PALITOS!", 540, 520, 100, t - 0.3, col=(255, 120, 80), ang=-6)
    return img, 4

@shot
def s20(t, D, T):    # dilema: 1 cueva oscura · 2 lago congelado
    cam = Cam(540, 960, 1.0)
    dr = D_(cam, bg=(176, 216, 240))
    dr.poly([(-100, -100), (540, -100), (540, 2600), (-100, 2600)], (30, 26, 44))
    dr.poly([(470, -100), (610, -100), (610, 2600), (470, 2600)], (20, 16, 26))
    o1 = t > tl(19, 0.2); o2 = t > tl(19, 0.6)
    if o1:
        k = eob((t - tl(19, 0.2)) / 0.3)
        cueva_boca(dr, 270, 1200, 200 * k + 1, 260 * k + 1, col=(90, 96, 124))
        ojos_oscuridad(dr, 270, 1090, 0.18 * k + 0.01, t + 1)
    if o2:
        k = eob((t - tl(19, 0.6)) / 0.3)
        dr.ell(810, 1120, 220 * k + 1, 90 * k + 1, (200, 236, 252))
        dr.line([(720, 1100), (780, 1140), (760, 1170), (850, 1130)], (90, 140, 190), 6)
    nico(dr, 540, 1560, 0.5, t, traje=PI, arms=(70, 70), elbows=(60, 60), expr="worried", look=(-0.8 if t < tl(19, 0.55) else 0.8, -0.3))
    f = tinta(dr); img = acabado(f, T); d = ImageDraw.Draw(img)
    d.text((540, 300), "¿QUÉ HACE NICO?", font=font(92), fill=(255, 222, 40), anchor="mm", stroke_width=12, stroke_fill=INK)
    for ok, x, n, a, b in ((o1, 270, "1", "LA CUEVA", "OSCURA"), (o2, 810, "2", "EL LAGO", "CONGELADO")):
        if not ok: continue
        d.ellipse([x - 90, 440, x + 90, 620], fill=(255, 255, 255), outline=INK, width=10)
        d.text((x, 532), n, font=font(130), fill=INK, anchor="mm")
        d.text((x, 700), a, font=font(50), fill=(255, 255, 255), anchor="mm", stroke_width=7, stroke_fill=INK)
        d.text((x, 760), b, font=font(44), fill=(255, 255, 255), anchor="mm", stroke_width=7, stroke_fill=INK)
    if o1: d.text((270, 1420), "ruidos raros…", font=font(40), fill=(200, 200, 230), anchor="mm", stroke_width=5, stroke_fill=INK)
    if o2: d.text((810, 1420), "el hielo cruje…", font=font(40), fill=(255, 255, 255), anchor="mm", stroke_width=5, stroke_fill=INK)
    copos(img, t, 30, wind=0.5)
    return img, 0

@shot
def s21(t, D, T):    # comenta 1 o 2 + portal + capítulo 2 mañana
    cam = Cam(540, 1100, 1.15)
    dr = D_(cam, bg=(40, 110, 200))
    for k in range(18):
        a = k * math.pi / 9 - t * 0.6
        dr.poly([(540, 1100), (540 + math.cos(a) * 2000, 1100 + math.sin(a) * 2000), (540 + math.cos(a + 0.17) * 2000, 1100 + math.sin(a + 0.17) * 2000)], (70, 140, 220))
    o = ease((t - D + 1.5) / 0.6)
    portal(dr, 540, 1150, 340, t, o)
    if t < D - 0.5: nico(dr, 540, 1900, 0.72, t, traje=PI, arms=(100, 170), elbows=(-20, 0), expr="happy", mouth=boca(20, t))
    f = tinta(dr); add_glow(f, *cam.p(540, 1150), 450, (150, 120, 255), 0.5 * o); img = acabado(f, T)
    d = ImageDraw.Draw(img)
    for k, (x, n) in enumerate(((330, "1"), (750, "2"))):
        p = 1 + 0.08 * math.sin(t * 8 + k * 3); r = 95 * p
        d.ellipse([x - r, 420 - r, x + r, 420 + r], fill=(255, 214, 10), outline=INK, width=10)
        d.text((x, 420), n, font=font(130 * p), fill=INK, anchor="mm")
    d.text((540, 610), "COMENTA", font=font(84), fill=(255, 255, 255), anchor="mm", stroke_width=10, stroke_fill=INK)
    if t > D - 2.4:
        d.rounded_rectangle([150, 690, 930, 850], radius=36, fill=(255, 214, 10), outline=INK, width=8)
        d.text((540, 745), "CAPÍTULO 2", font=font(66), fill=INK, anchor="mm")
        d.text((540, 810), "MAÑANA · 6 P. M.", font=font(44), fill=(200, 40, 50), anchor="mm")
    copos(img, t, 30)
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
    rng = np.random.default_rng(21)
    def add(s, sig, g=1.0):
        i0 = int(s * sr); i1 = min(n, i0 + len(sig))
        if 0 <= i0 < n: out[i0:i1] += g * sig[:i1 - i0]
    def seg(d): return np.arange(int(max(0.01, d) * sr)) / sr
    hz = lambda m: 440 * 2 ** ((m - 69) / 12)
    noise = rng.standard_normal(n)
    bp = lambda lo, hi: sosfilt(butter(2, [lo, hi], btype="band", fs=sr, output="sos"), noise)
    wh = bp(400, 3500); low = sosfilt(butter(2, 160, btype="low", fs=sr, output="sos"), noise)
    wind_n = bp(250, 1400)
    S_ = STARTS
    def musica(s, tend, g=1.0, dark=False):   # campanitas de hielo + bajo + tambor suave
        e = 0.18
        prog = [[62, 66, 69, 74], [59, 62, 66, 71], [55, 59, 62, 67], [57, 61, 64, 69]] if not dark else [[50, 53, 57, 62], [48, 51, 55, 60]]
        k = 0
        while s < tend:
            ch = prog[(k // 16) % len(prog)]; m = ch[[0, 2, 1, 3][k % 4]] + 12
            x = seg(e * 2)
            add(s, g * 0.04 * (np.sin(2 * np.pi * hz(m) * x) + 0.3 * np.sin(2 * np.pi * hz(m) * 2.76 * x)) * np.exp(-x * 7))
            if k % 8 == 0:
                xb = seg(e * 8); add(s, g * 0.08 * np.sin(2 * np.pi * hz(ch[0] - 24) * xb) * np.exp(-xb * 0.6))
            if k % 4 == 0:
                xt = seg(0.25); add(s, g * 0.13 * np.exp(-xt * 16) * np.sin(2 * np.pi * (80 + 50 * np.exp(-xt * 25)) * xt))
            if k % 2 == 1: add(s, g * 0.018 * rng.standard_normal(len(x)) * np.exp(-x * 60))
            k += 1; s += e
    def viento(s, tend, g=0.06):
        x = seg(tend - s); i0 = int(s * sr)
        add(s, g * wind_n[i0:i0 + len(x)] * (0.6 + 0.4 * np.sin(2 * np.pi * 0.3 * x)) * np.clip(x / 0.8, 0, 1))
    def dron(s, tend, g=0.08):
        xd = seg(tend - s); add(s, g * (np.sin(2 * np.pi * 41 * xd) + 0.5 * np.sin(2 * np.pi * 61.7 * xd)) * np.clip(xd / 1.5, 0, 1))
    def golpe(s, g=0.5):
        x = seg(0.6); add(s, g * (np.sin(2 * np.pi * (40 + 30 * np.exp(-x * 12)) * x) * np.exp(-x * 6) + 0.4 * low[:len(x)] * np.exp(-x * 8)))
    def rugido(s, d=1.4, g=0.45):
        x = seg(d)
        f0 = 90 + 50 * np.sin(np.pi * x / d)
        tone = np.sign(np.sin(2 * np.pi * np.cumsum(f0) / sr)) * 0.35 + np.sin(2 * np.pi * np.cumsum(f0 * 2) / sr) * 0.3
        env = np.sin(np.pi * np.clip(x / d, 0, 1)) ** 0.6
        add(s, g * (tone + bp(100, 1100)[:len(x)] * 0.8) * env)
    def trompeta(s, g=0.25):   # barrito de mamut
        x = seg(1.0); f0 = 300 + 200 * np.sin(np.pi * x)
        add(s, g * np.sign(np.sin(2 * np.pi * np.cumsum(f0) / sr)) * np.sin(np.pi * x) * 0.5)
    def fuego(s, tend, g=0.05):
        x = seg(tend - s); i0 = int(s * sr)
        cr = np.zeros(len(x))
        for j in rng.integers(0, len(x), int((tend - s) * 14)):
            m = min(len(x) - j, 300); cr[j:j + m] += rng.standard_normal(m) * np.exp(-np.arange(m) / 40)
        add(s, g * (0.5 * low[i0:i0 + len(x)] + cr))
    # gancho + ruleta
    musica(S_[0], S_[1], 0.6, dark=True); viento(S_[0], S_[1], 0.08)
    t0 = S_[RK] + tl(RK, 0.35); t1 = S_[RK] + tl(RK, 0.82)
    xr = seg(t1 - t0); add(t0, 0.06 * bp(150, 600)[:len(xr)] * (0.6 + 0.4 * np.sin(2 * np.pi * 18 * xr)))
    prev = int(ang_ruleta(t0) / 22.5)
    for k in range(int((t1 - t0) * FPS) + 2):
        T = t0 + k / FPS; a = ang_ruleta(T)
        if int(a / 22.5) != prev:
            prev = int(a / 22.5); xc = seg(0.03); add(T, 0.25 * np.exp(-xc * 200) * np.sin(2 * np.pi * 2500 * xc))
    x = seg(1.2); add(t1, 0.35 * np.exp(-x * 2.5) * (np.sin(2 * np.pi * 392 * x) + np.sin(2 * np.pi * 494 * x) + np.sin(2 * np.pi * 587 * x)) / 3)
    dron(S_[1], S_[2], 0.06)
    # llegada, frío, mamut
    xp = seg(1.6); add(S_[2] + DURS[2] * 0.2, 0.15 * wh[:len(xp)] * np.sin(np.pi * xp / 1.6) * (0.5 + 0.5 * np.sin(2 * np.pi * 9 * xp)))
    golpe(S_[2] + DURS[2] * 0.35 + 0.45, 0.3)
    musica(S_[2], S_[12], 0.75); viento(S_[2], S_[12], 0.04)
    trompeta(S_[5] + 0.1, 0.22); golpe(S_[5] + 0.2, 0.4)
    for k in range(int(DURS[10] * 0.78 / 0.12)):
        xs = seg(0.08); add(S_[10] + 0.1 + k * 0.12, 0.05 * wh[:len(xs)] * np.exp(-xs * 30))   # ras ras
    xs = seg(0.4); add(S_[10] + tl(10, 0.78), 0.3 * wh[:len(xs)] * np.exp(-xs * 12))   # chispa
    fuego(S_[10] + tl(10, 0.78), S_[18] + DURS[18], 0.05)
    # tigre
    dron(S_[12], S_[19], 0.09)
    musica(S_[13], S_[17], 0.35, dark=True)
    rugido(S_[13] + 0.1, 1.4, 0.45)
    x = seg(DURS[14]); add(S_[14], 0.04 * bp(60, 200)[:len(x)] * (0.5 + 0.5 * np.sin(2 * np.pi * 25 * x)))   # ronroneo
    # tormenta
    viento(S_[17], S_[19] + DURS[19], 0.16)
    musica(S_[17], S_[19], 0.7, dark=True)
    # dilema + cierre
    for k in range(int(DURS[19] / 0.5)):
        xh = seg(0.2); add(S_[19] + k * 0.5, 0.18 * np.exp(-xh * 14) * np.sin(2 * np.pi * 60 * xh))
    musica(S_[20], TOTAL, 0.7)
    x = seg(1.6); add(TOTAL - 1.6, 0.2 * wh[:len(x)] * np.sin(np.pi * x / 1.6) * (0.5 + 0.5 * np.sin(2 * np.pi * 9 * x)))
    for k in range(1, len(S_) - 1):
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
    if os.environ.get("RANGE"):
        a, b = [int(v) for v in os.environ["RANGE"].split(",")]
        p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                              "-c:v", "libx264", "-preset", "veryfast", "-crf", "24", "-tune", "animation", "-pix_fmt", "yuv420p", OUT], stdin=subprocess.PIPE)
        for k in range(a, b):
            p.stdin.write(frame(k / FPS).convert("RGB").tobytes())
            if k % 300 == 0: print(f"{k}/{b}", flush=True)
        p.stdin.close(); p.wait(); print("tramo listo", OUT); sys.exit()
    print("NFRAMES", int(TOTAL * FPS))
