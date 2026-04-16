---
name: wechat-message
description: 此技能用于在 macOS/Windows 上通过脚本自动化发送微信消息。当用户需要"发送微信消息"、"给微信好友发消息"、"微信自动发送"、"微信群里发消息"、或提到"wechat message"、"微信自动化"时使用此技能。macOS 使用 AppleScript + cliclick，Windows 使用 PowerShell，按平台选用对应脚本。
version: 1.3.0
---

# 微信消息发送技能

此技能通过平台脚本实现微信消息的自动化发送：**macOS 使用 AppleScript + cliclick**，**Windows 使用 PowerShell**。按当前操作系统选用对应脚本即可。

## 功能概述

- 自动激活微信应用
- 搜索指定联系人或群组
- 发送指定消息内容
- 支持中文和特殊字符

## 使用方法

### macOS（AppleScript）

```bash
osascript scripts/wechat_automation_script.applescript "<联系人名称>" "<消息内容>"
```

### Windows（PowerShell）

```powershell
powershell -ExecutionPolicy Bypass -File scripts/wechat_automation_script.ps1 "<联系人名称>" "<消息内容>"
```

### 参数说明

| 参数 | 必填 | 说明 |
|------|------|------|
| 联系人名称 | 是 | 微信联系人名称或群名称，需完全匹配 |
| 消息内容 | 是 | 要发送的消息文本 |

### 使用示例

**macOS：**
```bash
osascript scripts/wechat_automation_script.applescript "张三" "你好，今天有空吗？"
osascript scripts/wechat_automation_script.applescript "工作群" "大家好！"
```

**Windows：**
```powershell
powershell -ExecutionPolicy Bypass -File scripts/wechat_automation_script.ps1 "张三" "你好，今天有空吗？"
powershell -ExecutionPolicy Bypass -File scripts/wechat_automation_script.ps1 "工作群" "大家好！"
```

## 工作流程

两平台流程一致，仅快捷键不同：

1. **激活微信** - 将微信窗口置于最前
2. **打开搜索** - macOS：`Cmd+F` / Windows：`Ctrl+F`
3. **搜索联系人** - 粘贴联系人名并选择第一个匹配结果（Ctrl+V / Cmd+V）
4. **定位输入框** - macOS：cliclick 点击窗口右下角 / Windows：Tab 键定位
5. **发送消息** - 粘贴消息内容并按回车发送
6. **收尾** - macOS：`Cmd+H` 隐藏窗口 / Windows：最小化窗口

## 注意事项

- **微信必须已登录** - 执行前确保微信已打开并登录
- **联系人名称需精确匹配** - 搜索时会选择第一个匹配结果
- **执行时间约 15 秒** - 脚本包含多个延时，执行期间勿操作微信
- **macOS**：需要安装 cliclick 并授予 **辅助功能** 权限
- **Windows**：若提示无法执行脚本，请使用 `-ExecutionPolicy Bypass`；若在微信内修改过「搜索」快捷键，需在 `.ps1` 中把 `^f` 改为对应快捷键

## 权限配置

### macOS

#### 1. 安装 cliclick

使用 Homebrew 安装：

```bash
brew install cliclick
```

#### 2. 授予辅助功能权限

1. **系统设置** → **隐私与安全性** → **辅助功能**
2. 将 **终端**（或 iTerm、Cursor 等）加入列表并勾选
3. 如有 **System Events**，建议一并勾选

### Windows

无需额外权限；首次运行若受限，使用 `-ExecutionPolicy Bypass` 执行脚本即可。

## 故障排除

| 问题 | 可能原因 | 解决方案 |
|------|----------|----------|
| 消息未发送 | 焦点未在输入框 | 执行期间勿切换窗口，可重试 |
| 搜索不到联系人 | 名称不匹配 | 确认联系人/群名与微信中完全一致 |
| macOS 脚本无反应 | 未给辅助功能权限 | 在「辅助功能」中勾选终端等应用 |
| macOS 鼠标点击无效 | cliclick 未安装或权限不足 | `brew install cliclick` 并授予辅助功能权限 |
| Windows 无法执行脚本 | 执行策略限制 | 使用 `-ExecutionPolicy Bypass` |
| 发送中文乱码 | 编码问题 | 终端使用 UTF-8 编码 |

## 文件结构

```
wechat-message/
├── SKILL.md                                    # 本技能说明
├── README.md                                   # 使用说明
├── examples/
│   └── sample.md                               # 使用示例
└── scripts/
    ├── wechat_automation_script.applescript    # macOS 脚本
    └── wechat_automation_script.ps1            # Windows 脚本
```
