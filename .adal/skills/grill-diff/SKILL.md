---
name: grill-diff
description: Grill the diff. Specialists evaluate every finding internally — only high-value findings reach the user for discussion until reaching shared understanding.
license: MIT
metadata:
  author: shihyuho
  version: "1.0.0"
---

# Grill Diff

## Diff Scope

File scope and diff baseline are independent and combine freely (e.g. "against develop src/auth.ts").

- **Files:** user-specified if listed, otherwise all changed files.
- **Baseline:** staged > unstaged > user-specified branch > PR URL > current branch vs default branch.

## Review

Ask if there is a related spec or plan file. Read all changed files to build the full picture, then go through files one at a time. Interrogate every aspect of each change.

If a question can be answered by exploring the codebase, specs, or tests, explore yourself instead of asking.

When you spot a finding, consult all 3 specialists. Each sees earlier opinions, then gives opinion + confidence (high / medium / low). Classify:
- Any specialist rated **high** → present to user
- Highest is **medium**, or specialists disagree → present to user as "uncertain"
- All rated **low** → drop silently

After all findings in a file are classified, merge duplicates and link related ones. Present surviving findings one at a time, discussing with the user until reaching shared understanding. Provide your recommended fix for each.

Files with no surviving findings advance silently.

## Specialists

All 3 are consulted for every finding.

**correctness** — Correctness & Edge Cases
- Does this code do what it intends to do?
- Are edge cases handled — null, empty, boundary values, error paths?
- Are there race conditions, off-by-one errors, or state inconsistencies?

**security** — Security
- Is user input validated and sanitized at system boundaries?
- Are secrets kept out of code, logs, and version control?
- Is authentication/authorization checked where needed?
- Are there injection risks — SQL, command, template, or otherwise?
- Are new dependencies introduced? Are they from trusted sources?

**scope** — Scope & Necessity
- Is this change needed? What breaks if we revert it?
- With spec/plan: Is every spec requirement addressed? Is every change traceable to a spec requirement? Does the implementation match the spec's described behavior?
- Without spec/plan: Is this change doing too much — should it be split?
