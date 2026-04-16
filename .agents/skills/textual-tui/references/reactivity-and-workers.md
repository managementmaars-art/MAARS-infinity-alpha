# Reactivity and workers

This file is the default playbook for keeping Textual apps responsive.

## State choices

### `reactive`
Use when a state change should participate in automatic refresh/watcher behaviour.

Good fits:
- current filter text
- selected row key
- current step index
- UI-visible derived state inputs

### `var`
Use when you want stored state without the heavier reactive machinery.

Good fits:
- caches
- internal flags
- values that do not need automatic redraw behaviour

## Derived state

### `compute_*`
Use for cheap, deterministic derived values.

Rules:
- keep it fast
- no I/O
- no sleeps
- no subprocesses
- no network
- no UI mutation side effects

Bad smell:
- a compute method opening files, calling APIs, or rebuilding large structures repeatedly

### `watch_*`
Use to react to a state change with UI updates or local orchestration.

Good fits:
- updating a detail pane
- toggling classes
- switching visible content
- adjusting focus after state changes

Do not put long-running work here.

### `set_reactive`
Use when you need to set reactive state before mount without firing watchers too early.

Typical case:
- initial state restored from config or CLI args

## Workers

Use a worker whenever the task might block input or repaint.

Move these off the main event path:
- network calls
- subprocess work
- parsing large files
- sleeps / retries / polling
- expensive search
- filesystem scans
- model inference or streaming wrappers

### `@work`
Best for app/widget methods that naturally launch background work.

Patterns:
- search as the user types
- background refresh
- async fetch with result-handling in one place

### `run_worker(...)`
Good when launching work dynamically or from helper functions.

### `exclusive=True`
Use for “latest request wins”.

Typical cases:
- live search
- debounced filtering
- preview generation
- background refresh keyed by the current selection

If an older request finishes later than a newer request, it should not overwrite the UI.

## Thread workers

If you use thread workers:
- do not mutate widgets directly from the worker thread
- route updates back via `post_message(...)` or `call_from_thread(...)`

## Small but valuable APIs

### `notify(...)`
Use for lightweight global feedback:
- saved
- exported
- failed
- cancelled

### `batch_update()`
Use when a single user action causes many widget changes. It reduces flicker and intermediate layouts.

### `anchor()`
Use on scrollable transcript/log/chat views to keep the viewport pinned to the latest content.

### `begin_capture_print()`
Useful when you want `print(...)` output to land inside the app for debugging or monitoring.

## Default pattern for live search

1. input changes
2. store the current query reactively
3. launch a worker with `exclusive=True`
4. when results return, update the table/list
5. update the detail pane and status
6. notify on recoverable failures

## Red flags

- `time.sleep(...)` in `on_*` or `action_*`
- `requests.get(...)` inside watchers or handlers
- expensive loops in `compute_*`
- repeated `query_one(...)` calls all over the app because state and composition are muddled
- UI updates from a thread worker without marshalling back to the app thread
