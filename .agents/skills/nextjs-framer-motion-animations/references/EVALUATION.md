# Evaluation pack

Use this when you are improving the skill itself, reviewing a repo before broad edits, or checking whether your Motion guidance is still "expert" rather than merely plausible.

## What the pack tests

The pack is split into three layers:

1. **Trigger coverage**
   - `assets/evaluation-pack/trigger-tests.json`
   - Positive prompts that should load the skill
   - Negative prompts that should not

2. **Scenario fixtures + golden decisions**
   - `assets/evaluation-pack/fixtures/`
   - `assets/evaluation-pack/goldens/`
   - Small repos that represent the most failure-prone decisions:
     - passive App Router reveal
     - client-side presence UI
     - App Router route shell
     - Pages Router legacy route transitions
     - shared-layout tabs
     - design-system wrapper work

3. **Anti-pattern detection**
   - `scripts/check-motion-antipatterns.mjs`
   - Static checks for common mistakes such as:
     - mixed `motion` / `framer-motion`
     - server files importing client-only Motion paths
     - root layout widened to client without cause
     - index keys under `AnimatePresence`
     - `top` / `left` animation instead of transforms
     - repeated `layoutId` without `LayoutGroup id`
     - `motion.create()` inside render

## Scripts

### Scenario-aware planner
Use this before non-trivial edits:

```bash
node scripts/plan-motion-change.mjs --root /path/to/repo --target path/to/file.tsx --task "Add a subtle route transition"
```

It combines repo audit + target inspection + task wording, then returns JSON with:
- package strategy
- import-path choice
- boundary choice
- recommended pattern
- first steps
- reduced-motion plan
- performance plan
- validation checklist

### Anti-pattern scan

```bash
node scripts/check-motion-antipatterns.mjs --root /path/to/repo
```

Returns JSON with repo-level warnings and file-level issues.

### Full evaluation pack

```bash
node scripts/run-evaluation-pack.mjs
node scripts/run-evaluation-pack.mjs --case app-router-route-shell
node scripts/run-evaluation-pack.mjs --list
```

The evaluator runs the planner or anti-pattern scanner against the bundled fixtures and compares the result to the corresponding golden JSON.

## Expert bar

Treat the skill as "expert" only when all of these are true:

- It chooses the repo's existing package strategy unless migration is explicit.
- It keeps the Client Component boundary as small as possible.
- It distinguishes App Router route shells from `template.tsx` replay semantics.
- It treats `AnimatePresence`, `layoutId`, `LayoutGroup id`, and `motion.create()` as correctness-sensitive APIs.
- It accounts for reduced motion instead of treating it as optional polish.
- It explains validation, not just implementation.

## Manual review prompts

Use these when reviewing agent output:

- Did the answer keep the change local?
- Did it pick the right import path for the repo?
- Did it choose the correct Next.js boundary?
- Did it mention reduced motion?
- Did it avoid route-transition overreach?
- Did it call out likely failure modes before they happen?
- Did it describe how to validate the change?

## Output contract

See `assets/evaluation-pack/output-contract.json`.

The final answer should usually name:
- files changed or files likely to change
- chosen Motion API / pattern
- boundary strategy
- package decision
- reduced-motion handling
- performance considerations
- validation notes
- caveats
