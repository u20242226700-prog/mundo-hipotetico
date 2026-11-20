#!/usr/bin/env python3
"""¿Por qué las vías del tren tienen HUECOS? (formato "¿Por qué…?" de días pares, 2026-11-20 08:00)
Estilo vector + cómic (motor/vc.py). Nico con traje de MAQUINISTA (gorra de rayas con botón turquesa, overol de mezclilla,
pañuelo turquesa). Rival: Don Perfecto (rieles pegaditos). Jefe: Don Vapor. Dato: dilatación térmica del acero
(≈0,000012 por °C: un riel de 25 m crece ≈1,2 cm con 40 °C más)."""
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
DURS[0] += 0.25; DURS[1] += 0.7; DURS[8] += 0.35; DURS[15] += 0.35; DURS[16] += 0.7
CHUNKS = [
    [("¿Por qué las vías", ["vías"]), ("del tren", ["tren"]), ("tienen HUECOS", ["HUECOS"]), ("entre riel y riel?", ["riel?"])],
    [("Nico cruza el portal", ["portal"]), ("y cae en 1870…", ["1870…"]), ("¡justo en la gran", []), ("carrera del", []), ("ferrocarril!", ["ferrocarril!"])],
    [("¡Mis rieles", []), ("van pegaditos,", ["pegaditos,"]), ("sin un solo hueco!", ["hueco!"]), ("¡Perfectos,", ["¡Perfectos,"]), ("como yo!", [])],
    [("Uno.", ["Uno."]), ("Nico hace algo", []), ("rarísimo:", ["rarísimo:"]), ("deja un huequito", ["huequito"]), ("entre cada riel", ["riel"])],
    [("¿¡Huecos!?", ["¿¡Huecos!?"]), ("¡Te pago por rieles,", ["rieles,"]), ("no por agujeros,", ["agujeros,"]), ("muchacho!", [])],
    [("Confíe en mí,", []), ("jefe.", []), ("Ese huequito", ["huequito"]), ("es para cuando", []), ("llegue el verano", ["verano"])],
    [("Nadie le cree…", ["cree…"]), ("y el tren de", []), ("Don Perfecto", ["Perfecto"]), ("arranca primero.", ["primero."]), ("¡Va ganando!", ["ganando!"])],
    [("Dos.", ["Dos."]), ("Llega el verano.", ["verano."]), ("El sol calienta", ["sol"]), ("los rieles", []), ("a más de", []), ("cincuenta grados", ["cincuenta"])],
    [("Y el acero", ["acero"]), ("caliente…", ["caliente…"]), ("¡se estira!", ["estira!"]), ("Los rieles pegaditos", ["pegaditos"]), ("no tienen", []), ("para dónde crecer…", ["crecer…"]), ("y se doblan", ["doblan"]), ("como un fideo", ["fideo"])],
    [("¿¡Mis rieles", []), ("hacen olas!?", ["olas!?"]), ("¡Esto no estaba", []), ("en el plano!", ["plano!"])],
    [("Tres.", ["Tres."]), ("En la vía de Nico,", ["Nico,"]), ("cada riel se estira…", ["estira…"]), ("y se mete", []), ("en su huequito.", ["huequito."]), ("¡La vía sigue", []), ("derechita!", ["derechita!"])],
    [("Un riel de", []), ("25 metros", ["25"]), ("puede crecer", ["crecer"]), ("más de", []), ("un centímetro", ["centímetro"]), ("con el calor.", ["calor."]), ("Por eso,", []), ("el hueco", ["hueco"])],
    [("¡El truco no es", ["truco"]), ("que no haya espacio…", ["espacio…"]), ("es dejarle espacio", ["espacio"]), ("al calor!", ["calor!"])],
    [("¡Y por eso", []), ("los trenes viejos", ["trenes"]), ("hacen clac-clac,", ["clac-clac,"]), ("clac-clac!", ["clac-clac!"])],
    [("¡Muchacho,", []), ("desde hoy eres", []), ("mi jefe de vías!", ["jefe"])],
    [("¿Y Don Perfecto?", ["Perfecto?"]), ("Con sus rieles", []), ("doblados…", ["doblados…"]), ("inventó la", []), ("montaña rusa", ["montaña", "rusa"])],
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
STEEL = (172, 178, 192); STEEL_HOT = (250, 120, 50); WOOD = (122, 82, 50); WOOD_D = (92, 60, 36); BAL = (150, 136, 118)
PAS = [(220, 80, 80), (80, 120, 210), (240, 180, 60), (120, 180, 100), (180, 100, 200)]

def valle(dr, t, calor=0.0, yh=900, sol=True):
    day = [(90, 160, 230), (124, 184, 238), (166, 208, 242), (220, 232, 240)]
    hot = [(236, 140, 60), (246, 170, 80), (252, 200, 110), (255, 228, 160)]
    for k in range(4):
        dr.rrect(-1200, -1400 + k * 600, 2400, (-1400 + (k + 1) * 600 + 4) if k < 3 else yh + 10, 0, mix(day[k], hot[k], calor))
    if sol:
        r = 80 + 60 * calor
        for k in range(12):
            a = k * math.pi / 6 + t * 0.3
            dr.poly([(820 + math.cos(a) * r * 1.1, 330 + math.sin(a) * r * 1.1), (820 + math.cos(a + 0.12) * r * 1.9, 330 + math.sin(a + 0.12) * r * 1.9),
                     (820 + math.cos(a - 0.12) * r * 1.9, 330 + math.sin(a - 0.12) * r * 1.9)], mix((255, 236, 120), (255, 170, 60), calor), nolin=True)
        dr.ell(820, 330, r, r, mix((255, 232, 100), (255, 190, 60), calor))
    for k in range(5):   # nubes lentas
        x = 1500 - ((k * 610 + t * 40) % 2600)
        for j in range(3): dr.ell(x + j * 90, 200 + (k % 3) * 120 - (j % 2) * 30, 110, 55, mix((250, 250, 252), (255, 236, 200), calor), nolin=True)
    # montañas facetadas (cara de luz + cara de sombra)
    far = mix((150, 176, 210), (210, 170, 150), calor); far_d = mix((120, 146, 186), (180, 140, 124), calor)
    for mx, mh, mw in ((-150, 360, 420), (300, 460, 480), (760, 400, 440), (1180, 470, 460)):
        dr.poly([(mx - mw, yh), (mx, yh - mh), (mx, yh)], far, nolin=True)
        dr.poly([(mx, yh - mh), (mx + mw, yh), (mx, yh)], far_d, nolin=True)
        dr.poly([(mx - mw * 0.22, yh - mh * 0.78), (mx, yh - mh), (mx + mw * 0.2, yh - mh * 0.8), (mx, yh - mh * 0.7)], (250, 250, 252), nolin=True)
    g1 = mix((110, 170, 80), (190, 170, 80), calor); g2 = mix((84, 146, 64), (170, 146, 60), calor)
    dr.poly([(-1200, yh), (-300, yh - 120), (300, yh - 40), (900, yh - 150), (2400, yh - 30), (2400, 4000), (-1200, 4000)], g2, nolin=True)
    for k in range(-3, 12):   # pinos de fondo
        px = k * 130 + (k % 3) * 30; py = yh - 30 + (k % 2) * 20; s = 0.8 + (k % 3) * 0.2
        c = mix((40, 100, 60), (110, 110, 50), calor)
        for j in range(3): dr.poly([(px - 50 * s + j * 8 * s, py - j * 50 * s), (px + 50 * s - j * 8 * s, py - j * 50 * s), (px, py - (j + 1.6) * 50 * s)], c, nolin=True)
    dr.rrect(-1200, yh, 2400, 4000, 0, g1, nolin=True)
    for k in range(40):   # matitas de pasto
        gx = (k * 197) % 1600 - 260; gy = yh + 60 + (k * 131) % 1500
        dr.line([(gx, gy), (gx - 10, gy - 26), (gx, gy), (gx + 12, gy - 30)], g2, 6, nolin=True)

def via(dr, xv, yh, ybot, hw, t, wave=0.0, zc=3.6, gaps=False, glow=0.0, n=30, near=1.0):
    """Vía en perspectiva hacia el horizonte. wave = amplitud del pandeo (rieles doblados)."""
    pts = []
    for i in range(n):
        z = near + i * 0.55; s = 1 / z
        off = wave * hw * 1.6 * math.sin((z - zc) * 1.9) * math.exp(-((z - zc) / 1.7) ** 2)
        pts.append((xv + off * s, yh + (ybot - yh) * s, hw * s, s))
    L = [(x - w * 1.3, y) for x, y, w, s in pts]; R = [(x + w * 1.3, y) for x, y, w, s in pts]
    dr.poly(L + R[::-1], BAL, nolin=True)
    for i in range(n - 1, -1, -1):
        x, y, w, s = pts[i]
        dy = (ybot - yh) * (s - (1 / (near + (i + 1) * 0.55)))
        dr.poly([(x - w * 1.05, y - dy * 0.18), (x + w * 1.05, y - dy * 0.18), (x + w * 1.08, y + dy * 0.2), (x - w * 1.08, y + dy * 0.2)], WOOD, nolin=s < 0.18)
    col = mix(STEEL, STEEL_HOT, glow)
    for side in (-0.64, 0.64):
        for i in range(n - 1):
            x0, y0, w0, s0 = pts[i]; x1, y1, w1, s1 = pts[i + 1]
            a = (x0 + side * w0, y0); b = (x1 + side * w1, y1)
            if gaps and i % 3 == 2:
                b = (lerp(a[0], b[0], 0.8), lerp(a[1], b[1], 0.8))
            ww = max(2, 30 * s0 * hw / 520)
            dr.line([a, b], col, ww, nolin=s0 < 0.2)
            if s0 > 0.25: dr.line([(a[0] - ww * 0.15, a[1]), (b[0] - ww * 0.15, b[1])], mix(col, (255, 255, 255), 0.5), ww * 0.25, nolin=True)
    return pts

def via_lado(dr, x0, x1, y, t, gap=0, seg=330, shine=0.0, glow=0.0):
    """Vía vista de lado. y = parte de arriba del riel."""
    dr.rrect(x0, y + 26, x1, y + 90, 10, BAL)
    for k in range(int((x1 - x0) / 85) + 1):
        sx = x0 + k * 85
        dr.rrect(sx, y + 14, sx + 52, y + 40, 4, WOOD)
    col = mix(STEEL, STEEL_HOT, glow)
    x = x0
    while x < x1:
        dr.rrect(x, y - 4, min(x1, x + seg - gap), y + 18, 4, col)
        dr.rrect(x, y - 4, min(x1, x + seg - gap), y + 2, 2, mix(col, (255, 255, 255), 0.5), nolin=True)
        x += seg
    if shine > 0:
        sx = x0 + ((t * 0.6) % 1) * (x1 - x0)
        dr.poly([(sx, y - 4), (sx + 40, y - 4), (sx + 20, y + 18), (sx - 20, y + 18)], (255, 255, 255), nolin=True)

def humo(dr, x, y, t, s=1.0, n=5, dirx=-1, col=(240, 240, 244)):
    for k in range(n):
        ph = (t * 0.9 + k / n) % 1
        dr.ell(x + dirx * ph * 260 * s, y - ph * 280 * s, (30 + 60 * ph) * s, (26 + 50 * ph) * s, col, nolin=ph > 0.6)

def loco(dr, x, y, s, t, col=(180, 40, 40), acc=(246, 200, 60), name="", run=0.0, face=1, driver=None, smoke=True):
    """Locomotora de vapor de lado. (x, y) = centro sobre el riel."""
    F = lambda dx: x + face * dx * s; S = lambda v: v * s
    def R(ax, ay, bx, by, r, c, **k): dr.rrect(min(F(ax), F(bx)), y - S(ay), max(F(ax), F(bx)), y - S(by), S(r), c, **k)
    if smoke: humo(dr, F(130), y - S(330), t, s * 1.2, dirx=-face)
    R(-250, 300, -90, 60, 10, mix(col, (0, 0, 0), 0.2))   # fondo de cabina
    if driver: driver(F(-170), y - S(130))
    R(-260, 320, -80, 290, 8, (40, 36, 40))   # techo
    R(-250, 300, -230, 60, 4, col); R(-110, 300, -90, 60, 4, col)
    R(-250, 160, -90, 60, 8, col, shade=True)   # panel bajo de cabina
    R(-110, 220, 180, 80, 50, col, shade=True)   # caldera
    for bx in (-40, 60, 150): R(bx, 220, bx + 14, 80, 4, acc)
    dr.ell(F(185), y - S(150), S(50), S(70), (60, 60, 70), shade=True)
    dr.poly([(F(100), y - S(215)), (F(160), y - S(215)), (F(175), y - S(330)), (F(85), y - S(330))], (40, 36, 40))
    R(80, 345, 180, 320, 6, (40, 36, 40))
    dr.ell(F(20), y - S(228), S(42), S(30), acc)
    dr.rrect(min(F(150), F(200)), y - S(250), max(F(150), F(200)), y - S(205), S(8), (255, 230, 120))
    dr.poly([(F(190), y - S(70)), (F(270), y - S(4)), (F(190), y - S(4))], (60, 56, 60))
    dr.text(F(-170), y - S(136), name, int(S(34)), (255, 255, 255), stroke=4) if name else None
    for wx, wr in ((-170, 55), (-40, 66), (90, 66), (210, 34)):
        dr.ell(F(wx), y - S(wr), S(wr), S(wr), (40, 36, 44))
        dr.ell(F(wx), y - S(wr), S(wr * 0.7), S(wr * 0.7), acc)
        for j in range(4):
            a = run * t * 6 + j * math.pi / 4
            dr.line([(F(wx) + math.cos(a) * S(wr * 0.7), y - S(wr) + math.sin(a) * S(wr * 0.7)), (F(wx) - math.cos(a) * S(wr * 0.7), y - S(wr) - math.sin(a) * S(wr * 0.7))], (40, 36, 44), S(8), nolin=True)
    a = run * t * 6
    dr.line([(F(-40) + math.cos(a) * S(40), y - S(66) + math.sin(a) * S(40)), (F(90) + math.cos(a) * S(40), y - S(66) + math.sin(a) * S(40))], (200, 200, 210), S(12))

def loco_frente(dr, x, y, s, t, col=(120, 60, 160), smoke=True):
    S = lambda v: v * s
    if smoke: humo(dr, x, y - S(420), t, s, dirx=1)
    for sx in (-1, 1): dr.ell(x + sx * S(120), y - S(40), S(36), S(42), (40, 36, 44))
    dr.rrect(x - S(160), y - S(330), x + S(160), y - S(60), S(20), col, shade=True)
    dr.ell(x, y - S(210), S(118), S(118), (70, 70, 80), shade=True)
    dr.ell(x, y - S(210), S(70), S(70), (50, 50, 58))
    dr.rrect(x - S(36), y - S(440), x + S(36), y - S(320), S(8), (40, 36, 40))
    dr.ell(x, y - S(345), S(40), S(34), (255, 236, 130))
    dr.poly([(x - S(170), y - S(60)), (x + S(170), y - S(60)), (x + S(110), y), (x - S(110), y)], (60, 56, 60))

def perfecto(dr, x, y, s, t, mouth=0.0, expr="smug", arm_r=20, arm_l=20, look=(0, 0), regla=False, steam=0.0, red=0.0, elbow_r=0):
    """Don Perfecto: alto y flaco, chaleco morado, moño rojo, pelo engominado con raya perfecta. Alto ≈ 1060*s."""
    S = lambda v: v * s
    bob = S(5) * math.sin(t * 2.4 + 1)
    skin = mix((242, 208, 178), (240, 120, 100), red)
    for sx in (-1, 1):
        dr.rrect(x + sx * S(34) - S(20), y - S(430), x + sx * S(34) + S(20), y - S(14), S(10), (40, 40, 56))
        dr.poly([(x + sx * S(34) - S(26), y - S(30)), (x + sx * S(34) + sx * S(70), y - S(14)), (x + sx * S(34) - S(26), y)], (24, 24, 30))
    dr.rrect(x - S(95), y - S(780) + bob, x + S(95), y - S(400), S(40), (246, 246, 250), shade=True)
    for sx in (-1, 1): dr.poly([(x + sx * S(18), y - S(770) + bob), (x + sx * S(96), y - S(740) + bob), (x + sx * S(92), y - S(410)), (x + sx * S(14), y - S(430))], (120, 60, 160))
    for k in range(4): dr.ell(x - S(28), y - S(680) + k * S(66) + bob, S(9), S(9), (246, 200, 60))
    dr.line([(x - S(10), y - S(560)), (x - S(80), y - S(520))], (246, 200, 60), S(5))   # cadena de reloj
    hands = []
    for sx, ang, eb in ((-1, arm_l, 0), (1, arm_r, elbow_r)):
        shx, shy = x + sx * S(100), y - S(750) + bob
        a1 = math.radians(ang); a2 = math.radians(ang + eb)
        ex, ey = shx + sx * math.sin(a1) * S(160), shy + math.cos(a1) * S(160)
        hx, hy = ex + sx * math.sin(a2) * S(150), ey + math.cos(a2) * S(150)
        dr.line([(shx, shy), (ex, ey), (hx, hy)], (246, 246, 250), S(38))
        dr.ell(hx, hy, S(24), S(24), skin); hands.append((hx, hy))
    if regla:
        hx, hy = hands[1]
        dr.poly([(hx - S(14), hy - S(380)), (hx + S(26), hy - S(380)), (hx + S(26), hy + S(60)), (hx - S(14), hy + S(60))], (250, 210, 60))
        for k in range(10): dr.line([(hx - S(14), hy - S(360) + k * S(42)), (hx + S(4), hy - S(360) + k * S(42))], INK, S(4), nolin=True)
        dr.ell(hx, hy, S(24), S(24), skin)
    dr.rrect(x - S(30), y - S(840) + bob, x + S(30), y - S(760) + bob, S(10), skin)
    for sx in (-1, 1): dr.poly([(x, y - S(780) + bob), (x + sx * S(50), y - S(806) + bob), (x + sx * S(50), y - S(754) + bob)], (200, 40, 50))
    dr.ell(x, y - S(780) + bob, S(14), S(14), (170, 30, 40))
    hx, hy = x, y - S(950) + bob
    dr.ell(hx, hy, S(105), S(140), skin, shade=True)
    dr.chord(hx, hy - S(40), S(112), S(118), 180, 360, (30, 28, 36))   # pelo engominado
    dr.poly([(hx - S(112), hy - S(40)), (hx - S(100), hy - S(110)), (hx - S(80), hy - S(40))], (30, 28, 36))
    dr.line([(hx - S(30), hy - S(156)), (hx - S(36), hy - S(60))], skin, S(6), nolin=True)   # raya perfecta
    dr.line([(hx + S(10), hy - S(140)), (hx + S(70), hy - S(110))], (200, 210, 240), S(10), nolin=True)   # brillo
    for sx in (-1, 1):
        ex, ey = hx + sx * S(42), hy + S(4)
        big = 1.35 if expr == "shock" else 1.0
        dr.ell(ex, ey, S(22) * big, S(24) * big, (255, 255, 255))
        dr.ell(ex + look[0] * S(6), ey + look[1] * S(6), S(9), S(11), INK)
        if expr == "smug": dr.chord(ex, ey - S(2), S(24), S(26), 180, 360, skin)   # párpado a media asta
        tilt = {"smug": -12, "angry": 18, "shock": -16, "cry": -20}.get(expr, 0)
        dr.line([(ex - S(26), ey - S(44) + sx * S(tilt) * 0.5), (ex + S(26), ey - S(44) - sx * S(tilt) * 0.5)], (30, 28, 36), S(8))
    dr.poly([(hx, hy + S(10)), (hx + S(40), hy + S(58)), (hx, hy + S(62))], mix(skin, (200, 120, 100), 0.3))   # nariz puntiaguda
    for sx in (-1, 1): dr.line([(hx, hy + S(76)), (hx + sx * S(46), hy + S(70)), (hx + sx * S(60), hy + S(50))], (30, 28, 36), S(8))
    mo = clamp(mouth)
    if mo > 0.06 or expr in ("shock", "cry"):
        dr.ell(hx, hy + S(100), S(30), S(8 + 28 * max(mo, 0.5 if expr in ("shock", "cry") else 0)), (100, 24, 34))
    elif expr == "smug":
        dr.line([(hx - S(26), hy + S(98)), (hx + S(30), hy + S(92))], (100, 24, 34), S(7))
    else:
        dr.chord(hx, hy + S(90), S(28), S(20), 0, 180, (100, 24, 34))
    if steam > 0:
        for k in range(4):
            ph = (t * 1.3 + k / 4) % 1
            for sx in (-1, 1): dr.ell(hx + sx * (S(110) + ph * S(80)), hy - S(30) - ph * S(160), S(24 + 30 * ph), S(20 + 24 * ph), (250, 250, 250), nolin=True)
    return dict(hands=hands, head=(hx, hy))

def vapor(dr, x, y, s, t, mouth=0.0, expr="angry", arm_r=20, arm_l=20, jump=0.0, look=(0, 0), red=0.0, steam=0.0):
    """Don Vapor: dueño del ferrocarril, redondo, traje verde, chistera, bigotazo blanco y monóculo. Alto ≈ 1010*s."""
    S = lambda v: v * s
    y = y - S(jump); bob = S(6) * math.sin(t * 2.0)
    skin = mix((246, 196, 170), (236, 90, 80), red); suit = (52, 88, 70)
    for sx in (-1, 1):
        dr.rrect(x + sx * S(80) - S(36), y - S(160), x + sx * S(80) + S(36), y - S(10), S(14), (40, 44, 48))
        dr.ell(x + sx * S(90), y - S(10), S(60), S(24), (30, 26, 26))
    dr.ell(x, y - S(340) + bob, S(230), S(230), suit, shade=True)
    dr.poly([(x - S(70), y - S(540) + bob), (x + S(70), y - S(540) + bob), (x, y - S(330) + bob)], (246, 246, 246))
    dr.ell(x, y - S(300) + bob, S(150), S(150), (186, 50, 50))   # chaleco rojo
    for k in range(3): dr.ell(x, y - S(400) + k * S(70) + bob, S(10), S(10), (246, 200, 60))
    dr.line([(x, y - S(330) + bob), (x + S(60), y - S(280) + bob), (x + S(110), y - S(310) + bob)], (246, 200, 60), S(6))
    dr.ell(x + S(116), y - S(312) + bob, S(20), S(20), (246, 200, 60))
    hands = []
    for sx, ang in ((-1, arm_l), (1, arm_r)):
        shx, shy = x + sx * S(190), y - S(470) + bob
        a = math.radians(ang)
        hx, hy = shx + sx * math.sin(a) * S(230), shy + math.cos(a) * S(230)
        dr.line([(shx, shy), (hx, hy)], suit, S(70))
        dr.ell(hx, hy, S(40), S(40), skin); hands.append((hx, hy))
    hx, hy = x, y - S(680) + bob
    dr.ell(hx, hy, S(150), S(140), skin, shade=True)
    for sx in (-1, 1): dr.ell(hx + sx * S(138), hy + S(20), S(36), S(70), (246, 246, 246))   # patillas
    for sx in (-1, 1):
        ex, ey = hx + sx * S(55), hy - S(30)
        dr.ell(ex, ey, S(22), S(24), (255, 255, 255))
        dr.ell(ex + look[0] * S(6), ey + look[1] * S(6), S(10), S(12), INK)
        tilt = {"angry": 22, "happy": -10, "shock": -14}.get(expr, 0)
        dr.line([(ex - S(30), ey - S(40) - sx * S(tilt) * 0.5), (ex + S(30), ey - S(40) + sx * S(tilt) * 0.5)], (246, 246, 246), S(16))
    # monóculo
    X, Y0 = dr.cam.p(hx + S(55), hy - S(30)); r = dr.cam.s(S(36))
    dr.d.ellipse([X - r, Y0 - r, X + r, Y0 + r], outline=(246, 200, 60), width=max(3, int(dr.cam.s(S(8)))))
    dr.line([(hx + S(90), hy - S(20)), (hx + S(120), hy + S(120))], (246, 200, 60), S(4), nolin=True)
    mo = clamp(mouth)
    if mo > 0.06 or expr == "shock":
        dr.ell(hx, hy + S(88), S(46), S(10 + 36 * max(mo, 0.5 if expr == "shock" else 0)), (100, 24, 34))
    elif expr == "happy":
        dr.chord(hx, hy + S(80), S(46), S(34), 0, 180, (100, 24, 34))
    for sx in (-1, 1): dr.ell(hx + sx * S(56), hy + S(56), S(70), S(32), (250, 250, 250))   # bigotazo
    dr.ell(hx, hy + S(26), S(34), S(28), (230, 100, 100))   # nariz
    # chistera
    dr.rrect(hx - S(190), hy - S(130), hx + S(190), hy - S(100), S(14), (30, 28, 32))
    dr.rrect(hx - S(115), hy - S(340), hx + S(115), hy - S(110), S(12), (36, 34, 40), shade=True)
    dr.rrect(hx - S(115), hy - S(170), hx + S(115), hy - S(130), S(4), (186, 50, 50))
    if steam > 0:
        for k in range(4):
            ph = (t * 1.5 + k / 4) % 1
            dr.ell(hx + S(30) * math.sin(k + t * 3), hy - S(360) - ph * S(240), S(30 + 40 * ph), S(24 + 30 * ph), (250, 250, 250), nolin=True)
    return dict(hands=hands, head=(hx, hy))

def termometro(img, x, y, val, txt):
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([x - 40, y - 330, x + 40, y + 20], radius=40, fill=(250, 250, 250), outline=INK, width=8)
    d.ellipse([x - 70, y - 20, x + 70, y + 120], fill=(230, 50, 40), outline=INK, width=8)
    top = y - 20 - 290 * clamp(val)
    d.rounded_rectangle([x - 18, top, x + 18, y + 30], radius=18, fill=(230, 50, 40))
    for k in range(6): d.line([(x + 40, y - 40 - k * 50), (x + 64, y - 40 - k * 50)], fill=INK, width=6)
    d.text((x, y - 390), txt, font=font(74), fill=(255, 255, 255), anchor="mm", stroke_width=9, stroke_fill=INK)

def calor_ondas(img, t, a=1.0):
    d = ImageDraw.Draw(img)
    for k in range(int(10 * a)):
        ph = (t * 0.7 + k * 0.17) % 1
        y = 1500 - ph * 900; x = 80 + (k * 211) % 920
        pts = [(x + 14 * math.sin(j * 0.9 + t * 6 + k), y - j * 22) for j in range(8)]
        d.line(pts, fill=(255, 210, 150), width=6)

# ------------------------------------------------------------ planos
SHOTS = []
def shot(fn): SHOTS.append(fn); return fn
def tl(k, frac): return LEAD + len(VOZ[k]) / SR * frac
def D_(cam, bg=(0, 0, 0)): return D(cam, bg)

@shot
def s01(t, D, T):    # gancho: vía en perspectiva, zoom a un hueco
    u = ease(t / D)
    cam = Cam(lerp(540, 640, u), lerp(960, 1220, u), lerp(1.0, 1.55, u))
    dr = D_(cam); valle(dr, t, 0.0, yh=760)
    via(dr, 540, 760, 2200, 560, t, gaps=True)
    loco_frente(dr, 540, 790, 0.12 + 0.05 * u, t)
    f = tinta(dr); img = acabado(f, T)
    burst(img, "¿POR QUÉ?", 540, 380, 150, t - 0.1, ang=-6)
    if t > tl(0, 0.55):   # círculo sobre el hueco
        z = 1 + 2 * 0.55 + 0.55 * 0.9; s = 1 / z
        gx, gy = 540 + 0.64 * 560 * s, 760 + 1440 * s
        X, Y = cam.p(gx, gy); k = eob((t - tl(0, 0.55)) / 0.3); r = 110 * k + 1
        d = ImageDraw.Draw(img)
        d.ellipse([X - r, Y - r, X + r, Y + r], outline=(255, 60, 60), width=14)
        d.text((X - 40, Y - r - 70), "¿HUECO?", font=font(80 * k + 1), fill=(255, 230, 60), anchor="mm", stroke_width=10, stroke_fill=INK)
    return img, 0

@shot
def s02(t, D, T):    # portal → Nico maquinista cae en la gran carrera
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
    dr = D_(cam); valle(dr, t, 0.0, yh=1000)
    for px in (120, 960):   # postes con banderines
        dr.rrect(px - 14, 520, px + 14, 1300, 4, WOOD_D)
    for k in range(9):
        bx = 130 + k * 92; by = 560 + 40 * math.sin(k / 8 * math.pi)
        dr.poly([(bx, by), (bx + 80, by + 6), (bx + 40, by + 80)], PAS[k % 5])
    via_lado(dr, -300, 1400, 1380, t, gap=0)
    loco(dr, 140, 1380, 0.75, t, col=(120, 60, 160), name="PERFECTO", smoke=True)
    via_lado(dr, -300, 1400, 1640, t, gap=0)
    for k in range(4): persona(dr, -40 + k * 360, 2050 + (k % 2) * 30, 0.42, t, PAS[k], ph=k)
    portal(dr, 620, 1150, 220, t, 1 - ease((tt - 0.7) / 0.4))
    land = clamp(tt / 0.35)
    sq = 1 - 0.3 * math.exp(-tt * 7) * math.cos(tt * 20) if land >= 1 else 1.15
    nico(dr, 640, lerp(1050, 1860, land ** 2), 0.66, t, traje="maquinista", arms=(140, 140) if land < 1 else (30, 165), elbows=(0, 15), expr="shock" if tt < 0.9 else "happy", squash=sq, look=(-0.3, -0.6))
    f = tinta(dr)
    if tt < 0.2: f += 255 * (1 - tt / 0.2)
    img = acabado(f, T)
    if tt > 0.4: cartel(img, tt - 0.4, "GRAN CARRERA", "DEL FERROCARRIL · 1870", y=300, c2=(186, 50, 50))
    return img, 0

@shot
def s03(t, D, T):    # Don Perfecto presume sus rieles pegaditos
    u = ease(t / D)
    cam = Cam(lerp(560, 520, u), 1080, lerp(1.15, 1.25, u))
    dr = D_(cam); valle(dr, t, 0.0, yh=1000)
    via_lado(dr, -400, 1500, 1500, t, gap=0, shine=1.0)
    perfecto(dr, 420, 1900, 0.95, t, mouth=boca(2, t), expr="smug" if boca(2, t) < 0.3 else "happy", arm_r=160, elbow_r=-20, arm_l=25, regla=True, look=(0.5, 0))
    f = tinta(dr); img = acabado(f, T)
    nombre(img, t - 0.1, "DON PERFECTO", "el constructor sin errores", col=(120, 60, 160))
    if t > tl(2, 0.35): burst(img, "¡SIN HUECOS!", 760, 1300, 96, t - tl(2, 0.35), col=(220, 228, 240), ang=8)
    return img, 0

@shot
def s04(t, D, T):    # PASO 1: Nico deja un huequito entre cada riel
    u = ease(t / D)
    cam = Cam(560, lerp(1060, 1100, u), lerp(1.12, 1.22, u))
    dr = D_(cam); valle(dr, t, 0.0, yh=1000)
    via_lado(dr, -400, 1500, 1500, t, gap=46)
    nico(dr, 380, 1900, 0.72, t, traje="maquinista", arms=(20, 120), elbows=(0, 30), expr="happy", look=(0.8, 0.6))
    # Nico pone un riel nuevo con un martillo
    f = tinta(dr); img = acabado(f, T)
    tarjeta_paso(img, t, 1, "EL “ERROR”")
    if t > tl(3, 0.55):   # lupa sobre el hueco
        k = eob((t - tl(3, 0.55)) / 0.3); d = ImageDraw.Draw(img)
        X, Y = cam.p(4 * 330 - 400 - 23, 1505)
        r = 150 * k + 1; cx, cy = 790, 760
        d.line([(X, Y), (cx + 60, cy + r * 0.9)], fill=INK, width=10)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(196, 226, 250), outline=INK, width=12)
        d.rectangle([cx - r * 0.9, cy - 20 * k, cx - 26 * k, cy + 30 * k], fill=STEEL, outline=INK, width=5)
        d.rectangle([cx + 26 * k, cy - 20 * k, cx + r * 0.9, cy + 30 * k], fill=STEEL, outline=INK, width=5)
        d.text((cx, cy + 90 * k), "HUECO", font=font(46 * k + 1), fill=(220, 40, 40), anchor="mm")
    return img, 0

@shot
def s05(t, D, T):    # Don Vapor furioso
    cam = Cam(540, 1150, lerp(1.38, 1.48, ease(t / D)))
    dr = D_(cam); valle(dr, t, 0.0, yh=1000)
    via_lado(dr, -400, 1500, 1580, t, gap=46)
    vapor(dr, 540, 1960, 1.05, t, mouth=boca(4, t), expr="angry", arm_r=150 + 14 * math.sin(t * 9), arm_l=40, red=clamp(t / 1.0) * 0.6, steam=1.0)
    f = tinta(dr); img = acabado(f, T)
    burst(img, "¿¡HUECOS!?", 540, 380, 130, t - 0.05, col=(255, 90, 70), ang=-6)
    nombre(img, t - 0.15, "DON VAPOR", "dueño del ferrocarril", y=1400, col=(52, 88, 70))
    return img, 2 * math.sin(t * 40) if t < 1.0 else 0

@shot
def s06(t, D, T):    # Nico: confíe en mí, es para el verano
    cam = Cam(540, 1080, 1.6)
    dr = D_(cam); valle(dr, t, 0.0, yh=1000)
    nico(dr, 560, 1720, 0.72, t, traje="maquinista", arms=(25, 120), elbows=(0, 60), expr="smug" if boca(5, t) < 0.2 else "happy", mouth=boca(5, t), look=(-0.4, 0))
    f = tinta(dr); img = acabado(f, T)
    if t > tl(5, 0.55):   # hoja de calendario con sol: VERANO
        k = eob((t - tl(5, 0.55)) / 0.3); d = ImageDraw.Draw(img)
        x0, y0 = 600, 330
        d.rounded_rectangle([x0, y0, x0 + 380 * k + 1, y0 + 330 * k + 1], radius=20, fill=(252, 250, 244), outline=INK, width=8)
        d.rectangle([x0 + 8, y0 + 8, x0 + 380 * k - 8, y0 + 80 * k], fill=(220, 60, 50))
        d.text((x0 + 190 * k, y0 + 44 * k), "VERANO", font=font(48 * k + 1), fill=(255, 255, 255), anchor="mm")
        d.ellipse([x0 + 190 * k - 70 * k, y0 + 200 * k - 70 * k, x0 + 190 * k + 70 * k, y0 + 200 * k + 70 * k], fill=(255, 200, 40), outline=INK, width=6)
    return img, 0

@shot
def s07(t, D, T):    # el tren de Don Perfecto arranca primero
    u = ease(t / D)
    cam = Cam(540, 1150, 1.0)
    dr = D_(cam); valle(dr, t, 0.0, yh=1000)
    via_lado(dr, -400, 1500, 1420, t, gap=0)
    lx = lerp(260, 1250, ease(clamp((t - 0.5) / (D - 0.5))))
    loco(dr, lx, 1420, 0.85, t, col=(120, 60, 160), name="PERFECTO", run=2.5)
    via_lado(dr, -400, 1500, 1660, t, gap=40)
    loco(dr, -60, 1660, 0.6, t, col=(40, 150, 140), acc=TURQ, name="NICO", smoke=False)
    nico(dr, 300, 1960, 0.52, t, traje="maquinista", arms=(10, 10), expr="worried", look=(1, 0))
    for k in range(5): persona(dr, 520 + k * 130, 2080 + (k % 2) * 30, 0.4, t, PAS[k % 5], ph=k)
    f = tinta(dr); img = acabado(f, T)
    if t > tl(6, 0.6): burst(img, "¡VA GANANDO!", 620, 460, 100, t - tl(6, 0.6), col=(200, 150, 255), ang=-5)
    return img, 0

@shot
def s08(t, D, T):    # PASO 2: llega el verano, el sol calienta los rieles
    u = ease(t / D); cal = ease(clamp((t - 0.6) / (D - 1.2)))
    cam = Cam(540, lerp(980, 1060, u), lerp(1.0, 1.1, u))
    dr = D_(cam); valle(dr, t, cal, yh=820)
    via(dr, 540, 820, 2200, 560, t, glow=cal * 0.7)
    f = tinta(dr); add_glow(f, 820, 330, 260 + 120 * cal, (255, 200, 80), 0.3 + 0.3 * cal)
    img = acabado(f, T)
    calor_ondas(img, t, cal)
    tarjeta_paso(img, t, 2, "EL CALOR")
    if t > 1.0: termometro(img, 170, 1300, 0.25 + 0.7 * cal, f"{int(20 + 32 * cal)} °C")
    return img, 0

@shot
def s09(t, D, T):    # los rieles pegaditos se doblan como un fideo
    w = ease(clamp((t - tl(8, 0.35)) / 1.6)) * 1.0
    cam = Cam(540, 1060, 1.05)
    dr = D_(cam); valle(dr, t, 1.0, yh=820)
    via(dr, 540, 820, 2200, 560, t, wave=w, zc=3.4, glow=0.75)
    loco_frente(dr, 540, 830 + 1380 / 8.2, 0.42, t)
    f = tinta(dr); img = acabado(f, T)
    calor_ondas(img, t, 1.0)
    if w > 0.1: burst(img, "¡CRRRAC!", 300, 1180, 100, t - tl(8, 0.35) - 0.3, col=(255, 160, 60), ang=-10)
    if w > 0.6: burst(img, "¡COMO UN FIDEO!", 560, 420, 92, t - tl(8, 0.35) - 1.2, col=(255, 230, 60), ang=5)
    return img, (3 * math.sin(t * 30) if 0.1 < w < 0.95 else 0)

@shot
def s10(t, D, T):    # Don Perfecto en pánico
    cam = Cam(540, 1100, 1.25)
    dr = D_(cam); valle(dr, t, 1.0, yh=900)
    via(dr, 540, 900, 2300, 600, t, wave=1.0, zc=3.0, glow=0.75)
    perfecto(dr, 540, 2010, 1.0, t, mouth=boca(9, t), expr="shock", arm_r=165, arm_l=165, elbow_r=40, red=0.4, steam=1.0)
    f = tinta(dr); img = acabado(f, T)
    burst(img, "¿¡OLAS!?", 540, 400, 130, t - 0.1, col=(200, 150, 255), ang=6)
    return img, 2 * math.sin(t * 34)

@shot
def s11(t, D, T):    # PASO 3: diagrama sin huecos vs con huecos
    cam = Cam(540, 960, 1.0)
    dr = D_(cam, bg=(28, 58, 108))
    dr.rrect(-600, -400, 1700, 2400, 0, (28, 58, 108), nolin=True)
    for k in range(-2, 16): dr.line([(k * 80, -200), (k * 80, 2200)], (44, 78, 132), 3, nolin=True)
    for k in range(-2, 30): dr.line([(-200, k * 80), (1300, k * 80)], (44, 78, 132), 3, nolin=True)
    k = ease(clamp((t - tl(10, 0.2)) / 2.4))
    col = mix(STEEL, STEEL_HOT, k * 0.7)
    # fila 1: sin huecos (topes a los lados) → se arquea
    y1 = 920
    for sx in (90, 990): dr.rrect(sx - 30, y1 - 120, sx + 30, y1 + 60, 6, (120, 90, 70))
    pts = [(120 + j * 8.6, y1 - 150 * k * math.sin(math.pi * j / 100)) for j in range(101)]
    dr.line(pts, col, 36)
    for j in range(1, 4): dr.line([(120 + j * 217, y1 - 150 * k * math.sin(math.pi * j / 4) - 22), (120 + j * 217, y1 - 150 * k * math.sin(math.pi * j / 4) + 22)], INK, 5, nolin=True)
    # fila 2: con huecos → cada riel crece y llena su hueco
    y2 = 1340; L0, g0 = 190, 36
    for j in range(4):
        x0 = 120 + j * (L0 + g0)
        dr.rrect(x0, y2 - 18, x0 + L0 + (g0 - 6) * k, y2 + 18, 6, col)
    f = tinta(dr); img = acabado(f, T); d = ImageDraw.Draw(img)
    tarjeta_paso(img, t, 3, "EL HUECO")
    d.text((540, y1 - 250), "SIN HUECOS", font=font(60), fill=(255, 120, 110), anchor="mm", stroke_width=8, stroke_fill=INK)
    d.text((540, y2 - 110), "CON HUECOS", font=font(60), fill=(130, 240, 150), anchor="mm", stroke_width=8, stroke_fill=INK)
    if k > 0.6:
        check(img, 960, y1 - 250, False, 0.8); check(img, 960, y2 - 110, True, 0.8)
    return img, 0

@shot
def s12(t, D, T):    # dato: riel de 25 m crece más de 1 cm
    cam = Cam(540, 960, 1.0)
    dr = D_(cam); rayos_fondo(dr, 540, 1000, t, (240, 170, 70), (250, 190, 90))
    k = ease(clamp((t - tl(11, 0.45)) / 1.0))
    dr.rrect(-40, 1000, 900 + 40 * k, 1060, 8, mix(STEEL, STEEL_HOT, 0.5 * k), shade=True)
    dr.rrect(-40, 1000, 900 + 40 * k, 1014, 4, (230, 236, 246), nolin=True)
    dr.rrect(960, 990, 1200, 1070, 8, STEEL)
    for j in range(6): dr.rrect(40 + j * 170, 1060, 100 + j * 170, 1100, 4, WOOD)
    f = tinta(dr); img = acabado(f, T); d = ImageDraw.Draw(img)
    d.line([(40, 900), (860, 900)], fill=INK, width=8)
    for x in (40, 860): d.line([(x, 870), (x, 930)], fill=INK, width=8)
    d.text((450, 840), "25 METROS", font=font(84), fill=(255, 255, 255), anchor="mm", stroke_width=10, stroke_fill=INK)
    cx, cy, r = 760, 1420, 200   # lupa en la punta
    d.line([(930, 1060), (cx + 60, cy - r + 20)], fill=INK, width=12)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(250, 246, 236), outline=INK, width=14)
    tip = cx + 40 + 90 * k
    d.rectangle([cx - r + 30, cy - 40, tip, cy + 40], fill=mix(STEEL, STEEL_HOT, 0.5 * k), outline=INK, width=6)
    d.rectangle([cx + 140, cy - 40, cx + r - 10, cy + 40], fill=STEEL, outline=INK, width=6)
    if k > 0.3: d.text((cx, cy + 110), "+1 cm", font=font(70), fill=(220, 50, 40), anchor="mm")
    burst(img, "¡CRECE!", 300, 520, 120, t - tl(11, 0.45), col=(255, 255, 255), ang=-6)
    return img, 0

@shot
def s13(t, D, T):    # Nico: el truco es dejarle espacio al calor
    cam = Cam(540, 1080, 1.55)
    dr = D_(cam); rayos_fondo(dr, 540, 900, t, (40, 150, 140), (60, 180, 166))
    nico(dr, 540, 1740, 0.74, t, traje="maquinista", arms=(25, 170), elbows=(0, -10), expr="happy", mouth=boca(12, t), look=(0.3, -0.4))
    f = tinta(dr); img = acabado(f, T)
    if t > tl(12, 0.5): burst(img, "¡ESPACIO AL CALOR!", 540, 420, 92, t - tl(12, 0.5), ang=-5)
    return img, 0

@shot
def s14(t, D, T):    # el tren de Nico pasa: clac-clac
    cam = Cam(540, 1150, 1.0)
    dr = D_(cam); valle(dr, t, 0.6, yh=1000)
    via_lado(dr, -400, 1500, 1560, t, gap=34, glow=0.3)
    lx = lerp(-300, 1300, t / D)
    def drv(wx, wy): nico(dr, wx, wy + 60, 0.32, t, traje="maquinista", arms=(160, 20), elbows=(-20, 0), expr="happy", mouth=boca(13, t), look=(0.6, -0.2))
    loco(dr, lx, 1560, 1.0, t, col=(40, 150, 140), acc=TURQ, name="NICO", run=2.5, driver=drv)
    f = tinta(dr); img = acabado(f, T)
    for j in range(4):
        ph = (t * 2.2 + j * 0.5) % 2
        if ph < 0.5: burst(img, "¡CLAC!", 200 + j * 230, 1300 - (j % 2) * 80, 74, ph, col=(255, 255, 255), ang=-8 + j * 5)
    return img, 0

@shot
def s15(t, D, T):    # Don Vapor celebra: ¡jefe de vías!
    cam = Cam(540, lerp(1150, 1120, ease(t / D)), lerp(1.15, 1.22, ease(t / D)))
    dr = D_(cam); valle(dr, t, 0.2, yh=1000)
    via_lado(dr, -400, 1500, 1600, t, gap=34)
    vapor(dr, 720, 1900, 0.85, t, mouth=boca(14, t), expr="happy", arm_r=165, arm_l=165, jump=50 * abs(math.sin(t * 5)))
    nico(dr, 300, 1900, 0.62, t, traje="maquinista", arms=(20, 150), elbows=(0, 20), expr="happy_eyes", look=(1, 0))
    f = tinta(dr); img = acabado(f, T)
    burst(img, "¡JEFE DE VÍAS!", 540, 400, 100, t - tl(14, 0.4), ang=-5)
    return img, 0

@shot
def s16(t, D, T):    # remate: con los rieles doblados, Don Perfecto inventa la montaña rusa
    cam = Cam(540, 1060, 1.12)
    dr = D_(cam); valle(dr, t, 0.2, yh=1300)
    curva = lambda x: 1100 - 260 * math.sin((x + 60) / 230) * (0.6 + 0.4 * math.sin(x / 400))
    for x in range(-100, 1250, 120): dr.rrect(x - 12, curva(x), x + 12, 1500, 4, WOOD_D)
    dr.line([(x, curva(x)) for x in range(-200, 1301, 20)], (186, 50, 50), 26)
    dr.line([(x, curva(x) + 30) for x in range(-200, 1301, 20)], (120, 60, 160), 12)
    cx = lerp(-100, 1200, (t / D) ** 1.2); cy = curva(cx)
    perfecto(dr, cx, cy - 10, 0.42, t, expr="shock", arm_r=170, arm_l=170, steam=0.0)
    dr.rrect(cx - 110, cy - 115, cx + 110, cy - 10, 30, (240, 190, 60), shade=True)
    for k in range(5): persona(dr, 120 + k * 150, 1950 + (k % 2) * 30, 0.42, t, PAS[k % 5], ph=k)
    f = tinta(dr); img = acabado(f, T)
    cartel(img, t - 0.3, "MONTAÑA RUSA", "DE DON PERFECTO · 5 ¢", y=1400, c1=(120, 60, 160), c2=(186, 50, 50))
    if t > tl(15, 0.7): burst(img, "¡AAAAH!", 760, 700, 90, t - tl(15, 0.7), col=(255, 255, 255), ang=8)
    return img, 0

@shot
def s17(t, D, T):    # cierre + pregunta
    cam = Cam(540, 1000, 1.0)
    dr = D_(cam); rayos_fondo(dr, 540, 1000, -t, (18, 10, 30), (34, 20, 56))
    o = 1 - ease((t - D + 0.9) / 0.7)
    portal(dr, 540, 1080, 330, t, o)
    if t < D - 1.1:
        nico(dr, 540, 1560, 0.55, t, traje="maquinista", arms=(150, 30), elbows=(30, 0), expr="happy")
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
    rng = np.random.default_rng(7)
    def add(s, sig, g=1.0):
        i0 = int(s * sr); i1 = min(n, i0 + len(sig))
        if 0 <= i0 < n: out[i0:i1] += g * sig[:i1 - i0]
    def seg(d): return np.arange(int(d * sr)) / sr
    hz = lambda m: 440 * 2 ** ((m - 69) / 12)
    noise = rng.standard_normal(n)
    bp = lambda lo, hi: sosfilt(butter(2, [lo, hi], btype="band", fs=sr, output="sos"), noise)
    wh = bp(400, 3500); low = sosfilt(butter(2, 160, btype="low", fs=sr, output="sos"), noise); mid = bp(150, 900)
    S_ = STARTS
    def banjo(t0, t1, vol=1.0, e8=0.16):   # tonada de ferrocarril alegre
        mel = [67, 71, 74, 71, 72, 76, 74, 71, 69, 72, 76, 72, 74, 71, 67, 71]
        bass = [43, 50, 48, 50, 45, 50, 43, 50]
        k = 0; s = t0
        while s < t1:
            x = seg(e8 * 1.5); m = mel[k % len(mel)]
            pl = np.sin(2 * np.pi * hz(m) * x) * 0.6 + np.sin(2 * np.pi * hz(m) * 2 * x) * 0.25 + np.sin(2 * np.pi * hz(m) * 3 * x) * 0.1
            add(s, vol * 0.05 * pl * np.exp(-x * 14) * (1 - np.exp(-x * 400)))
            if k % 2 == 0:
                xb = seg(e8 * 2); bm = bass[(k // 2) % len(bass)]
                add(s, vol * 0.1 * np.exp(-xb * 6) * np.sin(2 * np.pi * hz(bm) * xb))
            if k % 2 == 1: add(s, vol * 0.04 * wh[:len(x)] * np.exp(-x * 50))
            k += 1; s += e8
    def chug(t0, t1, rate=0.22, g=0.12):
        s = t0
        while s < t1:
            x = seg(0.16); add(s, g * mid[:len(x)] * np.exp(-x * 18)); s += rate
    def silbato(t0, d=1.0, g=0.08):
        x = seg(d); env = np.minimum(1, x / 0.05) * np.minimum(1, (d - x) / 0.2)
        vib = 1 + 0.004 * np.sin(2 * np.pi * 6 * x)
        add(t0, g * env * sum(np.sin(2 * np.pi * f * vib * x) for f in (523, 659, 784)) / 3)
    def clac(t0, g=0.25):
        for dd in (0, 0.09):
            x = seg(0.05); add(t0 + dd, g * np.exp(-x * 90) * np.sin(2 * np.pi * 1300 * x) + g * 0.5 * wh[:len(x)] * np.exp(-x * 80))
    banjo(0, S_[7])
    x = seg(1.2); add(S_[1] + 0.1, 0.12 * np.sin(2 * np.pi * (200 + 600 * x) * x) * np.sin(np.pi * x / 1.2))   # portal
    x = seg(0.5); add(S_[1] + 1.3, 0.5 * np.exp(-x * 9) * np.sin(2 * np.pi * (60 + 40 * np.exp(-x * 20)) * x))
    silbato(S_[1] + 1.6, 0.8, 0.05)
    for k in range(5): add(S_[3] + 0.5 + k * 0.33, 0.25 * np.exp(-seg(0.12) * 40) * np.sin(2 * np.pi * 1800 * seg(0.12)))   # martillo
    x = seg(1.2); add(S_[4] + 0.2, 0.1 * low[:len(x)] * np.exp(-x * 2))   # vapor del jefe
    silbato(S_[6] + 0.3, 1.0, 0.09); chug(S_[6] + 0.5, S_[7], 0.18, 0.14)
    x = seg(DURS[7]); add(S_[7], 0.1 * np.sin(2 * np.pi * (110 + 40 * x / DURS[7]) * x) * (x / DURS[7]))   # calor que sube
    # pandeo: crujido metálico + golpe
    t0 = S_[8] + tl(8, 0.35)
    x = seg(1.6); add(t0, 0.18 * np.sin(2 * np.pi * (420 - 300 * x / 1.6 + 30 * np.sin(2 * np.pi * 13 * x)) * x) * np.exp(-x * 0.9))
    x = seg(0.6); add(t0 + 0.2, 0.35 * low[:len(x)] * np.exp(-x * 6))
    x = seg(0.6); add(S_[9] + 0.1, 0.1 * np.sin(2 * np.pi * (900 + 400 * np.sin(2 * np.pi * 9 * x)) * x) * np.exp(-x * 3))   # pánico
    x = seg(1.4); add(S_[10] + 2.6, 0.14 * np.exp(-x * 1.2) * (np.sin(2 * np.pi * 523 * x) + np.sin(2 * np.pi * 659 * x) + np.sin(2 * np.pi * 784 * x)) / 3)   # ¡encaja!
    banjo(S_[12], TOTAL, 0.8)
    chug(S_[13], S_[14], 0.2, 0.12); silbato(S_[13] + 0.1, 0.7, 0.08)
    s = S_[13] + 0.2
    while s < S_[14]: clac(s); s += 0.45
    x = seg(DURS[15]); add(S_[15] + 0.3, 0.08 * np.sin(2 * np.pi * (300 + 260 * np.sin(x * 2.5)) * x))   # montaña rusa
    for k in range(1, len(S_) - 1):
        x = seg(0.3); add(S_[k] - 0.08, 0.12 * wh[:len(x)] * np.sin(np.pi * x / 0.3))
    for k in (3, 7, 10):   # tarjetas de paso
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
