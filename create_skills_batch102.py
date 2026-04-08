import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # Legal Services and Law Firm Practice Management
    ('legal-matter-management', 'Manage legal matters from intake to close including docketing deadlines and tracking milestones'),
    ('legal-billing-timekeeping', 'Automate attorney timekeeping, LEDES billing formats, and invoice generation for law firm clients'),
    ('legal-document-automation', 'Generate and assemble legal documents using templates for contracts, pleadings, and agreements'),
    ('legal-conflict-checking', 'Screen new clients and matters for conflicts of interest across firm relationships and prior representations'),
    ('legal-case-docketing', 'Track court deadlines, statute of limitations, and filing requirements across multiple jurisdictions'),
    ('legal-client-portal', 'Build secure client-facing portals for document sharing, matter status, and communication logs'),
    ('legal-contract-review', 'Analyze contracts for risk clauses, missing provisions, and deviations from standard firm positions'),
    ('legal-discovery-management', 'Organize and process discovery documents including review workflows and privilege logging'),
    ('legal-compliance-tracker', 'Monitor regulatory changes and map compliance obligations to firm practice areas and client industries'),
    ('legal-knowledge-management', 'Capture and retrieve firm knowledge including precedent documents, memos, and research libraries'),
]
skills += [
    # Accounting, CPA, and Audit Firm Operations
    ('audit-engagement-management', 'Manage audit engagements from planning through report issuance with risk assessment and workpaper tracking'),
    ('cpa-tax-workflow', 'Automate tax preparation workflows including document collection, review queues, and e-file submission'),
    ('audit-workpaper-automation', 'Generate and populate audit workpapers from trial balance data and prior year files'),
    ('accounting-client-onboarding', 'Streamline new client onboarding with KYC checks, engagement letter generation, and portal setup'),
    ('audit-sampling-tools', 'Apply statistical and judgmental sampling methodologies for audit testing populations'),
    ('cpa-deadline-management', 'Track tax and audit deadlines across client portfolios with automated reminders and extension filing'),
    ('financial-statement-analysis', 'Analyze financial statements for anomalies, ratio trends, and disclosure completeness'),
    ('audit-risk-assessment', 'Identify and document audit risks including fraud risks and significant account materiality'),
    ('accounting-reconciliation-tools', 'Automate account reconciliations including bank recs, intercompany, and subledger tie-outs'),
    ('cpa-practice-analytics', 'Track firm KPIs including realization rates, utilization, and client profitability dashboards'),
]
skills += [
    # Telecommunications Carrier Network Operations
    ('telecom-network-provisioning', 'Automate provisioning of telecom services including voice, data, and IP circuits across carrier networks'),
    ('telecom-fault-management', 'Detect, classify, and route network faults to resolution teams with SLA tracking and escalation'),
    ('telecom-capacity-planning', 'Analyze network utilization trends and forecast capacity needs to prevent congestion and outages'),
    ('telecom-order-management', 'Manage service orders from customer request through network activation and billing cutover'),
    ('telecom-number-portability', 'Automate local number portability workflows including FOC tracking and cutover scheduling'),
    ('telecom-billing-mediation', 'Collect and normalize network usage data for billing mediation, rating, and invoice generation'),
    ('telecom-peering-management', 'Manage interconnect agreements, BGP peering sessions, and traffic exchange reporting'),
    ('telecom-sla-monitoring', 'Monitor carrier SLA metrics including latency, packet loss, and availability against contract thresholds'),
    ('telecom-fraud-detection', 'Identify and block telecom fraud patterns including toll fraud, SIM swapping, and wangiri attacks'),
    ('telecom-network-inventory', 'Maintain accurate network inventory of circuits, equipment, and logical resources across the carrier footprint'),
]
skills += [
    # Streaming Media and OTT Platform Operations
    ('ott-content-ingestion', 'Automate ingest, transcode, and quality control workflows for video content delivered to OTT platforms'),
    ('ott-catalog-management', 'Manage content catalogs including metadata enrichment, rights windowing, and availability scheduling'),
    ('ott-drm-implementation', 'Implement digital rights management with multi-DRM support for Widevine, FairPlay, and PlayReady'),
    ('ott-cdn-optimization', 'Optimize content delivery network routing, caching strategies, and origin offload for video streaming'),
    ('ott-recommendation-engine', 'Build personalization and recommendation pipelines using viewing history and engagement signals'),
    ('ott-subscriber-analytics', 'Analyze subscriber acquisition, churn, engagement, and lifetime value across streaming products'),
    ('ott-live-streaming-ops', 'Manage live streaming operations including encoder monitoring, failover, and latency optimization'),
    ('ott-ad-insertion', 'Implement server-side ad insertion for streaming with targeting, pacing, and measurement integration'),
    ('ott-quality-of-experience', 'Monitor streaming quality metrics including rebuffering rate, bitrate, and startup time at scale'),
    ('ott-rights-management', 'Track content licensing windows, territorial restrictions, and contract obligations for OTT distribution'),
]
skills += [
    # Healthcare Payer and Managed Care Organization Operations
    ('payer-claims-processing', 'Automate health insurance claims intake, adjudication, and payment processing with edit checking'),
    ('payer-prior-authorization', 'Streamline prior authorization workflows with clinical criteria evaluation and real-time status tracking'),
    ('payer-member-enrollment', 'Manage member enrollment, eligibility verification, and plan assignment across group and individual markets'),
    ('payer-provider-contracting', 'Administer provider network contracts including fee schedule configuration and credentialing tracking'),
    ('payer-utilization-management', 'Conduct utilization review including concurrent review, retrospective audits, and length-of-stay monitoring'),
    ('payer-care-management', 'Identify and engage high-risk members for care management programs to improve outcomes and reduce costs'),
    ('payer-risk-adjustment', 'Automate risk adjustment data submission and reconciliation for ACA, Medicare Advantage, and Medicaid'),
    ('payer-quality-reporting', 'Collect and report HEDIS, Stars, and other quality measures for regulatory and incentive programs'),
    ('payer-subrogation-recovery', 'Identify and pursue subrogation and coordination of benefits recovery opportunities from paid claims'),
    ('payer-network-adequacy', 'Monitor provider network adequacy against regulatory standards by specialty, geography, and access metrics'),
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
