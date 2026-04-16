#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: h5p-dev.sh [options]

Options:
  --workspace PATH   Workspace directory (default: .h5p-dev)
  --library NAME     Machine name override (e.g., H5P.MyType)
  --no-setup         Skip `h5p setup <library>`
  --no-server        Skip `h5p server`
  --help             Show help
USAGE
}

WORKSPACE=".h5p-dev"
LIBRARY=""
DO_SETUP=1
DO_SERVER=1

while [[ $# -gt 0 ]]; do
  case "$1" in
    --workspace)
      WORKSPACE="$2"; shift 2 ;;
    --library)
      LIBRARY="$2"; shift 2 ;;
    --no-setup)
      DO_SETUP=0; shift ;;
    --no-server)
      DO_SERVER=0; shift ;;
    --help)
      usage; exit 0 ;;
    *)
      echo "Unknown option: $1" >&2
      usage
      exit 1
      ;;
  esac
done

if ! command -v h5p >/dev/null 2>&1; then
  echo "h5p-cli is not installed. Run: npm install -g h5p-cli" >&2
  exit 1
fi

LIB_ROOT="$(pwd)"

if [[ -z "$LIBRARY" && -f "$LIB_ROOT/library.json" ]]; then
  LIBRARY=$(python - <<PY
import json
import sys
with open('library.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
print(data.get('machineName', ''))
PY
)
fi

if [[ -z "$LIBRARY" ]]; then
  echo "Could not determine library machine name. Use --library H5P.MyType" >&2
  exit 1
fi

mkdir -p "$WORKSPACE"

(
  cd "$WORKSPACE"
  h5p core
  mkdir -p libraries
  if [[ -e "libraries/$LIBRARY" && ! -L "libraries/$LIBRARY" ]]; then
    echo "libraries/$LIBRARY exists and is not a symlink. Remove it or choose a different workspace." >&2
    exit 1
  fi
  if [[ ! -L "libraries/$LIBRARY" ]]; then
    ln -s "$LIB_ROOT" "libraries/$LIBRARY"
  fi

  if [[ "$DO_SETUP" -eq 1 ]]; then
    HAS_DEPS=$(python - <<'PYIN'
import json
import os
path = os.path.join("..", "library.json")
try:
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    deps = (
        data.get('preloadedDependencies', [])
        + data.get('editorDependencies', [])
        + data.get('dynamicDependencies', [])
    )
    print('1' if deps else '0')
except Exception:
    print('0')
PYIN
)
    if [[ "$HAS_DEPS" == "1" ]]; then
      if ! h5p setup "$LIBRARY"; then
        echo "Warning: h5p setup failed. Continuing without dependency download." >&2
        echo "If this is a new library, re-run with --no-setup or install deps manually." >&2
      fi
    else
      echo "No dependencies found in library.json. Skipping h5p setup." >&2
    fi
  fi

  if [[ "$DO_SERVER" -eq 1 ]]; then
    h5p server
  else
    echo "Workspace ready at $WORKSPACE"
  fi
)
