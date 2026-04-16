---
name: lessons-learned
description: Use when starting, executing, or finishing non-trivial implementation tasks where reusable constraints may matter. Recall relevant lessons before work, capture reusable corrections or discoveries during and after work, and keep project memory in `docs/lessons/`.
license: MIT
metadata:
  author: shihyuho
  version: "1.0.0"
---

# Lessons Learned

Use this skill to maintain a lightweight project memory loop.

Treat this file as the **single source of truth** for lesson-memory behavior:
trigger rules, recall flow, capture flow, limits, and validation.
`README.md`, `references/`, and phase-entry commands must not override those
rules.

## Trigger Contract

Invoke this skill in these moments:

- **Task start**: Run recall before implementation.
- **During task**: Run capture when the user corrects your approach.
- **Task end**: Evaluate capture criteria and auto-capture qualifying lessons.

Do not trigger for:

- One-off factual Q&A with no reusable process.
- Pure concept explanation without actionable guidance.
- Formatting-only or administrative edits with no technical lesson.
- Non-reproducible context with no stable prevention rule.

## Minimal Execution Guardrails

When this skill is the primary process skill in a session:

- For non-trivial work (3+ steps), create a task tracker before implementation.
- Before claiming completion, run relevant verification commands and report evidence.
- Do not replace verification with assumptions or partial checks.

## Storage

Store all lesson artifacts under `docs/lessons/` at the project root:

```text
docs/lessons/
├── _index.md
├── api-timeout-retry-pattern.md
├── db-migration-run-order.md
└── null-check-before-save.md
```

Each lesson card is one atomic Zettelkasten note. Keep one reusable lesson per
card.

## Canonical Limits

Apply these limits everywhere in the skill package:

- Load **1-3** primary cards during recall.
- Load up to **2** related cards.
- Load at most **5** cards total.
- Use **0-2** `related` links per card.
- Use **3-6** tags per card.
- Keep `confidence` in the inclusive range `0.0-0.9`.

If another file conflicts with these limits, this file wins.

## Recall Phase

Run this phase before writing code.

1. Extract task keywords (technology, failure mode, domain terms).
2. Determine whether lesson storage exists:
   - If `docs/lessons/` does not exist, treat this as first-run state and skip recall.
   - If `docs/lessons/` exists but `_index.md` does not, read existing card frontmatter directly for this recall pass and warn that `_index.md` should be rebuilt during the next capture/update maintenance pass.
3. Determine working scope from the task context:
   - `project` for cross-cutting or repo-wide concerns
   - `module` for package/directory-level concerns
   - `feature` for a specific flow or component
4. Read `docs/lessons/_index.md`.
5. Build candidates for normal recall from cards in `docs/lessons/`.
   - Exclude only cards that explicitly set `confidence: 0.0`.
   - Cards with missing `confidence` remain eligible and use legacy fallback.
   - Cards with `confidence: 0.0` remain in `docs/lessons/` for explicit
     historical lookup.
   - Load cards excluded from normal recall only when the user explicitly asks
     to review cards excluded from normal recall.
6. Rank eligible candidates with this order:
   `tag match -> scope match -> confidence (desc) -> date (desc)`.
   - Legacy fallback applies only when `confidence` is missing: derive it from
     `source` (`user-correction=0.7`, `bug-fix=0.5`,
     `retrospective=0.3`). If both are missing, use `0.3`.
7. Load **1-3** primary cards.
8. Expand with `related` links from primary cards, loading up to **2**
   additional cards.
9. Enforce the hard cap: primary plus related cards must not exceed **5**
   total.
10. Apply loaded lessons as constraints for current work and mention loaded card IDs briefly.
11. Treat recall as read-only for `confidence`:
    - Do not change `confidence` because a lesson was loaded.
    - Do not change `confidence` because a lesson was not loaded.
    - Do not change `confidence` because a lesson was not used recently.

If no cards match, continue work without lesson constraints.

### Recall Warnings

Treat these as non-blocking and continue:

- `docs/lessons/` is missing on first run.
- `_index.md` is missing, so this recall pass used direct card metadata.
- A loaded card is missing `confidence` and needs legacy fallback.
- A `related` target is missing.

## Capture Phase

Run this phase when any of these conditions are met:

- The user corrected your approach
- The user asks for capture
- A bug fix revealed a reusable pattern
- A task completion surfaced a non-obvious reusable insight

Use this phase for both kinds of memory maintenance:

- creating a new lesson card when current work reveals a reusable new lesson
- updating an existing lesson card when current work shows that a recalled or
  related card is less applicable, partially outdated, or no longer valid

### Step 1 — Decide whether to capture

Ask: *"Will this lesson save time next time a similar task appears?"*

Apply this step separately for two decisions:

- whether to create a new lesson card
- whether to update an existing lesson card

Skipping new-card creation does not skip corrective updates to an existing card.
If current work shows that a recalled or related card needs correction, continue
to Step 2 for that existing card even when no new lesson is captured.

Only capture non-obvious insights. Prioritize lessons such as:
- Hidden relationships between files/modules.
- Execution paths that differ from what the code structure suggests.
- Non-obvious config, env vars, flags, or ordering constraints.
- Breakthroughs where error messages were misleading.
- Tool/API quirks and required workarounds.
- Build/test commands or operational prerequisites that are not documented nearby.
- Files that must be changed together for correctness.

Capture if:
- ✅ Reusable pattern or decision rule
- ✅ Costly mistake with a clear prevention strategy
- ✅ Key parameter, config, or precondition that is easy to forget
- ✅ Multi-attempt solution (include failure reasons + success conditions)

Update an existing card if:
- ✅ current work shows a recalled or related card is less applicable than before
- ✅ current work shows a recalled or related card is partially outdated
- ✅ current work shows a recalled or related card should no longer participate in normal recall

Skip if:
- ❌ One-off Q&A with no reusable process
- ❌ Pure concept explanation without actionable guidance
- ❌ Non-reproducible, context-specific conclusion
- ❌ Obvious framework/language behavior with no hidden constraint
- ❌ Session-specific notes that are unlikely to repeat

These skip rules apply to creating a new card. They do not block corrective
updates to an existing card when current evidence shows that the card should be
rewritten or its `confidence` should change.

### Step 2 — Write the Zettel card

Generate a semantic kebab-case ID that describes the lesson (e.g., `api-timeout-retry-pattern`) when creating a new card.

Before writing or updating a card, check for a semantically similar existing card and
make the decision explicit:

- `decision=create` when no similar card exists and a new lesson should be captured.
- `decision=update` when a similar card already covers the same lesson, or when current work corrects an existing card.

Use `decision=create` or `decision=update` only when all affected cards in the
capture pass share the same outcome kind. If one capture pass both creates and
updates cards, report only the `created=<n>` and `updated=<n>` counts.

When one capture pass affects multiple cards, report `created=<n>` and
`updated=<n>` counts. If one capture pass both creates and updates cards, do
not include `decision=`.

Assign a `scope` before writing the card:
- `project` for repo-wide constraints
- `module` for package/directory-level constraints
- `feature` for one flow/component

Assign initial `confidence` by `source`:
- `user-correction`: `0.7`
- `bug-fix`: `0.5`
- `retrospective`: `0.3`

Confidence changes only during capture/update, never during recall.

If the user explicitly confirms a lesson remains useful, increase `confidence` by
`+0.1` (max `0.9`).

Decrease `confidence` by `-0.1` when later evidence shows the lesson is less
applicable.

When a lesson is partially outdated, update the card content first, then
decrease `confidence` only if needed.

Set `confidence` directly to `0.0` only when the card should no longer
participate in normal recall.

Do not decrease `confidence` solely because the lesson was not used recently.

Write the card to `docs/lessons/<id>.md` using the template in
`references/card-template.md`.

Before creating a new card, check semantic duplication:

- If an existing card is semantically similar, update that card instead of creating a duplicate.
- Preserve existing card ID when updating.

When current work weakens a recalled or related card:

- update the existing card even if no new lesson card is created
- update the card content first when the lesson is only partially outdated
- then lower `confidence` only if the lesson's default applicability is weaker than before
- set `confidence` to `0.0` only when the card should no longer participate in normal recall

Minimal correction-capture example:

> Lessons capture report: decision=update, updated=1 (`db-migration-run-order`), confidence=0.7->0.6 (weaker applicability in current config), skipped=0

Card fields:

| Field | Purpose |
|---|---|
| `id` | Semantic kebab-case slug, also the filename |
| `date` | ISO date when the lesson was captured |
| `scope` | `project` / `module` / `feature` applicability |
| `tags` | 3–6 lowercase tags for recall matching |
| `source` | `user-correction` / `bug-fix` / `retrospective` |
| `confidence` | Numeric confidence score used for recall ranking |
| `related` | 0–2 high-relevance lesson references using `[[card-id]]` |
| Title | One-line summary of the lesson |
| Context | What was happening when the mistake occurred |
| Mistake | What went wrong |
| Lesson | Extracted rule or best practice |
| When to Apply | Future situations where this lesson matters |

Task-end behavior:

- If capture criteria are met, auto-capture without asking for permission first.
- After capture, report what was created or updated.
- For normal user-facing output, prefer a short capture summary.
- Do not reproduce the full card body unless the user asks to inspect it.

### Step 3 — Update the index

Upsert one row in `docs/lessons/_index.md` per card ID.

If `_index.md` does not exist, create it with this structure:

```markdown
# Lessons Index

> Auto-generated by lessons-learned skill. Do not edit manually.

| Card | Scope | Tags | Date |
|---|---|---|---|
```

Then keep rows sorted by `Date` descending (newest first).

### Step 4 — Confirm with user

Tell the user what was captured using a compact report, e.g.:

> Lessons capture report: created=1 (`api-timeout-retry-pattern`), updated=1 (`db-migration-run-order`), skipped=1 (obvious behavior)

If all affected cards share the same outcome kind, include `decision=create` or
`decision=update` in the report. If one capture pass both creates and updates
cards, report only the `created=<n>` and `updated=<n>` counts.

When capture or update changes confidence, include confidence transition
`old->new` for each affected card plus a short reason.

For new cards, use `none-><value>`.

If a transition reaches `0.0`, explicitly state that the card is excluded from
normal recall.

Examples:

- `Lessons capture report: decision=create, created=1 (\`api-timeout-retry-pattern\`), confidence=none->0.5 (new reusable pattern)`
- `Lessons capture report: decision=update, updated=1 (\`db-migration-run-order\`), confidence=0.7->0.6 (weaker applicability in current config)`
- `Lessons capture report: decision=update, updated=1 (\`legacy-bootstrap-flow\`), confidence=0.1->0.0 (excluded from normal recall)`

Keep this confirmation short. Prefer the decision, the affected card ID, and a
one-line rule summary. Avoid dumping the full markdown card or index contents in
normal output.

## Linking Rule

Use `related` links for high-value cards only.

Create `related` links when at least **2 of 4** conditions are true:

1. Reusable across different tasks.
2. Represents a high-cost mistake (multiple attempts or significant time loss).
3. Depends on critical parameter/config/decision details.
4. Connects naturally to at least two existing lesson cards.

Linking constraints:

- Add 0–2 related links per card, only when relevance is strong.
- Use deterministic ranking from `references/linking-heuristics.md`.
- Do not add weak or speculative links.

Broken related targets are non-blocking:

- If a related target is missing, ignore it and warn.
- Continue recall/capture flow.

## Anti-patterns

- Capturing obvious language/framework behavior with no hidden constraint.
- Capturing session-only notes (temporary logs, ad-hoc local paths, one-off environment noise).
- Writing verbose narrative cards without actionable prevention rules.
- Creating near-duplicate cards when an update to an existing card is enough.
- Recording broad advice without a concrete trigger in `When to Apply`.

## Validation

Apply these checks during capture or update. These are blocking failures unless
explicitly listed as warnings elsewhere.

- Card filename equals `id` slug.
- `date` format is ISO `YYYY-MM-DD`.
- `scope` is one of `project`, `module`, `feature`.
- `tags` count is 3–6.
- `source` is valid enum.
- `confidence` is numeric and in range `0.0-0.9`.
- `related` count is 0–2 and every target resolves to an existing card.
- Index row exists and matches card metadata, including `scope`.
- `_index.md` rows are ordered by `Date` descending (newest first).

## Integration Guide

When used with other skills in the same session, follow the Trigger Contract as
the single source of truth:

- task start -> recall
- user correction during work -> capture
- task end -> capture evaluation

This is a **non-replaceable** step — lesson capture cannot be substituted by
todo trackers, progress files, or other skill artifacts.
