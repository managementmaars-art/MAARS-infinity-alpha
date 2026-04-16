#!/usr/bin/env bash
# Detection patterns for SRP violations

set -euo pipefail

# Usage: ./detect-patterns.sh <pattern-type> <project-path>
# Pattern types: method-and, god-class, constructor-params, optional-config

PATTERN_TYPE="${1:-all}"
PROJECT_PATH="${2:-.}"

case "$PATTERN_TYPE" in
  "method-and")
    echo "🔍 Detecting methods with 'and' in name..."
    # Using ast-grep via mcp-cli
    mcp-cli call mcp__ast-grep__find_code '{
      "pattern": "def $NAME_and_$REST",
      "language": "python",
      "project_folder": "'"$PROJECT_PATH"'"
    }'
    ;;

  "god-class")
    echo "🔍 Detecting God classes (>15 methods)..."
    mcp-cli call mcp__ast-grep__find_code_by_rule '{
      "yaml": "id: god-class\nlanguage: python\nrule:\n  pattern: |\n    class $NAME:\n      $$$BODY\n  has:\n    stopBy: end\n    kind: function_definition\n    count: { min: 15 }",
      "project_folder": "'"$PROJECT_PATH"'"
    }'
    ;;

  "constructor-params")
    echo "🔍 Detecting constructors with many parameters (>5)..."
    mcp-cli call mcp__ast-grep__find_code_by_rule '{
      "yaml": "id: constructor-params\nlanguage: python\nrule:\n  pattern: |\n    def __init__(self, $$$PARAMS):\n      $$$BODY\n  constraints:\n    PARAMS:\n      count: { min: 5 }",
      "project_folder": "'"$PROJECT_PATH"'"
    }'
    ;;

  "optional-config")
    echo "🔍 Detecting optional config anti-pattern..."
    mcp-cli call mcp__ast-grep__find_code_by_rule '{
      "yaml": "id: optional-config\nlanguage: python\nrule:\n  pattern: \"$NAME: $TYPE | None = None\"\n  inside:\n    kind: function_definition\n    pattern: \"def __init__\"",
      "project_folder": "'"$PROJECT_PATH"'"
    }'
    ;;

  "all")
    echo "🔍 Running all SRP detection patterns..."
    echo ""
    "$0" method-and "$PROJECT_PATH"
    echo ""
    "$0" god-class "$PROJECT_PATH"
    echo ""
    "$0" constructor-params "$PROJECT_PATH"
    echo ""
    "$0" optional-config "$PROJECT_PATH"
    ;;

  *)
    echo "❌ Unknown pattern type: $PATTERN_TYPE"
    echo "Valid types: method-and, god-class, constructor-params, optional-config, all"
    exit 1
    ;;
esac
