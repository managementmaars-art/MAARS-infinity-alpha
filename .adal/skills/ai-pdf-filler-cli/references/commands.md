# Command Cheat Sheet

## Quick check

```bash
simplicity-cli --help
simplicity-cli help
```

If the command is missing, install first:

```bash
uv tool install ai-pdf-filler
# fallback
python3 -m pip install ai-pdf-filler
```

## Auth

Create an account and obtain an API key from `https://simplicity.ai`.

```bash
simplicity-cli login
```

```bash
printf '%s' "$SIMPLICITY_AI_API_KEY" | simplicity-cli login --api-key-stdin
```

Key precedence:

1. `--api-key`
2. `SIMPLICITY_AI_API_KEY`
3. saved key in `~/.config/simplicity-cli/config.json`

## New form workflow

```bash
simplicity-cli new --form-file ./form.pdf --context "applicant data"
```

```bash
simplicity-cli new --form-file ./form.pdf --source-file ./source.pdf
```

```bash
simplicity-cli new --form-url "https://example.com/form.pdf" --source-url "https://example.com/source.pdf"
```

Options:

- `--no-wait`
- `--poll-interval-seconds <n>`
- `--max-wait-seconds <n>`
- `--no-download`
- `--output <path>`

## Existing form workflow

```bash
simplicity-cli existing FORM_ID --context "first_name: John; last_name: Smoke; dob: 1990-07-07"
```

```bash
simplicity-cli existing FORM_ID --instructions "prefer exact legal names"
```

`--context` provides the field data to fill.
`--instructions` provides optional guidance for autofill behavior.

## Task workflow

```bash
simplicity-cli status TASK_ID
simplicity-cli wait TASK_ID
```

## JSON mode

```bash
simplicity-cli --json status TASK_ID
simplicity-cli --json new --form-file ./form.pdf --context "applicant data"
```
