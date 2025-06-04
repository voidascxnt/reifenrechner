@echo off
chcp 65001 > nul
title Felgenrechner Pro
color 0A

echo.
echo     🚗 FELGENRECHNER PRO 🚗
echo     ===============================
echo.
echo     ⚡ Alle Reifen-Kombinationen auf einen Klick
echo     🎯 Tuner-Features mit Scene Points
echo     📱 Apple PWA-Integration
echo.
echo     Starte Server...
echo.

:: Virtual Environment aktivieren
call venv\Scripts\activate.bat

:: Server starten mit Port 3000 (weniger Probleme als 8000)
echo 🌐 Server läuft auf: http://localhost:3000
echo.
echo ⭐ TIPP: Bookmark dir den Link für schnellen Zugriff!
echo 📱 APPLE: Speichere als App auf dem Home-Bildschirm
echo.
echo 🛑 Zum Beenden: Strg+C drücken
echo.

python backend.py

echo.
echo 👋 Server beendet. Danke fürs Nutzen!
pause
