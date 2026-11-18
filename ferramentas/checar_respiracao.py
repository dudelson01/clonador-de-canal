#!/usr/bin/env python3
"""Procura no corte decupado trechos SEM FALA que sobraram (respiracao, estalo de boca, rosto parado),
medindo no audio ORIGINAL de cada gravacao (mesmo criterio de voz do decupar.py).
Regra do canal: nada disso acima de ~0,15 s. Consoante surda ("s", "x", "t") colada na palavra e normal (ate ~0,12 s).
Uso: python3 checar_respiracao.py plano_decupagem.json pasta_decupagem [limite_s=0.15]"""
import json, os, sys
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "decupar.py")).read().replace("\nmain()", "\n")
dec = {}; exec(compile(src, "decupar", "exec"), dec)
plano = json.load(open(sys.argv[1])); D = json.load(open(os.path.join(sys.argv[2], "decupagem.json")))
LIM = float(sys.argv[3]) if len(sys.argv) > 3 else 0.15
E = {k: dec["envelopes"](v) for k, v in plano["tomadas"].items()}
Q = dec["QUADRO"]
# linha do tempo do corte: para cada quadro de 10 ms do video final, se tem voz (no original)
voz = []
for p in D:
    tot, low, lt, ll = E[p["t"]]
    for k in range(int(round(p["s"] / Q)), int(round(p["e"] / Q))):
        voz.append(k < len(low) and low[k] > ll)
runs, ini = [], None
for k, v in enumerate(voz + [True]):
    if not v and ini is None: ini = k
    if v and ini is not None: runs.append((ini, k)); ini = None
susp = []
for a, b in runs:
    dur = (b - a) * Q; livre = dur - (0.12 if a > 0 else 0) - (0.12 if b < len(voz) else 0)
    if livre > LIM: susp.append((a * Q, dur, livre))
print(f"trechos sem fala acima de {LIM:.2f} s (descontando consoantes): {len(susp)} | total {sum(s[2] for s in susp):.1f} s de {len(voz)*Q:.0f} s")
for t, d, l in sorted(susp, key=lambda x: -x[2])[:25]:
    print(f"  {int(t//60)}:{t%60:05.2f}  sem voz por {d:.2f} s (~{l:.2f} s alem das consoantes)")
