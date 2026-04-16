# Quick Reference

## When to Use Multi-Agent

| Situation | Use Multi-Agent? |
|-----------|------------------|
| Single task, single domain | No - Use single agent |
| 20+ tools, domain confusion | Yes - Split by domain |
| Subtask generates >1000 irrelevant tokens | Yes - Context isolation |
| Independent research facets | Yes - Parallelization |
| Different behavioral modes needed | Yes - Prompt specialization |
| Sequential work phases | No - Keep together |

## Token Overhead

Multi-agent uses **3-10x more tokens** than single-agent for equivalent tasks.

## Three Success Patterns

1. **Context Protection** - Subagent extracts summary, main agent stays clean
2. **Parallelization** - Independent research runs concurrently
3. **Specialization** - Focused tool sets per domain/role

## Decomposition Rules

### Effective (Context-Centric)
- Independent research paths
- Frontend/backend with clean API
- Blackbox verification

### Problematic (Problem-Centric)
- Planning → Implementation → Testing same feature
- Tightly coupled components
- Shared state synchronization

## Verification Checklist

Before adding multi-agent:
- [ ] Clear constraints exist
- [ ] Context-centric decomposition
- [ ] Specific verification criteria
