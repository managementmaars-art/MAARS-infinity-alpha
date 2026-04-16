# Data Contracts - Artifact Validation Quick Reference

> Consult this file when you need to know exactly what to pass to
> `artifact-validator` at a phase boundary, or what a PASS/FAIL verdict means
> for your next decision.
>
> Reminder: the orchestrator reads skill/reference/subagent files, talks to the
> user, and dispatches helpers. Validation stays delegated; this file is the
> compact contract reference, not a substitute for the phase playbooks.
>
> Use the validator's structured verdict as the orchestration decision input.
> Do not replace it with ad hoc raw-file checks at the orchestrator level.

---

## Validation by Phase Transition

Each row shows what to dispatch to `artifact-validator` and what to expect.

### Phases 1–4

For Phase 1, the compact gate below mirrors the stable snapshot contract owned
by `fetching-github-issue`. Treat that downstream skill as the authoritative
definition of `docs/<ISSUE_SLUG>.md`.

For Phase 4 and the Phase 5 precondition, use the stronger handoff contract
owned by `creating-github-child-issues`, not a shorthand of "`## GitHub Task
Issues` exists and has one row."

**Phase 4 write-model reminder:** Downstream creation prefers native child
issues when supported, then linked issues, then task-list references. Validation
must match whichever model the skill recorded, while still requiring a
workflow-level table plus per-task inline references for resumability.

| Phase | Direction     | Files to check           | Expected checks                                                |
| ----- | ------------- | ------------------------ | -------------------------------------------------------------- |
| 1     | postcondition | `docs/<ISSUE_SLUG>.md`   | File exists and contains the required Phase 1 snapshot headings defined by `fetching-github-issue` (stable even when sections are empty), including at minimum: `## Metadata`, `## Description`, `## Acceptance Criteria`, `## Comments`, `## Retrieval Warnings`, `## Child Issues`, `## Linked Issues`, `## Labels`, `## Assignees` — plus any additional headings that skill declares stable (for example `## Milestone`, `## Projects`, `## Attachments`) |
| 2     | precondition  | `docs/<ISSUE_SLUG>.md`   | Same as Phase 1 postcondition                                  |
| 2     | postcondition | `docs/<ISSUE_SLUG>-tasks.md` + planning intermediates | `docs/<ISSUE_SLUG>-stage-1-detailed.md` and `docs/<ISSUE_SLUG>-stage-2-prioritized.md` exist; `docs/<ISSUE_SLUG>-tasks.md` exists; final plan contains `## Issue Summary`, `## Problem Framing`, `## Assumptions and Constraints`, `## Cross-Cutting Open Questions`, `## Tasks`, `## Execution Order Summary`, `## Dependency Graph`, and `## Validation Report`; plan has ≥2 numbered task entries with the required task subsections from `planning-github-issue-tasks` |
| 3     | precondition  | `docs/<ISSUE_SLUG>-tasks.md` + planning intermediates | Same as Phase 2 postcondition                                  |
| 3     | postcondition | `docs/<ISSUE_SLUG>-upfront-critique.md` + `docs/<ISSUE_SLUG>-tasks.md` | `docs/<ISSUE_SLUG>-upfront-critique.md` exists; `docs/<ISSUE_SLUG>-tasks.md` contains `## Decisions Log` |
| 4     | precondition  | `docs/<ISSUE_SLUG>-upfront-critique.md` + `docs/<ISSUE_SLUG>-tasks.md` | Same as Phase 3 postcondition                                  |
| 4     | postcondition | `docs/<ISSUE_SLUG>-tasks.md` | Contains `## GitHub Task Issues`; immediately under that heading includes the machine handoff comment defined by `creating-github-child-issues`; contains the workflow-level table with one row per numbered plan task; rows may use `Not Created` or equivalent; every row that names a concrete GitHub issue has a matching per-task inline reference in the corresponding task section (exact line format owned by `creating-github-child-issues`) |
| 5     | precondition  | `docs/<ISSUE_SLUG>-tasks.md` | Same as Phase 4 postcondition                                  |

### Phases 5–7 (per task)

For Phase 5 postcondition and Phase 6 precondition, this quick reference names
the concrete four-file planning handoff. The detailed section requirements
inside those files are owned by `../../planning-github-task/SKILL.md` and its
`references/data-contracts.md`.

| Phase | Direction     | Files to check                      | Expected checks                  |
| ----- | ------------- | ----------------------------------- | -------------------------------- |
| 5     | postcondition | `docs/<ISSUE_SLUG>-task-<N>-brief.md` + `docs/<ISSUE_SLUG>-task-<N>-execution-plan.md` + `docs/<ISSUE_SLUG>-task-<N>-test-spec.md` + `docs/<ISSUE_SLUG>-task-<N>-refactoring-plan.md` | All 4 concrete Phase 5 planning artifacts exist |
| 6     | precondition  | Same four files as Phase 5 postcondition | Same as Phase 5 postcondition |
| 6     | postcondition | `docs/<ISSUE_SLUG>-task-<N>-critique.md` + `docs/<ISSUE_SLUG>-task-<N>-decisions.md` | Both critique and decisions artifacts exist |
| 7     | precondition  | Standard Phase 1-6 execution handoff | `docs/<ISSUE_SLUG>.md`, `docs/<ISSUE_SLUG>-tasks.md`, `docs/<ISSUE_SLUG>-task-<N>-brief.md`, `docs/<ISSUE_SLUG>-task-<N>-execution-plan.md`, `docs/<ISSUE_SLUG>-task-<N>-test-spec.md`, `docs/<ISSUE_SLUG>-task-<N>-refactoring-plan.md`, `docs/<ISSUE_SLUG>-task-<N>-critique.md`, and `docs/<ISSUE_SLUG>-task-<N>-decisions.md` all exist; this confirms the normal workflow reached execution after critique completion (**6 → 7 readiness**) |

For Phase 7 specifically, this table defines the orchestrator's normal
workflow-gate check. `../../executing-github-task/references/contracts.md`
remains authoritative for the execution skill's own required versus
conditional input semantics.

---

## Dispatch Format

Every dispatch to `artifact-validator` uses these inputs:

```
ISSUE_SLUG: <slug>
PHASE: <1-7>
DIRECTION: <precondition | postcondition>
TASK_NUMBER: <N>    (task-specific boundaries only)
```

The subagent returns a structured verdict:

```
VALIDATION: <PASS | FAIL | ERROR>
Phase: <N> | Direction: <precondition | postcondition>
File: <path>
Checks:
  - File exists: <yes/no>
  - <Section check>: <pass/fail - detail if failed>
```

If the validator itself cannot complete, it returns:

```text
VALIDATION: ERROR
Phase: <N> | Direction: <precondition | postcondition>
Reason: <what prevented validation>
```

For Phases 3 and 6, validation covers only the artifact boundary. The
clarification skill's final summary still carries `RE_PLAN_NEEDED` and
`BLOCKERS_PRESENT`, and the orchestrator must honor those flags separately at
the gate step.

`progress-tracker` dispatches use the same `ISSUE_SLUG` key for workflow identity.
When reading or updating per-task state, include `TASK_NUMBER` as the playbook
specifies.

### Progress tracker dispatch (summary)

Read `../subagents/progress-tracker.md` for full behavior. Typical orchestrator
inputs:

```
ISSUE_SLUG: <slug>
ACTION: read | initialize | update | initialize_task | update_task
```

- **`update`:** `PHASE` (1–4), `STATUS`, `SUMMARY`; for `PHASE=4` and
  `STATUS=complete`, include `TASKS` (metadata for the workflow task table, from
  the Phase 4 downstream summary).
- **`initialize_task`:** `TASK_NUMBER`, `TASK_TITLE`
- **`update_task`:** `TASK_NUMBER`, `PHASE` (5–7), `STATUS`, `SUMMARY`

---

## Handling Verdicts

**On PASS:** Proceed to the next step in the execution cycle. No action
needed — do not narrate the validation result unless the user asks.

**On FAIL:** Do not proceed. The response depends on the direction:

| Direction     | On FAIL                                                                                                               |
| ------------- | --------------------------------------------------------------------------------------------------------------------- |
| Precondition  | A required artifact is missing. Tell the user which phase produced it and offer to run that phase.                    |
| Postcondition | The phase did not produce its expected artifact. Report the specific check that failed and offer to re-run the phase. |

<example>
Postcondition failure after Phase 2:

artifact-validator returns:
VALIDATION: FAIL
Phase: 2 | Direction: postcondition
File: docs/acme-app-42-tasks.md + planning intermediates
Checks:
  - docs/acme-app-42-stage-1-detailed.md exists: pass
  - docs/acme-app-42-stage-2-prioritized.md exists: pass
  - docs/acme-app-42-tasks.md exists: pass
  - Contains ## Validation Report: fail - missing section
  - Numbered task entries with required subsections: pass

Orchestrator to user:
"Phase 2 (Plan Tasks) did not produce a plan that satisfies the downstream
contract for clarification. The final task plan is missing `## Validation
Report`, so Phase 3 would be working from an incomplete artifact. Would you
like me to re-run Phase 2?"
</example>

---

## Artifact Categories

The orchestrator does not need to decide artifact categories dynamically.
Keep this distinction in mind when coordinating the workflow:

- **Category A** (orchestration artifacts, `docs/<ISSUE_SLUG>*.md`): updated on disk
  only, preserved across sessions, never committed.
- **Category B** (implementation output): source code, tests, config changes —
  committed normally.
