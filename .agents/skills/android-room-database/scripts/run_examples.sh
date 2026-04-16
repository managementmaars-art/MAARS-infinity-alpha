#!/usr/bin/env bash
    set -euo pipefail

    cat <<'EOF'
    Skill: Android Room Database
    Canonical path: skills/android-room-database
    Example commands:
    Happy path: cd examples/orbittasks-compose && ./gradlew :app:testDebugUnitTest
Edge case: python3 scripts/eval_triggers.py --skill android-room-database
Failure recovery: cd examples/orbittasks-xml && ./gradlew :app:testDebugUnitTest
    EOF
