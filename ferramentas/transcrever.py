#!/usr/bin/env python3
"""Transcreve audio/video com faster-whisper (CPU), com tempo de cada palavra.
Uso: python3 transcrever.py midia saida.json [modelo=small] [idioma=pt] [prompt_inicial]
Saida: {"segmentos":[{"s","e","texto"}], "palavras":[{"w","s","e","p"}]}  (p = probabilidade)"""
import json, sys, time
from faster_whisper import WhisperModel

midia, saida = sys.argv[1], sys.argv[2]
modelo = sys.argv[3] if len(sys.argv) > 3 else "small"
idioma = sys.argv[4] if len(sys.argv) > 4 else "pt"
prompt = sys.argv[5] if len(sys.argv) > 5 else None
t0 = time.time()
m = WhisperModel(modelo, device="cpu", compute_type="int8")
# decodifica com ffmpeg (16 kHz mono) para nao depender da versao do PyAV
import subprocess, numpy as np
raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", midia, "-map", "0:a:0", "-ac", "1", "-ar", "16000",
                      "-f", "f32le", "-"], capture_output=True, check=True).stdout
audio = np.frombuffer(raw, np.float32)
segs, info = m.transcribe(audio, language=None if idioma == "auto" else idioma, word_timestamps=True,
                          vad_filter=False, initial_prompt=prompt, condition_on_previous_text=False)
out = {"idioma": info.language, "duracao": info.duration, "segmentos": [], "palavras": []}
for s in segs:
    out["segmentos"].append({"s": round(s.start, 2), "e": round(s.end, 2), "texto": s.text.strip()})
    for w in s.words or []:
        out["palavras"].append({"w": w.word.strip(), "s": round(w.start, 2), "e": round(w.end, 2), "p": round(w.probability, 2)})
json.dump(out, open(saida, "w"), ensure_ascii=False, indent=0)
print(f"ok {saida}: {len(out['palavras'])} palavras em {time.time()-t0:.0f}s ({info.language})")
