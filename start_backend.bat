@echo off
setlocal

set "ROOT=%~dp0"
set "BACKEND_DIR=%ROOT%backend"
set "VENV_DIR=%BACKEND_DIR%\venv"
set "VENV_PYTHON=%VENV_DIR%\Scripts\python.exe"

title MAARS Backend
cd /d "%BACKEND_DIR%"

echo.
echo ==========================================
echo             MAARS Backend
echo ==========================================
echo.

if not exist "server.py" (
    echo [ERROR] server.py not found in "%BACKEND_DIR%"
    echo.
    pause
    exit /b 1
)

set "PYTHON_BOOTSTRAP="
where py >nul 2>&1
if %errorlevel%==0 set "PYTHON_BOOTSTRAP=py -3"
if not defined PYTHON_BOOTSTRAP (
    where python >nul 2>&1
    if %errorlevel%==0 set "PYTHON_BOOTSTRAP=python"
)

if not defined PYTHON_BOOTSTRAP (
    echo [ERROR] Python was not found on PATH.
    echo Install Python 3 and try again.
    echo.
    pause
    exit /b 1
)

if not exist "%VENV_PYTHON%" (
    echo [SETUP] Creating backend virtual environment...
    call %PYTHON_BOOTSTRAP% -m venv "%VENV_DIR%"
    if errorlevel 1 (
        echo [ERROR] Failed to create backend virtual environment.
        echo.
        pause
        exit /b 1
    )
)

echo [SETUP] Verifying backend dependencies...
"%VENV_PYTHON%" -c "import fastapi, uvicorn" >nul 2>&1
if errorlevel 1 (
    echo [SETUP] Installing backend dependencies...
    "%VENV_PYTHON%" -m pip install --upgrade pip
    if errorlevel 1 (
        echo [ERROR] Failed to upgrade pip in backend virtual environment.
        echo.
        pause
        exit /b 1
    )
    "%VENV_PYTHON%" -m pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Failed to install backend requirements.
        echo.
        pause
        exit /b 1
    )
)

if not exist "%ROOT%.env" if not exist ".env" (
    echo [WARN] No .env file was found in the project root or backend folder.
    echo The server may start, but database and integration features may not work until env vars are configured.
    echo.
)

echo [RUN] Starting FastAPI on http://0.0.0.0:8000  (all interfaces)
echo.
"%VENV_PYTHON%" -m uvicorn server:app --reload --host 0.0.0.0 --port 8000

echo.
echo [INFO] Backend process exited.
pause
