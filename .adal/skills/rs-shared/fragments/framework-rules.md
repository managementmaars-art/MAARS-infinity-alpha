# Framework Rules

## Never Overwrite User Work

All spec files (01-05) and Cypress files belong to the user once created. Never overwrite, replace, or regenerate them without explicit approval. When making changes:
- Present diffs and get approval before writing
- Preserve all existing content — only add or modify what was discussed
- For Cypress files: merge additions, never replace

Conventions docs (`rootspec/CONVENTIONS/`) are created by `/rs-spec` and maintained by `/rs-impl`. Once created, they are never overwritten — `/rs-spec` skips creation if they already exist.

The only file that may be replaced during upgrades is `00.FRAMEWORK.md`.

## Reference Hierarchy

Each level can ONLY reference higher levels, never lower:

- **L1** → External sources only
- **L2** → L1 + External
- **L3** → L1-2 + External
- **L4** → L1-3 + Sibling L4 + External
- **L5** → All levels (1-4) + External

Referencing a lower level from a higher level is a violation.

## Placeholder Rule

Levels 1-4 must NOT contain numeric values. Use descriptive placeholders:
- `[short duration]` not `500ms`
- `[base_points]` not `100`
- `[brief delay]` not `2 seconds`

Only Level 5 (FINE_TUNING YAML) contains actual numeric values.

## Design Pillar Quality

Design Pillars (L1) must describe **feelings**, not features:
- Good: "Effortless Relief", "Empowered Action", "Calm Clarity"
- Bad: "Fast Search", "Social Features", "Dashboard Analytics"

Each pillar = one sentence describing an emotional experience.
Products typically have 3-5 pillars.

## Single Source of Truth

Each concern lives at exactly one level. No duplication across levels.
Changes flow downward through abstraction layers.

## Decision Filter

Every feature must support at least one Design Pillar from Level 1.
If a feature doesn't support any pillar, it doesn't belong.
