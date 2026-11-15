#!/usr/bin/env python3
"""LA RULETA DE NICO · Temporada 2: ZOMBIS EN EL ESPACIO · Capítulo 1/3.
Empate 3-3 (zombis vs espacio) → la ruleta junta los dos. Regla: los zombis no ven, flotan hacia el ruido.
Dilema: 1 cápsula de escape / 2 invernadero espacial."""
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
    [("Ustedes votaron…", ["votaron…"]), ("y quedó empate:", ["empate:"]), ("¡tres a tres!", ["tres", "tres!"]), ("Zombis contra espacio", ["Zombis", "espacio"])],
    [("Así que la ruleta", ["ruleta"]), ("decidió…", []), ("¡juntarlos!", ["¡juntarlos!"])],
    [("¿Zombis…", ["¿Zombis…"]), ("en el espacio?", ["espacio?"]), ("¡Eso ni existe!", ["existe!"])],
    [("Nico cruza el portal…", ["portal…"]), ("y aparece en", []), ("una estación espacial,", ["estación", "espacial,"]), ("a 400 kilómetros", ["400"]), ("de la Tierra", ["Tierra"])],
    [("¡Bienvenido a bordo!", ["bordo!"]), ("Soy Tuerca.", ["Tuerca."]), ("Tranquilo,", []), ("aquí nunca pasa nada", ["nada"])],
    [("Spoiler:", ["Spoiler:"]), ("sí pasa.", ["pasa."]), ("Un cohete de carga", ["cohete"]), ("trajo una caja…", ["caja…"]), ("que dice:", []), ("NO ABRIR", ["NO", "ABRIR"])],
    [("¿Y si es comida?", ["comida?"]), ("Llevo tres días", ["tres"]), ("comiendo", []), ("pasta de tubo", ["tubo"])],
    [("Nico la abre…", ["abre…"]), ("y adentro hay", []), ("un astronauta verde", ["verde"]), ("que lleva meses", ["meses"]), ("flotando", ["flotando"])],
    [("Grrr…", ["Grrr…"]), ("cerebrooo…", ["cerebrooo…"]), ("en gravedad", []), ("cerooo…", ["cerooo…"])],
    [("La regla de", []), ("estos zombis:", ["zombis:"]), ("no ven nada…", ["nada…"]), ("pero flotan hacia", []), ("cualquier ruido", ["ruido"])],
    [("Ok.", []), ("Silencio total.", ["Silencio"]), ("Puedo hacerlo.", ["hacerlo."])],
    [("Pero en una estación", []), ("nada es silencioso:", ["silencioso:"]), ("ventiladores,", ["ventiladores,"]), ("alarmas…", ["alarmas…"]), ("y Tuerca", ["Tuerca"])],
    [("¡ALERTA!", ["¡ALERTA!"]), ("¡ZOMBI A BORDO!", ["ZOMBI"]), ("¡ALERTA, ALERTA!", ["ALERTA!"])],
    [("¡Tuerca,", []), ("cállate!", ["cállate!"])],
    [("El zombi gira", ["zombi"]), ("la cabeza…", ["cabeza…"]), ("y se impulsa", ["impulsa"]), ("hacia ellos", ["ellos"])],
    [("Nico flota", []), ("hacia atrás…", ["atrás…"]), ("y por la ventana", ["ventana"]), ("ve más astronautas", ["más"]), ("flotando hacia", []), ("la estación", ["estación"])],
    [("Tuerca…", []), ("¿cuántos astronautas", ["cuántos"]), ("había aquí?", ["aquí?"])],
    [("Antes eran doce.", ["doce."]), ("Ahora son…", []), ("doce zombis", ["zombis"])],
    [("Uno:", ["Uno:"]), ("la cápsula de escape", ["cápsula"]), ("a la Tierra…", ["Tierra…"]), ("con un zombi", ["zombi"]), ("pegado afuera.", ["afuera."]), ("Dos:", ["Dos:"]), ("el invernadero", ["invernadero"]), ("donde las plantas", ["plantas"]), ("tapan el ruido…", ["ruido…"]), ("pero no hay salida", ["salida"])],
    [("¿Qué haría Nico?", ["Nico?"]), ("Comenta 1 o 2.", ["1", "2."]), ("En la próxima parte", []), ("verás si", []), ("elegiste bien", ["bien"])],
    [("Nos vemos en otro", []), ("mundo hipotético…", ["hipotético…"]), ("si sobrevivo", ["sobrevivo"])],
]
DURS[1] += 0.4; DURS[18] += 0.4; DURS[19] += 0.5; DURS[20] += 0.6
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

def badge(img, T):
    d = ImageDraw.Draw(img)
    f = font(36)
    d.rounded_rectangle([36, 110, 36 + f.getlength("LA RULETA DE NICO") + 44, 170], radius=16, fill=(230, 40, 50), outline=INK, width=5)
    d.text((58, 140), "LA RULETA DE NICO", font=f, fill=(255, 255, 255), anchor="lm")
    f2 = font(36); txt = "CAPÍTULO 3/3"
    x1 = W - 36; x0 = x1 - f2.getlength(txt) - 44
    d.rounded_rectangle([x0, 110, x1, 170], radius=16, fill=(255, 214, 10), outline=INK, width=5)
    d.text((x0 + 22, 140), txt, font=f2, fill=INK, anchor="lm")


def badge(img, T):
    d = ImageDraw.Draw(img)
    f = font(36)
    d.rounded_rectangle([36, 110, 36 + f.getlength("LA RULETA DE NICO") + 44, 170], radius=16, fill=(230, 40, 50), outline=INK, width=5)
    d.text((58, 140), "LA RULETA DE NICO", font=f, fill=(255, 255, 255), anchor="lm")
    txt = "CAPÍTULO 1/3"
    x1 = W - 36; x0 = x1 - f.getlength(txt) - 44
    d.rounded_rectangle([x0, 110, x1, 170], radius=16, fill=(255, 214, 10), outline=INK, width=5)
    d.text((x0 + 22, 140), txt, font=f, fill=INK, anchor="lm")
    f2 = font(30); t2 = "ZOMBIS EN EL ESPACIO"
    d.rounded_rectangle([36, 182, 36 + f2.getlength(t2) + 40, 230], radius=14, fill=(110, 200, 90), outline=INK, width=4)
    d.text((56, 206), t2, font=f2, fill=INK, anchor="lm")

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
def zastro(dr, x, y, s, t, mouth=0.0, ph=0.0, helmet=True, turn=0.0, arms=1.0):
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
    t0, t1 = STARTS[1] + 0.05, STARTS[2] - 0.55
    final = -90 - 360 * 4
    if T < t0: return 0.0
    u = clamp((T - t0) / (t1 - t0))
    return final * (1 - (1 - u) ** 3)

# ------------------------------------------------------------ planos
SHOTS = []
def shot(fn): SHOTS.append(fn); return fn
def tl(k, frac): return LEAD + len(VOZ[k]) / SR * frac

@shot
def s01(t, D, T):    # votos: empate 3 a 3
    cam = Cam(540, 1000, 1.0)
    dr = D_(cam); escenario_ruleta(dr, t, 0.0)
    nico(dr, 540, 1700, 0.55, t, traje="sudadera", arms=(60, 60), elbows=(70, 70), expr="nervous", look=(-0.8 if (t % 1.2) < 0.6 else 0.8, -0.2))
    f = tinta(dr)
    for x in (270, 810): add_cono(f, x, -50, 1700, 60, 520, (255, 236, 180), 0.25)
    img = acabado(f, T); d = ImageDraw.Draw(img)
    d.text((540, 330), "USTEDES VOTARON", font=font(78), fill=(255, 222, 40), anchor="mm", stroke_width=10, stroke_fill=INK)
    k = ease(t / max(0.1, tl(0, 0.35)))
    for row, (n, lab, col) in enumerate((("1", "ZOMBIS", (110, 190, 90)), ("2", "ESPACIO", (130, 90, 220)))):
        y = 440 + row * 150
        d.rounded_rectangle([90, y, 990, y + 110], radius=24, fill=(30, 20, 40), outline=INK, width=6)
        w = 380 * k
        if w > 30: d.rounded_rectangle([210, y + 14, 210 + w, y + 96], radius=18, fill=col)
        d.ellipse([104, y + 8, 196, y + 100], fill=(255, 255, 255), outline=INK, width=6)
        d.text((150, y + 55), n, font=font(64), fill=INK, anchor="mm")
        d.text((236, y + 55), lab, font=font(44), fill=(255, 255, 255), anchor="lm", stroke_width=6, stroke_fill=INK)
        d.text((960, y + 55), f"{int(round(3 * k))} VOTOS", font=font(44), fill=(255, 255, 255), anchor="rm", stroke_width=6, stroke_fill=INK)
    if t > tl(0, 0.5): burst(img, "¡EMPATE!", 540, 860, 130, t - tl(0, 0.5), col=(255, 90, 60), ang=-6)
    return img, 0

@shot
def s02(t, D, T):    # la ruleta decide juntarlos
    stop = T > STARTS[2] - 0.55
    cam = Cam(540, 1000, lerp(1.0, 1.12, ease(t / D)))
    dr = D_(cam); escenario_ruleta(dr, t); ruleta(dr, 540, 1080, 300, ang_ruleta(T), t, glow_seg=2 if stop else None)
    f = tinta(dr)
    for x in (300, 780): add_cono(f, x, -50, 1700, 60, 520, (255, 236, 180), 0.3)
    img = acabado(f, T)
    if stop:
        u = t - (D - 0.55 - 0.0) + 0.0
        burst(img, "ZOMBIS", 300, 330, 110, u, col=(130, 220, 100), ang=-8)
        burst(img, "+", 545, 340, 130, u - 0.05, col=(255, 255, 255), ang=0)
        burst(img, "ESPACIO", 790, 350, 100, u - 0.1, col=(190, 150, 255), ang=8)
    return img, (2 * math.sin(T * 40) if not stop else 6 * math.exp(-(t - D + 0.55) * 5))

@shot
def s03(t, D, T):    # Nico: ¿zombis en el espacio?
    cam = Cam(540, 1080, 1.65)
    dr = D_(cam); escenario_ruleta(dr, t, 0.0)
    nico(dr, 540, 1660, 0.62, t, traje="sudadera", arms=(140, 140), elbows=(40, 40), expr="shock" if t < tl(2, 0.55) else "angry", mouth=boca(2, t), look=(0, -0.2))
    f = tinta(dr); add_cono(f, 540, -50, 1700, 60, 700, (255, 236, 180), 0.3)
    img = acabado(f, T)
    burst(img, "¿¡QUÉ!?", 780, 470, 120, t - 0.1, col=(255, 222, 40), ang=8)
    return img, 3 * boca(2, t)

@shot
def s04(t, D, T):    # portal → estación espacial a 400 km
    u = t / D
    if u < 0.32:
        cam = Cam(540, 1000, lerp(1.0, 1.6, ease(u / 0.32)))
        dr = D_(cam, bg=(18, 10, 30)); escenario_ruleta(dr, t, 0.0)
        portal(dr, 540, 1050, 330, t, 1.0)
        nico(dr, 540, 1640 - 300 * ease(u / 0.32), 0.5 * (1 - 0.6 * ease(u / 0.32)), t, traje="sudadera", arms=(160, 160), elbows=(10, 10), expr="shock")
        f = tinta(dr); add_glow(f, *cam.p(540, 1050), 450, (150, 120, 255), 0.6)
        return acabado(f, T), 4
    cam = Cam(540, lerp(980, 1040, ease((u - 0.32) / 0.68)), 1.0)
    dr = D_(cam); estacion(dr, t)
    rot = math.sin(t * 0.9) * 12
    nico(dr, 450, 1640 + 30 * math.sin(t * 1.5), 0.7, t, traje="astronauta", arms=(110 + rot, 120 - rot), elbows=(20, -20), expr="shock" if u < 0.6 else "happy", look=(0.6, -0.3))
    f = tinta(dr); add_glow(f, *cam.p(820, 760), 300, (120, 190, 255), 0.3)
    img = acabado(f, T); d = ImageDraw.Draw(img)
    if u > 0.45:
        k = eob((u - 0.45) / 0.1)
        d.rounded_rectangle([110, 270, 970, 390], radius=30, fill=(30, 34, 60), outline=INK, width=6)
        d.text((540, 330), "ESTACIÓN ESPACIAL · 400 KM", font=font(int(52 * k) + 1), fill=(120, 230, 255), anchor="mm", stroke_width=5, stroke_fill=INK)
    if u < 0.4: burst(img, "¡FLOP!", 540, 420, 110, t - 0.32 * D, col=(120, 230, 255), ang=-6)
    return img, 0

@shot
def s05(t, D, T):    # Tuerca: bienvenido
    cam = Cam(540, 1000, lerp(1.1, 1.2, ease(t / D)))
    dr = D_(cam); estacion(dr, t)
    nico(dr, 280, 1900 + 20 * math.sin(t * 1.5), 0.5, t, traje="astronauta", arms=(40, 70), elbows=(30, 40), expr="happy", look=(1, -0.4))
    tuerca(dr, 680, 1150, 1.2, t, mouth=boca(4, t), look=(-0.6, 0))
    f = tinta(dr); img = acabado(f, T)
    tarjeta_nombre(img, t, "TUERCA", "el robot de la estación")
    return img, 0

@shot
def s06(t, D, T):    # spoiler: sí pasa — la caja NO ABRIR
    cam = Cam(540, 1050, lerp(1.0, 1.25, ease(t / D)))
    dr = D_(cam); estacion(dr, t)
    caja(dr, 540 + 20 * math.sin(t), 1150 + 20 * math.sin(t * 1.3), 1.25, t)
    f = tinta(dr)
    al = 0.5 + 0.5 * math.sin(t * 9) if t < tl(5, 0.3) else 0.25
    f = rojo(f, al)
    img = acabado(f, T); d = ImageDraw.Draw(img)
    if t < tl(5, 0.3): burst(img, "¡SPOILER!", 540, 420, 120, t - 0.1, col=(255, 80, 60), ang=-6)
    else:
        k = eob((t - tl(5, 0.3)) / 0.3)
        d.rounded_rectangle([170, 360, 910, 470], radius=26, fill=(255, 214, 10), outline=INK, width=6)
        d.text((540, 415), "CARGA DESDE LA TIERRA", font=font(int(50 * k) + 1), fill=INK, anchor="mm")
    return img, 0

@shot
def s07(t, D, T):    # Nico: ¿y si es comida? pasta de tubo
    cam = Cam(540, 1080, 1.7)
    dr = D_(cam); estacion(dr, t, win=None)
    info = nico(dr, 520, 1660, 0.62, t, traje="astronauta", arms=(20, 150), elbows=(0, 40), expr="worried" if t > tl(6, 0.4) else "happy", mouth=boca(6, t), look=(0.6, 0))
    hx, hy = info["hands"][1]
    tubo(dr, hx + 10, hy - 60, 1.3)
    f = tinta(dr); img = acabado(f, T)
    if t > tl(6, 0.5): burst(img, "3 DÍAS", 800, 470, 100, t - tl(6, 0.5), col=(255, 222, 40), ang=8)
    return img, 0

@shot
def s08(t, D, T):    # abre la caja: astronauta verde
    cam = Cam(540, 1050, 1.0)
    dr = D_(cam); estacion(dr, t)
    op = ease((t - 0.3) / 0.6)
    rise = ease((t - tl(7, 0.35)) / 1.2)
    if rise > 0: zastro(dr, 600, 1500 - 150 * rise, 0.62 * (0.5 + 0.5 * rise), t, mouth=0.4, arms=rise)
    caja(dr, 560, 1420, 1.0, t, op)
    if op > 0.1: gas(dr, 560, 1300, t, (0.5 + 0.3 * op) * (1 - 0.6 * rise))
    nico(dr, 220, 1950, 0.5, t, traje="astronauta", arms=(150, 150), elbows=(30, 30), expr="shock" if rise > 0.1 else "happy", look=(1, -0.5))
    f = tinta(dr); f = f * np.array([0.92, 1.04, 0.9], np.float32)
    img = acabado(f, T)
    if t > 0.3: burst(img, "¡CRAC!", 760, 420, 120, t - 0.3, col=(150, 240, 110), ang=7)
    return img, (8 * math.exp(-(t - 0.3) * 4) if t > 0.3 else 0)

@shot
def s09(t, D, T):    # zombi: cerebrooo en gravedad cerooo
    cam = Cam(540, 1050, lerp(1.35, 1.5, ease(t / D)))
    dr = D_(cam); estacion(dr, t, win=None)
    zastro(dr, 540, 1900, 0.85, t, mouth=boca(8, t), arms=1.0)
    f = tinta(dr); f = f * np.array([0.9, 1.05, 0.88], np.float32)
    img = acabado(f, T)
    tarjeta_nombre(img, t, "ZOMBI ESPACIAL", "lleva meses flotando")
    return img, 3 * boca(8, t)

@shot
def s10(t, D, T):    # la regla: no ven nada, flotan hacia el ruido
    cam = Cam(540, 1000, 1.0)
    dr = D_(cam, bg=(30, 20, 50))
    for k in range(18):
        a = k * math.pi / 9 + t * 0.3
        dr.poly([(540, 1100), (540 + math.cos(a) * 2000, 1100 + math.sin(a) * 2000), (540 + math.cos(a + 0.17) * 2000, 1100 + math.sin(a + 0.17) * 2000)], (44, 30, 70))
    zastro(dr, 540 + 140 * math.sin(t * 2.2) * (t > tl(9, 0.55)), 1900, 0.72, t, mouth=0.3)
    f = tinta(dr); img = acabado(f, T); d = ImageDraw.Draw(img)
    d.polygon([(0, 300), (W, 230), (W, 410), (0, 480)], fill=(110, 200, 90), outline=INK, width=8)
    d.text((540, 355), "REGLA DE LA SERIE", font=font(70), fill=INK, anchor="mm")
    if t > tl(9, 0.3):
        k = eob((t - tl(9, 0.3)) / 0.3)
        d.rounded_rectangle([90, 520, 520, 640], radius=26, fill=(30, 20, 40), outline=INK, width=6)
        d.text((305, 580), "✗ NO VEN", font=font(int(56 * k) + 1), fill=(255, 90, 80), anchor="mm")
    if t > tl(9, 0.6):
        k = eob((t - tl(9, 0.6)) / 0.3)
        d.rounded_rectangle([560, 520, 990, 640], radius=26, fill=(30, 20, 40), outline=INK, width=6)
        d.text((775, 580), "¡OYEN TODO!", font=font(int(52 * k) + 1), fill=(255, 222, 40), anchor="mm")
        ondas(img, 540, 960, t, (255, 222, 40), 3, 1.4)
    return img, 0

@shot
def s11(t, D, T):    # Nico susurra: silencio total
    cam = Cam(540, 1080, 1.75)
    dr = D_(cam); estacion(dr, t, win=None)
    nico(dr, 540, 1660, 0.62, t, traje="astronauta", arms=(20, 150), elbows=(0, 60), expr="nervous", mouth=boca(10, t) * 0.6, sweat=True, look=(0.5 * math.sin(t * 3), 0))
    f = oscuro(tinta(dr), 0.6)
    img = acabado(f, T)
    burst(img, "SHHH…", 780, 460, 100, t - 0.1, col=(170, 200, 255), ang=-6)
    return img, 0

@shot
def s12(t, D, T):    # pero todo hace ruido: ventiladores, alarmas… y Tuerca
    cam = Cam(540, 1000, 1.0)
    dr = D_(cam); estacion(dr, t)
    for k, (x, y) in enumerate(((330, 900), (740, 1050))):   # ventiladores
        dr.ell(x, y, 110, 110, (120, 126, 140))
        for j in range(4):
            a = t * 18 + j * math.pi / 2
            dr.poly([(x, y), (x + math.cos(a) * 95, y + math.sin(a) * 95), (x + math.cos(a + 0.6) * 95, y + math.sin(a + 0.6) * 95)], (200, 206, 216))
    tuerca(dr, 540, 1450, 0.75, t, mouth=0.2)
    f = tinta(dr); img = acabado(f, T)
    if t > tl(11, 0.45): burst(img, "VRRRR", 330, 740, 80, t - tl(11, 0.45), col=(200, 220, 255), ang=-8)
    if t > tl(11, 0.65): burst(img, "¡BIP!", 760, 860, 90, t - tl(11, 0.65), col=(255, 90, 80), ang=8)
    if t > tl(11, 0.85): burst(img, "¿YO?", 540, 1180, 90, t - tl(11, 0.85), col=(110, 240, 255), ang=-4)
    return img, 0

@shot
def s13(t, D, T):    # Tuerca grita ALERTA
    cam = Cam(540, 1000, 1.25)
    dr = D_(cam); estacion(dr, t, win=None)
    tuerca(dr, 540, 1100, 1.5, t, mouth=boca(12, t), alarm=True)
    f = tinta(dr); f = rojo(f, 0.5 + 0.5 * math.sin(t * 14))
    img = acabado(f, T)
    ondas(img, 540, 1050, t, (255, 90, 80), 3, 2.2)
    burst(img, "¡ALERTA!", 540, 420, 140, t - 0.05, col=(255, 222, 40), ang=-5)
    return img, 6 + 6 * boca(12, t)

@shot
def s14(t, D, T):    # Nico: ¡Tuerca, cállate!
    cam = Cam(540, 1080, 1.8)
    dr = D_(cam); estacion(dr, t, win=None)
    nico(dr, 540, 1660, 0.62, t, traje="astronauta", arms=(150, 150), elbows=(-20, -20), expr="angry", mouth=boca(13, t), look=(0, 0))
    f = rojo(tinta(dr), 0.35); img = acabado(f, T)
    burst(img, "¡CÁLLATE!", 540, 450, 130, t - 0.05, col=(255, 90, 60), ang=6)
    return img, 5 * boca(13, t)

@shot
def s15(t, D, T):    # el zombi gira la cabeza y se impulsa
    u = t / D
    turn = clamp(u / 0.4) * 1.0
    push = ease((u - 0.5) / 0.5)
    cam = Cam(540, 1050, lerp(1.0, 1.9, push))
    dr = D_(cam); estacion(dr, t)
    zastro(dr, 560, 1500 + 200 * push, 0.5 + 0.2 * push, t, mouth=0.6 * push, turn=-turn, arms=1.0)
    f = rojo(tinta(dr), 0.3); img = acabado(f, T)
    if u > 0.25: ondas(img, *cam.p(500, 1150), t, (255, 222, 40), 2, 1.0)
    if push > 0.05: burst(img, "¡FIUUU!", 540, 420, 120, t - 0.5 * D, col=(150, 240, 110), ang=-6)
    return img, (4 if push > 0 else 0)

@shot
def s16(t, D, T):    # Nico flota atrás… por la ventana: la horda
    u = ease(t / D)
    cam = Cam(lerp(560, 760, u), lerp(1100, 860, u), lerp(1.0, 1.7, u))
    dr = D_(cam); estacion(dr, t, win=(820, 760, 250), horda=clamp(t / D * 1.6))
    nico(dr, lerp(380, 480, u), 1850, 0.5, t, traje="astronauta", arms=(120, 140), elbows=(30, 20), expr="shock", look=(1, -0.6))
    f = tinta(dr); add_glow(f, *cam.p(820, 760), 300 * cam.z, (150, 240, 110), 0.25)
    img = acabado(f, T)
    if t > tl(15, 0.6): burst(img, "¡MÁS!", 300, 470, 120, t - tl(15, 0.6), col=(150, 240, 110), ang=-7)
    return img, 0

@shot
def s17(t, D, T):    # Nico: ¿cuántos astronautas había?
    cam = Cam(540, 1080, 1.75)
    dr = D_(cam); estacion(dr, t, win=None)
    nico(dr, 540, 1660, 0.62, t, traje="astronauta", arms=(30, 30), elbows=(-60, -60), expr="worried", mouth=boca(16, t), sweat=True, look=(-0.7, 0))
    f = oscuro(tinta(dr), 0.7, (0.9, 1.0, 1.15)); img = acabado(f, T)
    return img, 2 * math.sin(T * 30)

@shot
def s18(t, D, T):    # Tuerca: antes eran doce… ahora doce zombis
    cam = Cam(540, 1000, 1.15)
    dr = D_(cam, bg=(30, 60, 50))
    for k in range(18):
        a = k * math.pi / 9 - t * 0.4
        dr.poly([(540, 1100), (540 + math.cos(a) * 2000, 1100 + math.sin(a) * 2000), (540 + math.cos(a + 0.17) * 2000, 1100 + math.sin(a + 0.17) * 2000)], (40, 80, 60))
    tuerca(dr, 540, 1250, 1.3, t, mouth=boca(17, t), look=(0, 0.2))
    f = tinta(dr); img = acabado(f, T); d = ImageDraw.Draw(img)
    k = eob(t / 0.3)
    d.rounded_rectangle([250, 330, 830, 520], radius=36, fill=(20, 24, 30), outline=INK, width=8)
    zz = t > tl(17, 0.55)
    d.text((540, 425), "12 ZOMBIS" if zz else "12 ASTRONAUTAS", font=font(int((82 if zz else 58) * k) + 1), fill=(150, 240, 110) if zz else (255, 255, 255), anchor="mm")
    if zz: burst(img, "😬" if False else "¡UPS!", 800, 620, 90, t - tl(17, 0.55), col=(255, 222, 40), ang=8)
    return img, 0

@shot
def s19(t, D, T):    # dilema: 1 cápsula de escape · 2 invernadero
    cam = Cam(540, 960, 1.0)
    dr = D_(cam, bg=(8, 10, 28))
    estrellas(dr, t, 60, 11)
    dr.poly([(470, -100), (610, -100), (610, 2600), (470, 2600)], (20, 16, 26))
    o1 = t > tl(18, 0.02); o2 = t > tl(18, 0.47)
    if o1: capsula(dr, 270, 1080, 1.15 * eob((t - tl(18, 0.02)) / 0.3) + 0.01, t)
    if o2: invernadero(dr, 810, 1080, 0.95 * eob((t - tl(18, 0.47)) / 0.3) + 0.01, t)
    nico(dr, 540, 1760, 0.42, t, traje="astronauta", arms=(70, 70), elbows=(60, 60), expr="nervous", look=(-0.8 if t < tl(18, 0.45) else 0.8, -0.3))
    f = tinta(dr); img = acabado(f, T); d = ImageDraw.Draw(img)
    d.text((540, 300), "¿QUÉ HARÍA NICO?", font=font(82), fill=(255, 222, 40), anchor="mm", stroke_width=12, stroke_fill=INK)
    for ok, x, n, a, b in ((o1, 270, "1", "CÁPSULA", "DE ESCAPE"), (o2, 810, "2", "INVERNADERO", "ESPACIAL")):
        if not ok: continue
        d.ellipse([x - 80, 400, x + 80, 560], fill=(255, 255, 255), outline=INK, width=10)
        d.text((x, 482), n, font=font(116), fill=INK, anchor="mm")
        d.text((x, 640), a, font=font(54 if len(a) < 10 else 46), fill=(255, 255, 255), anchor="mm", stroke_width=7, stroke_fill=INK)
        d.text((x, 700), b, font=font(40), fill=(255, 222, 40), anchor="mm", stroke_width=6, stroke_fill=INK)
    return img, 0

@shot
def s20(t, D, T):    # comenta 1 o 2
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
    if t > tl(19, 0.45):
        kk = eob((t - tl(19, 0.45)) / 0.3)
        d.text((540, 520), "En la parte 2 verás", font=font(int(52 * kk) + 1), fill=(255, 255, 255), anchor="mm", stroke_width=7, stroke_fill=INK)
        d.text((540, 590), "si elegiste bien", font=font(int(52 * kk) + 1), fill=(255, 255, 255), anchor="mm", stroke_width=7, stroke_fill=INK)
    return img, 0

@shot
def s21(t, D, T):    # nos vemos en otro mundo hipotético… si sobrevivo
    cam = Cam(540, 1000, 1.0)
    dr = D_(cam); espacio_fondo(dr, t)
    o = 1 - ease((t - D + 1.0) / 0.8)
    portal(dr, 540, 1000, 330, t, o)
    zastro(dr, 900, 1500, 0.32, t, mouth=0.4, ph=1.0)
    if t < D - 1.0: nico(dr, 540, 1460, 0.5, t, traje="astronauta", arms=(150, 20), elbows=(30, 0), expr="nervous" if t > tl(20, 0.6) else "happy", mouth=boca(20, t), look=(0.6 if t > tl(20, 0.6) else 0, 0))
    f = tinta(dr); add_glow(f, *cam.p(540, 1000), 450, (150, 120, 255), 0.5 * o)
    img = acabado(f, T); d = ImageDraw.Draw(img)
    d.rounded_rectangle([150, 380, 930, 560], radius=36, fill=(255, 214, 10), outline=INK, width=8)
    d.text((540, 440), "CAPÍTULO 2", font=font(64), fill=INK, anchor="mm")
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
        """Arpegio espacial (synth) + bajo + bombo suave."""
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
    # votos + ruleta
    synth(0.0, S_[1], 0.8)
    x = seg(0.8); add(S_[0] + tl(0, 0.5), 0.25 * np.exp(-x * 4) * (np.sin(2 * np.pi * 311 * x) + np.sin(2 * np.pi * 330 * x)) / 2)
    t0, t1 = S_[1] + 0.05, S_[2] - 0.55
    xr = seg(t1 - t0); add(t0, 0.06 * bp(150, 600)[:len(xr)] * (0.6 + 0.4 * np.sin(2 * np.pi * 18 * xr)))
    prev = int(ang_ruleta(t0) / 22.5)
    for k in range(int((t1 - t0) * FPS) + 2):
        T = t0 + k / FPS; a = ang_ruleta(T)
        if int(a / 22.5) != prev:
            prev = int(a / 22.5); xc = seg(0.03); add(T, 0.25 * np.exp(-xc * 200) * np.sin(2 * np.pi * 2500 * xc))
    x = seg(1.2); add(t1, 0.35 * np.exp(-x * 2.5) * (np.sin(2 * np.pi * 262 * x) + np.sin(2 * np.pi * 392 * x) + np.sin(2 * np.pi * 523 * x)) / 3)
    # portal + estación
    x = seg(1.4); add(S_[3] + 0.1, 0.25 * wh[:len(x)] * np.sin(np.pi * x / 1.4) * (0.5 + 0.5 * np.sin(2 * np.pi * 9 * x)))
    synth(S_[3] + DURS[3] * 0.32, S_[5], 0.8)
    alarma(S_[5], tl(5, 0.3) + 0.2, 0.06)
    synth(S_[5] + tl(5, 0.3), S_[7], 0.7)
    # caja: crac + gas + gruñido
    x = seg(0.5); add(S_[7] + 0.3, 0.5 * (low[:len(x)] * 1.5 + 0.5 * wh[:len(x)]) * np.exp(-x * 7))
    x = seg(2.2); add(S_[7] + 0.5, 0.12 * bp(1500, 6000)[:len(x)] * np.exp(-x * 1.2))
    dron(S_[7], S_[11], 0.07)
    synth(S_[8], S_[11], 0.6, dark=True)
    # silencio + ruido
    for kk in range(int((S_[12] - S_[10]) / 0.8)):
        for dd in (0, 0.22):
            x = seg(0.25); add(S_[10] + kk * 0.8 + dd, 0.14 * np.exp(-x * 14) * np.sin(2 * np.pi * (52 + 20 * np.exp(-x * 30)) * x))
    xf = seg(DURS[11]); add(S_[11], 0.05 * bp(200, 900)[:len(xf)] * np.clip(xf / 0.5, 0, 1))
    x = seg(0.3); add(S_[11] + tl(11, 0.65), 0.12 * np.sin(2 * np.pi * 1760 * x) * (x < 0.15))
    alarma(S_[12], DURS[12] + DURS[13], 0.09)
    # persecución
    dron(S_[14], S_[18], 0.09)
    synth(S_[14], S_[18], 0.8, dark=True)
    x = seg(1.0); add(S_[14] + DURS[14] * 0.5, 0.3 * wh[:len(x)] * np.sin(np.pi * x / 1.0))
    x = seg(1.4); add(S_[15] + tl(15, 0.6), 0.3 * np.exp(-x * 2) * (np.sin(2 * np.pi * 311 * x) + np.sin(2 * np.pi * 370 * x) + np.sin(2 * np.pi * 440 * x)) / 3)
    # dilema + cierre
    for kk in range(int((S_[20] - S_[18]) / 0.6)):
        x = seg(0.3); add(S_[18] + kk * 0.6, 0.12 * np.exp(-x * 10) * np.sin(2 * np.pi * (55 + 20 * (kk % 2)) * x))
        x = seg(0.08); add(S_[18] + kk * 0.6 + 0.3, 0.05 * np.exp(-x * 60) * np.sin(2 * np.pi * 1200 * x))
    synth(S_[20], TOTAL, 0.6)
    x = seg(1.6); add(TOTAL - 1.6, 0.2 * wh[:len(x)] * np.sin(np.pi * x / 1.6) * (0.5 + 0.5 * np.sin(2 * np.pi * 9 * x)))
    for k in range(1, len(S_) - 1):   # whoosh en cada corte
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
