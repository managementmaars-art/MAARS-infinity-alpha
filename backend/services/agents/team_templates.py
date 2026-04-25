"""Team definitions — the collaborative workspaces 499 agents are grouped into.

Architecture:
  - An agent has an **individual office** (its specialist SOP, studio_tools, skills)
  - An agent belongs to a **team** (a shared workspace + team_sop + member list)
  - Commander Orion delegates to teams; teams internally coordinate members

28 teams cover the entire 499-agent roster. Each team:
  • maps to one-or-more role families (see role_templates.py)
  • has a team-wide SOP (intake → plan → fan-out to members → collect → deliver)
  • shares a studio_name (e.g. "Video Production Studio") + mission + memory tags
  • has a monthly budget envelope and a team lead

Adding a team:
  1. Append a TEAM_* dict below.
  2. Add its role_family matches to `TEAM_BY_ROLE_FAMILY`.
  3. Append to `ALL_TEAMS`.
"""
from __future__ import annotations
from typing import Any


# ── Team definitions ─────────────────────────────────────────────────

TEAM_COMMANDER = {
    "team_id":    "team_commander",
    "name":       "Commander's Bridge",
    "department": "Core Leadership",
    "studio_name":"Commander's Bridge",
    "mission":    "Orchestrate every MAARS capability into coordinated, verified action. "
                  "Never act without a measurable objective; never ship without verification.",
    "role_families": ["commander"],
    "shared_tools": ["query_agent_history", "create_task", "update_task",
                     "delegate_to_agent", "send_slack", "send_email"],
    "memory_tags": ["commander", "orchestration", "governance"],
    "languages":   ["en", "es", "fr", "de", "pt", "ja", "zh", "ar", "hi"],
    "monthly_budget_credits": 100_000,
}


TEAM_VIDEO_PRODUCTION = {
    "team_id":    "team_video_production",
    "name":       "Video Production Team",
    "department": "Creative & Marketing",
    "studio_name":"Video Production Studio",
    "mission":    "Ship polished product videos from brief to final MP4 — research every "
                  "angle, storyboard, generate footage + voice-over in any language, composite.",
    "role_families": ["video_creator", "designer", "writer", "brand_pr"],
    "shared_tools": ["web_search", "browser_open", "browser_navigate", "browser_extract",
                     "browser_screenshot", "generate_image", "generate_video",
                     "generate_voiceover", "generate_tts", "composite_video",
                     "send_email", "send_slack", "update_task"],
    "memory_tags": ["video", "creative", "brand", "product_ad"],
    "languages":   ["en", "es", "fr", "de", "pt", "ja", "zh", "ar", "hi", "it",
                    "nl", "pl", "ru", "tr", "id", "vi", "ko"],
    "monthly_budget_credits": 40_000,
}


TEAM_CONTENT_WRITING = {
    "team_id":    "team_content_writing",
    "name":       "Content & Writing Desk",
    "department": "Creative & Marketing",
    "studio_name":"Writing Desk",
    "mission":    "Research-backed writing that sounds human, ranks on target keywords, converts.",
    "role_families": ["writer"],
    "shared_tools": ["web_search", "browser_open", "browser_extract", "enhance_prompt",
                     "send_email", "send_slack", "update_task"],
    "memory_tags": ["writing", "content", "seo"],
    "languages":   ["en", "es", "fr", "de", "pt", "ja", "zh", "ar", "hi", "it"],
    "monthly_budget_credits": 20_000,
}


TEAM_DESIGN_STUDIO = {
    "team_id":    "team_design_studio",
    "name":       "Design Studio",
    "department": "Creative & Marketing",
    "studio_name":"Design Studio",
    "mission":    "Turn briefs into on-brand, export-ready visual assets backed by moodboard research.",
    "role_families": ["designer"],
    "shared_tools": ["web_search", "browser_extract", "browser_screenshot",
                     "enhance_prompt", "generate_image",
                     "send_slack", "send_email", "update_task"],
    "memory_tags": ["design", "visual", "brand"],
    "languages":   ["en", "es", "fr", "de", "pt", "ja", "zh", "ar", "hi"],
    "monthly_budget_credits": 30_000,
}


TEAM_STRATEGY = {
    "team_id":    "team_strategy",
    "name":       "Strategy Room",
    "department": "Research & Intelligence",
    "studio_name":"Strategy Room",
    "mission":    "Convert ambiguous business questions into defensible, action-ready strategy — "
                  "always with show-your-work citations.",
    "role_families": ["strategist"],
    "shared_tools": ["web_search", "browser_extract", "analyze_data",
                     "search_leads", "enrich_contact",
                     "send_email", "send_slack", "update_task"],
    "memory_tags": ["strategy", "research", "decisions"],
    "languages":   ["en"],
    "monthly_budget_credits": 25_000,
}


TEAM_RESEARCH = {
    "team_id":    "team_research",
    "name":       "Research Intelligence",
    "department": "Research & Intelligence",
    "studio_name":"Research Desk",
    "mission":    "Source the truth and distinguish it from noise — every claim cited.",
    "role_families": ["researcher"],
    "shared_tools": ["web_search", "browser_open", "browser_navigate", "browser_extract",
                     "analyze_data", "send_email", "send_slack", "update_task"],
    "memory_tags": ["research", "intel"],
    "languages":   ["en"],
    "monthly_budget_credits": 20_000,
}


TEAM_ANALYTICS = {
    "team_id":    "team_analytics",
    "name":       "Analytics & Experimentation",
    "department": "Research & Intelligence",
    "studio_name":"Analytics Lab",
    "mission":    "Turn data into decision-ready insights; design statistically-sound experiments.",
    "role_families": ["data_analyst", "experimenter"],
    "shared_tools": ["sql_query", "mongo_query", "rag_query", "analyze_data",
                     "code_python", "send_email", "send_slack", "update_task"],
    "memory_tags": ["data", "analytics", "experiments"],
    "languages":   ["en"],
    "monthly_budget_credits": 22_000,
}


TEAM_GROWTH_MARKETING = {
    "team_id":    "team_growth_marketing",
    "name":       "Growth & Marketing",
    "department": "Creative & Marketing",
    "studio_name":"Growth Office",
    "mission":    "Run acquisition + activation programs that are research-justified, measurable, compliant.",
    "role_families": ["marketer", "brand_pr"],
    "shared_tools": ["web_search", "search_leads", "enrich_contact", "browser_extract",
                     "enhance_prompt", "generate_image", "send_cold_email", "run_campaign",
                     "post_linkedin", "schedule_post", "analyze_data",
                     "send_email", "send_slack", "update_task"],
    "memory_tags": ["growth", "marketing", "campaigns", "brand"],
    "languages":   ["en", "es", "fr", "de", "pt"],
    "monthly_budget_credits": 25_000,
}


TEAM_SALES_OUTBOUND = {
    "team_id":    "team_sales_outbound",
    "name":       "Sales Outbound",
    "department": "Sales & Revenue",
    "studio_name":"Sales Office",
    "mission":    "Convert qualified ICP matches into booked meetings through research-driven outreach.",
    "role_families": ["sdr"],
    "shared_tools": ["web_search", "search_leads", "enrich_contact", "browser_extract",
                     "hubspot_op", "salesforce_op", "send_cold_email", "post_linkedin",
                     "send_sms", "twilio_sms", "create_task", "send_slack", "update_task"],
    "memory_tags": ["sales", "outreach", "pipeline"],
    "languages":   ["en", "es"],
    "monthly_budget_credits": 15_000,
}


TEAM_REVENUE_OPS = {
    "team_id":    "team_revenue_ops",
    "name":       "Revenue Operations",
    "department": "Sales & Revenue",
    "studio_name":"Revenue Strategy Room",
    "mission":    "Model pipeline, find leaks, design programs that hit the revenue number.",
    "role_families": ["revenue_strategy"],
    "shared_tools": ["hubspot_op", "salesforce_op", "analyze_data", "sql_query",
                     "create_task", "update_task", "send_email", "send_slack"],
    "memory_tags": ["revenue", "strategy", "gtm"],
    "languages":   ["en"],
    "monthly_budget_credits": 18_000,
}


TEAM_CUSTOMER_SUCCESS = {
    "team_id":    "team_customer_success",
    "name":       "Customer Success",
    "department": "Customer Experience & Operations",
    "studio_name":"Support Studio",
    "mission":    "Resolve customer issues on first contact with tone that leaves them feeling heard; "
                  "capture learnings for product.",
    "role_families": ["customer_success"],
    "shared_tools": ["query_agent_history", "rag_query", "web_search", "send_email",
                     "send_slack", "intercom_send", "zendesk_ticket", "freshdesk_ticket",
                     "webhook_action", "update_task", "create_task"],
    "memory_tags": ["support", "cx", "tickets"],
    "languages":   ["en", "es", "fr", "de", "pt", "ja", "zh", "ar", "hi"],
    "monthly_budget_credits": 18_000,
}


TEAM_ENGINEERING = {
    "team_id":    "team_engineering",
    "name":       "Engineering Bay",
    "department": "Product & Engineering",
    "studio_name":"Engineering Bay",
    "mission":    "Ship production-grade code with tests, docs, and verifiable behavior.",
    "role_families": ["developer"],
    "shared_tools": ["github_action", "query_agent_history", "analyze_data",
                     "send_slack", "update_task", "create_task"],
    "memory_tags": ["engineering", "code", "repo"],
    "languages":   ["en"],
    "monthly_budget_credits": 22_000,
}


TEAM_PLATFORM = {
    "team_id":    "team_platform",
    "name":       "Platform & Infrastructure",
    "department": "Platform & Infrastructure",
    "studio_name":"Control Room",
    "mission":    "Keep the system observable, fast, and within cost ceilings.",
    "role_families": ["data_platform"],
    "shared_tools": ["github_action", "webhook_action", "analyze_data", "create_task",
                     "update_task", "send_slack"],
    "memory_tags": ["platform", "data", "infra"],
    "languages":   ["en"],
    "monthly_budget_credits": 20_000,
}


TEAM_AI_LAB = {
    "team_id":    "team_ai_lab",
    "name":       "AI Lab",
    "department": "Platform & Infrastructure",
    "studio_name":"AI Lab",
    "mission":    "Make every model call cheaper, faster, better — with evidence.",
    "role_families": ["ai_optimizer"],
    "shared_tools": ["analyze_data", "http_request", "code_python", "github_action",
                     "webhook_action", "send_email", "send_slack", "update_task"],
    "memory_tags": ["ai_ops", "optimization", "models"],
    "languages":   ["en"],
    "monthly_budget_credits": 15_000,
}


TEAM_KNOWLEDGE = {
    "team_id":    "team_knowledge",
    "name":       "Memory & Knowledge",
    "department": "Platform & Infrastructure",
    "studio_name":"Knowledge Graph Office",
    "mission":    "Structure collective knowledge so humans + agents find what they need in one hop.",
    "role_families": ["knowledge_architect", "memory_ops"],
    "shared_tools": ["rag_query", "mongo_query", "sql_query", "code_python",
                     "webhook_action", "send_email", "update_task"],
    "memory_tags": ["knowledge", "taxonomy", "graph", "memory"],
    "languages":   ["en"],
    "monthly_budget_credits": 12_000,
}


TEAM_PRODUCT = {
    "team_id":    "team_product",
    "name":       "Product Office",
    "department": "Product & Engineering",
    "studio_name":"Product Office",
    "mission":    "Ship the right thing — customer-validated, shippable by the team, measurable impact.",
    "role_families": ["product_mgr"],
    "shared_tools": ["rag_query", "analyze_data", "query_agent_history", "web_search",
                     "send_slack", "create_task", "update_task"],
    "memory_tags": ["product", "prd", "roadmap"],
    "languages":   ["en"],
    "monthly_budget_credits": 15_000,
}


TEAM_FINANCE = {
    "team_id":    "team_finance",
    "name":       "Finance Desk",
    "department": "Sales & Revenue",
    "studio_name":"Finance Desk",
    "mission":    "Model the numbers with reconciled inputs + named assumptions; never a forecast without caveats.",
    "role_families": ["finance_analyst"],
    "shared_tools": ["sql_query", "mongo_query", "analyze_data", "code_python",
                     "send_email", "send_slack", "update_task"],
    "memory_tags": ["finance", "fpa", "models"],
    "languages":   ["en"],
    "monthly_budget_credits": 18_000,
}


TEAM_LEGAL = {
    "team_id":    "team_legal",
    "name":       "Legal & Compliance",
    "department": "Strategy & Governance",
    "studio_name":"Legal Desk",
    "mission":    "Review, redline, advise — always with jurisdiction flagged and human attorney on record for high-stakes.",
    "role_families": ["legal", "risk_governance"],
    "shared_tools": ["web_search", "browser_extract", "rag_query", "send_email",
                     "send_slack", "update_task"],
    "memory_tags": ["legal", "compliance", "contracts", "risk"],
    "languages":   ["en"],
    "monthly_budget_credits": 15_000,
}


TEAM_SECURITY = {
    "team_id":    "team_security",
    "name":       "Security Operations",
    "department": "Platform & Infrastructure",
    "studio_name":"Security Operations Center",
    "mission":    "Prevent breaches, detect anomalies, respond fast — with runbooks every oncall can execute.",
    "role_families": ["security"],
    "shared_tools": ["rag_query", "analyze_data", "webhook_action", "http_request",
                     "github_action", "send_email", "send_slack", "update_task"],
    "memory_tags": ["security", "infosec", "soc"],
    "languages":   ["en"],
    "monthly_budget_credits": 15_000,
}


TEAM_OPS_PMO = {
    "team_id":    "team_ops_pmo",
    "name":       "Ops PMO",
    "department": "Customer Experience & Operations",
    "studio_name":"PMO",
    "mission":    "Keep projects on time, on budget, blocker-free — with a paper trail every stakeholder can follow.",
    "role_families": ["project_mgr"],
    "shared_tools": ["create_task", "update_task", "query_tasks", "send_email",
                     "send_slack", "asana", "monday", "trello", "clickup", "linear", "jira"],
    "memory_tags": ["project", "pmo", "delivery"],
    "languages":   ["en"],
    "monthly_budget_credits": 18_000,
}


TEAM_HR = {
    "team_id":    "team_hr",
    "name":       "People & HR",
    "department": "Customer Experience & Operations",
    "studio_name":"People Office",
    "mission":    "Hire well, retain well, handle sensitive issues with discretion — all inside the law.",
    "role_families": ["hr"],
    "shared_tools": ["query_agent_history", "web_search", "rag_query", "send_email",
                     "send_slack", "create_task", "update_task", "webhook_action"],
    "memory_tags": ["hr", "people", "hiring"],
    "languages":   ["en"],
    "monthly_budget_credits": 10_000,
}


TEAM_PROCUREMENT = {
    "team_id":    "team_procurement",
    "name":       "Procurement",
    "department": "Customer Experience & Operations",
    "studio_name":"Procurement Desk",
    "mission":    "Source the right vendors at the right price with the right contracts.",
    "role_families": ["procurement"],
    "shared_tools": ["web_search", "browser_extract", "enrich_contact", "send_email",
                     "send_slack", "create_task", "update_task", "webhook_action"],
    "memory_tags": ["procurement", "vendors", "contracts"],
    "languages":   ["en"],
    "monthly_budget_credits": 10_000,
}


TEAM_RECOVERY = {
    "team_id":    "team_recovery",
    "name":       "Incident & Recovery",
    "department": "Platform & Infrastructure",
    "studio_name":"Incident Room",
    "mission":    "When things break: contain blast radius, restore service, write the postmortem so we don't repeat.",
    "role_families": ["recovery"],
    "shared_tools": ["analyze_data", "http_request", "webhook_action", "integration_action",
                     "send_slack", "send_email", "query_agent_history", "create_task",
                     "update_task"],
    "memory_tags": ["incident", "recovery", "uptime"],
    "languages":   ["en"],
    "monthly_budget_credits": 15_000,
}


TEAM_EXECUTION = {
    "team_id":    "team_execution",
    "name":       "Execution & Deployment",
    "department": "Customer Experience & Operations",
    "studio_name":"Execution Console",
    "mission":    "Execute verified plans against real systems — with approvals, safe rollout, complete audit trail.",
    "role_families": ["executor"],
    "shared_tools": ["integration_action", "http_request", "webhook_action",
                     "send_slack", "send_email", "update_task", "rag_query"],
    "memory_tags": ["execution", "deploy", "audit"],
    "languages":   ["en"],
    "monthly_budget_credits": 15_000,
}


TEAM_VERIFICATION = {
    "team_id":    "team_verification",
    "name":       "Quality Verification",
    "department": "Strategy & Governance",
    "studio_name":"Verification Desk",
    "mission":    "Catch errors before they reach the operator — every claim, number, artifact cross-checked.",
    "role_families": ["verifier"],
    "shared_tools": ["web_search", "browser_extract", "analyze_data", "rag_query",
                     "sql_query", "code_python", "send_slack", "send_email", "update_task"],
    "memory_tags": ["verification", "quality", "truth"],
    "languages":   ["en"],
    "monthly_budget_credits": 12_000,
}


TEAM_REPORTING = {
    "team_id":    "team_reporting",
    "name":       "Executive Reporting",
    "department": "Strategy & Governance",
    "studio_name":"Executive Reporting Desk",
    "mission":    "Turn sprawling data into 1-page decisions — every insight tied to an action, every number to a source.",
    "role_families": ["reporting"],
    "shared_tools": ["sql_query", "mongo_query", "analyze_data", "rag_query",
                     "send_email", "send_slack", "update_task"],
    "memory_tags": ["reporting", "executive", "dashboards"],
    "languages":   ["en"],
    "monthly_budget_credits": 12_000,
}


TEAM_INVESTOR_RELATIONS = {
    "team_id":    "team_investor_relations",
    "name":       "Investor Relations",
    "department": "Sales & Revenue",
    "studio_name":"IR Desk",
    "mission":    "Keep investors informed, confident, aligned — with data-backed narratives tied to shareholder value.",
    "role_families": ["investor_relations"],
    "shared_tools": ["sql_query", "analyze_data", "web_search", "enhance_prompt",
                     "send_email", "update_task", "send_slack"],
    "memory_tags": ["investor", "ir", "board"],
    "languages":   ["en"],
    "monthly_budget_credits": 10_000,
}


TEAM_SECRETARIAT = {
    "team_id":    "team_secretariat",
    "name":       "Executive Secretariat",
    "department": "Customer Experience & Operations",
    "studio_name":"Executive Office",
    "mission":    "Manage the operator's time, communications, and action items with precision.",
    "role_families": ["secretary"],
    "shared_tools": ["gmail_op", "send_email", "send_slack", "create_task", "update_task",
                     "zoom_create_meeting", "schedule_post", "webhook_action",
                     "query_tasks", "query_agent_history", "calendly_list"],
    "memory_tags": ["executive", "calendar", "ops"],
    "languages":   ["en", "es", "fr", "de", "pt", "ja", "zh", "ar", "hi"],
    "monthly_budget_credits": 10_000,
}


TEAM_INDUSTRY_SPECIALISTS = {
    "team_id":    "team_industry_specialists",
    "name":       "Industry Specialists",
    "department": "Research & Intelligence",
    "studio_name":"Domain Desk",
    "mission":    "Bring deep domain expertise (healthcare, energy, agri, logistics, media, education) — "
                  "answers tied to the sector's standards, regulations, best practices.",
    "role_families": ["industry_specialist"],
    "shared_tools": ["web_search", "browser_open", "browser_extract", "rag_query",
                     "analyze_data", "code_python", "send_email", "send_slack", "update_task"],
    "memory_tags": ["industry", "domain", "vertical"],
    "languages":   ["en"],
    "monthly_budget_credits": 20_000,
}


# ── Registry + detector ──────────────────────────────────────────────

ALL_TEAMS: list[dict[str, Any]] = [
    TEAM_COMMANDER, TEAM_VIDEO_PRODUCTION, TEAM_CONTENT_WRITING, TEAM_DESIGN_STUDIO,
    TEAM_STRATEGY, TEAM_RESEARCH, TEAM_ANALYTICS, TEAM_GROWTH_MARKETING,
    TEAM_SALES_OUTBOUND, TEAM_REVENUE_OPS, TEAM_CUSTOMER_SUCCESS, TEAM_ENGINEERING,
    TEAM_PLATFORM, TEAM_AI_LAB, TEAM_KNOWLEDGE, TEAM_PRODUCT, TEAM_FINANCE,
    TEAM_LEGAL, TEAM_SECURITY, TEAM_OPS_PMO, TEAM_HR, TEAM_PROCUREMENT,
    TEAM_RECOVERY, TEAM_EXECUTION, TEAM_VERIFICATION, TEAM_REPORTING,
    TEAM_INVESTOR_RELATIONS, TEAM_SECRETARIAT, TEAM_INDUSTRY_SPECIALISTS,
]


# Precompute role_family → team_id lookup. First match wins if a role
# family is listed on multiple teams (shouldn't happen — TEAM_GROWTH
# lists brand_pr; TEAM_VIDEO also lists brand_pr and designer because
# they collaborate on video, but we only want brand_pr agents in GROWTH
# and designer agents in DESIGN_STUDIO, NOT video). We flag overlap
# and let explicit agent-level detectors win.
_OVERLAPPING_FAMILIES = {"designer", "writer", "brand_pr"}  # video pulls these in

TEAM_BY_ROLE_FAMILY: dict[str, str] = {}
for team in ALL_TEAMS:
    for fam in team["role_families"]:
        if fam in _OVERLAPPING_FAMILIES and team["team_id"] == "team_video_production":
            continue  # designer stays in DESIGN_STUDIO; only flagged video creators go to video team
        if fam not in TEAM_BY_ROLE_FAMILY:
            TEAM_BY_ROLE_FAMILY[fam] = team["team_id"]


def detect_team_for_agent(agent_row: dict, role_family: str | None = None) -> str:
    """Map an agent row → team_id.

    Priority:
      1. Commander flag → team_commander
      2. Video Content Specialist (explicit) → team_video_production
      3. role_family lookup via TEAM_BY_ROLE_FAMILY
      4. department keyword fallback
    """
    name = (agent_row.get("name") or "").lower()
    role = (agent_row.get("role") or "").lower()
    desc = (agent_row.get("description") or "").lower()

    if agent_row.get("is_commander") or "commander" in role or "commander orion" in name:
        return "team_commander"

    # Video Content Specialist detector (same as office_seeder._is_video_creator)
    blob = f"{name} {role} {desc}"
    if ("video" in blob) and any(k in blob for k in (
        "creator", "producer", "director", "editor", "animator",
        "specialist", "content", "production",
    )):
        return "team_video_production"

    if role_family and role_family in TEAM_BY_ROLE_FAMILY:
        return TEAM_BY_ROLE_FAMILY[role_family]

    # Department-level fallback
    dept = (agent_row.get("department") or "").lower()
    if "creative" in dept or "marketing" in dept:  return "team_growth_marketing"
    if "research" in dept or "intelligence" in dept: return "team_research"
    if "sales" in dept or "revenue" in dept:       return "team_sales_outbound"
    if "engineering" in dept or "product" in dept: return "team_engineering"
    if "customer" in dept or "operations" in dept: return "team_customer_success"
    if "strategy" in dept or "governance" in dept: return "team_legal"
    if "platform" in dept or "infrastructure" in dept: return "team_platform"

    return "team_industry_specialists"


def team_by_id(team_id: str) -> dict[str, Any] | None:
    for t in ALL_TEAMS:
        if t["team_id"] == team_id:
            return t
    return None
