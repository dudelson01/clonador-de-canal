#!/usr/bin/env python3
"""Busca outliers no YouTube: views / inscritos alto em canal pequeno e video recente.
Uso: python3 outliers_busca.py saida.json "busca 1" "busca 2" ...
Etapa 1: ytsearch (flat) -> candidatos. Etapa 2: detalhe (inscritos, data) so dos melhores."""
import json, sys, time, subprocess, datetime

def run(args):
    r = subprocess.run(["yt-dlp", *args], capture_output=True, text=True)
    if "HTTP Error 429" in r.stderr or "not a bot" in r.stderr:
        print("YouTube bloqueou. Parando.", [l for l in r.stderr.splitlines() if "429" in l or "bot" in l][:2]); sys.exit(2)
    return r.stdout

def main():
    out, buscas = sys.argv[1], sys.argv[2:]
    try: cache = json.load(open(out))
    except Exception: cache = {}
    for b in buscas:
        if b in cache.get("_buscas", []): continue
        txt = run(["ytsearch25:" + b, "--flat-playlist", "-j"])
        for l in txt.splitlines():
            try: v = json.loads(l)
            except Exception: continue
            if not v.get("view_count"): continue
            cache.setdefault(v["id"], {"id": v["id"], "titulo": v.get("title"), "views": v["view_count"],
                "canal": v.get("channel"), "dur": v.get("duration"), "busca": b})
        cache.setdefault("_buscas", []).append(b)
        json.dump(cache, open(out, "w"), ensure_ascii=False)
        time.sleep(2)
    # detalhe: so quem tem views razoaveis e ainda sem inscritos
    cands = sorted([v for k, v in cache.items() if k != "_buscas" and "inscritos" not in v],
                   key=lambda v: -v["views"])[:int(60)]
    for v in cands:
        txt = run(["-j", "--skip-download", "--extractor-args", "youtube:skip=hls,dash,translated_subs", "--ignore-no-formats-error", "https://www.youtube.com/watch?v=" + v["id"]])
        try: d = json.loads(txt)
        except Exception: v["inscritos"] = None; continue
        v["inscritos"] = d.get("channel_follower_count")
        v["data"] = d.get("upload_date")
        v["canal_url"] = d.get("channel_url")
        json.dump(cache, open(out, "w"), ensure_ascii=False)
        time.sleep(1)

main()
