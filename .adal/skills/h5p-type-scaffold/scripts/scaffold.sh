#!/bin/bash
set -euo pipefail

# H5P content type scaffolder

usage() {
  cat >&2 <<'USAGE'
Usage: scaffold.sh [options]

Options:
  --title "Title"           Human-readable title (default: "Hello H5P")
  --machine "H5P.Name"      Machine name (default: "H5P.HelloH5P" or "H5PEditor.HelloH5P")
  --version "1.0.0"         Version (default: "1.0.0")
  --description "Text"      Short description
  --author "Name"           Author name
  --license "MIT"           License (default: "MIT")
  --kind "content|editor"   Library kind (default: "content")
  --template "name"         Template name (default: "snordian" for content, "editor" for editor)
  --out "/path"             Output directory (default: current directory)
  --dir "name"              Target directory name (default: h5p-<slug>)
  --help                    Show help
USAGE
}

TMP_DIR="$(mktemp -d)"
cleanup() {
  rm -rf "$TMP_DIR"
}
trap cleanup EXIT

TITLE="Hello H5P"
MACHINE="H5P.HelloH5P"
MACHINE_SET=0
VERSION="1.0.0"
DESCRIPTION="Example H5P content type"
AUTHOR="Your Name"
LICENSE="MIT"
KIND="content"
TEMPLATE=""
TEMPLATE_SET=0
OUT_DIR="."
TARGET_DIR_NAME=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --title)
      TITLE="$2"; shift 2 ;;
    --machine)
      MACHINE="$2"; MACHINE_SET=1; shift 2 ;;
    --version)
      VERSION="$2"; shift 2 ;;
    --description)
      DESCRIPTION="$2"; shift 2 ;;
    --author)
      AUTHOR="$2"; shift 2 ;;
    --license)
      LICENSE="$2"; shift 2 ;;
    --kind)
      KIND="$2"; shift 2 ;;
    --template)
      TEMPLATE="$2"; TEMPLATE_SET=1; shift 2 ;;
    --out)
      OUT_DIR="$2"; shift 2 ;;
    --dir)
      TARGET_DIR_NAME="$2"; shift 2 ;;
    --help)
      usage; exit 0 ;;
    *)
      echo "Unknown option: $1" >&2
      usage
      exit 1
      ;;
  esac
done

if [[ "$KIND" != "content" && "$KIND" != "editor" ]]; then
  echo "Invalid --kind. Expected content or editor." >&2
  exit 1
fi

if [[ "$KIND" == "editor" && "$MACHINE_SET" -eq 0 ]]; then
  MACHINE="H5PEditor.HelloH5P"
fi

if [[ "$KIND" == "content" ]]; then
  if [[ ! "$MACHINE" =~ ^H5P\.[A-Za-z0-9_]+$ ]]; then
    echo "Invalid --machine. Expected format like H5P.MyContentType" >&2
    exit 1
  fi
  BASE_NAME="${MACHINE#H5P.}"
else
  if [[ ! "$MACHINE" =~ ^H5PEditor\.[A-Za-z0-9_]+$ ]]; then
    echo "Invalid --machine. Expected format like H5PEditor.MyWidget" >&2
    exit 1
  fi
  BASE_NAME="${MACHINE#H5PEditor.}"
fi

SLUG=$(echo "$BASE_NAME" | sed -E 's/([a-z0-9])([A-Z])/\1-\2/g' | tr '[:upper:]' '[:lower:]')

IFS='.' read -r MAJOR MINOR PATCH <<< "$VERSION"
MAJOR="${MAJOR:-1}"
MINOR="${MINOR:-0}"
PATCH="${PATCH:-0}"

if [[ -z "$TARGET_DIR_NAME" ]]; then
  if [[ "$KIND" == "editor" ]]; then
    TARGET_DIR_NAME="h5peditor-$SLUG"
  else
    TARGET_DIR_NAME="h5p-$SLUG"
  fi
fi

TARGET_DIR="$OUT_DIR/$TARGET_DIR_NAME"
TEMPLATE_BASE="$(cd "$(dirname "$0")/.." && pwd)/assets/templates"
if [[ "$TEMPLATE_SET" -eq 0 ]]; then
  if [[ "$KIND" == "editor" ]]; then
    TEMPLATE="editor"
  else
    TEMPLATE="snordian"
  fi
fi
TEMPLATE_DIR="$TEMPLATE_BASE/$TEMPLATE"

if [[ ! -d "$TEMPLATE_DIR" ]]; then
  echo "Unknown template: $TEMPLATE" >&2
  echo "Available templates: $(ls -1 "$TEMPLATE_BASE" | tr '\n' ' ')" >&2
  exit 1
fi

if [[ -e "$TARGET_DIR" ]]; then
  echo "Target directory already exists: $TARGET_DIR" >&2
  exit 1
fi

mkdir -p "$TMP_DIR/work"
cp -R "$TEMPLATE_DIR/." "$TMP_DIR/work"

python - <<PY
import os
import json

work = os.path.join("$TMP_DIR", "work")
base_name = "$BASE_NAME"
widget_name = (base_name[:1].lower() + base_name[1:]) if base_name else "widget"
editor_machine = f"H5PEditor.{base_name}" if base_name else "H5PEditor.Widget"
replacements = {
  "__TITLE__": "$TITLE",
  "__DESCRIPTION__": "$DESCRIPTION",
  "__MAJOR__": "$MAJOR",
  "__MINOR__": "$MINOR",
  "__PATCH__": "$PATCH",
  "__MACHINE__": "$MACHINE",
  "__EDITOR_MACHINE__": editor_machine,
  "__SLUG__": "$SLUG",
  "__CLASS__": "$BASE_NAME",
  "__WIDGET__": widget_name,
  "__AUTHOR__": "$AUTHOR",
  "__LICENSE__": "$LICENSE",
  "__VERSION__": "$VERSION",
}

for root, _, files in os.walk(work):
  for name in files:
    path = os.path.join(root, name)
    with open(path, "r", encoding="utf-8") as f:
      data = f.read()
    for key, value in replacements.items():
      data = data.replace(key, value)
    with open(path, "w", encoding="utf-8") as f:
      f.write(data)

# Rename files containing __SLUG__
for root, _, files in os.walk(work):
  for name in files:
    if "__SLUG__" in name:
      new_name = name.replace("__SLUG__", "$SLUG")
      os.rename(os.path.join(root, name), os.path.join(root, new_name))
PY

mkdir -p "$OUT_DIR"
cp -R "$TMP_DIR/work" "$TARGET_DIR"

cat <<JSON
{
  "path": "$TARGET_DIR",
  "machineName": "$MACHINE",
  "slug": "$SLUG",
  "title": "$TITLE",
  "version": "$VERSION"
}
JSON
