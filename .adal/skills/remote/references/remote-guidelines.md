# Remote 工作规范

## 必须遵守

- 先理解用户意图，不机械照抄命令
- 默认只做读取、诊断、检查
- 涉及写操作、重启、删除、停服务、改配置时必须先征求用户确认
- 诊断类任务首轮不要用 `grep`、`head`、`tail` 预过滤
- 多维采集优先并行执行
- 信息不全时不要直接下结论
- 远程命令必须走标准主链：Windows 用 `remote.ps1`，其他系统用 `remote.sh`
- 不要手工执行 `sshpass ... ssh ...`（仅适用于 Linux/macOS）
- 连接失败后不要依次切换 `sshpass -k`、`sshpass -e`、`sshpass -p` 试错
- `Permission denied` 只能先解释为“远端拒绝了密码认证”

## 推荐执行方式

### 单命令

```bash
./skills/remote/scripts/remote.sh "10.0.0.8" "hostname && whoami"
```

Windows 示例：

```powershell
.\skills\remote\scripts\remote.ps1 -Address "10.0.0.8" -Username root -Password "secret" -Command "hostname && whoami"
```

补充要求：

- `windows-msys` 下使用 `SSH_ASKPASS` 机制自动提供密码，保持纯非交互
- 凭据无效时应直接返回失败诊断，不能依赖人工输入密码继续执行

### 并行多命令

```bash
./skills/remote/scripts/remote.sh --parallel "10.0.0.8" \
  "uptime" \
  "free -h" \
  "df -h"
```

### 调试模式

```bash
./skills/remote/scripts/remote.sh --parallel -v "10.0.0.8" \
  "uptime" \
  "free -h"
```

## 常见诊断模板

### 系统健康检查

```bash
./skills/remote/scripts/remote.sh --parallel "10.0.0.8" \
  "uptime && free -h && df -h" \
  "ps aux --sort=-%cpu | head -20" \
  "ps aux --sort=-%mem | head -20" \
  "systemctl list-units --failed" \
  "dmesg | tail -50"
```

### 磁盘空间检查

```bash
./skills/remote/scripts/remote.sh --parallel "10.0.0.8" \
  "df -h && df -i" \
  "du -sh /* 2>/dev/null | sort -hr | head -20" \
  "lsblk -o NAME,SIZE,TYPE,MOUNTPOINT,FSUSE%"
```

### 网络检查

```bash
./skills/remote/scripts/remote.sh --parallel "10.0.0.8" \
  "ss -tunlp && ss -s" \
  "ip addr show && ip route show" \
  "netstat -i"
```
