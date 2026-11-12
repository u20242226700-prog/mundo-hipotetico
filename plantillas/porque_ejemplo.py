#!/usr/bin/env python3
"""Prueba v2 del formato "¿Por qué…?" — estilo 2.5D:
personajes planos de palito (cabeza blanca grande, contorno negro grueso) dentro de un mundo con
perspectiva real (pista que corre hacia el horizonte, hangar en fuga, niebla de distancia, sombras duras),
cortes rápidos (~1.5 s), mapas térmicos neón, utilería de papel (periódico, calendario, manómetro).
Reutiliza la voz, los subtítulos y la música de porque.py."""
import math, os, sys, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy.io import wavfile

HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
_src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "porque_base.py")).read().split("\n")
exec("\n".join(_src[:137]), globals())          # utilidades del motor + avion()
OUT = sys.argv[1] if len(sys.argv) > 1 else "porque2.mp4"
_av_src = [l for l in _src[61:101]]
exec("\n".join(_av_src).replace("ws = hh * (0.30 if ventanas == \"redondas\" else 0.42)", "ws = hh * (0.30 if ventanas == \"redondas\" else 0.34)"), globals())
F_SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"

INK = (21, 21, 21, 255)
NICO = (38, 186, 196, 255); BRUNO = (214, 60, 58, 255)
GRISES = [(120, 128, 142, 255), (150, 120, 96, 255), (96, 110, 150, 255)]
SKY_T, SKY_B = (43, 120, 228), (150, 210, 240)

# ------------------------------------------------------------ personaje de palito 2D
def figura(img, x, y, s, ropa, expr="neutral", pose="idle", t=0.0, cara=(255, 255, 255, 255),
           vapor=False, mira=0.0, pelo=False, sombra=True, sudor=False):
    """(x, y) = pies en el suelo. s=1 → ~470 px de alto."""
    SS = 2; k = s * SS
    Wc, Hc = int(620 * k), int(680 * k)
    lay = Image.new("RGBA", (Wc, Hc), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    ox, oy = Wc / 2, Hc - 40 * k
    P = lambda px, py: (ox + px * k, oy + py * k)
    lw = max(2, int(7 * k))
    bob = 7 * math.sin(t * 16) if pose == "laugh" else 3 * math.sin(t * 2.4)
    # piernas
    for sg in (-1, 1):
        hip, knee, foot = P(sg * 20, -150), P(sg * 30, -76), P(sg * 36, -8)
        d.line([hip, knee, foot], fill=INK, width=lw, joint="curve")
        fx, fy = foot
        d.ellipse([fx - 14 * k + sg * 12 * k, fy - 11 * k, fx + 14 * k + sg * 12 * k, fy + 9 * k], fill=INK)
    # brazos según pose
    w = lambda f, a=1: a * math.sin(t * f)
    hands = {
        "idle": [(-72, -150 + 4 * w(2.4)), (72, -150 - 4 * w(2.4))],
        "point": [(-72, -152), (165, -330)],
        "arms_up": [(-125, -410 + 18 * w(11)), (125, -410 - 18 * w(11))],
        "cross": [(38, -212), (-38, -200)],
        "laugh": [(-44, -180), (44, -180)],
        "shock": [(-112, -365), (112, -365)],
        "chin": [(-72, -150), (22, -300)],
    }[pose]
    arms = []
    for sg, (hx_, hy_) in zip((-1, 1), hands):
        sh = (sg * 40, -245 + bob)
        mx, my = (sh[0] + hx_) / 2, (sh[1] + hy_) / 2
        L = math.hypot(hx_ - sh[0], hy_ - sh[1]) + 1e-6
        nx, ny = -(hy_ - sh[1]) / L, (hx_ - sh[0]) / L
        if nx * sg < 0: nx, ny = -nx, -ny
        el = (mx + nx * 18, my + ny * 18)
        arms.append([P(*sh), P(*el), P(hx_, hy_)])
    front_cross = pose == "cross"
    if not front_cross:
        for a in arms: d.line(a, fill=INK, width=lw, joint="curve")
    # torso (sudadera)
    d.rounded_rectangle([*P(-50, -272 + bob), *P(50, -138)], radius=int(42 * k), fill=ropa, outline=INK, width=int(lw * 0.85))
    d.line([P(-30, -182 + bob * 0.5), P(30, -182 + bob * 0.5)], fill=INK, width=int(lw * 0.6))
    if front_cross:
        for a in arms: d.line(a, fill=INK, width=lw, joint="curve")
    for a in arms:
        hx2, hy2 = a[-1]; d.ellipse([hx2 - 9 * k, hy2 - 9 * k, hx2 + 9 * k, hy2 + 9 * k], fill=INK)
    # cabeza + capucha
    hx, hy = P(mira * 10, -372 + bob)
    d.ellipse([hx - 100 * k, hy - 74 * k, hx + 100 * k, hy + 112 * k], fill=ropa, outline=INK, width=lw)
    d.ellipse([hx - 84 * k, hy - 96 * k, hx + 84 * k, hy + 94 * k], fill=cara, outline=INK, width=lw)
    if pelo:
        pts = [(-56, -78), (-46, -122), (-20, -92), (0, -134), (18, -94), (46, -120), (56, -76)]
        d.polygon([(hx + a * k, hy + b * k) for a, b in pts], fill=INK)
    F = lambda a, b: (hx + (a + mira * 8) * k, hy + b * k)
    blink = (t % 3.1) < 0.12 and expr not in ("shock",)
    lwf = max(2, int(6 * k))
    for sg in (-1, 1):
        ex, ey = F(sg * 31, -8)
        if expr == "shock":
            d.ellipse([ex - 29 * k, ey - 31 * k, ex + 29 * k, ey + 31 * k], fill=(255, 255, 255, 255), outline=INK, width=lwf)
            d.ellipse([ex - 8 * k, ey - 8 * k, ex + 8 * k, ey + 8 * k], fill=INK)
        elif expr in ("happy", "laugh") or blink:
            if blink and expr not in ("happy", "laugh"):
                d.line([ex - 12 * k, ey, ex + 12 * k, ey], fill=INK, width=lwf)
            else:
                d.arc([ex - 15 * k, ey - 12 * k, ex + 15 * k, ey + 14 * k], 200, 340, fill=INK, width=lwf)
        elif expr == "smug":
            d.chord([ex - 12 * k, ey - 14 * k, ex + 12 * k, ey + 16 * k], 0, 180, fill=INK)
            d.line([ex - 15 * k, ey, ex + 15 * k, ey], fill=INK, width=lwf)
        else:
            d.ellipse([ex - 10 * k, ey - 15 * k, ex + 10 * k, ey + 15 * k], fill=INK)
        # cejas
        bx = sg * 31
        if expr == "angry": a, b = F(bx + sg * 24, -48), F(bx - sg * 16, -30)
        elif expr == "worried": a, b = F(bx + sg * 24, -32), F(bx - sg * 16, -48)
        elif expr == "shock": a, b = F(bx + sg * 22, -60), F(bx - sg * 18, -64)
        elif expr == "smug" and sg > 0: a, b = F(bx + 22, -52), F(bx - 16, -44)
        else: a, b = F(bx + sg * 22, -38), F(bx - sg * 18, -42)
        d.line([a, b], fill=INK, width=lwf)
    # boca
    if expr == "neutral": d.line([F(-18, 44), F(18, 44)], fill=INK, width=lwf)
    elif expr == "happy":
        d.chord([*F(-36, 20), *F(36, 66)], 0, 180, fill=INK)
        d.rectangle([*F(-26, 43), *F(26, 50)], fill=(255, 255, 255, 255))
    elif expr == "smug": d.line([F(-14, 46), F(8, 44), F(28, 32)], fill=INK, width=lwf, joint="curve")
    elif expr == "worried": d.line([F(-22, 48), F(-10, 42), F(2, 48), F(14, 42), F(24, 48)], fill=INK, width=lwf)
    elif expr == "shock": d.ellipse([*F(-20, 30), *F(20, 82)], fill=INK)
    elif expr == "angry":
        d.rounded_rectangle([*F(-32, 32), *F(32, 60)], radius=int(8 * k), fill=(255, 255, 255, 255), outline=INK, width=lwf)
        for xx in (-14, 0, 14): d.line([F(xx, 32), F(xx, 60)], fill=INK, width=max(1, lwf // 2))
        d.line([F(-32, 46), F(32, 46)], fill=INK, width=max(1, lwf // 2))
    elif expr == "laugh":
        d.chord([*F(-44, 14), *F(44, 82)], 0, 180, fill=INK)
        d.rectangle([*F(-32, 48), *F(32, 56)], fill=(255, 255, 255, 255))
        d.chord([*F(-18, 58), *F(18, 82)], 180, 360, fill=(240, 100, 120, 255))
    if sudor:
        for j, (a, b) in enumerate([(96, -40), (108, 4)]):
            yy = b + ((t * 120 + j * 40) % 60)
            sx, sy = F(a, yy)
            d.polygon([(sx, sy - 18 * k), (sx - 9 * k, sy), (sx + 9 * k, sy)], fill=(120, 200, 255, 255))
            d.ellipse([sx - 9 * k, sy - 8 * k, sx + 9 * k, sy + 10 * k], fill=(120, 200, 255, 255))
    lay = lay.resize((Wc // SS, Hc // SS), Image.LANCZOS)
    if sombra:   # sombra dura alargada (sol desde la izquierda)
        sh = Image.new("RGBA", (int(420 * s), int(60 * s)), (0, 0, 0, 0))
        ImageDraw.Draw(sh).ellipse([0, 0, sh.width - 1, sh.height - 1], fill=(20, 24, 40, 90))
        img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(3)), (int(x - 90 * s), int(y - 30 * s)))
    img.alpha_composite(lay, (int(x - Wc / SS / 2), int(y - oy / SS)))
    if vapor:
        dv = ImageDraw.Draw(img)
        for sg in (-1, 1):
            for j in range(3):
                ph = (t * 1.6 + j / 3) % 1
                r = (9 + 22 * ph) * s
                cx = x + sg * (100 + 50 * ph) * s; cy = y - (420 + 130 * ph) * s
                a = int(230 * (1 - ph))
                dv.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255, a), outline=(21, 21, 21, a), width=max(2, int(4 * s)))

PURP = (129, 55, 157, 255)

# ------------------------------------------------------------ cielo y mundo en perspectiva
_RNG = np.random.default_rng(7)
_NUBES = [(_RNG.uniform(0, 1), _RNG.uniform(150, 950), _RNG.uniform(0.5, 1.4), [(_RNG.uniform(-1, 1), _RNG.uniform(-0.3, 0.3), _RNG.uniform(0.5, 1)) for _ in range(6)]) for _ in range(9)]
def cielo2(t, vel=30, top=SKY_T, bot=SKY_B, hy=1150):
    img = grad(top, bot, WW, WH)
    lay = Image.new("RGBA", (WW, WH), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for (u, cy, s, blobs) in _NUBES:
        if cy > hy - 80: continue
        cx = (u * (WW + 800) - t * vel * s) % (WW + 800) - 400
        for (ox, oy, r) in blobs:
            rr = r * 110 * s
            d.ellipse([cx + ox * 170 * s - rr, cy + oy * 80 * s - rr * 0.8 + 14 * s, cx + ox * 170 * s + rr, cy + oy * 80 * s + rr * 0.8 + 14 * s], fill=(176, 198, 228, 255))
        for (ox, oy, r) in blobs:
            rr = r * 110 * s
            d.ellipse([cx + ox * 170 * s - rr, cy + oy * 80 * s - rr * 0.8, cx + ox * 170 * s + rr, cy + oy * 80 * s + rr * 0.8 - 6 * s], fill=(255, 255, 255, 255))
    img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(4)))
    glow(img, 180, 260, 700, (255, 245, 220), 0.55)
    return img

_GROUND = {}
def suelo(img, t, vel=0.0, camh=260.0, camx=0.0, hy=1150, tono=1.0):
    """Pista de aterrizaje en perspectiva real + pasto a rayas + niebla de distancia."""
    Fp = 720.0
    h = WH - hy
    key = (camh, hy)
    if key not in _GROUND:
        rows = np.arange(1, h + 1, dtype=np.float32)[:, None]
        Z = camh * Fp / rows
        Xs = (np.arange(WW, dtype=np.float32)[None, :] - WW / 2) * Z / Fp
        _GROUND[key] = (Z, Xs)
    Z, Xs = _GROUND[key]
    X = Xs + camx
    off = t * vel
    zz = np.broadcast_to(Z + off, X.shape)
    Zb = np.broadcast_to(Z, X.shape)
    run = np.abs(X) < 520
    edge = (np.abs(X) > 470) & (np.abs(X) < 500)
    dash = (np.abs(X) < 16) & ((zz % 700) < 360)
    stripe = ((zz // 500) % 2).astype(bool)
    grass = np.where(stripe[..., None], np.array([96, 150, 70], np.float32), np.array([84, 136, 62], np.float32))
    tar = np.broadcast_to(np.array([78, 82, 90]), grass.shape).astype(np.float32).copy()
    noise = (((X * 0.37).astype(np.int64) * 7 + (zz * 0.21).astype(np.int64) * 13) % 9 - 4).astype(np.float32)
    tar += noise[..., None]
    col = np.where(run[..., None], tar, grass).astype(np.float32)
    col = np.where((edge | dash)[..., None], np.array([238, 238, 230], np.float32), col)
    fog = 1 - np.exp(-Zb / 5200.0)
    fogc = np.array([170, 200, 225], np.float32)
    col = col * (1 - fog[..., None] * 0.85) + fogc * fog[..., None] * 0.85
    col *= tono
    g = Image.fromarray(np.clip(col, 0, 255).astype(np.uint8)).convert("RGBA")
    img.alpha_composite(g, (0, hy))
    return lambda Xw, Zw: (WW / 2 + (Xw - camx) * Fp / Zw, hy + camh * Fp / Zw)

def montes(img, hy=1150, t=0.0):
    d = ImageDraw.Draw(img)
    r = np.random.default_rng(3)
    for layer, (col, amp, base) in enumerate([((150, 176, 205), 120, 30), ((118, 146, 150), 80, 4)]):
        xs = np.linspace(-50, WW + 50, 28)
        ys = hy - base - amp * (0.5 + 0.5 * np.sin(xs / (180 + layer * 60) + layer * 2)) - r.uniform(0, amp * 0.4, len(xs))
        d.polygon([(xs[0], hy + 2)] + list(zip(xs, ys)) + [(xs[-1], hy + 2)], fill=col + (255,))
    # torre de control a lo lejos
    d.rectangle([980, hy - 210, 1010, hy], fill=(120, 140, 160, 255))
    d.polygon([(955, hy - 210), (1035, hy - 210), (1025, hy - 260), (965, hy - 260)], fill=(90, 116, 140, 255))
    d.rectangle([965, hy - 252, 1025, hy - 232], fill=(190, 220, 240, 255))

def pista(t, vel=0.0, camh=260.0, hy=1150, tono=1.0, top=SKY_T, bot=SKY_B):
    img = cielo2(t, 30, top, bot, hy)
    montes(img, hy, t)
    proj = suelo(img, t, vel, camh, 0.0, hy, tono)
    return img, proj

def hangar2(t, letrero="HANGAR 7 · 1952"):
    img = grad((150, 140, 128), (120, 112, 104), WW, WH)
    d = ImageDraw.Draw(img)
    bx0, by0, bx1, by1 = 290, 560, 1006, 1300
    vx, vy = WW / 2, 1000
    # techo
    d.polygon([(0, 0), (WW, 0), (bx1, by0), (bx0, by0)], fill=(84, 82, 82, 255))
    for k in range(0, 13):   # cerchas de acero en fuga
        u = k / 12; xa = lerp(0, WW, u); xb = lerp(bx0, bx1, u)
        d.line([xa, 0, xb, by0], fill=(40, 42, 48, 255), width=6)
    for j in range(1, 6):
        u = (j / 6) ** 1.6
        yl = lerp(0, by0, u); xl = lerp(0, bx0, u); xr = lerp(WW, bx1, u)
        d.line([xl, yl, xr, yl], fill=(40, 42, 48, 255), width=int(lerp(16, 5, u)))
        if j < 5:
            u2 = ((j + 1) / 6) ** 1.6; yl2 = lerp(0, by0, u2); xl2 = lerp(0, bx0, u2); xr2 = lerp(WW, bx1, u2)
            for m in range(10):
                d.line([lerp(xl, xr, m / 10), yl, lerp(xl2, xr2, (m + 1) / 10), yl2], fill=(52, 54, 60, 255), width=int(lerp(6, 2, u)))
    # paredes laterales (chapa ondulada)
    d.polygon([(0, 0), (bx0, by0), (bx0, by1), (0, 1800)], fill=(168, 154, 136, 255))
    d.polygon([(WW, 0), (bx1, by0), (bx1, by1), (WW, 1800)], fill=(150, 138, 122, 255))
    for k in range(1, 16):
        u = k / 16
        d.line([lerp(0, bx0, u), lerp(0, by0, u), lerp(0, bx0, u), lerp(1800, by1, u)], fill=(140, 128, 112, 255), width=3)
        d.line([lerp(WW, bx1, u), lerp(0, by0, u), lerp(WW, bx1, u), lerp(1800, by1, u)], fill=(128, 118, 104, 255), width=3)
    # pared del fondo con portón abierto al cielo
    d.rectangle([bx0, by0, bx1, by1], fill=(176, 162, 144, 255))
    dx0, dy0, dx1 = 360, 760, 936
    sky = grad(SKY_T, SKY_B, dx1 - dx0, by1 - dy0)
    img.alpha_composite(sky, (dx0, dy0))
    d = ImageDraw.Draw(img)
    d.rectangle([dx0, by1 - 70, dx1, by1], fill=(96, 140, 80, 255))
    d.rectangle([dx0, by1 - 40, dx1, by1], fill=(90, 94, 100, 255))
    d.rectangle([dx0 - 14, dy0 - 14, dx1 + 14, dy0], fill=(60, 60, 64, 255))
    d.rectangle([dx0 - 14, dy0, dx0, by1], fill=(60, 60, 64, 255)); d.rectangle([dx1, dy0, dx1 + 14, by1], fill=(60, 60, 64, 255))
    f = font(F_BLACK, 52); tw = f.getlength(letrero)
    d.rectangle([WW / 2 - tw / 2 - 26, 610, WW / 2 + tw / 2 + 26, 700], fill=(36, 38, 44, 255))
    d.text((WW / 2 - tw / 2, 622), letrero, font=f, fill=(250, 200, 60, 255))
    # piso en fuga
    d.polygon([(bx0, by1), (bx1, by1), (WW, 1800), (WW, WH), (0, WH), (0, 1800)], fill=(150, 150, 146, 255))
    for k in range(-10, 11):
        d.line([vx + k * 36 * (bx1 - bx0) / 720, by1, vx + k * 230, WH], fill=(128, 128, 124, 255), width=3)
    yy = by1
    for j in range(12):
        yy += 26 * (1.32 ** j)
        if yy > WH: break
        u = clamp((1800 - yy) / (1800 - by1)); d.line([bx0 * u, yy, WW - (WW - bx1) * u, yy], fill=(128, 128, 124, 255), width=3)
    luz = Image.new("RGBA", (WW, WH), (0, 0, 0, 0))
    ImageDraw.Draw(luz).polygon([(dx0, by1), (dx1, by1), (dx1 + 380, WH), (dx0 - 380, WH)], fill=(255, 244, 210, 60))
    img.alpha_composite(luz.filter(ImageFilter.GaussianBlur(30)))
    d.line([0, 2050, WW, 2050], fill=(230, 190, 40, 255), width=14)
    return img

def sombra_avion(img, cx, cy, L):
    sh = Image.new("RGBA", (int(L * 1.0), int(L * 0.12)), (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse([0, 0, sh.width - 1, sh.height - 1], fill=(20, 24, 40, 80))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)), (int(cx - sh.width / 2 + L * 0.08), int(cy)))

# ------------------------------------------------------------ piel del avión con mapa térmico neón
WCX, WCY = WW / 2, 1000
_PIEL = {}
def _piel_base(forma):
    if forma in _PIEL: return _PIEL[forma]
    yy, xx = np.mgrid[0:WH, 0:WW].astype(np.float32)
    base = 168 + 40 * (1 - yy / WH) + 6 * np.sin(xx * 0.9 + yy * 0.05)
    metal = np.stack([base * 0.95, base * 0.98, base * 1.04], -1)
    for sx in (90, WW - 90):  # costuras
        metal[np.abs(xx - sx) < 3] *= 0.7
    for sy in (360, 1660):
        metal[np.abs(yy - sy) < 3] *= 0.7
    if forma == "cuadrada":
        a, b, rc = 270, 330, 22
        dx = np.abs(xx - WCX) - a; dy = np.abs(yy - WCY) - b
        dist = np.sqrt(np.maximum(dx, 0) ** 2 + np.maximum(dy, 0) ** 2) + np.minimum(np.maximum(dx, dy), 0)
        inside = dist < 0
        corners = [(WCX + sx * a, WCY + sy * b) for sx in (-1, 1) for sy in (-1, 1)]
        cdist = np.min([np.hypot(xx - px, yy - py) for px, py in corners], axis=0)
        s = 0.22 * np.exp(-np.maximum(dist, 0) / 160) + 1.1 * np.exp(-cdist / 75)
        frame_m = (dist >= 0) & (dist < 34)
    else:
        a, b = 230, 300
        r = np.sqrt(((xx - WCX) / a) ** 2 + ((yy - WCY) / b) ** 2)
        inside = r < 1
        dist = (r - 1) * 260
        s = 0.40 * np.exp(-np.maximum(dist, 0) / 190)
        frame_m = (dist >= 0) & (dist < 34)
    s[inside] = 0
    # ventana: cielo + reflejo
    skyc = np.stack([lerp(SKY_T[i], SKY_B[i], 1) * 0 + (SKY_T[i] + (SKY_B[i] - SKY_T[i]) * np.clip((yy - (WCY - b)) / (2 * b), 0, 1)) for i in range(3)], -1)
    streak = np.exp(-(((xx - WCX) + (yy - WCY) * 0.7 + 60) / 50) ** 2) * 70
    skyc = skyc + streak[..., None]
    metal = np.where(inside[..., None], skyc, metal)
    metal = np.where(frame_m[..., None], np.array([70, 74, 82], np.float32) + 50 * np.exp(-((dist - 8) / 6) ** 2)[..., None], metal)
    img = Image.fromarray(np.clip(metal, 0, 255).astype(np.uint8)).convert("RGBA")
    d = ImageDraw.Draw(img)
    for sy in (330, 1690):
        for x in range(40, WW, 70): d.ellipse([x - 9, sy - 9, x + 9, sy + 9], fill=(120, 124, 132, 255)); d.ellipse([x - 5, sy - 6, x + 3, sy + 2], fill=(220, 224, 230, 255))
    _PIEL[forma] = (img, s.astype(np.float32))
    return _PIEL[forma]

def neon_map(s):
    c1 = np.array([155, 81, 224], np.float32); c2 = np.array([255, 42, 109], np.float32); c3 = np.array([255, 208, 0], np.float32)
    lo = (s < 0.5)[..., None]
    return np.where(lo, c1 + (c2 - c1) * np.clip(s / 0.5, 0, 1)[..., None], c2 + (c3 - c2) * np.clip((s - 0.5) / 0.5, 0, 1)[..., None])

def piel(forma, presion, t=0.0, grieta=0.0):
    base, s = _piel_base(forma)
    img = base.copy()
    ss = np.clip(s * presion, 0, 1)
    sub = (slice(None, None, 2), slice(None, None, 2))   # media resolución para velocidad
    sm = ss[sub]
    col = neon_map(sm); a = np.clip((sm - 0.10) * 1.8, 0, 0.92)
    lay = np.concatenate([col, (a * 255)[..., None]], -1).astype(np.uint8)
    L = Image.fromarray(lay, "RGBA").resize((WW, WH), Image.BILINEAR)
    img.alpha_composite(L)
    gl = L.filter(ImageFilter.GaussianBlur(28)); ga = np.array(gl); ga[..., 3] = (ga[..., 3] * 0.8).astype(np.uint8)
    img.alpha_composite(Image.fromarray(ga))
    if grieta > 0:
        d = ImageDraw.Draw(img)
        x0, y0 = WCX + 270, WCY - 330
        r = np.random.default_rng(9); pts = [(x0, y0)]
        for j in range(int(2 + 16 * grieta)):
            px, py = pts[-1]; pts.append((px + r.uniform(10, 26), py - r.uniform(-8, 22)))
        d.line(pts, fill=(15, 8, 8, 255), width=12)
        if len(pts) > 6:
            bx, by = pts[5]; d.line([(bx, by), (bx + 30, by + 40), (bx + 50, by + 60)], fill=(15, 8, 8, 255), width=7)
    return img

# ------------------------------------------------------------ utilería de papel
def pegar(img, lay, cx, cy, ang=0.0, sombra=True):
    if ang: lay = lay.rotate(ang, resample=Image.BICUBIC, expand=True)
    if sombra:
        a = np.array(lay); sh = np.zeros_like(a); sh[..., 3] = (a[..., 3] * 0.4).astype(np.uint8)
        img.alpha_composite(Image.fromarray(sh).filter(ImageFilter.GaussianBlur(14)), (int(cx - lay.width / 2 + 22), int(cy - lay.height / 2 + 30)))
    img.alpha_composite(lay, (int(cx - lay.width / 2), int(cy - lay.height / 2)))

def periodico(titular, sub="1952"):
    w, h = 900, 1100
    lay = Image.new("RGBA", (w, h), (244, 236, 214, 255)); d = ImageDraw.Draw(lay)
    d.rectangle([0, 0, w - 1, h - 1], outline=(60, 50, 40, 255), width=6)
    f = font(F_SERIF, 74); t0 = "EL DIARIO DEL CIELO"; d.text((w / 2 - f.getlength(t0) / 2, 40), t0, font=f, fill=(30, 26, 22))
    d.line([40, 140, w - 40, 140], fill=(30, 26, 22), width=5); d.line([40, 152, w - 40, 152], fill=(30, 26, 22), width=2)
    f2 = font(F_BOLD, 34); d.text((50, 160), sub, font=f2, fill=(80, 70, 60)); d.text((w - 220, 160), "5 centavos", font=f2, fill=(80, 70, 60))
    fh = font(F_SERIF, 92); y = 230
    for line in titular:
        d.text((w / 2 - fh.getlength(line) / 2, y), line, font=fh, fill=(20, 18, 16)); y += 108
    y += 20
    d.rectangle([50, y, 470, y + 330], fill=(200, 192, 172, 255), outline=(60, 50, 40, 255), width=4)
    avion(lay, 260, y + 170, 400, "cuadradas", color=(230, 226, 214))
    for k in range(9):
        d.line([500, y + 20 + k * 36, w - 50, y + 20 + k * 36], fill=(150, 140, 125), width=10)
    for k in range(5):
        d.line([50, y + 370 + k * 36, w - 50, y + 370 + k * 36], fill=(150, 140, 125), width=10)
    return lay

def calendario(anio, vuelos):
    w, h = 620, 700
    lay = Image.new("RGBA", (w, h), (250, 248, 240, 255)); d = ImageDraw.Draw(lay)
    d.rectangle([0, 0, w, 170], fill=(200, 50, 50, 255))
    for x in range(70, w, 80): d.ellipse([x - 14, -14, x + 14, 14], fill=(40, 40, 44, 255))
    f = font(F_BLACK, 110); d.text((w / 2 - f.getlength(anio) / 2, 30), anio, font=f, fill=(255, 255, 255))
    for r_ in range(5):
        for c in range(7):
            x, y = 40 + c * 78, 210 + r_ * 92
            done = r_ * 7 + c < vuelos
            d.rectangle([x, y, x + 64, y + 76], outline=(180, 176, 168, 255), width=3)
            if done:
                d.line([x + 8, y + 8, x + 56, y + 68], fill=(210, 40, 40, 255), width=8); d.line([x + 56, y + 8, x + 8, y + 68], fill=(210, 40, 40, 255), width=8)
    lay = lay.copy(); ImageDraw.Draw(lay).rectangle([0, 0, w - 1, h - 1], outline=(40, 40, 44, 255), width=5)
    return lay

def manometro(val):
    r = 330; lay = Image.new("RGBA", (2 * r, 2 * r), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.ellipse([0, 0, 2 * r - 1, 2 * r - 1], fill=(60, 62, 68, 255))
    d.ellipse([22, 22, 2 * r - 22, 2 * r - 22], fill=(246, 242, 230, 255), outline=(30, 30, 34, 255), width=6)
    for k in range(11):
        a = math.radians(225 - k * 27); x1, y1 = r + math.cos(a) * (r - 50), r - math.sin(a) * (r - 50)
        x2, y2 = r + math.cos(a) * (r - 90), r - math.sin(a) * (r - 90)
        d.line([x1, y1, x2, y2], fill=(200, 40, 40, 255) if k > 7 else (30, 30, 34, 255), width=10)
    f = font(F_BLACK, 52); d.text((r - f.getlength("PRESIÓN") / 2, r + 90), "PRESIÓN", font=f, fill=(30, 30, 34))
    a = math.radians(225 - val * 270)
    d.line([r, r, r + math.cos(a) * (r - 80), r - math.sin(a) * (r - 80)], fill=(210, 40, 40, 255), width=16)
    d.ellipse([r - 30, r - 30, r + 30, r + 30], fill=(30, 30, 34, 255))
    return lay

def estrella(d, x, y, r, a=0.0, col=(255, 255, 255, 255)):
    pts = []
    for k in range(8):
        rr = r if k % 2 == 0 else r * 0.25; an = a + k * math.pi / 4
        pts.append((x + math.cos(an) * rr, y + math.sin(an) * rr))
    d.polygon(pts, fill=col)

def letras(img, txt, x, y, size, col=(255, 230, 0), ang=0.0, stroke=10):
    f = font(F_BLACK, size); tw = f.getlength(txt)
    lay = Image.new("RGBA", (int(tw + 60), int(size * 1.5)), (0, 0, 0, 0))
    ImageDraw.Draw(lay).text((30, 10), txt, font=f, fill=col + (255,), stroke_width=stroke, stroke_fill=(0, 0, 0))
    pegar(img, lay, x, y, ang, sombra=False)

def etiqueta2(img, txt, x, y, col, size=58):
    d = ImageDraw.Draw(img); f = font(F_BLACK, size); tw = f.getlength(txt)
    d.rounded_rectangle([x - tw / 2 - 30, y - 12, x + tw / 2 + 30, y + size + 22], radius=16, fill=col + (255,), outline=INK, width=6)
    d.text((x - tw / 2, y), txt, font=f, fill=(255, 255, 255, 255))

# ------------------------------------------------------------ planos: 13 frases, cada una con 2 cortes
SHOTS = []
def shot(fn): SHOTS.append(fn); return fn
def corte(t, D, f=0.5): return t >= D * f, (t - D * f if t >= D * f else t), (D * (1 - f) if t >= D * f else D * f)

@shot
def p1(t, D):
    b, tt, dd = corte(t, D, 0.42)
    if not b:   # ventana redonda gigante, la cámara se aleja
        img = piel("redonda", 0.0)
        return img, (WCX, WCY + 150, lerp(1.9, 1.05, ease(tt / dd)), 0)
    img = cielo2(t, 260, hy=WH + 10)   # plano aéreo: avión sobre las nubes
    avion(img, 690 + 30 * math.sin(t * 2), 1050 + 20 * math.sin(t * 3), 1150, "redondas", ang=-5)
    return img, (648, 1150, 1.0 + 0.08 * ease(tt / dd), 0)

@shot
def p2(t, D):
    b, tt, dd = corte(t, D, 0.5)
    if not b:
        img = hangar2(t)
        figura(img, 360, 1850, 1.0, NICO, "neutral", "idle", t, mira=0.6)
        figura(img, 940, 1850, 1.0, BRUNO, "smug", "cross", t, mira=-0.6, pelo=True)
        return img, (648, 1400, lerp(1.0, 1.08, ease(tt / dd)), 0)
    img = hangar2(t)   # cara a cara, contrapicado
    figura(img, 250, 2350, 2.2, NICO, "angry", "idle", t, mira=1)
    figura(img, 1050, 2350, 2.2, BRUNO, "smug", "idle", t, mira=-1, pelo=True)
    letras(img, "VS", 648 + 6 * math.sin(t * 40), 1150, 230, ang=8)
    return img, (648, 1250, 1.05, 4)

@shot
def p3(t, D):
    b, tt, dd = corte(t, D, 0.5)
    if not b:
        img = hangar2(t)
        sombra_avion(img, 720, 1430, 1150)
        avion(img, 720, 1200, 1150, "cuadradas", color=(240, 238, 232))
        figura(img, 330, 1900, 1.0, BRUNO, "smug", "point", t, pelo=True, mira=0.5)
        etiqueta2(img, "VENTANAS CUADRADAS", 648, 520, (200, 52, 52))
        return img, (lerp(560, 700, ease(tt / dd)), 1350, 1.04, 0)
    img = piel("cuadrada", 0.0)
    d = ImageDraw.Draw(img)
    for k, (x, y) in enumerate([(WCX - 150, WCY - 200), (WCX + 120, WCY + 80), (WCX - 60, WCY + 230)]):
        estrella(d, x, y, 60 + 25 * math.sin(t * 8 + k), t * 3 + k)
    return img, (WCX, WCY + 150, lerp(1.25, 1.1, ease(tt / dd)), 0)

@shot
def p4(t, D):
    b, tt, dd = corte(t, D, 0.45)
    if not b:
        img = hangar2(t)
        sombra_avion(img, 560, 1430, 1150)
        avion(img, 560, 1200, 1150, "redondas")
        figura(img, 980, 1900, 1.0, NICO, "worried", "chin", t, mira=-0.5)
        etiqueta2(img, "VENTANAS REDONDAS", 648, 520, (30, 150, 160))
        return img, (lerp(760, 640, ease(tt / dd)), 1350, 1.04, 0)
    img = hangar2(t)   # todos se burlan
    for k, x in enumerate((220, 470, 820, 1080)):
        ropa = BRUNO if k == 2 else GRISES[k % 3]
        figura(img, x, 1880 + (k % 2) * 40, 0.85, ropa, "laugh", "laugh", t + k * 0.3, pelo=(k == 2))
    for k, (x, y) in enumerate([(300, 1050), (700, 920), (1030, 1080), (520, 1200)]):
        if tt > 0.1 + k * 0.18: letras(img, "JA", x, y + 14 * math.sin(t * 12 + k), 120, ang=(-12 + k * 9))
    return img, (648, 1400, 1.02, 2)

@shot
def p5(t, D):
    b, tt, dd = corte(t, D, 0.5)
    if not b:   # despega el avión de Bruno, cámara baja pegada a la pista
        img, proj = pista(t, vel=2600, camh=170)
        k = ease(tt / dd)
        avion(img, lerp(250, 900, k), lerp(1250, 700, k ** 1.5), lerp(900, 1500, k), "cuadradas", ang=8 * k, color=(240, 238, 232))
        return img, (648, 1250, 1.0, 3)
    img = cielo2(t, 40); img = img.filter(ImageFilter.GaussianBlur(6))
    k = eob(tt / 0.35)
    pg = periodico(["¡TODAS LAS", "AEROLÍNEAS", "ELIGEN A BRUNO!"])
    pg = pg.resize((max(1, int(pg.width * k)), max(1, int(pg.height * k))), Image.LANCZOS)
    pegar(img, pg, 648, 1150, ang=(1 - k) * 380 - 4)
    return img, (648, 1200, 1.02, 0)

@shot
def p6(t, D):
    b, tt, dd = corte(t, D, 0.55)
    if not b:   # la cabina se infla y se desinfla
        img = cielo2(t, 200, (24, 70, 160), (120, 175, 230), hy=WH + 10)
        p = 1 + 0.045 * math.sin(t * 5)
        avion(img, 700, 1100, 1150 * p, "cuadradas", color=(240, 238, 232))
        d = ImageDraw.Draw(img); sg = 1 if math.sin(t * 5) > 0 else -1
        for k in range(9):
            x = 260 + k * 95
            for side in (-1, 1):
                y0 = 1100 + side * 120; y1 = 1100 + side * 230
                if sg < 0: y0, y1 = y1, y0
                d.line([x, y0, x, y1], fill=(255, 255, 255, 255), width=12)
                d.polygon([(x - 20, y1), (x + 20, y1), (x, y1 + (y1 - y0) / abs(y1 - y0) * 34)], fill=(255, 255, 255, 255))
        return img, (648, 1150, 1.0, 0)
    img = grad((30, 34, 44), (52, 56, 70))
    pegar(img, manometro(0.5 + 0.42 * math.sin(t * 5)), 648, 1050)
    return img, (648, 1100, lerp(1.0, 1.1, ease(tt / dd)), 0)

@shot
def p7(t, D):
    b, tt, dd = corte(t, D, 0.55)
    pres = 0.25 + 0.85 * ease(t / (D * 0.7)) + 0.08 * math.sin(t * 7)
    img = piel("cuadrada", pres, t)
    if not b:
        etiqueta2(img, "LA FUERZA SE ACUMULA", 648, 470, (120, 50, 150))
        return img, (WCX, WCY + 140, lerp(1.05, 1.15, ease(tt / dd)), 0)
    return img, (WCX + 200, WCY - 220, 2.1, 0)   # zoom a la esquina

@shot
def p8(t, D):
    b, tt, dd = corte(t, D, 0.55)
    if not b:   # calendario que pasa los años
        img = hangar2(t).filter(ImageFilter.GaussianBlur(8))
        yrs = ["1952", "1953", "1954"]; i = min(2, int(tt / dd * 3))
        pegar(img, calendario(yrs[i], int((tt / dd * 3 % 1) * 35)), 648, 1080, ang=-3)
        n = int(lerp(1, 3000, ease(tt / dd)))
        letras(img, f"{n:,}".replace(",", ".") + " VUELOS", 648, 560, 120)
        return img, (648, 1100, 1.0, 0)
    pres = 1.05 + 0.12 * math.sin(t * 9)
    img = piel("cuadrada", pres, t)
    return img, (WCX + 220, WCY - 260, 2.4 + 0.15 * math.sin(t * 9), 0)

@shot
def p9(t, D):
    b, tt, dd = corte(t, D, 0.5)
    if not b:   # ¡grieta!
        k = ease(tt / (dd * 0.8))
        img = piel("cuadrada", 1.15, t, grieta=k)
        if tt > dd * 0.35:
            img.alpha_composite(Image.new("RGBA", img.size, (255, 0, 0, int(60 + 40 * math.sin(t * 20)))))
        return img, (WCX + 260 + 120 * k, WCY - 300 - 40 * k, 2.0 + 0.3 * k, 26 * k * math.exp(-max(0, tt - dd * 0.4) * 3))
    img = hangar2(t)
    img.alpha_composite(Image.new("RGBA", img.size, (255, 0, 0, int(40 + 30 * math.sin(t * 20)))))
    figura(img, 648, 2550, 2.7, BRUNO, "shock", "shock", t, pelo=True, sudor=True, sombra=False)
    return img, (648, 1200, 1.0, 10 * math.exp(-tt * 4))

@shot
def p10(t, D):
    b, tt, dd = corte(t, D, 0.5)
    if not b:   # aviones en tierra, día gris
        img, proj = pista(t, 0, 230, tono=0.75, top=(100, 104, 120), bot=(170, 168, 172))
        for (x, y, L) in [(330, 1330, 640), (960, 1420, 780)]:
            sombra_avion(img, x, y + L * 0.18, L); avion(img, x, y, L, "cuadradas", crack=1.0, color=(220, 218, 212))
        d = ImageDraw.Draw(img)
        for k in range(14):   # cinta de "no pasar"
            x = k * 100; d.polygon([(x, 1700), (x + 50, 1700), (x + 30, 1740), (x - 20, 1740)], fill=(250, 200, 30, 255) if k % 2 else (30, 30, 30, 255))
        etiqueta2(img, "EN TIERRA", 648, 560, (200, 40, 40), 90)
        return img, (648, 1350, lerp(1.0, 1.06, ease(tt / dd)), 0)
    img = hangar2(t)   # Bruno morado de rabia, echando vapor
    figura(img, 648, 2350, 2.1, BRUNO, "angry", "idle", t, cara=PURP, vapor=True, pelo=True, sombra=False)
    return img, (648, 1250, 1.0, 5)

@shot
def p11(t, D):
    b, tt, dd = corte(t, D, 0.55)
    if not b:   # ventana redonda: fuerza repartida, sin punto rojo
        pres = 0.7 + 0.35 * ease(tt / dd) + 0.06 * math.sin(t * 6)
        img = piel("redonda", pres, t)
        etiqueta2(img, "FUERZA REPARTIDA ✓", 648, 470, (30, 150, 120))
        return img, (WCX, WCY + 140, lerp(1.15, 1.05, ease(tt / dd)), 0)
    img = hangar2(t)
    sombra_avion(img, 700, 1420, 1100); avion(img, 700, 1190, 1100, "redondas")
    figura(img, 648, 1950, 1.1, NICO, "happy", "arms_up", t)
    d = ImageDraw.Draw(img)
    for k in range(5): estrella(d, 300 + k * 180, 900 + 60 * math.sin(t * 5 + k), 34, t * 4 + k, (255, 230, 0, 255))
    return img, (648, 1450, 1.02, 0)

@shot
def p12(t, D):
    b, tt, dd = corte(t, D, 0.55)
    if not b:   # hoy: avión moderno pasa por encima, cámara en el suelo
        img, proj = pista(t, 300, 150)
        k = ease(tt / dd)
        avion(img, lerp(1500, -150, k), lerp(820, 620, k), 1700, "redondas", ang=-6, color=(246, 248, 252))
        return img, (648, 1200, 1.0, 3 * math.sin(t * 30) * (1 - abs(k - 0.5) * 2))
    img = piel("redonda", 0.0)
    return img, (WCX, WCY + 140, lerp(1.05, 1.3, ease(tt / dd)), 0)

@shot
def p13(t, D):
    img, proj = pista(t, 0, 230)
    sombra_avion(img, 700, 1390, 1100); avion(img, 700, 1180, 1100, "redondas")
    figura(img, 648, 1900, 1.15, NICO, "happy", "point" if (t % 1.6) < 0.8 else "arms_up", t)
    d = ImageDraw.Draw(img)
    for k in range(40):
        x = (k * 97) % WW; y = (k * 211 + t * 700) % 1400 + 250
        d.rectangle([x, y, x + 18, y + 30], fill=[(255, 214, 10), (60, 200, 255), (255, 80, 120)][k % 3] + (255,))
    return img, (648, 1400, 1.0 + 0.04 * ease(t / D), 0)

# ------------------------------------------------------------ voz, subtítulos, cámara y audio (de porque.py)
_s = next(i for i, l in enumerate(_src) if l.startswith("# ------------------------------------------------------------ voz y tiempos"))
_e = next(i for i, l in enumerate(_src) if l.startswith("def frame(T):"))
_m0 = next(i for i, l in enumerate(_src) if l.startswith("def make_audio"))
_m1 = next(i for i, l in enumerate(_src) if l.startswith("if __name__"))
exec("\n".join(_src[_s:_e] + _src[_m0:_m1]), globals())
CAPS = [(a, b, c.replace(" 👇", " ↓"), [h.replace(" 👇", "") for h in hl]) for a, b, c, hl in CAPS]

def frame(T):
    i = max(j for j in range(len(SHOTS)) if STARTS[j] <= T) if T < TOTAL else len(SHOTS) - 1
    t = T - STARTS[i]
    world, (cx, cy, z, sh) = SHOTS[i](t, DURS[i])
    img = camera(world, cx, cy, z, sh, T)
    img = realce.postproceso(img, T, tono="neutro", bloom=0.22, grano=0.0, motas=False)
    d = ImageDraw.Draw(img); f = font(F_BLACK, 46)
    d.rounded_rectangle([40, 120, 40 + f.getlength("¿POR QUÉ?") + 50, 200], radius=20, fill=(255, 214, 10, 240), outline=INK, width=5)
    d.text((65, 132), "¿POR QUÉ?", font=f, fill=(20, 20, 30))
    caption(img, T)
    return img.convert("RGB")

if __name__ == "__main__":
    if os.environ.get("PREVIEW"):
        ts = [float(x) for x in os.environ["PREVIEW"].split(",")]
        ims = [frame(T).resize((270, 480)) for T in ts]
        sheet = Image.new("RGB", (270 * 5, 480 * ((len(ims) + 4) // 5)))
        for k, im in enumerate(ims): sheet.paste(im, ((k % 5) * 270, (k // 5) * 480))
        sheet.save("sheet2.png"); print("TOTAL", TOTAL, [round(s, 1) for s in STARTS]); sys.exit()
    if os.environ.get("BIG"):
        frame(float(os.environ["BIG"])).save("big.png"); sys.exit()
    make_audio("audio2.wav")
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-i", "audio2.wav", "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-pix_fmt", "yuv420p",
                          "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
    for k in range(int(TOTAL * FPS)): p.stdin.write(frame(k / FPS).tobytes())
    p.stdin.close(); p.wait(); print("listo", OUT, TOTAL)
