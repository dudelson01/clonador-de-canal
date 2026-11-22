"""Efeitos sonoros sintetizados (curtos, sem chiado contínuo).

Uso: python ferramentas/sfx.py <pasta_saida>   -> gera whoosh, impacto, pop, carimbo, tique, maquina, clarao, riser, ding
"""
import sys, pathlib, wave, numpy as np

SR = 48000
rng = np.random.default_rng(7)


def t_(d): return np.arange(int(d * SR)) / SR


def bp(x, lo, hi):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    X[(f < lo) | (f > hi)] = 0
    return np.fft.irfft(X, len(x))


def whoosh(d=0.38):
    t = t_(d); x = rng.uniform(-1, 1, len(t))
    # varredura de filtro: soma de bandas com envelope deslizante
    out = np.zeros_like(x)
    for i, (lo, hi) in enumerate([(300, 700), (700, 1500), (1500, 3000), (3000, 6000)]):
        c = (i + .5) / 4 * d
        out += bp(x, lo, hi) * np.exp(-((t - c) / (d / 4)) ** 2)
    return out * 0.9


def impacto(d=0.9):
    t = t_(d); f = 38 + 90 * np.exp(-t * 18)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 4.5)
    click = bp(rng.uniform(-1, 1, len(t)), 1500, 5000) * np.exp(-t * 90) * .5
    return np.tanh((body + click) * 1.6)


def pop(d=0.12):
    t = t_(d); f = 900 - 500 * t / d
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 35)


def carimbo(d=0.35):
    t = t_(d); baque = np.sin(2 * np.pi * (90 + 60 * np.exp(-t * 40)) * t) * np.exp(-t * 18)
    papel = bp(rng.uniform(-1, 1, len(t)), 800, 4000) * np.exp(-t * 45) * .6
    return np.tanh((baque + papel) * 1.4)


def tique(d=0.05):
    t = t_(d); return np.sin(2 * np.pi * 2400 * t) * np.exp(-t * 120) * .6


def maquina(d=0.07):
    t = t_(d); x = bp(rng.uniform(-1, 1, len(t)), 1200, 6000) * np.exp(-t * 110)
    return x + np.sin(2 * np.pi * 180 * t) * np.exp(-t * 80) * .4


def clarao(d=1.2):
    t = t_(d); x = sum(np.sin(2 * np.pi * f * t) / k for k, f in enumerate([220, 330, 440, 660, 880], 1))
    return x * np.exp(-t * 3.5) * np.minimum(1, t / .01) * .5 + impacto(d) * .6


def riser(d=1.5):
    t = t_(d); f = 200 * 2 ** (t / d * 2.5)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) + .4 * np.sin(2 * np.pi * np.cumsum(f * 1.5) / SR)
    return x * (t / d) ** 2 * .5


def ding(d=0.9):
    t = t_(d); return sum(np.sin(2 * np.pi * 1320 * h * t) * a for h, a in [(1, 1), (2.76, .3), (5.4, .1)]) * np.exp(-t * 5) * .5


def salvar(x, p):
    x = x / (np.abs(x).max() + 1e-9) * 0.9
    fade = min(len(x), int(.01 * SR)); x[-fade:] *= np.linspace(1, 0, fade)
    with wave.open(str(p), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((x * 32767).astype(np.int16).tobytes())


if __name__ == "__main__":
    out = pathlib.Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    for nome in ["whoosh", "impacto", "pop", "carimbo", "tique", "maquina", "clarao", "riser", "ding"]:
        salvar(globals()[nome](), out / f"{nome}.wav")
    print("ok", out)
