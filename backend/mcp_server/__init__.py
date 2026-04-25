"""MAARS MCP server — exposes MAARS as an MCP-compatible toolset.

Run as a sidecar so a Cursor/Claude Desktop user can plug in one URL
(SSE) or one command (stdio) and drive MAARS from their editor:

    claude-desktop config.json  →  command: python -m mcp_server
    cursor settings             →  MCP URL: http://host/mcp/sse

Tools surfaced (wrap existing MAARS services 1:1):
  • maars.chat            — routes through llm_gateway.complete()
  • maars.image           — media_router image gen
  • maars.video           — media_router video gen
  • maars.tts             — voice synth
  • maars.web_search      — live web search
  • maars.list_agents     — the 499-agent roster
  • maars.agent_chat      — invoke one specific agent_id
  • maars.list_integrations — per-provider status
  • maars.integration_act — drive any connected integration (LinkedIn/X/etc)

Authority: the MCP client authenticates via a MAARS_MCP_TOKEN mapped to
a MAARS user_id, so per-agent budgets + wallet + skill cache all apply
exactly like a direct FastAPI call.
"""
