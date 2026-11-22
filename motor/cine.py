# -*- coding: utf-8 -*-
"""Motor de NOVELA GRÁFICA CINEMATOGRÁFICA — historias largas del domingo (16:9, 1920×1080).

Totalmente distinto al estilo de los Shorts (nada de vc.py / nico()):
- Personajes de proporciones adultas (~7,5 cabezas), rostro 3/4 con rasgos marcados, ropa de época.
- Claroscuro: sombra dura en bloque calculada sobre la silueta (luz de un lado) + luz de contorno.
- Paleta limitada por historia (PALETA), viñeta, grano de película, franjas de cine.
- Cámara con paralaje por capas (prof 0 = fondo quieto … 1 = primer plano), push/pull/pan/tilt/shake.
- Partículas (lluvia, polvo, humo, niebla, brasas, harina), subtítulos, música procedural y efectos.

Uso (ver episodios/largos/2026-11-22-mafia-1925/acto1.py):
    import cine; cine.render_acto(ACTO, escenas_module, "acto1.mp4", voz_dir)
"""
import math, os, random, subprocess, wave, struct
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

W, H, FPS = 1920, 1080, 30
CW, CH = 2112, 1188            # lienzo de composición (1.1×)
MX, MY = 220, 90               # márgenes para paralaje
LW, LH = CW + 2 * MX, CH + 2 * MY
SS = 2                         # superesmuestreo de dibujo

FONTS = "/usr/share/fonts/truetype/google-fonts/"
F_TIT = FONTS + "ofl/anton/Anton-Regular.ttf"
F_SUB = FONTS + "Poppins-SemiBold.ttf" if os.path.exists(FONTS + "Poppins-SemiBold.ttf") else FONTS + "Poppins-Bold.ttf"
F_SUBB = FONTS + "Poppins-Bold.ttf"
F_SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"


def _find(name, fallback):
    for root, _, files in os.walk(FONTS):
        if name in files:
            return os.path.join(root, name)
    return fallback


F_TIT = _find("Anton-Regular.ttf", F_SERIF)
F_OLD = _find("CrimsonText-Bold.ttf", _find("Cardo-Bold.ttf", F_SERIF))
F_TYPE = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"

_fc = {}


def font(path, size):
    k = (path, size)
    if k not in _fc:
        _fc[k] = ImageFont.truetype(path, size)
    return _fc[k]


# ------------------------------------------------------------------ paleta (se puede cambiar por historia)
PALETA = dict(
    ink=(16, 12, 10), dark=(40, 30, 24), mid=(98, 76, 58), light=(178, 150, 112),
    paper=(226, 206, 168), red=(170, 30, 26), lamp=(255, 196, 112), cold=(120, 132, 132),
)


def P(k):
    return PALETA[k]


def mix(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def shade(c, f):
    """Oscurece un color hacia la tinta (f<1) o lo aclara hacia papel (f>1)."""
    if f <= 1:
        return mix(P("ink"), c, f)
    return mix(c, P("paper"), min(1, f - 1))


# ------------------------------------------------------------------ utilidades de dibujo con superesmuestreo
class Lienzo:
    """Lienzo RGBA de tamaño (w,h) finales; se dibuja en coordenadas finales y se superesmuestrea."""

    def __init__(self, w, h, bg=None, ss=SS):
        self.w, self.h, self.ss = w, h, ss
        self.img = Image.new("RGBA", (w * ss, h * ss), bg + (255,) if bg else (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.img)

    def _p(self, pts):
        s = self.ss
        return [(x * s, y * s) for x, y in pts]

    def poly(self, pts, fill, ol=None, w=0):
        self.d.polygon(self._p(pts), fill=_rgba(fill), outline=None)
        if ol is not None and w > 0:
            pp = self._p(pts)
            self.d.line(pp + [pp[0]], fill=_rgba(ol), width=max(1, int(w * self.ss)), joint="curve")

    def ell(self, cx, cy, rx, ry, fill, ol=None, w=0):
        s = self.ss
        self.d.ellipse([(cx - rx) * s, (cy - ry) * s, (cx + rx) * s, (cy + ry) * s], fill=_rgba(fill) if fill else None,
                       outline=_rgba(ol) if ol is not None and w > 0 else None, width=max(1, int(w * s)) if w else 0)

    def rect(self, x0, y0, x1, y1, fill, ol=None, w=0):
        s = self.ss
        x0, x1 = min(x0, x1), max(x0, x1)
        y0, y1 = min(y0, y1), max(y0, y1)
        self.d.rectangle([x0 * s, y0 * s, x1 * s, y1 * s], fill=_rgba(fill) if fill else None,
                         outline=_rgba(ol) if ol is not None and w > 0 else None, width=max(1, int(w * s)) if w else 0)

    def line(self, pts, col, w):
        self.d.line(self._p(pts), fill=_rgba(col), width=max(1, int(w * self.ss)), joint="curve")

    def arc(self, cx, cy, rx, ry, a0, a1, col, w):
        s = self.ss
        self.d.arc([(cx - rx) * s, (cy - ry) * s, (cx + rx) * s, (cy + ry) * s], a0, a1, fill=_rgba(col), width=max(1, int(w * s)))

    def chord(self, cx, cy, rx, ry, a0, a1, fill):
        s = self.ss
        self.d.chord([(cx - rx) * s, (cy - ry) * s, (cx + rx) * s, (cy + ry) * s], a0, a1, fill=_rgba(fill))

    def text(self, xy, txt, f, fill, anchor="mm", stroke=0, stroke_fill=None, spacing=4):
        s = self.ss
        ff = font(f.path, int(f.size * s))
        self.d.text((xy[0] * s, xy[1] * s), txt, font=ff, fill=_rgba(fill), anchor=anchor,
                    stroke_width=int(stroke * s), stroke_fill=_rgba(stroke_fill) if stroke_fill else None, spacing=spacing * s)

    def final(self):
        if self.ss == 1:
            return self.img
        return self.img.resize((self.w, self.h), Image.LANCZOS)


def _rgba(c):
    if c is None:
        return None
    if len(c) == 4:
        return tuple(int(v) for v in c)
    return tuple(int(v) for v in c) + (255,)


def gradiente(w, h, top, bot, curva=1.0):
    t = np.linspace(0, 1, h)[:, None] ** curva
    a = np.array(top, np.float32)[None, None, :]
    b = np.array(bot, np.float32)[None, None, :]
    g = a + (b - a) * t[..., None]
    g = np.repeat(g, w, axis=1)
    return Image.fromarray(np.clip(g, 0, 255).astype(np.uint8), "RGB").convert("RGBA")


def textura(img, fuerza=10, escala=3, seed=1):
    """Ruido suave tipo papel/pared sobre una capa RGBA (respeta alfa)."""
    rng = np.random.default_rng(seed)
    w, h = img.size
    n = rng.normal(0, 1, (h // escala + 1, w // escala + 1)).astype(np.float32)
    n = cv2.resize(n, (w, h), interpolation=cv2.INTER_CUBIC)
    a = np.asarray(img).astype(np.int16)
    a[..., :3] = np.clip(a[..., :3] + (n[..., None] * fuerza), 0, 255)
    return Image.fromarray(a.astype(np.uint8), "RGBA")


def claroscuro(img, luz=(-1, -0.35), k=0.22, fuerza=0.62, rim=0.25, col_sombra=None, ref=None):
    """Sombra dura en bloque del lado opuesto a la luz + luz de contorno del lado iluminado.
    luz = dirección HACIA la fuente (x<0: luz desde la izquierda). k = ancho de la sombra (fracción del ancho)."""
    a = np.asarray(img).astype(np.float32)
    al = a[..., 3]
    bb = img.getbbox()
    if not bb:
        return img
    ref = ref or (bb[2] - bb[0])
    m = (al > 128).astype(np.uint8)
    lx, ly = luz
    n = math.hypot(lx, ly)
    lx, ly = lx / n, ly / n
    d = max(2, int(ref * k))
    # p está en sombra si al alejarse de la luz d px se sale de la silueta
    M = np.float32([[1, 0, lx * d], [0, 1, ly * d]])   # muestra p - d*(-L)... desplaza la máscara hacia la luz
    shifted = cv2.warpAffine(m, M, (m.shape[1], m.shape[0]), flags=cv2.INTER_NEAREST, borderValue=0)
    som = (m == 1) & (shifted == 0)
    som = cv2.GaussianBlur(som.astype(np.float32), (0, 0), max(1, d * 0.04))
    som = (som > 0.5).astype(np.float32)
    dr = max(2, int(ref * 0.02))
    M2 = np.float32([[1, 0, -lx * dr], [0, 1, -ly * dr]])
    sh2 = cv2.warpAffine(m, M2, (m.shape[1], m.shape[0]), flags=cv2.INTER_NEAREST, borderValue=0)
    rimm = ((m == 1) & (sh2 == 0)).astype(np.float32) * (1 - som)
    out = a.copy()
    cs = np.array(col_sombra or P("ink"), np.float32)
    f = fuerza * som[..., None]
    out[..., :3] = out[..., :3] * (1 - f) + cs * f * 0.9 + out[..., :3] * f * 0.1
    lamp = np.array(P("lamp"), np.float32)
    rr = rim * rimm[..., None]
    out[..., :3] = out[..., :3] * (1 - rr) + lamp * rr
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGBA")


# ------------------------------------------------------------------ PERSONAJES (proporciones adultas)
# Coordenadas en "cabezas" (u): x a la derecha (lado al que mira), y hacia abajo desde la coronilla.
POSES = {
    "idle":       dict(A=((0.98, 2.55), (0.92, 3.65)), B=((-0.98, 2.55), (-0.92, 3.65))),
    "caja":       dict(A=((1.02, 2.45), (0.66, 2.8)), B=((-1.02, 2.45), (-0.66, 2.8)), obj="caja"),
    "pan":        dict(A=((0.98, 2.5), (0.42, 2.45)), B=((-0.98, 2.55), (-0.92, 3.65)), obj="pan"),
    "manos":      dict(A=((1.3, 1.05), (1.25, 0.15)), B=((-1.3, 1.05), (-1.25, 0.15))),
    "senala":     dict(A=((1.62, 1.62), (2.45, 1.5)), B=((-0.98, 2.55), (-0.92, 3.65)), obj="dedo"),
    "brazos":     dict(A=((1.0, 2.45), (-0.45, 2.3)), B=((-1.0, 2.5), (0.5, 2.42)), cruz=True),
    "habla_mano": dict(A=((1.25, 2.5), (1.35, 1.75)), B=((-0.98, 2.55), (-0.92, 3.65)), obj="palma"),
    "libreta":    dict(A=((0.98, 2.6), (0.5, 2.5)), B=((-0.95, 2.6), (0.08, 2.55)), obj="libreta"),
    "sombrero":   dict(A=((1.05, 1.35), (0.42, 0.02)), B=((-0.98, 2.55), (-0.92, 3.65))),
    "canta":      dict(A=((1.45, 1.8), (2.15, 1.15)), B=((-1.45, 1.8), (-2.15, 1.15))),
    "silbato":    dict(A=((1.05, 1.9), (0.32, 0.85)), B=((-0.98, 2.55), (-0.92, 3.65)), obj="silbato"),
    "esposado":   dict(A=((0.82, 2.7), (0.14, 3.3)), B=((-0.82, 2.7), (-0.14, 3.3)), obj="esposas"),
    "botella":    dict(A=((1.25, 2.6), (1.55, 2.2)), B=((-0.98, 2.55), (-0.92, 3.65)), obj="botella"),
    "baile":      dict(A=((1.2, 1.4), (1.55, 0.55)), B=((-1.15, 2.6), (-1.55, 2.15))),
}

PERS = {}   # se llena con definir_personaje()


def definir_personaje(nombre, **kw):
    base = dict(cab=7.4, ancho=1.0, panza=0.0, piel=(214, 170, 128), pelo=P("dark"), sombrero=None,
                col_sombrero=P("dark"), banda=P("ink"), saco=P("mid"), pantalon=P("dark"), camisa=P("paper"),
                corbata=None, chaleco=None, delantal=None, bigote=None, cejas=P("ink"), rayas=False,
                mangas_cortas=False, tirantes=None, capa=None, gorro_pan=False, abrigo=False, mandibula=1.0,
                nariz=1.0, edad=0, barba=False, palillo=False, cigarro=False)
    base.update(kw)
    PERS[nombre] = base


def _arm(L, sx, sy, e, h, u, col, w0=0.34, w1=0.27, ol=None):
    """Brazo como dos segmentos gruesos con articulación redonda."""
    def seg(p, q, wa, wb):
        ang = math.atan2(q[1] - p[1], q[0] - p[0]) + math.pi / 2
        ca, sa = math.cos(ang), math.sin(ang)
        pts = [(p[0] + ca * wa / 2, p[1] + sa * wa / 2), (q[0] + ca * wb / 2, q[1] + sa * wb / 2),
               (q[0] - ca * wb / 2, q[1] - sa * wb / 2), (p[0] - ca * wa / 2, p[1] - sa * wa / 2)]
        L.poly([(sx + x * u, sy + y * u) for x, y in pts], col, ol, 0.035 * u if ol else 0)
    seg(e[0], e[1], w0, w0 * 0.92)
    L.ell(sx + e[1][0] * u, sy + e[1][1] * u, w0 * 0.47 * u, w0 * 0.47 * u, col)
    seg(e[1], h, w0 * 0.92, w1)


def dibujar_persona(nombre, u, pose="idle", boca=0, ojos=1, mira=1, luz=(-1, -0.35), recorte=None, tinte=None,
                    extra=None):
    """Devuelve (sprite RGBA, (ox, oy)) donde (ox,oy) es la posición de los pies dentro del sprite.
    u = alto de una cabeza en px finales. mira=1 derecha, -1 izquierda."""
    c = dict(PERS[nombre])
    if extra:
        c.update(extra)
    cab = c["cab"]
    an, pz = c["ancho"], c["panza"]
    OL = P("ink")
    ow = 0.045 * u
    wpx = int(5.2 * u * max(an, 1) + 4)
    hpx = int((cab + 0.7) * u + 4)
    if recorte:
        hpx = min(hpx, int(recorte))
    L = Lienzo(wpx, hpx)
    sx, sy = wpx / 2, 0.45 * u          # coronilla
    k = cab / 7.4                        # escala vertical del cuerpo
    def X(x): return sx + x * u
    def Y(y): return sy + y * u * (k if y > 1.15 else 1)
    po = POSES.get(pose, POSES["idle"])
    saco, pant, cam = c["saco"], c["pantalon"], c["camisa"]
    # --- capa (detrás)
    if c["capa"]:
        L.poly([(X(-1.1 * an), Y(1.25)), (X(1.1 * an), Y(1.25)), (X(1.7 * an), Y(5.6)), (X(-1.7 * an), Y(5.6))], c["capa"], OL, ow)
    # --- brazo B (lejano) detrás del torso
    mang = cam if c["mangas_cortas"] else saco
    def brazo(lado, delante=False):
        e, h = po[lado]
        e2 = ((e[0] * an if abs(e[0]) < 1.2 else e[0] + (an - 1) * 0.6 * np.sign(e[0]), e[1] * (k if e[1] > 1.15 else 1)),
              h if not po.get("cruz") else h)
        sh = (0.8 * an * (1 if lado == "A" else -1), 1.5)
        hh = (e2[1][0], e2[1][1])
        hand = (h[0], h[1] * (k if h[1] > 1.15 else 1))
        _arm(L, sx, sy, (sh, hh), hand, u, mang, 0.36, 0.28, OL)
        if c["mangas_cortas"]:
            # antebrazo de piel
            _arm(L, sx, sy, (hh, hh), hand, u, c["piel"], 0.3, 0.24, OL)
        L.ell(X(hand[0]), sy + hand[1] * u, 0.17 * u, 0.15 * u, c["piel"], OL, ow * 0.8)
        return hand
    hB = brazo("B")
    # --- piernas
    hipy, piey = 3.62, cab - 0.12
    for s in (-1, 1):
        x0 = s * 0.08
        L.poly([(X(x0 + s * 0.02), Y(hipy)), (X(s * 0.62 * an), Y(hipy)), (X(s * 0.46), Y(piey)), (X(s * 0.1), Y(piey))], pant, OL, ow)
        L.poly([(X(s * 0.08), Y(piey - 0.05)), (X(s * 0.5 + 0.22), Y(piey - 0.05)), (X(s * 0.52 + 0.3), Y(piey + 0.18)), (X(s * 0.05), Y(piey + 0.18))], OL)
    # --- abrigo largo
    if c["abrigo"]:
        L.poly([(X(-0.98 * an), Y(1.35)), (X(0.98 * an), Y(1.35)), (X(1.05 * an), Y(5.4)), (X(-1.05 * an), Y(5.4))], saco, OL, ow)
    # --- torso
    tw = 0.95 * an
    torso = [(X(-0.22), Y(1.14)), (X(0.22), Y(1.14)), (X(0.72 * an), Y(1.22)), (X(0.97 * an), Y(1.45)),
             (X(0.86 * an + pz * 0.3), Y(1.98)), (X(0.74 * an + pz * 0.7), Y(2.7)), (X(0.68 * an + pz * 0.45), Y(3.2)),
             (X(0.64 * an + pz * 0.2), Y(hipy + 0.05)), (X(-0.64 * an - pz * 0.2), Y(hipy + 0.05)),
             (X(-0.68 * an - pz * 0.45), Y(3.2)), (X(-0.74 * an - pz * 0.7), Y(2.7)), (X(-0.86 * an - pz * 0.3), Y(1.98)),
             (X(-0.97 * an), Y(1.45)), (X(-0.72 * an), Y(1.22))]
    L.poly(torso, saco, OL, ow)
    if c["rayas"]:
        for i in range(-6, 7):
            xx = i * 0.14 * an
            L.line([(X(xx), Y(1.4)), (X(xx * 0.85), Y(hipy))], shade(saco, 1.25), 0.014 * u)
    # camisa/pecho (V del saco)
    if not c["mangas_cortas"] or c["chaleco"]:
        pass
    vcol = c["chaleco"] or cam
    if c["mangas_cortas"]:
        L.poly(torso, cam, OL, ow)
        if c["chaleco"]:
            L.poly([(X(-0.62 * an), Y(1.35)), (X(-0.12), Y(1.35)), (X(0.0), Y(2.4)), (X(0.12), Y(1.35)), (X(0.62 * an), Y(1.35)),
                    (X(0.66 * an + pz * 0.3), Y(hipy)), (X(-0.66 * an - pz * 0.3), Y(hipy))], c["chaleco"], OL, ow)
            for i in range(3):
                L.ell(X(0.06), Y(2.6 + i * 0.3), 0.04 * u, 0.04 * u, OL)
        if c["tirantes"]:
            for s in (-1, 1):
                L.line([(X(s * 0.45), Y(1.32)), (X(s * 0.38), Y(hipy))], c["tirantes"], 0.09 * u)
    else:
        L.poly([(X(-0.3), Y(1.3)), (X(0.3), Y(1.3)), (X(0.0), Y(2.45))], vcol, OL, ow * 0.8)
        # solapas
        for s in (-1, 1):
            L.poly([(X(s * 0.3), Y(1.3)), (X(s * 0.52), Y(1.55)), (X(s * 0.2), Y(1.9)), (X(0), Y(2.45))], shade(saco, 0.8), OL, ow * 0.7)
        if c["corbata"]:
            L.poly([(X(-0.07), Y(1.35)), (X(0.07), Y(1.35)), (X(0.1), Y(2.2)), (X(0.0), Y(2.38)), (X(-0.1), Y(2.2))], c["corbata"], OL, ow * 0.6)
        for i in range(2):
            L.ell(X(0.1), Y(2.75 + i * 0.4), 0.05 * u, 0.05 * u, OL)
    if c["delantal"]:
        L.poly([(X(-0.55 * an), Y(1.9)), (X(0.55 * an), Y(1.9)), (X(0.72 * an + pz * 0.4), Y(2.8)), (X(0.68 * an), Y(5.0)),
                (X(-0.68 * an), Y(5.0)), (X(-0.72 * an - pz * 0.4), Y(2.8))], c["delantal"], OL, ow)
        L.line([(X(-0.75 * an - pz * 0.4), Y(2.8)), (X(0.75 * an + pz * 0.4), Y(2.8))], shade(c["delantal"], 0.7), 0.06 * u)
    # cinturón
    if not c["abrigo"] and not c["delantal"] and c["mangas_cortas"]:
        L.rect(X(-0.66 * an), Y(hipy - 0.08), X(0.66 * an), Y(hipy + 0.06), OL)
    # cuello
    L.poly([(X(-0.17), Y(0.9)), (X(0.17), Y(0.9)), (X(0.2), Y(1.2)), (X(-0.2), Y(1.2))], c["piel"], OL, ow)
    L.poly([(X(-0.26), Y(1.08)), (X(0.0), Y(1.3)), (X(0.26), Y(1.08)), (X(0.22), Y(1.2)), (X(-0.22), Y(1.2))], cam, OL, ow * 0.7)
    # --- objeto sostenido y brazo A
    obj = po.get("obj")
    if obj == "caja":
        L.poly([(X(-0.85), Y(2.15)), (X(0.85), Y(2.15)), (X(0.85), Y(3.15)), (X(-0.85), Y(3.15))], (150, 112, 70), OL, ow)
        for i in range(1, 4):
            L.line([(X(-0.85), Y(2.15 + i * 0.25)), (X(0.85), Y(2.15 + i * 0.25))], (110, 80, 50), 0.025 * u)
        L.text((X(0), Y(2.65)), "PANE", font(F_TIT, max(8, int(0.28 * u))), (70, 40, 20))
    hA = brazo("A")
    if po.get("cruz"):
        hB = brazo("B")
    if obj == "pan":
        L.ell(X(0.25), Y(2.38), 0.55 * u, 0.24 * u, (196, 140, 72), OL, ow)
        for i in range(3):
            L.line([(X(0.0 + i * 0.22), Y(2.25)), (X(0.12 + i * 0.22), Y(2.5))], (240, 200, 140), 0.035 * u)
    elif obj == "libreta":
        L.poly([(X(0.15), Y(2.25)), (X(0.65), Y(2.2)), (X(0.7), Y(2.75)), (X(0.2), Y(2.8))], P("paper"), OL, ow)
        for i in range(3):
            L.line([(X(0.25), Y(2.38 + i * 0.12)), (X(0.6), Y(2.35 + i * 0.12))], P("mid"), 0.02 * u)
    elif obj == "dedo":
        L.poly([(X(2.5), Y(1.46)), (X(2.85), Y(1.44)), (X(2.85), Y(1.52)), (X(2.5), Y(1.56))], c["piel"], OL, ow * 0.6)
    elif obj == "silbato":
        L.rect(X(0.3), Y(0.82), X(0.52), Y(0.92), (200, 190, 170), OL, ow * 0.6)
    elif obj == "esposas":
        for s in (-1, 1):
            L.ell(X(s * 0.16), Y(3.22), 0.12 * u, 0.06 * u, None, (200, 200, 200), 0.04 * u)
        L.line([(X(-0.08), Y(3.22)), (X(0.08), Y(3.22))], (200, 200, 200), 0.03 * u)
    elif obj == "botella":
        L.poly([(X(1.45), Y(1.7)), (X(1.62), Y(1.68)), (X(1.75), Y(2.4)), (X(1.5), Y(2.45))], (60, 80, 50), OL, ow * 0.6)
    elif obj == "palma":
        pass
    # --- CABEZA (3/4 hacia la derecha)
    hx, hy = 0.0, 0.5
    piel = c["piel"]
    mj = c["mandibula"]
    # oreja
    L.ell(X(-0.3), Y(0.56), 0.08 * u, 0.13 * u, piel, OL, ow * 0.8)
    # cráneo + mandíbula
    L.ell(X(hx), Y(0.42), 0.37 * u, 0.4 * u, piel, OL, ow)
    jaw = [(X(-0.36), Y(0.45)), (X(-0.3), Y(0.78)), (X(-0.12), Y(0.98 * mj + 0.02)), (X(0.12), Y(1.0 * mj)),
           (X(0.3), Y(0.86)), (X(0.38), Y(0.6)), (X(0.37), Y(0.4))]
    L.poly(jaw, piel, OL, ow)
    L.ell(X(hx), Y(0.42), 0.35 * u, 0.38 * u, piel)
    # pelo
    if not c["sombrero"] or c["sombrero"] in ("gorra",):
        L.chord(X(-0.02), Y(0.36), 0.39 * u, 0.36 * u, 180, 360, c["pelo"])
        L.poly([(X(-0.38), Y(0.36)), (X(-0.36), Y(0.62)), (X(-0.26), Y(0.42))], c["pelo"])
    # ojos y cejas
    ey = 0.5
    for ex, sc in ((0.19, 1.0), (-0.06, 0.82)):
        if ojos:
            L.ell(X(ex), Y(ey), 0.075 * u * sc, 0.04 * u, (236, 226, 206))
            L.ell(X(ex + 0.02), Y(ey), 0.032 * u * sc, 0.032 * u, OL)
            L.line([(X(ex - 0.08 * sc), Y(ey - 0.03)), (X(ex + 0.08 * sc), Y(ey - 0.035))], OL, 0.03 * u)
        else:
            L.line([(X(ex - 0.08 * sc), Y(ey + 0.005)), (X(ex + 0.08 * sc), Y(ey + 0.005))], OL, 0.03 * u)
        L.poly([(X(ex - 0.1 * sc), Y(ey - 0.1)), (X(ex + 0.1 * sc), Y(ey - 0.13)), (X(ex + 0.11 * sc), Y(ey - 0.085)),
                (X(ex - 0.1 * sc), Y(ey - 0.06))], c["cejas"])
    # nariz
    nz = c["nariz"]
    L.poly([(X(0.1), Y(0.52)), (X(0.2 + 0.06 * nz), Y(0.67)), (X(0.12), Y(0.7))], shade(piel, 0.6))
    L.line([(X(0.17 + 0.04 * nz), Y(0.6)), (X(0.2 + 0.06 * nz), Y(0.67)), (X(0.11), Y(0.7))], OL, 0.026 * u)
    # pómulo / arrugas
    L.line([(X(0.3), Y(0.62)), (X(0.24), Y(0.78))], shade(piel, 0.6), 0.02 * u)
    if c["edad"]:
        L.line([(X(0.05), Y(0.31)), (X(0.22), Y(0.3))], shade(piel, 0.6), 0.016 * u)
        L.line([(X(0.13), Y(0.8)), (X(0.04), Y(0.9))], shade(piel, 0.55), 0.018 * u)
    if c["barba"]:
        L.poly([(X(-0.3), Y(0.7)), (X(-0.12), Y(0.98)), (X(0.12), Y(1.0)), (X(0.3), Y(0.86)), (X(0.2), Y(0.78)), (X(-0.1), Y(0.82))], shade(piel, 0.78))
    # boca
    my = 0.84
    if boca:
        L.ell(X(0.11), Y(my), 0.075 * u, 0.04 * u + 0.03 * u * boca, (60, 20, 18), OL, ow * 0.6)
    else:
        L.line([(X(0.03), Y(my)), (X(0.21), Y(my - 0.01))], OL, 0.03 * u)
    if c["bigote"]:
        bc = c["bigote"]
        L.poly([(X(-0.04), Y(0.79)), (X(0.12), Y(0.74)), (X(0.29), Y(0.79)), (X(0.25), Y(0.82)), (X(0.12), Y(0.79)), (X(-0.02), Y(0.83))], bc, OL, ow * 0.4)
        if c.get("bigote_grande"):
            L.poly([(X(-0.15), Y(0.82)), (X(0.12), Y(0.72)), (X(0.42), Y(0.8)), (X(0.38), Y(0.86)), (X(0.12), Y(0.8)), (X(-0.12), Y(0.88))], bc, OL, ow * 0.4)
    if c["palillo"]:
        L.line([(X(0.2), Y(my)), (X(0.42), Y(my + 0.05))], (210, 190, 150), 0.02 * u)
    if c["cigarro"]:
        L.line([(X(0.2), Y(my)), (X(0.48), Y(my + 0.04))], (110, 70, 40), 0.06 * u)
        L.ell(X(0.49), Y(my + 0.04), 0.03 * u, 0.03 * u, P("lamp"))
    # sombreros
    sb, cs = c["sombrero"], c["col_sombrero"]
    if sb == "fedora":
        L.ell(X(0.02), Y(0.18), 0.62 * u, 0.12 * u, cs, OL, ow)
        L.poly([(X(-0.35), Y(0.2)), (X(-0.32), Y(-0.18)), (X(0.0), Y(-0.1)), (X(0.34), Y(-0.2)), (X(0.38), Y(0.2))], cs, OL, ow)
        L.rect(X(-0.36), Y(0.08), X(0.38), Y(0.18), c["banda"])
    elif sb == "fedora_lad":
        pts = [(-0.66, 0.24), (0.64, 0.08), (0.66, 0.16), (-0.64, 0.33)]
        L.poly([(X(x), Y(y)) for x, y in pts], cs, OL, ow)
        L.poly([(X(-0.36), Y(0.24)), (X(-0.3), Y(-0.15)), (X(0.04), Y(-0.1)), (X(0.36), Y(-0.24)), (X(0.38), Y(0.12))], cs, OL, ow)
        L.poly([(X(-0.36), Y(0.13)), (X(0.38), Y(0.02)), (X(0.38), Y(0.12)), (X(-0.36), Y(0.24))], c["banda"])
    elif sb == "gorra":
        L.chord(X(0.0), Y(0.22), 0.42 * u, 0.3 * u, 180, 360, cs)
        L.arc(X(0.0), Y(0.22), 0.42 * u, 0.3 * u, 180, 360, OL, ow)
        L.poly([(X(0.1), Y(0.18)), (X(0.62), Y(0.2)), (X(0.6), Y(0.27)), (X(0.05), Y(0.26))], shade(cs, 0.7), OL, ow * 0.8)
        L.line([(X(-0.42), Y(0.22)), (X(0.42), Y(0.22))], OL, ow)
    elif sb == "bombin":
        L.ell(X(0.0), Y(0.18), 0.52 * u, 0.1 * u, cs, OL, ow)
        L.chord(X(0.0), Y(0.2), 0.36 * u, 0.42 * u, 180, 360, cs)
        L.arc(X(0.0), Y(0.2), 0.36 * u, 0.42 * u, 180, 360, OL, ow)
        L.rect(X(-0.35), Y(0.1), X(0.35), Y(0.17), c["banda"])
    elif sb == "impermeable":
        L.poly([(X(-0.7), Y(0.38)), (X(-0.4), Y(-0.1)), (X(0.3), Y(-0.14)), (X(0.62), Y(0.2)), (X(0.75), Y(0.32)), (X(0.3), Y(0.22)), (X(-0.3), Y(0.24))], cs, OL, ow)
    elif sb == "lechero":
        L.poly([(X(-0.38), Y(0.25)), (X(-0.34), Y(-0.08)), (X(0.36), Y(-0.08)), (X(0.4), Y(0.25))], cs, OL, ow)
        L.poly([(X(0.1), Y(0.2)), (X(0.6), Y(0.24)), (X(0.56), Y(0.3)), (X(0.05), Y(0.28))], OL)
    elif sb == "chef":
        L.poly([(X(-0.34), Y(0.24)), (X(-0.3), Y(0.0)), (X(0.32), Y(0.0)), (X(0.36), Y(0.24))], cs, OL, ow)
        L.ell(X(0.0), Y(-0.08), 0.4 * u, 0.22 * u, cs, OL, ow)
    if c["gorro_pan"]:
        L.poly([(X(-0.36), Y(0.24)), (X(-0.32), Y(0.02)), (X(0.34), Y(0.02)), (X(0.38), Y(0.24))], (232, 224, 206), OL, ow)
    img = L.final()
    if tinte is None:
        img = claroscuro(img, (luz[0] * mira, luz[1]), k=0.2, fuerza=0.6, ref=int(2.0 * u))
    if mira < 0:
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
    if tinte is not None:
        col, t = tinte
        a = np.asarray(img).astype(np.float32)
        a[..., :3] = a[..., :3] * (1 - t) + np.array(col, np.float32) * t
        img = Image.fromarray(a.astype(np.uint8), "RGBA")
    pies = (wpx / 2, sy + (cab - 0.12 + 0.18) * u * k / k)
    return img, (wpx / 2, sy + (cab + 0.06) * u)


# ------------------------------------------------------------------ partículas y efectos
class Particulas:
    def __init__(self, tipo, n, seed=0):
        self.tipo = tipo
        r = np.random.default_rng(seed)
        self.x = r.uniform(0, W, n); self.y = r.uniform(0, H, n)
        self.s = r.uniform(0.4, 1.0, n); self.ph = r.uniform(0, 6.28, n)

    def dibujar(self, img, t):
        d = ImageDraw.Draw(img, "RGBA")
        tp = self.tipo
        if tp == "lluvia":
            for x, y, s in zip(self.x, self.y, self.s):
                yy = (y + t * 1500 * s) % (H + 80) - 40
                xx = (x - t * 220 * s) % W
                d.line([(xx, yy), (xx - 9 * s, yy + 46 * s)], fill=(200, 205, 205, int(70 * s)), width=2 if s > .8 else 1)
        elif tp in ("polvo", "harina"):
            col = (255, 230, 180) if tp == "polvo" else (245, 240, 230)
            for x, y, s, ph in zip(self.x, self.y, self.s, self.ph):
                xx = (x + math.sin(t * 0.6 + ph) * 30 + t * 12) % W
                yy = (y + math.cos(t * 0.4 + ph) * 20 - t * 6 * s) % H
                r = 1.5 + s * 2.5
                d.ellipse([xx - r, yy - r, xx + r, yy + r], fill=col + (int(70 * s),))
        elif tp == "brasas":
            for x, y, s, ph in zip(self.x, self.y, self.s, self.ph):
                yy = H - ((H - y + t * 90 * s) % H)
                xx = x + math.sin(t * 2 + ph) * 18
                r = 1.5 + s * 2
                d.ellipse([xx - r, yy - r, xx + r, yy + r], fill=(255, 150 + int(60 * s), 60, int(200 * s)))
        elif tp == "gaviotas":
            for i, (x, y, s, ph) in enumerate(zip(self.x[:5], self.y[:5] * 0.4, self.s, self.ph)):
                xx = (x + t * 80 * s) % (W + 200) - 100
                yy = y + math.sin(t + ph) * 10
                f = math.sin(t * 7 + ph) * 10 * s
                d.line([(xx - 22 * s, yy - f), (xx, yy), (xx + 22 * s, yy - f)], fill=(40, 34, 30, 200), width=3)
        elif tp == "salpicadura":
            for x, y, s, ph in zip(self.x, self.y, self.s, self.ph):
                k = ((t * 1.4 + ph) % 1.0)
                if k < 0.5:
                    xx = x; yy = H - k * 500 * s + k * k * 900
                    r = 2 + s * 3
                    d.ellipse([xx - r, yy - r, xx + r, yy + r], fill=(220, 226, 220, int(160 * (1 - k * 2))))
        elif tp == "vidrio":
            for x, y, s, ph in zip(self.x, self.y, self.s, self.ph):
                k = ((t * 0.9 + ph) % 1.0)
                xx = x + math.cos(ph) * k * 300; yy = H * 0.85 - math.sin(ph) * k * 400 + k * k * 600
                d.polygon([(xx, yy), (xx + 8 * s, yy + 3), (xx + 2, yy + 10 * s)], fill=(220, 230, 220, int(200 * (1 - k))))


def capa_niebla(seed, alto=0.5, densidad=0.45, col=(200, 190, 170)):
    r = np.random.default_rng(seed)
    n = r.normal(0, 1, (12, 40)).astype(np.float32)
    n = cv2.resize(n, (LW, int(LH * alto)), interpolation=cv2.INTER_CUBIC)
    n = (n - n.min()) / (n.max() - n.min())
    g = np.linspace(0, 1, n.shape[0])[:, None]
    a = np.clip(n * densidad * 255 * np.sin(g * math.pi), 0, 255)
    img = np.zeros((LH, LW, 4), np.uint8)
    y0 = LH - n.shape[0]
    img[y0:, :, :3] = col
    img[y0:, :, 3] = a.astype(np.uint8)
    return Image.fromarray(img, "RGBA")


def capa_humo(seed, col=(210, 190, 160), dens=0.35):
    r = np.random.default_rng(seed)
    n = r.normal(0, 1, (8, 22)).astype(np.float32)
    n = cv2.resize(n, (LW, LH), interpolation=cv2.INTER_CUBIC)
    n = (n - n.min()) / (n.max() - n.min())
    a = np.clip((n - 0.35) * 2 * dens * 255, 0, 255).astype(np.uint8)
    img = np.zeros((LH, LW, 4), np.uint8)
    img[..., :3] = col
    img[..., 3] = a
    return Image.fromarray(img, "RGBA")


# ------------------------------------------------------------------ postproceso (viñeta, grano, franjas, tono)
_vig = None
_grain = None


def _prep_post():
    global _vig, _grain
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    _vig = np.clip(1.0 - 0.55 * np.clip(d - 0.45, 0, 1) ** 1.6, 0.25, 1.0).astype(np.float32)
    r = np.random.default_rng(7)
    _grain = [(r.normal(0, 1, (H // 2, W // 2)) * 9).astype(np.float32) for _ in range(6)]
    _grain = [cv2.resize(g, (W, H), interpolation=cv2.INTER_LINEAR) for g in _grain]


def postproceso(arr, fi, latido=0.0, franjas=True, flash=0.0):
    if _vig is None:
        _prep_post()
    a = arr.astype(np.float32)
    v = _vig if latido <= 0 else np.clip(_vig - latido * (1 - _vig) * 1.4, 0.05, 1)
    a *= v[..., None]
    a += _grain[fi % 6][..., None]
    if flash > 0:
        a = a * (1 - flash) + 255 * flash
    a = np.clip(a, 0, 255).astype(np.uint8)
    if franjas:
        a[:44] = 0
        a[H - 44:] = 0
    return a


# ------------------------------------------------------------------ subtítulos
def partir_sub(texto, maxc=46):
    """Divide en bloques de hasta 2 líneas."""
    pal = texto.split()
    lineas, cur = [], ""
    for p in pal:
        if len(cur) + len(p) + 1 > maxc and cur:
            lineas.append(cur); cur = p
        else:
            cur = (cur + " " + p).strip()
    if cur:
        lineas.append(cur)
    bloques = []
    for i in range(0, len(lineas), 2):
        bloques.append("\n".join(lineas[i:i + 2]))
    return bloques


_subcache = {}


def sub_img(txt, col=(255, 255, 255)):
    k = (txt, col)
    if k in _subcache:
        return _subcache[k]
    f = font(F_SUBB, 44)
    tmp = Image.new("RGBA", (W, 200))
    d = ImageDraw.Draw(tmp)
    d.multiline_text((W / 2, 100), txt, font=f, fill=col + (255,), anchor="mm", align="center", stroke_width=5,
                     stroke_fill=(0, 0, 0, 255), spacing=6)
    bb = tmp.getbbox()
    im = tmp.crop(bb) if bb else tmp
    _subcache[k] = im
    return im


# ------------------------------------------------------------------ audio
SR = 44100


def leer_wav(p):
    w = wave.open(p)
    n = w.getnframes(); sr = w.getframerate(); ch = w.getnchannels()
    a = np.frombuffer(w.readframes(n), np.int16).astype(np.float32) / 32768
    if ch == 2:
        a = a.reshape(-1, 2).mean(1)
    if sr != SR:
        a = np.interp(np.linspace(0, len(a), int(len(a) * SR / sr), endpoint=False), np.arange(len(a)), a)
    return a


def escribir_wav(p, a):
    a = np.clip(a, -1, 1)
    if a.ndim == 1:
        a = np.stack([a, a], 1)
    w = wave.open(p, "wb"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((a * 32767).astype(np.int16).tobytes()); w.close()


def env(n, a=0.005, r=0.1):
    e = np.ones(n, np.float32)
    na, nr = int(a * SR), int(r * SR)
    if na: e[:na] = np.linspace(0, 1, na)
    if nr and nr < n: e[-nr:] *= np.linspace(1, 0, nr)
    return e


def tono(f, dur, tipo="sin", amp=0.3, a=0.01, r=0.2):
    n = int(dur * SR); t = np.arange(n) / SR
    if tipo == "sin":
        s = np.sin(2 * np.pi * f * t)
    elif tipo == "saw":
        s = sum(np.sin(2 * np.pi * f * k * t) / k for k in range(1, 7))
    elif tipo == "pluck":  # mandolina / piano simple
        s = sum(np.sin(2 * np.pi * f * k * t) * (0.6 ** k) for k in range(1, 6)) * np.exp(-t * 5)
    elif tipo == "piano":
        s = sum(np.sin(2 * np.pi * f * k * t) * (0.5 ** k) for k in range(1, 7)) * np.exp(-t * 2.8)
    elif tipo == "bass":
        s = (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t)) * np.exp(-t * 4)
    elif tipo == "acordeon":
        s = (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 1.004 * t) + 0.3 * np.sin(4 * np.pi * f * t)
             + 0.2 * np.sign(np.sin(2 * np.pi * f * t)) * 0.3)
    else:
        s = np.sin(2 * np.pi * f * t)
    return (s * amp * env(n, a, r)).astype(np.float32)


def ruido(dur, amp=0.3, lp=None, hp=None, seed=0):
    r = np.random.default_rng(seed)
    s = r.normal(0, 1, int(dur * SR)).astype(np.float32)
    if lp:
        k = max(1, int(SR / lp)); s = np.convolve(s, np.ones(k) / k, "same")
    if hp:
        k = max(1, int(SR / hp)); s = s - np.convolve(s, np.ones(k) / k, "same")
    s /= (np.abs(s).max() + 1e-6)
    return s * amp


def mf(n):  # midi -> Hz
    return 440 * 2 ** ((n - 69) / 12)


def add(buf, s, t0):
    i = int(t0 * SR)
    if i >= len(buf) or i + len(s) <= 0:
        return
    j = min(len(buf), i + len(s))
    buf[max(0, i):j] += s[max(0, -i):j - i]


def musica(estilo, dur, seed=0):
    """Música procedural de época. estilos: italia, jazz, tension, mar, final."""
    buf = np.zeros(int((dur + 2) * SR), np.float32)
    rng = random.Random(seed)
    if estilo == "italia":   # vals en la menor: acordeón + mandolina en trémolo
        bpm = 132; b = 60 / bpm
        prog = [(57, [57, 60, 64]), (62, [62, 65, 69]), (52, [56, 59, 64]), (57, [57, 60, 64]),
                (53, [57, 60, 65]), (50, [53, 57, 62]), (52, [56, 59, 62]), (57, [57, 60, 64])]
        mel = [76, 74, 72, 71, 72, 74, 76, 77, 76, 74, 72, 71, 69, 71, 72, 69]
        t = 0; i = 0
        while t < dur:
            root, ch = prog[(i // 3) % len(prog)]
            beat = i % 3
            if beat == 0:
                add(buf, tono(mf(root - 12), b * 0.9, "bass", 0.22), t)
            else:
                for n in ch:
                    add(buf, tono(mf(n), b * 0.6, "acordeon", 0.035, 0.02, 0.1), t)
            if i % 3 == 0:
                m = mel[(i // 3) % len(mel)]
                for k in range(6):   # trémolo
                    add(buf, tono(mf(m), b / 2.2, "pluck", 0.07), t + k * b / 2)
            t += b; i += 1
    elif estilo == "jazz":   # swing: contrabajo caminante + piano + escobillas
        bpm = 168; b = 60 / bpm
        prog = [(50, [65, 69, 72]), (55, [65, 67, 71]), (48, [64, 67, 71]), (57, [61, 64, 67])]
        walk = [0, 4, 7, 9]
        t = 0; i = 0
        while t < dur:
            root, ch = prog[(i // 4) % 4]
            add(buf, tono(mf(root - 12 + walk[i % 4]), b * 0.95, "bass", 0.26), t)
            sw = b * 0.66
            add(buf, ruido(0.06, 0.05, hp=3000, seed=i) * np.exp(-np.arange(int(0.06 * SR)) / 800), t)
            add(buf, ruido(0.05, 0.03, hp=4000, seed=i + 99) * np.exp(-np.arange(int(0.05 * SR)) / 600), t + sw)
            if i % 2 == 1:
                for n in ch:
                    add(buf, tono(mf(n), 0.25, "piano", 0.05), t + (0.0 if rng.random() < .6 else sw))
            if i % 8 == 6:
                for k, n in enumerate([ch[-1] + 12, ch[-2] + 12, ch[-1] + 14]):
                    add(buf, tono(mf(n), 0.3, "piano", 0.05), t + k * sw / 1.5)
            t += b; i += 1
    elif estilo == "tension":   # zumbido grave + pizzicato ostinato + timbal
        drone = tono(mf(38), dur + 1, "saw", 0.06, 1.5, 1.5)
        trem = 0.75 + 0.25 * np.sin(2 * np.pi * 0.25 * np.arange(len(drone)) / SR)
        add(buf, drone * trem, 0)
        b = 60 / 96
        pat = [50, 50, 53, 50, 49, 50, 56, 53]
        t = 0; i = 0
        while t < dur:
            add(buf, tono(mf(pat[i % 8]), 0.3, "pluck", 0.09), t)
            if i % 16 == 0:
                add(buf, tono(55, 1.2, "bass", 0.3) + ruido(1.2, 0.04, lp=200, seed=i), t)
            t += b / 2; i += 1
    elif estilo == "mar":
        for k, n in enumerate([38, 45, 50, 53]):
            s = tono(mf(n), dur + 1, "sin", 0.05, 3, 3)
            s *= 0.7 + 0.3 * np.sin(2 * np.pi * (0.07 + k * 0.03) * np.arange(len(s)) / SR + k)
            add(buf, s, 0)
        b = 60 / 70; t = 0; i = 0
        while t < dur:
            add(buf, tono(mf([62, 65, 69, 67][i % 4]), 1.6, "pluck", 0.05), t)
            t += b * 2; i += 1
    elif estilo == "final":    # vals cálido en do mayor
        bpm = 112; b = 60 / bpm
        prog = [(48, [60, 64, 67]), (53, [60, 65, 69]), (55, [59, 62, 67]), (48, [60, 64, 67])]
        mel = [72, 76, 79, 77, 76, 74, 72, 74, 76, 72, 71, 72]
        t = 0; i = 0
        while t < dur:
            root, ch = prog[(i // 6) % 4]
            beat = i % 3
            if beat == 0:
                add(buf, tono(mf(root - 12), b, "bass", 0.2), t)
            else:
                for n in ch:
                    add(buf, tono(mf(n), b * 0.7, "piano", 0.04), t)
            if i % 3 == 0:
                add(buf, tono(mf(mel[(i // 3) % len(mel)]), b * 2.6, "piano", 0.09), t)
            t += b; i += 1
    # reverb barata
    out = buf.copy()
    for dly, g in ((0.031, 0.35), (0.067, 0.25), (0.113, 0.18), (0.171, 0.12)):
        k = int(dly * SR); out[k:] += buf[:-k] * g
    return out[:int(dur * SR)]


def sfx(nombre, seed=0):
    if nombre == "whoosh":
        n = ruido(0.5, 0.25, lp=1500, seed=seed); e = np.sin(np.linspace(0, np.pi, len(n))) ** 2
        return n * e
    if nombre == "golpes":
        out = np.zeros(int(1.4 * SR), np.float32)
        for k in range(3):
            g = (tono(70, 0.25, "bass", 0.8) + ruido(0.25, 0.4, lp=500, seed=k) * np.exp(-np.arange(int(0.25 * SR)) / 1500))
            add(out, g, k * 0.32)
        return out
    if nombre == "trueno":
        n = ruido(3.0, 0.5, lp=180, seed=seed); return n * np.exp(-np.linspace(0, 4, len(n)))
    if nombre == "latido":
        out = np.zeros(int(1.0 * SR), np.float32)
        add(out, tono(52, 0.18, "bass", 0.7), 0); add(out, tono(48, 0.2, "bass", 0.55), 0.24)
        return out
    if nombre == "silbato":
        t = np.arange(int(0.9 * SR)) / SR
        return (np.sin(2 * np.pi * (2800 + 60 * np.sin(2 * np.pi * 30 * t)) * t) * 0.18 * env(len(t), 0.01, 0.1)).astype(np.float32)
    if nombre == "vidrio":
        out = np.zeros(int(1.0 * SR), np.float32)
        for k in range(6):
            add(out, ruido(0.2, 0.3, hp=3000, seed=k + seed) * np.exp(-np.arange(int(0.2 * SR)) / 900), k * 0.09)
            add(out, tono(2500 + 700 * k, 0.3, "sin", 0.06, 0.001, 0.25), k * 0.09)
        return out
    if nombre == "campanita":
        return tono(1760, 1.2, "pluck", 0.25) + tono(2637, 1.2, "pluck", 0.12)
    if nombre == "golpe_titulo":
        return tono(45, 1.8, "bass", 0.7) + ruido(1.8, 0.15, lp=300, seed=3) * np.exp(-np.linspace(0, 6, int(1.8 * SR)))
    if nombre == "mirilla":
        return ruido(0.15, 0.4, lp=2000, seed=5) * np.exp(-np.linspace(0, 5, int(0.15 * SR)))
    if nombre == "motor":
        t = np.arange(int(1.0 * SR)) / SR
        return (np.sign(np.sin(2 * np.pi * 38 * t)) * 0.05 + ruido(1.0, 0.04, lp=300, seed=8)).astype(np.float32)
    return np.zeros(100, np.float32)


AMB = {  # sonidos ambiente en bucle
    "lluvia": lambda d: ruido(d, 0.06, lp=4000, hp=400, seed=11),
    "olas": lambda d: ruido(d, 0.09, lp=600, seed=12) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.12 * np.arange(int(d * SR)) / SR)),
    "calle": lambda d: ruido(d, 0.025, lp=1200, seed=13),
    "fuego": lambda d: ruido(d, 0.03, lp=900, seed=14) * (np.random.default_rng(3).random(int(d * SR)) > 0.0005).astype(np.float32) + (np.random.default_rng(4).random(int(d * SR)) > 0.9997) * 0.25,
}


# ------------------------------------------------------------------ cámara
def camara(tipo, u, dur, seed=0):
    """Devuelve (sx, sy, zoom, ox, oy): desplazamiento de paralaje (px a prof=1), zoom extra y temblor."""
    e = u * u * (3 - 2 * u)   # suavizado
    sx = sy = 0.0; z = 1.0; ox = oy = 0.0
    if tipo == "push":
        z = 1.0 + 0.09 * e; sx = 30 * e
    elif tipo == "pull":
        z = 1.09 - 0.09 * e; sx = -30 * e
    elif tipo == "pan_r":
        sx = -170 + 340 * e; z = 1.02
    elif tipo == "pan_l":
        sx = 170 - 340 * e; z = 1.02
    elif tipo == "tilt_up":
        sy = 80 - 160 * e; z = 1.03
    elif tipo == "tilt_down":
        sy = -80 + 160 * e; z = 1.03
    elif tipo == "shake":
        z = 1.05 + 0.02 * e
        amp = 10 * (1 - u) + 3
        ox = amp * math.sin(u * dur * 37 + seed); oy = amp * math.cos(u * dur * 29 + seed * 2)
    else:  # drift
        sx = -40 + 80 * e; z = 1.0 + 0.025 * e
    return sx, sy, z, ox, oy


# ------------------------------------------------------------------ RENDER DE UN ACTO
ENC = {  # encuadre -> (u como fracción de CH, referencia)
    "full": 0.66, "medio": 0.205, "cara": 0.40,
}
VOZ_A_PERS = {"CAR": "carmine", "FRA": "frankie", "PINO": "pino", "TU": "tu", "IZZY": "izzy", "AGE": "agente"}


def _sprite_personaje(quien, x, enc, pose, mira, luz, boca, ojos, seed=0):
    cab = PERS[quien]["cab"]
    if enc == "full":
        u = CH * 0.66 / 7.4
        img, (fx, fy) = dibujar_persona(quien, u, pose, boca, ojos, mira, luz)
        px = x * CW - fx
        py = CH * 0.94 - fy
    else:
        u = CH * ENC[enc]
        top = CH * (0.17 if enc == "medio" else 0.19)
        rec = (CH - top) + 0.45 * u + 20
        img, (fx, fy) = dibujar_persona(quien, u, pose, boca, ojos, mira, luz, recorte=rec)
        px = x * CW - img.width / 2
        py = top - 0.45 * u
    return img, (int(px), int(py)), u


def _grupo_gente(x, tinte, seed, luz):
    """Pequeño grupo de figuras de fondo (siluetas tenues)."""
    r = random.Random(seed)
    u = CH * 0.5 / 7.4
    L = Image.new("RGBA", (int(u * 9), int(u * 8.2)), (0, 0, 0, 0))
    hats = ["fedora", "gorra", "bombin", None, "fedora_lad"]
    for i in range(3):
        nm = "_g%d" % i
        definir_personaje(nm, sombrero=r.choice(hats), saco=r.choice([P("mid"), P("dark"), (90, 70, 60)]),
                          pantalon=P("dark"), ancho=r.uniform(0.9, 1.15), panza=r.choice([0, 0, 0.2]),
                          bigote=r.choice([None, P("ink")]), mangas_cortas=r.random() < 0.3, chaleco=P("dark"))
        im, (fx, fy) = dibujar_persona(nm, u * r.uniform(0.9, 1.05), r.choice(["idle", "idle", "brazos", "habla_mano"]),
                                       0, 1, r.choice([-1, 1]), luz, tinte=(tinte, 0.55))
        L.paste(im, (int(u * (1.2 + i * 2.6) - fx), int(L.height - 4 - fy)), im)
    return L, (int(x * CW - L.width / 2), int(CH * 0.9 - L.height))


class Plano:
    def __init__(self, esc_mod, linea, dur, voz, t_voz, voz_amp, seed):
        spk, texto, p = linea
        self.spk, self.texto, self.p, self.dur, self.seed = spk, texto, p, dur, seed
        self.voz_amp, self.t_voz = voz_amp, t_voz
        self.capas = esc_mod.capas(p["esc"], p.get("ins"))
        luz = esc_mod.luz(p["esc"])
        self.luz = luz
        tinte = esc_mod.tinte_fondo(p["esc"])
        self.chars = []
        hablante = VOZ_A_PERS.get(spk)
        for k, (quien, x, enc, pose, mira) in enumerate(p["ch"]):
            if quien == "gente":
                im, pos = _grupo_gente(x, tinte, seed * 10 + k, luz)
                self.chars.append(dict(var={(0, 1): im}, pos=pos, prof=0.6, habla=False, quien=quien, enc="fondo"))
                continue
            habla = hablante is not None and quien.startswith(hablante)
            var = {}
            for b in ((0, 1) if habla else (0,)):
                for o in (1, 0):
                    im, pos, u = _sprite_personaje(quien, x, enc, pose, mira, luz, b, o, seed)
                    var[(b, o)] = im
            prof = {"full": 0.85, "medio": 1.0, "cara": 1.1}[enc]
            self.chars.append(dict(var=var, pos=pos, prof=prof, habla=habla, quien=quien, enc=enc, u=u, x=x))
        # foco de cámara: cabeza del primer personaje no-fondo
        self.foco = (CW / 2, CH * 0.45)
        for c in self.chars:
            if c["enc"] != "fondo":
                if c["enc"] == "full":
                    self.foco = (c["x"] * CW, CH * 0.4)
                elif c["enc"] == "medio":
                    self.foco = (c["x"] * CW, CH * 0.3)
                else:
                    self.foco = (c["x"] * CW, CH * 0.33)
                break
        fx = p["fx"]
        self.part = []
        for nm, n in (("lluvia", 260), ("polvo", 70), ("harina", 90), ("brasas", 40), ("gaviotas", 5), ("salpicadura", 30), ("vidrio", 25)):
            if nm in fx:
                self.part.append(Particulas(nm, n, seed))
        if "lluvia_ventana" in fx and "lluvia" not in fx:
            pass
        self.over = []   # capas de humo/niebla con deriva
        if "niebla" in fx:
            self.over.append((capa_niebla(seed, 0.55, 0.5, esc_mod.col_niebla(p["esc"])), 1.2, 25))
        if "humo" in fx or "humo_cigarro" in fx:
            self.over.append((capa_humo(seed, (200, 180, 150), 0.28 if "humo" in fx else 0.2), 0.9, 12))
        self.screen_fx = esc_mod.fx_pantalla(p["esc"], fx, seed)   # función (img, t, u) -> None
        self.inset = esc_mod.inserto_overlay(p.get("ins")) if p.get("ins") else None
        self.cam = p["cam"]
        self.lat = "latido" in fx
        cols = (255, 255, 255) if spk == "N" else (255, 214, 140)
        bl = partir_sub(texto)
        tot = sum(len(b) for b in bl)
        self.subs = []
        acc = 0
        vd = max(0.5, dur - t_voz - 0.25)
        for b in bl:
            a0 = t_voz + vd * acc / tot
            acc += len(b)
            self.subs.append((a0, t_voz + vd * acc / tot, sub_img(b, cols)))

    def frame(self, t, fi):
        u = min(1.0, t / max(0.01, self.dur))
        sx, sy, z, ox, oy = camara(self.cam, u, self.dur, self.seed)
        base = None
        for img, prof in self.capas:
            x0 = int(MX + sx * prof); y0 = int(MY + sy * prof)
            cr = img.crop((x0, y0, x0 + CW, y0 + CH))
            if base is None:
                base = cr.convert("RGBA") if cr.mode != "RGBA" else cr
            else:
                base.alpha_composite(cr)
        blink = (int(t * FPS) % 110) < 4
        for c in self.chars:
            b = 0
            if c["habla"] and self.voz_amp is not None:
                k = int((t - self.t_voz) * FPS)
                if 0 <= k < len(self.voz_amp):
                    b = 1 if self.voz_amp[k] > 0.06 else 0
            o = 0 if blink else 1
            im = c["var"].get((b, o)) or c["var"].get((0, o)) or c["var"][(0, 1)]
            bob = int(2.5 * math.sin(t * 2.1 + c["pos"][0] * 0.01)) if c["enc"] != "fondo" else 0
            base.paste(im, (int(c["pos"][0] + sx * c["prof"]), int(c["pos"][1] + sy * c["prof"] + bob)), im)
        for img, prof, vel in self.over:
            x0 = int((MX + sx * prof + t * vel) % (LW - CW)); y0 = MY
            base.alpha_composite(img.crop((x0, y0, x0 + CW, y0 + CH)))
        # cámara: recorte + zoom hacia el foco
        zz = 1.1 * z
        cw, chh = CW / zz, CH / zz
        k = min(1.0, (z - 1.0) * 6)
        cx = CW / 2 + (self.foco[0] - CW / 2) * k * 0.6 + ox
        cy = CH / 2 + (self.foco[1] - CH / 2) * k * 0.4 + oy
        cx = min(max(cx, cw / 2), CW - cw / 2); cy = min(max(cy, chh / 2), CH - chh / 2)
        arr = np.asarray(base)[..., :3]
        x0, y0 = cx - cw / 2, cy - chh / 2
        M = np.float32([[W / cw, 0, -x0 * W / cw], [0, H / chh, -y0 * H / chh]])
        out = cv2.warpAffine(arr, M, (W, H), flags=cv2.INTER_LINEAR)
        img = Image.fromarray(out)
        for pt in self.part:
            pt.dibujar(img, t + self.seed)
        if self.screen_fx:
            self.screen_fx(img, t, u)
        if self.inset is not None:
            a = min(1.0, max(0.0, (t - 0.25) / 0.35))
            if a > 0:
                ins = self.inset
                if a < 1:
                    ins = ins.copy(); ins.putalpha(ins.getchannel("A").point(lambda v: int(v * a)))
                img.paste(ins, (0, 0), ins)
        lat = 0.0
        if self.lat:
            ph = (t % 1.0)
            lat = 0.35 * (math.exp(-((ph - 0.05) / 0.06) ** 2) + 0.7 * math.exp(-((ph - 0.3) / 0.06) ** 2))
        flash = max(0.0, 0.35 * (1 - t / 0.12)) if t < 0.12 else 0.0
        arr = postproceso(np.asarray(img), fi, lat, True, flash)
        img = Image.fromarray(arr)
        for a0, a1, si in self.subs:
            if a0 <= t < a1:
                img.paste(si, ((W - si.width) // 2, H - 62 - si.height), si)
        return np.asarray(img)


class TituloActo:
    def __init__(self, titulo, dur, n):
        self.dur, self.titulo, self.n = dur, titulo, n
        L = Lienzo(W, H, P("ink"), 1)
        a, b = titulo.split(":", 1)
        L.text((W / 2, H / 2 - 95), a.strip(), font(F_TIT, 64), P("red"))
        L.text((W / 2, H / 2 + 20), b.strip(), font(F_TIT, 128), P("paper"))
        L.rect(W / 2 - 300, H / 2 + 110, W / 2 + 300, H / 2 + 116, P("red"))
        L.text((W / 2, H / 2 + 165), "NUEVA YORK · 1925", font(F_TYPE, 30), P("light"))
        self.img = L.final().convert("RGB")
        self.arr = np.asarray(self.img)

    def frame(self, t, fi):
        u = t / self.dur
        z = 1.0 + 0.04 * u
        M = np.float32([[z, 0, -(z - 1) * W / 2], [0, z, -(z - 1) * H / 2]])
        out = cv2.warpAffine(self.arr, M, (W, H))
        f = min(1, t / 0.3) * min(1, (self.dur - t) / 0.3)
        out = (out.astype(np.float32) * max(0, f)).astype(np.uint8)
        return postproceso(out, fi, 0, True)


def construir_linea_tiempo(acto, voz_dir, gap=0.32):
    items = []
    idx = acto["idx0"]
    lineas = list(acto.get("gancho", []))
    for ln in lineas:
        items.append(("linea", ln, idx)); idx += 1
    items.append(("titulo", acto["titulo"], None))
    for ln in acto["lineas"]:
        items.append(("linea", ln, idx)); idx += 1
    tl = []
    t = 0.0
    for kind, data, i in items:
        if kind == "titulo":
            d = 3.0
            tl.append(dict(kind=kind, data=data, t0=t, dur=d)); t += d
            continue
        wavp = os.path.join(voz_dir, "v%03d_f.wav" % i)
        a = leer_wav(wavp)
        vd = len(a) / SR
        extra = 0.0
        p = data[2]
        if p.get("ins") in ("titulo_video",):
            extra = 1.4
        if p.get("ins") in ("proximo",):
            extra = 2.5
        d = 0.18 + vd + gap + extra
        tl.append(dict(kind=kind, data=data, t0=t, dur=d, voz=a, t_voz=0.18, idx=i)); t += d
    return tl, t


def audio_acto(tl, total, esc_mod, ruta):
    n = int((total + 0.5) * SR)
    voz = np.zeros(n, np.float32); fx = np.zeros(n, np.float32); amb = np.zeros(n, np.float32)
    musc = np.zeros(n, np.float32)
    # música por segmentos con fundido
    segs = []
    prev = "tension"
    for it in tl:
        if it["kind"] == "titulo":
            m = None
        else:
            m = esc_mod.mood(it["data"][2]["esc"], it["data"][2].get("ins"))
        m = m or prev
        prev = m
        segs.append((it["t0"], it["dur"], m))
    pistas = {}
    for m in set(s[2] for s in segs):
        pistas[m] = musica(m, total + 1, seed=len(m))
    gain = {m: np.zeros(n, np.float32) for m in pistas}
    for t0, d, m in segs:
        i0 = int(t0 * SR); i1 = min(n, int((t0 + d) * SR))
        gain[m][i0:i1] = 1.0
    kf = int(0.8 * SR)
    for m in pistas:
        g = np.convolve(gain[m], np.ones(kf) / kf, "same")
        musc += pistas[m][:n] * g * 0.55
    for it in tl:
        t0 = it["t0"]
        if it["kind"] == "titulo":
            add(fx, sfx("golpe_titulo") * 0.8, t0)
            continue
        add(fx, sfx("whoosh", it["idx"]) * 0.22, t0 - 0.15)
        add(voz, it["voz"], t0 + it["t_voz"])
        p = it["data"][2]
        f = p["fx"]
        if "golpes" in f:
            add(fx, sfx("golpes") * 0.9, t0 + 0.05)
        if "latido" in f:
            for k in range(int(it["dur"])):
                add(fx, sfx("latido") * 0.5, t0 + k)
        if "silbato" in f or p.get("ins") == "silbato":
            add(fx, sfx("silbato"), t0 + 0.3)
        if "vidrio" in f:
            add(fx, sfx("vidrio", it["idx"]) * 0.7, t0 + 0.6)
        if "campanita" in it["data"][1]:
            add(fx, sfx("campanita") * 0.6, t0 + 0.4)
        if p.get("ins") == "mirilla":
            add(fx, sfx("mirilla") * 0.8, t0 + 0.4)
        if p["esc"] in ("bote",):
            m = sfx("motor"); 
            for k in range(int(it["dur"]) + 1):
                add(amb, m * 0.6, t0 + k)
        if p.get("ins") == "titulo_video":
            add(fx, sfx("golpe_titulo"), t0 + 0.1)
        if "reflector" in f:
            add(fx, tono(110, it["dur"], "saw", 0.03, 0.5, 0.5), t0)
        ambs = esc_mod.ambiente(p["esc"], f)
        for a in ambs:
            s = AMB[a](it["dur"] + 0.3)
            add(amb, s * env(len(s), 0.15, 0.15), t0)
        if "lluvia" in f and it["idx"] % 5 == 0:
            add(fx, sfx("trueno", it["idx"]) * 0.5, t0 + 0.5)
    # ducking de música bajo la voz
    envv = np.convolve(np.abs(voz), np.ones(4410) / 4410, "same")
    duck = 1.0 - 0.5 * np.clip(envv * 12, 0, 1)
    mixa = voz * 1.0 + fx * 0.8 + amb * 0.9 + musc * duck * 0.8
    pk = np.abs(mixa).max()
    if pk > 0.98:
        mixa *= 0.98 / pk
    escribir_wav(ruta, mixa)


def render_acto(acto, esc_mod, salida, voz_dir, solo=None, preview=None):
    tl, total = construir_linea_tiempo(acto, voz_dir)
    base = os.path.splitext(salida)[0]
    if preview:   # lista de índices de ítems -> png grande del cuadro medio
        for k in preview:
            it = tl[k]
            ob = _obj(it, esc_mod, acto)
            fr = ob.frame(it["dur"] * 0.55, 3)
            Image.fromarray(fr).save("%s_prev_%02d.png" % (base, k))
        return tl, total
    wav = base + "_audio.wav"
    audio_acto(tl, total, esc_mod, wav)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "%dx%d" % (W, H), "-r", str(FPS),
           "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "160k", "-shortest", salida]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    fi = 0
    nfr_total = int(round(total * FPS))
    for it in tl:
        ob = _obj(it, esc_mod, acto)
        n0 = int(round(it["t0"] * FPS)); n1 = int(round((it["t0"] + it["dur"]) * FPS))
        for f in range(n0, n1):
            t = f / FPS - it["t0"]
            pr.stdin.write(ob.frame(t, f).tobytes())
            fi += 1
        del ob
    pr.stdin.close(); pr.wait()
    return total


def _obj(it, esc_mod, acto):
    if it["kind"] == "titulo":
        return TituloActo(it["data"], it["dur"], acto["n"])
    a = it["voz"]
    hop = SR // FPS
    amp = np.array([np.abs(a[i:i + hop]).mean() for i in range(0, len(a), hop)]) * 4
    return Plano(esc_mod, it["data"], it["dur"], None, it["t_voz"], amp, it["idx"])
