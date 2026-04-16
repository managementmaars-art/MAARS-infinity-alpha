#!/usr/bin/env bash
# scripts/e2e/daemon_fallback.sh
# E2E wrapper for daemon fallback test - delegates to scripts/daemon/cass_daemon_e2e.sh
#
# This wrapper ensures the daemon E2E test is included in the orchestrated E2E runner
# (scripts/tests/run_all.sh) which picks up scripts/e2e/*.sh
#
# Part of T7.3: E2E daemon fallback + health script

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

DAEMON_E2E_SCRIPT="${PROJECT_ROOT}/scripts/daemon/cass_daemon_e2e.sh"

if [[ ! -x "$DAEMON_E2E_SCRIPT" ]]; then
    echo "ERROR: Daemon E2E script not found or not executable: $DAEMON_E2E_SCRIPT" >&2
    exit 1
fi

# Pass through all arguments to the daemon E2E script
exec "$DAEMON_E2E_SCRIPT" "$@"
