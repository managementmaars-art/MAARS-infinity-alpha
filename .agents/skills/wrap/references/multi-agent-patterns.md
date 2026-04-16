# Multi-Agent Orchestration Patterns

Patterns for designing multi-agent workflows in Claude Code.

## Core Principles

> **"Agent architecture should reflect the dependency graph of the task"**

If subtasks don't read or modify each other's state, run them **parallel**.
If previous output is next input, run them **sequential**.

## Parallel vs Sequential

| Condition | Pattern |
|-----------|---------|
| Subtasks are independent | **Parallel** |
| Previous output is next input | **Sequential** |
| Diverse perspectives needed | **Parallel** (Fan-out) |
| Proposals need validation | **2-Phase** (Generate→Validate) |

## 2-Phase Pipeline Pattern

```
Phase 1: Analysis (Parallel)
┌──────────┬──────────┬──────────┐
│ Agent A  │ Agent B  │ Agent C  │
└────┬─────┴────┬─────┴────┬─────┘
     └──────────┼──────────┘
                ↓
Phase 2: Validation (Sequential)
┌─────────────────────────────────┐
│         Validator Agent         │
└─────────────────────────────────┘
```

### Examples

**Session wrap:**
- Phase 1: doc-updater, automation-scout, learning-extractor, followup-suggester
- Phase 2: duplicate-checker

**Code review:**
- Phase 1: security-reviewer, style-checker, performance-analyzer
- Phase 2: final-reviewer

## Implementing in Claude Code

### Parallel Execution

Send multiple Task calls in single message:

```python
Task(subagent_type="agent-a", prompt="...")
Task(subagent_type="agent-b", prompt="...")
Task(subagent_type="agent-c", prompt="...")
```

### Sequential Execution

Wait for previous result:

```python
result_1 = Task(subagent_type="agent-a", prompt="...")
Task(subagent_type="agent-b", prompt=f"Validate: {result_1}")
```

## Model Selection

| Use Case | Model |
|----------|-------|
| Deep analysis | `sonnet` or `opus` |
| Quick validation | `haiku` |
| Creative reasoning | `opus` |
| Batch operations | `haiku` |

## Anti-Patterns

| Anti-Pattern | Alternative |
|--------------|-------------|
| Adding meaningless agents | Check if single agent sufficient |
| Excessive multi-hop | Direct communication |
| Unclear task boundaries | Define clear objectives |

## References

- [Anthropic Multi-Agent Research](https://www.anthropic.com/engineering/multi-agent-research-system)
- [Azure AI Agent Design Patterns](https://learn.microsoft.com/en-us/azure/architecture/ai-ml/guide/ai-agent-design-patterns)
