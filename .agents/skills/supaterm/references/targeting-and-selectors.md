# Targeting And Selectors

Use `sp ls --json` to discover the current Supaterm tree, including selectors and UUIDs.

```bash
sp ls
sp ls --json
sp ls --plain
```

## Ambient Targeting

When a command runs inside Supaterm, many commands can omit their target:

- `sp space focus` uses the current space
- `sp tab focus` uses the current tab
- `sp pane focus` uses the current pane
- `sp tab new` creates a tab in the current space
- `sp pane split` splits the current pane

That ambient context comes from:

- `SUPATERM_SOCKET_PATH`
- `SUPATERM_SURFACE_ID`
- `SUPATERM_TAB_ID`

## Selector Forms

- Space selector: `1`
- Tab selector: `1/2`
- Pane selector: `1/2/3`

You can also pass UUIDs anywhere the CLI accepts a space, tab, or pane target.

## Creation JSON

`sp ls --json` returns the full tree with generic object `id` fields inside each space, tab, and pane entry.

Creation commands return typed IDs instead:

```bash
sp tab new --json -- git status
```

```json
{
  "spaceID": "BBBDD2AB-3F53-4BCA-B120-CE4A5E8C7F18",
  "tabID": "3734DE02-672F-4914-95DE-35D093CE1B3A",
  "paneID": "5E6E9773-222B-468A-AA65-11341F2926FF",
  "spaceIndex": 2,
  "tabIndex": 1,
  "paneIndex": 1
}
```

Use `tabID` or `paneID` from creation output when chaining follow-up commands like `sp pane split --in <tabID>` or `sp pane send <paneID> ...`.

## `--in`

Targeted creation commands use `--in`:

- `sp tab new --in <space>`
- `sp pane split --in <tab>`
- `sp pane split --in <pane>`

Trailing arguments after `--` on `sp tab new` and `sp pane split` are treated as a command and its arguments.

`--script` sends raw shell script text exactly as provided.

Examples:

```bash
sp tab new --in 1 --cwd ~/tmp -- git status
sp tab new --in <space-uuid> --focus -- ping 1.1.1.1
sp pane split --in 1/2 left
sp pane split --in 1/2/3 down -- tail -f /tmp/server.log
sp pane split --in <tab-uuid> right
sp pane split --in <pane-uuid> up
```

## Target Rules By Family

- `space` commands accept a space selector or UUID
- `tab focus`, `tab close`, and `tab rename` accept a tab selector or UUID
- `tab next`, `tab prev`, and `tab last` accept an optional space selector or UUID
- `pane focus`, `pane close`, `pane capture`, `pane resize`, and `pane notify` accept a pane selector or UUID
- `pane split` accepts a tab selector, pane selector, or UUID through `--in`
- `pane layout` accepts an optional tab selector or UUID
- `pane send` accepts an optional pane selector or UUID as its first argument

## Outside Supaterm

Outside Supaterm, omit ambient assumptions and pass an explicit target:

```bash
sp tab new --in 1 -- git status
sp pane split --in 1/2 right
sp tab focus 1/2
sp pane focus 1/2/3
```
