"""Baixa fotos de pessoas do Wikimedia Commons (licença livre) e anota créditos.

Uso: python ferramentas/fotos_commons.py <pasta_saida> "Nome 1" "Nome 2" ... [--n 5]
Salva <pasta>/<slug>/<k>.jpg e <pasta>/creditos.json (arquivo, autor, licença, página).
"""
import json, os, re, sys, time, urllib.parse, urllib.request

UA = {"User-Agent": "clonador-de-canal/1.0 (ferramenta de edicao)"}
API = "https://commons.wikimedia.org/w/api.php"


def get(params):
    url = API + "?" + urllib.parse.urlencode({**params, "format": "json"})
    for i in range(6):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40) as r:
                time.sleep(2)
                return json.load(r)
        except Exception:
            time.sleep(15 * (i + 1))  # 429: espera e tenta de novo
    return {}


def slug(s): return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def limpa(h): return re.sub(r"<[^>]+>", "", h or "").strip()


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    n = int(sys.argv[sys.argv.index("--n") + 1]) if "--n" in sys.argv else 5
    out, nomes = args[0], [a for a in args[1:] if not a.isdigit()]
    os.makedirs(out, exist_ok=True)
    cred_f = os.path.join(out, "creditos.json")
    cred = json.load(open(cred_f)) if os.path.exists(cred_f) else {}
    for nome in nomes:
        d = os.path.join(out, slug(nome)); os.makedirs(d, exist_ok=True)
        ii_ = {"prop": "imageinfo", "iiprop": "url|size|extmetadata|mime", "iiurlwidth": 1600}
        r = get({"action": "query", "generator": "categorymembers", "gcmtitle": f"Category:{nome}", "gcmtype": "file",
                 "gcmlimit": 30, **ii_})
        pages = list(r.get("query", {}).get("pages", {}).values())
        r2 = get({"action": "query", "generator": "search", "gsrnamespace": 6, "gsrlimit": 20,
                  "gsrsearch": f'intitle:"{nome}" filetype:bitmap', **ii_})
        vistos = {p["title"] for p in pages}
        pages += [p for p in sorted(r2.get("query", {}).get("pages", {}).values(), key=lambda p: p.get("index", 99))
                  if p["title"] not in vistos]
        existentes = len([x for x in os.listdir(d) if x.endswith(".jpg")])
        if existentes >= n: print(nome, "já tem", existentes); continue
        k = existentes
        for p in pages:
            if k >= n: break
            ii = (p.get("imageinfo") or [{}])[0]
            if ii.get("mime") not in ("image/jpeg", "image/png") or ii.get("height", 0) < 500: continue
            md = ii.get("extmetadata", {})
            lic = limpa(md.get("LicenseShortName", {}).get("value"))
            if not re.search(r"CC BY|CC0|Public domain|PD", lic, re.I): continue
            f = os.path.join(d, f"{k}.jpg")
            try:
                with urllib.request.urlopen(urllib.request.Request(ii.get("thumburl") or ii["url"], headers=UA), timeout=60) as resp:
                    open(f, "wb").write(resp.read())
            except Exception:
                time.sleep(10); continue
            cred[f"{slug(nome)}/{k}.jpg"] = {"arquivo": p["title"], "autor": limpa(md.get("Artist", {}).get("value"))[:120],
                                            "licenca": lic, "pagina": ii.get("descriptionurl")}
            k += 1; time.sleep(1.5)
            if k >= n: break
        print(nome, k, "fotos", flush=True); time.sleep(1)
    json.dump(cred, open(cred_f, "w"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
