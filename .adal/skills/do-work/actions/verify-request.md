# Verify Request Action

> **Part of the do-work skill.** Evaluates REQ files against their originating User Request (UR) to find and fix coverage gaps. Runs automatically after the do action captures requests, or manually via `do work verify`.

A coverage analysis system that enumerates items from the original user input and maps each one to the extracted REQ files. Finds gaps, auto-fixes them, and stores the coverage metrics for traceability.

## Coverage Analysis Protocol

> This protocol is shared across all verify actions in do-work. The same enumeration-and-mapping approach is used by verify-request (input -> REQs) and verify-plan (REQ -> plan).

### The Protocol

1. **Enumerate** -- Parse the source document into a numbered list of discrete, verifiable items. Each item is one requirement, constraint, behavior, or detail that can be independently checked.
2. **Map** -- For each source item, search the target document(s) for coverage. Classify each as:
   - **Full** -- The item appears in the target with sufficient detail
   - **Partial** -- The item is mentioned but missing detail, specificity, or context
   - **Missing** -- The item does not appear in the target at all
3. **Calculate** -- Coverage % = (full + 0.5 x partial) / total x 100
4. **Fix** -- For missing and partial items, update the target document to include them. Don't invent requirements -- only add what the source explicitly contains.
5. **Recalculate** -- After fixes, recalculate coverage. Should be at or near 100%.
6. **Store** -- Append a verification section to the target document with the coverage map, metrics, and list of fixes applied.

## When This Runs

- **Automatically** after the do action creates REQ files (as part of the capture workflow)
- **Manually** when the user invokes `do work verify`, `do work check`, `do work evaluate`
- **Skippable** if the user says "skip verification" in their request

## Workflow

### Step 1: Find the Target UR

1. **If running automatically after do action**: Use the UR that was just created
2. **If user specifies a UR** (e.g., "verify UR-003"): Use that UR directly
3. **If user specifies a REQ** (e.g., "verify REQ-018"): Read the REQ's `user_request` field to find the UR
4. **If no target specified**: Find the most recent UR folder in `do-work/user-requests/` (highest UR number)

**Legacy support:** If the user points to a REQ with `context_ref` instead of `user_request`, read the referenced CONTEXT file from `do-work/assets/` and use its verbatim input as the source of truth.

### Step 2: Read the Original Input

1. Read `do-work/user-requests/UR-NNN/input.md`
2. Extract the full verbatim input section -- this is the source of truth
3. Note the `requests` array to know which REQs to evaluate

### Step 3: Read All Related REQs

1. Find all REQ files listed in the UR's `requests` array
2. Check `do-work/`, `do-work/working/`, and `do-work/archive/` for each
3. Read the full content of each REQ file

### Step 4: Enumerate Source Items

Parse the UR's verbatim input into a numbered list of discrete items. Each item is independently verifiable:

- **Requirements** -- specific features, behaviors, or outcomes requested
- **Constraints** -- limitations, restrictions, or conditions mentioned
- **UX/Interaction details** -- how things should look, feel, or behave
- **Intent signals** -- certainty level, scope cues, latitude given to the builder
- **Edge cases** -- error handling, fallbacks, or specific scenarios mentioned

**Guidelines for enumeration:**

- One item per line, numbered sequentially
- Each item should be independently checkable
- Don't merge related items -- if the user said two things, that's two items
- Don't split single concepts into sub-items -- if "OAuth with Google and GitHub" is one thought, it's one item
- Quote the user's words where possible for traceability
- Include passing mentions -- if they said it, it counts

### Step 5: Map Items to REQs

For each enumerated item, search all related REQ files:

1. Identify which REQ should contain it (by topic/feature alignment)
2. Find where it appears (which section: What, Detailed Requirements, Constraints, Builder Guidance, etc.)
3. Classify coverage:
   - **Full** -- The item is present with appropriate detail
   - **Partial** -- The item is present but missing specifics (e.g., "supports OAuth" but missing "with PKCE")
   - **Missing** -- The item does not appear in any REQ

### Step 6: Calculate Coverage

Apply the formula: **Coverage % = (full + 0.5 x partial) / total x 100**

Round to the nearest integer. This is the **pre-fix** coverage score.

### Step 7: Auto-Fix Gaps

**Fix the gaps directly. Do not ask the user for permission — just make the edits.** The default behavior is to fix, not to report and wait. The coverage map in Step 8 documents exactly what was changed, so nothing is hidden.

For each missing or partial item:

1. Determine the most appropriate REQ file (by topic alignment)
2. Determine the most appropriate section (Detailed Requirements for requirements, Constraints for constraints, Builder Guidance for intent signals, etc.)
3. **Edit the REQ file now** -- add the missing content:
   - **Missing items**: Add a new bullet point in the appropriate section
   - **Partial items**: Expand the existing bullet with the missing detail
4. If no existing REQ is appropriate for an item, note it as a recommendation for a new REQ (don't create REQs -- that's the do action's job)

**Don't expand beyond the source.** Only add what the user actually said. This is coverage repair, not requirements expansion.

**Don't ask.** Don't say "Want me to apply these fixes?" or "Should I update the REQ?" Just do it. The whole point of auto-fix is that it's automatic.

### Step 8: Recalculate and Store

1. **Recalculate coverage** after fixes (post-fix score)
2. **Append a verification section** to each REQ file that was evaluated:

```markdown
## Verification

**Source**: UR-NNN/input.md
**Pre-fix coverage**: 85% (17/20 items)
**Post-fix coverage**: 100% (20/20 items)

### Coverage Map

| # | Item | REQ Section | Status |
|---|------|-------------|--------|
| 1 | OAuth with Google and GitHub | REQ-005 Detailed Requirements | Full |
| 2 | PKCE for Google OAuth | REQ-005 Detailed Requirements | Partial -> Fixed |
| 3 | Mobile responsive layout | -- | Missing -> Fixed |
| ... | ... | ... | ... |

### Fixes Applied

- REQ-005: Expanded OAuth requirement to specify PKCE for Google
- REQ-005: Added "mobile responsive layout" to Constraints

*Verified by verify-request action*
```

3. **Print summary to terminal:**

```
Verification: UR-NNN
  Items: 20 enumerated from original input
  Pre-fix: 85% (17 full, 2 partial, 1 missing)
  Fixed: 3 items across 2 REQs
  Post-fix: 100%
```

## Scoring Guidelines

- **90-100%** pre-fix: Excellent capture -- minimal fixes needed
- **75-89%** pre-fix: Good capture -- some details dropped, auto-fixed
- **50-74%** pre-fix: Significant gaps -- important requirements were missing
- **Below 50%** pre-fix: Major gaps -- REQs needed substantial additions

## Legacy REQ Handling

For REQs created before the UR system:
- They won't have `user_request` in frontmatter
- They may reference `assets/CONTEXT-*.md` via `context_ref`
- They won't have a Builder Guidance section
- Score them the same way, but note that missing Builder Guidance is expected for legacy REQs
- If the user wants to verify legacy REQs and has the original CONTEXT file, use its verbatim input

## What NOT To Do

- Don't expand requirements beyond what the user said -- you're checking coverage, not inventing features
- Don't penalize REQs for missing details the user never mentioned
- Don't treat implementation details as gaps -- those are for the builder to decide
- Don't create new REQ files -- if coverage requires a new REQ, note the recommendation but let the do action handle it
- Don't modify files in `working/` or `archive/` -- verification only updates REQ files in the `do-work/` queue
