---
name: "android-serialization-offline-sync"
description: "Coordinate serialization, caching, conflict handling, and offline-first sync flows in Android apps."
metadata:
  version: "0.1.0"
  category: "data-platform"
  tags: ["android", "serialization", "offline-first", "sync"]
  triggers:
    include: ["offline sync android", "serialization model mapping android", "conflict resolution android cache", "sync queue android app", "json model migration android"]
    exclude: ["permission prompt only", "viewbinding only", "release tagging only"]
  owners: ["@android-agent-skills/maintainers"]
  test_targets: ["examples/orbittasks-compose", "examples/orbittasks-xml", "benchmarks/triggers.jsonl"]
---
# Android Serialization Offline Sync

## When To Use
- Use this skill when the request is about: offline sync android, serialization model mapping android, conflict resolution android cache.
- Primary outcome: Coordinate serialization, caching, conflict handling, and offline-first sync flows in Android apps.
- Handoff skills when the scope expands:
- `android-networking-retrofit-okhttp`
- `android-room-database`

## Workflow
1. Confirm the data source, persistence boundary, sync model, and device capability involved.
2. Model contracts explicitly before wiring network, storage, media, or background APIs.
3. Apply the recommended AndroidX or platform pattern with migration-safe defaults.
4. Validate offline, retry, and process death behavior against the sample apps and scenarios.
5. Escalate security, performance, or release risk to the linked supporting skills when needed.

## Guardrails
- Prefer typed models and explicit serializers over ad-hoc maps or bundles.
- Keep background work idempotent and cancellation-aware.
- Do not leak storage, media, or networking details into presentation code.
- Treat user data durability, privacy, and migration paths as part of the implementation.

## Anti-Patterns
- Blocking the main thread with disk or network calls.
- Treating retryable sync failures as terminal user-facing errors.
- Mixing cache models and wire models without a mapping layer.
- Requesting broad storage or notification capabilities when a narrower API exists.

## Examples
### Happy path
- Scenario: Sync local task edits to a remote model with explicit mapping.
- Command: `cd examples/orbittasks-compose && ./gradlew :app:testDebugUnitTest`

### Edge case
- Scenario: Recover when remote and local timestamps disagree after offline edits.
- Command: `cd examples/orbittasks-xml && ./gradlew :app:testDebugUnitTest`

### Failure recovery
- Scenario: Keep sync/serialization work separate from pure networking or Room-only requests.
- Command: `python3 scripts/eval_triggers.py --skill android-serialization-offline-sync`

## Done Checklist
- The implementation path is explicit, minimal, and tied to the right Android surface.
- Relevant example commands and benchmark prompts have been exercised or updated.
- Handoffs to adjacent skills are documented when the request crosses boundaries.
- Official references cover the chosen pattern and the main migration or troubleshooting path.

## Official References
- [https://developer.android.com/topic/architecture/data-layer/offline-first](https://developer.android.com/topic/architecture/data-layer/offline-first)
- [https://developer.android.com/kotlin/parcelize](https://developer.android.com/kotlin/parcelize)
- [https://kotlinlang.org/docs/serialization.html](https://kotlinlang.org/docs/serialization.html)
- [https://developer.android.com/topic/architecture/data-layer](https://developer.android.com/topic/architecture/data-layer)
