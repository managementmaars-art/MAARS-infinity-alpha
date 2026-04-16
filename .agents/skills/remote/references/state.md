# Remote 状态文件说明

`remote` skill 的本地状态目录由脚本内部函数自动确定（`remote.sh` / `setup.sh` 中的 `state_dir()`，`setup.ps1` 中的 `Get-StateDir`），agent 不需要关注具体路径。状态文件只写入宿主本地目录，不写入仓库。

## 1. bootstrap-state.json

用于表达 setup 结果与当前运行时的对应关系，推荐结构：

```json
{
  "skill_name": "remote",
  "sshpass_installed": false,
  "sshpass_version": "none",
  "sshpass_provider": "none",
  "auth_mechanism": "ssh_askpass",
  "ssh_installed": true,
  "ssh_version": "10.2",
  "os_type": "windows",
  "runtime_type": "windows-msys",
  "bash_available": true,
  "bash_flavor": "msys",
  "bash_path": "C:/Program Files/Git/bin/bash.exe",
  "windows_remote_ready": true,
  "last_setup_at": "2026-04-09T12:00:00+08:00",
  "last_verified_at": "2026-04-09T12:00:00+08:00"
}
```

Linux/macOS 示例：

```json
{
  "skill_name": "remote",
  "sshpass_installed": true,
  "sshpass_version": "1.10",
  "sshpass_provider": "linux",
  "auth_mechanism": "sshpass",
  "ssh_installed": true,
  "os_type": "linux",
  "runtime_type": "linux-wsl",
  "bash_available": true,
  "bash_flavor": "wsl",
  "bash_path": "/usr/bin/bash",
  "windows_remote_ready": false,
  "last_setup_at": "2026-04-09T12:00:00+08:00",
  "last_verified_at": "2026-04-09T12:00:00+08:00"
}
```

约束：

- 只表达安装与验证结果
- 不保存服务器业务数据
- 文件编码统一为无 BOM UTF-8；读取端需要兼容历史 BOM 文件
- `auth_mechanism` 允许值：`"ssh_askpass"`（Windows）、`"sshpass"`（Linux/macOS/WSL）
- `ssh_installed` 为布尔值，表示 SSH 客户端是否可用
- `ssh_version` 允许为 `"unknown"`
- `sshpass_version` 在 Windows 下固定为 `"none"`
- `runtime_type` 允许值：
  - `windows-msys`
  - `linux-wsl`
  - `linux-native`
  - `macos-native`
- `bash_flavor` 允许值：
  - `wsl`
  - `msys`
  - `native`
  - `unknown`
- `sshpass_provider` 允许值：
  - `linux`
  - `none`
  - `unknown`
- `runtime_type` 与其他字段的映射固定如下：
  - `windows-msys` -> `os_type=windows`、`bash_flavor=msys`、`sshpass_provider=none`、`auth_mechanism=ssh_askpass`
  - `linux-wsl` -> `os_type=linux`、`bash_flavor=wsl`、`sshpass_provider=linux`、`auth_mechanism=sshpass`
  - `linux-native` -> `os_type=linux`、`bash_flavor=native`、`sshpass_provider=linux`、`auth_mechanism=sshpass`
  - `macos-native` -> `os_type=macos`、`bash_flavor=native`、`sshpass_provider=linux`、`auth_mechanism=sshpass`
- 当 `bash_flavor=msys` 时，`auth_mechanism` 必须是 `ssh_askpass`
- 当 `bash_flavor=wsl` 或 `native` 时，`auth_mechanism` 必须是 `sshpass`
- 当前执行环境与状态文件不一致时，状态视为过期，需要重新按真实环境复核

## 2. servers.json

用于保存服务器连接信息，推荐结构：

```json
{
  "skill_name": "remote",
  "updated_at": "2026-04-09T12:00:00+08:00",
  "servers": [
    {
      "server_id": "10.0.0.8:22",
      "address": "10.0.0.8",
      "port": 22,
      "username": "root",
      "password": "secret",
      "last_verified_at": "2026-04-09T12:00:00+08:00",
      "last_error": "",
      "updated_at": "2026-04-09T12:00:00+08:00"
    }
  ]
}
```

约束：

- `server_id` 固定使用 `address:port`
- 端口默认 `22`
- 文件编码统一为无 BOM UTF-8；读取端需要兼容历史 BOM 文件
- 用户修改任一服务器信息后，立即更新本地记录
- 登录失败后，允许把失败信息写入 `last_error`
- 本 skill 属于内部 skill，允许在宿主本地状态目录明文保存密码
- 凭据内容不得写入仓库或 `.work`
