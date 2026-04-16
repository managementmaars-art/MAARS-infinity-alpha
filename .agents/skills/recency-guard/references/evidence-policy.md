# Evidence Policy

Read this file only when you are judging source quality or assigning confidence
inside a `recency-guard` subagent. This is the authoritative policy for source
tiers and confidence labels so the subagents do not drift over time.

## Source Quality Hierarchy

| Tier | Source Type | Examples |
| ---- | ----------- | -------- |
| 1 | Official documentation and specifications | Language docs, API refs, RFCs, standards |
| 2 | Peer-reviewed research and audited data | Academic papers, government data, audited reports |
| 3 | Authoritative first-party content | Official changelogs, company announcements, engineering blogs |
| 4 | Reputable journalism and analysis | Major publications, analyst reports |
| 5 | Practitioner and community content | Conference talks, respected blogs, Stack Overflow |
| 6 | Unvetted community content | Social posts, anonymous blogs, AI-generated pages |

When a source is both official and current, classify it by its primary role:
canonical product docs, API references, and specifications are Tier 1; official
announcements, changelogs, release notes, and engineering blog posts are Tier 3.

## Confidence Guidance

Use the same labels across both subagents, but apply them in the mode-specific
way below.

Use topic-appropriate recency windows. Around 30 days is a good default for
fast-moving product, version, pricing, and policy questions; slower-moving
standards, research, or historical claims can justify older evidence.

### For `recency-checker`

| Score | Criteria |
| ----- | -------- |
| `High` | Confirmed by a Tier 1-3 source published recently enough for the topic, with no credible counter-evidence |
| `Med` | Supported by a credible source, but older, indirect, or missing important scope/date context |
| `Low` | Supported only by weak sources, contradicted by better evidence, or not independently verified |

### For `claim-verifier`

| Score | Criteria |
| ----- | -------- |
| `High` | Strong support, no material unresolved counterexample, and no major reasoning failure |
| `Med` | Generally reasonable, but may still need a caveat, softer framing, or explicit exception |
| `Low` | Materially overstated, weakly supported, contradicted, or badly framed |
