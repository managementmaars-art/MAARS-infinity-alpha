
import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # AI governance and responsible AI platform
    ('ai-governance-platform', 'AI governance platform - model registry, lineage tracking, audit trails, policy enforcement, risk tiers'),
    ('responsible-ai-advanced', 'Responsible AI advanced - fairness metrics, bias auditing, explainability pipelines, model cards'),
    ('ai-risk-management', 'AI risk management - EU AI Act compliance, risk categorization, impact assessment, documentation'),
    ('mlops-governance', 'MLOps governance - model approval workflows, experiment tracking, reproducibility, lineage, compliance'),
    ('ai-observability-platform', 'AI observability platform - model drift detection, data drift, prediction monitoring, alerting'),
    ('llm-evaluation-platform', 'LLM evaluation platform - benchmark harness, red-teaming pipelines, safety evals, capability testing'),
    ('ai-incident-response', 'AI incident response - model failure detection, rollback procedures, impact assessment, communications'),
    ('synthetic-data-governance', 'Synthetic data governance - privacy validation, statistical fidelity, bias propagation, audit'),
    ('ai-supply-chain-security', 'AI supply chain security - model provenance, training data auditing, dependency scanning, SBOM'),
    ('human-in-the-loop-platform', 'Human-in-the-loop platform - active learning, annotation workflows, model-human handoffs, confidence'),
    # Low-code/no-code platform engineering
    ('low-code-platform-engineering', 'Low-code platform engineering - visual builders, formula engines, component libraries, extensibility'),
    ('no-code-workflow-automation', 'No-code workflow automation - trigger-action paradigm, visual flow builders, conditionals, error handling'),
    ('citizen-developer-platform', 'Citizen developer platform - governance, guardrails, shadow IT prevention, templates, center of excellence'),
    ('workflow-automation-platform', 'Workflow automation platform - Zapier clone design, webhook ingestion, step runners, error queues'),
    ('form-builder-platform', 'Form builder platform - conditional logic, multi-step, file uploads, integrations, submission handling'),
    ('visual-programming-advanced', 'Visual programming advanced - node-based editors, dataflow programming, blocks, live preview'),
    ('app-builder-platform', 'App builder platform - drag-and-drop UI, data binding, CRUD automation, role-based access, publishing'),
    ('rpa-platform-advanced', 'RPA platform advanced - attended vs unattended, bot orchestration, exception handling, AI augmentation'),
    ('integration-platform-advanced', 'Integration platform advanced - iPaaS design, connectors marketplace, transformation, error handling'),
    ('business-rules-engine-advanced', 'Business rules engine advanced - Drools, decision tables, rule versioning, testing, hot reload'),
    # Financial technology platform advanced
    ('payment-orchestration', 'Payment orchestration - routing logic, fallback providers, retry strategies, reconciliation, reporting'),
    ('banking-as-a-service', 'Banking as a service - BaaS platform design, ledger services, compliance APIs, white-label banking'),
    ('embedded-finance-platform', 'Embedded finance platform - BNPL integration, card issuance APIs, account origination, compliance'),
    ('financial-data-aggregation', 'Financial data aggregation - Plaid integration, Open Finance, data normalization, enrichment'),
    ('treasury-management-platform', 'Treasury management platform - cash pooling, FX hedging, liquidity forecasting, bank connectivity'),
    ('trade-surveillance-platform', 'Trade surveillance platform - market manipulation detection, wash trading, best execution, MiFID II'),
    ('wealth-management-platform-advanced', 'Wealth management platform advanced - AUM tracking, rebalancing engine, tax-loss harvesting, custody'),
    ('insurance-claims-platform', 'Insurance claims platform - FNOL, adjudication rules, subrogation, fraud detection, settlement'),
    ('factoring-platform', 'Factoring platform - invoice discounting, receivables management, credit scoring, risk tranching'),
    ('cryptocurrency-custody', 'Cryptocurrency custody platform - MPC wallets, cold storage, signing ceremony, compliance, reporting'),
    # Healthcare technology advanced
    ('clinical-workflow-automation', 'Clinical workflow automation - care pathway engines, order sets, clinical decision support, EHR integration'),
    ('population-health-platform-advanced', 'Population health platform advanced - risk stratification, care gap analysis, outreach, ACO'),
    ('telehealth-platform-advanced', 'Telehealth platform advanced - video consultations, async messaging, RPM integration, billing'),
    ('healthcare-data-exchange', 'Healthcare data exchange - FHIR R4/R5, CDS Hooks, SMART on FHIR, QHINs, TEFCA'),
    ('pharmacy-tech-advanced', 'Pharmacy technology advanced - prescription routing, PBM integration, drug interaction checking, adherence'),
    ('medical-device-platform', 'Medical device platform - device connectivity, FDA 510k, UDI, cybersecurity, post-market surveillance'),
    ('genomics-platform-advanced', 'Genomics platform advanced - variant calling pipelines, GWAS, polygenic risk scores, VCF management'),
    ('revenue-cycle-management-advanced', 'Revenue cycle management advanced - charge capture, coding, prior auth, denial management, AR'),
    ('health-plan-technology', 'Health plan technology - enrollment, claims adjudication, provider network, benefit configuration'),
    ('precision-medicine-platform-advanced', 'Precision medicine platform advanced - biomarker analysis, companion diagnostics, clinical trial matching'),
    # Education technology advanced
    ('adaptive-learning-platform-advanced', 'Adaptive learning platform advanced - knowledge graph, mastery tracking, spaced repetition, IRT'),
    ('learning-analytics-platform-advanced', 'Learning analytics platform advanced - xAPI, learning record store, predictive analytics, dropout'),
    ('virtual-classroom-platform', 'Virtual classroom platform - WebRTC integration, interactive whiteboard, breakout rooms, recording'),
    ('assessment-engine-advanced', 'Assessment engine advanced - item banks, psychometrics, computer adaptive testing, anti-cheating'),
    ('competency-based-education', 'Competency-based education platform - skill mapping, portfolio assessment, micro-credentials, badging'),
    ('tutoring-platform-advanced', 'Tutoring platform advanced - AI tutoring, human tutor matching, session management, progress tracking'),
    ('school-management-advanced', 'School management system advanced - SIS, gradebook, attendance, scheduling, parent portal'),
    ('curriculum-management-platform', 'Curriculum management platform - standards alignment, content sequencing, OER, outcomes mapping'),
    ('corporate-learning-platform', 'Corporate learning platform - compliance training, skill gap analysis, cohort management, completion'),
    ('language-learning-platform-advanced', 'Language learning platform advanced - SRS, speaking practice, grammar correction, content progression'),
    # Supply chain technology advanced
    ('supply-chain-control-tower', 'Supply chain control tower - end-to-end visibility, exception management, AI recommendations, KPIs'),
    ('demand-sensing-platform', 'Demand sensing platform - POS data integration, social signals, weather correlation, ML forecasting'),
    ('supplier-collaboration-platform', 'Supplier collaboration platform - vendor portal, PO management, capacity sharing, scorecards'),
    ('logistics-optimization-platform', 'Logistics optimization platform - route optimization, carrier selection, load planning, last-mile'),
    ('warehouse-management-advanced', 'Warehouse management system advanced - slotting, wave picking, robotics integration, RFID, voice'),
    ('trade-compliance-platform', 'Trade compliance platform - HS classification, denied party screening, export controls, duty drawback'),
    ('cold-chain-platform-advanced', 'Cold chain platform advanced - temperature monitoring, excursion alerts, IoT sensors, regulatory'),
    ('reverse-logistics-platform', 'Reverse logistics platform - returns management, refurbishment routing, disposition rules, credits'),
    ('supply-chain-finance-platform', 'Supply chain finance platform - dynamic discounting, supplier financing, inventory financing'),
    ('supply-chain-twin-platform', 'Supply chain digital twin - simulation, scenario modeling, disruption analysis, optimization'),
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
