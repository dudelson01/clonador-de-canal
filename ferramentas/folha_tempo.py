"""Folha com um quadro a cada N segundos e o tempo escrito (para achar cenas específicas).
Uso: python ferramentas/folha_tempo.py <video> <saida.png> [--passo 1] [--ini 0] [--fim 9999] [--col 12]"""
import sys, subprocess, numpy as np, cv2
a = sys.argv; v, out = a[1], a[2]
op = lambda n, d: float(a[a.index("--" + n) + 1]) if "--" + n in a else d
passo, ini, fim, col = op("passo", 1), op("ini", 0), op("fim", 9999), int(op("col", 12))
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", v], capture_output=True, text=True).stdout)
fim = min(fim, dur)
b = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(ini), "-t", str(fim - ini), "-i", v, "-vf", f"fps=1/{passo},scale=200:112",
                    "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], capture_output=True).stdout
f = np.frombuffer(b, np.uint8).reshape(-1, 112, 200, 3).copy()
for k in range(len(f)):
    cv2.putText(f[k], f"{ini + k * passo:.1f}", (2, 12), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)
ims = list(f) + [np.zeros_like(f[0])] * ((-len(f)) % col)
cv2.imwrite(out, np.vstack([np.hstack(ims[i:i + col]) for i in range(0, len(ims), col)]))
print(len(f), "quadros")
