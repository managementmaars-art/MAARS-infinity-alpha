$sourceFile = "C:\Users\Yaleena Yara\Desktop\skills-export\skills-top-9788.txt"
$successFile = ".\skills-installed-success.txt"
$failedFile  = ".\skills-installed-failed.txt"

if (!(Test-Path $sourceFile)) {
    Write-Error "Source file not found: $sourceFile"
    exit 1
}

$wshell = New-Object -ComObject WScript.Shell
$success = New-Object System.Collections.Generic.List[string]
$failed  = New-Object System.Collections.Generic.List[string]

# 8 visible + "23 more" = 31 additional agents
$additionalAgentsCount = 31

function Wait-ForWindow($titlePart, $timeoutSeconds = 25) {
    $sw = [Diagnostics.Stopwatch]::StartNew()
    while ($sw.Elapsed.TotalSeconds -lt $timeoutSeconds) {
        if ($wshell.AppActivate($titlePart)) {
            Start-Sleep -Milliseconds 500
            return $true
        }
        Start-Sleep -Milliseconds 300
    }
    return $false
}

function Send-Key($key, $delay = 180) {
    $wshell.SendKeys($key)
    Start-Sleep -Milliseconds $delay
}

function Toggle-AllAdditionalAgents {
    param([int]$Count)

    # Pass 1: flip every additional agent once
    for ($i = 0; $i -lt $Count; $i++) {
        Send-Key " "
        if ($i -lt ($Count - 1)) {
            Send-Key "{DOWN}"
        }
    }

    # Return to the top of the additional-agents list
    for ($i = 0; $i -lt ($Count - 1); $i++) {
        Send-Key "{UP}" 80
    }

    Start-Sleep -Milliseconds 300

    # Pass 2: flip every additional agent again
    # Result: everything ends selected
    for ($i = 0; $i -lt $Count; $i++) {
        Send-Key " "
        if ($i -lt ($Count - 1)) {
            Send-Key "{DOWN}"
        }
    }

    # Move back to top just to keep navigation stable
    for ($i = 0; $i -lt ($Count - 1); $i++) {
        Send-Key "{UP}" 80
    }
}

function Install-OneSkill($cmd) {
    Write-Host "Running: $cmd"

    $wrapped = @"
Set-Location '$PWD'
$cmd
"@

    $proc = Start-Process powershell -ArgumentList @(
        '-NoExit',
        '-ExecutionPolicy', 'Bypass',
        '-Command', $wrapped
    ) -PassThru

    if (-not (Wait-ForWindow "Windows PowerShell" 30)) {
        Write-Warning "Could not activate installer window."
        try { $proc.Kill() } catch {}
        return $false
    }

    Start-Sleep -Seconds 3

    # Universal stays included automatically.
    # Normalize Additional Agents to all selected.
    Toggle-AllAdditionalAgents -Count $additionalAgentsCount

    # Confirm agent selection
    Send-Key "{ENTER}" 700

    # Installation scope: Project
    Send-Key "{ENTER}" 700

    # Installation method: Symlink
    Send-Key "{ENTER}" 700

    # Proceed: Yes
    Send-Key "{ENTER}" 700

    $proc.WaitForExit()
    return ($proc.ExitCode -eq 0)
}

foreach ($raw in Get-Content $sourceFile) {
    $cmd = $raw.Trim()
    if ([string]::IsNullOrWhiteSpace($cmd)) { continue }

    $ok = Install-OneSkill $cmd

    if ($ok) {
        $success.Add($cmd)
    } else {
        $failed.Add($cmd)
    }

    Start-Sleep -Milliseconds 500
}

$success | Set-Content $successFile
$failed  | Set-Content $failedFile

Write-Host ""
Write-Host "Done."
Write-Host "Successful: $($success.Count)"
Write-Host "Failed:     $($failed.Count)"
