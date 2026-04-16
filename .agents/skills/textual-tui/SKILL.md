---
name: textual-tui
description: Build, refactor, debug, test, and package Python terminal user interfaces with Textual. Use when the user wants a TUI, terminal dashboard, admin console, multi-screen workflow, keyboard-first tool, data explorer, file browser, markdown or log viewer, editor, command palette, browser-served console app, or a migration from curses/Rich-only UI to Textual—even if they never say “Textual”. Covers TCSS and themes, built-in widgets, screens and modes, reactive state, workers, browser delivery APIs, and pytest Pilot or snapshot testing.
license: Proprietary
compatibility: Requires Python 3.9+ and the Textual package. `textual-dev`, `pytest`, and `pytest-asyncio` are strongly recommended. `pytest-textual-snapshot` and `textual[syntax]` are optional extras.
metadata:
  version: "2.0"
  scope: "Textual apps, TUIs, browser-served Textual apps, testing, refactors"
---

Use this skill when the task is fundamentally about **building or changing a Textual app**, not merely printing Rich output or writing a non-interactive CLI.

## Start by classifying the app

Pick the closest shape before writing code:

1. **Single-screen shell**  
   One main view with panels, tables, forms, or logs. Prefer containers plus built-in widgets.

2. **Multi-screen workflow**  
   Large context changes, separate flows, or drill-down views. Prefer `Screen` / `ModalScreen`.

3. **Multi-mode admin app**  
   Persistent top-level areas such as “dashboard / jobs / settings / logs”. Prefer named `MODES`, screen stacks, and command palette support.

4. **Data explorer**  
   Records plus details, filters, or side panes. Prefer `DataTable`, details panel, responsive breakpoints, and keyboard navigation.

5. **Document or filesystem tool**  
   Prefer `DirectoryTree`, `MarkdownViewer`, `TextArea`, `Tree`, and delivery APIs for export/download.

6. **Chat / streaming / long-running task UI**  
   Prefer a scrollable transcript or log plus `@work` / workers for background operations.

If the user has not chosen an architecture, choose one and proceed.

## Default engineering stance

- Prefer **built-in widgets first**. Only hand-roll behaviour when a built-in widget clearly does not fit.
- Keep the **`App` thin**. Move screen-specific logic into `Screen` classes and reusable composite widgets.
- Prefer **`.tcss` files** over inline `CSS` once styling grows beyond a toy example.
- Use **IDs and semantic classes** deliberately so styling and Pilot tests stay stable.
- Design for **narrow terminals first**, then add split panes and breakpoint-driven layouts.
- Leave behind **tests** whenever behaviour changes.

## Choose the right Textual primitive

- Use **`Screen`** when navigation changes the user’s working context.
- Use **`ModalScreen`** for short interruptions: confirmations, pickers, destructive actions.
- Use **`ContentSwitcher`** for wizard steps or one-screen subflows.
- Use **named `MODES`** when the app has durable top-level areas with separate navigation stacks.
- Use **command palette providers** when there are many actions, bindings, or discoverability matters.
- Use **workers** for network, subprocess, parsing, search, sleeps, or anything that may block input.

See:
- [Architecture decision tree](references/architecture-decision-tree.md)
- [Screens, modes, and command palette](references/screens-modes-command-palette.md)

## Widget-first selection rules

Before inventing custom widgets, check [the widget atlas](references/widget-selection-atlas.md).

Common defaults:
- `DataTable` for record-heavy views
- `DirectoryTree` for filesystem navigation
- `MarkdownViewer` for rich document views
- `TextArea` for editing
- `TabbedContent` for grouped settings or alternate panes
- `Log` / `RichLog` for live output
- `SelectionList`, `OptionList`, `ListView`, `Tree`, `Select`, `Switch`, `Input`, `Button` for most interaction needs

## Reactivity and workers

Use the playbook in [reactivity and workers](references/reactivity-and-workers.md).

Core rules:
- Put fast derived state in `compute_*`, but keep it cheap and side-effect free.
- Use `watch_*` for UI reactions, not blocking work.
- Use `var` when you want state without automatic refresh machinery.
- Use `set_reactive` before mount when initial state changes should not trip watchers early.
- Move blocking work into `@work` or `run_worker(...)`.
- Use `exclusive=True` for stale-search cancellation and similar “latest request wins” flows.
- For thread workers, update the UI via messages or `call_from_thread`.

## Browser, dev loop, and delivery

Textual may run in a terminal or be served to a browser. Build with both in mind when relevant.

- Use `textual run --dev` while iterating.
- Use `textual console` and devtools when behaviour is unclear.
- Use `textual serve` when browser parity matters.
- Prefer `deliver_text`, `deliver_binary`, or `deliver_screenshot` for browser-friendly exports and downloads.
- Use `open_url` when handing off to the user’s browser is appropriate.

See:
- [Browser and delivery guide](references/browser-and-delivery.md)
- [Packaging and CI](references/packaging-and-ci.md)

## Testing is part of the feature

Default output after any non-trivial change:

1. one smoke test with `run_test()`
2. one behaviour test for the changed flow
3. one narrow-terminal or alternate-size test when layout matters
4. one snapshot test when the view structure matters visually

See [testing matrix](references/testing-matrix.md).

## When working on an existing project

Start with the scripts, then refine by hand:

1. `python scripts/inspect_textual_project.py <project>`
2. `python scripts/audit_textual_project.py <project>`
3. Generate scaffolds or tests only after you understand the existing structure.

Use the audit to catch:
- oversized `App` classes
- blocking handlers
- missing breakpoints
- missed built-in widget opportunities
- missing command palette or delivery APIs
- missing Pilot tests

## Bundled scripts

- `scripts/scaffold_textual_app.py`  
  Generate starter apps, TCSS, tests, optional `pyproject.toml`, and CI workflow.

- `scripts/inspect_textual_project.py`  
  Inventory app classes, screens, widgets, bindings, IDs, workers, and styling.

- `scripts/audit_textual_project.py`  
  Heuristic architecture/performance/test audit for an existing Textual project.

- `scripts/generate_pilot_tests.py`  
  Emit starter smoke and behaviour tests for an existing app.

- `scripts/dump_dom_and_bindings.py`  
  If Textual is installed, launch an app under `run_test()` and dump DOM and active bindings.

- `scripts/emit_textual_pyproject.py`  
  Generate a packageable Hatch-based `pyproject.toml`.

- `scripts/emit_github_actions_ci.py`  
  Generate a GitHub Actions workflow for Textual tests.

- `scripts/build_upstream_pattern_atlas.py`  
  Summarise a local Textual repo snapshot into `references/repo-map.md` and `references/upstream-pattern-atlas.md`.

- `scripts/self_check.py`  
  Compile scripts and scaffold all bundled templates as a package validation step.

## Bundled starter templates

Available scaffolds:
- `dashboard`
- `form`
- `chat`
- `data-explorer`
- `file-browser`
- `settings`
- `wizard`
- `log-monitor`
- `editor`
- `admin-modes`
- `download-demo`

List them with:

```bash
python scripts/scaffold_textual_app.py --list-templates
```

Generate one with:

```bash
python scripts/scaffold_textual_app.py \
  --template data-explorer \
  --module my_app \
  --class-name MyApp \
  --app-title "My App" \
  --output-dir .
```

## Output checklist

Before you finish, aim to leave behind:

- a clear app structure
- stable IDs/classes for styling and tests
- TCSS separated from Python unless the app is tiny
- background work off the main event path
- keyboard-discoverable actions
- responsive layout decisions
- at least a smoke test and one behaviour test
- notes on how to run the app in dev mode

## Read next as needed

- [Architecture decision tree](references/architecture-decision-tree.md)
- [Widget selection atlas](references/widget-selection-atlas.md)
- [Reactivity and workers](references/reactivity-and-workers.md)
- [Screens, modes, and command palette](references/screens-modes-command-palette.md)
- [Browser and delivery](references/browser-and-delivery.md)
- [Testing matrix](references/testing-matrix.md)
- [Anti-patterns](references/anti-patterns.md)
- [Packaging and CI](references/packaging-and-ci.md)
- [Repository map](references/repo-map.md)
- [Upstream pattern atlas](references/upstream-pattern-atlas.md)
