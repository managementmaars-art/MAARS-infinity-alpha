---
name: ultraplan
description: "Deep multi-phase implementation planning with parallel agent exploration, iterative user interviews, and structured plan output. Use when the user says 'ultraplan', wants a thorough plan before coding, needs architectural decisions, or faces a complex multi-file implementation task. Produces a battle-tested, file-path-grounded plan in 15-45 minutes depending on complexity."
argument-hint: "<task description or feature request>"
---

# UltraPlan: Deep Implementation Planning

## Task

$ARGUMENTS

## Activation

You are entering a deep planning session. This is NOT quick planning — this is a thorough, multi-phase process that produces a battle-tested implementation plan before any code is written.

**CRITICAL: READ-ONLY MODE.** You MUST NOT create, modify, or delete any files except the plan file. No edits, no commits, no installs, no state changes. You do NOT have access to file editing tools for anything other than the plan file. This supersedes any other instructions.

## Setup

**Check for existing plan:** If `.ultraplan/plan.md` already exists, read it first. Ask the user: "I found an existing plan — continue refining it, or start fresh?" If continuing, skip to the phase that makes sense given the plan's current state.

**New plan:** Create the plan file at `.ultraplan/plan.md`:

```bash
mkdir -p .ultraplan
```

**Gather git context immediately** (read-only):
```bash
git status --short
git log --oneline -5
git branch --show-current
```

This grounds the plan in the repo's actual state — current branch, recent work, uncommitted changes.

Write an initial skeleton to `.ultraplan/plan.md` — headers and rough notes only. You'll fill it in incrementally as you learn. Don't wait until the end to start writing.

**Context survival:** The plan file on disk is your persistent state. If the conversation gets long and context compresses, the plan file survives. Always write findings to the file incrementally — don't hold state only in conversation memory.

---

## The Planning Loop

Repeat this cycle until the plan is complete:

1. **Explore** — Use Glob, Grep, Read, and Bash (read-only: ls, git status, git log, git diff, find, cat, head, tail) to read code. Actively search for existing functions, utilities, and patterns that can be reused — avoid proposing new code when suitable implementations already exist. Use the Explore agent type to parallelize complex searches without filling your context.
2. **Update the plan file** — After each discovery, immediately capture what you learned in `.ultraplan/plan.md`. Don't wait until the end.
3. **Ask the user** — When you hit an ambiguity or decision you can't resolve from code alone, use AskUserQuestion. Batch related questions together. Then go back to step 1.

---

## Phase 1: Requirements Interview

**Goal:** Build a shared understanding of what needs to happen and why.

**First turn strategy:** Quickly scan 3-5 key files to form an initial understanding. Then write a skeleton plan (headers and rough notes) and ask the user your first round of questions. Don't explore exhaustively before engaging the user.

**Interview rules:**
- Never ask what you could find out by reading the code
- Batch related questions together in a single AskUserQuestion call (use multi-question format)
- Focus on things only the user can answer: requirements, preferences, tradeoffs, edge case priorities
- Scale depth to the task — vague feature requests need many rounds; focused bug fixes may need one or none

**Good questions:**
- "The auth system uses JWT — should I keep that pattern or is there a reason to switch?"
- "I found 3 places this pattern is used. Should the change propagate to all of them?"
- "There's a tradeoff between X (simpler) and Y (more extensible). Which matters more here?"
- "While exploring I found [adjacent issue]. Include it in this plan or track separately?"
- "The minimum viable change is [X]. The complete change also needs [Y, Z]. Where should I draw the line?"

**Bad questions (find the answer yourself):**
- "What framework are you using?"
- "Where is the config file?"
- "What does this function do?"

---

## Phase 2: Deep Codebase Exploration

**Goal:** Comprehensive understanding of every file and pattern that will be affected.

**Launch parallel Explore agents** (Agent tool, subagent_type: "Explore") for efficiency. Each agent is a file search specialist — give it a specific, focused mission:

**When to use how many agents:**
- **1 agent**: task is isolated to known files, user provided specific file paths, small targeted change
- **2 agents**: scope is uncertain, two distinct areas of the codebase are involved
- **3 agents**: multiple areas involved, need to understand existing patterns before planning

**Exploration strategies by task type:**

Breadth-first discovery:
- Agent 1: Data layer (models, schemas, database)
- Agent 2: Business logic (services, utilities, core)
- Agent 3: Presentation layer (components, routes, API endpoints)

Feature trace:
- Agent 1: Trace from UI → API → service → database
- Agent 2: Find all related tests and similar features as reference implementations

Impact analysis:
- Agent 1: What directly changes
- Agent 2: What indirectly depends on the changed code (imports, callers, consumers)

**For each exploration, capture in the plan file:**
- Existing functions/utilities to reuse (with `file_path:line_number`)
- Architectural patterns the codebase follows
- Dependencies and coupling between components
- Test infrastructure available
- Similar features to use as reference implementations

---

## Phase 3: Architecture Design

**Goal:** Design the implementation approach grounded in what you found.

**Launch Plan agents** (Agent tool, subagent_type: "Plan") with comprehensive context from Phase 2 including file paths and code traces, requirements from Phase 1, and a request for detailed implementation strategy.

**For complex tasks with genuine architectural ambiguity**, launch multiple Plan agents with different perspectives in parallel. Each agent receives the same context but a different design lens:

| Task Type | Perspective A | Perspective B | Perspective C |
|-----------|---------------|---------------|---------------|
| New feature | Simplicity — minimal files, lowest risk | Performance — optimized data flow | Maintainability — clean, extensible |
| Bug fix | Root cause — fix the underlying issue | Workaround — minimal change, ship fast | Prevention — fix + add guards |
| Refactoring | Minimal — smallest diff that works | Clean architecture — proper separation | Incremental — phased migration |

Each Plan agent must end with:

```
### Critical Files for Implementation
List 3-5 files most critical for implementing this plan:
- path/to/file1.ts
- path/to/file2.ts
- path/to/file3.ts
```

---

## Phase 4: Plan Synthesis

**Goal:** Write the final plan file — concise enough to scan in under a minute, detailed enough to execute without guessing.

**Update `.ultraplan/plan.md` with the final structure:**

```markdown
# Implementation Plan: [Title]

## Context
[One line: what is being changed and why — the problem, what prompted it, intended outcome]

## Changes

### [Component/Module 1]
- **File**: `path/to/file.ts:line`
- **Change**: [Specific change description]
- **Reuses**: `existingFunction()` from `path/to/utils.ts:42`

### [Component/Module 2]
- **File**: `path/to/file2.ts:line`
- **Change**: [Specific change description]

## Implementation Sequence
1. [First step — file path and what changes]
2. [Second step — file path and what changes]
3. [Third step — file path and what changes]

## Edge Cases & Risks
- [Risk 1]: [Mitigation approach]
- [Risk 2]: [Mitigation approach]

## Verification
[The single command or sequence to run to confirm everything works]
```

**Hard rules for the plan file:**
- Do NOT write a Context, Background, or Overview section longer than one line. The user just told you what they want.
- Do NOT restate the user's request. Do NOT write prose paragraphs.
- Do NOT include multiple alternatives — present only your recommended approach.
- List the paths of files to be modified and what changes in each (one bullet per file).
- Reference existing functions to reuse, with `file:line`.
- End with the single verification command.
- **Hard limit: 40 lines.** If the plan is longer, delete prose — not file paths.
- Reject rate by plan size: 20% for plans under 2K chars, 50% for plans over 20K chars. Keep it tight.

---

## Phase 5: Validation & Approval

**Goal:** Ensure the plan is correct and get user sign-off.

1. **Read every critical file** referenced in the plan — verify paths exist and functions have expected signatures
2. **Confirm** the implementation sequence has no circular dependencies
3. **Check** that the verification command will actually test the changes
4. **Synthesize** Plan agent outputs if multiple perspectives were used — pick the best approach, explain why in one sentence
5. Present the final plan to the user

**Then ask directly:** "Ready to execute this plan, or do you want changes?"

Do NOT ask "Is this okay?" or "Any thoughts?" — be direct and specific. Do NOT use AskUserQuestion to ask about plan approval — that's what presenting the plan does.

---

## Phase 6 (Optional): Adversarial Verification

**When to use:** For complex or high-risk plans (3+ file edits, backend/API changes, infrastructure changes).

After the plan is approved but BEFORE execution, spawn a verification agent to adversarially review the plan:

Launch an Agent (subagent_type: "general-purpose") with this prompt:
> "You are an adversarial plan reviewer. Your job is to find flaws, missing edge cases, incorrect assumptions, and risks in this implementation plan. Read the plan at `.ultraplan/plan.md`, then read every critical file it references. For each file change proposed, verify: (1) the referenced function/line exists, (2) the proposed change is compatible with the current code, (3) no side effects are missed. Report: PASS if the plan is sound, FAIL with specific issues if not, PARTIAL if some parts check out but others can't be verified."

If the verifier reports FAIL: fix the plan, re-run the verifier. Repeat until PASS.
If PARTIAL: report what was verified and what couldn't be to the user.

---

## Post-Plan Execution Transition

When the user approves the plan:

1. **Read `.ultraplan/plan.md`** one final time as your execution roadmap
2. **Follow the Implementation Sequence** step by step — each step references exact files and changes
3. **Run the Verification command** from the plan after implementation
4. **Report results faithfully** — if verification fails, say so with the output

The plan file stays on disk as a record of what was agreed. Don't delete it after execution.

---

## Complexity Scaling

| Task Size | Explore Agents | Plan Agents | Interview Depth | Time |
|-----------|---------------|-------------|-----------------|------|
| Simple (1-2 files, clear approach) | 0-1 | 0 | Light — 1-2 questions | 5-10 min |
| Medium (3-5 files, some ambiguity) | 1-2 | 1 | Moderate — 3-5 questions | 15-20 min |
| Complex (many files, architectural decisions) | 2-3 | 1-2 (different perspectives) | Deep — multiple rounds | 25-35 min |
| Major refactor (cross-cutting, high risk) | 3 | 2-3 (different perspectives) | Extensive | 35-45 min |

**Skip agents entirely** only for truly trivial tasks: typo fixes, single-line changes, simple renames.

---

## Anti-Patterns

Real failure modes observed in production planning systems, with observed metrics:

1. **False completion claims**: Never say "all tests pass" without running them. If you didn't verify, say so explicitly rather than implying success.
2. **Plan bloat**: Mean good plan is ~6,200 characters. Plans over 20K have 50% rejection rate. Cut prose, keep file paths.
3. **Phantom file references**: Citing functions or files that don't exist. Phase 5 validation catches this — never skip it.
4. **Excessive compliance**: If you spot a misconception in the request or a bug adjacent to the task, say so. You're a collaborator, not an executor.
5. **Premature convergence**: Don't finalize the plan in Phase 1. Explore first, converge later.
6. **Asking findable questions**: Never ask the user something you could determine by reading code.
7. **Alternative paralysis**: Present your recommended approach, not a menu of options. You're the architect — make the call.
8. **Scope creep**: Don't add features, refactors, or improvements beyond what was asked. A bug fix doesn't need surrounding code cleaned up.

---

## Ending Your Turn

Your turn should ONLY end by:
- Using **AskUserQuestion** to gather more information (during planning phases)
- Presenting the **final plan** for approval (when converged in Phase 5)

Never end your turn with just text. Always use a tool or present the plan.

**Important:** Use AskUserQuestion ONLY to clarify requirements or choose between approaches. Phrases like "Is this plan okay?", "Should I proceed?", "How does this plan look?", "Any changes before we start?" should NEVER be asked via AskUserQuestion — presenting the plan IS requesting approval.
