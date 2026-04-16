# Agent Creation Guide

Complete guide for creating and configuring Claude Code subagents.

## Overview

Subagents are specialized AI assistants that handle specific types of tasks in isolated contexts. They provide:

- **Task Isolation**: Separate context for focused work
- **Tool Restrictions**: Limited access to only necessary tools
- **Model Selection**: Choose the best model for the task
- **Permission Control**: Custom permission handling modes

## File Structure

**File Format**: Markdown with YAML frontmatter
**Location**: `.claude/agents/[agent-name].md`

```markdown
---
name: agent-name
description: When to delegate to this agent
tools: Read, Write, Grep
model: sonnet
permissionMode: default
skills: skill-1, skill-2
hooks:
  PreToolUse:
    - matcher: 'Bash'
      hooks:
        - type: command
          command: './scripts/validate.sh'
---

# Agent System Prompt

[Agent instructions here]
```

## Frontmatter Fields

### Required Fields

**name** (string)

- Unique identifier for the agent
- Must be lowercase with hyphens only
- Examples: `code-reviewer`, `test-runner`, `data-analyzer`

**description** (string)

- When Claude should delegate to this subagent
- Include trigger terms users would naturally say
- Be specific about the agent's purpose
- Examples:
  - "Reviews code changes for quality, security, and best practices"
  - "Runs automated tests and reports results. Use when user asks to test code."
  - "Analyzes database schemas and suggests optimizations"

### Optional Fields

**tools** (array or comma-separated string)

- Allowlist of tools the agent can use
- If not specified, agent inherits all tools from parent
- Available tools: Read, Write, Edit, Bash, Grep, Glob, NotebookEdit, WebFetch, WebSearch, Skill, TodoWrite
- Syntax: `tools: Read, Write, Grep, Glob`
- Can restrict Bash with patterns: `Bash(python:*)`

**disallowedTools** (array or comma-separated string)

- Denylist of tools the agent cannot use
- Use when easier to block specific tools than list all allowed
- Syntax: `disallowedTools: Bash, Edit`
- Cannot be used with `tools` field

**model** (string)

- Model to use for this agent
- Can be a model alias (`sonnet`, `opus`, `haiku`, `inherit`) or specific model string
- Default: `sonnet` (if not specified)
- Use `inherit` to match the main conversation's model
- Recommendations:
  - `opus`: Complex reasoning, creative tasks
  - `sonnet`: General purpose, balanced
  - `haiku`: Fast, simple tasks

**permissionMode** (string)

- How to handle tool permissions
- Options:
  - `default`: Ask user for permission (standard behavior)
  - `acceptEdits`: Auto-approve edit-only operations
  - `dontAsk`: Auto-approve all operations (use cautiously)
  - `bypassPermissions`: Skip permission checks entirely
  - `plan`: Generate plan before execution
- Recommendations:
  - Use `default` for most agents
  - Use `acceptEdits` for trusted editing agents
  - Use `plan` for complex multi-step workflows
  - Avoid `bypassPermissions` unless necessary

**skills** (array or comma-separated string)

- Skills to load into agent context at startup
- Full skill content is injected, not just made available for invocation
- Syntax: `skills: skill-1, skill-2`
- Subagents don't inherit skills from the parent conversation
- Keep list minimal - only include necessary skills
- Skills add to context window size

**hooks** (object)

- Lifecycle hooks scoped to this agent
- See [Hooks Reference Guide](hooks-guide.md) for details
- Common hooks:
  - `PreToolUse`: Validate before tool execution
  - `PostToolUse`: Cleanup or logging after tool execution
  - `Stop`: Cleanup when agent completes

## System Prompt Structure

The content after frontmatter is the agent's system prompt. Structure it clearly:

```markdown
# Agent Name

[One-sentence description of the agent's role]

## Your Expertise

- [Area 1]
- [Area 2]
- [Area 3]

## Workflow

1. [Step 1]
2. [Step 2]
3. [Step 3]
4. [Step 4]

## Guidelines

- [Important rule 1]
- [Important rule 2]
- [Important rule 3]

## Examples

**Example 1**: [Scenario]
→ [How to handle]

**Example 2**: [Scenario]
→ [How to handle]
```

### System Prompt Best Practices

1. **Be specific**: Clearly define the agent's role and scope
2. **Include workflow**: Step-by-step process agents should follow
3. **Provide examples**: Concrete scenarios help agents understand context
4. **Set boundaries**: What the agent should NOT do
5. **Keep it concise**: Long prompts dilute important instructions
6. **Use formatting**: Headers, lists, and bold text for clarity

## Component Interaction

### Skills in Subagents

Load skills by listing them in the `skills` frontmatter field:

```yaml
---
name: api-developer
description: Develops REST APIs following best practices
tools: Read, Write, Edit, Bash
skills: api-design-patterns, security-best-practices
---
```

Important notes:

- Full skill content is injected at subagent startup
- Skills are not just "available" - they're loaded into context
- Keep skills list minimal to avoid context bloat
- Skills add to the agent's expertise immediately

### Commands Invoking Subagents

Commands delegate to subagents using the Task tool:

```markdown
---
description: Review code for quality issues
allowed-tools: Task(code-reviewer)
---

## Your Task

Use the Task tool to invoke the code-reviewer subagent:

- subagent_type: "code-reviewer"
- prompt: "Review the following files: [file list]"
```

### Tool Restrictions

**Inheritance**: Subagents inherit tools from parent by default

**Allowlist approach** (recommended for security):

```yaml
tools: Read, Grep, Glob # Only these tools allowed
```

**Denylist approach** (when most tools are needed):

```yaml
disallowedTools: Bash, Edit # All tools except these
```

**Pattern restrictions** (fine-grained control):

```yaml
tools: Read, Write, Bash(python:*) # Bash only for Python scripts
```

## Development Workflow

### Step 1: Identify the Need

Ask yourself:

- What task needs isolation?
- Does this require specialized behavior?
- Would tool restrictions improve security?
- Is this a repeated workflow?

### Step 2: Design the Interface

Define:

- What inputs does the agent need?
- What outputs should it provide?
- What tools are necessary?
- What model is appropriate?

### Step 3: Create the File

1. Create `.claude/agents/[name].md`
2. Add frontmatter with required fields
3. Write clear, focused system prompt
4. Include workflow steps
5. Add guidelines and examples

### Step 4: Write the System Prompt

Template:

```markdown
# [Agent Name]

You are [clear description of role and capabilities].

## Your Expertise

[List specific areas of expertise]

## Workflow

1. [First step - usually input validation]
2. [Middle steps - core processing]
3. [Final step - output formatting]

## Guidelines

- [Critical rules]
- [Best practices]
- [Common pitfalls to avoid]

## Examples

[Concrete examples showing expected behavior]
```

### Step 5: Test

1. Use `/agents` to verify agent appears in list
2. Test with representative tasks
3. Verify tool restrictions work
4. Check permission handling
5. Validate output quality

### Step 6: Iterate

Based on observed behavior:

- Refine description if agent doesn't trigger appropriately
- Adjust system prompt if behavior is off
- Modify tool restrictions if too restrictive or permissive
- Add examples if agent misunderstands common cases

## Troubleshooting

### Agent Not Loading

**Symptoms**: Agent doesn't appear in `/agents` list

**Solutions**:

1. Check file location: Must be in `.claude/agents/`
2. Verify YAML frontmatter syntax (no tabs, proper indentation)
3. Ensure `name` and `description` fields are present
4. Restart Claude Code session
5. Check for YAML parsing errors in logs

### Agent Not Triggering

**Symptoms**: Claude doesn't delegate to agent automatically

**Solutions**:

1. Review description - does it include trigger terms?
2. Make description more specific and detailed
3. Try explicit invocation: "Use the [agent-name] subagent to..."
4. Add more scenarios to description
5. Check if another agent has overlapping description

### Agent Has Wrong Tools

**Symptoms**: Permission errors or unexpected tool access

**Solutions**:

1. Verify `tools` or `disallowedTools` syntax
2. Check for tool name typos
3. Remember: `tools` is allowlist, `disallowedTools` is denylist
4. Cannot use both `tools` and `disallowedTools` together
5. Test with minimal tool set first

### Agent Behavior Incorrect

**Symptoms**: Agent doesn't follow instructions or makes mistakes

**Solutions**:

1. Simplify system prompt - less is often more
2. Add concrete examples of expected behavior
3. Use clearer workflow steps
4. Try different model (opus for complex reasoning)
5. Reduce loaded skills if context seems confused
6. Add explicit "do NOT" guidelines

### Skills Not Loading

**Symptoms**: Agent doesn't use skill knowledge

**Solutions**:

1. Verify skill names in `skills` field are correct
2. Check skills exist in `.claude/skills/[name]/SKILL.md`
3. Ensure skill SKILL.md has valid frontmatter
4. Try loading fewer skills (one at a time for testing)
5. Check skill file size - very large skills may cause issues

## Common Patterns

### Read-Only Research Agent

Use case: Safe exploration without modification risk

```yaml
---
name: codebase-explorer
description: Explores codebase to find information. Use when researching code structure or finding specific implementations.
tools: Read, Grep, Glob
model: haiku
permissionMode: plan
---
```

Benefits:

- Fast (haiku model)
- Safe (read-only tools)
- Structured (plan mode)

### High-Permission Editor Agent

Use case: Trusted automated editing

```yaml
---
name: code-formatter
description: Formats code according to style guidelines
tools: Read, Edit, Bash(prettier:*)
model: sonnet
permissionMode: acceptEdits
---
```

Benefits:

- Efficient (auto-approves edits)
- Restricted (only formatting tools)
- Controlled (pattern-limited Bash)

### Multi-Skill Specialist Agent

Use case: Domain expert with loaded knowledge

```yaml
---
name: api-developer
description: Develops REST APIs following best practices. Use when creating or modifying API endpoints.
tools: Read, Write, Edit, Bash(npm:*), Grep, Glob
model: sonnet
skills: api-design-patterns, security-best-practices, openapi-spec
permissionMode: default
---
```

Benefits:

- Expert knowledge loaded
- Full development tools
- Standard permissions

### Validation Agent with Hooks

Use case: Pre-flight checks before operations

```yaml
---
name: safe-deployer
description: Deploys code to production with validation checks
tools: Read, Bash
model: sonnet
permissionMode: plan
hooks:
  PreToolUse:
    - matcher: 'Bash'
      hooks:
        - type: command
          command: './scripts/pre-deploy-check.sh'
  Stop:
    - hooks:
        - type: command
          command: './scripts/post-deploy-notify.sh'
---
```

Benefits:

- Validation before execution
- Post-deployment cleanup
- Safety through planning

## Best Practices Summary

1. **Single Purpose**: Each agent should excel at one specific task
2. **Minimal Tools**: Only grant necessary tools for security
3. **Clear Descriptions**: Include trigger terms for automatic delegation
4. **Focused Prompts**: Concise system prompts with clear workflows
5. **Appropriate Model**: Match model to task complexity
6. **Load Relevant Skills**: Only include skills that are needed
7. **Test Thoroughly**: Verify behavior with representative tasks
8. **Iterate Based on Use**: Refine based on actual usage patterns
9. **Document Examples**: Show concrete scenarios in system prompt
10. **Use Hooks Wisely**: Add validation and cleanup where beneficial

## Advanced Topics

### Model Selection Strategy

**Use Opus when**:

- Complex reasoning required
- Creative problem solving
- Nuanced decision making
- Multi-step planning

**Use Sonnet when**:

- General purpose tasks
- Balanced speed and quality
- Most development work
- Standard agent operations

**Use Haiku when**:

- Simple, repetitive tasks
- Fast responses needed
- Read-only exploration
- Basic validation

### Permission Mode Strategy

**default**: Standard mode

- Use for most agents
- User reviews all operations
- Safest option

**acceptEdits**: Auto-approve edits

- Use for trusted editing agents
- Faster workflow for safe edits
- Still validates destructive operations

**plan**: Generate execution plan

- Use for complex workflows
- Shows steps before execution
- Good for learning agent behavior

**dontAsk**: Auto-approve all

- Use very sparingly
- Only for highly trusted, constrained agents
- Consider security implications

**bypassPermissions**: Skip all checks

- Rarely appropriate
- Only for internal automation
- Significant security risk

### Skill Loading Optimization

Tips for managing skills in agents:

1. **Load only what's needed**: Each skill adds to context
2. **Test incrementally**: Add skills one at a time
3. **Consider skill size**: Large skills consume more context
4. **Use progressive disclosure**: Split large skills into smaller ones
5. **Monitor behavior**: Too many skills can dilute focus

### Hook Integration

Common hook patterns for agents:

**Pre-validation**:

```yaml
hooks:
  PreToolUse:
    - matcher: 'Write|Edit'
      hooks:
        - type: command
          command: './scripts/validate-syntax.sh $TOOL_INPUT'
```

**Post-cleanup**:

```yaml
hooks:
  PostToolUse:
    - matcher: 'Bash'
      hooks:
        - type: command
          command: './scripts/cleanup-temp.sh'
```

**Agent lifecycle**:

```yaml
hooks:
  Stop:
    - hooks:
        - type: command
          command: './scripts/agent-summary.sh'
```

## Related Documentation

- [Skills Creation Guide](skills-guide.md) - How to create skills for agents
- [Commands Creation Guide](commands-guide.md) - How to invoke agents from commands
- [Hooks Reference Guide](hooks-guide.md) - Complete hooks documentation
- [Common Patterns & Examples](patterns-examples.md) - More agent examples

For official documentation, see [SKILL.md](SKILL.md#official-documentation).
