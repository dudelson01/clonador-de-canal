import json, sys
sys.path.insert(0, "ferramentas")
from legendas import grupos
V = "canais/canal-principal/videos/01-atores-nao-sao-mais-feios/"
t = json.load(open(V + "timeline.json"))
cor = {"Glenn": "Glen", "-Fantasmas": "Fantasmas", "Caça": "Caça-"}
leg = grupos(t["palavras"], 0, 32.0, 4, {"Glenn": "Glen"})
# junta "Caça" "-Fantasmas"
for g in leg:
    ws = g["palavras"]
    for i in range(len(ws) - 1):
        if ws[i]["w"] == "Caça" and ws[i + 1]["w"].startswith("Fantasmas"):
            ws[i]["w"] = "Caça-Fantasmas"; ws[i]["e"] = ws[i + 1]["e"]; del ws[i + 1]; break
    for w in ws:
        if w["w"] == "porque" : w["w"] = "por"
el = [
 {"tipo": "numero", "ini": 1.25, "fim": 4.3, "de": 0, "ate": 33, "sufixo": "ANOS", "dur": 0.6},
 {"tipo": "carimbo", "ini": 4.50, "fim": 5.9, "texto": "SÓ 33!", "rot": -9},
 {"tipo": "check", "ini": 7.0, "fim": 12.75, "titulo": "CURRÍCULO DE GENTE NORMAL",
  "itens": [{"t": "Boleto atrasado", "s": 8.1}, {"t": "Perdeu o último ônibus", "s": 9.6}, {"t": "Pastel de rodoviária", "s": 11.2}]},
 {"tipo": "etq", "ini": 13.15, "fim": 15.3, "html": "GLEN POWELL &middot; <em>35 ANOS</em>", "x": 1150, "y": 260},
 {"tipo": "carimbo", "ini": 16.5, "fim": 17.75, "texto": "BOLETOS: 0", "rot": 7},
 {"tipo": "filtro", "ini": 17.8, "fim": 20.3, "texto": "✨ FILTRO DE FÁBRICA: ATIVADO"},
 {"tipo": "flash", "ini": 22.7, "fim": 23.05},
 {"tipo": "letreiro", "ini": 22.7, "fim": 25.7, "texto": "PROIBIDO CARA DE GENTE"},
 {"tipo": "maquina", "ini": 25.75, "fim": 32.0, "cps": 20, "linhas": [
   {"t": "QUANDO ACONTECEU", "s": 26.7}, {"t": "POR QUE ACONTECEU", "s": 28.1}, {"t": "O ESTRAGO NOS FILMES", "s": 29.7}]},
]
# sem legenda embaixo quando o destaque já mostra o texto inteiro (máquina de escrever)
json.dump({"duracao": 32.0, "legenda": leg, "elementos": el}, open(V + "build/spec_gancho.json", "w"), ensure_ascii=False, indent=1)
print(len(leg), "legendas")
for g in leg: print(round(g["ini"],2), " ".join(w["w"] for w in g["palavras"]))

# ---------- som do gancho ----------
FX = V + "build/sfx/"
SFX = [
 (FX+"tique.wav",1.3,-6),(FX+"tique.wav",1.45,-8),(FX+"tique.wav",1.6,-8),(FX+"ding.wav",1.85,-10),
 (FX+"carimbo.wav",4.5,-2),
 (FX+"whoosh.wav",6.8,-10),(FX+"pop.wav",8.1,-6),(FX+"pop.wav",9.6,-6),(FX+"pop.wav",11.2,-6),
 (FX+"whoosh.wav",12.75,-8),(FX+"pop.wav",13.3,-8),
 (FX+"carimbo.wav",16.5,-3),
 (FX+"ding.wav",17.85,-9),(FX+"whoosh.wav",20.25,-10),
 (FX+"riser.wav",21.2,-12),(FX+"clarao.wav",22.7,-4),
 (FX+"whoosh.wav",25.7,-10),
] + [(FX+"maquina.wav", s + i/20, -12) for s,n in ((26.7,16),(28.1,17),(29.7,20)) for i in range(n)]
if __name__ == "__main__" and "--som" in sys.argv:
    from mixar import mixar
    mixar(V+"narracao.wav", V+"build/som_gancho.wav", 0, 32.0,
          musicas=[(V+"build/musica_gancho.wav", 0.0)], sfx=SFX)
    print("som ok")

# ---------- cenas do gancho (tempo da narração -> trecho do trailer) ----------
T = V + "midia/trailers/"
GB, TW, CH, TB, RK, TX = (T + x + ".mp4" for x in ("ghostbusters-1984", "twisters-2024", "chalamet-a-complete-unknown",
                                                   "the-batman-2022", "rocky-1976", "taxi-driver-1976"))
CENAS = [
 {"src": GB, "ss": 59.6, "dur": 2.40},                    # Bill Murray close: "tinha 33 anos"
 {"src": GB, "ss": 41.0, "dur": 2.10},                    # equipe no hotel: "Caça-Fantasmas"
 {"src": GB, "ss": 108.4, "dur": 2.30, "vel": 0.55, "zoom": 0.12},  # rosto do Bill: "33. Olha essa cara"
 {"src": GB, "ss": 104.4, "dur": 2.70, "efeito": "escurece"},       # equipe: checklist
 {"src": GB, "ss": 34.0, "dur": 1.70, "efeito": "escurece"},        # Ecto-1 na rua: "perdeu o ônibus"
 {"src": GB, "ss": 98.3, "dur": 1.65, "efeito": "escurece"},        # multidão: "pastel de rodoviária"
 {"src": TW, "ss": 65.88, "dur": 2.45, "vel": 0.37},        # Glen close: "Glen Powell, 35"
 {"src": TW, "ss": 98.1, "dur": 0.85},                    # Glen de chapéu
 {"src": TW, "ss": 57.4, "dur": 0.70},                    # Glen sorrindo
 {"src": TW, "ss": 47.3, "dur": 0.90},                    # Glen dirigindo
 {"src": TW, "ss": 113.9, "dur": 2.55, "vel": 0.42, "efeito": "filtro"},  # "pele com filtro"
 {"src": CH, "ss": 60.2, "dur": 1.20},                    # Chalamet na rua: "não é impressão sua"
 {"src": TB, "ss": 137.6, "dur": 1.20, "vel": 0.7},       # Pattinson
 {"src": CH, "ss": 82.85, "dur": 3.00, "vel": 0.45, "zoom": 0.1},  # Chalamet de óculos: "PROIBIDO CARA DE GENTE"
 {"src": RK, "ss": 132.15, "dur": 1.00, "vel": 0.5, "efeito": "escurece"},  # Stallone suado: "quando aconteceu"
 {"src": RK, "ss": 160.0, "dur": 1.40, "efeito": "escurece"},  # ringue do Rocky
 {"src": TX, "ss": 70.0, "dur": 1.60, "efeito": "escurece"},   # De Niro: "por que aconteceu"
 {"src": TW, "ss": 100.4, "dur": 2.30, "vel": 0.75, "efeito": "escurece"},  # Glen gritando: "mais chatos?"
]
if __name__ == "__main__" and "--video" in sys.argv:
    from montar import montar
    print("duração das cenas:", round(sum(c["dur"] for c in CENAS), 2))
    prev = "--preview" in sys.argv
    montar(CENAS, V + "build/artes_gancho.mov", V + "build/som_gancho.wav",
           V + ("out/amostra-gancho-preview.mp4" if prev else "out/amostra-gancho.mp4"), preview=prev)
    print("video ok")
