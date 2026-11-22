"""Música original sintetizada com numpy (sem samples, sem chiado).

Uso: python ferramentas/musica.py <saida.wav> <segundos> [--estilo curioso|tenso|epico] [--bpm 96] [--seed 1]

Estilos:
  curioso  - pluck brincalhão + baixo quente + batida leve (humor/curiosidade)
  tenso    - pulso grave + pad menor + sino (suspense leve)
  epico    - acordes largos + tambor grave (fechamento)
"""
import argparse, numpy as np, wave

SR = 48000


def nota(n):  # n = semitons a partir de A4
    return 440.0 * 2 ** (n / 12)


def env(n, a=0.005, d=0.2, s=0.0, r=0.05, dur=None):
    t = np.arange(n) / SR
    e = np.minimum(1, t / max(a, 1e-4))
    dec = np.exp(-np.maximum(0, t - a) / max(d, 1e-4))
    e = e * (s + (1 - s) * dec)
    if dur is not None:
        rel = np.clip(1 - (t - dur) / r, 0, 1)
        e = e * np.where(t > dur, rel, 1)
    return e


def pluck(f, dur, brilho=0.5, rng=None):
    """Karplus-Strong (corda dedilhada)."""
    rng = rng or np.random.default_rng(0)
    n = int(dur * SR); p = max(2, int(SR / f))
    buf = rng.uniform(-1, 1, p) * 0.5
    out = np.zeros(n); k = 0
    a = 0.5 + 0.49 * brilho
    for i in range(n):
        out[i] = buf[k]
        nk = (k + 1) % p
        buf[k] = (a * buf[k] + (1 - a) * buf[nk]) * 0.996
        k = nk
    return out * env(n, 0.002, dur * 0.6)


def sine(f, dur, harm=(1,), amp=(1,)):
    t = np.arange(int(dur * SR)) / SR
    return sum(a * np.sin(2 * np.pi * f * h * t) for h, a in zip(harm, amp))


def kick(dur=0.35):
    t = np.arange(int(dur * SR)) / SR
    f = 50 + 110 * np.exp(-t * 28)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t * 9) * 0.9


def snap(dur=0.12, rng=None):
    rng = rng or np.random.default_rng(1)
    t = np.arange(int(dur * SR)) / SR
    tom = np.sin(2 * np.pi * 1800 * t) * np.exp(-t * 60)
    ruido = rng.uniform(-1, 1, len(t)) * np.exp(-t * 70)
    return (0.5 * tom + 0.35 * ruido) * 0.5


def hat(dur=0.05, rng=None):
    rng = rng or np.random.default_rng(2)
    t = np.arange(int(dur * SR)) / SR
    x = rng.uniform(-1, 1, len(t))
    x = np.diff(np.concatenate([[0], x]))  # agudo
    return x * np.exp(-t * 120) * 0.12


def lowpass(x, fc):
    a = np.exp(-2 * np.pi * fc / SR); y = np.zeros_like(x); z = 0.0
    for i, v in enumerate(x):
        z = (1 - a) * v + a * z; y[i] = z
    return y


def add(buf, x, pos):
    i = int(pos * SR)
    if i >= len(buf): return
    x = x[: len(buf) - i]; buf[i:i + len(x)] += x


def curioso(seg, bpm, rng):
    b = 60 / bpm; L = int(seg * SR) + SR
    mus = np.zeros(L)
    # progressão menor brincalhona: Am - F - C - E (em semitons de A4)
    prog = [(-12, [0, 3, 7]), (-16, [-4, 0, 3]), (-21, [3, 7, 10]), (-17, [-5, -1, 2])]
    melodias = [[12, 15, 19, 15, 17, 15, 12, None], [8, 12, 15, None, 12, 10, 8, 7],
                [10, 12, 15, 19, None, 17, 15, 12], [11, None, 14, 11, 7, None, 11, 14]]
    t = 0.0; compasso = 0
    while t < seg:
        raiz, ac = prog[compasso % 4]
        mel = melodias[compasso % 4]
        for beat in range(4):
            tb = t + beat * b
            add(mus, kick() * (0.9 if beat in (0, 2) else 0), tb)
            if beat in (1, 3): add(mus, snap(rng=rng), tb)
            for h in (0, 0.5):
                add(mus, hat(rng=rng), tb + h * b)
            # baixo pulsando em colcheias
            for h in (0, 0.5):
                f = nota(raiz - 12 + (7 if (beat == 3 and h) else 0))
                x = sine(f, b * 0.48, (1, 2, 3), (1, .35, .12)) * env(int(b * 0.48 * SR), .004, .18, .3, .03, b * .4)
                add(mus, x * 0.32, tb + h * b)
        # pluck: melodia em colcheias
        for i, n in enumerate(mel):
            if n is None: continue
            add(mus, pluck(nota(n - 12), b * 0.9, 0.55, rng) * 0.33, t + i * b / 2)
        # pad suave do acorde
        for n in ac:
            x = sine(nota(n - 12), 4 * b, (1, 2), (1, .2)) * env(int(4 * b * SR), .5, 3, .6, .4, 4 * b - .3)
            add(mus, x * 0.05, t)
        t += 4 * b; compasso += 1
    return mus[: int(seg * SR)]


def tenso(seg, bpm, rng):
    b = 60 / bpm; L = int(seg * SR) + SR; mus = np.zeros(L)
    prog = [(-12, [0, 3, 7]), (-14, [-2, 1, 5]), (-16, [-4, 0, 3]), (-17, [-5, -1, 2])]
    t = 0.0; c = 0
    while t < seg:
        raiz, ac = prog[c % 4]
        for i in range(8):
            x = sine(nota(raiz - 12), b * .45, (1, 2), (1, .3)) * env(int(b * .45 * SR), .003, .12, .2, .03, b * .35)
            add(mus, x * (0.35 if i % 2 == 0 else 0.22), t + i * b / 2)
        add(mus, kick() * .6, t); add(mus, kick() * .45, t + 2.5 * b)
        for n in ac:
            x = sine(nota(n - 12), 4 * b, (1, 1.003, 2), (1, .8, .15)) * env(int(4 * b * SR), 1, 3, .7, .5, 4 * b - .4)
            add(mus, x * .045, t)
        add(mus, sine(nota(ac[2] + 12), 2.5, (1, 2.76, 5.4), (1, .3, .1)) * env(int(2.5 * SR), .002, .7) * .08, t + 2 * b)
        t += 4 * b; c += 1
    return mus[: int(seg * SR)]


def epico(seg, bpm, rng):
    b = 60 / bpm; L = int(seg * SR) + SR; mus = np.zeros(L)
    prog = [(-12, [0, 3, 7]), (-16, [-4, 0, 3]), (-21, [3, 7, 10]), (-14, [-2, 2, 5])]
    t = 0.0; c = 0
    while t < seg:
        raiz, ac = prog[c % 4]
        for n in ac + [ac[0] + 12]:
            x = sine(nota(n - 12), 4 * b, (1, 2, 3, 4), (1, .5, .25, .12)) * env(int(4 * b * SR), .08, 2, .5, .4, 4 * b - .3)
            add(mus, lowpass(x, 2500) * .07, t)
        add(mus, sine(nota(raiz - 24), 4 * b, (1, 2), (1, .3)) * env(int(4 * b * SR), .02, 2, .4, .3, 4 * b - .2) * .3, t)
        for i in (0, 1.5, 2, 3, 3.5):
            add(mus, kick(.5) * .8, t + i * b)
        t += 4 * b; c += 1
    return mus[: int(seg * SR)]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("saida"); p.add_argument("seg", type=float)
    p.add_argument("--estilo", default="curioso"); p.add_argument("--bpm", type=float, default=96)
    p.add_argument("--seed", type=int, default=1)
    a = p.parse_args()
    rng = np.random.default_rng(a.seed)
    x = {"curioso": curioso, "tenso": tenso, "epico": epico}[a.estilo](a.seg, a.bpm, rng)
    # fade de entrada/saída e normalização
    n = len(x); f = int(1.5 * SR)
    x[:f] *= np.linspace(0, 1, f); x[-f:] *= np.linspace(1, 0, f)
    x = np.tanh(x * 1.2) / np.tanh(1.2)
    x = x / (np.abs(x).max() + 1e-9) * 0.8
    st = np.stack([x, np.roll(x, int(0.012 * SR)) * 0.92], 1)  # leve largura estéreo
    with wave.open(a.saida, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((st * 32767).astype(np.int16).tobytes())
    print("ok", a.saida)


if __name__ == "__main__":
    main()
