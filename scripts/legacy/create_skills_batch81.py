
import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # Taxidermy and wildlife arts technology
    ('taxidermy-studio-platform', 'Taxidermy and wildlife mounting studio platform - order management, specimen tracking, client portal, billing'),
    ('wildlife-art-platform', 'Wildlife art and nature illustration platform - commission management, gallery, licensing, print sales'),
    ('nature-photography-platform', 'Nature and wildlife photography platform - expedition booking, print sales, licensing, stock library'),
    ('birding-guide-platform', 'Birding and ornithology guide service platform - tour booking, species lists, equipment rental, reports'),
    ('taxidermy-school-platform', 'Taxidermy school and education platform - course scheduling, technique videos, supply sales, certification'),
    ('wildlife-rehabilitation-platform', 'Wildlife rehabilitation center platform - animal intake, treatment records, volunteer management, donations'),
    ('insect-entomology-platform', 'Insect collection and entomology platform - specimen management, identification tools, sales, community'),
    ('fossil-paleontology-platform', 'Fossil and paleontology collector platform - specimen catalog, authentication, sales, exhibit management'),
    ('nature-journaling-platform', 'Nature journaling and citizen science platform - observation logging, species reporting, community, courses'),
    ('outdoor-education-platform', 'Outdoor education and nature school platform - program scheduling, curriculum, safety management, billing'),
    # Specialty vehicle and transportation services technology
    ('limousine-service-platform', 'Limousine and luxury car service platform - booking management, chauffeur scheduling, dispatch, billing'),
    ('party-bus-platform', 'Party bus and entertainment vehicle platform - booking, route planning, event coordination, billing'),
    ('food-truck-fleet-platform', 'Food truck fleet management platform - location tracking, scheduling, permit management, sales analytics'),
    ('mobile-services-platform', 'Mobile services vehicle management platform - route optimization, appointment booking, territory management'),
    ('towing-recovery-platform', 'Towing and roadside recovery platform - dispatch, job management, billing, fleet maintenance'),
    ('courier-bike-platform', 'Courier bike and cargo cycling service platform - delivery management, route optimization, tracking, billing'),
    ('pedicab-rickshaw-platform', 'Pedicab and cycle rickshaw transportation platform - booking, pricing zones, driver management, billing'),
    ('motor-coach-school-platform', 'Motor coach and school transportation platform - route management, student tracking, driver compliance'),
    ('helicopter-charter-platform', 'Helicopter charter and air taxi platform - booking, pilot scheduling, maintenance tracking, billing'),
    ('water-taxi-platform', 'Water taxi and ferry service platform - booking, vessel management, route scheduling, ticketing'),
    # Specialty education and learning technology
    ('coding-bootcamp-advanced', 'Advanced coding bootcamp management platform - cohort management, project tracking, career services, outcomes'),
    ('language-immersion-school', 'Language immersion school management platform - program scheduling, host family management, visa, billing'),
    ('gifted-education-platform', 'Gifted and talented education program platform - assessment, differentiated curriculum, enrichment, tracking'),
    ('special-education-platform', 'Special education and IEP management platform - goal tracking, service scheduling, progress reports, billing'),
    ('alternative-school-platform', 'Alternative and progressive school management platform - project-based learning, portfolios, narrative reports'),
    ('micro-school-platform', 'Micro school and learning pod management platform - enrollment, curriculum, compliance, billing, community'),
    ('unschooling-platform', 'Unschooling and self-directed learning platform - interest tracking, resource library, community, portfolios'),
    ('trade-school-platform', 'Trade school and vocational training platform - program management, apprenticeship tracking, licensing, outcomes'),
    ('online-school-platform', 'Online K-12 school management platform - LMS integration, attendance, grading, parent communication'),
    ('tutoring-franchise-platform', 'Tutoring franchise management platform - center operations, curriculum, franchisee reporting, billing'),
    # Specialty home and property services technology
    ('foundation-repair-platform', 'Foundation repair and waterproofing platform - inspection scheduling, engineering reports, warranty, billing'),
    ('radon-mitigation-platform', 'Radon testing and mitigation services platform - inspection scheduling, mitigation design, compliance, billing'),
    ('asbestos-abatement-platform', 'Asbestos testing and abatement services platform - air monitoring, remediation workflow, compliance, billing'),
    ('lead-paint-remediation-platform', 'Lead paint testing and remediation platform - inspection reports, containment protocols, compliance, billing'),
    ('home-automation-installation', 'Home automation and smart home installation platform - project management, device programming, service, billing'),
    ('swimming-pool-construction', 'Swimming pool and spa construction platform - design tools, permit management, construction scheduling, billing'),
    ('solar-installation-platform-adv', 'Solar panel installation and service platform - design, permitting, installation scheduling, monitoring'),
    ('generator-service-platform', 'Generator sales, installation and service platform - product catalog, service agreements, maintenance, billing'),
    ('well-drilling-platform', 'Well drilling and water systems platform - permit management, geological records, testing, compliance'),
    ('septic-services-platform', 'Septic system installation and maintenance platform - inspection records, pumping scheduling, compliance, billing'),
    # Specialty retail technology
    ('gun-range-retail-platform', 'Gun range and retail combined platform - range reservations, firearm sales, FFL compliance, membership'),
    ('military-surplus-platform', 'Military surplus and tactical gear retail platform - inventory management, authenticity verification, online sales'),
    ('uniform-supply-platform', 'Uniform and workwear supply platform - corporate accounts, custom embroidery, bulk ordering, catalog'),
    ('trophy-award-platform', 'Trophy, award and recognition retail platform - custom engraving, order management, corporate accounts, delivery'),
    ('office-supply-reseller-platform', 'Office supply reseller and contract platform - catalog management, corporate accounts, delivery, billing'),
    ('school-supply-platform', 'School supply and educational materials platform - teacher wish lists, classroom kits, bulk ordering, billing'),
    ('safety-equipment-platform', 'Safety equipment and PPE distribution platform - compliance tracking, training materials, bulk orders, billing'),
    ('janitorial-supply-platform', 'Janitorial supply and commercial cleaning products platform - distribution, chemical tracking, compliance, billing'),
    ('restaurant-supply-platform', 'Restaurant supply and food service equipment platform - catalog, equipment leasing, repair services, billing'),
    ('lab-supply-platform', 'Laboratory supply and scientific equipment platform - catalog, certification tracking, chemical management, billing'),
    # Specialty health and wellness services technology
    ('chiropractic-wellness-platform', 'Chiropractic and wellness center platform - patient management, adjustment records, care plans, billing'),
    ('physical-therapy-platform', 'Physical therapy and rehabilitation platform - exercise programs, progress tracking, insurance, billing'),
    ('occupational-therapy-platform-adv', 'Occupational therapy practice management platform - ADL assessment, adaptive equipment, goals, billing'),
    ('speech-therapy-platform', 'Speech therapy practice management platform - articulation tracking, session notes, parent portal, billing'),
    ('vision-therapy-platform', 'Vision therapy and optometric training platform - exercise scheduling, progress tracking, patient portal'),
    ('nutrition-counseling-platform', 'Nutrition counseling and dietitian platform - meal planning, food journals, lab results, telehealth, billing'),
    ('health-coaching-platform-adv', 'Health coaching practice management platform - client intake, goal tracking, content library, billing'),
    ('naturopathic-platform', 'Naturopathic medicine practice platform - intake forms, supplement protocols, lab integration, billing'),
    ('homeopathy-platform', 'Homeopathy practice management platform - repertory tools, remedy tracking, case management, billing'),
    ('ayurveda-platform', 'Ayurvedic medicine practice management platform - dosha assessment, treatment protocols, herb management, billing'),
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
