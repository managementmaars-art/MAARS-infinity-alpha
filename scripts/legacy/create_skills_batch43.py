
import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # Healthcare IT and clinical informatics
    ('clinical-informatics', 'Clinical informatics - EHR optimization, clinical workflows, decision support, data standards'),
    ('hl7-v2-messaging', 'HL7 v2 messaging - ADT, ORU, ORM, segments, parsing, integration engines, Mirth'),
    ('snomed-ct', 'SNOMED CT - clinical terminology, concept model, expressions, mapping, implementation, ECL'),
    ('icd-coding', 'ICD-10/11 coding - diagnosis codes, procedure codes, DRG, coding guidelines, AI-assisted'),
    ('loinc-standards', 'LOINC standards - laboratory, clinical, observation codes, mapping, RELMA, implementation'),
    ('dicom-advanced', 'DICOM advanced - SOP classes, workflows, WADO, DICOMweb, anonymization, de-identification'),
    ('radiology-ai', 'Radiology AI - CAD, triage, measurement, reporting, worklist integration, FDA clearance'),
    ('pathology-informatics', 'Pathology informatics - digital pathology, whole slide imaging, AI integration, LIS, reporting'),
    ('genomics-clinical', 'Clinical genomics - variant interpretation, VCF processing, NGS pipelines, pharmacogenomics'),
    ('drug-interaction-systems', 'Drug interaction systems - clinical decision support, alerts, severity, overrides, Cerner/Epic'),
    ('nursing-informatics', 'Nursing informatics - EHR documentation, workflows, CDSS, outcomes, quality metrics'),
    ('telehealth-integration', 'Telehealth integration - video platform APIs, scheduling, consent, documentation, billing'),
    ('patient-engagement', 'Patient engagement technology - portals, messaging, reminders, surveys, activation, mHealth'),
    ('healthcare-analytics-platform', 'Healthcare analytics platform - data warehouse, quality measures, HEDIS, population health'),
    ('revenue-cycle-management', 'Revenue cycle management - scheduling, registration, coding, billing, claims, denials, AR'),
    # Legal technology
    ('ediscovery-platform', 'eDiscovery platform - legal hold, collection, processing, review, production, TAR, Relativity'),
    ('contract-lifecycle-mgmt', 'Contract lifecycle management - CLM platforms, template, negotiation, approval, renewal, AI'),
    ('legal-research-ai', 'Legal research AI - case law, statutes, secondary sources, citation checking, brief analysis'),
    ('court-filing-systems', 'Court filing systems - PACER, EFSP, document formatting, e-signatures, filing requirements'),
    ('legal-ops-analytics', 'Legal ops analytics - matter management, outside counsel, budget, KPIs, benchmarking'),
    ('compliance-management-platform', 'Compliance management platform - controls, testing, evidence, gap analysis, reporting'),
    ('patent-search-analysis', 'Patent search and analysis - prior art, claims, prosecution history, FTO, landscape'),
    ('trademark-management', 'Trademark management - clearance, prosecution, monitoring, portfolio, renewals, TEAS'),
    # Real estate technology
    ('proptech-platform', 'PropTech platform - listing management, CRM, transaction management, MLS integration'),
    ('real-estate-analytics', 'Real estate analytics - AVM, market analysis, comparables, investment metrics, forecasting'),
    ('property-management-software', 'Property management software - tenant portal, maintenance, rent collection, accounting'),
    ('building-inspection-tech', 'Building inspection technology - inspection apps, reports, photos, compliance, IoT sensors'),
    ('real-estate-crm', 'Real estate CRM - lead management, pipeline, follow-up automation, transaction coordination'),
    ('mortgage-technology', 'Mortgage technology - loan origination, underwriting, closing, compliance, servicing, API'),
    # Insurance technology
    ('insurance-platform', 'Insurance platform - policy administration, claims, billing, agent portal, API, integration'),
    ('claims-management', 'Claims management - FNOL, adjudication, reserves, litigation, fraud, settlement, analytics'),
    ('actuarial-software', 'Actuarial software - ratemaking, reserving, capital modeling, predictive analytics, GRC'),
    ('insurance-underwriting-ai', 'Insurance underwriting AI - risk scoring, appetite, pricing, data enrichment, decisions'),
    ('insurtech-distribution', 'InsurTech distribution - digital quoting, binding, embedded insurance, API, white-label'),
    ('reinsurance-analytics', 'Reinsurance analytics - treaty, facultative, CAT modeling, exposure, profit commissions'),
    # Travel and hospitality
    ('hotel-management-system', 'Hotel management system - PMS, reservations, front desk, housekeeping, F&B, reporting'),
    ('airline-reservation-system', 'Airline reservation system - GDS, NDC, booking, inventory, pricing, ancillaries, API'),
    ('travel-technology-platform', 'Travel technology platform - OTA integration, content, search, booking flows, payments'),
    ('hospitality-analytics', 'Hospitality analytics - RevPAR, ADR, occupancy, segmentation, forecasting, competitive'),
    ('restaurant-technology', 'Restaurant technology - POS, KDS, ordering, delivery integration, inventory, analytics'),
    ('event-management-platform', 'Event management platform - registration, ticketing, mobile app, analytics, badge printing'),
    # Retail and e-commerce
    ('omnichannel-retail', 'Omnichannel retail - unified commerce, inventory visibility, BOPIS, returns, POS integration'),
    ('merchandising-systems', 'Merchandising systems - assortment planning, space planning, planogram, allocation, replenishment'),
    ('retail-analytics', 'Retail analytics - sales performance, basket analysis, customer segmentation, forecasting'),
    ('loyalty-platform', 'Loyalty platform - points, tiers, rewards, gamification, personalization, analytics, API'),
    ('ecommerce-personalization', 'E-commerce personalization - recommendations, dynamic pricing, A/B testing, segmentation'),
    ('retail-execution', 'Retail execution - field sales, store audits, task management, planogram compliance, mobility'),
    # Manufacturing and industry 4.0
    ('industry-4-platform', 'Industry 4.0 platform - IIoT, digital twin, predictive maintenance, MES, ERP integration'),
    ('manufacturing-execution-system', 'Manufacturing execution system - work orders, routing, quality, genealogy, reporting'),
    ('quality-management-system', 'Quality management system - CAPA, document control, training, audit, supplier, compliance'),
    ('predictive-maintenance-platform', 'Predictive maintenance - vibration, thermography, ML models, alerts, CMMS integration'),
    ('supply-chain-planning', 'Supply chain planning - S&OP, demand, supply, inventory, network design, optimization'),
    ('engineering-change-management', 'Engineering change management - ECO, BOM, PLM integration, approval workflows, revision'),
    ('product-lifecycle-management', 'Product lifecycle management - PLM, CAD integration, BOM, change management, configuration'),
    # Public safety and emergency services
    ('cad-dispatch-system', 'CAD dispatch system - 911, incident management, unit tracking, interoperability, GIS'),
    ('records-management-law-enforcement', 'Law enforcement RMS - incident reports, arrests, evidence, warrants, analytics'),
    ('fire-management-system', 'Fire management system - resource tracking, incident command, pre-plans, hydrants, NFIRS'),
    ('emergency-management-platform', 'Emergency management platform - EOC, resource management, public alerts, WebEOC'),
    ('corrections-management', 'Corrections management system - inmate records, classification, programs, releases, reporting'),
    # Non-profit and social sector
    ('nonprofit-crm', 'Nonprofit CRM - constituent management, fundraising, campaigns, events, grants, Salesforce NPSP'),
    ('grant-management', 'Grant management - prospect research, applications, reporting, compliance, portfolio tracking'),
    ('volunteer-management', 'Volunteer management - recruitment, scheduling, hours tracking, communication, recognition'),
    ('social-services-case-management', 'Social services case management - intake, assessments, service plans, referrals, reporting'),
    ('impact-measurement', 'Impact measurement - theory of change, logic models, data collection, outcomes, reporting'),
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
