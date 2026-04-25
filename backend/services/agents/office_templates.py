"""Department-level SOP templates for Agent Offices.

Every agent inherits an SOP from their department. The SOP is the
"research-first then produce" pattern the operator asked for, tuned
per department so a research analyst, a video creator, a salesperson,
and an engineer each follow a workflow that matches THEIR craft —
but all of them begin with thorough intake + context-gathering before
any production step.

Usage:

    from services.agents.office_templates import template_for_network
    template = template_for_network("10F")  # creative_brand
    office = materialize_office(agent_row, template)
"""
from __future__ import annotations
from .agent_office import AgentOffice, SOPStep, SkillWorkflow, QualityRule


# ── The universal 6-phase research-first SOP ─────────────────────────
# Every department's SOP starts from this skeleton. Each department
# fills in tools and expected_output specific to their craft.

def _base_sop(
    *, research_tools: list[str], production_tools: list[str],
    verify_tools: list[str] | None = None,
    deliver_tools: list[str] | None = None,
) -> list[SOPStep]:
    return [
        SOPStep(
            name="understand",
            description="Parse the client request into structured requirements. "
                        "Extract: goal, audience, constraints, format, deadline, "
                        "language, reference materials, success criteria. "
                        "Ask one clarifying question only if something is ambiguous.",
            tools=[],
            required=True,
            expected_output="JSON: { goal, audience, constraints, format, language, success_criteria }",
        ),
        SOPStep(
            name="research",
            description="Gather all external context needed to produce excellent output. "
                        "Web-search for the subject, its history, its competitors, prior art. "
                        "Read every relevant page. Extract facts, quotes, imagery, data "
                        "points. Do not produce yet — fill the reference file first.",
            tools=research_tools,
            required=True,
            expected_output="Research brief: key facts, references, imagery URLs, quotes, "
                           "competitor examples, gap you'll fill.",
        ),
        SOPStep(
            name="plan",
            description="Design the deliverable based on research findings. "
                        "Produce an outline / storyboard / blueprint. Decide tone, "
                        "structure, visual direction, length. Flag budget + "
                        "time cost. Plan must be approved by quality_rules before production.",
            tools=[],
            required=True,
            expected_output="Outline / storyboard / blueprint ready for production.",
        ),
        SOPStep(
            name="produce",
            description="Execute the plan using production tools. Do each step to "
                        "completion before moving to the next. Never ship a half-done output.",
            tools=production_tools,
            required=True,
            expected_output="Final artifact: file, post, report, video, code, etc.",
        ),
        SOPStep(
            name="verify",
            description="Run quality checks against the acceptance criteria. Fix any "
                        "issue discovered. If you can't fix, flag clearly to the client.",
            tools=verify_tools or [],
            required=True,
            expected_output="Pass/fail verdict per quality rule + corrected artifact.",
        ),
        SOPStep(
            name="deliver",
            description="Package the final artifact with a short summary of what was done, "
                        "references used, and any caveats. Store artifact in the reference "
                        "memory for future skill reuse.",
            tools=deliver_tools or [],
            required=True,
            expected_output="Client-facing deliverable + internal memory entry.",
        ),
    ]


# ── Department templates ─────────────────────────────────────────────

CREATIVE_BRAND = {
    "department": "Creative & Marketing",
    "studio_suffix": "Creative Studio",
    "mission_template": "Produce on-brand, research-backed creative output that "
                        "the client can ship the same day.",
    "research_tools":   ["web_search", "browser_open", "browser_navigate",
                         "browser_extract", "browser_screenshot", "search_gif",
                         "enhance_prompt"],
    "production_tools": ["generate_image", "generate_video", "generate_tts",
                         "generate_voiceover", "schedule_post", "post_linkedin",
                         "enhance_prompt"],
    "verify_tools":     ["web_search", "analyze_data"],
    "deliver_tools":    ["schedule_post", "send_slack", "send_email", "webhook_action"],
    "quality_rules": [
        QualityRule("on_brand",      "Output matches brand colors/voice/tone from research", "hard"),
        QualityRule("factually_correct", "Every claim is sourced from research step", "hard"),
        QualityRule("language_correct",  "Text is in client's requested language with native phrasing", "hard"),
        QualityRule("length_target",     "Artifact length matches client spec ±10%", "soft"),
        QualityRule("copyright_safe",    "No copyrighted reference reproduced; references inspired, not copied", "hard"),
    ],
    "memory_tags": ["creative", "brand", "content"],
    "languages":   ["en", "es", "fr", "de", "pt", "ja", "zh", "ar", "hi"],
    "skills": [
        SkillWorkflow(
            skill_id="blog_post_long",
            name="Long-form Blog Post",
            description="Research-backed 1,500-2,500 word article with imagery.",
            trigger_keywords=("blog post", "long-form article", "seo article",
                              "write an article", "thought leadership"),
            steps=[], avg_credits=900,
        ),
        SkillWorkflow(
            skill_id="brand_social_pack",
            name="7-Post Social Pack",
            description="A week of on-brand posts across LinkedIn + X + IG.",
            trigger_keywords=("social pack", "week of posts", "social calendar",
                              "7 posts", "content calendar"),
            steps=[], avg_credits=1200,
        ),
        SkillWorkflow(
            skill_id="product_hero_image",
            name="Product Hero Image",
            description="High-fidelity product shot generated from the product brief.",
            trigger_keywords=("hero image", "product photo", "landing image",
                              "ad creative", "banner image"),
            steps=[], avg_credits=350,
        ),
    ],
}


GROWTH_DISTRIBUTION = {
    "department": "Creative & Marketing",
    "studio_suffix": "Growth Office",
    "mission_template": "Acquire, activate, and expand users through data-informed, "
                        "legally compliant outreach.",
    "research_tools":   ["web_search", "search_leads", "enrich_contact",
                         "browser_open", "browser_navigate", "browser_extract",
                         "analyze_data"],
    "production_tools": ["send_cold_email", "run_campaign", "post_linkedin",
                         "schedule_post", "send_sms", "initiate_call"],
    "verify_tools":     ["analyze_data", "web_search"],
    "deliver_tools":    ["webhook_action", "send_slack", "update_task"],
    "quality_rules": [
        QualityRule("no_spam",       "Email content passes a deliverability check before send", "hard"),
        QualityRule("opted_in",      "Target is verified opted-in or B2B-lawful", "hard"),
        QualityRule("personalized",  "Every outreach references a specific prospect detail from research", "hard"),
        QualityRule("ab_test_ready", "Campaigns have at least 2 variants + measurable KPI", "soft"),
    ],
    "memory_tags": ["growth", "outreach", "campaigns"],
    "languages":   ["en", "es"],
    "skills": [
        SkillWorkflow(
            skill_id="cold_email_saas",
            name="Cold Email to SaaS Buyer",
            description="Qualify ICP → research prospect → send personalized cold email.",
            trigger_keywords=("cold email", "outbound email", "prospecting email",
                              "email a lead", "email a prospect"),
            steps=[], avg_credits=220,
        ),
        SkillWorkflow(
            skill_id="linkedin_connect_sequence",
            name="LinkedIn Connect + Follow-up",
            description="Send connect note + day-3 follow-up DM referencing prospect's posts.",
            trigger_keywords=("linkedin outreach", "connect on linkedin",
                              "linkedin dm", "social selling"),
            steps=[], avg_credits=180,
        ),
        SkillWorkflow(
            skill_id="drip_campaign_5",
            name="5-Touch Drip Campaign",
            description="Design + launch a 5-email sequence with A/B subject variants.",
            trigger_keywords=("drip campaign", "email sequence", "5 email sequence",
                              "nurture sequence", "email workflow"),
            steps=[], avg_credits=650,
        ),
    ],
}


RESEARCH_INTEL = {
    "department": "Research & Intelligence",
    "studio_suffix": "Research Desk",
    "mission_template": "Turn raw signals into decision-ready intelligence with every "
                        "claim sourced.",
    "research_tools":   ["web_search", "browser_open", "browser_navigate",
                         "browser_extract", "browser_screenshot", "search_leads",
                         "enrich_contact", "query_agent_history"],
    "production_tools": ["analyze_data", "enhance_prompt"],
    "verify_tools":     ["web_search", "analyze_data"],
    "deliver_tools":    ["send_slack", "send_email", "update_task"],
    "quality_rules": [
        QualityRule("sourced",        "Every claim cites at least one primary source", "hard"),
        QualityRule("fresh",          "Sources dated within 90 days unless historical context", "hard"),
        QualityRule("balanced",       "At least 2 opposing viewpoints considered", "hard"),
        QualityRule("quantified",     "Opinions distinguished from measured data", "hard"),
    ],
    "memory_tags": ["research", "intel", "analysis"],
    "languages":   ["en"],
    "skills": [
        SkillWorkflow(
            skill_id="competitor_teardown",
            name="Competitor Teardown",
            description="Public-source competitor analysis: pricing, positioning, "
                        "stack, funding, customers, strengths, gaps.",
            trigger_keywords=("competitor analysis", "competitor teardown",
                              "competitive analysis", "competitor research",
                              "who is competing"),
            steps=[], avg_credits=750,
        ),
        SkillWorkflow(
            skill_id="market_sizing",
            name="Market Sizing (TAM/SAM/SOM)",
            description="Bottom-up + top-down market size for a product/segment.",
            trigger_keywords=("market size", "tam sam som", "addressable market",
                              "market sizing", "how big is the market"),
            steps=[], avg_credits=900,
        ),
        SkillWorkflow(
            skill_id="industry_brief",
            name="Industry Briefing",
            description="One-page briefing on an industry: trends, regulators, "
                        "incumbents, disruptors, risks.",
            trigger_keywords=("industry brief", "industry overview",
                              "industry primer", "sector briefing"),
            steps=[], avg_credits=600,
        ),
    ],
}


ENGINEERING = {
    "department": "Product & Engineering",
    "studio_suffix": "Engineering Bay",
    "mission_template": "Ship production-grade code with tests, docs, and verifiable behavior.",
    "research_tools":   ["web_search", "github_action", "query_agent_history",
                         "analyze_data"],
    "production_tools": ["github_action", "webhook_action", "create_task"],
    "verify_tools":     ["github_action", "analyze_data"],
    "deliver_tools":    ["github_action", "send_slack", "update_task"],
    "quality_rules": [
        QualityRule("tests_included",    "Code change includes tests that cover the diff", "hard"),
        QualityRule("no_secrets",        "No API keys/secrets in commits", "hard"),
        QualityRule("matches_pattern",   "New code follows existing conventions in the repo", "hard"),
        QualityRule("pr_description",    "Change has a clear PR description with rationale", "soft"),
    ],
    "memory_tags": ["engineering", "code", "repo"],
    "languages":   ["en"],
    "skills": [
        SkillWorkflow(
            skill_id="pr_review",
            name="Pull Request Review",
            description="Review a PR: correctness, regressions, style, tests, docs.",
            trigger_keywords=("review this pr", "pr review", "review pull request",
                              "code review", "review my code"),
            steps=[], avg_credits=500,
        ),
        SkillWorkflow(
            skill_id="bug_triage",
            name="Bug Triage + Repro",
            description="Reproduce reported bug, isolate root cause, propose fix.",
            trigger_keywords=("triage this bug", "repro this bug", "investigate bug",
                              "bug fix", "error investigation"),
            steps=[], avg_credits=700,
        ),
        SkillWorkflow(
            skill_id="adr_writer",
            name="Architecture Decision Record",
            description="Capture context + options + decision + consequences.",
            trigger_keywords=("adr", "architecture decision", "design doc",
                              "architecture decision record", "technical decision"),
            steps=[], avg_credits=400,
        ),
    ],
}


SALES_REVENUE = {
    "department": "Sales & Revenue",
    "studio_suffix": "Sales Office",
    "mission_template": "Turn qualified leads into booked revenue through consultative, "
                        "research-informed outreach.",
    "research_tools":   ["web_search", "search_leads", "enrich_contact",
                         "browser_open", "browser_navigate", "browser_extract",
                         "hubspot_action", "salesforce_action"],
    "production_tools": ["send_cold_email", "send_sms", "initiate_call",
                         "post_linkedin", "hubspot_action", "salesforce_action",
                         "run_campaign"],
    "verify_tools":     ["analyze_data", "query_agent_history"],
    "deliver_tools":    ["hubspot_action", "salesforce_action", "send_slack"],
    "quality_rules": [
        QualityRule("qualified",     "Lead meets ICP (industry, size, title, region)", "hard"),
        QualityRule("personalized",  "Opening line references specific prospect fact from research", "hard"),
        QualityRule("clear_ask",     "Message ends with one specific next step", "hard"),
        QualityRule("compliance",    "Follows CAN-SPAM / GDPR / region-specific rules", "hard"),
    ],
    "memory_tags": ["sales", "outreach", "leads"],
    "languages":   ["en", "es"],
    "skills": [
        SkillWorkflow(
            skill_id="discovery_call_prep",
            name="Discovery Call Prep",
            description="Research prospect + company + stack; prep 8 discovery questions.",
            trigger_keywords=("discovery call prep", "research this prospect",
                              "prep for call", "sales call prep"),
            steps=[], avg_credits=380,
        ),
        SkillWorkflow(
            skill_id="demo_followup",
            name="Demo Follow-up Package",
            description="Post-demo recap + ROI summary + signed SOW draft.",
            trigger_keywords=("demo follow up", "demo recap", "post demo email",
                              "send recap", "recap email"),
            steps=[], avg_credits=420,
        ),
        SkillWorkflow(
            skill_id="objection_playbook",
            name="Objection Handling Playbook",
            description="Scan last 30 days of objections and draft rebuttals.",
            trigger_keywords=("objection playbook", "handle objections",
                              "sales objections", "overcome objections"),
            steps=[], avg_credits=500,
        ),
    ],
}


OPERATIONS = {
    "department": "Customer Experience & Operations",
    "studio_suffix": "Ops Center",
    "mission_template": "Execute operational tasks reliably with full audit trail and "
                        "resilience to failure.",
    "research_tools":   ["query_agent_history", "query_tasks", "analyze_data"],
    "production_tools": ["create_task", "update_task", "webhook_action",
                         "send_slack", "send_email", "schedule_post"],
    "verify_tools":     ["query_tasks", "analyze_data"],
    "deliver_tools":    ["send_slack", "send_email", "update_task"],
    "quality_rules": [
        QualityRule("idempotent",      "Operation can safely retry without duplicate effect", "hard"),
        QualityRule("logged",          "Every side-effect recorded with timestamp + actor", "hard"),
        QualityRule("reversible",      "Destructive actions have an undo path or approval", "hard"),
    ],
    "memory_tags": ["ops", "tasks", "runbooks"],
    "languages":   ["en"],
    "skills": [
        SkillWorkflow(
            skill_id="weekly_ops_digest",
            name="Weekly Ops Digest",
            description="Summarize the week's incidents + resolutions + backlog delta.",
            trigger_keywords=("weekly digest", "ops recap", "weekly report",
                              "status update", "weekly summary"),
            steps=[], avg_credits=280,
        ),
        SkillWorkflow(
            skill_id="runbook_writer",
            name="Runbook Author",
            description="Document a repeatable ops process with rollback steps.",
            trigger_keywords=("runbook", "sop document", "standard operating procedure",
                              "write a runbook", "process doc"),
            steps=[], avg_credits=350,
        ),
        SkillWorkflow(
            skill_id="vendor_onboarding",
            name="Vendor Onboarding",
            description="Provision accounts, collect tax docs, log into tracker.",
            trigger_keywords=("vendor onboarding", "onboard vendor",
                              "supplier setup", "new supplier"),
            steps=[], avg_credits=400,
        ),
    ],
}


FINANCE_CAPITAL = {
    "department": "Sales & Revenue",
    "studio_suffix": "Finance Desk",
    "mission_template": "Protect and allocate capital with numbers that tie back to raw data.",
    "research_tools":   ["query_agent_history", "analyze_data", "web_search"],
    "production_tools": ["analyze_data", "enhance_prompt"],
    "verify_tools":     ["analyze_data"],
    "deliver_tools":    ["send_email", "send_slack", "update_task"],
    "quality_rules": [
        QualityRule("reconciled",     "Numbers match the source-of-truth ledger", "hard"),
        QualityRule("assumptions",    "Every forecast states its assumptions", "hard"),
        QualityRule("regulatory",     "Output complies with relevant accounting standard", "hard"),
    ],
    "memory_tags": ["finance", "budget", "ledger"],
    "languages":   ["en"],
    "skills": [
        SkillWorkflow(
            skill_id="monthly_burn_review",
            name="Monthly Burn Review",
            description="Reconcile spend by category + runway projection + flags.",
            trigger_keywords=("burn review", "monthly burn", "cash runway",
                              "burn rate", "monthly financial review"),
            steps=[], avg_credits=500,
        ),
        SkillWorkflow(
            skill_id="pricing_model_build",
            name="Pricing Model Build",
            description="Build a unit-economics model for a new SKU/plan.",
            trigger_keywords=("pricing model", "unit economics", "build a pricing",
                              "price this sku", "pricing analysis"),
            steps=[], avg_credits=700,
        ),
        SkillWorkflow(
            skill_id="investor_update",
            name="Investor Update",
            description="Monthly investor email: KPIs, wins, asks, runway.",
            trigger_keywords=("investor update", "investor email",
                              "monthly investor", "board update"),
            steps=[], avg_credits=450,
        ),
    ],
}


CUSTOMER_EXPERIENCE = {
    "department": "Customer Experience & Operations",
    "studio_suffix": "Support Studio",
    "mission_template": "Solve customer problems on first contact with tone that leaves "
                        "them feeling heard.",
    "research_tools":   ["query_agent_history", "web_search", "analyze_data"],
    "production_tools": ["send_email", "send_slack", "send_sms", "create_task",
                         "webhook_action"],
    "verify_tools":     ["analyze_data"],
    "deliver_tools":    ["send_email", "send_slack", "update_task"],
    "quality_rules": [
        QualityRule("empathetic",      "Response acknowledges the customer's frustration", "hard"),
        QualityRule("accurate",        "Any fact stated matches product docs", "hard"),
        QualityRule("actionable",      "Response tells the customer exactly what to do next", "hard"),
        QualityRule("escalation_ready","Complex issues escalated to human with full context", "hard"),
    ],
    "memory_tags": ["support", "customer", "tickets"],
    "languages":   ["en", "es", "fr", "de", "pt", "ja", "zh", "ar", "hi"],
    "skills": [
        SkillWorkflow(
            skill_id="ticket_resolve_first_contact",
            name="First-Contact Ticket Resolution",
            description="Acknowledge, diagnose from product docs, resolve in one reply.",
            trigger_keywords=("resolve ticket", "handle this ticket",
                              "customer ticket", "respond to ticket"),
            steps=[], avg_credits=180,
        ),
        SkillWorkflow(
            skill_id="refund_request_triage",
            name="Refund Request Triage",
            description="Evaluate against refund policy; either process or escalate.",
            trigger_keywords=("refund request", "refund this", "money back",
                              "process refund", "return request"),
            steps=[], avg_credits=200,
        ),
        SkillWorkflow(
            skill_id="churn_save_outreach",
            name="Churn-Save Outreach",
            description="Reach out to at-risk customer with personalized save offer.",
            trigger_keywords=("churn save", "retention outreach", "at risk customer",
                              "cancellation save", "win back"),
            steps=[], avg_credits=320,
        ),
    ],
}


LEGAL_COMPLIANCE = {
    "department": "Strategy & Governance",
    "studio_suffix": "Legal Desk",
    "mission_template": "Review, redline, and advise — always with sources and jurisdiction "
                        "flagged; never practice law without a human attorney on record.",
    "research_tools":   ["web_search", "browser_open", "browser_navigate",
                         "browser_extract", "query_agent_history"],
    "production_tools": ["analyze_data", "enhance_prompt", "send_email"],
    "verify_tools":     ["web_search"],
    "deliver_tools":    ["send_email", "send_slack", "update_task"],
    "quality_rules": [
        QualityRule("jurisdiction",      "Output states which jurisdiction the advice assumes", "hard"),
        QualityRule("cited",             "Every legal claim cites a statute, case, or contract clause", "hard"),
        QualityRule("human_review_flag", "High-stakes output flagged for human attorney sign-off", "hard"),
    ],
    "memory_tags": ["legal", "compliance", "contracts"],
    "languages":   ["en"],
    "skills": [
        SkillWorkflow(
            skill_id="nda_redline",
            name="NDA Redline",
            description="Redline a mutual/one-way NDA against standard terms.",
            trigger_keywords=("nda redline", "review nda", "redline this nda",
                              "nda review", "confidentiality agreement"),
            steps=[], avg_credits=400,
        ),
        SkillWorkflow(
            skill_id="privacy_policy_draft",
            name="Privacy Policy Draft",
            description="Draft a jurisdiction-aware privacy policy for a product.",
            trigger_keywords=("privacy policy", "data policy", "gdpr policy",
                              "write privacy policy"),
            steps=[], avg_credits=550,
        ),
        SkillWorkflow(
            skill_id="tos_review",
            name="Terms of Service Review",
            description="Review vendor ToS for indemnification, termination, liability.",
            trigger_keywords=("review tos", "terms of service review",
                              "review terms", "contract review"),
            steps=[], avg_credits=500,
        ),
    ],
}


PLATFORM_INFRA = {
    "department": "Platform & Infrastructure",
    "studio_suffix": "Control Room",
    "mission_template": "Keep the system observable, fast, and within cost ceilings.",
    "research_tools":   ["analyze_data", "query_agent_history", "query_tasks"],
    "production_tools": ["webhook_action", "create_task", "update_task"],
    "verify_tools":     ["analyze_data"],
    "deliver_tools":    ["send_slack", "update_task"],
    "quality_rules": [
        QualityRule("change_logged",  "Every config change logged with rollback plan", "hard"),
        QualityRule("slo_preserved",  "Change doesn't degrade agreed SLO", "hard"),
    ],
    "memory_tags": ["infra", "ops", "kernel"],
    "languages":   ["en"],
    "skills": [
        SkillWorkflow(
            skill_id="incident_postmortem",
            name="Incident Postmortem",
            description="Reconstruct incident timeline + root cause + action items.",
            trigger_keywords=("postmortem", "post mortem", "incident review",
                              "rca", "root cause analysis"),
            steps=[], avg_credits=500,
        ),
        SkillWorkflow(
            skill_id="cost_audit_week",
            name="Weekly Cost Audit",
            description="Flag spend anomalies across providers + propose trims.",
            trigger_keywords=("cost audit", "spend audit", "weekly cost review",
                              "cost trim", "spend review"),
            steps=[], avg_credits=380,
        ),
        SkillWorkflow(
            skill_id="slo_health_report",
            name="SLO Health Report",
            description="Tally SLO compliance + error-budget burn + remediation.",
            trigger_keywords=("slo report", "error budget", "slo health",
                              "slo compliance", "reliability report"),
            steps=[], avg_credits=300,
        ),
    ],
}


# ── Network → Template map ───────────────────────────────────────────

TEMPLATES_BY_NETWORK: dict[str, dict] = {
    # Creative / Marketing
    "10F":                   CREATIVE_BRAND,       # Creative & Brand
    "creative_brand":        CREATIVE_BRAND,
    "10G":                   GROWTH_DISTRIBUTION,
    "growth_distribution":   GROWTH_DISTRIBUTION,
    "10Z":                   RESEARCH_INTEL,       # Live Web Search — research-first
    "web_search_intelligence": RESEARCH_INTEL,
    # Research
    "10M":                   RESEARCH_INTEL,
    "research_intelligence": RESEARCH_INTEL,
    "10N":                   RESEARCH_INTEL,       # Simulation — research-heavy
    # Engineering
    "10D":                   ENGINEERING,
    "product_development":   ENGINEERING,
    "10E":                   ENGINEERING,
    "engineering":           ENGINEERING,
    # Sales / Revenue
    "10H":                   SALES_REVENUE,
    "sales_revenue":         SALES_REVENUE,
    # Ops
    "10J":                   OPERATIONS,
    "operations":            OPERATIONS,
    "10S":                   OPERATIONS,           # Execution
    # Finance
    "10K":                   FINANCE_CAPITAL,
    "finance_capital":       FINANCE_CAPITAL,
    "10L":                   FINANCE_CAPITAL,      # Investment
    # Customer experience
    "10I":                   CUSTOMER_EXPERIENCE,
    "customer_experience":   CUSTOMER_EXPERIENCE,
    # Legal / Governance
    "10O":                   LEGAL_COMPLIANCE,
    "legal_governance":      LEGAL_COMPLIANCE,
    "10P":                   LEGAL_COMPLIANCE,     # Security maps similarly (audit-first)
    "10V":                   LEGAL_COMPLIANCE,     # Conflict resolution
    # Platform / Infra
    "10A":                   PLATFORM_INFRA,
    "core_platform":         PLATFORM_INFRA,
    "10Q":                   PLATFORM_INFRA,       # Memory & Knowledge
    "10R":                   PLATFORM_INFRA,       # Tooling
    "10W":                   PLATFORM_INFRA,       # Observability
    "10T":                   PLATFORM_INFRA,       # Verification
    "10X":                   PLATFORM_INFRA,       # Recovery
    # Strategic / Core Leadership — use research template (they reason a lot)
    "10B":                   RESEARCH_INTEL,
    "10C":                   RESEARCH_INTEL,       # Venture Creation
    "10U":                   RESEARCH_INTEL,       # Experimentation
    "10Y":                   CREATIVE_BRAND,       # Communications & Reporting
    "10AA":                  RESEARCH_INTEL,       # Industry-specific — domain research
    "10AB":                  CREATIVE_BRAND,       # Core Team (mixed; default creative)
    "core_team":             CREATIVE_BRAND,
}

DEFAULT_TEMPLATE = PLATFORM_INFRA


def template_for_network(network: str | None) -> dict:
    """Pick a department template for an agent's network code/name."""
    if not network:
        return DEFAULT_TEMPLATE
    return TEMPLATES_BY_NETWORK.get(str(network).lower(), TEMPLATES_BY_NETWORK.get(network, DEFAULT_TEMPLATE))


def materialize_office(agent_row: dict, template: dict | None = None) -> AgentOffice:
    """Build a fully-populated AgentOffice from an agent row + department template."""
    tpl = template or template_for_network(agent_row.get("network"))
    agent_name = agent_row.get("name") or agent_row.get("agent_id", "Unnamed Agent")
    studio = f"{agent_name} {tpl['studio_suffix']}"
    sop = _base_sop(
        research_tools=tpl["research_tools"],
        production_tools=tpl["production_tools"],
        verify_tools=tpl.get("verify_tools"),
        deliver_tools=tpl.get("deliver_tools"),
    )
    return AgentOffice(
        agent_id=agent_row["agent_id"],
        agent_name=agent_name,
        network=agent_row.get("network", ""),
        department=tpl["department"],
        studio_name=studio,
        mission=tpl["mission_template"],
        sop=sop,
        studio_tools=list(set(tpl["research_tools"] + tpl["production_tools"])),
        skills_library=list(tpl.get("skills") or []),
        quality_rules=list(tpl["quality_rules"]),
        reference_memory_tags=list(tpl["memory_tags"]),
        monthly_budget_credits=agent_row.get("monthly_budget_credits") or 1000,
        languages_supported=list(tpl.get("languages") or ["en"]),
    )
