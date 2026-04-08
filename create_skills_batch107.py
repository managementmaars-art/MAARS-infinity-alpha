import os

base = r"c:\Users\mirza\MAARS-Command\.claude\skills"

# Domain: Aerospace & Defense Manufacturing
skills = [
    {"name": "aerospace-program-lifecycle", "description": "Manage aerospace program lifecycles from concept definition through PDR, CDR, production, and sustainment phases."},
    {"name": "as9100-quality-management", "description": "Implement and maintain AS9100 quality management systems including FAIR, DCAI, and first article inspection processes."},
    {"name": "aerospace-supply-chain-risk", "description": "Assess and mitigate aerospace supply chain risks including sole-source dependencies, lead time variability, and counterfeit parts prevention."},
    {"name": "defense-export-compliance", "description": "Manage ITAR and EAR export compliance programs including license applications, technology control plans, and employee training."},
    {"name": "missile-systems-integration", "description": "Coordinate missile and guided munitions systems integration including interface control, test range coordination, and safety reviews."},
    {"name": "aircraft-mro-management", "description": "Manage aircraft maintenance, repair, and overhaul operations including workscope planning, airworthiness directives, and hangar utilization."},
    {"name": "defense-cost-estimating", "description": "Develop parametric and bottoms-up cost estimates for defense programs including should-cost analysis and independent cost reviews."},
    {"name": "radar-systems-sustainment", "description": "Sustain radar and electronic warfare systems including obsolescence management, software updates, and depot repair programs."},
    {"name": "spacecraft-operations", "description": "Operate spacecraft missions including ground station command, telemetry monitoring, anomaly resolution, and orbital maneuver planning."},
    {"name": "defense-test-evaluation", "description": "Plan and execute defense test and evaluation programs including DT and OT coordination, range scheduling, and test report generation."},
]

# Domain: Agricultural Technology / Precision Agriculture
skills += [
    {"name": "precision-farming-ops", "description": "Deploy precision farming operations including variable rate application, GPS-guided machinery, and field data management platforms."},
    {"name": "crop-yield-analytics", "description": "Analyze crop yield data using remote sensing, soil mapping, and weather integration to generate field-level performance insights."},
    {"name": "irrigation-management-systems", "description": "Manage smart irrigation systems including soil moisture monitoring, ET-based scheduling, and water use efficiency reporting."},
    {"name": "agri-supply-chain-traceability", "description": "Implement agricultural supply chain traceability from field to retail including GAP certification, lot tracking, and recall readiness."},
    {"name": "livestock-monitoring-ops", "description": "Operate livestock monitoring systems including wearable sensor data, health alert triage, and herd performance benchmarking."},
    {"name": "agri-input-procurement", "description": "Manage agricultural input procurement including seed, fertilizer, and chemical sourcing with contract management and market timing."},
    {"name": "farm-financial-planning", "description": "Develop farm financial plans including enterprise budgets, cash flow projections, FSA program optimization, and lender reporting."},
    {"name": "crop-insurance-management", "description": "Manage crop insurance programs including policy selection, acreage reporting, loss adjustment preparation, and indemnity tracking."},
    {"name": "agri-drone-operations", "description": "Coordinate agricultural drone operations including flight planning, crop scouting missions, spray applications, and FAA compliance."},
    {"name": "carbon-farming-programs", "description": "Enroll and manage carbon farming programs including soil carbon measurement, practice verification, and credit monetization."},
]

# Domain: Hospitality / Hotel Operations
skills += [
    {"name": "hotel-revenue-management", "description": "Optimize hotel revenue through dynamic room pricing, channel mix management, and demand forecasting across segments."},
    {"name": "property-management-system-ops", "description": "Operate hotel PMS platforms including reservation management, front desk workflows, housekeeping integration, and night audit processes."},
    {"name": "hotel-food-beverage-ops", "description": "Manage hotel food and beverage operations including outlet P&L, banquet event orders, menu engineering, and staffing optimization."},
    {"name": "hotel-group-sales", "description": "Develop group sales programs including RFP response, contract negotiation, rooming list management, and post-event billing."},
    {"name": "guest-experience-management", "description": "Design and manage guest experience programs including pre-arrival personalization, on-property service recovery, and loyalty integration."},
    {"name": "hotel-spa-wellness-ops", "description": "Operate hotel spa and wellness facilities including appointment scheduling, therapist productivity, retail sales, and membership programs."},
    {"name": "hospitality-procurement", "description": "Manage hospitality procurement including FF&E sourcing, OS&E purchasing, vendor contracts, and sustainability certifications."},
    {"name": "hotel-digital-marketing", "description": "Execute hotel digital marketing including OTA optimization, direct booking campaigns, reputation management, and metasearch bidding."},
    {"name": "convention-center-management", "description": "Manage convention center operations including event booking, setup coordination, AV services, and exhibitor services."},
    {"name": "hotel-asset-management", "description": "Perform hotel asset management including owner-operator relations, capital planning, brand compliance audits, and disposition strategy."},
]

# Domain: Environmental Consulting / Remediation
skills += [
    {"name": "site-investigation-management", "description": "Manage Phase I and Phase II environmental site investigations including sampling design, lab coordination, and regulatory reporting."},
    {"name": "remediation-design-ops", "description": "Design and implement site remediation systems including pump-and-treat, in-situ treatment, and monitored natural attenuation programs."},
    {"name": "environmental-permitting", "description": "Navigate environmental permitting processes including air, water, and waste permits across federal and state regulatory agencies."},
    {"name": "hazmat-waste-management", "description": "Manage hazardous waste programs including waste characterization, manifest tracking, transporter qualification, and TSDF compliance."},
    {"name": "environmental-compliance-auditing", "description": "Conduct environmental compliance audits including multimedia assessments, findings tracking, corrective action management, and follow-up verification."},
    {"name": "ecological-risk-assessment", "description": "Perform ecological risk assessments including receptor identification, exposure pathway analysis, and risk characterization for contaminated sites."},
    {"name": "brownfield-redevelopment", "description": "Manage brownfield redevelopment projects including liability allocation, cleanup cost estimation, regulatory closure, and grant funding."},
    {"name": "air-emissions-management", "description": "Track and manage facility air emissions including HAP and GHG inventories, Title V compliance, and emission reduction project tracking."},
    {"name": "environmental-litigation-support", "description": "Support environmental litigation including expert report preparation, cost allocation modeling, and natural resource damage assessments."},
    {"name": "climate-risk-assessment-env", "description": "Assess physical climate risks for facilities and assets including flood, wildfire, sea level rise, and extreme heat exposure modeling."},
]

# Domain: Private Equity / Venture Capital Operations
skills += [
    {"name": "deal-sourcing-pipeline", "description": "Build and manage deal sourcing pipelines including intermediary relationships, proprietary outreach, and CRM funnel management."},
    {"name": "pe-due-diligence-coordination", "description": "Coordinate private equity due diligence workstreams including financial, legal, commercial, and operational advisor management."},
    {"name": "investment-committee-management", "description": "Manage investment committee processes including memo preparation, presentation scheduling, voting documentation, and approval tracking."},
    {"name": "portfolio-company-monitoring", "description": "Monitor portfolio company performance including KPI dashboards, board reporting packages, and covenant compliance tracking."},
    {"name": "value-creation-planning", "description": "Develop and track value creation plans for portfolio companies including operational improvement initiatives and milestone accountability."},
    {"name": "fund-administration-pe", "description": "Administer private equity fund operations including capital calls, distributions, NAV calculations, and LP statement generation."},
    {"name": "exit-process-management", "description": "Manage portfolio company exit processes including sale process coordination, management presentations, and buyer diligence response."},
    {"name": "vc-portfolio-analytics", "description": "Analyze venture capital portfolio performance including TVPI, DPI, IRR attribution, and mark-to-market valuation modeling."},
    {"name": "lp-relations-management", "description": "Manage limited partner relations including quarterly reporting, annual meeting preparation, and co-investment opportunity communication."},
    {"name": "pe-fund-formation", "description": "Support private equity fund formation including LPA negotiation, regulatory filing, placement agent management, and closing logistics."},
]

os.makedirs(base, exist_ok=True)

SKILL_TEMPLATE = '''---
name: {name}
description: {description}
---

## Overview
{description}

## Core Framework
- Analyze requirements and constraints specific to {name}
- Design workflows aligned to industry best practices
- Implement automation and intelligence layers
- Monitor outcomes and continuously improve

## Key Prompts
- "Initiate {name} workflow for [context]"
- "Analyze current state of {name} and identify gaps"
- "Generate recommendations for {name} optimization"
- "Create detailed plan for {name} execution"

## Best Practices
- Always validate inputs against domain-specific regulatory and compliance requirements
- Maintain audit trails for all automated decisions
- Escalate ambiguous or high-risk decisions to human reviewers
- Use structured data formats for downstream system integration

## Common Patterns
- Intake and triage incoming work items
- Route to appropriate specialist or automated handler
- Track status and SLA compliance
- Generate reports and dashboards for stakeholders

## Models to Use
- Complex analysis and strategy: claude-opus-4-6
- Standard workflows and generation: claude-sonnet-4-6
- High-volume classification and routing: claude-haiku-4-5-20251001
'''

count = 0
for skill in skills:
    skill_dir = os.path.join(base, skill["name"])
    os.makedirs(skill_dir, exist_ok=True)
    skill_path = os.path.join(skill_dir, "SKILL.md")
    with open(skill_path, "w", encoding="utf-8") as f:
        f.write(SKILL_TEMPLATE.format(name=skill["name"], description=skill["description"]))
    count += 1

print(f"Done: {count} skills")
