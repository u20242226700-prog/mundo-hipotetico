"""Tablero de estilos: la misma escena (Nico le da pizza a un cavernícola frente a la cueva) en 3 estilos."""
import math, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFilter, ImageFont
W, H = 1080, 1920
F = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
def font(s): return ImageFont.truetype(F, int(s))
rng = np.random.default_rng(3)

# ============ A) VECTOR PLANO (tipo infografía animada): formas limpias, sin contorno, sombras de 2 tonos facetadas
def plano(ink=False):
    img = Image.new("RGB", (W, H)); d = ImageDraw.Draw(img)
    ids = Image.new("L", (W, H), 0); di = ImageDraw.Draw(ids)
    shadow = Image.new("L", (W, H), 0); ds = ImageDraw.Draw(shadow)
    nid = [1]
    def poly(pts, col, shade=None, sid=True):
        d.polygon(pts, fill=col)
        if sid: di.polygon(pts, fill=nid[0] % 255 + 1); nid[0] += 7
        if shade: ds.polygon(shade, fill=255)
    def ell(b, col, shade=False, sid=True):
        d.ellipse(b, fill=col)
        if sid: di.ellipse(b, fill=nid[0] % 255 + 1); nid[0] += 7
    # cielo en bandas (posterizado)
    bands = [(28, 36, 92), (58, 52, 120), (120, 70, 130), (196, 96, 112), (240, 140, 100), (252, 190, 120)]
    for k, c in enumerate(bands):
        d.rectangle([0, k * 190, W, (k + 1) * 190 + 2], fill=c)
    d.rectangle([0, 6 * 190, W, H], fill=bands[-1])
    for r, a in ((260, 40), (200, 70), (150, 255)):
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(lay).ellipse([300 - r, 1040 - r, 300 + r, 1040 + r], fill=(255, 236, 170, a))
        img.paste(lay, (0, 0), lay)
    d = ImageDraw.Draw(img)
    # montañas facetadas (lado luz / lado sombra)
    for (x, y, w_, c1, c2) in [(120, 760, 420, (92, 70, 130), (64, 48, 104)), (560, 640, 520, (104, 78, 140), (70, 52, 110)), (980, 780, 400, (92, 70, 130), (64, 48, 104))]:
        poly([(x - w_, 1250), (x, y), (x + w_, 1250)], c1)
        poly([(x, y), (x + w_, 1250), (x + w_ * 0.2, 1250)], c2, sid=False)
        poly([(x, y), (x - w_ * 0.22, y + 150), (x - w_ * 0.05, y + 120), (x + w_ * 0.1, y + 165), (x + w_ * 0.2, y + 135)], (250, 236, 240))
    # volcán
    poly([(700, 1250), (860, 900), (940, 900), (1100, 1250)], (130, 62, 80)); poly([(860, 900), (900, 930), (940, 900)], (255, 120, 60), sid=False)
    # colinas y pinos
    poly([(0, 1300)] + [(x, 1220 - 50 * math.sin(x / 140)) for x in range(0, W + 40, 40)] + [(W, 1300)], (60, 110, 96))
    for k in range(12):
        x = 40 + k * 95 + 20 * math.sin(k); yb = 1240 - 40 * math.sin(x / 140); h = 140 + 30 * math.sin(k * 2)
        poly([(x - 45, yb), (x, yb - h), (x + 45, yb)], (34, 78, 74)); poly([(x, yb - h), (x + 45, yb), (x, yb)], (24, 60, 60), sid=False)
    # suelo
    poly([(0, 1280), (W, 1280), (W, H), (0, H)], (232, 170, 96))
    poly([(0, 1280), (W, 1280), (W, 1330), (0, 1330)], (214, 150, 86), sid=False)
    for k in range(9):
        y = 1360 + k * 70 + k * k * 6
        d.line([(0, y), (W, y)], fill=(222, 160, 90), width=4)
    # cueva (acantilado facetado)
    poly([(0, 380), (300, 520), (420, 900), (470, 1300), (0, 1300)], (150, 96, 92))
    poly([(300, 520), (420, 900), (470, 1300), (330, 1300), (260, 900)], (118, 72, 78), sid=False)
    poly([(60, 1300), (60, 1000), (130, 900), (240, 900), (310, 1000), (310, 1300)], (44, 26, 44))
    ell([110, 1180, 260, 1300], (255, 150, 60))
    # sombras largas proyectadas (luz desde la izquierda/atardecer)
    for (fx, fw) in ((420, 120), (760, 150)):
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(lay).polygon([(fx - fw / 2, 1720), (fx + fw / 2, 1720), (fx + fw / 2 + 380, 1780), (fx - fw / 2 + 330, 1790)], fill=(150, 80, 70, 110))
        img.paste(lay, (0, 0), lay)
    d = ImageDraw.Draw(img)
    # --- Nico (vector): cabeza redonda, pelo en grumos, sudadera turquesa
    def nico(cx, fy, s=1.0):
        S = lambda v: v * s
        poly([(cx - S(50), fy - S(230)), (cx - S(20), fy - S(230)), (cx - S(18), fy), (cx - S(52), fy)], (40, 52, 92))
        poly([(cx + S(20), fy - S(230)), (cx + S(50), fy - S(230)), (cx + S(52), fy), (cx + S(18), fy)], (40, 52, 92))
        ell([cx - S(70), fy - S(24), cx - S(4), fy + S(10)], (30, 30, 40)); ell([cx + S(4), fy - S(24), cx + S(70), fy + S(10)], (30, 30, 40))
        d.rounded_rectangle([cx - S(110), fy - S(470), cx + S(110), fy - S(210)], radius=int(S(90)), fill=(40, 186, 204)); di.rounded_rectangle([cx - S(110), fy - S(470), cx + S(110), fy - S(210)], radius=int(S(90)), fill=nid[0] % 255 + 1); nid[0] += 7
        ds.rounded_rectangle([cx + S(40), fy - S(470), cx + S(110), fy - S(210)], radius=int(S(60)), fill=255)
        d.rounded_rectangle([cx - S(60), fy - S(330), cx + S(60), fy - S(260)], radius=int(S(30)), fill=(30, 150, 170))
        d.line([(cx - S(22), fy - S(450)), (cx - S(22), fy - S(390))], fill=(250, 250, 250), width=int(S(8))); d.line([(cx + S(22), fy - S(450)), (cx + S(22), fy - S(390))], fill=(250, 250, 250), width=int(S(8)))
        # brazo que ofrece
        d.line([(cx + S(90), fy - S(420)), (cx + S(220), fy - S(380))], fill=(40, 186, 204), width=int(S(46)))
        ell([cx + S(195), fy - S(410), cx + S(255), fy - S(350)], (248, 196, 150))
        d.line([(cx - S(90), fy - S(410)), (cx - S(120), fy - S(260))], fill=(40, 186, 204), width=int(S(46)))
        ell([cx - S(150), fy - S(285), cx - S(92), fy - S(228)], (248, 196, 150))
        hx, hy, R = cx, fy - S(640), S(190)
        ell([hx - R - S(26), hy - S(20), hx - R + S(40), hy + S(70)], (248, 196, 150)); ell([hx + R - S(40), hy - S(20), hx + R + S(26), hy + S(70)], (248, 196, 150))
        ell([hx - R, hy - R, hx + R, hy + R], (248, 196, 150))
        ds.ellipse([hx - R, hy - R, hx + R, hy + R], fill=255); ds.ellipse([hx - R - R * 0.28, hy - R - R * 0.2, hx + R - R * 0.28, hy + R - R * 0.2], fill=0)
        for k in range(7):
            a = math.pi + k * math.pi / 6
            px, py = hx + math.cos(a) * R * 0.86, hy + math.sin(a) * R * 0.86 - S(10)
            ell([px - S(70), py - S(60), px + S(70), py + S(60)], (66, 40, 30))
        for ex in (-70, 70):
            ell([hx + S(ex) - S(42), hy + S(10) - S(50), hx + S(ex) + S(42), hy + S(10) + S(50)], (255, 255, 255))
            ell([hx + S(ex) - S(20) + S(10), hy + S(10) - S(26), hx + S(ex) + S(20) + S(10), hy + S(10) + S(26)], (24, 18, 26))
            ell([hx + S(ex) - S(2), hy - S(10), hx + S(ex) + S(12), hy + S(4)], (255, 255, 255))
        ell([hx - S(125), hy + S(70), hx - S(75), hy + S(100)], (240, 140, 140)); ell([hx + S(75), hy + S(70), hx + S(125), hy + S(100)], (240, 140, 140))
        d.chord([hx - S(55), hy + S(60), hx + S(55), hy + S(140)], 0, 180, fill=(120, 30, 40))
        return (cx + S(225), fy - S(400))
    # --- cavernícola (vector)
    def cave(cx, fy, s=1.0):
        S = lambda v: v * s
        poly([(cx - S(60), fy - S(230)), (cx - S(20), fy - S(230)), (cx - S(18), fy), (cx - S(62), fy)], (200, 140, 100))
        poly([(cx + S(20), fy - S(230)), (cx + S(60), fy - S(230)), (cx + S(62), fy), (cx + S(18), fy)], (200, 140, 100))
        ell([cx - S(150), fy - S(560), cx + S(150), fy - S(180)], (206, 124, 58))
        ds.ellipse([cx - S(150), fy - S(560), cx + S(150), fy - S(180)], fill=255); ds.ellipse([cx - S(190), fy - S(590), cx + S(110), fy - S(210)], fill=0)
        for (a, b) in ((-60, -420), (50, -300), (-20, -250), (70, -470)): ell([cx + S(a) - S(20), fy + S(b) - S(14), cx + S(a) + S(20), fy + S(b) + S(14)], (150, 84, 40))
        d.line([(cx - S(130), fy - S(470)), (cx - S(250), fy - S(380))], fill=(206, 150, 108), width=int(S(56)))
        ell([cx - S(285), fy - S(410), cx - S(215), fy - S(345)], (206, 150, 108))
        hx, hy, R = cx, fy - S(690), S(180)
        for k in range(10):
            a = math.pi * 0.9 + k * math.pi * 1.2 / 9
            px, py = hx + math.cos(a) * R, hy + math.sin(a) * R
            ell([px - S(60), py - S(55), px + S(60), py + S(55)], (52, 34, 26))
        ell([hx - R, hy - R, hx + R, hy + R], (206, 150, 108))
        ds.ellipse([hx - R, hy - R, hx + R, hy + R], fill=255); ds.ellipse([hx - R - R * 0.28, hy - R - R * 0.2, hx + R - R * 0.28, hy + R - R * 0.2], fill=0)
        for k in range(8):
            a = math.pi * 0.15 + k * math.pi * 0.7 / 7
            px, py = hx + math.cos(a) * R * 0.85, hy + math.sin(a) * R * 0.85
            ell([px - S(55), py - S(50), px + S(55), py + S(50)], (52, 34, 26))
        d.rounded_rectangle([hx - S(110), hy - S(70), hx + S(110), hy - S(40)], radius=int(S(14)), fill=(52, 34, 26))
        for ex in (-55, 55): ell([hx + S(ex) - S(16), hy - S(30), hx + S(ex) + S(16), hy + S(10)], (24, 18, 26))
        ell([hx - S(45), hy - S(10), hx + S(45), hy + S(70)], (222, 166, 124))
        ell([hx - S(50), hy + S(70), hx + S(50), hy + S(140)], (120, 30, 40))
    nico(760, 1720, 0.9)
    cave(330, 1720, 0.9)
    # pizza en la mano de Nico
    px, py = 760 + 0.9 * 225 - 60, 1720 - 0.9 * 400 - 40
    d.polygon([(px - 120, py), (px + 30, py - 40), (px + 20, py + 60)], fill=(214, 150, 70))
    d.polygon([(px - 100, py + 2), (px + 18, py - 28), (px + 10, py + 46)], fill=(252, 200, 70))
    for (a, b) in ((-40, 0), (0, -10), (-10, 25)): d.ellipse([px + a - 14, py + b - 14, px + a + 14, py + b + 14], fill=(200, 50, 40))
    img_np = np.array(img).astype(np.float32)
    sh = np.array(shadow) > 0
    if not ink:
        img_np[sh] *= np.array([0.78, 0.74, 0.86])
        g = rng.normal(0, 4, (H, W, 1)); img_np = np.clip(img_np + g, 0, 255)
        out = Image.fromarray(img_np.astype(np.uint8))
        return out
    # ============ B) CÓMIC: tinta gruesa + trama de puntos en sombras + colores saturados
    hsv = cv2.cvtColor(img_np.astype(np.uint8), cv2.COLOR_RGB2HSV).astype(np.float32)
    hsv[..., 1] = np.clip(hsv[..., 1] * 1.35, 0, 255)
    img_np = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB).astype(np.float32)
    yy, xx = np.mgrid[0:H, 0:W]
    dots = (((xx % 14) - 7) ** 2 + ((yy % 14) - 7) ** 2) < 16
    img_np[sh & dots] *= 0.45
    lab = np.array(img.convert("RGB")).astype(np.int32)
    key = lab[..., 0] * 65536 + lab[..., 1] * 256 + lab[..., 2]
    edge = np.zeros((H, W), bool)
    edge[:, 1:] |= key[:, 1:] != key[:, :-1]; edge[1:, :] |= key[1:, :] != key[:-1, :]
    edge &= (yy > 1240) | (xx < 480) | True
    ed = cv2.dilate(edge.astype(np.uint8), np.ones((7, 7), np.uint8)) > 0
    img_np[ed] = (18, 12, 20)
    out = Image.fromarray(np.clip(img_np, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(out)
    d.rectangle([0, 0, W - 1, H - 1], outline=(18, 12, 20), width=24)
    f = font(170); txt = "¡ÑAM!"
    lay = Image.new("RGBA", (700, 260), (0, 0, 0, 0)); ImageDraw.Draw(lay).text((30, 20), txt, font=f, fill=(255, 220, 40), stroke_width=16, stroke_fill=(18, 12, 20))
    lay = lay.rotate(-10, expand=True, resample=Image.BICUBIC); out.paste(lay, (300, 300), lay)
    return out

# ============ C) SILUETA OSCURA CON OJOS QUE BRILLAN (diorama 3D al atardecer, estilo de los reels de "stickman 3D")
def sombra_ojos():
    import sys; sys.path.insert(0, "/home/claude/pizza")
    import clay
    from clay import Scene, render, composite, Mat
    from personajes import _arm_pts, N_HOOD, N_HOOD_D, WHITE
    from clay import Rig, CLOTH, GLOSS, EMIT, FLAT
    from escenario import valle, componer, add_light, sombra, fuego
    L = valle(cueva=True)
    bg = componer(L, -40, 0, 1.15)
    bg *= np.array([0.62, 0.55, 0.7])            # hora azul
    add_light(bg, 300, 1500, 300, (255, 150, 60), 0.8)
    add_light(bg, 640, 1500, 520, (255, 130, 50), 0.35)
    img = Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8)).convert("RGBA")
    fuego(img, 560, 1700, 0.9, 1.2)
    BLACK = (20, 20, 24)
    def persona(sc, x, y, s, hood, yaw=0.0, arms=("down", "down"), eyes="happy", t=0.0):
        rig = Rig(sc, x, y, 0, s, yaw)
        for sd in (-1, 1):
            rig.caps((0.12 * sd, 0.7, 0), (0.15 * sd, 0.1, 0.03), 0.055, 0.05, BLACK, GLOSS)
            rig.ell((0.17 * sd, 0.06, 0.08), 0.12, 0.07, 0.17, (30, 30, 36), GLOSS)
        rig.ell((0, 1.02, 0), 0.4, 0.5, 0.34, hood, CLOTH)
        rig.ell((0, 1.42, -0.04), 0.36, 0.14, 0.28, tuple(int(c * 0.8) for c in hood), CLOTH)
        for sd, spec in zip((-1, 1), arms):
            S_, E, Hh = _arm_pts(sd, spec, t, L1=0.38, L2=0.34, sh=(0.33, 1.28, 0.02))
            rig.caps(S_, E, 0.05, 0.05, BLACK, GLOSS); rig.caps(E, Hh, 0.05, 0.05, BLACK, GLOSS)
            rig.sphere(Hh, 0.09, BLACK, GLOSS)
        feats = []
        for sd in (-1, 1):
            if eyes == "happy":
                feats.append((sd * 0.3, 0.06, 0.13, 0.05, 0.0, (255, 250, 230), EMIT, 0.0))
                feats.append((sd * 0.3, 0.02, 0.12, 0.05, 0.0, BLACK, GLOSS, 0.0))
            else:
                feats.append((sd * 0.3, 0.05, 0.11, 0.17, 0.0, (255, 250, 230), EMIT, 0.0))
        sc.head(rig.P((0, 1.95, 0.02)), 0.62 * s, BLACK, Mat(spec=0.9, shin=60, toon=0.4, rim=1.8), yaw, feats)
        return rig
    S = 260
    sc = Scene()
    persona(sc, 760 / S, -1720 / S, 1.0, N_HOOD, yaw=-0.35, arms=("down", "offer"), eyes="happy")
    persona(sc, 330 / S, -1720 / S, 1.15, (196, 110, 50), yaw=0.35, arms=("offer", "down"), eyes="round")
    from personajes import pizza
    pizza(sc, 560 / S, -1270 / S, 0.6, 0.42)
    light = dict(key=clay._n((-0.8, 0.1, 0.6)), key_col=np.array([1.0, 0.62, 0.32], np.float32),
                 rim_col=np.array([0.5, 0.7, 1.0], np.float32), rim_dir=clay._n((0.8, 0.5, 0)),
                 sky=np.array([0.3, 0.32, 0.5], np.float32))
    for x in (330, 760): sombra(img, x, 1720, 130, 0.45)
    composite(img, render(sc, S, 0, 0, W, H, light, outline_px=0.01))
    a = np.array(img.convert("RGB")).astype(np.float32)
    small = cv2.resize(a, (W // 4, H // 4)); br = np.clip((small.mean(2, keepdims=True) - 170) / 85, 0, 1) * small
    a += cv2.resize(cv2.GaussianBlur(br, (0, 0), 8), (W, H)) * 0.6
    yy, xx = np.mgrid[0:H, 0:W]
    vig = 1 - 0.45 * (((xx - W / 2) / W) ** 2 + ((yy - H / 2) / H) ** 2) * 2
    a *= vig[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))

if __name__ == "__main__":
    A = plano(False); B = plano(True); C = sombra_ojos()
    for im, n in ((A, "estilo_A_vector.png"), (B, "estilo_B_comic.png"), (C, "estilo_C_siluetas.png")): im.save(n)
    board = Image.new("RGB", (3 * 540 + 80, 960 + 160), (16, 14, 20)); d = ImageDraw.Draw(board)
    for k, (im, name) in enumerate(((A, "A · VECTOR PLANO"), (B, "B · CÓMIC"), (C, "C · SILUETAS 3D"))):
        board.paste(im.resize((540, 960)), (20 + k * 560, 120))
        f = font(44); d.text((20 + k * 560 + 270 - f.getlength(name) / 2, 40), name, font=f, fill=(255, 220, 60))
    board.save("tablero_estilos.png"); print("ok")
