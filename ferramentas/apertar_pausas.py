#!/usr/bin/env python3
"""Aperta as pausas sem voz que sobraram DENTRO dos pedacos de uma decupagem (o Whisper estica o fim das
palavras e o modo 'palavras' deixa esse silencio). Usa o mesmo detector de voz do decupar.py.
Regra do canal: pausa entre palavras ate ~0,2 s fica; acima disso corta, deixando folga de voz.
Uso: python3 apertar_pausas.py plano_decupagem.json pasta_decupagem pasta_saida [--preview]
Saida: pasta_saida/decupagem.json + decupado.mp4 (mesmo formato do decupar.py)."""
import json, os, sys, subprocess
AQUI = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(AQUI, "decupar.py")).read().replace("\nmain()", "\n")
dec = {"__file__": os.path.join(AQUI, "decupar.py")}; exec(compile(src, "decupar", "exec"), dec)

PAUSA_MAX = 0.22    # silencio maior que isso dentro do pedaco e cortado
ANTES, DEPOIS = 0.06, 0.12   # folga mantida antes da voz que volta / depois da voz que acaba
BORDA_INI, BORDA_FIM = 0.10, 0.14   # folga nas bordas do pedaco (consoante surda no comeco, fim de palavra soprado)
FPS = 30

plano = json.load(open(sys.argv[1])); D = json.load(open(os.path.join(sys.argv[2], "decupagem.json")))
out = sys.argv[3]; preview = "--preview" in sys.argv
os.makedirs(out, exist_ok=True)
E = {k: dec["envelopes"](v) for k, v in plano["tomadas"].items()}
Q = dec["QUADRO"]
novos, cortado = [], 0.0
for p in D:
    tot, low, lt, ll = E[p["t"]]
    k0, k1 = int(round(p["s"] / Q)), int(round(p["e"] / Q))
    voz = [k < len(low) and low[k] > ll for k in range(k0, k1)]
    # buracos sem voz no MEIO do pedaco (bordas ficam como o decupar.py deixou)
    cortes, ini = [], None
    for i, v in enumerate(voz + [True]):
        if not v and ini is None: ini = i
        if v and ini is not None:
            if ini > 0 and i < len(voz) and (i - ini) * Q > PAUSA_MAX:
                cortes.append(((k0 + ini) * Q + DEPOIS, (k0 + i) * Q - ANTES))
            ini = None
    s, e_fim = p["s"], p["e"]
    # bordas: silencio no comeco/fim do pedaco tambem soma pausa na emenda
    if any(voz):
        v0 = voz.index(True); v1 = len(voz) - 1 - voz[::-1].index(True)
        if v0 * Q > BORDA_INI: s = (k0 + v0) * Q - BORDA_INI
        if (len(voz) - 1 - v1) * Q > BORDA_FIM: e_fim = (k0 + v1 + 1) * Q + BORDA_FIM
    cortes = [(a, b) for a, b in cortes if a > s and b < e_fim]
    cortado += (s - p["s"]) + (p["e"] - e_fim)
    for a, b in cortes:
        if b - a < 0.05: continue
        novos.append({**p, "s": round(s, 4), "e": round(a, 4)}); cortado += b - a; s = b
    novos.append({**p, "s": round(s, 4), "e": round(e_fim, 4)})
for p in novos:
    p["s"] = round(int(p["s"] * FPS + 1e-6) / FPS, 4); p["e"] = round(-(-p["e"] * FPS // 1) / FPS, 4)
novos = [p for p in novos if p["e"] - p["s"] >= 1 / FPS]
for x, y in zip(novos, novos[1:]):
    if x["t"] == y["t"] and x["s"] < y["s"] < x["e"]: y["s"] = x["e"]
novos = [p for p in novos if p["e"] - p["s"] >= 1 / FPS]
t = 0.0
for p in novos:
    p["dst_s"] = round(t, 3); t += p["e"] - p["s"]; p["dst_e"] = round(t, 3)
json.dump(novos, open(os.path.join(out, "decupagem.json"), "w"), ensure_ascii=False, indent=1)
print(f"{len(D)} -> {len(novos)} pedacos, cortou {cortado:.1f} s, duracao {t:.1f} s")
pasta = os.path.join(out, "pedacos"); os.makedirs(pasta, exist_ok=True)
escala = "scale=1280:-2," if preview else ""
lista = []
for i, p in enumerate(novos):
    arq = os.path.join(pasta, f"{i:04d}.mov"); nq = round((p["e"] - p["s"]) * FPS)
    fonte = plano.get("render", plano["tomadas"])[p["t"]]
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", f"{p['s']:.4f}", "-i", fonte,
                    "-t", f"{nq / FPS + 0.1:.4f}", "-vf", f"trim=end_frame={nq},setpts=PTS-STARTPTS,{escala}format=yuv420p",
                    "-af", f"asetpts=PTS-STARTPTS,aresample=48000,apad=whole_dur={nq / FPS:.4f},atrim=end={nq / FPS:.4f},afade=t=in:d=0.015,afade=t=out:st={max(0, nq / FPS - 0.025):.4f}:d=0.025",
                    "-c:v", "libx264", "-preset", "ultrafast" if preview else "fast", "-crf", "20",
                    "-c:a", "pcm_s16le", "-ac", "1", "-ar", "48000", arq], check=True)
    lista.append(f"file '{os.path.abspath(arq)}'")
open(os.path.join(pasta, "lista.txt"), "w").write("\n".join(lista))
subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", os.path.join(pasta, "lista.txt"),
                "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", os.path.join(out, "decupado.mp4")], check=True)
print("ok", os.path.join(out, "decupado.mp4"))
