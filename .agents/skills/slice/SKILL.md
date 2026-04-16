---
name: slice
description: Break one spec into a sequence of vertical slices — each slice a thin TDD-sized chunk of modules, responsibilities, and behaviours. The bridge between /spec (or /spike) and /tdd. Use after /spec (or /spike) and before /tdd.
argument-hint: "[optional: path to the Spec]"
---

Turn one spec into a sequence of **vertical slices** — each slice one TDD-sized chunk that cuts through the layers it touches, carrying its own list of behaviours. A slice is the unit `/tdd` operates on: one slice, one session, one clean pickup.

A slice plan tells a clean session exactly what to build and how to recognise it's done. It does **not** fix interface signatures — those emerge from the first test, GOOS-style. It fixes *modules and responsibilities*, so interfaces can be discovered, not designed upfront.

## Read the spec

Load the spec and any Technology Decisions from `/spike`. Summarise back: headline interaction, supporting jobs, system sketch, tech choices.

If `specs/<theory>/findings.md` already exists, read it — those are observations from earlier `/tdd` cycles that the user has decided should reshape slicing. This is a re-slice run; see **Re-slicing** below.

Check the spec's **Requires** field to decide how behaviours will be asserted:

- **Deterministic** — concrete input→output examples
- **Non-deterministic** (LLMs, AI, generative services) — contract assertions (structure, length, coverage, qualities any correct output has)

## Explore the codebase

Read what you need to name realistic modules — no more. Don't invent names for things that already exist; don't catalog methods you won't reference. The goal is a slice artifact a clean session can pick up cold without re-treading the same ground.

For each area the spec's system sketch touches, find:

- Existing modules and capabilities that already own part of the responsibility
- Conventions for how features are organised (vertical slices, feature folders, handler patterns)
- External boundaries that will need mocking (network, DB, LLM, time, randomness — see [../tdd/mocking.md](../tdd/mocking.md))

## Draft the slices

A slice is one **thin vertical slice** of the theory — a coherent user-facing capability cutting through the layers it needs, carrying 3–8 observable behaviours, roughly one TDD session of work.

For each slice, decide:

1. **Modules it touches** — which are new (with the responsibility each owns), which existing ones get extended, which external boundaries it crosses
2. **Entry point** — the outermost module the user or caller hits first
3. **Behaviours** — the observable outcomes from the outside, in the language of the domain
4. **Dependencies** — other slices that must be done first

Name modules by responsibility, not location. Files emerge in `/tdd`.

### The first slice is the tracer

The first slice's first behaviour is the **tracer bullet** — end-to-end through every layer the system sketch identifies. See [../tdd/tracer-bullets.md](../tdd/tracer-bullets.md). Mark the slice `tracer: true`. If its tracer behaviour fails during `/tdd`, the architecture can't carry the theory and re-slicing is needed.

Subsequent slices are loop-only — they extend the tracer, they don't replace it. No per-slice tracer phase.

### Behaviours are concrete

Write each behaviour with enough specificity that a clean session can write its test without asking questions. Three validation modes:

**`validation: automated`** — deterministic, concrete Given/When/Then with real values:

> **Writer can save a draft in progress**
> - Given editor is open with title *"How I Ship"* and body *"Ship small often"*
> - When writer clicks Save
> - Then the draft appears in the drafts list with title *"How I Ship"* and status *"Draft"*

**`validation: contract`** — non-deterministic output, structural assertions against a seeded input:

> **Teaser subject line stays under 60 characters**
> - For any generated teaser against seed *article-how-i-ship*: `teaser.subject.length ≤ 60`

**`validation: human`** — load-bearing for the theory but can only be judged in real use. No automated test. Captured in the slice so it isn't forgotten; gathered as evidence at the theory-level validation step in `/tdd`.

> **Question 2 probes deeper into the founder's first answer**
> - Validated by the user in real usage; no automated assertion.

If `validation: human` behaviours start appearing in most slices, that's a signal the theory is too gated on subjective judgment to test automatically — flag it to the user.

The behaviour list is the persisted form of Beck's *"running conversation with yourself"*. It stays stable across slices (so a clean Ralph session sees a coherent plan) but can evolve *within* a slice via `findings.md`.

### Seeds

If any behaviour's contracts reference fixture inputs (article titles, prompts, answers), list them in a **Seeds** section at the bottom of the slice. Contracts without seeds have nothing to check against.

## Check the size

Count the slices. If the number feels large for one theory, ask the user:

*"This spec produced N slices. Does that still feel like one thin improvement against the baseline, or should we split the theory?"*

No hard ceiling — the judgment is the user's. If the answer is "split", loop back to `/theories`.

## Present and pick the order

Show the user:

- Each slice: name, modules touched, behaviour count
- Which slice is the tracer
- The dependency graph — which slices depend on which

Ask the user to confirm the execution order. Dependencies constrain it; within those constraints, the user picks. Encode the decided order as the numeric prefix of each slice file (`01-`, `02-`, …). Keep `depends_on` in frontmatter as a safety check — `/tdd` refuses to start a slice whose dependencies aren't `status: done`.

Do not write files until the user has approved the slice set and the order.

## Write the slice files

Create `specs/<theory-slug>/slices/NN-<slice-slug>.md` for each slice. Format:

```xml
<slice-template>
---
slice: NN-<slug>
theory: <theory-slug>
status: pending
tracer: <true|false>
depends_on: [<slice-id>, ...]
---

# <Slice name>

One-line summary of what this slice delivers.

## Modules

**Entry point:** `<module>` — <responsibility>

**New modules:**
- `<module>` — <responsibility, one thing, thin interface>

**Extends existing:**
- `<module>` — <what it already owns, what this slice adds>

**External boundaries (mockable):**
- <HTTP / DB / LLM / time / random>

## Behaviours

### <Behaviour name, from the outside>
- `validation: automated | contract | human`
- <Given/When/Then, or contract assertion, or real-world note>

### <...>

## Seeds

- **<fixture name>**: <value>
</slice-template>
```
### Set up the theory branch

If a branch `theory/<theory-slug>` does not exist, create it from `main`. Commit the slice files and an empty `specs/<theory-slug>/findings.md` on this branch. Subsequent `/tdd` runs append commits to the same branch; it merges to main when the theory is complete.

Update the spec status to `Spec ready, sliced, awaiting /tdd`.

## Re-slicing

If `findings.md` already has entries when `/slice` is re-run, this is a re-slice pass. Read the findings, the existing slice files, and each slice's `status`.

- Slices marked `status: done` are **not rewritten**. Their work is on the theory branch.
- Pending slices are replaced by a new plan that folds in the findings.
- Renumber only the pending slices, continuing from the highest done slice.
- Clear reviewed findings entries after folding them in (or move them under a `## Resolved` section so the audit trail stays).

Present the re-slice plan the same way (size check, dep graph, user approval) before writing.

## What a slice is NOT

- **Not an architecture document.** One thin vertical slice, not a system design.
- **Not interface design.** Module names and responsibilities only. Interfaces emerge in tests.
- **Not an exhaustive method catalog.** If you haven't referenced it, don't list it.
- **Not scope expansion.** A small supporting job gets a small slice.
- **Not mutable.** Once written, slice files are read by `/tdd` but never written to. Mid-cycle observations go to `findings.md` and come back here on re-slice.

## Loop-backs

Go back to `/spec` if supporting jobs are too vague to map onto modules, the system sketch doesn't identify enough structure, or slicing reveals the headline interaction needs a layer the sketch didn't anticipate.

Go back to `/theories` if slicing yields more slices than one thin improvement can carry, or the total cost is disproportionate to the theory's value.
