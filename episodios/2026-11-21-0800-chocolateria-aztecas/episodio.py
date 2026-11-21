#!/usr/bin/env python3
"""¿Qué pasaría si abres una CHOCOLATERÍA en el imperio azteca? — 08:00 del 2026-11-21 (estilo vector + cómic)."""
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
DURS[0] += 0.5; DURS[1] += 0.4; DURS[5] += 0.4; DURS[8] += 0.5; DURS[9] += 0.3; DURS[10] += 0.6; DURS[11] += 1.2
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
    [("¿Qué pasaría si", []), ("abres una", []), ("CHOCOLATERÍA…", ["CHOCOLATERÍA…"]), ("en el imperio azteca?", ["azteca?"])],
    [("Nico cruza el portal", ["portal"]), ("y aparece en", []), ("TENOCHTITLAN", ["TENOCHTITLAN"]), ("la gran ciudad azteca", ["azteca"]), ("en el año 1500", ["1500"])],
    [("¡Chocolate dulce,", ["dulce,"]), ("en barrita!", ["barrita!"]), ("¡Pruébenlo,", []), ("está delicioso!", ["delicioso!"])],
    [("¿Chocolate duro?", ["duro?"]), ("Aquí lo tomamos", []), ("amargo, con espuma…", ["amargo,"]), ("¡y con CHILE!", ["CHILE!"])],
    [("Dato real:", ["real:"]), ("para los aztecas", []), ("los granos de cacao", ["cacao"]), ("eran DINERO", ["DINERO"]), ("un guajolote costaba", ["guajolote"]), ("unos 100 granos", ["100"]), ("y un aguacate, 3", ["3"])],
    [("Espera…", []), ("¿o sea que", []), ("me estoy comiendo…", ["comiendo…"]), ("el DINERO?", ["DINERO?"])],
    [("Pero las barritas", []), ("se ponen de moda", ["moda"]), ("y en el mercado", []), ("pagan… ¡con chocolate!", ["chocolate!"])],
    [("¡Te cambio", []), ("este guajolote", ["guajolote"]), ("por tres barritas!", ["tres"])],
    [("Nico se vuelve", []), ("el más RICO", ["RICO"]), ("de Tenochtitlan", []), ("Hasta que al mediodía", ["mediodía"]), ("sale el sol…", ["sol…"]), ("y el dinero", []), ("¡se DERRITE!", ["DERRITE!"])],
    [("¡No, no, no!", []), ("¡Mi fortuna!", ["fortuna!"]), ("¡Y el guajolote", ["guajolote"]), ("se come el banco!", ["banco!"])],
    [("Y así nació", []), ("la primera crisis", ["crisis"]), ("económica…", []), ("¡de CHOCOLATE!", ["CHOCOLATE!"]), ("¿Qué negocio llevo", ["negocio"]), ("a otra época?", ["época?"]), ("¡Coméntalo!", ["¡Coméntalo!"])],
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


# ------------------------------------------------------------ Tenochtitlan
CHOC, CHOC_D, CHOC_L = (110, 62, 36), (82, 44, 26), (150, 92, 56)
def cielo(dr, t, top=(90, 170, 230), bot=(200, 236, 250), sol=(860, 330), solr=110, solc=(255, 246, 200)):
    for k in range(6):
        u = k / 5; c = tuple(int(lerp(top[i], bot[i], u)) for i in range(3))
        dr.rrect(-700, -900 + k * 360, 1800, -900 + (k + 1) * 360 + 2, 0, c, nolin=True)
    if sol: dr.ell(sol[0], sol[1], solr, solr, solc, nolin=True)
    for k, (x, y, s) in enumerate(((150, 260, 1.0), (760, 120, 1.2), (420, 420, 0.7))):
        xx = (x + t * 12 * s) % 1600 - 250
        for (a, b, r) in ((-60, 10, 50), (0, -14, 66), (64, 10, 50)):
            dr.ell(xx + a * s, y + b * s, r * s, r * 0.5 * s, (255, 255, 255), nolin=True)

def volcanes(dr, gy):
    for (cx, w, h, c, cd) in ((80, 520, 520, (150, 140, 170), (120, 110, 146)), (820, 620, 640, (140, 132, 166), (112, 104, 140))):
        dr.poly([(cx - w, gy), (cx - 70, gy - h), (cx + 70, gy - h), (cx + w, gy)], c)
        dr.poly([(cx, gy - h), (cx + 70, gy - h), (cx + w, gy), (cx + w * 0.25, gy)], cd, nolin=True)
        dr.poly([(cx - 70, gy - h), (cx + 70, gy - h), (cx + 140, gy - h + 120), (cx + 40, gy - h + 80), (cx - 30, gy - h + 130), (cx - 140, gy - h + 120)], (250, 250, 255))

def templo(dr, x, base, s=1.0):
    S = lambda v: v * s
    cols = [(206, 180, 140), (196, 168, 128)]
    for k in range(5):
        w = S(480 - k * 70); y0 = base - S(k * 90)
        dr.poly([(x - w, y0), (x - w + S(30), y0 - S(90)), (x + w - S(30), y0 - S(90)), (x + w, y0)], cols[k % 2], shade=True)
        dr.poly([(x + w * 0.45, y0 - S(90)), (x + w - S(30), y0 - S(90)), (x + w, y0), (x + w * 0.5, y0)], tuple(int(v * 0.86) for v in cols[k % 2]), nolin=True)
    for sx in (-1, 1):   # escalinatas dobles
        dr.poly([(x + sx * S(40), base), (x + sx * S(170), base), (x + sx * S(120), base - S(450)), (x + sx * S(50), base - S(450))], (232, 214, 180))
        for k in range(12): dr.line([(x + sx * S(42 + k * 0.6), base - S(k * 38)), (x + sx * S(168 - k * 4), base - S(k * 38))], (200, 180, 146), S(4), nolin=True)
    top = base - S(450)
    for sx, col, roof in ((-1, (196, 52, 44), (236, 236, 230)), (1, (40, 120, 200), (236, 236, 230))):
        cx = x + sx * S(130)
        dr.rrect(cx - S(100), top - S(170), cx + S(100), top, S(6), col, shade=True)
        dr.rrect(cx - S(40), top - S(110), cx + S(40), top, S(6), (40, 26, 30))
        dr.poly([(cx - S(115), top - S(170)), (cx + S(115), top - S(170)), (cx + S(95), top - S(240)), (cx - S(95), top - S(240))], roof)
        for k in range(5): dr.rrect(cx - S(90) + k * S(40), top - S(232), cx - S(70) + k * S(40), top - S(186), S(4), col, nolin=True)

def lago(dr, t, gy, h=500):
    dr.rrect(-700, gy, 1800, gy + h, 0, (70, 150, 190))
    for k in range(7):
        yy = gy + 20 + k * 60
        xx = (t * 40 * (1 if k % 2 else -1)) % 300
        for j in range(-3, 9): dr.line([(j * 300 + xx - 60, yy), (j * 300 + xx + 60, yy)], (130, 200, 230), 6, nolin=True)

def canoa(dr, x, y, s, t, rem=True):
    S = lambda v: v * s
    dr.poly([(x - S(220), y - S(40)), (x + S(220), y - S(40)), (x + S(180), y + S(20)), (x - S(180), y + S(20))], (140, 90, 50))
    dr.rrect(x - S(30) - S(26), y - S(150), x - S(30) + S(26), y - S(40), S(20), (240, 236, 220))
    dr.ell(x - S(30), y - S(180), S(34), S(34), (190, 126, 84))
    dr.rrect(x - S(66), y - S(214), x + S(6), y - S(196), S(6), (196, 52, 44))
    a = math.sin(t * 3) * 0.5
    dr.line([(x + S(10), y - S(140)), (x + S(10) + math.sin(a) * S(160), y + S(30))], (110, 70, 40), S(10))

def chinampas(dr, gy):
    for k, x in enumerate((-300, 120, 560, 1000)):
        dr.poly([(x - 160, gy + 40), (x + 160, gy + 40), (x + 140, gy + 10), (x - 140, gy + 10)], (110, 160, 80))
        for j in range(4): dr.ell(x - 100 + j * 66, gy + 6, 26, 30, (70, 140, 70), nolin=True)

def ciudad(dr, t, gy=1250, tem=True):
    cielo(dr, t); volcanes(dr, gy - 180)
    lago(dr, t, gy - 190, 200)
    chinampas(dr, gy - 160)
    if tem: templo(dr, 540, gy, 0.9)
    for k, x in enumerate((-260, 130, 950, 1340)):
        dr.rrect(x - 130, gy - 180, x + 130, gy, 6, (232, 220, 196), shade=True)
        dr.rrect(x - 140, gy - 200, x + 140, gy - 175, 4, (196, 52, 44) if k % 2 else (40, 186, 204))
        dr.rrect(x - 30, gy - 110, x + 30, gy, 4, (70, 50, 40))
    dr.rrect(-700, gy, 1800, 2700, 0, (214, 196, 160))
    for k in range(9):
        yy = gy + 30 + k * k * 12 + k * 26
        dr.line([(-700, yy), (1800, yy + 6)], (196, 176, 140), 4, nolin=True)

def puesto(dr, x, gy, s=1.0, txt="CHOCOLATERÍA", col=TURQ, t=0):
    S = lambda v: v * s
    for sx in (-1, 1): dr.line([(x + sx * S(300), gy), (x + sx * S(300), gy - S(820))], (120, 80, 46), S(22))
    for k in range(6):
        c = col if k % 2 == 0 else (250, 246, 236)
        x0 = x - S(330) + k * S(110)
        dr.poly([(x0, gy - S(560)), (x0 + S(110), gy - S(560)), (x0 + S(120), gy - S(470)), (x0 + S(10), gy - S(470))], c)
    for k in range(6): dr.chord(x - S(330) + k * S(110) + S(65), gy - S(470), S(55), S(30), 0, 180, col if k % 2 == 0 else (250, 246, 236))
    dr.rrect(x - S(320), gy - S(840), x + S(320), gy - S(730), S(16), (250, 240, 210))
    dr.text(x, gy - S(785), txt, S(min(62, 1000 / max(4, len(txt)))), CHOC, f=F_BLACK)
    dr.rrect(x - S(320), gy - S(230), x + S(320), gy, S(10), (160, 108, 64), shade=True)
    for k in range(-4, 5): dr.line([(x + k * S(70), gy - S(220)), (x + k * S(70), gy - S(10))], (130, 86, 50), S(5), nolin=True)

def barra(dr, x, y, w, h, bite=0.0, melt=0.0, wrap=True):
    if melt > 0:
        h2 = h * (1 - 0.6 * melt); y = y + h * 0.6 * melt * 0.5
        dr.ell(x, y + h2 / 2, w * (0.55 + 0.4 * melt), h * 0.25 * melt + 4, CHOC_D)
        h = h2
    dr.rrect(x - w / 2, y - h / 2, x + w / 2, y + h / 2, min(w, h) * 0.12, CHOC, shade=True)
    nx = 4
    for i in range(nx):
        for j in range(2):
            cx = x - w / 2 + w * (i + 0.5) / nx; cy = y - h / 2 + h * (j + 0.5) / 2
            dr.rrect(cx - w / nx * 0.38, cy - h * 0.2, cx + w / nx * 0.38, cy + h * 0.2, 4, CHOC_L if melt < 0.5 else CHOC, nolin=True)
    if wrap and melt < 0.3:
        dr.rrect(x + w * 0.1, y - h / 2 - 6, x + w / 2 + 6, y + h / 2 + 6, 8, TURQ)
        dr.rrect(x + w * 0.18, y - h * 0.15, x + w * 0.42, y + h * 0.15, 4, (250, 246, 236), nolin=True)
    if bite > 0:
        bx = x - w / 2
        for k in range(3): dr.ell(bx + w * 0.05, y - h * 0.3 + k * h * 0.3, w * 0.09 * bite + 1, h * 0.2 * bite + 1, (255, 255, 255), nolin=True)
    if melt > 0.2:
        for k in range(3):
            dx = x - w * 0.3 + k * w * 0.3
            dr.ell(dx, y + h / 2 + 18 * melt * (1 + k % 2), 9, 18 * melt * (1 + k % 2), CHOC_D, nolin=True)

def grano(dr, x, y, r, a=0.0):
    dr.ell(x, y, r, r * 0.66, (120, 66, 44)); dr.line([(x - r * 0.7, y), (x + r * 0.7, y)], (80, 40, 26), max(2, r * 0.15), nolin=True)

def taza(dr, x, y, s=1.0):
    S = lambda v: v * s
    dr.poly([(x - S(70), y - S(120)), (x + S(70), y - S(120)), (x + S(50), y), (x - S(50), y)], (196, 110, 70), shade=True)
    for k in range(3): dr.line([(x - S(60) + k * S(40), y - S(80)), (x - S(40) + k * S(40), y - S(60))], (240, 230, 210), S(6), nolin=True)
    for k in range(5): dr.ell(x - S(56) + k * S(28), y - S(128), S(24), S(18), (226, 196, 160))
    dr.poly([(x + S(30), y - S(150)), (x + S(60), y - S(240)), (x + S(80), y - S(230)), (x + S(56), y - S(140))], (220, 40, 30))
    dr.rrect(x + S(56), y - S(250), x + S(80), y - S(230), S(4), (60, 140, 60))

def guajolote(dr, x, y, s, t, face=1, peck=0.0, choc=False):
    S = lambda v: v * s; f = face
    for k in range(9):
        a = math.radians(-160 + k * 17.5)
        tx, ty = x - f * S(60) + math.cos(a) * S(260) * -f, y - S(260) + math.sin(a) * S(260)
        dr.poly([(x - f * S(60), y - S(240)), (tx - S(40), ty), (tx + S(40), ty)], (120, 76, 46) if k % 2 else (150, 100, 60))
        dr.ell(tx, ty, S(34), S(34), (236, 220, 190))
    for sx in (-1, 1): dr.line([(x + sx * S(30), y - S(90)), (x + sx * S(30), y)], (230, 150, 60), S(14))
    dr.ell(x, y - S(200), S(150), S(120), (90, 60, 44), shade=True)
    for k in range(4): dr.chord(x + f * S(20) - k * f * S(40), y - S(170), S(40), S(30), 0, 180, (70, 44, 32))
    p = clamp(peck)
    nx, ny = x + f * S(120 + 60 * p), y - S(330) + S(170) * p
    dr.line([(x + f * S(90), y - S(260)), (nx, ny)], (110, 80, 60), S(46))
    dr.ell(nx, ny, S(56), S(52), (130, 170, 220))
    dr.ell(nx + f * S(10), ny - S(12), S(12), S(14), INK)
    dr.poly([(nx + f * S(48), ny - S(6)), (nx + f * S(96), ny + S(10)), (nx + f * S(48), ny + S(22))], (240, 180, 60))
    dr.ell(nx + f * S(40), ny + S(56), S(18), S(36), (220, 50, 50))
    if choc: dr.ell(nx + f * S(70), ny + S(24), S(26), S(14), CHOC_D, nolin=True)

def tochtli(dr, x, y, s, t, mouth=0.0, expr="angry", arms=(20, 20), look=(0, 0)):
    """Comerciante azteca: piel morena, cabello negro con flequillo, tilma naranja anudada, cinta roja con pluma."""
    S = lambda v: v * s; skin = (184, 120, 80); bob = S(5) * math.sin(t * 2.1)
    for sx in (-1, 1):
        dr.rrect(x + sx * S(45) - S(24), y - S(250), x + sx * S(45) + S(24), y - S(20), S(12), skin)
        dr.ell(x + sx * S(50), y - S(10), S(44), S(18), (150, 96, 50))
    dr.rrect(x - S(140), y - S(560) + bob, x + S(140), y - S(220), S(80), (246, 240, 224), shade=True)
    dr.poly([(x - S(140), y - S(540) + bob), (x + S(60), y - S(560) + bob), (x + S(150), y - S(260)), (x - S(150), y - S(240))], (226, 120, 50))
    for k in range(6): dr.poly([(x - S(140) + k * S(50), y - S(250)), (x - S(115) + k * S(50), y - S(220)), (x - S(90) + k * S(50), y - S(250))], (40, 120, 90))
    dr.ell(x + S(60), y - S(530) + bob, S(26), S(26), (40, 120, 90))
    hands = []
    for sx, a in ((-1, arms[0]), (1, arms[1])):
        shx, shy = x + sx * S(120), y - S(510) + bob
        ar = math.radians(a); hx_, hy_ = shx + sx * math.sin(ar) * S(220), shy + math.cos(ar) * S(220)
        dr.line([(shx, shy), (hx_, hy_)], skin, S(50)); dr.ell(hx_, hy_, S(32), S(32), skin); hands.append((hx_, hy_))
    hx, hy = x, y - S(720) + bob
    dr.ell(hx, hy, S(158), S(160), skin, shade=True)
    dr.chord(hx, hy - S(20), S(166), S(160), 180, 360, (30, 26, 30))
    dr.rrect(hx - S(166), hy - S(60), hx + S(166), hy - S(30), S(6), (30, 26, 30))
    dr.rrect(hx - S(170), hy - S(100), hx + S(170), hy - S(64), S(8), (196, 52, 44))
    dr.poly([(hx + S(110), hy - S(90)), (hx + S(170), hy - S(300)), (hx + S(200), hy - S(290)), (hx + S(150), hy - S(80))], (40, 160, 90))
    dr.ell(hx, hy + S(40), S(38), S(34), (166, 104, 68))
    if (t % 3.1) < 0.12:
        for sx in (-1, 1): dr.rrect(hx + sx * S(60) - S(30), hy - S(8), hx + sx * S(60) + S(30), hy + S(2), S(4), INK)
    else:
        for sx in (-1, 1):
            ex, ey = hx + sx * S(60), hy - S(5)
            big = 1.25 if expr == "shock" else 1.0
            dr.ell(ex, ey, S(28) * big, S(32) * big, (255, 255, 255)); dr.ell(ex + look[0] * S(9), ey + look[1] * S(9), S(13), S(16), INK)
            tilt = {"angry": 22, "happy": -8, "shock": -14}.get(expr, 0) * sx
            dr.line([(ex - S(34), ey - S(46) + S(tilt) * 0.5), (ex + S(34), ey - S(46) - S(tilt) * 0.5)], (30, 26, 30), S(14))
    mo = clamp(mouth)
    if mo > 0.06: dr.ell(hx, hy + S(100), S(40), S(8 + 30 * mo), (110, 30, 40))
    elif expr == "happy": dr.chord(hx, hy + S(86), S(42), S(28), 0, 180, (110, 30, 40))
    else: dr.line([(hx - S(34), hy + S(104)), (hx + S(34), hy + S(98))], (110, 30, 40), S(9))
    for sx in (-1, 1): dr.ell(hx + sx * S(150), hy + S(30), S(14), S(14), TURQ)
    return dict(head=(hx, hy), hands=hands)

def gente(dr, x, y, s, t, k=0, holds=False):
    S = lambda v: v * s; skin = [(184, 120, 80), (200, 140, 96), (170, 108, 70)][k % 3]
    tun = [(246, 240, 224), (226, 120, 50), (240, 210, 120), (196, 52, 44)][k % 4]
    bob = S(6) * abs(math.sin(t * 3 + k))
    dr.rrect(x - S(90), y - S(380) - bob, x + S(90), y, S(50), tun, shade=True)
    dr.ell(x, y - S(470) - bob, S(100), S(100), skin, shade=True)
    dr.chord(x, y - S(480) - bob, S(104), S(100), 180, 360, (30, 26, 30))
    for sx in (-1, 1): dr.ell(x + sx * S(36), y - S(470) - bob, S(12), S(15), INK, nolin=True)
    dr.chord(x, y - S(430) - bob, S(30), S(20), 0, 180, (110, 30, 40))
    if holds:
        hy = y - S(560) - bob - S(30) * abs(math.sin(t * 4 + k))
        dr.line([(x + S(70), y - S(320) - bob), (x + S(110), hy)], skin, S(36))
        barra(dr, x + S(110), hy - S(40), S(130), S(70))

# ------------------------------------------------------------ planos
SHOTS = []
def shot(fn): SHOTS.append(fn); return fn
def tl(k, frac): return LEAD + len(VOZ[k]) / SR * frac

@shot
def s01(t, D, T):   # gancho: Nico azteca con barra gigante frente al Templo Mayor
    cam = Cam(540, 1080 - t * 15 + 300, 1.15 + t * 0.03)
    dr = Lienzo(cam); ciudad(dr, t)
    info = nico(dr, 560, 1900, 0.72, t, traje="azteca", arms=(95, 30), elbows=(-50, -60), expr="happy", look=(-0.6, -0.2))
    hx, hy = info["hands"][0]
    barra(dr, hx - 60, hy - 40, 240, 130, bite=1.0)
    for k in range(10):
        ph = (t * 0.6 + k * 0.13) % 1
        grano(dr, 80 + k * 105, 300 + ph * 1500, 22, 0)
    f_ = tinta(dr); img = acabado(f_, T)
    if t > 0.9: burst(img, "¡CHOCOLATE!", 540, 470, 140, t - 0.9, col=(255, 200, 80), ang=-7)
    return img, 0

@shot
def s02(t, D, T):   # portal → vista de Tenochtitlan
    cam = Cam(540, 1080 + 150 - t * 20, 0.95 + 0.02 * t)
    dr = Lienzo(cam); ciudad(dr, t)
    canoa(dr, (t * 90) % 1500 - 200, 1080, 0.5, t)
    o = ease(t / 0.4) * (1 - ease((t - 2.6) / 0.4))
    portal(dr, 260, 1450, 210, t, o)
    u = clamp((t - 0.5) / 0.8)
    if t > 0.5:
        nico(dr, lerp(260, 600, eob(u)), 1900, 0.68, t, traje="azteca", arms=(30, 150) if t > 2 else (20, 20), elbows=(0, 30), expr="shock" if t < 1.8 else "happy", look=(0.4, -0.5))
    f_ = tinta(dr); img = acabado(f_, T)
    if t > 1.6: cartel(img, t - 1.6, "TENOCHTITLAN", "AÑO 1500", y=400)
    return img, 0

@shot
def s03(t, D, T):   # Nico en su puesto ofreciendo barritas
    cam = Cam(540, 1080 + 330, 1.2 + t * 0.03)
    dr = Lienzo(cam); ciudad(dr, t, tem=False)
    templo(dr, 900, 1250, 0.6)
    puesto(dr, 540, 1960, 1.0, "CHOCOLATERÍA NICO")
    info = nico(dr, 540, 1820, 0.62, t, traje="azteca", arms=(20, 120), elbows=(0, -40), expr="happy", mouth=boca(2, t), look=(0.5, 0))
    for k in range(5): barra(dr, 330 + k * 105, 1720, 90, 50)
    hx, hy = info["hands"][1]
    barra(dr, hx + 20, hy - 30, 150, 80)
    gente(dr, 60, 2080, 0.7, t, 1); gente(dr, 1010, 2080, 0.7, t, 2)
    f_ = tinta(dr); img = acabado(f_, T)
    if t > tl(2, 0.25): burst(img, "¡DULCE!", 800, 420, 120, t - tl(2, 0.25), col=(255, 160, 200), ang=6)
    return img, 0

@shot
def s04(t, D, T):   # Tochtli: aquí lo tomamos amargo, con espuma y con chile
    cam = Cam(540, 1060 + 80 - t * 15, 1.5 + t * 0.04)
    dr = Lienzo(cam); ciudad(dr, t, tem=False); templo(dr, 300, 1250, 0.55)
    info = tochtli(dr, 560, 1880, 1.0, t, mouth=boca(3, t), expr="shock" if t < tl(3, 0.3) else "angry", arms=(20, 70), look=(-0.5, 0))
    hx, hy = info["hands"][1]
    if t > tl(3, 0.3): taza(dr, hx + 10, hy + 20, 1.0)
    f_ = tinta(dr); img = acabado(f_, T)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([50, 300, 520, 380], radius=18, fill=(250, 240, 210), outline=INK, width=6)
    d.text((285, 340), "TOCHTLI · comerciante", font=font(38), fill=(150, 60, 30), anchor="mm")
    if t > tl(3, 0.78): burst(img, "¡CON CHILE!", 640, 520, 120, t - tl(3, 0.78), col=(255, 80, 50), ang=-6)
    return img, 0

@shot
def s05(t, D, T):   # dato: cacao = dinero; guajolote = 100 granos; aguacate = 3
    cam = Cam(540, 1080 + 300, 1.05)
    dr = Lienzo(cam); ciudad(dr, t, tem=False); templo(dr, 540, 1250, 0.6)
    guajolote(dr, 330, 1900, 1.0, t, face=1, peck=0.15 * (1 + math.sin(t * 3)))
    dr.ell(820, 1820, 70, 92, (60, 110, 50), shade=True); dr.ell(820, 1840, 46, 60, (200, 220, 120)); dr.ell(820, 1860, 26, 28, (130, 80, 40))
    n = int(clamp((t - tl(4, 0.3)) / (D * 0.5)) * 40)
    for k in range(n):
        grano(dr, 120 + (k % 10) * 46, 1980 + (k // 10) * 34, 20)
    f_ = tinta(dr); img = acabado(f_, T)
    d = ImageDraw.Draw(img)
    if t > tl(4, 0.12):
        k = eob((t - tl(4, 0.12)) / 0.3)
        d.rounded_rectangle([140, 290, 940, 420], radius=30, fill=(255, 214, 10), outline=INK, width=8)
        d.text((540, 355), "CACAO = DINERO", font=font(78 * k + 1), fill=INK, anchor="mm")
    if t > tl(4, 0.55):
        k = eob((t - tl(4, 0.55)) / 0.3)
        d.rounded_rectangle([110, 470, 520, 570], radius=22, fill=(250, 246, 236), outline=INK, width=6)
        d.text((315, 520), "= 100 granos", font=font(52 * k + 1), fill=(150, 60, 30), anchor="mm")
    if t > tl(4, 0.85):
        k = eob((t - tl(4, 0.85)) / 0.3)
        d.rounded_rectangle([620, 470, 990, 570], radius=22, fill=(250, 246, 236), outline=INK, width=6)
        d.text((805, 520), "= 3 granos", font=font(52 * k + 1), fill=(150, 60, 30), anchor="mm")
    return img, 0

@shot
def s06(t, D, T):   # Nico (primer plano) en shock: ¿me estoy comiendo el dinero?
    cam = Cam(540, 1500, 1.85 + t * 0.06)
    dr = Lienzo(cam); ciudad(dr, t, tem=False); puesto(dr, 540, 1960, 1.0, "CHOCOLATERÍA NICO")
    sh = t > tl(5, 0.65)
    info = nico(dr, 540, 1930, 0.7, t, traje="azteca", arms=(30, 125), elbows=(0, -70), expr="shock" if sh else "worried", mouth=boca(5, t), look=(0.4, 0.3), sweat=True)
    hx, hy = info["hands"][1]
    barra(dr, hx + 10, hy - 40, 170, 90, bite=1.0)
    if sh:
        for k in range(14):
            ph = (t * 0.9 + k * 0.071) % 1
            grano(dr, 260 + (k * 37) % 560, 600 + ph * 900, 18)
    f_ = tinta(dr); img = acabado(f_, T)
    if sh: burst(img, "¡DINERO!", 540, 420, 150, t - tl(5, 0.65), col=(120, 230, 120), ang=-8)
    return img, (8 if sh and t - tl(5, 0.65) < 0.3 else 0)

@shot
def s07(t, D, T):   # el mercado paga con barritas
    cam = Cam(500 + t * 30, 1100 + 400, 1.15)
    dr = Lienzo(cam); ciudad(dr, t)
    puesto(dr, 1000, 1900, 0.75, "NICO", t=t)
    for k, x in enumerate((-80, 180, 440, 700)):
        gente(dr, x, 1980 + (k % 2) * 60, 0.85, t, k, holds=t > tl(6, 0.55) or k % 2 == 0)
    f_ = tinta(dr); img = acabado(f_, T)
    if t > tl(6, 0.6): burst(img, "¡PAGO CON CHOCOLATE!", 540, 460, 84, t - tl(6, 0.6), ang=5)
    return img, 0

@shot
def s08(t, D, T):   # Tochtli cambia un guajolote por tres barritas
    cam = Cam(540, 1080 + 200, 1.3 + t * 0.03)
    dr = Lienzo(cam); ciudad(dr, t, tem=False); templo(dr, 820, 1250, 0.55)
    guajolote(dr, 230, 1960, 0.8, t, face=1, peck=0.2 * abs(math.sin(t * 4)))
    info = tochtli(dr, 680, 1940, 0.9, t, mouth=boca(7, t), expr="happy", arms=(20, 150), look=(-0.6, 0))
    hx, hy = info["hands"][1]
    for k in range(3): barra(dr, hx + 30, hy - 40 - k * 56, 140, 50)
    f_ = tinta(dr); img = acabado(f_, T)
    if t > tl(7, 0.5): burst(img, "1 🦃 = 3 BARRITAS".replace("🦃 ", ""), 540, 430, 96, t - tl(7, 0.5), col=(255, 214, 10), ang=-5)
    return img, 0

@shot
def s09(t, D, T):   # Nico rico sobre montaña de barritas → sale el sol y todo se derrite
    melt = clamp((t - tl(8, 0.62)) / (D - tl(8, 0.62) - 0.2))
    sky_k = clamp((t - tl(8, 0.45)) / 0.8)
    top = tuple(int(lerp(a, b, sky_k)) for a, b in zip((90, 170, 230), (255, 150, 60)))
    bot = tuple(int(lerp(a, b, sky_k)) for a, b in zip((200, 236, 250), (255, 230, 140)))
    cam = Cam(540, 1080 + 200, 1.05 + 0.08 * melt)
    dr = Lienzo(cam)
    cielo(dr, t, top=top, bot=bot, sol=(540, 520 - 200 * sky_k), solr=110 + 120 * sky_k, solc=(255, 250, 210))
    volcanes(dr, 1070); lago(dr, t, 1060, 200); templo(dr, 900, 1250, 0.5)
    dr.rrect(-700, 1250, 1800, 2700, 0, (214, 196, 160))
    if melt > 0: dr.ell(540, 1990, 380 + 160 * melt, 60 + 40 * melt, CHOC_D)
    for r in range(4):
        for c in range(6 - r):
            barra(dr, 540 - (5 - r) * 70 + c * 140, 1960 - r * 70, 130, 64, melt=melt)
    info = nico(dr, 540, 1700 + 90 * melt, 0.55, t, traje="azteca", arms=(160, 160) if melt < 0.15 else (60, 60), elbows=(20, 20), expr="happy_eyes" if melt < 0.15 else "shock", sweat=melt > 0)
    f_ = tinta(dr)
    if sky_k > 0: add_glow(f_, *cam.p(540, 520 - 200 * sky_k), 500, (255, 200, 90), 0.6 * sky_k)
    img = acabado(f_, T)
    if t < tl(8, 0.4): burst(img, "¡RICO!", 540, 470, 140, t - 0.2, col=(255, 214, 10), ang=-6)
    if melt > 0.05: burst(img, "¡SE DERRITE!", 540, 1180, 110, t - tl(8, 0.62) - 0.1, col=(255, 120, 60), ang=6)
    return img, (5 if melt > 0.05 else 0)

@shot
def s10(t, D, T):   # pánico: mi fortuna + el guajolote se come el banco
    cam = Cam(560, 1560, 1.02)
    dr = Lienzo(cam)
    cielo(dr, t, top=(255, 150, 60), bot=(255, 230, 140), sol=(860, 300), solr=200, solc=(255, 250, 210))
    volcanes(dr, 1070); lago(dr, t, 1060, 200)
    dr.rrect(-700, 1250, 1800, 2700, 0, (214, 196, 160))
    dr.ell(540, 1980, 700, 110, CHOC_D)
    for k in range(6): dr.ell(120 + k * 170, 1960 + 20 * math.sin(t * 3 + k), 60, 14, CHOC_L, nolin=True)
    # caja de "BANCO" con chocolate derretido
    dr.rrect(540, 1640, 880, 1900, 14, (150, 96, 56), shade=True)
    dr.rrect(520, 1610, 900, 1660, 10, (120, 76, 44))
    dr.text(710, 1760, "BANCO", 64, (250, 230, 190), f=F_SERIF)
    dr.ell(710, 1640, 160, 30, CHOC_D)
    peck = abs(math.sin(t * 6)) if t > tl(9, 0.5) else 0
    guajolote(dr, 920, 1660, 0.6, t, face=-1, peck=0.4 + 0.6 * peck, choc=True)
    nico(dr, 260, 1990, 0.72, t, traje="azteca", arms=(165, 165), elbows=(30, 30), expr="shock", mouth=boca(9, t), look=(0.8, 0) if t > tl(9, 0.5) else (0, -0.3), sweat=True)
    f_ = tinta(dr); img = acabado(f_, T)
    if t > tl(9, 0.55): burst(img, "¡ÑAM!", 760, 1300, 120, t - tl(9, 0.55), col=(255, 214, 10), ang=10)
    return img, 0

@shot
def s11(t, D, T):   # cartel: 1.ª crisis económica de chocolate + pregunta
    cam = Cam(540, 1150 + 150, 1.05)
    dr = Lienzo(cam)
    cielo(dr, t, top=(220, 110, 120), bot=(255, 190, 120), sol=(540, 1050)); volcanes(dr, 1100); lago(dr, t, 1090, 160)
    templo(dr, 540, 1250, 0.7)
    dr.rrect(-700, 1250, 1800, 2700, 0, (214, 196, 160)); dr.ell(540, 1980, 700, 90, CHOC_D)
    nico(dr, 300, 2050, 0.68, t, traje="azteca", arms=(20, 20), expr="nervous", look=(0.6, 0))
    guajolote(dr, 820, 2060, 0.72, t, face=-1, peck=0.1, choc=True)
    f_ = tinta(dr); img = acabado(f_, T)
    d = ImageDraw.Draw(img)
    k = eob(t / 0.3)
    d.rounded_rectangle([90, 300, 990, 470], radius=30, fill=(250, 240, 210), outline=INK, width=8)
    d.text((540, 350), "1.ª CRISIS ECONÓMICA", font=font(56 * k + 1), fill=(120, 50, 30), anchor="mm")
    d.text((540, 425), "…DE CHOCOLATE", font=font(56 * k + 1), fill=CHOC, anchor="mm")
    if t > tl(10, 0.55):
        k = eob((t - tl(10, 0.55)) / 0.3)
        d.rounded_rectangle([110, 520, 970, 730], radius=36, fill=(255, 214, 10), outline=INK, width=8)
        d.text((540, 585), "¿QUÉ NEGOCIO", font=font(68 * k + 1), fill=INK, anchor="mm")
        d.text((540, 670), "LLEVO A OTRA ÉPOCA?", font=font(60 * k + 1), fill=INK, anchor="mm")
    return img, 0

@shot
def s12(t, D, T):   # cierre con portal
    cam = Cam(540, 1080 + 300, 1.0)
    dr = Lienzo(cam, bg=(18, 10, 30)); ciudad(dr, t)
    o = 1 - ease((t - D + 1.0) / 0.8)
    portal(dr, 540, 1350, 300, t, o)
    if t < D - 1.2:
        info = nico(dr, 540, 1900, 0.62, t, traje="azteca", arms=(150, 20), elbows=(30, 0), expr="happy", mouth=boca(11, t))
        hx, hy = info["hands"][1]; barra(dr, hx + 10, hy - 20, 120, 60, bite=1.0)
    f_ = tinta(dr); add_glow(f_, *cam.p(540, 1350), 420, (150, 120, 255), 0.5 * o)
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
    # música "azteca": tambor grave (huéhuetl), teponaztli de dos tonos, flauta pentatónica, 104 bpm
    e8 = 60 / 104 / 2
    mel = [69, 72, 74, 76, 74, 72, 69, None, 67, 69, 72, 74, 72, 69, 67, None]
    k = 0; s = STARTS[1]
    while s < STARTS[11]:
        if k % 4 == 0:
            x = seg(0.35); add(s, 0.16 * np.exp(-x * 9) * np.sin(2 * np.pi * (90 - 30 * x) * x))
        if k % 4 == 3:
            x = seg(0.2); add(s, 0.08 * np.exp(-x * 14) * np.sin(2 * np.pi * 110 * x))
        x = seg(0.12); add(s, 0.05 * np.exp(-x * 30) * np.sin(2 * np.pi * (520 if (k // 2) % 2 else 390) * x))
        m = mel[(k // 2) % len(mel)]
        if k % 2 == 0 and m is not None and STARTS[3] < s < STARTS[8] + DURS[8] * 0.6 or (k % 2 == 0 and m is not None and s > STARTS[10]):
            x = seg(e8 * 1.8); f0 = hz(m + 12)
            add(s, 0.025 * (np.sin(2 * np.pi * f0 * x + 0.3 * np.sin(2 * np.pi * 5 * x)) + 0.3 * np.sin(4 * np.pi * f0 * x)) * np.sin(np.pi * x / (e8 * 1.8)))
        k += 1; s += e8
    S_ = STARTS
    for s0 in S_[1:-1]:
        x = seg(0.3); add(s0, 0.2 * wh[int(s0 * sr):int(s0 * sr) + len(x)] * np.sin(np.pi * x / 0.3) ** 2)
    x = seg(1.2); add(S_[1] + 0.2, 0.12 * np.sin(2 * np.pi * (200 + 600 * x) * x) * np.sin(np.pi * x / 1.2))
    x = seg(0.5); add(0.9, 0.15 * np.exp(-x * 5) * (np.sin(2 * np.pi * 784 * x) + np.sin(2 * np.pi * 988 * x)))
    for kk in range(int(DURS[0] / 0.25)): add(kk * 0.25 + 0.1, 0.04 * np.exp(-seg(0.2) * 15) * bp(2000, 6000)[kk * 1000:kk * 1000 + int(0.2 * sr)])
    x = seg(0.4); add(S_[2] + tl(2, 0.25), 0.15 * np.exp(-x * 6) * np.sin(2 * np.pi * (600 + 500 * x) * x))
    x = seg(0.6); add(S_[3] + tl(3, 0.78), 0.18 * np.exp(-x * 5) * bp(1500, 5000)[:len(x)])
    for kk in range(12):
        x = seg(0.08); add(S_[4] + tl(4, 0.3) + kk * DURS[4] * 0.04, 0.12 * np.exp(-x * 50) * np.sin(2 * np.pi * 1800 * x))
    x = seg(0.8); add(S_[5] + tl(5, 0.65), 0.3 * np.exp(-x * 3) * np.sin(2 * np.pi * (500 - 300 * x) * x))
    for kk in range(10):
        x = seg(0.1); add(S_[5] + tl(5, 0.65) + kk * 0.09, 0.08 * np.exp(-x * 40) * np.sin(2 * np.pi * (1400 + kk * 60) * x))
    x = seg(1.0); add(S_[6] + tl(6, 0.6), 0.2 * np.exp(-x * 2) * (np.sin(2 * np.pi * 659 * x) + np.sin(2 * np.pi * 784 * x)))
    x = seg(0.7); add(S_[7] + 0.1, 0.15 * np.sin(2 * np.pi * (300 + 250 * np.sin(2 * np.pi * 14 * x)) * x) * np.exp(-x * 3))
    x = seg(1.0); add(S_[8] + 0.2, 0.2 * np.exp(-x * 2) * (np.sin(2 * np.pi * 1047 * x) + np.sin(2 * np.pi * 1319 * x)))
    x = seg(2.5); add(S_[8] + tl(8, 0.62), 0.25 * bp(80, 400)[:len(x)] * np.exp(-x * 0.8) + 0.12 * np.sin(2 * np.pi * (300 - 200 * x / 2.5) * x) * np.exp(-x))
    x = seg(1.0); add(S_[9] + tl(9, 0.55), 0.2 * bp(200, 900)[:len(x)] * (np.sin(2 * np.pi * 7 * x) > 0) * np.exp(-x * 2))
    x = seg(1.4); add(S_[10] + 0.1, 0.22 * np.exp(-x * 1.3) * np.sin(2 * np.pi * (392 - 120 * x) * x))
    x = seg(1.0); add(S_[11] + DURS[11] - 0.9, 0.12 * np.sin(2 * np.pi * (300 + 600 * x) * x) * np.sin(np.pi * x))
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
        sheet.save("sheet_eg.png"); print("TOTAL", round(TOTAL, 2), [round(s, 2) for s in STARTS]); sys.exit()
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
