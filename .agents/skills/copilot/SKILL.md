---
name: copilot
description: Enter copilot mode — human drives, Claude assists. Relaxes worktree enforcement, allows main commits.
user_invocable: true
---

# Enter Copilot Mode

> **Claude Code only** — Codex and Cursor sessions are always autonomous.

## Activate

```bash
.claude/hooks/activate-copilot.sh
```

If the script does not exist, tell the user: "This project doesn't have mode switching hooks. Install the ai-env template or add activate-copilot.sh manually."
If it fails for another reason, inform the user with the error message and stop.

## Confirmation

After activation, print:

```
Mode: copilot
Relaxed: worktree requirement, main branch protection
Workflow: menu mode — tell me to follow it or just lead
TTL: 4h sliding (renews on each prompt) / 12h absolute ceiling
```

## Behavior

Follow **copilot mode** rules in `.claude/rules/operating-mode.md`.
When the current task or plan completes, revert with `/autonomous`.
