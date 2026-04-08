---
name: sales-ai
description: AI sales skills — outbound prospecting, cold email sequences, objection handling, proposal writing, CRM workflows, deal closing for MAARS sales agents
---

# Sales AI — MAARS Reference

## Outbound Prospecting Framework
```python
PROSPECTING_PROMPT = """
You are Marcus Drake, MAARS Sales Representative.

Research this prospect and create a personalized outreach:
- Company: {company}
- Contact: {name}, {title}
- Recent news/triggers: {triggers}
- Our solution: {product}
- Best fit reason: {icp_match}

Create:
1. LinkedIn connection note (300 chars)
2. Cold email (subject + 5-line body)
3. Follow-up sequence (Day 3, Day 7, Day 14)
4. Key talking points for first call

Tone: Consultative, not salesy. Lead with value, not pitch.
"""
```

## Cold Email Formula
```
SUBJECT: [Personalization] + [Curiosity/Benefit] — 6 words max
(Examples: "Re: {company}'s Q4 expansion" / "{Name}, quick thought on {pain}")

LINE 1: Personalized hook (specific to them, not generic)
LINE 2: Problem you help solve (from their perspective)
LINE 3: One-line proof (customer name + result)
LINE 4: Soft CTA (question, not "schedule a call")
SIGN-OFF: Name, title, one value-add link (optional)

RULES:
- Under 100 words for cold, under 150 for warm
- One ask, not multiple
- Make it easy to say yes ("15 min?" vs "let's schedule a meeting")
- No attachments on first email
```

## Objection Handling Playbook
```python
OBJECTIONS = {
    "too_expensive": [
        "What would the ROI need to be for this to make sense?",
        "Compared to {alternative}, what's the cost of not solving {problem}?",
        "We have options starting at {lower_tier} — what budget range works?",
    ],
    "not_right_time": [
        "What would need to change for this to be the right time?",
        "I understand. When {trigger_event} happens, would this be a priority?",
        "Can we schedule a 20-min check-in for [specific future date]?",
    ],
    "using_competitor": [
        "What do you like most about [competitor]?",
        "What would make you consider switching?",
        "Our customers who switched from [competitor] say [specific improvement].",
    ],
    "need_to_think": [
        "Of course. What specific questions can I answer to help you decide?",
        "What are the top 2-3 things you'd want to be sure about?",
        "Is there anything holding you back that I haven't addressed?",
    ],
    "need_approval": [
        "Who else is involved in this decision? I'd love to support you.",
        "What information would help you make the case internally?",
        "Would it be useful if I put together an ROI summary for your team?",
    ],
}
```

## Proposal Template
```
EXECUTIVE SUMMARY (1 page):
- Problem you're solving
- Proposed solution in plain English
- Expected outcomes + ROI
- Investment required
- Implementation timeline

SITUATION ANALYSIS:
- Current state (validated with discovery)
- Desired future state
- Gap analysis

PROPOSED SOLUTION:
- Scope of work
- Methodology
- Deliverables
- Timeline with milestones

INVESTMENT:
- Pricing options (Good/Better/Best)
- Payment terms
- What's included/excluded

SOCIAL PROOF:
- Relevant case study
- Reference contacts (if approved)

NEXT STEPS:
- Specific action items with dates
- Decision deadline (create urgency)
```

## Sales Metrics Tracking
```python
SALES_METRICS = {
    "pipeline": {
        "leads": "Total new leads this period",
        "mqls": "Marketing qualified leads",
        "sqls": "Sales qualified leads",
        "opportunities": "Deals in pipeline",
        "pipeline_value": "Total $ in pipeline",
        "weighted_pipeline": "Pipeline × avg close rate",
    },
    "velocity": {
        "avg_deal_size": "Average contract value",
        "sales_cycle_days": "Time from SQL to close",
        "win_rate": "Deals won / deals lost",
        "close_rate_by_stage": "% advancing at each stage",
    },
    "activity": {
        "calls_per_day": "Outbound dials",
        "connect_rate": "Calls / connects",
        "demo_booking_rate": "Connects / demos booked",
        "email_reply_rate": "Emails / replies",
    },
}
```

## Models to Use
- **Personalized outreach**: `gpt-4o` + Perplexity for company research
- **Proposal writing**: `claude-opus-4-6`
- **Objection responses**: `gpt-4o`
- **Bulk prospecting sequences**: `gpt-4o-mini`
- **CRM data analysis**: `gpt-4o` with code tools
