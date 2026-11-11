#!/usr/bin/env python3
"""Short: ¿Qué pasaría si llevas tu celular al Antiguo Egipto?  — 100% generado por código."""
import math, os, sys, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
WW, WH = 1296, 2304            # "mundo" (1.2x) para mover la cámara sin perder calidad
OUT = sys.argv[1] if len(sys.argv) > 1 else "egipto.mp4"
R = np.random.default_rng(3)

F_BLACK = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
F_BOLD = "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"
_fc = {}
def font(p, s):
    if (p, s) not in _fc: _fc[(p, s)] = ImageFont.truetype(p, s)
    return _fc[(p, s)]

OL = (34, 22, 40, 255)
YEL = (255, 214, 10); WHITE = (255, 255, 255)
SKIN = (246, 196, 152, 255); HOOD = (36, 178, 196, 255); PANTS = (44, 52, 86, 255)
EGY = (178, 112, 70, 255); KILT = (244, 238, 222, 255); GOLD = (240, 188, 52, 255); BLUE = (40, 84, 170, 255)

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)
def eob(x):
    x = clamp(x); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2
def lerp(a, b, t): return a + (b - a) * t
def lerpc(a, b, t): return tuple(int(lerp(x, y, t)) for x, y in zip(a, b))

# ------------------------------------------------------------ utilidades de dibujo
def grad(top, bot, w=WW, h=WH):
    t = np.linspace(0, 1, h)[:, None, None]
    a = np.array(top, float); b = np.array(bot, float)
    arr = (a + (b - a) * t).repeat(w, axis=1)
    out = np.dstack([arr, np.full((h, w, 1), 255)]).astype(np.uint8)
    return Image.fromarray(out, "RGBA")

def radial(size, color, strength=1.0, power=2.0):
    r = size / 2; c = (np.arange(size) + 0.5 - r) / r
    X, Y = np.meshgrid(c, c); rr = np.sqrt(X * X + Y * Y)
    a = np.clip(1 - rr, 0, 1) ** power * strength
    arr = np.zeros((size, size, 4), np.uint8); arr[..., :3] = color[:3]; arr[..., 3] = (a * 255).astype(np.uint8)
    return Image.fromarray(arr, "RGBA")
_rc = {}
def glow(img, x, y, size, color, strength=1.0, power=2.0):
    k = (size, color[:3], round(strength, 2), power)
    if k not in _rc:
        if len(_rc) > 300: _rc.clear()
        _rc[k] = radial(size, color, strength, power)
    img.alpha_composite(_rc[k], (int(x - size / 2), int(y - size / 2)))

def cap(d, p, r, col):
    d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=col)

def limb(d, pts, w, col, lw):
    d.line(pts, fill=OL, width=int(w + 2 * lw), joint="curve")
    for p in (pts[0], pts[-1]): cap(d, p, (w + 2 * lw) / 2, OL)
    d.line(pts, fill=col, width=int(w), joint="curve")
    for p in (pts[0], pts[-1]): cap(d, p, w / 2, col)

def shadow(d, x, y, w, a=70):
    d.ellipse([x - w, y - w * 0.18, x + w, y + w * 0.18], fill=(0, 0, 0, a))

def rot(px, py, cx, cy, a):
    c, s = math.cos(a), math.sin(a); dx, dy = px - cx, py - cy
    return (cx + dx * c - dy * s, cy + dx * s + dy * c)

# ------------------------------------------------------------ personaje: Nico
def nico(img, x, y, s=1.0, expr="happy", look=(0, 0), arms="down", phase=0.0, phone=False, screen=(120, 200, 255), flip=1, lean=0.0):
    d = ImageDraw.Draw(img); lw = 6 * s
    shadow(d, x, y + 4 * s, 95 * s)
    hip = (x, y - 150 * s)
    # piernas
    if arms == "run":
        a1, a2 = math.sin(phase) * 0.9, -math.sin(phase) * 0.9
    else:
        a1 = a2 = 0
    for sx, a in ((-24, a1), (24, a2)):
        hx = x + sx * s
        fx, fy = hx + math.sin(a) * 140 * s, y - (1 - math.cos(a)) * 140 * s * 0.5
        kx, ky = hx + math.sin(a * 0.5) * 70 * s + (12 * s if a > 0 else 0), y - 75 * s
        limb(d, [(hx, hip[1]), (kx, ky), (fx, fy)], 34 * s, PANTS, lw)
        d.ellipse([fx - 30 * s + 14 * s * flip, fy - 16 * s, fx + 30 * s + 14 * s * flip, fy + 12 * s], fill=(250, 250, 250, 255), outline=OL, width=int(lw))
    # cuerpo
    bx = x + lean * 40 * s
    d.rounded_rectangle([bx - 66 * s, y - 300 * s, bx + 66 * s, y - 140 * s], radius=int(40 * s), fill=HOOD, outline=OL, width=int(lw))
    d.rounded_rectangle([bx - 40 * s, y - 210 * s, bx + 40 * s, y - 160 * s], radius=int(16 * s), fill=(28, 150, 168, 255))
    d.line([bx - 14 * s, y - 290 * s, bx - 16 * s, y - 240 * s], fill=(255, 255, 255, 255), width=int(5 * s))
    d.line([bx + 14 * s, y - 290 * s, bx + 16 * s, y - 240 * s], fill=(255, 255, 255, 255), width=int(5 * s))
    # brazos
    sh_l, sh_r = (bx - 58 * s, y - 270 * s), (bx + 58 * s, y - 270 * s)
    if arms == "down":
        hl, hr = (bx - 84 * s, y - 160 * s), (bx + 84 * s, y - 160 * s)
    elif arms == "up":
        w_ = math.sin(phase * 2) * 18 * s
        hl, hr = (bx - 130 * s, y - 420 * s + w_), (bx + 130 * s, y - 420 * s - w_)
    elif arms == "phone":
        hl, hr = (bx - 84 * s, y - 160 * s), (bx + 70 * s, y - 330 * s)
    elif arms == "phone_up":
        hl, hr = (bx - 84 * s, y - 160 * s), (bx + 120 * s, y - 440 * s)
    elif arms == "run":
        hl = (bx - 60 * s - math.sin(phase) * 70 * s, y - 190 * s)
        hr = (bx + 60 * s + math.sin(phase) * 70 * s, y - 190 * s)
    else:
        hl, hr = (bx - 84 * s, y - 160 * s), (bx + 84 * s, y - 160 * s)
    for sh, hd in ((sh_l, hl), (sh_r, hr)):
        el = ((sh[0] + hd[0]) / 2 + (sh[0] - x) * 0.15, (sh[1] + hd[1]) / 2 + 10 * s)
        limb(d, [sh, el, hd], 30 * s, HOOD, lw)
        cap(d, hd, 21 * s, OL); cap(d, hd, 17 * s, SKIN)
    if phone:
        px, py = hr
        d.rounded_rectangle([px - 24 * s, py - 44 * s, px + 24 * s, py + 30 * s], radius=int(8 * s), fill=(24, 24, 32, 255), outline=OL, width=int(4 * s))
        d.rounded_rectangle([px - 18 * s, py - 38 * s, px + 18 * s, py + 24 * s], radius=int(5 * s), fill=screen + (255,))
    # cabeza
    hx, hy = bx + lean * 30 * s, y - 400 * s; r = 98 * s
    for ex in (-1, 1):
        cap(d, (hx + ex * 96 * s, hy + 10 * s), 24 * s, OL); cap(d, (hx + ex * 96 * s, hy + 10 * s), 19 * s, SKIN)
    d.ellipse([hx - r, hy - r, hx + r, hy + r], fill=SKIN, outline=OL, width=int(lw))
    hair = (58, 36, 30, 255)
    d.chord([hx - r - 4 * s, hy - r - 14 * s, hx + r + 4 * s, hy + r * 0.55], 180, 360, fill=hair, outline=OL, width=int(lw))
    for k in range(5):
        cx_ = hx - r * 0.8 + k * r * 0.4
        d.ellipse([cx_ - 30 * s, hy - r - 26 * s, cx_ + 30 * s, hy - r + 30 * s], fill=hair)
    d.ellipse([hx - r * 0.9, hy - r * 0.42, hx + r * 0.9, hy + r * 0.2], fill=SKIN)
    d.rectangle([hx - r * 0.85, hy - r * 0.2, hx + r * 0.85, hy + r * 0.2], fill=SKIN)
    # cara
    lx, ly = look[0] * 8 * s, look[1] * 8 * s
    for ex in (-36, 36):
        ecx, ecy = hx + ex * s, hy + 2 * s
        if expr == "shock":
            er = 28 * s
        else:
            er = 22 * s
        d.ellipse([ecx - er, ecy - er * 1.15, ecx + er, ecy + er * 1.15], fill=(255, 255, 255, 255), outline=OL, width=int(4 * s))
        pr = 11 * s if expr != "shock" else 8 * s
        d.ellipse([ecx - pr + lx, ecy - pr + ly, ecx + pr + lx, ecy + pr + ly], fill=OL)
        d.ellipse([ecx - pr * 0.4 + lx + 3 * s, ecy - pr * 0.6 + ly, ecx + pr * 0.2 + lx + 3 * s, ecy + ly], fill=(255, 255, 255, 255))
    by = hy - 38 * s
    if expr in ("worried", "scared"):
        d.line([hx - 58 * s, by + 4 * s, hx - 18 * s, by - 10 * s], fill=OL, width=int(7 * s))
        d.line([hx + 18 * s, by - 10 * s, hx + 58 * s, by + 4 * s], fill=OL, width=int(7 * s))
    elif expr == "smug":
        d.line([hx - 58 * s, by - 4 * s, hx - 18 * s, by - 4 * s], fill=OL, width=int(7 * s))
        d.line([hx + 18 * s, by - 14 * s, hx + 58 * s, by - 2 * s], fill=OL, width=int(7 * s))
    else:
        d.arc([hx - 60 * s, by - 10 * s, hx - 16 * s, by + 14 * s], 200, 340, fill=OL, width=int(7 * s))
        d.arc([hx + 16 * s, by - 10 * s, hx + 60 * s, by + 14 * s], 200, 340, fill=OL, width=int(7 * s))
    my = hy + 52 * s
    if expr == "happy" or expr == "smug":
        d.chord([hx - 30 * s, my - 22 * s, hx + 30 * s, my + 22 * s], 0, 180, fill=(120, 30, 40, 255), outline=OL, width=int(5 * s))
    elif expr == "shock":
        d.ellipse([hx - 18 * s, my - 14 * s, hx + 18 * s, my + 26 * s], fill=(120, 30, 40, 255), outline=OL, width=int(5 * s))
    elif expr == "scared":
        pts = [(hx - 30 * s + k * 10 * s, my + (6 if k % 2 else -6) * s) for k in range(7)]
        d.line(pts, fill=OL, width=int(6 * s))
    else:
        d.arc([hx - 24 * s, my - 4 * s, hx + 24 * s, my + 22 * s], 200, 340, fill=OL, width=int(6 * s))
    d.ellipse([hx - 76 * s, hy + 22 * s, hx - 46 * s, hy + 38 * s], fill=(240, 140, 140, 120))
    d.ellipse([hx + 46 * s, hy + 22 * s, hx + 76 * s, hy + 38 * s], fill=(240, 140, 140, 120))

# ------------------------------------------------------------ egipcios
def egipcio(img, x, y, s=1.0, kind="worker", pose="stand", item=None, t=0.0, mood="neutral", tint=None):
    d = ImageDraw.Draw(img); lw = 6 * s
    skin = EGY if tint is None else tint
    shadow(d, x, y + 4 * s, 85 * s)
    kneel = pose == "kneel"
    off = 110 * s if kneel else 0
    yb = y + off
    # piernas
    if not kneel:
        for sx in (-22, 22):
            limb(d, [(x + sx * s, y - 150 * s), (x + sx * s, y - 10 * s)], 30 * s, skin, lw)
    else:
        d.rounded_rectangle([x - 70 * s, y - 70 * s, x + 70 * s, y - 10 * s], radius=int(28 * s), fill=skin, outline=OL, width=int(lw))
    # falda
    d.polygon([(x - 62 * s, yb - 210 * s), (x + 62 * s, yb - 210 * s), (x + 74 * s, yb - 110 * s), (x - 74 * s, yb - 110 * s)], fill=KILT, outline=OL)
    if kind == "pharaoh":
        d.polygon([(x - 16 * s, yb - 200 * s), (x + 16 * s, yb - 200 * s), (x + 22 * s, yb - 110 * s), (x - 22 * s, yb - 110 * s)], fill=GOLD, outline=OL)
    # torso
    d.rounded_rectangle([x - 58 * s, yb - 320 * s, x + 58 * s, yb - 200 * s], radius=int(30 * s), fill=skin, outline=OL, width=int(lw))
    d.rectangle([x - 62 * s, yb - 222 * s, x + 62 * s, yb - 200 * s], fill=GOLD if kind == "pharaoh" else (196, 160, 90, 255), outline=OL)
    # collar
    for k, c in enumerate([GOLD, BLUE, GOLD, (200, 60, 50, 255)]):
        rr = (78 - k * 12) * s
        d.chord([x - rr, yb - 330 * s - rr * 0.55, x + rr, yb - 330 * s + rr * 0.85], 0, 180, fill=c, outline=OL)
    # brazos
    shl, shr = (x - 54 * s, yb - 300 * s), (x + 54 * s, yb - 300 * s)
    if kneel:
        b = math.sin(t * 6) * 16 * s
        hl, hr = (x - 120 * s, yb - 430 * s + b), (x + 120 * s, yb - 430 * s + b)
    elif pose == "angry":
        hl, hr = (x - 80 * s, yb - 190 * s), (x + 110 * s, yb - 440 * s + math.sin(t * 9) * 20 * s)
    elif pose == "point":
        hl, hr = (x - 80 * s, yb - 190 * s), (x + 150 * s, yb - 330 * s)
    elif pose == "throne":
        hl, hr = (x - 100 * s, yb - 220 * s), (x + 100 * s, yb - 220 * s)
    else:
        hl, hr = (x - 80 * s, yb - 180 * s), (x + 80 * s, yb - 180 * s)
    for sh, hd in ((shl, hl), (shr, hr)):
        limb(d, [sh, hd], 28 * s, skin, lw)
        d.rectangle([(sh[0] + hd[0]) / 2 - 16 * s, (sh[1] + hd[1]) / 2 - 8 * s, (sh[0] + hd[0]) / 2 + 16 * s, (sh[1] + hd[1]) / 2 + 8 * s], fill=GOLD)
    if item == "spear":
        px, py = hr
        d.line([px, py + 160 * s, px, py - 240 * s], fill=(110, 70, 40, 255), width=int(12 * s))
        d.polygon([(px - 18 * s, py - 230 * s), (px + 18 * s, py - 230 * s), (px, py - 300 * s)], fill=(200, 200, 210, 255), outline=OL)
    if item == "torch":
        px, py = hr
        d.line([px, py + 60 * s, px, py - 90 * s], fill=(110, 70, 40, 255), width=int(14 * s))
        fl = 1 + 0.15 * math.sin(t * 23)
        glow(img, px, py - 130 * s, int(260 * s), (255, 150, 40), 0.55)
        d = ImageDraw.Draw(img)
        d.polygon([(px - 26 * s, py - 92 * s), (px + 26 * s, py - 92 * s), (px + 8 * s, py - 170 * s * fl), (px, py - 200 * s * fl), (px - 12 * s, py - 160 * s * fl)], fill=(255, 160, 40, 255))
        d.polygon([(px - 12 * s, py - 92 * s), (px + 12 * s, py - 92 * s), (px, py - 150 * s * fl)], fill=(255, 236, 140, 255))
    # cabeza
    hx, hy = x, yb - 410 * s; r = 84 * s
    if kind == "pharaoh":
        # nemes rayado
        d.polygon([(hx - r * 1.25, hy - r * 0.6), (hx + r * 1.25, hy - r * 0.6), (hx + r * 1.45, hy + r * 1.6), (hx - r * 1.45, hy + r * 1.6)], fill=GOLD, outline=OL)
        for k in range(7):
            yy = hy - r * 0.4 + k * r * 0.3
            d.line([hx - r * 1.4, yy, hx + r * 1.4, yy], fill=BLUE, width=int(10 * s))
    d.ellipse([hx - r, hy - r, hx + r, hy + r], fill=skin, outline=OL, width=int(lw))
    if kind == "pharaoh":
        d.chord([hx - r * 1.12, hy - r * 1.35, hx + r * 1.12, hy + r * 0.4], 180, 360, fill=GOLD, outline=OL, width=int(lw))
        for k in range(4):
            yy = hy - r * 1.1 + k * r * 0.26
            d.line([hx - r * 0.95, yy, hx + r * 0.95, yy], fill=BLUE, width=int(9 * s))
        d.rectangle([hx - r, hy - r * 0.5, hx + r, hy - r * 0.32], fill=GOLD, outline=OL)
        d.polygon([(hx - 9 * s, hy - r * 1.2), (hx + 9 * s, hy - r * 1.2), (hx + 6 * s, hy - r * 0.6), (hx - 6 * s, hy - r * 0.6)], fill=(220, 60, 50, 255), outline=OL)
        d.rounded_rectangle([hx - 12 * s, hy + r * 0.85, hx + 12 * s, hy + r * 1.5], radius=int(6 * s), fill=(40, 30, 30, 255))
    else:
        d.chord([hx - r * 1.12, hy - r * 1.18, hx + r * 1.12, hy + r * 0.95], 150, 390, fill=(24, 20, 26, 255))
        d.rectangle([hx - r * 1.12, hy - r * 0.2, hx - r * 0.75, hy + r * 0.95], fill=(24, 20, 26, 255))
        d.rectangle([hx + r * 0.75, hy - r * 0.2, hx + r * 1.12, hy + r * 0.95], fill=(24, 20, 26, 255))
        d.ellipse([hx - r * 0.8, hy - r * 0.45, hx + r * 0.8, hy + r * 0.9], fill=skin)
    for ex in (-30, 30):
        ecx, ecy = hx + ex * s, hy + 4 * s
        d.ellipse([ecx - 22 * s, ecy - 13 * s, ecx + 22 * s, ecy + 13 * s], fill=(255, 255, 255, 255), outline=(20, 16, 20, 255), width=int(6 * s))
        d.line([ecx + (18 if ex > 0 else -18) * s, ecy, ecx + (36 if ex > 0 else -36) * s, ecy - 6 * s], fill=(20, 16, 20, 255), width=int(5 * s))
        pr = 8 * s
        d.ellipse([ecx - pr, ecy - pr, ecx + pr, ecy + pr], fill=(20, 16, 20, 255))
    by = hy - 30 * s
    if mood == "angry":
        d.line([hx - 52 * s, by - 10 * s, hx - 14 * s, by + 6 * s], fill=OL, width=int(8 * s))
        d.line([hx + 14 * s, by + 6 * s, hx + 52 * s, by - 10 * s], fill=OL, width=int(8 * s))
        d.arc([hx - 24 * s, hy + 40 * s, hx + 24 * s, hy + 66 * s], 200, 340, fill=OL, width=int(6 * s))
    elif mood == "shock":
        d.ellipse([hx - 16 * s, hy + 34 * s, hx + 16 * s, hy + 70 * s], fill=(110, 30, 40, 255), outline=OL, width=int(4 * s))
    elif mood == "happy":
        d.chord([hx - 26 * s, hy + 30 * s, hx + 26 * s, hy + 66 * s], 0, 180, fill=(110, 30, 40, 255), outline=OL, width=int(4 * s))
    elif mood == "cry":
        d.chord([hx - 26 * s, hy + 30 * s, hx + 26 * s, hy + 66 * s], 0, 180, fill=(110, 30, 40, 255), outline=OL, width=int(4 * s))
        for ex in (-30, 30):
            yy = hy + 20 * s + (t * 200 % 60) * s
            d.ellipse([hx + ex * s - 7 * s, yy, hx + ex * s + 7 * s, yy + 18 * s], fill=(120, 200, 255, 230))
    else:
        d.line([hx - 18 * s, hy + 50 * s, hx + 18 * s, hy + 50 * s], fill=OL, width=int(5 * s))

# ------------------------------------------------------------ escenarios
def pyramid(d, cx, by, w, h, lit=(236, 190, 116), shade=(184, 128, 76)):
    d.polygon([(cx - w / 2, by), (cx + w * 0.08, by), (cx, by - h)], fill=lit)
    d.polygon([(cx + w * 0.08, by), (cx + w / 2, by), (cx, by - h)], fill=shade)
    for k in range(1, 9):
        yy = by - h * k / 9; half = w / 2 * (1 - k / 9)
        d.line([cx - half, yy, cx + half * 0.16, yy], fill=lerpc(lit, (0, 0, 0), 0.12) + (255,), width=2)

def desert_bg(sky_top=(255, 170, 90), sky_bot=(255, 228, 170), sun=True, pyr=True):
    img = grad(sky_top, sky_bot)
    if sun: glow(img, 980, 560, 700, (255, 240, 180), 0.8); glow(img, 980, 560, 230, (255, 250, 220), 1.0, 0.6)
    d = ImageDraw.Draw(img)
    if pyr:
        pyramid(d, 380, 1330, 760, 520); pyramid(d, 860, 1360, 560, 380, (226, 176, 104), (170, 116, 70)); pyramid(d, 1180, 1370, 300, 200)
    return img

DUNE_SPEC = [((236, 186, 112, 255), 1420, 90, 1), ((222, 168, 94, 255), 1560, 70, 2), ((206, 150, 80, 255), 1700, 50, 3)]
DUNE_PH = [np.random.default_rng(sd).uniform(0, 6, 3) for *_, sd in DUNE_SPEC]

def paste_dunes(img, offs=(0, 0, 0)):
    d = ImageDraw.Draw(img)
    for (col, base, amp, _), ph, o in zip(DUNE_SPEC, DUNE_PH, offs):
        pts = [(x, base - amp * (0.6 * math.sin((x + o) * 0.004 + ph[0]) + 0.3 * math.sin((x + o) * 0.011 + ph[1]) + 0.1 * math.sin((x + o) * 0.03 + ph[2]))) for x in range(-16, WW + 32, 16)]
        d.polygon(pts + [(WW, WH), (0, WH)], fill=col)

def temple_bg():
    img = grad((124, 82, 52), (196, 142, 92))
    d = ImageDraw.Draw(img)
    # glifos
    gr = np.random.default_rng(9)
    for row in range(5):
        y0 = 520 + row * 120
        for k in range(14):
            x0 = 80 + k * 84 + (row % 2) * 30
            c = (100, 64, 40, 255); typ = gr.integers(0, 5)
            if typ == 0: d.ellipse([x0, y0, x0 + 46, y0 + 26], outline=c, width=6); d.ellipse([x0 + 16, y0 + 6, x0 + 30, y0 + 20], fill=c)
            elif typ == 1: d.line([x0 + 22, y0 - 10, x0 + 22, y0 + 40], fill=c, width=7); d.line([x0, y0 + 10, x0 + 44, y0 + 10], fill=c, width=7)
            elif typ == 2: d.polygon([(x0, y0 + 40), (x0 + 46, y0 + 40), (x0 + 23, y0)], outline=c, width=6)
            elif typ == 3: d.arc([x0, y0, x0 + 46, y0 + 46], 180, 360, fill=c, width=7); d.line([x0 + 23, y0 + 23, x0 + 23, y0 + 46], fill=c, width=7)
            else: d.rectangle([x0 + 6, y0 + 4, x0 + 40, y0 + 38], outline=c, width=6)
    # suelo
    d.rectangle([0, 1650, WW, WH], fill=(150, 104, 66, 255))
    for k in range(-10, 20):
        d.line([WW / 2 + k * 60, 1650, WW / 2 + k * 220, WH], fill=(130, 88, 54, 255), width=4)
    for yy in (1720, 1830, 1980, 2180): d.line([0, yy, WW, yy], fill=(130, 88, 54, 255), width=4)
    # alfombra
    d.polygon([(560, 1650), (736, 1650), (900, WH), (396, WH)], fill=(170, 40, 40, 255))
    d.polygon([(590, 1650), (706, 1650), (830, WH), (466, WH)], outline=GOLD, width=8)
    # columnas
    for cx in (110, 1186):
        d.rectangle([cx - 80, 300, cx + 80, 1650], fill=(214, 168, 108, 255), outline=OL, width=6)
        for k in range(6): d.line([cx - 80, 420 + k * 210, cx + 80, 420 + k * 210], fill=(176, 130, 80, 255), width=6)
        d.polygon([(cx - 120, 300), (cx + 120, 300), (cx + 90, 380), (cx - 90, 380)], fill=(60, 140, 120, 255), outline=OL)
    return img

def torch_wall(img, x, y, t, s=1.0):
    d = ImageDraw.Draw(img)
    d.rectangle([x - 12 * s, y, x + 12 * s, y + 90 * s], fill=(90, 60, 30, 255))
    fl = 1 + 0.18 * math.sin(t * 21 + x)
    glow(img, x, y - 30 * s, int(420 * s * fl), (255, 150, 50), 0.5)
    d = ImageDraw.Draw(img)
    d.polygon([(x - 30 * s, y), (x + 30 * s, y), (x + 10 * s, y - 80 * s * fl), (x, y - 110 * s * fl), (x - 14 * s, y - 70 * s * fl)], fill=(255, 150, 40, 255))
    d.polygon([(x - 14 * s, y), (x + 14 * s, y), (x, y - 60 * s * fl)], fill=(255, 238, 150, 255))

def portal(img, x, y, size, t, alpha=1.0):
    glow(img, x, y, int(size * 1.8), (150, 80, 255), 0.6 * alpha)
    d = ImageDraw.Draw(img)
    for k in range(7):
        rr = size / 2 * (1 - k * 0.12)
        a0 = (t * (140 + k * 40) * (1 if k % 2 else -1)) % 360
        col = (90, 230, 255, int(255 * alpha)) if k % 2 else (190, 110, 255, int(255 * alpha))
        d.arc([x - rr, y - rr * 0.42, x + rr, y + rr * 0.42], a0, a0 + 250, fill=col, width=int(14 - k))
    d.ellipse([x - size * 0.12, y - size * 0.05, x + size * 0.12, y + size * 0.05], fill=(255, 255, 255, int(200 * alpha)))

def phone_big(img, cx, cy, w, h, content, t, tilt=0.0):
    lay = Image.new("RGBA", (int(w + 80), int(h + 80)), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    ox, oy = 40, 40
    d.rounded_rectangle([ox, oy, ox + w, oy + h], radius=int(w * 0.14), fill=(20, 20, 28, 255), outline=(90, 90, 110, 255), width=6)
    sx0, sy0, sx1, sy1 = ox + 22, oy + 22, ox + w - 22, oy + h - 22
    scr = Image.new("RGBA", (int(sx1 - sx0), int(sy1 - sy0)), (0, 0, 0, 255))
    content(scr, t)
    m = Image.new("L", scr.size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, scr.width - 1, scr.height - 1], radius=int(w * 0.11), fill=255)
    lay.paste(scr, (int(sx0), int(sy0)), m)
    d.rounded_rectangle([ox + w / 2 - 70, oy + 34, ox + w / 2 + 70, oy + 72], radius=19, fill=(10, 10, 14, 255))
    if tilt: lay = lay.rotate(tilt, resample=Image.BICUBIC, expand=True)
    glow(img, cx, cy, int(max(w, h) * 1.4), (120, 190, 255), 0.25)
    img.alpha_composite(lay, (int(cx - lay.width / 2), int(cy - lay.height / 2)))

def status_bar(d, w, txt="Sin servicio", batt=0.84, col=WHITE):
    f = font(F_BOLD, 34)
    d.text((60, 30), "9:41", font=f, fill=col)
    bx = w - 120
    f3 = font(F_BOLD, 30); d.text((bx - 20 - f3.getlength(txt), 33), txt, font=f3, fill=col)
    d.rounded_rectangle([bx, 36, bx + 70, 70], radius=8, outline=col, width=4)
    bc = (60, 220, 100) if batt > 0.2 else (255, 60, 60)
    d.rounded_rectangle([bx + 6, 42, bx + 6 + 58 * batt, 64], radius=4, fill=bc)

# ------------------------------------------------------------ guion por planos
SHOTS = []
def shot(dur):
    def deco(fn): SHOTS.append((fn, dur)); return fn
    return deco

BG = {}
def cached(k, f):
    if k not in BG: BG[k] = f()
    return BG[k].copy()

@shot(2.4)
def s1(t):  # cae del portal al desierto
    img = cached("des", desert_bg)
    paste_dunes(img, (t * 30, t * 50, t * 80))
    portal(img, 648, 520, 520, t)
    fall = ease(t / 1.1)
    y = lerp(500, 1700, fall)
    land = t > 1.1
    sq = 1 + (0.12 * math.exp(-(t - 1.1) * 10) if land else 0)
    nico(img, 648, y, 1.25 * (1 if land else 0.9), "shock" if not land else "happy", arms="up" if not land else "phone", phase=t * 8, phone=land)
    if land and t < 1.6:
        d = ImageDraw.Draw(img)
        for k in range(14):
            a = k / 14 * math.pi; rr = 120 + (t - 1.1) * 900
            d.ellipse([648 + math.cos(a) * rr - 18, 1700 - math.sin(a) * rr * 0.3 - 18, 648 + math.cos(a) * rr + 18, 1700 - math.sin(a) * rr * 0.3 + 18], fill=(230, 190, 130, int(255 * (1.6 - t) * 2)))
    z = 1.0 + 0.12 * ease(t / 2.4)
    shake = 22 * math.exp(-(t - 1.1) * 8) if land else 0
    return img, (648, lerp(900, 1300, ease(t / 1.4)), z, shake)

def scr_nosignal(scr, t):
    w, h = scr.size
    arr = grad((40, 60, 140), (150, 70, 160), w, h); scr.paste(arr)
    d = ImageDraw.Draw(scr)
    status_bar(d, w, "Sin servicio", 0.84)
    cx, cy = w / 2, h * 0.42
    for k in range(4):
        hh = 50 + k * 40
        d.rounded_rectangle([cx - 120 + k * 64, cy + 90 - hh, cx - 80 + k * 64, cy + 90], radius=8, fill=(255, 255, 255, 70))
    if int(t * 4) % 2 == 0:
        d.line([cx - 160, cy - 110, cx + 160, cy + 130], fill=(255, 70, 70), width=22)
    f = font(F_BLACK, 74); tx = "0 barras"; d.text((cx - f.getlength(tx) / 2, cy + 180), tx, font=f, fill=WHITE)
    f2 = font(F_BOLD, 40); tx = "Año: 2560 a. C."; d.text((cx - f2.getlength(tx) / 2, cy + 290), tx, font=f2, fill=(255, 220, 120))

@shot(2.0)
def s2(t):  # celular sin señal
    img = cached("des_blur", lambda: desert_bg().filter(ImageFilter.GaussianBlur(18)))
    phone_big(img, 648, 1000, 580, 1120, scr_nosignal, t, tilt=6 * math.sin(t * 2))
    return img, (648, 1150, 1.05 + 0.1 * ease(t / 2), 0)

def crowd(img, t, n_pose="stand", mood="shock", spread=1.0, ybase=1780, s=0.95, item=None, tint=None):
    xs = [180, 420, 876, 1116]
    for i, x in enumerate(xs):
        egipcio(img, x + math.sin(t * 2 + i) * 6, ybase + (i % 2) * 40, s, "worker", n_pose, item, t + i, mood, tint)

@shot(2.2)
def s3(t):  # la gente se acerca
    img = cached("des", desert_bg)
    paste_dunes(img, (0, 0, 0))
    k = ease(t / 1.6)
    xs = [lerp(-200, 220, k), lerp(-60, 420, k), lerp(1500, 876, k), lerp(1400, 1100, k)]
    nico(img, 648, 1640, 1.0, "worried", look=(math.sin(t * 5), 0), arms="phone", phone=True)
    for i, x in enumerate(xs):
        egipcio(img, x, 1800 + (i % 2) * 40, 0.95, "worker", "stand", "spear" if i in (0, 3) else None, t + i, "shock")
    if t > 1.2:
        d = ImageDraw.Draw(img); f = font(F_BLACK, 120)
        for i, x in enumerate(xs):
            if i in (1, 2): d.text((x - 20, 1180 - 60 * eob((t - 1.2) / 0.3)), "!", font=f, fill=(255, 60, 60), stroke_width=8, stroke_fill=(0, 0, 0))
    return img, (648, 1450, 1.0 + 0.1 * ease(t / 2.2), 0)

def beam(img, x0, y0, ang, length, width, alpha):
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for k in range(6):
        wk = width * (1 - k * 0.15)
        p1 = rot(x0 + length, y0 - wk, x0, y0, ang); p2 = rot(x0 + length, y0 + wk, x0, y0, ang)
        d.polygon([(x0, y0), p1, p2], fill=(255, 255, 220, int(40 * alpha)))
    img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(6)))

@shot(2.4)
def s4(t):  # linterna -> los adoran
    img = cached("des_dusk", lambda: desert_bg((80, 50, 110), (230, 130, 90), sun=False))
    paste_dunes(img, (0, 0, 0))
    on = t > 0.5
    for i, x in enumerate([180, 420, 876, 1116]):
        egipcio(img, x, 1800 + (i % 2) * 40, 0.95, "worker", "kneel" if t > 0.9 else "stand", None, t + i, "happy" if t > 0.9 else "shock")
    nico(img, 648, 1640, 1.05, "smug" if on else "happy", arms="phone_up", phone=True, screen=(255, 255, 230) if on else (120, 200, 255))
    if on:
        a = ease((t - 0.5) / 0.2)
        beam(img, 648 + 126, 1640 - 470, -math.pi / 2 + 0.25 * math.sin(t * 3), 1400, 260, a)
        glow(img, 648 + 126, 1640 - 470, 500, (255, 255, 220), 0.9 * a)
    return img, (648, 1350, 1.05 + 0.15 * ease(t / 2.4), 14 * math.exp(-(t - 0.5) * 10) if on else 0)

@shot(2.2)
def s5(t):  # el faraón te manda llamar
    img = cached("temple", temple_bg)
    for x in (300, 996): torch_wall(img, x, 900, t)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([458, 1080, 838, 1720], radius=40, fill=GOLD, outline=OL, width=8)
    d.rounded_rectangle([500, 1130, 796, 1500], radius=30, fill=(200, 60, 50, 255), outline=OL, width=6)
    egipcio(img, 648, 1700, 1.15, "pharaoh", "point" if t > 0.8 else "throne", None, t, "neutral")
    k = ease(t / 2.2)
    nico(img, lerp(300, 420, k), 2150, 0.85, "worried", look=(1, -1), arms="phone", phone=True, phase=t * 9)
    return img, (648, lerp(1500, 1350, k), lerp(1.0, 1.18, k), 0)

def scr_selfie(scr, t):
    w, h = scr.size
    scr.paste(cached("temple_s", lambda: temple_bg().resize((w, int(w * WH / WW))).crop((0, 0, w, h))))
    f = font(F_BOLD, 40); d = ImageDraw.Draw(scr)
    big = Image.new("RGBA", (WW, WH), (0, 0, 0, 0))
    egipcio(big, 648, 1500, 1.6, "pharaoh", "stand", None, t, "shock" if t > 0.7 else "neutral")
    big = big.crop((148, 200, 1148, 1400)).resize((w, int(w * 1.2)))
    scr.alpha_composite(big, (0, int(h * 0.18)))
    d.ellipse([w / 2 - 60, h - 190, w / 2 + 60, h - 70], outline=WHITE, width=10)
    d.text((w / 2 - f.getlength("FOTO") / 2, 40), "FOTO", font=f, fill=(255, 214, 10))

@shot(2.2)
def s6(t):  # selfie y shock
    img = cached("temple_blur", lambda: temple_bg().filter(ImageFilter.GaussianBlur(14)))
    phone_big(img, 648, 1150, 660, 1260, scr_selfie, t, tilt=-5)
    if 0.7 < t < 1.1:
        a = 1 - (t - 0.7) / 0.4
        img.alpha_composite(Image.new("RGBA", img.size, (255, 255, 255, int(255 * a))))
    return img, (648, 1150, 1.08 + 0.08 * ease(t / 2.2), 18 * math.exp(-(t - 0.7) * 9) if t > 0.7 else 0)

def scr_pyramids_today(scr, t):
    w, h = scr.size
    scr.paste(grad((110, 180, 240), (240, 230, 210), w, h))
    d = ImageDraw.Draw(scr)
    pyramid(d, w * 0.38, h * 0.62, w * 0.75, h * 0.32, (214, 180, 130), (160, 124, 84))
    pyramid(d, w * 0.78, h * 0.64, w * 0.45, h * 0.2, (204, 170, 120), (150, 114, 76))
    d.rectangle([0, h * 0.62, w, h], fill=(214, 186, 140))
    rr = np.random.default_rng(4)
    for k in range(18):  # turistas
        x = rr.uniform(20, w - 20); y = rr.uniform(h * 0.66, h * 0.9); c = tuple(int(v) for v in rr.integers(40, 250, 3))
        d.ellipse([x - 8, y - 34, x + 8, y - 18], fill=(230, 180, 140)); d.rectangle([x - 9, y - 18, x + 9, y + 8], fill=c)
    f = font(F_BLACK, 52); tx = "HOY"; d.rounded_rectangle([40, 110, 80 + f.getlength(tx), 190], radius=16, fill=(255, 40, 60))
    d.text((60, 118), tx, font=f, fill=WHITE)
    status_bar(d, w, "Wi-Fi", 0.62, col=(30, 30, 40))

@shot(2.6)
def s7(t):  # pirámides siguen en pie
    img = cached("temple", temple_bg)
    for x in (300, 996): torch_wall(img, x, 900, t)
    egipcio(img, 330, 1960, 1.05, "pharaoh", "stand", None, t, "cry" if t > 0.9 else "shock")
    d = ImageDraw.Draw(img)
    phone_big(img, 860, 1260, 520, 1000, scr_pyramids_today, t, tilt=-8)
    if t > 1.0:
        f = font(F_BLACK, 110); tx = "+4.500 años"; k = eob((t - 1.0) / 0.3)
        lay = Image.new("RGBA", (900, 200), (0, 0, 0, 0)); ImageDraw.Draw(lay).text((20, 20), tx, font=f, fill=YEL, stroke_width=10, stroke_fill=(0, 0, 0))
        lay = lay.resize((max(1, int(900 * k)), max(1, int(200 * k))))
        img.alpha_composite(lay, (int(648 - lay.width / 2), int(560 - lay.height / 2)))
    return img, (648, 1300, 1.02 + 0.1 * ease(t / 2.6), 0)

COINS = [(R.uniform(0, WW), R.uniform(-2400, 0), R.uniform(0.7, 1.3), R.uniform(0, 6)) for _ in range(70)]
@shot(2.4)
def s8(t):  # el más rico
    img = cached("temple", temple_bg)
    for x in (300, 996): torch_wall(img, x, 900, t)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([458, 1080, 838, 1720], radius=40, fill=GOLD, outline=OL, width=8)
    d.rounded_rectangle([500, 1130, 796, 1500], radius=30, fill=(200, 60, 50, 255), outline=OL, width=6)
    nico(img, 648, 1720, 1.05, "smug", arms="up", phase=t * 5, phone=False)
    d = ImageDraw.Draw(img)  # corona de oro
    d.polygon([(560, 1210), (736, 1210), (760, 1110), (700, 1160), (648, 1080), (596, 1160), (536, 1110)], fill=GOLD, outline=OL)
    for x, y0, s, ph in COINS:
        y = y0 + t * 1400 * s
        if -60 < y < WH:
            cw = abs(math.cos(t * 6 + ph)) * 34 * s + 4
            d.ellipse([x - cw, y - 34 * s, x + cw, y + 34 * s], fill=(255, 200, 40, 255), outline=(150, 100, 10, 255), width=4)
    egipcio(img, 200, 2050, 0.9, "worker", "kneel", None, t, "happy")
    egipcio(img, 1096, 2050, 0.9, "worker", "kneel", None, t + 1, "happy")
    return img, (648, 1450, 1.05 + 0.12 * ease(t / 2.4), 0)

def scr_battery(scr, t):
    w, h = scr.size
    blink = int(t * 5) % 2 == 0
    scr.paste(grad((60, 10, 20), (20, 0, 10), w, h))
    d = ImageDraw.Draw(scr)
    pct = int(lerp(20, 1, ease(t / 1.6)))
    status_bar(d, w, "Sin servicio", pct / 100)
    cx, cy = w / 2, h * 0.45
    d.rounded_rectangle([cx - 150, cy - 260, cx + 150, cy + 260], radius=40, outline=WHITE, width=14)
    d.rounded_rectangle([cx - 50, cy - 300, cx + 50, cy - 260], radius=10, fill=WHITE)
    fh = 480 * pct / 100
    d.rounded_rectangle([cx - 126, cy + 236 - fh, cx + 126, cy + 236], radius=24, fill=(255, 50, 50) if blink else (200, 30, 30))
    f = font(F_BLACK, 130); tx = f"{pct}%"; d.text((cx - f.getlength(tx) / 2, cy + 300), tx, font=f, fill=(255, 70, 70) if blink else WHITE)
    f2 = font(F_BOLD, 40); tx = "Batería baja"; d.text((cx - f2.getlength(tx) / 2, cy + 460), tx, font=f2, fill=WHITE)

@shot(2.0)
def s9(t):
    img = cached("temple_blur", lambda: temple_bg().filter(ImageFilter.GaussianBlur(14)))
    img.alpha_composite(Image.new("RGBA", img.size, (255, 0, 0, int(60 + 40 * math.sin(t * 20)))))
    phone_big(img, 648, 980, 560, 1090, scr_battery, t, tilt=3 * math.sin(t * 30))
    return img, (648, 1150, 1.0 + 0.2 * ease(t / 2.0), 8)

@shot(2.2)
def s10(t):  # no hay enchufes
    img = cached("wall", lambda: temple_bg().crop((0, 300, WW, 300 + WH)).resize((WW, WH)))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 1650, WW, WH], fill=(150, 104, 66, 255))
    x = 648 + 260 * math.sin(t * 3.2)
    nico(img, x, 1840, 1.15, "scared", look=(math.copysign(1, math.cos(t * 3.2)), 0), arms="phone", phone=True, screen=(255, 60, 60), flip=1 if math.cos(t * 3.2) > 0 else -1)
    f = font(F_BLACK, 200)
    k = eob((t - 0.6) / 0.3)
    if t > 0.6:
        lay = Image.new("RGBA", (300, 300), (0, 0, 0, 0)); dd = ImageDraw.Draw(lay)
        dd.ellipse([20, 20, 280, 280], outline=(255, 60, 60), width=26); dd.line([60, 240, 240, 60], fill=(255, 60, 60), width=26)
        dd.rounded_rectangle([110, 90, 190, 210], radius=20, outline=WHITE, width=14); dd.line([130, 60, 130, 92], fill=WHITE, width=12); dd.line([170, 60, 170, 92], fill=WHITE, width=12)
        lay = lay.resize((max(1, int(300 * k)), max(1, int(300 * k))))
        img.alpha_composite(lay, (int(648 - lay.width / 2), int(820 - lay.height / 2)))
    return img, (648, 1500, 1.12, 0)

def scr_dead(scr, t):
    w, h = scr.size
    if t < 0.35:
        scr.paste(grad((60, 10, 20), (20, 0, 10), w, h))
        d = ImageDraw.Draw(scr); f = font(F_BLACK, 130); d.text((w / 2 - f.getlength("1%") / 2, h * 0.4), "1%", font=f, fill=(255, 60, 60))
        k = t / 0.35
        d.rectangle([0, 0, w, h * k * 0.5], fill=(0, 0, 0)); d.rectangle([0, h - h * k * 0.5, w, h], fill=(0, 0, 0))
    else:
        scr.paste((0, 0, 0, 255), (0, 0, w, h))

@shot(2.4)
def s11(t):  # muere y ya no eres dios
    img = cached("des_night", lambda: desert_bg((20, 10, 40), (120, 40, 50), sun=False))
    paste_dunes(img, (0, 0, 0))
    nico(img, 648, 1640, 1.0, "scared", arms="phone", phone=True, screen=(0, 0, 0))
    for i, x in enumerate([160, 400, 896, 1136]):
        egipcio(img, x + math.sin(t * 8 + i) * 8, 1820 + (i % 2) * 40, 0.95, "worker", "angry", "torch" if i % 2 == 0 else "spear", t + i, "angry")
    img.alpha_composite(Image.new("RGBA", img.size, (255, 30, 0, 40)))
    if t < 0.9:
        phone_big(img, 648, 1000, 420, 800, scr_dead, t, tilt=-4)
    return img, (648, 1400, 1.0 + 0.12 * ease(t / 2.4), 6 if t > 0.9 else 0)

@shot(2.4)
def s12(t):  # ¡CORRE!
    img = cached("des", desert_bg)
    off = t * 1600
    paste_dunes(img, (off * 0.3, off * 0.6, off))
    d = ImageDraw.Draw(img)
    for k in range(18):
        y = 400 + (k * 137) % 1500; x = (WW - (off * 2 + k * 300) % (WW + 600))
        d.line([x, y, x + 260, y], fill=(255, 255, 255, 120), width=6)
    nico(img, 780, 1760, 1.05, "scared", look=(-1, 0), arms="run", phase=t * 22, phone=False, lean=0.4)
    for i in range(3):
        egipcio(img, 330 - i * 190 + math.sin(t * 20 + i) * 10, 1860, 0.85, "worker", "angry", "spear" if i != 1 else "torch", t + i, "angry")
    return img, (620, 1450, 1.08, 10)

@shot(3.0)
def s13(t):  # salta al portal → loop
    img = cached("des", desert_bg)
    paste_dunes(img, (0, 0, 0))
    portal(img, 648, 1200, 640, t, ease(t / 0.4))
    k = ease((t - 0.3) / 0.9)
    if k < 1:
        nico(img, lerp(200, 648, k), lerp(1760, 1200, k) - math.sin(k * math.pi) * 400, 1.0 * (1 - 0.8 * k), "shock", arms="up", phase=t * 10)
    zoom = 1.0 + 0.6 * ease((t - 1.2) / 1.8)
    return img, (648, 1200, zoom, 0)

# ---------------- voz: cada plano dura lo que su frase (+ respiro) y los subtítulos siguen la voz
from scipy.io import wavfile as _wf
VOZ = []
for k in range(1, len(SHOTS) + 1):
    sr_, a_ = _wf.read(f"voz/v{k:02d}_f.wav"); VOZ.append(a_.astype(np.float32) / 32768.0)
VSR = 44100
LEAD = 0.12
CHUNKS = [
    [("¿Qué pasaría si", []), ("llevas tu CELULAR", ["CELULAR"]), ("al Antiguo Egipto?", ["Egipto?"])],
    [("Primero:", []), ("CERO señal", ["CERO"]), ("Ni una sola barra", ["barra"])],
    [("Pero la gente", []), ("empieza a acercarse…", ["acercarse…"])],
    [("Prendes la linterna…", ["linterna…"]), ("y te ADORAN", ["ADORAN"]), ("como a un dios", ["dios"])],
    [("El faraón", ["faraón"]), ("te manda llamar", [])],
    [("Le tomas una selfie…", ["selfie…"]), ("y queda en shock", ["shock"])],
    [("Le muestras", []), ("que sus pirámides", ["pirámides"]), ("siguen en pie", ["pie"]), ("+4.000 años después", ["+4.000"])],
    [("Te vuelves", []), ("el hombre más RICO", ["RICO"]), ("de Egipto", [])],
    [("Pero hay un problema…", ["problema…"]), ("la batería", ["batería"])],
    [("No hay enchufes", ["enchufes"]), ("La electricidad", []), ("no existirá", []), ("en MILES de años", ["MILES"])],
    [("El celular se apaga…", ["apaga…"]), ("y ya no eres", []), ("un DIOS", ["DIOS"])],
    [("¡CORRE!", ["¡CORRE!"])],
    [("¿Y tú qué llevarías?", ["llevarías?"]), ("Coméntalo", ["Coméntalo"])],
]
BASE = [d for _, d in SHOTS]
DURS = [max(b_, len(v) / VSR + LEAD + 0.28) for b_, v in zip(BASE, VOZ)]
STARTS = np.cumsum([0] + DURS).tolist()
TOTAL = STARTS[-1]

def speech_segments(v, n):
    """Divide la frase en n trozos usando las pausas reales de la voz; si no cuadra, reparte por letras."""
    win = int(0.02 * VSR); env = np.sqrt(np.convolve(v ** 2, np.ones(win) / win, mode="same"))
    quiet = env < max(0.01, env.max() * 0.06)
    gaps = []; i = 0; L = len(v)
    while i < L:
        if quiet[i]:
            j = i
            while j < L and quiet[j]: j += 1
            if (j - i) / VSR > 0.09 and i > 0 and j < L: gaps.append(((i + j) / 2 / VSR, (j - i) / VSR))
            i = j
        else: i += 1
    return gaps

CAPS = []
for k, (chunks, v) in enumerate(zip(CHUNKS, VOZ)):
    dur_v = len(v) / VSR; s0 = STARTS[k] + LEAD; n = len(chunks)
    gaps = sorted(speech_segments(v, n), key=lambda g: -g[1])[:n - 1]
    lens = np.array([len(c[0]) for c in chunks], float); prop = np.cumsum(lens) / lens.sum()
    bounds = []
    for m in range(n - 1):
        target = prop[m] * dur_v
        if gaps:
            g = min(gaps, key=lambda g: abs(g[0] - target))
            bounds.append(g[0] if abs(g[0] - target) < 0.45 else target)
        else: bounds.append(target)
    bounds = sorted(bounds)
    edges = [0.0] + bounds + [None]
    for m, (txt, hl) in enumerate(chunks):
        st = s0 + edges[m] if m > 0 else STARTS[k]
        en = s0 + edges[m + 1] if m < n - 1 else STARTS[k + 1]
        CAPS.append((st, en, txt, hl))

def text_layer(words, size, hl, stroke=10):
    f = font(F_BLACK, size); sp = f.getlength(" ")
    ws = [f.getlength(w) for w in words]; tot = sum(ws) + sp * (len(words) - 1)
    pad = stroke * 2 + 10; a, de = f.getmetrics()
    lay = Image.new("RGBA", (int(tot + pad * 2), a + de + pad * 2), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); x = pad
    for w, wd in zip(words, ws):
        d.text((x + 4, pad + 6), w, font=f, fill=(0, 0, 0, 160), stroke_width=stroke, stroke_fill=(0, 0, 0, 160))
        d.text((x, pad), w, font=f, fill=YEL if w in hl else WHITE, stroke_width=stroke, stroke_fill=(0, 0, 0))
        x += wd + sp
    return lay

def caption(img, T):
    for s, e, txt, hl in CAPS:
        if s <= T < e:
            words = txt.split(); size = 118
            while True:
                lay = text_layer(words, size, hl)
                if lay.width <= W - 50 or size < 60: break
                size -= 6
            k = 0.6 + 0.4 * eob((T - s) / 0.14)
            rot_ = 3 * (1 - eob((T - s) / 0.2))
            lay = lay.resize((max(1, int(lay.width * k)), max(1, int(lay.height * k))), Image.LANCZOS).rotate(rot_, resample=Image.BICUBIC, expand=True)
            img.alpha_composite(lay, (int(W / 2 - lay.width / 2), int(1330 - lay.height / 2)))
            return

def camera(world, cx, cy, z, shake, T):
    if shake: cx += shake * math.sin(T * 61); cy += shake * math.cos(T * 47)
    vw, vh = WW / z, WH / z
    x0 = clamp(cx - vw / 2, 0, WW - vw); y0 = clamp(cy - vh / 2, 0, WH - vh)
    return world.resize((W, H), Image.BILINEAR, box=(x0, y0, x0 + vw, y0 + vh))

def vignette():
    c = (np.arange(H) - H / 2) / (H / 2); r_ = (np.arange(W) - W / 2) / (W / 2)
    X, Y = np.meshgrid(r_, c); rr = np.sqrt(X ** 2 * 0.8 + Y ** 2)
    a = np.clip((rr - 0.75) / 0.6, 0, 1) ** 1.5 * 150
    arr = np.zeros((H, W, 4), np.uint8); arr[..., 3] = a.astype(np.uint8)
    return Image.fromarray(arr, "RGBA")
VIG = vignette()

def frame(T):
    i = max(j for j in range(len(SHOTS)) if STARTS[j] <= T) if T < TOTAL else len(SHOTS) - 1
    fn, base = SHOTS[i]; t = T - STARTS[i]
    world, (cx, cy, z, sh) = fn(t * base / DURS[i])
    # punch-in en cada cambio de plano
    z *= 1 + 0.07 * (1 - ease(t / 0.25))
    img = camera(world, cx, cy, z, sh, T)
    img.alpha_composite(VIG)
    caption(img, T)
    if i > 0 and t < 0.12:
        img.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(110 * (1 - t / 0.12)))))
    return img.convert("RGB")

# ------------------------------------------------------------ audio
def make_audio(path):
    from scipy.signal import butter, sosfilt
    from scipy.io import wavfile
    sr = 44100; n = int(TOTAL * sr); tt = np.arange(n) / sr; out = np.zeros(n)
    def hz(m): return 440 * 2 ** ((m - 69) / 12)
    def add(s, sig):
        i0 = int(s * sr); i1 = min(n, i0 + len(sig))
        if i0 < n: out[i0:i1] += sig[:i1 - i0]
    bpm = 118; b = 60 / bpm
    # escala Hijaz en Re: D Eb F# G A Bb C
    scale = [62, 63, 66, 67, 69, 70, 72, 74]
    mel = [0, 2, 3, 4, 3, 2, 1, 0, 4, 5, 4, 3, 2, 3, 1, 0]
    beats = int(TOTAL / b)
    for k in range(beats):
        s = k * b
        if 22.6 <= s < 22.6 + 2.4 * 0: continue
        # bombo
        seg = np.arange(int(0.22 * sr)) / sr
        add(s, 0.5 * np.exp(-seg * 16) * np.sin(2 * np.pi * (48 + 110 * np.exp(-seg * 35)) * seg))
        # hi-hat (contratiempo)
        hs = np.random.default_rng(k).standard_normal(int(0.05 * sr)) * np.exp(-np.arange(int(0.05 * sr)) / sr * 90)
        add(s + b / 2, 0.06 * hs)
        # bajo
        root = 38 if (k // 8) % 2 == 0 else 36
        seg = np.arange(int(b * 0.9 * sr)) / sr
        add(s, 0.16 * np.exp(-seg * 4) * np.sign(np.sin(2 * np.pi * hz(root) * seg)) * 0.5)
        # melodía pluck (corcheas)
        for half in (0, 1):
            m = scale[mel[(k * 2 + half) % 16]] + (12 if (k // 16) % 2 else 0)
            seg = np.arange(int(0.3 * sr)) / sr
            env = np.exp(-seg * 10)
            add(s + half * b / 2, 0.05 * env * (np.sin(2 * np.pi * hz(m) * seg) + 0.5 * np.sin(4 * np.pi * hz(m) * seg) * np.exp(-seg * 20)))
    noise = np.random.default_rng(1).standard_normal(n)
    sos = butter(2, [500, 4000], btype="band", fs=sr, output="sos"); wn = sosfilt(sos, noise)
    for s in STARTS[1:-1]:  # whoosh
        i0 = max(0, int((s - 0.2) * sr)); i1 = min(n, int((s + 0.2) * sr)); seg = tt[i0:i1] - (s - 0.2)
        out[i0:i1] += 0.5 * np.sin(np.pi * seg / 0.4) ** 2 * wn[i0:i1]
    for s, *_ in CAPS:  # pop
        seg = np.arange(int(0.04 * sr)) / sr; add(s, 0.07 * np.exp(-seg * 90) * np.sin(2 * np.pi * 1400 * seg))
    def at(k, x): return STARTS[k] + x * DURS[k] / BASE[k]
    def boom(s, v=0.8):
        seg = np.arange(int(0.9 * sr)) / sr; add(s, v * np.exp(-seg * 5) * np.sin(2 * np.pi * (40 + 70 * np.exp(-seg * 8)) * seg))
    boom(at(0, 1.1))                                    # aterrizaje
    seg = np.arange(int(1.1 * sr)) / sr                      # caída (silbido descendente)
    add(0.0, 0.12 * np.sin(2 * np.pi * (1600 - 1200 * seg / 1.1) * seg) * np.clip(1 - seg / 1.1, 0, 1))
    seg = np.arange(int(0.5 * sr)) / sr                      # "ding" linterna
    add(at(3, 0.5), 0.25 * np.exp(-seg * 6) * (np.sin(2 * np.pi * 1760 * seg) + np.sin(2 * np.pi * 2637 * seg)))
    sh = np.random.default_rng(7).standard_normal(int(0.12 * sr)) * np.exp(-np.arange(int(0.12 * sr)) / sr * 40)
    add(at(5, 0.7), 0.5 * sh); boom(at(5, 0.7), 0.4)  # click de cámara
    for k in range(40):                                      # monedas
        f = 2000 + (k * 373) % 1800; seg = np.arange(int(0.12 * sr)) / sr
        add(at(7, 0.1 + k * 0.055), 0.05 * np.exp(-seg * 30) * np.sin(2 * np.pi * f * seg))
    for k in range(5):                                       # alarma batería
        seg = np.arange(int(0.18 * sr)) / sr; add(STARTS[8] + k * 0.38, 0.12 * np.sign(np.sin(2 * np.pi * 880 * seg)) * 0.5)
    seg = np.arange(int(0.8 * sr)) / sr                      # apagado
    add(at(10, 0.1), 0.2 * np.sin(2 * np.pi * (600 * np.exp(-seg * 3)) * seg) * np.exp(-seg * 2))
    boom(at(10, 0.9), 0.6)
    i0 = int(STARTS[10] * sr); i1 = int(STARTS[12] * sr)    # multitud enojada
    sos2 = butter(2, [150, 700], btype="band", fs=sr, output="sos")
    out[i0:i1] += 0.25 * sosfilt(sos2, noise[i0:i1]) * (1 + 0.5 * np.sin(tt[i0:i1] * 7))
    for k in range(16):                                      # pasos corriendo
        seg = np.arange(int(0.06 * sr)) / sr; add(STARTS[11] + k * 0.15, 0.25 * np.exp(-seg * 60) * np.sin(2 * np.pi * 120 * seg))
    seg = np.arange(int(2.0 * sr)) / sr                      # portal
    add(STARTS[12], 0.12 * np.sin(2 * np.pi * (200 + 600 * seg / 2) * seg + 3 * np.sin(2 * np.pi * 6 * seg)) * np.clip(seg / 0.3, 0, 1))
    out = np.tanh(out * 1.3); out = out / np.max(np.abs(out)) * 0.35
    voice = np.zeros(n)
    for k, v in enumerate(VOZ):
        i0 = int((STARTS[k] + LEAD) * sr); i1 = min(n, i0 + len(v)); voice[i0:i1] += v[:i1 - i0]
    voice = voice / (np.max(np.abs(voice)) + 1e-9) * 0.95
    env = np.convolve(np.abs(voice), np.ones(4410) / 4410, mode="same")
    duck = 1 - 0.45 * np.clip(env / 0.05, 0, 1)
    out = out * duck + voice
    out *= np.clip((TOTAL - tt) / 0.5, 0, 1)
    out = out / np.max(np.abs(out)) * 0.95
    wavfile.write(path, sr, (out * 32767).astype(np.int16))

if __name__ == "__main__":
    if os.environ.get("PREVIEW"):
        ts = [float(x) for x in os.environ["PREVIEW"].split(",")]
        ims = [frame(T).resize((270, 480)) for T in ts]
        cols = 5; rows = (len(ims) + cols - 1) // cols
        sheet = Image.new("RGB", (270 * cols, 480 * rows))
        for k, im in enumerate(ims): sheet.paste(im, ((k % cols) * 270, (k // cols) * 480))
        sheet.save("sheet_eg.png"); sys.exit()
    make_audio("audio_eg.wav")
    nf = int(TOTAL * FPS)
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-i", "audio_eg.wav", "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p",
                          "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
    for k in range(nf):
        p.stdin.write(frame(k / FPS).tobytes())
        if k % 150 == 0: print(f"frame {k}/{nf}", flush=True)
    p.stdin.close(); p.wait(); print("listo", OUT, TOTAL)
