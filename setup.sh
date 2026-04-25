#!/usr/bin/env bash
# -----------------------------------------------------------------------------
# MAARS Command — one-command setup.
#
# Runs end-to-end:
#   1. verifies Python 3.11+ + MongoDB reachable
#   2. installs backend deps
#   3. writes .env (prompts for OPENAI_API_KEY / ANTHROPIC_API_KEY if missing)
#   4. runs migrations
#   5. seeds a test user, mints an API key, grants 50 credits
#   6. starts uvicorn and prints a usable banner
#
# Notes on spec reconciliation:
#   * Repo uses MongoDB (Motor async), not SQLite — DATABASE_URL is not used
#     by the backend; we set MONGO_URL/DB_NAME instead.
#   * Backend defaults to PORT=8000 (repo convention). Port 3000 is the
#     frontend dev server. Override with: PORT=9000 ./setup.sh
#   * ADMIN_API_KEY is written into .env as a no-op placeholder for future use;
#     the current admin surface is JWT + email-based.
# -----------------------------------------------------------------------------
set -euo pipefail

# ---------------------------------------------------------------- paths + tunables

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$REPO_ROOT/backend"
ENV_FILE="$REPO_ROOT/.env"
PORT="${PORT:-8000}"
MONGO_URL="${MONGO_URL:-mongodb://localhost:27017}"
DB_NAME="${DB_NAME:-maars_infinity}"
TEST_EMAIL="${TEST_EMAIL:-test@maars.local}"

# Portable Python executable discovery. Windows bash usually exposes `python`.
PY="${PYTHON:-}"
if [[ -z "$PY" ]]; then
  if command -v python >/dev/null 2>&1; then PY="python"
  elif command -v python3 >/dev/null 2>&1; then PY="python3"
  else
    echo "ERROR: no python interpreter on PATH" >&2; exit 1
  fi
fi

# ---------------------------------------------------------------- UI helpers

bold()  { printf '\033[1m%s\033[0m\n' "$*"; }
ok()    { printf '  \033[32m✓\033[0m %s\n' "$*"; }
warn()  { printf '  \033[33m!\033[0m %s\n' "$*"; }
fail()  { printf '  \033[31m✗\033[0m %s\n' "$*"; }

banner() {
  printf '\n%s\n' "----------------------------------"
  printf '%s\n' "MAARS Command — setup"
  printf '%s\n\n' "----------------------------------"
}

banner

# ---------------------------------------------------------------- preflight

bold "1/6  Preflight"
PY_VER="$($PY -c 'import sys; print("%d.%d" % sys.version_info[:2])')"
PY_MAJOR="${PY_VER%%.*}"
PY_MINOR="${PY_VER#*.}"
if (( PY_MAJOR < 3 || (PY_MAJOR == 3 && PY_MINOR < 11) )); then
  fail "Python 3.11+ required, found $PY_VER"
  exit 1
fi
ok "Python $PY_VER  ($PY)"

# MongoDB connectivity — try a brief ping via Python (we already have the driver once deps install,
# so we gate this behind a cheap TCP check here and validate in migration step).
if ! "$PY" -c "
import socket, sys, urllib.parse as u
p = u.urlparse('$MONGO_URL')
host = p.hostname or 'localhost'
port = p.port or 27017
try:
    s = socket.create_connection((host, port), timeout=2); s.close(); sys.exit(0)
except Exception as e:
    print(e, file=sys.stderr); sys.exit(1)
" 2>/dev/null; then
  fail "MongoDB not reachable at $MONGO_URL"
  warn "Start it locally (brew / systemd / docker) or set MONGO_URL to a running instance."
  warn "Example: docker run -d -p 27017:27017 --name maars-mongo mongo:7"
  exit 1
fi
ok "MongoDB reachable at $MONGO_URL"

# ---------------------------------------------------------------- deps

bold "2/6  Installing Python dependencies"
"$PY" -m pip install --quiet --disable-pip-version-check -r "$BACKEND_DIR/requirements.txt"
ok "backend requirements installed"

# ---------------------------------------------------------------- .env

bold "3/6  Environment (.env)"

prompt_optional() {
  local var="$1" label="$2" cur
  cur="${!var:-}"
  if [[ -z "$cur" ]] && [[ -f "$ENV_FILE" ]]; then
    cur="$(grep -E "^${var}=" "$ENV_FILE" | tail -1 | cut -d= -f2- || true)"
  fi
  if [[ -z "$cur" ]]; then
    printf "   paste %s (blank to skip): " "$label"
    read -r cur || true
  fi
  printf '%s' "$cur"
}

if [[ ! -f "$ENV_FILE" ]]; then
  warn ".env not found — creating one"
fi

OPENAI_API_KEY_VAL="$(prompt_optional OPENAI_API_KEY "OPENAI_API_KEY")"
ANTHROPIC_API_KEY_VAL="$(prompt_optional ANTHROPIC_API_KEY "ANTHROPIC_API_KEY")"
GROQ_API_KEY_VAL="$(prompt_optional GROQ_API_KEY "GROQ_API_KEY (optional — enables verifier + cheap routing)")"
DEEPSEEK_API_KEY_VAL="$(prompt_optional DEEPSEEK_API_KEY "DEEPSEEK_API_KEY (optional)")"

# Generate secrets only if the file doesn't already have them.
ensure_secret() {
  local name="$1"
  if [[ -f "$ENV_FILE" ]] && grep -qE "^${name}=..+" "$ENV_FILE"; then
    grep -E "^${name}=" "$ENV_FILE" | tail -1 | cut -d= -f2-
  else
    "$PY" -c 'import secrets; print(secrets.token_urlsafe(32))'
  fi
}

JWT_SECRET_VAL="$(ensure_secret JWT_SECRET)"
MAARS_API_KEY_PEPPER_VAL="$(ensure_secret MAARS_API_KEY_PEPPER)"

cat > "$ENV_FILE" <<EOF
# Written by setup.sh — safe to hand-edit.
# ─── core ────────────────────────────────────────────────────────────
PORT=${PORT}
MONGO_URL=${MONGO_URL}
DB_NAME=${DB_NAME}
JWT_SECRET=${JWT_SECRET_VAL}
MAARS_API_KEY_PEPPER=${MAARS_API_KEY_PEPPER_VAL}
ADMIN_API_KEY=admin123

# ─── LLM provider keys (optional — missing keys = provider disabled) ─
OPENAI_API_KEY=${OPENAI_API_KEY_VAL}
ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY_VAL}
GROQ_API_KEY=${GROQ_API_KEY_VAL}
DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY_VAL}

# ─── Stripe (optional — set to enable /billing/* flows) ──────────────
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=

# ─── hardening tunables ──────────────────────────────────────────────
MAARS_IP_RPM=300
ENVIRONMENT=development
EOF
ok ".env written  ($ENV_FILE)"

# Export everything for the current process so the Python scripts see it.
set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a

# ---------------------------------------------------------------- migrations

bold "4/6  Database migrations"
( cd "$BACKEND_DIR" && "$PY" -m scripts.migrate_wallets )
ok "migrations complete"

# ---------------------------------------------------------------- seed

bold "5/6  Seeding test user + API key + 50 credits"
SEED_OUT="$(cd "$BACKEND_DIR" && "$PY" -m scripts.seed_test_user --email "$TEST_EMAIL" 2>&1)"
MAARS_USER_ID="$(printf '%s\n' "$SEED_OUT" | awk -F= '/^MAARS_USER_ID=/{print $2; exit}')"
MAARS_API_KEY="$(printf '%s\n' "$SEED_OUT" | awk -F= '/^MAARS_API_KEY=/{print $2; exit}')"
MAARS_BALANCE="$(printf '%s\n' "$SEED_OUT" | awk -F= '/^MAARS_BALANCE=/{print $2; exit}')"

if [[ -z "$MAARS_API_KEY" ]]; then
  fail "seed step did not return an API key — raw output below"
  printf '%s\n' "$SEED_OUT"
  exit 1
fi
ok "user_id=$MAARS_USER_ID  balance=${MAARS_BALANCE} credits"

# Cache the credentials so `make dev` (or the next terminal) can print them again.
cat > "$REPO_ROOT/.maars-setup.env" <<EOF
MAARS_USER_ID=$MAARS_USER_ID
MAARS_USER_EMAIL=$TEST_EMAIL
MAARS_API_KEY=$MAARS_API_KEY
MAARS_BALANCE=$MAARS_BALANCE
EOF
ok "credentials cached in .maars-setup.env (git-ignore this file)"

# ---------------------------------------------------------------- banner

API_URL="http://localhost:${PORT}/api"
cat <<EOF

----------------------------------
MAARS READY
----------------------------------
API URL: $API_URL
API KEY: $MAARS_API_KEY
USER ID: $MAARS_USER_ID  (email: $TEST_EMAIL)
BALANCE: $MAARS_BALANCE credits

Test command:

curl $API_URL/v1/chat/completions \\
  -H "Authorization: Bearer $MAARS_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{
    "model": "maars/auto",
    "messages": [
      {"role": "user", "content": "Hello"}
    ]
  }'

Other useful endpoints:
  GET  $API_URL/v1/credits            (JWT auth, not the API key)
  GET  $API_URL/v1/models
  GET  $API_URL/v1/providers/health
  POST $API_URL/v2/platform/orchestrator/run

----------------------------------
Starting backend on port $PORT  —  Ctrl-C to stop.
----------------------------------

EOF

# ---------------------------------------------------------------- run

cd "$BACKEND_DIR"
exec "$PY" -m uvicorn server:app --host 0.0.0.0 --port "$PORT"
