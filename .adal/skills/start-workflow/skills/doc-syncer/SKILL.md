---
name: doc-syncer
description: "Sync project documentation after a feature is implemented: update {agent}/conventions/ and project README. Triggers on: /doc-syncer, sync docs, update documentation, update readme."
---

# doc-syncer

IRON LAW: Only update docs that are directly affected by the changes in this run. Do not rewrite docs wholesale.

## Invocation

Called by start-workflow, or standalone after implementation:
```
/doc-syncer
```

## Execution Flow

### Step 1 — Identify changed files

```bash
cd "$PROJECT_DIR"
git diff --name-only HEAD~{feature_commit_count} HEAD
```

Group changes by area:
- `src/components/**`, `src/pages/**`, `src/styles/**` → frontend changes
- `src/api/**`, `src/routes/**`, `src/middleware/**` → backend changes
- `migrations/**`, `prisma/**`, `schema.*` → database changes

### Step 2 — Update conventions

Resolve conventions directory (supports all agents):
```bash
CONVENTIONS_DIR=$(find \
  .claude/conventions \
  .cursor/conventions \
  .windsurf/conventions \
  .cline/conventions \
  .agents/conventions \
  -maxdepth 0 -type d 2>/dev/null | head -1)
```

If found, for each changed area read and update the corresponding file:
- Frontend changes → `$CONVENTIONS_DIR/frontend.md`
- Backend changes  → `$CONVENTIONS_DIR/backend.md`
- Database changes → `$CONVENTIONS_DIR/database.md`

Only add genuinely new patterns — do not duplicate existing entries.

If no conventions directory is found, skip this step.

### Step 3 — Update README

Read current `README.md`. Update only the sections affected by this feature:
- **Features** section: add a bullet for the new feature
- **API Reference** section: add/update endpoint docs if API changed
- **Environment Variables** section: add any new env vars introduced

Do not rewrite sections unrelated to this feature.

### Step 4 — Commit docs

```bash
git add "$CONVENTIONS_DIR" README.md
git commit -m "docs: update conventions and README for {feature_name}"
```

If no conventions directory was found, commit only README.md.

### Step 5 — Update state

```python
state['phases']['doc-syncer']['status'] = 'done'
state['phases']['doc-syncer']['files_updated'] = [list of updated files]
```
