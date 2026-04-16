---
name: ship-check
description: Run the standard post-change validation flow after a fix, refactor, or new feature. Use when implementation work is done and you should validate the latest changes by invoking the repo's review skills, starting with review-changes and then repo-doc-maintainer, before giving the final close-out.
disable-model-invocation: true
---

# Ship Check

## Overview

Run the repo's end-of-task validation flow after code or documentation changes.

This is an orchestration skill. It does not replace the specialized review skills. It tells the agent which checks to run, in what order, and how to summarize the result before final handoff.

## Standard Flow

Use this flow after finishing a fix, refactor, or feature:

1. Review the latest changes with `$review-changes`.
2. Check whether project documentation needs maintenance with `$repo-doc-maintainer`.
3. Report the combined outcome clearly.
4. If code changed, remind the user about any validation commands not yet run.

## Invocation Pattern

When this skill is invoked, explicitly use the other repo-local skills in sequence.

Start with:

`Use $review-changes to review the latest changes against the project's guidelines and report findings first.`

Then run:

`Use $repo-doc-maintainer to review the latest changes and decide whether project documentation should be updated.`

Do not skip either step unless the user explicitly narrows the scope.

## How To Interpret Results

### If `review-changes` finds issues

- present the findings first
- do not claim the work is validated
- if the issues are actionable and local, fix them before final handoff when appropriate
- rerun validation after fixes if you changed the code again

### If `review-changes` finds no issues

- say that the changes comply with the current repo guidance
- still run `$repo-doc-maintainer`

### If `repo-doc-maintainer` says docs should change

- update the docs if the current task includes making those maintenance edits
- otherwise report that documentation maintenance is recommended

### If `repo-doc-maintainer` says no doc update is needed

- state that explicitly in the final close-out

## Output Expectations

The final close-out should combine both checks:

- whether the implementation passed the repo-rule review
- whether documentation maintenance was needed
- whether project validation commands were run or remain outstanding

Keep the output compact. Prefer a brief status summary over a long checklist unless there are actual findings.

## Constraints

- Treat `$review-changes` as the source of truth for repo-rule compliance review.
- Treat `$repo-doc-maintainer` as the source of truth for doc-maintenance decisions.
- Do not invent a separate third review rubric here.
- Use this skill at the end of work, not before implementation starts.

## Validation Flow

Use this checklist after finishing implementation work.

**Required Review Skills**

1. `$review-changes`
2. `$repo-doc-maintainer`

**Default Sequence**

1. Inspect the latest working tree or commit range.
2. Run the repo-rule review via `$review-changes`.
3. Run the doc-maintenance review via `$repo-doc-maintainer`.
4. Summarize both results.

**Final Close-Out Should Cover**

- whether the changes respect the project's documented guidelines
- whether project documentation needed updates
- whether validation commands (lint, test, analyze) were run
- any residual risks, such as unrun tests or manual-only verification gaps

**When To Re-Run**

Re-run the flow if you make additional code or doc edits after the first validation pass.

## Closing Signal

After the final close-out, always emit a verdict on its own line:

- `VERDICT: APPROVED` — if both checks passed with no outstanding issues
- `VERDICT: REMARKS` — if issues were found or remain unresolved, followed by findings:

```
VERDICT: REMARKS

FINDINGS_START
- review-changes: <summary of issues, or "passed">
- repo-doc-maintainer: <summary of doc recommendations, or "no changes needed">
- validation commands: <any outstanding commands not yet run, or "all run">
FINDINGS_END
```

The `VERDICT:` line must be the last substantive output. When using `FINDINGS_START`/`FINDINGS_END` delimiters, place them on their own lines.
