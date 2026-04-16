---
name: audit-agent-consolidation
description: Analyze agents for consolidation opportunities. Groups agents by configuration, tracks references, and manages refactoring.
argument-hint: [--force | --plugin-only | --project-only | --references | --impact <group> | --track | --execute <plan>]
allowed-tools: Read, Bash, Glob, Grep, Task
---

# Audit Agent Consolidation Command

Analyze agents for consolidation opportunities and track refactoring progress.

## Initialization

Before auditing, initialize the environment:

1. Get the current UTC date for audit timestamps.
2. Capture the project root path for subagent communication.
3. Ensure the temp directory (`.claude/temp/`) exists.
4. Load the `ecosystem-health` skill for consolidation criteria access.

## What Gets Analyzed

- **Configuration fields**: tools, model, permissionMode, skills, color
- **Grouping**: Agents grouped by tools + model + permissionMode
- **Reference tracking**: Commands, skills, memory, agents that reference each agent
- **Consolidation scoring**: Based on configuration similarity and reference impact
- **Skills analysis**: Different skills = different purpose (auto-load guarantee)

## Command Arguments

| Argument | Description |
| --- | --- |
| *(none)* | Analyze mode: discover agents, group by config, recommend consolidation |
| `--force` | Re-analyze even if recent analysis exists (<24h) |
| `--plugin-only` | Only analyze plugin agents (`plugins/*/agents/`) |
| `--project-only` | Only analyze project agents (`.claude/agents/`) |
| `--references` | Show all component references for each agent |
| `--impact <group>` | Show detailed impact analysis for consolidating a specific group |
| `--track` | Persist analysis to tracking file in `.claude/temp/` |
| `--execute <plan>` | Execute consolidation plan (interactive with confirmation) |

## Modes of Operation

### Analyze Mode (Default)

Discovers agents, groups by configuration, calculates consolidation scores.

**Steps:**

1. Discover all agent files based on scope
2. Parse YAML frontmatter for each agent
3. Group agents by tools + model + permissionMode
4. Calculate consolidation scores using criteria from ecosystem-health skill
5. Generate recommendations
6. Display summary

### References Mode (`--references`)

Shows all components that reference each agent.

**Searches:**

- Skills: `skills/*/SKILL.md` for delegation patterns and Task invocations
- Memory: `.claude/memory/*.md` for agent references
- Agents: `agents/*.md` for chaining patterns

### Impact Mode (`--impact <group>`)

Shows detailed analysis of what would break if a group is consolidated.

**Reports:**

- All references to agents in the group
- Estimated refactoring effort
- Risk assessment
- Suggested migration path

### Track Mode (`--track`)

Persists analysis to `.claude/temp/agent-consolidation-{timestamp}.json` for:

- Multi-session consolidation efforts
- Progress tracking
- Historical comparison

### Execute Mode (`--execute <plan>`)

Interactive mode to apply a consolidation plan.

**REQUIRES explicit user confirmation for each step.**

## Step 1: Parse Arguments

Check for mode flags:

- `--force`: Set force_reanalyze = true
- `--plugin-only`: Set scope = "plugin"
- `--project-only`: Set scope = "project"
- `--references`: Set mode = "references"
- `--impact <group>`: Set mode = "impact", capture group ID
- `--track`: Set track = true
- `--execute <plan>`: Set mode = "execute", capture plan path

Default: mode = "analyze", scope = "all"

## Step 2: Discover Agents

Search for agent files based on scope:

**Plugin agents:**

- `plugins/*/agents/*.md`

**Project agents:**

- `.claude/agents/*.md`

**User agents (if scope = all):**

- `~/.claude/agents/*.md` (note: may not be accessible)

Build list of discovered agents with:

- Full path
- Scope (plugin:<name>, project, user)
- Last modified date

## Step 3: Present Discovery Summary

```text
## Agent Discovery

**Scope**: [ALL | PLUGIN | PROJECT]
**Agents Found**: [N]

| Scope | Count | Location |
| ----- | ----- | -------- |
| plugin:claude-ecosystem | 17 | plugins/claude-ecosystem/agents/ |
| plugin:code-quality | 3 | plugins/code-quality/agents/ |
| project | 2 | .claude/agents/ |
```

## Step 4: Execute Analysis

For Analyze mode, spawn `agent-consolidation-analyst` subagent with context:

- Scope (plugin:name, project, all)
- List of agent file paths
- Project root for output files
- Current UTC timestamp

**For large agent counts (>10), batch into groups of 5 for parallel analysis.**

The subagent will:

1. Parse all agent YAML frontmatter
2. Group by configuration
3. Search for references
4. Calculate scores
5. Write dual output (JSON + Markdown) to `.claude/temp/`

## Step 5: Aggregate Results

After subagent(s) complete:

1. Read JSON output file(s) from `.claude/temp/`
2. Aggregate groups and recommendations
3. Calculate totals

## Step 6: Display Results

### Analyze Mode Output

```text
Agent Consolidation Analysis
============================

Scope: [scope]
Agents Analyzed: [N]
Groups Found: [N]

Configuration Groups:
---------------------

Group 1: auditor-opus-plan ([N] agents)
  Config: tools=[standard+MCP], model=opus, permissionMode=plan
  Members:
    - skill-auditor (skills: skill-development) [2 refs]
    - skill-auditor (skills: skill-development) [2 refs, handles both skills and commands]
    - agent-auditor (skills: subagent-development) [2 refs]
    - hook-auditor (skills: hook-management) [2 refs]
    ... ([N] more)

  Consolidation: NO
  Score: 45/100
  Reason: Each agent's `skills:` field provides domain-specific
          knowledge via auto-load guarantee. Cannot replicate via
          Task tool prompt injection.

Group 2: researcher-haiku ([N] agents)
  Config: tools=[Read,Grep,WebFetch], model=haiku
  Members:
    - docs-researcher (skills: none) [1 ref]
    - issue-researcher (skills: none) [3 refs]

  Consolidation: REVIEW
  Score: 78/100
  Reason: Similar purpose, no skills field. Could potentially merge
          with query-based specialization in prompt.

Recommendations:
----------------
1. [NO ACTION] auditor-opus-plan - skills: auto-load justifies separation
2. [REVIEW] researcher-haiku - Consider meta-skill approach

Total Reference Count: [N]
Highest Impact Agent: [agent-name] ([N] references)
```

### References Mode Output

```text
Agent References Analysis
=========================

skill-auditor:
  Commands: 1
    - audit-skills.md:87 "spawn skill-auditor agent"
  Skills: 0
  Memory: 1
    - audit-protocol.md:45 "uses skill-auditor for validation"
  Total: 2 references

skill-auditor (commands):
  Commands: 1
    - audit-skills.md:66 "spawn skill-auditor agent"
  Skills: 0
  Memory: 1
    - audit-protocol.md:48 "uses skill-auditor for validation"
  Total: 2 references

...
```

### Track Mode

After analysis, if `--track` flag:

```text
Analysis persisted to:
  .claude/temp/agent-consolidation-2026-01-10T193000Z.json

Use --execute to apply consolidation plan.
```

## Important Notes

### The `skills:` Auto-Load Guarantee

**CRITICAL:** The `skills:` field provides an auto-load guarantee:

- Skill loads AUTOMATICALLY when agent starts
- No prompt required, no Claude decision needed
- Consistent, reliable domain knowledge

**Task tool CANNOT replicate this:**

- Cannot specify `skills:` parameter in Task tool
- Must describe skill content in prompt (token bloat)
- Claude must decide to invoke Skill tool (not guaranteed)

**Therefore:** Agents with different `skills:` fields should NOT be consolidated unless their skills can be merged into one meta-skill.

### Configuration Field Weights

| Field | Weight | Notes |
| ----- | ------ | ----- |
| `tools` | HIGH | Different tools = different capabilities |
| `model` | HIGH | Different models = different cost/capability |
| `permissionMode` | MEDIUM | Affects security posture |
| `skills` | CRITICAL | Auto-load guarantee cannot be replicated |
| `color` | LOW | Cosmetic, ignored for grouping |

### Scoring Thresholds

| Score | Recommendation | Action |
| ----- | -------------- | ------ |
| 85-100 | CONSOLIDATE | Strong candidate for merging |
| 70-84 | REVIEW | May consolidate with skill refactoring |
| 50-69 | UNLIKELY | Keep separate unless skills merge |
| 0-49 | NO ACTION | Different purposes, keep separate |

### Plugin Isolation Constraint

**CRITICAL:** Plugins cannot reference resources outside their individual plugin directory.

This means:

- Agents in `plugin-a/agents/` cannot consolidate with agents in `plugin-b/agents/`
- Cross-plugin consolidation is **architecturally impossible**
- Only agents within the SAME plugin can be consolidated
- When analyzing consolidation candidates, group only by plugin scope

When the analysis identifies similar agents across different plugins (e.g., `*-docs-researcher` agents), these should be noted as following a common **pattern** but are NOT consolidation candidates.

**Scope filtering recommendation:**

- Use `--plugin-only` and analyze each plugin separately
- Group recommendations by plugin, not globally
- Cross-plugin patterns inform template standardization, not consolidation

## Example Usage

### Example 1: Analyze All Agents

```text
User: /audit-agent-consolidation

Claude: Discovering agents...

## Agent Discovery
Scope: ALL
Agents Found: 22

[Analysis proceeds...]

Agent Consolidation Analysis
============================
...
```

### Example 2: Plugin-Only Analysis

```text
User: /audit-agent-consolidation --plugin-only

Claude: Discovering plugin agents only...

## Agent Discovery
Scope: PLUGIN
Agents Found: 20
...
```

### Example 3: Show References

```text
User: /audit-agent-consolidation --references

Claude: Analyzing agent references...

Agent References Analysis
=========================
...
```

### Example 4: Track for Multi-Session

```text
User: /audit-agent-consolidation --track

Claude: [Analysis...]

Analysis persisted to:
  .claude/temp/agent-consolidation-2026-01-10T193000Z.json
```

### Example 5: Impact Analysis

```text
User: /audit-agent-consolidation --impact auditor-opus-plan

Claude: Analyzing impact for group: auditor-opus-plan

Impact Analysis: auditor-opus-plan
==================================

Agents in Group: 13
Total References: 26

If consolidated, would need to update:
  - 13 command files (Task invocations)
  - 13 memory references

Risk Assessment: HIGH
Reason: skills: field provides domain-specific knowledge

Recommendation: Do NOT consolidate. The auto-load guarantee
cannot be replicated via Task tool.
```

## Ecosystem Health Integration

This command integrates with the `ecosystem-health` skill:

- Uses `references/consolidation-criteria.md` for scoring rubric
- Contributes to component coverage tracking
- Supports the audit orchestration workflow

Run `/ecosystem-health --status` to see overall audit coverage including agent consolidation.
