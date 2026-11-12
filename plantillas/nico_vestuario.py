"""Hoja de vestuario de Nico en estilo vector + cómic. Lo fijo: pelo de grumos, ojos grandes, cachetes,
y SIEMPRE algo turquesa (su color). Lo que cambia: la ropa según el mundo del episodio."""
import math, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
F = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
def font(s): return ImageFont.truetype(F, int(s))
TURQ = (40, 186, 204); TURQ_D = (28, 140, 160); SKIN = (248, 196, 150); HAIR = (66, 40, 30); INK = (18, 12, 20)

def nico(d, sh, cx, fy, s, traje):
    S = lambda v: v * s
    def E(b, c, shade=False):
        d.ellipse(b, fill=c)
        if shade: sh.ellipse(b, fill=255); sh.ellipse([b[0] - (b[2] - b[0]) * 0.28, b[1] - (b[3] - b[1]) * 0.18, b[2] - (b[2] - b[0]) * 0.28, b[3] - (b[3] - b[1]) * 0.18], fill=0)
    def R(b, r, c, shade=False):
        d.rounded_rectangle(b, radius=int(r), fill=c)
        if shade: sh.rounded_rectangle([b[0] + (b[2] - b[0]) * 0.62, b[1], b[2], b[3]], radius=int(r * 0.7), fill=255)
    pants = {"sudadera": (40, 52, 92), "cavernicola": SKIN, "astronauta": (236, 238, 244), "romano": SKIN, "pirata": (60, 44, 36)}[traje]
    shoe = {"sudadera": (30, 30, 40), "cavernicola": (120, 80, 50), "astronauta": (90, 96, 110), "romano": (150, 100, 60), "pirata": (24, 20, 20)}[traje]
    for sx in (-1, 1):
        R([cx + S(sx * 35 - 18), fy - S(230), cx + S(sx * 35 + 18), fy - S(10)], S(14), pants)
        E([cx + S(sx * 40 - 34), fy - S(28), cx + S(sx * 40 + 34), fy + S(8)], shoe)
    if traje == "romano":
        for sx in (-1, 1): d.line([(cx + S(sx * 35 - 18), fy - S(70)), (cx + S(sx * 35 + 18), fy - S(110))], fill=(120, 80, 50), width=int(S(8)))
    # torso por traje
    tb = [cx - S(110), fy - S(470), cx + S(110), fy - S(200)]
    if traje == "sudadera":
        R(tb, S(90), TURQ, True); R([cx - S(60), fy - S(330), cx + S(60), fy - S(262)], S(30), TURQ_D)
        for sx in (-22, 22): d.line([(cx + S(sx), fy - S(450)), (cx + S(sx), fy - S(392))], fill=(250, 250, 250), width=int(S(8)))
        arm = TURQ
    elif traje == "cavernicola":
        R(tb, S(90), (200, 120, 56), True)
        for (a, b) in ((-50, -420), (40, -300), (-20, -250), (60, -440), (-70, -320)): E([cx + S(a - 18), fy + S(b - 12), cx + S(a + 18), fy + S(b + 12)], (140, 78, 36))
        d.line([(cx - S(100), fy - S(445)), (cx + S(90), fy - S(250))], fill=TURQ, width=int(S(16)))   # tira turquesa
        arm = SKIN
    elif traje == "astronauta":
        R(tb, S(90), (236, 238, 244), True)
        R([cx - S(60), fy - S(400), cx + S(60), fy - S(310)], S(16), (90, 96, 110))
        for k, c in enumerate(((255, 80, 80), (255, 210, 60), TURQ)): E([cx - S(40) + k * S(32), fy - S(372), cx - S(18) + k * S(32), fy - S(350)], c)
        R([cx - S(110), fy - S(250), cx + S(110), fy - S(215)], S(14), TURQ)
        arm = (236, 238, 244)
    elif traje == "romano":
        R(tb, S(90), (250, 246, 236), True)
        d.polygon([(cx - S(110), fy - S(450)), (cx + S(20), fy - S(470)), (cx + S(110), fy - S(230)), (cx + S(60), fy - S(220))], fill=(190, 40, 40))
        d.line([(cx - S(90), fy - S(440)), (cx + S(100), fy - S(240))], fill=(210, 170, 60), width=int(S(10)))
        E([cx - S(108), fy - S(462), cx - S(78), fy - S(432)], TURQ)                                     # broche turquesa
        arm = SKIN
    else:  # pirata
        R(tb, S(90), (250, 246, 236), True)
        for k in range(5): d.rectangle([cx - S(100), fy - S(440) + k * S(48), cx + S(100), fy - S(420) + k * S(48)], fill=(40, 60, 120))
        R([cx - S(112), fy - S(280), cx + S(112), fy - S(240)], S(10), TURQ)                              # fajín turquesa
        arm = (250, 246, 236)
    for sx in (-1, 1):
        d.line([(cx + S(sx * 92), fy - S(430)), (cx + S(sx * 140), fy - S(270))], fill=arm, width=int(S(46)))
        E([cx + S(sx * 140 - 30), fy - S(300), cx + S(sx * 140 + 30), fy - S(240)], SKIN)
    if traje == "pirata":
        d.line([(cx + S(140), fy - S(270)), (cx + S(250), fy - S(470))], fill=(200, 205, 215), width=int(S(14)))
        d.line([(cx + S(110), fy - S(300)), (cx + S(170), fy - S(250))], fill=(210, 170, 60), width=int(S(14)))
    if traje == "cavernicola":
        d.line([(cx - S(140), fy - S(270)), (cx - S(200), fy - S(520))], fill=(130, 86, 52), width=int(S(30)))
        E([cx - S(240), fy - S(590), cx - S(160), fy - S(490)], (130, 86, 52))
    # cabeza (fija: identidad de Nico)
    hx, hy, R_ = cx, fy - S(640), S(190)
    for sx in (-1, 1): E([hx + sx * R_ - S(33), hy - S(20), hx + sx * R_ + S(33), hy + S(70)], SKIN)
    if traje == "astronauta":
        lay_r = R_ * 1.42
        d.ellipse([hx - lay_r, hy - lay_r, hx + lay_r, hy + lay_r], fill=(200, 230, 250))
    E([hx - R_, hy - R_, hx + R_, hy + R_], SKIN, True)
    for k in range(7):
        a = math.pi + k * math.pi / 6
        px, py = hx + math.cos(a) * R_ * 0.86, hy + math.sin(a) * R_ * 0.86 - S(10)
        E([px - S(70), py - S(60), px + S(70), py + S(60)], HAIR)
    for ex in (-70, 70):
        E([hx + S(ex - 42), hy - S(40), hx + S(ex + 42), hy + S(60)], (255, 255, 255))
        E([hx + S(ex - 10), hy - S(16), hx + S(ex + 30), hy + S(36)], (24, 18, 26))
        E([hx + S(ex - 2), hy - S(10), hx + S(ex + 12), hy + S(4)], (255, 255, 255))
    for ex in (-100, 100): E([hx + S(ex - 25), hy + S(70), hx + S(ex + 25), hy + S(100)], (240, 140, 140))
    d.chord([hx - S(55), hy + S(60), hx + S(55), hy + S(140)], 0, 180, fill=(120, 30, 40))
    # accesorios de cabeza
    if traje == "romano":
        for k in range(9):
            a = math.pi * 1.05 + k * math.pi * 0.9 / 8
            px, py = hx + math.cos(a) * R_ * 1.02, hy + math.sin(a) * R_ * 1.02 + S(30)
            d.ellipse([px - S(26), py - S(14), px + S(26), py + S(14)], fill=(110, 170, 70))
    if traje == "pirata":
        d.polygon([(hx - S(260), hy - S(110)), (hx, hy - S(330)), (hx + S(260), hy - S(110)), (hx, hy - S(170))], fill=(30, 26, 30))
        d.ellipse([hx - S(30), hy - S(260), hx + S(30), hy - S(200)], fill=TURQ)
        d.ellipse([hx + S(28), hy - S(44), hx + S(112), hy + S(64)], fill=(24, 18, 26)); d.line([(hx - S(150), hy - S(80)), (hx + S(180), hy - S(20))], fill=(24, 18, 26), width=int(S(8)))
    if traje == "cavernicola":
        d.line([(hx + S(40), hy - S(200)), (hx + S(130), hy - S(240))], fill=(250, 246, 230), width=int(S(18)))
        for x in (S(40), S(130)): E([hx + x - S(18), hy - S(200 if x < S(80) else 240) - S(18), hx + x + S(18), hy - S(200 if x < S(80) else 240) + S(18)], (250, 246, 230))
    if traje == "astronauta":
        lay_r = R_ * 1.42
        d.arc([hx - lay_r, hy - lay_r, hx + lay_r, hy + lay_r], 200, 260, fill=(255, 255, 255), width=int(S(16)))
        d.ellipse([hx - lay_r, hy - lay_r, hx + lay_r, hy + lay_r], outline=(90, 96, 110), width=int(S(14)))
        d.rectangle([hx - S(140), hy + lay_r - S(30), hx + S(140), hy + lay_r + S(10)], fill=TURQ)

def tinta(img_rgb, shadow):
    a = np.array(img_rgb).astype(np.float32)
    hsv = cv2.cvtColor(a.astype(np.uint8), cv2.COLOR_RGB2HSV).astype(np.float32); hsv[..., 1] = np.clip(hsv[..., 1] * 1.3, 0, 255)
    a = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB).astype(np.float32)
    Hh, Ww = a.shape[:2]; yy, xx = np.mgrid[0:Hh, 0:Ww]
    dots = (((xx % 12) - 6) ** 2 + ((yy % 12) - 6) ** 2) < 12
    sh = np.array(shadow) > 0
    a[sh] *= 0.86; a[sh & dots] *= 0.6
    lab = np.array(img_rgb).astype(np.int32); key = lab[..., 0] * 65536 + lab[..., 1] * 256 + lab[..., 2]
    e = np.zeros((Hh, Ww), bool); e[:, 1:] |= key[:, 1:] != key[:, :-1]; e[1:, :] |= key[1:, :] != key[:-1, :]
    e = cv2.dilate(e.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0
    a[e] = INK
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))

if __name__ == "__main__":
    trajes = [("sudadera", "CLÁSICO"), ("cavernicola", "EDAD DE PIEDRA"), ("romano", "ROMA"), ("astronauta", "ESPACIO"), ("pirata", "PIRATA")]
    Wd, Hd = 2200, 1250
    img = Image.new("RGB", (Wd, Hd), (250, 214, 120)); d = ImageDraw.Draw(img)
    for k in range(5): d.rectangle([k * 440, 0, (k + 1) * 440, Hd], fill=[(252, 218, 128), (246, 160, 110), (210, 120, 160), (90, 90, 170), (70, 150, 170)][k])
    sh = Image.new("L", (Wd, Hd), 0); dsh = ImageDraw.Draw(sh)
    for k, (t, name) in enumerate(trajes):
        nico(d, dsh, 220 + k * 440, 1080, 0.82, t)
    out = tinta(img, sh)
    d = ImageDraw.Draw(out)
    for k, (t, name) in enumerate(trajes):
        f = font(46); d.text((220 + k * 440 - f.getlength(name) / 2, 1130), name, font=f, fill=(255, 255, 255), stroke_width=7, stroke_fill=INK)
    f = font(70); txt = "NICO · UN MUNDO, UN TRAJE"
    d.text((Wd / 2 - f.getlength(txt) / 2, 30), txt, font=f, fill=(255, 230, 60), stroke_width=10, stroke_fill=INK)
    out.save("nico_vestuario.png"); print("ok")
