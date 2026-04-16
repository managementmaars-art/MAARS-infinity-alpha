# ISC Table Workflow

**Ideal State Criteria (ISC)** - Define success BEFORE execution.

## Purpose

An ISC table captures measurable success criteria before you start work. This prevents:
- "Is this done?" ambiguity
- Scope creep
- Incomplete verification
- Moving goalposts

## Template

```markdown
## ISC Table: [Task Name]

**Created:** [timestamp]
**Phase:** BUILD
**Effort Level:** [TRIVIAL | SIMPLE | MODERATE | COMPLEX | DETERMINED]

| # | Criterion | Metric | Target | Verification Method | Result |
|---|-----------|--------|--------|---------------------|--------|
| 1 | [What must be true] | [Measurable] | [Threshold] | [How to verify] | ⏳ |
| 2 | ... | ... | ... | ... | ⏳ |

### Notes
- [Any context, constraints, or assumptions]
```

## Result Symbols

| Symbol | Meaning |
|--------|---------|
| ⏳ | Pending - not yet verified |
| ✅ | Pass - criterion met |
| ❌ | Fail - criterion not met |
| ⚠️ | Partial - criterion partially met |
| ⏭️ | Skipped - not applicable |

## Writing Good Criteria

### DO:
- Use measurable outcomes ("Tests pass" not "Code works")
- Be specific ("Response time < 200ms" not "Fast enough")
- Include verification method for each criterion
- Keep criteria independent when possible

### DON'T:
- Use subjective measures ("Looks good")
- Combine multiple criteria in one row
- Set criteria you can't verify
- Add criteria after execution starts

## Examples

### Example 1: Bug Fix ISC

```markdown
## ISC Table: Fix null pointer in auth.ts

**Created:** 2026-01-17 11:45 PST
**Effort Level:** SIMPLE

| # | Criterion | Metric | Target | Verification Method | Result |
|---|-----------|--------|--------|---------------------|--------|
| 1 | Null check added | Code inspection | Present | Read auth.ts:42 | ⏳ |
| 2 | Tests pass | Exit code | 0 | `bun test auth.test.ts` | ⏳ |
| 3 | No new errors | Error count | 0 | `bun run build` | ⏳ |
```

### Example 2: Feature ISC

```markdown
## ISC Table: Add dark mode toggle

**Created:** 2026-01-17 11:45 PST
**Effort Level:** COMPLEX

| # | Criterion | Metric | Target | Verification Method | Result |
|---|-----------|--------|--------|---------------------|--------|
| 1 | Toggle component exists | File present | Yes | `ls src/components/ThemeToggle.tsx` | ⏳ |
| 2 | Theme persists | localStorage | Set on change | Browser dev tools | ⏳ |
| 3 | All components themed | Visual inspection | No un-themed elements | Manual review | ⏳ |
| 4 | Tests pass | Exit code | 0 | `bun test` | ⏳ |
| 5 | No accessibility issues | Contrast ratio | >= 4.5:1 | Lighthouse audit | ⏳ |
```

### Example 3: Research ISC

```markdown
## ISC Table: Investigate slow builds

**Created:** 2026-01-17 11:45 PST
**Effort Level:** DETERMINED

| # | Criterion | Metric | Target | Verification Method | Result |
|---|-----------|--------|--------|---------------------|--------|
| 1 | Root cause identified | Evidence | Clear explanation | Document finding | ⏳ |
| 2 | Reproducible | Consistency | 3+ times | Run build multiple times | ⏳ |
| 3 | Quantified impact | Time delta | Measured | Compare before/after | ⏳ |
| 4 | Recommendation made | Action items | Specific steps | Written proposal | ⏳ |
```

## Storage

ISC tables are stored in:
```
~/.claude/MEMORY/Work/[task-id]/isc.md
```

The `task-id` is derived from the task description (slug format).

## Integration

When you create an ISC table:
1. Write it to `MEMORY/Work/[task-id]/isc.md`
2. Update `MEMORY/State/algorithm-state.json` with the ISC path
3. Reference it during VERIFY phase
4. Update results as you verify each criterion
