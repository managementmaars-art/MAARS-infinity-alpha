
import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # Creative economy and film/TV production technology
    ('film-production-platform', 'Film and TV production platform - script breakdown, scheduling, budgeting, crew management, call sheets'),
    ('post-production-platform', 'Post-production technology platform - editorial workflow, VFX pipeline, color grading, sound, delivery'),
    ('casting-platform', 'Casting technology platform - talent database, audition management, self-tape, virtual casting, contracts'),
    ('music-production-platform', 'Music production platform - DAW integration, stem management, session booking, collaboration, mastering'),
    ('content-rights-management', 'Content rights management platform - rights clearance, licensing, royalty tracking, territory management'),
    ('animation-production-platform', 'Animation production platform - asset management, render farm, pipeline tools, review, delivery'),
    ('vfx-pipeline-platform', 'VFX pipeline platform - shot tracking, render management, review tools, versioning, DCC integration'),
    ('game-development-platform', 'Game development platform - version control, build automation, QA tracking, asset management, analytics'),
    ('podcast-production-platform', 'Podcast production platform - recording workflow, editing tools, transcript, distribution, monetization'),
    ('creator-economy-platform', 'Creator economy platform - content monetization, fan subscription, merchandise, analytics, brand deals'),
    # Social services and community technology
    ('social-services-case-management', 'Social services case management - intake, eligibility, service plans, referrals, outcomes tracking'),
    ('homelessness-tech-platform', 'Homelessness services technology - HMIS, coordinated entry, shelter management, housing navigation'),
    ('food-bank-platform', 'Food bank and pantry platform - inventory management, client intake, donor management, distribution'),
    ('community-health-worker-platform', 'Community health worker platform - patient outreach, social determinants, referral, care coordination'),
    ('benefits-navigation-platform', 'Benefits navigation platform - eligibility screening, enrollment assistance, document management'),
    ('child-welfare-platform', 'Child welfare technology platform - case management, family services, foster care, adoption, SACWIS'),
    ('disability-services-platform', 'Disability services technology platform - support coordination, funding management, provider portal'),
    ('senior-services-platform', 'Senior services technology platform - IADL assessment, caregiver coordination, transportation, meals'),
    ('reentry-services-platform', 'Reentry services platform - justice-involved individuals, employment, housing, benefits, mentorship'),
    ('refugee-services-platform', 'Refugee and immigrant services platform - case tracking, language support, resettlement, integration'),
    # Veterinary and pet care technology
    ('veterinary-practice-management', 'Veterinary practice management - PIMS, appointment booking, medical records, prescriptions, billing'),
    ('pet-health-platform', 'Pet health technology platform - wellness tracking, vaccine reminders, telehealth, wearables, nutrition'),
    ('veterinary-diagnostic-platform', 'Veterinary diagnostic platform - lab integration, imaging, pathology, telemedicine specialist referral'),
    ('pet-insurance-platform', 'Pet insurance technology platform - quoting, policy management, claims processing, wellness plans'),
    ('animal-shelter-platform', 'Animal shelter management platform - intake, adoption, foster, medical records, licensing, fundraising'),
    ('livestock-health-platform', 'Livestock health management platform - disease monitoring, vaccination, herd health, production'),
    ('equine-management-platform', 'Equine management technology platform - horse health records, training logs, competition, breeding'),
    ('zoo-aquarium-platform', 'Zoo and aquarium management platform - animal records, medical, husbandry, breeding, studbooks'),
    ('pet-grooming-platform', 'Pet grooming and boarding platform - appointment scheduling, service packages, client communications'),
    ('veterinary-pharmacy-platform', 'Veterinary pharmacy platform - prescription management, compounding, controlled substances, dispensing'),
    # Personal finance and consumer fintech
    ('personal-budgeting-platform', 'Personal budgeting platform - account aggregation, spending categorization, goal setting, alerts'),
    ('consumer-tax-platform', 'Consumer tax technology platform - tax filing, deduction optimization, tax planning, audit support'),
    ('investment-education-platform', 'Investment education platform - financial literacy, simulated trading, portfolio building, coaching'),
    ('debt-management-platform', 'Debt management technology platform - debt tracking, payoff strategies, negotiation tools, credit score'),
    ('financial-planning-platform', 'Financial planning technology platform - life goals, retirement, insurance, estate, advisor matching'),
    ('micro-investing-platform', 'Micro-investing platform - round-ups, fractional shares, thematic portfolios, automated investing'),
    ('bill-negotiation-platform', 'Bill negotiation technology platform - subscription tracking, negotiation automation, savings tracking'),
    ('credit-building-platform', 'Credit building technology platform - secured cards, credit builder loans, rent reporting, monitoring'),
    ('cash-advance-platform', 'Cash advance and earned wage access platform - payroll integration, on-demand pay, repayment'),
    ('financial-wellness-platform', 'Financial wellness technology platform - employee benefits, coaching, tools, savings, debt payoff'),
    # Arts and cultural institution technology
    ('museum-management-platform', 'Museum management platform - collections management, ticketing, exhibitions, visitor analytics, education'),
    ('gallery-platform', 'Art gallery technology platform - inventory management, artist CRM, sales tracking, consignment, provenance'),
    ('performing-arts-platform', 'Performing arts technology platform - ticketing, box office, season management, donor engagement'),
    ('library-management-advanced', 'Library management system advanced - ILS, digital collections, cataloging, patron services, analytics'),
    ('archive-management-platform', 'Digital archive management platform - digitization workflows, metadata, preservation, access control'),
    ('cultural-heritage-platform', 'Cultural heritage technology platform - 3D scanning, virtual tours, preservation, community engagement'),
    ('art-marketplace-platform', 'Art marketplace technology platform - authentication, provenance tracking, fractional ownership, NFT'),
    ('music-venue-platform', 'Music venue management platform - booking, ticketing, production management, artist settlement, FOH'),
    ('festival-management-platform', 'Festival and event management platform - lineup, ticketing, vendor management, volunteer, RFID'),
    ('public-art-platform', 'Public art management platform - commission management, artist database, project tracking, community'),
    # Faith and religious organization technology
    ('church-management-platform', 'Church management platform - ChMS, member management, giving, check-in, small groups, events'),
    ('online-giving-platform', 'Online giving and stewardship platform - recurring donations, pledges, text-to-give, reporting'),
    ('ministry-management-platform', 'Ministry management technology platform - volunteer coordination, curriculum, outreach, communication'),
    ('faith-community-platform', 'Faith community engagement platform - small groups, prayer requests, digital community, content'),
    ('religious-education-platform', 'Religious education technology platform - curriculum management, attendance, teacher tools, families'),
    ('mosque-management-platform', 'Mosque management technology platform - prayer times, Islamic calendar, zakat, halal certification'),
    ('synagogue-management-platform', 'Synagogue management platform - membership, lifecycle events, High Holiday seating, education'),
    ('multi-site-ministry-platform', 'Multi-site ministry technology platform - campus management, content sharing, unified reporting'),
    ('faith-based-nonprofit-platform', 'Faith-based nonprofit technology platform - donor management, programs, volunteer, community impact'),
    ('chaplaincy-platform', 'Chaplaincy and spiritual care platform - hospital chaplaincy, military, corporate, session tracking'),
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
