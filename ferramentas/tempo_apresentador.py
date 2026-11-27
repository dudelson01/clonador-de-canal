#!/usr/bin/env python3
"""Estima % do tempo com o apresentador na tela (cenario fixo), comparando cada segundo com um quadro de referencia.
Uso: python3 tempo_apresentador.py video.mp4 segundo_do_quadro_com_apresentador [limiar=0.80]
Funciona porque o apresentador grava sempre no mesmo cenario. Imprime % e os trechos."""
import subprocess, sys, numpy as np

video, t_ref = sys.argv[1], float(sys.argv[2])
lim = float(sys.argv[3]) if len(sys.argv) > 3 else 0.80
W, H = 48, 27
raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", video, "-map", "0:v:0", "-vf",
                      f"fps=1,scale={W}:{H},format=rgb24", "-f", "rawvideo", "-"], capture_output=True).stdout
fr = np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3).astype(np.float32)
def norm(a):
    a = a - a.mean(); return a / (np.linalg.norm(a) + 1e-6)
ref = norm(fr[int(t_ref)])
# borda do quadro (cenario) pesa mais que o centro (onde a pessoa se mexe)
mask = np.ones((H, W, 1), np.float32); mask[5:22, 14:34] = 0.3
sim = np.array([float((norm(f * mask) * norm(fr[int(t_ref)] * mask)).sum()) for f in fr])
on = sim >= lim
print(f"apresentador: {on.mean()*100:.0f}% de {len(fr)} s")
# trechos
trechos, ini = [], None
for i, v in enumerate(list(on) + [False]):
    if v and ini is None: ini = i
    if not v and ini is not None: trechos.append((ini, i)); ini = None
dur = [b - a for a, b in trechos]
if dur: print(f"vezes que aparece: {len(dur)} | duracao media: {np.mean(dur):.1f}s | maior: {max(dur)}s")
print("primeiros 90 s:", "".join("#" if x else "." for x in on[:90]))
