"""Gera legenda .srt (para subir no YouTube) a partir da timeline corrigida.
Uso: python srt.py <timeline.json> <saida.srt>
Blocos de até ~42 caracteres por linha, 2 linhas no máximo, quebrando em pontuação quando possível.
"""
import json, re, sys


def ts(t):
    h, r = divmod(t, 3600); m, s = divmod(r, 60)
    return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int(round((s - int(s)) * 1000)):03d}"


def main():
    tl = json.load(open(sys.argv[1], encoding="utf-8"))
    ws = []
    for w in tl:  # junta "1" + ".0" e "-dense", como na legenda queimada
        if ws and re.match(r"^[.,]\d|^-\w|^%", w["w"]):
            ws[-1] = dict(ws[-1], w=ws[-1]["w"] + w["w"], f=w["f"]); continue
        ws.append(dict(w))
    blocos, atual = [], []
    for w in ws:
        atual.append(w)
        txt = " ".join(x["w"] for x in atual)
        if len(txt) >= 70 or (len(txt) >= 35 and re.search(r"[.!?;:]$", w["w"])) or re.search(r"[.!?]$", w["w"]) and len(txt) > 20:
            blocos.append(atual); atual = []
    if atual:
        blocos.append(atual)
    out = []
    for k, b in enumerate(blocos, 1):
        txt = " ".join(x["w"] for x in b)
        if len(txt) > 42:  # quebra em 2 linhas perto do meio
            meio = len(txt) // 2; i = txt.rfind(" ", 0, meio + 8)
            txt = txt[:i] + "\n" + txt[i + 1:] if i > 0 else txt
        fim = b[-1]["f"] + 0.25
        if k < len(blocos):
            fim = min(fim, blocos[k][0]["i"])
        out.append(f"{k}\n{ts(b[0]['i'])} --> {ts(fim)}\n{txt}\n")
    open(sys.argv[2], "w", encoding="utf-8").write("\n".join(out))
    print(f"{sys.argv[2]}: {len(blocos)} legendas")


if __name__ == "__main__":
    main()
