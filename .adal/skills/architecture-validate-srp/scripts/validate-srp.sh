#!/usr/bin/env bash
# SRP Validation Script
# Detects Single Responsibility Principle violations

set -euo pipefail

# Default values
LEVEL="thorough"
PATH_TO_CHECK="src/"
OUTPUT_FORMAT="text"

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --level=*)
      LEVEL="${1#*=}"
      shift
      ;;
    --output-format=*)
      OUTPUT_FORMAT="${1#*=}"
      shift
      ;;
    *)
      PATH_TO_CHECK="$1"
      shift
      ;;
  esac
done

echo "SRP Validation Report"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Path: $PATH_TO_CHECK"
echo "Level: $LEVEL"
echo ""

violations=0
warnings=0

# Level 1: Naming pattern violations
if [[ "$LEVEL" == "fast" ]] || [[ "$LEVEL" == "thorough" ]] || [[ "$LEVEL" == "full" ]]; then
  echo "[LEVEL 1] Checking naming patterns..."

  # Find methods with "and" in name
  naming_violations=$(grep -rn "def .*_and_.*\|function.*And.*" "$PATH_TO_CHECK" 2>/dev/null || true)

  if [[ -n "$naming_violations" ]]; then
    echo "⚠️  Methods with 'and' in name found:"
    echo "$naming_violations" | while IFS= read -r line; do
      warnings=$((warnings + 1))
      echo "  - $line"
    done
  else
    echo "✅ No naming pattern violations"
  fi
  echo ""
fi

# Level 2: Size metrics
if [[ "$LEVEL" == "thorough" ]] || [[ "$LEVEL" == "full" ]]; then
  echo "[LEVEL 2] Checking size metrics..."

  # Find large files (>300 lines)
  large_files=$(find "$PATH_TO_CHECK" -name "*.py" -o -name "*.js" -o -name "*.ts" 2>/dev/null | \
    xargs wc -l 2>/dev/null | \
    awk '$1 > 300 {print}' || true)

  if [[ -n "$large_files" ]]; then
    echo "⚠️  Large files found (>300 lines):"
    echo "$large_files" | while IFS= read -r line; do
      warnings=$((warnings + 1))
      echo "  - $line"
    done
  else
    echo "✅ No oversized files"
  fi
  echo ""
fi

# Level 3: Constructor parameters
if [[ "$LEVEL" == "thorough" ]] || [[ "$LEVEL" == "full" ]]; then
  echo "[LEVEL 3] Checking constructor dependencies..."

  # Find constructors with many parameters (Python)
  constructor_violations=$(grep -A 10 "def __init__" "$PATH_TO_CHECK"/**/*.py 2>/dev/null | \
    grep -E "self,.*,.*,.*,.*," || true)

  if [[ -n "$constructor_violations" ]]; then
    echo "⚠️  Constructors with >4 parameters:"
    echo "$constructor_violations" | while IFS= read -r line; do
      warnings=$((warnings + 1))
      echo "  - $line"
    done
  else
    echo "✅ No constructor violations"
  fi
  echo ""
fi

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Summary:"
echo "  Critical violations: $violations"
echo "  Warnings: $warnings"

if [[ $violations -gt 0 ]]; then
  echo ""
  echo "❌ SRP validation failed - critical violations found"
  exit 1
elif [[ $warnings -gt 0 ]]; then
  echo ""
  echo "⚠️  SRP validation passed with warnings"
  exit 0
else
  echo ""
  echo "✅ SRP validation passed - no violations found"
  exit 0
fi
