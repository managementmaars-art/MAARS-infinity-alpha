
import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # Entertainment venue and amusement technology
    ('escape-room-platform', 'Escape room and immersive entertainment platform - room booking, game master tools, waiver, analytics'),
    ('trampoline-park-platform', 'Trampoline and indoor adventure park platform - capacity management, waivers, birthday parties, memberships'),
    ('go-kart-racing-platform', 'Indoor go-kart racing center platform - session booking, lap timing, leaderboards, leagues, birthday events'),
    ('billiards-poolhall-platform', 'Billiards and pool hall management platform - table reservations, league management, tournaments, bar POS'),
    ('paintball-airsoft-platform', 'Paintball and airsoft field management platform - field booking, equipment rental, waivers, tournaments'),
    ('shooting-range-platform', 'Shooting range management platform - lane reservations, membership, rental firearms, ammo sales, events'),
    ('roller-skating-rink-platform', 'Roller skating rink management platform - session scheduling, skate rental, party bookings, music, POS'),
    ('laser-tag-platform', 'Laser tag venue management platform - game session booking, group reservations, stats tracking, parties'),
    ('virtual-reality-arcade-platform', 'VR arcade and gaming lounge platform - headset booking, game library, session tracking, memberships'),
    ('mini-golf-platform', 'Mini golf course management platform - tee time booking, group reservations, birthday parties, POS'),
    # Tattoo body art and personal expression studios
    ('tattoo-studio-platform', 'Tattoo studio management platform - artist booking, consultation scheduling, aftercare, portfolio, deposits'),
    ('piercing-studio-platform', 'Body piercing studio management platform - appointment booking, jewelry inventory, aftercare, compliance'),
    ('tattoo-removal-platform', 'Tattoo removal clinic technology platform - laser treatment scheduling, progress photos, consent, billing'),
    ('hair-salon-advanced-platform', 'Advanced hair salon management platform - color formulas, stylebook, loyalty, commission, inventory'),
    ('barbershop-platform', 'Barbershop management platform - walk-in queue management, appointment booking, loyalty, product sales'),
    ('nail-salon-platform', 'Nail salon management platform - appointment scheduling, nail tech assignments, product tracking, loyalty'),
    ('med-spa-laser-platform', 'Medical spa laser and aesthetics platform - treatment protocols, device scheduling, consent, billing'),
    ('microblading-pmu-platform', 'Microblading and permanent makeup platform - consultation, patch testing, color theory, touch-up scheduling'),
    ('lash-extensions-platform', 'Lash extension studio platform - appointment management, client profiles, fill scheduling, product tracking'),
    ('spray-tan-platform', 'Spray tan and sunless tanning platform - appointment booking, formula tracking, mobile services, retail'),
    # Alternative wellness and holistic health technology
    ('float-tank-platform', 'Float tank and sensory deprivation center platform - pod reservations, cleaning cycles, memberships, retail'),
    ('cryotherapy-center-platform', 'Cryotherapy center management platform - session booking, waiver, temperature logs, package management'),
    ('iv-drip-therapy-platform', 'IV drip therapy bar platform - appointment booking, formula library, nurse scheduling, consent, billing'),
    ('hypnotherapy-platform', 'Hypnotherapy practice management platform - client intake, session notes, recording consent, billing'),
    ('acupuncture-clinic-platform', 'Acupuncture and TCM clinic platform - point protocols, herbal dispensary, treatment records, billing'),
    ('infrared-sauna-platform', 'Infrared sauna studio management platform - cabin reservations, cleaning protocols, memberships, retail'),
    ('salt-therapy-platform', 'Salt therapy and halotherapy center platform - session booking, halogenerator maintenance, memberships'),
    ('reiki-energy-healing-platform', 'Reiki and energy healing practice platform - session scheduling, client intake, distance sessions, billing'),
    ('sound-healing-platform', 'Sound healing and vibrational therapy platform - session booking, instrument management, group classes'),
    ('breathwork-platform', 'Breathwork and meditation studio platform - class scheduling, facilitator management, online streaming'),
    # Fishing and outdoor guiding services
    ('fishing-charter-platform', 'Fishing charter and guide service platform - trip booking, vessel management, licensing, weather alerts'),
    ('fly-fishing-guide-platform', 'Fly fishing guide service platform - trip booking, river conditions, equipment rental, license verification'),
    ('hunting-guide-platform', 'Hunting guide and outfitter platform - season management, tag tracking, camp logistics, client portal'),
    ('kayak-canoe-rental-platform', 'Kayak and canoe rental and touring platform - equipment rental, guided tours, safety waivers, billing'),
    ('scuba-diving-platform', 'Scuba diving operation management platform - dive trip booking, certification tracking, equipment, safety'),
    ('whale-watching-platform', 'Whale watching and eco-tour platform - trip scheduling, vessel management, naturalist booking, ticketing'),
    ('bird-watching-tour-platform', 'Bird watching and nature tour platform - tour scheduling, species lists, guide management, booking'),
    ('foraging-tour-platform', 'Foraging and wilderness education platform - tour booking, seasonal guides, safety, digital resources'),
    ('horseback-riding-platform', 'Horseback riding and equestrian experience platform - trail booking, lesson scheduling, horse management'),
    ('safari-expedition-platform', 'Safari and wildlife expedition management platform - multi-day booking, vehicle management, guide, permits'),
    # Specialty food and beverage production technology
    ('craft-distillery-platform', 'Craft distillery management platform - batch tracking, barrel aging, TTB compliance, distribution, tasting room'),
    ('meadery-platform', 'Meadery management platform - batch production, honey sourcing, fermentation tracking, taproom, distribution'),
    ('cidery-platform', 'Cidery and hard cider production platform - orchard management, pressing, fermentation, packaging, sales'),
    ('hot-sauce-production-platform', 'Hot sauce and condiment production platform - recipe management, batch tracking, co-packer, retail'),
    ('artisan-cheese-platform', 'Artisan cheese production management platform - milk sourcing, aging cave management, distribution, retail'),
    ('specialty-coffee-roaster', 'Specialty coffee roasting platform - green coffee sourcing, roast profiles, subscription management, wholesale'),
    ('tea-blending-platform', 'Tea blending and specialty tea platform - sourcing, blend recipes, quality testing, subscription, wholesale'),
    ('jerky-snack-production-platform', 'Jerky and specialty snack production platform - USDA compliance, batch tracking, retail, co-packing'),
    ('jam-preserve-platform', 'Jam, preserve and specialty food production platform - recipe management, FDA compliance, retail, wholesale'),
    ('food-truck-commissary-platform', 'Food truck commissary and shared kitchen platform - kitchen reservations, permit management, vendor billing'),
    # Specialty retail and collectibles technology
    ('comic-book-store-platform', 'Comic book and graphic novel retail platform - new issue pulls, subscription management, CGC tracking'),
    ('game-store-platform', 'Game store and tabletop gaming retail platform - inventory, organized play events, leagues, preorders'),
    ('record-store-platform', 'Record store and vinyl retail platform - inventory management, want lists, consignment, listening events'),
    ('used-bookstore-platform', 'Used bookstore management platform - acquisition pricing, inventory, buyback, rare book cataloging'),
    ('vintage-clothing-platform', 'Vintage clothing and resale boutique platform - sourcing, pricing, photography, multi-channel selling'),
    ('antique-mall-platform', 'Antique mall and dealer management platform - dealer booth billing, consignment, inventory, sales reporting'),
    ('collectible-card-platform', 'Collectible trading card store platform - PSA grading tracker, buylist management, singles pricing, events'),
    ('thrift-store-platform', 'Thrift store and resale management platform - donation intake, pricing, inventory, POS, donor receipts'),
    ('pawn-shop-platform', 'Pawn shop management platform - loan tracking, compliance reporting, e-Pawn integration, inventory, buyouts'),
    ('toy-collectible-platform', 'Toy and collectible specialty retail platform - graded toy tracking, consignment, preorders, authentication'),
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
