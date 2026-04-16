#!/usr/bin/env bash
set -euo pipefail

if command -v rider >/dev/null 2>&1 || command -v rider.bat >/dev/null 2>&1 || command -v rider64.exe >/dev/null 2>&1; then
  printf 'rider\n'
fi

if command -v webstorm >/dev/null 2>&1 || command -v webstorm.bat >/dev/null 2>&1 || command -v webstorm64.exe >/dev/null 2>&1; then
  printf 'webstorm\n'
fi

if command -v code >/dev/null 2>&1; then
  printf 'code\n'
fi

if command -v cursor >/dev/null 2>&1 || command -v cursor.cmd >/dev/null 2>&1; then
  printf 'cursor\n'
fi

if command -v windsurf >/dev/null 2>&1 || command -v windsurf.cmd >/dev/null 2>&1; then
  printf 'windsurf\n'
fi
