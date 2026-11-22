"""Troca cenas ruins de um plano (por índice) por outras do mesmo filme, ainda não usadas e não bloqueadas.
Uso: python ferramentas/trocar_cenas.py <plano.json> <indice_cenas.json> <bloqueadas.json> i1 i2 ...
As cenas trocadas entram na lista de bloqueadas. Em 'bebe-de-rosemary' só aceita cena com rosto."""
import json, sys
plano, indice, bloq = sys.argv[1:4]; ruins = [int(x) for x in sys.argv[4:]]
c = json.load(open(plano)); idx = json.load(open(indice)); bl = {tuple(x) for x in json.load(open(bloq))}
for i in ruins:
    if c[i].get("_filme"): bl.add((c[i]["_filme"], c[i]["_cena"]))
usados = {(x.get("_filme"), x.get("_cena")) for x in c}
for i in ruins:
    f = c[i].get("_filme"); d = c[i]["dur"]
    if not f: continue
    cand = [(j, s) for j, s in enumerate(idx[f]) if (f, j) not in bl and (f, j) not in usados and not s["cartela"]
            and s["brilho"] >= 35 and s["fim"] - s["ini"] - 0.25 >= d * 0.5 and (f != "bebe-de-rosemary-1968" or s["rosto"] > 0)]
    cand.sort(key=lambda x: -x[1]["rosto"])
    if not cand:
        # reaproveita outra cena boa do mesmo filme já usada, espelhada
        boas = [x for x in c if x.get("_filme") == f and (f, x.get("_cena")) not in bl]
        if boas:
            n = dict(boas[i % len(boas)]); n.update({"dur": d, "espelhar": True, "ss": round(n["ss"] + 0.4, 3)}); c[i] = n
            print(i, "-> espelho de", n["_cena"]); continue
        c[i] = {"src": "ARTE", "ss": 0, "dur": d}; print(i, "-> ARTE"); continue
    j, s = cand[0]; disp = s["fim"] - s["ini"] - 0.25
    c[i].update({"ss": round(s["ini"] + 0.12, 3), "vel": 1.0 if disp >= d else round(max(0.5, disp / d) - 0.01, 3), "_cena": j})
    usados.add((f, j)); print(i, "->", f, j)
json.dump(c, open(plano, "w"), indent=0); json.dump([list(x) for x in bl], open(bloq, "w"))
