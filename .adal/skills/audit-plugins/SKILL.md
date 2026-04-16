---
name: audit-plugins
description: Audit Claude Code plugins for quality, compliance, and distribution readiness. Use before releases or for periodic quality checks.
argument-hint: "[plugin-name] [--force | --skip-validation | --local-only | --global-only]"
allowed-tools: Read, Bash, Glob, Grep, Task
model: opus
---

# Audit Plugins Command

Validate plugin manifests, component organization, namespace compliance, and marketplace readiness.

## Initialization

Before auditing, initialize the environment:

1. Get the current UTC date for audit timestamps.
2. Capture the project root path for subagent communication.
3. Ensure the temp directory (`.claude/temp/`) exists.
4. Clean up any stale audit files if the user confirms.

The `plugin-development` skill provides authoritative validation guidance (auto-loaded when this command runs).

## What Gets Audited

- plugin.json manifest structure and validity
- Required fields (name, description, version)
- Component organization (commands, skills, agents, hooks)
- Namespace compliance and consistency
- Documentation completeness
- Distribution and marketplace readiness

## Command Arguments

| Argument | Description |
| --- | --- |
| *(none)* | Smart mode: audit only modified, never-audited, or stale (>90 days) plugins |
| `--force` | Audit ALL plugins regardless of status |
| `--skip-validation` | Skip finding validation (faster, but may include false positives) |
| `--local-only` | Only audit local/dev repo plugins |
| `--global-only` | Only audit globally installed plugins |
| `plugin-name` | Audit specific plugin(s) by name |
| `local:name` | Explicitly target local plugin |
| `global:name` | Explicitly target global plugin |

## Step 1: Discover Plugin Sources

Detect all plugin sources in local repo and globally installed locations.

For local discovery, check marketplace repos (`plugins/*/plugin.json`), single plugin repos (`.claude-plugin/plugin.json`), and track plugin names for deduplication.

For global discovery, check `~/.claude/plugins/` (Unix) or `%USERPROFILE%\.claude\plugins\` (Windows). Skip globals that have local dev versions.

## Step 2: Parse Arguments

Parse flags and plugin names from the command arguments. Read audit logs for each discovered source to determine audit status (modified, never audited, stale >90 days).

## Step 3: Present Audit Plan

Display mode (SMART or FORCE), sources discovered, deduplication status, and audit queue with batching strategy.

## Step 4: Execute Audits

For each plugin, spawn the `plugin-component-auditor` subagent with the following context:

- Source (local or global)
- Full path to plugin directory
- Manifest location (path to plugin.json)
- Last audit date or "Never audited"
- Current audit date
- Project root path

Run subagents in parallel batches of 3-5.

**Role boundaries:**

- **Subagents** write individual audit findings to `.claude/temp/` as JSON and markdown files
- **Main command** collects subagent results, aggregates scores, and updates the central audit log

## Step 4.5: Validate Findings

**Unless `--skip-validation` flag is present:**

1. Spawn the `audit-finding-validator` agent with:
   - `project_root`: The captured project root path
   - `audit_type`: "plugin"
   - `audit_files`: List of `.claude/temp/audit-*-plugin-*.json` file paths
2. Wait for validation to complete
3. Read updated JSON files with validation results
4. Filter out FALSE_POSITIVE findings completely before aggregation
5. Note: Filtered findings are logged to `.claude/temp/audit-filtered-findings.json`

**If `--skip-validation` flag is present:**

- Skip validation phase entirely (current speed preserved)
- Present all findings without filtering
- Note in summary: "Validation: Skipped"

## Step 5: Final Summary

Report total audited by source, results, and details table. Note that global plugin fixes must be applied manually.

**Include validation statistics (if validation was performed):**

- Validation performed: Yes/No
- Findings validated: X
- False positives filtered: Y
- Verified findings: Z
- Unverified findings: W

## Important Notes

### Deduplication

Local dev repo plugins take precedence over globally installed versions. Global plugins are read-only - report findings but recommend manual fixes.

### Cross-Platform Paths

| Platform | Global Plugins |
| --- | --- |
| Unix | `~/.claude/plugins/` |
| Windows | `%USERPROFILE%\.claude\plugins\` |

### Manifest Locations

Plugins may store their manifest in either `plugin.json` (root) or `.claude-plugin/plugin.json` (nested). Check both locations during discovery.

## Audit Log Location

All audit results are written to `.claude/audit/plugins.md`.

Use `/audit-log plugins` to view current audit status.

## Example Usage

### Example 1: Audit All Plugins

```text
User: /audit-plugins

Claude: Discovering plugin sources...

## Audit Plan
**Mode**: SMART
- Local: claude-ecosystem, code-quality, git (3 plugins)
- Global: soft-skills (1 plugin)
- Deduplicated: claude-ecosystem (global skipped)

**Will audit**: 4 plugins in 1 batch

[Spawns plugin-component-auditor subagents]

## Audit Complete
| Source | Plugin | Result | Score |
| --- | --- | --- | --- |
| local | claude-ecosystem | PASS | 100/100 |
| local | code-quality | PASS | 95/100 |
```

### Example 2: Audit Specific Plugin

```text
User: /audit-plugins claude-ecosystem
Claude: PASS (Score: 100/100)
```
