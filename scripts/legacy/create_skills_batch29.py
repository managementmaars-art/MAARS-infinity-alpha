
import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # Business & Professional Skills
    ('product-strategy', 'Product strategy - vision, market positioning, roadmapping, trade-offs, OKRs, GTM'),
    ('startup-fundraising', 'Startup fundraising - pitch deck, valuation, term sheets, due diligence, investors, SAFEs'),
    ('venture-capital', 'Venture capital - deal flow, thesis, due diligence, portfolio, board management, exits'),
    ('private-equity', 'Private equity - LBO, valuation, operational improvements, exits, debt structures, returns'),
    ('mergers-acquisitions', 'M&A - deal sourcing, valuation, LOI, due diligence, integration, synergies, HSR'),
    ('financial-modeling-advanced', 'Financial modeling advanced - LBO, DCF, merger, three-statement, sensitivities, scenarios'),
    ('corporate-finance', 'Corporate finance - capital structure, WACC, NPV, IRR, capital allocation, dividend policy'),
    ('accounting-advanced', 'Accounting advanced - GAAP, IFRS, consolidations, revenue recognition, ASC 606, leases'),
    ('tax-strategy', 'Tax strategy - corporate tax, transfer pricing, R&D credits, NOLs, international, structuring'),
    ('treasury-management', 'Treasury management - cash management, FX, liquidity, hedging, bank relationships, payments'),
    ('investor-relations', 'Investor relations - earnings calls, guidance, analyst days, roadshows, SEC filings, messaging'),
    ('board-governance', 'Board governance - charters, committees, fiduciary duties, executive compensation, reporting'),
    # Management & Leadership
    ('engineering-management', 'Engineering management - 1:1s, performance reviews, team building, roadmaps, hiring'),
    ('technical-leadership', 'Technical leadership - architecture decisions, mentoring, technical vision, influence'),
    ('executive-leadership', 'Executive leadership - CEO/CTO/VP roles, organizational design, culture, strategy'),
    ('organizational-design', 'Organizational design - structure, reporting, span of control, matrix, cross-functional'),
    ('change-management', 'Change management - Kotter, ADKAR, stakeholder buy-in, communication, resistance'),
    ('okr-implementation', 'OKR implementation - setting objectives, key results, cadence, check-ins, review, grading'),
    ('hiring-process', 'Hiring process - job descriptions, sourcing, screening, interviews, leveling, offers, onboarding'),
    ('performance-management', 'Performance management - reviews, ratings, PIPs, calibration, leveling, promotions, feedback'),
    ('remote-team-management', 'Remote team management - async communication, documentation, culture, tools, productivity'),
    ('diversity-inclusion', 'Diversity & inclusion - hiring bias, ERGs, pay equity, inclusive culture, metrics, programs'),
    ('employee-experience', 'Employee experience - onboarding, engagement, retention, surveys, ENPS, journey mapping'),
    ('compensation-design', 'Compensation design - salary bands, equity, bonuses, benefits, benchmarking, pay equity'),
    # Project & Program Management
    ('scrum-advanced', 'Scrum advanced - sprint planning, retrospectives, scaling, anti-patterns, metrics, maturity'),
    ('kanban-advanced', 'Kanban advanced - WIP limits, flow metrics, forecasting, classes of service, kanban maturity'),
    ('safe-agile', 'SAFe Agile - PI planning, ARTs, value streams, portfolio kanban, OKRs, DevOps'),
    ('prince2-pm', 'PRINCE2 - themes, processes, management products, tailoring, agile integration'),
    ('pmp-practices', 'PMP practices - PMBOK, scope, schedule, cost, quality, risk, procurement, stakeholder'),
    ('critical-path-method', 'Critical path method - network diagrams, CPM, PERT, resource leveling, crashing, EVM'),
    ('earned-value-management', 'Earned value management - PV, EV, AC, SPI, CPI, EAC, VAC, forecasting'),
    ('risk-management-pm', 'Risk management PM - identification, qualitative, quantitative, response, monitoring'),
    ('stakeholder-management', 'Stakeholder management - mapping, engagement, communication plans, influence, conflict'),
    ('program-management', 'Program management - roadmaps, dependency management, executive reporting, governance'),
    # Communication & Writing
    ('technical-documentation', 'Technical documentation - architecture docs, runbooks, ADRs, API docs, onboarding'),
    ('executive-communication', 'Executive communication - memos, strategy docs, board decks, presentations, framing'),
    ('persuasive-writing', 'Persuasive writing - argumentation, evidence, structure, rhetorical devices, audience'),
    ('business-writing', 'Business writing - emails, reports, proposals, SOWs, NDA review, clarity, tone'),
    ('speechwriting', 'Speechwriting - structure, storytelling, audience analysis, rhetoric, delivery notes'),
    ('data-storytelling', 'Data storytelling - narrative, visualization, context, insights, audience, call to action'),
    ('internal-comms-strategy', 'Internal communications strategy - channels, cadence, all-hands, newsletters, town halls'),
    ('crisis-communications', 'Crisis communications - messaging, spokesperson, media, timelines, post-incident review'),
    # Marketing deep
    ('demand-generation', 'Demand generation - campaigns, content, SEO, paid, ABM, attribution, pipeline'),
    ('growth-marketing', 'Growth marketing - acquisition, activation, retention, revenue, referral, experiments'),
    ('content-marketing', 'Content marketing - strategy, SEO, editorial calendar, distribution, repurposing, ROI'),
    ('performance-marketing', 'Performance marketing - SEM, paid social, display, programmatic, attribution, ROAS'),
    ('email-marketing-advanced', 'Email marketing advanced - segmentation, automation, deliverability, A/B, lifecycle'),
    ('social-media-strategy', 'Social media strategy - platforms, content mix, engagement, paid, influencer, analytics'),
    ('brand-strategy', 'Brand strategy - positioning, messaging, visual identity, voice, guidelines, equity'),
    ('product-marketing', 'Product marketing - positioning, launch, sales enablement, competitive, win/loss, personas'),
    ('developer-marketing', 'Developer marketing - devrel, documentation, community, conferences, content, SDKs'),
    ('partner-marketing', 'Partner marketing - co-marketing, MDF, joint GTM, enablement, attribution, programs'),
    ('account-based-marketing', 'ABM - target account lists, 1:1, 1:few, 1:many, intent data, personalization'),
    ('marketing-analytics', 'Marketing analytics - attribution models, MMM, incrementality, lifetime value, CAC'),
    ('seo-advanced', 'SEO advanced - technical audit, Core Web Vitals, E-E-A-T, schema, link building, SGE'),
    ('conversion-optimization', 'Conversion rate optimization - landing pages, testing, heatmaps, UX, copy, forms'),
    # Sales
    ('sales-methodology', 'Sales methodology - MEDDIC, Challenger, SPIN, value selling, discovery, closing'),
    ('enterprise-sales', 'Enterprise sales - complex deals, champions, economic buyers, procurement, legal, POC'),
    ('sales-operations', 'Sales operations - CRM, forecasting, territory, quota, compensation, process, analytics'),
    ('sales-enablement', 'Sales enablement - content, training, playbooks, onboarding, tools, coaching, metrics'),
    ('customer-success-advanced', 'Customer success advanced - health scores, QBRs, expansions, renewals, churn risk'),
    ('revenue-operations', 'Revenue operations - alignment, data, systems, process, reporting, lead to cash'),
    ('pricing-strategy', 'Pricing strategy - value-based, cost-plus, competitive, freemium, usage-based, tiered'),
    ('channel-sales', 'Channel sales - partners, resellers, MSPs, enablement, deal registration, margin'),
    ('inside-sales', 'Inside sales - SDR/BDR, sequences, cold calling, email, objection handling, pipeline'),
    ('deal-desk', 'Deal desk - discounting, approval workflows, CPQ, contract management, revenue recognition'),
    # Customer & UX
    ('ux-research', 'UX research - usability testing, interviews, surveys, card sorting, tree testing, synthesis'),
    ('user-interview-techniques', 'User interview techniques - scripting, moderation, bias, synthesis, affinity mapping'),
    ('design-thinking', 'Design thinking - empathize, define, ideate, prototype, test, iteration, facilitation'),
    ('service-design', 'Service design - blueprints, touchpoints, frontstage, backstage, personas, journey maps'),
    ('information-architecture', 'Information architecture - taxonomy, navigation, search, labeling, organization, IA audit'),
    ('accessibility-ux', 'Accessibility UX - WCAG, screen readers, keyboard, color contrast, cognitive load'),
    ('mobile-ux', 'Mobile UX - thumb zones, gestures, forms, navigation patterns, progressive disclosure'),
    ('conversational-ux', 'Conversational UX - chatbot design, NLU, intents, entities, fallbacks, voice UI'),
    ('data-driven-ux', 'Data-driven UX - analytics integration, event tracking, funnel analysis, A/B, heatmaps'),
    ('prototyping', 'Prototyping - wireframes, mockups, interactive, fidelity levels, tools, user testing'),
    # Finance/FinTech
    ('financial-risk', 'Financial risk - credit, market, liquidity, operational, model risk, ICAAP, stress tests'),
    ('quantitative-trading', 'Quantitative trading - alpha research, execution, risk management, backtesting, live'),
    ('robo-advisory', 'Robo advisory - portfolio construction, rebalancing, tax-loss harvesting, onboarding, API'),
    ('banking-core', 'Core banking - ledger, transactions, accounts, interest, loans, deposits, reconciliation'),
    ('payments-advanced', 'Payments advanced - card networks, ACH, wire, SWIFT, ISO 20022, settlement, clearing'),
    ('open-banking-advanced', 'Open banking advanced - PSD2, PSD3, FDX, consent, APIs, aggregation, TPP'),
    ('neobank-platform', 'Neobank platform - BaaS, ledger, compliance, onboarding, cards, limits, notifications'),
    ('crypto-trading', 'Crypto trading - orderbooks, liquidity, market making, arbitrage, on-chain, derivatives'),
    ('defi-advanced', 'DeFi advanced - AMM, yield, lending, leverage, liquidations, composability, MEV'),
    ('central-bank-digital', 'CBDC - design, privacy, programmability, distribution, offline, cross-border, policy'),
    # Operations
    ('supply-chain-advanced', 'Supply chain advanced - resilience, near-shoring, risk mapping, visibility, digital twin'),
    ('procurement-strategy', 'Procurement strategy - category management, supplier development, TCO, negotiation, ESG'),
    ('operations-excellence', 'Operations excellence - Six Sigma, Lean, waste elimination, process mapping, kaizen'),
    ('quality-management', 'Quality management - ISO 9001, TQM, FMEA, control charts, SPC, audit, CAPA'),
    ('facilities-management', 'Facilities management - space planning, HVAC, energy, maintenance, CMMS, workplace'),
    ('logistics-management', 'Logistics management - inbound, outbound, 3PL, TMS, last mile, returns, cold chain'),
    ('manufacturing-excellence', 'Manufacturing excellence - OEE, TPM, SPC, Poka-Yoke, SMED, 5S, pull systems'),
    ('inventory-management-advanced', 'Inventory management advanced - ABC analysis, cycle counting, FIFO, LIFO, reorder'),
    ('customer-service', 'Customer service - ticketing, SLAs, escalations, knowledge base, CSAT, FCR'),
    ('business-continuity', 'Business continuity - BIA, BCP, DR, RTO, RPO, testing, crisis management, recovery'),
    # HR Technology
    ('hris-systems', 'HRIS systems - Workday, SAP SuccessFactors, Oracle HCM, ADP, BambooHR, integrations'),
    ('talent-acquisition-tech', 'Talent acquisition tech - ATS, sourcing tools, HireVue, assessments, referrals'),
    ('learning-development', 'L&D - LMS, e-learning, microlearning, skills mapping, career pathing, coaching'),
    ('workforce-planning', 'Workforce planning - headcount modeling, scenario planning, skills forecasting, retention'),
    ('payroll-systems', 'Payroll systems - multi-jurisdiction, garnishments, benefits, compliance, reconciliation'),
    # Legal & Compliance
    ('contract-management', 'Contract management - CLM, lifecycle, templates, redlines, negotiation, obligations'),
    ('intellectual-property', 'Intellectual property - patents, trademarks, copyrights, trade secrets, licensing, FTO'),
    ('corporate-law-basics', 'Corporate law basics - formation, governance, equity, financing, board, securities'),
    ('employment-law', 'Employment law - at-will, discrimination, harassment, FMLA, FLSA, classification, WARN'),
    ('privacy-law', 'Privacy law - GDPR, CCPA, CPRA, VCDPA, biometric data, children privacy, enforcement'),
    ('regulatory-compliance-advanced', 'Regulatory compliance advanced - program design, testing, monitoring, reporting, exam'),
    ('export-controls', 'Export controls - EAR, ITAR, sanctions, OFAC, BIS, license exceptions, compliance program'),
    ('antitrust-competition', 'Antitrust/competition law - market definition, monopolization, M&A, cartel, compliance'),
    ('esg-reporting', 'ESG reporting - GRI, TCFD, SASB, EU taxonomy, scope 1/2/3, materiality, assurance'),
    # Healthcare operations
    ('hospital-operations', 'Hospital operations - patient flow, capacity, scheduling, throughput, quality metrics'),
    ('medical-billing', 'Medical billing - ICD-10, CPT, RCM, claims, denials, prior auth, ERA, remittance'),
    ('population-health', 'Population health - risk stratification, care management, analytics, outcomes, social determinants'),
    ('clinical-trials', 'Clinical trials - design, IRB, ICH-GCP, protocol, randomization, data management, analysis'),
    ('pharmacy-management', 'Pharmacy management - formulary, MTM, PBM, specialty, adherence, analytics'),
    # Education/EdTech
    ('curriculum-design', 'Curriculum design - learning objectives, Bloom taxonomy, assessment, scaffolding, UbD'),
    ('instructional-design', 'Instructional design - ADDIE, SAM, e-learning, storyboards, LMS, evaluation'),
    ('educational-assessment', 'Educational assessment - formative, summative, rubrics, feedback, analytics, adaptive'),
    ('k12-technology', 'K-12 technology - SIS, LMS, assessment platforms, parent communication, devices'),
    ('higher-education', 'Higher education - enrollment management, student success, accreditation, outcomes, CRM'),
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
