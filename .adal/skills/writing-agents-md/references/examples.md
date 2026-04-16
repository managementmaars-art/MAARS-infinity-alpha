# Writing Agents MD Examples

## Example 1: Package Scripts

### Bad

```md
## Commands
- `pnpm dev`
- `pnpm build`
- `pnpm test`
- `pnpm lint`
```

Why it is bad: this duplicates `package.json`.

### Better

```md
Use `pnpm`, not `npm`.
```

Why it is better: the tool choice may not be obvious from one file alone and changes agent behavior.

## Example 2: Architecture Summary

### Bad

```md
This app uses React on the frontend, Node on the backend, and packages under `packages/`.
The API routes live in `src/server/routes`.
```

Why it is bad: the model can discover this directly from the repo.

### Better

```md
`legacy/` still has production imports. Do not delete or migrate it casually.
```

Why it is better: it surfaces a costly landmine that code structure alone may not make obvious.

## Example 3: Legacy Technology

### Bad

```md
We use tRPC on the backend.
```

Why it is bad: this can anchor the model toward the wrong pattern if tRPC is only legacy.

### Better

```md
tRPC is legacy here. Do not add new tRPC endpoints unless the task explicitly requires touching legacy paths.
```

Why it is better: it labels the technology and tells the model how not to misuse it.

## Example 4: Workflow Guidance

### Bad

```md
Always use TDD, run full validation, and follow our frontend review process.
```

Why it is bad: this is broad workflow guidance better handled by skills.

### Better

```md
Use `writing-plans` when the user asks for an implementation plan.
```

Why it is better: it routes to a specific skill instead of storing a vague global workflow rule.

### Best

Delete the line from `AGENTS.md` / `CLAUDE.md` entirely if the repo already has the skill installed and no extra global routing note is needed.

## Example 5: Tiny File Is Acceptable

### Good

```md
# AGENTS.md

- Use `uv`, not `pip`.
- You are on WSL; watch for Windows/Linux path resolution issues.
- `legacy/` still has production imports; do not delete it blindly.
```

Why it is good: short, operational, non-obvious, and globally useful.

## Example 6: No File Needed

### Good

If the only candidate content is repo summary, scripts, architecture, and task-specific workflow guidance, do not create `AGENTS.md` / `CLAUDE.md` yet. Wait until repeated agent mistakes reveal a real global constraint.
