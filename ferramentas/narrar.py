"""Gera a narração completa de um roteiro .md, capítulo por capítulo, via ai33.pro.

Uso: python narrar.py <roteiro.md> <voice_id> <saida.wav> [--speed 1.0] [--model eleven_multilingual_v2]
- Lê só o texto falado: ignora título, marcações [VISUAL]/[3D]/[CADERNO], fontes {F#} e a lista de fontes.
- Gera cada capítulo (## ...) separado, junta com 0,5 s de pausa e normaliza para -14 LUFS.
- Salva também <saida>.secoes.json com início/fim de cada capítulo (para a edição).
"""
import argparse, json, os, re, subprocess, sys, tempfile
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tts_ai33 import tts  # noqa: E402


def capitulos(md):
    corpo = md.split("\n---\n", 1)[1]
    corpo = re.split(r"\n---\n", corpo)[0]  # corta a lista de fontes no fim
    caps = []
    for bloco in re.split(r"^## ", corpo, flags=re.M)[1:]:
        titulo, _, texto = bloco.partition("\n")
        texto = re.sub(r"\[[^\]]*\]", "", texto)
        texto = re.sub(r"\{F\d+\}", "", texto)
        texto = re.sub(r"[ \t]+", " ", texto)
        texto = "\n".join(l.strip() for l in texto.splitlines() if l.strip())
        texto = re.sub(r" +([.,!?;:])", r"\1", texto)
        if texto:
            caps.append({"titulo": titulo.strip(), "texto": texto})
    return caps


def dur(f):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("roteiro"); ap.add_argument("voice_id"); ap.add_argument("saida")
    ap.add_argument("--speed", type=float, default=1.0)
    ap.add_argument("--model", default="eleven_multilingual_v2")
    ap.add_argument("--tempo", type=float, default=1.0, help="acelera/desacelera o áudio final localmente (atempo)")
    a = ap.parse_args()
    caps = capitulos(open(a.roteiro, encoding="utf-8").read())
    tmp = tempfile.mkdtemp(prefix="narr_")
    cache = a.saida + ".caps"  # um mp3 por capítulo + o texto usado; só regera o que mudou
    os.makedirs(cache, exist_ok=True)
    arqs = [os.path.join(cache, f"{i:02d}.mp3") for i in range(len(caps))]

    def gera(i):
        txt = os.path.join(cache, f"{i:02d}.txt")
        if os.path.exists(arqs[i]) and os.path.exists(txt) and open(txt, encoding="utf-8").read() == caps[i]["texto"]:
            return 0
        c = tts(a.voice_id, caps[i]["texto"], arqs[i], a.model, a.speed)
        open(txt, "w", encoding="utf-8").write(caps[i]["texto"])
        print(f"  capítulo {i:02d} gerado ({c} créditos)")
        return c

    with ThreadPoolExecutor(3) as ex:
        custos = list(ex.map(gera, range(len(caps))))

    pausa = os.path.join(tmp, "pausa.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", "0.5", pausa], check=True)
    lista = os.path.join(tmp, "lista.txt"); t = 0.0
    with open(lista, "w") as L:
        for i, f in enumerate(arqs):
            w = os.path.join(tmp, f"{i:02d}.wav")
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f, "-ac", "1", "-ar", "44100", w], check=True)
            d = dur(w)
            caps[i].update(inicio=round(t / a.tempo, 2), fim=round((t + d) / a.tempo, 2)); t += d + 0.5
            L.write(f"file '{w}'\nfile '{pausa}'\n")
    bruto = os.path.join(tmp, "bruto.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lista, "-c", "copy", bruto], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", bruto, "-af", (f"atempo={a.tempo}," if a.tempo != 1.0 else "") + "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "44100", a.saida], check=True)
    palavras = sum(len(c["texto"].split()) for c in caps)
    total = dur(a.saida)
    json.dump({"duracao": round(total, 2), "palavras": palavras, "ppm": round(palavras / total * 60),
               "creditos": sum(c or 0 for c in custos), "capitulos": caps},
              open(a.saida + ".secoes.json", "w"), ensure_ascii=False, indent=1)
    print(f"ok: {a.saida} | {total/60:.1f} min | {palavras/total*60:.0f} ppm | créditos {sum(c or 0 for c in custos)}")


if __name__ == "__main__":
    main()
