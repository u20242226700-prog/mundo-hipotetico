"""Escenarios por capas con parallax + profundidad de campo, y efectos (fuego, humo, portal, chispas...)."""
import math
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1920
LW, LH = 1500, 2300           # tamaño de cada capa (margen para paneo y zoom)
F_BLACK = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
def font(s): return ImageFont.truetype(F_BLACK, int(s))

def _grad(stops, w=LW, h=LH):
    ys = np.linspace(0, 1, h)
    cols = np.zeros((h, 3), np.float32)
    for c in range(3):
        cols[:, c] = np.interp(ys, [s[0] for s in stops], [s[1][c] for s in stops])
    return np.repeat(cols[:, None, :], w, 1)

def _layer(w=LW, h=LH): return Image.new("RGBA", (w, h), (0, 0, 0, 0))

def _haze(lay, col, amount):
    a = np.array(lay).astype(np.float32)
    a[..., :3] = a[..., :3] * (1 - amount) + np.array(col, np.float32) * amount
    return Image.fromarray(a.astype(np.uint8), "RGBA")

GY = 1560   # línea del suelo en pantalla (pies de los personajes) con zoom 1

def valle(cueva=False, noche=0.0):
    """Capas del valle prehistórico al atardecer. Devuelve lista de (array RGBA float32, parallax)."""
    rng = np.random.default_rng(11)
    layers = []
    sky = _grad([(0, (78, 128, 205)), (0.32, (150, 160, 210)), (0.5, (255, 186, 140)), (0.62, (255, 222, 178)), (1, (255, 226, 190))])
    sky = Image.fromarray(np.dstack([sky, np.full(sky.shape[:2], 255)]).astype(np.uint8), "RGBA")
    d = ImageDraw.Draw(sky)
    cl = _layer(); dc = ImageDraw.Draw(cl)
    for k in range(7):
        cx, cy = rng.uniform(0, LW), rng.uniform(220, 900); s = rng.uniform(0.7, 1.5)
        for j in range(6):
            ox, oy = rng.uniform(-170, 170) * s, rng.uniform(-30, 30) * s; r = rng.uniform(60, 120) * s
            dc.ellipse([cx + ox - r, cy + oy - r * 0.55, cx + ox + r, cy + oy + r * 0.55], fill=(255, 226, 206, 150))
            dc.ellipse([cx + ox - r * 0.9, cy + oy - r * 0.55 + 18 * s, cx + ox + r * 0.9, cy + oy + r * 0.4 + 18 * s], fill=(236, 170, 150, 90))
    sky.alpha_composite(cl.filter(ImageFilter.GaussianBlur(14)))
    sun = _layer(); ImageDraw.Draw(sun).ellipse([300 - 90, 1080 - 90, 300 + 90, 1080 + 90], fill=(255, 246, 220, 255))
    sky.alpha_composite(sun.filter(ImageFilter.GaussianBlur(6)))
    g = np.array(sky).astype(np.float32)
    yy, xx = np.mgrid[0:LH, 0:LW]
    gl = np.exp(-(((xx - 300) ** 2 + (yy - 1080) ** 2) / (2 * 380.0 ** 2)))[..., None]
    g[..., :3] = np.clip(g[..., :3] + gl * np.array([90, 60, 20]), 0, 255)
    layers.append((g, 0.05))
    # montañas nevadas (perfil fractal)
    def ridge(n, base, amp, seed):
        r2 = np.random.default_rng(seed)
        pts = np.array([base, base], np.float32); a = amp
        for _ in range(n):
            new = []
            for i in range(len(pts) - 1):
                new += [pts[i], (pts[i] + pts[i + 1]) / 2 + r2.uniform(-a, a)]
            new.append(pts[-1]); pts = np.array(new, np.float32); a *= 0.55
        return pts
    m = _layer(); dm = ImageDraw.Draw(m)
    prof = ridge(7, 0, 380, 4)
    xs = np.linspace(-100, LW + 100, len(prof))
    prof = 1080 - np.abs(prof) * 0.8 - 190 * (1 + np.sin(xs / 300 + 0.5)) * (0.6 + 0.4 * np.sin(xs / 120))
    poly = [(xs[0], LH)] + list(zip(xs, prof)) + [(xs[-1], LH)]
    dm.polygon(poly, fill=(92, 98, 156, 255))
    snow = Image.new("L", (LW, LH), 0); ds = ImageDraw.Draw(snow)
    ds.polygon([(xs[0], LH)] + list(zip(xs, prof)) + [(xs[-1], LH)], fill=255)
    sm = np.array(snow) > 0
    yy, xx = np.mgrid[0:LH, 0:LW]
    topy = np.interp(np.arange(LW), xs, prof)
    depth = yy - topy[None, :]
    noise = cv2.GaussianBlur(rng.standard_normal((LH, LW)).astype(np.float32), (0, 0), 6) * 40
    snowline = (depth < np.clip(780 - topy[None, :], 0, 300) * 0.35 + noise * 0.45) & (topy[None, :] < 780) & sm
    ma = np.array(m).astype(np.float32)
    shade = np.clip((np.gradient(topy)[None, :]) * 2.0, -40, 40)
    nz = cv2.GaussianBlur(rng.standard_normal((LH, LW)).astype(np.float32), (0, 0), 14) * 120
    ma[..., :3] += np.where(sm[..., None], nz[..., None] * np.array([0.8, 0.8, 1.0]), 0)
    ma[..., :3] = np.where(snowline[..., None], np.array([236, 234, 250]) + nz[..., None] * 0.15, ma[..., :3])
    m = Image.fromarray(np.clip(ma, 0, 255).astype(np.uint8), "RGBA")
    m = _haze(m, (236, 190, 186), 0.30).filter(ImageFilter.GaussianBlur(2.5))
    layers.append((np.array(m).astype(np.float32), 0.12))
    # volcán
    v = _layer(); dv = ImageDraw.Draw(v)
    vx = 1120
    dv.polygon([(vx - 520, 1420), (vx - 95, 930), (vx + 95, 930), (vx + 540, 1420)], fill=(120, 92, 110, 255))
    dv.polygon([(vx - 95, 930), (vx - 40, 960), (vx, 935), (vx + 45, 965), (vx + 95, 930)], fill=(255, 120, 50, 255))
    for k in range(5):
        dv.line([(vx - 60 + k * 30, 960), (vx - 160 + k * 70, 1180 + k * 20)], fill=(230, 90, 40, 160), width=10)
    v = _haze(v, (240, 190, 180), 0.35).filter(ImageFilter.GaussianBlur(2))
    layers.append((np.array(v).astype(np.float32), 0.18))
    # colinas medias con pinos
    hl = _layer(); dh = ImageDraw.Draw(hl)
    xs = np.linspace(-50, LW + 50, 40)
    ys = 1330 - 70 * np.sin(xs / 210) - 40 * np.sin(xs / 90 + 1)
    dh.polygon([(xs[0], LH)] + list(zip(xs, ys)) + [(xs[-1], LH)], fill=(104, 140, 84, 255))
    for k in range(26):
        x = rng.uniform(0, LW); yb = np.interp(x, xs, ys) + rng.uniform(0, 60); h = rng.uniform(90, 170)
        for j in range(4):
            w_ = h * (0.42 - j * 0.08); y_ = yb - j * h * 0.22
            dh.polygon([(x - w_, y_), (x, y_ - h * 0.42), (x + w_, y_)], fill=(52, 92, 70, 255))
    hl = _haze(hl, (236, 200, 170), 0.25).filter(ImageFilter.GaussianBlur(1.5))
    layers.append((np.array(hl).astype(np.float32), 0.35))
    if cueva:
        c = _layer(); dc = ImageDraw.Draw(c)
        poly = [(-50, 260)]
        for k in range(12):
            u = k / 11
            poly.append((330 + 260 * u + 40 * math.sin(k * 2.1), 300 + 1200 * u))
        poly += [(640, LH), (-50, LH)]
        dc.polygon(poly, fill=(138, 114, 100, 255))
        c2 = np.array(c).astype(np.float32)
        yy, xx = np.mgrid[0:LH, 0:LW]
        n1 = cv2.GaussianBlur(rng.standard_normal((LH, LW)).astype(np.float32), (0, 0), 18)
        n2 = cv2.GaussianBlur(rng.standard_normal((LH, LW)).astype(np.float32), (0, 0), 4)
        strata = np.sin(yy / 38.0 + n1 * 6) * 10
        m_ = c2[..., 3:4] > 0
        tex = (n1 * 160 + n2 * 40 + strata)[..., None]
        c2[..., :3] = np.where(m_, c2[..., :3] + tex * np.array([1, 0.9, 0.8]), c2[..., :3])
        edge = np.clip(1 - np.abs(xx - np.interp(yy, [p[1] for p in poly[1:13]], [p[0] for p in poly[1:13]])) / 90, 0, 1)
        c2[..., :3] = np.where(m_, c2[..., :3] * (1 - 0.35 * edge[..., None]) + np.array([255, 200, 150]) * 0.25 * edge[..., None], c2[..., :3])
        cave = (((xx - 300) / 210.0) ** 2 + ((yy - 1380) / 330.0) ** 2) < 1
        dark = np.array([34, 22, 24], np.float32)
        glow_ = np.exp(-(((xx - 300) ** 2) / (2 * 150.0 ** 2) + ((yy - 1560) ** 2) / (2 * 170.0 ** 2)))
        c2[..., :3] = np.where(cave[..., None], dark + glow_[..., None] * np.array([210, 110, 40]), c2[..., :3])
        rim = (((xx - 300) / 235.0) ** 2 + ((yy - 1380) / 355.0) ** 2) < 1
        c2[..., :3] = np.where((rim & ~cave)[..., None], c2[..., :3] * 0.62, c2[..., :3])
        layers.append((np.clip(c2, 0, 255), 0.55))
    # suelo
    gnd = np.zeros((LH, LW, 4), np.float32)
    top = 1390
    ys = np.linspace(0, 1, LH - top)[:, None]
    base = np.array([150, 172, 86]) * (1 - ys[..., None] * 0.0) if False else None
    col = np.zeros((LH - top, LW, 3), np.float32)
    t_ = ys ** 0.8
    for c_, (a, b) in enumerate([(176, 118), (182, 150), (104, 66)]):
        col[..., c_] = a + (b - a) * t_
    noise = cv2.GaussianBlur(rng.standard_normal((LH - top, LW)).astype(np.float32), (0, 0), 3) * 18
    col += noise[..., None] * np.array([0.6, 1.0, 0.4])
    path = np.exp(-((np.arange(LW)[None, :] - (LW / 2 + 260 * (1 - ys) - 120)) / (60 + 420 * ys)) ** 2)
    col = col * (1 - path[..., None] * 0.55) + np.array([214, 186, 140]) * path[..., None] * 0.55
    gnd[top:, :, :3] = col; gnd[top:, :, 3] = 255
    gi = Image.fromarray(np.clip(gnd, 0, 255).astype(np.uint8), "RGBA"); dg = ImageDraw.Draw(gi)
    for k in range(260):
        x = rng.uniform(0, LW); y = top + (rng.uniform(0, 1) ** 1.6) * (LH - top); s = 0.4 + (y - top) / (LH - top) * 1.6
        cc = (int(90 + rng.uniform(-20, 20)), int(130 + rng.uniform(-20, 20)), 60, 255)
        for j in range(3):
            dg.line([(x, y), (x + (j - 1) * 8 * s, y - 26 * s)], fill=cc, width=max(1, int(3 * s)))
        if k % 9 == 0: dg.ellipse([x - 5 * s, y - 30 * s, x + 5 * s, y - 20 * s], fill=(255, 230, 120, 255) if k % 2 else (250, 160, 190, 255))
    gi = _haze(gi, (240, 200, 170), 0.0)
    ga = np.array(gi).astype(np.float32)
    ga[top:top + 50, :, :3] = ga[top:top + 50, :, :3] * 0.8 + np.array([240, 210, 180]) * 0.2
    layers.append((ga, 0.75))
    # primer plano (desenfocado): helechos en las esquinas
    fg = _layer(); df = ImageDraw.Draw(fg)
    for (bx, by, sgn) in [(-40, LH + 40, 1), (LW + 40, LH + 40, -1)]:
        for k in range(9):
            ang = -math.pi / 2 + sgn * (0.25 + k * 0.11)
            L_ = 520 + 80 * math.sin(k)
            ex, ey = bx + math.cos(ang) * L_, by + math.sin(ang) * L_
            df.line([(bx, by), (ex, ey)], fill=(40, 80, 40, 255), width=16)
            for j in range(10):
                u = j / 10; px, py = bx + (ex - bx) * u, by + (ey - by) * u
                for s2 in (-1, 1):
                    a2 = ang + s2 * 1.1
                    df.line([(px, py), (px + math.cos(a2) * 90 * (1 - u * 0.7), py + math.sin(a2) * 90 * (1 - u * 0.7))], fill=(52, 104, 50, 255), width=12)
    fg = fg.filter(ImageFilter.GaussianBlur(9))
    layers.append((np.array(fg).astype(np.float32), 1.3))
    return layers

def componer(layers, cam_x=0.0, cam_y=0.0, zoom=1.0, focus_y=GY):
    """Compone las capas con paneo/zoom y parallax. Devuelve uint8 RGB (H, W, 3)."""
    out = np.zeros((H, W, 3), np.float32)
    for arr, par in layers:
        z = 1 + (zoom - 1) * min(1.0, par * 1.2 + 0.1)
        # el centro de la capa (LW/2, ~1000) se mapea al centro de pantalla
        cx_l, cy_l = LW / 2 + cam_x * par, 1000 + cam_y * par
        M = np.array([[z, 0, W / 2 - cx_l * z], [0, z, H * 0.52 - cy_l * z + (focus_y - GY) * 0]], np.float32)
        warped = cv2.warpAffine(arr, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        a = warped[..., 3:4] / 255.0
        out = out * (1 - a) + warped[..., :3] * a
    return out

def cam_pt(x, y, cam_x=0.0, cam_y=0.0, zoom=1.0, par=0.75):
    """Punto de la capa del suelo (coords de pantalla con zoom 1, sin paneo) → pantalla."""
    z = 1 + (zoom - 1) * min(1.0, par * 1.2 + 0.1)
    return W / 2 + (x - W / 2 - cam_x * par) * z, H * 0.52 + (y - H * 0.52 - cam_y * par) * z

# ------------------------------------------------------------ efectos sobre PIL RGBA
def glow(img, x, y, r, col, a=1.0):
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    arr = np.zeros((img.size[1], img.size[0], 4), np.float32)
    x0, x1 = int(max(0, x - r * 2)), int(min(img.size[0], x + r * 2)); y0, y1 = int(max(0, y - r * 2)), int(min(img.size[1], y + r * 2))
    if x1 <= x0 or y1 <= y0: return
    yy, xx = np.mgrid[y0:y1, x0:x1]
    g = np.exp(-((xx - x) ** 2 + (yy - y) ** 2) / (2 * (r / 1.6) ** 2)) * a
    arr[y0:y1, x0:x1, :3] = col; arr[y0:y1, x0:x1, 3] = np.clip(g * 255, 0, 255)
    img.alpha_composite(Image.fromarray(arr.astype(np.uint8), "RGBA"))

def add_light(base, x, y, r, col, a=0.6):
    """Luz aditiva sobre un array float (H, W, 3)."""
    x0, x1 = int(max(0, x - r * 2.2)), int(min(base.shape[1], x + r * 2.2)); y0, y1 = int(max(0, y - r * 2.2)), int(min(base.shape[0], y + r * 2.2))
    if x1 <= x0 or y1 <= y0: return
    yy, xx = np.mgrid[y0:y1, x0:x1]
    g = np.exp(-((xx - x) ** 2 + (yy - y) ** 2) / (2 * (r / 1.5) ** 2)) * a
    base[y0:y1, x0:x1] += g[..., None] * np.array(col, np.float32)

def sombra(img, x, y, w, a=0.35):
    lay = Image.new("RGBA", (int(w * 2.8), int(w * 1.0)), (0, 0, 0, 0))
    ImageDraw.Draw(lay).ellipse([w * 0.2, w * 0.2, lay.width - w * 0.2, lay.height - w * 0.2], fill=(40, 26, 30, int(255 * a)))
    lay = lay.filter(ImageFilter.GaussianBlur(w * 0.08))
    img.alpha_composite(lay, (int(x - lay.width * 0.42), int(y - lay.height / 2)))

def fuego(img, x, y, s, t, seed=0):
    """Fogata: llamas en capas + brasas."""
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    rng = np.random.default_rng(seed)
    for k in range(5):  # leños
        a = k * 0.6 - 1.2
        d.line([(x - math.cos(a) * 90 * s, y + 10 * s), (x + math.cos(a) * 90 * s, y - 6 * s)], fill=(92, 56, 40, 255), width=int(26 * s))
    for layer, (col, sc_) in enumerate([((255, 90, 30), 1.0), ((255, 160, 40), 0.72), ((255, 236, 140), 0.42)]):
        for k in range(5):
            ph = t * (7 + k) + k * 1.3 + seed
            hh = (150 + 50 * math.sin(ph) + 30 * math.sin(ph * 2.3)) * s * sc_
            ww = (46 + 10 * math.sin(ph * 1.7)) * s * sc_
            cx = x + (k - 2) * 26 * s * sc_ + 8 * math.sin(ph * 1.3) * s
            d.polygon([(cx - ww, y), (cx - ww * 0.5, y - hh * 0.55), (cx + 12 * s * math.sin(ph), y - hh), (cx + ww * 0.5, y - hh * 0.55), (cx + ww, y)], fill=col + (235,))
            d.ellipse([cx - ww, y - ww * 0.9, cx + ww, y + ww * 0.6], fill=col + (235,))
    lay = lay.filter(ImageFilter.GaussianBlur(2.5 * s))
    img.alpha_composite(lay)
    glow(img, x, y - 80 * s, 260 * s, (255, 150, 60), 0.45)
    d = ImageDraw.Draw(img)
    for k in range(14):
        ph = (t * 0.7 + k / 14) % 1
        ex = x + math.sin(k * 7.1 + t * 2) * 80 * s * ph; ey = y - 40 * s - ph * 420 * s
        r = 5 * s * (1 - ph)
        d.ellipse([ex - r, ey - r, ex + r, ey + r], fill=(255, 200, 90, int(255 * (1 - ph))))

def humo(img, x, y, s, t, n=8, col=(240, 236, 230), alpha=150, spread=1.0, speed=1.0):
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for k in range(n):
        ph = (t * 0.35 * speed + k / n) % 1
        px = x + math.sin(k * 3.3 + t) * 30 * s * spread + ph * 60 * s * spread * math.sin(k)
        py = y - ph * 380 * s
        r = (20 + 60 * ph) * s
        d.ellipse([px - r, py - r, px + r, py + r], fill=col + (int(alpha * (1 - ph) * min(1, ph * 5)),))
    img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(6 * s)))

def olor(img, x0, y0, x1, y1, t, n=3, col=(255, 244, 200)):
    """Estelas de olor ondulantes de (x0, y0) a (x1, y1)."""
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for k in range(n):
        pts = []
        for j in range(40):
            u = j / 39
            px = x0 + (x1 - x0) * u; py = y0 + (y1 - y0) * u - math.sin(u * math.pi) * 120
            off = math.sin(u * 12 - t * 5 + k * 2) * 26 * (0.3 + u)
            pts.append((px + off * 0.3, py + off + (k - 1) * 40))
        d.line(pts, fill=col + (200,), width=26, joint="curve")
    img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(9)))
    lay2 = Image.new("RGBA", img.size, (0, 0, 0, 0)); d2 = ImageDraw.Draw(lay2)
    for k in range(n):
        pts = []
        for j in range(40):
            u = j / 39
            px = x0 + (x1 - x0) * u; py = y0 + (y1 - y0) * u - math.sin(u * math.pi) * 120
            off = math.sin(u * 12 - t * 5 + k * 2) * 26 * (0.3 + u)
            pts.append((px + off * 0.3, py + off + (k - 1) * 40))
        d2.line(pts, fill=(255, 250, 220, 150), width=7, joint="curve")
    img.alpha_composite(lay2.filter(ImageFilter.GaussianBlur(2)))

def estrella(d, x, y, r, a=0.0, col=(255, 255, 255, 255)):
    pts = []
    for k in range(8):
        rr = r if k % 2 == 0 else r * 0.22; an = a + k * math.pi / 4
        pts.append((x + math.cos(an) * rr, y + math.sin(an) * rr))
    d.polygon(pts, fill=col)

def chispas(img, pts, t, r=34):
    d = ImageDraw.Draw(img)
    for k, (x, y) in enumerate(pts):
        ph = (t * 1.8 + k * 0.37) % 1
        s = math.sin(ph * math.pi)
        if s > 0.05: estrella(d, x, y, r * s, ph * 2, (255, 255, 230, int(255 * s)))

def portal(img, x, y, r, t, open_=1.0):
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    R = r * open_
    if R < 4: return
    d.ellipse([x - R, y - R * 1.15, x + R, y + R * 1.15], fill=(40, 16, 70, 230))
    for k in range(9):
        rr = R * (1 - k * 0.1)
        col = (90, 230, 255) if k % 2 == 0 else (190, 110, 255)
        a0 = (t * (140 + k * 30) * (1 if k % 2 else -1)) % 360
        d.arc([x - rr, y - rr * 1.15, x + rr, y + rr * 1.15], a0, a0 + 250, fill=col + (255,), width=max(3, int(R * 0.05)))
    img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(1.2)))
    glow(img, x, y, R * 1.3, (140, 120, 255), 0.55)

def lineas_velocidad(img, t, n=26, col=(255, 255, 255), dirx=-1):
    d = ImageDraw.Draw(img)
    rng = np.random.default_rng(int(t * 30) % 1000)
    for k in range(n):
        y = rng.uniform(150, H - 200); x = rng.uniform(-200, W); L = rng.uniform(150, 420)
        d.line([(x, y), (x + L * -dirx, y)], fill=col + (int(rng.uniform(90, 200)),), width=int(rng.uniform(3, 9)))

def polvo(img, x, y, t, s=1.0, n=7):
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    ph = min(1.0, t / 0.8)
    for k in range(n):
        a = math.pi + k * math.pi / (n - 1)
        px = x + math.cos(a) * 170 * s * ph * (1 + 0.3 * math.sin(k)); py = y + math.sin(a) * 40 * s * ph - 30 * s * ph
        r = (30 + 60 * ph) * s
        d.ellipse([px - r, py - r, px + r, py + r], fill=(226, 206, 170, int(200 * (1 - ph))))
    img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(4)))

def corazon(d, x, y, r, col=(255, 80, 120, 255)):
    d.ellipse([x - r, y - r * 0.6, x, y + r * 0.3], fill=col); d.ellipse([x, y - r * 0.6, x + r, y + r * 0.3], fill=col)
    d.polygon([(x - r * 0.98, y - 0.05 * r), (x + r * 0.98, y - 0.05 * r), (x, y + r * 1.05)], fill=col)

def comic(img, txt, x, y, size, t, col=(255, 222, 40), ang=-6, pop=0.25):
    k = min(1.0, t / pop); k = 1 + 0.3 * math.sin(k * math.pi) if k < 1 else 1.0
    k *= min(1.0, t / 0.08 + 0.2)
    f = font(size * k); tw = f.getlength(txt)
    lay = Image.new("RGBA", (int(tw + 120), int(size * k * 1.6)), (0, 0, 0, 0))
    ImageDraw.Draw(lay).text((60, 14), txt, font=f, fill=col + (255,), stroke_width=int(14 * k), stroke_fill=(20, 14, 20))
    lay = lay.rotate(ang, resample=Image.BICUBIC, expand=True)
    img.alpha_composite(lay, (int(x - lay.width / 2), int(y - lay.height / 2)))
