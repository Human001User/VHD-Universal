@echo off
chcp 65001 > nul
title VitalDelete Bot — Установка
echo Устанавливаю зависимости...
pip install -r requirements.txt
echo.
echo Готово! Запустите start.bat
pause
