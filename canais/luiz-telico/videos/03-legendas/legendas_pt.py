#!/usr/bin/env python3
"""Legendas em portugues SO para as partes em ingles do video 03 (traducao feita a partir da transcricao).
Gera out/legendas_pt.srt (para subir no YouTube) e build/legendas_pt.ass (para queimar no video)."""
import os

AQUI = os.path.dirname(os.path.abspath(__file__))
L = [  # (inicio, fim, texto em portugues)
    (35.56, 37.06, "Quer dizer, é uma bagunça."),
    (37.18, 38.64, "Quando ele me deu um soco, eu fiquei nervoso."),
    (55.66, 58.36, "E quando eu acordei, estava num clube de strip"),
    (58.36, 59.90, "sendo ameaçado com uma conta"),
    (59.96, 62.32, "muito alta que eu tinha que pagar."),
    (62.58, 64.68, "Não foi uma experiência divertida na época."),
    (106.17, 108.89, "…país glorioso. Também tem um problema."),
    (141.67, 143.81, "…aqui está o roteiro. Eu falei que ia fazer"),
    (143.81, 145.00, "uma reescrita de quatro meses."),
    (159.15, 160.95, "Ih… A gente fez merda."),
    (167.67, 168.97, "Eu te amo. Beleza, já vou."),
    (179.42, 183.06, "…fazer teste pro vilão de uma comédia, tipo o ser humano"),
    (183.06, 184.25, "mais horrível."),
    (184.36, 187.70, "E ter conseguido esse papel foi muito importante"),
    (187.70, 189.30, "pra mim, pessoalmente."),
    (189.46, 190.36, "Tipo: ah, tá."),
    (190.42, 193.14, "Dá pra mudar a cabeça das pessoas se você"),
    (193.14, 194.35, "simplesmente insistir."),
    (194.44, 195.50, "Você tá bem?"),
    (195.62, 196.95, "Minha cabeça tá enfiada numa privada."),
    (197.09, 197.95, "O que você acha?"),
    (198.07, 199.00, "Faz as contas."),
    (206.51, 209.31, "Eu me reuni com o Todd Phillips seis meses antes, no outono,"),
    (209.31, 210.40, "para Se Beber, Não Case,"),
    (210.51, 213.65, "e aí não rolou, e a verdade é que"),
    (213.65, 214.60, "eu acho que eles tinham…"),
    (235.05, 238.03, "…percebi com comédias para maiores: se você"),
    (238.03, 239.90, "consegue fazer barato, por um preço,"),
    (240.00, 241.78, "eles realmente te dão liberdade no estúdio."),
    (241.86, 243.14, "Tipo: beleza, se você fizer por esse"),
    (243.14, 244.62, "valor, coloca o que quiser,"),
    (244.70, 245.90, "a gente vê na primeira exibição teste."),
    (257.23, 258.79, "Eu pensei: opa, como ele conseguiu meu e-mail?"),
    (258.89, 260.90, "Aí ele falou: bora nessa, cambada!"),
    (262.19, 263.50, "E eu pensei: isso é brincadeira?"),
    (263.65, 264.47, "E aí fui em frente,"),
    (264.49, 265.79, "e a gente começou a filmar."),
    (265.87, 267.41, "Fomos pra Vegas naquele outono."),
    (267.45, 268.60, "Aquilo mudou tudo."),
    (268.93, 270.20, "Você não vai usar isso, né?"),
    (271.00, 272.10, "A gente tá num."),
    (301.66, 303.12, "O que eu faço aqui."),
    (303.24, 304.86, "Eu cancelei. Cancelei."),
    (305.28, 306.68, "É, eu tinha um… como era o nome?"),
    (306.94, 309.40, "Se chamava Late World with Zach."),
    (309.79, 310.90, "Ótimo programa."),
    (311.77, 313.30, "Primeiro de abril!"),
    (314.42, 318.04, "Foi cancelado porque eu não escutava os convidados"),
    (318.04, 319.50, "e eu era péssimo nisso."),
    (319.60, 321.32, "Foi cancelado e aí eu pensei:"),
    (321.38, 324.38, "bom, foi uma boa tentativa de carreira,"),
    (324.38, 326.94, "e aí voltei a fazer microfone aberto"),
    (326.94, 327.72, "e tive que…"),
    (327.75, 331.61, "me recompor e começar a fazer teste pra, sei lá,"),
    (331.61, 333.95, "ajudante de garçom nº 2 ou mensageiro nº 4."),
    (350.61, 351.95, "Ele nem tava botando fé."),
    (352.03, 354.63, "Eu estava no Canadá e vim de avião pra um teste,"),
    (354.85, 356.83, "e pensei: isso vai ser um desperdício"),
    (356.83, 359.30, "de dinheiro, porque eu sou ruim em teste."),
    (359.47, 363.11, "Mas a Warner se interessou de verdade em ver ele gravado."),
    (363.41, 365.30, "Ah, é? Então vamos contar isso pra ele."),
    (371.99, 373.99, "Quando você coloca o Zach Galifianakis no pôster,"),
    (374.15, 377.03, "você atinge 99% do público sem nenhuma"),
    (377.03, 378.60, "expectativa, tipo: quem é esse cara?"),
    (378.81, 381.07, "Então isso permite mais surpresas,"),
    (381.97, 383.87, "e às vezes deixa o filme mais engraçado."),
    (384.07, 385.37, "Eu saía pra jantar com o resto do elenco"),
    (385.49, 386.20, "e dizia: quer saber,"),
    (386.25, 388.31, "acho que isso tá bom, e eu nunca tinha feito"),
    (388.31, 390.15, "nada bom. A gente conversava e pensava:"),
    (390.21, 391.75, "é, isso vai ser um bom filme,"),
    (392.27, 395.69, "mas virar um sucesso de bilheteria tão grande…"),
    (395.95, 398.13, "ninguém sabia. Quer dizer, é meio incrível,"),
    (398.35, 400.10, "mas também meio que arruinou minha vida."),
    (405.11, 406.10, "Você estava literalmente…"),
    (422.44, 425.60, "Eu filmava The Office e Se Beber, Não Case ao mesmo tempo."),
    (426.28, 428.66, "The Office concentrava as minhas cenas,"),
    (428.74, 431.06, "ou seja, juntaram todo o meu trabalho na segunda"),
    (431.06, 432.60, "e na terça da semana."),
    (432.72, 434.98, "Normalmente fica espalhado do jeito que encaixa."),
    (435.14, 438.36, "E Se Beber, Não Case aceitou filmar a minha semana"),
    (438.36, 441.90, "de quarta a domingo. Teve várias noites em que"),
    (441.90, 445.40, "a gente filmava de madrugada no domingo,"),
    (445.54, 448.60, "eu terminava às quatro da manhã e"),
    (448.60, 450.30, "tinha que estar no set"),
    (450.40, 453.80, "de The Office tipo às seis e meia"),
    (453.80, 456.80, "da manhã. Era loucura, nunca fiz isso antes"),
    (456.80, 460.04, "nem depois, mas eu fretei um jatinho pra me levar"),
    (460.04, 462.18, "às quatro da manhã de Las Vegas até o aeroporto"),
    (462.18, 464.00, "de Van Nuys, que, graças a Deus,"),
    (464.11, 466.90, "fica a uns 10 minutos do set da Dunder Mifflin."),
    (466.99, 468.60, "Uau. Eu não podia contar pra ninguém."),
    (468.75, 469.95, "Pra The Office,"),
    (470.11, 471.60, "eu só estava no horário."),
    (471.77, 474.41, "Tudo certo. Pra Se Beber, Não Case,"),
    (474.57, 476.65, "tudo certo. Aposto que você lembra com carinho."),
    (476.77, 477.91, "E essa é a parte mais louca:"),
    (478.03, 479.60, "foi tipo a melhor época."),
    (492.64, 493.70, "Quantos centímetros?"),
    (494.72, 497.84, "…de dilatação. Isso. Lembro de gravar meu teste pra Ligeiramente Grávidos"),
    (497.84, 502.50, "e eu me preparei bastante pra esse papel."),
    (502.76, 506.40, "Me inspirei em alguns médicos de quem eu não gostava muito"),
    (506.40, 510.10, "e com quem eu já tinha trabalhado."),
    (529.61, 530.60, "…ele pirou."),
    (530.83, 534.10, "O lugar inteiro ficou tipo: que po*** tá acontecendo ali?"),
    (535.56, 539.60, "Ei, você! É, você!"),
    (540.05, 544.75, "Eu só lembro do Todd Phillips sem conseguir parar de rir, e acho que"),
    (544.75, 546.55, "literalmente um ou dois dias depois eu ganhei o papel."),
    (546.60, 548.42, "Tchau, gayzinho!"),
    (550.20, 552.40, "Você disse que eu nunca seria feliz."),
    (552.59, 554.67, "Eu acredito que vou morrer sozinho."),
    (554.75, 556.10, "Eu ia querer assim."),
    (556.30, 558.54, "Bom, é assim que um viciado fala,"),
    (558.70, 561.48, "sabe, quando o viciado tá chapado e tem um vício,"),
    (561.80, 563.00, "ele fala assim."),
    (563.36, 566.62, "Tudo é extremo. Se não sai do meu jeito, é o fim do mundo."),
    (566.62, 568.72, "E sim, basicamente isso."),
    (568.86, 572.62, "O Mike é muito engraçado e topa qualquer coisa,"),
    (572.62, 576.30, "e a gente não sabia o que esperar quando ele apareceu no primeiro…"),
    (615.75, 618.45, "E mesmo tentando não dar um soco com toda a força,"),
    (618.45, 620.80, "ele chegou bem perto."),
    (627.61, 628.90, "Quantas vezes?"),
    (629.47, 633.30, "Porque se ele tivesse acertado, já era."),
    (644.40, 647.52, "…a cena em que eu jogo um bife num tigre e ele fala: tenta acertar a cabeça"),
    (648.00, 649.60, "com o bife."),
    (651.28, 654.52, "Teve uma hora em que eu estava empurrando o carro"),
    (654.52, 659.35, "de costas pro tigre, e o tigre ficou bem perto da minha…"),
    (659.59, 662.83, "…vértebra lombar, que é cercada de gordura."),
    (662.93, 664.50, "Então é tipo…"),
    (676.12, 680.30, "É verdade que não usaram efeitos especiais nessa cena?"),
    (680.48, 684.14, "Eu tenho um implante aqui, esse dente é falso,"),
    (684.14, 689.54, "e quando a gente ia filmar eu fui no meu dentista e falei: eles querem tirar meu…"),
    (689.54, 691.60, "isso é possível?"),
    (692.86, 696.00, "Tirar esse implante temporariamente? E ele topou."),
    (703.07, 704.00, "…um filme como esse."),
    (704.13, 707.53, "Pra mim, o segredo é sempre deixar o mais real possível. Então vamos mesmo pra Vegas."),
    (707.61, 709.95, "Vamos filmar de verdade no saguão do Caesars Palace."),
    (710.05, 712.40, "Usamos muitos figurantes pra gastar muito dinheiro em Vegas."),
    (712.40, 714.65, "E muita gente da equipe perdeu muito dinheiro em Vegas."),
    (714.77, 716.40, "Tem cara que não aguenta Vegas."),
    (728.80, 731.70, "Se chama bolsa carteiro. O Indiana Jones usa uma."),
    (746.55, 747.80, "Pronto pra soltar os cachorros?"),
]

def ts(t, sep=","):
    h, r = divmod(t, 3600); m, s = divmod(r, 60)
    return f"{int(h):02d}:{int(m):02d}:{int(s):02d}{sep}{int(round((s % 1) * 1000)):03d}" if sep == "," else \
           f"{int(h)}:{int(m):02d}:{s:05.2f}"

# duracao minima de leitura (1,0 s) sem invadir a proxima legenda
L.sort()
cues = []
for k, (a, b, t) in enumerate(L):
    nxt = L[k + 1][0] if k + 1 < len(L) else b + 2
    b = max(b, min(a + 1.0, nxt - 0.05))
    cues.append((a, b, t))
os.makedirs(os.path.join(AQUI, "out"), exist_ok=True); os.makedirs(os.path.join(AQUI, "build"), exist_ok=True)
with open(os.path.join(AQUI, "out/legendas_pt.srt"), "w") as f:
    for i, (a, b, t) in enumerate(cues, 1):
        f.write(f"{i}\n{ts(a)} --> {ts(b)}\n{t}\n\n")
# ASS: branco, contorno preto grosso, embaixo no centro, quebra automatica em ate 2 linhas (area segura)
ass = """[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Leg,Inter,58,&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,1,0,0,0,100,100,0,0,1,4.5,1.5,2,260,260,70,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
for a, b, t in cues:
    ass += f"Dialogue: 0,{ts(a, '.')},{ts(b, '.')},Leg,,0,0,0,,{t}\n"
open(os.path.join(AQUI, "build/legendas_pt.ass"), "w").write(ass)
print(len(cues), "legendas")
