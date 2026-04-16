# get course script - GET /aia/api/v1/courses/{course_id}/script
# Returns script_url (AES encrypted), decrypts and downloads script content
param([Parameter(Mandatory=$true, Position=0)][string]$CourseId)
$scriptDir = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
if (-not $scriptDir) { $scriptDir = Split-Path -Parent $PSCommandPath }
. (Join-Path $scriptDir "_common.ps1")
if (-not (Load-Config)) { exit 1 }
$raw = Invoke-ApiGet "/aia/api/v1/courses/$CourseId/script"
$body = Parse-Response $raw
$json = $body | ConvertFrom-Json
$scriptUrlEnc = $json.data.script_url
if (-not $scriptUrlEnc) { $scriptUrlEnc = $json.script_url }
if (-not $scriptUrlEnc) {
    Write-Host "Error: no script_url in response" -ForegroundColor Red
    exit 1
}
$py = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $py) { $py = (Get-Command python3 -ErrorAction SilentlyContinue).Source }
$decryptScript = Join-Path $scriptDir "_decrypt_script_url.py"
if (-not (Test-Path $decryptScript)) {
    Write-Host "Error: _decrypt_script_url.py not found" -ForegroundColor Red
    exit 1
}
$decryptedUrl = $scriptUrlEnc | & $py $decryptScript 2>$null
if (-not $decryptedUrl) {
    Write-Host "Error: failed to decrypt script_url (pip install pycryptodome)" -ForegroundColor Red
    exit 1
}
$decryptedUrl = $decryptedUrl.ToString().Trim()
$headers = @{ "User-Agent" = "hd_skill/1.0" }
try {
    $r = Invoke-WebRequest -Uri $decryptedUrl -UseBasicParsing -Method Get -Headers $headers -MaximumRedirection 5
    Write-Output $r.Content
} catch {
    $curl = Get-Command curl.exe -ErrorAction SilentlyContinue
    if ($curl) {
        $content = & curl.exe -sS -L -A "hd_skill/1.0" -- "$decryptedUrl" 2>$null
        if ($LASTEXITCODE -eq 0 -and $content) { Write-Output $content; return }
    }
    Write-Host "Error: failed to download script from URL" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}
