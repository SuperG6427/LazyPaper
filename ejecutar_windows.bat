@echo off
REM LazyPaper Launcher - Windows
chcp 65001 > nul
cd /d "%~dp0"
if not exist "lazypaper\lazypaper.py" (
    echo Error: Estructura de proyecto incorrecta.
    echo Debe existir: lazypaper\lazypaper.py
    pause
    exit /b 1
)
if "%VIRTUAL_ENV%"=="" (
    if exist "venv\" (
        call venv\Scripts\activate.bat
    ) else (
        python -m venv venv
        call venv\Scripts\activate.bat
        pip install -r requirements.txt
    )
)
cd lazypaper
python lazypaper.py
cd ..
pause