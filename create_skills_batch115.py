import os

base = r"c:\Users\mirza\MAARS-Command\.claude\skills"

# Domain: Advanced Materials Manufacturing
skills = [
    {"name": "advanced-ceramics-manufacturing", "description": "Manage advanced ceramics production including oxide and non-oxide processing, sintering optimization, net-shape forming, and quality certification."},
    {"name": "carbon-fiber-composite-manufacturing", "description": "Operate carbon fiber composite production including prepreg layup, autoclave curing, out-of-autoclave processes, and mechanical property testing."},
    {"name": "technical-glass-manufacturing", "description": "Manage technical glass production including borosilicate formulation, precision drawing, optical polishing, and glass-to-metal sealing operations."},
    {"name": "tungsten-carbide-production", "description": "Produce tungsten carbide components including powder blending, pressing, liquid phase sintering, grinding, and hardness verification."},
    {"name": "titanium-alloy-processing", "description": "Process titanium alloys including melting and casting, wrought processing, superplastic forming, chemical milling, and aerospace qualification."},
    {"name": "superalloy-manufacturing", "description": "Manufacture nickel superalloy components including vacuum induction melting, directional solidification, heat treatment cycles, and stress rupture testing."},
    {"name": "shape-memory-alloy-production", "description": "Produce shape memory alloys including nitinol melting, thermomechanical processing, transformation temperature control, and biomedical device qualification."},
    {"name": "amorphous-metal-manufacturing", "description": "Manufacture amorphous metals including melt spinning, ribbon production, core lamination, magnetic property optimization, and transformer application support."},
    {"name": "metal-matrix-composite-production", "description": "Produce metal matrix composites including powder metallurgy routes, liquid infiltration, stir casting, secondary processing, and tribology testing."},
    {"name": "refractory-metal-processing", "description": "Process refractory metals including molybdenum, niobium, and tantalum powder compaction, sintering, arc melting, rolling, and application engineering."},
]

# Domain: Photonics and Optical Systems Manufacturing
skills += [
    {"name": "precision-optics-manufacturing", "description": "Manufacture precision optical components including grinding, polishing, centering, coating deposition, and interferometric testing to lambda fractions."},
    {"name": "optical-lens-design-manufacturing", "description": "Design and manufacture optical lens systems including glass selection, aberration correction, assembly tolerancing, and MTF performance verification."},
    {"name": "laser-crystal-growth-technology", "description": "Grow laser crystals including Czochralski and flux methods, boule characterization, orientation cutting, polishing, and AR coating for gain media."},
    {"name": "optical-thin-film-coating", "description": "Deposit optical thin film coatings including AR, HR, and bandpass coatings via e-beam and sputtering, with spectrophotometric acceptance testing."},
    {"name": "fiber-optic-component-manufacturing", "description": "Manufacture fiber optic components including couplers, isolators, circulators, DWDM filters, and connectors with insertion loss and return loss testing."},
    {"name": "photodetector-manufacturing-ops", "description": "Produce photodetectors including InGaAs, Si, and APD devices with epitaxial growth, mesa etching, metallization, and responsivity characterization."},
    {"name": "laser-diode-manufacturing", "description": "Manufacture laser diodes including MOCVD epitaxy, cleaving, facet coating, chip bonding, and reliability burn-in screening for telecom and industrial use."},
    {"name": "lidar-system-manufacturing", "description": "Build LiDAR systems including pulsed and FMCW architectures, scan mechanism integration, time-of-flight electronics, and range accuracy calibration."},
    {"name": "infrared-camera-manufacturing", "description": "Manufacture infrared cameras including detector array hybridization, dewar assembly, read-out IC integration, calibration, and thermal sensitivity testing."},
    {"name": "optical-encoder-manufacturing", "description": "Produce optical encoders including disk patterning, detector array alignment, interpolation electronics assembly, and accuracy and repeatability qualification."},
]

# Domain: Medical Device Manufacturing Specialties
skills += [
    {"name": "implantable-cardiac-device-manufacturing", "description": "Manufacture implantable cardiac devices including pacemakers and ICDs with hermetic welding, battery integration, firmware loading, and sterility testing."},
    {"name": "orthopedic-implant-manufacturing", "description": "Produce orthopedic implants including CNC machining of cobalt-chrome and titanium, surface finishing, hydroxyapatite coating, and biocompatibility testing."},
    {"name": "neurostimulator-manufacturing", "description": "Build neurostimulators including deep brain and spinal cord stimulators with lead fabrication, electrode coating, connector assembly, and impedance testing."},
    {"name": "vascular-device-manufacturing", "description": "Manufacture vascular devices including stents, balloons, and catheters with laser cutting, electropolishing, hydrophilic coating, and burst pressure testing."},
    {"name": "ophthalmic-device-manufacturing", "description": "Produce ophthalmic devices including IOLs, phaco tips, and contact lenses with precision molding, optical power measurement, and sterility assurance."},
    {"name": "hearing-aid-manufacturing-ops", "description": "Manufacture hearing aids including receiver-in-canal designs with microphone assembly, DSP integration, acoustic testing, and custom shell fabrication."},
    {"name": "surgical-robot-manufacturing", "description": "Build surgical robotic systems including mechanical arm assembly, force-torque sensor integration, sterile drape qualification, and accuracy verification."},
    {"name": "diagnostic-imaging-detector-mfg", "description": "Manufacture diagnostic imaging detectors including flat panel X-ray detectors with scintillator deposition, TFT array bonding, and DQE measurement."},
    {"name": "in-vitro-diagnostic-instrument-mfg", "description": "Build in-vitro diagnostic instruments including immunoassay analyzers with fluidics assembly, photometric calibration, and reagent compatibility testing."},
    {"name": "wound-closure-device-manufacturing", "description": "Produce wound closure devices including staples, sutures, and surgical clips with wire forming, coating application, and tensile strength testing."},
]

# Domain: Biotechnology Equipment Manufacturing
skills += [
    {"name": "bioreactor-manufacturing-ops", "description": "Manufacture bioreactors including stirred tank, wave, and hollow fiber designs with vessel fabrication, sensor integration, and GMP cleaning validation."},
    {"name": "cell-culture-equipment-manufacturing", "description": "Build cell culture equipment including incubators, biosafety cabinets, and roller bottles with HEPA filtration, CO2 control, and uniformity qualification."},
    {"name": "fermentation-equipment-manufacturing", "description": "Manufacture fermentation vessels and accessories including pH probes, dissolved oxygen sensors, foam sensors, and harvest port assemblies."},
    {"name": "chromatography-column-manufacturing", "description": "Produce chromatography columns including media packing, axial compression systems, bed quality testing, and sanitization-in-place compatibility verification."},
    {"name": "tangential-flow-filtration-mfg", "description": "Build tangential flow filtration systems including cassette holders, pump heads, pressure regulators, and integrity testing apparatus."},
    {"name": "lyophilizer-manufacturing-ops", "description": "Manufacture freeze dryers including shelf systems, condenser coils, vacuum manifolds, CIP nozzle integration, and shelf temperature mapping qualification."},
    {"name": "bioprocess-sensor-manufacturing", "description": "Produce bioprocess sensors including single-use pH, DO, and turbidity probes with polymer body molding, calibration buffer preparation, and shelf-life testing."},
    {"name": "single-use-bioprocess-component-mfg", "description": "Manufacture single-use bioprocess components including bags, tubing assemblies, and manifolds with extractables testing and gamma irradiation validation."},
    {"name": "cell-therapy-manufacturing-equipment", "description": "Build cell therapy manufacturing equipment including closed system processing devices, cryopreservation equipment, and automated cell expansion platforms."},
    {"name": "analytical-scale-manufacturing", "description": "Produce analytical and precision scales including load cell calibration, vibration isolation integration, draft shield assembly, and OIML certification."},
]

# Domain: Environmental Technology Manufacturing
skills += [
    {"name": "air-quality-monitor-manufacturing", "description": "Build air quality monitors including particulate sensors, electrochemical gas sensors, data loggers, and EPA reference equivalent certification testing."},
    {"name": "water-quality-analyzer-manufacturing", "description": "Manufacture water quality analyzers including turbidimeters, TOC analyzers, and ion-selective electrode systems with reagent integration and span calibration."},
    {"name": "soil-monitoring-instrument-mfg", "description": "Produce soil monitoring instruments including TDR moisture sensors, soil gas samplers, and lysimeters with probe assembly and field calibration procedures."},
    {"name": "environmental-sampler-manufacturing", "description": "Build environmental samplers including automated water samplers, high-volume air samplers, and passive diffusion samplers with flow calibration and cleaning protocols."},
    {"name": "emission-monitoring-system-mfg", "description": "Manufacture continuous emission monitoring systems including gas analyzers, flow meters, data acquisition units, and EPA RATA certification support."},
    {"name": "noise-monitoring-equipment-mfg", "description": "Produce noise monitoring equipment including sound level meters, dosimeters, and noise mapping systems with IEC 61672 calibration and certification."},
    {"name": "groundwater-monitoring-equipment", "description": "Build groundwater monitoring equipment including pressure transducers, multi-level samplers, and dedicated pump systems with battery optimization."},
    {"name": "weather-station-manufacturing", "description": "Manufacture weather stations including anemometers, pyranometers, rain gauges, and data loggers with WMO calibration standards and telemetry integration."},
    {"name": "indoor-air-quality-monitor-mfg", "description": "Produce indoor air quality monitors including CO2, VOC, radon, and formaldehyde sensors with building automation system integration and certification."},
    {"name": "marine-environmental-monitor-mfg", "description": "Build marine environmental monitors including multi-parameter sondes, ADCP units, and moored sensor platforms with antifouling treatment and pressure rating."},
]

# Domain: Agricultural Equipment Manufacturing
skills += [
    {"name": "precision-planter-manufacturing", "description": "Manufacture precision planters including meter assemblies, down-force systems, row shutoffs, and electric drive units with seed spacing accuracy testing."},
    {"name": "sprayer-equipment-manufacturing", "description": "Build agricultural sprayers including boom systems, injection systems, section control, and pulse-width modulation nozzle bodies with flow calibration."},
    {"name": "harvester-header-manufacturing", "description": "Produce harvester headers including cutter bars, draper systems, reel assemblies, and crop lifters with synchronization testing and wear part qualification."},
    {"name": "grain-handling-equipment-mfg", "description": "Manufacture grain handling equipment including augers, bucket elevators, belt conveyors, and pneumatic conveyors with throughput and gentleness testing."},
    {"name": "grain-dryer-manufacturing-ops", "description": "Build grain dryers including mixed-flow, cross-flow, and tower designs with burner assemblies, airflow testing, and energy efficiency certification."},
    {"name": "irrigation-pivot-manufacturing", "description": "Manufacture center pivot irrigation systems including drive unit gearboxes, tower frames, pipe spans, end guns, and VRI control panel integration."},
    {"name": "tillage-equipment-manufacturing-ops", "description": "Produce tillage equipment including vertical tillage, strip-till, and disc tools with trip springs, gang angle adjustment, and soil engagement testing."},
    {"name": "baler-equipment-manufacturing", "description": "Build round and square balers including pickup, feeder, and knotting mechanisms with density adjustment, net wrapping systems, and bale ejection testing."},
    {"name": "livestock-equipment-manufacturing", "description": "Manufacture livestock equipment including automatic feeders, milking robots, sorting gates, and weighing platforms with hygiene design and ATEX compliance."},
    {"name": "greenhouse-climate-system-mfg", "description": "Build greenhouse climate systems including heating pipes, evaporative cooling pads, thermal screen drives, and climate computer integration with uniformity testing."},
]

# Domain: Food Processing Equipment Manufacturing
skills += [
    {"name": "food-mixing-equipment-manufacturing", "description": "Manufacture food mixing equipment including planetary mixers, spiral mixers, and continuous mixers with CIP compatibility, torque monitoring, and NSF certification."},
    {"name": "food-cooking-equipment-manufacturing", "description": "Build food cooking equipment including steam kettles, tilting skillets, combination ovens, and continuous cookers with temperature uniformity and sanitary design."},
    {"name": "food-slicing-portioning-equipment-mfg", "description": "Produce food slicing and portioning equipment including deli slicers, waterjet cutters, and weight-based portioners with yield optimization and USDA compliance."},
    {"name": "food-emulsification-equipment-mfg", "description": "Manufacture food emulsification equipment including colloid mills, high-pressure homogenizers, and rotor-stator systems with droplet size distribution testing."},
    {"name": "food-extrusion-equipment-manufacturing", "description": "Build food extruders including single and twin-screw designs for snacks, pasta, and textured proteins with die systems, cutting heads, and specific energy monitoring."},
    {"name": "food-thermal-processing-equipment", "description": "Manufacture food thermal processing equipment including retorts, UHT systems, and pasteurizers with F-value calculations, seal integrity testing, and FDA compliance."},
    {"name": "food-refrigeration-equipment-mfg", "description": "Build food refrigeration equipment including blast freezers, spiral freezers, and plate freezers with IQF performance, refrigerant charge optimization, and defrost cycling."},
    {"name": "food-drying-dehydration-equipment", "description": "Produce food drying equipment including spray dryers, drum dryers, and tunnel dryers with particle size distribution, moisture uniformity, and color retention testing."},
    {"name": "food-filling-equipment-manufacturing", "description": "Manufacture food filling equipment including piston fillers, volumetric fillers, and net weight fillers with fill accuracy, changeover time, and hygienic seal design."},
    {"name": "food-packaging-machine-manufacturing", "description": "Build food packaging machines including VFFS, HFFS, and tray sealers with film tension control, gas flushing, seal integrity, and metal detection integration."},
]

# Domain: Printing and Packaging Equipment Manufacturing
skills += [
    {"name": "offset-press-manufacturing", "description": "Manufacture offset printing presses including blanket cylinders, inking trains, dampening systems, and registration electronics with color density repeatability testing."},
    {"name": "digital-press-manufacturing", "description": "Build digital printing presses including electrophotographic and inkjet engines, media handling, RIP integration, and color gamut qualification for commercial print."},
    {"name": "flexographic-press-manufacturing", "description": "Produce flexographic printing presses including anilox roll management, doctor blade systems, UV curing, and register control for packaging applications."},
    {"name": "gravure-press-manufacturing", "description": "Manufacture rotogravure presses including cylinder engraving integration, ink supply systems, impression roll management, and drying tunnel design for decorative print."},
    {"name": "label-press-manufacturing", "description": "Build label printing presses including narrow-web offset, flexo, and combination presses with servo tension control, die station integration, and 100pct inspection."},
    {"name": "folding-carton-equipment-mfg", "description": "Manufacture folding carton equipment including die cutters, folder-gluers, and cartoning machines with crease quality testing and downstream integration."},
    {"name": "corrugated-equipment-manufacturing", "description": "Build corrugated board production lines including single facers, double backers, and slitter-scorers with flute profile control and ECT performance testing."},
    {"name": "rigid-box-manufacturing-equipment", "description": "Produce rigid box making equipment including casemakers, box lines, and lid-making machines with squareness, dimensional tolerance, and cosmetic finish control."},
    {"name": "bag-and-pouch-equipment-mfg", "description": "Manufacture bag and pouch making equipment including flat-bottom bag machines, standup pouch formers, and spout applicators with seal strength testing."},
    {"name": "blister-packaging-equipment-mfg", "description": "Build blister packaging equipment including thermoform-fill-seal machines, cold form lines, and inspection systems with seal integrity and child-resistance testing."},
]

# Domain: Textile and Apparel Equipment Manufacturing
skills += [
    {"name": "spinning-frame-manufacturing", "description": "Manufacture spinning frames including ring frames, open-end rotors, and air-jet spinners with spindle speed control, yarn tension monitoring, and ends-down tracking."},
    {"name": "weaving-loom-manufacturing", "description": "Build weaving looms including rapier, air-jet, and projectile designs with shedding mechanisms, weft insertion timing, and cloth fell position control."},
    {"name": "knitting-machine-manufacturing", "description": "Produce knitting machines including warp and weft knitting designs with cam systems, yarn feeders, defect sensors, and fabric tension control."},
    {"name": "dyeing-finishing-equipment-mfg", "description": "Manufacture textile dyeing and finishing equipment including jet dyeing machines, stenter frames, and calendering equipment with temperature and liquor ratio control."},
    {"name": "nonwoven-production-equipment-mfg", "description": "Build nonwoven production equipment including carding, air-lay, spunbond, and meltblown lines with basis weight control, tensile uniformity, and pore size testing."},
    {"name": "embroidery-machine-manufacturing", "description": "Manufacture commercial embroidery machines including multi-head systems, frame drives, thread tensioners, and color change automation with stitch count monitoring."},
    {"name": "quilting-machine-manufacturing", "description": "Produce quilting machines including channel quilters, multi-needle designs, and computerized pantograph systems with tension uniformity and pattern registration."},
    {"name": "industrial-sewing-equipment-mfg", "description": "Build industrial sewing equipment including lockstitch, chainstitch, and overlock machines with servo drives, thread monitoring, and automatic thread trimming."},
    {"name": "garment-cutting-equipment-mfg", "description": "Manufacture garment cutting equipment including automated cutting tables, knife systems, notchers, and drill markers with fabric utilization optimization."},
    {"name": "textile-inspection-equipment-mfg", "description": "Produce textile inspection equipment including inspection frames, pilling testers, color fastness equipment, and automated fabric defect detection systems."},
]

# Domain: Mining and Mineral Processing Equipment Manufacturing
skills += [
    {"name": "rock-drill-manufacturing", "description": "Manufacture rock drills including rotary percussion, DTH hammers, and hydraulic rock drills with bit retention, flushing channel design, and wear resistance testing."},
    {"name": "crushing-equipment-manufacturing", "description": "Build crushing equipment including jaw crushers, cone crushers, and impact crushers with liner management, power draw monitoring, and product gradation testing."},
    {"name": "grinding-mill-manufacturing", "description": "Manufacture grinding mills including ball mills, SAG mills, and vertical roller mills with liner selection, media charge optimization, and power draw modeling."},
    {"name": "screening-equipment-manufacturing", "description": "Produce screening equipment including vibrating screens, trommels, and banana screens with panel selection, throughput calculation, and blinding prevention."},
    {"name": "flotation-cell-manufacturing", "description": "Build flotation cells including mechanical and column designs with impeller geometry, air injection systems, froth control, and cell-to-cell flow modeling."},
    {"name": "thickener-clarifier-manufacturing", "description": "Manufacture thickeners and clarifiers including bridge-supported and truss designs with rake mechanism, torque overload protection, and underflow density control."},
    {"name": "cyclone-classifier-manufacturing", "description": "Produce hydrocyclone classifiers including ceramic-lined designs with vortex finder optimization, spigot selection, and cut size prediction modeling."},
    {"name": "filter-press-manufacturing", "description": "Build filter presses including membrane filter presses, recessed chamber, and automatic plate shifters with cake washing efficiency and moisture content testing."},
    {"name": "mine-ventilation-fan-manufacturing", "description": "Manufacture mine ventilation fans including axial flow and centrifugal designs with blade pitch adjustment, anti-stall control, and ATEX certification for gassy mines."},
    {"name": "longwall-equipment-manufacturing", "description": "Build longwall mining equipment including armored face conveyors, powered roof supports, and shearer loaders with hydraulic load sensing and face automation."},
]

# Domain: Oil and Gas Equipment Manufacturing
skills += [
    {"name": "wellhead-equipment-manufacturing", "description": "Manufacture wellhead equipment including christmas trees, casing heads, and tubing hangers with pressure rating qualification, H2S service testing, and API 6A compliance."},
    {"name": "subsea-christmas-tree-manufacturing", "description": "Build subsea christmas trees including horizontal and vertical designs with ROV interface panels, hydraulic actuation, and 15000 psi pressure testing."},
    {"name": "blowout-preventer-manufacturing-ops", "description": "Manufacture blowout preventers including annular and ram BOPs with rubber element qualification, wellbore seal testing, and API 16A certification."},
    {"name": "drilling-jar-manufacturing", "description": "Produce drilling jars including mechanical, hydraulic, and hydro-mechanical designs with impact force testing, tripping-in torque measurement, and service life validation."},
    {"name": "drill-bit-manufacturing-technology", "description": "Manufacture drill bits including PDC, tri-cone roller, and diamond core designs with cutter placement optimization, hydraulics modeling, and formation-specific performance testing."},
    {"name": "downhole-motor-manufacturing", "description": "Build positive displacement downhole motors including power section molding, bearing pack assembly, bit box qualification, and flow-torque performance mapping."},
    {"name": "mwd-lwd-instrument-manufacturing", "description": "Manufacture MWD/LWD instruments including drill collar machining, sensor integration, pressure vessel assembly, and calibration at elevated temperature and pressure."},
    {"name": "completion-tool-manufacturing", "description": "Produce completion tools including packers, plugs, sliding sleeves, and frac ports with elastomer qualification, load testing, and pressure cycling verification."},
    {"name": "pipeline-pig-manufacturing", "description": "Build pipeline pigs including foam pigs, cleaning pigs, gauging pigs, and intelligent inspection pigs with sizing, bypass ratio calculation, and operational trial testing."},
    {"name": "subsea-umbilical-manufacturing", "description": "Manufacture subsea umbilicals including thermoplastic hoses, power cables, and signal cables with pressure and electrical testing, bend stiffener qualification, and cathodic protection."},
]

# Domain: Power Generation Equipment Manufacturing
skills += [
    {"name": "steam-turbine-blade-manufacturing", "description": "Manufacture steam turbine blades including precision forging, airfoil machining, root profiling, coating application, and frequency tuning for resonance avoidance."},
    {"name": "gas-turbine-combustor-manufacturing", "description": "Build gas turbine combustors including liner fabrication, effusion cooling hole drilling, thermal barrier coating application, and rig combustion testing."},
    {"name": "wind-turbine-nacelle-manufacturing", "description": "Manufacture wind turbine nacelles including main frame welding, gearbox and generator integration, cooling system assembly, and power curve commissioning."},
    {"name": "hydraulic-turbine-manufacturing", "description": "Produce hydraulic turbines including Francis, Pelton, and Kaplan designs with runner casting, cavitation testing, and efficiency hill chart measurement."},
    {"name": "generator-stator-manufacturing", "description": "Manufacture generator stators including core lamination stacking, winding insertion, wedge installation, vacuum pressure impregnation, and high-potential testing."},
    {"name": "transformer-core-manufacturing", "description": "Build transformer cores including grain-oriented silicon steel cutting, step-lap jointing, core loss testing, and noise level measurement for power transformer assembly."},
    {"name": "power-capacitor-manufacturing", "description": "Manufacture power capacitors including film winding, impregnation, case assembly, dielectric withstand testing, and partial discharge measurement for reactive compensation."},
    {"name": "circuit-breaker-manufacturing", "description": "Produce medium and high voltage circuit breakers including contact system assembly, arc quenching mechanism, operating mechanism integration, and dielectric type testing."},
    {"name": "surge-arrester-manufacturing", "description": "Manufacture surge arresters including ZnO varistor stacking, housing application, sealing, and energy absorption capacity testing for transmission line protection."},
    {"name": "power-cable-manufacturing-ops", "description": "Build power cables including conductor stranding, insulation extrusion, screen application, armoring, and routine electrical testing for utility and industrial use."},
]

# Domain: Aerospace Manufacturing Specialties
skills += [
    {"name": "aircraft-structural-component-mfg", "description": "Manufacture aircraft structural components including spars, frames, and skin panels with automated fiber placement, autoclave curing, and ultrasonic inspection."},
    {"name": "engine-nacelle-manufacturing", "description": "Build engine nacelles including inner fixed structure, fan cowl, and thrust reverser with composite lay-up, metal bonding, acoustic liner installation, and FAA conformity."},
    {"name": "landing-gear-manufacturing", "description": "Manufacture landing gear including main and nose gear assemblies with steel and titanium machining, hard chrome plating, hydraulic component assembly, and drop testing."},
    {"name": "aerospace-fastener-manufacturing", "description": "Produce aerospace fasteners including titanium, steel, and aluminum bolts with heading, threading, heat treatment, cadmium plating, and AS9100 lot traceability."},
    {"name": "aircraft-window-manufacturing", "description": "Build aircraft windows including stretched acrylic forming, heater element embedment, edge treatment, optical distortion measurement, and bird strike resistance testing."},
    {"name": "aircraft-seat-manufacturing", "description": "Manufacture aircraft seats including structure fabrication, foam profile cutting, cover sewing, belt assembly, and 16g dynamic forward-facing crash test certification."},
    {"name": "avionics-box-manufacturing", "description": "Build avionics LRUs including chassis machining, PCB population, conformal coating, EMI shielding installation, and DO-160 environmental qualification."},
    {"name": "rocket-nozzle-manufacturing", "description": "Manufacture rocket nozzles including carbon-carbon composite lay-up, phenolic ablator bonding, graphite throat insert assembly, and hot-fire chamber pressure testing."},
    {"name": "propellant-tank-manufacturing", "description": "Produce spacecraft propellant tanks including titanium forming, electron beam welding, proof pressure testing, cleanliness verification, and leak testing."},
    {"name": "satellite-structure-manufacturing", "description": "Build satellite structures including carbon fiber honeycomb panels, insert installation, interface ring machining, dimensional verification, and modal survey testing."},
]

# Domain: Railway and Transportation Equipment Manufacturing
skills += [
    {"name": "railway-bogie-manufacturing", "description": "Manufacture railway bogies including frame welding, wheelset assembly, suspension spring and damper integration, brake rigging, and dynamic load testing."},
    {"name": "railway-wheel-axle-manufacturing", "description": "Produce railway wheels and axles including forging, rim profiling, axle turning, press fitting, ultrasonic inspection, and full-scale fatigue testing."},
    {"name": "pantograph-manufacturing", "description": "Build railway pantographs including collector head assembly, spring stiffness calibration, carbon insert bonding, pantograph dynamics testing, and contact force measurement."},
    {"name": "rail-fastening-system-manufacturing", "description": "Manufacture rail fastening systems including baseplate casting, resilient pad vulcanization, clip rolling, and load-deflection and fatigue testing."},
    {"name": "signaling-equipment-manufacturing", "description": "Build railway signaling equipment including axle counters, track circuits, point machines, and balise transponders with SIL certification and EMC testing."},
    {"name": "traction-converter-manufacturing", "description": "Manufacture traction power converters including IGBT module selection, heatsink assembly, DC link capacitor installation, and thermal and electrical qualification."},
    {"name": "maritime-propulsion-system-mfg", "description": "Build maritime propulsion systems including propeller casting, shaft machining, sterntube assembly, controllable pitch mechanism, and cavitation tunnel testing."},
    {"name": "marine-anchor-chain-manufacturing", "description": "Manufacture anchor chain including studless and studlink designs with steel bar forming, flash butt welding, proof load testing, and class society certification."},
    {"name": "offshore-crane-manufacturing", "description": "Build offshore cranes including pedestal structures, boom and jib assembly, winch drum fabrication, load cell integration, and SWL proof load testing to API 2C."},
    {"name": "heavy-truck-component-manufacturing", "description": "Produce heavy truck components including axle housings, fifth wheel assemblies, air spring suspensions, and brake caliper units with durability and NVH testing."},
]

os.makedirs(base, exist_ok=True)

SKILL_TEMPLATE = '''---
name: {name}
description: {description}
---

## Overview
{description}

## Core Framework
- Analyze requirements and constraints specific to {name}
- Design workflows aligned to industry best practices
- Implement automation and intelligence layers
- Monitor outcomes and continuously improve

## Key Prompts
- "Initiate {name} workflow for [context]"
- "Analyze current state of {name} and identify gaps"
- "Generate recommendations for {name} optimization"
- "Create detailed plan for {name} execution"

## Best Practices
- Always validate inputs against domain-specific regulatory and compliance requirements
- Maintain audit trails for all automated decisions
- Escalate ambiguous or high-risk decisions to human reviewers
- Use structured data formats for downstream system integration

## Common Patterns
- Intake and triage incoming work items
- Route to appropriate specialist or automated handler
- Track status and SLA compliance
- Generate reports and dashboards for stakeholders

## Models to Use
- Complex analysis and strategy: claude-opus-4-6
- Standard workflows and generation: claude-sonnet-4-6
- High-volume classification and routing: claude-haiku-4-5-20251001
'''

count = 0
for skill in skills:
    skill_dir = os.path.join(base, skill["name"])
    os.makedirs(skill_dir, exist_ok=True)
    skill_path = os.path.join(skill_dir, "SKILL.md")
    with open(skill_path, "w", encoding="utf-8") as f:
        f.write(SKILL_TEMPLATE.format(name=skill["name"], description=skill["description"]))
    count += 1

print(f"Done: {count} skills")
