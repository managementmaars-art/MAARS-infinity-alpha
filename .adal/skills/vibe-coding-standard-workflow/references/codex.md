# Codex Notes

Use this workflow in Codex when the repository needs a repeatable, document-first delivery loop.

## Instruction File Convention

- Prefer updating `AGENTS.md` when a Codex-facing instruction file is needed.
- If the repository already uses `CLAUDE.md` as well, keep both files aligned instead of splitting policy across them.

## Installation Shape

- Keep `agents/openai.yaml` present for Codex UI metadata.
- Publish the skill under `skills/vibe-coding-standard-workflow/` so Codex GitHub installers can target a single path cleanly.

## Execution Discipline

- Assume the user is the validation gate unless they explicitly ask Codex to run tests end-to-end.
- After each approved step, update `memory-bank/progress.md` and `memory-bank/architecture.md` before moving on.
