# Writing Agents MD Checklist

Use this checklist when reviewing `AGENTS.md` or `CLAUDE.md` content.

## Keep / Delete / Move Decision

For each line or section, ask:

1. **Discoverability**
   - Can the model learn this easily and reliably by reading `package.json`, README, config files, or source code?
   - If yes, usually delete it from the global file.
   - Keep it only if missing it would likely cause a costly mistake and the correct choice is still easy for the model to miss.

2. **Global relevance**
   - Does this matter across most tasks in the repo?
   - If it only matters for frontend, backend, docs, release, or one workflow, move it to a skill.

3. **Stability**
   - Will this still be true after the next refactor, file move, or dependency swap?
   - If not, narrow it or delete it.

4. **Anchoring risk**
   - Could this make the model reach for an outdated or legacy pattern?
   - If yes, delete it or mark it explicitly as `legacy`, `deprecated`, or `do not extend`.

5. **Operational impact**
   - If omitted, is the model likely to make a costly mistake?
   - If yes, it is a strong keep candidate.

## Strong Keep Candidates

- unusual package manager or task runner choices
- environment quirks not obvious from the repo
- test or cache traps that cause misleading results
- deprecated or dangerous directories that still matter in production
- rules about irreversible damage in sensitive areas

## Strong Delete Candidates

- script lists copied from `package.json`
- "this project uses React / Vite / TypeScript"
- directory structure summaries
- architecture paragraphs that restate code organization
- long style guides that only apply to some work

## Move-To-Skill Candidates

- feature implementation workflows
- review or verification protocols
- frontend or backend design preferences
- domain-specific modeling rules
- release, deployment, or incident procedures

## Final Review

Before finishing, check:

- Is every remaining line non-discoverable, global, and stable?
- For lines that are technically discoverable, is there a strong operational reason to keep them anyway?
- Is the file short enough that every line earns its token cost?
- Would the model still understand the repo without this file? It should.
- Does the file steer away from landmines rather than explain the whole codebase?
