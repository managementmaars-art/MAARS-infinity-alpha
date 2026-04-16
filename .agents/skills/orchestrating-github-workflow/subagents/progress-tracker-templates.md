# Progress Tracker — File Templates and Action Procedures

> This file contains the progress file templates and detailed action
> procedures. Read this when executing any action that creates or modifies
> progress files.
>
> Reminder: these are Category A orchestration artifacts. Update them on disk,
> preserve them across sessions, and summarize their state back to the
> orchestrator instead of returning raw file contents.

Loaded by: `./progress-tracker.md`

---

## Main Progress File Template

Location: `docs/<ISSUE_SLUG>-progress.md`

Used by the `initialize` action:

```markdown
# <ISSUE_SLUG> — Workflow Progress

| Phase | Skill                         | Status     | Completed at | Notes |
| ----- | ----------------------------- | ---------- | ------------ | ----- |
| 1     | fetching-github-issue         | ⬜ Pending | —            | —     |
| 2     | planning-github-issue-tasks   | ⬜ Pending | —            | —     |
| 3     | clarifying-assumptions        | ⬜ Pending | —            | —     |
| 4     | creating-github-child-issues   | ⬜ Pending | —            | —     |

## Task Execution (Phases 5–7)

_No tasks yet — populated after Phase 4 completes._

## Execution Log
```

---

## Task Execution Table Template

When Phase 4 completes (the `update` action receives `PHASE=4` with
`STATUS=complete`), replace the placeholder in the `## Task Execution`
section with this table, populated from the `TASKS` input.

Each `TASKS` entry should include:

- task number
- title
- dependencies, using `None` when there are no prerequisites
- priority, using `Unknown` when the plan does not provide one
- optional GitHub linkage fields when known (URL, `owner/repo#number`, etc.)

Use that metadata to build this table:

```markdown
## Task Execution (Phases 5–7)

| Task | Title              | Dependencies | Priority | Current Phase | Status     | Detail                                 |
| ---- | ------------------ | ------------ | -------- | ------------- | ---------- | -------------------------------------- |
| 1    | <title from TASKS> | <deps>       | <prio>   | —             | ⬜ Pending | `docs/<ISSUE_SLUG>-task-1-progress.md` |
| 2    | <title from TASKS> | <deps>       | <prio>   | —             | ⬜ Pending | `docs/<ISSUE_SLUG>-task-2-progress.md` |
| ...  | ...                | ...          | ...      | ...           | ...        | ...                                    |
```

---

## Per-Task Progress File Template

Location: `docs/<ISSUE_SLUG>-task-<N>-progress.md`

Used by the `initialize_task` action:

```markdown
# <ISSUE_SLUG> — Task <N>: <TASK_TITLE> — Progress

| Phase | Skill                  | Status     | Completed at | Notes |
| ----- | ---------------------- | ---------- | ------------ | ----- |
| 5     | planning-github-task   | ⬜ Pending | —            | —     |
| 6     | clarifying-assumptions | ⬜ Pending | —            | —     |
| 7     | executing-github-task  | ⬜ Pending | —            | —     |

## Re-plan History

_None_

## Activity Log
```

---

## Status Values

| Status    | Display     | Meaning                    |
| --------- | ----------- | -------------------------- |
| complete  | ✅ Complete | Phase/task finished        |
| active    | 🔄 Active   | Currently in progress      |
| failed    | ❌ Failed   | Errored — needs resolution |
| skipped   | ⏭️ Skipped  | Bypassed by user decision  |
| (default) | ⬜ Pending  | Not yet started            |

---

## Detailed Action Procedures

### `update` procedure

1. Read the current main progress file.
2. Update the row for the given phase (1–4) with the new status and a UTC
   timestamp.
3. If `PHASE=4` and `STATUS=complete`, populate the Task Execution table
   using the `TASKS` input, preserving each task's dependency, priority, and
   optional GitHub linkage metadata (see template above).
4. Append a one-line entry to `## Execution Log`:
   ```
   <UTC timestamp> — Phase <N>: <STATUS> — <SUMMARY>
   ```
5. Write the updated file.

### `initialize_task` procedure

Call this only after the orchestrator has selected a task and the Phase 5
precondition has passed.

1. Create the per-task progress file from the template at
   `docs/<ISSUE_SLUG>-task-<N>-progress.md`.
2. Update the corresponding task row in the main progress file's Task
   Execution table:
   - Current Phase → `Phase 5 - planning`
   - Status → `🔄 Active`
3. Append a one-line entry to the main file's `## Execution Log`:
   ```
   <UTC timestamp> — Task <N> started: <TASK_TITLE>
   ```

### `update_task` procedure

1. Read the per-task progress file.
2. Update the row for the given phase (5–7) with the new status and a UTC
   timestamp.
3. Append a one-line entry to the per-task file's `## Activity Log`:
   ```
   <UTC timestamp> — Phase <PHASE>: <STATUS> — <SUMMARY>
   ```
4. Write the updated per-task file.
5. Update the corresponding task row in the main progress file:
   - Current Phase → `Phase <PHASE> - <phase name>`
   - Status → the new status display value
   - If `PHASE=7` and `STATUS=complete`, set Status to `✅ Complete`
6. Append a one-line entry to the main file's `## Execution Log`:
   ```
   <UTC timestamp> — Task <N> Phase <PHASE>: <STATUS> — <SUMMARY>
   ```
