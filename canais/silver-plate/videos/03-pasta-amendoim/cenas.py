"""Plano de cenas do vídeo 03 (37 blocos). Gera cenas-prompts.json e cenas-blocos.json."""
import json, os, shutil

P = ", cinematic photo, warm natural light, shallow depth of field, realistic, 35mm film look, no text, no logos, no labels"
X = "Medical 3D render in glowing blue X-ray style, translucent anatomy, dark navy background, cinematic lighting, highly detailed, no text, "
N = ("Vintage illustrated notebook page, aged yellowed paper, hand-drawn ink and watercolor sketch, scientific journal aesthetic, "
     "the drawing placed in the lower two thirds of the page, large empty blank paper area at the top, no text, no letters, no numbers, drawing of ")
REUSO = {"v2_d42": "02-pernas-fortes/midia/img/d42", "v2_d43": "02-pernas-fortes/midia/img/d43", "v2_d44": "02-pernas-fortes/midia/img/d44",
         "v1_c12": "01-queijo-cottage/midia/img/c12", "v1_c78": "01-queijo-cottage/midia/img/c78", "v1_c81": "01-queijo-cottage/midia/img/c81",
         "v2_d61": "02-pernas-fortes/midia/img/d61", "v1_c36": "01-queijo-cottage/midia/img/c36"}


def T(en, es, pt, y=0.17, tam=0.085, x=0.5, cor="#3b2a1a"):
    return {"t": {"en": en, "es": es, "pt": pt}, "x": x, "y": y, "tam": tam, "cor": cor}


B = [
 # gancho
 [("e01", 1, "in", "Extreme close-up of a spoon slowly lifting thick creamy peanut butter out of a glass jar, dramatic side light" + P, []),
  ("e02", 1, "right", "Two heaping spoons of peanut butter on a small plate next to a jar on a kitchen table" + P, [])],
 [("e03", 1, "in", "An older man in his seventies spreading peanut butter on whole-grain toast in a sunny kitchen" + P, []),
  ("e04", 1, "left", "A glass jar of peanut butter on a nightstand at night next to a lamp, slightly mysterious mood" + P, [])],
 [("e05", 4, "in", "Top view of an open jar of peanut butter surrounded by roasted peanuts on a dark wooden table, empty space in the center" + P,
   [T("Peanut butter after 60", "Crema de cacahuate después de los 60", "Pasta de amendoim depois dos 60", y=0.5, tam=0.09, cor="#ffffff")]),
  ("v1_c12", 6, "right", None, [T("Sources in the description", "Fuentes en la descripción", "Fontes na descrição", y=0.15, tam=0.08, cor="#ffffff")])],
 # o que tem
 [("e06", 1, "in", N + "a jar of peanut butter with small arrows pointing to it", [T("2 tbsp: 190 kcal · 7 g protein", "2 cdas: 190 kcal · 7 g proteína", "2 colheres: 190 kcal · 7 g proteína", tam=0.075)])],
 [("e07", 1, "in", X + "small food particles breaking down into glowing nutrients inside a human stomach", []),
  ("e08", 1, "right", "Roasted peanuts, a bottle of olive oil and a few almonds on a rustic table" + P, [])],
 # mudança 1
 [("e09", 1, "in", X + "a thigh muscle receiving glowing protein particles", [])],
 [("e10", 1, "in", N + "a slice of toast with peanut butter next to a glass of milk", [T("≈ 20 g protein", "≈ 20 g de proteína", "≈ 20 g de proteína")]),
  ("v2_d43", 1, "right", None, [])],
 [("e11", 1, "in", "An older woman climbing the stairs at home with confidence, warm light" + P, []), ("v1_c36", 1, "left", None, [])],
 # mudança 2
 [("e12", 1, "in", "A breakfast table with peanut butter toast and a cup of coffee in morning light" + P, []),
  ("e13", 1, "right", "A university research kitchen with breakfast trays prepared for a nutrition study, no people faces visible" + P, [])],
 [("e14", 1, "in", N + "two blood sugar curves after a meal, one higher and one lower, with a small peanut drawn next to the lower one",
   [T("smaller rise after lunch", "sube menos después del almuerzo", "sobe menos depois do almoço")])],
 [("e15", 1, "in", N + "fifteen small female figures in a row", [T("15 women · small study", "15 mujeres · estudio pequeño", "15 mulheres · estudo pequeno")]),
  ("e16", 1, "left", "A plate of cookies left untouched on a kitchen counter while a woman walks away satisfied" + P, [])],
 # mudança 3
 [("e17", 1, "in", "An older couple walking in a park at sunset, healthy and relaxed" + P, []),
  ("e18", 1, "right", "Nurses in vintage 1980s uniforms filling out health questionnaires at a desk, nostalgic film photo, no readable text" + P, [])],
 [("e19", 1, "in", N + "a crowd of small female figures and a calendar", [T("83,818 women · 16 years · −21% diabetes", "83.818 mujeres · 16 años · −21% diabetes", "83.818 mulheres · 16 anos · −21% diabetes", tam=0.07)]),
  ("e20", 1, "right", "A bowl of roasted peanuts on a table in a modest home kitchen" + P, [])],
 [("e21", 1, "in", N + "a magnifying glass over a simple chart", [T("a link, not proof", "relación, no prueba", "ligação, não prova")])],
 # colesterol
 [("e22", 1, "in", "A jar of peanut butter next to a stick of butter on a kitchen counter" + P, [])],
 [("e23", 1, "in", N + "a heart with two arrows, one from a stick of butter and one from a jar of peanut butter", [T("swap butter for peanut butter", "cambia mantequilla por crema de cacahuate", "troque manteiga por pasta de amendoim", tam=0.075)]),
  ("e24", 1, "right", "Toast spread with a thin layer of peanut butter on a plate" + P, [])],
 # mudança 4
 [("e25", 1, "in", "A large spoon overflowing with peanut butter next to an open jar" + P, [])],
 [("e26", 1, "in", N + "two spoons on the left and four spoons on the right", [T("2 tbsp 190 kcal  ·  4 tbsp ≈ 380 kcal", "2 cdas 190 kcal  ·  4 cdas ≈ 380 kcal", "2 colheres 190 kcal  ·  4 colheres ≈ 380 kcal", tam=0.07)]),
  ("e27", 1, "right", "A hand dipping a spoon straight into a peanut butter jar late in the evening" + P, [])],
 [("e28", 1, "in", "A jar of peanut butter on a table where a plate of cookies was pushed aside" + P, []),
  ("e29", 1, "left", "Whole-grain bread and peanut butter replacing processed deli meats on a cutting board" + P, [])],
 # escolher o pote
 [("e30", 1, "in", "Two jars of peanut butter side by side on a supermarket shelf, labels blurred and unreadable" + P, [])],
 [("e31", 1, "in", N + "a short list with lines crossed out next to a jar", [T("just peanuts (+ salt)", "solo cacahuate (+ sal)", "só amendoim (+ sal)", tam=0.09)])],
 [("e32", 1, "in", "A jar of natural peanut butter with a layer of oil on top being stirred with a knife" + P, [])],
 # caseira
 [("e33", 1, "in", "Roasted peanuts being poured into a food processor on a kitchen counter" + P, [])],
 [("e34", 1, "right", "Peanut butter turning creamy inside a food processor bowl, close-up" + P, [])],
 [("e35", 1, "in", "A glass jar of homemade peanut butter with a spoon on a wooden table" + P, [])],
 # quanto e como
 [("e36", 1, "in", N + "a measuring tablespoon with peanut butter", [T("1–2 tbsp a day", "1–2 cdas al día", "1–2 colheres por dia", tam=0.1)]),
  ("e37", 1, "right", "An older woman measuring peanut butter with a measuring spoon in her kitchen" + P, [])],
 [("v2_d43", 1, "in", None, []), ("v2_d44", 1, "right", None, []), ("e38", 1, "in", "A banana and peanut butter smoothie in a glass next to a blender" + P, [])],
 [("e39", 1, "in", "A bowl of steamed vegetables and chicken with a creamy peanut sauce" + P, [])],
 # antes de dormir
 [("e40", 1, "in", "A dim bedroom at night with a small plate on the nightstand" + P, [])],
 [("e41", 1, "right", "A small piece of toast with peanut butter and a glass of milk on a nightstand at night, warm lamp" + P, [])],
 # cuidados
 [("v1_c78", 1, "in", None, [])],
 [("e42", 1, "in", "An older person drinking a glass of water while eating toast at the kitchen table" + P, [])],
 [("e43", 1, "in", "A jar of peanuts on a table with a small red warning sign card next to it, no text" + P, [])],
 # resumo
 [("e44", 1, "in", N + "four small drawings in a row: a muscle, a clock, a heart and a scale", [])],
 [("e45", 1, "right", "An older woman enjoying peanut butter toast next to a sunny window" + P, [])],
 [("v1_c81", 1, "in", None, [])],
 [("v2_d61", 1, "in", None, [])],
]

if __name__ == "__main__":
    os.makedirs("midia/img", exist_ok=True)
    for novo, velho in REUSO.items():
        dst = f"midia/img/{novo}.webp"
        if not os.path.exists(dst):
            shutil.copy(f"../{velho}.webp", dst)
    cenas, blocos, vistos = [], [], set()
    for bl in B:
        itens = []
        for cid, peso, mov, prompt, textos in bl:
            if prompt and cid not in vistos:
                cenas.append({"id": cid, "prompt": prompt, "ratio": "16:9"}); vistos.add(cid)
            itens.append({"id": cid, "img": cid, "peso": peso, "mov": mov, "textos": textos})
        blocos.append(itens)
    json.dump(cenas, open("cenas-prompts.json", "w"), ensure_ascii=False, indent=1)
    json.dump(blocos, open("cenas-blocos.json", "w"), ensure_ascii=False, indent=1)
    print(len(blocos), "blocos |", sum(len(b) for b in blocos), "cenas |", len(cenas), "imagens novas")
