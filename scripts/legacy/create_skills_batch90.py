
import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # Court reporting and litigation support technology
    ('court-reporting-software', 'Court reporting software and transcript management platform - CAT integration, realtime streaming, ASCII delivery, billing'),
    ('legal-videography-platform', 'Legal videography and deposition services platform - scheduling, sync transcript, exhibit linking, delivery'),
    ('litigation-support-platform', 'Litigation support and trial preparation platform - exhibit management, timeline builder, war room tools'),
    ('e-discovery-review-platform', 'E-discovery document review and production platform - TAR/predictive coding, review workflow, privilege log'),
    ('legal-exhibit-management', 'Legal exhibit management and courtroom presentation platform - exhibit tracking, marking, electronic presentation'),
    ('deposition-management-platform', 'Deposition management and scheduling platform - reporter scheduling, exhibits, video, transcript delivery'),
    ('trial-presentation-platform', 'Trial presentation technology platform - multimedia evidence, real-time sync, jury presentation'),
    ('jury-consulting-platform', 'Jury consulting and mock trial technology platform - mock juror management, survey tools, focus groups'),
    ('expert-witness-platform', 'Expert witness management and scheduling platform - expert directory, case assignment, fee management'),
    ('legal-hold-management-platform', 'Legal hold and data preservation management platform - custodian notification, acknowledgment tracking, release'),
    # Bail bonds and surety technology
    ('bail-bond-management-platform', 'Bail bond agency management platform - bond issuance, premium tracking, indemnitor management, compliance'),
    ('surety-bond-platform', 'Surety bond issuance and management platform - underwriting, bond issuance, claims, reinsurance'),
    ('defendant-monitoring-platform', 'Defendant monitoring and pretrial services platform - check-in tracking, GPS monitoring, compliance reporting'),
    ('fugitive-recovery-management', 'Fugitive recovery and bounty hunter management platform - warrant tracking, skip trace, recovery reporting'),
    ('bond-forfeiture-platform', 'Bond forfeiture and exoneration management platform - court date tracking, forfeiture processing, reinstatement'),
    ('collateral-management-bail', 'Bail bond collateral management platform - property liens, vehicle holds, jewelry tracking, release'),
    ('pretrial-services-platform', 'Pretrial services and supervision platform - risk assessment, supervision conditions, court date reminders'),
    ('criminal-justice-reform-tech', 'Criminal justice reform and alternative to incarceration platform - risk tools, diversion tracking, outcomes'),
    ('inmate-communication-platform', 'Inmate communication and visitation management platform - video visits, phone management, messaging, deposits'),
    ('reentry-employment-platform', 'Reentry employment services and job placement platform - employer partnerships, job matching, training, support'),
    # Specialty retail verticals technology
    ('gun-shop-management', 'Gun shop and firearms retail management platform - ATF compliance, 4473 digital, bound book, inventory'),
    ('pawn-management-platform', 'Pawn shop management and compliance platform - item tracking, loan management, regulatory compliance, reporting'),
    ('tobacco-retail-platform', 'Tobacco and smoke shop retail management platform - age verification, compliance, product catalog, loyalty'),
    ('kratom-supplement-platform', 'Herbal supplement and kratom retail management platform - product compliance, batch tracking, age verification'),
    ('hookah-lounge-platform', 'Hookah lounge and shisha retail management platform - session management, product inventory, age verification'),
    ('vitamin-supplement-retail', 'Vitamin and supplement specialty retail platform - formulation database, compliance, subscription, loyalty'),
    ('organic-grocery-platform', 'Organic and natural grocery store management platform - vendor certifications, PLU management, bulk inventory'),
    ('butcher-shop-platform', 'Butcher shop and specialty meat retail platform - custom cuts, aging inventory, wholesale, catering'),
    ('fishmonger-platform', 'Fishmonger and seafood retail management platform - catch tracking, freshness, sustainability certification'),
    ('candy-confectionery-retail', 'Candy and confectionery specialty retail platform - custom orders, bulk pricing, gifting, subscription'),
    # Veterinary specialty platforms
    ('equine-veterinary-platform', 'Equine veterinary practice management platform - large animal records, farm calls, Coggins testing, billing'),
    ('zoo-veterinary-platform', 'Zoo and wildlife veterinary management platform - species records, treatment protocols, quarantine, research'),
    ('avian-veterinary-platform', 'Avian and exotic bird veterinary practice platform - species-specific care, flight status, microchip, billing'),
    ('cattle-health-platform', 'Cattle and beef herd health management platform - treatment records, vaccination, weight gain, breeding'),
    ('swine-veterinary-platform', 'Swine veterinary and herd health platform - herd records, disease surveillance, vaccination, reporting'),
    ('poultry-health-platform', 'Poultry flock health management platform - flock records, mortality tracking, lab samples, biosecurity'),
    ('aquatic-veterinary-platform', 'Aquatic and fish health veterinary platform - water quality records, disease diagnosis, treatment, necropsy'),
    ('shelter-medicine-platform', 'Shelter medicine and population health platform - intake exams, disease surveillance, vaccination, outcomes'),
    ('telemedicine-vet-platform', 'Veterinary telemedicine and remote consultation platform - video consults, prescription, specialist referral'),
    ('animal-blood-bank-platform', 'Animal blood bank and transfusion medicine platform - donor management, typing, inventory, request management'),
    # Staffing and workforce solutions verticals
    ('travel-therapy-staffing', 'Travel therapy and allied health staffing platform - PT/OT/SLP placement, assignment management, compliance'),
    ('physician-staffing-platform', 'Physician and locum tenens staffing platform - credentialing, scheduling, payroll, malpractice, compliance'),
    ('construction-staffing-platform', 'Construction trades staffing and labor platform - craft worker roster, certification tracking, deployment'),
    ('warehouse-staffing-platform', 'Warehouse and fulfillment center staffing platform - shift management, temp-to-perm, skills matching'),
    ('hospitality-staffing-platform', 'Hospitality and hotel staffing platform - banquet staff, housekeeping, culinary, temporary staffing'),
    ('event-staffing-platform', 'Event staffing and gig worker management platform - event booking, worker scheduling, payments, ratings'),
    ('maritime-crewing-platform', 'Maritime crewing and seafarer management platform - STCW certification, vessel assignment, payroll, compliance'),
    ('airline-crew-platform', 'Airline crew scheduling and management platform - regulatory compliance, rest rules, pairing, bidding'),
    ('security-guard-staffing', 'Security guard staffing and management platform - post assignment, officer tracking, licensing, billing'),
    ('domestic-staffing-platform', 'Domestic staffing and household employee platform - nanny/housekeeper placement, payroll, compliance'),
    # Franchise development and operations technology
    ('franchise-discovery-platform', 'Franchise discovery and research platform - franchise directory, FDD analysis, investment comparison'),
    ('franchise-sales-platform', 'Franchise sales and lead generation platform - lead management, FDD distribution, territory mapping'),
    ('multi-unit-franchise-platform', 'Multi-unit franchise operator management platform - portfolio oversight, performance benchmarking, compliance'),
    ('franchise-field-ops-platform', 'Franchise field operations and support platform - field visit management, action plans, compliance tracking'),
    ('franchise-pos-platform', 'Franchise-wide POS and reporting platform - standardized reporting, menu management, royalty calculation'),
    ('franchise-hr-platform', 'Franchise HR and employee management platform - hiring portals, handbook compliance, payroll, benefits'),
    ('franchise-learning-platform', 'Franchise learning management and certification platform - initial training, ongoing education, compliance'),
    ('franchise-marketing-coop', 'Franchise marketing cooperative and ad fund platform - contribution tracking, campaign management, reporting'),
    ('franchise-real-estate-site', 'Franchise real estate and site selection platform - demographic analysis, territory management, approval'),
    ('franchise-exit-platform', 'Franchise resale and exit strategy management platform - valuation, buyer matching, transfer process, compliance'),
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
