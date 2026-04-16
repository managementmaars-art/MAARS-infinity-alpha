# send-feishu Usage Examples

## Setup

### 1. Configure Environment Variables

Add to `~/.zshrc` or `~/.bashrc`:

```bash
# Required for webhook sends (text/card to group)
export FEISHU_WEBHOOK="https://open.feishu.cn/open-apis/bot/v2/hook/YOUR-TOKEN"

# Required for API sends (images, files, or to individuals)
export FEISHU_APP_ID="cli_xxxx"
export FEISHU_APP_SECRET="secret_xxxx"

# Required when sending to a group via API
export FEISHU_CHAT_ID="oc_xxxx"

# Optional: for sending to yourself
export FEISHU_USER_OPEN_ID="ou_xxxx"

# Optional: if webhook has signature verification enabled
export FEISHU_WEBHOOK_SECRET="secret_xxxx"
```

### 2. Locate the Script

```bash
FEISHU_SEND="$(find ~/.claude/plugins -name 'send-feishu' -path '*/skills/*' -type d 2>/dev/null)/scripts/feishu-send"
```

Or from local development:
```bash
FEISHU_SEND="./skills/productivity/send-feishu/scripts/feishu-send"
```

## Examples

### Text Message

```bash
"$FEISHU_SEND" text "Deploy completed successfully! 🚀"

# To a group (API)
FEISHU_CHAT_ID="oc_xxx" "$FEISHU_SEND" text "Hello group"

# To yourself
FEISHU_USER_OPEN_ID="ou_xxx" "$FEISHU_SEND" text "Reminder: check PR queue"
```

### Card Message

```bash
# Success notification (green)
"$FEISHU_SEND" card "Deployment Status" "Production release v1.2.3 is live" --color green

# Warning (orange)
"$FEISHU_SEND" card "Memory Alert" "Staging server using 87% RAM" --color orange

# Error (red)
"$FEISHU_SEND" card "Build Failed" "GitHub Actions pipeline failed on main branch" --color red

# Info (blue, default)
"$FEISHU_SEND" card "Daily Report" "See attached spreadsheet for details"

# Special (purple)
"$FEISHU_SEND" card "🎉 Launch Day" "Feature X is now available to all users" --color purple
```

Cards support **lark_md** formatting in the body:
```bash
BODY="**Bold text**
*Italic text*
~~Strikethrough~~
[Link](https://example.com)"

"$FEISHU_SEND" card "Formatted Card" "$BODY" --color blue
```

### Image

```bash
# Screenshot or chart
"$FEISHU_SEND" image /path/to/screenshot.png

# Requires FEISHU_APP_ID + FEISHU_APP_SECRET
"$FEISHU_SEND" image ~/Desktop/architecture-diagram.png
```

### File

```bash
# Markdown report
"$FEISHU_SEND" file /path/to/report.md

# PDF, spreadsheet, document
"$FEISHU_SEND" file ~/downloads/metrics.xlsx
"$FEISHU_SEND" file ./deployment-log.pdf

# Requires FEISHU_APP_ID + FEISHU_APP_SECRET
```

## Dry-Run (Test without Sending)

```bash
# Verify environment variables are resolved
"$FEISHU_SEND" --dry-run text "test message"

# Output:
# [feishu-send] === Dry-run: resolved variables ===
# [feishu-send]   APP_ID     = cli_a92b***
# [feishu-send]   CHAT_ID    = oc_4851c***
# [feishu-send]   WEBHOOK    = https://***
# [feishu-send] === Dry-run: would send type='text'
# [feishu-send]   message='test message'
# [feishu-send] === Dry-run complete (no network requests made) ===
```

## Routing Behavior

The script automatically selects the best method based on available credentials:

| Need | Config | Method |
|------|--------|--------|
| Text to group | WEBHOOK | Webhook (fast) |
| Text to group | CHAT_ID + APP_ID | API (flexible) |
| Card to group | WEBHOOK | Webhook (recommended) |
| Card to group | CHAT_ID + APP_ID | API |
| Image to group | any + APP_ID | Upload + API |
| File to group | CHAT_ID + APP_ID | Upload + API |
| Anything to person | OPEN_ID + APP_ID | API |

## Error Messages

### Missing Credentials

```
ERROR: FEISHU_WEBHOOK not set
```
→ Set `FEISHU_WEBHOOK` in environment or pass via hook configuration

### Upload Failed

```
Image upload failed: {"code":99991663,"msg":"invalid token"}
```
→ Token expired; `FEISHU_APP_SECRET` may be wrong

### Bot Not in Chat

```
Send failed (230001): bot not in chat or no permission
```
→ Add the bot to the Feishu group first

### Special Characters

If message contains `$`, `"`, `\n`, or backslashes — the script handles them safely via environment variables.

## Integration with Claude Code Skills

Use in other skills:

```bash
# In a skill script
SKILL_DIR="$(find ~/.claude/plugins -name 'send-feishu' -path '*/skills/*' -type d)"
FEISHU_SEND="${SKILL_DIR}/scripts/feishu-send"

"$FEISHU_SEND" text "Analysis complete!"
"$FEISHU_SEND" card "Report" "$(cat report.md)" --color blue
"$FEISHU_SEND" file "/tmp/results.json"
```

## Troubleshooting

**Nothing happens (silent failure)**
→ Run dry-run first: `"$FEISHU_SEND" --dry-run text "test"`

**"command not found" or "No such file"**
→ Verify `$FEISHU_SEND` is set and executable

**Timeout**
→ Check internet connectivity, webhook/API endpoint reachability

**Emoji not showing**
→ Some Feishu clients may not render all emoji; fallback to text description
