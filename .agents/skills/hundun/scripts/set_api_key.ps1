# write api_key to local config
param([Parameter(Mandatory=$true, Position=0)][string]$ApiKey)
if ($ApiKey -notmatch '^hd_sk_') {
    Write-Host "Usage: api_key must start with hd_sk_" -ForegroundColor Red
    exit 1
}
$configPath = if ($env:HDXY_CONFIG) { $env:HDXY_CONFIG } else { Join-Path $env:USERPROFILE ".hdxy_config" }
$dir = Split-Path $configPath
if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
@"
# hd_skill config
api_key=$ApiKey
base_url=https://hddrapi.hundun.cn
"@ | Set-Content -Path $configPath -Encoding UTF8
Write-Host "Configured. Ready to use."
