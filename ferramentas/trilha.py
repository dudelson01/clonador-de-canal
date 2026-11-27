"""Trilha original sintetizada: synth nostálgico (pad + arpejo + batida leve), uma "faixa" por capítulo.

Uso: python trilha.py <narracao.wav.secoes.json> <saida.wav>
Cada capítulo recebe uma progressão/andamento diferente (sensação de progresso), com crossfade de 2 s entre eles.
Tudo gerado aqui com numpy: sem direitos de terceiros.
"""
import json, sys, wave
import numpy as np

SR = 48000
NOTAS = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5, "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}
# (andamento, progressão de acordes [raiz, tipo]) — tipo m = menor
FAIXAS = [
    (78, [("A", "m"), ("F", ""), ("C", ""), ("G", "")]),      # gancho: melancólico
    (86, [("C", ""), ("A", "m"), ("F", ""), ("G", "")]),      # ascensão: nostalgia anos 80
    (92, [("D", ""), ("B", "m"), ("G", ""), ("A", "")]),      # auge: mais claro
    (80, [("E", "m"), ("C", ""), ("G", ""), ("D", "")]),      # primeira rachadura
    (84, [("D", "m"), ("A#", ""), ("F", ""), ("C", "")]),     # Amazon
    (72, [("C", "m"), ("G#", ""), ("D#", ""), ("A#", "")]),   # o acordo: tenso
    (68, [("A", "m"), ("E", "m"), ("F", ""), ("E", "")]),     # a queda
    (74, [("F", ""), ("D", "m"), ("A#", ""), ("C", "")]),     # o que matou
    (82, [("G", ""), ("E", "m"), ("C", ""), ("D", "")]),      # o retorno: esperança
]


def hz(semi):  # semitons a partir do A4 = 440
    return 440 * 2 ** (semi / 12)


def acorde(raiz, tipo, oit=-1):
    r = NOTAS[raiz] - 9 + 12 * oit
    return [r, r + (3 if tipo == "m" else 4), r + 7]


def lp(x, fc):
    from scipy.signal import lfilter
    a = np.exp(-2 * np.pi * fc / SR)
    return lfilter([1 - a], [1, -a], x)


def faixa(dur, bpm, prog, seed):
    rng = np.random.default_rng(seed)
    n = int(dur * SR); t = np.arange(n) / SR
    beat = 60 / bpm; compasso = 4 * beat
    out = np.zeros(n)
    k = 0
    while k * compasso < dur:
        raiz, tipo = prog[k % len(prog)]
        a0, a1 = int(k * compasso * SR), min(n, int((k + 1) * compasso * SR))
        tt = t[a0:a1] - k * compasso
        env = np.minimum(1, tt / 0.4) * np.minimum(1, (compasso - tt) / 0.3 + 0.0)
        pad = np.zeros(a1 - a0)
        for s in acorde(raiz, tipo):
            for det in (-0.08, 0.08):
                f = hz(s + det)
                pad += 2 * ((tt * f) % 1) - 1  # serra desafinada
        out[a0:a1] += pad * env * 0.05
        # arpejo em colcheias, sino suave
        notas = acorde(raiz, tipo, oit=1) + [acorde(raiz, tipo, oit=2)[0]]
        for j in range(8):
            st = j * beat / 2
            b0 = a0 + int(st * SR)
            if b0 >= a1:
                break
            m = min(int(0.6 * SR), n - b0)
            tb = np.arange(m) / SR
            f = hz(notas[[0, 1, 2, 3, 2, 1, 2, 3][j]])
            out[b0:b0 + m] += (np.sin(2 * np.pi * f * tb) + 0.3 * np.sin(4 * np.pi * f * tb)) * np.exp(-tb * 6) * 0.10
        # baixo + batida leve (bumbo no 1 e 3, chimbal suave nos contratempos)
        for j in range(4):
            b0 = a0 + int(j * beat * SR); m = min(int(0.35 * SR), n - b0)
            if m <= 0:
                continue
            tb = np.arange(m) / SR
            if j in (0, 2):
                out[b0:b0 + m] += np.sin(2 * np.pi * (50 + 70 * np.exp(-tb * 35)) * tb) * np.exp(-tb * 10) * 0.30
                fb = hz(acorde(raiz, tipo, oit=-2)[0])
                out[b0:b0 + m] += np.sin(2 * np.pi * fb * tb) * np.exp(-tb * 4) * 0.12
            h0 = b0 + int(beat / 2 * SR); mh = min(int(0.05 * SR), n - h0)
            if mh > 0:
                th = np.arange(mh) / SR
                out[h0:h0 + mh] += rng.normal(0, 1, mh) * np.exp(-th * 120) * 0.025
        k += 1
    return lp(out, 5000)


def main():
    sec = json.load(open(sys.argv[1], encoding="utf-8"))
    caps = sec["capitulos"]; total = sec["duracao"] + 3
    y = np.zeros(int(total * SR)); X = 2.0
    for i, c in enumerate(caps):
        a = max(0.0, c["inicio"] - (X if i else 0)); z = (caps[i + 1]["inicio"] + X) if i + 1 < len(caps) else total
        bpm, prog = FAIXAS[i % len(FAIXAS)]
        f = faixa(z - a, bpm, prog, i)
        rampa = np.ones(len(f)); nx = int(X * SR)
        if i:
            rampa[:nx] = np.linspace(0, 1, nx)
        if i + 1 < len(caps):
            rampa[-nx:] = np.linspace(1, 0, nx)
        k = int(a * SR); y[k:k + len(f)] += (f * rampa)[: len(y) - k]
    y = y / (np.abs(y).max() + 1e-9) * 0.8
    with wave.open(sys.argv[2], "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((y * 32767).astype(np.int16).tobytes())
    print(f"ok: {sys.argv[2]} ({total/60:.1f} min, {len(caps)} faixas)")


if __name__ == "__main__":
    main()
