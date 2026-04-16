param(
  [Parameter(Mandatory = $true)]
  [string]$TargetProjectRoot,

  [string]$TargetRuntimeDir = 'assets/scripts/webui'
)

$ErrorActionPreference = 'Stop'

$skillRoot = Split-Path -Parent $PSScriptRoot
$runtimeSource = Join-Path $skillRoot 'assets/webui-runtime'
$runtimeTarget = Join-Path $TargetProjectRoot $TargetRuntimeDir

if (-not (Test-Path $runtimeSource)) {
  throw "Runtime source not found: $runtimeSource"
}

New-Item -ItemType Directory -Force -Path $runtimeTarget | Out-Null
Copy-Item (Join-Path $runtimeSource '*') $runtimeTarget -Recurse -Force

Write-Output "Installed WebUI runtime to: $runtimeTarget"
