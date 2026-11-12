"""Realce visual compartido para todos los episodios de Mundo Hipotético.

Uso dentro de episodio.py (después de definir los personajes y antes de los planos):

    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "motor"))
    import realce
    realce.aplicar(globals(), ["nico", "romano", "lion"])      # volumen a los personajes

y en frame(), justo antes de caption(img, T):

    img = realce.postproceso(img, T, tono="calido")

- volumen(): sombreado con luz desde arriba-izquierda, oclusión en los bordes y luz de contorno.
  Los personajes dejan de verse planos sin tener que redibujarlos.
- postproceso(): resplandor (bloom), corrección de color por ambiente, partículas de luz y grano fino.
- parpadeo(t) / respiracion(t): valores listos para animar ojos y cuerpo en nico() y similares.
"""
import math
import numpy as np
from PIL import Image, ImageFilter

# ------------------------------------------------------------------ personajes con volumen
RIM = {"calido": (255, 226, 170), "frio": (150, 210, 255), "noche": (170, 150, 255)}


def _sombrear(lay, rim_col=(255, 232, 190), fuerza=1.0):
    bb = lay.getbbox()
    if not bb:
        return None, None
    x0, y0, x1, y1 = bb
    pad = 12
    x0, y0 = max(0, x0 - pad), max(0, y0 - pad)
    x1, y1 = min(lay.width, x1 + pad), min(lay.height, y1 + pad)
    crop = lay.crop((x0, y0, x1, y1))
    c = np.asarray(crop).astype(np.float32)
    a = c[..., 3] / 255.0
    h, w = a.shape
    yy, xx = np.mgrid[0:h, 0:w]
    xx = xx / max(1, w - 1); yy = yy / max(1, h - 1)
    # luz general: más clara arriba-izquierda, más oscura abajo-derecha
    g = 1.10 - 0.30 * fuerza * (0.35 * xx + 0.65 * yy)
    # oclusión suave en los bordes de cada forma
    ab = np.asarray(crop.getchannel("A").filter(ImageFilter.GaussianBlur(max(3, h / 90)))).astype(np.float32) / 255.0
    ao = 0.80 + 0.20 * np.clip((ab - 0.45) * 2.2, 0, 1)
    # luz de contorno: borde que mira a la luz (arriba-izquierda)
    s = max(3, int(h / 120))
    sh = np.zeros_like(ab); sh[s:, s:] = ab[:-s, :-s]
    rim = np.clip(a - sh * 1.15, 0, 1) * a
    # sombra propia: borde que da la espalda a la luz
    sh2 = np.zeros_like(ab); sh2[:-s, :-s] = ab[s:, s:]
    back = np.clip(a - sh2 * 1.15, 0, 1) * a
    rgb = c[..., :3] * (g * ao * (1 - 0.35 * back))[..., None]
    rgb = rgb + rim[..., None] * np.array(rim_col, np.float32) * 0.55 * fuerza
    out = np.dstack([np.clip(rgb, 0, 255), c[..., 3]]).astype(np.uint8)
    return Image.fromarray(out, "RGBA"), (x0, y0)


def volumen(fn, ambiente="calido", fuerza=1.0):
    """Envuelve una función de dibujo fn(img, ...) para que el personaje salga con volumen."""
    def envuelta(img, *args, **kw):
        lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        fn(lay, *args, **kw)
        res, pos = _sombrear(lay, RIM.get(ambiente, RIM["calido"]), fuerza)
        if res is not None:
            img.alpha_composite(res, pos)
    envuelta.__wrapped__ = fn
    return envuelta


def aplicar(ns, nombres, ambiente="calido", fuerza=1.0):
    for n in nombres:
        if n in ns and not hasattr(ns[n], "__wrapped__"):
            ns[n] = volumen(ns[n], ambiente, fuerza)


# ------------------------------------------------------------------ animación de vida
def parpadeo(t, cada=3.1, fase=0.0):
    """0 = ojo abierto, 1 = cerrado. Parpadeo de ~0.13 s cada `cada` segundos (con doble parpadeo a veces)."""
    u = (t + fase) % cada
    k = 0.0
    for c in (0.0, 0.22 if int((t + fase) / cada) % 3 == 0 else -9):
        d = abs(u - c - 0.065)
        if d < 0.065:
            k = max(k, 1 - d / 0.065)
    return k


def respiracion(t, amp=1.0):
    """Desplazamiento vertical suave (px a escala 1) para que el personaje no se vea congelado."""
    return amp * 4.0 * math.sin(t * 2 * math.pi / 2.6)


# ------------------------------------------------------------------ posproceso del cuadro final
TONOS = {
    # (multiplicador sombras RGB, multiplicador luces RGB, saturación)
    "calido": ((0.96, 0.98, 1.06), (1.06, 1.01, 0.92), 1.12),
    "frio": ((0.92, 0.98, 1.10), (1.00, 1.02, 1.04), 1.08),
    "noche": ((0.90, 0.92, 1.12), (1.02, 0.98, 1.06), 1.05),
    "neutro": ((1.0, 1.0, 1.0), (1.0, 1.0, 1.0), 1.10),
}
_GRANO = None
_MOTAS = None


def _grano(w, h):
    global _GRANO
    if _GRANO is None:
        r = np.random.default_rng(11)
        _GRANO = [r.normal(0, 1, (h // 2, w // 2)).astype(np.float32) for _ in range(6)]
    return _GRANO


def postproceso(img, T, tono="calido", bloom=0.35, grano=3.0, motas=True, rayos=None):
    """img: PIL RGB o RGBA del tamaño final. Devuelve PIL RGBA."""
    rgb = img.convert("RGB")
    w, h = rgb.size
    a = np.asarray(rgb).astype(np.float32) / 255.0
    # bloom: lo brillante se ilumina alrededor
    if bloom > 0:
        small = rgb.resize((w // 4, h // 4), Image.BILINEAR)
        s = np.asarray(small).astype(np.float32) / 255.0
        lum = s.mean(axis=2, keepdims=True)
        br = np.clip((lum - 0.68) / 0.32, 0, 1) * s
        b = Image.fromarray((br * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(10)).resize((w, h), Image.BILINEAR)
        a = a + np.asarray(b).astype(np.float32) / 255.0 * bloom
    # color: tono de sombras/luces + curva S + saturación
    sh_m, hi_m, sat = TONOS.get(tono, TONOS["neutro"])
    lum = a.mean(axis=2, keepdims=True)
    mix = np.clip(lum, 0, 1)
    a = a * (np.array(sh_m) * (1 - mix) + np.array(hi_m) * mix)
    a = np.clip(a, 0, 1)
    a = a + 0.10 * (a - 0.5) * (1 - np.abs(2 * a - 1))  # contraste suave en medios tonos
    lum = a.mean(axis=2, keepdims=True)
    a = lum + (a - lum) * sat
    # grano fino animado
    if grano > 0:
        gs = _grano(w, h)
        g = gs[int(T * 24) % len(gs)]
        g = np.repeat(np.repeat(g, 2, axis=0), 2, axis=1)[:h, :w]
        a = a + (g * grano / 255.0)[..., None]
    if rayos:
        a = a + _rayos(w, h, rayos, T)
    out = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).convert("RGBA")
    if motas:
        _motas(out, T)
    return out


def _motas(img, T):
    """Partículas de luz flotando (polvo en el aire) para dar profundidad."""
    global _MOTAS
    w, h = img.size
    if _MOTAS is None:
        r = np.random.default_rng(5)
        _MOTAS = [(r.uniform(0, w), r.uniform(0, h), r.uniform(2, 6), r.uniform(10, 40), r.uniform(0, 6.28)) for _ in range(28)]
    lay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    from PIL import ImageDraw
    d = ImageDraw.Draw(lay)
    for x, y, s, v, ph in _MOTAS:
        yy = (y - T * v) % h
        xx = x + 18 * math.sin(T * 0.8 + ph)
        al = int(70 + 60 * math.sin(T * 2 + ph))
        d.ellipse([xx - s, yy - s, xx + s, yy + s], fill=(255, 245, 220, max(0, al)))
    img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(1.5)))


_RAYOS = {}
def _rayos(w, h, origen, T):
    """Rayos de luz suaves desde un punto (p. ej. (0.85, -0.05) = arriba a la derecha, en fracción del cuadro)."""
    key = (w, h, origen)
    if key not in _RAYOS:
        ox, oy = origen[0] * w, origen[1] * h
        yy, xx = np.mgrid[0:h // 4, 0:w // 4] * 4.0
        ang = np.arctan2(yy - oy, xx - ox)
        dist = np.sqrt((xx - ox) ** 2 + (yy - oy) ** 2) / h
        r = np.random.default_rng(3)
        fr = r.uniform(0, 6.28, 6); am = r.uniform(0.3, 1, 6); fq = r.integers(9, 31, 6)
        m = sum(a_ * np.cos(f_ * ang + p_) for a_, f_, p_ in zip(am, fq, fr))
        m = np.clip(m / 2.5, 0, 1) * np.exp(-dist * 1.6)
        im = Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(6)).resize((w, h), Image.BILINEAR)
        _RAYOS[key] = np.asarray(im).astype(np.float32) / 255.0
    m = _RAYOS[key] * (0.85 + 0.15 * math.sin(T * 0.9))
    return (m * 0.16)[..., None] * np.array([1.0, 0.93, 0.78], np.float32)
