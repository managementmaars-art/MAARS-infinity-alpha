# Contributing to servicenow-agent-skills

This guide is for ServiceNow developers who want to add a new skill to this repo. A *skill* is a directory containing a `SKILL.md` file that follows the [agentskills.io](https://agentskills.io) spec. Skills inject domain-specific knowledge into AI coding tools at context load time, giving them expert-level guidance without requiring tool-specific customisation.

## Adding a New Skill

Copy-paste this checklist into your PR description before submitting:

```markdown
- [ ] Skill directory created: `<skill-name>/SKILL.md`
- [ ] `SKILL.md` frontmatter: `name`, `description`, `version`, `compatibility` fields present
- [ ] `SKILL.md` name field matches parent directory name exactly
- [ ] `SKILL.md` body is routing-only (no inline API tables — all detail in references/)
- [ ] Token gate passes: SKILL.md body < 5000 tokens (~18000 chars)
- [ ] No tool-specific APIs: no `WebFetch`, `cursor_read_file`, or non-cross-platform calls
- [ ] Import paths use `@servicenow/sdk/core` (not `@servicenow/sdk`)
- [ ] `skills-ref validate` passes: 25/25
- [ ] Evals written for new skill (see Running Evals Locally below)
- [ ] PR title follows: `feat(<skill-name>): <brief description>`
```

## CI Gates

All four gates must pass before a PR can merge.

### Gate 1: skills-ref validate

Checks full SKILL.md spec compliance: frontmatter structure, line count ≤ 500, token count ≤ 5000, and progressive-disclosure structure (routing-only body with references in a subdirectory).

**Pass:**
```
✓ 25/25 checks passed
```

**Fail:**
```
✗ name field does not match directory name
✗ body exceeds 500 lines
```

**Run locally:**
```sh
uvx skills-ref validate <skill-name>/SKILL.md
```

---

### Gate 2: Token counter (`check-tokens.sh`)

Checks that the `SKILL.md` body stays under 5000 tokens. Uses a 4 chars/token approximation (18000 chars ≈ 4500 tokens) — no tokenizer dependency required.

**Pass:**
```
[PASS] sn-sdk-fluent: 3421 tokens (limit: 5000)
```

**Fail:**
```
[FAIL] my-skill: 6200 tokens (limit: 5000)
```

**Run locally:**
```sh
bash scripts/check-tokens.sh
```

---

### Gate 3: Tool API lint (`check-tool-apis.sh`)

Scans all `SKILL.md` files for tool-specific API calls that break cross-platform compatibility. Skills must work in Claude Code, Cursor, VS Code Copilot, Antigravity, and Codex — none of which share the same tool APIs.

**Blocked calls:** `WebFetch`, `cursor_read_file`, `Bash(`, `computer_use`

**Pass:**
```
[PASS] No tool-specific APIs found
```

**Fail:**
```
[FAIL] sn-sdk-fluent/SKILL.md:42: WebFetch — tool-specific, use external references instead
```

**Run locally:**
```sh
bash scripts/check-tool-apis.sh
```

---

### Gate 4: Import path enforcement

Checks that all code examples use `@servicenow/sdk/core` rather than `@servicenow/sdk`. The bare import path compiles but loads extra modules, causing type mismatches at runtime. This gate is enforced via evals, not a standalone script.

**Pass:** eval assertion `import.*@servicenow/sdk/core` matches all examples

**Fail:**
```typescript
import { Table } from '@servicenow/sdk'  // missing /core suffix
```

**Correct:**
```typescript
import { Table, StringColumn } from '@servicenow/sdk/core'
```

---

## Running Evals Locally

### Install skills-ref

```sh
pip install git+https://github.com/agentskills/agentskills.git#subdirectory=skills-ref
```

### Validate a skill

```sh
uvx skills-ref validate <skill-name>/SKILL.md
```

### Eval format

Each skill ships with an `evals/evals.json` file. Evals are structured as prompt + expected assertions, covering both trigger cases (skill knowledge applied) and no-trigger cases (off-topic queries routed elsewhere).

Example path:
```
sn-sdk-fluent/evals/evals.json
sn-sdk-setup/evals/evals.json
sn-scripting/evals/evals.json
```

### Eval methodology caveat (v1)

The published benchmark (87.5% with skill vs 30.6% without) was measured by pasting `SKILL.md` content inline into the AI context rather than installing to `~/.agents/skills/`. The numbers are valid but reflect this methodology. Future iterations should test with real installed paths to ensure the install-path loading behaviour is also covered.

---

## Making the Repo Public

Before making the repository public:

1. Replace all `OWNER` placeholders in `README.md` and `install.sh` with the actual GitHub username or organisation name.
2. Confirm `npm publish` credentials if you intend to publish the npm package.
3. Once public, `npx skills add OWNER/servicenow-agent-skills` will work automatically — no manual registry submission is required. Skills appear on the leaderboard when users run that command.

---

## License

All contributions are MIT licensed.
