#!/usr/bin/env bash
set -euo pipefail

ide_display_name="WebStorm"
usage_script_name="open-in-webstorm.sh"
ide_command_display="webstorm, webstorm.bat, webstorm64.exe"
ide_command_candidates=(webstorm webstorm.bat webstorm64.exe)
context_mode="webstorm"

source "$(dirname "${BASH_SOURCE[0]}")/lib/jetbrains-open.sh"
main "$@"
