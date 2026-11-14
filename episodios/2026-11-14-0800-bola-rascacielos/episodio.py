#!/usr/bin/env python3
"""¿Por qué hay una bola GIGANTE dentro de este rascacielos? (formato "¿Por qué…?" de días pares)
Estilo vector + cómic (motor/vc.py). Nico con traje de INGENIERO (casco con franja y chaleco con franjas turquesa).
Rival: Rocco (torre rígida). Alcalde gruñón. Dato real: Taipei 101, amortiguador de masa de 660 t."""
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
DURS[0] += 0.3; DURS[1] += 0.9; DURS[13] += 0.3; DURS[17] += 1.0
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
    [("¿Por qué hay", []), ("una bola GIGANTE", ["GIGANTE"]), ("colgando dentro", []), ("de este rascacielos?", ["rascacielos?"])],
    [("Nico cruza el portal", ["portal"]), ("y cae en un concurso:", ["concurso:"]), ("¡gana el rascacielos", []), ("más alto!", ["alto!"])],
    [("Su rival:", []), ("ROCCO", ["ROCCO"]), ("el ingeniero", []), ("más presumido", ["presumido"])],
    [("¡Mi torre es", []), ("de puro ACERO!", ["ACERO!"]), ("¡No se mueve", []), ("ni un milímetro!", ["milímetro!"])],
    [("Uno.", ["Uno."]), ("Nico hace algo", []), ("que parece un error:", ["error:"]), ("cuelga una bola enorme", ["bola"]), ("cerca de la punta…", ["punta…"]), ("y la deja mecerse", ["mecerse"])],
    [("¿¡Una BOLA!?", ["BOLA!?"]), ("¡Esto es un edificio,", []), ("no un reloj!", ["reloj!"])],
    [("Confíe en mí,", []), ("alcalde.", []), ("La bola", ["bola"]), ("es el secreto", ["secreto"])],
    [("Nadie le cree…", ["cree…"]), ("y Rocco se lleva", []), ("la medalla de oro", ["oro"])],
    [("Dos.", ["Dos."]), ("Esa noche llega", []), ("un TIFÓN", ["TIFÓN"]), ("con ráfagas de más de", []), ("200 km/h", ["200", "km/h"])],
    [("Ningún rascacielos", []), ("es rígido de verdad:", ["rígido"]), ("con el viento", ["viento"]), ("la punta se balancea…", ["balancea…"]), ("y la de Rocco,", []), ("cada vez MÁS", ["MÁS"])],
    [("¡Mi café!", ["café!"]), ("¡Todo se mueve!", ["mueve!"]), ("¡Me mareo!", ["mareo!"])],
    [("Tres.", ["Tres."]), ("En la torre de Nico", []), ("la bola se mueve", ["bola"]), ("al lado CONTRARIO…", ["CONTRARIO…"]), ("y frena el balanceo", ["frena"])],
    [("¡Si el edificio", []), ("se va para allá", ["allá"]), ("la bola lo jala", ["jala"]), ("para acá!", ["acá!"])],
    [("Donde Rocco", []), ("revientan las ventanas", ["ventanas"]), ("y todos salen corriendo…", ["corriendo…"]), ("mareados", ["mareados"])],
    [("Esto existe de verdad:", ["verdad:"]), ("el Taipei 101", ["Taipei", "101"]), ("en Taiwán", ["Taiwán"]), ("tiene una bola de", []), ("660 toneladas", ["660", "toneladas"]), ("cerca de la cima", ["cima"])],
    [("Se llama", []), ("amortiguador de masa", ["amortiguador"]), ("y reduce el balanceo", ["balanceo"]), ("hasta un 40 %", ["40", "%"])],
    [("¡Nico!", ["¡Nico!"]), ("¡Quiero una bola", ["bola"]), ("en cada edificio!", ["edificio!"])],
    [("Nos vemos en otro", []), ("mundo hipotético", ["hipotético"]), ("¿Qué otro secreto", ["secreto"]), ("de ingeniería quieres ver?", ["ingeniería"]), ("¡Comenta!", ["¡Comenta!"])],
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
                d.text((x, y), w, font=f, fill=(248, 231, 28) if w in hl else (255, 255, 255), anchor="lm", stroke_width=int(11 * k), stroke_fill=INK)
                x += f.getlength(w) + sp
            return

# ------------------------------------------------------------ escenarios
def mix(a, b, k): return tuple(int(lerp(a[i], b[i], k)) for i in range(3))
STEEL = (140, 150, 168); NTOWER = (88, 170, 186)

def cielo(dr, t, storm=0.0, y_top=-1200):
    day = [(90, 160, 230), (120, 182, 236), (164, 206, 240), (236, 222, 196)]
    st = [(26, 28, 44), (40, 42, 62), (56, 60, 80), (80, 84, 100)]
    for k in range(4):
        dr.rrect(-900, y_top + k * 520, 2000, y_top + (k + 1) * 520 + 4, 0, mix(day[k], st[k], storm))
    if storm < 0.5:
        for k in range(4):   # nubes planas
            x = (k * 420 + t * 20) % 2000 - 500; y = -500 + (k % 2) * 220
            for j in range(3): dr.ell(x + j * 90, y - (j % 2) * 30, 110, 60, mix((250, 250, 252), (90, 92, 110), storm), nolin=True)
    else:
        for k in range(6):
            x = (k * 380 + t * 160) % 2400 - 700; y = -700 + (k % 3) * 200
            for j in range(4): dr.ell(x + j * 110, y - (j % 2) * 40, 150, 80, (60 - 8 * (k % 2), 62, 80))

def skyline(dr, t, gy, storm=0.0):
    for layer, (col, hs, ws, sh) in enumerate((((176, 200, 222), 700, 170, 0.25), ((130, 156, 186), 480, 200, 0.6))):
        c = mix(col, (50, 54, 74), storm * 0.8)
        x = -800 + layer * 90; k = 0
        while x < 2000:
            w = ws + 50 * ((k * 3 + layer) % 3); h = hs * (0.5 + 0.5 * (((k * 7 + layer * 3) % 5) / 4))
            dr.rrect(x, gy - h, x + w, gy, 0, c, nolin=(layer == 0))
            if layer == 1:
                for r in range(int(h / 90)):
                    dr.rrect(x + 20, gy - h + 30 + r * 90, x + w - 20, gy - h + 50 + r * 90, 2, mix(c, (220, 230, 240) if storm < 0.5 else (230, 200, 120), 0.35), nolin=True)
            x += w + 30; k += 1

def suelo(dr, gy, storm=0.0):
    dr.rrect(-900, gy, 2000, gy + 80, 0, mix((180, 180, 186), (70, 70, 80), storm))
    dr.rrect(-900, gy + 80, 2000, 3200, 0, mix((96, 150, 80), (40, 60, 44), storm))
    for j in range(-8, 20): dr.rrect(j * 160, gy + 30, j * 160 + 80, gy + 44, 3, mix((250, 250, 250), (120, 120, 120), storm), nolin=True)

def torre(dr, x, base, w, h, sway, col, t, n=16, ball=None, broken=0.0, crane=False, spire=True, glass=(170, 214, 240), cut=0.84):
    """Torre que se dobla: la punta se desplaza `sway` px (curva f²). ball = ángulo del péndulo en rad (o None)."""
    def at(f): return x + sway * f * f, base - h * f, w / 2 * (1 - 0.22 * f)
    for i in range(n):
        f0, f1 = i / n, (i + 1) / n
        x0, y0, hw0 = at(f0); x1, y1, hw1 = at(f1)
        dr.poly([(x0 - hw0, y0 + 1), (x0 + hw0, y0 + 1), (x1 + hw1, y1), (x1 - hw1, y1)], col)
        dr.poly([(x0 + hw0 * 0.45, y0 + 1), (x0 + hw0, y0 + 1), (x1 + hw1, y1), (x1 + hw1 * 0.45, y1)], mix(col, (20, 20, 40), 0.25), shade=True)
        if ball is not None and cut - 0.07 < (f0 + f1) / 2 < cut + 0.07: continue
        xm, ym, hwm = at((f0 + f1) / 2)
        for j in range(4):
            wx = xm - hwm * 0.8 + j * hwm * 0.42
            g = glass
            if broken > 0 and ((i * 5 + j * 3) % 7) < 7 * broken: g = (34, 30, 44)
            dr.rrect(wx, ym - h / n * 0.32, wx + hwm * 0.3, ym + h / n * 0.22, 2, g)
    xt, yt, hwt = at(1.0)
    dr.rrect(xt - hwt * 1.05, yt - 18, xt + hwt * 1.05, yt + 6, 4, mix(col, (20, 20, 40), 0.3))
    if spire: dr.line([(xt, yt - 10), (xt + sway * 0.12, yt - h * 0.12)], (90, 96, 110), max(6, w * 0.04))
    if ball is not None:   # ventana de corte con el péndulo dentro
        xc, yc, hwc = at(cut)
        hh = h / n * 2.1
        dr.rrect(xc - hwc * 0.85, yc - hh, xc + hwc * 0.85, yc + hh * 0.7, 10, (44, 36, 60), nolin=True)
        dr.rrect(xc - hwc * 0.85, yc - hh, xc + hwc * 0.85, yc - hh + 14, 4, (230, 190, 60))
        px, py = xc, yc - hh + 10
        L = hh * 1.2; r = hwc * 0.36
        bx, by = px + math.sin(ball) * L, py + math.cos(ball) * L
        for sx in (-0.3, 0.3): dr.line([(px + sx * r, py), (bx + sx * r * 0.6, by - r * 0.6)], (200, 200, 210), max(3, r * 0.08))
        dr.ell(bx, by, r, r, (226, 180, 50), shade=True)
        dr.ell(bx - r * 0.35, by - r * 0.35, r * 0.22, r * 0.16, (255, 240, 180), nolin=True)
        dr.rrect(bx - r * 0.7, by - r * 0.08, bx + r * 0.7, by + r * 0.08, 3, TURQ, nolin=True)
    if crane:
        dr.line([(xt + hwt * 0.4, yt), (xt + hwt * 0.4, yt - 260)], (240, 180, 40), 18)
        dr.line([(xt - 200, yt - 250), (xt + 260, yt - 250)], (240, 180, 40), 18)
    return at(1.0)[:2], at(cut)[:2]

def torre101(dr, x, base, s, t, sway=0.0, col=(74, 150, 150)):
    """Silueta estilizada del Taipei 101: podio + 8 módulos que se abren hacia arriba + aguja."""
    S = lambda v: v * s
    dr.rrect(x - S(170), base - S(260), x + S(170), base, 6, mix(col, (20, 30, 40), 0.2), shade=True)
    y = base - S(260)
    for k in range(9):
        f = k / 9; dx = sway * f * f
        dr.poly([(x + dx - S(105), y), (x + dx + S(105), y), (x + dx + S(130), y - S(120)), (x + dx - S(130), y - S(120))], col)
        dr.poly([(x + dx + S(30), y), (x + dx + S(105), y), (x + dx + S(130), y - S(120)), (x + dx + S(40), y - S(120))], mix(col, (10, 20, 30), 0.25), shade=True)
        for j in range(3): dr.rrect(x + dx - S(90), y - S(30 + j * 30), x + dx + S(90), y - S(22 + j * 30), 2, (150, 210, 210), nolin=True)
        y -= S(124)
    dr.rrect(x - S(70), y - S(80), x + S(70), y, 4, col)
    dr.line([(x, y - S(70)), (x, y - S(330))], (120, 130, 140), S(16))
    return y

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

# ------------------------------------------------------------ personajes nuevos
def rocco(dr, x, y, s, t, mouth=0.0, expr="smug", arm_r=20, arm_l=20, sick=False, look=(0, 0), medal=False, lean=0.0):
    """(x, y) = pies. Ingeniero rival alto: traje rojo, bigote enorme, casco rojo. Altura ≈ 900*s."""
    S = lambda v: v * s
    bob = S(5) * math.sin(t * 2.3)
    L = lambda v: lean * S(v)
    suit = (186, 40, 44); skin = (196, 230, 160) if sick else (238, 190, 150)
    for sx in (-1, 1):
        dr.rrect(x + sx * S(40) - S(20), y - S(330), x + sx * S(40) + S(20), y - S(10), S(10), (40, 36, 50))
        dr.ell(x + sx * S(50), y - S(10), S(44), S(17), (20, 18, 24))
    tx = x + L(400)
    dr.rrect(tx - S(110), y - S(640) + bob, tx + S(110), y - S(300), S(50), suit, shade=True)
    dr.poly([(tx - S(40), y - S(640) + bob), (tx + S(40), y - S(640) + bob), (tx, y - S(520) + bob)], (250, 250, 250))
    dr.poly([(tx - S(14), y - S(610) + bob), (tx + S(14), y - S(610) + bob), (tx + S(20), y - S(470) + bob), (tx, y - S(440) + bob), (tx - S(20), y - S(470) + bob)], (230, 190, 50))
    hands = []
    for sx, ang in ((-1, arm_l), (1, arm_r)):
        shx, shy = tx + sx * S(100), y - S(610) + bob
        a = math.radians(ang)
        hx, hy = shx + sx * math.sin(a) * S(230), shy + math.cos(a) * S(230)
        dr.line([(shx, shy), (hx, hy)], suit, S(52))
        dr.ell(hx, hy, S(30), S(30), skin)
        hands.append((hx, hy))
    if medal:
        dr.line([(tx - S(50), y - S(630) + bob), (tx, y - S(520) + bob), (tx + S(50), y - S(630) + bob)], (40, 90, 200), S(14))
        dr.ell(tx, y - S(500) + bob, S(40), S(40), (250, 200, 50), shade=True)
    hx, hy = tx + L(250), y - S(800) + bob
    dr.ell(hx, hy, S(140), S(165), skin, shade=True)
    if sick or expr == "dizzy":
        for sx in (-1, 1):
            cx, cy = hx + sx * S(55), hy - S(25)
            for r in (30, 18, 7): dr.ell(cx, cy, S(r), S(r), (255, 255, 255) if r != 18 else INK)
    else:
        blink = (t % 3.4) < 0.12
        for sx in (-1, 1):
            ex, ey = hx + sx * S(55), hy - S(25)
            if blink: dr.rrect(ex - S(26), ey - S(3), ex + S(26), ey + S(5), S(3), INK); continue
            big = 1.3 if expr == "shock" else 1.0
            lid = expr == "smug"
            dr.ell(ex, ey, S(30) * big, S(34) * big, (255, 255, 255))
            dr.ell(ex + look[0] * S(9), ey + look[1] * S(9) + (S(6) if lid else 0), S(13), S(15), INK)
            if lid: dr.rrect(ex - S(32), ey - S(36), ex + S(32), ey - S(4), S(6), skin)
    tilt = {"angry": 16, "smug": -10, "shock": -16}.get(expr, -6)
    for sx in (-1, 1):
        ex = hx + sx * S(55)
        dr.line([(ex - S(32), hy - S(78) + sx * S(tilt) * 0.5), (ex + S(32), hy - S(78) - sx * S(tilt) * 0.5)], (40, 30, 30), S(14))
    dr.ell(hx, hy + S(25), S(30), S(34), mix(skin, (200, 110, 100), 0.4))
    mo = clamp(mouth)
    if mo > 0.06 or expr == "shock":
        mo = max(mo, 0.6 if expr == "shock" else 0)
        dr.ell(hx, hy + S(100), S(44), S(10 + 34 * mo), (100, 24, 34))
    else:
        dr.line([(hx - S(40), hy + S(98)), (hx + S(8), hy + S(104)), (hx + S(44), hy + S(86))], (100, 24, 34), S(10))
    for sx in (-1, 1):   # bigote enorme
        dr.poly([(hx, hy + S(58)), (hx + sx * S(60), hy + S(48)), (hx + sx * S(140), hy + S(20)), (hx + sx * S(120), hy + S(70)), (hx + sx * S(50), hy + S(84))], (36, 26, 26))
    dr.chord(hx, hy - S(90), S(150), S(130), 180, 360, (210, 44, 48))   # casco rojo
    dr.rrect(hx - S(190), hy - S(100), hx + S(190), hy - S(76), S(10), (170, 30, 36))
    dr.text(hx, hy - S(150), "R", S(70), (250, 220, 80))
    if sick:
        k = (t * 1.2) % 1
        dr.ell(hx + S(150), hy - S(40) + S(60) * k, S(14), S(20), (140, 210, 255))
    return dict(hands=hands, head=(hx, hy))

def alcalde(dr, x, y, s, t, mouth=0.0, expr="angry", arm_r=20, arm_l=20, red=0.0, look=(0, 0)):
    """(x, y) = pies. Bajito y redondo, chistera, banda tricolor, bigote gris. Altura ≈ 760*s."""
    S = lambda v: v * s
    bob = S(5) * math.sin(t * 2.6 + 1)
    skin = mix((240, 196, 160), (220, 70, 70), red)
    for sx in (-1, 1):
        dr.rrect(x + sx * S(50) - S(22), y - S(150), x + sx * S(50) + S(22), y - S(10), S(10), (34, 34, 46))
        dr.ell(x + sx * S(56), y - S(10), S(42), S(16), (20, 18, 24))
    dr.ell(x, y - S(320) + bob, S(175), S(195), (44, 46, 66), shade=True)
    dr.poly([(x - S(130), y - S(450) + bob), (x - S(80), y - S(480) + bob), (x + S(150), y - S(220) + bob), (x + S(110), y - S(170) + bob)], (250, 210, 50))
    dr.poly([(x - S(118), y - S(440) + bob), (x - S(95), y - S(456) + bob), (x + S(135), y - S(200) + bob), (x + S(118), y - S(186) + bob)], (40, 90, 200))
    dr.ell(x + S(10), y - S(330) + bob, S(26), S(26), TURQ)   # broche turquesa de la ciudad
    hands = []
    for sx, ang in ((-1, arm_l), (1, arm_r)):
        shx, shy = x + sx * S(140), y - S(440) + bob
        a = math.radians(ang)
        hx, hy = shx + sx * math.sin(a) * S(170), shy + math.cos(a) * S(170)
        dr.line([(shx, shy), (hx, hy)], (44, 46, 66), S(50))
        dr.ell(hx, hy, S(30), S(30), (250, 250, 250))
        hands.append((hx, hy))
    hx, hy = x, y - S(600) + bob
    dr.ell(hx, hy, S(135), S(130), skin, shade=True)
    blink = (t % 3.1) < 0.12
    for sx in (-1, 1):
        ex, ey = hx + sx * S(50), hy - S(15)
        if expr == "happy_eyes":
            dr.chord(ex, ey + S(5), S(28), S(22), 180, 360, INK); dr.chord(ex, ey + S(11), S(24), S(16), 180, 360, skin); continue
        if blink: dr.rrect(ex - S(24), ey - S(3), ex + S(24), ey + S(5), S(3), INK); continue
        dr.ell(ex, ey, S(26), S(30), (255, 255, 255))
        dr.ell(ex + look[0] * S(8), ey + look[1] * S(8), S(12), S(14), INK)
    tilt = {"angry": 22, "happy": -6, "happy_eyes": -8}.get(expr, 0)
    for sx in (-1, 1):
        ex = hx + sx * S(50)
        dr.line([(ex - S(30), hy - S(62) - sx * S(tilt) * 0.5), (ex + S(30), hy - S(62) + sx * S(tilt) * 0.5)], (150, 150, 160), S(14))
    dr.ell(hx, hy + S(25), S(30), S(28), mix(skin, (200, 110, 100), 0.4))
    mo = clamp(mouth)
    if mo > 0.06: dr.ell(hx, hy + S(90), S(42), S(10 + 30 * mo), (100, 24, 34))
    elif expr == "angry": dr.chord(hx, hy + S(108), S(40), S(26), 180, 360, (100, 24, 34))
    else: dr.chord(hx, hy + S(62), S(42), S(36), 0, 180, (100, 24, 34))
    for sx in (-1, 1): dr.ell(hx + sx * S(48), hy + S(58), S(56), S(22), (196, 196, 206))
    dr.rrect(hx - S(160), hy - S(118), hx + S(160), hy - S(96), S(8), (24, 22, 30))
    dr.rrect(hx - S(95), hy - S(330), hx + S(95), hy - S(110), S(10), (24, 22, 30))
    dr.rrect(hx - S(95), hy - S(160), hx + S(95), hy - S(130), S(4), (190, 40, 50))
    return dict(hands=hands, head=(hx, hy))

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

def taza(dr, x, y, s, spill=0.0):
    S = lambda v: v * s
    dr.rrect(x - S(40), y - S(80), x + S(40), y, S(12), (250, 250, 250), shade=True)
    dr.ell(x + S(48), y - S(42), S(20), S(24), (250, 250, 250))
    dr.ell(x, y - S(80), S(38), S(10), (110, 60, 30))
    if spill > 0:
        for k in range(5):
            dr.ell(x - S(30) + k * S(18) + spill * S(60), y - S(100) - spill * S(60) * math.sin(k + 1), S(12), S(16), (110, 60, 30))

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

# ------------------------------------------------------------ planos
SHOTS = []
def shot(fn): SHOTS.append(fn); return fn
def tl(k, frac): return LEAD + len(VOZ[k]) / SR * frac
def D_(cam, bg=(0, 0, 0)): return D(cam, bg)
GY = 1500

@shot
def s01(t, D, T):    # gancho: contrapicado de la torre con la bola brillando dentro
    u = ease(t / D)
    cam = Cam(540, lerp(560, 330, u), lerp(1.0, 1.45, u))
    dr = D_(cam); cielo(dr, t); skyline(dr, t, GY)
    sw = 30 * math.sin(t * 1.8)
    top, cut = torre(dr, 540, GY + 200, 560, 1900, sw, NTOWER, t, n=18, ball=-0.5 * math.sin(t * 1.8))
    suelo(dr, GY + 200)
    f = tinta(dr); add_glow(f, *cam.p(*cut), 220, (255, 220, 120), 0.45)
    img = acabado(f, T)
    burst(img, "¿POR QUÉ?", 540, 330, 150, t - 0.1, ang=-6)
    return img, 0

@shot
def s02(t, D, T):    # portal → Nico ingeniero cae al concurso
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
    cam = Cam(540, 1060, lerp(1.0, 1.06, ease(tt / (D - tp))))
    dr = D_(cam); cielo(dr, t); skyline(dr, t, GY)
    torre(dr, 150, GY, 300, 900, 0, STEEL, t, n=10, crane=True)
    torre(dr, 930, GY, 300, 760, 0, NTOWER, t, n=9, crane=True, spire=False)
    suelo(dr, GY)
    for k in range(6): persona(dr, -60 + k * 240, GY + 380 + (k % 2) * 40, 0.42, t, [(220, 80, 80), (80, 120, 210), (240, 180, 60), (120, 180, 100)][k % 4], ph=k)
    portal(dr, 540, 1150, 220, t, 1 - ease((tt - 0.7) / 0.4))
    land = clamp(tt / 0.35)
    sq = 1 - 0.3 * math.exp(-tt * 7) * math.cos(tt * 20) if land >= 1 else 1.15
    nico(dr, 540, lerp(1050, 1780, land ** 2), 0.66, t, traje="ingeniero", arms=(140, 140) if land < 1 else (30, 165), elbows=(0, 15), expr="shock" if tt < 0.9 else "happy", squash=sq, look=(0.3, -0.6), mouth=0.3 if tt > 0.9 else 0)
    f = tinta(dr)
    if tt < 0.2: f += 255 * (1 - tt / 0.2)
    img = acabado(f, T)
    if tt > 0.6: cartel(img, tt - 0.6, "GRAN CONCURSO", "¡GANA EL MÁS ALTO!", y=330)
    return img, 0

@shot
def s03(t, D, T):    # presentación de Rocco con su torre de acero
    cam = Cam(lerp(600, 520, ease(t / D)), 1150, 1.25)
    dr = D_(cam); cielo(dr, t); skyline(dr, t, GY)
    torre(dr, 760, GY + 80, 380, 1500, 0, STEEL, t, n=16)
    suelo(dr, GY + 80)
    rocco(dr, 420, 1800, 0.78, t, expr="smug", arm_r=150, arm_l=30, look=(1, 0), mouth=0.0)
    f = tinta(dr); img = acabado(f, T)
    nombre(img, t - tl(2, 0.25), "ROCCO", "el ingeniero presumido")
    return img, 0

@shot
def s04(t, D, T):    # "¡Mi torre es de puro acero!" primer plano
    cam = Cam(540, 1050, lerp(1.45, 1.6, ease(t / D)))
    dr = D_(cam); cielo(dr, t); skyline(dr, t, GY)
    torre(dr, 860, GY + 80, 380, 1500, 0, STEEL, t, n=16)
    suelo(dr, GY + 80)
    hit = (t * 3) % 1 < 0.5
    rocco(dr, 520, 1950, 0.95, t, expr="smug" if boca(3, t) < 0.4 else "angry", arm_r=30 if hit else 60, arm_l=150 + 20 * math.sin(t * 6), mouth=boca(3, t))
    f = tinta(dr); img = acabado(f, T)
    burst(img, "¡ACERO!", 820, 340, 140, t - 0.4, col=(200, 210, 230), ang=8)
    if t > tl(3, 0.55): burst(img, "0 mm", 260, 560, 110, t - tl(3, 0.55), col=(255, 120, 90), ang=-10)
    return img, 0

@shot
def s05(t, D, T):    # PASO 1: Nico cuelga la bola con la grúa
    u = ease(t / D)
    cam = Cam(560, lerp(980, 1060, u), lerp(1.05, 1.12, u))
    dr = D_(cam); cielo(dr, t); skyline(dr, t, GY)
    drop = clamp((t - 0.4) / 1.8)
    sw = 0.55 * math.sin(t * 2.6) * clamp((t - 2.0) / 0.5)
    top, cut = torre(dr, 700, GY, 460, 1100, 0, NTOWER, t, n=12, ball=sw if drop >= 1 else None, crane=True, cut=0.8)
    if drop < 1:   # la bola baja colgada de la grúa
        bx, by = top[0] + 120, lerp(top[1] - 700, cut[1], ease(drop))
        dr.line([(top[0] + 230, top[1] - 250), (bx, by - 60)], (60, 60, 70), 6)
        dr.ell(bx, by, 70, 70, (226, 180, 50), shade=True)
        dr.rrect(bx - 50, by - 6, bx + 50, by + 6, 3, TURQ, nolin=True)
    suelo(dr, GY)
    nico(dr, 280, 1720, 0.72, t, traje="ingeniero", arms=(160, 120), elbows=(10, 30), expr="happy", look=(0.6, -0.8))
    f = tinta(dr); img = acabado(f, T)
    tarjeta_paso(img, t, 1, "EL “ERROR”")
    if t > tl(4, 0.8): burst(img, "¿?", 850, 900, 150, t - tl(4, 0.8), col=(255, 255, 255), ang=8)
    return img, 0

@shot
def s06(t, D, T):    # alcalde furioso
    cam = Cam(540, 1050, lerp(1.5, 1.62, ease(t / D)))
    dr = D_(cam); cielo(dr, t); skyline(dr, t, GY)
    torre(dr, 900, GY + 80, 360, 1300, 0, NTOWER, t, n=14, ball=0.5 * math.sin(t * 2.6))
    suelo(dr, GY + 80)
    alcalde(dr, 520, 1950, 1.1, t, mouth=boca(5, t), expr="angry", arm_r=160 + 10 * math.sin(t * 9), arm_l=40, red=clamp(t / 1.2) * 0.8)
    f = tinta(dr); img = acabado(f, T)
    burst(img, "¿¡UNA BOLA!?", 540, 360, 120, t - 0.05, col=(255, 90, 70), ang=-6)
    d = ImageDraw.Draw(img)
    for k in range(3):   # vapor de rabia
        ph = (t * 1.5 + k / 3) % 1
        d.ellipse([360 + k * 170 - 30 * ph, 640 - 260 * ph, 360 + k * 170 + 50 + 40 * ph, 700 - 260 * ph], fill=(250, 250, 250), outline=INK, width=5)
    return img, 2 * math.sin(t * 40)

@shot
def s07(t, D, T):    # Nico: confíe en mí
    cam = Cam(540, 1060, 1.65)
    dr = D_(cam); cielo(dr, t); skyline(dr, t, GY)
    torre(dr, 220, GY + 80, 360, 1300, 0, NTOWER, t, n=14, ball=0.5 * math.sin(t * 2.6))
    suelo(dr, GY + 80)
    nico(dr, 560, 1700, 0.72, t, traje="ingeniero", arms=(25, 120), elbows=(0, 60), expr="smug" if boca(6, t) < 0.2 else "happy", mouth=boca(6, t), look=(-0.4, 0))
    f = tinta(dr); img = acabado(f, T)
    if t > tl(6, 0.5):
        d = ImageDraw.Draw(img); k = eob((t - tl(6, 0.5)) / 0.3)
        d.ellipse([760 - 70 * k, 520 - 70 * k, 760 + 70 * k, 520 + 70 * k], fill=(226, 180, 50), outline=INK, width=8)
        burst(img, "SECRETO", 760, 680, 70, t - tl(6, 0.5), col=(248, 231, 28), ang=6)
    return img, 0

@shot
def s08(t, D, T):    # todos se van con Rocco; medalla
    u = ease(t / D)
    cam = Cam(lerp(380, 700, u), 1200, 1.05)
    dr = D_(cam); cielo(dr, t); skyline(dr, t, GY)
    torre(dr, 120, GY, 300, 1100, 0, NTOWER, t, n=12, ball=0.5 * math.sin(t * 2.6))
    torre(dr, 980, GY, 340, 1250, 0, STEEL, t, n=13)
    suelo(dr, GY)
    nico(dr, 160, 1760, 0.5, t, traje="ingeniero", arms=(10, 10), expr="worried", look=(1, 0))
    dr.ell(330 + (t * 140) % 500, 1730, 34, 34, (190, 160, 100))   # bola de paja rodando
    rocco(dr, 900, 1760, 0.6, t, expr="smug", arm_r=170, arm_l=30, medal=t > tl(7, 0.55))
    alcalde(dr, 700, 1760, 0.5, t, expr="happy", arm_r=120, arm_l=20, look=(1, 0))
    for k in range(5):
        persona(dr, 500 + k * 150 - (1 - u) * 300, 1800 + (k % 2) * 30, 0.36, t, [(220, 80, 80), (80, 120, 210), (240, 180, 60), (120, 180, 100)][k % 4], ph=k, run=u < 0.6)
    f = tinta(dr); img = acabado(f, T)
    if t > tl(7, 0.55): burst(img, "¡ORO!", 760, 420, 120, t - tl(7, 0.55), ang=8)
    return img, 0

@shot
def s09(t, D, T):    # PASO 2: llega el tifón
    storm = clamp(t / 0.8)
    cam = Cam(540, 900, lerp(1.0, 1.08, ease(t / D)))
    dr = D_(cam); cielo(dr, t, storm); skyline(dr, t, GY, storm)
    sw = 25 * math.sin(t * 3) * storm
    torre(dr, 260, GY, 320, 1250, sw * 0.4, mix(NTOWER, (40, 70, 80), storm * 0.5), t, n=13, ball=-0.3 * math.sin(t * 3))
    torre(dr, 820, GY, 340, 1300, sw * 1.6, mix(STEEL, (60, 64, 80), storm * 0.5), t, n=13)
    suelo(dr, GY, storm)
    f = tinta(dr)
    lt = tl(8, 0.35); flash(f, t, lt, 0.2)
    img = acabado(f, T); lluvia(img, t, storm); viento(img, t, storm)
    tarjeta_paso(img, t, 2, "EL TIFÓN")
    if t > tl(8, 0.7):
        d = ImageDraw.Draw(img); k = eob((t - tl(8, 0.7)) / 0.3)
        d.rounded_rectangle([200, 300, 880, 430], radius=20, fill=(30, 30, 46), outline=(250, 200, 60), width=8)
        d.text((540, 365), "VIENTO: +200 KM/H", font=font(60 * k + 1), fill=(250, 220, 60), anchor="mm")
    return img, (6 * math.sin(t * 20) if t > lt else 0)

@shot
def s10(t, D, T):    # la torre de Rocco se balancea cada vez más
    u = t / D
    cam = Cam(540, 860, lerp(0.95, 1.05, ease(u)))
    dr = D_(cam); cielo(dr, t, 1.0); skyline(dr, t, GY, 1.0)
    amp_r = lerp(40, 260, ease(u)); amp_n = 30
    torre(dr, 250, GY, 320, 1250, amp_n * math.sin(t * 2.4), (50, 110, 124), t, n=13, ball=-0.45 * math.sin(t * 2.4))
    torre(dr, 800, GY, 340, 1300, amp_r * math.sin(t * 2.4), (100, 106, 124), t, n=13)
    suelo(dr, GY, 1.0)
    f = tinta(dr); img = acabado(f, T); lluvia(img, t, 1.0); viento(img, t, 0.7)
    medidor(img, t, 0.3 + 0.65 * ease(u) * (0.75 + 0.25 * abs(math.sin(t * 2.4))), x=800, y=520, label="ROCCO")
    medidor(img, t, 0.15 + 0.05 * abs(math.sin(t * 2.4)), x=280, y=520, label="NICO")
    return img, 3

@shot
def s11(t, D, T):    # Rocco en su oficina mareado
    ang = 9 * math.sin(t * 2.4)
    cam = Cam(540, 1050, 1.25)
    dr = D_(cam, bg=(200, 190, 170))
    dr.rrect(-600, -400, 1700, 1300, 0, (214, 200, 176))
    for k in range(-2, 4):   # ventana con tormenta
        dr.rrect(80 + k * 340, 300, 360 + k * 340, 950, 8, (40, 44, 66))
        dr.rrect(80 + k * 340, 610, 360 + k * 340, 630, 2, (150, 130, 110))
    dr.rrect(-600, 1300, 1700, 3000, 0, (120, 80, 60))
    dr.rrect(120, 1340, 980, 1420, 10, (150, 96, 60), shade=True)
    rocco(dr, 540, 2000, 0.95, t, expr="dizzy", arm_r=150, arm_l=150 + 15 * math.sin(t * 7), mouth=boca(10, t), sick=True)
    taza(dr, 820 + 60 * math.sin(t * 2.4), 1340, 1.2, spill=clamp(t / 0.6))
    f = tinta(dr)
    img = acabado(f, T)
    img = img.rotate(ang, resample=Image.BILINEAR, center=(540, 1100), fillcolor=(20, 16, 24))
    s = 1 + abs(math.sin(math.radians(ang))) * 0.9
    w2, h2 = int(W / s), int(H / s)
    img = img.crop(((W - w2) // 2, (H - h2) // 2, (W - w2) // 2 + w2, (H - h2) // 2 + h2)).resize((W, H), Image.BILINEAR)
    burst(img, "¡MI CAFÉ!", 540, 380, 120, t - 0.05, col=(200, 140, 80), ang=-8)
    return img, 0

@shot
def s12(t, D, T):    # PASO 3: la bola va al lado contrario (corte grande)
    ph = t * 2.4
    cam = Cam(540, 980, 1.0)
    dr = D_(cam, bg=(30, 32, 50)); cielo(dr, t, 1.0)
    sw = 90 * math.sin(ph)
    top, cut = torre(dr, 540, GY + 900, 760, 2300, sw, (50, 120, 134), t, n=16, ball=-0.55 * math.sin(ph), cut=0.72)
    f = tinta(dr); add_glow(f, *cam.p(*cut), 260, (255, 210, 120), 0.35)
    img = acabado(f, T); lluvia(img, t, 0.6)
    tarjeta_paso(img, t, 3, "LA BOLA")
    if t > 1.2:
        s_ = math.sin(ph)
        flechas(img, 540 + 160 * (1 if s_ > 0 else -1), 380, 1 if s_ > 0 else -1, (255, 120, 90), 1.0, "EDIFICIO")
        flechas(img, 540 - 160 * (1 if s_ > 0 else -1), 1350, -1 if s_ > 0 else 1, (248, 231, 28), 1.0, "BOLA")
    return img, 0

@shot
def s13(t, D, T):    # Nico explica junto a la bola (interior)
    ph = t * 2.4
    cam = Cam(540, 1060, 1.3)
    dr = D_(cam, bg=(44, 40, 60))
    dr.rrect(-600, -400, 1700, 1500, 0, (60, 56, 80))
    for k in range(5): dr.rrect(-300 + k * 380, -200, -260 + k * 380, 1500, 0, (80, 76, 104))
    dr.rrect(-600, 1500, 1700, 3000, 0, (90, 86, 110))
    px, py = 700, 0
    bx, by = px + math.sin(-0.35 * math.sin(ph)) * 820, py + math.cos(-0.35 * math.sin(ph)) * 820
    for sx in (-50, 50): dr.line([(px + sx, py), (bx + sx * 0.6, by - 150)], (200, 200, 210), 12)
    dr.ell(bx, by, 220, 220, (226, 180, 50), shade=True)
    dr.rrect(bx - 155, by - 18, bx + 155, by + 18, 6, TURQ, nolin=True)
    nico(dr, 330, 1700, 0.8, t, traje="ingeniero", arms=(95 + 30 * math.sin(ph), 95 - 30 * math.sin(ph)), elbows=(20, 20), expr="happy", mouth=boca(12, t), look=(0.8, -0.3))
    f = tinta(dr); add_glow(f, *cam.p(bx - 100, by - 100), 260, (255, 230, 150), 0.3)
    img = acabado(f, T)
    burst(img, "¡JALA!", 800, 400, 120, t - tl(12, 0.55), col=(248, 231, 28), ang=7)
    return img, 0

@shot
def s14(t, D, T):    # revientan las ventanas de Rocco
    cam = Cam(540, 1000, lerp(1.0, 1.1, ease(t / D)))
    dr = D_(cam); cielo(dr, t, 1.0); skyline(dr, t, GY, 1.0)
    br = clamp((t - 0.4) / 0.5)
    torre(dr, 540, GY, 520, 1400, 120 * math.sin(t * 2.4) * (1 - 0.6 * br), (100, 106, 124), t, n=14, broken=br)
    suelo(dr, GY, 1.0)
    for k in range(5):
        x = (k * 230 + t * 260) % 1400 - 200
        persona(dr, x, 1800 + (k % 2) * 40, 0.42, t, [(220, 80, 80), (80, 120, 210), (240, 180, 60), (120, 180, 100)][k % 4], ph=k, dizzy=True, run=True)
    rocco(dr, (300 + t * 200) % 1300 - 100, 1830, 0.5, t * 3, expr="dizzy", sick=True, arm_r=150, arm_l=150)
    f = tinta(dr); flash(f, t, 0.4, 0.15)
    img = acabado(f, T); lluvia(img, t, 0.8)
    d = ImageDraw.Draw(img)
    if br > 0:
        rng = np.random.default_rng(5)
        for k in range(30):   # vidrios volando
            vx, vy = rng.uniform(-600, 600), rng.uniform(-500, -100); tt = t - 0.4
            x = 540 + vx * tt; y = 700 + vy * tt + 900 * tt * tt
            d.polygon([(x, y), (x + 26, y + 10), (x + 6, y + 30)], fill=(190, 226, 250), outline=INK)
    burst(img, "¡CRASH!", 540, 360, 150, t - 0.4, col=(190, 226, 250), ang=-7)
    return img, (10 * math.exp(-(t - 0.4) * 3) if t > 0.4 else 0)

@shot
def s15(t, D, T):    # REVELACIÓN: Taipei 101 de verdad
    u = ease(t / D)
    cam = Cam(540, lerp(900, 760, u), lerp(0.92, 1.0, u))
    dr = D_(cam); cielo(dr, t, 0.0); skyline(dr, t, GY)
    yt = torre101(dr, 540, GY + 120, 1.0, t)
    suelo(dr, GY + 120)
    f = tinta(dr)
    flash(f, t, 0, 0.2)
    img = acabado(f, T)
    cartel(img, t - 0.2, "TAIPEI 101", "TAIWÁN · 508 m", y=300)
    if t > tl(14, 0.6):   # zoom de lupa a la bola
        k = eob((t - tl(14, 0.6)) / 0.35); d = ImageDraw.Draw(img)
        cx, cy = 730, 1000
        X, Y = cam.p(540, yt + 360)
        d.line([(X, Y), (cx - 160 * k, cy)], fill=INK, width=8)
        d.ellipse([cx - 190 * k, cy - 190 * k, cx + 190 * k, cy + 190 * k], fill=(44, 36, 60), outline=INK, width=10)
        bx = cx + 40 * math.sin(t * 2.4) * k
        d.line([(cx, cy - 190 * k), (bx, cy + 10 * k)], fill=(200, 200, 210), width=8)
        d.ellipse([bx - 100 * k, cy - 70 * k, bx + 100 * k, cy + 130 * k], fill=(226, 180, 50), outline=INK, width=8)
        d.text((W / 2 + 60, cy + 260 * k), "660 TONELADAS", font=font(60 * k + 1), fill=(248, 231, 28), anchor="mm", stroke_width=9, stroke_fill=INK)
    return img, 0

@shot
def s16(t, D, T):    # amortiguador de masa · −40 %
    cam = Cam(540, 1000, 1.0)
    dr = D_(cam); rayos_fondo(dr, 540, 1000, t, (28, 90, 110), (34, 110, 130))
    ph = t * 2.4
    px, py = 320, 420
    bx, by = px + math.sin(0.5 * math.sin(ph)) * 420, py + math.cos(0.5 * math.sin(ph)) * 420
    dr.line([(px, py), (bx, by)], (220, 220, 230), 12)
    dr.ell(bx, by, 150, 150, (226, 180, 50), shade=True)
    dr.rrect(bx - 110, by - 14, bx + 110, by + 14, 4, TURQ, nolin=True)
    dr.rrect(120, py - 30, 520, py, 6, (90, 96, 110))
    # barras: sin bola vs con bola
    k = eob((t - tl(15, 0.5)) / 0.5)
    dr.rrect(640, 1350 - 600, 800, 1350, 8, (230, 70, 60), shade=True)
    dr.rrect(860, 1350 - 600 * lerp(1.0, 0.6, k), 1020, 1350, 8, (90, 200, 110), shade=True)
    f = tinta(dr); img = acabado(f, T)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([90, 230, 990, 360], radius=24, fill=(250, 250, 246), outline=INK, width=8)
    d.text((540, 295), "AMORTIGUADOR DE MASA", font=font(62), fill=INK, anchor="mm")
    d.text((720, 1410), "SIN", font=font(44), fill=(255, 255, 255), anchor="mm", stroke_width=6, stroke_fill=INK)
    d.text((940, 1410), "CON", font=font(44), fill=(255, 255, 255), anchor="mm", stroke_width=6, stroke_fill=INK)
    d.text((360, 1440), "BALANCEO", font=font(52), fill=(255, 255, 255), anchor="mm", stroke_width=7, stroke_fill=INK)
    if t > tl(15, 0.6): burst(img, "-40 %", 880, 620, 130, t - tl(15, 0.6), col=(120, 240, 140), ang=8)
    return img, 0

@shot
def s17(t, D, T):    # remate: bolas en TODOS los edificios (hasta la casa del perro)
    u = ease(t / D)
    cam = Cam(540, lerp(1150, 1050, u), lerp(1.3, 1.0, u))
    dr = D_(cam); cielo(dr, t); skyline(dr, t, GY)
    for k, (x, w, h, c) in enumerate(((-120, 260, 900, (200, 160, 120)), (980, 300, 1000, (150, 160, 190)))):
        torre(dr, x, GY, w, h, 0, c, t, n=10, ball=0.5 * math.sin(t * 2.6 + k), cut=0.7)
    torre(dr, 540, GY, 340, 1200, 0, NTOWER, t, n=12, ball=0.5 * math.sin(t * 2.6))
    suelo(dr, GY)
    # casita del perro con su bolita
    dr.rrect(780, 1640, 980, 1790, 6, (190, 70, 60), shade=True)
    dr.poly([(760, 1650), (880, 1560), (1000, 1650)], (120, 50, 40))
    dr.ell(880, 1740, 46, 50, (50, 30, 30))
    bb = 880 + 30 * math.sin(t * 4)
    dr.line([(880, 1560), (bb, 1500)], (60, 60, 70), 4); dr.ell(bb, 1500, 22, 22, (226, 180, 50))
    alcalde(dr, 380, 1880, 0.72, t, mouth=boca(16, t), expr="happy_eyes" if boca(16, t) < 0.3 else "happy", arm_r=165, arm_l=165)
    nico(dr, 680, 1880, 0.55, t, traje="ingeniero", arms=(20, 150), elbows=(0, 20), expr="happy_eyes", look=(-1, 0))
    f = tinta(dr); img = acabado(f, T)
    burst(img, "¡UNA BOLA PARA TODOS!", 540, 360, 84, t - tl(16, 0.4), ang=-5)
    return img, 0

@shot
def s18(t, D, T):    # cierre + pregunta
    cam = Cam(540, 1000, 1.0)
    dr = D_(cam); rayos_fondo(dr, 540, 1000, -t, (18, 10, 30), (34, 20, 56))
    o = 1 - ease((t - D + 0.9) / 0.7)
    portal(dr, 540, 1080, 330, t, o)
    if t < D - 1.1:
        info = nico(dr, 540, 1560, 0.55, t, traje="ingeniero", arms=(150, 30), elbows=(30, 0), expr="happy", mouth=0.0)
    f = tinta(dr); add_glow(f, 540, 1080, 450, (150, 120, 255), 0.5 * o)
    img = acabado(f, T)
    d = ImageDraw.Draw(img)
    if t > tl(17, 0.4):
        k = eob((t - tl(17, 0.4)) / 0.3)
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
    pizz(0, S_[8])
    # tormenta: viento + tambores tensos
    x = seg(S_[14] - S_[8]); add(S_[8], 0.5 * windn[:len(x)] * (0.4 + 0.6 * np.abs(np.sin(2 * np.pi * x / 3.1))) * np.clip(x / 1.0, 0, 1))
    for kk in range(int((S_[14] - S_[8]) / 0.42)):
        x = seg(0.3); add(S_[8] + kk * 0.42, 0.15 * np.exp(-x * 10) * np.sin(2 * np.pi * (55 + 2 * (kk % 2)) * x))
    lt = S_[8] + tl(8, 0.35); x = seg(2.0); add(lt, 0.9 * low[:len(x)] * np.exp(-x * 2))   # trueno
    x = seg(S_[12] - S_[10]); add(S_[10], 0.05 * np.sin(2 * np.pi * 70 * x) * np.sin(2 * np.pi * x / 2.6))   # crujido
    for kk in range(6):   # crujidos metálicos
        x = seg(0.5); add(S_[9] + 0.8 + kk * 0.9, 0.08 * np.sin(2 * np.pi * (180 - 60 * x) * x) * np.exp(-x * 5))
    # vidrios
    tc = S_[13] + 0.4; x = seg(1.2); add(tc, 0.6 * bp(2500, 8000)[:len(x)] * np.exp(-x * 4)); add(tc, 0.5 * np.exp(-x * 5) * np.sin(2 * np.pi * (60 + 40 * np.exp(-x * 10)) * x))
    # revelación y final alegre
    x = seg(1.5); add(S_[14], 0.18 * np.exp(-x * 1.5) * (np.sin(2 * np.pi * 523 * x) + np.sin(2 * np.pi * 659 * x) + np.sin(2 * np.pi * 784 * x)) / 3)
    pizz(S_[14] + 0.3, TOTAL, 0.8)
    x = seg(1.2); add(S_[1] + 0.1, 0.12 * np.sin(2 * np.pi * (200 + 600 * x) * x) * np.sin(np.pi * x / 1.2))   # portal
    x = seg(0.5); add(S_[1] + 1.3, 0.5 * np.exp(-x * 9) * np.sin(2 * np.pi * (60 + 40 * np.exp(-x * 20)) * x))
    for k in range(1, len(S_) - 1):
        x = seg(0.3); add(S_[k] - 0.08, 0.12 * wh[:len(x)] * np.sin(np.pi * x / 0.3))
    for k in (4, 8, 11):   # tarjetas de paso: "zas"
        x = seg(0.5); add(S_[k] + 0.15, 0.2 * wh[:len(x)] * np.sin(np.pi * x / 0.5)); x = seg(0.2); add(S_[k] + 0.4, 0.2 * np.exp(-x * 20) * np.sin(2 * np.pi * 900 * x))
    x = seg(1.0); add(S_[7] + tl(7, 0.55), 0.25 * np.exp(-x * 3) * (np.sin(2 * np.pi * 784 * x) + np.sin(2 * np.pi * 1175 * x)) / 2)   # medalla
    x = seg(0.8); add(S_[16] + 0.2, 0.25 * np.exp(-x * 4) * np.sin(2 * np.pi * (300 + 300 * x) * x))
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
