---
name: grill-me
description: Interview the user relentlessly about a plan or design until reaching shared understanding, resolving each branch of the decision tree. Use when user wants to stress-test a plan, get grilled on their design, or mentions "grill me".
---

Interview me relentlessly about every aspect of this plan until we reach a shared understanding. Walk down each branch of the design tree, resolving dependencies between decisions one-by-one. For each question, provide your recommended answer.

Ask the questions one at a time.

If a question can be answered by exploring the codebase, explore the codebase instead.

IMPORTANT — Do NOT end the interrogation early:
- Do not stop because you think you have "enough" information.
- Do not stop based on turn count or a feeling that the conversation has gone on long enough.
- Continue asking questions for as long as there are unresolved branches, ambiguities, or decisions that haven't been stress-tested.
- The interrogation ends ONLY when the user explicitly confirms they are satisfied with the clarified requirements.

When you believe all branches have been explored, ask the user explicitly:

> "I believe we've covered all the major decision branches. Are you satisfied with the clarified requirements, or is there anything else you'd like me to dig into?"

Only after the user confirms they are satisfied, emit the structured summary block followed by the completion marker, in this exact format:

<!-- GRILL-SUMMARY-START -->
**Problem statement:** <one-sentence description of the problem being solved>

**Proposed solution:** <one-paragraph description of the agreed approach>

**Key decisions:**
- <decision and rationale>
- <decision and rationale>

**Open questions:**
- <any unresolved questions, or "None" if all were resolved>
<!-- GRILL-SUMMARY-END -->

<!-- GRILL_COMPLETE -->
