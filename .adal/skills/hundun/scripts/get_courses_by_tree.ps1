# get courses by tree - GET /aia/api/v1/courses/by-tree/{treeId}
param([Parameter(Mandatory=$true, Position=0)][string]$TreeId)
$scriptDir = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
if (-not $scriptDir) { $scriptDir = Split-Path -Parent $PSCommandPath }
. (Join-Path $scriptDir "_common.ps1")
if (-not (Load-Config)) { exit 1 }
Invoke-CollectIntent "search_by_tree:treeId=$TreeId" "skill_search_tree" "tree_search" ""
$raw = Invoke-ApiGet "/aia/api/v1/courses/by-tree/$TreeId"
Parse-Response $raw
