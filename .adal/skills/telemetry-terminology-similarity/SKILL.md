---
name: telemetry-terminology-similarity
description: Score telemetry field name similarity across syntactic, taxonomic, and semantic layers. TRIGGERS - field name collision, terminology overlap, schema dedup, naming inconsistency, telemetry naming, log field similarity.
allowed-tools: Read, Bash, Grep, Edit, Write
---

# Telemetry Terminology Similarity

Score pairwise similarity of telemetry field names across three independent layers. Emits raw scores — no thresholds, no clustering, no opinions. The consuming AI agent applies its own domain judgment.

> **Self-Evolving Skill**: This skill improves through use. If instructions are wrong, parameters drifted, or a workaround was needed — fix this file immediately, don't defer. Only update for real, reproducible issues.

## When to Use This Skill

Use this skill when:

- Auditing a telemetry/logging schema for naming collisions
- Comparing two JSONL log schemas for field overlap
- Detecting `trace_id` vs `traceId` vs `request_id` vs `correlation_id` style problems
- Validating field naming consistency before shipping telemetry changes

## Architecture

5-layer scoring pipeline — each layer catches what the others miss:

```
┌─────────────────────────────────────────────────────────┐
│  Layer 1: NORMALIZE                                     │
│  camelCase/snake_case split + abbreviation expansion    │
│  wordninja for concatenated words                       │
│  "traceId" → "trace id", "ts" → "timestamp"            │
├─────────────────────────────────────────────────────────┤
│  Layer 2: SYNTACTIC (RapidFuzz, 0-100)                  │
│  token_set_ratio on normalized forms                    │
│  Catches: trace_id ↔ traceId, level ↔ log_level        │
├─────────────────────────────────────────────────────────┤
│  Layer 3: TAXONOMIC (WordNet Wu-Palmer, 0.0-1.0)        │
│  Head-noun synonym detection via hypernym tree          │
│  Catches: level ↔ severity, error ↔ fault, op ↔ action │
├─────────────────────────────────────────────────────────┤
│  Layer 4: SEMANTIC (sentence-transformers, 0.0-1.0)     │
│  Cosine similarity via all-MiniLM-L6-v2 embeddings     │
│  Catches: error ↔ exception, user_id ↔ account_id      │
├─────────────────────────────────────────────────────────┤
│  Layer 5: CANONICAL (--canonical flag, optional)        │
│  RapidFuzz vs bundled OTel/OCSF/CloudEvents dictionary  │
│  Catches: http_method → http.request.method (OTel)      │
├─────────────────────────────────────────────────────────┤
│  Output: All pairs scored + canonical anchors.          │
│  Agent decides what to act on — tool computes, judges.  │
│  Use proposer-prompt.md for structured rename proposals.│
└─────────────────────────────────────────────────────────┘
```

## Two-Phase Workflow: Score → Propose

The skill works in two phases:

1. **Phase 1 — Score** (`term_similarity.py`): Compute raw similarity scores across 5 layers. Tool computes, no opinions emitted.
2. **Phase 2 — Propose** (`references/proposer-prompt.md`): A bundled prompt template that consumes the scoring JSON and asks the LLM to produce structured rename proposals with confidence levels, evidence citations, and explicit escape hatches.

The two phases are deliberately separated. Phase 1 is deterministic and reproducible; Phase 2 applies domain judgment that only an LLM with conversation context can provide.

## Dependencies

All installed via `uv run` (PEP 723 inline metadata — no global install needed):

| Package                 | Purpose                             | Size    |
| ----------------------- | ----------------------------------- | ------- |
| `sentence-transformers` | Semantic embeddings (MiniLM-L6)     | ~80 MB  |
| `rapidfuzz`             | Fast fuzzy string matching (C++)    | ~1.3 MB |
| `wordninja`             | Probabilistic word splitting        | ~0.5 MB |
| `nltk`                  | WordNet Wu-Palmer synonym detection | ~30 MB  |
| `orjson`                | Fast JSON serialization             | ~0.3 MB |

First run downloads the `all-MiniLM-L6-v2` model (~80 MB) and WordNet data (~30 MB).

## Script Location

The analysis script lives in this skill's `references/` directory. Resolve the path before use:

```bash
# SSoT-OK: marketplace path resolution for cross-repo invocation
SCRIPT_DIR="$(dirname "$(find ~/.claude/plugins -path '*/telemetry-terminology-similarity/references/term_similarity.py' -print -quit 2>/dev/null)")"
SCRIPT="$SCRIPT_DIR/term_similarity.py"
```

All examples below assume `$SCRIPT` is set. When invoking from the cc-skills repo itself, use the relative path directly.

## Usage

### Analyze field names directly

```bash
# SSoT-OK: uv run handles PEP 723 inline deps
uv run --python 3.13 "$SCRIPT" \
  trace_id traceId request_id correlation_id \
  level severity log_level priority
```

### Extract fields from a Python codebase

Use Python regex extraction (macOS lacks `grep -P`):

```bash
python3 -c "
import re, glob
fields = set()
for f in glob.glob('**/*.py', recursive=True):
    text = open(f).read()
    for m in re.finditer(r'\"([a-z][a-z0-9_]*?)\":', text):
        fields.add(m.group(1))
for f in sorted(fields):
    print(f)
" | uv run --python 3.13 "$SCRIPT"
```

### Analyze from stdin (pipe from jq, etc.)

```bash
head -1 telemetry.jsonl | jq -r 'keys[]' | uv run --python 3.13 "$SCRIPT"
```

### Analyze a JSONL file's fields

```bash
uv run --python 3.13 "$SCRIPT" --jsonl /path/to/telemetry.jsonl
```

### Compare two JSON schemas

```bash
uv run --python 3.13 "$SCRIPT" --schema-a schema_v1.json --schema-b schema_v2.json
```

### Control output size

```bash
uv run --python 3.13 "$SCRIPT" --top 30 field1 field2 field3   # Top 30 pairs
uv run --python 3.13 "$SCRIPT" --top 0 field1 field2 field3    # All pairs
uv run --python 3.13 "$SCRIPT" --json field1 field2 field3     # JSON output
```

### Lookup against canonical standards (OTel/OCSF/CloudEvents)

```bash
# Anchor each field against 1,453 bundled canonical names from OTel + OCSF + CloudEvents
uv run --python 3.13 "$SCRIPT" --canonical http_method http_status request_id severity
```

Output adds a `=== CANONICAL ANCHORS ===` section showing the closest standard names per field. Useful for "should we rename to match an industry standard" decisions.

### Generate structured rename proposals (Phase 2)

After running with `--json --canonical`, paste the output into [`references/proposer-prompt.md`](./references/proposer-prompt.md) — a bundled prompt template that produces atomic, reviewable rename proposals with confidence levels and explicit escape hatches.

```bash
# Phase 1: Score
uv run --python 3.13 "$SCRIPT" --json --canonical [fields...] > analysis.json

# Phase 2: Apply proposer prompt (paste analysis.json into the template)
# The LLM produces structured proposals.json — review atomically
```

## Parameters

| Parameter       | Default | Description                                                  |
| --------------- | ------- | ------------------------------------------------------------ |
| `--top`         | 50      | Show top N pairs by combined score (0 = all)                 |
| `--canonical`   | false   | Lookup each field against bundled OTel/OCSF/CloudEvents dict |
| `--jsonl`       | —       | Extract fields from a JSONL file (all unique keys)           |
| `--schema-a/-b` | —       | Cross-schema comparison (two JSON schema files)              |
| `--json`        | false   | Output as structured JSON instead of text                    |

## Output Format

### Text output (default)

```
Fields analyzed: 21
Unique after normalization: 19

=== EXACT DUPLICATES (after normalization) ===
  trace_id  ==  traceId
  timestamp  ==  ts

=== SCORED PAIRS (sorted by combined score) ===
    syn    tax    sem   comb  pair
    ---    ---    ---   ----  ----
  100.0  0.000  0.560  1.000  level                     <-> log_level
    0.0  1.000  0.472  1.000  error                     <-> fault
   66.7  0.909  0.457  0.909  operation                 <-> action
   46.2  0.833  0.251  0.833  level                     <-> severity
   28.6  0.667  0.700  0.700  error                     <-> exception
```

Three independent scores per pair — the agent reads all three to decide:

- **syn** (syntactic): high = surface-level name variant
- **tax** (taxonomic): high = WordNet synonym (hypernym tree)
- **sem** (semantic): high = embedding similarity (distributional)
- **comb** (combined): max(syn/100, tax, sem) — sorting key

### JSON output (`--json`)

Structured JSON with `exact_duplicates` and `scored_pairs` arrays.

## How Each Layer Contributes

| Scenario                  | syn   | tax   | sem   | Which layer wins |
| ------------------------- | ----- | ----- | ----- | ---------------- |
| `trace_id` vs `traceId`   | 100.0 | 0.0   | 1.0   | Syntactic        |
| `level` vs `severity`     | 46.2  | 0.833 | 0.251 | Taxonomic        |
| `error` vs `fault`        | 0.0   | 1.000 | 0.472 | Taxonomic        |
| `operation` vs `action`   | 66.7  | 0.909 | 0.457 | Taxonomic        |
| `error` vs `exception`    | 28.6  | 0.667 | 0.700 | Semantic         |
| `user_id` vs `account_id` | 47.1  | 0.0   | 0.792 | Semantic         |

## Abbreviation Dictionary

The normalizer expands common telemetry abbreviations:

| Abbr   | Expansion | Abbr   | Expansion     |
| ------ | --------- | ------ | ------------- |
| `ts`   | timestamp | `uid`  | user id       |
| `req`  | request   | `resp` | response      |
| `err`  | error     | `msg`  | message       |
| `svc`  | service   | `env`  | environment   |
| `op`   | operation | `lvl`  | level         |
| `evt`  | event     | `ctx`  | context       |
| `acct` | account   | `cfg`  | configuration |
| `dur`  | duration  | `lat`  | latency       |

Add domain-specific abbreviations by editing `ABBREVIATIONS` in `term_similarity.py`.

## Troubleshooting

| Issue                            | Cause             | Solution                                        |
| -------------------------------- | ----------------- | ----------------------------------------------- |
| `ModuleNotFoundError`            | Missing deps      | Use `uv run` (PEP 723 resolves automatically)   |
| Model download slow              | First run         | Cached after first download (~110 MB total)     |
| Script not found from other repo | Path not resolved | Set `$SCRIPT` per Script Location section       |
| `grep: invalid option -- P`      | macOS lacks PCRE  | Use `python3 -c "import re..."` pattern instead |

## Post-Execution Reflection

After this skill completes, check before closing:

1. **Did the command succeed?** — If not, fix the instruction or error table that caused the failure.
2. **Did parameters or output change?** — If the underlying tool's interface drifted, update Usage examples and Parameters table to match.
3. **Was a workaround needed?** — If you had to improvise (different flags, extra steps), update this SKILL.md so the next invocation doesn't need the same workaround.

Only update if the issue is real and reproducible — not speculative.
