"""Monta um bloco de vídeo: cenas (com zoom lento e efeitos) + artes com alfa + som mixado.

Uso como módulo:
  montar(cenas, artes_mov, som_wav, saida_mp4, preview=False)
  cena = {"src": "arquivo.mp4", "ss": 12.3, "dur": 2.4, "vel": 1.0, "zoom": 0.06,
          "efeito": None | "filtro" | "escurece" | "pb", "espelhar": False}
"""
import subprocess, pathlib, tempfile, shutil

W, H, FPS = 1920, 1080, 30


def _cena(c, out, w, h):
    vel = c.get("vel", 1.0); dur = c["dur"]; z = c.get("zoom", 0.06); z0 = c.get("z0", 1.0)
    N = str(max(1, round(dur * FPS)))  # quadros exatos: sem isso a soma dos cortes vai atrasando a imagem
    fonte = dur * vel + 0.3
    # zoom lento contínuo (sem tremer): escala cresce com o tempo, recorte central; z0 = zoom inicial ("pulo de zoom")
    zf = f"({z0}+{z}*t/{dur:.3f})"
    vf = [f"setpts=PTS/{vel}" if vel != 1 else "null",
          f"scale={w}:{h}:force_original_aspect_ratio=increase", f"crop={w}:{h}",
          f"scale=w='ceil({w}*{zf}/2)*2':h='ceil({h}*{zf}/2)*2':eval=frame",
          (f"crop={w}:{h}:x='max(0,min(iw-{w},iw*{c['foco'][0]}-{w}/2))':y='max(0,min(ih-{h},ih*{c['foco'][1]}-{h}/2))'"
           if c.get("foco") else f"crop={w}:{h}"),
          "unsharp=5:5:0.4", "setsar=1"]
    ef = c.get("efeito")
    if ef == "filtro":
        vf.append("split[a][b];[b]gblur=sigma=14,eq=brightness=0.04[g];[a][g]blend=all_mode=lighten:all_opacity=0.5,eq=saturation=1.05:brightness=0.03")
    elif ef == "lavado":
        vf.append("eq=saturation=0.35:contrast=0.8:brightness=0.04:gamma=1.1")
    elif ef == "escurece":
        vf.append("eq=brightness=-0.08:saturation=0.9")
    elif ef == "pb":
        vf.append("hue=s=0")
    if c.get("espelhar"): vf.append("hflip")
    if not c.get("sem_vinheta"): vf.append("vignette=PI/5")
    vf.append(f"fps={FPS},setpts=PTS-STARTPTS,format=yuv420p")
    if c["src"].lower().endswith((".jpg", ".jpeg", ".png")):  # FOTO: zoom lento + fundo desfocado da própria foto
        z0 = c.get("z0", 1.0); z = c.get("zoom", 0.08)
        fc = (f"[0]scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},gblur=sigma=30,eq=brightness=-0.15[bg];"
              f"[0]scale=-2:{h}[fg];[bg][fg]overlay=(W-w)/2:0,"
              f"scale=w='ceil({w}*({z0}+{z}*t/{dur:.3f})/2)*2':h='ceil({h}*({z0}+{z}*t/{dur:.3f})/2)*2':eval=frame,crop={w}:{h},"
              f"fps={FPS},format=yuv420p")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-framerate", str(FPS), "-t", f"{dur + 0.5:.3f}", "-i", c["src"],
                        "-filter_complex", fc, "-frames:v", N, "-c:v", "libx264", "-preset", "veryfast", "-crf", "16", out], check=True)
        return
    if c["src"] == "ARTE":  # fundo de arte (sem cena): degradê escuro animado
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                        f"gradients=s={w}x{h}:c0=0x1b2430:c1=0x0b0b0e:x0=0:y0=0:x1={w}:y1={h}:speed=0.02:d={dur + 0.5:.3f}:r={FPS}",
                        "-vf", "vignette=PI/4,format=yuv420p", "-frames:v", N, "-c:v", "libx264", "-preset", "veryfast", "-crf", "16", out], check=True)
        return
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(c["ss"]), "-t", f"{fonte:.3f}", "-i", c["src"],
                    "-filter_complex", ",".join(vf), "-an", "-frames:v", N, "-c:v", "libx264", "-preset", "veryfast", "-crf", "16",
                    "-r", str(FPS), out], check=True)


def montar(cenas, artes_mov, som_wav, saida, preview=False):
    w, h = (960, 540) if preview else (W, H)
    d = pathlib.Path(tempfile.mkdtemp())
    try:
        lista = []
        for i, c in enumerate(cenas):
            o = d / f"c{i:03d}.mp4"; _cena(c, str(o), w, h); lista.append(f"file '{o}'")
        (d / "l.txt").write_text("\n".join(lista))
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(d / "l.txt"),
                        "-c", "copy", str(d / "base.mp4")], check=True)
        fc = f"[1]scale={w}:{h}[a];[0][a]overlay=0:0:format=auto,format=yuv420p[v]"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(d / "base.mp4"), "-i", artes_mov, "-i", som_wav,
                        "-filter_complex", fc, "-map", "[v]", "-map", "2:a",
                        "-c:v", "libx264", "-preset", "medium" if not preview else "veryfast", "-crf", "18",
                        "-r", str(FPS), "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest",
                        "-movflags", "+faststart", saida], check=True)
    finally:
        shutil.rmtree(d, ignore_errors=True)
    return saida


def base(cenas, saida, preview=False, paralelo=3):
    """Só as cenas (sem artes/som), concatenadas. Renderiza as cenas em paralelo."""
    from concurrent.futures import ThreadPoolExecutor
    w, h = (960, 540) if preview else (W, H)
    d = pathlib.Path(tempfile.mkdtemp())
    try:
        outs = [str(d / f"c{i:04d}.mp4") for i in range(len(cenas))]
        with ThreadPoolExecutor(paralelo) as ex:
            list(ex.map(lambda a: _cena(a[0], a[1], w, h), zip(cenas, outs)))
        (d / "l.txt").write_text("\n".join(f"file '{o}'" for o in outs))
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(d / "l.txt"),
                        "-c", "copy", saida], check=True)
    finally:
        shutil.rmtree(d, ignore_errors=True)
    return saida
