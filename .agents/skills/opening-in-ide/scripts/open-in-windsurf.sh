#!/usr/bin/env bash
set -euo pipefail

ide_display_name="Windsurf"
usage_script_name="open-in-windsurf.sh"
ide_command_display="windsurf, windsurf.cmd"
ide_command_candidates=(windsurf windsurf.cmd)

source "$(dirname "${BASH_SOURCE[0]}")/lib/vscode-family-open.sh"
main "$@"
