# Kodevu

> The name **Kodevu** is a phonetic play on "code review".

A Node.js tool that fetches Git commits or SVN revisions, sends the diff to a supported AI reviewer CLI, and writes review results to report files.

## Pure & Zero Config

Kodevu is designed to be stateless and requires no mandatory configuration. All settings work out-of-the-box via command-line arguments and environment variables, with an optional persistent config file for convenience.

1. **Automatic Detection**: Detects repository type (Git/SVN), language, and available reviewers.
2. **Stateless**: Does not track history; reviews exactly what you ask for.
3. **Flexible**: Every setting can be set via config file, ENV var, or CLI flag, with CLI taking highest priority.

## Quick Start

Get a review of your latest commit in seconds:

```bash
npx kodevu .
```

Review reports are saved to `~/.kodevu/` by default.
Console output is intentionally concise by default; detailed execution logs are written to `~/.kodevu/logs/`.

## Install as an AI Agent Skill

Kodevu includes a natively supported `SKILL.md` file, which allows it to be installed as a specialized skill in AI agent coding assistants.

To install:

```bash
npx skills add gyteng/kodevu
```

## Usage

```bash
npx kodevu [target] [options]
```

### Options

- `target`: Repository path (Git) or SVN URL/Working copy (default: `.`).
- `--reviewer, -r`: `codex`, `gemini`, `copilot`, `openai`, `opencode` or `auto` (default: `auto`).
- `--rev, -v`: A specific revision or commit hash to review.
- `--last, -n`: Number of latest revisions to review (default: 1). Use negative values (e.g., `-3`) to review only the 3rd commit from the top.
- `--uncommitted, -u`: Review current uncommitted changes in the target working tree.
- `--lang, -l`: Output language (e.g., `zh`, `en`, `auto`).
- `--prompt, -p`: Additional instructions for the reviewer. Use `@file.txt` to read from a file.
- `--output, -o`: Report output directory (default: `~/.kodevu`).
- `--format, -f`: Output formats (e.g., `markdown`, `json`, or `markdown,json`).
- `--openai-api-key`: API key used when `--reviewer openai`.
- `--openai-base-url`: Base URL used when `--reviewer openai` (default: `https://api.openai.com/v1`).
- `--openai-model`: Model used when `--reviewer openai` (default: `gpt-5-mini`).
- `--openai-org`: Optional OpenAI organization ID.
- `--openai-project`: Optional OpenAI project ID.
- `--debug, -d`: Show extra debug information on the console.
- `--version, -V`: Print the current version and exit.

> [!IMPORTANT]
> `--rev` and `--last` are mutually exclusive. Specifying both will result in an error.

> [!IMPORTANT]
> `--uncommitted` is mutually exclusive with `--rev` and `--last`.

### Environment Variables

You can set these in your shell to change default behavior without typing flags every time:

- `KODEVU_REVIEWER`: Default reviewer.
- `KODEVU_LANG`: Default language.
- `KODEVU_OUTPUT_DIR`: Default output directory.
- `KODEVU_PROMPT`: Default prompt instructions.
- `KODEVU_TIMEOUT`: Reviewer execution timeout in milliseconds.
- `KODEVU_OPENAI_API_KEY`: API key for `openai`.
- `KODEVU_OPENAI_BASE_URL`: Base URL for `openai`.
- `KODEVU_OPENAI_MODEL`: Model for `openai`.
- `KODEVU_OPENAI_ORG`: Optional organization ID for `openai`.
- `KODEVU_OPENAI_PROJECT`: Optional project ID for `openai`.

### Configuration File

For persistent settings that survive across shells and AI tools, create `~/.kodevu/config.json`:

```json
{
  "reviewer": "openai",
  "openaiApiKey": "sk-...",
  "openaiBaseUrl": "https://your-gateway.example.com/v1",
  "openaiModel": "gpt-4o",
  "lang": "zh"
}
```

The file is optional and silently ignored if absent. **Priority order** (highest wins):

```
CLI flags  >  Environment variables  >  Config file  >  Built-in defaults
```

Supported keys: `reviewer`, `lang`, `outputDir`, `prompt`, `commandTimeoutMs`, `outputFormats`, `openaiApiKey`, `openaiBaseUrl`, `openaiModel`, `openaiOrganization`, `openaiProject`.

## Examples

### Selecting Revisions

Review the **latest 3** commits:
```bash
npx kodevu . --last 3
```

Review **only the 3rd** latest commit:
```bash
npx kodevu . --last -3
```

Review a **specific commit** hash:
```bash
npx kodevu . --rev abc1234
```

Review **current uncommitted changes** (Git/SVN working copy):
```bash
npx kodevu . --uncommitted
```

### Options & Formatting

Review using **custom instructions** from a file:
```bash
npx kodevu . --prompt @my-rules.txt
```

Generate **JSON reports** in a local folder:
```bash
npx kodevu . --format json --output ./reports
```

### Environment Variables

Set a **persistent reviewer** for your shell session:
```bash
export KODEVU_REVIEWER=gemini
npx kodevu .
```

Use the OpenAI API directly with a small set of extra settings:
```bash
export KODEVU_REVIEWER=openai
export KODEVU_OPENAI_API_KEY=sk-...
export KODEVU_OPENAI_MODEL=gpt-5-mini
npx kodevu .
```

Use a custom OpenAI-compatible endpoint:
```bash
npx kodevu . \
  --reviewer openai \
  --openai-api-key sk-... \
  --openai-base-url https://your-gateway.example.com/v1 \
  --openai-model gpt-5-mini
```


## License

MIT
