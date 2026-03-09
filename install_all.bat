@echo off
REM Script di installazione completa per l'applicazione di riconoscimento vocale
REM Esegui questo script con doppio click per installare tutte le dipendenze

echo ================================================
echo   INSTALLAZIONE COMPLETA
echo   Riconoscimento Vocale Vosk
echo ================================================
echo.

REM Controlla se Python è installato
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python non trovato!
    echo Installa Python da https://www.python.org/downloads/
    echo Assicurati di aver selezionato "Add Python to PATH" durante l'installazione.
    pause
    exit /b 1
)

echo Python trovato!
echo.

REM Installa le dipendenze Python
 echo [1/2] Installazione dipendenze Python...
 echo.
 python scripts/install_dependencies.py
 if errorlevel 1 (
     echo.
     echo ERROR: Installazione dipendenze fallita!
     pause
     exit /b 1
 )
 
 echo.
 echo ================================================
 echo.
 
 REM Chiedi quale modello scaricare
 echo [2/2] Scegli il modello vocale da scaricare:
 echo.
 echo 1) Small (48 MB) - Piú veloce, meno accurato
  echo 2) Medium (1.2 GB) - Piú lento, piú accurato
 echo.
 set /p choice="Scegli 1 o 2: "
 
 if "%choice%"=="1" (
     echo Scaricamento modello Small...
     python scripts/download_model.py small
 ) else if "%choice%"=="2" (
     echo Scaricamento modello Medium...
     python scripts/download_model.py medium
 ) else (
     echo Scelta non valida, uso modello Small di default...
     python scripts/download_model.py small
 )
 if errorlevel 1 (
     echo.
     echo ERROR: Scaricamento modello fallito!
     pause
     exit /b 1
 )

echo.
echo ================================================
echo INSTALLAZIONE COMPLETATA CON SUCCESSO!
echo ================================================
echo.
echo Per avviare l'applicazione, esegui: python main.py
echo.
pause
