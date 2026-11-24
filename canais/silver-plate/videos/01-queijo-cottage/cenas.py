"""Plano de cenas do vídeo 01 (igual nos 3 idiomas). Gera cenas.json com prompts e textos por idioma.
Cada bloco do roteiro (43 no total) recebe uma lista de imagens: (id, peso, movimento, prompt|None, textos).
prompt None = reaproveita imagem já gerada.
"""
import json

P = ", cinematic photo, warm natural light, shallow depth of field, realistic, 35mm film look, no text, no logos, no labels"
X = "Medical 3D render in glowing blue X-ray style, translucent anatomy, dark navy background, cinematic lighting, highly detailed, no text, "
N = ("Vintage illustrated notebook page, aged yellowed paper, hand-drawn ink and watercolor sketch, scientific journal aesthetic, "
     "the drawing placed in the lower two thirds of the page, large empty blank paper area at the top, no text, no letters, no numbers, drawing of ")


def T(en, es, pt, y=0.17, tam=0.09, x=0.5, cor="#3b2a1a"):
    return {"t": {"en": en, "es": es, "pt": pt}, "x": x, "y": y, "tam": tam, "cor": cor}


B = [
 # 00 gancho
 [("c01", 11, "in", None, []), ("c02", 6, "right", None, []), ("c03", 12, "in", None, []), ("c04", 8, "left", None, []), ("c05", 10, "in", None, [])],
 # 01
 [("c06", 14, "right", None, []), ("c07", 8, "in", None, []), ("c08", 9, "left", None, []), ("c09", 12, "in", None, "C09"),
  ("c10", 14, "in", "A breakfast table at sunrise with an old wall clock in the background showing early morning, a cup of coffee and an empty plate" + P, [])],
 # 02 título + aviso
 [("c11", 6, "in", "Top view of an elegant antique silver plate on a dark wooden table surrounded by fresh foods: eggs, berries, oats, a bowl of cottage cheese, the center of the plate empty and shiny" + P,
   [T("Silver Plate Nutrition", "Plato Plateado", "Prato Prateado", y=0.5, tam=0.12, cor="#ffffff")]),
  ("c12", 24, "right", "A pair of reading glasses resting on an open notebook with handwritten notes next to a cup of tea, soft morning light" + P,
   [T("Sources in the description", "Fuentes en la descripción", "Fontes na descrição", y=0.15, tam=0.08, cor="#ffffff")])],
 # 03
 [("c13", 20, "in", X + "the thigh muscle of an elderly person slowly thinning, muscle fibers dissolving into drifting particles", []),
  ("c14", 18, "out", N + "two cross-sections of a human thigh side by side, the right one with visibly less muscle", [T("−3 to 5% per decade", "−3 a 5% por década", "−3 a 5% por década")])],
 # 04
 [("c15", 20, "right", N + "a simple hand-drawn curve on a graph that stays flat then bends down more steeply toward the right, with small human figures from young to old along the bottom",
   [T("faster after 60", "más rápido después de los 60", "mais rápido depois dos 60")]),
  ("c16", 20, "in", X + "front view of the legs of a standing elderly person with the large thigh muscles highlighted in brighter blue", [])],
 # 05
 [("c17", 10, "left", "An older woman gripping a wooden stair railing at home, determined expression" + P, []),
  ("c18", 14, "in", "A grandmother kneeling with open arms as a small grandchild runs toward her in a sunny backyard, joyful" + P, [])],
 # 06
 [("c19", 1, "in", "Top-down view of a simple breakfast of one slice of toast and a cup of black coffee on a kitchen table" + P, [])],
 # 07
 [("c20", 14, "in", X + "muscle fibers being repaired by small glowing building blocks attaching to them", []),
  ("c21", 20, "out", N + "a balance scale with a small human figure on one side and a pile of protein foods (eggs, fish, beans, cheese) on the other",
   [T("1.0–1.2 g protein per kg / day", "1,0–1,2 g de proteína por kg / día", "1,0–1,2 g de proteína por kg / dia", tam=0.08)]),
  ("c22", 12, "in", N + "a bathroom scale next to a small plate of protein foods",
   [T("70 kg → 70–84 g a day", "70 kg → 70–84 g al día", "70 kg → 70–84 g por dia")])],
 # 08
 [("c23", 12, "right", "An elderly man eating a small breakfast of toast and coffee alone at the kitchen table, morning light" + P, []),
  ("c24", 20, "in", N + "three plates in a row: a small breakfast plate with toast, a medium lunch plate, and a large dinner plate with meat and vegetables",
   [T("breakfast: only 10–13 g", "desayuno: solo 10–13 g", "café da manhã: só 10–13 g")])],
 # 09
 [("c25", 18, "in", N + "a single plate with a generous portion of protein foods: eggs, a bowl of cottage cheese, beans",
   [T("25–30 g per meal", "25–30 g por comida", "25–30 g por refeição")]),
  ("c26", 14, "out", X + "an aging muscle with dim, weak glowing signals, only a few fibers lighting up faintly", []),
  ("c27", 16, "right", N + "an old light switch that is off next to a breakfast plate and lunch plate, and switched on next to a dinner plate",
   [T("only one real chance: dinner", "una sola oportunidad: la cena", "uma só chance: o jantar", tam=0.08)])],
 # 10
 [("c28", 1, "in", X + "close-up of aging muscle cells with a mysterious soft glow", [])],
 # 11
 [("c29", 1, "in", "Extreme close-up of a spoon full of creamy cottage cheese lifted toward the camera" + P, [])],
 # 12
 [("c30", 20, "in", X + "a human stomach with white milk protein forming soft clumps inside, glowing particles", []),
  ("c31", 20, "right", X + "tiny glowing particles slowly passing from the intestine into the bloodstream over time", [])],
 # 13
 [("c32", 1, "left", X + "glowing amino acid particles flowing through blood vessels toward a thigh muscle", [])],
 # 14
 [("c33", 14, "in", X + "a thigh muscle receiving faint, flickering signals, most of them fading before arriving", []),
  ("c34", 16, "out", "An elderly hand holding an old mobile phone with a blank dark screen near a window, the phone looks like it has weak signal" + P, [])],
 # 15
 [("c35", 20, "in", N + "a muscle in the center with two arrows pointing to it, one arrow from a plate of food and one from a walking figure",
   [T("more protein per meal  +  movement", "más proteína por comida  +  movimiento", "mais proteína por refeição  +  movimento", tam=0.075)]),
  ("c36", 20, "right", "An older man doing a sit-to-stand exercise from a dining chair in a bright living room, focused and steady" + P, [])],
 # 16
 [("c37", 1, "in", "A white bowl of cottage cheese in close-up on a rustic wooden table with four brown eggs beside it, morning light" + P, [])],
 # 17
 [("c38", 20, "in", N + "a measuring cup filled with cottage cheese",
   [T("1 cup (220 g) = 24 g protein", "1 taza (220 g) = 24 g de proteína", "1 xícara (220 g) = 24 g de proteína", tam=0.08)]),
  ("c39", 12, "right", N + "a single brown egg", [T("1 egg = 6.3 g", "1 huevo = 6,3 g", "1 ovo = 6,3 g")]),
  ("c09b", 12, "in", None, "C09")],
 # 18
 [("c40", 1, "in", N + "one bowl of cottage cheese with a large check mark next to it",
   [T("almost 25–30 g in one bowl", "casi 25–30 g en un tazón", "quase 25–30 g numa tigela", tam=0.08)])],
 # 19
 [("c41", 1, "in", "Slow motion close-up of a spoon lifting creamy cottage cheese out of a bowl, soft side light" + P, [])],
 # 20
 [("c42", 12, "right", "A shopping basket in a supermarket containing a plain tub of cottage cheese, eggs and bread" + P, []),
  ("c43", 12, "in", N + "four foods side by side with small price tags: a steak, a fish, a tub of protein powder and a tub of cottage cheese",
   [T("compare price per gram of protein", "compara el precio por gramo de proteína", "compare o preço por grama de proteína", tam=0.075)])],
 # 21
 [("c44", 14, "in", "A single sunny-side-up egg on a white plate on a kitchen table" + P, []),
  ("c45", 14, "left", "A breakfast plate with two eggs and a bowl of cottage cheese with berries, top-down view" + P, [])],
 # 22 mitos
 [("c46", 1, "in", N + "an open notebook with four numbered empty lines and a quill pen", [T("4 myths", "4 mitos", "4 mitos", tam=0.13)])],
 # 23
 [("c47", 10, "in", N + "an older person sketch with a small plate of food", [T("Myth 1: you need less protein", "Mito 1: necesitas menos proteína", "Mito 1: precisa de menos proteína", tam=0.08)]),
  ("c48", 12, "right", N + "two plates, a small one and a larger one with more protein foods, with an arrow pointing to the larger",
   [T("0.8 → 1.0–1.2 g per kg", "0,8 → 1,0–1,2 g por kg", "0,8 → 1,0–1,2 g por kg")])],
 # 24
 [("c49", 10, "in", N + "a pair of human kidneys with a question mark drawn beside them", [T("Myth 2: protein hurts kidneys", "Mito 2: la proteína daña los riñones", "Mito 2: proteína estraga o rim", tam=0.08)]),
  ("c50", 10, "out", X + "a pair of healthy human kidneys glowing calmly", [])],
 # 25
 [("c51", 8, "in", N + "a steak, an egg, a wedge of cheese, a bowl of beans and a fish side by side", [T("Myth 3: only meat counts", "Mito 3: solo la carne sirve", "Mito 3: só carne serve", tam=0.08)]),
  ("c52", 8, "right", "A bowl of cottage cheese with a spoon ready to eat on a kitchen counter, no cooking needed" + P, [])],
 # 26
 [("c53", 6, "in", N + "a plate of food and a resting armchair", [T("Myth 4: food alone is enough", "Mito 4: la comida basta", "Mito 4: só a comida basta", tam=0.08)]),
  ("c54", 14, "in", X + "a full human body standing up from a chair, the leg muscles lighting up brightly", []),
  ("c55", 10, "left", "A smiling woman in her seventies walking briskly in a park in the morning" + P, [])],
 # 27 receitas
 [("c56", 1, "in", "Top-down view of a kitchen counter with ingredients: a tub of cottage cheese, bananas, berries, oats, bread, tomatoes, eggs and milk" + P, [])],
 # 28
 [("c57", 1, "in", "Top-down view of a bowl of cottage cheese topped with sliced banana, blueberries and oats" + P, []),
  ("c58", 1, "right", "Close-up of a spoon scooping cottage cheese with banana and berries" + P, [])],
 # 29
 [("c59", 1, "in", "Whole-grain toast spread with cottage cheese, sliced tomato, black pepper and a drizzle of olive oil on a wooden board" + P, []),
  ("c60", 1, "left", "Cottage cheese tomato toast with a halved boiled egg on the side on a plate" + P, [])],
 # 30
 [("c61", 1, "in", "Creamy scrambled eggs in a pan with spoonfuls of cottage cheese being stirred in" + P, []),
  ("c62", 1, "right", "A plate of fluffy creamy scrambled eggs on a breakfast table" + P, [])],
 # 31
 [("c63", 1, "in", "A blender with cottage cheese, a banana and milk on a kitchen counter" + P, []),
  ("c64", 1, "left", "Elderly hands holding a tall glass of thick creamy banana smoothie" + P, [])],
 # 32
 [("c65", 1, "in", N + "three plates of similar size each with a portion of protein food", [T("spread protein across the day", "reparte la proteína en el día", "espalhe a proteína pelo dia", tam=0.08)]),
  ("c66", 1, "right", "A happy older man eating a bowl of cottage cheese with fruit at breakfast" + P, [])],
 # 33 noite
 [("c67", 1, "in", "A dim kitchen at night with a small bowl on the table lit by a warm lamp" + P, [])],
 # 34
 [("c68", 12, "in", N + "a bedside table with a glass of milky drink and a clock showing night",
   [T("48 men · age 72 · 40 g before sleep", "48 hombres · 72 años · 40 g antes de dormir", "48 homens · 72 anos · 40 g antes de dormir", tam=0.075)]),
  ("c69", 12, "right", X + "leg muscle fibers glowing softly and rebuilding at night, a moon shape in the background", [])],
 # 35
 [("c70", 12, "in", N + "a small bowl of cottage cheese next to a larger glass of milky drink",
   [T("1 cup ≈ 24 g   ·   study: 40 g", "1 taza ≈ 24 g   ·   estudio: 40 g", "1 xícara ≈ 24 g   ·   estudo: 40 g", tam=0.08)]),
  ("c71", 10, "right", "A glass of milky drink on a bedside table next to a lamp at night" + P, []),
  ("c72", 10, "in", "An elderly man sleeping peacefully in bed at night, soft blue light" + P, []),
  ("c73", 10, "left", "A small bowl of cottage cheese next to a plate of cookies on a table in the evening, warm lamp light" + P, [])],
 # 36 cuidados
 [("c74", 1, "in", "Close-up of a glass salt shaker spilling a little salt on a dark table" + P, [])],
 # 37
 [("c75", 12, "in", N + "a salt shaker next to a bowl of cottage cheese", [T("≈ 700 mg sodium per cup", "≈ 700 mg de sodio por taza", "≈ 700 mg de sódio por xícara", tam=0.08)]),
  ("c76", 12, "right", "An older woman checking her blood pressure with a home monitor at the kitchen table, blank display" + P, []),
  ("c77", 8, "in", "A small half portion of cottage cheese in a little bowl" + P, [])],
 # 38
 [("c78", 12, "in", X + "a pair of human kidneys with a soft red warning glow", []),
  ("c79", 10, "right", "An older man talking with his doctor in a bright clinic office, seen from behind the patient" + P, [])],
 # 39
 [("c80", 1, "in", "A glass of milk next to a bowl of cottage cheese on a kitchen counter" + P, [])],
 # 40 resumo
 [("c13b", 8, "in", None, "C13"), ("c24b", 8, "right", None, "C24"), ("c37b", 8, "in", None, "C37")],
 # 41
 [("c81", 1, "in", "An older couple having breakfast together at a sunny kitchen table, smiling and talking" + P, [])],
 # 42
 [("c82", 1, "in", "An older man climbing a staircase at home with confidence and a smile, warm light" + P, [])],
]

C09 = [T("=", "=", "=", x=0.415, y=0.5, tam=0.16), T("1 cup ≈ 24 g", "1 taza ≈ 24 g", "1 xícara ≈ 24 g", x=0.24, y=0.66, tam=0.075),
       T("4 eggs ≈ 25 g", "4 huevos ≈ 25 g", "4 ovos ≈ 25 g", x=0.66, y=0.66, tam=0.075),
       T("protein", "proteína", "proteína", y=0.2, tam=0.10, cor="#7a4a22")]

if __name__ == "__main__":
    cenas, blocos = [], []
    reuso = {"C09": ("c09", C09)}
    for k, bl in enumerate(B):
        itens = []
        for cid, peso, mov, prompt, textos in bl:
            img = cid
            if isinstance(textos, str):  # reaproveita imagem + textos de outra cena
                if textos == "C09":
                    img, textos = "c09", C09
                else:
                    orig = textos.lower(); img = orig
                    textos = next((x[4] for b2 in B for x in b2 if x[0] == orig), [])
            if prompt:
                cenas.append({"id": cid, "prompt": prompt, "ratio": "16:9"})
            itens.append({"id": cid, "img": img, "peso": peso, "mov": mov, "textos": textos})
        blocos.append(itens)
    json.dump(cenas, open("cenas-prompts.json", "w"), ensure_ascii=False, indent=1)
    json.dump(blocos, open("cenas-blocos.json", "w"), ensure_ascii=False, indent=1)
    print(len(blocos), "blocos |", sum(len(b) for b in blocos), "cenas |", len(cenas), "imagens novas a gerar")
