# Zettel Card Template

Use this template when creating a new lesson card.

This file supports `SKILL.md`. If this file and `SKILL.md` disagree, follow
`SKILL.md`.

```markdown
---
id: <semantic-kebab-case-id>
date: <YYYY-MM-DD>
scope: <project | module | feature>
tags: [tag1, tag2, tag3]
source: <user-correction | bug-fix | retrospective>
confidence: <0.0-0.9>
related: ["[[related-card-id-1]]"]
---

# <One-line lesson title>

## Context
<What was happening when the mistake occurred or the insight emerged.>

## Mistake
<What went wrong, or what was suboptimal.>

## Lesson
- <Extracted rule or best practice>
- <Additional key points>

## When to Apply
<Future situations where this lesson is relevant.>
```

## Field Guidelines

- **id**: Use descriptive slugs. Prefer `api-timeout-retry-pattern` over `lesson-001`.
- **scope**: Choose one — `project` (repo-wide), `module` (package/directory), `feature` (specific flow/component).
- **tags**: 3–6 lowercase tags. Include technology names, error categories, and domain concepts.
- **source**: Choose one — `user-correction` (user pointed out a mistake), `bug-fix` (discovered during debugging), `retrospective` (insight from task review).
- **confidence**: Initialize by source (`user-correction=0.7`, `bug-fix=0.5`, `retrospective=0.3`). Keep range `0.0-0.9`. For recall/capture behavior and `0.0` handling, follow `SKILL.md`.
- **related**: 0-2 high-relevance wikilink references in `[[card-id]]` form. Add links only when high-value criteria are met (2-of-4 gate in `references/linking-heuristics.md`).
- **Context**: Keep to 1–2 sentences. Enough context to understand the scenario.
- **Mistake**: Be specific. Include error messages or symptoms when available.
- **Lesson**: Write actionable rules, not vague advice. Prefer "always do X before Y" over "be careful with X".
- **When to Apply**: Think in terms of triggers — what keywords or task types should activate recall of this lesson.

## Validation Checklist

- Required fields exist: `id`, `date`, `scope`, `tags`, `source`, `confidence`, `related`.
- `scope` is one of `project`, `module`, `feature`.
- `tags` count is between 3 and 6.
- `confidence` is numeric and between 0.0 and 0.9.
- `related` count is between 0 and 2.
- Every `related` target resolves to an existing card ID.
- Index metadata should match the card after any update.
