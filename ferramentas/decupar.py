#!/usr/bin/env python3
"""Decupagem de gravacao com rosto: monta o corte a partir de uma lista de trechos escolhidos.
Uso: python3 decupar.py plano_decupagem.json saida_dir [--preview]
plano_decupagem.json:
{ "tomadas": {"1": "bruto/gravacao1.mp4", "2": "bruto/gravacao2.mp4"},
  "transcricoes": {"1": "build/gravacao1.json", "2": "build/gravacao2.json"},
  "trechos": [ {"t": "1", "de": "durante quase", "ate": "nao era", "perto": 5, "bloco": "gancho", "obs": "..."}, ... ] }
- "de"/"ate": primeiras/ultimas palavras do trecho (sem acento/pontuacao tanto faz), procuradas perto de "perto" (s).
- Ou "ini"/"fim" em segundos, quando a transcricao falhou.
Cada trecho vira pedacos cortando pausas internas > PAUSA_MAX (deixa PAUSA_RESTO).
Saidas: decupagem.json (pedacos com tempos de origem e de destino), decupado.mp4, cortes.txt."""
import json, os, re, subprocess, sys, unicodedata

PAD_INI, PAD_FIM = 0.08, 0.18      # folga antes da 1a palavra / depois da ultima
PAUSA_MAX, PAUSA_RESTO = 0.55, 0.28  # pausa interna maior que isso e encurtada

def norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9 ]", " ", s).split()

def acha(palavras, frase, perto, depois_de=None, janela=40):
    alvo = norm(frase)
    toks = [norm(w["w"]) for w in palavras]
    flat = [(i, t) for i, ts in enumerate(toks) for t in ts]
    cands = []
    for k in range(len(flat) - len(alvo) + 1):
        if [t for _, t in flat[k:k + len(alvo)]] == alvo:
            i0, i1 = flat[k][0], flat[k + len(alvo) - 1][0]
            if depois_de is not None and i0 < depois_de: continue
            if abs(palavras[i0]["s"] - perto) <= janela: cands.append((abs(palavras[i0]["s"] - perto), i0, i1))
    if not cands: return None
    return sorted(cands)[0][1:]

# --- corte fino pela VOZ (o tempo das palavras do Whisper erra ~0,1-0,3 s) ---
# Separa voz (vibracao das cordas vocais: energia forte em 100-900 Hz) de respiracao/estalo de boca
# (ruido sem vibracao). Mantem consoantes surdas (s, f, ch, t) so encostadas na voz, ate CONSOANTE s.
QUADRO = 0.010          # 10 ms
SIL_MIN = 0.15          # buraco sem voz maior que isso, dentro da fala, e cortado (0,08 comia "e", "a" fracos entre palavras; respiracao dura 0,2 s ou mais)
BRUTO = {}
INCL = {}
INCL_VOZ = 10.0         # dentro da palavra, so conta como voz o que tem grave pelo menos 10 dB acima do agudo
PALAVRA_MAX = 1.20      # dentro de uma palavra (ate 1,2 s do inicio dela) a voz soprada/fraca nao e cortada (antes 0,55: comia o fim de "quiseram", "algoritmo")
PER_MIN = 0.38          # periodicidade minima para contar como voz (respiracao fica abaixo)
CONSOANTE = 0.10        # quanto de som sem vibracao pode ficar grudado antes/depois da voz ("s" final, "f" inicial)
# So gruda som sem vibracao quando a palavra da borda COMECA/TERMINA com consoante surda. Senao esse som e respiracao.
FRIC_INI, PLOS_INI = ("s", "f", "x", "ch", "z", "j", "ce", "ci"), ("t", "p", "c", "k", "q")
FRIC_FIM = ("s", "z", "x")

def borda(trans_t, t0, t1):
    """(quadros de consoante permitidos antes, depois) do bloco de voz t0-t1, pela 1a e ultima palavra."""
    # palavras que estao de fato neste bloco (pelo menos 30% dentro), nao o rabo da anterior nem o inicio da proxima
    ws = [w for w in trans_t if min(w["e"], t1 + 0.05) - max(w["s"], t0 - 0.05) > 0.3 * max(w["e"] - w["s"], 0.05)]
    if not ws: return 0, 0
    w0 = (norm(ws[0]["w"]) or [""])[0]; w1 = (norm(ws[-1]["w"]) or [""])[-1]
    ini = CONSOANTE if w0.startswith(FRIC_INI) else 0.04 if w0.startswith(PLOS_INI) else 0.0
    fim = CONSOANTE if w1.endswith(FRIC_FIM) else 0.05 if w1.endswith(("r", "t")) else 0.0
    return int(round(ini / QUADRO)), int(round(fim / QUADRO))
FOLGA = 0.025           # respiro minimo de cada lado do corte
BUSCA = 0.35            # janela extra para achar o fim real da voz fora do trecho pedido

def envelopes(arq):
    import numpy as np
    def env(filtro):
        raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", arq, "-map", "0:a:0", "-ac", "1", "-ar", "16000",
                              "-af", filtro, "-f", "f32le", "-"], capture_output=True, check=True).stdout
        a = np.frombuffer(raw, np.float32); n = int(16000 * QUADRO)
        a = a[: len(a) // n * n].reshape(-1, n)
        return 20 * np.log10(np.sqrt((a ** 2).mean(1)) + 1e-9)
    tot = env("highpass=f=80")
    low = env("highpass=f=100,lowpass=f=900")
    hf = env("highpass=f=3500")      # chiado de "s", "x", "ch", estouro de "t"
    m = min(len(tot), len(low), len(hf)); tot, low, hf = tot[:m], low[:m], hf[:m]
    # "som" util fora da voz = consoante: agudo forte. Respiracao tem agudo bem mais fraco.
    lim_hf = max(np.percentile(hf, 10) + 12, np.percentile(hf, 90) - 22)
    # so conta como som o que tem chiado de consoante: agudo forte E mais forte que o grave ("s", "x", "t");
    # o sopro depois do "s" (expiracao) tem grave ~ agudo e fica de fora
    tot = np.where((hf > lim_hf) & (hf - low > 3), tot, -200.0)
    lim_tot = np.percentile(tot[tot > -200], 5) if (tot > -200).any() else -60
    lim_low = max(np.percentile(low, 10) + 12, np.percentile(low, 70) - 20)
    # VOZ = grave forte E com tom regular (periodicidade). Respiracao forte faz o grave vibrar, mas nao tem tom.
    import sys as _s; _s.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from vozeamento import periodicidade
    per = periodicidade(arq); per = np.concatenate([per, np.zeros(max(0, m - len(per)))])[:m]
    BRUTO[arq] = low.copy()          # grave sem o filtro de tom (usado dentro das palavras)
    INCL[arq] = low - hf             # inclinacao: voz tem grave >> agudo; respiracao e "plana"; "s" tem agudo > grave
    low = np.where(per >= PER_MIN, low, -200.0)
    return tot, low, lim_tot, lim_low

def blocos(mask, min_len=1):
    out, ini = [], None
    for k, v in enumerate(list(mask) + [False]):
        if v and ini is None: ini = k
        if not v and ini is not None:
            if k - ini >= min_len: out.append([ini, k])
            ini = None
    return out

def apertar(pedacos, tomadas, trans=None):
    import numpy as np
    E = {k: envelopes(v) for k, v in tomadas.items()}
    novos = []
    gmin, cmax = int(round(SIL_MIN / QUADRO)), int(round(CONSOANTE / QUADRO))
    for p in pedacos:
        tot, low, lt, ll = E[p["t"]]
        a, b = int(p["s"] / QUADRO), int(p["e"] / QUADRO)
        i0 = max(0, a - int(BUSCA / QUADRO)); i1 = min(len(tot), b + int(BUSCA / QUADRO))
        # voz = vibracao com tom regular OU som forte com cara de voz (grave >> agudo): pega silaba fraca/rouca
        # do comeco e do fim da frase ("Ate", "Mas", "fui"), que o tom sozinho perdia. Respiracao e plana e fica de fora.
        bruto_t = BRUTO[tomadas[p["t"]]]; incl_t = INCL[tomadas[p["t"]]]
        voz = (low[i0:i1] > ll) | ((bruto_t[i0:i1] > ll) & (incl_t[i0:i1] >= INCL_VOZ))
        if trans:                      # protege as palavras: voz soprada/rouca dentro de palavra fica
            bruto = BRUTO[tomadas[p["t"]]]; incl = INCL[tomadas[p["t"]]]
            for w in trans[p["t"]]:
                if w["e"] < i0 * QUADRO or w["s"] > i1 * QUADRO: continue
                k0 = max(i0, int(w["s"] / QUADRO)); k1 = min(i1, int(min(w["e"], w["s"] + PALAVRA_MAX) / QUADRO) + 1)
                for k in range(k0, k1):
                    if bruto[k] > ll and incl[k] >= INCL_VOZ: voz[k - i0] = True
        som = tot[i0:i1] > lt          # qualquer som (voz, consoante, respiracao)
        vb = [[x + i0, y + i0] for x, y in blocos(voz, 2)]          # >= 20 ms de voz
        vb = [t for t in vb if t[1] > a and t[0] < b]
        if not vb:
            novos.append(p); continue
        ext = int(0.15 / QUADRO)
        if vb[0][0] < a - ext: vb[0][0] = a
        if vb[-1][1] > b + ext: vb[-1][1] = b
        # junta voz separada por buraco curto (oclusivas, silabas)
        junt = [vb[0]]
        for t in vb[1:]:
            if t[0] - junt[-1][1] <= gmin: junt[-1][1] = t[1]
            else: junt.append(t)
        for s_, e_ in junt:
            # gruda consoante surda encostada (som continuo sem vibracao), no maximo CONSOANTE
            # atravessa pausas de ate 60 ms (fechamento de "t", "p", "k") desde que volte a ter som
            def tem(k): return 0 <= k - i0 < len(som) and som[k - i0]
            ci, cf = borda(trans[p["t"]], s_ * QUADRO, e_ * QUADRO) if trans else (cmax, cmax)
            lim_ini = max(a - ext if s_ >= a - ext else s_, s_ - ci)
            s2 = k = s_
            while k - 1 >= lim_ini:
                if tem(k - 1): k -= 1; s2 = k; continue
                j = k - 1
                while j >= lim_ini and not tem(j) and k - j <= 6: j -= 1
                if j >= lim_ini and tem(j) and k - j <= 6: k = j + 1; continue
                break
            lim_fim = min(b + ext, e_ + cf)
            e2 = k = e_
            while k < lim_fim:
                if tem(k): k += 1; e2 = k; continue
                j = k
                while j < lim_fim and not tem(j) and j - k < 6: j += 1
                if j < lim_fim and tem(j) and j - k < 6: k = j; continue
                break
            q = dict(p)
            q["s"] = round(max(0, s2 * QUADRO - FOLGA), 3)
            q["e"] = round(e2 * QUADRO + FOLGA, 3)
            if [s_, e_] != junt[-1]: q.pop("texto", None)
            novos.append(q)
    for x, y in zip(novos, novos[1:]):
        if x["t"] == y["t"] and x["s"] < y["s"] < x["e"]:
            meio = round((x["e"] + y["s"]) / 2, 3); x["e"] = meio; y["s"] = meio
    return novos

# --- modo "palavras" (plano["modo"] == "palavras"): corte montado em volta das PALAVRAS transcritas ---
# O que nao e palavra (dedo na tela, mao no oculos, tosse, nariz, silencio, respiracao) fica de fora.
# O fim de cada palavra vai ate o som acabar de verdade (+ folga natural), para nao soar abrupto.
JUNTA = 0.20        # pausa entre palavras ate isso fica como foi falada
CAUDA = 0.06        # folga natural depois do fim do som
FOLGA_INI = 0.03    # folga antes do inicio do som
MAX_FIM, MAX_INI = 0.40, 0.15   # quanto o som pode passar do tempo que o Whisper deu para a palavra

def por_palavras(plano, trans):
    import numpy as np
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from vozeamento import periodicidade
    S, B, PISO, R, V, FR = {}, {}, {}, {}, {}, {}
    for k, arq in plano["tomadas"].items():
        envelopes(arq)
        b, inc = BRUTO[arq], INCL[arq]
        per = periodicidade(arq); m = min(len(b), len(per)); b, inc, per = b[:m], inc[:m], per[:m]
        hf = b - inc
        piso, piso_hf = np.percentile(b, 10), np.percentile(hf, 10)
        resp = (inc >= -3) & (inc < 7) & (per < 0.45)                 # sopro: plano, sem tom
        fric = (inc < -3) & (hf > piso_hf + 12)                       # chiado de consoante
        som = ((b > piso + 8) & ~resp) | fric
        S[k] = som; B[k] = b; PISO[k] = piso; R[k] = resp; V[k] = per; FR[k] = fric
    out = []
    for n, tr in enumerate(plano["trechos"]):
        t = tr["t"]; som = S[t]; L = len(som)
        ws = [w for w in trans[t] if tr["ini"] - 0.02 <= (w["s"] + w["e"]) / 2 <= tr["fim"] + 0.02]
        if not ws: print(f"aviso: trecho {n} sem palavras"); continue
        blocos = [[ws[0]["s"], ws[0]["e"]]]
        for w in ws[1:]:
            if w["s"] - blocos[-1][1] <= JUNTA: blocos[-1][1] = max(blocos[-1][1], w["e"])
            else: blocos.append([w["s"], w["e"]])
        for b0, b1 in blocos:
            k = min(L - 1, int(round(b1 / QUADRO)))
            if som[k]:
                while k + 1 < L and som[k + 1] and (k + 1) * QUADRO <= b1 + MAX_FIM: k += 1
            else:
                while k > int(b0 / QUADRO) and not som[k]: k -= 1
            # nunca termina antes do fim da palavra; depois acompanha o som caindo (fim fraco da vogal) ate 0,15 s
            # fim arrastado ("horrooor", "rrr" final) parece sopro: segue enquanto ha som (sem queda para silencio),
            # tolerando 20 ms de queda, ate 0,6 s depois da palavra e sem passar do fim do trecho
            kf = max(k + 1, int(round(b1 / QUADRO)))
            lim = min(L, int((b1 + 0.6) / QUADRO), int((tr["fim"] + 0.05) / QUADRO))
            forte = lambda q: q < L and (B[t][q] > PISO[t] + 6 or FR[t][q])     # som grave OU chiado final ("z", "s")
            while kf < lim and (forte(kf) or forte(kf + 1) or forte(kf + 2)): kf += 1
            fim = kf * QUADRO + CAUDA
            j = min(L - 1, int(round(b0 / QUADRO)))
            if j > 0 and som[j - 1]:
                while j - 1 >= 0 and som[j - 1] and (j - 1) * QUADRO >= b0 - MAX_INI: j -= 1
            else:
                while j < k and not som[j]: j += 1
            # comeco pelo SOM (nao pelo tempo do Whisper, que as vezes estica a palavra por cima de uma respiracao);
            # volta ate 0,15 s se houver voz fraca (nao sopro) antes
            j0 = j
            while j - 1 >= 0 and j0 - (j - 1) <= int(0.15 / QUADRO) and B[t][j - 1] > PISO[t] + 4 and not R[t][j - 1]: j -= 1
            # palavra curtinha logo antes ("Ai", "E"), separada por pausa de ate 120 ms: entra junto (ate 0,35 s antes)
            while True:
                q = j - 1; dip = 0
                while q >= 0 and dip <= 12 and not S[t][q] and (not R[t][q] or B[t][q] <= PISO[t] + 10): q -= 1; dip += 1
                if q < 0 or dip > 12 or not S[t][q] or (j0 - q) * QUADRO > 0.35: break
                while q - 1 >= 0 and S[t][q - 1] and (j0 - q) * QUADRO <= 0.35: q -= 1
                j = q
            ini = max(0, j * QUADRO - FOLGA_INI)
            if fim - ini < 0.08: continue
            if out and out[-1]["t"] == t and out[-1]["n"] == n and ini <= out[-1]["e"] + 0.02:
                out[-1]["e"] = round(max(out[-1]["e"], fim), 3); continue
            out.append({"t": t, "s": round(ini, 3), "e": round(fim, 3), "n": n, "bloco": tr.get("bloco", ""), "texto": tr.get("obs", "")})
    # respiracao (>= 0,12 s) DENTRO de um pedaco tambem sai; sobra curta e baixa (< 0,15 s, sem voz forte) e descartada
    limpo = []
    for p in out:
        t = p["t"]; R_, B_ = R[t], B[t]
        k0, k1 = int(p["s"] / QUADRO), min(len(R_), int(p["e"] / QUADRO))
        cortes, k = [], k0
        while k < k1:
            # sopro logo depois de voz forte = fim de palavra sumindo (nao e respiracao)
            colado = any(B_[q] > PISO[t] + 14 and V[t][q] >= 0.5 for q in range(max(k0, k - 4), k))
            if R_[k] and B_[k] > PISO[t] + 4:
                j = k
                while j < k1 and not FR[t][j] and (R_[j] or B_[j] <= PISO[t] + 4): j += 1
                # 0,12 s de sopro; se vem colado na voz (pode ser fim de palavra sumindo), so a partir de 0,18 s
                if sum(R_[k:j]) * QUADRO >= (0.18 if colado else 0.12):
                    cortes.append((k + (int(0.06 / QUADRO) if colado else 0), j))
                k = j
            else: k += 1
        partes, ini = [], p["s"]
        for a, b in cortes:
            partes.append((ini, a * QUADRO + 0.02)); ini = b * QUADRO - 0.02
        partes.append((ini, p["e"]))
        # comeco do pedaco: pula sopro/silencio que sobrou antes da voz (ate 0,3 s)
        a0, b0_ = partes[0]; q = int(a0 / QUADRO); lim0 = q + int(0.3 / QUADRO)
        while q < min(lim0, int(b0_ / QUADRO)) and not FR[t][q] and (R_[q] or B_[q] <= PISO[t] + 6): q += 1
        partes[0] = (max(a0, q * QUADRO - FOLGA_INI), b0_)
        for a, b in partes:
            ka, kb = int(a / QUADRO), max(int(a / QUADRO) + 1, int(b / QUADRO))
            forte = ((B_[ka:kb] > PISO[t] + 18) & (V[t][ka:kb] >= 0.6)).sum() >= 3   # voz de verdade (forte e com tom)
            if b - a < 0.08 or (b - a < 0.60 and not forte): continue
            limpo.append(dict(p, s=round(a, 3), e=round(b, 3)))
    out = limpo
    # pedaco vizinho da mesma tomada nao pode se sobrepor
    for x, y in zip(out, out[1:]):
        if x["t"] == y["t"] and y["s"] < x["e"] and y["s"] > x["s"]:
            meio = round((x["e"] + y["s"]) / 2, 3); x["e"] = meio; y["s"] = meio
    return out

def main():
    plano = json.load(open(sys.argv[1])); out = sys.argv[2]; preview = "--preview" in sys.argv
    os.makedirs(out, exist_ok=True)
    trans = {k: json.load(open(v))["palavras"] for k, v in plano["transcricoes"].items()}
    pedacos, erros = [], []
    for n, tr in enumerate(plano["trechos"]):
        P = trans[tr["t"]]
        if tr.get("exato"):  # tempos exatos, sem ajuste (para cortes dentro de uma palavra mal transcrita)
            pedacos.append({"t": tr["t"], "s": tr["ini"], "e": tr["fim"], "n": n, "bloco": tr.get("bloco", ""), "texto": tr.get("obs", "")}); continue
        if "ini" in tr:
            ws = [w for w in P if w["s"] >= tr["ini"] - 0.05 and w["e"] <= tr["fim"] + 0.05]
            if not ws:
                pedacos.append({"t": tr["t"], "s": tr["ini"], "e": tr["fim"], "n": n, "bloco": tr.get("bloco", "")}); continue
            i0, i1 = P.index(ws[0]), P.index(ws[-1])
        else:
            a = acha(P, tr["de"], tr["perto"])
            if not a: erros.append(f"#{n} nao achei inicio '{tr['de']}' perto de {tr['perto']}s (tomada {tr['t']})"); continue
            b = acha(P, tr["ate"], P[a[0]]["s"] + 5, depois_de=a[0], janela=60)
            if not b: erros.append(f"#{n} nao achei fim '{tr['ate']}' (tomada {tr['t']})"); continue
            i0, i1 = a[0], b[1]
        ws = P[i0:i1 + 1]
        ini = max(0, ws[0]["s"] - PAD_INI) if i0 == 0 or P[i0 - 1]["e"] < ws[0]["s"] - PAD_INI else (P[i0 - 1]["e"] + ws[0]["s"]) / 2
        fim_lim = P[i1 + 1]["s"] if i1 + 1 < len(P) else ws[-1]["e"] + 1
        fim = min(ws[-1]["e"] + PAD_FIM, (ws[-1]["e"] + fim_lim) / 2 if fim_lim - ws[-1]["e"] < 2 * PAD_FIM else ws[-1]["e"] + PAD_FIM)
        # divide nas pausas internas longas
        s = ini
        for a_, b_ in zip(ws, ws[1:]):
            gap = b_["s"] - a_["e"]
            if gap > PAUSA_MAX:
                pedacos.append({"t": tr["t"], "s": round(s, 3), "e": round(a_["e"] + PAUSA_RESTO / 2, 3), "n": n, "bloco": tr.get("bloco", "")})
                s = b_["s"] - PAUSA_RESTO / 2
        pedacos.append({"t": tr["t"], "s": round(s, 3), "e": round(fim, 3), "n": n, "bloco": tr.get("bloco", ""),
                        "texto": " ".join(w["w"] for w in ws)})
    if erros:
        print("\n".join(erros)); sys.exit(1)
    pedacos = por_palavras(plano, trans) if plano.get("modo") == "palavras" else apertar(pedacos, plano["tomadas"], trans)
    # encaixa cada corte na borda de um quadro (1/30 s): imagem e som com a MESMA duracao, sem atraso acumulado
    FPS = 30
    for p in pedacos:
        p["s"] = round(int(p["s"] * FPS + 1e-6) / FPS, 4)
        p["e"] = round(-(-p["e"] * FPS // 1) / FPS, 4)
    pedacos = [p for p in pedacos if p["e"] - p["s"] >= 1 / FPS]
    for x, y in zip(pedacos, pedacos[1:]):   # sem repetir quadro entre pedacos vizinhos da mesma tomada
        if x["t"] == y["t"] and x["s"] < y["s"] < x["e"]: y["s"] = x["e"]
    pedacos = [p for p in pedacos if p["e"] - p["s"] >= 1 / FPS]
    # tempos no video final
    t = 0.0
    for p in pedacos:
        p["dst_s"] = round(t, 3); t += p["e"] - p["s"]; p["dst_e"] = round(t, 3)
    json.dump(pedacos, open(os.path.join(out, "decupagem.json"), "w"), ensure_ascii=False, indent=1)
    with open(os.path.join(out, "cortes.txt"), "w") as f:
        for n, tr in enumerate(plano["trechos"]):
            ps = [p for p in pedacos if p["n"] == n]
            txt = next((p.get("texto") for p in ps if p.get("texto")), "")
            f.write(f"{ps[0]['dst_s']:7.2f}s  [grav. {tr['t']} {ps[0]['s']:.1f}-{ps[-1]['e']:.1f}s] {tr.get('bloco','')}: {txt}\n")
    print(f"{len(plano['trechos'])} trechos -> {len(pedacos)} pedacos, duracao {t:.1f}s")
    # render: cada pedaco re-encodado (corte exato) + concat
    pasta = os.path.join(out, "pedacos"); os.makedirs(pasta, exist_ok=True)
    escala = "scale=1280:-2," if preview else ""
    lista = []
    for i, p in enumerate(pedacos):
        arq = os.path.join(pasta, f"{i:04d}.mp4"); d = p["e"] - p["s"]
        # corta da copia em 30 quadros fixos e so-quadros-chave (render), entao o -ss e exato no quadro
        fonte = plano.get("render", plano["tomadas"])[p["t"]]
        nq = round(d * FPS)
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", f"{p['s']:.4f}", "-i", fonte,
                        "-t", f"{nq / FPS + 0.1:.4f}", "-vf", f"trim=end_frame={nq},setpts=PTS-STARTPTS,{escala}format=yuv420p",
                        "-af", f"asetpts=PTS-STARTPTS,aresample=48000,apad=whole_dur={nq / FPS:.4f},atrim=end={nq / FPS:.4f},afade=t=in:d=0.015,afade=t=out:st={max(0, nq / FPS - 0.025):.4f}:d=0.025",
                        "-c:v", "libx264", "-preset", "ultrafast" if preview else "fast", "-crf", "20",
                        "-c:a", "pcm_s16le", "-ac", "1", "-ar", "48000", arq.replace(".mp4", ".mov")], check=True)
        lista.append(f"file '{os.path.abspath(arq.replace('.mp4', '.mov'))}'")
    open(os.path.join(pasta, "lista.txt"), "w").write("\n".join(lista))
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", os.path.join(pasta, "lista.txt"),
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", os.path.join(out, "decupado.mp4")], check=True)
    print("ok", os.path.join(out, "decupado.mp4"))

main()
