---
name: wrap
description: Session wrap-up workflow. Use when user asks to "wrap up session", "end session", "/wrap", or wants to analyze completed work before ending.
user-invocable: true
disable-model-invocation: true
argument-hint: [notes]
---

# Wrap Skill

Comprehensive session wrap-up workflow with multi-agent analysis.

## Execution Flow

```
┌─────────────────────────────────────────────────────┐
│  1. Check Git Status                                │
├─────────────────────────────────────────────────────┤
│  2. Phase 1: 4 Analysis Agents (Parallel)           │
│     ┌─────────────────┬─────────────────┐           │
│     │  doc-updater    │  automation-    │           │
│     │  (docs update)  │  scout          │           │
│     ├─────────────────┼─────────────────┤           │
│     │  learning-      │  followup-      │           │
│     │  extractor      │  suggester      │           │
│     └─────────────────┴─────────────────┘           │
├─────────────────────────────────────────────────────┤
│  3. Phase 2: Validation Agent (Sequential)          │
│     ┌───────────────────────────────────┐           │
│     │       duplicate-checker           │           │
│     └───────────────────────────────────┘           │
├─────────────────────────────────────────────────────┤
│  4. Integrate Results & AskUserQuestion             │
├─────────────────────────────────────────────────────┤
│  5. Execute Selected Actions                        │
└─────────────────────────────────────────────────────┘
```

## Step 1: Check Git Status

```bash
git status --short
git diff --stat HEAD~3 2>/dev/null || git diff --stat
```

## Step 2: Phase 1 - Analysis Agents (Parallel)

Execute 4 agents in parallel (single message with 4 Task calls).

### Session Summary (Provide to all agents)

```
Session Summary:
- Work: [Main tasks performed]
- Files: [Created/modified files]
- Decisions: [Key decisions made]
```

### Parallel Execution

```
Task(subagent_type="doc-updater", ...)
Task(subagent_type="automation-scout", ...)
Task(subagent_type="learning-extractor", ...)
Task(subagent_type="followup-suggester", ...)
```

| Agent | Role | Output |
|-------|------|--------|
| **doc-updater** | CLAUDE.md/context.md updates | Specific content to add |
| **automation-scout** | Detect automation patterns | skill/command/agent suggestions |
| **learning-extractor** | Extract learning points | TIL format summary |
| **followup-suggester** | Suggest follow-up tasks | Prioritized task list |

## Step 3: Phase 2 - Validation Agent

Run after Phase 1 completes.

```
Task(
    subagent_type="duplicate-checker",
    prompt="""
Validate Phase 1 results.

## doc-updater proposals:
[doc-updater results]

## automation-scout proposals:
[automation-scout results]
"""
)
```

## Step 4: Integrate Results

```markdown
## Wrap Analysis Results

### Documentation Updates
[doc-updater summary]
- Duplicate check: [duplicate-checker feedback]

### Automation Suggestions
[automation-scout summary]
- Duplicate check: [duplicate-checker feedback]

### Learning Points
[learning-extractor summary]

### Follow-up Tasks
[followup-suggester summary]
```

## Step 5: Action Selection

```
AskUserQuestion(
    questions=[{
        "question": "Which actions would you like to perform?",
        "header": "Wrap Options",
        "multiSelect": true,
        "options": [
            {"label": "Create commit (Recommended)", "description": "Commit changes"},
            {"label": "Update CLAUDE.md", "description": "Document new knowledge"},
            {"label": "Create automation", "description": "Generate skill/command/agent"},
            {"label": "Skip", "description": "End without action"}
        ]
    }]
)
```

## Step 6: Execute Selected Actions

Execute only user-selected actions.

---

## Quick Reference

### When to Use

- End of significant work session
- Before switching to different project
- After completing a feature or fixing a bug

### When to Skip

- Very short session with trivial changes
- Only reading/exploring code
- Quick one-off question answered

### Arguments

- Empty: Proceed interactively (full workflow)
- Message provided: Use as commit message directly
