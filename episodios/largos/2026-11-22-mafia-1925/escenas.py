# -*- coding: utf-8 -*-
"""Escenarios, insertos y personajes de "La Mafia en Nueva York, 1925" (motor/cine.py)."""
import sys, os, math, random
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "motor"))
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFilter
import cine
from cine import (Lienzo, P, mix, shade, font, gradiente, textura, LW, LH, CW, CH, MX, MY, W, H,
                  F_TIT, F_OLD, F_TYPE, F_SUBB, definir_personaje, dibujar_persona, capa_niebla)

cine.PALETA.update(ink=(16, 12, 10), dark=(42, 32, 26), mid=(104, 80, 60), light=(180, 150, 110),
                   paper=(228, 208, 170), red=(168, 30, 26), lamp=(255, 200, 120), cold=(110, 124, 126))

INK, DARK, MID, LIGHT, PAPER, RED, LAMP = P("ink"), P("dark"), P("mid"), P("light"), P("paper"), P("red"), P("lamp")
NOCHE = (30, 32, 34)

# ------------------------------------------------------------------ personajes
definir_personaje("tu", sombrero="gorra", col_sombrero=(92, 74, 58), saco=(120, 96, 72), camisa=(222, 206, 176),
                  mangas_cortas=True, chaleco=(70, 54, 44), pantalon=(76, 60, 48), piel=(214, 168, 124), pelo=(40, 28, 22),
                  mandibula=0.97)
definir_personaje("carmine", sombrero="fedora", col_sombrero=(34, 28, 26), banda=RED, saco=(46, 40, 38), rayas=True,
                  corbata=(160, 28, 24), camisa=(220, 206, 180), ancho=1.15, panza=0.35, bigote=(40, 32, 28), edad=1,
                  piel=(200, 156, 116), mandibula=1.05, cigarro=True)
definir_personaje("frankie", sombrero="fedora_lad", col_sombrero=(110, 100, 90), banda=(30, 24, 22), saco=(128, 118, 104),
                  corbata=(40, 34, 30), ancho=0.92, palillo=True, mandibula=1.08, nariz=1.3, piel=(206, 164, 122))
definir_personaje("pino", gorro_pan=True, mangas_cortas=True, camisa=(230, 222, 204), delantal=(236, 230, 214),
                  pantalon=(70, 58, 50), ancho=1.1, panza=0.4, bigote=(230, 226, 214), cejas=(210, 206, 196),
                  pelo=(220, 216, 206), edad=1, piel=(212, 164, 124), bigote_grande=True)
definir_personaje("izzy", cab=6.3, sombrero="bombin", col_sombrero=(60, 48, 40), saco=(112, 88, 64), corbata=(80, 30, 26),
                  ancho=1.2, panza=0.55, piel=(214, 170, 130), edad=1)
definir_personaje("izzy_pescador", cab=6.3, sombrero="impermeable", col_sombrero=(196, 160, 70), saco=(186, 150, 66),
                  abrigo=True, corbata=None, camisa=(170, 140, 70), ancho=1.2, panza=0.55, piel=(214, 170, 130), edad=1, barba=True)
definir_personaje("izzy_opera", cab=6.3, sombrero=None, pelo=(30, 24, 20), saco=(30, 26, 26), capa=(120, 24, 22),
                  corbata=(230, 220, 200), camisa=(236, 228, 210), ancho=1.2, panza=0.55, piel=(214, 170, 130),
                  bigote=(26, 20, 18), bigote_grande=True, edad=1)
definir_personaje("izzy_lechero", cab=6.3, sombrero="lechero", col_sombrero=(230, 226, 214), saco=(226, 222, 210),
                  corbata=(40, 40, 40), ancho=1.2, panza=0.55, piel=(214, 170, 130), edad=1)
definir_personaje("moe", cab=7.0, sombrero="bombin", col_sombrero=(40, 34, 30), saco=(78, 70, 62), corbata=(30, 26, 24),
                  ancho=1.25, panza=0.6, bigote=(50, 40, 34), piel=(206, 162, 122), edad=1)
definir_personaje("agente", sombrero="fedora", col_sombrero=(30, 28, 28), banda=(20, 18, 18), saco=(54, 52, 50), abrigo=True,
                  corbata=(30, 28, 28), ancho=1.05, mandibula=1.06)

# ------------------------------------------------------------------ ayudas de dibujo
def ladrillos(L, x0, y0, x1, y1, col, esc=1.0, seed=0):
    r = random.Random(seed)
    L.rect(x0, y0, x1, y1, col)
    bh, bw = 26 * esc, 64 * esc
    y = y0; fila = 0
    while y < y1:
        off = (bw / 2) * (fila % 2)
        x = x0 - off
        while x < x1:
            c = shade(col, r.uniform(0.82, 1.08))
            L.rect(max(x0, x + 2), y + 2, min(x1, x + bw - 2), min(y1, y + bh - 2), c)
            x += bw
        y += bh; fila += 1


def tablones(L, x0, y0, x1, y1, col, ancho=60, vertical=True, seed=0):
    r = random.Random(seed)
    if vertical:
        x = x0
        while x < x1:
            L.rect(x, y0, min(x1, x + ancho - 3), y1, shade(col, r.uniform(0.85, 1.05)))
            for k in range(3):
                yy = r.uniform(y0, y1)
                L.line([(x + 8, yy), (x + ancho - 12, yy + r.uniform(-6, 6))], shade(col, 0.75), 2)
            x += ancho
    else:
        y = y0
        while y < y1:
            L.rect(x0, y, x1, min(y1, y + ancho - 3), shade(col, r.uniform(0.85, 1.05)))
            y += ancho


def resplandor(img, x, y, r, col, a=0.6):
    """Brillo radial aditivo-ish sobre una capa RGBA."""
    g = Image.new("RGBA", (int(2 * r), int(2 * r)), (0, 0, 0, 0))
    arr = np.zeros((int(2 * r), int(2 * r), 4), np.uint8)
    yy, xx = np.mgrid[0:int(2 * r), 0:int(2 * r)]
    d = np.sqrt((xx - r) ** 2 + (yy - r) ** 2) / r
    al = np.clip(1 - d, 0, 1) ** 2 * 255 * a
    arr[..., :3] = col; arr[..., 3] = al.astype(np.uint8)
    g = Image.fromarray(arr, "RGBA")
    img.alpha_composite(g, (int(x - r), int(y - r)))


def edificio(L, x, w, ytop, ybot, col, seed=0, noche=False, escalera=True):
    r = random.Random(seed)
    L.rect(x, ytop, x + w, ybot, col, INK, 3)
    L.rect(x - 8, ytop - 18, x + w + 8, ytop, shade(col, 0.7), INK, 3)   # cornisa
    cols = max(2, int(w / 110))
    filas = int((ybot - ytop - 160) / 120)
    for i in range(cols):
        for j in range(filas):
            wx = x + 30 + i * (w - 60) / cols; wy = ytop + 50 + j * 120
            lit = noche and r.random() < 0.35
            c = (LAMP if lit else shade(col, 0.45)) if noche else shade(col, 0.5 if r.random() < .7 else 0.35)
            L.rect(wx, wy, wx + (w - 60) / cols - 34, wy + 72, c, INK, 2)
            L.rect(wx - 4, wy + 72, wx + (w - 60) / cols - 30, wy + 80, shade(col, 0.8))
    if escalera:
        ex = x + w * 0.55
        for j in range(filas):
            wy = ytop + 130 + j * 120
            L.rect(ex - 80, wy, ex + 80, wy + 6, INK)
            for k in range(7):
                L.line([(ex - 80 + k * 26, wy), (ex - 80 + k * 26, wy - 30)], INK, 2)
            L.line([(ex - 80, wy - 30), (ex + 80, wy - 30)], INK, 2)
            L.line([(ex + 40, wy), (ex - 40, wy + 114)], INK, 3)


def farol(L, x, ybase, h=520, col=INK):
    L.rect(x - 7, ybase - h, x + 7, ybase, col)
    L.rect(x - 16, ybase - 20, x + 16, ybase, col)
    L.line([(x, ybase - h), (x + 50, ybase - h - 20), (x + 70, ybase - h)], col, 6)
    L.poly([(x + 52, ybase - h), (x + 88, ybase - h), (x + 80, ybase - h + 40), (x + 60, ybase - h + 40)], LAMP, INK, 3)


def carreta(L, x, y, s=1.0, carga="fruta"):
    L.poly([(x - 150 * s, y - 120 * s), (x + 150 * s, y - 120 * s), (x + 140 * s, y - 40 * s), (x - 140 * s, y - 40 * s)], (120, 88, 56), INK, 3)
    for k in range(5):
        L.line([(x - 140 * s, y - 120 * s + k * 18 * s), (x + 140 * s, y - 120 * s + k * 18 * s)], (90, 64, 42), 2)
    L.ell(x - 90 * s, y - 30 * s, 34 * s, 34 * s, DARK, INK, 3)
    L.ell(x + 90 * s, y - 30 * s, 34 * s, 34 * s, DARK, INK, 3)
    L.line([(x + 150 * s, y - 100 * s), (x + 260 * s, y - 140 * s)], INK, 6)
    if carga == "fruta":
        for k in range(12):
            L.ell(x - 125 * s + k * 22 * s, y - 132 * s, 13 * s, 13 * s, (170, 60, 40) if k % 3 else (190, 150, 60), INK, 2)
    else:
        for k in range(3):
            L.rect(x - 130 * s + k * 90 * s, y - 200 * s, x - 50 * s + k * 90 * s, y - 120 * s, (150, 112, 70), INK, 3)


def ropa_tendida(L, x0, x1, y, seed=0):
    r = random.Random(seed)
    L.line([(x0, y), ((x0 + x1) / 2, y + 40), (x1, y)], INK, 2)
    x = x0 + 40
    while x < x1 - 60:
        t = (x - x0) / (x1 - x0)
        yy = y + 160 * t * (1 - t)
        w = r.uniform(40, 80); h = r.uniform(50, 110)
        L.rect(x, yy, x + w, yy + h, r.choice([PAPER, LIGHT, (160, 140, 110), (150, 60, 50)]), INK, 2)
        x += w + r.uniform(20, 60)


def caja(L, x, y, w, h, col=(140, 104, 66), txt=None):
    L.rect(x, y, x + w, y + h, col, INK, 3)
    for k in range(1, 4):
        L.line([(x, y + k * h / 4), (x + w, y + k * h / 4)], shade(col, 0.7), 2)
    L.line([(x, y), (x + w, y + h)], shade(col, 0.75), 4)
    if txt:
        L.text((x + w / 2, y + h / 2), txt, font(F_TIT, int(h * 0.22)), shade(col, 0.45))


def silueta_skyline(L, y, col, seed=0, alto=1.0):
    r = random.Random(seed)
    x = -20
    while x < LW:
        w = r.uniform(60, 160); h = r.uniform(80, 320) * alto
        L.rect(x, y - h, x + w, y + 10, col)
        if r.random() < 0.2:
            L.poly([(x + w * 0.3, y - h), (x + w * 0.5, y - h - 90 * alto), (x + w * 0.7, y - h)], col)
        x += w + r.uniform(-10, 10)


def mar(L, y0, y1, top, bot, seed=0, brillo=None):
    img = gradiente(LW, int(y1 - y0), top, bot)
    L.img.paste(img.resize((LW * L.ss, int(y1 - y0) * L.ss)), (0, int(y0 * L.ss)))
    r = random.Random(seed)
    for k in range(160):
        yy = r.uniform(y0 + 10, y1); t = (yy - y0) / (y1 - y0)
        xx = r.uniform(0, LW); w = 20 + 140 * t
        L.line([(xx, yy), (xx + w, yy)], shade(bot, 1.15) if brillo is None else brillo, 1 + 3 * t)


def capa(L, textur=6, seed=0):
    img = L.final()
    if textur:
        img = textura(img, textur, 3, seed)
    return img


def vacia():
    return Lienzo(LW, LH)


# ------------------------------------------------------------------ escenarios
def _almacen():
    F = Lienzo(LW, LH, DARK)
    ladrillos(F, 0, 0, LW, LH, (60, 46, 38), 1.3, 3)
    # ventana alta con lluvia
    F.rect(1500, 160, 2000, 560, (96, 108, 110), INK, 10)
    for k in range(1, 4):
        F.line([(1500 + k * 125, 160), (1500 + k * 125, 560)], INK, 8)
    F.line([(1500, 360), (2000, 360)], INK, 8)
    f = capa(F, 8, 1)
    # haz de luz
    hz = Image.new("RGBA", (LW, LH)); d = ImageDraw.Draw(hz)
    d.polygon([(1500, 560), (2000, 560), (1500, LH), (700, LH)], fill=(170, 180, 175, 40))
    hz = hz.filter(ImageFilter.GaussianBlur(30))
    f.alpha_composite(hz)
    M = vacia()
    for i, (x, y, w, h) in enumerate([(100, 700, 300, 230), (130, 470, 260, 230), (420, 760, 280, 210), (2060, 640, 300, 290),
                                      (2100, 380, 260, 260), (1760, 800, 280, 200)]):
        caja(M, x, y, w, h, (120 + i * 6, 90, 60), "PANE" if i % 2 else "OLIO")
    M.rect(0, 1010, LW, LH, (50, 40, 34))
    m = capa(M, 6, 2)
    N = vacia()
    caja(N, -60, 860, 420, 380, (90, 66, 44))
    caja(N, 2240, 900, 420, 360, (84, 62, 42))
    return [(f, 0.3), (m, 0.6), (N.final(), 1.25)]


def _puerta_almacen():
    F = Lienzo(LW, LH, DARK)
    ladrillos(F, 0, 0, LW, LH, (56, 44, 36), 1.6, 4)
    F.rect(700, 40, 1850, 1300, INK)
    tablones(F, 730, 60, 1820, 1290, (98, 74, 50), 110, True, 5)
    for yy in (260, 1050):
        F.rect(730, yy, 1820, yy + 40, (70, 54, 40), INK, 3)
    F.ell(1700, 700, 26, 26, (150, 130, 90), INK, 4)
    f = capa(F, 8, 3)
    return [(f, 0.6)]


def _negro():
    F = Lienzo(LW, LH, (10, 8, 8), 1)
    return [(F.final(), 0.0)]


def _barco():
    F = Lienzo(LW, LH)
    F.img.paste(gradiente(LW * 2, LH * 2, (150, 140, 120), (210, 196, 166)))
    silueta_skyline(F, 640, (140, 128, 110), 7, 0.7)
    f = capa(F, 4, 7)
    M = vacia()
    mar(M, 640, LH, (120, 112, 98), (70, 62, 52), 3)
    m = capa(M, 4, 8)
    N = vacia()
    N.rect(0, 980, LW, LH, (80, 62, 46), INK, 4)
    N.rect(0, 900, LW, 920, (60, 46, 36), INK, 3)
    for x in range(0, LW, 120):
        N.rect(x, 900, x + 14, 990, (60, 46, 36), INK, 2)
    N.line([(400, 0), (520, 980)], INK, 10)
    N.line([(520, 200), (980, 980)], INK, 3)
    return [(f, 0.2), (m, 0.45), (N.final(), 1.0)]


def _estatua():
    F = Lienzo(LW, LH)
    F.img.paste(gradiente(LW * 2, LH * 2, (170, 156, 128), (220, 204, 170)))
    resplandor(F.img, 1500 * 2, 380 * 2, 500, (255, 236, 190), 0.55)
    f = capa(F, 4, 9)
    M = vacia()
    c = (70, 66, 58)
    cx = 1300
    _p, _e, _l = M.poly, M.ell, M.line
    T = lambda x, y: (cx + (x - cx) * 0.7, 900 - (900 - y) * 0.7)
    M.poly = lambda pts, *a, **k: _p([T(*q) for q in pts], *a, **k)
    M.ell = lambda x, y, rx, ry, *a, **k: _e(*T(x, y), rx * 0.7, ry * 0.7, *a, **k)
    M.line = lambda pts, col, w: _l([T(*q) for q in pts], col, w * 0.7)
    M.poly([(cx - 260, 900), (cx + 260, 900), (cx + 200, 760), (cx - 200, 760)], c)            # pedestal base
    M.poly([(cx - 150, 760), (cx + 150, 760), (cx + 120, 520), (cx - 120, 520)], c)
    M.poly([(cx - 140, 500), (cx + 140, 500), (cx + 140, 525), (cx - 140, 525)], c)
    M.poly([(cx - 70, 500), (cx + 70, 500), (cx + 55, 250), (cx + 30, 200), (cx - 35, 200), (cx - 60, 260)], c)  # túnica
    M.ell(cx, 175, 32, 38, c)
    for a in range(-60, 61, 24):
        ra = math.radians(a - 90)
        M.line([(cx, 160), (cx + math.cos(ra) * 75, 160 + math.sin(ra) * 75)], c, 9)
    M.poly([(cx + 30, 230), (cx + 60, 220), (cx + 110, 40), (cx + 85, 30)], c)                    # brazo
    M.poly([(cx + 80, 40), (cx + 120, 40), (cx + 112, 0), (cx + 88, 0)], c)
    M.ell(cx + 100, -15, 18, 26, (255, 210, 140))
    M.poly([(cx - 60, 300), (cx - 20, 300), (cx - 30, 380), (cx - 75, 370)], shade(c, 0.8))
    M.poly, M.ell, M.line = _p, _e, _l
    M.rect(0, 880, LW, 905, (80, 74, 64))
    mar(M, 900, LH, (130, 120, 100), (80, 72, 60), 5)
    return [(f, 0.1), (capa(M, 3, 10), 0.4)]


def _ellis():
    F = Lienzo(LW, LH, (150, 128, 98))
    for i in range(5):
        x = 140 + i * 480
        F.rect(x, 120, x + 300, 720, (210, 190, 150), INK, 6)
        F.chord(x + 150, 120, 150, 110, 180, 360, (210, 190, 150))
        F.line([(x + 150, 20), (x + 150, 720)], INK, 4)
        for k in range(1, 5):
            F.line([(x, 120 + k * 120), (x + 300, 120 + k * 120)], INK, 3)
    ladrillos(F, 0, 760, LW, 900, (130, 100, 76), 1.2, 11)
    F.rect(0, 900, LW, LH, (96, 80, 62))
    for k in range(-20, 30):
        F.line([(k * 120, 900), (k * 120 - 300, LH)], (84, 70, 54), 3)
    f = capa(F, 8, 11)
    hz = Image.new("RGBA", (LW, LH)); d = ImageDraw.Draw(hz)
    for i in range(5):
        x = 140 + i * 480
        d.polygon([(x, 120), (x + 300, 120), (x + 600, LH), (x + 200, LH)], fill=(255, 240, 200, 28))
    f.alpha_composite(hz.filter(ImageFilter.GaussianBlur(24)))
    N = vacia()
    for x in range(0, LW, 260):
        N.rect(x, 940, x + 12, 1100, (60, 50, 40), INK, 2)
    N.rect(0, 940, LW, 956, (70, 58, 46), INK, 2)
    return [(f, 0.35), (N.final(), 1.15)]


def _mulberry(noche=False):
    sky = ((40, 42, 46), (70, 66, 60)) if noche else ((196, 176, 136), (226, 206, 168))
    F = Lienzo(LW, LH)
    F.img.paste(gradiente(LW * 2, LH * 2, *sky))
    fc = (60, 56, 52) if noche else (156, 132, 100)
    for i in range(6):
        edificio(F, 760 + i * 180, 170, 260 + (i % 3) * 40, 900, shade(fc, 1.0 + 0.05 * i), i, noche, False)
    f = capa(F, 5, 12)
    M = vacia()
    lc = (70, 56, 46) if noche else (128, 92, 68)
    rc = (60, 48, 40) if noche else (112, 84, 62)
    edificio(M, -40, 760, 40, 960, lc, 21, noche)
    edificio(M, 1800, 800, 60, 960, rc, 22, noche)
    ropa_tendida(M, 720, 1800, 300, 3)
    ropa_tendida(M, 720, 1800, 520, 4)
    # tienda: panadería
    M.rect(80, 700, 700, 960, (90, 66, 48), INK, 4)
    M.poly([(60, 640), (720, 640), (760, 720), (40, 720)], RED, INK, 4)
    for k in range(8):
        M.poly([(60 + k * 82, 640), (101 + k * 82, 640), (101 + k * 82 + 6, 720), (60 + k * 82 + 6, 720)], (226, 210, 180) if k % 2 else RED)
    M.text((390, 600), "PANETTERIA PINO", font(F_TIT, 52), PAPER, stroke=3, stroke_fill=INK)
    M.rect(130, 750, 650, 930, LAMP if noche else (150, 140, 120), INK, 4)
    M.rect(0, 960, LW, LH, (58, 50, 44) if noche else (120, 100, 78))
    for k in range(-10, 40):
        M.line([(k * 90, 960), (k * 90 - 200, LH)], (50, 44, 38) if noche else (104, 86, 66), 2)
    if noche:
        farol(M, 760, 980); farol(M, 1880, 980)
    m = capa(M, 6, 13)
    if noche:
        for x in (848, 1968):
            resplandor(m, x, 480, 230, LAMP, 0.45)
            resplandor(m, x, 1100, 160, LAMP, 0.25)
    N = vacia()
    if not noche:
        carreta(N, 1500, 1180, 1.6)
    return [(f, 0.3), (m, 0.65), (N.final(), 1.2)]


def _panaderia(final=False):
    F = Lienzo(LW, LH, (96, 70, 50))
    ladrillos(F, 0, 0, LW, LH, (110, 78, 56), 1.1, 15)
    # horno
    F.rect(140, 260, 900, 1000, (90, 62, 46), INK, 6)
    ladrillos(F, 150, 270, 890, 990, (130, 86, 58), 0.9, 16)
    F.chord(520, 760, 260, 230, 180, 360, INK)
    F.rect(260, 760, 780, 900, INK)
    F.chord(520, 790, 220, 180, 180, 360, (255, 140, 50))
    F.rect(300, 790, 740, 880, (255, 150, 60))
    for k in range(9):
        F.ell(340 + k * 48, 850, 26, 18, (255, 200, 90))
    # estantes de pan
    for j in range(4):
        y = 260 + j * 170
        F.rect(1150, y, 2100, y + 16, (70, 50, 36), INK, 3)
        for k in range(9):
            F.ell(1200 + k * 100, y - 30, 44, 30, (196, 140, 72), INK, 3)
            F.line([(1185 + k * 100, y - 40), (1205 + k * 100, y - 20)], (240, 200, 140), 4)
    # ventana
    F.rect(2180, 200, 2520, 700, (200, 186, 150) if not final else (250, 220, 160), INK, 8)
    F.line([(2350, 200), (2350, 700)], INK, 6)
    f = capa(F, 7, 15)
    resplandor(f, 520, 820, 520, (255, 150, 60), 0.5)
    if final:
        resplandor(f, 2350, 450, 600, (255, 220, 150), 0.5)
    N = vacia()
    N.rect(-20, 1010, LW + 20, LH, (88, 62, 44), INK, 5)
    N.rect(-20, 990, LW + 20, 1030, (120, 86, 60), INK, 4)
    for k in range(5):
        N.ell(1500 + k * 120, 990, 50, 26, (200, 146, 78), INK, 3)
    N.ell(500, 995, 110, 30, (236, 230, 214), INK, 3)   # harina
    return [(f, 0.4), (N.final(), 1.2)]


def _callejon():
    F = Lienzo(LW, LH, NOCHE)
    F.img.paste(gradiente(LW * 2, LH * 2, (24, 24, 26), (54, 50, 46)))
    ladrillos(F, 0, 0, 900, 1000, (62, 46, 40), 1.2, 17)
    ladrillos(F, 1650, 0, LW, 1000, (56, 42, 36), 1.2, 18)
    F.poly([(900, 0), (1100, 200), (1100, 900), (900, 1000)], (40, 34, 30))
    F.poly([(1650, 0), (1450, 200), (1450, 900), (1650, 1000)], (36, 30, 26))
    F.rect(1100, 200, 1450, 900, (70, 66, 60))
    F.rect(0, 1000, LW, LH, (36, 34, 32))
    for k in range(6):
        F.ell(600 + k * 260, 1150 + (k % 2) * 60, 120, 18, (80, 78, 74))
    farol(F, 1300, 900, 420)
    f = capa(F, 8, 17)
    resplandor(f, 1388, 490, 260, LAMP, 0.5)
    N = vacia()
    for j in range(4):
        y = 120 + j * 230
        N.rect(0, y, 520, y + 8, INK)
        for k in range(11):
            N.line([(k * 48, y), (k * 48, y - 40)], INK, 3)
        N.line([(0, y - 40), (520, y - 40)], INK, 3)
        N.line([(420, y), (180, y + 222)], INK, 5)
    N.rect(2100, 820, 2350, 1060, (50, 50, 48), INK, 4)  # bote de basura
    N.ell(2225, 820, 125, 26, (64, 64, 60), INK, 4)
    return [(f, 0.35), (N.final(), 1.15)]


def _oficina():
    F = Lienzo(LW, LH, (50, 38, 30))
    tablones(F, 0, 0, LW, LH, (70, 52, 40), 90, True, 19)
    F.rect(1650, 150, 2250, 760, (150, 140, 120), INK, 10)  # ventana
    F.rect(500, 220, 820, 520, (90, 70, 50), INK, 8)        # cuadro
    F.ell(660, 340, 60, 70, (60, 46, 36))
    F.rect(560, 420, 760, 500, (60, 46, 36))
    F.rect(240, 560, 470, 1000, (40, 38, 36), INK, 6)       # caja fuerte
    F.ell(355, 740, 50, 50, (90, 86, 80), INK, 5)
    f = capa(F, 6, 19)
    N = vacia()
    N.rect(600, 960, 1950, LH + 20, (60, 40, 28), INK, 6)    # escritorio
    N.rect(560, 930, 1990, 975, (84, 56, 38), INK, 5)
    N.poly([(1600, 930), (1640, 760), (1760, 760), (1800, 930)], (40, 60, 40), INK, 4)  # lámpara
    N.rect(1690, 700, 1710, 760, INK)
    N.rect(820, 900, 1000, 935, PAPER, INK, 3)
    N.rect(1100, 880, 1180, 935, (60, 80, 50), INK, 3)       # botella
    n = N.final()
    resplandor(n, 1700, 900, 380, LAMP, 0.5)
    return [(f, 0.35), (n, 1.25)]


def _puerta_speak():
    F = Lienzo(LW, LH, NOCHE)
    ladrillos(F, 0, 0, LW, LH, (64, 48, 40), 1.3, 20)
    F.rect(950, 260, 1600, 1100, INK)
    tablones(F, 975, 280, 1575, 1100, (80, 58, 40), 100, True, 21)
    F.rect(1200, 520, 1350, 570, (40, 30, 24), INK, 4)
    F.rect(1050, 150, 1500, 240, (40, 34, 30), INK, 4)
    F.text((1275, 195), "LAVANDERIA", font(F_TIT, 56), LIGHT)
    for k in range(7):                                        # escalones
        F.rect(600 - k * 60, 1100 + k * 30, 1950 + k * 60, 1130 + k * 30, (70, 64, 58), INK, 3)
    f = capa(F, 7, 20)
    resplandor(f, 1275, 120, 300, LAMP, 0.45)
    return [(f, 0.5)]


def _speakeasy(escenario=False):
    F = Lienzo(LW, LH, (60, 36, 28))
    tablones(F, 0, 0, LW, LH, (84, 52, 38), 70, True, 22)
    # escenario con telón
    F.rect(1500 if not escenario else 500, 200, 2450 if not escenario else 2050, 900, (110, 22, 20), INK, 6)
    x0 = 1500 if not escenario else 500; x1 = 2450 if not escenario else 2050
    for k in range(int((x1 - x0) / 60)):
        F.line([(x0 + k * 60, 200), (x0 + k * 60 + 10, 900)], (80, 14, 14), 6)
    F.rect(x0 - 40, 860, x1 + 40, 940, (60, 40, 30), INK, 4)
    if not escenario:
        # banda en silueta
        for i, x in enumerate((1650, 1900, 2200)):
            F.ell(x, 560, 34, 40, INK)
            F.poly([(x - 60, 860), (x - 50, 610), (x + 50, 610), (x + 60, 860)], INK)
        F.line([(1900, 630), (1990, 560)], (200, 170, 90), 10)    # trompeta
        F.rect(2100, 700, 2330, 860, INK)                             # piano
        # barra
        F.rect(0, 380, 1300, 420, (90, 60, 40), INK, 4)
        for k in range(22):
            F.rect(40 + k * 56, 300, 70 + k * 56, 378, [(70, 90, 60), (110, 60, 30), (150, 120, 60)][k % 3], INK, 2)
        F.rect(0, 760, 1300, 1000, (70, 44, 30), INK, 6)
        F.rect(0, 730, 1340, 770, (110, 74, 48), INK, 5)
    F.rect(0, 1000, LW, LH, (50, 34, 26))
    for k in range(-5, 40):
        F.line([(k * 80, 1000), (k * 80 - 120, LH)], (60, 40, 30), 3)
    f = capa(F, 7, 22)
    for x in range(200, LW, 500):
        resplandor(f, x, 160, 260, LAMP, 0.45)
    return [(f, 0.4)]


def _cuarto():
    F = Lienzo(LW, LH, (40, 34, 30))
    tablones(F, 0, 0, LW, LH, (58, 46, 38), 120, True, 23)
    F.rect(1500, 180, 2000, 700, (80, 92, 96), INK, 10)
    F.line([(1750, 180), (1750, 700)], INK, 8); F.line([(1500, 440), (2000, 440)], INK, 8)
    F.rect(200, 760, 1200, 1000, (150, 136, 112), INK, 5)      # cama
    F.rect(200, 640, 260, 1000, (70, 54, 40), INK, 4)
    F.rect(240, 720, 520, 800, PAPER, INK, 4)
    F.rect(0, 1000, LW, LH, (50, 40, 32))
    f = capa(F, 7, 23)
    hz = Image.new("RGBA", (LW, LH)); d = ImageDraw.Draw(hz)
    d.polygon([(1500, 700), (2000, 700), (1600, LH), (900, LH)], fill=(150, 170, 170, 34))
    f.alpha_composite(hz.filter(ImageFilter.GaussianBlur(26)))
    return [(f, 0.4)]


def _muelle(amanecer=False):
    sky = ((210, 160, 110), (236, 210, 170)) if amanecer else ((24, 26, 30), (60, 58, 54))
    F = Lienzo(LW, LH)
    F.img.paste(gradiente(LW * 2, LH * 2, *sky))
    if amanecer:
        resplandor(F.img, 1800 * 2, 640 * 2, 700, (255, 220, 160), 0.6)
    silueta_skyline(F, 640, (110, 90, 74) if amanecer else (34, 34, 36), 30, 0.9)
    f = capa(F, 4, 24)
    M = vacia()
    mar(M, 640, LH, (150, 120, 90) if amanecer else (40, 44, 46), (90, 70, 54) if amanecer else (22, 24, 26), 6)
    m = capa(M, 4, 25)
    N = vacia()
    wc = (110, 84, 60) if amanecer else (60, 48, 40)
    N.poly([(0, 860), (LW, 820), (LW, LH), (0, LH)], wc, INK, 4)
    for k in range(40):
        N.line([(k * 70, 860 - k * 1.5), (k * 70 - 90, LH)], shade(wc, 0.7), 3)
    for x in (120, 760, 1500, 2300):
        N.rect(x, 640, x + 46, 900, shade(wc, 0.6), INK, 4)
        N.ell(x + 23, 640, 23, 9, shade(wc, 0.8), INK, 3)
    caja(N, 1750, 690, 200, 160, (130, 96, 62)); caja(N, 1960, 720, 170, 130, (124, 92, 60))
    caja(N, 1820, 560, 170, 130, (120, 88, 58))
    if not amanecer:
        farol(N, 900, 860, 460)
    n = N.final()
    if not amanecer:
        resplandor(n, 988, 400, 250, LAMP, 0.45)
    return [(f, 0.15), (m, 0.4), (n, 1.0)]


def _bote():
    F = Lienzo(LW, LH)
    F.img.paste(gradiente(LW * 2, LH * 2, (18, 20, 24), (44, 46, 48)))
    F.ell(1900, 260, 70, 70, (200, 196, 176))
    f = capa(F, 3, 26)
    M = vacia()
    mar(M, 560, LH, (40, 44, 46), (16, 18, 20), 7, (70, 76, 76))
    m = capa(M, 3, 27)
    N = vacia()
    N.poly([(-40, 900), (LW + 40, 900), (LW + 40, LH), (-40, LH)], (50, 40, 32), INK, 6)
    N.poly([(-40, 860), (LW + 40, 860), (LW + 40, 920), (-40, 920)], (80, 62, 46), INK, 5)
    for k in range(4):
        caja(N, 1700 + k * 150, 760 - (k % 2) * 40, 150, 110, (110, 82, 54))
    return [(f, 0.1), (m, 0.5), (N.final(), 1.1)]


def _mar_noche():
    F = Lienzo(LW, LH)
    F.img.paste(gradiente(LW * 2, LH * 2, (14, 16, 20), (40, 42, 44)))
    F.ell(600, 220, 60, 60, (190, 186, 166))
    for k in range(9):    # barcos en fila en el horizonte
        x = 300 + k * 250
        F.poly([(x - 80, 610), (x + 80, 610), (x + 60, 640), (x - 60, 640)], (12, 12, 14))
        F.rect(x - 4, 520, x + 4, 612, (12, 12, 14))
        F.rect(x - 30, 585, x + 20, 612, (12, 12, 14))
        F.ell(x + 30, 598, 4, 4, LAMP)
    f = capa(F, 3, 28)
    M = vacia()
    mar(M, 640, LH, (34, 38, 40), (12, 14, 16), 8, (60, 64, 66))
    return [(f, 0.15), (capa(M, 3, 29), 0.5)]


def _oficina_federal():
    F = Lienzo(LW, LH, (120, 104, 80))
    F.rect(0, 0, LW, 620, (150, 132, 102))
    F.rect(0, 620, LW, 650, (90, 72, 54))
    tablones(F, 0, 650, LW, LH, (100, 80, 60), 60, True, 30)
    F.rect(400, 120, 1100, 230, (60, 50, 40), INK, 4)
    F.text((750, 175), "PROHIBITION BUREAU", font(F_TIT, 60), PAPER)
    for k in range(4):
        F.rect(1400 + k * 200, 200, 1560 + k * 200, 420, PAPER, INK, 3)
        F.text((1480 + k * 200, 240), "WANTED", font(F_TIT, 30), INK)
        F.ell(1480 + k * 200, 320, 40, 46, MID)
    for k in range(3):
        F.rect(150 + k * 220, 500, 340 + k * 220, 1000, (80, 84, 80), INK, 4)
        for j in range(4):
            F.rect(170 + k * 220, 530 + j * 115, 320 + k * 220, 620 + j * 115, (96, 100, 96), INK, 3)
    f = capa(F, 6, 30)
    return [(f, 0.4)]


def _calle_lluvia():
    F = Lienzo(LW, LH)
    F.img.paste(gradiente(LW * 2, LH * 2, (20, 22, 26), (50, 48, 46)))
    edificio(F, -40, 900, 80, 940, (50, 44, 40), 31, True)
    edificio(F, 1700, 900, 40, 940, (46, 40, 36), 32, True)
    F.rect(860, 380, 1720, 940, (60, 50, 42), INK, 4)
    F.rect(1100, 560, 1480, 940, (40, 30, 24), INK, 4)
    F.text((1290, 470), "MAGAZZINO", font(F_TIT, 64), (150, 130, 100))
    F.rect(0, 940, LW, LH, (34, 34, 34))
    for k in range(10):
        F.line([(k * 300, 1000 + k % 3 * 50), (k * 300 + 200, 1000 + k % 3 * 50)], (90, 86, 76), 4)
    farol(F, 700, 960); farol(F, 1850, 960)
    # auto de los años 20
    F.poly([(200, 1080), (260, 960), (520, 930), (640, 960), (760, 980), (780, 1080)], (24, 24, 24), INK, 4)
    F.ell(320, 1090, 55, 55, INK); F.ell(680, 1090, 55, 55, INK)
    F.ell(765, 1000, 20, 16, LAMP)
    f = capa(F, 6, 31)
    for x in (788, 1938):
        resplandor(f, x, 460, 240, LAMP, 0.45)
        resplandor(f, x, 1150, 200, LAMP, 0.25)
    resplandor(f, 790, 1000, 160, LAMP, 0.5)
    return [(f, 0.4)]


def _carcel():
    F = Lienzo(LW, LH, (80, 74, 66))
    ladrillos(F, 0, 0, LW, LH, (96, 88, 78), 1.4, 33)
    F.rect(1650, 200, 1950, 420, (200, 196, 180), INK, 8)
    for k in range(5):
        F.line([(1660 + k * 70, 200), (1660 + k * 70, 420)], INK, 10)
    F.rect(200, 760, 1100, 880, (70, 64, 58), INK, 5)
    F.rect(0, 1000, LW, LH, (60, 56, 50))
    f = capa(F, 7, 33)
    hz = Image.new("RGBA", (LW, LH)); d = ImageDraw.Draw(hz)
    d.polygon([(1650, 420), (1950, 420), (1500, LH), (900, LH)], fill=(230, 220, 190, 34))
    f.alpha_composite(hz.filter(ImageFilter.GaussianBlur(20)))
    N = vacia()
    for k in range(13):
        N.rect(60 + k * 200, -20, 96 + k * 200, LH + 20, (30, 28, 26), INK, 4)
    N.rect(0, 120, LW, 160, (30, 28, 26), INK, 4)
    return [(f, 0.35), (N.final(), 1.3)]


def _panaderia_final():
    F = Lienzo(LW, LH)
    F.img.paste(gradiente(LW * 2, LH * 2, (220, 190, 140), (240, 220, 180)))
    edificio(F, -60, 800, 60, 980, (150, 112, 84), 40, False)
    edificio(F, 1800, 800, 100, 980, (138, 104, 78), 41, False)
    F.rect(700, 300, 1850, 980, (170, 130, 96), INK, 5)
    F.rect(760, 420, 1790, 520, (40, 30, 24), INK, 5)
    F.text((1275, 470), "PANADERÍA PINO", font(F_TIT, 76), (230, 200, 120))
    F.poly([(720, 540), (1830, 540), (1880, 640), (670, 640)], RED, INK, 4)
    for k in range(13):
        F.poly([(720 + k * 85, 540), (762 + k * 85, 540), (768 + k * 85, 640), (726 + k * 85, 640)], PAPER if k % 2 else RED)
    F.rect(780, 680, 1500, 940, (240, 210, 150), INK, 6)
    for k in range(7):
        F.ell(840 + k * 95, 880, 40, 26, (196, 140, 72), INK, 3)
    F.rect(1560, 660, 1760, 980, (80, 56, 40), INK, 5)
    F.rect(0, 980, LW, LH, (150, 126, 96))
    f = capa(F, 6, 40)
    resplandor(f, 1900, 200, 700, (255, 230, 170), 0.5)
    return [(f, 0.4)]


# ------------------------------------------------------------------ insertos de pantalla completa
def _papel(seed=0):
    F = Lienzo(LW, LH, (40, 32, 26), 1)
    p = Lienzo(1700, 1150, (226, 214, 184), 1)
    img = textura(p.final(), 10, 2, seed)
    F.img.paste(img, (430, 110))
    return F


def _periodico(ins):
    F = _periodico_base(ins)
    return [(textura(F.final(), 5, 3, 50), 0.5)]


PERIODICOS = {
    "periodico_ley_seca": ("NEW YORK DAILY", "JANUARY 17, 1920", "NATION GOES DRY", "Prohibition law in force at midnight · Saloons close"),
    "periodico_izzy": ("THE EVENING WORLD", "1925", "IZZY & MOE STRIKE AGAIN", "Master of disguise raids speakeasies · 'Nobody suspects a fat man'"),
    "dato_izzy": ("NEW YORK HERALD", "1925", "4,932 ARRESTS", "Izzy Einstein & Moe Smith: 95% convicted · More than 100 disguises"),
    "periodico_alcantarilla": ("DAILY NEWS", "1925", "BOOZE DOWN THE SEWER", "Agents pour seized liquor into the gutter"),
    "periodico_despido": ("NEW YORK TIMES", "NOVEMBER 1925", "IZZY AND MOE LET GO", "Famous dry agents among 38 dismissed in shake-up"),
    "periodico_fin": ("NEW YORK DAILY", "DECEMBER 5, 1933", "PROHIBITION ENDS!", "Repeal ratified · 13 years of the dry law are over"),
}


def _periodico_base(ins):
    nom, fecha, tit, sub = PERIODICOS.get(ins, PERIODICOS["periodico_ley_seca"])
    F = _papel(hash(ins) % 100)
    x0, y0 = 430, 110
    F.text((x0 + 850, y0 + 110), nom, font(F_OLD, 120), INK)
    F.rect(x0 + 60, y0 + 190, x0 + 1640, y0 + 196, INK)
    F.text((x0 + 850, y0 + 225), fecha + "  ·  PRICE TWO CENTS", font(F_TYPE, 30), INK)
    F.rect(x0 + 60, y0 + 255, x0 + 1640, y0 + 259, INK)
    fs = 190
    while font(F_TIT, fs).getlength(tit) > 1500 and fs > 80:
        fs -= 6
    F.text((x0 + 850, y0 + 420), tit, font(F_TIT, fs), INK)
    F.text((x0 + 850, y0 + 590), sub, font(F_OLD, 50), (60, 50, 40))
    r = random.Random(3)
    for col in range(3):
        cx = x0 + 80 + col * 530
        if col == 1:
            F.rect(cx, y0 + 680, cx + 470, y0 + 1080, (150, 136, 110), INK, 3)
            F.ell(cx + 235, y0 + 830, 90, 100, (100, 90, 74))
            F.rect(cx + 120, y0 + 920, cx + 350, y0 + 1080, (100, 90, 74))
            continue
        for k in range(16):
            w = r.uniform(380, 470)
            F.rect(cx, y0 + 690 + k * 24, cx + w, y0 + 700 + k * 24, (120, 110, 94))
    return F


def _detalle_caja(ins):
    F = Lienzo(LW, LH, (50, 38, 30), 1)
    tablones(F, 0, 0, LW, LH, (70, 52, 40), 100, False, 60)
    F.rect(380, 200, 2180, 1200, (150, 112, 70), INK, 12)
    F.rect(430, 250, 2130, 1150, (196, 170, 110), INK, 6)
    r = random.Random(4)
    for k in range(260):    # paja
        x = r.uniform(440, 2120); y = r.uniform(260, 1140); a = r.uniform(0, 6.28)
        F.line([(x, y), (x + math.cos(a) * 60, y + math.sin(a) * 60)], (220, 190, 110), 4)
    if ins == "botellas_pan":
        for k in range(6):
            x = 560 + k * 270
            F.poly([(x, 1100), (x + 160, 1100), (x + 160, 640), (x + 115, 560), (x + 110, 420), (x + 50, 420), (x + 45, 560), (x, 640)],
                   [(60, 84, 54), (110, 60, 30), (80, 70, 50)][k % 3], INK, 6)
            F.rect(x + 45, 400, x + 115, 440, (150, 110, 70), INK, 4)
            F.rect(x + 20, 720, x + 140, 880, PAPER, INK, 4)
            F.text((x + 80, 800), ["RYE", "RUM", "GIN"][k % 3], font(F_TIT, 48), INK)
            F.line([(x + 30, 660), (x + 40, 1060)], (200, 220, 190), 8)
        for k in range(3):
            F.ell(700 + k * 600, 380, 230, 90, (196, 140, 72), INK, 6)
    else:
        for j in range(3):
            for k in range(4):
                F.ell(640 + k * 430, 420 + j * 300, 190, 110, (200, 146, 76), INK, 6)
                for q in range(3):
                    F.line([(560 + k * 430 + q * 60, 380 + j * 300), (600 + k * 430 + q * 60, 460 + j * 300)], (245, 210, 150), 8)
    return [(textura(F.final(), 6, 3, 61), 0.5)]


def _mirilla():
    F = Lienzo(LW, LH, (50, 38, 30), 1)
    tablones(F, 0, 0, LW, LH, (84, 60, 42), 140, True, 62)
    F.rect(900, 450, 1650, 760, INK, (40, 30, 24), 12)
    F.rect(940, 490, 1610, 720, (20, 14, 12))
    # ojos que miran desde dentro
    for ex in (1140, 1420):
        F.ell(ex, 605, 70, 34, (210, 196, 170))
        F.ell(ex + 10, 605, 30, 30, INK)
        F.poly([(ex - 90, 540), (ex + 90, 530), (ex + 90, 560), (ex - 90, 566)], (60, 44, 34))
    F.rect(940, 490, 1610, 515, (40, 30, 24))
    return [(textura(F.final(), 6, 3, 63), 0.6)]


def _mapa(ins):
    F = Lienzo(LW, LH, (40, 32, 26), 1)
    F.rect(330, 90, 2220, 1270, (214, 196, 156), INK, 10)
    # costa (NY / NJ / Long Island) estilizada
    costa = [(330, 300), (700, 330), (900, 420), (1000, 560), (1060, 520), (1200, 480), (1500, 430), (1900, 380), (2220, 330),
             (2220, 90), (330, 90)]
    F.poly(costa, (178, 158, 118), INK, 6)
    F.poly([(330, 300), (700, 330), (820, 560), (780, 900), (720, 1270), (330, 1270)], (178, 158, 118), INK, 6)
    F.text((560, 200), "NEW YORK", font(F_TIT, 64), (90, 70, 50))
    F.text((520, 760), "NEW JERSEY", font(F_TIT, 52), (90, 70, 50))
    F.text((1600, 250), "LONG ISLAND", font(F_TIT, 52), (90, 70, 50))
    F.ell(1000, 560, 16, 16, RED)
    F.text((1000, 610), "MANHATTAN", font(F_TYPE, 28), INK)
    # líneas de límite
    def linea(off, col, txt, dash=True):
        pts = [(780 + off, 1270), (840 + off, 900), (900 + off, 620 + off * 0.2), (1200, 560 + off * 0.75), (2220, 430 + off * 0.75)]
        for i in range(len(pts) - 1):
            a, b = pts[i], pts[i + 1]
            n = 16
            for k in range(0, n, 2):
                p0 = (a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n)
                p1 = (a[0] + (b[0] - a[0]) * (k + 1) / n, a[1] + (b[1] - a[1]) * (k + 1) / n)
                F.line([p0, p1], col, 8)
        F.text((pts[-2][0] + 180, pts[-2][1] + 40 + off * 0.05), txt, font(F_TIT, 46), col)
    linea(60, (90, 70, 50), "3 MILLAS")
    if ins == "mapa_millas2":
        linea(330, RED, "12 MILLAS (1924)")
        y = 1000
        for k in range(6):
            x = 1500 + k * 110
            F.poly([(x - 40, y), (x + 40, y), (x + 30, y + 22), (x - 30, y + 22)], INK)
            F.rect(x - 3, y - 50, x + 3, y, INK)
        F.text((1780, 1100), "RUM ROW", font(F_TIT, 64), RED)
    else:
        y = 860
        for k in range(6):
            x = 1300 + k * 110
            F.poly([(x - 40, y), (x + 40, y), (x + 30, y + 22), (x - 30, y + 22)], INK)
            F.rect(x - 3, y - 50, x + 3, y, INK)
    F.text((1275, 1220), "LA FILA DEL RON · RUM ROW", font(F_TYPE, 34), INK)
    return [(textura(F.final(), 8, 3, 64), 0.5)]


def _disfraces():
    F = Lienzo(LW, LH, (190, 176, 146), 1)
    for k in range(9):
        y = 1000 - k * 100
        F.line([(0, y), (LW, y)], (120, 108, 88), 4)
        F.text((140, y - 20), "%d'" % (k + 3), font(F_TYPE, 30), (90, 80, 64))
    F.text((LW / 2, 140), "IZZY EINSTEIN · +100 DISFRACES", font(F_TIT, 72), INK)
    img = F.final()
    u = 125
    for i, (nm, pose, lab) in enumerate([("izzy_pescador", "libreta", "PESCADOR"), ("izzy_opera", "canta", "TENOR"),
                                         ("izzy_lechero", "idle", "LECHERO"), ("izzy", "sombrero", "AGENTE")]):
        im, (fx, fy) = dibujar_persona(nm, u, pose, 0, 1, 1)
        x = 520 + i * 500
        img.paste(im, (int(x - fx), int(1040 - fy)), im)
        d = ImageDraw.Draw(img)
        d.rectangle([x - 130, 1060, x + 130, 1120], fill=INK + (255,))
        d.text((x, 1090), lab, font=font(F_TIT, 40), fill=PAPER + (255,), anchor="mm")
    return [(textura(img, 6, 3, 65), 0.5)]


def _dilema():
    F = Lienzo(LW, LH, INK, 1)
    F.rect(MX + 40, MY + 120, LW / 2 - 20, LH - MY - 160, (60, 70, 80), PAPER, 6)
    F.rect(LW / 2 + 20, MY + 120, LW - MX - 40, LH - MY - 160, (70, 50, 36), PAPER, 6)
    F.text((LW / 4 + 60, MY + 260), "1", font(F_TIT, 140), PAPER)
    F.text((LW / 4 + 60, LH / 2 + 40), "HUIR DE\nNUEVA YORK", font(F_TIT, 96), PAPER)
    F.text((3 * LW / 4 - 60, MY + 260), "2", font(F_TIT, 140), PAPER)
    F.text((3 * LW / 4 - 60, LH / 2 + 40), "IR AL ALMACÉN\nCOMO SI NADA", font(F_TIT, 96), PAPER)
    F.text((LW / 2, LH - MY - 90), "¿Y UNA TERCERA OPCIÓN?", font(F_TIT, 64), RED)
    return [(F.final(), 0.3)]


CACHE = {}


def capas(esc, ins=None):
    k = (esc, ins if esc in ("periodico", "detalle_caja", "mapa") else None)
    if k in CACHE:
        return CACHE[k]
    fn = {
        "almacen": _almacen, "puerta_almacen": _puerta_almacen, "negro_titulo": _negro, "barco": _barco,
        "estatua": _estatua, "ellis": _ellis, "mulberry": lambda: _mulberry(False), "mulberry_noche": lambda: _mulberry(True),
        "panaderia": lambda: _panaderia(False), "callejon": _callejon, "oficina": _oficina, "puerta_speak": _puerta_speak,
        "speakeasy": lambda: _speakeasy(False), "speakeasy_escenario": lambda: _speakeasy(True), "cuarto": _cuarto,
        "muelle": lambda: _muelle(False), "muelle_amanecer": lambda: _muelle(True), "bote": _bote, "mar_noche": _mar_noche,
        "oficina_federal": _oficina_federal, "calle_lluvia": _calle_lluvia, "carcel": _carcel,
        "panaderia_final": _panaderia_final, "mirilla": _mirilla, "disfraces": _disfraces, "dilema": _dilema,
        "periodico": lambda: _periodico(ins), "detalle_caja": lambda: _detalle_caja(ins), "mapa": lambda: _mapa(ins),
    }[esc]
    out = []
    for img, prof in fn():
        if img.size != (LW, LH):
            img = img.resize((LW, LH))
        if esc in ("periodico", "detalle_caja", "mapa", "mirilla", "disfraces", "dilema"):
            f = 0.8
            sm = img.resize((int(LW * f), int(LH * f)), Image.LANCZOS)
            bg = Image.new("RGBA", (LW, LH), (24, 18, 14, 255))
            bg.paste(sm, ((LW - sm.width) // 2, (LH - sm.height) // 2 + 10))
            img = bg
        out.append((img, prof))
    CACHE[k] = out
    return out


def luz(esc):
    return {"panaderia": (-1, -0.3), "oficina": (1, -0.2), "almacen": (1, -0.6), "callejon": (0.4, -1),
            "speakeasy": (0.2, -1), "speakeasy_escenario": (0, -1), "muelle": (1, -0.5), "muelle_amanecer": (1, -0.2),
            "calle_lluvia": (-1, -0.5), "carcel": (1, -0.6), "panaderia_final": (1, -0.4), "cuarto": (1, -0.4)}.get(esc, (-1, -0.4))


def tinte_fondo(esc):
    return {"mulberry_noche": (40, 40, 44), "speakeasy": (60, 36, 28), "ellis": (150, 130, 100), "barco": (150, 140, 120),
            "mulberry": (150, 126, 96), "muelle": (40, 40, 42), "almacen": (50, 40, 34)}.get(esc, (60, 50, 40))


def col_niebla(esc):
    return {"barco": (220, 210, 186), "estatua": (226, 214, 184), "muelle_amanecer": (240, 214, 176)}.get(esc, (120, 124, 124))


def mood(esc, ins=None):
    if ins in ("pregunta", "proximo"):
        return "final"
    return {"barco": "italia", "estatua": "italia", "ellis": "italia", "mulberry": "italia", "panaderia": "italia",
            "speakeasy": "jazz", "speakeasy_escenario": "jazz", "puerta_speak": "jazz", "mirilla": "jazz",
            "oficina": "tension", "almacen": "tension", "puerta_almacen": "tension", "callejon": "tension",
            "mulberry_noche": "tension", "calle_lluvia": "tension", "carcel": "tension", "cuarto": "tension",
            "mar_noche": "mar", "bote": "mar", "muelle": "mar", "muelle_amanecer": "mar", "oficina_federal": "jazz",
            "disfraces": "jazz", "panaderia_final": "final", "negro_titulo": "tension"}.get(esc)


def ambiente(esc, fx):
    a = []
    if "lluvia" in fx or "lluvia_ventana" in fx or esc in ("calle_lluvia",):
        a.append("lluvia")
    if esc in ("mar_noche", "bote", "muelle", "muelle_amanecer", "barco", "estatua"):
        a.append("olas")
    if esc in ("panaderia",):
        a.append("fuego")
    if esc in ("mulberry", "ellis"):
        a.append("calle")
    return a


# ------------------------------------------------------------------ efectos en pantalla (después de la cámara)
_ov = {}


def _overlay(nombre):
    if nombre in _ov:
        return _ov[nombre]
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    if nombre == "persiana":
        for k in range(-10, 30):
            y = k * 70
            d.polygon([(0, y), (W, y - 500), (W, y - 470), (0, y + 30)], fill=(0, 0, 0, 90))
        img = img.filter(ImageFilter.GaussianBlur(3))
    elif nombre == "reflector":
        img = Image.new("RGBA", (W * 2, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
        d.polygon([(W * 2 - 80, H * 0.52), (W * 0.9, H * 0.15), (W * 0.75, H * 1.2)], fill=(240, 240, 220, 70))
        img = img.filter(ImageFilter.GaussianBlur(18))
    elif nombre == "foco":
        d.polygon([(W / 2 - 60, 0), (W / 2 + 60, 0), (W / 2 + 520, H), (W / 2 - 520, H)], fill=(255, 236, 190, 46))
        img = img.filter(ImageFilter.GaussianBlur(24))
    elif nombre == "luz_rendija":
        for x in (cine.W * 0.35, W * 0.48, W * 0.6):
            d.line([(x, 60), (x, H - 60)], fill=(255, 240, 200, 180), width=6)
        d.rectangle([W * 0.3, H - 110, W * 0.7, H - 95], fill=(255, 240, 200, 200))
        img = img.filter(ImageFilter.GaussianBlur(4))
    elif nombre == "luz_calida":
        arr = np.zeros((H, W, 4), np.uint8); arr[..., :3] = LAMP
        yy, xx = np.mgrid[0:H, 0:W]
        arr[..., 3] = (np.clip(1 - yy / H, 0, 1) ** 2 * 50).astype(np.uint8)
        img = Image.fromarray(arr, "RGBA")
    elif nombre == "luz_dorada":
        arr = np.zeros((H, W, 4), np.uint8); arr[..., :3] = (255, 220, 150)
        yy, xx = np.mgrid[0:H, 0:W]
        arr[..., 3] = (np.clip(xx / W, 0, 1) ** 2 * 70).astype(np.uint8)
        img = Image.fromarray(arr, "RGBA")
    elif nombre == "luz_dura":
        arr = np.zeros((H, W, 4), np.uint8)
        yy, xx = np.mgrid[0:H, 0:W]
        arr[..., 3] = (np.clip((xx / W - 0.5) * 2, 0, 1) * 120).astype(np.uint8)
        img = Image.fromarray(arr, "RGBA")
    _ov[nombre] = img
    return img


def fx_pantalla(esc, fx, seed):
    efectos = []
    if "persiana" in fx:
        efectos.append(("static", _overlay("persiana")))
    if "luz_dura" in fx:
        efectos.append(("static", _overlay("luz_dura")))
    if "luces_calidas" in fx:
        efectos.append(("flicker", _overlay("luz_calida")))
    if "luz_dorada" in fx:
        efectos.append(("static", _overlay("luz_dorada")))
    if "foco" in fx:
        efectos.append(("static", _overlay("foco")))
    if "luz_rendija" in fx:
        efectos.append(("flicker", _overlay("luz_rendija")))
    if "reflector" in fx:
        efectos.append(("reflector", _overlay("reflector")))
    olas = "olas" in fx
    luces = "luces_barcos" in fx
    vapor = "vapor" in fx
    if not efectos and not olas and not luces and not vapor:
        return None
    r = random.Random(seed)
    olas_p = [(r.uniform(0, W), r.uniform(H * 0.6, H), r.uniform(0.5, 1)) for _ in range(40)]

    def f(img, t, u):
        for kind, ov in efectos:
            if kind == "static":
                img.paste(ov, (0, 0), ov)
            elif kind == "flicker":
                a = 0.75 + 0.25 * math.sin(t * 13) * math.sin(t * 7.3)
                o = ov.copy(); o.putalpha(ov.getchannel("A").point(lambda v: int(v * a)))
                img.paste(o, (0, 0), o)
            elif kind == "reflector":
                x = int(-W * 0.9 + (math.sin(t * 0.5 + seed) * 0.5 + 0.5) * W * 0.9)
                img.paste(ov, (x, 0), ov)
        d = ImageDraw.Draw(img, "RGBA")
        if olas:
            for x, y, s in olas_p:
                xx = (x + math.sin(t * 1.3 + y) * 40) % W
                w = 60 + 140 * (y / H)
                d.line([(xx, y), (xx + w, y + math.sin(t * 2 + x) * 3)], fill=(200, 200, 190, int(60 * s)), width=2)
        if luces:
            for k in range(9):
                a = int(150 + 100 * math.sin(t * 3 + k))
                xx = 300 + k * 230
                d.ellipse([xx - 5, H * 0.53 - 5, xx + 5, H * 0.53 + 5], fill=LAMP + (a,))
        if vapor:
            for k in range(10):
                ph = (t * 0.25 + k / 10) % 1
                x = 600 + k * 80 + math.sin(t + k) * 30
                y = H * 0.7 - ph * 500
                rr = 40 + ph * 80
                d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=(255, 250, 240, int(40 * (1 - ph))))
    return f


# ------------------------------------------------------------------ insertos en recuadro (viñeta de cómic)
_ins = {}


def _panel(w, h, x, y, contenido):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    p = Lienzo(w, h, PAPER, 2)
    contenido(p, w, h)
    pi = p.final()
    d = ImageDraw.Draw(img)
    d.rectangle([x + 14, y + 14, x + w + 14, y + h + 14], fill=(0, 0, 0, 140))
    img.paste(pi, (x, y))
    d.rectangle([x, y, x + w, y + h], outline=INK + (255,), width=8)
    return img


def inserto_overlay(ins):
    if ins in _ins:
        return _ins[ins]
    out = None
    if ins == "titulo_video":
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0)); L = Lienzo(W, H, None, 2)
        L.text((W / 2, H / 2 - 170), "¿QUÉ PASARÍA SI TRABAJARAS PARA LA", font(F_TIT, 66), PAPER)
        L.text((W / 2, H / 2 + 10), "MAFIA", font(F_TIT, 260), RED, stroke=4, stroke_fill=INK)
        L.text((W / 2, H / 2 + 190), "NUEVA YORK · 1925", font(F_TYPE, 46), LIGHT)
        out = L.final()
    elif ins == "sello":
        def c(p, w, h):
            p.text((w / 2, h / 2 - 40), "ADMITTED", font(F_TIT, 90), RED)
            p.text((w / 2, h / 2 + 50), "ELLIS ISLAND · 1925", font(F_TYPE, 30), INK)
            p.rect(30, 30, w - 30, h - 30, None, RED, 8)
        out = _panel(560, 300, W - 700, 120, c)
    elif ins == "sobre":
        def c(p, w, h):
            p.rect(0, 0, w, h, (120, 100, 70))
            p.poly([(60, 120), (w - 60, 120), (w - 60, h - 60), (60, h - 60)], (226, 206, 160), INK, 5)
            for k in range(4):
                p.rect(100 + k * 30, 60 + k * 10, 360 + k * 30, 190 + k * 10, (150, 170, 130), INK, 4)
                p.text((230 + k * 30, 125 + k * 10), "$10", font(F_TIT, 50), (60, 80, 50))
        out = _panel(520, 340, W - 660, 110, c)
    elif ins == "libreta":
        def c(p, w, h):
            p.rect(0, 0, w, h, (236, 228, 200))
            for k in range(8):
                p.line([(30, 60 + k * 40), (w - 30, 60 + k * 40)], (150, 160, 180), 2)
            p.text((w / 2, 80), "PIER 7 · 4:50 AM", font(F_TYPE, 34), INK)
            p.text((w / 2, 160), "boy w/ cap — bread cart", font(F_TYPE, 30), INK)
            p.text((w / 2, 240), "30 cases RYE", font(F_TYPE, 34), RED)
        out = _panel(560, 360, W - 700, 110, c)
    elif ins in ("dato_speak", "dato_guardia"):
        txt = {"dato_speak": ("DECENAS DE MILES", "de bares secretos en Nueva York"),
               "dato_guardia": ("POCOS BARCOS", "para vigilar miles de kilómetros de costa")}[ins]
        def c(p, w, h, txt=txt):
            p.rect(0, 0, w, 26, RED)
            p.text((w / 2, 110), txt[0], font(F_TIT, 84), INK)
            p.text((w / 2, 200), txt[1], font(F_SUBB, 30), (70, 56, 44))
        out = _panel(720, 270, 120, 110, c)
    elif ins == "pregunta":
        L = Lienzo(W, H, None, 2)
        L.text((W / 2, 220), "¿TÚ QUÉ HABRÍAS HECHO?", font(F_TIT, 110), PAPER)
        for i, t in enumerate(["1 · ACEPTAR EL TRATO", "2 · HUIR", "3 · CAMBIAR LAS CAJAS"]):
            L.rect(W / 2 - 520, 380 + i * 150, W / 2 + 520, 490 + i * 150, (40, 30, 24), RED, 6)
            L.text((W / 2, 435 + i * 150), t, font(F_TIT, 70), PAPER)
        out = L.final()
    elif ins == "proximo":
        L = Lienzo(W, H, None, 2)
        L.text((W / 2, 200), "¿PRÓXIMO DOMINGO?", font(F_TIT, 110), PAPER)
        L.rect(220, 310, 900, 770, (30, 30, 60), (255, 60, 160), 8)
        L.text((560, 500), "YAKUZA", font(F_TIT, 120), (255, 80, 170))
        L.text((560, 640), "TOKIO · AÑOS 80", font(F_TYPE, 40), PAPER)
        L.rect(1020, 310, 1700, 770, (70, 56, 30), (230, 190, 90), 8)
        L.text((1360, 500), "CHEF REAL", font(F_TIT, 110), (240, 200, 100))
        L.text((1360, 640), "VERSALLES · 1680", font(F_TYPE, 40), PAPER)
        L.text((W / 2, 860), "COMENTA 1 O 2 · MUNDO HIPOTÉTICO", font(F_TIT, 52), LIGHT)
        out = L.final()
    _ins[ins] = out
    return out
