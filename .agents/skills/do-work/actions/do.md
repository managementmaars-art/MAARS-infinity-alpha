# Do Action

> **Part of the do-work skill.** Invoked when routing determines the user is adding a request. Creates a `do-work/` folder in your project for request tracking.

A fast-capture system for turning quick ideas into structured request files. Designed for speed - minimal interaction when intent is clear, human-in-the-loop only when genuinely ambiguous.

## Required Outputs

Every invocation of the do action produces exactly two things:

1. **A User Request (UR) folder** at `do-work/user-requests/UR-NNN/` containing an `input.md` with the full verbatim user input
2. **One or more REQ files** at `do-work/REQ-NNN-slug.md`, each linked to the UR via `user_request: UR-NNN` in frontmatter

Both are mandatory. Never create one without the other. This applies to every invocation — simple or complex, one REQ or ten.

- A REQ without a `user_request` field is orphaned — there is no source of truth to verify against
- A UR without REQ files is pointless — nothing gets queued for the work action
- The verify action depends on this linkage to evaluate capture quality

## Philosophy

- **Speed over perfection**: This is a rapid capture interface, not a design review
- **Represent, don't expand**: If the user says 5 words, write a 5-word request (with structure). Don't inflate a simple idea into a 400-word PRD
- **The building agent solves technical questions**: You're capturing intent, not making architectural decisions
- **Multiple requests are expected**: Users often say "do X, and also Y, and don't forget Z"
- **Never be lossy**: For complex inputs, preserve ALL detail - don't summarize away requirements

## Simple vs Complex Requests

This skill handles two modes:

| Mode | Input Size | Approach |
|------|------------|----------|
| **Simple** | Short, 1-3 features | Quick capture, lean format |
| **Complex** | Long, detailed, multi-feature | Full preservation with context document |

### Detecting Complex Requests

Treat a request as **complex** when ANY of these apply:

- **Length**: Input is >500 words or feels substantial
- **Detail**: Includes specific requirements, constraints, edge cases, acceptance criteria
- **Breadth**: Describes 3+ distinct features or components
- **Explicit**: User says "spec", "PRD", "detailed requirements", "here's what I need..."
- **Nuance**: Contains "must", "should", "never", "always", specific values, or conditional logic
- **Relationships**: Features depend on each other or have sequencing

**When in doubt, treat it as complex.** Over-preserving is better than losing requirements.

### The Lossy Problem

When splitting a 15-minute detailed spec into 5 requests, information gets lost:
- Shared context disappears
- Cross-feature requirements fall through cracks
- The "why" behind decisions vanishes
- Subtle constraints get summarized away
- **User certainty level** — hedges like "I'm not trying to be prescriptive," "these are just ideas," "I don't know what that looks like" signal the builder has latitude. Hard statements like "must," "definitely," "never" signal firm requirements.
- **Scope awareness cues** — when the user says things like "keep it simple" or "don't over-build," that's important builder guidance that gets dropped during extraction.
- **Thinking evolution** — when users talk through options and land on a decision, note the final decision AND that they explored alternatives (the context doc has the full journey, but the REQ should flag that the user was exploratory here).

**Solution: User Request (UR) Documents**

Every invocation of the do action creates a User Request (UR) folder that preserves the FULL verbatim input. For complex requests, individual REQ files reference back to their UR. For simple requests, the UR is minimal (just `input.md` with the original text), but the traceability is consistent.

## Request File Location

All request files go in the project's `do-work/` folder:
- `do-work/` at the project root (create if it doesn't exist)
- `do-work/user-requests/UR-NNN/` for each user request invocation, containing:
  - `input.md` — the verbatim original input (always created)
  - `assets/` — screenshots, images, and other reference materials for this request

**CRITICAL: The do action writes to these locations:**
1. `do-work/` root - ONLY for `REQ-*.md` request files (the queue)
2. `do-work/user-requests/UR-NNN/` - For the verbatim input and assets per user request

**NEVER write to:**
- `do-work/working/` - This is exclusively managed by the work action
- `do-work/archive/` - This is exclusively managed by the work action
- The project root directory - All do-work files stay within `do-work/`

This folder name reflects the **do-work pattern** - requests created by the do action are processed by the work action.

### File Immutability Rule

**Files in `working/` and `archive/` are IMMUTABLE. They must never be modified, appended to, or updated by any action other than the work action's own processing pipeline.**

This is a hard rule with no exceptions:

- **`do-work/working/`**: A builder is actively working on this request. The content is locked. No addendums, no "oh wait, one more thing." If you modify a file mid-build, you risk corrupting the builder's context or creating conflicts with work already in progress.
- **`do-work/archive/`**: This is the historical record. Completed work is done. Changing archived files rewrites history and breaks traceability.

**What happens when someone wants to add to an in-flight or completed request?**

Create a **new addendum request** that references the original. The addendum goes through the normal queue as its own REQ file. This keeps the original intact and gives the builder a clean, standalone unit of work.

See Step 2 for the full addendum-to-in-flight workflow.

## File Naming Convention

**Request files:** `REQ-[number]-[slug].md`
- Location: `do-work/` root (the queue)
- Examples: `REQ-001-dark-mode.md`, `REQ-002-export-to-pdf.md`

**User Request (UR) folders:** `do-work/user-requests/UR-[number]/`
- Created for EVERY do action invocation (simple or complex)
- Contains `input.md` with the full verbatim user input
- Contains `assets/` subfolder for screenshots and attachments specific to this request
- Examples: `do-work/user-requests/UR-001/input.md`, `do-work/user-requests/UR-002/assets/screenshot.png`

**UR folder lifecycle:**
- Created in `do-work/user-requests/` by the do action
- Referenced by REQ files via `user_request: UR-NNN` frontmatter field
- The work action moves UR folders to `do-work/archive/UR-NNN/` when **all related REQs** are complete, pulling archived REQ files into the UR folder for self-contained units

**Screenshot and asset files:**
- Location: `do-work/user-requests/UR-NNN/assets/`
- Naming: `REQ-[num]-[descriptive-name].png` (or appropriate extension)
- Examples: `do-work/user-requests/UR-003/assets/REQ-017-toc-screenshot.png`

To get the next REQ number, check existing `REQ-*.md` files in `do-work/`, `do-work/working/`, and `do-work/archive/` (and inside `archive/UR-*/`), then increment from the highest. UR folders use their own numbering sequence — check `do-work/user-requests/` and `do-work/archive/UR-*/` for the highest existing UR number.

### Backward Compatibility

REQ files created before the UR system will not have a `user_request` field, and their assets may live in `do-work/assets/` or reference `CONTEXT-*.md` files. This is fine — the work action handles both patterns:

- **REQs without `user_request`**: Process and archive normally — move directly to `do-work/archive/` (not into a UR subfolder)
- **REQs with `context_ref` pointing to `assets/CONTEXT-*.md`**: The work action archives the CONTEXT file alongside the REQ when all related REQs are complete (legacy behavior)
- **Assets in `do-work/assets/`**: Left in place (legacy) — only new assets go into UR folders
- **New REQs always get `user_request`**: Going forward, every REQ created by the do action includes a `user_request: UR-NNN` field

## Request File Format

### Simple Request Format

For quick captures - short, single-feature requests.

```markdown
---
id: REQ-001
title: Brief descriptive title
status: pending
created_at: 2025-01-26T10:00:00Z
user_request: UR-001
---

# [Brief Title]

## What
[1-3 sentences describing what is being requested]

## Why (if provided)
[User's stated reasoning - ONLY if they gave one. Omit section if not provided]

## Context
[Any additional context, constraints, or details the user mentioned]

## Assets
[Detailed description of any screenshots, or links to manually-saved files]

---
*Source: [original verbatim request]*

## Verification

**Source**: UR-001/input.md
**Pre-fix coverage**: 100% (3/3 items)

### Coverage Map

| # | Item | REQ Section | Status |
|---|------|-------------|--------|
| 1 | Add dark mode toggle | What | Full |
| 2 | App-wide | What | Full |
| 3 | Toggle in settings | Context | Full |

*Verified by verify-request action*
```

Keep it lean. If the user said "add dark mode", the What section might just be "Add a dark mode toggle to the app." That's fine.

**Every REQ file must end with a `## Verification` section.** If it doesn't have one, Step 5.5 was skipped — go back and run it.

### Complex Request Format

For detailed, multi-feature, or nuanced requests. Uses additional fields and references a context document.

```markdown
---
id: REQ-005
title: OAuth login flow
status: pending
created_at: 2025-01-26T10:00:00Z
user_request: UR-001
related: [REQ-006, REQ-007, REQ-008]
batch: auth-system
---

# OAuth Login Flow

## What
Implement OAuth-based authentication with Google and GitHub providers.

## Detailed Requirements
[Extract ALL requirements from the original input that apply to THIS feature specifically.
DO NOT SUMMARIZE. Include everything the user said about this feature.]

- Must support Google OAuth 2.0 with PKCE
- Must support GitHub OAuth
- Redirect to /dashboard after successful login
- Store refresh tokens encrypted at rest (user said "tokens must be encrypted")
- Handle token expiration gracefully - refresh automatically if possible
- Show loading spinner during OAuth redirect
- Handle OAuth errors with user-friendly messages, not technical errors
- "Remember me" checkbox to extend session duration
- Log authentication events for security audit

## Constraints
[Any limitations or restrictions mentioned]

- Must work with existing session management system
- Cannot use third-party auth services (user explicitly said "no Auth0 or similar")
- Must support existing users migrating from password auth

## Dependencies
[What this feature needs or what needs it]

- Depends on: REQ-007 (session management) - needs session system first
- Blocks: REQ-006 (user profile) - profile needs auth to exist

## Builder Guidance
[Capture the user's tone/intent signals that affect HOW to build, not WHAT to build]

- Certainty level: Exploratory / Firm / Mixed
- Scope cues: [Any "keep it simple," "don't over-build," "just ideas" signals]
- [Any specific latitude given to the builder]

## Open Questions
[Ambiguities that the builder should clarify or decide]

- Should OAuth be the only login method, or alongside password?
- What happens if user's email from OAuth doesn't match existing account?

## Full Context
See [user-requests/UR-001/input.md](./user-requests/UR-001/input.md) for complete verbatim input.

---
*Source: See UR-001/input.md for full verbatim input*

## Verification

**Source**: UR-001/input.md
**Pre-fix coverage**: 90% (9/10 items)
**Post-fix coverage**: 100% (10/10 items)

### Coverage Map

| # | Item | REQ Section | Status |
|---|------|-------------|--------|
| 1 | Google OAuth 2.0 with PKCE | Detailed Requirements | Full |
| 2 | GitHub OAuth | Detailed Requirements | Full |
| 3 | Redirect to /dashboard | Detailed Requirements | Full |
| 4 | Encrypt refresh tokens at rest | Detailed Requirements | Full |
| 5 | Handle token expiration | Detailed Requirements | Full |
| 6 | Loading spinner during redirect | Detailed Requirements | Full |
| 7 | User-friendly error messages | Detailed Requirements | Full |
| 8 | Remember me checkbox | Detailed Requirements | Full |
| 9 | No Auth0 or similar | Constraints | Full |
| 10 | Migrate existing password users | Constraints | Missing -> Fixed |

### Fixes Applied

- Added "Must support existing users migrating from password auth" to Constraints

*Verified by verify-request action*
```

### User Request (UR) input.md Format

Created for EVERY do action invocation. Preserves the FULL verbatim input.

**Location:** `do-work/user-requests/UR-[number]/input.md`

```markdown
---
id: UR-001
title: Authentication System Requirements
created_at: 2025-01-26T10:00:00Z
requests: [REQ-005, REQ-006, REQ-007, REQ-008]
word_count: 1847
---

# Authentication System Requirements

## Summary
[2-3 sentence overview of what this user request covers]

User described a complete authentication system including OAuth login, user profiles,
session management, and password reset flows. Emphasized security requirements and
integration with existing systems.

## Extracted Requests

| ID | Title | Summary |
|----|-------|---------|
| REQ-005 | OAuth login flow | Google/GitHub OAuth with PKCE |
| REQ-006 | User profile management | Profile editing, avatar upload |
| REQ-007 | Session management | Token storage, expiration, refresh |
| REQ-008 | Password reset flow | Email-based reset with expiry |

## Batch Constraints
[Cross-cutting concerns that apply to all REQs in this batch — omit for simple single-REQ requests]

- [Shared design principles, sequencing requirements, performance budgets]
- [User tone signals: "keep it simple," scope cues, latitude given]

## Full Verbatim Input

[THE COMPLETE, UNEDITED INPUT FROM THE USER]

[Paste the entire 15 minutes of transcribed text here, exactly as received.
Do not summarize, edit, or clean up. This is the source of truth.]

[If the input was very long, it's okay - include all of it. The builder
can read this if they need context that wasn't captured in the individual
request files.]

---
*Captured: 2025-01-26T10:00:00Z*
```

**For simple requests**, the input.md is minimal:

```markdown
---
id: UR-005
title: Add keyboard shortcuts
created_at: 2025-01-26T10:00:00Z
requests: [REQ-020]
word_count: 4
---

# Add keyboard shortcuts

## Full Verbatim Input

add keyboard shortcuts

---
*Captured: 2025-01-26T10:00:00Z*
```

### Frontmatter Fields

**All requests:**

| Field | Required | Description |
|-------|----------|-------------|
| `id` | Yes | Request identifier (REQ-NNN) |
| `title` | Yes | Short title |
| `status` | Yes | Always `pending` when created |
| `created_at` | Yes | ISO 8601 timestamp |
| `user_request` | Yes | UR identifier linking back to the originating user request (UR-NNN) |

**Complex requests (additional fields):**

| Field | Required | Description |
|-------|----------|-------------|
| `related` | If applicable | Array of related REQ IDs |
| `batch` | If applicable | Batch name grouping related requests |
| `addendum_to` | If applicable | Original REQ ID this request amends (used when the original is in `working/` or `archive/`) |

**UR input.md documents:**

| Field | Required | Description |
|-------|----------|-------------|
| `id` | Yes | User request identifier (UR-NNN) |
| `title` | Yes | Descriptive title for the request or batch |
| `created_at` | Yes | ISO 8601 timestamp |
| `requests` | Yes | Array of REQ IDs extracted from this user request |
| `word_count` | Yes | Word count of original input (for reference) |

The work action adds additional fields (`claimed_at`, `route`, `completed_at`) as it processes each request.

**Note:** Legacy REQ files may have `context_ref` instead of `user_request`. The work action handles both.

## Workflow

### Step 0: Declare Your Capture Order

**Before doing anything else**, write out the following checklist. Treat it as your active work order — check items off as you complete each step. Do not start Step 1 until you have written this out.

```
Capture order:
[ ] Step 1:   Parse input — single vs. multiple requests
[ ] Step 1.5: Assess complexity — simple or complex mode
[ ] Step 2:   Check for existing requests — duplicates, addendums
[ ] Step 3:   Clarify only if genuinely ambiguous (skip if clear)
[ ] Step 4:   Handle screenshots if present (skip if none)
[ ] Step 5:   Create UR folder with input.md
[ ] Step 5:   Create REQ file(s) with user_request: UR-NNN in frontmatter
[ ] Step 5:   Update UR requests array with all REQ IDs
[ ] Step 5.5: *** MANDATORY *** Verify requests — enumerate items from UR input, map to REQs, fix gaps, append ## Verification to every REQ file
[ ] Step 6:   Report back — include verification coverage, never report without it
```

Marking Step 5.5 as done means every REQ file you created has a `## Verification` section appended to it. If any file is missing this section, Step 5.5 is not complete — go back.

### Step 1: Parse the Request

Read the user's input. Look for:
- Single request vs multiple requests
- Clear intent vs ambiguous intent
- Any provided context (screenshots, references to existing behavior)

**Multiple request indicators:**
- "and also", "oh and", "plus", "additionally"
- Comma-separated lists
- Numbered items
- Distinct topics in the same message

### Step 1.5: Assess Complexity

Determine if this is a simple or complex request.

**Complex indicators** (any of these → complex mode):
- Input is >500 words
- 3+ distinct features or components
- Detailed requirements, constraints, or acceptance criteria
- User says "spec", "PRD", "detailed", "requirements"
- Contains specific values, conditions, or edge cases
- Features have dependencies or sequencing
- Multiple stakeholders or user types mentioned

**Simple indicators** (all of these → simple mode):
- Short, focused input (<200 words)
- 1-2 features max
- No detailed constraints
- Quick idea capture

**When uncertain → treat as complex.** It's better to over-preserve than lose requirements.

### Step 2: Check for Existing Requests

Read all files in `do-work/` folder, **and list filenames in `do-work/working/` and `do-work/archive/`** (don't read their contents — just check for matching IDs/slugs). For each parsed request:
- Does a similar request already exist?
- Is this an enhancement to an existing request?
- Is this a duplicate?
- **Where does the existing request live?** (queue, working, or archive)

**If duplicate/similar found — the location matters:**

| Existing request is in... | Action |
|---------------------------|--------|
| `do-work/` (queue) | Safe to append an addendum to the pending file |
| `do-work/working/` | **NEVER modify.** Create a new addendum REQ (see below) |
| `do-work/archive/` | **NEVER modify.** Create a new addendum REQ (see below) |

**If the match is in the queue (`do-work/` root):**
- If clearly the same thing: Tell user, don't create new file
- If similar but potentially different: Use your environment's ask-user prompt/tool to clarify
- If enhancement: Ask if they want to update the existing request

**Updating a queued request (addendum, not rewrite):**

Don't rework the original content — that's lossy. Instead, append an Addendum section:

```markdown
## Addendum (2025-01-27)

User added: "dark mode should also affect the sidebar"

- Sidebar must also respect dark mode theme
- [any other new requirements extracted from the update]
```

This preserves the original request intact. The building agent reconciles the original + addendum during planning — it can see what came first and what was added later.

**If the match is in `working/` or `archive/` — create an addendum REQ:**

The original request is either being actively built or already completed. You cannot touch it. Instead, create a brand new request that explicitly references the original:

```markdown
---
id: REQ-021
title: "Addendum: dark mode sidebar support"
status: pending
created_at: 2025-01-27T09:00:00Z
user_request: UR-006
addendum_to: REQ-005
---

# Addendum: Dark Mode Sidebar Support

## What
Add sidebar support to the existing dark mode implementation (REQ-005).

## Context
This is an addendum to REQ-005 (dark mode), which is currently [in progress / completed].
The user realized after the original request was claimed that the sidebar also needs dark mode support.

## Requirements
- Sidebar must also respect the dark mode theme
- [any other new requirements]

---
*Source: Addendum to REQ-005. Original request: "dark mode should also affect the sidebar"*
```

Key rules for addendum REQs:
- **`addendum_to` field**: Links to the original REQ ID so the builder has context
- **Standalone**: The addendum must contain enough detail to be built independently — don't assume the builder has the original request open
- **Goes in the queue**: It's a normal pending REQ in `do-work/` and gets processed in order like everything else
- **Tell the user**: Explain that the original is already claimed/completed and this will be handled as a follow-up request

### Step 3: Clarify Only If Needed

Use your environment's ask-user prompt/tool ONLY when:
- Request is genuinely ambiguous (could mean two very different things)
- Similar request exists and it's unclear if this is new or a revision
- User's intent could conflict with existing requests

**DO NOT ask questions when:**
- You can reasonably infer the intent
- The request is simple and clear
- Technical implementation is unclear (that's for the building agent)

If your tool supports a structured question UI (e.g., multiple-choice), use it; otherwise ask a plain-text question.

Example good question:
```
You said "fix the search". I found an existing request about search performance (REQ-003).
Did you mean:
- Update that request (search performance)
- Something different (describe a new search issue)
```

Example unnecessary question (don't do this):
```
You want dark mode. Should it:
- Use system preferences
- Have its own toggle
- Support scheduled switching
```
^ These are implementation details for the building agent.

### Step 4: Handle Screenshots

**Image Cache Discovery (platform-specific)**: If your environment exposes a local cache for images, use it. Example: Claude Code caches images shared in conversation at `~/.claude/image-cache/[session-uuid]/[number].png`. Use your tool's attachment APIs or cache paths when available.

If the user passes a screenshot:

1. **Find the cached/attached image**: Use your tool's attachment UI or image cache (Claude Code path above). If you have a direct file path from the tool, use that.
2. **Verify it's the right image**: Use your tool's image viewing capability on the `.png` file to confirm it matches what the user shared
3. **Copy to UR assets**: `cp ~/.claude/image-cache/[uuid]/[n].png do-work/user-requests/UR-[num]/assets/REQ-[num]-[slug].png`
4. **Reference in request file**: Point to `do-work/user-requests/UR-[num]/assets/REQ-[num]-[slug].png` in the Assets section
5. **Still write a description**: Even with the file saved, include a thorough text description for searchability and context

**Finding the right image (Claude Code example):**
```bash
# List recent image cache sessions
find ~/.claude/image-cache -name "*.png" -exec ls -la {} \;

# Images are numbered in order shared (1.png, 2.png, etc.)
```

**Fallback** if cache is empty or images can't be found:
- Write a detailed description as the primary record
- Ask the user to provide a file path or save the image to `do-work/user-requests/UR-NNN/assets/` if needed

When describing screenshots, be thorough - this is the primary record:
- **What it shows**: UI state, screen area, dialog, error message, etc.
- **Visual layout**: Where elements are positioned relative to each other
- **All visible text**: Labels, buttons, headings, error text - quote exactly
- **What the user is pointing out**: Infer from context what's relevant
- **UI state**: Selected items, toggle states, hover states, etc.
- **Problems visible**: Misalignment, missing labels, redundant elements

Example good description:
```
Screenshot shows settings panel with:
- "Featured Items" section heading (bold, ~14px)
- "Show Featured Item" label with toggle switch (enabled/blue) on same line
- Dropdown below showing "1 hour" - NO LABEL explaining what this controls
- "Refresh Featured Items" button at bottom
Problem: The dropdown's purpose is unclear without a label.
```

Example bad description:
```
Screenshot of settings with a dropdown.
```

### Step 5: Write Request Files

#### Simple Mode

**1. Create the User Request (UR) folder:**
   a. Determine the next UR number (check `do-work/user-requests/` and `do-work/archive/UR-*/` for highest existing number)
   b. Create `do-work/user-requests/UR-NNN/input.md` with the verbatim user input (minimal format — see UR input.md Format above)
   c. Leave the `requests` array empty initially — you will fill it in step 3

**2. Create REQ files** (one per distinct request):
   a. Determine the next REQ number (check `do-work/`, `working/`, and `archive/` for highest existing number)
   b. Create a slug from the request (lowercase, hyphens, 3-4 words max)
   c. Generate the current ISO 8601 timestamp for `created_at`
   d. Write the file using the **simple request format**
   e. **Set `user_request: UR-NNN`** in frontmatter — this links the REQ back to its UR
   f. Keep the original verbatim request in the Source field

**3. Link them together:**
   a. Update the UR's `requests` array with all created REQ IDs
   b. Verify every REQ file has `user_request: UR-NNN` in its frontmatter

#### Complex Mode

For complex, multi-feature requests:

**1. Create the User Request (UR) folder first:**

1. Determine the next UR number (check `do-work/user-requests/` and `do-work/archive/UR-*/`)
2. Create `do-work/user-requests/UR-NNN/`
3. Create `do-work/user-requests/UR-NNN/assets/` (for screenshots/attachments)
4. Write `do-work/user-requests/UR-NNN/input.md`:

```yaml
---
id: UR-001
title: [Descriptive name for this batch]
created_at: 2025-01-26T10:00:00Z
requests: []  # Will fill in after creating requests
word_count: [count words in original input]
---
```

- Include a brief summary (2-3 sentences)
- Leave the `requests` array empty initially
- **Paste the FULL verbatim input** in the "Full Verbatim Input" section
- Do NOT edit, clean up, or summarize the verbatim input

**2. Identify all distinct features/requests:**
- Read through the input carefully
- List each distinct feature, component, or deliverable
- Note dependencies between them
- Note shared constraints or requirements

**3. Create individual request files:**

For EACH identified feature:
1. Determine the next REQ number
2. Create using the **complex request format**
3. Set `user_request` to the UR identifier (e.g., `UR-001`)
4. Set `related` to other REQ IDs in this batch
5. Set `batch` to a short name for this group

**Critical: Detailed Requirements section**

This is where lossiness happens. For each request:
- Extract EVERY requirement from the original input that applies to THIS feature
- **DO NOT SUMMARIZE** - use the user's words or close paraphrases
- Include specific values, constraints, conditions
- Include edge cases and error handling requirements
- Include "must", "should", "never" statements
- If something might apply, include it (let builder filter)

**4. Update the UR input.md:**
- Go back and fill in the `requests` array with all created REQ IDs
- Update the "Extracted Requests" table

**4.5. Identify Batch-Level Concerns:**
- After creating all REQs, identify any requirements that apply to the BATCH as a whole, not individual REQs
- Add these to the UR's input.md as a "Batch Constraints" section
- Examples: sequencing ("make sure everything's stable first"), shared design principles, performance budgets, user tone signals ("keep it simple," "don't over-engineer")
- These should also appear in each relevant REQ's Constraints section so builders see them without needing to read the context doc

**5. Verify completeness:**
- Re-read the original input
- Check that every requirement appears in at least one request file
- Check that every REQ captures relevant UX/interaction details (e.g., "auto-scroll to current file," "collapse on click," "highlight active item" type behaviors) — these are easy to drop
- Check that cross-cutting/batch concerns from step 4.5 appear in every relevant REQ's Constraints section
- Check that the user's intent signals are preserved — not just the WHAT, but the HOW-FIRMLY (exploratory vs firm, latitude given, scope cues)
- If something doesn't fit any request, either:
  - Create another request for it, OR
  - Add it to the most relevant request's "Context" section

**Frontmatter examples:**

Simple:
```yaml
---
id: REQ-004
title: Add keyboard shortcuts
status: pending
created_at: 2025-01-26T14:30:00Z
user_request: UR-003
---
```

Complex:
```yaml
---
id: REQ-012
title: OAuth login flow
status: pending
created_at: 2025-01-26T14:30:00Z
user_request: UR-005
related: [REQ-013, REQ-014, REQ-015]
batch: auth-system
---
```

### Step 5.5: Verify Requests

**[Mandatory step -- runs automatically after file creation]**

Verify the REQ files you just created against the UR's verbatim input. Fix any gaps. Store the results. Do not ask the user for permission — just fix and report.

**Skip condition:** If the user's input included "skip verification" or similar language, skip this step entirely.

**1. Enumerate source items:**

Re-read the UR's verbatim input. Extract a numbered list of every discrete requirement, constraint, behavior, UX detail, intent signal, and edge case the user mentioned. One item per line. If they said it, it counts — even passing mentions.

**2. Map each item to the REQs:**

For each enumerated item, find where it appears in the REQ files you just created. Classify each:
- **Full** -- present with appropriate detail
- **Partial** -- mentioned but missing specifics
- **Missing** -- not in any REQ

**3. Calculate coverage:**

Coverage % = (full + 0.5 x partial) / total x 100

**4. Auto-fix gaps (do not ask -- just fix):**

For each missing or partial item, edit the appropriate REQ file directly:
- Add missing items as bullet points in the most relevant section
- Expand partial items with the missing detail
- Don't invent requirements — only add what the user actually said

**5. Store results — append to each REQ file:**

```markdown
## Verification

**Source**: UR-NNN/input.md
**Pre-fix coverage**: 85% (17/20 items)
**Post-fix coverage**: 100% (20/20 items)

### Coverage Map

| # | Item | REQ Section | Status |
|---|------|-------------|--------|
| 1 | [item from input] | REQ-NNN [section] | Full |
| 2 | [item from input] | REQ-NNN [section] | Partial -> Fixed |
| 3 | [item from input] | -- | Missing -> Fixed |

### Fixes Applied

- REQ-NNN: Added "[requirement]" to [section]
- REQ-NNN: Expanded "[requirement]" with [detail]

*Verified by verify-request action*
```

See [verify-request action](./verify-request.md) for the full protocol (used when running verification manually via `do work verify`).

### Step 6: Report Back

**BEFORE reporting: Check that every REQ file has a `## Verification` section.** If any REQ you just created does not have one, STOP — go back to Step 5.5 and run verification now. Do not report back without verification results. The only exception is if the user said "skip verification."

After creating files, give a brief summary:
- What files were created
- Any existing requests that were updated
- Any requests that were skipped (duplicates)

Keep it concise. Don't explain your reasoning unless asked.

#### Include Verification Coverage

Since verify-request runs automatically in Step 5.5, include the coverage results in your report. After listing the created files, add the verification summary:

```
Verification: UR-NNN
  Coverage: 95% (19/20 items) -> 100% after fixes
  Fixed: 1 item in REQ-005
```

If verification was skipped (user said "skip verification"), note it:

```
Verification: skipped (user request)
```

If the pre-fix coverage was below 75%, call it out so the user knows significant gaps were found and fixed:

> Coverage was 65% on first pass -- several requirements from your input were missing from the REQs. Auto-fixed all gaps. You can run `/do-work verify` again to review the fixes.

### STOP After Capture

**The do action ends here.** After reporting back to the user, you are done. Do not proceed to process the queue, start implementation, or transition into the work action.

**Final check before stopping:** Every REQ file you created MUST have a `## Verification` section appended to it. If any REQ is missing this section, you skipped Step 5.5. Go back and run it now — enumerate items from the UR input, map them to the REQ, calculate coverage, fix gaps, and append the verification section. This is not optional.

This is a hard boundary:
- **Do NOT** report back without verification results on every REQ file
- **Do NOT** check for pending requests and start working on them
- **Do NOT** offer to "go ahead and start building" unless the user explicitly asked for that
- **Do NOT** treat capture as step one of a capture-then-execute pipeline
- **DO** let the user decide when to run `do work run` (or equivalent)

The only exception: if the user's original input explicitly combined capture and execution (e.g., "add this and start working on it", "capture these and run the queue"). Short of that, capture is the complete action.

### Do Action Checklist

Use this to verify you haven't skipped a step:

```
□ Parse input — single vs multiple requests (Step 1)
□ Assess complexity — simple or complex mode (Step 1.5)
□ Check for existing requests — duplicates, addendums (Step 2)
□ Clarify only if genuinely ambiguous (Step 3)
□ Handle screenshots if present (Step 4)
□ Create UR folder with input.md (Step 5)
□ Create REQ file(s) with user_request: UR-NNN in frontmatter (Step 5)
□ Update UR requests array with all REQ IDs (Step 5)
□ Run verify-request on created REQs — enumerate, map, fix, store (Step 5.5)
□ Report created files to user, include verification coverage (Step 6)
```

**Common mistakes:**
- Creating REQ files but forgetting the UR folder
- Creating the UR folder but not setting `user_request` in REQ frontmatter
- Skipping the UR for simple requests (it's required for ALL requests)
- Not updating the UR's `requests` array after creating REQs
- Skipping verify-request (it's mandatory unless the user said "skip verification")

## Examples

### Example 1: Simple Single Request

```
User: do work add keyboard shortcuts

Assistant: Created REQ-004-keyboard-shortcuts.md
```

### Example 2: Multiple Requests

```
User: do work add dark mode, also the search feels slow, and we need an export button

Assistant: Created:
- REQ-005-dark-mode.md
- REQ-006-search-performance.md
- REQ-007-export-button.md
```

### Example 3: Potential Duplicate

```
User: do work fix the lag when typing

Assistant: [Uses ask-user prompt/tool]
I found an existing request REQ-006 about search performance that mentions typing lag.
Is this:
- The same issue (I'll note you reported it again)
- A different typing lag issue (I'll create a new request)
```

### Example 4: Request with Screenshot

```
User: do work when I click here [screenshot] nothing happens

Assistant: Created:
- do-work/user-requests/UR-004/input.md (verbatim input)
- do-work/user-requests/UR-004/assets/REQ-008-button-click-fix.png
- do-work/REQ-008-button-click-fix.md
```

(Request file includes path to saved screenshot plus detailed description)

### Example 5: Enhancement to Queued Request (Addendum)

```
User: do work dark mode should also affect the sidebar

Assistant: [Checks existing — REQ-005-dark-mode.md is in do-work/ queue]
Found REQ-005-dark-mode.md (pending). Added addendum for sidebar requirement.
```

(The original request content stays intact. An Addendum section is appended with the new requirement and timestamp.)

### Example 5b: Enhancement to In-Flight Request (New Addendum REQ)

```
User: do work dark mode should also affect the sidebar

Assistant: [Checks existing — REQ-005-dark-mode.md is in do-work/working/]
REQ-005-dark-mode.md is currently being worked on. I can't modify it
while a builder is active. Creating a follow-up request instead.

Created:
- do-work/user-requests/UR-006/input.md (verbatim input)
- do-work/REQ-021-addendum-dark-mode-sidebar.md (addendum_to: REQ-005)
```

(A new REQ is created that references the original. The builder will pick it up after REQ-005 is done.)

### Example 6: Complex Multi-Feature Request

```
User: do work [15 minutes of detailed requirements about an authentication system
including OAuth, user profiles, session management, password reset,
security requirements, migration from old system, etc.]

Assistant: This is a complex request with multiple features. Creating UR folder
and individual requests...

Created:
- do-work/user-requests/UR-001/input.md (full verbatim input preserved, 1847 words)
- do-work/REQ-010-oauth-login.md (user_request: UR-001, related to REQ-011,012,013)
- do-work/REQ-011-user-profiles.md (user_request: UR-001, depends on REQ-010)
- do-work/REQ-012-session-management.md (user_request: UR-001, blocks REQ-010)
- do-work/REQ-013-password-reset.md (user_request: UR-001, alternative to REQ-010)

All requests reference UR-001 for full requirements.

Verification: UR-NNN
  Coverage: 92% → 100% after fixes (2 items fixed)
```

### Example 7: Detecting Complexity

```
User: do work I need a new dashboard. It should have a summary card at the top
showing total users, active sessions, and revenue. Below that, a chart
showing trends over the last 30 days - make sure it's interactive so users
can hover for details. The chart should support different time ranges.
On the right side, show a feed of recent activity. Users should be able to
filter the activity by type. Oh and the whole thing needs to work on mobile,
so the layout should stack vertically on small screens. Also add a date
range picker that affects all the widgets.

Assistant: [Detects: multiple components, specific requirements, responsive design
constraints, interactive features → Complex mode]

Created:
- do-work/user-requests/UR-002/input.md (preserves full input)
- do-work/REQ-014-dashboard-summary-cards.md (user_request: UR-002)
- do-work/REQ-015-dashboard-trend-chart.md (user_request: UR-002)
- do-work/REQ-016-dashboard-activity-feed.md (user_request: UR-002)
- do-work/REQ-017-dashboard-date-picker.md (user_request: UR-002)
- do-work/REQ-018-dashboard-responsive-layout.md (user_request: UR-002)

Each request includes full detailed requirements and references UR-002.

Verification: UR-NNN
  Coverage: 92% → 100% after fixes (2 items fixed)
```

## What NOT To Do

**For all requests (simple and complex):**
- **Don't create REQ files without a UR folder** — every invocation creates both, linked via `user_request` frontmatter
- **Don't skip the UR for simple requests** — even "add dark mode" gets a UR folder with `input.md`
- **Don't skip the `user_request` field in REQ frontmatter** — this is the link back to the source of truth
- Don't ask about implementation details
- Don't create multi-page PRDs for **simple** requests
- Don't refuse to create a request because it's "too vague" - capture what was said
- Don't merge obviously distinct requests into one file
- Don't make the user wait for questions you could answer yourself
- Don't add requirements the user didn't mention

**For complex requests specifically:**
- **Don't summarize detailed requirements** - preserve the user's exact words
- **Don't drop edge cases or constraints** - if the user mentioned it, capture it
- **Don't assume something is obvious** - write it down explicitly
- **Don't split related requirements** across unrelated requests - keep context together
- **Don't "clean up" the verbatim input** - typos, rambling, and all

## Edge Cases

**User says something is broken but doesn't say what:**
Create the request anyway with what they said. The building agent or a follow-up conversation can clarify.

**User references something from earlier conversation:**
Include that context in the request file.

**User gives a very long, detailed request:**
Switch to complex mode. Create a UR folder with the full verbatim input in input.md. Split into multiple requests, each referencing the UR.

**Request seems impossible or contradictory:**
Not your call. Capture it. The building agent will figure it out or ask. For complex requests, note contradictions in the "Open Questions" section.

**Requirement applies to multiple features:**
Include it in ALL relevant request files. Duplication is better than losing it.

**User changes their mind mid-request:**
Capture the final decision, but note the evolution in the UR's input.md. The builder might need to understand why.

**Features have circular dependencies:**
Note the dependencies in both request files. The builder will work out the sequencing.

**Some requirements are vague, others specific:**
Capture both. Vague ones go in as-is; the builder can ask for clarification. Don't try to make vague requirements more specific.

**User mentions something once in passing:**
Capture it. If they said "oh and it should probably work offline too" - that's a requirement, even if brief.
