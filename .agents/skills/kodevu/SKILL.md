---
name: kodevu
description: A tool to fetch Git/SVN diffs, send them to an AI reviewer, and generate configurable code review reports.
---

# Kodevu Skill

Kodevu is a Node.js tool that fetches Git commits or SVN revisions, sends the diff to a supported AI reviewer CLI, and writes review results to report files. It supports an optional persistent config file at `~/.kodevu/config.json` for settings that should survive across sessions.

## Usage

Use `npx kodevu` to review a codebase.

### Reviewing the latest commit

```bash
npx kodevu .
```

### Reviewing a specific commit

```bash
npx kodevu . --rev <commit-hash>
```

### Reviewing the last N commits

```bash
npx kodevu . --last 3
```

### Reviewing uncommitted changes

```bash
npx kodevu . --uncommitted
```

### Supported Reviewers

`kodevu` supports several AI reviewer backends: `auto`, `openai`, `gemini`, `codex`, `copilot`. The default is `auto`, which probes available CLI tools in your `PATH`.

Example using OpenAI:
```bash
npx kodevu . --reviewer openai --openai-api-key <YOUR_API_KEY> --openai-model gpt-5-mini
```

### Generating JSON Reports

By default, review reports are generated as Markdown files in `~/.kodevu/`. You can specify `--format json` or change the output directory using `--output <dir>`.
```bash
npx kodevu . --format json --output ./reports
```

### Custom Prompts

You can provide additional instructions to the reviewer using `--prompt`:
```bash
npx kodevu . --prompt "Focus on security issues and suggest optimizations."
```
Or from a file: `--prompt @my-rules.txt`

### Environment Variables

All options can also be set via environment variables to avoid repetitive flags:

- `KODEVU_REVIEWER` – Default reviewer.
- `KODEVU_LANG` – Default output language.
- `KODEVU_OUTPUT_DIR` – Default output directory.
- `KODEVU_PROMPT` – Default prompt instructions.
- `KODEVU_OPENAI_API_KEY` – API key for `openai`.
- `KODEVU_OPENAI_BASE_URL` – Base URL for `openai`.
- `KODEVU_OPENAI_MODEL` – Model for `openai`.

### Configuration File

For persistent settings that survive across shells and AI tool invocations, create `~/.kodevu/config.json`:

```json
{
  "reviewer": "openai",
  "openaiApiKey": "sk-...",
  "openaiBaseUrl": "https://your-gateway.example.com/v1",
  "openaiModel": "gpt-4o",
  "lang": "zh"
}
```

The file is optional and silently ignored if absent. Priority: **CLI flags > ENV vars > config file > defaults**.

## Working with Target Repositories

- **Git**: `target` must be a local repository or subdirectory.
- **SVN**: `target` can be a working copy path or repository URL.

```bash
npx kodevu /path/to/project --last 1
```
