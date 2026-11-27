#!/usr/bin/env python3
"""Mede o "vozeamento" (periodicidade) do audio em quadros de 10 ms: voz tem tom regular (nota da voz, 75-400 Hz);
respiracao, sopro e estalo nao tem. Devolve um valor 0..1 por quadro (autocorrelacao normalizada no melhor atraso).
Uso como modulo: periodicidade(arquivo) -> np.array (1 valor a cada 10 ms)
Uso direto: python3 vozeamento.py arquivo ini fim   (imprime o perfil)"""
import subprocess, sys, numpy as np

SR = 16000
def audio(arq):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", arq, "-map", "0:a:0", "-ac", "1", "-ar", str(SR),
                          "-af", "highpass=f=70,lowpass=f=1000", "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32)

def periodicidade(arq, quadro=0.010, janela=0.040):
    a = audio(arq); hop = int(SR * quadro); w = int(SR * janela)
    lmin, lmax = SR // 400, SR // 75
    n = max(0, (len(a) - w) // hop)
    out = np.zeros(n, np.float32)
    # processa em blocos para ir rapido (FFT da autocorrelacao)
    idx = np.arange(w)[None, :] + (np.arange(n) * hop)[:, None]
    for i0 in range(0, n, 4000):
        seg = a[idx[i0:i0 + 4000]] * np.hanning(w)[None, :]
        seg = seg - seg.mean(1, keepdims=True)
        F = np.fft.rfft(seg, 2 * w, axis=1)
        ac = np.fft.irfft(F * np.conj(F), axis=1)[:, :w]
        e = ac[:, :1] + 1e-9
        r = ac[:, lmin:lmax] / e
        out[i0:i0 + len(seg)] = np.clip(r.max(1), 0, 1)
    return out

if __name__ == "__main__":
    p = periodicidade(sys.argv[1]); a, b = float(sys.argv[2]), float(sys.argv[3])
    print(" ".join(f"{x:.2f}" for x in p[int(a * 100):int(b * 100)]))
