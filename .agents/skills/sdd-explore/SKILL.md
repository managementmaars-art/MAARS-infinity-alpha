---
name: sdd-explore
description: >
  Investigates and analyzes an idea or codebase area before committing to changes. Pure research, no writes.
  Trigger: /sdd-explore <topic>, explore, investigate codebase, research feature, analyze before changing.
format: procedural
model: sonnet
metadata:
  version: "3.0"
---

# sdd-explore

> Investigates and analyzes an idea or area of the codebase before committing to changes.

**Triggers**: `/sdd-explore <topic>`, explore, investigate codebase, analyze before changing, research feature

---

## Purpose

The exploration phase is **optional but valuable**. Its goal is to understand the terrain before proposing changes. It creates no code and modifies nothing. It only reads and analyzes.

Use it when:

- The request is vague or complex
- You are unsure of the scope of the change
- You want to understand the impact before committing
- There are multiple possible approaches

---

## Process

### Skill Resolution

When the orchestrator launches this sub-agent, it resolves the skill path using:

```
1. .claude/skills/sdd-explore/SKILL.md     (project-local — highest priority)
2. ~/.claude/skills/sdd-explore/SKILL.md   (global catalog — fallback)
```

Project-local skills override the global catalog. See `docs/SKILL-RESOLUTION.md` for the full algorithm.

---

### Step 0 — Load project context + Spec context preload

Follow `skills/_shared/sdd-phase-common.md` **Section F** (Project Context Load) and **Section G** (Spec Context Preload). Both are non-blocking.

### Step 0 sub-step — Handoff context preload

This sub-step is **non-blocking**: any failure (missing file, unreadable file, no slug) MUST produce
at most an INFO-level note. This sub-step MUST NOT produce `status: blocked` or `status: failed`.

1. Resolve the change slug from the invocation context.
2. Check whether a proposal already exists in engram: `mem_search(query: "sdd/<slug>/proposal")`.
3. If absent: skip silently — log `INFO: no pre-seeded proposal found — proceeding without handoff context.`
4. If present: retrieve via `mem_get_observation(id)`. Treat its content as **supplemental intent enrichment**:
   - It informs what the explore should prioritize, not what the codebase shows.
   - It MUST NOT override live codebase findings.
   - Log: `Handoff context loaded from engram: sdd/<slug>/proposal`
5. When loaded, include a `## Handoff Context` section in the exploration output
   (placed before `## Current State`) summarizing:
   - Decision that triggered the change
   - Goal and success criteria from the seeded proposal
   - Explore targets listed in the proposal
   - Constraints ("do not do" items)

---

### Step 1 — Understand the request

I classify what type of exploration is needed:

- **New feature**: What already exists? Where would it fit?
- **Bug**: Where is the problem? What is the root cause?
- **Refactor**: What code is affected? What are the risks?
- **Integration**: What exists to connect? What is missing?

### Step 2 — Branch Diff scan

This step is **non-blocking**: any failure (git unavailable, no working tree, empty diff) MUST produce at most an INFO-level note. This step MUST NOT produce `status: blocked` or `status: failed`.

1. Run `git status --short` to identify modified, staged, and untracked files in the current working tree.
2. Filter results to files relevant to the domain being explored (match by path prefix, filename, or keyword overlap with the change name).
3. Classify each file as: `modified`, `staged`, `deleted`, or `untracked`.
4. Write output to the `## Branch Diff` section.

**If git is unavailable or diff is empty**: log `INFO: branch diff unavailable or empty — skipping Branch Diff section` and include an empty `## Branch Diff` section with that note.

**Output format:**
```
## Branch Diff

Files modified in current branch relevant to this change:
- path/to/file.ts (modified)
- path/to/other.ts (staged, pending deletion)
- path/to/new-file.ts (untracked)
```

### Step 3 — Prior Attempts archive scan

This step is **non-blocking**: any failure MUST produce at most an INFO-level note.

Search engram for prior archived changes related to this topic:
```
mem_search(query: "sdd/archive-report", project: "{project}")
```

Filter results by keyword overlap with the current change slug. For each related result, retrieve via `mem_get_observation(id)` to check outcome.

Write output to the `## Prior Attempts` section.

**Output format:**
```
## Prior Attempts

Prior archived changes related to this topic:
- auth-flow-v1: COMPLETED
- auth-flow-v2: ABANDONED

[or: "No prior attempts found."]
```

### Step 4 — Contradiction Analysis

This step is **non-blocking**: contradictions are informational and MUST NOT cause `status: blocked` or `status: failed`. At most, contradictions may cause `status: warning`.

1. Compare the user's stated intent (from change description and any pre-seeded proposal) against:
   - Loaded feature files from Step 0 (behavioral contracts)
   - Prior attempt outcomes from Step 3
   - `ai-context/` files
2. For each potential contradiction detected, classify severity:
   - **CERTAIN**: the user says "remove X" AND a loaded spec explicitly states "X MUST exist" — no ambiguity
   - **UNCERTAIN**: the user intent implies removing or changing X, but there is no explicit spec contract — ambiguous
3. Assign impact level: `INFO` (minimal), `WARNING` (notable), `CRITICAL` (breaking)
4. Write output to the `## Contradiction Analysis` section.
5. Do NOT block exploration — the status remains `ok` unless contradictions are severe enough to set `status: warning`.

**Output format:**
```
## Contradiction Analysis

Contradictions detected between user intent and existing context:

- Item: [feature or behavior name]
  Status: CERTAIN|UNCERTAIN — [explanation of what contradicts what]
  Severity: INFO|WARNING|CRITICAL
  Resolution: [suggested resolution or "Requires user confirmation"]

[or: "No contradictions detected."]
```

### Step 5 — Investigate the codebase

I read real code following this hierarchy:

1. Entry points of the affected area
2. Files related to the functionality
3. Existing tests (they reveal expected behavior)
4. Relevant configurations
5. `ai-context/architecture.md` if it exists (to understand past decisions)

### Step 6 — Analyze approaches

For each possible approach I generate a comparison table:

| Approach   | Pros | Cons | Effort          | Risk            |
| ---------- | ---- | ---- | --------------- | --------------- |
| [Option A] |      |      | Low/Medium/High | Low/Medium/High |
| [Option B] |      |      |                 |                 |

### Step 7 — Identify risks and dependencies

- Code that would break with the change
- Dependencies that would need to be updated
- Tests that would fail
- Non-obvious side effects

### Step 8 — Save if a change name was specified

**Pre-save naming check (non-blocking):**

If `<change-name>` starts with `explore-`, warn before writing:

```
Note: The change name "[change-name]" starts with "explore-".
Standalone explore folders (e.g. explore-fy-topic) are not part of a full SDD planning cycle
and will not be automatically cleaned up or archived.

If you intend this as a full SDD change, use a descriptive slug and continue with /sdd-propose:
  /sdd-propose <description>   <- starts the planning cycle from proposal

If you intend this as a one-off investigation, proceed as-is.
```

This warning is informational only — writing proceeds regardless of the name.

If invoked as `/sdd-explore <change-name>`, I persist the exploration artifact.

**Write:** Call `mem_save` with `topic_key: sdd/{change-name}/explore`, `type: architecture`, `project: {project}`, content = full exploration markdown. Do NOT write any file.
  - If no change name provided: log `INFO: no change name — skipping artifact persistence` and skip.
  - If Engram MCP is not reachable: skip persistence. Return exploration content inline only.

**Persisted artifact** (compact — only what downstream phases consume):

```markdown
# Exploration: [topic]

## Current State
[2-3 sentence summary of what currently exists in the codebase]

## Branch Diff
- [path/to/file] (modified|staged|deleted|untracked)
[or: "No relevant changes in current branch."]

## Prior Attempts
- [slug]: [outcome]
[or: "None found."]

## Contradiction Analysis
- [Item]: [CERTAIN|UNCERTAIN] — [one-line explanation]
[or: "No contradictions detected."]

## Recommendation
[Recommended approach in 1-2 sentences]

## Ready for Proposal
[Yes/No — and why if No]
```

**Conversational output** (shown to user but NOT persisted):

The full analysis — including Affected Areas table, Analyzed Approaches with pros/cons/effort/risk, Identified Risks with mitigations, Open Questions, and Handoff Context — is presented in the conversational response to the orchestrator. This content is ephemeral and does not need to survive across sessions.

---

## Output to Orchestrator

```json
{
  "status": "ok|warning|blocked",
  "summary": "Analysis of [topic]: [2-3 lines of the main finding]",
  "artifacts": ["engram:sdd/{change-name}/explore"],
  "next_recommended": ["sdd-propose"],
  "risks": ["[risk if found]"]
}
```

---

## Rules

- I ONLY read code — I never modify anything in this phase
- I read real code, never assume or invent
- If I find something unexpected (technical debt, inconsistencies), I report it
- I keep the analysis concise: the goal is to inform, not to write a thesis
- If the exploration reveals that the change is trivial, I say so clearly
