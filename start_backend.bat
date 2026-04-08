@echo off
cd /d "%~dp0backend"
call venv\Scripts\activate
start "MAARS Backend" cmd /k "uvicorn server:app --reload --port 8000"
