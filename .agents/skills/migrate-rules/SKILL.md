---
name: migrate-rules
description: >
  Consolidate scattered agent config files (.cursorrules, CLAUDE.md,
  copilot-instructions.md, etc.) into an AGENTS.md-centered structure.
  Removes duplicates and converts existing files to bridges or cleans them up.
  "consolidate rules", "migrate rules", "clean up agent configs",
  "convert cursorrules to AGENTS.md", "merge rule files", "unify configs",
  Use when a project already has multiple agent config files and wants to
  switch to the AGENTS.md standard.
metadata:
  author: dev-goraebap
  version: "0.7.1"
---
<!-- AUTO-GENERATED - DO NOT EDIT DIRECTLY. Edit src/ instead. -->

# migrate-rules

Consolidate scattered agent config files into an **AGENTS.md-centered structure**. Remove duplicates and convert existing files to bridges or clean them up.

Most teams already have rules scattered across `.cursorrules`, `CLAUDE.md`, `.github/copilot-instructions.md`, and more. This skill provides a realistic path from that state to the AGENTS.md standard.

## Guard Rails

| # | Check | On Failure |
|---|-------|------------|
| 1 | CWD is a Git repository | "Please run inside a Git repository" |
| 2 | At least one agent config file exists | "No agent config files found. Use /init-public-rules to create one." |
| 3 | Only AGENTS.md exists, no other agent files | "Already consolidated into AGENTS.md. Run /audit-rules to verify quality." |
| - | Skill update check | **Session dedup**: if you have already fetched `manifest.json` for any agent-collabo skill earlier in this conversation, skip this check entirely and proceed. Otherwise: Let `SELF` be the value of the `name` field in this SKILL.md's frontmatter (e.g., `init-public-rules`). Let `LOCAL` be `metadata.version` from this same frontmatter. Fetch `https://raw.githubusercontent.com/dev-goraebap/agent-collabo/main/manifest.json` (1 HTTP request, fail silently on network error). Then evaluate exactly one case in this order: **Case A — outdated**: if `manifest.skills[SELF]` exists and `LOCAL < manifest.skills[SELF]`, tell the user (in their language) "agent-collabo `{SELF}` has a new version ({LOCAL} → {manifest.skills[SELF]}). Run `/agent-collabo-updater` when convenient. Continuing with the current task." then proceed. **Case B — up to date**: if `manifest.skills[SELF]` exists and `LOCAL === manifest.skills[SELF]`, proceed silently. **Case C — renamed away**: if `SELF` does NOT exist as a key in `manifest.skills` AND `SELF` exists as a key in `manifest.deprecated` (note: check the keys of `deprecated`, not the `renamedTo` values), tell the user "This skill `{SELF}` was renamed to `{manifest.deprecated[SELF].renamedTo}` since v{manifest.deprecated[SELF].since}. Run `/agent-collabo-updater` to migrate." then proceed. **Case D — unknown**: if `SELF` is not in `manifest.skills` and not in `manifest.deprecated`, tell the user "Skill `{SELF}` is no longer maintained. Run `/agent-collabo-updater` to clean up." then proceed with caution. Important: `manifest.deprecated` maps OLD names → NEW names. Never warn about a skill whose name is currently in `manifest.skills` just because that name appears as a `renamedTo` value somewhere in `deprecated`. **CDN cache caveat**: GitHub raw enforces `Cache-Control: max-age=300`, so right after a new release is pushed the manifest may be stale for up to 5 minutes via Fastly PoPs. If the user explicitly mentions they just released a new version (e.g., "I just pushed v0.X.Y") and this check still reports up-to-date or shows an older `manifest.version`, do not insist the local install is current — instead mention the 5-minute CDN window and suggest retrying shortly. For all other users this is invisible because they fetch long after the cache expires. |

## Language Policy

Conduct all user-facing communication in the user's language: interview questions, follow-up prompts, status messages, diagnostic reports, and summaries. Detect the language from (in order):

1. The language of the user's most recent messages in the current session
2. Declarations in their local rules file (e.g., `CLAUDE.local.md`, `.cursor/rules/local.mdc`) — look for instructions like "respond in Korean"
3. OS locale (`$LANG`, `$LC_ALL`)
4. English as fallback

Generated file content follows the file's audience: team-shared files (`AGENTS.md`, `CHANGELOG.md`) stay in English regardless of the user's language; personal files (`CLAUDE.local.md`, `GEMINI.local.md`, etc.) use the user's language unless they specify otherwise.

## Workflow

### Step 1: Scan Project

Search for all agent-related config files in the project:

| File | Agent |
|------|-------|
| `AGENTS.md` | Universal |
| `CLAUDE.md` or `.claude/CLAUDE.md` | Claude Code |
| `CLAUDE.local.md` | Claude Code personal |
| `.cursorrules` | Cursor (legacy) |
| `.cursor/rules/*.mdc` | Cursor (current) |
| `.github/copilot-instructions.md` | GitHub Copilot |
| `.windsurfrules` or `.windsurf/rules/*.md` | Windsurf |
| `GEMINI.md` | Gemini CLI |
| `.roo/rules/*.md` | Roo Code |
| `.junie/guidelines.md` | JetBrains Junie |

### Step 2: Status Report

Present a summary of discovered files:

```
📋 Agent Config File Status

Files found (3):
  - CLAUDE.md (45 lines) — build commands, code style, boundaries
  - .cursorrules (30 lines) — code style, test rules
  - .github/copilot-instructions.md (20 lines) — code style

Duplicates detected:
  - "Code style" rules duplicated across 3 files (similar content)
  - "Build commands" only in CLAUDE.md

Personal settings mixed in:
  - CLAUDE.md line 12: "Always respond in Korean" → recommend moving to personal config
```

### Step 3: Propose Consolidation Strategy

Present a consolidation plan based on analysis.

**Target structure.** The consolidated AGENTS.md follows the minimal 7-section layout (see `init-public-rules` / `references/agents-md-template.md` for full structure):

| Section | Included when |
|---|---|
| `# {Name}` + overview | Always |
| `## Project Structure` | Scattered files describe build flows, source-of-truth files, or forbidden zones |
| `## External Tools` | Scattered files mention MCP servers, shared CLIs, or required agent skills |
| `## Git Workflow` | Scattered files describe branching, commit conventions, or PR rules |
| `## Code Style` | Scattered files contain linter-uncovered style rules |
| `## Testing` | Scattered files contain mock policies, fixture locations, or test workflow rules |
| `## Boundaries` | Scattered files contain "never do / ask first / always do" content |
| `## References` | Scattered files link to design docs, ADRs, or specs |

**Rule classification and mapping:**

Map rules from existing files to the new sections as follows:

| Source content | Target section |
|---|---|
| "Always / Never / Ask before" directives | `## Boundaries` |
| Branch prefixes, commit format, merge rules | `## Git Workflow` |
| MCP server usage, shared tool conventions | `## External Tools` |
| Early return, naming rules, type preferences | `## Code Style` |
| Mock policy, fixture location, single test command | `## Testing` |
| Contract / flow / forbidden zones | `## Project Structure` |
| Design doc / ADR / spec links | `## References` |

**Classification principles:**
- Rules common across all files → Consolidate into the matching section
- Rules in only one file → Ask user whether to include
- Conflicting rules (same topic, different content) → Ask user which to keep
- Personal settings (response language, personal habits) → Guide to `CLAUDE.local.md`, do not migrate into AGENTS.md
- Content that copies `package.json` scripts verbatim, directory trees, or tech stack lists → **Drop**, not migrate (agents can read these directly)
- Content that is a truism ("write clean code") → **Drop**, not migrate

**Existing file handling:**

| Existing File | AGENTS.md Native Support | Action |
|--------------|-------------------------|--------|
| `.cursorrules` | Yes (Cursor reads AGENTS.md natively) | Suggest deletion |
| `.cursor/rules/*.mdc` | Yes | Suggest deletion (team rules go to AGENTS.md) |
| `CLAUDE.md` | No | Convert to `@AGENTS.md` or `@../AGENTS.md` bridge |
| `.github/copilot-instructions.md` | Yes (Copilot reads AGENTS.md natively) | Suggest deletion |
| `.windsurfrules` / `.windsurf/rules/` | Yes | Suggest deletion |
| `GEMINI.md` | Requires config | Keep or provide setup guidance |
| `.roo/rules/*.md` | Yes | Suggest deletion |
| `.junie/guidelines.md` | Yes | Suggest deletion |

Present the plan and get user approval.

### Step 4: User Approval

```
Proceed with the consolidation plan above?
1. Apply all
2. Select items individually
3. Cancel
```

### Step 5: Execute

Execute only user-approved items:

1. **Create or update AGENTS.md** — Write with consolidated rules
2. **Convert bridges** — CLAUDE.md → single `@AGENTS.md` line (location is user's choice)
3. **Clean up redundant files** — Ask before deleting files for agents that natively read AGENTS.md
4. **Separate personal settings** — Guide moving personal settings from team files to CLAUDE.local.md etc.
5. **Update .gitignore** — As needed

### Step 6: Summary

```
✅ Migration Complete

Result:
  - AGENTS.md (newly created, 72 lines)
  - CLAUDE.md → converted to @AGENTS.md bridge
  - .cursorrules → deleted (Cursor reads AGENTS.md natively)
  - .github/copilot-instructions.md → deleted

Token impact:
  - Before: 3 files, 95 lines (~285 tokens, with duplicates)
  - After: 1 file, 72 lines (~216 tokens, duplicates removed)

Next steps:
  - /audit-rules — verify the consolidated result
  - /refine-boundaries — restructure Boundaries into 3-tier format (future)
  - /git-workflow — refine Git Workflow with preset + delta (future)
  - /manage-tools — organize External Tools into Agent Skills / MCPs / CLIs (future)
  - /manage-refs — manage References entries (future)
```

## Prohibited Actions

- Never delete existing files without user approval
- Never include personal config files (CLAUDE.local.md, etc.) in consolidation
- Never delete files for agents that cannot natively read AGENTS.md — convert to bridges instead
