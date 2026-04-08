
import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # Retail technology deep
    ('pos-system-advanced', 'Point of sale system advanced - omnichannel POS, payment terminals, loyalty, inventory sync, BOPIS'),
    ('retail-merchandising-platform', 'Retail merchandising platform - assortment planning, space management, planogram, category management'),
    ('retail-erp-advanced', 'Retail ERP advanced - JDA, Manhattan, Blue Yonder, retail-specific modules, seasonal planning'),
    ('loss-prevention-technology', 'Loss prevention technology - video analytics, shrinkage reduction, RFID gates, EAS, case management'),
    ('retail-pricing-platform', 'Retail pricing platform - competitive pricing, markdown optimization, price elasticity, promotion'),
    ('retail-workforce-management', 'Retail workforce management - labor scheduling, task management, compliance, store operations'),
    ('commerce-cloud-platform', 'Commerce cloud platform - Salesforce Commerce Cloud, SAP Commerce, headless architecture'),
    ('omnichannel-fulfillment', 'Omnichannel fulfillment platform - BOPIS, ship-from-store, order routing, inventory visibility'),
    ('retail-data-analytics-advanced', 'Retail data analytics advanced - basket analysis, customer segmentation, store performance, shopper'),
    ('fashion-retail-platform', 'Fashion retail technology platform - PLM, size optimization, trend forecasting, visual merchandising'),
    # Hospitality and travel technology
    ('hotel-pms-advanced', 'Hotel PMS advanced - Opera, Protel, room inventory, rate management, channel manager, PCI'),
    ('restaurant-management-advanced', 'Restaurant management advanced - table management, kitchen display, recipe costing, labor scheduling'),
    ('travel-booking-platform-advanced', 'Travel booking platform advanced - GDS integration, NDC, dynamic packaging, booking engine'),
    ('airline-distribution-platform', 'Airline distribution platform - NDC API, offer management, order management, PSS integration'),
    ('revenue-management-hospitality', 'Revenue management hospitality - RMS, dynamic pricing, demand forecasting, channel optimization'),
    ('events-venue-platform', 'Events and venue management platform - event booking, catering, AV management, SMERF segments'),
    ('spa-wellness-platform', 'Spa and wellness technology platform - booking, treatment management, membership, retail, intake'),
    ('loyalty-hospitality-platform', 'Loyalty and hospitality platform - points economy, tier management, partner integration, redemption'),
    ('fleet-management-travel', 'Fleet management travel and tourism - bus/coach operations, tour scheduling, driver management'),
    ('cruise-ship-technology', 'Cruise ship technology platform - cabin management, excursions, onboard commerce, embarkation'),
    # Agriculture and agritech platform
    ('precision-ag-advanced', 'Precision agriculture advanced - variable rate application, yield mapping, NDVI analysis, prescription maps'),
    ('farm-management-advanced', 'Farm management advanced - agronomy decisions, input tracking, compliance, record keeping, subsidies'),
    ('crop-protection-platform', 'Crop protection technology platform - pest scouting, IPM, spray planning, resistance management'),
    ('livestock-management-advanced', 'Livestock management advanced - herd tracking, breeding records, health protocols, traceability, EID'),
    ('aquaculture-tech-advanced', 'Aquaculture technology advanced - biomass estimation, feeding optimization, water quality, harvest'),
    ('agri-supply-chain-advanced', 'Agricultural supply chain advanced - grain elevator, crop marketing, contract management, transport'),
    ('food-safety-traceability', 'Food safety and traceability platform - GS1, FSMA 204, blockchain traceability, recall management'),
    ('greenhouse-automation-advanced', 'Greenhouse automation advanced - climate control, hydroponics, lighting, fertigation, yield prediction'),
    ('agri-insurance-platform', 'Agricultural insurance platform - parametric, MPCI, claims, crop monitoring, index products'),
    ('rural-banking-fintech', 'Rural and agricultural banking fintech - farm credit, crop loans, digital payments, financial inclusion'),
    # Sports and recreation technology
    ('sports-performance-platform', 'Sports performance analytics platform - athlete tracking, load monitoring, GPS, force plates, video'),
    ('team-management-sports', 'Team management sports platform - scheduling, travel, roster, contracts, scouting, video analysis'),
    ('ticketing-venue-platform', 'Ticketing and venue platform - dynamic pricing, mobile tickets, access control, fan experience'),
    ('sports-media-rights', 'Sports media rights and streaming platform - rights management, OTT, digital distribution, monetization'),
    ('athlete-management-system', 'Athlete management system - performance data, health records, contracts, social media, sponsorship'),
    ('fantasy-sports-platform', 'Fantasy sports platform - real-time scoring, draft tools, trade analysis, contest management'),
    ('golf-technology-platform', 'Golf technology platform - tee time booking, course management, handicap, turf management, coaching'),
    ('fitness-gym-management', 'Fitness and gym management platform - member management, class booking, access control, PT, billing'),
    ('sports-officiating-tech', 'Sports officiating technology - VAR systems, electronic officiating, scorekeeping, rule enforcement'),
    ('outdoor-recreation-tech', 'Outdoor recreation technology - trail management, permit systems, park operations, visitor analytics'),
    # Education administration technology
    ('higher-ed-student-info', 'Higher education student information system - enrollment, registration, financial aid, degree audit'),
    ('learning-management-advanced', 'Learning management system advanced - xAPI compliance, content authoring, assessments, analytics'),
    ('ed-finance-platform', 'Education finance platform - tuition management, financial aid administration, budgeting, reporting'),
    ('student-success-platform', 'Student success platform - early alert, advising, retention analytics, degree planning, coaching'),
    ('campus-management-platform', 'Campus management platform - space management, facilities, events, housing, dining, ID systems'),
    ('research-admin-platform', 'Research administration platform - grants management, IRB, technology transfer, compliance, reporting'),
    ('alumni-fundraising-platform', 'Alumni and fundraising platform - advancement CRM, donor management, campaigns, stewardship'),
    ('ed-analytics-advanced', 'Education analytics advanced - institutional research, IPEDS, predictive analytics, benchmark reporting'),
    ('online-program-management', 'Online program management platform - enrollment marketing, academic operations, student services'),
    ('k12-district-platform', 'K-12 district management platform - SIS, curriculum alignment, assessment, staff management, compliance'),
    # Nonprofit and social impact technology
    ('nonprofit-crm-advanced', 'Nonprofit CRM advanced - donor management, major gifts, planned giving, stewardship, moves management'),
    ('fundraising-platform-advanced', 'Fundraising technology platform advanced - peer-to-peer, crowdfunding, events, recurring giving'),
    ('program-management-nonprofit', 'Nonprofit program management - case management, outcomes tracking, reporting, grant compliance'),
    ('volunteer-management-advanced', 'Volunteer management advanced - scheduling, onboarding, tracking, recognition, communications'),
    ('impact-measurement-platform', 'Impact measurement and reporting platform - theory of change, SROI, ESG, stakeholder reporting'),
    ('community-engagement-platform', 'Community engagement technology platform - civic participation, consultation, feedback, co-design'),
    ('social-enterprise-platform', 'Social enterprise technology platform - hybrid mission/revenue models, B-corp analytics, reporting'),
    ('humanitarian-tech-platform', 'Humanitarian technology platform - aid distribution, beneficiary management, cash transfers, reporting'),
    ('advocacy-platform-advanced', 'Advocacy and policy platform advanced - grassroots organizing, campaign management, coalition tools'),
    ('giving-circle-platform', 'Giving circle and DAF platform - donor advised funds, collective giving, grant recommendations'),
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
