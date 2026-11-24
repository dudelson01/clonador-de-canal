# Pesquisa: nicho de nutrição (24/11/2026)

Busca pela YouTube Data API em PT, EN e ES, vídeos dos últimos 45 dias ordenados por views.
**Outlier** = canal com menos de 50 mil inscritos, vídeo com 10 mil+ views, views ÷ inscritos ≥ 2, duração ≥ 3 min.

## Subnichos

| Subnicho | Canais pequenos com outlier | Views somadas | Idiomas |
|---|---|---|---|
| **Nutrição para 60+** (músculo/sarcopenia, pernas fortes) | 42 | 11,1 mi | EN 26 · ES 24 · PT 1 |
| "O que acontece se comer X todo dia" | 24 | 5,5 mi | EN 21 · ES 3 · PT 1 |
| Proteína/músculo depois dos 50 | 19 | 4,3 mi | EN 13 · ES 4 · PT 3 |
| Comer antes de dormir | 17 | 3,3 mi | EN 11 · PT 8 · ES 7 |
| Jejum/emagrecimento | 10 | 2,3 mi | quase tudo pessoa real (vlog) |
| Rins e fígado | 8 | 1,5 mi | ES 6 · PT 3 |
| Intestino | 5 | 0,8 mi | ES · PT |
| Alimentos perigosos / vitaminas / glicose | 1–3 | — | fraco |

Lista completa: `outliers.json` (155 vídeos). Grade das thumbs: `thumbs-outliers.jpg`.

## Distribuição de views dos canais pequenos (28 canais novos do nicho)
Arquivo: `canais-distribuicao.json`.
- Mediana: **71% dos vídeos com menos de 1.000 views** e só 10% acima de 10 mil.
- Em média, **1 vídeo responde por 77% de todas as views do canal**: o nicho funciona à base de hits.
- Os temas que viram hit se repetem entre canais (amendoim × rins, fruta antes de dormir × rins, café da manhã para músculo depois dos 60).
- Viés da amostra: só aparecem canais que tiveram pelo menos 1 hit. Canais que nunca estouraram não entram na busca.
