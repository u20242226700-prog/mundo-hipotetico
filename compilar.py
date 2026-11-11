#!/usr/bin/env python3
"""Recopilatorio semanal para YouTube (video normal 16:9).

Uso:
  python3 compilar.py salida.mp4 "Título del recopilatorio" "episodios/carpeta1|Título 1" "episodios/carpeta2|Título 2" ...

Cada Short vertical se coloca centrado sobre su propio fondo desenfocado (1920x1080), con una tarjeta
de título de 1.6 s antes de cada historia y una portada de 3 s al inicio. Sin voz nueva.
"""
import os, sys, subprocess, tempfile
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np

W, H, FPS = 1920, 1080, 30
F_BLACK = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
F_BOLD = "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"
AQUI = os.path.dirname(os.path.abspath(__file__))
NICO = os.path.join(AQUI, "marca", "foto_perfil_nico.png")

def run(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

def fondo():
    c = (np.arange(W) - W / 2) / (W / 2); r = (np.arange(H) - H / 2) / (H / 2)
    X, Y = np.meshgrid(c, r); rr = np.sqrt(X ** 2 * 0.6 + Y ** 2)
    top = np.array([96, 44, 180]); bot = np.array([10, 8, 36])
    arr = bot + (top - bot) * np.clip(1 - rr * 0.8, 0, 1)[..., None] ** 1.3
    return Image.fromarray(arr.astype(np.uint8)).convert("RGBA")

def texto_centrado(img, txt, y, size, color, max_w=W - 200):
    d = ImageDraw.Draw(img)
    while size > 40:
        f = ImageFont.truetype(F_BLACK, size)
        if f.getlength(txt) <= max_w: break
        size -= 6
    d.text((W / 2 - f.getlength(txt) / 2, y), txt, font=f, fill=color, stroke_width=10, stroke_fill=(0, 0, 0))

def tarjeta(path, titulo, sub=None, con_nico=False):
    img = fondo()
    if con_nico and os.path.exists(NICO):
        n = Image.open(NICO).convert("RGBA").resize((520, 520))
        m = Image.new("L", n.size, 0); ImageDraw.Draw(m).ellipse([0, 0, 519, 519], fill=255)
        img.paste(n, (W // 2 - 260, 90), m)
        texto_centrado(img, titulo, 660, 96, (255, 214, 10))
        if sub: texto_centrado(img, sub, 800, 54, (255, 255, 255))
    else:
        if sub: texto_centrado(img, sub, 380, 56, (255, 255, 255))
        texto_centrado(img, titulo, 470, 100, (255, 214, 10))
    img.convert("RGB").save(path)

def clip_imagen(img, seg, out):
    run(["ffmpeg", "-y", "-loop", "1", "-i", img, "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
         "-t", str(seg), "-r", str(FPS), "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "160k", "-shortest", out])

def clip_short(src, out):
    vf = (f"[0:v]split=2[a][b];[a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=30:5,eq=brightness=-0.12[bg];"
          f"[b]scale=-2:{H}[fg];[bg][fg]overlay=(W-w)/2:0,fps={FPS},format=yuv420p[v]")
    run(["ffmpeg", "-y", "-i", src, "-filter_complex", vf, "-map", "[v]", "-map", "0:a?", "-c:v", "libx264", "-preset", "veryfast",
         "-crf", "20", "-c:a", "aac", "-b:a", "160k", "-ar", "44100", "-ac", "2", out])

def main():
    out, titulo, items = sys.argv[1], sys.argv[2], sys.argv[3:]
    tmp = tempfile.mkdtemp()
    partes = []
    tarjeta(f"{tmp}/portada.png", titulo, "Mundo Hipotético", con_nico=True)
    clip_imagen(f"{tmp}/portada.png", 3, f"{tmp}/00.mp4"); partes.append(f"{tmp}/00.mp4")
    for k, it in enumerate(items, 1):
        carpeta, t = it.split("|", 1)
        tarjeta(f"{tmp}/t{k}.png", t, f"Historia {k}")
        clip_imagen(f"{tmp}/t{k}.png", 1.6, f"{tmp}/{k:02d}a.mp4")
        clip_short(os.path.join(carpeta, "video.mp4"), f"{tmp}/{k:02d}b.mp4")
        partes += [f"{tmp}/{k:02d}a.mp4", f"{tmp}/{k:02d}b.mp4"]
    tarjeta(f"{tmp}/fin.png", "¿Qué hacemos la próxima semana?", "Comenta tu idea 👇  ·  Suscríbete", con_nico=True)
    clip_imagen(f"{tmp}/fin.png", 4, f"{tmp}/99.mp4"); partes.append(f"{tmp}/99.mp4")
    with open(f"{tmp}/lista.txt", "w") as f:
        for p in partes: f.write(f"file '{p}'\n")
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", f"{tmp}/lista.txt", "-c", "copy", "-movflags", "+faststart", out])
    print("listo", out)

if __name__ == "__main__":
    main()
