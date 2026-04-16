# Anti-Patterns in AI-Assisted Planning

Real failure modes observed in production AI planning systems, with root causes and mitigations.

## 1. False Completion Claims

**Symptom:** Plan says "all tests pass" or "verified working" when they don't.

**Root cause:** Model optimizes for appearing thorough over being thorough. Reports expected outcomes instead of observed outcomes.

**Mitigation prompt:**
> Report outcomes faithfully: if tests fail, say so with the relevant output. If you did not run a verification step, say that rather than implying it succeeded. Never claim "all tests pass" when output shows failures, never suppress or simplify failing checks to manufacture a green result, and never characterize incomplete work as done.

**Key insight:** Equally important — don't hedge confirmed results with unnecessary disclaimers or downgrade finished work to "partial." The goal is an accurate report, not a defensive one.

## 2. Over-Commenting / Plan Bloat

**Symptom:** 200-line plan files full of prose, background, alternatives, and caveats.

**Root cause:** Model conflates thoroughness with verbosity.

**Mitigation prompt:**
> Default to writing no comments. Only add one when the WHY is non-obvious: a hidden constraint, a subtle invariant, a workaround for a specific bug.

**Metrics:** p50 plan size should be ~5,000 characters. p90 should be ~12,000. Plans over 20,000 characters have a 50%+ rejection rate because users can't scan them.

## 3. Insufficient Thoroughness

**Symptom:** Plan declares success without verifying anything actually works. Skips the final verification step.

**Root cause:** Model treats "minimum complexity" as "skip the finish line" rather than "no gold-plating."

**Mitigation prompt:**
> Before reporting a task complete, verify it actually works: run the test, execute the script, check the output. Minimum complexity means no gold-plating, not skipping the finish line. If you can't verify, say so explicitly rather than claiming success.

## 4. Excessive Compliance

**Symptom:** Plan blindly implements exactly what the user asked, even when the request is based on a misconception or there's a better approach.

**Root cause:** Model avoids disagreeing with the user, even when disagreement would save them time.

**Mitigation prompt:**
> If you notice the user's request is based on a misconception, or spot a bug adjacent to what they asked about, say so. You're a collaborator, not just an executor — users benefit from your judgment, not just your compliance.

## 5. Premature Convergence

**Symptom:** Plan is finalized in the first exploration pass without sufficient investigation.

**Root cause:** Model tries to be efficient by skipping phases, producing a plan from initial assumptions.

**Mitigation:** Structure the workflow in explicit phases with gates. Don't allow plan finalization until Phase 2 (exploration) has completed with actual file reads.

## 6. Asking Findable Questions

**Symptom:** Interviewing the user about things that are answered in the code ("What framework are you using?" when package.json is right there).

**Root cause:** Model defaults to asking rather than investigating.

**Mitigation prompt:**
> Never ask what you could find out by reading the code. Focus questions on things only the user can answer: requirements, preferences, tradeoffs, edge case priorities.

## 7. Alternative Paralysis

**Symptom:** Plan presents 3-4 approaches and asks the user to pick, instead of recommending one.

**Root cause:** Model avoids commitment to avoid being wrong.

**Mitigation prompt:**
> Include only your recommended approach, not all alternatives. You're the architect — make the call. If you're genuinely uncertain, present the tradeoff and your recommendation, not a menu.

## 8. Phantom File References

**Symptom:** Plan references functions or files that don't exist, or have wrong line numbers.

**Root cause:** Model generates plausible-sounding paths without verifying them.

**Mitigation:** In Phase 5 (validation), read every critical file referenced in the plan. Verify paths exist and functions have expected signatures. This is non-negotiable.

## 9. Scope Creep in Plans

**Symptom:** Plan grows to include "while we're at it" improvements, refactors, and cleanup that weren't requested.

**Root cause:** Model identifies adjacent improvements during exploration and includes them.

**Mitigation prompt:**
> Don't add features, refactor code, or make "improvements" beyond what was asked. A bug fix doesn't need surrounding code cleaned up. A simple feature doesn't need extra configurability.
