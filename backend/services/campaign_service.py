"""Campaign Service — Campaign builder, templates, PDF, and scheduling."""
from datetime import datetime, timezone
from bson import ObjectId
from db import db


CAMPAIGN_TEMPLATES = [
    {
        "template_id": "content_marketing",
        "name": "Content Marketing Campaign",
        "description": "Full content pipeline from research to distribution",
        "category": "Marketing",
        "color": "#ec4899",
        "steps": [
            {"order": 1, "title": "Market Research", "agent_role": "Research Analyst", "agent_network": "research_intelligence", "default_task": "Research current market trends, audience demographics, and competitor content strategies. Provide a structured brief."},
            {"order": 2, "title": "Content Strategy", "agent_role": "Content Strategist", "agent_network": "creative_brand", "default_task": "Based on the research brief, create a content strategy with topics, formats, channels, and a publishing schedule."},
            {"order": 3, "title": "Content Creation", "agent_role": "Content Creator", "agent_network": "creative_brand", "default_task": "Write the primary content piece following the strategy. Include headlines, body, and calls to action."},
            {"order": 4, "title": "SEO Optimization", "agent_role": "SEO Specialist", "agent_network": "growth_distribution", "default_task": "Optimize the content for search engines. Suggest meta tags, keywords, and structural improvements."},
            {"order": 5, "title": "Distribution Plan", "agent_role": "Growth Marketer", "agent_network": "growth_distribution", "default_task": "Create a multi-channel distribution plan with scheduling, platform-specific adaptations, and tracking metrics."},
        ],
    },
    {
        "template_id": "product_launch",
        "name": "Product Launch",
        "description": "End-to-end product launch coordination",
        "category": "Product",
        "color": "#3b82f6",
        "steps": [
            {"order": 1, "title": "Market Analysis", "agent_role": "Market Analyst", "agent_network": "research_intelligence", "default_task": "Analyze target market size, competitive landscape, and positioning opportunities for the product launch."},
            {"order": 2, "title": "Pricing Strategy", "agent_role": "Financial Analyst", "agent_network": "finance_capital", "default_task": "Recommend pricing tiers based on market analysis, cost structure, and competitive positioning."},
            {"order": 3, "title": "Launch Messaging", "agent_role": "Brand Strategist", "agent_network": "creative_brand", "default_task": "Craft launch messaging, value propositions, and key talking points for different audience segments."},
            {"order": 4, "title": "Go-to-Market Plan", "agent_role": "Growth Lead", "agent_network": "growth_distribution", "default_task": "Build a detailed go-to-market plan with timeline, channels, budget allocation, and success metrics."},
            {"order": 5, "title": "Sales Enablement", "agent_role": "Sales Strategist", "agent_network": "sales_revenue", "default_task": "Create sales collateral, objection handling guides, and demo scripts for the sales team."},
        ],
    },
    {
        "template_id": "customer_onboarding",
        "name": "Customer Onboarding",
        "description": "Automated customer onboarding workflow",
        "category": "Customer Success",
        "color": "#14b8a6",
        "steps": [
            {"order": 1, "title": "Welcome Setup", "agent_role": "Onboarding Specialist", "agent_network": "customer_experience", "default_task": "Create a personalized welcome sequence with account setup instructions and key resources."},
            {"order": 2, "title": "Needs Assessment", "agent_role": "Customer Analyst", "agent_network": "customer_experience", "default_task": "Analyze the customer profile and create a needs assessment with recommended features and configurations."},
            {"order": 3, "title": "Training Plan", "agent_role": "Training Coordinator", "agent_network": "operations", "default_task": "Design a training curriculum tailored to the customer's needs, with milestones and deliverables."},
            {"order": 4, "title": "Success Metrics", "agent_role": "Success Manager", "agent_network": "customer_experience", "default_task": "Define success metrics, health score thresholds, and escalation triggers for this customer."},
        ],
    },
    {
        "template_id": "sales_outreach",
        "name": "Sales Outreach Campaign",
        "description": "Multi-touch sales prospecting pipeline",
        "category": "Sales",
        "color": "#f97316",
        "steps": [
            {"order": 1, "title": "Lead Research", "agent_role": "Lead Researcher", "agent_network": "research_intelligence", "default_task": "Research the target company: decision makers, pain points, recent news, and technology stack."},
            {"order": 2, "title": "Outreach Copy", "agent_role": "Sales Copywriter", "agent_network": "creative_brand", "default_task": "Write personalized outreach emails (cold, follow-up, break-up) based on the research findings."},
            {"order": 3, "title": "Objection Prep", "agent_role": "Sales Strategist", "agent_network": "sales_revenue", "default_task": "Anticipate objections and prepare response frameworks with supporting evidence and case studies."},
            {"order": 4, "title": "Follow-up Sequence", "agent_role": "Campaign Manager", "agent_network": "growth_distribution", "default_task": "Design a multi-channel follow-up sequence with timing, channels, and escalation paths."},
        ],
    },
    {
        "template_id": "security_audit",
        "name": "Security Audit",
        "description": "Comprehensive security review workflow",
        "category": "Engineering",
        "color": "#ef4444",
        "steps": [
            {"order": 1, "title": "Threat Assessment", "agent_role": "Security Analyst", "agent_network": "security", "default_task": "Identify potential threat vectors, vulnerability categories, and risk levels for the target system."},
            {"order": 2, "title": "Code Review", "agent_role": "Security Engineer", "agent_network": "engineering", "default_task": "Review code patterns for common vulnerabilities: injection, XSS, auth bypass, data exposure."},
            {"order": 3, "title": "Compliance Check", "agent_role": "Compliance Officer", "agent_network": "legal_governance", "default_task": "Verify compliance with relevant standards (SOC2, GDPR, HIPAA) and identify gaps."},
            {"order": 4, "title": "Remediation Plan", "agent_role": "Security Lead", "agent_network": "security", "default_task": "Create a prioritized remediation plan with severity ratings, fix recommendations, and implementation timeline."},
        ],
    },
    {
        "template_id": "data_analysis",
        "name": "Data Analysis Pipeline",
        "description": "End-to-end data analysis workflow",
        "category": "Analytics",
        "color": "#8b5cf6",
        "steps": [
            {"order": 1, "title": "Data Assessment", "agent_role": "Data Analyst", "agent_network": "research_intelligence", "default_task": "Assess available data sources, quality metrics, and identify key variables for analysis."},
            {"order": 2, "title": "Statistical Analysis", "agent_role": "Statistician", "agent_network": "research_intelligence", "default_task": "Perform statistical analysis on the dataset. Identify correlations, trends, and anomalies."},
            {"order": 3, "title": "Insight Generation", "agent_role": "Business Analyst", "agent_network": "strategic_executive", "default_task": "Translate statistical findings into business insights with actionable recommendations."},
            {"order": 4, "title": "Executive Summary", "agent_role": "Executive Advisor", "agent_network": "strategic_executive", "default_task": "Create a concise executive summary with key findings, strategic implications, and recommended next steps."},
        ],
    },
]


async def get_campaign_templates():
    return CAMPAIGN_TEMPLATES


async def get_campaigns(user_id):
    results = []
    async for c in db.campaigns.find({"user_id": user_id}, {"_id": 0}).sort("created_at", -1):
        results.append(c)
    return results


async def get_campaign(user_id, campaign_id):
    return await db.campaigns.find_one({"user_id": user_id, "campaign_id": campaign_id}, {"_id": 0})


async def create_campaign(user_id, data):
    now = datetime.now(timezone.utc).isoformat()
    template_id = data.get("template_id")
    template = next((t for t in CAMPAIGN_TEMPLATES if t["template_id"] == template_id), None)

    steps = data.get("steps", [])
    if template and not steps:
        steps = []
        for s in template["steps"]:
            agent = await db.agents.find_one(
                {"network": s["agent_network"]},
                {"_id": 0, "agent_id": 1, "name": 1, "role": 1, "avatar": 1, "network": 1}
            )
            steps.append({
                "order": s["order"],
                "title": s["title"],
                "task": data.get("context", "") + "\n\n" + s["default_task"] if data.get("context") else s["default_task"],
                "agent_id": agent["agent_id"] if agent else None,
                "agent_name": agent["name"] if agent else s["agent_role"],
                "agent_role": s["agent_role"],
                "agent_network": s["agent_network"],
                "agent_avatar": agent.get("avatar") if agent else None,
                "status": "pending",
                "output": None,
            })

    campaign = {
        "campaign_id": f"camp_{ObjectId()}",
        "user_id": user_id,
        "template_id": template_id,
        "name": data.get("name") or (template["name"] if template else "Custom Campaign"),
        "description": data.get("description") or (template["description"] if template else ""),
        "category": data.get("category") or (template["category"] if template else "Custom"),
        "color": data.get("color") or (template["color"] if template else "#6366f1"),
        "context": data.get("context", ""),
        "steps": steps,
        "status": "draft",
        "created_at": now,
        "updated_at": now,
    }
    await db.campaigns.insert_one(campaign)
    campaign.pop("_id", None)
    return campaign


async def update_campaign(user_id, campaign_id, data):
    now = datetime.now(timezone.utc).isoformat()
    update = {"$set": {"updated_at": now}}
    for field in ["name", "description", "steps", "context", "status"]:
        if field in data:
            update["$set"][field] = data[field]
    await db.campaigns.update_one({"user_id": user_id, "campaign_id": campaign_id}, update)
    return await get_campaign(user_id, campaign_id)


async def delete_campaign(user_id, campaign_id):
    await db.campaigns.delete_one({"user_id": user_id, "campaign_id": campaign_id})
    return True


async def execute_campaign(user_id, campaign_id):
    """Execute a campaign step-by-step with real LLM calls."""
    from services.llm_service import call_llm_with_fallback

    campaign = await get_campaign(user_id, campaign_id)
    if not campaign:
        return None

    await db.campaigns.update_one(
        {"campaign_id": campaign_id},
        {"$set": {"status": "running", "updated_at": datetime.now(timezone.utc).isoformat()}}
    )

    user = await db.users.find_one({"user_id": user_id}, {"_id": 0})
    api_keys = user.get("api_keys", {}) if user else {}

    accumulated_context = f"Campaign: {campaign['name']}\nContext: {campaign.get('context', '')}\n\n"

    for i, step in enumerate(campaign.get("steps", [])):
        try:
            agent = None
            if step.get("agent_id"):
                agent = await db.agents.find_one(
                    {"agent_id": step["agent_id"]},
                    {"_id": 0, "system_prompt": 1, "model_provider": 1, "model_name": 1, "name": 1, "role": 1}
                )

            system_prompt = (agent.get("system_prompt") if agent else
                           f"You are a {step.get('agent_role', 'AI assistant')}. Complete the assigned task professionally.")
            provider = agent.get("model_provider", "openai") if agent else "openai"
            model = agent.get("model_name", "gpt-4o-mini") if agent else "gpt-4o-mini"

            task_prompt = f"{accumulated_context}STEP {i+1}: {step.get('title', 'Task')}\n\nTask: {step.get('task', 'Complete this step.')}"

            response_text, used_provider, used_model = await call_llm_with_fallback(
                api_keys, provider, model,
                system_prompt, task_prompt, [], None,
                temperature=0.7, max_tokens=1024
            )

            accumulated_context += f"\n--- Step {i+1} Output ({step.get('title', '')}) ---\n{response_text}\n"

            await db.campaigns.update_one(
                {"campaign_id": campaign_id, f"steps.{i}.order": step["order"]},
                {"$set": {
                    f"steps.{i}.status": "completed",
                    f"steps.{i}.output": response_text,
                    f"steps.{i}.model_used": f"{used_provider}/{used_model}",
                    f"steps.{i}.completed_at": datetime.now(timezone.utc).isoformat(),
                }}
            )
        except Exception as e:
            await db.campaigns.update_one(
                {"campaign_id": campaign_id},
                {"$set": {
                    f"steps.{i}.status": "failed",
                    f"steps.{i}.output": f"Error: {str(e)}",
                    "status": "failed",
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                }}
            )
            return await get_campaign(user_id, campaign_id)

    await db.campaigns.update_one(
        {"campaign_id": campaign_id},
        {"$set": {"status": "completed", "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    return await get_campaign(user_id, campaign_id)


async def generate_campaign_pdf(user_id, campaign_id):
    """Generate a PDF report for a completed campaign with full Unicode support."""
    from fpdf import FPDF
    import os, tempfile
    from pathlib import Path

    campaign = await get_campaign(user_id, campaign_id)
    if not campaign:
        return None

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=20)

    font_dir = Path(__file__).parent.parent
    dejavu_regular = font_dir / "DejaVuSans.ttf"
    dejavu_bold = font_dir / "DejaVuSans-Bold.ttf"
    if dejavu_regular.exists():
        pdf.add_font("DejaVu", "", str(dejavu_regular))
    if dejavu_bold.exists():
        pdf.add_font("DejaVu", "B", str(dejavu_bold))
    font_name = "DejaVu" if dejavu_regular.exists() else "Helvetica"

    pdf.add_page()
    pdf.set_font(font_name, "B", 22)
    pdf.set_text_color(99, 102, 241)
    pdf.cell(0, 14, "MAARS \u221e", ln=True, align="C")
    pdf.set_font(font_name, "", 10)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 6, "Autonomous Multi-Agent Campaign Report", ln=True, align="C")
    pdf.ln(8)

    pdf.set_draw_color(60, 60, 60)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(4)
    pdf.set_font(font_name, "B", 14)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(0, 10, str(campaign.get("name") or "Campaign Report"), ln=True)
    pdf.set_font(font_name, "", 9)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 5, f"Category: {campaign.get('category') or 'N/A'}  |  Status: {(campaign.get('status') or 'N/A').upper()}  |  Steps: {len(campaign.get('steps', []))}", ln=True)
    if campaign.get("context"):
        pdf.ln(3)
        pdf.set_font(font_name, "", 9)
        pdf.multi_cell(0, 5, f"Context: {campaign['context']}")
    pdf.ln(6)

    for i, step in enumerate(campaign.get("steps", [])):
        pdf.set_font(font_name, "B", 11)
        pdf.set_text_color(30, 30, 30)
        status_label = (step.get("status") or "pending").upper()
        pdf.cell(0, 8, f"Step {i+1}: {step.get('title') or 'Untitled'}  [{status_label}]", ln=True)
        pdf.set_font(font_name, "", 8)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 5, f"Agent: {step.get('agent_name') or 'N/A'}  |  Role: {step.get('agent_role') or 'N/A'}", ln=True)
        if step.get("task"):
            pdf.set_font(font_name, "", 8)
            pdf.set_text_color(80, 80, 80)
            pdf.multi_cell(0, 4, f"Task: {step['task'][:300]}")
        if step.get("output"):
            pdf.ln(2)
            pdf.set_font(font_name, "", 9)
            pdf.set_text_color(30, 30, 30)
            pdf.multi_cell(0, 4.5, step["output"][:2000])
        pdf.ln(4)
        pdf.set_draw_color(200, 200, 200)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(3)

    pdf.ln(4)
    pdf.set_font(font_name, "", 7)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 5, f"Generated by MAARS \u221e  |  {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}", ln=True, align="C")

    fd, path = tempfile.mkstemp(suffix=".pdf")
    os.close(fd)
    pdf.output(path)
    return path


async def schedule_campaign(user_id, campaign_id, schedule_data):
    """Set a schedule for auto-executing a campaign."""
    now = datetime.now(timezone.utc).isoformat()
    schedule = {
        "frequency": schedule_data.get("frequency", "weekly"),
        "day_of_week": schedule_data.get("day_of_week"),
        "day_of_month": schedule_data.get("day_of_month"),
        "hour": schedule_data.get("hour", 9),
        "minute": schedule_data.get("minute", 0),
        "enabled": schedule_data.get("enabled", True),
        "next_run": schedule_data.get("next_run"),
        "last_run": None,
        "run_count": 0,
        "updated_at": now,
    }
    await db.campaigns.update_one(
        {"user_id": user_id, "campaign_id": campaign_id},
        {"$set": {"schedule": schedule}}
    )
    return await get_campaign(user_id, campaign_id)


async def get_scheduled_campaigns(user_id):
    """Get all campaigns with active schedules."""
    results = []
    async for c in db.campaigns.find(
        {"user_id": user_id, "schedule.enabled": True}, {"_id": 0}
    ).sort("created_at", -1):
        results.append(c)
    return results


async def remove_schedule(user_id, campaign_id):
    """Remove schedule from a campaign."""
    await db.campaigns.update_one(
        {"user_id": user_id, "campaign_id": campaign_id},
        {"$unset": {"schedule": ""}}
    )
    return await get_campaign(user_id, campaign_id)
