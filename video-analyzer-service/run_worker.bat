@echo off
echo ========================================
echo Worker Mollo - Video Analyzer
echo ========================================
cd /d "%~dp0"
call venv\Scripts\activate
python worker.py
pause
