#!/usr/bin/env python3
"""Decupagem de gravacao com rosto: monta o corte a partir de uma lista de trechos escolhidos.
Uso: python3 decupar.py plano_decupagem.json saida_dir [--preview]
plano_decupagem.json:
{ "tomadas": {"1": "bruto/gravacao1.mp4", "2": "bruto/gravacao2.mp4"},
  "transcricoes": {"1": "build/gravacao1.json", "2": "build/gravacao2.json"},
  "trechos": [ {"t": "1", "de": "durante quase", "ate": "nao era", "perto": 5, "bloco": "gancho", "obs": "..."}, ... ] }
- "de"/"ate": primeiras/ultimas palavras do trecho (sem acento/pontuacao tanto faz), procuradas perto de "perto" (s).
- Ou "ini"/"fim" em segundos, quando a transcricao falhou.
Cada trecho vira pedacos cortando pausas internas > PAUSA_MAX (deixa PAUSA_RESTO).
Saidas: decupagem.json (pedacos com tempos de origem e de destino), decupado.mp4, cortes.txt."""
import json, os, re, subprocess, sys, unicodedata

PAD_INI, PAD_FIM = 0.08, 0.18      # folga antes da 1a palavra / depois da ultima
PAUSA_MAX, PAUSA_RESTO = 0.55, 0.28  # pausa interna maior que isso e encurtada

def norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9 ]", " ", s).split()

def acha(palavras, frase, perto, depois_de=None, janela=40):
    alvo = norm(frase)
    toks = [norm(w["w"]) for w in palavras]
    flat = [(i, t) for i, ts in enumerate(toks) for t in ts]
    cands = []
    for k in range(len(flat) - len(alvo) + 1):
        if [t for _, t in flat[k:k + len(alvo)]] == alvo:
            i0, i1 = flat[k][0], flat[k + len(alvo) - 1][0]
            if depois_de is not None and i0 < depois_de: continue
            if abs(palavras[i0]["s"] - perto) <= janela: cands.append((abs(palavras[i0]["s"] - perto), i0, i1))
    if not cands: return None
    return sorted(cands)[0][1:]

def main():
    plano = json.load(open(sys.argv[1])); out = sys.argv[2]; preview = "--preview" in sys.argv
    os.makedirs(out, exist_ok=True)
    trans = {k: json.load(open(v))["palavras"] for k, v in plano["transcricoes"].items()}
    pedacos, erros = [], []
    for n, tr in enumerate(plano["trechos"]):
        P = trans[tr["t"]]
        if tr.get("exato"):  # tempos exatos, sem ajuste (para cortes dentro de uma palavra mal transcrita)
            pedacos.append({"t": tr["t"], "s": tr["ini"], "e": tr["fim"], "n": n, "bloco": tr.get("bloco", ""), "texto": tr.get("obs", "")}); continue
        if "ini" in tr:
            ws = [w for w in P if w["s"] >= tr["ini"] - 0.05 and w["e"] <= tr["fim"] + 0.05]
            if not ws:
                pedacos.append({"t": tr["t"], "s": tr["ini"], "e": tr["fim"], "n": n, "bloco": tr.get("bloco", "")}); continue
            i0, i1 = P.index(ws[0]), P.index(ws[-1])
        else:
            a = acha(P, tr["de"], tr["perto"])
            if not a: erros.append(f"#{n} nao achei inicio '{tr['de']}' perto de {tr['perto']}s (tomada {tr['t']})"); continue
            b = acha(P, tr["ate"], P[a[0]]["s"] + 5, depois_de=a[0], janela=60)
            if not b: erros.append(f"#{n} nao achei fim '{tr['ate']}' (tomada {tr['t']})"); continue
            i0, i1 = a[0], b[1]
        ws = P[i0:i1 + 1]
        ini = max(0, ws[0]["s"] - PAD_INI) if i0 == 0 or P[i0 - 1]["e"] < ws[0]["s"] - PAD_INI else (P[i0 - 1]["e"] + ws[0]["s"]) / 2
        fim_lim = P[i1 + 1]["s"] if i1 + 1 < len(P) else ws[-1]["e"] + 1
        fim = min(ws[-1]["e"] + PAD_FIM, (ws[-1]["e"] + fim_lim) / 2 if fim_lim - ws[-1]["e"] < 2 * PAD_FIM else ws[-1]["e"] + PAD_FIM)
        # divide nas pausas internas longas
        s = ini
        for a_, b_ in zip(ws, ws[1:]):
            gap = b_["s"] - a_["e"]
            if gap > PAUSA_MAX:
                pedacos.append({"t": tr["t"], "s": round(s, 3), "e": round(a_["e"] + PAUSA_RESTO / 2, 3), "n": n, "bloco": tr.get("bloco", "")})
                s = b_["s"] - PAUSA_RESTO / 2
        pedacos.append({"t": tr["t"], "s": round(s, 3), "e": round(fim, 3), "n": n, "bloco": tr.get("bloco", ""),
                        "texto": " ".join(w["w"] for w in ws)})
    if erros:
        print("\n".join(erros)); sys.exit(1)
    # tempos no video final
    t = 0.0
    for p in pedacos:
        p["dst_s"] = round(t, 3); t += p["e"] - p["s"]; p["dst_e"] = round(t, 3)
    json.dump(pedacos, open(os.path.join(out, "decupagem.json"), "w"), ensure_ascii=False, indent=1)
    with open(os.path.join(out, "cortes.txt"), "w") as f:
        for n, tr in enumerate(plano["trechos"]):
            ps = [p for p in pedacos if p["n"] == n]
            txt = next((p.get("texto") for p in ps if p.get("texto")), "")
            f.write(f"{ps[0]['dst_s']:7.2f}s  [grav. {tr['t']} {ps[0]['s']:.1f}-{ps[-1]['e']:.1f}s] {tr.get('bloco','')}: {txt}\n")
    print(f"{len(plano['trechos'])} trechos -> {len(pedacos)} pedacos, duracao {t:.1f}s")
    # render: cada pedaco re-encodado (corte exato) + concat
    pasta = os.path.join(out, "pedacos"); os.makedirs(pasta, exist_ok=True)
    escala = "scale=1280:-2," if preview else ""
    lista = []
    for i, p in enumerate(pedacos):
        arq = os.path.join(pasta, f"{i:04d}.mp4"); d = p["e"] - p["s"]
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", f"{p['s']:.3f}", "-i", plano["tomadas"][p["t"]],
                        "-t", f"{d:.3f}", "-vf", f"{escala}fps=30,format=yuv420p",
                        "-af", f"aresample=48000,afade=t=in:d=0.012,afade=t=out:st={max(0, d - 0.015):.3f}:d=0.015",
                        "-c:v", "libx264", "-preset", "ultrafast" if preview else "fast", "-crf", "20",
                        "-c:a", "pcm_s16le", "-ac", "1", "-ar", "48000", arq.replace(".mp4", ".mov")], check=True)
        lista.append(f"file '{os.path.abspath(arq.replace('.mp4', '.mov'))}'")
    open(os.path.join(pasta, "lista.txt"), "w").write("\n".join(lista))
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", os.path.join(pasta, "lista.txt"),
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", os.path.join(out, "decupado.mp4")], check=True)
    print("ok", os.path.join(out, "decupado.mp4"))

main()
