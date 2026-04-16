# search courses by keyword - GET /aia/api/v1/courses/search?keyword=xxx
param([Parameter(Mandatory=$true, Position=0)][string]$Keyword)
$scriptDir = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
if (-not $scriptDir) { $scriptDir = Split-Path -Parent $PSCommandPath }
. (Join-Path $scriptDir "_common.ps1")
if (-not (Load-Config)) { exit 1 }
$encoded = Get-UrlEncode $Keyword
$raw = Invoke-ApiGet "/aia/api/v1/courses/search?keyword=$encoded"
Parse-Response $raw
# 埋点放成功后，避免先于搜课且失败时干扰排错
Invoke-CollectIntent "关键字搜课：$Keyword" "skill_search_keyword" "关键字搜课" ""
