---
name: theories
description: Turn a Goals Document into a set of theories — each one a hypothesis about what might solve the problem, with a clear way to test it. Use after /goals to decide what to build and why.
argument-hint: "[optional: path to Goals Document]"
---

Every feature is a theory — a guess about what might solve the problem. Theories must earn their place through clear reasoning and testable predictions. The user originates theories; your job is to help shape them.

## Read the Goals Document

Load `./goals.md`, or the goal tracking issue if the project uses GitHub. If none is provided, ask for it. Summarise the problem statement and current state back — the current state is the baseline theories will be measured against.

## Draw out theories

This is a collaborative brainstorm. Do not propose theories yourself — the people closest to the problem have the best intuitions.

Ask: *"Looking at the current state, what do you think would move the needle?"*

For each theory the user proposes, help them structure it:

- **We believe** — one sentence on what the software could do (not how)
- **Will improve** — reference the specific baseline metric from Goals (e.g. *"reduce manual onboarding steps from 14 to 3"*). If no baseline was measurable, describe the observable change that would count as improvement.
- **We'll know it worked when** — a concrete, observable outcome
- **Validation approach** — the cheapest way to test this (build, mockup, manual, conversation)

If the user gets stuck, prompt with open questions (*"What do users struggle with most?"*, *"If you could only change one thing, what would it be?"*) — don't answer for them.

If a theory doesn't clearly address the problem or improve the current state, say so and ask whether the theory or the goals need adjusting. If no observable outcome can be stated, the theory isn't clear enough yet.

When the user runs dry, read the theories back and ask: *"Is that the set, or is there anything else nagging at you?"*

## Write the Theories document

```xml
<theories-template>
## Theories

### 1. <name>
- **We believe:** ...
- **Will improve:** ...
- **We'll know it worked when:** ...
- **Validation approach:** build | mockup | manual | conversation
- **Builds on:** <prior theory, if any>

### 2. <name>
...
</theories-template>
```

No implementation details, technical architecture, UI design, test cases, or time estimates.

## Output

Write to `./theories.md`. If the project uses GitHub issues:

1. Create one tracking issue labelled `goal` containing the Goals Document sections (problem, current state, root causes) plus a Theories checklist.
2. For each **build** theory, create a child issue labelled `theory` with the template fields. Mockup/manual/conversation theories are tracked as plain text in the goal issue's checklist — they don't need issues.
3. Link the child issues back into the goal's checklist.

Create `goal` and `theory` labels if they don't already exist.

## Loop-backs

Go back to `/goals` if a theory doesn't address the problem, the problem turns out to be several problems, or the baseline is missing data needed to form meaningful theories.
