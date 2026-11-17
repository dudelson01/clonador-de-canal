# Clonador de Canal com Claude Code

Com este kit, o Claude estuda um canal do YouTube que já dá certo e aprende a **fórmula** dele: roteiro, narração e edição. Depois ele pesquisa pautas, escreve o roteiro e **edita o vídeo sozinho**, até o MP4 pronto para postar.

> Clonar = copiar a **fórmula**, não o conteúdo. O kit já vem configurado para não reupar vídeo, não copiar roteiro e não clonar a voz de ninguém. Isso protege o seu canal de desmonetização.

---

## 1. O que você precisa

- Um computador com **Windows 10/11** (Mac também funciona, veja no fim).
- **Claude Code** com uma assinatura do Claude (Pro ou Max). Baixe em claude.ai/download e use a aba **Code**, ou instale no terminal.
- Uns **10 GB livres** no disco (vídeos e modelos de transcrição).
- Opcional, para voz de IA e banco de imagens: chaves de API (veja o passo 3).

## 2. Instalar (uma vez só)

1. Descompacte esta pasta onde quiser (ex.: `Área de Trabalho\Clonador-de-Canal`).
2. Dê dois cliques em **`instalar-windows.bat`**. Ele instala Python, Node.js, ffmpeg, yt-dlp, o Whisper (transcrição) e o navegador que renderiza as artes. Se o Windows pedir permissão, aceite.
3. Quando terminar, **feche e abra o terminal (ou o Claude Code) de novo**.

Se o `python` abrir a Microsoft Store: vá em **Configurações → Aplicativos → Configurações avançadas de aplicativos → Aliases de execução de aplicativo** e desligue os dois "Instalador de aplicativo (python)". Depois rode o `instalar-windows.bat` de novo.

## 3. Chaves de API (opcional)

1. Copie o arquivo **`.env.exemplo`** e renomeie a cópia para **`.env`**.
2. Abra no Bloco de Notas e preencha só o que for usar:
   - **ElevenLabs**: voz de IA (se você não for gravar a sua voz).
   - **Pexels** e **Pixabay**: vídeos e fotos grátis para a edição (as duas chaves são de graça).
3. Salve.

**Nunca mande o arquivo `.env` para ninguém** e nunca cole a chave no chat. Se compartilhar a pasta, apague o `.env` antes.

## 4. Usar

Abra o Claude Code **nesta pasta** e mande:

> Clona esse canal: https://www.youtube.com/@nomedocanal

Ele vai:
1. fazer o **raio-x** do canal (vídeos que mais bombaram, títulos, duração, thumbs);
2. estudar 3 vídeos e montar o **DNA do canal** (molde de roteiro, tipo de voz e a edição medida em números: segundos por corte, legenda, efeitos, música);
3. pedir a sua aprovação.

Depois é só seguir:

| Você diz | O Claude faz |
|---|---|
| `Pesquisa pautas` | acha 5 ideias com números que provam que o tema funciona |
| `Roteiro da ideia 2` | escreve o roteiro no molde do canal |
| `Narra` | gera a voz de IA (ou mande o seu áudio: `Decupa esse áudio`) |
| `Edita` | monta uma amostra de 30 s; aprovou, faz o vídeo inteiro |
| `Mete ficha` | faz tudo até o final sem parar para perguntar |
| `Refaz só o item 3` | corrige só aquele pedaço |
| `Anota isso` | grava a sua preferência para não esquecer nos próximos vídeos |
| `Status` | mostra o que está pronto e o que falta |

No fim você recebe, na pasta `canais/<canal>/videos/<video>/out/`:
- `video.mp4` pronto para postar;
- `seo.txt` com título, descrição com capítulos, tags, comentário fixado e sugestões de thumb;
- `painel.png` com quadros do vídeo, para você conferir rápido.

## 5. Dicas

- **Corrija o Claude sempre que algo não ficar bom** ("os cortes estão lentos", "a música está alta", "tira esse chiado") e diga "anota isso". Ele guarda no `CANAL.md` do canal, e o próximo vídeo já sai melhor.
- O primeiro vídeo demora mais. Do terceiro em diante, com as decisões anotadas, fica muito mais rápido.
- Se o YouTube bloquear as buscas ("não sou um robô"), é normal depois de muitas pesquisas: espere algumas horas.
- Na primeira transcrição o Whisper baixa o modelo (algumas centenas de MB). Sem placa de vídeo NVIDIA ele roda na CPU, mais devagar, mas funciona.
- Vídeo com pessoa, lugar ou evento **realista gerado por IA**: marque "conteúdo alterado ou sintético" na hora de postar.

## 6. Mac

No Terminal, com o Homebrew instalado:

```bash
brew install python node ffmpeg yt-dlp
```

```bash
python3 -m pip install numpy faster-whisper
```

```bash
npm install && npx playwright install chromium
```

Depois siga a partir do passo 3.
