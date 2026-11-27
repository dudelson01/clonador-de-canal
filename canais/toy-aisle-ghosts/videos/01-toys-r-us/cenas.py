"""Plano de cenas do vídeo 01 (depois do gancho). Gera cenas.json (gancho + resto) e imagens-resto.json.
Âncora = palavras da narração como a transcrição ouviu (ver timeline.json).
C(ancora, imgs, legenda, **extra) = cards · P(ancora, texto) = palavra em tela preta · N(...) = número · A(...) = ano · M(...) = mapa
Imagem nova: ("id", "prompt"); imagem já gerada: "id".
"""
import json

V = ", authentic 1990s 35mm film photograph, slightly faded warm colors, film grain, candid documentary snapshot, realistic, no readable text, no logos"
O = ", vintage 1940s-1950s photograph, black and white or faded sepia, film grain, realistic, no readable text, no logos"
N8 = ", realistic news photograph, natural light, documentary style, no readable text, no logos"
M6 = ", realistic photograph, 2020s, bright and clean, documentary style, no readable text, no logos"
NOVAS = {}


def _imgs(imgs):
    ids = []
    for i in imgs:
        if isinstance(i, tuple):
            NOVAS[i[0]] = i[1]; ids.append(i[0])
        else:
            ids.append(i)
    return ids


def C(anc, imgs, leg=None, **kw):
    d = {"ancora": anc, "tipo": "cards", "imgs": _imgs(imgs if isinstance(imgs, list) else [imgs])}
    if leg:
        d["legenda"] = leg
    d.update(kw); return d


def P(anc, txt, **kw):
    return {"ancora": anc, "tipo": "palavra", "texto": txt, **kw}


def N(anc, valor, rotulo=None, **kw):
    return {"ancora": anc, "tipo": "numero", "valor": valor, **({"rotulo": rotulo} if rotulo else {}), **kw}


def A(anc, ano):
    return {"ancora": anc, "tipo": "ano", "valor": ano}


def M(anc, pinos, modo, rotulo=None):
    return {"ancora": anc, "tipo": "mapa", "pinos": pinos, "modo": modo, **({"rotulo": rotulo} if rotulo else {})}


RESTO = [
 # --- capítulo 1: a loja de berços ---
 C("The story starts", "i04", "Washington, D.C. — 1948"),
 C("A 25 year", ("i14", "A young man in a 1940s US Army uniform seen from behind, standing on a city sidewalk in Washington DC after the war, face not visible" + O), "a 25-year-old war veteran"),
 C("opened a small", ("i15", "A small 1940s bicycle repair shop on a city street, bicycles outside, with a tiny shop entrance on the lower level" + O), "below his father's bike shop"),
 P("It wasn't a toy", "NOT A TOY STORE."),
 C("It sold baby", [("i16", "A 1940s wooden baby crib in a modest showroom" + O), ("i17", "A 1940s baby pram stroller on a sidewalk" + O)], "baby furniture"),
 C("He called it", ("i18", "A small 1940s family store facade with an awning and baby furniture in the window, black and white photograph, no readable signs"), "Children's Bargain Town"),
 C("It was perfect", ("i19", "1945 soldiers returning home hugging their families at a crowded train station" + O), "perfect timing"),
 C("Soldiers were coming", ("i20", "A 1950s city park full of young mothers pushing baby prams, baby boom era" + O), "the baby boom"),
 P("But Lazarus noticed", "BUT..."),
 C("A family buys", "i16", "a crib: bought once"),
 P("Then they never", "THEY NEVER COME BACK."),
 C("Toys were different", ("i21", "A 1950s child playing with tin toys and wooden blocks on a living room floor" + O), "toys were different"),
 C("Toys broke", ("i22", "A broken vintage tin toy robot and a worn doll lying on an old wooden floor" + O), "they break. kids outgrow them."),
 C("And every birthday", [("i23", "A 1950s kids birthday party around a cake with candles" + O), ("i24", "A 1950s Christmas morning, kids opening presents under a decorated tree" + O)], "every birthday, every Christmas"),
 P("So he did", "THE IDEA."),
 C("He looked at", ("i25", "A brand new 1950s American supermarket with wide aisles, shoppers and bright shelves" + O), "the new supermarkets"),
 C("with their giant", ("i26", "A long row of 1950s metal shopping carts lined up at a supermarket entrance" + O), "giant aisles. shopping carts."),
 P("Why not a", "A SUPERMARKET... FOR TOYS?"),
 A("In 1957 he", 1957),
 C("he opened his first", ("i27", "Grand opening of a big 1950s toy store, crowd of families with children lined up outside, vintage color photograph, faded, no readable signs"), "the first toys-only store"),
 C("He gave it", ("i28", "Close-up of a child's hand writing big crayon letters on paper, one letter R written backwards, playful, warm light, no other text"), "a name a kid could have written"),
 P("Toys R Us The", 'TOYS"R"US'),
 # --- capítulo 2: a era de ouro ---
 C("formula was simple", ("i29", "A huge 1980s toy superstore interior, long aisles with shelves to the ceiling, shoppers with carts" + V), "the formula"),
 C("Huge stores", ("i30", "A 1980s big-box toy store exterior with a full parking lot on a sunny day, plain facade" + V), "huge stores"),
 C("Every toy you", ("i31", "Towering shelves packed with colorful toy boxes stacked all the way to a warehouse ceiling" + V), "stacked to the ceiling"),
 C("low prices", ("i32", "Close-up of bright orange price stickers on toy boxes in a store, 1980s" + V), "low prices"),
 C("and a giraffe", ("i33", "A friendly cartoon-style plush giraffe toy sitting on a toy store shelf, generic design" + V), "...and a giraffe"),
 C("the giraffe had started", "i18", "Geoffrey the Giraffe"),
 C("Now he became", ("i35", "A giant smiling giraffe mascot statue at the entrance of a 1980s toy store, kids posing next to it" + V), "the face of an empire"),
 M("Through the 70s", 420, "surge", "1970s → 1980s"),
 P("It became what", "CATEGORY KILLER.", vermelho=True),
 C("Small toy shops", ("i36", "A small family-owned toy shop on a main street with empty windows and closed shutters, 1980s" + V), "small shops couldn't compete", placa="CLOSED"),
 N("For roughly 15", 15, "years at #1"),
 C("And it had", ("i37", "A 1980s family watching a commercial on a glowing CRT television in a cozy living room" + V), "the jingle"),
 P("I don't want", "I DON'T WANNA GROW UP..."),
 C("If you were", ("i38", "A 1990s kid pressing his face against a glass display case full of video games in a toy store" + V), "the video game aisle"),
 C("where you grabbed", ("i39", "Close-up of a child's hand holding a small paper ticket in front of a wall of video game boxes, 1990s" + V), "grab the paper ticket"),
 C("The bikes hanging", ("i40", "Rows of colorful kids bicycles hanging from a toy store ceiling" + V), "bikes on the ceiling"),
 C("The wish list", ("i41", "A kid lying on the carpet circling toys with a marker in a thick holiday toy catalog, 1990s" + V), "the wish list"),
 C("It wasn't just", "i06", "not just a store"),
 C("It was the place", ("i42", "A family Christmas shopping in a busy 1990s toy store, excited kids, festive decorations" + V), "where Christmas started"),
 A("In 2001 the", 2001),
 C("opened its crown", ("i43", "Times Square at night with a giant glowing multi-story toy store facade and crowds on the sidewalk, no readable signs" + N8), "the Times Square flagship"),
 C("with a 60", ("i44", "A colorful ferris wheel inside a multi-story toy store atrium, kids riding it" + N8), "a 60-foot Ferris wheel inside"),
 C("and a giant animatronic", ("i45", "A giant animatronic T-rex dinosaur inside a toy store, kids looking up amazed" + N8), "an animatronic T-Rex"),
 P("But by then", "BUT..."),
 C("And the first crack", ("i46", "A cracked glass storefront window of a toy store, crack lines spreading across the glass" + N8), "the first crack"),
 # --- capítulo 3: Walmart ---
 C("In the 90s Walmart", "i11", "Walmart & Target"),
 C("They didn't need", ("i47", "Toys on a discount store shelf with big red sale price tags, 1990s" + V), "toys at cost... or at a loss"),
 C("just to get", ("i48", "Parents with kids walking into a big discount superstore entrance through automatic doors, 1990s" + V), "just to get parents inside"),
 C("Once you were", ("i49", "A shopping cart overflowing with groceries, clothes and a toy box on top" + V), "groceries. clothes. everything."),
 P("Toys R Us couldn't", "TOYS WERE ALL IT SOLD."),
 A("In 1998 for", 1998),
 N("Walmart sold 17", 174, "Walmart", div=10, sufixo="%"),
 N("Toys R Us sold 16", 168, 'Toys"R"Us', div=10, sufixo="%"),
 C("It was still", ("i50", "A giant toy store with very few customers, a lonely employee standing in an empty aisle" + V), "a giant with a problem"),
 P("And its solution", "IT GOT WORSE."),
 # --- capítulo 4: Amazon ---
 A("In 1999 the", 1999),
 C("the internet was exploding", ("i51", "A beige late-1990s computer with a CRT monitor showing a web page loading, dial-up modem on the desk" + V), "the internet boom"),
 C("That Christmas its", ("i52", "A frustrated parent at a home computer late at night in 1999, error window on the screen, blurred" + V), "the website couldn't keep up"),
 A("So in 2000", 2000),
 C("It signed a 10", ("i53", "Two businessmen in suits shaking hands over a signed contract in a 2000s office" + N8), carimbo="10 YEARS"),
 C("would become the", "i10", "the only toy seller on Amazon"),
 C("In plain English", ("i54", "Close-up of one hand passing a ring of keys to another hand, dramatic light" + N8), "handing over the keys"),
 P("that would one", "TO AMAZON.", vermelho=True),
 C("For a few", ("i55", "A warehouse full of toy boxes being packed into shipping boxes by workers, early 2000s" + N8), "for a few years, it worked"),
 C("Then Amazon started", ("i56", "A laptop screen showing an online marketplace grid full of toy listings, blurred unreadable text" + N8), "other sellers, same toys"),
 C("felt betrayed", ("i57", "A courtroom with a wooden judge's gavel and stacks of legal documents" + N8), carimbo="LAWSUIT"),
 A("In 2006 a judge", 2006),
 P("It won in court", "IT WON IN COURT..."),
 C("Almost a decade", ("i58", "Calendar pages flying away in the wind, retro concept photo of time passing" + N8), "a lost decade online"),
 N("Years later Amazon", 51, "settlement", prefixo="$", sufixo="M"),
 C("By then Amazon", ("i59", "A huge modern fulfillment center with conveyor belts and robots moving packages" + M6), "Amazon was the future"),
 C("was still figuring", "i52", "still fixing its website"),
 C("If you grew up", ("i60", "A plush giraffe toy standing in a dark toy store aisle under a soft spotlight" + V), "subscribe for more"),
 C("the toys the stores", "i31", "toys. stores. brands."),
 # --- capítulo 5: o acordo ---
 P("Now we get", "THE REAL ANSWER."),
 C("In March of 2005", "i12", "March 2005"),
 C("three investment firms", ("i61", "Three silhouettes of investors at a long dark boardroom table, dramatic side lighting" + N8), "Bain Capital · KKR · Vornado"),
 N("agreed to buy", 66, "buyout", div=10, prefixo="$", sufixo="B"),
 P("But here's the", "THE CATCH."),
 C("Most of that", ("i62", "Stacks of banknotes on bank loan documents with a pen, cold office light" + N8), "most of it was borrowed"),
 P("It's called a", "LEVERAGED BUYOUT.", vermelho=True),
 C("And in a", "i61", "the debt doesn't stay with the buyers..."),
 C("It gets loaded", ("i63", "A heavy iron chain and weight attached to a red shopping cart, dramatic studio light" + N8), "...it goes on the company"),
 C("Overnight", ("i64", "A big-box toy store exterior at dusk under ominous dark storm clouds" + N8), "overnight"),
 N("carrying around", 5, "of debt", prefixo="$", sufixo="B"),
 N("Just the interest", 400, "interest every year", prefixo="$", sufixo="M"),
 C("Every single year", ("i65", "Banknotes burning in a metal bin in the dark" + N8), "every single year"),
 C("before fixing a", ("i66", "A broken shelf and a flickering fluorescent light in a tired old toy store" + N8), "before fixing a single store"),
 C("that's money that", ("i67", "Store blueprints and a website wireframe sketch on a desk with a coffee cup" + N8), "better stores. better website."),
 C("Instead it went", "i62", carimbo="TO THE LENDERS"),
 C("The stores started", ("i68", "Messy toy store shelves with toys fallen on the floor under dim light" + N8), "tired stores"),
 C("The website stayed", "i52", "a clunky website"),
 C("And customers noticed", "i50", "customers noticed"),
 C("In December of", ("i69", "A dark empty multi-story toy store facade in Times Square with lights off and windows papered over" + N8), "Dec 30, 2015", placa="CLOSED"),
 N("The rent there", 42, "rent per year", prefixo="$", sufixo="M"),
 C("The company simply", "i44", "goodbye, crown jewel"),
 P("Then came the", "THEN..."),
 # --- capítulo 6: a queda ---
 C("In September of", ("i70", "A newspaper on a kitchen table next to a coffee cup, big bankruptcy headline blurred and unreadable" + N8), "September 2017", carimbo="CHAPTER 11"),
 C("The plan was", ("i71", "Worried executives in a meeting room looking at falling charts on a screen" + N8), "the plan: survive Christmas"),
 C("But Christmas went", ("i72", "A toy store at Christmas almost empty of shoppers, big sale signs without readable text" + N8), "Christmas went badly"),
 C("Suppliers got nervous", ("i73", "An idle loading dock with parked delivery trucks and stacked boxes" + N8), "suppliers got nervous"),
 C("And on March", "i01", "March 15, 2018"),
 M("Every store in", 735, "some", "every store"),
 C("Exactly one week", "i03", "March 22, 2018"),
 C("The man who had", ["i18", "i29"], "from a crib shop to an empire"),
 C("The liquidation sales", "i02", "liquidation", placa="SALE"),
 C("Shelves emptied", ("i74", "Completely empty toy store shelves with only price tags left" + N8), "shelves emptied"),
 C("Signs came down", ("i75", "Workers on a lift removing a large store sign from a building facade, letters unreadable" + N8), "signs came down"),
 C("By the end", "i13", "June 2018", placa="CLOSED"),
 N("Around 30", 30000, "jobs lost"),
 C("And because of", "i05", carimbo="NO SEVERANCE"),
 N("Later that year", 20, "hardship fund", prefixo="$", sufixo="M"),
 C("For many workers", ("i76", "A former retail employee walking alone across an empty parking lot carrying a cardboard box" + N8), "far less than they lost"),
 # --- capítulo 7: o que matou ---
 P("So was it", "WAS IT AMAZON?"),
 C("Was it Walmart", "i11", "Walmart?"),
 C("The honest answer", ["i10", "i11"], "all of them — but not equally"),
 C("Walmart took its", "i48", "Walmart took the customers"),
 C("The Amazon deal", "i59", "Amazon took the internet"),
 C("But plenty of", ("i77", "Busy big-box electronics and department stores with shoppers, still thriving" + M6), "others survived"),
 C("couldn't survive was", "i63", "$400M a year out the door"),
 C("walking out the", "i65"),
 P("The debt didn't", "THE DEBT.", vermelho=True),
 C("It took away", "i09", "no chance to fight back"),
 # --- capítulo 8: o fantasma volta ---
 C("And that's where", "i13", "the end?"),
 P("But it didn't", "BUT IT DIDN'T."),
 C("The brand was", ("i78", "A contract with signatures being slid across a desk between two people, close-up" + M6), "sold, and sold again"),
 C("Its new owner", ("i79", "A colorful toy shop section inside a big department store" + M6), "shops inside Macy's"),
 C("Then a flagship", ("i80", "A large modern two-story toy store inside a giant mall, bright and colorful" + M6), "a new flagship"),
 C("Then shops and", ("i81", "A small toy shop in an airport terminal, travelers with suitcases walking by" + M6), "airports"),
 N("And this year", 120, "new stores in 2026"),
 M("stores bringing its", 160, "surge", "~160 stores"),
 C("A lot of", ("i82", "Adult collectors browsing collectible action figures in a modern toy store" + M6), "the new shoppers: adults"),
 C("The same kids", [("i83", "A parent and a young child shopping together in a modern toy store, both smiling" + M6), "i06"], "the kids who sang the jingle"),
 C("It's not the", "i08", "not the same company"),
 C("What's coming back", "i33", "the name. the giraffe. the memory."),
 C("But maybe that's", "i39", "what it really sold"),
 P("Not toys", "NOT TOYS."),
 C("The feeling of", ("i84", "A child seen from behind walking through automatic doors into a glowing toy store, magical warm light" + V), "the feeling"),
 C("So tell me", "i41", "your first toy? tell me below"),
 C("And if you", ("i85", "A pile of small generic plush bean-bag animals with heart-shaped tags, on a wooden table" + V), "next: Beanie Babies"),
]

gancho = [c for c in json.load(open("cenas.json", encoding="utf-8")) if len(c["id"]) == 3 and c["id"] < "s21"]
cenas = gancho + [dict(c, id=f"s{21 + k:03d}") for k, c in enumerate(RESTO)]
json.dump(cenas, open("cenas.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump([{"id": k, "prompt": v, "ratio": "16:9"} for k, v in NOVAS.items()], open("imagens-resto.json", "w", encoding="utf-8"), indent=1)
print(f"{len(cenas)} cenas, {len(NOVAS)} imagens novas (~{len(NOVAS) * 550} créditos)")
