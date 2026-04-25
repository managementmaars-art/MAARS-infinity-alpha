
import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # Social sciences and humanities computing
    ('computational-social-science-advanced', 'Computational social science - agent-based models, NLP for social data, network analysis, ABM'),
    ('digital-humanities-advanced', 'Digital humanities advanced - TEI encoding, distant reading, corpus linguistics, DH tools'),
    ('social-network-analysis-advanced', 'Social network analysis - centrality measures, community detection, temporal networks, gephi'),
    ('text-analytics-social', 'Social text analytics - sentiment, hate speech, stance detection, framing, social media NLP'),
    ('survey-methodology-tech', 'Survey methodology technology - online surveys, sampling, conjoint analysis, Qualtrics, SPSS'),
    ('qualitative-research-tech', 'Qualitative research technology - NVivo, Atlas.ti, MAXQDA, coding, thematic analysis tools'),
    ('political-analytics', 'Political analytics - election forecasting, voting models, redistricting, sentiment, campaign'),
    ('economics-data-science', 'Economics data science - econometrics, causal inference, natural experiments, panel data, IV'),
    ('archaeology-digital', 'Digital archaeology - GIS for archaeology, 3D documentation, photogrammetry, LiDAR, databases'),
    ('linguistics-nlp-research', 'Linguistics NLP research - syntax parsing, semantics, pragmatics, corpus tools, annotation'),
    # Sports science and analytics deep
    ('sports-biomechanics-tech', 'Sports biomechanics technology - motion capture, force plates, EMG, kinematics, OpenSim'),
    ('performance-analytics-advanced', 'Performance analytics advanced - wearable sensors, GPS tracking, HRV, load monitoring, SIMS'),
    ('sports-computer-vision', 'Sports computer vision - player tracking, action recognition, pose estimation, ball tracking'),
    ('esports-data-science', 'Esports data science - match data APIs, replay analysis, performance metrics, ML prediction'),
    ('fantasy-sports-analytics', 'Fantasy sports analytics - player projections, lineup optimization, pricing models, DFS tools'),
    ('sports-medicine-informatics', 'Sports medicine informatics - injury prediction, recovery tracking, EHR integration, athlete mgmt'),
    ('coaching-analytics-platform', 'Coaching analytics platform - tactical analysis, GPS data visualization, heat maps, opponent'),
    ('sports-broadcast-tech', 'Sports broadcast technology - live stats, AR overlays, replay systems, telestration tools'),
    ('stadium-tech-advanced', 'Stadium technology advanced - ticketing systems, fan engagement, WiFi density, digital signage'),
    ('sports-betting-algorithms', 'Sports betting algorithms - odds modeling, Kelly criterion, arbitrage detection, market making'),
    # Media production technology
    ('video-production-pipeline', 'Video production pipeline - editorial workflow, media management, conform, online finishing'),
    ('broadcast-engineering', 'Broadcast engineering - SDI, IP video, SMPTE 2110, playout automation, master control'),
    ('streaming-platform-engineering', 'Streaming platform engineering - video CDN, adaptive bitrate, DRM, metrics, player SDK'),
    ('podcast-engineering', 'Podcast engineering - recording, editing, hosting, distribution, RSS, dynamic ad insertion'),
    ('music-distribution-tech', 'Music distribution technology - DSP delivery, metadata standards, royalty calculation, CMS'),
    ('music-rights-management', 'Music rights management - ISRC, ISWC, mechanical rights, synchronization, Harry Fox, ASCAP'),
    ('game-audio-middleware', 'Game audio middleware - Wwise integration, FMOD, adaptive audio, interactive music, audio buses'),
    ('vfx-pipeline-advanced', 'VFX pipeline advanced - Nuke, Mari, Houdini FX, OpenEXR, USD, color pipeline, render farm'),
    ('animation-pipeline', 'Animation pipeline - rigging systems, USD workflow, Maya to Houdini, character animation tools'),
    ('live-production-tech', 'Live production technology - OBS, vMix, StreamYard, WebRTC, NDI, live switching, RTMP'),
    # Publishing and content platforms
    ('headless-cms-advanced', 'Headless CMS advanced - Contentful, Sanity, Strapi, content modeling, GraphQL APIs, CDN'),
    ('digital-publishing-platform', 'Digital publishing platform - EPUB3, accessibility, DRM, distribution, reading apps, analytics'),
    ('academic-publishing-tech', 'Academic publishing technology - manuscript submission, peer review, CrossRef, DOI, JATS XML'),
    ('news-cms-platform', 'News CMS platform - editorial workflow, wire feed integration, SEO, structured data, AMP'),
    ('e-learning-content-platform', 'E-learning content platform - SCORM, xAPI, content authoring, LMS integration, WCAG'),
    ('knowledge-graph-platform', 'Knowledge graph platform - RDF, SPARQL, property graphs, reasoning, entity resolution'),
    ('semantic-web-advanced', 'Semantic web advanced - OWL ontologies, linked data, schema.org, SHACL validation, SKOS'),
    ('wiki-platform-engineering', 'Wiki platform engineering - MediaWiki, Confluence, Notion, collaborative editing, versioning'),
    ('documentation-platform', 'Documentation platform - Docusaurus, MkDocs, Sphinx, versioning, search, multi-language'),
    ('content-intelligence-platform', 'Content intelligence platform - content scoring, SEO analysis, readability, topic modeling'),
    # Cultural and creative technology
    ('museum-tech-platform', 'Museum technology platform - collection management, digital exhibitions, visitor apps, TMS'),
    ('library-tech-advanced', 'Library technology advanced - ILS, Koha, linked data catalogs, digital preservation, MARC'),
    ('art-marketplace-tech', 'Art marketplace technology - provenance tracking, authentication, auction systems, valuation'),
    ('fashion-tech-platform', 'Fashion technology platform - 3D design, virtual try-on, PLM, sustainability tracking, retail'),
    ('architecture-bim-advanced', 'Architecture BIM advanced - Revit API, IFC, Dynamo, parametric design, collaboration workflows'),
    ('interior-design-tech', 'Interior design technology - space planning software, AR visualization, product configurator'),
    ('event-tech-platform', 'Event technology platform - registration, ticketing, virtual events, networking, badge printing'),
    ('travel-tech-advanced', 'Travel technology advanced - GDS integration, booking engines, dynamic pricing, loyalty systems'),
    ('hospitality-pms', 'Hospitality PMS - property management, channel management, revenue management, OTA integration'),
    ('restaurant-tech-advanced', 'Restaurant technology advanced - POS systems, kitchen display, delivery integrations, analytics'),
    # Agricultural and environmental technology deep
    ('precision-ag-platform', 'Precision agriculture platform - variable rate application, yield mapping, satellite imagery AI'),
    ('crop-simulation-models', 'Crop simulation models - DSSAT, APSIM, climate change impact, growth modeling, calibration'),
    ('livestock-genomics', 'Livestock genomics - genomic selection, GWAS, SNP chips, breeding values, pedigree analysis'),
    ('aquaculture-automation', 'Aquaculture automation - water quality monitoring, feeding control, harvest optimization, IoT'),
    ('forestry-data-systems', 'Forestry data systems - inventory management, LiDAR processing, fire risk, carbon sequestration'),
    ('environmental-dna', 'Environmental DNA technology - eDNA sampling, metabarcoding, biodiversity monitoring, qPCR'),
    ('soil-science-tech', 'Soil science technology - soil sensors, spectroscopy, microbiome analysis, carbon monitoring'),
    ('weather-forecasting-ml', 'Weather forecasting ML - NWP models, ensemble methods, nowcasting, bias correction, downscaling'),
    ('ocean-technology', 'Ocean technology - AUV programming, ocean sensors, NOAA data, wave modeling, bathymetry'),
    ('wildlife-monitoring-tech', 'Wildlife monitoring technology - camera traps, acoustic monitoring, GPS collars, bioacoustics'),
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
