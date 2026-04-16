---
name: mem
description: Store and retrieve memories (notes, facts, decisions, snippets, images) using a local SQLite database with full-text search. Use when you need to remember information across sessions, recall previous decisions, store code snippets, or search your knowledge base.
---

# mem — Agent Memory Store

A CLI tool for storing and retrieving memories with full-text search. Data is stored locally in `~/.mem/mem.db`.

## When to Use

- **Remember** user preferences, project decisions, important facts
- **Store** code snippets, commands, configurations for later recall
- **Search** your knowledge base before asking the user for information you may have stored
- **Attach** images (screenshots, diagrams) to memories

## Commands

Three operators: (none) = recall, `+` = remember, `-` = forget.

### Recall (search, list, get)

```bash
mem                             # list recent memories
mem "deploy"                    # full-text search
mem "database" --tag db         # search filtered by tag
mem 7sjtNVyZrNIa                # get full content by ID
mem --tag prefs                 # list filtered by tag
mem "api" --limit 5 --json     # limit results, JSON output
mem --full                      # show full content for all
```

### Remember

```bash
mem + "user prefers dark mode" --tag prefs
mem + "deploy: bun build --compile" --tag deploy
mem + "chose SQLite for simplicity" --tag architecture
mem + --image ./screenshot.png --title "Current UI" --tag ui
echo "long content" | mem + --tag notes
```

### Forget

```bash
mem - <id>                      # delete one memory
mem - id1 id2 id3               # delete multiple
```

## Piping

```bash
mem "old" --json | jq -r '.[].id' | xargs -I{} mem - {}
echo "long content" | mem + --tag notes
```

## Best Practices

1. **Tag consistently** — Use lowercase, descriptive tags like `prefs`, `api`, `deploy`, `db`
2. **Search before asking** — Check if you've stored relevant information before asking the user
3. **Store decisions** — When making architectural or design decisions, store the reasoning
4. **Keep memories atomic** — One concept per memory for better searchability

## Output Formats

- Default: One-line summary per result
- `--full`: Complete content inline
- `--json`: Structured JSON for parsing
