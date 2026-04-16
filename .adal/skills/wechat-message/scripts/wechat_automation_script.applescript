#!/usr/bin/osascript

-- 微信自动化脚本 - 发送消息给联系人
-- 用法: osascript wechat_automation_script.applescript [用户名] [消息内容]
-- 如果不传参数,则从剪切板获取用户名和消息内容
-- 参数说明:
--   $1: 用户名 (可选,不传则从剪切板获取)
--   $2: 消息内容 (可选,不传则从剪切板获取)

on run argv
    -- 获取用户名参数
    set userName to ""
    if (count of argv) >= 1 then
        set userName to item 1 of argv
    end if

    -- 获取消息内容参数
    set messageText to ""
    if (count of argv) >= 2 then
        set messageText to item 2 of argv
    end if

    -- 拉起微信
    try
        -- 第一步：优先用系统标准方式激活（不需要任何权限）
        tell application "WeChat"
            activate
            delay 0.4
        end tell
        
        -- 第二步：检查激活是否成功（判断是否仍在后台/最小化）
        -- 如果 activate 无效（最小化到 Dock），才执行 Dock 点击
        tell application "System Events"
            if frontmost of process "WeChat" is false then
                try
                    tell process "Dock" to tell list 1
                        -- 优先英文，失败自动切中文
                        try
                            click UI element "WeChat"
                        on error errDock1 number numDock1
                            log "[wechat-automation] Dock 点击 WeChat 失败 (" & numDock1 & "): " & errDock1 & "，尝试「微信」"
                            try
                                click UI element "微信"
                            on error errDock2 number numDock2
                                log "[wechat-automation] Dock 点击「微信」失败 (" & numDock2 & "): " & errDock2
                            end try
                        end try
                    end tell
                on error errDock number numDock
                    log "[wechat-automation] 访问 Dock 列表异常 (" & numDock & "): " & errDock
                end try
            end if
        end tell
    on error errLaunch number numLaunch
        log "[wechat-automation] 拉起微信流程异常 (" & numLaunch & "): " & errLaunch
    end try

    delay 0.5

    -- 使用快捷键 Cmd+F 打开搜索框
    tell application "System Events"
        tell process "WeChat"
            keystroke "f" using {command down}
        end tell
    end tell

    delay 1

    -- 输入用户名（使用剪切板粘贴方式）
    if userName is not "" then
        -- 如果提供了用户名参数,先存入剪切板tesdt
        set the clipboard to userName
    end if
    -- 直接使用 Cmd+V 粘贴用户名（无论是否提供参数,都使用粘贴方式）
    tell application "System Events"
        tell process "WeChat"
            keystroke "v" using {command down}
        end tell
    end tell

    delay 1

    -- 按回车选择第一个联系人
    tell application "System Events"
        tell process "WeChat"
            keystroke return
        end tell
    end tell

    delay 0.5

    -- 关键：点击微信窗口右下角区域，确保焦点移动到聊天输入框
    try
        tell application "System Events"
            tell process "WeChat"
                set windowPosition to position of window 1
                set windowSize to size of window 1
                -- 计算右下角位置（窗口宽度-25, 窗口高度-10）
                set xCoord to (item 1 of windowPosition) + (item 1 of windowSize) - 25
                set yCoord to (item 2 of windowPosition) + (item 2 of windowSize) - 10
            end tell
        end tell
        my clickAtScreenPosition(xCoord, yCoord)
    on error errWin number numWin
        log "[wechat-automation] 获取微信主窗口坐标失败，已跳过右下角点击 (" & numWin & "): " & errWin
    end try

    delay 0.5

    -- 处理消息内容
    if messageText is not "" then
        -- 如果提供了消息内容参数,存入剪切板
        set the clipboard to messageText
    end if
    -- 使用 Cmd+V 粘贴消息（无论是否提供参数,都使用粘贴方式）
    tell application "System Events"
        tell process "WeChat"
            keystroke "v" using {command down}
        end tell
    end tell

    delay 1

    -- 按回车发送消息
    tell application "System Events"
        tell process "WeChat"
            keystroke return
        end tell
    end tell

    delay 0.5

    -- 再按一次回车确保发送
    tell application "System Events"
        tell process "WeChat"
            keystroke return
        end tell
    end tell

    delay 0.5 

    -- 隐藏微信窗口（使用 Cmd+H）
    tell application "System Events"
        tell process "WeChat"
            keystroke "h" using {command down}
        end tell
    end tell

    return "微信消息发送完成"
end run

-- 使用 PATH 中的 cliclick（命令名，非全路径）；失败则跳过，假定输入框已聚焦
on clickAtScreenPosition(x, y)
    set px to x as integer
    set py to y as integer
    try
        do shell script "cliclick c:" & px & "," & py
        log "[wechat-automation] cliclick 点击成功，坐标 (" & px & "," & py & ")"
    on error errMsg number errNum
        log "[wechat-automation] cliclick 点击失败 (" & errNum & "): " & errMsg & "，坐标 (" & px & "," & py & ")"
    end try
end clickAtScreenPosition
