---
name: audit-docs-delegation
description: Audit skills and memory files for docs-management delegation compliance. Detects hardcoded Claude Code data and verifies proper delegation patterns.
argument-hint: "[skill-name] [--force | --plugin-only | --project-only]"
allowed-tools: Read, Bash, Glob, Grep, Task
---

# Audit Docs-Delegation Command

Audit skills and memory files for docs-management delegation compliance.

## Initialization

Before auditing, initialize the environment:

1. Get the current UTC date for audit timestamps.
2. Capture the project root path for subagent communication.
3. Ensure the temp directory (`.claude/temp/`) exists.
4. Clean up any stale audit files if the user confirms.

The `ecosystem-health` skill provides authoritative validation guidance (auto-loaded when this command runs).

## What Gets Audited

- **Hardcoded Claude Code data**: Hook event types, YAML frontmatter fields, settings keys
- **Volatile information**: GitHub issue references, model names with versions, token limits
- **Delegation patterns**: Verification notes, MANDATORY sections, skill references
- **Exempt patterns**: Configuration files, educational content, self-specification

## Command Arguments

| Argument | Description |
| --- | --- |
| *(none)* | Smart mode: audit modified, never-audited, or stale (>90 days) files |
| `--force` | Audit ALL files regardless of status |
| `--plugin-only` | Only audit local plugin skills |
| `--project-only` | Only audit project files (`.claude/skills/`, `.claude/memory/`) |
| `skill-name` | Audit specific skill(s) by name |

## Step 1: Discover Audit Targets

Search for files that may contain Claude Code references:

**Skills:**

- `plugins/*/skills/*/SKILL.md` (local plugins)
- `.claude/skills/*/SKILL.md` (project skills)

**Memory Files:**

- `.claude/memory/*.md` (project memory)
- `plugins/*/skills/*/references/*.md` (skill references)

**Audit Framework Files:**

- `plugins/*/skills/*/references/audit-framework.md` (audit validation rules)
- `plugins/*/skills/*/references/*-criteria.md` (validation criteria files)

**Exclusions (auto-exempt):**

- `hooks.json` files (configuration specification)
- `hooks/*.py`, `hooks/*.sh` (hook implementations)
- `canonical/` directories (scraped documentation cache)
- `plugins/tac/lessons/` (educational content)

Build a list of discovered files with their scope (plugin, project) and full path.

## Step 2: Parse Arguments

Check for `--force`, `--plugin-only`, `--project-only` flags or specific skill names.

Build the audit queue based on discovered files and arguments:

- **Smart mode**: Filter to modified, never-audited, or stale (>90 days) files
- **Force mode**: Include all discovered files
- **Scoped modes**: Filter to matching scope only

## Step 3: Present Audit Plan

Display audit mode (SMART or FORCE), targets discovered, and list each with scope and last modified date.

```text
## Audit Plan
**Mode**: SMART
**Files discovered**: 15

1. [plugin:claude-ecosystem] skills/hook-management/SKILL.md
2. [plugin:claude-ecosystem] skills/skill-development/SKILL.md
3. [project] .claude/memory/workflows.md
...

**Will audit**: 8 files (7 skipped - recently audited)
```

## Step 4: Execute Audits

For each file, spawn the `docs-delegation-auditor` subagent with the following context:

- Scope (plugin:name or project)
- Full path to the file
- Last audit date or "Never audited"
- Current audit date
- Project root path

Run subagents in parallel batches of 3-5.

Subagents write findings to `.claude/temp/` as both JSON (for recovery/aggregation) and markdown (for human review). The main conversation thread collects results and updates audit logs using its Write/Edit tools.

**CRITICAL:** After ALL audits complete, sync results to the audit log at `.claude/audit/docs-delegation.md`.

## Step 5: Final Summary

Report total files audited, results by scope, and details table. List any compliance issues with remediation steps.

```text
## Audit Complete

### Summary
- **Total audited**: 8 files
- **COMPLIANT**: 5 (62%)
- **PARTIALLY COMPLIANT**: 2 (25%)
- **NON-COMPLIANT**: 1 (13%)

### Results
| Scope | File | Classification | Score |
| --- | --- | --- | --- |
| plugin | hook-management/SKILL.md | ✅ COMPLIANT | 95/100 |
| plugin | skill-development/SKILL.md | ✅ COMPLIANT | 100/100 |
| project | workflows.md | ⚠️ PARTIAL | 78/100 |
| plugin | lesson-014-analysis.md | ❌ NON-COMPLIANT | 65/100 |

### Issues Found
1. **lesson-014-analysis.md** (Score: 65)
   - HIGH: Hardcoded `PreToolUse`, `PostToolUse` without delegation note
   - Missing MANDATORY section
   - **Action**: Add verification note pointing to docs-management
```

## Scoring

Files are scored out of 100 points with deductions for hardcoded patterns:

| Deduction | Amount | Condition |
| --- | --- | --- |
| HIGH risk pattern | -15 each | Hardcoded without delegation note |
| MEDIUM risk pattern | -8 each | Hardcoded without delegation note |
| Missing MANDATORY section | -20 | File has hardcoded data but no delegation section |
| Missing verification notes | -15 | Hardcoded data without verification blockquote |

**Thresholds:**

- **COMPLIANT** (85+): Ready for use, proper delegation
- **PARTIALLY COMPLIANT** (70-84): Functional with improvement opportunities
- **NON-COMPLIANT** (<70): Hardcoded data that should be delegated

## Important Notes

### HIGH Risk Patterns

These indicate hardcoded Claude Code information that should delegate to docs-management:

| Pattern | Example |
| --- | --- |
| Hook event types | `PreToolUse`, `PostToolUse`, `SessionStart` |
| YAML frontmatter fields (in prose) | `allowed-tools`, `permissionMode`, `color` |
| Settings keys | `CLAUDE_HOOK_*`, `apiChoice`, `sandboxMode` |

### MEDIUM Risk Patterns

| Pattern | Example |
| --- | --- |
| GitHub issue references | `#10437`, `#15326` |
| Model names with versions | `Opus 4.5`, `claude-opus-4-5` |
| Token limits | `25K tokens`, `context window` |

### Compliance Patterns (What Makes Files Compliant)

| Pattern | Description |
| --- | --- |
| Verification note | `> **Documentation Verification:**` blockquote |
| MANDATORY section | `## MANDATORY:` or `## 🚨.*MANDATORY` |
| Query pattern table | Table with `docs-management` query patterns |
| Skill reference | `invoke the X-management skill` |

### Exempt Patterns (Not Flagged)

| Pattern | Reason |
| --- | --- |
| `hooks.json` event names | Configuration specification |
| `allowed-tools` in YAML frontmatter | Self-specification |
| `tools` in agent YAML frontmatter | Agent definition |
| Educational content | Instructional, not authoritative |
| `canonical/` directories | Scraped docs cache |

## Audit Log Location

All audit results are written to `.claude/audit/docs-delegation.md`.

Use `/audit-log docs-delegation` to view current audit status.

## Example Usage

### Example 1: Audit All Files

```text
User: /audit-docs-delegation

Claude: Discovering audit targets...

## Audit Plan
**Mode**: SMART
**Files discovered**: 25

1. [plugin:claude-ecosystem] skills/hook-management/SKILL.md
2. [plugin:claude-ecosystem] skills/skill-development/SKILL.md
3. [plugin:tac] analysis/lesson-014-analysis.md
...

**Will audit**: 12 files (13 skipped - recently audited)

[Spawns docs-delegation-auditor subagents]

## Audit Complete
| Scope | File | Classification | Score |
| --- | --- | --- | --- |
| plugin | hook-management/SKILL.md | ✅ COMPLIANT | 95/100 |
```

### Example 2: Force Audit All

```text
User: /audit-docs-delegation --force

Claude: Auditing all files (force mode)...
```

### Example 3: Audit Specific Skill

```text
User: /audit-docs-delegation hook-management

Claude: Auditing hook-management skill...
```

### Example 4: Plugin-Only Audit

```text
User: /audit-docs-delegation --plugin-only

Claude: Auditing plugin skills only...
```
