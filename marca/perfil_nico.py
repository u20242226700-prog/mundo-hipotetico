import math, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import sys; sys.path.insert(0, "../episodios/2026-11-11-celular-egipto"); import episodio as E
WW, WH = 1296, 2304
c = (np.arange(WW) - 648) / 648; r_ = (np.arange(WH) - 1050) / 648
X, Y = np.meshgrid(c, r_); rr = np.sqrt(X**2 + Y**2)
top = np.array([96, 44, 180]); bot = np.array([12, 8, 40])
bg = bot + (top - bot) * np.clip(1 - rr * 0.9, 0, 1)[..., None] ** 1.3
img = Image.fromarray(bg.astype(np.uint8)).convert("RGBA")
d = ImageDraw.Draw(img); rng = np.random.default_rng(5)
for _ in range(200):
    x, y, s = rng.uniform(0, WW), rng.uniform(0, WH), rng.uniform(1.5, 4)
    d.ellipse([x-s, y-s, x+s, y+s], fill=(255, 255, 255, int(rng.uniform(80, 230))))
# portal detrás de la cabeza
cx, cy = 648, 1000
E.glow(img, cx, cy, 1300, (150, 80, 255), 0.7)
lay = Image.new("RGBA", (WW, WH), (0,0,0,0)); dd = ImageDraw.Draw(lay)
for k in range(6):
    r = 470 - k*40; col = (90, 230, 255, 255) if k % 2 else (200, 120, 255, 255)
    a0 = k * 50
    dd.arc([cx-r, cy-r, cx+r, cy+r], a0, a0 + 290, fill=col, width=22 - k*2)
lay = Image.alpha_composite(lay.filter(ImageFilter.GaussianBlur(14)), lay)
img.alpha_composite(lay)
E.glow(img, cx, cy, 700, (255, 255, 255), 0.35)
# Nico saludando
E.nico(img, 648, 1880, 2.05, "happy", look=(0, 0.3), arms="up", phase=0.6)
# signo de pregunta
f = ImageFont.truetype("/usr/share/fonts/opentype/inter/InterDisplay-Black.otf", 260)
q = Image.new("RGBA", (320, 360), (0,0,0,0)); qd = ImageDraw.Draw(q)
qd.text((50, 10), "?", font=f, fill=(255, 214, 10), stroke_width=16, stroke_fill=(20, 10, 40))
q = q.rotate(-16, resample=Image.BICUBIC, expand=True)
img.alpha_composite(q, (790, 600))
out = img.crop((648-560, 1080-560, 648+560, 1080+560)).resize((1080, 1080), Image.LANCZOS)
out.convert("RGB").save("foto_perfil_nico.png")
# vista previa en círculo
m = Image.new("L", (1080,1080), 0); ImageDraw.Draw(m).ellipse([0,0,1079,1079], fill=255)
pv = Image.new("RGB", (1080,1080), (255,255,255)); pv.paste(out.convert("RGB"), (0,0), m); pv.resize((300,300)).save("pv_circle.png")
