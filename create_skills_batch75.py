
import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # Performing arts and entertainment technology
    ('comedy-club-platform', 'Comedy club and stand-up management platform - booking, ticketing, talent management, show production'),
    ('magic-entertainment-platform', 'Magic and illusion entertainment platform - booking, show management, prop tracking, tour logistics'),
    ('burlesque-cabaret-platform', 'Burlesque and cabaret venue management platform - performer booking, show scheduling, ticket sales'),
    ('circus-arts-platform', 'Circus arts and aerial performance platform - training management, production, booking, safety compliance'),
    ('improv-theater-platform', 'Improv and sketch comedy theater platform - class scheduling, show management, membership, box office'),
    ('open-mic-platform', 'Open mic and live music venue platform - event management, talent booking, ticketing, sound production'),
    ('karaoke-venue-platform', 'Karaoke venue management platform - room reservations, song library management, food service, loyalty'),
    ('comedy-writing-platform', 'Comedy writing and development platform - script management, punchline tracking, pitch scheduling, rights'),
    ('talent-show-platform', 'Talent show and competition management platform - registration, judging, scoring, audience voting, live streaming'),
    ('variety-show-platform', 'Variety show production management platform - act booking, production scheduling, set design, billing'),
    # Legal services niche technology
    ('immigration-law-platform', 'Immigration law practice technology platform - case tracking, USCIS forms, client portal, status alerts'),
    ('family-law-platform', 'Family law practice technology platform - divorce, custody, support calculations, document assembly'),
    ('criminal-defense-platform', 'Criminal defense practice technology platform - case management, court dates, plea tracking, client portal'),
    ('personal-injury-platform', 'Personal injury law platform - case management, medical liens, settlement tracking, demand letters'),
    ('estate-attorney-platform', 'Estate planning attorney platform - document drafting, trust administration, probate, beneficiary management'),
    ('corporate-law-platform', 'Corporate law practice technology platform - entity management, board minutes, cap table, compliance'),
    ('intellectual-property-law', 'Intellectual property law practice platform - patent/trademark prosecution, docketing, client portal'),
    ('real-estate-law-platform', 'Real estate law practice technology platform - transaction management, title, closing, escrow tracking'),
    ('employment-law-platform', 'Employment law practice technology platform - discrimination cases, wage claims, EEOC, arbitration'),
    ('bankruptcy-law-platform', 'Bankruptcy law practice technology platform - means test, schedules, 341 hearings, plan management'),
    # Health and wellness studio technology
    ('yoga-studio-platform', 'Yoga studio management technology platform - class scheduling, membership, teacher management, billing'),
    ('pilates-studio-platform', 'Pilates studio management platform - reformer reservations, client profiles, package management, billing'),
    ('barre-studio-platform', 'Barre fitness studio management platform - class booking, membership, retail, instructor scheduling'),
    ('crossfit-gym-platform', 'CrossFit and functional fitness gym platform - WOD tracking, membership, competition management, billing'),
    ('martial-arts-platform', 'Martial arts school management platform - belt tracking, class scheduling, tournament registration, billing'),
    ('boxing-gym-platform', 'Boxing and combat sports gym platform - training sessions, sparring scheduling, fight camp management'),
    ('rock-climbing-gym-platform', 'Rock climbing gym management platform - wall route setting, membership, waiver, day passes, events'),
    ('swimming-pool-platform', 'Swimming pool and aquatics facility platform - lane reservations, lessons, team management, billing'),
    ('cycle-studio-platform', 'Indoor cycling and spin studio platform - bike reservations, class scheduling, performance tracking, billing'),
    ('wellness-retreat-platform', 'Wellness retreat and destination spa management platform - retreat booking, itinerary, meals, excursions'),
    # Specialty medical and clinical technology
    ('telehealth-mental-health', 'Telehealth mental health platform - HIPAA video therapy, intake, scheduling, billing, crisis resources'),
    ('wound-care-platform', 'Wound care clinic technology platform - wound measurement, photography, treatment protocols, billing'),
    ('infusion-clinic-platform', 'Infusion and IV therapy clinic platform - scheduling, drug procurement, chair management, nursing notes'),
    ('sleep-clinic-platform', 'Sleep clinic management platform - polysomnography, CPAP supply management, titration, billing'),
    ('hyperbaric-platform', 'Hyperbaric oxygen therapy platform - chamber scheduling, treatment logs, insurance billing, compliance'),
    ('concierge-medicine-platform', 'Concierge and direct primary care platform - membership billing, unlimited access, wellness planning'),
    ('functional-medicine-platform', 'Functional medicine practice platform - root cause analysis, lab panels, personalized protocols'),
    ('regenerative-medicine-platform', 'Regenerative medicine clinic platform - stem cell, PRP therapy, informed consent, outcome tracking'),
    ('weight-loss-clinic-platform', 'Medical weight loss clinic technology platform - program management, body composition, medication, billing'),
    ('aesthetics-med-spa-platform', 'Medical aesthetics and med-spa platform - treatment tracking, before/after photos, consent, billing'),
    # Event services and wedding industry technology
    ('wedding-planning-platform', 'Wedding planning technology platform - vendor management, budget tracking, timeline, guest management'),
    ('wedding-venue-platform', 'Wedding venue management platform - availability calendar, event coordination, catering, billing'),
    ('florist-platform', 'Florist and floral design management platform - order management, delivery scheduling, event planning, billing'),
    ('wedding-photography-tech', 'Wedding photography and videography platform - inquiry management, contracts, gallery delivery, albums'),
    ('dj-entertainment-platform', 'DJ and entertainment services platform - booking management, music library, equipment tracking, billing'),
    ('event-rental-platform', 'Event equipment rental platform - inventory management, delivery scheduling, damage tracking, billing'),
    ('catering-company-platform', 'Catering company management platform - event proposals, menu management, kitchen prep, staffing, billing'),
    ('photo-booth-platform', 'Photo booth rental services platform - booking, customization options, digital delivery, social sharing'),
    ('wedding-dress-platform', 'Bridal boutique and wedding dress management platform - appointments, fittings, alterations, inventory'),
    ('honeymoon-travel-platform', 'Honeymoon and couples travel planning platform - package customization, booking, registry integration'),
    # Childcare subsidy and child welfare technology
    ('child-support-platform', 'Child support enforcement technology platform - payment processing, case management, compliance reporting'),
    ('foster-care-platform', 'Foster care management technology platform - placement matching, case management, court reporting, training'),
    ('adoption-services-platform', 'Adoption services technology platform - home study management, matching, legal process, post-placement'),
    ('early-intervention-platform', 'Early intervention services platform - IFSP management, therapy scheduling, progress reporting, billing'),
    ('head-start-platform', 'Head Start and early childhood program platform - enrollment, developmental screening, family services, reporting'),
    ('child-protective-services', 'Child protective services technology platform - investigation management, safety planning, court reports'),
    ('kinship-care-platform', 'Kinship care and relative placement platform - family assessment, support services, legal assistance'),
    ('teen-parent-services-platform', 'Teen parent services technology platform - case management, education support, childcare assistance'),
    ('child-abuse-prevention-tech', 'Child abuse prevention technology platform - training, risk assessment, resource referrals, reporting'),
    ('youth-development-platform', 'Youth development program technology platform - enrollment, mentoring, activities, outcomes, funding'),
    # Sports and recreation management technology
    ('youth-sports-platform', 'Youth sports league management platform - registration, scheduling, standings, volunteer management, billing'),
    ('adult-recreation-platform', 'Adult recreational sports league platform - team registration, scheduling, stats, playoffs, communication'),
    ('sports-facility-platform', 'Sports facility management technology platform - court/field reservations, leagues, tournaments, billing'),
    ('swim-team-platform', 'Competitive swim team management platform - practice scheduling, meet entries, timing, results, billing'),
    ('tennis-club-platform', 'Tennis club management platform - court reservations, lessons, tournaments, membership, pro shop'),
    ('golf-club-management-platform', 'Golf club management platform - tee time reservations, membership, lessons, handicap, tournaments'),
    ('youth-camp-platform', 'Youth summer camp management platform - registration, cabins, activities, dietary needs, parent portal'),
    ('sports-complex-platform', 'Multi-sport complex management platform - facility scheduling, leagues, events, concessions, billing'),
    ('esports-tournament-platform', 'Esports tournament management platform - bracket management, live streaming, prize distribution, stats'),
    ('outdoor-adventure-platform', 'Outdoor adventure and guide service platform - tour booking, equipment, waivers, guide scheduling'),
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
