---
name: sdd-status
description: >
  Shows the status of all active SDD changes and orchestrator state. Uses engram for persistence.
  Trigger: /sdd-status, show active changes, what changes are in progress, SDD status, orchestrator status.
format: procedural
model: haiku
---

# sdd-status

> Shows the status of all active SDD changes and orchestrator configuration.

**Triggers**: `/sdd-status`, SDD status, active changes, show open changes, what changes are in progress, orchestrator status

---

## Process

### Step 0 — Detect persistence mode

Follow `skills/_shared/persistence-contract.md` **Mode Detection for Standalone Skills**:
1. Check Engram MCP reachability → if reachable: `engram`, else `none`

### Step 1 — Locate active changes

**engram mode**: Search engram for active SDD state artifacts:
```
mem_search(query: "sdd/", project: "{project}") → list all SDD-related observations
```
Filter for artifacts that do NOT have an `archive-report` topic_key (those are completed).

**none mode**: Report "No persistence configured — cannot show change status."

Stop here if no changes found.

---

### Step 2 — Classify and group changes

For each active change found in engram, check which artifact types exist:

- `explore` → marks explore phase done
- `proposal` → marks propose phase done
- `spec` → marks spec phase done
- `design` → marks design phase done
- `tasks` → marks tasks phase done
- `verify-report` → marks verify phase done

**Infer phase label for each change:**

| Condition                                                 | Phase Label                         |
| --------------------------------------------------------- | ----------------------------------- |
| No artifacts at all                                       | not started                         |
| only explore (no proposal)                                | explore only — awaiting proposal    |
| proposal present, spec and design absent                  | propose done — awaiting spec/design |
| proposal + spec + design present, tasks absent            | spec+design done — awaiting tasks   |
| tasks present, verify-report absent                       | tasks done — ready for apply/verify |
| verify-report present                                     | verify done — ready to archive      |

**Group changes by action bucket:**

```
READY TO ARCHIVE    : verify-report present
AWAITING SPEC/DESIGN: proposal present, tasks absent, (spec or design absent)
AWAITING APPLY      : tasks present, verify-report absent
EXPLORE ONLY        : only explore, no proposal
```

---

### Step 3 — Render output

Output format (grouped, no redundancy):

```
Active SDD Changes

-- Ready to Archive --
  [change-name]   explore ok  proposal ok  spec ok  design ok  tasks ok  verify ok

-- Awaiting Apply/Verify --
  [change-name]   explore ok  proposal ok  spec ok  design ok  tasks ok  verify -

-- Awaiting Spec/Design --
  [change-name]   explore -  proposal ok  spec -  design -  tasks -  verify -

-- Explore Only (no proposal yet) --
  [change-name]   explore ok  proposal -

Next actions:
  - [N] ready to archive → /sdd-archive <name>
  - [N] awaiting spec/design → /sdd-spec <name> + /sdd-design <name>
```

Rules for this format:
- Each group header is shown only if the group has at least one entry
- Use `ok` for present, `-` for absent
- "Next actions" section is omitted if all groups are empty
- Do NOT repeat each change's phase in a separate list — the group it belongs to IS its phase

---

### Step 4 — Orchestrator state

Read the project's `CLAUDE.md` and report:
- Persistence mode: engram / none
- Skills registry count (from `## Skills` section)
- Configuration source path

Include this as a header section BEFORE the active changes output:

```
Orchestrator
  Mode: [engram|none]
  Skills: [N] registered
  Config: [path to CLAUDE.md]
```

---

## Rules

- Read-only: I only inspect engram — no mutations
- I never modify any files in this phase
- If no engram artifacts found, I report gracefully and suggest `/sdd-explore <topic>` or `/sdd-propose <change-name>`
