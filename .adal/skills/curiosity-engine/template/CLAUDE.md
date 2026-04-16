# Curiosity Engine

A self-improving knowledge wiki. Uses the `curiosity-engine` skill.

## Layout
- `vault/` — raw source files + FTS5 search index. Append-only.
- `wiki/` — git-tracked markdown. The agent maintains this.
- `wiki/schema.md` — operating protocol. Read before any operation.

## Quick commands
- "Add <file> to the vault" — ingest a source
- "What do I know about X?" — query the wiki
- "Lint" — check wiki health
- "Run the curator for N cycles" — autonomous improvement

## Bash discipline (hard rule)

This workspace is designed for uninterrupted autonomous loops. Approval prompts break that, so the bash surface is deliberately tiny. The ONLY bash commands allowed:

1. `git -C wiki <subcmd> ...` — never `cd wiki && git ...`, never `git -c X=Y -C wiki ...`
2. `python3 <skill_path>/scripts/<named_script>.py ...` — never `python3 -c "..."`
3. `bash <skill_path>/scripts/evolve_guard.sh ...`
4. `date ...`

**For everything else, use the tool layer:**
- Read (not `cat`/`head`/`tail`/`less`)
- Glob (not `ls`/`find`)
- Grep (not `grep`/`rg`)
- Edit / Write (not `sed`/`mv`/`cp`/`touch`/`rm`/`>>`/`>`)

**No compound shell:** no pipes (`|`), no `&&`, no `$(...)`, no backticks, no heredocs, no inline scripts. One command per bash call. If you need two things, make two calls.

**Why:** every other bash command either has a safe tool-layer equivalent or cannot be scoped to the workspace via prefix matching without risking the user's wider filesystem. Breaking this rule means approval prompts, which means an autonomous loop stops and waits for a human — defeating the point.

Subagents spawned from this workspace inherit the same rule. Include the discipline block verbatim in every Agent prompt.
