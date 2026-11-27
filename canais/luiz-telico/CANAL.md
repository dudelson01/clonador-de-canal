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
Thumbs SEM o rosto do Luiz (decisão de 18/11/2026): ver `referencia/thumbs.md`.
Títulos: ver `referencia/titulos.md`. Resumo: obra famosa no começo; contradiz o que o público acha ("não é sobre", "te ENGANOU", "FURO"); uma palavra em CAIXA ALTA no máximo; fala com "você"; 4 a 9 palavras.

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
- 2026-11-18: Thumbs SEM o rosto do Luiz por enquanto (início do canal). Padrão: personagem da obra em close + 2-4 palavras minúsculas brancas que contradizem + 1 destaque (sublinhado vermelho ou seta à mão). Ref.: Brett's Thoughts e SB Cinema (referencia/thumbs.md).
- 2026-11-19 (vídeo 02, decupagem v1 reprovada): sobrou respiração, palavras cortadas e frase repetida. Regras novas: (1) transcrever as gravações com Whisper medium e prompt de hesitação, e NÃO confiar no tempo das palavras em trecho com várias tentativas (o Whisper junta as tentativas numa frase só); (2) só grudar som sem voz na palavra se for chiado de consoante (agudo > grave), nunca sopro; (3) proteger a palavra inteira; (4) antes de mandar, rodar checar_palavras, checar_respiracao (seção 'respiracoes') e conferir_texto (frase repetida) e ler a transcrição do corte inteiro.
- 2026-11-20: O aluno regravou o vídeo 02 com MAIS humor e personalidade no roteiro (piadas e comentários são parte do formato agora: manter as piadas, cortar só erros). Exigência repetida: ZERO respiração e TODOS os erros cortados (tropeço, frase refeita, palavra errada).
- 2026-11-20: YouTube bloqueou o download de trailers neste ambiente ('não sou um robô'). Não burlar: pedir os trailers ao aluno pelo Drive ou tentar depois.
- 2026-11-20 (vídeo 02, decupagem v4 reprovada): 'cortou demais, cortou palavras, perdeu o contexto'. O corte por tom de voz comia sílaba fraca no começo/fim da frase e palavras curtas ('e', 'a', 'eu'). Regras: começo/fim de cada frase medidos pelo áudio (não pelo Whisper); som com cara de voz (grave >> agudo) conta como voz mesmo sem tom; não cortar pausa menor que 0,15 s; conferir SEMPRE com ferramentas/comparar_trechos.py (transcreve original e corte de cada frase e lista palavra que sumiu) antes de mandar.
- 2026-11-21 (vídeo 02, correções do aluno na v5b): fim de palavra cortado (escuraçada, assim, história, final feliz…) e cortes abruptos; trechos sem fala sobrando (dedo na tela, ajeitando óculos, tosse, assoar o nariz; o Whisper transcreveu a tosse como 'a fim!' e o nariz como 'fuuu'). Preferência: NENHUM espaço grande sem fala, mas também nada de corte abrupto. Regra nova: decupar em modo 'palavras' (plano['modo']='palavras'): o corte é montado em volta das palavras transcritas; pausa entre palavras até 0,2 s fica como foi falada; o fim de cada palavra vai até o som acabar (+0,06 s) e nunca antes do fim da palavra; fade de 25 ms nas emendas. Desconfiar de 'fala' curta e estranha do Whisper (tosse, espirro, nariz).
- 2026-11-21: Decupagem v6 do vídeo 02 APROVADA (modo 'palavras' + cortes manuais). O aluno pediu 'edição muito boa: animações, textos, clipes'.
- 2026-11-21 (vídeo 02, edição): o aluno manda os trailers pelo Drive (YouTube bloqueia aqui). Arquivos do Drive precisam estar como 'Qualquer pessoa com o link'. Trailers com faixa preta/legenda embutida: zoom mínimo por trailer (gerar_plano_video.py: ZMIN/FOCO). Rosto: zoom parte do topo do quadro (boné encosta no topo nesta gravação). Artes novas: meme, diálogo mãe x filho, lista ✓/✗, versus, card de filme, IA glitch, polaroid, dinheiro. Efeitos de cor no rosto ilustram a fala (lavado, crt, pb, vermelho).
- 2026-11-21 (correção do aluno no vídeo 02): animações do lado direito grandes demais, cortadas na borda. Regra: toda arte fica inteira dentro da área segura (artes.html mede a largura natural e empurra/encolhe; listas quebram linha). Conferir SEMPRE com ferramentas/artes/conferir_bordas.mjs antes de renderizar.
- 2026-11-26 (retenção do vídeo "Os maiores erros de Maze Runner", 14:53, média 4:51 = 32,6%): 0:30=67%, 3:55=36%, 7:04=30%, 13:23=25%, fim=16%. A perda está quase toda em 0:50–3:55, num bloco de ARGUMENTO abstrato (custo da CRUEL, memória, verdugos) sem cena; a curva fica estável quando o roteiro passa a contar o filme cena por cena (3:34 em diante). A tese foi entregue aos 0:37 (mata o loop aberto). Queda final a partir do "no fim das contas" + ressalva + CTA longo.
- 2026-11-26: Referência nova de formato: Quarto do Caio, "A SÉRIE MAIS PERTURBADA DA NETFLIX" (resumo comentado de You T2, 47 min, ~1 mi views em canal pequeno). Regras para os próximos roteiros: (1) RESUMO COMENTADO em ordem cronológica, furos dentro da cena em que acontecem; (2) nada de bloco de teoria > 20–30 s sem cena; (3) gancho = cena/reviravolta ("final feliz? não"), promessa sem entregar a conclusão; apresentação do canal só depois do gancho (~1:00–1:40); (4) mini-gancho a cada 30–60 s ("adivinha…", "veremos mais pra frente"); (5) Luiz faz a pergunta do espectador ("Mas Luiz, por que…?"); (6) muita personalidade/piada/referência; (7) final no clímax, sem "no fim das contas", despedida ≤ 20 s; (8) título amplo/emocional sem depender do nome da obra; thumb com frase em tom de fofoca sobre cena do ÚLTIMO TERÇO do vídeo.
- 2026-11-26: Próxima pauta escolhida: Resident Evil (2026, Zach Cregger). Clipes: só trechos curtos (trailers/clipes oficiais ou gravação curta do aluguel), nunca o filme inteiro.
- 2026-11-27: Vídeo 04 (Resident Evil): a EDIÇÃO ficou com um editor humano. Entregue: roteiro v3 + decupagem v1 (out/decupagem_v1_previa.mp4, 7:49). Não editar este vídeo.
