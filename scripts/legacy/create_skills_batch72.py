
import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # Notary, title, and document services technology
    ('notary-services-platform', 'Notary services technology platform - remote online notary, document management, identity verification'),
    ('apostille-services-platform', 'Apostille and document authentication platform - certification workflow, tracking, multi-jurisdiction'),
    ('process-server-platform', 'Process server and legal document delivery platform - job management, GPS tracking, proof of service'),
    ('court-reporting-platform', 'Court reporting technology platform - transcript management, real-time reporting, exhibits, billing'),
    ('records-retrieval-platform', 'Records retrieval services platform - medical/legal record requests, tracking, HIPAA compliance'),
    ('background-check-platform', 'Background check technology platform - criminal, employment, education verification, consent management'),
    ('private-investigator-platform', 'Private investigator management platform - case management, surveillance logs, reports, billing'),
    ('skip-tracing-platform', 'Skip tracing technology platform - subject location, data aggregation, compliance, case management'),
    ('repossession-platform', 'Repossession services management platform - assignment routing, condition reports, storage, compliance'),
    ('bail-bonds-platform', 'Bail bonds management platform - defendant tracking, court date monitoring, collateral, compliance'),
    # Government and public sector technology
    ('permit-management-platform', 'Government permit management platform - application workflow, inspection scheduling, compliance tracking'),
    ('license-management-gov', 'Government license management platform - professional licenses, renewals, CE tracking, disciplinary'),
    ('grant-management-gov', 'Government grant management platform - application, review, award, reporting, compliance, closeout'),
    ('procurement-gov-platform', 'Government procurement technology platform - RFP, bidding, vendor management, contract, compliance'),
    ('tax-assessment-platform', 'Tax assessment and administration platform - valuation, appeals, exemptions, billing, collection'),
    ('vital-records-platform', 'Vital records management platform - birth/death/marriage, issuance, amendments, genealogy access'),
    ('court-case-management', 'Court case management system - docketing, scheduling, e-filing, records, reporting, public access'),
    ('corrections-platform', 'Corrections management technology platform - inmate records, programs, classification, release, reporting'),
    ('benefits-admin-gov', 'Government benefits administration platform - eligibility, enrollment, payments, fraud detection, appeals'),
    ('public-works-platform', 'Public works management technology platform - infrastructure assets, work orders, permits, inspections'),
    # Specialty food and beverage technology
    ('brewery-management-platform', 'Brewery management technology platform - recipe management, batch tracking, inventory, TTB compliance'),
    ('winery-management-platform', 'Winery management technology platform - vineyard tracking, vintage management, compliance, DTC sales'),
    ('distillery-platform', 'Distillery management platform - spirit production tracking, barrel management, TTB compliance, distribution'),
    ('food-truck-platform', 'Food truck and mobile food service platform - location management, menu, POS, commissary scheduling'),
    ('catering-management-platform', 'Catering management technology platform - event booking, menu management, kitchen, staffing, billing'),
    ('meal-prep-platform', 'Meal prep and meal kit delivery platform - subscription, recipe management, portioning, delivery routes'),
    ('ghost-kitchen-platform', 'Ghost kitchen and virtual restaurant platform - multi-brand operations, order aggregation, kitchen management'),
    ('specialty-coffee-platform', 'Specialty coffee roastery and cafe platform - green coffee sourcing, roast profiles, subscription, wholesale'),
    ('chocolate-confectionery-platform', 'Chocolate and confectionery production platform - recipe management, batch tracking, compliance, DTC'),
    ('artisan-food-producer-platform', 'Artisan food producer technology platform - cottage food compliance, online sales, farmers markets, scaling'),
    # Medical device and equipment technology
    ('medical-equipment-rental', 'Medical equipment rental and management platform - inventory, maintenance, patient assignment, billing'),
    ('dme-platform', 'Durable medical equipment platform - order management, insurance billing, delivery, HCPCS coding'),
    ('medical-device-repair', 'Medical device repair and maintenance platform - work orders, parts inventory, calibration, ISO 13485'),
    ('biomedical-engineering-platform', 'Biomedical engineering technology platform - equipment lifecycle, PM schedules, recalls, regulatory'),
    ('clinical-equipment-tracking', 'Clinical equipment tracking platform - asset management, utilization, preventive maintenance, compliance'),
    ('sterilization-platform', 'Sterilization and decontamination management platform - cycle records, biological indicators, compliance'),
    ('surgical-instrument-tracking', 'Surgical instrument tracking platform - set management, sterilization, traceability, loan sets'),
    ('hospital-supply-chain', 'Hospital supply chain technology platform - procurement, inventory, par levels, vendor management'),
    ('medical-gas-platform', 'Medical gas management platform - cylinder tracking, inspection, distribution, regulatory compliance'),
    ('prosthetics-orthotics-platform', 'Prosthetics and orthotics practice platform - L-code billing, fitting records, manufacturer ordering'),
    # Interior design and home staging technology
    ('interior-design-platform', 'Interior design practice management platform - project management, mood boards, procurement, client portal'),
    ('home-staging-platform', 'Home staging management platform - inventory tracking, staging jobs, photography coordination, billing'),
    ('furniture-rental-platform', 'Furniture rental and staging platform - catalog, reservations, delivery, installation, billing'),
    ('space-planning-platform', 'Space planning and floor plan technology - 3D visualization, furniture placement, client presentations'),
    ('design-build-platform', 'Design-build project management platform - design-construction integration, permitting, subcontractors'),
    ('color-consulting-platform', 'Color consulting and paint management platform - color recommendations, fan decks, project records'),
    ('textile-sourcing-platform', 'Interior textile sourcing and specification platform - fabric library, samples, purchasing, tracking'),
    ('art-consulting-platform', 'Art consulting and curation platform - collection management, client profiles, procurement, installation'),
    ('window-treatment-platform', 'Window treatment measurement and installation platform - measure, quote, fabrication, installation, billing'),
    ('lighting-design-platform', 'Architectural lighting design platform - fixture specification, photometric analysis, commissioning'),
    # Franchise and multi-unit operations technology
    ('franchise-management-platform', 'Franchise management technology platform - franchise development, operations, royalty collection, compliance'),
    ('multi-unit-restaurant-platform', 'Multi-unit restaurant management platform - centralized menu, labor, food cost, mystery shopper, ops'),
    ('franchise-crm-platform', 'Franchise CRM and lead management platform - prospect tracking, territory mapping, qualification, closing'),
    ('franchise-compliance-platform', 'Franchise compliance technology platform - standards enforcement, audits, brand guidelines, corrective action'),
    ('franchise-training-platform', 'Franchise training and onboarding platform - LMS, operational manuals, certification, new store opening'),
    ('franchise-marketing-platform', 'Franchise marketing technology platform - local marketing, national fund management, co-op advertising'),
    ('multi-unit-retail-platform', 'Multi-unit retail management platform - store performance, inventory, visual merchandising, HR'),
    ('area-developer-platform', 'Area developer management technology platform - territory management, development schedules, reporting'),
    ('franchise-finance-platform', 'Franchise finance and reporting platform - royalty calculation, P&L reporting, benchmarking, FDD'),
    ('franchise-supply-platform', 'Franchise supply chain and purchasing platform - approved vendor management, group purchasing, compliance'),
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
