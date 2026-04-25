
import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # Energy technology advanced
    ('smart-grid-platform-advanced', 'Smart grid platform advanced - AMI, SCADA integration, demand response, grid analytics, DERMS'),
    ('energy-trading-platform', 'Energy trading platform - ETRM systems, power markets, day-ahead bidding, balancing mechanisms'),
    ('renewable-energy-platform', 'Renewable energy platform - generation forecasting, curtailment management, PPA tracking, ERCOT'),
    ('ev-charging-platform', 'EV charging platform - OCPP, smart charging, load management, fleet electrification, billing'),
    ('carbon-management-platform', 'Carbon management platform - Scope 1/2/3 accounting, SBTi alignment, carbon credits, ESG reporting'),
    ('energy-efficiency-platform', 'Energy efficiency platform - ISO 50001, M&V methodology, commissioning, benchmarking, ECMs'),
    ('microgrid-management', 'Microgrid management - islanding, battery dispatch, renewable integration, resilience, VPPs'),
    ('hydrogen-energy-platform', 'Hydrogen energy platform - electrolysis, fuel cell integration, storage, distribution, safety systems'),
    ('grid-edge-platform', 'Grid edge platform - DER aggregation, DERMS, transactive energy, grid services, virtual power plants'),
    ('nuclear-energy-tech', 'Nuclear energy technology - plant operations software, simulation, safety systems, waste management'),
    # Advanced manufacturing technology
    ('mes-platform-advanced', 'MES platform advanced - production scheduling, OEE tracking, genealogy, quality management, ERP sync'),
    ('quality-management-manufacturing', 'Quality management manufacturing - SPC, FMEA, APQP, PPAP, IATF 16949, quality gates'),
    ('digital-factory-platform', 'Digital factory platform - PLM integration, digital twin, line simulation, changeover optimization'),
    ('predictive-maintenance-advanced', 'Predictive maintenance advanced - vibration analysis, thermal imaging, anomaly detection, CMMS integration'),
    ('additive-manufacturing-platform', 'Additive manufacturing platform - build preparation, parameter optimization, quality control, materials'),
    ('robotics-integration-platform', 'Robotics integration platform - robot orchestration, vision systems, safety compliance, OEE'),
    ('material-traceability-platform', 'Material traceability platform - lot tracking, genealogy, supply chain visibility, recall management'),
    ('production-planning-advanced', 'Production planning advanced - constraint-based scheduling, bottleneck analysis, SIOP, finite capacity'),
    ('lean-manufacturing-tech', 'Lean manufacturing technology - VSM tools, Kaizen management, standard work, digital boards'),
    ('industrial-ai-platform', 'Industrial AI platform - edge ML deployment, process optimization, defect detection, yield improvement'),
    # Government and public sector technology
    ('digital-government-platform', 'Digital government platform - GovTech, citizen services, digital identity, service design, APIs'),
    ('open-data-platform', 'Open data platform - CKAN, metadata standards, licensing, data portals, API publication'),
    ('regulatory-intelligence-platform', 'Regulatory intelligence platform - horizon scanning, change tracking, impact analysis, obligation mgmt'),
    ('case-management-government', 'Case management government - workflow engines, document management, appeals, citizen portal'),
    ('grants-management-platform', 'Grants management platform - application processing, review workflows, disbursement, reporting'),
    ('tax-administration-platform', 'Tax administration platform - e-filing, audit selection, collections, taxpayer portal, analytics'),
    ('law-enforcement-platform', 'Law enforcement technology platform - CAD, RMS, evidence management, predictive policing'),
    ('emergency-management-advanced', 'Emergency management technology - EOC software, resource tracking, mass notification, NIMS'),
    ('elections-technology', 'Elections technology - voter registration, poll books, results reporting, election management'),
    ('public-health-platform', 'Public health platform - disease surveillance, contact tracing, immunization registry, reporting'),
    # Biotechnology and life sciences platform
    ('laboratory-informatics', 'Laboratory informatics - LIMS, ELN, data management, instrument integration, 21 CFR Part 11'),
    ('clinical-data-management', 'Clinical data management - EDC systems, data cleaning, safety reporting, eCRF, CDISC standards'),
    ('bioprocess-informatics', 'Bioprocess informatics - process analytical technology, real-time monitoring, batch records, CPP/CQA'),
    ('drug-discovery-informatics-advanced', 'Drug discovery informatics advanced - ADMET prediction, target identification, scaffold hopping'),
    ('regulatory-submission-platform', 'Regulatory submission platform - eCTD, NDA/BLA, FDA submissions, document management'),
    ('pharmacovigilance-platform', 'Pharmacovigilance platform - adverse event reporting, signal detection, risk management, EudraVigilance'),
    ('protein-engineering-platform', 'Protein engineering platform - directed evolution, protein design, expression systems, characterization'),
    ('cell-therapy-platform', 'Cell therapy manufacturing platform - process automation, quality control, chain of custody, ATMP'),
    ('genomics-sequencing-platform', 'Genomics sequencing platform - LIMS integration, pipeline management, variant calling, reporting'),
    ('synthetic-biology-platform-advanced', 'Synthetic biology platform advanced - genetic design, part registry, metabolic modeling, automation'),
    # Cybersecurity operations platform advanced
    ('soc-automation-platform', 'SOC automation platform - SOAR workflows, alert triage, investigation, enrichment, case management'),
    ('threat-hunting-platform', 'Threat hunting platform - hypothesis-driven, behavioral analytics, MITRE ATT&CK, investigation'),
    ('vulnerability-intelligence-platform', 'Vulnerability intelligence platform - asset correlation, exploit prediction, patch prioritization'),
    ('devsecops-platform-advanced', 'DevSecOps platform advanced - SAST/DAST/SCA orchestration, security gates, developer feedback loops'),
    ('cloud-native-security-platform', 'Cloud-native security platform - CNAPP, workload protection, network policies, secrets management'),
    ('identity-security-operations', 'Identity security operations - privileged access analytics, lateral movement detection, credential hygiene'),
    ('supply-chain-security-platform', 'Software supply chain security platform - SBOM management, provenance, signing, policy enforcement'),
    ('security-data-platform', 'Security data platform - data lake for security, normalization, enrichment, detection engineering'),
    ('attack-surface-management-platform', 'Attack surface management platform - continuous discovery, exposure scoring, remediation tracking'),
    ('cyber-threat-intelligence-platform', 'Cyber threat intelligence platform - collection, processing, analysis, sharing, TIP integration'),
    # Logistics and transportation technology
    ('transportation-management-advanced', 'Transportation management advanced - multimodal TMS, freight audit, carrier performance, network design'),
    ('last-mile-delivery-platform', 'Last mile delivery platform - route optimization, driver app, proof of delivery, customer notifications'),
    ('port-logistics-platform', 'Port logistics platform - terminal operating systems, vessel scheduling, gate management, EDI'),
    ('air-cargo-management', 'Air cargo management - cargo booking, ULD tracking, dangerous goods, AMS/ACAS compliance'),
    ('fleet-management-advanced', 'Fleet management advanced - telematics, preventive maintenance, driver scoring, fuel optimization'),
    ('freight-marketplace-platform', 'Freight marketplace platform - load matching, pricing algorithms, carrier onboarding, digital freight'),
    ('customs-clearance-platform', 'Customs clearance platform - HTS classification, ISF filing, broker collaboration, duty management'),
    ('cold-chain-logistics-platform', 'Cold chain logistics platform - temperature monitoring, excursion management, sensor networks'),
    ('postal-automation-platform', 'Postal automation platform - mail processing, address verification, sortation, delivery management'),
    ('urban-mobility-platform', 'Urban mobility platform - MaaS integration, multimodal routing, micro-mobility, transit data'),
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
