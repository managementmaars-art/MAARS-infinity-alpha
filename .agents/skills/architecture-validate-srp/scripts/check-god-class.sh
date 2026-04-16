#!/usr/bin/env bash
# God Class Detection Script
# Checks for classes with too many dependencies or low cohesion

set -euo pipefail

FILE="${1:-}"

if [[ -z "$FILE" ]]; then
  echo "Usage: $0 <python-file>"
  exit 1
fi

if [[ ! -f "$FILE" ]]; then
  echo "Error: File not found: $FILE"
  exit 1
fi

echo "God Class Detection"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "File: $FILE"
echo ""

# Check 1: Count constructor parameters
echo "[CHECK 1] Constructor parameters..."

constructors=$(grep -A 20 "def __init__" "$FILE" || true)

if [[ -n "$constructors" ]]; then
  # Count parameters (rough estimate by counting commas)
  param_count=$(echo "$constructors" | head -n 1 | tr -cd ',' | wc -c)

  if [[ $param_count -gt 8 ]]; then
    echo "❌ CRITICAL: $param_count parameters (threshold: 8)"
    echo "   This is a strong God Class indicator"
  elif [[ $param_count -gt 4 ]]; then
    echo "⚠️  WARNING: $param_count parameters (threshold: 4)"
    echo "   Consider splitting responsibilities"
  else
    echo "✅ OK: $param_count parameters"
  fi
else
  echo "ℹ️  No constructors found"
fi
echo ""

# Check 2: Count methods
echo "[CHECK 2] Method count..."

method_count=$(grep -c "^\s*def " "$FILE" || true)

if [[ $method_count -gt 25 ]]; then
  echo "❌ CRITICAL: $method_count methods (threshold: 25)"
elif [[ $method_count -gt 15 ]]; then
  echo "⚠️  WARNING: $method_count methods (threshold: 15)"
else
  echo "✅ OK: $method_count methods"
fi
echo ""

# Check 3: File size
echo "[CHECK 3] File size..."

line_count=$(wc -l < "$FILE")

if [[ $line_count -gt 500 ]]; then
  echo "❌ CRITICAL: $line_count lines (threshold: 500)"
elif [[ $line_count -gt 300 ]]; then
  echo "⚠️  WARNING: $line_count lines (threshold: 300)"
else
  echo "✅ OK: $line_count lines"
fi
echo ""

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Recommendation:"

if [[ $param_count -gt 8 ]] || [[ $method_count -gt 25 ]] || [[ $line_count -gt 500 ]]; then
  echo "❌ This class exhibits God Class characteristics"
  echo "   Strongly recommend refactoring by actor responsibility"
  exit 1
elif [[ $param_count -gt 4 ]] || [[ $method_count -gt 15 ]] || [[ $line_count -gt 300 ]]; then
  echo "⚠️  This class may be doing too much"
  echo "   Consider reviewing for multiple actors"
  exit 0
else
  echo "✅ No God Class indicators detected"
  exit 0
fi
