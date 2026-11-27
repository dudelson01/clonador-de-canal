#!/usr/bin/env python3
"""Folha de conferencia das etiquetas (nome + seta) num video montado: 2 quadros por etiqueta
(logo depois de a seta terminar de desenhar e perto do fim), para ver se aponta para o personagem certo.
Uso: python3 conferir_setas.py plano.json video.mp4 saida.png"""
import json, subprocess, sys, os, tempfile
plano = json.load(open(sys.argv[1])); video, saida = sys.argv[2], sys.argv[3]
tmp = tempfile.mkdtemp()
fs = []
for a in plano["artes"]:
    if a["tipo"] != "etiqueta": continue
    for j, t in enumerate([a["ini"] + min(0.5, a["dur"] * 0.6), a["ini"] + a["dur"] - 0.08]):
        f = os.path.join(tmp, f"{len(fs):03d}.png")
        txt = f"{a['id']} {t:.2f}".replace(":", "\\:")
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", f"{t:.3f}", "-i", video, "-frames:v", "1", "-vf",
                        f"scale=384:-2,drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:text='{txt}':x=3:y=3:fontsize=15:fontcolor=yellow:box=1:boxcolor=black", f])
        fs.append(f)
subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-framerate", "1", "-i", os.path.join(tmp, "%03d.png"), "-vf", "tile=6x8", "-frames:v", "1", saida])
print(len(fs) // 2, "etiquetas ->", saida)
