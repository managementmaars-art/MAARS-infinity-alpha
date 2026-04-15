#!/usr/bin/env bash
# MAARS · auto-commit
# Fires from a Claude Code Stop hook at the end of every session. Commits any
# work that's new since HEAD — but only with tight guardrails, because a
# misfired auto-commit can poison git history far more than a skipped one.
#
# Guardrails:
#   1. Only stages tracked-file modifications + newly-added files in a short
#      allow-list of paths (backend/, frontend/src/, .claude/MEMORY.md, docs).
#   2. Hard cap on total file count — if the tree looks like a mass rewrite
#      (> MAX_FILES) the commit is skipped and the operator is expected to
#      review manually.
#   3. Never stages anything matching the deny list (.env files, credentials,
#      key material, node_modules, venv, build artifacts).
#   4. No-op if no paths qualify.
#   5. Message is derived from the changed files, not a generic "auto-commit".
#   6. Uses --no-verify guard: if pre-commit hooks fail, we do NOT bypass —
#      we just bail so the operator sees the failure.

set -u

cd "$(git rev-parse --show-toplevel 2>/dev/null)" || exit 0
[ -d .git ] || exit 0

MAX_FILES=40                          # refuse to auto-commit mass rewrites

# Paths we're willing to auto-stage.  (Relative to repo root.) Deliberately
# narrow — only source trees, not data dirs, not build output, not vendored
# binaries. Widen here if a new source tree is added.
ALLOW=(
  "backend/routes/"
  "backend/services/"
  "backend/governance/"
  "backend/verification/"
  "backend/kernel/"
  "backend/memory_system/"
  "backend/orchestrator/"
  "backend/portfolio/"
  "backend/runtime/"
  "backend/scripts/"
  "backend/shared/"
  "backend/testing_harness/"
  "backend/workers/"
  "backend/router/"
  "backend/models/"
  "backend/data/"
  "backend/intelligence/"
  "backend/infinity_catalog.py"
  "backend/server.py"
  "backend/config.py"
  "backend/auth.py"
  "backend/db.py"
  "backend/requirements.txt"
  "backend/Dockerfile"
  "frontend/src/"
  "frontend/public/"
  "frontend/package.json"
  "frontend/Dockerfile"
  "frontend/craco.config.js"
  "frontend/tailwind.config.js"
  "frontend/postcss.config.js"
  ".claude/MEMORY.md"
  ".githooks/"
  "scripts/"
  "README.md"
  "start_backend.bat"
  "start_frontend.bat"
  "docker-compose.yml"
  ".gitignore"
)

# Paths we refuse to auto-stage — even if ALLOW matched. Layered defence
# against accidental commits of secrets, huge binaries, or anything the
# operator clearly didn't author by hand.
DENY_REGEX='(^|/)(\.env(\..*)?$|.*\.(pem|key|crt|pfx|p12|jks|cer)$|.*_rsa$|.*_ed25519$|.*\.ppk$|credentials\.json$|secrets\.(json|yaml|yml|toml)$|node_modules/|venv/|\.venv/|build/|dist/|__pycache__/|\.DS_Store$|\.screenshots/|uploads/|browser_data/|\.git/|test_reports/|failed-[0-9]+\.log$|\.(dll|exe|pak|bin|so|dylib|woff2?|ttf|otf|eot|zip|tar|gz|tgz|7z|whl|mp4|mov|avi|pdf|png|jpg|jpeg|gif|ico|svg\.br|wasm)$)'

# Collect candidate files: modified-tracked + newly-added that are inside
# ALLOW and outside DENY.
candidates=()
while IFS= read -r line; do
    status="${line:0:2}"
    path="${line:3}"
    # skip submodule / rename indicators — we only want plain adds/modifies.
    case "$status" in
        " M"|"MM"|"M "|"A "|"??"|"AM") ;;
        *) continue ;;
    esac
    # allow-list check
    hit=0
    for prefix in "${ALLOW[@]}"; do
        case "$path" in
            "$prefix"*) hit=1; break ;;
        esac
    done
    [ "$hit" = "1" ] || continue
    # deny-list check
    if echo "$path" | grep -Eq "$DENY_REGEX"; then continue; fi
    candidates+=("$path")
done < <(git status --porcelain=v1 2>/dev/null)

# Bail if nothing to do.
if [ "${#candidates[@]}" = "0" ]; then exit 0; fi

# Sanity cap.
if [ "${#candidates[@]}" -gt "$MAX_FILES" ]; then
    echo "auto-commit: ${#candidates[@]} files > $MAX_FILES cap — skipping; review manually." >&2
    exit 0
fi

# Stage.
git add -- "${candidates[@]}" 2>/dev/null || exit 0

# Double-check we actually staged something (guardrails could have filtered
# everything away).
if git diff --cached --quiet; then exit 0; fi

# Build a human-readable commit message from the changed files.
count="${#candidates[@]}"
top3=$(printf '%s\n' "${candidates[@]}" | head -3 | tr '\n' ',' | sed 's/,$//' | sed 's/,/, /g')
if [ "$count" -le 3 ]; then
    subject="auto: update $top3"
else
    subject="auto: update $count files (${top3}, …)"
fi
stamp=$(date -u +"%Y-%m-%dT%H:%MZ")

git commit -m "$subject" -m "Auto-committed by scripts/auto-commit.sh at $stamp." >/dev/null 2>&1 || {
    echo "auto-commit: commit failed (hook? index lock?); leaving changes staged." >&2
    exit 0
}

echo "auto-commit: committed $count file(s) as \"$subject\"."
