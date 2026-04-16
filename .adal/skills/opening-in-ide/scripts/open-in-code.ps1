#!/usr/bin/env pwsh
$script:IdeDisplayName = 'VS Code'
$script:UsageScriptName = 'open-in-code.ps1'
$script:IdeCommandDisplay = 'code, code.cmd'
$script:IdeCommandCandidates = @('code', 'code.cmd')

. "$PSScriptRoot/lib/VSCodeFamilyOpen.ps1"
Invoke-VSCodeFamilyOpen @args
