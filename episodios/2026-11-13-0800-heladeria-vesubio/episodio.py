#!/usr/bin/env python3
"""¿Qué pasaría si abres una heladería al lado del Vesubio en el año 79? (petición de comentarios: "a un volcán")
Estilo vector + cómic (motor/vc.py). Nico con traje de HELADERO (moño, delantal y franja del gorro turquesa)."""
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
DURS = [len(v) / SR + LEAD + 0.32 for v in VOZ]
DURS[0] += 0.3; DURS[8] += 0.8; DURS[12] += 0.9
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
    [("¿Y si abres", []), ("una HELADERÍA", ["HELADERÍA"]), ("al lado de un volcán…", ["volcán…"]), ("en el año 79?", ["79?"])],
    [("Ustedes pidieron", []), ("VOLCÁN", ["VOLCÁN"]), ("Nico cruza el portal", ["portal"]), ("y aparece en Pompeya…", ["Pompeya…"]), ("vestido de heladero", ["heladero"])],
    [("¡Helados!", ["¡Helados!"]), ("¡Helados fríos!", ["fríos!"]), ("¡Hace un calor", []), ("de volcán!", ["volcán!"])],
    [("Los romanos ya compraban", ["romanos"]), ("nieve de las montañas", ["nieve"]), ("para enfriar sus bebidas…", ["bebidas…"]), ("pero nunca habían probado", []), ("un helado de chocolate", ["chocolate"])],
    [("¡Por Júpiter!", ["Júpiter!"]), ("¡Está más frío", ["frío"]), ("que la nieve del Vesubio!", ["Vesubio!"]), ("¡Quiero diez!", ["diez!"])],
    [("En una hora", ["hora"]), ("toda Pompeya hace fila", ["fila"])],
    [("Pero hay un detalle…", ["detalle…"]), ("la montaña de al lado…", ["montaña"]), ("está echando humo", ["humo"])],
    [("Tranquilos, tranquilos…", []), ("es solo una montaña", ["montaña"]), ("¿Verdad?", ["¿Verdad?"])],
    [("No era una montaña", []), ("Era el VESUBIO", ["VESUBIO"]), ("año 79", ["79"]), ("y lanzó una nube de ceniza", ["ceniza"]), ("de más de 30 km de alto", ["30", "km"])],
    [("¡Cambio de menú!", ["menú!"]), ("¡Helado de lava!", ["lava!"]), ("¡Gratis!", ["¡Gratis!"]), ("¡Todos al portal!", ["portal!"]), ("¡Corran!", ["¡Corran!"])],
    [("Nico salva a toda la fila…", ["salva"]), ("y los trae al presente", ["presente"]), ("El problema:", ["problema:"]), ("el romano abrió", ["romano"]), ("su propia heladería…", ["heladería…"]), ("justo al frente", ["frente"])],
    [("Helado de nieve", []), ("del Vesubio", ["Vesubio"]), ("¡Dos por uno!", ["Dos", "uno!"])],
    [("Nos vemos en otro", []), ("mundo hipotético", ["hipotético"]), ("¿Qué negocio llevo", ["negocio"]), ("a la próxima época?", ["época?"])],
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
def mix(a, b, k): return tuple(int(lerp(a[i], b[i], k)) for i in range(3))

def cielo(dr, t, dark=0.0, y_top=-900):
    day = [(96, 170, 230), (130, 190, 236), (180, 210, 236), (250, 214, 170)]
    ash = [(40, 30, 34), (64, 44, 40), (110, 60, 40), (200, 90, 40)]
    for k in range(4):
        dr.rrect(-600, y_top + k * 420, 1700, y_top + (k + 1) * 420 + 4, 0, mix(day[k], ash[k], dark))

def volcan(dr, cx, by, w, h, t, humo=0.3, erup=0.0):
    pk = by - h
    dr.poly([(cx - w / 2, by), (cx - w * 0.09, pk), (cx + w * 0.02, pk + 10), (cx - w * 0.02, by)], (128, 104, 92))
    dr.poly([(cx - w * 0.02, by), (cx + w * 0.02, pk + 10), (cx + w * 0.09, pk), (cx + w / 2, by)], (92, 72, 66), shade=True)
    dr.poly([(cx - w * 0.38, by - h * 0.25), (cx - w * 0.2, by - h * 0.32), (cx - w * 0.05, by - h * 0.22), (cx - w * 0.02, by), (cx - w * 0.46, by)], (96, 140, 80))
    dr.poly([(cx + w * 0.42, by - h * 0.12), (cx + w * 0.2, by - h * 0.26), (cx + w * 0.02, by - h * 0.2), (cx - w * 0.02, by), (cx + w * 0.5, by)], (74, 112, 66), shade=True)
    if erup > 0:
        for k in range(3):
            xx = cx + (k - 1) * w * 0.05
            dr.line([(xx, pk + 20), (xx + (k - 1) * w * 0.1, pk + h * 0.45 * erup), (xx + (k - 1) * w * 0.16, pk + h * 0.8 * erup)], (255, 120, 30), w * 0.025, nolin=True)
    n = int(4 + 10 * humo)
    for k in range(n):
        ph = (t * (0.18 + 0.4 * erup) + k / n) % 1
        r = w * (0.05 + 0.12 * ph) * (1 + 2.2 * erup)
        x = cx + math.sin(k * 2.3 + t * 0.5) * w * 0.06 * (1 + ph * 3) + ph * w * 0.15 * (1 - erup)
        y = pk - ph * h * (0.9 + 3.5 * erup)
        g = int(lerp(190, 70, erup)) - int(30 * (k % 2))
        dr.ell(x, y, r, r * 0.85, (g, g - 6, g - 10), shade=(k % 3 == 0))
    if erup > 0.3:
        rng = np.random.default_rng(3)
        for k in range(14):
            ph = (t * 0.7 + k / 14) % 1
            vx = rng.uniform(-1, 1) * w * 0.55; vy = rng.uniform(0.7, 1.2) * h * 1.6
            x = cx + vx * ph; y = pk - vy * ph + 1.8 * h * ph * ph
            dr.ell(x, y, w * 0.018, w * 0.018, (255, 150, 40), nolin=True)

def casas(dr, t, gy=1380, dark=0.0):
    cols = [(214, 120, 70), (232, 180, 110), (190, 70, 60), (236, 206, 150), (200, 140, 90)]
    x = -420; k = 0
    while x < 1500:
        w = 230 + 60 * (k % 3); h = 330 + 90 * ((k * 7) % 3)
        c = mix(cols[k % 5], (60, 40, 40), dark * 0.6)
        dr.rrect(x, gy - h, x + w, gy, 0, c, shade=(k % 2 == 1))
        dr.poly([(x - 20, gy - h), (x + w / 2, gy - h - 70), (x + w + 20, gy - h)], mix((170, 70, 50), (60, 30, 30), dark * 0.6))
        dr.rrect(x + w * 0.35, gy - 170, x + w * 0.65, gy, 30, (70, 44, 36))
        dr.rrect(x + 30, gy - h + 60, x + 80, gy - h + 130, 6, (70, 44, 36))
        if k % 2 == 0:
            for j in range(3):
                cx = x + 40 + j * (w - 80) / 2
                dr.rrect(cx - 14, gy - h + 20, cx + 14, gy, 6, (244, 236, 216))
        x += w + 10; k += 1

def suelo(dr, gy=1380, col=(150, 140, 130)):
    dr.rrect(-600, gy, 1700, 2700, 0, col)
    for r in range(10):
        yy = gy + 20 + r * r * 8 + r * 26
        for j in range(-6, 18):
            xx = -300 + j * (90 + r * 10) + (r % 2) * 45
            dr.ell(xx, yy, 34 + r * 5, 10 + r * 2, (128, 120, 112))

def calle_pompeya(dr, t, humo=0.3, erup=0.0, dark=0.0, vx=760, vby=1000, vw=1200, vh=600):
    cielo(dr, t, dark)
    volcan(dr, vx, vby, vw, vh, t, humo, erup)
    casas(dr, t, 1380, dark)
    suelo(dr)

def calle_moderna(dr, t, gy=1380):
    for k, c in enumerate([(120, 190, 240), (150, 206, 244), (190, 224, 246), (220, 236, 246)]):
        dr.rrect(-600, -900 + k * 420, 1700, -900 + (k + 1) * 420 + 4, 0, c)
    x = -420; k = 0
    while x < 1500:
        w = 260 + 50 * (k % 3); h = 600 + 140 * ((k * 5) % 3)
        c = [(90, 110, 140), (130, 150, 170), (200, 170, 140), (110, 130, 120)][k % 4]
        dr.rrect(x, gy - h, x + w, gy, 0, c, shade=(k % 2 == 0))
        for r in range(int((h - 120) / 110)):
            for j in range(3):
                wx = x + 30 + j * (w - 60) / 3
                dr.rrect(wx, gy - h + 40 + r * 110, wx + (w - 60) / 3 - 24, gy - h + 110 + r * 110, 4, (200, 230, 250))
        x += w + 16; k += 1
    dr.rrect(-600, gy, 1700, gy + 90, 0, (190, 190, 196))
    dr.rrect(-600, gy + 90, 1700, 2700, 0, (70, 72, 80))
    for j in range(-4, 12): dr.rrect(j * 220, gy + 260, j * 220 + 120, gy + 280, 4, (250, 220, 60))

def portal(dr, x, y, r, t, o=1.0):
    R = r * o
    if R < 4: return
    dr.ell(x, y, R, R * 1.18, (40, 16, 70), nolin=True)
    for k in range(7):
        rr = R * (1 - k * 0.12); a0 = (t * (160 + 30 * k) * (1 if k % 2 else -1)) % 360
        X, Y = dr.cam.p(x, y); rx, ry = dr.cam.s(rr), dr.cam.s(rr * 1.18)
        dr.d.arc([X - rx, Y - ry, X + rx, Y + ry], a0, a0 + 240, fill=(90, 230, 255) if k % 2 == 0 else (190, 110, 255), width=max(3, int(dr.cam.s(R * 0.05))))
        dr.dn.arc([X - rx, Y - ry, X + rx, Y + ry], a0, a0 + 240, fill=255, width=max(3, int(dr.cam.s(R * 0.05))) + 4)

# ------------------------------------------------------------ utilería y personajes
def cono(dr, x, y, s, t, sabores=((120, 70, 40), (250, 160, 190)), melt=0.0, lava=False):
    """(x, y) = punta de arriba del cono."""
    S = lambda v: v * s
    dr.poly([(x - S(55), y), (x + S(55), y), (x, y + S(170))], (226, 172, 100), shade=True)
    for k in range(3):
        dr.line([(x - S(45) + k * S(30), y + S(5)), (x - S(5) + k * S(18), y + S(150))], (190, 130, 70), S(5))
    for k, c in enumerate(sabores):
        yy = y - S(35) - k * S(70)
        if lava: c = (255, 110 + 40 * (k % 2), 30)
        dr.ell(x, yy, S(66), S(52), c, shade=True)
        for j in range(4):
            dr.ell(x - S(48) + j * S(32), yy + S(40), S(17), S(15) + S(30) * melt * ((j + k) % 2), c)
    top = y - S(35) - (len(sabores) - 1) * S(70)
    dr.ell(x + S(8), top - S(50), S(14), S(14), (220, 30, 50))

def carrito(dr, x, y, s, t, letrero="HELADOS NICO", col=TURQ):
    S = lambda v: v * s
    dr.line([(x + S(150), y - S(260)), (x + S(150), y - S(720))], (120, 120, 130), S(14))
    for k in range(6):
        a0 = 180 + k * 30
        X, Y = dr.cam.p(x + S(150), y - S(700))
        r = dr.cam.s(S(300))
        dr.d.pieslice([X - r, Y - r * 0.6, X + r, Y + r * 0.6], a0, a0 + 30, fill=col if k % 2 == 0 else (252, 250, 244))
    dr.rrect(x - S(250), y - S(330), x + S(250), y - S(70), S(24), (252, 248, 236), shade=True)
    dr.rrect(x - S(250), y - S(200), x + S(250), y - S(150), S(4), col)
    dr.text(x, y - S(255), letrero, S(46), (40, 40, 60))
    for k, c in enumerate(((120, 70, 40), (250, 160, 190), (150, 230, 190), (255, 240, 170))):
        tx = x - S(180) + k * S(120)
        dr.rrect(tx - S(50), y - S(380), tx + S(50), y - S(330), S(10), (200, 204, 214))
        dr.ell(tx, y - S(385), S(46), S(30), c)
    for sx in (-1, 1):
        dr.ell(x + sx * S(170), y - S(55), S(55), S(55), (50, 50, 60))
        dr.ell(x + sx * S(170), y - S(55), S(20), S(20), (190, 190, 200))

def romano(dr, x, y, s, t, mouth=0.0, expr="happy", arm_r=20, arm_l=20, look=(0, 0), toga=(246, 240, 226), banda=(190, 40, 44), cono_r=False, bob_ph=0.0):
    """(x, y) = pies. Romano gordo con toga y corona de laurel. Altura ≈ 860*s."""
    S = lambda v: v * s
    bob = S(5) * math.sin(t * 2.4 + bob_ph)
    skin = (236, 184, 140)
    for sx in (-1, 1):
        dr.rrect(x + sx * S(55) - S(24), y - S(170), x + sx * S(55) + S(24), y - S(10), S(14), skin)
        dr.ell(x + sx * S(58), y - S(10), S(44), S(16), (120, 80, 50))
        for k in range(3): dr.line([(x + sx * S(55) - S(24), y - S(40) - k * S(40)), (x + sx * S(55) + S(24), y - S(30) - k * S(40))], (120, 80, 50), S(6))
    dr.ell(x, y - S(360) + bob, S(185), S(215), toga, shade=True)
    dr.poly([(x - S(140), y - S(520) + bob), (x - S(80), y - S(540) + bob), (x + S(170), y - S(260) + bob), (x + S(130), y - S(200) + bob)], banda)
    hands = []
    for sx, ang in ((-1, arm_l), (1, arm_r)):
        shx, shy = x + sx * S(150), y - S(500) + bob
        a = math.radians(ang)
        hx, hy = shx + sx * math.sin(a) * S(190), shy + math.cos(a) * S(190)
        dr.line([(shx, shy), (hx, hy)], skin, S(56))
        dr.ell(hx, hy, S(34), S(34), skin)
        hands.append((hx, hy))
    if cono_r:
        hx, hy = hands[1]; cono(dr, hx, hy - S(30), s * 0.9, t)
    hx, hy = x, y - S(680) + bob
    dr.ell(hx, hy + S(110), S(120), S(60), skin)   # papada
    for sx in (-1, 1): dr.ell(hx + sx * S(118), hy - S(50), S(42), S(50), (120, 110, 100))
    for sx in (-1, 1): dr.ell(hx + sx * S(146), hy + S(15), S(26), S(38), skin)
    dr.ell(hx, hy, S(145), S(150), skin, shade=True)
    for k in range(9):   # laurel
        a = math.pi * (1.05 + k * 0.1)
        lx, ly = hx + math.cos(a) * S(140), hy + math.sin(a) * S(120) - S(20)
        dr.ell(lx, ly, S(30), S(16), (80, 160, 60) if k % 2 else (60, 130, 50))
    if expr == "happy_eyes":
        for sx in (-1, 1):
            dr.chord(hx + sx * S(55), hy - S(10), S(30), S(22), 180, 360, INK)
            dr.chord(hx + sx * S(55), hy - S(4), S(26), S(16), 180, 360, skin)
    else:
        blink = (t % 3.6) < 0.12
        for sx in (-1, 1):
            ex, ey = hx + sx * S(55), hy - S(15)
            if blink: dr.rrect(ex - S(26), ey - S(3), ex + S(26), ey + S(5), S(3), INK); continue
            big = 1.25 if expr == "shock" else 1.0
            sm = s < 0.5
            dr.ell(ex, ey, S(28) * big * (1.15 if sm else 1), S(32) * big * (1.15 if sm else 1), (255, 255, 255), nolin=sm)
            dr.ell(ex + look[0] * S(9), ey + look[1] * S(9), S(13), S(15), INK, nolin=sm)
    tilt = {"angry": 14, "smug": 8, "shock": -10}.get(expr, -6)
    for sx in (-1, 1):
        ex = hx + sx * S(55)
        dr.line([(ex - S(32), hy - S(68) + sx * S(tilt) * 0.5), (ex + S(32), hy - S(68) - sx * S(tilt) * 0.5)], (110, 100, 90), S(14), nolin=s < 0.5)
    dr.ell(hx, hy + S(30), S(36), S(34), (224, 150, 120))
    mo = clamp(mouth)
    if mo > 0.06 or expr == "shock":
        mo = max(mo, 0.6 if expr == "shock" else 0)
        dr.ell(hx, hy + S(95), S(46), S(10 + 34 * mo), (110, 26, 36))
    elif expr == "smug":
        dr.line([(hx - S(40), hy + S(95)), (hx + S(10), hy + S(100)), (hx + S(46), hy + S(80))], (110, 26, 36), S(10))
    else:
        dr.chord(hx, hy + S(70), S(48), S(40), 0, 180, (110, 26, 36))
    for sx in (-1, 1): dr.ell(hx + sx * S(95), hy + S(55), S(22), S(13), (240, 140, 130))
    return dict(hands=hands, head=(hx, hy))

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
    d.rounded_rectangle([140, y, 940, y + 170], radius=30, fill=(244, 228, 190), outline=INK, width=8)
    d.text((540, y + 50), l1, font=font(70 * k + 1, F_SERIF), fill=(120, 40, 30), anchor="mm")
    d.text((540, y + 122), l2, font=font(50 * k + 1), fill=(40, 140, 160), anchor="mm")

def badge(img, T):
    d = ImageDraw.Draw(img); f = font(36); txt = "¿QUÉ PASARÍA SI…?"
    d.rounded_rectangle([36, 110, 36 + f.getlength(txt) + 44, 170], radius=16, fill=TURQ, outline=INK, width=5)
    d.text((58, 140), txt, font=f, fill=(255, 255, 255), anchor="lm")

def calor(img, t, a=1.0):
    d = ImageDraw.Draw(img)
    for k in range(5):
        x = 120 + k * 210; y0 = 900 - ((t * 120 + k * 60) % 300)
        pts = [(x + 14 * math.sin(y / 30 + t * 6), y) for y in range(int(y0), int(y0) + 160, 10)]
        d.line(pts, fill=(255, 250, 220), width=5)

# ------------------------------------------------------------ planos
SHOTS = []
def shot(fn): SHOTS.append(fn); return fn
def tl(k, frac): return LEAD + len(VOZ[k]) / SR * frac
def D_(cam, bg=(0, 0, 0)): return D(cam, bg)

@shot
def s01(t, D, T):    # gancho: Nico heladero con cono frente al volcán humeante
    cam = Cam(540, 1050, lerp(1.08, 1.22, ease(t / D)))
    dr = D_(cam); calle_pompeya(dr, t, humo=0.6)
    carrito(dr, 820, 1640, 0.8, t)
    info = nico(dr, 330, 1660, 0.66, t, traje="heladero", arms=(20, 150), elbows=(0, 30), expr="happy", mouth=0.3 * abs(math.sin(t * 9)))
    hx, hy = info["hands"][1]; cono(dr, hx, hy - 40, 0.8, t)
    f = tinta(dr); add_glow(f, *cam.p(760, 380), 260, (255, 200, 140), 0.3)
    img = acabado(f, T)
    burst(img, "¿Y SI…?", 540, 330, 160, t - 0.1, ang=-6)
    return img, 0

@shot
def s02(t, D, T):    # pidieron volcán → portal → aparece en Pompeya de heladero
    tp = D * 0.4
    if t < tp:
        cam = Cam(540, 1000, 1.0)
        dr = D_(cam, bg=(18, 10, 30))
        for k in range(16):
            a = k * math.pi / 8 + t * 0.4
            dr.poly([(540, 1000), (540 + math.cos(a) * 2000, 1000 + math.sin(a) * 2000), (540 + math.cos(a + 0.2) * 2000, 1000 + math.sin(a + 0.2) * 2000)], (34, 20, 56))
        portal(dr, 540, 1050, 300, t, ease(t / 0.4))
        walk = clamp((t - 0.3) / (tp - 0.4))
        if walk < 1: nico(dr, 540, 1560 - 30 * walk, 0.6 * (1 - 0.5 * walk), t, arms=(30, 30), expr="happy")
        f = tinta(dr); add_glow(f, 540, 1050, 380, (150, 120, 255), 0.5)
        if t > tp - 0.15: f += 255 * clamp((t - (tp - 0.15)) / 0.15)
        img = acabado(f, T)
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([110, 300, 970, 560], radius=36, fill=(255, 255, 255), outline=INK, width=8)
        d.text((540, 370), "USTEDES PIDIERON:", font=font(54), fill=INK, anchor="mm")
        d.text((540, 470), "VOLCÁN", font=font(120 * eob(t / 0.3) + 1), fill=(230, 70, 40), anchor="mm", stroke_width=6, stroke_fill=INK)
        return img, 0
    tt = t - tp
    cam = Cam(540, 1080, lerp(1.0, 1.08, ease(tt / (D - tp))))
    dr = D_(cam); calle_pompeya(dr, t, humo=0.5)
    portal(dr, 540, 1250, 220, t, 1 - ease((tt - 0.8) / 0.5))
    land = clamp(tt / 0.35)
    sq = 1 - 0.3 * math.exp(-tt * 7) * math.cos(tt * 20) if land >= 1 else 1.15
    nico(dr, 540, lerp(1150, 1700, land ** 2), 0.68, t, traje="heladero", arms=(140, 140) if land < 1 else (40, 160), elbows=(0, 20), expr="shock" if tt < 1.0 else "happy", squash=sq, look=(0.4, -0.5))
    f = tinta(dr)
    if tt < 0.2: f += 255 * (1 - tt / 0.2)
    img = acabado(f, T)
    if tt > 0.9: cartel(img, tt - 0.9, "POMPEYA", "AÑO 79 d. C.")
    return img, 0

@shot
def s03(t, D, T):    # ¡Helados fríos! (primer plano, calor)
    cam = Cam(450, 1180, 1.55)
    dr = D_(cam); calle_pompeya(dr, t, humo=0.5)
    carrito(dr, 790, 1700, 0.8, t)
    info = nico(dr, 420, 1720, 0.66, t, traje="heladero", arms=(150, 30), elbows=(20, 0), expr="happy", mouth=boca(2, t))
    hx, hy = info["hands"][0]; cono(dr, hx, hy - 40, 0.8, t, melt=0.5)
    f = tinta(dr); add_glow(f, W * 0.5, 300, 600, (255, 180, 80), 0.35)
    img = acabado(f, T); calor(img, t)
    burst(img, "¡HELADOS!", 560, 330, 140, t - 0.05, col=(120, 230, 255), ang=6)
    return img, 0

@shot
def s04(t, D, T):    # los romanos compraban nieve… pero nunca chocolate
    half = tl(3, 0.55)
    if t < half:
        cam = Cam(540, 1050, lerp(1.0, 1.1, ease(t / half)))
        dr = D_(cam); cielo(dr, t)
        dr.rrect(-600, 700, 1700, 1300, 0, (110, 160, 90))
        volcan(dr, 300, 1100, 900, 700, t, humo=0.2)
        dr.poly([(500, 1100), (820, 520), (1150, 1100)], (150, 160, 180))
        dr.poly([(700, 740), (820, 520), (940, 740), (880, 700), (820, 760), (760, 700)], (250, 250, 255))
        suelo(dr, 1250, (170, 150, 120))
        r = romano(dr, 560, 1900, 0.72, t, expr="happy", arm_r=172, arm_l=172, toga=(220, 200, 160), banda=(120, 80, 50))
        (lx, ly), (rx_, ry) = r["hands"]
        dr.rrect(lx - 40, ly - 190, rx_ + 40, ly - 10, 20, (240, 248, 255), shade=True)
        dr.text((lx + rx_) / 2, ly - 100, "NIEVE", 56, (60, 110, 180))
        f = tinta(dr); img = acabado(f, T)
        cartel(img, t - 0.3, "NIEVE + MIEL", "el 'helado' romano", y=380)
        return img, 0
    tt = t - half
    cam = Cam(540, 980, lerp(1.2, 1.35, ease(tt / (D - half))))
    dr = D_(cam, bg=(110, 60, 40))
    for k in range(16):
        a = k * math.pi / 8 + t * 0.5
        dr.poly([(540, 980), (540 + math.cos(a) * 2000, 980 + math.sin(a) * 2000), (540 + math.cos(a + 0.2) * 2000, 980 + math.sin(a + 0.2) * 2000)], (140, 80, 50))
    k = eob(tt / 0.35)
    cono(dr, 540, 980, 2.2 * k + 0.01, t, sabores=((110, 60, 34), (130, 74, 44), (96, 54, 30)))
    f = tinta(dr); add_glow(f, *cam.p(540, 800), 400, (255, 220, 160), 0.3)
    img = acabado(f, T)
    burst(img, "¡CHOCOLATE!", 540, 330, 130, tt - 0.2, ang=-5)
    return img, 0

@shot
def s05(t, D, T):    # ¡Por Júpiter! romano prueba
    cam = Cam(540, 1050, lerp(1.25, 1.4, ease(t / D)))
    dr = D_(cam); calle_pompeya(dr, t, humo=0.5)
    r = romano(dr, 540, 1900, 0.95, t, mouth=boca(4, t), expr="happy_eyes" if t < tl(4, 0.5) else "shock", arm_r=165, arm_l=40, cono_r=True)
    f = tinta(dr)
    img = acabado(f, T)
    burst(img, "¡POR JÚPITER!", 540, 330, 120, t - 0.05, col=(255, 222, 40), ang=-7)
    if t > tl(4, 0.82):
        burst(img, "x10", 860, 620, 150, t - tl(4, 0.82), col=(120, 230, 255), ang=10)
    d = ImageDraw.Draw(img)
    for k in range(5):
        a = t * 2 + k * 1.25
        x, y = 540 + math.cos(a) * 380, 760 + math.sin(a) * 120
        d.text((x, y), "✦", font=font(60), fill=(255, 240, 150), anchor="mm")
    return img, 0

@shot
def s06(t, D, T):    # toda Pompeya hace fila
    u = ease(t / D)
    cam = Cam(lerp(420, 640, u), 1150, 1.05)
    dr = D_(cam); calle_pompeya(dr, t, humo=0.6)
    togas = [((246, 240, 226), (190, 40, 44)), ((210, 220, 240), (60, 80, 160)), ((240, 220, 180), (120, 80, 50)), ((236, 200, 210), (150, 40, 90))]
    for k in range(9, -1, -1):
        x = 360 + k * 140; s = 0.36 + 0.02 * (k % 2)
        tg, bd = togas[k % 4]
        romano(dr, x, 1560 + (k % 2) * 30, s, t, expr="happy", arm_r=60 if k % 3 == 0 else 20, toga=tg, banda=bd, bob_ph=k)
    carrito(dr, 140, 1640, 0.7, t)
    nico(dr, -40, 1660, 0.55, t, traje="heladero", arms=(120, 150), elbows=(30, 20), expr="happy_eyes")
    f = tinta(dr); img = acabado(f, T)
    d = ImageDraw.Draw(img)
    for k in range(10):   # monedas volando
        ph = (t * 1.2 + k / 10) % 1
        x = 300 + k * 60 - ph * 200; y = 900 - math.sin(ph * math.pi) * 420
        d.ellipse([x - 22, y - 22, x + 22, y + 22], fill=(250, 200, 50), outline=INK, width=5)
    return img, 0

@shot
def s07(t, D, T):    # la montaña echa humo (plano general)
    cam = Cam(760, 760, lerp(1.0, 1.25, ease(t / D)))
    dr = D_(cam); calle_pompeya(dr, t, humo=1.0, dark=0.15)
    f = tinta(dr)
    img = acabado(f, T)
    if t > tl(6, 0.6): burst(img, "RUMMMM…", 540, 330, 110, t - tl(6, 0.6), col=(255, 255, 255), ang=-4)
    return img, 3 * math.sin(t * 30) if t > tl(6, 0.5) else 0

@shot
def s08(t, D, T):    # Nico: tranquilos… ¿verdad? (helado derritiéndose)
    cam = Cam(540, 1150, 1.7)
    dr = D_(cam); calle_pompeya(dr, t, humo=1.0, dark=0.25)
    info = nico(dr, 540, 1760, 0.66, t, traje="heladero", arms=(60, 25), elbows=(70, 0), expr="nervous", mouth=boca(7, t), sweat=True, look=(0.8, -0.6))
    hx, hy = info["hands"][0]; cono(dr, hx, hy - 40, 0.8, t, melt=0.5 + 0.5 * math.sin(t * 2))
    f = tinta(dr); img = acabado(f, T)
    if t > tl(7, 0.75):
        d = ImageDraw.Draw(img); d.text((860, 560), "?", font=font(170), fill=(255, 222, 40), anchor="mm", stroke_width=12, stroke_fill=INK)
    return img, 2 * math.sin(t * 40)

@shot
def s09(t, D, T):    # ERUPCIÓN · nube de 30 km
    te = tl(8, 0.18)
    erup = clamp((t - te) / 0.6)
    cam = Cam(700, lerp(820, 620, ease(t / D)), lerp(1.0, 0.9, ease(t / D)))
    dr = D_(cam); calle_pompeya(dr, t, humo=1.0, erup=erup, dark=0.25 + 0.6 * erup)
    f = tinta(dr)
    add_glow(f, *cam.p(760, 420), 380, (255, 120, 40), 0.7 * erup)
    if 0 < t - te < 0.2: f += 255 * (1 - (t - te) / 0.2)
    img = acabado(f, T)
    burst(img, "¡BOOOM!", 540, 360, 170, t - te, col=(255, 140, 40), ang=-8)
    if t > tl(8, 0.7):
        k = eob((t - tl(8, 0.7)) / 0.4); d = ImageDraw.Draw(img)
        x = 960; y1 = 1250; y0 = y1 - 700 * k
        d.line([(x, y1), (x, y0)], fill=(255, 255, 255), width=10)
        for j in range(8): d.line([(x - 30, y1 - j * 100 * k), (x, y1 - j * 100 * k)], fill=(255, 255, 255), width=6)
        d.text((x - 40, y0 - 60), "+30 KM", font=font(84), fill=(255, 222, 40), anchor="rm", stroke_width=10, stroke_fill=INK)
    return img, (16 * math.exp(-(t - te) * 2.5) if t > te else 0)

@shot
def s10(t, D, T):    # ¡Helado de lava! ¡Corran! (todos corren al portal)
    cam = Cam(540, 1150, 1.15)
    dr = D_(cam); calle_pompeya(dr, t, humo=1.0, erup=1.0, dark=0.9, vx=760, vby=1000)
    portal(dr, 960, 1300, 250, t, 1.0)
    run = (t * 260) % 1
    for k in range(4):
        x = (-200 + k * 190 + t * 330) % 1200 - 80
        romano(dr, x, 1640 + (k % 2) * 40, 0.4, t * 3, expr="shock", arm_r=150, arm_l=150, toga=[(246, 240, 226), (210, 220, 240), (240, 220, 180), (236, 200, 210)][k], bob_ph=k)
    info = nico(dr, 420 + 40 * math.sin(t * 2), 1740 - 30 * abs(math.sin(t * 12)), 0.62, t, traje="heladero", arms=(160, 40), elbows=(10, 60), expr="shock", mouth=boca(9, t), look=(-0.8, -0.3))
    hx, hy = info["hands"][0]; cono(dr, hx, hy - 40, 0.75, t, lava=True, melt=0.6)
    f = tinta(dr); add_glow(f, *cam.p(960, 1300), 300, (150, 120, 255), 0.5); add_glow(f, W / 2, 0, 700, (255, 90, 30), 0.35)
    img = acabado(f, T)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([90, 290, 600, 420], radius=20, fill=(30, 20, 20), outline=(255, 120, 40), width=8)
    d.text((345, 330), "MENÚ DE HOY:", font=font(40), fill=(255, 255, 255), anchor="mm")
    d.text((345, 385), "HELADO DE LAVA", font=font(50), fill=(255, 140, 40), anchor="mm")
    rng = np.random.default_rng(int(t * 10))
    for k in range(40):   # ceniza cayendo
        ph = (t * 0.6 + k / 40) % 1
        x = (k * 97 + t * 40) % W; y = ph * H
        d.ellipse([x - 5, y - 5, x + 5, y + 5], fill=(120, 110, 110))
    return img, 5

@shot
def s11(t, D, T):    # presente: el romano abrió su heladería al frente
    half = tl(10, 0.42)
    if t < half:
        cam = Cam(540, 1150, lerp(1.0, 1.08, ease(t / half)))
        dr = D_(cam); calle_moderna(dr, t)
        portal(dr, 540, 1250, 260, t, 1 - ease((t - half + 0.6) / 0.5))
        for k in range(4):
            romano(dr, 200 + k * 230, 1660 + (k % 2) * 30, 0.38, t, expr="happy", arm_r=150, arm_l=20, toga=[(246, 240, 226), (210, 220, 240), (240, 220, 180), (236, 200, 210)][k], bob_ph=k)
        f = tinta(dr); add_glow(f, 540, 1150, 300, (150, 120, 255), 0.4)
        if t < 0.2: f += 255 * (1 - t / 0.2)
        img = acabado(f, T)
        cartel(img, t - 0.2, "PRESENTE", "2026", y=380)
        return img, 0
    tt = t - half
    u = ease(tt / (D - half))
    cam = Cam(lerp(300, 760, u), 1200, 1.05)
    dr = D_(cam); calle_moderna(dr, t)
    carrito(dr, 230, 1640, 0.7, t)
    nico(dr, 470, 1680, 0.55, t, traje="heladero", arms=(20, 20), expr="shock", look=(1, 0))
    carrito(dr, 960, 1640, 0.7, t, letrero="GELATVS 2x1", col=(200, 40, 50))
    romano(dr, 760, 1680, 0.55, t, expr="smug", arm_r=150, arm_l=20, look=(-1, 0))
    for k in range(5):
        romano(dr, 1180 + k * 120, 1720, 0.34, t, expr="happy", toga=[(210, 220, 240), (240, 220, 180), (236, 200, 210)][k % 3], bob_ph=k)
    f = tinta(dr); img = acabado(f, T)
    return img, 0

@shot
def s12(t, D, T):    # "Helado de nieve del Vesubio. ¡Dos por uno!"
    cam = Cam(540, 1050, 1.35)
    dr = D_(cam); calle_moderna(dr, t)
    carrito(dr, 900, 1900, 0.9, t, letrero="GELATVS 2x1", col=(200, 40, 50))
    romano(dr, 470, 1900, 0.95, t, mouth=boca(11, t), expr="smug", arm_r=165, arm_l=30, cono_r=True)
    f = tinta(dr); img = acabado(f, T)
    burst(img, "2x1", 830, 520, 190, t - tl(11, 0.55), col=(255, 80, 60), ang=12)
    return img, 0

@shot
def s13(t, D, T):    # cierre: Nico celoso + nos vemos + pregunta
    cam = Cam(540, 1000, 1.0)
    dr = D_(cam, bg=(18, 10, 30))
    for k in range(16):
        a = k * math.pi / 8 - t * 0.4
        dr.poly([(540, 1000), (540 + math.cos(a) * 2000, 1000 + math.sin(a) * 2000), (540 + math.cos(a + 0.2) * 2000, 1000 + math.sin(a + 0.2) * 2000)], (34, 20, 56))
    o = 1 - ease((t - D + 0.9) / 0.7)
    portal(dr, 540, 1080, 330, t, o)
    if t < D - 1.1:
        info = nico(dr, 540, 1560, 0.55, t, traje="heladero", arms=(150, 30), elbows=(30, 0), expr="happy")
        hx, hy = info["hands"][1]; cono(dr, hx, hy - 35, 0.7, t)
    f = tinta(dr); add_glow(f, 540, 1080, 450, (150, 120, 255), 0.5 * o)
    img = acabado(f, T)
    d = ImageDraw.Draw(img)
    if t > tl(12, 0.45):
        k = eob((t - tl(12, 0.45)) / 0.3)
        d.rounded_rectangle([90, 300, 990, 560], radius=36, fill=(255, 214, 10), outline=INK, width=8)
        d.text((540, 380), "¿QUÉ NEGOCIO LLEVO", font=font(62 * k + 1), fill=INK, anchor="mm")
        d.text((540, 470), "A OTRA ÉPOCA?", font=font(62 * k + 1), fill=INK, anchor="mm")
        d.text((540, 640), "COMENTA 👇" if False else "¡COMENTA!", font=font(80), fill=(255, 255, 255), anchor="mm", stroke_width=10, stroke_fill=INK)
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
    if i > 0 and t < 0.06:   # destello en el corte
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
    # A) tarantela alegre (la menor → do, 6/8 rápido) del inicio hasta el humo
    def tarantela(t0, t1, vol=1.0):
        e8 = 0.14
        mel = [69, 72, 76, 72, 69, 72, 71, 74, 77, 74, 71, 74, 72, 76, 79, 76, 72, 76, 71, 69, 68, 69, 71, 72]
        bass = [45, 45, 52, 52, 48, 48, 52, 45]
        k = 0; s = t0
        while s < t1:
            x = seg(e8 * 1.2); m = mel[k % len(mel)]
            pl = np.sin(2 * np.pi * hz(m) * x) * 0.6 + np.sin(2 * np.pi * hz(m) * 2 * x) * 0.25 + np.sin(2 * np.pi * hz(m) * 3 * x) * 0.1
            add(s, vol * 0.05 * pl * np.exp(-x * 9) * (1 - np.exp(-x * 300)))
            if k % 3 == 0:
                xb = seg(e8 * 2.5); bm = bass[(k // 6) % len(bass)]
                add(s, vol * 0.1 * np.exp(-xb * 4) * np.sin(2 * np.pi * hz(bm) * xb))
                add(s, vol * 0.12 * np.exp(-x * 25) * np.sin(2 * np.pi * (80 + 50 * np.exp(-x * 25)) * x))
            if k % 3 == 2: add(s, vol * 0.04 * rng.standard_normal(len(x)) * np.exp(-x * 40))   # pandereta
            k += 1; s += e8
    tarantela(0, S_[6])
    tarantela(S_[10] + DURS[10] * 0.42, S_[12] + DURS[12], 0.8)
    # B) tensión (humo, nervios)
    for kk in range(int((S_[8] - S_[6]) / 0.7)):
        x = seg(0.4); add(S_[6] + kk * 0.7, 0.14 * np.exp(-x * 6) * np.sin(2 * np.pi * (49 + 3 * (kk % 2)) * x))
    x = seg(S_[8] - S_[6]); add(S_[6], 0.35 * low[:len(x)] * (0.3 + 0.7 * x / x[-1]))
    # erupción
    te = S_[8] + tl(8, 0.18)
    x = seg(2.5); add(te, 1.0 * low[:len(x)] * np.exp(-x * 1.2)); add(te, 0.6 * np.exp(-x * 3) * np.sin(2 * np.pi * (40 + 40 * np.exp(-x * 8)) * x))
    # C) huida: tambores rápidos
    for kk in range(int(DURS[9] / 0.15)):
        x = seg(0.12); add(S_[9] + kk * 0.15, (0.16 if kk % 2 == 0 else 0.08) * np.exp(-x * 25) * np.sin(2 * np.pi * (90 + 40 * np.exp(-x * 30)) * x))
    x = seg(DURS[9]); add(S_[9], 0.12 * low[:len(x)])
    # efectos
    x = seg(1.2); add(S_[1] + 0.1, 0.12 * np.sin(2 * np.pi * (200 + 600 * x) * x) * np.sin(np.pi * x / 1.2))   # portal
    tp = S_[1] + DURS[1] * 0.4; x = seg(0.5); add(tp, 0.5 * np.exp(-x * 9) * np.sin(2 * np.pi * (60 + 40 * np.exp(-x * 20)) * x))
    for k in range(1, len(S_) - 1):   # whoosh en cada corte
        x = seg(0.3); add(S_[k] - 0.08, 0.12 * wh[:len(x)] * np.sin(np.pi * x / 0.3))
    x = seg(1.0); add(S_[4] + 0.1, 0.25 * np.exp(-x * 3) * (np.sin(2 * np.pi * 784 * x) + np.sin(2 * np.pi * 1047 * x)) / 2)   # ding mágico
    for kk in range(10):
        x = seg(0.08); add(S_[5] + 0.2 + kk * 0.2, 0.15 * np.exp(-x * 50) * np.sin(2 * np.pi * (2200 + 200 * (kk % 3)) * x))   # monedas
    x = seg(0.8); add(S_[10] + 0.05, 0.3 * np.sin(2 * np.pi * (700 - 500 * x) * x) * np.exp(-x * 3))   # portal salida
    x = seg(0.6); add(S_[11] + tl(11, 0.55), 0.3 * np.exp(-x * 6) * np.sin(2 * np.pi * (300 + 200 * x) * x))   # 2x1 "boing"
    x = seg(1.6); add(S_[12] + 0.2, 0.12 * np.exp(-x * 1.5) * (np.sin(2 * np.pi * 523 * x) + np.sin(2 * np.pi * 784 * x)) / 2)
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
        ts = [float(x) for x in os.environ["PREVIEW"].split(",")]
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
