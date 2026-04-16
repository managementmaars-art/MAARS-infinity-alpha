---
name: chezmoi-sync
description: Interactive chezmoi drift check and sync. TRIGGERS - chezmoi sync, sync dotfiles, dotfile drift, chezmoi guard, chezmoi check.
allowed-tools: Read, Edit, Bash, AskUserQuestion
---

# Chezmoi Sync (Interactive)

On-demand replacement for the automatic chezmoi stop guard. Run this skill whenever you want to check for chezmoi drift and sync tracked dotfiles.

> **Self-Evolving Skill**: This skill improves through use. If instructions are wrong, parameters drifted, or a workaround was needed — fix this file immediately, don't defer. Only update for real, reproducible issues.

## Workflow

### Step 1: Check for drift

Run `chezmoi status` and `chezmoi diff --no-pager` to detect drift between the source repo and home directory.

```bash
chezmoi source-path && chezmoi status && echo "---" && chezmoi diff --no-pager | head -80
```

If output is empty (no drift), report "Chezmoi is clean — no drift detected" and stop.

### Step 2: Present drift to user (AskUserQuestion)

If drift exists, use `AskUserQuestion` to show the user what drifted and ask what to do.

**Question 1** (header: "Drift action"):

> "Chezmoi detected N drifted file(s): [list files]. What would you like to do?"

Options:

- **Sync all** — `chezmoi re-add` all drifted files, commit, and push
- **Review each** — Walk through each file individually with per-file choices
- **Ignore** — Skip sync, I'll handle it later

### Step 3a: Sync all (if chosen)

```bash
chezmoi re-add --verbose
chezmoi git -- add -A && chezmoi git -- commit -m "sync: dotfiles" && chezmoi git -- push
chezmoi status  # Verify clean
```

Report the commit hash and confirm clean state.

### Step 3b: Review each (if chosen)

For each drifted file, use `AskUserQuestion`:

**Question** (header: "File action"):

> "[filename] has changed. What should we do?"

Options:

- **Sync** — Add this file to chezmoi source (`chezmoi add <path>`)
- **Diff** — Show the full diff first, then ask again
- **Forget** — Stop tracking this file (`chezmoi forget --force <path>`)
- **Skip** — Leave it drifted for now

After processing all files, if any were synced:

```bash
chezmoi git -- add -A && chezmoi git -- commit -m "sync: dotfiles" && chezmoi git -- push
```

### Step 3c: Ignore (if chosen)

Report: "Skipped chezmoi sync. Run `/dotfiles-tools:chezmoi-sync` when ready."

## Notes

- Always use `chezmoi forget --force` (not bare `forget`) to avoid TTY prompt issues
- The chezmoi source dir is `~/own/dotfiles` (configured in `~/.config/chezmoi/chezmoi.toml`)


## Post-Execution Reflection

After this skill completes, reflect before closing the task:

0. **Locate yourself.** — Find this SKILL.md's canonical path before editing.
1. **What failed?** — Fix the instruction that caused it.
2. **What worked better than expected?** — Promote to recommended practice.
3. **What drifted?** — Fix any script, reference, or dependency that no longer matches reality.
4. **Log it.** — Evolution-log entry with trigger, fix, and evidence.

Do NOT defer. The next invocation inherits whatever you leave behind.
