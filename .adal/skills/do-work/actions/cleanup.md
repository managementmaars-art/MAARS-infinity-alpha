# Cleanup Action

> **Part of the do-work skill.** Invoked when routing determines the user wants to tidy the archive, or automatically at the end of the work loop. Consolidates loose files and ensures the archive is well-organized.

The archive should be a collection of self-contained UR folders, each containing their original input and all related REQ files. Over time, REQ files can end up loose in the archive root — either from intermediate archival (when not all REQs were done yet) or from legacy requests predating the UR system. This action fixes that.

## When This Runs

- **Automatically** at the end of every work loop (after all pending REQs are processed)
- **Manually** when the user invokes it (e.g., `do work cleanup`, `do work tidy`)

## What It Does

Three passes, in order:

### Pass 1: Close Completed User Requests

Check `do-work/user-requests/` for UR folders that are ready to archive.

For each UR folder in `do-work/user-requests/`:

1. Read `input.md` and parse the `requests` array from frontmatter (e.g., `[REQ-044, REQ-045, REQ-046]`)
2. For each REQ ID in the array, check if it exists with `status: completed` in ANY of these locations:
   - `do-work/archive/UR-NNN/` (already consolidated)
   - `do-work/archive/` root (loose in archive)
   - `do-work/working/` (just completed, not yet moved)
3. If **ALL** REQs are completed:
   - Gather any loose completed REQ files from `do-work/archive/` root into the UR folder
   - Gather any completed REQ files from `do-work/working/` into the UR folder
   - Move the entire UR folder to `do-work/archive/UR-NNN/`
   - Report: `Archived UR-NNN (all N REQs complete)`
4. If **NOT all** REQs are completed:
   - Leave the UR folder in `user-requests/` — it's not ready yet
   - Report: `UR-NNN still open (X/Y REQs complete)`

### Pass 2: Consolidate Loose REQ Files in Archive

Check `do-work/archive/` root for any `REQ-*.md` files that should be inside a UR folder.

For each loose `REQ-*.md` file directly in `do-work/archive/` (not inside a subfolder):

1. Read its frontmatter and check for a `user_request` field
2. **If it has `user_request: UR-NNN`:**
   - Check if `do-work/archive/UR-NNN/` exists
   - If yes: move the REQ file into that UR folder
   - If no: check if `do-work/user-requests/UR-NNN/` exists (UR still open — leave the REQ in archive root for now, Pass 1 will handle it on next run)
   - If the UR folder doesn't exist anywhere: report a warning — `REQ-XXX references UR-NNN but no UR folder found`
3. **If it has NO `user_request` field (legacy/standalone):**
   - Move it to `do-work/archive/legacy/` (create the folder if needed)
   - Report: `Moved REQ-XXX to archive/legacy/ (no UR reference)`

### Pass 3: Fix Misplaced Folders

Check for UR folders that ended up in wrong locations within the archive.

1. Check if `do-work/archive/user-requests/` exists (this is a common mistake — the entire `user-requests/` dir got moved instead of individual UR folders)
2. If it exists, for each `UR-NNN/` folder inside it:
   - If `do-work/archive/UR-NNN/` does NOT already exist: move it up to `do-work/archive/UR-NNN/`
   - If `do-work/archive/UR-NNN/` DOES already exist: merge contents (move files from the misplaced folder into the correct one)
   - Report: `Fixed misplaced UR-NNN (was in archive/user-requests/)`
3. If `do-work/archive/user-requests/` is now empty, remove it

Also check for and consolidate any loose CONTEXT-*.md files:
- Move to `do-work/archive/legacy/` alongside legacy REQs

## Reporting

Print a summary at the end:

```
Archive cleanup complete:
  - Archived: UR-011 (3 REQs), UR-004 (8 REQs)
  - Consolidated: 5 loose REQs into their UR folders
  - Legacy: 24 REQs moved to archive/legacy/
  - Fixed: 1 misplaced UR folder
  - Still open: UR-015 (2/4 REQs complete)
```

If nothing needed fixing:
```
Archive is clean. No loose files or pending closures found.
```

## Archive Structure After Cleanup

```
do-work/archive/
├── UR-001/                    # Self-contained: input + all REQs
│   ├── input.md
│   ├── assets/
│   ├── REQ-018-feature.md
│   └── REQ-019-feature.md
├── UR-002/
│   ├── input.md
│   └── REQ-024-feature.md
├── legacy/                    # REQs and CONTEXT docs without UR references
│   ├── REQ-001-old-task.md
│   ├── REQ-002-old-task.md
│   └── CONTEXT-001-batch.md
└── hold/                      # Items on hold (unchanged by cleanup)
    └── ...
```

**No loose REQ or CONTEXT files should exist directly in `do-work/archive/` after cleanup.**

## What This Action Does NOT Do

- Delete any files — only moves them into the right location
- Modify file contents or frontmatter — files are relocated as-is
- Touch files in `do-work/` root (the queue) or `do-work/working/` — those are the work action's responsibility
- Archive UR folders that still have pending/in-progress REQs
- Process any REQ files (use the work action for that)
