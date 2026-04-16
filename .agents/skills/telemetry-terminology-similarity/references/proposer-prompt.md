# Proposer Prompt Template

A copy-pasteable prompt that consumes the output of `term_similarity.py --canonical --json` and asks the LLM to produce **structured, actionable rename proposals** with confidence levels, evidence citations, and explicit escape hatches.

## When to Use

After running `term_similarity.py --json --canonical` on a codebase, paste the JSON output into the template below. The LLM produces a `proposals[]` array where each entry is one atomic, revertable decision.

## Design Principles

This template encodes 7 research-validated principles:

1. **Reasoning before verdict** (CoT improves calibration in 33/36 settings — arXiv 2505.14489)
2. **Categorical confidence** (HIGH/MEDIUM/LOW, not numerical — EMNLP 2023)
3. **Score legend with anchored examples** (prevents axis misalignment)
4. **Disagreement → flag rule** (multi-layer disagreement is structural honesty trigger)
5. **Hard gates from domain context** (co-occurrence, bounded context — overrides scores)
6. **Explicit escape hatch** (`flag_for_review` is high-status, not failure)
7. **Atomic proposals with required edits[].file/line** (vagueness is structurally impossible)

---

## The Template

````markdown
You are reviewing similarity scores for telemetry/log/schema field names in a codebase. Your job is to produce **atomic, reviewable rename proposals** — not vague suggestions.

# Score Interpretation Legend

Three independent layers score each pair:

- **syn** (syntactic, 0-100): RapidFuzz `token_set_ratio` on normalized field names.
  - `>85` = near-identical strings (likely surface variant)
  - `60-85` = shared prefix/suffix (related)
  - `<60` = visually distinct strings

- **tax** (taxonomic, 0.0-1.0): WordNet Wu-Palmer head-noun similarity.
  - `>0.85` = WordNet synonyms (e.g., level↔severity, error↔fault)
  - `0.5-0.85` = related concepts (siblings in hypernym tree)
  - `<0.5` = unrelated branches

- **sem** (semantic, 0.0-1.0): sentence-transformers cosine similarity.
  - `>0.75` = embedding cousins (same context distribution)
  - `0.5-0.75` = loosely related
  - `<0.5` = different contexts

- **comb** (combined): `max(syn/100, tax, sem)` — the strongest single signal wins.

# Anchored Examples

| syn | tax  | sem  | pair                            | verdict         | reason                                                              |
| --- | ---- | ---- | ------------------------------- | --------------- | ------------------------------------------------------------------- |
| 100 | 0.0  | 0.96 | `user_id` vs `userId`           | RENAME          | Pure case variant — surface drift only                              |
| 0   | 1.00 | 0.47 | `error` vs `fault`              | RENAME          | True synonyms via WordNet                                           |
| 67  | 0.91 | 0.46 | `operation` vs `action`         | RENAME          | Synonyms + shared substring                                         |
| 47  | 0.0  | 0.79 | `user_id` vs `account_id`       | LEAVE_DISTINCT  | High semantic, zero taxonomic = related entities, not duplicates    |
| 88  | 0.30 | 0.40 | `order_total` vs `order_status` | FALSE_POSITIVE  | String overlap only — completely different concepts                 |
| 56  | 0.0  | 0.54 | `request_id` vs `trace_id`      | FLAG_FOR_REVIEW | Could be merged or could be intentionally distinct (OTel uses both) |

# Canonical Anchor Interpretation

If `canonical_anchors` shows a high-score match in OTel/OCSF/CloudEvents, **bias strongly** toward renaming the local field to match the standard. The standard exists for ecosystem interop (OTel collectors, dashboards, vendor tools).

Example:

- Local field: `http_method` (score 100 vs OTel `http.request.method`)
- Proposal: rename to `http.request.method` (the OTel canonical name)

# Hard Gates (Override All Scores)

Two criteria veto any rename, regardless of how clean the scores look:

1. **Co-occurrence gate**: If both fields appear in the same log entry / span / row / record, they refer to **distinct concepts** and must NOT be merged. Their similarity is a naming-disambiguation problem, not a duplication problem.

2. **Bounded context gate**: If the two fields originate in different services, modules, or domain layers, leave them alone. Translate at the boundary instead. Forcing global consistency destroys local clarity.

You don't have direct access to verify these gates — but you SHOULD list them as `blocking_unknowns` for any high-confidence rename you propose, so a human can verify before applying.

# Disagreement Rule (Mandatory)

If the three layers (syn, tax, sem) disagree by more than one band, the proposal `kind` MUST be `flag_for_review`. You may not propose a rename in this case. The disagreement itself is the signal.

Example: `(syn=88, tax=0.30, sem=0.40)` — syntactic says "similar", taxonomic says "unrelated", semantic says "unrelated". This is a string coincidence, not a real duplicate. Flag, don't rename.

# Output Schema (REQUIRED)

Emit a single JSON object matching this schema:

```json
{
  "summary": {
    "total_pairs_reviewed": <int>,
    "rename_proposals": <int>,
    "leave_distinct": <int>,
    "false_positives": <int>,
    "flagged_for_review": <int>
  },
  "proposals": [
    {
      "id": "<stable-slug, e.g. rename-trace-id-001>",
      "kind": "rename | annotate | merge | split | flag_for_review | no_action",
      "confidence": "HIGH | MEDIUM | LOW",
      "field_a": "<name>",
      "field_b": "<name>",
      "evidence": {
        "syn": <number>,
        "tax": <number>,
        "sem": <number>,
        "agreement": "all_agree | partial | disagree",
        "dominant_layer": "syntactic | taxonomic | semantic | none"
      },
      "canonical_match": {
        "name": "<canonical name from OTel/OCSF/CloudEvents>",
        "source": "otel | ocsf | cloudevents | none",
        "score": <number>
      },
      "reasoning": "<2-3 sentences: which layer dominates, why, what real-world relationship would produce this score pattern>",
      "proposed_action": "<one sentence: e.g., 'Rename trace_id → http.request.method to match OTel canonical'>",
      "blocking_unknowns": [
        "<things a human must verify before applying, e.g., 'Do these fields ever co-occur in the same span?'>"
      ]
    }
  ]
}
```

# Quality Bar

A reviewer prefers **5 honest `flag_for_review` proposals** over **1 confidently-wrong rename**. If you cannot construct a plausible real-world story for a pair from name alone, return `flag_for_review` with the unknowns logged.

`blocking_unknowns` MUST be a non-empty array for any HIGH-confidence rename — you have no access to the actual files, so you must explicitly defer file/line enumeration to a follow-up step.

# Process

1. **PLAN**: Read all scored pairs and canonical anchors. Build a mental model of which pairs cluster around which concepts.
2. **CLASSIFY**: For each pair with `combined > 0.6`, walk the rules above and classify into one of the 6 `kind` values.
3. **CITE**: Every proposal must reference the specific (syn, tax, sem) triple that justifies it.
4. **VERIFY**: Before emitting a proposal, ask: "Could two reasonable engineers disagree about this?" If yes, downgrade confidence by one level.
5. **EMIT**: Output the JSON object. No prose outside the JSON.

# Input

[Paste the output of `term_similarity.py --json --canonical` below]

```json
<INSERT ANALYSIS JSON HERE>
```
````

---

## Example Usage

```bash
# 1. Run the analysis
SCRIPT="$(find ~/.claude/plugins -path '*/telemetry-terminology-similarity/references/term_similarity.py' -print -quit)"
python3 -c "import re,glob; fields=set();
[fields.add(m.group(1)) for f in glob.glob('**/*.rs', recursive=True)
 for m in re.finditer(r'^\s*(?:pub\s+)?([a-z][a-z0-9_]*)\s*:\s*[A-Z]', open(f).read(), re.MULTILINE)];
print('\n'.join(sorted(fields)))" | uv run --python 3.13 "$SCRIPT" --json --canonical > analysis.json

# 2. Apply the proposer prompt (paste analysis.json into the template above)
# The LLM produces a structured proposals.json

# 3. Review proposals atomically — accept/reject one at a time
```

## Why Not Just Ask "Find Duplicates"?

A naive prompt like "find duplicate field names" fails three ways:

1. **Fabrication**: LLMs invent specifics rather than say "I don't know"
2. **Bundling**: Multiple unrelated renames get crammed into one proposal
3. **Anchoring bias**: Earlier items contaminate later judgments

The structured template eliminates all three: required `blocking_unknowns[]` array forces honesty, atomic `id` per proposal prevents bundling, and the score legend + anchored examples calibrate the model upfront.

## Two-Pass Variant (Higher Quality)

For higher-stakes audits, run the prompt **twice**:

**Pass 1 — Drafter**: Use the template above. Be generous; emit anything that _could_ warrant action.

**Pass 2 — Critic**: Take Pass 1's output, paste into:

```
You are reviewing a junior engineer's refactor proposals for a telemetry naming audit.
For each proposal, do one of:
- APPROVE: keep as-is
- DOWNGRADE_TO_FLAG: confidence too high for the evidence; convert to flag_for_review
- REJECT_WITH_REASON: the proposal is wrong (string coincidence, related-but-distinct concepts, or bundled concerns)

Reject if any of:
- evidence.agreement is "disagree" but kind is "rename"
- the proposal bundles multiple unrelated renames
- blocking_unknowns is empty (impossible — every proposal has unknowns from this analysis)
- the proposed_action contradicts the canonical_match

Output: same JSON schema as input, with "critic_verdict" added per proposal.
```

Empirically eliminates 30-50% of low-quality proposals from Pass 1.
