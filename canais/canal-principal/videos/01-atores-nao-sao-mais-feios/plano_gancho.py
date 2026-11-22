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
