
import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # Cemetery and funeral services technology
    ('funeral-home-management', 'Funeral home management platform - case management, arrangement, obituaries, financial planning, aftercare'),
    ('cemetery-management-platform', 'Cemetery management platform - plot inventory, interment records, mapping, maintenance, sales'),
    ('end-of-life-planning-tech', 'End-of-life planning technology - advance directives, digital estate, legacy planning, grief support'),
    ('cremation-services-platform', 'Cremation services platform - authorization workflows, tracking, documentation, urn selection, delivery'),
    ('bereavement-support-platform', 'Bereavement and grief support platform - counseling, peer support, community resources, aftercare'),
    # Childcare and early education technology
    ('childcare-management-platform', 'Childcare management platform - enrollment, attendance, billing, parent communication, ratios'),
    ('early-childhood-platform', 'Early childhood education platform - developmental milestones, curriculum, portfolio, family engagement'),
    ('daycare-software-platform', 'Daycare software platform - check-in/out, meal tracking, incident reports, immunization, licensing'),
    ('nanny-agency-platform', 'Nanny and au pair agency platform - matching, background checks, contracts, payroll, family portal'),
    ('after-school-program-platform', 'After-school program management platform - enrollment, attendance, activities, billing, reports'),
    # Home and property services technology
    ('home-services-management', 'Home services management platform - booking, dispatch, job management, invoicing, customer portal'),
    ('property-maintenance-platform', 'Property maintenance technology platform - work orders, vendor management, preventive maintenance'),
    ('landscaping-tech-platform', 'Landscaping and lawn care platform - route planning, client management, chemical tracking, irrigation'),
    ('cleaning-services-platform', 'Cleaning services technology platform - scheduling, quality control, supply tracking, client management'),
    ('home-inspection-platform', 'Home inspection technology platform - mobile inspection, report generation, photo annotation, delivery'),
    ('smart-home-management', 'Smart home management platform - device integration, automation rules, energy monitoring, security'),
    ('moving-relocation-platform', 'Moving and relocation services platform - quote management, inventory, tracking, claims, coordination'),
    ('storage-facility-platform', 'Self-storage facility management platform - unit inventory, gate access, billing, tenant portal'),
    ('pest-control-platform', 'Pest control technology platform - treatment records, scheduling, chemical tracking, compliance, reports'),
    ('pool-spa-management', 'Pool and spa service management - route optimization, chemical logging, equipment tracking, billing'),
    # Automotive aftermarket technology
    ('auto-repair-shop-platform', 'Auto repair shop management platform - work orders, labor tracking, parts inventory, DVI, CRM'),
    ('tire-wheel-platform', 'Tire and wheel retail platform - fitment guide, inventory, mounting scheduling, fleet accounts'),
    ('auto-parts-platform', 'Auto parts retail and distribution platform - fitment data, inventory, B2B portal, core returns'),
    ('vehicle-inspection-platform', 'Vehicle inspection technology platform - safety inspection, emissions, digital reports, compliance'),
    ('automotive-auction-platform', 'Automotive auction technology platform - vehicle listings, bidding, condition reports, title, transport'),
    ('roadside-assistance-platform', 'Roadside assistance technology platform - dispatch, GPS, service tracking, partner network, billing'),
    ('auto-detailing-platform', 'Auto detailing services platform - booking, service packages, detailer mobile app, CRM, reviews'),
    ('car-rental-platform', 'Car rental technology platform - fleet management, reservations, rate management, damage, telematics'),
    ('driving-school-platform', 'Driving school management platform - lesson scheduling, instructor management, student tracking, licensing'),
    ('rv-marina-management', 'RV park and marina management platform - reservations, site management, amenities, billing, maps'),
    # Beauty and personal care technology
    ('salon-management-platform', 'Salon and spa management platform - appointment booking, POS, staff management, loyalty, inventory'),
    ('beauty-booking-platform', 'Beauty services booking platform - marketplace, stylist profiles, instant booking, reviews, payments'),
    ('cosmetics-formulation-platform', 'Cosmetics formulation and compliance platform - ingredient database, safety assessment, labeling'),
    ('beauty-ecommerce-platform', 'Beauty ecommerce and subscription platform - product curation, shade matching, subscription boxes'),
    ('tattoo-studio-platform', 'Tattoo and piercing studio platform - consultation booking, design management, aftercare, consent forms'),
    ('barbershop-platform', 'Barbershop management platform - walk-in queue, appointment booking, loyalty, POS, staff management'),
    ('nail-salon-platform', 'Nail salon management platform - appointment booking, technician scheduling, services menu, POS, reviews'),
    ('beauty-supply-platform', 'Beauty supply distribution platform - professional ordering, brand management, education, loyalty'),
    ('aesthetic-clinic-platform', 'Aesthetic clinic technology platform - consultation, treatment planning, before/after, consent, follow-up'),
    ('wellness-spa-platform', 'Wellness and spa technology platform - experience booking, membership, treatment rooms, retail, packages'),
    # Trades and skilled labor technology
    ('contractor-management-platform', 'Contractor management platform - project management, subcontractor, scheduling, billing, compliance'),
    ('electrical-contractor-platform', 'Electrical contractor technology platform - estimating, permits, project management, service dispatch'),
    ('plumbing-contractor-platform', 'Plumbing contractor technology platform - dispatch, flat rate pricing, service history, inventory'),
    ('hvac-contractor-platform', 'HVAC contractor technology platform - service dispatch, preventive maintenance, equipment tracking, billing'),
    ('roofing-contractor-platform', 'Roofing contractor technology platform - aerial measurement, estimating, project management, warranty'),
    ('solar-installation-platform', 'Solar installation technology platform - site assessment, design tools, permitting, installation, monitoring'),
    ('construction-trades-platform', 'Construction trades management platform - bid management, scheduling, labor tracking, materials, safety'),
    ('field-service-advanced', 'Field service management advanced - multi-trade dispatch, IoT integration, predictive maintenance, analytics'),
    ('inspection-services-platform', 'Inspection services technology platform - scheduling, mobile forms, findings, reporting, compliance'),
    ('facilities-maintenance-platform', 'Facilities maintenance technology platform - work orders, asset management, compliance, vendor management'),
    # Travel and adventure tourism technology
    ('adventure-travel-platform', 'Adventure travel technology platform - tour booking, guide management, waivers, safety protocols'),
    ('eco-tourism-platform', 'Eco-tourism technology platform - sustainability tracking, guided experiences, conservation impact, booking'),
    ('cruise-booking-platform', 'Cruise booking technology platform - cabin selection, excursions, onboard activities, loyalty, transfers'),
    ('luxury-travel-platform', 'Luxury travel technology platform - concierge services, private aviation, villa rentals, experiences'),
    ('travel-insurance-platform', 'Travel insurance technology platform - quoting, policy management, claims, assistance services'),
    ('vacation-rental-platform', 'Vacation rental technology platform - property management, channel manager, dynamic pricing, guest portal'),
    ('tour-operator-platform', 'Tour operator technology platform - itinerary builder, supplier management, booking, operations'),
    ('destination-management-platform', 'Destination management company platform - ground operations, transfers, activities, event management'),
    ('travel-visa-platform', 'Travel visa and documentation technology platform - requirements, application tracking, document management'),
    ('backpacker-hostel-platform', 'Backpacker and hostel management platform - bed inventory, check-in, community features, tours, billing'),
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
