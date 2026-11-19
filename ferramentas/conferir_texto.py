#!/usr/bin/env python3
"""Confere o TEXTO do corte decupado: compara o que as gravacoes dizem nos pedacos escolhidos
com o que o video decupado diz (as duas transcricoes feitas com prompt de hesitacao, para o Whisper
nao "limpar" repeticoes). Mostra:
  - palavra que SOBROU no corte (repeticao, frase refeita, tropeco),
  - palavra que SUMIU no corte (palavra cortada),
  - frase repetida (mesmas 3+ palavras em sequencia duas vezes seguidas no corte).
Uso: python3 conferir_texto.py plano_decupagem.json pasta_decupagem transcricao_do_corte.json
(no plano, "transcricoes" devem ser as transcricoes verbatim das gravacoes)"""
import difflib, json, os, re, sys, unicodedata

def norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9 ]", " ", s).split()

def mmss(t): return f"{int(t // 60)}:{t % 60:05.2f}"

plano = json.load(open(sys.argv[1])); D = json.load(open(os.path.join(sys.argv[2], "decupagem.json")))
corte = json.load(open(sys.argv[3]))["palavras"]
trans = {k: json.load(open(v))["palavras"] for k, v in plano["transcricoes"].items()}

# texto esperado: palavras das gravacoes cujo MEIO cai num pedaco mantido, na ordem do corte
esperado = []
for p in D:
    for w in trans[p["t"]]:
        m = (w["s"] + w["e"]) / 2
        dentro = min(w["e"], p["e"]) - max(w["s"], p["s"])
        if dentro >= 0.5 * max(w["e"] - w["s"], 0.02):   # metade da palavra ou mais dentro do pedaco
            for tok in norm(w["w"]):
                esperado.append((tok, p["dst_s"] + (m - p["s"]), p["t"], m))
obtido = [(tok, (w["s"] + w["e"]) / 2) for w in corte for tok in norm(w["w"])]

sm = difflib.SequenceMatcher(None, [x[0] for x in esperado], [x[0] for x in obtido], autojunk=False)
prob = 0
for op, i1, i2, j1, j2 in sm.get_opcodes():
    if op == "equal": continue
    a = " ".join(x[0] for x in esperado[i1:i2]); b = " ".join(x[0] for x in obtido[j1:j2])
    t = obtido[j1][1] if j1 < len(obtido) else esperado[i1][1]
    # trocas de grafia do Whisper (nolan/nola, tenet/tannet) com o mesmo tamanho nao contam
    if op == "replace" and i2 - i1 == j2 - j1 and all(difflib.SequenceMatcher(None, x[0], y[0]).ratio() > 0.6
                                                        for x, y in zip(esperado[i1:i2], obtido[j1:j2])):
        continue
    prob += 1
    tipo = {"insert": "SOBROU", "delete": "SUMIU", "replace": "TROCOU"}[op]
    print(f"{mmss(t)}  {tipo}: esperado '{a}' | no corte '{b}'")

# repeticao dentro do proprio corte: n-grama (3 a 6 palavras) repetido logo em seguida
toks = [x[0] for x in obtido]
for n in range(6, 2, -1):
    for i in range(len(toks) - 2 * n + 1):
        if toks[i:i + n] == toks[i + n:i + 2 * n]:
            prob += 1; print(f"{mmss(obtido[i][1])}  REPETIU: '{' '.join(toks[i:i + n])}' duas vezes seguidas")
print("problemas:", prob)
