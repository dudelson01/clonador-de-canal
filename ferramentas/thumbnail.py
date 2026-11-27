"""Monta thumbnail 1280x720 no padrão do canal (aprovado no vídeo 1).

Uso: python thumbnail.py <fundo> <circulo> <saida.jpg> --l1 "TEXTO AMARELO" --l2 "TEXTO BRANCO" --l3 "FAIXA VERMELHA" --selo "1 É|RUIM"
Layout: texto em 3 níveis à esquerda (Anton, contorno preto grosso), faixa vermelha, círculo 3D no canto
superior direito com seta vermelha, selo vermelho redondo embaixo à esquerda. Fundo levemente escurecido à esquerda.
"""
import argparse, math, os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

FONTE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fontes", "Anton-Regular.ttf")
W, H = 1280, 720
AMARELO, BRANCO, VERMELHO, PRETO = (255, 230, 0), (255, 255, 255), (224, 27, 27), (0, 0, 0)


def cobre(img, w, h):
    r = max(w / img.width, h / img.height)
    img = img.resize((round(img.width * r), round(img.height * r)), Image.LANCZOS)
    x, y = (img.width - w) // 2, (img.height - h) // 2
    return img.crop((x, y, x + w, y + h))


def fonte_que_cabe(txt, larg_max, alt_max):
    for tam in range(int(alt_max), 20, -2):
        f = ImageFont.truetype(FONTE, tam)
        x0, y0, x1, y1 = f.getbbox(txt)
        if x1 - x0 <= larg_max:
            return f
    return ImageFont.truetype(FONTE, 20)


def texto(d, xy, txt, f, cor, contorno=9):
    d.text(xy, txt, font=f, fill=cor, stroke_width=contorno, stroke_fill=PRETO)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("fundo"); ap.add_argument("circulo"); ap.add_argument("saida")
    ap.add_argument("--l1", required=True); ap.add_argument("--l2", required=True)
    ap.add_argument("--l3", required=True); ap.add_argument("--selo", required=True)
    ap.add_argument("--larg", type=int, default=790, help="largura máxima do bloco de texto")
    a = ap.parse_args()

    base = cobre(Image.open(a.fundo).convert("RGB"), W, H)
    # escurece suavemente a esquerda para o texto saltar
    grad = Image.new("L", (W, H), 0); g = ImageDraw.Draw(grad)
    for x in range(W):
        g.line([(x, 0), (x, H)], fill=int(110 * max(0, 1 - x / (W * 0.62))))
    base = Image.composite(Image.new("RGB", (W, H), (20, 14, 8)), base, grad)
    d = ImageDraw.Draw(base)

    x0, larg = 42, a.larg
    f1 = fonte_que_cabe(a.l1, larg, 175)
    f2 = fonte_que_cabe(a.l2, larg, 110)
    f3 = fonte_que_cabe(a.l3, larg - 60, 165)
    y = 28
    b1 = f1.getbbox(a.l1); texto(d, (x0, y - b1[1]), a.l1, f1, AMARELO); y += b1[3] - b1[1] + 30
    b2 = f2.getbbox(a.l2); texto(d, (x0, y - b2[1]), a.l2, f2, BRANCO, 8); y += b2[3] - b2[1] + 40
    b3 = f3.getbbox(a.l3); alt3 = b3[3] - b3[1]
    faixa = (0, y - 14, x0 + (b3[2] - b3[0]) + 60, y + alt3 + 18)
    d.rectangle(faixa, fill=VERMELHO)
    d.text((x0 + 10, y - b3[1]), a.l3, font=f3, fill=BRANCO, stroke_width=4, stroke_fill=(120, 0, 0))

    # selo redondo
    r = 104; cx, cy = x0 + r + 20, min(H - r - 26, faixa[3] + r + 34)
    d.ellipse((cx - r - 7, cy - r - 7, cx + r + 7, cy + r + 7), fill=BRANCO)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=VERMELHO)
    linhas = a.selo.split("|") if "|" in a.selo else [a.selo]  # use | para quebrar linha no selo
    fs = min((fonte_que_cabe(l, r * 1.5, 78 if len(linhas) > 1 else 90) for l in linhas), key=lambda f: f.size)
    alt_l = fs.getbbox("Hg")[3] - fs.getbbox("Hg")[1]; ytot = len(linhas) * alt_l + (len(linhas) - 1) * 6
    for i, l in enumerate(linhas):
        bb = fs.getbbox(l)
        d.text((cx - (bb[2] - bb[0]) / 2 - bb[0], cy - ytot / 2 + i * (alt_l + 6) - bb[1]), l, font=fs, fill=BRANCO,
               stroke_width=3, stroke_fill=(110, 0, 0))

    # círculo 3D no canto superior direito
    R = 128; ccx, ccy = W - R - 30, R + 26
    circ = cobre(Image.open(a.circulo).convert("RGB"), 2 * R, 2 * R)
    m = Image.new("L", (2 * R, 2 * R), 0); ImageDraw.Draw(m).ellipse((0, 0, 2 * R - 1, 2 * R - 1), fill=255)
    sombra = Image.new("L", (W, H), 0); ImageDraw.Draw(sombra).ellipse((ccx - R - 4, ccy - R + 6, ccx + R + 10, ccy + R + 16), fill=140)
    base = Image.composite(Image.new("RGB", (W, H), PRETO), base, sombra.filter(ImageFilter.GaussianBlur(10)))
    d = ImageDraw.Draw(base)
    d.ellipse((ccx - R - 8, ccy - R - 8, ccx + R + 8, ccy + R + 8), fill=BRANCO)
    base.paste(circ, (ccx - R, ccy - R), m)
    d = ImageDraw.Draw(base)

    # seta vermelha curva do círculo para baixo/esquerda (aponta para o alimento)
    pts = []
    ax, ay = ccx - R * 0.75, ccy + R * 0.55
    bx, by = ccx - R * 1.55, ccy + R * 1.9
    cxp, cyp = ccx - R * 1.75, ccy + R * 0.7
    for k in range(25):
        t = k / 24
        pts.append(((1 - t) ** 2 * ax + 2 * (1 - t) * t * cxp + t ** 2 * bx, (1 - t) ** 2 * ay + 2 * (1 - t) * t * cyp + t ** 2 * by))
    d.line(pts, fill=BRANCO, width=26, joint="curve"); d.line(pts, fill=VERMELHO, width=16, joint="curve")
    ang = math.atan2(pts[-1][1] - pts[-4][1], pts[-1][0] - pts[-4][0])
    ponta = [(bx + 34 * math.cos(ang), by + 34 * math.sin(ang)),
             (bx + 30 * math.cos(ang + 2.3), by + 30 * math.sin(ang + 2.3)),
             (bx + 30 * math.cos(ang - 2.3), by + 30 * math.sin(ang - 2.3))]
    d.polygon(ponta, fill=VERMELHO, outline=BRANCO, width=4)

    base.save(a.saida, quality=93)
    print("ok:", a.saida)


if __name__ == "__main__":
    main()
