# Writing Agents MD Principles

This skill is based on three recurring ideas:

## 0. Empirical results are mixed

Evidence is mixed: concise context can help bounded tasks, but extra always-on instructions can hurt broader work. Default to minimalism.

## 1. Global context is expensive

Everything in `AGENTS.md` or `CLAUDE.md` competes with the actual task for attention and tokens. A short high-signal file is better than a long accurate one.

## 2. Redundant context is noise

If the model can rediscover something by reading the repo, putting the same fact into a global rule file usually adds noise rather than value.

## 3. Anchoring is real

Mentioning a technology, pattern, or path makes the model more likely to reach for it. This is especially risky for legacy systems and partial migrations.

## 4. Friction should drive edits

Use global rule files to capture repeated agent mistakes or hidden landmines that have not yet been solved in code, tooling, or tests. Do not treat them as permanent architecture documentation.

## 5. Skills should absorb task-specific guidance

When the guidance is conditional, workflow-heavy, or domain-specific, it belongs in a skill that can be loaded on demand rather than in always-on global instructions.
