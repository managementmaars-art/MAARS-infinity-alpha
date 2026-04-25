
import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # Mushroom and specialty agriculture technology
    ('mushroom-cultivation-platform', 'Mushroom cultivation and specialty fungi farm platform - grow room management, substrate batches, harvest tracking, wholesale'),
    ('csa-farm-platform', 'Community-supported agriculture CSA management platform - share management, box assembly, pickup scheduling, member portal'),
    ('microgreens-farm-platform', 'Microgreens and sprout farm management platform - tray scheduling, variety tracking, restaurant delivery, subscriptions'),
    ('aquaponics-platform', 'Aquaponics and hydroponic farm management platform - system monitoring, fish health, nutrient dosing, harvest tracking'),
    ('beekeeping-platform', 'Beekeeping and apiary management platform - hive inspections, honey extraction, swarm tracking, product sales'),
    ('goat-farm-platform', 'Goat farm and dairy management platform - herd records, milk production, cheese making, kidding schedules'),
    ('alpaca-farm-platform', 'Alpaca and llama farm management platform - herd records, fiber production, shearing scheduling, sales'),
    ('lavender-farm-platform', 'Lavender farm and agritourism platform - field management, U-pick booking, product processing, retail'),
    ('flower-farm-platform', 'Cut flower farm management platform - crop planning, CSA shares, farmers market, wholesale floral accounts'),
    ('hemp-cbd-farm-platform', 'Hemp and CBD cultivation management platform - DEA licensing, COA tracking, extraction batches, compliance'),
    # Board game and tabletop gaming culture technology
    ('board-game-cafe-platform', 'Board game café management platform - table reservations, game library management, food/drink POS, events'),
    ('tabletop-rpg-platform', 'Tabletop RPG campaign management platform - campaign tracking, character sheets, session scheduling, group finder'),
    ('game-design-platform', 'Tabletop game design and publishing platform - playtesting management, rulebook versioning, Kickstarter, manufacturing'),
    ('miniature-painting-platform', 'Miniature painting and wargaming studio platform - commission workflow, painting stages, client gallery, supply'),
    ('wargaming-club-platform', 'Wargaming club and tournament management platform - event scheduling, army lists, ranking system, venue booking'),
    ('trading-card-game-platform', 'Trading card game tournament and store platform - event management, deck registration, standings, prize support'),
    ('escape-room-design-platform', 'Escape room design and consulting platform - puzzle design tools, client projects, testing, installation'),
    ('trivia-night-platform', 'Trivia night and quiz event management platform - question bank, scoring system, venue partnerships, leaderboards'),
    ('larp-platform', 'Live action roleplay LARP event management platform - event registration, character creation, rule systems, scheduling'),
    ('puzzle-subscription-platform', 'Puzzle and brain teaser subscription box platform - curation, difficulty tracking, subscriber management, shipping'),
    # Therapy and expressive arts practices technology
    ('art-therapy-platform', 'Art therapy practice management platform - client session notes, artwork documentation, treatment goals, billing'),
    ('music-therapy-platform', 'Music therapy practice management platform - session protocols, instrument tracking, goal documentation, billing'),
    ('dance-movement-therapy-platform', 'Dance and movement therapy practice platform - session scheduling, documentation, group programs, billing'),
    ('drama-therapy-platform', 'Drama therapy and psychodrama practice platform - session notes, group management, protocol tracking, billing'),
    ('equine-therapy-platform', 'Equine-assisted therapy practice platform - horse and rider scheduling, session documentation, billing'),
    ('horticultural-therapy-platform', 'Horticultural therapy practice platform - garden session planning, patient progress, plant tracking, billing'),
    ('animal-assisted-therapy-platform', 'Animal-assisted therapy practice platform - handler and animal certification, session records, referrals'),
    ('play-therapy-platform', 'Play therapy practice management platform - toy room management, session documentation, parent reports, billing'),
    ('sand-tray-therapy-platform', 'Sand tray therapy practice platform - figurine catalog, session documentation, photo records, treatment planning'),
    ('somatic-therapy-platform', 'Somatic therapy and body-based practice platform - intake assessments, session notes, trauma protocols, billing'),
    # Specialty law practice technology
    ('maritime-law-platform', 'Maritime law practice management platform - admiralty cases, vessel tracking, cargo claims, Jones Act, billing'),
    ('aviation-law-platform', 'Aviation law practice management platform - FAA compliance, accident investigation, manufacturer liability, billing'),
    ('elder-law-platform', 'Elder law practice management platform - estate planning, Medicaid planning, guardianship, long-term care, billing'),
    ('adoption-law-platform', 'Adoption law practice management platform - case workflow, home study coordination, court filings, billing'),
    ('military-law-platform', 'Military law and veterans benefits practice platform - UCMJ cases, VA claims, discharge upgrades, billing'),
    ('tribal-law-platform', 'Tribal law and indigenous rights practice platform - sovereignty issues, treaty rights, tribal court, billing'),
    ('space-law-platform', 'Space law and commercial space practice platform - launch licensing, satellite regulations, liability, contracts'),
    ('cannabis-law-platform', 'Cannabis law practice management platform - licensing applications, regulatory compliance, contracts, billing'),
    ('crypto-law-platform', 'Cryptocurrency and blockchain law practice platform - regulatory matters, token compliance, DeFi, DAO, billing'),
    ('influencer-law-platform', 'Influencer and creator law practice platform - brand deals, IP, defamation, FTC compliance, billing'),
    # Staffing and talent placement technology
    ('creative-staffing-platform', 'Creative staffing agency management platform - talent roster, project matching, portfolio, time tracking, billing'),
    ('tech-staffing-platform', 'Technology staffing agency platform - developer matching, skills assessment, contract management, billing'),
    ('healthcare-staffing-advanced', 'Healthcare staffing agency advanced platform - credential verification, shift management, compliance, billing'),
    ('legal-staffing-platform', 'Legal staffing and attorney placement platform - bar verification, case matching, contract attorneys, billing'),
    ('executive-search-platform', 'Executive search and headhunter platform - candidate management, client engagement, interview coordination'),
    ('gig-economy-platform', 'Gig economy and freelancer marketplace platform - skill matching, rating system, payment processing, disputes'),
    ('seasonal-staffing-platform', 'Seasonal and temporary staffing platform - mass hiring, onboarding, scheduling, bulk payroll, compliance'),
    ('diversity-staffing-platform', 'Diversity and inclusion staffing platform - diverse candidate sourcing, DEI metrics, client reporting, billing'),
    ('government-contractor-staffing', 'Government contractor staffing platform - security clearance tracking, contract vehicles, compliance'),
    ('entertainment-casting-platform', 'Entertainment casting and talent agency platform - actor profiles, audition management, contracts, billing'),
    # Cultural and community center technology
    ('cultural-center-platform', 'Cultural center management platform - program scheduling, language classes, cultural events, membership, grants'),
    ('community-garden-platform', 'Community garden management platform - plot assignments, workday scheduling, harvest sharing, membership'),
    ('makerspace-platform', 'Makerspace and hackerspace management platform - equipment booking, membership, project documentation, safety'),
    ('coworking-space-platform', 'Coworking space management platform - desk/office booking, membership plans, amenities, community events'),
    ('incubator-accelerator-platform', 'Business incubator and accelerator management platform - cohort management, mentorship, milestone tracking'),
    ('neighborhood-association-platform', 'Neighborhood association management platform - dues collection, meeting management, projects, communication'),
    ('civic-engagement-platform', 'Civic engagement and local democracy platform - petition management, town halls, volunteer coordination'),
    ('immigrant-services-platform', 'Immigrant and refugee services organization platform - case management, language access, benefits navigation'),
    ('youth-center-platform', 'Youth center and after-school program platform - enrollment, activity scheduling, attendance, parent portal'),
    ('senior-center-platform', 'Senior center and aging services platform - program scheduling, transportation coordination, meal programs'),
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
