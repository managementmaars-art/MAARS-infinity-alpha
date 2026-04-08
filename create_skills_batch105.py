import os

base = r"c:\Users\mirza\MAARS-Command\.claude\skills"

# Domain: Wealth Management / Private Banking
skills = [
    {"name": "wealth-client-onboarding", "description": "Orchestrate high-net-worth client onboarding including KYC, suitability assessments, and account setup workflows."},
    {"name": "investment-policy-statement", "description": "Draft and maintain Investment Policy Statements aligned to client risk tolerance, time horizon, and return objectives."},
    {"name": "portfolio-rebalancing-automation", "description": "Automate portfolio drift detection and rebalancing execution within IPS guidelines and tax constraints."},
    {"name": "alternative-investments-ops", "description": "Manage alternative investment operations including hedge fund subscriptions, PE capital calls, and illiquid asset tracking."},
    {"name": "trust-estate-administration", "description": "Administer trust and estate accounts including distribution tracking, beneficiary management, and fiduciary compliance."},
    {"name": "private-banking-credit", "description": "Structure and monitor private banking credit facilities including Lombard loans, mortgages, and securities-backed lending."},
    {"name": "family-office-reporting", "description": "Produce consolidated family office reporting across custodians, asset classes, and entity structures."},
    {"name": "tax-loss-harvesting", "description": "Identify and execute tax-loss harvesting opportunities while managing wash-sale rules and portfolio integrity."},
    {"name": "wealth-fee-billing", "description": "Automate AUM-based fee calculations, billing cycles, invoice generation, and revenue reconciliation."},
    {"name": "philanthropy-advisory", "description": "Support philanthropic planning including donor-advised funds, private foundations, and charitable giving strategies."},
]

# Domain: Automotive OEM Manufacturing
skills += [
    {"name": "vehicle-program-management", "description": "Manage vehicle development programs across concept, design, engineering, validation, and launch phases using gate reviews."},
    {"name": "bill-of-materials-automotive", "description": "Maintain multi-level automotive BOM structures across trims, options, and regional variants with cost rollup."},
    {"name": "supplier-tooling-management", "description": "Track supplier tooling ownership, amortization schedules, and capacity agreements across the supply base."},
    {"name": "warranty-claims-processing", "description": "Process warranty claims from dealer submission through root-cause analysis, part returns, and reimbursement."},
    {"name": "homologation-compliance", "description": "Manage vehicle homologation and regulatory type approval across global markets including emissions and safety standards."},
    {"name": "automotive-quality-gates", "description": "Implement Production Part Approval Process (PPAP) and Advanced Product Quality Planning (APQP) across new model launches."},
    {"name": "dealer-network-management", "description": "Manage dealer network performance including sales targets, training compliance, facility standards, and franchise agreements."},
    {"name": "vehicle-configuration-rules", "description": "Define and enforce option compatibility rules, constraint matrices, and order-to-production feasibility checks."},
    {"name": "automotive-recall-management", "description": "Coordinate safety recall campaigns including NHTSA/regulatory notifications, remedy part production, and dealer repair completion."},
    {"name": "connected-vehicle-telematics", "description": "Manage connected vehicle data pipelines, OTA software update deployment, and telematics service operations."},
]

# Domain: Pharmaceutical Retail / Specialty Pharmacy
skills += [
    {"name": "specialty-pharmacy-intake", "description": "Automate specialty pharmacy patient intake including benefit investigation, prior authorization, and hub enrollment."},
    {"name": "prior-authorization-management", "description": "Manage prior authorization workflows from submission through appeal, denial override, and peer-to-peer review."},
    {"name": "medication-therapy-management", "description": "Deliver medication therapy management services including comprehensive medication reviews and targeted interventions."},
    {"name": "cold-chain-dispensing", "description": "Manage cold-chain dispensing operations including temperature monitoring, specialized packaging, and carrier coordination."},
    {"name": "patient-adherence-programs", "description": "Design and operate patient adherence programs using refill reminders, copay assistance, and clinical outreach."},
    {"name": "pharmacy-benefit-adjudication", "description": "Process pharmacy benefit claims through real-time adjudication, formulary checking, and plan accumulator management."},
    {"name": "controlled-substance-tracking", "description": "Maintain DEA-compliant controlled substance tracking including EPCS, inventory reconciliation, and diversion monitoring."},
    {"name": "specialty-drug-distribution", "description": "Manage specialty drug distribution including limited distribution network compliance, hub dispensing, and 3PL coordination."},
    {"name": "pharmacy-accreditation-ops", "description": "Maintain URAC and ACHC accreditation standards across specialty pharmacy clinical and operational functions."},
    {"name": "biosimilar-conversion-program", "description": "Execute biosimilar conversion programs including payer strategy, prescriber engagement, and patient transition management."},
]

# Domain: Federal Government Contracting
skills += [
    {"name": "proposal-development-federal", "description": "Develop compliant federal proposals including PWS/SOW response, price volumes, and color team review management."},
    {"name": "contract-administration-far", "description": "Administer federal contracts under FAR/DFARS including modification processing, deliverable tracking, and contracting officer correspondence."},
    {"name": "cost-accounting-standards", "description": "Maintain CAS compliance including disclosure statements, cost allocation methodologies, and DCAA audit readiness."},
    {"name": "earned-value-management", "description": "Implement EVMS on federal programs including WBS development, baseline control, variance analysis, and IBR preparation."},
    {"name": "federal-subcontract-management", "description": "Manage federal subcontract flowdowns, small business subcontracting plans, and consent-to-subcontract processes."},
    {"name": "security-clearance-management", "description": "Administer facility and personnel security clearance programs including e-QIP submissions, visit authorizations, and FSO duties."},
    {"name": "government-property-management", "description": "Track and manage government-furnished property and equipment under federal contracts including annual inventory and loss reporting."},
    {"name": "federal-invoicing-wawf", "description": "Process federal contract invoices through WAWF including milestone billing, cost-plus vouchers, and prompt payment compliance."},
    {"name": "bid-protest-response", "description": "Coordinate bid protest responses to GAO and Court of Federal Claims including agency report preparation and legal coordination."},
    {"name": "small-business-set-aside", "description": "Navigate small business set-aside programs including 8(a), SDVOSB, HUBZone, and WOSB certifications and compliance."},
]

# Domain: Commercial Real Estate Development
skills += [
    {"name": "cre-deal-underwriting", "description": "Underwrite commercial real estate acquisitions including pro forma modeling, cap rate analysis, and debt sizing."},
    {"name": "development-entitlement", "description": "Manage entitlement processes including zoning applications, variance requests, environmental review, and public hearings."},
    {"name": "construction-draw-management", "description": "Process construction loan draws including inspector certifications, lien waiver collection, and lender reporting."},
    {"name": "tenant-leasing-management", "description": "Manage commercial tenant leasing from LOI through lease execution including deal tracking and commission management."},
    {"name": "property-asset-management", "description": "Operate commercial properties including NOI optimization, capital expenditure planning, and investor reporting."},
    {"name": "cre-fund-administration", "description": "Administer real estate funds including capital call management, waterfall calculations, and LP reporting."},
    {"name": "environmental-due-diligence", "description": "Manage Phase I/II environmental assessments, remediation oversight, and regulatory compliance for CRE transactions."},
    {"name": "cre-debt-placement", "description": "Structure and place commercial real estate debt including agency loans, CMBS execution, and mezzanine financing."},
    {"name": "space-planning-tenant-improvements", "description": "Coordinate space planning, TI construction management, and landlord work letter negotiations for commercial tenants."},
    {"name": "cre-market-analytics", "description": "Analyze commercial real estate markets including vacancy trends, rent comps, absorption data, and submarket forecasting."},
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
