
import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # Medical specialty technology
    ('ophthalmology-platform', 'Ophthalmology practice platform - EHR, imaging integration, surgical scheduling, optical dispensary, billing'),
    ('dermatology-platform', 'Dermatology practice technology platform - lesion tracking, teledermatology, phototherapy, cosmetic procedures'),
    ('orthopedic-platform', 'Orthopedic practice technology platform - implant tracking, surgical planning, PT integration, outcomes'),
    ('cardiology-platform', 'Cardiology practice platform - ECG integration, cath lab, device monitoring, remote patient monitoring'),
    ('oncology-platform', 'Oncology practice technology platform - treatment protocols, infusion management, clinical trials, supportive care'),
    ('gastroenterology-platform', 'Gastroenterology practice platform - endoscopy scheduling, pathology integration, screening reminders'),
    ('neurology-platform', 'Neurology practice technology platform - neuroimaging, EEG/EMG, epilepsy monitoring, cognitive assessment'),
    ('fertility-clinic-platform', 'Fertility clinic technology platform - IVF cycle management, embryo tracking, donor matching, outcomes'),
    ('pain-management-platform', 'Pain management clinic platform - controlled substance tracking, treatment plans, outcome measures, urine drug screening'),
    ('blood-bank-platform', 'Blood bank and tissue management platform - inventory, crossmatch, transfusion records, traceability, alerts'),
    # Financial advisory and wealth management technology
    ('wealth-management-platform', 'Wealth management technology platform - portfolio management, financial planning, CRM, compliance, reporting'),
    ('financial-advisor-platform', 'Financial advisor technology platform - client portal, proposal tools, fee billing, compliance, onboarding'),
    ('robo-advisor-platform', 'Robo-advisor technology platform - algorithm-driven portfolios, rebalancing, tax-loss harvesting, client app'),
    ('estate-planning-tech', 'Estate planning technology platform - document drafting, trust administration, executor tools, beneficiary management'),
    ('family-office-platform', 'Family office technology platform - consolidated reporting, alternative investments, entity management, tax'),
    ('investment-banking-platform', 'Investment banking technology platform - deal management, pitch books, capital markets, M&A analytics'),
    ('hedge-fund-tech', 'Hedge fund technology platform - order management, risk analytics, investor reporting, compliance, back office'),
    ('private-equity-platform', 'Private equity technology platform - deal flow, portfolio monitoring, LP reporting, fund administration'),
    ('insurance-advisor-platform', 'Insurance advisor technology platform - quoting, needs analysis, policy management, renewal tracking, CRM'),
    ('mortgage-broker-platform', 'Mortgage broker technology platform - loan origination, rate comparison, pipeline management, compliance, closing'),
    # Real estate and property professional technology
    ('real-estate-agent-platform', 'Real estate agent technology platform - CRM, MLS integration, showing scheduling, transaction management'),
    ('real-estate-broker-platform', 'Real estate broker/brokerage platform - agent management, transaction coordination, commission tracking'),
    ('property-management-advanced', 'Property management advanced platform - multi-unit, maintenance, tenant portal, accounting, lease management'),
    ('commercial-real-estate-platform', 'Commercial real estate technology - deal pipeline, lease administration, property analytics, tenant management'),
    ('real-estate-appraisal-platform', 'Real estate appraisal technology platform - comp selection, report generation, UAD, USPAP compliance'),
    ('title-escrow-platform', 'Title and escrow technology platform - title search, commitment, closing workflow, funds management, recording'),
    ('hoa-management-platform', 'HOA and condo association management platform - dues, violations, maintenance, meetings, resident portal'),
    ('real-estate-investment-platform', 'Real estate investment technology - deal analysis, syndication, crowdfunding, investor portal, distributions'),
    ('property-tax-platform', 'Property tax management technology - assessment appeals, exemptions, valuation, compliance, multi-jurisdiction'),
    ('land-registry-platform', 'Land registry and records management platform - parcel data, deed recording, GIS, chain of title, public access'),
    # Translation, interpretation, and language services
    ('translation-services-platform', 'Translation services technology platform - project management, CAT tools, TM, glossary, quality, billing'),
    ('interpretation-platform', 'Interpretation services platform - over-the-phone, video remote, in-person scheduling, language matching'),
    ('localization-platform', 'Software and content localization platform - string management, workflow, pseudo-localization, QA, delivery'),
    ('language-learning-platform', 'Language learning technology platform - adaptive curriculum, speech recognition, immersive content, gamification'),
    ('subtitling-captioning-platform', 'Subtitling and captioning technology platform - automated transcription, time-coding, QC, distribution'),
    ('legal-translation-platform', 'Legal and certified translation platform - certified documents, notarization, ATA compliance, court filing'),
    ('medical-interpretation-platform', 'Medical interpretation technology platform - HIPAA-compliant, real-time, on-demand, language matching'),
    ('multilingual-content-platform', 'Multilingual content management platform - CMS integration, translation memory, workflow, publishing'),
    ('language-access-platform', 'Language access compliance platform - LEP services, Title VI, healthcare, legal, government compliance'),
    ('nlp-translation-platform', 'NLP and machine translation platform - neural MT, post-editing, quality estimation, domain adaptation'),
    # Photography and videography professional services
    ('photography-studio-platform', 'Photography studio management platform - booking, contracts, client gallery, proofing, print ordering'),
    ('event-photography-platform', 'Event photography management platform - event scheduling, on-site printing, image delivery, licensing'),
    ('photo-lab-platform', 'Professional photo lab management platform - order management, print production, color calibration, fulfillment'),
    ('video-production-management', 'Video production management platform - pre-production, crew management, shot lists, post, delivery'),
    ('wedding-photography-platform', 'Wedding photography platform - inquiry management, contracts, albums, client portal, vendor network'),
    ('real-estate-photography-platform', 'Real estate photography platform - booking, delivery, virtual tours, drone integration, MLS delivery'),
    ('stock-photography-platform', 'Stock photography platform - contributor management, licensing, search, rights management, royalties'),
    ('drone-services-platform', 'Drone services technology platform - flight planning, FAA compliance, delivery, data processing, analytics'),
    ('360-vr-content-platform', 'VR and 360 content platform - capture workflow, stitching, interactive hotspots, distribution, analytics'),
    ('product-photography-platform', 'Product photography platform - e-commerce shoots, batch processing, background removal, CDN delivery'),
    # Printing, signage, and promotional products technology
    ('print-shop-platform', 'Print shop management platform - order management, prepress workflow, production scheduling, finishing, billing'),
    ('wide-format-print-platform', 'Wide format printing technology platform - signage orders, substrate management, installation, tracking'),
    ('promotional-products-platform', 'Promotional products technology platform - product sourcing, customization, order management, decoration'),
    ('packaging-design-platform', 'Packaging design and production platform - dieline management, brand compliance, supplier integration'),
    ('digital-print-platform', 'Digital printing technology platform - web-to-print, variable data, personalization, finishing, fulfillment'),
    ('label-print-platform', 'Label printing technology platform - design templates, compliance, versioning, run management, regulatory'),
    ('screen-printing-platform', 'Screen printing and embroidery platform - art separation, screen management, order scheduling, fulfillment'),
    ('commercial-print-platform', 'Commercial printing platform - offset management, color management, bindery, MIS, client portal'),
    ('print-procurement-platform', 'Print procurement and management platform - vendor sourcing, RFQ, spec management, inventory, analytics'),
    ('3d-print-service-platform', '3D printing service platform - model validation, material selection, quote, production, quality, delivery'),
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
