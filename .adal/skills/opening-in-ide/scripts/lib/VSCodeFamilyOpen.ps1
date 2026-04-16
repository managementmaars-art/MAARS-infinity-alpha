Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Fail {
    param(
        [Parameter(Mandatory = $true)][string]$Message,
        [Parameter(Mandatory = $false)][int]$Code = 2
    )

    [Console]::Error.WriteLine($Message)
    exit $Code
}

function Show-VSCodeFamilyUsage {
    @"
Usage: $script:UsageScriptName [path] [--line N]

Open a file or folder in $script:IdeDisplayName.
If possible, open it within the nearest .code-workspace, .sln directory, or .csproj directory context.

Arguments:
  path         File or directory to open (default: .)
  --line, -l   Line number when opening a file
  --help, -h   Show this help
"@
}

function Get-BestMatch {
    param(
        [Parameter(Mandatory = $true)][string]$DirectoryName,
        [Parameter(Mandatory = $true)][string[]]$Candidates
    )

    foreach ($candidate in $Candidates) {
        $base = [System.IO.Path]::GetFileNameWithoutExtension($candidate)
        if ($base -eq $DirectoryName) {
            return $candidate
        }
    }

    return ($Candidates | Sort-Object | Select-Object -First 1)
}

function Find-NearestMatch {
    param(
        [Parameter(Mandatory = $true)][string]$StartDirectory,
        [Parameter(Mandatory = $true)][ValidateSet('code-workspace', 'sln', 'csproj')][string]$Extension
    )

    $dir = (Resolve-Path -LiteralPath $StartDirectory).Path
    while ($true) {
        $matches = @(Get-ChildItem -LiteralPath $dir -Filter "*.$Extension" -File -ErrorAction SilentlyContinue | Select-Object -ExpandProperty FullName)
        if ($matches.Count -gt 0) {
            $dirName = Split-Path -Leaf $dir
            return Get-BestMatch -DirectoryName $dirName -Candidates $matches
        }

        $parent = [System.IO.Directory]::GetParent($dir)
        if ($null -eq $parent) {
            break
        }
        $dir = $parent.FullName
    }

    return $null
}

function Get-VSCodeFamilyCommand {
    foreach ($candidate in $script:IdeCommandCandidates) {
        if (Get-Command $candidate -ErrorAction SilentlyContinue) {
            return $candidate
        }
    }

    return $null
}

function Start-VSCodeFamilyDetached {
    param(
        [Parameter(Mandatory = $true)][string]$FilePath,
        [Parameter(Mandatory = $true)][string[]]$Arguments
    )

    Start-Process -FilePath $FilePath -ArgumentList $Arguments | Out-Null
    exit 0
}

function Invoke-VSCodeFamilyOpen {
    $target = '.'
    $targetProvided = $false
    $line = $null

    for ($i = 0; $i -lt $args.Count; $i++) {
        switch ($args[$i]) {
            '-h' { Show-VSCodeFamilyUsage; exit 0 }
            '--help' { Show-VSCodeFamilyUsage; exit 0 }
            '-l' {
                if ($i + 1 -ge $args.Count) {
                    Fail 'Error: missing value for --line' 2
                }
                $i++
                if ($args[$i] -notmatch '^[1-9][0-9]*$') {
                    Fail 'Error: --line must be a positive integer' 2
                }
                $line = [int]$args[$i]
            }
            '--line' {
                if ($i + 1 -ge $args.Count) {
                    Fail 'Error: missing value for --line' 2
                }
                $i++
                if ($args[$i] -notmatch '^[1-9][0-9]*$') {
                    Fail 'Error: --line must be a positive integer' 2
                }
                $line = [int]$args[$i]
            }
            default {
                if ($targetProvided) {
                    Fail 'Error: only one path argument is supported' 2
                }
                $target = $args[$i]
                $targetProvided = $true
            }
        }
    }

    $commandPath = Get-VSCodeFamilyCommand
    if (-not $commandPath) {
        Fail "Error: $script:IdeDisplayName CLI not found on PATH. Expected one of: $script:IdeCommandDisplay" 127
    }

    if (-not (Test-Path -LiteralPath $target)) {
        Fail "Error: path does not exist: $target" 2
    }

    $target = (Resolve-Path -LiteralPath $target).Path

    if (Test-Path -LiteralPath $target -PathType Container) {
        $openMode = 'dir'
        $searchDir = $target
    }
    else {
        $openMode = 'file'
        $searchDir = Split-Path -Parent $target
    }

    $contextPath = Find-NearestMatch -StartDirectory $searchDir -Extension 'code-workspace'
    if (-not $contextPath) {
        $solution = Find-NearestMatch -StartDirectory $searchDir -Extension 'sln'
        if ($solution) {
            $contextPath = Split-Path -Parent $solution
        }
    }
    if (-not $contextPath) {
        $project = Find-NearestMatch -StartDirectory $searchDir -Extension 'csproj'
        if ($project) {
            $contextPath = Split-Path -Parent $project
        }
    }

    if ($contextPath) {
        if ($openMode -eq 'file') {
            if ($line) {
                Start-VSCodeFamilyDetached -FilePath $commandPath -Arguments @($contextPath, '--goto', "$target`:$line")
            }

            Start-VSCodeFamilyDetached -FilePath $commandPath -Arguments @($contextPath, $target)
        }

        Start-VSCodeFamilyDetached -FilePath $commandPath -Arguments @($contextPath)
    }

    if ($openMode -eq 'file' -and $line) {
        Start-VSCodeFamilyDetached -FilePath $commandPath -Arguments @('--goto', "$target`:$line")
    }

    Start-VSCodeFamilyDetached -FilePath $commandPath -Arguments @($target)
}
