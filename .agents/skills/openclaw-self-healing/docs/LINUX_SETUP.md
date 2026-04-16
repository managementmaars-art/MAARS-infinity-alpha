# Linux Setup Guide (systemd)

> ✅ **Fully Supported** — User-level systemd, no `sudo` required.

## ⚡ One-Click Install (Recommended)

```bash
curl -sSL https://raw.githubusercontent.com/Ramsbaby/openclaw-self-healing/main/install-linux.sh | bash
```

Custom workspace:
```bash
curl -sSL https://raw.githubusercontent.com/Ramsbaby/openclaw-self-healing/main/install-linux.sh | bash -s -- --workspace ~/my-openclaw
```

The installer automatically:
- Detects your distro (Ubuntu/Debian/RHEL/Arch/etc.)
- Checks prerequisites (tmux, Claude CLI, OpenClaw, jq)
- Downloads scripts + sets permissions (chmod 700)
- Installs systemd user units (`~/.config/systemd/user/`)
- Enables lingering (services run without active login)
- Starts the healthcheck timer

## Supported Distros

| Distro | Package Manager | Tested |
|--------|----------------|--------|
| Ubuntu 20.04+ | apt | ✅ |
| Debian 11+ | apt | ✅ |
| Fedora / RHEL 8+ | dnf | ✅ |
| Arch / Manjaro | pacman | ✅ |
| Raspberry Pi OS | apt | ✅ |

## Prerequisites

```bash
# Ubuntu/Debian
sudo apt install -y tmux curl jq
npm install -g @anthropic-ai/claude-code

# Fedora/RHEL
sudo dnf install -y tmux curl jq
npm install -g @anthropic-ai/claude-code

# Arch
sudo pacman -S --noconfirm tmux curl jq
npm install -g @anthropic-ai/claude-code
```

OpenClaw must be installed: https://github.com/openclaw/openclaw

## Architecture (Linux)

```
~/.config/systemd/user/
├── openclaw-gateway.service         # Level 0: KeepAlive (Restart=always)
├── openclaw-healthcheck.service     # Level 2: Health Check (oneshot)
├── openclaw-healthcheck.timer       # Level 2: 5-minute interval trigger
└── openclaw-emergency-recovery.service  # Level 3: Claude Doctor (on-demand)
```

All services run as **user-level systemd units** — no root privileges needed.

### Key Difference from macOS

| macOS | Linux |
|-------|-------|
| `launchctl load/unload` | `systemctl --user enable/start` |
| `~/Library/LaunchAgents/*.plist` | `~/.config/systemd/user/*.service` |
| LaunchAgent KeepAlive | systemd `Restart=always` |
| `launchctl list` | `systemctl --user list-units` |

## Manual Installation

<details>
<summary>Click to expand</summary>

```bash
# 1. Create directories
mkdir -p ~/openclaw/scripts ~/.config/systemd/user

# 2. Download scripts
for script in gateway-healthcheck.sh emergency-recovery.sh emergency-recovery-monitor.sh; do
  curl -sSL "https://raw.githubusercontent.com/Ramsbaby/openclaw-self-healing/main/scripts/$script" \
    -o ~/openclaw/scripts/$script
  chmod 700 ~/openclaw/scripts/$script
done

# 3. Download systemd units
for unit in openclaw-gateway.service openclaw-healthcheck.service openclaw-healthcheck.timer openclaw-emergency-recovery.service; do
  curl -sSL "https://raw.githubusercontent.com/Ramsbaby/openclaw-self-healing/main/systemd/$unit" \
    -o ~/.config/systemd/user/$unit
done

# 4. Setup environment
cp ~/.openclaw/.env.example ~/.openclaw/.env  # or create manually
chmod 600 ~/.openclaw/.env

# 5. Enable lingering (services persist after logout)
loginctl enable-linger $USER

# 6. Reload and enable
systemctl --user daemon-reload
systemctl --user enable openclaw-gateway.service
systemctl --user enable --now openclaw-healthcheck.timer
```

</details>

## Useful Commands

```bash
# Check status
systemctl --user status openclaw-gateway
systemctl --user status openclaw-healthcheck.timer
systemctl --user list-timers

# View logs
journalctl --user -u openclaw-healthcheck -f
journalctl --user -u openclaw-gateway --since "1 hour ago"

# Manually trigger Level 3
systemctl --user start openclaw-emergency-recovery

# Restart gateway
systemctl --user restart openclaw-gateway

# Disable self-healing
systemctl --user stop openclaw-healthcheck.timer
systemctl --user disable openclaw-healthcheck.timer
```

## Troubleshooting

### Services don't start after reboot

Enable lingering:
```bash
sudo loginctl enable-linger $USER
```

### `openclaw` command not found in service

The systemd units include common PATH locations (`~/.local/bin`, `~/.nvm/versions/node/current/bin`, `/usr/local/bin`). If your `openclaw` is installed elsewhere, add its path to the unit file:

```bash
systemctl --user edit openclaw-gateway.service
# Add under [Service]:
# Environment=PATH=/your/custom/path:$PATH
```

### Health check logs

```bash
# View recent health check results
cat ~/openclaw/memory/healthcheck-$(date +%Y-%m-%d).log

# View metrics
cat ~/openclaw/memory/.healthcheck-metrics.json | tail -5
```

### Emergency recovery won't trigger

Check that tmux and Claude CLI are accessible:
```bash
which tmux    # Must return a path
which claude  # Must return a path
```

## Uninstall

```bash
systemctl --user stop openclaw-healthcheck.timer
systemctl --user stop openclaw-gateway
systemctl --user disable openclaw-gateway.service openclaw-healthcheck.timer
rm ~/.config/systemd/user/openclaw-*.service ~/.config/systemd/user/openclaw-*.timer
systemctl --user daemon-reload
```
