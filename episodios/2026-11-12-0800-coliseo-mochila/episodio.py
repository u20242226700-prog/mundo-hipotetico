#!/usr/bin/env python3
"""Short: ¿Qué pasaría si caes en el Coliseo romano con tu mochila? — 100% generado por código."""
import math, os, sys, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
WW, WH = 1296, 2304            # "mundo" (1.2x) para mover la cámara sin perder calidad
OUT = sys.argv[1] if len(sys.argv) > 1 else "coliseo.mp4"
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


# ------------------------------------------------------------ romanos
ROM = (226, 170, 128, 255); TOGA = (244, 238, 224, 255); PURP = (120, 40, 140, 255)
RED = (190, 40, 40, 255); STEEL = (176, 184, 196, 255); LEAF = (80, 160, 60, 255)
GOLD = (240, 188, 52, 255)

def laurel(d, hx, hy, r, s):
    for side in (-1, 1):
        for k in range(6):
            a = math.radians(200 + k * 24) if side < 0 else math.radians(340 - k * 24)
            px, py = hx + math.cos(a) * r * 1.02, hy + math.sin(a) * r * 0.95
            d.ellipse([px - 20 * s, py - 11 * s, px + 20 * s, py + 11 * s], fill=LEAF, outline=OL, width=max(1, int(3 * s)))

def romano(img, x, y, s=1.0, kind="citizen", pose="stand", t=0.0, mood="neutral", tunic=None):
    d = ImageDraw.Draw(img); lw = 6 * s
    shadow(d, x, y + 4 * s, 85 * s)
    for sx in (-22, 22):
        limb(d, [(x + sx * s, y - 150 * s), (x + sx * s, y - 10 * s)], 30 * s, ROM, lw)
        for k in range(3): d.line([x + sx * s - 16 * s, y - 20 * s - k * 26 * s, x + sx * s + 16 * s, y - 30 * s - k * 26 * s], fill=(110, 70, 40, 255), width=int(5 * s))
    col = tunic or {"citizen": TOGA, "gladiator": (150, 44, 40, 255), "emperor": TOGA}[kind]
    d.polygon([(x - 62 * s, y - 320 * s), (x + 62 * s, y - 320 * s), (x + 80 * s, y - 120 * s), (x - 80 * s, y - 120 * s)], fill=col, outline=OL)
    if kind == "emperor":
        d.polygon([(x - 62 * s, y - 320 * s), (x - 20 * s, y - 320 * s), (x + 80 * s, y - 150 * s), (x + 50 * s, y - 120 * s)], fill=PURP, outline=OL)
    if kind == "gladiator":
        d.rectangle([x - 70 * s, y - 210 * s, x + 70 * s, y - 180 * s], fill=(110, 70, 40, 255), outline=OL)
        d.rectangle([x - 16 * s, y - 210 * s, x + 16 * s, y - 180 * s], fill=GOLD)
    shl, shr = (x - 54 * s, y - 300 * s), (x + 54 * s, y - 300 * s)
    w_ = math.sin(t * 12)
    if pose == "cheer":
        hl, hr = (x - 120 * s, y - 440 * s + w_ * 20 * s), (x + 120 * s, y - 440 * s - w_ * 20 * s)
    elif pose == "clap":
        g = abs(math.sin(t * 9)) * 50 * s
        hl, hr = (x - 14 * s - g, y - 300 * s), (x + 14 * s + g, y - 300 * s)
    elif pose == "sword":
        hl, hr = (x - 110 * s, y - 230 * s), (x + 120 * s, y - 380 * s + w_ * 10 * s)
    elif pose == "reach":
        hl, hr = (x - 80 * s, y - 180 * s), (x - 150 * s, y - 300 * s)
    else:
        hl, hr = (x - 80 * s, y - 180 * s), (x + 80 * s, y - 180 * s)
    acol = STEEL if kind == "gladiator" else ROM
    for sh, hd in ((shl, hl), (shr, hr)):
        limb(d, [sh, hd], 28 * s, ROM, lw)
        cap(d, hd, 19 * s, OL); cap(d, hd, 15 * s, ROM)
    if kind == "gladiator":
        limb(d, [shr, hr], 28 * s, acol, lw)
        for k in range(1, 4):
            px, py = lerp(shr[0], hr[0], k / 4), lerp(shr[1], hr[1], k / 4)
            d.line([px - 16 * s, py, px + 16 * s, py], fill=(110, 116, 130, 255), width=int(4 * s))
        if pose == "sword":
            px, py = hr
            d.polygon([(px - 10 * s, py), (px + 10 * s, py), (px + 8 * s, py - 190 * s), (px, py - 220 * s), (px - 8 * s, py - 190 * s)], fill=(220, 226, 236, 255), outline=OL)
            d.rectangle([px - 34 * s, py - 6 * s, px + 34 * s, py + 10 * s], fill=GOLD, outline=OL)
        px, py = hl  # escudo
        d.rounded_rectangle([px - 70 * s, py - 120 * s, px + 70 * s, py + 110 * s], radius=int(24 * s), fill=RED, outline=OL, width=int(lw))
        d.rounded_rectangle([px - 54 * s, py - 104 * s, px + 54 * s, py + 94 * s], radius=int(18 * s), outline=GOLD, width=int(6 * s))
        d.ellipse([px - 26 * s, py - 26 * s, px + 26 * s, py + 26 * s], fill=GOLD, outline=OL, width=int(4 * s))
    hx, hy = x, y - 410 * s; r = 84 * s
    d.ellipse([hx - r, hy - r, hx + r, hy + r], fill=ROM, outline=OL, width=int(lw))
    if kind == "gladiator":
        d.chord([hx - r * 1.12, hy - r * 1.3, hx + r * 1.12, hy + r * 0.6], 180, 360, fill=STEEL, outline=OL, width=int(lw))
        d.rectangle([hx - r * 1.12, hy - r * 0.38, hx - r * 0.7, hy + r * 0.7], fill=STEEL, outline=OL)
        d.rectangle([hx + r * 0.7, hy - r * 0.38, hx + r * 1.12, hy + r * 0.7], fill=STEEL, outline=OL)
        for k in range(9):  # penacho
            a = math.radians(200 + k * 17.5)
            px, py = hx + math.cos(a) * r * 1.1, hy - r * 0.6 + math.sin(a) * r * 1.0
            d.ellipse([px - 26 * s, py - 26 * s, px + 26 * s, py + 26 * s], fill=RED, outline=OL, width=int(3 * s))
    else:
        d.chord([hx - r * 1.05, hy - r * 1.12, hx + r * 1.05, hy + r * 0.3], 180, 360, fill=(70, 46, 34, 255))
    for ex in (-30, 30):
        ecx, ecy = hx + ex * s, hy + 6 * s
        er = 18 * s if mood != "shock" else 22 * s
        d.ellipse([ecx - er, ecy - er * 1.1, ecx + er, ecy + er * 1.1], fill=(255, 255, 255, 255), outline=OL, width=int(4 * s))
        pr = 8 * s; d.ellipse([ecx - pr, ecy - pr, ecx + pr, ecy + pr], fill=OL)
    if mood == "stars":
        for ex in (-30, 30):
            cx_, cy_ = hx + ex * s, hy + 6 * s
            pts = [(cx_ + math.cos(math.radians(a)) * (24 if i % 2 == 0 else 10) * s, cy_ + math.sin(math.radians(a)) * (24 if i % 2 == 0 else 10) * s) for i, a in enumerate(range(-90, 270, 36))]
            d.polygon(pts, fill=YEL, outline=OL)
    by = hy - 28 * s
    if mood == "angry":
        d.line([hx - 50 * s, by - 10 * s, hx - 14 * s, by + 6 * s], fill=OL, width=int(8 * s))
        d.line([hx + 14 * s, by + 6 * s, hx + 50 * s, by - 10 * s], fill=OL, width=int(8 * s))
        d.arc([hx - 24 * s, hy + 42 * s, hx + 24 * s, hy + 66 * s], 200, 340, fill=OL, width=int(6 * s))
    elif mood in ("shock",):
        d.ellipse([hx - 16 * s, hy + 34 * s, hx + 16 * s, hy + 70 * s], fill=(110, 30, 40, 255), outline=OL, width=int(4 * s))
    elif mood in ("happy", "stars"):
        d.chord([hx - 28 * s, hy + 28 * s, hx + 28 * s, hy + 68 * s], 0, 180, fill=(110, 30, 40, 255), outline=OL, width=int(4 * s))
    else:
        d.line([hx - 18 * s, hy + 50 * s, hx + 18 * s, hy + 50 * s], fill=OL, width=int(5 * s))
    if kind == "emperor":
        laurel(d, hx, hy - 10 * s, r, s)

# ------------------------------------------------------------ león
MANE = (186, 96, 36, 255); FUR = (236, 178, 86, 255); MUZ = (250, 226, 180, 255)

def lion(img, x, y, s=1.0, pose="stand", t=0.0, mood="angry"):
    L = int(760 * s); Hh = int(820 * s)
    lay = Image.new("RGBA", (L, Hh), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    cx, by = L / 2, Hh - 30 * s; lw = 6 * s
    bob = abs(math.sin(t * 10)) * 30 * s if pose == "dance" else 0
    shadow(d, cx, by + 4 * s, 170 * s)
    # cola
    tw = math.sin(t * 8) * 40 * s
    limb(d, [(cx + 120 * s, by - 160 * s - bob), (cx + 230 * s, by - 230 * s + tw), (cx + 250 * s, by - 330 * s + tw)], 22 * s, FUR, lw)
    cap(d, (cx + 250 * s, by - 340 * s + tw), 30 * s, MANE)
    # patas traseras
    for sx in (-90, 90):
        limb(d, [(cx + sx * s, by - 150 * s - bob), (cx + sx * 1.1 * s, by - 20 * s)], 56 * s, FUR, lw)
        d.ellipse([cx + sx * 1.1 * s - 44 * s, by - 44 * s, cx + sx * 1.1 * s + 44 * s, by + 8 * s], fill=FUR, outline=OL, width=int(lw))
    # cuerpo
    d.ellipse([cx - 160 * s, by - 330 * s - bob, cx + 160 * s, by - 100 * s - bob], fill=FUR, outline=OL, width=int(lw))
    d.ellipse([cx - 80 * s, by - 280 * s - bob, cx + 80 * s, by - 130 * s - bob], fill=MUZ)
    # patas delanteras
    if pose == "dance":
        w = math.sin(t * 10)
        arms = [((cx - 110 * s, by - 280 * s - bob), (cx - 230 * s, by - 420 * s - bob + w * 40 * s)), ((cx + 110 * s, by - 280 * s - bob), (cx + 230 * s, by - 420 * s - bob - w * 40 * s))]
    elif pose == "pounce":
        arms = [((cx - 110 * s, by - 280 * s), (cx - 200 * s, by - 380 * s)), ((cx + 110 * s, by - 280 * s), (cx + 200 * s, by - 380 * s))]
    else:
        arms = [((cx - 90 * s, by - 260 * s), (cx - 120 * s, by - 30 * s)), ((cx + 90 * s, by - 260 * s), (cx + 120 * s, by - 30 * s))]
    for a, b in arms:
        limb(d, [a, b], 50 * s, FUR, lw)
        d.ellipse([b[0] - 40 * s, b[1] - 34 * s, b[0] + 40 * s, b[1] + 22 * s], fill=FUR, outline=OL, width=int(lw))
        if pose == "pounce":
            for k in (-1, 0, 1): d.line([b[0] + k * 18 * s, b[1] - 30 * s, b[0] + k * 22 * s, b[1] - 56 * s], fill=(255, 255, 255, 255), width=int(6 * s))
    # cabeza
    hx, hy = cx + (math.sin(t * 10) * 26 * s if pose == "dance" else 0), by - 470 * s - bob; R_ = 150 * s
    pts = []
    for k in range(28):
        a = k / 28 * math.tau; rr = R_ * (1.0 if k % 2 == 0 else 0.78)
        pts.append((hx + math.cos(a) * rr * 1.08, hy + math.sin(a) * rr))
    d.polygon(pts, fill=MANE, outline=OL)
    for ex in (-1, 1):
        d.ellipse([hx + ex * 78 * s - 26 * s, hy - 96 * s - 26 * s, hx + ex * 78 * s + 26 * s, hy - 96 * s + 26 * s], fill=FUR, outline=OL, width=int(lw))
    d.ellipse([hx - 100 * s, hy - 100 * s, hx + 100 * s, hy + 96 * s], fill=FUR, outline=OL, width=int(lw))
    d.ellipse([hx - 62 * s, hy + 6 * s, hx + 62 * s, hy + 86 * s], fill=MUZ, outline=OL, width=int(4 * s))
    d.polygon([(hx - 20 * s, hy + 6 * s), (hx + 20 * s, hy + 6 * s), (hx, hy + 30 * s)], fill=(60, 30, 30, 255))
    for ex in (-40, 40):
        ecx, ecy = hx + ex * s, hy - 30 * s
        if mood == "happy":
            d.arc([ecx - 22 * s, ecy - 14 * s, ecx + 22 * s, ecy + 18 * s], 200, 340, fill=OL, width=int(8 * s))
        else:
            d.ellipse([ecx - 20 * s, ecy - 22 * s, ecx + 20 * s, ecy + 22 * s], fill=(255, 250, 200, 255), outline=OL, width=int(4 * s))
            d.ellipse([ecx - 9 * s, ecy - 9 * s, ecx + 9 * s, ecy + 9 * s], fill=OL)
    if mood == "angry":
        d.line([hx - 70 * s, hy - 70 * s, hx - 16 * s, hy - 50 * s], fill=OL, width=int(10 * s))
        d.line([hx + 16 * s, hy - 50 * s, hx + 70 * s, hy - 70 * s], fill=OL, width=int(10 * s))
        d.chord([hx - 44 * s, hy + 30 * s, hx + 44 * s, hy + 96 * s], 0, 180, fill=(120, 30, 40, 255), outline=OL, width=int(4 * s))
        for k in (-26, 26): d.polygon([(hx + k * s - 8 * s, hy + 50 * s), (hx + k * s + 8 * s, hy + 50 * s), (hx + k * s, hy + 74 * s)], fill=(255, 255, 255, 255))
    elif mood == "happy":
        d.chord([hx - 36 * s, hy + 34 * s, hx + 36 * s, hy + 84 * s], 0, 180, fill=(120, 30, 40, 255), outline=OL, width=int(4 * s))
    else:
        d.arc([hx - 26 * s, hy + 40 * s, hx + 26 * s, hy + 66 * s], 200, 340, fill=OL, width=int(6 * s))
    tilt = math.sin(t * 10) * 9 if pose == "dance" else 0
    if tilt: lay = lay.rotate(tilt, resample=Image.BICUBIC, center=(L / 2, by))
    img.alpha_composite(lay, (int(x - L / 2), int(y - by)))

# ------------------------------------------------------------ objetos
def speaker(img, x, y, s=1.0, pulse=0.0, red=False):
    d = ImageDraw.Draw(img)
    w, h = 210 * s, 120 * s
    d.rounded_rectangle([x - w, y - h, x + w, y + h], radius=int(h), fill=(40, 44, 60, 255), outline=OL, width=int(7 * s))
    for ex in (-1, 1):
        rr = 78 * s * (1 + 0.12 * pulse)
        d.ellipse([x + ex * 110 * s - rr, y - rr, x + ex * 110 * s + rr, y + rr], fill=(24, 26, 36, 255), outline=(90, 220, 240, 255) if not red else (255, 60, 60, 255), width=int(6 * s))
        r2 = rr * 0.4; d.ellipse([x + ex * 110 * s - r2, y - r2, x + ex * 110 * s + r2, y + r2], fill=(70, 74, 96, 255))
    d.rounded_rectangle([x - 26 * s, y - h - 10 * s, x + 26 * s, y - h + 14 * s], radius=int(8 * s), fill=(90, 220, 240, 255) if not red else (255, 60, 60, 255))

def notes(img, x, y, t, n=6, spread=420, col=(255, 230, 60)):
    d = ImageDraw.Draw(img)
    for k in range(n):
        ph = (t * 0.9 + k / n) % 1.0
        px = x + math.sin(k * 2.3 + t * 2) * spread * 0.5 + (k - n / 2) * 30
        py = y - ph * 600
        a = int(255 * math.sin(ph * math.pi))
        s = 1.2 + 0.4 * (k % 2)
        c = col + (a,)
        d.ellipse([px - 22 * s, py - 16 * s, px + 22 * s, py + 16 * s], fill=c, outline=(0, 0, 0, a), width=4)
        d.line([px + 18 * s, py, px + 18 * s, py - 80 * s], fill=(0, 0, 0, a), width=int(8 * s))
        d.line([px + 18 * s, py, px + 18 * s, py - 80 * s], fill=c, width=int(4 * s))
        if k % 2: d.polygon([(px + 18 * s, py - 80 * s), (px + 50 * s, py - 60 * s), (px + 18 * s, py - 56 * s)], fill=c)

def chocolate(img, x, y, s=1.0, rot_=0):
    lay = Image.new("RGBA", (int(320 * s), int(420 * s)), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle([20 * s, 20 * s, 300 * s, 400 * s], radius=int(20 * s), fill=(110, 60, 30, 255), outline=OL, width=int(6 * s))
    for i in range(2):
        for j in range(3):
            d.rounded_rectangle([40 * s + i * 130 * s, 40 * s + j * 110 * s, 150 * s + i * 130 * s, 130 * s + j * 110 * s], radius=int(10 * s), fill=(140, 80, 40, 255))
    d.rectangle([20 * s, 260 * s, 300 * s, 400 * s], fill=(200, 40, 50, 255), outline=OL, width=int(6 * s))
    d.rectangle([20 * s, 290 * s, 300 * s, 306 * s], fill=GOLD)
    if rot_: lay = lay.rotate(rot_, resample=Image.BICUBIC, expand=True)
    img.alpha_composite(lay, (int(x - lay.width / 2), int(y - lay.height / 2)))

def portal(img, x, y, size, t, alpha=1.0):
    glow(img, x, y, int(size * 1.8), (150, 80, 255), 0.6 * alpha)
    d = ImageDraw.Draw(img)
    for k in range(7):
        rr = size / 2 * (1 - k * 0.12)
        a0 = (t * (140 + k * 40) * (1 if k % 2 else -1)) % 360
        col = (90, 230, 255, int(255 * alpha)) if k % 2 else (190, 110, 255, int(255 * alpha))
        d.arc([x - rr, y - rr * 0.42, x + rr, y + rr * 0.42], a0, a0 + 250, fill=col, width=int(14 - k))
    d.ellipse([x - size * 0.12, y - size * 0.05, x + size * 0.12, y + size * 0.05], fill=(255, 255, 255, int(200 * alpha)))

def pop_text(img, txt, x, y, k, size=120, col=YEL):
    if k <= 0: return
    f = font(F_BLACK, size)
    tw = int(f.getlength(txt)) + 60
    lay = Image.new("RGBA", (tw, size + 80), (0, 0, 0, 0)); ImageDraw.Draw(lay).text((30, 20), txt, font=f, fill=col, stroke_width=10, stroke_fill=(0, 0, 0))
    lay = lay.resize((max(1, int(lay.width * k)), max(1, int(lay.height * k))))
    img.alpha_composite(lay, (int(x - lay.width / 2), int(y - lay.height / 2)))

# ------------------------------------------------------------ Coliseo
STONE = (214, 180, 132); STONE_D = (176, 140, 98)
SAND = (232, 204, 150)

def colosseum_bg():
    img = grad((80, 150, 235), (190, 220, 250))
    glow(img, 1050, 250, 600, (255, 250, 220), 0.7)
    d = ImageDraw.Draw(img)
    # muro superior con arcos
    d.rectangle([0, 360, WW, 660], fill=STONE + (255,))
    for row, (y0, h) in enumerate(((390, 110), (520, 110))):
        for k in range(14):
            x0 = -20 + k * 96 + (row % 2) * 48
            d.rectangle([x0 + 18, y0 + 30, x0 + 78, y0 + h], fill=(120, 90, 66, 255))
            d.ellipse([x0 + 18, y0, x0 + 78, y0 + 60], fill=(120, 90, 66, 255))
            d.rectangle([x0 + 6, y0 - 6, x0 + 18, y0 + h], fill=STONE_D + (255,))
    d.line([0, 360, WW, 360], fill=OL, width=6)
    d.rectangle([0, 640, WW, 664], fill=STONE_D + (255,))
    # gradas
    for k, y0 in enumerate(range(664, 1250, 66)):
        c = lerpc(STONE, STONE_D, (k % 2) * 0.5)
        d.rectangle([0, y0, WW, y0 + 66], fill=c + (255,))
        d.line([0, y0 + 64, WW, y0 + 64], fill=(150, 116, 80, 255), width=4)
    # palco del emperador
    d.rectangle([840, 1000, 1200, 1250], fill=(160, 30, 40, 255), outline=OL, width=6)
    for k in range(8): d.polygon([(840 + k * 45, 1000), (885 + k * 45, 1000), (862 + k * 45, 1050)], fill=GOLD)
    for cx in (850, 1190): d.rectangle([cx - 14, 860, cx + 14, 1250], fill=(240, 232, 214, 255), outline=OL, width=4)
    d.rectangle([826, 846, 1214, 876], fill=(240, 232, 214, 255), outline=OL, width=4)
    # podio (muro de la arena)
    d.rectangle([0, 1250, WW, 1400], fill=(236, 226, 206, 255))
    d.rectangle([0, 1300, WW, 1330], fill=(160, 30, 40, 255))
    d.line([0, 1250, WW, 1250], fill=OL, width=6); d.line([0, 1400, WW, 1400], fill=OL, width=6)
    # puerta
    d.rectangle([520, 1270, 776, 1400], fill=(30, 22, 26, 255), outline=OL, width=6)
    d.chord([520, 1200, 776, 1340], 180, 360, fill=(30, 22, 26, 255), outline=OL, width=6)
    # arena
    d.rectangle([0, 1400, WW, WH], fill=SAND + (255,))
    rr = np.random.default_rng(5)
    for _ in range(260):
        x = rr.uniform(0, WW); y = rr.uniform(1420, WH); w = rr.uniform(10, 40)
        d.line([x, y, x + w, y], fill=(214, 184, 128, 255), width=3)
    return img

CROWD = []
_cr = np.random.default_rng(11)
for y0 in range(700, 1250, 66):
    for k in range(30):
        x = -10 + k * 46 + _cr.uniform(-8, 8)
        if 820 < x < 1220 and y0 > 960: continue
        CROWD.append((x, y0 + 40, tuple(int(v) for v in _cr.integers(60, 250, 3)), _cr.uniform(0, 6), tuple(int(v) for v in ROM[:3] * np.array(_cr.uniform(0.75, 1.05)))))

def crowd(img, t, excite=0.3):
    d = ImageDraw.Draw(img)
    for x, y, c, ph, sk in CROWD:
        b = abs(math.sin(t * (4 + 8 * excite) + ph)) * 10 * excite
        yy = y - b
        if excite > 0.6:
            d.line([x - 12, yy - 6, x - 20, yy - 36], fill=sk, width=6); d.line([x + 12, yy - 6, x + 20, yy - 36], fill=sk, width=6)
        d.rectangle([x - 15, yy, x + 15, yy + 26], fill=c)
        d.ellipse([x - 12, yy - 24, x + 12, yy], fill=sk)

def gate(img, lift):
    d = ImageDraw.Draw(img)
    for k in range(7):
        x = 536 + k * 38
        d.line([x, 1210 - lift, x, 1400 - lift], fill=(70, 66, 70, 255), width=12)
    for y in range(1240, 1400, 50):
        d.line([524, y - lift, 772, y - lift], fill=(70, 66, 70, 255), width=10)

def emperor_box(img, t, pose="stand", mood="neutral", s=0.6):
    romano(img, 1020, 1240, s, "emperor", pose, t, mood)
    d = ImageDraw.Draw(img); d.rectangle([840, 1170, 1200, 1250], fill=(160, 30, 40, 255), outline=OL, width=6)
    for k in range(8): d.polygon([(840 + k * 45, 1170), (885 + k * 45, 1170), (862 + k * 45, 1215)], fill=GOLD)

# ------------------------------------------------------------ guion por planos
SHOTS = []
def shot(dur):
    def deco(fn): SHOTS.append((fn, dur)); return fn
    return deco

BG = {}
def cached(k, f):
    if k not in BG: BG[k] = f()
    return BG[k].copy()

@shot(3.0)
def s1(t):  # cae del portal al Coliseo
    img = cached("col", colosseum_bg)
    crowd(img, t, 0.3)
    emperor_box(img, t)
    portal(img, 648, 760, 520, t)
    fall = ease(t / 1.1); y = lerp(760, 2150, fall); land = t > 1.1
    nico(img, 648, y, 1.3 * (1 if land else 0.85), "shock" if not land else "worried", look=(math.sin(t * 4), 0), arms="up" if not land else "down", phase=t * 8)
    if land and t < 1.7:
        d = ImageDraw.Draw(img)
        for k in range(14):
            a = k / 14 * math.pi; rr = 120 + (t - 1.1) * 900
            d.ellipse([648 + math.cos(a) * rr - 18, 2150 - math.sin(a) * rr * 0.3 - 18, 648 + math.cos(a) * rr + 18, 2150 - math.sin(a) * rr * 0.3 + 18], fill=(230, 200, 140, int(255 * (1.7 - t) * 1.6)))
    z = 1.0 + 0.12 * ease(t / 3.0)
    shake = 22 * math.exp(-(t - 1.1) * 8) if land else 0
    return img, (648, lerp(1000, 1600, ease(t / 1.4)), z, shake)

COMMENT = ["Wow, jajaja sería genial,", "el próximo video", "hazlo de Roma"]
def comment_card(img, x, y, k, t):
    if k <= 0: return
    w, h = 900, 380
    lay = Image.new("RGBA", (w + 40, h + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle([24, 28, w + 24, h + 28], radius=40, fill=(0, 0, 0, 90))
    d.rounded_rectangle([14, 14, w + 14, h + 14], radius=40, fill=(255, 255, 255, 255), outline=OL, width=6)
    d.ellipse([50, 50, 150, 150], fill=(255, 120, 60, 255)); d.ellipse([80, 66, 120, 106], fill=(255, 220, 190, 255)); d.chord([62, 100, 138, 170], 180, 360, fill=(255, 220, 190, 255))
    d.text((176, 56), "Comentario en TikTok", font=font(F_BOLD, 38), fill=(130, 130, 140))
    for i, ln in enumerate(COMMENT):
        d.text((176, 120 + i * 64), ln, font=font(F_BLACK, 52), fill=(20, 20, 30) if i < 2 else (230, 40, 70))
    hb = 1 + 0.25 * abs(math.sin(t * 6))
    hx_, hy_ = w - 50, 90
    d.ellipse([hx_ - 28 * hb, hy_ - 20 * hb, hx_ + 2, hy_ + 10], fill=(255, 50, 80)); d.ellipse([hx_ - 2, hy_ - 20 * hb, hx_ + 28 * hb, hy_ + 10], fill=(255, 50, 80))
    d.polygon([(hx_ - 28 * hb, hy_ - 2), (hx_ + 28 * hb, hy_ - 2), (hx_, hy_ + 34 * hb)], fill=(255, 50, 80))
    lay = lay.resize((max(1, int(lay.width * k)), max(1, int(lay.height * k))))
    img.alpha_composite(lay, (int(x - lay.width / 2), int(y - lay.height / 2)))

@shot(3.6)
def s2(t):  # lo pidieron en comentarios
    img = cached("col_blur", lambda: colosseum_bg().filter(ImageFilter.GaussianBlur(10)))
    comment_card(img, 648, 1000, 1.25 * eob(t / 0.35), t)
    nico(img, 648, 2250, 1.3, "happy", arms="up", phase=t * 4)
    return img, (648, 1400, 1.05 + 0.06 * ease(t / 3.6), 0)

@shot(3.8)
def s3(t):  # 50.000 romanos y un gladiador
    img = cached("col", colosseum_bg)
    crowd(img, t, 0.9)
    emperor_box(img, t)
    d = ImageDraw.Draw(img)
    k = ease((t - 1.6) / 0.6)
    romano(img, lerp(1600, 920, k), 2200, 1.25, "gladiator", "sword", t, "angry")
    nico(img, lerp(648, 340, k), 2180, 1.2, "worried" if t < 1.6 else "scared", look=(1 if t > 1.6 else 0, -1), arms="down")
    pop_text(img, "50.000", 648, 820, eob((t - 0.2) / 0.3), 190)
    z = lerp(1.0, 1.12, ease(t / 3.8))
    return img, (648, lerp(1100, 1650, ease((t - 1.4) / 0.8)), z, 6 if 0.2 < t < 1.4 else 0)

def backpack(img, x, y, s, open_):
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([x - 230 * s, y - 280 * s, x + 230 * s, y + 280 * s], radius=int(90 * s), fill=(230, 80, 60, 255), outline=OL, width=int(8 * s))
    d.rounded_rectangle([x - 160 * s, y + 20 * s, x + 160 * s, y + 220 * s], radius=int(40 * s), fill=(200, 60, 46, 255), outline=OL, width=int(6 * s))
    d.line([x - 120 * s, y + 60 * s, x + 120 * s, y + 60 * s], fill=(255, 220, 90, 255), width=int(8 * s))
    if open_ > 0:
        d.ellipse([x - 190 * s, y - 300 * s, x + 190 * s, y - 200 * s], fill=(60, 20, 20, 255), outline=OL, width=int(6 * s))
    fy = y - 280 * s - open_ * 120 * s
    d.chord([x - 230 * s, fy - 60 * s, x + 230 * s, fy + 100 * s], 180, 360, fill=(240, 100, 76, 255), outline=OL, width=int(8 * s))

def notebook(img, x, y, s):
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([x - 110 * s, y - 150 * s, x + 110 * s, y + 150 * s], radius=int(14 * s), fill=(60, 110, 220, 255), outline=OL, width=int(6 * s))
    d.rectangle([x - 70 * s, y - 100 * s, x + 80 * s, y - 50 * s], fill=(255, 255, 255, 255), outline=OL, width=int(3 * s))
    for k in range(7): d.ellipse([x - 124 * s, y - 130 * s + k * 42 * s, x - 96 * s, y - 112 * s + k * 42 * s], outline=(200, 200, 210, 255), width=int(5 * s))

def calculator(img, x, y, s):
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([x - 100 * s, y - 150 * s, x + 100 * s, y + 150 * s], radius=int(20 * s), fill=(80, 84, 96, 255), outline=OL, width=int(6 * s))
    d.rectangle([x - 76 * s, y - 126 * s, x + 76 * s, y - 66 * s], fill=(170, 210, 160, 255), outline=OL, width=int(3 * s))
    d.text((x - 60 * s, y - 126 * s), "58008", font=font(F_BLACK, int(46 * s)), fill=(30, 50, 30))
    for i in range(3):
        for j in range(4):
            d.rounded_rectangle([x - 76 * s + i * 54 * s, y - 46 * s + j * 46 * s, x - 34 * s + i * 54 * s, y - 12 * s + j * 46 * s], radius=int(6 * s), fill=(220, 220, 228, 255) if (i + j) % 3 else (255, 150, 60, 255))

@shot(4.0)
def s4(t):  # la mochila
    img = cached("col_blur", lambda: colosseum_bg().filter(ImageFilter.GaussianBlur(10)))
    op = ease(t / 0.4)
    items = [(0.9, notebook, 300, 780, -12), (2.0, calculator, 980, 760, 10), (3.1, None, 648, 600, 0)]
    for t0, fn, tx, ty, r_ in items:
        if t < t0: continue
        k = eob((t - t0) / 0.35)
        x, y = lerp(648, tx, k), lerp(1300, ty, k)
        if fn is None:
            glow(img, x, y, 700, (90, 220, 240), 0.5 * k)
            speaker(img, x, y, 1.3 * k + 0.01, pulse=0)
        else:
            fn(img, x, y, 1.15 * k + 0.01)
    backpack(img, 648, 1500, 1.15, op)
    return img, (648, 1250, 1.0 + 0.05 * ease(t / 4), 10 * math.exp(-(t - 3.1) * 8) if t > 3.1 else 0)

@shot(2.2)
def s5(t):  # se abre la reja: león
    img = cached("col", colosseum_bg)
    crowd(img, t, 0.5)
    k = ease((t - 0.1) / 0.8)
    lk = ease((t - 0.8) / 0.8)
    if lk > 0: lion(img, 680, lerp(1400, 2050, lk), lerp(0.55, 1.2, lk), "stand", t, "angry")
    gate(img, k * 220)
    nico(img, 350, 2250, 1.15, "scared", look=(1, -1), arms="down")
    return img, (648, lerp(1300, 1600, lk), lerp(1.25, 1.05, lk), 12 if t > 1.4 else 0)

@shot(1.6)
def s6(t):  # pone reguetón
    img = cached("col_blur", lambda: colosseum_bg().filter(ImageFilter.GaussianBlur(10)))
    pulse = abs(math.sin(t * 9.8))
    glow(img, 648, 900, int(900 + 200 * pulse), (255, 60, 200), 0.4)
    nico(img, 600, 2250, 1.35, "smug", arms="phone_up", phase=t)
    speaker(img, 600 + 300, 2250 - 760, 0.9, pulse)
    notes(img, 760, 1500, t * 2, 7)
    pop_text(img, "VOL MAX", 648, 760, eob(t / 0.3), 140, (255, 90, 200))
    return img, (648, 1450, 1.08 + 0.05 * pulse, 8 * pulse)

def disco(img, t):
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for k, c in enumerate([(255, 60, 200), (60, 220, 255), (255, 230, 60)]):
        a = math.sin(t * 3 + k * 2) * 0.5
        x0 = 648 + math.sin(a) * 2400
        d.polygon([(648, 300), (x0 - 200, WH), (x0 + 200, WH)], fill=c + (60,))
    img.alpha_composite(lay)

@shot(1.6)
def s7(t):  # el león baila
    img = cached("col", colosseum_bg)
    crowd(img, t, 0.7)
    disco(img, t)
    lion(img, 760, 2150, 1.25, "dance", t, "happy")
    nico(img, 200, 2250, 1.0, "shock", arms="phone_up")
    speaker(img, 200 + 200, 2250 - 560, 0.6, abs(math.sin(t * 9.8)))
    notes(img, 700, 1300, t * 2, 6)
    return img, (648, 1600, 1.08 + 0.04 * abs(math.sin(t * 9.8)), 5)

@shot(2.6)
def s8(t):  # público enloquece, emperador aplaude
    img = cached("col", colosseum_bg)
    crowd(img, t, 1.0)
    romano(img, 1020, 1240, 0.6, "emperor", "clap", t, "happy")
    d = ImageDraw.Draw(img); d.rectangle([840, 1170, 1200, 1250], fill=(160, 30, 40, 255), outline=OL, width=6)
    for k in range(8): d.polygon([(840 + k * 45, 1170), (885 + k * 45, 1170), (862 + k * 45, 1215)], fill=GOLD)
    rr = np.random.default_rng(int(t * 10))
    for k in range(40):  # pétalos
        x = (k * 97 + t * 200) % WW; y = (k * 211 + t * 600) % 1400 + 500
        d.ellipse([x - 10, y - 6, x + 10, y + 6], fill=(255, 120 + (k % 3) * 40, 160, 255))
    k = ease(t / 2.6)
    return img, (lerp(648, 1000, k), lerp(1000, 1080, k), lerp(1.0, 1.7, k), 4)

@shot(4.6)
def s9(t):  # chocolate al emperador
    img = cached("col", colosseum_bg)
    crowd(img, t, 0.4)
    romano(img, 930, 2230, 1.3, "emperor", "reach" if t > 0.8 else "stand", t, "stars" if t > 1.6 else "shock")
    k = ease((t - 0.2) / 0.8)
    nico(img, 300, 2230, 1.25, "happy", arms="phone_up")
    chocolate(img, lerp(450, 700, k), lerp(1680, 1700, k), 0.6, -15)
    if t > 2.6:
        kk = eob((t - 2.6) / 0.35)
        f = font(F_BLACK, 70)
        lay = Image.new("RGBA", (860, 300), (0, 0, 0, 0)); dd = ImageDraw.Draw(lay)
        dd.rounded_rectangle([10, 10, 850, 290], radius=40, fill=(255, 255, 255, 255), outline=OL, width=8)
        dd.text((50, 40), "CACAO", font=font(F_BLACK, 100), fill=(110, 60, 30))
        dd.text((50, 170), "→ viene de AMÉRICA", font=f, fill=(230, 40, 70))
        lay = lay.resize((max(1, int(860 * kk)), max(1, int(300 * kk))))
        img.alpha_composite(lay, (int(648 - lay.width / 2), int(820 - lay.height / 2)))
    return img, (648, 1500, 1.05 + 0.08 * ease(t / 4.6), 0)

@shot(2.6)
def s10(t):  # Nico Máximo
    img = cached("col", colosseum_bg)
    crowd(img, t, 1.0)
    d = ImageDraw.Draw(img)
    for k in range(50):
        x = (k * 131 + t * 90) % WW; y = (k * 173 + t * 900) % 1800 + 300
        cw = abs(math.cos(t * 6 + k)) * 22 + 3
        d.ellipse([x - cw, y - 22, x + cw, y + 22], fill=(255, 200, 40, 255), outline=(150, 100, 10, 255), width=3)
    nico(img, 648, 2250, 1.35, "smug", arms="up", phase=t * 5)
    s = 1.35; hx, hy = 648, 2250 - 400 * s
    laurel(ImageDraw.Draw(img), hx, hy - 30, 98 * s, s)
    k = eob((t - 0.3) / 0.35)
    if k > 0:
        f = font(F_BLACK, 130)
        lay = Image.new("RGBA", (1000, 260), (0, 0, 0, 0)); dd = ImageDraw.Draw(lay)
        dd.rounded_rectangle([10, 10, 990, 250], radius=30, fill=(160, 30, 40, 255), outline=GOLD, width=12)
        tx = "CAMPEÓN"; dd.text((500 - f.getlength(tx) / 2, 50), tx, font=f, fill=GOLD, stroke_width=6, stroke_fill=OL)
        lay = lay.resize((max(1, int(1000 * k)), max(1, int(260 * k))))
        img.alpha_composite(lay, (int(648 - lay.width / 2), int(820 - lay.height / 2)))
    return img, (648, 1400, 1.04 + 0.08 * ease(t / 2.6), 0)

@shot(1.7)
def s11(t):  # batería del parlante
    img = cached("col_blur", lambda: colosseum_bg().filter(ImageFilter.GaussianBlur(10)))
    img.alpha_composite(Image.new("RGBA", img.size, (255, 0, 0, int(50 + 40 * math.sin(t * 20)))))
    blink = int(t * 6) % 2 == 0
    speaker(img, 648, 1350, 1.5, 0, red=True)
    d = ImageDraw.Draw(img)
    cx, cy = 648, 860
    d.rounded_rectangle([cx - 220, cy - 110, cx + 200, cy + 110], radius=30, outline=WHITE, width=16)
    d.rounded_rectangle([cx + 200, cy - 40, cx + 240, cy + 40], radius=10, fill=WHITE)
    pct = lerp(0.2, 0.02, ease(t / 1.4))
    d.rounded_rectangle([cx - 196, cy - 86, cx - 196 + 372 * pct + 8, cy + 86], radius=16, fill=(255, 50, 50) if blink else (180, 20, 20))
    pop_text(img, f"{int(pct * 100)}%", 648, 1120, 1.0, 120, (255, 80, 80) if blink else WHITE)
    return img, (648, 1250, 1.0 + 0.15 * ease(t / 1.7), 6)

@shot(1.4)
def s12(t):  # el león deja de bailar
    img = cached("col", colosseum_bg)
    crowd(img, 0, 0.0)
    img.alpha_composite(Image.new("RGBA", img.size, (0, 0, 40, 90)))
    lion(img, 780, 2150, 1.25, "stand", t, "neutral" if t < 0.6 else "angry")
    nico(img, 330, 2250, 1.05, "scared", look=(1, 0), arms="phone_up")
    speaker(img, 330 + 210, 2250 - 580, 0.6, 0, red=True)
    if t > 0.6:
        d = ImageDraw.Draw(img); f = font(F_BLACK, 150)
        d.text((640, 1080 - 50 * eob((t - 0.6) / 0.3)), "!", font=f, fill=(255, 60, 60), stroke_width=10, stroke_fill=(0, 0, 0))
    return img, (700, 1650, lerp(1.05, 1.3, ease(t / 1.4)), 0)

@shot(1.8)
def s13(t):  # ¡CORRE!
    img = cached("col", colosseum_bg)
    crowd(img, t, 0.9)
    d = ImageDraw.Draw(img); off = t * 1600
    for k in range(16):
        y = 1450 + (k * 137) % 800; x = (WW - (off * 2 + k * 300) % (WW + 600))
        d.line([x, y, x + 260, y], fill=(255, 255, 255, 140), width=6)
    nico(img, 920, 2220, 1.2, "scared", look=(-1, 0), arms="run", phase=t * 22, lean=0.4)
    lion(img, 330 + math.sin(t * 20) * 10, 2260, 1.05, "pounce", t, "angry")
    return img, (648, 1750, 1.1, 10)

@shot(2.6)
def s14(t):  # salta al portal → loop
    img = cached("col", colosseum_bg)
    crowd(img, t, 0.6)
    emperor_box(img, t, "stand", "shock")
    portal(img, 648, 1200, 640, t, ease(t / 0.4))
    k = ease((t - 0.2) / 0.9)
    if k < 1:
        nico(img, lerp(200, 648, k), lerp(2000, 1200, k) - math.sin(k * math.pi) * 400, 1.0 * (1 - 0.8 * k), "shock", arms="up", phase=t * 10)
    lk = ease(t / 1.4)
    if lk < 1: lion(img, lerp(100, 520, lk), 2150, 0.8, "pounce", t, "shock")
    zoom = 1.0 + 0.6 * ease((t - 1.1) / 1.5)
    return img, (648, 1200, zoom, 0)

# ---------------- voz: cada plano dura lo que su frase (+ respiro) y los subtítulos siguen la voz
from scipy.io import wavfile as _wf
VOZ = []
for k in range(1, len(SHOTS) + 1):
    sr_, a_ = _wf.read(f"voz/v{k:02d}_f.wav"); VOZ.append(a_.astype(np.float32) / 32768.0)
VSR = 44100
LEAD = 0.12
CHUNKS = [
    [("¿Qué pasaría si", []), ("caes en el COLISEO", ["COLISEO"]), ("con tu mochila?", ["mochila?"])],
    [("Ustedes", []), ("lo pidieron", ["pidieron"]), ("en los comentarios…", ["comentarios…"]), ("así que aquí estoy", [])],
    [("50.000 romanos", ["50.000"]), ("gritando…", []), ("y un GLADIADOR", ["GLADIADOR"]), ("enfrente", [])],
    [("Abres la mochila:", ["mochila:"]), ("un cuaderno,", []), ("una calculadora…", []), ("y un PARLANTE", ["PARLANTE"])],
    [("Abren la reja…", ["reja…"]), ("y sale un LEÓN", ["LEÓN"])],
    [("Reguetón", ["Reguetón"]), ("a todo volumen…", ["volumen…"])],
    [("y el león", []), ("se pone a BAILAR", ["BAILAR"])],
    [("El público", []), ("ENLOQUECE", ["ENLOQUECE"]), ("El emperador", []), ("te aplaude", ["aplaude"])],
    [("Le das chocolate", ["chocolate"]), ("al emperador…", []), ("y alucina:", ["alucina:"]), ("el cacao", []), ("venía de AMÉRICA", ["AMÉRICA"])],
    [("Ahora eres", []), ("la estrella de Roma:", ["Roma:"]), ("NICO MÁXIMO", ["NICO", "MÁXIMO"])],
    [("Pero el parlante", []), ("se queda sin batería…", ["batería…"])],
    [("y el león", []), ("deja de bailar", ["deja"])],
    [("¡CORRE!", ["¡CORRE!"])],
    [("¿A qué época", ["época"]), ("voy mañana?", ["mañana?"]), ("Coméntalo", ["Coméntalo"])],
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
            img.alpha_composite(lay, (int(W / 2 - lay.width / 2), int(1600 - lay.height / 2)))
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
    def at(k, x): return STARTS[k] + x * DURS[k] / BASE[k]
    noise = np.random.default_rng(1).standard_normal(n)
    # --- música épica (tambores + metales) fuera de la parte del reguetón
    bpm = 120; b = 60 / bpm
    scale = [62, 64, 65, 67, 69, 71, 72, 74]  # re dórico
    mel = [0, 4, 3, 4, 5, 4, 3, 1, 0, 2, 4, 2, 1, 0, 1, 0]
    rg0, rg1 = STARTS[5], STARTS[10] + DURS[10] * 0.55   # reguetón
    sil0, sil1 = rg1, STARTS[12]                          # silencio incómodo
    for k in range(int(TOTAL / b)):
        s = k * b
        if rg0 - 0.05 <= s < sil1: continue
        seg = np.arange(int(0.25 * sr)) / sr
        add(s, 0.55 * np.exp(-seg * 14) * np.sin(2 * np.pi * (50 + 100 * np.exp(-seg * 30)) * seg))
        if k % 2: add(s + b / 2, 0.25 * np.random.default_rng(k).standard_normal(int(0.12 * sr)) * np.exp(-np.arange(int(0.12 * sr)) / sr * 30))
        root = 38 if (k // 8) % 2 == 0 else 36
        seg = np.arange(int(b * 0.9 * sr)) / sr
        add(s, 0.16 * np.exp(-seg * 4) * np.sign(np.sin(2 * np.pi * hz(root) * seg)) * 0.5)
        m = scale[mel[k % 16]]
        seg = np.arange(int(b * 0.95 * sr)) / sr
        env = np.clip(seg / 0.03, 0, 1) * np.exp(-seg * 3)
        sig = sum(np.sin(2 * np.pi * hz(m) * h_ * seg) / h_ for h_ in (1, 2, 3, 4, 5))
        add(s, 0.045 * env * sig)
    # --- dembow
    b2 = 60 / 96; k = 0
    while rg0 + k * b2 < rg1:
        s = rg0 + k * b2
        seg = np.arange(int(0.25 * sr)) / sr
        add(s, 0.7 * np.exp(-seg * 12) * np.sin(2 * np.pi * (45 + 90 * np.exp(-seg * 30)) * seg))
        for off in ((0.75,) if k % 2 == 0 else (0.5, 0.75)):
            sn = np.random.default_rng(k * 3).standard_normal(int(0.1 * sr)) * np.exp(-np.arange(int(0.1 * sr)) / sr * 35)
            add(s + off * b2, 0.35 * sn)
        seg = np.arange(int(b2 * 0.5 * sr)) / sr
        add(s, 0.2 * np.exp(-seg * 6) * np.sin(2 * np.pi * hz(33 if (k // 4) % 2 == 0 else 31) * seg))
        hs = np.random.default_rng(100 + k).standard_normal(int(0.04 * sr)) * np.exp(-np.arange(int(0.04 * sr)) / sr * 90)
        add(s + b2 / 2, 0.08 * hs)
        k += 1
    sos = butter(2, [500, 4000], btype="band", fs=sr, output="sos"); wn = sosfilt(sos, noise)
    for s in STARTS[1:-1]:  # whoosh
        i0 = max(0, int((s - 0.2) * sr)); i1 = min(n, int((s + 0.2) * sr)); seg = tt[i0:i1] - (s - 0.2)
        out[i0:i1] += 0.5 * np.sin(np.pi * seg / 0.4) ** 2 * wn[i0:i1]
    for s, *_ in CAPS:  # pop
        seg = np.arange(int(0.04 * sr)) / sr; add(s, 0.07 * np.exp(-seg * 90) * np.sin(2 * np.pi * 1400 * seg))
    def boom(s, v=0.8):
        seg = np.arange(int(0.9 * sr)) / sr; add(s, v * np.exp(-seg * 5) * np.sin(2 * np.pi * (40 + 70 * np.exp(-seg * 8)) * seg))
    def roar(s, dur=1.2, v=0.5):
        i0 = int(s * sr); i1 = min(n, i0 + int(dur * sr))
        if i0 >= n: return
        seg = tt[i0:i1] - s
        sos3 = butter(2, [80, 600], btype="band", fs=sr, output="sos")
        g = sosfilt(sos3, noise[i0:i1]) * (1 + 0.8 * np.sin(2 * np.pi * 28 * seg)) * np.clip(seg / 0.1, 0, 1) * np.exp(-seg * 1.5)
        out[i0:i1] += v * 4 * g
    def crowd_noise(a, b_, v=0.3):
        i0 = int(a * sr); i1 = min(n, int(b_ * sr))
        sos2 = butter(2, [200, 1500], btype="band", fs=sr, output="sos")
        seg = tt[i0:i1] - a
        out[i0:i1] += v * sosfilt(sos2, noise[i0:i1]) * np.clip(seg / 0.3, 0, 1) * np.clip((b_ - tt[i0:i1]) / 0.3, 0, 1)
    seg = np.arange(int(1.1 * sr)) / sr                      # caída
    add(0.0, 0.12 * np.sin(2 * np.pi * (1600 - 1200 * seg / 1.1) * seg) * np.clip(1 - seg / 1.1, 0, 1))
    boom(at(0, 1.1))
    crowd_noise(0.0, STARTS[2], 0.12)
    crowd_noise(STARTS[2], STARTS[3], 0.4)                   # 50.000 gritando
    for k_, t0 in enumerate((0.9, 2.0, 3.1)):                # objetos de la mochila
        seg = np.arange(int(0.25 * sr)) / sr; add(at(3, t0), 0.2 * np.exp(-seg * 12) * np.sin(2 * np.pi * (500 + 400 * k_ + 600 * seg) * seg))
    i0 = int(at(4, 0.1) * sr); seg = np.arange(int(0.8 * sr)) / sr   # reja
    add(at(4, 0.1), 0.1 * np.sign(np.sin(2 * np.pi * (70 + 30 * np.sin(seg * 9)) * seg)) * np.exp(-seg * 2))
    roar(at(4, 1.0), 1.2, 0.6)
    crowd_noise(STARTS[7], STARTS[8], 0.45)                  # público enloquece
    seg = np.arange(int(0.6 * sr)) / sr
    add(at(8, 1.6), 0.18 * np.exp(-seg * 5) * (np.sin(2 * np.pi * 1320 * seg) + np.sin(2 * np.pi * 1760 * seg)))  # brillo
    crowd_noise(STARTS[9], STARTS[10], 0.35)
    for k_ in range(30):                                     # monedas
        f = 2000 + (k_ * 373) % 1800; seg = np.arange(int(0.12 * sr)) / sr
        add(STARTS[9] + 0.1 + k_ * 0.07, 0.04 * np.exp(-seg * 30) * np.sin(2 * np.pi * f * seg))
    seg = np.arange(int(0.8 * sr)) / sr                      # se apaga el parlante
    add(rg1, 0.25 * np.sin(2 * np.pi * (500 * np.exp(-seg * 3)) * seg) * np.exp(-seg * 2))
    roar(at(11, 0.6), 0.9, 0.4)
    roar(STARTS[12], 1.0, 0.6)
    for k_ in range(10):                                     # pasos
        seg = np.arange(int(0.06 * sr)) / sr; add(STARTS[12] + k_ * 0.15, 0.25 * np.exp(-seg * 60) * np.sin(2 * np.pi * 120 * seg))
    seg = np.arange(int(2.0 * sr)) / sr                      # portal
    add(STARTS[13], 0.12 * np.sin(2 * np.pi * (200 + 600 * seg / 2) * seg + 3 * np.sin(2 * np.pi * 6 * seg)) * np.clip(seg / 0.3, 0, 1))
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
