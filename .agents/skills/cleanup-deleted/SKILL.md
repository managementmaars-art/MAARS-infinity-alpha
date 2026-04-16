---
name: cleanup-deleted
description: "Use when user wants to clean up Telegram by purging deleted or ghost accounts from their dialog list and contacts, or removing spam ghosts that clutter the chat list."
allowed-tools: Bash, Read, Grep, Glob
---

# Cleanup Deleted Telegram Accounts

Scan and purge deleted/ghost accounts from your Telegram dialog list and contacts. These are accounts that were deleted by their owners or banned by Telegram but still appear as "Deleted Account" in your chat list.

The script uses 3 progressively aggressive deletion methods because Telegram's dialog cache can be stubborn:

1. **delete_dialog** — standard removal
2. **DeleteHistoryRequest** — force-clear the conversation history
3. **Block + Unblock + delete** — resets Telegram's peer state cache, then deletes

After the first pass, it re-scans for survivors and retries with method 3.

> **Self-Evolving Skill**: This skill improves through use. If instructions are wrong, parameters drifted, or a workaround was needed — fix this file immediately, don't defer. Only update for real, reproducible issues.

## Preflight

1. Session must exist: `~/.local/share/telethon/<profile>.session`
   - If missing, run `/tlg:setup` first

## Usage

```bash
/usr/bin/env bash << 'EOF'
SCRIPT="${CLAUDE_PLUGIN_ROOT:-$HOME/.claude/plugins/marketplaces/cc-skills/plugins/tlg}/scripts/cleanup_deleted.py"

# Scan only (no deletions)
uv run --python 3.13 "$SCRIPT" --dry-run

# Clean all profiles
uv run --python 3.13 "$SCRIPT"

# Clean specific profile
uv run --python 3.13 "$SCRIPT" -p eon

# Clean multiple specific profiles
uv run --python 3.13 "$SCRIPT" -p eon missterryli
EOF
```

## Parameters

| Parameter      | Type | Description                      |
| -------------- | ---- | -------------------------------- |
| `-p/--profile` | list | Profiles to clean (default: all) |
| `--dry-run`    | flag | Scan and report without deleting |

## What Gets Cleaned

| Source                      | Action                                        |
| --------------------------- | --------------------------------------------- |
| Regular dialogs             | Deleted user chats removed                    |
| Archived dialogs (folder=1) | Deleted user chats removed                    |
| Contact list                | Deleted contacts removed                      |
| Stubborn ghosts             | Block+unblock forces cache reset, then delete |

## Recommended Cadence

Run monthly or whenever you notice "Deleted Account" entries appearing in your chat list. Spam accounts that message you and later get banned by Telegram are the primary source.

## Post-Execution Reflection

After this skill completes, check before closing:

1. **Did the command succeed?** — If not, fix the instruction or error table that caused the failure.
2. **Did parameters or output change?** — If tg-cli.py's interface drifted, update Usage examples and Parameters table to match.
3. **Was a workaround needed?** — If you had to improvise (different flags, extra steps), update this SKILL.md so the next invocation doesn't need the same workaround.

Only update if the issue is real and reproducible — not speculative.
