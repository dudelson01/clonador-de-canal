"""Gera plano-<lang>.json (cenas com início/fim reais) a partir de cenas-blocos.json, do roteiro e da timeline do idioma.
Uso: python plano_idioma.py en|es|pt
"""
import json, re, subprocess, sys

L = sys.argv[1]


def blocos(md):
    corpo = md.split("\n---\n", 1)[1]; corpo = re.split(r"\n---\n", corpo)[0]
    out = []
    for ci, bl in enumerate(re.split(r"^## ", corpo, flags=re.M)[1:]):
        _, _, txt = bl.partition("\n")
        for par in [p.strip() for p in txt.split("\n\n") if p.strip()]:
            fala = " ".join(l for l in par.splitlines() if not l.startswith("["))
            fala = re.sub(r"\{F\d+\}", "", fala).strip()
            if fala:
                out.append({"cap": ci, "n": len(fala.split())})
    return out


bs = blocos(open(f"roteiro-{L}.md", encoding="utf-8").read())
plano_b = json.load(open("cenas-blocos.json", encoding="utf-8"))
assert len(bs) == len(plano_b), (len(bs), len(plano_b))
sec = json.load(open(f"narracao-{L}.wav.secoes.json", encoding="utf-8"))
tl = json.load(open(f"timeline-{L}.json", encoding="utf-8"))
dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f"narracao-{L}.wav"]))

# início de cada bloco: fração de palavras dentro do capítulo -> palavra correspondente na timeline
inicios = []
for k, b in enumerate(bs):
    cap = sec["capitulos"][b["cap"]]
    mesmos = [x for x in bs if x["cap"] == b["cap"]]
    antes = sum(x["n"] for x in bs[:k] if x["cap"] == b["cap"])
    frac = antes / sum(x["n"] for x in mesmos)
    ws = [w for w in tl if cap["inicio"] - 0.2 <= w["i"] < cap["fim"] + 0.2]
    t = cap["inicio"] if frac == 0 or not ws else ws[min(len(ws) - 1, round(frac * len(ws)))]["i"]
    inicios.append(max(0.0, t - 0.15))
inicios[0] = 0.0

cenas = []
for k, itens in enumerate(plano_b):
    a = inicios[k]; z = inicios[k + 1] if k + 1 < len(inicios) else dur
    tot = sum(i["peso"] for i in itens); t = a
    for i in itens:
        d = (z - a) * i["peso"] / tot
        textos = [dict(x, t=x["t"][L]) for x in i["textos"]]
        cenas.append({"id": i["id"], "img": f"midia/img/{i['img']}.webp", "ini": round(t, 2), "fim": round(t + d, 2), "mov": i["mov"], "textos": textos})
        t += d
cenas[-1]["fim"] = round(dur, 2)
# cenas longas (> 9 s): divide em enquadramentos da mesma imagem (aberto -> close), mantendo ~6-7 s por corte
div = []
for c in cenas:
    d = c["fim"] - c["ini"]; n = max(1, round(d / 6.5)) if d > 9 else 1
    for j in range(n):
        p2 = dict(c, ini=round(c["ini"] + d * j / n, 2), fim=round(c["ini"] + d * (j + 1) / n, 2))
        if j % 2 == 1:
            p2.update(mov="close", id=c["id"] + f"_{j}", textos=[])  # no close o texto do caderno sairia cortado
        elif j > 0:
            p2.update(id=c["id"] + f"_{j}")
        div.append(p2)
cenas = div
json.dump(cenas, open(f"plano-{L}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
ds = [c["fim"] - c["ini"] for c in cenas]
print(f"{L}: {len(cenas)} cenas | {dur/60:.1f} min | por cena: média {sum(ds)/len(ds):.1f}s, mín {min(ds):.1f}s, máx {max(ds):.1f}s")
