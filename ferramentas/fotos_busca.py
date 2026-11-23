"""Baixa mais fotos livres do Commons por BUSCA (list=search), devagar, sem repetir as que já existem/foram descartadas.
Uso: python ferramentas/fotos_busca.py <pasta_fotos> <alvo_por_ator> "Nome|termo extra" ..."""
import json, os, re, sys, time, urllib.parse, urllib.request
UA = {"User-Agent": "clonador-de-canal/1.0 (ferramenta de edicao)"}
API = "https://commons.wikimedia.org/w/api.php"
def get(p):
    for i in range(5):
        try:
            with urllib.request.urlopen(urllib.request.Request(API + "?" + urllib.parse.urlencode({**p, "format": "json"}), headers=UA), timeout=40) as r:
                time.sleep(3); return json.load(r)
        except Exception: time.sleep(30 * (i + 1))
    return {}
def slug(s): return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
pasta, alvo = sys.argv[1], int(sys.argv[2])
cf = os.path.join(pasta, "creditos.json"); cred = json.load(open(cf)) if os.path.exists(cf) else {}
ja = {v["arquivo"] for v in cred.values()}
for arg in sys.argv[3:]:
    nome = arg.split("|")[0]; d = os.path.join(pasta, slug(nome)); os.makedirs(d, exist_ok=True)
    tem = len([x for x in os.listdir(d) if x.endswith(".jpg")])
    if tem >= alvo: print(nome, "ok", tem); continue
    r = get({"action": "query", "list": "search", "srnamespace": 6, "srlimit": 40, "srsearch": nome})
    titulos = [x["title"] for x in r.get("query", {}).get("search", []) if x["title"] not in ja
               and x["title"].lower().endswith((".jpg", ".jpeg")) and nome.split()[-1].lower() in x["title"].lower()]
    for i in range(0, len(titulos), 10):
        if tem >= alvo: break
        r = get({"action": "query", "titles": "|".join(titulos[i:i + 10]), "prop": "imageinfo",
                 "iiprop": "url|extmetadata|size", "iiurlwidth": 1280})
        for p in r.get("query", {}).get("pages", {}).values():
            if tem >= alvo: break
            ii = (p.get("imageinfo") or [{}])[0]; md = ii.get("extmetadata", {})
            lic = re.sub("<[^>]+>", "", md.get("LicenseShortName", {}).get("value", ""))
            if not re.search(r"CC BY|CC0|Public domain|PD", lic, re.I) or ii.get("height", 0) < 500: continue
            n = 0
            while os.path.exists(os.path.join(d, f"{n}.jpg")): n += 1
            f = os.path.join(d, f"{n}.jpg")
            try:
                time.sleep(4)
                b = urllib.request.urlopen(urllib.request.Request(ii["thumburl"], headers=UA), timeout=60).read()
                if len(b) < 5000: continue
                open(f, "wb").write(b)
            except Exception as e:
                print("erro", e); time.sleep(30); continue
            ja.add(p["title"]); tem += 1
            cred[f"{slug(nome)}/{n}.jpg"] = {"arquivo": p["title"], "autor": re.sub("<[^>]+>", "", md.get("Artist", {}).get("value", ""))[:120],
                                            "licenca": lic, "pagina": ii.get("descriptionurl")}
            json.dump(cred, open(cf, "w"), ensure_ascii=False, indent=1)
    print(nome, tem, flush=True)
