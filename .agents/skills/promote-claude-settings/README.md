# promote-claude-settings

Interactively promote entries from a project's `.claude/settings.local.json` into the global `~/.claude/settings.json`.

## Usage

Invoke with `/promote-claude-settings` or say "promote settings" in conversation.

## What it does

1. Reads both the project-local and global settings files
2. Shows a diff summary (new / exists / conflict)
3. Walks through each entry for confirmation
4. For each entry, evaluates whether the value contains project-specific narrowing (relative paths, absolute paths, project-specific names) and suggests broadening before promoting to global
5. Writes approved changes to `~/.claude/settings.json`
5. Optionally cleans up the local file

## Installation

```bash
npx skills add shihyuho/skills --skill promote-claude-settings -g
```

## Scope

- Handles all top-level keys (`permissions`, `env`, `hooks`, `enabledPlugins`, etc.)
- Array values (e.g. `permissions.allow`) are compared per-element
- Does not touch `.claude/settings.json` (project shared settings)
- No scripts — Claude handles JSON diffing and editing in conversation
