---
name: metamedium
description: This skill should be used when the key question is whether to optimize content (what) or redesign form (how/medium). Trigger on "내용 vs 형식", "content vs form", "metamedium", "형식을 바꿔볼까", "새로운 포맷", "perspective shift", "diminishing returns". For requirement clarification use vague; for strategy blind spots use unknown.
user-invocable: true
argument-hint: [work-or-plan]
---

# Metamedium: Content vs Form Reframing

Distinguish **content** (what is produced) from **form** (the medium/structure that produces or delivers it) to decide where leverage is highest.

## When to Use

- Output quality improves slowly despite more effort
- Repeatedly producing content inside the same format
- Deciding between incremental optimization vs structural redesign

For requirement clarification, use **vague**. For strategy blind spots, use **unknown**.

## Core Idea

- Content optimization is usually linear
- Form redesign can be multiplicative

Use this question when stuck:

`What new form could make this recurring problem disappear?`

## Protocol

### Phase 1: Label

Classify the user's current activities:
- `[CONTENT]` direct outputs (doc, code change, campaign copy)
- `[FORM]` systems/pipelines/templates/tools enabling repeated outputs

### Phase 2: Fork (AskUserQuestion required)

Ask user to choose one path using options:
- Proceed with content optimization
- Explore form redesign
- Content now, track form opportunity

### Phase 3: Branch

If content:
- Proceed and add a `Form Opportunity` note

If form:
- Propose 2-3 alternative forms
- For each: structure, new properties, minimum viable test

If hybrid:
- Deliver content outcome plus deferred form backlog item

### Phase 4: Output

```markdown
## Content/Form Analysis

**Current work**: [description]
**Classification**: [CONTENT / FORM]

### Form Opportunity
| Field | Detail |
|-------|--------|
| Alternative form | ... |
| New properties | ... |
| Minimum test | ... |
| Status | exploring / later / rejected |
```

## Rules

1. Always label current work first
2. Do not force form redesign when costs exceed leverage
3. If user stays with content, still preserve at least one form option
4. Prefer testable form changes over abstract ideation

## Additional Resources

- `references/alan-kay-quotes.md`
