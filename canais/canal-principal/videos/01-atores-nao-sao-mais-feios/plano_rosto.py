"""Versão HÍBRIDA com o rosto do aluno (voz dele, gravação decupada).

python plano_rosto.py --timeline   -> transcreve build/rosto/voz.wav (tempo de cada palavra)
python plano_rosto.py --plano      -> cenas (rosto nas piadas, trailers nos exemplos) + destaques remapeados
python plano_rosto.py --artes      -> renderiza artes (2 pedaços)
python plano_rosto.py --som        -> música por parte + efeitos + voz (-14 LUFS)
python plano_rosto.py --video      -> monta tudo em out/video-rosto.mp4
"""
import json, re, sys, os, subprocess, difflib, pathlib
sys.path.insert(0, "ferramentas")
V = "canais/canal-principal/videos/01-atores-nao-sao-mais-feios/"
R = V + "build/rosto/"
A = sys.argv


def norm(w): return re.sub(r"[^\wà-ú]", "", w.lower())


if "--timeline" in A:
    subprocess.run(["python3", "ferramentas/transcrever.py", R + "voz.wav", R + "timeline.json"], check=True)

CORTES = json.load(open(R + "cortes.json"))
TL = json.load(open(R + "timeline.json"))
PAL = TL["palavras"]
FIM = CORTES[-1]["fim"] + 1.0
ROSTO = R + "rosto.mp4"


def em(palavra, depois=0.0, ate=None):
    p = norm(palavra)
    for w in PAL:
        if w["s"] >= depois - 0.05 and norm(w["w"]).startswith(p) and (ate is None or w["s"] <= ate):
            return round(w["s"], 3)
    raise ValueError(f"palavra não achada: {palavra} depois de {depois}")


# ---------- mapa tempo antigo (narração IA) -> tempo novo (voz do aluno) ----------
VELHO = json.load(open(V + "timeline.json"))["palavras"]
a_ = [norm(w["w"]) for w in VELHO]; b_ = [norm(w["w"]) for w in PAL]
sm = difflib.SequenceMatcher(None, a_, b_, autojunk=False)
PARES = []
for blk in sm.get_matching_blocks():
    for k in range(blk.size):
        PARES.append((VELHO[blk.a + k]["s"], PAL[blk.b + k]["s"]))


def novo(t):
    """Converte um tempo da narração antiga no tempo correspondente da gravação nova."""
    import bisect
    xs = [p[0] for p in PARES]
    i = bisect.bisect_left(xs, t)
    if i == 0: return PARES[0][1] + (t - PARES[0][0])
    if i >= len(PARES): return PARES[-1][1] + (t - PARES[-1][0])
    (x0, y0), (x1, y1) = PARES[i - 1], PARES[i]
    if x1 - x0 > 4:  # lacuna grande (texto diferente): usa o vizinho mais próximo
        return y0 + (t - x0) if t - x0 < x1 - t else y1 - (x1 - t)
    return y0 + (t - x0) * (y1 - y0) / max(1e-6, x1 - x0)


# ---------- cenas: rosto nos trechos "cam", trailers no resto ----------
M = ["twisters-2024", "the-batman-2022", "deadpool-wolverine-2024", "homem-aranha-2021", "creed-2015", "chalamet-a-complete-unknown"]
O = ["rocky-1976", "taxi-driver-1976", "poderoso-chefao-1972", "era-uma-vez-no-oeste-1968", "ghostbusters-1984",
     "batman-1989", "star-wars-1977", "tres-homens-em-conflito-1966", "homem-aranha-2002", "x-men-2000"]
POOL = [  # (pedaço da nota do trecho, filmes, opções)
 ("33 anos quando", ["ghostbusters-1984"], {}), ("Agora olha o Glenn", ["twisters-2024"], {}),
 ("O que eu quero", O, {}), ("sem nutricionista", O, {}), ("sem cirurgião", O, {}),
 ("Hoje os atores", M, {}), ("Eles não parecem", M, {}), ("Claro, não é todo", M, {"efeito": "lavado"}),
 ("As pessoas fumam", O + M, {}), ("Stallone tinha 29", ["rocky-1976"], {}),
 ("Vamos comparar", ["die-hard-1988", "twisters-2024"], {}), ("O Bruce já", ["die-hard-1988"], {}),
 ("Agora Batman", ["batman-1989", "the-batman-2022"], {}), ("O Keaton", ["batman-1989"], {}),
 ("O Pattinson", ["the-batman-2022"], {}), ("Antes tinha ator", O, {}),
 ("Olha a abertura", ["era-uma-vez-no-oeste-1968"], {}), ("Três pistoleiros", ["era-uma-vez-no-oeste-1968"], {}),
 ("Um tem cabelo", ["era-uma-vez-no-oeste-1968"], {}), ("Quase 15", ["era-uma-vez-no-oeste-1968"], {}),
 ("Mesma coisa com O Poderoso", ["poderoso-chefao-1972"], {}), ("Kurt Russell", ["fuga-de-nova-york-1981", "rocky-1976"], {}),
 ("Hugh Jackman", ["x-men-2000", "deadpool-wolverine-2024"], {}), ("Cidade de Deus", ["cidade-de-deus-2002"], {}),
 ("você acredita", ["cidade-de-deus-2002"], {}), ("Olha a Mia", ["bebe-de-rosemary-1968"], {"alvo": 2.6}),
 ("rosto comum da Mia", ["bebe-de-rosemary-1968"], {"alvo": 2.6}), ("Star Wars", ["star-wars-1977"], {}),
 ("Taxi Driver", ["taxi-driver-1976"], {}), ("parecem que pertencem", ["taxi-driver-1976"], {}),
 ("No fim de Rocky", ["rocky-1976"], {}), ("Em", ["creed-2015"], {}), ("Creed,", ["creed-2015"], {}),
 ("depois da luta", ["creed-2015"], {}), ("Homem-Aranha de 2002", ["homem-aranha-2002"], {}),
 ("A máscara rasgada", ["homem-aranha-2002"], {}), ("Tom Holland", ["homem-aranha-2021"], {}),
 ("Três Homens", ["tres-homens-em-conflito-1966"], {}), ("Em 2021", "ARTE", {}), ("A ideia dela", M, {}),
 ("Para ator", M, {}), ("O público", M, {"efeito": "escurece"}), ("É chato demais", M, {"efeito": "escurece"}),
 ("Teve uma pessoa", ["invasores-de-corpos-1978"], {}), ("Nós não temos", M, {}),
 ("apelido na gringa", ["chalamet-a-complete-unknown", "twisters-2024", "the-batman-2022"], {}),
 ("Isso não é só", M + ["era-uma-vez-no-oeste-1968", "ghostbusters-1984"], {}),
 ("Rocky ensanguentado", ["rocky-1976", "tres-homens-em-conflito-1966", "taxi-driver-1976", "era-uma-vez-no-oeste-1968"], {"alvo": 1.6}),
]


def pool_de(nota):
    for chave, filmes, op in POOL:
        if (nota == chave) if len(chave) <= 6 else (nota.startswith(chave) or chave in nota[:40]):
            return filmes, op
    return O, {}


def cenas_rosto(c):
    """Rosto em tela cheia; trechos longos ganham 'pulos de zoom' a cada frase (~3 s)."""
    dur = c["fim"] - c["ini"]
    n = max(1, round(dur / 3.2)); d = dur / n; out = []
    for k in range(n):
        out.append({"src": ROSTO, "ss": round(c["ini"] + k * d, 4), "dur": round(d, 4), "vel": 1.0,
                    "z0": [1.0, 1.14, 1.06][k % 3], "zoom": 0.03, "sem_vinheta": True, "_rosto": True})
    return out


# ---------- destaques: os do vídeo aprovado, remapeados + novos para os improvisos ----------
def destaques():
    sys.argv = ["x"]
    import importlib.util
    sp = importlib.util.spec_from_file_location("pc", V + "plano_completo.py"); pc = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(pc)
    old = pc.destaques()
    sg = json.load(open(V + "build/spec_gancho.json"))["elementos"]
    tira = {"ROSTO CONFIDENCIAL", "CALMA!"}  # agora o rosto aparece; "Calma" vira o rosto mesmo
    out = []
    for e in sg + old:
        if e.get("texto") in tira: continue
        n = dict(e); n["ini"] = round(novo(e["ini"]), 3); n["fim"] = round(max(n["ini"] + 0.6, novo(e["fim"])), 3)
        if "itens" in n: n["itens"] = [{**it, "s": round(novo(it["s"]), 3)} for it in n["itens"]]
        if "linhas" in n: n["linhas"] = [{**l, "s": round(novo(l["s"]), 3)} for l in n["linhas"]]
        if n["tipo"] == "insc": n["clique"] = round(em("inscreve", n["ini"] - 1) - n["ini"] + 0.2, 3)
        out.append(n)
    E = lambda tipo, ini, fim, **k: {"tipo": tipo, "ini": round(ini, 3), "fim": round(fim, 3), **k}
    # abertura: a gravação começa em "33 anos" -> etiqueta com o nome dele
    out = [x for x in out if not (x["tipo"] == "numero" and x["ini"] < 3)]
    out += [E("etq", 0.0, 2.6, html="BILL MURRAY &middot; <em>CAÇA-FANTASMAS</em>", x=1100, y=240),
            E("numero", em("anos", 0) - 0.5, 3.6, de=0, ate=33, sufixo="ANOS", dur=0.5)]
    # improvisos do aluno
    t = em("subiu", 150); out.append(E("carimbo", t, t + 2.0, texto="10º ANDAR NO MÍNIMO", rot=6))
    t = em("bali", 200); out.append(E("etq", t, t + 2.6, html="BALI &middot; <em>OU MADRID?</em> 🤔", x=1150, y=240))
    t = em("filtrado", 300); out.append(E("filtro", t - 0.8, t + 2.4, texto="✨ FILTRO NATURAL DE FÁBRICA"))
    t = em("sobrenome", 480); out.append(E("carimbo", t - 0.6, t + 1.6, texto="SUTHERLAND (EU TENTEI)", rot=-6))
    t = em("chalamet", em("papel", 480)); out.append(E("carimbo", t - 0.3, t + 1.6, texto="DE NOVO ELE?", rot=7))
    # sem sobreposição: o que vier depois começa quando o anterior acaba
    out.sort(key=lambda x: x["ini"]); final = []
    for x in out:
        if x["tipo"] != "flash" and final:
            ant = [f for f in final if f["tipo"] != "flash"]
            if ant and x["ini"] < ant[-1]["fim"]:
                if x["ini"] - ant[-1]["ini"] < 0.8: continue  # dois destaques no mesmo ponto: fica o primeiro
                ant[-1]["fim"] = x["ini"]
        final.append(x)
    return final


if __name__ == "__main__":
    if "--plano" in A:
        from planejar import Escolhedor
        from legendas import grupos
        es = Escolhedor(V + "build/indice_cenas.json", V + "midia/trailers", bloqueadas=V + "build/bloqueadas.json")
        cenas = []
        for c in CORTES:
            if c["cam"]:
                cenas += cenas_rosto(c)
            else:
                filmes, op = pool_de(c["nota"])
                cenas += es.segmento(c["ini"], c["fim"], filmes, op)
        # o último trecho segura 1 s a mais (respiro no fim)
        cenas[-1]["dur"] = round(cenas[-1]["dur"] + 1.0, 4)
        json.dump(cenas, open(R + "plano.json", "w"), ensure_ascii=False, indent=0)
        leg = grupos(PAL, 0, FIM, 4, {"Glenn": "Glen", "Farrell": "Farrow", "Deniro": "De Niro", "Hulk": "Hugh",
                                      "Axe": "X", "Kitton": "Keaton", "Kinton": "Keaton", "Peterson": "Pattinson",
                                      "Pattison": "Pattinson", "Bennett": "Benedict", "Silvestre": "Sylvester",
                                      "Graham": "Glen", "Steelwood": "Eastwood", "Surtland": "Sutherland",
                                      "Surtlund": "Sutherland", "pix": "Pix", "Rock": "Rocky"})
        el = destaques()
        json.dump({"duracao": FIM, "legenda": leg, "elementos": el}, open(R + "spec.json", "w"), ensure_ascii=False)
        print(len(cenas), "cenas;", sum(1 for c in cenas if c.get("_rosto")), "de rosto;",
              round(sum(c["dur"] for c in cenas if c.get("_rosto")) / FIM * 100), "% do tempo com rosto;",
              len(el), "destaques; duração", round(FIM, 1), "s")
