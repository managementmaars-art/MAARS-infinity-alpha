# 微信自动化脚本 - Windows 版 - 发送消息给联系人
# 编码说明：本文件须为 UTF-8 带 BOM，否则在中文 Windows 下会被当 GBK 解析导致语法错误（如报“缺少右侧大括号”）
# 用法: powershell -ExecutionPolicy Bypass -File wechat_automation_script.ps1 [用户名] [消息内容]
# 若不传参数，则从剪切板获取：第一行为联系人名称，第二行起为消息内容
# 参数说明:
#   $args[0]: 用户名 (可选，不传则从剪切板获取)
#   $args[1]: 消息内容 (可选，不传则从剪切板获取)

#Requires -Version 5.1

param(
    [string]$UserName = "",
    [string]$MessageText = ""
)

# 若未传参，从剪切板读取（第一行=联系人，其余=消息）
if ($UserName -eq "" -and $MessageText -eq "" -and $args.Count -eq 0) {
    try {
        $clip = Get-Clipboard -Raw -ErrorAction SilentlyContinue
        if ($clip) {
            $lines = $clip -split "`r?`n", 2
            $UserName = $lines[0].Trim()
            $MessageText = if ($lines.Count -gt 1) { $lines[1].Trim() } else { "" }
        }
    } catch {
        # 无剪切板或不可用则保持为空
    }
}

# 兼容位置参数：powershell -File script.ps1 "联系人" "消息"
if ($args.Count -ge 1 -and $UserName -eq "") { $UserName = $args[0] }
if ($args.Count -ge 2 -and $MessageText -eq "") { $MessageText = $args[1] }

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

# P/Invoke：置前窗口与最小化（同一会话重复运行时不重复添加类型）
try {
    Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
using System.Text;
public class Win32 {
    [DllImport("user32.dll", SetLastError = true)]
    public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll", SetLastError = true)]
    public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
    [DllImport("user32.dll")]
    public static extern bool GetWindowRect(IntPtr hWnd, out Win32.RECT lpRect);
    [DllImport("user32.dll")]
    public static extern bool SetCursorPos(int x, int y);
    [DllImport("user32.dll")]
    public static extern void mouse_event(int dwFlags, int dx, int dy, int cButtons, int dwExtraInfo);
    public const int SW_RESTORE = 9;
    public const int SW_MINIMIZE = 6;
    public const int MOUSEEVENTF_LEFTDOWN = 0x02;
    public const int MOUSEEVENTF_LEFTUP = 0x04;
    [StructLayout(LayoutKind.Sequential)]
    public struct RECT { public int Left; public int Top; public int Right; public int Bottom; }
}
"@
} catch {
    if ($_.Exception.Message -notmatch "already exists") { throw }
}

function Get-WeChatWindowHandle {
    $procs = @("微信", "Weixin")
    foreach ($name in $procs) {
        $pList = @(Get-Process -Name $name -ErrorAction SilentlyContinue)
        foreach ($p in $pList) {
            if ($p -and $p.MainWindowHandle -ne [IntPtr]::Zero) {
                return $p.MainWindowHandle
            }
        }
    }
    return $null
}

function Focus-WeChat {
    $hwnd = Get-WeChatWindowHandle
    if (-not $hwnd) {
        Write-Error "未找到微信窗口，请确保微信已登录并已打开主界面。"
        exit 1
    }
    [Win32]::ShowWindow($hwnd, [Win32]::SW_RESTORE) | Out-Null
    Start-Sleep -Milliseconds 300
    [Win32]::SetForegroundWindow($hwnd) | Out-Null
    Start-Sleep -Milliseconds 500
    return $hwnd
}

function Send-KeysToWeChat {
    param([string]$Keys)
    Start-Sleep -Milliseconds 200
    [System.Windows.Forms.SendKeys]::SendWait($Keys)
}

# 主流程
try {
    # 0. 校验联系人名
    if ($UserName -eq "") {
        Write-Error "联系人名不能为空，请通过参数或剪切板（第一行）提供。"
        exit 1
    }
    # 1. 激活微信
    $hwnd = Focus-WeChat
    Start-Sleep -Seconds 2

    # 2. 打开搜索框（Windows 微信一般为 Ctrl+F，若已自定义请改此处）
    Send-KeysToWeChat("^f")
    Start-Sleep -Milliseconds 1500

    # 3. 输入联系人：用剪切板粘贴
    if ($UserName -ne "") {
        Set-Clipboard -Value $UserName
    }
    Send-KeysToWeChat("^v")
    Start-Sleep -Seconds 2

    # 4. 回车选择第一个结果
    Send-KeysToWeChat("{ENTER}")
    Start-Sleep -Milliseconds 1500

    # 5. 点击窗口右下角定位输入框
    $rect = New-Object -TypeName "Win32+RECT"
    [Win32]::GetWindowRect($hwnd, [ref]$rect) | Out-Null
    $x = $rect.Right - 20
    $y = $rect.Bottom - 20
    [Win32]::SetCursorPos([int]$x, [int]$y) | Out-Null
    Start-Sleep -Milliseconds 100
    [Win32]::mouse_event([Win32]::MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    [Win32]::mouse_event([Win32]::MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    Start-Sleep -Seconds 1

    # 6. 粘贴消息内容（仅当有内容时粘贴，否则会误粘贴上一步的联系人名）
    if ($MessageText -ne "") {
        Set-Clipboard -Value $MessageText
        Send-KeysToWeChat("^v")
        Start-Sleep -Seconds 2
    }

    # 7. 回车发送
    Send-KeysToWeChat("{ENTER}")
    Start-Sleep -Milliseconds 500
    Send-KeysToWeChat("{ENTER}")
    Start-Sleep -Seconds 3

    # 8. 最小化微信窗口
    [Win32]::ShowWindow($hwnd, [Win32]::SW_MINIMIZE) | Out-Null

    Write-Host "微信消息发送完成"
} catch {
    Write-Error $_.Exception.Message
    exit 1
}
