"""Plano de cenas do vídeo 02 (39 blocos, igual nos 3 idiomas). Gera cenas-prompts.json e cenas-blocos.json.
Item: (id, peso, movimento, prompt ou None para reaproveitar, textos)
Reaproveitadas do vídeo 01 (copiadas para midia/img com o prefixo v1_).
"""
import json, os, shutil

P = ", cinematic photo, warm natural light, shallow depth of field, realistic, 35mm film look, no text, no logos, no labels"
X = "Medical 3D render in glowing blue X-ray style, translucent anatomy, dark navy background, cinematic lighting, highly detailed, no text, "
N = ("Vintage illustrated notebook page, aged yellowed paper, hand-drawn ink and watercolor sketch, scientific journal aesthetic, "
     "the drawing placed in the lower two thirds of the page, large empty blank paper area at the top, no text, no letters, no numbers, drawing of ")
REUSO = {"v1_c12": "c12", "v1_c16": "c16", "v1_c21": "c21", "v1_c25": "c25", "v1_c36": "c36", "v1_c54": "c54", "v1_c78": "c78", "v1_c37": "c37"}


def T(en, es, pt, y=0.17, tam=0.085, x=0.5, cor="#3b2a1a"):
    return {"t": {"en": en, "es": es, "pt": pt}, "x": x, "y": y, "tam": tam, "cor": cor}


B = [
 # gancho
 [("d01", 1, "in", "An older woman in her seventies standing up from a dining chair without using her hands, confident" + P, []),
  ("d02", 1, "right", "Close-up of an older person's feet stepping out of bed onto a wooden floor in the morning" + P, []),
  ("d03", 1, "in", "An older man getting into the driver's seat of a car in a driveway, sunny morning" + P, [])],
 [("d04", 1, "right", "An ordinary supermarket aisle with a simple shopping basket in the foreground" + P, []),
  ("d05", 1, "in", "Expensive-looking unlabeled protein powder tubs and supplement bottles on a store shelf, cold light" + P, []),
  ("d06", 1, "in", "A bunch of fresh spinach leaves half in shadow on a dark wooden table, mysterious dramatic light" + P, [])],
 [("d07", 4, "in", "Flat lay top view on a rustic wooden table of eggs, a can of sardines, a bowl of lentils, Greek yogurt, a glass of milk, a jar of peanut butter and fresh spinach, empty space in the center" + P,
   [T("7 cheap foods for strong legs", "7 alimentos baratos para piernas fuertes", "7 alimentos baratos para pernas fortes", y=0.5, tam=0.09, cor="#ffffff")]),
  ("v1_c12", 6, "right", None, [T("Sources in the description", "Fuentes en la descripción", "Fontes na descrição", y=0.15, tam=0.08, cor="#ffffff")])],
 # por que as pernas
 [("v1_c16", 1, "in", None, []),
  ("d08", 1, "left", "An older woman walking carefully along a garden path keeping her balance" + P, [])],
 [("v1_c21", 1, "out", None, [T("1.0–1.2 g protein per kg / day", "1,0–1,2 g de proteína por kg / día", "1,0–1,2 g de proteína por kg / dia", tam=0.08)]),
  ("v1_c25", 1, "in", None, [T("25–30 g per meal", "25–30 g por comida", "25–30 g por refeição")]),
  ("d09", 1, "right", "A shopping basket on a kitchen table filled with eggs, canned sardines, lentils, yogurt, milk, peanut butter and spinach" + P, [])],
 # teste da cadeira
 [("d10", 1, "in", "A sturdy wooden dining chair placed against a wall with a simple kitchen timer on the floor beside it" + P, [])],
 [("d11", 1, "in", "An older man sitting in the middle of a sturdy chair against a wall, feet flat on the floor, arms crossed over his chest" + P, []),
  ("d12", 1, "right", "An older man halfway through standing up from a chair with arms crossed over his chest, a family member standing beside him for safety" + P, [])],
 [("d13", 3, "in", N + "a simple chair and a small stopwatch",
   [T("men 14 · women 12  (60–64)", "hombres 14 · mujeres 12  (60–64)", "homens 14 · mulheres 12  (60–64)", y=0.13, tam=0.065),
    T("men 12 · women 11  (65–69)", "hombres 12 · mujeres 11  (65–69)", "homens 12 · mulheres 11  (65–69)", y=0.24, tam=0.065),
    T("men 12 · women 10  (70–74)", "hombres 12 · mujeres 10  (70–74)", "homens 12 · mulheres 10  (70–74)", y=0.35, tam=0.065)]),
  ("d14", 2, "right", "An older woman doing a chair stand exercise in her living room while her daughter counts beside her" + P, [])],
 [("d15", 1, "in", "An older woman writing a number on a small notepad stuck to the refrigerator door" + P, [])],
 # 1 ovos
 [("d16", 1, "in", "A carton of brown eggs on a kitchen counter in morning light" + P, [])],
 [("d17", 1, "in", N + "two eggs next to a glass of milk", [T("≈ 20 g protein", "≈ 20 g de proteína", "≈ 20 g de proteína")])],
 [("d18", 1, "right", "A plate of scrambled eggs with fresh spinach on a breakfast table" + P, []),
  ("d19", 1, "in", "A glass bowl of six peeled boiled eggs inside an open refrigerator" + P, [])],
 # 2 sardinha
 [("d20", 1, "in", "An open can of sardines on a wooden board with lemon wedges" + P, []),
  ("d21", 1, "right", "Close-up of sardines on a fork showing the soft edible bones" + P, [])],
 [("d22", 1, "in", X + "glowing omega-3 particles flowing into a thigh muscle", []),
  ("d23", 1, "out", N + "a thigh muscle getting slightly bigger next to a calendar", [T("6 months · thigh muscle +3.6%", "6 meses · músculo del muslo +3,6%", "6 meses · músculo da coxa +3,6%", tam=0.075)])],
 [("d24", 1, "in", N + "a fish oil capsule next to a small sardine", [T("the study used capsules", "el estudio usó cápsulas", "o estudo usou cápsulas")]),
  ("d25", 1, "right", "Sardines on whole-grain toast with red onion and lemon on a plate" + P, []),
  ("d26", 1, "in", "Mashed sardines with lemon and chopped onion in a small bowl" + P, []),
  ("d27", 1, "left", "Two plain unlabeled cans of fish on a kitchen shelf" + P, [])],
 # 3 lentilha e feijão
 [("d28", 1, "in", "A pot of lentil soup steaming on a stove" + P, []),
  ("d29", 1, "right", "Close-up of dry brown lentils and black beans in wooden bowls" + P, [])],
 [("d30", 1, "in", N + "a bowl of lentils next to a bowl of rice", [T("+ rice = more complete protein", "+ arroz = proteína más completa", "+ arroz = proteína mais completa")]),
  ("d31", 1, "right", "A home-style plate of rice and beans with a fork, simple everyday meal" + P, []),
  ("d32", 1, "in", "Canned beans being rinsed under the kitchen tap in a colander" + P, [])],
 # 4 iogurte
 [("d33", 1, "in", "A bowl of thick Greek yogurt with honey and walnuts" + P, []),
  ("d34", 1, "right", "A spoon lifting very thick Greek yogurt from a bowl" + P, [])],
 [("d35", 1, "in", "An older hand holding a plain yogurt tub in a supermarket, label out of focus" + P, []),
  ("d36", 1, "left", "An older woman enjoying a bowl of Greek yogurt with berries in the afternoon at home" + P, [])],
 # 5 leite
 [("d37", 1, "in", "Milk being poured into a glass on a breakfast table" + P, []),
  ("d38", 1, "right", "A bowl of oatmeal with milk and a cup of coffee with milk on a table" + P, [])],
 [("d39", 1, "in", N + "a small sun and a glass of milk with a question mark", [T("vitamin D?", "¿vitamina D?", "vitamina D?", tam=0.11)]),
  ("d40", 1, "right", "An older woman talking with her doctor who is showing a blood test sheet with no readable text" + P, []),
  ("d41", 1, "in", "A glass of milk next to a plain carton on a kitchen counter" + P, [])],
 # 6 pasta de amendoim
 [("d42", 1, "in", "Close-up of a spoon of creamy peanut butter over an open jar" + P, [])],
 [("d43", 1, "right", "Whole-grain toast with peanut butter and banana slices on a plate" + P, []),
  ("d44", 1, "in", "A bowl of oatmeal with a spoon of peanut butter and apple slices on the side" + P, [])],
 # 7 folhas verdes
 [("d45", 1, "in", "A pile of fresh spinach, lettuce, kale and a beetroot on a wooden table" + P, []),
  ("d46", 1, "right", "Close-up of bright green spinach leaves with water droplets" + P, [])],
 [("d47", 1, "in", N + "a pair of legs walking next to a pile of leafy green vegetables", [T("3,759 people · 12 years · +11% leg strength", "3.759 personas · 12 años · +11% de fuerza", "3.759 pessoas · 12 anos · +11% de força", tam=0.07)]),
  ("d48", 1, "left", "An older man walking briskly through a park in the morning" + P, [])],
 [("d49", 1, "in", X + "blood vessels widening with more glowing blood flowing to the leg muscles", []),
  ("d50", 1, "right", "A green smoothie with spinach being poured into a glass" + P, []),
  ("d51", 1, "in", "An older man choosing fresh leafy greens at a farmers market stall" + P, [])],
 # um dia de proteína
 [("d52", 1, "in", N + "a timeline of a day with four small plates of food", [])],
 [("d53", 1, "right", "Breakfast table with two scrambled eggs with spinach and a glass of milk" + P, [])],
 [("d54", 1, "in", "A bowl of lentil soup with a slice of bread" + P, [])],
 [("d55", 1, "left", "A cup of Greek yogurt with fruit as an afternoon snack on a sunny table" + P, [])],
 [("d56", 1, "in", "A dinner plate with sardines on toast and a big green salad" + P, [])],
 [("d57", 1, "in", N + "four small plates of food in a row", [T("≈ 75 g protein in one day", "≈ 75 g de proteína en un día", "≈ 75 g de proteína num dia")])],
 # cuidados
 [("v1_c78", 1, "in", None, [])],
 [("d58", 1, "right", "A weekly pill organizer next to a bowl of fresh spinach on a kitchen table" + P, [])],
 [("d59", 1, "in", "A small bowl of peanuts next to a can of fish on a table" + P, [])],
 # resumo
 [("d60", 1, "in", N + "seven small foods in a row: eggs, a sardine, lentils, a yogurt cup, a glass of milk, a peanut butter jar and spinach", [])],
 [("v1_c54", 1, "in", None, []), ("v1_c36", 1, "right", None, [])],
 [("d61", 1, "in", "An older couple walking together hand in hand in a park" + P, [])],
 [("v1_c37", 1, "in", None, [])],
]

if __name__ == "__main__":
    os.makedirs("midia/img", exist_ok=True)
    for novo, velho in REUSO.items():
        dst = f"midia/img/{novo}.webp"
        if not os.path.exists(dst):
            shutil.copy(f"../01-queijo-cottage/midia/img/{velho}.webp", dst)
    cenas, blocos = [], []
    for bl in B:
        itens = []
        for cid, peso, mov, prompt, textos in bl:
            if prompt:
                cenas.append({"id": cid, "prompt": prompt, "ratio": "16:9"})
            itens.append({"id": cid, "img": cid, "peso": peso, "mov": mov, "textos": textos})
        blocos.append(itens)
    json.dump(cenas, open("cenas-prompts.json", "w"), ensure_ascii=False, indent=1)
    json.dump(blocos, open("cenas-blocos.json", "w"), ensure_ascii=False, indent=1)
    print(len(blocos), "blocos |", sum(len(b) for b in blocos), "cenas |", len(cenas), "imagens novas")
