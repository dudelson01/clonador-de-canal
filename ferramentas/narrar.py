"""Gera a narração completa de um roteiro.md, bloco por bloco, com cache.

Uso: python ferramentas/narrar.py <pasta_do_video> <voice_id> [--model eleven_v4] [--speed 1.0]

- Lê <pasta>/roteiro.md, separa os blocos pelos títulos "## [...]".
- Tira marcações ([CENA], [TELA], [ARTE], negrito, comentários).
- Gera cada bloco pela ai33 pro (cache em build/tts/<hash>.mp3: só paga o que mudou).
- Junta tudo em narracao.wav (48 kHz) e grava build/blocos.json com o início de cada bloco.
"""
import argparse, hashlib, json, pathlib, re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from ai33_tts import gerar

PAUSA_ENTRE_BLOCOS = 0.45  # segundos


def blocos_do_roteiro(md):
    md = re.sub(r"<!--.*?-->", "", md, flags=re.S)
    partes = re.split(r"^## \[(.+?)\].*$", md, flags=re.M)
    blocos = []
    for i in range(1, len(partes), 2):
        nome, corpo = partes[i], partes[i + 1]
        linhas = []
        for l in corpo.splitlines():
            l = re.sub(r"\*\*\[[^\]]*\]\*\*", "", l)   # **[CENA: ...]**
            l = l.replace("**", "").strip()
            if not l or l == "---" or l.startswith("#"):
                continue
            l = l.replace("&", "e").replace("…", "...")
            linhas.append(l)
        if linhas:
            # linha que não termina frase emenda na próxima (evita pausa no meio da frase)
            texto = ""
            for l in linhas:
                texto += l + ("\n" if re.search(r"[.!?:]$|\.\.\.$", l) else " ")
            blocos.append({"titulo": nome, "texto": texto.strip()})
    return blocos


def dur(f):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f],
                                capture_output=True, text=True).stdout)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("pasta"); p.add_argument("voice_id")
    p.add_argument("--model", default="eleven_v4"); p.add_argument("--speed", type=float, default=1.0)
    a = p.parse_args()
    pasta = pathlib.Path(a.pasta)
    build = pasta / "build" / "tts"; build.mkdir(parents=True, exist_ok=True)
    blocos = blocos_do_roteiro((pasta / "roteiro.md").read_text(encoding="utf-8"))

    def um(b):
        h = hashlib.sha1(f"{a.voice_id}|{a.model}|{a.speed}|{b['texto']}".encode()).hexdigest()[:12]
        mp3 = build / f"{h}.mp3"
        if not mp3.exists():
            gerar(a.voice_id, b["texto"], str(mp3), a.model, a.speed)
            print("gerado:", b["titulo"], flush=True)
        else:
            print("cache:", b["titulo"], flush=True)
        b["arquivo"] = str(mp3)
        return b

    with ThreadPoolExecutor(4) as ex:
        blocos = list(ex.map(um, blocos))

    # junta com pausa curta entre blocos
    lista = pasta / "build" / "concat.txt"
    silencio = pasta / "build" / "silencio.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=mono",
                    "-t", str(PAUSA_ENTRE_BLOCOS), str(silencio)], check=True)
    t = 0.0; linhas = []
    for i, b in enumerate(blocos):
        wav = pathlib.Path(b["arquivo"]).with_suffix(".wav")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", b["arquivo"], "-ar", "48000", "-ac", "1", str(wav)], check=True)
        b["ini"] = round(t, 3); t += dur(str(wav)); b["fim"] = round(t, 3)
        linhas.append(f"file '{wav.resolve()}'")
        if i < len(blocos) - 1:
            linhas.append(f"file '{silencio.resolve()}'"); t += PAUSA_ENTRE_BLOCOS
    lista.write_text("\n".join(linhas))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lista),
                    "-ar", "48000", "-ac", "1", str(pasta / "narracao.wav")], check=True)
    (pasta / "build" / "blocos.json").write_text(json.dumps(
        [{k: b[k] for k in ("titulo", "ini", "fim", "texto")} for b in blocos], ensure_ascii=False, indent=1))
    print(f"narracao.wav: {t/60:.1f} min, {len(blocos)} blocos")


if __name__ == "__main__":
    main()
