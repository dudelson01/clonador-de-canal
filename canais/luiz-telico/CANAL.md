# Luiz Telico (referências: SB Cinema, Barry Cinema, Nerd Desempregado, colletiquette, Potatopixel)

## Nicho e público
Cultura pop. Subnicho: **o que o filme ou a série REALMENTE quer dizer** (análise que muda como o público vê uma obra famosa). Público brasileiro que maratona séries e filmes populares.

## Idioma e formato
Português (BR). Vídeo longo: 6 a 12 min depois da decupagem (o 1º saiu com 6:02; referências entre 10 e 15 min). Frequência a definir.
Formato **híbrido com rosto**: Luiz aparece na câmera no gancho, nas opiniões e nos pedidos de inscrição; o resto é narração por cima de cenas, imagens e artes.

## Molde de roteiro (com tempos)
Usado no vídeo 01 (Stranger Things), baseado nas referências com rosto (SB Cinema, Brett's Thoughts, Leo Irvine):
- [GANCHO 0-30 s] Frase que contradiz o público ("você achou que era X. Não era.") + promessa de revelar uma cena/detalhe no fim (loop aberto). Rosto no começo, cenas rápidas por cima dos nomes citados.
- [BLOCOS] 4 a 5 blocos, cada um com uma cena/temporada concreta e o significado dela. Cada bloco termina numa frase-resumo de impacto ("o que morre ali é a infância").
- [PONTE] "até aqui parece só X, mas…" entre blocos.
- [COMENTÁRIO DO LUIZ] 1 opinião pessoal curta por bloco (humor/emoção). Manter curto.
- [CTA] no meio (~3:15), ligado ao tema ("se você também cresceu junto com esses personagens…").
- [FINAL] paga o loop aberto do gancho, repete a tese ("então não, X nunca foi sobre Y") e termina com pergunta pessoal para os comentários + CTA curto.
Referências analisadas: referencia/medicoes/resumo-edicao.md.

## Voz
A voz do próprio Luiz, gravada em vídeo. Etapa E = decupar o VÍDEO gravado (cortar erros e pausas), não só o áudio.

## Edição em números
| Item | Referência (medida) | Nosso alvo (aprovado no vídeo 01) |
|---|---|---|
| Segundos por plano (1º min / resto) | 2,4–3,5 s / 4–5 s (SB Cinema, Brett) | 1–2,5 s nas cenas; rosto até ~4,5 s e aí troca o enquadramento |
| Rosto na tela | 33–75% (SB Backrooms 55%, Brett 75%) | ~55–65% |
| Cena de filme/série | tela cheia, 2–4 s, zoom lento | tela cheia, zoom lento 1,10→1,20, faixas pretas e logo da fonte disfarçados |
| Legenda | nenhuma referência usa legenda completa | só frase-chave embaixo (Inter, branco, palavra forte em vermelho) |
| Destaques | seta/nome à mão, carimbo SPOILER, citação, gráfico | nome escrito à mão + seta (Caveat), carimbo (Anton), máquina de escrever (Special Elite), contador, palavra vermelha tremendo, carta, botão inscrever |
| Rosto | cenário escuro, luz lateral | tratamento de cor mais escuro/contraste + vinheta; zoom forte (1,22) nos comentários e frases de impacto |
| Música / efeitos | trilha baixa, troca por parte | trilha original de synth anos 80, 1 clima por parte (suspense, triste, tenso, final), ducking na voz; whoosh baixo nos cortes, impacto, carimbo, teclas, rebobinar |
| Volume | — | -14 LUFS, pico ≤ -2 dBTP |
Ferramentas: ferramentas/decupar.py, montar.py, artes/, som.py, checar_palavras.py, checar_respiracao.py.

## Títulos e thumbs (padrões)
Ver `referencia/titulos.md`. Resumo: obra famosa no começo; contradiz o que o público acha ("não é sobre", "te ENGANOU", "FURO"); uma palavra em CAIXA ALTA no máximo; fala com "você"; 4 a 9 palavras.

## O que vamos fazer MELHOR que a referência
- Rosto e opinião de fã (as referências que mais crescem são dark ou quase dark).
- Ângulos que os canais pequenos não fizeram (ex.: Stranger Things pelo significado, não pelo furo).

## Decisões deste canal
- 2026-11-17: Nicho: cultura pop.
- 2026-11-17: O aluno MOSTRA O ROSTO. Formato híbrido (rosto no gancho, nas opiniões e nos CTAs; narração sobre cenas no resto).
- 2026-11-17: Canais dark servem para subnicho, temas, títulos, duração e molde de roteiro. Para edição com apresentador e thumbs com rosto, estudar também 1 ou 2 canais COM rosto.
- 2026-11-17: Subnicho: "o que o filme/série REALMENTE quer dizer".
- 2026-11-17: Idioma: português (BR).
- 2026-11-17: Nome do canal: **Luiz Telico**.
- 2026-11-18: Decupagem com o MÍNIMO de silêncio: cortes pela energia do áudio (não pelo tempo do Whisper), nenhuma pausa acima de ~0,15 s, folga de 35 ms antes e 60 ms depois da voz, sem cortar palavra. O aluno achou a 1ª versão (pausas de até 0,3 s) lenta demais.
- 2026-11-18: Manter os comentários pessoais curtos do Luiz (opinião de fã, humor); cortar os longos, os que têm palavrão pesado e os que afirmam fato errado ou não confirmado.
- 2026-11-18: v3 da decupagem aprovada como padrão de corte: tirar também respiração e estalo de boca (o aluno não quer o rosto na tela sem fala). Corte pela vibração da voz (100-900 Hz); só fica som sem vibração se for chiado de consoante ("s", "x", "t") grudado na palavra, até 0,12 s. Conferir sempre com ferramentas/checar_palavras.py + nova transcrição.
- 2026-11-18: Formato da amostra de 30 s APROVADO (rosto + cenas com zoom, nomes à mão com seta, frase-chave embaixo, carimbo, máquina de escrever, trilha synth original, efeitos contidos). Fontes do Google (Caveat, Special Elite, Anton) instaladas com autorização.
- 2026-11-18: Vídeo final: nenhum trecho preto, nenhuma respiração/estalo de boca/rosto parado (repetido pelo aluno como "muito importante"). Conferir com blackdetect + checar_respiracao.py antes de entregar.
- 2026-11-18: Imagens de trailer: conferir o 1º e o último quadro de cada cena (trailer tem transição preta e troca de plano rápida).
- 2026-11-18 (correções do aluno no vídeo 01): (1) zoom no rosto SEGUE o rosto (ferramentas/achar_rosto.py) e deixa o boné inteiro com folga em cima — nunca rosto baixo/cortado; (2) etiqueta com seta só dentro do plano do personagem: usar os cortes reais do trailer (filtrar raio/luz piscando) e conferir com ferramentas/conferir_setas.py; (3) zero respiração: voz = grave + tom regular (ferramentas/vozeamento.py), mas nunca cortar dentro de palavra transcrita (voz soprada do "Mike"); (4) conferir a IDENTIDADE do personagem antes de usar o plano (a "Max" de 3:45 era a Nancy).
