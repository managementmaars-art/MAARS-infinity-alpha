
import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # Computer vision specialized
    ('3d-reconstruction', '3D reconstruction - NeRF, 3D Gaussian Splatting, structure from motion, SLAM, depth estimation'),
    ('medical-image-analysis', 'Medical image analysis - segmentation, registration, DICOM processing, nnUNet, radiomics'),
    ('satellite-image-analysis', 'Satellite image analysis - multispectral, change detection, land cover classification, GEE'),
    ('industrial-vision', 'Industrial computer vision - defect detection, measurement, OCR, barcode, calibration, Halcon'),
    ('video-understanding-advanced', 'Video understanding - temporal models, action recognition, video transformers, optical flow'),
    ('3d-point-cloud-advanced', 'Point cloud advanced - registration, segmentation, PointNet++, KD-tree, voxelization'),
    ('face-analysis', 'Face analysis - detection, recognition, anti-spoofing, landmark, emotion, age, DeepFace'),
    ('ocr-document-understanding', 'OCR and document understanding - layout analysis, table extraction, form processing, VQA'),
    ('autonomous-perception', 'Autonomous perception - BEV representation, sensor fusion, object detection 3D, tracking'),
    ('generative-vision-models', 'Generative vision models - GAN training, diffusion fine-tuning, ControlNet, inpainting'),
    # NLP specialized
    ('information-extraction', 'Information extraction - NER, relation extraction, event detection, coreference, OpenIE'),
    ('dialogue-systems-advanced', 'Dialogue systems advanced - dialogue state tracking, belief update, policy learning, TOD'),
    ('text-generation-advanced', 'Text generation advanced - controlled generation, constrained decoding, watermarking, RAG'),
    ('multilingual-nlp', 'Multilingual NLP - cross-lingual transfer, mBERT, XLM-R, low-resource, code-switching'),
    ('clinical-nlp-advanced', 'Clinical NLP advanced - de-identification, ICD coding, clinical NER, UMLS, n2c2'),
    ('legal-nlp-advanced', 'Legal NLP advanced - contract analysis, citation extraction, argument mining, LexNLP'),
    ('conversational-ai-advanced', 'Conversational AI advanced - intent recognition, slot filling, contextual understanding'),
    ('semantic-similarity', 'Semantic similarity - bi-encoders, cross-encoders, contrastive learning, ANN indexing'),
    ('question-answering-advanced', 'Question answering advanced - reading comprehension, open-domain QA, multi-hop, KBQA'),
    ('text-summarization-advanced', 'Text summarization advanced - extractive, abstractive, hierarchical, multi-document'),
    # Geospatial deep
    ('remote-sensing-advanced', 'Remote sensing advanced - satellite imagery, hyperspectral, SAR, change detection, LiDAR'),
    ('geospatial-ml', 'Geospatial ML - geo-aware models, satellite foundation models, spatiotemporal prediction'),
    ('spatial-databases-advanced', 'Spatial databases advanced - PostGIS, Oracle Spatial, partitioning, index strategies'),
    ('routing-optimization', 'Routing optimization - VRP, TSP, OSRM, Valhalla, GraphHopper, fleet optimization'),
    ('gis-3d-analysis', '3D GIS analysis - CityGML, 3D Tiles, point cloud processing, urban digital twin'),
    ('climate-data-analysis', 'Climate data analysis - CMIP6, ERA5, xarray, zarr, Pangeo, climate downscaling'),
    ('elevation-analysis', 'Elevation analysis - DEM processing, terrain analysis, watershed delineation, LiDAR DEM'),
    ('indoor-positioning', 'Indoor positioning - BLE beacons, WiFi fingerprinting, UWB, SLAM, floor plan analysis'),
    ('geospatial-visualization', 'Geospatial visualization - Deck.gl, Kepler.gl, MapLibre, CesiumJS, 3D globe rendering'),
    ('geospatial-etl', 'Geospatial ETL - GDAL/OGR, Fiona, Shapely, coordinate reference systems, format conversion'),
    # Healthcare IT specialized
    ('clinical-decision-support-advanced', 'Clinical decision support advanced - CDS Hooks, SMART on FHIR, rules engines, NLP'),
    ('healthcare-interoperability', 'Healthcare interoperability - HL7 FHIR R4, IHE profiles, X12, NCPDP, C-CDA'),
    ('medical-device-connectivity', 'Medical device connectivity - IEEE 11073, HL7 POCT, bedside monitors, wearables, IHE PCD'),
    ('population-health-analytics', 'Population health analytics - risk stratification, care gaps, HEDIS, quality measures'),
    ('pharmacy-systems-advanced', 'Pharmacy systems advanced - CPOE, BCMA, drug interaction checking, PK/PD modeling'),
    ('radiology-informatics-advanced', 'Radiology informatics - DICOM WADO, OHIF viewer, AI-assisted reporting, RIS/PACS'),
    ('genetic-counseling-tech', 'Genetic counseling tech - PanelApp, ClinVar, variant interpretation, ACMG criteria'),
    ('precision-medicine-platform', 'Precision medicine platform - biomarker analysis, companion diagnostics, molecular tumor board'),
    ('healthcare-nlp-advanced', 'Healthcare NLP advanced - clinical BERT, Bio-ELECTRA, MIMIC dataset, note summarization'),
    ('telehealth-advanced', 'Telehealth advanced - WebRTC video, remote monitoring integration, asynchronous care, RPM'),
    # Supply chain and logistics technology
    ('supply-chain-optimization', 'Supply chain optimization - S&OP, demand sensing, multi-echelon inventory, network design'),
    ('warehouse-robotics', 'Warehouse robotics - AMR, conveyors, sorters, pick-and-place, WES integration, slotting'),
    ('logistics-data-platform', 'Logistics data platform - shipment tracking, visibility, event streaming, ML ETA'),
    ('customs-compliance-platform', 'Customs compliance platform - HTS classification, duty calculation, trade agreements, AES'),
    ('cold-chain-advanced', 'Cold chain advanced - temperature monitoring, HACCP, GDP compliance, IoT sensors, deviation'),
    ('reverse-logistics', 'Reverse logistics - returns management, RMA workflows, disposition, refurbishment, recycling'),
    ('freight-brokerage-tech', 'Freight brokerage technology - load board, rate engines, carrier matching, TMS integration'),
    ('last-mile-advanced', 'Last mile delivery advanced - route optimization, proof of delivery, smart lockers, micro-fulfillment'),
    ('trade-finance-advanced', 'Trade finance advanced - LC processing, documentary credit, factoring, supply chain finance'),
    ('demand-forecasting-ml', 'Demand forecasting ML - hierarchical forecasting, intermittent demand, Prophet, TFT, LightGBM'),
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
