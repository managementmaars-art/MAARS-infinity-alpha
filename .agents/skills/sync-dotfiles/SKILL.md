---
name: sync-dotfiles
description: Sync user-level AI configs (~/.claude/, ~/.codex/) with the dotfiles/ directory. Use when dotfiles drift, after sessions that change permissions/hooks, on new machines, or when the user says "sync", "pull dotfiles", "push configs".
---

## When to invoke
- User says "sync dotfiles", "pull configs", "push configs", "check drift"
- After a session where permissions or hooks were modified
- On a new machine after cloning ai-env

## Subcommands
Map user intent to sync.sh subcommand:

| Intent | Command | What it does |
|--------|---------|-------------|
| "check what's different" | `sync.sh diff` | Show drift between repo and home |
| "what's tracked" | `sync.sh status` | Show file registry |
| "capture my local changes" | `sync.sh pull` | Home → repo (home wins) |
| "deploy repo configs" | `sync.sh push` | Repo → home (repo wins) |
| "install skills" | `sync.sh skills-push` | Install skills via npx |
| "sync" (ambiguous) | Show diff first, then ask direction | Safe default |

## Running sync.sh

The sync script is bundled with this skill at `sync.sh` (same directory as this SKILL.md).
Run it directly — the script discovers the ai-env repo automatically:

```bash
/path/to/skill/sync.sh <subcommand>
```

The script sets `AI_ENV_ROOT` automatically via the discovery chain below. To override:

```bash
AI_ENV_ROOT=/custom/path/to/ai-env /path/to/skill/sync.sh push
```

## AI_ENV_ROOT discovery
The script discovers the ai-env repo (where `dotfiles/` lives) automatically:
1. If `$AI_ENV_ROOT` is set and `$AI_ENV_ROOT/dotfiles` exists: use that
2. If the script is inside an ai-env git repo (e.g., running from a symlink): use that repo root
3. If `~/projects/camacho/ai-env` exists: use that
4. Clone `camacho/ai-env` to a temp dir via GitHub
5. If clone fails: error with instructions to set `AI_ENV_ROOT`

## After pull
Show `git diff dotfiles/` and offer to commit: `chore: sync dotfiles`

## After push
Run `sync.sh status` to confirm, warn about any missing files.
