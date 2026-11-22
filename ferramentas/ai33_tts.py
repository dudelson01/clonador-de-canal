"""Gera narração pela ai33 pro (API no estilo ElevenLabs).

Uso: python ai33_tts.py <voice_id> <arquivo_texto> <saida.mp3> [--model eleven_v4] [--speed 1.0]

A chave vem do .env (AI33_API_KEY). Na nuvem, o proxy injeta a chave sozinho.
Nunca imprime a chave.
"""
import argparse, json, os, pathlib, sys, time, urllib.error, urllib.request

BASE = "https://api.ai33.pro"
RAIZ = pathlib.Path(__file__).resolve().parent.parent


def chave():
    env = RAIZ / ".env"
    if env.exists():
        for l in env.read_text(encoding="utf-8").splitlines():
            if l.startswith("AI33_API_KEY=") and l.split("=", 1)[1].strip():
                return l.split("=", 1)[1].strip()
    return os.environ.get("AI33_API_KEY", "proxy-injected")


def req(metodo, caminho, corpo=None, tentativas=5):
    for i in range(tentativas):
        try:
            return _req(metodo, caminho, corpo)
        except urllib.error.HTTPError as e:
            if e.code < 500 or i == tentativas - 1:
                raise
            time.sleep(3 * (i + 1))


def baixar(url, destino, tentativas=5):
    for i in range(tentativas):
        try:
            r = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(r, timeout=120) as resp, open(destino, "wb") as f:
                f.write(resp.read())
            return destino
        except Exception:
            if i == tentativas - 1:
                raise
            time.sleep(3 * (i + 1))


def _req(metodo, caminho, corpo=None):
    dados = json.dumps(corpo).encode() if corpo is not None else None
    r = urllib.request.Request(BASE + caminho, data=dados, method=metodo,
                               headers={"xi-api-key": chave(), "Content-Type": "application/json"})
    with urllib.request.urlopen(r, timeout=60) as resp:
        return json.load(resp)


def gerar(voice_id, texto, saida, model="eleven_v4", speed=1.0, fmt="mp3_44100_192", timeout=600):
    if "_" not in voice_id.split("_")[0] and not voice_id.startswith(("elevenlabs_", "minimax_", "clone_", "edge_", "kokoro_", "vbee_", "fishaudio_")):
        voice_id = "elevenlabs_" + voice_id  # API v3 exige o prefixo do provedor
    corpo = {"text": texto, "model_id": model, "voice_id": voice_id, "with_transcript": True,
             "voice_settings": {"speed": float(speed)}}
    r = req("POST", "/v3/text-to-speech", corpo)
    tid = r.get("task_id")
    if not r.get("success") or not tid:
        raise RuntimeError(f"falha ao criar tarefa: {r}")
    t0 = time.time()
    while True:
        d = req("GET", f"/v3/task/{tid}").get("data", {})
        st = str(d.get("status", "")).lower()
        if st == "done":
            break
        if st == "error":
            raise RuntimeError(f"erro na geração: {d}")
        if time.time() - t0 > timeout:
            raise TimeoutError("demorou demais")
        time.sleep(2)
    url = (d.get("metadata") or {}).get("audio_url")
    if not url:
        raise RuntimeError(f"sem audio_url: {d}")
    pathlib.Path(saida).parent.mkdir(parents=True, exist_ok=True)
    baixar(url, saida)
    srt = (d.get("metadata") or {}).get("srt_url")
    if srt:
        baixar(srt, str(pathlib.Path(saida).with_suffix(".srt")))
    return d


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("voice_id"); p.add_argument("texto"); p.add_argument("saida")
    p.add_argument("--model", default="eleven_v4"); p.add_argument("--speed", type=float, default=1.0)
    a = p.parse_args()
    d = gerar(a.voice_id, pathlib.Path(a.texto).read_text(encoding="utf-8"), a.saida, a.model, a.speed)
    print("ok:", a.saida, "| créditos usados:", d.get("credit_cost", d.get("cost", "?")))
