"""Busca e baixa fotos reais e livres do Wikimedia Commons (não precisa de chave).

Uso:
  python commons.py buscar <buscas.json> <pasta_candidatos>   → baixa até N candidatos por busca + folhas de contato
  python commons.py baixar <escolhas.json> <pasta_img> <creditos.txt>  → baixa a escolhida em alta e anota o crédito

buscas.json   = {"i01": "Toys R Us store closing 2018", ...}  (ou {"i01": {"q": "...", "n": 8}})
escolhas.json = {"i01": "File:Nome do arquivo.jpg", ...}
Só aceita licenças livres (domínio público, CC0, CC BY, CC BY-SA). O crédito vai para creditos.txt (obrigatório na descrição).
"""
import json, os, re, sys, time
import requests
from PIL import Image, ImageDraw, ImageFont

API = "https://commons.wikimedia.org/w/api.php"
# A Wikimedia exige um contato no User-Agent (política de robôs). O aluno define COMMONS_CONTACT no .env;
# nunca grave o contato neste arquivo.
def _contato():
    c = os.environ.get("COMMONS_CONTACT", "")
    env = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
    if not c and os.path.exists(env):
        for l in open(env, encoding="utf-8"):
            if l.startswith("COMMONS_CONTACT="):
                c = l.split("=", 1)[1].strip()
    return c


UA = {"User-Agent": f"ClonadorDeCanal/1.0 (video documentary research; {_contato() or 'no contact'}) python-requests"}
LIVRE = re.compile(r"public domain|pd|cc0|cc[- ]by(?![- ]?nc)(?![- ]?nd)", re.I)


def api(params):
    for t in range(6):
        r = requests.get(API, params={**params, "format": "json"}, headers=UA, timeout=60)
        if r.status_code == 429:
            time.sleep(5 * (t + 1)); continue
        r.raise_for_status(); return r.json()
    raise SystemExit("Commons recusou (429) várias vezes; tente mais tarde")


def limpa(html):
    return re.sub(r"<[^>]+>", "", html or "").strip()


def buscar(q, n=8, largura=1280):
    d = api({"action": "query", "generator": "search", "gsrsearch": f"{q} filetype:bitmap", "gsrnamespace": 6, "gsrlimit": n * 2,
             "prop": "imageinfo", "iiprop": "url|size|extmetadata|mime", "iiurlwidth": largura})
    out = []
    for p in sorted(d.get("query", {}).get("pages", {}).values(), key=lambda p: p.get("index", 0)):
        ii = (p.get("imageinfo") or [{}])[0]
        md = ii.get("extmetadata", {})
        lic = limpa(md.get("LicenseShortName", {}).get("value"))
        if ii.get("mime") not in ("image/jpeg", "image/png") or ii.get("width", 0) < 800 or not LIVRE.search(lic):
            continue
        url = (ii.get("thumburl") or ii["url"]).split("?")[0].replace("//thumb.wikimedia.org/", "//upload.wikimedia.org/")
        out.append({"titulo": p["title"], "url": url, "w": ii["width"], "h": ii["height"],
                    "licenca": lic, "autor": limpa(md.get("Artist", {}).get("value"))[:120],
                    "pagina": ii.get("descriptionurl"), "data": limpa(md.get("DateTimeOriginal", {}).get("value"))[:30]})
        if len(out) >= n:
            break
    return out


def baixa(url, dest):
    for t in range(8):
        r = requests.get(url, headers=UA, timeout=120)
        if r.status_code == 429:
            time.sleep(10 * (t + 1)); continue
        r.raise_for_status(); open(dest, "wb").write(r.content); return
    raise SystemExit(f"falhou: {url}")


def folha(itens, dest, rotulo):
    f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
    tw, th = 400, 250
    im = Image.new("RGB", (tw * 4, (th + 40) * ((len(itens) + 3) // 4) + 40), "white")
    d = ImageDraw.Draw(im); d.text((8, 8), rotulo[:150], fill="black", font=f)
    for k, (arq, meta) in enumerate(itens):
        try:
            t = Image.open(arq).convert("RGB"); t.thumbnail((tw - 8, th - 8))
        except Exception:
            continue
        x, y = (k % 4) * tw, 40 + (k // 4) * (th + 40)
        im.paste(t, (x + 4, y + 4)); d.text((x + 4, y + th), f"{k}: {meta['titulo'][5:45]}", fill="black", font=f)
    im.save(dest, quality=85)


def main():
    modo = sys.argv[1]
    if modo == "buscar":
        buscas = json.load(open(sys.argv[2], encoding="utf-8")); pasta = sys.argv[3]
        os.makedirs(pasta, exist_ok=True)
        idx_path = os.path.join(pasta, "candidatos.json")
        idx = json.load(open(idx_path, encoding="utf-8")) if os.path.exists(idx_path) else {}
        for cid, b in buscas.items():
            q, n = (b, 8) if isinstance(b, str) else (b["q"], b.get("n", 8))
            if cid in idx and idx[cid]["q"] == q:
                continue
            res = buscar(q, n); time.sleep(1)
            itens = []
            for k, r in enumerate(res):
                arq = os.path.join(pasta, f"{cid}_{k}.jpg")
                if not os.path.exists(arq):
                    try:
                        baixa(re.sub(r"/\d+px-", "/500px-", r["url"]) if "/thumb/" in r["url"] else r["url"], arq); time.sleep(0.5)
                    except Exception as e:
                        print("  erro", e); continue
                itens.append((arq, r))
            idx[cid] = {"q": q, "res": res}
            folha(itens, os.path.join(pasta, f"folha_{cid}.jpg"), f"{cid}: {q}")
            print(f"{cid}: {len(res)} candidatos ({q})")
            json.dump(idx, open(idx_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    elif modo == "baixar":
        esc = json.load(open(sys.argv[2], encoding="utf-8")); pasta = sys.argv[3]; cred = sys.argv[4]
        idx = json.load(open(os.path.join(os.path.dirname(sys.argv[2]), "candidatos", "candidatos.json"), encoding="utf-8"))
        linhas = []
        for cid, titulo in esc.items():
            meta = next(r for v in idx.values() for r in v["res"] if r["titulo"] == titulo)
            dest = os.path.join(pasta, cid + ".webp")
            tmp = dest + ".dl"
            baixa(meta["url"], tmp); time.sleep(0.5)
            Image.open(tmp).convert("RGB").save(dest, quality=92); os.remove(tmp)
            linhas.append(f"{cid}: \"{titulo[5:]}\" — {meta['autor'] or 'autor desconhecido'} — {meta['licenca']} — {meta['pagina']}")
            print("  ok", cid, titulo)
        antigos = [l for l in (open(cred, encoding="utf-8").read().splitlines() if os.path.exists(cred) else [])
                   if l.split(":")[0] not in esc]
        open(cred, "w", encoding="utf-8").write("\n".join(sorted(antigos + linhas)) + "\n")


if __name__ == "__main__":
    main()
