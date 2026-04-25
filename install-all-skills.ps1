$sourceFile = "C:\Users\Yaleena Yara\Desktop\skills-export\skills-top-9788.txt"
$successFile = ".\skills-installed-success.txt"
$failedFile  = ".\skills-installed-failed.txt"

if (!(Test-Path $sourceFile)) {
    Write-Error "Source file not found: $sourceFile"
    exit 1
}

$success = New-Object System.Collections.Generic.List[string]
$failed  = New-Object System.Collections.Generic.List[string]

Get-Content $sourceFile | ForEach-Object {
    $cmd = $_.Trim()
    if ([string]::IsNullOrWhiteSpace($cmd)) { return }

    Write-Host "Running: $cmd"
    Invoke-Expression $cmd

    if ($LASTEXITCODE -eq 0) {
        $success.Add($cmd)
    } else {
        $failed.Add($cmd)
    }
}

$success | Set-Content $successFile
$failed  | Set-Content $failedFile

Write-Host ""
Write-Host "Done."
Write-Host "Successful: $($success.Count)"
Write-Host "Failed: $($failed.Count)"
