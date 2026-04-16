# Anti-patterns

Use this file when reviewing generated code or planning a refactor.

## Architecture smells

### Giant `App` class
Symptoms:
- hundreds of lines
- many `on_*` and `action_*` methods
- screen-specific logic everywhere

Fix:
- extract `Screen` classes
- extract composite widgets
- keep `App` for orchestration

### Inline CSS sprawl
Symptoms:
- long `CSS = """..."""` blocks
- styling mixed with business logic
- hard-to-test selectors

Fix:
- move to `.tcss`
- keep classes semantic
- keep styling separate from control flow

## Performance smells

### Blocking handlers
Symptoms:
- `time.sleep(...)`
- network calls in `on_*`
- subprocess execution in button handlers

Fix:
- workers, messages, notifications

### Heavy `compute_*`
Symptoms:
- I/O
- parsing
- long loops
- side effects

Fix:
- keep computes pure and cheap
- move work elsewhere

## Widget misuse

### Manual Rich tables inside `Static`
Use `DataTable` when the user needs focus, selection, cursor movement, or row interactions.

### Ad-hoc tab systems
Use `TabbedContent` / `TabPane`.

### Ad-hoc file tree widgets
Use `DirectoryTree`.

### Home-grown markdown panes
Use `MarkdownViewer` or `Markdown`.

## Testing smells

- no `run_test()` coverage
- brittle selectors tied to literal text
- behaviour changes with only manual testing
- layout-heavy app with no size-based test or snapshot coverage

## Browser parity smells

- writing files directly to the local filesystem with no browser-aware path
- assuming terminal width
- export/report flows without delivery APIs
