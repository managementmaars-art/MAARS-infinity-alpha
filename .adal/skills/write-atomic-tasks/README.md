# write-atomic-tasks

A skill for writing precise, autonomous-execution-ready tasks using the SMART+ framework.

## What This Skill Provides

This skill transforms vague task descriptions into detailed specifications that enable autonomous agent execution without clarifying questions. It extracts and formalizes the task precision guidelines from the todo-manager agent into a reusable skill available to ALL agents.

## Skill Contents

### SKILL.md (292 lines)
Main skill documentation with:
- SMART+ Framework (Specific, Measurable, Actionable, Referenced, Testable, +Context)
- Task Template with Location and Verify metadata
- Precision Checklist (6 questions every task must answer)
- Forbidden Vague Patterns with alternatives
- Task Decomposition Rules

### Supporting Files

**examples/transformation-examples.md**
- 10 comprehensive vague → precise transformations
- Covers: error handling, data models, tests, bug fixes, features, refactoring, performance, logging, documentation, configuration
- Common patterns summary

**references/smart-framework-deep-dive.md**
- Detailed explanation of each SMART+ component
- Framework application workflow
- Anti-patterns and corrections
- Complete validation checklist

**scripts/validate_task.py**
- Automated task precision validator
- Checks for forbidden vague patterns
- Validates all SMART+ components
- Can validate single tasks or entire todo.md files

**templates/task-template.md**
- Copy-paste ready task templates
- Field explanations
- Templates by task type (feature, bug fix, refactor, performance, config)
- Quick validation checklist

## Usage Examples

### Validate a Single Task
```bash
python ~/.claude/skills/write-atomic-tasks/scripts/validate_task.py "Add error handling"
```

### Validate Entire Todo File
```bash
python ~/.claude/skills/write-atomic-tasks/scripts/validate_task.py --file todo.md
```

### Invoke Skill from Any Agent
When an agent needs to write precise tasks, they invoke this skill with phrases like:
- "Write a task for..."
- "Make this task more precise"
- "Break down this feature into tasks"

## Key Features

1. **Framework-Agnostic** - Works for any programming language or project type
2. **Autonomous Execution Focus** - Tasks precise enough for headless/parallel execution
3. **Validation Support** - Automated checking via validate_task.py script
4. **Comprehensive Examples** - 10+ real-world transformation examples
5. **Template Library** - Ready-to-use templates for common task types

## Skill Metrics

| Metric | Target | Status |
|--------|--------|--------|
| SKILL.md lines | <350 | ✅ 292 lines |
| YAML valid | Required | ✅ Passes |
| Description elements | 4 required | ✅ All present |
| Supporting files | Optional | ✅ 4 files |
| Context reduction | 60-80% | ✅ Progressive disclosure |

## Validation Status

```
✅ YAML valid
✅ Description has 4 elements (what, when, terms, context)
✅ SKILL.md is ONLY file in root
✅ SKILL.md <350 lines (292 lines)
✅ Structural compliance passed
✅ Supporting files in subdirectories
✅ Examples tested and functional
✅ Tool restrictions appropriate (none needed)
✅ Discoverable (rich trigger phrases in description)
```

## Source Material

Extracted from `/Users/dawiddutoit/projects/play/temet-run/.claude/agents/todo-manager.md` which contains the original SMART+ framework and task precision guidelines.

## Integration

This skill is stored in `~/.claude/skills/` (global user skills directory) and is available to all agents in all projects.

## Next Steps

1. Test discovery with trigger phrase: "Can you help me write precise tasks?"
2. Use in real workflow with todo-manager agent
3. Monitor invocation metrics and refine if needed
4. Commit to repository if project-specific version needed

## License

Part of the temet-run project's Agent Skills ecosystem.
