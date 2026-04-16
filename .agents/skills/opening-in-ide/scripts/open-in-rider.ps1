#!/usr/bin/env pwsh
$script:IdeDisplayName = 'Rider'
$script:UsageScriptName = 'open-in-rider.ps1'
$script:IdeCommandDisplay = 'rider, rider.bat, rider64.exe'
$script:IdeCommandCandidates = @('rider', 'rider.bat', 'rider64.exe')
$script:ContextMode = 'rider'

. "$PSScriptRoot/lib/JetBrainsOpen.ps1"
Invoke-JetBrainsOpen @args
