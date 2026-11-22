# Canal principal (nome a definir)

## Nicho e público
Cinema e cultura pop, com outliers gringos adaptados para o português do Brasil.

## Idioma e formato
- Português do Brasil.
- Vídeo longo (cerca de 10 a 12 min), 16:9.

## Voz
- Voz de IA (ai33 pro, API v3, modelo eleven_v4), do começo ao fim. Voz: Gabriel - Casual (jovem, "amigo contando história"). Amostras das outras em referencia/amostras-voz/

## Roteiro
- A tese e os exemplos vêm do outlier gringo, mas o texto é reescrito do zero (nunca uma tradução palavra por palavra).
- Humor e personalidade: comparações do dia a dia brasileiro, autodepreciação leve, exemplo brasileiro quando couber.

## Edição
- Canal dark: sem rosto.
- Cenas curtas dos filmes citados (2 a 4 s), sempre com narração por cima, mais artes, textos e memes animados nas piadas.

## Decisões deste canal
- 2026-11-22: o canal vai ser **dark**, sem mostrar o rosto do aluno (melhor para a produtividade no começo). Narração por voz de IA (ai33 pro).
- 2026-11-22: voz escolhida: **Gabriel - Casual** (ai33 pro, voice_id BECjFqjKpX1jVslC0trK, modelo eleven_v4, velocidade 1.0).
- 2026-11-22: blocos longos da ai33 às vezes cortam a última palavra. Conferir a energia no fim de cada bloco; se cortar, gerar a última frase sozinha e emendar. Final com "..." e "!" ajuda. Na emenda, o atraso vale para os DOIS canais (adelay=...:all=1): senão fica eco de duas vozes (erro de 2026-11-22, já corrigido).
- 2026-11-22: roteiros com **humor e personalidade**, adaptados de outliers gringos, nunca traduzidos ao pé da letra.
- 2026-11-22: **formato da amostra APROVADO** (gancho de 32 s): cenas curtas dos trailers com zoom lento, legenda palavra por palavra com a palavra falada em amarelo, um destaque animado diferente a cada frase (contador, carimbo, checklist, etiqueta, tela de filtro, letreiro, máquina de escrever), música original curiosa com ducking, efeitos discretos, -14 LUFS.
- 2026-11-22: legenda da narração **menor**: Montserrat 900, 46 px (era 66), contorno 8 px, mais embaixo (top 868 px).
- 2026-11-22: YouTube bloqueia download na nuvem. Trailers: o aluno baixa no PC e manda pelo Drive, cada arquivo como "qualquer pessoa com o link".
- 2026-11-22: vídeo 01 ("Por que os atores não são mais feios?") entregue: 10:49, 259 cenas de 20 trailers, 109 destaques, 7 músicas originais (uma por parte). Ferramentas: indice_cenas.py (rostos/cartelas), planejar.py, folha_plano.py (conferência), plano_completo.py.
- 2026-11-22: na conferência, bloquear cenas com letreiro/crédito/logo/anúncio dos trailers (build/bloqueadas.json) e carimbo sempre em UMA linha (white-space:nowrap).
- 2026-11-22: o aluno gravou o roteiro com o PRÓPRIO ROSTO. Formato híbrido escolhido: **rosto em tela cheia nas piadas, ganchos, transições e CTA (~33% do tempo), trailers com a voz dele por cima nos exemplos**. Pulos de zoom (100/114/106%) a cada ~3 s no rosto.
- 2026-11-22: decupagem: ficar com a última versão boa, manter os bons improvisos dele (ex.: "subiu mais que 10", "Bali ou Madrid", "não sei falar esse sobrenome") e dar destaque a eles. Cortes alinhados aos quadros (1/30 s) para a boca não dessincronizar.
- 2026-11-22: com o rosto na tela, carimbo e letreiro descem para a altura do peito (não cobrem o rosto).
- 2026-11-22: entregue out/video-rosto.mp4 (12:05) + out/seo-rosto.txt. A versão só com voz de IA (out/video.mp4) continua disponível.
- 2026-11-22: **versão com rosto NÃO aprovada.** O aluno reclamou:
  - cortes que comem palavras ("mais chatos", "Timothée Chalamet") e frase repetida (0:45);
  - **rosto parado sem falar** depois de várias frases: cortar TODA pausa longa (máx. ~0,2 s de respiro);
  - **clipes desconexos da fala**: falou de um ator/filme, tem que aparecer AQUELE ator/AQUELA cena. Pode usar **fotos dos atores**. Nada de cena genérica "do filme" com outro ator;
  - **menos animações** na tela e **SEM legenda embaixo**;
  - referência de edição: vídeo mandado pelo Drive (estudar e copiar o estilo).

