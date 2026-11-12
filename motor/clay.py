"""clay.py — mini renderer 3D por "impostores" (esferas, elipsoides, cápsulas, cajas) en numpy.
Look de figura 3D estilizada: luz principal cálida + relleno frío + luz de borde + brillo especular,
oclusión ambiental por profundidad y contorno por discontinuidad de profundidad/objeto.
Coordenadas del mundo: x derecha, y arriba, z hacia la cámara. Proyección ortográfica."""
import math
import numpy as np
import cv2

def _n(v):
    v = np.asarray(v, np.float32); return v / (np.linalg.norm(v) + 1e-9)

class Mat:
    def __init__(self, spec=0.25, shin=30.0, emit=0.0, rim=1.0, flat=0.0, outline=True, toon=0.55):
        self.spec, self.shin, self.emit, self.rim, self.flat, self.outline, self.toon = spec, shin, emit, rim, flat, outline, toon

SKIN = Mat(spec=0.12, shin=18); CLOTH = Mat(spec=0.05, shin=8); GLOSS = Mat(spec=0.9, shin=90)
FLAT = Mat(spec=0.0, flat=0.85, rim=0.2, outline=False); EMIT = Mat(emit=1.0, outline=False, spec=0)
EYE = Mat(spec=0.6, shin=60, flat=0.35, rim=0.1); HAIR = Mat(spec=0.18, shin=14, toon=0.75)
STONE = Mat(spec=0.06, shin=6, toon=0.7); FUR = Mat(spec=0.04, shin=6, toon=0.75)

class Scene:
    def __init__(self):
        self.p = []
    def sphere(self, c, r, col, mat=SKIN, oid=None):
        self.p.append(("s", np.asarray(c, np.float32), float(r), col, mat, oid))
    def head(self, c, r, col, mat, yaw, feats, oid=None):
        """Esfera con rasgos pintados sobre su superficie. feats: lista de
        (ax, ay, rx, ry, rot, color, mat, borde) en radianes (longitud/latitud de la cabeza)."""
        self.p.append(("h", np.asarray(c, np.float32), (float(r), float(yaw), feats), col, mat, oid))
    def ell(self, c, rx, ry, rz, col, mat=SKIN, rot=0.0, oid=None):
        self.p.append(("e", np.asarray(c, np.float32), (float(rx), float(ry), float(rz), float(rot)), col, mat, oid))
    def caps(self, a, b, ra, rb, col, mat=SKIN, oid=None):
        self.p.append(("c", (np.asarray(a, np.float32), np.asarray(b, np.float32)), (float(ra), float(rb)), col, mat, oid))
    def box(self, c, hx, hy, hz, col, mat=STONE, bevel=0.25, oid=None):
        self.p.append(("b", np.asarray(c, np.float32), (float(hx), float(hy), float(hz), float(bevel)), col, mat, oid))
    def chain(self, pts, radii, col, mat=SKIN, oid=None):
        for k in range(len(pts) - 1):
            self.caps(pts[k], pts[k + 1], radii[k], radii[k + 1], col, mat, oid)
    def extend(self, other): self.p += other.p

LIGHT = dict(key=_n((-0.55, 0.62, 0.56)), key_col=np.array([1.0, 0.92, 0.80], np.float32),
             fill=_n((0.75, 0.05, 0.45)), fill_col=np.array([0.50, 0.62, 0.88], np.float32),
             sky=np.array([0.55, 0.62, 0.80], np.float32), ground=np.array([0.42, 0.34, 0.22], np.float32),
             rim_col=np.array([1.0, 0.86, 0.66], np.float32), rim_dir=_n((0.7, 0.45, 0.0)),
             outline=np.array([0.10, 0.07, 0.08], np.float32), ao=0.55)

def render(scene, S, ox, oy, W, H, light=None, ss=1.5, outline_px=5.0):
    """Devuelve (RGBA uint8 de W×H, x0, y0) recortado a la caja que ocupa la escena.
    S = píxeles por unidad; (ox, oy) = posición en pantalla del origen del mundo."""
    L = dict(LIGHT); L.update(light or {})
    prims = scene.p
    if not prims: return None
    # caja envolvente en pantalla
    xs, ys = [], []
    for kind, c, r, col, mat, oid in prims:
        if kind == "s": pts = [(c, r)]
        elif kind == "h": pts = [(c, r[0])]
        elif kind == "e": pts = [(c, max(r[0], r[1]))]
        elif kind == "c": pts = [(c[0], r[0]), (c[1], r[1])]
        else: pts = [(c, max(r[0], r[1]) * 1.42)]
        for cc, rr in pts:
            xs += [ox + (cc[0] - rr) * S, ox + (cc[0] + rr) * S]; ys += [oy - (cc[1] + rr) * S, oy - (cc[1] - rr) * S]
    pad = int(outline_px * 2 + 4)
    x0 = max(0, int(min(xs)) - pad); x1 = min(W, int(max(xs)) + pad)
    y0 = max(0, int(min(ys)) - pad); y1 = min(H, int(max(ys)) + pad)
    if x1 <= x0 or y1 <= y0: return None
    bw, bh = int((x1 - x0) * ss), int((y1 - y0) * ss)
    Sx = S * ss; OX = (ox - x0) * ss; OY = (oy - y0) * ss
    Z = np.full((bh, bw), -1e9, np.float32)
    N = np.zeros((bh, bw, 3), np.float32); A = np.zeros((bh, bw, 3), np.float32)
    MI = np.full((bh, bw), -1, np.int32); ID = np.full((bh, bw), -1, np.int32)
    mats = []; matidx = {}
    for i, (kind, c, r, col, mat, oid) in enumerate(prims):
        if id(mat) not in matidx: matidx[id(mat)] = len(mats); mats.append(mat)
        mi = matidx[id(mat)]
        oidv = i if oid is None else oid
        colv = np.array(col[:3], np.float32) / (255.0 if max(col[:3]) > 1.0 else 1.0)
        if kind == "c":
            a, b = c; ra, rb = r
            ax, ay = OX + a[0] * Sx, OY - a[1] * Sx; bx, by = OX + b[0] * Sx, OY - b[1] * Sx
            R = max(ra, rb) * Sx
            px0 = int(max(0, min(ax, bx) - R - 1)); px1 = int(min(bw, max(ax, bx) + R + 2))
            py0 = int(max(0, min(ay, by) - R - 1)); py1 = int(min(bh, max(ay, by) + R + 2))
            if px1 <= px0 or py1 <= py0: continue
            gx, gy = np.meshgrid(np.arange(px0, px1, dtype=np.float32) + 0.5, np.arange(py0, py1, dtype=np.float32) + 0.5)
            dx, dy = bx - ax, by - ay; dd = dx * dx + dy * dy + 1e-6
            t = np.clip(((gx - ax) * dx + (gy - ay) * dy) / dd, 0, 1)
            cx, cy = ax + t * dx, ay + t * dy
            rr = (ra + (rb - ra) * t) * Sx
            u, v = (gx - cx) / rr, (gy - cy) / rr
            d2 = u * u + v * v; m = d2 < 1
            h = np.sqrt(np.clip(1 - d2, 0, 1))
            z = (a[2] + (b[2] - a[2]) * t) + h * rr / Sx
            nx, ny, nz = u, -v, h
        elif kind == "b":
            hx, hy, hz, bev = r
            cx_, cy_ = OX + c[0] * Sx, OY - c[1] * Sx
            px0 = int(max(0, cx_ - hx * Sx)); px1 = int(min(bw, cx_ + hx * Sx + 1))
            py0 = int(max(0, cy_ - hy * Sx)); py1 = int(min(bh, cy_ + hy * Sx + 1))
            if px1 <= px0 or py1 <= py0: continue
            gx, gy = np.meshgrid(np.arange(px0, px1, dtype=np.float32) + 0.5, np.arange(py0, py1, dtype=np.float32) + 0.5)
            u = (gx - cx_) / (hx * Sx); v = (gy - cy_) / (hy * Sx)
            bb = bev * min(hx, hy) / np.array([hx, hy])
            ex = np.clip((np.abs(u) - (1 - bb[0])) / bb[0], 0, 1); ey = np.clip((np.abs(v) - (1 - bb[1])) / bb[1], 0, 1)
            m = (ex ** 2 + ey ** 2) < 1
            nx = np.sign(u) * ex; ny = -np.sign(v) * ey
            nz = np.sqrt(np.clip(1 - nx * nx - ny * ny, 0, 1))
            z = c[2] + hz * nz
        else:
            if kind == "s": rx = ry = rz = r; rot = 0.0
            elif kind == "h": rx = ry = rz = r[0]; rot = 0.0
            else: rx, ry, rz, rot = r
            cx_, cy_ = OX + c[0] * Sx, OY - c[1] * Sx
            R = max(rx, ry) * Sx
            px0 = int(max(0, cx_ - R - 1)); px1 = int(min(bw, cx_ + R + 2))
            py0 = int(max(0, cy_ - R - 1)); py1 = int(min(bh, cy_ + R + 2))
            if px1 <= px0 or py1 <= py0: continue
            gx, gy = np.meshgrid(np.arange(px0, px1, dtype=np.float32) + 0.5, np.arange(py0, py1, dtype=np.float32) + 0.5)
            qx, qy = gx - cx_, gy - cy_
            if rot:
                cr, sr = math.cos(rot), math.sin(rot)
                qx, qy = qx * cr + qy * sr, -qx * sr + qy * cr
            u, v = qx / (rx * Sx), qy / (ry * Sx)
            d2 = u * u + v * v; m = d2 < 1
            h = np.sqrt(np.clip(1 - d2, 0, 1))
            z = c[2] + h * rz
            lnx, lny, lnz = u / rx, v / ry, h / max(rz, 1e-4)
            if rot:
                lnx, lny = lnx * cr - lny * sr, lnx * sr + lny * cr
            nx, ny, nz = lnx, -lny, lnz
        sub = Z[py0:py1, px0:px1]
        w = m & (z > sub)
        if not w.any(): continue
        sub[w] = z[w]
        nn = np.stack([nx, ny, nz], -1); nn /= (np.linalg.norm(nn, axis=-1, keepdims=True) + 1e-6)
        N[py0:py1, px0:px1][w] = nn[w]
        A[py0:py1, px0:px1][w] = colv
        MI[py0:py1, px0:px1][w] = mi; ID[py0:py1, px0:px1][w] = oidv
        if kind == "h" and r[2]:
            yaw = r[1]; cy_, sy_ = math.cos(yaw), math.sin(yaw)
            lx = nn[..., 0] * cy_ - nn[..., 2] * sy_; lz = nn[..., 0] * sy_ + nn[..., 2] * cy_
            axm = np.arctan2(lx, lz); aym = np.arcsin(np.clip(nn[..., 1], -1, 1))
            subA = A[py0:py1, px0:px1]; subM = MI[py0:py1, px0:px1]
            for (fx, fy, frx, fry, frot, fcol, fmat, fb) in r[2]:
                du, dv = axm - fx, aym - fy
                if frot:
                    cr, sr = math.cos(frot), math.sin(frot)
                    du, dv = du * cr + dv * sr, -du * sr + dv * cr
                d2 = (du / frx) ** 2 + (dv / fry) ** 2
                if id(fmat) not in matidx: matidx[id(fmat)] = len(mats); mats.append(fmat)
                fc = np.array(fcol[:3], np.float32) / 255.0
                if fb > 0:
                    rb = w & (d2 < (1 + fb) ** 2) & (d2 >= 1)
                    subA[rb] = L["outline"]; subM[rb] = matidx[id(fmat)]
                inn = w & (d2 < 1)
                subA[inn] = fc; subM[inn] = matidx[id(fmat)]
    mask = MI >= 0
    if not mask.any(): return None
    # parámetros de material por píxel
    def mp(attr): arr = np.array([getattr(m_, attr) for m_ in mats] + [0], np.float32); return arr[MI]
    spec, shin, emit, rimk, flat, toon = mp("spec"), mp("shin"), mp("emit"), mp("rim"), mp("flat"), mp("toon")
    nx, ny, nz = N[..., 0], N[..., 1], N[..., 2]
    ndl = nx * L["key"][0] + ny * L["key"][1] + nz * L["key"][2]
    dif = np.clip(ndl, 0, 1)
    st = np.clip((ndl + 0.05) / 0.25, 0, 1); st = st * st * (3 - 2 * st)
    dif = toon * st + (1 - toon) * dif
    fil = np.clip(nx * L["fill"][0] + ny * L["fill"][1] + nz * L["fill"][2], 0, 1)
    hv = _n(L["key"] + np.array([0, 0, 1], np.float32))
    sp = np.clip(nx * hv[0] + ny * hv[1] + nz * hv[2], 0, 1) ** shin * spec
    rim = (1 - np.clip(nz, 0, 1)) ** 2.6 * np.clip(nx * L["rim_dir"][0] + ny * L["rim_dir"][1] + 0.35, 0, 1) * rimk
    amb = L["sky"][None, None] * (0.5 + 0.5 * ny)[..., None] * 0.42 + L["ground"][None, None] * (0.5 - 0.5 * ny)[..., None] * 0.25
    # oclusión ambiental por profundidad
    zf = np.where(mask, Z, 0).astype(np.float32); mf = mask.astype(np.float32)
    k = max(3, int(0.06 * Sx) | 1)
    zb = cv2.GaussianBlur(zf, (0, 0), k) / (cv2.GaussianBlur(mf, (0, 0), k) + 1e-5)
    ao = np.clip((zb - Z) / 0.12, 0, 1) * L["ao"]
    ao = np.where(mask, ao, 0)
    lit = A * (amb + L["key_col"][None, None] * (dif * 1.12)[..., None] + L["fill_col"][None, None] * (fil * 0.32)[..., None])
    lit = lit * (1 - 0.6 * ao[..., None]) + (sp[..., None] * L["key_col"][None, None]) + rim[..., None] * L["rim_col"][None, None] * 0.55
    flatc = A * (0.92 + 0.12 * dif[..., None])
    lit = lit * (1 - flat[..., None]) + flatc * flat[..., None]
    col = lit * (1 - emit[..., None]) + A * emit[..., None]
    # contorno
    outl = np.array([m_.outline for m_ in mats] + [False])[MI] & mask
    edge = np.zeros_like(mask)
    for sy_, sx_ in ((0, 1), (1, 0), (1, 1), (1, -1)):
        Zs = np.roll(np.roll(Z, sy_, 0), sx_, 1); IDs = np.roll(np.roll(ID, sy_, 0), sx_, 1)
        Ms = np.roll(np.roll(mask, sy_, 0), sx_, 1)
        e = (mask != Ms) | ((ID != IDs) & (np.abs(Z - Zs) > 0.10))
        edge |= e
    edge &= (outl | ~mask) & (np.roll(outl, 1, 0) | np.roll(outl, 1, 1) | outl)
    edge[0, :] = False; edge[:, 0] = False; edge[:, -1] = False; edge[-1, :] = False
    kk = max(1, int(outline_px * ss / 2))
    edge = cv2.dilate(edge.astype(np.uint8), np.ones((kk, kk), np.uint8)).astype(bool)
    alpha = mask.astype(np.float32)
    alpha = np.maximum(alpha, edge.astype(np.float32))
    col = np.where(edge[..., None], L["outline"][None, None], col)
    rgba = np.concatenate([np.clip(col, 0, 1), alpha[..., None]], -1)
    rgba[..., :3] *= rgba[..., 3:4]
    out = cv2.resize(rgba, (x1 - x0, y1 - y0), interpolation=cv2.INTER_AREA)
    a = out[..., 3:4]
    out[..., :3] = np.where(a > 1e-4, out[..., :3] / np.maximum(a, 1e-4), 0)
    return (np.clip(out * 255, 0, 255).astype(np.uint8), x0, y0)

def composite(img_rgba, res):
    """Pega el resultado de render() sobre una imagen PIL RGBA."""
    from PIL import Image
    if res is None: return
    arr, x0, y0 = res
    img_rgba.alpha_composite(Image.fromarray(arr, "RGBA"), (x0, y0))

# ------------------------------------------------------------ utilidades de pose
def rot_y(p, yaw, piv):
    c, s = math.cos(yaw), math.sin(yaw)
    x, y, z = p[0] - piv[0], p[1], p[2] - piv[2]
    return np.array([piv[0] + x * c + z * s, y, piv[2] - x * s + z * c], np.float32)

class Rig:
    """Ayudante: construye un personaje en coordenadas locales y lo transforma (posición, escala, giro, squash)."""
    def __init__(self, sc, x, y, z, s=1.0, yaw=0.0, squash=1.0):
        self.sc, self.o, self.s, self.yaw, self.sq = sc, np.array([x, y, z], np.float32), s, yaw, squash
        self.c, self.sn = math.cos(yaw), math.sin(yaw)
    def P(self, p):
        x, y, z = p
        x2, z2 = x * self.c + z * self.sn, -x * self.sn + z * self.c
        k = 1 / math.sqrt(self.sq)
        return self.o + np.array([x2 * self.s * k, y * self.s * self.sq, z2 * self.s * k], np.float32)
    def sphere(self, p, r, col, mat=SKIN, oid=None): self.sc.sphere(self.P(p), r * self.s, col, mat, oid)
    def ell(self, p, rx, ry, rz, col, mat=SKIN, rot=0.0, oid=None):
        ex = math.sqrt((rx * self.c) ** 2 + (rz * self.sn) ** 2); ez = math.sqrt((rz * self.c) ** 2 + (rx * self.sn) ** 2)
        k = 1 / math.sqrt(self.sq)
        self.sc.ell(self.P(p), ex * self.s * k, ry * self.s * self.sq, ez * self.s * k, col, mat, rot, oid)
    def caps(self, a, b, ra, rb, col, mat=SKIN, oid=None): self.sc.caps(self.P(a), self.P(b), ra * self.s, rb * self.s, col, mat, oid)
    def chain(self, pts, radii, col, mat=SKIN, oid=None):
        for k in range(len(pts) - 1): self.caps(pts[k], pts[k + 1], radii[k], radii[k + 1], col, mat, oid)
