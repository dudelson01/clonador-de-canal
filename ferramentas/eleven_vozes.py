"""Lista as vozes da conta ElevenLabs (lê a chave do .env, nunca imprime)."""
import json, os, sys, urllib.request, pathlib
env = {}
for l in pathlib.Path(__file__).resolve().parent.parent.joinpath(".env").read_text().splitlines():
    if "=" in l and not l.startswith("#"):
        k, v = l.split("=", 1); env[k.strip()] = v.strip()
key = env.get("ELEVENLABS_API_KEY")
if not key: sys.exit("falta a chave ELEVENLABS_API_KEY")
def get(url):
    r = urllib.request.Request(url, headers={"xi-api-key": key})
    return json.load(urllib.request.urlopen(r, timeout=30))
try:
    u = get("https://api.elevenlabs.io/v1/user/subscription")
    print("plano:", u.get("tier"), "| caracteres usados:", u.get("character_count"), "/", u.get("character_limit"))
except Exception as e:
    print("assinatura:", e)
v = get("https://api.elevenlabs.io/v1/voices")
for x in v["voices"]:
    l = x.get("labels", {})
    print(x["voice_id"], "|", x["name"], "|", x.get("category"), "|", l.get("gender"), l.get("age"), l.get("accent"), l.get("language", ""), "|", l.get("description", l.get("descriptive", "")))
