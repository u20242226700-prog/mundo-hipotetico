#!/usr/bin/env python3
"""Short vertical: ¿Qué pasaría si la Luna desapareciera? — renderizado 100% por código."""
import math, subprocess, sys, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
OUT = sys.argv[1] if len(sys.argv) > 1 else "luna.mp4"
rng = np.random.default_rng(7)

F_BLACK = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
F_BOLD = "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"
F_REG = "/usr/share/fonts/truetype/google-fonts/Poppins-Medium.ttf"
_fc = {}
def font(path, size):
    k = (path, size)
    if k not in _fc:
        _fc[k] = ImageFont.truetype(path, size)
    return _fc[k]

YEL = (255, 214, 10)
WHITE = (255, 255, 255)
RED = (255, 72, 72)

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x):
    x = clamp(x); return x * x * (3 - 2 * x)
def ease_out_back(x):
    x = clamp(x); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2
def lerp(a, b, t): return a + (b - a) * t
def lerpc(c1, c2, t): return tuple(int(lerp(a, b, t)) for a, b in zip(c1, c2))

# ---------------------------------------------------------------- escenas
SCENES = [  # (nombre, duración)
    ("hook", 4.0), ("noche", 4.0), ("mareas", 6.0), ("eje", 5.0),
    ("caos", 5.5), ("tranquilo", 4.5), ("cta", 3.5),
]
STARTS = np.cumsum([0] + [d for _, d in SCENES]).tolist()
TOTAL = STARTS[-1]

CAPS = [  # (inicio, fin, texto, palabras resaltadas)
    (0.0, 1.2, "¿Qué pasaría si", []),
    (1.2, 2.0, "la Luna", ["Luna"]),
    (2.0, 2.9, "desapareciera", ["desapareciera"]),
    (2.9, 4.0, "esta noche?", []),
    (4.0, 4.8, "Primero:", []),
    (4.8, 6.0, "las noches serían", []),
    (6.0, 8.0, "MUCHO más oscuras", ["oscuras"]),
    (8.0, 9.0, "Las mareas", ["mareas"]),
    (9.0, 10.2, "dependen sobre todo", []),
    (10.2, 11.0, "de la Luna", ["Luna"]),
    (11.0, 12.3, "sin ella quedarían", []),
    (12.3, 14.0, "en un tercio", ["tercio"]),
    (14.0, 15.2, "Pero lo peor:", ["peor:"]),
    (15.2, 16.4, "la Luna mantiene", []),
    (16.4, 17.6, "estable el eje", ["estable"]),
    (17.6, 19.0, "de la Tierra", []),
    (19.0, 20.0, "Sin ella", []),
    (20.0, 21.4, "podría tambalearse", ["tambalearse"]),
    (21.4, 22.8, "de 0° a 85°", ["0°", "85°"]),
    (22.8, 24.5, "estaciones extremas", ["extremas"]),
    (24.5, 25.5, "Tranquilo:", []),
    (25.5, 27.0, "la Luna solo se aleja", []),
    (27.0, 29.0, "3,8 cm al año", ["3,8", "cm"]),
    (29.0, 30.2, "¿Qué tema", []),
    (30.2, 31.3, "hago mañana?", []),
    (31.3, 32.5, "Coméntalo", ["Coméntalo"]),
]

# ---------------------------------------------------------------- recursos
def gradient(top, bot, w=W, h=H):
    t = np.linspace(0, 1, h)[:, None, None]
    a = np.array(top, float)[None, None, :]; b = np.array(bot, float)[None, None, :]
    arr = (a + (b - a) * t).repeat(w, axis=1)
    return arr

_gcache = {}
def bg(top, bot):
    k = (top, bot)
    if k not in _gcache:
        arr = gradient(top, bot).astype(np.uint8)
        _gcache[k] = Image.fromarray(arr, "RGB").convert("RGBA")
    return _gcache[k].copy()

STARS = [(rng.uniform(0, W), rng.uniform(0, H), rng.uniform(1.0, 3.2), rng.uniform(0, 6.28)) for _ in range(260)]
def draw_stars(img, T, bright=1.0, ymax=H):
    d = ImageDraw.Draw(img)
    for x, y, s, ph in STARS:
        if y > ymax: continue
        a = bright * (0.55 + 0.45 * math.sin(T * 2.2 + ph))
        c = int(255 * clamp(a))
        d.ellipse([x - s, y - s, x + s, y + s], fill=(c, c, min(255, c + 20), 255))

# Textura de la Tierra (ruido periódico en longitud)
TW, TH = 1024, 512
lon = np.linspace(0, 2 * np.pi, TW, endpoint=False)[None, :]
lat = np.linspace(np.pi / 2, -np.pi / 2, TH)[:, None]
def pnoise(terms, kmax, seed):
    r = np.random.default_rng(seed); n = np.zeros((TH, TW))
    for _ in range(terms):
        k = r.integers(1, kmax + 1); m = r.uniform(0.5, kmax)
        amp = 1.0 / (k + m * 0.5)
        n += amp * np.sin(k * lon + r.uniform(0, 6.28)) * np.cos(m * lat + r.uniform(0, 6.28))
    return (n - n.min()) / (n.max() - n.min())
land_n = pnoise(60, 6, 3)
detail = pnoise(80, 14, 11)
cloud_n = pnoise(70, 10, 21)
landmask = (land_n * 0.8 + detail * 0.2) > 0.58
tex = np.zeros((TH, TW, 3))
tex[:] = np.array([28, 104, 214])
deep = (land_n < 0.4)[..., None]
tex = np.where(deep, np.array([18, 74, 176]), tex)
green = np.array([62, 168, 86]); brown = np.array([178, 146, 92])
landcol = green + (brown - green) * np.clip((detail - 0.35) * 2.2, 0, 1)[..., None]
tex = np.where(landmask[..., None], landcol, tex)
ice = (np.abs(lat) > np.radians(68)).repeat(TW, axis=1)
tex = np.where(ice[..., None], np.array([236, 244, 252]), tex)
cloud_a = np.clip((cloud_n - 0.6) * 3.5, 0, 0.85)

_grid = {}
def earth(diam, rot, tilt_deg, cloud_rot=None):
    if diam not in _grid:
        r = diam / 2
        c = (np.arange(diam) + 0.5 - r) / r
        X, Y = np.meshgrid(c, c); yy = -Y
        rr = np.sqrt(X ** 2 + yy ** 2)
        Z = np.sqrt(np.clip(1 - rr ** 2, 0, 1))
        alpha = np.clip((1 - rr) * r, 0, 1)
        L = np.array([-0.55, 0.38, 0.74]); L = L / np.linalg.norm(L)
        lam = np.clip(X * L[0] + yy * L[1] + Z * L[2], 0, 1)
        shade = 0.18 + 0.92 * lam
        rim = np.clip((rr - 0.82) / 0.18, 0, 1) ** 2  # brillo atmosférico en el borde
        _grid[diam] = (X, yy, Z, alpha, shade, rim)
    X, yy, Z, alpha, shade, rim = _grid[diam]
    t = math.radians(tilt_deg)
    xb = X * math.cos(t) - yy * math.sin(t)
    yb = X * math.sin(t) + yy * math.cos(t)
    la = np.arcsin(np.clip(yb, -1, 1)); lo = np.arctan2(xb, Z)
    v = ((0.5 - la / np.pi) * (TH - 1)).astype(int)
    u = (((lo + rot) / (2 * np.pi)) % 1 * TW).astype(int) % TW
    col = tex[v, u]
    cr = rot * 1.3 if cloud_rot is None else cloud_rot
    uc = (((lo + cr) / (2 * np.pi)) % 1 * TW).astype(int) % TW
    ca = cloud_a[v, uc][..., None]
    col = col * (1 - ca) + 255 * ca
    col = col * shade[..., None]
    col = col * (1 - rim[..., None] * 0.5) + np.array([120, 180, 255]) * rim[..., None] * 0.5
    out = np.dstack([np.clip(col, 0, 255), alpha * 255]).astype(np.uint8)
    return Image.fromarray(out, "RGBA")

def glow(diam, color, strength=0.55):
    s = int(diam * 1.5); r = s / 2
    c = (np.arange(s) + 0.5 - r) / (diam / 2)
    X, Y = np.meshgrid(c, c); rr = np.sqrt(X ** 2 + Y ** 2)
    a = np.clip(1 - (rr - 0.9) / 0.6, 0, 1) ** 2 * strength
    arr = np.zeros((s, s, 4), np.uint8); arr[..., :3] = color; arr[..., 3] = (a * 255).astype(np.uint8)
    return Image.fromarray(arr, "RGBA")
_glows = {}
def paste_glow(img, cx, cy, diam, color=(90, 160, 255), strength=0.55):
    k = (diam, color, strength)
    if k not in _glows: _glows[k] = glow(diam, color, strength)
    g = _glows[k]; img.alpha_composite(g, (int(cx - g.width / 2), int(cy - g.height / 2)))

def paste_earth(img, cx, cy, diam, rot, tilt=23.4):
    paste_glow(img, cx, cy, diam)
    e = earth(diam, rot, tilt)
    img.alpha_composite(e, (int(cx - diam / 2), int(cy - diam / 2)))

# Personaje Luna (diseño original)
def make_moon(d, mood="happy"):
    S = d * 2
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0)); dr = ImageDraw.Draw(im)
    dr.ellipse([0, 0, S - 1, S - 1], fill=(206, 208, 220, 255))
    r2 = np.random.default_rng(5)
    for _ in range(9):
        cx, cy = r2.uniform(0.2, 0.8) * S, r2.uniform(0.15, 0.85) * S
        if abs(cx - S / 2) < S * 0.3 and S * 0.3 < cy < S * 0.75: continue
        rr = r2.uniform(0.04, 0.09) * S
        dr.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=(172, 174, 192, 255))
        dr.ellipse([cx - rr * 0.8, cy - rr * 0.8, cx + rr * 0.6, cy + rr * 0.6], fill=(160, 162, 182, 255))
    # sombreado
    c = (np.arange(S) + 0.5 - S / 2) / (S / 2); X, Y = np.meshgrid(c, c)
    lam = np.clip(-0.5 * X - 0.4 * Y + 0.75 * np.sqrt(np.clip(1 - X ** 2 - Y ** 2, 0, 1)), 0, 1)
    arr = np.array(im).astype(float); arr[..., :3] *= (0.45 + 0.6 * lam)[..., None]
    im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)); dr = ImageDraw.Draw(im)
    ey = S * 0.46; ew, eh = S * 0.075, S * 0.13
    for ex in (S * 0.36, S * 0.64):
        dr.rounded_rectangle([ex - ew, ey - eh, ex + ew, ey + eh], radius=int(ew), fill=(20, 22, 40, 255))
        dr.ellipse([ex - ew * 0.2, ey - eh * 0.75, ex + ew * 0.6, ey - eh * 0.25], fill=(255, 255, 255, 255))
    for bx in (S * 0.25, S * 0.75):
        dr.ellipse([bx - S * 0.06, S * 0.6 - S * 0.03, bx + S * 0.06, S * 0.6 + S * 0.03], fill=(240, 150, 160, 150))
    if mood == "happy":
        dr.arc([S * 0.4, S * 0.55, S * 0.6, S * 0.72], 20, 160, fill=(20, 22, 40, 255), width=int(S * 0.025))
    else:
        dr.line([S * 0.43, S * 0.66, S * 0.57, S * 0.66], fill=(20, 22, 40, 255), width=int(S * 0.025))
    return im.resize((d, d), Image.LANCZOS)
MOON_HAPPY = make_moon(440, "happy"); MOON_FLAT = make_moon(440, "flat")
def paste_moon(img, cx, cy, d, mood="happy", alpha=1.0):
    m = (MOON_HAPPY if mood == "happy" else MOON_FLAT).resize((int(d), int(d)), Image.LANCZOS)
    if alpha < 1:
        a = np.array(m); a[..., 3] = (a[..., 3] * alpha).astype(np.uint8); m = Image.fromarray(a)
    img.alpha_composite(m, (int(cx - d / 2), int(cy - d / 2)))

# Ciudad
CITY = []
x = -20
while x < W + 20:
    bw = rng.integers(70, 160); bh = rng.integers(200, 560)
    wins = [(wx, wy, rng.random() < 0.45) for wx in range(x + 14, x + bw - 20, 28) for wy in range(H - bh + 24, H - 40, 40)]
    CITY.append((x, bw, bh, wins)); x += bw + rng.integers(4, 18)

PARTS = [(rng.uniform(0, 6.28), rng.uniform(120, 420), rng.uniform(4, 11)) for _ in range(46)]

# ---------------------------------------------------------------- UI
def text_layer(words, size, highlight, fnt=F_BLACK, stroke=9):
    f = font(fnt, size)
    space = f.getlength(" ")
    widths = [f.getlength(w) for w in words]
    total = sum(widths) + space * (len(words) - 1)
    pad = stroke * 2 + 10
    asc, desc = f.getmetrics()
    lay = Image.new("RGBA", (int(total + pad * 2), asc + desc + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay); x = pad
    for w, wd in zip(words, widths):
        col = YEL if w in highlight else WHITE
        d.text((x, pad), w, font=f, fill=col, stroke_width=stroke, stroke_fill=(0, 0, 0))
        x += wd + space
    return lay

def caption(img, T):
    for s, e, txt, hl in CAPS:
        if s <= T < e:
            words = txt.split(); size = 112
            while True:
                lay = text_layer(words, size, hl)
                if lay.width <= W - 60 or size < 60: break
                size -= 6
            k = 0.72 + 0.28 * ease_out_back((T - s) / 0.16)
            lay = lay.resize((max(1, int(lay.width * k)), max(1, int(lay.height * k))), Image.LANCZOS)
            img.alpha_composite(lay, (int(W / 2 - lay.width / 2), int(1500 - lay.height / 2)))
            return

def pill(img, parts, y=210, size=46, bgc=(10, 14, 34, 215), border=(255, 255, 255, 60)):
    f = font(F_BLACK, size); sp = f.getlength(" ")
    tw = sum(f.getlength(t) for t, _ in parts) + sp * (len(parts) - 1)
    pw, ph = tw + 70, size + 44
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    x0 = W / 2 - pw / 2
    d.rounded_rectangle([x0, y, x0 + pw, y + ph], radius=22, fill=bgc, outline=border, width=3)
    x = x0 + 35
    for t, c in parts:
        d.text((x, y + 14), t, font=f, fill=c); x += f.getlength(t) + sp
    img.alpha_composite(ov)

def progress(img, n, y=318, total=5):
    d = ImageDraw.Draw(img); w, g = 46, 14
    x0 = W / 2 - (total * w + (total - 1) * g) / 2
    for i in range(total):
        c = YEL + (255,) if i < n else (255, 255, 255, 70)
        d.rounded_rectangle([x0 + i * (w + g), y, x0 + i * (w + g) + w, y + 9], radius=4, fill=c)

def source(img, txt):
    f = font(F_REG, 30); d = ImageDraw.Draw(img)
    tw = f.getlength(txt)
    d.text((W / 2 - tw / 2, 1810), txt, font=f, fill=(255, 255, 255, 170), stroke_width=2, stroke_fill=(0, 0, 0))

def center_text(img, txt, y, size, color, fnt=F_BLACK, stroke=8):
    f = font(fnt, size); d = ImageDraw.Draw(img); tw = f.getlength(txt)
    d.text((W / 2 - tw / 2, y), txt, font=f, fill=color, stroke_width=stroke, stroke_fill=(0, 0, 0))

# ---------------------------------------------------------------- escenas
def s_hook(img, t, T):
    draw_stars(img, T)
    cx, cy, ed = 540, 960, 560
    ang = 1.0 + T * 1.25
    mx, my = cx + 420 * math.cos(ang), cy + 150 * math.sin(ang)
    md = 150 * (1 + 0.15 * math.sin(ang))
    k = 1 - ease((t - 2.2) / 0.45)
    behind = math.sin(ang) < 0
    if behind and k > 0: paste_moon(img, mx, my, md * (0.3 + 0.7 * k), "flat", k)
    paste_earth(img, cx, cy, ed, T * 0.35)
    if not behind and k > 0: paste_moon(img, mx, my, md * (0.3 + 0.7 * k), "flat", k)
    pt = (t - 2.45) / 1.1
    if 0 < pt < 1:
        mx0, my0 = cx + 420 * math.cos(1.0 + 2.45 * 1.25 + 0), cy + 150 * math.sin(1.0 + 2.45 * 1.25)
        d = ImageDraw.Draw(img)
        for a, dist, s in PARTS:
            px, py = mx0 + math.cos(a) * dist * ease(pt), my0 + math.sin(a) * dist * ease(pt)
            al = int(255 * (1 - pt)); ss = s * (1 - pt * 0.6)
            d.ellipse([px - ss, py - ss, px + ss, py + ss], fill=(230, 232, 245, al))
    center_text(img, "¿QUÉ PASARÍA SI", 250, 76, WHITE)
    center_text(img, "LA LUNA DESAPARECE?", 345, 80, YEL)

def s_noche(img, t, T):
    d = ease((t - 0.9) / 2.2)
    top = lerpc((14, 22, 62), (2, 3, 10), d); bot = lerpc((60, 58, 120), (8, 9, 22), d)
    img.alpha_composite(bg(top, bot))
    draw_stars(img, T, 0.35 + 0.75 * d, ymax=1350)
    if d < 1:
        paste_glow(img, 760, 520, 200, (230, 230, 255), 0.5 * (1 - d))
        paste_moon(img, 760, 520, 200, "flat", 1 - d)
    dr = ImageDraw.Draw(img)
    rimc = lerpc((120, 120, 190), (16, 18, 34), d)
    for x, bw, bh, wins in CITY:
        dr.rectangle([x, H - bh, x + bw, H], fill=(12, 14, 30, 255))
        dr.line([x, H - bh, x + bw, H - bh], fill=rimc + (255,), width=4)
        for wx, wy, on in wins:
            if on: dr.rectangle([wx, wy, wx + 12, wy + 18], fill=(255, 200, 90, 230))
    pill(img, [("1 ·", YEL), ("NOCHES MÁS OSCURAS", WHITE)]); progress(img, 1)

def s_mareas(img, t, T):
    img.alpha_composite(bg((96, 170, 236), (250, 214, 170)))
    dr = ImageDraw.Draw(img)
    dr.ellipse([860, 760, 980, 880], fill=(255, 236, 160, 255))
    p = ease((t - 2.6) / 2.2)
    level = lerp(1000, 1235, p)
    pts = [(x, level + 14 * math.sin(x * 0.012 + T * 3) + 6 * math.sin(x * 0.031 - T * 5)) for x in range(0, W + 20, 20)]
    dr.polygon(pts + [(W, H), (0, H)], fill=(30, 120, 210, 255))
    pts2 = [(x, y + 26) for x, y in pts]
    dr.line(pts, fill=(220, 240, 255, 255), width=6)
    dr.polygon(pts2 + [(W, H), (0, H)], fill=(22, 98, 186, 255))
    sand = lambda x: 1700 - (x / W) * 920
    dr.polygon([(0, sand(0)), (W, sand(W)), (W, H), (0, H)], fill=(236, 204, 140, 255))
    dr.line([(0, sand(0)), (W, sand(W))], fill=(210, 176, 112, 255), width=8)
    if p > 0.05:  # marca de la marea de hoy
        for x in range(30, W, 50): dr.line([x, 1000, x + 26, 1000], fill=(255, 255, 255, 200), width=5)
        f = font(F_BOLD, 34); dr.text((40, 950), "marea de hoy", font=f, fill=(255, 255, 255, 230), stroke_width=3, stroke_fill=(0, 60, 120))
    val = int(round(lerp(100, 33, p)))
    center_text(img, f"{val}%", 440, 190, YEL if p > 0.5 else WHITE, stroke=10)
    center_text(img, "altura de las mareas", 650, 48, WHITE, F_BOLD, 6)
    pill(img, [("2 ·", YEL), ("MAREAS", WHITE)]); progress(img, 2)
    source(img, "Fuente: NASA JPL")

def axis_scene(img, T, tilt, ed=560, cy=900, label_col=YEL, jitter=0):
    img.alpha_composite(bg((6, 10, 32), (24, 20, 70)))
    draw_stars(img, T)
    cx = 540 + jitter
    dr = ImageDraw.Draw(img)
    r = ed / 2
    for yy in range(int(cy - r * 1.55), int(cy - r * 0.2), 34):
        dr.line([cx, yy, cx, yy + 18], fill=(255, 255, 255, 110), width=4)
    paste_earth(img, cx, cy, ed, T * 0.45, tilt)
    dr = ImageDraw.Draw(img)
    t = math.radians(tilt); L = r * 1.45
    dx, dy = math.sin(t) * L, -math.cos(t) * L
    dr.line([cx - dx, cy - dy, cx + dx, cy + dy], fill=(255, 255, 255, 235), width=7)
    dr.ellipse([cx + dx - 11, cy + dy - 11, cx + dx + 11, cy + dy + 11], fill=label_col + (255,))
    ar = r * 1.22
    dr.arc([cx - ar, cy - ar, cx + ar, cy + ar], -90, -90 + max(tilt, 0.5), fill=label_col + (255,), width=9)
    return cx

def s_eje(img, t, T):
    tilt = 23.4 + 0.5 * math.sin(t * 2.2)
    cx = axis_scene(img, T, tilt)
    center_text(img, "23,4°", 1215, 96, YEL)
    pill(img, [("3 ·", YEL), ("EL EJE DE LA TIERRA", WHITE)]); progress(img, 3)

def s_caos(img, t, T):
    sv = math.sin(1.7 * t + 0.8 * math.sin(3.1 * t) - 1.9)
    tilt = 42.5 + 42.5 * sv
    jit = 6 * math.sin(T * 41)
    axis_scene(img, T, tilt, label_col=RED, jitter=jit)
    tint = (255, 60, 40) if sv > 0 else (90, 170, 255)
    ov = Image.new("RGBA", img.size, tint + (int(70 * abs(sv)),)); img.alpha_composite(ov)
    center_text(img, f"{int(round(tilt))}°", 1205, 100, RED)
    word = "VERANOS EXTREMOS" if sv > 0 else "ERAS DE HIELO"
    center_text(img, word, 1325, 50, WHITE, F_BOLD, 7)
    pill(img, [("SIN LUNA:", WHITE), ("CAOS", RED)]); progress(img, 4)
    source(img, "Fuente: NASA JPL · Laskar et al. (Nature, 1993)")

def s_tranquilo(img, t, T):
    img.alpha_composite(bg((40, 22, 86), (120, 60, 120)))
    draw_stars(img, T, 0.6, ymax=900)
    bob = 18 * math.sin(T * 3)
    paste_glow(img, 540, 760 + bob, 400, (240, 230, 255), 0.45)
    paste_moon(img, 540, 760 + bob, 400, "happy")
    dr = ImageDraw.Draw(img)
    x0, x1, y = 190, 890, 1090
    dr.rounded_rectangle([x0, y, x1, y + 90], radius=12, fill=(250, 220, 120, 255), outline=(60, 40, 10, 255), width=4)
    for i in range(0, 11):
        xx = x0 + 20 + i * 66
        dr.line([xx, y, xx, y + (40 if i % 5 == 0 else 24)], fill=(60, 40, 10, 255), width=4)
    g = ease((t - 0.3) / 2.0)
    dr.rounded_rectangle([x0 + 20, y + 52, x0 + 20 + 3.8 / 10 * 660 * g, y + 78], radius=8, fill=(255, 80, 80, 255))
    center_text(img, "3,8 cm / año", 1210, 84, YEL)
    center_text(img, "≈ lo que crecen tus uñas en un año", 1325, 40, WHITE, F_BOLD, 5)
    pill(img, [("TRANQUILO", YEL)]); progress(img, 5)
    source(img, "Fuente: NASA (medición láser Tierra-Luna)")

def s_cta(img, t, T):
    img.alpha_composite(bg((8, 12, 40), (30, 24, 80)))
    draw_stars(img, T)
    cx, cy = 540, 900
    ang = T * 1.5; k = ease(t / 0.8)
    mx, my = cx + 330 * math.cos(ang), cy + 110 * math.sin(ang)
    if math.sin(ang) < 0: paste_moon(img, mx, my, 120 * k + 1, "happy", k)
    paste_earth(img, cx, cy, 420, T * 0.35)
    if math.sin(ang) >= 0: paste_moon(img, mx, my, 120 * k + 1, "happy", k)
    center_text(img, "¿QUÉ PASARÍA SI…", 250, 80, WHITE)
    center_text(img, "TÚ ELIGES EL PRÓXIMO", 350, 72, YEL)
    s = 1 + 0.06 * math.sin(T * 8)
    bw, bh = 470 * s, 120 * s
    dr = ImageDraw.Draw(img)
    dr.rounded_rectangle([W / 2 - bw / 2, 1220 - bh / 2, W / 2 + bw / 2, 1220 + bh / 2], radius=30, fill=(255, 40, 60, 255))
    center_text(img, "SÍGUEME", 1220 - 42, 72, WHITE, stroke=0)

FN = {"hook": s_hook, "noche": s_noche, "mareas": s_mareas, "eje": s_eje,
      "caos": s_caos, "tranquilo": s_tranquilo, "cta": s_cta}

def frame(T):
    i = max(j for j in range(len(SCENES)) if STARTS[j] <= T) if T < TOTAL else len(SCENES) - 1
    name, dur = SCENES[i]; t = T - STARTS[i]
    img = bg((7, 11, 31), (20, 26, 69))
    FN[name](img, t, T)
    caption(img, T)
    if i > 0 and t < 0.3:  # transición: zoom + destello
        z = 1 + 0.08 * (1 - ease(t / 0.3))
        big = img.resize((int(W * z), int(H * z)), Image.BILINEAR)
        ox, oy = (big.width - W) // 2, (big.height - H) // 2
        img = big.crop((ox, oy, ox + W, oy + H))
        a = int(140 * (1 - clamp(t / 0.2)))
        if a > 0: img.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, a)))
    return img.convert("RGB")

# ---------------------------------------------------------------- audio
def make_audio(path):
    sr = 44100; n = int(TOTAL * sr); tt = np.arange(n) / sr
    out = np.zeros(n)
    def note(f): return 440 * 2 ** ((f - 69) / 12)
    chords = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]  # Am F C G
    for ci in range(int(TOTAL / 4) + 1):
        s = ci * 4.0; ch = chords[ci % 4]
        i0, i1 = int(s * sr), min(n, int((s + 4.2) * sr))
        if i0 >= n: break
        seg = tt[i0:i1] - s
        env = np.clip(seg / 0.6, 0, 1) * np.clip((4.2 - seg) / 0.8, 0, 1)
        for m in ch:
            f = note(m)
            out[i0:i1] += 0.05 * env * (np.sin(2 * np.pi * f * seg) + 0.4 * np.sin(2 * np.pi * f * 1.003 * seg) + 0.2 * np.sin(2 * np.pi * f * 2 * seg))
        bass = note(ch[0] - 12)
        out[i0:i1] += 0.06 * env * np.sin(2 * np.pi * bass * seg)
    # arpegio
    step = 60 / 120 / 2
    k = 0
    while k * step < TOTAL - 0.2:
        s = k * step; ch = chords[int(s / 4) % 4]
        f = note(ch[k % 3] + 12)
        i0 = int(s * sr); i1 = min(n, i0 + int(0.35 * sr)); seg = tt[i0:i1] - s
        out[i0:i1] += 0.035 * np.exp(-seg * 9) * np.sin(2 * np.pi * f * seg)
        k += 1
    # bombo desde la escena 3
    b = 60 / 120; s = STARTS[2]
    while s < TOTAL - 3.5:
        i0 = int(s * sr); i1 = min(n, i0 + int(0.25 * sr)); seg = tt[i0:i1] - s
        out[i0:i1] += 0.22 * np.exp(-seg * 18) * np.sin(2 * np.pi * (50 + 90 * np.exp(-seg * 30)) * seg)
        s += b
    noise = np.random.default_rng(1).standard_normal(n)
    from scipy.signal import butter, sosfilt
    sos = butter(2, [400, 3000], btype="band", fs=sr, output="sos")
    wn = sosfilt(sos, noise)
    for s in STARTS[1:-1]:  # whoosh en cada cambio de escena
        i0 = max(0, int((s - 0.25) * sr)); i1 = min(n, int((s + 0.25) * sr)); seg = tt[i0:i1] - (s - 0.25)
        out[i0:i1] += 0.35 * np.sin(np.pi * seg / 0.5) ** 2 * wn[i0:i1]
    for s, *_ in CAPS:  # "pop" de subtítulos
        i0 = int(s * sr); i1 = min(n, i0 + int(0.05 * sr)); seg = tt[i0:i1] - s
        out[i0:i1] += 0.05 * np.exp(-seg * 80) * np.sin(2 * np.pi * 1300 * seg)
    s = 2.45; i0 = int(s * sr); i1 = i0 + int(1.2 * sr); seg = tt[i0:i1] - s  # boom de la Luna
    out[i0:i1] += 0.5 * np.exp(-seg * 3.5) * np.sin(2 * np.pi * (38 + 60 * np.exp(-seg * 6)) * seg)
    fade = np.clip((TOTAL - tt) / 1.0, 0, 1); out *= fade
    out = out / np.max(np.abs(out)) * 0.85
    from scipy.io import wavfile
    wavfile.write(path, sr, (out * 32767).astype(np.int16))

if __name__ == "__main__":
    if os.environ.get("PREVIEW"):
        for T in [float(x) for x in os.environ["PREVIEW"].split(",")]:
            frame(T).save(f"prev_{T:05.1f}.png")
        sys.exit()
    make_audio("audio.wav")
    nf = int(TOTAL * FPS)
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                          "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", "audio.wav",
                          "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
                          "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", OUT],
                         stdin=subprocess.PIPE)
    for k in range(nf):
        p.stdin.write(frame(k / FPS).tobytes())
        if k % 150 == 0: print(f"frame {k}/{nf}", flush=True)
    p.stdin.close(); p.wait()
    print("listo", OUT)
