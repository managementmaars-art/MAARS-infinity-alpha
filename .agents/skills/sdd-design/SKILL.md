---
name: sdd-design
description: >
  Produces the technical design with architecture decisions, data flow, and a file change plan.
  Trigger: /sdd-design <change-name>, technical design, change architecture, how to implement.
format: procedural
model: sonnet
thinking: enabled
metadata:
  version: "3.0"
---

# sdd-design

> Produces the technical design with architecture decisions, data flow, and a file change plan.

**Triggers**: `/sdd-design <change-name>`, technical design, change architecture, sdd design

---

## Purpose

The design defines **HOW to implement** what the specs say the system MUST do. It is the bridge between requirements and code. It documents technical decisions and their justification.

---

## Process

### Skill Resolution

When the orchestrator launches this sub-agent, it resolves the skill path using:

```
1. .claude/skills/sdd-design/SKILL.md     (project-local — highest priority)
2. ~/.claude/skills/sdd-design/SKILL.md   (global catalog — fallback)
```

Project-local skills override the global catalog. See `docs/SKILL-RESOLUTION.md` for the full algorithm.

---

### Step 0 — Load project context + Spec context preload

Follow `skills/_shared/sdd-phase-common.md` **Section F** (Project Context Load) and **Section G** (Spec Context Preload). Both are non-blocking.

---

### Step 1 — Read prior artifacts

I must read:

- The proposal artifact:
  - `mem_search(query: "sdd/{change-name}/proposal")` → `mem_get_observation(id)`.
  - If not found and Engram not reachable: proposal content passed inline from orchestrator.
- The spec artifact:
  - `mem_search(query: "sdd/{change-name}/spec")` → `mem_get_observation(id)`.
  - If not found and Engram not reachable: spec content passed inline from orchestrator.
- `ai-context/architecture.md` if it exists
- `ai-context/conventions.md` if it exists

Then I read real code:

- Relevant entry points
- Files that will be affected according to the proposal
- Existing patterns to follow (not reinvent)
- Existing tests (they reveal current contracts)

### Step 2 — Design the technical solution

I evaluate the solution considering:

- Patterns already used in the project (prefer consistency)
- Minimal impact on existing code
- Testability
- Reversibility (rollback plan from the proposal)

#### Skills Registry cross-reference

When recommending a skill, library, or technology pattern in the design, I MUST check the project Skills Registry extracted in Step 0 and follow these rules:

- **Registered skill**: reference it by its exact registered name (e.g., `typescript`, `react-19`).
- **Global catalog skill, not registered in project**: mark it as optional with a note, e.g. `[optional — not registered in project; add via /skill-add <name>]`.
- **Skill not in the global catalog**: state it as a new dependency and flag it for review.

This check applies to the Technical Decisions table, the Testing Strategy table, and any inline recommendations in the design narrative. It ensures design output stays aligned with the project's declared toolset.

### Step 3 — Create design.md

I persist the design artifact to engram:

Call `mem_save` with `topic_key: sdd/{change-name}/design`, `type: architecture`, `project: {project}`, content = full design markdown. Do NOT write any file.

If Engram MCP is not reachable: skip persistence. Return design content inline only.

Content format:

```markdown
# Technical Design: [change-name]

Date: [YYYY-MM-DD]
Proposal: engram:sdd/[name]/proposal

## General Approach

[High-level description of the technical solution in 3-5 lines]

## Technical Decisions

| Decision   | Choice           | Discarded Alternatives         | Justification     |
| ---------- | ---------------- | ------------------------------ | ----------------- |
| [decision] | [what is chosen] | [alternative A, alternative B] | [why this choice] |

## Data Flow

[ASCII diagram or description of the flow]

Example:
```

Request → Middleware → Controller → Service → Repository → DB
↓
Validator (Zod)
↓
Response DTO

````

## File Change Matrix
| File | Action | What is added/modified |
|------|--------|------------------------|
| `src/modules/auth/auth.service.ts` | Modify | Add `refreshToken()` method |
| `src/modules/auth/auth.controller.ts` | Modify | New endpoint POST /auth/refresh |
| `src/modules/auth/dto/refresh.dto.ts` | Create | DTO for refresh request |
| `src/modules/auth/auth.module.ts` | Modify | Register new provider |
| `tests/auth/refresh-token.spec.ts` | Create | Tests for the new endpoint |

## Interfaces and Contracts
[Type definitions, interfaces, DTOs, schemas to be created]

```typescript
// Example
interface RefreshTokenRequest {
  refreshToken: string;
}

interface RefreshTokenResponse {
  accessToken: string;
  expiresIn: number;
}
````

## Testing Strategy

| Layer       | What to test              | Tool                 |
| ----------- | ------------------------- | -------------------- |
| Unit        | [service/function]        | [jest/vitest/pytest] |
| Integration | [endpoint/module]         | [supertest/httpx]    |
| E2E         | [full flow if applicable] | [playwright/cypress] |

## Migration Plan

[If there are changes to DB, schema, or existing data:]

- Step 1: [migration script]
- Step 2: [gradual rollout if applicable]
- Step 3: [post-cleanup]

[If no migration: "No data migration required."]

## Open Questions

[Aspects that need clarification before implementing]

- [question]: [impact if not resolved]

[If none: "None."]

````

### Step 4 — ADR Detection and Generation

This step is **non-blocking**: any failure produces a warning in the output, never `status: blocked` or `status: failed`.

1. **Scan for significant decisions**: read the Technical Decisions table in the newly created `design.md`. For each row, check whether the text (across all columns) contains any of the following keywords (case-insensitive):
   `pattern`, `convention`, `cross-cutting`, `replaces`, `introduces`, `architecture`, `global`, `system-wide`, `breaking`

2. **No match → skip silently**: if no row matches any keyword, do nothing and produce no output for this step.

3. **Match found → generate ADR**:
   a. **Prerequisite check**: if `docs/templates/adr-template.md` does not exist OR `docs/adr/README.md` does not exist, log the warning `"ADR infrastructure not found (docs/templates/adr-template.md or docs/adr/README.md missing) — skipping ADR generation"` and stop this step.
   b. **Determine next ADR number**: count existing files matching `docs/adr/[0-9][0-9][0-9]-*.md`. The next number is `count + 1`, zero-padded to 3 digits (e.g., `001`, `012`, `100`).
   c. **Derive slug**: `<NNN>-<change-name>[-<first-matched-keyword>]`, all lowercase, spaces replaced with hyphens, non-alphanumeric characters (except hyphens) removed, truncated to 50 characters.
   d. **Copy template**: copy `docs/templates/adr-template.md` to `docs/adr/<slug>.md`.
   e. **Pre-fill content** in the new ADR file:
      - Title (H1): derived from the slug (replace hyphens with spaces, title-case)
      - Status: `Proposed`
      - Context section: content from the **Justification** column of the first matched row
      - Decision section: content from the **Choice** column of the first matched row
   f. **Update index**: append a new row to the ADR index table in `docs/adr/README.md`:
      `| [NNN] | [Title] | Proposed | [YYYY-MM-DD] | [brief one-line context] |`
   g. **Artifacts**: add `docs/adr/<slug>.md` to the artifacts list.

---

## Examples of well-documented decisions

### Well documented
```markdown
| Input validation | Zod at controller layer | Class-validator, manual |
The project already uses Zod for DB schemas (Drizzle).
Maintaining consistency avoids two validation systems. |
````

### Poorly documented

```markdown
| Validation | Zod | others | It's better |
```

---

## Useful ASCII diagrams

```
# Authentication flow
Client → POST /auth/login
            ↓
        AuthController
            ↓
        AuthService.validateCredentials()
            ↓
        UserRepository.findByEmail()
            ↓
        bcrypt.compare(password, hash)
            ↓ (success)
        JwtService.sign(payload)
            ↓
        Response { token, refreshToken }

# Module structure
auth/
├── auth.module.ts
├── auth.controller.ts
├── auth.service.ts
├── strategies/
│   ├── jwt.strategy.ts
│   └── local.strategy.ts
└── dto/
    ├── login.dto.ts
    └── refresh.dto.ts
```

### Step 5 — Summary to orchestrator

I return a clear executive summary to the orchestrator with all artifacts produced (design.md and any ADR file created in Step 4).

---

## Output to Orchestrator

```json
{
  "status": "ok|warning|blocked",
  "summary": "Design for [change-name]: [N] affected files, approach [brief description], risk [level].",
  "artifacts": ["engram:sdd/{change-name}/design"],
  "next_recommended": ["sdd-tasks (requires spec + design completed)"],
  "risks": ["[technical risk if found]"]
}
```

---

## Rules

- ALWAYS read real code before designing — never assume the structure
- Every decision MUST have justification (the "why", not just the "what")
- Follow existing project patterns unless the change explicitly corrects them
- The file matrix must be concrete (real paths, not "some auth file")
- ASCII diagrams are preferable to long descriptions
- If I detect that the proposal is incompatible with the current architecture, I report it as a blocker
- I do NOT write implementation code — that is `sdd-apply`
