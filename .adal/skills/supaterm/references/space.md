# Space Commands

`sp space` creates, selects, renames, closes, and navigates spaces.

## Create

`sp space new <name>` creates a space. `--focus` switches to it immediately.

```bash
sp space new Work
sp space new --focus Build
```

## Focus

`sp space focus [space]` selects a space. Inside Supaterm, omitting the target uses the current space.

```bash
sp space focus
sp space focus 1
sp space focus <space-uuid>
```

## Rename

`sp space rename <name> [space]` renames a space.

```bash
sp space rename Work
sp space rename Logs 1
sp space rename Build <space-uuid>
```

## Close

`sp space close [space]` closes a space.

```bash
sp space close
sp space close 1
sp space close <space-uuid>
```

## Navigate

Use navigation commands to move through spaces:

```bash
sp space next
sp space prev
sp space last
```

## Output

Mutating `space` commands support the standard output flags:

```bash
sp space new --json --focus Work
sp space focus --plain 1
sp space close --quiet 1
```
