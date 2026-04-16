#!/usr/bin/env bash
set -euo pipefail

ide_display_name="VS Code"
usage_script_name="open-in-code.sh"
ide_command_display="code, code.cmd"
ide_command_candidates=(code code.cmd)

source "$(dirname "${BASH_SOURCE[0]}")/lib/vscode-family-open.sh"
main "$@"
