# Raio-X do nicho — 24/11/2026

Fonte: YouTube Data API. Busca em PT, EN e ES, vídeos dos últimos 45 dias, ordenados por views.
**Outlier** = canal com menos de 50 mil inscritos, vídeo com 10 mil+ views, views ÷ inscritos ≥ 2, duração ≥ 3 min.

## 1. Subnichos testados (quantos canais pequenos têm outliers)

| Subnicho | Canais pequenos com outlier | Views somadas | Veredito |
|---|---|---|---|
| Ascensão e queda: **marcas/empresas** ("What Happened to…", "…Empire Is Collapsing") | 23+ | ~10 mi | ✅ **mais forte** |
| Queda de impérios (Roma, Otomano, etc.) | 24 | ~6 mi | ⚠️ dominado por canais grandes de história |
| Empresas que faliram (genérico) | 16 | ~2,4 mi | ✅ mesmo fenômeno das marcas |
| Civilizações e artefatos perdidos | 6 | 0,5 mi | ❌ fraco |
| Casos históricos não resolvidos | 6 | 0,6 mi | ❌ fraco, dominado por true crime grande |
| Desaparecimentos misteriosos | 6 | 0,5 mi | ❌ fraco |
| Navios/aviões desaparecidos | 1 | 0,2 mi | ❌ |
| "Bilionário perdeu tudo" | 43 | 27 mi | ❌ **falso positivo**: são novelinhas de IA, não documentário |

**Idiomas:** quase todo o sinal está em **inglês (EUA)**. Em PT e ES há pouquíssimos outliers no subnicho.

## 2. O padrão que está funcionando: arquivos de "What Happened to [marca]?"

Uma onda de canais novos (criados em 2026), cada um especializado em **uma categoria de marcas**:

| Canal | Categoria | Inscritos | Criado | Posts/30d | Mediana | Maior vídeo |
|---|---|---|---|---|---|---|
| Forgotten Fragrance Empires | perfumes/cosméticos | 5.960 | mar/26 | 4 | 7.104 | 570.701 |
| The American Shoe Archive | tênis/sapatos | 3.940 | ago/26 | 30 | 1.218 | 474.811 |
| The Forgotten Vanity | cosméticos | 1.750 | out/26 | 25 | 1.517 | 89.187 |
| Forgotten Foundations | lingerie | 1.510 | jan/26 | 25 | 3.047 | 123.958 |
| Forgotten Storefronts | lojas de roupa | 1.470 | jan/26 | 25 | 706 | 74.303 |
| Forgotten Dress Empires | vestidos | 213 | out/26 | 23 | 364 | 12.194 |
| Proxy | brinquedos/jogos | 3.560 | fev/26 | 1 | 2.315 | **2.723.083** (Nerf) |
| Hungerwise | comida/restaurantes | 9.880 | fev/26 | 4 | **32.288** | 1.129.235 |
| Sarah Johnson | "Empire Is Collapsing" | 10.700 | out/26 | 33 | 7.250 | 462.669 |

**Leitura:**
- Os canais que postam todo dia têm mediana baixa (300 a 3 mil views): é loteria de volume. Os que postam pouco e caprichado (**Hungerwise** e **Proxy**) têm mediana bem maior.
- O formato "X's $N Billion Empire Is Collapsing" já tem pelo menos 8 clones em 45 dias, e o título exagera ("Walmart está colapsando"). Risco de saturação e de conteúdo enganoso. **Evitar.**
- As categorias perfume, tênis, lingerie, vestidos, lojas e restaurantes **já têm dono**.
- **Brinquedos e marcas de infância** não têm nenhum canal-arquivo dedicado, mas têm as maiores explosões: Nerf (2,7 mi com 3,5 mil inscritos), Zombie Catchers (1,26 mi), Rita's Putties (285 mil). **Faixa livre.**

## 3. Por que os outliers viralizaram

| Elemento | Padrão observado |
|---|---|
| **Título** | `What Happened to [MARCA]?` + subtítulo com nostalgia e o público ("The ___ Every 70s Girl Wore", "Every American Grew Up Using") ou um número/consequência ("Foot Locker Shut Down After Four Decades", "Sold for Nothing"). A marca vem primeiro, porque o público busca e reconhece pelo nome. |
| **Thumbnail** | Duas escolas: (a) **nostalgia quente**: o produto icônico gigante em primeiro plano, pessoa da época, logo vintage, tons sépia/dourado e quase nenhum texto (Noxzema, Avon, Prell); (b) **choque**: logo em chamas ou caindo dinheiro, fundo escuro e 2–3 palavras enormes ("GREEDY SLOP", "FROM ICON TO COLLAPSE", "CATALOG GONE"). Sempre **o logo real e reconhecível**. |
| **Gancho** (Goodwill, 462 mil) | Paradoxo nos primeiros 10 s ("ganha o estoque de graça e ainda assim não fecha a conta") → promessa ("nobody in the organization has the power to fix it") → cena concreta e visual (a fila de carros no galpão de doações). Sem "olá, bem-vindos". |
| **Descrição** | Começa com uma pergunta de nostalgia ("Do you remember the iconic blue jar…?"), 3 hashtags no topo, capítulos com marcas/datas. |
| **Engajamento** | Muitos comentários (Noxzema: 1.150; Nerf: 1.126). O público conta as próprias memórias, o que impulsiona o vídeo. |
| **Duração** | Duas faixas que funcionam: 8–20 min (Proxy, Hungerwise) ou 40–50 min (arquivos "boomer", que o público assiste deitado). |

Grades das thumbs analisadas: `referencia/thumbs/grid0.jpg` e `grid1.jpg`. Dados brutos: `referencia/outliers.json`.
