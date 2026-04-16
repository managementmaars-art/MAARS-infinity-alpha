---
name: promote-claude-settings
description: Promote entries from the current project's .claude/settings.local.json into the global ~/.claude/settings.json. Use when user says "promote settings", "upgrade settings", "sync settings to global", "move local settings to global", or wants to move project-local Claude Code settings to global scope.
license: MIT
metadata:
  author: shihyuho
  version: "1.0.0"
---

# promote-claude-settings

Interactively promote entries from `.claude/settings.local.json` (project) to `~/.claude/settings.json` (global).

## Workflow

### 1. Read both files

- Read `.claude/settings.local.json` from the current project root
- Read `~/.claude/settings.json`
- If local file is missing or empty (`{}`), tell the user and stop

### 2. Diff

Compare every top-level key in local against global. For array values (e.g. `permissions.allow`), compare per-element, not the whole array.

Classify each entry:

| Status | Meaning |
|--------|---------|
| **New** | Not in global — can be added |
| **Exists** | Already identical in global — skip |
| **Conflict** | Present in global with a different value |

Present the full diff summary to the user before asking anything.

### 3. Interactive confirm (per item)

Walk through every non-"Exists" entry and ask:

- **New** → "Add to global? (Y/N)"
- **Conflict** → show both values, ask "Use local / Keep global / Skip"

Use the question tool for each prompt.

#### 3a. Scope generalization (local → global)

Local settings are often written with project-specific context. Before promoting **any** entry to global, evaluate whether it contains narrowing signals that won't make sense outside this project. If so, suggest a broader version.

**Common narrowing signals:**

- Relative paths (`./mvnw`, `./gradlew`, `./scripts/foo`)
- Absolute paths (`/Users/matt/project-x/...`)
- Project-specific directory or file names
- Overly specific subcommand locks that only apply to one project's workflow

**Examples:**

| Local value | Why it's too narrow | Suggested generalization |
|---|---|---|
| `Bash(./mvnw test:*)` | Relative path + subcommand lock | `Bash(*mvnw*)` |
| `Bash(./gradlew build:*)` | Relative path | `Bash(*gradlew*)` |
| `Bash(npx vitest:*)` | Already generic | Keep as-is |
| Hook command: `cd ./api && lint` | Relative path | Evaluate if hook makes sense globally |
| Env: `PROJECT_ROOT=/Users/matt/foo` | Absolute path | Likely should not be promoted |

**For each entry being promoted:**

1. **Detect** whether the value contains project-specific narrowing
2. **Suggest** a broader alternative with a brief rationale (or recommend skipping promotion if it doesn't make sense globally)
3. **Ask** the user: "Original: `X` → Suggested: `Y` — Use suggested version / Keep original / Custom?"
4. Use whichever version the user picks

If the value is already generic, skip this step for that entry.

### 4. Write to global

Apply confirmed changes to `~/.claude/settings.json` with the Edit tool. If the file does not exist, create it.

### 5. Cleanup confirm

If removing promoted entries would leave `settings.local.json` as `{}`, explain that the file is now effectively empty (`{}`) and ask whether to delete it entirely or keep the empty file. If the user chooses to keep it, leave the file as-is (do not remove entries).

If removing promoted entries would still leave other entries in the file, ask whether to remove the promoted entries.

## Edge cases

- `~/.claude/settings.json` missing → create with confirmed entries
- JSON parse error → report and stop; do not attempt repair
- Do NOT touch `.claude/settings.json` (project shared settings)
