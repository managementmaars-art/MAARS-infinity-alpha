---
name: product-management-ai
description: AI product management skills — PRDs, roadmaps, user stories, sprint planning, OKRs, feature prioritization, product metrics for MAARS product agents
---

# Product Management AI — MAARS Reference

## PRD Template
```python
PRD_PROMPT = """
You are Elena Kovacs, MAARS Product Manager.

Write a PRD for: {feature_name}

Structure:
1. OVERVIEW (2 paragraphs): What we're building and why
2. PROBLEM STATEMENT: User pain point, current workaround, frequency/severity
3. SUCCESS METRICS: Primary metric + secondary metrics (quantified targets)
4. USER STORIES: "As a [user], I want [action] so that [benefit]"
5. REQUIREMENTS:
   - Functional (must-haves)
   - Non-functional (performance, security, scalability)
   - Out of scope (explicit)
6. DESIGN CONSIDERATIONS: UX principles, edge cases, error states
7. TECHNICAL NOTES: Integration points, data model changes, API contracts
8. TIMELINE: Milestones with dates
9. OPEN QUESTIONS: Decisions not yet made
10. DEPENDENCIES: Teams, systems, or data required
"""
```

## Prioritization Frameworks
```python
PRIORITIZATION = {
    "RICE": {
        "formula": "(Reach × Impact × Confidence) / Effort",
        "reach": "How many users affected per quarter?",
        "impact": "1=minimal, 2=low, 3=medium, 4=high, 5=massive",
        "confidence": "High=100%, Medium=80%, Low=50%",
        "effort": "Person-months",
    },
    "MoSCoW": {
        "Must": "Critical for launch, no workaround",
        "Should": "Important but not critical, manual workaround exists",
        "Could": "Nice to have, low impact if excluded",
        "Wont": "Out of scope for this cycle",
    },
    "ICE": {
        "formula": "Impact × Confidence × Ease",
        "all_scored": "1-10 scale",
        "note": "Simpler than RICE, good for early stage",
    },
    "Kano": {
        "basic_needs": "Expected, absence causes dissatisfaction",
        "performance": "More = better (linear satisfaction)",
        "delighters": "Unexpected, cause delight when present",
        "indifferent": "Users don't care either way",
    },
}
```

## User Story Format
```
STORY: As a [specific user type], I want [action/capability] so that [benefit/outcome]

ACCEPTANCE CRITERIA (Given/When/Then):
- Given [context], when [action], then [expected outcome]
- Given [edge case], when [action], then [expected behavior]

DEFINITION OF DONE:
□ Feature works as described in all ACs
□ Unit + integration tests written
□ No regression in related features
□ Docs updated
□ Analytics event added
□ Design reviewed and approved
```

## OKR Framework
```python
OKR_TEMPLATE = """
OBJECTIVE: [Inspirational, qualitative goal]

KR1: [Measurable outcome] — from [baseline] to [target] by [date]
  Initiatives: [2-3 specific projects that drive this KR]
  
KR2: [Measurable outcome] — from [baseline] to [target] by [date]
  Initiatives: [2-3 specific projects that drive this KR]
  
KR3: [Measurable outcome] — from [baseline] to [target] by [date]
  Initiatives: [2-3 specific projects that drive this KR]

OKR RULES:
- Objective should be memorable and inspiring
- KRs should be measurable (numbers, not activities)
- 60-70% achievement = good (if always hitting 100%, not ambitious enough)
- Max 3 objectives per team per quarter
"""
```

## Sprint Planning
```python
SPRINT_PLANNING_PROMPT = """
Plan a {duration}-week sprint for team: {team}
Velocity: {velocity} story points
Available capacity: {capacity} (accounting for meetings, PTO)
Previous sprint: {previous_sprint_summary}

From the backlog:
{backlog_items}

Create:
1. SPRINT GOAL: One sentence describing sprint purpose
2. COMMITTED STORIES: Items fitting within velocity
3. STORY POINT DISTRIBUTION: By team member
4. RISKS & BLOCKERS: Known impediments
5. DEPENDENCIES: External blockers to resolve
6. DEFINITION OF DONE: Sprint-specific criteria
"""
```

## Product Metrics Framework
```python
PRODUCT_METRICS = {
    "acquisition": ["signups", "CAC", "channel_attribution", "conversion_rate"],
    "activation": ["time_to_value", "onboarding_completion", "feature_adoption_D7"],
    "retention": ["DAU_MAU", "D1/D7/D30_retention", "churn_rate", "NRR"],
    "revenue": ["MRR", "ARPU", "LTV", "expansion_revenue"],
    "referral": ["NPS", "viral_coefficient", "referral_rate"],
    "engagement": ["session_length", "sessions_per_week", "feature_usage_depth"],
    
    "north_star": "The one metric that best captures core product value",
    "leading_indicators": "Metrics that predict future north star performance",
    "guardrail_metrics": "Metrics that must not degrade (e.g., churn, NPS)",
}
```

## Models to Use
- **PRDs + strategy**: `claude-opus-4-6` (best at structured long-form)
- **User story writing**: `gpt-4o`
- **Data analysis + metrics**: `gpt-4o` with code interpreter
- **Quick prioritization**: `claude-sonnet-4-6`
- **Competitive research**: `perplexity/sonar-pro`
