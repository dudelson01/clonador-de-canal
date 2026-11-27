# Toy Aisle Ghosts — DNA do canal (rascunho para aprovar)

**Nicho:** ascensão e queda de empresas
**Subnicho:** *What Happened to…?*, a história de brinquedos, lojas e marcas de infância dos anos 80, 90 e 2000 que sumiram, faliram ou se transformaram.
**Idioma:** inglês (público dos EUA, 25–45 anos, nostálgico). Versão PT/ES só depois de validar.
**Formato:** vídeo longo de 14–20 min, 1 a 2 por semana (qualidade > volume; veja o raio-x).
**Nomes alternativos:** Toy Aisle Ghosts (livre em 24/11/26) · The Lost Toy Aisle · Recess Is Over

## Sobre o canal (About)
> Every toy you begged for had a story nobody told you. Toy Aisle Ghosts digs into the rise, the fall and the strange afterlife of the toys, stores and brands that raised a generation: the boardroom fights, the bad bets, the fads that burned out overnight. New deep-dive every week.

**Palavras-chave do canal:** what happened to, toy history, rise and fall, 90s nostalgia, 80s toys, discontinued toys, toy companies, business documentary, childhood brands, toy store

## Configuração obrigatória no YouTube
- **Não é conteúdo para crianças** ("No, it's not made for kids"). O público é adulto e nostálgico. Marcar "para crianças" mata o alcance e a monetização.
- Narração e imagens de IA: marcar "conteúdo alterado ou sintético" quando houver pessoa, lugar ou evento realista gerado por IA.

## Roteiro (molde)
1. **Gancho (0–20 s):** paradoxo ou fato chocante verificável, sem saudação. Ex.: "One week after Toys"R"Us announced it was closing every store in America, the man who founded it died."
2. **Promessa (20–40 s):** o que o vídeo vai revelar e por que importa.
3. **Ascensão (30%):** origem humilde, a sacada genial, o auge com números.
4. **Virada (30%):** o erro, a decisão ruim, o concorrente, a dívida.
5. **Queda (25%):** falência, liquidação, o último dia.
6. **Depois (10%):** o que existe hoje, o retorno e a nostalgia, com uma pergunta para os comentários ("What was the first toy you remember buying there?").
- Microganchos a cada ~2 min ("But that wasn't the real problem.").
- Todo número e data conferido em fonte confiável antes de narrar.

## Narração
- Voz de IA (ai33.pro), masculina, grave, tom de documentário, ~165–170 palavras/min (Nerf: 187).
- **Voz escolhida (27/11/26): "Daniel - Warm, Confident & Compelling"** (ai33/ElevenLabs, voice_id 8GmsjNWRZ3Rk8VmRpvBZ), atempo 1,05 para chegar perto de 168 palavras/min.
- Nunca clonar voz de pessoa real.

## Edição (medida em 27/11/26 nos 3 vídeos enviados pelo aluno; detalhes em `referencia/edicao-medida.md`)
- **Corte a cada ~2,0 s na intro (60 s) e ~2,8 s no resto.** Referências: 1,7 a 3,6 s por plano.
- **Base visual:** colagem sobre papel creme de catálogo antigo. Fotos de IA estilo "foto/catálogo dos anos 80–90" entram como cards com borda branca e sombra, 1 ou 2 por vez, sempre deslizando ou com zoom lento.
- **Frase-chave da narração acima do card** (2–6 palavras, negrito itálico): datas, lugares, números.
- **Palavra solta em tela preta** nas viradas de capítulo ("BUT…", "THE DEBT", "WAS IT AMAZON?").
- Destaques: mapa dos EUA com pinos, contador de número e de ano, etiqueta de preço, carimbo ("CHAPTER 11"), placa "CLOSED".
- **Sem material de terceiros** (vídeos de outros canais, comerciais), ao contrário de Nerf/Zombie Catchers: protege o canal de "conteúdo reutilizado".
- Sem rosto realista de pessoa real gerado por IA (ex.: Charles Lazarus aparece só como silhueta).
- Sem legenda contínua.
- Trilha sintetizada, synth nostálgico baixinho sob a voz, troca a cada capítulo. -14 LUFS.

## Thumbnail (padrão do canal)
- Escola "nostalgia + perda": o produto/logo icônico **grande e reconhecível**, dentro de um cenário abandonado, apagado ou rachado. Contraste quente (produto) contra frio (fundo).
- Texto: no máximo 3 palavras, fonte grossa, branco com contorno ou faixa vermelha.
- Sem rosto de pessoa real inventada; sem copiar arte de outro canal.

## Decisões deste canal
- 24/11/2026: nicho e subnicho escolhidos com base no raio-x (aguardando aprovação do aluno).
- 27/11/2026: aluno enviou 3 vídeos de referência (Nerf, Zombie Catchers, Every Restaurant Chain) e pediu o vídeo 1. Edição medida e definida acima; roteiro do vídeo 1 (Toys"R"Us) escrito com gancho atual (120 lojas novas no Natal de 2026).
- 27/11/2026: aluno escolheu a voz C (Daniel) entre 3 amostras.
- 27/11/2026: aluno aprovou o formato da amostra do gancho (colagem em papel creme, cards, palavra em tela preta, mapa/números/carimbos, trilha synth). Ferramenta: `ferramentas/colagem.py` + `ferramentas/trilha.py`. Fluxo: roteiro → `narrar.py` → `timeline.py` (conferir trechos suspeitos com o modelo medium; o small trocou "Toys R Us" por "Lazarus") → `cenas.py` do vídeo → `imagem_ai33.py` (1K, 550 créditos/imagem) → `colagem.py --musica trilha.wav`.
- 27/11/2026: aluno pediu o vídeo 1 refeito com **fotos reais do Wikimedia Commons**. 48 das 84 imagens viraram fotos reais livres (lojas fechando em 2018, Times Square, Geoffrey, lojas novas, Washington anos 40 da Library of Congress, Walmart, Amazon etc.); ficaram em IA só as cenas metafóricas ou sem foto livre (Lazarus, chave passando de mão, dinheiro queimando, quadro de reunião…). Ferramenta: `ferramentas/commons.py buscar` → olhar as folhas → `reais/escolhas.json` → `commons.py usar` (grava em `midia/img` e anota `reais/creditos.txt`). **Créditos na descrição e no comentário fixado são obrigatórios** (CC BY / CC BY-SA). A Wikimedia limita robôs num IP compartilhado: a ferramenta faz 1 pedido a cada 2–3 s e repete o que der 429; definir `COMMONS_CONTACT=` no `.env` (contato do aluno) ajuda a não ser bloqueado.
