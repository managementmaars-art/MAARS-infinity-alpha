@echo off
setlocal

set "ROOT=%~dp0"
set "FRONTEND_DIR=%ROOT%frontend"

title MAARS Frontend
cd /d "%FRONTEND_DIR%"

echo.
echo ==========================================
echo             MAARS Frontend
echo ==========================================
echo.

if not exist "package.json" (
    echo [ERROR] package.json not found in "%FRONTEND_DIR%"
    echo.
    pause
    exit /b 1
)

where npm >nul 2>&1
if errorlevel 1 (
    echo [ERROR] npm was not found on PATH.
    echo Install Node.js and npm, then try again.
    echo.
    pause
    exit /b 1
)

if not exist "node_modules" (
    echo [SETUP] node_modules not found. Installing frontend dependencies...
    call npm install
    if errorlevel 1 (
        echo [ERROR] Failed to install frontend dependencies.
        echo.
        pause
        exit /b 1
    )
)

echo [RUN] Starting frontend on http://localhost:3000
echo.
call npm start

echo.
echo [INFO] Frontend process exited.
pause
