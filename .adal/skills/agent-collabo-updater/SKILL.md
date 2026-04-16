---
name: agent-collabo-updater
description: >
  Update locally installed agent-collabo skills to the latest version.
  Compares installed skills (both global and project scope) against the
  remote manifest and applies the minimal set of add/remove operations:
  updates changed skills, removes deprecated ones, and renames skills
  whose names changed. Detects installation scope automatically and
  notifies the user about session restart for new slash commands.
  "update agent-collabo", "agent collabo updater", "스킬 업데이트", "업데이트 적용",
  "apply skill updates", "sync agent-collabo skills",
  Use when other agent-collabo skills notify you of available updates,
  or when you want to manually pull the latest skill versions.
metadata:
  author: dev-goraebap
  version: "0.6.5"
---
<!-- AUTO-GENERATED - DO NOT EDIT DIRECTLY. Edit src/ instead. -->

# agent-collabo-updater

Apply pending updates from the agent-collabo manifest to your locally installed skills. Handles updates, removals, and renames in one workflow, scoped to whichever installations exist (global, project, or both).

This skill replaces raw `npx skills` command suggestions in other skill guardrails — when another agent-collabo skill detects a newer version available, it tells you to run `/agent-collabo-updater` instead of memorizing CLI flags.

## Guardrails

| # | Check | On failure |
|---|-------|------------|
| 1 | Network reachable to `raw.githubusercontent.com` | "Cannot fetch manifest. Check your network and retry." |
| 2 | At least one agent-collabo skill is installed locally (global or project) | "agent-collabo is not installed in this environment. To install: `npx skills add dev-goraebap/agent-collabo --all -g -y` (global) or `npx skills add dev-goraebap/agent-collabo --all -y` (current project)." |

## Language Policy

Conduct all user-facing communication in the user's language: interview questions, follow-up prompts, status messages, diagnostic reports, and summaries. Detect the language from (in order):

1. The language of the user's most recent messages in the current session
2. Declarations in their local rules file (e.g., `CLAUDE.local.md`, `.cursor/rules/local.mdc`) — look for instructions like "respond in Korean"
3. OS locale (`$LANG`, `$LC_ALL`)
4. English as fallback

Generated file content follows the file's audience: team-shared files (`AGENTS.md`, `CHANGELOG.md`) stay in English regardless of the user's language; personal files (`CLAUDE.local.md`, `GEMINI.local.md`, etc.) use the user's language unless they specify otherwise.

## Workflow

### Step 1: Fetch the remote manifest

Fetch `https://raw.githubusercontent.com/dev-goraebap/agent-collabo/main/manifest.json`. Parse `version`, `skills`, and `deprecated`. On network failure, stop with the guardrail message.

### Step 2: Detect locally installed agent-collabo skills

Scan **both scopes**. agent-collabo can be installed globally, in the current project, or both — you must check both independently.

**Global scope:**

1. Read `~/.agents/.skill-lock.json` (skip if missing — means no global skills are tracked).
2. Filter entries where `source === "dev-goraebap/agent-collabo"`.
3. For each match, read the skill's SKILL.md (`~/.agents/skills/<name>/SKILL.md` or the path indicated by the lock entry) and parse `metadata.version` from the frontmatter.

**Project scope:**

1. List directories under `<cwd>/.agents/skills/` (skip if missing).
2. For each candidate, read `<cwd>/.agents/skills/<name>/SKILL.md` and parse the frontmatter. Treat it as agent-collabo if `metadata.author === "dev-goraebap"`. (Project installs do not track source repo, so the author field is the most reliable signal.)
3. Parse `metadata.version`.

Build a flat list:

```
[
  { scope: "global",  name: "audit-rules",  version: "0.5.1" },
  { scope: "project", name: "init-public-rules", version: "0.5.0" },
  ...
]
```

If both lists are empty, exit via Guardrail #2.

### Step 3: Classify each installed skill

For each entry, compare against the remote manifest:

| Condition | Action | Notes |
|-----------|--------|-------|
| `name in manifest.skills` and `version === manifest.skills[name]` | **skip** | Already up to date |
| `name in manifest.skills` and `version < manifest.skills[name]` | **update** | Reinstall with `npx skills add ... --skill <name>` |
| `name in manifest.deprecated` | **rename** | Remove old name, install `manifest.deprecated[name].renamedTo` |
| `name not in manifest.skills` and `name not in manifest.deprecated` | **remove** | Skill is no longer maintained |

Also check: skills present in `manifest.skills` but missing locally → mark as **new (opt-in)**. Do not auto-install, but **do present them as install candidates in the same interview** so the user can opt in without a separate round-trip. The user might have intentionally excluded a skill, so the default is to leave it uninstalled — but the choice should live in the same flow as updates, not in a follow-up step.

For each new skill, fetch a one-sentence summary from the remote SKILL.md frontmatter (`description` field, first sentence) so the user has enough context to decide. If the frontmatter cannot be fetched cheaply, fall back to just the skill name and version.

The "scope" of a new skill install needs an explicit choice. If both global and project scopes have agent-collabo installations, ask which scope to install the new skill into (default: same scope as the majority of currently-installed agent-collabo skills). If only one scope exists, use that scope without asking.

### Step 4: Present a friendly summary and run a single interview

Show the summary in the user's language (per Language Policy). Group by action and scope, then ask **one** interview question that covers updates, renames, removals, and new-skill opt-in together — never split across multiple round-trips.

Example template (translate at runtime):

```
agent-collabo v{remote.version} is available.

Updates (5) — all global:
  - audit-rules: 0.6.0 -> 0.7.0
  - init-private-rules: 0.6.0 -> 0.6.1
  - init-public-rules: 0.6.0 -> 0.6.1
  - migrate-rules: 0.6.0 -> 0.6.1
  - agent-collabo-updater: 0.6.0 -> 0.6.1

Renames (1):
  - review-rules -> audit-rules  (since 0.3.0)  [global]

No longer maintained (1):
  - old-skill  [global]

New skills available (1):
  - example-skill (0.1.0)
    One-sentence description fetched from the remote SKILL.md frontmatter.

How would you like to proceed?
```

Then offer the choices below. Adapt the menu to what is actually present:

**Case A — there are new skills (any count):**

```
  1. Apply updates / renames / removes only (skip new skills)
  2. Apply everything (updates + install all new skills)
  3. Apply updates + choose new skills individually
  4. Cancel
```

If only **one** new skill is available, hide option 3 — option 2 already covers it. If **multiple** new skills are available, keep option 3 so the user can pick a subset.

**Case B — no new skills (current behavior preserved):**

```
  1. Apply (proceed with updates / renames / removes)
  2. Cancel
```

**Case C — nothing to do at all:**

Print "All skills are up to date." and exit. No interview.

**If the user picks option 3 (individual selection):** ask once for the subset, accepting either index numbers (`1, 3`), skill names (`example-skill, foo-skill`), or "all" / "none". Validate the input and proceed.

The selected new skills are added to the operation set built in Step 5 — they go into the same `npx skills add` command alongside updates, so there is exactly one CLI invocation per scope.

If the user declines (cancel / option N), exit gracefully without running anything.

### Step 5: Execute actions, grouped by scope

Build a minimal set of `npx skills` commands. **Crucial: `-g` is a scope switch, not a global-only flag.** Same command without `-g` operates on the current project.

For each scope (global, project), if there are any operations:

**Adds and updates** (combine update + new-name from rename + opt-in new skills selected in Step 4):
```bash
# Global
npx skills add dev-goraebap/agent-collabo --skill <name1> --skill <name2> -g -y

# Project (run from cwd)
npx skills add dev-goraebap/agent-collabo --skill <name1> --skill <name2> -y
```

**Removes** (combine rename old-name + deprecated):
```bash
# Global
npx skills remove <oldName1> <oldName2> -g -y

# Project
npx skills remove <oldName1> <oldName2> -y
```

Run each command via the Bash tool. Capture stdout/stderr and report any failures inline.

If a scope has no operations, do not run a command for it.

### Step 6: Result report and session restart notice

Show a summary of what was done (translate at runtime per Language Policy):

```
Done.
  - Updated: audit-rules, migrate-rules
  - Renamed: review-rules -> audit-rules
  - Removed: old-skill

IMPORTANT
  Newly added or renamed slash commands (e.g. /audit-rules) are not picked
  up by the current session. Claude Code, Cursor, and most agents load
  the skill list only at session start.

  -> End the current conversation and start a new session to use them.
```

Always print the restart notice if any add or rename action ran. Skip it if only removes happened (removal doesn't introduce a new slash command).

## Notes

- This skill **does not** include the update-check guardrail that other agent-collabo skills use as their first guardrail row — it would create an infinite loop (the updater checking for an update of itself before running). Updater self-updates happen via the same flow when other skills trigger it.
- The updater never edits the `agent-collabo` source repo — it only operates on installed copies under `~/.agents/skills/` or `<cwd>/.agents/skills/`.
- Manifest format compatibility: this updater expects the v1 manifest schema (`{ version, repository, skills, deprecated }`). If a future manifest version arrives that this updater cannot parse, it should print an error and ask the user to upgrade the updater itself first.
