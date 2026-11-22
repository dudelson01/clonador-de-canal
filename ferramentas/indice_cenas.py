"""Indexa as cenas de vários trailers: rosto (tamanho), brilho, movimento e "cara de cartela" (texto/logo).

Uso: python ferramentas/indice_cenas.py <pasta_trailers> <saida.json>
Usa as folhas <build>/folhas/<nome>.json (de folha_cenas.py) se existirem; senão detecta os cortes.
"""
import json, sys, pathlib, subprocess
import numpy as np, cv2

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from folha_cenas import cortes

CASC = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")


def quadro(video, t):
    r = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", video, "-frames:v", "1",
                        "-vf", "scale=480:270:force_original_aspect_ratio=decrease,pad=480:270:(ow-iw)/2:(oh-ih)/2",
                        "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], capture_output=True)
    if len(r.stdout) < 480 * 270 * 3: return None
    return np.frombuffer(r.stdout[:480 * 270 * 3], np.uint8).reshape(270, 480, 3)


def analisa(video, cenas, dur_total):
    out = []
    for c in cenas:
        d = c["fim"] - c["ini"]
        ts = [c["ini"] + d * k for k in (0.2, 0.5, 0.8)]
        fr = [quadro(video, t) for t in ts]
        fr = [f for f in fr if f is not None]
        if not fr: continue
        rost, bril, sat, var, mov = 0.0, [], [], [], 0.0
        for f in fr:
            g = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)
            faces = CASC.detectMultiScale(g, 1.15, 5, minSize=(24, 24))
            if len(faces): rost = max(rost, max(w * h for x, y, w, h in faces) / (480 * 270))
            hsv = cv2.cvtColor(f, cv2.COLOR_BGR2HSV)
            bril.append(float(hsv[..., 2].mean())); sat.append(float(hsv[..., 1].mean())); var.append(float(g.std()))
        if len(fr) > 1:
            mov = float(np.mean([np.abs(fr[i].astype(int) - fr[i + 1].astype(int)).mean() for i in range(len(fr) - 1)]))
        b, s, v = np.mean(bril), np.mean(sat), np.mean(var)
        # cartela: escuro e quase sem textura, ou fim/começo do trailer (logos e créditos)
        cartela = (b < 28 and v < 22) or c["ini"] < 3.5 or c["fim"] > dur_total - 6
        out.append({**c, "rosto": round(rost, 4), "brilho": round(b, 1), "sat": round(s, 1),
                    "mov": round(mov, 1), "cartela": bool(cartela)})
    return out


def main():
    pasta, saida = pathlib.Path(sys.argv[1]), sys.argv[2]
    folhas = pasta.parent.parent / "build" / "folhas"
    idx = {}
    for v in sorted(pasta.glob("*.mp4")):
        dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(v)],
                                   capture_output=True, text=True).stdout)
        j = folhas / f"{v.stem}.json"
        cenas = json.loads(j.read_text()) if j.exists() else cortes(str(v))
        idx[v.stem] = analisa(str(v), cenas, dur)
        print(v.stem, len(idx[v.stem]), "cenas,", sum(not c["cartela"] for c in idx[v.stem]), "úteis,",
              sum(c["rosto"] > 0 for c in idx[v.stem]), "com rosto", flush=True)
    pathlib.Path(saida).write_text(json.dumps(idx, ensure_ascii=False, indent=0))


if __name__ == "__main__":
    main()
