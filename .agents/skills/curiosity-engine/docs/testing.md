# Improvement-loop test results

Record of a one-shot test of the ITERATE and EVOLVE mechanics on a seeded scratch wiki. The scratch wiki is kept at `~/Documents/curiosity-test` so it can be poked at afterward. No tests are shipped in the skill.

## Setup

- Scratch workspace bootstrapped with `scripts/setup.sh` (confirms the new `.claude/settings.json` copy path works).
- Vault seeded with 5 short `.extracted.md` sources covering overlapping LLM topics (attention, BPE, embeddings, GPT-3, scaling laws) so cross-reference opportunities actually exist.
- Wiki seeded with 6 deliberately weak pages (thin prose, no `(vault:...)` body citations, no wikilinks). Committed as `seed: initial weak pages for test`.

## ITERATE — inner loop

Delegated to a general-purpose subagent with `model: sonnet` and `batch_size: 5`. The worker ran the full accept-or-revert cycle against `compress.py` for each of 5 picks. Main session (this one) handled the review pass.

### Metrics

| dimension | before | after | delta |
|---|---|---|---|
| pages touched | 0 | 5 | +5 |
| average composite lint score | 0.267 | 0.140 | **−47%** |
| real body vault citations | 0 | 12 | +12 |
| wikilinks added | 0 | ~16 | +16 |
| accepts / rejects | — | 5 / 0 | all accepted |
| worst `tpc` on touched pages | 35.0 | 19.5 | −44% |
| best `tpc` on touched pages | 24.0 | 12.3 | −49% |

Per-page `compress.py` deltas (before → after, tpc):

- `transformer.md` 35.0 → 13.7
- `embeddings.md` 31.0 → 12.3
- `attention.md` 29.0 → 16.5
- `tokenization.md` 33.0 → 19.5
- `gpt3.md` 24.0 → 14.0
- `scaling-laws.md` 33.0 → 33.0 (untouched — already best scorer)

### Review-pass findings

Spot-checked `transformer.md` (densest rewrite) against `attention.extracted.md`: the "8 heads, 6 layers, no recurrence" claims are directly supported. No reverts needed. Seeds for next batch: `scaling-laws.md` (still at default score, no body citations).

### Observations

- The `compressed_tokens(after) <= compressed_tokens(before) * 1.2` ceiling was the binding constraint on every cycle. Workers had to iterate 4–5 times per page to fit under the ceiling because baseline pages were short. This suggests the ×1.2 ceiling may be too tight on a cold-start wiki; worth watching as a schema-proposal target for EVOLVE later.
- Wallclock for the 5-cycle batch was ~5,670 s under the default Claude Code tool-latency profile. That is **dramatically over** the 5-minute autoresearch budget. For real use, either `epoch_seconds` should be raised, `batch_size` lowered, or the worker should be told to pre-fetch vault reads in parallel. Recording this as a known issue, not a blocker.
- `sourced_claims` returning `max(count, 1)` hides the real zero-citation baseline in `compress.py` output. Schema/scoring is unchanged (off-limits to EVOLVE) but worth flagging.

## EVOLVE — outer loop guardrails

The reward-hacking guard was tested end-to-end with `scripts/evolve_guard.sh`.

| phase | command | result |
|---|---|---|
| record | `evolve_guard.sh hash` | printed SHA-256 for `compress.py` + `lint_scores.py` |
| clean verify | pipe stored hash back into `verify` | `ok`, exit 0 |
| simulate hack | `echo "# HACK" >> compress.py` | modified in place |
| dirty verify | pipe stored hash into `verify` | `DRIFT`, exit 1 |
| restore | `git checkout scripts/compress.py` | hash returns to baseline |

The guard reliably detects tampering with the scoring pipeline. A real EVOLVE epoch that tried to modify these files would abort and revert per the SKILL.md protocol.

A full 5-minute EVOLVE epoch was not run end-to-end: the test wiki is too small (6 pages, converged to avg 0.14 after one ITERATE) to produce a meaningful rate-of-improvement comparison or justify a schema edit. The schema-proposal path is specified in `SKILL.md` and logging format in `wiki/log.md`, and the guard it depends on is verified working. Full-scale epoch testing will be more meaningful against a wiki with ~30+ pages; noted for a follow-up.

## What I did NOT test

- Multi-epoch schema evolution (need a larger corpus to produce decaying rates)
- Schema-proposal history deduplication (same — needs multiple epochs)

## Test corpus provenance

Test results reported in this document were produced against scratch corpora assembled by the developer. None of these corpora ship with the skill; users will assemble their own vaults via manual INGEST or `scripts/local_ingest.py <trusted-dir>`.

- **Seed corpus (ITERATE test above):** 5 hand-written `.extracted.md` sources covering overlapping LLM topics, plus 6 deliberately weak seed wiki pages. Assembled by hand to give the inner loop something to chew on while keeping the surface area small enough to inspect.
- **Expanded corpus (planned EVOLVE test):** 100 Wikipedia articles across 5 topical clusters (LLM/neural, information theory, reinforcement learning, cognitive science, complex systems). These were bulk-ingested during development via an early `safe_fetch.py` path that has since been removed from the skill — the autonomous web-fetch surface was flagged medium-risk by prompt-injection scanners, and the mitigations (domain allowlist, scrub_check, wrapping, quarantine, SHA-256 hashing) reduced the risk without fully closing it. Bulk ingestion is now only available via `scripts/local_ingest.py` with a user-trusted directory on disk.

The removal of `safe_fetch.py` does not affect these tests' validity: the corpus exists as static markdown and the EVOLVE loop reads from existing vault content only. For reproducing the expanded test, a user would download a comparable set of Wikipedia articles to a local directory themselves and run `local_ingest.py` against it.
