"""Reconhecimento facial nos trailers: acha em que momentos aparece cada ator.

Modelos (OpenCV Zoo, baixados do Hugging Face para ferramentas/modelos/):
  face_detection_yunet_2023mar.onnx, face_recognition_sface_2021dec.onnx

python ferramentas/rostos.py varrer <pasta_trailers> <saida_dir>          -> <saida>/<trailer>.npz (rostos a cada 0,5 s)
python ferramentas/rostos.py ator <foto_ou_quadro.jpg> <saida.npy>          -> assinatura do rosto (o maior da imagem)
python ferramentas/rostos.py achar <rostos_dir> <trailer> <assinatura.npy>  -> momentos em que o ator aparece
"""
import sys, os, json, subprocess, pathlib
import numpy as np, cv2

M = pathlib.Path(__file__).resolve().parent / "modelos"
DET = cv2.FaceDetectorYN.create(str(M / "face_detection_yunet_2023mar.onnx"), "", (320, 320), 0.7, 0.3, 50)
REC = cv2.FaceRecognizerSF.create(str(M / "face_recognition_sface_2021dec.onnx"), "")
LIMIAR = 0.36  # similaridade de cosseno do SFace (mesma pessoa >= ~0,363)


def rostos(img):
    h, w = img.shape[:2]
    DET.setInputSize((w, h))
    _, f = DET.detect(img)
    out = []
    for r in (f if f is not None else []):
        al = REC.alignCrop(img, r)
        feat = REC.feature(al).flatten()
        out.append({"box": r[:4].tolist(), "score": float(r[14]), "area": float(r[2] * r[3] / (w * h)), "feat": feat})
    return out


def quadros(video, passo=0.5, largura=960):
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", video, "-vf", f"fps=1/{passo},scale={largura}:-2",
                          "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], stdout=subprocess.PIPE)
    h = int(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                            "-of", "csv=p=0", video], capture_output=True, text=True).stdout.split(",")[1].split()[0])
    w0 = int(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width",
                             "-of", "csv=p=0", video], capture_output=True, text=True).stdout.split()[0])
    H = int(round(h * largura / w0 / 2) * 2)
    n = largura * H * 3; k = 0
    while True:
        b = p.stdout.read(n)
        if len(b) < n: break
        yield k * passo, np.frombuffer(b, np.uint8).reshape(H, largura, 3)
        k += 1


def varrer(pasta, saida):
    os.makedirs(saida, exist_ok=True)
    for v in sorted(pathlib.Path(pasta).glob("*.mp4")):
        o = pathlib.Path(saida) / (v.stem + ".npz")
        if o.exists(): continue
        T, B, A, F = [], [], [], []
        for t, img in quadros(str(v)):
            for r in rostos(img):
                if r["score"] < 0.8: continue
                T.append(t); B.append(r["box"]); A.append(r["area"]); F.append(r["feat"])
        np.savez_compressed(o, t=np.array(T), box=np.array(B), area=np.array(A), feat=np.array(F))
        print(v.stem, len(T), "rostos", flush=True)


def assinatura(img_path):
    img = cv2.imread(img_path)
    s = max(1, max(img.shape[:2]) / 1600); img = cv2.resize(img, None, fx=1 / s, fy=1 / s) if s > 1 else img
    rs = rostos(img)
    if not rs: return None
    return max(rs, key=lambda r: r["area"])["feat"]


def cos(a, b): return (a @ b.T) / (np.linalg.norm(a, axis=-1)[:, None] * np.linalg.norm(b, axis=-1)[None, :] + 1e-9)


def achar(npz, assin, limiar=LIMIAR):
    d = np.load(npz)
    if len(d["t"]) == 0: return []
    ref = np.atleast_2d(assin)
    s = cos(d["feat"], ref).max(1)
    ok = s >= limiar
    return [{"t": float(t), "sim": float(x), "area": float(a)} for t, x, a, o in zip(d["t"], s, d["area"], ok) if o]


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "varrer": varrer(sys.argv[2], sys.argv[3])
    elif cmd == "ator":
        f = assinatura(sys.argv[2]); print("rosto:", f is not None)
        if f is not None: np.save(sys.argv[3], f)
    elif cmd == "achar":
        r = achar(os.path.join(sys.argv[2], sys.argv[3] + ".npz"), np.load(sys.argv[4]))
        print(json.dumps(r[:50]))
