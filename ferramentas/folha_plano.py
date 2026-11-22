"""Folhas de conferência do plano: um quadro do meio de cada cena, com índice, tempo e filme.
Uso: python ferramentas/folha_plano.py <plano.json> <pasta_saida> [--ini 32]"""
import json, subprocess, sys, pathlib, cv2, numpy as np
from concurrent.futures import ThreadPoolExecutor
plano, out = sys.argv[1], pathlib.Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
t0 = float(sys.argv[sys.argv.index("--ini") + 1]) if "--ini" in sys.argv else 32.0
c = json.load(open(plano)); ts = []; t = t0
for x in c: ts.append(t); t += x["dur"]
F = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
def um(i):
    x = c[i]; lab = f"{i} {ts[i]:.0f}s {(x.get('_filme') or 'ARTE')[:10]}"; o = str(out / f"{i:03d}.png")
    if x["src"] == "ARTE":
        cmd = ["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "color=c=0x1b2430:s=240x135", "-frames:v", "1"]
    else:
        m = x["ss"] + x["dur"] * x.get("vel", 1) / 2
        cmd = ["ffmpeg", "-v", "error", "-y", "-ss", str(m), "-i", x["src"], "-frames:v", "1"]
    subprocess.run(cmd + ["-vf", f"scale=240:135,setsar=1,drawtext=fontfile={F}:text='{lab}':fontsize=12:fontcolor=yellow:box=1:boxcolor=black:x=2:y=2", o],
                   stderr=subprocess.DEVNULL)
with ThreadPoolExecutor(4) as ex: list(ex.map(um, range(len(c))))
fs = [out / f"{i:03d}.png" for i in range(len(c))]
for p, a in enumerate(range(0, len(fs), 88)):
    ims = [cv2.resize(cv2.imread(str(f)), (240, 135)) for f in fs[a:a + 88]]
    ims += [np.zeros_like(ims[0])] * ((-len(ims)) % 11)
    cv2.imwrite(str(out.parent / f"folha_plano_{p + 1}.png"), np.vstack([np.hstack(ims[i:i + 11]) for i in range(0, len(ims), 11)]))
print("ok")
