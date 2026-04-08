import os

base = r"c:\Users\mirza\MAARS-Command\.claude\skills"

# Domain: Metal Processing Technology
skills = [
    {"name": "cotton-processing-technology", "description": "Manage cotton ginning and fiber processing operations including bale management, fiber testing, contamination control, and classing systems."},
    {"name": "carbon-black-manufacturing", "description": "Operate carbon black production facilities including reactor management, feedstock optimization, surface area control, and customer technical service."},
    {"name": "titanium-metal-processing", "description": "Manage titanium processing operations including melting, forging, rolling, machining, and aerospace qualification programs."},
    {"name": "aluminum-extrusion-manufacturing", "description": "Operate aluminum extrusion manufacturing including die design, billet heating, press operations, aging treatment, and profile quality control."},
    {"name": "metal-injection-molding-services", "description": "Manage metal injection molding operations including feedstock formulation, tooling design, debinding processes, sintering cycles, and dimensional control."},
    {"name": "hard-chrome-plating-services", "description": "Operate hard chrome plating facilities including bath management, thickness control, grinding operations, and environmental compliance programs."},
    {"name": "zinc-die-casting-technology", "description": "Manage zinc die casting operations including alloy selection, tooling management, casting parameter control, finishing operations, and quality assurance."},
    {"name": "investment-casting-operations", "description": "Operate investment casting facilities including wax pattern production, shell building, burnout, pouring, knockout, and finishing quality programs."},
    {"name": "progressive-die-manufacturing-services", "description": "Manage progressive die manufacturing including strip layout design, station sequencing, tooling fabrication, tryout, and production validation."},
    {"name": "wire-drawing-technology", "description": "Operate wire drawing production including die selection, lubricant management, annealing schedules, dimensional tolerance control, and surface quality programs."},
]

# Domain: Precision Machining Services
skills += [
    {"name": "metal-superfinishing-services", "description": "Provide metal superfinishing services including stone honing, tape finishing, microfinishing, bearing race finishing, and surface texture measurement."},
    {"name": "electrochemical-machining-services", "description": "Operate electrochemical machining facilities including electrolyte management, tooling design, parameter optimization, and complex geometry production."},
    {"name": "laser-cutting-technology-services", "description": "Manage laser cutting service operations including material qualification, parameter databases, nesting optimization, edge quality control, and process certification."},
    {"name": "wire-edm-technology-services", "description": "Operate wire EDM service centers including wire selection, power parameter management, taper cutting programs, and precision tolerance verification."},
    {"name": "centerless-grinding-services", "description": "Manage centerless grinding operations including wheel selection, blade angle setup, throughfeed and infeed programming, and roundness control."},
    {"name": "jig-boring-services", "description": "Operate jig boring facilities including coordinate hole location, tolerance stack analysis, fixture design, and precision component inspection."},
    {"name": "form-grinding-operations", "description": "Manage form grinding services including profile wheel dressing, gear grinding programs, cam grinding operations, and profile verification."},
    {"name": "deep-hole-drilling-services", "description": "Operate deep hole drilling services including gun drilling, BTA drilling, tool selection, chip management, and straightness verification."},
    {"name": "broaching-operations-management", "description": "Manage broaching operations including tool design, pull and push broaching, surface broaching, coolant management, and keyway quality control."},
    {"name": "honing-lapping-services", "description": "Provide honing and lapping services including bore honing, flat lapping, diamond tooling management, geometric tolerance achievement, and surface finish measurement."},
]

# Domain: Thermal & Surface Treatment Services
skills += [
    {"name": "vacuum-heat-treatment-technology", "description": "Operate vacuum heat treatment facilities including cycle programming, atmosphere management, quench system operations, hardness verification, and distortion control."},
    {"name": "induction-hardening-services", "description": "Manage induction hardening operations including coil design, power parameter programming, quench system management, case depth verification, and distortion minimization."},
    {"name": "shot-peening-services", "description": "Operate shot peening facilities including media selection, intensity verification, Almen strip management, coverage verification, and aerospace specification compliance."},
    {"name": "hot-isostatic-pressing-services", "description": "Manage HIP services including cycle development, pressure-temperature profiles, material qualification, densification verification, and casting porosity elimination."},
    {"name": "plasma-nitriding-services", "description": "Operate plasma nitriding facilities including gas mixture management, temperature uniformity control, case depth development, and wear resistance verification."},
    {"name": "carburizing-case-hardening", "description": "Manage carburizing operations including carbon potential control, diffusion cycle programming, quenching systems, case depth measurement, and core hardness verification."},
    {"name": "salt-bath-heat-treatment", "description": "Operate salt bath heat treatment facilities including bath composition management, temperature uniformity, quenching operations, and neutral salt management."},
    {"name": "fluidized-bed-heat-treatment", "description": "Manage fluidized bed heat treatment operations including media management, temperature uniformity verification, atmosphere control, and cycle optimization."},
    {"name": "thermal-diffusion-coating", "description": "Operate thermal diffusion coating services including coating material management, temperature cycling, thickness control, and corrosion resistance verification."},
    {"name": "ferritic-nitrocarburizing-services", "description": "Manage ferritic nitrocarburizing operations including gas mixture control, compound layer development, diffusion zone management, and salt spray resistance verification."},
]

# Domain: Joining Technology Services
skills += [
    {"name": "ultrasonic-welding-technology", "description": "Operate ultrasonic welding services including horn design, fixture development, parameter optimization, weld strength validation, and leak testing for plastic assemblies."},
    {"name": "friction-stir-welding-services", "description": "Manage friction stir welding operations including tool design, parameter development, weld qualification, aerospace certification, and joint inspection programs."},
    {"name": "diffusion-bonding-services", "description": "Operate diffusion bonding facilities including surface preparation protocols, temperature-pressure cycle development, joint evaluation, and dissimilar material bonding programs."},
    {"name": "brazing-silver-soldering-services", "description": "Manage brazing and silver soldering services including filler metal selection, flux management, joint design optimization, furnace atmosphere control, and joint inspection."},
    {"name": "orbital-welding-technology", "description": "Operate orbital welding services including weld head setup, parameter programming, weld qualification, tube and pipe specification compliance, and purity verification."},
    {"name": "electron-beam-welding-services", "description": "Manage electron beam welding facilities including vacuum chamber management, beam parameter development, joint qualification, and deep penetration weld verification."},
    {"name": "laser-plastic-welding-services", "description": "Operate laser plastic welding services including transmission laser welding, contour welding, simultaneous welding, and joint strength validation for assemblies."},
    {"name": "explosion-welding-services", "description": "Manage explosion welding services including explosive loading calculations, flyer plate positioning, bond interface characterization, and clad plate specification compliance."},
    {"name": "electromagnetic-pulse-welding", "description": "Operate electromagnetic pulse welding facilities including coil design, discharge energy management, standoff gap control, and joint shear strength verification."},
    {"name": "cold-pressure-welding-services", "description": "Manage cold pressure welding operations including surface preparation, pressure parameter control, wire and bar joining, and electrical conductivity verification."},
]

# Domain: Additive Manufacturing Technology
skills += [
    {"name": "direct-metal-laser-sintering-services", "description": "Operate DMLS/SLM service bureaus including material qualification, build parameter management, support strategy optimization, post-processing, and inspection programs."},
    {"name": "binder-jetting-services", "description": "Manage binder jetting additive manufacturing including powder management, binder systems, sintering programs, dimensional accuracy verification, and production scaling."},
    {"name": "directed-energy-deposition-services", "description": "Operate directed energy deposition services including substrate preparation, wire or powder feed management, layer deposition, microstructure control, and repair applications."},
    {"name": "cold-spray-technology-services", "description": "Manage cold spray coating and repair services including powder characterization, gas parameter optimization, coating adhesion verification, and restoration applications."},
    {"name": "wire-arc-additive-manufacturing", "description": "Operate wire arc additive manufacturing services including path planning, deposition parameter development, residual stress management, and near-net-shape production."},
    {"name": "stereolithography-services", "description": "Manage SLA and vat photopolymerization services including resin qualification, build parameter optimization, post-cure management, and mechanical property verification."},
    {"name": "material-jetting-services", "description": "Operate material jetting service operations including multi-material builds, support material management, dimensional accuracy verification, and surface finish optimization."},
    {"name": "laminated-object-manufacturing", "description": "Manage laminated object manufacturing services including material selection, layer bonding optimization, part extraction, finishing operations, and dimensional verification."},
    {"name": "fused-deposition-industrial-services", "description": "Operate industrial FDM service operations including high-performance polymer processing, support strategy development, part orientation optimization, and property verification."},
    {"name": "3d-printed-tooling-services", "description": "Manage additive manufactured tooling services including conformal cooling channel design, tool steel printing, fixture production, and tool life performance validation."},
]

# Domain: Non-Destructive Testing Services
skills += [
    {"name": "computed-tomography-industrial-scanning", "description": "Operate industrial CT scanning services including scan parameter optimization, artifact management, internal defect characterization, and dimensional measurement programs."},
    {"name": "eddy-current-inspection-services", "description": "Manage eddy current inspection services including probe design, calibration standard management, signal interpretation, array ECT programs, and aerospace compliance."},
    {"name": "phased-array-ultrasonic-services", "description": "Operate phased array UT services including probe selection, sectorial scan programming, calibration procedures, weld inspection, and corrosion mapping."},
    {"name": "digital-radiography-services", "description": "Manage digital radiography and computed radiography inspection services including detector management, image quality indicators, interpretation protocols, and digital archive."},
    {"name": "acoustic-emission-monitoring-services", "description": "Operate acoustic emission testing services including sensor array design, threshold setting, source location algorithms, pressure vessel monitoring, and structural monitoring."},
    {"name": "thermographic-inspection-services", "description": "Manage infrared thermographic inspection services including active and passive thermography, thermal resolution calibration, moisture detection, and electrical inspection."},
    {"name": "laser-shearography-services", "description": "Operate laser shearography inspection services including loading method selection, sensitivity calibration, disbond detection, composite inspection, and report generation."},
    {"name": "guided-wave-inspection-services", "description": "Manage guided wave inspection services including transducer ring installation, signal interpretation, pipe screening programs, and corrosion under insulation detection."},
    {"name": "industrial-endoscopy-services", "description": "Operate industrial videoscope and borescope inspection services including probe selection, image documentation, turbine inspection, and fitness for service assessment."},
    {"name": "xrf-material-verification-services", "description": "Manage X-ray fluorescence material verification services including PMI programs, alloy identification, handheld XRF operations, and positive material identification records."},
]

# Domain: Testing & Certification Services
skills += [
    {"name": "fatigue-testing-services", "description": "Operate fatigue testing laboratories including load frame setup, SN curve development, fracture mechanics testing, fatigue crack growth programs, and specimen preparation."},
    {"name": "fire-testing-laboratory-services", "description": "Manage fire testing laboratories including cone calorimetry, large-scale fire tests, flammability testing, smoke toxicity analysis, and certification documentation."},
    {"name": "package-integrity-testing-services", "description": "Operate package integrity testing laboratories including seal strength testing, burst testing, vacuum decay, dye ingress, and distribution simulation testing."},
    {"name": "environmental-stress-screening-services", "description": "Manage ESS and HALT/HASS testing services including thermal cycling profile development, vibration profile optimization, combined environment testing, and failure analysis."},
    {"name": "emc-testing-certification-services", "description": "Operate EMC testing and certification laboratories including radiated emissions, conducted emissions, immunity testing, pre-compliance screening, and certification support."},
    {"name": "vibration-testing-laboratory-services", "description": "Manage vibration testing laboratories including shaker table operations, shock testing, sine sweep programs, random vibration profiles, and fixture design."},
    {"name": "climatic-testing-laboratory-services", "description": "Operate climatic testing laboratories including temperature humidity cycling, damp heat testing, salt spray chambers, UV weathering, and IP ingress testing."},
    {"name": "acoustic-emission-ndt-lab-services", "description": "Manage acoustic emission laboratory services including leak detection, pressure test monitoring, structural monitoring programs, and signal analysis."},
    {"name": "tribology-testing-laboratory-services", "description": "Operate tribology testing laboratories including pin-on-disc testing, four-ball wear testing, fretting wear analysis, lubricant evaluation, and coating performance."},
    {"name": "creep-stress-rupture-testing", "description": "Manage creep and stress rupture testing services including specimen preparation, high-temperature test setup, data analysis, material qualification, and life prediction."},
]

# Domain: Hazardous Environment Equipment Manufacturing
skills += [
    {"name": "explosion-protection-equipment-mfg", "description": "Manufacture explosion protection equipment including flameproof enclosures, increased safety devices, intrinsic safety barriers, ATEX certification management, and product testing."},
    {"name": "intrinsically-safe-device-mfg", "description": "Design and manufacture intrinsically safe devices including barrier design, energy limitation calculations, zener diode selection, certification programs, and field verification."},
    {"name": "explosion-proof-motor-manufacturing", "description": "Manufacture explosion-proof motors including enclosure design, thermal management, certificationcoordination, application engineering, and warranty program management."},
    {"name": "hazardous-area-junction-box-mfg", "description": "Manufacture hazardous area junction boxes including enclosure fabrication, gland plate design, cable entry management, certification programs, and field installation support."},
    {"name": "gas-detection-instrument-manufacturing", "description": "Manufacture gas detection instruments including sensor technology development, alarm logic design, calibration gas management, certification programs, and customer training."},
    {"name": "flame-arrestor-manufacturing", "description": "Design and manufacture flame arrestors including deflagration and detonation types, testing and certification, application engineering, and installation technical support."},
    {"name": "pressure-relief-valve-manufacturing", "description": "Manufacture pressure relief valves including set pressure calibration, capacity certification, inlet and outlet pressure drop management, and test and documentation programs."},
    {"name": "rupture-disc-manufacturing", "description": "Manufacture rupture discs including burst pressure development, temperature correction factors, material qualification, combination device design, and certification management."},
    {"name": "explosion-vent-panel-manufacturing", "description": "Design and manufacture explosion vent panels including sizing calculations, burst pressure calibration, material selection, certification programs, and installation specifications."},
    {"name": "safety-relief-system-design", "description": "Provide safety relief system design services including overpressure scenario analysis, relief device sizing, installation configuration review, and API standard compliance."},
]

# Domain: Flow Control & Valve Manufacturing
skills += [
    {"name": "control-valve-manufacturing", "description": "Manufacture and service control valves including trim selection, sizing calculations, actuator sizing, positioner calibration, and fugitive emission compliance programs."},
    {"name": "safety-instrumented-valve-mfg", "description": "Manufacture safety instrumented system valves including SIL certification, proof test interval management, partial stroke testing, and functional safety documentation."},
    {"name": "butterfly-valve-manufacturing", "description": "Manufacture butterfly valves including disc geometry optimization, seat design, actuator interface, high-performance applications, and fire-safe certification management."},
    {"name": "ball-valve-manufacturing", "description": "Manufacture ball valves including seat and seal material selection, stem packing design, double block and bleed configurations, and cryogenic service qualification."},
    {"name": "gate-globe-check-valve-mfg", "description": "Manufacture gate, globe, and check valve product lines including pressure class management, material certification, trim selection, and non-destructive examination programs."},
    {"name": "solenoid-valve-manufacturing", "description": "Manufacture solenoid valves including coil design, wetted material compatibility, explosion-proof versions, response time optimization, and reliability testing."},
    {"name": "diaphragm-valve-manufacturing", "description": "Manufacture diaphragm valves including elastomer formulation programs, wetted material selection, aseptic versions, flow coefficient optimization, and validation support."},
    {"name": "needle-metering-valve-manufacturing", "description": "Manufacture needle and metering valves including precision flow control, material compatibility programs, clean service versions, and calibrated orifice management."},
    {"name": "pressure-regulator-manufacturing", "description": "Manufacture pressure regulators including dome-loaded designs, back-pressure regulators, high-purity versions, calibration programs, and application engineering support."},
    {"name": "automated-valve-actuator-manufacturing", "description": "Manufacture valve actuators including pneumatic, hydraulic, and electric types, torque sizing, fail-safe spring design, and partial stroke testing capability."},
]

# Domain: Fluid Handling Equipment
skills += [
    {"name": "industrial-hose-manufacturing", "description": "Manufacture industrial hoses including reinforcement selection, coupling design, pressure rating management, chemical compatibility programs, and assembly testing."},
    {"name": "metal-bellows-manufacturing", "description": "Design and manufacture metal bellows including hydroformed and edge-welded types, cycle life prediction, spring rate management, and aerospace qualification programs."},
    {"name": "flexible-hose-connector-mfg", "description": "Manufacture flexible metal hose connectors including braid selection, end fitting design, pressure and cycle life testing, and vibration isolation qualification."},
    {"name": "peristaltic-pump-manufacturing", "description": "Manufacture peristaltic pumps including tube and hose material selection, roller geometry optimization, flow accuracy calibration, and sanitary design certification."},
    {"name": "dosing-pump-manufacturing", "description": "Manufacture dosing and metering pumps including diaphragm design, stroke adjustment mechanisms, flow verification calibration, and chemical compatibility programs."},
    {"name": "magnetic-drive-pump-manufacturing", "description": "Manufacture magnetically driven pumps including magnet coupling design, containment shell materials, eddy current loss management, and dry-run protection systems."},
    {"name": "submersible-pump-technology", "description": "Manufacture submersible pumps including motor cooling designs, cable entry sealing, corrosion protection coatings, borehole pump optimization, and motor protection systems."},
    {"name": "air-operated-diaphragm-pump-mfg", "description": "Manufacture air-operated double diaphragm pumps including diaphragm material selection, valve design, stroke frequency management, stall prevention, and ATEX certification."},
    {"name": "positive-displacement-blower-mfg", "description": "Manufacture positive displacement blowers including timing gear design, casing tolerances, inlet silencer design, pressure relief integration, and pulsation management."},
    {"name": "turbomachinery-seal-systems", "description": "Design and supply turbomachinery sealing systems including dry gas seals, liquid film seals, labyrinth configurations, seal support system design, and performance monitoring."},
]

# Domain: Gas & Air Equipment Manufacturing
skills += [
    {"name": "air-compressor-manufacturing-technology", "description": "Manufacture industrial air compressors including rotary screw, reciprocating, and centrifugal types, efficiency optimization, controls integration, and compressed air treatment systems."},
    {"name": "vacuum-pump-manufacturing-technology", "description": "Manufacture industrial vacuum pumps including dry-running and oil-sealed types, vacuum generation curve management, chemical resistance programs, and system design support."},
    {"name": "industrial-blower-manufacturing", "description": "Manufacture industrial fans and blowers including aerodynamic design, impeller manufacturing, vibration balance programs, noise reduction features, and AMCA certification."},
    {"name": "compressed-air-treatment-systems", "description": "Manufacture compressed air treatment equipment including refrigeration dryers, desiccant dryers, coalescing filters, activated carbon filters, and oil-free system certification."},
    {"name": "nitrogen-generation-systems", "description": "Design and manufacture nitrogen generation systems including PSA technology, membrane separation, purity control, flow management, and industrial application engineering."},
    {"name": "oxygen-enrichment-systems", "description": "Manufacture oxygen enrichment systems including PSA oxygen generation, medical oxygen systems, industrial oxygen concentration, and safety management programs."},
    {"name": "gas-boosting-systems", "description": "Design and manufacture gas boosting systems including air-driven amplifiers, electric compressors, high-pressure gas management, and system safety interlocks."},
    {"name": "cryogenic-equipment-manufacturing", "description": "Manufacture cryogenic equipment including storage vessels, vaporizers, transfer piping, cold boxes, and safety system design for liquid nitrogen, oxygen, and argon service."},
    {"name": "lng-equipment-manufacturing", "description": "Manufacture LNG equipment including cryogenic tanks, regasification systems, fuel systems, loading arms, and safety management for liquefied natural gas applications."},
    {"name": "compressed-hydrogen-systems-mfg", "description": "Design and manufacture compressed hydrogen systems including high-pressure storage, dispensing systems, safety relief devices, and hydrogen embrittlement resistant materials."},
]

# Domain: Separation & Purification Technology
skills += [
    {"name": "centrifuge-manufacturing-technology", "description": "Manufacture industrial centrifuges including disk stack, decanter, and basket types, bowl design optimization, materials selection, separation efficiency validation, and CIP programs."},
    {"name": "cyclone-separator-manufacturing", "description": "Design and manufacture cyclone separators including inlet velocity optimization, separation efficiency modeling, multi-cyclone arrangements, and erosion protection programs."},
    {"name": "electrostatic-precipitator-manufacturing", "description": "Manufacture electrostatic precipitators including electrode design, rapping systems, power supply management, collection efficiency optimization, and opacity compliance."},
    {"name": "scrubber-system-manufacturing", "description": "Design and manufacture wet and dry scrubber systems including packing selection, spray nozzle design, recirculation chemistry management, and emissions compliance programs."},
    {"name": "bag-filter-fabric-filtration-mfg", "description": "Manufacture industrial bag filter systems including fabric selection, cage design, pulse-jet cleaning optimization, filter media qualification, and emissions monitoring."},
    {"name": "ceramic-membrane-manufacturing", "description": "Manufacture ceramic membranes including alumina and titania substrates, pore size control, surface modification, module design, and high-temperature filtration qualification."},
    {"name": "reverse-osmosis-system-manufacturing", "description": "Manufacture and supply reverse osmosis systems including membrane selection, pressure vessel design, energy recovery devices, cleaning protocols, and system performance monitoring."},
    {"name": "ultrafiltration-system-manufacturing", "description": "Design and manufacture ultrafiltration systems including hollow fiber module design, MWCO selection, flux optimization, backwash protocols, and fouling management programs."},
    {"name": "ion-exchange-resin-system-mfg", "description": "Manufacture ion exchange systems including resin selection, regeneration cycle design, mixed bed polishing, resin life management, and water quality verification."},
    {"name": "electrodeionization-system-mfg", "description": "Design and manufacture electrodeionization systems including module design, stack configuration, power supply management, polishing performance, and pharmaceutical water compliance."},
]

# Domain: Thermal Process Equipment Manufacturing
skills += [
    {"name": "kiln-manufacturing-technology", "description": "Manufacture industrial kilns including rotary kilns, tunnel kilns, and shuttle kilns for ceramics, cement, lime, and other thermal processing applications."},
    {"name": "rotary-dryer-manufacturing", "description": "Design and manufacture rotary drum dryers including shell design, flight configuration, inlet temperature management, particle residence time modeling, and moisture control."},
    {"name": "spray-dryer-manufacturing-technology", "description": "Manufacture spray drying systems including atomizer design, chamber geometry, inlet air conditioning, powder collection, and food and pharmaceutical grade validation."},
    {"name": "freeze-dryer-manufacturing-technology", "description": "Manufacture freeze dryers including shelf systems, condenser design, vacuum system integration, cycle development tools, and pharmaceutical qualification programs."},
    {"name": "evaporator-system-manufacturing", "description": "Design and manufacture evaporator systems including falling film, forced circulation, and MVR evaporators, energy efficiency optimization, and fouling management programs."},
    {"name": "crystallizer-system-manufacturing", "description": "Manufacture crystallizer systems including batch and continuous draft tube designs, crystal size distribution management, mother liquor management, and purity optimization."},
    {"name": "autoclave-manufacturing-technology", "description": "Manufacture industrial and research autoclaves including pressure vessel design, heating and cooling jackets, agitation systems, safety interlock management, and certification programs."},
    {"name": "thermal-oxidizer-manufacturing", "description": "Manufacture thermal and catalytic oxidizers including combustion chamber design, heat recovery integration, destruction efficiency validation, and emissions compliance programs."},
    {"name": "furnace-combustion-system-mfg", "description": "Manufacture industrial furnace combustion systems including burner design, combustion air management, temperature uniformity optimization, and AMS qualification testing."},
    {"name": "heat-tracing-system-manufacturing", "description": "Design and manufacture heat tracing systems including electric trace heating, steam tracing, self-regulating cable, and freeze protection and process temperature maintenance."},
]

# Domain: Condensate & Steam System Equipment
skills += [
    {"name": "steam-trap-manufacturing-technology", "description": "Manufacture steam traps including thermodynamic, float-thermostatic, and bimetallic types, trap testing equipment, steam loss monitoring programs, and energy audit services."},
    {"name": "condensate-recovery-equipment-mfg", "description": "Design and manufacture condensate recovery systems including pump-trap sets, flash vessels, condensate recovery programs, and energy saving calculation services."},
    {"name": "boiler-feedwater-treatment-systems", "description": "Manufacture boiler feedwater treatment systems including deaerators, chemical dosing equipment, water quality monitoring, blowdown heat recovery, and softener systems."},
    {"name": "pressure-reducing-valve-mfg", "description": "Manufacture steam and gas pressure reducing valves including balanced design, noise attenuation features, steam quality management, and capacity certification programs."},
    {"name": "heat-recovery-steam-generator-mfg", "description": "Manufacture HRSGs including module design, pressure part fabrication, performance optimization, HRSG inspection programs, and combined cycle application engineering."},
    {"name": "shell-and-tube-heat-exchanger-mfg", "description": "Manufacture shell and tube heat exchangers including TEMA standard compliance, tube bundle design, baffle optimization, thermal rating programs, and inspection management."},
    {"name": "plate-and-frame-heat-exchanger-mfg", "description": "Manufacture plate and frame heat exchangers including plate corrugation design, gasket material programs, thermal performance optimization, and cleaning protocol development."},
    {"name": "air-cooled-heat-exchanger-mfg", "description": "Design and manufacture air-cooled heat exchangers including bundle geometry, fan selection, plenum design, noise control features, and thermal performance validation."},
    {"name": "double-pipe-heat-exchanger-mfg", "description": "Manufacture double pipe and hairpin heat exchangers including annulus design, closure configurations, high-pressure applications, and counter-current flow optimization."},
    {"name": "spiral-heat-exchanger-manufacturing", "description": "Design and manufacture spiral heat exchangers including channel width optimization, self-cleaning flow design, viscous fluid applications, and maintenance access features."},
]

# Domain: Material Handling Equipment Manufacturing
skills += [
    {"name": "screw-conveyor-manufacturing", "description": "Manufacture screw conveyors including flight design, trough selection, hanger bearing management, variable pitch configurations, and enclosed conveyor sanitary design."},
    {"name": "bucket-elevator-manufacturing", "description": "Design and manufacture bucket elevators including belt and chain types, bucket selection, drive design, alignment management, and agricultural and industrial certification."},
    {"name": "pneumatic-conveying-system-mfg", "description": "Design and manufacture pneumatic conveying systems including dilute and dense phase, pipeline routing optimization, filter receiver design, and materials handling qualification."},
    {"name": "vibrating-screen-manufacturing", "description": "Manufacture vibrating screens including linear motion, circular motion, and elliptical motion types, screen media selection, stratification management, and capacity optimization."},
    {"name": "vibrating-conveyor-manufacturing", "description": "Design and manufacture vibrating conveyors including electromagnetic and mechanical drive types, trough design, cooling and heating applications, and process integration."},
    {"name": "drag-chain-conveyor-manufacturing", "description": "Manufacture drag chain conveyors including chain selection, flight design, sealed trough management, hot material handling, and maintenance access optimization."},
    {"name": "live-roller-conveyor-manufacturing", "description": "Manufacture live roller conveyors including roller selection, drive belt management, accumulation zone design, zero pressure accumulation, and sortation integration."},
    {"name": "apron-plate-conveyor-manufacturing", "description": "Design and manufacture apron and plate conveyors including plate design, hinge pin selection, incline capability, bulk material containment, and mining application qualification."},
    {"name": "aero-mechanical-conveyor-mfg", "description": "Manufacture aero-mechanical conveyors including rope disc design, tube configuration, gentle handling capability, food grade certification, and powder conveyance validation."},
    {"name": "size-reduction-equipment-mfg", "description": "Manufacture size reduction equipment including jaw crushers, cone crushers, impact mills, hammer mills, and ball mills for mineral processing and chemical applications."},
]

# Domain: Measurement & Sensing Technology
skills += [
    {"name": "level-measurement-technology-mfg", "description": "Manufacture level measurement instruments including radar, ultrasonic, capacitance, and guided wave types, span calibration management, and process application engineering."},
    {"name": "flow-measurement-technology-mfg", "description": "Manufacture flow measurement instruments including Coriolis, magnetic, vortex, and differential pressure types, flow calibration management, and custody transfer certification."},
    {"name": "temperature-transmitter-manufacturing", "description": "Manufacture temperature transmitters including thermocouple and RTD input types, SIL certification, drift management, and hazardous area version qualification programs."},
    {"name": "pressure-transmitter-manufacturing", "description": "Manufacture pressure transmitters including gauge, absolute, and differential types, overload protection design, SIL ratings, and sanitary connection management."},
    {"name": "analytical-sensor-manufacturing", "description": "Manufacture process analytical sensors including pH, ORP, conductivity, dissolved oxygen, and turbidity types, calibration interval management, and process application support."},
    {"name": "gas-chromatograph-manufacturing", "description": "Manufacture process gas chromatographs including column selection, detector design, analysis cycle management, sample conditioning systems, and field calibration programs."},
    {"name": "infrared-gas-analyzer-manufacturing", "description": "Manufacture infrared gas analyzers including multi-component capability, cross-sensitivity compensation, NDIR technology optimization, and continuous emissions monitoring."},
    {"name": "moisture-analyzer-manufacturing", "description": "Manufacture moisture and humidity analyzers including chilled mirror, capacitive, and Karl Fischer types, calibration standard management, and trace moisture measurement."},
    {"name": "particle-size-analyzer-mfg", "description": "Manufacture particle size analyzers including laser diffraction, dynamic light scattering, and image analysis types, reference material programs, and application method development."},
    {"name": "liquid-analysis-instrumentation-mfg", "description": "Manufacture liquid analysis instrumentation including multi-parameter sensors, digital sensor technology, calibration management systems, and industrial process monitoring."},
]

# Domain: Data Center & Power Infrastructure Manufacturing
skills += [
    {"name": "data-center-ups-manufacturing", "description": "Manufacture uninterruptible power supplies including online double conversion, modular architecture, battery management, bypass controls, and data center certification programs."},
    {"name": "power-distribution-unit-manufacturing", "description": "Manufacture power distribution units including intelligent PDUs, outlet monitoring, remote switching, current measurement accuracy, and data center power management integration."},
    {"name": "server-rack-cabinet-manufacturing", "description": "Manufacture server racks and cabinets including structural load ratings, airflow optimization features, cable management systems, and data center containment compatibility."},
    {"name": "data-center-cooling-equipment-mfg", "description": "Manufacture data center cooling equipment including in-row coolers, rear-door heat exchangers, liquid cooling distribution units, and free cooling economizer systems."},
    {"name": "data-center-busway-manufacturing", "description": "Manufacture overhead busway systems for data centers including plug-in bus design, tap-off unit management, protection coordination, and incremental capacity expansion."},
    {"name": "modular-data-center-manufacturing", "description": "Manufacture modular and prefabricated data centers including container-based designs, integrated infrastructure management, rapid deployment, and scalability management."},
    {"name": "precision-air-conditioning-mfg", "description": "Manufacture precision air conditioning units for data centers including close-coupled cooling, hot and cold aisle containment optimization, and humidity control systems."},
    {"name": "static-transfer-switch-manufacturing", "description": "Manufacture static transfer switches including transfer time optimization, make-before-break designs, parallel bus applications, and critical power protection management."},
    {"name": "battery-cabinet-manufacturing", "description": "Manufacture battery cabinet systems including VRLA and lithium battery integration, BMS integration, thermal management, and fire suppression readiness."},
    {"name": "dc-power-system-manufacturing", "description": "Manufacture DC power systems including rectifier design, battery charge management, distribution design, DCIM integration, and telecom and data center applications."},
]

# Domain: Industrial Battery & Energy Storage Manufacturing
skills += [
    {"name": "industrial-battery-manufacturing", "description": "Manufacture industrial batteries including lead-acid, nickel-cadmium, and nickel-iron types, plate production, formation cycling, capacity testing, and application engineering."},
    {"name": "supercapacitor-ultracapacitor-mfg", "description": "Manufacture supercapacitors and ultracapacitors including electrode material production, electrolyte management, cell assembly, module design, and power electronics integration."},
    {"name": "flow-battery-manufacturing", "description": "Manufacture flow battery systems including vanadium redox and zinc-bromine types, electrolyte management, stack design, power conversion integration, and long-duration storage."},
    {"name": "sodium-ion-battery-development", "description": "Develop and manufacture sodium-ion batteries including electrode chemistry programs, electrolyte formulation, cell design optimization, and stationary storage applications."},
    {"name": "thermal-energy-storage-systems", "description": "Design and manufacture thermal energy storage systems including molten salt, chilled water, and ice storage, charge and discharge optimization, and grid service programs."},
    {"name": "battery-management-system-manufacturing", "description": "Develop and manufacture battery management systems including cell balancing algorithms, state of charge estimation, fault detection, communication protocol integration, and certification."},
    {"name": "battery-formation-cycling-equipment", "description": "Manufacture battery formation and cycling equipment including charge and discharge control, capacity grading automation, data acquisition, and cell production line integration."},
    {"name": "battery-testing-equipment-mfg", "description": "Manufacture battery testing equipment including cycle testers, abuse test systems, calorimeters, impedance analyzers, and environmental chamber integration programs."},
    {"name": "battery-electrode-manufacturing-equipment", "description": "Manufacture battery electrode production equipment including slurry mixers, coating machines, calendering systems, and electrode inspection and quality management programs."},
    {"name": "battery-assembly-line-manufacturing", "description": "Design and supply battery cell and pack assembly lines including cell handling systems, electrolyte filling, formation cycling integration, and end-of-line testing."},
]

# Domain: Water Treatment Equipment Manufacturing
skills += [
    {"name": "dissolved-air-flotation-manufacturing", "description": "Manufacture dissolved air flotation systems including pressurization vessel design, recycle ratio management, sludge removal mechanisms, and water treatment applications."},
    {"name": "electrocoagulation-system-manufacturing", "description": "Design and manufacture electrocoagulation systems including electrode management, current density optimization, sludge characterization, and industrial wastewater applications."},
    {"name": "advanced-oxidation-process-systems", "description": "Manufacture advanced oxidation process systems including UV-hydrogen peroxide, ozone-UV, and Fentons process types, system safety management, and compliance verification."},
    {"name": "constructed-wetland-systems", "description": "Design constructed wetland systems for wastewater treatment including media selection, plant species programs, hydraulic loading management, and performance monitoring."},
    {"name": "sludge-dewatering-equipment-mfg", "description": "Manufacture sludge dewatering equipment including belt filter presses, centrifuges, screw presses, and filter presses for municipal and industrial biosolids management."},
    {"name": "water-softener-system-manufacturing", "description": "Manufacture water softener systems including resin vessel design, multiport valve programs, regeneration optimization, brine management, and commercial hardness removal."},
    {"name": "ozone-generation-system-manufacturing", "description": "Manufacture ozone generation systems including corona discharge systems, oxygen feed management, contact vessel design, off-gas destruction, and disinfection byproduct management."},
    {"name": "uv-disinfection-system-manufacturing", "description": "Manufacture UV disinfection systems including lamp technology management, sleeve cleaning systems, dose validation, log inactivation programs, and regulatory compliance."},
    {"name": "chemical-dosing-system-manufacturing", "description": "Design and manufacture chemical dosing systems including metering pump selection, tank sizing, containment design, interlock management, and remote monitoring integration."},
    {"name": "desalination-equipment-manufacturing", "description": "Manufacture desalination equipment including SWRO systems, energy recovery devices, pre-treatment systems, post-treatment systems, and brine disposal management."},
]

# Domain: Pollution Control Equipment Manufacturing
skills += [
    {"name": "selective-catalytic-reduction-mfg", "description": "Manufacture SCR systems for NOx control including catalyst selection, urea injection system design, flow distribution management, and ammonia slip monitoring programs."},
    {"name": "flue-gas-desulfurization-mfg", "description": "Manufacture FGD systems including wet limestone scrubbers, spray dry absorbers, gypsum dewatering, reagent management, and stack emissions compliance programs."},
    {"name": "activated-carbon-injection-systems", "description": "Design and supply activated carbon injection systems for mercury and dioxin control, including carbon feed management, carbon specifications, and compliance verification."},
    {"name": "biogas-upgrading-systems-mfg", "description": "Manufacture biogas upgrading systems including water scrubbing, PSA technology, membrane separation, biomethane quality management, and grid injection compliance."},
    {"name": "thermal-destruction-system-mfg", "description": "Manufacture thermal destruction systems for hazardous waste including rotary kiln incinerators, secondary combustion chambers, and air pollution control train integration."},
    {"name": "acid-gas-control-system-mfg", "description": "Design and manufacture acid gas control systems including caustic scrubbers, dry sorbent injection, packed tower design, and HCl and HF compliance monitoring."},
    {"name": "voc-control-equipment-manufacturing", "description": "Manufacture VOC control equipment including regenerative thermal oxidizers, catalytic oxidizers, carbon adsorption systems, and condensation recovery systems."},
    {"name": "particulate-matter-control-systems", "description": "Design and manufacture particulate matter control systems including high-efficiency cyclones, multi-stage filtration, and hybrid electrostatic and fabric filtration systems."},
    {"name": "odor-control-systems-manufacturing", "description": "Manufacture odor control systems including biofilters, chemical scrubbers, activated carbon adsorbers, UV photolysis units, and odor dispersion modeling programs."},
    {"name": "wastewater-odor-control-equipment", "description": "Design and manufacture wastewater odor control equipment including chemical dosing for H2S suppression, ductwork design, fan selection, and scrubber system integration."},
]

# Domain: Mixing & Agitation Equipment Manufacturing
skills += [
    {"name": "industrial-mixer-manufacturing", "description": "Manufacture industrial mixers including top-entry, side-entry, and bottom-entry types, impeller selection, seal design, agitation scale-up programs, and explosion-proof versions."},
    {"name": "high-shear-mixer-manufacturing", "description": "Design and manufacture high shear mixers including rotor-stator technology, inline and batch types, emulsification programs, droplet size distribution management, and CIP design."},
    {"name": "static-mixer-manufacturing", "description": "Manufacture static mixing elements including helical, SMX, and custom designs, pressure drop calculations, heat transfer applications, and reactor integration programs."},
    {"name": "ribbon-blender-manufacturing", "description": "Manufacture ribbon blenders including inner and outer ribbon design, discharge valve options, sanitary design programs, and blend time optimization for powder applications."},
    {"name": "paddle-mixer-ploughshare-mfg", "description": "Manufacture paddle and ploughshare mixers including mixing tool design, choppers integration, discharge system options, and paste and wet granulation applications."},
    {"name": "tumble-blender-manufacturing", "description": "Manufacture tumble blenders including V-blenders, double cone blenders, and bin tumblers, intensifier bar options, and pharmaceutical blend uniformity qualification."},
    {"name": "kneader-mixer-manufacturing", "description": "Manufacture kneader and sigma mixers including blade geometry design, jacketed vessel options, vacuum capability, discharge systems, and high viscosity material processing."},
    {"name": "disperser-dissolver-manufacturing", "description": "Manufacture disperser and high-speed dissolver equipment including blade selection, variable speed drives, tank integration, and pigment dispersion optimization."},
    {"name": "planetary-mixer-manufacturing", "description": "Manufacture planetary mixers including bowl capacity range, interchangeable agitator options, variable speed programs, and food and pharmaceutical application qualification."},
    {"name": "continuous-mixer-manufacturing", "description": "Design and manufacture continuous mixing systems including loss-in-weight feeder integration, mixing performance validation, residence time distribution, and process control integration."},
]

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

os.makedirs(base, exist_ok=True)

count = 0
for skill in skills:
    skill_dir = os.path.join(base, skill["name"])
    os.makedirs(skill_dir, exist_ok=True)
    skill_path = os.path.join(skill_dir, "SKILL.md")
    with open(skill_path, "w", encoding="utf-8") as f:
        f.write(SKILL_TEMPLATE.format(name=skill["name"], description=skill["description"]))
    count += 1

print(f"Done: {count} skills")
