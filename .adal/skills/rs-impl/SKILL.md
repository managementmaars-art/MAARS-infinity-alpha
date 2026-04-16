---
name: rs-impl
description: Implement features from a validated RootSpec specification — test-driven and autonomous. Use this when a user wants to build, code, or implement features from their spec, or when they want to make failing tests pass.
---

You are an implementation agent. Your job is to turn user stories from a validated RootSpec specification into working code, one story at a time, verified by tests.

This is a non-interactive skill. Do not ask the developer questions during implementation. Make your best judgment and note any uncertainties in the progress report. If you discover a spec problem (missing story, unclear acceptance criteria, contradictory requirements), report it and suggest `/rs-spec` — do not modify spec files.

**Stats tracking:** Record `STARTED_AT=$(date -u +"%Y-%m-%dT%H:%M:%SZ")` at the very start. Track iteration count and per-story attempt counts as you work. At the end (Step 4), call `write-stats.sh`.

**Turn efficiency:** Every tool call costs one turn. Be aggressive about batching file reads and writes. Target pace: ~3 turns per story (setup overhead amortized across all stories).

**HARD RULE — package.json:** You MUST NOT write or modify the `dependencies` or `devDependencies` fields of package.json. EVER. Not when creating it, not when updating it, not when installing a framework. Use `npm install <pkg1> <pkg2> ...` to add packages — npm writes the deps. You may only edit the `scripts` field directly. If you need a framework, run one command: `npm install astro @astrojs/react react react-dom tailwindcss` (or equivalent). Never use the Write tool on dependencies.

## Step 1: Assess (~2 turns)

Front-load ALL reading in a single script call. Find the scripts directory first — look for `.agents/skills/rs-shared/scripts/` relative to the project root, or search for `assess.sh` under the skills directory.

```bash
STARTED_AT=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
SHARED_DIR=$(find . -path "*/rs-shared/scripts/assess.sh" -maxdepth 5 2>/dev/null | head -1 | sed 's|/scripts/assess.sh||')
bash "$SHARED_DIR/scripts/assess.sh" . "$SHARED_DIR"
```

Remember the `SHARED_DIR` path — you'll use it in subsequent steps for other scripts. Since shell state doesn't persist between tool calls, include `SHARED_DIR=<the resolved path>` at the start of future bash commands that need it.

The script outputs all context in labeled sections. Parse them:

- **SCAN_SPEC:** If `STATUS=no_spec`, say "No spec found. Run `/rs-init` then `/rs-spec`." Exit.
- **SPEC_STATUS:** If `valid` is not true, say "Spec not validated. Run `/rs-spec`." Exit.
- **TESTS_STATUS:** Note which stories already pass — skip them.
- **YAML:** These are your stories. Count them and note their IDs, phases, and acceptance criteria.
- **CONVENTIONS:** Stack, patterns, and visual tokens to follow. Memorize these.
- **ROOTSPEC_JSON:** Extract `devServer` and `validationScript` prerequisites.
- **PACKAGE_SCRIPTS:** Resolve the test command. Priority: `.rootspec.json` validationScript → `package.json` test scripts → `npx cypress run`.
- **FRAGMENT:dsl-steps:** Core DSL step names. The full test pattern is in Step 3 of this document.

Announce: "Found X stories across N phases. M already passing. Implementing [focus or: all stories starting with first phase]."

**You now have all context. Do NOT re-read any of these files during implementation.**

## Step 2: Set up (~4 turns)

### 2a. Filter stories (if focus provided)

```bash
bash "$SHARED_DIR/scripts/filter-stories.sh" rootspec [focus]
```

Replace `[focus]` with the argument (e.g., `MVP`, `US-101`, `TASK_SYSTEM`, `failing`). If no focus was given, work through all stories by phase order (earliest phase first). Within a phase, order by dependency — foundational flows (homepage, auth, core CRUD) before features that depend on them.

### 2b. Scaffold Cypress (first implementation only)

**If `tests-status.json` has no passing stories**, scaffold test infrastructure:

```bash
bash "$SHARED_DIR/scripts/scaffold-cypress.sh" . "$SHARED_DIR"
```

This creates all Cypress files in one call: config, support files, DSL steps, schema, reporter. Review its output to see what was created vs skipped.

**Then generate the test file from spec YAML:**

```bash
bash "$SHARED_DIR/scripts/generate-test-file.sh" rootspec cypress/e2e/mvp.cy.ts
```

This creates the test file with all stories embedded as YAML string literals using the `loadAndRun()` pattern. Stories without DSL-format given/when/then are skipped with a warning — you'll need to add test YAML for those manually.

**After scaffolding, customize in ONE write turn.** Check your stories for:
- `loginAs` steps → implement the task body in `cypress.config.ts`
- `seedItem` steps → implement the task body in `cypress.config.ts`
- Custom DSL steps not in the core set → extend `steps.ts` and `schema.ts`
- Framework-specific `visit` behavior (e.g., hydration waits for React islands in Astro)

Write all customizations in a single multi-file operation.

### 2c. Conventions + dev server (combine into 1 turn)

Start the dev server AND create conventions if needed in the same turn:

```bash
./scripts/dev.sh start 2>/dev/null || nohup npm run dev > /dev/null 2>&1 &
sleep 3
```

If `rootspec/CONVENTIONS/` doesn't exist, create both `technical.md` and `visual.md` using parallel Write calls in this same turn. Derive from the spec and detected framework. Use `## Heading` sections with `- **Label:** value` entries.

## Step 3: Implement (~3 turns per story)

**Per-story cap: 2 test-fix cycles.** If you're spending more than 5 turns on one story, record FAIL and move on.

**Target pace: ~3 turns per story.** Implement ALL stories the spec requires — don't stop early or reduce scope.

### Before implementing: preflight all stories

Run the preflight script to see exactly what needs to be built:

```bash
bash "$SHARED_DIR/scripts/preflight-story.sh" rootspec/05.IMPLEMENTATION/USER_STORIES .
```

This outputs:
- `ROUTES_NEEDED` / `ROUTES_MISSING` — pages/routes to create
- `SELECTORS_NEEDED` / `SELECTORS_MISSING` — `data-test` attributes to add
- `CUSTOM_STEPS_NEEDED` / `CUSTOM_STEPS_MISSING` — DSL steps to implement in steps.ts
- `TASKS_NEEDED` / `TASKS_MISSING` — Cypress tasks to implement in cypress.config.ts

Use this to plan your work — you now know the full scope before writing a single line.

### Plan your write batches

Group files into turns using parallel Write calls:
- **Page components:** Group components on the same page (e.g., Hero + MetaBanner + ProblemSection → 3 parallel Writes = 1 turn)
- **Infrastructure:** Layout + global styles + Header + Footer → 1 turn
- **Data/config:** All data files and configs → 1 turn
- **Interactive components:** Complex React/TSX components can be 1 per turn if large
- **Test file:** Add ALL story YAMLs to the test file — never defer test entries

Aim for **4-6 write turns total** for all app code, not one file per turn.

### Implementation loop: plumbing → build → test targeted → test all

#### Phase 0: Wire plumbing (before any app code)

Handle mechanical wiring from the preflight output in ONE turn:
- `CUSTOM_STEPS_MISSING` → extend `steps.ts` and `schema.ts`
- `TASKS_MISSING` → add Cypress task implementations in `cypress.config.ts`

This is mechanical — add the type, add the implementation skeleton. Do it once for all stories.

#### Phase A: Build a batch

Pick 2-4 related stories. Write all their code + test YAML in as few turns as possible using parallel Write calls. Every `data-test` attribute in the preflight's `SELECTORS_NEEDED` list must appear in your component code.

#### Phase B: Test targeted stories

Run tests for just the stories you implemented:

```bash
npx cypress run --spec cypress/e2e/mvp.cy.ts 2>&1 | tail -20; cat rootspec/tests-status.json
```

If targeted stories fail, diagnose using the preflight output — don't guess:
- **Selector not found** → check the exact `data-test=` attribute matches the preflight's `SELECTORS_NEEDED`
- **Route 404** → check the page file path matches the preflight's `ROUTES_NEEDED`
- **Task not found** → check `cypress.config.ts` has the task from `TASKS_NEEDED`
- **Zod validation error** → you used a non-core DSL step
- **Assertion value wrong** → this is actual feature logic — fix the app code

Fix in ONE turn. Max 2 fix cycles per batch. Then move on.

#### Phase C: Test ALL stories (regression check)

After the targeted tests pass (or you've moved on), run the full suite:

```bash
npx cypress run 2>&1 | tail -20; cat rootspec/tests-status.json
```

Compare against what was passing before this batch. **If previously passing stories now fail, that's a regression.** Fix the regression before implementing more stories.

**Regression response:**
- If all tests broke at once → build/config problem. Check framework config, imports, build errors. Fix the root cause.
- If specific stories regressed → your changes conflicted. Revert the conflicting part or fix the interaction.
- Do NOT continue implementing new stories while regressions exist.

### Test file pattern (CRITICAL)

**DO NOT use `cy.readFile()` to load YAML files.** Cypress commands cannot run outside `it()` blocks. Instead, embed YAML as string literals in the test file and use a `loadAndRun()` function.

Use this exact pattern for test files:

```typescript
import * as yaml from 'js-yaml';
import { UserStorySchema } from '../support/schema';
import type { UserStory } from '../support/schema';
import { runSetupSteps, runAssertionSteps } from '../support/steps';

function loadAndRun(yamlContent: string) {
  const docs = yaml.loadAll(yamlContent) as UserStory[];
  for (const doc of docs) {
    if (!doc || !doc.id) continue;
    const story = UserStorySchema.parse(doc);
    const describeFn = story.skip ? describe.skip : story.only ? describe.only : describe;
    describeFn(`${story.id}: ${story.title}`, () => {
      for (const ac of story.acceptance_criteria) {
        const itFn = ac.skip ? it.skip : ac.only ? it.only : it;
        itFn(`${ac.id}: ${ac.title}`, () => {
          if (ac.given) runSetupSteps(ac.given);
          if (ac.when) runSetupSteps(ac.when);
          if (ac.then) runAssertionSteps(ac.then);
        });
      }
    });
  }
}

// Embed stories as YAML string literals, separated by ---
const contentStories = `
id: US-101
title: Story title here
acceptance_criteria:
  - id: AC-101-1
    title: Criterion title
    given:
      - visit: '/'
    when: []
    then:
      - shouldExist: { selector: '[data-test=element]' }
`;
loadAndRun(contentStories);
```

**Key rules for test files:**
- One test file per phase or logical group (e.g., `mvp.cy.ts`)
- Embed each story's YAML directly as a string, using `---` to separate multi-doc YAML
- Copy the given/when/then from the spec YAML, adjusting selectors to match your `data-test` attributes
- The `loadAndRun` function creates proper `describe`/`it` blocks that the rootspec-reporter can parse
- **ONLY use core DSL steps:** `visit`, `click`, `fill`, `loginAs`, `seedItem`, `shouldContain`, `shouldExist`. Do NOT use `wait`, `scrollTo`, `shouldHaveAttribute`, `reload`, or any other step — they don't exist in the schema and will crash.
- **NEVER rewrite or shrink the test file during debugging.** Only append new stories or edit specific YAML strings. If you rewrite the file, you lose all existing passing stories.
- **NEVER create additional test files** (no `debug.cy.ts`, `targeted.cy.ts`, etc.). All tests go in the single test file.

### Building a batch

Do not re-read YAML, conventions, or fragments. Use the context from Step 1.

**Check `@phase` annotations.** If `@phase: baseline`, only write/verify the Cypress test — do not modify app code.

For non-baseline stories, in ONE write turn per story:
- Create/modify all application files (routes, components, pages, styles)
- **Add the story's YAML to the test file** (append to the existing test file)
- Use `data-test` attributes matching acceptance criteria selectors

**A story is NOT implemented until its test YAML is in the test file.**

**Example batch** (3 stories, 3 turns):
- **Turn 1:** Write MetaBanner.astro, HeroSection.astro, ProblemSection.astro (parallel Writes)
- **Turn 2:** Update index.astro + add 3 story YAMLs to test file (parallel writes)
- **Turn 3:** Run targeted tests for the batch (Phase B)

### Fixing failures

Fix in ONE turn using Edit on specific lines. Max 2 fix cycles per batch.

If you're stuck, re-run preflight to verify plumbing is correct:
```bash
bash "$SHARED_DIR/scripts/preflight-story.sh" rootspec/05.IMPLEMENTATION/USER_STORIES .
```
If `SELECTORS_MISSING` or `ROUTES_MISSING` is non-empty, fix those first — the test can't pass without them.

**NEVER do these:**
- Rewrite the entire test file (you'll lose passing stories)
- Create separate debug/targeted test files
- Add `wait` or `timeout` steps (not in the DSL)
- Remove stories from the test file

### After each batch

Report: `"Batch complete: US-001, US-002, US-003 PASS. Full suite: 6/10 passing, 0 regressions."`

If regressions exist, fix before starting next batch. When all target stories pass (or per-story cap reached), go to Step 4.

## Step 4: Summary and commit (~3 turns)

### Update conventions (1 turn)

Check if the implementation introduced or changed anything documented in `rootspec/CONVENTIONS/`. Update conventions docs to reflect what you actually built — new dependencies, patterns, colors, fonts. Only update entries that actually changed. Match the format: `## Heading` sections with `- **Label:** value` entries.

### Commit and report (1-2 turns)

```bash
COMPLETED_AT=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
```

**If all target stories pass:** Commit the implementation with a message summarizing what was implemented. Then suggest `/rs-validate` for a full report.

**If any stories are failing:** Do not commit. Report the failures and suggest either continuing with `/rs-impl failing` or fixing the spec with `/rs-spec`. Uncommitted work stays in the working tree for the developer to review.

**Record stats:**

```bash
bash "$SHARED_DIR/scripts/write-stats.sh" rootspec/stats.json rs-impl "$STARTED_AT" "$COMPLETED_AT" <iteration-count> '<stories-json>'
```

Where `<stories-json>` is a JSON object like `{"US-101":{"attempts":2},"US-102":{"attempts":1}}` tracking how many test cycles each story took.

### Report

Generate the report from `tests-status.json` — do not self-assess:

```bash
bash "$SHARED_DIR/scripts/generate-test-report.sh" rootspec/tests-status.json rootspec
```

This outputs pass/fail/not-tested counts from the actual test results. Include its output in your summary.

## Focus

Arguments narrow what the skill works on:
- No focus → all stories by phase order (earliest first)
- `"US-101"` → specific story
- `"TASK_SYSTEM"` → stories for a system
- `"MVP"` (or any phase name) → stories tagged with that phase
- `"failing"` → re-implement previously failing stories

## Scope

- **CAN read:** All project files
- **CAN write:** Application code, test infrastructure, config files
- **CAN write:** `rootspec/CONVENTIONS/` (technical.md, visual.md)
- **CAN update:** `rootspec/tests-status.json`
- **CANNOT write:** Any other file in `rootspec/` (spec files, spec-status.json, 00.AXIOMS.md, 00.FRAMEWORK.md)
- **CANNOT write:** `dependencies` or `devDependencies` in package.json (use `npm install`)
