@echo off
chcp 65001 > nul
echo 🚗 Felgenrechner - Setup
echo ===============================

:: Prüfen ob Python installiert ist
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python ist nicht installiert oder nicht im PATH!
    echo Bitte Python von python.org installieren
    pause
    exit /b 1
)

echo ✅ Python gefunden
echo.

:: Virtual Environment erstellen
echo 📦 Erstelle Virtual Environment...
if exist venv (
    echo ⚠️  Virtual Environment existiert bereits
) else (
    python -m venv venv
    echo ✅ Virtual Environment erstellt
)

:: Virtual Environment aktivieren
echo 🔄 Aktiviere Virtual Environment...
call venv\Scripts\activate.bat

:: Requirements installieren
echo 📥 Installiere Dependencies...
pip install -r requirements.txt

echo.
echo 🎉 Setup komplett!
echo 💡 Nutze jetzt 'start.bat' zum Starten
echo.
pause
