---
name: supaterm
description: Control Supaterm spaces, tabs, panes, and coding-agent integrations with `sp`.
---

Use this skill when you need to control Supaterm from a terminal that is already running inside Supaterm.

## Terminology

- Space: the top-level container that contains multiple tabs, users might use this to separate work / life profile. 
- Tab: a terminal tab inside a space
- Pane: a split terminal region inside a tab

## Fast Start

Discover selectors and UUIDs:

```bash
sp ls --json
```

Creation commands use typed JSON keys instead of a generic `id`:

```bash
sp tab new --json -- git status
# => { "spaceID": "...", "tabID": "...", "paneID": "...", ... }

sp pane split --json right
# => { "spaceID": "...", "tabID": "...", "paneID": "...", ... }
```

Create and focus spaces:

```bash
sp space new Work
sp space new --focus Build
sp space focus 1
```

Create and focus tabs:

```bash
sp tab new --focus -- git status
sp tab focus 1/2
```

Trailing arguments after `--` are treated as a command and its arguments.

`--script` sends raw shell script text exactly as provided.

Split panes and send commands:

```bash
sp pane split down -- htop
sp pane split --layout keep right
sp pane send --newline 'echo hello'
```

Trailing arguments after `--` are treated as a command and its arguments.

`--script` sends raw shell script text exactly as provided.

## Deep-Dive References

- [Targeting and selectors](references/targeting-and-selectors.md)
- [Space commands](references/space.md)
- [Tab commands](references/tab.md)
- [Pane commands](references/pane.md)
- [Agent commands](references/agent.md)
