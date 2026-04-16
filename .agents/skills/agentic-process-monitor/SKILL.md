---
name: agentic-process-monitor
description: Monitor background processes from Claude Code using sentinel files, heartbeat liveness, and subagent polling. Best practices and anti-patterns for autonomous loops that need to kick off work, detect completion/failure/hang/timeout, and resume the main context without wasting tokens. TRIGGERS - monitor background process, sentinel file, heartbeat monitoring, process supervision, agentic loop monitor, background task health, detect hung process, poll for completion, watchdog pattern, process liveness, monitor long-running task, agent poll loop, circuit breaker pattern.
allowed-tools: Read, Bash, Write
---

# Agentic Process Monitor

Patterns for monitoring background processes from Claude Code — detecting success, failure, timeout, and hung processes, then returning results to the main context to drive the next action.

**Companion skills**: `devops-tools:pueue-job-orchestration` (remote/queued work) | `devops-tools:distributed-job-safety` (concurrency)

---

> **Self-Evolving Skill**: This skill improves through use. If instructions are wrong, parameters drifted, or a workaround was needed — fix this file immediately, don't defer. Only update for real, reproducible issues.

## Architecture: Sentinel + Heartbeat + Agent

```
Main Context                          Monitor Agent (subagent)
─────────────                         ──────────────────────
1. Start work (Bash run_in_background)
   └─ work wrapper writes sentinel files
2. Launch Agent (poll every 15s) ────► poll loop:
3. Continue other work                  .status exists? → return result
                                        .heartbeat stale? → kill, return error
                                        elapsed > max? → kill, return timeout
4. Agent returns ◄──────────────────── detected outcome
5. Act on result (next step / retry / abort)
```

**Why this architecture**: The main context stays lean (no polling tokens burned). The subagent handles all the waiting. If the subagent itself fails, the main context can recover by checking sentinel files directly.

---

## Sentinel Protocol

The work process writes 4 files to a known directory (e.g., `/tmp/<project>-monitor/`):

| File               | When Written                   | Purpose                       |
| ------------------ | ------------------------------ | ----------------------------- |
| `<step>.pid`       | On start                       | PID for timeout kill          |
| `<step>.heartbeat` | Every N seconds during work    | mtime freshness = alive proof |
| `<step>.status`    | On exit (`SUCCESS` / `FAILED`) | Completion sentinel           |
| `<step>.result`    | On success                     | Structured output (JSON)      |

### Work Wrapper Template

```bash
#!/usr/bin/env bash
set -uo pipefail
STEP="${1:?step name required}"
MONITOR_DIR="${2:-/tmp/monitor}"
mkdir -p "$MONITOR_DIR"

echo $$ > "${MONITOR_DIR}/${STEP}.pid"

# Heartbeat: touch file every 10s in background
(while true; do touch "${MONITOR_DIR}/${STEP}.heartbeat"; sleep 10; done) &
HB_PID=$!
trap "kill $HB_PID 2>/dev/null" EXIT

# === YOUR WORK HERE ===
if your_command --args 2>"${MONITOR_DIR}/${STEP}.log"; then
    echo "SUCCESS" > "${MONITOR_DIR}/${STEP}.status"
    echo '{"key": "value"}' > "${MONITOR_DIR}/${STEP}.result"
else
    echo "FAILED" > "${MONITOR_DIR}/${STEP}.status"
fi
```

---

## Monitor Decision Tree

The polling agent checks every `POLL_INTERVAL` seconds (default: 15s):

```
every POLL_INTERVAL:
  .status exists?
    → read status + result, return to main context
  .heartbeat exists AND mtime stale (> STALE_THRESHOLD)?
    → process hung — kill PID, return "hung" error
  elapsed > MAX_TIMEOUT?
    → timeout — kill PID, return "timeout" error
  otherwise
    → sleep POLL_INTERVAL, continue
```

### Recommended Defaults

| Parameter            | Default       | Rationale                              |
| -------------------- | ------------- | -------------------------------------- |
| `POLL_INTERVAL`      | 15s           | Balances latency vs token cost         |
| `HEARTBEAT_INTERVAL` | 10s           | Must be < STALE_THRESHOLD / 2          |
| `STALE_THRESHOLD`    | 60s           | 6x heartbeat interval = generous slack |
| `MAX_TIMEOUT`        | 1800s (30min) | Catch infrastructure failures          |

---

## Circuit Breaker

Prevent repeated failures from wasting compute. Three consecutive crashes or failures → stop and report. Reset counter on any success.

```
consecutive_failures = 0
MAX_CONSECUTIVE = 3

on failure:
  consecutive_failures += 1
  if consecutive_failures >= MAX_CONSECUTIVE:
    STOP — likely infrastructure, not the work itself

on success:
  consecutive_failures = 0
```

---

## Agent Self-Healing

If the monitoring subagent fails (context overflow, timeout, crash), the main context recovers:

1. Check `.status` file directly — work may have finished while agent was dead
2. If `.status` exists → read result, continue normally
3. If no `.status` but `.heartbeat` is fresh → spawn replacement monitor agent
4. If no `.status` and `.heartbeat` is stale → process hung, kill PID, log error

This guarantees the main context never gets permanently stuck.

---

## Anti-Patterns

| Anti-Pattern                | Why It Fails                                                                                                                          | Use Instead                                                           |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------- |
| `tail -f \| grep -m1`       | Broken on macOS — pipe buffering prevents grep exit from killing tail, causing permanent hang                                         | Poll the log file for markers with `grep` in a loop                   |
| `run_in_background` alone   | Task IDs can expire or become unretrievable; stuck-as-running bug; no intermediate progress                                           | Sentinel files + agent polling                                        |
| Poll from main context      | Each poll injects output into the context window, burning ~50K tokens per check                                                       | Delegate polling to a subagent                                        |
| Hardcoded `sleep` timeout   | Wastes time on fast completions, too short for slow ones                                                                              | Poll interval + max timeout                                           |
| PID-only liveness check     | Cannot distinguish a hung process (PID alive, no progress) from a running one                                                         | Heartbeat file mtime — hung process stops touching the file           |
| `uv run` masking stale venv | `uv run` has its own resolution that bypasses broken venv state; console scripts (pytest, ruff) have stale shebangs after repo rename | Run `uv sync --python 3.13 --extra dev` after any repo rename or move |

---

## Environment Preflight

Run before entering any autonomous loop. If any check fails, fix before proceeding.

```bash
# 1. Python package importable?
uv run --python 3.13 python -c "import your_package" \
  || uv sync --python 3.13 --extra dev

# 2. Console scripts have valid shebangs? (catches post-rename breakage)
uv run --python 3.13 pytest --co -q tests/ 2>/dev/null \
  || uv sync --python 3.13 --extra dev

# 3. External service reachable?
curl -sf "http://localhost:PORT/?query=SELECT+1" \
  || echo "FAIL: start service or SSH tunnel"
```

### Common uv/venv Failures

| Symptom                                                         | Root Cause                                                       | Fix                                 |
| --------------------------------------------------------------- | ---------------------------------------------------------------- | ----------------------------------- |
| `ModuleNotFoundError` but `uv run python -c "import ..."` works | Stale venv — console script shebangs point to old repo path      | `uv sync --python 3.13 --extra dev` |
| `bad interpreter: ...old-path/.venv/bin/python3`                | Same — `.venv/bin/pytest` shebang hardcoded pre-rename directory | `uv sync --python 3.13 --extra dev` |
| `pip show` says not found, `uv run` says installed              | `uv run` resolution bypasses venv pip metadata                   | `uv sync` reconciles both           |

**Rule**: After any repo rename, directory move, or Python version change → always `uv sync --python 3.13 --extra dev` before running anything.


## Post-Execution Reflection

After this skill completes, check before closing:

1. **Did the command succeed?** — If not, fix the instruction or error table that caused the failure.
2. **Did parameters or output change?** — If the underlying tool's interface drifted, update Usage examples and Parameters table to match.
3. **Was a workaround needed?** — If you had to improvise (different flags, extra steps), update this SKILL.md so the next invocation doesn't need the same workaround.

Only update if the issue is real and reproducible — not speculative.
