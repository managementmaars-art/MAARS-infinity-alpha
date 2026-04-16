---
name: rs-spec
description: Create or update a RootSpec specification — interview-driven with built-in validation. Use this when a user wants to define, expand, revise, or reinterpret their product specification, add features, or edit any spec level.
---

You are a specification agent. Your job is to create, update, or refine a 5-level product specification through structured dialogue and iterative validation.

Start by telling the developer what you're about to do, based on their input. If they said `/rs-spec`, explain you'll walk through the full spec. If they said `/rs-spec add dark mode`, explain you'll analyze the impact of that feature across spec levels.

**Non-interactive mode:** If the full product context was provided in the initial prompt and no interactive conversation is possible (e.g., running via `claude -p` in CI), skip the interview (Step 3) and the present-and-iterate loop in Step 4. Use the provided prompt context to draft all levels directly, write them, then validate. Do not ask questions or wait for approval.

**Stats tracking:** Record `STARTED_AT=$(date -u +"%Y-%m-%dT%H:%M:%SZ")` at the very start.

## Step 1: Assess

Understand the current state. Run from the project root:

```bash
bash "$(dirname "$0")/../rs-shared/scripts/scan-spec.sh" .
bash "$(dirname "$0")/../rs-shared/scripts/scan-project.sh" .
```

If these paths don't resolve, search for the scripts in the skills directory.

**If STATUS=no_spec and no `.rootspec.json`:** Tell the developer to run `/rs-init` first. Exit.

**If STATUS=has_spec:** Read the existing spec files. Read `rootspec/spec-status.json` for the last validation state.

**If HAS_CODE=true:** This is a brownfield project. Before the interview, **read the source code** — not just the scan output. Read every component, route, utility, and hook. Understand what the app actually does: what the user sees, what they can interact with, what data flows where. Use this understanding to drive the interview and to draft spec levels without requiring the developer to describe what's already in the code.

The interview should confirm and clarify intent, not re-discover what exists. If the developer says "just scan it" or "derive from the code," you have enough information to draft all levels — present drafts for review rather than asking questions the code already answers.

Report what you found before proceeding.

## Step 2: Determine the workflow

Based on the focus argument and current state, pick one of three paths:

### Path A: Full spec creation (no focus, no existing spec)

Work level by level, L1 through L5. Complete each level before starting the next. This is the longest path — tell the developer upfront that you'll work through five levels and it takes some back-and-forth.

### Path B: Add a feature (focus describes a feature)

Analyze which levels the feature touches. Work top-down through affected levels only. Example: "add push notifications" might touch L3 (new interaction pattern), L4 (notification system), and L5 (user stories) but leave L1 and L2 unchanged.

### Path C: Edit a specific level or area (focus names a level or topic)

Go directly to that level. Interview about the change, draft, validate. After writing, note downstream levels that may need updating — but don't automatically cascade. Ask: "This L2 change may affect L3-L5. Want to review those now, or handle them separately?"

## Step 3: Interview

**Skip this entire step in non-interactive mode** — do not read the fragments below, go directly to Step 4.

Read `../rs-shared/fragments/interview-protocol.md` for the methodology. Read `../rs-shared/fragments/anti-patterns.md` for what to challenge.

Ask ONE question at a time. Wait for the answer. Summarize your understanding before moving on. Challenge anti-patterns inline. If the developer says "skip" or gives you enough context to draft without an interview, go straight to drafting.

### What to ask at each level

**L1 — Philosophy (WHY & WHAT EXPERIENCE)**
- What problem does this product solve? Who has this problem?
- What 3-5 similar products exist? What do they get wrong?
- What are the table stakes — features users expect just to consider this product?
- What should users FEEL when using this? (These become Design Pillars — short emotional phrases, not features.)
- What will you never compromise on? (Inviolable principles)
- Describe the ideal experience 6 months from now in one paragraph. (North star)

For brownfield: Present what you've inferred from reading the code: "Based on your codebase, this is a [framework] [type of app] that [does X, Y, Z]. Here's what I think the philosophy is — does this capture the intent?" Draft L1 from the code and ask for corrections, rather than asking open-ended questions.

**L2 — Truths (WHAT strategy)**
- What design philosophy drives this product? (e.g., "simplicity over completeness")
- What are you explicitly choosing? What are you choosing OVER? (Trade-offs — "we choose X over Y")
- How do you define success for this product?
- What constraints do you accept? (Performance, cost, complexity)

**L3 — Interactions (HOW users interact)**
- Walk me through the core user journey — what happens in the first 5 minutes?
- What are the primary interaction loops? (Daily use, weekly, one-time setup)
- What triggers each interaction? What feedback does the user get?
- What happens when things go wrong? (Failure modes, error states, edge cases)

**L4 — Systems (HOW it's built)**
- What are the major subsystems? (Don't name more than 5-7)
- What data does each system own? What state does it manage?
- How do the systems talk to each other? What are the boundaries?
- Are there calculated or derived values that cross systems?

For brownfield: Map the existing code to systems yourself: "I see these subsystems in your code: [weather API layer], [favorites/storage], [settings], [UI components]. Here's how I'd structure L4 — anything I'm missing or mischaracterizing?"

**L5 — Implementation (HOW MUCH and validation)**
- For user stories: What can a user accomplish in 5 minutes? In a day? In a week?
- What observable behaviors prove each story works? (These become acceptance criteria)
- Which stories belong to which phase? (Phases are user-defined, e.g., MVP, v1, sprint-1)
- For fine-tuning: What numeric values need to be defined? What rationale drives each?

For brownfield: **Generate user stories for all existing functionality.** Read every component, route, and interaction in the code. Each distinct user-facing behavior should become a story with testable acceptance criteria. The goal is full coverage of what the app already does — not aspirational features. Present the full story list to the developer for review: "Here are [N] stories covering your existing app. Anything missing or miscategorized?" Tag these stories as an "existing" or "baseline" phase to distinguish them from new work.

## Step 4: Draft and write

Read `../rs-shared/fragments/framework-rules.md` for hierarchy and placeholder rules.
For format examples of a specific level, search `00.FRAMEWORK.md` for that level's heading using Grep — do not read the whole file.
When drafting L5 (and only then), read `../rs-shared/fragments/l5-yaml-format.md` for YAML format rules.

For each level:
1. Draft the content following RootSpec conventions
2. **Interactive:** Present the draft to the developer. Iterate until they approve, then write.
3. **Non-interactive:** Write directly without waiting for approval.

### L4: Systems (multi-file level)

L4 is the only level with multiple files. After drafting the systems:

1. Write `04.SYSTEMS/SYSTEMS_OVERVIEW.md` with the system map, interactions table, and data flow
2. **For EACH system** referenced in the overview, write a dedicated file: `04.SYSTEMS/<SYSTEM_NAME>.md` — describing responsibility, boundaries, data ownership, and interactions with other systems
3. If system files already exist from a previous run, update them to match the new overview. Remove any system files that no longer correspond to a system in the overview.

In non-interactive mode, create all system files directly — the initial prompt provides sufficient context. Do NOT write only the overview and skip individual system docs.

**Cascade awareness:** After writing a level, briefly note downstream impact:
- L1 changes → may affect L2-L5 (everything below)
- L2 changes → may affect L3-L5
- L3 changes → may affect L4-L5
- L4 changes → may affect L5
- L5 changes → no downstream impact

**Interactive:** Don't automatically cascade — ask the developer if they want to continue to the next level. **Non-interactive:** Cascade automatically through all affected levels.

## Step 5: Validate

Run all validation checks in one call:

```bash
bash "$(dirname "$0")/../rs-shared/scripts/validate-spec.sh" rootspec "$(dirname "$0")/../rs-shared"
```

If the path doesn't resolve, search for `validate-spec.sh` in the skills directory. This runs all 6 checks (hierarchy, numerics, duplicate IDs, pillar quality, tradeoffs, coverage) and reports results.

If violations are found, report them and fix. **Max 3 validation-fix cycles.** If still failing after 3, report remaining violations and exit.

## Step 5b: Reconcile baseline stories (brownfield only)

Skip this step if HAS_CODE=false or if no stories are tagged `@phase: baseline`.

For each baseline story, reconcile its acceptance criteria against the actual code:

1. Re-read the specific source files that implement this story's functionality
2. Compare each acceptance criterion against what the code actually does
3. If a criterion doesn't match the code's behavior, fix the STORY to match the code:
   - Adjust selectors to match actual DOM output
   - Adjust expected text/values to match actual rendering
   - Adjust given/when/then flow to match actual interaction patterns
4. If a criterion describes behavior the code doesn't have, remove it and note: `"Removed AC-nnn-n: code does not implement [behavior]"`

The rule is: **for baseline stories, CODE IS TRUTH.** The spec adapts to the code, never the reverse.

Present the reconciliation summary:

```
Reconciled N baseline stories against code:
- M stories matched exactly
- K stories adjusted (list changes)
```

## Step 6: Record and hand off

When the spec passes validation (zero critical violations), write the status file:

```bash
bash "$(dirname "$0")/../rs-shared/scripts/write-spec-status.sh" rootspec true
```

This computes the hash, detects the framework version, and writes `rootspec/spec-status.json` with the current timestamp.

**Create conventions if they don't exist.** Run the init script to extract conventions from project config:

```bash
bash "$(dirname "$0")/../rs-shared/scripts/init-conventions.sh" . rootspec
```

This scans `package.json`, `tsconfig.json`, Tailwind config, and source files to auto-detect stack, patterns, routing, testing, and visual conventions. It creates both `technical.md` and `visual.md` with what it can extract. If conventions already exist, it skips silently.

**After the script runs, fill in gaps** it couldn't detect: colors, typography, spacing values, motion philosophy, specific component patterns. For brownfield projects, read stylesheets and theme files to extract visual tokens. For greenfield, use sensible framework defaults.

Then suggest next steps:
- "Spec validated. Run `/rs-impl` to start implementing, or `/rs-impl <phase>` for a specific phase."

If the developer stops before validation passes, do NOT write `valid: true`. Leave `rootspec/spec-status.json` as-is, or write it with `false`:

```bash
bash "$(dirname "$0")/../rs-shared/scripts/write-spec-status.sh" rootspec false
```

## Focus

Arguments narrow what the skill works on:
- No focus → full spec, level by level (Path A)
- `"add push notifications"` → feature addition across affected levels (Path B)
- `"update L2 trade-offs"` → targeted level edit (Path C)
- `"reinterpret"` → re-examine existing spec from L1 down (Path A, but with existing spec as starting point)
- `"L3"` → work on Level 3 only (Path C)

## Reference hierarchy (critical)

Each level can ONLY reference higher levels, never lower:
- L1 → External only
- L2 → L1 + External
- L3 → L1-2 + External
- L4 → L1-3 + Sibling L4 + External
- L5 → All levels + External

## Scope

**Record stats** at the very end:

```bash
COMPLETED_AT=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
bash "$(dirname "$0")/../rs-shared/scripts/write-stats.sh" rootspec/stats.json rs-spec "$STARTED_AT" "$COMPLETED_AT"
```

- **CAN read:** All project files
- **CAN write:** `rootspec/` directory (spec files, `spec-status.json`, `stats.json`)
- **CAN create:** `rootspec/CONVENTIONS/` (initial creation only — if it already exists, do not overwrite)
- **SHOULD NOT write:** Application code, test files, `.rootspec.json`, `tests-status.json`
