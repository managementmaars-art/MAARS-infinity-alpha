# MAARS Command — Fully Automated New Device Setup
# One-liner to run on new device:
#   irm https://raw.githubusercontent.com/managementmaars-art/MAARS-infinity-alpha/main/new_device_setup.ps1 | iex

$ErrorActionPreference = "Stop"
$REPO_URL  = "https://github.com/managementmaars-art/MAARS-infinity-alpha.git"
$BUNDLE_URL = "https://github.com/managementmaars-art/MAARS-infinity-alpha/releases/download/migration-v1/MAARS_MIGRATION_BUNDLE.zip"
$PROJECT_DIR = "$env:USERPROFILE\MAARS-Command"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  MAARS Command — Device Setup" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

function Step($msg) { Write-Host "`n>> $msg" -ForegroundColor Yellow }
function OK($msg)   { Write-Host "   OK: $msg" -ForegroundColor Green }

# ── 1. Git ────────────────────────────────────────────────────────────────────
Step "Checking Git"
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    winget install --id Git.Git -e --source winget --silent
    $env:PATH += ";C:\Program Files\Git\cmd"
}
OK "Git: $(git --version)"

# ── 2. Python ─────────────────────────────────────────────────────────────────
Step "Checking Python"
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    winget install --id Python.Python.3.11 -e --source winget --silent
    $env:PATH += ";$env:LOCALAPPDATA\Programs\Python\Python311;$env:LOCALAPPDATA\Programs\Python\Python311\Scripts"
}
OK "Python: $(python --version)"

# ── 3. Node.js ────────────────────────────────────────────────────────────────
Step "Checking Node.js"
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    winget install --id OpenJS.NodeJS.LTS -e --source winget --silent
    $env:PATH += ";C:\Program Files\nodejs"
}
OK "Node.js: $(node --version)"

# ── 4. Clone repo ─────────────────────────────────────────────────────────────
Step "Cloning repository"
if (Test-Path $PROJECT_DIR) {
    Write-Host "   Pulling latest..." -ForegroundColor Yellow
    Set-Location $PROJECT_DIR
    git pull origin main
} else {
    git clone $REPO_URL $PROJECT_DIR
    Set-Location $PROJECT_DIR
}
git config user.email "management.maars@marsgc.net"
git config user.name "managementmaars-art"
OK "Repository ready at $PROJECT_DIR"

# ── 5. Download credentials bundle ────────────────────────────────────────────
Step "Downloading credentials bundle"
$bundlePath = "$env:TEMP\MAARS_MIGRATION_BUNDLE.zip"
$extractPath = "$env:TEMP\maars_bundle"

Write-Host "   Fetching from GitHub release..." -ForegroundColor Yellow
Invoke-WebRequest -Uri $BUNDLE_URL -OutFile $bundlePath -UseBasicParsing

if (Test-Path $extractPath) { Remove-Item $extractPath -Recurse -Force }
Expand-Archive -Path $bundlePath -DestinationPath $extractPath -Force

# Copy .env files into the project
$backendEnvSrc = Join-Path $extractPath "backend\.env"
$frontendEnvSrc = Join-Path $extractPath "frontend\.env.local"

if (Test-Path $backendEnvSrc) {
    Copy-Item $backendEnvSrc "backend\.env" -Force
    Copy-Item $backendEnvSrc ".env" -Force
    OK "backend/.env installed"
} else {
    Write-Host "   WARNING: backend/.env not found in bundle — you may need to create it manually." -ForegroundColor Red
}

if (Test-Path $frontendEnvSrc) {
    Copy-Item $frontendEnvSrc "frontend\.env.local" -Force
    OK "frontend/.env.local installed"
}

# Cleanup
Remove-Item $bundlePath -Force -ErrorAction SilentlyContinue
Remove-Item $extractPath -Recurse -Force -ErrorAction SilentlyContinue

# ── 6. Python virtual env + deps ─────────────────────────────────────────────
Step "Installing Python dependencies"
Set-Location "$PROJECT_DIR\backend"
python -m venv venv
.\venv\Scripts\pip install --upgrade pip --quiet
.\venv\Scripts\pip install -r requirements.txt --quiet
OK "Python dependencies installed"

# ── 7. Node.js deps ───────────────────────────────────────────────────────────
Step "Installing Node.js dependencies"
Set-Location "$PROJECT_DIR\frontend"
npm install --silent
OK "Node.js dependencies installed"

# ── 8. Start scripts ──────────────────────────────────────────────────────────
Step "Creating start scripts"
Set-Location $PROJECT_DIR

@"
@echo off
cd /d "%~dp0backend"
call venv\Scripts\activate
start "MAARS Backend" cmd /k "uvicorn server:app --reload --port 8000"
"@ | Out-File "start_backend.bat" -Encoding ascii

@"
@echo off
cd /d "%~dp0frontend"
start "MAARS Frontend" cmd /k "npm start"
"@ | Out-File "start_frontend.bat" -Encoding ascii

@"
@echo off
echo Starting MAARS Command...
start "" "%~dp0start_backend.bat"
timeout /t 3 /nobreak >nul
start "" "%~dp0start_frontend.bat"
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo API Docs: http://localhost:8000/docs
echo.
pause
"@ | Out-File "START_MAARS.bat" -Encoding ascii

OK "START_MAARS.bat ready"

# ── Done ──────────────────────────────────────────────────────────────────────
Write-Host "`n========================================" -ForegroundColor Green
Write-Host "  Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Project:  $PROJECT_DIR"
Write-Host "  Start:    Double-click START_MAARS.bat"
Write-Host "  Backend:  http://localhost:8000"
Write-Host "  Frontend: http://localhost:3000"
Write-Host "  API Docs: http://localhost:8000/docs"
Write-Host ""
Write-Host "  Ensure MongoDB is running before starting." -ForegroundColor Yellow
Write-Host ""

$launch = Read-Host "Launch MAARS now? (Y/n)"
if ($launch -ne "n" -and $launch -ne "N") {
    Start-Process "$PROJECT_DIR\START_MAARS.bat"
}
