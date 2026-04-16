# Execute Algorithm Workflow

Full algorithm execution template for complex tasks.

## Pre-Flight Check

Before starting, classify the effort level:

| If the task is... | Effort Level | Algorithm Depth |
|-------------------|--------------|-----------------|
| Single obvious action | TRIVIAL | Just do it |
| Few steps, clear path | SIMPLE | PLAN → EXECUTE → VERIFY |
| Multiple steps, decisions needed | MODERATE | Full algorithm, brief |
| Many steps, significant decisions | COMPLEX | Full algorithm, thorough |
| Novel problem, research needed | DETERMINED | Full with iteration |

---

## Phase 1: OBSERVE

**Goal:** Understand current state before proposing changes.

### Checklist
- [ ] Read relevant files (don't skim—actually read)
- [ ] Search for related patterns in codebase
- [ ] Check for existing solutions or prior attempts
- [ ] Document constraints and dependencies
- [ ] Note what's working that shouldn't be broken

### Output Format
```markdown
## OBSERVE Summary

**Context gathered:**
- [Key file 1]: [What it does, relevant parts]
- [Key file 2]: [What it does, relevant parts]

**Constraints identified:**
- [Constraint 1]
- [Constraint 2]

**Dependencies:**
- [What this touches/affects]

**Prior art:**
- [What's been tried, what exists]
```

### Transition Criteria
Move to THINK when you can answer:
- What exists currently?
- What are the hard constraints?
- What would success look like?

---

## Phase 2: THINK

**Goal:** Generate multiple approaches, not just the first idea.

### Checklist
- [ ] Brainstorm at least 2-3 distinct approaches
- [ ] For each approach, identify pros/cons
- [ ] Challenge your assumptions
- [ ] Consider edge cases and failure modes
- [ ] Identify what you don't know

### Output Format
```markdown
## THINK Summary

**Approach A: [Name]**
- Pros: [List]
- Cons: [List]
- Risk: [Low/Medium/High]

**Approach B: [Name]**
- Pros: [List]
- Cons: [List]
- Risk: [Low/Medium/High]

**Unknowns:**
- [What we don't know yet]

**Recommendation:** [Approach] because [rationale]
```

### Transition Criteria
Move to PLAN when you can justify your chosen approach.

---

## Phase 3: PLAN

**Goal:** Sequence the work into concrete steps.

### Checklist
- [ ] Break work into discrete steps
- [ ] Order steps logically (dependencies first)
- [ ] Identify checkpoints/milestones
- [ ] Note potential blockers
- [ ] Estimate relative complexity of each step

### Output Format
```markdown
## PLAN Summary

**Steps:**
1. [Step 1] - [complexity: low/med/high]
2. [Step 2] - [complexity: low/med/high]
3. [Step 3] - [complexity: low/med/high]

**Checkpoints:**
- After step [N]: Verify [what]

**Potential blockers:**
- [Blocker 1]: Mitigation [how]
```

### Transition Criteria
Move to BUILD when you have concrete, actionable steps.

---

## Phase 4: BUILD (Define Success)

**Goal:** Create ISC table defining measurable success criteria.

### Checklist
- [ ] Define measurable criterion for each major outcome
- [ ] Set specific pass/fail thresholds
- [ ] Specify verification method for each
- [ ] Ensure criteria are independent
- [ ] Save ISC table to MEMORY/Work/

### Output Format
See `workflows/isc-table.md` for full template.

```markdown
## ISC Table: [Task Name]

| # | Criterion | Metric | Target | Verification Method | Result |
|---|-----------|--------|--------|---------------------|--------|
| 1 | ... | ... | ... | ... | ⏳ |
```

### Transition Criteria
Move to EXECUTE when ISC table is complete and saved.

---

## Phase 5: EXECUTE

**Goal:** Do the work according to plan.

### Checklist
- [ ] Follow planned steps in order
- [ ] Use TodoWrite to track progress
- [ ] Note deviations and why
- [ ] Capture unexpected findings
- [ ] Don't skip steps (note if you do)

### Execution Notes
```markdown
## EXECUTE Log

**Step 1:** [Description]
- Status: [Done/In Progress/Blocked]
- Notes: [Any deviations or findings]

**Step 2:** [Description]
- Status: [Done/In Progress/Blocked]
- Notes: [Any deviations or findings]

**Deviations from plan:**
- [What changed and why]
```

### Transition Criteria
Move to VERIFY when all planned work is complete (code written, not just "feels done").

---

## Phase 6: VERIFY

**Goal:** Test against ISC criteria with skeptical evaluation.

### Checklist
- [ ] Run each verification method from ISC
- [ ] Update ISC table with results (✅/❌/⚠️)
- [ ] For failures, note what went wrong
- [ ] Look for edge cases not in ISC
- [ ] Be skeptical—assume something's wrong

### Output Format
```markdown
## VERIFY Results

| # | Criterion | Result | Notes |
|---|-----------|--------|-------|
| 1 | [Criterion] | ✅ | [Passed as expected] |
| 2 | [Criterion] | ❌ | [What failed, why] |
| 3 | [Criterion] | ⚠️ | [Partial, what's missing] |

**Overall:** [PASS / FAIL / PARTIAL]

**If FAIL/PARTIAL:** Return to [PHASE] to address [issue]
```

### Transition Criteria
Move to LEARN when all criteria are evaluated (not necessarily passed).

---

## Phase 7: LEARN

**Goal:** Extract insights for continuous improvement.

### Checklist
- [ ] Document what worked well
- [ ] Document what didn't work
- [ ] Identify patterns (positive and negative)
- [ ] Note anything to remember for future
- [ ] Save learning to MEMORY/Learning/

### Output Format
```markdown
## LEARN Summary

**What worked:**
- [Effective approach 1]
- [Effective approach 2]

**What didn't work:**
- [Problem 1]: [Why, how to avoid]
- [Problem 2]: [Why, how to avoid]

**Patterns identified:**
- [Recurring pattern, positive or negative]

**For next time:**
- [Key insight to remember]
```

### Storage
Save to: `~/.claude/MEMORY/Learning/[PHASE]/[date]_[topic].md`

---

## State Tracking

Throughout execution, maintain state in:
```json
// ~/.claude/MEMORY/State/algorithm-state.json
{
  "current_task": "task-name-slug",
  "current_phase": "EXECUTE",
  "phase_history": [
    {"phase": "OBSERVE", "started": "timestamp", "completed": "timestamp"},
    {"phase": "THINK", "started": "timestamp", "completed": "timestamp"},
    ...
  ],
  "isc_path": "MEMORY/Work/task-name-slug/isc.md",
  "effort_level": "COMPLEX"
}
```

---

## Quick Reference

| Phase | Key Question | Primary Output |
|-------|--------------|----------------|
| OBSERVE | What exists? | Context summary |
| THINK | What are the options? | Approach comparison |
| PLAN | What's the sequence? | Step list |
| BUILD | What's success? | ISC table |
| EXECUTE | Is it done? | Implementation |
| VERIFY | Did it work? | Test results |
| LEARN | What did we learn? | Insights |
