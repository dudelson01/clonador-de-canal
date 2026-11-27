#!/usr/bin/env python3
"""Monta uma grade com as thumbs recentes de varios canais (1 linha por canal), para conferir rosto/estilo.
Uso: python3 grade_thumbs.py dados.json saida.png pasta_cache "Canal 1" "Canal 2" ...
dados.json = saida do canais_crescendo.py. Baixa de i.ytimg.com."""
import json, sys, os, urllib.request
from PIL import Image, ImageDraw, ImageFont

dados, saida, cache, nomes = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4:]
os.makedirs(cache, exist_ok=True)
db = json.load(open(dados))["canais"]
por_nome = {c["nome"]: c for c in db.values()}
W, H, N, LAB = 256, 144, 6, 220
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 15)
img = Image.new("RGB", (LAB + W * N, H * len(nomes)), "white")
d = ImageDraw.Draw(img)
for i, nome in enumerate(nomes):
    c = por_nome[nome]
    d.text((6, i * H + 6), f"{i+1}. {nome[:22]}", fill="black", font=font)
    d.text((6, i * H + 28), f"{c['inscritos']:,} insc.", fill="gray", font=font)
    for j, v in enumerate((c.get("recentes") or [])[:N]):
        p = os.path.join(cache, v["id"] + ".jpg")
        if not os.path.exists(p):
            try: urllib.request.urlretrieve(f"https://i.ytimg.com/vi/{v['id']}/mqdefault.jpg", p)
            except Exception: continue
        try: img.paste(Image.open(p).convert("RGB").resize((W, H)), (LAB + j * W, i * H))
        except Exception: pass
img.save(saida)
print("ok", saida)
