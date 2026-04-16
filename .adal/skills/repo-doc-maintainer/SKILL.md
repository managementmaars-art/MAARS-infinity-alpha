---
name: repo-doc-maintainer
description: Review recent repository changes and decide whether AGENTS.md or other project-level documentation needs a high-level update. Use when finishing a feature, fix, refactor, or architectural change and you need to preserve repo-shaping guidance such as new patterns, constraints, workflows, validation rules, or onboarding-relevant gotchas without adding low-level implementation detail.
disable-model-invocation: true
---

# Repo Doc Maintainer

## Overview

Review the latest local changes, classify whether they introduced stable repo-shaping knowledge, and update project-level documentation (AGENTS.md, CLAUDE.md, or equivalent) only when that knowledge would help the next contributor work safely.

Keep docs compact and high signal. Do not turn any file into a changelog, feature walkthrough, or implementation dump.

## Workflow

1. Inspect the latest change set.
2. Compare the change against the current guidance in the project's documentation files.
3. Decide whether the change introduced new high-level knowledge that future contributors need.
4. Update only the appropriate document and only at the correct level of abstraction.
5. Summarize what changed or explicitly say no doc update is needed.

## Inspect The Change Set

Check the local diff first. Prefer the smallest scope that answers the question:

- `git status --short`
- `git diff --stat`
- `git diff -- <path>`
- `git log -1 --stat`

If the user asks about merged or already committed work, inspect the relevant commit or commit range instead.

Read the affected code before editing docs. Do not infer a new rule from filenames alone.

## Decide Whether Docs Should Change

Update docs only for durable, reusable guidance such as:

- a new architectural pattern or layering rule
- a new dependency or repo-wide technology choice
- a new required validation or workflow step
- a new DI, routing, state, API, persistence, or testing convention
- a new gotcha that is subtle, repeatable, and likely to cause regressions
- a new location of truth for important behavior

Do not update docs for:

- one-off feature details
- temporary workarounds unless they are active repo constraints
- file-by-file summaries
- naming trivia
- low-level implementation mechanics that are obvious from code
- changes that are already captured adequately in existing docs

Use this test: if the next competent contributor would likely make a mistake without knowing this, and the guidance remains useful beyond one feature, document it.

## Choose The Right File

Update `AGENTS.md` (or `CLAUDE.md`) when the guidance should be visible in the fastest possible repo brief:

- stable architectural constraints
- repo-wide rules
- mandatory validation commands
- short "what matters" reminders

If neither `AGENTS.md` nor `CLAUDE.md` exists and a doc update is warranted, create `AGENTS.md` at the repo root with only the guidance that meets the criteria above. Do not create it for weak candidates.

Keep additions terse. Prefer a single bullet or short sentence.

Update onboarding or developer docs when the guidance needs more explanation:

- decision rules
- examples
- gotchas
- workflow detail
- rationale that helps a new contributor apply the rule correctly

If a rule belongs in both files, put the shortest possible reminder in AGENTS.md and the fuller explanation in the onboarding doc.

## Editing Rules

- Keep docs high level and DRY.
- Preserve existing tone and structure.
- Integrate new guidance into the most relevant existing section instead of appending random notes.
- Prefer editing or tightening an existing bullet before adding a new one when the concept already exists.
- Avoid repeating the same rule in multiple sections of the same file.
- Do not document speculative patterns. The rule should already exist in code or workflow.

## Output Expectations

After review, report one of these outcomes:

- no doc update needed, with a brief reason
- updated AGENTS.md / CLAUDE.md
- updated onboarding docs
- updated both

When you update docs, describe the repo-shaping guidance you added, not a file-by-file diff dump.

## Doc Update Criteria

Use this rubric when deciding whether a recent change deserves documentation in project-level docs.

### Good Candidates

- New repo-wide API or data-access pattern
- New state-management rule that affects multiple features
- New dependency-injection registration requirement
- New routing or bootstrap constraint
- New persistence, localization, or testing convention
- New validation command, CI expectation, or test convention
- New subtle regression trap discovered through real work

### Weak Candidates

- Single-screen implementation detail
- Private helper extraction
- Renaming or code movement with no behavior change
- Temporary experiment
- Feature-specific copy or asset changes
- Test-only detail that does not represent a broader repo convention

### Questions To Ask

1. Would this still matter in a month?
2. Does this affect more than one file, feature, or future task?
3. Would a contributor who skips this guidance likely make a real mistake?
4. Is the rule already captured clearly in one of the docs?
5. Can this be stated at a high level without teaching the implementation?

If the answer to the first three is mostly yes, document it. If the last two are no, document it carefully and concisely.
