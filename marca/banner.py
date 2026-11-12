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
planeta(d, 330, 640, 110); reloj(d, 300, 960, 85); rayo(d, 620, 1010, 0.9)
cohete(d, 2250, 700, 1.1); planeta(d, 2330, 1040, 60)
fq = ImageFont.truetype(E.F_BLACK, 150)
for (qx, qy, col) in [(560, 470, (90, 230, 255)), (2050, 1020, (200, 120, 255)), (2420, 470, (255, 214, 10))]:
    d.text((qx, qy), "?", font=fq, fill=col, stroke_width=10, stroke_fill=(20, 10, 40))

# portal + Nico a la izquierda de la zona segura
cx, cy = 900, 730
E.glow(img, cx, cy, 560, (150, 80, 255), 0.7)
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
d.text((1115, 830), "¿Qué pasaría si…? · Videos 8 a. m. y 6 p. m.", font=f2, fill=(255, 255, 255), stroke_width=4, stroke_fill=(0, 0, 0))
img.convert("RGB").save(__import__("os").path.join(__import__("os").path.dirname(__import__("os").path.abspath(__file__)), "banner_youtube.png"))
# vista previa con zona segura móvil (1546x423)
pv = img.convert("RGB").copy(); ImageDraw.Draw(pv).rectangle([507, 508, 2053, 931], outline=(255, 0, 0), width=6)
pv.resize((1280, 720)).save("/tmp/banner_pv.png")
