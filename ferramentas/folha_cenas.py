"""Detecta os cortes de um vídeo e monta uma folha de contato com o tempo de cada cena.

Uso: python ferramentas/folha_cenas.py <video.mp4> <saida.png> [--limiar 0.3] [--colunas 6]
Também grava <saida>.json com as cenas [{ini, fim}].
"""
import argparse, json, re, subprocess, pathlib, tempfile


def cortes(video, limiar=0.3):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", video, "-vf", f"scale=320:-1,select='gt(scene,{limiar})',showinfo",
                        "-an", "-f", "null", "-"], capture_output=True, text=True).stderr
    ts = [float(x) for x in re.findall(r"pts_time:([\d.]+)", r)]
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", video],
                               capture_output=True, text=True).stdout)
    b = [0.0] + ts + [dur]
    return [{"ini": round(b[i], 2), "fim": round(b[i + 1], 2)} for i in range(len(b) - 1) if b[i + 1] - b[i] > 0.4]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("video"); p.add_argument("saida")
    p.add_argument("--limiar", type=float, default=0.3); p.add_argument("--colunas", type=int, default=6)
    a = p.parse_args()
    cenas = cortes(a.video, a.limiar)
    pathlib.Path(a.saida).with_suffix(".json").write_text(json.dumps(cenas))
    with tempfile.TemporaryDirectory() as d:
        for i, c in enumerate(cenas):
            meio = (c["ini"] + c["fim"]) / 2
            txt = f"{i}  {c['ini']:.1f}-{c['fim']:.1f}"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(meio), "-i", a.video, "-frames:v", "1",
                            "-vf", f"scale=320:180:force_original_aspect_ratio=decrease,pad=320:180:(ow-iw)/2:(oh-ih)/2,"
                                   f"drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf:text='{txt}':"
                                   f"fontsize=18:fontcolor=yellow:box=1:boxcolor=black@0.7:x=4:y=4",
                            f"{d}/{i:03d}.png"])
        n = len(cenas); lin = -(-n // a.colunas)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", "1", "-i", f"{d}/%03d.png",
                        "-vf", f"tile={a.colunas}x{lin}:padding=4", "-frames:v", "1", a.saida])
    print(n, "cenas ->", a.saida)


if __name__ == "__main__":
    main()
