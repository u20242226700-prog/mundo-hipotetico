#!/usr/bin/env python3
"""¿Qué pasaría si abres un GIMNASIO en plena era vikinga?
Estilo vector + cómic (motor/vc.py). Nico con traje VIKINGO (túnica roja, chaleco de piel, cinturón turquesa):
llega con casco de cuernos (el mito) y luego entrena con cinta y silbato turquesa.
Dato real: los vikingos no usaban cascos con cuernos; la imagen se popularizó con el vestuario de
El anillo del nibelungo de Wagner (Bayreuth, 1876, diseñador Carl Emil Doepler)."""
import math, os, sys, subprocess
import numpy as np
from PIL import Image, ImageDraw
from scipy.io import wavfile
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "motor"))
from vc import *
Canvas = D

FPS = 30
OUT = sys.argv[1] if len(sys.argv) > 1 else "video.mp4"
VOZ_DIR = os.path.join(HERE, "voz")
VOZ_F = sorted(f for f in os.listdir(VOZ_DIR) if f.endswith("_f.wav"))
VOZ = [wavfile.read(f"{VOZ_DIR}/{f}")[1].astype(np.float32) / 32768 for f in VOZ_F]
SR = 44100; LEAD = 0.1
DURS = [len(v) / SR + LEAD + 0.28 for v in VOZ]
DURS[0] += 0.3; DURS[8] += 0.6; DURS[12] += 0.5; DURS[13] += 0.9
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
    [("¿Y si abres", []), ("un GIMNASIO…", ["GIMNASIO…"]), ("en plena", []), ("era vikinga?", ["vikinga?"])],
    [("Nico cruza el portal", ["portal"]), ("y aparece en Noruega,", ["Noruega,"]), ("año 900…", ["900…"]), ("con su casco", []), ("de cuernos", ["cuernos"])],
    [("¿Cuernos?", ["¿Cuernos?"]), ("¡Ja, ja, ja!", []), ("¡Pareces", []), ("una cabra!", ["cabra!"])],
    [("Dato real:", ["real:"]), ("los vikingos", []), ("NUNCA usaron", ["NUNCA"]), ("cascos con cuernos", ["cuernos"]), ("Eso lo inventó", []), ("una ópera", ["ópera"]), ("en 1876", ["1876"])],
    [("Bueno…", []), ("¡Bienvenidos al", []), ("Gimnasio Nico!", ["Nico!"]), ("¡Primera clase", []), ("gratis!", ["gratis!"])],
    [("Levantaban rocas", ["rocas"]), ("y remaban días enteros…", ["remaban"]), ("pero nunca", []), ("habían visto", []), ("una mancuerna", ["mancuerna"])],
    [("¡Por Odín!", ["Odín!"]), ("¡Con estos brazos", ["brazos"]), ("llego remando", []), ("a Inglaterra!", ["Inglaterra!"])],
    [("En una semana", ["semana"]), ("todo el pueblo", []), ("está enorme", ["enorme"]), ("Demasiado", ["Demasiado"]), ("enorme", [])],
    [("Se suben al barco…", ["barco…"]), ("y el barco", []), ("se hunde", ["hunde"])],
    [("Eh…", []), ("¿y si hoy", []), ("hacemos cardio?", ["cardio?"])],
    [("Al día siguiente", []), ("Bjorn abrió", ["Bjorn"]), ("su propio gimnasio…", ["gimnasio…"]), ("y encontró", []), ("la pesa perfecta", ["perfecta"])],
    [("¡Miren!", ["¡Miren!"]), ("¡Esta pesa", []), ("habla!", ["habla!"])],
    [("¡Bájameee!", ["¡Bájameee!"])],
    [("Nos vemos en otro", []), ("mundo hipotético", ["hipotético"]), ("¿Qué negocio llevo", ["negocio"]), ("a la próxima época?", ["época?"])],
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
def mix(a, b, k): return tuple(int(lerp(a[i], b[i], k)) for i in range(3))

def cielo(dr, t, y_top=-900, tarde=0.0):
    c = [(70, 120, 190), (110, 156, 210), (170, 190, 220), (240, 196, 180)]
    c2 = [(60, 50, 110), (120, 70, 120), (220, 110, 100), (250, 170, 90)]
    for k in range(4):
        dr.rrect(-600, y_top + k * 460, 1700, y_top + (k + 1) * 460 + 4, 0, mix(c[k], c2[k], tarde))

def montanas(dr, base=900):
    for k, (cx, w, h, c1, c2) in enumerate([(-100, 900, 520, (110, 132, 170), (84, 102, 140)), (650, 1100, 640, (100, 122, 162), (76, 94, 132)), (1350, 900, 480, (110, 132, 170), (84, 102, 140))]):
        pk = base - h
        dr.poly([(cx - w / 2, base), (cx - 30, pk), (cx + 10, pk + 30), (cx - 10, base)], c1)
        dr.poly([(cx - 10, base), (cx + 10, pk + 30), (cx + 30, pk), (cx + w / 2, base)], c2, shade=True)
        dr.poly([(cx - w * 0.16, pk + h * 0.28), (cx - 30, pk), (cx + 30, pk), (cx + w * 0.17, pk + h * 0.3), (cx + w * 0.06, pk + h * 0.22), (cx, pk + h * 0.3), (cx - w * 0.07, pk + h * 0.21)], (240, 246, 252))

def agua(dr, t, y0=900, y1=1150):
    dr.rrect(-600, y0, 1700, y1, 0, (50, 96, 140))
    for r in range(5):
        for j in range(-4, 14):
            x = j * 140 + (r % 2) * 70 + 30 * math.sin(t * 1.2 + r)
            dr.rrect(x, y0 + 30 + r * 46, x + 70, y0 + 38 + r * 46, 4, (110, 160, 200), nolin=True)

def casa_larga(dr, x, gy, w, h, k=0):
    wood = [(130, 84, 50), (150, 98, 58), (116, 74, 44)][k % 3]
    dr.rrect(x, gy - h, x + w, gy, 0, wood, shade=True)
    for j in range(int(w / 40)):
        dr.line([(x + 20 + j * 40, gy - h + 6), (x + 20 + j * 40, gy - 6)], (96, 60, 36), 5)
    dr.poly([(x - 40, gy - h + 10), (x + w / 2, gy - h - h * 0.75), (x + w + 40, gy - h + 10)], (96, 140, 70))
    dr.poly([(x + w / 2, gy - h - h * 0.75), (x + w + 40, gy - h + 10), (x + w / 2, gy - h + 10)], (74, 112, 56), shade=True)
    for sx in (-1, 1):   # cabezas de dragón en el techo
        ex = x + w / 2 + sx * 30
        dr.line([(ex, gy - h - h * 0.72), (ex + sx * 50, gy - h - h * 0.95), (ex + sx * 85, gy - h - h * 0.9)], (110, 70, 40), 16)
    dr.rrect(x + w * 0.42, gy - h * 0.62, x + w * 0.58, gy, 20, (60, 36, 24))

def pueblo(dr, t, gy=1380, tarde=0.0, casas=True):
    cielo(dr, t, tarde=tarde)
    montanas(dr, 930)
    agua(dr, t, 930, 1120)
    dr.rrect(-600, 1120, 1700, gy, 0, (110, 150, 80))
    if casas:
        for k, (x, w, h) in enumerate([(-380, 420, 230), (110, 380, 210), (560, 460, 250), (1090, 400, 220)]):
            casa_larga(dr, x, gy - 20 + (k % 2) * 20, w, h, k)
    dr.rrect(-600, gy, 1700, 2700, 0, (126, 104, 74))
    rng = np.random.default_rng(5)
    for k in range(40):
        x = rng.uniform(-500, 1600); y = gy + 30 + rng.uniform(0, 1) ** 2 * 700
        dr.ell(x, y, 24 + y * 0.01, 8 + y * 0.004, (106, 86, 60))

def portal(dr, x, y, r, t, o=1.0):
    R = r * o
    if R < 4: return
    dr.ell(x, y, R, R * 1.18, (40, 16, 70), nolin=True)
    for k in range(7):
        rr = R * (1 - k * 0.12); a0 = (t * (160 + 30 * k) * (1 if k % 2 else -1)) % 360
        X, Y = dr.cam.p(x, y); rx, ry = dr.cam.s(rr), dr.cam.s(rr * 1.18)
        dr.d.arc([X - rx, Y - ry, X + rx, Y + ry], a0, a0 + 240, fill=(90, 230, 255) if k % 2 == 0 else (190, 110, 255), width=max(3, int(dr.cam.s(R * 0.05))))
        dr.dn.arc([X - rx, Y - ry, X + rx, Y + ry], a0, a0 + 240, fill=255, width=max(3, int(dr.cam.s(R * 0.05))) + 4)

def rayos_bg(dr, cx, cy, c1, c2, t, sp=0.4):
    dr.img.paste(c1, [0, 0, W, H])
    for k in range(16):
        a = k * math.pi / 8 + t * sp
        dr.d.polygon([dr.cam.p(cx, cy), dr.cam.p(cx + math.cos(a) * 3000, cy + math.sin(a) * 3000), dr.cam.p(cx + math.cos(a + 0.2) * 3000, cy + math.sin(a + 0.2) * 3000)], fill=c2)

# ------------------------------------------------------------ utilería y personajes
def mancuerna(dr, x, y, s, ang=0.0, col=(60, 64, 76)):
    S = lambda v: v * s
    a = math.radians(ang); ca, sa = math.cos(a), math.sin(a)
    P = lambda dx, dy: (x + dx * ca - dy * sa, y + dx * sa + dy * ca)
    dr.line([P(-S(110), 0), P(S(110), 0)], (190, 196, 206), S(22))
    for sx in (-1, 1):
        for k, (off, hh) in enumerate(((95, 85), (140, 105))):
            cx, cy = P(sx * S(off), 0)
            w = S(22); hh = S(hh)
            pts = [P(sx * S(off) - w, -hh), P(sx * S(off) + w, -hh), P(sx * S(off) + w, hh), P(sx * S(off) - w, hh)]
            dr.poly(pts, col if k else (80, 86, 100), shade=k == 1)

def roca(dr, x, y, s, col=(140, 140, 150)):
    S = lambda v: v * s
    dr.poly([(x - S(120), y), (x - S(140), y - S(90)), (x - S(60), y - S(160)), (x + S(70), y - S(150)), (x + S(140), y - S(70)), (x + S(110), y)], col, shade=True)

def cabra(dr, x, y, s, t, face=1):
    S = lambda v: v * s; f = face
    for k in (-1, 1):
        dr.rrect(x + k * S(60) - S(10), y - S(90), x + k * S(60) + S(10), y, S(6), (80, 70, 60))
    dr.ell(x, y - S(120), S(110), S(60), (236, 232, 222), shade=True)
    hx, hy = x + f * S(110), y - S(180) + S(6) * math.sin(t * 5)
    dr.line([(hx - f * S(10), hy - S(30)), (hx - f * S(50), hy - S(80)), (hx - f * S(80), hy - S(60))], (150, 130, 100), S(12))
    dr.ell(hx, hy, S(46), S(36), (236, 232, 222))
    dr.ell(hx + f * S(30), hy + S(40), S(12), S(22), (236, 232, 222))
    dr.ell(hx + f * S(10), hy - S(8), S(8), S(8), INK)

def vikingo(dr, x, y, s, t, mouth=0.0, expr="happy", arm_r=20, arm_l=20, elb_r=0, elb_l=0, look=(0, 0), musc=1.0,
            barba=(210, 110, 50), tunica=(60, 100, 150), bob_ph=0.0, wet=False):
    """(x, y) = pies. Vikingo grandote con casco SIN cuernos, barba trenzada y chaleco de piel. Altura ≈ 980*s.
    musc = tamaño de músculos (1 normal, 1.8 enorme). Devuelve manos y cabeza."""
    S = lambda v: v * s
    bob = S(5) * math.sin(t * 2.2 + bob_ph)
    skin = (240, 190, 150)
    mw = 1 + 0.45 * (musc - 1)
    for sx in (-1, 1):
        dr.rrect(x + sx * S(70) - S(34) * mw, y - S(260), x + sx * S(70) + S(34) * mw, y - S(20), S(18), (90, 66, 46))
        dr.ell(x + sx * S(74), y - S(20), S(56), S(24), (60, 40, 30))
        for k in range(3): dr.line([(x + sx * S(70) - S(34) * mw, y - S(60) - k * S(55)), (x + sx * S(70) + S(34) * mw, y - S(40) - k * S(55))], (150, 110, 70), S(8))
    tw = S(200) * mw
    dr.rrect(x - tw, y - S(620) + bob, x + tw, y - S(220), S(110), tunica, shade=True)
    for sx in (-1, 1):
        dr.poly([(x + sx * S(40), y - S(615) + bob), (x + sx * tw * 1.02, y - S(560) + bob), (x + sx * tw * 1.02, y - S(300)), (x + sx * S(70), y - S(300))], (140, 104, 70))
    dr.rrect(x - tw * 1.03, y - S(330), x + tw * 1.03, y - S(280), S(10), (70, 46, 30))
    dr.rrect(x - S(30), y - S(338), x + S(30), y - S(272), S(8), (210, 170, 60))
    hands = []
    for sx, ang, eb in ((-1, arm_l, elb_l), (1, arm_r, elb_r)):
        shx, shy = x + sx * (tw - S(20)), y - S(560) + bob
        a1 = math.radians(ang); a2 = math.radians(ang + eb)
        L = S(130)
        ex, ey = shx + sx * math.sin(a1) * L, shy + math.cos(a1) * L
        hx, hy = ex + sx * math.sin(a2) * L, ey + math.cos(a2) * L
        dr.line([(shx, shy), (ex, ey)], skin, S(80) * mw)
        dr.line([(ex, ey), (hx, hy)], skin, S(70) * mw)
        if musc > 1.05:   # bíceps
            mx, my = (shx + ex) / 2, (shy + ey) / 2
            dr.ell(mx, my, S(58) * musc, S(48) * musc, skin, shade=True)
        dr.rrect(ex + (hx - ex) * 0.55 - S(42) * mw, ey + (hy - ey) * 0.55 - S(30), ex + (hx - ex) * 0.55 + S(42) * mw, ey + (hy - ey) * 0.55 + S(30), S(10), (120, 84, 54))
        dr.ell(hx, hy, S(48) * mw, S(48) * mw, skin)
        hands.append((hx, hy))
    hx, hy = x, y - S(790) + bob
    dr.ell(hx, hy, S(160), S(160), skin, shade=True)
    # barba trenzada
    dr.poly([(hx - S(160), hy + S(10)), (hx - S(120), hy + S(200)), (hx - S(40), hy + S(250)), (hx + S(40), hy + S(250)), (hx + S(120), hy + S(200)), (hx + S(160), hy + S(10)), (hx + S(80), hy + S(90)), (hx - S(80), hy + S(90))], barba)
    for sx in (-1, 1):
        dr.rrect(hx + sx * S(50) - S(22), hy + S(230), hx + sx * S(50) + S(22), hy + S(360), S(14), barba)
        dr.rrect(hx + sx * S(50) - S(24), hy + S(330), hx + sx * S(50) + S(24), hy + S(350), S(4), TURQ if sx > 0 else (210, 170, 60))
    for sx in (-1, 1): dr.ell(hx + sx * S(55), hy + S(80), S(70), S(26), mix(barba, (255, 255, 255), 0.15))
    dr.ell(hx, hy + S(30), S(40), S(40), (226, 150, 120))
    mo = clamp(mouth)
    if mo > 0.06 or expr in ("shock", "laugh"):
        mo = max(mo, 0.6 if expr in ("shock", "laugh") else 0)
        dr.ell(hx, hy + S(130), S(56), S(12 + 40 * mo), (100, 24, 30))
        dr.ell(hx, hy + S(130 + 24 * mo), S(30), S(8 + 10 * mo), (230, 110, 120))
    elif expr == "smug":
        dr.line([(hx - S(44), hy + S(132)), (hx + S(10), hy + S(136)), (hx + S(50), hy + S(116))], (100, 24, 30), S(12))
    else:
        dr.chord(hx, hy + S(100), S(55), S(44), 0, 180, (100, 24, 30))
    blink = (t % 3.7) < 0.12
    for sx in (-1, 1):
        ex, ey = hx + sx * S(60), hy - S(30)
        if expr == "laugh":
            dr.chord(ex, ey + S(10), S(30), S(22), 180, 360, INK); dr.chord(ex, ey + S(16), S(26), S(16), 180, 360, skin)
        elif blink:
            dr.rrect(ex - S(28), ey - S(3), ex + S(28), ey + S(5), S(3), INK)
        else:
            big = 1.25 if expr == "shock" else 1.0
            dr.ell(ex, ey, S(30) * big, S(34) * big, (255, 255, 255))
            dr.ell(ex + look[0] * S(10), ey + look[1] * S(10), S(14), S(17), INK)
        tilt = {"angry": 18, "smug": 8, "shock": -12, "laugh": -8}.get(expr, -4)
        dr.line([(ex - S(38), ey - S(55) + sx * S(tilt) * 0.5), (ex + S(38), ey - S(55) - sx * S(tilt) * 0.5)], mix(barba, (0, 0, 0), 0.2), S(18))
    for sx in (-1, 1): dr.ell(hx + sx * S(105), hy + S(40), S(22), S(13), (240, 140, 130))
    # casco redondo SIN cuernos (como los reales), con protector de nariz
    dr.chord(hx, hy - S(70), S(172), S(150), 180, 360, (150, 156, 170))
    dr.rrect(hx - S(178), hy - S(85), hx + S(178), hy - S(58), S(8), (120, 126, 140))
    dr.rrect(hx - S(14), hy - S(210), hx + S(14), hy + S(10), S(6), (120, 126, 140))
    if wet:
        k = (t * 1.5) % 1
        for j in range(3): dr.ell(hx - S(120) + j * S(110), hy + S(60) + S(220) * ((k + j * 0.3) % 1), S(12), S(18), (140, 210, 255))
    return dict(hands=hands, head=(hx, hy))

def drakkar(dr, x, y, s, t, hund=0.0, n_vik=0, musc=1.8):
    """(x, y) = línea de flotación al centro. hund = 0..1 cuánto se hunde."""
    S = lambda v: v * s
    y = y + S(260) * hund
    tilt = S(40) * hund
    dr.line([(x, y - S(40)), (x, y - S(560))], (110, 76, 46), S(22))
    for k in range(5):
        dr.rrect(x - S(230), y - S(540) + k * S(84), x + S(230), y - S(456) + k * S(84), 0, (200, 50, 46) if k % 2 == 0 else (246, 236, 220))
    if n_vik:
        for k in range(n_vik):
            vikingo(dr, x - S(330) + k * S(220), y - S(30), s * 0.5, t, expr="shock" if hund > 0.3 else "happy", arm_r=60, arm_l=40, musc=musc, barba=[(210, 110, 50), (240, 210, 120), (120, 80, 50), (200, 200, 200)][k % 4], tunica=[(60, 100, 150), (150, 50, 50), (70, 120, 70), (120, 80, 140)][k % 4], bob_ph=k)
    hull = [(x - S(480), y - S(100) - tilt), (x + S(480), y - S(100) + tilt), (x + S(380), y + S(40) + tilt), (x - S(380), y + S(40) - tilt)]
    dr.poly(hull, (130, 86, 50), shade=True)
    dr.line([(x + S(470), y - S(100) + tilt), (x + S(540), y - S(260) + tilt), (x + S(600), y - S(280) + tilt), (x + S(590), y - S(240) + tilt)], (130, 86, 50), S(40))
    dr.ell(x + S(585), y - S(268) + tilt, S(10), S(10), INK)
    dr.line([(x - S(470), y - S(100) - tilt), (x - S(540), y - S(240) - tilt), (x - S(510), y - S(270) - tilt)], (130, 86, 50), S(36))
    for k in range(7):
        sx = x - S(360) + k * S(120)
        dr.ell(sx, y - S(70) + tilt * (k - 3) / 3, S(46), S(46), [(220, 180, 60), (50, 110, 170), (190, 50, 46), TURQ][k % 4])
        dr.ell(sx, y - S(70) + tilt * (k - 3) / 3, S(12), S(12), (160, 160, 170))

def burst(img, txt, x, y, size, t, col=(255, 222, 40), ang=-6):
    k = eob(t / 0.22) if t < 0.22 else 1.0
    if k <= 0.02 or t < 0: return
    f = font(size * k)
    lay = Image.new("RGBA", (int(f.getlength(txt) + 140), int(size * k * 1.7)), (0, 0, 0, 0))
    ImageDraw.Draw(lay).text((70, 16), txt, font=f, fill=col + (255,), stroke_width=int(15 * k), stroke_fill=INK)
    lay = lay.rotate(ang, resample=Image.BICUBIC, expand=True)
    img.paste(lay, (int(x - lay.width / 2), int(y - lay.height / 2)), lay)

def cartel(img, t, l1, l2, y=470):
    k = eob(t / 0.3); d = ImageDraw.Draw(img)
    if k < 0.05: return
    d.rounded_rectangle([140, y, 940, y + 170], radius=30, fill=(236, 214, 170), outline=INK, width=8)
    d.text((540, y + 50), l1, font=font(70 * k + 1, F_SERIF), fill=(120, 40, 30), anchor="mm")
    d.text((540, y + 122), l2, font=font(50 * k + 1), fill=(40, 140, 160), anchor="mm")

def letrero(dr, x, y, w, txt, size, col=(150, 100, 60), tcol=(250, 240, 210)):
    dr.line([(x - w / 2 + 40, y), (x - w / 2 + 40, y + 420)], (100, 66, 40), 26)
    dr.line([(x + w / 2 - 40, y), (x + w / 2 - 40, y + 420)], (100, 66, 40), 26)
    dr.rrect(x - w / 2, y - 80, x + w / 2, y + 80, 18, col, shade=True)
    dr.text(x, y, txt, size, tcol, stroke=5)

def badge(img, T):
    d = ImageDraw.Draw(img); f = font(36); txt = "¿QUÉ PASARÍA SI…?"
    d.rounded_rectangle([36, 110, 36 + f.getlength(txt) + 44, 170], radius=16, fill=TURQ, outline=INK, width=5)
    d.text((58, 140), txt, font=f, fill=(255, 255, 255), anchor="lm")

def tick(img, x, y, ok, t, size=150):
    k = eob(t / 0.25)
    if k < 0.05 or t < 0: return
    d = ImageDraw.Draw(img); r = size * k / 2
    d.ellipse([x - r, y - r, x + r, y + r], fill=(60, 190, 90) if ok else (220, 50, 50), outline=INK, width=8)
    q = r * 0.45; lw = max(4, int(r * 0.22))
    if ok: d.line([(x - q, y), (x - q * 0.25, y + q * 0.75), (x + q, y - q * 0.7)], fill=(255, 255, 255), width=lw, joint="curve")
    else:
        d.line([(x - q, y - q), (x + q, y + q)], fill=(255, 255, 255), width=lw); d.line([(x - q, y + q), (x + q, y - q)], fill=(255, 255, 255), width=lw)

# ------------------------------------------------------------ planos
SHOTS = []
def shot(fn): SHOTS.append(fn); return fn
def tl(k, frac): return LEAD + len(VOZ[k]) / SR * frac
BARBAS = [(210, 110, 50), (240, 210, 120), (120, 80, 50), (200, 200, 200), (170, 70, 40)]
TUNS = [(60, 100, 150), (150, 50, 50), (70, 120, 70), (120, 80, 140), (170, 120, 50)]

@shot
def s01(t, D, T):    # gancho: Nico entrenador vikingo levantando mancuerna frente al fiordo
    cam = Cam(540, 1080, lerp(1.1, 1.25, ease(t / D)))
    dr = Canvas(cam); pueblo(dr, t)
    letrero(dr, 830, 1080, 420, "GYM", 90)
    up = 0.5 + 0.5 * math.sin(t * 5)
    info = nico(dr, 400, 1680, 0.68, t, traje="vikingo_coach", arms=(20, 25), elbows=(0, lerp(10, 135, up)), expr="happy", mouth=0.3 * abs(math.sin(t * 9)))
    hx, hy = info["hands"][1]; mancuerna(dr, hx, hy, 0.6, 0)
    vikingo(dr, 860, 1760, 0.5, t, expr="shock", arm_l=20, arm_r=30, look=(-1, -0.2))
    f = tinta(dr); img = acabado(f, T)
    burst(img, "¿Y SI…?", 540, 330, 160, t - 0.1, ang=-6)
    return img, 0

@shot
def s02(t, D, T):    # portal → aparece en Noruega con casco de cuernos
    tp = D * 0.35
    if t < tp:
        cam = Cam(540, 1000, 1.0)
        dr = Canvas(cam, bg=(18, 10, 30)); rayos_bg(dr, 540, 1000, (18, 10, 30), (34, 20, 56), t)
        portal(dr, 540, 1050, 300, t, ease(t / 0.4))
        walk = clamp((t - 0.3) / (tp - 0.4))
        if walk < 1: nico(dr, 540, 1560 - 30 * walk, 0.6 * (1 - 0.5 * walk), t, arms=(30, 30), expr="happy")
        f = tinta(dr); add_glow(f, 540, 1050, 380, (150, 120, 255), 0.5)
        if t > tp - 0.15: f += 255 * clamp((t - (tp - 0.15)) / 0.15)
        return acabado(f, T), 0
    tt = t - tp
    cam = Cam(540, 1100, lerp(1.0, 1.12, ease(tt / (D - tp))))
    dr = Canvas(cam); pueblo(dr, t)
    cabra(dr, 950, 1500, 0.6, t, face=-1)
    portal(dr, 540, 1250, 220, t, 1 - ease((tt - 0.8) / 0.5))
    land = clamp(tt / 0.35)
    sq = 1 - 0.3 * math.exp(-tt * 7) * math.cos(tt * 20) if land >= 1 else 1.15
    nico(dr, 520, lerp(1150, 1720, land ** 2), 0.68, t, traje="vikingo", arms=(140, 140) if land < 1 else (30, 150), elbows=(0, 20), expr="shock" if tt < 0.9 else "smug", squash=sq, look=(0.4, -0.5))
    f = tinta(dr)
    if tt < 0.2: f += 255 * (1 - tt / 0.2)
    img = acabado(f, T)
    if tt > 0.8: cartel(img, tt - 0.8, "NORUEGA", "AÑO 900 · ERA VIKINGA", y=360)
    return img, 0

@shot
def s03(t, D, T):    # Bjorn se ríe: ¡pareces una cabra!
    cam = Cam(600, 1150, lerp(1.2, 1.32, ease(t / D)))
    dr = Canvas(cam); pueblo(dr, t)
    cabra(dr, 180, 1560, 0.55, t, face=1)
    nico(dr, 250, 1800, 0.45, t, traje="vikingo", arms=(20, 20), expr="worried", look=(1, -0.5))
    r = vikingo(dr, 720, 1980, 0.92, t, mouth=boca(2, t), expr="laugh" if t < tl(2, 0.6) else "happy", arm_l=150, elb_l=-30, arm_r=30, look=(-1, 0))
    f = tinta(dr); img = acabado(f, T)
    burst(img, "¡JA JA JA!", 600, 340, 130, t - 0.1, ang=-8)
    if t > tl(2, 0.7): burst(img, "¡BEEE!", 230, 980, 90, t - tl(2, 0.7), col=(255, 255, 255), ang=10)
    return img, 2 * math.sin(t * 30) if t < tl(2, 0.6) else 0

@shot
def s04(t, D, T):    # dato real: nunca usaron cuernos; ópera de 1876
    half = tl(3, 0.52)
    if t < half:
        cam = Cam(540, 1000, lerp(1.0, 1.08, ease(t / half)))
        dr = Canvas(cam); rayos_bg(dr, 540, 1000, (36, 60, 90), (50, 80, 116), t, 0.2)
        # casco con cuernos (falso) vs casco real
        for sx, horns in ((-1, True), (1, False)):
            hx, hy = 540 + sx * 240, 1050
            if horns:
                for k in (-1, 1): dr.poly([(hx + k * 120, hy - 60), (hx + k * 210, hy - 150), (hx + k * 230, hy - 270), (hx + k * 180, hy - 160), (hx + k * 100, hy - 110)], (246, 236, 210))
            dr.chord(hx, hy, 160, 150, 180, 360, (150, 156, 170))
            dr.rrect(hx - 166, hy - 18, hx + 166, hy + 12, 8, (120, 126, 140))
            dr.rrect(hx - 14, hy - 150, hx + 14, hy + 110, 6, (120, 126, 140))
        f = tinta(dr); img = acabado(f, T)
        tick(img, 300, 1260, False, t - tl(3, 0.25), 170)
        tick(img, 780, 1260, True, t - tl(3, 0.32), 170)
        d = ImageDraw.Draw(img)
        d.text((300, 700), "MITO", font=font(80), fill=(255, 255, 255), anchor="mm", stroke_width=9, stroke_fill=INK)
        d.text((780, 700), "REAL", font=font(80), fill=(255, 214, 10), anchor="mm", stroke_width=9, stroke_fill=INK)
        return img, 0
    tt = t - half
    cam = Cam(540, 1050, lerp(1.05, 1.18, ease(tt / (D - half))))
    dr = Canvas(cam, bg=(30, 12, 16))
    dr.rrect(-600, 1400, 1700, 2700, 0, (90, 50, 30))
    for k in range(8):   # telón rojo
        dr.rrect(-200 + k * 190, -200, -200 + k * 190 + 200, 1400, 60, (170, 30, 40) if k % 2 == 0 else (140, 20, 32), shade=k % 2 == 1)
    dr.rrect(-200, 1360, 1300, 1420, 0, (200, 160, 60))
    # cantante de ópera con casco de cuernos
    v = vikingo(dr, 540, 1760, 0.62, t, mouth=0.4 + 0.4 * abs(math.sin(t * 4)), expr="happy", arm_l=120, arm_r=120, elb_l=20, elb_r=20, barba=(240, 220, 160), tunica=(200, 170, 60))
    hx, hy = v["head"]
    for k in (-1, 1): dr.poly([(hx + k * 90, hy - 90), (hx + k * 160, hy - 160), (hx + k * 175, hy - 250), (hx + k * 135, hy - 165), (hx + k * 70, hy - 120)], (246, 236, 210))
    f = tinta(dr)
    add_cono(f, 540, 0, 1500, 120, 700, (255, 240, 200), 0.22)
    img = acabado(f, T)
    d = ImageDraw.Draw(img)
    for k in range(4):
        ph = (t * 0.8 + k / 4) % 1
        d.text((700 + k * 60 - ph * 80, 900 - ph * 400), "♪", font=font(90, F_SERIF), fill=(255, 230, 120), anchor="mm", stroke_width=5, stroke_fill=INK)
    burst(img, "ÓPERA · 1876", 540, 380, 110, tt - 0.1, col=(255, 222, 40), ang=-5)
    return img, 0

@shot
def s05(t, D, T):    # Nico: ¡Bienvenidos al Gimnasio Nico!
    cam = Cam(500, 1150, lerp(1.35, 1.5, ease(t / D)))
    dr = Canvas(cam); pueblo(dr, t)
    letrero(dr, 520, 820, 620, "GIMNASIO NICO", 70, col=(40, 150, 166))
    for k in range(3): mancuerna(dr, 860, 1500 - k * 60, 0.6, 0)
    roca(dr, 150, 1560, 0.8)
    nico(dr, 470, 1800, 0.66, t, traje="vikingo_coach", arms=(130, 130), elbows=(-20, -20), expr="happy" if t < tl(4, 0.2) else "happy_eyes", mouth=boca(4, t))
    f = tinta(dr); img = acabado(f, T)
    if t > tl(4, 0.65): burst(img, "¡GRATIS!", 560, 420, 140, t - tl(4, 0.65), col=(120, 230, 120), ang=8)
    return img, 0

@shot
def s06(t, D, T):    # levantaban rocas… nunca una mancuerna
    half = tl(5, 0.55)
    if t < half:
        u = ease(t / half)
        cam = Cam(lerp(420, 660, u), 1150, 1.1)
        dr = Canvas(cam); pueblo(dr, t)
        drakkar(dr, 1150, 1080, 0.45, t)
        for k in range(3):
            up = 0.5 + 0.5 * math.sin(t * 4 + k * 2)
            kw = dict(expr="angry", arm_l=lerp(150, 175, up), arm_r=lerp(150, 175, up), elb_l=-20, elb_r=-20, barba=BARBAS[k], tunica=TUNS[k], bob_ph=k)
            v = vikingo(dr, 220 + k * 330, 1740 + (k % 2) * 30, 0.5, t, **kw)
            (lx, ly), (rx, ry) = v["hands"]
            roca(dr, (lx + rx) / 2, ly + 20, 1.0)
            vikingo(dr, 220 + k * 330, 1740 + (k % 2) * 30, 0.5, t, **kw)
        f = tinta(dr); return acabado(f, T), 0
    tt = t - half
    cam = Cam(540, 1000, lerp(1.15, 1.3, ease(tt / (D - half))))
    dr = Canvas(cam); rayos_bg(dr, 540, 1000, (150, 110, 60), (180, 140, 80), t)
    k = eob(tt / 0.35)
    mancuerna(dr, 540, 1000, 2.6 * k + 0.01, -10)
    f = tinta(dr); add_glow(f, *cam.p(540, 1000), 380, (255, 240, 200), 0.3)
    img = acabado(f, T); d = ImageDraw.Draw(img)
    for j in range(6):
        a = t * 2 + j * 1.05
        d.text((540 + math.cos(a) * 420, 1000 + math.sin(a) * 300), "✦", font=font(70), fill=(255, 240, 150), anchor="mm")
    burst(img, "¿¡QUÉ ES ESO!?", 540, 400, 110, tt - 0.15, ang=-5)
    return img, 0

@shot
def s07(t, D, T):    # Bjorn: ¡Por Odín! (bíceps)
    cam = Cam(540, 1100, lerp(1.25, 1.38, ease(t / D)))
    dr = Canvas(cam); pueblo(dr, t)
    up = 0.5 + 0.5 * math.sin(t * 6)
    v = vikingo(dr, 540, 2000, 0.95, t, mouth=boca(6, t), expr="happy", arm_r=lerp(90, 120, up), elb_r=lerp(-20, -130, up), arm_l=95, elb_l=-110, musc=lerp(1.2, 1.5, ease(t / D)))
    hx, hy = v["hands"][1]; mancuerna(dr, hx, hy, 0.75, 90)
    f = tinta(dr); img = acabado(f, T)
    burst(img, "¡POR ODÍN!", 540, 330, 130, t - 0.05, ang=-7)
    if t > tl(6, 0.6): burst(img, "💪" if False else "¡RUMBO A INGLATERRA!", 540, 520, 64, t - tl(6, 0.6), col=(120, 230, 255), ang=4)
    return img, 0

@shot
def s08(t, D, T):    # una semana después: todos enormes
    u = ease(t / D)
    cam = Cam(540, 1300, lerp(1.35, 1.2, u))
    dr = Canvas(cam); pueblo(dr, t, tarde=0.3)
    m = lerp(1.0, 2.0, ease((t - tl(7, 0.15)) / (D * 0.7)))
    for k in range(4, -1, -1):
        vikingo(dr, 130 + k * 205, 1720 + (k % 2) * 40, 0.46, t, expr="happy" if k % 2 else "smug", arm_l=95, elb_l=-110, arm_r=95, elb_r=-110, musc=m, barba=BARBAS[k], tunica=TUNS[k], bob_ph=k)
    f = tinta(dr); img = acabado(f, T)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([660, 260, 1010, 450], radius=20, fill=(250, 246, 236), outline=INK, width=7)
    d.rectangle([660, 260, 1010, 320], fill=(200, 50, 46), outline=INK, width=7)
    day = min(7, 1 + int(t / D * 8))
    d.text((835, 390), f"DÍA {day}", font=font(70), fill=INK, anchor="mm")
    if t > tl(7, 0.6): burst(img, "¡DEMASIADO!", 420, 560, 120, t - tl(7, 0.6), col=(255, 100, 80), ang=-8)
    return img, 0

@shot
def s09(t, D, T):    # se suben al barco… y se hunde
    th = tl(8, 0.5)
    hund = ease((t - th) / 0.9)
    cam = Cam(560, 1150, lerp(1.2, 1.32, ease(t / D)))
    dr = Canvas(cam); cielo(dr, t, tarde=0.3); montanas(dr, 930)
    dr.rrect(-600, 930, 1700, 2700, 0, (50, 96, 140))
    drakkar(dr, 560, 1300, 0.9, t, hund=hund, n_vik=4, musc=2.0)
    dr.rrect(-600, 1300 + 60, 1700, 2700, 0, (46, 90, 134))
    for r in range(6):
        for j in range(-4, 14):
            x = j * 150 + (r % 2) * 75 + 30 * math.sin(t * 2 + r)
            dr.rrect(x, 1380 + r * 70, x + 80, 1390 + r * 70, 4, (110, 160, 200), nolin=True)
    f = tinta(dr); img = acabado(f, T)
    if hund > 0.2:
        d = ImageDraw.Draw(img)
        for k in range(12):
            ph = (t * 1.3 + k / 12) % 1
            x = 300 + k * 45; y = 1350 - ph * 500
            d.ellipse([x - 14, y - 14, x + 14, y + 14], outline=(220, 240, 255), width=5)
    burst(img, "¡GLUB GLUB!", 540, 380, 130, t - th - 0.3, col=(120, 220, 255), ang=-6)
    return img, (5 * math.sin(t * 25) if hund > 0 and hund < 1 else 0)

@shot
def s10(t, D, T):    # Nico: ¿y si hoy hacemos cardio?
    cam = Cam(540, 1150, 1.6)
    dr = Canvas(cam); pueblo(dr, t, tarde=0.3, casas=False)
    for k in range(3):
        vikingo(dr, 150 + k * 380, 1700, 0.55, t, expr="angry", arm_l=20, arm_r=20, musc=2.0, barba=BARBAS[k + 1], tunica=TUNS[k + 1], wet=True, look=(0.5 if k == 0 else -0.5, 0.3))
    nico(dr, 540, 1840, 0.62, t, traje="vikingo_coach", arms=(60, 25), elbows=(70, 0), expr="nervous", mouth=boca(9, t), sweat=True, look=(0.8, -0.6))
    f = tinta(dr); img = acabado(f, T)
    if t > tl(9, 0.55): burst(img, "¿CARDIO?", 560, 420, 130, t - tl(9, 0.55), col=(255, 255, 255), ang=6)
    return img, 2 * math.sin(t * 40)

@shot
def s11(t, D, T):    # Bjorn abre GYM VALHALLA y mira a Nico
    u = ease(t / D)
    cam = Cam(lerp(380, 640, u), 1150, lerp(1.0, 1.15, u))
    dr = Canvas(cam); pueblo(dr, t)
    letrero(dr, 300, 900, 520, "GIMNASIO NICO", 54, col=(40, 150, 166))
    letrero(dr, 800, 820, 480, "GYM VALHALLA", 54, col=(170, 40, 40))
    for k in range(3):
        vikingo(dr, 1130 + k * 160, 1700, 0.36, t, expr="happy", arm_l=95, elb_l=-110, arm_r=95, elb_r=-110, musc=1.8, barba=BARBAS[k + 2], tunica=TUNS[k + 2], bob_ph=k)
    nico(dr, 280, 1700, 0.5, t, traje="vikingo_coach", arms=(20, 20), expr="shock", look=(1, 0))
    vikingo(dr, 780, 1760, 0.7, t, expr="smug", arm_l=20, arm_r=120, elb_r=-60, musc=2.0, look=(-1, 0))
    f = tinta(dr); img = acabado(f, T)
    return img, 0

@shot
def s12(t, D, T):    # ¡Miren! ¡Esta pesa habla! — Bjorn levanta a Nico como pesa
    cam = Cam(520, 950, 1.0)
    dr = Canvas(cam); pueblo(dr, t)
    letrero(dr, 180, 1000, 360, "VALHALLA", 60, col=(170, 40, 40))
    up = 0.5 + 0.5 * math.sin(t * 5)
    v = vikingo(dr, 330, 1950, 0.8, t, mouth=boca(11, t), expr="laugh" if t > tl(11, 0.5) else "happy", arm_r=lerp(150, 172, up), elb_r=lerp(-10, 0, up), arm_l=95, elb_l=-110, musc=2.0)
    hx, hy = v["hands"][1]
    nico(dr, hx, hy - 20, 0.55, t, traje="vikingo_coach", arms=(170, 170), elbows=(0, 0), expr="shock", sweat=True)
    dr.ell(hx, hy - 20, 60, 40, (240, 190, 150))   # mano agarrando los pies
    f = tinta(dr); img = acabado(f, T)
    burst(img, "¡HABLA!", 300, 420, 120, t - tl(11, 0.6), ang=-8)
    return img, 0

@shot
def s13(t, D, T):    # primer plano: ¡Bájameee!
    up = 0.5 + 0.5 * math.sin(t * 7)
    cam = Cam(540, 1100 - 120 * up, 1.7)
    dr = Canvas(cam); pueblo(dr, t, casas=False)
    nico(dr, 540, 1700 - 120 * up, 0.66, t, traje="vikingo_coach", arms=(165, 165), elbows=(10, 10), expr="shock", mouth=max(boca(12, t), 0.5), sweat=True)
    dr.ell(540, 1700 - 120 * up, 160, 80, (240, 190, 150))
    f = tinta(dr); img = acabado(f, T)
    burst(img, "¡BÁJAMEEE!", 540, 380, 130, t - 0.05, col=(255, 120, 80), ang=-6)
    return img, 4 * math.sin(t * 50)

@shot
def s14(t, D, T):    # cierre
    cam = Cam(540, 1000, 1.0)
    dr = Canvas(cam, bg=(18, 10, 30)); rayos_bg(dr, 540, 1000, (18, 10, 30), (34, 20, 56), -t)
    o = 1 - ease((t - D + 0.9) / 0.7)
    portal(dr, 540, 1080, 330, t, o)
    if t < D - 1.1:
        up = 0.5 + 0.5 * math.sin(t * 5)
        info = nico(dr, 540, 1560, 0.55, t, traje="vikingo_coach", arms=(20, 25), elbows=(0, lerp(10, 135, up)), expr="happy")
        hx, hy = info["hands"][1]; mancuerna(dr, hx, hy, 0.5, 0)
    f = tinta(dr); add_glow(f, 540, 1080, 450, (150, 120, 255), 0.5 * o)
    img = acabado(f, T)
    d = ImageDraw.Draw(img)
    if t > tl(13, 0.45):
        k = eob((t - tl(13, 0.45)) / 0.3)
        d.rounded_rectangle([90, 300, 990, 560], radius=36, fill=(255, 214, 10), outline=INK, width=8)
        d.text((540, 380), "¿QUÉ NEGOCIO LLEVO", font=font(62 * k + 1), fill=INK, anchor="mm")
        d.text((540, 470), "A OTRA ÉPOCA?", font=font(62 * k + 1), fill=INK, anchor="mm")
        d.text((540, 640), "¡COMENTA!", font=font(80), fill=(255, 255, 255), anchor="mm", stroke_width=10, stroke_fill=INK)
    return img, 0

assert len(SHOTS) == len(VOZ), (len(SHOTS), len(VOZ))

# ------------------------------------------------------------ cuadro
def frame(T):
    i = max(j for j in range(len(SHOTS)) if STARTS[j] <= T) if T < TOTAL else len(SHOTS) - 1
    t = T - STARTS[i]
    img, sh = SHOTS[i](t, DURS[i], T)
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
    rng = np.random.default_rng(7)
    def add(s, sig, g=1.0):
        i0 = int(s * sr); i1 = min(n, i0 + len(sig))
        if 0 <= i0 < n: out[i0:i1] += g * sig[:i1 - i0]
    def seg(d): return np.arange(int(d * sr)) / sr
    hz = lambda m: 440 * 2 ** ((m - 69) / 12)
    noise = rng.standard_normal(n)
    bp = lambda lo, hi: sosfilt(butter(2, [lo, hi], btype="band", fs=sr, output="sos"), noise)
    wh = bp(400, 3500); low = sosfilt(butter(2, 160, btype="low", fs=sr, output="sos"), noise)
    S_ = STARTS
    # A) marcha vikinga: tambor grave + palmas + melodía modal (re dórico) en "cuerno"
    def marcha(t0, t1, vol=1.0):
        bt = 0.36
        mel = [62, 65, 67, 69, 67, 65, 64, 62, 60, 62, 65, 64]
        k = 0; s = t0
        while s < t1:
            x = seg(0.3)
            if k % 2 == 0: add(s, vol * 0.2 * np.exp(-x * 14) * np.sin(2 * np.pi * (60 + 40 * np.exp(-x * 30)) * x))
            if k % 4 == 2: add(s, vol * 0.06 * rng.standard_normal(len(x)) * np.exp(-x * 30))
            if k % 2 == 0:
                m = mel[(k // 2) % len(mel)]; xm = seg(bt * 1.9)
                tone = sum(np.sin(2 * np.pi * hz(m) * h * xm) / h for h in (1, 2, 3, 4))
                add(s, vol * 0.035 * tone * np.minimum(1, xm * 20) * np.exp(-xm * 2.2))
            k += 1; s += bt
    marcha(0, S_[8])
    marcha(S_[10], S_[13] + DURS[13], 0.85)
    # B) hundimiento: bajo + burbujas
    x = seg(DURS[8] + DURS[9]); add(S_[8], 0.25 * low[:len(x)] * (0.3 + 0.7 * np.minimum(1, x / 2)))
    th = S_[8] + tl(8, 0.5)
    for kk in range(16):
        x = seg(0.07); add(th + 0.1 + kk * 0.11, 0.12 * np.exp(-x * 40) * np.sin(2 * np.pi * (500 + 900 * x * 10 + 80 * (kk % 4)) * x))
    x = seg(1.2); add(th, 0.4 * (low[:len(x)] * 1.2 + 0.3 * wh[:len(x)]) * np.exp(-x * 2.5))   # crujido/splash
    # efectos
    x = seg(1.2); add(S_[1] + 0.1, 0.12 * np.sin(2 * np.pi * (200 + 600 * x) * x) * np.sin(np.pi * x / 1.2))   # portal
    tp = S_[1] + DURS[1] * 0.35; x = seg(0.5); add(tp, 0.5 * np.exp(-x * 9) * np.sin(2 * np.pi * (60 + 40 * np.exp(-x * 20)) * x))
    for k in range(1, len(S_) - 1):
        x = seg(0.3); add(S_[k] - 0.08, 0.12 * wh[:len(x)] * np.sin(np.pi * x / 0.3))
    x = seg(0.5); add(S_[2] + tl(2, 0.7), 0.12 * np.sin(2 * np.pi * (380 + 30 * np.sin(2 * np.pi * 9 * x)) * x) * np.exp(-x * 4))   # cabra "beee"
    for j, tt in enumerate((0.25, 0.32)):   # ✗ / ✓
        x = seg(0.3); add(S_[3] + tl(3, tt), 0.18 * np.exp(-x * 10) * np.sin(2 * np.pi * (220 if j == 0 else 880) * x))
    x = seg(1.0); add(S_[5] + tl(5, 0.55), 0.25 * np.exp(-x * 3) * (np.sin(2 * np.pi * 784 * x) + np.sin(2 * np.pi * 1047 * x)) / 2)   # ding mancuerna
    x = seg(0.6); add(S_[11] + tl(11, 0.55), 0.3 * np.exp(-x * 6) * np.sin(2 * np.pi * (300 + 200 * x) * x))   # boing
    x = seg(1.6); add(S_[13] + 0.2, 0.12 * np.exp(-x * 1.5) * (np.sin(2 * np.pi * 523 * x) + np.sin(2 * np.pi * 784 * x)) / 2)
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
