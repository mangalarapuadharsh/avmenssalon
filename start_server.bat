@echo off
echo Starting Backend Server...
cd /d "%~dp0"
start http://localhost:5000
python backend/app.py
pause
