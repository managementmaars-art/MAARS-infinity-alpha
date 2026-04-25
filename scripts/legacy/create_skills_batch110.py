import os

base = r"c:\Users\mirza\MAARS-Command\.claude\skills"

# Domain: Semiconductor / Chip Manufacturing
skills = [
    {"name": "wafer-fab-operations", "description": "Manage semiconductor wafer fabrication operations including photolithography scheduling, yield monitoring, and equipment utilization."},
    {"name": "chip-design-tape-out", "description": "Coordinate IC design tape-out processes including DRC sign-off, PDK management, mask set ordering, and foundry submission."},
    {"name": "semiconductor-yield-engineering", "description": "Analyze semiconductor yield data using SPC, defect pareto analysis, and process of record management to improve die yield."},
    {"name": "semiconductor-supply-chain", "description": "Manage semiconductor supply chains including substrate procurement, advanced packaging coordination, and allocation management."},
    {"name": "chip-packaging-assembly", "description": "Oversee chip packaging and assembly operations including die attach, wire bond, flip chip, and final test coordination."},
    {"name": "semiconductor-equipment-maintenance", "description": "Maintain semiconductor fab equipment including preventive maintenance scheduling, spare parts management, and tool qualification."},
    {"name": "process-technology-development", "description": "Develop semiconductor process technologies including node shrink programs, materials qualification, and PDK release management."},
    {"name": "semiconductor-quality-reliability", "description": "Manage semiconductor quality and reliability programs including JEDEC testing, failure analysis, and customer quality reporting."},
    {"name": "esd-contamination-control", "description": "Implement ESD and contamination control programs in semiconductor fabs including cleanroom protocols and particle monitoring."},
    {"name": "semiconductor-ip-licensing", "description": "Manage semiconductor IP licensing including architecture license negotiations, royalty tracking, and standards body participation."},
]

# Domain: Event Management / Live Events
skills += [
    {"name": "event-production-management", "description": "Manage live event production from concept through execution including venue coordination, technical production, and run-of-show management."},
    {"name": "event-registration-ops", "description": "Operate event registration systems including ticketing platforms, badge management, attendee communication, and on-site check-in."},
    {"name": "conference-program-management", "description": "Develop conference programs including speaker recruitment, abstract review, session scheduling, and content track management."},
    {"name": "event-sponsorship-management", "description": "Manage event sponsorship programs including package development, sponsor activation delivery, lead retrieval, and post-event reporting."},
    {"name": "live-event-av-production", "description": "Coordinate audiovisual production for live events including stage design, lighting, sound, broadcast, and streaming operations."},
    {"name": "event-vendor-coordination", "description": "Coordinate event vendor networks including catering, decor, entertainment, security, and logistics supplier management."},
    {"name": "virtual-hybrid-event-ops", "description": "Operate virtual and hybrid event platforms including digital attendee experience, virtual networking, and content on-demand delivery."},
    {"name": "event-budget-financial-mgmt", "description": "Manage event budgets including cost tracking, attrition clause management, revenue reconciliation, and post-event financial reporting."},
    {"name": "event-safety-security-ops", "description": "Plan and execute event safety and security programs including crowd management, emergency response, and venue security coordination."},
    {"name": "tradeshow-exhibit-management", "description": "Manage tradeshow exhibit programs including booth design, freight logistics, I&D coordination, and lead capture strategy."},
]

# Domain: Staffing & Recruitment Technology
skills += [
    {"name": "ats-platform-operations", "description": "Operate applicant tracking system platforms including job posting workflows, candidate pipeline management, and hiring manager dashboards."},
    {"name": "talent-sourcing-automation", "description": "Automate talent sourcing using AI matching, Boolean search, candidate outreach sequences, and multi-channel pipeline building."},
    {"name": "recruiter-productivity-analytics", "description": "Analyze recruiter performance metrics including time-to-fill, pipeline conversion, source effectiveness, and cost-per-hire optimization."},
    {"name": "contingent-workforce-management", "description": "Manage contingent workforce programs including VMS platform operations, agency performance, rate card management, and compliance tracking."},
    {"name": "onboarding-automation", "description": "Automate employee onboarding workflows including document collection, background check coordination, system provisioning, and day-one readiness."},
    {"name": "employer-brand-management", "description": "Develop and manage employer brand programs including career site optimization, Glassdoor management, and candidate experience surveys."},
    {"name": "recruitment-marketing-ops", "description": "Execute recruitment marketing campaigns including programmatic job advertising, talent community management, and candidate nurture workflows."},
    {"name": "interview-process-management", "description": "Standardize interview processes including structured interview design, scheduling automation, feedback collection, and decision documentation."},
    {"name": "diversity-recruiting-programs", "description": "Implement diversity recruiting programs including sourcing diversification, bias mitigation in screening, and inclusive offer practices."},
    {"name": "workforce-planning-analytics", "description": "Develop workforce plans using headcount modeling, skills gap analysis, attrition forecasting, and hiring scenario planning."},
]

# Domain: Architecture & Engineering Professional Services
skills += [
    {"name": "ae-project-delivery-mgmt", "description": "Manage architecture and engineering project delivery including scope control, fee management, milestone tracking, and client reporting."},
    {"name": "design-quality-management", "description": "Implement design quality management programs including QA/QC checklists, peer review workflows, and design standards compliance."},
    {"name": "ae-business-development", "description": "Drive architecture and engineering business development including pursuit strategy, proposal development, and client relationship management."},
    {"name": "structural-engineering-ops", "description": "Coordinate structural engineering operations including analysis workflows, drawing production, peer review, and code compliance documentation."},
    {"name": "mep-engineering-coordination", "description": "Manage MEP engineering coordination including system design reviews, clash resolution, energy modeling, and commissioning support."},
    {"name": "ae-contract-management", "description": "Administer professional services contracts including scope change management, subconsultant coordination, and payment application processing."},
    {"name": "sustainability-certification-mgmt", "description": "Manage building sustainability certifications including LEED documentation, energy compliance modeling, and third-party review coordination."},
    {"name": "ae-resource-utilization", "description": "Optimize architecture and engineering staff utilization including project staffing plans, utilization tracking, and bench time management."},
    {"name": "permit-submission-management", "description": "Manage building permit submission processes including jurisdiction-specific requirements, plan check response, and approval tracking."},
    {"name": "ae-technology-adoption", "description": "Lead technology adoption programs for AE firms including BIM standards, digital delivery requirements, and collaboration platform rollout."},
]

# Domain: Chemical Manufacturing
skills += [
    {"name": "chemical-process-safety-mgmt", "description": "Implement process safety management programs including PHA facilitation, MOC procedures, LOPA analysis, and PSI documentation."},
    {"name": "batch-chemical-manufacturing", "description": "Manage batch chemical production operations including master batch records, in-process controls, and yield optimization."},
    {"name": "chemical-regulatory-compliance", "description": "Navigate chemical regulatory compliance including TSCA, REACH, SDS management, and hazardous chemical inventory reporting."},
    {"name": "chemical-raw-material-sourcing", "description": "Manage chemical raw material procurement including supplier qualification, certificate of analysis review, and alternative sourcing programs."},
    {"name": "chemical-plant-turnaround", "description": "Plan and execute chemical plant turnarounds including scope development, contractor management, critical path scheduling, and startup readiness."},
    {"name": "specialty-chemical-formulation", "description": "Manage specialty chemical formulation programs including development workflows, scale-up protocols, and technical data sheet generation."},
    {"name": "chemical-distribution-logistics", "description": "Manage chemical distribution logistics including hazmat shipping compliance, bulk vs packaged mode optimization, and carrier qualification."},
    {"name": "environmental-health-safety-chem", "description": "Operate EHS programs in chemical facilities including industrial hygiene monitoring, permit-to-work systems, and incident investigation."},
    {"name": "continuous-chemical-process-ops", "description": "Operate continuous chemical processes including reactor control, distillation column management, and real-time process analytics."},
    {"name": "chemical-product-stewardship", "description": "Manage chemical product stewardship programs including downstream user communication, exposure scenario development, and responsible care reporting."},
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
