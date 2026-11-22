"""Escolhe as cenas de cada trecho da narração a partir do índice de cenas (indice_cenas.py).

segmentos = [(ini, fim, ["filme1", "filme2"] | "ARTE", {"alvo": 2.3, "efeito": "escurece", "rosto": True})]
Retorna a lista de cenas para montar.py, cobrindo exatamente ini..fim.
"""
import json, os, random

ALVO = 2.3  # segundos por corte (DNA aprovado: 1,9 a 2,8)


class Escolhedor:
    def __init__(self, indice_json, pasta_trailers, seed=3):
        self.idx = json.load(open(indice_json))
        self.pasta = pasta_trailers
        self.usado = {}  # (filme, i) -> vezes
        self.rng = random.Random(seed)
        self.giro = {}

    def _melhores(self, filme, rosto):
        cs = [(i, c) for i, c in enumerate(self.idx.get(filme, [])) if not c["cartela"] and c["fim"] - c["ini"] >= 0.8]
        def nota(ic):
            i, c = ic
            n = -3.0 * self.usado.get((filme, i), 0)
            if rosto: n += min(c["rosto"], 0.08) * 40
            n += min(c["brilho"], 120) / 120
            n += self.rng.random() * 0.6
            return n
        return sorted(cs, key=nota, reverse=True)

    def cena(self, filme, dur, rosto=True):
        src = os.path.join(self.pasta, filme + ".mp4")
        if not os.path.exists(src):
            return {"src": "ARTE", "ss": 0, "dur": dur}
        for i, c in self._melhores(filme, rosto):
            vez = self.usado.get((filme, i), 0)
            disp = c["fim"] - c["ini"] - 0.25
            if disp < dur * 0.5: continue
            vel = 1.0 if disp >= dur else round(max(0.5, disp / dur) - 0.01, 3)
            usa = dur * vel
            folga = max(0.0, disp - usa)
            ss = c["ini"] + 0.12 + (folga * (0.5 if vez % 2 else 0.0))
            self.usado[(filme, i)] = vez + 1
            return {"src": src, "ss": round(ss, 3), "dur": round(dur, 3), "vel": vel, "_filme": filme, "_cena": i}
        return {"src": "ARTE", "ss": 0, "dur": dur}

    def segmento(self, ini, fim, filmes, op=None):
        op = op or {}
        total = fim - ini
        if filmes == "ARTE":
            return [{"src": "ARTE", "ss": 0, "dur": round(total, 3)}]
        alvo = op.get("alvo", ALVO)
        n = max(1, round(total / alvo))
        base = total / n
        durs = [base] * n
        out = []
        k = self.giro.get(tuple(filmes), 0)
        for d in durs:
            f = filmes[k % len(filmes)]; k += 1
            c = self.cena(f, d, op.get("rosto", True))
            if op.get("efeito"): c["efeito"] = op["efeito"]
            out.append(c)
        self.giro[tuple(filmes)] = k
        # corrige arredondamento para fechar exatamente no fim
        soma = sum(c["dur"] for c in out)
        out[-1]["dur"] = round(out[-1]["dur"] + (total - soma), 3)
        return out
