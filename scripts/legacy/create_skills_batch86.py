
import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # Cannabis cultivation and production technology
    ('cannabis-cultivation-platform', 'Cannabis cultivation and grow management platform - strain tracking, grow cycles, yield optimization, compliance'),
    ('cannabis-dispensary-tech', 'Cannabis dispensary point-of-sale and compliance platform - inventory, age verification, state reporting, loyalty'),
    ('cannabis-delivery-platform', 'Cannabis delivery and logistics platform - order management, driver dispatch, compliance, tracking'),
    ('cannabis-testing-lab-platform', 'Cannabis testing laboratory management platform - sample intake, COA generation, compliance, client portal'),
    ('hemp-processing-platform', 'Hemp processing and extraction facility platform - batch management, extraction records, QC, compliance'),
    ('cannabis-wholesale-platform', 'Cannabis wholesale distribution platform - order management, license verification, delivery, reporting'),
    ('cannabis-brand-platform', 'Cannabis brand and marketing platform - compliant advertising, dispensary placement, analytics, compliance'),
    ('cannabis-compliance-platform', 'Cannabis regulatory compliance management platform - license tracking, seed-to-sale, state reporting'),
    ('cannabis-real-estate-platform', 'Cannabis real estate and facility leasing platform - zoning compliance, facility requirements, broker tools'),
    ('psychedelics-research-platform', 'Psychedelics clinical research and therapy platform - IRB management, dosing protocols, outcome tracking'),
    # Micro-mobility and urban transportation technology
    ('escooter-fleet-platform', 'Electric scooter fleet management and sharing platform - fleet deployment, charging management, trip data, revenue'),
    ('ebike-sharing-platform', 'Electric bike sharing and subscription platform - fleet management, docking, maintenance, trip analytics'),
    ('micro-mobility-platform', 'Micro-mobility operations management platform - multi-modal fleet, permit management, city partnerships'),
    ('cargo-bike-platform', 'Cargo bike and last-mile delivery platform - fleet management, route optimization, charging, billing'),
    ('electric-moped-platform', 'Electric moped sharing and fleet management platform - booking, geofencing, helmet management, insurance'),
    ('dockless-mobility-platform', 'Dockless mobility and shared transportation platform - vehicle tracking, parking compliance, user management'),
    ('transit-tech-platform', 'Public transit technology and operations platform - scheduling, real-time tracking, passenger information'),
    ('parking-technology-platform', 'Smart parking technology and management platform - occupancy sensors, reservation, payment, enforcement'),
    ('autonomous-shuttle-platform', 'Autonomous shuttle and fixed-route operations platform - route management, passenger safety, fleet monitoring'),
    ('mobility-hub-platform', 'Mobility hub and multi-modal transportation platform - mode integration, trip planning, payment, analytics'),
    # Indigenous and minority business technology
    ('indigenous-business-platform', 'Indigenous and Native American business marketplace platform - tribal enterprise support, cultural authenticity, compliance'),
    ('minority-business-platform', 'Minority-owned business marketplace and certification platform - MBE certification, supplier diversity, connections'),
    ('women-business-platform', 'Women-owned business certification and marketplace platform - WOSB certification, contracting, community, resources'),
    ('veteran-business-platform', 'Veteran-owned business certification and marketplace platform - VOSB/SDVOSB certification, federal contracting, support'),
    ('lgbtq-business-platform', 'LGBTQ-owned business certification and directory platform - certification, marketplace, community, advocacy'),
    ('disability-business-platform', 'Disability-owned business certification and marketplace platform - DBE certification, accessibility tools, supplier diversity'),
    ('rural-business-platform', 'Rural and agricultural business marketplace platform - rural certification, USDA programs, market access, resources'),
    ('social-enterprise-marketplace', 'Social enterprise and B-corp marketplace platform - impact metrics, certification, consumer connections, reporting'),
    ('fair-trade-marketplace', 'Fair trade certified product marketplace platform - certification verification, producer stories, supply chain'),
    ('cooperative-platform', 'Worker cooperative and collective business platform - democratic governance, profit sharing, membership, compliance'),
    # Home services aggregator and marketplace technology
    ('home-services-marketplace', 'Home services aggregator and booking marketplace platform - pro matching, instant booking, reviews, payments'),
    ('handyman-marketplace-platform', 'Handyman and general repair services marketplace platform - skill matching, scheduling, reviews, insurance verification'),
    ('home-renovation-marketplace', 'Home renovation and contractor marketplace platform - project posting, bid management, milestone payments'),
    ('appliance-repair-marketplace', 'Appliance repair services marketplace platform - brand specialization, parts sourcing, warranty tracking, scheduling'),
    ('emergency-home-services-platform', 'Emergency home repair and services platform - 24/7 dispatch, licensed pros, insurance billing, tracking'),
    ('smart-home-services-platform', 'Smart home installation services marketplace platform - device expertise, certification, scheduling, remote support'),
    ('seasonal-home-services-platform', 'Seasonal home maintenance services platform - service bundles, reminder scheduling, pro matching, reviews'),
    ('home-cleaning-marketplace', 'Home cleaning services marketplace platform - cleaner vetting, recurring booking, supplies, reviews, payments'),
    ('moving-services-marketplace', 'Moving and relocation services marketplace platform - truck sizing, labor booking, storage, reviews, insurance'),
    ('home-warranty-tech-platform', 'Home warranty and service contract technology platform - coverage management, claim submission, pro dispatch'),
    # Caregiver and elder care marketplace technology
    ('caregiver-marketplace', 'Caregiver and home care aide marketplace platform - background checks, certification verification, scheduling, payments'),
    ('elder-care-marketplace', 'Elder care services marketplace and coordination platform - care matching, care plans, family portal, billing'),
    ('senior-companion-platform', 'Senior companion and social engagement platform - companion matching, activity scheduling, family updates'),
    ('respite-care-platform', 'Respite care and caregiver relief platform - temporary care matching, scheduling, family coordination'),
    ('dementia-care-platform', 'Dementia and Alzheimer care specialized platform - care protocols, family education, safety monitoring, billing'),
    ('in-home-nursing-platform', 'In-home nursing and skilled care marketplace platform - RN/LPN matching, care plan management, insurance billing'),
    ('disability-support-marketplace', 'Disability support worker marketplace platform - NDIS/Medicaid compliance, skill matching, scheduling, payments'),
    ('adult-day-care-platform', 'Adult day care program management platform - enrollment, activity scheduling, transportation, health monitoring'),
    ('senior-moving-platform', 'Senior move management and downsizing platform - estate sale integration, senior move specialists, storage'),
    ('aging-care-coordination-platform', 'Aging care coordination and navigation platform - benefits assessment, care coordination, family portal'),
    # Genealogy and ancestry technology
    ('genealogy-dna-platform', 'Genealogy DNA testing and ancestry platform - DNA matching, family tree integration, ethnicity estimates'),
    ('family-history-platform', 'Family history research and preservation platform - document management, oral histories, family publishing'),
    ('vital-records-retrieval-platform', 'Vital records retrieval and document ordering platform - birth/death/marriage certificates, apostille, delivery'),
    ('cemetery-genealogy-platform', 'Cemetery and burial records genealogy platform - grave mapping, transcription, photograph management'),
    ('ancestral-travel-platform', 'Ancestral heritage travel and genealogy tourism platform - destination planning, local genealogists, DNA tours'),
    ('immigrant-genealogy-platform', 'Immigrant and ship passenger records research platform - database access, naturalization records, surname search'),
    ('military-genealogy-platform', 'Military records and veteran genealogy research platform - service records, pension files, burial records'),
    ('surname-registry-platform', 'Surname registry and family association management platform - member directory, reunion planning, newsletter'),
    ('one-name-study-platform', 'One-name study and surname research platform - worldwide family tree, DNA project, research collaboration'),
    ('adoptee-search-platform', 'Adoptee and birth family search and reunion platform - DNA matching, records search, reunion coordination, counseling'),
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
