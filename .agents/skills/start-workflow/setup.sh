#!/usr/bin/env bash
# workflow-skills setup check
# Verifies all required dependencies are installed

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

ok()   { echo -e "${GREEN}✓${NC} $1"; }
warn() { echo -e "${YELLOW}⚠${NC}  $1"; }
fail() { echo -e "${RED}✗${NC} $1"; MISSING=1; }

MISSING=0

echo "=== workflow-skills dependency check ==="
echo ""

# codex CLI
if command -v codex &>/dev/null; then
  ok "codex CLI  ($(codex --version 2>/dev/null || echo 'installed'))"
else
  fail "codex CLI not found"
  warn "  Install: npm install -g openai/codex"
fi

# openspec CLI
if command -v openspec &>/dev/null; then
  ok "openspec   ($(openspec --version 2>/dev/null || echo 'installed'))"
else
  fail "openspec not found"
  warn "  Install: npm install -g @fission-ai/openspec"
fi

# python3 + requests
if python3 -c "import requests" &>/dev/null; then
  ok "python3 + requests"
else
  fail "python3 requests not found"
  warn "  Install: pip3 install requests"
fi

# ~/.claude/.env check (optional)
echo ""
echo "=== Optional: Telegram integration ==="
if [ -f "$HOME/.claude/.env" ]; then
  if grep -q "TG_BOT_TOKEN" "$HOME/.claude/.env" && grep -q "TG_CHAT_ID" "$HOME/.claude/.env"; then
    ok "~/.claude/.env  (TG_BOT_TOKEN + TG_CHAT_ID found)"
  else
    warn "~/.claude/.env exists but TG_BOT_TOKEN/TG_CHAT_ID missing"
    warn "  Add them to enable security gate and TG notifications"
  fi
else
  warn "~/.claude/.env not found — Telegram features disabled"
  warn "  Create it with: TG_BOT_TOKEN=xxx and TG_CHAT_ID=xxx"
  warn "  Get a bot token from @BotFather on Telegram"
fi

echo ""
if [ "$MISSING" -eq 0 ]; then
  echo -e "${GREEN}All required dependencies OK. Ready to use /start-workflow.${NC}"
else
  echo -e "${RED}Some dependencies are missing. Install them before using /start-workflow.${NC}"
  exit 1
fi
