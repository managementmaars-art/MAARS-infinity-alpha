# Skills Creation Guide

Complete guide for creating and configuring Claude Code skills.

## Overview

Skills are reusable knowledge packages that can be loaded into conversations or subagents. They provide:

- **Domain Expertise**: Specialized knowledge Claude lacks
- **Terminology**: Domain-specific vocabulary and patterns
- **Best Practices**: Guidelines for specific tasks
- **Progressive Disclosure**: Split large content across files

## File Structure

**File Format**: Markdown with YAML frontmatter
**Location**: `.claude/skills/[skill-name]/SKILL.md`

```markdown
---
name: skill-name
description: What this skill does and when to use it
allowed-tools: Read, Bash
model: sonnet
context: fork
user-invocable: true
---

# Skill Name

## Overview

[Brief overview of skill purpose]

## Core Content

[Main knowledge organized with clear headings]

## Examples

[Concrete usage examples]

## Best Practices

[Guidelines for applying this knowledge]
```

## Frontmatter Fields

### Required Fields

**name** (string, max 64 chars)

- Skill identifier
- Must be lowercase with hyphens only
- Gerund form preferred: `analyzing-data`, `processing-pdfs`
- Also acceptable: `data-analysis`, `pdf-processing`
- Avoid vague names: `helper`, `utils`, `tools`
- Examples: `api-design-patterns`, `security-best-practices`

**description** (string, max 1024 chars)

- What the skill does and when to use it
- Include trigger terms users would naturally say
- Be specific about the skill's domain
- Examples:
  - "REST API design patterns and best practices. Use when designing or reviewing APIs."
  - "Python testing with pytest. Use when writing or debugging Python tests."
  - "SQL query optimization techniques. Use when analyzing or improving database queries."

### Optional Fields

**allowed-tools** (array or comma-separated string)

- Tools Claude can use without asking permission when this skill is active
- Only applies during skill execution scope
- Syntax: `allowed-tools: Read, Bash(python:*)`
- Supports comma-separated values or YAML-style lists
- Use for skills that need specific tool access

**model** (string)

- Model to use when skill is active
- Can be a model alias (`sonnet`, `opus`, `haiku`) or specific model string (e.g., `claude-sonnet-4-20250514`)
- Default: inherits from parent context
- Use when skill requires specific model capabilities

**context** (string)

- Set to `fork` to run skill in isolated sub-agent context with its own conversation history
- Creates separate conversation thread
- Useful for complex multi-step workflows
- Default: runs in current context

**agent** (string)

- Specify which agent type to use when `context: fork` is set
- Can reference: `Explore`, `Plan`, `general-purpose`, or a custom agent name from `.claude/agents/`
- Defaults to `general-purpose` if not specified
- Only valid with `context: fork`

**hooks** (object)

- Lifecycle hooks scoped to skill execution
- Supports `PreToolUse`, `PostToolUse`, and `Stop` events
- See [Hooks Reference Guide](hooks-guide.md) for details
- Hooks automatically cleaned up when skill completes

**user-invocable** (boolean)

- Controls whether the skill appears in the slash command menu
- Does not affect the `Skill` tool or automatic discovery
- Default: `true`
- Set to `false` for skills only used internally by agents or Claude programmatically

## Content Structure

### Basic Skill Template

```markdown
---
name: skill-name
description: Clear description with trigger terms
---

# Skill Name

## Overview

Brief 2-3 sentence overview of what this skill provides.

## Core Concepts

### Concept 1

[Explanation with examples]

### Concept 2

[Explanation with examples]

## Quick Reference

- Key point 1
- Key point 2
- Key point 3

## Examples

### Example 1: [Scenario]

[Concrete example with code or steps]

### Example 2: [Scenario]

[Concrete example with code or steps]

## Best Practices

1. [Practice 1]
2. [Practice 2]
3. [Practice 3]

## Common Pitfalls

- [Pitfall 1 and how to avoid]
- [Pitfall 2 and how to avoid]
```

### Content Best Practices

1. **Be concise**: Assume Claude is smart, avoid over-explaining
2. **Use examples**: Concrete examples beat abstract explanations
3. **Stay current**: Avoid time-sensitive information (dates, versions)
4. **Structure clearly**: Use headings, lists, and formatting
5. **Focus on gaps**: Only include what Claude doesn't already know
6. **Provide context**: Explain when and why to use techniques
7. **Add references**: Link to external documentation when helpful

## Progressive Disclosure Pattern

For skills over 500 lines, split content across multiple files:

```
skill-name/
├── SKILL.md              # Main overview with links (< 500 lines)
├── reference.md          # Detailed reference information
├── examples.md           # Extended usage examples
├── advanced.md           # Advanced topics
└── scripts/
    └── helper.py         # Utility scripts (executed, not loaded)
```

### SKILL.md with Progressive Disclosure

```markdown
---
name: large-skill
description: Comprehensive knowledge area
---

# Large Skill

## Quick Start

[Essential information for getting started]

## Core Concepts

[Fundamental concepts and patterns]

## Detailed Topics

For in-depth coverage, see:

- **API Reference**: [reference.md](reference.md) - Complete API documentation
- **Usage Examples**: [examples.md](examples.md) - Real-world usage patterns
- **Advanced Topics**: [advanced.md](advanced.md) - Complex scenarios and edge cases

## Quick Reference

[Most commonly used information]

## Utility Scripts

This skill includes helper scripts:

- `python scripts/validate.py <input>` - Validates input format
- `python scripts/generate.py <options>` - Generates boilerplate

Run from the skill directory: `.claude/skills/large-skill/`
```

### Progressive Disclosure Rules

1. **One level deep**: `SKILL.md → reference.md`, not `SKILL.md → advanced.md → details.md`
2. **Clear boundaries**: Each file covers distinct topics
3. **Self-contained**: Each file can be understood independently
4. **Main file focus**: SKILL.md should be immediately useful
5. **Use TOC for long files**: Files >100 lines need table of contents

### When to Use Progressive Disclosure

**Use progressive disclosure when**:

- SKILL.md exceeds 500 lines
- Content has clear topic boundaries
- Some content is advanced/rarely needed
- Examples are extensive

**Keep single file when**:

- Content is under 500 lines
- Topics are tightly coupled
- All content is equally important
- Splitting would harm readability

## Development Workflow

### Step 1: Identify the Knowledge Gap

Ask yourself:

- What does Claude need to know?
- What domain-specific terms exist?
- What patterns or best practices apply?
- When would this knowledge be useful?

### Step 2: Gather Information

Collect:

- Terminology and definitions
- Common patterns and anti-patterns
- Best practices and guidelines
- Concrete examples
- Reference documentation

### Step 3: Organize Content

Structure with:

1. Overview (what and why)
2. Core concepts (fundamentals)
3. Quick reference (commonly used info)
4. Examples (concrete usage)
5. Best practices (how to use well)
6. Pitfalls (what to avoid)

### Step 4: Create the Skill

1. Create directory: `.claude/skills/[name]/`
2. Create `SKILL.md` with frontmatter
3. Write concise, focused content
4. Add concrete examples
5. Include trigger terms in description

### Step 5: Test

1. Load skill manually or via agent
2. Test with tasks that should trigger it
3. Verify terminology is applied correctly
4. Check if examples are helpful
5. Validate skill triggers appropriately

### Step 6: Refine

Based on observed behavior:

- Adjust description if skill doesn't trigger
- Simplify content if Claude seems confused
- Add examples for common misunderstandings
- Split into multiple files if too large
- Remove redundant information

## Usage in Components

### Skills in Subagents

Load skills into agents via the `skills` frontmatter field:

```yaml
---
name: api-developer
description: Develops REST APIs
tools: Read, Write, Edit
skills: api-design-patterns, openapi-spec, security-best-practices
---
```

Key points:

- Full skill content is injected at agent startup
- Skills are in agent's context immediately
- Keep skills list minimal to avoid context bloat
- Skills persist for entire agent session

### Skills in Commands

Commands can reference skills indirectly through agents:

```markdown
---
description: Design a REST API
allowed-tools: Task(api-developer)
---

## Your Task

The api-developer agent has api-design-patterns skill loaded.
Delegate to that agent for API design tasks.
```

### Skills with Forked Context

Advanced pattern for isolated skill execution:

```yaml
---
name: complex-analysis
description: Complex data analysis with isolation
context: fork
agent: data-analyzer
allowed-tools: Read, Bash(python:*)
---
```

Benefits:

- Isolated context for focused work
- Can use specialized agent
- Cleanup automatic when complete

## Troubleshooting

### Skill Not Loading

**Symptoms**: Skill doesn't appear or isn't available

**Solutions**:

1. Check file location: `.claude/skills/[name]/SKILL.md`
2. Verify YAML frontmatter is valid
3. Ensure `name` and `description` fields present
4. Check for YAML syntax errors (no tabs)
5. Restart Claude Code session
6. For agent skills, verify `skills` list in agent frontmatter

### Skill Not Being Applied

**Symptoms**: Skill loaded but knowledge not used

**Solutions**:

1. Check description includes clear trigger terms
2. Make description more specific
3. Verify content is concise and clear
4. Reduce content if overly verbose
5. Add concrete examples showing usage
6. Check if multiple skills conflict

### Skill Causing Confusion

**Symptoms**: Claude behaves incorrectly with skill loaded

**Solutions**:

1. Simplify content - less is often more
2. Remove information Claude already knows
3. Focus on gaps in Claude's knowledge
4. Add clear examples of correct usage
5. Split into smaller, focused skills
6. Check for contradictory information

### Progressive Disclosure Not Working

**Symptoms**: Linked files not being read

**Solutions**:

1. Verify relative paths are correct
2. Ensure linked files exist in skill directory
3. Check markdown link syntax: `[text](file.md)`
4. Don't nest more than one level deep
5. Make each file self-contained
6. Test links manually

## Common Patterns

### Domain Terminology Skill

Use case: Industry-specific vocabulary

```markdown
---
name: kubernetes-terminology
description: Kubernetes architecture and terminology. Use when working with K8s.
---

# Kubernetes Terminology

## Core Concepts

- **Pod**: Smallest deployable unit, one or more containers
- **Deployment**: Manages replica sets and rolling updates
- **Service**: Stable network endpoint for pods
- **Ingress**: HTTP/HTTPS routing to services

## Quick Reference

[Essential commands and patterns]

## Examples

[Concrete K8s configuration examples]
```

### API/Library Reference Skill

Use case: Framework-specific knowledge

```markdown
---
name: fastapi-patterns
description: FastAPI web framework patterns. Use when building FastAPI applications.
allowed-tools: Read, Bash(python:*)
---

# FastAPI Patterns

## Quick Start

[Basic app structure]

## Core Patterns

### Dependency Injection

[Explanation with code examples]

### Request Validation

[Explanation with code examples]

## Detailed Reference

See [reference.md](reference.md) for complete API documentation.
```

### Best Practices Skill

Use case: Guidelines and conventions

```markdown
---
name: code-review-guidelines
description: Code review best practices. Use when reviewing code or providing feedback.
---

# Code Review Guidelines

## Principles

1. Be constructive and specific
2. Focus on code, not author
3. Explain the "why" behind suggestions
4. Prioritize by severity

## Review Checklist

- [ ] Security vulnerabilities
- [ ] Performance issues
- [ ] Code clarity and maintainability
- [ ] Test coverage

## Examples

[Good and bad review comments]
```

### Process/Workflow Skill

Use case: Step-by-step procedures

```markdown
---
name: deployment-workflow
description: Production deployment process. Use when deploying to production.
---

# Deployment Workflow

## Pre-Deployment Checklist

1. All tests passing
2. Code reviewed and approved
3. Staging validation complete
4. Rollback plan prepared

## Deployment Steps

1. [Step 1]
2. [Step 2]
3. [Step 3]

## Post-Deployment Verification

[Validation steps]

## Rollback Procedure

[Emergency rollback steps]
```

## Best Practices Summary

1. **Be concise**: Only include what Claude doesn't know
2. **Use progressive disclosure**: Split files over 500 lines
3. **Keep references one level deep**: Don't nest deeply
4. **Include trigger terms**: Help skill load automatically
5. **Provide examples**: Concrete beats abstract
6. **Stay current**: Avoid time-sensitive information
7. **Structure clearly**: Use headings and formatting
8. **Test thoroughly**: Verify skill improves behavior
9. **Focus on gaps**: Don't explain what Claude knows
10. **Add TOC for long files**: Files >100 lines need contents

## Advanced Topics

### Tool Permissions in Skills

Skills can specify allowed tools:

```yaml
---
name: python-testing
description: Python testing with pytest
allowed-tools: Read, Bash(python:*, pytest:*)
---
```

Benefits:

- Tools available without permission during skill execution
- Scoped to skill's operation
- Automatically cleaned up

Limitations:

- Only applies when skill is actively executing
- Parent context permissions still apply
- Use sparingly for security

### Model Selection in Skills

Skills can specify required model:

```yaml
---
name: creative-writing
description: Creative writing techniques and styles
model: opus
---
```

Use cases:

- Complex reasoning tasks need opus
- Simple lookup tasks can use haiku
- Most skills work with default (sonnet)

### Forked Context Skills

Advanced isolation pattern:

```yaml
---
name: sensitive-analysis
description: Analyzes sensitive data in isolation
context: fork
agent: data-analyzer
allowed-tools: Read
---
```

When to use:

- Sensitive data processing
- Complex multi-step workflows
- Need complete context isolation
- Want automatic cleanup

Trade-offs:

- Higher overhead (separate context)
- Can't access parent context easily
- Good for security and isolation

### Hook Integration

Skills can include lifecycle hooks:

```yaml
---
name: validated-edits
description: File editing with validation
hooks:
  PreToolUse:
    - matcher: 'Write|Edit'
      hooks:
        - type: command
          command: './scripts/validate-syntax.sh $TOOL_INPUT'
---
```

Use cases:

- Pre-validation before operations
- Post-processing after tool use
- Logging and monitoring
- Cleanup operations

## Related Documentation

- [Agent Creation Guide](agents-guide.md) - Loading skills into agents
- [Commands Creation Guide](commands-guide.md) - Using skills in commands
- [Hooks Reference Guide](hooks-guide.md) - Adding hooks to skills
- [Common Patterns & Examples](patterns-examples.md) - More skill examples

For official documentation, see [SKILL.md](SKILL.md#official-documentation).
