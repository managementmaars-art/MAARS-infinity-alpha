---
name: audit-hooks
description: Audit Claude Code hooks for quality, compliance, and maintainability. Use after creating hooks, before releases, or for periodic quality checks.
argument-hint: "[hook-name] [--force | --skip-validation | --plugin-only | --project-only | --global-only]"
allowed-tools: Read, Bash, Glob, Grep, Task
---

# Audit Hooks Command

Audit Claude Code hooks for quality, compliance, and maintainability.

## Initialization

Before auditing, initialize the environment:

Get the current UTC date, capture the project root path, ensure the temp directory exists, and clean up any stale audit files if the user confirms. The `hook-management` skill provides authoritative validation guidance (auto-loaded when this command runs).

## What Gets Audited

- hooks.json configuration structure and validity
- Hook script existence and structure
- Matcher configuration appropriateness
- Environment variable naming conventions
- Decision control usage
- Test existence and coverage

## Command Arguments

| Argument | Description |
| --- | --- |
| *(none)* | Smart mode: audit only modified, never-audited, or stale (>90 days) hooks |
| `--force` | Audit ALL hooks regardless of status |
| `--skip-validation` | Skip finding validation (faster, but may include false positives) |
| `--plugin-only` | Only audit local plugin hooks |
| `--project-only` | Only audit project hooks (`.claude/hooks/`) |
| `--global-only` | Only audit globally installed plugin hooks |
| `hook-name` | Audit specific hook(s) by name |
| `plugin:name` | Explicitly target plugin hook |

## Step 1: Discover Hook Sources

Detect all hook sources in local repo and globally installed plugins.

For local discovery, check marketplace repos, single plugin repos, and `.claude/hooks/`. Track plugin names for deduplication.

For global discovery, check `~/.claude/plugins/` (Unix) or `%USERPROFILE%\.claude\plugins\` (Windows). Skip globals that have local dev versions.

## Step 2: Parse Arguments

Parse flags and hook names. Read audit logs for each source.

## Step 3: Present Audit Plan

Display mode, sources discovered, deduplication status, and audit queue.

## Step 4: Execute Audits

For each hook, spawn the `hook-auditor` subagent with source, path, and last audit date. Run in parallel batches of 3-5.

Subagents write findings to `.claude/temp/`. The main conversation thread collects results and updates audit logs using its Write/Edit tools.

## Step 4.5: Validate Findings

**Unless `--skip-validation` flag is present:**

1. Spawn the `audit-finding-validator` agent with:
   - `project_root`: The captured project root path
   - `audit_type`: "hook"
   - `audit_files`: List of `.claude/temp/audit-*-hook-*.json` file paths
2. Wait for validation to complete
3. Read updated JSON files with validation results
4. Filter out FALSE_POSITIVE findings completely before aggregation
5. Note: Filtered findings are logged to `.claude/temp/audit-filtered-findings.json`

**If `--skip-validation` flag is present:**

- Skip validation phase entirely (current speed preserved)
- Present all findings without filtering
- Note in summary: "Validation: Skipped"

## Step 5: Final Summary

Report total audited by source, results, and details table. Note that global hook fixes must be applied manually.

**Include validation statistics (if validation was performed):**

- Validation performed: Yes/No
- Findings validated: X
- False positives filtered: Y
- Verified findings: Z
- Unverified findings: W

## Important Notes

### Deduplication

Local dev repo plugins take precedence over globally installed versions. Global hooks are read-only - report findings but recommend manual fixes.

### Cross-Platform Paths

| Platform | Global Plugins |
| --- | --- |
| Unix | `~/.claude/plugins/` |
| Windows | `%USERPROFILE%\.claude\plugins\` |

## Audit Log Location

All audit results are written to `.claude/audit/hooks.md`.

Use `/audit-log hooks` to view current audit status.

## Example Usage

### Example 1: Audit All Hooks

```text
User: /audit-hooks

Claude: Discovering hook sources...

## Audit Plan
**Mode**: SMART
- Plugin: claude-ecosystem (4 hooks)
- Local: .claude/hooks/ (2 hooks)
- Deduplicated: claude-ecosystem (global skipped)

**Will audit**: 3 hooks

[Spawns hook-auditor subagents]

## Audit Complete
| Source | Hook | Result | Score |
| --- | --- | --- | --- |
| plugin | prevent-backup-files | PASS | 100/100 |
```

### Example 2: Audit Specific Hook

```text
User: /audit-hooks plugin:prevent-backup-files
Claude: PASS (Score: 100/100)
```
