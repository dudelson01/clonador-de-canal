#!/usr/bin/env python3
"""Mede a edicao de um video de referencia: cortes, folhas de quadros e volume.
Uso: python3 medir_edicao.py video.mp4 pasta_saida [limiar_cena=0.3]
Gera: cortes.json, folha_XX.png (1 quadro a cada 4 s, 6x5), resumo impresso."""
import json, os, re, subprocess, sys, statistics

video, out = sys.argv[1], sys.argv[2]
lim = float(sys.argv[3]) if len(sys.argv) > 3 else 0.3
os.makedirs(out, exist_ok=True)
dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", video],
                           capture_output=True, text=True).stdout.strip())
# cortes (analisa em baixa resolucao para ir rapido; so o 1o stream de video)
r = subprocess.run(["ffmpeg", "-hide_banner", "-i", video, "-map", "0:v:0", "-vf",
                    f"scale=320:-2,select='gt(scene,{lim})',showinfo", "-f", "null", "-"],
                   capture_output=True, text=True)
cortes = [float(x) for x in re.findall(r"pts_time:([\d.]+)", r.stderr)]
planos = [b - a for a, b in zip([0] + cortes, cortes + [dur])]
def media(xs): return round(statistics.mean(xs), 2) if xs else None
intro = [p for p, t in zip(planos, [0] + cortes) if t < 60]
resto = [p for p, t in zip(planos, [0] + cortes) if t >= 60]
# volume
v = subprocess.run(["ffmpeg", "-hide_banner", "-i", video, "-map", "0:a:0", "-af", "ebur128", "-f", "null", "-"],
                   capture_output=True, text=True).stderr
lufs = re.findall(r"I:\s+(-?[\d.]+) LUFS", v)
res = {"duracao_s": round(dur, 1), "cortes": len(cortes), "cortes_por_min": round(len(cortes) / dur * 60, 1),
       "seg_por_plano_intro_60s": media(intro), "seg_por_plano_resto": media(resto),
       "mediana_plano": round(statistics.median(planos), 2), "maior_plano_s": round(max(planos), 1),
       "maior_plano_inicio": round(([0] + cortes)[planos.index(max(planos))], 1),
       "lufs": float(lufs[-1]) if lufs else None, "tempos_cortes": cortes}
json.dump(res, open(os.path.join(out, "cortes.json"), "w"), indent=1)
subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", video, "-map", "0:v:0", "-vf",
                "fps=1/4,scale=320:-2,tile=6x5", os.path.join(out, "folha_%02d.png")])
print(json.dumps({k: v for k, v in res.items() if k != "tempos_cortes"}, ensure_ascii=False))
