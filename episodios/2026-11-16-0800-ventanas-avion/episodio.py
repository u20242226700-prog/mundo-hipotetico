#!/usr/bin/env python3
"""¿Por qué las ventanas de los aviones son redondas? (formato "¿Por qué…?" de días pares)
Estilo vector + cómic (motor/vc.py). Nico con traje de PILOTO (gorro de cuero, gafas con correa turquesa,
chaqueta de aviador y bufanda turquesa). Rival: Bruno (diseñador elegante, ventanas cuadradas, peluca).
Jefa: Doña Rita (dueña de la aerolínea). Dato real: de Havilland Comet, 1954 (grietas de fatiga en esquinas)."""
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
DURS[0] += 0.3; DURS[1] += 1.1; DURS[11] += 0.4; DURS[15] += 1.0
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
    [("¿Por qué las ventanas", []), ("de los aviones", ["aviones"]), ("son REDONDAS…", ["REDONDAS…"]), ("y nunca cuadradas?", ["cuadradas?"])],
    [("Nico cruza el portal", ["portal"]), ("y cae en una fábrica", ["fábrica"]), ("de aviones", ["aviones"])],
    [("¡Ventanas cuadradas", ["cuadradas"]), ("y gigantes!", ["gigantes!"]), ("¡Como en una", []), ("casa de lujo!", ["lujo!"])],
    [("Uno.", ["Uno."]), ("Nico hace algo raro:", ["raro:"]), ("ventanas pequeñitas…", ["pequeñitas…"]), ("y redondas", ["redondas"])],
    [("¿¡Redondas!?", ["¿¡Redondas!?"]), ("¡Parecen las", []), ("de una lavadora!", ["lavadora!"])],
    [("Confíe en mí,", []), ("jefa.", []), ("El peligro está", ["peligro"]), ("en las esquinas", ["esquinas"])],
    [("Nadie le cree…", ["cree…"]), ("y todos los pasajeros", []), ("se van con Bruno", ["Bruno"])],
    [("Dos.", ["Dos."]), ("Allá arriba", ["arriba"]), ("la cabina se infla", ["infla"]), ("como un globo…", ["globo…"]), ("y al aterrizar", []), ("se desinfla.", ["desinfla."]), ("Una y otra vez", ["vez"])],
    [("¿Qué fue", []), ("ese ruidito?", ["ruidito?"]), ("¿Crac?", ["¿Crac?"])],
    [("Tres.", ["Tres."]), ("En una esquina", ["esquina"]), ("toda la fuerza", ["fuerza"]), ("se amontona en un punto", ["punto"]), ("y el metal se agrieta.", ["agrieta."]), ("En una curva,", ["curva,"]), ("se reparte", ["reparte"])],
    [("¡Lo redondo", ["redondo"]), ("no tiene", []), ("un punto débil", ["débil"]), ("por donde romperse!", ["romperse!"])],
    [("En la prueba", []), ("de presión…", ["presión…"]), ("¡PUM!", ["¡PUM!"]), ("La ventana de Bruno", []), ("sale volando…", ["volando…"]), ("y su peluca también", ["peluca"])],
    [("Esto pasó de verdad:", ["verdad:"]), ("en 1954", ["1954"]), ("el Comet,", ["Comet,"]), ("el primer jet", ["jet"]), ("de pasajeros,", []), ("tuvo accidentes", []), ("por grietas que nacían", ["grietas"]), ("en esquinas de su fuselaje", ["esquinas"])],
    [("Lo probaron", []), ("dentro de una", []), ("piscina gigante.", ["piscina"]), ("Desde entonces,", []), ("las ventanas de avión", []), ("son redondeadas", ["redondeadas"])],
    [("¡Nico!", ["¡Nico!"]), ("¡Quiero ventanas redondas…", ["redondas…"]), ("hasta en mi oficina!", ["oficina!"])],
    [("Nos vemos en otro", []), ("mundo hipotético", ["hipotético"]), ("¿Qué otro secreto", ["secreto"]), ("de ingeniería quieres ver?", ["ingeniería"]), ("¡Comenta!", ["¡Comenta!"])],
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
        dr.line([(x, y_floor), (x, -200), (x + 150, -600)], (70, 80, 104), 26, nolin=True)
    for k in range(-3, 7):   # ventanales altos
        dr.rrect(-200 + k * 300, -300, -60 + k * 300, 300, 10, (170, 210, 236), nolin=True)
        dr.rrect(-200 + k * 300, -10, -60 + k * 300, 6, 2, (120, 140, 170), nolin=True)
    dr.rrect(-1200, y_floor, 2400, 3400, 0, (176, 178, 186))
    for k in range(-6, 14): dr.rrect(k * 220, y_floor + 160, k * 220 + 120, y_floor + 186, 4, (240, 200, 50), nolin=True)
    dr.rrect(-1200, y_floor - 8, 2400, y_floor + 8, 0, (60, 64, 80))

def pista(dr, t, gy=1500):
    dr.rrect(-1200, gy, 2400, 3400, 0, (110, 170, 90))
    dr.rrect(-1200, gy + 40, 2400, gy + 360, 0, (70, 72, 84))
    for k in range(-6, 14): dr.rrect(k * 260 - (t * 200) % 260, gy + 190, k * 260 + 130 - (t * 200) % 260, gy + 210, 3, (250, 250, 250), nolin=True)
    dr.rrect(1300, gy - 600, 1500, gy, 0, (210, 214, 224), shade=True)   # torre de control
    dr.rrect(1250, gy - 760, 1550, gy - 600, 20, (120, 190, 220))

def avion(dr, x, y, L, t, win="round", col=(240, 242, 248), stripe=TURQ, infl=0.0, crack=0.0, hole=-1, face=1,
          nwin=7, gear=True, heads=False, cola=(40, 120, 200), crack_win=None):
    """Avión de perfil. (x, y) = centro del fuselaje, L = largo. win: 'round' | 'square' | 'comet'."""
    H = L * 0.17 * (1 + infl)
    xn, xt = x + face * L / 2, x - face * L / 2
    sh = mix(col, (20, 20, 40), 0.25)
    # ala del fondo
    dr.poly([(x - face * L * 0.02, y + H * 0.1), (x + face * L * 0.08, y + H * 0.1), (x - face * L * 0.12, y - H * 0.75), (x - face * L * 0.18, y - H * 0.75)], sh)
    # cola
    dr.poly([(xt + face * L * 0.04, y - H * 0.35), (xt + face * L * 0.2, y - H * 0.45), (xt + face * L * 0.03, y - H * 1.75), (xt - face * L * 0.05, y - H * 1.75)], cola)
    dr.poly([(xt + face * L * 0.0, y - H * 1.2), (xt + face * L * 0.08, y - H * 1.2), (xt + face * L * 0.05, y - H * 1.45), (xt - face * L * 0.02, y - H * 1.45)], stripe, nolin=True)
    dr.poly([(xt - face * L * 0.02, y - H * 0.1), (xt + face * L * 0.12, y - H * 0.1), (xt + face * L * 0.0, y - H * 0.55), (xt - face * L * 0.08, y - H * 0.55)], sh)
    # fuselaje
    dr.rrect(x - L / 2, y - H / 2, x + L / 2, y + H / 2, H / 2, col, shade=True)
    dr.ell(xn - face * H * 0.2, y + H * 0.04, H * 0.7, H * 0.48, col)
    dr.rrect(x - L * 0.45, y + H * 0.1, x + L * 0.45, y + H * 0.2, H * 0.04, stripe, nolin=True)
    # cabina de pilotos
    cx = xn - face * H * 0.42
    dr.poly([(cx - face * H * 0.1, y - H * 0.2), (cx + face * H * 0.25, y - H * 0.2), (cx + face * H * 0.38, y - H * 0.04), (cx - face * H * 0.1, y - H * 0.04)], (50, 60, 90))
    # ventanas
    wins = []
    x0, x1 = x - face * L * 0.32, x + face * L * 0.26
    for k in range(nwin):
        wx = lerp(x0, x1, k / max(1, nwin - 1)); wy = y - H * 0.12
        wins.append((wx, wy))
        g = (30, 24, 40) if k == hole else GLASS
        if win == "round":
            r = H * 0.12
            dr.ell(wx, wy, r * 0.8, r, g)
            if heads and k != hole and k % 2 == 0: dr.ell(wx, wy + r * 0.3, r * 0.45, r * 0.5, (236, 190, 150), nolin=True)
        else:
            ww, hh = (H * 0.38, H * 0.32) if win == "square" else (H * 0.24, H * 0.22)
            dr.rrect(wx - ww / 2, wy - hh / 2, wx + ww / 2, wy + hh / 2, H * (0.01 if win == "square" else 0.02), g)
            if heads and k != hole and k % 2 == 0: dr.ell(wx, wy + hh * 0.2, hh * 0.3, hh * 0.35, (236, 190, 150), nolin=True)
    if crack > 0:
        idx = range(nwin) if crack_win is None else [crack_win]
        for k in idx:
            wx, wy = wins[k]
            ww, hh = (H * 0.38, H * 0.32) if win == "square" else (H * 0.24, H * 0.22)
            for sx, sy in ((1, -1), (-1, 1)):
                px, py = wx + sx * ww / 2, wy + sy * hh / 2
                pts = [(px, py)]
                for j in range(1, 5):
                    f = j / 4 * crack
                    pts.append((px + sx * H * 0.22 * f + (j % 2) * H * 0.03 * sx, py + sy * H * 0.18 * f - (j % 2) * H * 0.03))
                dr.line(pts, INK, max(3, H * 0.018))
    # ala delantera + motor
    dr.poly([(x - face * L * 0.04, y + H * 0.2), (x + face * L * 0.1, y + H * 0.2), (x - face * L * 0.14, y + H * 1.0), (x - face * L * 0.22, y + H * 1.0)], mix(col, (20, 20, 40), 0.12), shade=True)
    if win != "comet":
        ex = x - face * L * 0.05
        dr.rrect(ex - L * 0.07, y + H * 0.42, ex + L * 0.07, y + H * 0.74, H * 0.16, (200, 204, 214), shade=True)
        dr.ell(ex + face * L * 0.07, y + H * 0.58, H * 0.07, H * 0.15, (60, 64, 80))
    if gear:
        for gx in (x - face * L * 0.08, xn - face * L * 0.1):
            dr.line([(gx, y + H * 0.4), (gx, y + H * 0.85)], (90, 90, 100), H * 0.05)
            dr.ell(gx, y + H * 0.9, H * 0.1, H * 0.1, (30, 30, 36))
    return wins, H

# ------------------------------------------------------------ personajes nuevos
def bruno(dr, x, y, s, t, mouth=0.0, expr="smug", arm_r=20, arm_l=20, wig=(0, 0), wig_on=True, sweat=False, look=(0, 0), lean=0.0):
    """(x, y) = pies. Diseñador elegante: traje morado, gafas de sol, peluca copete naranja. Altura ≈ 900*s.
    wig = desplazamiento de la peluca (para que salga volando); wig_on=False → calvo."""
    S = lambda v: v * s
    bob = S(5) * math.sin(t * 2.3)
    suit = (112, 58, 168); skin = (236, 192, 156)
    for sx in (-1, 1):
        dr.rrect(x + sx * S(36) - S(18), y - S(330), x + sx * S(36) + S(18), y - S(10), S(10), (60, 34, 96))
        dr.poly([(x + sx * S(36) - S(24), y - S(4)), (x + sx * S(36) + sx * S(70), y - S(4)), (x + sx * S(36) + S(20), y - S(34))], (250, 250, 250))
    tx = x + lean * S(80)
    dr.rrect(tx - S(95), y - S(650) + bob, tx + S(95), y - S(300), S(46), suit, shade=True)
    dr.poly([(tx - S(36), y - S(650) + bob), (tx + S(36), y - S(650) + bob), (tx, y - S(520) + bob)], (250, 170, 200))
    dr.poly([(tx - S(40), y - S(640) + bob), (tx, y - S(600) + bob), (tx + S(40), y - S(640) + bob), (tx, y - S(560) + bob)], (250, 210, 60))   # pajarita dorada
    dr.ell(tx - S(55), y - S(560) + bob, S(18), S(12), (250, 120, 160))   # pañuelo
    hands = []
    for sx, ang in ((-1, arm_l), (1, arm_r)):
        shx, shy = tx + sx * S(88), y - S(615) + bob
        a = math.radians(ang)
        hx, hy = shx + sx * math.sin(a) * S(230), shy + math.cos(a) * S(230)
        dr.line([(shx, shy), (hx, hy)], suit, S(48))
        dr.ell(hx, hy, S(28), S(28), (250, 250, 250))
        hands.append((hx, hy))
    hx, hy = tx + lean * S(140), y - S(810) + bob
    dr.ell(hx, hy, S(130), S(160), skin, shade=True)
    for sx in (-1, 1): dr.ell(hx + sx * S(128), hy + S(10), S(22), S(34), skin)
    # gafas de sol
    if expr == "shock":
        for sx in (-1, 1):
            dr.ell(hx + sx * S(52), hy - S(20), S(36), S(40), (255, 255, 255)); dr.ell(hx + sx * S(52) + look[0] * S(8), hy - S(18), S(13), S(15), INK)
        dr.rrect(hx - S(120), hy - S(130), hx + S(120), hy - S(100), S(10), (24, 22, 30))   # gafas subidas a la frente
    else:
        for sx in (-1, 1): dr.rrect(hx + sx * S(52) - S(48), hy - S(52), hx + sx * S(52) + S(48), hy + S(10), S(20), (24, 22, 30))
        dr.line([(hx - S(10), hy - S(30)), (hx + S(10), hy - S(30))], (24, 22, 30), S(10))
        dr.ell(hx - S(70), hy - S(36), S(14), S(8), (255, 255, 255), nolin=True)
    tilt = {"angry": 16, "smug": -14, "shock": -18, "worried": -20}.get(expr, -6)
    for sx in (-1, 1):
        ex = hx + sx * S(52)
        dr.line([(ex - S(34), hy - S(70) + sx * S(tilt) * 0.5), (ex + S(34), hy - S(70) - sx * S(tilt) * 0.5)], (60, 40, 30), S(12))
    dr.ell(hx, hy + S(35), S(24), S(30), mix(skin, (200, 110, 100), 0.35))
    dr.line([(hx - S(60), hy + S(66)), (hx - S(10), hy + S(58)), (hx + S(10), hy + S(58)), (hx + S(60), hy + S(66))], (60, 40, 30), S(9))   # bigotito
    mo = clamp(mouth)
    if mo > 0.06 or expr == "shock":
        mo = max(mo, 0.6 if expr == "shock" else 0)
        dr.ell(hx, hy + S(108), S(40), S(10 + 32 * mo), (100, 24, 34))
    elif expr == "worried":
        dr.line([(hx - S(40), hy + S(112)), (hx - S(14), hy + S(104)), (hx + S(14), hy + S(112)), (hx + S(40), hy + S(104))], (100, 24, 34), S(9))
    else:
        dr.line([(hx - S(44), hy + S(100)), (hx, hy + S(110)), (hx + S(46), hy + S(92))], (100, 24, 34), S(10))
    if wig_on:   # peluca copete
        wx, wy = hx + wig[0], hy + wig[1]
        dr.ell(wx, wy - S(130), S(140), S(60), (236, 160, 50))
        for k in range(4): dr.ell(wx - S(90) + k * S(70), wy - S(175) - S(20) * (k % 2), S(70), S(55), (246, 180, 60))
        dr.ell(wx + S(80), wy - S(210), S(90), S(50), (250, 196, 80))
    else:
        dr.ell(hx - S(40), hy - S(120), S(36), S(18), (255, 240, 220), nolin=True)   # brillo de la calva
    if sweat:
        k = (t * 1.3) % 1
        dr.ell(hx + S(150), hy - S(40) + S(60) * k, S(14), S(20), (140, 210, 255))
    return dict(hands=hands, head=(hx, hy))

def rita(dr, x, y, s, t, mouth=0.0, expr="angry", arm_r=20, arm_l=20, red=0.0, look=(0, 0), jump=0.0):
    """(x, y) = pies. Doña Rita, dueña de la aerolínea: blazer rojo, moño gris enorme, gafas de ojo de gato, perlas. Altura ≈ 820*s."""
    S = lambda v: v * s
    y = y - S(jump)
    bob = S(5) * math.sin(t * 2.6 + 1)
    skin = mix((240, 200, 170), (226, 80, 80), red)
    for sx in (-1, 1):
        dr.rrect(x + sx * S(40) - S(18), y - S(170), x + sx * S(40) + S(18), y - S(14), S(10), skin)
        dr.ell(x + sx * S(46), y - S(12), S(34), S(14), (170, 30, 40))
    dr.poly([(x - S(150), y - S(170)), (x + S(150), y - S(170)), (x + S(120), y - S(330)), (x - S(120), y - S(330))], (40, 40, 60))   # falda
    dr.rrect(x - S(140), y - S(540) + bob, x + S(140), y - S(300), S(60), (206, 46, 58), shade=True)
    dr.poly([(x - S(50), y - S(540) + bob), (x + S(50), y - S(540) + bob), (x, y - S(440) + bob)], (250, 250, 250))
    for k in range(7):   # perlas
        a = math.pi * (0.15 + 0.7 * k / 6)
        dr.ell(x + math.cos(a) * S(60), y - S(540) + bob + math.sin(a) * S(50), S(11), S(11), (250, 246, 236))
    dr.ell(x + S(80), y - S(470) + bob, S(18), S(18), (250, 210, 60))   # broche de alas
    hands = []
    for sx, ang in ((-1, arm_l), (1, arm_r)):
        shx, shy = x + sx * S(120), y - S(500) + bob
        a = math.radians(ang)
        hx, hy = shx + sx * math.sin(a) * S(180), shy + math.cos(a) * S(180)
        dr.line([(shx, shy), (hx, hy)], (206, 46, 58), S(46))
        dr.ell(hx, hy, S(28), S(28), skin)
        hands.append((hx, hy))
    hx, hy = x, y - S(690) + bob
    dr.ell(hx, hy - S(200), S(120), S(95), (200, 200, 212), shade=True)   # moño
    dr.ell(hx, hy - S(60), S(150), S(110), (200, 200, 212))
    dr.ell(hx, hy, S(130), S(140), skin, shade=True)
    for sx in (-1, 1):
        ex, ey = hx + sx * S(50), hy - S(5)
        if expr == "happy_eyes":
            dr.chord(ex, ey + S(5), S(28), S(22), 180, 360, INK); dr.chord(ex, ey + S(11), S(24), S(16), 180, 360, skin)
        else:
            dr.ell(ex, ey, S(26), S(30), (255, 255, 255))
            dr.ell(ex + look[0] * S(8), ey + look[1] * S(8), S(12), S(14), INK)

        X, Y = dr.cam.p(ex, ey); rx, ry = dr.cam.s(S(40)), dr.cam.s(S(36))
        dr.d.ellipse([X - rx, Y - ry, X + rx, Y + ry], outline=(220, 40, 70), width=max(3, int(dr.cam.s(S(10)))))
        dr.dn.ellipse([X - rx, Y - ry, X + rx, Y + ry], outline=255, width=max(3, int(dr.cam.s(S(10)))) + 3)
        dr.poly([(ex + sx * S(30), ey - S(26)), (ex + sx * S(66), ey - S(56)), (ex + sx * S(42), ey - S(10))], (220, 40, 70))
    tilt = {"angry": 22, "happy": -6, "happy_eyes": -8}.get(expr, 0)
    for sx in (-1, 1):
        ex = hx + sx * S(50)
        dr.line([(ex - S(28), hy - S(62) - sx * S(tilt) * 0.5), (ex + S(28), hy - S(62) + sx * S(tilt) * 0.5)], (120, 120, 130), S(10))
    for sx in (-1, 1): dr.ell(hx + sx * S(80), hy + S(50), S(22), S(13), (240, 140, 150))
    mo = clamp(mouth)
    if mo > 0.06: dr.ell(hx, hy + S(80), S(38), S(10 + 30 * mo), (180, 30, 50))
    elif expr == "angry": dr.chord(hx, hy + S(98), S(36), S(22), 180, 360, (180, 30, 50))
    else: dr.chord(hx, hy + S(58), S(40), S(34), 0, 180, (180, 30, 50))
    return dict(hands=hands, head=(hx, hy))

def lavadora(img, x, y, sz, t):
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([x - sz, y - sz * 1.15, x + sz, y + sz * 1.05], radius=int(sz * 0.15), fill=(246, 246, 250), outline=INK, width=8)
    d.rectangle([x - sz + 10, y - sz * 1.15 + 10, x + sz - 10, y - sz * 0.75], fill=(210, 214, 226), outline=INK, width=5)
    d.ellipse([x - sz * 0.65, y - sz * 0.6, x + sz * 0.65, y + sz * 0.7], fill=(90, 96, 110), outline=INK, width=8)
    d.ellipse([x - sz * 0.5, y - sz * 0.45, x + sz * 0.5, y + sz * 0.55], fill=(110, 180, 230), outline=INK, width=5)
    a = t * 6
    for k in range(3):
        d.ellipse([x + math.cos(a + k * 2.1) * sz * 0.25 - 16, y + 0.05 * sz + math.sin(a + k * 2.1) * sz * 0.25 - 16, x + math.cos(a + k * 2.1) * sz * 0.25 + 16, y + 0.05 * sz + math.sin(a + k * 2.1) * sz * 0.25 + 16], fill=(250, 250, 255))

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

# ------------------------------------------------------------ planos
SHOTS = []
def shot(fn): SHOTS.append(fn); return fn
def tl(k, frac): return LEAD + len(VOZ[k]) / SR * frac
def D_(cam, bg=(0, 0, 0)): return D(cam, bg)
GY = 1500
PAS = [(220, 80, 80), (80, 120, 210), (240, 180, 60), (120, 180, 100), (180, 100, 200)]

@shot
def s01(t, D, T):    # gancho: avión volando, zoom a la ventana redonda con Nico saludando
    u = ease(t / D)
    cam = Cam(lerp(540, 690, u), lerp(960, 900, u), lerp(1.0, 2.1, u))
    dr = D_(cam); cielo(dr, t, 0.2); nubes(dr, t, 1400, 500, layer=0, col=(236, 240, 248))
    wins, H = avion(dr, 540, 960 + 12 * math.sin(t * 2), 1500, t, win="round", gear=False, heads=True)
    wx, wy = wins[4]
    dr.ell(wx, wy, H * 0.096, H * 0.12, (150, 200, 236))
    nico(dr, wx, wy + H * 0.14, H * 0.00028, t, traje="piloto", arms=(20, 160), elbows=(0, 30 + 25 * math.sin(t * 12)), expr="happy")
    nubes(dr, t, 300, 900, n=4, layer=1, sz=1.4)
    f = tinta(dr); img = acabado(f, T)
    burst(img, "¿POR QUÉ?", 540, 380, 150, t - 0.1, ang=-6)
    if t > tl(0, 0.7):
        k = eob((t - tl(0, 0.7)) / 0.25); d = ImageDraw.Draw(img)
        d.rounded_rectangle([700 - 90 * k, 560 - 80 * k, 700 + 90 * k, 560 + 80 * k], radius=4, fill=GLASS, outline=INK, width=10)
        check(img, 790, 470, False, 0.7 * k + 0.01)
    return img, 0

@shot
def s02(t, D, T):    # portal → Nico piloto cae en la fábrica de aviones
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
    dr = D_(cam); hangar(dr, t)
    avion(dr, 240, 1180, 1100, t, win="square", col=(250, 240, 250), stripe=(150, 80, 200), cola=(112, 58, 168), face=-1)
    avion(dr, 900, 1250, 900, t, win="round", col=(236, 240, 246), cola=(40, 120, 200))
    for k in range(4): persona(dr, -40 + k * 330, 1900 + (k % 2) * 30, 0.4, t, PAS[k], ph=k)
    portal(dr, 540, 1150, 220, t, 1 - ease((tt - 0.7) / 0.4))
    land = clamp(tt / 0.35)
    sq = 1 - 0.3 * math.exp(-tt * 7) * math.cos(tt * 20) if land >= 1 else 1.15
    nico(dr, 540, lerp(1050, 1800, land ** 2), 0.66, t, traje="piloto", arms=(140, 140) if land < 1 else (30, 165), elbows=(0, 15), expr="shock" if tt < 0.9 else "happy", squash=sq, look=(0.3, -0.6))
    f = tinta(dr)
    if tt < 0.2: f += 255 * (1 - tt / 0.2)
    img = acabado(f, T)
    if tt > 0.5: cartel(img, tt - 0.5, "FÁBRICA DE AVIONES", "¡DISEÑA EL AVIÓN DEL FUTURO!", y=300)
    return img, 0

@shot
def s03(t, D, T):    # Bruno presume ventanas cuadradas gigantes
    cam = Cam(lerp(560, 520, ease(t / D)), 1080, lerp(1.25, 1.35, ease(t / D)))
    dr = D_(cam); hangar(dr, t)
    avion(dr, 820, 1050, 1300, t, win="square", col=(250, 240, 250), stripe=(150, 80, 200), cola=(112, 58, 168), face=-1, nwin=6)
    bruno(dr, 430, 1900, 1.0, t, expr="smug" if boca(2, t) < 0.3 else "happy", arm_r=150 + 15 * math.sin(t * 5), arm_l=60, mouth=boca(2, t))
    f = tinta(dr); img = acabado(f, T)
    nombre(img, t - 0.1, "BRUNO", "el diseñador elegante", col=(112, 58, 168))
    if t > tl(2, 0.55): burst(img, "¡LUJO!", 800, 760, 130, t - tl(2, 0.55), col=(250, 200, 240), ang=8)
    return img, 0

@shot
def s04(t, D, T):    # PASO 1: Nico pone ventanitas redondas
    u = ease(t / D)
    cam = Cam(560, lerp(1060, 1100, u), lerp(1.15, 1.25, u))
    dr = D_(cam); hangar(dr, t)
    wins, H = avion(dr, 700, 1000, 1200, t, win="round", nwin=7)
    # escalera
    dr.rrect(300, 1060, 330, 1520, 4, (240, 190, 50)); dr.rrect(470, 1060, 500, 1520, 4, (240, 190, 50))
    for k in range(6): dr.rrect(300, 1100 + k * 75, 500, 1116 + k * 75, 4, (240, 190, 50))
    put = clamp((t - 1.0) / 0.6)
    tgt = wins[1]
    hx, hy = lerp(560, tgt[0], ease(put)), lerp(780, tgt[1], ease(put))
    info = nico(dr, 400, 1080, 0.62, t, traje="piloto", arms=(30, 150), elbows=(0, 10), expr="happy", look=(0.8, -0.5))
    if put < 1:
        rx, ry = H * 0.096, H * 0.12
        dr.ell(info["hands"][1][0] + 30, info["hands"][1][1] - 40, rx * 1.4, ry * 1.4, (220, 224, 232))
        dr.ell(info["hands"][1][0] + 30, info["hands"][1][1] - 40, rx, ry, GLASS)
    f = tinta(dr); img = acabado(f, T)
    tarjeta_paso(img, t, 1, "EL “ERROR”")
    if put >= 1: burst(img, "¡CLIC!", 780, 820, 100, t - 1.6, col=(255, 255, 255), ang=8)
    return img, 0

@shot
def s05(t, D, T):    # Doña Rita furiosa: ¡parecen de lavadora!
    cam = Cam(540, 1060, lerp(1.5, 1.62, ease(t / D)))
    dr = D_(cam); hangar(dr, t)
    avion(dr, 900, 900, 1100, t, win="round", nwin=7)
    rita(dr, 470, 1930, 1.2, t, mouth=boca(4, t), expr="angry", arm_r=150 + 12 * math.sin(t * 9), arm_l=40, red=clamp(t / 1.0) * 0.8)
    f = tinta(dr); img = acabado(f, T)
    burst(img, "¿¡REDONDAS!?", 540, 360, 120, t - 0.05, col=(255, 90, 70), ang=-6)
    nombre(img, t - 0.15, "DOÑA RITA", "dueña de la aerolínea", y=470, col=(206, 46, 58))
    if t > tl(4, 0.5):
        k = eob((t - tl(4, 0.5)) / 0.3)
        lavadora(img, 830, 860, 130 * k + 1, t)
    return img, 2 * math.sin(t * 40)

@shot
def s06(t, D, T):    # Nico: confíe en mí, el peligro está en las esquinas
    cam = Cam(540, 1080, 1.7)
    dr = D_(cam); hangar(dr, t)
    avion(dr, 260, 920, 1100, t, win="round", nwin=7)
    nico(dr, 560, 1700, 0.72, t, traje="piloto", arms=(25, 120), elbows=(0, 60), expr="smug" if boca(5, t) < 0.2 else "happy", mouth=boca(5, t), look=(-0.4, 0))
    f = tinta(dr); img = acabado(f, T)
    if t > tl(5, 0.45):
        k = eob((t - tl(5, 0.45)) / 0.3); d = ImageDraw.Draw(img)
        cx, cy, r = 800, 560, 120 * k + 1
        d.rectangle([cx - r, cy - r * 0.85, cx + r, cy + r * 0.85], fill=GLASS, outline=INK, width=10)
        for sx, sy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
            pr = 34 + 10 * math.sin(t * 10)
            d.ellipse([cx + sx * r - pr, cy + sy * r * 0.85 - pr, cx + sx * r + pr, cy + sy * r * 0.85 + pr], outline=(240, 50, 50), width=9)
        burst(img, "¡PELIGRO!", 800, 760, 70, t - tl(5, 0.45), col=(255, 90, 70), ang=6)
    return img, 0

@shot
def s07(t, D, T):    # todos se suben al avión de Bruno; en el de Nico, solo una paloma
    u = ease(t / D)
    cam = Cam(lerp(420, 640, u), 1150, 1.0)
    dr = D_(cam); cielo(dr, t); pista(dr, t * 0, GY)
    avion(dr, 900, 1150, 1000, t, win="square", col=(250, 240, 250), stripe=(150, 80, 200), cola=(112, 58, 168), face=-1, nwin=6, heads=u > 0.6)
    wins, H = avion(dr, 60, 1250, 700, t, win="round", nwin=7)
    dr.ell(wins[3][0], wins[3][1] + 4, 12, 14, (150, 150, 160))   # paloma en la ventana
    dr.poly([(wins[3][0] + 8, wins[3][1]), (wins[3][0] + 22, wins[3][1] + 4), (wins[3][0] + 8, wins[3][1] + 8)], (240, 180, 50))
    nico(dr, 260, 1790, 0.5, t, traje="piloto", arms=(10, 10), expr="worried", look=(1, 0))
    bruno(dr, 1000, 1790, 0.55, t, expr="smug", arm_r=160, arm_l=30)
    for k in range(6):
        persona(dr, 420 + k * 110 + u * 300, 1840 + (k % 2) * 30, 0.36, t, PAS[k % 5], ph=k, run=u < 0.85)
    f = tinta(dr); img = acabado(f, T)
    if t > tl(6, 0.6): burst(img, "¡TODOS CON BRUNO!", 640, 420, 84, t - tl(6, 0.6), col=(250, 200, 240), ang=-5)
    return img, 0

@shot
def s08(t, D, T):    # PASO 2: la cabina se infla como un globo, vuelo tras vuelo
    cam = Cam(540, 1000, 1.0)
    dr = D_(cam); cielo(dr, t, 0.9); nubes(dr, t, 1700, 400, layer=0, col=(200, 214, 236))
    ph = t * 3.2
    infl = 0.09 * (0.5 + 0.5 * math.sin(ph))
    wins, H = avion(dr, 540, 1000, 1150, t, win="square", col=(250, 240, 250), stripe=(150, 80, 200), cola=(112, 58, 168), face=1, nwin=6, gear=False, heads=True, infl=infl)
    f = tinta(dr); img = acabado(f, T)
    d = ImageDraw.Draw(img)
    a = 0.5 + 0.5 * math.sin(ph)
    for k in range(7):   # flechas de presión hacia afuera
        x = 240 + k * 100
        for sgn in (-1, 1):
            y0 = 1000 + sgn * (H / 2 + 20); y1 = y0 + sgn * (40 + 50 * a)
            d.line([(x, y0), (x, y1)], fill=INK, width=20); d.line([(x, y0), (x, y1)], fill=(255, 120, 90), width=10)
            d.polygon([(x - 22, y1), (x + 22, y1), (x, y1 + sgn * 30)], fill=(255, 120, 90), outline=INK)
    tarjeta_paso(img, t, 2, "LA PRESIÓN")
    if t > 1.4:
        d.rounded_rectangle([90, 1220, 520, 1340], radius=20, fill=(30, 30, 46), outline=(250, 200, 60), width=8)
        d.text((305, 1280), "10.000 m", font=font(64), fill=(250, 220, 60), anchor="mm")
        n = 1 + int(max(0, t - 1.4) * 9)
        d.rounded_rectangle([560, 1220, 990, 1340], radius=20, fill=(250, 250, 246), outline=INK, width=8)
        d.text((775, 1280), f"VUELO Nº {n}", font=font(56), fill=INK, anchor="mm")
    if t > tl(7, 0.3): burst(img, "¡SE INFLA!", 540, 700, 90 + 20 * a, t - tl(7, 0.3), col=(255, 200, 80), ang=-5)
    return img, 0

@shot
def s09(t, D, T):    # Bruno dentro de su avión: ¿crac?
    cam = Cam(540, 1060, 1.0)
    dr = D_(cam, bg=(230, 220, 200))
    dr.rrect(-600, -400, 1700, 2600, 0, (232, 222, 204))
    dr.rrect(-600, 1500, 1700, 2600, 0, (110, 90, 120))
    wx, wy, ww, hh = 300, 760, 420, 380
    dr.rrect(wx - ww / 2 - 30, wy - hh / 2 - 30, wx + ww / 2 + 30, wy + hh / 2 + 30, 10, (210, 200, 186), shade=True)
    dr.rrect(wx - ww / 2, wy - hh / 2, wx + ww / 2, wy + hh / 2, 4, (110, 160, 220))
    for j in range(3): dr.ell(wx - 120 + j * 110 - (t * 200) % 300, wy + 80, 90, 40, (240, 244, 250), nolin=True)
    cr = clamp((t - tl(8, 0.55)) / 0.4)
    if cr > 0:
        px, py = wx + ww / 2, wy - hh / 2
        dr.line([(px, py), (px + 50 * cr, py - 30 * cr), (px + 70 * cr, py - 80 * cr), (px + 120 * cr, py - 100 * cr)], INK, 7)
    dr.rrect(500, 1150, 1020, 1700, 60, (60, 110, 180), shade=True)   # asiento
    bruno(dr, 700, 2150, 1.05, t, expr="worried" if cr <= 0 else "shock", arm_r=40, arm_l=150 + 8 * math.sin(t * 8), mouth=boca(8, t), sweat=True, look=(-1, -0.4))
    f = tinta(dr); img = acabado(f, T)
    if cr > 0: burst(img, "¿CRAC?", 760, 420, 130, t - tl(8, 0.55), col=(255, 255, 255), ang=8)
    return img, (4 * math.sin(t * 50) if 0 < cr < 1 else 0)

@shot
def s10(t, D, T):    # PASO 3: esquina = la fuerza se amontona · curva = se reparte
    cam = Cam(540, 960, 1.0)
    dr = D_(cam, bg=(40, 44, 60))
    dr.rrect(-600, -400, 1700, 2600, 0, (44, 48, 66))
    for px in (300, 780):
        dr.rrect(px - 230, 640, px + 230, 1340, 20, (170, 176, 190), shade=True)
        for k in range(6): dr.ell(px - 200 + k * 80, 660, 7, 7, (120, 124, 140), nolin=True)
    sq = (300, 990, 120, 110)
    dr.rrect(sq[0] - sq[2], sq[1] - sq[3], sq[0] + sq[2], sq[1] + sq[3], 2, GLASS)
    dr.ell(780, 990, 115, 125, GLASS)
    cr = clamp((t - tl(9, 0.45)) / 1.2)
    if cr > 0:
        x0, y0 = sq[0] + sq[2], sq[1] - sq[3]
        dr.line([(x0, y0), (x0 + 30 * cr, y0 - 40 * cr), (x0 + 60 * cr, y0 - 50 * cr), (x0 + 80 * cr, y0 - 110 * cr), (x0 + 105 * cr, y0 - 150 * cr)], INK, 8)
    f = tinta(dr)
    pul = 0.5 + 0.5 * math.sin(t * 6)
    for sx, sy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        add_glow(f, sq[0] + sx * sq[2], sq[1] + sy * sq[3], 70 + 20 * pul, (255, 60, 40), 0.75)
    add_glow(f, 780, 990, 190, (80, 200, 255), 0.18)
    img = acabado(f, T); d = ImageDraw.Draw(img)
    for k in range(9):   # líneas de fuerza
        yy = 700 + k * 72
        for px, curva in ((300, False), (780, True)):
            pts = []
            for j in range(21):
                xx = px - 220 + j * 22
                dy = yy - 990
                if curva:
                    g = math.exp(-((xx - px) / 150) ** 2)
                    yv = yy + (math.copysign(1, dy) if dy else 1) * 120 * g * math.exp(-(dy / 220) ** 2)
                else:
                    near = abs(xx - px) < 135
                    yv = yy + ((math.copysign(1, dy) if dy else 1) * max(0, 125 - abs(dy)) if near else 0)
                pts.append((xx, yv))
            d.line(pts, fill=(255, 110, 80) if not curva else (120, 220, 255), width=4)
    tarjeta_paso(img, t, 3, "LAS ESQUINAS")
    if t > 1.5:
        d.rounded_rectangle([70, 1380, 530, 1470], radius=16, fill=(230, 60, 60), outline=INK, width=6)
        d.text((300, 1425), "PUNTO DÉBIL", font=font(48), fill=(255, 255, 255), anchor="mm")
    if t > tl(9, 0.75):
        d.rounded_rectangle([550, 1380, 1010, 1470], radius=16, fill=(80, 190, 110), outline=INK, width=6)
        d.text((780, 1425), "SE REPARTE", font=font(48), fill=(255, 255, 255), anchor="mm")
    return img, 0

@shot
def s11(t, D, T):    # Nico explica junto a una ventana redonda gigante
    cam = Cam(540, 1060, 1.3)
    dr = D_(cam); hangar(dr, t)
    dr.ell(760, 720, 330, 370, (220, 224, 234), shade=True)
    dr.ell(760, 720, 250, 290, GLASS)
    nubes(dr, t, 760, 200, n=3, sz=0.6, layer=1)
    for k in range(16):   # fuerza repartida alrededor
        a = k * math.pi / 8 + t * 1.5
        dr.line([(760 + math.cos(a) * 340, 720 + math.sin(a) * 380), (760 + math.cos(a) * 400, 720 + math.sin(a) * 450)], (120, 220, 255), 10, nolin=True)
    nico(dr, 330, 1700, 0.8, t, traje="piloto", arms=(70 + 25 * math.sin(t * 5), 150), elbows=(30, 10), expr="happy", mouth=boca(10, t), look=(0.8, -0.3))
    f = tinta(dr); img = acabado(f, T)
    burst(img, "¡SIN PUNTO DÉBIL!", 600, 300, 86, t - tl(10, 0.5), col=(120, 240, 140), ang=-5)
    return img, 0

@shot
def s12(t, D, T):    # prueba de presión: ¡PUM! sale la ventana y la peluca de Bruno
    tp = tl(11, 0.3)
    cam = Cam(540, 1080, lerp(1.0, 1.12, ease(t / D)))
    dr = D_(cam); hangar(dr, t)
    infl = 0.06 * clamp(t / tp) if t < tp else 0.0
    wins, H = avion(dr, 600, 900, 1250, t, win="square", col=(250, 240, 250), stripe=(150, 80, 200), cola=(112, 58, 168), face=-1, nwin=6, infl=infl, hole=2 if t >= tp else -1, crack=0.6 if t < tp else 1.0, crack_win=2)
    dr.rrect(120, 1300, 420, 1420, 10, (250, 210, 50)); dr.text(270, 1360, "PRUEBA", 56, INK)
    tt = max(0, t - tp)
    bruno(dr, 820, 1900, 0.75, t, expr="shock" if t >= tp else "smug", arm_r=170 if t >= tp else 40, arm_l=170 if t >= tp else 60,
          wig=(150 * tt, -900 * tt + 600 * tt * tt), look=(-1, -1))
    if t >= tp:   # el panel de la ventana sale volando
        wx, wy = wins[2]
        px, py = wx - 500 * tt, wy - 700 * tt + 900 * tt * tt
        ang = tt * 9; c, s_ = math.cos(ang), math.sin(ang); hw, hh = 70, 60
        pts = [(px + c * x - s_ * y, py + s_ * x + c * y) for x, y in ((-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh))]
        dr.poly(pts, GLASS)
    f = tinta(dr); flash(f, t, tp, 0.15)
    img = acabado(f, T)
    medidor(img, t, clamp(t / tp) if t < tp else 0.1, x=250, y=620, label="PRESIÓN")
    burst(img, "¡PUM!", 600, 380, 170, t - tp, col=(255, 222, 40), ang=-8)
    return img, (12 * math.exp(-(t - tp) * 4) if t > tp else 0)

@shot
def s13(t, D, T):    # REVELACIÓN: el Comet, 1954
    u = ease(t / D)
    cam = Cam(lerp(540, 600, u), 980, lerp(1.0, 1.08, u))
    dr = D_(cam); cielo(dr, t, 0.0, sepia=0.55)
    nubes(dr, t, 1500, 160, layer=0, col=(236, 224, 200))
    wins, H = avion(dr, 540, 1000, 1250, t, win="comet", col=(214, 216, 222), stripe=(40, 70, 140), cola=(40, 70, 140), nwin=8, gear=False)
    f = tinta(dr); flash(f, t, 0, 0.2)
    img = acabado(f, T)
    cartel(img, t - 0.2, "COMET · 1954", "PRIMER JET DE PASAJEROS", y=300)
    if t > tl(12, 0.55):
        k = eob((t - tl(12, 0.55)) / 0.35); d = ImageDraw.Draw(img)
        X, Y = cam.p(*wins[5])
        cx, cy = 760, 1320
        d.line([(X, Y), (cx - 150 * k, cy - 60 * k)], fill=INK, width=8)
        d.ellipse([cx - 180 * k, cy - 180 * k, cx + 180 * k, cy + 180 * k], fill=(200, 202, 210), outline=INK, width=10)
        d.rounded_rectangle([cx - 90 * k, cy - 80 * k, cx + 90 * k, cy + 80 * k], radius=int(10 * k), fill=GLASS, outline=INK, width=6)
        x0, y0 = cx + 90 * k, cy - 80 * k
        d.line([(x0, y0), (x0 + 30 * k, y0 - 30 * k), (x0 + 50 * k, y0 - 40 * k), (x0 + 70 * k, y0 - 80 * k)], fill=(220, 40, 40), width=8)
        d.text((cx, cy + 230 * k), "GRIETA EN LA ESQUINA", font=font(48 * k + 1), fill=(255, 255, 255), anchor="mm", stroke_width=8, stroke_fill=INK)
    return img, 0

@shot
def s14(t, D, T):    # la prueba en la piscina gigante → desde entonces, ventanas redondeadas
    sw = tl(13, 0.45)
    if t < sw:
        cam = Cam(540, 1000, lerp(1.0, 1.06, t / sw))
        dr = D_(cam); hangar(dr, t, 1600)
        dr.rrect(-60, 760, 1140, 1600, 16, (60, 140, 200), shade=True)
        avion(dr, 540, 1150, 1050, t, win="comet", col=(214, 216, 222), stripe=(40, 70, 140), cola=(40, 70, 140), nwin=8, gear=False, infl=0.05 * (0.5 + 0.5 * math.sin(t * 5)))
        dr.rrect(-60, 900, 1140, 1600, 0, (70, 160, 220), nolin=True)
        for k in range(8):
            ph = (t * 0.8 + k * 0.13) % 1
            dr.ell(80 + k * 130, 1500 - ph * 600, 16, 16, (200, 236, 255), nolin=True)
        dr.rrect(-60, 890, 1140, 912, 4, (180, 220, 250), nolin=True)
        f = tinta(dr); img = acabado(f, T)
        cartel(img, t - 0.1, "PRUEBA EN PISCINA", "INFLAR · DESINFLAR · REPETIR", y=320)
        n = int(t / sw * 3000)
        d = ImageDraw.Draw(img)
        d.text((540, 1430), f"× {n:,}".replace(",", "."), font=font(90), fill=(255, 255, 255), anchor="mm", stroke_width=10, stroke_fill=INK)
        return img, 0
    tt = t - sw
    cam = Cam(540, 1000, 1.0)
    dr = D_(cam); rayos_fondo(dr, 540, 1000, t, (28, 90, 110), (34, 110, 130))
    for px, sqw in ((300, True), (780, False)):
        dr.ell(px, 1000, 200, 250, (226, 230, 238), shade=True)
        if sqw: dr.rrect(px - 120, 1000 - 110, px + 120, 1000 + 110, 4, GLASS)
        else: dr.rrect(px - 115, 1000 - 165, px + 115, 1000 + 165, 110, GLASS)
    f = tinta(dr); img = acabado(f, T)
    k = eob(tt / 0.3)
    check(img, 300, 700, False, k + 0.01); check(img, 780, 700, True, k + 0.01)
    d = ImageDraw.Draw(img)
    d.text((300, 1330), "ANTES", font=font(60), fill=(255, 255, 255), anchor="mm", stroke_width=8, stroke_fill=INK)
    d.text((780, 1330), "HOY", font=font(60), fill=(255, 255, 255), anchor="mm", stroke_width=8, stroke_fill=INK)
    return img, 0

@shot
def s15(t, D, T):    # remate: oficina de Doña Rita con todo redondo; Bruno calvo al fondo
    u = ease(t / D)
    cam = Cam(540, lerp(1150, 1080, u), lerp(1.25, 1.1, u))
    dr = D_(cam, bg=(240, 220, 190))
    dr.rrect(-600, -400, 1700, 1550, 0, (244, 226, 196))
    for k, (x, r) in enumerate(((140, 140), (540, 170), (940, 140))):
        dr.ell(x, 640, r, r * 1.15, (200, 186, 160), shade=True); dr.ell(x, 640, r * 0.78, r * 0.9, (130, 190, 236))
    dr.rrect(-600, 1550, 1700, 3000, 0, (150, 100, 70))
    dr.ell(540, 1600, 300, 60, (120, 70, 40), shade=True)   # mesa redonda
    bruno(dr, 980, 1640, 0.42, t, expr="worried", arm_r=100, arm_l=20, wig_on=False)
    dr.ell(1090, 1360, 50, 26, (236, 160, 50))   # la peluca en su mano
    rita(dr, 380, 1900, 0.85, t, mouth=boca(14, t), expr="happy_eyes" if boca(14, t) < 0.3 else "happy", arm_r=165, arm_l=165, jump=60 * abs(math.sin(t * 5)))
    nico(dr, 720, 1900, 0.6, t, traje="piloto", arms=(20, 150), elbows=(0, 20), expr="happy_eyes", look=(-1, 0))
    f = tinta(dr); img = acabado(f, T)
    burst(img, "¡TODO REDONDO!", 540, 330, 100, t - tl(14, 0.4), ang=-5)
    return img, 0

@shot
def s16(t, D, T):    # cierre + pregunta
    cam = Cam(540, 1000, 1.0)
    dr = D_(cam); rayos_fondo(dr, 540, 1000, -t, (18, 10, 30), (34, 20, 56))
    o = 1 - ease((t - D + 0.9) / 0.7)
    portal(dr, 540, 1080, 330, t, o)
    if t < D - 1.1:
        nico(dr, 540, 1560, 0.55, t, traje="piloto", arms=(150, 30), elbows=(30, 0), expr="happy")
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
    windn = bp(150, 900)
    S_ = STARTS
    def pizz(t0, t1, vol=1.0, mel=None, bass=None, e8=0.16):
        mel = mel or [72, 76, 79, 76, 74, 77, 81, 77, 72, 76, 79, 84, 83, 79, 74, 71]
        bass = bass or [48, 48, 53, 53, 48, 48, 55, 55]
        k = 0; s = t0
        while s < t1:
            x = seg(e8 * 1.5); m = mel[k % len(mel)]
            pl = np.sin(2 * np.pi * hz(m) * x) * 0.6 + np.sin(2 * np.pi * hz(m) * 2 * x) * 0.2
            add(s, vol * 0.05 * pl * np.exp(-x * 14) * (1 - np.exp(-x * 400)))
            if k % 2 == 0:
                xb = seg(e8 * 2); bm = bass[(k // 4) % len(bass)]
                add(s, vol * 0.1 * np.exp(-xb * 6) * np.sin(2 * np.pi * hz(bm) * xb))
            if k % 4 == 0: add(s, vol * 0.12 * np.exp(-x * 25) * np.sin(2 * np.pi * (80 + 50 * np.exp(-x * 25)) * x))
            if k % 4 == 2: add(s, vol * 0.05 * rng.standard_normal(len(x)) * np.exp(-x * 40))
            k += 1; s += e8
    pizz(0, S_[7])
    # tensión: tambores graves + zumbido de presión
    for kk in range(int((S_[12] - S_[7]) / 0.45)):
        x = seg(0.3); add(S_[7] + kk * 0.45, 0.14 * np.exp(-x * 10) * np.sin(2 * np.pi * (55 + 3 * (kk % 2)) * x))
    x = seg(S_[8] - S_[7]); add(S_[7], 0.06 * np.sin(2 * np.pi * (90 + 30 * np.sin(2 * np.pi * x * 3.2 / (2 * np.pi))) * x) * (0.5 + 0.5 * np.sin(x * 3.2)))   # globo
    x = seg(1.0); add(S_[7] + 0.5, 0.25 * windn[:len(x)] * np.sin(np.pi * x))
    tcr = S_[8] + tl(8, 0.55); x = seg(0.35); add(tcr, 0.5 * bp(1500, 6000)[:len(x)] * np.exp(-x * 14))   # crac
    tcr = S_[9] + tl(9, 0.45); x = seg(0.5); add(tcr, 0.3 * bp(1500, 6000)[:len(x)] * np.exp(-x * 9))
    tp = S_[11] + tl(11, 0.3)
    x = seg(tl(11, 0.3)); add(S_[11], 0.08 * np.sin(2 * np.pi * (120 + 160 * x / max(x[-1], 1e-3)) * x))   # sube la presión
    x = seg(2.0); add(tp, 1.0 * low[:len(x)] * np.exp(-x * 2.5)); add(tp, 0.6 * np.exp(-x * 5) * np.sin(2 * np.pi * (60 + 40 * np.exp(-x * 10)) * x))   # ¡PUM!
    x = seg(1.2); add(tp + 0.1, 0.4 * bp(2500, 8000)[:len(x)] * np.exp(-x * 4))   # vidrio
    x = seg(0.8); add(tp + 0.3, 0.12 * np.sin(2 * np.pi * (500 + 900 * x) * x) * np.exp(-x * 2))   # peluca volando (silbido)
    # revelación seria y piscina
    x = seg(2.5); add(S_[12], 0.16 * np.exp(-x * 0.8) * (np.sin(2 * np.pi * 220 * x) + np.sin(2 * np.pi * 262 * x) + np.sin(2 * np.pi * 330 * x)) / 3)
    for kk in range(14):
        x = seg(0.12); add(S_[13] + kk * 0.2, 0.06 * np.sin(2 * np.pi * (300 + 500 * x / 0.12) * x) * np.exp(-x * 20))   # burbujas
    sw = S_[13] + tl(13, 0.45); x = seg(1.2); add(sw, 0.2 * np.exp(-x * 2) * (np.sin(2 * np.pi * 523 * x) + np.sin(2 * np.pi * 659 * x) + np.sin(2 * np.pi * 784 * x)) / 3)
    pizz(sw, TOTAL, 0.8)
    x = seg(1.2); add(S_[1] + 0.1, 0.12 * np.sin(2 * np.pi * (200 + 600 * x) * x) * np.sin(np.pi * x / 1.2))   # portal
    x = seg(0.5); add(S_[1] + 1.3, 0.5 * np.exp(-x * 9) * np.sin(2 * np.pi * (60 + 40 * np.exp(-x * 20)) * x))
    for k in range(1, len(S_) - 1):
        x = seg(0.3); add(S_[k] - 0.08, 0.12 * wh[:len(x)] * np.sin(np.pi * x / 0.3))
    for k in (3, 7, 9):   # tarjetas de paso: "zas"
        x = seg(0.5); add(S_[k] + 0.15, 0.2 * wh[:len(x)] * np.sin(np.pi * x / 0.5)); x = seg(0.2); add(S_[k] + 0.4, 0.2 * np.exp(-x * 20) * np.sin(2 * np.pi * 900 * x))
    x = seg(0.3); add(S_[3] + 1.6, 0.25 * np.exp(-x * 30) * np.sin(2 * np.pi * 1200 * x))   # clic de la ventana
    x = seg(0.8); add(S_[14] + 0.2, 0.25 * np.exp(-x * 4) * np.sin(2 * np.pi * (300 + 300 * x) * x))
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
