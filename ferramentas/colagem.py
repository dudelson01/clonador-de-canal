"""Edição no estilo "colagem em papel de catálogo" (Toy Aisle Ghosts e canais parecidos).

Uso: python colagem.py <cenas.json> <narracao.wav> <timeline.json> <saida.mp4> [--ini 0] [--fim 30] [--preview]

cenas.json = lista de cenas. Cada cena começa na palavra da narração indicada em "ancora" e vai até a próxima:
  {"id": "s01", "ancora": "On March", "tipo": "cards", "imgs": ["i01"], "legenda": "March 15, 2018",
   "carimbo": "CHAPTER 11", "placa": "CLOSED"}
  {"tipo": "palavra", "texto": "GONE."}                       ← palavra solta em tela preta
  {"tipo": "numero", "valor": 94, "rotulo": "years old", "de": 0, "fmt": "{:,}", "prefixo": "", "sufixo": ""}
  {"tipo": "ano", "valor": 2005}                               ← contador de ano rolando
  {"tipo": "mapa", "pinos": 735, "modo": "surge|some", "rotulo": "735 stores"}
Imagens em midia/img/<id>.webp (relativo ao cenas.json); o mapa usa midia/img/mapa.webp.
Cada cena vira um clipe em build/clipes (cache: só refaz o que mudou). Som: whoosh nos cards, pop nas palavras,
batida no carimbo, tique no contador, trilha sintetizada (ferramentas/trilha.py) com ducking sob a voz, -14 LUFS.
"""
import argparse, hashlib, json, math, os, random, re, shutil, subprocess, sys, tempfile
from concurrent.futures import ProcessPoolExecutor
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

FERR = os.path.dirname(os.path.abspath(__file__))
F = lambda n: os.path.join(FERR, "fontes", n)
W, H, FPS = 1920, 1080, 30
VERSAO = "colagem-4"  # mude para invalidar o cache de clipes quando o visual mudar
TINTA, VERMELHO, PAPEL = (28, 26, 30), (206, 32, 41), (243, 234, 215)
SR = 48000


# ---------- tempos das cenas ----------
norm = lambda s: re.sub(r"[^\w]", "", s.lower().replace("’", "'"))


def resolve_tempos(cenas, tl, dur):
    ws = [norm(w["w"]) for w in tl]
    pos = 0
    for c in cenas:
        alvo = [norm(x) for x in c["ancora"].split() if norm(x)]
        achou = None
        for k in range(pos, len(ws) - len(alvo) + 1):
            if ws[k:k + len(alvo)] == alvo:
                achou = k; break
        if achou is None:
            raise SystemExit(f"âncora não encontrada na timeline (depois da palavra {pos}): {c['id']} '{c['ancora']}'")
        c["ini"] = max(0.0, tl[achou]["i"] - 0.12); pos = achou + 1
    cenas[0]["ini"] = 0.0
    for a, b in zip(cenas, cenas[1:]):
        a["fim"] = b["ini"]
    cenas[-1]["fim"] = dur
    return cenas


# ---------- peças visuais ----------
def papel():
    rng = np.random.default_rng(7)
    base = np.ones((H, W, 3)) * np.array(PAPEL, float)
    ruido = rng.normal(0, 1, (H // 4, W // 4))
    ruido = np.array(Image.fromarray(((ruido * 18) + 128).clip(0, 255).astype(np.uint8)).resize((W, H), Image.BICUBIC), float) - 128
    fibra = rng.normal(0, 4, (H, W))
    yy, xx = np.mgrid[0:H, 0:W]
    vin = 1 - 0.18 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    img = (base + (ruido * 0.35 + fibra)[..., None]) * vin[..., None]
    return Image.fromarray(img.clip(0, 255).astype(np.uint8))


_PAPEL = None


def fundo(preto=False):
    global _PAPEL
    if preto:
        return Image.new("RGB", (W, H), (8, 8, 10))
    if _PAPEL is None:
        _PAPEL = papel()
    return _PAPEL.copy()


def card(path, maxw, maxh, ang):
    im = Image.open(path).convert("RGB")
    r = min(maxw / im.width, maxh / im.height)
    im = im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)
    b = 14
    c = Image.new("RGBA", (im.width + 2 * b, im.height + 2 * b), (252, 250, 245, 255))
    c.paste(im, (b, b))
    pad = 40
    som = Image.new("RGBA", (c.width + 2 * pad, c.height + 2 * pad), (0, 0, 0, 0))
    sh = Image.new("RGBA", c.size, (0, 0, 0, 120))
    som.paste(sh, (pad + 10, pad + 16), sh)
    som = som.filter(ImageFilter.GaussianBlur(14))
    som.alpha_composite(c, (pad, pad))
    return som.rotate(ang, resample=Image.BICUBIC, expand=True)


def texto_img(txt, fonte, tam, cor, contorno=0, cor_contorno=(0, 0, 0), maxw=W - 200):
    f = ImageFont.truetype(F(fonte), tam)
    while f.getlength(txt) > maxw and tam > 30:
        tam -= 4; f = ImageFont.truetype(F(fonte), tam)
    l, t, r, b = f.getbbox(txt, stroke_width=contorno)
    im = Image.new("RGBA", (r - l + 20, b - t + 20), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((10 - l, 10 - t), txt, font=f, fill=cor, stroke_width=contorno, stroke_fill=cor_contorno)
    return im


def carimbo_img(txt):
    t = texto_img(txt, "ArchivoBlack.ttf", 110, VERMELHO + (255,))
    pad = 26
    im = Image.new("RGBA", (t.width + 2 * pad, t.height + 2 * pad), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((4, 4, im.width - 5, im.height - 5), 14, outline=VERMELHO + (255,), width=10)
    im.alpha_composite(t, (pad, pad))
    # textura de tinta falhada
    a = np.array(im); rng = np.random.default_rng(len(txt))
    falha = rng.random(a.shape[:2]) < 0.05
    a[..., 3] = np.where(falha, a[..., 3] * 0.6, a[..., 3]).astype(np.uint8)
    return Image.fromarray(a).rotate(-12, resample=Image.BICUBIC, expand=True)


def placa_img(txt):
    t = texto_img(txt, "ArchivoBlack.ttf", 64, (255, 255, 255, 255))
    pad = 22
    im = Image.new("RGBA", (t.width + 2 * pad, t.height + 2 * pad + 70), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx = im.width // 2
    d.line((cx, 8, cx - 90, 72), fill=(40, 40, 40, 255), width=4); d.line((cx, 8, cx + 90, 72), fill=(40, 40, 40, 255), width=4)
    d.ellipse((cx - 9, 0, cx + 9, 18), fill=(30, 30, 30, 255))
    d.rounded_rectangle((0, 70, im.width - 1, im.height - 1), 16, fill=VERMELHO + (255,), outline=(255, 255, 255, 255), width=5)
    im.alpha_composite(t, (pad, 70 + pad))
    return im


def ease(x):
    x = min(1.0, max(0.0, x)); return 1 - (1 - x) ** 3


def zoom(img, z, cx=W / 2, cy=H / 2):
    # mostra a região (W/z × H/z) centrada em (cx, cy), redimensionada para W×H
    a = 1 / z
    return img.transform((W, H), Image.AFFINE, (a, 0, cx - W / 2 * a, 0, a, cy - H / 2 * a), resample=Image.BILINEAR)


# ---------- cenas ----------
def frames_cards(c, n, base):
    imgs = [os.path.join(base, "midia", "img", i + ".webp") for i in c["imgs"]]
    leg = c.get("legenda")
    topo = 250 if leg else 0
    if len(imgs) == 1:
        caixas = [(W / 2, (H + topo) / 2 + (20 if leg else 0), 1300 if not leg else 1180, 700 if not leg else 650, -1.5)]
    else:
        caixas = [(W * 0.29, (H + topo) / 2 + 20, 840, 560, -2.5), (W * 0.71, (H + topo) / 2 + 30, 840, 560, 2.0)]
    cs = [card(p, mw, mh, ang) for p, (_, _, mw, mh, ang) in zip(imgs, caixas)]
    ltxt = texto_img(leg, "Montserrat-ExtraBoldItalic.ttf", 84, TINTA + (255,)) if leg else None
    carimbo = carimbo_img(c["carimbo"]) if c.get("carimbo") else None
    placa = placa_img(c["placa"]) if c.get("placa") else None
    lado = 1 if sum(map(ord, c["id"])) % 2 else -1
    fim_anim = 0.35 * len(cs) + 0.6
    estat = None
    for k in range(n):
        t = k / FPS
        if estat is None or t <= fim_anim:
            f = fundo().convert("RGBA")
            for j, (cimg, (cx, cy, *_)) in enumerate(zip(cs, caixas)):
                p = ease((t - j * 0.3) / 0.32)
                if p <= 0:
                    continue
                x0 = cx + (1 - p) * lado * (W * 0.75) - cimg.width / 2
                f.alpha_composite(cimg, (int(x0), int(cy - cimg.height / 2)))
            if ltxt is not None:
                p = ease((t - 0.1) / 0.3)
                if p > 0:
                    l2 = ltxt.copy(); l2.putalpha(l2.getchannel("A").point(lambda v: int(v * p)))
                    f.alpha_composite(l2, (int(W / 2 - ltxt.width / 2), int(150 - ltxt.height / 2 + (1 - p) * 20)))
            if placa is not None:
                p = ease((t - 0.45) / 0.35)
                if p > 0:
                    cx, cy, *_ = caixas[0]
                    ang = math.sin(t * 7) * 10 * (1 - p) + 4
                    pr = placa.rotate(ang, resample=Image.BICUBIC, expand=True)
                    f.alpha_composite(pr, (int(cx + 120 - pr.width / 2), int(cy - cs[0].height / 2 - 40 - (1 - p) * 300)))
            if carimbo is not None:
                p = (t - 0.55) / 0.14
                if p > 0:
                    s = 1 + 0.9 * (1 - ease(p))
                    cimg = carimbo.resize((int(carimbo.width * s), int(carimbo.height * s)), Image.BICUBIC)
                    cx, cy = W / 2 + (230 if len(cs) == 1 else 0), (H + topo) / 2 + 80
                    f.alpha_composite(cimg, (int(cx - cimg.width / 2), int(cy - cimg.height / 2)))
            f = f.convert("RGB")
            if t > fim_anim:
                estat = f
        else:
            f = estat
        yield zoom(f, 1.0 + 0.045 * k / max(1, n))


def frames_palavra(c, n, base):
    txt = c["texto"]
    cor = VERMELHO + (255,) if c.get("vermelho") else (245, 245, 245, 255)
    ti = texto_img(txt, "Montserrat-Black.ttf", 170, cor)
    for k in range(n):
        t = k / FPS
        f = fundo(preto=True).convert("RGBA")
        s = 1.18 - 0.18 * ease(t / 0.22)
        im = ti.resize((int(ti.width * s), int(ti.height * s)), Image.BICUBIC)
        dx = math.sin(t * 60) * 6 * max(0, 1 - t / 0.3)
        f.alpha_composite(im, (int(W / 2 - im.width / 2 + dx), int(H / 2 - im.height / 2)))
        yield zoom(f.convert("RGB"), 1.0 + 0.03 * k / max(1, n))


def frames_numero(c, n, base, ano=False):
    v1 = c["valor"]; v0 = c.get("de", v1 - 25 if ano else 0)
    fmt = c.get("fmt", "{}" if ano else "{:,}")
    rot = texto_img(c["rotulo"].upper(), "Montserrat-Black.ttf", 64, (255, 255, 255, 255)) if c.get("rotulo") else None
    dur_conta = min(1.0, n / FPS * 0.5)
    for k in range(n):
        t = k / FPS
        p = ease(t / dur_conta)
        v = round(v0 + (v1 - v0) * p)
        s = c.get("prefixo", "") + fmt.format(v) + c.get("sufixo", "")
        f = fundo().convert("RGBA")
        num = texto_img(s, "ArchivoBlack.ttf", 300, TINTA + (255,))
        bat = 1 + 0.08 * max(0, 1 - (t - dur_conta) / 0.15) if t >= dur_conta else 1
        if bat != 1:
            num = num.resize((int(num.width * bat), int(num.height * bat)), Image.BICUBIC)
        f.alpha_composite(num, (int(W / 2 - num.width / 2), int(H / 2 - num.height / 2 - 60)))
        if rot is not None:
            pr = ease((t - 0.2) / 0.3)
            if pr > 0:
                bw, bh = rot.width + 60, rot.height + 24
                tarja = Image.new("RGBA", (bw, bh), VERMELHO + (255,))
                tarja.alpha_composite(rot, (30, 12))
                tarja = tarja.rotate(-2, resample=Image.BICUBIC, expand=True)
                f.alpha_composite(tarja, (int(W / 2 - tarja.width / 2), int(H / 2 + 150 + (1 - pr) * 40)))
        yield zoom(f.convert("RGB"), 1.0 + 0.04 * k / max(1, n))


_PINOS = {}


def pinos_mapa(path, qtd):
    chave = (path, qtd)
    if chave not in _PINOS:
        m = Image.open(path).convert("L")
        ys0, xs0 = np.nonzero(np.array(m) < 110)
        m = m.crop((xs0.min() - 4, ys0.min() - 4, xs0.max() + 5, ys0.max() + 5))  # só o mapa, sem a margem branca
        r = min(1450 / m.width, 760 / m.height)
        m = m.resize((round(m.width * r), round(m.height * r)), Image.LANCZOS)
        a = np.array(m) < 110
        ys, xs = np.nonzero(a)
        rng = np.random.default_rng(3)
        # mais lojas no leste e na Califórnia, como uma rede de varejo real
        peso = 0.35 + (xs / m.width) ** 1.6 + 0.6 * np.exp(-((xs / m.width - 0.05) ** 2) / 0.004)
        idx = rng.choice(len(xs), size=min(qtd, len(xs)), replace=False, p=peso / peso.sum())
        ordem = rng.permutation(len(idx))
        _PINOS[chave] = (m, list(zip(xs[idx][ordem], ys[idx][ordem])))
    return _PINOS[chave]


def frames_mapa(c, n, base):
    m, pts = pinos_mapa(os.path.join(base, "midia", "img", "mapa.webp"), c.get("pinos", 735))
    mapa = Image.new("RGBA", m.size, (0, 0, 0, 0))
    mapa.putalpha(Image.fromarray(((np.array(m) < 110) * 255).astype(np.uint8)))
    cor = Image.new("RGBA", m.size, (30, 42, 66, 255)); cor.putalpha(mapa.getchannel("A")); mapa = cor
    ox, oy = (W - m.width) // 2, (H - m.height) // 2 + 40
    rot = texto_img(c["rotulo"], "Montserrat-ExtraBoldItalic.ttf", 70, TINTA + (255,)) if c.get("rotulo") else None
    some = c.get("modo") == "some"
    dur_anim = min(1.6, n / FPS * 0.7)
    pino = Image.new("RGBA", (22, 22), (0, 0, 0, 0))
    ImageDraw.Draw(pino).ellipse((4, 4, 17, 17), fill=VERMELHO + (255,), outline=(255, 255, 255, 255), width=2)
    for k in range(n):
        t = k / FPS
        p = ease(t / dur_anim)
        q = round(len(pts) * (1 - p if some else p))
        f = fundo().convert("RGBA")
        f.alpha_composite(mapa, (ox, oy))
        for x, y in pts[:q]:
            f.alpha_composite(pino, (int(ox + x - 11), int(oy + y - 11)))
        if rot is not None:
            f.alpha_composite(rot, (int(W / 2 - rot.width / 2), 70))
        yield zoom(f.convert("RGB"), 1.0 + 0.03 * k / max(1, n))


TIPOS = {"cards": frames_cards, "palavra": frames_palavra, "numero": frames_numero, "mapa": frames_mapa,
         "ano": lambda c, n, b: frames_numero(c, n, b, ano=True)}


def render_cena(args):
    c, base, preview = args
    n = max(1, round((c["fim"] - c["ini"]) * FPS))
    chave = hashlib.sha1(json.dumps([VERSAO, {k: v for k, v in c.items() if k not in ("ini", "fim", "ancora")}, n, preview,
                                     [os.path.getsize(os.path.join(base, "midia", "img", i + ".webp")) for i in c.get("imgs", [])]],
                                    ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:16]
    pasta = os.path.join(base, "build", "clipes"); os.makedirs(pasta, exist_ok=True)
    out = os.path.join(pasta, f"{c['id']}_{chave}.mp4")
    if os.path.exists(out):
        return out
    w, h = (960, 540) if preview else (W, H)
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                          "-i", "-", "-vf", f"scale={w}:{h}", "-c:v", "libx264", "-preset", "veryfast" if preview else "medium",
                          "-crf", "19", "-pix_fmt", "yuv420p", out + ".tmp.mp4"], stdin=subprocess.PIPE)
    for f in TIPOS[c["tipo"]](c, n, base):
        p.stdin.write(f.tobytes())
    p.stdin.close(); p.wait()
    shutil.move(out + ".tmp.mp4", out)
    return out


# ---------- som ----------
def sfx(tipo, rng):
    if tipo == "whoosh":
        d = 0.45; t = np.arange(int(SR * d)) / SR
        ruido = rng.normal(0, 1, len(t))
        # ruído filtrado com corte subindo e descendo (passa-baixa de 1 polo variável)
        fc = 300 + 2600 * np.sin(np.pi * t / d) ** 2
        a = np.exp(-2 * np.pi * fc / SR); y = np.zeros_like(ruido); acc = 0.0
        for i in range(len(ruido)):
            acc = a[i] * acc + (1 - a[i]) * ruido[i]; y[i] = acc
        return y * np.sin(np.pi * t / d) ** 2 * 0.9
    if tipo == "pop":
        d = 0.18; t = np.arange(int(SR * d)) / SR
        return np.sin(2 * np.pi * (180 + 500 * np.exp(-t * 40)) * t) * np.exp(-t * 22) * 0.8
    if tipo == "batida":
        d = 0.5; t = np.arange(int(SR * d)) / SR
        corpo = np.sin(2 * np.pi * (70 + 60 * np.exp(-t * 30)) * t) * np.exp(-t * 9)
        estalo = rng.normal(0, 1, len(t)) * np.exp(-t * 70) * 0.5
        return (corpo + estalo) * 0.9
    if tipo == "tique":
        d = 0.04; t = np.arange(int(SR * d)) / SR
        return np.sin(2 * np.pi * 2200 * t) * np.exp(-t * 160) * 0.35
    if tipo == "plim":
        d = 0.25; t = np.arange(int(SR * d)) / SR
        return (np.sin(2 * np.pi * 1320 * t) + 0.4 * np.sin(2 * np.pi * 2640 * t)) * np.exp(-t * 18) * 0.25
    raise ValueError(tipo)


def trilha_efeitos(cenas, ini, fim):
    rng = np.random.default_rng(11)
    n = int((fim - ini) * SR) + SR
    y = np.zeros(n)
    cache = {}

    def poe(tipo, t, g=1.0):
        if tipo not in cache:
            cache[tipo] = sfx(tipo, rng)
        s = cache[tipo]; k = int((t - ini) * SR)
        if 0 <= k < n:
            m = min(len(s), n - k); y[k:k + m] += s[:m] * g

    for c in cenas:
        if c["fim"] <= ini or c["ini"] >= fim:
            continue
        t0 = c["ini"]
        if c["tipo"] == "cards":
            poe("whoosh", t0, 0.5)
            if len(c["imgs"]) > 1:
                poe("whoosh", t0 + 0.3, 0.35)
            if c.get("carimbo"):
                poe("batida", t0 + 0.6, 0.8)
            if c.get("placa"):
                poe("plim", t0 + 0.75, 0.8)
        elif c["tipo"] == "palavra":
            poe("pop", t0, 0.8); poe("batida", t0, 0.35)
        elif c["tipo"] in ("numero", "ano"):
            dc = min(1.0, (c["fim"] - c["ini"]) * 0.5)
            for k in range(14):
                poe("tique", t0 + dc * ease(k / 14) * 0.98, 0.7)
            poe("batida", t0 + dc, 0.6)
        elif c["tipo"] == "mapa":
            dc = min(1.6, (c["fim"] - c["ini"]) * 0.7)
            for k in range(10):
                poe("plim", t0 + dc * k / 10, 0.35)
    return y


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cenas"); ap.add_argument("narracao"); ap.add_argument("timeline"); ap.add_argument("saida")
    ap.add_argument("--ini", type=float, default=0.0); ap.add_argument("--fim", type=float, default=None)
    ap.add_argument("--preview", action="store_true")
    ap.add_argument("--musica", default=None, help="wav da trilha (ferramentas/trilha.py); sem ela, só voz e efeitos")
    a = ap.parse_args()
    base = os.path.dirname(os.path.abspath(a.cenas))
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", a.narracao]))
    cenas = resolve_tempos(json.load(open(a.cenas, encoding="utf-8")), json.load(open(a.timeline, encoding="utf-8")), dur)
    json.dump(cenas, open(os.path.join(base, "plano.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    fim = min(a.fim or dur, dur)
    sel = [dict(c) for c in cenas if c["fim"] > a.ini and c["ini"] < fim]
    sel[0]["ini"] = max(sel[0]["ini"], a.ini); sel[-1]["fim"] = min(sel[-1]["fim"], fim)
    # cenas cortadas pelo --ini/--fim não podem reaproveitar o cache da cena inteira: o n de quadros muda a chave
    with ProcessPoolExecutor(max(1, (os.cpu_count() or 2))) as ex:
        clipes = list(ex.map(render_cena, [(c, base, a.preview) for c in sel]))
    tmp = tempfile.mkdtemp(prefix="colagem_")
    lista = os.path.join(tmp, "lista.txt")
    open(lista, "w").write("".join(f"file '{p}'\n" for p in clipes))
    video = os.path.join(tmp, "video.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lista, "-c", "copy", video], check=True)
    fx = trilha_efeitos(cenas, a.ini, fim)
    fxw = os.path.join(tmp, "fx.wav")
    import wave
    with wave.open(fxw, "wb") as wv:
        wv.setnchannels(1); wv.setsampwidth(2); wv.setframerate(SR)
        wv.writeframes((np.clip(fx, -1, 1) * 32767 * 0.5).astype(np.int16).tobytes())
    ins = ["-i", video, "-ss", str(a.ini), "-t", str(fim - a.ini), "-i", a.narracao, "-i", fxw]
    filtro = "[1:a]aresample=48000,asplit=2[voz][sc];[2:a]volume=0.55[fx];"
    if a.musica:
        ins += ["-ss", str(a.ini), "-t", str(fim - a.ini), "-i", a.musica]
        filtro += ("[3:a]aresample=48000,volume=0.20[m];[m][sc]sidechaincompress=threshold=0.03:ratio=5:attack=40:release=600[md];"
                   "[voz][fx][md]amix=inputs=3:normalize=0:duration=first[mix];")
    else:
        filtro += "[sc]anullsink;[voz][fx]amix=inputs=2:normalize=0:duration=first[mix];"
    filtro += "[mix]loudnorm=I=-14:TP=-1.5:LRA=11[a]"
    subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", filtro, "-map", "0:v", "-map", "[a]",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest", "-movflags", "+faststart", a.saida], check=True)
    print(f"ok: {a.saida} ({len(sel)} cenas, {fim - a.ini:.1f}s)")


if __name__ == "__main__":
    main()
