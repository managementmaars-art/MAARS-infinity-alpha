
import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # Clinical research and life sciences technology
    ('clinical-research-org-platform', 'Clinical research organization technology platform - protocol management, site monitoring, data management, regulatory'),
    ('clinical-trial-management', 'Clinical trial management system - study setup, enrollment, randomization, eCRF, safety reporting'),
    ('biobank-management-platform', 'Biobank and sample management technology platform - specimen tracking, consent, storage, distribution'),
    ('pharmacovigilance-signal', 'Pharmacovigilance signal detection platform - adverse event reporting, signal monitoring, regulatory submission'),
    ('drug-safety-platform', 'Drug safety and regulatory affairs platform - IND/NDA management, REMS tracking, label management'),
    ('medical-writing-platform', 'Medical writing and regulatory documentation platform - CSR, dossier, submission management, version control'),
    ('lab-information-system', 'Laboratory information management system - sample management, instrument integration, QC, reporting'),
    ('preclinical-research-platform', 'Preclinical research management platform - animal study management, in vitro tracking, data management'),
    ('research-site-management', 'Clinical research site management platform - enrollment, visit scheduling, source data, audit trail'),
    ('irt-system-platform', 'Interactive response technology platform - randomization, drug supply management, unblinding, reporting'),
    # Funeral and end-of-life services technology
    ('funeral-home-platform', 'Funeral home management technology platform - arrangement, obituaries, cremation tracking, billing, aftercare'),
    ('cremation-tech-platform', 'Cremation services technology platform - authorization workflow, chain of custody, scheduling, billing'),
    ('cemetery-tech-platform', 'Cemetery management technology platform - interment records, lot sales, mapping, maintenance, perpetual care'),
    ('memorial-services-platform', 'Memorial and celebration of life services platform - venue booking, tribute pages, streaming, flowers'),
    ('grief-support-platform', 'Grief support and counseling technology platform - support groups, one-on-one counseling, resources, follow-up'),
    ('estate-administration-tech', 'Estate administration technology platform - asset inventory, beneficiary management, probate tracking'),
    ('pre-need-planning-platform', 'Pre-need funeral planning technology platform - preneed contracts, trust management, portability, compliance'),
    ('death-care-compliance', 'Death care industry compliance technology - state licensing, FTC rule compliance, price disclosure, audits'),
    ('genealogy-research-platform', 'Genealogy research technology platform - family tree building, record access, DNA matching, collaboration'),
    ('legacy-preservation-platform', 'Legacy preservation and life story technology platform - memoir creation, digital archives, video stories'),
    # Auction and liquidation technology
    ('auction-house-platform', 'Auction house management technology platform - consignment, cataloging, bidding, settlement, buyer management'),
    ('online-auction-platform', 'Online auction technology platform - real-time bidding, proxy bidding, payment, buyer verification'),
    ('government-surplus-auction', 'Government surplus and seized property auction platform - compliance, public notice, bidding, settlement'),
    ('agricultural-auction-platform', 'Agricultural commodity auction platform - grain, livestock, equipment bidding, market integration'),
    ('charity-auction-platform', 'Charity and nonprofit auction technology platform - silent, live, online bidding, donor management, reporting'),
    ('heavy-equipment-auction', 'Heavy equipment auction technology platform - appraisal, inspection reports, global bidding, logistics'),
    ('real-estate-auction-platform', 'Real estate auction technology platform - bidding engine, title search integration, closing management'),
    ('jewelry-auction-platform', 'Jewelry and luxury goods auction platform - authentication, grading, reserve pricing, buyer premium'),
    ('wine-auction-platform', 'Fine wine and spirits auction platform - provenance tracking, cellar records, bidding, compliance'),
    ('bankruptcy-auction-platform', 'Bankruptcy and distressed asset auction platform - legal compliance, credit bidding, stalking horse, settlement'),
    # Insurance adjusting and claims field services technology
    ('insurance-adjuster-platform', 'Insurance adjuster management technology platform - claim assignment, field inspection, estimate, reporting'),
    ('property-claims-platform', 'Property damage claims technology platform - inspection photos, Xactimate integration, settlement, fraud'),
    ('auto-claims-platform', 'Automobile claims technology platform - damage assessment, rental, total loss, subrogation, payment'),
    ('workers-comp-claims', 'Workers compensation claims technology platform - injury reporting, medical management, return to work, reserves'),
    ('catastrophe-claims-platform', 'Catastrophe claims management platform - event activation, adjuster deployment, mass claims, reporting'),
    ('desk-adjuster-platform', 'Desk adjuster technology platform - remote claims handling, virtual inspections, document review, settlement'),
    ('public-adjuster-platform', 'Public adjuster technology platform - policyholder representation, claim negotiation, documentation, billing'),
    ('claims-analytics-platform', 'Claims analytics technology platform - loss trends, reserve adequacy, fraud indicators, benchmarking'),
    ('subrogation-platform', 'Subrogation and recovery technology platform - claim identification, demand letters, arbitration, collection'),
    ('salvage-recovery-platform', 'Salvage and recovery technology platform - total loss vehicles, property salvage, auction integration'),
    # Pest control and environmental services technology
    ('pest-control-management', 'Pest control company management platform - route scheduling, treatment records, chemical tracking, billing'),
    ('termite-inspection-platform', 'Termite inspection and treatment technology platform - inspection reports, bond management, warranty, billing'),
    ('wildlife-control-platform', 'Wildlife control and removal services platform - trap management, dispatch, compliance, billing'),
    ('lawn-chemical-platform', 'Lawn chemical application and treatment platform - application records, licensing, notification, billing'),
    ('fumigation-platform', 'Fumigation services management platform - tarp scheduling, chemical tracking, clearance testing, compliance'),
    ('rodent-control-platform', 'Rodent control management technology platform - inspection, bait station mapping, monitoring, reporting'),
    ('bed-bug-services-platform', 'Bed bug treatment services platform - heat treatment scheduling, dog inspection, follow-up, billing'),
    ('mosquito-control-platform', 'Mosquito control services platform - seasonal scheduling, treatment records, customer portal, billing'),
    ('drywood-termite-platform', 'Drywood termite treatment and tent fumigation platform - scheduling, permit, chemical tracking, compliance'),
    ('environmental-services-tech', 'Environmental services technology platform - hazardous waste, soil remediation, compliance, reporting'),
    # Security services and monitoring technology
    ('guard-patrol-platform', 'Security guard patrol management platform - post orders, patrol logging, incident reporting, scheduling'),
    ('alarm-monitoring-platform', 'Alarm monitoring technology platform - signal processing, dispatch, subscriber management, UL compliance'),
    ('video-monitoring-platform', 'Video surveillance monitoring platform - camera management, event detection, remote monitoring, reporting'),
    ('access-control-management', 'Access control system management platform - credential management, door scheduling, audit trail, integration'),
    ('executive-protection-platform', 'Executive protection and personal security platform - threat assessment, detail scheduling, travel security'),
    ('loss-prevention-platform', 'Retail loss prevention technology platform - incident management, CCTV integration, shrink analytics'),
    ('security-investigations-platform', 'Security investigations management platform - case management, evidence tracking, interview recording'),
    ('background-screening-platform', 'Background screening services platform - order management, court research, compliance, report delivery'),
    ('drone-security-platform', 'Drone security and aerial surveillance platform - flight scheduling, incident response, video analytics'),
    ('cybersecurity-mssp-platform', 'Managed security services provider platform - SOC operations, client monitoring, incident response, reporting'),
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
