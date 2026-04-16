---
name: writing-agents-md
description: Use when creating, rewriting, pruning, or reviewing `AGENTS.md` or `CLAUDE.md`, especially to remove repo summaries, stale rules, and other low-signal global instructions. Trigger when deciding what belongs in always-on agent files versus a task-specific skill.
license: MIT
metadata:
  author: shihyuho
  version: "1.0.0"
---

# Writing Agents MD

## Overview

`AGENTS.md` and `CLAUDE.md` should be minimal guardrails, not repo handbooks.

Do not assume more global instructions improve outcomes; extra always-on guidance often slows or misdirects work.

Keep only information that is all three:

- hard to discover from the repo itself
- globally relevant across most tasks
- stable enough not to rot quickly

If a detail fails any of those tests, delete it, narrow it, or move it into a skill.

## When to Use

- Creating a new `AGENTS.md` or `CLAUDE.md`
- Reviewing, pruning, or rewriting an existing `AGENTS.md` or `CLAUDE.md`
- Removing repo summaries, stale rules, or handbook-style guidance from a global agent file
- Deciding whether guidance belongs in a global rule file or a skill

## Workflow

1. Identify the target file and whether the task is create, rewrite, or review.
2. Analyze the repo for high-value, non-obvious, global constraints.
3. If `AGENTS.md` or `CLAUDE.md` already exists, read it only after that analysis as historical input, not as the source of truth. If it conflicts with what the repo shows, trust the repo.
4. Classify each item as `keep`, `rewrite`, `delete`, `move-to-skill`, or `stale`.
5. Keep only rules that are non-discoverable, global, and stable.
6. Rewrite the file into a short, high-signal document.
7. Briefly explain what was removed or marked stale and why, so the file does not bloat again.

## Core Filter

Before keeping any line, ask:

1. Can the model discover this easily and reliably by reading the repo?
2. Does this matter for most tasks, not just some tasks?
3. Is this likely to remain true as files, paths, and architecture evolve?

If the answer is `yes / no / no`, it does not belong in a global rule file.

Even if something is technically discoverable, keep it only when omitting it is likely to cause a costly mistake and the model is unlikely to infer the right choice reliably.

## Keep

Good candidates for `AGENTS.md` or `CLAUDE.md`:

- non-obvious tool choices like `uv`, not `pip`
- environment-specific constraints like WSL path behavior
- expensive landmines like false-positive cache behavior
- legacy areas that still have production imports and must not be removed casually

Keep constraints that redirect the agent away from costly wrong defaults. Be cautious with instructions that add new standing requirements the agent would not otherwise follow.

## Delete Or Move Out

Usually remove these from global files:

- package scripts copied from `package.json`
- directory tours and architecture summaries
- tech stack summaries the repo already makes obvious
- file-path-heavy instructions that will rot quickly
- task-specific workflows, style preferences, or domain guidance

Move workflow or domain guidance into a skill instead of keeping it globally.

Every standing instruction is a potential landmine. Prefer a smaller file over a more prescriptive one.

## Guardrails

- Do not generate repo overviews, directory tours, or handbook-style summaries in global agent files.
- Do not repeat information the model can discover from code, docs, or config.
- Do not mention legacy technologies without clearly labeling them as legacy or avoid-using.
- Do not keep broad instructions in the global file if they only matter for some tasks.
- If the repo has little truly global guidance, prefer a very short file over a padded one.
- If unsure whether a line earns its keep, cut it.

## Output Shape

Aim for a short file that may include sections like:

- environment or tooling constraints
- important landmines
- minimal routing notes to existing skills

Avoid turning the file into a setup guide, architecture document, or coding standards manual.

If the repo has almost no truly global, non-obvious constraints, a tiny file is acceptable and no file is sometimes acceptable too.

## References

- See `references/checklist.md` for the full keep/delete decision list.
- See `references/examples.md` for bad, better, and good examples.
- See `references/principles.md` for the underlying rationale.
