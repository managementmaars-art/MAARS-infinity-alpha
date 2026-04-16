---
name: goals
description: Produce a Goals Document through user interview — a focused problem statement, current state baseline, and root causes. Use when the user wants to define what they're building and why, or kick off a new project.
argument-hint: "[optional: brief description of the idea or problem]"
---

Force clarity about the PROBLEM before anyone thinks about solutions. Interview the user until you can state it in one sentence, with a measurable baseline and identified root causes.

## Interview

Push for these answers, one question at a time. If an answer might live in the codebase or existing files, explore first and confirm with the user rather than asking cold.

- **Who has this problem and why it matters to them.**
- **What they do today** — current workflow, or why existing solutions fail.
- **How bad it is** — push for concrete numbers (frequency, duration, failure rates, costs). If the user doesn't have data, propose ways to gather it. If no baseline can be established, flag it in the Goals Document — theories without baselines can't be measured.
- **Root causes** — keep asking "why" until distinct causes surface.

If the user describes features, UI, or implementation, redirect: *"That's a solution — what's the problem it solves?"*

Push for **one focused problem statement**. One sentence. If several problems surface, help the user pick the one that matters most right now.

## Categorise root causes

Walk through each root cause and tag it:

- 🔧 **Potentially solvable by software** — friction, automation gaps, tooling, process steps
- 🧠 **Likely not a software problem** — motivation, fear, habit, external constraints, human judgement

Be honest. Don't force causes into the software bucket.

## Write the Goals Document

```xml
<goals-template>
## Problem Statement
Who, what, why — one focused problem, one sentence.

## Current State
What happens today. How bad it is. Any baseline data or observations.

## Root Causes
- 🔧 Software-solvable: ...
- 🧠 Not a software problem: ...
</goals-template>
```
No features, solutions, user stories, technical architecture, or success criteria. Success criteria belong to individual theories — they come later.

## Output

Write to `./goals.md`. If the project uses GitHub issues, `/theories` will fold this into the goal tracking issue later.

Present the result for sign-off.
