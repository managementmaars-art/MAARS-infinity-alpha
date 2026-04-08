
import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # Talent agency and casting technology
    ('talent-agency-platform', 'Talent agency management platform - roster management, booking, contracts, commission tracking, billing'),
    ('casting-platform', 'Casting and audition management platform - breakdown distribution, submissions, sides, scheduling, reporting'),
    ('sports-agent-platform', 'Sports agent and athlete representation platform - contract management, endorsements, scheduling, finances'),
    ('entertainment-agency-platform', 'Entertainment agency technology platform - tour management, rider management, settlements, accounting'),
    ('modeling-agency-platform', 'Modeling agency technology platform - comp card management, casting, client portal, booking, billing'),
    ('voice-over-platform', 'Voice-over talent marketplace platform - auditions, recording delivery, licensing, royalty tracking'),
    ('influencer-talent-platform', 'Influencer talent management platform - creator roster, brand deals, contracts, analytics, payments'),
    ('lecture-bureau-platform', 'Speakers bureau and lecture management platform - speaker roster, booking, travel, contracts, billing'),
    ('literary-agency-platform', 'Literary agency technology platform - manuscript tracking, submissions, publisher relations, royalties'),
    ('production-company-platform', 'Production company management platform - project development, crew management, budgets, releases'),
    # Tutoring and test prep technology
    ('tutoring-center-platform', 'Tutoring center management platform - student scheduling, session notes, progress tracking, billing'),
    ('online-tutoring-platform', 'Online tutoring marketplace platform - tutor matching, video sessions, payment, progress analytics'),
    ('test-prep-platform', 'Test preparation technology platform - adaptive practice, diagnostic assessment, score prediction, reporting'),
    ('sat-act-platform', 'SAT/ACT test prep platform - diagnostic testing, personalized study plans, score tracking, coaching'),
    ('gmat-gre-platform', 'GMAT/GRE test preparation platform - quant/verbal practice, adaptive learning, analytics, coaching'),
    ('bar-exam-platform', 'Bar exam preparation platform - MBE/MEE practice, essay grading, performance tracking, study planning'),
    ('medical-board-prep-platform', 'Medical board exam preparation platform - USMLE/COMLEX practice, clinical vignettes, analytics'),
    ('k12-tutoring-platform', 'K-12 tutoring technology platform - subject alignment, homework help, progress reporting, parent portal'),
    ('executive-education-platform', 'Executive education technology platform - cohort management, case studies, facilitation, networking'),
    ('professional-licensing-prep', 'Professional licensing exam prep platform - study materials, practice tests, track progress, compliance'),
    # Pet care and veterinary technology
    ('pet-grooming-tech', 'Pet grooming services technology platform - appointment booking, breed-specific notes, loyalty, mobile grooming'),
    ('pet-boarding-platform', 'Pet boarding and kennel management platform - reservation, pet profiles, feeding instructions, webcam'),
    ('pet-daycare-platform', 'Pet daycare management platform - check-in/out, activity reports, vaccination tracking, billing'),
    ('veterinary-telemedicine-platform', 'Veterinary telemedicine platform - virtual consultations, prescription refills, follow-up care'),
    ('pet-insurance-tech', 'Pet insurance technology platform - policy management, claims processing, wellness benefits, network'),
    ('animal-rescue-platform', 'Animal rescue and adoption technology platform - intake management, foster network, adoption workflow'),
    ('livestock-auction-platform', 'Livestock auction technology platform - lot management, bidding, buyer/seller portal, settlement'),
    ('equine-management-tech', 'Equine management technology platform - health records, training logs, show management, breeding'),
    ('aquarium-zoo-platform', 'Aquarium and zoo management technology platform - animal records, enrichment, visitor experience, care'),
    ('pet-food-subscription', 'Pet food and supplies subscription platform - breed-specific recommendations, auto-delivery, nutrition'),
    # Nonprofit and social services technology
    ('social-services-platform', 'Social services technology platform - case management, referrals, outcome tracking, reporting'),
    ('community-development-platform', 'Community development finance institution platform - loan management, impact metrics, portfolio, grants'),
    ('domestic-violence-platform', 'Domestic violence services technology platform - case management, safety planning, shelter, legal advocacy'),
    ('food-pantry-platform', 'Food pantry and hunger relief platform - inventory management, client intake, distribution, donor management'),
    ('refugee-resettlement-platform', 'Refugee resettlement technology platform - case management, benefits, employment services, integration'),
    ('disability-services-tech', 'Disability services technology platform - accommodation management, assistive tech, compliance, outreach'),
    ('legal-aid-platform', 'Legal aid organization technology platform - intake, case management, court tracking, outcome reporting'),
    ('substance-abuse-treatment', 'Substance abuse treatment technology platform - MAT tracking, group therapy, compliance, outcome data'),
    ('crisis-hotline-platform', 'Crisis hotline technology platform - call routing, counselor management, follow-up, reporting'),
    ('veterans-services-platform', 'Veterans services technology platform - benefits navigation, case management, employment, peer support'),
    # Mining and natural resources technology
    ('mine-management-platform', 'Mine operations management platform - production tracking, equipment management, safety, compliance'),
    ('geological-survey-platform', 'Geological survey technology platform - field data collection, sample tracking, report generation, GIS'),
    ('mineral-rights-platform', 'Mineral rights management platform - lease management, royalty tracking, title research, compliance'),
    ('mining-safety-platform', 'Mining safety management technology platform - incident reporting, inspection, training, regulatory'),
    ('quarry-management-platform', 'Quarry and aggregate management platform - production tracking, inventory, equipment, sales, billing'),
    ('oil-gas-field-platform', 'Oil and gas field management platform - well management, production data, maintenance, regulatory'),
    ('pipeline-management-platform', 'Pipeline operations management platform - asset management, integrity, inspection, compliance, GIS'),
    ('environmental-mining-platform', 'Environmental compliance for mining - monitoring, reporting, reclamation planning, permit tracking'),
    ('mining-supply-chain-platform', 'Mining supply chain technology platform - procurement, inventory, vendor management, logistics'),
    ('rare-earth-mining-platform', 'Rare earth and critical minerals platform - grade tracking, processing, logistics, market analytics'),
    # Recycling and circular economy technology
    ('recycling-facility-platform', 'Recycling facility management platform - material intake, sorting, processing, sales, compliance'),
    ('e-waste-recycling-platform', 'E-waste and electronics recycling platform - device intake, data destruction, material recovery, reporting'),
    ('scrap-metal-platform', 'Scrap metal and ferrous recycling platform - scale tickets, pricing, inventory, compliance, accounts'),
    ('reverse-logistics-tech', 'Reverse logistics technology platform - returns processing, refurbishment, resale, recycling, reporting'),
    ('circular-economy-tech', 'Circular economy technology platform - product lifecycle, take-back programs, material flows, impact'),
    ('battery-recycling-platform', 'Battery recycling technology platform - collection, processing, material recovery, regulatory compliance'),
    ('textile-recycling-platform', 'Textile recycling and resale platform - collection, sorting, grading, resale channels, impact metrics'),
    ('composting-platform', 'Composting and organics management platform - collection routes, processing, quality testing, sales'),
    ('deposit-refund-platform', 'Container deposit and refund technology platform - redemption center management, counting, reporting'),
    ('waste-marketplace-platform', 'Industrial waste marketplace technology - waste classification, exchange, compliance, logistics'),
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
