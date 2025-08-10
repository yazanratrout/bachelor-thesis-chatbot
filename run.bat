@echo off
SETLOCAL
REM Ensure we run from the folder that contains this .bat
cd /d "%~dp0"

REM             #Config
SET "VENV_DIR=venv"
SET "REQUIREMENTS=requirements.txt"
SET "STREAMLIT_APP=ui/app.py"

REM             #Check Python Installation
where python >nul 2>nul
IF ERRORLEVEL 1 (
    echo [ERROR] Python is not installed or not added to PATH.
    pause
    exit /b 1
)

REM             #Create virtual environment if not exists
IF NOT EXIST "%VENV_DIR%\Scripts\python.exe" (
    echo [INFO] Creating virtual environment...
    python -m venv "%VENV_DIR%"
)

REM             #Use venv's python for everything (no activation required)
SET "PYV=%VENV_DIR%\Scripts\python.exe"

echo [INFO] Installing required packages...
"%PYV%" -m pip install --upgrade pip
"%PYV%" -m pip install -r "%REQUIREMENTS%"

echo [INFO] Launching the chatbot...
"%PYV%" -m streamlit run "%STREAMLIT_APP%"

ENDLOCAL
