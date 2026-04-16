---
name: work-unit-ritual
description: >
  Encode a 6-step work-unit ritual into AGENTS.md and orchestrate the
  ritual at runtime. Reads the project's External Tools (for the issue
  tracker CLI), Git Workflow (for branch/commit/PR rules), and
  References (for spec context) to perform one work unit end-to-end:
  plan → discuss → register issue → implement → completion check →
  close. Runs in two modes — setup (writes the ritual spec to AGENTS.md
  once) and runtime (executes one work unit using the stored spec).
  "work unit ritual", "do a work unit", "start task", "plan and implement",
  "issue workflow", "setup work ritual", "ritualized work",
  "task workflow", "complete a task end to end",
  Slash trigger: "/work-unit-ritual". First-run sets up the ritual;
  subsequent runs execute a ritual using the stored spec.
metadata:
  author: dev-goraebap
  version: "0.1.1"
---
<!-- AUTO-GENERATED - DO NOT EDIT DIRECTLY. Edit src/ instead. -->

# work-unit-ritual

Encode and execute a **6-step work-unit ritual** — the sequence a disciplined engineer follows when taking a non-trivial task from idea to closed issue. This skill has two modes: **setup** (write the ritual spec into AGENTS.md once) and **runtime** (execute one work unit using the stored spec).

**Philosophy.** Every other agent-collabo skill writes context *about* the project. This one also writes a *protocol* — a sequence of named steps the agent follows to turn intent into shipped work. The protocol itself lives in AGENTS.md so every future agent session, regardless of model or tool, follows the same rhythm. At runtime this skill is the orchestrator that walks through the steps; without it, a user can still follow the protocol by hand because it's documented in AGENTS.md.

## The 6-step ritual

```
1. Plan            — Interview the user. Read specs, git log, existing issues.
                     Propose a plan.
2. Discuss         — Optional. Iterate on the plan until consensus.
3. Register        — Open an issue following the project's convention.
4. Implement       — Execute the plan following the Git Workflow rules.
5. Completion check — Ask: "close the issue, or more changes?" Always reflect
                     implementation changes back into the issue body before
                     closing.
6. Close           — Follow the Git Workflow merge and PR rules. Close the
                     issue.
```

## Scope

**In scope:**
- **Setup mode**: write the ritual spec into AGENTS.md (as a subsection of `## Git Workflow`) and add gate rules to `## Boundaries`
- **Runtime mode**: execute one work-unit cycle by reading the stored spec and walking through the 6 steps
- Detect the issue tracker from `## External Tools > CLIs` (`gh` / `glab` / `linear-cli`) or from the project's remote (`git remote -v`)
- Reflect implementation changes back into the issue body at step 5 (this is the key discipline the ritual enforces)

**Out of scope:**
- Choosing which branching model, commit format, or PR rules to use — those come from `## Git Workflow` via `/git-workflow`. This skill reads them, it does not define them.
- Managing issue tracker credentials or authentication
- Tracking issue state across time (the tracker does that, not AGENTS.md)
- Cross-project work coordination

## Prerequisites

This skill requires three things to be in place before it can run (setup or runtime):

| Required | Why | If missing |
|---|---|---|
| `## Git Workflow` in AGENTS.md | The ritual reads branch/commit/PR rules from here | Redirect to `/git-workflow`. Stop. |
| `## External Tools > CLIs` with an issue tracker CLI (`gh`, `glab`, `linear-cli`, etc.) | The ritual uses this CLI to register and close issues | Redirect to `/manage-tools`. Stop. |
| AGENTS.md exists | Nothing to read from | Redirect to `/init-public-rules`. Stop. |

## Guardrails

| # | Check | On failure |
|---|-------|------------|
| 1 | CWD is a Git repository | "Please run this inside a Git repository." |
| 2 | AGENTS.md exists | "AGENTS.md not found. Run /init-public-rules first." |
| 3 | `## Git Workflow` section exists in AGENTS.md | "AGENTS.md has no ## Git Workflow section. Run /git-workflow first to define branching, commits, and PR rules. This skill extends that section — it does not define it. Stopping." |
| 4 | An issue tracker CLI is registered in `## External Tools > CLIs` OR detectable from `git remote -v` | "No issue tracker CLI found. Run /manage-tools to register one (e.g., `gh` for GitHub, `glab` for GitLab, `linear-cli` for Linear). Stopping." |
| - | Skill update check | **Session dedup**: if you have already fetched `manifest.json` for any agent-collabo skill earlier in this conversation, skip this check entirely and proceed. Otherwise: Let `SELF` be the value of the `name` field in this SKILL.md's frontmatter (e.g., `init-public-rules`). Let `LOCAL` be `metadata.version` from this same frontmatter. Fetch `https://raw.githubusercontent.com/dev-goraebap/agent-collabo/main/manifest.json` (1 HTTP request, fail silently on network error). Then evaluate exactly one case in this order: **Case A — outdated**: if `manifest.skills[SELF]` exists and `LOCAL < manifest.skills[SELF]`, tell the user (in their language) "agent-collabo `{SELF}` has a new version ({LOCAL} → {manifest.skills[SELF]}). Run `/agent-collabo-updater` when convenient. Continuing with the current task." then proceed. **Case B — up to date**: if `manifest.skills[SELF]` exists and `LOCAL === manifest.skills[SELF]`, proceed silently. **Case C — renamed away**: if `SELF` does NOT exist as a key in `manifest.skills` AND `SELF` exists as a key in `manifest.deprecated` (note: check the keys of `deprecated`, not the `renamedTo` values), tell the user "This skill `{SELF}` was renamed to `{manifest.deprecated[SELF].renamedTo}` since v{manifest.deprecated[SELF].since}. Run `/agent-collabo-updater` to migrate." then proceed. **Case D — unknown**: if `SELF` is not in `manifest.skills` and not in `manifest.deprecated`, tell the user "Skill `{SELF}` is no longer maintained. Run `/agent-collabo-updater` to clean up." then proceed with caution. Important: `manifest.deprecated` maps OLD names → NEW names. Never warn about a skill whose name is currently in `manifest.skills` just because that name appears as a `renamedTo` value somewhere in `deprecated`. **CDN cache caveat**: GitHub raw enforces `Cache-Control: max-age=300`, so right after a new release is pushed the manifest may be stale for up to 5 minutes via Fastly PoPs. If the user explicitly mentions they just released a new version (e.g., "I just pushed v0.X.Y") and this check still reports up-to-date or shows an older `manifest.version`, do not insist the local install is current — instead mention the 5-minute CDN window and suggest retrying shortly. For all other users this is invisible because they fetch long after the cache expires. |

## Language Policy

Conduct all user-facing communication in the user's language: interview questions, follow-up prompts, status messages, diagnostic reports, and summaries. Detect the language from (in order):

1. The language of the user's most recent messages in the current session
2. Declarations in their local rules file (e.g., `CLAUDE.local.md`, `.cursor/rules/local.mdc`) — look for instructions like "respond in Korean"
3. OS locale (`$LANG`, `$LC_ALL`)
4. English as fallback

Generated file content follows the file's audience: team-shared files (`AGENTS.md`, `CHANGELOG.md`) stay in English regardless of the user's language; personal files (`CLAUDE.local.md`, `GEMINI.local.md`, etc.) use the user's language unless they specify otherwise.

## Modes

### Setup mode

Triggered when `## Git Workflow` does not contain a `### Work unit ritual` subsection. Writes the ritual spec once, then exits. Runs an interview about issue convention and writes the result.

**Write-once principle.** This skill follows `/manage-refs` and `/git-workflow`'s write-once approach. Re-running on a project that already has the ritual set up produces a 2-choice menu: "refine spec" or "overwrite from scratch". No silent drift management.

### Runtime mode

Triggered when the ritual is already set up AND the user invokes `/work-unit-ritual` to start an actual work unit. Walks through the 6 steps.

## Workflow

### Step A: Determine mode

1. Read AGENTS.md.
2. Check whether `## Git Workflow > ### Work unit ritual` subsection exists.
3. If absent → **Setup mode** (Step B).
4. If present → Ask:
   ```
   Work unit ritual is already set up. What would you like to do?

   1. Start a new work unit (runtime mode)
   2. Refine the existing ritual spec
   3. Overwrite the ritual spec from scratch
   4. Cancel
   ```

### Step B: Setup mode — encode the ritual

#### B1. Detect the issue tracker

From `## External Tools > CLIs`, match known tracker CLIs:
- `gh` → GitHub Issues
- `glab` → GitLab Issues
- `linear-cli` → Linear
- `jira-cli` → Jira
- `plane-cli` → Plane

If multiple match, ask the user which one this project uses primarily. If none match but `git remote -v` shows a GitHub/GitLab URL, ask the user whether `gh` / `glab` is available and redirect to `/manage-tools` to register it if not.

#### B2. Ask about issue convention (with hybrid pre-scan)

Present a default template and let the user toggle fields:

```
What should go into each issue body? Default template (toggle what
you want to change):

  a) Why — background and motivation                         [recommended]
  b) Acceptance criteria — what "done" looks like             [recommended]
  c) Related spec — pointer into ## References if applicable  [recommended]
  d) Plan — the approach agreed in step 1                     [recommended]
  e) Changes — appended in step 5 when implementation differed
     from the plan (critical: keeps the issue honest about
     what shipped)                                            [recommended]
  f) Labels / milestone
  g) Assignee

[recommended] = included by default in a good issue template.
Enter the letters of the items you want (e.g., "a, b, c, d, e"):
```

If the user wants to write the convention from scratch, switch to open interview. Otherwise use the checklist result as-is.

#### B3. Write the ritual spec into AGENTS.md

Append a `### Work unit ritual` subsection inside the existing `## Git Workflow` section. The content is:

```markdown
### Issue tracking

- Tracker: <tool name, e.g., GitHub Issues via `gh`>
- Issue template: see ### Issue convention below

### Issue convention

Each issue body contains:

- **Why** — background and motivation
- **Acceptance criteria** — explicit "done" conditions
- **Related spec** — pointer into `## References` if applicable
- **Plan** — the approach agreed in step 1 of the ritual
- **Changes** — appended in step 5 when the implementation diverges
  from the plan; keeps the issue body honest about what shipped

### Work unit ritual

For any non-trivial task, follow this sequence:

1. **Plan** — Read `## References` (if present), `git log -20`, and
   existing issues for context. Propose a written plan to the user.
2. **Discuss** *(optional)* — If the user wants to iterate on the
   plan, loop until they approve.
3. **Register** — Open an issue following the `### Issue convention`
   above, using the tracker from `### Issue tracking`.
4. **Implement** — Follow the rules in this `## Git Workflow` section
   (branching, commits, merges). Reference the issue in commits.
5. **Completion check** — Ask: "close the issue, or more changes?"
   Before closing, append any **Changes** that diverged from the
   original **Plan** into the issue body. The issue must accurately
   reflect what shipped.
6. **Close** — Follow the PR/merge rules in this section. Close the
   issue (via the tracker CLI, not by guessing).
```

#### B4. Append gate rules to `## Boundaries`

The ritual introduces two cross-cutting autonomy rules that belong in `## Boundaries`. Ask the user once:

```
The ritual introduces two gate rules. Add them to ## Boundaries?

### Ask first
  - Opening, commenting on, or closing an issue
  - Implementing a non-trivial task without a written plan

### Never do
  - Close an issue without appending implementation changes to the body
  - Close an issue without user approval

(y/n)
```

On "y", append to `## Boundaries`. If `## Boundaries` does not exist, redirect to `/refine-boundaries`:
> "No ## Boundaries section yet. Run /refine-boundaries to create it, then re-run this skill. Stopping at the Boundaries step; the ritual spec was already written to ## Git Workflow."

This is a rare case where the skill deliberately does partial work — the ritual spec itself is valuable even without gate rules, and the user can add Boundaries later.

#### B5. Summary

```
✅ Work unit ritual set up.

Written to AGENTS.md:
  - ## Git Workflow > ### Issue tracking
  - ## Git Workflow > ### Issue convention
  - ## Git Workflow > ### Work unit ritual
  - ## Boundaries updates (Ask first + Never do)

Next time you have a non-trivial task, run /work-unit-ritual to
execute the ritual. The agent will follow the 6 steps using the
spec just written.
```

### Step C: Runtime mode — execute one work unit

Called when the ritual is already set up and the user wants to start a task.

#### C1. Gather context

1. Ask the user: "What do you want to work on?" Accept a one-line description.
2. Read the ritual spec from `## Git Workflow > ### Work unit ritual` — use it as the protocol, do not improvise.
3. Read `## References` (if present) for any relevant spec pointers. Do not auto-load unless the user's task clearly matches one.
4. Run `git log --oneline -20` for recent context.
5. Check the tracker for existing open issues that might be related:
   - GitHub: `gh issue list --search "<keywords from user task>"`
   - GitLab: `glab issue list --search "<keywords>"`
   - Linear: `linear issue list`

#### C2. Step 1 — Plan

Synthesize a written plan. Present it to the user:

```
Plan for: "<user task description>"

Context I read:
  - git log (last 20 commits)
  - Related spec: docs/payment-prd.md (from ## References)
  - Existing issues: #42 "Payment flow idle timeout" (possibly related)

Proposed plan:
  1. <step>
  2. <step>
  3. <step>

Acceptance criteria:
  - <criterion>
  - <criterion>

Approve this plan, or discuss?
```

#### C3. Step 2 — Discuss (optional)

If the user wants changes, loop. Each iteration produces a new plan version. Stop when the user approves.

#### C4. Step 3 — Register

Open an issue using the tracker CLI. Fill in the body using the project's `### Issue convention`. **Ask before creating the issue** (per the Boundaries gate rule added in setup).

```
Ready to open this issue:

  Title: <title>
  Body:
    ## Why
    ...
    ## Acceptance criteria
    ...
    ## Related spec
    docs/payment-prd.md
    ## Plan
    1. ...

Create via `gh issue create`? (y/n)
```

Store the issue number returned by the CLI for later steps.

#### C5. Step 4 — Implement

Execute the plan following `## Git Workflow` rules. This is the actual coding phase — use whatever other agent skills and tools are appropriate.

Reference the issue in commit messages per the project's convention (e.g., `feat(payment): handle idle timeout (#<issue>)`).

#### C6. Step 5 — Completion check

When the implementation is done, ask the user:

```
Implementation looks complete. Before closing the issue:

1. Review the diff between plan and what was actually done
2. Any changes from the plan should be reflected in the issue body

Changes I detected vs the original plan:
  - Added a retry with exponential backoff (not in original plan)
  - Skipped the rollback step (user decided to defer)

Shall I update the issue body with a ## Changes section reflecting
these? (y/n)

Then: close the issue, or more changes needed?

1. Close issue
2. More changes needed (return to step 4)
3. Abandon work unit (leave issue open, do not close)
```

Before closing, update the issue body via `gh issue edit <num> --body-file <tempfile>` to append or update a `## Changes` section. This is the **critical discipline** the ritual enforces — issues must tell the truth about what shipped.

#### C7. Step 6 — Close

1. Follow the PR/merge rules from `## Git Workflow` (open PR, wait for checks, merge).
2. Close the issue via the CLI: `gh issue close <num>`.
3. Summary:
   ```
   ✅ Work unit complete.

   Issue #<num>: <title>
   Commits: <count>
   PR: <url or merge commit SHA>
   Changes from original plan: <summary>
   ```

## Interaction with other skills

- **`/git-workflow`** must run before this skill. This skill appends `### Issue tracking`, `### Issue convention`, and `### Work unit ritual` into `## Git Workflow`. It never modifies the preset rules themselves.
- **`/manage-tools`** must have registered the issue tracker CLI in `## External Tools > CLIs`. This skill reads it at runtime to choose the right CLI.
- **`/refine-boundaries`** owns `## Boundaries`. This skill asks once to add its two gate rules during setup. Rule removal or restructuring goes through `/refine-boundaries`.
- **`/manage-refs`** owns `## References`. This skill reads references at runtime to gather context; it never writes there.

## Prohibited actions

- Never run the ritual without prerequisites in place — redirect to the right skill instead
- Never guess at branch/commit/PR rules — always read `## Git Workflow`
- Never close an issue without appending `## Changes` for any divergence from the plan (this is the ritual's core discipline)
- Never register an issue without user confirmation (enforced by the Boundaries "Ask first" gate)
- Never create a **second** `## Git Workflow` section — append to the existing one
- Never overwrite the user's preset choice in `## Git Workflow` — only add subsections
