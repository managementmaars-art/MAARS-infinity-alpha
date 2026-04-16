Apply these structural additions to the plan during the write step. The input plan's content (task objectives, implementation notes, DoD, etc.) is preserved unchanged — only annotations, renumbering, and new sections are added.

Stage 1 uses `## Issue Summary`. Insert `## Execution Order Summary` **immediately after** `## Issue Summary` and **before** `## Problem Framing`.

### Replace letter labels with numbers

```markdown
## Task 1: <Title> ← was "Task C"
```

### Add priority annotation to each task

Immediately after the task heading:

```markdown
> **Priority:** Risk=4 Complexity=3 Value-unlock=5 Dependency=4 | Total=16/20
> **Was:** Task C | **Rationale:** On the critical path; unblocks Tasks 2, 3, 5.
```

### Add dependency annotations to each task

(See Part 1 in the subagent definition for the annotation format.)

After renumbering, all `Dependencies / prerequisites` must use NEW task numbers
with the old label in parentheses for traceability:

```markdown
**Dependencies / prerequisites:**

- **Hard:** Task 1 (was Task C — creates the schema)
- **Soft:** Task 3 (was Task B — establishes the pattern)
```

### Add execution summary (insert after `## Issue Summary`)

```markdown
## Execution Order Summary

| Order | Task | Title                  | Risk | Complexity | Value | Dep | Total | Rationale (one line)            |
| ----- | ---- | ---------------------- | ---- | ---------- | ----- | --- | ----- | ------------------------------- |
| 1     | C→1  | Set up database schema | 4    | 3          | 5     | 4   | 16    | Critical path, unblocks 3 tasks |
| 2     | A→2  | Configure auth         | 3    | 2          | 4     | 3   | 12    | High risk, early signal         |
| …     | …    | …                      | …    | …          | …     | …   | …     | …                               |

### Recommended execution phases

**Phase 1 (sequential — critical path):**
Tasks 1, 2 — must be done in order.

**Phase 2 (parallelizable):**
Tasks 3, 4, 5 — can be done simultaneously after Phase 1.

**Phase 3 (sequential — finalization):**
Tasks 6, 7 — depend on Phase 2 completion.
```

### Add dependency graph (append at end of document)

```markdown
## Dependency Graph

### Critical path

<The longest chain of hard dependencies. This determines the minimum
sequential execution time.>

Task 1 → Task 3 → Task 6 → Task 8

### Parallel groups

<Groups of tasks that can execute simultaneously.>

- **Group 1 (after Task 1):** Tasks 2, 4, 5
- **Group 2 (after Task 3):** Tasks 6, 7
- **Independent:** Task 9 (no dependencies, can start anytime)

### Dependency matrix

| Task | Hard depends on | Soft depends on | Parallel with |
| ---- | --------------- | --------------- | ------------- |
| 1    | —               | —               | 9             |
| 2    | 1               | —               | 4, 5          |
| …    | …               | …               | …             |
```

Downstream skills parse the `## Execution Order Summary`, `## Dependency Graph`, `**Dependencies / prerequisites:**`, and `**Priority:**` headings programmatically — changing or omitting them breaks the pipeline.
