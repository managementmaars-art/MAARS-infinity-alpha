# Troubleshooting (Symptom-First)

## Use When
- A job, deploy, build, or auth operation is failing and you need a diagnosis path.
- You have an error message or symptom and need the fix, not the architecture.
- You need the quick triage sequence before diving into specific docs.

## Load Next
- `references/deploy-debug.md` for architecture-level debugging (K8s, workers, ingress).
- `references/secrets-auth.md` for auth and secret resolution failures.
- `references/builds-releases.md` for build-specific failure analysis.

## Ask If Missing
- Confirm the exact error message or symptom.
- Confirm the environment (staging, local docker, k3d) and `EVE_API_URL`.
- Confirm whether the issue is with a job, deploy, build, or system-level operation.

## Quick Triage (Start Here)

Run these three commands first. They cover 80% of issues.

```bash
eve system health --json                  # 1. Is the platform up?
eve job diagnose <id>                     # 2. What went wrong with this job?
./bin/eh status                           # 3. What's the local environment state?
```

If `system health` fails, the platform is down -- check `eve system logs api`.
If `job diagnose` returns useful output, follow its recommendations.
If `./bin/eh status` shows services stopped, restart with `./bin/eh start <mode>`.

## Auth + Identity Issues

| Symptom | Cause | Fix |
|---|---|---|
| `401 Unauthorized` on every request | No token or expired token | `eve auth login --email <email>` |
| `403 Forbidden` | Missing permission for action | `eve auth permissions` to check catalog; `eve access explain --org <id> --user <id> --permission <perm>` |
| "OAuth token has expired" | Claude auth stale | `./bin/eh auth extract --save` then redeploy |
| Bootstrap fails | Bootstrap window closed or token wrong | Check `eve auth bootstrap --status`; use recovery mode or set `EVE_BOOTSTRAP_TOKEN` |
| Service principal token rejected | Token revoked or scopes insufficient | `eve auth list-service-accounts --org <id>`; recreate if needed |
| `eve auth creds` shows expired | Local AI tool creds stale | Re-auth with the tool (`claude setup-token`, codex login); then `eve auth sync` |

## Secret Resolution Issues

| Symptom | Cause | Fix |
|---|---|---|
| Job fails during clone | `GITHUB_TOKEN` missing or wrong scope | `eve secrets show GITHUB_TOKEN --project <id>`; re-set with `eve secrets set` |
| "secret resolution failed" | `EVE_INTERNAL_API_KEY` missing | Set on both API and worker; restart |
| Empty env var in runner | Secret not at correct scope | Check scope hierarchy: project > user > org > system |
| `[resolveSecrets]` warnings in logs | Master key or internal key mismatch | Verify `EVE_SECRETS_MASTER_KEY` and `EVE_INTERNAL_API_KEY` are set |
| Secret shows `null` | Secret exists at wrong scope | `eve secrets list --project <id>` vs `--org <id>` to find it |

## Deploy + Environment Issues

| Symptom | Cause | Fix |
|---|---|---|
| Deploy hangs at "deploying" | Pipeline step stuck or health check loop | `eve pipeline logs <pipeline> <run-id> --follow` to find stuck step |
| `status: degraded` after deploy | Pods unhealthy | `eve env diagnose <project> <env>` for K8s events |
| Ingress returns 404 | Missing ingress config or DNS | Check manifest `x-eve.ingress.public: true`; verify `EVE_DEFAULT_DOMAIN` |
| "Service X ready check failed" | Container crash or config error | `eve env logs <project> <env> --service <name>` |
| Rollback needed | Bad deploy | `eve env rollback <project> <env>` |
| Env stuck in unknown state | K8s unreachable | `eve env recover <project> <env>` to analyze and suggest recovery |
| Deploy bypasses pipeline | Used `--direct` flag | Re-run without `--direct` to use configured pipeline |

## Job Execution Issues

| Symptom | Cause | Fix |
|---|---|---|
| Job won't start (stuck in ready) | Orchestrator unhealthy or concurrency full | `eve system orchestrator status`; check `ORCH_CONCURRENCY` |
| Job blocked | Unresolved dependencies | `eve job dep list <id>` to see blockers |
| Job failed immediately | Clone, secret, or workspace error | `eve job diagnose <id>` -- check first attempt's error |
| Job stuck active ("running for Xs") | Harness hanging or worker crash | `eve job diagnose <id>`; check runner-logs if K8s |
| Harness logs missing | Startup error, not harness | `eve job runner-logs <id>` for K8s pod logs |

## Build Issues

| Symptom | Cause | Fix |
|---|---|---|
| Build fails | Dockerfile error or registry auth | `eve build diagnose <build_id>` for last 30 lines of BuildKit output |
| "registry auth failed" | Wrong registry config | Use `registry: "eve"` for managed; set `REGISTRY_USERNAME`/`REGISTRY_PASSWORD` for BYO |
| Build not triggered | Pipeline not configured | Check `environments.<env>.pipeline` in manifest |
| Image not found after build | Tag mismatch | `eve build show <id>` for artifacts; check release tag |
| Build timeout | Large image or slow network | Check BuildKit resource limits; consider multi-stage builds |

## Network + Connectivity Issues

| Symptom | Cause | Fix |
|---|---|---|
| `ECONNREFUSED` to API | Wrong `EVE_API_URL` or service down | `./bin/eh status` to verify; correct URL for mode |
| k3d ingress 502 | Service not ready or wrong namespace | `eve system pods` to check; wait for rollout |
| Can't reach `*.lvh.me` | DNS or k3d not running | `lvh.me` resolves to 127.0.0.1; ensure k3d cluster is up |
| Webhook delivery fails | Endpoint unreachable or HMAC mismatch | `eve webhooks deliveries <id>` for delivery logs |

## Real-Time Debugging (Multi-Terminal)

For active issues, use three terminals simultaneously:

```bash
# Terminal 1: Watch job status
watch -n 5 'eve job show <id> --verbose 2>&1 | head -30'

# Terminal 2: Stream harness output
eve job follow <id>

# Terminal 3: Runner pod logs (K8s only)
eve job runner-logs <id>
```

Startup errors (clone, workspace, auth) appear in orchestrator/worker/runner logs, **not** in `follow`.

```bash
eve system logs api -f                # API errors
eve system logs orchestrator -f       # Job claim/dispatch issues
eve system logs worker -f             # Workspace/harness issues
```

## Local Stack Troubleshooting

### Docker Compose

```bash
./bin/eh status                        # Check current mode and ports
./bin/eh start docker                  # Restart stack
docker logs eve-api -f                 # API logs
docker logs eve-orchestrator -f        # Orchestrator logs
docker logs eve-worker -f              # Worker logs
```

Logs for local dev mode at `/tmp/eve-{api,orchestrator,worker}.log`.

### K3d Stack

```bash
eve local status [--watch]             # Full status dashboard
eve local health                       # Health check (exits non-zero if unhealthy)
eve local logs <service> -f            # Stream service logs
eve local reset --force                # Nuclear: destroy + recreate
```

If k3d cluster is stale or corrupted, `eve local reset --force` is the fastest recovery.

## Common Error Reference

| Error Message | Meaning | Fix |
|---|---|---|
| "OAuth token has expired" | Claude auth token stale | `./bin/eh auth extract --save` then redeploy |
| "git clone failed" | Repo inaccessible or token wrong | Check `GITHUB_TOKEN` secret scope |
| "Orchestrator restarted while attempt was running" | Job orphaned on restart | Auto-retries via recovery; no action needed |
| "secret resolution failed" | Internal API key missing/wrong | Set `EVE_INTERNAL_API_KEY` on API + worker |
| "insufficient permissions" | RBAC deny | `eve access explain --org <id> --user <id> --permission <perm>` |

## Debugging Checklist

When all else fails, work through this systematically:

1. **Platform health**: `eve system health --json` -- is the API responding?
2. **Environment state**: `./bin/eh status` -- correct mode, URLs, ports?
3. **Auth state**: `eve auth status` -- valid token? correct org context?
4. **Secrets**: `eve secrets list --project <id>` -- all required keys present?
5. **Job/deploy diagnosis**: `eve job diagnose <id>` or `eve env diagnose <proj> <env>`
6. **Logs**: `eve system logs <service> -f` -- any errors in API/orchestrator/worker?
7. **K8s pods** (last resort): `eve system pods` -- all pods running?
