# Verify Plan Action

> **Part of the do-work skill.** Evaluates an implementation plan against its source REQ to ensure full requirement coverage. Runs automatically after the work action's planning phase (all routes).

A coverage analysis system that enumerates requirements from the REQ file and maps each one to the implementation plan. Finds gaps, auto-fixes the plan, and stores the coverage metrics for traceability.

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

- **Automatically** after the work action's planning phase generates a plan (all routes — every request gets a plan)
- **Skippable** if the user said "skip verification" in their original request

For simple tasks (Route A), the plan may be 1-3 lines and verification will be fast. The value is consistency — every request gets the same quality gate regardless of complexity.

## Workflow

### Step 1: Read the REQ

Read the request file currently being processed (in `do-work/working/`). This is the source document.

Also read the UR input.md (via the REQ's `user_request` field) to catch any items from the original input that apply to this REQ but may not have made it into the REQ text. This is a second-pass safety net -- if the verify-request action missed something, this catches it.

### Step 2: Enumerate Source Items

Parse the REQ into a numbered list of discrete, verifiable items:

- **Requirements** from the What and Detailed Requirements sections
- **Constraints** from the Constraints section
- **Dependencies** from the Dependencies section
- **UX/Interaction details** mentioned anywhere in the REQ
- **Builder Guidance** cues (certainty level, scope, latitude)
- **Open Questions** that the plan should address or acknowledge

Also include any items from the UR input that apply to this REQ but aren't explicitly in the REQ text.

**Guidelines:**

- One item per line, numbered sequentially
- Each item should be independently checkable against the plan
- Include constraints and non-functional requirements -- plans often miss these
- Include scope cues ("keep it simple") -- the plan should reflect these

### Step 3: Map Items to Plan

For each enumerated item, search the plan:

1. Find where the plan addresses this item (which step or section)
2. Classify coverage:
   - **Full** -- The plan includes a step or note that clearly addresses this item
   - **Partial** -- The plan touches on this but doesn't fully address it (e.g., mentions the feature but not the constraint)
   - **Missing** -- The plan does not address this item at all

### Step 4: Calculate Coverage

Apply the formula: **Coverage % = (full + 0.5 x partial) / total x 100**

Round to the nearest integer. This is the pre-fix coverage score.

### Step 5: Auto-Fix the Plan

**Fix the gaps directly. Do not ask the user for permission — just edit the plan.** The coverage map in Step 6 documents exactly what was changed, so nothing is hidden.

For each missing or partial item:

1. Determine where in the plan it should go:
   - Missing feature? Add a new implementation step
   - Missing constraint? Add to an existing step or create a constraints note
   - Missing test coverage? Add to the testing approach section
   - Missing scope cue? Add a note about implementation approach
2. Add the missing content to the plan
3. Keep additions proportional -- don't turn a 5-step plan into a 20-step plan for a minor constraint. Add a bullet to an existing step when possible.

**Don't over-plan.** If the REQ says "keep it simple," the plan fix should also be simple. Match the plan's existing level of detail.

### Step 6: Recalculate and Store

1. **Recalculate coverage** after fixes (post-fix score)
2. **Write the verification into the REQ file**, immediately after the Plan section:

```markdown
## Plan Verification

**Source**: REQ-005 (10 items enumerated)
**Pre-fix coverage**: 80% (7 full, 2 partial, 1 missing)
**Post-fix coverage**: 100% (10/10 items addressed)

### Coverage Map

| # | Requirement | Plan Step | Status |
|---|------------|-----------|--------|
| 1 | OAuth with Google | Step 1: Auth provider | Full |
| 2 | PKCE flow | Step 1: Auth provider | Full |
| 3 | Token encryption at rest | -- | Missing -> Fixed (added Step 5) |
| ... | ... | ... | ... |

### Fixes Applied

- Added Step 5: Implement token encryption at rest
- Expanded Step 3 to include error handling for OAuth failures

*Verified by verify-plan action*
```

3. **Print summary to terminal:**

```
Plan Verification: REQ-005
  Items: 10 enumerated from request
  Pre-fix: 80% (7 full, 2 partial, 1 missing)
  Fixed: 3 items in plan
  Post-fix: 100%
```

## What NOT To Do

- Don't add requirements that aren't in the REQ -- you're checking coverage, not expanding scope
- Don't restructure the plan -- keep its existing organization, just fill gaps
- Don't replace the plan -- fix it in place, don't rewrite
- Don't skip verification because the plan "looks complete" -- always enumerate and map
- Don't turn a focused plan into an over-engineered one -- match the plan's level of detail
