"""vc.py — motor de animación VECTOR + CÓMIC de Mundo Hipotético.
Cada cuadro: 1) formas planas (sin degradados) dibujadas a través de una cámara, 2) pase de tinta:
contorno negro donde cambia el color + trama de puntos en las sombras + saturación, 3) efectos de luz,
texto y partículas encima, 4) grano y viñeta."""
import math
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
F_BLACK = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
F_SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
_FC = {}
def font(s, f=F_BLACK):
    k = (f, int(s))
    if k not in _FC: _FC[k] = ImageFont.truetype(f, max(1, int(s)))
    return _FC[k]

INK = (18, 12, 20)
TURQ = (40, 186, 204); TURQ_D = (28, 140, 160)
SKIN = (248, 196, 150); HAIR = (66, 40, 30)

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(x): x = clamp(x); return x * x * (3 - 2 * x)
def eob(x):
    x = clamp(x); c = 1.70158
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2
def lerp(a, b, k): return a + (b - a) * k

class Cam:
    def __init__(self, cx=540, cy=960, z=1.0, sx=0.0, sy=0.0, rot=0.0):
        self.cx, self.cy, self.z, self.sx, self.sy = cx, cy, z, sx, sy
    def p(self, x, y): return ((x - self.cx) * self.z + W / 2 + self.sx, (y - self.cy) * self.z + H / 2 + self.sy)
    def s(self, v): return v * self.z

class D:
    """Lienzo plano + máscara de sombra, con cámara."""
    def __init__(self, cam, bg=(0, 0, 0)):
        self.cam = cam
        self.img = Image.new("RGB", (W, H), bg); self.d = ImageDraw.Draw(self.img)
        self.sh = Image.new("L", (W, H), 0); self.ds = ImageDraw.Draw(self.sh)
        self.nolin = Image.new("L", (W, H), 0); self.dn = ImageDraw.Draw(self.nolin)
    def P(self, pts): return [self.cam.p(x, y) for x, y in pts]
    def poly(self, pts, col, shade=False, nolin=False):
        q = self.P(pts); self.d.polygon(q, fill=col)
        if shade: self.ds.polygon(q, fill=255)
        if nolin: self.dn.polygon(q, fill=255)
    def ell(self, cx, cy, rx, ry, col, shade=None, nolin=False):
        x, y = self.cam.p(cx, cy); rx, ry = self.cam.s(rx), self.cam.s(ry)
        b = [x - rx, y - ry, x + rx, y + ry]
        self.d.ellipse(b, fill=col)
        if shade:   # sombra en media luna (luz desde arriba-izquierda)
            self.ds.ellipse(b, fill=255)
            self.ds.ellipse([b[0] - rx * 0.3, b[1] - ry * 0.25, b[2] - rx * 0.3, b[3] - ry * 0.25], fill=0)
        if nolin: self.dn.ellipse(b, fill=255)
    def rrect(self, x0, y0, x1, y1, r, col, shade=False, nolin=False):
        a = self.cam.p(x0, y0); b = self.cam.p(x1, y1)
        bb = [min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1])]
        rr = max(0, min(int(self.cam.s(r)), int((bb[2] - bb[0]) / 2), int((bb[3] - bb[1]) / 2)))
        self.d.rounded_rectangle(bb, radius=rr, fill=col)
        if shade: self.ds.rounded_rectangle([bb[0] + (bb[2] - bb[0]) * 0.62, bb[1], bb[2], bb[3]], radius=rr, fill=255)
        if nolin: self.dn.rounded_rectangle(bb, radius=rr, fill=255)
    def line(self, pts, col, w, nolin=False):
        q = self.P(pts); ww = max(1, int(self.cam.s(w)))
        self.d.line(q, fill=col, width=ww, joint="curve")
        for x, y in (q[0], q[-1]):
            self.d.ellipse([x - ww / 2, y - ww / 2, x + ww / 2, y + ww / 2], fill=col)
        if nolin: self.dn.line(q, fill=255, width=ww)
    def chord(self, cx, cy, rx, ry, a0, a1, col):
        x, y = self.cam.p(cx, cy); rx, ry = self.cam.s(rx), self.cam.s(ry)
        self.d.chord([x - rx, y - ry, x + rx, y + ry], a0, a1, fill=col)
    def pie(self, cx, cy, r, a0, a1, col):
        x, y = self.cam.p(cx, cy); r = self.cam.s(r)
        self.d.pieslice([x - r, y - r, x + r, y + r], a0, a1, fill=col)
    def text(self, x, y, s, size, col, anchor="mm", stroke=0, f=F_BLACK, nolin=True):
        X, Y = self.cam.p(x, y); fz = font(self.cam.s(size), f)
        self.d.text((X, Y), s, font=fz, fill=col, anchor=anchor, stroke_width=int(self.cam.s(stroke)), stroke_fill=INK)
        if nolin:
            bb = self.d.textbbox((X, Y), s, font=fz, anchor=anchor, stroke_width=int(self.cam.s(stroke)))
            self.dn.rectangle(bb, fill=255)

_YY, _XX = np.mgrid[0:H, 0:W]
_DOTS = (((_XX % 12) - 6) ** 2 + ((_YY % 12) - 6) ** 2) < 13
_VIG = (1 - 0.38 * (((_XX - W / 2) / W) ** 2 + ((_YY - H / 2) / H) ** 2) * 2).astype(np.float32)[..., None]
_GR = [np.random.default_rng(k).normal(0, 1, (H // 2, W // 2)).astype(np.float32) for k in range(4)]

def tinta(dr, ink_w=6, sat=1.3):
    """Pase de cómic: contornos + trama + saturación. Devuelve float32 (H, W, 3)."""
    a = np.asarray(dr.img).astype(np.int32)
    key = (a[..., 0] << 16) | (a[..., 1] << 8) | a[..., 2]
    e = np.zeros((H, W), np.uint8)
    e[:, 1:] |= (key[:, 1:] != key[:, :-1]); e[1:, :] |= (key[1:, :] != key[:-1, :])
    nl = np.asarray(dr.nolin) > 0
    e[nl] = 0
    e = cv2.dilate(e, np.ones((ink_w, ink_w), np.uint8)) > 0
    f = a.astype(np.float32)
    if sat != 1.0:
        hsv = cv2.cvtColor(a.astype(np.uint8), cv2.COLOR_RGB2HSV).astype(np.float32)
        hsv[..., 1] = np.clip(hsv[..., 1] * sat, 0, 255)
        f = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB).astype(np.float32)
    sh = np.asarray(dr.sh) > 0
    f[sh] *= 0.84
    f[sh & _DOTS] *= 0.62
    f[e] = INK
    return f

def acabado(f, T, grain=3.0):
    f = f * _VIG
    g = _GR[int(T * 24) % 4]
    g = np.repeat(np.repeat(g, 2, 0), 2, 1)
    f = f + g[..., None] * grain
    return Image.fromarray(np.clip(f, 0, 255).astype(np.uint8))

def add_glow(f, x, y, r, col, a=0.6):
    x0, x1 = int(max(0, x - r * 2.2)), int(min(W, x + r * 2.2)); y0, y1 = int(max(0, y - r * 2.2)), int(min(H, y + r * 2.2))
    if x1 <= x0 or y1 <= y0: return
    g = np.exp(-((_XX[y0:y1, x0:x1] - x) ** 2 + (_YY[y0:y1, x0:x1] - y) ** 2) / (2 * (r / 1.5) ** 2)) * a
    f[y0:y1, x0:x1] += g[..., None] * np.array(col, np.float32)

def add_cono(f, x, y_top, y_bot, w_top, w_bot, col, a=0.35):
    """Cono de luz de reflector (aditivo, bordes suaves)."""
    y0, y1 = int(max(0, y_top)), int(min(H, y_bot))
    if y1 <= y0: return
    yy = _YY[y0:y1]; xx = _XX[y0:y1]
    u = (yy - y_top) / max(1, (y_bot - y_top))
    half = w_top / 2 + (w_bot - w_top) / 2 * u
    k = np.clip(1 - np.abs(xx - x) / half, 0, 1) ** 0.6 * (0.55 + 0.45 * u)
    f[y0:y1] += (k * a)[..., None] * np.array(col, np.float32)

# ------------------------------------------------------------ NICO
def nico(dr, x, y, s, t, traje="sudadera", arms=(15, 15), elbows=(0, 0), mouth=0.0, expr="happy", look=(0, 0),
         blink=None, squash=1.0, lean=0.0, sick=False, sweat=False):
    """(x, y) = pies. Altura ≈ 870*s. arms = ángulo de cada brazo en grados (0 = abajo, 90 = horizontal afuera,
    180 = arriba); elbows = flexión."""
    sq = squash; st = 1 / math.sqrt(sq)
    S = lambda v: v * s
    def X(dx): return x + S(dx) * st + lean * S(-dx * 0 + 0)
    bob = S(6) * math.sin(t * 2.6)
    def Y(dy): return y - S(dy) * sq + (bob if dy > 230 else 0)
    def LX(dx, dy): return x + S(dx) * st + lean * S(dy) * 0.25
    pants = {"sudadera": (40, 52, 92), "pirata": (60, 44, 36), "heladero": (44, 46, 60)}.get(traje, (40, 52, 92))
    shoe = {"sudadera": (30, 30, 40), "pirata": (24, 20, 20)}.get(traje, (30, 30, 40))
    # piernas
    for sx in (-1, 1):
        dr.rrect(LX(sx * 35 - 18, 230), Y(230), LX(sx * 35 + 18, 10), Y(10), S(14), pants)
        dr.ell(LX(sx * 42, 8), Y(8), S(36) * st, S(18), shoe)
    if traje == "pirata":
        for sx in (-1, 1): dr.rrect(LX(sx * 35 - 22, 95), Y(95), LX(sx * 35 + 22, 20), Y(20), S(10), (36, 28, 24))
    # torso
    tx0, tx1, ty0, ty1 = LX(-110, 470), LX(110, 200), Y(470), Y(200)
    if traje == "sudadera":
        dr.rrect(tx0, ty0, tx1, ty1, S(90), TURQ, True)
        dr.rrect(LX(-60, 330), Y(330), LX(60, 262), Y(262), S(30), TURQ_D)
        for sx in (-22, 22): dr.line([(LX(sx, 450), Y(450)), (LX(sx, 392), Y(392))], (250, 250, 250), S(8))
        armc = TURQ
    elif traje == "heladero":   # chaqueta blanca de heladero, delantal y moño turquesa
        dr.rrect(tx0, ty0, tx1, ty1, S(90), (250, 250, 246), True)
        dr.rrect(LX(-96, 340), Y(340), LX(96, 196), Y(196), S(30), TURQ)
        for k in range(4): dr.rrect(LX(-96 + k * 52, 340), Y(340), LX(-76 + k * 52, 196), Y(196), S(4), (250, 250, 246))
        for sx in (-1, 1):
            for k in range(2): dr.ell(LX(sx * 40, 420 - k * 50), Y(420 - k * 50), S(9), S(9), (200, 200, 210))
        dr.poly([(LX(0, 455), Y(455)), (LX(-50, 480), Y(480)), (LX(-50, 430), Y(430))], TURQ_D)
        dr.poly([(LX(0, 455), Y(455)), (LX(50, 480), Y(480)), (LX(50, 430), Y(430))], TURQ_D)
        dr.ell(LX(0, 455), Y(455), S(12), S(12), TURQ)
        armc = (250, 250, 246)
    else:
        dr.rrect(tx0, ty0, tx1, ty1, S(90), (250, 246, 236), True)
        for k in range(5):
            yy = 440 - k * 48
            dr.rrect(LX(-104, yy), Y(yy), LX(104, yy - 20), Y(yy - 20), S(4), (40, 60, 120))
        dr.rrect(LX(-114, 285), Y(285), LX(114, 240), Y(240), S(10), TURQ)
        dr.poly([(LX(70, 270), Y(270)), (LX(120, 270), Y(270)), (LX(105, 200), Y(200)), (LX(80, 210), Y(210))], TURQ_D)
        armc = (250, 246, 236)
    # brazos (hombro → codo → mano)
    hands = []
    for sx, a, eb in ((-1, arms[0], elbows[0]), (1, arms[1], elbows[1])):
        shx, shy = LX(sx * 92, 430), Y(430)
        a1 = math.radians(a); a2 = math.radians(a + eb)
        ex, ey = shx + sx * math.sin(a1) * S(95), shy + math.cos(a1) * S(95)
        hx, hy = ex + sx * math.sin(a2) * S(90), ey + math.cos(a2) * S(90)
        dr.line([(shx, shy), (ex, ey), (hx, hy)], armc, S(44))
        dr.ell(hx, hy, S(30), S(30), SKIN)
        hands.append((hx, hy))
    # cabeza
    hx, hy, R = LX(0, 640), Y(640), S(190)
    face = (196, 222, 150) if sick else SKIN
    for sx in (-1, 1): dr.ell(hx + sx * R, hy + S(25), S(33), S(45), face)
    dr.ell(hx, hy, R * st, R * sq, face, shade=True)
    for k in range(7):
        a = math.pi + k * math.pi / 6
        px, py = hx + math.cos(a) * R * 0.86, hy + math.sin(a) * R * 0.86 * sq - S(10)
        dr.ell(px, py, S(70), S(60), HAIR)
    if blink is None: blink = (t % 3.3) < 0.12
    for k, ex in enumerate((-70, 70)):
        cx, cy = hx + S(ex), hy + S(10)
        if expr == "happy_eyes" or (blink and expr != "shock"):
            dr.chord(cx, cy + S(10), S(36), S(26), 180, 360, (24, 18, 26)) if expr == "happy_eyes" else dr.rrect(cx - S(34), cy - S(4), cx + S(34), cy + S(6), S(4), (24, 18, 26))
            if expr == "happy_eyes": dr.chord(cx, cy + S(16), S(30), S(20), 180, 360, face)
            continue
        big = 1.18 if expr == "shock" else 1.0
        dr.ell(cx, cy, S(42) * big, S(50) * big, (255, 255, 255))
        pr = S(16) if expr == "shock" else S(21)
        px, py = cx + look[0] * S(14), cy + look[1] * S(14)
        dr.ell(px, py, pr, pr * 1.25, (24, 18, 26))
        dr.ell(px - S(6), py - S(9), S(7), S(7), (255, 255, 255))
        # cejas
        by = cy - S(72) * big
        tilt = {"angry": 18, "nervous": -16, "worried": -16, "shock": -4, "smug": 8}.get(expr, -4) * (1 if ex < 0 else -1)
        dr.line([(cx - S(34), by + S(tilt) * 0.5), (cx + S(34), by - S(tilt) * 0.5)], HAIR, S(13))
    for ex in (-100, 100): dr.ell(hx + S(ex), hy + S(85), S(25), S(15), (240, 140, 140) if not sick else (170, 200, 130))
    # boca
    mo = clamp(mouth)
    if mo > 0.06 or expr == "shock":
        mo = max(mo, 0.6 if expr == "shock" else 0)
        dr.ell(hx, hy + S(108), S(48 - 10 * (expr == "shock")), S(14 + 34 * mo), (120, 30, 40))
        dr.ell(hx, hy + S(108 + 22 * mo), S(26), S(8 + 10 * mo), (236, 110, 120))
    elif expr in ("nervous", "worried"):
        pts = [(hx + S(-50 + k * 20), hy + S(110 + (8 if k % 2 else -4))) for k in range(6)]
        dr.line(pts, (120, 30, 40), S(9))
    elif expr == "smug":
        dr.line([(hx - S(40), hy + S(112)), (hx + S(10), hy + S(115)), (hx + S(48), hy + S(98))], (120, 30, 40), S(10))
    else:
        dr.chord(hx, hy + S(80), S(55), S(48), 0, 180, (120, 30, 40))
    if sweat:
        k = (t * 1.2) % 1
        dr.ell(hx + S(170), hy - S(40) + S(60) * k, S(14), S(20), (140, 210, 255))
    # sombrero pirata
    if traje == "pirata":
        dr.poly([(hx - S(270), hy - S(105)), (hx, hy - S(330)), (hx + S(270), hy - S(105)), (hx, hy - S(165))], (30, 26, 30))
        dr.ell(hx, hy - S(232), S(28), S(28), TURQ)
        dr.ell(hx, hy - S(232), S(12), S(12), (255, 255, 255))
    if traje == "heladero":   # gorro de papel blanco con franja turquesa
        dr.poly([(hx - S(175), hy - S(140)), (hx + S(175), hy - S(140)), (hx + S(135), hy - S(275)), (hx - S(135), hy - S(275))], (252, 252, 248))
        dr.rrect(hx - S(166), hy - S(195), hx + S(166), hy - S(165), S(4), TURQ)
    return dict(hands=hands, head=(hx, hy), top=(hx, hy - R))

# ------------------------------------------------------------ CAPITÁN BARBAGRIS
def capitan(dr, x, y, s, t, mouth=0.0, expr="angry", arm_r=20, arm_l=20, blink=None, look=(0, 0)):
    S = lambda v: v * s
    bob = S(5) * math.sin(t * 2.1)
    # pata de palo + bota
    dr.rrect(x - S(70), y - S(240), x - S(20), y - S(10), S(12), (130, 86, 52))
    dr.rrect(x + S(20), y - S(240), x + S(80), y - S(10), S(14), (40, 30, 30))
    dr.ell(x + S(60), y - S(10), S(50), S(22), (24, 18, 20))
    # abrigo rojo y panza
    dr.poly([(x - S(170), y - S(200)), (x - S(130), y - S(560) + bob), (x + S(130), y - S(560) + bob), (x + S(170), y - S(200))], (170, 34, 38), shade=False)
    dr.ell(x, y - S(360) + bob, S(150), S(160), (236, 226, 200), shade=True)
    dr.rrect(x - S(150), y - S(300) + bob, x + S(150), y - S(260) + bob, S(10), (40, 30, 30))
    dr.rrect(x - S(25), y - S(305) + bob, x + S(25), y - S(255) + bob, S(6), (230, 190, 60))
    for k in range(4): dr.ell(x - S(110), y - S(520) + bob + k * S(70), S(13), S(13), (230, 190, 60))
    # brazos: derecho garfio, izquierdo mano
    for sx, ang in ((-1, arm_l), (1, arm_r)):
        shx, shy = x + sx * S(140), y - S(520) + bob
        a = math.radians(ang)
        hx, hy = shx + sx * math.sin(a) * S(200), shy + math.cos(a) * S(200)
        dr.line([(shx, shy), (hx, hy)], (170, 34, 38), S(70))
        if sx > 0:
            dr.rrect(hx - S(26), hy - S(16), hx + S(26), hy + S(30), S(8), (90, 60, 40))
            dr.line([(hx, hy + S(20)), (hx, hy + S(70)), (hx + S(30), hy + S(95)), (hx + S(55), hy + S(70))], (200, 205, 215), S(14))
        else:
            dr.ell(hx, hy + S(10), S(34), S(34), (232, 180, 140))
    # cabeza
    hx, hy = x, y - S(700) + bob
    dr.ell(hx, hy, S(170), S(165), (232, 180, 140), shade=True)
    # barba gris larga
    dr.poly([(hx - S(170), hy + S(10)), (hx - S(120), hy + S(250)), (hx - S(40), hy + S(330)), (hx, hy + S(280)), (hx + S(40), hy + S(340)), (hx + S(120), hy + S(250)), (hx + S(170), hy + S(10)), (hx + S(90), hy + S(80)), (hx - S(90), hy + S(80))], (170, 174, 184))
    # boca
    mo = clamp(mouth)
    dr.ell(hx, hy + S(115), S(55), S(10 + 40 * mo), (90, 20, 30))
    if mo > 0.3: dr.rrect(hx - S(40), hy + S(105 - 30 * mo), hx + S(40), hy + S(105 - 18 * mo), S(4), (250, 240, 200))
    # bigote
    for sx in (-1, 1): dr.ell(hx + sx * S(60), hy + S(80), S(70), S(28), (190, 194, 204))
    dr.ell(hx, hy + S(30), S(42), S(46), (222, 150, 120))   # nariz
    # ojo + parche
    if blink is None: blink = (t % 3.8) < 0.12
    ex, ey = hx + S(65), hy - S(40)
    if blink: dr.rrect(ex - S(30), ey - S(4), ex + S(30), ey + S(6), S(3), INK)
    else:
        dr.ell(ex, ey, S(34), S(38), (255, 255, 255))
        dr.ell(ex + look[0] * S(10), ey + look[1] * S(10), S(16), S(19), INK)
    dr.line([(hx - S(160), hy - S(130)), (hx + S(160), hy - S(10))], INK, S(10))
    dr.ell(hx - S(65), hy - S(40), S(42), S(40), INK)
    tilt = {"angry": 22, "smug": -6, "laugh": -10}.get(expr, 10)
    dr.line([(ex - S(45), ey - S(60) - S(tilt)), (ex + S(45), ey - S(60) + S(tilt) * 0.3)], (120, 124, 134), S(22))
    # sombrero con calavera
    dr.poly([(hx - S(300), hy - S(110)), (hx - S(200), hy - S(330)), (hx, hy - S(400)), (hx + S(200), hy - S(330)), (hx + S(300), hy - S(110)), (hx, hy - S(170))], (28, 24, 28))
    dr.rrect(hx - S(250), hy - S(170), hx + S(250), hy - S(135), S(10), (230, 190, 60))
    dr.ell(hx, hy - S(270), S(46), S(42), (250, 250, 245))
    for sx in (-1, 1): dr.ell(hx + sx * S(17), hy - S(275), S(11), S(13), INK)
    dr.rrect(hx - S(22), hy - S(245), hx + S(22), hy - S(225), S(4), (250, 250, 245))
    return dict(head=(hx, hy), shoulder=(x - S(140), y - S(560) + bob))

# ------------------------------------------------------------ LORO
def loro(dr, x, y, s, t, mouth=0.0, flap=0.0, look=(0, 0), face=1):
    """(x, y) = patas. face = 1 mira a la derecha."""
    S = lambda v: v * s; f = face
    dr.poly([(x - f * S(30), y - S(60)), (x - f * S(120), y + S(120)), (x - f * S(70), y + S(130)), (x - f * S(5), y - S(30))], (40, 90, 200))     # cola azul
    dr.poly([(x - f * S(10), y - S(50)), (x - f * S(80), y + S(140)), (x - f * S(40), y + S(150)), (x + f * S(15), y - S(20))], (230, 50, 40))
    dr.ell(x, y - S(110), S(70), S(100), (60, 180, 70), shade=True)
    wa = math.sin(t * 30) * flap
    dr.poly([(x - f * S(10), y - S(150)), (x - f * S(110), y - S(120) - S(140) * wa), (x - f * S(60), y - S(40))], (40, 140, 60))
    hx, hy = x + f * S(15), y - S(220)
    dr.ell(hx, hy, S(62), S(58), (230, 50, 40), shade=True)
    dr.ell(hx + f * S(18), hy - S(10), S(22), S(22), (255, 255, 255))
    dr.ell(hx + f * S(22) + look[0] * S(6), hy - S(10) + look[1] * S(6), S(10), S(10), INK)
    mo = clamp(mouth)
    bx, by = hx + f * S(50), hy + S(5)
    dr.poly([(bx, by - S(30)), (bx + f * S(70), by - S(5) - S(10) * mo), (bx + f * S(30), by + S(5))], (250, 200, 60))
    dr.poly([(bx, by + S(5) + S(20) * mo), (bx + f * S(45), by + S(15) + S(30) * mo), (bx + f * S(5), by + S(30) + S(20) * mo)], (220, 160, 40))
    for k in (-1, 1): dr.line([(x + k * S(15), y - S(15)), (x + k * S(20), y + S(5))], (200, 150, 60), S(8))
    return (hx, hy)

# ------------------------------------------------------------ TIBURÓN
def aleta(dr, x, y, s, col=(120, 130, 150)):
    S = lambda v: v * s
    dr.poly([(x - S(70), y), (x + S(10), y - S(140)), (x + S(60), y)], col, shade=True)

def tiburon(dr, x, y, s, t, jaw=0.6, face=1):
    S = lambda v: v * s; f = face
    dr.poly([(x - f * S(260), y), (x - f * S(330), y - S(90)), (x - f * S(300), y), (x - f * S(330), y + S(80))], (110, 120, 140))
    dr.ell(x, y, S(260), S(120), (130, 140, 160), shade=True)
    dr.ell(x + f * S(20), y + S(50), S(200), S(60), (230, 232, 236))
    dr.poly([(x - f * S(20), y - S(100)), (x + f * S(40), y - S(230)), (x + f * S(90), y - S(100))], (110, 120, 140))
    jx = x + f * S(210)
    dr.poly([(jx, y - S(10)), (jx + f * S(110), y - S(70) - S(60) * jaw), (jx + f * S(110), y + S(70) + S(60) * jaw)], (90, 20, 30))
    for k in range(4):
        u = k / 3
        dr.poly([(jx + f * S(20 + 80 * u), y - S(20) - S(50 + 40 * jaw) * u), (jx + f * S(35 + 80 * u), y - S(40) - S(50 + 40 * jaw) * u + S(40)), (jx + f * S(50 + 80 * u), y - S(20) - S(50 + 40 * jaw) * u)], (255, 255, 255))
    dr.ell(x + f * S(140), y - S(40), S(16), S(16), INK)
