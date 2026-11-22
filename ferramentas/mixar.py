"""Mixa voz + música (com ducking suave) + efeitos, e normaliza para -14 LUFS / -1.5 dBTP.

Uso como módulo:
  mixar(voz_wav, saida_wav, ini, fim, musicas=[(wav, ini_s)], sfx=[(wav, t, ganho_db)],
        musica_db=-22, ducking_db=-7, sfx_bus_db=-6)
"""
import subprocess, json, re, wave, numpy as np

SR = 48000


def ler(path, ss=0, t=None, canais=2):
    cmd = ["ffmpeg", "-v", "error", "-ss", str(ss), "-i", str(path)] + (["-t", str(t)] if t else []) + \
          ["-ac", str(canais), "-ar", str(SR), "-f", "f32le", "-"]
    return np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.float32).reshape(-1, canais).copy()


def db(x): return 10 ** (x / 20)


def envelope_voz(v, janela=0.05):
    m = np.abs(v).mean(1); n = int(janela * SR)
    k = np.convolve(m, np.ones(n) / n, mode="same")
    ativo = (k > 0.01).astype(np.float32)
    # suaviza (ataque ~120 ms, soltura ~450 ms) para não "ir e voltar"
    out = np.zeros_like(ativo); z = 0.0
    a_at, a_rel = np.exp(-1 / (0.12 * SR)), np.exp(-1 / (0.45 * SR))
    for i, x in enumerate(ativo):
        a = a_at if x > z else a_rel
        z = a * z + (1 - a) * x; out[i] = z
    return out


def mixar(voz, saida, ini, fim, musicas=(), sfx=(), musica_db=-17, ducking_db=-7, sfx_bus_db=-8):
    dur = fim - ini; N = int(dur * SR)
    v = ler(voz, ini, dur)[:N]; v = np.pad(v, ((0, N - len(v)), (0, 0)))
    mus = np.zeros((N, 2), np.float32)
    for wav, t0 in musicas:
        m = ler(wav); i = int((t0 - ini) * SR)
        if i < 0: m = m[-i:]; i = 0
        m = m[: N - i]; mus[i:i + len(m)] += m
    duck = db(ducking_db * envelope_voz(v))[:, None]
    mus *= db(musica_db) * duck
    fx = np.zeros((N, 2), np.float32)
    for wav, t, g in sfx:
        s = ler(wav); i = int((t - ini) * SR)
        if i < 0 or i >= N: continue
        s = s[: N - i]; fx[i:i + len(s)] += s * db(g)
    fx *= db(sfx_bus_db)
    mix = v + mus + fx
    tmp = saida + ".tmp.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-",
                    "-c:a", "pcm_f32le", tmp], input=np.clip(mix, -1, 1).astype(np.float32).tobytes(), check=True)
    # 2 passadas de loudnorm
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", tmp, "-af", "loudnorm=I=-14:TP=-2:LRA=11:print_format=json",
                        "-f", "null", "-"], capture_output=True, text=True).stderr
    j = json.loads(re.findall(r"\{[^{}]+\}", r)[-1])
    af = (f"loudnorm=I=-14:TP=-2:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:"
          f"measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-af", af, "-ar", str(SR), "-c:a", "pcm_s16le", saida], check=True)
    import os; os.remove(tmp)
    return saida
