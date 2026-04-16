#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-.}"

if [[ ! -d "$ROOT" ]]; then
  echo "error: root path is not a directory: $ROOT" >&2
  exit 1
fi

find "$ROOT" \
  \( \
    -path "*/.git/*" -o \
    -path "*/node_modules/*" -o \
    -path "*/dist/*" -o \
    -path "*/build/*" -o \
    -path "*/target/*" -o \
    -path "*/.idea/*" -o \
    -path "*/.venv/*" -o \
    -path "*/venv/*" -o \
    -path "*/__pycache__/*" \
  \) -prune -o \
  -type f \
  \( \
    -iname "*.md" -o \
    -iname "*.mdx" -o \
    -iname "*.txt" -o \
    -iname "*.rst" -o \
    -iname "*.adoc" -o \
    -iname "*.asciidoc" -o \
    -iname "*.pdf" -o \
    -iname "*.docx" -o \
    -iname "*.mmd" -o \
    -iname "*.mermaid" -o \
    -iname "*.puml" -o \
    -iname "*.plantuml" -o \
    -iname "*.drawio" -o \
    -iname "*.d2" -o \
    -iname "*.svg" -o \
    -iname "*.png" -o \
    -iname "*.jpg" -o \
    -iname "*.jpeg" -o \
    -iname "*.webp" \
  \) -print0 | \
while IFS= read -r -d '' file; do
  rel="${file#./}"
  if [[ "$ROOT" != "." ]]; then
    prefix="${ROOT%/}/"
    rel="${file#"$prefix"}"
  fi

  name_lower="$(printf '%s' "$rel" | tr '[:upper:]' '[:lower:]')"
  category="doc"
  case "$name_lower" in
    *.mmd|*.mermaid|*.puml|*.plantuml|*.drawio|*.d2)
      category="diagram-src"
      ;;
    *.svg|*.png|*.jpg|*.jpeg|*.webp)
      category="diagram-img"
      ;;
  esac

  size_bytes="$(wc -c < "$file" | tr -d '[:space:]')"
  printf '%s\t%s\t%s\n' "$category" "$size_bytes" "$rel"
done | sort -t $'\t' -k1,1 -k3,3 | awk 'BEGIN {print "category\tsize_bytes\tpath"} {print}'
