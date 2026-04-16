# Phase Checklist

Quick reference for algorithm phases. Use for rapid assessment during execution.

---

## OBSERVE ✓

```
□ Read relevant files (not skim)
□ Search for patterns/prior art
□ Document constraints
□ Note dependencies
□ Identify what's working
```

**Exit:** Can answer "What exists? What are the constraints?"

---

## THINK ✓

```
□ Generate 2+ approaches
□ List pros/cons for each
□ Challenge assumptions
□ Consider failure modes
□ Identify unknowns
```

**Exit:** Can justify chosen approach with rationale.

---

## PLAN ✓

```
□ Break into discrete steps
□ Order by dependencies
□ Set checkpoints
□ Note blockers
□ Estimate complexity
```

**Exit:** Have concrete, actionable steps.

---

## BUILD ✓

```
□ Define measurable criteria
□ Set pass/fail thresholds
□ Specify verification methods
□ Ensure independence
□ Save ISC table
```

**Exit:** ISC table complete and saved.

---

## EXECUTE ✓

```
□ Follow plan steps
□ Track with TodoWrite
□ Note deviations
□ Capture findings
□ Complete all steps
```

**Exit:** All planned work complete (code written).

---

## VERIFY ✓

```
□ Run all ISC verifications
□ Update results (✅/❌/⚠️)
□ Note failures
□ Check edge cases
□ Be skeptical
```

**Exit:** All criteria evaluated.

---

## LEARN ✓

```
□ Document what worked
□ Document what didn't
□ Identify patterns
□ Note for future
□ Save to MEMORY/Learning/
```

**Exit:** Insights captured and stored.

---

## Effort-Based Shortcuts

| Level | Skip |
|-------|------|
| TRIVIAL | All phases—just do it |
| SIMPLE | OBSERVE, THINK → light PLAN |
| MODERATE | Brief each phase |
| COMPLEX | Full each phase |
| DETERMINED | Full + iterate |

---

## Red Flags

🚩 **In OBSERVE:** Not reading files, just assuming
🚩 **In THINK:** Only one approach considered
🚩 **In PLAN:** Vague steps like "implement feature"
🚩 **In BUILD:** Unmeasurable criteria like "works well"
🚩 **In EXECUTE:** Skipping steps, not tracking
🚩 **In VERIFY:** Not running actual tests
🚩 **In LEARN:** Skipping this phase entirely

---

## State File

Location: `~/.claude/MEMORY/State/algorithm-state.json`

```json
{
  "current_task": "slug",
  "current_phase": "PHASE",
  "effort_level": "LEVEL",
  "isc_path": "path/to/isc.md"
}
```
