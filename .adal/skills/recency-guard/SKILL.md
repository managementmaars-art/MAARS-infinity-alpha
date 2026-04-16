---
name: "recency-guard"
description: 'Validate answers whose value depends on current external facts. Use this skill whenever a response includes time-sensitive claims, rankings, recommendations, pricing, version status, policy changes, availability, or other facts that could have changed recently. Also use it when the user asks for a verified, fact-checked, or up-to-date answer. This skill runs a sequential validation pipeline: recency audit, claim stress-test, completeness check, and clarity pass. Skip it for purely creative writing, casual chat, or requests with no factual claims to verify.'
---

# Recency Guard

You are a response-validation skill for answers that depend on current external
facts. This skill does four things in order: **draft** a usable answer,
**verify** high-risk claims with web-capable subagents, **close** coverage gaps
from the user's request, and **polish** the final wording so uncertainty is
accurate but unobtrusive.

The user should receive only a clean final answer unless they explicitly ask for
the verification details.

## Inputs

| Input | Required | Example |
| ----- | -------- | ------- |
| `USER_REQUEST` | Yes | `"Compare the best React data-fetching libraries in 2026"` |
| `DRAFT_RESPONSE` | Yes | A provisional answer that still needs validation |
| `TODAYS_DATE` | Yes | `2026-04-06` |
| `RECENCY_RISK_HINT` | No | `"Pricing and release status matter most"` |

## Pipeline Overview

| Phase | Mode | Goal | Output |
| ----- | ---- | ---- | ------ |
| `Draft prep` | Inline | Create or inspect the draft before validation begins | Draft ready for verification |
| `Verify` | Subagents | Run the recency audit, then the claim stress-test | Claim-level revisions applied |
| `Completeness` | Inline | Ensure the answer covers the whole request | Missing items fixed or acknowledged |
| `Clarity` | Inline | Make the answer precise, readable, and useful | Final user-visible response |

Execution Steps below expand Phase 2 into two sequential subagent calls. Step 6
is cross-cutting repair policy rather than a separate pipeline phase. Do not
parallelize the subagents.

## Subagent Registry

| Subagent | Path | Purpose |
| -------- | ---- | ------- |
| `recency-checker` | `./subagents/recency-checker.md` | Verifies time-sensitive factual claims against current sources and returns only the claims that need revision, qualification, or removal |
| `claim-verifier` | `./subagents/claim-verifier.md` | Stress-tests the most decision-shaping claims for evidence strength, overstatement, and meaningful counterexamples |

To dispatch a subagent, read only the listed `.md` file for the step you are
about to run, launch it with the platform's subagent/task tool, pass the input
values as the job payload, and keep only the structured report it returns.

## How This Skill Works

Within this four-step flow, the orchestrator does two kinds of work: inline
drafting/editing and delegated verification. It drafts and polishes inline,
then decides which claims need fresh evidence, dispatches one subagent at a
time, and integrates only the verdicts that matter. Keep only the current
draft, the user's request, and a short list of unresolved claims in working
memory. The subagents do the web-heavy evidence gathering; the orchestrator
does not retain raw search results, full source dumps, or exploratory notes.

Use inline validation only when it directly improves the final answer. Web-heavy
fact checking and credibility pressure-tests are delegated because the
orchestrator needs concise findings, not the search process itself.

## Execution Steps

### 1. Prepare the draft

If no draft exists yet, write one first. This skill validates a concrete answer;
it does not replace answering the user.

Mark claims that are likely to need fresh evidence or careful wording:

- Version numbers, release status, deprecations, and compatibility claims
- Pricing, quotas, limits, policy changes, and availability
- Rankings, "best" recommendations, and popularity claims
- Benchmarks, adoption claims, and market comparisons
- Any statement the user is likely to act on directly

### 2. Dispatch `recency-checker`

Read `./subagents/recency-checker.md` only when you are ready to dispatch it.
Pass:

- `USER_REQUEST`
- `DRAFT_RESPONSE`
- `TODAYS_DATE`
- `RECENCY_RISK_HINT` if you have one

Apply only the changes it recommends. If it returns `FAIL`, revise the flagged
claims and rerun `recency-checker` on the updated draft until it returns `PASS`
or you hit the repair cap in Step 6. If it returns `PASS`, continue to Step 3.
Treat `Verified summary` as informational only; required edits appear under
`Flagged claims`.

### 3. Dispatch `claim-verifier`

Read `./subagents/claim-verifier.md` only when you are ready to dispatch it.
Pass:

- `USER_REQUEST`
- The revised `DRAFT_RESPONSE` from Step 2
- `TODAYS_DATE`

Apply only the claim-level changes it recommends. If it returns `FAIL`, revise
the flagged claims and rerun `claim-verifier` on the updated draft until it
returns `PASS` or you hit the repair cap in Step 6. If it returns `PASS`,
continue to Step 4.

### 4. Completeness check inline

Re-read the user's request word by word and confirm:

- Every requested deliverable is present
- Every sub-question has been answered
- Every explicit constraint, scope limit, and formatting instruction is honored
- Any genuinely unanswerable point is acknowledged instead of silently omitted

If the answer is still missing material the user asked for, fix that now. Partial
coverage is acceptable only when the user explicitly allowed it.

If this step adds a new time-sensitive claim, rerun `recency-checker` before
continuing. If it adds a new decision-shaping claim, rerun `claim-verifier`
after the recency pass. If both conditions apply, rerun both in that order,
subject to the repair cap in Step 6.

### 5. Clarity pass inline

Edit the answer so the user can act on it quickly:

- Put the bottom line near the top
- Define jargon only when the user needs it
- Remove filler, redundancy, and process narration
- Keep qualifiers proportional to evidence strength
- Prefer concrete wording over abstract phrasing

If this pass introduces a new factual claim that the user could act on, rerun
`recency-checker` for freshness and then `claim-verifier` for decision-shaping
claims when applicable before sending the answer, subject to the repair cap in
Step 6.

### 6. Fix loop and escalation

Use targeted repair cycles instead of rerunning the whole pipeline:

Any rerun of `recency-checker` or `claim-verifier` on the same draft counts
toward that subagent's repair budget, whether the rerun was triggered by `FAIL`
or by new claims introduced during completeness or clarity edits.

- If a subagent returns `FAIL`, fix only the flagged claims, then rerun that
  same subagent on the updated draft
- If a subagent returns `TOOLS_MISSING`, do not present the answer as freshly
  verified; qualify time-sensitive claims and explain the limitation if it
  materially affects the user's decision
- If a subagent returns `ERROR`, retry once with the same inputs; if the second
  attempt also errors, keep only clearly supported claims and surface the
  remaining uncertainty
- Do not run more than 2 repair cycles per subagent for the same draft. Count
  this as the initial review plus up to 2 additional reruns of that subagent,
  regardless of why they were needed. If uncertainty remains material after
  that, tell the user directly

## Integration Policy

When folding subagent findings back into the draft:

- `High` confidence claims can be stated directly
- `Med` confidence claims should usually carry light context such as
  `as of <date>`, `based on current documentation`, or a brief caveat
- `Low` confidence claims should be removed, replaced, or explicitly marked
  uncertain
- Do not merge subagent confidence labels into one blended score.
  `recency-checker` measures freshness; `claim-verifier` measures reasoning
  strength
- When both subagents touch the same claim, apply the stricter result. A
  required revision from either subagent wins, and user-visible certainty should
  reflect the weaker remaining confidence
- When sources conflict, prefer the higher-authority source and mention the
  conflict only if it materially changes the recommendation

Maintain a short internal list of claims that remain qualified or unresolved. If
the user explicitly asks for the verification reasoning, summarize only those
final claim-level findings rather than dumping the entire audit process.

## Output Rules

Produce a clean final answer that reads as if it were written correctly the
first time.

- Keep verification work invisible unless the user asks for it
- Mention evidence limits only when they affect the answer
- Use natural, local qualifiers instead of bolted-on disclaimer blocks
- Avoid headings such as `Final Answer` or `Validation Summary`

## Example

<example>
Input:
- `USER_REQUEST`: "What's the best TypeScript ORM right now for a greenfield SaaS?"
- `DRAFT_RESPONSE`: "Prisma is the best TypeScript ORM."

Flow:
1. Dispatch `recency-checker`.
2. It returns `FAIL` because "best" is overstated and recent releases changed
   the trade-offs.
3. Revise the draft to compare Prisma, Drizzle, and Kysely with date-aware
   qualifiers.
4. Dispatch `claim-verifier`.
5. It returns `FAIL` because the recommendation still reads as universal rather
   than context-dependent.
6. Reframe the answer around workload fit, ecosystem, and migration
   constraints.
7. Run the completeness and clarity checks, then send the final answer.

User-visible result:
"Prisma is still the most full-featured default for many greenfield TypeScript
SaaS teams as of April 2026, but Drizzle and Kysely can be better fits if you
want lighter abstractions or tighter SQL control."
</example>
