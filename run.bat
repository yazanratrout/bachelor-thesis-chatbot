@echo off
SETLOCAL

REM             #Config
SET VENV_DIR=venv
SET REQUIREMENTS=requirements.txt
SET STREAMLIT_APP=ui/app.py

REM             #Check Python Installation
where python >nul 2>nul
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not added to PATH.
    pause
    exit /b 1
)

REM             #Create virtual environment if not exists
IF NOT EXIST "%VENV_DIR%" (
    echo [INFO] Creating virtual environment...
    python -m venv %VENV_DIR%
)

REM             #Activate virtual environment
call %VENV_DIR%\Scripts\activate.bat

REM             #Upgrade pip and install dependencies
echo [INFO] Installing required packages...
pip install --upgrade pip
pip install -r %REQUIREMENTS%

REM             #Start the Streamlit app
echo [INFO] Launching the chatbot...
streamlit run %STREAMLIT_APP%

ENDLOCAL
