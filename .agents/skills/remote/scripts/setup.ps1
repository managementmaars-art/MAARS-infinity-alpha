param(
    [switch]$Force
)

$ErrorActionPreference = "Stop"

function Write-Log {
    param([string]$Message)
    Write-Host "[remote/setup] $Message"
}

function Quote-BashArg {
    param([string]$Value)

    return "'" + ($Value -replace "'", "'""'""'") + "'"
}

function Get-StateDir {
    $base = $env:LOCALAPPDATA
    if ([string]::IsNullOrWhiteSpace($base)) {
        throw "未检测到 LOCALAPPDATA，无法写入 remote 状态目录。"
    }

    return Join-Path $base "remote"
}

function Get-BootstrapStateFile {
    return Join-Path (Get-StateDir) "bootstrap-state.json"
}

function Write-Utf8NoBomFile {
    param(
        [string]$Path,
        [string]$Content
    )

    $utf8NoBom = [System.Text.UTF8Encoding]::new($false)
    [System.IO.File]::WriteAllText($Path, $Content, $utf8NoBom)
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
        throw "未识别到当前执行环境，无法安全完成 remote setup。"
    }

    return $runtimeType
}

function Get-HostOsForRuntime {
    param([string]$RuntimeType)

    switch ($RuntimeType) {
        "windows-msys" { return "windows" }
        "linux-wsl" { return "linux" }
        "linux-native" { return "linux" }
        "macos-native" { return "macos" }
        default { return "unknown" }
    }
}

function Get-BashFlavorForRuntime {
    param([string]$RuntimeType)

    switch ($RuntimeType) {
        "windows-msys" { return "msys" }
        "linux-wsl" { return "wsl" }
        "linux-native" { return "native" }
        "macos-native" { return "native" }
        default { return "unknown" }
    }
}

function Test-SshAvailable {
    $cmd = Get-Command ssh -ErrorAction SilentlyContinue
    if ($null -eq $cmd) {
        return $false
    }

    # 局部切换 ErrorActionPreference：全局 "Stop" 会导致 ssh -V 的 stderr 输出被当作终止错误
    $prevEAP = $ErrorActionPreference
    try {
        $ErrorActionPreference = 'Continue'
        $output = (& ssh -V 2>&1 | Out-String).Trim()
        if (-not [string]::IsNullOrWhiteSpace($output)) {
            return $true
        }
    } catch {
    } finally {
        $ErrorActionPreference = $prevEAP
    }

    return $false
}

function Get-SshVersion {
    # 局部切换 ErrorActionPreference：全局 "Stop" 会导致 ssh -V 的 stderr 输出被当作终止错误
    $prevEAP = $ErrorActionPreference
    try {
        $ErrorActionPreference = 'Continue'
        $output = (& ssh -V 2>&1 | Out-String).Trim()
        if ($output -match 'OpenSSH_([0-9]+\.[0-9]+)') {
            return $Matches[1]
        }
    } catch {
    } finally {
        $ErrorActionPreference = $prevEAP
    }

    return "unknown"
}

function Write-BootstrapState {
    param(
        [bool]$SshInstalled,
        [string]$RuntimeType,
        [string]$BashPath
    )

    $stateDir = Get-StateDir
    $stateFile = Get-BootstrapStateFile
    $null = New-Item -ItemType Directory -Path $stateDir -Force

    $now = [DateTimeOffset]::Now.ToString("yyyy-MM-ddTHH:mm:sszzz")
    # Windows 路径反斜杠在 PS 5.1 ConvertTo-Json 下不会被转义，统一转为正斜杠避免生成无效 JSON
    $normalizedBashPath = $BashPath -replace '\\', '/'
    $payload = [ordered]@{
        skill_name           = "remote"
        sshpass_installed    = $false
        sshpass_version      = "none"
        sshpass_provider     = "none"
        auth_mechanism       = "ssh_askpass"
        ssh_installed        = $SshInstalled
        ssh_version          = (Get-SshVersion)
        os_type              = (Get-HostOsForRuntime -RuntimeType $RuntimeType)
        runtime_type         = $RuntimeType
        bash_available       = $true
        bash_flavor          = (Get-BashFlavorForRuntime -RuntimeType $RuntimeType)
        bash_path            = $normalizedBashPath
        windows_remote_ready = ($SshInstalled -and $RuntimeType -eq "windows-msys")
        last_setup_at        = $now
        last_verified_at     = $now
    }

    $json = $payload | ConvertTo-Json -Depth 4
    Write-Utf8NoBomFile -Path $stateFile -Content $json
}

$bash = Get-BashCommand
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Push-Location $scriptDir
try {
    $runtimeType = Get-RuntimeType -BashPath $bash.Source

    if ($runtimeType -eq "linux-wsl") {
        Write-Log "当前执行环境为 linux-wsl，改为在 WSL 内安装 Linux sshpass。"
        $quoted = New-Object System.Collections.Generic.List[string]
        $quoted.Add("REMOTE_RUNTIME_TYPE=$(Quote-BashArg -Value $runtimeType)")
        $quoted.Add("REMOTE_HOST_BASH_PATH=$(Quote-BashArg -Value ($bash.Source -replace '\\', '/'))")
        if (-not [string]::IsNullOrWhiteSpace($env:LOCALAPPDATA)) {
            $quoted.Add("REMOTE_HOST_WINDOWS_LOCALAPPDATA=$(Quote-BashArg -Value $env:LOCALAPPDATA)")
        }
        $quoted.Add((Quote-BashArg -Value "./setup.sh"))
        if ($Force) {
            $quoted.Add("--force")
        }

        & $bash.Source -lc ([string]::Join(' ', $quoted))
        exit $LASTEXITCODE
    }

    if ($runtimeType -ne "windows-msys") {
        throw "当前执行环境不受支持：$runtimeType"
    }

    # Windows: 验证 SSH 可用性（使用 SSH_ASKPASS 机制，不安装 sshpass）
    if ((-not $Force) -and (Test-SshAvailable)) {
        Write-Log "检测到可用 SSH，跳过安装。"
    } else {
        if (-not (Test-SshAvailable)) {
            throw "未检测到可用的 SSH。Windows 下 SSH 通常随 Git for Windows 或 MSYS2 提供，请确认已安装。"
        }
    }

    $verified = Test-SshAvailable
    Write-BootstrapState -SshInstalled $verified -RuntimeType $runtimeType -BashPath $bash.Source
    if (-not $verified) {
        throw "SSH 验证失败，无法完成 Windows 远程访问环境设置。"
    }

    Write-Log "SSH 已完成验证（使用 SSH_ASKPASS 机制），状态文件已写入 $(Get-BootstrapStateFile)"
    Write-Log "Windows 下远程访问必须通过 scripts/remote.ps1 进入，当前执行环境为 $runtimeType。"
}
finally {
    Pop-Location
}
