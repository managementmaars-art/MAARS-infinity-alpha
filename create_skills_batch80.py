
import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # Psychic, spiritual, and alternative belief services technology
    ('astrology-platform', 'Astrology and birth chart technology platform - natal chart generation, reading booking, horoscope subscription'),
    ('numerology-platform', 'Numerology and life path technology platform - calculation engine, report generation, consultation booking'),
    ('tarot-platform', 'Tarot and oracle card reading platform - virtual deck, reader marketplace, session management, subscriptions'),
    ('psychic-services-platform', 'Psychic and clairvoyant services platform - reader marketplace, session booking, review management'),
    ('spiritual-coaching-platform', 'Spiritual coaching and life purpose platform - coach profiles, session scheduling, content library'),
    ('meditation-app-platform', 'Meditation and mindfulness app platform - guided sessions, teacher marketplace, streaks, community'),
    ('metaphysical-shop-platform', 'Metaphysical and crystal shop platform - inventory management, crystal properties, online store, events'),
    ('shamanic-healing-platform', 'Shamanic healing and energy work platform - practitioner directory, session booking, ceremony management'),
    ('astrology-school-platform', 'Astrology education and certification platform - course delivery, chart exercises, student progress, exams'),
    ('divination-tools-platform', 'Divination tools and esoteric products platform - digital tools, reading history, product sales, community'),
    # Specialty construction and trade services technology
    ('masonry-contractor-platform', 'Masonry and brickwork contractor platform - project estimation, material management, scheduling, billing'),
    ('tile-flooring-platform', 'Tile and flooring contractor management platform - measurement tools, material ordering, installation scheduling'),
    ('drywall-insulation-platform', 'Drywall and insulation contractor platform - takeoff tools, job costing, scheduling, material tracking'),
    ('painting-contractor-platform', 'Painting contractor management platform - color consultation, surface area calculation, scheduling, billing'),
    ('concrete-contractor-platform', 'Concrete contractor management platform - pour scheduling, mix design, finishing, curing records'),
    ('steel-erection-platform', 'Steel erection and structural steel contractor platform - drawing management, lift planning, safety, billing'),
    ('waterproofing-platform', 'Waterproofing and moisture control contractor platform - inspection reports, warranty management, billing'),
    ('excavation-grading-platform', 'Excavation and grading contractor platform - earthwork calculations, equipment scheduling, compliance'),
    ('asphalt-paving-platform', 'Asphalt paving and seal coating contractor platform - project estimation, material tracking, crew scheduling'),
    ('demolition-contractor-platform', 'Demolition contractor management platform - hazmat surveys, debris tracking, permit management, billing'),
    # Specialty healthcare diagnostics and testing technology
    ('genetic-testing-platform', 'Genetic testing and genomics services platform - sample collection, result delivery, counseling, consent'),
    ('allergy-testing-platform', 'Allergy testing and immunotherapy platform - panel management, desensitization protocols, patient tracking'),
    ('diagnostic-imaging-platform', 'Diagnostic imaging center management platform - modality scheduling, DICOM, report delivery, billing'),
    ('lab-testing-direct-platform', 'Direct-to-consumer lab testing platform - test ordering, sample logistics, result delivery, physician review'),
    ('pathology-lab-platform', 'Pathology laboratory management platform - case management, specimen tracking, staining protocols, reporting'),
    ('toxicology-testing-platform', 'Toxicology testing laboratory platform - chain of custody, confirmation testing, MRO review, reporting'),
    ('cardiac-monitoring-platform', 'Cardiac monitoring and remote ECG platform - device management, arrhythmia detection, physician alerts'),
    ('continuous-glucose-platform', 'Continuous glucose monitoring technology platform - device integration, trend analytics, care team alerts'),
    ('point-of-care-testing-platform', 'Point-of-care testing management platform - device integration, result capture, quality control, reporting'),
    ('hearing-testing-platform', 'Hearing testing and audiometry platform - audiogram management, device fitting, follow-up scheduling'),
    # Music and audio production technology
    ('recording-studio-platform', 'Recording studio management platform - session booking, engineer scheduling, equipment tracking, billing'),
    ('music-producer-platform', 'Music producer and beat maker marketplace platform - beat licensing, collaboration, royalty splits, delivery'),
    ('podcast-network-platform', 'Podcast network management platform - show management, ad insertion, distribution, analytics, billing'),
    ('audio-book-production-platform', 'Audiobook production and distribution platform - narrator marketplace, studio booking, mastering, delivery'),
    ('voice-acting-platform', 'Voice acting and voice-over marketplace platform - auditions, project management, licensing, payments'),
    ('music-sync-licensing-platform', 'Music sync licensing technology platform - catalog management, placement tracking, royalties, clearance'),
    ('independent-label-platform', 'Independent record label management platform - artist roster, release management, distribution, royalties'),
    ('concert-promoter-platform', 'Concert promoter and live event technology platform - booking, ticketing, production, settlement, marketing'),
    ('music-publishing-platform', 'Music publishing administration platform - catalog registration, royalty collection, co-publisher splits'),
    ('beat-store-platform', 'Beat store and digital music marketplace platform - licensing options, lease management, exclusives, analytics'),
    # Fine arts and creative services technology
    ('art-gallery-platform', 'Art gallery management platform - artist representation, exhibition planning, sales tracking, provenance'),
    ('art-studio-rental-platform', 'Art studio rental and coworking platform - space booking, equipment sharing, residency management'),
    ('photography-gallery-platform', 'Photography gallery and print sales platform - image management, print fulfillment, licensing, royalties'),
    ('ceramic-studio-platform', 'Ceramic and pottery studio management platform - kiln scheduling, class booking, glaze inventory, sales'),
    ('textile-art-platform', 'Textile art and fiber craft platform - pattern sales, workshop booking, supply sourcing, community'),
    ('street-art-platform', 'Street art and mural commission platform - artist portfolio, commission requests, location mapping, permits'),
    ('printmaking-platform', 'Printmaking studio and print sales platform - edition management, press scheduling, inventory, sales'),
    ('sculpture-platform', 'Sculpture studio and commission management platform - material tracking, casting records, installation, sales'),
    ('calligraphy-platform', 'Calligraphy and hand lettering services platform - commission management, workshop booking, digital products'),
    ('illustration-platform', 'Illustration and graphic art marketplace platform - commission workflow, licensing, portfolio, client management'),
    # Specialty food services and catering technology
    ('private-chef-platform', 'Private chef and in-home dining platform - chef marketplace, menu customization, booking, dietary management'),
    ('meal-kit-platform', 'Meal kit and recipe box subscription platform - menu planning, ingredient procurement, box assembly, delivery'),
    ('ghost-restaurant-platform', 'Ghost kitchen and virtual restaurant platform - brand management, multi-concept ordering, delivery integration'),
    ('food-hall-platform', 'Food hall and market hall management platform - vendor management, shared ordering, revenue sharing, marketing'),
    ('specialty-diet-platform', 'Specialty diet and therapeutic nutrition platform - dietitian marketplace, meal planning, grocery integration'),
    ('pop-up-restaurant-platform', 'Pop-up restaurant and supper club platform - event booking, ticketing, menu management, payments'),
    ('ice-cream-shop-platform', 'Ice cream and frozen dessert shop platform - flavor rotation, custom orders, truck management, events'),
    ('bakery-management-platform', 'Bakery management and wholesale platform - production scheduling, custom orders, wholesale accounts, delivery'),
    ('chocolate-artisan-platform', 'Artisan chocolate and confectionery platform - recipe management, production batches, retail, gifting'),
    ('cooking-class-platform', 'Cooking class and culinary education platform - class scheduling, ingredient kits, chef profiles, certificates'),
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
