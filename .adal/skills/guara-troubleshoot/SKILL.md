---
name: guara-troubleshoot
description: "Diagnoses and resolves issues on GuaraCloud — failed deployments, crash loops, health check failures, image pull errors, OOM kills, and CLI errors. Use when the user reports something broken, a deployment failed, a service is unhealthy, or they see an error."
license: Apache-2.0
metadata:
  author: guaracloud
  version: "1.0"
---

# Troubleshooting GuaraCloud

## First Things to Check

When something is wrong, start here:

```bash
# 1. Is the service running?
guara services info

# 2. What do the logs say?
guara logs --level error --since 1h

# 3. What's the deployment history?
guara deployments list

# 4. Is the platform itself healthy?
guara status
```

## Health Statuses

`guara services info` reports these health statuses:

| Status | Meaning | Action |
|---|---|---|
| `healthy` | All replicas running and passing health checks | No action needed |
| `crash_loop` | Container repeatedly crashing and restarting | Check logs: `guara logs --level error` |
| `image_pull_error` | Cannot pull the container image | Check deployment logs, verify build succeeded |
| `oom_killed` | Container exceeded memory limit | Reduce memory usage or upgrade tier — see [guaracloud.com/docs](https://guaracloud.com/docs) |
| `degraded` | Some but not all replicas healthy | Check logs, may resolve on its own during rolling updates |
| `unknown` | Status cannot be determined | Wait a moment, then check again |

## Deployment Failure Decision Tree

**Deployment status is `failed`:**

1. Check deployment logs: `guara logs --since 10m --level error`
2. If **build error** → fix code/Dockerfile and redeploy: `guara deploy`
3. If **image pull error** → previous build may have failed silently. Check `guara deployments list` for the last healthy deployment, then `guara rollback`
4. If **crash on startup** → app fails to start. Check logs for stack traces, missing env vars, or port mismatches

**Container keeps restarting (crash_loop):**

1. Check logs: `guara logs --level error --since 30m`
2. Common causes:
   - Missing environment variables → `guara env list` to check, `guara env set` to fix
   - Wrong port → service listens on a different port than configured. Check with `guara services info`
   - Missing dependencies → Dockerfile or buildpack not installing all deps
   - OOM → app needs more memory than tier allows
3. If you can't determine the cause from logs, exec into the container: `guara exec -- env` to check runtime environment

**Service stuck in `deploying`:**

1. Wait — deployments can take up to 10 minutes
2. If still stuck, check `guara deployments list` for the status
3. The new deployment may be waiting for health checks to pass

## Tier Limit Errors

The CLI surfaces these when a tier limit is reached:

- **"Resource exceeds your tier quota"** → service needs more CPU/memory than tier allows
- **"Maximum number of projects reached"** → delete an unused project or upgrade
- **"Maximum number of services reached"** → delete an unused service or upgrade
- **"Build minutes quota exceeded"** → wait for next billing cycle or upgrade
- **"Maximum number of custom domains reached"** → remove an existing domain or upgrade
- **"Account resource pool exhausted"** → scale down other services or upgrade

For all tier limits, direct the user to [guaracloud.com/docs](https://guaracloud.com/docs) to see current tier details and upgrade options.

## Authentication Errors

- **"Authentication failed. API key is invalid or revoked"** → `guara login` to re-authenticate
- **"Authentication failed. API key has expired"** → `guara login` to generate a new key
- **"Not authenticated"** → `guara login`
- **"Account is suspended due to billing issues"** → update payment at [app.guaracloud.com](https://app.guaracloud.com)
- **"Terms of Service must be accepted"** → accept at [app.guaracloud.com](https://app.guaracloud.com)

## Network and Session Errors

- **"Could not reach GuaraCloud API"** → check internet connection and API URL: `guara config get api-url`
- **"No ready pods available"** → service is not running. Start it: `guara services start`
- **"Session disconnected due to inactivity"** → reconnect by running the command again
- **"Maximum concurrent sessions reached"** → close existing exec/proxy sessions first

## Common Pitfalls

1. **Forgot to deploy after creating a service** — `services create` does NOT trigger a build. Run `guara deploy` after.
2. **Port mismatch** — the `--port` in `services create` must match what the app listens on.
3. **Missing GitHub App** — install at [github.com/apps/guaracloud](https://github.com/apps/guaracloud) if you see "No GitHub App installation found."
4. **Env var change didn't take effect** — `guara env set` triggers a rolling restart, but check logs to confirm the new process picked up the change.
5. **DNS not propagated for custom domain** — `guara domains list` shows `pending` until CNAME propagates. This can take minutes to hours.

For the full error code reference, see [references/error-codes.md](references/error-codes.md).
