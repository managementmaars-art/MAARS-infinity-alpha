# Configuration

Set `SERPER_API_KEY` before running the search script.

Get an API key from `https://serper.dev`.

## Check whether it is already set

```bash
printenv SERPER_API_KEY
```

If the command prints nothing, configure it.

## Set it for the current shell

```bash
export SERPER_API_KEY="your_api_key"
```

## Persist it in a shell profile

Zsh:

```bash
echo 'export SERPER_API_KEY="your_api_key"' >> ~/.zshrc
source ~/.zshrc
```

Bash:

```bash
echo 'export SERPER_API_KEY="your_api_key"' >> ~/.bashrc
source ~/.bashrc
```

Fish:

```fish
set -Ux SERPER_API_KEY "your_api_key"
```

## Verify the configuration

Run:

```bash
python3 scripts/serper_search.py "OpenAI"
```

If configuration is missing, the script returns:

```json
{"error": "SERPER_API_KEY environment variable not set"}
```
