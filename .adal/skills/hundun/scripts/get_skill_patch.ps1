# GET /aia/api/v1/skill/patch?skill_id=&module_key=[&version=]
# Omit version to fetch current active patch (patch_status=current).
param(
    [Parameter(Position = 0)]
    [string]$ModuleKey = 'core',
    [Parameter(Position = 1)]
    [string]$Version = '',
    [Parameter(Position = 2)]
    [string]$SkillId = 'hd_skill'
)
$scriptDir = if ($PSScriptRoot) { $PSScriptRoot } elseif ($MyInvocation.MyCommand.Path) { Split-Path -Parent $MyInvocation.MyCommand.Path } else { Split-Path -Parent $PSCommandPath }
if (-not $scriptDir) { Write-Host 'Cannot resolve script directory.' -ForegroundColor Red; exit 1 }
. (Join-Path $scriptDir '_common.ps1')
if (-not (Load-Config)) { exit 1 }
$path = "/aia/api/v1/skill/patch?skill_id=$([System.Uri]::EscapeDataString($SkillId))&module_key=$([System.Uri]::EscapeDataString($ModuleKey))"
if ($Version) { $path += "&version=$([System.Uri]::EscapeDataString($Version))" }
$raw = Invoke-ApiGet $path
Parse-Response $raw
