---
name: audit-memory
description: Audit Claude Code CLAUDE.md memory files for quality, compliance, and organization. Use to validate import syntax, detect circular imports, and check hierarchy compliance.
argument-hint: "[project | user | all] [--force | --skip-validation] [--token-budget]"
allowed-tools: Read, Bash, Glob, Grep, Task
---

# Audit Memory Command

Audit Claude Code CLAUDE.md memory files for quality, compliance, and organization.

## Initialization

Before auditing, initialize the environment:

Get the current UTC date, capture the project root path, ensure the temp directory exists, and clean up stale audit files. The `memory-management` skill provides authoritative validation guidance (auto-loaded when this command runs).

## What Gets Audited

- Import syntax (`@path/to/file.md`)
- Hierarchy compliance (enterprise > project > user)
- Circular import detection
- Size guidelines and progressive disclosure
- Content organization

## Command Arguments

| Argument | Description |
| --- | --- |
| *(none)* | Audit all discoverable CLAUDE.md files |
| `project` | Only audit project-level files |
| `user` | Only audit `~/.claude/CLAUDE.md` |
| `all` | Audit all scopes explicitly |
| `--force` | Audit regardless of modification status |
| `--skip-validation` | Skip finding validation (faster, but may include false positives) |
| `--token-budget` | Run ONLY token budget analysis (skip full audit) |

## Step 1: Discover CLAUDE.md Files

Check root `CLAUDE.md`, `.claude/CLAUDE.md`, user `~/.claude/CLAUDE.md` (Unix) or `%USERPROFILE%\.claude\CLAUDE.md` (Windows), and `.claude/memory/*.md`.

Build list with scope and level (root/dot-claude/memory/user).

## Step 2: Parse Arguments

Parse scope selector and `--force` flag. Filter files to match requested scope.

## Step 3: Present Audit Plan

Display mode, files discovered, primary files, and imported memory files.

## Step 4: Execute Audits

For each file, spawn the `memory-component-auditor` subagent with scope, level, path, and last audit date. Run in parallel batches of 3-5.

After individual audits, perform cross-file circular import detection by building an import graph.

Subagents write findings to `.claude/temp/`. The main conversation thread collects results and updates audit logs using its Write/Edit tools.

## Step 4.5: Validate Findings

**Unless `--skip-validation` flag is present:**

1. Spawn the `audit-finding-validator` agent with:
   - `project_root`: The captured project root path
   - `audit_type`: "memory"
   - `audit_files`: List of `.claude/temp/audit-*-memory-*.json` file paths
2. Wait for validation to complete
3. Read updated JSON files with validation results
4. Filter out FALSE_POSITIVE findings completely before aggregation
5. Note: Filtered findings are logged to `.claude/temp/audit-filtered-findings.json`

**If `--skip-validation` flag is present:**

- Skip validation phase entirely (current speed preserved)
- Present all findings without filtering
- Note in summary: "Validation: Skipped"

## Step 5: Final Summary

Report total audited by scope, results, circular import check, and details tables. Provide remediation steps for issues.

**Include validation statistics (if validation was performed):**

- Validation performed: Yes/No
- Findings validated: X
- False positives filtered: Y
- Verified findings: Z
- Unverified findings: W

## Step 6: Token Budget Analysis (included by default)

**Scope:** Only always-loaded files (root CLAUDE.md + files with @-prefix imports marked as "Always-loaded")

**Note:** Use `--token-budget` to run ONLY this step (skips Steps 1-5 full audit).

### 6.1 Fetch Official Guidance

Invoke `memory-management` skill (which delegates to `docs-management`) to fetch current official guidance on memory file sizing. Official docs recommend keeping memory "concise and focused" with progressive disclosure - specific token thresholds are repo-specific standards, not official requirements.

### 6.2 Calculate Tokens Per File

For each always-loaded file:

1. Read file content
2. Estimate tokens: `len(content) / 4` (approximate for English markdown)
3. Extract declared Token Budget from header if present (e.g., `**Token Budget:** ~1,800 tokens`)
4. Record file path, actual tokens, declared budget

### 6.3 Calculate Aggregate Total

Sum all always-loaded file tokens. Do NOT include on-demand files (those without @ prefix in root, or marked "Context-Dependent").

### 6.4 Evaluate Against Repo-Specific Thresholds

**These thresholds are repo-specific standards (see audit-framework.md), NOT from official Claude Code docs:**

| Status | Token Range | Guidance |
| --- | --- | --- |
| PASS | ≤12k tokens | Within repo budget |
| WARN | 12k-15k tokens | At upper limit, monitor |
| FAIL | >15k tokens | Over budget, remediation needed |

### 6.5 Generate Report

Report includes:

1. **Top 5 largest files** by token count with percentage of total
2. **Aggregate total** vs repo-specific budget
3. **Declared vs actual variance** for files where declared budget differs from actual by >20%
4. **Status** (PASS/WARN/FAIL) based on aggregate total

### 6.6 Suggest Remediation (if FAIL or WARN)

If over budget, recommend:

- Files that could move to on-demand loading (not critical for every session)
- Large files (>2k tokens) that could be split using hub pattern
- Reference progressive disclosure guidance from official docs (via memory-management skill)

### 6.7 Update Audit Log

Add Token Budget Analysis section to `.claude/audit/memory.md` with:

- Status and analysis date
- Metrics table (total, budget, variance)
- Top 5 largest files table
- Declared vs actual variance table (if any discrepancies)

## Important Notes

### Import Syntax

Valid: `@path/to/file.md` (e.g., `@.claude/memory/workflows.md`)

### Hierarchy Compliance

1. Enterprise (highest precedence)
2. Project root (`CLAUDE.md`)
3. Project dot-claude (`.claude/CLAUDE.md`)
4. User (`~/.claude/CLAUDE.md` - lowest)

### Size Guidelines

| File Type | Recommended Size |
| --- | --- |
| Root CLAUDE.md | < 50 lines core + imports |
| Memory imports | < 500 lines each |

### Cross-Platform Paths

| Platform | User Memory |
| --- | --- |
| Unix | `~/.claude/CLAUDE.md` |
| Windows | `%USERPROFILE%\.claude\CLAUDE.md` |

## Audit Log Location

All audit results are written to `.claude/audit/memory.md`.

Use `/audit-log memory` to view current audit status.

## Example Usage

### Example 1: Audit All Memory Files

```text
User: /audit-memory

Claude: Discovering CLAUDE.md files...

## Audit Plan
**Mode**: SMART
**Files discovered**: 12

### Primary Files:
1. [project:root] CLAUDE.md
2. [user] ~/.claude/CLAUDE.md

### Imported Files:
3. [project:memory] .claude/memory/workflows.md
...

[Spawns memory-component-auditor subagents]

## Audit Complete
**Circular Import Check**: ✓ No cycles detected

| Scope | File | Result | Score |
| --- | --- | --- | --- |
| project | CLAUDE.md | PASS | 100/100 |
```

### Example 2: Audit Project Only

```text
User: /audit-memory project
Claude: Auditing project-level files...
```
