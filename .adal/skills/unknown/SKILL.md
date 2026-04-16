---
name: unknown
description: This skill should be used when the user provides a strategy, plan, or decision document and wants to surface hidden assumptions and blind spots using the Known/Unknown 4-quadrant framework. Trigger on "known unknown", "4분면 분석", "blind spots", "what am I missing", "뭘 놓치고 있지", "전략 점검", "가정 점검", "quadrant analysis". For requirement clarification use vague; for content-vs-form reframing use metamedium.
user-invocable: true
argument-hint: [strategy-topic-or-doc]
---

# Unknown: Strategy Blind Spot Analysis

Surface hidden assumptions and strategic blind spots using the Known/Unknown 4-quadrant lens.

## When to Use

- Strategy documents that look coherent but are hard to execute
- Plans with unclear risk boundaries
- Decision discussions where the team asks: "What are we missing?"

For requirement clarification, use **vague**. For content/form leverage decisions, use **metamedium**.

## Core Lens

Classify insights into four quadrants:

- **Known Knowns (KK)**: validated facts and working mechanisms
- **Known Unknowns (KU)**: explicit uncertainties requiring experiments
- **Unknown Knowns (UK)**: existing but underused assets/capabilities
- **Unknown Unknowns (UU)**: unobserved risks requiring early-warning antennas

Default resource split (adjustable):
- KK 60%: systematize
- KU 25%: experiment
- UK 10%: leverage
- UU 5%: install antennas

## Non-Negotiable Interaction Rule

Use **AskUserQuestion** for each round (R1/R2/R3). Ask with hypothesis options, not open free-text prompts.

## 3-Round Pattern

- **R1 (3-4 questions)**: broad scan across all quadrants
- **R2 (2-3 questions)**: drill into weakest link discovered in R1
- **R3 (2-3 questions, optional)**: execution detail for top priorities

Cap total questions at **7-10**.

## Protocol

### Phase 1: Intake

If a doc is provided, extract goals, assumptions, dependencies, and unstated constraints.

### Phase 2: Context Sweep

Scan project context (README, plans, prior notes) to identify likely UK candidates (assets the team has but is not using).

### Phase 3: Draft + R1

Create a provisional 4-quadrant draft, then run R1 AskUserQuestion (single batched call).

### Phase 4: R2 Deepening

Design R2 only from R1 responses:
- Compound bottlenecks
- Surprising answers
- "Other" selections

### Phase 5: R3 Execution (optional)

If needed, confirm owner, timeline, stop-criteria, and promotion conditions.

### Phase 6: Playbook Output

Produce a structured playbook using `references/playbook-template.md`.

## Rules

1. Hypotheses as options
2. R2 derives from R1, R3 derives from R2
3. Include both `what to start` and `what to stop`
4. Every KU gets promotion condition and kill condition
5. Prefer small experiments over large speculative plans

## Additional Resources

- `references/question-design.md`
- `references/playbook-template.md`
