---
name: nonprofit-ai
description: AI nonprofit skills — grant writing, donor communications, impact reporting, volunteer management, fundraising campaigns, program evaluation for MAARS nonprofit agents
---

# Nonprofit AI — MAARS Reference

## Grant Writing
```python
GRANT_PROPOSAL_PROMPT = """
Write a grant proposal for: {organization}
Grant: {grant_name} from {funder}
Amount requested: ${amount}
Project: {project_name}
Deadline: {deadline}

Funder priorities: {funder_priorities}
Review criteria: {evaluation_criteria}
Page limit: {page_limit}
Required sections: {required_sections}

Write:
1. EXECUTIVE SUMMARY (1 page): Problem, solution, ask, organization
2. STATEMENT OF NEED:
   - Data-backed problem statement
   - Geographic/demographic specificity
   - Why now? Urgency rationale
   - Gap this project fills
   
3. PROJECT DESCRIPTION:
   - Theory of change (inputs → activities → outputs → outcomes → impact)
   - Target population (specific, not broad)
   - Program activities (what, when, who, where)
   - Evidence base: What research supports this approach
   
4. EVALUATION PLAN:
   - Process metrics (what we'll do)
   - Outcome metrics (what will change)
   - Data collection methods
   - Learning and adaptation process
   
5. ORGANIZATIONAL CAPACITY:
   - Relevant experience and track record
   - Key staff qualifications
   - Partnerships and community relationships
   
6. BUDGET NARRATIVE:
   - Justification for each line item
   - Other funding sources (shows leverage)
   - Sustainability after grant period

Tone: {tone} (formal foundation/government/corporate/community)
"""
```

## Donor Communication
```python
DONOR_COMM_TEMPLATES = {
    "major_gift_ask": """
Dear {donor_name},

Your {years_giving}-year partnership with {org_name} has changed lives.
[Specific story about impact of previous gift]

Today, I'm reaching out because we have an extraordinary opportunity:
{opportunity_description}

With your leadership gift of ${ask_amount}, we can {specific_outcome}.
[Concrete example of what that amount enables]

{peer_validation — "Other leaders like you are making gifts of..."}

I'd love to discuss this further. Could we schedule a call this week?

With deep gratitude,
{executive_name}
""",
    "annual_fund_appeal": """
Subject: {subject_line_with_urgency}

{donor_name},

{opening_story — 2 sentences about one person we helped}

Because of supporters like you, {org_name} was able to {annual_achievement}.

This year, we're working toward {specific_goal}. We need {number} donors
to give ${amount} to make it happen.

Will you make your gift today?
[GIVE NOW BUTTON]

Every dollar {specific_impact_statement}.

Thank you,
{name}

P.S. {urgency_or_matching_gift_note}
""",
    "thank_you": """
Dear {donor_name},

Thank you for your generous gift of ${amount} to {org_name}.

Your gift is already at work: {immediate_impact_statement}.

Because of you, {beneficiary_example}. That's the power of your generosity.

We'll send your tax receipt within 24 hours. Your gift is fully 
tax-deductible as allowed by law.

With gratitude,
{org_name} Team

Tax ID: {ein}
""",
}
```

## Impact Reporting
```python
IMPACT_REPORT_PROMPT = """
Create an impact report for: {org_name}
Period: {period}
Audience: {audience} (donors/funders/board/public)
Format: {format} (annual report/program report/grant report)

Data provided:
{program_data}

Structure:
1. YEAR IN NUMBERS: Key stats visualized as infographics
   - People served, programs run, outcomes achieved

2. THEORY OF CHANGE VALIDATION:
   - Inputs used → Activities conducted → Outputs delivered →
     Outcomes achieved → Long-term impact evidence

3. STORIES OF CHANGE:
   - 2-3 compelling individual stories (anonymized if needed)
   - Before/after narrative
   - Voice of the community member, not just the org

4. PROGRAM HIGHLIGHTS:
   - What worked and why
   - What we learned and changed
   - Challenges faced honestly

5. FINANCIAL SUMMARY:
   - Revenue by source
   - Program vs. admin/fundraising ratio
   - Efficiency metrics (cost per outcome)

6. LOOKING AHEAD:
   - Next year priorities
   - Funding needs
   - Strategic direction

Design notes: {design_direction} — include photo placements
"""

def calculate_nonprofit_efficiency(data: dict) -> dict:
    """Calculate key nonprofit financial ratios"""
    total_revenue = data["total_revenue"]
    program_expenses = data["program_expenses"]
    admin_expenses = data["admin_expenses"]
    fundraising_expenses = data["fundraising_expenses"]
    total_expenses = program_expenses + admin_expenses + fundraising_expenses
    
    return {
        "program_expense_ratio": program_expenses / total_expenses,
        "admin_ratio": admin_expenses / total_expenses,
        "fundraising_efficiency": (total_revenue - fundraising_expenses) / fundraising_expenses,
        "cost_per_outcome": total_expenses / data.get("outcomes_achieved", 1),
        "charity_navigator_estimate": "A" if program_expenses/total_expenses > 0.75 else "B",
        "guidestar_seal_eligible": program_expenses/total_expenses > 0.65,
    }
```

## Fundraising Campaign Planning
```python
CAMPAIGN_PLANNING_PROMPT = """
Plan a fundraising campaign for: {org_name}
Campaign type: {type} (year-end/GivingTuesday/capital/emergency/anniversary)
Goal: ${goal}
Timeline: {timeline}
Current donor base: {donor_count} donors
Previous best campaign: ${previous_best}

Plan:
1. GOAL BREAKDOWN:
   - Major gifts ($10K+): {major_count} at ${avg_major} = ${total}
   - Mid-level ($1K-10K): {mid_count} at ${avg_mid} = ${total}
   - Annual fund (<$1K): {count} at avg ${avg} = ${total}

2. TIMELINE:
   - Cultivation phase: [Build donor relationships]
   - Soft launch (board/major donors): [1-2 weeks before public]
   - Public launch: [Announcement with momentum from soft launch]
   - Mid-campaign push: [Content, updates, urgency]
   - End sprint: [Final 48-hour surge]

3. MATCHING GIFT STRATEGY:
   - Recruit matching donor(s) for amplification
   - Use match to create urgency

4. CONTENT CALENDAR:
   - Email sequence (frequency + subject lines)
   - Social media plan
   - Major donor outreach cadence

5. CHANNELS:
   - Email (primary) → Open rate target: {open_rate}%
   - Social media → Platforms + posting schedule
   - Direct mail → Segment and timing
   - Events → Cultivation events

6. SUCCESS METRICS:
   - Donors acquired (new vs. renewed)
   - Average gift size
   - Retention rate vs. last campaign
   - Cost to raise a dollar (target: <$0.20)
"""
```

## Volunteer Management
```python
VOLUNTEER_MANAGEMENT_PROMPT = """
Design volunteer program for: {org_name}
Volunteer roles needed: {roles}
Current volunteer count: {current_vol}
Target volunteer hours/month: {target_hours}

Program design:
1. ROLE DESCRIPTIONS:
   For each role:
   - Title and summary (excitement-first)
   - Time commitment (hours/week, minimum duration)
   - Location (in-person/remote/hybrid)
   - Skills required vs. preferred
   - Training provided
   - Impact of the role

2. RECRUITMENT STRATEGY:
   - Target profiles for each role
   - Recruitment channels (volunteer match sites, corporate partners, schools)
   - Application process (simple ≠ less committed)

3. ONBOARDING:
   - Welcome sequence (before first day)
   - Orientation (in-person + async options)
   - Buddy/mentor matching
   - 30-day check-in

4. RETENTION & RECOGNITION:
   - Milestones to celebrate
   - Recognition program
   - Leadership pathway
   - Annual volunteer appreciation

5. MANAGEMENT TOOLS:
   - Volunteer management system (VolunteerHub, InitLive, Salesforce)
   - Hour tracking
   - Communication platform
   - Feedback/survey cadence
"""
```

## Program Evaluation
```python
EVALUATION_FRAMEWORK_PROMPT = """
Design program evaluation for: {program_name}
Program theory: {theory_of_change}
Target outcomes: {outcomes}
Stakeholders: {stakeholders}
Budget for evaluation: ${eval_budget}
Timeframe: {timeframe}

Evaluation design:
1. EVALUATION QUESTIONS:
   - Implementation: Is the program being delivered as intended?
   - Outcomes: Are participants experiencing targeted changes?
   - Attribution: Are changes due to the program?

2. INDICATORS:
   For each outcome:
   - Indicator: Measurable proxy
   - Data source: Where to find it
   - Baseline: Starting point
   - Target: Expected change

3. DATA COLLECTION:
   - Surveys (tool: SurveyMonkey/Typeform/Google)
   - Interviews/focus groups
   - Administrative data (existing records)
   - Observation protocols

4. ANALYSIS PLAN:
   - Quantitative: Statistical tests, comparison groups
   - Qualitative: Thematic analysis, narrative coding

5. REPORTING:
   - Internal learning: Quarterly program team reviews
   - Funder reports: Per grant requirements
   - Public sharing: Annual impact report

6. UTILIZATION:
   - How findings will inform program decisions
   - Who will see results and act on them

EVALUATION BUDGET ALLOCATION: Staff time, tools, external evaluator
"""
```

## Models to Use
- **Grant writing**: `claude-opus-4-6` (best at persuasive long-form writing)
- **Impact stories**: `claude-sonnet-4-6` (emotional, authentic narrative)
- **Donor communications**: `claude-sonnet-4-6` (warm, relationship-focused)
- **Financial analysis**: `gpt-4o` with code tools (ratios, projections)
- **Program evaluation**: `claude-opus-4-6` (research design, methodology)
- **Funder research**: `perplexity/sonar-pro` (current grant opportunities)
- **Multilingual communications**: `gpt-4o` (global organizations)
