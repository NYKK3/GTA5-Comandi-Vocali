@echo off
REM Script per avviare l'applicazione di riconoscimento vocale

echo ================================================
echo   Riconoscimento Vocale - Vosk
echo ================================================
echo.

REM Controlla se Python è installato
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python non trovato!
    echo Installa Python da https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Avvia l'applicazione
echo Avvio dell'applicazione...
echo.
python main.py

pause
