---
name: bot-process-control
description: Gmail Commander daemon lifecycle - start, stop, restart, status, logs, launchd plist management. TRIGGERS - bot start, bot stop, bot restart, bot status, bot logs, launchd, daemon, process control, gmail-commander service.
allowed-tools: Read, Bash, Grep, Glob
---

# Bot Process Control

Manage the Gmail Commander bot daemon and scheduled digest via launchd.

> **Self-Evolving Skill**: This skill improves through use. If instructions are wrong, parameters drifted, or a workaround was needed — fix this file immediately, don't defer. Only update for real, reproducible issues.

## Mandatory Preflight

### Step 1: Check Current Process Status

```bash
echo "=== Gmail Commander Processes ==="
pgrep -fl "gmail-commander" 2>/dev/null || echo "No processes found"

echo ""
echo "=== launchd Status ==="
launchctl list | grep gmail-commander 2>/dev/null || echo "No launchd jobs"

echo ""
echo "=== PID Files ==="
cat /tmp/gmail-commander-bot.pid 2>/dev/null && echo " (bot)" || echo "No bot PID file"
cat /tmp/gmail-digest.pid 2>/dev/null && echo " (digest)" || echo "No digest PID file"
```

## Two Services

| Service    | Type          | Trigger                    | PID File                     |
| ---------- | ------------- | -------------------------- | ---------------------------- |
| Bot Daemon | KeepAlive     | Always-on (grammY polling) | /tmp/gmail-commander-bot.pid |
| Digest     | StartInterval | Every 6 hours (21600s)     | /tmp/gmail-digest.pid        |

## launchd Plist Templates

### Bot Daemon — `com.terryli.gmail-commander-bot.plist`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.terryli.gmail-commander-bot</string>
    <key>ProgramArguments</key>
    <array>
        <string>{{HOME}}/own/amonic/bin/gmail-commander-bot</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <dict>
        <key>NetworkState</key>
        <true/>
    </dict>
    <key>StandardOutPath</key>
    <string>{{HOME}}/.local/state/launchd-logs/gmail-commander-bot/stdout.log</string>
    <key>StandardErrorPath</key>
    <string>{{HOME}}/.local/state/launchd-logs/gmail-commander-bot/stderr.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>{{HOME}}/.local/share/mise/shims:/usr/local/bin:/usr/bin:/bin</string>
    </dict>
    <key>ThrottleInterval</key>
    <integer>10</integer>
</dict>
</plist>
```

### Scheduled Digest — `com.terryli.gmail-commander-digest.plist`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.terryli.gmail-commander-digest</string>
    <key>ProgramArguments</key>
    <array>
        <string>{{HOME}}/own/amonic/bin/gmail-commander-digest</string>
    </array>
    <key>StartInterval</key>
    <integer>21600</integer>
    <key>StandardOutPath</key>
    <string>{{HOME}}/.local/state/launchd-logs/gmail-commander-digest/stdout.log</string>
    <key>StandardErrorPath</key>
    <string>{{HOME}}/.local/state/launchd-logs/gmail-commander-digest/stderr.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>{{HOME}}/.local/share/mise/shims:/usr/local/bin:/usr/bin:/bin</string>
    </dict>
</dict>
</plist>
```

## Quick Operations

### Start Bot

```bash
launchctl load ~/Library/LaunchAgents/com.terryli.gmail-commander-bot.plist
```

### Stop Bot

```bash
launchctl unload ~/Library/LaunchAgents/com.terryli.gmail-commander-bot.plist
```

### Restart Bot

```bash
launchctl unload ~/Library/LaunchAgents/com.terryli.gmail-commander-bot.plist
launchctl load ~/Library/LaunchAgents/com.terryli.gmail-commander-bot.plist
```

### Force Kill (Emergency)

```bash
pkill -f "gmail-commander.*bot.ts"
rm -f /tmp/gmail-commander-bot.pid
```

### View Logs

```bash
# Recent bot output (centralized launchd logs)
tail -50 ~/.local/state/launchd-logs/gmail-commander-bot/stderr.log

# Recent digest output
tail -50 ~/.local/state/launchd-logs/gmail-commander-digest/stderr.log

# Audit log (NDJSON, app-managed)
cat $PROJECT_DIR/logs/audit/$(date +%Y-%m-%d).ndjson | jq .

# OAuth token refresher log
tail -20 ~/.local/state/launchd-logs/gmail-oauth-refresher/stderr.log
```

## System Resources (Expected)

- **Memory**: ~20-30 MB RSS (Bun runtime + grammY)
- **CPU**: Negligible (idle polling, wakes on message)
- **Network**: Minimal (single long-poll connection to Telegram API)
- **Disk**: ~1 MB/day audit logs (14-day rotation)

## Telegram Commands

| Command  | Description                         |
| -------- | ----------------------------------- |
| /inbox   | Show recent inbox emails            |
| /search  | Search emails (Gmail query syntax)  |
| /read    | Read email by ID                    |
| /compose | Compose a new email                 |
| /reply   | Reply to an email                   |
| /abort   | Cancel current compose/reply action |
| /drafts  | List draft emails                   |
| /digest  | Run email digest now                |
| /status  | Bot status and stats                |
| /help    | Show all commands                   |

> **Note**: `/abort` cancels any in-progress compose or reply session. Works at any step in the flow.

## OAuth Token Management

### Two-Layer Token Architecture

```
Browser Auth (one-time, interactive)
  → Google issues: access_token (1h TTL) + refresh_token (7d TTL in Testing mode)
  → Saved to: ~/.claude/tools/gmail-tokens/<GMAIL_OP_UUID>.json

Silent Refresh (automatic, no browser)
  → Uses refresh_token to get new access_token
  → Fails with invalid_grant when refresh_token itself expires
```

### Hourly Token Refresher (launchd)

A compiled Swift binary runs hourly to proactively refresh the access token:

| File   | Path                                                                            |
| ------ | ------------------------------------------------------------------------------- |
| Source | `~/.claude/automation/gmail-token-refresher/main.swift`                         |
| Binary | `~/.claude/automation/gmail-token-refresher/gmail-oauth-token-hourly-refresher` |
| Plist  | `~/Library/LaunchAgents/com.terryli.gmail-oauth-token-hourly-refresher.plist`   |
| Log    | `$PROJECT_DIR/logs/token-refresher.log`                                         |

**Why hourly**: Access tokens expire every 1 hour. Refreshing hourly keeps the token perpetually valid. Frequent refresh also increases the chance Google issues a new `refresh_token`, resetting its 7-day clock.

**Verify it's running**:

```bash
launchctl list | grep gmail-oauth-token
tail -5 $PROJECT_DIR/logs/token-refresher.log
```

**Credentials source**: `GMAIL_OP_UUID` item in 1Password Claude Automation vault (fields: `client_id`, `client_secret`). Accessed via service account token — no biometric prompt required.

### Diagnosing `invalid_grant`

`invalid_grant` means the **refresh token** itself expired (not just the access token):

```bash
# Symptom in audit log:
cat $PROJECT_DIR/logs/audit/$(date +%Y-%m-%d).ndjson | jq 'select(.event == "gmail.error")'
# → "Token expired, refreshing...\nError: invalid_grant\n"

# Check token file age:
ls -la ~/.claude/tools/gmail-tokens/<GMAIL_OP_UUID>.json
```

**Fix**:

```bash
# 1. Delete expired token
rm ~/.claude/tools/gmail-tokens/<GMAIL_OP_UUID>.json

# 2. Trigger browser re-auth (opens Google consent page)
source $PROJECT_DIR/.env.launchd
$PLUGIN_DIR/scripts/gmail-cli/gmail list -n 1

# 3. Restart bot
launchctl unload ~/Library/LaunchAgents/com.terryli.gmail-commander-bot.plist
launchctl load ~/Library/LaunchAgents/com.terryli.gmail-commander-bot.plist
```

**Root cause**: Google OAuth apps in **Testing mode** issue refresh tokens with 7-day TTL. Permanent fix: publish the Google Cloud OAuth app (Google Cloud Console → OAuth consent screen → Publish app).

### Diagnosing Stale PID Lock

If the bot exits uncleanly, the PID file may block restart:

```bash
# Symptom: launchctl shows bot loaded but PID is dead
kill -0 $(cat /tmp/gmail-commander-bot.pid) 2>&1
# → "No such process"

# Fix: restart via launchctl (acquireLock handles stale PIDs automatically)
launchctl unload ~/Library/LaunchAgents/com.terryli.gmail-commander-bot.plist
launchctl load ~/Library/LaunchAgents/com.terryli.gmail-commander-bot.plist
```

## Post-Change Checklist

- [ ] YAML frontmatter valid (no colons in description)
- [ ] Trigger keywords current
- [ ] Path patterns use $HOME not hardcoded paths
- [ ] launchd plist templates match actual launcher scripts
- [ ] OAuth token refresher launchd service loaded and running


## Post-Execution Reflection

After this skill completes, reflect before closing the task:

0. **Locate yourself.** — Find this SKILL.md's canonical path before editing.
1. **What failed?** — Fix the instruction that caused it.
2. **What worked better than expected?** — Promote to recommended practice.
3. **What drifted?** — Fix any script, reference, or dependency that no longer matches reality.
4. **Log it.** — Evolution-log entry with trigger, fix, and evidence.

Do NOT defer. The next invocation inherits whatever you leave behind.
