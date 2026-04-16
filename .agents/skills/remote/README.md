# Remote 远程访问技能

`remote` 是一个面向内部场景的 Linux 服务器远程访问 skill。它在宿主本地状态目录保存：

- `bootstrap-state.json`：当前运行时对应的 setup 与验证状态
- `servers.json`：服务器地址、端口、用户名、密码与最近一次验证结果

密码传递机制：
- Windows（`windows-msys`）：`SSH_ASKPASS`（OpenSSH 原生支持，无需额外安装）
- Linux/macOS/WSL：`sshpass`

## 目录结构

```text
skills/remote/
├── README.md
├── SKILL.md
├── agents/
│   └── openai.yaml
├── references/
│   ├── remote-guidelines.md
│   ├── setup.md
│   └── state.md
└── scripts/
    ├── remote.ps1
    ├── remote.sh
    ├── runtime.sh
    ├── setup.ps1
    └── setup.sh
```

## 状态目录

状态目录由脚本内部函数自动确定，不在此列出具体路径。其中包含：

- `bootstrap-state.json`
- `servers.json`

## setup

`remote` 不做 code agent 探测，只做执行环境判定。标准执行环境只有四种：

- `windows-msys`
- `linux-wsl`
- `linux-native`
- `macos-native`

其中 `linux-wsl` 直接按 Linux 分支处理。具体判定方法、成功标准和修复边界统一见 `references/setup.md`。

### Windows

```powershell
powershell -ExecutionPolicy Bypass -File .\skills\remote\scripts\setup.ps1
```

- `windows-msys`：验证 SSH 可用性，使用 `SSH_ASKPASS` 机制（无需安装 sshpass）
- `linux-wsl`：由 `setup.ps1` 转发到 `setup.sh` 安装 sshpass

### macOS / Linux

```bash
bash ./skills/remote/scripts/setup.sh
```

## 远程执行

### Windows

Windows 下所有远程访问都必须走 `bash -lc`。推荐入口是 `remote.ps1`，它内部先按 `scripts/runtime.sh` 判定当前执行环境，再转发到 `bash -lc`：

```powershell
.\skills\remote\scripts\remote.ps1 -Save -Address "10.0.0.8" -Username root -Password "secret"
.\skills\remote\scripts\remote.ps1 -Address "10.0.0.8" -Username root -Password "secret" -Command "hostname && whoami"
.\skills\remote\scripts\remote.ps1 -Parallel -Address "10.0.0.8" -Commands "uptime" "free -h" "df -h"
```

兼容旧版透传调用：

```powershell
.\skills\remote\scripts\remote.ps1 --save "10.0.0.8" --user root --password "secret"
.\skills\remote\scripts\remote.ps1 "10.0.0.8" "hostname && whoami"
```

状态文件统一使用无 BOM 的 UTF-8 写入；读取端兼容历史 UTF-8 BOM 文件。
`windows-msys` 下使用 `SSH_ASKPASS` 机制自动提供密码，保持纯非交互；凭据错误时应直接失败。

如果手工执行，也只能显式使用：

```powershell
bash -lc './skills/remote/scripts/remote.sh "10.0.0.8" "hostname && whoami"'
```

禁止：

- 在 Windows 下直接执行 `remote.sh`
- 在连接失败后手工切换不同的密码传递参数试错

### macOS / Linux

```bash
./skills/remote/scripts/remote.sh --save "10.0.0.8" --user root --password "secret"
./skills/remote/scripts/remote.sh "10.0.0.8" "hostname && whoami"
./skills/remote/scripts/remote.sh --parallel "10.0.0.8" "uptime" "free -h" "df -h"
```

## 服务器记录管理

首次访问或用户修改连接信息后，先写入服务器记录：

```bash
./skills/remote/scripts/remote.sh --save "10.0.0.8" --user root --password "secret" --port 22
```

查看当前记录：

```bash
./skills/remote/scripts/remote.sh --show "10.0.0.8"
```

## 工作边界

- 默认只做读取、诊断、检查
- 默认不做批量改动、重启、删除、停服务
- 诊断类任务首轮不应先用 `grep/head/tail` 过滤
- 多维采集优先并行执行
- 认证失败时只能先报告"远端拒绝了密码认证"，不能直接归因为密码特殊字符或兼容性问题
