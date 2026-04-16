#!/usr/bin/env pwsh
$script:IdeDisplayName = 'WebStorm'
$script:UsageScriptName = 'open-in-webstorm.ps1'
$script:IdeCommandDisplay = 'webstorm, webstorm.bat, webstorm64.exe'
$script:IdeCommandCandidates = @('webstorm', 'webstorm.bat', 'webstorm64.exe')
$script:ContextMode = 'webstorm'

. "$PSScriptRoot/lib/JetBrainsOpen.ps1"
Invoke-JetBrainsOpen @args
