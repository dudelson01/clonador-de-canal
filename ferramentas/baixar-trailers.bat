@echo off
chcp 65001 >nul
REM Baixa os trailers do video "Por que os atores nao sao mais feios?"
REM Precisa do yt-dlp e do ffmpeg (o instalar-windows.bat ja instala os dois).
REM Os arquivos vao para a pasta "trailers" ao lado deste arquivo.

cd /d "%~dp0"
if not exist trailers mkdir trailers
python -m pip install -U yt-dlp >nul 2>&1

set F=-f "bv*[height<=1080][ext=mp4]+ba[ext=m4a]/b[height<=1080]" --merge-output-format mp4 --no-playlist

call :baixa ghostbusters-1984      "https://www.youtube.com/watch?v=wQAljlSmjC8"
call :baixa twisters-2024          "https://www.youtube.com/watch?v=wdok0rZdmx4"
call :baixa rocky-1976             "https://www.youtube.com/watch?v=-Hk-LYcavrw"
call :baixa the-batman-2022        "https://www.youtube.com/watch?v=mqqft2x_Aa4"
call :baixa taxi-driver-1976       "https://www.youtube.com/watch?v=T5IligQP7Fo"
call :baixa chalamet-a-complete-unknown "ytsearch1:A Complete Unknown official trailer Searchlight"
call :baixa die-hard-1988          "ytsearch1:Die Hard 1988 official trailer"
call :baixa batman-1989            "ytsearch1:Batman 1989 official trailer Michael Keaton"
call :baixa era-uma-vez-no-oeste-1968 "ytsearch1:Once Upon a Time in the West 1968 trailer"
call :baixa poderoso-chefao-1972   "ytsearch1:The Godfather 1972 official trailer Paramount"
call :baixa fuga-de-nova-york-1981 "ytsearch1:Escape from New York 1981 trailer"
call :baixa x-men-2000             "ytsearch1:X-Men 2000 official trailer"
call :baixa deadpool-wolverine-2024 "ytsearch1:Deadpool and Wolverine official trailer Marvel"
call :baixa cidade-de-deus-2002    "ytsearch1:Cidade de Deus trailer oficial 2002"
call :baixa bebe-de-rosemary-1968  "ytsearch1:Rosemary's Baby 1968 official trailer"
call :baixa star-wars-1977         "ytsearch1:Star Wars 1977 original trailer"
call :baixa creed-2015             "ytsearch1:Creed 2015 official trailer"
call :baixa homem-aranha-2002      "ytsearch1:Spider-Man 2002 official trailer Tobey Maguire"
call :baixa homem-aranha-2021      "ytsearch1:Spider-Man No Way Home official trailer"
call :baixa tres-homens-em-conflito-1966 "ytsearch1:The Good the Bad and the Ugly 1966 trailer"
call :baixa invasores-de-corpos-1978 "ytsearch1:Invasion of the Body Snatchers 1978 trailer"

echo.
echo ============================================
echo Pronto! Agora:
echo 1. Clique com o botao direito na pasta "trailers" e escolha Compactar (zip).
echo 2. Suba o trailers.zip no Google Drive e compartilhe como "qualquer pessoa com o link".
echo 3. Mande o link para o Claude.
echo ============================================
pause
exit /b

:baixa
echo Baixando %1 ...
python -m yt_dlp %F% -o "trailers\%~1.%%(ext)s" "%~2"
timeout /t 3 >nul
exit /b
