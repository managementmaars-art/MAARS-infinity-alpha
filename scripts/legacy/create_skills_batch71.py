
import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # Antiques, collectibles, and resale technology
    ('antique-collectibles-platform', 'Antiques and collectibles marketplace platform - authentication, provenance, condition grading, auctions'),
    ('thrift-consignment-platform', 'Thrift store and consignment shop platform - inventory intake, pricing, donor management, POS, e-commerce'),
    ('liquidation-surplus-platform', 'Liquidation and surplus goods platform - lot management, bidding, buyer tiers, manifest, shipping'),
    ('pawn-shop-platform', 'Pawn shop management platform - collateral tracking, loans, buyouts, compliance, appraisal, inventory'),
    ('rare-book-platform', 'Rare book and manuscript platform - bibliographic records, condition reports, valuation, dealer network'),
    ('coin-numismatic-platform', 'Numismatic and coin dealer platform - grading, population reports, auction, certification, inventory'),
    ('vinyl-records-platform', 'Vinyl records marketplace and shop platform - catalog, grading, pressing info, sales, wishlist matching'),
    ('art-auction-platform', 'Art auction technology platform - lot management, bidding engine, buyer premium, consignor portal'),
    ('estate-sale-platform', 'Estate sale management platform - estate intake, catalog, online bidding, cashiering, distribution'),
    ('sports-memorabilia-platform', 'Sports memorabilia platform - authentication, grading, registry, auction, collector management'),
    # Personal and laundry services technology
    ('dry-cleaning-platform', 'Dry cleaning and laundry service platform - order tracking, garment tagging, route management, billing'),
    ('alterations-tailoring-platform', 'Alterations and tailoring platform - measurement records, job tracking, customer communication, billing'),
    ('shoe-repair-platform', 'Shoe repair shop management platform - job intake, repair tracking, customer notification, history'),
    ('laundromat-platform', 'Laundromat and coin laundry platform - machine monitoring, remote payment, loyalty, maintenance alerts'),
    ('personal-styling-platform', 'Personal styling and wardrobe management platform - client profiles, outfit records, purchase tracking'),
    ('clothing-rental-platform', 'Clothing rental and fashion subscription platform - inventory, sizing, logistics, cleaning, membership'),
    ('personal-shopping-platform', 'Personal shopping service technology platform - client preferences, sourcing, order management, billing'),
    ('monogram-embroidery-platform', 'Monogram and embroidery service platform - design management, order workflow, production, delivery'),
    ('uniform-workwear-platform', 'Uniform and workwear management platform - sizing, corporate accounts, decoration, inventory, reorder'),
    ('custom-apparel-platform', 'Custom apparel production platform - design tools, order management, decoration workflow, fulfillment'),
    # Agricultural custom services technology
    ('custom-harvest-platform', 'Custom harvesting services technology platform - job scheduling, equipment tracking, billing, crop records'),
    ('ag-custom-application-platform', 'Agricultural custom application services - pesticide/fertilizer application records, equipment, billing'),
    ('grain-storage-platform', 'Grain storage and elevator management platform - inventory, moisture tracking, shrink calculation, settlements'),
    ('seed-genetics-platform', 'Seed genetics and trait management platform - variety selection, trial data, licensing, distribution'),
    ('soil-testing-platform', 'Soil testing and analysis platform - sample management, lab results, recommendation reports, history'),
    ('agronomy-consulting-platform', 'Agronomy consulting technology platform - field records, recommendations, visit reports, billing'),
    ('irrigation-management-platform', 'Irrigation management technology platform - scheduling, water usage, system monitoring, billing'),
    ('crop-scouting-platform', 'Crop scouting technology platform - field observations, pest/disease identification, reporting, maps'),
    ('farm-equipment-rental', 'Farm equipment rental and leasing platform - fleet tracking, reservations, maintenance, billing'),
    ('agricultural-drone-platform', 'Agricultural drone services platform - mission planning, imagery processing, analytics, compliance'),
    # Senior living and long-term care technology
    ('assisted-living-platform', 'Assisted living facility technology platform - resident management, care plans, ADL tracking, billing'),
    ('memory-care-platform', 'Memory care technology platform - behavioral monitoring, safety alerts, family communication, activity'),
    ('skilled-nursing-platform', 'Skilled nursing facility technology platform - MDS, care planning, clinical documentation, billing'),
    ('continuing-care-platform', 'Continuing care retirement community platform - resident services, transitions, dining, wellness, billing'),
    ('independent-living-platform', 'Independent living community platform - resident engagement, services, maintenance, payments, events'),
    ('senior-transportation-platform', 'Senior transportation services platform - scheduling, driver management, NEMT billing, family portal'),
    ('long-term-care-insurance-tech', 'Long-term care insurance technology platform - policy administration, claims, care coordination, benefits'),
    ('senior-nutrition-platform', 'Senior nutrition and meal delivery platform - dietary restrictions, delivery routing, intake tracking'),
    ('life-enrichment-platform', 'Life enrichment and activity technology platform - resident interests, program management, attendance'),
    ('aging-in-place-platform', 'Aging in place technology platform - home modification, caregiver matching, remote monitoring, safety'),
    # Cleaning and restoration services technology
    ('water-damage-restoration-platform', 'Water damage restoration platform - emergency response, moisture mapping, drying logs, documentation'),
    ('fire-restoration-platform', 'Fire and smoke damage restoration platform - assessment, remediation workflow, insurance docs, billing'),
    ('mold-remediation-platform', 'Mold remediation technology platform - assessment, containment protocols, air quality testing, documentation'),
    ('biohazard-cleanup-platform', 'Biohazard cleanup and crime scene restoration platform - job management, compliance, documentation'),
    ('commercial-cleaning-platform', 'Commercial cleaning services platform - contract management, scheduling, quality control, billing'),
    ('janitorial-services-platform', 'Janitorial services management platform - work orders, supply tracking, inspection, time tracking'),
    ('carpet-cleaning-platform', 'Carpet and upholstery cleaning platform - route optimization, job management, chemical tracking, billing'),
    ('window-cleaning-platform', 'Window cleaning services platform - high-rise management, scheduling, safety compliance, billing'),
    ('pressure-washing-platform', 'Pressure washing services platform - quote management, route scheduling, equipment tracking, billing'),
    ('air-duct-cleaning-platform', 'Air duct cleaning services platform - system inspection, before/after documentation, scheduling, billing'),
    # Arborist and tree services technology
    ('tree-service-platform', 'Tree service and arborist technology platform - job estimation, crew scheduling, equipment, billing'),
    ('urban-forestry-platform', 'Urban forestry management platform - tree inventory GIS, canopy analysis, maintenance scheduling'),
    ('landscape-architecture-platform', 'Landscape architecture technology platform - design tools, project management, plant database, billing'),
    ('lawn-care-platform', 'Lawn care services platform - route optimization, application records, irrigation, client communication'),
    ('irrigation-installation-platform', 'Irrigation installation and repair platform - design tools, installation records, maintenance, billing'),
    ('hardscape-platform', 'Hardscape and outdoor construction platform - design, estimating, material tracking, project management'),
    ('christmas-light-platform', 'Holiday light installation services platform - scheduling, design templates, inventory, installation, billing'),
    ('snow-ice-management-platform', 'Snow and ice management platform - site mapping, treatment records, fleet tracking, salt management'),
    ('turf-management-platform', 'Turf management technology platform - sports field maintenance, soil data, treatment records, calendar'),
    ('golf-course-management-platform', 'Golf course turf management platform - agronomic records, irrigation, chemical programs, equipment'),
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
