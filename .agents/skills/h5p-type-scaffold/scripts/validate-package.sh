#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: validate-package.sh [options]

Validate an unpacked H5P package directory against the intended upload flow.

Options:
  --mode MODE      Validation mode: library-install | content-import
                   (default: library-install)
  --dir PATH       Unpacked package directory to validate (default: .)
  --help           Show help
USAGE
}

MODE="library-install"
PACKAGE_DIR="."

while [[ $# -gt 0 ]]; do
  case "$1" in
    --mode)
      MODE="$2"; shift 2 ;;
    --dir)
      PACKAGE_DIR="$2"; shift 2 ;;
    --help)
      usage; exit 0 ;;
    *)
      echo "Unknown option: $1" >&2
      usage
      exit 1
      ;;
  esac
done

if [[ "$MODE" != "library-install" && "$MODE" != "content-import" ]]; then
  echo "Invalid --mode '$MODE'. Expected library-install or content-import." >&2
  exit 1
fi

if [[ ! -d "$PACKAGE_DIR" ]]; then
  echo "Directory does not exist: $PACKAGE_DIR" >&2
  exit 1
fi

ALLOWED_EXT_RE='\.(json|png|jpe?g|gif|bmp|tiff?|svg|eot|ttf|woff2?|otf|webm|mp4|vtt|ogg|mp3|txt|pdf|rtf|docx?|xlsx?|pptx?|odt|ods|odp|xml|csv|diff|patch|swf|md|textile|wav|js|css)$'

# Check for files without allowed extensions in the package directory.
# These files will be rejected by strict validators (e.g. Drupal 11.x H5P
# 2.0.0 beta) even though older H5P platforms accept them.
check_file_extensions() {
  local dir="$1"
  local h5pignore="$dir/.h5pignore"
  local find_excludes=()

  if [[ -f "$h5pignore" ]]; then
    while IFS= read -r line || [[ -n "$line" ]]; do
      line="${line%%#*}"
      line="$(echo "$line" | sed 's/^[[:space:]]*//' | sed 's/[[:space:]]*$//')"
      [[ -z "$line" ]] && continue
      find_excludes+=( -not -path "./${line}" -not -path "./${line}/*" )
    done < "$h5pignore"
  fi

  local bad_files=()
  while IFS= read -r fpath; do
    # Skip dotfiles (hidden files)
    [[ "$fpath" == .* ]] && continue
    echo "$fpath" | grep -q '/\.' && continue
    if ! echo "$fpath" | grep -Eiq "$ALLOWED_EXT_RE"; then
      bad_files+=("$fpath")
    fi
  done < <(cd "$dir" && find . -type f ${find_excludes[@]+"${find_excludes[@]}"} | sed 's|^\./||' | sort)

  if [[ ${#bad_files[@]} -gt 0 ]]; then
    echo "Warning: Files without an allowed H5P extension detected:" >&2
    printf '  %s\n' "${bad_files[@]}" >&2
    echo "Strict validators (e.g. Drupal 11.x H5P 2.0.0) will reject these." >&2
    echo "Use scripts/pack.sh to create a clean .h5p archive." >&2
  fi
}

if [[ "$MODE" == "library-install" ]]; then
  if [[ ! -f "$PACKAGE_DIR/library.json" ]]; then
    echo "library-install mode requires library.json at package root." >&2
    exit 1
  fi

  if [[ -f "$PACKAGE_DIR/h5p.json" ]]; then
    echo "library-install mode should not include h5p.json at package root." >&2
    exit 1
  fi

  if [[ -d "$PACKAGE_DIR/content" ]]; then
    echo "library-install mode should not include content/ at package root." >&2
    exit 1
  fi

  check_file_extensions "$PACKAGE_DIR"

  echo "OK: library-install layout is valid."
  exit 0
fi

if [[ ! -f "$PACKAGE_DIR/h5p.json" ]]; then
  echo "content-import mode requires h5p.json at package root." >&2
  exit 1
fi

if [[ ! -f "$PACKAGE_DIR/content/content.json" ]]; then
  echo "content-import mode requires content/content.json." >&2
  exit 1
fi

python - <<'PY' "$PACKAGE_DIR/h5p.json" "$PACKAGE_DIR/content/content.json"
import json
import sys

h5p_json_path = sys.argv[1]
content_json_path = sys.argv[2]

def fail(msg):
    print(msg, file=sys.stderr)
    sys.exit(1)

try:
    with open(h5p_json_path, "r", encoding="utf-8") as f:
        h5p = json.load(f)
except Exception as exc:
    fail(f"Invalid JSON in h5p.json: {exc}")

try:
    with open(content_json_path, "r", encoding="utf-8") as f:
        json.load(f)
except Exception as exc:
    fail(f"Invalid JSON in content/content.json: {exc}")

required_scalar = ["title", "mainLibrary", "license"]
missing = [k for k in required_scalar if not h5p.get(k)]
if missing:
    fail(f"h5p.json missing required field(s): {', '.join(missing)}")

deps_key = None
for candidate in ("preloadedDependencies", "preloadDependencies"):
    if candidate in h5p:
        deps_key = candidate
        break

if deps_key is None:
    fail("h5p.json missing required field: preloadedDependencies (or preloadDependencies)")

deps = h5p[deps_key]
if not isinstance(deps, list):
    fail(f"h5p.json field {deps_key} must be an array.")

for idx, dep in enumerate(deps):
    if not isinstance(dep, dict):
        fail(f"h5p.json {deps_key}[{idx}] must be an object.")
    for key in ("machineName", "majorVersion", "minorVersion"):
        if key not in dep:
            fail(f"h5p.json {deps_key}[{idx}] missing '{key}'.")

print("OK: content-import layout is valid.")
PY
