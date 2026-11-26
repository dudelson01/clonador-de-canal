# Silver Plate — DNA do canal (3 idiomas)

| Idioma | Nome do canal | Público |
|---|---|---|
| Inglês | **Silver Plate Nutrition** | EUA, 60+ (RPM mais alto) |
| Espanhol | **Plato Plateado** | América Latina, Espanha e hispânicos nos EUA, 60+ |
| Português | **Prato Prateado** | Brasil, 60+ |

Confirmar se o nome está livre na hora de criar cada canal (o de EN não apareceu na busca de 24/11/26).

**Nicho:** nutrição · **Subnicho:** alimentação para força, músculo, sono e rins depois dos 60, sempre a partir de comida comum e barata.
**Promessa do canal:** "Comida simples, explicada com ciência, para viver forte depois dos 60."

## Sobre o canal (About)
- **EN:** Simple, affordable food, explained with real science, for staying strong after 60. Every video cites its sources. We are not doctors and this channel is not medical advice: talk to your doctor before changing your diet, especially if you take medication or have kidney disease.
- **ES:** Comida simple y barata, explicada con ciencia de verdad, para mantenerse fuerte después de los 60. Cada video cita sus fuentes. No somos médicos y este canal no es consejo médico: hable con su médico antes de cambiar su alimentación, sobre todo si toma medicamentos o tiene enfermedad renal.
- **PT:** Comida simples e barata, explicada com ciência de verdade, para continuar forte depois dos 60. Todo vídeo cita as fontes. Não somos médicos e este canal não é orientação médica: fale com seu médico antes de mudar a alimentação, principalmente se toma remédios ou tem doença nos rins.

## Regras de segurança (não negociáveis)
1. **Nada de "médico" falso.** Narrador sem título, sem jaleco de IA, sem "Dr. Fulano". Nunca usar nome de médico real no título.
2. **Nada de cura.** Usar "ajuda", "protege", "estudos mostram"; nunca "cura", "reverte", "mata a doença", "veneno".
3. **Todo número vem de fonte** (estudo, USDA, órgão de saúde), listada na descrição.
4. **Sempre o "lado B":** para quem não é indicado (ex.: doença renal, pressão alta, remédio anticoagulante). Isso dá credibilidade e protege o canal.
5. Aviso falado em 1 frase no início e escrito na descrição.
6. Marcar "conteúdo alterado ou sintético" quando houver pessoa realista gerada por IA.

## Produção: 1 roteiro → 3 vídeos
1. Roteiro mestre em **inglês**, com os fatos checados.
2. Adaptação (não tradução literal) para **ES e PT**: trocar medidas, nomes de alimentos locais (cottage = "requesón/queso cottage" = "queijo cottage") e exemplos de preço e mercado.
3. Narração na **ai33.pro**: 1 voz fixa por idioma, madura, calma e calorosa, ~165 palavras/min em EN e ~150 em ES/PT (medido nas referências).
4. A mesma edição serve para os 3; só mudam narração, textos na tela e thumbnail.
5. **Ritmo:** 5 vídeos/semana em cada idioma por 60 dias (~40 por canal).
6. **Regra de corte:** se até o vídeo 40 nenhum vídeo de um idioma passar de 10 mil views, mudar o formato nesse idioma.

## Roteiro (molde, 12–20 min)
1. **Gancho (0–20 s):** situação do dia a dia + perda ("Depois dos 60, a escada parece mais alta a cada ano…") + a revelação prometida ("um alimento de R$ 8 na geladeira do mercado…").
2. **Aviso (1 frase):** "Isto não substitui seu médico. As fontes estão na descrição."
3. **O problema explicado** (o que acontece no corpo), com 1 número forte.
4. **O alimento:** o que tem, quanto comer, comparação fácil ("a proteína de 4 ovos").
5. **Como comer:** 3 receitas ou combinações baratas.
6. **Erros comuns + para quem NÃO serve.**
7. **Resumo em 3 pontos + pergunta para comentar** ("Você já come isso no café da manhã?").
- Microgancho a cada ~2 min ("Mas o mais importante é a hora em que você come…").

## Edição (medida nos vídeos de referência em 24/11/26; detalhes em `referencia/edicao-medida.md`)
- **Sem música.** Só voz, como nos 3 vídeos de referência.
- **Uma imagem a cada ~6 s** (4 s no gancho e em listas), sempre com zoom lento ou pan; corte seco.
- Estilo visual em 3 camadas:
  1. foto cinematográfica de IA (cozinha, mercado, idosos no dia a dia), luz quente;
  2. **órgão/músculo 3D estilo raio-x azul** para explicar o que acontece no corpo;
  3. **caderno antigo ilustrado** (papel envelhecido, desenho a nanquim) para números e estudos.
- **Legenda:** 2–4 palavras por vez, MAIÚSCULA, branca com contorno preto, palavra-chave em **amarelo**, no terço inferior.
- Número-chave em tela cheia no estilo caderno ("24 g").
- Narração: ~165 palavras/min em EN, ~150 em ES/PT. Voz no volume padrão do YouTube (-14 LUFS).
- **Duração-alvo:** 11–13 min (~1.900 palavras) para liberar anúncios no meio do vídeo.

## Thumbnail (padrão)
- Alimento em **close, saturado**, ocupando 40% da imagem + 1 elemento de contraste (ovos, perna, músculo 3D com seta).
- Texto de **3 a 5 palavras**, fonte grossa, amarelo/branco com faixa vermelha. Pergunta ou comparação, nunca "veneno"/"cura".
- Pessoa 60+ (IA) com expressão de surpresa ou alívio, **sem jaleco nem estetoscópio**.
- Mesma composição nos 3 idiomas; só troca o texto.

## Decisões deste canal
- 24/11/2026: canal criado nos 3 idiomas, com regras de segurança acima (aprovado pelo aluno).
- 24/11/2026: edição definida a partir da medição de 3 vídeos de referência enviados pelo aluno.
- 26/11/2026: vídeo 2 produzido nos 3 idiomas. Erros pegos e corrigidos no processo: falha temporária (503) da ai33 → ferramentas agora tentam de novo; legenda com palavra ouvida errada pela transcrição ("mitratos", "cotade") → **sempre rodar `ferramentas/corrigir_timeline.py` depois da transcrição**, que usa a grafia do roteiro e mantém números em algarismo.
- Fluxo por vídeo: roteiro EN → ES/PT → `narrar.py` → transcrição (timeline) → `corrigir_timeline.py` → `cenas.py` + `imagem_ai33.py` (1K) → `plano_idioma.py` → `montar.py` → conferir painel.
