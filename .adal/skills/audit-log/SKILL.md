---
name: audit-log
description: View audit log entries for all component types (skills, commands, agents, hooks, etc.) to monitor audit health and track coverage
argument-hint: "[component-type] [plugin:name | project | all]"
allowed-tools: Read, Grep, Bash, Glob
---

# Audit Log

View audit log entries from all discovered sources in the repository. Use this command to monitor audit health, identify components needing re-auditing (>90 days old or never audited), and track audit coverage across your codebase.

## Supported Component Types

- **skills** - Skill audit logs
- **commands** - Command audit logs
- **agents** - Agent audit logs
- **hooks** - Hook audit logs
- **memory** - CLAUDE.md file audit logs
- **mcp** - MCP configuration audit logs
- **settings** - Settings file audit logs
- **plugins** - Plugin manifest audit logs
- **output-styles** - Output style audit logs
- **statuslines** - Status line audit logs

## Arguments

- **No argument** or **all**: Show summary of ALL audit logs across all component types
- **{component-type}**: Filter to specific type (e.g., `skills`, `commands`, `agents`)

## Audit Log Location

All audit logs are stored in `.claude/audit/`:

```text
.claude/audit/
├── skills.md        # Skill audits
├── commands.md      # Command audits
├── agents.md        # Agent audits
├── hooks.md         # Hook audits
├── memory.md        # CLAUDE.md file audits
├── mcp.md           # MCP config audits
├── settings.md      # Settings file audits
├── plugins.md       # Plugin manifest audits
├── output-styles.md # Output style audits
└── statuslines.md   # Status line audits
```

## Discovery

Read audit logs from `.claude/audit/{type}.md` for each component type.

Component types: skills, commands, agents, hooks, memory, mcp, settings, plugins, output-styles, statuslines.

## Display Format

### Summary View (default)

When no component type specified, show a summary across all types:

```markdown
# Audit Log Summary

## By Component Type

| Type | Total | Recent | Stale | Never |
| --- | --- | --- | --- | --- |
| Skills | 15 | 12 | 2 | 1 |
| Commands | 27 | 20 | 5 | 2 |
| Agents | 8 | 6 | 1 | 1 |

## Sources Discovered

**Location**: `.claude/audit/`
- skills.md (15 entries)
- commands.md (27 entries)
- agents.md (8 entries)

## Items Needing Attention

Run `/audit-log {type}` to see details for a specific component type.
Run `/audit-{type}` to audit components (e.g., `/audit-skills`, `/audit-agents`).
```

### Component Type View

When component type specified (e.g., `/audit-log commands`), show detailed view:

```markdown
# Command Audit Log

**Location**: .claude/audit/commands.md

| Command | Last Audit | Days Ago | Status |
| --- | --- | --- | --- |
| audit-log | 2025-12-17 | 8 | Recent |
| audit-skills | 2025-12-17 | 8 | Recent |
| scrape-docs | 2025-10-01 | 85 | Recent |
| scrape-claude-docs | 2025-12-15 | 10 | Recent |

**Stats**: 27 commands, 20 recent, 5 stale, 2 never audited
```

## Staleness Rules

- **Recent**: Audited within last 90 days
- **Stale**: Last audit > 90 days ago
- **Never Audited**: No audit date recorded

## Error Handling

If no audit logs found for requested type:

```markdown
# No Audit Logs Found

No {type} audit logs were found in this repository.

**Checked location**: .claude/audit/{type}.md (not found)

**To create audit logs**, run `/audit-{type}` to audit your {type}.
Audit logs are created automatically when components are audited.
```

## Example Usage

### Example 1: View All Audit Logs (Summary)

```text
User: /audit-log

Claude: Discovering audit logs...

# Audit Log Summary

## By Component Type

| Type | Total | Recent | Stale | Never |
| --- | --- | --- | --- | --- |
| Skills | 15 | 12 | 2 | 1 |
| Commands | 27 | 25 | 2 | 0 |
| Agents | 8 | 6 | 1 | 1 |

## Sources Discovered

**Location**: `.claude/audit/`
- skills.md
- commands.md
- agents.md

## Items Needing Attention

- 3 skills need re-audit
- 2 commands need re-audit
- 2 agents need re-audit

Run `/audit-log skills` to see skill details.
```

### Example 2: View Command Audit Logs

```text
User: /audit-log commands

Claude: Reading command audit logs...

# Command Audit Log

**Location**: .claude/audit/commands.md

| Command | Last Audit | Days Ago | Status |
| --- | --- | --- | --- |
| audit-log | 2025-12-17 | 8 | Recent |
| audit-skills | 2025-12-17 | 8 | Recent |

**Stats**: 27 commands, 25 recent, 2 stale, 0 never audited
```

### Example 3: View Skills Only

```text
User: /audit-log skills

Claude: Reading skill audit logs...

# Skill Audit Log

**Location**: .claude/audit/skills.md

| Skill | Last Audit | Days Ago | Status |
| --- | --- | --- | --- |
| docs-management | 2025-12-17 | 8 | Recent |
| skill-development | 2025-12-17 | 8 | Recent |

**Stats**: 15 skills, 12 recent, 2 stale, 1 never audited
```
