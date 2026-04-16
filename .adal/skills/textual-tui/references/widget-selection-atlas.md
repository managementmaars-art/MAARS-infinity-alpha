# Widget selection atlas

Prefer the built-in widget that already matches the interaction model.

## High-value widgets

### `DataTable`
Use for:
- searchable result sets
- keyboard navigation over rows
- dashboards with metrics or records
- master/detail layouts

Prefer over:
- manual Rich `Table` rendered into `Static`
- custom cursor logic for rows

Pair with:
- filter `Input`
- detail `Static` / `Markdown`
- responsive pane layout

### `DirectoryTree`
Use for:
- file browsers
- repository explorers
- import pickers
- project navigation

Pair with:
- preview pane
- `TextArea` or `MarkdownViewer`
- path/status footer

### `MarkdownViewer`
Use for:
- rendered notes, help, changelogs, docs, AI output
- long-form content needing browser-like navigation

Prefer over:
- hand-rendering markdown into many small widgets

### `TextArea`
Use for:
- text/code editing
- configuration editors
- scratch pads
- prompt builders

Pair with:
- save action
- status line
- optional preview or lint output

### `TabbedContent` / `TabPane`
Use for:
- grouped settings
- alternate detail views
- inspector panes

Prefer over:
- hand-written tab state unless the behaviour is highly custom

### `Log` / `RichLog`
Use for:
- streaming output
- task history
- captured stdout/stderr
- diagnostics

Prefer `Log` for simple text streams and `RichLog` when rich renderables matter.

### `Tree`
Use for:
- hierarchical data that is not the filesystem
- settings groups
- expandable summaries

### `SelectionList`, `OptionList`, `ListView`, `Select`
Quick guide:
- `SelectionList` for multi-select checklists
- `OptionList` for keyboard-first option menus
- `ListView` for custom row widgets
- `Select` for compact form dropdowns

### `Switch`, `Checkbox`, `Input`, `Button`, `Label`, `Static`
These cover most form and control needs. Reach for them before custom controls.

## Widget pairings that work well

- `DataTable` + detail `Static`
- `DirectoryTree` + `TextArea`
- `Input` + `DataTable` + status `Label`
- `MarkdownViewer` + `Footer`
- `TabbedContent` + per-tab forms
- `Log` + filter `Input`

## Signals you are missing a built-in

Stop and reconsider if you are about to:
- hand-roll tabs
- hand-roll file trees
- write your own editable multiline text widget
- render a Rich table into `Static` and then emulate selection
- manage long-form markdown as many individual `Static` widgets

## Styling advice

Make widget choice do most of the work. Use TCSS for:
- layout
- spacing
- responsive pane arrangement
- semantic states via classes

Do not create custom widgets only to solve a styling problem.
