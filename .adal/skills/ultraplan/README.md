# UltraPlan

Deep multi-phase implementation planning skill for Claude Code. Produces battle-tested, file-path-grounded implementation plans through parallel agent exploration, iterative user interviews, and structured convergence.

## What It Does

UltraPlan runs a structured planning session before any code is written. Instead of jumping into implementation, it:

1. **Interviews you** to understand requirements, preferences, and constraints
2. **Explores your codebase** in parallel using multiple specialized agents
3. **Designs an architecture** grounded in what actually exists in your code
4. **Writes a concrete plan** with exact file paths, line numbers, and reusable functions
5. **Validates everything** before presenting the plan for your approval

The result is a plan file (`.ultraplan/plan.md`) that's detailed enough to execute without guessing, and concise enough to review in under a minute.

## Installation

### From the Skills Registry (Recommended)

```bash
npx skills add 6missedcalls/ultraplan
```

### Manual Installation

```bash
# Clone the repo
git clone https://github.com/6missedcalls/ultraplan.git

# Copy to your Claude Code skills directory
mkdir -p ~/.claude/skills/ultraplan
cp -r ultraplan/SKILL.md ultraplan/references ~/.claude/skills/ultraplan/
```

## Companion: Autonomous Mode (CLAUDE.md)

UltraPlan ships with a companion `CLAUDE.md` file that unlocks two additional capabilities when installed globally at `~/.claude/CLAUDE.md`. These are independent of the planning skill itself — they enhance Claude Code's baseline behavior across all repos.

### Always-Autonomous Mode

Derived from Claude Code's internal `getProactiveSection()` function (`src/constants/prompts.ts:860-913`), this replicates the "unfocused terminal" behavior where Claude operates with maximum autonomy. When the terminal is unfocused, Claude Code internally shifts into a mode where it makes decisions, commits, pushes, and acts without waiting for confirmation. The `CLAUDE.md` companion activates this behavior permanently:

- **Bias toward action** — reads files, runs tests, explores the codebase, and makes changes without asking
- **Commits and pushes autonomously** when a logical unit of work is complete
- **Picks an approach and goes** rather than asking which of two reasonable options to use
- **Only pauses for genuinely irreversible actions** (force push to main, dropping databases, deleting branches with unmerged work)

This is the exact behavioral shift Claude Code applies internally when it detects the user has switched away from the terminal. The `CLAUDE.md` version makes it the default at all times.

### Employee-Tier Prompt Enhancements

Derived from 6 `ant`-only (`process.env.USER_TYPE === 'ant'`) system prompt sections that Anthropic uses internally for their own employees. These are production-tested behavioral refinements that are normally gated behind an internal user type check:

- **Stricter comment rules** — default to writing no comments; only add one when the WHY is non-obvious (hidden constraints, subtle invariants, workarounds). Never explain WHAT the code does or reference the current task.
- **Assertiveness** — if the user's request is based on a misconception, or there's a bug adjacent to what they asked about, say so. Collaborator, not just executor.
- **Truthful reporting / false-claims mitigation** — never claim "all tests pass" when output shows failures, never suppress failing checks to manufacture a green result, never characterize incomplete work as done. Equally, don't hedge confirmed results with unnecessary disclaimers.
- **Prose communication style** — write for a person, not a console. Complete sentences, no unexplained jargon, assume the reader has lost context.
- **Numeric length anchors** — 25 words max between tool calls, 100 words max for final responses (unless the task requires more). These are the exact token budgets Anthropic's internal prompts enforce.
- **Conciseness directives** — no narrating each step, no listing every file read, no explaining routine actions.

### Installing the Companion CLAUDE.md

```bash
# The autonomous mode + employee-tier enhancements are in the companion CLAUDE.md
# Copy to your global Claude config to enable across all repos:
curl -o ~/.claude/CLAUDE.md https://raw.githubusercontent.com/6missedcalls/ultraplan/main/CLAUDE.md
```

> **Note:** `~/.claude/CLAUDE.md` loads globally across every repository Claude Code opens. If you already have a global `CLAUDE.md`, merge the contents manually rather than overwriting.

## Bonus: Hidden Claude Code Environment Variables

These are real environment variables that Claude Code's planning system respects today. Set them before launching `claude`:

```bash
# Unlock more parallel plan agents (default: 1, max: 10)
export CLAUDE_CODE_PLAN_V2_AGENT_COUNT=3

# More explore agents for codebase scanning (default: 3, max: 10)
export CLAUDE_CODE_PLAN_V2_EXPLORE_AGENT_COUNT=5

# Enable the iterative interview workflow (normally gated)
export CLAUDE_CODE_PLAN_MODE_INTERVIEW_PHASE=true
```

These work with the standard Claude Code binary — no custom build required. They control the built-in `/plan` command behavior, and the UltraPlan skill layers on top of them.

## Usage

### Keyword Trigger

Just include "ultraplan" anywhere in your prompt:

```
ultraplan add user authentication with OAuth2 and JWT tokens
```

### Slash Command

```
/ultraplan redesign the caching layer for better performance
```

### What Happens

1. Claude enters **read-only planning mode** (no file modifications except `.ultraplan/plan.md`)
2. Scans key files, then asks you clarifying questions
3. Launches parallel Explore agents to map the codebase
4. Launches Plan agents to design the implementation
5. Writes the final plan with file paths and verification steps
6. Presents it for your approval before any code is written

## Plan File Output

Plans are written to `.ultraplan/plan.md` with this structure:

```markdown
# Implementation Plan: [Title]

## Context
[One paragraph: what and why]

## Changes

### [Component 1]
- **File**: `src/auth/middleware.ts:42`
- **Change**: Add JWT validation middleware
- **Reuses**: `validateToken()` from `src/utils/crypto.ts:15`

### [Component 2]
- **File**: `src/routes/auth.ts:8`
- **Change**: Add login/logout endpoints

## Implementation Sequence
1. Create JWT middleware — `src/auth/middleware.ts`
2. Add auth routes — `src/routes/auth.ts`
3. Wire into app — `src/app.ts:23`

## Verification
npm test -- --filter=auth && npm run e2e -- --spec=auth
```

## Complexity Scaling

UltraPlan automatically scales to match task complexity:

| Task | Agents | Interview | Time |
|------|--------|-----------|------|
| Fix a bug in 2 files | 1 Explore | 1-2 questions | 5-10 min |
| Add a feature across 5 files | 2 Explore, 1 Plan | 3-5 questions | 15-20 min |
| Architectural refactor | 3 Explore, 2 Plan | Multiple rounds | 25-35 min |
| Major system redesign | 3 Explore, 3 Plan (different perspectives) | Extensive | 35-45 min |

## Design Principles

This skill is built on patterns extracted from production planning systems:

- **Explore before you plan.** Never propose changes to code you haven't read.
- **Ask before you assume.** Don't make large assumptions about user intent.
- **Reuse before you create.** Search for existing functions before proposing new ones.
- **One approach, not a menu.** Present your recommended approach, not all alternatives.
- **File paths are mandatory.** Every code reference includes `file:line`.
- **Verify before you claim.** If you didn't run it, don't say it passes.

## Anti-Patterns Addressed

The skill includes explicit mitigations for common AI planning failures:

- **False completion claims** (saying "tests pass" without running them)
- **Plan bloat** (200-line plans when 30 lines suffice)
- **Phantom file references** (citing functions that don't exist)
- **Alternative paralysis** (presenting options instead of recommending)
- **Scope creep** (adding unrequested improvements)
- **Premature convergence** (finalizing before exploring)
- **Asking findable questions** (interviewing about things in the code)

See `references/anti-patterns.md` for detailed failure modes and mitigations.

## Directory Structure

```
ultraplan/
  SKILL.md                  # Main skill file
  CLAUDE.md                 # Companion: autonomous mode + employee-tier enhancements
  README.md                 # This file
  LICENSE                   # MIT
  package.json              # Package metadata
  .gitignore                # Git ignore rules
  references/
    index.md                # Reference file index
    planning-patterns.md    # Plan templates and agent strategies
    anti-patterns.md        # Failure modes and mitigations
```

## License

MIT
