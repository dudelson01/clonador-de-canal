"""Transcreve a narração com tempo de cada palavra (faster-whisper) e salva a timeline.

Uso: python timeline.py <narracao.wav> <timeline.json> [--modelo medium] [--idioma en]
Saída: [{"w": "palavra", "i": inicio, "f": fim}, ...]  (formato usado por montar.py e corrigir_timeline.py)
Depois rode corrigir_timeline.py com o roteiro para acertar a grafia.
"""
import argparse, json
from faster_whisper import WhisperModel

ap = argparse.ArgumentParser()
ap.add_argument("audio"); ap.add_argument("saida")
ap.add_argument("--modelo", default="medium"); ap.add_argument("--idioma", default="en")
a = ap.parse_args()
m = WhisperModel(a.modelo, device="cpu", compute_type="int8")
segs, _ = m.transcribe(a.audio, language=a.idioma, word_timestamps=True, vad_filter=False)
tl = [{"w": w.word.strip(), "i": round(w.start, 2), "f": round(w.end, 2)} for s in segs for w in s.words if w.word.strip()]
json.dump(tl, open(a.saida, "w", encoding="utf-8"), ensure_ascii=False)
print(f"ok: {len(tl)} palavras, até {tl[-1]['f']:.1f}s")
