#!/usr/bin/env bash
# Launch the MAARS MCP server (stdio transport).
#
# Usage — Claude Desktop config.json:
#   {
#     "mcpServers": {
#       "maars": {
#         "command": "bash",
#         "args": ["/absolute/path/to/backend/scripts/run_mcp.sh"],
#         "env": {
#           "MAARS_MCP_TOKEN": "maars_mcp_xxxxxxxx"
#         }
#       }
#     }
#   }
#
# Issue the token at POST /api/mcp/tokens/issue in the MAARS admin UI
# (Universal Gateway → Commander Intel → MCP Tokens). The token maps
# to your MAARS user_id; every tool call the MCP client makes will be
# billed to that wallet and attributed to `agent_commander`.

set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$HERE"

# Prefer the repo venv's Python if present (Windows git-bash + Linux/macOS)
if [ -x "venv/Scripts/python.exe" ]; then
  PY="venv/Scripts/python.exe"
elif [ -x "venv/bin/python" ]; then
  PY="venv/bin/python"
else
  PY="python3"
fi

# Backend URL must point to a running MAARS API (default localhost:8001)
export MAARS_API_URL="${MAARS_API_URL:-http://127.0.0.1:8001}"

exec "$PY" -m mcp_server
