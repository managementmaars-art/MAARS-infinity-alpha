import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # Retail Banking and Consumer Financial Services Operations
    ('online-banking-platform-ops', 'Manage online banking platforms including session management, feature rollouts, and user experience optimization without disrupting active customer sessions'),
    ('mobile-banking-app-management', 'Oversee mobile banking application lifecycle including release management, push notification systems, biometric auth integration, and crash analytics'),
    ('branch-operations-technology', 'Support branch banking technology stacks including teller cash dispensers, vault management systems, branch capture, and lobby management software'),
    ('consumer-lending-origination', 'Automate consumer loan origination workflows covering application intake, credit decisioning, document collection, underwriting queues, and closing coordination'),
    ('deposit-operations-systems', 'Manage deposit operations platforms for account opening, signature card processing, holds management, interest accrual, and statement generation'),
    ('card-services-management', 'Operate card services platforms covering issuance, activation, PIN management, dispute processing, rewards tracking, and card controls for debit and credit products'),
    ('fraud-operations-technology', 'Configure and tune fraud detection systems including rules engines, ML model thresholds, case management queues, alert routing, and SAR filing workflows'),
    ('teller-system-administration', 'Administer teller platform configurations including transaction routing, override controls, cash drawer reconciliation, and end-of-day balancing procedures'),
    ('atm-channel-management', 'Manage ATM network operations including device monitoring, cash forecasting, software deployment, incident management, and surcharge configuration'),
    ('kyc-aml-compliance-systems', 'Implement and maintain KYC and AML compliance technology including customer due diligence workflows, watchlist screening, transaction monitoring, and regulatory reporting'),
]
skills += [
    # Pharmaceutical Manufacturing Operations Technology
    ('batch-record-management', 'Design and manage electronic batch record systems for pharmaceutical manufacturing including recipe management, in-process controls, and batch release workflows compliant with 21 CFR Part 11'),
    ('equipment-qualification-lifecycle', 'Execute equipment qualification protocols including IQ, OQ, and PQ documentation, requalification scheduling, and change control integration for GMP manufacturing assets'),
    ('pharmaceutical-qa-systems', 'Implement quality assurance management systems for pharma operations covering CAPA workflows, change control, complaint handling, and quality event investigation'),
    ('regulatory-submission-technology', 'Manage technology supporting regulatory submissions including eCTD compilation, submission tracking, agency correspondence management, and label change coordination'),
    ('stability-testing-management', 'Configure stability study management platforms covering protocol setup, sample scheduling, results capture, out-of-specification handling, and trend reporting'),
    ('serialization-track-trace', 'Implement pharmaceutical serialization and track-and-trace systems for unit-level coding, aggregation, commissioning, and regulatory compliance with DSCSA and EU FMD requirements'),
    ('cleanroom-environmental-monitoring', 'Manage cleanroom environmental monitoring systems including continuous particle counting, microbial sampling scheduling, alert and action limit management, and trend analysis'),
    ('deviation-management-systems', 'Administer deviation management platforms for pharmaceutical manufacturing covering deviation capture, root cause investigation, impact assessment, and CAPA linkage'),
    ('validation-lifecycle-management', 'Oversee computer system validation lifecycle including validation planning, protocol authoring, execution tracking, summary reporting, and periodic review scheduling'),
    ('lims-integration-pharma', 'Integrate laboratory information management systems with manufacturing execution systems, instrument interfaces, and quality systems for seamless data flow in pharma operations'),
]
skills += [
    # Media and Entertainment Production Technology
    ('production-scheduling-systems', 'Implement and manage production scheduling platforms for film and television covering shoot day planning, resource allocation, call sheet generation, and schedule change communication'),
    ('script-breakdown-technology', 'Use script breakdown software to tag and categorize script elements including characters, locations, props, wardrobe, and special requirements to drive production planning'),
    ('production-budgeting-platforms', 'Manage production budgeting software for film and TV including top sheet creation, cost tracking, purchase order management, cost-to-complete forecasting, and final cost reports'),
    ('cast-crew-management-systems', 'Administer cast and crew management platforms covering deal memo tracking, availability calendars, contact management, and union contract compliance reporting'),
    ('location-management-technology', 'Use location management software for scouting databases, permit tracking, location agreements, site surveys, and production day logistics coordination'),
    ('post-production-workflow-management', 'Design and manage post-production workflows including editorial handoff, review and approval routing, version control, conform processes, and deliverable tracking'),
    ('vfx-pipeline-management', 'Oversee VFX production pipeline technology including shot tracking, render farm management, asset versioning, artist task assignment, and client review systems'),
    ('sound-design-workflow-systems', 'Configure sound design and audio post-production workflow platforms covering spotting session notes, asset management, ADR scheduling, mix session organization, and delivery specifications'),
    ('music-licensing-management', 'Manage music licensing platforms for production covering cue sheet creation, sync license tracking, master use requests, royalty reporting, and music budget monitoring'),
    ('distribution-metadata-management', 'Implement distribution metadata management systems for film and TV covering title metadata, localization asset tracking, platform delivery specifications, and content availability windows'),
]
skills += [
    # Workforce Management and HR Technology Platforms
    ('time-attendance-systems', 'Configure and administer time and attendance platforms including clock-in methods, overtime rules, pay period processing, exception management, and payroll export integration'),
    ('shift-scheduling-optimization', 'Use workforce scheduling platforms to build optimized shift schedules based on labor demand forecasts, employee availability, skill requirements, and compliance constraints'),
    ('leave-management-systems', 'Implement leave management platforms covering leave request workflows, accrual policy configuration, FMLA tracking, return-to-work management, and absence reporting'),
    ('payroll-system-integration', 'Design integrations between workforce management and payroll systems ensuring accurate transfer of hours, earnings codes, cost center allocations, and exception data'),
    ('labor-demand-forecasting', 'Apply labor forecasting tools and methods to predict staffing needs based on historical patterns, business drivers, and seasonal adjustments to optimize workforce planning'),
    ('field-service-workforce-management', 'Manage field service workforce platforms including technician dispatch, mobile work order management, GPS tracking, parts inventory, and customer appointment scheduling'),
    ('hr-analytics-platforms', 'Implement HR analytics platforms for workforce insights including turnover analysis, headcount reporting, diversity metrics, compensation benchmarking, and predictive attrition modeling'),
    ('onboarding-automation-systems', 'Design automated onboarding workflows covering new hire task assignment, document collection, system access provisioning, training enrollment, and manager notification'),
    ('performance-management-technology', 'Configure performance management platforms for goal setting, continuous feedback, mid-year reviews, annual evaluations, calibration workflows, and development planning'),
    ('compensation-planning-systems', 'Implement compensation planning platforms supporting merit cycle management, salary range configuration, bonus pool allocation, equity awards, and total rewards statements'),
]
skills += [
    # Environmental Health and Safety (EHS) Management Technology
    ('ehs-incident-reporting-systems', 'Configure EHS incident reporting platforms for near-miss capture, injury and illness recording, OSHA log management, root cause investigation, and corrective action tracking'),
    ('chemical-inventory-sds-management', 'Manage chemical inventory and SDS management systems covering chemical approval workflows, inventory tracking by location, SDS repository maintenance, and exposure limit monitoring'),
    ('environmental-permit-compliance', 'Implement permit compliance management platforms for air, water, and waste permits including monitoring schedule management, deviation reporting, and regulatory submission tracking'),
    ('ehs-audit-management', 'Design EHS audit management workflows covering audit scheduling, checklist configuration, field observation capture, finding classification, and corrective action assignment'),
    ('safety-training-tracking-systems', 'Administer safety training tracking platforms for curriculum management, completion tracking, certification expiration alerts, and regulatory training compliance reporting'),
    ('ppe-management-technology', 'Implement PPE management systems for hazard-based PPE requirement mapping, issuance tracking, inspection scheduling, and inventory management at site and department level'),
    ('contractor-safety-management', 'Configure contractor safety management platforms covering prequalification workflows, insurance verification, safety orientation tracking, and on-site permit management'),
    ('environmental-monitoring-systems', 'Manage environmental monitoring technology for continuous emissions monitoring, stormwater sampling, groundwater tracking, and regulatory data reporting to environmental agencies'),
    ('ehs-risk-assessment-platforms', 'Use EHS risk assessment platforms to conduct job hazard analyses, process hazard reviews, risk matrix scoring, control hierarchy documentation, and residual risk tracking'),
    ('ehs-regulatory-reporting-automation', 'Automate EHS regulatory reporting processes including Tier II chemical reporting, TRI Form R submissions, OSHA 300A posting, and state-specific environmental compliance reports'),
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
