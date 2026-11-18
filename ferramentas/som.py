#!/usr/bin/env python3
"""Trilha e efeitos sonoros ORIGINAIS, sintetizados com numpy (sem amostras de terceiros).
Uso:
  python3 som.py musica saida.wav duracao_s [clima=suspense|triste|tenso|final] [seed=1]
  python3 som.py partes saida.wav suspense:0:70 triste:70:195 tenso:195:268 final:268:362
  python3 som.py efeitos pasta_saida
Efeitos: whoosh, impacto, pop, carimbo, tecla, subida (riser), rebobinar. Todos curtos e contidos (sem chiado continuo)."""
import sys, os, wave, numpy as np

SR = 48000

def salva(arq, x, sr=SR):
    x = np.asarray(x, np.float64)
    if x.ndim == 1: x = np.stack([x, x], 1)
    pico = np.max(np.abs(x)) or 1
    x = x / pico * 0.89
    with wave.open(arq, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((x * 32767).astype("<i2").tobytes())

def env(n, a=0.005, r=0.1):
    t = np.arange(n) / SR; e = np.ones(n)
    ia = min(int(a * SR), n); ir = min(int(r * SR), n - ia)
    if ia: e[:ia] = np.linspace(0, 1, ia)
    if ir: e[-ir:] *= np.linspace(1, 0, ir) ** 2
    return e

def lp(x, fc):  # passa-baixa de 1 polo (fc pode variar no tempo)
    fc = np.broadcast_to(np.asarray(fc, float), x.shape)
    a = np.exp(-2 * np.pi * fc / SR); y = np.zeros_like(x); s = 0.0
    for i in range(len(x)):
        s = (1 - a[i]) * x[i] + a[i] * s; y[i] = s
    return y

def saw(f, n, det=0.0):
    t = np.arange(n) / SR; out = 0
    for d in (-det, 0, det):
        ph = (t * f * (1 + d)) % 1.0
        out = out + (2 * ph - 1)
    return out / 3

# ---------------- musica ----------------
CLIMAS = {
    # bpm, acordes (MIDI), brilho do filtro, mistura serra/seno no arpejo, volume do baixo
    "suspense": dict(bpm=92, acordes=[[57, 60, 64, 67], [53, 57, 60, 64], [50, 53, 57, 64], [52, 57, 59, 64]], brilho=1400, serra=1.0, baixo=0.22),
    "triste":   dict(bpm=74, acordes=[[48, 55, 60, 64], [45, 52, 57, 60], [41, 48, 53, 57], [43, 50, 55, 59]], brilho=900,  serra=0.35, baixo=0.12),
    "tenso":    dict(bpm=104, acordes=[[50, 53, 57, 62], [46, 50, 53, 58], [43, 46, 50, 55], [45, 49, 52, 57]], brilho=1700, serra=1.0, baixo=0.30),
    "final":    dict(bpm=84, acordes=[[53, 57, 60, 65], [48, 52, 55, 60], [45, 48, 52, 57], [43, 47, 50, 55]], brilho=1100, serra=0.55, baixo=0.16),
}

def musica(dur, seed=1, clima="suspense"):
    """Synth anos 80 ORIGINAL (arpejo em semicolcheias, baixo e pad), com progressoes proprias por clima."""
    C = CLIMAS[clima]
    semi = 60 / C["bpm"] / 4
    n = int(dur * SR); mix = np.zeros(n)
    nota = lambda m: 440 * 2 ** ((m - 69) / 12)
    acordes = C["acordes"]
    padrao = [0, 2, 1, 3, 2, 1, 0, 2, 3, 1, 2, 0, 1, 3, 2, 1]
    passo = int(semi * SR); compasso = 16 * passo
    for k in range(int(np.ceil(n / passo))):
        ac = acordes[(k // 16) % 4]
        i0 = k * passo; L = min(int(passo * 0.9), n - i0)
        if L <= 0: break
        m = ac[padrao[k % 16]] + (12 if (k // 32) % 2 and k % 4 == 3 else 0)
        t = np.arange(L) / SR; f = nota(m + 12)
        x = C["serra"] * saw(f, L, 0.004) + (1 - C["serra"]) * np.sin(2 * np.pi * f * t)
        x = x * env(L, 0.003, 0.08)
        x = lp(x, C["brilho"] + 700 * np.sin(2 * np.pi * (i0 + np.arange(L)) / SR / 8) ** 2)
        mix[i0:i0 + L] += 0.16 * x
        if k % 2 == 0:
            Lb = min(int(passo * 1.8), n - i0)
            b = saw(nota(ac[0] - 12), Lb, 0.002) * env(Lb, 0.004, 0.12)
            mix[i0:i0 + Lb] += C["baixo"] * lp(b, 420)
    for c in range(int(np.ceil(n / compasso))):
        ac = acordes[c % 4]; i0 = c * compasso; L = min(compasso + passo * 2, n - i0)
        if L <= 0: break
        p = sum(saw(nota(m), L, 0.006) for m in ac) / 4
        mix[i0:i0 + L] += 0.10 * lp(p, 700) * env(L, 0.6, 0.6)
    d = int(0.011 * SR); dir_ = np.concatenate([np.zeros(d), mix[:-d]])
    est = np.stack([mix * 0.9 + 0.1 * dir_, dir_ * 0.9 + 0.1 * mix], 1)
    return est * env(n, 1.0, 1.5)[:, None]

def trilha_por_partes(partes, saida):
    """partes = [(clima, inicio_s, fim_s), ...] -> uma faixa so, com troca suave (2 s) entre as partes."""
    total = partes[-1][2]; n = int(total * SR); out = np.zeros((n, 2)); X = int(2.0 * SR)
    for q, (clima, a, b) in enumerate(partes):
        i0 = max(0, int(a * SR) - X // 2); i1 = min(n, int(b * SR) + X // 2)
        seg = musica((i1 - i0) / SR, q + 1, clima)
        seg = seg / (np.max(np.abs(seg)) or 1)
        e = np.ones(i1 - i0)
        if q > 0: e[:X] = np.linspace(0, 1, X)
        if q < len(partes) - 1: e[-X:] = np.linspace(1, 0, X)
        out[i0:i1] += seg * e[:, None]
    salva(saida, out)

# ---------------- efeitos ----------------
def ruido_banda(n, f0, f1, q=0.3, seed=0):
    rng = np.random.default_rng(seed); w = rng.standard_normal(n)
    fc = np.geomspace(f0, f1, n)
    return lp(w, fc) - lp(w, fc * q)

def efeitos():
    E = {}
    n = int(0.42 * SR)    # whoosh: varredura curta de ruido filtrado, com envelope em sino
    s = ruido_banda(n, 300, 3500, 0.35, 1); e = np.sin(np.linspace(0, np.pi, n)) ** 2
    E["whoosh"] = s * e
    n = int(0.9 * SR); t = np.arange(n) / SR   # impacto: sub grave descendo + clique
    f = 95 * np.exp(-t * 3.5) + 38; ph = 2 * np.pi * np.cumsum(f) / SR
    E["impacto"] = np.sin(ph) * np.exp(-t * 4.5) + 0.25 * ruido_banda(n, 2000, 300, 0.3, 2) * np.exp(-t * 40)
    n = int(0.12 * SR); t = np.arange(n) / SR   # pop (etiqueta)
    E["pop"] = np.sin(2 * np.pi * (900 - 2500 * t) * t) * np.exp(-t * 38)
    n = int(0.5 * SR); t = np.arange(n) / SR    # carimbo: baque surdo + "tapa" curto
    E["carimbo"] = 0.9 * np.sin(2 * np.pi * 70 * t) * np.exp(-t * 14) + 0.5 * ruido_banda(n, 1800, 400, 0.4, 3) * np.exp(-t * 55)
    n = int(0.05 * SR); t = np.arange(n) / SR   # tecla de maquina de escrever
    E["tecla"] = ruido_banda(n, 4000, 1500, 0.5, 4) * np.exp(-t * 160) + 0.3 * np.sin(2 * np.pi * 180 * t) * np.exp(-t * 90)
    n = int(1.0 * SR); t = np.arange(n) / SR    # subida (antes de revelacao): tom subindo + ar
    f = 120 * 2 ** (t * 2.2); ph = 2 * np.pi * np.cumsum(f) / SR
    E["subida"] = (0.6 * np.sin(ph) + 0.3 * ruido_banda(n, 400, 6000, 0.4, 5)) * (t / t[-1]) ** 2 * env(n, 0.01, 0.03)
    n = int(0.6 * SR); t = np.arange(n) / SR    # rebobinar: whoosh ao contrario, mais agudo
    E["rebobinar"] = (ruido_banda(n, 4000, 500, 0.4, 6) * np.sin(np.linspace(0, np.pi, n)) ** 2)[::-1]
    return E

if __name__ == "__main__":
    if sys.argv[1] == "musica":
        dur = float(sys.argv[3]); clima = sys.argv[4] if len(sys.argv) > 4 else "suspense"
        seed = int(sys.argv[5]) if len(sys.argv) > 5 else 1
        salva(sys.argv[2], musica(dur, seed, clima)); print("ok", sys.argv[2])
    elif sys.argv[1] == "partes":   # python3 som.py partes saida.wav suspense:0:70 triste:70:195 ...
        partes = [(x.split(":")[0], float(x.split(":")[1]), float(x.split(":")[2])) for x in sys.argv[3:]]
        trilha_por_partes(partes, sys.argv[2]); print("ok", sys.argv[2])
    elif sys.argv[1] == "efeitos":
        os.makedirs(sys.argv[2], exist_ok=True)
        for k, v in efeitos().items(): salva(os.path.join(sys.argv[2], k + ".wav"), v)
        print("ok efeitos:", ", ".join(efeitos().keys()))
