# Pane Commands

`sp pane` splits, focuses, closes, resizes, captures, notifies, and sends text to panes.

## Split

`sp pane split <direction>` creates a new pane beside the current pane when run inside Supaterm. Use `--in` to target a tab or pane explicitly. Trailing arguments after `--` are treated as a command and its arguments. `--script` sends raw shell script text exactly as provided.

```bash
sp pane split right
sp pane split down -- htop
sp pane split down --script 'echo hi; pwd'
sp pane split --layout keep right
sp pane split --in 1/2 left
sp pane split --in <tab-uuid> left
sp pane split --in 1/2/3 down -- tail -f /tmp/server.log
```

Flags:

- `--layout keep` preserves the existing pane sizing
- `--cwd <path>` sets the starting working directory
- `--script <script>` sends raw shell script text exactly as provided
- `--in <tab-or-pane>` targets a tab selector, pane selector, or UUID

## Focus And Close

```bash
sp pane focus
sp pane focus 1/2/3
sp pane focus <pane-uuid>

sp pane close
sp pane close 1/2/3
sp pane close <pane-uuid>
```

## Send Text

`sp pane send` sends literal text. It accepts an optional pane target first, or stdin.

```bash
sp pane send --newline 'echo hello'
sp pane send 1/2/3 'pwd'
sp pane send <pane-uuid> 'clear'
printf 'pwd' | sp pane send
```

## Capture

`sp pane capture` captures visible output or scrollback.

```bash
sp pane capture
sp pane capture --scope scrollback --lines 200
sp pane capture --json <pane-uuid>
```

## Resize

`sp pane resize <direction> <amount> [pane]` resizes a pane by cell count.

```bash
sp pane resize right 10
sp pane resize down 5 1/2/3
sp pane resize left 8 <pane-uuid>
```

## Layout

`sp pane layout <mode> [tab]` applies a layout to a tab.

Supported modes:

- `equalize`
- `tile`
- `main-vertical`

Examples:

```bash
sp pane layout equalize
sp pane layout tile 1/2
sp pane layout main-vertical <tab-uuid>
```

## Notify

`sp pane notify` sends a Supaterm notification for a pane.

```bash
sp pane notify --body "All tests passed"
sp pane notify 1/2/3 --body "Deploy complete"
sp pane notify <pane-uuid> --body "Deploy complete"
```

## Output

Mutating `pane` commands support the standard output flags:

```bash
sp pane split --json right
sp pane focus --plain 1/2/3
sp pane close --quiet 1/2/3
```
