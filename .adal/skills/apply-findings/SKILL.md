---
name: apply-findings
description: Apply fixes from audit or review findings. Use after /audit-* or /review commands to implement recommendations from the current conversation.
argument-hint: "[--dry-run] [--research-first]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, Task, Skill
---

# Apply Findings Command

Apply all fixes, improvements, recommendations, and suggestions from audit/review findings in the current conversation.

## Arguments

- `$ARGUMENTS` may contain:
  - `--dry-run`: Show what would be implemented without making changes
  - `--research-first`: Force MCP research even for Claude Code content (adds extra validation layer)

## Workflow

### Step 1: Context Analysis

Scan the current conversation for actionable items:

- Audit findings (issues, warnings, errors)
- Code review suggestions
- Improvement recommendations
- Numbered TODO items
- Severity-tagged items (CRITICAL, HIGH, MEDIUM, LOW)

Create a prioritized list of items to implement, grouped by:

1. **CRITICAL** - Must fix immediately
2. **HIGH** - Should fix before completion
3. **MEDIUM** - Recommended improvements
4. **LOW** - Nice-to-have enhancements
5. **INFO** - Suggestions without severity

**If no actionable items are found**, report "No actionable findings found in current conversation" and STOP.

**If `--dry-run` is specified**, report the prioritized list and STOP here without making changes.

### Step 2: Categorize Findings

Categorize each finding as either:

- **Claude Code content**: plugins, skills, agents, commands, hooks, output-styles, CLAUDE.md, memory files, MCP config
- **External content**: application code, libraries, frameworks, infrastructure, general patterns

**Detection criteria for Claude Code content:**

- File paths containing `plugins/*/`, `.claude/`, `CLAUDE.md`
- Component keywords: skill, agent, command, hook, output-style, MCP server, YAML frontmatter

### Step 3: Research Phase (Automatic)

Research is **automatic by default** - no flag needed. The approach varies by content type:

#### For Claude Code Content

**Try claude-ecosystem skills first:**

1. **Attempt to invoke `docs-management` skill** for official documentation
2. **Spawn `claude-code-guide` subagent** in parallel for live web verification:

   ```text
   Task(claude-code-guide): "WebFetch https://code.claude.com/docs/en/claude_code_docs_map.md
   to find relevant pages about [detected component types]. Then WebFetch those specific pages.
   Return key findings with source URLs. Do NOT use Skill tool."
   ```

3. **Load relevant development skills** based on component type:
   - Skills → `skill-development`
   - Agents → `subagent-development`
   - Commands → `skill-development`
   - Hooks → `hook-management`
   - Output styles → `output-customization`
   - MCP → `mcp-integration`
   - Memory files → `memory-management`

**Fallback to MCP if:**

- `docs-management` skill is not available (claude-ecosystem plugin not installed)
- Skills don't return sufficient guidance for the specific finding
- `--research-first` flag was specified (adds MCP as extra validation layer)

Fallback uses `mcp-research` agent with query: "Claude Code [component type] best practices [specific topic]"

#### For External Content (Non-Claude Code)

**Use MCP research when findings involve:**

- API usage patterns or library-specific implementations
- Architectural decisions or design patterns
- Security concerns or best practices
- Framework conventions or configuration
- Version-specific behavior or breaking changes
- Performance optimizations or trade-offs

**Skip MCP research for trivial fixes:**

- Typos, formatting, naming conventions
- Obvious bug fixes with clear solutions
- Simple refactors already specified in the finding

**When research is needed**, delegate to `mcp-research` agent:

```text
Task(mcp-research): "Research best practices for [implementation topics from findings].
Use microsoft-learn for .NET/Azure, context7+ref for libraries, perplexity for general validation.
Return actionable guidance with citations."
```

This validates concepts and approaches against current documentation without over-researching mechanical fixes.

### Step 4: Implementation

For each item in priority order (CRITICAL -> HIGH -> MEDIUM -> LOW -> INFO):

1. **State the item** being implemented with its source (e.g., "Audit finding #3: Missing description field")

2. **Apply the fix/improvement** using appropriate tools:
   - `Edit` for code modifications
   - `Write` for new files
   - `Bash` for commands/scripts

3. **Verify the change**:
   - For code: lint check if applicable
   - For config: validate syntax
   - For Claude Code components: basic structure validation

4. **Mark item status**:
   - ✅ Implemented successfully
   - ⏭️ Skipped (with reason)
   - ❌ Failed (with error)

**Continue through all items**, logging each result.

### Step 5: Summary Report

After all items processed, provide a summary:

```markdown
## Apply Findings Summary

**Total items found:** X
**Implemented:** Y ✅
**Skipped:** Z ⏭️
**Failed:** W ❌

### Implemented
- [item 1 description]
- [item 2 description]

### Skipped (if any)
- [item] - Reason: [why skipped]

### Failed (if any)
- [item] - Error: [what went wrong]

### Follow-up Actions (if any)
- [suggested manual steps for failed items]
- [verification commands to run]
```

## Usage Examples

### After an audit

```text
/claude-ecosystem:audit-skills my-skill
# ... audit output with findings ...
/apply-findings
```

### Preview changes first

```text
/apply-findings --dry-run
```

### Extra validation for Claude Code changes

```text
# When you want MCP to double-check Claude Code skill/docs-management guidance
/apply-findings --research-first
```

### After code review

```text
# Review finds issues...
/apply-findings
```

## Important Notes

- This command operates on the **current conversation context**
- It looks for actionable items in recent messages (audits, reviews, analysis output)
- If no actionable items are found, it reports that and exits
- **Research is smart by default:**
  - Claude Code content → tries docs-management + claude-code-guide first, falls back to MCP
  - External content (conceptual/architectural) → uses MCP to validate approach
  - Trivial fixes (typos, formatting, obvious bugs) → applies directly without research
  - Works even if claude-ecosystem plugin is not installed (falls back to MCP)
- `--research-first` adds MCP as an extra validation layer for Claude Code content
- Items are applied in priority order - critical issues first
- Each change is verified before moving to the next item
