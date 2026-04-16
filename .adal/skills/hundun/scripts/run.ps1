# hd_skill Windows entry: run .ps1 first, fallback to .sh + Git Bash
# Usage: .\scripts\run.ps1 <script_name> [args...]
# Example: .\scripts\run.ps1 search_courses "keyword"

param(
    [Parameter(Mandatory=$true, Position=0)]
    [string]$ScriptName,
    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]]$ScriptArgs
)

$ErrorActionPreference = "Stop"
$ScriptDir = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
if (-not $ScriptDir) { Write-Host "Cannot get script dir. Run scripts\\run.ps1 from the skill folder." -ForegroundColor Red; exit 1 }
$SkillDir = Split-Path -Parent $ScriptDir
if (-not $SkillDir) { Write-Host "Cannot get skill dir from scripts\\run.ps1." -ForegroundColor Red; exit 1 }
$scriptPath = Join-Path $ScriptDir "$ScriptName.ps1"
$shPath = Join-Path $ScriptDir "$ScriptName.sh"

# Prefer .ps1 (native, no Git Bash)
if (Test-Path $scriptPath) {
    & $scriptPath @ScriptArgs
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    return
}

# Fallback: .sh + Git Bash
$ConfigPath = Join-Path $env:USERPROFILE ".hdxy_skill_run.conf"
function Get-Config {
    if (Test-Path $ConfigPath) {
        $cfg = @{}
        Get-Content $ConfigPath -ErrorAction SilentlyContinue | ForEach-Object {
            if ($_ -match '^([^#=]+)=(.*)$') { $cfg[$matches[1].Trim()] = $matches[2].Trim() }
        }
        return $cfg
    }
    return @{}
}
function Find-Bash {
    $cfg = Get-Config
    if ($cfg["bash_path"] -and (Test-Path $cfg["bash_path"])) { return $cfg["bash_path"] }
    $b = Get-Command bash -ErrorAction SilentlyContinue
    if ($b) { return $b.Source }
    $paths = @("C:\Program Files\Git\bin\bash.exe", "C:\Program Files\Git\usr\bin\bash.exe")
    foreach ($p in $paths) { if (Test-Path $p) { return $p } }
    return $null
}

if (-not (Test-Path $shPath)) {
    Write-Host "Script not found: $ScriptName" -ForegroundColor Red
    exit 1
}

$bashPath = Find-Bash
if (-not $bashPath) {
    Write-Host "Git Bash not found. Install: https://git-scm.com/download/win" -ForegroundColor Red
    Write-Host "Or use .ps1 scripts directly." -ForegroundColor Yellow
    exit 1
}

$config = Get-Config
$config["bash_path"] = $bashPath
$config["skill_dir"] = $SkillDir
($config.GetEnumerator() | ForEach-Object { "$($_.Key)=$($_.Value)" }) -join "`n" | Set-Content $ConfigPath -Encoding UTF8

# Convert to Git Bash path: C:\ -> /c/
if ($SkillDir -match '^([A-Za-z]):') {
    $drive = $Matches[1].ToLowerInvariant()
    $rest = $SkillDir.Substring(2) -replace '\\', '/'
    $skillDirUnix = "/$drive/$rest"
} else {
    $skillDirUnix = $SkillDir -replace '\\', '/'
}
function Escape-BashArg($a) { return "'" + ($a -replace "'", "'\''") + "'" }
$argStr = if ($ScriptArgs) { ($ScriptArgs | ForEach-Object { Escape-BashArg $_ }) -join " " } else { "" }
$cmd = "cd '$skillDirUnix' && ./scripts/$ScriptName.sh $argStr"
$bashArgs = @('-c', $cmd)
& $bashPath @bashArgs
