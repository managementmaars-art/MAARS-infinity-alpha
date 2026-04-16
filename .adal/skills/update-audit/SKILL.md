---
name: update-audit
description: Check operating system, apps, drivers, runtimes, package managers, and core tools for outdated versions, weak choices, or obvious upgrade opportunities after asking the user to choose Audit mode or YOLO mode.
---

# Update Audit

Use this when the user wants a focused pass on updates, outdated tools, and whether the machine is using the right software stack.

## First Step: Pick A Mode

At the start of the interaction, ask the user to choose one mode:

Ask exactly:
`Choose a mode: Audit mode (recommended) or YOLO mode.`

- `Audit mode` (recommended): inspect first, report findings, ask before changing anything
- `YOLO mode`: still try to be safe, but carry out actions without asking again after the initial mode choice

If the user already picked a mode earlier in the same task, do not ask again.

## When To Use

- operating system update check
- outdated apps or runtimes
- old drivers or package managers
- whether the machine is using the right tools
- upgrade and replacement opportunities

## What To Check

- OS update status
- app update status
- runtimes and SDKs
- package managers
- drivers where visible
- obvious outdated or low-value tools
- better-maintained replacements when useful

## Rules

- prefer evidence over assumptions
- prioritize high-impact outdated or risky components first
- distinguish “outdated” from “optional upgrade”
- in Audit mode, ask before changing anything
- in YOLO mode, proceed without repeated approval, but still avoid reckless actions
- separate urgent security or stability updates from ordinary freshness improvements
- only recommend replacements when there is a concrete maintenance, security, or usability reason

## Output

Report:

1. critical updates
2. outdated tools worth attention
3. replacements or better choices
4. recommended next steps
5. approval-required changes in Audit mode

## Read Next

- `references/checklist.md`
- `references/report.md`
- `references/windows.md`
- `references/macos.md`
- `references/linux.md`
