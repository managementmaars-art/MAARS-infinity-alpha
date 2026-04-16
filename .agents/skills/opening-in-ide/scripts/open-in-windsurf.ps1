#!/usr/bin/env pwsh
$script:IdeDisplayName = 'Windsurf'
$script:UsageScriptName = 'open-in-windsurf.ps1'
$script:IdeCommandDisplay = 'windsurf, windsurf.cmd'
$script:IdeCommandCandidates = @('windsurf', 'windsurf.cmd')

. "$PSScriptRoot/lib/VSCodeFamilyOpen.ps1"
Invoke-VSCodeFamilyOpen @args
