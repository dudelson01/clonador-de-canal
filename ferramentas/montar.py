"""Monta um trecho de vídeo a partir de um plano de cenas, da narração e da timeline de palavras.

Uso: python montar.py <plano.json> <narracao.wav> <timeline.json> <saida.mp4> [--ini 0] [--fim 30]
plano.json: [{"id","ini","fim","mov": in|out|left|right, "img": opcional, "textos": [ {"t","x","y","tam","cor"} ]}]
- Imagens em midia/img/<id>.webp (relativo ao plano), redimensionadas para 4K e animadas (zoom/pan lento).
- Legenda: 2–3 palavras por vez, MAIÚSCULA, Anton, branca com contorno; palavra-chave em amarelo.
- Sem música (padrão medido nas referências).
"""
import argparse, json, os, re, subprocess, tempfile
from PIL import Image, ImageDraw, ImageFont

FERR = os.path.dirname(os.path.abspath(__file__))
FONTES = os.path.join(FERR, "fontes")
W, H, FPS = 1920, 1080, 30
PARADAS = set("""a an the and or but of to in on at for with from by as is it its it's you your you've i i'm we our they he she
this that these those be been was were are am do does did not no so if then than up out about just one can will has have had
de la el los las y o en un una que se con por para del al es lo su sus no mas más pero como te tu tus ya
o os as e um uma que se com por para do da dos das no na nos nas ao é seu sua seus suas mas como te você""".split())


def prepara(img, textos, dest):
    im = Image.open(img).convert("RGB")
    r = max(W * 2 / im.width, H * 2 / im.height)
    im = im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)
    x0, y0 = (im.width - W * 2) // 2, (im.height - H * 2) // 2
    im = im.crop((x0, y0, x0 + W * 2, y0 + H * 2))
    d = ImageDraw.Draw(im)
    for t in textos or []:  # coordenadas em fração da tela
        f = ImageFont.truetype(os.path.join(FONTES, t.get("fonte", "Caveat.ttf")), int(t.get("tam", 0.08) * H * 2))
        d.text((t["x"] * W * 2, t["y"] * H * 2), t["t"], font=f, fill=t.get("cor", "#3b2a1a"), anchor="mm")
    im.save(dest, quality=95)


def clipe(png, dur, mov, dest):
    n = max(1, round(dur * FPS))
    z = {"in": f"1+0.10*on/{n}", "out": f"1.10-0.10*on/{n}"}.get(mov, "1.08")
    if mov == "left":
        x = f"(iw-iw/zoom)*(1-on/{n})"
    elif mov == "right":
        x = f"(iw-iw/zoom)*on/{n}"
    else:
        x = "iw/2-(iw/zoom/2)"
    vf = (f"zoompan=z='{z}':x='{x}':y='ih/2-(ih/zoom/2)':d={n}:s={W}x{H}:fps={FPS},"
          f"format=yuv420p")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-i", png, "-vf", vf, "-frames:v", str(n),
                    "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-r", str(FPS), dest], check=True)


def legenda_ass(timeline, ini, fim, dest):
    ws = [w for w in timeline if ini <= w["i"] < fim]
    blocos, atual = [], []
    for w in ws:
        atual.append(w)
        ultima = re.sub(r"[^\w']", "", w["w"]).lower()
        if re.search(r"[.,!?;:]$", w["w"]) or len(atual) >= 4 or (len(atual) >= 3 and ultima not in PARADAS):
            blocos.append(atual); atual = []
    if atual:
        blocos.append(atual)

    def ts(t):
        t = max(0, t - ini); return f"{int(t//3600)}:{int(t%3600//60):02d}:{t%60:05.2f}"

    linhas = []
    for k, b in enumerate(blocos):
        a = b[0]["i"]; z = blocos[k + 1][0]["i"] if k + 1 < len(blocos) else b[-1]["f"] + 0.3
        z = min(z, b[-1]["f"] + 0.6)
        limpa = [re.sub(r"[^\w'’.%-]", "", x["w"]).strip(".").upper() for x in b]
        cand = [i for i, x in enumerate(limpa) if x and (any(c.isdigit() for c in x) or (len(x) >= 4 and x.lower() not in PARADAS))]
        chave = max(cand, key=lambda i: (any(c.isdigit() for c in limpa[i]), len(limpa[i]))) if cand else -1
        txt = " ".join(("{\\c&H00D7FF&}" + x + "{\\c&HFFFFFF&}") if i == chave else x for i, x in enumerate(limpa) if x)
        linhas.append(f"Dialogue: 0,{ts(a)},{ts(z)},Leg,,0,0,0,,{{\\fad(60,0)}}{txt}")
    cab = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Leg,Anton,104,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,0,0,0,0,100,100,1,0,1,6,2,2,80,80,120,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    open(dest, "w", encoding="utf-8").write(cab + "\n".join(linhas) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plano"); ap.add_argument("narracao"); ap.add_argument("timeline"); ap.add_argument("saida")
    ap.add_argument("--ini", type=float, default=0.0); ap.add_argument("--fim", type=float, default=None)
    a = ap.parse_args()
    base = os.path.dirname(os.path.abspath(a.plano))
    cenas = json.load(open(a.plano, encoding="utf-8"))
    fim = a.fim or cenas[-1]["fim"]
    tmp = tempfile.mkdtemp(prefix="montar_")
    lista = os.path.join(tmp, "lista.txt")
    with open(lista, "w") as L:
        for c in cenas:
            if c["fim"] <= a.ini or c["ini"] >= fim:
                continue
            ci, cf = max(c["ini"], a.ini), min(c["fim"], fim)
            png = os.path.join(tmp, c["id"] + ".jpg")
            prepara(os.path.join(base, c.get("img", f"midia/img/{c['id']}.webp")), c.get("textos"), png)
            mp4 = os.path.join(tmp, c["id"] + ".mp4")
            clipe(png, cf - ci, c.get("mov", "in"), mp4)
            L.write(f"file '{mp4}'\n")
            print(f"  cena {c['id']} {ci:.1f}-{cf:.1f}s")
    video = os.path.join(tmp, "video.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lista, "-c", "copy", video], check=True)
    ass = os.path.join(tmp, "leg.ass")
    legenda_ass(json.load(open(a.timeline, encoding="utf-8")), a.ini, fim, ass)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", video, "-ss", str(a.ini), "-t", str(fim - a.ini), "-i", a.narracao,
                    "-vf", f"ass={ass}:fontsdir={FONTES}", "-map", "0:v", "-map", "1:a",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", a.saida], check=True)
    print(f"ok: {a.saida}")


if __name__ == "__main__":
    main()
