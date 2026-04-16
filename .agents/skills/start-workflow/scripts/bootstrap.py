#!/usr/bin/env python3
"""
bootstrap.py — Initialize a workflow run directory and state.json
Usage: python3 bootstrap.py <feature_name> <input_raw> [tg_chat_id]
Prints RUN_DIR to stdout on success.
"""
import json, os, sys, uuid
from datetime import datetime, timezone

def main():
    if len(sys.argv) < 3:
        sys.stderr.write("Usage: bootstrap.py <feature_name> <input_raw> [tg_chat_id]\n")
        sys.exit(1)

    feature_name = sys.argv[1]
    input_raw    = sys.argv[2]
    tg_chat_id   = sys.argv[3] if len(sys.argv) > 3 else ""

    run_id  = uuid.uuid4().hex[:8]
    run_dir = f"/tmp/workflow-{run_id}"
    os.makedirs(run_dir, exist_ok=True)

    state = {
        "run_id":      run_id,
        "run_dir":     run_dir,
        "input_raw":   input_raw,
        "input_type":  None,
        "fetched_content": None,
        "feature_name": feature_name,
        "specs_dir":   f"specs/{feature_name}-{run_id}",
        "status":      "RUNNING",
        "phase":       "init",
        "phases": {
            "spec-writer": {
                "status": "pending", "artifacts": {},
                "openspec_change": "", "openspec_validated": False
            },
            "coding": {
                "status": "pending", "last_task": ""
            },
            "code-review": {
                "status": "pending", "round": 0, "rounds": []
            },
            "security-gate": {
                "status": "pending", "is_sensitive": False
            },
            "test-runner": {
                "status": "pending", "summary": ""
            },
            "openspec-archive": {
                "status": "pending", "archived_at": None
            },
            "doc-syncer": {
                "status": "pending", "files_updated": []
            },
        },
        "tg_chat_id":   tg_chat_id,
        "error":        None,
        "started_at":   datetime.now(timezone.utc).isoformat(),
        "completed_at": None,
    }

    state_file = os.path.join(run_dir, "state.json")
    tmp = state_file + ".tmp." + str(os.getpid())
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    os.replace(tmp, state_file)

    print(run_dir)  # orchestrator captures this

if __name__ == "__main__":
    main()
