# Agent Verification Patterns

Testing agent behavior and integrating with `eve-agent-optimisation` for efficiency analysis.

## When to Apply

Any Eve app that includes agents (defined in `agents.yaml`) needs behavioral verification. This goes beyond "does the agent run" to "does it run correctly and efficiently."

## Two-Phase Approach

1. **Correctness** — Does the agent produce the right output?
2. **Efficiency** — Does it get there without waste?

Always verify correctness first. Efficiency analysis on a broken agent is pointless.

## Phase 1: Correctness Verification

### Create a Test Job

```bash
# Simple job with known input
JOB_ID=$(eve job create \
  --project $PROJ_ID \
  --agent $AGENT_SLUG \
  --prompt "Process the test document at fixtures/sample-document.md" \
  --json | jq -r '.id')

echo "Job: $JOB_ID"
```

### Follow Execution

```bash
# Stream logs in real-time
eve job follow $JOB_ID

# Or poll status
while true; do
  STATUS=$(eve job show $JOB_ID --json | jq -r '.phase')
  echo "Status: $STATUS"
  [[ "$STATUS" == "done" || "$STATUS" == "cancelled" ]] && break
  sleep 10
done
```

### Verify Output

```bash
# Get job result
RESULT=$(eve job result $JOB_ID --json)
EXIT_CODE=$(echo "$RESULT" | jq -r '.exit_code')
OUTPUT=$(echo "$RESULT" | jq -r '.output')

# Assert success
[[ "$EXIT_CODE" == "0" ]] && echo "PASS: Agent completed successfully" || echo "FAIL: Exit code $EXIT_CODE"

# Assert output contains expected content
echo "$OUTPUT" | grep -q "expected_keyword" && echo "PASS: Output correct" || echo "FAIL: Missing expected output"
```

### Error Case Testing

```bash
# Bad input — agent should handle gracefully
BAD_JOB=$(eve job create \
  --project $PROJ_ID \
  --agent $AGENT_SLUG \
  --prompt "Process nonexistent-file.md" \
  --json | jq -r '.id')

eve job follow $BAD_JOB

# Should complete (not hang) with a clear error message
RESULT=$(eve job result $BAD_JOB --json)
echo "$RESULT" | jq -r '.output'
# Should explain what went wrong, not crash with a stack trace
```

### Missing Secrets Testing

```bash
# Temporarily remove a required secret
eve secrets delete --org $ORG_ID --key REQUIRED_API_KEY

# Run the agent
NOSECRET_JOB=$(eve job create \
  --project $PROJ_ID \
  --agent $AGENT_SLUG \
  --prompt "Process test document" \
  --json | jq -r '.id')

eve job follow $NOSECRET_JOB

# Agent should fail fast with a clear message about the missing secret
# NOT hang, retry indefinitely, or produce wrong output

# Restore the secret
eve secrets set --org $ORG_ID --key REQUIRED_API_KEY --value "$SAVED_VALUE"
```

## Phase 2: Efficiency Verification

After correctness is confirmed, measure efficiency.

### Capture Baseline Metrics

```bash
# Get receipt for the successful job
RECEIPT=$(eve job receipt $JOB_ID --json)

# Extract key metrics
TOKENS_IN=$(echo "$RECEIPT" | jq '.input_tokens')
TOKENS_OUT=$(echo "$RECEIPT" | jq '.output_tokens')
COST=$(echo "$RECEIPT" | jq '.total_cost')
DURATION=$(echo "$RECEIPT" | jq '.duration_seconds')
TOOL_CALLS=$(echo "$RECEIPT" | jq '.tool_calls')

echo "Baseline metrics:"
echo "  Input tokens:  $TOKENS_IN"
echo "  Output tokens: $TOKENS_OUT"
echo "  Cost:          $COST"
echo "  Duration:      ${DURATION}s"
echo "  Tool calls:    $TOOL_CALLS"
```

### Record Baselines in Test Plan

Include a baselines section in the test plan:

```markdown
## Baselines (recorded YYYY-MM-DD)

| Metric | Baseline | Acceptable Range |
|--------|----------|-----------------|
| Input tokens | 15,000 | < 25,000 |
| Output tokens | 3,000 | < 5,000 |
| Cost | $0.12 | < $0.25 |
| Duration | 45s | < 120s |
| Tool calls | 8 | < 15 |
```

### Integration with eve-agent-optimisation

After capturing baselines, run the optimization skill for deeper analysis:

```
/eve-agent-optimisation
```

The optimization skill will:
1. Analyze the job execution trace
2. Identify unnecessary tool calls and blind alleys
3. Suggest harness/model changes
4. Recommend prompt improvements

Record optimization findings in the test plan for future regression detection.

### Regression Detection

On subsequent runs, compare against baselines:

```bash
NEW_RECEIPT=$(eve job receipt $NEW_JOB_ID --json)
NEW_TOKENS=$(echo "$NEW_RECEIPT" | jq '.input_tokens')

if [ "$NEW_TOKENS" -gt 25000 ]; then
  echo "REGRESSION: Input tokens ($NEW_TOKENS) exceeded threshold (25,000)"
  echo "Baseline was: $TOKENS_IN"
fi
```

## Multi-Agent Coordination

When the app has multiple agents that work together:

### Dependency Order

```bash
# Create parent job
PARENT=$(eve job create \
  --project $PROJ_ID \
  --agent coordinator-agent \
  --prompt "Coordinate the full workflow" \
  --json | jq -r '.id')

# Follow the parent — child jobs appear in logs
eve job follow $PARENT

# List child jobs
eve job list --parent $PARENT --json | jq '.[] | {id, agent, phase}'
```

### What to Check

- [ ] Parent job creates child jobs in correct order
- [ ] Dependencies between jobs are respected (child B waits for child A)
- [ ] All child jobs complete before parent completes
- [ ] Results aggregate correctly at the parent level
- [ ] Failure in one child is handled (retry, skip, or fail parent)

### Coordination Timing

```bash
# Get all job timestamps
eve job list --parent $PARENT --json | jq '.[] | {
  id: .id,
  agent: .agent,
  started: .started_at,
  completed: .completed_at,
  duration: (.completed_at | fromdateiso8601) - (.started_at | fromdateiso8601)
}'
```

## Correctness Checklist

- [ ] Agent completes primary task with correct output
- [ ] Agent handles bad input gracefully (clear error, no hang)
- [ ] Agent handles missing secrets gracefully (fast fail, clear message)
- [ ] Agent handles network errors gracefully (retry or clear error)
- [ ] Multi-agent coordination completes in dependency order (if applicable)

## Efficiency Checklist

- [ ] Token usage within baseline thresholds
- [ ] Duration within baseline thresholds
- [ ] No unnecessary tool calls (< 2x minimum needed)
- [ ] No blind alleys (tool calls that produce unused results)
- [ ] Cost within budget bounds
