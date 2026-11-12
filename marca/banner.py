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
# escenas laterales: pirámide (izq) y columna romana (der), fuera de la zona segura
d.polygon([(250, 980), (700, 980), (475, 560)], fill=(236, 190, 116, 255)); d.polygon([(475, 560), (700, 980), (520, 980)], fill=(184, 128, 76, 255))
for x0 in (2150, 2330):
    d.rectangle([x0, 600, x0+90, 980], fill=(226, 222, 210, 255)); d.rectangle([x0-20, 570, x0+110, 610], fill=(240, 236, 226, 255))
d.rectangle([2110, 540, 2460, 575], fill=(240, 236, 226, 255))
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
