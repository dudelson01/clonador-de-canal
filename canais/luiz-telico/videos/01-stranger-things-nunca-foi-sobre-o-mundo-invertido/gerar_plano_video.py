#!/usr/bin/env python3
"""Gera plano_video.json (video inteiro) a partir da amostra aprovada + cenas do resto.
Cenas: (ini, fim, tipo, src, t_fonte, zoom0, zoom1, [sfx])  tipo: R=rosto, V=video.  Tempos = tempo no decupado."""
import json

A = json.load(open("plano_amostra.json"))
cenas = A["cenas"]; artes = A["artes"]
# corrige repeticao da amostra (mesmos planos do trailer em 0:19 e 0:30)
novas = []
for c in cenas:
    if c.get("src") == "t1" and c["t"] == 7.9:   # "a prova esta na ultima cena": porao aberto + outro angulo
        novas.append(dict(c, fim=20.85, t=3.6, zoom=[1.10, 1.16]))
        novas.append({"ini": 20.85, "fim": 21.90, "tipo": "video", "src": "t1", "t": 11.0, "zoom": [1.12, 1.16], "fala": "da serie,"})
    elif c.get("src") == "t1" and c["t"] == 3.0 and c["ini"] > 28:   # "pro porao dos Wheeler"
        novas.append(dict(c, t=8.0))
    elif c.get("src") == "t1" and c["t"] == 5.0 and c["ini"] < 11:
        novas.append(dict(c, t=16.4))
    elif c.get("src") == "t1" and c["t"] == 9.0:
        novas.append(dict(c, t=9.1, fim=32.0))
    else:
        novas.append(c)
cenas = novas

R, V = "rosto", "video"
def r(a, b, z0=1.0, z1=1.06, sfx=None):
    d = {"ini": a, "fim": b, "tipo": R, "zoom": [z0, z1]}
    if sfx: d["sfx"] = sfx
    return d
def v(a, b, src, t, z0=1.12, z1=1.18, sfx=None):
    d = {"ini": a, "fim": b, "tipo": V, "src": src, "t": t, "zoom": [z0, z1]}
    if src.startswith("px"): d["zoom"] = [max(1.0, z0 - 0.1), max(1.04, z1 - 0.1)]
    d["sfx"] = sfx if sfx is not None else [["whoosh", 0]]
    return d
P = lambda a, b: r(a, b, 1.22, 1.25)   # "punch-in": zoom forte no rosto

resto = [
    # --- BLOCO 1: o porao ---
    r(32.00, 34.30),
    v(34.30, 36.70, "t2", 13.0),                         # moleques jogando
    v(36.70, 38.86, "t1", 13.3),                         # os quatro com as bicicletas
    r(38.86, 42.20),                                     # mesa cheia de dados, salgadinho, mae chamando
    v(42.20, 45.30, "t1", 59.6, 1.12, 1.22),             # monstro sem nome (olhos no escuro)
    r(45.30, 49.24),
    r(49.24, 52.20),
    v(52.20, 55.30, "t2", 15.4),                         # atraves da brincadeira
    P(55.30, 58.92),
    v(58.92, 61.00, "t1", 25.2),                         # o Will, o mais novo
    v(61.00, 64.18, "t1", 27.3, 1.12, 1.20, []),         # o mais crianca do grupo
    v(64.18, 66.60, "t1", 39.6, 1.12, 1.18),             # some voltando pra casa (cartaz de desaparecido)
    v(66.60, 68.60, "t3", 5.0, 1.14, 1.20),              # mundo invertido
    r(68.60, 70.70),
    # --- PONTE ---
    r(70.70, 75.50, sfx=[["subida", 3.8]]),
    P(75.50, 78.12),
    # --- BLOCO 2: o castelo ---
    v(78.12, 79.90, "t2", 60.0),                         # terceira temporada, os amigos...
    v(79.90, 82.05, "t2", 117.0),                        # namorando
    v(82.05, 84.34, "t2", 29.0),                         # o Will ainda quer jogar
    v(84.34, 86.90, "t2", 96.0),                         # mapa
    r(86.90, 90.40),
    v(90.40, 92.80, "t1", 91.0),                         # a briga, o Mike
    r(92.80, 97.70),
    P(97.70, 101.80),                                    # comentario: quebrava a cara do Mike
    r(101.80, 103.80),
    v(103.80, 106.00, "t1", 51.0),                       # castelo Byers
    v(106.00, 108.05, "t1", 37.0, 1.10, 1.16),           # no mato
    v(108.05, 110.80, "t2", 77.2, 1.12, 1.18),           # destroi o castelo sozinho (Will chorando)
    r(110.80, 114.90),
    v(114.90, 117.60, "t1", 17.0),                       # a infancia do Will
    r(117.60, 120.85),
    v(120.85, 123.75, "t2", 138.0, 1.12, 1.20),          # o mundo invertido tenta levar
    r(123.75, 126.85),
    P(126.85, 133.45),                                   # comentario: 18 anos
    # --- BLOCO 2B: Hopper ---
    r(133.45, 135.90),
    v(135.90, 137.80, "t1", 53.0),                       # o adulto mais durao
    v(137.80, 139.80, "t1", 46.6),                       # tenta segurar o tempo
    v(139.80, 141.00, "t1", 50.0),                       # O Hopper
    v(141.00, 142.85, "t1", 67.5),                       # adotou a Eleven
    r(142.85, 149.75),
    P(149.75, 151.85),                                   # pai ciumento
    r(151.85, 155.30),
    v(155.30, 157.40, "t1", 54.0, 1.10, 1.14),           # a carta (arte por cima)
    P(157.40, 162.15),                                   # comentario: chorei
    v(162.15, 165.20, "t1", 48.0),                       # na carta ele admite
    v(165.20, 168.55, "t1", 116.0),                      # medo de ela crescer
    r(168.55, 172.85),
    v(172.85, 174.50, "t3", 28.4),                       # que ela nao pare de mudar
    v(174.50, 176.00, "t3", 52.0),                       # russos
    v(176.00, 177.80, "t2", 125.0),                      # monstros
    v(177.80, 178.70, "t2", 43.35, 1.12, 1.16),          # devorador de mentes
    r(178.70, 181.05),
    P(181.05, 186.40),                                   # comentario: tempo invencivel
    r(186.40, 189.30),
    v(189.30, 192.20, "t3", 30.0),                       # todo mundo ja foi a Eleven
    v(192.20, 195.00, "t2", 97.0),                       # vai ser o Hopper
    # --- CTA ---
    r(195.00, 203.70),
    # --- BLOCO 3: Vecna ---
    r(203.70, 205.90),
    v(205.90, 207.90, "t3", 37.9),                       # o vilao muda de forma
    P(207.90, 213.85),                                   # comentario: era bonito antes
    v(213.85, 215.65, "t3", 37.0, 1.16, 1.24, [["impacto", 0.05]]),   # ...ficou feio
    r(215.65, 219.42),
    v(219.42, 223.80, "t3", 15.0, 1.12, 1.20),           # culpa, trauma, sozinho
    v(223.80, 226.00, "t3", 14.0),                       # a Max
    v(226.00, 228.85, "t3", 7.0, 1.14, 1.20),            # se afastou de todo mundo
    r(228.85, 233.40),
    v(233.40, 236.00, "t3", 84.0),                       # como a Max escapa
    v(236.00, 238.88, "t3", 64.0),                       # os amigos chamando por ela
    P(238.88, 242.60),                                   # comentario: de arrepiar
    v(242.60, 245.45, "t1", 87.0),                       # imaginacao (T1)
    v(245.45, 247.62, "t3", 58.0),                       # nao enfrentar sozinho (T4)
    r(247.62, 251.15),
    v(251.15, 253.30, "t1", 7.1, 1.12, 1.18),            # o demogorgon
    v(253.30, 255.62, "t3", 37.0, 1.14, 1.20),           # o Vecna
    # --- PONTE ---
    r(255.62, 259.40),
    v(259.40, 262.00, "t3", 103.0, 1.04, 1.10),          # a ultima temporada (titulo)
    r(262.00, 264.50),
    P(264.50, 268.40),                                   # que despedida ruim
    # --- BLOCO 4: a porta ---
    r(268.40, 270.40, sfx=[["rebobinar", 0.1]]),
    r(270.40, 275.50),
    v(275.50, 279.00, "t1", 3.0, 1.10, 1.18),            # no mesmo lugar onde comecou
    v(279.00, 284.20, "t1", 8.0, 1.10, 1.20),            # a ultima campanha
    r(284.20, 289.20),
    v(289.20, 291.65, "t1", 74.0),                       # o Mike fechando a porta
    r(291.65, 293.45),
    v(293.45, 296.30, "t1", 115.0),                      # muita vida pela frente
    v(296.30, 299.05, "t1", 73.0, 1.08, 1.16),           # a nossa historia termina
    r(299.05, 301.35),
    v(301.35, 303.30, "t3", 5.6, 1.14, 1.20),            # nao foi um lugar, foi uma fase
    v(303.30, 306.25, "t1", 19.0, 1.10, 1.18),           # tudo que voce ama naquela idade
    r(306.25, 311.65),
    # --- BLOCO 5: Eleven ---
    v(311.65, 314.00, "t3", 29.0),                       # e a Eleven?
    r(314.00, 317.50),
    v(317.50, 319.70, "t1", 117.0),                      # os poderes dela
    v(319.70, 320.60, "t1", 122.0, 1.12, 1.15),          # parte magica de ser crianca
    r(320.60, 323.25),
    v(323.25, 326.80, "t1", 118.0),                      # mover o mundo
    r(326.80, 330.10),
    v(330.10, 331.90, "t1", 11.0, 1.10, 1.16),           # ela fica la, no porao
    # --- FINAL ---
    r(331.90, 335.60),
    v(335.60, 338.00, "t2", 25.5),                       # a ultima vez que voce jogou
    v(338.00, 341.45, "t2", 114.0),                      # com seus amigos
    v(341.45, 343.10, "px147704", 1.0),                  # futebol na rua
    v(343.10, 344.40, "px997", 4.0),                     # volei
    v(344.40, 345.40, "px24711", 3.0),                   # pique
    v(345.40, 346.45, "px85339", 2.0),                   # pique pega
    v(346.45, 347.70, "px24711", 12.0),                  # pique esconde
    r(347.70, 350.05),
    r(350.05, 353.70),
    r(353.70, 362.04),
]

# ---- ajustes depois da conferencia quadro a quadro (cenas que escureciam ou trocavam de plano) ----
AJ = {
    58.92: [v(58.92, 61.00, "t1", 5.0)],
    61.00: [v(61.00, 62.90, "t1", 25.9, 1.12, 1.18, []), r(62.90, 64.18)],
    64.18: [v(64.18, 66.60, "t1", 39.5)],
    90.40: [v(90.40, 91.90, "t1", 91.0), r(91.90, 92.80)],
    103.80: [v(103.80, 105.00, "t1", 51.0)],
    106.00: [v(105.00, 107.00, "t1", 36.9, 1.10, 1.16), v(107.00, 108.60, "t2", 78.3, 1.12, 1.18, [])],
    108.05: [r(108.60, 110.80)],
    114.90: [v(114.90, 116.40, "t1", 10.1), r(116.40, 117.60)],
    135.90: [v(135.90, 137.60, "t1", 53.4)],
    137.80: [v(137.60, 139.80, "t1", 46.6)],
    139.80: [v(139.80, 141.00, "t2", 116.5)],
    141.00: [v(141.00, 142.85, "t1", 67.0)],
    155.30: [v(155.30, 157.40, "t1", 53.4, 1.10, 1.14)],
    162.15: [v(162.15, 165.20, "t2", 97.0)],
    165.20: [v(165.20, 166.60, "t1", 116.3), r(166.60, 168.55)],
    172.85: [v(172.85, 174.50, "t3", 28.2)],
    189.30: [v(189.30, 192.20, "t1", 92.0)],
    192.20: [v(192.20, 195.00, "t1", 46.6)],
    205.90: [v(205.90, 207.00, "t3", 37.6)],
    207.90: [P(207.00, 213.85)],
    219.42: [v(219.42, 221.40, "t3", 15.0), r(221.40, 223.80)],
    233.40: [r(233.40, 234.90)],
    236.00: [v(234.90, 238.88, "t3", 64.0)],
    242.60: [v(242.60, 244.00, "t1", 87.3), r(244.00, 245.45)],
    275.50: [v(275.50, 279.00, "t1", 3.3, 1.10, 1.18)],
    279.00: [v(279.00, 281.00, "t1", 8.0), r(281.00, 284.20)],
    289.20: [v(289.20, 290.60, "t1", 74.2), v(290.60, 291.65, "t1", 73.5)],
    293.45: [v(293.45, 295.20, "t1", 115.0), r(295.20, 296.30)],
    296.30: [v(296.30, 297.60, "t1", 73.0, 1.08, 1.14), r(297.60, 299.05)],
    303.30: [v(303.30, 306.25, "t2", 10.0)],
    317.50: [v(317.50, 318.70, "t1", 117.1), v(318.70, 319.70, "t1", 122.2, 1.12, 1.15)],
    319.70: [r(319.70, 323.25)],
    320.60: [],
    323.25: [v(323.25, 325.00, "t1", 118.0), r(325.00, 326.80)],
    330.10: [v(330.10, 331.90, "t1", 10.9, 1.10, 1.16)],
    338.00: [v(338.00, 341.45, "t1", 87.3)],
}
AJ.update({
    58.92: [v(58.92, 60.40, "t1", 5.4)],
    61.00: [v(60.40, 62.00, "t1", 26.2, 1.12, 1.18, []), r(62.00, 64.18)],
    90.40: [v(90.40, 91.40, "t1", 91.0), r(91.40, 92.80)],
    106.00: [v(105.00, 106.30, "t1", 36.9, 1.10, 1.16), v(106.30, 107.40, "t2", 78.2, 1.12, 1.18, [])],
    108.05: [r(107.40, 110.80)],
    137.80: [v(137.60, 139.80, "t1", 46.3)],
    139.80: [v(139.80, 141.00, "t2", 116.2)],
    162.15: [v(162.15, 163.60, "t2", 97.0), r(163.60, 165.20)],
    165.20: [v(165.20, 166.30, "t1", 116.3), r(166.30, 168.55)],
    172.85: [v(172.85, 173.90, "t3", 28.2), r(173.90, 174.50)],
    189.30: [v(189.30, 190.60, "t1", 92.0), r(190.60, 192.20)],
    192.20: [v(192.20, 193.90, "t1", 46.6), r(193.90, 195.00)],
    275.50: [v(275.50, 277.10, "t1", 3.6, 1.10, 1.16), r(277.10, 279.00)],
    296.30: [v(296.30, 297.10, "t1", 73.0, 1.08, 1.12), r(297.10, 299.05)],
    317.50: [v(317.50, 318.70, "t1", 117.1), v(318.70, 319.55, "t1", 122.05, 1.12, 1.15)],
    319.70: [r(319.55, 323.25)],
    323.25: [v(323.25, 324.40, "t1", 118.0), r(324.40, 326.80)],
    330.10: [v(330.10, 331.30, "t1", 10.9, 1.10, 1.14), r(331.30, 331.90)],
    338.00: [v(338.00, 339.40, "t2", 28.0), r(339.40, 341.45)],
})
AJ.update({   # 2a conferencia: trechos pretos encontrados com blackdetect no video montado
    42.20: [r(42.20, 45.30)],
    61.00: [r(60.40, 64.18)],
    137.80: [v(137.60, 139.20, "t1", 47.2), r(139.20, 139.80)],
    192.20: [v(192.20, 193.10, "t1", 50.0), r(193.10, 195.00)],
    213.85: [v(213.85, 215.40, "t3", 37.0, 1.16, 1.24, [["impacto", 0.05]])],
    215.65: [r(215.40, 219.42)],
    226.00: [v(226.00, 227.40, "t3", 7.0, 1.14, 1.20), r(227.40, 228.85)],
    253.30: [v(253.30, 254.80, "t3", 37.0, 1.14, 1.20), r(254.80, 255.62)],
    259.40: [v(259.40, 262.00, "t3", 104.8, 1.04, 1.10)],
    317.50: [v(317.50, 318.70, "t1", 117.1), v(318.70, 319.25, "t1", 122.05, 1.12, 1.15)],
    319.70: [r(319.25, 323.25)],
})
AJ.update({   # 3a conferencia: planos curtos do trailer (Will 5,5-6,0 / mapa 96,0-96,5 / Eleven 92,0-92,6)
    58.92: [v(58.92, 59.50, "t1", 5.45)],
    61.00: [r(59.50, 64.18)],
    84.34: [v(84.34, 84.85, "t2", 95.95), r(84.85, 86.90)],
    189.30: [v(189.30, 189.90, "t1", 92.0), r(189.90, 192.20)],
})
novo = []
for c in resto:
    k = round(c["ini"], 2)
    if k in AJ: novo += AJ[k]
    else: novo.append(c)
resto = sorted(novo, key=lambda c: c["ini"])
# rosto vizinho: estica ate a proxima cena para nao sobrar buraco
for x, y in zip(resto, resto[1:]):
    if abs(x["fim"] - y["ini"]) > 1e-6 and x["tipo"] == R: x["fim"] = y["ini"]

# rosto longo (> 4,5 s): divide no meio e alterna o enquadramento (aberto -> fechado), sem cortar a fala
def divide(c):
    if c["tipo"] != R or c["fim"] - c["ini"] <= 4.5: return [c]
    m = round((c["ini"] + c["fim"]) / 2 * 30) / 30
    z = c["zoom"]; fechado = z[0] >= 1.2
    a = dict(c, fim=m); b = dict(c, ini=m, zoom=[1.0, 1.05] if fechado else [1.17, 1.20]); b.pop("sfx", None)
    return divide(a) + divide(b)
resto = [x for c in resto for x in divide(c)]
cenas = cenas + resto
# sanidade: sem buraco nem sobreposicao
for x, y in zip(cenas, cenas[1:]):
    assert abs(x["fim"] - y["ini"]) < 1e-6, (x, y)

arte = lambda i, a, d, tipo, **k: dict(id=i, ini=a, dur=d, tipo=tipo, **k)
artes += [
    arte("nomes", 36.80, 2.05, "maquina", texto="Mike · Dustin · Lucas · Will", x=110, y=900, sfx="teclas"),
    arte("dados", 39.10, 2.9, "chave", texto="mesa cheia de <b>dados</b>, salgadinho..."),
    arte("sem_nome", 42.60, 2.6, "chave", texto="o primeiro monstro <b>não tem nome</b>"),
    arte("demo_jogo", 46.80, 2.3, "chave", texto="Demogorgon: um monstro do <b>jogo</b>"),
    arte("criancas", 56.20, 2.6, "chave", texto="porque elas ainda são <b>crianças</b>"),
    arte("will", 58.97, 0.53, "etiqueta", texto="Will", x=1250, y=260, sx=1300, sy=370, ax=1010, ay=480, sfx="pop"),
    arte("desaparecido", 64.70, 1.8, "carimbo", texto="DESAPARECIDO", x=1250, y=260),
    arte("t3", 74.10, 1.6, "canto", texto="Temporada 3", sfx="pop"),
    arte("mapa", 84.38, 0.47, "etiqueta", texto="o mapa da campanha", x=1000, y=760, sx=1080, sy=740, ax=900, ay=480, rot=2, sfx="pop"),
    arte("frase_dor", 93.30, 2.6, "chave", texto="a frase que dói mais que <b>qualquer monstro</b>"),
    arte("castelo", 103.90, 1.05, "etiqueta", texto="Castelo Byers", x=1150, y=220, sx=1230, sy=330, ax=980, ay=500, sfx="pop"),
    arte("infancia", 115.20, 2.2, "chave", texto="o que morre ali é a <b>infância</b>"),
    arte("licenca", 124.10, 2.6, "chave", texto="crescer leva todo mundo <b>sem pedir licença</b>"),
    arte("anos", 131.95, 1.45, "contador", de=15, ate=18, rotulo="ANOS", x=1480, y=380, tam=160, tc=0.6, sfx="pop"),
    arte("hopper", 139.90, 1.1, "etiqueta", texto="Hopper", x=1200, y=200, sx=1270, sy=310, ax=1020, ay=430, sfx="pop"),
    arte("eleven", 141.05, 1.75, "etiqueta", texto="Eleven", x=1200, y=220, sx=1260, sy=330, ax=1000, ay=480, sfx="pop"),
    arte("regras", 147.10, 2.6, "chave", texto="fecha a porta, inventa regra e até <b>ameaça</b>"),
    arte("carta", 155.35, 2.0, "carta", linhas=["El,", "eu sei que você", "está crescendo..."], vel=0.035),
    arte("crescer", 165.40, 3.0, "chave", texto="medo de ela <b>crescer</b>"),
    arte("mudar", 172.95, 1.5, "chave", texto="que ela <b>não pare de mudar</b>"),
    arte("russos", 174.60, 1.3, "etiqueta", texto="russos", x=1250, y=230, sx=1300, sy=330, ax=1060, ay=480, sfx="pop"),
    arte("tempo", 179.20, 1.8, "perigo", texto="O TEMPO", x=470, y=430),
    arte("ja_foi", 190.10, 2.0, "chave", texto="todo mundo já foi a <b>Eleven</b>"),
    arte("sera", 192.60, 2.3, "chave", texto="um dia, quase todo mundo vai ser o <b>Hopper</b>"),
    arte("inscrever1", 195.40, 3.2, "inscrever"),
    arte("t4", 206.00, 1.6, "canto", texto="Temporada 4", sfx="pop"),
    arte("feio", 213.95, 1.6, "etiqueta", texto="o \"bonito\"", x=1250, y=230, sx=1300, sy=330, ax=1000, ay=440, sfx="pop"),
    arte("culpa", 219.80, 3.9, "chave", texto="com <b>culpa</b>, com <b>trauma</b> e <b>sozinho</b>"),
    arte("max", 223.90, 1.9, "etiqueta", texto="Max", x=1250, y=240, sx=1290, sy=340, ax=1000, ay=480, sfx="pop"),
    arte("cresce", 229.40, 3.8, "chave", texto="o monstro que aparece <b>quando a gente cresce</b>"),
    arte("t1b", 242.70, 1.4, "canto", texto="Temporada 1", sfx="pop"),
    arte("t4b", 245.55, 1.4, "canto", texto="Temporada 4", sfx="pop"),
    arte("demo2", 251.30, 1.8, "etiqueta", texto="medo de criança", x=1050, y=200, sx=1150, sy=300, ax=760, ay=450, sfx="pop"),
    arte("vecna2", 253.40, 2.1, "etiqueta", texto="medo de adolescente", x=180, y=280, sx=520, sy=380, ax=820, ay=560, sfx="pop"),
    arte("despedindo", 261.90, 2.5, "chave", texto="ela estava <b>se despedindo de você</b>"),
    arte("duffer", 271.20, 2.6, "maquina", texto="Matt e Ross Duffer · os criadores", x=110, y=900, sfx="teclas"),
    arte("segunda2", 273.30, 2.0, "chave", texto="sabiam desde a <b>2ª temporada</b>", y=800),
    arte("spoiler2", 275.70, 2.2, "carimbo", texto="SPOILER", x=1480, y=230),
    arte("ultima", 280.00, 3.8, "chave", texto="a <b>última</b> campanha"),
    arte("ultimo", 286.90, 2.2, "chave", texto="agora eles sabem que é o <b>último</b>"),
    arte("porta", 289.30, 1.25, "etiqueta", texto="Mike", x=1250, y=230, sx=1300, sy=330, ax=1020, ay=470, sfx="pop"),
    arte("fase", 301.45, 1.8, "chave", texto="não foi um lugar, foi uma <b>fase</b>"),
    arte("sempre", 309.50, 2.1, "chave", texto="o pra sempre <b>sempre acaba</b>"),
    arte("poderes", 317.60, 2.0, "chave", texto="eles não quiseram tirar os <b>poderes</b> dela"),
    arte("magica", 321.00, 2.2, "chave", texto="a parte <b>mágica</b> de ser criança"),
    arte("porao2", 330.20, 1.65, "maquina", texto="no porão.", x=110, y=900, sfx="teclas"),
    arte("nunca", 332.90, 2.7, "chave", texto="nunca foi sobre o <b>Mundo Invertido</b>"),
    arte("ultima_vez", 347.90, 1.95, "chave", texto="a gente nunca sabe qual foi a <b>última vez</b>"),
    arte("comenta", 350.30, 3.3, "chave", texto="qual foi o seu <b>último jogo</b>? comenta aí"),
    arte("inscrever2", 357.20, 2.8, "inscrever"),
]
plano = dict(A, cenas=cenas, artes=artes, fim=362.04)
plano["fontes"] = dict(A["fontes"], **{k: f"midia/pixabay/{k}.mp4" for k in ["px147704", "px997", "px24711", "px85339"]})
plano["trilha"] = {"arquivo": "midia/som/trilha_video.wav", "volume_db": -21}
json.dump(plano, open("plano_video.json", "w"), ensure_ascii=False, indent=1)
print(len(cenas), "cenas,", len(artes), "artes,", "rosto:", round(sum(c["fim"] - c["ini"] for c in cenas if c["tipo"] == R) / 362.04 * 100), "%")
