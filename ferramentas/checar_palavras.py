#!/usr/bin/env python3
"""Confere se a decupagem cortou SOM de alguma palavra: para cada palavra dos trechos escolhidos (tempo do Whisper),
pega os quadros de 10 ms com som (acima do piso de ruido) e mede quantos ficaram nos pedacos mantidos.
Lista as palavras que perderam mais de 60 ms de voz. Uso: python3 checar_palavras.py plano.json pasta_decupagem"""
import json, sys, os
sys.argv_bak = sys.argv; sys.argv = [sys.argv[0], "x", "x"]
import importlib.util
spec = importlib.util.spec_from_file_location("dec", os.path.join(os.path.dirname(__file__), "decupar.py"))
src = open(spec.origin).read().replace("\nmain()", "\n")
dec = {"__file__": os.path.join(os.path.dirname(os.path.abspath(__file__)), "decupar.py")}; exec(compile(src, "decupar", "exec"), dec)
sys.argv = sys.argv_bak
plano = json.load(open(sys.argv[1])); D = json.load(open(os.path.join(sys.argv[2], "decupagem.json")))
trans = {k: json.load(open(v))["palavras"] for k, v in plano["transcricoes"].items()}
E = {k: dec["envelopes"](v) for k, v in plano["tomadas"].items()}
# usa o grave BRUTO (sem filtro de tom): pega tambem voz soprada/rouca perdida
E = {k: (e[0], dec["BRUTO"][plano["tomadas"][k]], e[2], e[3]) for k, e in E.items()}
Q = dec["QUADRO"]; ruins = 0
for n in sorted(set(p["n"] for p in D)):
    ps = [p for p in D if p["n"] == n]; t = ps[0]["t"]; tot, low, lt, ll = E[t]
    lo, hi = min(p["s"] for p in ps), max(p["e"] for p in ps)
    for w in trans[t]:
        if w["e"] < lo + 0.02 or w["s"] > hi - 0.02: continue
        frames = [k for k in range(int(w["s"] / Q), int(w["e"] / Q)) if k < len(tot) and low[k] > ll]  # so VOZ (vibracao)
        perd = [k for k in frames if not any(p["s"] <= k * Q + Q / 2 <= p["e"] for p in ps)]
        if len(perd) * Q >= 0.03:
            ruins += 1; print(f"trecho {n} grav {t} '{w['w']}' {w['s']:.2f}-{w['e']:.2f}: perdeu {len(perd)*Q*1000:.0f} ms de voz (de {len(frames)*Q*1000:.0f})")
print("palavras suspeitas:", ruins)
