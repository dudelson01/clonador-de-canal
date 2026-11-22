"""Folha de conferência de um plano com a FRASE falada embaixo de cada plano.
Uso: python ferramentas/folha_storyboard.py <plano.json> <pasta_tmp> <prefixo_saida>"""
import json, subprocess, cv2, numpy as np, os, sys
from concurrent.futures import ThreadPoolExecutor
plano, S, pre = sys.argv[1:4]; os.makedirs(S, exist_ok=True)
for f in os.listdir(S): os.remove(os.path.join(S, f))
c = json.load(open(plano)); ts = []; t = 0
for x in c: ts.append(t); t += x["dur"]
def um(i):
    x = c[i]; o = os.path.join(S, f"{i:03d}.png")
    if x["src"] == "ARTE": cmd = ["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "color=c=0x1b2430:s=240x135", "-frames:v", "1", o]
    elif x["src"].endswith(".jpg"): cmd = ["ffmpeg", "-v", "error", "-y", "-i", x["src"], "-vf", "scale=240:135:force_original_aspect_ratio=decrease,pad=240:135:(ow-iw)/2:(oh-ih)/2", "-frames:v", "1", o]
    else:
        m = x["ss"] + x["dur"] * x.get("vel", 1) / 2
        cmd = ["ffmpeg", "-v", "error", "-y", "-ss", str(m), "-i", x["src"], "-frames:v", "1", "-vf", "scale=240:135" + (",hflip" if x.get("espelhar") else ""), o]
    subprocess.run(cmd, stderr=subprocess.DEVNULL)
with ThreadPoolExecutor(4) as ex: list(ex.map(um, range(len(c))))
ims = []
for i, x in enumerate(c):
    im = cv2.imread(os.path.join(S, f"{i:03d}.png")); im = cv2.resize(im, (240, 135)) if im is not None else np.zeros((135, 240, 3), np.uint8)
    im = cv2.copyMakeBorder(im, 0, 18, 0, 0, cv2.BORDER_CONSTANT)
    cv2.putText(im, f"{i} {ts[i]:.0f}s", (2, 12), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)
    cv2.putText(im, x.get("_frase", "")[:30], (2, 149), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1); ims.append(im)
ims += [np.zeros_like(ims[0])] * ((-len(ims)) % 10)
rows = [np.hstack(ims[i:i + 10]) for i in range(0, len(ims), 10)]
for p in range(0, len(rows), 9): cv2.imwrite(f"{pre}_{p // 9 + 1}.png", np.vstack(rows[p:p + 9]))
print(len(rows), "linhas")
