"""Busca e baixa fotos reais e livres do Wikimedia Commons (não precisa de chave).

Uso:
  python commons.py buscar <buscas.json> <pasta_candidatos>   → baixa até N candidatos por busca + folhas de contato
  python commons.py baixar <escolhas.json> <pasta_img> <creditos.txt>  → baixa a escolhida em alta e anota o crédito
  python commons.py usar   <escolhas.json> <pasta_img> <creditos.txt>  → igual, mas aproveita o candidato já baixado
                                                                         (a busca já baixa em 1280 px; só baixa se for menor)

buscas.json   = {"i01": "Toys R Us store closing 2018", ...}  (ou {"i01": {"q": "..." ou ["...", "..."], "n": 8}})
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


_ultimo = [0.0]


def get(url, **kw):
    """Uma requisição a cada INTERVALO s: a Wikimedia limita clientes automáticos (429) num IP compartilhado."""
    espera = _ultimo[0] + float(os.environ.get("COMMONS_INTERVALO", "3")) - time.time()
    if espera > 0:
        time.sleep(espera)
    _ultimo[0] = time.time()
    return requests.get(url, headers=UA, **kw)


def api(params):
    for t in range(20):
        r = get(API, params={**params, "format": "json"}, timeout=60)
        if r.status_code == 429:  # espera o que o servidor pede (retry-after), sem recuo crescente
            s = int(r.headers.get("retry-after", "30")) + 1
            print(f"  API 429, esperando {s} s", flush=True)
            time.sleep(s); continue
        r.raise_for_status(); return r.json()
    raise SystemExit("Commons recusou (429) várias vezes; tente mais tarde")


def limpa(html):
    return re.sub(r"<[^>]+>", "", html or "").strip()


def buscar(q, n=8):
    d = api({"action": "query", "generator": "search", "gsrsearch": f"{q} filetype:bitmap", "gsrnamespace": 6, "gsrlimit": n * 2,
             "prop": "imageinfo", "iiprop": "url|size|extmetadata|mime"})  # sem iiurlwidth: a API limita (429) quem pede miniaturas
    out = []
    for p in sorted(d.get("query", {}).get("pages", {}).values(), key=lambda p: p.get("index", 0)):
        ii = (p.get("imageinfo") or [{}])[0]
        md = ii.get("extmetadata", {})
        lic = limpa(md.get("LicenseShortName", {}).get("value"))
        if ii.get("mime") not in ("image/jpeg", "image/png") or ii.get("width", 0) < 800 or not LIVRE.search(lic):
            continue
        url = ii["url"].split("?")[0]  # original; tamanhos() monta as miniaturas
        out.append({"titulo": p["title"], "url": url, "w": ii["width"], "h": ii["height"],
                    "licenca": lic, "autor": limpa(md.get("Artist", {}).get("value"))[:120],
                    "pagina": ii.get("descriptionurl"), "data": limpa(md.get("DateTimeOriginal", {}).get("value"))[:30]})
        if len(out) >= n:
            break
    return out


def tamanhos(url, larguras):
    """URLs alternativas da mesma imagem. A Wikimedia limita (429) larguras fora da lista padrão e originais grandes;
    330, 960 e 1280 px costumam já estar prontas no cache."""
    if "/thumb/" not in url:  # original: monta a miniatura (só larguras menores que a imagem existem)
        m = re.match(r"(https://upload\.wikimedia\.org/wikipedia/commons)/(\w/\w\w)/([^/]+)$", url)
        if not m:
            return [url]
        url = f"{m[1]}/thumb/{m[2]}/{m[3]}/1280px-{m[3]}"
    return [re.sub(r"/\d+px-", f"/{w}px-", url) for w in larguras] + [re.sub(r"/thumb(/.+)/[^/]+$", r"\1", url)]


def baixa(url, dest, tentativas=8):
    urls = url if isinstance(url, list) else [url]
    for u in urls:
        for t in range(tentativas):
            r = get(u, timeout=120)
            if r.status_code == 429:  # o balde do IP é compartilhado: ~metade passa; tentar de novo no ritmo de get()
                continue
            if r.status_code == 404:
                break
            r.raise_for_status(); open(dest, "wb").write(r.content); return
    raise SystemExit(f"falhou: {urls[0]}")


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
            if cid in idx and idx[cid]["q"] == q:  # já buscado: só tenta de novo os candidatos que não baixaram
                res = idx[cid]["res"]
                if os.environ.get("COMMONS_SO_NOVOS") or all(os.path.exists(os.path.join(pasta, f"{cid}_{k}.jpg")) for k in range(len(res))):
                    continue
            else:
                res, vistos = [], set()
                for qq in (q if isinstance(q, list) else [q]):
                    for r in buscar(qq, n):
                        if r["titulo"] not in vistos:
                            vistos.add(r["titulo"]); res.append(r)
            itens = []
            for k, r in enumerate(res):
                arq = os.path.join(pasta, f"{cid}_{k}.jpg")
                if not os.path.exists(arq):
                    try:
                        baixa(tamanhos(r["url"], [w for w in (1280, 960) if w < r["w"]] or [330])[:1], arq)
                    except (Exception, SystemExit) as e:
                        print("  pulei", k, e); continue
                itens.append((arq, r))
            idx[cid] = {"q": q, "res": res}
            folha(itens, os.path.join(pasta, f"folha_{cid}.jpg"), f"{cid}: {q if isinstance(q, str) else ' | '.join(q)}")
            print(f"{cid}: {len(res)} candidatos ({q})", flush=True)
            json.dump(idx, open(idx_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    elif modo in ("baixar", "usar"):
        esc = json.load(open(sys.argv[2], encoding="utf-8")); pasta = sys.argv[3]; cred = sys.argv[4]
        idx = json.load(open(os.path.join(os.path.dirname(sys.argv[2]), "candidatos", "candidatos.json"), encoding="utf-8"))
        linhas = []
        for cid, titulo in esc.items():
            meta = next(r for v in idx.values() for r in v["res"] if r["titulo"] == titulo)
            dest = os.path.join(pasta, cid + ".webp")
            tmp = dest + ".dl"
            cand = [os.path.join(os.path.dirname(sys.argv[2]), "candidatos", f"{c}_{k}.jpg")
                    for c, v in idx.items() for k, r in enumerate(v["res"]) if r["titulo"] == titulo]
            cand = [c for c in cand if os.path.exists(c) and Image.open(c).width >= min(960, meta["w"])]
            if modo == "usar" and cand:
                Image.open(cand[0]).convert("RGB").save(dest, quality=92)
            else:
                baixa(tamanhos(meta["url"], [w for w in (1920, 1280, 960) if w < meta["w"]] or [330]), tmp)
                Image.open(tmp).convert("RGB").save(dest, quality=92); os.remove(tmp)
            linhas.append(f"{cid}: \"{titulo[5:]}\" — {meta['autor'] or 'autor desconhecido'} — {meta['licenca']} — {meta['pagina']}")
            print("  ok", cid, titulo)
        antigos = [l for l in (open(cred, encoding="utf-8").read().splitlines() if os.path.exists(cred) else [])
                   if l.split(":")[0] not in esc]
        open(cred, "w", encoding="utf-8").write("\n".join(sorted(antigos + linhas)) + "\n")


if __name__ == "__main__":
    main()
