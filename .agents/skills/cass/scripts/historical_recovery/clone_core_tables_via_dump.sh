#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 || $# -gt 3 ]]; then
  echo "usage: $0 SOURCE_DB OUTPUT_DB [--include-meta]" >&2
  exit 2
fi

SOURCE_DB=$1
OUTPUT_DB=$2
INCLUDE_META=${3:-}

if [[ ! -f "$SOURCE_DB" ]]; then
  echo "source db does not exist: $SOURCE_DB" >&2
  exit 1
fi

if [[ -e "$OUTPUT_DB" ]]; then
  echo "refusing to overwrite existing output db: $OUTPUT_DB" >&2
  exit 1
fi

mkdir -p "$(dirname "$OUTPUT_DB")"

TABLES=(sources agents workspaces conversations messages snippets)
if [[ "$INCLUDE_META" == "--include-meta" ]]; then
  TABLES=(meta "${TABLES[@]}")
fi

sqlite3 "$SOURCE_DB" ".dump ${TABLES[*]}" | sqlite3 "$OUTPUT_DB"

python3 - "$OUTPUT_DB" <<'PY'
import json
import sqlite3
import sys

path = sys.argv[1]
conn = sqlite3.connect(path)
cur = conn.cursor()
summary = {"output_db": path}
for table in ["sources", "agents", "workspaces", "conversations", "messages", "snippets"]:
    try:
        summary[table] = cur.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    except Exception as exc:
        summary[table] = f"ERR: {type(exc).__name__}: {exc}"
try:
    summary["quick_check"] = cur.execute("PRAGMA quick_check(1)").fetchone()[0]
except Exception as exc:
    summary["quick_check"] = f"ERR: {type(exc).__name__}: {exc}"
print(json.dumps(summary, ensure_ascii=False, indent=2))
conn.close()
PY
