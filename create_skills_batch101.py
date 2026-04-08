import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # Biotech and life sciences research operations
    ('lims-configuration', 'configure and manage laboratory information management systems for sample tracking and data integrity'),
    ('lab-inventory-management', 'manage reagents supplies and consumables across research labs with automated reorder and expiry tracking'),
    ('cro-vendor-management', 'manage contract research organization relationships timelines deliverables and quality oversight'),
    ('clinical-trial-operations', 'coordinate clinical trial logistics including site management patient enrollment and regulatory submissions'),
    ('biobank-sample-tracking', 'track biological samples from collection through storage analysis and disposal with chain of custody'),
    ('regulatory-compliance-gxp', 'ensure GxP compliance across lab operations including SOPs audit trails and deviation management'),
    ('assay-development-workflow', 'design and validate assay workflows from development through qualification and routine use'),
    ('electronic-lab-notebook', 'implement and manage electronic lab notebook systems for experiment capture and data management'),
    ('lab-equipment-calibration', 'schedule track and document equipment calibration maintenance and qualification activities'),
    ('research-project-portfolio', 'manage research project portfolios including resource allocation milestone tracking and reporting'),
]
skills += [
    # Commercial aviation and airline operations
    ('crew-scheduling-optimization', 'optimize crew scheduling to meet regulatory rest requirements while minimizing cost and maximizing coverage'),
    ('aircraft-maintenance-tracking', 'track aircraft maintenance schedules airworthiness directives and component life limits across the fleet'),
    ('ground-operations-management', 'coordinate ground handling turnaround activities including fueling catering baggage and boarding'),
    ('revenue-management-airline', 'implement airline revenue management including fare class controls overbooking and ancillary pricing'),
    ('flight-operations-dispatch', 'manage flight dispatch including fuel planning weather analysis route optimization and regulatory compliance'),
    ('airport-slot-coordination', 'manage airport slot requests allocations and coordination with slot coordinators and authorities'),
    ('irregular-operations-recovery', 'manage irregular operations including cancellations delays rebooking and passenger reaccommodation'),
    ('cargo-operations-management', 'manage air cargo operations including acceptance build-up loading and delivery coordination'),
    ('safety-management-aviation', 'implement aviation safety management systems including hazard identification risk assessment and reporting'),
    ('passenger-experience-ops', 'optimize passenger experience touchpoints from booking through arrival including loyalty and service recovery'),
]
skills += [
    # Rail and mass transit operations
    ('rail-fleet-management', 'manage rail rolling stock fleet including maintenance scheduling availability tracking and lifecycle planning'),
    ('timetable-planning-rail', 'develop and optimize rail timetables balancing capacity demand infrastructure constraints and connections'),
    ('fare-collection-systems', 'implement and manage automated fare collection systems including smart cards validators and revenue reconciliation'),
    ('rail-safety-management', 'manage rail safety systems including signaling compliance incident reporting and safety case maintenance'),
    ('passenger-information-systems', 'manage real-time passenger information systems including departure boards apps and delay notifications'),
    ('train-crew-rostering', 'roster train drivers and conductors to comply with working time regulations and operational requirements'),
    ('infrastructure-maintenance-rail', 'plan and coordinate rail infrastructure maintenance including track signaling and overhead line work'),
    ('capacity-planning-transit', 'analyze and plan transit network capacity to match demand patterns and service level targets'),
    ('revenue-protection-rail', 'implement revenue protection programs including barrier management inspection and fare evasion reduction'),
    ('intermodal-connectivity', 'optimize connections between rail bus ferry and other modes to improve journey times and reliability'),
]
skills += [
    # E-commerce platform and marketplace operations
    ('seller-onboarding-marketplace', 'design and manage seller onboarding workflows including verification catalog setup and policy training'),
    ('product-catalog-management', 'manage product catalog operations including taxonomy enrichment quality scoring and attribute standardization'),
    ('order-fulfillment-ecommerce', 'orchestrate order fulfillment from placement through pick pack ship and delivery confirmation'),
    ('returns-management-ecommerce', 'manage returns and refunds including authorization inspection restocking and customer communication'),
    ('marketplace-trust-safety', 'implement trust and safety programs including fraud detection counterfeit removal and seller performance'),
    ('pricing-strategy-ecommerce', 'implement dynamic pricing strategies including competitive monitoring repricing rules and margin protection'),
    ('search-merchandising', 'optimize search and merchandising including ranking algorithms facets promotions and A/B testing'),
    ('seller-performance-management', 'monitor and manage seller performance metrics including defect rates fulfillment speed and customer satisfaction'),
    ('promotions-campaigns-ecommerce', 'plan and execute promotional campaigns including deal mechanics funding sourcing and performance tracking'),
    ('customer-experience-ecommerce', 'optimize end-to-end customer experience including reviews Q&A post-purchase and loyalty programs'),
]
skills += [
    # Third-party logistics and fulfillment center operations
    ('warehouse-management-system', 'configure and operate warehouse management systems for inventory slotting receiving putaway and picking'),
    ('pick-pack-operations', 'optimize pick and pack operations including wave planning zone routing batch picking and packing standards'),
    ('carrier-integration-3pl', 'integrate with carrier APIs for rate shopping label generation tracking and exception management'),
    ('inbound-receiving-operations', 'manage inbound receiving including appointment scheduling unloading inspection putaway and discrepancy resolution'),
    ('inventory-accuracy-management', 'maintain inventory accuracy through cycle counting reconciliation investigation and root cause correction'),
    ('returns-processing-3pl', 'process returned goods including receipt inspection grading restocking or disposition and client reporting'),
    ('labor-management-warehouse', 'plan and manage warehouse labor including staffing scheduling productivity measurement and incentive programs'),
    ('fulfillment-client-management', 'manage 3PL client relationships including SLA reporting billing integration and issue escalation'),
    ('dangerous-goods-handling', 'manage dangerous goods storage handling documentation and carrier compliance for hazardous materials'),
    ('fulfillment-network-optimization', 'optimize fulfillment network including node selection inventory positioning and routing to minimize cost and transit time'),
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
