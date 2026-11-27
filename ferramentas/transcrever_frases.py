#!/usr/bin/env python3
"""Separa a gravacao em FALAS pelas pausas (energia do audio) e transcreve cada fala sozinha.
Assim cada tentativa de uma frase vira uma linha separada, com inicio e fim reais (o Whisper,
transcrevendo o arquivo inteiro, junta tentativas repetidas numa frase so e erra os tempos).
Uso: python3 transcrever_frases.py midia saida.json [modelo=medium] [pausa_min=0.45] [idioma=pt|auto]
(idioma=auto: detecta o idioma de cada fala; util para video com partes em ingles)
Saida: {"falas":[{"i","s","e","texto","palavras":[{"w","s","e","p"}]}]}  (tempos no arquivo original)"""
import json, subprocess, sys, time
import numpy as np
from faster_whisper import WhisperModel

midia, saida = sys.argv[1], sys.argv[2]
modelo = sys.argv[3] if len(sys.argv) > 3 else "medium"
PAUSA = float(sys.argv[4]) if len(sys.argv) > 4 else 0.45
IDIOMA = sys.argv[5] if len(sys.argv) > 5 else "pt"
SR, Q = 16000, 0.01
raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", midia, "-map", "0:a:0", "-ac", "1", "-ar", str(SR),
                      "-f", "f32le", "-"], capture_output=True, check=True).stdout
a = np.frombuffer(raw, np.float32)
filt = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", midia, "-map", "0:a:0", "-ac", "1", "-ar", str(SR),
                       "-af", "highpass=f=100,lowpass=f=3000", "-f", "f32le", "-"], capture_output=True, check=True).stdout
b = np.frombuffer(filt, np.float32); n = int(SR * Q)
db = 20 * np.log10(np.sqrt((b[: len(b) // n * n].reshape(-1, n) ** 2).mean(1)) + 1e-9)
piso = np.percentile(db, 10); lim = max(piso + 14, np.percentile(db, 60) - 24)
fala = db > lim
# blocos de fala separados por pausas >= PAUSA
blocos, ini, ult = [], None, None
for k, v in enumerate(fala):
    if v:
        if ini is None: ini = k
        elif (k - ult) * Q >= PAUSA: blocos.append((ini, ult)); ini = k
        ult = k
if ini is not None: blocos.append((ini, ult))
blocos = [(x, y) for x, y in blocos if (y - x) * Q >= 0.20]
print(f"{len(blocos)} falas (piso {piso:.0f} dB, limite {lim:.0f} dB)")
t0 = time.time()
m = WhisperModel(modelo, device="cpu", compute_type="int8")
out = {"falas": []}
for i, (x, y) in enumerate(blocos):
    s, e = max(0, x * Q - 0.15), min(len(a) / SR, (y + 1) * Q + 0.20)
    seg = a[int(s * SR): int(e * SR)]
    segs, inf = m.transcribe(seg, language=None if IDIOMA == "auto" else IDIOMA, word_timestamps=True, vad_filter=False,
                             condition_on_previous_text=False,
                             initial_prompt=None if IDIOMA == "auto" else "Ééé... então, tipo... então, tipo, eu, eu acho que... que o, o cinema...")
    ws = []
    for sg in segs:
        for w in sg.words or []:
            ws.append({"w": w.word.strip(), "s": round(s + w.start, 2), "e": round(s + w.end, 2), "p": round(w.probability, 2)})
    out["falas"].append({"i": i, "s": round(x * Q, 2), "e": round((y + 1) * Q, 2), "texto": " ".join(w["w"] for w in ws), "palavras": ws,
                         "idioma": inf.language, "p_idioma": round(inf.language_probability, 2)})
    if i % 20 == 0: print(f"  {i}/{len(blocos)} {time.time()-t0:.0f}s", flush=True)
json.dump(out, open(saida, "w"), ensure_ascii=False, indent=0)
print(f"ok {saida}: {len(blocos)} falas em {time.time()-t0:.0f}s")
