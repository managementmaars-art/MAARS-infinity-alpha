---
name: send-feishu
description: Use when user says "发到飞书", "发送到飞书", "发送到飞书群", "飞书通知", "通知飞书", "feishu", "发给我", "私发飞书", or explicitly invokes /send-feishu to send messages, images, or files to Feishu group chat or individual via webhook or API
allowed-tools: Bash
---

# Send Feishu Message

The send logic is in `scripts/feishu-send` (bundled with this skill).

## Step 0 — Locate and prepare the script

```bash
# Find the script relative to where this skill is installed
SKILL_DIR="$(find ~/.claude/plugins -name 'send-feishu' -path '*/skills/*' -type d 2>/dev/null | head -1)"
FEISHU_SEND="${SKILL_DIR}/scripts/feishu-send"
chmod +x "$FEISHU_SEND" 2>/dev/null
echo "script: $FEISHU_SEND"
```

If the script is not found (e.g., skill loaded from local dev path), use:
```bash
FEISHU_SEND="$(dirname "$0")/scripts/feishu-send"
```

## Choose Format

| Situation | Format |
|-----------|--------|
| Simple one-liner, status update | `text` |
| Has title + body, structured data, report | `card` |
| Image file / screenshot / chart | `image` |
| .md / .html / .pdf / .doc / large content | `file` |
| User says "发给我" / "私发" / names a person | use `FEISHU_USER_OPEN_ID` |

Card color: `green`=success, `orange`=warning, `red`=error, `blue`=info (default), `purple`=highlight.

## Send

```bash
# Text
"$FEISHU_SEND" text "消息内容"

# Card
"$FEISHU_SEND" card "标题" "正文（支持 lark_md：**粗体** *斜体* \n换行）" --color blue

# Image
"$FEISHU_SEND" image /path/to/image.png

# File
"$FEISHU_SEND" file /path/to/report.md

# Dry-run (verify vars without sending)
"$FEISHU_SEND" --dry-run text "test"
```

The script handles: variable resolution (including `CTI_FEISHU_*` aliases) → routing → token acquisition → upload → send → error reporting.

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `FEISHU_WEBHOOK` | Group webhook URL |
| `FEISHU_APP_ID` + `FEISHU_APP_SECRET` | Required for image/file upload and API sends |
| `FEISHU_CHAT_ID` | Group chat ID (`oc_xxx`) |
| `FEISHU_USER_OPEN_ID` | Individual (`ou_xxx`) |
| `FEISHU_WEBHOOK_SECRET` | Only if webhook signature is enabled |

If vars are unset after resolution, tell user which ones to configure.
