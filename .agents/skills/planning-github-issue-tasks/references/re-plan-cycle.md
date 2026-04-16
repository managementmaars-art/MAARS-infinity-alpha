# Re-Plan Cycle and Error Handling

This file is loaded when Phase 3 critique triggers a re-plan dispatch back
to Phase 2, or when an error occurs during the pipeline. On the happy path,
this file is never read.

> Read this file only for re-plan or recovery paths.
>
> Preserve existing stage artifacts, restart from the earliest affected stage,
> and rerun only the gates that are now invalid.

## Re-Plan Cycle

If Phase 3 critique triggers a re-plan, the orchestrator re-dispatches this
skill with the same `ISSUE_SLUG`, plus:

- `RE_PLAN=true` — signals this is a re-dispatch
- `DECISIONS` — the decisions from Phase 3 that require plan changes

On re-plan:

1. **Re-dispatch only the affected stages first.** Use the new decisions and
   the existing on-disk artifacts to update only the parts of the plan that are
   no longer valid. If the critique affects the whole plan, re-run all three
   stages.
2. **Pass targeted fix inputs.** The affected subagent receives its original
   inputs plus `DECISIONS` and, when applicable, `VALIDATION_ISSUES`.
3. **Overwrite the affected stage artifacts** with updated versions so the
   latest plan stays resumable.
4. **Re-run only the failing validation gates first,** then run post-pipeline
   validation again once the updated plan is complete.

**Maximum re-plan cycles:** 3 iterations. If Phase 3 critique still has
unresolved concerns after 3 cycles, escalate to the user.

This re-plan budget is separate from the per-gate targeted fix budget below:
re-plan tracks critique-driven planning revisions, while targeted fix cycles
track repeated failures at the same validator boundary.

## Error Handling

- If any subagent fails, stop the pipeline. Report the failure with the stage
  number and the subagent's structured summary.
- If a `stage-validator` check fails, re-dispatch only the stage that produced
  that artifact. Pass the validator's issues list as `VALIDATION_ISSUES`, then
  re-run only that failing gate.
- **Maximum targeted fix cycles per gate:** 3. If the same gate still fails
  after the third cycle, stop and report.
- Intermediate files are always preserved — they are never deleted, regardless
  of success or failure.
