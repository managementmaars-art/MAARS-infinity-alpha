# Changelog

What's new, what's better, what's different. Most recent stuff on top.

---

## 0.12.4 — The Resume (2026-03-07)

Interrupted runs left requests stranded in `working/` — future runs skipped them, assuming another session was still active. Now `do work` automatically unclaims anything in `working/` that's been there over an hour before starting. `do work resume` does the same thing immediately, no age check — for when you know the session is gone and want to pick it back up now. Unclaimed requests move back to the queue with their existing plan sections intact.

- Added stale claim check to Step 1: files in working/ older than 1 hour are unclaimed and requeued
- Added `do work resume` command: immediate unclaim of all working/ files, no threshold
- Updated `do work` command description to document the 1-hour auto-unclaim behavior

## 0.12.3 — The Work Order (2026-03-07)

Mandatory steps were getting skipped because the checklists lived at the end of the files — retrospective checks agents had already blown past. Flipped the model: both do and work now open with a Step 0 that requires declaring your work order upfront, before touching any files. The checklist becomes a prospective commitment, not a retrospective review. Added a hard gate at the Step 4.5 → Step 5 boundary in work.md so Plan Verification can't be quietly skipped.

- Added Step 0 to do.md: agents must write out the capture order checklist before starting Step 1
- Added Step 0 to work.md: agents must write out the work order checklist before starting Step 1
- Added transition gate in work.md between Step 4.5 and Step 5 requiring ## Plan Verification in the file
- Checklist items define artifacts: "done" means the section is written, not just mentally completed

## 0.12.2 — The Triple Lock (2026-03-06)

Agents were still skipping Step 5.5 verification despite having the instructions. Three reinforcements: both REQ format templates (simple and complex) now include a `## Verification` section so agents see it as part of the expected output. Step 6 opens with a hard gate — "check every REQ has a Verification section, if not go back." And the STOP section repeats the check as a final catch.

- Added `## Verification` section to simple request format template with example coverage map
- Added `## Verification` section to complex request format template with example coverage map
- Added verification gate at top of Step 6: "BEFORE reporting, check every REQ has verification"
- Added verification check to STOP section: "if any REQ is missing verification, go back"
- Added note after simple format: "Every REQ file must end with a Verification section"

## 0.12.1 — The No-Ask Fix (2026-03-06)

Verification was asking permission instead of just fixing, and the inline steps were hand-waves pointing to separate files. Agents need the actual instructions right where they're working, not a link to go read. Fixed for both verify-request (in do.md) and verify-plan (in work.md).

- verify-request.md and verify-plan.md Step 5/7 now explicitly say "do not ask — just fix"
- do.md Step 5.5 is now self-contained with full inline instructions (enumerate, map, calculate, fix, store)
- work.md Step 4.5 is now self-contained with full inline instructions (same protocol)
- Agents no longer need to read separate verify action files during the do/work workflows
- Standalone verify files still exist for manual `do work verify` invocations

## 0.12.0 — The Proportional Planner (2026-03-06)

Planning is no longer gated by complexity. Every request gets a plan — the plan just scales to the task. A config change gets a one-liner. A new feature gets a multi-step strategy. Routes A/B/C still exist as complexity labels for retrospective analysis, but they no longer decide whether planning happens. verify-plan and exploration follow the same principle: they run based on the plan's content, not on a pre-hoc routing decision.

- Planning is mandatory for all routes — plan depth scales to complexity assessment
- Route labels (A/B/C) are now complexity hints for the planner, not workflow forks
- verify-plan runs on all routes (consistent quality gate regardless of complexity)
- Exploration is driven by plan content (references unknown files/patterns) instead of route
- Architecture diagram simplified to linear flow: triage -> plan -> verify -> explore? -> implement -> test
- Implementation prompts consolidated from three route variants to two (with/without exploration)
- Complexity Triage section renamed to Complexity Assessment, reframed as calibration not gating

## 0.11.0 — The Coverage Report (2026-03-06)

Verification is no longer a suggestion -- it's baked into the workflow. After capturing requests, the do action now automatically verifies every REQ against the original input: enumerates items, maps coverage, auto-fixes gaps, and stores the metrics. The work action does the same for plans -- after Route C planning, every plan gets verified against its REQ before exploration begins. Both use the same Coverage Analysis Protocol (enumerate, map, calculate, fix, store) so the measurement is consistent end-to-end. Skip it if you want ("skip verification"), but by default it runs.

- Split `verify.md` into `verify-request.md` (input -> REQs) and `verify-plan.md` (REQ -> plan)
- Added Coverage Analysis Protocol: enumerate source items, map to target, calculate %, auto-fix, store results
- verify-request runs automatically after do action creates REQ files (Step 5.5)
- verify-plan runs automatically after work action planning phase (Step 4.5, Route C only)
- Both auto-fix gaps instead of just reporting them -- coverage repair is the default behavior
- Coverage metrics stored in REQ files for traceability (available to downstream actions)
- Both skippable with "skip verification" in user input
- Updated work action architecture diagram, progress reporting, checklists, and examples

## 0.10.0 — The Hard Stop (2026-02-16)

Capture no longer slides into execution. The do action now has an explicit boundary: after writing files and reporting back, it stops. No helpful "let me go ahead and start building that for you." The user decides when to run the queue — always. Both SKILL.md (routing level) and do.md (action level) enforce this, so even eager agents get the message.

- Added "Capture ≠ Execute" guardrail to SKILL.md core concepts
- Added "STOP After Capture" section to do.md workflow, before the checklist
- Only exception: user explicitly asks for capture + execution in the same invocation

## 0.9.5 — The Reinstall (2026-02-04)

`npx skills update` silently fails to update files despite reporting success. Switched the update command to `npx skills add bladnman/do-work -g -y` which does a full reinstall and actually works. Also fixed the upstream URL — version checks now hit `version.md` where the version number actually lives.

- Update command changed from `npx skills update` to `npx skills add -g -y` (full reinstall)
- Upstream URL fixed: `SKILL.md` → `actions/version.md`

## 0.9.4 — The Passport (2026-02-04)

Install and update commands are no longer tied to a single CLI tool. Switched from `npx install-skill` / `npx add-skill` to the portable `npx skills` CLI, which works across multiple agentic coding tools. Update checks now point to `npx skills update` instead of a reinstall command.

- README install command updated to `npx skills add bladnman/do-work`
- Version action "update available" message now suggests `npx skills update`
- Fallback/manual update uses `npx skills add` instead of `npx install-skill`

## 0.9.3 — The Timestamp (2026-02-04)

Every changelog entry now carries a date. Backfilled all existing entries from git history so nothing's undated. Future entries get dates automatically — the CLAUDE.md format template and rules were updated to enforce it.

- Added `(YYYY-MM-DD)` dates to all 12 existing changelog entries via git history
- Updated CLAUDE.md changelog format template to include date
- Added "Date every entry" rule to changelog guidelines

## 0.9.2 — The Front Door (2026-02-04)

The SKILL.md frontmatter was broken — missing closing delimiters and markdown syntax mixed into the YAML. The `add-skill` CLI couldn't parse the skill metadata properly. Now it's valid YAML frontmatter that tools can actually read.

- Fixed SKILL.md frontmatter: removed `##` from name field, added closing `---`
- Cleaned up upstream URL (was wrapped in a markdown link inside YAML)

## 0.9.1 — The Gatekeeper (2026-02-04)

Keywords like "version" and "changelog" were sneaking past the routing table and getting treated as task content. Fixed by reordering the routing table so keyword patterns are checked before the descriptive-content catch-all, and added explicit priority language so agents match keywords first.

- Routing table now has numbered priority — first match wins, top to bottom
- "Descriptive content" catch-all moved to last position (priority 7)
- Step 2 clarifies that single keywords matching the table are routed actions, not content
- Fixes: `do work version` no longer asks "Add this as a request?"

## 0.9.0 — The Rewind (2026-02-04)

You can now ask "what's new" and actually see what's new — right at the bottom of your terminal where you're already looking. The version action gained changelog display with a twist: it reverses the entries so the latest changes land at the bottom of the output, no scrolling required. Portable across skills — any project with a CHANGELOG.md gets this for free.

- Changelog display added to the version action: `do work changelog`, `release notes`, `what's new`, `updates`, `history`
- Entries print oldest-to-newest so the most recent version appears at the bottom of terminal output
- Routing table updated with changelog keyword detection
- Works with any skill that has a CHANGELOG.md in its root

## 0.8.0 — The Clarity Pass (2026-02-03)

The UR system was hiding in plain sight — documented everywhere but easy to miss if you weren't reading carefully. This release restructures the do action and skill definition so the UR + REQ pairing is unmissable, even for agents that skim. Also added agent compatibility guidance to CLAUDE.md so future edits keep the skill portable across platforms.

- Added "Required Outputs" section to top of do.md — UR + REQ pairing stated upfront as mandatory
- Restructured Step 5 Simple Mode — UR creation now has equal weight with REQ creation
- Added Do Action Checklist at end of workflow — mirrors the work action's orchestrator checklist
- Moved UR anti-patterns to general "What NOT To Do" section (was under complex-only)
- Updated SKILL.md with core concept callout about UR + REQ pairing
- Added Agent Compatibility section to CLAUDE.md — generalized language, standalone-prompt design, floor-not-ceiling

## 0.7.0 — The Nudge (2026-02-01)

Complex requests now get a gentle suggestion to run `/do-work verify` after capture. If your input had lots of features, nuanced constraints, or multiple REQs, the system lets you know verification is available — so you can catch dropped details before building starts. Simple requests stay clean and quiet.

- Verify hint added to do action's report step for meaningfully complex requests
- Triggers on: complex mode, 3+ REQ files, or notably long/nuanced input
- Two complex examples updated to show the hint in action
- No change for simple requests — no hint, no noise

## 0.6.0 — The Bouncer (2026-02-01)

Working and archive folders are now off-limits. Once a request is claimed by a builder or archived, nobody can reach in and modify it — not even to add "one more thing." If you forgot something, it goes in as a new addendum request that references the original. Clean boundaries, no mid-flight surprises.

- Files in `working/` and `archive/` are now explicitly immutable
- New `addendum_to` frontmatter field for follow-up requests
- Do action checks request location before deciding how to handle duplicates
- Work action reinforces immutability in its folder docs

## 0.5.0 — The Record Keeper (2026-02-01)

Now you can see what changed and when. Added this very changelog so the project has a memory. CLAUDE.md got updated with rules to keep it honest — every version bump gets a changelog entry, no exceptions.

- Added `CHANGELOG.md` with full retroactive history
- Updated commit workflow: version bump → changelog entry → commit

## 0.4.0 — The Organizer (2026-02-01)

The archive got a brain. New **cleanup action** automatically tidies your archive at the end of every work loop — closing completed URs, sweeping loose REQs into their folders, and herding legacy files where they belong. Also introduced the **User Request (UR) system** that groups related REQs under a single umbrella, so your work has structure from capture to completion.

- Cleanup action: `do work cleanup` (or automatic after every work loop)
- UR system: related REQs now live under UR folders with shared context
- Routing expanded: cleanup/tidy/consolidate keywords recognized
- Work loop exit now triggers automatic archive consolidation

## 0.3.0 — Self-Aware (2026-01-28)

The skill learned its own version number. New **version action** lets you check what you're running and whether there's an update upstream. Documentation got a glow-up too.

- Version check: `do work version`
- Update check: `do work check for updates`
- Improved docs across the board

## 0.2.0 — Trust but Verify (2026-01-27)

Added a **testing phase** to the work loop and clarified what the orchestrator is (and isn't) responsible for. REQs now get validated before they're marked done.

- Testing phase baked into the work loop
- Clearer orchestrator responsibilities
- Better separation of concerns

## 0.1.1 — Typo Patrol (2026-01-27)

Fixed a username typo in the installation command. Small but important — can't install a skill if the command is wrong.

- Fixed: incorrect username in `npx install-skill` command

## 0.1.0 — Hello, World (2026-01-27)

The beginning. Core task capture and processing system with do/work routing, REQ file management, and archive workflow.

- Task capture via `do work <description>`
- Work loop processing with `do work run`
- REQ file lifecycle: pending → working → archived
- Git-aware: auto-commits after each completed request

