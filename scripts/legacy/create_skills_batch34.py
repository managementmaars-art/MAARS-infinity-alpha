
import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # Sports and fitness technology
    ('sports-analytics-advanced', 'Sports analytics advanced - event data, tracking, expected goals, StatsBomb, Opta, R, Python'),
    ('biomechanics-analysis', 'Biomechanics analysis - motion capture, force plates, IMU, kinematics, kinetics, injury risk'),
    ('wearable-sports-tech', 'Wearable sports tech - GPS vests, heart rate, lactate, readiness, load monitoring, Catapult'),
    ('sports-video-analysis', 'Sports video analysis - Hudl, Nacsport, tagging, coding, dashboards, synchronization'),
    ('coaching-platforms', 'Coaching platforms - Catapult, STATSports, GPS tracking, dashboards, periodization, load'),
    ('sports-nutrition-tech', 'Sports nutrition technology - dietary analysis, supplementation timing, body composition, apps'),
    ('sports-medicine-tech', 'Sports medicine technology - injury surveillance, imaging, ultrasound, rehabilitation, return to play'),
    ('performance-testing', 'Performance testing tech - VO2max, force velocity, strength testing, normative data, benchmarks'),
    ('esports-analytics', 'Esports analytics - player performance, hero/champion meta, draft analysis, replay parsing'),
    ('esports-coaching-tools', 'Esports coaching tools - replay analysis, VOD review, strategic planning, team communication'),
    ('fitness-app-development', 'Fitness app development - workout tracking, progress metrics, social features, API integrations'),
    ('sports-betting-tech', 'Sports betting technology - odds compilation, risk management, APIs, live betting, trading'),
    ('stadium-technology', 'Stadium technology - IPTV, WiFi 6, cashless, access control, fan engagement, operations'),
    ('swimming-technology', 'Swimming technology - timing systems, touch pads, race analysis, stroke mechanics, starts'),
    ('cycling-technology', 'Cycling technology - power meters, training zones, WKO5, aerodynamics, fitting, marginal gains'),
    ('running-technology', 'Running technology - GPS watches, power, cadence, shoe sensors, track, biomechanics'),
    ('combat-sports-tech', 'Combat sports technology - punch tracking, judging systems, head impact, fight analytics'),
    ('rowing-technology', 'Rowing technology - Concept2, NK, ergometer, on-water telemetry, video analysis'),
    # Fitness and wellness technology
    ('fitness-wearables', 'Fitness wearables - Garmin, Polar, Wahoo, WHOOP, Oura, API integration, data analysis'),
    ('sleep-technology', 'Sleep technology - sleep staging, EEG, actigraphy, app development, SDK, coaching algorithms'),
    ('mental-wellness-apps', 'Mental wellness apps - CBT, mindfulness, mood tracking, crisis intervention, PHQ-9, GAD-7'),
    ('telehealth-platform', 'Telehealth platform - video consult, scheduling, EHR integration, prescribing, payment, security'),
    ('health-coaching-tech', 'Health coaching technology - behavior change, habit stacking, engagement, gamification, outcomes'),
    ('rehabilitation-technology', 'Rehabilitation technology - sensor-guided exercise, progress tracking, games, telerehab'),
    ('pain-management-tech', 'Pain management technology - TENS, neurostimulation, apps, VR therapy, outcome tracking'),
    # Environmental and sustainability technology
    ('ocean-monitoring', 'Ocean monitoring - Argo floats, autonomous gliders, satellite SST, buoys, IoT sensors, platforms'),
    ('conservation-technology', 'Conservation technology - camera traps, acoustic monitors, eDNA, GPS collars, citizen science'),
    ('biodiversity-informatics', 'Biodiversity informatics - GBIF, iNaturalist, taxonomic databases, occurrence data, mapping'),
    ('carbon-accounting', 'Carbon accounting - GHG protocol, scope 1/2/3, MRV, lifecycle assessment, carbon credits'),
    ('climate-adaptation-tech', 'Climate adaptation technology - flood modeling, heat islands, resilience planning, early warning'),
    ('remote-sensing-advanced', 'Remote sensing advanced - SAR, multispectral, hyperspectral, change detection, classification'),
    ('environmental-monitoring', 'Environmental monitoring - air quality, water quality, IoT sensors, data pipelines, alerts'),
    ('ecological-modeling', 'Ecological modeling - species distribution, population dynamics, habitat, MaxEnt, R, Python'),
    ('precision-conservation', 'Precision conservation - geospatial targeting, payment for ecosystem services, effectiveness'),
    ('waste-management-tech', 'Waste management technology - sorting AI, route optimization, recycling systems, circular economy'),
    ('water-management-tech', 'Water management technology - smart meters, leak detection, demand forecasting, SCADA, AMI'),
    # Space and aerospace technology
    ('satellite-design', 'Satellite design - bus, payload, power, ADCS, comms, thermal, launch integration, testing'),
    ('smallsat-cubesat', 'SmallSat/CubeSat - form factors, COTS, SDR, solar panels, deployables, rideshare, licensing'),
    ('ground-station-software', 'Ground station software - antenna control, scheduling, TT&C, CCSDS, demodulation, SLE'),
    ('mission-planning', 'Mission planning - STK, GMAT, SPICE, trajectory design, orbital mechanics, link budgets'),
    ('astrodynamics', 'Astrodynamics - Keplerian orbits, perturbations, maneuvers, Lambert problem, station-keeping'),
    ('launch-vehicle-engineering', 'Launch vehicle engineering - propulsion, staging, trajectory, GNC, recovery, structures'),
    ('spacecraft-gns', 'Spacecraft GN&C - attitude determination, sensors, actuators, control laws, MATLAB, simulation'),
    ('space-propulsion', 'Space propulsion - chemical, electric, ion thrusters, Hall effect, Isp, propellant management'),
    ('space-debris-tracking', 'Space debris tracking - TLE, conjunction analysis, collision avoidance, SSA, maneuver planning'),
    ('deep-space-communication', 'Deep space communication - DSN, coherent ranging, Doppler, coding, arraying, CCSDS AOS'),
    ('space-systems-engineering', 'Space systems engineering - MBSE, DOORS, V-model, trade studies, verification, ECSS'),
    ('lunar-mars-operations', 'Lunar/Mars operations - ISRU, surface power, comms delay, autonomy, habitat, life support'),
    ('space-weather', 'Space weather - solar flares, CMEs, radiation belts, geomagnetic storms, forecasting, impact'),
    # Automotive technology deep
    ('autonomous-driving', 'Autonomous driving - perception, prediction, planning, control, CARLA, LGSVL, safety, SOTIF'),
    ('adas-systems', 'ADAS systems - ACC, AEB, LKAS, BSD, parking assist, camera, radar, lidar, fusion'),
    ('automotive-cybersecurity', 'Automotive cybersecurity - ISO 21434, TARA, AUTOSAR SecOC, V2X security, EVITA'),
    ('connected-vehicle', 'Connected vehicle - V2X, DSRC, C-V2X, OTA, telematics, cloud backend, privacy'),
    ('autosar-advanced', 'AUTOSAR advanced - Classic, Adaptive, SWC, RTE, MCAL, communication stack, toolchain'),
    ('functional-safety-automotive', 'Functional safety automotive - ISO 26262, ASIL, FMEA, FTA, safety concept, verification'),
    ('electric-vehicle-systems', 'Electric vehicle systems - BMS, inverter, thermal management, charging, range modeling'),
    ('vehicle-diagnostics', 'Vehicle diagnostics - OBD-II, UDS, CAN, J1939, flashing, JTAG, calibration, INCA'),
    ('automotive-hmi', 'Automotive HMI - Qt, Android Auto, CarPlay, instrument cluster, OTA, NLP, voice, safety'),
    ('automotive-testing', 'Automotive testing - HIL, SIL, PIL, model-based testing, test automation, coverage, CAPL'),
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
