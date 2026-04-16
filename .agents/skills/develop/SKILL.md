---
name: develop
description: "Integrates GuaraCloud into local development workflows — project linking, remote shell access, port forwarding, log streaming, and environment management. Use when the user wants to connect their local environment to GuaraCloud, tail logs, exec into a container, or forward ports."
license: Apache-2.0
metadata:
  author: guaracloud
  version: "1.0"
---

# Local Development with GuaraCloud

## Project Linking

Link your working directory to a GuaraCloud project so commands automatically know which project/service to target:

```bash
guara link                                    # Interactive picker
guara link --project my-app --service api     # Direct link
```

This creates `.guara.json` in the current directory:

```json
{
  "project": "my-app",
  "service": "api"
}
```

The CLI walks upward from the current directory to find this file. Add `.guara.json` to `.gitignore` if it contains developer-specific choices.

Remove a link:

```bash
guara unlink
```

## Remote Shell (exec)

Open an interactive shell in a running service container:

```bash
guara exec                          # Default shell (/bin/sh)
guara exec --shell /bin/bash        # Use bash
```

Run a one-shot command:

```bash
guara exec -- ls -la /app
guara exec -- cat /etc/hostname
guara exec -- env                   # Check runtime env vars
guara exec -- node -e "console.log(process.env.DATABASE_URL)"
```

**JSON mode** buffers output and returns structured result:

```bash
guara exec --json -- whoami
# Returns: { "exitCode": 0, "output": "node\n", "command": ["whoami"] }
```

**Requirements:** Service must be running with at least one healthy pod. If you get "No ready pods available", start the service first: `guara services start`.

## Port Forwarding (proxy)

Forward a local port to the service's container port:

```bash
guara proxy                         # Random local port assigned
guara proxy --local-port 8080       # Forward localhost:8080 -> container
```

Use cases:
- Connect to a database running in the service
- Test API endpoints locally
- Debug with local tools

Press Ctrl+C to stop. Only one TCP connection at a time per proxy session.

## Log Streaming

View recent logs:

```bash
guara logs                          # Last 100 lines
guara logs --lines 500              # More lines
```

Stream in real time:

```bash
guara logs --follow                 # Polls every 2.5s
guara logs -f --level error         # Only errors, streaming
```

Filter logs:

```bash
guara logs --level error            # By level: trace|debug|info|warn|error|fatal
guara logs --since 1h               # Last hour (also: 30m, 2d, 90s)
guara logs --search "connection refused"  # Text search
guara logs --since 2h --level warn --search "timeout"  # Combined
```

Time range query:

```bash
guara logs --since 2026-04-01T00:00:00Z --until 2026-04-01T12:00:00Z
```

## Environment Management

List current env vars (values masked):

```bash
guara env list
guara env list --json               # Full values in JSON
```

Set variables:

```bash
guara env set KEY=value
guara env set KEY1=val1 KEY2=val2   # Multiple at once
guara env set NPM_TOKEN=xxx --build # Available during Docker build
```

Remove variables:

```bash
guara env unset KEY
guara env unset KEY1 KEY2
```

**Important:** `env set` and `env unset` trigger a rolling restart of the service. The new process picks up the updated environment.

## CLI Configuration

```bash
guara config list                   # Show api-url and api-key status
guara config get api-url            # Get specific value
guara config set api-url https://api.guaracloud.com
guara config reset                  # Reset to defaults
```

## Tips

- **Use `--json` for scripting.** All commands support `--json` for structured output and `--quiet` for minimal output (IDs only).
- **Use `--yes` to skip prompts** in CI/CD or scripted workflows.
- **Env var overrides are useful in CI:** `GUARA_API_KEY`, `GUARA_PROJECT`, `GUARA_SERVICE` let you skip `guara login` and `guara link`.
