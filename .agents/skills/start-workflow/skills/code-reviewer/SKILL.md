---
name: code-reviewer
description: "Codex-powered code review with up to 2 rounds and automatic fix loop. Reviews git changes against specs, classifies findings by severity (P0-P3), applies fixes, re-reviews. Triggers on: /code-reviewer, review code, codex review, run code review."
---

# code-reviewer

IRON LAW: Maximum 2 review rounds. After round 2, record unresolved findings but do not block the pipeline. Never fabricate Codex output — always run the command and read the actual output.

## Invocation

Called by start-workflow, or standalone:
```
/code-reviewer
```

## Severity Levels

| Level | Action |
|-------|--------|
| P0 — Critical (security, data loss, correctness bug) | Must fix before next round |
| P1 — High (logic error, broken contract) | Fix in this round |
| P2 — Medium (code smell, missing tests) | Fix if round ≤ 1 |
| P3 — Low (style, naming) | Record, do not fix |

## Execution Flow

### For each round N (1 to 2):

**Step A — Update state**
```python
state['phases']['code-review']['round'] = N
state['phases']['code-review']['status'] = 'running'
```

**Step B — Run `codex review`**

`codex review` is designed for non-interactive/CI use and handles auth without session files.

```bash
# Write custom instructions to a file first
cat > "$RUN_DIR/review-instructions-N.txt" << 'EOF'
You are reviewing a feature implementation. Classify every finding with severity P0/P1/P2/P3.

Feature: {feature_name}

Specs summary:
{specs content, truncated to 1500 chars}

Prior round fixes already applied (do not re-flag these):
{prior_fixes or "None — this is round 1"}

Respond in this exact structure:
## P0 — Critical
(list findings or "None")
## P1 — High
(list findings or "None")
## P2 — Medium
(list findings or "None")
## P3 — Low
(list findings or "None")
## APPROVED
YES or NO
## REASONING
One sentence.
EOF

# Run codex review against commits made during the coding phase
# --base uses the commit SHA recorded before coding started (stored in state.phases.coding.base_sha)
codex review --base {coding_base_sha} \
  - < "$RUN_DIR/review-instructions-N.txt" \
  > "$RUN_DIR/review-round-N.txt" 2>&1
REVIEW_EXIT=$?
```

If `coding_base_sha` is not available, fall back to:
```bash
codex review --uncommitted \
  - < "$RUN_DIR/review-instructions-N.txt" \
  > "$RUN_DIR/review-round-N.txt" 2>&1
```

Validate output:
```bash
if [ $REVIEW_EXIT -ne 0 ] || [ ! -s "$RUN_DIR/review-round-N.txt" ]; then
  echo "codex review failed (exit $REVIEW_EXIT)"
  # mark state error and stop
fi
```

If the failure output contains `permission denied` or mentions `~/.codex/sessions`, request elevated sandbox permissions from the user to access `~/.codex/` and retry the command.

**Step C — Parse findings**

Read `$RUN_DIR/review-round-N.txt`. Extract all P0/P1/P2/P3 findings and APPROVED value.

Update state atomically:
```python
round_data = {
    'number': N,
    'codex_raw': open(f'{run_dir}/review-round-{N}.txt').read(),
    'p0': [...], 'p1': [...], 'p2': [...], 'p3': [...],
    'approved': True/False,
    'fixes_applied': False,
}
state['phases']['code-review']['rounds'].append(round_data)
```

**Step D — Apply fixes (if N < 2 and not APPROVED)**

For each P0 and P1 finding:
1. Read the relevant file(s)
2. Apply the fix
3. `git add` and `git commit -m "fix(review): {finding_summary}"`

For P2 findings in round 1: apply if straightforward, skip if complex.

Mark `fixes_applied = True` in state. Do NOT fix P3 items.

**Step E — Stop conditions**
1. `APPROVED: YES` → mark `state.phases.code-review.status = done`, stop
2. Round 2 complete → record unresolved P0/P1, mark `status = done` (capped), stop
3. `codex review` failed → mark `status = error`, propagate error

### After all rounds

```python
state['phases']['code-review']['unresolved_after_cap'] = [
    # P0/P1 items not fixed (only present if capped at round 2)
]
state['phases']['code-review']['status'] = 'done'
```
