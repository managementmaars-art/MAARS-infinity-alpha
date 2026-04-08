# MAARS Command — Fully Automated New Device Setup
# One-liner to run on new device (in PowerShell as Administrator):
#   irm https://raw.githubusercontent.com/managementmaars-art/MAARS-infinity-alpha/main/new_device_setup.ps1 | iex

$ErrorActionPreference = "Stop"
$REPO_URL     = "https://github.com/managementmaars-art/MAARS-infinity-alpha.git"
$RELEASE_BASE = "https://github.com/managementmaars-art/MAARS-infinity-alpha/releases/download/migration-v1"
$PROJECT_DIR  = "$env:USERPROFILE\MAARS-Command"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  MAARS Command — Device Setup" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

function Step($msg) { Write-Host "`n>> $msg" -ForegroundColor Yellow }
function OK($msg)   { Write-Host "   OK: $msg" -ForegroundColor Green }
function Download($url, $dest) {
    Write-Host "   Downloading $(Split-Path $dest -Leaf)..." -ForegroundColor Gray
    Invoke-WebRequest -Uri $url -OutFile $dest -UseBasicParsing
}

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

# ── 4. MongoDB ────────────────────────────────────────────────────────────────
Step "Checking MongoDB"
$mongoSvc = Get-Service -Name MongoDB -ErrorAction SilentlyContinue
$mongoRunning = $mongoSvc -and $mongoSvc.Status -eq "Running"
if (-not $mongoRunning) {
    $mongoInstalled = Get-Command mongod -ErrorAction SilentlyContinue
    if (-not $mongoInstalled) {
        Write-Host "   Installing MongoDB..." -ForegroundColor Yellow
        winget install --id MongoDB.Server -e --source winget --silent
    }
    Start-Service MongoDB -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 3
}
OK "MongoDB ready"

# ── 5. Clone repo ─────────────────────────────────────────────────────────────
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

# ── 6. Credentials bundle ─────────────────────────────────────────────────────
Step "Installing credentials (.env files)"
$tmp = "$env:TEMP\maars_migration"
New-Item -ItemType Directory -Force -Path $tmp | Out-Null

$bundleZip = "$tmp\MAARS_MIGRATION_BUNDLE.zip"
Download "$RELEASE_BASE/MAARS_MIGRATION_BUNDLE.zip" $bundleZip
Expand-Archive -Path $bundleZip -DestinationPath "$tmp\bundle" -Force

$backendSrc  = "$tmp\bundle\backend\.env"
$frontendSrc = "$tmp\bundle\frontend\.env.local"
if (Test-Path $backendSrc)  { Copy-Item $backendSrc  "backend\.env" -Force; Copy-Item $backendSrc ".env" -Force }
if (Test-Path $frontendSrc) { Copy-Item $frontendSrc "frontend\.env.local" -Force }
OK "Credentials installed"

# ── 7. Restore MongoDB data ───────────────────────────────────────────────────
Step "Restoring MongoDB database"
$dbZip = "$tmp\MAARS_DB_EXPORT.zip"
Download "$RELEASE_BASE/MAARS_DB_EXPORT.zip" $dbZip
Expand-Archive -Path $dbZip -DestinationPath "$tmp\db" -Force

# Use Python (already confirmed available) to restore
$restoreScript = @"
import pymongo, json, os, sys

client = pymongo.MongoClient('mongodb://localhost:27017', serverSelectionTimeoutMS=5000)
export_root = sys.argv[1]

restored = 0
for db_name in os.listdir(export_root):
    db_path = os.path.join(export_root, db_name)
    if not os.path.isdir(db_path): continue
    db = client[db_name]
    for fname in os.listdir(db_path):
        if not fname.endswith('.json'): continue
        coll_name = fname[:-5]
        with open(os.path.join(db_path, fname)) as f:
            docs = json.load(f)
        if docs:
            db[coll_name].drop()
            db[coll_name].insert_many(docs)
            restored += len(docs)
            print(f'  restored {db_name}.{coll_name}: {len(docs)} docs')

print(f'Total restored: {restored} docs')
"@
$restoreScript | python - "$tmp\db\db_export"
OK "MongoDB data restored"

# ── 8. Restore uploads ────────────────────────────────────────────────────────
Step "Restoring uploads"
$uploadsZip = "$tmp\MAARS_UPLOADS.zip"
Download "$RELEASE_BASE/MAARS_UPLOADS.zip" $uploadsZip

New-Item -ItemType Directory -Force -Path "backend\uploads" | Out-Null
Expand-Archive -Path $uploadsZip -DestinationPath "." -Force
OK "Uploads restored"

# ── 9. Cleanup temp ───────────────────────────────────────────────────────────
Remove-Item $tmp -Recurse -Force -ErrorAction SilentlyContinue

# ── 10. Python dependencies ───────────────────────────────────────────────────
Step "Installing Python dependencies"
Set-Location "$PROJECT_DIR\backend"
python -m venv venv
.\venv\Scripts\pip install --upgrade pip --quiet
.\venv\Scripts\pip install -r requirements.txt --quiet
OK "Python dependencies installed"

# ── 11. Node.js dependencies ──────────────────────────────────────────────────
Step "Installing Node.js dependencies"
Set-Location "$PROJECT_DIR\frontend"
npm install --silent
OK "Node.js dependencies installed"

# ── 12. Start scripts ─────────────────────────────────────────────────────────
Step "Creating launch shortcuts"
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

$launch = Read-Host "Launch MAARS now? (Y/n)"
if ($launch -ne "n" -and $launch -ne "N") {
    Start-Process "$PROJECT_DIR\START_MAARS.bat"
}
