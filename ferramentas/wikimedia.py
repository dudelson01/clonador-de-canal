#!/usr/bin/env python3
"""Busca e baixa fotos LIVRES do Wikimedia Commons, anotando autor e licenca em creditos.txt.
Uso: python3 wikimedia.py pasta_saida "nome_arquivo|busca" ["nome2|busca2" ...]
     (opcional: "nome|File:Titulo_exato.jpg" para pegar um arquivo especifico)
Baixa a 1a imagem (jpg/png) com licenca livre (CC0, CC BY, CC BY-SA, dominio publico), largura ate 1920 px.
Cada busca gera pasta_saida/<nome>.jpg e uma linha em pasta_saida/creditos.txt."""
import json, os, re, sys, time, urllib.parse, urllib.request

API = "https://commons.wikimedia.org/w/api.php"
UA = {"User-Agent": "VideoEditBot/1.0 (personal video editing; low volume)"}
LIVRE = re.compile(r"(cc0|cc[- ]by|public domain|pd[- ]|domínio público|dominio publico)", re.I)

def get(params):
    url = API + "?" + urllib.parse.urlencode(dict(params, format="json"))
    return json.loads(baixa(url))

def baixa(url):
    # o Wikimedia limita pedidos (429) no IP compartilhado: espera e tenta de novo, devagar
    for tent in range(12):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r:
                return r.read()
        except Exception as e:
            err = e; time.sleep(min(60, 5 * (tent + 1)))
    raise err

def info(titulos):
    d = get({"action": "query", "titles": "|".join(titulos), "prop": "imageinfo",
             "iiprop": "url|extmetadata|mime|size", "iiurlwidth": 1920})
    out = []
    for p in d.get("query", {}).get("pages", {}).values():
        ii = (p.get("imageinfo") or [{}])[0]
        if not ii or ii.get("mime") not in ("image/jpeg", "image/png"): continue
        md = ii.get("extmetadata", {})
        lic = md.get("LicenseShortName", {}).get("value", "")
        autor = re.sub("<[^>]+>", "", md.get("Artist", {}).get("value", "")).strip()
        out.append({"titulo": p["title"], "url": ii.get("thumburl") or ii["url"], "lic": lic, "autor": autor,
                    "pagina": ii.get("descriptionurl", ""), "w": ii.get("width", 0)})
    return out

def buscar(busca):
    if busca.startswith("File:"): return info([busca])
    r = get({"action": "query", "list": "search", "srsearch": busca + " filetype:bitmap", "srnamespace": 6, "srlimit": 15})
    tit = [x["title"] for x in r.get("query", {}).get("search", [])]
    cands = info(tit) if tit else []
    ordem = {t: i for i, t in enumerate(tit)}
    cands.sort(key=lambda c: ordem.get(c["titulo"], 99))
    return cands

def main():
    pasta = sys.argv[1]; os.makedirs(pasta, exist_ok=True)
    cred = open(os.path.join(pasta, "creditos.txt"), "a")
    for item in sys.argv[2:]:
        nome, busca = item.split("|", 1)
        dest = os.path.join(pasta, nome + ".jpg")
        if os.path.exists(dest): print("ja existe", nome); continue
        try:
            achado = buscar(busca)
        except Exception as e:
            print("FALHOU", nome, e); continue
        cands = [c for c in achado if LIVRE.search(c["lic"]) and c["w"] >= 800]
        if not cands: print("NADA livre para", nome, "|", busca); continue
        c = cands[0]
        dados = baixa(c["url"])            # baixa tudo antes de criar o arquivo (arquivo vazio = foto quebrada)
        open(dest, "wb").write(dados)
        cred.write(f"{nome}.jpg | {c['titulo']} | {c['autor']} | {c['lic']} | {c['pagina']}\n"); cred.flush()
        print("ok", nome, "<-", c["titulo"], "|", c["lic"])
        time.sleep(4)

main()
