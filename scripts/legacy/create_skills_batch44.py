
import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # Media and entertainment technology
    ('broadcast-automation', 'Broadcast automation - playout, MAM, routing, graphics, master control, SDI/IP workflows'),
    ('streaming-platform-tech', 'Streaming platform technology - CDN, DRM, adaptive bitrate, player SDK, analytics, ABR'),
    ('ott-platform', 'OTT platform - content management, subscription, recommendations, ad insertion, analytics'),
    ('gaming-platform', 'Gaming platform - player identity, matchmaking, leaderboards, telemetry, anti-cheat, LiveOps'),
    ('content-moderation-platform', 'Content moderation platform - classifier models, human review, appeals, policy enforcement'),
    ('digital-asset-management', 'Digital asset management - DAM systems, metadata, search, rights management, distribution'),
    ('podcast-technology', 'Podcast technology - hosting, RSS, transcription, analytics, monetization, distribution'),
    ('music-streaming-tech', 'Music streaming technology - catalog, licensing, recommendations, playlist, royalty tracking'),
    ('esports-platform-tech', 'Esports platform technology - tournament brackets, stat tracking, streaming overlay, API'),
    ('vr-ar-platform', 'VR/AR platform - content pipeline, rendering, spatial audio, social, monetization, distribution'),
    # Telecommunications deep
    ('telecom-bss', 'Telecom BSS - billing, CRM, order management, mediation, revenue assurance, analytics'),
    ('telecom-oss', 'Telecom OSS - network inventory, fault management, configuration, performance, provisioning'),
    ('voip-systems', 'VoIP systems - SIP, WebRTC, media servers, codec, QoS, call routing, compliance recording'),
    ('network-slicing', 'Network slicing - 5G core, slice management, isolation, SLA, orchestration, NSMF'),
    ('sd-wan-advanced', 'SD-WAN advanced - overlay, underlay, policies, application steering, analytics, SASE'),
    ('telecom-fraud-management', 'Telecom fraud management - IRSF, SIM swap, wangiri, PBX hacking, detection, prevention'),
    ('number-portability', 'Number portability - LNP, MNP, porting workflows, NPAC, database queries, compliance'),
    ('roaming-management', 'Roaming management - bilateral agreements, TAP, RAP, fraud, steering, analytics'),
    # Defense and government technology
    ('c2-tactical-systems', 'C2 tactical systems - command and control, situational awareness, mapping, comms integration'),
    ('military-logistics-systems', 'Military logistics systems - supply chain, maintenance, asset tracking, RFID, ERP'),
    ('intelligence-analysis-platform', 'Intelligence analysis platform - data fusion, link analysis, visualization, OSINT, HUMINT'),
    ('cybersecurity-defense-platform', 'Cybersecurity defense platform - SOC, threat intel, SOAR, endpoint, network, cloud'),
    ('identity-management-gov', 'Government identity management - CAC/PIV, FICAM, identity federation, privileged access'),
    ('geospatial-intelligence', 'Geospatial intelligence - satellite imagery analysis, change detection, object recognition'),
    ('signals-intelligence', 'Signals intelligence - RF collection, spectrum analysis, direction finding, protocol analysis'),
    # Financial services deep
    ('trading-platform', 'Trading platform - order management, execution, risk, position management, connectivity, FIX'),
    ('market-data-platform', 'Market data platform - feed handling, normalization, distribution, replay, reference data'),
    ('risk-management-platform', 'Risk management platform - VaR, stress testing, limits, breaches, aggregation, reporting'),
    ('compliance-surveillance', 'Compliance surveillance - trade surveillance, communications, market abuse, MAR, reporting'),
    ('custody-settlement', 'Custody and settlement - DvP, reconciliation, corporate actions, income, reporting, SWIFT'),
    ('prime-brokerage-tech', 'Prime brokerage technology - margin, stock loan, synthetic, reporting, client portal'),
    ('wealth-management-platform', 'Wealth management platform - portfolio management, rebalancing, reporting, client portal'),
    ('fund-administration', 'Fund administration - NAV calculation, investor reporting, transfer agency, reconciliation'),
    ('trade-finance-platform', 'Trade finance platform - LC, guarantees, supply chain finance, digitization, blockchain'),
    ('KYC-AML-platform', 'KYC/AML platform - onboarding, screening, monitoring, case management, SAR, regulatory'),
    # Agritech deep
    ('farm-iot-platform', 'Farm IoT platform - sensor networks, data aggregation, dashboards, alerts, ML analytics'),
    ('crop-disease-ai', 'Crop disease AI - image classification, severity scoring, treatment recommendations, alerts'),
    ('irrigation-automation', 'Irrigation automation - soil sensors, weather data, scheduling, precision delivery, logging'),
    ('greenhouse-control', 'Greenhouse control - climate control, lighting, nutrients, monitoring, automation, integration'),
    ('livestock-monitoring', 'Livestock monitoring - health alerts, estrus, feeding behavior, location tracking, analytics'),
    ('agri-marketplace', 'Agricultural marketplace - commodity trading, price discovery, logistics, financing, compliance'),
    ('carbon-farming', 'Carbon farming - soil carbon measurement, MRV, credit issuance, registry, payments'),
    # Water technology
    ('water-treatment-scada', 'Water treatment SCADA - process control, sensors, alarms, compliance, reporting, cybersecurity'),
    ('water-quality-monitoring', 'Water quality monitoring - IoT sensors, analytics, regulatory reporting, alerts, LIMS'),
    ('smart-water-networks', 'Smart water networks - AMI, leak detection, pressure management, digital twin, hydraulic'),
    ('water-billing-systems', 'Water billing systems - meter reading, billing, customer service, collections, analytics'),
    # Education technology platforms
    ('lms-development-advanced', 'LMS development advanced - xAPI, SCORM, adaptive learning, analytics, accessibility'),
    ('student-information-system', 'Student information system - enrollment, grades, attendance, scheduling, reporting, FERPA'),
    ('assessment-platform', 'Assessment platform - item banking, adaptive testing, proctoring, psychometrics, reporting'),
    ('virtual-classroom', 'Virtual classroom - video conferencing, whiteboard, breakout rooms, recording, LMS integration'),
    ('competency-management', 'Competency management - skill frameworks, assessments, development plans, gap analysis'),
    ('alumni-engagement', 'Alumni engagement - database, communications, events, fundraising, career services, portal'),
    # Procurement and sourcing technology
    ('e-procurement-platform', 'E-procurement platform - requisitions, approvals, purchase orders, receiving, invoice matching'),
    ('supplier-management', 'Supplier management - onboarding, qualification, performance, risk, development, portal'),
    ('contract-compliance', 'Contract compliance - obligation tracking, milestone monitoring, renewal alerts, analytics'),
    ('spend-analytics', 'Spend analytics - categorization, supplier consolidation, savings opportunities, benchmarking'),
    ('sourcing-platform', 'Sourcing platform - RFX, auction, negotiation, award, supplier collaboration, analytics'),
    ('invoice-automation', 'Invoice automation - OCR, matching, exceptions, approval, payment, analytics, compliance'),
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
