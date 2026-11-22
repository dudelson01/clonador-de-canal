"""Monta um bloco de vídeo: cenas (com zoom lento e efeitos) + artes com alfa + som mixado.

Uso como módulo:
  montar(cenas, artes_mov, som_wav, saida_mp4, preview=False)
  cena = {"src": "arquivo.mp4", "ss": 12.3, "dur": 2.4, "vel": 1.0, "zoom": 0.06,
          "efeito": None | "filtro" | "escurece" | "pb", "espelhar": False}
"""
import subprocess, pathlib, tempfile, shutil

W, H, FPS = 1920, 1080, 30


def _cena(c, out, w, h):
    vel = c.get("vel", 1.0); dur = c["dur"]; z = c.get("zoom", 0.06)
    fonte = dur * vel + 0.1
    # zoom lento contínuo (sem tremer): escala cresce com o tempo, recorte central
    zf = f"(1+{z}*t/{dur:.3f})"
    vf = [f"setpts=PTS/{vel}" if vel != 1 else "null",
          f"scale={w}:{h}:force_original_aspect_ratio=increase", f"crop={w}:{h}",
          f"scale=w='ceil({w}*{zf}/2)*2':h='ceil({h}*{zf}/2)*2':eval=frame", f"crop={w}:{h}",
          "unsharp=5:5:0.4", "setsar=1"]
    ef = c.get("efeito")
    if ef == "filtro":
        vf.append("split[a][b];[b]gblur=sigma=14,eq=brightness=0.04[g];[a][g]blend=all_mode=lighten:all_opacity=0.5,eq=saturation=1.05:brightness=0.03")
    elif ef == "escurece":
        vf.append("eq=brightness=-0.08:saturation=0.9")
    elif ef == "pb":
        vf.append("hue=s=0")
    if c.get("espelhar"): vf.append("hflip")
    vf.append("vignette=PI/5")
    vf.append(f"fps={FPS},trim=duration={dur:.3f},setpts=PTS-STARTPTS,format=yuv420p")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(c["ss"]), "-t", f"{fonte:.3f}", "-i", c["src"],
                    "-filter_complex", ",".join(vf), "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "16",
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
