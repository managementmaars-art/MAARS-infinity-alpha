---
name: spec-writer
description: "Generate structured specifications for a feature using openspec. Produces specs, design, and tasks documents. Called by start-workflow or standalone. Triggers on: /spec-writer, write specs, generate specs, create spec, write requirements."
---

# spec-writer

IRON LAW: Always generate all four documents in order (proposal → specs → design → tasks) before marking done. openspec's `spec-driven` schema requires proposal.md first — skipping it will cause validate to fail. Read project conventions before writing.

## Invocation

Called by start-workflow with context in state.json, or standalone:
```
/spec-writer "feature description"
```

## Execution Flow

### Step 1 — Load Project Conventions

Resolve the conventions directory (supports all agents):
```bash
CONVENTIONS_DIR=$(find \
  .claude/conventions \
  .cursor/conventions \
  .windsurf/conventions \
  .cline/conventions \
  .agents/conventions \
  -maxdepth 0 -type d 2>/dev/null | head -1)
```

If found, read the following files (if they exist):
- `$CONVENTIONS_DIR/frontend.md` — FE framework, component patterns, styling conventions
- `$CONVENTIONS_DIR/backend.md`  — API structure, error handling, logging patterns
- `$CONVENTIONS_DIR/database.md` — Schema naming, migration conventions, indexing rules

If no conventions directory is found, proceed with general best practices.

### Step 2 — Initialize openspec (once per project)

```bash
# Check if already initialized
if [ ! -f ".openspec/config.yaml" ]; then
  openspec init .
fi
```

### Step 3 — Create Change

```bash
CHANGE_NAME="{feature_name}"
openspec new change "$CHANGE_NAME"
```

### Step 4 — Generate proposal document (REQUIRED FIRST)

```bash
openspec instructions proposal --change "$CHANGE_NAME"
```

Read the instructions output. Then write the proposal document with:
- Problem statement: what problem this feature solves
- Proposed solution: high-level approach (2-3 sentences)
- Success criteria: how we know this is done
- Scope: what's in and explicitly out of scope

This must exist before specs/design/tasks — openspec validate will fail without it.

### Step 5 — Generate specs document

```bash
openspec instructions specs --change "$CHANGE_NAME"
```

Read the instructions output. Then write `{change_dir}/specs` with:
- Functional requirements (numbered list, minimum 5)
- Non-functional requirements (performance, security, accessibility)
- Dependencies on other systems

Incorporate project conventions from Step 1 where relevant.

### Step 6 — Generate design document

```bash
openspec instructions design --change "$CHANGE_NAME"
```

Read instructions, then write the design document with:
- Architecture decision (which components are affected)
- Data model changes (new tables/fields/schemas)
- API contract (endpoints, request/response shapes)
- UI/UX flow (if frontend involved)
- Security considerations

### Step 7 — Generate tasks document

```bash
openspec instructions tasks --change "$CHANGE_NAME"
```

Read instructions, then write the tasks document as an ordered checklist:
- Each task must be independently implementable
- Each task must be completable in one git commit
- Tasks ordered from foundational (DB/model) to surface (UI/API)
- Include test tasks explicitly

### Step 8 — Validate

```bash
openspec status --change "$CHANGE_NAME" --json
openspec validate "$CHANGE_NAME"
```

If validation fails, fix the flagged issues before marking done.

### Step 9 — Update State

Write specs_dir and artifact paths to state.json:
```python
state['phases']['spec-writer']['status'] = 'done'
state['phases']['spec-writer']['artifacts'] = {
    'proposal': '<path>',
    'specs': '<path>',
    'design': '<path>',
    'tasks': '<path>',
}
state['phases']['spec-writer']['openspec_change'] = CHANGE_NAME
state['phases']['spec-writer']['openspec_validated'] = True
state['specs_dir'] = '<openspec change directory>'
```

## Output Quality Rules

- proposal: Must include success criteria
- specs: At least 5 functional requirements
- design: Must include data model changes even if "none" (state it explicitly)
- tasks: Minimum 4 tasks, maximum 20; each ≤ 2 hours of work
- No vague tasks like "implement feature" — each must be specific and verifiable
