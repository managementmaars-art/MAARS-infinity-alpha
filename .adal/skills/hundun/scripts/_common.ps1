# hd_skill common logic (PowerShell) - equivalent to _common.sh
$script:CommonScriptDir = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Path }

# Force UTF-8 output to avoid garbled Chinese on Windows
$OutputEncoding = [System.Text.Encoding]::UTF8
if ([Console]::OutputEncoding -ne [System.Text.Encoding]::UTF8) {
    try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch {}
}
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
$script:ConfigPath = if ($env:HDXY_CONFIG) { $env:HDXY_CONFIG } else { Join-Path $env:USERPROFILE ".hdxy_config" }
$script:DefaultBaseUrl = "https://hddrapi.hundun.cn"
$script:BaseUrl = if ($env:HDXY_API_BASE_URL) { $env:HDXY_API_BASE_URL } else { $script:DefaultBaseUrl }
$script:ApiKey = ""

function Load-Config {
    if (-not (Test-Path $script:ConfigPath)) {
        $dir = Split-Path $script:ConfigPath
        if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
        @"
# hd_skill config (auto-generated)
# Replace api_key from https://tools.hundun.cn/h5Bin/aia/#/keys

api_key=
base_url=$script:DefaultBaseUrl
"@ | Set-Content -Path $script:ConfigPath -Encoding UTF8
        Write-Host "Config created: $script:ConfigPath" -ForegroundColor Yellow
        Write-Host "Send api_key (hd_sk_...) to AI to configure. Get key: https://tools.hundun.cn/h5Bin/aia/#/keys" -ForegroundColor Yellow
        return $false
    }
    $lines = Get-Content $script:ConfigPath -ErrorAction SilentlyContinue
    foreach ($line in $lines) {
        if ($line -match '^api_key=(.*)$') { $script:ApiKey = $matches[1].Trim() }
        if ($line -match '^base_url=(.*)$') { $script:BaseUrl = $matches[1].Trim() }
    }
    if ($env:HDXY_API_BASE_URL) { $script:BaseUrl = $env:HDXY_API_BASE_URL }
    $script:BaseUrl = $script:BaseUrl.TrimEnd('/')
    return $true
}

function Get-UrlEncode([string]$s) {
    if ($s -eq $null) { return "" }
    [System.Uri]::EscapeDataString($s)
}

# PS 5.x: use DownloadData + UTF-8 decode (more reliable than DownloadString for JSON with CJK).
function Read-WebClientUtf8([string]$url, [hashtable]$extraHeaders) {
    $wc = New-Object System.Net.WebClient
    foreach ($h in $extraHeaders.GetEnumerator()) {
        $wc.Headers.Add($h.Key, $h.Value)
    }
    $utf8 = [System.Text.Encoding]::UTF8
    $respBody = ""
    $respCode = 200
    try {
        $bytes = $wc.DownloadData($url)
        $respBody = $utf8.GetString($bytes)
    } catch {
        $ex = $_.Exception
        $respCode = 0
        if ($ex.Response) {
            $respCode = [int]$ex.Response.StatusCode
            try {
                $sr = New-Object System.IO.StreamReader($ex.Response.GetResponseStream(), $utf8)
                $respBody = $sr.ReadToEnd()
                $sr.Close()
            } catch { }
        }
    }
    $out = New-Object PSCustomObject
    $out | Add-Member -NotePropertyName Body -NotePropertyValue $respBody -Force
    $out | Add-Member -NotePropertyName StatusCode -NotePropertyValue $respCode -Force
    return $out
}

function Invoke-ApiGetNoAuth([string]$path) {
    $url = "$script:BaseUrl$path"
    $result = Read-WebClientUtf8 $url @{}
    return "$($result.Body)`n$($result.StatusCode)"
}

function Invoke-ApiGet([string]$path) {
    if (-not $script:ApiKey) {
        Write-Host "Error: api_key not configured. Send api_key (hd_sk_...) to AI. Get key: https://tools.hundun.cn/h5Bin/aia/#/keys" -ForegroundColor Red
        return $null
    }
    $url = "$script:BaseUrl$path"
    $result = Read-WebClientUtf8 $url @{ "X-API-Key" = $script:ApiKey }
    return "$($result.Body)`n$($result.StatusCode)"
}

function Invoke-ApiGetQuery([string]$path, [string]$key, [string]$value) {
    $encoded = Get-UrlEncode $value
    Invoke-ApiGet "$path`?$key=$encoded"
}

function Invoke-ApiPost([string]$path, [string]$body) {
    if (-not $script:ApiKey) {
        Write-Host "Error: api_key not configured." -ForegroundColor Red
        return $null
    }
    $url = "$script:BaseUrl$path"
    $origin = ([System.Uri]$script:BaseUrl).GetLeftPart([System.UriPartial]::Authority)
    $wc = New-Object System.Net.WebClient
    $wc.Encoding = [System.Text.Encoding]::UTF8
    $wc.Headers.Add("X-API-Key", $script:ApiKey)
    $wc.Headers.Add("Origin", $origin)
    $wc.Headers.Add("Content-Type", "application/json; charset=utf-8")
    $utf8 = [System.Text.Encoding]::UTF8
    try {
        $resp = $wc.UploadString($url, "POST", $body)
        return "$resp`n200"
    } catch {
        $ex = $_.Exception
        $status = 0
        $respBody = ""
        if ($ex.Response) {
            $status = [int]$ex.Response.StatusCode
            try {
                $sr = New-Object System.IO.StreamReader($ex.Response.GetResponseStream(), $utf8)
                $respBody = $sr.ReadToEnd()
                $sr.Close()
            } catch { }
        }
        return "${respBody}`n$status"
    }
}

function Invoke-CollectIntent([string]$intentDesc, [string]$sceneValue, [string]$sceneDesc, [string]$extra) {
    if (-not $script:ApiKey) { return }
    try {
        $body = @{ intent_desc = $intentDesc; scene_value = $sceneValue; scene_desc = $sceneDesc; extra_related_content = $extra } | ConvertTo-Json
        Invoke-ApiPost "/aia/api/v1/intent/collect" $body | Out-Null
    } catch {
        # intent collect must not block search and other main flows
    }
}

function Parse-Response([string]$raw) {
    $lines = $raw -split "`n"
    $httpCode = $lines[-1]
    $body = ($lines[0..($lines.Count-2)] -join "`n")
    if ($httpCode -ne "200") {
        Write-Host "HTTP $httpCode" -ForegroundColor Red
        Write-Host $body.Substring(0, [Math]::Min(500, $body.Length)) -ForegroundColor Red
        exit 1
    }
    $errNo = if ($body -match '"error_no"\s*:\s*(-?\d+)') { $matches[1] } else { $null }
    $errMsg = if ($body -match '"error_msg"\s*:\s*"([^"]*)"') { $matches[1] } else { "Unknown error" }
    if ($errNo -and $errNo -ne "0") {
        Write-Host $errMsg -ForegroundColor Red
        exit 1
    }
    if ($body -match '"compressed"\s*:\s*true') {
        try {
            $json = $body | ConvertFrom-Json
            $data = $json.data
            if (-not $data) { throw "no data" }
            $bytes = [Convert]::FromBase64String($data)
            $utf8 = [System.Text.Encoding]::UTF8
            # 1) Try zstd CLI
            $zstd = Get-Command zstd -ErrorAction SilentlyContinue
            if ($zstd) {
                $tmpIn = [System.IO.Path]::GetTempFileName()
                $tmpOut = [System.IO.Path]::GetTempFileName()
                [System.IO.File]::WriteAllBytes($tmpIn, $bytes)
                & zstd -d $tmpIn -o $tmpOut 2>$null
                if (Test-Path $tmpOut) {
                    $decoded = [System.IO.File]::ReadAllText($tmpOut, $utf8)
                    Remove-Item $tmpIn, $tmpOut -Force -ErrorAction SilentlyContinue
                    Write-Output $decoded
                    return
                }
                Remove-Item $tmpIn -Force -ErrorAction SilentlyContinue
            }
            # 2) Fallback: Python + zstandard (pip install zstandard)
            $py = (Get-Command python -ErrorAction SilentlyContinue).Source
            if (-not $py) { $py = (Get-Command python3 -ErrorAction SilentlyContinue).Source }
            $pyScript = Join-Path $script:CommonScriptDir "_decompress.py"
            if ($py -and (Test-Path $pyScript)) {
                $tmpJson = [System.IO.Path]::GetTempFileName()
                $utf8NoBom = New-Object System.Text.UTF8Encoding $false
                [System.IO.File]::WriteAllText($tmpJson, $body, $utf8NoBom)
                $decoded = & $py $pyScript $tmpJson 2>$null
                Remove-Item $tmpJson -Force -ErrorAction SilentlyContinue
                $decStr = if ($decoded -is [array]) { $decoded -join "`n" } else { [string]$decoded }
                if ($decStr.Length -gt 10) { Write-Output $decStr; return }
            }
        } catch { }
    }
    Write-Output $body
}
