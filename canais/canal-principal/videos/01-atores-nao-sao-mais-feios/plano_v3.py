"""Versão 3 (com rosto): edição no estilo da referência, sem legenda, quase sem animação,
imagem SEMPRE conectada à fala (storyboard frase a frase).

python plano_v3.py --plano   -> build/v3/plano.json + build/v3/spec.json + folha de conferência
python plano_v3.py --som | --artes | --video
"""
import json, re, sys, os, subprocess, glob
sys.path.insert(0, "ferramentas")
V = "canais/canal-principal/videos/01-atores-nao-sao-mais-feios/"
R = V + "build/rosto/"; O3 = V + "build/v3/"; os.makedirs(O3, exist_ok=True)
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
 ("esse homem nunca", ("F", "glen-powell", 0)),
 ("a pele dele", ("F", "glen-powell", 2)),
 ("e não é impressão", R_),
 ("hollywood parou", ("C", CH, [82.85], 0.5)),
 ("hoje eu vou", R_),
 ("bruce willis de", ("F", "bruce-willis", 0), ("Bruce Willis", "")),
 ("o que eu quero", R_),
 ("antigamente", ("P", VELHOS)),
 ("era um rosto", R_),
 ("hoje os atores", ("M", [("F", "glen-powell", 0), ("A", "michael-b-jordan", CR), ("A", "hugh-jackman", DP), ("A", "timoth-e-chalamet", CH)])),
 ("e eu falo", R_),
 ("e sim a imagem", ("P", NOVOS, "lavado")),
 ("mas pegar qualquer", R_),
 ("o elenco parecia", ("P", VELHOS)),
 ("parte do motivo", R_),
 ("seu avô", ("P", [OE, TRS, PC])),
 ("você quando chegar", R_),
 ("silvestre stallone", ("A", "sylvester-stallone", RK), ("Sylvester Stallone", "29 anos em Rocky (1976)")),
 ("terceiro ainda acho", R_),
 ("com a mesma idade", ("A", "timoth-e-chalamet", CH, 0.55), ("Timothée Chalamet", "29 anos")),
 ("tá bom eu sei", R_),
 ("um é boxeador", ("C", RK, [160.0])),
 ("o outro parece", ("A", "timoth-e-chalamet", CH)),
 ("vamos comparar", R_),
 ("de um lado bruce", ("F", "bruce-willis", 1), ("Bruce Willis", "33 anos em Duro de Matar (1988)")),
 ("do outro", ("F", "glen-powell", 1), ("Glen Powell", "35 anos em Twisters (2024)")),
 ("o bruce já", ("F", "bruce-willis", 2)),
 ("o grey parece", ("F", "glen-powell", 2)),
 ("ele é dois", R_),
 ("agora batman", ("A", "michael-keaton", B89), ("Michael Keaton", "37 anos em Batman (1989)")),
 ("robert pattinson", ("F", "robert-pattinson", 0), ("Robert Pattinson", "35 anos em The Batman (2022)")),
 ("o quinton tem", ("A", "michael-keaton", B89)),
 ("o pattinson foi", ("M", [("C", TB, [137.55], 0.45), ("F", "robert-pattinson", 0)])),
 ("e mesmo assim", ("F", "robert-pattinson", 1)),
 ("bali ou", R_),
 ("se eu passar", R_),
 ("mas não é só", R_),
 ("antes tinha", ("P", [TRS, OE])),
 ("olha a abertura", ("P", [OE]), ("Era Uma Vez no Oeste", "1968")),
 ("ninguém precisou", R_),
 ("quase 15", ("P", [OE])),
 ("hoje isso seria", R_),
 ("mesma coisa com", ("P", [PC]), ("O Poderoso Chefão", "1972")),
 ("e não era só", ("F", "kurt-russell", 0), ("Kurt Russell", "Fuga de Nova York (1981)")),
 ("agora olha o hulk", ("C", XM, [63.45], 0.4), ("Hugh Jackman", "X-Men (2000)")),
 ("e olha ele em", ("A", "hugh-jackman", DP), ("Hugh Jackman", "Deadpool & Wolverine (2024)")),
 ("o wolverine de 2000", ("C", XM, [63.5], 0.38, {"espelhar": True})),
 ("o de 2024", ("A", "hugh-jackman", DP)),
 ("controlado por", R_),
 ("e aqui tem o exemplo", ("P", [CD]), ("Cidade de Deus", "2002")),
 ("é por isso que esse filme", R_),
 ("e é por isso que você", ("P", [CD])),
 ("inclusive", R_),
 ("como que o", ("A", "timoth-e-chalamet", CH)),
 ("que o cara tem", R_),
 ("olha a mia", ("F", "mia-farrow", 0), ("Mia Farrow", "O Bebê de Rosemary (1968)")),
 ("ao longo do filme", ("P", [RS])),
 ("agora imagine", ("F", "margot-robbie", 0), ("Margot Robbie", "")),
 ("ela ia cortar", R_),
 ("é o rosto comum", ("F", "mia-farrow", 1)),
 ("e quando parece", R_),
 ("em star wars", ("P", [SW]), ("Star Wars", "1977")),
 ("e em taxi driver", ("P", [TX]), ("Taxi Driver", "1976")),
 ("o próprio deniro", ("A", "robert-de-niro", TX), ("Robert De Niro", "")),
 ("cara isso é mágico", R_),
 ("eles parecem que", ("P", [TX])),
 ("isso tem nome", R_),
 ("no fim de rocky", ("M", [("C", RK, [157.0]), ("A", "sylvester-stallone", RK)])),
 ("quidge depois", ("A", "michael-b-jordan", CR, 0.62), ("Michael B. Jordan", "Creed (2015)")),
 ("no fim de homem", ("A", "tobey-maguire", HA2), ("Tobey Maguire", "Homem-Aranha (2002)")),
 ("o tom holland", ("M", [("A", "tom-holland", HA21), ("P", [HA21])]), ("Tom Holland", "Homem-Aranha: Sem Volta para Casa (2021)")),
 ("e eu bato", R_),
 ("e em três homens", ("A", "clint-eastwood", TRS, 0.62), ("Clint Eastwood", "Três Homens em Conflito (1966)")),
 ("hoje o máximo", ("P", NOVOS)),
 ("mas quando todo", R_),
 ("em 2021", ("Q", {"tipo": "tweet", "nome": "Raquel S. Benedict", "user": "ensaio &middot; 2021",
                    "texto": "“Todo mundo é bonito e ninguém tem tesão.”", "likes": "o nome é esse mesmo"})),
 ("sim é esse", R_),
 ("a ideia dela", ("M", [("A", "timoth-e-chalamet", CH, 0.55), ("A", "michael-b-jordan", CR, 0.62), ("A", "hugh-jackman", DP, 0.7), ("F", "glen-powell", 2), ("A", "tom-holland", HA21), ("F", "chris-evans", 0), ("F", "robert-pattinson", 0)])),
 ("e tem tecnologia", R_),
 ("percebendo", ("Q", {"tipo": "tweet", "nome": "cinéfilo cansado", "user": "@saudade_dos_80",
                      "texto": "que saudade de ator com dente normal", "likes": "48 mil"})),
 ("é chato demais", ("Q", {"tipo": "tweet", "nome": "maria vê filmes", "user": "@mariavefilmes",
                          "texto": "é chato demais todo mundo ter o mesmo dente e o mesmo corpo", "likes": "31 mil"})),
 ("teve uma pessoa", ("A", "donald-sutherland", IV), ("Donald Sutherland", "Invasores de Corpos (1978)")),
 ("é bonito sim", ("F", "donald-sutherland", 0)),
 ("e se perguntou", ("A", "donald-sutherland", IV)),
 ("será que seria", ("F", "timoth-e-chalamet", 0)),
 ("o ryan reynolds", ("M", [("F", "ryan-reynolds", 0), ("A", "ryan-reynolds", DP)]), ("Ryan Reynolds", "")),
 ("o chris evans", ("F", "chris-evans", 0), ("Chris Evans", "")),
 ("ai mas ele", ("F", "chris-evans", 1)),
 ("nós não temos", R_),
 ("parece que todo mundo", ("M", [("A", "hugh-jackman", DP, 0.7), ("A", "michael-b-jordan", CR, 0.62)])),
 ("e isso tem até", R_),
 ("é aquele rosto", ("F", "timoth-e-chalamet", 1)),
 ("é por isso que tem", R_),
 ("o cara está em", ("P", [CH])),
 ("o personagem é", R_),
 ("e isso não é só", ("P", NOVOS)),
 ("antes era a bagunça", ("C", TX, [128.5, 131.0], 1.0)),
 ("a poeira", ("P", [OE, TRS])),
 ("hoje muita coisa", ("P", NOVOS, "lavado")),
 ("olha não é todo", R_),
 ("rock ensanguentado", ("M", [("A", "sylvester-stallone", RK), ("A", "clint-eastwood", TRS, 0.62), ("A", "robert-de-niro", TX), ("P", [OE])])),
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
        vistos.add((tr, i)); cand.append((i, c, x["t"]))
    novos = [c for c in cand if (tr, c[0]) not in usados] or cand
    return novos


def resolve(vis, dur):
    """Devolve lista de planos (cenas para montar.py) cobrindo 'dur' segundos."""
    if vis == "R":
        n = max(1, round(dur / 3.0)); d = dur / n
        return [{"tipo": "R", "dur": d, "z0": [1.0, 1.14, 1.06][k % 3]} for k in range(n)]
    kind = vis[0]
    if kind == "F":
        f = foto(vis[1], vis[2] if len(vis) > 2 else None)
        if f is None: return resolve("R", dur)  # sem foto: volta para o rosto (nunca imagem errada)
        return [{"src": f, "ss": 0, "dur": dur, "zoom": 0.07}]
    if kind == "C":
        tr, lista = vis[1], vis[2]; vel = vis[3] if len(vis) > 3 else 1.0
        n = max(1, min(len(lista), round(dur / 1.8))); d = dur / n
        ext = vis[4] if len(vis) > 4 else {}
        return [{"src": TR + tr + ".mp4", "ss": lista[k], "dur": d, "vel": vel, **ext} for k in range(n)]
    if kind == "A":
        ator, tr = vis[1], vis[2]
        cand = planos_ator(ator, tr, dur, vis[3] if len(vis) > 3 else 0.5)
        if not cand: return resolve("R", dur)
        n = max(1, round(dur / 2.2)); d = dur / n; out = []
        for k in range(n):
            i, c, t = cand[k % len(cand)]; usados.add((tr, i))
            ss = max(c["ini"] + 0.08, t - 0.5); disp = c["fim"] - 0.08 - ss
            if disp < d * 0.45: ss = c["ini"] + 0.08; disp = c["fim"] - c["ini"] - 0.16
            vel = 1.0 if disp >= d else round(max(0.45, disp / d), 3)
            out.append({"src": TR + tr + ".mp4", "ss": round(ss, 3), "dur": d, "vel": vel, "_filme": tr, "_cena": i})
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
    el.append({"tipo": "insc", "ini": round(t_cta - 1.2, 3), "fim": round(t_cta + 2.6, 3), "nome": "Seu Canal", "clique": 1.4})
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
    mixar(R + "voz.wav", O3 + "som.wav", 0, FIM, musicas=mus, sfx=sfx, musica_db=-21)
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
                    "-ar", "48000", "-shortest", "-movflags", "+faststart", V + "out/video-rosto-v3.mp4"], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", V + "out/video-rosto-v3.mp4", "-c:v", "libx264", "-preset", "medium",
                    "-b:v", "3900k", "-maxrate", "5000k", "-bufsize", "8000k", "-c:a", "copy", "-movflags", "+faststart",
                    V + "out/video-rosto-v3-envio.mp4"], check=True)
    print("VIDEO v3 ok")
