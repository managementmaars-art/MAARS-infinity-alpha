import os

base = r"c:\Users\mirza\MAARS-Command\.claude\skills"

# Domain: Industrial Automation Systems
skills = [
    {"name": "plc-scada-integration", "description": "Integrate PLC and SCADA systems for industrial automation including communication protocols, data historian integration, and HMI configuration."},
    {"name": "industrial-automation-commissioning", "description": "Commission industrial automation systems including factory acceptance testing, site acceptance testing, loop checkout, and startup support."},
    {"name": "robot-cell-safety-validation", "description": "Validate robotic cell safety systems including risk assessment, safety zone configuration, light curtain testing, and CE marking compliance."},
    {"name": "motion-control-systems", "description": "Manage motion control system programs including servo axis configuration, multi-axis coordination, and precision positioning applications."},
    {"name": "industrial-network-design", "description": "Design industrial automation networks including EtherNet/IP, PROFINET, Modbus TCP topology design and bandwidth management."},
    {"name": "automated-guided-vehicle-systems", "description": "Design and manage AGV system programs including traffic management, charging station scheduling, and WMS integration."},
    {"name": "vision-guided-assembly-systems", "description": "Implement vision-guided assembly automation including pick-and-place calibration, assembly verification, and defect rejection systems."},
    {"name": "industrial-automation-testing", "description": "Execute industrial automation testing programs including simulation-based testing, production line validation, and OEE measurement."},
    {"name": "batch-process-automation", "description": "Automate batch process operations including ISA-88 recipe management, phase logic development, and batch reporting integration."},
    {"name": "automation-project-management", "description": "Manage industrial automation projects including scope definition, vendor management, milestone tracking, and commissioning coordination."},
]

# Domain: Specialty Gases Industry
skills += [
    {"name": "specialty-gas-cylinder-operations", "description": "Manage specialty gas cylinder operations including cylinder preparation, gas filling, analytical verification, and tracking."},
    {"name": "gas-blending-operations", "description": "Manage specialty gas blending including gravimetric blending, cylinder preparation, mixture certification, and SPC monitoring."},
    {"name": "gas-handling-safety-programs", "description": "Implement industrial gas handling safety programs including emergency response procedures, storage compliance, and handler training."},
    {"name": "ultra-high-purity-gas-ops", "description": "Manage ultra-high purity gas operations for semiconductor applications including contamination control, purity verification, and supply chain management."},
    {"name": "gas-distribution-fleet-mgmt", "description": "Manage gas distribution fleet operations including cylinder logistics, delivery scheduling, DOT compliance, and driver training."},
    {"name": "gas-customer-technical-service", "description": "Provide gas customer technical service including application support, equipment troubleshooting, and gas selection guidance."},
    {"name": "cryogenic-systems-operations", "description": "Operate cryogenic systems including liquid gas storage, vaporizer management, pressure building circuits, and safety valve testing."},
    {"name": "gas-regulatory-reporting", "description": "Manage gas industry regulatory reporting including DOT cylinder qualification records, OSHA hazcom compliance, and EPA reporting."},
    {"name": "gas-demand-forecasting", "description": "Forecast industrial gas demand using historical consumption analytics, seasonal patterns, and customer expansion planning."},
    {"name": "gas-production-quality-control", "description": "Execute gas production quality control programs including purity analysis, moisture testing, and product specification compliance."},
]

# Domain: Abrasives Manufacturing
skills += [
    {"name": "bonded-abrasives-manufacturing", "description": "Manage bonded abrasives manufacturing including grinding wheel mix preparation, pressing, kiln firing, and balance testing."},
    {"name": "coated-abrasives-manufacturing", "description": "Manage coated abrasives manufacturing including backing preparation, resin coating, grain application, and product testing."},
    {"name": "superabrasives-operations", "description": "Manage superabrasive product operations including diamond and CBN wheel manufacturing, dressing operations, and application support."},
    {"name": "abrasive-raw-material-mgmt", "description": "Manage abrasive raw material supply including alumina, silicon carbide, and specialty grain procurement with quality verification."},
    {"name": "abrasive-product-development", "description": "Develop abrasive products from application requirements through grain selection, bond chemistry, and performance validation."},
    {"name": "abrasive-application-engineering", "description": "Provide abrasive application engineering support including speed and feed optimization, coolant selection, and process parameter development."},
    {"name": "abrasive-quality-testing", "description": "Execute abrasive product quality testing programs including hardness testing, porosity analysis, burst speed testing, and performance trials."},
    {"name": "abrasive-safety-compliance", "description": "Manage abrasive safety compliance programs including ANSI B7.1 standards, mounted point safety, and operator training."},
    {"name": "abrasive-distribution-management", "description": "Manage abrasive product distribution through industrial distributor and direct channels including stocking programs and application support."},
    {"name": "abrasive-market-development", "description": "Drive abrasive market development in metalworking, aerospace, and precision grinding segments with application case studies."},
]

# Domain: Springs Manufacturing
skills += [
    {"name": "compression-spring-manufacturing", "description": "Manage compression spring manufacturing including coiling operations, stress relief, end grinding, and load rate testing."},
    {"name": "extension-spring-manufacturing", "description": "Manage extension spring manufacturing including coiling, hook formation, initial tension setting, and load deflection testing."},
    {"name": "torsion-spring-manufacturing", "description": "Manage torsion spring manufacturing including coiling, leg forming, angular measurement, and torque rate verification."},
    {"name": "spring-raw-material-sourcing", "description": "Source spring manufacturing materials including music wire, stainless steel, and alloy wire with material certification tracking."},
    {"name": "spring-quality-management", "description": "Implement spring quality management programs including load testing, dimensional inspection, and surface finish verification."},
    {"name": "spring-application-engineering", "description": "Provide spring application engineering support including spring rate calculation, stress analysis, and fatigue life estimation."},
    {"name": "specialty-spring-manufacturing", "description": "Manage specialty spring products including constant force springs, volute springs, and custom flat spring fabrication."},
    {"name": "spring-heat-treatment", "description": "Manage spring heat treatment operations including stress relieving, precipitation hardening, and shot peening programs."},
    {"name": "spring-surface-finishing", "description": "Manage spring surface finishing programs including shot blasting, electroplating, powder coating, and corrosion resistance testing."},
    {"name": "spring-distribution-channel", "description": "Manage spring product distribution through industrial distributors, OEM programs, and catalog channels with technical support."},
]

# Domain: Industrial Valves Manufacturing
skills += [
    {"name": "ball-valve-manufacturing", "description": "Manage ball valve manufacturing including body machining, ball lapping, seat assembly, pressure testing, and API 6D compliance."},
    {"name": "gate-valve-manufacturing", "description": "Manage gate valve manufacturing including body casting, machining, wedge assembly, stem sealing, and API 600 compliance."},
    {"name": "butterfly-valve-manufacturing", "description": "Manage butterfly valve manufacturing including disc machining, liner molding, shaft assembly, and torque testing programs."},
    {"name": "control-valve-manufacturing", "description": "Manage control valve manufacturing including body assembly, trim selection, actuator mounting, and flow coefficient verification."},
    {"name": "valve-actuation-systems", "description": "Manage valve actuation system programs including pneumatic actuators, electric actuators, fail-safe systems, and position feedback."},
    {"name": "valve-testing-qualification", "description": "Execute valve testing and qualification programs including API leakage testing, fire-safe testing, and low-temperature performance."},
    {"name": "valve-materials-engineering", "description": "Manage valve materials engineering including exotic alloy specifications, heat number traceability, and NACE MR0175 compliance."},
    {"name": "valve-aftermarket-service", "description": "Manage valve aftermarket service operations including field repair, trim kitting, actuator upgrades, and valve automation programs."},
    {"name": "valve-sales-applications", "description": "Manage valve sales and application engineering across process industry, power generation, and water treatment markets."},
    {"name": "valve-quality-systems", "description": "Implement valve quality management systems including API Q1 certification, first article inspection, and third-party inspection coordination."},
]

# Domain: Compressors Manufacturing
skills += [
    {"name": "centrifugal-compressor-manufacturing", "description": "Manage centrifugal compressor manufacturing including impeller machining, casing assembly, rotor balancing, and API 617 acceptance testing."},
    {"name": "reciprocating-compressor-manufacturing", "description": "Manage reciprocating compressor manufacturing including cylinder boring, valve assembly, piston rod installation, and performance testing."},
    {"name": "screw-compressor-manufacturing", "description": "Manage screw compressor manufacturing including rotor profile machining, bearing housing assembly, seal installation, and oil system testing."},
    {"name": "compressor-application-engineering", "description": "Provide compressor application engineering support including head calculation, driver sizing, performance curve analysis, and surge control design."},
    {"name": "compressor-package-assembly", "description": "Manage compressor package assembly including skid fabrication, piping, instrumentation installation, and package acceptance testing."},
    {"name": "compressor-aftermarket-services", "description": "Manage compressor aftermarket service programs including overhaul, rerates, spare parts, and field service operations."},
    {"name": "compressor-reliability-programs", "description": "Implement compressor reliability programs including vibration analysis, thermodynamic performance monitoring, and predictive maintenance."},
    {"name": "compressor-control-systems", "description": "Manage compressor control system programs including anti-surge control, capacity control, and compression system automation."},
    {"name": "compressor-raw-materials", "description": "Manage compressor manufacturing materials including alloy steel forgings, specialty castings, and precision machined components."},
    {"name": "compressor-sales-distribution", "description": "Manage compressor sales and distribution including OEM relationships, rental fleet programs, and application-specific solutions."},
]

# Domain: Lifting & Material Handling Equipment
skills += [
    {"name": "overhead-crane-manufacturing", "description": "Manage overhead crane manufacturing including bridge fabrication, end truck assembly, hoist installation, and CMAA load testing."},
    {"name": "hoist-manufacturing-operations", "description": "Manage hoist manufacturing operations including gear assembly, drum winding, brake system testing, and FEM/HMI classification."},
    {"name": "forklift-fleet-management", "description": "Manage industrial forklift fleet programs including utilization tracking, operator certification, battery management, and maintenance scheduling."},
    {"name": "pallet-jack-management", "description": "Manage pallet jack and material handling equipment programs including fleet inventory, maintenance scheduling, and operator training."},
    {"name": "lifting-equipment-inspection", "description": "Manage lifting equipment inspection programs including annual certification, load testing, NDT inspection, and compliance records."},
    {"name": "rigging-hardware-distribution", "description": "Manage rigging hardware distribution programs including wire rope, chain, shackles, and load monitoring equipment."},
    {"name": "dock-equipment-management", "description": "Manage dock equipment programs including dock levelers, dock seals, dock doors, and vehicle restraint systems."},
    {"name": "crane-rail-systems", "description": "Manage crane rail system programs including rail installation, alignment, welding qualification, and periodic inspection."},
    {"name": "aerial-work-platform-management", "description": "Manage aerial work platform fleet programs including ANSI/SIA compliance, operator training, and preventive maintenance scheduling."},
    {"name": "lifting-equipment-sales", "description": "Manage lifting and material handling equipment sales through direct and distribution channels including application engineering."},
]

# Domain: Industrial Sensors Manufacturing
skills += [
    {"name": "pressure-sensor-manufacturing", "description": "Manage pressure sensor manufacturing including sensing element fabrication, calibration, housing assembly, and IP rating testing."},
    {"name": "temperature-sensor-manufacturing", "description": "Manage temperature sensor manufacturing including thermocouple wire production, RTD assembly, calibration, and drift testing."},
    {"name": "flow-sensor-manufacturing", "description": "Manage flow sensor manufacturing including magnetic flowmeter, Coriolis, and vortex flow sensor assembly and calibration."},
    {"name": "level-sensor-manufacturing", "description": "Manage level sensor manufacturing including ultrasonic, radar, and guided wave radar sensor assembly and performance testing."},
    {"name": "gas-detection-sensor-ops", "description": "Manage gas detection sensor programs including electrochemical, infrared, and catalytic bead sensor manufacturing and calibration."},
    {"name": "sensor-raw-material-mgmt", "description": "Manage sensor manufacturing materials including sensing elements, electronics components, and housing materials procurement."},
    {"name": "sensor-calibration-programs", "description": "Manage sensor calibration programs including traceable standards, uncertainty analysis, and ILAC accreditation compliance."},
    {"name": "sensor-application-support", "description": "Provide industrial sensor application support including sensor selection, installation guidance, and troubleshooting."},
    {"name": "sensor-distribution-channel", "description": "Manage sensor distribution channel programs including stocking distributors, rep networks, and OEM account management."},
    {"name": "sensor-product-development", "description": "Develop industrial sensor products including MEMS design, signal conditioning, digital output protocols, and hazardous area certification."},
]

# Domain: Advanced Manufacturing Technologies
skills += [
    {"name": "additive-manufacturing-production", "description": "Manage additive manufacturing production operations including metal powder bed fusion, binder jetting, and FDM production scheduling."},
    {"name": "laser-processing-operations", "description": "Manage laser processing operations including cutting, welding, marking, and surface treatment with process parameter optimization."},
    {"name": "waterjet-cutting-operations", "description": "Manage waterjet cutting operations including abrasive waterjet programming, nozzle maintenance, garnet management, and part quality inspection."},
    {"name": "edm-wire-operations", "description": "Manage EDM wire and sinker operations including electrode design, cutting parameter optimization, and surface finish requirements."},
    {"name": "precision-metrology-advanced", "description": "Manage precision metrology programs including CMM, optical measurement, surface plate work, and NIST-traceable calibration."},
    {"name": "advanced-welding-operations", "description": "Manage advanced welding operations including electron beam, laser beam, friction stir, and plasma welding processes."},
    {"name": "surface-coating-technologies", "description": "Manage surface coating technology programs including thermal spray, PVD, CVD, and electroplating process qualification."},
    {"name": "clean-room-manufacturing", "description": "Manage clean room manufacturing operations including ISO classification compliance, gowning procedures, and particle monitoring programs."},
    {"name": "lean-manufacturing-implementation", "description": "Implement lean manufacturing programs including value stream mapping, kaizen events, 5S deployment, and standard work development."},
    {"name": "digital-twin-manufacturing-ops", "description": "Deploy digital twin manufacturing programs including virtual commissioning, process simulation, and real-time performance monitoring."},
]

# Domain: Specialty Food Ingredients Manufacturing
skills += [
    {"name": "flavor-ingredient-manufacturing", "description": "Manage flavor ingredient manufacturing including natural extraction, reaction flavor development, and FEMA GRAS compliance."},
    {"name": "texture-ingredient-manufacturing", "description": "Manage texture ingredient manufacturing including hydrocolloid production, starch modification, and texture profile analysis."},
    {"name": "preservative-antimicrobial-mfg", "description": "Manage preservative and antimicrobial ingredient manufacturing including fermentation, purification, and antimicrobial efficacy testing."},
    {"name": "enzyme-manufacturing-operations", "description": "Manage food enzyme manufacturing including fermentation, downstream processing, activity standardization, and GRAS notification management."},
    {"name": "emulsifier-manufacturing-ops", "description": "Manage food emulsifier manufacturing including lecithin processing, mono-diglyceride production, and HLB value testing."},
    {"name": "colorant-ingredient-operations", "description": "Manage food colorant ingredient operations including natural pigment extraction, synthetic dye production, and FD&C compliance."},
    {"name": "sweetener-ingredient-manufacturing", "description": "Manage sweetener ingredient manufacturing including high-intensity sweeteners, polyol production, and sweetness profiling."},
    {"name": "acidulant-ingredient-manufacturing", "description": "Manage acidulant ingredient manufacturing including citric acid, lactic acid, and phosphate production with food grade quality control."},
    {"name": "vitamin-mineral-premix", "description": "Manage vitamin and mineral premix operations including blend formulation, potency verification, and stability testing programs."},
    {"name": "food-ingredient-regulatory", "description": "Navigate food ingredient regulatory compliance including GRAS affirmations, food additive petitions, and international approval management."},
]

# Domain: Metal Cans & Containers Manufacturing
skills += [
    {"name": "steel-can-manufacturing", "description": "Manage steel can manufacturing operations including sheet metal forming, seaming, lacquer application, and leak testing."},
    {"name": "aluminum-can-manufacturing", "description": "Manage aluminum beverage can manufacturing including cup drawing, bodymaking, flanging, and necking operations."},
    {"name": "can-end-manufacturing", "description": "Manage can end manufacturing including conversion press operations, compound lining, countersink specification, and drop test compliance."},
    {"name": "can-printing-decoration", "description": "Manage can printing and decoration operations including ink system management, base coat application, and color consistency."},
    {"name": "can-raw-material-sourcing", "description": "Source can manufacturing raw materials including tinplate, electrolytic tin plate, and aluminum sheet with specification management."},
    {"name": "can-filling-seaming-ops", "description": "Manage can filling and seaming operations including fill level control, seam integrity testing, and nitrogen purge programs."},
    {"name": "can-quality-assurance", "description": "Execute can quality assurance programs including seam inspection, leak testing, wall thickness measurement, and drop test compliance."},
    {"name": "can-sustainability-programs", "description": "Manage can sustainability programs including recycled content targets, carbon footprint reduction, and end-of-life recyclability."},
    {"name": "aerosol-can-manufacturing", "description": "Manage aerosol can manufacturing including drawn and welded production, dome formation, pressure testing, and valve installation."},
    {"name": "can-customer-technical-service", "description": "Provide can customer technical service including filling line compatibility, package design review, and performance testing."},
]

# Domain: Corrugated Containers Manufacturing
skills += [
    {"name": "corrugator-operations", "description": "Manage corrugator production including single facer, double backer, slitter scorer, and cutoff operations with caliper control."},
    {"name": "box-plant-manufacturing", "description": "Manage corrugated box plant operations including flexo folder gluer, rotary die cutter, and gluing machine operations."},
    {"name": "corrugated-design-engineering", "description": "Design corrugated packaging solutions including ECT testing, compression strength modeling, and custom structure development."},
    {"name": "corrugated-raw-material-mgmt", "description": "Manage corrugated raw material procurement including linerboard, medium, and recycled fiber sourcing with specification management."},
    {"name": "corrugated-printing-operations", "description": "Manage corrugated printing operations including flexographic printing quality, ink management, and photo-quality graphics reproduction."},
    {"name": "corrugated-customer-service", "description": "Manage corrugated packaging customer service including order management, specification review, sample production, and delivery coordination."},
    {"name": "corrugated-quality-testing", "description": "Execute corrugated quality testing programs including flat crush, edge crush, burst strength, and moisture content testing."},
    {"name": "corrugated-sustainability", "description": "Lead corrugated packaging sustainability programs including recycled content certification, carbon footprint reduction, and SFI/FSC compliance."},
    {"name": "corrugated-sales-management", "description": "Manage corrugated packaging sales programs including account development, price management, and technical value selling."},
    {"name": "corrugated-production-scheduling", "description": "Optimize corrugated production scheduling including order batching, specification planning, and downtime minimization."},
]

# Domain: Electronic Components Distribution
skills += [
    {"name": "component-distribution-ops", "description": "Manage electronic component distribution operations including franchised line management, inventory planning, and order fulfillment."},
    {"name": "component-counterfeit-prevention", "description": "Manage counterfeit component prevention programs including supplier qualification, test and inspection protocols, and AS6081 compliance."},
    {"name": "component-supply-chain-risk", "description": "Manage electronic component supply chain risk programs including shortage monitoring, lifecycle management, and last-time-buy coordination."},
    {"name": "component-lifecycle-management", "description": "Manage component lifecycle programs including product change notifications, last-time-buy decisions, and obsolescence mitigation."},
    {"name": "component-technical-sales", "description": "Manage component technical sales programs including design-in support, cross-reference analysis, and FAE technical assistance."},
    {"name": "component-warehouse-operations", "description": "Manage component distribution warehouse operations including pick-pack, kitting, reel splicing, and moisture sensitive device handling."},
    {"name": "component-pricing-contracts", "description": "Manage component distribution pricing and contracts including spot buys, long-term agreements, and consignment inventory programs."},
    {"name": "component-demand-planning", "description": "Manage component demand planning using consumption analytics, design-in pipeline tracking, and lead time monitoring."},
    {"name": "component-customer-portal", "description": "Manage component customer portal programs including order management, inventory visibility, technical documentation, and account analytics."},
    {"name": "franchise-line-management", "description": "Manage franchised line relationships with component manufacturers including territory management, stock balancing, and marketing programs."},
]

# Domain: Switchgear & Circuit Breaker Manufacturing
skills += [
    {"name": "low-voltage-switchgear-mfg", "description": "Manage low-voltage switchgear manufacturing including bus bar fabrication, circuit breaker mounting, wiring, and dielectric testing."},
    {"name": "medium-voltage-switchgear-mfg", "description": "Manage medium-voltage switchgear manufacturing including vacuum interrupter assembly, draw-out mechanism, and withstand testing."},
    {"name": "circuit-breaker-manufacturing", "description": "Manage circuit breaker manufacturing including molded case, insulated case, and air circuit breaker assembly and calibration."},
    {"name": "switchgear-engineering-design", "description": "Provide switchgear engineering design support including short circuit calculation, coordination study, and arc flash analysis."},
    {"name": "switchgear-testing-programs", "description": "Execute switchgear testing programs including type testing, routine testing per IEC 62271, and commissioning testing."},
    {"name": "switchgear-project-management", "description": "Manage switchgear project execution including utility coordination, engineering review, factory acceptance testing, and installation support."},
    {"name": "switchgear-service-operations", "description": "Manage switchgear service operations including preventive maintenance, CB testing, insulation resistance, and arc flash assessment."},
    {"name": "switchgear-raw-materials", "description": "Manage switchgear manufacturing materials including copper bus, insulating materials, relay components, and enclosure fabrication."},
    {"name": "intelligent-electronic-devices", "description": "Manage intelligent electronic device programs including relay coordination, communication protocols, and IEC 61850 implementation."},
    {"name": "switchgear-distribution-sales", "description": "Manage switchgear distribution and sales programs including electrical distributor channels, specifier programs, and project quotation."},
]

# Domain: Wiring & Cables Manufacturing
skills += [
    {"name": "wire-drawing-operations", "description": "Manage wire drawing operations including die management, lubrication systems, annealing, and diameter tolerance control."},
    {"name": "cable-extrusion-operations", "description": "Manage cable extrusion operations including insulation extrusion, jacket application, and conductor configuration management."},
    {"name": "power-cable-manufacturing", "description": "Manage power cable manufacturing including stranding, insulation, shielding, armoring, and electrical testing programs."},
    {"name": "data-cable-manufacturing", "description": "Manage data cable manufacturing including twisted pair, coaxial, and fiber optic cable production with transmission performance testing."},
    {"name": "cable-testing-qualification", "description": "Execute cable testing programs including conductor resistance, insulation resistance, high pot, and flame propagation testing."},
    {"name": "cable-raw-material-sourcing", "description": "Source cable manufacturing raw materials including copper rod, aluminum rod, insulation compounds, and armor materials."},
    {"name": "cable-application-engineering", "description": "Provide cable application engineering support including ampacity calculation, voltage drop analysis, and installation specification."},
    {"name": "cable-distribution-channel", "description": "Manage cable distribution channel programs including electrical distribution, utility programs, and project specification channels."},
    {"name": "cable-quality-management", "description": "Implement cable quality management programs including UL listing compliance, Mil-Spec compliance, and customer witness testing."},
    {"name": "specialty-cable-development", "description": "Develop specialty cable products including high-flex, high-temperature, and ruggedized designs for demanding applications."},
]

# Domain: HVAC Equipment Manufacturing (expanded)
skills += [
    {"name": "chiller-manufacturing-ops", "description": "Manage chiller manufacturing operations including centrifugal and screw compressor assembly, refrigerant charging, and AHRI certification."},
    {"name": "air-handling-unit-manufacturing", "description": "Manage air handling unit manufacturing including coil fabrication, fan assembly, filtration section, and AMCA performance testing."},
    {"name": "variable-refrigerant-flow-mfg", "description": "Manage variable refrigerant flow system manufacturing including multi-split design, branch controller assembly, and AHRI 1230 testing."},
    {"name": "commercial-rooftop-unit-mfg", "description": "Manage commercial rooftop unit manufacturing including DX coil assembly, economizer integration, and ARI 360 rating compliance."},
    {"name": "hydronic-equipment-manufacturing", "description": "Manage hydronic HVAC equipment manufacturing including fan coil units, heat pump water heaters, and hydronic cassette production."},
    {"name": "ventilation-equipment-mfg", "description": "Manage ventilation equipment manufacturing including energy recovery ventilators, demand control ventilation, and ASHRAE 62.1 compliance."},
    {"name": "hvac-controls-firmware", "description": "Manage HVAC controls firmware development including BACnet, Modbus, and KNX protocol implementation with demand response capability."},
    {"name": "hvac-refrigerant-transition", "description": "Manage HVAC refrigerant transition programs including A2L refrigerant qualification, regulatory timeline tracking, and product changeover."},
    {"name": "hvac-manufacturing-quality-systems", "description": "Implement HVAC manufacturing quality systems including ARI certification maintenance, ISO 9001 compliance, and warranty analytics."},
    {"name": "hvac-product-launches", "description": "Manage HVAC product launch programs including regulatory compliance, channel training, installation documentation, and service support."},
]

# Domain: Refrigeration Equipment Manufacturing
skills += [
    {"name": "commercial-refrigeration-mfg", "description": "Manage commercial refrigeration manufacturing including reach-in and walk-in cooler production, refrigerant charging, and NSF compliance."},
    {"name": "display-case-manufacturing", "description": "Manage refrigerated display case manufacturing including coil assembly, glass door integration, lighting, and energy certification."},
    {"name": "industrial-refrigeration-systems", "description": "Manage industrial refrigeration system manufacturing including ammonia system components, pressure vessel fabrication, and IIAR compliance."},
    {"name": "refrigeration-compressor-ops", "description": "Manage refrigeration compressor programs including reciprocating, scroll, and rotary compressor manufacturing and AHRI rating."},
    {"name": "refrigeration-controls-development", "description": "Develop refrigeration controls solutions including case controller firmware, store controller integration, and energy management systems."},
    {"name": "cold-storage-equipment-mfg", "description": "Manage cold storage equipment manufacturing including blast freezers, plate freezers, and cold storage room prefabricated panels."},
    {"name": "refrigeration-aftermarket-parts", "description": "Manage refrigeration aftermarket parts programs including genuine parts, OEM cross-reference, and refrigerant management programs."},
    {"name": "refrigeration-testing-validation", "description": "Execute refrigeration equipment testing programs including AHRI certification, pulldown performance, and energy consumption verification."},
    {"name": "refrigeration-tech-training", "description": "Manage refrigeration technician training programs including EPA 608 certification prep, system troubleshooting, and product-specific training."},
    {"name": "refrigeration-sustainability", "description": "Lead refrigeration sustainability programs including low-GWP refrigerant adoption, energy efficiency targets, and natural refrigerant transition."},
]

# Domain: Diagnostic Imaging Equipment Manufacturing
skills += [
    {"name": "x-ray-system-manufacturing", "description": "Manage X-ray system manufacturing including X-ray tube assembly, generator calibration, detector integration, and FDA 510k compliance."},
    {"name": "ultrasound-system-manufacturing", "description": "Manage ultrasound system manufacturing including transducer assembly, beamformer integration, image processing, and IEC 60601 compliance."},
    {"name": "mri-system-manufacturing", "description": "Manage MRI system manufacturing including magnet assembly, gradient coil installation, RF coil production, and field uniformity testing."},
    {"name": "ct-scanner-manufacturing", "description": "Manage CT scanner manufacturing including gantry assembly, detector module integration, slip ring, and image quality calibration."},
    {"name": "nuclear-medicine-equipment-mfg", "description": "Manage nuclear medicine equipment manufacturing including gamma camera assembly, SPECT/CT integration, and calibration source management."},
    {"name": "diagnostic-imaging-regulatory", "description": "Navigate diagnostic imaging regulatory compliance including FDA 510k/PMA, IEC 60601, and international device registration."},
    {"name": "imaging-software-development", "description": "Manage imaging software development including DICOM compliance, image reconstruction algorithms, and AI-assisted diagnostic tools."},
    {"name": "imaging-service-operations", "description": "Manage diagnostic imaging equipment service operations including preventive maintenance, applications training, and remote diagnostics."},
    {"name": "imaging-equipment-distribution", "description": "Manage imaging equipment distribution programs including dealer networks, GPO contracts, and refurbished equipment programs."},
    {"name": "imaging-quality-systems", "description": "Implement imaging equipment quality management systems including ISO 13485 compliance, design controls, and risk management."},
]

# Domain: EV Charging & Energy Storage Systems
skills += [
    {"name": "ev-charging-hardware-mfg", "description": "Manage EV charging hardware manufacturing including Level 2 EVSE, DC fast charger, and wireless charging system production."},
    {"name": "ev-charging-network-operations", "description": "Manage EV charging network operations including charger monitoring, uptime management, billing systems, and utilization analytics."},
    {"name": "battery-energy-storage-mfg", "description": "Manage battery energy storage system manufacturing including cell integration, BMS assembly, thermal management, and UL 9540 compliance."},
    {"name": "grid-scale-battery-operations", "description": "Manage grid-scale battery operations including state of charge management, frequency regulation, and demand charge reduction."},
    {"name": "ev-battery-second-life", "description": "Develop EV battery second-life programs including capacity grading, system integration for stationary storage, and safety certification."},
    {"name": "energy-storage-commissioning", "description": "Manage energy storage system commissioning including factory acceptance testing, site acceptance, safety validation, and PCS testing."},
    {"name": "charging-infrastructure-planning", "description": "Plan EV charging infrastructure including site assessment, utility interconnection, grid capacity analysis, and permit coordination."},
    {"name": "virtual-power-plant-operations", "description": "Manage virtual power plant operations including distributed energy resource aggregation, dispatch optimization, and demand response."},
    {"name": "energy-storage-safety-program", "description": "Manage energy storage safety programs including thermal runaway prevention, fire suppression integration, and first responder training."},
    {"name": "ev-fleet-charging-management", "description": "Manage EV fleet charging programs including depot charging design, smart charging software, and utility rate optimization."},
]

# Domain: Clean Technology Manufacturing
skills += [
    {"name": "solar-panel-manufacturing", "description": "Manage solar panel manufacturing including cell stringing, lamination, frame assembly, and IEC 61215 qualification testing."},
    {"name": "wind-turbine-component-mfg", "description": "Manage wind turbine component manufacturing including blade production, nacelle assembly, and hub machining with quality certification."},
    {"name": "fuel-cell-manufacturing", "description": "Manage fuel cell manufacturing including MEA production, bipolar plate fabrication, stack assembly, and performance testing."},
    {"name": "electrolyzer-manufacturing", "description": "Manage electrolyzer manufacturing including PEM and alkaline stack assembly, catalyst management, and hydrogen purity testing."},
    {"name": "heat-pump-manufacturing", "description": "Manage heat pump manufacturing including ground source, air source, and water source heat pump assembly and performance testing."},
    {"name": "green-hydrogen-equipment-mfg", "description": "Manage green hydrogen equipment manufacturing including electrolyzers, compression systems, and storage vessel production."},
    {"name": "energy-efficiency-equipment-mfg", "description": "Manage energy efficiency equipment manufacturing including LED drivers, variable speed drives, and power quality devices."},
    {"name": "cleantech-quality-systems", "description": "Implement clean technology quality management systems including IEC standards compliance, reliability testing, and field performance tracking."},
    {"name": "cleantech-supply-chain", "description": "Manage clean technology supply chains including critical mineral sourcing, domestic content compliance, and supplier qualification."},
    {"name": "cleantech-product-certification", "description": "Navigate clean technology product certifications including UL, CE marking, IEC testing, and utility interconnection standards."},
]

# Domain: Biotechnology Equipment Manufacturing
skills += [
    {"name": "bioreactor-manufacturing-ops", "description": "Manage bioreactor manufacturing including vessel fabrication, agitation system assembly, sparger installation, and clean-in-place qualification."},
    {"name": "chromatography-equipment-mfg", "description": "Manage chromatography equipment manufacturing including column assembly, packing operations, flow distribution testing, and USP compliance."},
    {"name": "bioprocess-filter-manufacturing", "description": "Manage bioprocess filter manufacturing including membrane manufacturing, capsule assembly, integrity testing, and sterility validation."},
    {"name": "single-use-bioprocess-mfg", "description": "Manage single-use bioprocess equipment manufacturing including bag assembly, tubing manifold fabrication, and extractables testing."},
    {"name": "cell-culture-equipment-mfg", "description": "Manage cell culture equipment manufacturing including incubators, biosafety cabinets, cryogenic storage, and IQ/OQ documentation."},
    {"name": "bioprocess-instrumentation-mfg", "description": "Manage bioprocess instrumentation manufacturing including pH, DO, conductivity, and pressure sensors for GMP environments."},
    {"name": "bioprocess-equipment-service", "description": "Manage bioprocess equipment service operations including calibration, preventive maintenance, qualification support, and spare parts."},
    {"name": "bioprocess-equipment-validation", "description": "Execute bioprocess equipment validation programs including IQ/OQ/PQ protocols, clean steam testing, and regulatory submission support."},
    {"name": "bioprocess-equipment-sales", "description": "Manage bioprocess equipment sales programs through direct and distribution channels including CRO and CMO account development."},
    {"name": "bioprocess-equipment-rd", "description": "Manage bioprocess equipment research and development including continuous manufacturing platforms, digital twin integration, and PAT technology."},
]

# Domain: Water Treatment Equipment Manufacturing (expanded)
skills += [
    {"name": "reverse-osmosis-system-mfg", "description": "Manage reverse osmosis system manufacturing including pressure vessel assembly, element loading, pump skid, and system commissioning."},
    {"name": "uv-disinfection-system-mfg", "description": "Manage UV disinfection system manufacturing including lamp module assembly, ballast integration, sensor mounting, and dose validation."},
    {"name": "electrocoagulation-system-mfg", "description": "Manage electrocoagulation system manufacturing including electrode array assembly, power supply integration, and contaminant removal testing."},
    {"name": "water-softener-manufacturing", "description": "Manage water softener manufacturing including tank assembly, valve configuration, control head programming, and salt bridge prevention."},
    {"name": "deionization-system-manufacturing", "description": "Manage deionization system manufacturing including mixed bed resin loading, conductivity monitoring, and regeneration system assembly."},
    {"name": "industrial-wastewater-systems", "description": "Design and manage industrial wastewater treatment system manufacturing including DAF systems, biological treatment, and clarifier fabrication."},
    {"name": "water-treatment-skid-assembly", "description": "Manage water treatment skid assembly operations including package system integration, piping, instrumentation, and factory acceptance testing."},
    {"name": "desalination-equipment-mfg", "description": "Manage desalination equipment manufacturing including SWRO high-pressure pump assembly, energy recovery device production, and membrane housing."},
    {"name": "water-treatment-controls-mfg", "description": "Manage water treatment controls manufacturing including PLC panels, SCADA integration, remote monitoring systems, and alarm management."},
    {"name": "water-treatment-equipment-service", "description": "Manage water treatment equipment service operations including membrane replacement, pump repair, chemical dosing calibration, and system optimization."},
]

# Domain: Aerospace Support Equipment Manufacturing
skills += [
    {"name": "ground-support-equipment-mfg", "description": "Manage ground support equipment manufacturing including tow tractors, cargo loaders, aircraft jacks, and power supply units."},
    {"name": "aircraft-tooling-manufacturing", "description": "Manage aircraft tooling manufacturing including jig and fixture fabrication, drill templates, assembly tools, and OEM qualification."},
    {"name": "aerospace-test-equipment-mfg", "description": "Manage aerospace test equipment manufacturing including avionics test sets, engine test stands, and structural test equipment."},
    {"name": "aircraft-maintenance-tooling", "description": "Manage aircraft maintenance tooling programs including calibrated tool tracking, special tool kits, and tooling loan programs."},
    {"name": "aircraft-ground-power-units", "description": "Manage aircraft ground power unit manufacturing including diesel GPU, eGPU assembly, aviation standard compliance, and rental fleet."},
    {"name": "aerospace-tooling-quality", "description": "Implement aerospace tooling quality programs including AS9100 compliance, first article inspection, and material traceability."},
    {"name": "aircraft-hangar-equipment", "description": "Manage aircraft hangar equipment programs including aircraft shelters, hangar doors, hydraulic lifts, and maintenance stands."},
    {"name": "aerospace-maintenance-equipment", "description": "Manage aerospace maintenance equipment programs including docking systems, engine stands, and avionics bench test equipment."},
    {"name": "ground-handling-equipment-ops", "description": "Manage airport ground handling equipment operations including fleet management, preventive maintenance, and IATA ground operations compliance."},
    {"name": "aerospace-equipment-distribution", "description": "Manage aerospace support equipment distribution programs including dealer network, rental fleet, and MRO customer accounts."},
]

# Domain: Marine Equipment Manufacturing
skills += [
    {"name": "marine-engine-manufacturing", "description": "Manage marine engine manufacturing including inboard, outboard, and stern drive assembly, performance dyno testing, and EPA compliance."},
    {"name": "marine-propulsion-systems", "description": "Manage marine propulsion system manufacturing including propellers, thrusters, gearboxes, and pod drives with classification approval."},
    {"name": "marine-deck-equipment-mfg", "description": "Manage marine deck equipment manufacturing including winches, capstans, anchor windlasses, and mooring equipment."},
    {"name": "marine-navigation-equipment", "description": "Manage marine navigation equipment manufacturing including radar systems, AIS transponders, chart plotters, and VHF radios."},
    {"name": "marine-safety-equipment-mfg", "description": "Manage marine safety equipment manufacturing including life rafts, EPIRBs, immersion suits, and fire suppression systems."},
    {"name": "commercial-fishing-equipment-mfg", "description": "Manage commercial fishing equipment manufacturing including winches, net drums, fish handling systems, and hydraulic power packs."},
    {"name": "marine-hvac-refrigeration-mfg", "description": "Manage marine HVAC and refrigeration equipment manufacturing including chilled water systems, cabin units, and fish hold cooling."},
    {"name": "marine-equipment-classification", "description": "Navigate marine equipment classification approval programs including DNV, ABS, LR, and BV type approval processes."},
    {"name": "marine-equipment-service-network", "description": "Manage marine equipment service network including dealer service training, spare parts supply, and warranty management."},
    {"name": "pleasure-craft-equipment-mfg", "description": "Manage pleasure craft equipment manufacturing including outboard motors, marine electronics, and boat accessories with NMMA compliance."},
]

# Domain: Construction Equipment Components
skills += [
    {"name": "hydraulic-excavator-components", "description": "Manage excavator component manufacturing including boom cylinders, bucket pins, track frame fabrication, and bucket tooth systems."},
    {"name": "undercarriage-component-mfg", "description": "Manage undercarriage component manufacturing including track chains, sprockets, idlers, and track pads with wear analysis programs."},
    {"name": "construction-engine-integration", "description": "Manage construction equipment engine integration programs including emissions compliance, engine monitoring, and Tier 4 Final certification."},
    {"name": "construction-attachment-mfg", "description": "Manage construction equipment attachment manufacturing including buckets, breakers, augers, and quick-couplers with OEM compatibility."},
    {"name": "cab-operator-environment-mfg", "description": "Manage operator cab manufacturing including ROPS/FOPS certification, climate control integration, and ergonomics compliance."},
    {"name": "construction-electrical-systems", "description": "Manage construction equipment electrical system manufacturing including wiring harnesses, controller integration, and telematics modules."},
    {"name": "construction-component-quality", "description": "Implement construction equipment component quality programs including weld inspection, dimensional compliance, and field validation."},
    {"name": "oem-construction-partnerships", "description": "Manage OEM construction equipment partnerships including component supply agreements, development programs, and capacity planning."},
    {"name": "aftermarket-construction-parts", "description": "Manage aftermarket construction equipment parts programs including non-OEM supply, field service parts, and warranty administration."},
    {"name": "construction-equipment-telematics", "description": "Manage construction equipment telematics programs including fleet utilization data, maintenance alerts, and fuel consumption analytics."},
]

# Domain: Optical Instruments Manufacturing
skills += [
    {"name": "microscope-manufacturing-ops", "description": "Manage microscope manufacturing including optical assembly, illumination systems, stage mechanisms, and resolution testing."},
    {"name": "telescope-manufacturing-ops", "description": "Manage telescope manufacturing including mirror fabrication, optical tube assembly, mount systems, and optical performance testing."},
    {"name": "survey-instrument-manufacturing", "description": "Manage survey instrument manufacturing including total station assembly, GPS module integration, and angular accuracy calibration."},
    {"name": "optometry-equipment-manufacturing", "description": "Manage optometry equipment manufacturing including slit lamps, phoropters, keratometers, and refractometers with FDA compliance."},
    {"name": "industrial-inspection-optics", "description": "Manage industrial inspection optic manufacturing including borescopes, endoscopes, and video borescopes for maintenance applications."},
    {"name": "optical-coating-operations", "description": "Manage optical coating operations including anti-reflection coatings, hard coatings, and specialty filter coating processes."},
    {"name": "lens-grinding-polishing", "description": "Manage lens grinding and polishing operations including CNC surfacing, hand polishing, and interferometric quality inspection."},
    {"name": "night-vision-optics-manufacturing", "description": "Manage night vision optics manufacturing including image intensifier tubes, IR lens assembly, and mil-spec compliance programs."},
    {"name": "optics-raw-material-sourcing", "description": "Source optical raw materials including optical glass, crystal substrates, coating materials, and precision optical components."},
    {"name": "optics-test-metrology-systems", "description": "Manage optical testing and metrology systems including interferometers, MTF testing, and spectrophotometric verification."},
]

# Domain: Structural Steel Fabrication
skills += [
    {"name": "structural-steel-fabrication", "description": "Manage structural steel fabrication operations including plasma cutting, drilling, welding, and AISC quality certification."},
    {"name": "steel-detailing-drafting", "description": "Manage structural steel detailing programs including 3D modeling, connection design, shop drawings, and BIM coordination."},
    {"name": "structural-welding-quality", "description": "Implement structural welding quality programs including AWS D1.1 compliance, welder qualification, and NDE inspection management."},
    {"name": "steel-surface-treatment", "description": "Manage structural steel surface treatment programs including blast cleaning, prime painting, and galvanizing specifications."},
    {"name": "steel-erection-management", "description": "Manage structural steel erection operations including crane coordination, bolt-up procedures, and OSHA fall protection compliance."},
    {"name": "steel-fabrication-scheduling", "description": "Manage structural steel fabrication scheduling including mill order management, fabrication sequencing, and delivery coordination."},
    {"name": "specialty-steel-fabrication", "description": "Manage specialty steel fabrication programs including stainless steel, weathering steel, and high-strength steel applications."},
    {"name": "steel-procurement-management", "description": "Manage structural steel procurement including mill buying, service center relationships, and steel price risk management."},
    {"name": "steel-quality-certification", "description": "Manage structural steel quality certification programs including material test reports, AISC certification, and customer audit support."},
    {"name": "seismic-steel-fabrication", "description": "Manage seismic structural steel fabrication programs including special moment frames, demand critical welds, and AWS D1.8 compliance."},
]

# Domain: Plastics Recycling Technology
skills += [
    {"name": "mechanical-recycling-operations", "description": "Manage mechanical plastics recycling operations including sorting, washing, granulation, and pelletizing for post-consumer resin production."},
    {"name": "chemical-recycling-technology", "description": "Manage chemical plastics recycling technology including pyrolysis, gasification, and depolymerization process operations and product quality."},
    {"name": "recycled-content-certification", "description": "Manage recycled content certification programs including GRS certification, PCR content tracking, and mass balance accounting."},
    {"name": "plastic-waste-collection-systems", "description": "Design and manage plastic waste collection systems including curbside programs, deposit schemes, and industrial collection networks."},
    {"name": "plastics-sorting-technology", "description": "Manage plastics sorting technology programs including near-infrared sorting, AI-assisted identification, and contamination reduction."},
    {"name": "recycled-resin-quality-control", "description": "Execute recycled resin quality control programs including melt flow, contamination testing, color consistency, and application suitability."},
    {"name": "extended-producer-responsibility", "description": "Manage extended producer responsibility compliance programs including EPR registration, fee calculation, reporting, and take-back coordination."},
    {"name": "plastic-credit-platforms", "description": "Manage plastic credit programs including collection verification, credit issuance, registry management, and corporate offset programs."},
    {"name": "recycling-partnership-development", "description": "Develop recycling partnership programs including brand owner commitments, retailer programs, and municipal collaboration agreements."},
    {"name": "recycling-infrastructure-investment", "description": "Manage recycling infrastructure investment programs including MRF upgrades, collection expansion, and technology deployment."},
]

# Domain: Textile Recycling Technology
skills += [
    {"name": "textile-mechanical-recycling", "description": "Manage textile mechanical recycling operations including fiber opening, blending, nonwoven production, and quality testing."},
    {"name": "textile-chemical-recycling-ops", "description": "Manage textile chemical recycling operations including polyester glycolysis, cotton pulp production, and fiber certification."},
    {"name": "textile-collection-programs", "description": "Develop textile collection programs including retail take-back, charitable sorting partnerships, and industrial collection networks."},
    {"name": "textile-sorting-grading", "description": "Manage textile sorting and grading operations including automated sorting, manual grading, and fiber content identification."},
    {"name": "recycled-fiber-certification", "description": "Manage recycled fiber certification programs including Global Recycled Standard, RCS certification, and chain-of-custody audits."},
    {"name": "textile-circular-design", "description": "Develop textile circular design programs including recyclability assessment, mono-material design, and end-of-life planning."},
    {"name": "textile-recycling-market-development", "description": "Develop textile recycled fiber markets including brand partnerships, specification development, and supply chain integration."},
    {"name": "textile-waste-logistics", "description": "Manage textile waste logistics programs including collection container networks, transportation optimization, and sorting facility operations."},
    {"name": "fiber-to-fiber-recycling", "description": "Manage fiber-to-fiber recycling technology programs including closed-loop cotton, polyester depolymerization, and blend separation."},
    {"name": "textile-recycling-policy-compliance", "description": "Navigate textile recycling policy compliance including EU textile EPR regulations, state-level requirements, and reporting obligations."},
]

# Domain: Adhesives Application Equipment
skills += [
    {"name": "hot-melt-application-systems", "description": "Manage hot melt adhesive application system programs including melt tank selection, applicator gun design, and temperature control."},
    {"name": "pressure-sensitive-applicators", "description": "Manage pressure sensitive adhesive application equipment including roll coaters, gravure systems, and slot die technology."},
    {"name": "spray-adhesive-systems", "description": "Manage spray adhesive application systems including airless spray, electrostatic spray, and swirl spray equipment programs."},
    {"name": "robotic-adhesive-dispensing", "description": "Manage robotic adhesive dispensing programs including bead application, seam sealing, and form-in-place gasket systems."},
    {"name": "adhesive-dispensing-quality", "description": "Implement adhesive dispensing quality programs including bead width monitoring, coverage verification, and bond strength testing."},
    {"name": "adhesive-equipment-maintenance", "description": "Manage adhesive dispensing equipment maintenance programs including nozzle cleaning, pump rebuild, and filter change schedules."},
    {"name": "assembly-adhesive-automation", "description": "Automate assembly adhesive operations including dispensing path programming, cure monitoring, and defect detection integration."},
    {"name": "sealing-dispensing-equipment", "description": "Manage sealant dispensing equipment programs including cartridge guns, bulk dispensing systems, and two-component mixing systems."},
    {"name": "adhesive-equipment-sales", "description": "Manage adhesive application equipment sales programs through distributor channels, OEM programs, and direct end-user accounts."},
    {"name": "adhesive-process-optimization", "description": "Optimize adhesive application processes including open time management, fixture time reduction, and cure cycle optimization."},
]

# Domain: Industrial Cleaning Services Technology
skills += [
    {"name": "industrial-parts-washing-ops", "description": "Manage industrial parts washing operations including aqueous cleaning systems, solvent degreasers, and ultrasonic cleaning programs."},
    {"name": "tank-cleaning-operations", "description": "Manage industrial tank cleaning operations including confined space procedures, high-pressure water blasting, and waste management."},
    {"name": "industrial-vacuum-services", "description": "Manage industrial vacuum services operations including wet-dry vac systems, HEPA filtration, and hazardous material collection."},
    {"name": "pressure-washing-industrial", "description": "Manage industrial pressure washing operations including ultra-high pressure applications, surface preparation, and surface cleaning verification."},
    {"name": "dry-ice-blasting-operations", "description": "Manage dry ice blasting operations including equipment rental programs, food-grade cleaning applications, and environmental compliance."},
    {"name": "chemical-cleaning-services", "description": "Manage chemical cleaning service operations including CIP systems, chemical descaling, passivation, and system restoration."},
    {"name": "industrial-cleaning-scheduling", "description": "Manage industrial cleaning service scheduling including planned maintenance shutdowns, turnaround coordination, and crew management."},
    {"name": "cleaning-service-safety", "description": "Manage industrial cleaning safety programs including confined space rescue, chemical exposure protection, and OSHA compliance."},
    {"name": "cleaning-service-contracts", "description": "Manage industrial cleaning service contracts including scope of work development, pricing, performance metrics, and contract renewal."},
    {"name": "cleanroom-cleaning-services", "description": "Manage cleanroom cleaning services including ISO classification compliance, cleaning protocols, contamination monitoring, and validation."},
]

# Domain: Scientific Research Equipment Manufacturing
skills += [
    {"name": "scanning-electron-microscope-mfg", "description": "Manage SEM manufacturing including electron gun assembly, detector integration, vacuum system, and resolution performance testing."},
    {"name": "spectrometer-manufacturing-ops", "description": "Manage spectrometer manufacturing including optical bench assembly, detector integration, wavelength calibration, and stray light testing."},
    {"name": "nmr-instrument-manufacturing", "description": "Manage NMR instrument manufacturing including superconducting magnet assembly, gradient coil, and RF system integration."},
    {"name": "xrd-equipment-manufacturing", "description": "Manage X-ray diffractometer manufacturing including goniometer assembly, detector mounting, and Bragg angle calibration."},
    {"name": "thermal-analysis-instrument-mfg", "description": "Manage thermal analysis instrument manufacturing including DSC, TGA, and DMA assembly with temperature accuracy verification."},
    {"name": "particle-analysis-instrument-mfg", "description": "Manage particle analysis instrument manufacturing including laser diffraction, dynamic light scattering, and zeta potential measurement."},
    {"name": "surface-analysis-equipment-mfg", "description": "Manage surface analysis equipment manufacturing including XPS, AES, and SIMS systems with ultrahigh vacuum technology."},
    {"name": "scientific-instrument-service", "description": "Manage scientific instrument service operations including preventive maintenance, calibration, application support, and upgrade programs."},
    {"name": "scientific-instrument-sales", "description": "Manage scientific instrument sales through direct and distribution channels including key account management and demo programs."},
    {"name": "scientific-instrument-applications", "description": "Provide scientific instrument application support including method development, data interpretation, and workshop programs."},
]

# Domain: Specialty Packaging Materials
skills += [
    {"name": "multilayer-film-manufacturing", "description": "Manage multilayer film manufacturing including blown film extrusion, layer ratio optimization, and barrier property testing."},
    {"name": "foil-laminate-manufacturing", "description": "Manage foil laminate manufacturing including aluminum foil lamination, adhesive application, and barrier performance testing."},
    {"name": "metallized-film-production", "description": "Manage metallized film production including vacuum metallization, optical density control, and barrier property verification."},
    {"name": "retort-pouch-manufacturing", "description": "Manage retort pouch manufacturing including foil laminate construction, heat sealing, retort testing, and FDA food contact compliance."},
    {"name": "active-packaging-development", "description": "Develop active packaging products including oxygen scavengers, moisture absorbers, and antimicrobial packaging technology."},
    {"name": "biodegradable-packaging-ops", "description": "Manage biodegradable packaging operations including PLA, PHA, and starch-based material production with compostability certification."},
    {"name": "packaging-ink-manufacturing", "description": "Manage packaging ink manufacturing including formulation development, viscosity control, adhesion testing, and food contact compliance."},
    {"name": "specialty-coating-packaging-mfg", "description": "Manage specialty packaging coating manufacturing including heat seal coatings, release coatings, and functional barrier coatings."},
    {"name": "tamper-evident-packaging-mfg", "description": "Manage tamper-evident packaging manufacturing including shrink band application, induction sealing, and breakaway closure production."},
    {"name": "packaging-closures-manufacturing", "description": "Manage packaging closure manufacturing including bottle caps, fitments, dispensing closures, and child-resistant closure compliance."},
]

# Domain: Energy Equipment Services
skills += [
    {"name": "turbine-overhaul-services", "description": "Manage turbine overhaul service operations including disassembly, component inspection, repair, replacement, and performance testing."},
    {"name": "generator-rewind-services", "description": "Manage generator rewind service operations including winding removal, insulation application, impregnation, and hipot testing."},
    {"name": "energy-equipment-field-service", "description": "Manage energy equipment field service operations including startup support, troubleshooting, outage support, and performance audits."},
    {"name": "energy-equipment-parts-supply", "description": "Manage energy equipment spare parts supply programs including OEM and non-OEM parts, emergency supply, and consignment inventory."},
    {"name": "energy-equipment-rental-fleet", "description": "Manage energy equipment rental fleet programs including generator sets, load banks, transformers, and emergency power systems."},
    {"name": "boiler-inspection-services", "description": "Manage boiler inspection service operations including NBIC compliance, NDE testing, tube inspection, and regulatory reporting."},
    {"name": "heat-recovery-optimization", "description": "Provide heat recovery optimization services including thermal audit, steam trap surveys, condensate return, and waste heat utilization."},
    {"name": "power-plant-performance-testing", "description": "Manage power plant performance testing programs including ASME PTC testing, acceptance testing, and efficiency guarantee verification."},
    {"name": "emission-control-services", "description": "Manage emission control equipment services including SCR catalyst replacement, CEMS calibration, and compliance testing."},
    {"name": "energy-equipment-digital-services", "description": "Manage energy equipment digital service programs including remote monitoring, predictive analytics, and digital twin services."},
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
