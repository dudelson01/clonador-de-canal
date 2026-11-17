#!/usr/bin/env python3
"""Acha canais pequenos crescendo num nicho.
Uso: python3 canais_crescendo.py saida.json "busca 1" "busca 2" ...
1) busca videos do ultimo mes (pagina de resultados com filtro) -> canais
2) abre a pagina /videos de cada canal: inscritos + views dos 30 videos mais recentes
3) calcula mediana recente / inscritos e o maior outlier recente.
Usa so paginas de busca e de canal (nao abre pagina de video)."""
import json, sys, time, subprocess, statistics, urllib.parse

MIN_VIEWS = 20000  # so mede canal com algum video recente acima disso
FILTRO_MES = "EgIIBA%3D%3D"  # filtro "este mes" da busca do YouTube

def ytdlp(args):
    r = subprocess.run(["yt-dlp", *args], capture_output=True, text=True)
    if "HTTP Error 429" in r.stderr or "not a bot" in r.stderr:
        print("YouTube bloqueou. Parando (dados salvos)."); sys.exit(2)
    return r.stdout

def main():
    out, buscas = sys.argv[1], sys.argv[2:]
    try: db = json.load(open(out))
    except Exception: db = {"buscas": [], "canais": {}}
    for b in buscas:
        if b in db["buscas"]: continue
        url = "https://www.youtube.com/results?search_query=" + urllib.parse.quote(b) + "&sp=" + FILTRO_MES
        for l in ytdlp(["--flat-playlist", "--playlist-items", "1:40", "-j", url]).splitlines():
            try: v = json.loads(l)
            except Exception: continue
            cid = v.get("channel_id")
            if not cid: continue
            c = db["canais"].setdefault(cid, {"nome": v.get("channel"), "url": v.get("channel_url") or "https://www.youtube.com/channel/" + cid, "buscas": [], "achados": []})
            if b not in c["buscas"]: c["buscas"].append(b)
            c["achados"].append({"id": v.get("id"), "titulo": v.get("title"), "views": v.get("view_count")})
        db["buscas"].append(b)
        json.dump(db, open(out, "w"), ensure_ascii=False, indent=1)
        print("busca ok:", b, "| canais:", len(db["canais"]), flush=True)
        time.sleep(3)
    for cid, c in db["canais"].items():
        if "inscritos" in c: continue
        if max((a["views"] or 0) for a in c["achados"]) < MIN_VIEWS: continue
        txt = ytdlp(["-J", "--flat-playlist", "--playlist-items", "1:30", c["url"] + "/videos"])
        try: d = json.loads(txt)
        except Exception: d = None
        if not isinstance(d, dict): c["inscritos"] = None; continue
        c["inscritos"] = d.get("channel_follower_count")
        vids = [{"id": e.get("id"), "titulo": e.get("title"), "views": e.get("view_count") or 0, "dur": e.get("duration")}
                for e in d.get("entries") or []]
        c["recentes"] = vids
        vs = [v["views"] for v in vids if v["views"]]
        if vs:
            med = statistics.median(vs)
            c["mediana"] = med
            c["mediana_por_insc"] = round(med / c["inscritos"], 2) if c["inscritos"] else None
            top = max(vids, key=lambda v: v["views"])
            c["top"] = top
            c["top_x_mediana"] = round(top["views"] / med, 1) if med else None
            c["top_x_insc"] = round(top["views"] / c["inscritos"], 1) if c["inscritos"] else None
        json.dump(db, open(out, "w"), ensure_ascii=False, indent=1)
        time.sleep(2)
    print("fim. canais:", len(db["canais"]))

main()
