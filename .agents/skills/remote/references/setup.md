# Remote setup 说明

仅在以下情况参考本文件：

- 第一次使用 `remote` skill
- `bootstrap-state.json` 不存在
- `bootstrap-state.json` 显示未就绪
- `bootstrap-state.json` 与当前运行时不一致
- 远程执行前发现认证工具真实不可用

## 执行环境判定

`remote` 不做 code agent 探测，只做执行环境判定。唯一判定方法由 `scripts/runtime.sh` 定义，统一收敛为四种执行环境：

- `windows-msys`
  - `uname -s` 命中 `MINGW*`、`MSYS*` 或 `CYGWIN*`
  - 密码传递使用 `SSH_ASKPASS` 机制（OpenSSH 原生支持）
- `linux-wsl`
  - `uname -s` 为 `Linux`
  - 且命中 `WSL_DISTRO_NAME`、`WSL_INTEROP`，或 `/proc/version` 包含 `microsoft`
  - 视为 Linux 分支处理，使用 `sshpass`
- `linux-native`
  - `uname -s` 为 `Linux`
  - 且不命中 WSL 信号
- `macos-native`
  - `uname -s` 为 `Darwin`

判定优先级固定为：

```text
windows-msys -> linux-wsl -> linux-native / macos-native
```

agent 不要靠口头约定或手工判断环境；必须复用标准脚本内的判定方法。

## 状态目录

状态目录由脚本内部函数自动确定（`remote.sh` / `setup.sh` 中的 `state_dir()`，`setup.ps1` 中的 `Get-StateDir`），agent 不应直接拼接路径来读取 `bootstrap-state.json`。检查状态必须按执行环境选择对应命令：
- `windows-msys`：`powershell -ExecutionPolicy Bypass -File .\skills\remote\scripts\remote.ps1 -CheckBootstrap`
- `linux-wsl`、`linux-native`、`macos-native`：`bash ./skills/remote/scripts/remote.sh --check-bootstrap`

setup 成功后写入：

- `bootstrap-state.json`
- Windows 写入必须使用无 BOM UTF-8；读取端需要兼容历史 BOM 文件

## 检测方式

### Windows（`windows-msys`）

验证 SSH 可用性：

```text
1. ssh 命令存在
2. ssh -V 有输出
```

如 SSH 不可用，直接终止 skill（`exit 13`）。Windows 11 自带 OpenSSH，通常无需额外安装。

### Linux / macOS

验证 sshpass 可用性：

```text
1. 命令存在
2. sshpass -V 或 sshpass -h 至少一种可识别
```

如命令不存在或帮助/版本输出异常，判定为未完成 setup。
这一步必须由标准脚本完成，agent 不应手工探测后再裸跑 SSH。

## 自动 setup

### windows-msys

执行方式：

```powershell
powershell -ExecutionPolicy Bypass -File .\skills\remote\scripts\setup.ps1
```

Windows 使用 `SSH_ASKPASS` 机制，不需要安装 `sshpass`。setup 脚本只验证 SSH 可用性，不可用则抛异常。

状态文件写为 `runtime_type=windows-msys`、`bash_flavor=msys`、`auth_mechanism=ssh_askpass`

注意：

- `windows-msys` 下远程访问推荐通过 `scripts/remote.ps1` 进入。
- 不允许在连接失败后依次切换 `sshpass -k`、`sshpass -e`、`sshpass -p` 试错。
- `setup.ps1` 只负责验证，不负责直接远程连接。

### linux-wsl / linux-native

执行方式：

```bash
bash ./skills/remote/scripts/setup.sh
```

自动安装顺序：

```bash
apt-get update && apt-get install -y sshpass
dnf install -y sshpass
yum install -y sshpass
```

说明：

- `linux-wsl` 直接按 Linux 分支处理，不需要单独引入 Windows setup 规则
- RHEL / CentOS / Fedora 系如缺依赖，可先启用 `epel-release`
- 如果从 Windows PowerShell 进入 WSL，标准入口仍然是 `setup.ps1`，由它转发到 `setup.sh`

### macos-native

```bash
brew install hudochenkov/sshpass/sshpass
```

说明：

- Homebrew 核心仓库不包含 `sshpass`，需通过第三方 tap 安装。

## 成功标准

- `bootstrap-state.json` 中认证机制已就绪
- `bootstrap-state.json` 中 `runtime_type` 与当前执行环境一致
- `bootstrap-state.json` 中 `bash_flavor` 与当前执行环境映射一致
- `bootstrap-state.json` 中 `auth_mechanism` 与当前运行环境对应的机制一致
- `windows-msys` 下 `bootstrap-state.json` 还必须满足 `bash_available=true` 与 `windows_remote_ready=true`
- `bootstrap-state.json` 记录最近一次 setup 与验证时间

## 修复边界

只有以下情况才触发 setup 或强制修复：

- 认证工具不可用（Windows: SSH 不可用；Linux/macOS: sshpass 不可用）
- `bootstrap-state.json` 缺失
- `bootstrap-state.json` 与当前执行环境不一致
- 状态文件显示未安装，且脚本复核真实环境后仍不可用

以下情况不触发 setup：

- 地址输错
- 端口错误
- 用户名或密码错误
- 远程命令本身执行失败
