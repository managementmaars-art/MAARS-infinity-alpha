"""Agent quality tests — verifies the prompt enhancer produces
premium, client-opaque, tool-aware system prompts for every agent.

Run: pytest backend/tests/test_agent_quality.py -v

These tests are STATIC — they inspect the enhanced prompt text without
calling any LLM. They catch 3 classes of regression:

  1. **Opacity regression** — a future PR accidentally names a backend
     provider (Apollo, Hunter, Pollinations, Edge TTS, etc.) in the
     agent prompt, which would leak into chat output.

  2. **Tool-awareness regression** — a future tool is added to an
     agent's AGENT_TOOL_MAP but the enhancer doesn't surface it, so
     the LLM doesn't know the tool exists.

  3. **Standards regression** — the MAARS operating standards block
     gets accidentally stripped by an edit.

For runtime quality (does the agent actually produce GOOD output?),
operators run `pytest -v -k live` which hits the real LLM via the
chat endpoint — kept separate because it costs credits.
"""
import pytest


# Every forbidden string — any of these in an agent's system prompt
# means a backend leak is possible.
FORBIDDEN_IN_PROMPT = [
    "Pollinations", "pollinations",
    "Apollo", "apollo.io",
    "Hunter", "hunter.io",
    "SendGrid", "sendgrid",
    "Resend", "resend.com",
    "ElevenLabs", "elevenlabs",
    "Edge TTS", "edge-tts",
    "Deepgram", "deepgram",
    "Fal.ai", "fal-ai",
    "Twilio", "twilio",
    "Brave Search", "brave.com",
]

# Required blocks — the enhanced prompt must contain these.
REQUIRED_SECTIONS = [
    "MAARS OPERATING STANDARDS",
    "QUALITY FLOOR",
    "BRAND VOICE",
    "PLATFORM INTEGRITY",
    "COMPLIANCE BASELINE",
    "ESCALATE TO HUMAN",
]

# Agents we care most about — the outbound + creative workhorses.
CRITICAL_AGENTS = [
    "agent_commander",
    "agent_marketing",
    "agent_sales",
    "agent_socialmedia",
    "agent_email",
    "agent_growthhacker",
    "agent_copywriter",
]


@pytest.fixture(scope="module")
def agent_lookup():
    from config import DEFAULT_AGENTS
    return {a["agent_id"]: a for a in DEFAULT_AGENTS}


@pytest.fixture(scope="module")
def tool_map():
    from config import AGENT_TOOL_MAP
    return AGENT_TOOL_MAP


# ──────────────────────────────────────────────────────────────────
# 1. Opacity tests — no backend brand names in any enhanced prompt.
# ──────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("agent_id", CRITICAL_AGENTS)
def test_no_backend_leaks_in_prompt(agent_id, agent_lookup, tool_map):
    from services.agents.agent_prompt_enhancer import enhance_agent_prompt
    agent = agent_lookup.get(agent_id)
    assert agent is not None, f"{agent_id} not in DEFAULT_AGENTS"
    tools = tool_map.get(agent_id, [])
    enhanced = enhance_agent_prompt(agent, tools=tools)
    for forbidden in FORBIDDEN_IN_PROMPT:
        assert forbidden not in enhanced, (
            f"LEAK in {agent_id}: found '{forbidden}'. Agent could mention "
            "this backend to a client. Check recent edits to the agent's "
            "system_prompt or AGENT_TOOL_MAP description."
        )


# ──────────────────────────────────────────────────────────────────
# 2. Required sections — standards block must be present.
# ──────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("agent_id", CRITICAL_AGENTS)
def test_enhanced_prompt_has_required_sections(agent_id, agent_lookup, tool_map):
    from services.agents.agent_prompt_enhancer import enhance_agent_prompt
    agent = agent_lookup[agent_id]
    tools = tool_map.get(agent_id, [])
    enhanced = enhance_agent_prompt(agent, tools=tools)
    for section in REQUIRED_SECTIONS:
        assert section in enhanced, (
            f"{agent_id} is missing required section '{section}'. "
            "Someone may have stripped the MAARS operating standards block "
            "in agent_prompt_enhancer.py."
        )


# ──────────────────────────────────────────────────────────────────
# 3. Tool awareness — every tool in AGENT_TOOL_MAP appears in prompt.
# ──────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("agent_id", CRITICAL_AGENTS)
def test_all_assigned_tools_surfaced(agent_id, agent_lookup, tool_map):
    from services.agents.agent_prompt_enhancer import enhance_agent_prompt
    agent = agent_lookup[agent_id]
    tools = tool_map.get(agent_id, [])
    enhanced = enhance_agent_prompt(agent, tools=tools)
    for tool_name in tools:
        assert tool_name in enhanced, (
            f"{agent_id} has '{tool_name}' in AGENT_TOOL_MAP but it's not "
            "visible in the enhanced prompt. The LLM won't know this tool "
            "exists. Check agent_prompt_enhancer._tool_block()."
        )


# ──────────────────────────────────────────────────────────────────
# 4. Outbound agents must have the right tools — catches config drift.
# ──────────────────────────────────────────────────────────────────

OUTBOUND_REQUIRED_TOOLS = {
    "agent_sales":        ["search_leads", "send_cold_email", "run_campaign"],
    "agent_marketing":    ["run_campaign", "enhance_prompt"],
    "agent_growthhacker": ["search_leads", "run_campaign"],
    "agent_email":        ["send_cold_email", "run_campaign"],
    "agent_socialmedia":  ["post_linkedin", "schedule_post"],
}


@pytest.mark.parametrize("agent_id,required_tools", list(OUTBOUND_REQUIRED_TOOLS.items()))
def test_outbound_agents_have_required_tools(agent_id, required_tools, tool_map):
    actual = set(tool_map.get(agent_id, []))
    missing = [t for t in required_tools if t not in actual]
    assert not missing, (
        f"{agent_id} is missing outbound tools: {missing}. Without these "
        "the agent can't do its core job. Add them in config.AGENT_TOOL_MAP."
    )


# ──────────────────────────────────────────────────────────────────
# 5. Agent descriptions themselves should be neutral too — clients
#    see these in the agent picker and "agent did X" mentions.
# ──────────────────────────────────────────────────────────────────

def test_agent_descriptions_have_no_backend_names(agent_lookup):
    for agent_id, agent in agent_lookup.items():
        desc = agent.get("description", "") + " " + agent.get("role", "")
        for forbidden in FORBIDDEN_IN_PROMPT:
            assert forbidden not in desc, (
                f"{agent_id} description leaks '{forbidden}': {desc!r}"
            )


# ──────────────────────────────────────────────────────────────────
# 6. Tool descriptions in config.AGENT_TOOLS are neutral.
# ──────────────────────────────────────────────────────────────────

def test_agent_tools_descriptions_neutral():
    from config import AGENT_TOOLS
    for tname, tmeta in AGENT_TOOLS.items():
        desc = tmeta.get("description", "")
        for forbidden in FORBIDDEN_IN_PROMPT:
            assert forbidden not in desc, (
                f"tool '{tname}' description leaks '{forbidden}': {desc!r}"
            )


# ──────────────────────────────────────────────────────────────────
# 7. Sanity: enhanced prompt is substantially longer than the base —
#    confirms the enhancer actually added content.
# ──────────────────────────────────────────────────────────────────

def test_enhancer_adds_substantial_content(agent_lookup, tool_map):
    from services.agents.agent_prompt_enhancer import enhance_agent_prompt
    agent = agent_lookup["agent_marketing"]
    tools = tool_map.get("agent_marketing", [])
    base = agent.get("system_prompt", "")
    enhanced = enhance_agent_prompt(agent, tools=tools)
    assert len(enhanced) > len(base) + 1000, (
        "Enhanced prompt should be at least 1000 chars longer than base "
        "(standards block + tool hints). If not, the enhancer is broken."
    )
