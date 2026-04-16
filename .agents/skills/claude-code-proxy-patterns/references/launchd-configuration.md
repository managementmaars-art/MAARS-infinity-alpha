# Launchd Service Configuration

The Go proxy runs as a macOS launchd daemon for auto-restart on crash and boot persistence.

**Why launchd?**:

- Auto-restarts if proxy crashes
- Starts on system boot (RunAtLoad)
- Runs as root (needed for port 80/443 if ever needed)
- Resource limits can be enforced

**Plist Location**: `/Library/LaunchDaemons/com.terryli.claude-proxy.plist`

## Full Configuration

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <!-- Unique identifier -->
    <key>Label</key><string>com.terryli.claude-proxy</string>

    <!-- Program to run -->
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/claude-proxy</string>
    </array>

    <!-- Start on boot -->
    <key>RunAtLoad</key><true/>

    <!-- Auto-restart on crash (any non-zero exit) -->
    <key>KeepAlive</key>
    <dict>
        <key>SuccessfulExit</key><false/>
    </dict>

    <!-- Environment variables passed to the proxy -->
    <key>EnvironmentVariables</key>
    <dict>
        <key>PORT</key><string>8082</string>
        <key>HAIKU_PROVIDER_API_KEY</key><string>sk-cp-49GSmHBfC0c65pvYrFoZZy8xEjOVxXrUiTIJn65ynTvgzoiGEvM7q9V5dYYe6PwjMfZaGelKoE2oTq1hKnttv8ODm36O8gklUIi1eaTVOKbPILlIPfNcM0E</string>
        <key>HAIKU_PROVIDER_BASE_URL</key><string>https://api.minimax.io/anthropic</string>
        <key>ANTHROPIC_DEFAULT_HAIKU_MODEL</key><string>claude-haiku-4-5-20251001</string>
    </dict>

    <!-- Resource limits -->
    <key>SoftResourceLimits</key>
    <dict>
        <key>NumberOfFiles</key><integer>65536</integer>
    </dict>

    <!-- Log output -->
    <key>StandardOutPath</key><string>/Users/terryli/.claude/logs/proxy-stdout.log</string>
    <key>StandardErrorPath</key><string>/Users/terryli/.claude/logs/proxy-stderr.log</string>
</dict>
</plist>
```

## Key launchd Properties

| Key                                | Purpose            | Value for Proxy                                |
| ---------------------------------- | ------------------ | ---------------------------------------------- |
| `Label`                            | Unique identifier  | `com.terryli.claude-proxy`                     |
| `ProgramArguments`                 | Command + args     | `["/usr/local/bin/claude-proxy"]`              |
| `RunAtLoad`                        | Start at boot      | `true`                                         |
| `KeepAlive/SuccessfulExit`         | Restart on crash   | `false` (always restart)                       |
| `EnvironmentVariables`             | Env vars for proxy | PORT, API keys, etc.                           |
| `SoftResourceLimits/NumberOfFiles` | FD limit           | `65536`                                        |
| `StandardOutPath`                  | stdout log         | `/Users/terryli/.claude/logs/proxy-stdout.log` |
| `StandardErrorPath`                | stderr log         | `/Users/terryli/.claude/logs/proxy-stderr.log` |

## Commands

```bash
# Install plist (one-time)
sudo cp /path/to/com.terryli.claude-proxy.plist /Library/LaunchDaemons/
sudo chown root:wheel /Library/LaunchDaemons/com.terryli.claude-proxy.plist
sudo chmod 644 /Library/LaunchDaemons/com.terryli.claude-proxy.plist

# Start (load)
sudo launchctl load -w /Library/LaunchDaemons/com.terryli.claude-proxy.plist

# Stop (unload)
sudo launchctl unload -w /Library/LaunchDaemons/com.terryli.claude-proxy.plist

# Restart
sudo launchctl unload -w /Library/LaunchDaemons/com.terryli.claude-proxy.plist
sudo launchctl load -w /Library/LaunchDaemons/com.terryli.claude-proxy.plist

# Check status
sudo launchctl list | grep claude-proxy

# View running PID info
ps aux | grep claude-proxy

# View logs
tail -f /Users/terryli/.claude/logs/proxy-stdout.log
tail -f /Users/terryli/.claude/logs/proxy-stderr.log

# Test health
curl -s http://127.0.0.1:8082/health | jq .
```

## Verification Checklist

```bash
# 1. Plist exists
ls -la /Library/LaunchDaemons/com.terryli.claude-proxy.plist

# 2. Loaded in launchd
sudo launchctl list | grep claude-proxy

# 3. Process running
ps aux | grep claude-proxy | grep -v grep

# 4. Port listening
lsof -i :8082

# 5. Health endpoint responds
curl -s http://127.0.0.1:8082/health | jq .
```

## Debugging launchd Issues

```bash
# Check if plist is valid
plutil -lint /Library/LaunchDaemons/com.terryli.claude-proxy.plist

# View full launchd logs
log show --predicate 'process == "claude-proxy"' --last 5m

# Check stderr for errors
tail -50 /Users/terryli/.claude/logs/proxy-stderr.log
```
