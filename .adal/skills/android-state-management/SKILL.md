---
name: "android-state-management"
description: "Model screen state, events, reducers, and side effects for Android UIs with predictable lifecycle-aware ownership."
metadata:
  version: "0.1.0"
  category: "product"
  tags: ["android", "state", "ui-state", "viewmodel"]
  triggers:
    include: ["android ui state reducer", "state management in compose or xml android", "one-off events in android screen", "loading empty error state android", "viewmodel state container"]
    exclude: ["retrofit serialization", "play store release", "binary alignment"]
  owners: ["@android-agent-skills/maintainers"]
  test_targets: ["examples/orbittasks-compose", "examples/orbittasks-xml", "benchmarks/triggers.jsonl"]
---
# Android State Management

## When To Use
- Use this skill when the request is about: android ui state reducer, state management in compose or xml android, one-off events in android screen.
- Primary outcome: Model screen state, events, reducers, and side effects for Android UIs with predictable lifecycle-aware ownership.
- Handoff skills when the scope expands:
- `android-coroutines-flow`
- `android-ui-states-validation`

## Workflow
1. Confirm the user-visible journey, target device behavior, and failure states that matter.
2. Identify the owning screens, activities, destinations, and state holders for the flow.
3. Implement the flow with explicit loading, success, empty, and error handling.
4. Validate accessibility, configuration changes, and back-stack behavior in the showcase apps.
5. Escalate data, architecture, or release concerns to the specialized skills called out in the handoff notes.

## Guardrails
- Treat loading, empty, error, offline, and permission-denied states as first-class UI states.
- Do not hide navigation or permission side effects inside reusable UI components.
- Prefer lifecycle-aware APIs over manual callback chains.
- Keep deep links, intents, and permission prompts testable and observable.

## Anti-Patterns
- Assuming the happy path is enough for product flows.
- Hard-coding request codes or route strings in multiple places.
- Triggering navigation directly from repositories or network layers.
- Shipping flows without recovery UI for denied permissions or broken state.

## Remediation Examples
### Keep one immutable UI state surface
```kotlin
data class TaskBoardState(
    val tasks: List<TaskUiModel> = emptyList(),
    val isLoading: Boolean = false,
    val errorMessage: String? = null,
)
```

### Separate persistent state from one-off events
```kotlin
private val _uiState = MutableStateFlow(TaskBoardState())
val uiState: StateFlow<TaskBoardState> = _uiState.asStateFlow()

private val _events = MutableSharedFlow<TaskBoardEvent>(replay = 0)
val events: SharedFlow<TaskBoardEvent> = _events
```

### Reduce state updates instead of mutating UI directly
```kotlin
_uiState.update { state ->
    state.copy(isLoading = false, tasks = refreshedTasks, errorMessage = null)
}
```

## Examples
### Happy path
- Scenario: Drive the Compose task board from a single immutable screen state.
- Command: `cd examples/orbittasks-compose && ./gradlew :app:testDebugUnitTest`

### Edge case
- Scenario: Represent permission denied and sync failed states explicitly in the XML fixture.
- Command: `cd examples/orbittasks-xml && ./gradlew :app:testDebugUnitTest`

### Failure recovery
- Scenario: Separate state requests from coroutines, navigation, and UI validation prompts.
- Command: `python3 scripts/eval_triggers.py --skill android-state-management`

## Done Checklist
- The implementation path is explicit, minimal, and tied to the right Android surface.
- Relevant example commands and benchmark prompts have been exercised or updated.
- Handoffs to adjacent skills are documented when the request crosses boundaries.
- Official references cover the chosen pattern and the main migration or troubleshooting path.

## Official References
- [https://developer.android.com/topic/architecture/ui-layer/state-production](https://developer.android.com/topic/architecture/ui-layer/state-production)
- [https://developer.android.com/topic/architecture/ui-layer/events](https://developer.android.com/topic/architecture/ui-layer/events)
- [https://developer.android.com/topic/libraries/architecture/viewmodel](https://developer.android.com/topic/libraries/architecture/viewmodel)
- [https://developer.android.com/jetpack/compose/state](https://developer.android.com/jetpack/compose/state)
