@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ==============================================
echo   Clonador de Canal - instalacao (Windows)
echo ==============================================
echo.
echo === 1/4 Instalando Python, Node.js e ffmpeg (winget) ===
winget install -e --id Python.Python.3.12 --accept-source-agreements --accept-package-agreements
winget install -e --id OpenJS.NodeJS.LTS --accept-source-agreements --accept-package-agreements
winget install -e --id Gyan.FFmpeg --accept-source-agreements --accept-package-agreements
echo.
echo === 2/4 Atualizando o PATH desta janela ===
set "PATH=%PATH%;%ProgramFiles%\nodejs;%LOCALAPPDATA%\Programs\Python\Python312;%LOCALAPPDATA%\Programs\Python\Python312\Scripts"
echo.
echo === 3/4 Bibliotecas do Python (yt-dlp, Whisper, numpy) ===
python -m pip install --upgrade pip
python -m pip install --upgrade numpy faster-whisper yt-dlp requests python-dotenv
echo.
echo === 4/4 Playwright (renderiza legendas e artes) ===
call npm install
call npx playwright install chromium
echo.
echo ==============================================
echo Pronto! Feche esta janela e abra o Claude Code nesta pasta.
echo Se algum comando acima "nao foi encontrado", feche, abra de novo
echo e rode o instalar-windows.bat mais uma vez.
echo ==============================================
pause
