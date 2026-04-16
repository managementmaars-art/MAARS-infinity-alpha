#!/usr/bin/env bash
set -euo pipefail

ide_display_name="Cursor"
usage_script_name="open-in-cursor.sh"
ide_command_display="cursor, cursor.cmd"
ide_command_candidates=(cursor cursor.cmd)

source "$(dirname "${BASH_SOURCE[0]}")/lib/vscode-family-open.sh"
main "$@"
