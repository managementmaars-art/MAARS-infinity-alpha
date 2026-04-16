---
name: guara-deploy
description: "Deploys and manages services on GuaraCloud — creating projects and services, triggering deployments, rollbacks, scaling, custom domains, and environment variables. Use when the user wants to deploy an app, manage services, configure domains, set env vars, or scale."
license: Apache-2.0
metadata:
  author: guaracloud
  version: "1.0"
---

# Deploying on GuaraCloud

## Build Methods

| Method | When to use | What happens |
|---|---|---|
| `dockerfile` | Project has a Dockerfile | Builds using the Dockerfile in the repo |
| `buildpack` | No Dockerfile, or prefer auto-detection | Heroku-style buildpacks detect language and build automatically |

For monorepos, use `--root-dir`, `--build-cmd`, and `--start-cmd` to specify the subdirectory and custom commands.

## Create a Project

```bash
guara projects create --name my-app
```

## Create a Service

```bash
# With Dockerfile
guara services create --name api --build-method dockerfile --repo https://github.com/user/repo --port 3000

# With buildpack
guara services create --name api --build-method buildpack --repo https://github.com/user/repo --port 8080

# Monorepo (buildpack)
guara services create --name web --build-method buildpack \
  --repo https://github.com/user/monorepo \
  --root-dir ./apps/web \
  --build-cmd "pnpm --filter web build" \
  --start-cmd "pnpm --filter web start" \
  --port 3000

# Interactive (no flags)
guara services create
```

Creating a service does NOT trigger a build. Deploy separately after creation.

**Requires:** GitHub App installed. If not installed, the CLI will prompt with a link.

## Deploy

```bash
guara deploy                    # Deploy default branch
guara deploy --branch develop   # Deploy specific branch
guara deploy --commit abc123f   # Deploy specific commit
```

The CLI polls deployment status and shows a spinner. Terminal statuses:
- **healthy** — deployment succeeded, service is live
- **failed** — build or deploy error occurred
- **rolled_back** — deployment was replaced by a rollback
- **superseded** — a newer deployment replaced this one

## Rollback

```bash
guara rollback                     # Interactive: pick from healthy deployments
guara rollback --deployment <id>   # Direct rollback to specific deployment
```

Only deployments with status `healthy` and a valid image are available for rollback.

## Service Lifecycle

```bash
guara services stop      # Scale to zero replicas
guara services start     # Restore to configured replicas
guara services restart   # Rolling restart (zero downtime)
guara services delete    # Permanent deletion
```

## Autoscaling

```bash
guara scale --autoscaling on    # Enable autoscaling
guara scale --autoscaling off   # Disable, use fixed replicas
```

## Custom Domains

```bash
# Add domain
guara domains add --domain api.myapp.com

# The CLI returns a CNAME target. User must add this DNS record:
#   api.myapp.com CNAME <cname-target>

# Verify status
guara domains list

# Remove
guara domains remove --domain api.myapp.com
```

Domain status progresses: `pending` → `active` once DNS propagates and verification succeeds.

## Environment Variables

```bash
guara env set DATABASE_URL=postgres://...
guara env set KEY1=val1 KEY2=val2
guara env list
guara env unset KEY
```

**Important:** Setting or unsetting env vars triggers a rolling restart of the service.

To make a variable available during Docker builds (as a build arg):
```bash
guara env set NPM_TOKEN=xxx --build
```

## Deployment Status Check

After deploying, verify the service is healthy:
```bash
guara services info
```

Check deployment history:
```bash
guara deployments list
```

For step-by-step deployment scenarios, see [references/workflows.md](references/workflows.md).

For tier limits and pricing, see [guaracloud.com/docs](https://guaracloud.com/docs).
