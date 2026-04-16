---
name: audit-agents
description: Audit Claude Code subagents for quality, compliance, and maintainability. Use after creating or modifying agents, before releases, or for periodic quality checks.
argument-hint: "[agent-name] [--force | --skip-validation | --plugin-only | --project-only | --global-only | --recover]"
allowed-tools: Read, Bash, Glob, Grep, Task
---

# Audit Agents Command

Audit Claude Code subagents for quality, compliance with official documentation, and maintainability.

## Initialization

Before auditing, initialize the environment:

Get the current UTC date, capture the project root path, ensure the temp directory exists, and clean up stale audit files (unless `--recover`). The `subagent-development` skill provides authoritative validation guidance (auto-loaded when this command runs).

## What Gets Audited

- YAML frontmatter (name, description, tools, model, color)
- Naming conventions (lowercase kebab-case, max 64 chars)
- Description quality (third person, "PROACTIVELY use when..." guidance)
- Tool access configuration appropriateness
- Model selection correctness (haiku/sonnet/opus based on complexity)

## Command Arguments

| Argument | Description |
| --- | --- |
| *(none)* | Smart mode: audit modified, never-audited, or stale (>90 days) agents |
| `--force` | Audit ALL agents regardless of status |
| `--skip-validation` | Skip finding validation (faster, but may include false positives) |
| `--plugin-only` | Only audit local plugin agents |
| `--project-only` | Only audit project agents (`.claude/agents/`) |
| `--global-only` | Only audit globally installed plugin agents |
| `--recover` | Recover results from interrupted audit |
| `agent-name` | Audit specific agent(s) by name |

## Step 1: Discover Agent Sources

Detect all agent sources in local repo and globally installed plugins.

For local discovery, check marketplace repos, single plugin repos, and `.claude/agents/`. Track plugin names for deduplication.

For global discovery, check `~/.claude/plugins/` (Unix) or `%USERPROFILE%\.claude\plugins\` (Windows). Skip globals with local dev versions.

## Step 2: Determine Audit Queue

If specific agents named, audit those. If `--force`, audit all. Otherwise, audit modified/stale agents.

## Step 3: Present Audit Plan

Display mode, sources discovered, deduplication status, and audit queue.

## Step 4: Execute Audits

For each agent, spawn the `agent-auditor` subagent with source, path, and last audit date. Run in parallel batches of 3-5.

Subagents write findings to `.claude/temp/`. The main conversation thread collects results and updates audit logs using its Write/Edit tools.

## Step 4.5: Validate Findings

**Unless `--skip-validation` flag is present:**

1. Spawn the `audit-finding-validator` agent with:
   - `project_root`: The captured project root path
   - `audit_type`: "agent"
   - `audit_files`: List of `.claude/temp/audit-*-agent-*.json` file paths
2. Wait for validation to complete
3. Read updated JSON files with validation results
4. Filter out FALSE_POSITIVE findings completely before aggregation
5. Note: Filtered findings are logged to `.claude/temp/audit-filtered-findings.json`

**If `--skip-validation` flag is present:**

- Skip validation phase entirely (current speed preserved)
- Present all findings without filtering
- Note in summary: "Validation: Skipped"

## Step 5: Final Summary

Report total audited by source, results, and details table. Note that global agent fixes must be applied manually.

**Include validation statistics (if validation was performed):**

- Validation performed: Yes/No
- Findings validated: X
- False positives filtered: Y
- Verified findings: Z
- Unverified findings: W

## Scoring

- **PASS** (85+): Ready for use
- **PASS WITH WARNINGS** (70-84): Functional with improvement opportunities
- **FAIL** (<70): Issues that should be addressed

## Audit Log Location

All audit results are written to `.claude/audit/agents.md`.

Use `/audit-log agents` to view current audit status.

## Recovery

If context collapses mid-audit, use `/audit-agents --recover` to recover from `.claude/temp/` JSON files.

## Example Usage

### Example 1: Audit All Agents

```text
User: /audit-agents

Claude: Discovering agent sources...

## Audit Plan
**Mode**: SMART
- Plugin: claude-ecosystem (12 agents)
- Plugin: code-quality (3 agents)
- Deduplicated: claude-ecosystem (global skipped)

**Will audit**: 5 agents

[Spawns agent-auditor subagents]

## Audit Complete
| Source | Agent | Result | Score |
| --- | --- | --- | --- |
| plugin | code-reviewer | PASS | 100/100 |
```

### Example 2: Audit Specific Agent

```text
User: /audit-agents plugin:code-reviewer
Claude: PASS (Score: 100/100)
```
