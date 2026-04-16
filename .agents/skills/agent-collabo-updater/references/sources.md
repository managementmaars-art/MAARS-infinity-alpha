# References

## Sources Particularly Referenced by This Skill

| Source | Key Takeaway |
|--------|-------------|
| [vercel-labs/skills CLI source](https://github.com/vercel-labs/skills/blob/main/src/cli.mts) | `runAdd` / `removeCommand` / `runList` flag semantics — `-g` is a scope switch, not a global-only flag |
| [Agent Skills Specification](https://agentskills.io/specification) | SKILL.md frontmatter format and `metadata.version` field |
| [npx skills lock file format](https://github.com/vercel-labs/skills/blob/main/src/skill-lock.ts) | `~/.agents/.skill-lock.json` v3 schema with `source`, `sourceType`, `skillFolderHash` |

## Why this skill exists

The default `npx skills check` and `npx skills update` commands operate on every skill in the global lock file at once and cannot target a specific package. agent-collabo provides its own manifest at `https://raw.githubusercontent.com/dev-goraebap/agent-collabo/main/manifest.json`, and this skill applies the diff between that manifest and what is locally installed — covering updates, deprecations, and renames in a single user-friendly flow.
