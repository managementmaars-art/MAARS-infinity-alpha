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
# Find real python.exe — search common install locations, ignore Windows Store alias
$pythonExe = $null
$pythonSearchPaths = @(
    "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python310\python.exe",
    "C:\Python312\python.exe",
    "C:\Python311\python.exe",
    "C:\Python310\python.exe",
    "C:\Program Files\Python312\python.exe",
    "C:\Program Files\Python311\python.exe"
)
foreach ($p in $pythonSearchPaths) {
    if (Test-Path $p) { $pythonExe = $p; break }
}
# Also try py launcher
if (-not $pythonExe -and (Get-Command py -ErrorAction SilentlyContinue)) {
    $pythonExe = (py -c "import sys; print(sys.executable)" 2>$null)
}
if (-not $pythonExe) {
    Write-Host "   Installing Python 3.11 via winget..." -ForegroundColor Yellow
    winget install --id Python.Python.3.11 -e --source winget --accept-package-agreements --accept-source-agreements
    # Refresh PATH from registry
    $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH","User")
    foreach ($p in $pythonSearchPaths) {
        if (Test-Path $p) { $pythonExe = $p; break }
    }
}
if (-not $pythonExe) { Write-Host "ERROR: Python not found after install. Please install manually from python.org" -ForegroundColor Red; exit 1 }
OK "Python: $($pythonExe) -- $( & $pythonExe --version)"
Set-Alias -Name python -Value $pythonExe -Scope Script

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
if (Test-Path "$PROJECT_DIR\.git") {
    Write-Host "   Repo exists — force-syncing to origin/main..." -ForegroundColor Yellow
    Set-Location $PROJECT_DIR
    git fetch origin
    git reset --hard origin/main
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
$vscodeSrc = "$tmp\bundle\.vscode\settings.json"
if (Test-Path $vscodeSrc) {
    New-Item -ItemType Directory -Force -Path ".vscode" | Out-Null
    Copy-Item $vscodeSrc ".vscode\settings.json" -Force
}
OK "Credentials + VS Code settings installed"

# ── 7. Restore uploads (no Python needed) ────────────────────────────────────
Step "Restoring uploads"
$uploadsZip = "$tmp\MAARS_UPLOADS.zip"
Download "$RELEASE_BASE/MAARS_UPLOADS.zip" $uploadsZip
New-Item -ItemType Directory -Force -Path "backend\uploads" | Out-Null
Expand-Archive -Path $uploadsZip -DestinationPath "." -Force
OK "Uploads restored"

# ── 8. Python venv + dependencies (installs pymongo) ─────────────────────────
Step "Installing Python dependencies"
Set-Location "$PROJECT_DIR\backend"
& $pythonExe -m venv venv
& ".\venv\Scripts\python.exe" -m pip install --upgrade pip --quiet
& ".\venv\Scripts\python.exe" -m pip install -r requirements.txt --quiet
OK "Python dependencies installed"

# ── 9. Restore MongoDB data (now pymongo is available in venv) ────────────────
Step "Restoring MongoDB database"
$venvPython = "$PROJECT_DIR\backend\venv\Scripts\python.exe"
$dbZip = "$tmp\MAARS_DB_EXPORT.zip"
Download "$RELEASE_BASE/MAARS_DB_EXPORT.zip" $dbZip
Expand-Archive -Path $dbZip -DestinationPath "$tmp\db" -Force

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
            print('  restored ' + db_name + '.' + coll_name + ': ' + str(len(docs)) + ' docs')

print('Total restored: ' + str(restored) + ' docs')
"@
$restoreScript | & $venvPython - "$tmp\db\db_export"
OK "MongoDB data restored"

# ── 10. Restore .claude (skills + settings) ──────────────────────────────────
Step "Restoring Claude skills and settings"
$claudeZip = "$tmp\MAARS_CLAUDE_PROJECT.zip"
Download "$RELEASE_BASE/MAARS_CLAUDE_PROJECT.zip" $claudeZip
Expand-Archive -Path $claudeZip -DestinationPath $PROJECT_DIR -Force
OK "Project .claude restored (skills + settings)"

# Restore global Claude memory (~/.claude)
$claudeGlobalZip = "$tmp\MAARS_CLAUDE_GLOBAL.zip"
Download "$RELEASE_BASE/MAARS_CLAUDE_GLOBAL.zip" $claudeGlobalZip
Expand-Archive -Path $claudeGlobalZip -DestinationPath "$env:TEMP\maars_claude_global" -Force

$globalSrc = "$env:TEMP\maars_claude_global\claude_global"
$globalDest = "$env:USERPROFILE\.claude"
New-Item -ItemType Directory -Force -Path "$globalDest\projects\c--Users-$($env:USERNAME)-MAARS-Command\memory" | Out-Null

if (Test-Path "$globalSrc\settings.json") {
    Copy-Item "$globalSrc\settings.json" "$globalDest\settings.json" -Force
}
if (Test-Path "$globalSrc\memory") {
    Copy-Item "$globalSrc\memory\*" "$globalDest\projects\c--Users-$($env:USERNAME)-MAARS-Command\memory\" -Force
}
Remove-Item "$env:TEMP\maars_claude_global" -Recurse -Force -ErrorAction SilentlyContinue
OK "Global Claude memory restored"

# ── 11. Restore AI tools (Claude credentials, Cline, Codex) ──────────────────
Step "Restoring AI tool credentials (Claude, Cline, Codex)"
$aiToolsZip = "$tmp\MAARS_AI_TOOLS.zip"
Download "$RELEASE_BASE/MAARS_AI_TOOLS.zip" $aiToolsZip
Expand-Archive -Path $aiToolsZip -DestinationPath "$tmp\ai_tools" -Force
$at = "$tmp\ai_tools"

# Claude Code credentials + global settings
$claudeDest = "$env:USERPROFILE\.claude"
New-Item -ItemType Directory -Force -Path $claudeDest | Out-Null
if (Test-Path "$at\claude\.credentials.json") {
    Copy-Item "$at\claude\.credentials.json" "$claudeDest\.credentials.json" -Force
}
if (Test-Path "$at\claude\settings.json") {
    Copy-Item "$at\claude\settings.json" "$claudeDest\settings.json" -Force
}
if (Test-Path "$at\.claude.json") {
    Copy-Item "$at\.claude.json" "$env:USERPROFILE\.claude.json" -Force
}

# Cline
$clineDest = "$env:USERPROFILE\.cline\data"
New-Item -ItemType Directory -Force -Path $clineDest | Out-Null
if (Test-Path "$at\cline\data\secrets.json")     { Copy-Item "$at\cline\data\secrets.json"     "$clineDest\secrets.json"     -Force }
if (Test-Path "$at\cline\data\globalState.json") { Copy-Item "$at\cline\data\globalState.json" "$clineDest\globalState.json" -Force }

# Codex
$codexDest = "$env:USERPROFILE\.codex"
New-Item -ItemType Directory -Force -Path "$codexDest\skills" | Out-Null
if (Test-Path "$at\codex\auth.json")   { Copy-Item "$at\codex\auth.json"   "$codexDest\auth.json"   -Force }
if (Test-Path "$at\codex\config.toml") { Copy-Item "$at\codex\config.toml" "$codexDest\config.toml" -Force }
if (Test-Path "$at\codex\skills") {
    Copy-Item "$at\codex\skills\*" "$codexDest\skills\" -Recurse -Force
}

OK "AI tool credentials restored (Claude Code, Cline, Codex)"

# ── 12. Restore screen recording ─────────────────────────────────────────────
Step "Restoring screen recording"
$recZip = "$tmp\MAARS_SCREEN_RECORDING.zip"
Download "$RELEASE_BASE/MAARS_SCREEN_RECORDING.zip" $recZip
$recDest = "$env:USERPROFILE\Videos\Screen Recordings"
New-Item -ItemType Directory -Force -Path $recDest | Out-Null
Expand-Archive -Path $recZip -DestinationPath $recDest -Force
OK "Screen recording restored to Videos\Screen Recordings"

# ── 13. Cleanup temp ──────────────────────────────────────────────────────────
Remove-Item $tmp -Recurse -Force -ErrorAction SilentlyContinue

# ── 14. Node.js dependencies ──────────────────────────────────────────────────
Step "Installing Node.js dependencies"
Set-Location "$PROJECT_DIR\frontend"
npm install --silent
OK "Node.js dependencies installed"

# ── 15. Start scripts ─────────────────────────────────────────────────────────
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
