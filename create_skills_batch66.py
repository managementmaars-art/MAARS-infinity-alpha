
import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # Marine and maritime technology
    ('maritime-ops-platform', 'Maritime operations platform - vessel management, voyage optimization, port calls, crew management'),
    ('vessel-tracking-platform', 'Vessel tracking and monitoring - AIS data, satellite tracking, ETA prediction, fleet visibility'),
    ('marine-cargo-management', 'Marine cargo management - bill of lading, container tracking, stowage planning, dangerous goods'),
    ('port-terminal-os', 'Port terminal operating system - berth planning, yard management, gate automation, equipment control'),
    ('maritime-safety-platform', 'Maritime safety platform - ISM code, safety management system, incident reporting, SOLAS compliance'),
    ('marine-engineering-platform', 'Marine engineering technology - PMS, machinery monitoring, class surveys, dry-dock management'),
    ('shipping-freight-platform', 'Shipping freight platform - chartering, freight rates, spot market, FFA, route optimization'),
    ('offshore-operations-tech', 'Offshore operations technology - rig management, subsea systems, ROV operations, riser monitoring'),
    ('fisheries-management-tech', 'Fisheries management technology - catch tracking, quota management, vessel monitoring, licensing'),
    ('naval-architecture-software', 'Naval architecture software - hull design, stability calculations, structural analysis, CFD'),
    # Environmental and sustainability technology
    ('environmental-compliance-platform', 'Environmental compliance platform - permit management, monitoring, reporting, regulatory compliance'),
    ('esg-data-platform', 'ESG data platform - emission tracking, social metrics, governance indicators, reporting standards'),
    ('carbon-capture-platform', 'Carbon capture technology platform - CCUS, monitoring, verification, storage management'),
    ('circular-economy-platform', 'Circular economy technology platform - material flow, product lifecycle, take-back, recycling'),
    ('biodiversity-tech-platform', 'Biodiversity technology platform - habitat monitoring, species tracking, conservation metrics'),
    ('water-resource-management', 'Water resource management technology - watershed modeling, allocation, conservation, pricing'),
    ('air-quality-platform', 'Air quality monitoring platform - sensor networks, dispersion modeling, compliance reporting'),
    ('waste-management-advanced', 'Waste management advanced technology - smart bins, route optimization, sorting, compliance tracking'),
    ('climate-risk-platform', 'Climate risk and resilience platform - physical risk modeling, transition risk, scenario analysis'),
    ('renewable-certificates', 'Renewable energy certificates platform - REC trading, I-REC, REGO, verification, registry'),
    # Digital health and wellness
    ('mental-health-platform-advanced', 'Mental health technology platform advanced - digital therapeutics, CBT tools, crisis support'),
    ('chronic-disease-management', 'Chronic disease management platform - care plans, medication adherence, remote monitoring, coaching'),
    ('nutrition-health-platform', 'Nutrition and health technology platform - dietary assessment, meal planning, metabolomics, coaching'),
    ('sleep-technology-platform', 'Sleep technology platform - wearable integration, CBT-I, sleep scoring, clinical analytics'),
    ('women-health-platform', 'Women\'s health technology platform - fertility tracking, pregnancy monitoring, menopause care, PCOS'),
    ('pediatric-health-platform', 'Pediatric health technology - growth tracking, immunizations, developmental screening, parenting'),
    ('elder-care-technology', 'Elder care technology platform - fall detection, cognitive monitoring, caregiver coordination, aging'),
    ('rehabilitation-platform', 'Rehabilitation technology platform - exercise therapy, progress tracking, remote PT, outcome measures'),
    ('addiction-treatment-tech', 'Addiction treatment technology - recovery support, MAT, peer support, relapse prevention'),
    ('preventive-health-platform', 'Preventive health platform - health risk assessment, screening reminders, wellness programs, biometrics'),
    # Smart city and urban tech
    ('smart-city-os', 'Smart city operating system - data integration, service orchestration, citizen engagement, KPIs'),
    ('urban-mobility-advanced', 'Urban mobility advanced technology - MaaS, UTMC, traffic signal optimization, congestion pricing'),
    ('smart-parking-platform', 'Smart parking platform - real-time availability, dynamic pricing, EV charging, enforcement'),
    ('public-transit-platform', 'Public transit technology platform - GTFS, real-time tracking, fare systems, passenger information'),
    ('city-infrastructure-monitoring', 'City infrastructure monitoring - bridges, roads, utilities sensor networks, predictive maintenance'),
    ('urban-planning-digital', 'Digital urban planning platform - 3D modeling, zoning simulation, impact assessment, public engagement'),
    ('city-services-platform', 'City services digital platform - permit applications, payments, complaints, citizen portal'),
    ('smart-lighting-platform', 'Smart lighting platform - adaptive control, energy management, fault detection, pole sensors'),
    ('emergency-services-tech', 'Emergency services technology - CAD, resource dispatch, incident management, first responder tools'),
    ('public-safety-analytics', 'Public safety analytics platform - crime analysis, predictive tools, resource allocation, dashboards'),
    # Legal and compliance technology advanced
    ('compliance-automation-platform', 'Compliance automation platform - control testing, evidence collection, audit management, reporting'),
    ('regulatory-change-platform', 'Regulatory change management platform - tracking, impact analysis, implementation, attestation'),
    ('litigation-management', 'Litigation management platform - matter tracking, e-billing, outside counsel, risk analytics'),
    ('privacy-tech-platform', 'Privacy technology platform - consent management, DSR automation, data mapping, DPIA, breach response'),
    ('intellectual-property-platform', 'Intellectual property management platform - patent portfolio, trademark, licensing, renewals'),
    ('corporate-governance-platform', 'Corporate governance technology platform - board management, entity management, ESG reporting'),
    ('legal-research-platform', 'Legal research technology platform - case law, statute search, regulatory databases, AI analysis'),
    ('contract-automation-advanced', 'Contract automation advanced - template intelligence, NLP extraction, workflow, execution, analysis'),
    ('whistleblower-platform', 'Whistleblower and ethics reporting platform - anonymous reporting, case management, investigation'),
    ('sanctions-compliance-platform', 'Sanctions compliance technology - screening automation, watchlist management, adverse media'),
    # HR technology advanced
    ('talent-acquisition-platform', 'Talent acquisition technology platform - ATS, sourcing, screening, assessment, onboarding'),
    ('performance-management-platform', 'Performance management technology platform - OKRs, reviews, feedback, calibration, analytics'),
    ('learning-experience-platform', 'Learning experience platform - personalized learning, skills graph, content curation, social learning'),
    ('compensation-benchmarking', 'Compensation benchmarking platform - salary surveys, pay equity analysis, merit modeling, total rewards'),
    ('workforce-analytics-platform', 'Workforce analytics advanced platform - people analytics, attrition prediction, capacity planning'),
    ('employee-wellbeing-platform', 'Employee wellbeing technology platform - mental health, financial wellness, benefits navigation'),
    ('dei-analytics-platform', 'DEI analytics and reporting platform - pay equity, representation metrics, inclusion surveys'),
    ('succession-planning-tech', 'Succession planning technology - talent assessment, development tracking, bench strength analytics'),
    ('gig-workforce-platform', 'Gig and contingent workforce platform - sourcing, engagement, payments, compliance, analytics'),
    ('hr-service-delivery', 'HR service delivery technology - case management, knowledge base, chatbot, self-service, analytics'),
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
