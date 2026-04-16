# writing-agents-md

## Purpose

This skill helps agents create or prune `AGENTS.md` / `CLAUDE.md` so they stay short, high-signal, and focused on real global constraints.

The rule of thumb:

1. Can the agent discover this from the repo?
2. Does it matter across most tasks?
3. Will it stay true long enough to deserve always-on context?

If not, delete it, narrow it, or move it into a task-specific skill.

## Source priority

- Analyze the repo before reading any existing `AGENTS.md` or `CLAUDE.md`.
- Treat existing files as historical input only; if they conflict with what the repo shows, trust the repo.

## What it optimizes for

- keep non-obvious tool or environment hazards
- keep production landmines that look safe to remove
- delete repo summaries, script lists, and directory tours
- avoid turning deleted noise into generic global meta-guidance

If a repo has no real global constraints yet, a tiny file or no file is acceptable.

## Installation

```bash
npx skills add shihyuho/skills --skill writing-agents-md -g
```

## References

- Addy Osmani, "Stop Using /init for AGENTS.md"  
  https://addyosmani.com/blog/agents-md/
- Theo, "Delete your CLAUDE.md (and your AGENT.md too)"  
  https://www.youtube.com/watch?v=GcNu6wrLTJc
- Matt Pocock, "Never Run claude /init"  
  https://www.youtube.com/watch?v=9tmsq-Gvx6g
- Lulla et al., arXiv:2601.20404  
  https://arxiv.org/abs/2601.20404
- Gloaguen et al., arXiv:2602.11988  
  https://arxiv.org/abs/2602.11988
