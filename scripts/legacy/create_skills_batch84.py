
import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # Subscription box and curated product services
    ('subscription-box-platform', 'Subscription box curated product service platform - product curation, box assembly, subscriber management, billing'),
    ('beauty-subscription-platform', 'Beauty and cosmetics subscription box platform - product sampling, brand partnerships, subscriber analytics'),
    ('food-subscription-platform', 'Specialty food subscription service platform - artisan product curation, producer relationships, delivery'),
    ('book-subscription-platform', 'Book subscription and reading club platform - curation algorithm, reading progress, community, shipping'),
    ('pet-subscription-platform', 'Pet product subscription box platform - breed-specific curation, treat testing, vet-approved products'),
    ('kids-subscription-platform', 'Children educational subscription box platform - age-based curation, curriculum alignment, parent portal'),
    ('craft-subscription-platform', 'Arts and crafts subscription box platform - project kits, instruction content, community sharing'),
    ('wine-subscription-platform', 'Wine subscription and club management platform - sommelier curation, tasting notes, cellar management'),
    ('wellness-subscription-platform', 'Wellness and self-care subscription box platform - holistic curation, practitioner partnerships, tracking'),
    ('gaming-subscription-platform', 'Gaming subscription and loot box management platform - game curation, digital rewards, community rewards'),
    # Niche professional services technology
    ('notary-mobile-platform', 'Mobile notary services management platform - appointment scheduling, document tracking, E&O compliance, billing'),
    ('process-serving-platform', 'Process serving and legal delivery management platform - job assignments, proof of service, GPS tracking'),
    ('private-investigator-tech', 'Private investigation case management platform - case workflow, evidence management, billing, reporting'),
    ('bail-recovery-platform', 'Bail recovery and fugitive apprehension platform - warrant management, skip tracing, compliance, billing'),
    ('repo-tech-platform', 'Vehicle repossession technology platform - account assignment, GPS, condition reports, compliance, billing'),
    ('skip-trace-platform', 'Skip tracing and asset search platform - database integration, search workflow, reporting, billing'),
    ('business-broker-platform', 'Business broker and M&A advisory platform - listing management, buyer matching, deal room, valuation'),
    ('franchise-broker-platform', 'Franchise broker and development consultant platform - franchise matching, client management, commissions'),
    ('commercial-appraiser-platform', 'Commercial real estate appraisal management platform - assignment tracking, comparables, report generation'),
    ('forensic-accounting-platform', 'Forensic accounting and litigation support platform - case management, document review, expert witness'),
    # Animal and pet industry verticals
    ('dog-training-platform', 'Dog training and behavior modification platform - client management, training plans, progress tracking, billing'),
    ('horse-training-platform', 'Horse training and equestrian coaching platform - horse profiles, training logs, competition management'),
    ('exotic-pet-platform', 'Exotic pet specialty veterinary and shop platform - species-specific care, permit tracking, breeder registry'),
    ('dog-breeding-platform', 'Dog breeding management and puppy placement platform - health testing records, whelping logs, buyer screening'),
    ('cat-cafe-platform', 'Cat café and feline adoption center platform - cat profiles, visitor management, adoption process, POS'),
    ('animal-shelter-rescue-platform', 'Animal shelter and rescue organization platform - intake management, foster network, adoption workflow'),
    ('pet-cemetery-platform', 'Pet cemetery and cremation services platform - arrangement management, plot records, memorial services'),
    ('aquarium-shop-platform', 'Aquarium and fish specialty retail platform - livestock inventory, water testing, quarantine tracking'),
    ('reptile-specialty-platform', 'Reptile specialty shop and breeder platform - species management, feeding records, permit compliance'),
    ('livestock-auction-advanced', 'Livestock auction and sale management platform - animal cataloging, bidding, health certificates, settlement'),
    # Sports analytics and performance technology
    ('athlete-recruitment-platform', 'Athlete recruitment and college scouting platform - prospect profiles, film sharing, coach communication'),
    ('sports-performance-analytics', 'Sports performance analytics and athlete monitoring platform - biometrics, training load, injury prevention'),
    ('video-analysis-sports-platform', 'Sports video analysis and coaching platform - play breakdown, telestration, team film room'),
    ('sport-specific-training-platform', 'Sport-specific training program management platform - periodization, exercise library, athlete tracking'),
    ('youth-sports-registration', 'Youth sports league and club registration platform - team formation, scheduling, payment, parent portal'),
    ('referee-management-platform', 'Referee and official management platform - certification tracking, assignment, availability, payment'),
    ('sports-nutrition-platform', 'Sports nutrition and athlete meal planning platform - macro tracking, supplement management, dietitian portal'),
    ('fantasy-sports-platform', 'Fantasy sports league management and analytics platform - draft tools, scoring, trade analysis, statistics'),
    ('sports-travel-platform', 'Sports travel and tournament trip management platform - team booking, hotel blocks, transportation, budgets'),
    ('athletic-scholarship-platform', 'Athletic scholarship management and NIL platform - eligibility tracking, compliance, deal management'),
    # Environmental and sustainability technology
    ('carbon-offset-marketplace', 'Carbon offset marketplace and project management platform - project verification, credit issuance, trading'),
    ('sustainability-reporting-platform', 'Corporate sustainability reporting and ESG platform - data collection, framework mapping, disclosure'),
    ('circular-economy-marketplace', 'Circular economy and secondhand goods marketplace platform - product authentication, condition grading, logistics'),
    ('green-building-platform', 'Green building certification and sustainability platform - LEED/BREEAM tracking, energy modeling, reporting'),
    ('renewable-energy-marketplace', 'Renewable energy procurement and PPA management platform - project sourcing, contract management, RECs'),
    ('waste-diversion-platform', 'Waste diversion and recycling program management platform - tonnage tracking, diversion rates, reporting'),
    ('environmental-impact-platform', 'Environmental impact assessment and mitigation platform - project screening, permit tracking, monitoring'),
    ('reforestation-platform', 'Reforestation and tree planting program management platform - site management, species tracking, carbon accounting'),
    ('ocean-plastic-platform', 'Ocean plastic recovery and recycling platform - collection management, material tracking, brand partnerships'),
    ('sustainable-agriculture-platform', 'Sustainable agriculture certification and market platform - organic certification, regenerative practices, sales'),
    # Emerging healthcare verticals
    ('longevity-clinic-platform', 'Longevity medicine and anti-aging clinic platform - biomarker tracking, protocol management, lifestyle coaching'),
    ('psychedelic-therapy-platform', 'Psychedelic-assisted therapy clinic platform - patient screening, dosing protocols, integration support'),
    ('ketamine-clinic-platform', 'Ketamine infusion therapy clinic management platform - treatment protocols, patient monitoring, billing'),
    ('functional-medicine-clinic', 'Functional medicine and integrative health clinic platform - root cause analysis, lab work, protocol tracking'),
    ('precision-nutrition-platform', 'Precision nutrition and metabolic health platform - CGM integration, microbiome testing, personalized plans'),
    ('regenerative-therapy-platform', 'Regenerative medicine and stem cell therapy platform - patient screening, protocol management, outcome tracking'),
    ('biohacking-platform', 'Biohacking and quantified self optimization platform - experiment tracking, biomarker monitoring, community'),
    ('concierge-health-platform', 'Concierge and direct primary care practice platform - membership management, same-day access, care coordination'),
    ('women-longevity-platform', 'Women\'s health optimization and longevity platform - hormonal health, menopause management, personalized care'),
    ('men-health-platform', 'Men\'s health optimization and testosterone therapy platform - lab management, protocol tracking, telemedicine'),
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
