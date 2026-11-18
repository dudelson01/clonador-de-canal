#!/usr/bin/env python3
"""Monta um trecho editado (amostra ou bloco) a partir de um plano de cenas.
Uso: python3 montar.py plano.json saida.mp4 [--preview]
- cenas "rosto": imagem da fala decupada (mesmo tempo), com tratamento de cor escuro/cinema e zoom.
- cenas "video": trecho de fonte (trailer etc.), sem o som da fonte, com zoom lento e tapa-logo opcional.
- artes: PNG transparentes renderizados por ferramentas/artes/render_artes.mjs, sobrepostos no tempo.
- som: voz (da fala decupada) + trilha com ducking + efeitos; mix final -14 LUFS, pico -1.5 dBTP (loudnorm 2 passadas)."""
import json, os, subprocess, sys, re, hashlib

def chave(*objs):
    return hashlib.md5(json.dumps(objs, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:10]

FERR = os.path.dirname(os.path.abspath(__file__))
FPS = 30
GRADE_ROSTO = "eq=contrast=1.10:saturation=0.88:brightness=-0.035:gamma=0.97,vignette=angle=PI/4.2"
GRADE_VIDEO = "eq=contrast=1.04:saturation=1.0"
FOCO_ROSTO = (0.50, 0.36)   # onde fica o rosto no quadro (para o zoom centrar)

def sh(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode: print(r.stderr[-3000:]); sys.exit(1)
    return r

def zoom_filtro(z0, z1, dur, foco=(0.5, 0.5), W=1920, H=1080):
    n = max(1, round(dur * FPS))
    fx, fy = foco
    z = f"({z0}+({z1}-{z0})*on/{n})"
    # sobe a resolucao antes para o zoom lento nao tremer
    return (f"scale=3840:2160:flags=lanczos,zoompan=z='{z}':d=1:fps={FPS}:s={W}x{H}:"
            f"x='max(0,min(iw-iw/zoom,{fx}*iw-iw/zoom/2))':y='max(0,min(ih-ih/zoom,{fy}*ih-ih/zoom/2))'")

def main():
    plano = json.load(open(sys.argv[1])); saida = sys.argv[2]; preview = "--preview" in sys.argv
    base = os.path.dirname(os.path.abspath(sys.argv[1]))
    P = lambda p: os.path.join(base, p)
    tmp = P("build/montagem"); os.makedirs(tmp, exist_ok=True)
    i0, i1 = plano["inicio"], plano["fim"]
    # 1) cenas
    lista = []
    for k, c in enumerate(plano["cenas"]):
        dur = c["fim"] - c["ini"]; nq = round(dur * FPS)
        z0, z1 = c.get("zoom", [1, 1])
        arq = os.path.join(tmp, "cenas", f"{chave(c, plano.get('tapa_logo', {}).get(c.get('src')), GRADE_ROSTO, GRADE_VIDEO, preview)}.mp4")
        os.makedirs(os.path.dirname(arq), exist_ok=True)
        if os.path.exists(arq):   # cena igual ja renderizada: reaproveita
            lista.append(f"file '{arq}'"); continue
        if c["tipo"] == "rosto":
            ent = ["-ss", f"{c['ini']:.4f}", "-i", P(plano["fala"])]
            vf = f"{zoom_filtro(z0, z1, dur, tuple(c.get('foco', FOCO_ROSTO)))},{GRADE_ROSTO}"
        else:
            ent = ["-ss", f"{c['t']:.4f}", "-i", P(plano["fontes"][c["src"]])]
            logo = plano.get("tapa_logo", {}).get(c["src"])
            vf = (f"fps={FPS}," + (f"delogo={logo}," if logo else "") +
                  f"{zoom_filtro(z0, z1, dur, tuple(c.get('foco', (0.5, 0.5))))},{GRADE_VIDEO}")
        sh(["ffmpeg", "-loglevel", "error", "-y", *ent, "-an", "-vf", f"{vf},trim=end_frame={nq},setpts=PTS-STARTPTS,format=yuv420p",
            "-r", str(FPS), "-c:v", "libx264", "-preset", "veryfast" if preview else "medium", "-crf", "16", arq])
        lista.append(f"file '{arq}'")
    open(os.path.join(tmp, "cenas.txt"), "w").write("\n".join(lista))
    sh(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", os.path.join(tmp, "cenas.txt"), "-c", "copy", os.path.join(tmp, "base.mp4")])
    # 2) artes
    artes = plano.get("artes", [])
    html = open(os.path.join(FERR, "artes", "artes.html")).read()
    for a in artes:   # pasta da arte = id + assinatura (muda se a arte ou o desenho mudarem)
        a["_dir"] = os.path.join(tmp, "artes", a["id"] + "_" + chave({k: v for k, v in a.items() if k not in ("ini", "sfx", "_dir")}, html))
    falta = [dict(a, id=os.path.basename(a["_dir"])) for a in artes if not os.path.exists(os.path.join(a["_dir"], "0000.png"))]
    if falta:
        falta = [{k: v for k, v in a.items() if k != "_dir"} for a in falta]
        json.dump(falta, open(os.path.join(tmp, "artes.json"), "w"), ensure_ascii=False)
        sh(["node", os.path.join(FERR, "artes", "render_artes.mjs"), os.path.join(tmp, "artes.json"), os.path.join(tmp, "artes")])
    ent = ["-i", os.path.join(tmp, "base.mp4")]; fv = []; fc = []; ult = "[0:v]"
    for j, a in enumerate(artes):
        ent += ["-framerate", str(FPS), "-itsoffset", f"{a['ini'] - i0:.4f}", "-i", os.path.join(a["_dir"], "%04d.png")]
        fv.append(f"{ult}[{j+1}:v]overlay=eof_action=pass:format=auto[v{j}]"); ult = f"[v{j}]"
    # 3) som: voz + trilha (ducking) + efeitos
    na = len(artes) + 1
    ent += ["-ss", f"{i0:.4f}", "-t", f"{i1 - i0:.4f}", "-i", P(plano["fala"])]; voz = na; na += 1
    tr = plano.get("trilha")
    if tr:
        ent += ["-i", P(tr["arquivo"])]; mus = na; na += 1
    fx = []
    efd = P(plano.get("efeitos_dir", "midia/som/efeitos"))
    for c in plano["cenas"]:
        for nome, off in c.get("sfx", []): fx.append((nome, c["ini"] + off))
    for a in artes:
        if a.get("sfx") == "teclas":
            n = len(a["texto"]); vel = a.get("vel", 0.045)
            fx += [("tecla", a["ini"] + 0.05 + q * vel) for q in range(n) if a["texto"][q] != " "]
        elif a.get("sfx"): fx.append((a["sfx"], a["ini"]))
        if a["tipo"] == "carimbo": fx.append(("carimbo", a["ini"]))
        if a["tipo"] == "perigo": pass
    nivel = {"whoosh": -26, "impacto": -14, "pop": -24, "carimbo": -16, "tecla": -28, "subida": -24, "rebobinar": -22}
    fxl = []
    for q, (nome, t) in enumerate(fx):
        ent += ["-i", os.path.join(efd, nome + ".wav")]
        ms = int(max(0, t - i0) * 1000)
        fc.append(f"[{na}:a]volume={nivel.get(nome, -20)}dB,adelay={ms}|{ms}[fx{q}]"); fxl.append(f"[fx{q}]"); na += 1
    fc.append(f"[{voz}:a]aresample=48000,highpass=f=70,acompressor=threshold=-20dB:ratio=3:attack=5:release=120:makeup=2,asplit=2[vz][vzsc]")
    mix = ["[vz]"]
    if tr:
        fc.append(f"[{mus}:a]aresample=48000,volume={tr.get('volume_db', -20)}dB[mu0]")
        fc.append(f"[mu0][vzsc]sidechaincompress=threshold=0.03:ratio=4:attack=60:release=450:makeup=1[mu]")
        mix.append("[mu]")
    else:
        fc.append("[vzsc]anullsink")
    if fxl:
        fc.append(f"{''.join(fxl)}amix=inputs={len(fxl)}:normalize=0[fxs]"); mix.append("[fxs]")
    fc.append(f"{''.join(mix)}amix=inputs={len(mix)}:normalize=0:duration=first,atrim=0:{i1 - i0:.4f}[pre]")
    graf = ";".join(fc)
    # loudnorm 2 passadas
    medir = sh(["ffmpeg", "-hide_banner", "-y", *ent, "-filter_complex", graf + ";[pre]loudnorm=I=-14:TP=-2.0:LRA=11:print_format=json[aout]",
                "-map", "[aout]", "-f", "null", "-"])
    m = json.loads(re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", medir.stderr).group(0))
    ln = (f"loudnorm=I=-14:TP=-2.0:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:"
          f"measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true,aresample=48000")
    vmap = ult if artes else "[0:v]"
    sh(["ffmpeg", "-loglevel", "error", "-y", *ent, "-filter_complex", ";".join(fv + [graf]) + f";[pre]{ln}[aout]",
        "-map", vmap, "-map", "[aout]", "-t", f"{i1 - i0:.4f}", "-r", str(FPS),
        "-c:v", "libx264", "-preset", "veryfast" if preview else "slow", "-crf", "18", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", saida])
    print("ok", saida)

main()
