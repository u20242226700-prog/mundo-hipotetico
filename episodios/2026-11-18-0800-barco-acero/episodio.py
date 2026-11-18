#!/usr/bin/env python3
"""¿Por qué los barcos de acero flotan? (formato "¿Por qué…?" de días pares)
Estilo vector + cómic (motor/vc.py). Nico con traje de CAPITÁN DE BARCO (marinero: gorra blanca con banda turquesa,
chaqueta azul marino, pañuelo turquesa). Rival: Tito (constructor fortachón, barco de acero macizo).
Juez: Almirante Morsa. Dato real: principio de Arquímedes; el acero es ~7,85 veces más denso que el agua."""
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
DURS[0] += 0.3; DURS[1] += 1.1; DURS[7] += 0.6; DURS[14] += 0.5; DURS[15] += 1.0
CHUNKS = [
    [("¿Por qué un barco", []), ("de ACERO", ["ACERO"]), ("de miles de toneladas", ["toneladas"]), ("flota…", ["flota…"]), ("si un clavo", ["clavo"]), ("se hunde?", ["hunde?"])],
    [("Nico cruza el portal", ["portal"]), ("y cae en un astillero…", ["astillero…"]), ("¡justo en el gran", []), ("concurso de barcos!", ["barcos!"])],
    [("¡Mi barco es", []), ("de acero MACIZO!", ["MACIZO!"]), ("¡Más acero,", ["acero,"]), ("más fuerte!", ["fuerte!"]), ("¡Nada lo hunde!", ["hunde!"])],
    [("Uno.", ["Uno."]), ("Nico hace algo raro:", ["raro:"]), ("un barco HUECO…", ["HUECO…"]), ("casi vacío", ["vacío"]), ("por dentro", [])],
    [("¿¡Hueco!?", ["¿¡Hueco!?"]), ("¡Eso se va a hundir,", ["hundir,"]), ("muchacho!", []), ("¡Está vacío!", ["vacío!"])],
    [("Confíe en mí,", []), ("almirante.", []), ("El secreto está", ["secreto"]), ("en el agua", ["agua"]), ("que empuja", ["empuja"])],
    [("Nadie le cree…", ["cree…"]), ("y todos apuestan", []), ("por el barco", []), ("brillante de Tito", ["Tito"])],
    [("Dos.", ["Dos."]), ("¡Al agua!", ["agua!"]), ("El barco de Tito", []), ("aparta un poquito", ["poquito"]), ("de agua…", []), ("y se va directo", []), ("al fondo", ["fondo"])],
    [("¿¡Glu glu!?", ["¿¡Glu", "glu!?"]), ("¡Pero si era", []), ("el más fuerte!", ["fuerte!"])],
    [("Tres.", ["Tres."]), ("El agua empuja", ["empuja"]), ("hacia arriba", ["arriba"]), ("con la misma fuerza", ["fuerza"]), ("que pesa el agua", []), ("que apartas.", ["apartas."]), ("El barco hueco", ["hueco"]), ("aparta muchísima agua…", ["muchísima"]), ("y ese empujón", ["empujón"]), ("lo sostiene", ["sostiene"])],
    [("¡No importa", []), ("cuánto pesa,", ["pesa,"]), ("sino cuánta agua", ["agua"]), ("aparta!", ["aparta!"])],
    [("Esto lo descubrió", []), ("Arquímedes", ["Arquímedes"]), ("hace más de", []), ("dos mil años.", ["años."]), ("Dice la leyenda", []), ("que fue en una bañera…", ["bañera…"]), ("y salió gritando:", []), ("¡Eureka!", ["¡Eureka!"])],
    [("El acero pesa", ["acero"]), ("casi 8 veces más", ["8"]), ("que el agua.", ["agua."]), ("Pero un casco", []), ("lleno de aire,", ["aire,"]), ("en promedio,", []), ("pesa menos", ["menos"]), ("que el agua que aparta", ["aparta"])],
    [("¡Muchacho,", []), ("eres mi nuevo", []), ("capitán!", ["capitán!"]), ("¡Todos a bordo!", ["bordo!"])],
    [("Bueno…", []), ("a lo mejor", []), ("sí importa", ["importa"]), ("un poquito", ["poquito"]), ("lo que pesa", ["pesa"])],
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

# ------------------------------------------------------------ escenarios
def cielo(dr, t, alto=0.0, y_top=-1400, sepia=0.0):
    day = [(86, 156, 228), (118, 180, 236), (160, 204, 240), (226, 230, 236)]
    hi = [(20, 34, 90), (34, 60, 128), (60, 100, 170), (110, 150, 210)]
    for k in range(4):
        c = mix(day[k], hi[k], alto); c = mix(c, (196, 170, 120), sepia)
        dr.rrect(-1200, y_top + k * 700, 2400, (y_top + (k + 1) * 700 + 4) if k < 3 else 4000, 0, c)

def nubes(dr, t, y0=600, vel=260, n=6, col=(250, 250, 252), sz=1.0, layer=0):
    for k in range(n):
        x = 2200 - ((k * 517 + t * vel + layer * 300) % 3000)
        y = y0 + ((k * 211) % 5) * 120
        for j in range(4): dr.ell(x + j * 110 * sz, y - (j % 2) * 40 * sz, 150 * sz, 80 * sz, col, nolin=layer == 0)

def hangar(dr, t, y_floor=1500):
    dr.rrect(-1200, -1400, 2400, y_floor, 0, (92, 104, 130))
    for k in range(-4, 8):   # vigas en arco
        x = k * 300

STEEL = (150, 160, 176); STEEL_D = (96, 104, 122); SEA = (40, 120, 176); SEA_D = (24, 78, 130); AIRE = (226, 244, 252)

def mar_fondo(dr, ys, t, deep=2600):
    """Agua de fondo (vista de acuario): desde la superficie ys hacia abajo."""
    dr.rrect(-1200, ys, 2400, ys + 380, 0, SEA, nolin=True)
    dr.rrect(-1200, ys + 380, 2400, ys + 900, 0, mix(SEA, SEA_D, 0.5), nolin=True)
    dr.rrect(-1200, ys + 900, 2400, deep + 1400, 0, SEA_D, nolin=True)
    for k in range(10):   # rayos de luz bajo el agua
        x = -200 + k * 160 + 40 * math.sin(t * 0.7 + k)
        dr.poly([(x, ys + 10), (x + 50, ys + 10), (x + 160, ys + 900), (x + 70, ys + 900)], mix(SEA, (120, 200, 230), 0.25), nolin=True)

def olas(dr, ys, t, col=(210, 236, 248), amp=14):
    pts = [(x, ys + amp * math.sin(x / 70 + t * 3)) for x in range(-1200, 2401, 40)]
    dr.line(pts, col, 16)

def muelle(dr, t, gy=1450, ys=1250):
    """Astillero: cielo + grúas + mar al fondo + muelle de madera al frente (gy = piso)."""
    cielo(dr, t, 0.0)
    nubes(dr, t, 300, 60, n=4, layer=0, col=(246, 248, 252))
    for gx, h in ((-120, 900), (1180, 1050)):   # grúas
        dr.rrect(gx - 30, ys - h, gx + 30, ys, 6, (230, 150, 40), shade=True)
        dr.rrect(gx - 260, ys - h - 30, gx + 360, ys - h + 20, 6, (230, 150, 40), shade=True)
        dr.line([(gx + 300, ys - h + 20), (gx + 300, ys - h + 360)], INK, 5)
        dr.rrect(gx + 280, ys - h + 350, gx + 320, ys - h + 390, 4, (80, 80, 90))
    dr.rrect(-1200, ys, 2400, gy, 0, SEA, nolin=True)
    olas(dr, ys, t, amp=8)
    dr.rrect(-1200, gy, 2400, 3400, 0, (166, 112, 66))
    for k in range(-6, 14): dr.line([(k * 180, gy), (k * 180, 3400)], (130, 84, 46), 6, nolin=True)
    dr.rrect(-1200, gy - 10, 2400, gy + 22, 0, (120, 76, 40))
    for k in range(-4, 10): dr.rrect(k * 260 - 22, gy - 60, k * 260 + 22, gy + 10, 8, (110, 70, 40), shade=True)

def gaviota(dr, x, y, s, t):
    S = lambda v: v * s
    f = math.sin(t * 9) * 0.5
    dr.ell(x, y, S(40), S(22), (250, 250, 250))
    dr.ell(x + S(34), y - S(14), S(18), S(16), (250, 250, 250))
    dr.poly([(x + S(48), y - S(14)), (x + S(70), y - S(8)), (x + S(48), y - S(6))], (240, 180, 50))
    dr.ell(x + S(38), y - S(18), S(4), S(4), INK, nolin=True)
    for sx in (-1, 1):
        dr.poly([(x - S(10), y - S(6)), (x + S(14), y - S(6)), (x + sx * S(4) - S(30), y - S(60) * (0.6 + f * sx))], (220, 224, 232))

def barco_macizo(dr, x, y, L, t, shine=1.0, tilt=0.0):
    """Lingote de acero con forma de barco. (x, y) = centro de la línea de cubierta. Alto ≈ 0.42 L."""
    H = L * 0.34
    c, s_ = math.cos(tilt), math.sin(tilt)
    R = lambda px, py: (x + (px - x) * c - (py - y) * s_, y + (px - x) * s_ + (py - y) * c)
    hull = [R(x - L / 2, y), R(x + L / 2, y), R(x + L * 0.4, y + H), R(x - L * 0.42, y + H)]
    dr.poly(hull, STEEL, shade=True)
    dr.poly([R(x - L / 2, y), R(x + L / 2, y), R(x + L / 2 - 8, y + H * 0.14), R(x - L / 2 + 8, y + H * 0.14)], (190, 198, 212))
    for k in range(9):
        px = x - L * 0.4 + k * L * 0.1
        for j in range(2): dr.ell(*R(px, y + H * (0.32 + j * 0.36)), L * 0.008, L * 0.008, STEEL_D, nolin=True)
    if shine > 0:   # brillo diagonal de lingote
        sx = x - L * 0.3 + ((t * 0.5) % 1) * L * 0.8
        dr.poly([R(sx, y + H * 0.16), R(sx + L * 0.06, y + H * 0.16), R(sx - L * 0.04, y + H * 0.95), R(sx - L * 0.1, y + H * 0.95)], (236, 242, 250), nolin=True)
    cab = [R(x - L * 0.14, y), R(x + L * 0.14, y), R(x + L * 0.12, y - H * 0.5), R(x - L * 0.12, y - H * 0.5)]
    dr.poly(cab, (180, 188, 204), shade=True)
    dr.rrect(*R(x - L * 0.09, y - H * 0.42), *R(x + L * 0.09, y - H * 0.28), L * 0.01, (110, 160, 210)) if abs(tilt) < 0.01 else None
    dr.text(*R(x, y + H * 0.55), "TITO", int(L * 0.09), (70, 76, 92))
    return H

def barco_hueco(dr, x, y, L, t, corte=False, tilt=0.0, gente=False):
    """Barco hueco. (x, y) = centro de la línea de cubierta. corte=True muestra el interior lleno de AIRE."""
    H = L * 0.34; e = L * 0.03
    c, s_ = math.cos(tilt), math.sin(tilt)
    R = lambda px, py: (x + (px - x) * c - (py - y) * s_, y + (px - x) * s_ + (py - y) * c)
    hull = [R(x - L / 2, y), R(x + L / 2, y), R(x + L * 0.4, y + H), R(x - L * 0.42, y + H)]
    if corte:
        dr.poly(hull, (60, 66, 84))
        dr.poly([R(x - L / 2 + e * 1.4, y + e * 0.6), R(x + L / 2 - e * 1.4, y + e * 0.6), R(x + L * 0.4 - e, y + H - e), R(x - L * 0.42 + e, y + H - e)], AIRE)
        dr.text(*R(x, y + H * 0.5), "AIRE", int(L * 0.1), (120, 170, 200))
    else:
        dr.poly(hull, (250, 250, 248), shade=True)
        dr.poly([R(x - L * 0.47, y + H * 0.62), R(x + L * 0.455, y + H * 0.62), R(x + L * 0.4, y + H), R(x - L * 0.42, y + H)], (200, 50, 50))
        dr.poly([R(x - L * 0.49, y + H * 0.14), R(x + L * 0.49, y + H * 0.14), R(x + L * 0.485, y + H * 0.26), R(x - L * 0.485, y + H * 0.26)], TURQ, nolin=True)
        for k in range(6): dr.ell(*R(x - L * 0.3 + k * L * 0.12, y + H * 0.42), L * 0.022, L * 0.022, (110, 170, 220))
        dr.text(*R(x, y + H * 0.82), "NICO", int(L * 0.06), (255, 255, 255))
    cab = [R(x - L * 0.2, y), R(x + L * 0.1, y), R(x + L * 0.08, y - H * 0.45), R(x - L * 0.18, y - H * 0.45)]
    dr.poly(cab, (250, 250, 248), shade=True)
    dr.poly([R(x + L * 0.14, y), R(x + L * 0.22, y), R(x + L * 0.24, y - H * 0.8), R(x + L * 0.14, y - H * 0.8)], (200, 50, 50))
    dr.poly([R(x + L * 0.14, y - H * 0.62), R(x + L * 0.235, y - H * 0.62), R(x + L * 0.24, y - H * 0.8), R(x + L * 0.14, y - H * 0.8)], TURQ)
    for k in range(3):   # humito
        ph = (t * 0.8 + k / 3) % 1
        dr.ell(*R(x + L * 0.19 + ph * L * 0.12, y - H * (0.9 + ph * 0.8)), L * 0.03 * (0.6 + ph), L * 0.025 * (0.6 + ph), (236, 238, 242), nolin=True)
    if gente:
        for k in range(3): dr.ell(*R(x - L * 0.14 + k * L * 0.07, y - H * 0.25), L * 0.02, L * 0.025, (236, 196, 160))
    return H

def tito(dr, x, y, s, t, mouth=0.0, expr="smug", arm_r=30, arm_l=30, wet=False, look=(0, 0), flex=False):
    """(x, y) = pies. Constructor fortachón: camiseta sin mangas, overol naranja, bigote, pelo cepillo. Altura ≈ 880*s."""
    S = lambda v: v * s
    bob = S(5) * math.sin(t * 2.2 + 0.5)
    skin = (214, 160, 120); ov = (236, 120, 40)
    for sx in (-1, 1):
        dr.rrect(x + sx * S(50) - S(30), y - S(300), x + sx * S(50) + S(30), y - S(10), S(14), ov)
        dr.ell(x + sx * S(60), y - S(8), S(48), S(22), (60, 44, 34))
    dr.poly([(x - S(170), y - S(640) + bob), (x + S(170), y - S(640) + bob), (x + S(100), y - S(290)), (x - S(100), y - S(290))], (238, 238, 232), shade=True)
    dr.rrect(x - S(100), y - S(420), x + S(100), y - S(280), S(16), ov)
    for sx in (-1, 1): dr.line([(x + sx * S(70), y - S(420)), (x + sx * S(110), y - S(630) + bob)], ov, S(22))
    dr.rrect(x - S(30), y - S(390), x + S(30), y - S(350), S(6), TURQ if False else (250, 200, 60))
    hands = []
    for sx, ang in ((-1, arm_l), (1, arm_r)):
        shx, shy = x + sx * S(165), y - S(600) + bob
        a = math.radians(ang)
        if flex:
            ex, ey = shx + sx * S(150), shy + S(10)
            hx, hy = ex + sx * S(10), ey - S(150)
            dr.line([(shx, shy), (ex, ey), (hx, hy)], skin, S(80))
            dr.ell(ex - sx * S(40), ey - S(50), S(60), S(50), skin)
        else:
            hx, hy = shx + sx * math.sin(a) * S(250), shy + math.cos(a) * S(250)
            dr.line([(shx, shy), (hx, hy)], skin, S(80))
        dr.ell(hx, hy, S(46), S(46), skin)
        hands.append((hx, hy))
    hx, hy = x, y - S(760) + bob
    dr.rrect(hx - S(50), hy + S(40), hx + S(50), hy + S(130), S(20), skin)
    dr.ell(hx, hy, S(115), S(130), skin, shade=True)
    dr.rrect(hx - S(118), hy - S(170), hx + S(118), hy - S(80), S(20), (50, 36, 30))   # pelo cepillo
    for k in range(7): dr.line([(hx - S(100) + k * S(33), hy - S(165)), (hx - S(100) + k * S(33), hy - S(195))], (50, 36, 30), S(14))
    for sx in (-1, 1):
        ex, ey = hx + sx * S(46), hy - S(20)
        if expr == "cry":
            dr.chord(ex, ey + S(6), S(24), S(18), 180, 360, INK); dr.chord(ex, ey + S(12), S(20), S(12), 180, 360, skin)
            k = (t * 1.6 + (sx > 0) * 0.5) % 1
            dr.ell(ex + sx * S(10), ey + S(40) + S(90) * k, S(12), S(18), (140, 210, 255))
        else:
            big = 1.3 if expr == "shock" else 1.0
            dr.ell(ex, ey, S(22) * big, S(26) * big, (255, 255, 255))
            dr.ell(ex + look[0] * S(7), ey + look[1] * S(7), S(10), S(12), INK)
        tilt = {"angry": 18, "smug": 10, "shock": -14, "cry": -20}.get(expr, 0)
        dr.line([(ex - S(30), ey - S(44) + sx * S(tilt) * 0.5), (ex + S(30), ey - S(44) - sx * S(tilt) * 0.5)], (50, 36, 30), S(16))
    dr.ell(hx, hy + S(30), S(26), S(22), mix(skin, (190, 100, 80), 0.4))
    mo = clamp(mouth)
    if mo > 0.06 or expr in ("shock", "cry"):
        mo = max(mo, 0.5 if expr in ("shock", "cry") else 0)
        dr.ell(hx, hy + S(90), S(40), S(10 + 34 * mo), (100, 24, 34))
    elif expr == "smug":
        dr.line([(hx - S(40), hy + S(92)), (hx + S(10), hy + S(96)), (hx + S(44), hy + S(80))], (100, 24, 34), S(10))
    else:
        dr.chord(hx, hy + S(76), S(40), S(30), 0, 180, (100, 24, 34))
    dr.poly([(hx - S(80), hy + S(70)), (hx, hy + S(50)), (hx + S(80), hy + S(70)), (hx + S(60), hy + S(84)), (hx, hy + S(68)), (hx - S(60), hy + S(84))], (50, 36, 30))   # bigote
    if wet:
        for k in range(4):
            ph = (t * 1.5 + k * 0.25) % 1
            dr.ell(hx - S(120) + k * S(80), hy - S(150) + S(260) * ph, S(10), S(15), (140, 210, 255))
        dr.ell(hx + S(60), hy - S(200), S(40), S(26), (60, 150, 90))   # alga en la cabeza
    return dict(hands=hands, head=(hx, hy))

def morsa(dr, x, y, s, t, mouth=0.0, expr="angry", arm_r=20, arm_l=20, jump=0.0, look=(0, 0), red=0.0):
    """(x, y) = base. Almirante Morsa: cuerpo de pera marrón, bicornio azul con dorado, medallas, colmillos. Alto ≈ 900*s."""
    S = lambda v: v * s
    y = y - S(jump)
    bob = S(6) * math.sin(t * 2.0)
    body = mix((150, 104, 80), (220, 90, 80), red); dark = mix(body, (40, 20, 20), 0.3)
    dr.ell(x, y - S(250), S(260), S(260), body, shade=True)
    dr.ell(x, y - S(470) + bob, S(200), S(200), body, shade=True)
    for sx in (-1, 1): dr.poly([(x + sx * S(150), y - S(20)), (x + sx * S(300), y + S(10)), (x + sx * S(290), y - S(60)), (x + sx * S(170), y - S(90))], dark)
    dr.rrect(x - S(150), y - S(470) + bob, x + S(150), y - S(120), S(60), (36, 52, 104), shade=True)   # chaqueta de almirante
    dr.rrect(x - S(150), y - S(170), x + S(150), y - S(130), S(10), TURQ)
    for k in range(3): dr.ell(x - S(60) + k * S(60), y - S(380) + bob, S(18), S(18), [(246, 200, 60), (220, 60, 60), (246, 200, 60)][k])
    for sx in (-1, 1): dr.rrect(x + sx * S(150) - S(40), y - S(470) + bob, x + sx * S(150) + S(40), y - S(440) + bob, S(6), (246, 200, 60))
    hands = []
    for sx, ang in ((-1, arm_l), (1, arm_r)):
        shx, shy = x + sx * S(170), y - S(420) + bob
        a = math.radians(ang)
        hx, hy = shx + sx * math.sin(a) * S(200), shy + math.cos(a) * S(200)
        dr.line([(shx, shy), (hx, hy)], (36, 52, 104), S(60))
        dr.ell(hx, hy, S(46), S(30), dark)
        hands.append((hx, hy))
    hx, hy = x, y - S(660) + bob
    dr.ell(hx, hy, S(170), S(150), body, shade=True)
    for sx in (-1, 1):
        ex, ey = hx + sx * S(62), hy - S(40)
        dr.ell(ex, ey, S(22), S(24), (255, 255, 255))
        dr.ell(ex + look[0] * S(6), ey + look[1] * S(6), S(11), S(13), INK)
        tilt = {"angry": 20, "happy": -8, "shock": -14}.get(expr, 0)
        dr.line([(ex - S(30), ey - S(40) - sx * S(tilt) * 0.5), (ex + S(30), ey - S(40) + sx * S(tilt) * 0.5)], (60, 40, 30), S(14))
    mo = clamp(mouth)
    if mo > 0.06 or expr == "shock":
        dr.ell(hx, hy + S(80), S(50), S(12 + 40 * max(mo, 0.5 if expr == "shock" else 0)), (100, 24, 34))
    for sx in (-1, 1):   # colmillos
        dr.poly([(hx + sx * S(30), hy + S(70)), (hx + sx * S(56), hy + S(70)), (hx + sx * S(48), hy + S(230)), (hx + sx * S(40), hy + S(232))], (252, 248, 236))
    for sx in (-1, 1): dr.ell(hx + sx * S(52), hy + S(52), S(62), S(46), mix(body, (240, 210, 180), 0.5))   # hocico
    dr.ell(hx, hy + S(14), S(30), S(20), (60, 36, 30))
    for sx in (-1, 1):
        for k in range(3): dr.line([(hx + sx * S(70), hy + S(44) + k * S(14)), (hx + sx * S(150), hy + S(30) + k * S(22))], (60, 40, 30), S(4), nolin=True)
    if expr == "happy" and mo < 0.06: dr.chord(hx, hy + S(96), S(40), S(26), 0, 180, (100, 24, 34))
    # bicornio
    dr.poly([(hx - S(230), hy - S(120)), (hx, hy - S(300)), (hx + S(230), hy - S(120)), (hx, hy - S(160))], (30, 40, 84))
    dr.line([(hx - S(220), hy - S(124)), (hx, hy - S(164)), (hx + S(220), hy - S(124))], (246, 200, 60), S(10))
    dr.ell(hx, hy - S(210), S(26), S(26), TURQ); dr.ell(hx, hy - S(210), S(10), S(10), (255, 255, 255))
    return dict(hands=hands, head=(hx, hy))

def banera(dr, x, y, s, t, agua=True):
    S = lambda v: v * s
    for sx in (-1, 1): dr.ell(x + sx * S(200), y + S(20), S(26), S(20), (246, 200, 60))
    dr.chord(x, y - S(100), S(260), S(150), 0, 180, (250, 250, 252))
    dr.rrect(x - S(270), y - S(130), x + S(270), y - S(90), S(20), (240, 240, 246))
    if agua:
        for k in range(5): dr.ell(x - S(200) + k * S(100), y - S(130) - S(10) * math.sin(t * 5 + k), S(60), S(30), (236, 246, 252))
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


def badge(img, T):
    d = ImageDraw.Draw(img); f = font(36); txt = "¿POR QUÉ…?"
    d.rounded_rectangle([36, 110, 36 + f.getlength(txt) + 44, 170], radius=16, fill=TURQ, outline=INK, width=5)
    d.text((58, 140), txt, font=f, fill=(255, 255, 255), anchor="lm")


def flechas_up(img, xs, y, t, col=(120, 230, 140), L=120, txt=None):
    d = ImageDraw.Draw(img); a = 0.5 + 0.5 * math.sin(t * 6)
    for x in xs:
        y1 = y - L - 20 * a
        d.line([(x, y), (x, y1)], fill=INK, width=30); d.line([(x, y), (x, y1)], fill=col, width=16)
        d.polygon([(x - 34, y1), (x + 34, y1), (x, y1 - 44)], fill=col, outline=INK)
    if txt: d.text((sum(xs) / len(xs), y + 60), txt, font=font(56), fill=col, anchor="mm", stroke_width=8, stroke_fill=INK)

def burbujas(dr, x, y, t, n=8, w=200, h=600):
    for k in range(n):
        ph = (t * 0.9 + k * 0.137) % 1
        dr.ell(x - w / 2 + (k * 73) % w + 10 * math.sin(t * 4 + k), y - ph * h, 10 + (k % 3) * 6, 10 + (k % 3) * 6, (200, 236, 255), nolin=True)

# ------------------------------------------------------------ planos
SHOTS = []
def shot(fn): SHOTS.append(fn); return fn
def tl(k, frac): return LEAD + len(VOZ[k]) / SR * frac
def D_(cam, bg=(0, 0, 0)): return D(cam, bg)
GY = 1450; YS = 1250
PAS = [(220, 80, 80), (80, 120, 210), (240, 180, 60), (120, 180, 100), (180, 100, 200)]

@shot
def s01(t, D, T):    # gancho: barco gigante de acero flotando vs. clavo que se hunde
    u = ease(t / D)
    cam = Cam(540, lerp(980, 1020, u), lerp(1.0, 1.12, u))
    dr = D_(cam); cielo(dr, t, 0.0); nubes(dr, t, 250, 80, n=4)
    ys = 1080
    mar_fondo(dr, ys, t)
    barco_hueco(dr, 470, ys - 120 + 8 * math.sin(t * 2), 1000, t, gente=True)
    # clavo hundiéndose en el agua (derecha)
    cy = ys + 80 + 700 * ease(clamp((t - tl(0, 0.55)) / 1.2))
    dr.rrect(880, cy - 90, 900, cy + 60, 4, (120, 124, 136)); dr.rrect(860, cy - 100, 920, cy - 84, 4, (120, 124, 136))
    if t > tl(0, 0.55): burbujas(dr, 890, cy, t, n=5, w=60, h=200)
    olas(dr, ys, t)
    f = tinta(dr); img = acabado(f, T)
    burst(img, "¿POR QUÉ?", 540, 360, 150, t - 0.1, ang=-6)
    if t > tl(0, 0.3):
        k = eob((t - tl(0, 0.3)) / 0.3); d = ImageDraw.Draw(img)
        d.rounded_rectangle([80, 1340, 560, 1440], radius=20, fill=(30, 30, 46), outline=(250, 200, 60), width=8)
        d.text((320, 1390), "50.000 t", font=font(70 * k + 1), fill=(250, 220, 60), anchor="mm")
    if t > tl(0, 0.65):
        k = eob((t - tl(0, 0.65)) / 0.3); d = ImageDraw.Draw(img)
        d.rounded_rectangle([700, 1340, 1020, 1440], radius=20, fill=(250, 250, 246), outline=INK, width=8)
        d.text((860, 1390), "5 g", font=font(70 * k + 1), fill=(220, 50, 50), anchor="mm")
        check(img, 1000, 1310, False, 0.5)
    return img, 0

@shot
def s02(t, D, T):    # portal → Nico capitán cae en el astillero
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
    dr = D_(cam); muelle(dr, t, GY, YS)
    barco_macizo(dr, 200, YS - 60, 700, t, shine=1)
    barco_hueco(dr, 880, YS - 50, 560, t)
    for k in range(4): persona(dr, -40 + k * 330, 1950 + (k % 2) * 30, 0.4, t, PAS[k], ph=k)
    portal(dr, 540, 1150, 220, t, 1 - ease((tt - 0.7) / 0.4))
    land = clamp(tt / 0.35)
    sq = 1 - 0.3 * math.exp(-tt * 7) * math.cos(tt * 20) if land >= 1 else 1.15
    nico(dr, 540, lerp(1050, 1820, land ** 2), 0.66, t, traje="marinero", arms=(140, 140) if land < 1 else (30, 165), elbows=(0, 15), expr="shock" if tt < 0.9 else "happy", squash=sq, look=(0.3, -0.6))
    f = tinta(dr)
    if tt < 0.2: f += 255 * (1 - tt / 0.2)
    img = acabado(f, T)
    if tt > 0.5: cartel(img, tt - 0.5, "GRAN CONCURSO", "¿QUÉ BARCO FLOTA MEJOR?", y=300)
    return img, 0

@shot
def s03(t, D, T):    # Tito presume su barco de acero macizo
    cam = Cam(lerp(560, 520, ease(t / D)), 1080, lerp(1.2, 1.3, ease(t / D)))
    dr = D_(cam); muelle(dr, t, GY, YS)
    barco_macizo(dr, 760, 1020, 900, t, shine=1)
    tito(dr, 400, 1900, 1.0, t, expr="smug" if boca(2, t) < 0.3 else "happy", mouth=boca(2, t), flex=t > tl(2, 0.5), arm_r=150, arm_l=30)
    f = tinta(dr); img = acabado(f, T)
    nombre(img, t - 0.1, "TITO", "el constructor fortachón", col=(236, 120, 40))
    if t > tl(2, 0.25): burst(img, "¡MACIZO!", 780, 760, 120, t - tl(2, 0.25), col=(220, 228, 240), ang=8)
    return img, 0

@shot
def s04(t, D, T):    # PASO 1: el barco de Nico es hueco (corte)
    u = ease(t / D)
    cam = Cam(560, lerp(1060, 1090, u), lerp(1.12, 1.2, u))
    dr = D_(cam); muelle(dr, t, GY, YS)
    op = clamp((t - tl(3, 0.45)) / 0.5)
    barco_hueco(dr, 620, 900, 900, t, corte=op > 0.5)
    nico(dr, 300, 1880, 0.7, t, traje="marinero", arms=(20, 120), elbows=(0, 20), expr="happy", look=(0.8, -0.5))
    f = tinta(dr); img = acabado(f, T)
    tarjeta_paso(img, t, 1, "EL “ERROR”")
    if op > 0.5: burst(img, "¡HUECO!", 640, 1260, 100, t - tl(3, 0.45) - 0.25, col=(255, 255, 255), ang=6)
    return img, 0

@shot
def s05(t, D, T):    # Almirante Morsa furioso
    cam = Cam(540, 1060, lerp(1.45, 1.55, ease(t / D)))
    dr = D_(cam); muelle(dr, t, GY, YS)
    barco_hueco(dr, 920, 1000, 600, t, corte=True)
    morsa(dr, 470, 1880, 1.05, t, mouth=boca(4, t), expr="angry", arm_r=150 + 12 * math.sin(t * 9), arm_l=40, red=clamp(t / 1.2) * 0.6, look=(0.6, 0))
    f = tinta(dr); img = acabado(f, T)
    burst(img, "¿¡HUECO!?", 540, 380, 130, t - 0.05, col=(255, 90, 70), ang=-6)
    nombre(img, t - 0.15, "ALMIRANTE MORSA", "el juez del concurso", y=490, col=(36, 52, 104))
    return img, 2 * math.sin(t * 40) if t < 1.0 else 0

@shot
def s06(t, D, T):    # Nico: confíe en mí, el secreto está en el agua que empuja
    cam = Cam(540, 1080, 1.65)
    dr = D_(cam); muelle(dr, t, GY, YS)
    nico(dr, 560, 1720, 0.72, t, traje="marinero", arms=(25, 120), elbows=(0, 60), expr="smug" if boca(5, t) < 0.2 else "happy", mouth=boca(5, t), look=(-0.4, 0))
    f = tinta(dr); img = acabado(f, T)
    if t > tl(5, 0.5):
        k = eob((t - tl(5, 0.5)) / 0.3); d = ImageDraw.Draw(img)
        cx, cy, r = 820, 600, 150 * k + 1
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(60, 140, 200), outline=INK, width=10)
        flechas_up(img, [cx - 50 * k, cx + 50 * k], cy + 90 * k, t, col=(120, 230, 140), L=110 * k + 1)
        burst(img, "¡EMPUJA!", 820, 820, 70, t - tl(5, 0.5), col=(120, 230, 140), ang=6)
    return img, 0

@shot
def s07(t, D, T):    # todos apuestan por Tito; en el barco de Nico solo una gaviota
    u = ease(t / D)
    cam = Cam(lerp(420, 640, u), 1150, 1.0)
    dr = D_(cam); muelle(dr, t, GY, YS)
    barco_macizo(dr, 960, YS - 40, 760, t, shine=1)
    barco_hueco(dr, 80, YS - 40, 520, t)
    gaviota(dr, 80, YS - 160, 1.0, t)
    nico(dr, 260, 1820, 0.5, t, traje="marinero", arms=(10, 10), expr="worried", look=(1, 0))
    tito(dr, 1040, 1830, 0.55, t, expr="smug", flex=True)
    for k in range(6):
        persona(dr, 420 + k * 110 + u * 300, 1880 + (k % 2) * 30, 0.36, t, PAS[k % 5], ph=k, run=u < 0.85)
    f = tinta(dr); img = acabado(f, T)
    if t > tl(6, 0.55): burst(img, "¡TODOS CON TITO!", 640, 420, 84, t - tl(6, 0.55), col=(250, 170, 90), ang=-5)
    return img, 0

@shot
def s08(t, D, T):    # PASO 2: al agua → el barco macizo se hunde
    ys = 820
    cam = Cam(540, lerp(900, 1150, ease(clamp((t - 1.2) / (D - 1.2)))), 1.0)
    dr = D_(cam); cielo(dr, t, 0.0, y_top=-1800); mar_fondo(dr, ys, t)
    sink = ease(clamp((t - tl(7, 0.5)) / (D - tl(7, 0.5) - 0.3)))
    dip = ease(clamp((t - 0.4) / 0.6))
    by = ys - 120 + 140 * dip + 1100 * sink
    barco_macizo(dr, 540, by, 760, t, shine=0, tilt=0.12 * sink)
    if sink > 0: burbujas(dr, 540, by, t, n=12, w=500, h=500)
    # agua desplazada: una franjita pequeña
    if t > tl(7, 0.3):
        k = eob((t - tl(7, 0.3)) / 0.3)
        dr.rrect(780, ys - 30 * k, 960, ys, 6, (110, 190, 230), nolin=True)
    olas(dr, ys, t, amp=10 + 20 * math.exp(-max(0, t - 0.9) * 3))
    f = tinta(dr); img = acabado(f, T)
    tarjeta_paso(img, t, 2, "¡AL AGUA!")
    if t > tl(7, 0.3):
        d = ImageDraw.Draw(img); X, Y = cam.p(830, ys - 30)
        d.text((X, Y - 70), "POQUITA AGUA", font=font(46), fill=(255, 255, 255), anchor="mm", stroke_width=8, stroke_fill=INK)
    if sink > 0.5: burst(img, "¡GLU GLU!", 540, 420, 130, t - tl(7, 0.5) - 1.0, col=(150, 220, 255), ang=-6)
    return img, 0

@shot
def s09(t, D, T):    # Tito empapado con el agua al cuello
    cam = Cam(540, 1060, 1.0)
    dr = D_(cam); cielo(dr, t, 0.1)
    ys = 1330
    dr.rrect(-1200, ys, 2400, 3400, 0, SEA, nolin=True)
    tito(dr, 540, 2180, 1.25, t, expr="cry" if boca(8, t) < 0.25 else "shock", mouth=boca(8, t), wet=True, arm_r=160 + 10 * math.sin(t * 8), arm_l=165)
    dr.rrect(-1200, ys + 60, 2400, 3400, 0, SEA, nolin=True)
    olas(dr, ys + 60, t, amp=16)
    for k in range(5):
        ph = (t * 1.2 + k * 0.2) % 1
        dr.ell(200 + k * 170, ys + 40 - 100 * math.sin(ph * math.pi), 14, 14, (220, 240, 255), nolin=True)
    f = tinta(dr); img = acabado(f, T)
    burst(img, "¿GLU GLU?", 540, 400, 120, t - 0.1, col=(150, 220, 255), ang=6)
    return img, 2 * math.sin(t * 30)

@shot
def s10(t, D, T):    # PASO 3: el empuje del agua (diagrama)
    cam = Cam(540, 960, 1.0)
    dr = D_(cam, bg=(30, 40, 60)); ys = 900
    dr.rrect(-600, -400, 1700, ys, 0, (34, 44, 70))
    mar_fondo(dr, ys, t)
    # izquierda: macizo, aparta poca agua (se hunde)
    lx, rx = 290, 790
    sk = ease(clamp((t - tl(9, 0.15)) / 2.0))
    barco_macizo(dr, lx, ys - 70 + 650 * sk, 420, t, shine=0)
    # derecha: hueco con corte, flota; zona de agua apartada marcada
    rh = 0.34 * 500
    disp = ease(clamp((t - tl(9, 0.62)) / 0.6))
    if disp > 0:
        dr.poly([(rx - 250, ys), (rx + 250, ys), (rx + 200, ys - 40 + rh), (rx - 210, ys - 40 + rh)], (120, 210, 250), nolin=True)
    barco_hueco(dr, rx, ys - 40, 500, t, corte=True)
    olas(dr, ys, t, amp=8)
    f = tinta(dr)
    if disp > 0: add_glow(f, rx, ys + 110, 260, (120, 230, 140), 0.25 * disp)
    img = acabado(f, T); d = ImageDraw.Draw(img)
    tarjeta_paso(img, t, 3, "EL EMPUJE")
    flechas_up(img, [lx - 40, lx + 40], 1450, t, col=(255, 150, 90), L=60)
    d.rounded_rectangle([60, 1500, 520, 1580], radius=16, fill=(230, 60, 60), outline=INK, width=6)
    d.text((290, 1540), "EMPUJE CHIQUITO", font=font(42), fill=(255, 255, 255), anchor="mm")
    if disp > 0:
        flechas_up(img, [rx - 110, rx, rx + 110], 1420, t, col=(120, 230, 140), L=150 * disp + 1)
        d.rounded_rectangle([560, 1500, 1020, 1580], radius=16, fill=(80, 190, 110), outline=INK, width=6)
        d.text((790, 1540), "EMPUJE GIGANTE", font=font(42), fill=(255, 255, 255), anchor="mm")
    return img, 0

@shot
def s11(t, D, T):    # Nico sobre su barco flotando, explica
    cam = Cam(540, 1060, 1.25)
    dr = D_(cam); cielo(dr, t, 0.0); nubes(dr, t, 300, 80, n=4)
    ys = 1320
    mar_fondo(dr, ys, t)
    by = ys - 150 + 10 * math.sin(t * 2)
    barco_hueco(dr, 560, by, 1000, t)
    nico(dr, 380, by + 2, 0.66, t, traje="marinero", arms=(70 + 25 * math.sin(t * 5), 150), elbows=(30, 10), expr="happy", mouth=boca(10, t), look=(0.6, -0.3))
    olas(dr, ys, t)
    f = tinta(dr); img = acabado(f, T)
    flechas_up(img, [300, 540, 780], 1560, t, col=(120, 230, 140), L=110)
    burst(img, "¡FLOTA!", 560, 330, 130, t - tl(10, 0.5), col=(120, 240, 140), ang=-5)
    return img, 0

@shot
def s12(t, D, T):    # Arquímedes en la bañera: ¡Eureka!
    u = ease(t / D)
    cam = Cam(540, lerp(1100, 1040, u), lerp(1.0, 1.12, u))
    dr = D_(cam, bg=(230, 210, 170))
    dr.rrect(-600, -400, 1700, 1500, 0, (232, 212, 172))
    for k in range(4):   # columnas griegas
        x = 60 + k * 320
        dr.rrect(x - 50, 300, x + 50, 1500, 6, (246, 236, 214), shade=True)
        dr.rrect(x - 75, 270, x + 75, 320, 6, (246, 236, 214))
        for j in range(3): dr.line([(x - 30 + j * 30, 330), (x - 30 + j * 30, 1490)], (210, 196, 170), 5, nolin=True)
    dr.rrect(-600, 1500, 1700, 3000, 0, (190, 150, 110))
    ex = t > tl(11, 0.82)
    # Arquímedes: anciano con barba y corona de laurel (genérico)
    S = 1.0; ax, ay = 540, 1360 - (160 if ex else 0) * ease(clamp((t - tl(11, 0.82)) / 0.2))
    dr.ell(ax, ay - 140, 150, 170, (238, 200, 166), shade=True)
    dr.ell(ax, ay - 40, 120, 110, (250, 250, 250))   # barba
    for sx in (-1, 1):
        dr.ell(ax + sx * 55, ay - 180, 22, 26, (255, 255, 255)); dr.ell(ax + sx * 55, ay - 176, 10, 13, INK)
        dr.line([(ax + sx * 30, ay - 230), (ax + sx * 85, ay - 240 + (12 if ex else 0))], (220, 220, 226), 12)
    if ex: dr.ell(ax, ay - 80, 40, 36, (100, 24, 34))
    for k in range(7): dr.ell(ax - 130 + k * 43, ay - 300 + abs(k - 3) * 10, 30, 18, (90, 160, 70))
    if ex:
        for sx in (-1, 1): dr.line([(ax + sx * 110, ay - 20), (ax + sx * 230, ay - 220)], (238, 200, 166), 50)
    banera(dr, 540, 1640, 1.6, t)
    if ex:
        for k in range(10):
            ph = ((t - tl(11, 0.82)) * 1.4 + k * 0.1) % 1
            dr.ell(160 + k * 85, 1450 + 300 * ph - 200 * math.sin(ph * math.pi), 18, 24, (170, 220, 250), nolin=True)
    f = tinta(dr)
    f = f * 0.85 + np.array([196, 170, 120]) * 0.15
    img = acabado(f, T)
    cartel(img, t - 0.2, "ARQUÍMEDES", "HACE MÁS DE 2.000 AÑOS", y=300, c2=(170, 110, 40))
    if ex: burst(img, "¡EUREKA!", 540, 760, 150, t - tl(11, 0.82), ang=-8)
    return img, (6 * math.exp(-(t - tl(11, 0.82)) * 4) if ex else 0)

@shot
def s13(t, D, T):    # dato: acero ≈ 8× agua, pero casco con aire pesa menos en promedio
    cam = Cam(540, 960, 1.0)
    dr = D_(cam, bg=(28, 90, 110)); rayos_fondo(dr, 540, 1000, t, (28, 90, 110), (34, 110, 130))
    sw = tl(12, 0.4)
    if t < sw:   # balanza: 1 cubo de acero vs 8 de agua
        tilt = 0.12 * ease(clamp(t / 0.6))
        cx, cy = 540, 820
        dr.rrect(cx - 20, cy, cx + 20, 1380, 6, (200, 170, 90), shade=True)
        dr.rrect(cx - 160, 1360, cx + 160, 1400, 10, (200, 170, 90))
        lx, ly = cx - 360 * math.cos(tilt), cy + 360 * math.sin(tilt)
        rx, ry = cx + 360 * math.cos(tilt), cy - 360 * math.sin(tilt)
        dr.line([(lx, ly), (rx, ry)], (200, 170, 90), 26)
        for px, py in ((lx, ly), (rx, ry)):
            dr.line([(px - 120, py + 220), (px, py), (px + 120, py + 220)], INK, 5)
            dr.chord(px, py + 220, 150, 50, 0, 180, (220, 190, 110))
        dr.rrect(lx - 70, ly + 80, lx + 70, ly + 220, 10, STEEL, shade=True)
        for k in range(8):
            qx = rx - 115 + (k % 4) * 76; qy = ry + 160 - (k // 4) * 70
            dr.rrect(qx - 34, qy - 30, qx + 34, qy + 30, 8, (90, 170, 230))
        f = tinta(dr); img = acabado(f, T); d = ImageDraw.Draw(img)
        d.text((lx, ly + 320), "ACERO", font=font(58), fill=(255, 255, 255), anchor="mm", stroke_width=8, stroke_fill=INK)
        d.text((rx, ry + 320), "AGUA ×8", font=font(58), fill=(150, 220, 255), anchor="mm", stroke_width=8, stroke_fill=INK)
        burst(img, "≈ 8 VECES", 540, 420, 110, t - 0.2, ang=-5)
        return img, 0
    tt = t - sw
    dr.rrect(-600, 1180, 1700, 2600, 0, SEA)
    barco_hueco(dr, 540, 1120, 760, t, corte=True)
    olas(dr, 1180, t)
    f = tinta(dr); img = acabado(f, T); d = ImageDraw.Draw(img)
    k = eob(tt / 0.3)
    d.rounded_rectangle([90, 340, 990, 520], radius=30, fill=(250, 246, 236), outline=INK, width=8)
    d.text((540, 430), "ACERO + AIRE  <  AGUA", font=font(64 * k + 1), fill=INK, anchor="mm")
    if tt > 0.8: check(img, 900, 330, True, 0.8)
    flechas_up(img, [340, 540, 740], 1560, t, col=(120, 230, 140), L=100)
    return img, 0

@shot
def s14(t, D, T):    # Morsa celebra: ¡eres mi nuevo capitán! ¡todos a bordo!
    cam = Cam(540, lerp(1080, 1040, ease(t / D)), lerp(1.2, 1.3, ease(t / D)))
    dr = D_(cam); muelle(dr, t, GY, YS)
    barco_hueco(dr, 300, YS - 50, 560, t)
    morsa(dr, 680, 1880, 0.95, t, mouth=boca(13, t), expr="happy", arm_r=165, arm_l=165, jump=50 * abs(math.sin(t * 5)))
    nico(dr, 280, 1880, 0.62, t, traje="marinero", arms=(20, 150), elbows=(0, 20), expr="happy_eyes", look=(1, 0))
    f = tinta(dr); img = acabado(f, T)
    burst(img, "¡CAPITÁN NICO!", 540, 360, 100, t - tl(13, 0.3), ang=-5)
    return img, 0

@shot
def s15(t, D, T):    # remate: la morsa salta al barco, que se hunde hasta el borde; Tito en una bañera
    ys = 1220
    cam = Cam(540, 1060, 1.1)
    dr = D_(cam); cielo(dr, t, 0.0); nubes(dr, t, 300, 80, n=4)
    mar_fondo(dr, ys, t)
    tj = 0.6
    land = clamp((t - tj) / 0.35)
    dip = 150 * ease(land) + (12 * math.sin(t * 9) * math.exp(-(t - tj - 0.35) * 2) if land >= 1 else 0)
    by = ys - 150 + dip
    tito(dr, 880, ys + 30 + 8 * math.sin(t * 2.4), 0.3, t, expr="cry", wet=True, arm_r=150, arm_l=20)
    banera(dr, 880, ys + 10 + 8 * math.sin(t * 2.4), 0.55, t)
    barco_hueco(dr, 480, by, 760, t, tilt=0.04 * ease(land))
    nico(dr, 300, by + 2, 0.5, t, traje="marinero", arms=(40, 40), elbows=(40, 40), expr="nervous" if boca(14, t) < 0.2 else "worried", mouth=boca(14, t), sweat=True, look=(1, 0))
    my = lerp(300, by + 10, ease(land)) if land < 1 else by + 10
    morsa(dr, 600, my, 0.55, t, expr="happy", arm_r=170, arm_l=170)
    olas(dr, ys, t, amp=10 + 30 * math.exp(-max(0, t - tj - 0.35) * 3) * (land >= 1))
    f = tinta(dr); img = acabado(f, T)
    if land >= 1: burst(img, "¡SPLASH!", 540, 420, 130, t - tj - 0.35, col=(150, 220, 255), ang=-6)
    return img, (10 * math.exp(-(t - tj - 0.35) * 5) if land >= 1 else 0)

@shot
def s16(t, D, T):    # cierre + pregunta
    cam = Cam(540, 1000, 1.0)
    dr = D_(cam); rayos_fondo(dr, 540, 1000, -t, (18, 10, 30), (34, 20, 56))
    o = 1 - ease((t - D + 0.9) / 0.7)
    portal(dr, 540, 1080, 330, t, o)
    if t < D - 1.1:
        nico(dr, 540, 1560, 0.55, t, traje="marinero", arms=(150, 30), elbows=(30, 0), expr="happy")
    f = tinta(dr); add_glow(f, 540, 1080, 450, (150, 120, 255), 0.5 * o)
    img = acabado(f, T)
    d = ImageDraw.Draw(img)
    if t > tl(15, 0.4):
        k = eob((t - tl(15, 0.4)) / 0.3)
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
    wh = bp(400, 3500); low = sosfilt(butter(2, 160, btype="low", fs=sr, output="sos"), noise)
    S_ = STARTS
    def pizz(t0, t1, vol=1.0, mel=None, bass=None, e8=0.17):
        mel = mel or [67, 72, 76, 72, 74, 71, 67, 71, 72, 76, 79, 76, 77, 74, 71, 74]   # aire marinero
        bass = bass or [48, 48, 55, 55, 53, 53, 55, 55]
        k = 0; s = t0
        while s < t1:
            x = seg(e8 * 1.5); m = mel[k % len(mel)]
            pl = np.sin(2 * np.pi * hz(m) * x) * 0.6 + np.sin(2 * np.pi * hz(m) * 2 * x) * 0.2 + np.sin(2 * np.pi * hz(m) * 3 * x) * 0.1
            add(s, vol * 0.05 * pl * np.exp(-x * 12) * (1 - np.exp(-x * 400)))
            if k % 2 == 0:
                xb = seg(e8 * 2); bm = bass[(k // 4) % len(bass)]
                add(s, vol * 0.1 * np.exp(-xb * 6) * np.sin(2 * np.pi * hz(bm) * xb))
            if k % 4 == 0: add(s, vol * 0.12 * np.exp(-x * 25) * np.sin(2 * np.pi * (80 + 50 * np.exp(-x * 25)) * x))
            if k % 4 == 2: add(s, vol * 0.05 * rng.standard_normal(len(x)) * np.exp(-x * 40))
            k += 1; s += e8
    def glu(t0, nb=8, sp=0.13, g=0.12):
        for kk in range(nb):
            x = seg(0.1); add(t0 + kk * sp, g * np.sin(2 * np.pi * (250 + 600 * x / 0.1 + 40 * kk) * x) * np.exp(-x * 25))
    def splash(t0, g=0.6, d=1.2):
        x = seg(d); add(t0, g * bp(300, 5000)[:len(x)] * np.exp(-x * 4)); add(t0, 0.4 * g * low[:len(x)] * np.exp(-x * 5))
    pizz(0, S_[7])
    # gaviota
    x = seg(0.4); add(S_[6] + 0.6, 0.06 * np.sin(2 * np.pi * (1400 - 600 * x) * x) * np.sin(np.pi * x / 0.4))
    # tensión: tambores graves al agua
    for kk in range(int((S_[10] - S_[7]) / 0.45)):
        x = seg(0.3); add(S_[7] + kk * 0.45, 0.13 * np.exp(-x * 10) * np.sin(2 * np.pi * (55 + 3 * (kk % 2)) * x))
    splash(S_[7] + 0.5, 0.7)
    x = seg(1.8); add(S_[7] + tl(7, 0.5), 0.14 * np.sin(2 * np.pi * (300 - 220 * x / 1.8) * x) * np.exp(-x * 0.8))   # tobogán hacia abajo
    glu(S_[7] + tl(7, 0.6), 12)
    glu(S_[8] + 0.1, 5, 0.18, 0.1)
    x = seg(1.4); add(S_[10] + 0.3, 0.16 * np.exp(-x * 1.2) * (np.sin(2 * np.pi * 523 * x) + np.sin(2 * np.pi * 659 * x) + np.sin(2 * np.pi * 784 * x)) / 3)   # ¡flota!
    # Arquímedes: lira + chapoteo en el eureka
    for kk, m in enumerate([62, 66, 69, 74, 69, 66, 62, 69]):
        x = seg(0.6); add(S_[11] + kk * 0.35, 0.06 * np.sin(2 * np.pi * hz(m) * x) * np.exp(-x * 5))
    splash(S_[11] + tl(11, 0.82), 0.5, 0.9)
    x = seg(2.5); add(S_[12], 0.12 * np.exp(-x * 0.8) * (np.sin(2 * np.pi * 220 * x) + np.sin(2 * np.pi * 262 * x) + np.sin(2 * np.pi * 330 * x)) / 3)
    pizz(S_[13], TOTAL, 0.8)
    x = seg(0.6); add(S_[14] + 0.1, 0.12 * np.sin(2 * np.pi * (200 + 500 * x) * x) * np.exp(-x * 3))   # salto de la morsa
    splash(S_[14] + 0.95, 1.0, 1.5)
    x = seg(1.0); add(S_[14] + 1.1, 0.12 * np.sin(2 * np.pi * (300 - 150 * x) * x) * np.exp(-x * 2))   # crujido del barco
    x = seg(1.2); add(S_[1] + 0.1, 0.12 * np.sin(2 * np.pi * (200 + 600 * x) * x) * np.sin(np.pi * x / 1.2))   # portal
    x = seg(0.5); add(S_[1] + 1.3, 0.5 * np.exp(-x * 9) * np.sin(2 * np.pi * (60 + 40 * np.exp(-x * 20)) * x))
    for k in range(1, len(S_) - 1):
        x = seg(0.3); add(S_[k] - 0.08, 0.12 * wh[:len(x)] * np.sin(np.pi * x / 0.3))
    for k in (3, 7, 9):   # tarjetas de paso
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
