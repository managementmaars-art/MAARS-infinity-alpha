import os

base = r"c:\Users\mirza\MAARS-Command\.claude\skills"

# Domain: Supply Chain Technology / Logistics Tech
skills = [
    {"name": "tms-platform-operations", "description": "Operate transportation management system platforms including carrier selection, load tendering, freight audit, and shipment visibility."},
    {"name": "wms-platform-operations", "description": "Manage warehouse management system operations including slotting optimization, pick path sequencing, labor management, and inventory accuracy."},
    {"name": "supply-chain-control-tower", "description": "Deploy supply chain control tower solutions including multi-tier visibility, exception alerting, and cross-functional response coordination."},
    {"name": "last-mile-delivery-ops", "description": "Optimize last-mile delivery operations including route optimization, driver dispatch, proof of delivery, and customer notification workflows."},
    {"name": "supply-chain-network-design", "description": "Design supply chain networks including DC footprint optimization, flow path modeling, and total landed cost analysis."},
    {"name": "demand-sensing-analytics", "description": "Deploy demand sensing analytics using POS data, external signals, and ML models to improve short-horizon forecast accuracy."},
    {"name": "freight-procurement-ops", "description": "Manage freight procurement programs including RFP execution, rate benchmarking, carrier contract management, and mode optimization."},
    {"name": "supply-chain-risk-platform", "description": "Operate supply chain risk monitoring platforms including supplier financial health tracking, geopolitical alerts, and disruption scenario modeling."},
    {"name": "reverse-logistics-management", "description": "Manage reverse logistics operations including returns intake, disposition routing, refurbishment workflows, and recovery value tracking."},
    {"name": "supply-chain-data-integration", "description": "Integrate supply chain data streams including EDI, API connectivity, master data management, and cross-system data quality governance."},
]

# Domain: Construction Technology / ConTech
skills += [
    {"name": "bim-project-coordination", "description": "Coordinate Building Information Modeling workflows including model federation, clash detection, and design review management."},
    {"name": "construction-project-controls", "description": "Implement construction project controls including schedule management, cost tracking, earned value, and change order analytics."},
    {"name": "construction-safety-management", "description": "Manage construction site safety programs including hazard identification, toolbox talks, incident reporting, and OSHA compliance tracking."},
    {"name": "construction-procurement-ops", "description": "Manage construction procurement including subcontractor bidding, scope of work development, contract execution, and lien waiver collection."},
    {"name": "field-inspection-management", "description": "Coordinate field inspection programs including punch list management, deficiency tracking, photo documentation, and closeout verification."},
    {"name": "construction-document-control", "description": "Manage construction document control including drawing logs, submittal tracking, RFI workflows, and specification compliance."},
    {"name": "prefab-modular-construction-ops", "description": "Manage prefabrication and modular construction operations including factory scheduling, quality inspection, and site coordination."},
    {"name": "construction-cost-estimating", "description": "Develop construction cost estimates including quantity takeoffs, unit cost databases, GC markup modeling, and value engineering."},
    {"name": "construction-equipment-management", "description": "Track and optimize construction equipment fleets including utilization monitoring, maintenance scheduling, and rental cost management."},
    {"name": "smart-building-commissioning", "description": "Commission smart building systems including BAS integration, IoT sensor validation, energy performance verification, and occupant handover."},
]

# Domain: Maritime / Shipping Operations
skills += [
    {"name": "vessel-operations-management", "description": "Manage commercial vessel operations including voyage planning, port scheduling, crew management, and flag state compliance."},
    {"name": "maritime-cargo-operations", "description": "Coordinate maritime cargo operations including stowage planning, cargo documentation, dangerous goods compliance, and port agency management."},
    {"name": "ship-technical-management", "description": "Oversee ship technical management including planned maintenance systems, drydock scheduling, class surveys, and defect resolution."},
    {"name": "maritime-charter-management", "description": "Manage vessel chartering including fixture negotiation, charter party administration, hire payments, and laytime calculations."},
    {"name": "port-terminal-operations", "description": "Operate port and terminal facilities including berth scheduling, crane productivity, gate operations, and yard capacity management."},
    {"name": "maritime-fuel-management", "description": "Manage marine fuel operations including bunker procurement, fuel quality testing, consumption monitoring, and emissions compliance."},
    {"name": "maritime-insurance-claims", "description": "Manage maritime insurance and P&I club claims including hull damage, cargo loss, collision liability, and survey coordination."},
    {"name": "maritime-regulatory-compliance", "description": "Navigate maritime regulatory compliance including IMO conventions, ISM code, ISPS security, and flag/port state inspections."},
    {"name": "container-fleet-management", "description": "Manage container fleet operations including equipment positioning, repair programs, lease portfolio management, and utilization tracking."},
    {"name": "maritime-decarbonization-ops", "description": "Implement maritime decarbonization programs including CII rating management, alternative fuel transition planning, and EU ETS compliance."},
]

# Domain: EdTech / Online Education
skills += [
    {"name": "lms-platform-administration", "description": "Administer learning management system platforms including course publishing, enrollment workflows, progress tracking, and integrations."},
    {"name": "online-course-development", "description": "Develop online courses including instructional design, multimedia production, assessment design, and accessibility compliance."},
    {"name": "edtech-learner-analytics", "description": "Analyze learner engagement and performance data to identify at-risk students, optimize content, and improve completion rates."},
    {"name": "corporate-learning-programs", "description": "Design and operate corporate learning programs including skill gap analysis, curriculum mapping, and training ROI measurement."},
    {"name": "edtech-product-management", "description": "Manage EdTech product development including feature prioritization, educator feedback loops, and learning outcome measurement."},
    {"name": "virtual-classroom-operations", "description": "Operate virtual classroom environments including live session facilitation, breakout coordination, and synchronous learning support."},
    {"name": "edtech-content-licensing", "description": "Manage educational content licensing including publisher agreements, copyright compliance, open educational resources, and content curation."},
    {"name": "student-enrollment-marketing", "description": "Execute student enrollment marketing campaigns including funnel analytics, digital advertising, and application conversion optimization."},
    {"name": "competency-based-education-ops", "description": "Implement competency-based education programs including mastery assessment design, pacing flexibility, and credential mapping."},
    {"name": "edtech-partnerships", "description": "Develop EdTech institutional partnerships including university agreements, employer tuition programs, and workforce training contracts."},
]

# Domain: Cybersecurity Services
skills += [
    {"name": "soc-operations-management", "description": "Manage security operations center functions including alert triage, incident escalation, threat intelligence integration, and analyst workflow optimization."},
    {"name": "penetration-testing-ops", "description": "Coordinate penetration testing engagements including scoping, rules of engagement, report delivery, and remediation tracking."},
    {"name": "vulnerability-management-program", "description": "Operate vulnerability management programs including scanner deployment, CVSS prioritization, SLA tracking, and patch verification."},
    {"name": "incident-response-management", "description": "Manage cybersecurity incident response including containment playbooks, forensic coordination, stakeholder communication, and post-incident review."},
    {"name": "zero-trust-architecture", "description": "Implement zero trust security architectures including identity-based access, microsegmentation, continuous verification, and policy enforcement."},
    {"name": "cloud-security-posture-mgmt", "description": "Manage cloud security posture including misconfiguration detection, compliance benchmarking, drift remediation, and multi-cloud governance."},
    {"name": "security-awareness-training", "description": "Design and operate security awareness training programs including phishing simulations, role-based modules, and behavior change metrics."},
    {"name": "third-party-risk-cyber", "description": "Assess and manage third-party cybersecurity risks including vendor questionnaires, continuous monitoring, and contractual security requirements."},
    {"name": "data-loss-prevention-ops", "description": "Operate data loss prevention programs including policy configuration, endpoint and email controls, alert investigation, and exception management."},
    {"name": "cyber-threat-intelligence", "description": "Produce and operationalize cyber threat intelligence including actor profiling, IOC management, and intelligence sharing program participation."},
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
