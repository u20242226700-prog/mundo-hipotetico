#!/usr/bin/env python3
"""LA RULETA DE NICO · T3: DINOSAURIOS · Capítulo 2/3.
Nico eligió la 2 (barro): el barro tapa el olor a bloqueador y el T-Rex se va. La ruleta cae en ??? = LLUVIA:
el aguacero lava el barro y el T-Rex vuelve. Llegan al río crecido; al otro lado está la manada de Trici.
Dato real: en Montana se hallaron 3 tricerátops jóvenes juntos (Mathews et al. 2009).
Dilema: 1 lanzar el bloqueador lejos / 2 que Trici llame a gritos a su manada."""
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
VOZ_F = sorted(f for f in os.listdir(VOZ_DIR) if f.endswith(".wav"))
VOZ = [wavfile.read(f"{VOZ_DIR}/{f}")[1].astype(np.float32) / 32768 for f in VOZ_F]
SR = 44100; LEAD = 0.08
DURS = [len(v) / SR + LEAD + 0.16 for v in VOZ]
ENV = []
for v in VOZ:
    hop = SR // 60
    e = np.array([np.sqrt(np.mean(v[i:i + hop] ** 2)) for i in range(0, len(v), hop)])
    e = e / (np.percentile(e, 95) + 1e-6); ENV.append(np.convolve(e, np.ones(3) / 3, mode="same"))
def boca(k, t):
    i = int((t - LEAD) * 60)
    return float(np.clip(ENV[k][i] * 1.15 - 0.12, 0, 1)) if 0 <= i < len(ENV[k]) else 0.0


CHUNKS = [
    [("Antes, en", []), ("La Ruleta de Nico:", ["Ruleta"]), ("un T-Rex que", ["T-Rex"]), ("encuentra todo", []), ("por el olor…", ["olor…"]), ("y Nico, que", []), ("huele a bloqueador", ["bloqueador"])],
    [("Nico eligió", []), ("la opción dos:", ["dos:"]), ("¡al barro!", ["barro!"])],
    [("¡Trici,", []), ("al barro!", ["barro!"]), ("¡Rápido,", []), ("revuélcate!", ["revuélcate!"])],
    [("¡Iiiu!", ["¡Iiiu!"]), ("¡Está frío", ["frío"]), ("y huele horrible!", ["horrible!"])],
    [("¡Exacto!", ["¡Exacto!"]), ("Si huele horrible…", ["horrible…"]), ("ya no huele", []), ("a bloqueador", ["bloqueador"])],
    [("Se quedan quietos,", ["quietos,"]), ("como dos estatuas", []), ("de barro…", ["barro…"]), ("y el T-Rex llega", ["T-Rex"])],
    [("Sniff…", ["Sniff…"]), ("sniff…", ["sniff…"]), ("¿Dónde está…", []), ("el olor", []), ("a playa?", ["playa?"])],
    [("Lo olfatea…", ["olfatea…"]), ("a un centímetro", ["centímetro"]), ("de la nariz", []), ("de Nico", [])],
    [("Mmm…", []), ("solo barro.", ["barro."]), ("Qué asco", ["asco"])],
    [("¡Y se va!", ["va!"]), ("¡Funcionó!", ["¡Funcionó!"])],
    [("¡Trici,", []), ("lo logramos!", ["logramos!"]), ("¡Somos los reyes", ["reyes"]), ("del barro!", ["barro!"])],
    [("Pero la ruleta", ["ruleta"]), ("vuelve a girar…", []), ("gira, gira…", ["gira…"]), ("¡y cae en", []), ("el misterio!", ["misterio!"]), ("¡LLUVIA!", ["¡LLUVIA!"])],
    [("Cae un aguacero", ["aguacero"]), ("prehistórico…", []), ("y la lluvia", []), ("les lava", []), ("todo el barro", ["barro"])],
    [("¡Nico, mira!", []), ("¡Ya no estamos", []), ("sucios!", ["sucios!"])],
    [("No, no, no…", []), ("¡eso es malo!", ["malo!"]), ("¡Vuelvo a oler", []), ("a bloqueador!", ["bloqueador!"])],
    [("Y a lo lejos", []), ("se oye un rugido", ["rugido"]), ("que ya conocen", [])],
    [("¡Grrr!", ["¡Grrr!"]), ("¡Ahí está", []), ("otra vez…", []), ("el olor", []), ("a playa!", ["playa!"])],
    [("Corren hasta", []), ("la orilla del río…", ["río…"]), ("y al otro lado…", []), ("¡está la manada", ["manada"]), ("de Trici!", ["Trici!"])],
    [("Dato real:", ["real:"]), ("en Montana", ["Montana"]), ("encontraron tres", ["tres"]), ("tricerátops jóvenes", ["tricerátops"]), ("enterrados juntos.", ["juntos."]), ("Los bebés", []), ("quizá andaban", []), ("en grupo", ["grupo"])],
    [("¡Mamá!", ["¡Mamá!"]), ("¡Mamááá!", ["¡Mamááá!"]), ("¡Estoy aquí!", ["aquí!"])],
    [("Pero el río", []), ("está crecido…", ["crecido…"]), ("y el T-Rex", ["T-Rex"]), ("está a diez pasos", ["diez"])],
    [("Tengo una", []), ("idea loca…", ["loca…"]), ("y otra todavía", []), ("más loca", ["loca"])],
    [("¿Qué hace Nico?", ["Nico?"]), ("Uno:", ["Uno:"]), ("lanzar el bloqueador", ["bloqueador"]), ("lejos, para que", []), ("el T-Rex", []), ("siga el olor.", ["olor."]), ("Dos:", ["Dos:"]), ("que Trici llame", ["Trici"]), ("a gritos", ["gritos"]), ("a su manada", ["manada"])],
    [("¿Uno o dos?", ["Uno", "dos?"]), ("Comenta,", ["Comenta,"]), ("y en el capítulo final", ["final"]), ("verás si", []), ("elegiste bien.", ["bien."]), ("Nos vemos en otro", []), ("mundo hipotético", ["hipotético"])],
]
RK = 11
DURS[11] += 0.5; DURS[22] += 0.45; DURS[23] += 0.4
STARTS = np.cumsum([0] + DURS).tolist(); TOTAL = STARTS[-1]
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
def escenario_ruleta(dr, t, luces=1.0):
    dr.rrect(-400, -400, 1480, 2400, 0, (34, 18, 52))
    for k in range(9):   # paneles de la pared
        x = -60 + k * 150
        dr.rrect(x, 200, x + 120, 1250, 20, (44, 24, 66))
    dr.ell(540, 1520, 820, 210, (58, 30, 86))
    dr.ell(540, 1510, 700, 160, (78, 42, 112))
    dr.rrect(-400, 1600, 1480, 2400, 0, (24, 12, 36))
    for sx in (-1, 1):   # telones
        for k in range(5):
            x0 = (540 + sx * 560) + sx * k * 70
            dr.poly([(x0, -100), (x0 + sx * 90, -100), (x0 + sx * 60 + 20 * math.sin(t + k), 1800), (x0 - sx * 10, 1800)], (160, 26, 40) if k % 2 else (130, 18, 32))
    dr.rrect(-400, -100, 1480, 60, 0, (130, 18, 32))
    if luces > 0.5 and dr.cam.z < 1.1:
        dr.text(540, 250, "LA RULETA", 120, (255, 230, 90), stroke=6)
        dr.text(540, 370, "DE NICO", 120, (90, 236, 255), stroke=6)

SEG = [("VOLCÁN", (230, 80, 50)), ("PIRATAS", (40, 186, 204)), ("???", (30, 26, 40)), ("TIBURONES", (60, 110, 200)),
       ("DINOS", (90, 170, 70)), ("ESPACIO", (110, 70, 190)), ("ZOMBIS", (120, 160, 90)), ("HIELO", (170, 220, 240))]
def ruleta(dr, cx, cy, r, ang, t, glow_seg=None):
    dr.ell(cx, cy, r * 1.12, r * 1.12, (60, 40, 30))
    dr.ell(cx, cy, r * 1.06, r * 1.06, (230, 190, 60))
    for i, (name, col) in enumerate(SEG):
        a0 = -90 - 22.5 + i * 45 + ang
        c = col if glow_seg != i or int(t * 8) % 2 else (255, 255, 255)
        dr.pie(cx, cy, r, a0, a0 + 45, c)
    for i, (name, col) in enumerate(SEG):
        a = math.radians(-90 + i * 45 + ang)
        tx, ty = cx + math.cos(a) * r * 0.64, cy + math.sin(a) * r * 0.64
        dr.text(tx, ty, name, 28 if len(name) > 6 else 36, (255, 255, 255), stroke=4)
    for k in range(16):
        a = math.radians(k * 22.5 + ang * 0.0)
        on = (int(t * 10) + k) % 2 == 0
        dr.ell(cx + math.cos(a) * r * 1.09, cy + math.sin(a) * r * 1.09, r * 0.035, r * 0.035, (255, 245, 180) if on else (150, 110, 40), nolin=True)
    dr.ell(cx, cy, r * 0.16, r * 0.16, (230, 190, 60))
    dr.ell(cx, cy, r * 0.08, r * 0.08, TURQ)
    dr.poly([(cx - r * 0.13, cy - r * 1.22), (cx + r * 0.13, cy - r * 1.22), (cx, cy - r * 0.95)], (230, 40, 50))

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
    f = font(size * k)
    lay = Image.new("RGBA", (int(f.getlength(txt) + 140), int(size * k * 1.7)), (0, 0, 0, 0))
    ImageDraw.Draw(lay).text((70, 16), txt, font=f, fill=col + (255,), stroke_width=int(15 * k), stroke_fill=INK)
    lay = lay.rotate(ang, resample=Image.BICUBIC, expand=True)
    img.paste(lay, (int(x - lay.width / 2), int(y - lay.height / 2)), lay)

def tarjeta_nombre(img, t, nombre, sub):
    k = eob(t / 0.3)
    lay = Image.new("RGBA", (W, 420), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    off = (1 - k) * -W
    d.polygon([(off, 80), (off + W, 20), (off + W, 300), (off, 360)], fill=(230, 40, 50, 255), outline=INK, width=10)
    d.text((off + 70, 120), nombre, font=font(92), fill=(255, 255, 255), stroke_width=8, stroke_fill=INK)
    d.text((off + 76, 236), sub, font=font(46), fill=(255, 222, 60), stroke_width=6, stroke_fill=INK)
    img.paste(lay, (0, 260), lay)


def D_(cam, bg=(0, 0, 0)): return D(cam, bg)
def oscuro(f, k=0.3, tint=(0.75, 0.85, 1.25)): return np.clip(f * k * np.array(tint, np.float32), 0, 255)
def rojo(f, a):   # luz de alarma
    return np.clip(f * np.array([1.0 + 0.25 * a, 1 - 0.45 * a, 1 - 0.45 * a], np.float32), 0, 255)

# ------------------------------------------------------------ selva prehistórica
SKY = [(116, 196, 226), (150, 210, 228), (190, 222, 214), (232, 228, 180), (250, 214, 150)]
def cielo(dr, y0=-900, y1=1000):
    n = len(SKY); h = (y1 - y0) / n
    for k, c in enumerate(SKY): dr.rrect(-600, y0 + k * h, 1700, y0 + (k + 1) * h + 2, 0, c, nolin=True)

def volcan(dr, x, y, s, t):
    S = lambda v: v * s
    dr.poly([(x - S(420), y), (x - S(70), y - S(380)), (x + S(70), y - S(380)), (x + S(420), y)], (150, 120, 120))
    dr.poly([(x, y - S(380)), (x + S(70), y - S(380)), (x + S(420), y), (x + S(120), y)], (120, 94, 100))
    dr.poly([(x - S(70), y - S(380)), (x + S(70), y - S(380)), (x + S(40), y - S(330)), (x - S(40), y - S(330))], (240, 110, 60))
    for k in range(5):   # humo
        u = (t * 0.15 + k / 5) % 1
        dr.ell(x + S(40) * math.sin(u * 4 + k) + S(120) * u, y - S(420) - S(500) * u, S(60 + 90 * u), S(50 + 70 * u), (226, 222, 216), nolin=True)

def montanas(dr, y, cols=((120, 170, 160), (96, 146, 140))):
    for k, (x, w, h) in enumerate(((-100, 520, 420), (380, 600, 520), (900, 560, 380))):
        dr.poly([(x - w / 2, y), (x, y - h), (x + w / 2, y)], cols[0], nolin=True)
        dr.poly([(x, y - h), (x + w / 2, y), (x + w * 0.1, y)], cols[1], nolin=True)

def pterodactilo(dr, x, y, s, t, ph=0.0):
    S = lambda v: v * s
    f = math.sin(t * 6 + ph)
    dr.poly([(x - S(160), y - S(60) * f), (x, y), (x + S(160), y - S(60) * f), (x + S(30), y + S(20)), (x - S(30), y + S(20))], (90, 70, 90), nolin=True)
    dr.poly([(x + S(20), y - S(10)), (x + S(110), y + S(10)), (x + S(20), y + S(20))], (90, 70, 90), nolin=True)

def fronda(dr, x0, y0, ang, L, col, col2, t=0.0, n=9, ph=0.0, w=1.0):
    """Hoja de helecho: tallo curvo con foliolos a los lados."""
    pts = []
    for i in range(n + 1):
        u = i / n
        a = math.radians(ang + 40 * u * u + 4 * math.sin(t * 1.5 + ph))
        if i == 0: x, y = x0, y0
        else: x, y = pts[-1][0] + math.sin(a) * L / n, pts[-1][1] - math.cos(a) * L / n
        pts.append((x, y))
    for i in range(1, n):
        u = i / n; (x, y) = pts[i]
        a = math.radians(ang + 40 * u * u)
        ln = L * 0.2 * (1 - u * 0.75) * w
        for sd in (-1, 1):
            b = a + sd * 1.2
            ex, ey = x + math.sin(b) * ln, y - math.cos(b) * ln
            dr.poly([(x, y), ((x + ex) / 2 + math.cos(b) * ln * 0.18, (y + ey) / 2 + math.sin(b) * ln * 0.18), (ex, ey), ((x + ex) / 2 - math.cos(b) * ln * 0.18, (y + ey) / 2 - math.sin(b) * ln * 0.18)], col if sd < 0 else col2)
    dr.line(pts, (60, 110, 50), max(3, L * 0.018))

def helecho(dr, x, y, s, t, col=(70, 160, 70), col2=(50, 130, 60), ph=0.0):
    for k, a in enumerate((-70, -40, -12, 15, 42, 68)):
        fronda(dr, x, y, a, 520 * s * (0.8 + 0.2 * (k % 2)), col, col2, t, ph=ph + k)

def palma(dr, x, y, s, t, ph=0.0, col=(60, 140, 70)):
    """Cícada / palmera prehistórica: tronco con escamas + copa de frondas."""
    S = lambda v: v * s
    sw = S(12) * math.sin(t * 0.8 + ph)
    dr.poly([(x - S(40), y), (x + S(40), y), (x + S(26) + sw, y - S(900)), (x - S(26) + sw, y - S(900))], (140, 96, 60))
    for k in range(12):
        yy = y - S(40) - k * S(72); xx = x + sw * k / 12
        dr.poly([(xx - S(36), yy), (xx + S(36), yy), (xx, yy - S(40))], (118, 78, 48))
    for k, a in enumerate((-100, -65, -30, 0, 30, 65, 100)):
        fronda(dr, x + sw, y - S(900), a, S(560), col, (col[0] - 18, col[1] - 26, col[2] - 10), t, n=8, ph=ph + k, w=0.8)

def selva_bg(dr, t, hor=1050, ptero=True, volc=True, trees=True):
    cielo(dr, -900, hor)
    if volc: volcan(dr, 820, hor - 40, 0.7, t)
    montanas(dr, hor)
    if ptero:
        for k in range(2): pterodactilo(dr, (200 + k * 380 + t * 60) % 1500 - 200, 300 + k * 120, 0.35 - k * 0.08, t, k)
    dr.rrect(-600, hor - 60, 1700, hor + 40, 0, (90, 150, 110), nolin=True)   # selva lejana
    for k in range(14): dr.ell(-300 + k * 140, hor - 50, 110, 80, (76, 136, 98) if k % 2 else (86, 150, 104), nolin=True)
    dr.rrect(-600, hor, 1700, 2700, 0, (134, 172, 80))
    for k in range(9):   # manchas del suelo
        dr.ell(-200 + (k * 237) % 1500, hor + 120 + (k * 173) % 1300, 160, 40, (118, 156, 70))
    if trees:
        palma(dr, 70, hor + 200, 0.95, t, 0.0)
        palma(dr, 1010, hor + 260, 1.05, t, 1.7)
        helecho(dr, 300, hor + 80, 0.6, t, ph=2)
        helecho(dr, 840, hor + 100, 0.55, t, ph=4)

def helechos_frente(dr, t, y=1900, s=1.0):
    helecho(dr, -40, y, 1.0 * s, t, (46, 120, 56), (36, 100, 48), 0.5)
    helecho(dr, 1120, y + 30, 1.0 * s, t, (46, 120, 56), (36, 100, 48), 3.3)

def huella(dr, x, y, s, col=(96, 92, 46)):
    S = lambda v: v * s
    dr.ell(x, y, S(150), S(110), col)
    for a in (-35, 0, 35):
        r = math.radians(a)
        cx, cy = x + math.sin(r) * S(210), y - math.cos(r) * S(150)
        dr.poly([(x + math.sin(r - 0.25) * S(90), y - math.cos(r - 0.25) * S(70)), (cx + math.sin(r) * S(80), cy - math.cos(r) * S(70)),
                 (x + math.sin(r + 0.25) * S(90), y - math.cos(r + 0.25) * S(70))], col)

def rio(dr, t, y0, y1, col=(70, 150, 210)):
    dr.rrect(-600, y0, 1700, y1, 0, col)
    for k in range(8):
        x = -200 + ((k * 230 + t * 90) % 1600); y = y0 + 40 + (k * 97) % max(40, (y1 - y0 - 60))
        dr.line([(x, y), (x + 70, y - 8), (x + 140, y)], (170, 220, 245), 8, nolin=True)

def tronco(dr, x, y, s, t, ang=0.0):
    S = lambda v: v * s
    y = y + S(10) * math.sin(t * 2)
    dr.rrect(x - S(340), y - S(60), x + S(340), y + S(60), S(60), (140, 92, 52), True)
    for k in range(3): dr.line([(x - S(240) + k * S(170), y - S(40)), (x - S(170) + k * S(170), y - S(30))], (110, 70, 40), S(8))
    dr.ell(x + S(330), y, S(52), S(60), (196, 150, 96))
    dr.ell(x + S(330), y, S(30), S(36), (170, 124, 76))
    dr.ell(x - S(120), y - S(60), S(30), S(14), (80, 160, 70))

def barro(dr, x, y, s, t):
    S = lambda v: v * s
    dr.ell(x, y, S(360), S(110), (112, 80, 52))
    dr.ell(x - S(30), y - S(10), S(300), S(80), (130, 96, 62))
    for k in range(4):
        u = (t * 0.8 + k / 4) % 1
        r = S(18) * (0.3 + u)
        dr.ell(x - S(200) + k * S(130), y - S(20) + S(20) * (k % 2), r, r * 0.8, (150, 114, 76))

# ------------------------------------------------------------ TRICI (bebé tricerátops)
TRI = (246, 162, 92); TRI_D = (222, 128, 70); TRI_B = (252, 214, 160); FRILL = (232, 98, 96)
def trici(dr, x, y, s, t, mouth=0.0, face=1, expr="happy", look=(0, 0), walk=0.0, hop=0.0, sweat=False):
    """(x, y) = suelo. Mide ≈ 520*s de alto. face = 1 mira a la derecha."""
    S = lambda v: v * s
    F = lambda dx: x + face * S(dx)
    y = y - S(40) * abs(math.sin(hop * math.pi)) if hop else y
    by = y - S(170) + S(6) * math.sin(t * 3)
    # cola
    dr.poly([(F(-150), by - S(30)), (F(-330), by + S(40) + S(10) * math.sin(t * 4)), (F(-150), by + S(60))], TRI_D)
    # patas
    for k, dx in enumerate((-110, -40, 60, 130)):
        sw = S(16) * math.sin(walk * 9 + k * 1.6) if walk else 0
        dr.rrect(F(dx) - S(30) + sw, by + S(30), F(dx) + S(30) + sw, y, S(20), TRI_D if k % 2 else TRI)
        dr.ell(F(dx) + sw, y - S(6), S(38), S(16), (240, 230, 210))
    # cuerpo
    dr.ell(x, by, S(210), S(140), TRI, shade=True)
    dr.ell(F(20), by + S(60), S(150), S(60), TRI_B)
    for k in range(3): dr.ell(F(-90 + k * 70), by - S(90), S(26), S(16), TRI_D)
    # gola (frill) detrás de la cabeza
    hx, hy = F(190), by - S(130)
    dr.ell(hx - face * S(40), hy - S(40), S(170), S(160), FRILL)
    for k in range(7):
        a = math.radians(-170 + k * 27)
        dr.ell(hx - face * S(40) + math.cos(a) * S(150), hy - S(40) + math.sin(a) * S(140), S(20), S(20), (250, 200, 80))
    # cabeza
    dr.ell(hx, hy, S(130), S(118), TRI, shade=True)
    dr.ell(hx + face * S(90), hy + S(40), S(80), S(60), TRI_B)   # hocico
    dr.poly([(hx + face * S(150), hy + S(10)), (hx + face * S(200), hy + S(45)), (hx + face * S(150), hy + S(80))], (230, 200, 160))   # pico
    dr.poly([(hx + face * S(95), hy - S(20)), (hx + face * S(130), hy - S(70)), (hx + face * S(125), hy - S(10))], (255, 246, 220))   # cuerno nariz
    for dx in (-40, 40):   # cuernitos
        dr.poly([(hx + S(dx) - S(16), hy - S(100)), (hx + S(dx) + face * S(10), hy - S(160)), (hx + S(dx) + S(16), hy - S(98))], (255, 246, 220))
    # ojos grandes
    blink = (t % 2.9) < 0.12
    for k, dx in enumerate((-30, 50)):
        ex, ey = hx + face * S(dx) - S(10), hy - S(30)
        if expr == "happy_eyes" or (blink and expr != "shock"):
            dr.chord(ex, ey + S(6), S(26), S(20), 180, 360, (24, 18, 26)); dr.chord(ex, ey + S(12), S(22), S(14), 180, 360, TRI)
            continue
        big = 1.2 if expr in ("shock", "scared") else 1.0
        dr.ell(ex, ey, S(30) * big, S(38) * big, (255, 255, 255))
        px, py = ex + (look[0] + face * 0.3) * S(9), ey + look[1] * S(10)
        dr.ell(px, py, S(15), S(19), (24, 18, 26))
        dr.ell(px - S(5), py - S(7), S(6), S(6), (255, 255, 255))
        if expr in ("scared", "sad"):
            dr.line([(ex - S(26), ey - S(48) + (S(10) if dx < 0 else -S(4))), (ex + S(26), ey - S(48) + (-S(4) if dx < 0 else S(10)))], TRI_D, S(9))
    dr.ell(hx + face * S(10), hy + S(30), S(20), S(12), (250, 140, 150))   # cachete
    mo = clamp(mouth)
    if mo > 0.06 or expr in ("shock", "scared"):
        mo = max(mo, 0.5 if expr in ("shock", "scared") else 0)
        dr.ell(hx + face * S(110), hy + S(78), S(32), S(8 + 20 * mo), (120, 30, 40))
    else:
        dr.line([(hx + face * S(80), hy + S(72)), (hx + face * S(110), hy + S(82)), (hx + face * S(140), hy + S(74))], (120, 30, 40), S(7))
    if sweat:
        k = (t * 1.2) % 1
        dr.ell(hx - face * S(90), hy - S(60) + S(50) * k, S(12), S(17), (140, 210, 255))
    return (hx, hy)

# ------------------------------------------------------------ T-REX
RX = (112, 150, 72); RX_D = (86, 120, 56); RX_B = (214, 210, 140); RX_S = (74, 104, 48)
def trex_cabeza(dr, hx, hy, s, t, mouth=0.0, face=-1, sniff=0.0, eye_look=(0, 0), angry=True):
    """Cabeza del T-Rex. (hx, hy) = centro del cráneo. face=-1 mira a la izquierda."""
    S = lambda v: v * s
    F = lambda dx: hx + face * S(dx)
    mo = clamp(mouth)
    ja = 0.08 + 0.55 * mo
    # mandíbula inferior (rota hacia abajo)
    jx0, jy0 = F(-120), hy + S(40)
    def J(dx, dy):   # punto de la mandíbula rotado alrededor de la bisagra
        a = ja
        return (jx0 + face * (dx * math.cos(a) - dy * math.sin(a)) * s, jy0 + (dx * math.sin(a) + dy * math.cos(a)) * s)
    jaw = [J(0, 0), J(420, -10), J(440, 30), J(380, 70), J(60, 90), J(-30, 60)]
    dr.poly([J(10, 0), J(410, -6), J(400, 50), J(40, 70)], (150, 40, 50))   # boca por dentro
    for k in range(6):   # dientes de abajo
        bx, by_ = J(80 + k * 55, -4)
        dr.poly([(bx - S(12), by_), (bx + face * S(4), by_ - S(34)), (bx + S(12), by_)], (250, 248, 232))
    dr.poly(jaw, RX_B)
    # cráneo superior
    sk = [(F(-230), hy - S(130)), (F(-60), hy - S(200)), (F(150), hy - S(180)), (F(310), hy - S(120)), (F(370), hy - S(40)), (F(360), hy + S(30)),
          (F(-120), hy + S(55)), (F(-250), hy + S(10))]
    dr.poly(sk, RX, shade=True)
    dr.ell(F(-120), hy - S(70), S(160), S(150), RX, shade=True)   # cráneo alto y redondo
    dr.ell(F(250), hy - S(60), S(130), S(100), RX)                 # hocico redondo
    dr.ell(F(250), hy - S(10), S(90), S(40), RX_B)
    for k in range(7):   # dientes de arriba
        tx = F(-60 + k * 58)
        dr.poly([(tx - S(13), hy + S(28)), (tx + face * S(2), hy + S(28) + S(40)), (tx + S(13), hy + S(28))], (250, 248, 232))
    dr.poly([(F(-120), hy + S(30)), (F(350), hy + S(20)), (F(352), hy + S(36)), (F(-120), hy + S(52))], RX_D)
    for k in range(4): dr.ell(F(-150 + k * 60), hy - S(110) + k * S(8), S(26), S(14), RX_S)   # rayas
    # fosa nasal (se abre al olfatear)
    nr = S(16 + 10 * sniff)
    dr.ell(F(340), hy - S(100), nr, nr * 0.7, (40, 40, 30))
    # ojo pequeño con ceja dura
    ex, ey = F(40), hy - S(110)
    dr.ell(ex, ey, S(62), S(56), (255, 255, 255))
    dr.ell(ex + face * S(8) + eye_look[0] * S(14), ey + eye_look[1] * S(10), S(34), S(34), (250, 200, 50))
    dr.ell(ex + face * S(8) + eye_look[0] * S(14), ey + eye_look[1] * S(10), S(10), S(28), (24, 18, 26))
    if angry: dr.poly([(F(-40), hy - S(185)), (F(110), hy - S(150)), (F(100), hy - S(120)), (F(-40), hy - S(150))], RX_D)
    return (F(340), hy - S(100))

def trex(dr, x, y, s, t, mouth=0.0, face=-1, sniff=0.0, step=0.0, eye_look=(0, 0)):
    """(x, y) = pies. Alto ≈ 1500*s. Devuelve la posición de la nariz."""
    S = lambda v: v * s
    F = lambda dx: x + face * S(dx)
    bob = S(20) * abs(math.sin(step * math.pi)) if step else 0
    by = y - S(820) - bob
    # cola
    dr.poly([(F(-120), by - S(140)), (F(-820), by - S(60) + S(30) * math.sin(t * 1.5)), (F(-860), by - S(30) + S(30) * math.sin(t * 1.5)), (F(-120), by + S(150))], RX_D)
    # pierna de atrás
    l2 = S(40) * math.sin(step * math.pi * 2) if step else 0
    dr.ell(F(-80), by + S(160), S(170), S(230), RX_D)
    dr.poly([(F(-120) + l2, by + S(320)), (F(-30) + l2, by + S(320)), (F(-10) + l2, y - S(20)), (F(-110) + l2, y - S(20))], RX_D)
    dr.ell(F(-40) + l2, y - S(25), S(110), S(36), RX_S)
    # cuerpo
    dr.ell(x, by, S(380), S(300), RX, shade=True)
    dr.ell(F(110), by + S(90), S(240), S(170), RX_B)
    for k in range(5): dr.poly([(F(-260 + k * 90), by - S(260) + k * S(10)), (F(-210 + k * 90), by - S(300) + k * S(10)), (F(-190 + k * 90), by - S(230) + k * S(10))], RX_S)
    # pierna de adelante
    dr.ell(F(40), by + S(180), S(190), S(250), RX, shade=True)
    dr.poly([(F(0) - l2, by + S(340)), (F(100) - l2, by + S(340)), (F(120) - l2, y - S(20)), (F(10) - l2, y - S(20))], RX)
    dr.ell(F(80) - l2, y - S(25), S(120), S(38), RX_S)
    for k in range(3): dr.poly([(F(150 + k * 30) - l2, y - S(40)), (F(200 + k * 20) - l2, y - S(10)), (F(150 + k * 30) - l2, y - S(5))], (250, 246, 230))
    # cuello
    dr.poly([(F(160), by - S(240)), (F(300), by - S(470)), (F(470), by - S(380)), (F(340), by - S(40))], RX)
    # bracitos (el chiste)
    for k in range(2):
        ax, ay = F(300 + k * 30), by - S(40) + k * S(30)
        wig = math.sin(t * 7 + k) * S(14)
        dr.line([(ax, ay), (ax + face * S(70), ay + S(30) + wig), (ax + face * S(110), ay + S(10) + wig)], RX_D if k else RX, S(26))
    return trex_cabeza(dr, F(440), by - S(470), s, t, mouth, face, sniff, eye_look)

def olor(img, x, y, t, col=(255, 236, 140), n=3, ang=0.0, size=1.0):
    """Líneas onduladas de olor."""
    d = ImageDraw.Draw(img)
    for k in range(n):
        u = (t * 0.8 + k / n) % 1
        pts = []
        for i in range(12):
            v = i / 11
            px = x + math.cos(ang) * v * 260 * size - math.sin(ang) * 30 * math.sin(v * 9 + t * 6 + k) * size + (k - 1) * 60 * size * math.sin(ang)
            py = y + math.sin(ang) * v * 260 * size + math.cos(ang) * 30 * math.sin(v * 9 + t * 6 + k) * size - u * 80 * size + (k - 1) * 60 * size * math.cos(ang)
            pts.append((px, py))
        a = 1 - abs(u - 0.5) * 2
        if a > 0.15:
            d.line(pts, fill=INK, width=int(18 * size), joint="curve")
            d.line(pts, fill=col, width=int(9 * size), joint="curve")

def bloqueador(dr, x, y, s, t):
    S = lambda v: v * s
    dr.rrect(x - S(60), y - S(140), x + S(60), y + S(130), S(40), (250, 220, 60), True)
    dr.rrect(x - S(30), y - S(190), x + S(30), y - S(130), S(8), (240, 110, 60))
    dr.ell(x, y - S(20), S(42), S(42), (255, 150, 40))
    dr.text(x, y + S(70), "FPS 50", S(28), (40, 30, 30))

def badge(img, T):
    d = ImageDraw.Draw(img)
    f = font(36)
    d.rounded_rectangle([36, 110, 36 + f.getlength("LA RULETA DE NICO") + 44, 170], radius=16, fill=(230, 40, 50), outline=INK, width=5)
    d.text((58, 140), "LA RULETA DE NICO", font=f, fill=(255, 255, 255), anchor="lm")
    txt = "CAPÍTULO 2/3"
    x1 = W - 36; x0 = x1 - f.getlength(txt) - 44
    d.rounded_rectangle([x0, 110, x1, 170], radius=16, fill=(255, 214, 10), outline=INK, width=5)
    d.text((x0 + 22, 140), txt, font=f, fill=INK, anchor="lm")
    if True:
        f2 = font(30); t2 = "DINOSAURIOS"
        d.rounded_rectangle([36, 182, 36 + f2.getlength(t2) + 40, 230], radius=14, fill=(110, 200, 90), outline=INK, width=4)
        d.text((56, 206), t2, font=f2, fill=INK, anchor="lm")

def ang_ruleta(T):
    t0, t1 = STARTS[RK] + LEAD + len(VOZ[RK]) / SR * 0.35, STARTS[RK] + LEAD + len(VOZ[RK]) / SR * 0.82
    final = -90 - 360 * 4
    if T < t0: return 0.0
    u = clamp((T - t0) / (t1 - t0))
    return final * (1 - (1 - u) ** 3)

def temblor(T):
    """Pasos del T-Rex (para sacudir la cámara)."""
    return 0.0

# ------------------------------------------------------------ extras del capítulo 2
MUD = (122, 86, 54); MUD2 = (98, 68, 42)
NICO_MUD = [(150, 760, 40), (165, 590, 34), (-165, 560, 34), (-70, 310, 70), (80, 240, 66),
            (10, 400, 52), (-90, 150, 50), (85, 100, 48), (-40, 50, 44), (55, 25, 40), (-150, 330, 38), (150, 330, 38)]
def embarrar(dr, x, y, s, amt=1.0, t=0.0):
    """Manchas de barro sobre Nico (amt 0..1: la lluvia las va quitando)."""
    n = int(round(len(NICO_MUD) * clamp(amt)))
    for k, (dx, dy, r) in enumerate(NICO_MUD[:n]):
        drip = 8 * s * math.sin(t * 2 + k)
        dr.ell(x + dx * s, y - dy * s + drip, r * s * 1.15, r * s * 0.6, MUD if k % 2 else MUD2)
TRI_MUD = [(-120, -40, 60), (0, -90, 70), (110, 0, 60), (-40, 40, 50), (60, -170, 45), (-200, 20, 40)]
def embarrar_tri(dr, x, y, s, face=1, amt=1.0):
    n = int(round(len(TRI_MUD) * clamp(amt)))
    by = y - 170 * s
    for k, (dx, dy, r) in enumerate(TRI_MUD[:n]):
        dr.ell(x + face * dx * s, by + dy * s, r * s, r * s * 0.8, MUD if k % 2 else MUD2)
def mojar(f, a=1.0):   # cielo de tormenta: más oscuro y azul
    return np.clip(f * (1 - 0.32 * a) * np.array([0.9, 0.95, 1.12], np.float32) ** a, 0, 255)
def lluvia(img, t, a=1.0, n=90):
    d = ImageDraw.Draw(img)
    for k in range(int(n * a)):
        x0 = (k * 137 + t * 220) % (W + 300) - 150
        y0 = ((k * 263) % H + t * 2400 + k * 31) % (H + 200) - 100
        d.line([(x0, y0), (x0 - 28, y0 + 90)], fill=(200, 225, 255), width=5)
    for k in range(int(10 * a)):   # salpicaduras
        u = (t * 3 + k * 0.37) % 1
        x = (k * 211) % W; y = 1500 + (k * 97) % 400
        r = 10 + 40 * u
        d.ellipse([x - r, y - r * 0.3, x + r, y + r * 0.3], outline=(210, 230, 255), width=4)
def corona(dr, x, y, s):
    S = lambda v: v * s
    dr.poly([(x - S(110), y), (x - S(120), y - S(110)), (x - S(55), y - S(50)), (x, y - S(130)), (x + S(55), y - S(50)), (x + S(120), y - S(110)), (x + S(110), y)], MUD)
    dr.ell(x, y - S(130), S(18), S(18), (255, 222, 40))
def charco_barro(dr, x, y, s, t):
    barro(dr, x, y, s, t)

# ------------------------------------------------------------ planos
SHOTS = []
def shot(fn): SHOTS.append(fn); return fn
def tl(k, frac): return LEAD + len(VOZ[k]) / SR * frac
EXP = "explorador"

@shot
def s01(t, D, T):    # Antes en La Ruleta de Nico: T-Rex que huele + Nico huele a bloqueador
    u = t / D
    cam = Cam(540, 1080, lerp(1.05, 1.15, ease(u)))
    dr = D_(cam); selva_bg(dr, t, hor=1000, trees=False)
    trex(dr, 900, 1900, 0.6, t, mouth=0.2, face=-1, sniff=abs(math.sin(t * 8)), eye_look=(-0.6, 0.4))
    trici(dr, 200, 1820, 0.36, t, face=1, expr="scared", sweat=True)
    nico(dr, 430, 1840, 0.55, t, traje=EXP, arms=(20, 120) if u > 0.6 else (60, 60), elbows=(0, 60), expr="nervous", look=(1, -0.3), sweat=True)
    if u > 0.6: bloqueador(dr, 640, 1420, 0.6, t)
    f = oscuro(tinta(dr), 0.85, (1.0, 0.95, 0.9)); img = acabado(f, T); d = ImageDraw.Draw(img)
    d.polygon([(0, 270), (W, 230), (W, 400), (0, 440)], fill=(40, 30, 60), outline=INK, width=8)
    d.text((540, 335), "ANTES EN LA RULETA…", font=font(70), fill=(255, 255, 255), anchor="mm", stroke_width=7, stroke_fill=INK)
    olor(img, 420, 900, t, (255, 236, 140), 3, -0.3, 1.0)
    return img, 0

@shot
def s02(t, D, T):    # Nico eligió la 2: ¡al barro! (salto + salpicón)
    u = t / D
    cam = Cam(540, 1150, lerp(1.1, 1.25, ease(u)))
    dr = D_(cam); selva_bg(dr, t, hor=1000, trees=False)
    barro(dr, 540, 1700, 1.5, t)
    jump = clamp(u / 0.55)
    yy = 1700 - 520 * math.sin(jump * math.pi) if jump < 1 else 1760
    nico(dr, 600, yy, 0.55, t, traje=EXP, arms=(165, 165), elbows=(0, 0), expr="shock" if jump < 1 else "happy", look=(0, 0.6))
    trici(dr, 380, yy + 20, 0.34, t, face=1, expr="shock" if jump < 1 else "happy_eyes")
    if jump >= 1: embarrar(dr, 600, 1760, 0.55, 0.7, t)
    f = tinta(dr); img = acabado(f, T); d = ImageDraw.Draw(img)
    r = 95 * (1 + 0.06 * math.sin(t * 8))
    d.ellipse([540 - r, 520 - r, 540 + r, 520 + r], fill=(255, 214, 10), outline=INK, width=10)
    d.text((540, 520), "2", font=font(130), fill=INK, anchor="mm")
    if jump >= 1: burst(img, "¡SPLASH!", 540, 900, 120, t - 0.55 * D, col=(200, 150, 100), ang=-6)
    return img, (8 * math.exp(-(t - 0.55 * D) * 6) if jump >= 1 else 0)

@shot
def s03(t, D, T):    # Nico (embarrado): ¡Trici, al barro! ¡revuélcate!
    cam = Cam(540, 1150, 1.7)
    dr = D_(cam); selva_bg(dr, t, hor=1000, trees=False)
    nico(dr, 540, 1760, 0.66, t, traje=EXP, arms=(150, 40), elbows=(-20, 60), expr="happy", mouth=boca(2, t), look=(-0.7, 0.2))
    embarrar(dr, 540, 1760, 0.66, 0.85, t)
    barro(dr, 540, 1800, 1.6, t)
    f = tinta(dr); img = acabado(f, T)
    burst(img, "¡AL BARRO!", 540, 470, 110, t - 0.1, col=(200, 150, 100), ang=-6)
    return img, 0

@shot
def s04(t, D, T):    # Trici: ¡Iiiu! está frío y huele horrible
    cam = Cam(540, 1150, 1.6)
    dr = D_(cam); selva_bg(dr, t, hor=1000, trees=False)
    sh = math.sin(t * 30) * 8 if t < 0.8 else 0
    trici(dr, 520 + sh, 1700, 0.72, t, mouth=boca(3, t), face=1, expr="scared", look=(0, -0.5))
    embarrar_tri(dr, 520 + sh, 1700, 0.72, 1, 1.0)
    barro(dr, 520, 1740, 1.4, t)
    f = tinta(dr); img = acabado(f, T)
    olor(img, 300, 700, t, (170, 210, 90), 3, -1.3, 1.1)
    burst(img, "¡IIIU!", 780, 520, 130, t - 0.05, col=(170, 230, 90), ang=8)
    return img, 2 if t < 0.8 else 0

@shot
def s05(t, D, T):    # Nico: ¡exacto! si huele horrible, ya no huele a bloqueador
    cam = Cam(500, 1100, 1.5)
    dr = D_(cam); selva_bg(dr, t, hor=1000, trees=False)
    nico(dr, 430, 1760, 0.66, t, traje=EXP, arms=(20, 140), elbows=(0, 60), expr="smug", mouth=boca(4, t), look=(0.6, -0.2))
    embarrar(dr, 430, 1760, 0.66, 1.0, t)
    bloqueador(dr, 820, 1250, 0.8, t)
    f = tinta(dr); img = acabado(f, T); d = ImageDraw.Draw(img)
    if t > tl(4, 0.5):
        X, Y = cam.p(820, 1230)
        d.line([(X - 140, Y - 180), (X + 140, Y + 180)], fill=INK, width=40); d.line([(X - 140, Y + 180), (X + 140, Y - 180)], fill=INK, width=40)
        d.line([(X - 140, Y - 180), (X + 140, Y + 180)], fill=(230, 40, 50), width=26); d.line([(X - 140, Y + 180), (X + 140, Y - 180)], fill=(230, 40, 50), width=26)
    burst(img, "OLOR: 0%", 760, 520, 80, t - 0.2, col=(110, 230, 110), ang=6)
    return img, 0

@shot
def s06(t, D, T):    # quietos como estatuas de barro… y el T-Rex llega (patas enormes entran)
    u = t / D
    cam = Cam(540, 1150, 1.2)
    dr = D_(cam); selva_bg(dr, t, hor=1000, trees=False)
    for k in range(2): helecho(dr, 120 + k * 840, 1500, 0.9, t, ph=k)
    nico(dr, 380, 1800, 0.5, t, traje=EXP, arms=(90, 90), elbows=(0, 0), expr="nervous", look=(1, 0), blink=False)
    embarrar(dr, 380, 1800, 0.5, 1.0, 0)
    trici(dr, 640, 1820, 0.34, t, face=1, expr="scared", look=(1, 0))
    embarrar_tri(dr, 640, 1820, 0.34, 1, 1.0)
    if u > 0.55:   # pata del T-Rex que entra
        k = ease((u - 0.55) / 0.35)
        px = lerp(1400, 960, k)
        dr.poly([(px - 90, 900), (px + 90, 900), (px + 110, 1880), (px - 80, 1880)], RX_D)
        dr.ell(px + 10, 1870, 190, 60, RX_S)
        for dx in (-140, -60, 30): dr.poly([(px + dx, 1860), (px + dx - 60, 1900), (px + dx + 10, 1905)], (250, 246, 230))
    f = tinta(dr); img = acabado(f, T)
    if u < 0.5: burst(img, "QUIETOS…", 540, 520, 100, t - 0.1, col=(200, 150, 100), ang=-4)
    if u > 0.9: burst(img, "¡PUM!", 760, 900, 130, t - 0.9 * D, col=(255, 140, 60), ang=8)
    return img, (9 * math.exp(-(t - 0.9 * D) * 6) if u > 0.9 else 0)

@shot
def s07(t, D, T):    # T-Rex: sniff… sniff… ¿dónde está el olor a playa?
    u = t / D
    cam = Cam(540, 1000, 1.0)
    dr = D_(cam); selva_bg(dr, t, hor=1250, trees=False)
    helecho(dr, 100, 1900, 1.4, t, ph=1); helecho(dr, 980, 1900, 1.4, t, ph=3)
    sn = abs(math.sin(t * 9)) if boca(6, t) < 0.2 else 0.3
    trex_cabeza(dr, lerp(640, 580, ease(u)), 1050, 1.25, t, mouth=boca(6, t) * 0.8, face=-1, sniff=sn, eye_look=(-0.6, 0.5))
    f = tinta(dr); img = acabado(f, T)
    burst(img, "SNIFF", 300, 600, 110, t - 0.2, col=(200, 240, 160), ang=-10)
    if u > 0.45: burst(img, "SNIFF", 340, 1350, 90, t - 0.45 * D, col=(200, 240, 160), ang=8)
    return img, 2 + 4 * boca(6, t)

@shot
def s08(t, D, T):    # a un centímetro de la nariz de Nico (primerísimo plano, tensión)
    u = t / D
    cam = Cam(lerp(620, 650, u), 1050, lerp(1.55, 1.8, ease(u)))
    dr = D_(cam); selva_bg(dr, t, hor=900, trees=False)
    nico(dr, 470, 1500, 0.62, t, traje=EXP, arms=(20, 20), elbows=(0, 0), expr="nervous", look=(1, 0), sweat=True, blink=False)
    embarrar(dr, 470, 1500, 0.62, 1.0, 0)
    trex_cabeza(dr, 960, 1060, 0.75, t, mouth=0.05, face=-1, sniff=abs(math.sin(t * 10)), eye_look=(-1, 0.4))
    f = tinta(dr); img = acabado(f, T); d = ImageDraw.Draw(img)
    d.rounded_rectangle([340, 470, 740, 570], radius=24, fill=(255, 255, 255), outline=INK, width=6)
    d.text((540, 520), "1 cm", font=font(60), fill=(230, 40, 50), anchor="mm")
    return img, 1.5

@shot
def s09(t, D, T):    # T-Rex: mmm… solo barro. qué asco
    cam = Cam(560, 1050, 1.15)
    dr = D_(cam); selva_bg(dr, t, hor=1200, trees=False)
    trex_cabeza(dr, 600, 1080, 1.15, t, mouth=boca(8, t) * 0.7, face=-1, sniff=0.2, eye_look=(0, -0.8), angry=False)
    f = tinta(dr); img = acabado(f, T)
    olor(img, 120, 1000, t, (170, 210, 90), 3, -0.2, 1.0)
    if t > tl(8, 0.5): burst(img, "¡PUAJ!", 780, 520, 130, t - tl(8, 0.5), col=(170, 230, 90), ang=8)
    return img, 0

@shot
def s10(t, D, T):    # ¡y se va! ¡funcionó!
    u = t / D
    cam = Cam(540, 1100, 1.05)
    dr = D_(cam); selva_bg(dr, t, hor=1000, trees=False)
    trex(dr, lerp(560, 900, u), 1450, 0.3, t, mouth=0.1, face=1, step=(t * 1.5) % 1)
    nico(dr, 380, 1820, 0.5, t, traje=EXP, arms=(150, 150) if u > 0.5 else (60, 60), elbows=(10, 10), expr="happy" if u > 0.5 else "nervous", look=(1, -0.2))
    embarrar(dr, 380, 1820, 0.5, 1.0, t)
    trici(dr, 660, 1840, 0.34, t, face=1, expr="happy_eyes" if u > 0.5 else "scared", hop=(t * 1.6) % 1 if u > 0.5 else 0)
    embarrar_tri(dr, 660, 1840, 0.34, 1, 1.0)
    helechos_frente(dr, t, 2080, 0.7)
    f = tinta(dr); img = acabado(f, T)
    if u > 0.45: burst(img, "¡FUNCIONÓ!", 540, 500, 110, t - 0.45 * D, col=(110, 230, 110), ang=-6)
    return img, 0

@shot
def s11(t, D, T):    # Nico: ¡somos los reyes del barro! (corona de barro)
    cam = Cam(540, 1300, 1.45)
    dr = D_(cam); selva_bg(dr, t, hor=1000, trees=False)
    nico(dr, 450, 1780, 0.64, t, traje=EXP, arms=(160, 120), elbows=(0, -30), expr="happy", mouth=boca(10, t), look=(0.5, -0.3))
    embarrar(dr, 450, 1780, 0.64, 1.0, t)
    corona(dr, 450, 1780 - 0.64 * 930, 0.6)
    trici(dr, 820, 1780, 0.42, t, face=-1, expr="happy_eyes", hop=(t * 1.6) % 1)
    embarrar_tri(dr, 820, 1780, 0.42, -1, 1.0)
    f = tinta(dr); img = acabado(f, T)
    burst(img, "¡REYES DEL BARRO!", 540, 470, 86, t - 0.3, col=(255, 222, 40), ang=-6)
    return img, 0

@shot
def s12(t, D, T):    # la ruleta vuelve a girar → ??? → ¡LLUVIA!
    stop = T > STARTS[RK] + tl(RK, 0.82)
    cam = Cam(540, 1000, lerp(1.0, 1.12, ease(t / D)))
    dr = D_(cam); escenario_ruleta(dr, t); ruleta(dr, 540, 1080, 300, ang_ruleta(T), t, glow_seg=2 if stop else None)
    f = tinta(dr)
    for x in (300, 780): add_cono(f, x, -50, 1700, 60, 520, (255, 236, 180), 0.3)
    if stop: add_glow(f, 540, 760, 260, (120, 180, 255), 0.5)
    img = acabado(f, T)
    if t < tl(RK, 0.35): burst(img, "¿?", 540, 1500, 130, t, col=(255, 222, 40), ang=-4)
    if stop:
        u = t - tl(RK, 0.82)
        burst(img, "???", 540, 1480, 110, u, col=(200, 200, 220), ang=-5)
        if u > 0.35: burst(img, "¡LLUVIA!", 540, 1640, 130, u - 0.35, col=(120, 190, 255), ang=4)
    return img, (2 * math.sin(T * 40) if not stop else 6 * math.exp(-(t - tl(RK, 0.82)) * 5))

@shot
def s13(t, D, T):    # aguacero: la lluvia les lava el barro
    u = t / D
    cam = Cam(540, 1120, lerp(1.1, 1.3, ease(u)))
    dr = D_(cam); selva_bg(dr, t, hor=1000, trees=False, ptero=False)
    amt = 1 - ease((u - 0.25) / 0.65)
    nico(dr, 400, 1800, 0.56, t, traje=EXP, arms=(30, 30), elbows=(40, 40), expr="worried" if amt < 0.5 else "happy", look=(0, -0.6))
    embarrar(dr, 400, 1800, 0.56, amt, t)
    trici(dr, 720, 1820, 0.38, t, face=-1, expr="happy", look=(0, -0.5))
    embarrar_tri(dr, 720, 1820, 0.38, -1, amt)
    f = mojar(tinta(dr)); img = acabado(f, T)
    lluvia(img, t)
    burst(img, "¡SPLISH!", 540, 520, 100, t - 0.2, col=(150, 200, 255), ang=-6)
    return img, 0

@shot
def s14(t, D, T):    # Trici: ¡Nico, mira! ¡ya no estamos sucios!
    cam = Cam(540, 1150, 1.6)
    dr = D_(cam); selva_bg(dr, t, hor=1000, trees=False, ptero=False)
    trici(dr, 520, 1700, 0.72, t, mouth=boca(13, t), face=1, expr="happy", look=(0.5, -0.3), hop=(t * 1.4) % 1)
    f = mojar(tinta(dr)); img = acabado(f, T)
    lluvia(img, t)
    burst(img, "¡LIMPIOS!", 760, 520, 110, t - 0.3, col=(150, 220, 255), ang=8)
    return img, 0

@shot
def s15(t, D, T):    # Nico: no no no… ¡vuelvo a oler a bloqueador!
    cam = Cam(540, 1080, 1.75)
    dr = D_(cam); selva_bg(dr, t, hor=1000, trees=False, ptero=False)
    shake = math.sin(t * 14) * 25 if t < tl(14, 0.4) else 0
    nico(dr, 540, 1660, 0.62, t, traje=EXP, arms=(70 + shake, 70 - shake), elbows=(70, 70), expr="nervous", mouth=boca(14, t), look=(0, 0.3), sweat=True)
    f = mojar(tinta(dr)); img = acabado(f, T)
    lluvia(img, t)
    if t > tl(14, 0.5):
        olor(img, 440, 760, t, (255, 236, 140), 3, -1.2, 1.2)
        burst(img, "¡OLOR A PLAYA!", 540, 470, 86, t - tl(14, 0.5), col=(255, 222, 40), ang=-6)
    return img, 0

@shot
def s16(t, D, T):    # a lo lejos, un rugido que ya conocen (T-Rex gira la cabeza a lo lejos)
    u = t / D
    cam = Cam(540, 1080, lerp(1.0, 1.15, ease(u)))
    dr = D_(cam); selva_bg(dr, t, hor=1150, trees=False, ptero=False)
    trex(dr, 760, 1330, 0.2, t, mouth=0.6 if u > 0.4 else 0.1, face=-1 if u > 0.4 else 1)
    palma(dr, -60, 1600, 0.9, t, 0); palma(dr, 1140, 1600, 0.9, t, 2)
    nico(dr, 300, 1760, 0.45, t, traje=EXP, arms=(30, 30), elbows=(50, 50), expr="shock" if u > 0.4 else "worried", look=(1, -0.4))
    helechos_frente(dr, t, 2100, 0.8)
    f = mojar(tinta(dr)); img = acabado(f, T)
    lluvia(img, t)
    if u > 0.4: burst(img, "GROOAAR", 760, 850, 90, t - 0.4 * D, col=(150, 240, 110), ang=6)
    return img, (3 if u > 0.4 else 0)

@shot
def s17(t, D, T):    # T-Rex: ¡grrr! ¡ahí está otra vez el olor a playa!
    u = t / D
    cam = Cam(540, 1000, lerp(1.0, 1.1, ease(u)))
    dr = D_(cam); selva_bg(dr, t, hor=1250, trees=False, ptero=False)
    trex_cabeza(dr, 600, 1060, 1.3, t, mouth=0.2 + boca(16, t) * 0.8, face=-1, sniff=0.8, eye_look=(-0.8, 0.3))
    f = mojar(tinta(dr)); add_glow(f, *cam.p(600 - 40 * 1.3 * -1 * -1, 1060 - 110 * 1.3), 120, (255, 220, 60), 0.4)
    img = acabado(f, T)
    lluvia(img, t)
    burst(img, "¡GRRR!", 300, 560, 130, t - 0.05, col=(150, 240, 110), ang=-8)
    return img, 3 + 6 * boca(16, t)

@shot
def s18(t, D, T):    # corren a la orilla del río… ¡al otro lado está la manada!
    u = t / D
    cam = Cam(lerp(420, 640, ease(u)), 1100, 1.0)
    dr = D_(cam); cielo(dr, -900, 1000); montanas(dr, 1000)
    dr.rrect(-600, 1000, 1700, 2700, 0, (120, 160, 74))
    for k in range(5): trici(dr, 520 + k * 140, 1080, 0.14 + 0.01 * k, t + k, face=-1)
    rio(dr, t * 2.2, 1120, 1520, (80, 130, 170))
    nico(dr, lerp(160, 470, ease(min(1, u * 1.6))), 1840, 0.5, t, traje=EXP, arms=(70 + 60 * math.sin(t * 14), 70 - 60 * math.sin(t * 14)) if u < 0.6 else (30, 150), elbows=(60, 0),
         expr="shock" if u < 0.6 else "happy", look=(1, -0.6))
    trici(dr, lerp(-80, 760, ease(min(1, u * 1.6))), 1860, 0.36, t, face=1, walk=t * 2 if u < 0.6 else 0, expr="happy" if u > 0.6 else "scared", look=(0.5, -0.8))
    f = mojar(tinta(dr), 0.7); img = acabado(f, T)
    lluvia(img, t, 0.8)
    if u > 0.6:
        d = ImageDraw.Draw(img); X, Y = cam.p(800, 1040)
        d.text((X, Y - 170), "¡MANADA!", font=font(64), fill=(255, 222, 40), anchor="mm", stroke_width=8, stroke_fill=INK)
    return img, 0

@shot
def s19(t, D, T):    # DATO REAL: 3 tricerátops jóvenes juntos en Montana
    cam = Cam(540, 1000, 1.0)
    dr = D_(cam, bg=(60, 44, 34))
    for k in range(18):
        a = k * math.pi / 9 + t * 0.3
        dr.poly([(540, 1150), (540 + math.cos(a) * 2000, 1150 + math.sin(a) * 2000), (540 + math.cos(a + 0.17) * 2000, 1150 + math.sin(a + 0.17) * 2000)], (78, 58, 44))
    dr.ell(540, 1500, 520, 140, (150, 120, 84))   # capa de roca
    for k in range(3):
        if t > tl(18, 0.25 + 0.1 * k):
            trici(dr, 260 + k * 270, 1470 - (k % 2) * 30, 0.3, t + k * 0.7, face=1 if k != 1 else -1, expr="happy_eyes")
    f = tinta(dr); img = acabado(f, T); d = ImageDraw.Draw(img)
    d.polygon([(0, 290), (W, 240), (W, 400), (0, 450)], fill=(255, 214, 10), outline=INK, width=8)
    d.text((540, 345), "DATO REAL", font=font(76), fill=INK, anchor="mm")
    d.rounded_rectangle([110, 500, 970, 610], radius=26, fill=(255, 255, 255), outline=INK, width=6)
    d.text((540, 555), "MONTANA, EE. UU.", font=font(56), fill=INK, anchor="mm")
    if t > tl(18, 0.55): burst(img, "3 JÓVENES JUNTOS", 540, 900, 76, t - tl(18, 0.55), col=(110, 230, 110), ang=-4)
    return img, 0

@shot
def s20(t, D, T):    # Trici: ¡mamá! ¡estoy aquí! (mamá tricerátops al otro lado)
    u = t / D
    cam = Cam(540, 1100, 1.15)
    dr = D_(cam); cielo(dr, -900, 1000); montanas(dr, 1000)
    dr.rrect(-600, 1000, 1700, 2700, 0, (120, 160, 74))
    rio(dr, t * 2.2, 1150, 1400, (80, 130, 170))
    trici(dr, 820, 1140, 0.62, t, mouth=0.6 if u > 0.6 else 0, face=-1, expr="happy" if u > 0.6 else "shock", look=(-0.5, 0.3))   # mamá (grande)
    trici(dr, 300, 1640, 0.5, t, mouth=boca(19, t), face=1, expr="happy", look=(0.6, -0.6), hop=(t * 1.8) % 1)
    f = mojar(tinta(dr), 0.6); img = acabado(f, T)
    lluvia(img, t, 0.6)
    tarjeta_nombre(img, t - 0.4, "MAMÁ TRICI", "la manada la encontró")
    return img, 0

@shot
def s21(t, D, T):    # el río crecido… y el T-Rex a diez pasos
    u = t / D
    cam = Cam(540, 1260, lerp(1.0, 1.1, ease(u)))
    dr = D_(cam); selva_bg(dr, t, hor=950, trees=False, ptero=False)
    rio(dr, t * 3.0, 1050, 1450, (80, 130, 170))
    for k in range(5):   # olas del río crecido
        x = -100 + ((k * 260 + t * 400) % 1400)
        dr.ell(x, 1250 + (k % 2) * 80, 90, 24, (220, 236, 250), nolin=True)
    trex(dr, 860, 1960, 0.5, t, mouth=0.5 + 0.3 * math.sin(t * 4), face=-1, step=(t * 1.2) % 1)
    nico(dr, 360, 1880, 0.45, t, traje=EXP, arms=(150, 150), elbows=(20, 20), expr="shock", look=(1, -0.4), sweat=True)
    trici(dr, 140, 1900, 0.32, t, face=1, expr="scared", sweat=True)
    f = mojar(tinta(dr)); img = acabado(f, T)
    lluvia(img, t)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([290, 440, 790, 560], radius=28, fill=(230, 40, 50), outline=INK, width=8)
    d.text((540, 500), "10 PASOS", font=font(70), fill=(255, 255, 255), anchor="mm", stroke_width=6, stroke_fill=INK)
    return img, 3 * abs(math.sin(t * 1.2 * math.pi))

@shot
def s22(t, D, T):    # Nico: tengo una idea loca… y otra más loca (bombillo)
    cam = Cam(540, 1080, 1.7)
    dr = D_(cam); selva_bg(dr, t, hor=1000, trees=False, ptero=False)
    nico(dr, 540, 1680, 0.62, t, traje=EXP, arms=(20, 150), elbows=(0, 40), expr="smug", mouth=boca(21, t), look=(0.3, -0.5))
    f = mojar(tinta(dr), 0.7)
    X, Y = cam.p(540, 1680 - 0.62 * 1050)
    add_glow(f, X, Y - 40, 200, (255, 236, 120), 0.6)
    img = acabado(f, T); lluvia(img, t, 0.6); d = ImageDraw.Draw(img)
    d.ellipse([X - 70, Y - 160, X + 70, Y - 20], fill=(255, 230, 80), outline=INK, width=8)
    d.rectangle([X - 30, Y - 20, X + 30, Y + 20], fill=(150, 150, 160), outline=INK, width=6)
    if t > tl(21, 0.5): burst(img, "¡x2!", 820, 560, 110, t - tl(21, 0.5), col=(255, 222, 40), ang=8)
    return img, 0

@shot
def s23(t, D, T):    # dilema: 1 bloqueador lejos · 2 Trici llama a su manada
    cam = Cam(540, 960, 1.0)
    dr = D_(cam, bg=(250, 214, 150))
    dr.poly([(540, -100), (1600, -100), (1600, 2600), (540, 2600)], (120, 160, 74))
    dr.poly([(470, -100), (610, -100), (610, 2600), (470, 2600)], (20, 16, 26))
    o1 = t > tl(22, 0.1); o2 = t > tl(22, 0.62)
    if o1:
        k = eob((t - tl(22, 0.1)) / 0.3)
        a = (t * 4) % (2 * math.pi)
        bloqueador(dr, 270 + 60 * math.sin(t * 2), 1080, 0.55 * k + 0.01, t)
    if o2: trici(dr, 840, 1250, 0.42 * eob((t - tl(22, 0.62)) / 0.3) + 0.01, t, mouth=0.8, face=-1, expr="happy")
    nico(dr, 540, 1560, 0.5, t, traje=EXP, arms=(70, 70), elbows=(60, 60), expr="worried", look=(-0.8 if t < tl(22, 0.6) else 0.8, -0.3))
    f = tinta(dr); img = acabado(f, T); d = ImageDraw.Draw(img)
    if o1: olor(img, 120, 900, t, (255, 236, 140), 3, -0.4, 0.8)
    if o2: burst(img, "¡MAMÁ!", 810, 860, 80, t - tl(22, 0.62), col=(255, 160, 200), ang=6)
    d.text((540, 300), "¿QUÉ HACE NICO?", font=font(92), fill=(255, 222, 40), anchor="mm", stroke_width=12, stroke_fill=INK)
    for ok, x, n, a, b in ((o1, 270, "1", "LANZAR EL", "BLOQUEADOR"), (o2, 810, "2", "TRICI LLAMA", "A SU MANADA")):
        if not ok: continue
        d.ellipse([x - 90, 440, x + 90, 620], fill=(255, 255, 255), outline=INK, width=10)
        d.text((x, 532), n, font=font(130), fill=INK, anchor="mm")
        d.text((x, 700), a, font=font(46), fill=(255, 255, 255), anchor="mm", stroke_width=7, stroke_fill=INK)
        d.text((x, 760), b, font=font(44), fill=(255, 255, 255), anchor="mm", stroke_width=7, stroke_fill=INK)
    return img, 0

@shot
def s24(t, D, T):    # comenta 1 o 2 + portal + capítulo final mañana
    cam = Cam(540, 1100, 1.15)
    dr = D_(cam, bg=(230, 40, 50))
    for k in range(18):
        a = k * math.pi / 9 - t * 0.6
        dr.poly([(540, 1100), (540 + math.cos(a) * 2000, 1100 + math.sin(a) * 2000), (540 + math.cos(a + 0.17) * 2000, 1100 + math.sin(a + 0.17) * 2000)], (250, 70, 70))
    o = ease((t - D + 1.5) / 0.6)
    portal(dr, 540, 1150, 340, t, o)
    if t < D - 0.5: nico(dr, 540, 1900, 0.72, t, traje=EXP, arms=(100, 170), elbows=(-20, 0), expr="happy", mouth=boca(23, t))
    f = tinta(dr); add_glow(f, *cam.p(540, 1150), 450, (150, 120, 255), 0.5 * o); img = acabado(f, T)
    d = ImageDraw.Draw(img)
    for k, (x, n) in enumerate(((330, "1"), (750, "2"))):
        p = 1 + 0.08 * math.sin(t * 8 + k * 3); r = 95 * p
        d.ellipse([x - r, 420 - r, x + r, 420 + r], fill=(255, 214, 10), outline=INK, width=10)
        d.text((x, 420), n, font=font(130 * p), fill=INK, anchor="mm")
    d.text((540, 610), "COMENTA", font=font(84), fill=(255, 255, 255), anchor="mm", stroke_width=10, stroke_fill=INK)
    if t > D - 2.6:
        d.rounded_rectangle([130, 690, 950, 850], radius=36, fill=(255, 214, 10), outline=INK, width=8)
        d.text((540, 745), "CAPÍTULO FINAL", font=font(64), fill=INK, anchor="mm")
        d.text((540, 810), "MAÑANA · 6 P. M.", font=font(44), fill=(200, 40, 50), anchor="mm")
    return img, 0
assert len(SHOTS) == len(VOZ), (len(SHOTS), len(VOZ))

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
    badge(img, T)
    caption(img, T)
    return img

# ------------------------------------------------------------ sonido
def make_audio(path):
    from scipy.signal import butter, sosfilt
    sr = SR; n = int(TOTAL * sr) + sr; out = np.zeros(n)
    rng = np.random.default_rng(11)
    def add(s, sig, g=1.0):
        i0 = int(s * sr); i1 = min(n, i0 + len(sig))
        if 0 <= i0 < n: out[i0:i1] += g * sig[:i1 - i0]
    def seg(d): return np.arange(int(d * sr)) / sr
    hz = lambda m: 440 * 2 ** ((m - 69) / 12)
    noise = rng.standard_normal(n)
    bp = lambda lo, hi: sosfilt(butter(2, [lo, hi], btype="band", fs=sr, output="sos"), noise)
    wh = bp(400, 3500); low = sosfilt(butter(2, 160, btype="low", fs=sr, output="sos"), noise)
    S_ = STARTS
    def aventura(s, tend, g=1.0, dark=False):   # marimba + tambores tribales
        e = 0.17
        prog = [[60, 64, 67, 72], [57, 60, 64, 69], [53, 57, 60, 65], [55, 59, 62, 67]] if not dark else [[45, 48, 52, 57], [44, 48, 51, 56]]
        k = 0
        while s < tend:
            ch = prog[(k // 16) % len(prog)]; m = ch[[0, 2, 1, 3][k % 4]] + (12 if (k // 8) % 2 else 0)
            x = seg(e * 1.5)
            add(s, g * 0.05 * np.sin(2 * np.pi * hz(m) * x) * np.exp(-x * 9) * (1 - np.exp(-x * 200)))
            if k % 8 == 0:
                xb = seg(e * 8); add(s, g * 0.09 * np.sin(2 * np.pi * hz(ch[0] - 24) * xb) * np.exp(-xb * 0.7))
            if k % 4 in (0, 3):
                xt = seg(0.25); add(s, g * 0.16 * np.exp(-xt * 16) * np.sin(2 * np.pi * (90 + 60 * np.exp(-xt * 25)) * xt))
            if k % 2 == 1: add(s, g * 0.025 * rng.standard_normal(len(x)) * np.exp(-x * 50))
            k += 1; s += e
    def dron(s, tend, g=0.08):
        xd = seg(max(0.01, tend - s)); add(s, g * (np.sin(2 * np.pi * 41 * xd) + 0.5 * np.sin(2 * np.pi * 61.7 * xd)) * np.clip(xd / 1.5, 0, 1))
    def pisada(s, g=0.6):
        x = seg(0.7); add(s, g * (np.sin(2 * np.pi * (38 + 30 * np.exp(-x * 12)) * x) * np.exp(-x * 5) + 0.5 * low[:len(x)] * np.exp(-x * 7)))
    def rugido(s, d=1.6, g=0.5):
        x = seg(d)
        f0 = 70 + 40 * np.sin(np.pi * x / d)
        tone = np.sign(np.sin(2 * np.pi * np.cumsum(f0) / sr)) * 0.4 + np.sin(2 * np.pi * np.cumsum(f0 * 2) / sr) * 0.3
        rough = bp(80, 900)[:len(x)] * 0.8
        env = np.sin(np.pi * np.clip(x / d, 0, 1)) ** 0.6
        add(s, g * (tone + rough) * env * (0.7 + 0.3 * np.sin(2 * np.pi * 23 * x)))
    def pio(s, g=0.12):   # pasito de Trici / bocina linda
        x = seg(0.18); add(s, g * np.sin(2 * np.pi * (900 + 600 * x / 0.18) * x) * np.exp(-x * 12))
    def lluvia_snd(s, tend, g=0.06):
        x = seg(max(0.01, tend - s)); add(s, g * bp(1500, 7000)[:len(x)] * np.clip(x / 0.8, 0, 1) * np.clip((tend - s - x) / 0.8, 0, 1))
    def trueno(s, g=0.5):
        x = seg(2.5); add(s, g * low[:len(x)] * 6 * np.exp(-x * 1.6) * (0.6 + 0.4 * np.sin(2 * np.pi * 3 * x)))
    def splash(s, g=0.3):
        x = seg(0.6); add(s, g * bp(200, 2500)[:len(x)] * np.exp(-x * 7))
    # recap + barro
    aventura(S_[0], S_[1], 0.4, dark=True)
    x = seg(DURS[0]); add(S_[0], 0.08 * bp(300, 1500)[:len(x)] * (np.abs(np.sin(2 * np.pi * 4.5 * x)) ** 4))
    aventura(S_[1], S_[5], 0.75)
    splash(S_[1] + DURS[1] * 0.55, 0.5)
    for k in range(3): splash(S_[2] + 0.3 + k * 0.5, 0.15)
    # estatuas + T-Rex
    dron(S_[5], S_[9], 0.1)
    pisada(S_[5] + DURS[5] * 0.9, 0.8)
    x = seg(DURS[6]); add(S_[6], 0.12 * bp(300, 1500)[:len(x)] * (np.abs(np.sin(2 * np.pi * 4.5 * x)) ** 4))
    x = seg(DURS[7]); add(S_[7], 0.1 * bp(300, 1500)[:len(x)] * (np.abs(np.sin(2 * np.pi * 5 * x)) ** 4))
    for k in range(int(DURS[7] / 0.5)):
        xh = seg(0.2); add(S_[7] + k * 0.5, 0.2 * np.exp(-xh * 14) * np.sin(2 * np.pi * 60 * xh))
    for k in range(3): pisada(S_[9] + 0.2 + k * 0.6, 0.4 - 0.1 * k)
    aventura(S_[9], S_[11], 0.9)
    # ruleta
    t0 = S_[RK] + tl(RK, 0.35); t1 = S_[RK] + tl(RK, 0.82)
    xr = seg(t1 - t0); add(t0, 0.06 * bp(150, 600)[:len(xr)] * (0.6 + 0.4 * np.sin(2 * np.pi * 18 * xr)))
    prev = int(ang_ruleta(t0) / 22.5)
    for k in range(int((t1 - t0) * FPS) + 2):
        T = t0 + k / FPS; a = ang_ruleta(T)
        if int(a / 22.5) != prev:
            prev = int(a / 22.5); xc = seg(0.03); add(T, 0.25 * np.exp(-xc * 200) * np.sin(2 * np.pi * 2500 * xc))
    x = seg(1.2); add(t1, 0.35 * np.exp(-x * 2.5) * (np.sin(2 * np.pi * 330 * x) + np.sin(2 * np.pi * 392 * x) + np.sin(2 * np.pi * 466 * x)) / 3)
    dron(S_[11], S_[12], 0.06)
    # lluvia: desde el plano 13 hasta el 22
    trueno(S_[12], 0.6); lluvia_snd(S_[12], S_[22], 0.07)
    aventura(S_[12], S_[15], 0.45, dark=True)
    trueno(S_[15] + 0.2, 0.4)
    rugido(S_[15] + DURS[15] * 0.4, 1.6, 0.55)
    rugido(S_[16] + 0.05, 1.0, 0.35)
    aventura(S_[17], S_[18], 1.0)
    aventura(S_[18], S_[19], 0.4)
    aventura(S_[19], S_[22], 0.8, dark=True)
    for k in range(int(DURS[20] * 1.2)): pisada(S_[20] + k / 1.2, 0.5)
    x = seg(DURS[20]); add(S_[20], 0.07 * bp(200, 1200)[:len(x)])
    # dilema + cierre
    dron(S_[22], S_[23], 0.1)
    for k in range(int(DURS[22] / 0.5)):
        xh = seg(0.2); add(S_[22] + k * 0.5, 0.18 * np.exp(-xh * 14) * np.sin(2 * np.pi * 60 * xh))
    aventura(S_[23], TOTAL, 0.7)
    x = seg(1.6); add(TOTAL - 1.6, 0.2 * wh[:len(x)] * np.sin(np.pi * x / 1.6) * (0.5 + 0.5 * np.sin(2 * np.pi * 9 * x)))
    for k in range(1, len(S_) - 1):
        x = seg(0.25); add(S_[k] - 0.08, 0.06 * wh[:len(x)] * np.sin(np.pi * x / 0.25))
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
        ts = [STARTS[i] + DURS[i] * 0.6 for i in range(len(SHOTS))] if os.environ["PREVIEW"] == "auto" else [float(x) for x in os.environ["PREVIEW"].split(",")]
        ims = [frame(T).resize((270, 480)) for T in ts]
        sheet = Image.new("RGB", (270 * 6, 480 * ((len(ims) + 5) // 6)))
        for k, im in enumerate(ims): sheet.paste(im, ((k % 6) * 270, (k // 6) * 480))
        sheet.save("sheet.png"); print("TOTAL", round(TOTAL, 2), [round(s, 2) for s in STARTS]); sys.exit()
    if os.environ.get("BIG"):
        for k, T in enumerate(os.environ["BIG"].split(",")): frame(float(T)).save(f"big{k}.png")
        sys.exit()
    if os.environ.get("AUDIO"):
        make_audio("audio.wav"); sys.exit()
    if os.environ.get("RANGE"):
        a, b = [int(v) for v in os.environ["RANGE"].split(",")]
        p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                              "-c:v", "libx264", "-preset", "veryfast", "-crf", "24", "-tune", "animation", "-pix_fmt", "yuv420p", OUT], stdin=subprocess.PIPE)
        for k in range(a, b):
            p.stdin.write(frame(k / FPS).convert("RGB").tobytes())
            if k % 300 == 0: print(f"{k}/{b}", flush=True)
        p.stdin.close(); p.wait(); print("tramo listo", OUT); sys.exit()
    print("NFRAMES", int(TOTAL * FPS))
