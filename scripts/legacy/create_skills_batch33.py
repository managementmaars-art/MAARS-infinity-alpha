
import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # Construction and built environment technology
    ('bim-advanced', 'BIM advanced - Revit, IFC, COBie, LOD, clash detection, 4D/5D, OpenBIM, digital twin'),
    ('autodesk-revit', 'Autodesk Revit - families, parameters, schedules, worksharing, API, dynamo, interop'),
    ('civil-engineering-software', 'Civil engineering software - AutoCAD Civil 3D, drainage, roads, grading, quantities'),
    ('structural-analysis-software', 'Structural analysis - SAP2000, ETABS, STAAD, RISA, Tekla, finite element modeling'),
    ('construction-management', 'Construction management - Procore, PlanGrid, scheduling, RFI, submittals, cost tracking'),
    ('primavera-scheduling', 'Primavera P6 - WBS, activities, resources, baselines, critical path, claims, reporting'),
    ('geotechnical-software', 'Geotechnical software - PLAXIS, GEO5, slope stability, settlement, pile design, borings'),
    ('hydraulic-modeling', 'Hydraulic modeling - HEC-RAS, SWMM, InfoWorks, floodplain, drainage, stormwater'),
    ('transportation-engineering', 'Transportation engineering - traffic simulation, VISSIM, SYNCHRO, HCM, signal timing'),
    ('gis-advanced', 'GIS advanced - spatial analysis, raster, network analysis, geoprocessing, ModelBuilder, REST'),
    ('lidar-processing', 'LiDAR processing - point clouds, classification, DTM, DSM, feature extraction, drone survey'),
    ('photogrammetry', 'Photogrammetry - structure from motion, Agisoft, Pix4D, point cloud, accuracy, calibration'),
    ('drone-surveying', 'Drone surveying - flight planning, GCPs, photogrammetry, LiDAR, corridor, legal, safety'),
    ('smart-building-iot', 'Smart building IoT - BMS, SCADA, occupancy, HVAC control, energy management, protocols'),
    ('building-energy-modeling', 'Building energy modeling - EnergyPlus, OpenStudio, eQUEST, LEED, ASHRAE, Passivhaus'),
    # Mining and resources technology
    ('mining-software', 'Mining software - Vulcan, Surpac, Datamine, Minesight, block models, pit optimization'),
    ('mining-simulation', 'Mining simulation - fleet management, dispatch, haulage, conveyor, ventilation, blast modeling'),
    ('geoscience-software', 'Geoscience software - Petrel, Kingdom, Landmark, seismic interpretation, log analysis'),
    ('reservoir-simulation', 'Reservoir simulation - Eclipse, tNavigator, CMG, IMEX, compositional, history matching'),
    ('well-log-analysis', 'Well log analysis - petrophysics, LAS files, Techlog, IP, porosity, saturation, lithology'),
    ('oilfield-data', 'Oilfield data - WITSML, PRODML, OpenWells, EDM, production, drilling, completion data'),
    # Agriculture technology deep
    ('precision-agriculture', 'Precision agriculture - variable rate, prescription maps, GPS guidance, yield monitoring'),
    ('crop-modeling', 'Crop modeling - DSSAT, APSIM, AquaCrop, growth stages, soil water, nutrients, yield'),
    ('agricultural-iot', 'Agricultural IoT - soil sensors, weather stations, irrigation control, pest traps, connectivity'),
    ('farm-management-software', 'Farm management software - AgX, Climate FieldView, Granular, records, compliance'),
    ('vertical-farming-tech', 'Vertical farming technology - lighting, HVAC, nutrients, automation, AI optimization, ROI'),
    ('aquaculture-technology', 'Aquaculture technology - recirculating, water quality, feeding automation, fish health, genetics'),
    ('livestock-technology', 'Livestock technology - RFID, estrus detection, milking robots, health monitoring, genetics'),
    ('agri-drone-spraying', 'Agricultural drone spraying - flow rate, coverage, obstacle avoidance, tank mixing, regulation'),
    ('food-safety-technology', 'Food safety technology - HACCP, traceability, blockchain, rapid testing, FSMA, GFSI'),
    ('food-processing-automation', 'Food processing automation - SCADA, vision inspection, robotics, CIP, safety, OEE'),
    # Textile and apparel technology
    ('textile-cad', 'Textile CAD - Lectra, Optitex, pattern making, grading, nesting, 3D virtual fitting'),
    ('fabric-simulation', 'Fabric simulation - CLO 3D, Marvelous Designer, drape, physical properties, rendering'),
    ('textile-testing', 'Textile testing - tensile, tear, abrasion, color fastness, dimensional stability, moisture'),
    ('apparel-plm', 'Apparel PLM - Centric, PTC FlexPLM, techpacks, BOM, costing, compliance, supplier'),
    # Printing and publishing technology
    ('prepress-workflow', 'Prepress workflow - color management, proofing, PDF/X, imposition, preflight, JDF'),
    ('digital-printing-advanced', 'Digital printing advanced - inkjet, laser, variable data, substrate handling, icc profiles'),
    ('packaging-design-tech', 'Packaging design tech - structural, dieline, prototyping, CAPE, TOPS Pro, simulation'),
    ('3d-printing-advanced', '3D printing advanced - FDM, SLA, SLS, DMLS, topology optimization, supports, post-processing'),
    ('additive-manufacturing', 'Additive manufacturing - design for AM, lattice structures, multi-material, simulation, qualification'),
    # Logistics and supply chain tech
    ('warehouse-management', 'Warehouse management - WMS, picking, putaway, slotting, inventory accuracy, RFID, AGV'),
    ('transportation-management', 'TMS - route optimization, load building, carrier management, freight audit, visibility'),
    ('last-mile-delivery', 'Last mile delivery - route optimization, ORTOOLS, proof of delivery, drones, locker, returns'),
    ('cold-chain-management', 'Cold chain management - temperature monitoring, validation, GDP, pharmaceutical, 21 CFR Part 11'),
    ('supply-chain-visibility', 'Supply chain visibility - track and trace, EPCIS, RFID, IoT, blockchain, risk monitoring'),
    ('demand-planning-advanced', 'Demand planning advanced - statistical forecasting, ML, consensus planning, IBF, S&OP'),
    ('inventory-optimization', 'Inventory optimization - safety stock, reorder points, multi-echelon, stochastic, simulation'),
    ('digital-twin-supply-chain', 'Digital twin supply chain - simulation, disruption modeling, network design, scenario analysis'),
    # Energy sector technology
    ('energy-trading-systems', 'Energy trading systems - ETRM, power markets, day-ahead, balancing, risk, settlement'),
    ('smart-grid-advanced', 'Smart grid advanced - AMI, DERMS, ADMS, demand response, microgrids, EV integration'),
    ('grid-modeling', 'Grid modeling - PSS/E, DIgSILENT, PowerWorld, load flow, stability, protection coordination'),
    ('solar-energy-systems', 'Solar energy systems - PVsyst, simulation, shading, MPPT, string inverters, monitoring'),
    ('wind-energy-systems', 'Wind energy systems - AEP calculation, micrositing, wake modeling, SCADA, condition monitoring'),
    ('battery-storage-systems', 'Battery storage systems - sizing, cycling, degradation, BMS, grid services, business case'),
    ('hydrogen-technology', 'Hydrogen technology - electrolysis, fuel cells, storage, safety, PEMFC, SOE, green H2'),
    ('nuclear-technology', 'Nuclear technology - PWR, BWR, control systems, safety analysis, instrumentation, waste'),
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
