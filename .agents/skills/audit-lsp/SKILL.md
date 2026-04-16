---
name: audit-lsp
description: Audit Claude Code LSP server configurations for quality and compliance. Use when creating or validating plugin LSP servers, or troubleshooting code intelligence issues.
argument-hint: [--force | --skip-validation]
allowed-tools: Read, Bash, Glob, Grep, Task
---

# Audit LSP Servers Command

Audit Claude Code LSP (Language Server Protocol) server configurations for quality and compliance.

## Initialization

Before auditing, initialize the environment:

1. Get the current UTC date for audit timestamps.
2. Capture the project root path for subagent communication.
3. Ensure the temp directory (`.claude/temp/`) exists.
4. Clean up any stale audit files if the user confirms.

The `plugin-development` skill provides authoritative validation guidance (auto-loaded when this command runs).

## What Gets Audited

- `.lsp.json` file structure and validity
- LSP server configuration fields
- Language/file type associations
- Server command and arguments
- Plugin manifest `lspServers` references

## Command Arguments

| Argument | Description |
| --- | --- |
| *(none)* | Audit all discoverable LSP configurations |
| `--force` | Audit regardless of modification status |
| `--skip-validation` | Skip finding validation (faster, but may include false positives) |

## Step 1: Discover LSP Configurations

Search for `.lsp.json` files in:

- Project root (`.lsp.json`)
- Plugin directories (`plugins/*/.lsp.json`)
- User plugins directory

Also check `plugin.json` manifests for `lspServers` field references.

Build a list of discovered LSP configurations with their scope (project, plugin, or user) and full path.

If no LSP configurations are found, report this and provide guidance on how to create one.

## Step 2: Parse Arguments

Check if the `--force` flag is present in the command arguments. Build the audit queue based on discovered configurations and the force flag.

## Step 3: Present Audit Plan

Display audit mode (SMART or FORCE), configurations discovered, and list each with scope and last modified date.

## Step 4: Execute Audits

For each LSP configuration, spawn the `plugin-component-auditor` subagent with the following context:

- Scope (project, plugin, or user)
- Full path to the `.lsp.json` file
- Associated plugin manifest (if applicable)
- Last audit date or "Never audited"
- Current audit date
- Project root path

Run subagents in parallel when multiple configurations exist.

Subagents write findings to `.claude/temp/` as both JSON (for recovery/aggregation) and markdown (for human review). The main conversation thread collects results and updates audit logs using its Write/Edit tools.

## Step 4.5: Validate Findings

**Unless `--skip-validation` flag is present:**

1. Spawn the `audit-finding-validator` agent with:
   - `project_root`: The captured project root path
   - `audit_type`: "lsp"
   - `audit_files`: List of `.claude/temp/audit-*-lsp-*.json` file paths
2. Wait for validation to complete
3. Read updated JSON files with validation results
4. Filter out FALSE_POSITIVE findings completely before aggregation
5. Note: Filtered findings are logged to `.claude/temp/audit-filtered-findings.json`

**If `--skip-validation` flag is present:**

- Skip validation phase entirely (current speed preserved)
- Present all findings without filtering
- Note in summary: "Validation: Skipped"

## Step 5: Final Summary

Report total configurations audited, results by scope, and details table. List configuration or server issues with remediation steps.

**Include validation statistics (if validation was performed):**

- Validation performed: Yes/No
- Findings validated: X
- False positives filtered: Y
- Verified findings: Z
- Unverified findings: W

## Important Notes

### LSP Configuration Requirements

LSP configurations must specify valid server commands, proper language associations, and correct initialization options.

### Configuration Locations

| Location | Purpose |
| --- | --- |
| `.lsp.json` (project root) | Project-specific LSP servers |
| `plugins/*/.lsp.json` | Plugin-provided LSP servers |
| Plugin manifest `lspServers` | Reference to LSP configurations |

### Common LSP Server Types

- TypeScript/JavaScript language servers
- Python language servers
- Go language servers
- Custom domain-specific servers

## Audit Log Location

All audit results are written to `.claude/audit/lsp.md`.

Use `/audit-log lsp` to view current audit status.

## Example Usage

### Example 1: Audit All LSP Configurations

```text
User: /audit-lsp

Claude: Discovering LSP configurations...

## Audit Plan
**Mode**: SMART
**Configurations discovered**: 2

1. [project] .lsp.json
2. [plugin] plugins/typescript/.lsp.json

[Spawns plugin-component-auditor subagents]

## Audit Complete
| Scope | Config | Result | Score |
| --- | --- | --- | --- |
| project | .lsp.json | PASS | 100/100 |
| plugin | typescript/.lsp.json | PASS | 95/100 |
```

### Example 2: Force Audit

```text
User: /audit-lsp --force

Claude: Auditing all LSP configurations (force mode)...
```
