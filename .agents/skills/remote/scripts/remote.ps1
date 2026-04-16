$ErrorActionPreference = "Stop"

function Write-Log {
    param([string]$Message)
    Write-Host "[remote] $Message"
}

function Quote-BashArg {
    param([string]$Value)

    return "'" + ($Value -replace "'", "'""'""'") + "'"
}

function Parse-InvocationArguments {
    param([string[]]$RawArgs)

    $parsed = [ordered]@{
        Save          = $false
        Show          = $false
        CheckBootstrap = $false
        Parallel      = $false
        Verbose       = $false
        Address       = $null
        Port          = $null
        Username      = $null
        Password      = $null
        Command       = $null
        Commands      = New-Object System.Collections.Generic.List[string]
        Passthrough   = $false
        PassthroughArgs = New-Object System.Collections.Generic.List[string]
    }

    $knownShortArgs = @(
        '-Save', '-Show', '-CheckBootstrap', '-Parallel', '-Verbose',
        '-Address', '-Port', '-Username', '-Password',
        '-Command', '-Commands'
    )

    for ($index = 0; $index -lt $RawArgs.Length; $index++) {
        $token = [string]$RawArgs[$index]

        if ($token.StartsWith('--')) {
            $parsed.Passthrough = $true
            break
        }

        if ($token.StartsWith('-') -and -not $knownShortArgs.Contains($token)) {
            $parsed.Passthrough = $true
            break
        }

        switch ($token) {
            '-Save' {
                $parsed.Save = $true
            }
            '-Show' {
                $parsed.Show = $true
            }
            '-CheckBootstrap' {
                $parsed.CheckBootstrap = $true
            }
            '-Parallel' {
                $parsed.Parallel = $true
            }
            '-Verbose' {
                $parsed.Verbose = $true
            }
            '-Address' {
                $index++
                if ($index -ge $RawArgs.Length) {
                    throw "参数 -Address 缺少值。"
                }
                $parsed.Address = [string]$RawArgs[$index]
            }
            '-Port' {
                $index++
                if ($index -ge $RawArgs.Length) {
                    throw "参数 -Port 缺少值。"
                }
                $parsed.Port = [string]$RawArgs[$index]
            }
            '-Username' {
                $index++
                if ($index -ge $RawArgs.Length) {
                    throw "参数 -Username 缺少值。"
                }
                $parsed.Username = [string]$RawArgs[$index]
            }
            '-Password' {
                $index++
                if ($index -ge $RawArgs.Length) {
                    throw "参数 -Password 缺少值。"
                }
                $parsed.Password = [string]$RawArgs[$index]
            }
            '-Command' {
                $index++
                if ($index -ge $RawArgs.Length) {
                    throw "参数 -Command 缺少值。"
                }
                $parsed.Command = [string]$RawArgs[$index]
            }
            '-Commands' {
                $index++
                if ($index -ge $RawArgs.Length) {
                    throw "参数 -Commands 至少需要一条命令。"
                }

                while ($index -lt $RawArgs.Length) {
                    $value = [string]$RawArgs[$index]
                    if ($value.StartsWith('-')) {
                        $index--
                        break
                    }

                    $parsed.Commands.Add($value)
                    $index++
                }

                if ($parsed.Commands.Count -eq 0) {
                    throw "参数 -Commands 至少需要一条命令。"
                }
            }
            default {
                $parsed.Passthrough = $true
                break
            }
        }
    }

    if ($parsed.Passthrough) {
        foreach ($arg in $RawArgs) {
            $parsed.PassthroughArgs.Add([string]$arg)
        }
    }

    return $parsed
}

function Build-RemoteShArgs {
    param($ParsedArgs)

    if ($ParsedArgs.Passthrough) {
        return ,$ParsedArgs.PassthroughArgs.ToArray()
    }

    $hasModeCount = 0
    foreach ($enabled in @($ParsedArgs.Save, $ParsedArgs.Show, $ParsedArgs.CheckBootstrap, $ParsedArgs.Parallel)) {
        if ($enabled) {
            $hasModeCount++
        }
    }
    if ($hasModeCount -gt 1) {
        throw "-Save、-Show、-CheckBootstrap、-Parallel 只能选择一种。"
    }

    $translated = New-Object System.Collections.Generic.List[string]

    if ($ParsedArgs.CheckBootstrap) {
        # --check-bootstrap 不需要 -Address、-Port 等参数
        $translated.Add("--check-bootstrap")
    } elseif ($ParsedArgs.Show) {
        # --show 不需要 -Address（无地址时列出所有已保存服务器）
        $translated.Add("--show")
    } else {
        if ([string]::IsNullOrWhiteSpace($ParsedArgs.Address)) {
            throw "请提供 -Address。"
        }
        if (-not [string]::IsNullOrWhiteSpace($ParsedArgs.Port)) {
            if ($ParsedArgs.Port -notmatch '^[0-9]+$') {
                throw "-Port 必须是数字。"
            }
        }
    }

    if ($ParsedArgs.Save) {
        if ([string]::IsNullOrWhiteSpace($ParsedArgs.Username) -or [string]::IsNullOrWhiteSpace($ParsedArgs.Password)) {
            throw "-Save 必须同时提供 -Username 和 -Password。"
        }
        if ($ParsedArgs.Commands.Count -gt 0) {
            throw "-Save 不允许同时提供 -Commands。请使用 -Command 指定单条命令。"
        }

        $translated.Add("--save")
    } elseif ($ParsedArgs.Show) {
        if (-not [string]::IsNullOrWhiteSpace($ParsedArgs.Username) -or -not [string]::IsNullOrWhiteSpace($ParsedArgs.Password)) {
            throw "-Show 不需要 -Username 或 -Password。"
        }
        if (-not [string]::IsNullOrWhiteSpace($ParsedArgs.Command) -or $ParsedArgs.Commands.Count -gt 0) {
            throw "-Show 不允许同时提供 -Command 或 -Commands。"
        }
    } elseif ($ParsedArgs.Parallel) {
        if (-not [string]::IsNullOrWhiteSpace($ParsedArgs.Command)) {
            throw "-Parallel 模式下请只使用 -Commands。"
        }
        if ($ParsedArgs.Commands.Count -eq 0) {
            throw "-Parallel 模式下必须提供 -Commands。"
        }

        $translated.Add("--parallel")
        if ($ParsedArgs.Verbose) {
            $translated.Add("--verbose")
        }
    } else {
        if ($ParsedArgs.CheckBootstrap) {
            # 已在上方处理，无需额外参数
        } elseif ($ParsedArgs.Commands.Count -gt 0) {
            throw "非并行模式下请使用 -Command，而不是 -Commands。"
        } elseif ([string]::IsNullOrWhiteSpace($ParsedArgs.Command)) {
            throw "请提供 -Command，或改用旧版透传参数。"
        }
        if (-not $ParsedArgs.CheckBootstrap -and $ParsedArgs.Verbose) {
            throw "-Verbose 仅在 -Parallel 模式下可用。"
        }
    }

    if (-not [string]::IsNullOrWhiteSpace($ParsedArgs.Port)) {
        $translated.Add("--port")
        $translated.Add($ParsedArgs.Port)
    }
    if (-not [string]::IsNullOrWhiteSpace($ParsedArgs.Username)) {
        $translated.Add("--user")
        $translated.Add($ParsedArgs.Username)
    }
    if (-not [string]::IsNullOrWhiteSpace($ParsedArgs.Password)) {
        $translated.Add("--password")
        $translated.Add($ParsedArgs.Password)
    }

    if (-not $ParsedArgs.CheckBootstrap) {
        if (-not $ParsedArgs.Show -or -not [string]::IsNullOrWhiteSpace($ParsedArgs.Address)) {
            $translated.Add($ParsedArgs.Address)
        }

        if ($ParsedArgs.Parallel) {
            foreach ($command in $ParsedArgs.Commands) {
                $encoded = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($command))
                $translated.Add("--command-base64")
                $translated.Add($encoded)
            }
        } elseif (-not $ParsedArgs.Show -and -not $ParsedArgs.Save) {
            if (-not [string]::IsNullOrWhiteSpace($ParsedArgs.Command)) {
                $encoded = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($ParsedArgs.Command))
                $translated.Add("--command-base64")
                $translated.Add($encoded)
            }
        }
    }

    return ,$translated.ToArray()
}

function Get-BashCommand {
    $bash = Get-Command bash -ErrorAction SilentlyContinue
    if ($null -eq $bash) {
        throw "Windows 下 remote skill 必须通过 bash -lc 执行，但当前环境未检测到 bash。"
    }

    return $bash
}

function Get-RuntimeType {
    param([string]$BashPath)

    $runtimeType = (& $BashPath -lc "source ./runtime.sh; remote_detect_runtime_type").Trim()
    if ([string]::IsNullOrWhiteSpace($runtimeType) -or $runtimeType -eq "unknown") {
        throw "未识别到当前执行环境，无法安全执行 remote skill。"
    }

    return $runtimeType
}

$bash = Get-BashCommand
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Push-Location $scriptDir
try {
    $runtimeType = Get-RuntimeType -BashPath $bash.Source
    if ($runtimeType -ne "windows-msys" -and $runtimeType -ne "linux-wsl") {
        throw "当前执行环境不受支持：$runtimeType"
    }

    $parsedArgs = Parse-InvocationArguments -RawArgs $args
    $remoteShArgs = Build-RemoteShArgs -ParsedArgs $parsedArgs

    $quoted = New-Object System.Collections.Generic.List[string]
    $quoted.Add("REMOTE_RUNTIME_TYPE=$(Quote-BashArg -Value $runtimeType)")
    $quoted.Add("REMOTE_HOST_BASH_PATH=$(Quote-BashArg -Value ($bash.Source -replace '\\', '/'))")
    if (-not [string]::IsNullOrWhiteSpace($env:LOCALAPPDATA)) {
        $quoted.Add("REMOTE_HOST_WINDOWS_LOCALAPPDATA=$(Quote-BashArg -Value $env:LOCALAPPDATA)")
    }
    $quoted.Add((Quote-BashArg -Value "./remote.sh"))
    foreach ($arg in $remoteShArgs) {
        $quoted.Add((Quote-BashArg -Value ([string]$arg)))
    }

    $commandString = [string]::Join(' ', $quoted)
    Write-Log "Windows 下固定通过 bash -lc 调用 remote.sh。当前执行环境：$runtimeType。"

    & $bash.Source -lc $commandString
    exit $LASTEXITCODE
}
finally {
    Pop-Location
}
