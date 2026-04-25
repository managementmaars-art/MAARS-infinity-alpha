
import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # Specialty retail and niche commerce technology
    ('gun-shop-platform', 'Firearms dealer and gun shop management platform - FFL compliance, ATF Form 4473, background checks, inventory'),
    ('hunting-fishing-platform', 'Hunting and fishing license and outfitter platform - tag management, guide booking, equipment rental'),
    ('archery-pro-shop-platform', 'Archery pro shop management platform - bow fitting, range scheduling, lesson booking, repair tracking'),
    ('sporting-goods-retail', 'Sporting goods retail management platform - team sales, equipment fitting, custom uniforms, school accounts'),
    ('tackle-bait-platform', 'Tackle and bait shop management platform - seasonal inventory, fishing report integration, tournament weigh-in'),
    ('outdoor-gear-platform', 'Outdoor gear and adventure equipment retail platform - rental, guided trips, gear fitting, used gear'),
    ('skateboard-surf-platform', 'Action sports and skateboard shop platform - custom boards, team management, contest registration'),
    ('music-instrument-tech', 'Musical instrument retail technology platform - lesson scheduling, repair tracking, band program sales'),
    ('coin-stamp-platform', 'Coin and stamp dealer technology platform - grading, authentication, show inventory, consignment, pricing'),
    ('hobby-craft-platform', 'Hobby and craft store management platform - class scheduling, club management, custom orders, kits'),
    # Transportation and logistics niche technology
    ('hazmat-transport-platform', 'Hazardous materials transportation technology platform - manifest management, DOT compliance, driver training'),
    ('oversize-load-platform', 'Oversize and overweight load transportation platform - permit management, escort coordination, route survey'),
    ('flatbed-specialized-platform', 'Flatbed and specialized freight technology platform - load securement, coil/machinery, pilot cars, permits'),
    ('bulk-liquid-transport', 'Bulk liquid transportation technology platform - tank cleaning records, food grade certification, routing'),
    ('livestock-transport-platform', 'Livestock transportation technology platform - health certificates, USDA compliance, route planning, welfare'),
    ('auto-transport-platform', 'Auto transport and vehicle hauling platform - load booking, damage inspection, carrier management, tracking'),
    ('moving-van-line-platform', 'Moving van line and relocation technology platform - binding estimates, weight tickets, claim management'),
    ('courier-platform-advanced', 'Advanced courier and messenger service platform - on-demand dispatch, proof of delivery, chain of custody'),
    ('charter-bus-platform', 'Charter bus and motorcoach management platform - trip planning, driver assignment, DOT compliance, billing'),
    ('airport-shuttle-platform', 'Airport shuttle and ground transportation platform - flight tracking, reservation, dispatch, driver management'),
    # Religious and faith community technology
    ('church-giving-platform', 'Church giving and stewardship technology platform - online giving, pledge management, donor analytics, campaigns'),
    ('synagogue-platform', 'Synagogue management technology platform - membership, High Holiday tickets, lifecycle events, donations'),
    ('mosque-platform', 'Mosque management technology platform - membership, prayer times, Jumu\'ah management, Zakat, events'),
    ('hindu-temple-platform', 'Hindu temple management technology platform - puja scheduling, archana booking, festival management, donations'),
    ('religious-retreat-platform', 'Religious retreat center technology platform - retreat booking, spiritual director scheduling, meals, lodging'),
    ('faith-formation-platform', 'Faith formation and religious education technology - curriculum, sacramental prep, attendance, family portal'),
    ('chaplaincy-services-platform', 'Chaplaincy services management platform - visit tracking, referrals, crisis response, interfaith coordination'),
    ('religious-conference-platform', 'Religious conference and convocation platform - registration, housing, speaker management, session tracking'),
    ('seminary-platform', 'Seminary and theological school management platform - enrollment, formation records, field placement, ordination'),
    ('religious-publishing-platform', 'Religious publishing and media technology platform - content management, distribution, licensing, royalties'),
    # Pharmacy and drug store technology
    ('independent-pharmacy-platform', 'Independent pharmacy management platform - prescription workflow, compounding, MTM, 340B compliance'),
    ('specialty-pharmacy-platform', 'Specialty pharmacy technology platform - prior authorization, cold chain, patient adherence, hub services'),
    ('long-term-care-pharmacy', 'Long-term care pharmacy technology platform - blister pack, facility billing, chart orders, medication sync'),
    ('mail-order-pharmacy-platform', 'Mail order pharmacy technology platform - auto-refill, batch dispensing, 90-day supply, delivery tracking'),
    ('pharmacy-benefits-platform', 'Pharmacy benefits management technology platform - formulary management, prior auth, rebates, analytics'),
    ('compounding-pharmacy-platform', 'Compounding pharmacy management platform - formula management, beyond-use dating, USP compliance'),
    ('veterinary-pharmacy-tech', 'Veterinary pharmacy technology platform - species-specific dosing, controlled substance, VCPR compliance'),
    ('nuclear-pharmacy-platform', 'Nuclear pharmacy technology platform - dose calibration, patient scheduling, radiation safety, waste disposal'),
    ('infusion-pharmacy-platform', 'Home infusion pharmacy technology platform - referral management, clinical documentation, billing, delivery'),
    ('cannabis-dispensary-platform', 'Cannabis dispensary management platform - seed-to-sale tracking, state compliance, POS, inventory'),
    # Cleaning and facility services specialties
    ('pool-maintenance-platform', 'Swimming pool maintenance and service platform - route scheduling, chemical tracking, equipment repair, billing'),
    ('chimney-sweep-platform', 'Chimney sweep and fireplace services platform - inspection reports, cleaning records, repair quotes, scheduling'),
    ('hoarding-cleanup-platform', 'Hoarding cleanup and extreme cleaning platform - assessment, remediation workflow, coordination, billing'),
    ('estate-cleanout-platform', 'Estate cleanout and junk removal platform - scheduling, load tracking, donation management, disposal'),
    ('power-washing-equipment', 'Pressure washing equipment rental and services platform - equipment tracking, route optimization, billing'),
    ('awning-cleaning-platform', 'Awning and exterior cleaning services platform - route management, chemical tracking, before/after photos'),
    ('gutter-cleaning-platform', 'Gutter cleaning and maintenance services platform - route scheduling, inspection photos, upsell management'),
    ('dryer-vent-cleaning-platform', 'Dryer vent cleaning services platform - residential/commercial scheduling, inspection photos, billing'),
    ('industrial-cleaning-platform', 'Industrial cleaning services technology platform - confined space, specialty coatings, compliance, scheduling'),
    ('crime-scene-cleaning-platform', 'Crime scene and trauma cleanup technology platform - insurance billing, PPE tracking, certification, compliance'),
    # Public safety and emergency services technology
    ('fire-station-management', 'Fire station management technology platform - shift scheduling, apparatus management, training, NFIRS reporting'),
    ('ems-platform', 'Emergency medical services technology platform - dispatch, ePCR, billing, QA, fleet management, crew scheduling'),
    ('911-dispatch-platform', '911 dispatch and CAD technology platform - call processing, unit dispatch, mapping, incident tracking'),
    ('emergency-notification-platform', 'Emergency notification and mass alert system - multi-channel alerts, population targeting, incident management'),
    ('hazmat-response-platform', 'Hazmat response technology platform - chemical database, response guides, decontamination, post-incident'),
    ('search-rescue-platform', 'Search and rescue management technology platform - team deployment, GPS tracking, resource management, ICS'),
    ('law-enforcement-records', 'Law enforcement records management system - incident reports, arrest records, evidence, warrants, analytics'),
    ('body-camera-platform', 'Body worn camera and evidence management platform - video storage, redaction, chain of custody, court export'),
    ('fire-inspection-platform', 'Fire inspection and code enforcement technology platform - inspection scheduling, violations, permits, compliance'),
    ('drone-first-responder', 'Drone as first responder technology platform - automated launch, live video, incident response integration'),
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
