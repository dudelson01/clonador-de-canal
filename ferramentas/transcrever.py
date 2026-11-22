"""Transcreve um áudio/vídeo com o tempo de cada palavra (Whisper) -> JSON {palavras, frases}.

Uso: python ferramentas/transcrever.py <entrada> <saida.json> [--modelo medium] [--prompt "texto inicial"]
O prompt com hesitações ("Ééé... então, tipo...") ajuda a achar falsas largadas na decupagem.
"""
import argparse, json, subprocess
import numpy as np
from faster_whisper import WhisperModel

p = argparse.ArgumentParser()
p.add_argument("entrada"); p.add_argument("saida")
p.add_argument("--modelo", default="medium"); p.add_argument("--prompt", default=None)
a = p.parse_args()
pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", a.entrada, "-vn", "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
                     capture_output=True, check=True).stdout
audio = np.frombuffer(pcm, np.int16).astype(np.float32) / 32768
m = WhisperModel(a.modelo, device="cpu", compute_type="int8")
segs, _ = m.transcribe(audio, language="pt", word_timestamps=True, vad_filter=True,
                       condition_on_previous_text=False, initial_prompt=a.prompt)
pal, fr = [], []
for s in segs:
    fr.append({"texto": s.text.strip(), "s": round(s.start, 3), "e": round(s.end, 3)})
    for w in s.words or []:
        pal.append({"w": w.word.strip(), "s": round(w.start, 3), "e": round(w.end, 3), "p": round(w.probability, 2)})
    print(f"[{s.start:7.1f}] {s.text.strip()}", flush=True)
json.dump({"palavras": pal, "frases": fr}, open(a.saida, "w"), ensure_ascii=False, indent=0)
print("ok", len(pal), "palavras")
