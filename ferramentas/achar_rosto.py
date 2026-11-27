#!/usr/bin/env python3
"""Acha o rosto do apresentador num trecho de video (sem bibliotecas extras: cor de pele + numpy).
Funciona bem com cenario fixo (parede/cortina) e o apresentador de frente para a camera.
rosto(video, ini, fim) -> (cx, cy, alto) em fracao do quadro: centro do rosto e altura aproximada do rosto.
Uso direto: python3 achar_rosto.py video.mp4 ini fim"""
import subprocess, sys, numpy as np

W, H = 192, 108

def quadros(video, ini, fim, passo=0.4):
    out = []
    t = ini + 0.05
    while t < fim - 0.02:
        raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-ss", f"{t:.3f}", "-i", video, "-frames:v", "1",
                              "-vf", f"scale={W}:{H}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
        if len(raw) == W * H * 3: out.append(np.frombuffer(raw, np.uint8).reshape(H, W, 3).astype(np.float32))
        t += passo
    return out

def pele(img):
    r, g, b = img[..., 0], img[..., 1], img[..., 2]
    y = 0.299 * r + 0.587 * g + 0.114 * b
    cr = (r - y) * 0.713 + 128; cb = (b - y) * 0.564 + 128
    return (cr > 136) & (cr < 175) & (cb > 85) & (cb < 128) & (y > 35) & (r > b + 10)

def um_quadro(img):
    m = pele(img).astype(np.float32)
    m[int(H * 0.80):] = 0                      # ignora a parte de baixo (maos, braco)
    col = m.sum(0); col = np.convolve(col, np.ones(9) / 9, "same")
    if col.max() < 3: return None
    cx = int(np.argmax(col))
    faixa = m[:, max(0, cx - 14):cx + 15]      # coluna do rosto (~15% da largura)
    lin = faixa.sum(1)
    linhas = np.where(lin > max(3, lin.max() * 0.35))[0]
    if len(linhas) < 5: return None
    topo, base = linhas[0], linhas[0]
    for k in linhas:                           # bloco continuo de cima para baixo (testa ate o queixo)
        if k - base > 9: break   # atravessa a tira escura do bone
        base = k
    alto = (base - topo + 1) / H
    # centro horizontal refinado: media ponderada da pele dentro do bloco do rosto
    bloco = m[topo:base + 1, max(0, cx - 20):cx + 21]
    xs = np.arange(max(0, cx - 20), max(0, cx - 20) + bloco.shape[1])
    if bloco.sum() > 0: cx = float((bloco.sum(0) * xs).sum() / bloco.sum(0).sum())
    return cx / W, (topo + base) / 2 / H, alto

def rosto(video, ini, fim):
    rs = [x for x in (um_quadro(q) for q in quadros(video, ini, fim)) if x]
    if not rs: return None
    a = np.array(rs)
    return tuple(float(v) for v in np.median(a, 0))

if __name__ == "__main__":
    print(rosto(sys.argv[1], float(sys.argv[2]), float(sys.argv[3])))
