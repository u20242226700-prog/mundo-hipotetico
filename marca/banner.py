import sys, math, numpy as np
import os; EP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "episodios", "2026-11-11-celular-egipto"); sys.path.insert(0, EP); os.chdir(EP)
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import episodio as E
W, H = 2560, 1440
c = (np.arange(W) - W/2) / (W/2); r = (np.arange(H) - H/2) / (H/2)
X, Y = np.meshgrid(c, r); rr = np.sqrt(X**2*0.35 + Y**2)
top = np.array([100, 46, 186]); bot = np.array([10, 8, 36])
img = Image.fromarray((bot + (top-bot)*np.clip(1-rr*0.9, 0, 1)[..., None]**1.3).astype(np.uint8)).convert("RGBA")
d = ImageDraw.Draw(img); rng = np.random.default_rng(4)
for _ in range(500):
    x, y, s = rng.uniform(0, W), rng.uniform(0, H), rng.uniform(1.5, 4)
    d.ellipse([x-s, y-s, x+s, y+s], fill=(255, 255, 255, int(rng.uniform(70, 230))))
# nebulosas
neb = Image.new("RGBA", (W, H), (0, 0, 0, 0)); nd = ImageDraw.Draw(neb)
for (nx, ny, nr, col) in [(300, 300, 420, (255, 80, 180, 90)), (2300, 350, 460, (60, 200, 255, 80)), (1280, 200, 520, (150, 90, 255, 70)), (400, 1200, 380, (60, 200, 255, 60)), (2250, 1150, 420, (255, 120, 80, 70))]:
    nd.ellipse([nx-nr, ny-nr*0.7, nx+nr, ny+nr*0.7], fill=col)
img.alpha_composite(neb.filter(ImageFilter.GaussianBlur(120)))
# Tierra gigante asomando abajo
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render as RR
earth = RR.earth(2600, 2.4, 18)
E.glow(img, W//2, H + 1050, 3200, (90, 170, 255), 0.55)
img.alpha_composite(earth.crop((0, 0, 2600, 380)), (W//2 - 1300, H - 380))
d = ImageDraw.Draw(img)
# líneas de velocidad saliendo del portal
cxp, cyp = 900, 730
for k in range(36):
    ang = k / 36 * 2 * math.pi + 0.07
    r0, r1 = 260, 260 + 120 + (k * 53 % 140)
    d.line([cxp + math.cos(ang) * r0, cyp + math.sin(ang) * r0 * 0.9, cxp + math.cos(ang) * r1, cyp + math.sin(ang) * r1 * 0.9], fill=(200, 160, 255, 90), width=4)
# elementos genéricos a los lados (fuera de la zona segura): planeta, reloj, rayo, cohete y signos de pregunta
def planeta(d, x, y, r):
    d.ellipse([x-r, y-r, x+r, y+r], fill=(255, 140, 90, 255))
    d.chord([x-r, y-r, x+r, y+r], 200, 340, fill=(255, 175, 120, 255))
    d.arc([x-r*1.7, y-r*0.45, x+r*1.7, y+r*0.45], 0, 180, fill=(255, 214, 10, 255), width=14)
def reloj(d, x, y, r):
    d.ellipse([x-r, y-r, x+r, y+r], fill=(245, 245, 255, 255), outline=(30, 20, 50, 255), width=12)
    d.line([x, y, x, y-r*0.65], fill=(30, 20, 50, 255), width=12); d.line([x, y, x+r*0.45, y+r*0.2], fill=(30, 20, 50, 255), width=12)
def rayo(d, x, y, s):
    d.polygon([(x, y), (x+60*s, y), (x+20*s, y+90*s), (x+70*s, y+90*s), (x-20*s, y+230*s), (x+10*s, y+120*s), (x-40*s, y+120*s)], fill=(255, 214, 10, 255), outline=(30, 20, 50, 255))
def cohete(d, x, y, s):
    d.polygon([(x, y-150*s), (x+55*s, y-40*s), (x+55*s, y+90*s), (x-55*s, y+90*s), (x-55*s, y-40*s)], fill=(240, 240, 250, 255), outline=(30, 20, 50, 255))
    d.ellipse([x-28*s, y-50*s, x+28*s, y+6*s], fill=(90, 200, 255, 255), outline=(30, 20, 50, 255), width=6)
    d.polygon([(x-55*s, y+30*s), (x-100*s, y+110*s), (x-55*s, y+90*s)], fill=(255, 80, 90, 255))
    d.polygon([(x+55*s, y+30*s), (x+100*s, y+110*s), (x+55*s, y+90*s)], fill=(255, 80, 90, 255))
    d.polygon([(x-30*s, y+90*s), (x+30*s, y+90*s), (x, y+170*s)], fill=(255, 170, 40, 255))
for (gx, gy, gs, gc) in [(330, 640, 360, (255, 140, 90)), (300, 960, 260, (255, 255, 255)), (650, 1100, 300, (255, 214, 10)), (2250, 700, 420, (90, 200, 255)), (2460, 960, 220, (255, 140, 90))]:
    E.glow(img, gx, gy, gs, gc, 0.45)
d = ImageDraw.Draw(img)
planeta(d, 330, 640, 110); reloj(d, 300, 960, 85); rayo(d, 620, 1010, 0.9)
cohete(d, 2250, 700, 1.1); planeta(d, 2460, 960, 60)
# estela del cohete
for k in range(8):
    rr_ = 22 - k * 2; yy = 905 + k * 30
    d.ellipse([2250 - rr_, yy - rr_, 2250 + rr_, yy + rr_], fill=(255, 210, 140, max(0, 200 - k * 25)))
# destellos
for (sx, sy, ss) in [(800, 420, 26), (1700, 470, 20), (2000, 980, 24), (500, 840, 18), (1850, 560, 16), (1100, 1000, 20)]:
    d.polygon([(sx, sy - ss), (sx + ss * 0.25, sy - ss * 0.25), (sx + ss, sy), (sx + ss * 0.25, sy + ss * 0.25), (sx, sy + ss), (sx - ss * 0.25, sy + ss * 0.25), (sx - ss, sy), (sx - ss * 0.25, sy - ss * 0.25)], fill=(255, 255, 255, 230))
fq = ImageFont.truetype(E.F_BLACK, 150)
for (qx, qy, col) in [(560, 470, (90, 230, 255)), (2050, 1020, (200, 120, 255)), (2420, 470, (255, 214, 10))]:
    d.text((qx, qy), "?", font=fq, fill=col, stroke_width=10, stroke_fill=(20, 10, 40))

# portal + Nico a la izquierda de la zona segura
cx, cy = 900, 730
E.glow(img, cx, cy, 760, (150, 80, 255), 0.85)
lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dd = ImageDraw.Draw(lay)
for k in range(5):
    rad = 165 - k*20; col = (90, 230, 255, 255) if k % 2 else (200, 120, 255, 255)
    dd.arc([cx-rad, cy-rad, cx+rad, cy+rad], k*60, k*60+290, fill=col, width=14-k*2)
img.alpha_composite(Image.alpha_composite(lay.filter(ImageFilter.GaussianBlur(10)), lay))
E.nico(img, cx, 915, 0.72, "happy", arms="up", phase=0.6)
# texto
f1 = ImageFont.truetype(E.F_BLACK, 110); f2 = ImageFont.truetype(E.F_BOLD, 40)
d = ImageDraw.Draw(img)
d.text((1110, 575), "Mundo", font=f1, fill=(255, 255, 255), stroke_width=10, stroke_fill=(0, 0, 0))
d.text((1110, 685), "Hipotético", font=f1, fill=(255, 214, 10), stroke_width=10, stroke_fill=(0, 0, 0))
d.rounded_rectangle([1100, 822, 1990, 892], radius=35, fill=(20, 12, 50, 210), outline=(150, 110, 255, 255), width=4)
d.text((1130, 832), "¿Qué pasaría si…? · Videos 8 a. m. y 6 p. m.", font=f2, fill=(255, 255, 255), stroke_width=4, stroke_fill=(0, 0, 0))
img.convert("RGB").save(__import__("os").path.join(__import__("os").path.dirname(__import__("os").path.abspath(__file__)), "banner_youtube.png"))
# vista previa con zona segura móvil (1546x423)
pv = img.convert("RGB").copy(); ImageDraw.Draw(pv).rectangle([507, 508, 2053, 931], outline=(255, 0, 0), width=6)
pv.resize((1280, 720)).save("/tmp/banner_pv.png")
