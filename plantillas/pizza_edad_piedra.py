#!/usr/bin/env python3
"""BORRADOR PREMIUM — ¿Qué pasaría si abres una pizzería en la Edad de Piedra?
Personajes 3D (clay) renderizados con clay.py, escenario por capas con parallax y profundidad de campo,
lip sync con la voz, luz del fuego sobre los personajes, cámara cinematográfica, sonido procedural."""
import math, os, sys, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy.io import wavfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "motor"))
import realce
from clay import Scene, render, composite, _n, Mat, STONE, GLOSS, EMIT, FLAT
from personajes import nico, cavernicola, mamut, pizza, caja_pizza, roca, gema
from escenario import *

FPS = 30
OUT = sys.argv[1] if len(sys.argv) > 1 else "pizza.mp4"
YEL = (255, 214, 10); WHITE = (255, 255, 255)

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)
def eob(x):
    x = clamp(x); c = 1.70158
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2
def lerp(a, b, k): return a + (b - a) * k

# ------------------------------------------------------------ voz y tiempos
VOZ_DIR = os.environ.get("VOZ_DIR", "voz")
VOZ_F = sorted(os.listdir(VOZ_DIR))
VOZ = [wavfile.read(f"{VOZ_DIR}/{f}")[1].astype(np.float32) / 32768 for f in VOZ_F]
QUIEN = [f.split("_")[1][0] for f in VOZ_F]   # N narrador, K Nico, C cavernícola
SR = 44100; LEAD = 0.12
DURS = [len(v) / SR + LEAD + 0.36 for v in VOZ]
DURS[0] += 0.25; DURS[10] += 1.0; DURS[13] += 1.1; DURS[6] += 0.25
STARTS = np.cumsum([0] + DURS).tolist(); TOTAL = STARTS[-1]

ENV = []
for v in VOZ:   # envolvente para lip sync (60 por segundo)
    hop = SR // 60
    e = np.array([np.sqrt(np.mean(v[i:i + hop] ** 2)) for i in range(0, len(v), hop)])
    e = e / (np.percentile(e, 95) + 1e-6)
    ENV.append(np.convolve(e, np.ones(3) / 3, mode="same"))
def boca(k, t):
    i = int((t - LEAD) * 60)
    if i < 0 or i >= len(ENV[k]): return 0.0
    return float(np.clip(ENV[k][i] * 1.1 - 0.12, 0, 1))

CHUNKS = [
    [("¿Qué pasaría si", []), ("abres una PIZZERÍA", ["PIZZERÍA"]), ("en la Edad de Piedra?", ["Piedra?"])],
    [("Nico cruza un portal", ["portal"]), ("y aparece hace", []), ("15.000 años", ["15.000"]), ("con una caja de pizza", ["pizza"])],
    [("Los cavernícolas", []), ("nunca habían olido", ["olido"]), ("nada igual", [])],
    [("¡¿UGA?!", ["¡¿UGA?!"]), ("¡UGA UGA!", ["¡UGA", "UGA!"])],
    [("No hay horno", ["horno"]), ("ni harina", ["harina"]), ("ni dinero…", ["dinero…"]), ("¡pero hay FUEGO!", ["FUEGO!"])],
    [("Construye un horno", ["horno"]), ("de piedra", ["piedra"]), ("muele trigo salvaje", ["trigo"]), ("con una roca…", [])],
    [("…y sale la primera", []), ("pizza de la historia", ["pizza"])],
    [("Le pagan con", []), ("lo único que tienen:", []), ("piedras brillantes", ["brillantes"])],
    [("En una semana", []), ("toda la tribu", ["tribu"]), ("hace fila", ["fila"])],
    [("Hasta que algo enorme", ["enorme"]), ("huele la pizza", [])],
    [("¡UN MAMUT!", ["MAMUT!"])],
    [("Tranquilo, grandote…", ["grandote…"]), ("toma, una porción", ["porción"])],
    [("Y así nació", []), ("el primer delivery…", ["delivery…"]), ("en MAMUT", ["MAMUT"])],
    [("¿A qué época", ["época"]), ("llevo la pizzería?", []), ("¡Coméntalo!", ["¡Coméntalo!"])],
]
CAPS = []
for k, (ch, v) in enumerate(zip(CHUNKS, VOZ)):
    dv = len(v) / SR; s0 = STARTS[k] + LEAD
    lens = np.array([len(c[0]) + 4 for c in ch], float); cum = np.concatenate([[0], np.cumsum(lens) / lens.sum()])
    for m, (txt, hl) in enumerate(ch):
        st = STARTS[k] if m == 0 else s0 + cum[m] * dv
        en = STARTS[k + 1] if m == len(ch) - 1 else s0 + cum[m + 1] * dv
        CAPS.append((st, en, txt, hl))

def text_layer(words, size, hl, stroke=11):
    f = font(size); sp = f.getlength(" ")
    ws = [f.getlength(w) for w in words]; tot = sum(ws) + sp * (len(words) - 1)
    pad = stroke * 2 + 10; a, de = f.getmetrics()
    lay = Image.new("RGBA", (int(tot + pad * 2), a + de + pad * 2), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); x = pad
    for w, wd in zip(words, ws):
        d.text((x, pad), w, font=f, fill=YEL if w in hl else WHITE, stroke_width=stroke, stroke_fill=(10, 8, 12)); x += wd + sp
    return lay

def caption(img, T):
    for s, e, txt, hl in CAPS:
        if s <= T < e:
            words = txt.split(); size = 100
            while True:
                lay = text_layer(words, size, hl)
                if lay.width <= W - 70 or size < 56: break
                size -= 6
            k = 0.62 + 0.38 * eob((T - s) / 0.15)
            lay = lay.resize((max(1, int(lay.width * k)), max(1, int(lay.height * k))), Image.LANCZOS)
            img.alpha_composite(lay, (int(W / 2 - lay.width / 2), int(1690 - lay.height / 2))); return

# ------------------------------------------------------------ escenarios (se construyen una vez)
print("construyendo escenarios…", flush=True)
VALLE = valle(cueva=False)
CUEVA = valle(cueva=True)

def fondo(L, cx=0.0, cy=0.0, z=1.0, luces=()):
    bg = componer(L, cx, cy, z)
    for (x, y, r, col, a) in luces: add_light(bg, x, y, r, col, a)
    return Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8)).convert("RGBA")

def gp(sx, sy, S): return sx / S, -sy / S          # punto de pantalla (pies) → mundo con ox=oy=0
def rend(img, sc, S, light=None): composite(img, render(sc, S, 0, 0, W, H, light))

def luz_fuego(sx, sy, fx, fy, k=1.0):
    d = _n((fx - sx, -(fy - sy), 900.0))
    return dict(key=d, key_col=np.array([1.0, 0.72, 0.45], np.float32) * (0.9 + 0.12 * k),
                rim_col=np.array([1.0, 0.6, 0.3], np.float32))

def sacudida(T, a):
    return a * math.sin(T * 63), a * math.cos(T * 51)

# ------------------------------------------------------------ planos
SHOTS = []
def shot(fn): SHOTS.append(fn); return fn

@shot
def s01(t, D, T):   # gancho: Nico con la pizza humeante / plano general del valle
    if t < D * 0.62:
        z = lerp(1.0, 1.08, ease(t / (D * 0.62)))
        img = fondo(VALLE, 0, 0, z)
        S = 300 * z
        sx, sy = cam_pt(540, 1640, 0, 0, z)
        sombra(img, sx, sy, 150)
        sc = Scene(); x, y = gp(sx, sy, S)
        info = nico(sc, x, y, 0, t, arms=("hold", "hold"), expr="happy", look=(0, 0))
        hl, hr = info["hands"]["L"], info["hands"]["R"]
        hx, hy, hz = (hl[0] + hr[0]) / 2, (hl[1] + hr[1]) / 2 + 0.05, max(hl[2], hr[2]) + 0.25
        caja_pizza(sc, hx, hy - 0.12, hz, 0.95, abierta=0.32)
        pizza(sc, hx, hy + 0.02, hz + 0.32, 0.42)
        rend(img, sc, S)
        humo(img, hx * S, -(hy + 0.3) * S, 0.7, t, n=6, alpha=120)
        chispas(img, [(hx * S - 120, -(hy + 0.2) * S - 60), (hx * S + 130, -(hy + 0.25) * S - 20)], t, 30)
        return img, (0.15, 0.2)
    tt = t - D * 0.62; dd = D * 0.38
    z = lerp(0.8, 0.84, tt / dd)
    img = fondo(VALLE, lerp(-60, 60, tt / dd), 0, z)
    sc = Scene()
    for k, (sx, sy, s_) in enumerate([(300, 1330, 26), (420, 1345, 30), (880, 1315, 22)]):
        x, y = gp(sx + tt * 12, sy, 28); mamut(sc, x, y, 0, t + k, s=s_ / 28, face=1 if k < 2 else -1, walk=t * 3 + k)
    rend(img, sc, 28)
    humo(img, *cam_pt(1120 - 400, 960 - 30, 0, 0, z, 0.18), 1.4, t, n=7, col=(120, 110, 120), alpha=170, speed=0.6)
    sc = Scene(); sx, sy = cam_pt(540, 1600, 0, 0, z)
    S = 110; x, y = gp(sx, sy, S)
    nico(sc, x, y, 0, t, arms=("hold", "hold"), expr="happy", yaw=0.3)
    sombra(img, sx, sy, 60); rend(img, sc, S)
    return img, (0.15, 0.2)

@shot
def s02(t, D, T):   # portal: Nico sale volando y aterriza
    img = fondo(VALLE, 0, 0, 1.0)
    px, py = 560, 1130
    op = ease(t / 0.5) * (1 - ease((t - D * 0.72) / 0.45))
    portal(img, px, py, 210, t, op)
    S = 260
    t0, t1 = 0.45, 1.25
    sc = Scene()
    if t < t0:
        pass
    else:
        if t < t1:
            u = (t - t0) / (t1 - t0)
            sx = lerp(px, 580, u); sy = lerp(py + 120, 1600, u * u) - math.sin(u * math.pi) * 260
            yaw = u * 2 * math.pi; sq = 1.15
            info = nico(sc, *gp(sx, sy, S), 0, t, yaw=yaw, arms=("up", "up"), expr="shock", squash=sq)
        else:
            u = t - t1
            sq = 1 - 0.32 * math.exp(-u * 7) * math.cos(u * 22)
            hy = 0.55 * math.sin(u * 2.6) if u > 0.5 else 0.0
            sx, sy = 580, 1600
            sombra(img, sx, sy, 140)
            info = nico(sc, *gp(sx, sy, S), 0, t, squash=sq, head_yaw=hy, arms=("hold", "down"),
                        expr="shock" if u < 0.6 else "happy", look=(hy * 1.5, 0))
            hl = info["hands"]["L"]
            caja_pizza(sc, hl[0] + 0.05, hl[1] + 0.02, hl[2] + 0.35, 0.9)
            polvo(img, sx, sy, u, 1.2)
        rend(img, sc, S)
    return img, (0.2, 0.3)

def frente_cueva(t, z=1.0, cx=0.0, fuego_on=False):
    luces = [(cam_pt(300, 1500, cx, 0, z, 0.55)[0], cam_pt(300, 1500, cx, 0, z, 0.55)[1], 260, (255, 140, 50), 0.35)]
    return fondo(CUEVA, cx, 0, z, luces)

@shot
def s03(t, D, T):   # cavernícolas asoman detrás de una roca y huelen
    z = 1.12
    img = frente_cueva(t, z, cx=lerp(-30, 10, t / D))
    S = 200
    sc = Scene()
    for k, sx in enumerate((250, 540, 830)):
        rise = eob((t - 0.15 - k * 0.22) / 0.4)
        sniff = 0.05 * math.sin(t * 22 + k) if t > 0.8 else 0
        cavernicola(sc, *gp(sx, 1720 - rise * 300 - sniff * S, S), -1.0, t, var=k, expr="happy", head_yaw=0.25 * math.sin(t * 1.5 + k),
                    blink=1.0 if t > 1.0 else None)
    roca(sc, *gp(560, 1960, S), 0.6, 1.25, col=(140, 124, 112), seed=2)
    roca(sc, *gp(170, 1990, S), 0.8, 0.8, col=(128, 116, 104), seed=5)
    roca(sc, *gp(960, 1980, S), 0.8, 0.9, col=(150, 132, 118), seed=7)
    rend(img, sc, S)
    if t > 0.4: olor(img, -80, 1300, 830, 1080, t, n=3)
    return img, (0.15, 0.2)

@shot
def s04(t, D, T):   # ¡¿UGA?! primer plano con anticipación y salto
    img = frente_cueva(t, 1.35, cx=60)
    S = 470
    if t < 0.28: sq = 1 - 0.18 * ease(t / 0.28); jy = 0
    else:
        u = t - 0.28
        jy = max(0.0, math.sin(min(u / 0.55, 1) * math.pi)) * 0.35 if u < 0.55 else 0.0
        sq = 1.12 if u < 0.3 else 1 - 0.1 * math.exp(-(u - 0.3) * 6) * math.cos((u - 0.3) * 20)
    sc = Scene()
    m = boca(3, t)
    cavernicola(sc, *gp(540, 2380 - jy * S, S), 0, t, var=0, expr="shock", mouth=max(m, 0.25), arms=("up", "up"), squash=sq, look=(0, 0.3))
    rend(img, sc, S)
    if t > 0.3: comic(img, "¡¿UGA?!", 540, 440, 170, t - 0.3, ang=-8)
    sh = 14 if 0.3 < t < 0.9 else 0
    return img, (0.1, 0.0), sh

def tarjeta(img, x, y, txt, ok, t, s=1.0):
    k = eob(t / 0.25)
    if k <= 0.01: return
    f = font(48 * s * k); tw = f.getlength(txt)
    wd, hd = tw + 130 * s * k, 96 * s * k
    lay = Image.new("RGBA", (int(wd + 20), int(hd + 20)), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle([6, 6, wd + 6, hd + 6], radius=int(24 * s * k), fill=(20, 16, 22, 120))
    d.rounded_rectangle([0, 0, wd, hd], radius=int(24 * s * k), fill=(255, 250, 240, 255), outline=(20, 16, 22, 255), width=int(5 * s * k) or 1)
    d.text((24 * s * k, hd / 2 - 28 * s * k), txt, font=f, fill=(30, 24, 30))
    cx, cy, r = wd - 50 * s * k, hd / 2, 26 * s * k
    if ok:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(40, 180, 90, 255))
        d.line([(cx - r * 0.5, cy), (cx - r * 0.1, cy + r * 0.45), (cx + r * 0.55, cy - r * 0.45)], fill=(255, 255, 255, 255), width=int(8 * s * k) or 1)
    else:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(220, 50, 50, 255))
        for sg in (-1, 1): d.line([(cx - r * 0.45, cy - r * 0.45 * sg), (cx + r * 0.45, cy + r * 0.45 * sg)], fill=(255, 255, 255, 255), width=int(8 * s * k) or 1)
    img.alpha_composite(lay, (int(x - wd / 2), int(y - hd / 2)))

@shot
def s05(t, D, T):   # Nico: no hay horno, ni harina, ni dinero… ¡pero hay fuego!
    dv = len(VOZ[4]) / SR
    on = t > LEAD + dv * 0.62
    img = frente_cueva(t, 1.18, cx=-40)
    S = 300; sx, sy = 640, 1660
    fx, fy = 260, 1650
    if on:
        k = ease((t - LEAD - dv * 0.62) / 0.3)
        arr = np.array(img).astype(np.float32); add_light(arr[..., :3], fx, fy - 120, 520, (255, 150, 60), 0.5 * k)
        img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGBA")
        fuego(img, fx, fy, 1.1 * k + 0.01, t)
    sombra(img, sx, sy, 160)
    sc = Scene()
    nico(sc, *gp(sx, sy, S), 0, t, arms=("shrug", "shrug") if not on else ("point", "hip"), yaw=0 if not on else -0.35,
         expr="nervous" if not on else "happy", mouth=boca(4, t), head_yaw=0 if not on else -0.3, look=(0, 0) if not on else (-0.8, 0))
    rend(img, sc, S, luz_fuego(sx, sy - 400, fx, fy - 150) if on else None)
    for k, (txt, frac) in enumerate([("HORNO", 0.05), ("HARINA", 0.25), ("DINERO", 0.45)]):
        tarjeta(img, 330 + (k % 2) * 40, 330 + k * 125, txt, False, t - LEAD - dv * frac)
    if on: tarjeta(img, 760, 520, "FUEGO", True, t - LEAD - dv * 0.62, 1.25)
    return img, (0.15, 0.2)

OVEN_STONES = []
for ring, (ry, n, rad) in enumerate([(0.15, 9, 1.05), (0.55, 8, 0.95), (0.95, 7, 0.78), (1.3, 5, 0.52), (1.55, 1, 0.0)]):
    for k in range(n):
        a = math.pi * 1.08 + k * (math.pi * 0.84 / max(1, n - 1)) if n > 1 else 1.5 * math.pi
        OVEN_STONES.append((math.cos(a) * rad * 1.15, ry, math.sin(a) * rad * 0.5 + 0.5, 0.27 if ring < 4 else 0.32, ring))

def horno(sc, cx, cy, t, built=1.0, glow_k=1.0):
    n = len(OVEN_STONES); shown = int(built * n + 0.999)
    for i, (x, y, z, r, ring) in enumerate(OVEN_STONES[:shown]):
        fall = clamp((built * n - i) / 1.0)
        yy = y + (1 - eob(fall)) * 2.5
        g = 128 + (i * 37) % 30
        sc.sphere((cx + x, cy + yy, z), r, (g, g - 8, g - 18), STONE, oid=5000)
    if built >= 1.0:
        sc.ell((cx, cy + 0.75, 0.15), 1.05, 0.85, 0.5, (124, 116, 108), STONE, oid=5000)
        sc.ell((cx, cy + 0.42, 0.68), 0.46, 0.4, 0.05, (30, 16, 12), FLAT)
        sc.ell((cx, cy + 0.34, 0.72), 0.32, 0.22, 0.04, (255, int(120 + 60 * glow_k), 40), EMIT)

@shot
def s06(t, D, T):   # construye el horno / muele trigo
    if t < D * 0.5:
        u = t / (D * 0.5)
        img = frente_cueva(t, 1.15, cx=-20)
        S = 250
        sc = Scene()
        horno(sc, *gp(400, 1640, S), t, built=clamp(u * 1.25))
        nico(sc, *gp(820, 1660, S), 0, t, arms=("down", "point"), yaw=-0.5, head_yaw=-0.3, expr="happy", look=(-0.8, 0))
        sombra(img, 820, 1660, 130); sombra(img, 400, 1650, 200)
        rend(img, sc, S)
        return img, (0.15, 0.2)
    tt = t - D * 0.5
    img = frente_cueva(t, 1.4, cx=40)
    S = 330
    gr = math.sin(tt * 12)
    sc = Scene()
    sx, sy = 520, 1720
    nico(sc, *gp(sx, sy, S), 0, t, arms=((22, -70 + 20 * gr, 0.9), (22, -70 + 20 * gr, 0.9)), expr="happy", look=(0, -0.7), bob=False)
    bx, by = gp(sx, sy - 0.62 * S, S)
    roca(sc, bx, by - 0.45, 1.1, 0.55, col=(132, 122, 112), seed=9)
    sc.box((bx, by, 1.45), 0.85, 0.1, 0.3, (156, 146, 134), STONE, bevel=0.5)
    sc.sphere((bx + 0.22 * gr, by + 0.27, 1.85), 0.24, (120, 112, 104), STONE)
    for k in range(10):
        a = k * 0.6
        sc.sphere((bx - 0.55 + k * 0.12, by + 0.12, 1.78 + 0.02 * math.sin(a)), 0.06, (240, 230, 204), FLAT)
    rend(img, sc, S)
    humo(img, 520, 1500, 0.55, tt, n=5, col=(255, 252, 240), alpha=160, spread=2.0, speed=2.0)
    return img, (0.15, 0.2)

@shot
def s07(t, D, T):   # sale la primera pizza
    z = lerp(1.25, 1.4, ease(t / D))
    img = frente_cueva(t, z, cx=-80)
    arr = np.array(img).astype(np.float32); add_light(arr[..., :3], 420, 1350, 600, (255, 160, 70), 0.45)
    img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGBA")
    S = 340
    sc = Scene()
    ox_, oy_ = gp(380, 1780, S)
    horno(sc, ox_, oy_, t, built=1.0, glow_k=1 + 0.2 * math.sin(t * 15))
    u = eob(t / 0.7)
    px, py = gp(lerp(400, 640, u), lerp(1580, 1260, u), S)
    sc.box((px, py - 0.12, 1.3), 0.62, 0.05, 0.4, (176, 124, 76), STONE, bevel=0.6)
    sc.caps((px + 0.55, py - 0.12, 1.3), (px + 1.6, py - 0.3, 1.3), 0.06, 0.06, (150, 104, 62), STONE)
    pizza(sc, px, py, 1.4, 0.55)
    rend(img, sc, S, dict(key=_n((-0.4, 0.5, 0.8)), key_col=np.array([1.0, 0.82, 0.6], np.float32)))
    sxp, syp = px * S, -py * S
    humo(img, sxp, syp - 40, 1.0, t, n=8, alpha=150)
    chispas(img, [(sxp - 220, syp - 120), (sxp + 200, syp - 80), (sxp - 40, syp - 230), (sxp + 260, syp + 60)], t, 46)
    glow(img, sxp, syp, 300, (255, 230, 150), 0.35 * u)
    return img, (0.55, 0.62)

@shot
def s08(t, D, T):   # le pagan con piedras brillantes
    img = frente_cueva(t, 1.25, cx=30)
    S = 270
    sc = Scene()
    cavernicola(sc, *gp(300, 1700, S), 0, t, var=1, yaw=0.45, arms=("down", "offer"), expr="happy", head_yaw=0.3)
    u = t
    happy = t > 1.4
    info = nico(sc, *gp(790, 1700, S), 0, t, yaw=-0.4, arms=("offer", "offer"), expr="shock" if not happy else "happy", head_yaw=-0.2, look=(-0.4, -0.5))
    hx = (info["hands"]["L"][0] + info["hands"]["R"][0]) / 2; hy = info["hands"]["L"][1] + 0.15; hz = info["hands"]["L"][2] + 0.4
    cols = [(60, 230, 210), (170, 90, 255), (255, 90, 140), (90, 200, 255), (255, 220, 70)]
    gpts = []
    for k in range(5):
        fall = clamp((t - 0.35 - k * 0.18) / 0.45)
        if fall <= 0: continue
        x0, y0 = gp(420, 1080, S)
        gx = lerp(x0, hx + (k - 2) * 0.12, fall); gy = lerp(y0, hy + (k % 2) * 0.1, fall) + math.sin(fall * math.pi) * 0.6
        gema(sc, gx, gy, hz + 0.1 * k, 0.15, cols[k]); gpts.append((gx * S, -gy * S))
    sombra(img, 300, 1700, 170); sombra(img, 790, 1700, 150)
    rend(img, sc, S)
    if t > 1.2: chispas(img, [(p[0] + 30, p[1] - 30) for p in gpts], t, 40)
    return img, (0.15, 0.2)

@shot
def s09(t, D, T):   # toda la tribu hace fila
    cx = lerp(220, -160, ease(t / D))
    z = 1.05
    img = frente_cueva(t, z, cx=cx)
    sc = Scene()
    S0 = 230
    fx, fy = cam_pt(330, 1610, cx, 0, z)
    sx, sy = cam_pt(380, 1640, cx, 0, z)
    sombra(img, sx, sy, 120)
    nico(sc, *gp(sx, sy, S0), 0, t, yaw=0.35, arms=("offer", "down"), expr="happy", head_yaw=0.1)
    for k in range(6):
        d = k / 5
        ssx, ssy = cam_pt(700 + k * 150, 1660 - k * 55, cx, 0, z)
        S = S0 * (1 - 0.5 * d)
        sombra(img, ssx, ssy, 110 * (1 - 0.5 * d))
        cavernicola(sc, *gp(ssx, ssy, S0), -k * 0.8, t, s=(1 - 0.5 * d), var=k, yaw=-0.45, expr="happy",
                    arms=("down", "down"), head_yaw=0.2 * math.sin(t * 3 + k), club=(k == 2))
    rend(img, sc, S0)
    # letrero de piedra tallado
    lay = Image.new("RGBA", (420, 200), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle([0, 0, 419, 199], radius=50, fill=(150, 138, 124, 255), outline=(40, 30, 30, 255), width=8)
    f = font(104); d.text((210 - f.getlength("PIZZA") / 2, 34), "PIZZA", font=f, fill=(70, 54, 48), stroke_width=3, stroke_fill=(190, 178, 160))
    ex, ey = cam_pt(250, 1040, cx, 0, z, 0.55)
    img.alpha_composite(lay.rotate(4, expand=True, resample=Image.BICUBIC), (int(ex - 210), int(ey - 100)))
    return img, (0.15, 0.2)

@shot
def s10(t, D, T):   # algo enorme huele la pizza: todos se congelan
    img = frente_cueva(t, 1.22, cx=0)
    S = 270
    sc = Scene()
    look = (0.7, 0.8)
    nico(sc, *gp(560, 1700, S), 0, t, arms=("hold", "down"), expr="shock", look=look, head_yaw=0.3, bob=False)
    hl = sc.p[-1]
    cavernicola(sc, *gp(250, 1690, S), -0.4, t, var=2, expr="shock", look=look, head_yaw=0.4, bob=False)
    cavernicola(sc, *gp(880, 1720, S), -0.2, t, var=3, expr="shock", look=look, head_yaw=-0.1, bob=False, yaw=-0.3)
    for k in range(6):  # piedritas que saltan
        ph = (t * 3 + k * 0.37) % 1
        sc.sphere(gp(150 + k * 160, 1830 - abs(math.sin(ph * math.pi)) * 60, S) + (1.4,), 0.06, (120, 110, 100), STONE)
    for x in (250, 560, 880): sombra(img, x, 1700, 140)
    rend(img, sc, S)
    k = ease(t / D)
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); arr = np.zeros((H, W, 4), np.uint8)
    xx = np.arange(W)[None, :]
    arr[..., 3] = np.clip((xx - W * (1.1 - 0.9 * k)) / 300 * 150, 0, 150).astype(np.uint8)
    arr[..., :3] = (20, 10, 30)
    img.alpha_composite(Image.fromarray(arr, "RGBA"))
    return img, (0.15, 0.2), 3 + 10 * k

@shot
def s11(t, D, T):   # ¡UN MAMUT!
    img = fondo(VALLE, 120, -60, 1.15)
    S = 215
    tr = ease(t / 0.45)
    sc = Scene()
    mamut(sc, *gp(820, 1800, S), 0, t, face=-1, trunk=tr, mouth=0.9 * tr * (1 - ease((t - 1.1) / 0.3)), expr="angry", ears=tr)
    rend(img, sc, S)
    polvo(img, 700, 1800, t, 2.2)
    if t > 0.2: comic(img, "¡MAMUT!", 540, 380, 190, t - 0.2, col=(255, 90, 60), ang=6)
    return img, (0.5, 0.0), 26 * math.exp(-t * 1.6)

@shot
def s12(t, D, T):   # Nico le da una porción
    img = fondo(VALLE, -80, 0, 1.1)
    S = 160
    eat = t > D * 0.62
    sc = Scene()
    trunk = 0.15 + 0.5 * ease((t - D * 0.35) / 0.5) - (0.3 * ease((t - D * 0.62) / 0.3))
    mamut(sc, *gp(830, 1700, S), -0.8, t, face=-1, trunk=clamp(trunk), expr="happy" if eat else "neutral",
          eye_happy=eat, mouth=0.4 * abs(math.sin(t * 12)) if eat else 0.0)
    rend(img, sc, S)
    S2 = 240
    sc2 = Scene()
    info = nico(sc2, *gp(190, 1760, S2), 0.5, t, yaw=0.3, arms=("down", "offer") if not eat else ("down", "down"), expr="nervous" if not eat else "happy",
                mouth=boca(11, t), sweat=not eat, head_yaw=0.35, look=(0.6, 0.6))
    if not eat:
        hr = info["hands"]["R"]
        pizza(sc2, hr[0] + 0.15, hr[1] + 0.2, hr[2] + 0.3, 0.32)
    sombra(img, 190, 1760, 130)
    rend(img, sc2, S2)
    if eat:
        d = ImageDraw.Draw(img)
        for k in range(4):
            ph = ((t - D * 0.62) * 0.8 + k * 0.25) % 1
            corazon(d, 520 + 90 * math.sin(k * 2 + t * 2), 900 - ph * 380, 34 * (1 - ph * 0.4), (255, 80, 120, int(255 * (1 - ph))))
    return img, (0.15, 0.2)

@shot
def s13(t, D, T):   # el primer delivery en mamut
    cx = t * 520 - 300
    img = fondo(VALLE, cx, -30, 1.0)
    S = 150
    sc = Scene()
    mx, my = 420, 1720
    bump = abs(math.sin(t * 6)) * 0.1
    mxw, myw = gp(mx, my, S)
    mamut(sc, mxw, myw + bump, 0, t, s=1.0, face=1, walk=t * 9, trunk=0.45, expr="happy")
    for k in range(4):
        sc.box((mxw - 1.0, myw + bump + 4.35 + k * 0.26, 0.9), 0.48, 0.12, 0.48, (226, 196, 150), Mat(spec=0.05, toon=0.6), bevel=0.3)
    nico(sc, mxw + 0.55, myw + bump + 4.05, 1.0, t, s=1.0, arms=("wave", "up"), expr="happy", bob=False)
    sombra(img, mx + 40, my, 330, 0.3)
    rend(img, sc, S)
    lineas_velocidad(img, t, 18, dirx=1)
    polvo(img, mx - 330, my, (t * 2) % 0.8, 1.2)
    return img, (0.15, 0.2)

@shot
def s14(t, D, T):   # cierre: Nico sobre la cabeza del mamut habla a cámara
    img = fondo(VALLE, 60, -120, 1.25)
    if t > D - 0.9:
        portal(img, 540, 900, 340, t, ease((t - (D - 0.9)) / 0.6))
    S = 200
    sc = Scene()
    mxw, myw = gp(1000, 2420, S)
    mamut(sc, mxw, myw, -2, t, s=1.0, face=-1, trunk=0.6, expr="happy", eye_happy=True)
    rend(img, sc, S)
    sc2 = Scene()
    m = boca(13, t)
    S2 = 270
    hx, hy = (mxw - 2.1) * S, -(myw + 3.5 + 1.05) * S
    nico(sc2, *gp(hx, hy, S2), 0, t, arms=("point", "wave") if t < D * 0.6 else ("up", "up"), expr="happy", mouth=m, look=(0, 0))
    rend(img, sc2, S2)
    if t > D * 0.5:
        k = eob((t - D * 0.5) / 0.3)
        f = font(64 * k + 1); txt = "¿QUÉ ÉPOCA?"
        tw = f.getlength(txt); lay = Image.new("RGBA", (int(tw + 120), int(150 * k + 10)), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        d.rounded_rectangle([0, 0, tw + 110, 120 * k], radius=int(40 * k) + 1, fill=(255, 255, 255, 255), outline=(20, 16, 22, 255), width=6)
        d.polygon([(60, 118 * k), (110, 118 * k), (50, 150 * k)], fill=(255, 255, 255, 255))
        d.text((55, 22 * k), txt, font=f, fill=(30, 24, 30))
        img.alpha_composite(lay, (int(hx - lay.width / 2), int(hy - 2.55 * S2 - 190)))
    return img, (0.15, 0.2)

# ------------------------------------------------------------ cuadro final
def frame(T):
    i = max(j for j in range(len(SHOTS)) if STARTS[j] <= T) if T < TOTAL else len(SHOTS) - 1
    t = T - STARTS[i]
    res = SHOTS[i](t, DURS[i], T)
    img, rayos = res[0], res[1]
    sh = res[2] if len(res) > 2 else 0
    if sh:
        dx, dy = sacudida(T, sh)
        img = img.transform(img.size, Image.AFFINE, (1, 0, dx, 0, 1, dy), resample=Image.BILINEAR)
    # pequeño empuje de cámara al inicio de cada plano
    zk = 1 + 0.035 * (1 - ease(t / 0.3))
    if zk > 1.001:
        w2, h2 = int(W / zk), int(H / zk)
        img = img.crop(((W - w2) // 2, (H - h2) // 2, (W - w2) // 2 + w2, (H - h2) // 2 + h2)).resize((W, H), Image.BILINEAR)
    img = realce.postproceso(img, T, tono="calido", bloom=0.3, grano=1.4, motas=True, rayos=rayos)
    # barrido de transición (desenfoque de movimiento los primeros cuadros)
    if i > 0 and t < 0.1:
        k = int(60 * (1 - t / 0.1))
        if k > 2:
            a = np.array(img); a = cv2_blur(a, k); img = Image.fromarray(a)
    caption(img, T)
    if i == 0 and t < 2.0:
        f = font(40); d = ImageDraw.Draw(img)
        d.rounded_rectangle([40, 120, 40 + f.getlength("MUNDO HIPOTÉTICO") + 50, 186], radius=18, fill=(38, 178, 198, 230), outline=(15, 12, 16), width=4)
        d.text((65, 128), "MUNDO HIPOTÉTICO", font=f, fill=(255, 255, 255))
    return img.convert("RGB")

def cv2_blur(a, k):
    import cv2
    return cv2.blur(a, (k, 1))

# ------------------------------------------------------------ sonido
def make_audio(path):
    from scipy.signal import butter, sosfilt
    sr = SR; n = int(TOTAL * sr) + sr; tt = np.arange(n) / sr; out = np.zeros(n)
    rng = np.random.default_rng(3)
    def add(s, sig, g=1.0):
        i0 = int(s * sr); i1 = min(n, i0 + len(sig))
        if 0 <= i0 < n: out[i0:i1] += g * sig[:i1 - i0]
    def seg(d): return np.arange(int(d * sr)) / sr
    hz = lambda m: 440 * 2 ** ((m - 69) / 12)
    # música: marimba + bajo + tambores tribales, 104 bpm
    b = 60 / 104
    prog = [[57, 60, 64], [53, 57, 60], [55, 59, 62], [52, 55, 59]]
    mel = [69, 72, 74, 72, 76, 74, 72, 69, 67, 69, 72, 71]
    for k in range(int(TOTAL / (b / 2)) + 1):
        s = k * b / 2; bar = int(s / (4 * b)) % 4; ch = prog[bar]
        x = seg(0.35)
        if k % 2 == 0:
            m = mel[(k // 2) % len(mel)] if (k // 2) % 4 != 3 else ch[0] + 12
            env = np.exp(-x * 9)
            add(s, 0.06 * env * (np.sin(2 * np.pi * hz(m) * x) + 0.4 * np.sin(2 * np.pi * hz(m) * 4 * x) * np.exp(-x * 30)))
        if k % 4 == 0:
            xb = seg(0.5); add(s, 0.11 * np.exp(-xb * 5) * np.sin(2 * np.pi * hz(ch[0] - 24) * xb))
        xd = seg(0.25)
        if k % 4 == 0: add(s, 0.28 * np.exp(-xd * 16) * np.sin(2 * np.pi * (70 + 90 * np.exp(-xd * 25)) * xd))     # tambor grave
        if k % 4 == 2: add(s, 0.14 * np.exp(-xd * 20) * np.sin(2 * np.pi * (180 + 120 * np.exp(-xd * 30)) * xd))   # tom
        if k % 2 == 1: add(s, 0.025 * rng.standard_normal(len(xd)) * np.exp(-xd * 40))                           # shaker
        for m in ch:
            if k % 8 == 0:
                xp = seg(1.6); add(s, 0.012 * np.exp(-xp * 1.2) * np.sin(2 * np.pi * hz(m) * xp))
    noise = rng.standard_normal(n)
    bp = lambda lo, hi: sosfilt(butter(2, [lo, hi], btype="band", fs=sr, output="sos"), noise)
    wh = bp(400, 3500); low = sosfilt(butter(2, 160, btype="low", fs=sr, output="sos"), noise)
    def whoosh(s, d=0.4, g=0.35):
        i0 = int(max(0, s - d / 2) * sr); i1 = min(n, i0 + int(d * sr)); x = np.arange(i1 - i0) / (i1 - i0)
        out[i0:i1] += g * np.sin(np.pi * x) ** 2 * wh[i0:i1]
    for s in STARTS[1:-1]: whoosh(s, 0.35, 0.25)
    S_ = STARTS
    # portal (zumbido que sube) + golpe al aterrizar
    x = seg(1.3); add(S_[1], 0.12 * np.sin(2 * np.pi * (200 + 500 * x) * x) * np.sin(np.pi * x / 1.3))
    x = seg(0.4); add(S_[1] + 1.25, 0.6 * np.exp(-x * 12) * np.sin(2 * np.pi * (60 + 60 * np.exp(-x * 20)) * x))
    for k in range(4): add(S_[2] + 0.9 + k * 0.28, 0.12 * bp(1500, 5000)[:int(0.12 * sr)] * np.hanning(int(0.12 * sr)))   # olfateo
    for k in range(3): add(S_[3] + 0.3 + k * 0.05, 0.0 * x[:10])
    x = seg(0.15); add(S_[3] + 0.3, 0.3 * np.exp(-x * 30) * np.sin(2 * np.pi * 900 * x))   # pop del texto
    for k in range(3): add(S_[4] + LEAD + len(VOZ[4]) / SR * (0.05 + 0.2 * k), 0.2 * np.exp(-x * 25) * np.sign(np.sin(2 * np.pi * 220 * x)))  # error
    xf = seg(1.5); add(S_[4] + LEAD + len(VOZ[4]) / SR * 0.62, 0.25 * wh[:len(xf)] * np.exp(-xf * 2) * (1 - np.exp(-xf * 20)))      # fuego
    for k in range(int(DURS[5] * 0.5 / 0.12)):   # piedras que caen
        xs = seg(0.12); add(S_[5] + k * 0.12, 0.25 * np.exp(-xs * 40) * bp(800, 3000)[:len(xs)])
    xg = seg(DURS[5] * 0.5); add(S_[5] + DURS[5] * 0.5, 0.06 * bp(300, 1200)[:len(xg)] * (0.5 + 0.5 * np.sin(2 * np.pi * 1.9 * xg)))
    xz = seg(1.6); add(S_[6], 0.08 * bp(3000, 8000)[:len(xz)] * np.exp(-xz * 1.2))                    # chisporroteo
    for k, f0 in enumerate((1318, 1568, 2093)):
        xd = seg(0.6); add(S_[6] + 0.55 + k * 0.08, 0.1 * np.exp(-xd * 6) * np.sin(2 * np.pi * f0 * xd))   # brillo pizza
    for k in range(5):
        xd = seg(0.5); add(S_[7] + 0.8 + k * 0.18, 0.08 * np.exp(-xd * 8) * np.sin(2 * np.pi * (1800 + 200 * k) * xd))   # gemas
    xr = seg(DURS[9]); add(S_[9], 0.5 * low[:len(xr)] * (xr / DURS[9]) ** 1.5)                               # retumbo
    for k in range(4):
        xs = seg(0.35); add(S_[9] + 0.3 + k * 0.45, 0.4 * np.exp(-xs * 10) * np.sin(2 * np.pi * 45 * xs))   # pisadas
    xr = seg(1.5)  # rugido
    roar = (np.sign(np.sin(2 * np.pi * (110 + 40 * np.sin(2 * np.pi * 6 * xr)) * xr)) * 0.3 + bp(200, 1200)[:len(xr)] * 0.8)
    add(S_[10] + 0.05, 0.35 * roar * np.sin(np.pi * np.clip(xr / 1.5, 0, 1)) ** 0.5)
    xm = seg(0.12)
    for k in range(5): add(S_[11] + DURS[11] * 0.62 + k * 0.17, 0.2 * bp(300, 2000)[:len(xm)] * np.hanning(len(xm)))   # ñam
    for k in range(int(DURS[12] / 0.33)):
        xs = seg(0.3); add(S_[12] + k * 0.33, 0.35 * np.exp(-xs * 12) * np.sin(2 * np.pi * 50 * xs))      # galope
    x = seg(1.0); add(S_[13] + DURS[13] - 0.9, 0.12 * np.sin(2 * np.pi * (300 + 600 * x) * x) * np.sin(np.pi * x))
    out = np.tanh(out * 1.2)
    out = out / (np.max(np.abs(out)) + 1e-9) * 0.33
    voice = np.zeros(n)
    for k, v in enumerate(VOZ):
        i0 = int((STARTS[k] + LEAD) * sr); i1 = min(n, i0 + len(v)); voice[i0:i1] += v[:i1 - i0] / (np.max(np.abs(v)) + 1e-9)
    voice *= 0.92
    env = np.convolve(np.abs(voice), np.ones(4410) / 4410, mode="same")
    mix = out * (1 - 0.5 * np.clip(env / 0.05, 0, 1)) + voice
    mix = mix[:int(TOTAL * sr)]; tt = tt[:len(mix)]
    mix *= np.clip((TOTAL - tt) / 0.4, 0, 1)
    mix = mix / np.max(np.abs(mix)) * 0.95
    wavfile.write(path, sr, (mix * 32767).astype(np.int16))

if __name__ == "__main__":
    if os.environ.get("PREVIEW"):
        ts = [float(x) for x in os.environ["PREVIEW"].split(",")]
        ims = [frame(T).resize((270, 480)) for T in ts]
        sheet = Image.new("RGB", (270 * 5, 480 * ((len(ims) + 4) // 5)))
        for k, im in enumerate(ims): sheet.paste(im, ((k % 5) * 270, (k // 5) * 480))
        sheet.save("sheet.png"); print("TOTAL", TOTAL, [round(s, 2) for s in STARTS]); sys.exit()
    if os.environ.get("BIG"):
        frame(float(os.environ["BIG"])).save("big.png"); sys.exit()
    make_audio("audio.wav")
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-i", "audio.wav", "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-pix_fmt", "yuv420p",
                          "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
    N = int(TOTAL * FPS)
    for k in range(N):
        p.stdin.write(frame(k / FPS).tobytes())
        if k % 150 == 0: print(f"{k}/{N}", flush=True)
    p.stdin.close(); p.wait(); print("listo", OUT, TOTAL)
