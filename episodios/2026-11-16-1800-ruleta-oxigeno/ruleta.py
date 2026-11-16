#!/usr/bin/env python3
"""LA RULETA DE NICO · T2: ZOMBIS EN EL ESPACIO · Capítulo 2/3.
Nico eligió el invernadero (2). La ruleta cae en ??? = SIN OXÍGENO (10 min). Tuerca hace de cebo, Nico
consigue el tanque, pero un zombi con audífonos no se fue. Dilema: 1 quitarle los audífonos / 2 lanzarle el tanque."""
import math, os, sys, subprocess
import numpy as np
from PIL import Image, ImageDraw
from scipy.io import wavfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vc import *

FPS = 30
OUT = sys.argv[1] if len(sys.argv) > 1 else "video.mp4"
VOZ_DIR = os.environ.get("VOZ_DIR", "voz")
VOZ_F = sorted(f for f in os.listdir(VOZ_DIR) if f.endswith(".wav"))
VOZ = [wavfile.read(f"{VOZ_DIR}/{f}")[1].astype(np.float32) / 32768 for f in VOZ_F]
SR = 44100; LEAD = 0.1
DURS = [len(v) / SR + LEAD + 0.26 for v in VOZ]
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
    [("Antes en", []), ("La Ruleta de Nico:", ["Ruleta"]), ("una caja", ["caja"]), ("que decía", []), ("NO ABRIR…", ["NO", "ABRIR…"]), ("y doce astronautas", ["doce"]), ("zombis", ["zombis"])],
    [("Nico eligió", []), ("la opción dos:", ["dos:"]), ("¡el invernadero", ["¡el", "invernadero"]), ("espacial!", ["espacial!"])],
    [("¡Tuerca,", ["¡Tuerca,"]), ("al invernadero!", ["invernadero!"]), ("¡Ya, ya, ya!", ["ya!"])],
    [("Las plantas", ["plantas"]), ("tapan el ruido…", ["ruido…"]), ("y los zombis", ["zombis"]), ("pasan de largo", ["largo"])],
    [("Funcionó…", ["Funcionó…"]), ("aquí nadie", []), ("nos oye", ["oye"])],
    [("Afirmativo.", []), ("Y hay tomates.", ["tomates."])],
    [("Pero la ruleta", ["ruleta"]), ("vuelve a girar…", ["girar…"]), ("y cae en…", []), ("¡el signo", []), ("de pregunta!", ["pregunta!"])],
    [("Alerta silenciosa:", ["silenciosa:"]), ("oxígeno", ["oxígeno"]), ("al 10 %", ["10", "%"])],
    [("¿Diez por ciento?", ["Diez"]), ("¿Y eso", []), ("cuánto es?", ["cuánto"])],
    [("Diez minutos.", ["minutos."]), ("Nueve, si sigues", ["Nueve,"]), ("hablando.", [])],
    [("Las plantas", []), ("sí hacen oxígeno…", ["oxígeno…"]), ("pero tan despacio", ["despacio"]), ("que no alcanzan", []), ("ni para un astronauta", ["astronauta"])],
    [("El tanque", ["tanque"]), ("de oxígeno está", []), ("en el módulo", []), ("de al lado…", []), ("lleno de zombis", ["zombis"])],
    [("Tengo una idea.", ["idea."]), ("Tuerca,", []), ("necesito tu voz", ["voz"])],
    [("¿Mi alarma?", ["alarma?"]), ("¡Por fin alguien", []), ("la aprecia!", ["aprecia!"])],
    [("Tuerca vuela", ["vuela"]), ("al otro extremo", ["extremo"]), ("de la estación…", []), ("y grita:", ["grita:"])],
    [("¡ALERTA!", ["¡ALERTA!"]), ("¡CEREBROS GRATIS!", ["GRATIS!"]), ("¡CEREBROS GRATIS!", ["GRATIS!"])],
    [("Los doce zombis", ["doce"]), ("flotan hacia el ruido…", ["ruido…"])],
    [("y Nico cruza", []), ("el módulo vacío", ["vacío"]), ("hasta el tanque", ["tanque"])],
    [("¡Lo tengo!", ["tengo!"]), ("¡Aire para un mes!", ["mes!"])],
    [("Pero al darse", []), ("la vuelta…", ["vuelta…"]), ("un zombi", ["zombi"]), ("no se fue", ["fue"])],
    [("No oyó a Tuerca…", ["Tuerca…"]), ("porque tiene", []), ("audífonos puestos", ["audífonos"])],
    [("Grrr…", ["Grrr…"]), ("cerebrooo…", ["cerebrooo…"])],
    [("Uno:", ["Uno:"]), ("quitarle", []), ("los audífonos", ["audífonos"]), ("para que oiga", []), ("a Tuerca…", ["Tuerca…"]), ("pero también", []), ("oirá a Nico.", ["Nico."]),
     ("Dos:", ["Dos:"]), ("lanzarle el tanque", ["tanque"]), ("y huir…", ["huir…"]), ("con cinco minutos", ["cinco"]), ("de aire", ["aire"])],
    [("¿Qué haría Nico?", ["Nico?"]), ("Comenta 1 o 2.", ["1", "2."]), ("En el capítulo final", ["final"]), ("verás si", []), ("elegiste bien", ["bien"])],
    [("Nos vemos en otro", []), ("mundo hipotético…", ["hipotético…"]), ("si me queda aire", ["aire"])],
]
DURS[6] += 0.4; DURS[22] += 0.4; DURS[23] += 0.4; DURS[24] += 0.5

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

# ------------------------------------------------------------ espacio
def estrellas(dr, t, n=80, seed=5, area=(-400, -800, 1500, 2600)):
    rng = np.random.default_rng(seed)
    for k in range(n):
        x, y = rng.uniform(area[0], area[2]), rng.uniform(area[1], area[3])
        r = rng.uniform(2, 5) * (0.7 + 0.3 * math.sin(t * 3 + k))
        dr.ell(x, y, r, r, (255, 250, 230), nolin=True)

def tierra(dr, x, y, r, t):
    dr.ell(x, y, r * 1.05, r * 1.05, (120, 190, 255), nolin=True)
    dr.ell(x, y, r, r, (46, 110, 210), shade=True)
    a = t * 0.05
    for (dx, dy, rx, ry) in ((-0.35, -0.3, 0.32, 0.2), (0.25, -0.05, 0.22, 0.34), (-0.1, 0.42, 0.3, 0.14), (0.5, 0.45, 0.18, 0.12)):
        cx = x + r * (dx + 0.1 * math.sin(a)); cy = y + r * dy
        if (cx - x) ** 2 + (cy - y) ** 2 < (r * 0.8) ** 2: dr.ell(cx, cy, r * rx, r * ry, (90, 180, 90))
    for (dx, dy, rx) in ((-0.5, 0.1, 0.2), (0.1, -0.55, 0.25), (0.3, 0.25, 0.15)):
        dr.ell(x + r * dx, y + r * dy, r * rx, r * rx * 0.3, (250, 250, 255), nolin=True)

def ventana(dr, x, y, r, t, horda=0.0):
    dr.ell(x, y, r * 1.18, r * 1.18, (150, 156, 170), shade=True)
    dr.ell(x, y, r, r, (8, 10, 26))
    X, Y = dr.cam.p(x, y)
    estrellas(dr, t, 30, 8, (x - r * 0.8, y - r * 0.8, x + r * 0.8, y + r * 0.2))
    tierra(dr, x + r * 0.2, y + r * 1.1, r * 0.9, t)
    for k in range(int(5 * horda)):   # zombis flotando afuera
        u = (k * 0.37) % 1
        zx = x - r * 0.6 + r * 1.2 * u + 20 * math.sin(t + k)
        zy = y - r * 0.5 + r * 0.6 * ((k * 0.61) % 1) + 10 * math.cos(t * 1.3 + k)
        zastro(dr, zx, zy + 0.35 * r, 0.24 * r / 300 * (0.7 + 0.3 * u) * (0.6 + 0.4 * horda), t, ph=k, helmet=True)
    # marco por encima (tapa lo que sale)
    ww = max(3, int(dr.cam.s(r * 0.18))); rr = dr.cam.s(r * 1.09)
    dr.d.ellipse([X - rr, Y - rr, X + rr, Y + rr], outline=(150, 156, 170), width=ww)
    for k in range(8):
        a = k * math.pi / 4
        dr.ell(x + math.cos(a) * r * 1.09, y + math.sin(a) * r * 1.09, r * 0.04, r * 0.04, (100, 106, 120))

def estacion(dr, t, win=(820, 760, 250), horda=0.0):
    """Interior de un módulo: pared del fondo + paredes laterales en perspectiva."""
    dr.rrect(-500, -900, 1600, 2600, 0, (182, 188, 200))
    dr.poly([(-500, -900), (180, 300), (180, 1500), (-500, 2600)], (160, 166, 180))
    dr.poly([(1600, -900), (900, 300), (900, 1500), (1600, 2600)], (150, 156, 170))
    dr.poly([(-500, -900), (1600, -900), (900, 300), (180, 300)], (200, 206, 216))
    dr.poly([(-500, 2600), (1600, 2600), (900, 1500), (180, 1500)], (140, 146, 160))
    dr.rrect(180, 300, 900, 1500, 0, (210, 214, 224))
    for k in range(4):   # paneles y cables
        dr.rrect(220 + k * 170, 360, 360 + k * 170, 560, 10, (226, 230, 238))
        dr.ell(250 + k * 170, 400, 10, 10, ((230, 60, 60), (60, 200, 110), (250, 200, 50), (90, 160, 255))[k], nolin=True)
    dr.rrect(200, 1180, 880, 1210, 10, (250, 200, 50))          # pasamanos amarillo
    for k in range(5): dr.rrect(-300 + k * 60, 300 + k * 260, -240 + k * 60, 330 + k * 260, 6, (250, 200, 50))
    dr.line([(-400, 1900), (60, 1300), (180, 1250)], (60, 70, 90), 14)
    dr.line([(-400, 2000), (100, 1400), (180, 1350)], (230, 70, 60), 10)
    dr.rrect(300, 650, 500, 780, 10, (40, 44, 56)); dr.rrect(312, 662, 488, 768, 6, (90, 200, 255))   # laptop con velcro
    dr.text(400, 715, "ISS-NICO", 26, (255, 255, 255))
    if win: ventana(dr, *win, t, horda)

def espacio_fondo(dr, t):
    dr.rrect(-500, -900, 1600, 2600, 0, (8, 10, 28))
    estrellas(dr, t, 110, 3)
    tierra(dr, 540, 2500, 1200, t)

# ------------------------------------------------------------ personajes
ZC = (130, 182, 104); ZC_D = (98, 150, 80)
def zastro(dr, x, y, s, t, mouth=0.0, ph=0.0, helmet=True, turn=0.0, arms=1.0, phones=False):
    """Astronauta zombi flotando. (x, y) = pies. Ojos blancos SIN pupila: no ve nada."""
    S = lambda v: v * s
    y = y + S(16) * math.sin(t * 1.5 + ph)
    suit = (200, 204, 210)
    for sx in (-1, 1):
        a = math.sin(t * 1.3 + ph + sx) * 0.3
        fx, fy = x + sx * S(45) + S(60) * a, y - S(10)
        dr.line([(x + sx * S(40), y - S(230)), (fx, fy)], suit, S(54))
        dr.ell(fx, fy, S(40), S(22), (110, 116, 130))
    dr.rrect(x - S(118), y - S(490), x + S(118), y - S(200), S(80), suit, True)
    dr.rrect(x - S(60), y - S(430), x + S(10), y - S(370), S(8), (150, 156, 168))
    dr.ell(x + S(60), y - S(300), S(26), S(26), (240, 120, 50))
    dr.line([(x - S(90), y - S(260)), (x - S(40), y - S(300)), (x - S(70), y - S(330))], (90, 96, 110), S(6))   # rasgadura
    for sx in (-1, 1):
        shx, shy = x + sx * S(96), y - S(440)
        hx = shx + sx * S(150) * (0.4 + 0.6 * arms); hy = shy - S(30) * arms + S(150) * (1 - arms) + S(12) * math.sin(t * 2 + sx + ph)
        dr.line([(shx, shy), (hx, hy)], suit, S(46))
        dr.ell(hx, hy, S(32), S(30), ZC)
    hx, hy, R = x + S(30) * turn, y - S(650), S(180)
    if helmet: dr.ell(hx, hy - S(10), R * 1.3, R * 1.3, (150, 196, 200))
    dr.ell(hx, hy, R, R, ZC, shade=True)
    for k in range(5): dr.line([(hx - S(60) + k * S(30), hy - R * 0.92), (hx - S(70) + k * S(30) + S(20) * math.sin(t + k), hy - R * 1.12)], (60, 50, 40), S(8))
    for k, (ex, rr) in enumerate(((-70, 52), (75, 36))):
        cx, cy = hx + S(ex) + S(26) * turn, hy - S(5)
        dr.ell(cx, cy + S(10), S(rr + 12), S(rr + 8), ZC_D)
        dr.ell(cx, cy, S(rr), S(rr * 1.05), (242, 246, 230))
    dr.line([(hx - S(120), hy - S(95)), (hx + S(20), hy - S(120))], (70, 50, 60), S(6))
    for k in range(4): dr.line([(hx - S(105) + k * S(38), hy - S(118) + k * S(-5)), (hx - S(95) + k * S(38), hy - S(85) + k * S(-5))], (70, 50, 60), S(5))
    mo = clamp(mouth)
    jx, jy = hx + S(20) * turn, hy + S(95)
    dr.ell(jx, jy, S(72), S(18 + 46 * mo), (60, 24, 36))
    for k in range(5):
        if k == 2: continue
        dr.rrect(jx - S(56) + k * S(24), jy - S(18 + 46 * mo) + S(2), jx - S(40) + k * S(24), jy - S(18 + 46 * mo) + S(22), S(3), (240, 236, 200))
    if helmet:
        X, Y0 = dr.cam.p(hx, hy - S(10)); rr = dr.cam.s(R * 1.3); ww = max(2, int(dr.cam.s(S(20))))
        dr.d.ellipse([X - rr, Y0 - rr, X + rr, Y0 + rr], outline=(200, 204, 210), width=ww)
        dr.line([(hx + R * 0.6, hy - R * 0.9), (hx + R * 0.85, hy - R * 0.55), (hx + R * 0.7, hy - R * 0.4), (hx + R * 1.0, hy - R * 0.15)], INK, S(5))
    if phones:   # audífonos rosados con música
        X, Y0 = dr.cam.p(hx, hy); rr = dr.cam.s(R * 1.02); ww = max(3, int(dr.cam.s(S(26))))
        dr.d.arc([X - rr, Y0 - rr * 1.05, X + rr, Y0 + rr], 190, 350, fill=(40, 40, 50), width=ww)
        for sx in (-1, 1):
            dr.rrect(hx + sx * R * 0.98 - S(40), hy - S(70), hx + sx * R * 0.98 + S(40), hy + S(50), S(30), (255, 90, 170))
            dr.ell(hx + sx * R * 0.98, hy - S(10), S(22), S(40), (200, 50, 120))
    return (hx, hy)

def tuerca(dr, x, y, s, t, mouth=0.0, alarm=False, look=(0, 0)):
    """Robot de la estación. (x, y) = centro."""
    S = lambda v: v * s
    y = y + S(14) * math.sin(t * 3)
    for sx in (-1, 1):
        a = math.sin(t * 6 + sx) * 0.3 + (0.9 if alarm else 0)
        dr.line([(x + sx * S(140), y + S(20)), (x + sx * S(220), y + S(60) - S(120) * a)], (150, 156, 170), S(24))
        dr.ell(x + sx * S(220), y + S(60) - S(120) * a, S(28), S(28), (110, 116, 130))
    dr.line([(x, y - S(160)), (x + S(20), y - S(260))], (120, 126, 140), S(10))
    bl = (255, 60, 50) if (alarm and int(t * 8) % 2) else ((255, 210, 60) if not alarm else (120, 30, 30))
    dr.ell(x + S(20), y - S(270), S(30), S(30), bl, nolin=True)
    dr.rrect(x - S(160), y - S(170), x + S(160), y + S(150), S(70), (206, 212, 222), True)
    dr.rrect(x - S(120), y - S(130), x + S(120), y + S(40), S(40), (26, 34, 54))
    ec = (255, 90, 80) if alarm else (110, 240, 255)
    blink = (t % 2.7) < 0.12
    for sx in (-1, 1):
        ex, ey = x + sx * S(55) + look[0] * S(10), y - S(55) + look[1] * S(8)
        if blink: dr.rrect(ex - S(28), ey - S(4), ex + S(28), ey + S(4), S(3), ec, nolin=True)
        elif alarm: dr.poly([(ex - S(30), ey - S(20) if sx < 0 else ey + S(10)), (ex + S(30), ey + S(10) if sx < 0 else ey - S(20)), (ex + S(30), ey + S(25)), (ex - S(30), ey + S(25))], ec, nolin=True)
        else: dr.ell(ex, ey, S(28), S(34), ec, nolin=True)
    mo = clamp(mouth)
    dr.rrect(x - S(50), y + S(2) - S(16) * mo, x + S(50), y + S(14) + S(16) * mo, S(8), ec, nolin=True)
    hp = [(x + math.cos(math.radians(a)) * S(38), y + S(95) + math.sin(math.radians(a)) * S(38)) for a in range(0, 360, 60)]
    dr.poly(hp, (230, 190, 60)); dr.ell(x, y + S(95), S(15), S(15), (150, 120, 40))
    for sx in (-1, 1): dr.ell(x + sx * S(60), y + S(200), S(22), S(30) + S(10) * math.sin(t * 30), (90, 200, 255), nolin=True)
    return (x, y)

def caja(dr, x, y, s, t, open_=0.0):
    S = lambda v: v * s
    a = open_ * 1.2
    lx, ly = x - S(170), y - S(150)
    lid = [(lx, ly), (lx + math.cos(-a) * S(340), ly + math.sin(-a) * S(340)), (lx + math.cos(-a) * S(340) + math.sin(-a) * S(40) * 0, ly + math.sin(-a) * S(340) - S(40)), (lx, ly - S(40))]
    dr.rrect(x - S(170), y - S(150), x + S(170), y + S(150), S(12), (196, 146, 84), True)
    for xx in (-110, 110): dr.rrect(x + S(xx) - S(16), y - S(150), x + S(xx) + S(16), y + S(150), S(2), (170, 120, 64))
    dr.text(x, y - S(30), "NO", S(84), (220, 40, 40))
    dr.text(x, y + S(60), "ABRIR", S(74), (220, 40, 40))
    if open_ > 0.02:
        dr.poly([(x - S(170), y - S(150)), (x + S(170), y - S(150)), (x + S(150), y - S(120)), (x - S(150), y - S(120))], (40, 60, 30))
        dr.poly(lid, (210, 160, 96))
    else:
        dr.rrect(x - S(180), y - S(190), x + S(180), y - S(150), S(8), (210, 160, 96))
        dr.rrect(x - S(30), y - S(190), x + S(30), y - S(150), S(2), (230, 220, 190))

def gas(dr, x, y, t, k=1.0):
    for i in range(10):
        a = i * 0.63 + t * 0.7
        r = (80 + 40 * math.sin(t * 2 + i)) * k
        dr.ell(x + math.cos(a) * 160 * k, y - 120 * k - (i * 30 + t * 120) % 360 * k, r, r * 0.8, (150, 230, 110), nolin=True)

def capsula(dr, x, y, s, t):
    S = lambda v: v * s
    dr.poly([(x - S(200), y + S(150)), (x - S(110), y - S(170)), (x + S(110), y - S(170)), (x + S(200), y + S(150))], (236, 238, 246), shade=True)
    dr.rrect(x - S(210), y + S(130), x + S(210), y + S(190), S(14), (80, 86, 100))
    dr.ell(x, y - S(20), S(70), S(70), (20, 30, 60)); dr.ell(x, y - S(20), S(52), S(52), (90, 160, 230))
    dr.rrect(x - S(150), y + S(70), x + S(150), y + S(100), S(6), TURQ)
    for sx in (-1, 1): dr.ell(x + sx * S(140), y + S(240) + S(20) * math.sin(t * 30 + sx), S(36), S(70), (255, 160, 50), nolin=True)
    # zombi pegado afuera (brazos y cara)
    dr.ell(x + S(150), y - S(120), S(70), S(70), ZC)
    dr.ell(x + S(130), y - S(130), S(22), S(22), (242, 246, 230)); dr.ell(x + S(175), y - S(125), S(16), S(16), (242, 246, 230))
    dr.ell(x + S(150), y - S(85), S(30), S(14), (60, 24, 36))
    for dy in (-40, 40): dr.ell(x + S(80), y + S(dy), S(26), S(22), ZC)

def invernadero(dr, x, y, s, t):
    S = lambda v: v * s
    dr.rrect(x - S(260), y - S(260), x + S(260), y + S(220), S(30), (60, 40, 80))
    for k in range(3):
        yy = y - S(170) + k * S(140)
        dr.rrect(x - S(230), yy + S(60), x + S(230), yy + S(84), S(6), (170, 176, 190))
        for j in range(5):
            px = x - S(190) + j * S(95); sw = S(6) * math.sin(t * 2 + j + k)
            for (dx, dy, r) in ((0, 20, 34), (-26, 36, 24), (26, 36, 24), (sw, -6, 26)):
                dr.ell(px + dx, yy + S(dy), S(r), S(r * 0.8), (70, 190, 90) if (j + k) % 2 else (50, 160, 80))
    for k in range(3): dr.rrect(x - S(230), y - S(250) + k * S(140), x + S(230), y - S(236) + k * S(140), S(4), (240, 120, 255), nolin=True)

def tubo(dr, x, y, s, ang=0.0):
    S = lambda v: v * s
    dr.rrect(x - S(36), y - S(110), x + S(36), y + S(80), S(14), (236, 238, 246))
    dr.rrect(x - S(36), y - S(20), x + S(36), y + S(30), S(4), TURQ)
    dr.text(x, y + S(5), "PASTA", S(18), (255, 255, 255))
    dr.rrect(x - S(16), y - S(140), x + S(16), y - S(108), S(4), (230, 70, 60))

def ondas(img, x, y, t, col=(255, 222, 40), n=3, size=1.0):
    d = ImageDraw.Draw(img)
    for k in range(n):
        r = (40 + ((t * 160 + k * 60) % 180)) * size
        a = 1 - ((t * 160 + k * 60) % 180) / 180
        if a < 0.15: continue
        d.arc([x - r, y - r, x + r, y + r], -50, 50, fill=col, width=max(3, int(10 * a * size)))
        d.arc([x - r, y - r, x + r, y + r], 130, 230, fill=col, width=max(3, int(10 * a * size)))

def ang_ruleta(T):
    t0, t1 = STARTS[6] + 0.05, STARTS[6] + LEAD + len(VOZ[6]) / SR * 0.72
    final = -90 - 360 * 4
    if T < t0: return 0.0
    u = clamp((T - t0) / (t1 - t0))
    return final * (1 - (1 - u) ** 3)


def badge(img, T):
    d = ImageDraw.Draw(img)
    f = font(36)
    d.rounded_rectangle([36, 110, 36 + f.getlength("LA RULETA DE NICO") + 44, 170], radius=16, fill=(230, 40, 50), outline=INK, width=5)
    d.text((58, 140), "LA RULETA DE NICO", font=f, fill=(255, 255, 255), anchor="lm")
    txt = "CAPÍTULO 2/3"
    x1 = W - 36; x0 = x1 - f.getlength(txt) - 44
    d.rounded_rectangle([x0, 110, x1, 170], radius=16, fill=(255, 214, 10), outline=INK, width=5)
    d.text((x0 + 22, 140), txt, font=f, fill=INK, anchor="lm")
    f2 = font(30); t2 = "ZOMBIS EN EL ESPACIO"
    d.rounded_rectangle([36, 182, 36 + f2.getlength(t2) + 40, 230], radius=14, fill=(110, 200, 90), outline=INK, width=4)
    d.text((56, 206), t2, font=f2, fill=INK, anchor="lm")

# ------------------------------------------------------------ props nuevos
def invernadero_bg(dr, t, zpass=0.0):
    """Módulo invernadero: luz morada de cultivo, estantes de plantas, pasillo con ventana al fondo."""
    dr.rrect(-500, -900, 1600, 2600, 0, (70, 44, 96))
    dr.poly([(-500, -900), (200, 320), (200, 1450), (-500, 2600)], (58, 36, 82))
    dr.poly([(1600, -900), (880, 320), (880, 1450), (1600, 2600)], (52, 32, 74))
    dr.poly([(-500, 2600), (1600, 2600), (880, 1450), (200, 1450)], (44, 28, 60))
    dr.rrect(200, 320, 880, 1450, 0, (92, 60, 120))
    dr.rrect(300, 420, 780, 1000, 40, (12, 14, 34))   # ventana del pasillo
    estrellas(dr, t, 25, 21, (320, 440, 760, 980))
    if zpass > 0:   # zombis pasando de largo por el pasillo
        for k in range(3):
            u = (zpass * 1.3 - k * 0.35)
            if 0 < u < 1: zastro(dr, lerp(200, 880, u), 1000, 0.32, t, ph=k, arms=1.0)
    X, Y = dr.cam.p(540, 710); rx, ry = dr.cam.s(255), dr.cam.s(305)
    dr.d.rounded_rectangle([X - rx, Y - ry, X + rx, Y + ry], radius=int(dr.cam.s(50)), outline=(150, 156, 170), width=max(3, int(dr.cam.s(24))))
    for k in range(4): dr.rrect(-400 + k * 40, 200 + k * 330, 200, 230 + k * 330, 4, (240, 120, 255), nolin=True)   # luces de cultivo
    for k in range(4): dr.rrect(880, 200 + k * 330, 1480 - k * 40, 230 + k * 330, 4, (240, 120, 255), nolin=True)
    for side in (-1, 1):   # estantes con plantas en primer plano
        for k in range(3):
            yy = 560 + k * 420; x0 = 60 if side < 0 else 1020
            dr.rrect(x0 - 220, yy + 90, x0 + 220, yy + 120, 6, (170, 176, 190))
            for j in range(4):
                px = x0 - 165 + j * 110; sw = 8 * math.sin(t * 2 + j + k)
                for (dx, dy, r) in ((0, 40, 52), (-38, 64, 38), (38, 64, 38), (sw, 0, 40)):
                    dr.ell(px + dx, yy + dy, r, r * 0.8, (70, 190, 90) if (j + k) % 2 else (50, 160, 80))
                if (j + k) % 3 == 0: dr.ell(px + 20, yy + 40, 14, 14, (230, 50, 50))   # tomates

def hojas_frente(dr, t, y=1750):
    for k in range(7):
        x = -60 + k * 190; sw = 10 * math.sin(t * 1.6 + k)
        dr.ell(x + sw, y + 40 * (k % 2), 150, 110, (40, 140, 70) if k % 2 else (56, 170, 84))

def tanque(dr, x, y, s, t, glow=0.0):
    S = lambda v: v * s
    dr.rrect(x - S(110), y - S(330), x + S(110), y + S(300), S(100), (60, 140, 230), True)
    dr.rrect(x - S(110), y - S(80), x + S(110), y - S(10), S(4), TURQ)
    dr.text(x, y + S(110), "O2", S(150), (255, 255, 255), stroke=6)
    dr.rrect(x - S(40), y - S(400), x + S(40), y - S(320), S(10), (150, 156, 170))
    dr.ell(x, y - S(410), S(56), S(20), (230, 70, 60))
    dr.line([(x - S(60), y - S(260)), (x - S(60), y + S(220))], (170, 220, 255), S(14), nolin=True)

def o2_hud(img, T):
    """Cuenta regresiva de oxígeno (tiempo de cómic): 10:00 → 5:00 entre el plano 8 y el dilema."""
    if T < STARTS[7] + 0.4: return
    d = ImageDraw.Draw(img)
    ok = STARTS[18] <= T < STARTS[22]
    if ok: txt, col, fg = "O2  TANQUE OK", (90, 210, 110), INK
    else:
        u = clamp((T - STARTS[7]) / (STARTS[22] - STARTS[7]))
        secs = int(600 - 300 * u) if T < STARTS[22] else 300
        txt, col, fg = f"O2  {secs // 60}:{secs % 60:02d}", (230, 40, 50) if int(T * 2) % 2 or T > STARTS[22] else (170, 20, 34), (255, 255, 255)
    f = font(46); w = f.getlength(txt) + 50
    d.rounded_rectangle([W - 36 - w, 186, W - 36, 250], radius=18, fill=col, outline=INK, width=5)
    d.text((W - 36 - w / 2, 218), txt, font=f, fill=fg, anchor="mm")

def notas(img, x, y, t, n=4):
    d = ImageDraw.Draw(img)
    for k in range(n):
        u = (t * 0.7 + k / n) % 1
        xx = x + 120 * math.sin(u * 6 + k) + (k - n / 2) * 50; yy = y - u * 300
        a = 1 - u
        if a < 0.2: continue
        r = 22 * (0.6 + 0.4 * a)
        d.ellipse([xx - r * 1.3, yy - r, xx + r * 1.3, yy + r], fill=(255, 120, 190), outline=INK, width=5)
        d.line([(xx + r * 1.1, yy), (xx + r * 1.1, yy - r * 4)], fill=INK, width=8)
        d.line([(xx + r * 1.1, yy - r * 4), (xx + r * 2.6, yy - r * 3)], fill=INK, width=8)

def medidor(img, x, y, pct, t, label="OXÍGENO"):
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([x - 300, y - 70, x + 300, y + 70], radius=30, fill=(20, 22, 34), outline=INK, width=8)
    w = 560 * pct
    if w > 20: d.rounded_rectangle([x - 280, y - 50, x - 280 + w, y + 50], radius=20, fill=(230, 40, 50) if pct < 0.3 else (90, 210, 110))
    d.text((x, y), f"{label} {int(round(pct * 100))} %", font=font(54), fill=(255, 255, 255), anchor="mm", stroke_width=7, stroke_fill=INK)

# ------------------------------------------------------------ planos
SHOTS = []
def shot(fn): SHOTS.append(fn); return fn
def tl(k, frac): return LEAD + len(VOZ[k]) / SR * frac

@shot
def s01(t, D, T):    # antes en la ruleta: caja + 12 zombis
    u = t / D
    cam = Cam(lerp(560, 760, ease(u)), lerp(1080, 880, ease(u)), lerp(1.0, 1.5, ease(u)))
    dr = D_(cam); estacion(dr, t, win=(820, 760, 250), horda=clamp(u * 1.5))
    caja(dr, 330, 1330, 0.75, t, 1.0)
    zastro(dr, 330, 1260, 0.42, t, mouth=0.4)
    f = rojo(tinta(dr), 0.25); img = acabado(f, T)
    k = eob(t / 0.3); d = ImageDraw.Draw(img)
    d.polygon([(0, 300), (W, 250), (W, 420), (0, 470)], fill=(230, 40, 50), outline=INK, width=8)
    d.text((540, 360), "ANTES EN…", font=font(int(80 * k) + 1), fill=(255, 255, 255), anchor="mm", stroke_width=8, stroke_fill=INK)
    if t > tl(0, 0.7): burst(img, "12 ZOMBIS", 540, 560, 110, t - tl(0, 0.7), col=(150, 240, 110), ang=-6)
    return img, 0

@shot
def s02(t, D, T):    # Nico eligió la opción dos: invernadero
    cam = Cam(540, 960, 1.0)
    dr = D_(cam, bg=(8, 10, 28)); estrellas(dr, t, 60, 11)
    capsula(dr, 270, 1080, 1.0, t)
    k = eob(t / 0.35)
    invernadero(dr, 800, 1080, 0.95 + 0.15 * k, t)
    f = tinta(dr)
    f[:, :540] *= 0.4
    img = acabado(f, T); d = ImageDraw.Draw(img)
    d.text((540, 330), "NICO ELIGIÓ…", font=font(84), fill=(255, 222, 40), anchor="mm", stroke_width=12, stroke_fill=INK)
    d.ellipse([720, 420, 880, 580], fill=(255, 255, 255), outline=INK, width=10); d.text((800, 502), "2", font=font(116), fill=INK, anchor="mm")
    d.text((800, 1440), "INVERNADERO", font=font(58), fill=(255, 255, 255), anchor="mm", stroke_width=8, stroke_fill=INK)
    if t > 0.3: d.line([(700, 800), (780, 900), (930, 680)], fill=(110, 230, 110), width=40, joint="curve")
    d.line([(150, 900), (390, 1260)], fill=(230, 40, 50), width=26); d.line([(390, 900), (150, 1260)], fill=(230, 40, 50), width=26)
    return img, 0

@shot
def s03(t, D, T):    # Nico: ¡Tuerca, al invernadero! (huyen por el pasillo)
    u = t / D
    cam = Cam(540, 1080, 1.55)
    dr = D_(cam); estacion(dr, t, win=None)
    zastro(dr, 980 - 80 * u, 1500, 0.45, t, mouth=0.5)
    nico(dr, 470 - 40 * u, 1660, 0.62, t, traje="astronauta", arms=(150, 60), elbows=(-10, 40), expr="shock", mouth=boca(2, t), look=(-0.8, 0), sweat=True)
    tuerca(dr, 180 - 60 * u, 1050, 0.55, t, alarm=True)
    f = rojo(tinta(dr), 0.4); img = acabado(f, T)
    burst(img, "¡YA, YA, YA!", 560, 440, 110, t - tl(2, 0.55), col=(255, 222, 40), ang=-6)
    return img, 3 + 3 * boca(2, t)

@shot
def s04(t, D, T):    # las plantas tapan el ruido, zombis pasan de largo
    cam = Cam(540, 1000, lerp(1.0, 1.1, ease(t / D)))
    dr = D_(cam); invernadero_bg(dr, t, zpass=t / D)
    nico(dr, 450, 1720, 0.58, t, traje="astronauta", arms=(20, 150), elbows=(0, 60), expr="nervous", look=(0.3, -0.6), sweat=True)
    tuerca(dr, 760, 1400, 0.55, t, look=(-0.3, -0.6))
    hojas_frente(dr, t, 1880)
    f = tinta(dr); add_glow(f, *cam.p(540, 710), 400, (240, 140, 255), 0.25)
    img = acabado(f, T)
    burst(img, "SHHH…", 540, 380, 100, t - 0.2, col=(200, 170, 255), ang=-5)
    return img, 0

@shot
def s05(t, D, T):    # Nico: funcionó, aquí nadie nos oye
    cam = Cam(540, 1080, 1.75)
    dr = D_(cam); invernadero_bg(dr, t)
    nico(dr, 540, 1660, 0.62, t, traje="astronauta", arms=(20, 140), elbows=(0, 70), expr="smug", mouth=boca(4, t) * 0.7, look=(0.4, 0))
    hojas_frente(dr, t, 1600)
    f = tinta(dr); img = acabado(f, T)
    return img, 0

@shot
def s06(t, D, T):    # Tuerca: afirmativo, y hay tomates
    cam = Cam(540, 1050, 1.3)
    dr = D_(cam); invernadero_bg(dr, t)
    x, y = tuerca(dr, 540, 1150, 1.15, t, mouth=boca(5, t))
    dr.ell(540 + 260, 1150 + 40 - 120 * 0.3, 52, 48, (230, 50, 50)); dr.ell(540 + 260, 1150 - 10 - 36, 22, 10, (60, 160, 70))
    f = tinta(dr); img = acabado(f, T)
    if t > tl(5, 0.45): burst(img, "¡TOMATES!", 540, 450, 110, t - tl(5, 0.45), col=(255, 90, 80), ang=6)
    return img, 0

@shot
def s07(t, D, T):    # la ruleta vuelve a girar → ??? = SIN OXÍGENO
    stop = T > STARTS[6] + tl(6, 0.72)
    cam = Cam(540, 1000, lerp(1.0, 1.12, ease(t / D)))
    dr = D_(cam); escenario_ruleta(dr, t); ruleta(dr, 540, 1080, 300, ang_ruleta(T), t, glow_seg=2 if stop else None)
    f = tinta(dr)
    for x in (300, 780): add_cono(f, x, -50, 1700, 60, 520, (255, 236, 180), 0.3)
    img = acabado(f, T)
    if stop:
        u = t - tl(6, 0.72)
        burst(img, "¡SIN OXÍGENO!", 540, 1500, 105, u, col=(120, 230, 255), ang=-5)
    return img, (2 * math.sin(T * 40) if not stop else 6 * math.exp(-(t - tl(6, 0.72)) * 5))

@shot
def s08(t, D, T):    # Tuerca: alerta silenciosa, oxígeno al 10 %
    cam = Cam(540, 1000, 1.2)
    dr = D_(cam); invernadero_bg(dr, t)
    tuerca(dr, 540, 1200, 1.1, t, mouth=boca(7, t), alarm=True)
    f = rojo(oscuro(tinta(dr), 0.75, (1, 0.9, 1.1)), 0.35 + 0.15 * math.sin(t * 6)); img = acabado(f, T)
    medidor(img, 540, 440, lerp(0.25, 0.10, ease(t / 0.8)), t)
    return img, 0

@shot
def s09(t, D, T):    # Nico: ¿diez por ciento? ¿y eso cuánto es?
    cam = Cam(540, 1080, 1.8)
    dr = D_(cam); invernadero_bg(dr, t)
    nico(dr, 540, 1660, 0.62, t, traje="astronauta", arms=(40, 120), elbows=(-50, 80), expr="worried", mouth=boca(8, t), look=(-0.5, -0.2))
    f = rojo(tinta(dr), 0.2); img = acabado(f, T)
    burst(img, "¿10 %?", 800, 470, 110, t - 0.1, col=(255, 222, 40), ang=8)
    return img, 0

@shot
def s10(t, D, T):    # Tuerca: diez minutos, nueve si sigues hablando
    cam = Cam(540, 1000, 1.0)
    dr = D_(cam, bg=(40, 16, 30))
    for k in range(18):
        a = k * math.pi / 9 + t * 0.4
        dr.poly([(540, 1150), (540 + math.cos(a) * 2000, 1150 + math.sin(a) * 2000), (540 + math.cos(a + 0.17) * 2000, 1150 + math.sin(a + 0.17) * 2000)], (64, 22, 40))
    tuerca(dr, 540, 1350, 1.0, t, mouth=boca(9, t), look=(0, 0.2))
    f = tinta(dr); img = acabado(f, T); d = ImageDraw.Draw(img)
    nine = t > tl(9, 0.45)
    k = eob((t - (tl(9, 0.45) if nine else 0)) / 0.25)
    d.rounded_rectangle([230, 360, 850, 600], radius=40, fill=(20, 22, 30), outline=INK, width=10)
    d.text((540, 480), "09:00" if nine else "10:00", font=font(int(150 * (0.7 + 0.3 * k))), fill=(255, 70, 60), anchor="mm")
    if nine: burst(img, "¡-1!", 860, 650, 100, t - tl(9, 0.45), col=(255, 222, 40), ang=10)
    return img, 0

@shot
def s11(t, D, T):    # dato: las plantas hacen oxígeno… muy despacio
    cam = Cam(540, 1050, 1.25)
    dr = D_(cam); invernadero_bg(dr, t)
    nico(dr, 380, 1800, 0.55, t, traje="astronauta", arms=(110, 20), elbows=(20, 0), expr="happy" if t < tl(10, 0.45) else "worried", look=(0.8, -0.4))
    for k in range(5):   # burbujitas de O2 muy lentas
        u = ((t * 0.12 + k * 0.2) % 1)
        dr.ell(760 + 30 * math.sin(k + t), 1250 - 300 * u, 22, 22, (170, 230, 255), nolin=True)
    f = tinta(dr); img = acabado(f, T); d = ImageDraw.Draw(img)
    d.polygon([(0, 300), (W, 240), (W, 400), (0, 460)], fill=(255, 214, 10), outline=INK, width=8)
    d.text((540, 350), "DATO REAL", font=font(76), fill=INK, anchor="mm")
    if t > tl(10, 0.45):
        k = eob((t - tl(10, 0.45)) / 0.3)
        d.rounded_rectangle([140, 500, 940, 620], radius=26, fill=(30, 20, 40), outline=INK, width=6)
        d.text((540, 560), "🐌 MUY LENTO" if False else "MUY, MUY LENTO", font=font(int(60 * k) + 1), fill=(255, 120, 100), anchor="mm")
    return img, 0

@shot
def s12(t, D, T):    # el tanque está en el módulo de al lado… lleno de zombis
    u = t / D
    cam = Cam(540, lerp(900, 1050, ease(u)), lerp(1.4, 1.0, ease(u)))
    dr = D_(cam); estacion(dr, t, win=None)
    tanque(dr, 540, 1150, 0.9, t)
    for k, (x, y, s) in enumerate(((200, 1500, 0.4), (860, 1550, 0.42), (360, 1950, 0.5), (760, 2000, 0.48), (540, 1000, 0.3))):
        if u > 0.35 or k == 4: zastro(dr, x + 30 * math.sin(t + k), y, s, t, ph=k, mouth=0.3)
    f = tinta(dr); f = f * np.array([0.9, 1.05, 0.88], np.float32); img = acabado(f, T)
    if u > 0.4: burst(img, "¡LLENO!", 540, 460, 120, t - 0.4 * D, col=(150, 240, 110), ang=-6)
    return img, 0

@shot
def s13(t, D, T):    # Nico: tengo una idea, Tuerca necesito tu voz
    cam = Cam(540, 1080, 1.75)
    dr = D_(cam); invernadero_bg(dr, t)
    nico(dr, 540, 1660, 0.62, t, traje="astronauta", arms=(20, 160), elbows=(0, 20), expr="smug", mouth=boca(12, t), look=(0.6, -0.2))
    f = tinta(dr); add_glow(f, 790, 520, 200, (255, 230, 120), 0.5); img = acabado(f, T)
    burst(img, "💡" if False else "¡IDEA!", 800, 480, 110, t - 0.1, col=(255, 222, 40), ang=8)
    return img, 0

@shot
def s14(t, D, T):    # Tuerca: ¿mi alarma? ¡por fin alguien la aprecia!
    cam = Cam(540, 1050, lerp(1.2, 1.35, ease(t / D)))
    dr = D_(cam); invernadero_bg(dr, t)
    tuerca(dr, 540, 1150 - 40 * math.sin(t * 5), 1.15, t, mouth=boca(13, t), look=(0, -0.3))
    f = tinta(dr); img = acabado(f, T); d = ImageDraw.Draw(img)
    for k in range(4):   # corazones
        u = (t * 0.6 + k * 0.25) % 1
        hx, hy, r = 300 + k * 160, 900 - u * 400, 26 * (1 - u * 0.5)
        d.polygon([(hx - r * 2, hy), (hx + r * 2, hy), (hx, hy + r * 2.4)], fill=(255, 90, 140), outline=INK)
        d.ellipse([hx - r * 2, hy - r * 1.1, hx, hy + r * 0.9], fill=(255, 90, 140)); d.ellipse([hx, hy - r * 1.1, hx + r * 2, hy + r * 0.9], fill=(255, 90, 140))
    if t > tl(13, 0.4): burst(img, "¡POR FIN!", 540, 440, 120, t - tl(13, 0.4), col=(255, 222, 40), ang=-6)
    return img, 0

@shot
def s15(t, D, T):    # Tuerca vuela al otro extremo de la estación
    u = t / D
    cam = Cam(540, 1000, 1.0)
    dr = D_(cam); espacio_fondo(dr, t)
    # la estación por fuera: módulos en fila
    for k in range(5):
        x = -100 + k * 300
        dr.rrect(x, 900, x + 260, 1130, 60, (220, 224, 232), True)
        dr.ell(x + 130, 1015, 40, 40, (20, 30, 60))
    for sx in (-1, 1): dr.rrect(540 + sx * 120 - 260, 760, 540 + sx * 120 + 260, 880, 6, (40, 70, 150))
    dr.ell(lerp(250, 1000, ease(u)), 820 - 60 * math.sin(u * 3), 26, 26, (255, 210, 60), nolin=True)
    tuerca(dr, lerp(250, 1000, ease(u)), 1350 - 80 * math.sin(u * 3), 0.42, t, look=(1, 0))
    f = tinta(dr); img = acabado(f, T)
    if u > 0.2: burst(img, "¡FIUUU!", 540, 520, 110, t - 0.2 * D, col=(120, 230, 255), ang=-6)
    return img, 0

@shot
def s16(t, D, T):    # Tuerca: ¡ALERTA! ¡CEREBROS GRATIS!
    cam = Cam(540, 1000, 1.25)
    dr = D_(cam); estacion(dr, t, win=None)
    tuerca(dr, 540, 1150, 1.4, t, mouth=boca(15, t), alarm=True)
    f = tinta(dr); f = rojo(f, 0.5 + 0.5 * math.sin(t * 14))
    img = acabado(f, T); d = ImageDraw.Draw(img)
    ondas(img, 540, 1100, t, (255, 90, 80), 3, 2.4)
    k = eob(t / 0.25)
    d.rounded_rectangle([110, 330, 970, 520], radius=30, fill=(255, 214, 10), outline=INK, width=10)
    d.text((540, 425), "CEREBROS GRATIS", font=font(int(80 * k) + 1), fill=(200, 30, 40), anchor="mm")
    return img, 6 + 6 * boca(15, t)

@shot
def s17(t, D, T):    # los doce zombis flotan hacia el ruido
    u = t / D
    cam = Cam(540, 1000, 1.0)
    dr = D_(cam); estacion(dr, t, win=None)
    for k in range(6):
        x = lerp(-200 + (k % 3) * 220, 1300 + (k % 3) * 200, ease(clamp(u * 0.75 - k * 0.04)))
        zastro(dr, x, 1350 + (k // 3) * 450 + 40 * math.sin(t * 2 + k), 0.36 + 0.06 * (k // 3), t, ph=k, mouth=0.5, turn=1.0)
    f = tinta(dr); img = acabado(f, T)
    ondas(img, 1000, 900, t, (255, 90, 80), 3, 1.4)
    burst(img, "→ ¡RUIDO!", 700, 460, 100, t - 0.1, col=(255, 222, 40), ang=-5)
    return img, 0

@shot
def s18(t, D, T):    # Nico cruza el módulo vacío hasta el tanque
    u = t / D
    cam = Cam(lerp(420, 640, ease(u)), 1050, 1.1)
    dr = D_(cam); estacion(dr, t, win=None)
    tanque(dr, 820, 1250, 0.8, t)
    rot = math.sin(t * 2) * 15
    nico(dr, lerp(120, 560, ease(u)), 1700 + 30 * math.sin(t * 2), 0.55, t, traje="astronauta", arms=(100 + rot, 110 - rot), elbows=(10, -10), expr="nervous", look=(1, 0), sweat=True)
    f = oscuro(tinta(dr), 0.8, (0.9, 0.95, 1.15)); img = acabado(f, T)
    burst(img, "PUNTITAS…", 540, 440, 90, t - 0.2, col=(200, 220, 255), ang=-5)
    return img, 0

@shot
def s19(t, D, T):    # Nico: ¡lo tengo! ¡aire para un mes!
    cam = Cam(560, 1080, 1.45)
    dr = D_(cam); estacion(dr, t, win=None)
    tanque(dr, 700, 1300, 0.75, t)
    nico(dr, 470, 1660, 0.6, t, traje="astronauta", arms=(60, 140), elbows=(60, 20), expr="happy_eyes", mouth=boca(18, t), look=(0.3, 0))
    f = tinta(dr); add_glow(f, *cam.p(700, 1300), 260, (120, 200, 255), 0.4); img = acabado(f, T)
    burst(img, "¡AIRE!", 560, 460, 140, t - 0.1, col=(120, 230, 255), ang=-6)
    return img, 0

@shot
def s20(t, D, T):    # al darse la vuelta… un zombi no se fue
    u = t / D
    cam = Cam(540, 1050, lerp(1.0, 1.3, ease(u)))
    dr = D_(cam); estacion(dr, t, win=None)
    tanque(dr, 150, 1400, 0.45, t)
    if u > 0.45: zastro(dr, 800, 1650, 0.62, t, mouth=0.3, phones=True, turn=-0.5)
    nico(dr, 360, 1760, 0.56, t, traje="astronauta", arms=(70, 70) if u < 0.45 else (160, 160), elbows=(60, 60) if u < 0.45 else (20, 20), expr="happy" if u < 0.45 else "shock", look=(1, -0.3) if u > 0.45 else (-0.6, 0))
    f = tinta(dr); img = acabado(f, T)
    if u > 0.5: burst(img, "¡GLUP!", 300, 460, 120, t - 0.5 * D, col=(255, 222, 40), ang=-8)
    return img, (5 * math.exp(-(t - 0.45 * D) * 5) if u > 0.45 else 0)

@shot
def s21(t, D, T):    # no oyó a Tuerca: tiene audífonos
    cam = Cam(540, 1050, lerp(1.35, 1.55, ease(t / D)))
    dr = D_(cam); estacion(dr, t, win=None)
    zastro(dr, 540 + 30 * math.sin(t * 3), 1720, 0.85, t, mouth=0.25 + 0.2 * math.sin(t * 6), phones=True, turn=0.3 * math.sin(t * 4))
    f = tinta(dr); f = f * np.array([0.95, 1.04, 0.95], np.float32); img = acabado(f, T)
    notas(img, 540, 820, t, 5)
    if t > tl(20, 0.5): tarjeta_nombre(img, t - tl(20, 0.5), "ZOMBI DJ", "no oye nada: tiene audífonos")
    return img, 0

@shot
def s22(t, D, T):    # grrr… cerebrooo
    cam = Cam(540, 1050, 1.7)
    dr = D_(cam); estacion(dr, t, win=None)
    zastro(dr, 540, 1760, 0.9, t, mouth=boca(21, t), phones=True)
    f = rojo(tinta(dr), 0.35); img = acabado(f, T)
    burst(img, "¡GRRR!", 540, 450, 140, t - 0.05, col=(150, 240, 110), ang=-6)
    return img, 3 + 4 * boca(21, t)

@shot
def s23(t, D, T):    # dilema: 1 quitarle los audífonos · 2 lanzarle el tanque
    cam = Cam(540, 960, 1.0)
    dr = D_(cam, bg=(8, 10, 28))
    estrellas(dr, t, 60, 11)
    dr.poly([(470, -100), (610, -100), (610, 2600), (470, 2600)], (20, 16, 26))
    o1 = t > tl(22, 0.02); o2 = t > tl(22, 0.5)
    if o1:
        k1 = eob((t - tl(22, 0.02)) / 0.3)
        zastro(dr, 270, 1380, 0.36 * k1 + 0.01, t, mouth=0.3, phones=int(t * 2) % 2 == 0)
    if o2:
        k2 = eob((t - tl(22, 0.5)) / 0.3)
        tanque(dr, 810 + 40 * math.sin(t * 3), 1080, 0.55 * k2 + 0.01, t)
    nico(dr, 540, 1760, 0.42, t, traje="astronauta", arms=(70, 70), elbows=(60, 60), expr="nervous", look=(-0.8 if t < tl(22, 0.5) else 0.8, -0.3))
    f = tinta(dr); img = acabado(f, T); d = ImageDraw.Draw(img)
    d.text((540, 300), "¿QUÉ HARÍA NICO?", font=font(82), fill=(255, 222, 40), anchor="mm", stroke_width=12, stroke_fill=INK)
    for ok, x, n, a, b in ((o1, 270, "1", "QUITARLE", "LOS AUDÍFONOS"), (o2, 810, "2", "LANZARLE", "EL TANQUE")):
        if not ok: continue
        d.ellipse([x - 80, 400, x + 80, 560], fill=(255, 255, 255), outline=INK, width=10)
        d.text((x, 482), n, font=font(116), fill=INK, anchor="mm")
        d.text((x, 640), a, font=font(52), fill=(255, 255, 255), anchor="mm", stroke_width=7, stroke_fill=INK)
        d.text((x, 700), b, font=font(40), fill=(255, 222, 40), anchor="mm", stroke_width=6, stroke_fill=INK)
    if o1: d.text((270, 1460), "…te oirá a ti", font=font(38), fill=(255, 255, 255), anchor="mm", stroke_width=5, stroke_fill=INK)
    if o2: d.text((810, 1460), "…5 min de aire", font=font(38), fill=(255, 255, 255), anchor="mm", stroke_width=5, stroke_fill=INK)
    return img, 0

@shot
def s24(t, D, T):    # comenta 1 o 2
    cam = Cam(540, 1000, 1.0)
    dr = D_(cam, bg=(230, 40, 50))
    for k in range(18):
        a = k * math.pi / 9 + t * 0.5
        dr.poly([(540, 1150), (540 + math.cos(a) * 2000, 1150 + math.sin(a) * 2000), (540 + math.cos(a + 0.17) * 2000, 1150 + math.sin(a + 0.17) * 2000)], (200, 30, 44))
    nico(dr, 540, 1880, 0.72, t, traje="astronauta", arms=(20, 100), elbows=(0, 60), expr="smug", look=(0, 0.2))
    f = tinta(dr); img = acabado(f, T); d = ImageDraw.Draw(img)
    k = eob(t / 0.3)
    d.rounded_rectangle([140, 290, 940, 450], radius=44, fill=(255, 214, 10), outline=INK, width=10)
    d.text((540, 370), "COMENTA 1 o 2", font=font(int(92 * k) + 1), fill=INK, anchor="mm")
    if t > tl(23, 0.45):
        kk = eob((t - tl(23, 0.45)) / 0.3)
        d.text((540, 520), "En el capítulo final", font=font(int(52 * kk) + 1), fill=(255, 255, 255), anchor="mm", stroke_width=7, stroke_fill=INK)
        d.text((540, 590), "verás si elegiste bien", font=font(int(52 * kk) + 1), fill=(255, 255, 255), anchor="mm", stroke_width=7, stroke_fill=INK)
    return img, 0

@shot
def s25(t, D, T):    # nos vemos en otro mundo hipotético… si me queda aire
    cam = Cam(540, 1000, 1.0)
    dr = D_(cam); espacio_fondo(dr, t)
    o = 1 - ease((t - D + 1.0) / 0.8)
    portal(dr, 540, 1000, 330, t, o)
    zastro(dr, 900, 1500, 0.32, t, mouth=0.4, ph=1.0, phones=True)
    if t < D - 1.0: nico(dr, 540, 1460, 0.5, t, traje="astronauta", arms=(150, 20), elbows=(30, 0), expr="nervous" if t > tl(24, 0.6) else "happy", mouth=boca(24, t), look=(0.6 if t > tl(24, 0.6) else 0, 0))
    f = tinta(dr); add_glow(f, *cam.p(540, 1000), 450, (150, 120, 255), 0.5 * o)
    img = acabado(f, T); d = ImageDraw.Draw(img)
    d.rounded_rectangle([150, 380, 930, 560], radius=36, fill=(255, 214, 10), outline=INK, width=8)
    d.text((540, 440), "CAPÍTULO 3 · FINAL", font=font(60), fill=INK, anchor="mm")
    d.text((540, 510), "MAÑANA · 6 P. M.", font=font(46), fill=(200, 40, 50), anchor="mm")
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
    if i < 23: o2_hud(img, T)
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
    wh = bp(400, 3500); low = sosfilt(butter(2, 180, btype="low", fs=sr, output="sos"), noise)
    S_ = STARTS
    def synth(s, tend, g=1.0, dark=False):
        e = 0.16
        prog = [[57, 60, 64, 69], [53, 57, 60, 65], [55, 59, 62, 67], [52, 56, 59, 64]] if not dark else [[45, 48, 51, 57], [44, 47, 50, 56]]
        k = 0
        while s < tend:
            ch = prog[(k // 16) % len(prog)]; m = ch[k % 4] + (12 if (k // 4) % 2 else 0)
            x = seg(e * 1.6)
            tri = 2 * np.abs(2 * ((hz(m) * x) % 1) - 1) - 1
            add(s, g * 0.04 * tri * np.exp(-x * 6) * (1 - np.exp(-x * 80)))
            if k % 8 == 0:
                xb = seg(e * 8); add(s, g * 0.08 * np.sin(2 * np.pi * hz(ch[0] - 24) * xb) * np.exp(-xb * 0.8))
            if k % 4 == 0 and not dark:
                add(s, g * 0.14 * np.exp(-x * 22) * np.sin(2 * np.pi * (60 + 50 * np.exp(-x * 30)) * x))
            if k % 4 == 2 and not dark: add(s, g * 0.03 * rng.standard_normal(len(x)) * np.exp(-x * 40))
            k += 1; s += e
    def dron(s, tend, g=0.08):
        xd = seg(tend - s); add(s, g * (np.sin(2 * np.pi * 41 * xd) + 0.5 * np.sin(2 * np.pi * 61.7 * xd)) * np.clip(xd / 1.5, 0, 1))
    def alarma(s, d, g=0.07):
        for kk in range(int(d / 0.5)):
            x = seg(0.25); add(s + kk * 0.5, g * np.sign(np.sin(2 * np.pi * (880 if kk % 2 else 660) * x)) * (1 - np.exp(-x * 80)))
    def tic(s, tend, g=0.06, per=1.0):
        kk = 0
        while s + kk * per < tend:
            x = seg(0.05); add(s + kk * per, g * np.exp(-x * 120) * np.sin(2 * np.pi * (1500 if kk % 2 else 1100) * x)); kk += 1
    # recap + huida
    dron(0, S_[1], 0.07); synth(S_[0], S_[1], 0.5, dark=True)
    x = seg(0.8); add(S_[1] + 0.3, 0.25 * np.exp(-x * 4) * (np.sin(2 * np.pi * 523 * x) + np.sin(2 * np.pi * 659 * x)) / 2)
    alarma(S_[2], DURS[2], 0.07); synth(S_[2], S_[3], 0.8)
    # invernadero tranquilo
    synth(S_[3], S_[6], 0.45)
    # ruleta
    t0, t1 = S_[6] + 0.05, S_[6] + tl(6, 0.72)
    xr = seg(t1 - t0); add(t0, 0.06 * bp(150, 600)[:len(xr)] * (0.6 + 0.4 * np.sin(2 * np.pi * 18 * xr)))
    prev = int(ang_ruleta(t0) / 22.5)
    for k in range(int((t1 - t0) * FPS) + 2):
        T = t0 + k / FPS; a = ang_ruleta(T)
        if int(a / 22.5) != prev:
            prev = int(a / 22.5); xc = seg(0.03); add(T, 0.25 * np.exp(-xc * 200) * np.sin(2 * np.pi * 2500 * xc))
    x = seg(1.2); add(t1, 0.35 * np.exp(-x * 2.5) * (np.sin(2 * np.pi * 311 * x) + np.sin(2 * np.pi * 370 * x) + np.sin(2 * np.pi * 440 * x)) / 3)
    # oxígeno: reloj + dron
    tic(S_[7], S_[18], 0.05, 1.0)
    dron(S_[7], S_[12], 0.06); synth(S_[7], S_[12], 0.5, dark=True)
    synth(S_[12], S_[15], 0.7)
    x = seg(1.0); add(S_[14] + 0.3, 0.3 * wh[:len(x)] * np.sin(np.pi * x / 1.0))
    alarma(S_[15], DURS[15], 0.1)
    dron(S_[16], S_[18], 0.08); synth(S_[16], S_[18], 0.7, dark=True)
    x = seg(1.0); add(S_[18], 0.3 * np.exp(-x * 2) * (np.sin(2 * np.pi * 523 * x) + np.sin(2 * np.pi * 659 * x) + np.sin(2 * np.pi * 784 * x)) / 3)
    synth(S_[18], S_[19] + DURS[19] * 0.45, 0.7)
    x = seg(1.4); add(S_[19] + DURS[19] * 0.45, 0.35 * np.exp(-x * 2) * (np.sin(2 * np.pi * 233 * x) + np.sin(2 * np.pi * 277 * x) + np.sin(2 * np.pi * 330 * x)) / 3)
    x = seg(0.4); add(S_[19] + DURS[19] * 0.45, 0.4 * low[:len(x)] * np.exp(-x * 6))
    # música de los audífonos (bajito, "sale" del audífono)
    s = S_[20]; kk = 0
    while s < S_[22]:
        x = seg(0.12); add(s, 0.05 * np.sign(np.sin(2 * np.pi * hz([72, 76, 79, 76][kk % 4]) * x)) * np.exp(-x * 20)); s += 0.18; kk += 1
    dron(S_[20], S_[22], 0.08)
    # dilema + cierre
    for kk in range(int((S_[24] - S_[22]) / 0.6)):
        x = seg(0.3); add(S_[22] + kk * 0.6, 0.12 * np.exp(-x * 10) * np.sin(2 * np.pi * (55 + 20 * (kk % 2)) * x))
        x = seg(0.08); add(S_[22] + kk * 0.6 + 0.3, 0.05 * np.exp(-x * 60) * np.sin(2 * np.pi * 1200 * x))
    synth(S_[24], TOTAL, 0.6)
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
    if os.environ.get("RANGE"):   # render de un tramo (sin audio) para paralelizar
        a, b = [int(v) for v in os.environ["RANGE"].split(",")]
        p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                              "-c:v", "libx264", "-preset", "veryfast", "-crf", "26", "-tune", "animation", "-pix_fmt", "yuv420p", OUT], stdin=subprocess.PIPE)
        for k in range(a, b):
            p.stdin.write(frame(k / FPS).convert("RGB").tobytes())
            if k % 300 == 0: print(f"{k}/{b}", flush=True)
        p.stdin.close(); p.wait(); print("tramo listo", OUT); sys.exit()
    print("NFRAMES", int(TOTAL * FPS))
