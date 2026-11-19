#!/usr/bin/env python3
"""¿Qué pasaría si abres un SPA en el Viejo Oeste? — 08:00 del 2026-11-19 (estilo vector + cómic)."""
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
DURS[0] += 0.4; DURS[1] += 0.5; DURS[6] += 0.3; DURS[8] += 0.5; DURS[9] += 0.8; DURS[10] += 1.2
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
    [("¿Qué pasaría si", []), ("abres un SPA…", ["SPA…"]), ("en el Viejo Oeste?", ["Oeste?"])],
    [("Nico cruza el portal", ["portal"]), ("y aparece en un", []), ("pueblo vaquero", ["vaquero"]), ("del año 1880", ["1880"])],
    [("Forastero…", ["Forastero…"]), ("este pueblo no es", []), ("para debiluchos", ["debiluchos"])],
    [("¡Relájate, vaquero!", ["vaquero!"]), ("Mascarilla de pepino", ["pepino"]), ("masaje…", ["masaje…"]), ("¡y agua calientita!", ["calientita!"])],
    [("Dato real:", ["real:"]), ("en el Viejo Oeste", []), ("un baño caliente", ["baño"]), ("costaba unos 25 centavos…", ["25"]), ("y varios vaqueros", []), ("usaban la MISMA agua", ["MISMA"])],
    [("El spa de Nico", []), ("se llena:", ["llena:"]), ("vaqueros con pepinos", ["pepinos"]), ("en los ojos", [])],
    [("Pero al mediodía", ["mediodía"]), ("hay un DUELO…", ["DUELO…"]), ("y los dos están", []), ("demasiado relajados", ["relajados"])],
    [("¿Duelo?", ["¿Duelo?"]), ("Mmm…", []), ("mejor otra mascarilla", ["mascarilla"])],
    [("¿En serio?", []), ("¿Hasta el CABALLO", ["CABALLO"]), ("quiere mascarilla?", ["mascarilla?"])],
    [("Y así el Salvaje Oeste…", ["Salvaje"]), ("se volvió el", []), ("RELAJADO Oeste", ["RELAJADO"]), ("¿Qué negocio llevo", ["negocio"]), ("a otra época?", ["época?"]), ("¡Coméntalo!", ["¡Coméntalo!"])],
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


# ------------------------------------------------------------ escenarios del Viejo Oeste
SAND, SAND_D = (226, 180, 120), (204, 156, 100)
def cielo(dr, t, top=(250, 150, 80), bot=(255, 224, 150), sol=(880, 380)):
    for k in range(6):
        u = k / 5; c = tuple(int(lerp(top[i], bot[i], u)) for i in range(3))
        dr.rrect(-600, -900 + k * 380, 1700, -900 + (k + 1) * 380 + 2, 0, c, nolin=True)
    if sol: dr.ell(sol[0], sol[1], 120, 120, (255, 246, 200), nolin=True)
    for k, (x, y, s) in enumerate(((150, 230, 1.0), (760, 140, 1.2))):
        xx = (x + t * 10 * s) % 1500 - 200
        for (a, b, r) in ((-60, 10, 50), (0, -14, 66), (64, 10, 50)):
            dr.ell(xx + a * s, y + b * s, r * s, r * 0.5 * s, (255, 236, 210), nolin=True)

def mesas(dr, gy=1180):
    for (x0, w, h, c, cd) in ((-300, 520, 330, (196, 104, 70), (160, 80, 56)), (420, 380, 230, (206, 116, 76), (170, 88, 60)), (860, 560, 380, (190, 98, 66), (150, 74, 52))):
        dr.poly([(x0, gy), (x0 + 60, gy - h), (x0 + w - 60, gy - h), (x0 + w, gy)], c)
        dr.poly([(x0 + w * 0.55, gy - h), (x0 + w - 60, gy - h), (x0 + w, gy), (x0 + w * 0.62, gy)], cd, nolin=True)
    dr.rrect(-600, gy - 10, 1700, gy + 60, 0, (214, 160, 104))

def cactus(dr, x, y, s=1.0):
    S = lambda v: v * s; g, gd = (96, 160, 80), (70, 128, 62)
    dr.rrect(x - S(40), y - S(420), x + S(40), y, S(40), g, shade=True)
    dr.rrect(x - S(150), y - S(300), x - S(90), y - S(140), S(30), g)
    dr.rrect(x - S(150), y - S(180), x - S(30), y - S(130), S(25), g)
    dr.rrect(x + S(90), y - S(350), x + S(150), y - S(210), S(30), g)
    dr.rrect(x + S(30), y - S(250), x + S(150), y - S(200), S(25), g)
    for k in range(5): dr.line([(x - S(10), y - S(380) + k * S(70)), (x + S(10), y - S(370) + k * S(70))], gd, S(5), nolin=True)

def fachada(dr, x0, x1, base, h, col, rot, sign=None, sign_col=(240, 220, 170), txt_col=(110, 50, 30)):
    dr.rrect(x0, base - h, x1, base, 4, col, shade=True)
    for k in range(int((x1 - x0) / 40)): dr.line([(x0 + k * 40, base - h), (x0 + k * 40, base)], tuple(int(v * 0.85) for v in col), 3, nolin=True)
    dr.rrect(x0 - 10, base - h - 70, x1 + 10, base - h + 10, 4, col)
    dr.rrect(x0 - 20, base - 200, x1 + 20, base - 180, 4, tuple(int(v * 0.7) for v in col))
    for px in (x0, x1): dr.line([(px, base - 190), (px, base)], tuple(int(v * 0.7) for v in col), 12)
    w = x1 - x0
    dr.rrect(x0 + w * 0.15, base - h + 60, x0 + w * 0.42, base - h + 170, 4, (60, 50, 60))
    dr.rrect(x0 + w * 0.58, base - h + 60, x0 + w * 0.85, base - h + 170, 4, (60, 50, 60))
    dr.rrect(x0 + w * 0.35, base - 170, x0 + w * 0.65, base, 4, tuple(int(v * 0.6) for v in col))
    if sign:
        dr.rrect(x0 + 20, base - h - 60, x1 - 20, base - h, 6, sign_col)
        dr.text((x0 + x1) / 2, base - h - 30, sign, min(56, (w - 60) / max(3, len(sign)) * 1.6), txt_col, f=F_SERIF)

def calle(dr, t, gy=1250, spa=False):
    cielo(dr, t); mesas(dr, gy - 60)
    fachada(dr, -260, 160, gy, 520, (176, 120, 76), None, "SALOON")
    fachada(dr, 220, 560, gy, 440, (150, 104, 70), None, "BANCO")
    fachada(dr, 620, 1000, gy, 500, (120, 150, 160) if spa else (186, 140, 90), None, "SPA NICO" if spa else "BARBERÍA", (40, 186, 204) if spa else (240, 220, 170), (255, 255, 255) if spa else (110, 50, 30))
    dr.rrect(-600, gy, 1700, 2700, 0, SAND)
    for k in range(9):
        yy = gy + 30 + k * k * 12 + k * 26
        dr.line([(-600, yy), (1700, yy + 10)], SAND_D, 4, nolin=True)

def tumbleweed(dr, x, y, r, t):
    a = t * 6
    dr.ell(x, y, r, r, (170, 130, 80), nolin=True)
    for k in range(6):
        aa = a + k * 1.05
        dr.line([(x + math.cos(aa) * r, y + math.sin(aa) * r), (x - math.cos(aa + 0.5) * r, y - math.sin(aa + 0.5) * r)], (120, 86, 50), max(3, r * 0.08), nolin=True)

def pepino(dr, x, y, r):
    dr.ell(x, y, r, r, (110, 170, 80)); dr.ell(x, y, r * 0.75, r * 0.75, (200, 230, 160), nolin=True)
    for k in range(5):
        a = k * 1.256; dr.ell(x + math.cos(a) * r * 0.4, y + math.sin(a) * r * 0.4, r * 0.08, r * 0.12, (240, 250, 220), nolin=True)

def vaquero(dr, x, y, s, t, hat=(40, 34, 36), vest=(60, 50, 50), shirt=(120, 110, 150), mouth=0.0, expr="angry", arms=(20, 20),
            mask=False, pepinos=False, toalla=False, star=False, stache=(60, 40, 30), look=(0, 0), skin=(232, 178, 130), bata=False):
    S = lambda v: v * s
    bob = S(5) * math.sin(t * 2.0)
    for sx in (-1, 1):
        dr.rrect(x + sx * S(45) - S(24), y - S(260), x + sx * S(45) + S(24), y - S(20), S(12), (70, 70, 100) if not bata else (250, 250, 250))
        dr.poly([(x + sx * S(45) - S(30), y - S(90)), (x + sx * S(45) + S(30), y - S(90)), (x + sx * S(45) + S(34), y), (x + sx * S(45) - S(50) * (sx < 0) - S(20), y)], (110, 66, 34))
    body = (250, 250, 250) if bata else shirt
    dr.rrect(x - S(140), y - S(560) + bob, x + S(140), y - S(240), S(80), body, shade=True)
    if not bata:
        for sx in (-1, 1): dr.poly([(x + sx * S(40), y - S(555) + bob), (x + sx * S(140), y - S(520) + bob), (x + sx * S(140), y - S(250)), (x + sx * S(50), y - S(250))], vest)
        dr.rrect(x - S(140), y - S(290), x + S(140), y - S(250), S(8), (80, 50, 30)); dr.rrect(x - S(30), y - S(298), x + S(30), y - S(242), S(6), (230, 190, 60))
        if star:
            cx, cy = x - S(80), y - S(440) + bob
            dr.poly([(cx + math.cos(math.pi / 2 + k * math.pi / 5) * S(40 if k % 2 == 0 else 17) * -1, cy - math.sin(math.pi / 2 + k * math.pi / 5) * S(40 if k % 2 == 0 else 17)) for k in range(10)], (240, 200, 60))
    else:
        dr.poly([(x - S(30), y - S(555) + bob), (x + S(60), y - S(400)), (x + S(20), y - S(250)), (x - S(10), y - S(250))], (230, 230, 236), nolin=True)
        dr.rrect(x - S(140), y - S(380), x + S(140), y - S(350), S(8), TURQ)
    hands = []
    for sx, a in ((-1, arms[0]), (1, arms[1])):
        shx, shy = x + sx * S(120), y - S(520) + bob
        ar = math.radians(a); hx_, hy_ = shx + sx * math.sin(ar) * S(220), shy + math.cos(ar) * S(220)
        dr.line([(shx, shy), (hx_, hy_)], body, S(56)); dr.ell(hx_, hy_, S(32), S(32), skin); hands.append((hx_, hy_))
    hx, hy = x, y - S(720) + bob
    dr.ell(hx, hy, S(160), S(155), skin, shade=True)
    if mask:
        dr.ell(hx, hy + S(10), S(140), S(130), (150, 210, 130), nolin=False)
    dr.ell(hx, hy + S(40), S(36), S(32), tuple(int(v * 0.88) for v in ((150, 210, 130) if mask else skin)))
    if pepinos:
        for sx in (-1, 1): pepino(dr, hx + sx * S(60), hy - S(20), S(46))
    else:
        if (t % 3.1) < 0.12 or expr == "sleepy":
            for sx in (-1, 1): dr.chord(hx + sx * S(60), hy - S(25), S(30), S(18), 0, 180, INK)
        else:
            for sx in (-1, 1):
                ex, ey = hx + sx * S(60), hy - S(25)
                big = 1.25 if expr == "shock" else 1.0
                dr.ell(ex, ey, S(30) * big, S(34) * big, (255, 255, 255)); dr.ell(ex + look[0] * S(9), ey + look[1] * S(9), S(14), S(17), INK)
                tilt = {"angry": 22, "happy": -8, "shock": -14}.get(expr, 0) * sx
                dr.line([(ex - S(36), ey - S(50) + S(tilt) * 0.5), (ex + S(36), ey - S(50) - S(tilt) * 0.5)], (60, 40, 30), S(14))
    mo = clamp(mouth)
    if mo > 0.06: dr.ell(hx, hy + S(100), S(40), S(8 + 30 * mo), (110, 30, 40))
    elif expr in ("happy", "sleepy"): dr.chord(hx, hy + S(86), S(40), S(26), 0, 180, (110, 30, 40))
    else: dr.line([(hx - S(34), hy + S(104)), (hx + S(34), hy + S(98))], (110, 30, 40), S(9))
    if stache:
        for sx in (-1, 1): dr.poly([(hx, hy + S(70)), (hx + sx * S(90), hy + S(72)), (hx + sx * S(120), hy + S(110)), (hx + sx * S(70), hy + S(92))], stache)
    if toalla:
        dr.ell(hx, hy - S(120), S(170), S(90), (250, 250, 250)); dr.ell(hx, hy - S(190), S(120), S(60), (250, 250, 250))
        dr.rrect(hx - S(168), hy - S(110), hx + S(168), hy - S(88), S(8), TURQ, nolin=True)
    else:
        dr.ell(hx, hy - S(110), S(270), S(50), hat, shade=True)
        dr.poly([(hx - S(150), hy - S(110)), (hx - S(130), hy - S(270)), (hx, hy - S(240)), (hx + S(130), hy - S(270)), (hx + S(150), hy - S(110))], hat)
        dr.rrect(hx - S(150), hy - S(160), hx + S(150), hy - S(130), S(6), tuple(min(255, int(v * 1.6) + 30) for v in hat))
    return dict(head=(hx, hy), hands=hands)

def tina(dr, x, y, s, t, agua=(120, 200, 230), burb=True):
    S = lambda v: v * s
    dr.rrect(x - S(240), y - S(260), x + S(240), y, S(40), (150, 96, 56), shade=True)
    for k in range(-3, 4): dr.line([(x + k * S(64), y - S(250)), (x + k * S(64), y - S(10))], (120, 76, 44), S(5), nolin=True)
    for yy in (60, 200): dr.rrect(x - S(244), y - S(yy) - S(14), x + S(244), y - S(yy) + S(14), S(6), (110, 110, 120))
    dr.ell(x, y - S(260), S(240), S(40), agua)
    if burb:
        for k in range(7):
            ph = (t * 0.7 + k * 0.17) % 1
            dr.ell(x - S(200) + k * S(66), y - S(280) - ph * S(60), S(18) * (1 - ph * 0.5), S(18) * (1 - ph * 0.5), (250, 250, 255), nolin=True)

def tina_front(dr, x, y, s, agua=(120, 200, 230)):
    S = lambda v: v * s
    dr.rrect(x - S(250), y - S(200), x + S(250), y, S(40), (150, 96, 56), shade=True)
    for k in range(-3, 4): dr.line([(x + k * S(64), y - S(190)), (x + k * S(64), y - S(10))], (120, 76, 44), S(5), nolin=True)
    dr.rrect(x - S(254), y - S(80) - S(14), x + S(254), y - S(80) + S(14), S(6), (110, 110, 120))
    dr.rrect(x - S(258), y - S(214), x + S(258), y - S(186), S(10), agua)

def espuma(dr, x, y, s, t):
    for k in range(9):
        dr.ell(x - s * 220 + k * s * 55, y + s * 6 * math.sin(t * 3 + k), s * 44, s * 30, (250, 252, 255), nolin=True)

# ------------------------------------------------------------ planos
SHOTS = []
def shot(fn): SHOTS.append(fn); return fn
def tl(k, frac): return LEAD + len(VOZ[k]) / SR * frac
POLVO = dict(hat=(40, 34, 36), vest=(60, 50, 50), shirt=(120, 100, 150), stache=(40, 30, 26))
RUSTY = dict(hat=(190, 150, 100), vest=(110, 70, 40), shirt=(80, 130, 90), stache=(200, 110, 60), skin=(244, 190, 150))

@shot
def s01(t, D, T):   # gancho: Nico vaquero en tina con mascarilla y pepinos frente a un cactus
    cam = Cam(540, 1080 - t * 15 + 320, 1.15 + t * 0.03)
    dr = Lienzo(cam); cielo(dr, t); mesas(dr, 1150)
    dr.rrect(-600, 1150, 1700, 2700, 0, SAND)
    cactus(dr, 140, 1400, 0.9); cactus(dr, 960, 1300, 0.6)
    tina(dr, 540, 1820, 1.25, t)
    info = nico(dr, 540, 1880, 0.62, t, traje="vaquero", arms=(150, 150), elbows=(40, 40), expr="happy_eyes")
    hx, hy = info["head"]
    for sx in (-1, 1): pepino(dr, hx + sx * 43, hy + 6, 30)
    tina_front(dr, 540, 1850, 1.25); espuma(dr, 540, 1610, 1.3, t)
    f_ = tinta(dr); img = acabado(f_, T)
    if t > 0.9: burst(img, "SPA", 540, 470, 190, t - 0.9, col=(90, 236, 255), ang=-7)
    return img, 0

@shot
def s02(t, D, T):   # portal → calle del pueblo vaquero
    cam = Cam(540, 1080 + 200, 1.0)
    dr = Lienzo(cam); calle(dr, t)
    o = ease(t / 0.4) * (1 - ease((t - 2.4) / 0.4))
    portal(dr, 300, 1430, 210, t, o)
    tumbleweed(dr, (t * 320) % 1600 - 200, 1820 - abs(math.sin(t * 5)) * 60, 70, t)
    u = clamp((t - 0.5) / 0.8)
    if t > 0.5:
        nico(dr, lerp(300, 560, eob(u)), 1880, 0.68, t, traje="vaquero", arms=(30, 150) if t > 2 else (20, 20), elbows=(0, 30), expr="shock" if t < 1.8 else "happy", look=(0.6, -0.3))
    f_ = tinta(dr); img = acabado(f_, T)
    if t > 1.6: cartel(img, t - 1.6, "VIEJO OESTE", "AÑO 1880", y=430)
    return img, 0

@shot
def s03(t, D, T):   # Polvo: forastero, este pueblo no es para debiluchos
    cam = Cam(540, 1060 - t * 20 + 60, 1.45 + t * 0.04)
    dr = Lienzo(cam); calle(dr, t)
    vaquero(dr, 560, 1880, 1.0, t, mouth=boca(2, t), expr="angry", arms=(25, 40), look=(-0.5, 0), **POLVO)
    tumbleweed(dr, 1100 - t * 260, 1820, 60, -t)
    f_ = tinta(dr); img = acabado(f_, T)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([50, 300, 420, 380], radius=18, fill=(250, 240, 210), outline=INK, width=6)
    d.text((235, 340), "POLVO · bandido", font=font(40), fill=(120, 40, 30), anchor="mm")
    return img, 0

@shot
def s04(t, D, T):   # Nico ofrece el spa: mascarilla de pepino, masaje, agua caliente
    cam = Cam(540, 1080 + 350, 1.25)
    dr = Lienzo(cam, bg=(0, 0, 0)); calle(dr, t, spa=True)
    vaquero(dr, 200, 1980, 0.85, t, expr="shock" if t > tl(3, 0.4) else "angry", arms=(20, 20), look=(1, 0), **POLVO)
    info = nico(dr, 660, 1900, 0.66, t, traje="vaquero", arms=(20, 110), elbows=(0, -50), expr="happy", mouth=boca(3, t), look=(-0.6, 0))
    hx, hy = info["hands"][1]
    if t > tl(3, 0.3): pepino(dr, hx + 10, hy - 50, 50)
    f_ = tinta(dr); img = acabado(f_, T)
    items = [("🥒 MASCARILLA", 0.3), ("💆 MASAJE", 0.55), ("♨ AGUA CALIENTE", 0.75)]
    d = ImageDraw.Draw(img)
    for k, (txt, fr) in enumerate((("MASCARILLA", 0.3), ("MASAJE", 0.55), ("AGUA CALIENTE", 0.75))):
        if t > tl(3, fr):
            kk = eob((t - tl(3, fr)) / 0.25); y = 300 + k * 110
            d.rounded_rectangle([560, y, 560 + 460 * kk + 1, y + 90], radius=20, fill=TURQ, outline=INK, width=6)
            if kk > 0.6: d.text((790, y + 45), "✓ " + txt if False else txt, font=font(44), fill=(255, 255, 255), anchor="mm", stroke_width=4, stroke_fill=INK)
    return img, 0

def barberia(dr, t):
    dr.rrect(-600, -900, 1700, 2700, 0, (150, 100, 66))
    for k in range(-6, 14): dr.line([(k * 110, -900), (k * 110, 1300)], (130, 86, 56), 5, nolin=True)
    dr.rrect(-600, 1300, 1700, 2700, 0, (120, 80, 52))
    for k in range(8): dr.line([(-600, 1340 + k * 90), (1700, 1340 + k * 90)], (100, 66, 42), 4, nolin=True)
    dr.rrect(620, 820, 980, 1040, 10, (240, 226, 190))
    dr.text(800, 880, "BAÑO", 56, (110, 50, 30), f=F_SERIF)
    dr.text(800, 970, "25¢", 80, (200, 50, 40))

@shot
def s05(t, D, T):   # dato real: baño 25 centavos y la misma agua para varios vaqueros
    cam = Cam(540, 1100 + 300, 1.1)
    dr = Lienzo(cam); barberia(dr, t)
    n = min(4, 1 + int(t / (D / 4.2)))
    dark = clamp((n - 1) / 3)
    agua = tuple(int(lerp(a, b, dark)) for a, b in zip((120, 200, 230), (120, 92, 50)))
    for k in range(4 - n):
        vaquero(dr, 120 + k * 160 - 80, 1700, 0.55, t + k, expr="happy", arms=(15, 15), **(RUSTY if k % 2 else POLVO))
    tina(dr, 680, 1900, 1.15, t, agua=agua, burb=False)
    vaquero(dr, 680, 2010, 0.8, t, expr="happy" if n < 3 else "shock", arms=(140, 140), **(POLVO if n % 2 else RUSTY))
    tina_front(dr, 680, 1930, 1.15, agua=agua)
    for k in range(int(dark * 6)):
        ph = (t * 0.6 + k * 0.2) % 1
        dr.line([(560 + k * 50, 1600 - ph * 120), (575 + k * 50, 1560 - ph * 120), (560 + k * 50, 1520 - ph * 120)], (110, 140, 60), 7, nolin=True)
    f_ = tinta(dr); img = acabado(f_, T)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([60, 300, 420, 420], radius=22, fill=(255, 214, 10), outline=INK, width=7)
    d.text((240, 360), f"VAQUERO #{n}", font=font(52), fill=INK, anchor="mm")
    if n >= 3: burst(img, "¡PUAJ!", 300, 560, 120, t - (D / 4.2) * 2, col=(160, 220, 90), ang=-8)
    return img, 0

@shot
def s06(t, D, T):   # el spa se llena: fila de vaqueros en tinas con pepinos
    cam = Cam(540 + t * 40, 1150 + 250, 1.0)
    dr = Lienzo(cam); dr.rrect(-600, -900, 1800, 2700, 0, (190, 226, 222))
    for k in range(-6, 16): dr.line([(k * 110, -900), (k * 110, 1300)], (170, 208, 204), 5, nolin=True)
    dr.rrect(-600, 1300, 1800, 2700, 0, (236, 228, 214))
    dr.rrect(200, 700, 880, 860, 20, TURQ); dr.text(540, 780, "SPA NICO", 96, (255, 255, 255), stroke=6)
    for k, (x, sty) in enumerate(((150, POLVO), (540, RUSTY), (930, POLVO), (1300, RUSTY))):
        tina(dr, x, 1800, 0.8, t + k, burb=True)
        vaquero(dr, x, 1900, 0.6, t + k * 0.7, expr="happy", arms=(150, 150), mask=True, pepinos=True, toalla=(k % 2 == 0), **sty)
        tina_front(dr, x, 1820, 0.8); espuma(dr, x, 1660, 0.8, t + k)
    nico(dr, 1060 + t * 40, 2080, 0.5, t, traje="vaquero", arms=(20, 140), elbows=(0, 20), expr="happy")
    f_ = tinta(dr); img = acabado(f_, T)
    burst(img, "¡LLENO!", 540, 590, 130, t - 0.4, ang=6)
    return img, 0

@shot
def s07(t, D, T):   # duelo al mediodía: los dos relajados con toalla y mascarilla
    cam = Cam(540, 1150 + 250, 1.0 + 0.05 * t)
    dr = Lienzo(cam); calle(dr, t, spa=True)
    dr.rrect(470, 620, 610, 800, 6, (150, 104, 70)); dr.ell(540, 660, 60, 60, (250, 250, 240))
    dr.line([(540, 660), (540, 615)], INK, 7, nolin=True); dr.line([(540, 660), (542, 620)], INK, 5, nolin=True)
    tumbleweed(dr, (t * 240) % 1500 - 200, 1950, 70, t)
    yawn = (t % 2.0) > 1.2
    vaquero(dr, 200, 2000, 0.75, t, expr="sleepy", arms=(10, 10), mask=True, toalla=True, mouth=0.7 if yawn else 0, bata=True, **POLVO)
    vaquero(dr, 880, 2000, 0.75, t + 1, expr="sleepy", arms=(10, 10), mask=True, toalla=True, mouth=0.7 if not yawn else 0, bata=True, **RUSTY)
    f_ = tinta(dr); img = acabado(f_, T)
    burst(img, "12:00 · DUELO", 540, 300, 100, t - 0.2, col=(255, 90, 60), ang=-4)
    if t > tl(6, 0.7): burst(img, "zzz…", 860, 760, 90, t - tl(6, 0.7), col=(200, 230, 255), ang=8)
    return img, 0

@shot
def s08(t, D, T):   # Polvo (primer plano) relajado: ¿duelo? mejor otra mascarilla
    cam = Cam(540, 1080 + 150, 1.7 + t * 0.05)
    dr = Lienzo(cam); calle(dr, t, spa=True)
    vaquero(dr, 540, 1960, 1.0, t, mouth=boca(7, t), expr="sleepy", arms=(140, 20), mask=True, pepinos=t > tl(7, 0.55), toalla=True, bata=True, **POLVO)
    f_ = tinta(dr); img = acabado(f_, T)
    if t > tl(7, 0.6): burst(img, "AHHH…", 300, 420, 110, t - tl(7, 0.6), col=(160, 230, 140), ang=-8)
    return img, 0

@shot
def s09(t, D, T):   # ¿hasta el caballo quiere mascarilla?
    cam = Cam(540, 1150 + 350, 1.15)
    dr = Lienzo(cam); calle(dr, t, spa=True)
    tina(dr, 780, 1950, 1.3, t)
    pos = caballo(dr, 860, 1880, 1.0, t, face=-1)
    hx, hy = 860 - 300, 1880 - 600
    dr.ell(hx - 40, hy + 20, 92, 56, (150, 210, 130))
    pepino(dr, hx - 20, hy - 5, 34)
    dr.ell(hx - 110, hy + 35, 42, 38, (128, 82, 50)); dr.ell(hx - 128, hy + 30, 7, 9, INK, nolin=True)
    dr.chord(hx - 70, hy + 50, 30, 18, 0, 180, (110, 30, 40))
    dr.ell(hx + 10, hy - 100, 100, 50, (250, 250, 250)); dr.rrect(hx - 90, hy - 90, hx + 110, hy - 72, 6, TURQ, nolin=True)
    tina_front(dr, 780, 1980, 1.3); espuma(dr, 780, 1720, 1.25, t)
    nico(dr, 200, 1950, 0.66, t, traje="vaquero", arms=(150, 30), elbows=(30, 0), expr="shock" if t < tl(8, 0.5) else "happy", mouth=boca(8, t), look=(1, -0.3), sweat=True)
    f_ = tinta(dr); img = acabado(f_, T)
    if t > tl(8, 0.4): burst(img, "¡HIIII!", 640, 480, 110, t - tl(8, 0.4), ang=8)
    return img, 0

@shot
def s10(t, D, T):   # cartel: SALVAJE OESTE → RELAJADO OESTE + pregunta
    cam = Cam(540, 1150 + 150, 1.05)
    dr = Lienzo(cam); cielo(dr, t, top=(220, 110, 120), bot=(255, 190, 120), sol=(540, 1050)); mesas(dr, 1200)
    dr.rrect(-600, 1200, 1700, 2700, 0, SAND)
    cactus(dr, 950, 1500, 0.7)
    dr.line([(300, 1950), (300, 1100)], (110, 70, 40), 26); dr.line([(780, 1950), (780, 1100)], (110, 70, 40), 26)
    dr.rrect(160, 1080, 920, 1340, 14, (210, 160, 100), shade=True)
    flip = t > tl(9, 0.42)
    dr.text(540, 1160, "BIENVENIDO AL", 48, (110, 50, 30), f=F_SERIF)
    dr.text(540, 1260, "RELAJADO OESTE" if flip else "SALVAJE OESTE", 76, TURQ if flip else (170, 40, 30), stroke=4 if flip else 0)
    caballo(dr, 1250 - t * 120, 2150, 0.6, t, face=-1, walk=t * 8)
    nico(dr, 1250 - t * 120 + 20, 2150 - 450 * 0.6 + 200 * 0.6 - 60, 0.4, t, traje="vaquero", arms=(150, 20), elbows=(30, 0), expr="happy")
    f_ = tinta(dr); img = acabado(f_, T)
    if t > tl(9, 0.6):
        k = eob((t - tl(9, 0.6)) / 0.3); d = ImageDraw.Draw(img)
        d.rounded_rectangle([110, 360, 970, 570], radius=36, fill=(255, 214, 10), outline=INK, width=8)
        d.text((540, 425), "¿QUÉ NEGOCIO", font=font(68 * k + 1), fill=INK, anchor="mm")
        d.text((540, 510), "LLEVO A OTRA ÉPOCA?", font=font(60 * k + 1), fill=INK, anchor="mm")
    return img, 0

@shot
def s11(t, D, T):   # cierre con portal
    cam = Cam(540, 1080 + 300, 1.0)
    dr = Lienzo(cam, bg=(18, 10, 30)); calle(dr, t, spa=True)
    o = 1 - ease((t - D + 1.0) / 0.8)
    portal(dr, 540, 1350, 300, t, o)
    if t < D - 1.2:
        nico(dr, 540, 1880, 0.6, t, traje="vaquero", arms=(150, 20), elbows=(30, 0), expr="happy", mouth=boca(10, t))
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
    # música western (guitarra punteada + bajo galopante + silbido), la menor, 112 bpm
    e8 = 60 / 112 / 2
    mel = [69, 72, 76, 74, 72, 69, 67, 69, 64, 67, 69, 72, 71, 69, 67, 64]
    bass = [45, 52, 45, 52, 43, 50, 40, 47]
    k = 0; s = STARTS[1]
    while s < STARTS[10]:
        x = seg(e8 * 1.5); m = mel[k % len(mel)]
        if k % 2 == 0:
            f0 = hz(m); pl = sum((0.6 ** h) * np.sin(2 * np.pi * f0 * (h + 1) * x) for h in range(5))
            add(s, 0.03 * pl * np.exp(-x * 6))
        xb = seg(e8 * 0.9)
        add(s, 0.06 * np.exp(-xb * 6) * np.sin(2 * np.pi * hz(bass[(k // 2) % 8] + (12 if k % 2 else 0)) * xb))
        if k % 2 == 1: add(s, 0.05 * np.exp(-seg(0.06) * 60) * bp(800, 2500)[int(s * sr):int(s * sr) + int(0.06 * sr)])
        k += 1; s += e8
    S_ = STARTS
    # silbido del gancho
    x = seg(1.4); add(0.2, 0.06 * np.sin(2 * np.pi * (1200 + 500 * np.sin(np.pi * x / 1.4)) * x) * np.sin(np.pi * x / 1.4))
    for kk in range(int(DURS[0] / 0.25)): add(kk * 0.25 + 0.1, 0.04 * np.exp(-seg(0.2) * 15) * bp(2000, 6000)[kk * 1000:kk * 1000 + int(0.2 * sr)])
    for s0 in S_[1:-1]:
        x = seg(0.3); add(s0, 0.2 * wh[int(s0 * sr):int(s0 * sr) + len(x)] * np.sin(np.pi * x / 0.3) ** 2)
    x = seg(1.2); add(S_[1] + 0.2, 0.12 * np.sin(2 * np.pi * (200 + 600 * x) * x) * np.sin(np.pi * x / 1.2))
    x = seg(0.8); add(S_[2], 0.15 * bp(200, 900)[:len(x)] * np.exp(-x * 3))
    for kk, fr in enumerate((0.3, 0.55, 0.75)):
        x = seg(0.3); add(S_[3] + tl(3, fr), 0.15 * np.exp(-x * 10) * np.sin(2 * np.pi * (880 + kk * 220) * x))
    for kk in range(4):
        x = seg(0.5); add(S_[4] + kk * DURS[4] / 4.2, 0.15 * bp(300, 1500)[kk * 5000:kk * 5000 + len(x)] * np.exp(-x * 5))
    x = seg(0.5); add(S_[4] + DURS[4] / 4.2 * 2, 0.2 * np.exp(-x * 4) * np.sin(2 * np.pi * (300 - 200 * x) * x))
    x = seg(1.0); add(S_[5] + 0.4, 0.2 * np.exp(-x * 2) * (np.sin(2 * np.pi * 659 * x) + np.sin(2 * np.pi * 784 * x)))
    x = seg(1.5); add(S_[6], 0.25 * np.exp(-x * 1.2) * np.sin(2 * np.pi * 523 * x) * (1 + 0.3 * np.sin(2 * np.pi * 6 * x)))
    for kk in range(3): add(S_[6] + 0.1 + kk * 0.5, 0.18 * np.exp(-seg(0.3) * 12) * np.sin(2 * np.pi * 1000 * seg(0.3)))
    x = seg(1.0); add(S_[7] + tl(7, 0.6), 0.08 * bp(300, 1200)[:len(x)] * np.sin(np.pi * x))
    x = seg(0.9); add(S_[8] + tl(8, 0.4), 0.25 * np.sin(2 * np.pi * (700 + 300 * np.sin(2 * np.pi * 9 * x)) * x) * np.exp(-x * 2.5))
    for kk in range(int(DURS[9] / 0.3)):
        xs = seg(0.12); add(S_[9] + kk * 0.3, 0.15 * np.exp(-xs * 30) * bp(200, 1200)[int(kk * 3000):int(kk * 3000) + len(xs)])
    x = seg(0.6); add(S_[9] + tl(9, 0.42), 0.2 * np.exp(-x * 4) * (np.sin(2 * np.pi * 784 * x) + np.sin(2 * np.pi * 1047 * x)))
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
