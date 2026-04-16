#!/usr/bin/env pwsh
$script:IdeDisplayName = 'Cursor'
$script:UsageScriptName = 'open-in-cursor.ps1'
$script:IdeCommandDisplay = 'cursor, cursor.cmd'
$script:IdeCommandCandidates = @('cursor', 'cursor.cmd')

. "$PSScriptRoot/lib/VSCodeFamilyOpen.ps1"
Invoke-VSCodeFamilyOpen @args
