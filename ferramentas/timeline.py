"""Transcreve narracao.wav com tempo de cada palavra e grava timeline.json.

Uso: python ferramentas/timeline.py <pasta_do_video> [--modelo medium]

timeline.json = {"palavras": [{"w","s","e"}], "frases": [{"texto","s","e"}], "blocos": [...]}
Também grava build/transcricao_conferencia.txt para comparar com o roteiro.
"""
import argparse, json, pathlib, subprocess
import numpy as np
from faster_whisper import WhisperModel


def main():
    p = argparse.ArgumentParser()
    p.add_argument("pasta"); p.add_argument("--modelo", default="medium")
    a = p.parse_args()
    pasta = pathlib.Path(a.pasta)
    pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", str(pasta / "narracao.wav"), "-ac", "1", "-ar", "16000",
                          "-f", "s16le", "-"], capture_output=True, check=True).stdout
    audio = np.frombuffer(pcm, np.int16).astype(np.float32) / 32768
    m = WhisperModel(a.modelo, device="cpu", compute_type="int8")
    segs, _ = m.transcribe(audio, language="pt", word_timestamps=True, vad_filter=False,
                           condition_on_previous_text=False)
    palavras, frases = [], []
    for s in segs:
        frases.append({"texto": s.text.strip(), "s": round(s.start, 3), "e": round(s.end, 3)})
        for w in s.words or []:
            palavras.append({"w": w.word.strip(), "s": round(w.start, 3), "e": round(w.end, 3)})
    blocos_f = pasta / "build" / "blocos.json"
    blocos = json.loads(blocos_f.read_text()) if blocos_f.exists() else []
    (pasta / "timeline.json").write_text(json.dumps(
        {"palavras": palavras, "frases": frases,
         "blocos": [{k: b[k] for k in ("titulo", "ini", "fim")} for b in blocos]}, ensure_ascii=False, indent=0))
    (pasta / "build" / "transcricao_conferencia.txt").write_text(
        "\n".join(f"[{f['s']:7.2f}] {f['texto']}" for f in frases), encoding="utf-8")
    print(len(palavras), "palavras,", len(frases), "frases")


if __name__ == "__main__":
    main()
