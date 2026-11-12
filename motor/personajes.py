"""Personajes 3D (clay) de Mundo Hipotético: Nico, cavernícolas, mamut y utilería."""
import math
import numpy as np
from clay import Scene, Rig, SKIN, CLOTH, GLOSS, FLAT, EMIT, EYE, HAIR, STONE, FUR, Mat

# paleta Nico (igual que la foto de perfil)
N_SKIN = (246, 196, 152); N_HAIR = (66, 40, 28); N_HOOD = (38, 178, 198); N_HOOD_D = (28, 140, 160)
N_PANTS = (44, 56, 92); N_SHOE = (36, 36, 44); WHITE = (250, 250, 250); DARK = (28, 20, 26)
CHEEK = (240, 140, 140); MOUTH = (120, 30, 40); TONGUE = (236, 110, 120)

ARMS = {  # (ángulo hombro, flexión codo, adelante) en grados; 0 = colgando
    "down": (12, 8, 0.0), "up": (165, 10, 0.0), "wave": (150, 40, 0.0), "hold": (28, -95, 0.35),
    "hold_up": (110, -60, 0.3), "point": (80, 0, 0.25), "hip": (35, -110, 0.0), "shrug": (55, 95, 0.0),
    "grind": (40, -80, 0.35), "offer": (95, -20, 0.45), "think": (30, -140, 0.3),
}

def _arm_pts(side, spec, t=0.0, L1=0.36, L2=0.33, sh=(0.36, 1.2, 0.02)):
    if isinstance(spec, str): spec = ARMS[spec]
    a1, a2, fwd = spec
    a1 = math.radians(a1); a2 = math.radians(a2)
    S = np.array([sh[0] * side, sh[1], sh[2]], np.float32)
    d1 = np.array([math.sin(a1) * side, -math.cos(a1), 0], np.float32)
    E = S + d1 * L1 + np.array([0, 0, fwd * 0.6], np.float32)
    d2 = np.array([math.sin(a1 + a2) * side, -math.cos(a1 + a2), 0], np.float32)
    Hh = E + d2 * L2 + np.array([0, 0, fwd * 0.5], np.float32)
    return S, E, Hh

def _face(rig, hc, R, hy, t, expr, mouth, look, blink, cheeks=True, eye_s=1.0, brow_col=DARK, eye_y=0.04,
          small_eyes=False, skin=N_SKIN, unibrow=False, oid=None, mat=SKIN):
    """Cabeza con rasgos pintados sobre la esfera (siguen la curvatura al girar)."""
    F = []
    def put(ax, ay, rx, ry, col, m, rot=0.0, border=0.0): F.append((ax, ay, rx, ry, rot, col, m, border))
    if blink is None: blink = 1.0 if (t % 3.3) < 0.11 else 0.0
    wide = {"shock": 1.22, "nervous": 1.08, "angry": 0.9, "sad": 0.95}.get(expr, 1.0)
    for side in (-1, 1):
        ax = side * 0.34
        if small_eyes:
            if blink > 0.5: put(ax, eye_y, 0.09, 0.016, DARK, FLAT)
            else:
                put(ax, eye_y, 0.075, 0.095, DARK, EYE)
                put(ax - 0.025, eye_y + 0.04, 0.022, 0.024, WHITE, EMIT)
        else:
            if blink > 0.5:
                put(ax, eye_y - 0.02, 0.15 * eye_s, 0.02, DARK, FLAT)
            else:
                put(ax, eye_y, 0.17 * eye_s * wide, 0.21 * eye_s * wide, WHITE, EYE, border=0.1)
                lx, ly = look
                pr = 0.1 * eye_s * (0.72 if expr == "shock" else 1.0)
                put(ax + lx * 0.07, eye_y + ly * 0.07, pr, pr * 1.15, DARK, EYE)
                put(ax + lx * 0.07 - 0.04, eye_y + ly * 0.07 + 0.055, 0.036, 0.036, WHITE, EMIT)
        if not unibrow:
            by = eye_y + 0.29 * eye_s * wide + (0.04 if expr in ("shock", "nervous") else 0)
            tilt = {"angry": -0.5, "nervous": 0.35, "sad": 0.4, "shock": 0.1, "proud": -0.15}.get(expr, 0.08) * side
            put(ax, by, 0.13, 0.032, brow_col, FLAT, rot=tilt)
        if cheeks and expr not in ("shock", "angry"):
            put(side * 0.55, -0.17, 0.12, 0.07, CHEEK, FLAT)
    if unibrow:
        put(0, eye_y + 0.24, 0.42, 0.065, brow_col, HAIR, rot=0.0)
    my = -0.31
    o = float(np.clip(mouth, 0, 1))
    if o > 0.06 or expr == "shock":
        o = max(o, 0.5 if expr == "shock" else 0.0)
        w = 0.19 if expr != "shock" else 0.13
        put(0, my - 0.02 * o, w, 0.04 + 0.12 * o, MOUTH, FLAT, border=0.08)
        put(0, my - 0.07 * o, w * 0.62, 0.02 + 0.05 * o, TONGUE, FLAT)
        if o > 0.3: put(0, my + 0.07 * o, w * 0.78, 0.028, WHITE, FLAT)
    elif expr in ("happy", "proud", "laugh"):
        put(0, my - 0.02, 0.2, 0.095, MOUTH, FLAT, border=0.08)
        put(0, my + 0.035, 0.17, 0.032, WHITE, FLAT)
        put(0, my - 0.065, 0.1, 0.035, TONGUE, FLAT)
    elif expr in ("sad", "nervous"):
        for k, x in enumerate((-0.15, -0.05, 0.05, 0.15)):
            put(x, my + (0.022 if k % 2 else -0.015), 0.062, 0.022, DARK, FLAT, rot=0.55 if k % 2 else -0.55)
    else:
        put(0, my, 0.11, 0.02, DARK, FLAT)
    rig.sc.head(rig.P(hc), R * rig.s, skin, mat, rig.yaw + hy, F, oid)

def nico(sc, x, y, z, t, s=1.0, yaw=0.0, head_yaw=0.0, arms=("down", "down"), mouth=0.0, expr="happy",
         look=(0, 0), blink=None, squash=1.0, walk=0.0, bob=True, sweat=False):
    """(x, y, z) = pies. Altura total ≈ 2.55 * s. Devuelve puntos útiles en el mundo."""
    if abs(math.sin(yaw)) < 0.9:   # la cara nunca gira más de ~30° respecto a la cámara (se ve rara de perfil)
        head_yaw = float(np.clip(yaw + head_yaw, -0.5, 0.5)) - yaw
    rig = Rig(sc, x, y, z, s, yaw, squash)
    br = 0.025 * math.sin(t * 2.6) if bob else 0.0
    # piernas y zapatos
    for side in (-1, 1):
        ph = math.sin(walk + (0 if side > 0 else math.pi)) if walk else 0.0
        hip = (0.17 * side, 0.62, 0.0); foot = (0.19 * side + ph * 0.0, 0.14 + max(0, ph) * 0.12, ph * 0.22)
        rig.caps(hip, foot, 0.12, 0.11, N_PANTS, CLOTH)
        rig.ell((foot[0], 0.1 + max(0, ph) * 0.12, foot[2] + 0.07), 0.15, 0.1, 0.2, N_SHOE, GLOSS)
    # torso (sudadera)
    rig.ell((0, 0.95 + br, 0), 0.43, 0.46, 0.36, N_HOOD, CLOTH)
    rig.ell((0, 0.78 + br, 0.27), 0.25, 0.12, 0.07, N_HOOD_D, CLOTH)
    for side in (-1, 1):
        rig.caps((0.08 * side, 1.18 + br, 0.30), (0.08 * side, 0.98 + br, 0.33), 0.025, 0.025, WHITE, CLOTH)
    rig.ell((0, 1.3 + br, -0.06), 0.4, 0.15, 0.3, N_HOOD_D, CLOTH)
    # brazos
    hands = {}
    for side, spec in zip((-1, 1), arms):
        Sh, E, Hh = _arm_pts(side, spec, t, sh=(0.36, 1.2 + br, 0.02))
        rig.caps(Sh, E, 0.105, 0.1, N_HOOD, CLOTH); rig.caps(E, Hh, 0.1, 0.095, N_HOOD, CLOTH)
        rig.sphere(Hh, 0.125, N_SKIN, SKIN)
        hands["L" if side < 0 else "R"] = rig.P(Hh)
    # cabeza
    hc = np.array([0, 1.88 + br * 1.4, 0.02], np.float32); R = 0.64
    for side in (-1, 1):
        a = side * 1.45 + head_yaw
        if math.cos(a + yaw) > -0.3:
            rig.sphere(hc + np.array([math.sin(a) * R * 0.98, -0.02, math.cos(a) * R * 0.98]), 0.15, N_SKIN, SKIN)
    # pelo: grumos arriba + atrás + flequillo
    for k in range(7):
        a = -1.25 + k * (2.5 / 6) + head_yaw
        for ring, (ry_, rr_, zz) in enumerate([(0.52, 0.27, 0.15), (0.42, 0.3, -0.25)]):
            p = hc + np.array([math.sin(a) * R * 0.78, R * ry_ + 0.08, math.cos(a) * R * 0.78 * (0.35 if ring == 0 else -0.6)], np.float32)
            rig.sphere(p, rr_, N_HAIR, HAIR, oid=9100)
    for k in range(5):
        a = -0.62 + k * 0.31 + head_yaw
        p = hc + np.array([math.sin(a) * R * 0.84, R * 0.42, math.cos(a) * R * 0.62], np.float32)
        rig.sphere(p, 0.2, N_HAIR, HAIR, oid=9100)
    _face(rig, hc, R, head_yaw, t, expr, mouth, look, blink, oid=9001)
    if sweat:
        p = hc + np.array([math.sin(0.9 + head_yaw) * R, 0.25 - (t * 0.6 % 0.4), math.cos(0.9 + head_yaw) * R + 0.05])
        rig.ell(p, 0.06, 0.09, 0.05, (140, 210, 255), GLOSS)
    return dict(hands=hands, head=rig.P(hc), mouth=rig.P(hc + np.array([0, -0.2, R])), top=rig.P(hc + np.array([0, R + 0.25, 0])))

CAVE_VAR = [  # piel, pelo, piel de animal
    ((206, 150, 108), (52, 34, 24), (196, 120, 56)),
    ((176, 120, 84), (36, 26, 22), (150, 104, 66)),
    ((222, 170, 128), (120, 60, 30), (210, 160, 90)),
    ((150, 100, 72), (30, 24, 22), (180, 90, 50)),
    ((214, 160, 118), (90, 70, 50), (120, 100, 80)),
]

def cavernicola(sc, x, y, z, t, s=1.0, yaw=0.0, var=0, head_yaw=0.0, arms=("down", "down"), mouth=0.0, expr="neutral",
                look=(0, 0), squash=1.0, club=False, bob=True, blink=None):
    skin, hair, fur = CAVE_VAR[var % len(CAVE_VAR)]
    head_yaw = float(np.clip(yaw + head_yaw, -0.55, 0.55)) - yaw
    rig = Rig(sc, x, y, z, s, yaw, squash)
    br = 0.03 * math.sin(t * 2.2 + var) if bob else 0.0
    for side in (-1, 1):
        rig.caps((0.2 * side, 0.6, 0), (0.22 * side, 0.14, 0.02), 0.15, 0.13, skin, SKIN)
        rig.ell((0.24 * side, 0.1, 0.12), 0.2, 0.11, 0.25, skin, SKIN)
    rig.ell((0, 1.0 + br, 0), 0.55, 0.55, 0.42, fur, FUR)               # túnica de piel
    for k, (a, b) in enumerate([(-0.25, 0.85), (0.22, 1.1), (0.05, 0.7), (-0.18, 1.25), (0.3, 0.8)]):
        rig.ell((a, b + br, 0.36), 0.08, 0.06, 0.05, tuple(int(c * 0.6) for c in fur), FUR)
    rig.caps((-0.35, 1.38 + br, 0.25), (0.3, 0.62 + br, 0.38), 0.05, 0.05, tuple(int(c * 0.7) for c in fur), FUR)
    hands = {}
    for side, spec in zip((-1, 1), arms):
        Sh, E, Hh = _arm_pts(side, spec, t, L1=0.42, L2=0.38, sh=(0.48, 1.34 + br, 0.02))
        rig.caps(Sh, E, 0.15, 0.13, skin, SKIN); rig.caps(E, Hh, 0.13, 0.12, skin, SKIN)
        rig.sphere(Hh, 0.15, skin, SKIN)
        hands["L" if side < 0 else "R"] = rig.P(Hh)
    if club:
        Hh = hands["R"]; inv = rig  # palo apoyado en el hombro
        hp = np.array(_arm_pts(1, arms[1], t, L1=0.42, L2=0.38, sh=(0.48, 1.34 + br, 0.02))[2])
        rig.caps(hp + np.array([0, -0.15, 0.12]), hp + np.array([0.25, 1.05, 0.2]), 0.08, 0.2, (120, 80, 48), STONE)
    hc = np.array([0, 1.98 + br * 1.3, 0.04], np.float32); R = 0.6
    rig.sphere(hc + np.array([math.sin(head_yaw) * R, -0.06, math.cos(head_yaw) * R]), 0.17, tuple(min(255, int(c * 1.05)) for c in skin), SKIN)  # nariz
    # pelo revuelto + barba
    r_ = np.random.default_rng(var + 3)
    for k in range(11):
        a = -1.6 + k * 0.32 + head_yaw
        p = hc + np.array([math.sin(a) * R * 0.85, R * (0.55 + 0.1 * r_.uniform()), math.cos(a) * R * 0.6 - 0.15], np.float32)
        rig.sphere(p, 0.24 + 0.05 * r_.uniform(), hair, HAIR, oid=8100)
    for k in range(7):
        a = -1.0 + k * 0.33 + head_yaw
        p = hc + np.array([math.sin(a) * R * 0.86, -R * (0.55 + 0.12 * abs(math.sin(a * 2))), math.cos(a) * R * 0.75], np.float32)
        rig.sphere(p, 0.2, hair, HAIR, oid=8100)
    # uniceja
    _face(rig, hc, R, head_yaw, t, expr, mouth, look, blink, cheeks=False, eye_s=0.85, brow_col=hair,
          small_eyes=(expr not in ("shock",)), skin=skin, unibrow=True, oid=8001)
    def D(ax, ay): return np.array([math.sin(ax + head_yaw) * math.cos(ay), math.sin(ay), math.cos(ax + head_yaw) * math.cos(ay)])
    return dict(hands=hands, head=rig.P(hc), nose=rig.P(hc + D(0, -0.1) * R))

M_FUR = (128, 70, 44); M_FUR_D = (92, 48, 30); IVORY = (246, 236, 210)

def mamut(sc, x, y, z, t, s=1.0, face=-1, trunk=0.0, mouth=0.0, expr="neutral", walk=0.0, ears=0.0, eye_happy=False, blink=None):
    """Mamut de perfil mirando a `face` (-1 = izquierda). Altura ≈ 4.6 * s. trunk: 0 = colgando, 1 = arriba (rugido)."""
    f = face
    def P(px, py, pz=0.0): return np.array([x + px * f * s, y + py * s, z + pz * s], np.float32)
    # patas (las de atrás un poco más oscuras/al fondo)
    for k, (lx, dz) in enumerate([(-1.0, -0.6), (1.1, -0.6), (-0.9, 0.6), (1.2, 0.6)]):
        ph = math.sin(walk + k * 1.6) * (1 if walk else 0)
        col = M_FUR_D if dz < 0 else M_FUR
        sc.caps(P(lx, 1.8, dz), P(lx + ph * 0.25, 0.3 + max(0, ph) * 0.2, dz), 0.48 * s, 0.42 * s, col, FUR)
        sc.ell(P(lx + ph * 0.25, 0.22 + max(0, ph) * 0.2, dz + 0.1), 0.45 * s, 0.22 * s, 0.4 * s, (70, 52, 44), STONE)
    sc.ell(P(0, 2.5, 0), 2.1 * s, 1.55 * s, 1.4 * s, M_FUR, FUR, oid=7001)        # cuerpo
    sc.ell(P(-0.6, 3.45, 0), 1.35 * s, 0.95 * s, 1.0 * s, M_FUR, FUR, oid=7001)                       # joroba
    for k in range(7):  # mechones de pelo largo en el costado
        sc.ell(P(-1.5 + k * 0.5, 2.0 + 0.25 * math.sin(k * 1.7), 1.25), 0.13 * s, 0.55 * s, 0.1 * s, M_FUR_D, FUR, rot=0.15 * f * math.sin(t * 2 + k))
    sc.sphere(P(1.85, 1.3, 0.2), 0.0001, M_FUR, FUR)
    for k in range(6):  # flecos bajo la panza
        sc.ell(P(-1.3 + k * 0.5, 1.15 + 0.05 * math.sin(t * 3 + k), 0.7), 0.2 * s, 0.38 * s, 0.14 * s, M_FUR_D, FUR)
    sc.caps(P(-2.0, 2.9, 0), P(-2.5, 2.1 + 0.15 * math.sin(t * 4), 0), 0.14 * s, 0.07 * s, M_FUR_D, FUR)  # cola
    # cabeza
    hc = P(2.1, 3.5, 0.3); HR = 1.15
    sc.sphere(hc, HR * s, M_FUR, FUR, oid=7002)
    def surf(px, py, lift=0.03):
        dx, dy = px - 2.1, py - 3.5
        h = math.sqrt(max(0.0, HR * HR - dx * dx - dy * dy))
        return P(px, py, 0.3 + h + lift)
    sc.sphere(P(1.7, 4.55, 0.1), 0.55 * s, M_FUR_D, FUR, oid=7002)               # copete
    eo = 1.0 if eye_happy else 0.0
    sc.ell(surf(1.55 - 0.3 * ears, 3.45, 0.08), 0.5 * s, 0.72 * s, 0.12 * s, M_FUR_D, FUR, rot=0.2 * f)   # oreja
    # ojo
    ep = surf(2.62, 3.82, 0.0)
    if blink is None: blink = 1.0 if (t % 3.7) < 0.12 else 0.0
    if eye_happy:
        sc.ell(ep, 0.17 * s, 0.05 * s, 0.05 * s, (30, 20, 20), FLAT, rot=0.0)
    else:
        sc.ell(ep, 0.17 * s, 0.2 * s * (1 - 0.9 * blink), 0.08 * s, WHITE, EYE)
        if blink < 0.5:
            sc.ell(ep + np.array([0.05 * f * s, -0.02 * s, 0.06 * s]), 0.09 * s, 0.11 * s, 0.05 * s, DARK, EYE)
            sc.sphere(ep + np.array([0.02 * f * s, 0.05 * s, 0.11 * s]), 0.035 * s, WHITE, EMIT)
    br = {"angry": 0.35, "happy": -0.2}.get(expr, 0.0)
    sc.ell(ep + np.array([0, 0.28 * s, 0.06 * s]), 0.22 * s, 0.05 * s, 0.04 * s, (50, 30, 22), FLAT, rot=br * f)
    # colmillos
    for dz, sh in ((1.25, 1.0), (-0.5, 0.85)):
        pts = []
        for k in range(7):
            u = k / 6
            ang = -1.4 + u * 2.6
            pts.append(P(2.75 + 1.5 * u, 2.75 - 0.75 * u + 1.25 * u * u, dz + 0.3 * u))
        sc.chain(pts, [0.17 * s * sh * (1 - 0.8 * k / 6) + 0.02 for k in range(7)], IVORY if dz > 0 else (220, 210, 186), GLOSS)
    # trompa
    pts = []; rad = []
    for k in range(10):
        u = k / 9
        a = (-1.5 + 2.4 * trunk) * u + 0.35 * math.sin(t * 2.5 + u * 3) * u
        base = P(3.05, 3.2, 0.7)
        pts.append(None); rad.append(0.36 * s * (1 - 0.6 * u))
    p = np.array(surf(2.95, 3.15, -0.25)); pts[0] = p.copy()
    ang = -1.25 + 1.8 * trunk
    for k in range(1, 10):
        u = k / 9
        ang += (0.22 - 0.48 * trunk) * (1.2 if k > 6 else 0.6) + 0.08 * math.sin(t * 2.5 + k * 0.6)
        step = 0.36 * s
        p = p + np.array([math.cos(ang) * step * f, math.sin(ang) * step, 0.02 * s])
        pts[k] = p.copy()
    sc.chain(pts, rad, M_FUR, FUR)
    if mouth > 0.05:
        sc.ell(surf(2.55, 2.75, 0.05), 0.25 * s, (0.08 + 0.22 * mouth) * s, 0.06 * s, MOUTH, FLAT)
    return dict(head=hc, trunk_tip=pts[-1], back=P(-0.2, 4.2, 0.4), eye=ep)

# ------------------------------------------------------------ utilería
def pizza(sc, cx, cy, cz, r, t=0.0, tilt=0.42, bite=0.0, steam=True):
    """Pizza vista en 3/4 desde arriba."""
    sc.ell((cx, cy - r * 0.04, cz), r * 1.0, r * tilt, r * 0.18, (206, 140, 66), Mat(spec=0.2, shin=20, toon=0.6))   # borde
    sc.ell((cx, cy + r * 0.02, cz + 0.02), r * 0.86, r * tilt * 0.84, r * 0.16, (250, 196, 60), Mat(spec=0.55, shin=40, toon=0.4))  # queso
    rr = np.random.default_rng(5)
    for k in range(7):
        a = k * 0.9 + 0.3; d = 0.55 * r * (0.35 + 0.65 * ((k * 37) % 10) / 10)
        px, py = cx + math.cos(a) * d, cy + r * 0.04 + math.sin(a) * d * tilt
        sc.ell((px, py, cz + 0.22 * r), r * 0.15, r * 0.15 * tilt * 1.2, r * 0.05, (190, 40, 36), Mat(spec=0.5, shin=40))
    for k in range(4):
        a = k * 1.6 + 1.1; d = 0.45 * r
        sc.ell((cx + math.cos(a) * d, cy + r * 0.06 + math.sin(a) * d * tilt, cz + 0.23 * r), r * 0.08, r * 0.045, r * 0.03, (60, 150, 60), FLAT, rot=a)

def caja_pizza(sc, cx, cy, cz, w, abierta=0.0):
    sc.box((cx, cy, cz), w * 0.5, w * 0.11, w * 0.5, (226, 196, 150), Mat(spec=0.05, shin=6, toon=0.6), bevel=0.3)
    if abierta > 0:
        sc.box((cx, cy + w * 0.11 + w * 0.42 * abierta, cz - 0.05), w * 0.5, w * 0.42 * abierta, w * 0.05, (214, 180, 132), Mat(spec=0.05, toon=0.6), bevel=0.2)

def roca(sc, cx, cy, cz, r, col=(150, 140, 128), seed=0, mat=STONE):
    rr = np.random.default_rng(seed)
    sc.ell((cx, cy, cz), r * 1.2, r * 0.8, r, col, mat, oid=6000 + seed)
    for k in range(3):
        a = rr.uniform(0, 2 * math.pi)
        sc.sphere((cx + math.cos(a) * r * 0.6, cy + r * 0.2 + rr.uniform(-0.1, 0.25) * r, cz + 0.1 * r), r * rr.uniform(0.45, 0.6),
                  tuple(int(c * rr.uniform(0.9, 1.08)) for c in col), mat, oid=6000 + seed)

def gema(sc, cx, cy, cz, r, col):
    sc.ell((cx, cy, cz), r, r * 0.85, r * 0.8, col, Mat(spec=1.6, shin=120, toon=0.2, rim=1.5))
