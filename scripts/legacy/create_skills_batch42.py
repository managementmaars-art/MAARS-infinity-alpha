
import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # From alirezarezvani/claude-skills - product-team
    ('agile-product-owner', 'Agile product owner - backlog refinement, story writing, sprint planning, stakeholder alignment'),
    ('code-to-prd', 'Code to PRD - reverse-engineer existing code into product requirements document, feature docs'),
    ('competitive-teardown', 'Competitive teardown - product analysis, feature comparison, positioning gaps, opportunity map'),
    ('experiment-designer', 'Experiment designer - A/B test hypothesis, sample size, metrics, analysis plan, results'),
    ('research-summarizer', 'Research summarizer - synthesize user interviews, surveys, data into actionable product insights'),
    ('roadmap-communicator', 'Roadmap communicator - stakeholder presentations, roadmap narratives, prioritization rationale'),
    ('saas-scaffolder', 'SaaS scaffolder - project structure, auth, billing, multi-tenancy, API, admin, onboarding'),
    ('ui-design-system', 'UI design system - component library, tokens, guidelines, accessibility, documentation, adoption'),
    ('ux-researcher-designer', 'UX researcher designer - research methods, wireframes, prototypes, usability testing, synthesis'),
    # From c-level-advisor
    ('agent-protocol', 'Agent protocol - multi-agent communication standards, handoffs, state, trust, observability'),
    ('board-deck-builder', 'Board deck builder - executive narrative, financials, strategy slides, appendix, design'),
    ('board-meeting', 'Board meeting prep - agenda, pre-reads, Q&A preparation, follow-up tracking, minutes'),
    ('ceo-advisor', 'CEO advisor - strategy, fundraising, team building, culture, decision-making, stakeholder management'),
    ('cfo-advisor', 'CFO advisor - financial strategy, FP&A, fundraising, cash management, board reporting, M&A'),
    ('chief-of-staff', 'Chief of staff - executive support, cross-functional projects, OKR tracking, leadership ops'),
    ('chro-advisor', 'CHRO advisor - people strategy, talent, compensation, culture, org design, HRIS, compliance'),
    ('ciso-advisor', 'CISO advisor - security strategy, risk management, compliance, incident response, board reporting'),
    ('cmo-advisor', 'CMO advisor - brand strategy, demand gen, product marketing, growth, analytics, team building'),
    ('company-os', 'Company OS - operating cadence, meeting rhythms, goal setting, communication, knowledge management'),
    ('competitive-intel', 'Competitive intelligence - market monitoring, win/loss, positioning, battlecards, alerts'),
    ('context-engine', 'Context engine - organizational knowledge capture, institutional memory, decision history'),
    ('coo-advisor', 'COO advisor - operations strategy, process excellence, team scaling, metrics, cross-functional'),
    ('cpo-advisor', 'CPO advisor - product strategy, roadmap, prioritization, team structure, metrics, customer'),
    ('cro-advisor', 'CRO advisor - revenue strategy, sales process, partnerships, pricing, expansion, forecasting'),
    ('cs-onboard', 'CS onboard - customer success onboarding, health scores, playbooks, QBR, expansion motions'),
    ('cto-advisor', 'CTO advisor - technical strategy, architecture, team building, vendor selection, innovation'),
    ('culture-architect', 'Culture architect - values definition, rituals, hiring for culture, recognition, remote culture'),
    ('decision-logger', 'Decision logger - decision documentation, context capture, outcome tracking, institutional memory'),
    ('executive-mentor', 'Executive mentor - leadership coaching, career development, feedback, blind spots, growth'),
    ('founder-coach', 'Founder coach - founder psychology, decisions under uncertainty, cofounder dynamics, burnout'),
    ('internal-narrative', 'Internal narrative - all-hands messaging, strategy communication, change management comms'),
    ('intl-expansion', 'International expansion - market selection, localization, legal, ops, GTM, team structure'),
    ('ma-playbook', 'M&A playbook - target screening, due diligence, integration planning, PMO, synergy tracking'),
    ('org-health-diagnostic', 'Org health diagnostic - team engagement, retention risk, collaboration patterns, dysfunction'),
    ('scenario-war-room', 'Scenario war room - strategic planning, stress testing, competitive scenarios, decision trees'),
    ('strategic-alignment', 'Strategic alignment - OKR cascading, cross-functional priority alignment, operating reviews'),
    # From business-growth
    ('contract-and-proposal-writer', 'Contract and proposal writer - SOW, MSA, NDA, RFP responses, proposal templates'),
    ('customer-success-manager', 'Customer success manager - onboarding, health scores, QBRs, renewal, expansion, churn'),
    ('sales-engineer', 'Sales engineer - technical discovery, demo, POC, RFP, objection handling, champion building'),
    # From finance
    ('business-investment-advisor', 'Business investment advisor - ROI analysis, build vs buy, capital allocation, business cases'),
    ('financial-analyst', 'Financial analyst - modeling, variance analysis, forecasting, dashboards, scenarios, reporting'),
    ('saas-metrics-coach', 'SaaS metrics coach - ARR, churn, LTV, CAC, NRR, cohorts, unit economics, benchmarks'),
    # From project-management
    ('atlassian-admin', 'Atlassian admin - Jira/Confluence administration, schemes, permissions, automation, integrations'),
    ('atlassian-templates', 'Atlassian templates - Jira issue types, Confluence page templates, workflow customization'),
    ('confluence-expert', 'Confluence expert - space architecture, templates, macros, permissions, search, migration'),
    ('jira-expert', 'Jira expert - JQL, workflows, automation rules, custom fields, dashboards, reporting, API'),
    ('meeting-analyzer', 'Meeting analyzer - transcript analysis, action items, decisions, follow-ups, effectiveness'),
    ('scrum-master', 'Scrum master - sprint facilitation, retrospectives, impediment removal, metrics, coaching'),
    ('senior-pm', 'Senior PM - strategic project management, executive stakeholders, program governance, risk'),
    ('team-communications', 'Team communications - async comms, status updates, decision announcements, team cohesion'),
    # From ra-qm-team
    ('regulatory-affairs-head', 'Regulatory affairs head - strategy, submissions, agency interactions, labeling, post-market'),
    ('quality-manager-qmr', 'Quality manager QMR - management review, KPIs, corrective actions, audit findings, trends'),
    ('quality-manager-qms-iso13485', 'QMS ISO 13485 - quality management system, design controls, validation, risk management'),
    ('capa-officer', 'CAPA officer - corrective/preventive actions, root cause analysis, effectiveness checks, tracking'),
    ('quality-documentation-manager', 'Quality documentation manager - SOPs, work instructions, document control, training records'),
    ('risk-management-specialist', 'Risk management specialist - ISO 14971, risk files, FMEA, hazard analysis, residual risk'),
    ('information-security-manager-iso27001', 'Information security manager ISO 27001 - ISMS, controls, risk treatment, audit, PDCA'),
    ('mdr-745-specialist', 'MDR 745 specialist - EU Medical Device Regulation, technical files, EUDAMED, PMS, vigilance'),
    ('fda-consultant-specialist', 'FDA consultant specialist - 510k, PMA, De Novo, quality systems, inspections, recalls'),
    ('qms-audit-expert', 'QMS audit expert - internal audits, supplier audits, CAPA follow-up, audit program management'),
    ('isms-audit-expert', 'ISMS audit expert - ISO 27001 internal audit, evidence collection, nonconformity, closure'),
    ('gdpr-dsgvo-expert', 'GDPR/DSGVO expert - privacy compliance, DPIAs, data mapping, breach notification, DPO support'),
]

for name, desc in skills:
    d = os.path.join(base, name)
    os.makedirs(d, exist_ok=True)
    title = name.replace('-', ' ').title()
    content = f'''---
name: {name}
description: {desc}
---

# {title} - MAARS Reference

## Overview
{desc}

## Core Framework
Use structured approach: define goal, identify audience, create hypothesis, execute, measure.

## Key Prompts
- "For [project], implement {title.lower()} for [use case]. Requirements: [X]. Provide working code examples."
- "Analyze [existing implementation] and suggest 3 improvements prioritized by impact."
- "Write a {title.lower()} template for a [type] project with [specific requirements]."

## Best Practices
1. Read official documentation before implementation
2. Test in isolation before full integration
3. Handle errors and edge cases explicitly
4. Document configuration and requirements
5. Monitor and alert on key metrics

## Common Patterns
- Setup and initialization
- Core operations
- Error handling and retries
- Authentication and security
- Performance and scaling

## Models to Use
- Architecture: claude-opus-4-6
- Implementation: claude-sonnet-4-6
- Quick lookups: claude-haiku-4-5-20251001
'''
    with open(os.path.join(d, 'SKILL.md'), 'w') as f:
        f.write(content)

print('Done:', len(skills), 'skills')
