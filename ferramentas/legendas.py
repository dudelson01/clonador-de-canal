"""Agrupa as palavras da timeline.json em legendas curtas (até N palavras, quebra na pontuação).

Uso como módulo: grupos(palavras, ini, fim, max_palavras=4, correcoes={})
"""
import re

PONT = re.compile(r"[.,!?;:…]$")


def limpa(w, correcoes):
    w = correcoes.get(w.strip(".,;:…"), w) if w.strip(".,;:…") in correcoes else w
    w = w.lstrip("-")
    # sem pontuação na legenda, menos ? e !
    w = re.sub(r"[.,;:…]+$", "", w)
    return w


def grupos(palavras, ini=0, fim=1e9, max_palavras=4, correcoes=None, max_dur=2.4):
    """Quebra em frases (pontuação ou pausa), depois divide cada frase em pedaços equilibrados."""
    import math
    correcoes = correcoes or {}
    ps = [p for p in palavras if p["s"] >= ini - 0.01 and p["s"] < fim]
    frases, atual = [], []
    for i, p in enumerate(ps):
        atual.append(p)
        if PONT.search(p["w"]) or i == len(ps) - 1 or ps[i + 1]["s"] - p["e"] > 0.35:
            frases.append(atual); atual = []
    out = []
    for f in frases:
        n = max(math.ceil(len(f) / max_palavras), math.ceil((f[-1]["e"] - f[0]["s"]) / max_dur))
        n = min(n, len(f)); tam = len(f) / n
        for k in range(n):
            out.append(f[round(k * tam):round((k + 1) * tam)])
    res = []
    for j, g in enumerate(out):
        ini_g = g[0]["s"] - 0.05
        prox = out[j + 1][0]["s"] - 0.05 if j + 1 < len(out) else g[-1]["e"] + 0.4
        fim_g = min(prox, g[-1]["e"] + 0.6)
        res.append({"ini": round(ini_g, 3), "fim": round(fim_g, 3),
                    "palavras": [{"w": limpa(p["w"], correcoes), "s": p["s"], "e": p["e"]} for p in g]})
    return res
