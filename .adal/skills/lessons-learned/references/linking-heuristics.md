# Linking Heuristics

Use these rules to build `related` links for lesson cards.

This file supports `SKILL.md`. It does not define independent limits.

## High-Value Gate (2-of-4)

Only create `related` links when at least **2** of these conditions are true:

1. The lesson is reusable across multiple task types.
2. The lesson comes from a high-cost mistake (multiple attempts or significant time loss).
3. The lesson depends on critical parameters, config, or ordering decisions.
4. The lesson naturally connects to at least two existing cards.

If fewer than two conditions are true, do not add `related` links.

## Deterministic Ranking

When multiple candidates are available, rank in this order:

1. Tag overlap count (descending)
2. Keyword overlap count from title + lesson text (descending)
3. Card recency by `date` (newer first)
4. Stable tie-breaker by `id` (ascending)

Select the top candidates and cap at 2 links.

## Link Constraints

- Never link to the current card itself.
- Never duplicate IDs in `related`.
- Keep `related` focused: include fewer links rather than weak links.
- Use only `[[card-id]]` format.

## Broken-Link Handling

If a `related` target does not exist:

1. Remove the invalid entry.
2. Warn in output/log.
3. Continue workflow without failure.
4. Re-rank remaining valid candidates and backfill if qualified.

If no qualified candidates remain, keep `related: []`.
