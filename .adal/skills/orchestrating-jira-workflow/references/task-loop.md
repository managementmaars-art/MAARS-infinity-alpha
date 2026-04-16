# Task Loop - Phases 5-7

> Read this file when entering the per-task execution loop.
>
> Reminder: the orchestrator reads skill/reference/subagent files, talks to the
> user, and dispatches helpers. Codebase inspection, searches, Jira queries,
> and file updates stay delegated.

Each task passes through Phase 5 (plan), Phase 6 (critique), and Phase 7
(execution kickoff + execute) before the next task begins.

If `progress-tracker` already reported a mid-task resume point such as
`Resume from: Phase 6, Task 2` or `Resume from: Phase 7, Task 2`, skip Task
Selection and re-enter the loop directly at that phase for that task.

---

## Task Selection

Before entering the loop for a task:

1. **Get remaining tasks.** Dispatch `progress-tracker`:

   ```
   TICKET_KEY: <KEY>
   ACTION: read
   ```

   The summary shows which tasks are complete and which remain, including the
   dependency, priority, and status metadata needed for task selection.

2. **Present remaining tasks to the user.** Show the task list with
   dependencies, priority, and status from the `progress-tracker` summary.
   Let the user choose — never auto-select.

3. **Gather pre-task context.** Dispatch relevant utility subagents to gather
   context the downstream skill's kickoff and execution steps may need. These
   are independent and can run in parallel:

   | Need                        | Dispatch to             |
   | --------------------------- | ----------------------- |
   | Current ticket status       | `ticket-status-checker` |
   | Working tree / branch state | `codebase-inspector`    |
   | Relevant code to locate     | `code-reference-finder` |
   | Documentation / config      | `documentation-finder`  |

   Not all dispatches are needed every time — use judgment based on the task.

4. **Prepare task tracking.** Do not initialize task progress yet.

   Initialize it only after the Phase 5 precondition passes and only when the
   selected task does not already have a progress file.

---

## Phase 5 — Plan Task Execution

**Skill:** `planning-jira-task` (at `../../planning-jira-task/SKILL.md`)

**Announce:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Phase 5/7 — Plan Task Execution (Task <N>)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Validate preconditions:** Dispatch `artifact-validator`:

```
TICKET_KEY: <KEY>
PHASE: 5
DIRECTION: precondition
TASK_NUMBER: <N>
```

**Start task tracking:** If the Phase 5 precondition passes and this task does
not already have a progress file, dispatch `progress-tracker`:

```text
TICKET_KEY: <KEY>
ACTION: initialize_task
TASK_NUMBER: <N>
TASK_TITLE: "<title>"
```

If resuming a task that already has a progress file, do not re-initialize it.
Keep the existing task progress artifact and continue from the reported phase.

**Invoke:** Read the skill's SKILL.md and invoke with `TICKET_KEY` and
`TASK_NUMBER`. Retain the pre-task utility summaries for coordination and only
pass them forward when the downstream skill explicitly asks for them. Follow
every step defined in the skill.

The skill runs a 4-subagent pipeline:

1. `execution-prepper` — validates task and assembles the execution brief
2. `execution-planner` — analyzes task and codebase, produces execution plan
3. `test-strategist` — defines behavior-driven tests
4. `refactoring-advisor` — evaluates pre-implementation refactoring needs

**Validate output:** Dispatch `artifact-validator`:

```
TICKET_KEY: <KEY>
PHASE: 5
DIRECTION: postcondition
TASK_NUMBER: <N>
```

Expected: the full Phase 5 planning handoff exists for the task:

- `docs/<KEY>-task-<N>-brief.md`
- `docs/<KEY>-task-<N>-execution-plan.md`
- `docs/<KEY>-task-<N>-test-spec.md`
- `docs/<KEY>-task-<N>-refactoring-plan.md`

Treat `planning-jira-task` as the owner of the detailed section contract inside
those files.

**Update progress:** Dispatch `progress-tracker`:

```
TICKET_KEY: <KEY>
ACTION: update_task
TASK_NUMBER: <N>
PHASE: 5
STATUS: complete
SUMMARY: "Planning complete — <approach summary>"
```

Retain the downstream completion summary at orchestration level: the four
artifact paths, one or two sentences on the recommended approach, the test
coverage shape, and the refactoring verdict.

**Gate:** Automatic → proceed to Phase 6.

---

## Phase 6 — Clarify + Critique Execution Plan

**Skill:** `clarifying-assumptions` (at `../../clarifying-assumptions/SKILL.md`)
**Mode:** `critique`

**Announce:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Phase 6/7 — Clarify + Critique (Task <N>)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Validate preconditions:** Dispatch `artifact-validator`:

```
TICKET_KEY: <KEY>
PHASE: 6
DIRECTION: precondition
TASK_NUMBER: <N>
```

Expected: the same four Phase 5 planning artifacts still exist:

- `docs/<KEY>-task-<N>-brief.md`
- `docs/<KEY>-task-<N>-execution-plan.md`
- `docs/<KEY>-task-<N>-test-spec.md`
- `docs/<KEY>-task-<N>-refactoring-plan.md`

**Invoke:** Read the skill's SKILL.md and invoke with:

- `MODE=critique`
- `TICKET_KEY`
- `TASK_NUMBER`
- `ITERATION=<current iteration or 1>`

The skill derives the standard artifact paths from `TICKET_KEY` and
`TASK_NUMBER`. The Phase 5 planning artifacts remain on disk for its delegated
reads.

The skill dispatches its `critique-analyzer` to review the planning artifacts,
then walks the user through all critique items and any deferred questions for
this task.

### Re-plan cycle

If the skill reports `RE_PLAN_NEEDED=true`:

1. Re-dispatch Phase 5 (`planning-jira-task`) with:
   - `RE_PLAN=true`
   - `DECISIONS_FILE=docs/<KEY>-task-<N>-decisions.md`
2. Let `planning-jira-task` decide the targeted reruns: rerun only the
   invalidated Phase 5 subagents plus their downstream dependents.
3. After the targeted Phase 5 rerun completes, re-dispatch Phase 6 to critique
   the updated plan.
4. Maximum 3 iterations. After 3, present accumulated critique to the user and
   ask how to proceed.

<example>
Re-plan cycle for per-task planning:

Phase 6 (iteration 1):
critique-analyzer: "The execution plan uses a synchronous HTTP call for
the notification service. User impact: 200-500ms added latency on every
save. Alternative: async event via message queue."
User: "You're right, let's go async."
→ RE_PLAN_NEEDED=true

Phase 5 (re-dispatch):
`planning-jira-task` reruns only the invalidated subagents for the decision:
"Use async event for notifications." `execution-planner` updates the plan,
`test-strategist` adjusts test cases, and `refactoring-advisor` refreshes the
refactoring recommendation to match the new approach.

Phase 6 (iteration 2):
critique-analyzer: Notification decision resolved. No new concerns.
User confirms plan.
→ RE_PLAN_NEEDED=false → advance to gate
</example>

**Validate output:** Dispatch `artifact-validator`:

```
TICKET_KEY: <KEY>
PHASE: 6
DIRECTION: postcondition
TASK_NUMBER: <N>
```

Expected: `docs/<KEY>-task-<N>-decisions.md` exists, even if it only records
that no additional decisions were needed beyond critique approval, and
`docs/<KEY>-task-<N>-critique.md` exists for the task-level critique report.

**Update progress:** Dispatch `progress-tracker`:

```
TICKET_KEY: <KEY>
ACTION: update_task
TASK_NUMBER: <N>
PHASE: 6
STATUS: complete
SUMMARY: "N critique items addressed, plan confirmed"
```

**Gate:** First honor the clarification summary.

If `BLOCKERS_PRESENT=true`, stop before execution and surface the unresolved
items. Do not offer Phase 7 as the next step until the blockers are resolved.

If `BLOCKERS_PRESENT=false`, user confirmation is still required. The user must
confirm the plan is ready for implementation before Phase 7 begins. This keeps
Phase 6 critique-only in the execution sense: no implementation, no kickoff,
no Jira `In Progress` transition, and no commits happen here. Recording
critique outcomes in `docs/<KEY>-task-<N>-decisions.md` is still in scope.
Phase 7 kickoff remains the first execution mutation boundary.

```
The execution plan for Task <N> has been critiqued and updated.
Ready to start execution kickoff and implementation? (y/n)
```

---

## Phase 7 — Kick Off and Execute Task

**Skill:** `executing-jira-task` (at `../../executing-jira-task/SKILL.md`)

**Announce:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Phase 7/7 — Kick Off + Execute (Task <N>)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Validate preconditions:** Dispatch `artifact-validator`:

```
TICKET_KEY: <KEY>
PHASE: 7
DIRECTION: precondition
TASK_NUMBER: <N>
```

Expected: the standard workflow handoff from Phases 5 and 6 is present for the
task:

- `docs/<KEY>-task-<N>-brief.md`
- `docs/<KEY>-task-<N>-execution-plan.md`
- `docs/<KEY>-task-<N>-test-spec.md`
- `docs/<KEY>-task-<N>-refactoring-plan.md`
- `docs/<KEY>-task-<N>-critique.md`
- `docs/<KEY>-task-<N>-decisions.md`

This gate confirms that critique completed before execution begins. Once it
passes, `../../executing-jira-task/references/contracts.md` is authoritative for
the execution skill's own required versus conditional artifact semantics.

**Invoke:** Read the skill's SKILL.md and invoke with `TICKET_KEY` and
`TASK_NUMBER`. Keep any pre-task utility summaries at hand for coordination,
but do not treat them as required top-level inputs unless the downstream skill
explicitly accepts them. Follow every step defined in the skill.

The downstream skill starts with an explicit **execution kickoff**. That kickoff
is the first mutation boundary after critique approval. It is where the
workflow:

- confirms task/workspace readiness
- applies any safe startup state changes
- transitions the Jira subtask to `In Progress` when possible
- returns `READY` or a clear blocker before implementation begins

The skill manages its own kickoff step, implementation pipeline, and quality
gates internally. The orchestrator does not intervene in kickoff handling or
quality gate fix cycles unless the downstream skill returns a blocker or
exhausts its internal retry budget.

If `executing-jira-task` reports `BLOCKED` because `task-executor`,
`documentation-writer`, or `requirements-verifier` could not proceed due to a
missing tool, runtime, credential, permission, or environment capability, stop
the task immediately. Surface the exact blocker to the user, do not treat it as
an ordinary implementation gap, and resume from this Phase 7 step only after
the capability is restored.

### Quality gate escalation

The orchestrator only acts when the skill reports that its fix cycle limit is
exhausted. In that case, present the accumulated gate feedback to the user:

<example>
Quality gates did not pass after 3 fix cycles for Task 2.

Accumulated feedback:

- clean-code-reviewer: "extract-validation module has 4 functions over 30
  lines each — violates single-responsibility"
- architecture-reviewer: PASS
- security-auditor: PASS

Options:

1. Accept the current state and move to the next task
2. Provide guidance for a different approach
3. Re-run the full task pipeline from Phase 5 (for fundamental approach issues)
</example>

Option 3 is for fundamental approach failures — not for minor code quality
issues that can be accepted.

There is no orchestrator-level Phase 7 postcondition artifact check. The
downstream execution skill owns its internal kickoff and quality gates and
returns the completion summary that drives the workflow update.

**Update progress:** Dispatch `progress-tracker`:

```
TICKET_KEY: <KEY>
ACTION: update_task
TASK_NUMBER: <N>
PHASE: 7
STATUS: <complete | failed | skipped>
SUMMARY: "<completion, failure, or user-directed stop summary>"
```

Use `STATUS=complete` only when `executing-jira-task` reports a successful task
completion path. If the execution skill stops with a blocker, error, or
exhausted fix cycle, follow `./error-handling.md` and record `failed` (or
`skipped` when the user explicitly chooses to accept or stop without finishing
the task).

When recording a blocker-driven stop as `failed`, keep the summary explicit
about the missing capability and the fact that the task should resume from
Phase 7 once the blocker is resolved.

`update_task` already mirrors the per-task completion state into the
workflow-level Task Execution table. Do not dispatch a second workflow-level
`update` call here.

---

## Loop Continuation

After Phase 7 completes for a task:

1. Return to the **Task Selection** procedure above.
2. Present remaining tasks to the user.
3. The user selects the next task — never auto-continue.
4. Continue until all tasks are complete or the user stops.

---

## Final Summary

When all tasks are complete (or the user decides to stop), dispatch
`progress-tracker` with `ACTION=read` for the final state, then present:

```markdown
## Workflow Summary — <TICKET_KEY>

| Phase | Status      | Key outcome                            |
| ----- | ----------- | -------------------------------------- |
| 1     | ✅ Complete | Ticket fetched (N comments)            |
| 2     | ✅ Complete | N tasks planned                        |
| 3     | ✅ Complete | N/N questions resolved, N critiqued    |
| 4     | ✅ Complete | N tasks linked to Jira subtasks        |
| 5–7   | ✅ Complete | N/N tasks planned, critiqued, kicked off, executed |

Per-task detail in docs/<TICKET_KEY>-task-<N>-progress.md.
All artifacts are in docs/<TICKET_KEY>*.
```
