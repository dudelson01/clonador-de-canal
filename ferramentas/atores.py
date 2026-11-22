"""Acha em que momentos de cada trailer aparece cada ator (reconhecimento facial).

python ferramentas/atores.py <pasta_rostos> <pasta_fotos> <atores.json> <saida.json> <pasta_folhas>

atores.json = {"bill-murray": {"trailers": ["ghostbusters-1984"], "refs": ["ghostbusters-1984@108.5"]}, ...}
  refs extras "trailer@tempo" = um quadro do trailer onde o ator aparece (o maior rosto naquele instante).
Saída: {ator: {trailer: [{"t": s, "area": a, "sim": x}, ...]}} + folhas de conferência por ator.
"""
import json, sys, os, glob, subprocess
import numpy as np, cv2
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rostos import assinatura, cos

pasta_r, pasta_f, atores_f, saida, folhas = sys.argv[1:6]
A = json.load(open(atores_f)); os.makedirs(folhas, exist_ok=True)
TR = os.path.join(os.path.dirname(pasta_r.rstrip("/")), "..", "midia", "trailers")


def carrega(tr):
    d = np.load(os.path.join(pasta_r, tr + ".npz"))
    return d["t"], d["area"], d["feat"], d["box"]


res = {}
for ator, cfg in A.items():
    refs = []
    for f in glob.glob(os.path.join(pasta_f, ator, "*.jpg")):
        s = assinatura(f)
        if s is not None: refs.append(s)
    for r in cfg.get("refs", []):
        tr, t = r.split("@"); T, Ar, F, B = carrega(tr)
        ix = np.where(np.abs(T - float(t)) < 0.26)[0]
        if len(ix): refs.append(F[ix[np.argmax(Ar[ix])]])
    if not refs: print(ator, "SEM REFERÊNCIA"); continue
    R = np.array(refs); res[ator] = {}
    for tr in cfg["trailers"]:
        T, Ar, F, B = carrega(tr)
        if len(T) == 0: continue
        s = cos(F, R).max(1)
        ok = s >= 0.36
        if ok.sum() >= 2:  # amplia com os próprios achados (outros ângulos do mesmo ator)
            R2 = np.vstack([R, F[ok]]); s = np.maximum(s, cos(F, R2[len(R):]).mean(1) + 0.05)
            ok = s >= 0.40
        achados = [{"t": float(t), "area": float(a), "sim": round(float(x), 3), "box": b.tolist()}
                   for t, a, x, b, o in zip(T, Ar, s, B, ok) if o]
        res[ator][tr] = achados
        # folha de conferência: os 12 maiores rostos achados
        top = sorted(achados, key=lambda x: -x["area"])[:12]
        ims = []
        for x in top:
            v = os.path.join(TR, tr + ".mp4")
            b = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(x["t"]), "-i", v, "-frames:v", "1", "-vf", "scale=320:180",
                                "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], capture_output=True).stdout
            if len(b) < 320 * 180 * 3: continue
            im = np.frombuffer(b[:320 * 180 * 3], np.uint8).reshape(180, 320, 3).copy()
            cv2.putText(im, f"{x['t']:.1f} {x['sim']}", (3, 14), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 255), 1)
            ims.append(im)
        if ims:
            ims += [np.zeros_like(ims[0])] * ((-len(ims)) % 6)
            cv2.imwrite(os.path.join(folhas, f"{ator}__{tr}.png"), np.vstack([np.hstack(ims[i:i + 6]) for i in range(0, len(ims), 6)]))
        print(ator, tr, len(achados), "aparições", flush=True)
json.dump(res, open(saida, "w"))
