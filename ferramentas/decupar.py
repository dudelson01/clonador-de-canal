"""Aplica uma decupagem (lista de trechos) numa gravação: corta voz e vídeo juntos, sem cortar palavras.

Uso: python ferramentas/decupar.py <gravacao.mp4> <transcricao.json> <decupagem.py> <pasta_saida> [--preview]
Saída: voz.wav (48 kHz, limpa), rosto.mp4 (vídeo sem áudio, 30 fps), cortes.json (origem -> nova linha do tempo).
"""
import json, sys, pathlib, subprocess, importlib.util
import numpy as np

grav, trans, dec, out = sys.argv[1:5]; prev = "--preview" in sys.argv
out = pathlib.Path(out); out.mkdir(parents=True, exist_ok=True)
pal = json.load(open(trans))["palavras"]
spec = importlib.util.spec_from_file_location("d", dec); d = importlib.util.module_from_spec(spec); spec.loader.exec_module(d)

SR = 16000
pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", grav, "-vn", "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"],
                     capture_output=True, check=True).stdout
a = np.frombuffer(pcm, np.int16).astype(np.float32) / 32768
H = SR // 100  # 10 ms
rms = np.array([20 * np.log10(np.sqrt(np.mean(a[i:i + H] ** 2)) + 1e-9) for i in range(0, len(a) - H, H)])
piso = np.percentile(rms, 10)
LIM = max(piso + 12, -48)


def palavra_em(t):
    return min(range(len(pal)), key=lambda i: abs(pal[i]["s"] - t))


def silencio(t, dur=0.05):
    i = int(t * 100); n = max(1, int(dur * 100))
    return np.all(rms[max(0, i):i + n] < LIM)


cortes, t_novo = [], 0.0
for tr in d.TRECHOS:
    bloco, ini, ult, cam, nota = tr[:5]
    if len(tr) > 5 and tr[5]:
        cortes.append({"bloco": bloco, "cam": cam, "nota": nota, "src_s": ini, "src_e": ult,
                       "ini": round(t_novo, 3), "fim": round(t_novo + ult - ini, 3)})
        t_novo += ult - ini; continue
    i0, i1 = palavra_em(ini), palavra_em(ult)
    s, e = pal[i0]["s"], pal[i1]["e"]
    ant = pal[i0 - 1]["e"] if i0 > 0 else 0.0
    prox = pal[i1 + 1]["s"] if i1 + 1 < len(pal) else e + 1.0
    # início: volta até achar silêncio (máx 0,3 s), sem invadir a palavra anterior
    t = s
    while t > s - 0.30 and t > ant + 0.03 and not silencio(t - 0.04, 0.04): t -= 0.01
    s2 = max(t - 0.04, ant + 0.02, 0)
    # fim: avança até o silêncio (máx 0,5 s), sem invadir a próxima palavra
    t = e
    while t < e + 0.50 and t < prox - 0.03 and not silencio(t, 0.06): t += 0.01
    e2 = min(t + 0.08, prox - 0.02)
    cortes.append({"bloco": bloco, "cam": cam, "nota": nota, "src_s": round(s2, 3), "src_e": round(e2, 3),
                   "ini": round(t_novo, 3), "fim": round(t_novo + e2 - s2, 3)})
    t_novo += e2 - s2
# corta silêncios longos DENTRO de cada trecho (rosto parado sem falar): pausa > 0,35 s vira 0,2 s
PAUSA, RESPIRO = 0.35, 0.10
novos = []
for c in cortes:
    if "[pausa]" in c["nota"] or "[inteiro]" in c["nota"]:  # pausa de efeito / frase inteira: não mexe
        novos.append(c); continue
    i0, i1 = int(c["src_s"] * 100), int(c["src_e"] * 100)
    sil = rms[i0:i1] < LIM
    partes, ini, k = [], c["src_s"], 0
    while k < len(sil):
        if sil[k]:
            j = k
            while j < len(sil) and sil[j]: j += 1
            a_, b_ = c["src_s"] + k / 100, c["src_s"] + j / 100
            if b_ - a_ >= PAUSA and k > 0 and j < len(sil):
                partes.append((ini, a_ + RESPIRO)); ini = b_ - RESPIRO
            k = j
        else:
            k += 1
    partes.append((ini, c["src_e"]))
    for s_, e_ in partes:
        # apara silêncio nas bordas: deixa 0,08 s antes da fala e 0,14 s depois
        a_, b_ = int(s_ * 100), int(e_ * 100)
        while a_ < b_ and rms[a_] < LIM: a_ += 1
        while b_ > a_ and rms[b_ - 1] < LIM: b_ -= 1
        s_, e_ = max(s_, a_ / 100 - 0.08), min(e_, b_ / 100 + 0.14)
        if e_ - s_ > 0.12: novos.append({**c, "src_s": round(s_, 3), "src_e": round(e_, 3)})
print(len(cortes), "trechos ->", len(novos), "depois de tirar as pausas")
cortes = novos
# alinha cada corte à grade de quadros (1/30 s) para voz e boca ficarem sincronizadas
Q = 1 / 30; t_novo = 0.0
for c in cortes:
    c["src_s"] = round(round(c["src_s"] / Q) * Q, 4); c["src_e"] = round(round(c["src_e"] / Q) * Q, 4)
    c["ini"] = round(t_novo, 4); t_novo += c["src_e"] - c["src_s"]; c["fim"] = round(t_novo, 4)
json.dump(cortes, open(out / "cortes.json", "w"), ensure_ascii=False, indent=0)
print(len(cortes), "trechos ->", round(t_novo / 60, 2), "min")

# áudio: cada trecho com fade de 12 ms; limpeza leve (graves, ruído, de-esser suave)
fa, fv = [], []
for k, c in enumerate(cortes):
    du = c["src_e"] - c["src_s"]
    fa.append(f"[0:a]atrim={c['src_s']}:{c['src_e']},asetpts=PTS-STARTPTS,afade=t=in:d=0.012,"
              f"afade=t=out:st={max(0, du - 0.012):.3f}:d=0.012[a{k}]")
    fv.append(f"[0:v]trim={c['src_s']}:{c['src_e']},setpts=PTS-STARTPTS[v{k}]")
n = len(cortes)
fc_a = ";".join(fa) + ";" + "".join(f"[a{k}]" for k in range(n)) + f"concat=n={n}:v=0:a=1," \
       "highpass=f=75,afftdn=nr=8:nf=-45,equalizer=f=6500:t=q:w=2:g=-2,aresample=48000[A]"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", grav, "-filter_complex", fc_a, "-map", "[A]", "-ac", "1",
                str(out / "voz.wav")], check=True)
print("voz ok")
if "--so-voz" in sys.argv: sys.exit(0)
# vídeo: um trecho por vez (pouca memória), depois junta sem reencodar
from concurrent.futures import ThreadPoolExecutor
tmp = out / "trechos"; tmp.mkdir(exist_ok=True)
esc = ["-vf", "scale=960:540"] if prev else []
def um(kc):
    k, c = kc; o = tmp / f"t{k:03d}.mp4"
    nq = round((c["src_e"] - c["src_s"]) * 30)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{c['src_s']:.4f}", "-i", grav, "-frames:v", str(nq),
                    "-an", *esc, "-r", "30", "-c:v", "libx264", "-preset", "veryfast" if prev else "medium", "-crf", "17",
                    "-pix_fmt", "yuv420p", str(o)], check=True)
    return o
with ThreadPoolExecutor(2) as ex:
    arqs = list(ex.map(um, enumerate(cortes)))
(tmp / "l.txt").write_text("\n".join(f"file '{x.resolve()}'" for x in arqs))
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(tmp / "l.txt"), "-c", "copy",
                str(out / "rosto.mp4")], check=True)
print("rosto ok")
