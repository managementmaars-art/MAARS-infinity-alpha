# Deploy Cycle Patterns

The fix/deploy loop for verification against cloud and local environments.

## Environment Detection

```bash
if [[ "$EVE_API_URL" == https://* ]]; then
  ENV_TYPE="cloud"
  echo "Target: Cloud staging ($EVE_API_URL)"
else
  ENV_TYPE="local"
  echo "Target: Local k3d ($EVE_API_URL)"
fi
```

## Cloud (Staging) — Default

Staging is the default verification target. It matches the real user experience.

### Fix/Deploy Loop

```
discover bug → fix code → commit → tag release-v* → push tag →
  wait for CI (publish-images → infra dispatch → deploy) →
  re-run failed scenario
```

### Step by Step

```bash
# 1. Fix the code
git add -A && git commit -m "fix: description of fix"

# 2. Tag and push
LAST_TAG=$(git tag --list 'release-v*' --sort=-version:refname | head -1)
# Increment version (e.g., release-v0.1.241 → release-v0.1.242)
NEXT_VERSION=$(echo "$LAST_TAG" | awk -F. '{print $1"."$2"."$3+1}')
git tag "$NEXT_VERSION"
git push origin main "$NEXT_VERSION"

# 3. Wait for deploy
echo "Waiting for CI to build and deploy..."
# Monitor: check GitHub Actions on both repos
# Source repo: publish-images workflow
# Infra repo: deploy workflow (triggered via repository_dispatch)

# 4. Verify deploy landed
eve system health --json
kubectl -n eve get pods  # Check all pods are Running/Ready

# 5. Re-run the failed scenario
```

### Monitoring the Deploy

Two repos are involved:

1. **Source repo** (`eve-horizon`): `publish-images.yml` builds container images
2. **Infra repo** (`incept5-eve-infra`): receives dispatch, applies k8s manifests

```bash
# Check source repo workflow
gh run list --repo incept5/eve-horizon-2 --workflow publish-images.yml --limit 3

# Check infra repo workflow
gh run list --repo incept5/incept5-eve-infra --limit 3
```

### Typical Timing

| Phase | Duration |
|-------|----------|
| Image builds (6 services) | ~3-5 minutes |
| Repository dispatch | ~10 seconds |
| Infra apply + rollout | ~2-3 minutes |
| **Total** | **~5-8 minutes** |

## Local (k3d)

Local verification is faster but less representative.

### Fix/Deploy Loop

```
discover bug → fix code → pnpm build →
  ./bin/eh k8s-image push → ./bin/eh k8s deploy →
  re-run failed scenario
```

### Step by Step

```bash
# 1. Fix the code
# (edit files)

# 2. Build
pnpm build

# 3. Push images to k3d registry and deploy
./bin/eh k8s-image push
./bin/eh k8s deploy

# 4. Wait for rollout
kubectl -n eve rollout status deployment/eve-api --timeout=120s

# 5. Re-run the failed scenario
```

### Typical Timing

| Phase | Duration |
|-------|----------|
| `pnpm build` | ~30-60 seconds |
| `k8s-image push` | ~30-60 seconds |
| `k8s deploy` | ~30-60 seconds |
| **Total** | **~2-3 minutes** |

## Waiting for Deploys

### Cloud — Poll Until Ready

```bash
wait_for_deploy() {
  local max_wait=600  # 10 minutes
  local interval=30
  local elapsed=0

  while [ $elapsed -lt $max_wait ]; do
    if eve system health --json 2>/dev/null | jq -e '.status == "ok"' > /dev/null; then
      echo "Deploy ready after ${elapsed}s"
      return 0
    fi
    echo "Waiting... (${elapsed}s)"
    sleep $interval
    elapsed=$((elapsed + interval))
  done

  echo "Deploy not ready after ${max_wait}s"
  return 1
}
```

### Local — Rollout Status

```bash
# Wait for all deployments
for deploy in eve-api eve-orchestrator eve-worker eve-agent-runtime eve-gateway; do
  kubectl -n eve rollout status deployment/$deploy --timeout=120s
done
```

## When to Use Which Environment

| Situation | Environment |
|-----------|-------------|
| Initial verification of a new app | Cloud (staging) |
| Rapid iteration on a failing scenario | Local (k3d) |
| Pre-handoff final verification | Cloud (staging) |
| CI automated runs | Cloud (staging) |
| Debugging platform issues | Local (k3d) first, then cloud |

## Including Deploy Cycle in Test Plans

When a scenario is expected to involve fix/deploy iteration, include this section:

```markdown
## Fix/Deploy Cycle

This scenario may require iteration. Follow the deploy cycle for your environment:

### Cloud (Staging)
1. Fix code and commit
2. Tag: `git tag release-v<next> && git push origin main release-v<next>`
3. Wait ~5-8 minutes for CI
4. Verify: `eve system health --json`
5. Re-run from Phase N

### Local (k3d)
1. Fix code
2. `pnpm build && ./bin/eh k8s-image push && ./bin/eh k8s deploy`
3. Wait ~2-3 minutes
4. Re-run from Phase N
```
