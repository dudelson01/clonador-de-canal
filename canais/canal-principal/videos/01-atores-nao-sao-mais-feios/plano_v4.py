"""Versão 4 (com rosto; correções do aluno sobre a v3): edição no estilo da referência, sem legenda, quase sem animação,
imagem SEMPRE conectada à fala (storyboard frase a frase).

python plano_v3.py --plano   -> build/v3/plano.json + build/v3/spec.json + folha de conferência
python plano_v3.py --som | --artes | --video
"""
import json, re, sys, os, subprocess, glob
sys.path.insert(0, "ferramentas")
V = "canais/canal-principal/videos/01-atores-nao-sao-mais-feios/"
R = V + "build/rosto/"; O3 = V + "build/v4/"; os.makedirs(O3, exist_ok=True)
A = sys.argv
CORTES = json.load(open(R + "cortes.json"))
PAL = json.load(open(R + "timeline.json"))["palavras"]
FIM = CORTES[-1]["fim"] + 0.8
ROSTO = R + "rosto.mp4"
FOTOS = V + "midia/fotos/"
TR = V + "midia/trailers/"
IDX = json.load(open(V + "build/indice_cenas.json"))
BLOQ = {tuple(x) for x in json.load(open(V + "build/bloqueadas.json"))}
ACH = json.load(open(V + "build/atores_achados.json"))

GB, TW, RK, CH, B89, TB = "ghostbusters-1984", "twisters-2024", "rocky-1976", "chalamet-a-complete-unknown", "batman-1989", "the-batman-2022"
OE, PC, FG, XM, DP, CD = "era-uma-vez-no-oeste-1968", "poderoso-chefao-1972", "fuga-de-nova-york-1981", "x-men-2000", "deadpool-wolverine-2024", "cidade-de-deus-2002"
RS, SW, TX, CR, HA2, HA21 = "bebe-de-rosemary-1968", "star-wars-1977", "taxi-driver-1976", "creed-2015", "homem-aranha-2002", "homem-aranha-2021"
TRS, IV = "tres-homens-em-conflito-1966", "invasores-de-corpos-1978"
VELHOS = [RK, TX, PC, OE, GB, TRS, B89]
NOVOS = [TW, DP, CR, CH, HA21, TB]


def norm(w): return re.sub(r"[^\wà-ú]", "", w.lower())


def foto(slug, k=None):
    fs = sorted(glob.glob(f"{FOTOS}{slug}/*.jpg"))
    if not fs: return None
    return fs[k % len(fs)] if k is not None else fs[0]


R_ = "R"
# ---------------- STORYBOARD: (âncora = primeiras palavras da frase, visual, nome opcional) ----------------
SB = [
 ("33 anos", ("A", "bill-murray", GB), ("Bill Murray", "33 anos em Caça-Fantasmas (1984)")),
 ("33", R_),
 ("olha essa cara", ("C", GB, [108.4], 0.6)),
 ("isso é um homem", R_),
 ("agora olha o", ("C", TW, [65.88], 0.4), ("Glen Powell", "35 anos em Twisters (2024)")),
 ("esse homem nunca", ("F", "glen-powell")),
 ("a pele dele", ("F", "glen-powell")),
 ("e não é impressão", R_),
 ("hollywood parou", ("C", CH, [82.85], 0.5)),
 ("hoje eu vou", R_),
 ("bruce willis de", ("F", "bruce-willis"), ("Bruce Willis", "")),
 ("o que eu quero", R_),
 ("antigamente", ("P", VELHOS)),
 ("era um rosto", R_),
 ("hoje os atores", ("M", [("F", "glen-powell"), ("A", "michael-b-jordan", CR, 0.62), ("A", "hugh-jackman", DP, 0.7), ("A", "timoth-e-chalamet", CH, 0.55)])),
 ("e eu falo", R_),
 ("e sim a imagem", ("P", NOVOS, "lavado")),
 ("mas pegar qualquer", R_),
 ("o elenco parecia", ("P", VELHOS)),
 ("parte do motivo", R_),
 ("seu avô", ("P", [OE, TRS, PC])),
 ("você quando chegar", R_),
 ("silvestre stallone", ("C", RK, [28.5, 141.0], 1.0, {"foco": [0.5, 0.42], "z0": 1.25}), ("Sylvester Stallone", "29 anos em Rocky (1976)")),
 ("olha esse rosto", ("C", RK, [137.2, 31.0], 1.0, {"foco": [0.5, 0.4], "z0": 1.3})),
 ("terceiro ainda acho", R_),
 ("com a mesma idade", ("A", "timoth-e-chalamet", CH, 0.55), ("Timothée Chalamet", "29 anos")),
 ("tá bom eu sei", R_),
 ("um é boxeador", ("C", RK, [155.0])),
 ("o outro parece", ("A", "timoth-e-chalamet", CH, 0.55)),
 ("vamos comparar", R_),
 ("de um lado bruce", ("F", "bruce-willis"), ("Bruce Willis", "33 anos em Duro de Matar (1988)")),
 ("do outro", ("F", "glen-powell"), ("Glen Powell", "35 anos em Twisters (2024)")),
 ("o bruce já", ("F", "bruce-willis")),
 ("o grey parece", ("F", "glen-powell")),
 ("ele é dois", R_),
 ("agora batman", ("A", "michael-keaton", B89), ("Michael Keaton", "37 anos em Batman (1989)")),
 ("robert pattinson", ("F", "robert-pattinson"), ("Robert Pattinson", "35 anos em The Batman (2022)")),
 ("o quinton tem", ("A", "michael-keaton", B89)),
 ("o pattinson foi", ("C", TB, [57.0, 80.0, 109.0, 114.0])),
 ("e mesmo assim", ("F", "robert-pattinson")),
 ("bali ou", R_),
 ("se eu passar", R_),
 ("que os atores antigos", R_),
 ("antes tinha", ("C", OE, [21.0, 14.0, 70.3, 129.0])),
 ("olha a abertura", ("C", OE, [7.5, 16.0]), ("Era Uma Vez no Oeste", "1968")),
 ("três pistoleiros", ("C", OE, [76.0, 79.0])),
 ("um tem um cabelo", ("C", OE, [76.0], 0.6, {"foco": [0.22, 0.55], "z0": 1.6})),
 ("o outro tem uma barba", ("C", OE, [21.0, 22.4])),
 ("e o terceiro tem", ("C", OE, [14.0, 74.0])),
 ("ninguém precisou", R_),
 ("quase 15", ("C", OE, [76.0, 83.0, 31.0])),
 ("isso seria um", R_),
 ("mesma coisa com", ("P", [PC]), ("O Poderoso Chefão", "1972")),
 ("e não era só", ("F", "kurt-russell"), ("Kurt Russell", "Fuga de Nova York (1981)")),
 ("agora olha o hulk", ("C", XM, [63.45], 0.4), ("Hugh Jackman", "X-Men (2000)")),
 ("e olha ele em", ("A", "hugh-jackman", DP, 0.7), ("Hugh Jackman", "Deadpool & Wolverine (2024)")),
 ("o wolverine de 2000", ("C", XM, [63.5], 0.38, {"espelhar": True})),
 ("o de 2024", ("A", "hugh-jackman", DP, 0.7)),
 ("controlado por", R_),
 ("e aqui tem o exemplo", ("P", [CD]), ("Cidade de Deus", "2002")),
 ("é por isso que esse filme", R_),
 ("e é por isso que você", ("P", [CD])),
 ("inclusive", R_),
 ("como que o", ("F", "timoth-e-chalamet")),
 ("que o cara tem", R_),
 ("olha a mia", ("F", "mia-farrow"), ("Mia Farrow", "O Bebê de Rosemary (1968)")),
 ("ao longo do filme", ("C", RS, [40.0, 42.6, 20.5, 69.0])),
 ("agora imagine", ("F", "margot-robbie"), ("Margot Robbie", "")),
 ("ela ia cortar", R_),
 ("é o rosto comum", ("F", "mia-farrow")),
 ("e quando parece", ("C", RS, [39.3])),
 ("em star wars", ("C", SW, [93.0, 96.0, 56.5]), ("Star Wars", "1977")),
 ("do outro lado os", ("C", SW, [88.0, 19.0, 79.0])),
 ("só pela cara", ("C", SW, [95.0, 89.2])),
 ("e em taxi driver", ("C", TX, [29.0, 57.5, 43.5]), ("Taxi Driver", "1976")),
 ("um careca em", ("C", TX, [70.5, 74.0, 79.0, 83.0])),
 ("o próprio deniro", ("C", TX, [27.0, 114.5]), ("Robert De Niro", "")),
 ("cara isso é mágico", R_),
 ("eles parecem que", ("C", TX, [129.5, 140.5, 152.0])),
 ("isso tem nome", R_),
 ("no fim de rocky", ("C", RK, [155.0, 136.6, 133.0, 156.5], 1.0, {"foco": [0.5, 0.4], "z0": 1.2})),
 ("quidge depois", ("C", CR, [70.0, 84.5, 116.0, 111.0], 1.0, {"foco": [0.5, 0.42], "z0": 1.2}), ("Michael B. Jordan", "Creed (2015)")),
 ("no fim de homem", ("C", HA2, [120.95, 23.0, 87.0], 0.4), ("Tobey Maguire", "Homem-Aranha (2002)")),
 ("o tom holland", ("C", HA21, [7.0, 106.6, 151.0, 18.6]), ("Tom Holland", "Homem-Aranha: Sem Volta para Casa (2021)")),
 ("e a máscara ele", ("C", HA21, [162.3, 151.0], 0.4)),
 ("e eu bato", R_),
 ("e em três homens", ("A", "clint-eastwood", TRS, 0.62), ("Clint Eastwood", "Três Homens em Conflito (1966)")),
 ("hoje o máximo", ("P", NOVOS)),
 ("mas quando todo", R_),
 ("em 2021", ("Q", {"tipo": "ensaio", "pub": "Blood Knife &middot; 2021", "titulo": "Everyone Is Beautiful and No One Is Horny",
                    "trad": "“Todo mundo é bonito e ninguém tem tesão”", "autor": "Raquel S. Benedict"})),
 ("sim é esse", R_),
 ("a ideia dela", ("M", [("A", "timoth-e-chalamet", CH, 0.55), ("A", "michael-b-jordan", CR, 0.62), ("A", "hugh-jackman", DP, 0.7), ("F", "glen-powell"), ("A", "tom-holland", HA21), ("F", "chris-evans"), ("F", "robert-pattinson")])),
 ("e tem tecnologia", R_),
 ("teve uma pessoa", ("A", "donald-sutherland", IV), ("Donald Sutherland", "Invasores de Corpos (1978)")),
 ("é bonito sim", ("F", "donald-sutherland")),
 ("e se perguntou", ("A", "donald-sutherland", IV)),
 ("será que seria", ("F", "timoth-e-chalamet")),
 ("o ryan reynolds", ("M", [("F", "ryan-reynolds"), ("A", "ryan-reynolds", DP)]), ("Ryan Reynolds", "")),
 ("o chris evans", ("F", "chris-evans"), ("Chris Evans", "")),
 ("ai mas ele", ("F", "chris-evans")),
 ("nós não temos", R_),
 ("parece que todo mundo", ("M", [("A", "hugh-jackman", DP, 0.7), ("A", "michael-b-jordan", CR, 0.62)])),
 ("e isso tem até", R_),
 ("é aquele rosto", ("F", "timoth-e-chalamet")),
 ("é por isso que tem", R_),
 ("o cara está em", ("P", [CH])),
 ("o personagem é", R_),
 ("e isso não é só", ("P", NOVOS)),
 ("antes era a bagunça", ("C", TX, [128.5, 131.0], 1.0)),
 ("a poeira", ("C", OE, [35.0, 146.0])),
 ("hoje muita coisa", ("P", NOVOS, "lavado")),
 ("olha não é todo", R_),
 ("rock ensanguentado", ("M", [("C", RK, [141.0], 1.0, {"foco": [0.5, 0.4], "z0": 1.2}), ("A", "clint-eastwood", TRS, 0.62), ("C", TX, [27.0]), ("C", OE, [76.0])])),
 ("os atores não são", ("P", NOVOS)),
 ("e é justamente", R_),
]


# ---------------- âncoras: acha cada frase em sequência na fala ----------------
def acha(frase, depois, limiar=0.78):
    """Primeira posição depois de 'depois' cujas palavras parecem com a frase (tolera erro do transcritor)."""
    import difflib
    alvo = " ".join(norm(x) for x in frase.split()); n = len(frase.split())
    ws = [(norm(w["w"]), w["s"]) for w in PAL]
    for i in range(len(ws)):
        if ws[i][1] < depois - 0.05: continue
        for m in (n, n + 1, n - 1):
            if m < 1: continue
            cand = " ".join(x[0] for x in ws[i:i + m])
            if difflib.SequenceMatcher(None, alvo, cand).ratio() >= limiar and cand[:2] == alvo[:2]:
                return ws[i][1]
    raise ValueError(f"âncora não achada: '{frase}' depois de {depois:.1f}")


def tempos():
    t, out = 0.0, []
    for k, e in enumerate(SB):
        s = 0.0 if k == 0 else acha(e[0], t)
        out.append(round(max(0.0, s - 0.08), 3)); t = s + 0.1
    return out


# ---------------- resolve cada visual em planos ----------------
usados = set()
USO_FOTO = {}
# clipes do próprio ator para alternar com as fotos (tempo no trailer)
FOTO_CLIPE = {
 "glen-powell": ("twisters-2024", [65.9, 57.4, 98.1, 47.3]),
 "robert-pattinson": ("the-batman-2022", [137.55, 64.6, 72.3]),
 "timoth-e-chalamet": ("chalamet-a-complete-unknown", [82.85, 60.2, 85.0]),
 "mia-farrow": ("bebe-de-rosemary-1968", [40.0, 42.6, 20.5, 69.0]),
 "michael-keaton": ("batman-1989", [31.0, 80.0]),
 "sylvester-stallone": ("rocky-1976", [28.5, 141.0]),
 "ryan-reynolds": ("deadpool-wolverine-2024", [88.5, 62.5]),
 "kurt-russell": ("fuga-de-nova-york-1981", [81.5, 83.2], 0.3),
 "margot-robbie": ("x", []),
}
FOTO_CLIPE = {k: v for k, v in FOTO_CLIPE.items() if v[1]}
ALT = {}
def altura(tr):
    if tr not in ALT:
        o = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                            "-of", "csv=p=0", TR + tr + ".mp4"], capture_output=True, text=True).stdout.split()[0].split(",")
        ALT[tr] = 960 * int(o[1]) / int(o[0])
    return ALT[tr]


def cena_de(tr, t):
    for i, c in enumerate(IDX.get(tr, [])):
        if c["ini"] <= t < c["fim"]: return i, c
    return None, None


def planos_ator(ator, tr, dur, minsim=0.5):
    ach = [x for x in ACH.get(ator, {}).get(tr, []) if x["sim"] >= minsim]
    vistos, cand = set(), []
    for x in sorted(ach, key=lambda x: -x["area"] * x["sim"]):
        i, c = cena_de(tr, x["t"])
        if i is None or c["cartela"] or (tr, i) in BLOQ or (tr, i) in vistos or not (30 <= c["brilho"] <= 215): continue
        vistos.add((tr, i)); cand.append((i, c, x["t"], x.get("box")))
    novos = [c for c in cand if (tr, c[0]) not in usados] or cand
    return novos


def resolve(vis, dur):
    """Devolve lista de planos (cenas para montar.py) cobrindo 'dur' segundos."""
    if vis == "R":
        n = max(1, round(dur / 3.0)); d = dur / n
        return [{"tipo": "R", "dur": d, "z0": [1.0, 1.14, 1.06][k % 3]} for k in range(n)]
    kind = vis[0]
    if kind == "F":
        fs = sorted(glob.glob(f"{FOTOS}{vis[1]}/*.jpg"))
        if not fs: return resolve("R", dur)  # sem foto: volta para o rosto (nunca imagem errada)
        n = max(1, round(dur / 1.3)); d = dur / n
        # menos de 3 fotos: alterna foto / clipe do mesmo ator, para nunca repetir a mesma imagem
        extra = []
        if len(fs) < n and vis[1] in FOTO_CLIPE:
            tr, tempos = FOTO_CLIPE[vis[1]][:2]; vclip = (FOTO_CLIPE[vis[1]][2:] or [1.0])[0]
            extra = [("C", tr, t_) for t_ in tempos]
        uniq = len(fs) + len(extra)
        if n > uniq: n = max(1, min(n, max(uniq, round(dur / 2.2)))); d = dur / n  # poucas imagens: cada uma fica mais tempo
        seq = []
        fi = USO_FOTO.get(vis[1], 0); ci = USO_FOTO.get(vis[1] + "#c", 0)
        # cada foto entra uma vez; o resto do tempo vai para clipes do ator; só repete foto se não houver clipe
        ordem = []
        for k in range(n):
            ordem.append("F" if (k < len(fs) or not extra) else "C")
        if extra and len(fs) >= 1:  # intercala: F C F C ... em vez de F F C C
            fotos = ordem.count("F"); clips = ordem.count("C"); ordem = []
            while fotos or clips:
                if fotos: ordem.append("F"); fotos -= 1
                if clips: ordem.append("C"); clips -= 1
        for o in ordem:
            if o == "C":
                _, tr, t_ = extra[ci % len(extra)]; ci += 1
                seq.append({"src": TR + tr + ".mp4", "ss": t_, "dur": d, "vel": vclip})
            else:
                seq.append({"src": fs[fi % len(fs)], "ss": 0, "dur": d, "zoom": 0.07}); fi += 1
        USO_FOTO[vis[1]] = fi; USO_FOTO[vis[1] + "#c"] = ci
        return seq
    if kind == "C":
        tr, lista = vis[1], vis[2]; vel = vis[3] if len(vis) > 3 else 1.0
        n = max(1, min(len(lista), round(dur / 1.8))); d = dur / n
        ext = dict(vis[4]) if len(vis) > 4 else {}
        return [{"src": TR + tr + ".mp4", "ss": lista[k], "dur": d, "vel": vel, **ext} for k in range(n)]
    if kind == "A":
        ator, tr = vis[1], vis[2]
        cand = planos_ator(ator, tr, dur, vis[3] if len(vis) > 3 else 0.5)
        if not cand: return resolve("R", dur)
        n = max(1, round(dur / 2.2)); d = dur / n; out = []
        for k in range(n):
            i, c, t, box = cand[k % len(cand)]; usados.add((tr, i))
            ss = max(c["ini"] + 0.08, t - 0.5); disp = c["fim"] - 0.08 - ss
            if disp < d * 0.45: ss = c["ini"] + 0.08; disp = c["fim"] - c["ini"] - 0.16
            vel = 1.0 if disp >= d else round(max(0.45, disp / d), 3)
            foco = None
            if box:
                H = altura(tr); foco = [round((box[0] + box[2] / 2) / 960, 3), round((box[1] + box[3] / 2) / H, 3)]
            out.append({"src": TR + tr + ".mp4", "ss": round(ss, 3), "dur": d, "vel": vel, "_filme": tr, "_cena": i,
                        **({"foco": foco, "z0": 1.3, "zoom": 0.08} if foco else {})})
        return out
    if kind == "P":
        from planejar import Escolhedor
        global ES
        if "ES" not in globals():
            ES = Escolhedor(V + "build/indice_cenas.json", TR.rstrip("/"), bloqueadas=V + "build/bloqueadas.json")
            for u in usados: ES.usado[u] = ES.usado.get(u, 0) + 1
        out = ES.segmento(0, dur, vis[1], {"efeito": vis[2]} if len(vis) > 2 else {})
        for o in out:
            if o.get("_filme"): usados.add((o["_filme"], o["_cena"]))
        return out
    if kind == "M":
        n = len(vis[1]); d = dur / n; out = []
        for v in vis[1]: out += resolve(v, d)
        return out
    if kind == "Q":
        return [{"src": "ARTE", "ss": 0, "dur": dur}]
    raise ValueError(vis)


if __name__ == "__main__" and "--plano" in A:
    T = tempos() + [FIM]
    cenas, el = [], []
    vistos_nome = set()
    for k, e in enumerate(SB):
        a, b = T[k], T[k + 1]; vis = e[1]
        ps = resolve(vis, b - a)
        t = a
        for p in ps:
            if p.get("tipo") == "R":
                p = {"src": ROSTO, "ss": round(t, 4), "dur": round(p["dur"], 4), "vel": 1.0, "z0": p["z0"], "zoom": 0.03,
                     "sem_vinheta": True, "_rosto": True}
            p["dur"] = round(p["dur"], 4); p["_frase"] = e[0]
            cenas.append(p); t += p["dur"]
        if len(e) > 2 and e[2] and e[2][0] not in vistos_nome:
            vistos_nome.add(e[2][0])
            el.append({"tipo": "nome", "ini": round(a + 0.3, 3), "fim": round(min(b, a + 3.6), 3), "titulo": e[2][0], "sub": e[2][1]})
        if vis[0] == "Q" if isinstance(vis, tuple) else False:
            el.append({**vis[1], "ini": round(a + 0.1, 3), "fim": round(b - 0.1, 3)})
    # CTA: botão de inscrever discreto
    t_cta = acha("se inscreve", 300)
    el.append({"tipo": "insc", "ini": round(t_cta - 1.2, 3), "fim": round(t_cta + 2.6, 3), "nome": "Lupa Infinita", "clique": 1.4,
               "avatar": "../../" + V + "midia/canal/avatar.jpg"})
    json.dump(cenas, open(O3 + "plano.json", "w"), ensure_ascii=False, indent=0)
    json.dump({"duracao": FIM, "legenda": [], "elementos": el}, open(O3 + "spec.json", "w"), ensure_ascii=False)
    rosto = sum(c["dur"] for c in cenas if c.get("_rosto"))
    print(len(cenas), "planos;", round(rosto / FIM * 100), "% rosto;", sum(1 for c in cenas if c["src"].endswith(".jpg")), "fotos;",
          len(el), "elementos; duração", round(sum(c["dur"] for c in cenas), 1), "/", round(FIM, 1))

if __name__ == "__main__" and "--som" in A:
    from mixar import mixar
    ini = {}
    for c in CORTES: ini.setdefault(c["bloco"], c["ini"])
    partes = [("GANCHO", "curioso", 100, 0, 11), ("P2", "tenso", 90, 0, 2), ("CTA", "curioso", 94, -3, 3),
              ("P4", "tenso", 100, 2, 4), ("P5", "curioso", 96, 2, 5), ("P6", "tenso", 84, -2, 6), ("FINAL", "epico", 80, 0, 7)]
    mus = []
    for i, (b, est, bpm, tom, seed) in enumerate(partes):
        a = max(0.0, ini[b] - (1.5 if i else 0)); fim = (ini[partes[i + 1][0]] + 0.5) if i + 1 < len(partes) else FIM + 1.5
        f = O3 + f"musica_{i}.wav"
        subprocess.run(["python3", "ferramentas/musica.py", f, str(fim - a), "--estilo", est, "--bpm", str(bpm),
                        "--tom", str(tom), "--seed", str(seed)], check=True, capture_output=True)
        mus.append((f, a))
    el = json.load(open(O3 + "spec.json"))["elementos"]; FX = V + "build/sfx/"
    sfx = []
    for e in el:
        if e["tipo"] == "tweet": sfx.append((FX + "pop.wav", e["ini"], -8))
        if e["tipo"] == "insc": sfx += [(FX + "pop.wav", e["ini"], -8), (FX + "tique.wav", e["ini"] + 1.4, -6)]
    # whoosh bem baixinho só quando entra/sai do rosto (troca de "mundo")
    cenas = json.load(open(O3 + "plano.json")); t = 0; ant = None
    for c in cenas:
        r = bool(c.get("_rosto"))
        if ant is not None and r != ant: sfx.append((FX + "whoosh.wav", t - 0.12, -20))
        ant = r; t += c["dur"]
    mixar(R + "voz.wav", O3 + "som.wav", 0, FIM, musicas=mus, sfx=sfx, musica_db=-17)
    print("som ok")

if __name__ == "__main__" and "--artes" in A:
    subprocess.run(["node", "ferramentas/arte/render.mjs", O3 + "spec.json", O3 + "artes.mov"], check=True, stdout=subprocess.DEVNULL)
    print("artes ok")

if __name__ == "__main__" and "--video" in A:
    from montar import base
    cenas = json.load(open(O3 + "plano.json"))
    base(cenas, O3 + "base.mp4", paralelo=2); print("base ok")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", O3 + "base.mp4", "-i", O3 + "artes.mov", "-i", O3 + "som.wav",
                    "-filter_complex", "[0][1]overlay=0:0:eof_action=pass,format=yuv420p[v]", "-map", "[v]", "-map", "2:a",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-r", "30", "-c:a", "aac", "-b:a", "192k",
                    "-ar", "48000", "-shortest", "-movflags", "+faststart", V + "out/video-rosto-v4.mp4"], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", V + "out/video-rosto-v4.mp4", "-c:v", "libx264", "-preset", "medium",
                    "-b:v", "3900k", "-maxrate", "5000k", "-bufsize", "8000k", "-c:a", "copy", "-movflags", "+faststart",
                    V + "out/video-rosto-v4-envio.mp4"], check=True)
    print("VIDEO v4 ok")
