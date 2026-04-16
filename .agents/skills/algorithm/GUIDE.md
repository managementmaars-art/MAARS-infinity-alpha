# Algorithm Tools Guide

Executable tools for ISC (Ideal State Criteria) tracking and effort classification. These complement your existing markdown workflows with programmatic management.

---

## Quick Reference

```bash
# Classify effort level
bun run ~/.claude/skills/Algorithm/Tools/EffortClassifier.ts -r "your request"

# Manage ISC tables
bun run ~/.claude/skills/Algorithm/Tools/ISCManager.ts <command> [options]
```

---

## 1. Effort Classification

Before starting work, classify the effort level to determine appropriate depth.

### Basic Usage

```bash
# Classify a request
bun run EffortClassifier.ts -r "Add authentication to the API"
```

Output:
```
EFFORT: THOROUGH
CONFIDENCE: 80%
REASONING: High complexity score (6): authentication, api
MIN ISC ROWS: 10
SUGGESTED MODEL: sonnet
SUGGESTED TRAITS: thorough, meticulous
```

### Effort Levels

| Level | When to Use | ISC Depth | Model |
|-------|-------------|-----------|-------|
| **TRIVIAL** | Greetings, acknowledgments | Skip ISC | none |
| **QUICK** | Single-step, obvious fix | 2-3 rows | haiku |
| **STANDARD** | Multi-step, bounded scope | 5+ rows | sonnet |
| **THOROUGH** | Complex, multi-file, architectural | 10+ rows | sonnet |
| **DETERMINED** | "Until done", unlimited iteration | 20+ rows | opus |

### Override Effort

Force a specific level when auto-classification is wrong:

```bash
# CLI override
bun run EffortClassifier.ts -r "simple task" --override DETERMINED

# Inline override (in your request)
"algorithm effort THOROUGH: create the feature"
```

### JSON Output

For programmatic use:

```bash
bun run EffortClassifier.ts -r "Add dark mode" -o json
```

---

## 2. ISC Manager

Track Ideal State Criteria as work progresses through the Algorithm phases.

### Workflow Overview

```
1. CREATE   → Start new ISC for a task
2. ADD      → Define success criteria (rows)
3. PHASE    → Track Algorithm phase transitions
4. CLAIM    → Agents claim rows for parallel work
5. UPDATE   → Mark rows as ACTIVE → DONE
6. VERIFY   → Confirm each criterion passes
7. CLEAR    → Archive when complete
```

### Create ISC

```bash
bun run ISCManager.ts create -r "Add dark mode support" -e STANDARD
```

Output:
```
ISC created for: Add dark mode support
Effort: STANDARD
Saved to: ~/.claude/MEMORY/Work/current-isc.json
```

### Add Rows

Each row represents one success criterion. Always pair with verification method.

```bash
# With verification (recommended)
bun run ISCManager.ts add \
  -d "Theme toggle component exists" \
  -s EXPLICIT \
  --verify-method browser \
  --verify-criteria "Toggle visible in settings page"

# Without verification (legacy)
bun run ISCManager.ts add -d "Uses TypeScript" -s INFERRED
```

#### Source Types

| Source | Meaning | Example |
|--------|---------|---------|
| `EXPLICIT` | User directly stated this | "I want a toggle button" |
| `INFERRED` | Derived from context | User's codebase uses TypeScript |
| `IMPLICIT` | Industry standard/best practice | "Tests should pass" |
| `RESEARCH` | Discovered during research | "Library X is better than Y" |

#### Verification Methods

| Method | When to Use |
|--------|-------------|
| `browser` | Visual/UI verification |
| `test` | Automated test suite |
| `grep` | Code pattern search |
| `api` | API endpoint testing |
| `lint` | Linting/type checking |
| `manual` | Human inspection required |
| `agent` | Another agent verifies |
| `inferred` | Success implied by other rows |

### View ISC

```bash
# Formatted table
bun run ISCManager.ts show

# JSON format
bun run ISCManager.ts show -o json

# Evolution log
bun run ISCManager.ts log

# Status summary
bun run ISCManager.ts summary
```

Example output:
```
## 🎯 IDEAL STATE CRITERIA

**Request:** Add dark mode support
**Effort:** STANDARD | **Phase:** EXECUTE | **Iteration:** 1

| # | What Ideal Looks Like | Source | Capability | Verify | Status |
|---|----------------------|--------|------------|--------|--------|
| 1 | Theme toggle exists | EXPLICIT | 🤖 engineer | 🌐 browser | ✅ DONE |
| 2 | Theme persists | INFERRED | 🤖 engineer | 🧪 test | 🔄 ACTIVE |
| 3 | All components themed | IMPLICIT | — | 👁️ manual | ⏳ PENDING |
```

### Update Status

```bash
# Mark as active (working on it)
bun run ISCManager.ts update --row 1 --status ACTIVE

# Mark as done
bun run ISCManager.ts update --row 1 --status DONE

# Mark as blocked with reason
bun run ISCManager.ts update --row 1 --status BLOCKED --reason "Waiting on API"

# Mark as adjusted (scope changed)
bun run ISCManager.ts update --row 1 --status ADJUSTED --reason "Using CSS vars instead"
```

### Set Capability

Assign which capability/agent handles a row:

```bash
bun run ISCManager.ts capability --row 1 -c execution.engineer
bun run ISCManager.ts capability --row 2 -c research.perplexity
bun run ISCManager.ts capability --row 3 -c thinking.deep_thinking
```

### Verify Results

After execution, record verification results:

```bash
# Passed
bun run ISCManager.ts verify --row 1 --result PASS

# Failed and adjusted
bun run ISCManager.ts verify --row 2 --result ADJUSTED --reason "Changed approach"

# Blocked
bun run ISCManager.ts verify --row 3 --result BLOCKED --reason "Dependency missing"
```

### Phase Transitions

Track Algorithm phase progression:

```bash
bun run ISCManager.ts phase -p THINK
bun run ISCManager.ts phase -p PLAN
bun run ISCManager.ts phase -p BUILD
bun run ISCManager.ts phase -p EXECUTE
bun run ISCManager.ts phase -p VERIFY
bun run ISCManager.ts phase -p LEARN
```

### Iteration

When cycling back through phases:

```bash
bun run ISCManager.ts iterate
# Now on iteration: 2
```

---

## 3. Advanced Features

### Agent Claims (Parallel Work)

For multi-agent execution, agents claim rows before working:

```bash
# Claim a row
bun run ISCManager.ts claim --row 1 --agent Engineer

# Release a claim
bun run ISCManager.ts release --row 1

# See available (unclaimed) rows
bun run ISCManager.ts available
```

Claims auto-expire after 30 minutes if not completed.

### Research Override

When research contradicts a planned approach:

```bash
# Block a row with research finding
bun run ISCManager.ts research-block \
  --row 2 \
  --reason "Use Zustand instead of Redux" \
  -s research.perplexity

# User acknowledges and overrides (proceed anyway)
bun run ISCManager.ts acknowledge --row 2 --action OVERRIDE

# User accepts research (will change approach)
bun run ISCManager.ts acknowledge --row 2 --action ACCEPT
```

### Nested ISC

For complex rows that need their own Algorithm execution:

```bash
# Mark row as nested (spawns child ISC)
bun run ISCManager.ts nest --row 5

# Update child progress
bun run ISCManager.ts child-status --row 5 --child-status IN_PROGRESS
bun run ISCManager.ts child-status --row 5 --child-status COMPLETE
```

### Interview Protocol

When a request is unclear, use interview questions:

```bash
bun run ISCManager.ts interview -r "Make it better"
```

Output:
```
═══════════════════════════════════════════════════════════
  INTERVIEW PROTOCOL - Clarify Ideal State
═══════════════════════════════════════════════════════════

Request: "Make it better"

When ideal state is unclear, ask these questions:

  1. What does success look like when this is done?
  2. Who will use this and what will they do with it?
  3. What would make you show this to your friends?
  4. What existing thing is this most similar to?
  5. What should this definitely NOT do?

───────────────────────────────────────────────────────────
Use answers to create clear, testable ISC rows.
═══════════════════════════════════════════════════════════
```

### Clear/Archive

When finished:

```bash
bun run ISCManager.ts clear
# Archived to: ~/.claude/MEMORY/Work/archive-1769250500568.json
# Current ISC cleared.
```

---

## 4. Capabilities Registry

The `Data/Capabilities.yaml` file defines what's available at each effort level.

### Effort Unlocks

| Effort | Unlocked Capabilities |
|--------|----------------------|
| TRIVIAL | Nothing (skip Algorithm) |
| QUICK | haiku, intern, ralph_loop |
| STANDARD | + sonnet, deep_thinking, research, engineer, qa_tester, verification |
| THOROUGH | + tree_of_thought, plan_mode, council debate |
| DETERMINED | + opus, all capabilities |

### Capability Categories

```yaml
models:        # haiku, sonnet, opus
thinking:      # deep_thinking, tree_of_thought, plan_mode
debate:        # council
analysis:      # first_principles
research:      # perplexity, claude
execution:     # intern, engineer, qa_tester, ralph_loop
verification:  # browser, skeptical_verifier
```

---

## 5. Integration Examples

### Full Workflow Example

```bash
# 1. Classify effort
bun run EffortClassifier.ts -r "Add user authentication"
# → THOROUGH

# 2. Create ISC
bun run ISCManager.ts create -r "Add user authentication" -e THOROUGH

# 3. Add criteria
bun run ISCManager.ts add -d "Login form exists" -s EXPLICIT \
  --verify-method browser --verify-criteria "Form renders at /login"
bun run ISCManager.ts add -d "JWT tokens issued" -s EXPLICIT \
  --verify-method api --verify-criteria "POST /auth returns token"
bun run ISCManager.ts add -d "Protected routes redirect" -s INFERRED \
  --verify-method browser --verify-criteria "Unauthenticated user redirected"
bun run ISCManager.ts add -d "Tests pass" -s IMPLICIT \
  --verify-method test --verify-criteria "bun test exits 0"

# 4. Assign capabilities
bun run ISCManager.ts capability --row 1 -c execution.engineer
bun run ISCManager.ts capability --row 2 -c execution.engineer
bun run ISCManager.ts capability --row 3 -c execution.engineer
bun run ISCManager.ts capability --row 4 -c execution.qa_tester

# 5. Track progress
bun run ISCManager.ts phase -p EXECUTE
bun run ISCManager.ts update --row 1 --status ACTIVE
# ... do work ...
bun run ISCManager.ts update --row 1 --status DONE
bun run ISCManager.ts verify --row 1 --result PASS

# 6. View progress
bun run ISCManager.ts show
bun run ISCManager.ts summary

# 7. Complete
bun run ISCManager.ts phase -p LEARN
bun run ISCManager.ts clear
```

### Using with Existing Workflows

These tools complement your existing markdown workflows:

| Existing Workflow | New Tool | Relationship |
|-------------------|----------|--------------|
| `Isctable.md` | `ISCManager.ts` | Template → Executable |
| `Executealgorithm.md` | `EffortClassifier.ts` | Manual → Automated |
| `Phasechecklist.md` | `phase` command | Reference → Tracking |

Use the tools for programmatic tracking while referencing the workflows for conceptual guidance.

---

## 6. File Locations

```
~/.claude/skills/Algorithm/
├── SKILL.md                    # Core Algorithm documentation
├── GUIDE.md                    # This file
├── Tools/
│   ├── ISCManager.ts          # ISC lifecycle management
│   └── EffortClassifier.ts    # Effort classification
├── Data/
│   └── Capabilities.yaml      # Capability registry
└── workflows/
    ├── Isctable.md            # ISC template reference
    ├── Executealgorithm.md    # Full execution template
    └── Phasechecklist.md      # Phase checklist

~/.claude/MEMORY/Work/
├── current-isc.json           # Active ISC table
└── archive-*.json             # Completed ISCs
```

---

## 7. Troubleshooting

### "No current ISC"
Run `create` first before other commands.

### Row not found
Use `show` to see current row IDs.

### Claim rejected
Row may be already claimed or not PENDING. Use `available` to see claimable rows.

### Stale claim
Claims expire after 30 minutes. The next claim attempt will override.
