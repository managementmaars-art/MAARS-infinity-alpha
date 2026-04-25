$log = "C:\Users\Yaleena Yara\MAARS-Command\skills-progress.log"
$json = "C:\Users\Yaleena Yara\MAARS-Command\skills-progress.json"

if (!(Test-Path $log)) {
    New-Item -ItemType File -Path $log | Out-Null
}

if (!(Test-Path $json)) {
@'
{
  "totalCommands": 0,
  "currentCommandIndex": 0,
  "installedCommands": 0,
  "failedCommands": 0,
  "remainingCommands": 0,
  "installedSkills": 0,
  "failedSkills": 0,
  "currentCommand": "",
  "currentRepoSkillCount": 0
}
'@ | Set-Content $json
}

Start-Process powershell -ArgumentList @(
    "-NoLogo",
    "-NoExit",
    "-Command",
    @"
`$Host.UI.RawUI.WindowTitle = 'Skills Install Log'
Get-Content '$log' -Wait
"@
)

Start-Process powershell -ArgumentList @(
    "-NoLogo",
    "-NoExit",
    "-Command",
    @"
`$Host.UI.RawUI.WindowTitle = 'Skills Install Counters'
while (`$true) {
    Clear-Host

    if (Test-Path '$json') {
        try {
            `$data = Get-Content '$json' -Raw | ConvertFrom-Json

            Write-Host 'MAARS COMMAND Skills Install Status' -ForegroundColor Cyan
            Write-Host '=====================' -ForegroundColor Cyan
            Write-Host ''

            Write-Host ('Total Commands     : ' + `$data.totalCommands)
            Write-Host ('Current Index      : ' + `$data.currentCommandIndex)
            Write-Host ('Installed Commands : ' + `$data.installedCommands) -ForegroundColor Green
            Write-Host ('Failed Commands    : ' + `$data.failedCommands) -ForegroundColor Red
            Write-Host ('Remaining Commands : ' + `$data.remainingCommands) -ForegroundColor Yellow
            Write-Host ''
            Write-Host ('Installed Skills   : ' + `$data.installedSkills) -ForegroundColor Green
            Write-Host ('Failed Skills      : ' + `$data.failedSkills) -ForegroundColor Red
            Write-Host ('Repo Skill Count   : ' + `$data.currentRepoSkillCount)
            Write-Host ''
            Write-Host 'Current Command:' -ForegroundColor Cyan
            Write-Host `$data.currentCommand
            Write-Host ''
            Write-Host ('Last Refresh       : ' + (Get-Date))
        }
        catch {
            Write-Host 'Waiting for valid progress JSON...' -ForegroundColor Yellow
        }
    }
    else {
        Write-Host 'Waiting for progress file...' -ForegroundColor Yellow
    }

    Start-Sleep 2
}
"@
)