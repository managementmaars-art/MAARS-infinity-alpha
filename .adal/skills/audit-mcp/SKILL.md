---
name: audit-mcp
description: Audit MCP server configurations for quality, compliance, and security. Use to validate .mcp.json files and server setups.
argument-hint: "[project | user | settings | all] [--force | --skip-validation]"
allowed-tools: Read, Bash, Glob, Grep, Task
---

# Audit MCP Command

Audit MCP server configurations for quality, compliance, and security.

## Step 0: Initialize Audit Environment

Get the current UTC date, capture the project root path, ensure the temp directory exists, and clean up any stale audit files if the user confirms. Invoke the `claude-ecosystem:mcp-integration` skill to load authoritative MCP configuration guidance.

## What Gets Audited

This command audits MCP server configurations from multiple sources:

- **Project scope**: `.mcp.json` in project root (version-controlled, team-shared)
- **User (Global) scope**: `~/.claude.json` with root-level `mcpServers` key
- **Local scope**: `.claude/settings.local.json` with `mcpServers` key if present
- **Plugin scope**: `.mcp.json` files within plugin directories
- **Enterprise scope**: `managed-mcp.json` in system directories

For each configuration, validate JSON structure, server fields, transport types, authentication, environment variable usage, and security (no exposed credentials).

## Command Arguments

- **No arguments**: Audit all discoverable MCP configurations
- **project**: Audit only `.mcp.json` in project root
- **user**: Audit user-level config (`~/.claude.json`)
- **all**: Audit all MCP configs (project + user + plugins)
- **--force**: Audit regardless of modification status
- **--skip-validation**: Skip finding validation (faster, but may include false positives)

## Step 1: CLI-First Discovery (MANDATORY)

**ALWAYS start by running `claude mcp list`** to get the authoritative list of configured MCP servers. This provides ground truth from the running system and prevents missing configurations stored in unexpected locations.

```bash
# Get authoritative list with scope information
claude mcp list

# Get details on specific server if needed
claude mcp get <server-name>
```

**Why CLI First:**

- File locations can change between Claude Code versions
- User config is in `~/.claude.json` (NOT `~/.claude/.mcp.json` - this path does not exist)
- The `mcpServers` key may be deep in the file (line 200+) and easy to miss with partial reads
- CLI output shows scope, connection status, and transport type

## Step 2: Verify Configuration Files

After CLI discovery, verify the configuration files exist and can be read. For large files like `~/.claude.json`, use grep to find the `mcpServers` key position before reading.

**Configuration locations (per official docs):**

| Scope | Location |
| --- | --- |
| Project | `.mcp.json` (project root) |
| User (Global) | `~/.claude.json` (root-level `mcpServers` key) |
| Local | `.claude/settings.local.json` (`mcpServers` key) |
| Plugin | `plugins/*/.mcp.json` |
| Enterprise | `managed-mcp.json` (system paths) |

Build a list of discovered configurations with scope, path, and server count.

## Step 3: Parse Arguments and Filter

Parse the scope selector and `--force` flag. Filter discovered configurations to match the requested scope.

## Step 4: Present Audit Plan

Display audit mode (SMART or FORCE), configurations discovered, and list each file with scope and server count.

## Step 5: Execute Audits

For each configuration, invoke the `mcp-auditor` subagent with scope, path, config type, and last audit date. Run audits in parallel when multiple configurations exist.

## Step 5.5: Validate Findings

**Unless `--skip-validation` flag is present:**

1. Spawn the `audit-finding-validator` agent with:
   - `project_root`: The captured project root path
   - `audit_type`: "mcp"
   - `audit_files`: List of `.claude/temp/audit-*-mcp-*.json` file paths
2. Wait for validation to complete
3. Read updated JSON files with validation results
4. Filter out FALSE_POSITIVE findings completely before aggregation
5. Note: Filtered findings are logged to `.claude/temp/audit-filtered-findings.json`

**If `--skip-validation` flag is present:**

- Skip validation phase entirely (current speed preserved)
- Present all findings without filtering
- Note in summary: "Validation: Skipped"

## Step 6: Final Summary

Report total configurations audited, server count, results by scope, and a details table. List security alerts and configuration issues with remediation steps.

**Include validation statistics (if validation was performed):**

- Validation performed: Yes/No
- Findings validated: X
- False positives filtered: Y
- Verified findings: Z
- Unverified findings: W

## Important Notes

### Security Considerations

MCP configurations must NEVER contain hardcoded API keys, tokens, or passwords in version-controlled files. Use environment variable expansion (`${API_KEY}`) for sensitive values.

**Credential severity by location:**

| Location | Hardcoded Credentials | Severity |
| --- | --- | --- |
| `.mcp.json` (project, version-controlled) | CRITICAL FAILURE | Keys exposed in git |
| `~/.claude.json` (user, NOT version-controlled) | WARNING | Acceptable for personal use |

### Transport Types

Valid types: `stdio` (local processes), `http` (recommended for remote), `sse` (deprecated).

### Cross-Platform Paths

| Platform | User Config Location |
| --- | --- |
| Unix | `~/.claude.json` |
| Windows | `%USERPROFILE%\.claude.json` |

## Audit Log Location

All audit results are written to `.claude/audit/mcp.md`.

Use `/audit-log mcp` to view current audit status.

## Example Usage

### Example 1: Audit All MCP Configurations

```text
User: /audit-mcp

Claude: Running CLI discovery first...
$ claude mcp list
perplexity: cmd /c npx -y perplexity-mcp - Connected (User scope)
firecrawl: cmd /c npx -y firecrawl-mcp - Connected (User scope)
...

## Audit Plan
**Mode**: SMART
**MCP servers discovered via CLI**: 5
**Configuration file**: ~/.claude.json

### Servers to Audit:
1. [user] perplexity - stdio
2. [user] firecrawl - stdio
3. [user] context7 - stdio
4. [user] microsoft-learn - http
5. [user] ref - http

[Spawns mcp-auditor subagent]

## MCP Audit Complete
**Total servers**: 5
**Scope**: User (Global)

| Server | Transport | Security | Result |
| --- | --- | --- | --- |
| perplexity | stdio | WARNING: Hardcoded API key | 85/100 |
| firecrawl | stdio | WARNING: Hardcoded API key | 85/100 |
| context7 | stdio | PASS | 95/100 |
| microsoft-learn | http | PASS | 95/100 |
| ref | http | WARNING: API key in URL | 85/100 |
```

### Example 2: Audit Project MCP Only

```text
User: /audit-mcp project

Claude: Checking for project .mcp.json...
[Audits .mcp.json in project root if exists]
```

### Example 3: Audit with Force

```text
User: /audit-mcp --force

Claude: Running full MCP audit (force mode)...
[Audits all configs regardless of modification status]
```
