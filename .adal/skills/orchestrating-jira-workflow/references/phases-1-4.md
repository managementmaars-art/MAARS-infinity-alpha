# Phases 1-4 - Linear Pipeline

> Read this file when entering Phase 1, 2, 3, or 4.
>
> Reminder: the orchestrator reads skill/reference/subagent files, talks to the
> user, and dispatches helpers. Artifact checks, Jira calls, file updates, and
> other execution work stay delegated.

After Phase 4 completes, read `./task-loop.md` to enter the per-task loop.

For every phase below, follow the standard cycle from `SKILL.md`:
**announce -> validate preconditions -> invoke skill -> validate
postconditions -> update progress -> gate check**

---

## Phase 1 - Fetch Ticket

**Skill:** `fetching-jira-ticket` at `../../fetching-jira-ticket/SKILL.md`

1. Announce Phase 1.
2. There is no artifact precondition for a fresh start.
3. Read the phase skill and invoke it with `JIRA_URL`.
4. Dispatch `artifact-validator` with:

   ```
   TICKET_KEY: <KEY>
   PHASE: 1
   DIRECTION: postcondition
   ```

5. Expect: `docs/<KEY>.md` exists and satisfies the Phase 1 snapshot contract
   from `fetching-jira-ticket`, including the required top-level sections used
   by downstream phases.
6. Dispatch `progress-tracker` with:

   ```
   TICKET_KEY: <KEY>
   ACTION: update
   PHASE: 1
   STATUS: complete
   SUMMARY: "Ticket fetched - N comments, N subtasks found"
   ```

**Gate:** Automatic. Proceed to Phase 2 when validation passes.

---

## Phase 2 - Plan Tasks

**Skill:** `planning-jira-tasks` at `../../planning-jira-tasks/SKILL.md`

1. Announce Phase 2.
2. Dispatch `artifact-validator` with:

   ```
   TICKET_KEY: <KEY>
   PHASE: 2
   DIRECTION: precondition
   ```

3. Expect: `docs/<KEY>.md` exists and still satisfies the full Phase 1 snapshot
   contract, not just a single-section check.
4. Read the phase skill and invoke it with:
   - `TICKET_KEY`
5. The downstream skill produces `docs/<KEY>-tasks.md` plus planning
   intermediates.
6. Dispatch `artifact-validator` with:

   ```
   TICKET_KEY: <KEY>
   PHASE: 2
   DIRECTION: postcondition
   ```

7. Expect the full Phase 2 contract, not the older shorthand only:
   - `docs/<KEY>-stage-1-detailed.md` exists
   - `docs/<KEY>-stage-2-prioritized.md` exists
   - `docs/<KEY>-tasks.md` exists
   - The final plan contains `## Ticket Summary`, `## Execution Order Summary`,
     `## Problem Framing`, `## Assumptions and Constraints`,
     `## Cross-Cutting Open Questions`, `## Tasks`, `## Dependency Graph`, and
     `## Validation Report`
   - The final plan has at least 2 numbered task entries
   - Each numbered task includes the eight required subsections from
     `planning-jira-tasks`
8. Dispatch `progress-tracker` with:

   ```
   TICKET_KEY: <KEY>
   ACTION: update
   PHASE: 2
   STATUS: complete
   SUMMARY: "N tasks planned, execution order determined"
   ```

**Gate:** Automatic. Proceed to Phase 3 when validation passes.

---

## Phase 3 - Clarify Assumptions + Critique Plan

**Skill:** `clarifying-assumptions` at `../../clarifying-assumptions/SKILL.md`
**Mode:** `upfront`

1. Announce Phase 3.
2. Dispatch `artifact-validator` with:

   ```
   TICKET_KEY: <KEY>
   PHASE: 3
   DIRECTION: precondition
   ```

3. Expect the full Phase 2 contract to remain intact before clarification:
   - `docs/<KEY>-stage-1-detailed.md` still exists
   - `docs/<KEY>-stage-2-prioritized.md` still exists
   - `docs/<KEY>-tasks.md` still satisfies the full Phase 2 postcondition
4. Read the phase skill and invoke it with:
   - `MODE=upfront`
   - `TICKET_KEY`
   - `ITERATION=<current iteration or 1>`
   - Let the skill derive the standard artifact paths from `TICKET_KEY`; the
     validated Phase 2 artifacts stay on disk for the downstream reads
5. The downstream skill handles user-facing critique and clarification inline,
   while delegating its analysis helpers.

### Re-plan cycle

If the skill reports `RE_PLAN_NEEDED=true`:

1. Re-run Phase 2 with the same `TICKET_KEY` plus:
   - `RE_PLAN=true`
   - `DECISIONS=<accepted decisions from critique>`
2. Re-run only the failing boundary: Phase 2 postcondition, then Phase 3 again.
3. Do not re-raise critique items that the user already resolved consciously.
4. Maximum: 3 re-plan loops. After the third, present the accumulated critique
   and ask the user how to proceed.

<example>
Iteration 1:
Critique finds that the plan defaults to Redis without project-specific
justification.
User decides: "Use in-memory LRU for now."
-> `RE_PLAN_NEEDED=true`

Re-run Phase 2 with `RE_PLAN=true` and `DECISIONS="Use in-memory LRU for now."`

Iteration 2:
Updated plan reflects in-memory LRU.
Critique finds no unresolved concern on caching.
-> `RE_PLAN_NEEDED=false`
</example>

6. Dispatch `artifact-validator` with:

   ```
   TICKET_KEY: <KEY>
   PHASE: 3
   DIRECTION: postcondition
   ```

7. Expect:
   - `docs/<KEY>-upfront-critique.md` exists
   - `docs/<KEY>-tasks.md` contains `## Decisions Log`
8. Dispatch `progress-tracker` with:

   ```
   TICKET_KEY: <KEY>
   ACTION: update
   PHASE: 3
   STATUS: complete
   SUMMARY: "N/N questions resolved, N critique items addressed"
   ```

**Gate:** First honor the clarification summary.

If `BLOCKERS_PRESENT=true`, stop before Jira writes and surface the unresolved
items. Do not offer Phase 4 as the next step until the blockers are resolved.

If `BLOCKERS_PRESENT=false`, user confirmation is still required before Jira
writes. Present:

```
Plan is ready. How would you like to proceed?

1. Create subtasks in Jira now
2. Review the plan first
3. Stop here and create subtasks manually
```

Only proceed to Phase 4 when the user explicitly chooses option 1.

---

## Phase 4 - Create Jira Subtasks

**Skill:** `creating-jira-subtasks` at `../../creating-jira-subtasks/SKILL.md`

1. Announce Phase 4.
2. Dispatch `artifact-validator` with:

   ```
   TICKET_KEY: <KEY>
   PHASE: 4
   DIRECTION: precondition
   ```

3. Expect the validated Phase 3 outputs needed for safe Jira writes:
   - `docs/<KEY>-upfront-critique.md` exists
   - `docs/<KEY>-tasks.md` contains the validated decisions log
4. Read the phase skill and invoke it with `JIRA_URL`.
5. The downstream skill creates or reconciles Jira subtasks, updates
   `docs/<KEY>-tasks.md` with the Phase 4 handoff artifacts, and returns the
   `Created/Linked Subtasks` table plus any warnings or failures.
6. Dispatch `artifact-validator` with:

   ```
   TICKET_KEY: <KEY>
   PHASE: 4
   DIRECTION: postcondition
   ```

7. Expect the validated Phase 4 handoff contract:
   - `docs/<KEY>-tasks.md` contains a `## Jira Subtasks` table
   - The table has one row per numbered task
   - Rows may use `Not Created`, but every row with a Jira-style key has a
     matching `Jira Subtask: <KEY>` line in the corresponding task section
8. Dispatch `progress-tracker` with:

   ```
   TICKET_KEY: <KEY>
   ACTION: update
   PHASE: 4
   STATUS: complete
   SUMMARY: "N tasks linked to Jira subtasks (M created now, K already linked)"
   TASKS: [rows from Created/Linked Subtasks with task number, title, dependencies, priority, and any optional linkage metadata]
   ```

9. Use the downstream `Created/Linked Subtasks` table as the source for
   `TASKS`, preserving dependency and priority metadata for later task
   selection.
10. If the downstream summary includes warnings or failed creates, surface them
    before task selection so the user can see which tasks still lack Jira
    linkage.

**Gate:** User chooses which task to execute next. Never auto-start a task.

<example>
Subtasks created in Jira. Which task would you like to work on first?

| # | Title | Dependencies | Priority |
| - | ----- | ------------ | -------- |
| 1 | Add input validation | None | High |
| 2 | Implement caching layer | Task 1 | High |
| 3 | Update API documentation | None | Medium |

Pick a task number, or say "show me the full plan" for more detail.
</example>

---

## Next Step

After the user selects a task, read `./task-loop.md` and begin the per-task
execution loop for Phases 5-7.
