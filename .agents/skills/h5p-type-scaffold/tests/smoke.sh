#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TMP_BASE="/tmp/h5p-type-scaffold-smoke"

assert_not_content_package_layout() {
  local dir="$1"
  local label="$2"

  if [[ -f "$dir/h5p.json" ]]; then
    echo "$label should not include h5p.json (content package file)" >&2
    exit 1
  fi

  if [[ -d "$dir/content" ]]; then
    echo "$label should not include content/ (content package folder)" >&2
    exit 1
  fi
}

cleanup() {
  rm -rf "$TMP_BASE"
}
trap cleanup EXIT

mkdir -p "$TMP_BASE"

echo "=== Smoke Test: h5p-type-scaffold ==="

echo "Testing content template (default snordian)..."
bash "$SCRIPT_DIR/scripts/scaffold.sh" \
  --title "Smoke Content" \
  --machine "H5P.SmokeContent" \
  --out "$TMP_BASE" >/dev/null

CONTENT_DIR="$TMP_BASE/h5p-smoke-content"

if [[ ! -f "$CONTENT_DIR/library.json" ]]; then
  echo "Missing library.json" >&2
  exit 1
fi

if ! grep -Eq '"runnable"[[:space:]]*:[[:space:]]*1' "$CONTENT_DIR/library.json"; then
  echo "Content library.json should be runnable" >&2
  exit 1
fi

if [[ ! -f "$CONTENT_DIR/src/entries/dist.js" ]]; then
  echo "Missing snordian entrypoint" >&2
  exit 1
fi

if [[ ! -f "$CONTENT_DIR/README.md" ]]; then
  echo "Missing content README.md" >&2
  exit 1
fi

if [[ ! -f "$CONTENT_DIR/DEV.md" ]]; then
  echo "Missing content DEV.md" >&2
  exit 1
fi

assert_not_content_package_layout "$CONTENT_DIR" "Content scaffold"

if grep -R -E -q '__[A-Z_]+' "$CONTENT_DIR"; then
  echo "Found unresolved template tokens in content output" >&2
  exit 1
fi

echo "Testing content template (vanilla)..."
bash "$SCRIPT_DIR/scripts/scaffold.sh" \
  --title "Smoke Vanilla" \
  --machine "H5P.SmokeVanilla" \
  --template vanilla \
  --out "$TMP_BASE" >/dev/null

VANILLA_DIR="$TMP_BASE/h5p-smoke-vanilla"

if [[ ! -f "$VANILLA_DIR/library.json" ]]; then
  echo "Missing vanilla library.json" >&2
  exit 1
fi

if ! grep -Eq '"runnable"[[:space:]]*:[[:space:]]*1' "$VANILLA_DIR/library.json"; then
  echo "Vanilla library.json should be runnable" >&2
  exit 1
fi

if [[ ! -f "$VANILLA_DIR/semantics.json" ]]; then
  echo "Missing vanilla semantics.json" >&2
  exit 1
fi

if [[ ! -f "$VANILLA_DIR/src/entries/h5p-smoke-vanilla.js" ]]; then
  echo "Missing vanilla entrypoint" >&2
  exit 1
fi

if [[ ! -f "$VANILLA_DIR/README.md" ]]; then
  echo "Missing vanilla README.md" >&2
  exit 1
fi

if [[ ! -f "$VANILLA_DIR/DEV.md" ]]; then
  echo "Missing vanilla DEV.md" >&2
  exit 1
fi

assert_not_content_package_layout "$VANILLA_DIR" "Vanilla scaffold"

if grep -R -E -q '__[A-Z_]+' "$VANILLA_DIR"; then
  echo "Found unresolved template tokens in vanilla output" >&2
  exit 1
fi

echo "Testing editor template..."
bash "$SCRIPT_DIR/scripts/scaffold.sh" \
  --title "Smoke Editor" \
  --kind editor \
  --machine "H5PEditor.SmokeEditor" \
  --out "$TMP_BASE" >/dev/null

EDITOR_DIR="$TMP_BASE/h5peditor-smoke-editor"

if [[ ! -f "$EDITOR_DIR/library.json" ]]; then
  echo "Missing editor library.json" >&2
  exit 1
fi

if ! grep -Eq '"runnable"[[:space:]]*:[[:space:]]*0' "$EDITOR_DIR/library.json"; then
  echo "Editor library.json should be non-runnable" >&2
  exit 1
fi

if [[ ! -f "$EDITOR_DIR/src/entries/dist.js" ]]; then
  echo "Missing editor entrypoint" >&2
  exit 1
fi

if [[ ! -f "$EDITOR_DIR/README.md" ]]; then
  echo "Missing editor README.md" >&2
  exit 1
fi

if [[ ! -f "$EDITOR_DIR/DEV.md" ]]; then
  echo "Missing editor DEV.md" >&2
  exit 1
fi

assert_not_content_package_layout "$EDITOR_DIR" "Editor scaffold"

if grep -R -E -q '__[A-Z_]+' "$EDITOR_DIR"; then
  echo "Found unresolved template tokens in editor output" >&2
  exit 1
fi

if [[ ! -x "$SCRIPT_DIR/scripts/h5p-dev.sh" ]]; then
  echo "Missing or non-executable h5p-dev.sh helper" >&2
  exit 1
fi

if [[ ! -x "$SCRIPT_DIR/scripts/validate-package.sh" ]]; then
  echo "Missing or non-executable validate-package.sh helper" >&2
  exit 1
fi

if [[ ! -x "$SCRIPT_DIR/scripts/pack.sh" ]]; then
  echo "Missing or non-executable pack.sh helper" >&2
  exit 1
fi

echo "Testing pack.sh (no directory entries)..."
# Create a minimal built library to pack
PACK_DIR="$TMP_BASE/pack-test-lib"
mkdir -p "$PACK_DIR/dist" "$PACK_DIR/language"
cat > "$PACK_DIR/library.json" <<'JSON'
{
  "title": "Pack Test",
  "machineName": "H5P.PackTest",
  "majorVersion": 1,
  "minorVersion": 0,
  "patchVersion": 0,
  "runnable": 1,
  "preloadedJs": [{ "path": "dist/h5p-pack-test.js" }],
  "preloadedCss": [{ "path": "dist/h5p-pack-test.css" }]
}
JSON
cat > "$PACK_DIR/semantics.json" <<'JSON'
[{ "name": "text", "type": "text", "label": "Text" }]
JSON
echo "console.log('test');" > "$PACK_DIR/dist/h5p-pack-test.js"
echo ".test{}" > "$PACK_DIR/dist/h5p-pack-test.css"
echo '{"semantics":[]}' > "$PACK_DIR/language/en.json"
cat > "$PACK_DIR/.h5pignore" <<'TXT'
node_modules
src
.git
.babelrc
.h5pignore
webpack.config.js
package.json
package-lock.json
README.md
TXT

PACK_OUT="$TMP_BASE/H5P.PackTest.h5p"
bash "$SCRIPT_DIR/scripts/pack.sh" --dir "$PACK_DIR" --out "$PACK_OUT" --strict >/dev/null

if [[ ! -f "$PACK_OUT" ]]; then
  echo "pack.sh did not create output file" >&2
  exit 1
fi

# Verify no directory entries in the zip
DIR_ENTRIES=$(zipinfo -1 "$PACK_OUT" | grep '/$' || true)
if [[ -n "$DIR_ENTRIES" ]]; then
  echo "pack.sh output contains directory entries:" >&2
  echo "$DIR_ENTRIES" >&2
  exit 1
fi

# Verify expected files are present
for expected in library.json semantics.json dist/h5p-pack-test.js dist/h5p-pack-test.css language/en.json; do
  if ! zipinfo -1 "$PACK_OUT" | grep -qx "$expected"; then
    echo "pack.sh output missing expected file: $expected" >&2
    exit 1
  fi
done

# Verify dotfiles are excluded
DOTFILES=$(zipinfo -1 "$PACK_OUT" | grep '/\.\|^\.' || true)
if [[ -n "$DOTFILES" ]]; then
  echo "pack.sh output contains dotfiles:" >&2
  echo "$DOTFILES" >&2
  exit 1
fi

echo "Testing package validator..."
bash "$SCRIPT_DIR/scripts/validate-package.sh" \
  --mode library-install \
  --dir "$CONTENT_DIR" >/dev/null

CONTENT_PKG_DIR="$TMP_BASE/content-import-example"
mkdir -p "$CONTENT_PKG_DIR/content"

cat > "$CONTENT_PKG_DIR/h5p.json" <<'JSON'
{
  "title": "Smoke Content Import",
  "language": "en",
  "mainLibrary": "H5P.SmokeContent",
  "license": "U",
  "embedTypes": ["iframe"],
  "preloadedDependencies": [
    { "machineName": "H5P.SmokeContent", "majorVersion": 1, "minorVersion": 0 }
  ]
}
JSON

cat > "$CONTENT_PKG_DIR/content/content.json" <<'JSON'
{
  "text": "hello"
}
JSON

bash "$SCRIPT_DIR/scripts/validate-package.sh" \
  --mode content-import \
  --dir "$CONTENT_PKG_DIR" >/dev/null

if bash "$SCRIPT_DIR/scripts/validate-package.sh" \
  --mode library-install \
  --dir "$CONTENT_PKG_DIR" >/dev/null 2>&1; then
  echo "library-install validator should fail for content package layout" >&2
  exit 1
fi

if bash "$SCRIPT_DIR/scripts/validate-package.sh" \
  --mode content-import \
  --dir "$CONTENT_DIR" >/dev/null 2>&1; then
  echo "content-import validator should fail for library package layout" >&2
  exit 1
fi

echo "✓ Smoke tests passed"
