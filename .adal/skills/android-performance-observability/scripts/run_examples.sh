#!/usr/bin/env bash
    set -euo pipefail

    cat <<'EOF'
    Skill: Android Performance Observability
    Canonical path: skills/android-performance-observability
    Example commands:
    Happy path: python3 scripts/eval_triggers.py --skill android-performance-observability
Edge case: cd examples/orbittasks-xml && ./gradlew :app:assembleDebug
Failure recovery: cd examples/orbittasks-compose && ./gradlew :app:assembleDebug
    EOF
