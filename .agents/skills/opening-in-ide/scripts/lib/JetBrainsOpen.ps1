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

function Show-JetBrainsUsage {
    @"
Usage: $script:UsageScriptName [path] [--line N]

Open a file or folder in $script:IdeDisplayName.
If possible, open it within the nearest project context.

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

function Find-NearestProjectFile {
    param(
        [Parameter(Mandatory = $true)][string]$StartDirectory,
        [Parameter(Mandatory = $true)][ValidateSet('sln', 'csproj')][string]$Extension
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

function Find-NearestWebStormContextDirectory {
    param(
        [Parameter(Mandatory = $true)][string]$StartDirectory
    )

    $markers = @('.idea', 'package.json', 'pnpm-workspace.yaml', 'yarn.lock', 'package-lock.json', 'bun.lock', 'bun.lockb', 'tsconfig.json', 'jsconfig.json')
    $dir = (Resolve-Path -LiteralPath $StartDirectory).Path

    while ($true) {
        if (Test-Path -LiteralPath (Join-Path $dir '.idea') -PathType Container) {
            return $dir
        }

        foreach ($marker in $markers) {
            if (Test-Path -LiteralPath (Join-Path $dir $marker)) {
                return $dir
            }
        }

        $parent = [System.IO.Directory]::GetParent($dir)
        if ($null -eq $parent) {
            break
        }
        $dir = $parent.FullName
    }

    return $null
}

function Get-JetBrainsCommand {
    foreach ($candidate in $script:IdeCommandCandidates) {
        if (Get-Command $candidate -ErrorAction SilentlyContinue) {
            return $candidate
        }
    }

    return $null
}

function Start-JetBrainsDetached {
    param(
        [Parameter(Mandatory = $true)][string]$FilePath,
        [Parameter(Mandatory = $true)][string[]]$Arguments
    )

    Start-Process -FilePath $FilePath -ArgumentList $Arguments | Out-Null
    exit 0
}

function Open-WithJetBrainsContext {
    param(
        [Parameter(Mandatory = $true)][string]$ContextPath,
        [Parameter(Mandatory = $true)][string]$OpenMode,
        [Parameter(Mandatory = $true)][string]$Target,
        [Parameter(Mandatory = $false)][int]$Line,
        [Parameter(Mandatory = $true)][string]$CommandPath
)

    if ($OpenMode -eq 'file') {
        $effectiveLine = $Line
        if ((-not $effectiveLine) -and $script:ContextMode -eq 'webstorm') {
            $effectiveLine = 1
        }

        if ($effectiveLine) {
            Start-JetBrainsDetached -FilePath $CommandPath -Arguments @($ContextPath, '--line', "$effectiveLine", $Target)
        }

        Start-JetBrainsDetached -FilePath $CommandPath -Arguments @($ContextPath, $Target)
    }

    Start-JetBrainsDetached -FilePath $CommandPath -Arguments @($ContextPath)
}

function Invoke-JetBrainsOpen {
    $target = '.'
    $targetProvided = $false
    $line = $null

    for ($i = 0; $i -lt $args.Count; $i++) {
        switch ($args[$i]) {
            '-h' { Show-JetBrainsUsage; exit 0 }
            '--help' { Show-JetBrainsUsage; exit 0 }
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

    $commandPath = Get-JetBrainsCommand
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

    if ($script:ContextMode -eq 'rider') {
        $solution = Find-NearestProjectFile -StartDirectory $searchDir -Extension sln
        if ($solution) {
            Open-WithJetBrainsContext -ContextPath $solution -OpenMode $openMode -Target $target -Line $line -CommandPath $commandPath
        }

        $project = Find-NearestProjectFile -StartDirectory $searchDir -Extension csproj
        if ($project) {
            Open-WithJetBrainsContext -ContextPath $project -OpenMode $openMode -Target $target -Line $line -CommandPath $commandPath
        }
    }
    elseif ($script:ContextMode -eq 'webstorm') {
        $contextDir = Find-NearestWebStormContextDirectory -StartDirectory $searchDir
        if ($contextDir) {
            Open-WithJetBrainsContext -ContextPath $contextDir -OpenMode $openMode -Target $target -Line $line -CommandPath $commandPath
        }
    }

    if ($openMode -eq 'file' -and $line) {
        Start-JetBrainsDetached -FilePath $commandPath -Arguments @('--line', "$line", $target)
    }

    Start-JetBrainsDetached -FilePath $commandPath -Arguments @($target)
}
