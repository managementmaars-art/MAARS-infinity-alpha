# course trees - GET /aia/api/v1/courses/trees
$scriptDir = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
if (-not $scriptDir) { $scriptDir = Split-Path -Parent $PSCommandPath }
. (Join-Path $scriptDir "_common.ps1")
if (-not (Load-Config)) { exit 1 }
Invoke-CollectIntent "get_course_trees" "skill_search_tree" "tree_search" ""
$raw = Invoke-ApiGet "/aia/api/v1/courses/trees"
Parse-Response $raw
