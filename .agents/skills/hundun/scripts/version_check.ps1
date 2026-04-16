# credential status check - GET /aia/api/v1/user/status/check (auth required)
$scriptDir = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
if (-not $scriptDir) { $scriptDir = Split-Path -Parent $PSCommandPath }
. (Join-Path $scriptDir "_common.ps1")

function Write-LoginGuidance {
    Write-Host "当前凭证可能已失效、无权限或未完成登录。请打开 https://tools.hundun.cn/h5Bin/aia/#/keys 登录混沌会员账号后，重新生成一个 hd_sk_ 开头的密钥发给 AI。拿到有效密钥后，我会继续当前任务。" -ForegroundColor Yellow
}

if (-not (Load-Config)) { exit 1 }

if (-not $script:ApiKey) {
    Write-LoginGuidance
    exit 1
}

$script:BaseUrl = $script:BaseUrl.TrimEnd('/')
$result = Read-WebClientUtf8 "$script:BaseUrl/aia/api/v1/user/status/check" @{
    "X-API-Key" = $script:ApiKey
    "X-Disable-Compress" = "true"
}
$raw = "$($result.Body)`n$($result.StatusCode)"
$body = $result.Body
$statusCode = [string]$result.StatusCode
$errMsg = if ($body -match '"error_msg"\s*:\s*"([^"]*)"') { $matches[1] } else { "" }
$authHint = "$statusCode $errMsg $body"
if ($authHint -match 'api[_ -]?key|密钥|鉴权|权限|401|403|unauthorized|forbidden|失效|未登录') {
    Write-LoginGuidance
    exit 1
}

Parse-Response $raw
