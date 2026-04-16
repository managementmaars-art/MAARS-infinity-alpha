---
name: spec
description: Turn one theory into a clear brief — headline interaction, supporting jobs, and system sketch. The bridge between a theory and the slicing step. Use after /theories to specify one theory at a time.
argument-hint: "[optional: path to Theories, or paste/describe the theory]"
---

Turn one theory into a clear picture of what the software does — from the user's experience down to responsibilities and collaborations.

## Read the theory

Load it from `./theories.md` or a GitHub issue. Summarise it back — what this theory delivers, what aspect of the current state it improves, what it builds on.

## Workflow

### Identify the Key user interactions

Prompt the user for the primary action or actions the user needs to take to get the value promised by the theory.

Avoid being drawn into discussing implementation details, this is about the interaction and experience in terms of what the user wants to do, what they provide, what they get back from this action.

### Identify Supporting jobs

*"What must the system be able to do to deliver that experience?"*

### System sketch

*"Looking at the interaction and the jobs, how do the pieces of the system fit together? What data does each job need, and who provides it?"*

Work with the user to identify the system's responsibilities and collaborations. 

Napkin-level, not architecture, and **not** the UI's layout. 

## Write the spec

```xml
<spec-template>
**Status:** Spec ready, awaiting /spike (or /slice if no unknowns)
**Part of:** <theories reference>
**Improves:** <aspect of current state, referencing baseline>
**Builds on:** <optional>
**Requires:** <api, llm, external service>

## Description
<one sentence on what the software can do after this theory>

## Headline Interaction
<what the user sees and does>

## Supporting Jobs
<list of capabilities with one-line descriptions>

## System Sketch
<system responsibilities, collaborations, data flow — not UI layout>
</spec-template>
```

No code, test implementations, technology choices, or physical UI design (wireframes, mockups, screen layouts, component choices). The spec is a logical description; module design emerges in `/slice`, and physical implementation in `/tdd`.

## Output

Write to `./specs/<theory-number>-<slug>.md`, or edit the corresponding GitHub issue body.

## Loop-backs

Go back to `/theories` if specifying reveals the theory can't be described as a single thin slice, doesn't clearly improve any aspect of current state, or depends on capabilities that belong to a different theory.
