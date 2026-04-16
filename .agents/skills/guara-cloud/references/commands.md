# CLI Command Reference

## Authentication

### guara login
Authenticate with GuaraCloud.
```
guara login                        # Browser OAuth (opens browser)
guara login --api-key <key>        # Direct API key
guara login --browser              # Force browser login
```

### guara logout
Clear stored credentials.
```
guara logout
```

### guara whoami
Show authenticated user (email, role, tier).
```
guara whoami
guara whoami --json
```

## Projects

### guara projects list
```
guara projects list
guara projects list --json
```

### guara projects create
```
guara projects create --name my-app
guara projects create --name my-app --json
```

### guara projects info
```
guara projects info --project my-app
guara projects info --json
```

## Services

### guara services list
```
guara services list --project my-app
guara services list --json
```

### guara services create
Create a new service (does NOT trigger a build).
```
guara services create --name api --build-method dockerfile --port 3000
guara services create --name api --build-method buildpack --repo https://github.com/user/repo --port 8080
guara services create --name web --build-method buildpack --repo https://github.com/user/monorepo --root-dir ./apps/web --build-cmd "pnpm --filter web build" --start-cmd "pnpm --filter web start" --port 3000
guara services create  # Interactive prompts
```

**Flags:**
| Flag | Description |
|---|---|
| `--name`, `-n` | Service name |
| `--build-method`, `-b` | `dockerfile` or `buildpack` |
| `--repo` | GitHub repository URL |
| `--branch` | Git branch (default: main) |
| `--port` | Container port |
| `--root-dir` | Root directory for build (default: .) |
| `--dockerfile-path` | Custom Dockerfile path (default: Dockerfile) |
| `--build-cmd` | Custom build command (buildpack monorepos) |
| `--start-cmd` | Custom start command (buildpack monorepos) |
| `--public` | Make publicly accessible |
| `--no-auto-deploy` | Disable auto-deploy on push |

### guara services info
```
guara services info --project my-app --service api
guara services info --json
```

### guara services start / stop / restart
```
guara services start
guara services stop
guara services restart
```

### guara services delete
```
guara services delete --project my-app --service old-api --yes
```

## Deployments

### guara deploy
Trigger a new deployment. Polls until terminal status (healthy, failed, rolled_back).
```
guara deploy
guara deploy --branch develop
guara deploy --commit abc123f
guara deploy --json    # Polls then outputs final state
guara deploy --quiet   # Outputs deployment ID immediately
```

### guara rollback
Rollback to a previous healthy deployment.
```
guara rollback                     # Interactive picker
guara rollback --deployment <id>   # Direct rollback
```

### guara deployments list
```
guara deployments list
guara deployments list --json
```

## Domains

### guara domains list
```
guara domains list
guara domains list --json
```

### guara domains add
```
guara domains add --domain api.myapp.com
```
Returns the CNAME target. User must add a CNAME record at their DNS provider.

### guara domains remove
```
guara domains remove --domain api.myapp.com --yes
```

## Scaling

### guara scale
Enable or disable autoscaling.
```
guara scale --autoscaling on
guara scale --autoscaling off
```

## Environment Variables

### guara env list
```
guara env list
guara env list --json
```
Values are masked by default.

### guara env set
Set one or more env vars. Triggers a rolling restart if the service is running.
```
guara env set KEY=value
guara env set KEY1=value1 KEY2=value2
guara env set DATABASE_URL=postgres://... --build   # Available at build time
```

### guara env unset
```
guara env unset KEY
guara env unset KEY1 KEY2
```

## Local Development

### guara link
Link current directory to a project/service. Creates `.guara.json`.
```
guara link                          # Interactive picker
guara link --project my-app --service api
```

### guara unlink
Remove `.guara.json` from current directory.
```
guara unlink
```

### guara exec
Execute command or start interactive shell in a running container.
```
guara exec                          # Interactive shell (/bin/sh)
guara exec --shell /bin/bash        # Use bash
guara exec -- ls -la /app           # One-shot command
guara exec -- cat /etc/hostname     # One-shot command
```

### guara proxy
Forward a local port to the service's container port.
```
guara proxy                         # Random local port
guara proxy --local-port 8080       # Specific local port
```
Press Ctrl+C to stop.

### guara logs
View or stream service logs.
```
guara logs                          # Last 100 lines
guara logs --follow                 # Stream in real time
guara logs --lines 500              # More lines
guara logs --level error            # Filter by level
guara logs --since 1h               # Last hour
guara logs --since 30m --search "connection refused"
guara logs --json                   # JSON output
```

**Flags:**
| Flag | Short | Description |
|---|---|---|
| `--follow` | `-f` | Stream in real time (polls every 2.5s) |
| `--lines` | `-n` | Number of lines (default: 100) |
| `--since` | | Start time: relative (`1h`, `30m`, `2d`, `90s`) or ISO8601 |
| `--until` | | End time (ISO8601) |
| `--search` | | Filter by text |
| `--level` | | Filter: `trace`, `debug`, `info`, `warn`, `error`, `fatal` |

## Utility

### guara open
Open service URL in browser.
```
guara open
```

### guara status
Check platform status.
```
guara status
guara status --json
```

### guara config list / get / set / reset
Manage CLI configuration (api-url, api-key status).
```
guara config list
guara config get api-url
guara config set api-url https://api.guaracloud.com
guara config reset
```
