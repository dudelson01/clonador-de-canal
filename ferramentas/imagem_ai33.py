"""Gera imagens via ai33.pro (/v3/image, modelo Imagen 3, assíncrono).

Uso: python imagem_ai33.py <cenas.json> <pasta_saida> [--res 2K]
cenas.json = [{"id": "c01", "prompt": "...", "ratio": "16:9"}, ...]
Pula cenas que já têm arquivo na pasta (não gasta crédito de novo).
"""
import argparse, json, os, sys, time
from concurrent.futures import ThreadPoolExecutor
import requests

API = "https://api.ai33.pro"
H = {"xi-api-key": "dummy", "User-Agent": "clonador-de-canal/1.0"}  # no ambiente de nuvem o proxy injeta a chave


def _post(form):
    for t in range(6):
        r = requests.post(API + "/v3/image", files={k: (None, str(v)) for k, v in form.items()}, headers=H, timeout=120)  # multipart
        if r.status_code == 429 and t < 5:
            time.sleep(10 * (t + 1)); continue
        if r.status_code >= 400:
            raise SystemExit(f"erro {r.status_code}: {r.text[:300]}")
        return r.json()


def gera(cena, pasta, res):
    out = os.path.join(pasta, cena["id"] + ".webp")
    if os.path.exists(out):
        return 0
    r = _post({"prompt": cena["prompt"], "model_id": "image-v3", "aspect_ratio": cena.get("ratio", "16:9"), "resolution": res})
    if not r.get("success"):
        raise SystemExit(f"{cena['id']}: {r}")
    tid = r["task_id"]
    for _ in range(200):
        d = requests.get(f"{API}/v3/task/{tid}", headers=H, timeout=60).json()["data"]
        if d["status"] == "done":
            url = d["metadata"]["image_urls"][0]
            img = requests.get(url, headers=H, timeout=120); img.raise_for_status()
            open(out, "wb").write(img.content)
            print(f"  {cena['id']} ok ({d.get('credit_cost')} créditos)")
            return d.get("credit_cost") or 0
        if d["status"] in ("failed", "error"):
            print(f"  {cena['id']} FALHOU: {d.get('error') or d.get('metadata')}"); return 0
        time.sleep(3)
    print(f"  {cena['id']} tempo esgotado"); return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cenas"); ap.add_argument("pasta"); ap.add_argument("--res", default="2K")
    a = ap.parse_args()
    os.makedirs(a.pasta, exist_ok=True)
    cenas = json.load(open(a.cenas, encoding="utf-8"))
    with ThreadPoolExecutor(3) as ex:
        custos = list(ex.map(lambda c: gera(c, a.pasta, a.res), cenas))
    print(f"total: {sum(custos)} créditos")
