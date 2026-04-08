import os

base = r"c:\Users\mirza\MAARS-Command\.claude\skills"

# Domain: Specialty Retail
skills = [
    {"name": "retail-merchandise-planning", "description": "Develop retail merchandise plans including open-to-buy budgets, assortment depth, and seasonal allocation strategies."},
    {"name": "retail-visual-merchandising", "description": "Design and execute visual merchandising programs including planogram compliance, fixture layouts, and window display management."},
    {"name": "retail-inventory-replenishment", "description": "Automate retail inventory replenishment using min-max triggers, vendor-managed inventory, and sell-through analytics."},
    {"name": "retail-loss-prevention", "description": "Manage retail loss prevention programs including shrinkage audits, exception reporting, CCTV oversight, and employee awareness training."},
    {"name": "retail-store-operations", "description": "Oversee specialty retail store operations including labor scheduling, daily opening procedures, cash management, and KPI tracking."},
    {"name": "retail-loyalty-programs", "description": "Design and operate retail loyalty programs including points mechanics, tier management, personalized offers, and redemption analytics."},
    {"name": "retail-omnichannel-fulfillment", "description": "Coordinate omnichannel retail fulfillment including BOPIS, ship-from-store, curbside pickup, and inventory reservation logic."},
    {"name": "retail-private-label-development", "description": "Develop private label retail products including vendor sourcing, product specification, packaging design, and margin management."},
    {"name": "retail-markdown-optimization", "description": "Optimize retail markdown cadence using sell-through thresholds, margin floor constraints, and end-of-season clearance planning."},
    {"name": "retail-franchise-management", "description": "Manage retail franchise networks including franchisee onboarding, brand standards enforcement, royalty tracking, and field support."},
]

# Domain: Urban Planning / Smart Cities
skills += [
    {"name": "land-use-planning", "description": "Develop land use plans including zoning code updates, comprehensive plan amendments, and community engagement facilitation."},
    {"name": "smart-city-iot-ops", "description": "Operate smart city IoT infrastructure including sensor networks, data platform integration, and city operations center management."},
    {"name": "urban-mobility-planning", "description": "Plan urban mobility solutions including multimodal corridor design, demand modeling, and transit-oriented development analysis."},
    {"name": "affordable-housing-programs", "description": "Manage affordable housing programs including LIHTC project financing, deed restriction monitoring, and applicant waitlist administration."},
    {"name": "urban-resilience-planning", "description": "Develop urban climate resilience plans including heat island mitigation, flood adaptation, and critical infrastructure hardening strategies."},
    {"name": "city-budget-planning", "description": "Coordinate municipal budget planning including departmental request review, revenue forecasting, and council presentation preparation."},
    {"name": "urban-economic-development", "description": "Manage urban economic development programs including business attraction incentives, enterprise zones, and workforce pipeline coordination."},
    {"name": "public-space-management", "description": "Oversee public space operations including park programming, plaza maintenance contracts, events permitting, and user experience monitoring."},
    {"name": "smart-parking-management", "description": "Operate smart parking systems including dynamic pricing, occupancy monitoring, citation management, and revenue reporting."},
    {"name": "gis-urban-analytics", "description": "Deploy GIS analytics for urban planning including spatial equity analysis, service coverage mapping, and demographic change modeling."},
]

# Domain: Food & Beverage Manufacturing
skills += [
    {"name": "food-safety-management-systems", "description": "Implement food safety management systems including HACCP plans, HARPC compliance, and FSMA preventive control programs."},
    {"name": "food-production-scheduling", "description": "Schedule food and beverage production runs including changeover optimization, allergen sequencing, and co-pack coordination."},
    {"name": "recipe-formula-management", "description": "Manage food product formulas including ingredient specifications, nutritional calculations, label compliance, and version control."},
    {"name": "food-quality-control", "description": "Execute food quality control programs including sensory evaluation, micro testing protocols, shelf-life studies, and supplier COA review."},
    {"name": "food-regulatory-compliance", "description": "Navigate food regulatory compliance including FDA registration, nutrition labeling, organic certification, and allergen declaration."},
    {"name": "food-packaging-ops", "description": "Manage food packaging operations including filling line efficiency, primary and secondary packaging specifications, and sustainability targets."},
    {"name": "food-cold-chain-management", "description": "Manage food cold chain logistics including temperature monitoring, carrier qualification, shelf-life allocation, and recall readiness."},
    {"name": "food-co-manufacturing-ops", "description": "Operate food co-manufacturing partnerships including capacity booking, quality oversight, toll processing agreements, and audit programs."},
    {"name": "food-product-development", "description": "Manage food product development from ideation through scale-up including sensory panels, market testing, and commercialization handoff."},
    {"name": "beverage-brewing-distilling-ops", "description": "Operate brewing and distilling production including fermentation monitoring, aging programs, blending, and TTB compliance reporting."},
]

# Domain: Insurance Technology / Insurtech
skills += [
    {"name": "insurtech-product-configuration", "description": "Configure insurance product rules including coverage logic, rating factors, eligibility rules, and form management within policy administration systems."},
    {"name": "digital-underwriting-automation", "description": "Automate digital underwriting workflows including data enrichment, risk scoring, appetite matching, and straight-through processing."},
    {"name": "claims-automation-ops", "description": "Operate claims automation platforms including FNOL intake, coverage verification, damage estimation, and settlement payment processing."},
    {"name": "insurance-api-integration", "description": "Manage insurance API integrations including carrier connectivity, data exchange standards, and third-party data vendor onboarding."},
    {"name": "telematics-ubi-programs", "description": "Operate usage-based insurance telematics programs including device provisioning, driving behavior scoring, and discount calculation."},
    {"name": "insurtech-fraud-detection", "description": "Deploy fraud detection analytics for insurance including network link analysis, claim anomaly scoring, and SIU referral workflows."},
    {"name": "embedded-insurance-ops", "description": "Manage embedded insurance distribution including partner API setup, white-label product configuration, and revenue sharing reconciliation."},
    {"name": "parametric-insurance-programs", "description": "Design and operate parametric insurance programs including trigger definition, index data sourcing, and automated payout execution."},
    {"name": "insurance-data-platform-ops", "description": "Operate insurance data platforms including policy data warehousing, actuarial data feeds, and regulatory reporting pipelines."},
    {"name": "digital-broker-platform-ops", "description": "Manage digital broker platform operations including carrier market access, comparative quoting workflows, and policy servicing automation."},
]

# Domain: Renewable Energy Development
skills += [
    {"name": "solar-project-development", "description": "Develop utility-scale solar projects from site identification through interconnection, permitting, financing, and commercial operation."},
    {"name": "wind-energy-development", "description": "Manage wind energy project development including wind resource assessment, turbine layout optimization, and offtake negotiation."},
    {"name": "energy-storage-development", "description": "Develop battery energy storage projects including site selection, interconnection strategy, revenue stacking analysis, and EPC procurement."},
    {"name": "renewable-interconnection-mgmt", "description": "Manage grid interconnection processes for renewable projects including queue position management, study milestones, and upgrade cost allocation."},
    {"name": "power-purchase-agreement-ops", "description": "Structure and manage power purchase agreements including offtake negotiation, credit assessment, curtailment provisions, and performance guarantees."},
    {"name": "renewable-project-finance", "description": "Execute renewable energy project financing including tax equity structures, debt placement, sponsor equity, and financial model management."},
    {"name": "renewable-asset-management", "description": "Manage operating renewable energy assets including O&M contractor oversight, performance monitoring, revenue optimization, and investor reporting."},
    {"name": "rec-carbon-credit-management", "description": "Track and monetize renewable energy certificates and carbon credits including registry accounts, retirement tracking, and buyer contract fulfillment."},
    {"name": "community-solar-program-ops", "description": "Operate community solar subscription programs including subscriber enrollment, bill credit allocation, and utility program compliance."},
    {"name": "renewable-permitting-compliance", "description": "Navigate renewable energy permitting including NEPA review, endangered species consultation, cultural resource surveys, and construction permits."},
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
