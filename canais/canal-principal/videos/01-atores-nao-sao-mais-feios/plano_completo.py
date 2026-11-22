"""Plano do vídeo inteiro: cenas por trecho, destaques animados, música por parte e som.

python plano_completo.py --plano            -> grava build/plano.json e build/spec_completo.json
python plano_completo.py --artes            -> renderiza artes por bloco (build/artes/bNN.mov)
python plano_completo.py --musica --som     -> música por parte + mix completo (build/som_completo.wav)
python plano_completo.py --video [--bloco N]-> monta blocos e junta em out/video.mp4
"""
import json, re, sys, os, subprocess, pathlib
sys.path.insert(0, "ferramentas")
from legendas import grupos

V = "canais/canal-principal/videos/01-atores-nao-sao-mais-feios/"
TL = json.load(open(V + "timeline.json"))
PAL = TL["palavras"]
BLOCOS = TL["blocos"]
FIM = BLOCOS[-1]["fim"] + 1.2


def norm(w): return re.sub(r"[^\wà-ú]", "", w.lower())


def em(palavra, depois=0.0):
    """Início da primeira palavra que começa com `palavra` depois do tempo dado."""
    p = norm(palavra)
    for w in PAL:
        if w["s"] >= depois - 0.05 and norm(w["w"]).startswith(p):
            return round(w["s"], 3)
    raise ValueError(f"palavra não achada: {palavra} depois de {depois}")


# ---------------- trechos de cenas ----------------
M = ["twisters-2024", "the-batman-2022", "deadpool-wolverine-2024", "homem-aranha-2021", "creed-2015", "chalamet-a-complete-unknown"]
O = ["rocky-1976", "taxi-driver-1976", "poderoso-chefao-1972", "era-uma-vez-no-oeste-1968", "ghostbusters-1984",
     "batman-1989", "star-wars-1977", "tres-homens-em-conflito-1966", "homem-aranha-2002", "x-men-2000"]
RK, TX, TB, B89, CH, TW = "rocky-1976", "taxi-driver-1976", "the-batman-2022", "batman-1989", "chalamet-a-complete-unknown", "twisters-2024"
DH = "die-hard-1988"
ESC = {"efeito": "escurece"}

SEG = [  # (ini, fim, filmes, opções)
 (32.0, 37.0, O, {}), (37.0, 39.5, [DH], {}), (39.5, 52.7, O, {}),
 (52.7, 62.4, M, {}), (62.4, 69.2, "ARTE", {}), (69.2, 74.0, M, {}), (74.0, 78.5, M, {"efeito": "lavado"}),
 (78.5, 84.99, O, {}),
 # parte 1
 (84.99, 90.0, M, {}), (90.0, 99.6, O, {}), (99.6, 105.2, M, {}), (105.2, 108.3, "ARTE", {}),
 (108.3, 116.1, [RK], {}), (116.1, 125.6, [CH], {}), (125.6, 130.3, [TW, DH], {}),
 (130.3, 134.6, [DH], {}), (134.6, 138.4, [TW], {}), (138.4, 143.6, [DH], {}), (143.6, 149.3, [TW], {}),
 (149.3, 150.6, "ARTE", {}), (150.6, 155.0, [B89], {}), (155.0, 157.9, [TB], {}), (157.9, 164.8, [B89], {}),
 (164.8, 174.8, [TB], {}), (174.8, 183.474, [TB, B89], ESC),
 # parte 2
 (183.474, 197.5, O, {}), (197.5, 233.0, ["era-uma-vez-no-oeste-1968"], {}),
 (233.0, 247.5, ["poderoso-chefao-1972"], {}), (247.5, 256.9, ["fuga-de-nova-york-1981", "rocky-1976"], {}),
 (256.9, 263.2, ["x-men-2000"], {}), (263.2, 275.2, ["deadpool-wolverine-2024"], {}),
 (275.2, 293.574, ["cidade-de-deus-2002"], {}),
 # CTA
 (293.574, 303.468, O, ESC),
 # parte 3
 (303.468, 307.1, O, {}), (307.1, 320.2, ["bebe-de-rosemary-1968"], {"alvo": 2.6}), (320.2, 326.8, "ARTE", {}),
 (326.8, 334.6, ["bebe-de-rosemary-1968"], {"alvo": 2.6}), (334.6, 349.8, ["star-wars-1977"], {}),
 (349.8, 383.397, [TX], {}),
 # parte 4
 (383.397, 388.7, M, {}), (388.7, 400.6, [RK], {}), (400.6, 407.7, ["creed-2015"], {}),
 (407.7, 419.8, ["homem-aranha-2002"], {}), (419.8, 429.6, ["homem-aranha-2021"], {}), (429.6, 435.0, "ARTE", {}),
 (435.0, 443.8, ["tres-homens-em-conflito-1966"], {}), (443.8, 456.978, M, {}),
 # parte 5
 (456.978, 458.6, M, ESC), (458.6, 470.6, "ARTE", {}), (470.6, 499.5, M, {}), (499.5, 510.5, M, {}),
 (510.5, 521.8, M, ESC), (521.8, 540.8, ["invasores-de-corpos-1978"], {}),
 (540.8, 543.2, ["deadpool-wolverine-2024"], {}), (543.2, 548.4, M, {}), (548.4, 555.558, M, {}),
 # parte 6
 (555.558, 566.3, M, {}), (566.3, 584.8, [CH, TW, TB], {}), (584.8, 593.0, M, {}),
 (593.0, 599.3, ["era-uma-vez-no-oeste-1968", "ghostbusters-1984", "tres-homens-em-conflito-1966"], {}),
 (599.3, 603.461, M, {"efeito": "lavado"}),
 # final
 (603.461, 623.9, M, {}), (623.9, 633.2, [RK, "tres-homens-em-conflito-1966", TX, "era-uma-vez-no-oeste-1968"], {"alvo": 1.6}),
 (633.2, 634.5, "ARTE", {}), (634.5, FIM, O, ESC),
]

# ---------------- destaques ----------------
def E(tipo, ini, fim, **k): return {"tipo": tipo, "ini": round(ini, 3), "fim": round(fim, 3), **k}

def destaques():
    e = []
    # antes que me cancelem
    e += [E("carimbo", em("calma", 32), 35.6, texto="CALMA!", rot=-6),
          E("etq", em("bruce", 36), 39.4, html="BRUCE WILLIS &middot; <em>NÃO É FEIO</em>", x=1150, y=260),
          E("check", 41.6, 49.6, titulo="ROSTO DE ANTIGAMENTE", itens=[{"t": "Sem personal trainer", "s": em("personal", 41)},
            {"t": "Sem nutricionista", "s": em("nutricionista", 45)}, {"t": "Sem cirurgião plástico", "s": em("cirurgião", 46)}]),
          E("carimbo", em("lotérica", 50), 52.7, texto="100% GENTE", rot=7),
          E("maquina", 52.9, 58.5, linhas=[{"t": "CABELO PERFEITO", "s": em("cabelo", 52)}, {"t": "PELE PERFEITA", "s": em("pele", 55)},
            {"t": "CORPO DE REVISTA", "s": em("corpo", 56)}]),
          E("flash", em("modelo", 58), em("modelo", 58) + 0.3), E("letreiro", em("modelo", 58), 62.3, texto="MODELO DE PERFUME"),
          E("carimbo", em("mostrar", 62), 68.9, texto="ROSTO CONFIDENCIAL", rot=-7),
          E("filtro", 74.1, 78.4, texto="🎨 FILTRO: STREAMING"),
          E("numero", em("antes", 78.5), 82.0, de=2024, ate=1999, sufixo="OU ANTES", dur=0.9)]
    # parte 1
    e += [E("maquina", 90.1, 96.3, linhas=[{"t": "FUMAM MENOS", "s": em("fumam", 90)}, {"t": "COMEM MELHOR", "s": em("comem", 91)},
            {"t": "VÃO AO MÉDICO", "s": em("médico", 92)}, {"t": "SE VESTEM MAIS JOVEM", "s": em("vestem", 93)}]),
          E("vs", 96.4, 105.0, esq="VOVÔ", esqs="40 ANOS (PARECIA 60)", dir="VOCÊ", dirs="40 ANOS + TÊNIS DE CORRIDA"),
          E("flash", em("comparações", 105), em("comparações", 105) + 0.3),
          E("letreiro", em("comparações", 105), 108.2, texto="AQUI É QUE DÓI"),
          E("numero", em("29", 108), 111.6, de=0, ate=29, sufixo="ANOS"),
          E("check", 112.8, 116.1, titulo="CURRÍCULO DO ROCKY", itens=[{"t": "Geladeira no 3º andar", "s": em("geladeira", 112)},
            {"t": "Sem elevador", "s": em("elevador", 113)}]),
          E("etq", em("timothée", 116), 119.7, html="TIMOTHÉE CHALAMET &middot; <em>29 ANOS</em>", x=1100, y=240),
          E("carimbo", em("poeta", 122), 125.6, texto="POETA FRANCÊS TRISTE", rot=-6),
          E("vs", 128.0, 138.0, esq="BRUCE WILLIS", esqs="33 &middot; DURO DE MATAR", dir="GLEN POWELL", dirs="35 &middot; TWISTERS"),
          E("check", 138.5, 143.6, titulo="O BRUCE TINHA", itens=[{"t": "Entradas", "s": em("entradas", 138)},
            {"t": "Barba por fazer", "s": em("barba", 139)}, {"t": "Cara de quem dormiu no sofá", "s": em("dormiu", 140)}]),
          E("carimbo", em("comercial", 144), 149.2, texto="+2 ANOS (JURA?)", rot=6),
          E("flash", 149.4, 149.7), E("letreiro", 149.4, 150.6, texto="BATMAN"),
          E("numero", em("37", 150), 154.7, de=0, ate=37, sufixo="ANOS · 1989"),
          E("etq", em("pattinson", 154), 157.8, html="ROBERT PATTINSON &middot; <em>35 ANOS</em>", x=1100, y=240),
          E("check", 157.9, 164.7, titulo="KEATON", itens=[{"t": "Rugas na boca", "s": em("rugas", 158)},
            {"t": "Cabelo recuando", "s": em("cabelo", 159)}, {"t": "Barba sem planejamento", "s": em("barbinha", 161)}]),
          E("carimbo", em("semanas", 165), 169.9, texto="3 SEMANAS SEM DORMIR", rot=-6),
          E("filtro", em("queixo", 170), 174.6, texto="✨ MODO: SPA EM BALI"),
          E("flash", em("atropelado", 179), em("atropelado", 179) + 0.3),
          E("letreiro", em("atropelado", 179), 183.3, texto="ATROPELADO PELO BATMÓVEL")]
    # parte 2
    e += [E("maquina", 189.7, 195.0, linhas=[{"t": "NARIZ GRANDE", "s": em("nariz", 189)}, {"t": "TESTA ENORME", "s": em("testa", 190)},
            {"t": "OLHO CAÍDO", "s": em("olho", 191)}, {"t": "CABELO INDO EMBORA", "s": em("cabelo", 192)}]),
          E("carimbo", em("informação", 195), 197.5, texto="ISSO É INFORMAÇÃO", rot=-5),
          E("etq", em("abertura", 197), 202.6, html="ERA UMA VEZ NO OESTE &middot; <em>1968</em>", x=1080, y=240),
          E("numero", em("nenhum", 202), 205.2, de=3, ate=0, sufixo="SOBREVIVENTES"),
          E("check", 207.4, 216.2, titulo="OS 3 PISTOLEIROS", itens=[{"t": "Cabelo batendo na cara", "s": em("cabelo", 207)},
            {"t": "Barba até o pescoço", "s": em("barba", 209)}, {"t": "Queixo quadrado", "s": em("queixo", 212)}]),
          E("numero", em("15", 222), 228.5, de=0, ate=15, sufixo="MINUTOS SEM DIÁLOGO"),
          E("carimbo", em("briefing", 229), 233.0, texto="BRIEFING: 3 PÁGINAS", rot=6),
          E("etq", em("poderoso", 232), 239.5, html="O PODEROSO CHEFÃO &middot; <em>1972</em>", x=1080, y=240),
          E("maquina", 240.0, 247.3, linhas=[{"t": "CORTE DE CABELO", "s": em("corte", 240)}, {"t": "TERNO", "s": em("terno", 241)},
            {"t": "TAMANHO DA BARRIGA", "s": em("barriga", 242)}]),
          E("etq", em("kurt", 248), 253.5, html="KURT RUSSELL &middot; <em>FUGA DE NOVA YORK</em>", x=1050, y=240),
          E("carimbo", em("tanquinho", 254), 258.0, texto="TANQUINHO: NÃO", rot=-6),
          E("vs", em("hugh", 258), 266.0, esq="WOLVERINE 2000", esqs="UM CARA FORTE", dir="WOLVERINE 2024", dirs="UM PROJETO"),
          E("check", 266.5, 275.2, titulo="WOLVERINE 2024", itens=[{"t": "Planilha de frango", "s": em("frango", 266)},
            {"t": "Batata-doce", "s": em("batata", 268)}, {"t": "Equipe de 8 pessoas", "s": em("equipe", 270)}]),
          E("flash", em("cidade", 276), em("cidade", 276) + 0.3), E("letreiro", em("cidade", 276), 279.0, texto="CIDADE DE DEUS"),
          E("etq", em("comunidades", 281), 286.0, html="ELENCO DAS <em>COMUNIDADES DO RIO</em>", x=1060, y=240),
          E("carimbo", em("esquina", 290), 293.5, texto="SAIU DA ESQUINA", rot=-6)]
    # CTA
    e += [E("insc", 294.0, 300.0, clique=em("inscreve", 297) - 294.0 + 0.2),
          E("carimbo", em("filtro", 300), 303.3, texto="SEM FILTRO DE BELEZA", rot=5)]
    # parte 3
    e += [E("flash", em("daí", 303), em("daí", 303) + 0.3), E("letreiro", em("daí", 303), 306.9, texto="E DAÍ?"),
          E("etq", em("mia", 307), 309.9, html="MIA FARROW &middot; <em>O BEBÊ DE ROSEMARY</em>", x=1040, y=240),
          E("maquina", 310.0, 316.2, linhas=[{"t": "CABELO CURTINHO", "s": em("cabelo", 310)}, {"t": "MAIS PÁLIDA", "s": em("pálida", 312)},
            {"t": "MAIS MAGRA", "s": em("magra", 313)}, {"t": "MAIS APAGADA", "s": em("apagada", 314)}]),
          E("carimbo", em("margot", 320), 323.1, texto="MARGOT ROBBIE?", rot=-5),
          E("filtro", em("tendência", 323), 326.8, texto="📱 TENDÊNCIA NO TIKTOK"),
          E("vs", 334.7, 345.4, esq="FAMÍLIA DO LUKE", esqs="GENTE DO INTERIOR", dir="OFICIAIS DO IMPÉRIO", dirs="NUNCA RIRAM"),
          E("carimbo", em("explodir", 346), 349.7, texto="VAI EXPLODIR UM PLANETA", rot=6),
          E("etq", em("taxi", 350), 355.4, html="TAXI DRIVER &middot; <em>1976</em>", x=1150, y=240),
          E("check", 355.7, 365.0, titulo="OS TAXISTAS", itens=[{"t": "Careca com cabelo atrás", "s": em("careca", 355)},
            {"t": "Barba e óculos redondos", "s": em("barba", 358)}, {"t": "Olheira e olho vermelho", "s": em("olheira", 362)}]),
          E("carimbo", em("aceita", 371), 373.3, texto="ACEITA PIX?", rot=-7),
          E("flash", em("imersão", 379), em("imersão", 379) + 0.3), E("letreiro", em("imersão", 379), 383.2, texto="IMERSÃO")]
    # parte 4
    e += [E("carimbo", em("machucado", 385), 388.6, texto="NINGUÉM SE MACHUCA", rot=-5),
          E("numero", em("15", 389), 391.5, de=0, ate=15, sufixo="ROUNDS"),
          E("check", 391.6, 400.5, titulo="ROCKY NO FIM", itens=[{"t": "Encharcado", "s": em("encharcado", 391)},
            {"t": "Cabelo grudado", "s": em("cabelo", 392)}, {"t": "Rosto inchado", "s": em("inchado", 394)}, {"t": "Sangue", "s": em("sangue", 395)}]),
          E("etq", em("creed", 400), 403.6, html="CREED &middot; <em>2015</em>", x=1250, y=240),
          E("filtro", em("suorzinho", 403), 407.7, texto="✨ SUOR ELEGANTE: ATIVADO"),
          E("maquina", 407.8, 419.6, linhas=[{"t": "UNIFORME DESTRUÍDO", "s": em("uniforme", 409)}, {"t": "MÁSCARA RASGADA", "s": em("máscara", 411)},
            {"t": "SUJEIRA, SUOR, HEMATOMA", "s": em("sujeira", 416)}]),
          E("vs", 420.0, 429.5, esq="2002", esqs="MÁSCARA RASGADA", dir="2021", dirs="2 ARRANHÕES DE DESIGNER"),
          E("carimbo", em("dedinho", 430), 435.0, texto="QUINA 1 × 0 EU", rot=-6),
          E("etq", em("clint", 436), 440.8, html="CLINT EASTWOOD &middot; <em>1966</em>", x=1150, y=240),
          E("carimbo", em("irreconhecível", 441), 443.8, texto="IRRECONHECÍVEL", rot=6),
          E("filtro", em("manchinha", 444), 448.2, texto="✨ SUJEIRA DECORATIVA"),
          E("flash", em("perfeito", 452.5), em("perfeito", 452.5) + 0.3),
          E("letreiro", em("perfeito", 452.5), 456.9, texto="PERFEITO = SEM GRAÇA")]
    # parte 5
    e += [E("carimbo", 457.2, 458.6, texto="POR QUÊ?", rot=5),
          E("tweet", 458.7, 470.5, nome="Raquel S. Benedict", user="ensaio &middot; 2021",
            texto="“Todo mundo é bonito e ninguém tem tesão.”", likes="o nome é esse mesmo"),
          E("carimbo", em("investimento", 472), 477.5, texto="CORPO = INVESTIMENTO", rot=-6),
          E("maquina", 480.1, 485.8, linhas=[{"t": "PELE PERFEITA", "s": em("pele", 480)}, {"t": "MANDÍBULA MARCADA", "s": em("mandíbula", 481)},
            {"t": "DENTE BRANCO", "s": em("dente", 482)}]),
          E("etq", em("atriz", 488), 493.8, html="ATRIZES: <em>PROIBIDO ENVELHECER</em>", x=1000, y=240),
          E("flash", em("seguro", 497), em("seguro", 497) + 0.3),
          E("letreiro", em("seguro", 497), 499.5, texto="ROSTO SEGURO = SEM SURPRESA"),
          E("check", 501.1, 508.2, titulo="DÁ PRA CONSERTAR", itens=[{"t": "A entrada", "s": em("entrada", 501)},
            {"t": "O dente", "s": em("dente", 502)}, {"t": "A pele", "s": em("pele", 503)}]),
          E("tweet", 514.9, 517.4, nome="cinéfilo cansado", user="@saudade_dos_80", texto="que saudade de ator com dente normal", likes="48 mil"),
          E("tweet", 517.5, 521.7, nome="maria vê filmes", user="@mariavefilmes", texto="é chato demais todo mundo ter o mesmo dente e o mesmo corpo", likes="31 mil"),
          E("etq", em("donald", 525), 531.0, html="DONALD SUTHERLAND &middot; <em>40 E POUCOS</em>", x=1000, y=240),
          E("flash", em("quem", 538), em("quem", 538) + 0.3),
          E("letreiro", em("quem", 538), 540.8, texto="QUEM FARIA HOJE?"),
          E("carimbo", em("bigode", 541), 543.2, texto="BIGODE FALSO", rot=-6),
          E("filtro", em("chris", 543), 548.3, texto="👓 MODO: HOMEM COMUM"),
          E("numero", em("5", 552), 555.5, de=0, ate=5, sufixo="DA MANHÃ · ACADEMIA")]
    # parte 6
    e += [E("flash", em("iphone", 557), em("iphone", 557) + 0.3), E("letreiro", em("iphone", 557), 561.3, texto="CARA DE IPHONE"),
          E("filtro", em("limpinho", 561), 566.2, texto="📸 MODO RETRATO: LIGADO"),
          E("etq", em("época", 567), 569.3, html="FILME DE ÉPOCA &middot; <em>1800 E POUCOS</em>", x=1000, y=240),
          E("check", 569.4, 576.8, titulo="O ATOR DE ÉPOCA", itens=[{"t": "Corte de barbearia de shopping", "s": em("barbearia", 570)},
            {"t": "Dente de clareamento", "s": em("clareamento", 574)}]),
          E("carimbo", em("escova", 578), 584.7, texto="NUNCA VIU ESCOVA", rot=6),
          E("maquina", 588.4, 593.0, linhas=[{"t": "LUZ PERFEITA", "s": em("luz", 588)}, {"t": "CENÁRIO PERFEITO", "s": em("cenário", 589)},
            {"t": "ROUPA LIMPINHA", "s": em("roupa", 591)}]),
          E("filtro", em("streaming", 600), 603.4, texto="🎨 FILTRO: STREAMING")]
    # final
    e += [E("flash", em("medo", 613), em("medo", 613) + 0.3), E("letreiro", em("medo", 613), 615.4, texto="MEDO DE ARRISCAR"),
          E("numero", em("dinheiro", 615), 619.4, de=0, ate=100, sufixo="% SEGURO"),
          E("maquina", 624.0, 630.0, linhas=[{"t": "NÃO SÃO MAIS FEIOS", "s": em("feios", 624)}, {"t": "NEM SUJOS", "s": em("sujos", 626)},
            {"t": "NEM MACHUCADOS", "s": em("machucados", 627)}]),
          E("carimbo", em("perfeito", 631), 633.2, texto="TODO MUNDO PERFEITO", rot=-5),
          E("flash", em("problema", 633), em("problema", 633) + 0.3),
          E("letreiro", em("esse", 633.2), 634.5, texto="ESSE É O PROBLEMA"),
          E("tweet", 634.6, 640.0, nome="Você", user="@nos_comentarios", texto="Qual ator de hoje ainda tem cara de gente de verdade?", likes="comenta aí 👇"),
          E("etq", em("diretor", 640), 644.1, html="DIRETOR DE ELENCO? <em>TÔ DISPONÍVEL</em>", x=900, y=240),
          E("carimbo", em("mostrar", 646), FIM, texto="ROSTO CONFIDENCIAL", rot=-7)]
    return e


def spec():
    leg = grupos(PAL, 32.4, FIM, 4, {"Glenn": "Glen", "Farrell": "Farrow", "Deniro": "De Niro", "Tobi": "Tobey",
                                       "picks": "Pix", "Oculus": "óculos", "adjuvante": "coadjuvante"})
    # junta "com o" + "coadjuvante" (erro do transcritor) e números que viraram dígitos ficam como estão
    for g in leg:
        ws = g["palavras"]
        for i in range(len(ws) - 1):
            if ws[i]["w"].lower() == "com" and ws[i + 1]["w"] == "o" and i + 2 < len(ws) and ws[i + 2]["w"] == "coadjuvante":
                del ws[i:i + 2]; break
    return {"duracao": FIM, "legenda": leg, "elementos": destaques()}


# ---------------- música por parte ----------------
FAIXAS = [  # (ini, fim, estilo, bpm, tom, seed)
 (32.0, 184.5, "curioso", 100, 0, 1), (183.0, 294.5, "tenso", 90, 0, 2), (293.0, 384.0, "curioso", 94, -3, 3),
 (382.5, 458.0, "tenso", 100, 2, 4), (456.5, 556.5, "curioso", 96, 2, 5), (555.0, 604.5, "tenso", 84, -2, 6),
 (603.0, FIM + 1.5, "epico", 80, 0, 7)]


def musicas():
    out = []
    for i, (a, b, est, bpm, tom, seed) in enumerate(FAIXAS):
        f = V + f"build/musica_{i}.wav"
        if not os.path.exists(f):
            subprocess.run(["python3", "ferramentas/musica.py", f, str(b - a), "--estilo", est, "--bpm", str(bpm),
                            "--tom", str(tom), "--seed", str(seed)], check=True)
        out.append((f, a))
    return out


def sfx_de(elementos):
    FX = V + "build/sfx/"
    s = []
    for e in elementos:
        t = e["ini"]; tp = e["tipo"]
        if tp == "carimbo": s.append((FX + "carimbo.wav", t, -3))
        elif tp == "numero": s += [(FX + "tique.wav", t + k * 0.12, -8) for k in range(5)] + [(FX + "ding.wav", t + 0.6, -10)]
        elif tp == "check": s += [(FX + "whoosh.wav", t, -10)] + [(FX + "pop.wav", it["s"], -6) for it in e["itens"]]
        elif tp == "etq": s.append((FX + "pop.wav", t + 0.12, -7))
        elif tp == "filtro": s.append((FX + "ding.wav", t, -9))
        elif tp == "flash": s += [(FX + "riser.wav", t - 1.4, -13), (FX + "clarao.wav", t, -5)]
        elif tp == "vs": s += [(FX + "whoosh.wav", t, -8), (FX + "impacto.wav", t + 0.3, -8)]
        elif tp == "tweet": s.append((FX + "pop.wav", t, -6))
        elif tp == "insc": s += [(FX + "pop.wav", t, -6), (FX + "tique.wav", t + e.get("clique", 1.2), -4)]
        elif tp == "maquina":
            for l in e["linhas"]:
                s += [(FX + "maquina.wav", l["s"] + i / 20, -12) for i in range(len(l["t"]))]
    return s


def whooshs(cenas, ini):
    FX = V + "build/sfx/"; t = ini; s = []
    for c in cenas[:-1]:
        t += c["dur"]; s.append((FX + "whoosh.wav", t - 0.12, -17))
    return s


if __name__ == "__main__":
    a = sys.argv
    if "--plano" in a:
        sys.path.insert(0, "ferramentas")
        from planejar import Escolhedor
        es = Escolhedor(V + "build/indice_cenas.json", V + "midia/trailers", bloqueadas=V + "build/bloqueadas.json")
        cenas = []
        for ini, fim, filmes, op in SEG:
            cenas += es.segmento(ini, fim, filmes, op)
        json.dump(cenas, open(V + "build/plano.json", "w"), ensure_ascii=False, indent=0)
        sp = spec(); json.dump(sp, open(V + "build/spec_completo.json", "w"), ensure_ascii=False)
        print(len(cenas), "cenas,", round(sum(c["dur"] for c in cenas), 2), "s;", len(sp["elementos"]), "destaques;",
              sum(c["src"] == "ARTE" for c in cenas), "fundos de arte")
    if "--musica" in a:
        musicas(); print("músicas ok")
    if "--som" in a:
        from mixar import mixar
        cenas = json.load(open(V + "build/plano.json"))
        sp = json.load(open(V + "build/spec_completo.json"))
        mixar(V + "narracao.wav", V + "build/som_resto.wav", 32.0, FIM, musicas=musicas(),
              sfx=sfx_de(sp["elementos"]) + whooshs(cenas, 32.0))
        print("som ok")
    if "--video" in a:
        from montar import base
        cenas = json.load(open(V + "build/plano.json"))
        b = V + "build/base_resto.mp4"
        if "--refaz-base" in a or not os.path.exists(b):
            base(cenas, b); print("base ok")
        # artes em 2 pedaços: a1 começa em 32 s (0 no resto), a2 em 340 s (308 s no resto)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", b, "-i", V + "build/artes/a1.mov",
                        "-itsoffset", "308", "-i", V + "build/artes/a2.mov",
                        "-filter_complex", "[0][1]overlay=0:0:eof_action=pass[x];[x][2]overlay=0:0:eof_action=pass,format=yuv420p[v]",
                        "-map", "[v]", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-r", "30",
                        V + "build/video_resto.mp4"], check=True)
        print("resto ok")
        # gancho (já aprovado) só vídeo, com a legenda menor
        from montar import base as _b
        import importlib.util
        spec_g = importlib.util.spec_from_file_location("pg", V + "plano_gancho.py"); pg = importlib.util.module_from_spec(spec_g)
        sys.argv = ["x"]; spec_g.loader.exec_module(pg)
        _b(pg.CENAS, V + "build/base_gancho.mp4")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", V + "build/base_gancho.mp4", "-i", V + "build/artes_gancho.mov",
                        "-filter_complex", "[0][1]overlay=0:0,format=yuv420p[v]", "-map", "[v]", "-c:v", "libx264",
                        "-preset", "medium", "-crf", "18", "-r", "30", V + "build/video_gancho.mp4"], check=True)
        # junta vídeo + som
        (pathlib.Path(V) / "build/vl.txt").write_text(f"file '{os.path.abspath(V + 'build/video_gancho.mp4')}'\n"
                                                      f"file '{os.path.abspath(V + 'build/video_resto.mp4')}'\n")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", V + "build/som_gancho.wav", "-i", V + "build/som_resto.wav",
                        "-filter_complex", "[0][1]concat=n=2:v=0:a=1[a]", "-map", "[a]", V + "build/som_final.wav"], check=True)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", V + "build/vl.txt",
                        "-i", V + "build/som_final.wav", "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest", "-movflags", "+faststart",
                        V + "out/video.mp4"], check=True)
        print("VIDEO FINAL ok")
