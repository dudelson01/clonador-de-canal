#!/usr/bin/env python3
"""Teste mais direto de palavra cortada: para cada trecho do plano, transcreve o audio ORIGINAL do trecho
e o mesmo trecho no video DECUPADO (mesmo modelo, mesmo prompt) e compara palavra por palavra.
Palavra que existe no original e falta no corte = palavra comida pela decupagem.
Uso: python3 comparar_trechos.py plano_decupagem.json pasta_decupagem [modelo=medium]"""
import difflib, json, os, re, subprocess, sys, unicodedata
import numpy as np
from faster_whisper import WhisperModel

def norm(s):
    s = unicodedata.normalize("NFD", s.lower()); s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9 ]", " ", s).split()

def audio(arq):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", arq, "-map", "0:a:0", "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32)

plano = json.load(open(sys.argv[1])); pasta = sys.argv[2]; modelo = sys.argv[3] if len(sys.argv) > 3 else "medium"
D = json.load(open(os.path.join(pasta, "decupagem.json")))
A = {k: audio(v) for k, v in plano["tomadas"].items()}; C = audio(os.path.join(pasta, "decupado.mp4"))
m = WhisperModel(modelo, device="cpu", compute_type="int8")
def txt(a, s, e):
    segs, _ = m.transcribe(a[int(max(0, s) * 16000): int(e * 16000)], language="pt", vad_filter=False,
                           condition_on_previous_text=False, temperature=0.0)
    return [t for x in segs for t in norm(x.text)]
ruins = 0
for n, tr in enumerate(plano["trechos"]):
    ps = [p for p in D if p["n"] == n]
    if not ps: print(f"#{n} SUMIU INTEIRO: {tr.get('obs','')}"); ruins += 1; continue
    # original = a frase PEDIDA inteira (nao so o que sobrou), senao palavra comida na borda nao aparece
    o = txt(A[ps[0]["t"]], min(tr.get("ini", 1e9), min(p["s"] for p in ps)) - 0.05, max(tr.get("fim", 0), max(p["e"] for p in ps)) + 0.05)
    c = txt(C, ps[0]["dst_s"] - 0.02, ps[-1]["dst_e"] + 0.02)
    perdas = []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, o, c, autojunk=False).get_opcodes():
        if op in ("delete", "replace") and (op == "delete" or i2 - i1 > j2 - j1):
            perdas.append(" ".join(o[i1:i2]) + (f" -> '{' '.join(c[j1:j2])}'" if op == "replace" else ""))
    if perdas:
        ruins += 1
        t = ps[0]["dst_s"]
        print(f"#{n} {int(t//60)}:{t%60:04.1f}  original: {' '.join(o)}\n      corte:    {' '.join(c)}\n      faltou: {perdas}", flush=True)
print("trechos com palavra faltando:", ruins, "de", len(plano["trechos"]))
