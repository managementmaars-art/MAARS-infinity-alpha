#!/usr/bin/env bash
set -euo pipefail

ide_display_name="Rider"
usage_script_name="open-in-rider.sh"
ide_command_display="rider, rider.bat, rider64.exe"
ide_command_candidates=(rider rider.bat rider64.exe)
context_mode="rider"

source "$(dirname "${BASH_SOURCE[0]}")/lib/jetbrains-open.sh"
main "$@"
