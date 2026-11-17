#!/usr/bin/env python3
"""¿Qué pasaría si abres un DELIVERY en la Edad Media? — 08:00 del 2026-11-17 (estilo vector + cómic)."""
import math, os, sys, subprocess
import numpy as np
from PIL import Image, ImageDraw
from scipy.io import wavfile
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "..", "motor"))
from vc import *
import vc as _vc
Lienzo = _vc.D

FPS = 30
OUT = sys.argv[1] if len(sys.argv) > 1 else "video_raw.mp4"
VOZ_DIR = os.path.join(HERE, "voz")
VOZ_F = sorted(f for f in os.listdir(VOZ_DIR) if f.endswith(".wav"))
VOZ = [wavfile.read(f"{VOZ_DIR}/{f}")[1].astype(np.float32) / 32768 for f in VOZ_F]
SR = 44100; LEAD = 0.1
DURS = [len(v) / SR + LEAD + 0.3 for v in VOZ]
DURS[0] += 0.3; DURS[1] += 0.4; DURS[7] += 0.5; DURS[9] += 0.8; DURS[10] += 1.2
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
    [("¿Qué pasaría si", []), ("abres un DELIVERY…", ["DELIVERY…"]), ("en la Edad Media?", ["Media?"])],
    [("Nico cruza el portal", ["portal"]), ("y aparece en un castillo", ["castillo"]), ("del año 1200", ["1200"]), ("con su moto y su mochila", ["moto"])],
    [("¿Qué es esa bestia", ["bestia"]), ("de metal que ruge?", []), ("¡Guardias!", ["¡Guardias!"])],
    [("¡Tranquilo, majestad!", []), ("Pizza a domicilio", ["Pizza"]), ("en 30 minutos…", ["30"]), ("o es gratis", ["gratis"])],
    [("En la Edad Media", []), ("un mensaje a caballo", ["caballo"]), ("podía tardar DÍAS", ["DÍAS"])],
    [("Nico entrega la pizza", []), ("en 10 minutos", ["10"]), ("El rey no lo puede creer", [])],
    [("¡Quiero 100 pizzas!", ["100"]), ("¡Para todo el reino!", ["reino!"])],
    [("Pero hay un problema:", ["problema:"]), ("no hay gasolineras…", ["gasolineras…"]), ("y la moto se queda seca", ["seca"])],
    [("Bueno…", []), ("¿alguien tiene un caballo?", ["caballo?"])],
    [("Y así nació el primer", []), ("delivery… a caballo", ["caballo"]), ("¿A qué época llevo a Nico?", ["época"]), ("¡Coméntalo!", ["¡Coméntalo!"])],
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
def cielo(dr, t, top=(90, 150, 220), bot=(190, 220, 240)):
    for k in range(6):
        u = k / 5; c = tuple(int(lerp(top[i], bot[i], u)) for i in range(3))
        dr.rrect(-500, -900 + k * 380, 1600, -900 + (k + 1) * 380 + 2, 0, c)
    for k, (x, y, s) in enumerate(((150, 250, 1.0), (800, 160, 1.3), (520, 420, 0.8))):
        xx = (x + t * 12 * s) % 1500 - 200
        for (a, b, r) in ((-60, 10, 60), (0, -20, 80), (70, 10, 60), (20, 25, 70)):
            dr.ell(xx + a * s, y + b * s, r * s, r * 0.7 * s, (255, 255, 255), nolin=True)

def colinas(dr, gy=1180):
    dr.poly([(-500, gy), (-100, gy - 220), (300, gy - 90), (700, gy - 260), (1100, gy - 120), (1600, gy - 200), (1600, gy + 100), (-500, gy + 100)], (110, 160, 90))
    dr.poly([(-500, gy + 40), (200, gy - 80), (600, gy + 10), (1000, gy - 70), (1600, gy + 20), (1600, gy + 200), (-500, gy + 200)], (90, 140, 74))

def castillo(dr, t, cx=540, base=1250, s=1.0):
    S = lambda v: v * s
    stone, stone_d, roof = (176, 168, 158), (140, 132, 124), (170, 50, 50)
    dr.rrect(cx - S(420), base - S(520), cx + S(420), base, 6, stone, shade=True)
    for k in range(-8, 9):
        if k % 2 == 0: dr.rrect(cx + S(k * 50) - S(22), base - S(570), cx + S(k * 50) + S(22), base - S(510), 2, stone)
    for sx in (-1, 1):
        tx = cx + sx * S(420)
        dr.rrect(tx - S(110), base - S(760), tx + S(110), base, 8, stone_d, shade=True)
        dr.poly([(tx - S(140), base - S(760)), (tx, base - S(980)), (tx + S(140), base - S(760))], roof)
        dr.line([(tx, base - S(980)), (tx, base - S(1060))], (60, 50, 40), S(8))
        dr.poly([(tx, base - S(1060)), (tx + S(80) + S(10) * math.sin(t * 5), base - S(1035)), (tx, base - S(1010))], TURQ)
        dr.rrect(tx - S(25), base - S(620), tx + S(25), base - S(540), S(25), (50, 40, 50))
    dr.rrect(cx - S(150), base - S(380), cx + S(150), base, S(150), (70, 46, 34))
    for k in range(5): dr.line([(cx - S(120) + k * S(60), base - S(330)), (cx - S(120) + k * S(60), base)], (50, 34, 26), S(8))
    for sx in (-260, 260): dr.rrect(cx + S(sx) - S(30), base - S(420), cx + S(sx) + S(30), base - S(320), S(30), (50, 40, 50))

def patio(dr, t, gy=1250):
    cielo(dr, t); colinas(dr, gy - 80); castillo(dr, t, 540, gy, 1.0)
    dr.rrect(-500, gy, 1600, 2600, 0, (196, 176, 140))
    for k in range(10):
        yy = gy + 30 + k * k * 10 + k * 22
        dr.line([(-500, yy), (1600, yy)], (176, 156, 122), 4)
    for k in range(-6, 8):
        dr.line([(540 + k * 120, gy), (540 + k * 420, 2600)], (176, 156, 122), 4)

def sala_trono(dr, t):
    dr.rrect(-500, -900, 1600, 2600, 0, (120, 100, 110))
    for k in range(-2, 9): dr.rrect(k * 160 - 70, -900, k * 160 + 70, 1250, 10, (134, 112, 124))
    for x in (160, 920):
        dr.rrect(x - 60, 300, x + 60, 900, 10, (170, 40, 50))
        dr.ell(x, 300, 60, 30, (230, 190, 60))
        dr.poly([(x - 60, 860), (x + 60, 860), (x, 930)], (230, 190, 60))
    dr.rrect(-500, 1250, 1600, 2600, 0, (150, 120, 100))
    dr.poly([(380, 1250), (700, 1250), (1000, 2600), (80, 2600)], (180, 40, 50))
    dr.rrect(330, 520, 750, 1270, 60, (200, 160, 60), shade=True)
    dr.rrect(380, 600, 700, 1250, 40, (160, 40, 60))

# ------------------------------------------------------------ personajes y utilería
def rey(dr, x, y, s, t, mouth=0.0, expr="angry", arms=(25, 25), look=(0, 0), blink=None, comiendo=False):
    S = lambda v: v * s
    bob = S(5) * math.sin(t * 2.2)
    for sx in (-1, 1):
        dr.rrect(x + sx * S(50) - S(26), y - S(200), x + sx * S(50) + S(26), y - S(10), S(12), (90, 40, 110))
        dr.ell(x + sx * S(56), y - S(10), S(40), S(18), (60, 40, 30))
    dr.poly([(x - S(230), y - S(160)), (x - S(170), y - S(540) + bob), (x + S(170), y - S(540) + bob), (x + S(230), y - S(160))], (170, 36, 50))
    dr.ell(x, y - S(330) + bob, S(165), S(170), (110, 50, 140), shade=True)
    dr.rrect(x - S(165), y - S(290) + bob, x + S(165), y - S(250) + bob, S(10), (230, 190, 60))
    for k in range(9):
        dr.ell(x - S(200) + k * S(50), y - S(170), S(22), S(22), (250, 250, 250))
        dr.ell(x - S(200) + k * S(50), y - S(170), S(6), S(8), INK)
    for sx, a in ((-1, arms[0]), (1, arms[1])):
        shx, shy = x + sx * S(150), y - S(500) + bob
        ar = math.radians(a); hx, hy = shx + sx * math.sin(ar) * S(190), shy + math.cos(ar) * S(190)
        dr.line([(shx, shy), (hx, hy)], (110, 50, 140), S(66))
        dr.ell(hx, hy, S(34), S(34), (240, 196, 160))
    hx, hy = x, y - S(680) + bob
    dr.ell(hx, hy, S(165), S(160), (240, 196, 160), shade=True)
    dr.poly([(hx - S(150), hy + S(20)), (hx - S(100), hy + S(170)), (hx, hy + S(210)), (hx + S(100), hy + S(170)), (hx + S(150), hy + S(20)), (hx, hy + S(90))], (150, 90, 50))
    mo = clamp(mouth)
    dr.ell(hx, hy + S(110), S(50), S(10 + 38 * mo), (100, 24, 34))
    for sx in (-1, 1): dr.ell(hx + sx * S(55), hy + S(78), S(66), S(24), (170, 100, 56))
    dr.ell(hx, hy + S(35), S(36), S(38), (230, 160, 130))
    if blink is None: blink = (t % 3.4) < 0.12
    for sx in (-1, 1):
        ex, ey = hx + sx * S(62), hy - S(30)
        if blink: dr.rrect(ex - S(26), ey - S(4), ex + S(26), ey + S(6), S(3), INK)
        else:
            big = 1.25 if expr == "shock" else 1.0
            dr.ell(ex, ey, S(30) * big, S(34) * big, (255, 255, 255))
            dr.ell(ex + look[0] * S(9), ey + look[1] * S(9), S(14), S(17), INK)
        tilt = {"angry": 20, "happy": -8, "shock": -14}.get(expr, 0) * sx
        dr.line([(ex - S(36), ey - S(54) - S(tilt) * 0.5 * -1), (ex + S(36), ey - S(54) + S(tilt) * 0.5 * -1)], (130, 80, 46), S(14))
    dr.poly([(hx - S(140), hy - S(110)), (hx - S(150), hy - S(260)), (hx - S(80), hy - S(190)), (hx, hy - S(290)), (hx + S(80), hy - S(190)), (hx + S(150), hy - S(260)), (hx + S(140), hy - S(110))], (240, 200, 60))
    for k, c in enumerate(((220, 40, 60), TURQ, (220, 40, 60))): dr.ell(hx - S(70) + k * S(70), hy - S(150), S(16), S(16), c)
    if comiendo:
        dr.poly([(hx + S(30), hy + S(100)), (hx + S(190), hy + S(60)), (hx + S(170), hy + S(150))], (240, 190, 70))
    return (hx, hy)

def guardia(dr, x, y, s, t, face=1, expr="shock"):
    S = lambda v: v * s
    for sx in (-1, 1): dr.rrect(x + sx * S(35) - S(18), y - S(220), x + sx * S(35) + S(18), y - S(10), S(10), (110, 116, 126))
    dr.rrect(x - S(100), y - S(470), x + S(100), y - S(200), S(70), (160, 166, 176), shade=True)
    dr.rrect(x - S(30), y - S(460), x + S(30), y - S(210), S(10), (40, 70, 160))
    dr.line([(x + f(face) * S(130), y - S(700)), (x + f(face) * S(130), y - S(30))], (120, 80, 50), S(14)) if False else None
    sx = face
    dr.line([(x + sx * S(140), y - S(760)), (x + sx * S(140), y - S(20))], (120, 80, 50), S(14))
    dr.poly([(x + sx * S(140) - S(30), y - S(760)), (x + sx * S(140), y - S(860)), (x + sx * S(140) + S(30), y - S(760))], (200, 205, 215))
    dr.line([(x + sx * S(90), y - S(420)), (x + sx * S(140), y - S(330))], (160, 166, 176), S(40))
    hx, hy = x, y - S(620)
    dr.ell(hx, hy, S(150), S(150), (240, 196, 160), shade=True)
    big = 1.2 if expr == "shock" else 1.0
    for e in (-1, 1):
        dr.ell(hx + e * S(55), hy, S(28) * big, S(32) * big, (255, 255, 255)); dr.ell(hx + e * S(55) + sx * S(6), hy, S(12), S(15), INK)
    dr.ell(hx, hy + S(80), S(26), S(10 + 18 * (expr == "shock")), (100, 24, 34))
    dr.poly([(hx - S(170), hy - S(20)), (hx - S(150), hy - S(150)), (hx, hy - S(200)), (hx + S(150), hy - S(150)), (hx + S(170), hy - S(20)), (hx + S(110), hy - S(60)), (hx - S(110), hy - S(60))], (170, 176, 186))
    dr.rrect(hx - S(12), hy - S(200), hx + S(12), hy - S(30), S(4), (150, 156, 166))
def f(x): return x

def moto(dr, x, y, s, t, face=1, vibra=0.0, rueda=0.0):
    S = lambda v: v * s; fc = face
    vy = math.sin(t * 50) * S(3) * vibra
    for wx in (-150, 150):
        cx, cy = x + fc * S(wx), y - S(70)
        dr.ell(cx, cy, S(72), S(72), (30, 30, 36)); dr.ell(cx, cy, S(36), S(36), (190, 194, 204))
        a = rueda
        for k in range(3):
            aa = a + k * 2.09
            dr.line([(cx, cy), (cx + math.cos(aa) * S(34), cy + math.sin(aa) * S(34))], (120, 124, 134), S(6))
    dr.poly([(x - fc * S(170), y - S(110) + vy), (x - fc * S(60), y - S(210) + vy), (x + fc * S(110), y - S(210) + vy), (x + fc * S(170), y - S(110) + vy), (x + fc * S(80), y - S(90) + vy), (x - fc * S(90), y - S(90) + vy)], (230, 60, 60), shade=True)
    dr.rrect(x - fc * S(150) - S(10), y - S(250) + vy, x - fc * S(20) + S(10), y - S(210) + vy, S(14), (40, 40, 48))
    dr.line([(x + fc * S(110), y - S(210) + vy), (x + fc * S(150), y - S(320) + vy)], (60, 60, 70), S(14))
    dr.line([(x + fc * S(120), y - S(320) + vy), (x + fc * S(190), y - S(320) + vy)], (60, 60, 70), S(12))
    dr.ell(x + fc * S(175), y - S(200) + vy, S(26), S(22), (255, 240, 160))
    dr.line([(x - fc * S(170), y - S(120) + vy), (x - fc * S(230), y - S(105) + vy)], (150, 154, 164), S(16))
    caja = (x - fc * S(130), y - S(250) + vy)
    dr.rrect(caja[0] - S(80), caja[1] - S(150), caja[0] + S(80), caja[1], S(14), TURQ, shade=True)
    dr.text(caja[0], caja[1] - S(75), "NICO", S(36), (255, 255, 255), stroke=3)
    return (x - fc * S(50), y - S(220) + vy)

def caja_pizza(dr, x, y, s, abierta=False):
    S = lambda v: v * s
    dr.rrect(x - S(110), y - S(26), x + S(110), y + S(26), S(6), (230, 200, 150), shade=True)
    if abierta:
        dr.poly([(x - S(110), y - S(26)), (x + S(110), y - S(26)), (x + S(100), y - S(200)), (x - S(100), y - S(200))], (220, 188, 140))
        dr.ell(x, y - S(30), S(96), S(24), (240, 190, 70));
        for k in range(4): dr.ell(x - S(60) + k * S(40), y - S(32) + (k % 2) * S(6), S(13), S(7), (200, 50, 40))
    else:
        dr.text(x, y, "PIZZA", S(30), (200, 50, 40), stroke=0)

def caballo(dr, x, y, s, t, face=1, walk=0.0, col=(150, 96, 60)):
    S = lambda v: v * s; fc = face
    for k, (lx, dz) in enumerate(((-150, 0), (-110, 1), (120, 0), (160, 1))):
        ph = math.sin(walk + k * 1.7) * 0.4 * (1 if walk else 0)
        c = tuple(int(v * (0.8 if dz else 1)) for v in col)
        bx, by = x + fc * S(lx), y - S(300)
        dr.line([(bx, by), (bx + fc * S(30) * ph, y - S(150)), (bx + fc * S(10) * ph, y - S(10))], c, S(34))
        dr.rrect(bx + fc * S(10) * ph - S(22), y - S(26), bx + fc * S(10) * ph + S(22), y, S(6), (50, 36, 30))
    dr.ell(x, y - S(360), S(230), S(110), col, shade=True)
    dr.poly([(x + fc * S(160), y - S(410)), (x + fc * S(250), y - S(600)), (x + fc * S(320), y - S(570)), (x + fc * S(230), y - S(370))], col)
    hx, hy = x + fc * S(300), y - S(600)
    dr.ell(hx + fc * S(40), hy + S(20), S(90), S(55), col, shade=True)
    dr.ell(hx + fc * S(110), hy + S(35), S(40), S(36), tuple(int(v * 0.85) for v in col))
    dr.ell(hx + fc * S(20), hy - S(5), S(14), S(16), INK)
    dr.poly([(hx - fc * S(10), hy - S(40)), (hx + fc * S(10), hy - S(110)), (hx + fc * S(30), hy - S(40))], col)
    for k in range(6): dr.ell(x + fc * S(160 + k * 22), y - S(430 + k * 30), S(26), S(36), (60, 40, 30))
    dr.poly([(x - fc * S(220), y - S(380)), (x - fc * S(330), y - S(200) + S(20) * math.sin(t * 6)), (x - fc * S(260), y - S(190))], (60, 40, 30))
    return (x - fc * S(30), y - S(450))

def gorra(dr, info, s):
    hx, hy = info["head"]; S = lambda v: v * s
    dr.chord(hx, hy - S(110), S(185), S(120), 180, 360, TURQ)
    dr.rrect(hx - S(10), hy - S(130), hx + S(250), hy - S(100), S(14), TURQ_D)
    dr.ell(hx, hy - S(225), S(18), S(18), (255, 255, 255))

def mochila_pos(info, s):
    return info["head"][0] - s * 150, info["head"][1] + s * 330

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
    fz = font(size * k)
    lay = Image.new("RGBA", (int(fz.getlength(txt) + 140), int(size * k * 1.7)), (0, 0, 0, 0))
    ImageDraw.Draw(lay).text((70, 16), txt, font=fz, fill=col + (255,), stroke_width=int(15 * k), stroke_fill=INK)
    lay = lay.rotate(ang, resample=Image.BICUBIC, expand=True)
    img.paste(lay, (int(x - lay.width / 2), int(y - lay.height / 2)), lay)

def cartel(img, t, l1, l2, y=470):
    k = eob(t / 0.3); d = ImageDraw.Draw(img)
    d.rounded_rectangle([140, y, 940, y + 170], radius=30, fill=(236, 214, 160), outline=INK, width=8)
    d.text((540, y + 55), l1, font=font(70 * k + 1, F_SERIF), fill=(90, 50, 30), anchor="mm")
    d.text((540, y + 125), l2, font=font(48 * k + 1), fill=(200, 50, 40), anchor="mm")

def badge(img, T):
    d = ImageDraw.Draw(img); fz = font(36); txt = "¿QUÉ PASARÍA SI…?"
    d.rounded_rectangle([36, 110, 36 + fz.getlength(txt) + 44, 170], radius=16, fill=TURQ, outline=INK, width=5)
    d.text((58, 140), txt, font=fz, fill=(255, 255, 255), anchor="lm")

def reloj(img, x, y, txt, col=(255, 255, 255), t=1.0):
    k = eob(t / 0.25); d = ImageDraw.Draw(img); r = 120 * k
    if r < 2: return
    d.ellipse([x - r, y - r, x + r, y + r], fill=(250, 250, 250), outline=INK, width=10)
    d.rectangle([x - 18 * k, y - r - 34 * k, x + 18 * k, y - r], fill=INK)
    d.text((x, y), txt, font=font(70 * k), fill=col, anchor="mm", stroke_width=int(6 * k), stroke_fill=INK)

# ------------------------------------------------------------ planos
SHOTS = []
def shot(fn): SHOTS.append(fn); return fn
def tl(k, frac): return LEAD + len(VOZ[k]) / SR * frac

@shot
def s01(t, D, T):   # gancho: Nico en moto de delivery a toda velocidad
    cam = Cam(540, 1050, 1.05)
    dr = Lienzo(cam); cielo(dr, t * 3)
    off = (t * 900) % 600
    for k in range(-2, 6): dr.rrect(-500, 1300, 1600, 2600, 0, (70, 74, 84))
    for k in range(-1, 5): dr.rrect(k * 600 - off - 100, 1560, k * 600 - off + 150, 1590, 8, (250, 220, 90))
    colinas(dr, 1250)
    for k in range(-1, 4):
        bx = k * 520 - (t * 300) % 520
        dr.rrect(bx, 900, bx + 220, 1300, 6, (150, 170, 200)); dr.rrect(bx + 40, 960, bx + 90, 1010, 4, (220, 236, 250)); dr.rrect(bx + 130, 960, bx + 180, 1010, 4, (220, 236, 250))
    dr.rrect(-500, 1300, 1600, 1330, 0, (60, 62, 70))
    seat = moto(dr, 540, 1640, 1.15, t, face=1, vibra=1.0, rueda=t * 20)
    info = nico(dr, seat[0] + 10, seat[1] + 210, 0.6, t, arms=(70, 70), elbows=(40, 40), expr="happy", look=(1, 0))
    gorra(dr, info, 0.6)
    f_ = tinta(dr); img = acabado(f_, T)
    d = ImageDraw.Draw(img)
    for k in range(14):
        y = 700 + (k * 97) % 900; x0 = (k * 211 + int(t * 1400)) % 1300 - 200
        d.line([(x0, y), (x0 - 180, y)], fill=(255, 255, 255), width=6)
    return img, 2

@shot
def s02(t, D, T):   # portal → patio del castillo, frena en seco
    cam = Cam(540, 1100, 1.0)
    dr = Lienzo(cam); patio(dr, t)
    o = ease(t / 0.4) * (1 - ease((t - 2.2) / 0.4))
    portal(dr, 300, 1450, 200, t, o)
    u = clamp((t - 0.4) / 1.0)
    mx = lerp(200, 600, eob(u))
    if t > 0.4:
        seat = moto(dr, mx, 1780, 0.9, t, face=1, vibra=1.0 - u * 0.6, rueda=t * 14 * (1 - u))
        info = nico(dr, seat[0] + 8, seat[1] + 165, 0.48, t, arms=(70, 70), elbows=(40, 40), expr="shock" if t < 2 else "happy", look=(0.6, -0.4))
        gorra(dr, info, 0.48)
    f_ = tinta(dr); img = acabado(f_, T)
    if t > 1.6: cartel(img, t - 1.6, "EDAD MEDIA", "AÑO 1200")
    return img, (10 * math.exp(-(t - 1.4) * 5) if t > 1.4 else 0)

@shot
def s03(t, D, T):   # el rey: ¿qué es esa bestia de metal? ¡guardias!
    cam = Cam(540, 1050, 1.15)
    dr = Lienzo(cam); sala_trono(dr, t)
    rey(dr, 540, 1500, 0.9, t, mouth=boca(2, t), expr="shock" if t < tl(2, 0.7) else "angry", arms=(60, 130) if t > tl(2, 0.7) else (30, 30), look=(-0.6, 0.2))
    if t > tl(2, 0.72):
        u = eob((t - tl(2, 0.72)) / 0.35)
        guardia(dr, lerp(-200, 140, u), 1900, 0.85, t, face=1)
        guardia(dr, lerp(1280, 940, u), 1900, 0.85, t, face=-1)
    f_ = tinta(dr); img = acabado(f_, T)
    if t > tl(2, 0.72): burst(img, "¡GUARDIAS!", 540, 400, 140, t - tl(2, 0.72), col=(255, 90, 60), ang=5)
    return img, (8 if t > tl(2, 0.72) and t < tl(2, 0.72) + 0.4 else 0)

@shot
def s04(t, D, T):   # Nico: pizza a domicilio en 30 min o es gratis (rodeado de lanzas)
    cam = Cam(540, 1080, 1.3)
    dr = Lienzo(cam); sala_trono(dr, t)
    guardia(dr, 160, 1950, 0.8, t, face=1); guardia(dr, 920, 1950, 0.8, t, face=-1)
    info = nico(dr, 540, 1800, 0.62, t, arms=(20, 100), elbows=(0, -60), expr="happy", mouth=boca(3, t), look=(0, -0.3))
    gorra(dr, info, 0.62)
    hx, hy = info["hands"][1]
    caja_pizza(dr, hx + 30, hy - 20, 0.9, abierta=t > tl(3, 0.3))
    f_ = tinta(dr); img = acabado(f_, T)
    if t > tl(3, 0.45): reloj(img, 860, 520, "30:00", (255, 214, 10), t - tl(3, 0.45))
    if t > tl(3, 0.8): burst(img, "¡O ES GRATIS!", 400, 480, 90, t - tl(3, 0.8), ang=-8)
    return img, 0

def mapa_bg(dr):
    dr.rrect(-500, -900, 1600, 2600, 0, (70, 46, 34))
    pts = [(80, 360), (300, 330), (600, 350), (1000, 320), (1010, 700), (990, 1150), (700, 1180), (400, 1160), (70, 1190), (90, 760)]
    dr.poly(pts, (236, 214, 160))
    dr.poly([(150, 450), (420, 420), (480, 600), (300, 700), (160, 640)], (160, 196, 120))
    dr.poly([(600, 800), (900, 760), (940, 1050), (640, 1080)], (160, 196, 120))
    for (x, y) in ((260, 520), (800, 930)):
        dr.rrect(x - 40, y - 60, x + 40, y + 10, 4, (176, 168, 158)); dr.poly([(x - 50, y - 60), (x, y - 120), (x + 50, y - 60)], (170, 50, 50))
    dr.text(540, 410, "REINO DE NICOLANDIA", 34, (110, 60, 40), f=F_SERIF)

@shot
def s05(t, D, T):   # un mensaje a caballo tardaba días (mapa, caballito lento, calendario)
    cam = Cam(540, 800, 1.25)
    dr = Lienzo(cam); mapa_bg(dr)
    u = clamp(t / D) * 0.45
    for k in range(18):
        uu = k / 17
        dr.ell(lerp(300, 780, uu), lerp(560, 900, uu) - math.sin(uu * math.pi) * 120, 6, 6, (160, 60, 50), nolin=True)
    px, py = lerp(300, 780, u), lerp(560, 900, u) - math.sin(u * math.pi) * 120
    caballo(dr, px, py + 30, 0.18, t, face=1, walk=t * 3)
    f_ = tinta(dr); img = acabado(f_, T)
    d = ImageDraw.Draw(img); dias = 1 + int(t * 1.2)
    d.rounded_rectangle([700, 1230, 1000, 1480], radius=20, fill=(250, 248, 240), outline=INK, width=8)
    d.rectangle([700, 1230, 1000, 1310], fill=(200, 50, 50), outline=INK, width=8)
    d.text((850, 1270), "DÍAS", font=font(44), fill=(255, 255, 255), anchor="mm")
    d.text((850, 1400), str(dias), font=font(110), fill=INK, anchor="mm")
    return img, 0

@shot
def s06(t, D, T):   # Nico lo hace en 10 min · el rey con la boca abierta
    if t < D * 0.5:
        cam = Cam(540, 800, 1.25)
        dr = Lienzo(cam); mapa_bg(dr)
        u = ease(t / (D * 0.5))
        for k in range(18):
            uu = k / 17
            dr.ell(lerp(300, 780, uu), lerp(560, 900, uu) - math.sin(uu * math.pi) * 120, 6, 6, (40, 186, 204) if uu < u else (160, 60, 50), nolin=True)
        px, py = lerp(300, 780, u), lerp(560, 900, u) - math.sin(u * math.pi) * 120
        moto(dr, px, py + 40, 0.22, t, face=1, vibra=1, rueda=t * 30)
        f_ = tinta(dr); img = acabado(f_, T)
        reloj(img, 850, 1350, f"{int(u * 10):02d}:00", (40, 186, 204), t)
        return img, 0
    tt = t - D * 0.5
    cam = Cam(540, 1050, 1.35)
    dr = Lienzo(cam); sala_trono(dr, t)
    rey(dr, 540, 1550, 0.95, t, expr="shock", arms=(140, 140), look=(0, 0.2), mouth=0.6)
    caja_pizza(dr, 540, 1350, 1.1, abierta=True)
    f_ = tinta(dr); img = acabado(f_, T)
    burst(img, "¡10 MIN!", 540, 430, 150, tt, col=(90, 236, 255), ang=-6)
    return img, 0

@shot
def s07(t, D, T):   # ¡cien pizzas para todo el reino!
    cam = Cam(540, 1050, 1.2)
    dr = Lienzo(cam); sala_trono(dr, t)
    n = int(clamp(t / D) * 14) + 3
    for k in range(n):
        col = k % 2; row = k // 2
        caja_pizza(dr, 210 + col * 660, 1900 - row * 56, 0.95)
    rey(dr, 540, 1550, 0.95, t, mouth=boca(6, t), expr="happy", arms=(150, 150) if (t % 0.8) < 0.4 else (130, 130), comiendo=t > D * 0.7)
    f_ = tinta(dr); img = acabado(f_, T)
    burst(img, "¡100 PIZZAS!", 540, 420, 130, t - 0.2, ang=6)
    return img, 3 * math.sin(T * 40) * boca(6, t)

@shot
def s08(t, D, T):   # no hay gasolineras: la moto se apaga
    cam = Cam(540, 1150, 1.25)
    dr = Lienzo(cam); cielo(dr, t); colinas(dr, 1250)
    dr.rrect(-500, 1250, 1600, 2600, 0, (176, 150, 110))
    for k in range(6): dr.line([(-500, 1300 + k * 80), (1600, 1300 + k * 80 - 30)], (156, 130, 92), 5)
    stop = t > tl(7, 0.7)
    u = clamp(t / tl(7, 0.7))
    mx = lerp(250, 540, ease(u))
    seat = moto(dr, mx, 1750, 1.0, t, face=1, vibra=0 if stop else (1 if (t * 6) % 1 < 0.6 else 0.2), rueda=0 if stop else t * 8)
    info = nico(dr, seat[0] + 8, seat[1] + 180, 0.52, t, arms=(70, 70), elbows=(40, 40), expr="worried" if stop else "nervous", look=(0.3, 0.6))
    gorra(dr, info, 0.52)
    f_ = tinta(dr); img = acabado(f_, T)
    d = ImageDraw.Draw(img)
    gx, gy = 820, 560; r = 140
    d.pieslice([gx - r, gy - r, gx + r, gy + r], 180, 360, fill=(250, 250, 250), outline=INK, width=8)
    d.text((gx - r + 30, gy - 20), "E", font=font(48), fill=(220, 40, 40), anchor="mm"); d.text((gx + r - 30, gy - 20), "F", font=font(48), fill=INK, anchor="mm")
    ang = math.radians(180 + 160 * (1 - ease(u)) + (2 * math.sin(t * 30) if not stop else 0))
    d.line([(gx, gy), (gx + math.cos(ang) * (r - 25), gy + math.sin(ang) * (r - 25))], fill=(220, 40, 40), width=12)
    d.ellipse([gx - 16, gy - 16, gx + 16, gy + 16], fill=INK)
    if stop:
        burst(img, "¡PFFF…!", 300, 520, 110, t - tl(7, 0.7), col=(200, 200, 210), ang=-8)
        for k in range(4):
            ph = (t * 0.8 + k * 0.25) % 1
            sx_, sy_ = cam.p(mx - 230, 1640)
            rr = 20 + 60 * ph
            d.ellipse([sx_ - rr - ph * 80, sy_ - rr - ph * 160, sx_ + rr - ph * 80, sy_ + rr - ph * 160], fill=(120, 120, 130))
    return img, 0

@shot
def s09(t, D, T):   # ¿alguien tiene un caballo? → aparece un caballo
    cam = Cam(540, 1150, 1.3)
    dr = Lienzo(cam); cielo(dr, t); colinas(dr, 1250)
    dr.rrect(-500, 1250, 1600, 2600, 0, (176, 150, 110))
    moto(dr, 300, 1800, 0.9, t, face=1)
    if t > tl(8, 0.6):
        u = eob((t - tl(8, 0.6)) / 0.6)
        caballo(dr, lerp(1400, 900, u), 1850, 0.75, t, face=-1, walk=t * 8 if u < 1 else 0)
    info = nico(dr, 600, 1820, 0.6, t, arms=(20, 150), elbows=(0, 20), expr="nervous", mouth=boca(8, t), look=(0.8, -0.2), sweat=True)
    gorra(dr, info, 0.6)
    f_ = tinta(dr); img = acabado(f_, T)
    if t > tl(8, 0.6): burst(img, "¡HIIII!", 820, 520, 110, t - tl(8, 0.6), ang=8)
    return img, 0

@shot
def s10(t, D, T):   # el primer delivery a caballo + pregunta
    cx = t * 260
    cam = Cam(540 + 0, 1150, 1.05)
    dr = Lienzo(cam); cielo(dr, t * 2)
    dr.poly([(-500, 1180), (1600, 1180), (1600, 1300), (-500, 1300)], (90, 140, 74))
    for k in range(-1, 4):
        bx = k * 600 - (cx % 600)
        castillo(dr, t, bx + 300, 1200, 0.3)
    dr.rrect(-500, 1300, 1600, 2600, 0, (176, 150, 110))
    bob = abs(math.sin(t * 7)) * 14
    seat = caballo(dr, 540, 1850 - bob, 0.85, t, face=1, walk=t * 9)
    for k in range(5): caja_pizza(dr, seat[0] - 190, seat[1] - 10 - k * 46 - bob, 0.75)
    info = nico(dr, seat[0] + 20, seat[1] + 200 - bob, 0.5, t, arms=(150, 30), elbows=(20, 0), expr="happy", look=(1, 0))
    gorra(dr, info, 0.5)
    f_ = tinta(dr); img = acabado(f_, T)
    if t > tl(9, 0.5):
        k = eob((t - tl(9, 0.5)) / 0.3); d = ImageDraw.Draw(img)
        d.rounded_rectangle([120, 400, 960, 600], radius=36, fill=(255, 214, 10), outline=INK, width=8)
        d.text((540, 465), "¿A QUÉ ÉPOCA", font=font(70 * k + 1), fill=INK, anchor="mm")
        d.text((540, 545), "LLEVO A NICO? 👇".replace(" 👇", ""), font=font(70 * k + 1), fill=INK, anchor="mm")
    else:
        burst(img, "DELIVERY 1200", 540, 470, 100, t, col=(90, 236, 255), ang=-5)
    return img, 0

@shot
def s11(t, D, T):   # cierre con portal
    cam = Cam(540, 1050, 1.0)
    dr = Lienzo(cam, bg=(18, 10, 30)); patio(dr, t)
    o = 1 - ease((t - D + 1.0) / 0.8)
    portal(dr, 540, 1250, 300, t, o)
    if t < D - 1.2:
        info = nico(dr, 540, 1650, 0.5, t, arms=(150, 20), elbows=(30, 0), expr="happy")
        gorra(dr, info, 0.5)
    f_ = tinta(dr); add_glow(f_, *cam.p(540, 1250), 420, (150, 120, 255), 0.5 * o)
    return acabado(f_, T), 0

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
    badge(img, T); caption(img, T)
    return img

# ------------------------------------------------------------ sonido
def make_audio(path):
    from scipy.signal import butter, sosfilt
    sr = SR; n = int(TOTAL * sr) + sr; out = np.zeros(n)
    rng = np.random.default_rng(5)
    def add(s, sig, g=1.0):
        i0 = int(s * sr); i1 = min(n, i0 + len(sig))
        if 0 <= i0 < n: out[i0:i1] += g * sig[:i1 - i0]
    def seg(d): return np.arange(int(d * sr)) / sr
    hz = lambda m: 440 * 2 ** ((m - 69) / 12)
    noise = rng.standard_normal(n)
    bp = lambda lo, hi: sosfilt(butter(2, [lo, hi], btype="band", fs=sr, output="sos"), noise)
    wh = bp(400, 3500)
    # música medieval alegre (laúd + tambor), re dórico, 120 bpm
    e8 = 0.25
    mel = [62, 64, 65, 67, 69, 67, 65, 64, 62, 69, 72, 71, 69, 67, 65, 64]
    bass = [50, 50, 48, 48, 50, 53, 48, 50]
    k = 0; s = STARTS[1]
    while s < STARTS[10]:
        x = seg(e8 * 1.4); m = mel[k % len(mel)]
        if k % 2 == 0 or k % 8 == 7:
            pl = np.sin(2 * np.pi * hz(m) * x) + 0.5 * np.sin(2 * np.pi * hz(m) * 2 * x) + 0.25 * np.sin(2 * np.pi * hz(m) * 3 * x)
            add(s, 0.035 * pl * np.exp(-x * 7))
        if k % 4 == 0:
            xb = seg(e8 * 4); add(s, 0.07 * np.exp(-xb * 2.5) * np.sin(2 * np.pi * hz(bass[(k // 4) % 8]) * xb))
            add(s, 0.15 * np.exp(-x * 18) * np.sin(2 * np.pi * (80 + 50 * np.exp(-x * 25)) * x))
        if k % 4 == 2: add(s, 0.05 * rng.standard_normal(len(x)) * np.exp(-x * 28))
        k += 1; s += e8
    S_ = STARTS
    # moto
    x = seg(DURS[0]); add(0, 0.12 * np.sign(np.sin(2 * np.pi * (70 + 8 * np.sin(2 * np.pi * 3 * x)) * x)) * 0.5 + 0.05 * bp(100, 600)[:len(x)])
    x = seg(1.2); add(S_[1] + 0.2, 0.12 * np.sin(2 * np.pi * (200 + 600 * x) * x) * np.sin(np.pi * x / 1.2))
    x = seg(0.6); add(S_[1] + 1.4, 0.25 * bp(1500, 5000)[:len(x)] * np.exp(-x * 5))
    for s0 in S_[1:-1]:
        x = seg(0.3); add(s0, 0.2 * wh[int(s0 * sr):int(s0 * sr) + len(x)] * np.sin(np.pi * x / 0.3) ** 2)
    x = seg(0.6); add(S_[2] + tl(2, 0.72), 0.25 * np.exp(-x * 4) * (np.sin(2 * np.pi * 392 * x) + np.sin(2 * np.pi * 523 * x)))
    x = seg(0.4); add(S_[3] + tl(3, 0.45), 0.2 * np.exp(-x * 9) * np.sin(2 * np.pi * 1200 * x))
    for kk in range(int(DURS[4] / 0.5)): add(S_[4] + kk * 0.5, 0.15 * np.exp(-seg(0.1) * 40) * np.sin(2 * np.pi * 300 * seg(0.1)))
    x = seg(DURS[5] * 0.5); add(S_[5], 0.1 * np.sign(np.sin(2 * np.pi * (90 + 40 * x) * x)) * 0.5)
    x = seg(1.0); add(S_[5] + DURS[5] * 0.5, 0.2 * np.exp(-x * 2) * (np.sin(2 * np.pi * 659 * x) + np.sin(2 * np.pi * 784 * x)))
    x = seg(1.2); add(S_[7] + tl(7, 0.7) - 0.6, 0.12 * np.sign(np.sin(2 * np.pi * (80 - 50 * x) * x)) * np.exp(-x * 1.5))
    x = seg(0.9); add(S_[8] + tl(8, 0.6), 0.25 * np.sin(2 * np.pi * (700 + 300 * np.sin(2 * np.pi * 9 * x)) * x) * np.exp(-x * 2.5))
    for kk in range(int(DURS[9] / 0.3)):
        xs = seg(0.12); add(S_[9] + kk * 0.3, 0.2 * np.exp(-xs * 30) * bp(200, 1200)[int(kk * 3000):int(kk * 3000) + len(xs)])
    x = seg(1.0); add(S_[10] + DURS[10] - 0.9, 0.12 * np.sin(2 * np.pi * (300 + 600 * x) * x) * np.sin(np.pi * x))
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
                          "-i", "audio.wav", "-c:v", "libx264", "-preset", "veryfast", "-crf", "26", "-tune", "animation", "-pix_fmt", "yuv420p",
                          "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
    N = int(TOTAL * FPS)
    for k in range(N):
        p.stdin.write(frame(k / FPS).convert("RGB").tobytes())
        if k % 300 == 0: print(f"{k}/{N}", flush=True)
    p.stdin.close(); p.wait(); print("listo", OUT, TOTAL)
