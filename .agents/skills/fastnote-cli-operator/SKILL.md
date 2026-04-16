---
name: fastnote-cli-operator
description: Operate the FastNote local notebook through natural language by mapping requests to note CRUD, search, pin, and tag commands. Use this whenever the user wants to create, list, inspect, update, pin, unpin, delete, or review FastNote notes or tags, even if they never mention the CLI. Execute the bundled zero-dependency script directly instead of relying on the project package runtime.
---

# FastNote CLI Operator

Use this skill to turn natural-language FastNote requests into direct local note operations.

## What this skill does

- Executes FastNote note operations without importing the FastNote app
- Uses the bundled script at `scripts/fastnote_cli.py`
- Reads and writes the same SQLite database schema as the project CLI
- Returns a short human summary first, then the raw JSON payload

## Command coverage

Map user intent onto one of these commands:

- `list`
- `get <id>`
- `create`
- `update <id>`
- `delete <id>`
- `pin <id> --value true|false`
- `tags`

`list` returns note summaries to keep agent context small.
`get` returns the full note, including `content`.
For long or multi-line note bodies, prefer `--content-file` or `--content-stdin` over `--content`.

## Safety and decision rules

- Treat `update` as full replacement.
- If the user asks to update a note but omits title, content, or pinned state, ask for the missing fields instead of guessing.
- Only execute `delete` immediately when the user is explicit that no confirmation is needed, such as "delete note 12 now" or "remove 12, no need to confirm".
- If the delete intent is not explicit enough, ask for confirmation before running it.
- Preserve the CLI's strict boolean style: use `true` and `false`.
- If the note body is long, contains multiple paragraphs, or includes Chinese long-form text, use `--content-file` or `--content-stdin` to avoid shell length, quoting, and newline issues.

## Execution

Run the bundled script with Python from any shell:

```bash
python skills/fastnote-cli-operator/scripts/fastnote_cli.py <command> ...
```

If needed, pass an explicit database path:

```bash
python skills/fastnote-cli-operator/scripts/fastnote_cli.py --db /absolute/path/to/fastnote.sqlite3 <command> ...
```

If `--db` is omitted, the script resolves the default FastNote database path by platform:

- Windows: `%LOCALAPPDATA%\FastNote\fastnote.sqlite3`
- macOS: `~/Library/Application Support/FastNote/fastnote.sqlite3`
- Linux: `~/.local/share/FastNote/fastnote.sqlite3`

The script itself is cross-platform. Avoid shell-specific wrappers unless the user explicitly asks for one.

## Response format

Always reply in two parts:

1. A concise natural-language summary of what happened
2. The raw JSON returned by the script

Examples:

- Create success: "Created note 14 titled `Inbox` with tags `work`, `urgent`."
- List success: "Found 3 notes, including 2 pinned notes."
- Delete success: "Deleted note 9."
- Not found: "Note 9 does not exist."

Then include the JSON payload in a fenced `json` block.

For context efficiency:

- `list` returns `id`, `title`, `preview`, `is_pinned`, `created_at`, `updated_at`, and `tags`
- `get` returns the full note object, including `content`

## First-use transparency

On every run, the script includes a `meta` object with:

- `db_path`: the exact SQLite file path in use
- `db_initialized`: whether this run created the database file for first use
- `data_dir_created`: whether this run created the parent data directory
- `backup_reminder`: a reminder to back up the database file regularly

When `db_initialized` is `true`, tell the user plainly that:

- the skill created a local FastNote SQLite database for them
- where the database file is located
- that the data stays local on this machine
- they should back up the SQLite file periodically

Keep this explanation short but explicit. The point is transparency and trust, not verbosity.

Use this template on first use, adapting only the path:

```text
This is the first time this FastNote skill has been used on this machine, so it created a local SQLite database for your notes.
Database path: <db_path>
Your data stays on this machine. Back up this SQLite file periodically if you want to avoid accidental data loss.
```

On later runs, if it helps the task, you can use this shorter template:

```text
FastNote database in use: <db_path>
Remember to back up this SQLite file periodically.
```

## Common mappings

**Example 1**
User: "Create a pinned note titled sprint plan with content finalize API scope and tags work, planning"
Action:

```bash
python skills/fastnote-cli-operator/scripts/fastnote_cli.py create --title "sprint plan" --content "finalize API scope" --tag work --tag planning --pinned true
```

**Example 1b**
User: "Create a note from this long draft"
Action:

```bash
python skills/fastnote-cli-operator/scripts/fastnote_cli.py create --title "draft" --content-file /absolute/path/to/draft.txt --pinned false
```

**Example 2**
User: "Show pinned notes tagged work"
Action:

```bash
python skills/fastnote-cli-operator/scripts/fastnote_cli.py list --tag work --pinned true
```

**Example 3**
User: "Set note 7 to unpinned"
Action:

```bash
python skills/fastnote-cli-operator/scripts/fastnote_cli.py pin 7 --value false
```

**Example 4**
User: "Update note 5 title to Draft v2 and content to Updated body, keep it unpinned, tags todo and urgent"
Action:

```bash
python skills/fastnote-cli-operator/scripts/fastnote_cli.py update 5 --title "Draft v2" --content "Updated body" --tag todo --tag urgent --pinned false
```

When the content comes from stdin:

```bash
python skills/fastnote-cli-operator/scripts/fastnote_cli.py update 5 --title "Draft v2" --content-stdin --tag todo --pinned false
```

## Implementation notes

- The script intentionally has zero third-party dependencies.
- It mirrors the current FastNote CLI JSON envelopes and exit codes.
- It depends on the repository's SQLite schema staying compatible.
