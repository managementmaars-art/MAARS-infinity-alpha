# Claude Code Notes

Use this workflow in Claude Code when a repository needs stronger project memory and stricter phased execution.

## Instruction File Convention

- Prefer updating `CLAUDE.md` when a Claude-facing instruction file is needed.
- If the repository already contains `AGENTS.md`, keep the two files aligned instead of letting them drift.

## Marketplace Packaging

- This repository exposes `.claude-plugin/marketplace.json` so Claude Code users can add the repository as a marketplace.
- The marketplace entry points directly at `./skills/vibe-coding-standard-workflow`, matching Anthropic's public `anthropics/skills` pattern.

## Execution Discipline

- Reload `memory-bank/` files between implementation steps instead of relying on long-lived chat context.
- Do not advance to the next implementation step until the current one is validated.
