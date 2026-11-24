"""Narração via ai33.pro (API v3, assíncrona).

Uso:  python tts_ai33.py <voice_id> <arquivo_texto> <saida.mp3> [--model eleven_multilingual_v2] [--speed 1.0]
- voice_id: id da ElevenLabs com ou sem o prefixo "elevenlabs_".
- A chave da ai33 é injetada pelo ambiente; localmente, defina AI33_API_KEY no .env.
Fluxo: POST /v3/text-to-speech -> task_id -> GET /v3/task/{id} até status=done -> baixa data.audio_url.
"""
import argparse, json, os, sys, time
import requests

API = "https://api.ai33.pro"


def key():
    k = os.environ.get("AI33_API_KEY", "")
    env = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
    if not k and os.path.exists(env):
        for line in open(env, encoding="utf-8"):
            if line.startswith("AI33_API_KEY="):
                k = line.split("=", 1)[1].strip()
    return k or "dummy"  # no ambiente de nuvem o proxy injeta a chave real


def req(method, path, body=None):
    r = requests.request(method, API + path, json=body, timeout=120,
                         headers={"xi-api-key": key(), "User-Agent": "clonador-de-canal/1.0"})
    r.raise_for_status()
    return r.json()


def tts(voice_id, text, out, model="eleven_multilingual_v2", speed=1.0, stability=0.5, similarity=0.75):
    if not voice_id.startswith(("elevenlabs_", "minimax_", "fishaudio_")):
        voice_id = "elevenlabs_" + voice_id
    body = {"voice_id": voice_id, "text": text, "model_id": model,
            "voice_settings": {"stability": stability, "similarity_boost": similarity}}
    if abs(speed - 1.0) > 1e-3:
        body["speed"] = speed  # a ai33 aplica como pós-processamento (postprocess_speed)
    r = req("POST", "/v3/text-to-speech", body)
    if not r.get("success"):
        raise SystemExit(f"erro ao criar tarefa: {r}")
    tid = r["task_id"]
    for _ in range(600):
        t = req("GET", f"/v3/task/{tid}")["data"]
        if t["status"] == "done":
            url = t.get("metadata", {}).get("audio_url") or t.get("audio_url")
            a = requests.get(url, timeout=300, headers={"User-Agent": "clonador-de-canal/1.0"})
            a.raise_for_status()
            open(out, "wb").write(a.content)
            return t.get("credit_cost")
        if t["status"] in ("failed", "error"):
            raise SystemExit(f"tarefa falhou: {t}")
        time.sleep(3)
    raise SystemExit("tempo esgotado esperando a tarefa")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("voice_id"); ap.add_argument("texto"); ap.add_argument("saida")
    ap.add_argument("--model", default="eleven_multilingual_v2")
    ap.add_argument("--speed", type=float, default=1.0)
    a = ap.parse_args()
    cost = tts(a.voice_id, open(a.texto, encoding="utf-8").read().strip(), a.saida, a.model, a.speed)
    print(f"ok: {a.saida} (créditos: {cost})")
