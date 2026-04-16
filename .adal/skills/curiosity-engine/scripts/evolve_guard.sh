#!/usr/bin/env bash
# evolve_guard.sh — reward-hacking guard for the EVOLVE meta-loop.
#
# EVOLVE is allowed to edit wiki/schema.md but nothing about the scoring or
# staging pipeline. This script records a fingerprint of the guarded scripts
# at epoch start and compares it at epoch end. If anything drifted, the epoch
# must be aborted and the schema edit reverted.
#
# Usage:
#   evolve_guard.sh hash                    # print fingerprint to stdout
#   evolve_guard.sh snapshot <outfile>      # write fingerprint to outfile
#   evolve_guard.sh check <snapshotfile>    # compare snapshot vs current; exit 0/1
#
# The snapshot/check pair replaces the earlier stdin-based verify mode so
# the whole flow stays inside the curiosity-engine bash discipline rule
# (no pipes, no heredocs, one arg-based command per bash call).

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
GUARDED=(
    "$SCRIPT_DIR/compress.py"
    "$SCRIPT_DIR/lint_scores.py"
    "$SCRIPT_DIR/score_diff.py"
    "$SCRIPT_DIR/sweep.py"
    "$SCRIPT_DIR/epoch_summary.py"
)

fingerprint() {
    for f in "${GUARDED[@]}"; do
        if [ ! -f "$f" ]; then
            echo "MISSING:$(basename "$f")"
        else
            printf '%s:%s\n' "$(shasum -a 256 "$f" | awk '{print $1}')" "$(basename "$f")"
        fi
    done
}

case "${1:-}" in
    hash)
        fingerprint
        ;;
    snapshot)
        if [ -z "${2:-}" ]; then
            echo "usage: evolve_guard.sh snapshot <outfile>" >&2
            exit 2
        fi
        fingerprint > "$2"
        echo "wrote $2"
        ;;
    check)
        if [ -z "${2:-}" ] || [ ! -f "$2" ]; then
            echo "usage: evolve_guard.sh check <snapshotfile>" >&2
            exit 2
        fi
        expected="$(cat "$2")"
        actual="$(fingerprint)"
        if [ "$expected" = "$actual" ]; then
            echo "ok"
            exit 0
        fi
        echo "DRIFT"
        echo "--- expected ---"
        echo "$expected"
        echo "--- actual ---"
        echo "$actual"
        exit 1
        ;;
    verify)
        # Legacy stdin-based mode kept for any stale callers; not recommended
        # under the bash discipline rule. Prefer snapshot/check.
        expected="$(cat)"
        actual="$(fingerprint)"
        if [ "$expected" = "$actual" ]; then
            echo "ok"
            exit 0
        fi
        echo "DRIFT"
        exit 1
        ;;
    *)
        echo "usage: evolve_guard.sh {hash|snapshot <file>|check <file>}" >&2
        exit 2
        ;;
esac
