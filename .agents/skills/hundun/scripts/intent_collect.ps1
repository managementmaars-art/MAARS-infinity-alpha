# intent collect - POST /aia/api/v1/intent/collect
param(
    [Parameter(Mandatory=$true, Position=0)][string]$IntentDesc,
    [Parameter(Position=1)][string]$SceneDesc = "",
    [Parameter(Position=2)][string]$SceneValue = "",
    [Parameter(Position=3)][string]$ExtraRelatedContent = ""
)
$scriptDir = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
if (-not $scriptDir) { $scriptDir = Split-Path -Parent $PSCommandPath }
. (Join-Path $scriptDir "_common.ps1")
if (-not (Load-Config)) { exit 1 }
$body = @{ intent_desc = $IntentDesc; scene_desc = $SceneDesc; scene_value = $SceneValue; extra_related_content = $ExtraRelatedContent } | ConvertTo-Json
$raw = Invoke-ApiPost "/aia/api/v1/intent/collect" $body
Parse-Response $raw
