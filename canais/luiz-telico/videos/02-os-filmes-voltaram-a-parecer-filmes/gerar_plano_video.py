#!/usr/bin/env python3
"""Gera plano_video.json (video 02 inteiro) ancorado na fala aprovada (timeline.json).
Cada imagem de apoio (B-roll) tem uma lista de fontes em ordem de preferencia: trailer do aluno (midia/trailers/<id>.mp4)
ou foto livre (midia/fotos/<nome>.jpg). Usa a primeira que existir; se nenhuma existir ainda, a cena fica no rosto
com um efeito de cor que ilustra a fala. Rodar de novo quando chegar midia nova troca as cenas sozinho.
Uso: python3 gerar_plano_video.py"""
import json, os, re, unicodedata

AQUI = os.path.dirname(os.path.abspath(__file__))
TL = json.load(open(os.path.join(AQUI, "timeline.json")))["palavras"]
FIM = round(max(w["e"] for w in TL) + 0.25, 2)

def norm(s):
    s = unicodedata.normalize("NFD", s.lower()); s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9 ]", " ", s).split()
TOK = [(t, w["s"], w["e"]) for w in TL for t in norm(w["w"])]

_cursor = [0]
def T(frase, depois=None, fim=False):
    """tempo (s) do inicio da frase na fala (ou do fim, com fim=True), procurando a partir do ultimo achado."""
    alvo = norm(frase); i0 = 0
    if depois is not None: i0 = next(i for i, x in enumerate(TOK) if x[1] >= depois - 0.05)
    else: i0 = _cursor[0]
    for i in range(i0, len(TOK) - len(alvo) + 1):
        if [x[0] for x in TOK[i:i + len(alvo)]] == alvo:
            return round(TOK[i + len(alvo) - 1][2] if fim else TOK[i][1], 2)
    raise SystemExit(f"nao achei '{frase}' depois de {TOK[i0][1]:.1f}s")

def existe(rel): return os.path.exists(os.path.join(AQUI, rel)) and os.path.getsize(os.path.join(AQUI, rel)) > 10000

# trailers que o aluno mandar: midia/trailers/<id>.mp4 ; "t" = segundo do trailer a usar (ajustar ao conferir)
TRAILERS = {k: f"midia/trailers/{k}.mp4" for k in
            ("duna", "odisseia", "batman", "oppenheimer", "backrooms", "obsession", "doomsday", "ainda", "agente", "pecadores", "barbie")}

ZMIN = {"agente": 1.18, "ainda": 1.08, "backrooms": 1.10, "barbie": 1.16, "batman": 1.37, "doomsday": 1.37,
        "duna": 1.24, "obsession": 1.21, "odisseia": 1.37, "oppenheimer": 1.26, "pecadores": 1.10}
FOCO = {"duna": [0.5, 0.42]}          # Duna tem legenda embutida embaixo: sobe o foco para ela ficar fora
PILAR = {"backrooms": [(58, 82), (99, 105)]}   # trechos com faixa lateral (4:3): zoom maior
CORTES_T = json.load(open(os.path.join(AQUI, "build/cortes_trailers.json"))) if os.path.exists(os.path.join(AQUI, "build/cortes_trailers.json")) else {}
def inicio_do_plano(src, t):
    """comeca no inicio do plano do trailer que contem t (sem pegar o fim do plano anterior nem preto)."""
    cs = [c for c in CORTES_T.get(src, {}).get("cortes", []) if c <= t + 0.3]
    if cs and t - cs[-1] < 1.2: t = cs[-1] + 0.08
    for a, b in CORTES_T.get(src, {}).get("pretos", []):
        if a - 0.05 <= t <= b: t = b + 0.05
    return round(t, 2)

# ---------------- marcas de corte (cenas) ----------------
cortes = []   # (ini, tipo, dados)
def _anda(t):   # so as CENAS andam o cursor de busca (artes podem olhar a frente sem atrapalhar)
    _cursor[0] = next((i for i, x in enumerate(TOK) if x[1] >= t - 0.05), _cursor[0])
def R(t, z=(1.0, 1.06), efeito=None, sfx=None):            # rosto
    _anda(t); cortes.append((t, "rosto", dict(zoom=list(z), efeito=efeito, sfx=sfx)))
def P(t, efeito=None, sfx=None): R(t, (1.20, 1.24), efeito, sfx)   # punch-in no rosto (piada, enfase)
def B(t, fontes, efeito_rosto=None, z=(1.08, 1.16), efeito=None, sfx=(("whoosh", 0),), foco=None):
    """imagem de apoio: primeira fonte que existir; senao rosto com efeito."""
    _anda(t)
    for f in fontes:
        if isinstance(f, tuple):                       # ("trailer_id", segundo)
            if existe(TRAILERS[f[0]]):
                zm = ZMIN.get(f[0], 1.08)
                if any(a <= f[1] <= b for a, b in PILAR.get(f[0], [])): zm = 1.36
                d = dict(src=f[0], t=inicio_do_plano(f[0], f[1]), zoom=[zm, round(zm + 0.07, 2)], efeito=efeito, sfx=[list(x) for x in sfx])
                if f[0] in FOCO: d["foco"] = FOCO[f[0]]
                cortes.append((t, "video", d)); return
        elif existe(f"midia/fotos/{f}.jpg"):
            d = dict(arquivo=f"midia/fotos/{f}.jpg", zoom=[1.04, 1.14], efeito=efeito, sfx=[list(s) for s in sfx])
            if foco: d["foco"] = foco
            cortes.append((t, "foto", d)); return
    R(t, (1.10, 1.16), efeito_rosto, sfx=[list(s) for s in sfx] if efeito_rosto else None)

artes = []
def A(t, tipo, dur, **k):
    artes.append(dict(id=f"{tipo}_{len(artes):03d}", ini=round(t, 2), dur=dur, tipo=tipo, **k))

# ================= ABERTURA (objetos sem cor) =================
R(0.0, (1.0, 1.05))
A(T("sem cor"), "chave", 2.6, texto="Sem <b>cor</b>. Sem <b>vida</b>.")
P(T("tipo essa muleta"), efeito="lavado")
A(T("muleta"), "canto", 6.5, texto="OBJETO 1: MULETA")
R(T("igualmente tambem"), (1.06, 1.12), efeito="lavado")
A(T("cortina"), "canto", 6.0, texto="OBJETO 2: CORTINA")
P(T("igual tambem esse laptop"), efeito="lavado")
A(T("laptop"), "canto", 5.5, texto="OBJETO 3: LAPTOP")
A(T("bomba atomica"), "maquina", 2.6, x=980, y=760, texto="“BOMBA ATÔMICA DE 2013”", sfx="teclas")
R(T("a diferenca"))
B(T("os filmes de hollywood"), ["hollywood"], sfx=(("whoosh", 0),))
A(T("bastante investimento"), "dinheiro", 1.8, de=0, ate=200, fmt="US$ {v} MI", rotulo="de orçamento", sfx="ding")
P(T("e estao parecendo eles"), efeito="lavado", sfx=[["boing", 0.35]])
A(T("e estao parecendo eles"), "meme", 2.2, texto="…E ESTÃO IGUAIS À MULETA")

# ================= GANCHO =================
R(T("faz anos que a gente"), (1.0, 1.08))
A(T("o cinema morreu"), "maquina", 2.4, x=120, y=110, texto="“O CINEMA MORREU”", sfx="teclas")
B(T("filme de heroi"), [("doomsday", 106.0)], efeito_rosto=None)
A(T("continuacao"), "lista", 3.2, x=1180, y=200, titulo="Hollywood hoje", vel=0.55,
  itens=[{"texto": "Continuação"}, {"texto": "Remake"}, {"texto": "Herói igual"}])
P(T("so que em 2026"), sfx=[["subida", 0]])
A(T("2026"), "carimbo", 1.6, x=1450, y=300, texto="2026")
B(T("um filme de terror"), [("obsession", 106.1), "dolares"], efeito_rosto=None)
A(T("um filme de terror"), "cardfilme", 3.4, titulo="Obsession", sub="custou menos que um apartamento")
A(T("meio bilhao"), "dinheiro", 2.0, de=0, ate=500, fmt="US$ {v} MI", rotulo="de bilheteria", sfx="ding")
B(T("um garoto de 20 anos"), [("backrooms", 100.0), "corredor_amarelo"])
A(T("um garoto de 20 anos"), "cardfilme", 3.6, titulo="Backrooms", sub="Kane Parsons, 20 anos, começou no YouTube", cor="#e8c300")
A(T("a maior estreia"), "carimbo", 1.8, x=1400, y=420, texto="RECORDE")

# ================= PIADA: O PRIMO (mae x filho) =================
P(T("rapaz eu nao queria"))
A(T("rapaz eu nao queria"), "meme", 2.4, texto="IMAGINA SER PRIMO DESSE CARA")
R(T("oi tudo bem artuzinho"), (1.10, 1.14))
A(T("oi tudo bem artuzinho"), "dialogo", 11.2, y=110, falas=[
    {"quem": "MÃE", "texto": "Oi, tudo bem, Artuzinho? O seu primo ganhou meio bilhão de dólares. E você?", "t": 0.0, "alto": 230},
    {"quem": "ARTUZINHO", "texto": "Zerei o GTA 6 em menos de uma semana!", "lado": "dir", "t": T("bom mamae") - T("oi tudo bem artuzinho")},
    {"quem": "MÃE", "texto": "Você é um desgosto pra família.", "t": T("artuzinho voce e um desgosto") - T("oi tudo bem artuzinho")}])
R(T("bom mamae"), (1.0, 1.03), sfx=[["pop", 0]])
P(T("artuzinho voce e um desgosto"), sfx=[["pop", 0]])
P(T("que horror"), sfx=[["errou", 0]])
A(T("que horror"), "meme", 1.4, texto="QUE HORROR!", cor="#ff2b2b")

# ================= A ODISSEIA / TESE =================
B(T("alem do mais"), [("odisseia", 42.0), "homero", "odisseia_arte"])
A(T("um poema de quase"), "contador", 2.2, x=1450, y=420, de=0, ate=3000, rotulo="ANOS", tc=1.0)
B(T("christopher nolan"), [("odisseia", 10.0), "nolan"])
A(T("christopher nolan"), "cardfilme", 4.2, titulo="A Odisseia", sub="Christopher Nolan · 2026")
A(T("o maior filme da carreira"), "carimbo", 1.8, x=1400, y=380, texto="MAIOR ESTREIA DO NOLAN", rot=-6)
t0 = T("os filmes voltaram")
for k, (src, tt) in enumerate([("odisseia", 50.0), ("duna", 46.0), ("batman", 92.0), ("oppenheimer", 172.0)]):
    B(round(t0 + k * 0.95, 2), [(src, tt)], sfx=(("impacto" if k == 0 else "whoosh", 0.03),))
A(t0, "meme", 3.4, y=90, texto="OS FILMES VOLTARAM A PARECER FILMES", tam=92)
R(T("porque hollywood esta"))
A(T("encruzilhada"), "versus", 3.4, a="FINAL BOM", b="FINAL RUIM", tam=100)
P(T("o final ruim ja comecou"))
A(T("ja comecou"), "perigo", 1.3, texto="JÁ COMEÇOU")
R(T("no fim do video"), (1.06, 1.12))
A(T("no fim do video"), "maquina", 2.0, x=120, y=860, texto="FICA ATÉ O FIM…", sfx="teclas")

# ================= 1. O VISUAL DE STREAMING =================
R(T("repara numa coisa"), (1.0, 1.06), sfx=[["rebobinar", 0]])
R(T("com meio apagada"), (1.08, 1.14), efeito="lavado")
A(T("com meio apagada"), "chave", 3.0, texto="Cor apagada · tudo <b>cinza</b> · tudo <b>bege</b>")
P(T("o rosto do ator nitido"), efeito="lavado")
A(T("fundo todo borrado"), "chave", 2.2, texto="Rosto nítido, fundo <b>borrado</b>")
R(T("nenhuma imagem que voce"), (1.0, 1.05), efeito="lavado")
R(T("eu acho que a unica imagem"), (1.06, 1.1))
A(T("euphoria"), "canto", 3.0, texto="EUPHORIA (HBO)")
P(T("nao que eu seja tarado"), sfx=[["boing", 0.2]])
A(T("nao que eu seja tarado"), "meme", 2.2, texto="NÃO QUE EU SEJA TARADO")
R(T("eles fixam o rosto"), (1.3, 1.42))
A(T("eles fixam o rosto"), "chave", 2.4, texto="Rosto <b>colado</b> na câmera")
R(T("e as vezes o ator nem"), (1.0, 1.04))
A(T("nem e bonito"), "meme", 1.6, texto="NEM É BONITO", y=140)
P(T("nao que eu seja mas"), sfx=[["bonk", 0.1]])
R(T("e tem gente que chama"), (1.0, 1.05))
A(T("visual netflix"), "carimbo", 2.2, x=1380, y=360, texto="“VISUAL NETFLIX”")
R(T("mas nao e culpa"), (1.06, 1.12))
P(T("e uma escolha"))
A(T("e uma escolha"), "chave", 1.8, texto="É uma <b>escolha</b>.")
R(T("e o filme feito"), (1.0, 1.05))
A(T("no celular"), "lista", 3.6, x=1180, y=160, titulo="Feito pra qualquer tela", vel=0.6,
  itens=[{"texto": "Celular"}, {"texto": "Ônibus"}, {"texto": "TV velha"}])
R(T("sabe aquelas televisoes"), (1.04, 1.1), efeito="crt", sfx=[["rebobinar", 0]])
A(T("sabe aquelas televisoes"), "canto", 4.0, texto="TV DE TUBO")
R(T("ai na frente a tela"), (1.1, 1.16), efeito="crt")
P(T("dar um tapa nela"), efeito="crt", sfx=[["bonk", 0.15]])
R(T("entao esses filmes tambem"), (1.0, 1.06), efeito="crt")
P(T("e o famoso"), sfx=[["impacto", 0.1]])
A(T("e o famoso"), "meme", 2.0, texto="O FAMOSO “TÁ BOM ASSIM”")
R(T("enquadra foca"), (1.0, 1.05))
A(T("enquadra foca"), "lista", 2.6, x=1250, y=240, vel=0.45, itens=[{"texto": "Enquadra"}, {"texto": "Foca"}, {"texto": "Ilumina"}, {"texto": "Pronto."}])
B(T("agora pensa em duna"), [("duna", 46.0), "deserto"], efeito_rosto="vivido", efeito=None)
A(T("agora pensa em duna"), "cardfilme", 3.4, titulo="Duna: Parte 2", sub="Denis Villeneuve · 2024", cor="#ff8a1e")
B(T("naquela cena do gladiador"), [("duna", 100.0)], efeito_rosto="pb", efeito=None)
A(T("preto e branco"), "chave", 2.4, texto="Gladiador em <b>preto e branco</b> no sol negro")
B(T("pensa tambem em a odisseia"), [("odisseia", 50.0), "imax_camera"])
A(T("camera imax"), "cardfilme", 2.8, titulo="A Odisseia", sub="filmado inteiro com câmeras IMAX")
B(T("aquele trambolho"), ["imax_camera", "geladeira"], efeito_rosto=None)
A(T("do tamanho de uma geladeira"), "meme", 2.4, texto="DO TAMANHO DE UMA GELADEIRA", tam=96)
B(T("pensa em batman"), [("batman", 126.0), "chuva_noite"], efeito_rosto="vermelho")
A(T("pensa em batman"), "cardfilme", 3.0, titulo="Batman", sub="Matt Reeves · 2022", cor="#c40000")
B(T("contam a historia"), [("batman", 135.8), "chuva_noite"], efeito_rosto="vermelho")
R(T("nenhuma dessas escolhas"), (1.0, 1.06))
A(T("nenhuma dessas escolhas"), "chave", 2.6, texto="Nenhuma era <b>segura</b>")
P(T("e justamente por isso"))
R(T("ate porque todo investimento"), (1.04, 1.1))
B(T("se nao fosse o risco do bitcoin"), ["bitcoin"], efeito_rosto=None)
A(T("bitcoin"), "dinheiro", 2.2, de=0, ate=1, fmt="₿ {v}", rotulo="o risco que deu certo", tc=0.4, cor="#f7931a", sfx="ding")
R(T("talvez o daniel fraga"), (1.06, 1.12))
A(T("daniel fraga"), "canto", 3.2, texto="DANIEL FRAGA (YOUTUBER)")
R(T("nao sei se voce conhece"), (1.0, 1.05))
A(T("ficou muito rico"), "meme", 2.2, texto="FICOU RICO ANTES DE TODO MUNDO", tam=90)

# ================= PONTE =================
R(T("ate aqui parece so papo"), (1.0, 1.06))
B(T("mas a imagem bonita nao explica"), ["hollywood", ("backrooms", 30.0)], efeito_rosto=None)
A(T("um garoto do youtube"), "chave", 2.6, texto="Um garoto do YouTube <b>derrubou Hollywood</b>")
P(T("isso tem a ver"), sfx=[["subida", 0]])

# ================= 2. FILME DE QUEM QUIS FAZER =================
R(T("em 2020 no fim"), (1.0, 1.06))
A(T("em 2020 no fim"), "maquina", 3.0, x=120, y=110, texto="2020 · FIM DAS FILMAGENS DE TENET", sfx="teclas")
A(T("o robert pattinson"), "polaroid", 3.6, src="__FOTO__pattinson", legenda="Robert Pattinson", x=1300, y=150) if existe("midia/fotos/pattinson.jpg") else \
    A(T("o robert pattinson"), "canto", 3.0, texto="ROBERT PATTINSON")
B(T("um livro com discursos"), ["livro", "oppenheimer"], efeito_rosto=None)
A(T("discursos do oppenheimer"), "chave", 2.4, texto="Discursos de <b>J. Robert Oppenheimer</b>")
P(T("se eu tenho um amigo rico"))
A(T("ele poderia me dar"), "lista", T("eu nao sei se eu continuaria") - T("ele poderia me dar") + 0.2, x=1080, y=150, titulo="Presente de amigo rico",
  vel=0.75, itens=[{"texto": "Lamborghini"}, {"texto": "Ferrari"}, {"texto": "iPhone 18"}, {"texto": "Livro do Oppenheimer", "ok": False}])
A(T("eu corto essa amizade"), "carimbo", 1.6, x=640, y=520, texto="AMIZADE CANCELADA", rot=-8)
R(T("ele poderia me dar"), (1.0, 1.04))
P(T("mas ele me da um livro"), sfx=[["errou", 0.6]])
R(T("eu nao sei se eu continuaria"), (1.08, 1.12))
B(T("mas o nolan ate que gostou"), ["nolan"], efeito_rosto=None)
A(T("nao conseguiu largar"), "chave", 2.0, texto="Leu e <b>não conseguiu largar</b>")
B(T("um cientista tentando"), [("oppenheimer", 166.0), "trinity", "oppenheimer"], efeito_rosto="pb")
A(T("um cientista tentando"), "chave", 3.4, texto="Um cientista vivendo com o que <b>soltou no mundo</b>")
B(T("tres anos depois"), [("oppenheimer", 94.0), "oppenheimer"])
A(T("tres anos depois"), "cardfilme", 3.0, titulo="Oppenheimer", sub="Christopher Nolan · 2023")
B(T("tres horas de gente"), [("oppenheimer", 100.0), "lousa_fisica"])
A(T("tres horas de gente"), "contador", 2.0, x=1450, y=400, de=0, ate=3, rotulo="HORAS", tc=0.6)
A(T("chegou perto de um bilhao"), "dinheiro", 2.2, de=0, ate=950, fmt="US$ {v} MI", rotulo="no mundo", sfx="ding")
P(T("cara imagina voce pegar"))
R(T("um filme que gera"), (1.0, 1.06))
P(T("gente isso e muita coisa"), sfx=[["impacto", 0]])
A(T("gente isso e muita coisa"), "meme", 1.8, texto="ISSO É MUITA COISA!")

# Backrooms
B(T("agora pensa no back"), [("backrooms", 26.0), "corredor_amarelo"], efeito=None)
A(T("agora pensa no back"), "cardfilme", 3.0, titulo="Backrooms", sub="A24 · 2026", cor="#e8c300")
B(T("o ken parsons"), ["kane_parsons", ("backrooms", 44.0)], efeito_rosto=None)
A(T("o ken parsons"), "canto", 4.0, texto="KANE PARSONS")
R(T("adolescente sozinho"), (1.0, 1.06))
P(T("todo mundo achando"), sfx=[["boing", 0.8]])
R(T("mas nao ele estava sendo"), (1.04, 1.1), sfx=[["plim", 0.4]])
A(T("sendo criativo"), "chave", 1.8, texto="Ele estava sendo <b>criativo</b>")
B(T("em 2026 ele virou"), [("backrooms", 4.0), "corredor_amarelo"])
A(T("diretor mais jovem"), "carimbo", 2.0, x=1400, y=380, texto="Nº 1 MAIS JOVEM")
A(T("a maior estreia da historia da a24"), "carimbo", 1.8, x=520, y=640, texto="RECORDE DA A24", rot=6)
R(T("o que esses dois"), (1.0, 1.06))
A(T("ninguem mandou"), "versus", 2.6, a="NINGUÉM MANDOU", b="ELES QUISERAM", cor1="#ffffff", cor2="#2bd96b", tam=84)
P(T("tem autenticidade"), sfx=[["plim", 0]])

# piada 2: o outro primo
R(T("filho o seu outro primo"), (1.10, 1.14))
A(T("filho o seu outro primo"), "dialogo", T("que horror", depois=310) - T("filho o seu outro primo", depois=300) + 1.0, y=110, falas=[
    {"quem": "MÃE", "texto": "Filho, o seu outro primo criou os Backrooms. E você, o que fez?", "t": 0.0, "alto": 230},
    {"quem": "ARTUZINHO", "texto": "Ah, mamãe, eu criei um canal no YouTube!", "lado": "dir", "t": T("ah mamae eu criei", depois=307) - T("filho o seu outro primo", depois=300)},
    {"quem": "MÃE", "texto": "Você é o desgosto da família!", "t": T("voce realmente", depois=309) - T("filho o seu outro primo", depois=300)}])
R(T("ah mamae eu criei", depois=307), (1.0, 1.03), sfx=[["pop", 0]])
A(T("ah mamae eu criei", depois=307) + 0.4, "inscrever", 1.8, x=1180, y=860)
P(T("voce realmente", depois=309), sfx=[["errou", 1.0]])

# Marvel
R(T("agora olha o caminho contrario"), (1.0, 1.06), sfx=[["rebobinar", 0]])
B(T("a marvel anunciou"), [("doomsday", 26.0)], efeito_rosto=None)
A(T("a marvel anunciou"), "cardfilme", 3.4, titulo="Vingadores: A Dinastia Kang", sub="o plano original", cor="#c40000", tam=76)
R(T("o ator saiu"), (1.06, 1.12))
A(T("o plano desmoronou"), "perigo", 1.3, texto="DESMORONOU")
B(T("e o filme virou outra coisa"), [("doomsday", 124.0)], efeito_rosto=None)
A(T("virou outra coisa"), "cardfilme", 2.6, titulo="Vingadores: Doomsday", sub="dezembro de 2026", cor="#2e7d32", tam=80)
B(T("pra salvar"), ["rdj", ("doomsday", 104.0)])
A(T("robert downey"), "canto", 3.0, texto="ROBERT DOWNEY JR.")
A(T("doutor destino", depois=325) if False else T("o nosso homem de ferro"), "meme", 2.6, texto="DE HOMEM DE FERRO A DOUTOR DESTINO", tam=80)
R(T("chamaram de volta tambem"), (1.0, 1.06))
A(T("chamaram de volta tambem"), "lista", T("eu vou ver") - T("chamaram de volta tambem"), x=1100, y=160, titulo="Chamaram de volta", vel=1.6,
  itens=[{"texto": "Robert Downey Jr."}, {"texto": "Os mesmos diretores"}, {"texto": "X-Men de 20 anos atrás"}])
P(T("eu vou ver"))
R(T("mas me diz uma coisa"), (1.0, 1.06))
B(T("ou alguem numa sala"), ["sala_reuniao", "planilha"], efeito_rosto=None)
A(T("sala de reuniao"), "versus", 2.8, a="IDEIA", b="PLANILHA")
R(T("porque sabe que os vingadores"), (1.04, 1.1))
A(T("da dinheiro", depois=349), "dinheiro", 1.8, de=0, ate=2.8, fmt="US$ {v} BI", dec=1, rotulo="Vingadores: Ultimato", sfx="ding")
P(T("ai eu falo bora"))
R(T("ai nossa mas o kang"), (1.0, 1.06))
P(T("entao traz a porra"), sfx=[["impacto", 0.1]])
A(T("entao traz a porra"), "meme", 2.4, texto="TRAZ O HOMEM DE FERRO DE VOLTA!", tam=88)
R(T("traz traz esse cara"), (1.0, 1.08))
P(T("eu sei que ele morreu"), sfx=[["bonk", 0.4]])
A(T("eu sei que ele morreu"), "chave", 2.0, texto="(ele <b>morreu</b>, mas a gente dá um jeito)")
R(T("traz essa porra"), (1.12, 1.2))
P(T("entao traz pode"))

# ================= 3. ISSO DA DINHEIRO? =================
R(T("ai vem a pergunta"), (1.0, 1.06))
A(T("ah luiz mas nem todo"), "maquina", 3.0, x=120, y=110, texto="“Mas filme assim dá dinheiro?”", sfx="teclas")
P(T("confia no pai"), sfx=[["plim", 0]])
A(T("confia no pai"), "meme", 1.8, texto="CONFIA NO PAI")
R(T("caiu um pouquinho"), (1.0, 1.04))
B(T("obsession custou"), [("obsession", 12.0), "dolares"])
A(T("obsession custou"), "cardfilme", 2.4, titulo="Obsession", sub="Curry Barker · 2026", cor="#7b1fa2")
A(T("750 mil"), "dinheiro", 1.8, de=0, ate=750, fmt="US$ {v} MIL", rotulo="custou", cor="#ff5252")
A(T("e lucrou mais de 500"), "dinheiro", 2.2, de=0, ate=500, fmt="US$ {v} MI", rotulo="fez no mundo inteiro", sfx="ding")
R(T("e o filme que mais lucrou"), (1.04, 1.1))
A(T("em toda a historia", depois=386), "carimbo", 1.8, x=1400, y=380, texto="RECORDE HISTÓRICO")
B(T("a odysseyia") if any(t[0] == "odysseyia" for t in TOK) else T("um poema grego"), [("odisseia", 68.0), "homero"])
A(T("teve a maior estreia da carreira"), "dinheiro", 2.4, de=0, ate=260, fmt="US$ {v} MI", rotulo="no 1º fim de semana", sfx="ding")
R(T("deixa eu ajeitar"), (1.0, 1.04))
R(T("as pessoas nao pararam"), (1.04, 1.1))
A(T("as pessoas nao pararam"), "chave", 2.2, texto="As pessoas <b>não pararam</b> de ir ao cinema")
B(T("pra ver um filme que vai estar"), ["celular", "sofa"], efeito_rosto=None)
B(T("da pra ver um filme em qualquer sofa"), ["sofa"], efeito_rosto=None)
P(T("voce so sai de casa"))
A(T("voce so sai de casa"), "chave", 2.6, texto="Só sai de casa pelo que <b>não cabe no sofá</b>")

# ================= 4. E O BRASIL =================
R(T("e nao e so la fora"), (1.0, 1.06))
B(T("em 2025 ainda estou aqui"), [("ainda", 38.0), "fernanda_torres", "oscar"])
A(T("ainda estou aqui") + 1.2, "polaroid", 3.4, src="__FOTO__fernanda_torres", legenda="Fernanda Torres", x=1320, y=120, w=480, h=300, rot=5)
A(T("em 2025 ainda estou aqui"), "cardfilme", 3.4, titulo="Ainda Estou Aqui", sub="Walter Salles · Oscar de Filme Internacional", cor="#2e7d32", tam=82)
B(T("um filme sobre uma familia"), [("ainda", 102.0), "oscar"])
P(T("ate porque se voce quiser"), sfx=[["boing", 1.4]])
B(T("melhor voce ficar com"), [("oppenheimer", 36.0), "trinity"], efeito_rosto=None, sfx=(("impacto", 0.1),))
B(T("e logo depois veio o agente"), [("agente", 20.0), "wagner_moura"])
A(T("e logo depois veio o agente"), "cardfilme", 3.0, titulo="O Agente Secreto", sub="Kleber Mendonça Filho · 2025", cor="#ffd400", tam=82)
B(T("virou o filme brasileiro"), [("agente", 100.0), "oscar"])
A(T("mais indicado"), "contador", 2.2, x=1450, y=380, de=0, ate=4, rotulo="INDICAÇÕES", tc=0.6)
A(T("2 milhoes"), "dinheiro", 2.2, de=0, ate=2, fmt="{v} MILHÕES", rotulo="de pessoas no cinema", cor="#ffd400", tc=0.6)
P(T("saiu sem estatueta"), sfx=[["errou", 0.5]])
R(T("mas olha o que ele provou"), (1.0, 1.06))
A(T("o brasileiro vai ao cinema"), "chave", 2.6, texto="Brasileiro vai ver filme brasileiro? <b>Sim.</b>")
P(T("quando alguem faz com vontade"), sfx=[["plim", 0]])
R(T("agora parece que os filmes"), (1.0, 1.06))
P(T("ah e brasileiro"))
A(T("ah e brasileiro"), "meme", 1.8, texto="“AH, É BRASILEIRO?”")
R(T("entao coloca merda"), (1.04, 1.1))
A(T("coloca um monte de gente"), "lista", T("que que da") - T("coloca um monte de gente"), x=1080, y=170, titulo="A receita", vel=1.8,
  itens=[{"texto": "Gente falando nada com nada"}, {"texto": "Diálogo horroroso"}, {"texto": "Sotaque forçado"}])
P(T("que que da"), sfx=[["errou", 0.8]])
A(T("ninguem vai assistir"), "carimbo", 1.6, x=1400, y=420, texto="NINGUÉM ASSISTE")

# ================= VIRADA =================
R(T("entao ta tudo resolvido"), (1.0, 1.06))
A(T("final feliz"), "chave", 1.8, texto="Final <b>feliz</b>?")
B(T("so que em fevereiro"), ["paramount"], efeito_rosto=None, sfx=(("impacto", 0.1),))
A(T("so que em fevereiro"), "cardfilme", 3.4, titulo="Paramount + Warner", sub="acordo de fevereiro de 2026", cor="#1565c0", tam=82)
B(T("o estudio que bancou"), ["warner", ("barbie", 6.0)], efeito_rosto=None)
A(T("o estudio que bancou"), "lista", 3.6, x=1180, y=150, titulo="Warner bancou", vel=0.55,
  itens=[{"texto": "Duna"}, {"texto": "Batman"}, {"texto": "Barbie"}, {"texto": "Pecadores"}])
B(T("o negocio esta travado"), ["tribunal"], efeito_rosto=None)
A(T("travado na justica"), "carimbo", 1.8, x=1400, y=380, texto="TRAVADO NA JUSTIÇA")
R(T("e quando dois gigantes"), (1.0, 1.06))
P(T("o primeiro corte"))
A(T("os filmes arriscados"), "perigo", 1.3, texto="CORTE")
R(T("so o que e garantido"), (1.04, 1.1))
A(T("so o que e garantido"), "lista", 3.4, x=1180, y=200, titulo="Fica só", vel=0.6, itens=[{"texto": "Continuação"}, {"texto": "Remake"}, {"texto": "Marca conhecida"}])
R(T("so que ate isso acaba"), (1.0, 1.06))
B(T("nao sobra desenho"), [("barbie", 10.0)], efeito_rosto=None)
B(T("jogo para virar filme"), ["controle_game"], efeito_rosto=None)
B(T("anos 80"), ["vhs"], efeito_rosto=None)

# ================= FINAL RUIM + SAIDA =================
P(T("e ai que chega o final ruim"), sfx=[["subida", 0.2]])
R(T("as ideias velhas"), (1.0, 1.06))
B(T("nao precisa mais de ideia"), ["robo", "codigo"], efeito_rosto="pb", efeito=None, sfx=(("impacto", 0.1),))
A(T("nao precisa mais de ideia"), "ia", 2.6, texto="IA", sub="o final ruim")
R(T("nem de diretor"), (1.0, 1.08), efeito="pb")
A(T("nem de diretor"), "lista", T("enfim galera") - T("nem de diretor"), x=1180, y=180, vel=0.7,
  itens=[{"texto": "Diretor", "ok": False}, {"texto": "Fotógrafo", "ok": False}, {"texto": "Ator", "ok": False}, {"texto": "Ninguém", "ok": False}])
R(T("enfim galera"), (1.0, 1.05))
R(T("se gostaram"), (1.04, 1.1))
A(T("se inscrever"), "inscrever", 2.2, x=1180, y=860)
P(T("e isso galera valeu"))
A(T("fui"), "meme", 1.4, texto="FUI!", y=160)

# ---------------- monta as cenas ----------------
cortes.sort(key=lambda c: c[0])
cenas = []
for k, (t, tipo, d) in enumerate(cortes):
    fim = cortes[k + 1][0] if k + 1 < len(cortes) else FIM
    if fim - t < 0.05: continue
    c = {"ini": round(t, 3), "fim": round(fim, 3), "tipo": tipo}
    for kk, v in d.items():
        if v is not None: c[kk] = v
    cenas.append(c)
# rosto parado mais de 4 s: alterna enquadramento (aberto / fechado) a cada ~3 s para manter movimento
final = []
for c in cenas:
    dur = c["fim"] - c["ini"]
    if c["tipo"] != "rosto" or dur <= 4.2: final.append(c); continue
    n = int(dur // 3.0); passo = dur / n
    for i in range(n):
        q = dict(c, ini=round(c["ini"] + i * passo, 3), fim=round(c["ini"] + (i + 1) * passo, 3))
        if i % 2 == 1: q["zoom"] = [1.12, 1.17]
        if i > 0: q.pop("sfx", None)
        final.append(q)
cenas = final
# rosto: o bone fica perto do topo do quadro nesta gravacao; o zoom parte do TOPO (bone sempre inteiro, regra do canal)
for c in cenas:
    if c["tipo"] == "rosto": c["foco"] = [0.5, 0.0]
# fotos locais nas artes polaroid
for a in artes:
    if str(a.get("src", "")).startswith("__FOTO__"):
        a["src"] = "file://" + os.path.join(AQUI, "midia/fotos", a["src"][8:] + ".jpg")
artes.sort(key=lambda a: a["ini"])
plano = {"fala": "build/fala.mp4", "fontes": {k: v for k, v in TRAILERS.items() if existe(v)},
         "inicio": 0.0, "fim": FIM, "trilha": {"arquivo": "midia/som/trilha.wav", "volume_db": -21},
         "efeitos_dir": "midia/som/efeitos", "cenas": cenas, "artes": artes}
json.dump(plano, open(os.path.join(AQUI, "plano_video.json"), "w"), ensure_ascii=False, indent=1)
tipos = {}
for c in cenas: tipos[c["tipo"]] = tipos.get(c["tipo"], 0) + c["fim"] - c["ini"]
print(len(cenas), "cenas,", len(artes), "artes; duracao", FIM, "s;",
      ", ".join(f"{k} {v / FIM * 100:.0f}%" for k, v in tipos.items()),
      "; plano medio", round(FIM / len(cenas), 2), "s")
