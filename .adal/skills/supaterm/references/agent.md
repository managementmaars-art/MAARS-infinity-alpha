# Agent Commands

`sp agent` manages Supaterm's coding-agent hook bridge.

## Install Hooks

Install Supaterm's managed hook bridge into an agent configuration:

```bash
sp agent install-hook claude
sp agent install-hook codex
```

Effects:

- `claude` installs Supaterm hooks into `~/.claude/settings.json`
- `codex` enables Codex hooks and installs Supaterm hooks into `~/.codex/hooks.json`

## Remove Hooks

Remove Supaterm-managed hooks from an agent configuration:

```bash
sp agent remove-hook claude
sp agent remove-hook codex
```

## Forward Hook Events

`sp agent receive-agent-hook --agent <agent>` reads one hook payload from stdin and forwards it to Supaterm.

```bash
printf '{"hook_event_name":"Notification","message":"Claude needs your attention"}' \
  | sp agent receive-agent-hook --agent claude
```

Use this when wiring an external agent hook system into Supaterm. This is lower-level than `install-hook` and `remove-hook`.

## Output

`receive-agent-hook` is a forwarding command. `install-hook` and `remove-hook` report failures through stderr and exit status.
