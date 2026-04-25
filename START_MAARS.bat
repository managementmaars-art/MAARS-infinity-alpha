@echo off
setlocal

set "ROOT=%~dp0"
title MAARS Launcher

echo.
echo ==========================================
echo           MAARS Command Launcher
echo ==========================================
echo.

if not exist "%ROOT%backend\server.py" (
    echo [ERROR] Backend entrypoint not found at "%ROOT%backend\server.py"
    echo Make sure you are launching from the MAARS project root.
    echo.
    pause
    exit /b 1
)

if not exist "%ROOT%frontend\package.json" (
    echo [ERROR] Frontend package.json not found at "%ROOT%frontend\package.json"
    echo Make sure you are launching from the MAARS project root.
    echo.
    pause
    exit /b 1
)

if not exist "%ROOT%start_backend.bat" (
    echo [ERROR] Missing start_backend.bat
    echo.
    pause
    exit /b 1
)

if not exist "%ROOT%start_frontend.bat" (
    echo [ERROR] Missing start_frontend.bat
    echo.
    pause
    exit /b 1
)

echo [1/2] Launching backend...
start "MAARS Backend" "%ROOT%start_backend.bat"

echo [2/2] Launching frontend...
timeout /t 5 /nobreak >nul
start "MAARS Frontend" "%ROOT%start_frontend.bat"

echo.
echo Preview URLs:
echo   Frontend:  http://localhost:3000
echo   Backend:   http://localhost:8000
echo   API Docs:  http://localhost:8000/docs
echo.
echo Separate windows were opened for backend and frontend.
echo If one of them closes, read that window for the exact error.
echo.
pause
