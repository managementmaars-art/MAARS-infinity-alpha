---
name: sdd-spec
description: >
  Writes delta specifications with requirements and Given/When/Then scenarios for a change.
  Trigger: /sdd-spec <change-name>, write specs, functional requirements, specification phase.
format: procedural
model: sonnet
metadata:
  version: "3.0"
---

# sdd-spec

> Writes delta specifications with requirements and Given/When/Then scenarios.

**Triggers**: `/sdd-spec <change-name>`, write specs, specifications, functional requirements, sdd spec

---

## Purpose

Specs define **WHAT the system must do** from the perspective of observable behavior. They do not say how to implement it. They are the source of truth for verification.

**Key concept — Delta Specs:**
Specs are deltas (changes) on top of what already exists, not full replacements.

- If there is no existing spec: I write a complete spec
- If a spec already exists: I write ADDED/MODIFIED/REMOVED sections

---

## Process

### Skill Resolution

When the orchestrator launches this sub-agent, it resolves the skill path using:

```
1. .claude/skills/sdd-spec/SKILL.md     (project-local — highest priority)
2. ~/.claude/skills/sdd-spec/SKILL.md   (global catalog — fallback)
```

Project-local skills override the global catalog. See `docs/SKILL-RESOLUTION.md` for the full algorithm.

---

### Step 0a — Load project context

Follow `skills/_shared/sdd-phase-common.md` **Section F** (Project Context Load). Non-blocking.

### Step 0b — Domain context preload

After loading project context and before identifying affected domains, I perform an optional, non-blocking domain context preload:

1. **List candidates**: List all `.md` files in `ai-context/features/`, excluding `_template.md` and any file whose name begins with an underscore. If the directory is absent, skip this step silently.
2. **Apply the filename-stem matching heuristic**:
   - Split the change slug on hyphens to produce stems; discard any single-character stems.
   - For each candidate file, compute its domain slug (filename without `.md` extension).
   - A match occurs when: the domain slug appears in the change name, OR any change-name stem appears in the domain slug (case-insensitive comparison).
3. **Load matches**: If one or more files match, read each file and inject its content as enrichment context before writing the spec. If no file matches, skip silently — do NOT produce an error or warning.
4. **Multiple matches**: If more than one file matches, load all matching files.
5. **Non-blocking contract**: This step MUST NEVER produce `status: blocked` or `status: failed`. Any file read error is treated as a miss (skip silently).
6. **Enrichment note**: Feature file content is treated as enrichment context — it surfaces business rules, invariants, and known gotchas that should inform the spec's requirements and THEN clauses. Both feature files and any existing domain specs MUST be read when both are present.
7. **Orchestrator reporting**: When one or more feature files are loaded, the `summary` field MUST note that domain context was preloaded (e.g., "domain context loaded from ai-context/features/auth.md"). Each loaded file path MUST appear in the `artifacts` list (read, not written).

### Step 0c — Spec context preload

Follow `skills/_shared/sdd-phase-common.md` **Section G** (Spec Context Preload). Non-blocking.

---

### Step 1 — Read prior artifacts

I must read:

- The proposal artifact (the WHAT and WHY):
  - `mem_search(query: "sdd/{change-name}/proposal")` → `mem_get_observation(id)` for full content.
  - If not found and Engram not reachable: proposal content passed inline from orchestrator.
- `ai-context/architecture.md` if it exists (to understand the current system)

#### Step 1 extended — Validate against Supersedes section

After reading the proposal, I perform a Supersedes cross-check before writing any spec:

1. **Check for Supersedes section**: look for `## Supersedes` in the proposal.
   - **If absent** (older archived change): log `WARNING: proposal has no Supersedes section — backwards compat mode; skipping validation` and proceed without validation.
   - **If present and states "None — purely additive"**: skip validation; proceed to Step 2.
   - **If present with REMOVED or REPLACED items**: proceed to step 2 below.

2. **For each REMOVED item in Supersedes**: scan the delta spec I am about to write for any requirement that says "preserve X", "X MUST remain", or "backward compatibility with X". If found:
   - Emit `MUST_RESOLVE` warning: "Spec includes a preservation requirement for '[X]' but proposal says '[X]' is REMOVED. Confirm intent."
   - Pause for user confirmation before continuing.

3. **For each REPLACED item in Supersedes**: verify the spec describes the new replacement, not the old behavior. If spec only describes old behavior without acknowledging replacement, add a note: `[PENDING: spec does not describe replacement behavior for [X] — clarify with design]`.

4. **For CONTRADICTED items**: verify the spec aligns with the resolution documented in `## Contradiction Resolution` of the proposal. If mismatch, emit `MUST_RESOLVE` warning.

### Step 2 — Identify affected domains

From the proposal I extract the domains that need specs:

- One domain = one coherent functional area (auth, payments, users, notifications, etc.)
- Each domain has its own spec file

### Step 3 — Write delta specs

For each affected domain, I persist the delta spec to engram:

Call `mem_save` with `topic_key: sdd/{change-name}/spec`, `type: architecture`, `project: {project}`, content = all domain specs concatenated (separated by `---`). Do NOT write any file.

If Engram MCP is not reachable: skip persistence. Return spec content inline only.

Content format:

#### If NO existing spec — Full spec:

```markdown
# Spec: [Domain]

Change: [change-name]
Date: [YYYY-MM-DD]

## Requirements

### Requirement: [Descriptive name]

[Description using RFC 2119 keywords]

#### Scenario: [Case name]

- **GIVEN** [precondition — system state]
- **WHEN** [action — what happens]
- **THEN** [observable result — what must happen]
- **AND** [additional result if applicable]

#### Scenario: [Edge case]

- **GIVEN** [...]
- **WHEN** [...]
- **THEN** [...]
```

#### If spec ALREADY EXISTS — Delta:

```markdown
# Delta Spec: [Domain]

Change: [change-name]
Date: [YYYY-MM-DD]

## ADDED — New requirements

### Requirement: [Name]

[Description]

#### Scenario: [Name]

- **GIVEN** [...]
- **WHEN** [...]
- **THEN** [...]

## MODIFIED — Modified requirements

### Requirement: [Name of existing requirement]

[New description]
_(Before: [previous description])_

#### Scenario: [Name] _(modified)_

- **GIVEN** [...]
- **WHEN** [...]
- **THEN** [...]

## REMOVED — Removed requirements

### Requirement: [Name]

_(Reason: [why it is being removed])_
```

### RFC 2119 Keywords (required)

| Keyword      | Meaning                                             |
| ------------ | --------------------------------------------------- |
| **MUST**     | Absolute requirement                                |
| **MUST NOT** | Absolute prohibition                                |
| **SHOULD**   | Recommended (exceptions allowed with justification) |
| **MAY**      | Optional                                            |

### Types of scenarios to cover

For each requirement I include:

1. **Happy path**: The normal, successful flow
2. **Edge cases**: Extreme values, empty lists, maximums
3. **Error cases**: What happens when something fails
4. **Security cases**: If applicable (authentication, authorization, permissions)

---

## Examples of well-written scenarios

### Well written

```
#### Scenario: Successful login with valid credentials
- GIVEN that the user exists with email "user@example.com" and the correct password
- WHEN they send POST /auth/login with those credentials
- THEN they receive status 200
- AND they receive a valid JWT in the "token" field
- AND the token expires in 24 hours

#### Scenario: Failed login with incorrect password
- GIVEN that the user exists with email "user@example.com"
- WHEN they send POST /auth/login with an incorrect password
- THEN they receive status 401
- AND the error message does NOT reveal whether the email exists
```

### Poorly written (too vague)

```
#### Scenario: The user can log in
- GIVEN there is a user
- WHEN they log in
- THEN it works
```

---

## Output to Orchestrator

```json
{
  "status": "ok|warning|blocked",
  "summary": "Specs for [change-name]: [N] domains, [M] requirements, [K] scenarios.",
  "artifacts": ["engram:sdd/{change-name}/spec"],
  "next_recommended": ["sdd-tasks (after sdd-design)"],
  "risks": []
}
```

---

## Rules

- Specs describe OBSERVABLE BEHAVIOR, not implementation
- Each requirement MUST have at least 1 scenario (happy path minimum)
- Scenarios MUST be testable and verifiable
- I do NOT include implementation details (that is `sdd-design`)
- I do NOT invent behavior — I base everything on the proposal and existing code
- If something is ambiguous in the proposal, I mark it as `[Pending clarification]` and list it in risks
- I do NOT add "preserve X" or "backward compatibility with X" requirements that are NOT explicitly stated in the proposal — if the proposal is silent, treat as pending clarification, NOT as implicit preservation
- If the proposal has no Supersedes section (archived change compatibility), I skip validation and proceed without error — backwards compat mode is non-blocking
