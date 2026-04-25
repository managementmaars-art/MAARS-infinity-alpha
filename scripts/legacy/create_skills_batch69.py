
import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # Specialty retail and niche commerce
    ('wine-spirits-platform', 'Wine and spirits retail technology platform - inventory, sommelier tools, compliance, subscription clubs'),
    ('book-publishing-platform', 'Book publishing technology platform - manuscript management, editorial workflow, distribution, royalties'),
    ('music-instrument-retail', 'Musical instruments retail platform - rental management, lessons booking, repair tracking, trade-ins'),
    ('sporting-goods-platform', 'Sporting goods retail technology platform - equipment rental, team sales, custom uniforms, warranties'),
    ('pharmacy-retail-platform', 'Pharmacy retail technology platform - prescription management, insurance billing, immunizations, MTM'),
    ('optical-retail-platform', 'Optical retail technology platform - vision benefits, lens ordering, frame fitting, patient records'),
    ('jewelry-luxury-platform', 'Jewelry and luxury retail platform - custom design, appraisal, resizing, insurance, authentication'),
    ('craft-hobby-platform', 'Craft and hobby retail technology platform - project kits, classes, online community, loyalty rewards'),
    ('toy-game-retail', 'Toy and game retail technology platform - age recommendations, registry, layaway, educational tools'),
    ('garden-nursery-platform', 'Garden center and nursery platform - plant database, care guides, landscaping services, wholesale'),
    # Security and access control technology
    ('physical-security-platform', 'Physical security technology platform - access control, surveillance, visitor management, incident response'),
    ('video-surveillance-platform', 'Video surveillance technology platform - camera management, video analytics, cloud storage, alerts'),
    ('intrusion-detection-physical', 'Physical intrusion detection technology - sensors, alarms, monitoring, response protocols, reporting'),
    ('guard-management-platform', 'Security guard management platform - scheduling, patrol tracking, incident reports, client portal'),
    ('visitor-management-advanced', 'Visitor management technology advanced - pre-registration, badge printing, host notifications, compliance'),
    ('access-control-platform', 'Access control technology platform - credential management, door control, anti-passback, audit logs'),
    ('perimeter-security-tech', 'Perimeter security technology platform - fence sensors, LiDAR, thermal imaging, drone detection'),
    ('security-operations-center', 'Security operations center technology - alarm monitoring, dispatch, incident management, reporting'),
    ('parking-enforcement-platform', 'Parking enforcement technology platform - mobile LPR, digital citations, permit management, appeals'),
    ('loss-prevention-advanced', 'Loss prevention technology advanced - EAS, RFID, analytics, employee investigation, exception reporting'),
    # Wellness and alternative health technology
    ('acupuncture-practice-platform', 'Acupuncture practice management platform - EHR, SOAP notes, insurance billing, herb dispensary'),
    ('chiropractic-platform', 'Chiropractic practice technology platform - EHR, X-ray integration, care plans, billing, scheduling'),
    ('naturopathic-medicine-platform', 'Naturopathic medicine platform - functional health records, supplement dispensary, lab integration'),
    ('massage-therapy-platform', 'Massage therapy practice platform - booking, SOAP notes, client intake, membership, insurance billing'),
    ('meditation-mindfulness-platform', 'Meditation and mindfulness technology platform - guided sessions, progress tracking, corporate wellness'),
    ('holistic-wellness-platform', 'Holistic wellness technology platform - multi-modality, practitioner directory, health journey tracking'),
    ('health-coaching-advanced', 'Health coaching technology advanced - habit tracking, behavior change, biometric integration, groups'),
    ('integrative-medicine-platform', 'Integrative medicine technology platform - multi-provider coordination, evidence-based protocols, tracking'),
    ('teletherapy-platform', 'Teletherapy and online counseling platform - HIPAA video, scheduling, notes, billing, crisis resources'),
    ('occupational-therapy-platform', 'Occupational therapy platform - goal setting, activities of daily living, adaptive equipment, outcomes'),
    # Event and experience economy technology
    ('conference-management-platform', 'Conference and event management platform - registration, abstract submission, scheduling, exhibitors'),
    ('virtual-events-platform', 'Virtual and hybrid events technology platform - streaming, networking, gamification, analytics, sponsors'),
    ('escape-room-platform', 'Escape room business management platform - booking, capacity management, GM tools, analytics, waivers'),
    ('amusement-park-platform', 'Amusement park technology platform - ticketing, ride operations, guest experience, maintenance, analytics'),
    ('cinema-management-platform', 'Cinema management technology platform - scheduling, ticketing, concessions, loyalty, ODS'),
    ('bowling-entertainment-platform', 'Bowling and entertainment complex platform - lane reservations, POS, leagues, food service, events'),
    ('go-kart-platform', 'Go-kart and racing entertainment platform - timing systems, kart tracking, booking, leagues, safety'),
    ('trampoline-park-platform', 'Trampoline park management platform - online booking, waiver management, party packages, safety'),
    ('laser-tag-platform', 'Laser tag and entertainment venue platform - game management, scoring, loyalty, booking, analytics'),
    ('immersive-experience-platform', 'Immersive experience technology platform - interactive installations, AR/VR, ticketing, operations'),
    # Specialized professional services
    ('architecture-practice-platform', 'Architecture practice management platform - project management, BIM integration, billing, client portal'),
    ('engineering-firm-platform', 'Engineering firm technology platform - project tracking, drawing management, calculations, billing'),
    ('environmental-consulting-platform', 'Environmental consulting platform - field data collection, report generation, regulatory, client portal'),
    ('surveying-mapping-platform', 'Surveying and mapping technology platform - field data, CAD integration, report generation, GPS'),
    ('veterinary-specialist-platform', 'Veterinary specialist practice platform - referral management, advanced imaging, specialty records, billing'),
    ('dental-specialist-platform', 'Dental specialist practice platform - referral workflow, specialty EHR, imaging, treatment planning'),
    ('mental-health-group-practice', 'Mental health group practice technology - multi-provider scheduling, billing, EHR, supervision tools'),
    ('home-health-agency-platform', 'Home health agency technology platform - care scheduling, clinical documentation, billing, compliance'),
    ('hospice-palliative-care', 'Hospice and palliative care technology platform - interdisciplinary care, family portal, symptom management'),
    ('dialysis-center-platform', 'Dialysis center management technology - treatment scheduling, water quality, outcomes, billing, compliance'),
    # Transportation and logistics niche
    ('taxi-rideshare-platform', 'Taxi and rideshare technology platform - dispatch, driver app, fare calculation, fleet management'),
    ('school-bus-platform', 'School bus management technology platform - routing, GPS tracking, student ridership, communication'),
    ('medical-transport-platform', 'Medical transportation technology platform - NEMT, scheduling, eligibility verification, billing'),
    ('courier-platform', 'Courier and messenger service platform - on-demand dispatch, proof of delivery, billing, analytics'),
    ('moving-company-platform', 'Moving company technology platform - job estimation, inventory, crew scheduling, trucks, billing'),
    ('waste-collection-platform', 'Waste collection and recycling platform - route optimization, customer service, compliance, billing'),
    ('snow-removal-platform', 'Snow removal and winter services platform - route management, property database, tracking, billing'),
    ('airport-ground-transport', 'Airport ground transportation platform - transfer booking, driver dispatch, flight tracking, billing'),
    ('boat-rental-charter', 'Boat rental and charter management platform - reservations, captain scheduling, safety, billing, maintenance'),
    ('bicycle-sharing-platform', 'Bicycle and e-bike sharing platform - station management, bike tracking, membership, payment, analytics'),
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
