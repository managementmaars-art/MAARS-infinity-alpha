
import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # Aviation and aerospace technology
    ('aviation-ops-platform', 'Aviation operations platform - flight operations, OCC, crew scheduling, dispatch, MEL management, ACARS'),
    ('aircraft-maintenance-platform', 'Aircraft maintenance platform - MRO systems, airworthiness, work orders, part 145, CAMO, Trax'),
    ('flight-data-analytics', 'Flight data analytics - FDM/FOQA, exceedance detection, risk profiling, safety metrics, ASAP'),
    ('air-traffic-management', 'Air traffic management technology - SWIM, FIXM, AIXM, trajectory management, TBO, UTM'),
    ('aerospace-manufacturing-tech', 'Aerospace manufacturing technology - AS9100, MBOM, S1000D, configuration management, PLM'),
    ('satellite-operations-platform', 'Satellite operations platform - telemetry processing, command sequencing, orbit determination, LEOP'),
    ('space-mission-systems', 'Space mission systems - mission planning, ground segment, data downlink, space situational awareness'),
    ('drone-traffic-management', 'Drone traffic management - UTM/U-space, BVLOS operations, corridor management, detect and avoid'),
    ('airline-revenue-management', 'Airline revenue management - fare class optimization, O&D forecasting, overbooking, codeshare'),
    ('avionics-software-development', 'Avionics software development - DO-178C, ARINC 429/664, IMA, FMS integration, DO-254'),
    # Mining and natural resources technology
    ('mine-operations-platform', 'Mine operations platform - fleet management, dispatch systems, drill-blast optimization, SCADA'),
    ('geological-data-platform', 'Geological data platform - core logging, drillhole databases, resource estimation, Leapfrog, QGIS'),
    ('mine-planning-software', 'Mine planning software - open pit optimization, underground scheduling, Whittle, Deswik, Vulcan'),
    ('mining-asset-management', 'Mining asset management - CMMS for heavy equipment, predictive maintenance, reliability, RCM'),
    ('minerals-processing-platform', 'Minerals processing platform - process control, metallurgical accounting, grade control, recovery'),
    ('environmental-monitoring-mining', 'Environmental monitoring mining - tailings management, water quality, dust monitoring, rehabilitation'),
    ('oil-gas-upstream-platform', 'Oil and gas upstream platform - reservoir management, well planning, production optimization, Petrel'),
    ('pipeline-management-platform', 'Pipeline management platform - SCADA, leak detection, pigging, cathodic protection, ILI data'),
    ('refinery-operations-tech', 'Refinery operations technology - advanced process control, optimization, planning, LP models, LIMS'),
    ('natural-resources-trading', 'Natural resources trading platform - commodity trading, hedging, logistics, quality management, ETRM'),
    # Automotive technology platform
    ('connected-vehicle-platform', 'Connected vehicle platform - OTA updates, telemetry, remote diagnostics, SOTA/FOTA, V2X'),
    ('automotive-data-platform', 'Automotive data platform - CAN bus, AUTOSAR, vehicle signals, fleet analytics, Covesa VSS'),
    ('ev-battery-management', 'EV battery management platform - BMS integration, state estimation, degradation modeling, charging'),
    ('autonomous-driving-platform', 'Autonomous driving platform - perception pipeline, sensor fusion, HD maps, scenario testing, SOTIF'),
    ('automotive-cybersecurity', 'Automotive cybersecurity - ISO 21434, UNECE WP.29, HSM, IDS, OTA security, TARA'),
    ('dealer-management-system', 'Dealer management system - inventory management, F&I, service scheduling, CRM, DMS integration'),
    ('automotive-manufacturing-mes', 'Automotive manufacturing MES - ANDON, quality gates, sequence scheduling, traceability, IATF'),
    ('vehicle-lifecycle-platform', 'Vehicle lifecycle platform - configuration, homologation, type approval, aftermarket, end-of-life'),
    ('mobility-as-a-service-platform', 'Mobility as a service platform - journey planning, multimodal booking, payment, account management'),
    ('fleet-electrification-platform', 'Fleet electrification platform - TCO analysis, charging infrastructure, range planning, V2G'),
    # Media and entertainment technology
    ('ott-platform-advanced', 'OTT platform advanced - video delivery, CDN integration, DRM, adaptive bitrate, player SDK, DAI'),
    ('media-asset-management', 'Media asset management - DAM, MAM, content ingest, proxy generation, metadata, search, archive'),
    ('broadcast-technology-platform', 'Broadcast technology platform - playout automation, MCR, SDI/IP hybrid, SMPTE 2110, contribution'),
    ('content-delivery-platform', 'Content delivery platform - CDN architecture, edge caching, origin shielding, purge, real-time'),
    ('video-processing-platform', 'Video processing platform - transcoding pipeline, codec optimization, quality metrics, VMAF, packaging'),
    ('music-tech-platform', 'Music technology platform - rights management, royalty calculation, DSP distribution, metadata, ISRCs'),
    ('gaming-backend-platform', 'Gaming backend platform - matchmaking, leaderboards, inventory, economy, anti-cheat, LiveOps'),
    ('esports-platform', 'Esports platform - tournament management, brackets, prize pools, spectator tools, stats, broadcasting'),
    ('podcast-platform-advanced', 'Podcast platform advanced - hosting, RSS, analytics, dynamic ad insertion, monetization, discovery'),
    ('live-streaming-platform', 'Live streaming platform - ingest, transcoding, WebRTC, low-latency HLS, chat, monetization'),
    # Insurance technology deep
    ('actuarial-platform', 'Actuarial technology platform - mortality tables, GLM pricing, CAT modeling, reserving, Solvency II'),
    ('insurance-underwriting-platform', 'Insurance underwriting platform - risk scoring, appetite management, referral workflows, capacity'),
    ('claims-automation-platform', 'Claims automation platform - straight-through processing, fraud detection, settlement optimization'),
    ('telematics-insurance-platform', 'Telematics insurance platform - UBI, PAYD, driving behavior scoring, crash detection, claims'),
    ('insurtech-distribution', 'Insurtech distribution platform - embedded insurance, API-first quoting, bind, policy issuance'),
    ('reinsurance-platform', 'Reinsurance platform - treaty management, facultative, cession, experience analysis, retrocession'),
    ('insurance-data-analytics', 'Insurance data analytics - predictive modeling, churn, CLV, NPS, combined ratio, loss development'),
    ('parametric-insurance-platform', 'Parametric insurance platform - trigger management, index data, automated payouts, basis risk'),
    ('insurance-compliance-platform', 'Insurance compliance platform - regulatory filing, rate approval, form filing, state compliance'),
    ('life-insurance-platform', 'Life insurance technology platform - illustration, new business, policy admin, in-force management'),
    # Professional services technology
    ('legal-tech-platform-advanced', 'Legal technology platform advanced - matter management, e-billing, legal ops, contract lifecycle'),
    ('law-firm-practice-management', 'Law firm practice management - time tracking, billing, trust accounting, document management, CRM'),
    ('contract-intelligence-platform', 'Contract intelligence platform - AI extraction, clause library, obligation tracking, renewal alerts'),
    ('e-discovery-platform', 'E-discovery platform - legal hold, data preservation, processing, review, TAR, production, EDRM'),
    ('accounting-firm-platform', 'Accounting firm technology platform - audit management, tax workflow, engagement management, CPE'),
    ('consulting-firm-platform', 'Consulting firm technology platform - project staffing, knowledge management, methodology, IP'),
    ('professional-billing-platform', 'Professional services billing platform - T&M, fixed fee, milestone, expense management, WIP'),
    ('talent-marketplace-professional', 'Professional talent marketplace - skills matching, project staffing, contractor management, bench'),
    ('knowledge-management-professional', 'Knowledge management professional services - expertise location, document intelligence, communities'),
    ('client-portal-professional', 'Client portal professional services - secure collaboration, document sharing, status, communication'),
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
