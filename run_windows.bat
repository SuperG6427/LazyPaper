@echo off
REM LazyPaper Launcher - Windows
chcp 65001 > nul
cd /d "%~dp0"
if not exist "lazypaper\lazypaper.py" (
    echo Error: Incorrect project structure.
    echo Must exist: lazypaper\lazypaper.py
    pause
    exit /b 1
)
if "%VIRTUAL_ENV%"=="" (
    REM Not in virtualenv, check if exists
    if exist "venv\" (
        echo Activating existing virtual environment...
        call venv\Scripts\activate.bat
    ) else (
        echo Virtual environment not found. Creating...
        python -m venv venv
        call venv\Scripts\activate.bat
        echo Installing dependencies...
        pip install -r requirements.txt
    )
) else (
    echo Already in virtual environment: %VIRTUAL_ENV%
)
cd lazypaper
python lazypaper.py
cd ..
pause