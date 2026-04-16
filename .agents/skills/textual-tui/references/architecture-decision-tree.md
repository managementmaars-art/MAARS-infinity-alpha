# Architecture decision tree

Use this file when the user has described an app but not its internal shape.

## First cut

### Does the user mainly need one working surface?
Use a single `Screen` with containers and built-in widgets.

Best for:
- dashboards
- search tools
- editors
- settings panes
- monitors

Default structure:
- `App`
- one root screen or default screen
- composite widgets for repeated chunks
- external `.tcss`

### Does the user move between distinct contexts?
Use `Screen` classes.

Signals:
- drill-down views
- home -> detail -> edit
- separate flows with different headers/footers
- modal confirmation steps

Rule of thumb:
- if going “back” should restore the previous view, that usually wants a `Screen`

### Are there durable top-level areas with their own navigation stacks?
Use named `MODES`.

Signals:
- dashboard / jobs / settings / logs
- inbox / projects / account
- an app-level sidebar or command palette that jumps between sections

Rule of thumb:
- use modes for **persistent product areas**
- use screens for **within-area navigation**

### Is the flow linear and local to one screen?
Use `ContentSwitcher` or a small state machine.

Best for:
- multi-step forms
- onboarding
- short wizards
- alternate detail panes

### Is the interruption brief and task-specific?
Use `ModalScreen`.

Best for:
- confirmation dialogs
- pickers
- destructive actions
- tiny forms

## Layout choices

### Data-heavy tools
Prefer:
- `DataTable`
- filter/search input
- details pane
- breakpoint-driven collapse on narrow terminals

Avoid:
- rendering static Rich tables inside `Static` when the table needs focus or cursoring

### Filesystem/document tools
Prefer:
- `DirectoryTree`
- preview/detail pane
- `MarkdownViewer` or `TextArea`
- delivery APIs for export/download

### Chat and live task tools
Prefer:
- transcript/log widget
- input dock
- worker-driven background tasks
- anchored scrolling
- clear status/notification path

## Extraction rules

Split code when any of these happen:
- `App` grows beyond a few hundred lines
- the same query selectors appear everywhere
- a screen has its own state and actions
- widget event handling dominates the app class
- styling is hard to reason about without opening Python

Good extraction targets:
- `Screen` for route-level behaviour
- composite `Widget` for reusable panes
- helper module for domain logic
- `.tcss` for all layout and theme work

## Stable defaults

When unsure:
1. start with one screen
2. compose built-in widgets
3. externalise styling
4. add IDs/classes deliberately
5. move long-running work into workers
6. add at least one Pilot test before expanding scope
