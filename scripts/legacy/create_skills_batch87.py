
import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # Disaster preparedness and emergency management technology
    ('emergency-preparedness-platform', 'Emergency preparedness and disaster planning platform - risk assessment, resource pre-positioning, alert systems'),
    ('wildfire-management-platform', 'Wildfire incident management and evacuation platform - fire behavior modeling, evacuation routing, resource tracking'),
    ('flood-management-platform', 'Flood emergency management and monitoring platform - gauge data integration, early warning, evacuation coordination'),
    ('earthquake-response-platform', 'Earthquake response and damage assessment platform - impact modeling, survivor locating, resource deployment'),
    ('hurricane-emergency-platform', 'Hurricane tracking and emergency management platform - storm modeling, shelter management, utility coordination'),
    ('disaster-relief-platform', 'Disaster relief operations and humanitarian response platform - resource distribution, volunteer coordination, logistics'),
    ('community-resilience-platform', 'Community resilience and disaster preparedness platform - neighborhood planning, resource mapping, drills'),
    ('crisis-mapping-platform', 'Crisis mapping and situational awareness platform - real-time data aggregation, interactive maps, crowdsourcing'),
    ('mass-casualty-platform', 'Mass casualty incident management platform - triage tracking, hospital capacity, victim family notification'),
    ('emergency-shelter-management', 'Emergency shelter management and tracking platform - capacity management, registration, resource allocation, pets'),
    # Auction and liquidation technology
    ('online-auction-tech-platform', 'Online auction technology platform - bidding engine, payment processing, seller/buyer management, analytics'),
    ('government-auction-platform', 'Government and surplus asset auction platform - GSA compliance, asset listing, sealed bids, reporting'),
    ('bank-repo-auction-platform', 'Bank repossession and foreclosure auction platform - asset management, legal compliance, online bidding'),
    ('industrial-auction-platform', 'Industrial equipment auction and remarketing platform - equipment valuation, inspection reports, transport'),
    ('art-auction-tech-platform', 'Art auction technology and gallery sales platform - provenance tracking, authentication, condition reports'),
    ('charity-auction-tech-platform', 'Charity fundraising auction technology platform - item donation, bidding, tax receipt generation, analytics'),
    ('real-time-auction-platform', 'Real-time live auction broadcasting platform - video streaming, simultaneous bidding, auctioneer tools'),
    ('collectibles-auction-platform', 'Collectibles and memorabilia auction platform - grading integration, authentication, buyer protection'),
    ('livestock-online-auction', 'Online livestock auction and marketing platform - animal data, video, health records, settlement'),
    ('timber-auction-platform', 'Timber and forest products auction platform - cruise data, contract management, bidding, settlement'),
    # Addiction and behavioral health technology
    ('addiction-recovery-platform', 'Addiction recovery and substance use disorder platform - care coordination, peer support, meeting finder, sobriety tracking'),
    ('telehealth-addiction-platform', 'Telehealth addiction treatment and MAT platform - virtual counseling, medication management, monitoring'),
    ('recovery-coaching-platform', 'Recovery coaching and peer support platform - coach matching, session scheduling, progress tracking, billing'),
    ('behavioral-health-analytics', 'Behavioral health analytics and outcomes platform - assessment tools, treatment planning, outcomes measurement'),
    ('harm-reduction-platform', 'Harm reduction services and outreach platform - syringe programs, naloxone distribution, case management'),
    ('sober-living-platform', 'Sober living home management and recovery housing platform - occupancy, house rules, drug testing, peer community'),
    ('eating-disorder-platform', 'Eating disorder treatment and recovery platform - meal planning, body image tools, telehealth, community'),
    ('gambling-addiction-platform', 'Problem gambling intervention and recovery platform - self-exclusion, spending tracking, counseling, support'),
    ('digital-addiction-platform', 'Digital addiction and screen time management platform - usage tracking, family controls, treatment tools'),
    ('codependency-recovery-platform', 'Codependency recovery and relationship health platform - self-assessment, therapy tools, group support, resources'),
    # Environmental remediation and cleanup technology
    ('contamination-site-platform', 'Contaminated site assessment and remediation platform - sampling data, remedy design, regulatory tracking'),
    ('hazmat-cleanup-platform', 'Hazardous materials cleanup and disposal platform - manifest management, disposal tracking, compliance, billing'),
    ('brownfield-redevelopment-platform', 'Brownfield site redevelopment and cleanup platform - site assessment, regulatory interface, cost tracking'),
    ('oil-spill-response-platform', 'Oil spill response and remediation platform - spill tracking, resource deployment, cleanup monitoring'),
    ('industrial-wastewater-platform', 'Industrial wastewater treatment and management platform - effluent monitoring, permit compliance, reporting'),
    ('stormwater-management-platform', 'Stormwater management and MS4 compliance platform - runoff modeling, BMP tracking, permit reporting'),
    ('air-emissions-platform', 'Air emissions monitoring and compliance platform - continuous monitoring, permit management, reporting'),
    ('soil-remediation-platform', 'Soil contamination assessment and remediation platform - sampling data, treatment technology, progress tracking'),
    ('groundwater-remediation', 'Groundwater remediation and monitoring platform - well data, treatment system monitoring, regulatory reporting'),
    ('decommissioning-platform', 'Facility decommissioning and demolition management platform - hazmat surveys, waste tracking, compliance, costs'),
    # Specialty hospitality and accommodation technology
    ('boutique-hotel-platform', 'Boutique hotel management and guest experience platform - PMS, personalization, local experiences, reputation'),
    ('hostel-management-platform', 'Hostel and budget accommodation management platform - bed management, shared facilities, international guests'),
    ('glamping-platform', 'Glamping and luxury camping management platform - site management, booking, amenity scheduling, guest experience'),
    ('treehouse-resort-platform', 'Treehouse and unique accommodation platform - property management, booking, guest experience, maintenance'),
    ('houseboat-platform', 'Houseboat and floating accommodation management platform - marina integration, boat systems, booking, guest services'),
    ('castle-estate-platform', 'Historic castle and estate rental management platform - event venue, accommodation booking, preservation, tours'),
    ('monasteries-retreat-platform', 'Monastery and spiritual retreat accommodation platform - program scheduling, silence policy, dietary management'),
    ('farm-stay-platform', 'Farm stay and agritourism accommodation platform - booking, farm activity scheduling, seasonal management'),
    ('submarine-hotel-platform', 'Underwater and submarine hotel management platform - dive operations, safety protocols, booking, maintenance'),
    ('ice-hotel-platform', 'Ice hotel and frozen accommodation management platform - seasonal construction, booking, guest safety, activities'),
    # Immigration and citizenship technology
    ('immigration-case-management', 'Immigration case management and attorney platform - case tracking, document management, deadline alerts, billing'),
    ('visa-application-platform', 'Visa application and processing management platform - form completion, document collection, status tracking'),
    ('naturalization-platform', 'Naturalization and citizenship application platform - eligibility checking, application preparation, civics test prep'),
    ('immigration-compliance-platform', 'Immigration compliance and I-9 management platform - employee verification, audit preparation, reporting'),
    ('asylum-case-platform', 'Asylum application and refugee status platform - case management, hearing preparation, legal representation'),
    ('daca-platform', 'DACA and deferred action management platform - renewal tracking, work authorization, legal support'),
    ('deportation-defense-platform', 'Deportation defense and removal proceedings platform - case management, bond hearings, appeals, legal research'),
    ('immigration-bond-platform', 'Immigration bond and detention management platform - bond tracking, family communication, release coordination'),
    ('work-visa-platform', 'Work visa and employment authorization platform - petition management, labor condition applications, tracking'),
    ('global-mobility-platform', 'Global mobility and expatriate management platform - assignment tracking, immigration compliance, relocation support'),
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
