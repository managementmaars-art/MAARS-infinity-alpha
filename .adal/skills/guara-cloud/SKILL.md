---
name: guara-cloud
description: "Provides foundational knowledge about GuaraCloud PaaS platform — projects, services, deployments, tiers, build methods, and CLI installation and authentication. Use when the user mentions GuaraCloud, asks about platform concepts, or needs to set up the CLI."
license: Apache-2.0
metadata:
  author: guaracloud
  version: "1.0"
---

# GuaraCloud Platform

GuaraCloud is a Platform-as-a-Service that deploys containerized applications from GitHub repositories. Billing is in BRL (Brazilian Real).

## Core Concepts

**User** — Authenticated via GitHub or Google OAuth. Has one subscription tier (hobby, pro, business, enterprise) that governs limits across all projects.

**Project** — Organizational unit containing one or more services. Each project is isolated.

**Service** — A deployable container within a project. Has its own subdomain, env vars, scaling config, and deployment history. Subdomain format: `{service}-{project}.guaracloud.com`.

**Deployment** — A build-and-deploy cycle triggered by git push, manual trigger, rollback, or config change. Tracks build status, image tag, commit SHA, and errors.

**Domain** — Each service gets an automatic subdomain. Users can add custom domains via CNAME verification.

**Project Members** — Role-based access: `owner`, `admin`, `member`, `viewer`.

## CLI Installation

```bash
npm install -g @guaracloud/cli
```

Binary names: `guara` or `guaracloud` (interchangeable).

Requires Node.js >= 20.

## Authentication

```bash
# Browser-based OAuth (interactive)
guara login

# Direct API key (non-interactive / CI)
guara login --api-key <key>

# Verify
guara whoami
```

API keys are stored in the OS keychain (macOS Keychain, Windows Credential Manager, Linux Secret Service). Falls back to config file if keychain unavailable.

**Environment variable override:** Set `GUARA_API_KEY` to skip stored credentials.

## Context Resolution

Commands that need a project/service resolve context in this order:

1. `--project` / `--service` flags
2. `GUARA_PROJECT` / `GUARA_SERVICE` environment variables
3. `.guara.json` file (walked upward from current directory)

Link a directory to a project:

```bash
guara link
# Creates .guara.json with { "project": "slug", "service": "slug" }
```

## Global Flags

| Flag | Short | Description |
|---|---|---|
| `--json` | | Output as JSON |
| `--quiet` | `-q` | Suppress non-essential output |
| `--project` | `-p` | Project slug override |
| `--service` | `-s` | Service slug override |
| `--yes` | `-y` | Skip confirmation prompts |
| `--api-key` | | Override API key for this request |
| `--api-url` | | Override API base URL |

## Command Index

| Command | Purpose | See skill |
|---|---|---|
| `login` | Authenticate | — |
| `logout` | Clear credentials | — |
| `whoami` | Show current user | — |
| `projects list` | List projects | guara-deploy |
| `projects create` | Create project | guara-deploy |
| `projects info` | Project details | guara-deploy |
| `services list` | List services | guara-deploy |
| `services create` | Create service | guara-deploy |
| `services info` | Service details | guara-deploy |
| `services start` | Start stopped service | guara-deploy |
| `services stop` | Stop running service | guara-deploy |
| `services restart` | Rolling restart | guara-deploy |
| `services delete` | Delete service | guara-deploy |
| `deploy` | Trigger deployment | guara-deploy |
| `rollback` | Rollback deployment | guara-deploy |
| `deployments list` | Deployment history | guara-deploy |
| `scale` | Toggle autoscaling | guara-deploy |
| `domains list` | List custom domains | guara-deploy |
| `domains add` | Add custom domain | guara-deploy |
| `domains remove` | Remove domain | guara-deploy |
| `env list` | List env vars | guara-develop |
| `env set` | Set env vars | guara-develop |
| `env unset` | Remove env vars | guara-develop |
| `link` | Link dir to project | guara-develop |
| `unlink` | Remove link | guara-develop |
| `exec` | Shell into container | guara-develop |
| `proxy` | Forward local port | guara-develop |
| `logs` | View/stream logs | guara-develop |
| `open` | Open service in browser | — |
| `status` | Platform status | — |
| `config list` | Show CLI config | — |
| `config get` | Get config value | — |
| `config set` | Set config value | — |
| `config reset` | Reset to defaults | — |

For full flag reference, see [references/commands.md](references/commands.md).

## Tier Information

For tier limits, pricing, and quotas, see [guaracloud.com/docs](https://guaracloud.com/docs). The CLI will return descriptive errors when a tier limit is reached.

## Important Rules

- **Always use the `guara` CLI.** Do not call the REST API directly.
- **Check service status** before suggesting actions. Run `guara services info` to see current state.
- **Use `--json` for scripting.** Parse structured output instead of scraping human-readable text.
- **Link projects** with `guara link` so context resolution works automatically.
