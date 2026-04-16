---
name: audit-output-styles
description: Audit Claude Code output styles for quality, compliance, and usability. Use when creating custom styles or validating existing ones.
argument-hint: "[plugin | project | user | all] [--force | --skip-validation]"
allowed-tools: Read, Bash, Glob, Grep, Task
model: opus
---

# Audit Output Styles Command

Audit Claude Code output styles for quality, compliance, and usability.

## Initialization

Before auditing, initialize the environment:

1. Get the current UTC date for audit timestamps.
2. Capture the project root path for subagent communication.
3. Ensure the temp directory (`.claude/temp/`) exists.
4. Clean up any stale audit files if the user confirms.

The `output-customization` skill provides authoritative validation guidance (auto-loaded when this command runs).

## What Gets Audited

- Markdown file format (must be `.md`, not `.json`)
- YAML frontmatter (name, description, keep-coding-instructions)
- Content structure and clarity
- File naming conventions
- Style switching compatibility

## Command Arguments

| Argument | Description |
| --- | --- |
| *(none)* | Audit all discoverable output styles |
| `plugin` | Only audit plugin output styles |
| `project` | Only audit `.claude/output-styles/*.md` |
| `user` | Only audit `~/.claude/output-styles/*.md` |
| `all` | Audit all scopes explicitly |
| `--force` | Audit regardless of modification status |
| `--skip-validation` | Skip finding validation (faster, but may include false positives) |

## Step 1: Discover Output Styles

Check plugin directories (`plugins/*/output-styles/*.md`), project directory (`.claude/output-styles/*.md`), and user directory (`~/.claude/output-styles/*.md` on Unix, `%USERPROFILE%\.claude\output-styles\` on Windows).

Warn about any `.json` files found (wrong format - output styles must be markdown).

## Step 2: Parse Arguments

Parse the scope selector (plugin, project, user, all) and `--force` flag from command arguments. Filter discovered styles to match the requested scope.

## Step 3: Present Audit Plan

Display mode (SMART or FORCE), styles discovered, plugins with styles, and file list with scope.

## Step 4: Execute Audits

For each style, spawn the `output-style-auditor` subagent with the following context:

- Scope (plugin, project, or user)
- Full path to the style file
- Style name (derived from filename)
- Last audit date or "Never audited"
- Current audit date
- Project root path

Run subagents in parallel batches of 3-5.

Subagents write findings to `.claude/temp/` as both JSON (for recovery/aggregation) and markdown (for human review). The main conversation thread collects results and updates audit logs using its Write/Edit tools.

## Step 4.5: Validate Findings

**Unless `--skip-validation` flag is present:**

1. Spawn the `audit-finding-validator` agent with:
   - `project_root`: The captured project root path
   - `audit_type`: "output-style"
   - `audit_files`: List of `.claude/temp/audit-*-output-style-*.json` file paths
2. Wait for validation to complete
3. Read updated JSON files with validation results
4. Filter out FALSE_POSITIVE findings completely before aggregation
5. Note: Filtered findings are logged to `.claude/temp/audit-filtered-findings.json`

**If `--skip-validation` flag is present:**

- Skip validation phase entirely (current speed preserved)
- Present all findings without filtering
- Note in summary: "Validation: Skipped"

## Step 5: Final Summary

Report total audited by scope, results, and details table. List format warnings for `.json` files with remediation (convert to `.md`).

**Include validation statistics (if validation was performed):**

- Validation performed: Yes/No
- Findings validated: X
- False positives filtered: Y
- Verified findings: Z
- Unverified findings: W

## Important Notes

### Frontmatter Requirements

Output styles require YAML frontmatter with `name`, `description`, and optionally `keep-coding-instructions`.

### File Naming

Use kebab-case with `.md` extension (e.g., `my-style.md`).

### Cross-Platform Paths

| Platform | User Styles |
| --- | --- |
| Unix | `~/.claude/output-styles/` |
| Windows | `%USERPROFILE%\.claude\output-styles\` |

## Audit Log Location

All audit results are written to `.claude/audit/output-styles.md`.

Use `/audit-log output-styles` to view current audit status.

## Example Usage

### Example 1: Audit All Output Styles

```text
User: /audit-output-styles

Claude: Discovering output styles...

## Audit Plan
**Mode**: SMART
**Styles discovered**: 3
**Plugins with styles**: 2

1. [plugin:claude-ecosystem] concise-coder.md
2. [plugin:soft-skills] code-review-comment.md
3. [project] custom-style.md

[Spawns output-style-auditor subagents]

## Audit Complete
| Scope | Style | Result | Score |
| --- | --- | --- | --- |
| plugin | concise-coder | PASS | 100/100 |
| project | custom-style | PASS | 98/100 |
```

### Example 2: Audit Plugin Styles Only

```text
User: /audit-output-styles plugin
Claude: Auditing plugin output styles only...
```
