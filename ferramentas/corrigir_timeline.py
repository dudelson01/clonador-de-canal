"""Corrige a grafia da timeline (transcrição automática) usando o texto do roteiro, mantendo os tempos.

Uso: python corrigir_timeline.py <roteiro.md> <timeline.json>   (sobrescreve a timeline; guarda .orig.json)
- Alinha palavra a palavra (difflib). Onde a transcrição ouviu errado ("mitratos"), troca pela palavra do roteiro.
- Mantém números em algarismo da transcrição ("18" fica melhor na legenda que "dezoito").
"""
import difflib, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from narrar import capitulos  # noqa: E402

norm = lambda s: re.sub(r"[^\w]", "", s.lower())


def main():
    rot, tl_path = sys.argv[1], sys.argv[2]
    ref = " ".join(c["texto"] for c in capitulos(open(rot, encoding="utf-8").read())).split()
    tl = json.load(open(tl_path, encoding="utf-8"))
    orig = tl_path.replace(".json", ".orig.json")
    if not os.path.exists(orig):
        json.dump(tl, open(orig, "w", encoding="utf-8"), ensure_ascii=False)
    else:
        tl = json.load(open(orig, encoding="utf-8"))
    a = [norm(w) for w in ref]; b = [norm(w["w"]) for w in tl]
    trocas = 0
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if op != "replace" or (i2 - i1) != (j2 - j1):
            continue  # só troca 1-para-1 (palavra ouvida errada); blocos de tamanhos diferentes ficam como estão
        for k in range(j2 - j1):
            w = tl[j1 + k]
            if any(ch.isdigit() for ch in w["w"]) or not any(ch.isalpha() for ch in w["w"]):  # números e símbolos (%) ficam
                continue
            pont = re.findall(r"[.,!?;:]+$", w["w"])
            nova = re.sub(r"[.,!?;:]+$", "", ref[i1 + k]) + (pont[0] if pont else "")
            if norm(nova) != norm(w["w"]):
                print(f"  {w['w']!r} -> {nova!r}"); w["w"] = nova; trocas += 1
    json.dump(tl, open(tl_path, "w", encoding="utf-8"), ensure_ascii=False)
    print(f"{tl_path}: {trocas} palavras corrigidas")


if __name__ == "__main__":
    main()
