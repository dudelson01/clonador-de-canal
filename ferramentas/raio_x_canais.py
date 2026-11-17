#!/usr/bin/env python3
"""Raio-x rapido de varios canais (so paginas de canal, sem abrir video).
Uso: python3 raio_x_canais.py saida.json @handle1 @handle2 ...
Para cada canal: inscritos, 100 videos longos mais recentes (views, duracao, titulo),
mediana, outliers (>=3x a mediana) e os 30 mais recentes."""
import json, sys, time, subprocess, statistics

def ytdlp(args):
    r = subprocess.run(["yt-dlp", *args], capture_output=True, text=True)
    if "HTTP Error 429" in r.stderr or "not a bot" in r.stderr:
        print("YouTube bloqueou. Parando (dados salvos)."); sys.exit(2)
    return r.stdout

out, handles = sys.argv[1], sys.argv[2:]
try: db = json.load(open(out))
except Exception: db = {}
for h in handles:
    h = h.split("?")[0].rstrip("/").split("/")[-1]
    if h in db: continue
    txt = ytdlp(["-J", "--flat-playlist", "--playlist-items", "1:100", f"https://www.youtube.com/{h}/videos"])
    try: d = json.loads(txt)
    except Exception: d = None
    if not isinstance(d, dict):
        db[h] = {"erro": "sem dados"}; print("sem dados:", h); continue
    vids = [{"id": e.get("id"), "titulo": e.get("title"), "views": e.get("view_count") or 0,
             "dur": e.get("duration")} for e in d.get("entries") or [] if e]
    vs = [v["views"] for v in vids if v["views"]]
    med = statistics.median(vs) if vs else 0
    for v in vids: v["x"] = round(v["views"] / med, 1) if med else None
    db[h] = {"nome": d.get("channel"), "inscritos": d.get("channel_follower_count"),
             "url": f"https://www.youtube.com/{h}", "n_lidos": len(vids), "mediana": med,
             "mediana_30_recentes": statistics.median([v["views"] for v in vids[:30]] or [0]),
             "dur_media_min": round(statistics.mean([v["dur"] for v in vids if v["dur"]] or [0]) / 60, 1),
             "videos": vids}
    json.dump(db, open(out, "w"), ensure_ascii=False, indent=1)
    print("ok:", h, d.get("channel"), d.get("channel_follower_count"), flush=True)
    time.sleep(3)
