import os

base = r"c:\Users\mirza\MAARS-Command\.claude\skills"

# Domain: Bearings Manufacturing
skills = [
    {"name": "bearing-product-engineering", "description": "Engineer precision bearing products including radial, thrust, and angular contact designs with tolerance stacking and load capacity calculations."},
    {"name": "bearing-materials-selection", "description": "Select bearing materials including steel grades, ceramic options, and polymer choices based on load, speed, temperature, and corrosion requirements."},
    {"name": "bearing-lubrication-management", "description": "Manage bearing lubrication programs including grease specification, re-lubrication intervals, oil mist systems, and contamination control."},
    {"name": "bearing-quality-inspection", "description": "Inspect bearing quality including dimensional metrology, noise and vibration testing, torque measurement, and surface finish analysis."},
    {"name": "bearing-failure-analysis", "description": "Analyze bearing failures including spalling, fretting, electrical erosion, and misalignment damage with root cause documentation and corrective action."},
    {"name": "bearing-application-engineering", "description": "Provide bearing application engineering support including mounting recommendations, shaft and housing fits, and service life calculations."},
    {"name": "bearing-supply-chain-ops", "description": "Manage bearing supply chain operations including distributor programs, counterfeit prevention, traceability, and consignment inventory management."},
    {"name": "bearing-remanufacturing-ops", "description": "Operate bearing remanufacturing programs including disassembly inspection, component replacement, reassembly, and performance verification."},
    {"name": "bearing-predictive-maintenance", "description": "Deploy bearing predictive maintenance programs using vibration analysis, temperature monitoring, and ultrasound to detect early failure onset."},
    {"name": "bearing-catalog-management", "description": "Manage bearing product catalogs including cross-reference databases, interchange equivalents, and technical specification documentation."},
]

# Domain: Gear Manufacturing
skills += [
    {"name": "gear-design-engineering", "description": "Design precision gears including spur, helical, bevel, and worm types with tooth profile optimization, load analysis, and noise reduction."},
    {"name": "gear-hobbing-operations", "description": "Operate gear hobbing processes including hob selection, feed and speed optimization, tooth accuracy measurement, and tooling management."},
    {"name": "gear-grinding-finishing", "description": "Execute gear grinding and finishing operations including profile grinding, thread grinding, superfinishing, and gear accuracy inspection."},
    {"name": "gear-heat-treatment-ops", "description": "Manage gear heat treatment operations including case carburizing, nitriding, induction hardening, and metallurgical quality verification."},
    {"name": "gear-quality-metrology", "description": "Measure gear quality using CMM, gear testers, surface profilometers, and statistical process control for AGMA and ISO grade compliance."},
    {"name": "gearbox-assembly-testing", "description": "Assemble and test gearboxes including backlash adjustment, bearing preload setting, leak testing, and functional run-in procedures."},
    {"name": "gear-failure-investigation", "description": "Investigate gear failures including tooth fracture, pitting, scuffing, and wear modes with tribological analysis and redesign recommendations."},
    {"name": "gear-material-procurement", "description": "Procure gear materials including alloy steel bar stock, forgings, and castings with chemical and mechanical property verification."},
    {"name": "gear-application-support", "description": "Provide gear application engineering support including power rating calculations, service factor selection, and installation guidance."},
    {"name": "gear-catalog-product-mgmt", "description": "Manage gear product lines including standard catalog items, custom engineering projects, and obsolescence management programs."},
]

# Domain: Power Transmission Equipment
skills += [
    {"name": "power-transmission-system-design", "description": "Design power transmission systems including belt drives, chain drives, gear drives, and couplings with service factor and efficiency analysis."},
    {"name": "coupling-selection-engineering", "description": "Select and engineer shaft couplings including flexible, rigid, fluid, and disc types for torque capacity, misalignment, and vibration damping."},
    {"name": "belt-drive-system-ops", "description": "Design and maintain belt drive systems including V-belt, synchronous belt, and flat belt drives with tension monitoring and replacement programs."},
    {"name": "chain-drive-maintenance", "description": "Maintain chain drive systems including lubrication programs, elongation monitoring, sprocket inspection, and replacement scheduling."},
    {"name": "gearmotor-selection-apps", "description": "Select and apply gearmotors including planetary, parallel shaft, and bevel-helical types for torque, speed, and mounting requirements."},
    {"name": "torque-limiter-clutch-ops", "description": "Apply torque limiters and overload clutches including slip torque calibration, reset procedures, and protective system integration."},
    {"name": "variable-speed-drive-ops", "description": "Operate variable speed drive systems including mechanical CVTs, hydraulic drives, and electromechanical configurations for process control."},
    {"name": "power-transmission-reliability", "description": "Implement reliability programs for power transmission components including MTBF tracking, failure mode libraries, and upgrade initiatives."},
    {"name": "power-trans-inventory-mgmt", "description": "Manage power transmission spare parts inventory including critical spares identification, stocking levels, and vendor-managed programs."},
    {"name": "power-trans-digital-catalog", "description": "Develop digital product catalogs for power transmission equipment including selection tools, 3D models, and configurator interfaces."},
]

# Domain: Linear Motion Systems
skills += [
    {"name": "linear-guide-rail-selection", "description": "Select linear guide rails and carriages including profile rail, round rail, and miniature types for load capacity, accuracy, and travel length."},
    {"name": "ball-screw-system-design", "description": "Design ball screw drive systems including lead selection, preload specification, support bearing configuration, and critical speed analysis."},
    {"name": "linear-actuator-integration", "description": "Integrate linear actuators including electric cylinders, rodless actuators, and linear modules into automated machine designs."},
    {"name": "linear-motion-accuracy-verification", "description": "Verify linear motion system accuracy including straightness, flatness, positioning repeatability, and parallelism measurement programs."},
    {"name": "linear-axis-maintenance", "description": "Maintain linear motion axes including lubrication management, wiper replacement, clearance adjustment, and wear monitoring programs."},
    {"name": "linear-motion-sizing-software", "description": "Use linear motion sizing software to calculate loads, moments, duty cycles, and select appropriate components for application requirements."},
    {"name": "linear-stage-assembly-ops", "description": "Assemble precision linear stages including base machining requirements, component alignment procedures, and functional acceptance testing."},
    {"name": "linear-motion-cleanroom-apps", "description": "Apply linear motion systems in cleanroom environments including low-outgassing materials, lubrication-free options, and contamination controls."},
    {"name": "gantry-system-engineering", "description": "Engineer multi-axis gantry systems including structural analysis, drive configuration, payload management, and coordinated motion control."},
    {"name": "linear-motion-lifecycle-mgmt", "description": "Manage linear motion component lifecycles including travel life calculations, predictive replacement scheduling, and cost-of-ownership analysis."},
]

# Domain: Pneumatic Components Manufacturing
skills += [
    {"name": "pneumatic-cylinder-design", "description": "Design pneumatic cylinders including bore sizing, stroke selection, cushioning, and mounting configuration for force and speed requirements."},
    {"name": "pneumatic-valve-selection", "description": "Select pneumatic valves including directional control, flow control, and pressure control types for circuit function and response requirements."},
    {"name": "pneumatic-circuit-design", "description": "Design pneumatic circuits including logic diagrams, component sizing, flow calculation, and safety circuit integration."},
    {"name": "pneumatic-fitting-tubing-ops", "description": "Specify pneumatic fittings and tubing including push-to-connect, compression, and barb types with pressure rating and material selection."},
    {"name": "pneumatic-actuator-maintenance", "description": "Maintain pneumatic actuators including seal replacement, bore inspection, cushion adjustment, and performance restoration procedures."},
    {"name": "pneumatic-system-commissioning", "description": "Commission pneumatic systems including pressure setting, flow adjustment, leak testing, and functional verification procedures."},
    {"name": "frl-unit-management", "description": "Manage filter-regulator-lubricator units including element replacement schedules, pressure setting verification, and oil level monitoring."},
    {"name": "pneumatic-safety-exhaust-valve", "description": "Apply safety exhaust valves and quick exhaust systems for pneumatic safety category compliance and energy isolation programs."},
    {"name": "compressed-air-quality-mgmt", "description": "Manage compressed air quality including ISO 8573 classification, desiccant dryer operation, and contamination monitoring programs."},
    {"name": "pneumatic-component-catalog-mgmt", "description": "Manage pneumatic component product lines including parametric configurators, cross-reference tools, and application engineering documentation."},
]

# Domain: Hydraulic Systems Manufacturing
skills += [
    {"name": "hydraulic-pump-selection", "description": "Select hydraulic pumps including gear, vane, and piston types for flow, pressure, efficiency, and noise requirements in system designs."},
    {"name": "hydraulic-valve-engineering", "description": "Engineer hydraulic valves including directional, pressure relief, flow control, and proportional types for circuit performance requirements."},
    {"name": "hydraulic-cylinder-manufacturing", "description": "Manufacture hydraulic cylinders including tube honing, piston rod grinding, seal groove machining, and leak testing operations."},
    {"name": "hydraulic-circuit-design", "description": "Design hydraulic circuits including symbol schematic creation, flow and pressure analysis, heat generation calculation, and safety valve sizing."},
    {"name": "hydraulic-fluid-management", "description": "Manage hydraulic fluid programs including viscosity grade selection, contamination monitoring, filtration specification, and change-out intervals."},
    {"name": "hydraulic-system-commissioning", "description": "Commission hydraulic systems including flushing procedures, pressure setting, pump startup, and system performance verification."},
    {"name": "hydraulic-filtration-systems", "description": "Design and maintain hydraulic filtration systems including beta ratio selection, differential pressure monitoring, and bypass valve management."},
    {"name": "hydraulic-accumulator-management", "description": "Manage hydraulic accumulators including pre-charge pressure verification, bladder inspection, safety compliance, and energy storage calculations."},
    {"name": "hydraulic-predictive-maintenance", "description": "Deploy predictive maintenance for hydraulic systems including oil analysis, pressure wave monitoring, and thermal imaging programs."},
    {"name": "hydraulic-power-unit-assembly", "description": "Assemble hydraulic power units including reservoir fabrication, component mounting, piping installation, and factory acceptance testing."},
]

# Domain: Industrial Sensors Manufacturing
skills += [
    {"name": "proximity-sensor-engineering", "description": "Engineer proximity sensors including inductive, capacitive, and magnetic types with switching distance, frequency, and output configuration."},
    {"name": "photoelectric-sensor-design", "description": "Design photoelectric sensing systems including through-beam, retro-reflective, and diffuse configurations for detection range and target requirements."},
    {"name": "pressure-sensor-manufacturing", "description": "Manufacture pressure sensors including piezoresistive, capacitive, and strain gauge types with accuracy, range, and process connection specifications."},
    {"name": "temperature-sensor-production", "description": "Produce temperature sensors including thermocouples, RTDs, and thermistors with accuracy class, response time, and protection tube specifications."},
    {"name": "flow-sensor-engineering", "description": "Engineer flow sensors including electromagnetic, vortex, ultrasonic, and Coriolis types for fluid media, flow range, and accuracy requirements."},
    {"name": "level-sensor-applications", "description": "Apply level sensors including ultrasonic, radar, float, and capacitive types for liquid and solid level measurement in process vessels."},
    {"name": "vision-system-integration", "description": "Integrate machine vision systems including camera selection, lens optics, illumination design, and image processing algorithm development."},
    {"name": "encoder-resolver-selection", "description": "Select encoders and resolvers including incremental, absolute, optical, and magnetic types for position feedback accuracy and environment requirements."},
    {"name": "safety-sensor-systems", "description": "Design safety sensor systems including light curtains, safety laser scanners, and safety mats for machinery guarding and risk assessment compliance."},
    {"name": "sensor-calibration-programs", "description": "Manage sensor calibration programs including calibration intervals, NIST-traceable standards, uncertainty budgets, and certificate management."},
]

# Domain: RFID & Auto-ID Technology
skills += [
    {"name": "rfid-system-design", "description": "Design RFID systems including frequency selection, reader infrastructure, antenna placement, and tag selection for identification and tracking applications."},
    {"name": "rfid-tag-manufacturing-ops", "description": "Manage RFID tag manufacturing including inlay production, encapsulation, encoding, and quality verification for HF and UHF products."},
    {"name": "rfid-middleware-integration", "description": "Integrate RFID middleware including reader management, event filtering, data normalization, and enterprise system connectivity."},
    {"name": "barcode-system-design", "description": "Design barcode systems including symbology selection, label specification, print quality verification, and scanner placement optimization."},
    {"name": "auto-id-warehouse-ops", "description": "Deploy auto-ID solutions in warehouse operations including receiving, putaway, picking, and shipping scan workflows for inventory accuracy."},
    {"name": "rtls-system-deployment", "description": "Deploy real-time location systems using UWB, BLE, or Wi-Fi technologies for asset tracking, personnel safety, and workflow analytics."},
    {"name": "rfid-healthcare-apps", "description": "Implement RFID in healthcare settings including patient identification, asset tracking, medication management, and sterilization cycle tracking."},
    {"name": "serialization-traceability-ops", "description": "Manage product serialization and traceability programs including unique identifier assignment, scan event capture, and genealogy data management."},
    {"name": "auto-id-retail-ops", "description": "Deploy auto-ID in retail environments including inventory counting, loss prevention, self-checkout, and omnichannel fulfillment applications."},
    {"name": "rfid-standards-compliance", "description": "Navigate RFID and auto-ID standards compliance including GS1, EPC Gen2, ISO 18000, and regulatory mandates for pharmaceutical and food sectors."},
]

# Domain: Test & Measurement Instruments
skills += [
    {"name": "oscilloscope-applications", "description": "Apply oscilloscopes for electronics troubleshooting including waveform analysis, protocol decoding, and jitter measurement in development and production."},
    {"name": "spectrum-analyzer-ops", "description": "Operate spectrum analyzers for RF signal characterization including spurious emissions measurement, phase noise, and adjacent channel power."},
    {"name": "network-analyzer-calibration", "description": "Calibrate and operate network analyzers for S-parameter measurement, impedance characterization, and antenna tuning in RF design validation."},
    {"name": "power-meter-analyzer-ops", "description": "Use power meters and analyzers for electrical power quality measurement including harmonics, power factor, and energy consumption analysis."},
    {"name": "signal-generator-applications", "description": "Apply signal generators for stimulus-response testing including arbitrary waveform generation, modulated signal creation, and parametric sweeps."},
    {"name": "data-acquisition-system-ops", "description": "Operate data acquisition systems including channel configuration, sample rate setting, trigger setup, and real-time data processing for test applications."},
    {"name": "logic-analyzer-debug", "description": "Use logic analyzers for digital system debugging including timing analysis, protocol decoding, and state machine verification."},
    {"name": "calibration-lab-management", "description": "Manage calibration laboratory operations including ISO 17025 accreditation, measurement uncertainty documentation, and instrument asset management."},
    {"name": "emi-emc-test-management", "description": "Manage EMI/EMC testing programs including pre-compliance screening, accredited test lab coordination, and certification documentation."},
    {"name": "test-equipment-lifecycle-mgmt", "description": "Manage test equipment lifecycle including acquisition, calibration scheduling, repair coordination, and obsolescence planning."},
]

# Domain: Industrial Weighing Systems
skills += [
    {"name": "load-cell-selection-engineering", "description": "Select load cells including single-point, bending beam, shear beam, and compression types for capacity, accuracy, and environmental requirements."},
    {"name": "scale-calibration-management", "description": "Manage industrial scale calibration programs including NIST traceability, legal-for-trade certification, calibration intervals, and adjustment documentation."},
    {"name": "belt-weigher-operations", "description": "Operate belt weigher systems including speed sensor maintenance, idler alignment, span calibration, and totalizer accuracy verification."},
    {"name": "tank-hopper-weighing-systems", "description": "Design and maintain tank and hopper weighing systems including structural mount design, thermal compensation, and CIP wash-down protection."},
    {"name": "truck-scale-operations", "description": "Operate truck scale systems including foundation maintenance, indicator calibration, ticketing integration, and axle weight enforcement."},
    {"name": "checkweigher-systems-mgmt", "description": "Manage checkweigher systems in production lines including statistical rejection analysis, OEE monitoring, and regulatory compliance documentation."},
    {"name": "force-torque-measurement-ops", "description": "Apply force and torque measurement systems for assembly tooling, materials testing, and product characterization with traceability documentation."},
    {"name": "weighing-system-integration", "description": "Integrate weighing systems with ERP and MES platforms including data communication protocols, batch management, and inventory reconciliation."},
    {"name": "hazardous-area-weighing", "description": "Deploy weighing systems in hazardous areas including ATEX/IECEx certified equipment selection, intrinsically safe installations, and compliance documentation."},
    {"name": "weighing-system-validation", "description": "Validate weighing systems for pharmaceutical and food applications including IQ/OQ/PQ protocols, USP requirements, and FDA 21 CFR Part 11 compliance."},
]

# Domain: Vibration Analysis & Monitoring
skills += [
    {"name": "vibration-sensor-selection", "description": "Select vibration sensors including accelerometers, velocity transducers, and displacement probes for machine monitoring frequency range and mounting."},
    {"name": "vibration-data-collection", "description": "Collect vibration data using portable analyzers and online systems with route-based programs, trigger conditions, and trend data management."},
    {"name": "vibration-spectrum-analysis", "description": "Analyze vibration spectra for fault detection including bearing defect frequencies, gear mesh harmonics, imbalance, and misalignment signatures."},
    {"name": "rotor-balancing-ops", "description": "Perform rotor balancing operations including single-plane and two-plane balancing, influence coefficient method, and balance quality grade verification."},
    {"name": "shaft-alignment-programs", "description": "Execute precision shaft alignment programs using laser alignment tools, rim-and-face methods, and soft foot detection with tolerance verification."},
    {"name": "ois-vibration-monitoring", "description": "Deploy online integrated vibration monitoring systems including sensor wiring, barrier selection, alarm setpoint management, and historian integration."},
    {"name": "structural-vibration-testing", "description": "Conduct structural vibration testing including modal analysis, frequency response measurement, and resonance identification for design validation."},
    {"name": "vibration-iso-compliance", "description": "Apply ISO vibration standards including ISO 10816, ISO 13373, and machinery vibration severity charts for acceptance criteria and reporting."},
    {"name": "vibration-training-programs", "description": "Develop vibration analysis training programs including ISO Cat I through Cat IV certification paths, practical exercises, and competency assessment."},
    {"name": "vibration-cbm-program-mgmt", "description": "Manage condition-based maintenance programs using vibration analysis including work order generation, repair effectiveness verification, and KPI reporting."},
]

# Domain: Acoustic & Noise Control
skills += [
    {"name": "industrial-noise-measurement", "description": "Measure industrial noise levels using sound level meters and dosimeters for OSHA compliance, noise mapping, and control prioritization."},
    {"name": "acoustic-product-design", "description": "Design acoustic products including noise barriers, enclosures, silencers, and vibration isolation mounts for industrial noise control applications."},
    {"name": "hearing-conservation-programs", "description": "Implement hearing conservation programs including noise exposure monitoring, audiometric testing, hearing protection selection, and employee training."},
    {"name": "sound-power-measurement", "description": "Measure sound power levels of machinery using ISO 3740 series methods for product certification, noise labeling, and source ranking."},
    {"name": "building-acoustics-design", "description": "Design building acoustics including speech intelligibility, reverberation time, impact sound isolation, and HVAC noise control."},
    {"name": "product-noise-testing", "description": "Conduct product noise testing including anechoic chamber measurements, sound quality analysis, and psychoacoustic metric calculation."},
    {"name": "hvac-noise-control", "description": "Control HVAC system noise including duct silencer selection, fan noise prediction, breakout analysis, and vibration isolation design."},
    {"name": "acoustic-modeling-simulation", "description": "Create acoustic models using FEA and BEM software for product development, room acoustics prediction, and noise reduction design."},
    {"name": "noise-vibration-harshness-nvh", "description": "Manage NVH programs for automotive and industrial products including order tracking, transfer path analysis, and sound quality targets."},
    {"name": "acoustic-compliance-certification", "description": "Navigate acoustic compliance certifications including OSHA, CE marking, EPA noise regulations, and environmental impact acoustic assessments."},
]

# Domain: Environmental Test Chambers
skills += [
    {"name": "climatic-chamber-operations", "description": "Operate climatic test chambers including temperature-humidity cycling, condensation testing, and product qualification to IEC and MIL-STD standards."},
    {"name": "thermal-shock-testing", "description": "Execute thermal shock testing including air-to-air and liquid-to-liquid transitions, dwell times, and failure analysis of thermally cycled products."},
    {"name": "altitude-chamber-testing", "description": "Conduct altitude simulation testing including low pressure operation, rapid decompression, and combined temperature-altitude profiles."},
    {"name": "salt-spray-corrosion-testing", "description": "Run salt spray corrosion tests per ASTM B117, ISO 9227, and cyclic corrosion test standards with specimen preparation and result evaluation."},
    {"name": "vibration-chamber-combined-testing", "description": "Execute combined vibration and temperature testing including HALT, HASS, and AGREE profiles for product reliability screening."},
    {"name": "uv-weathering-testing", "description": "Conduct UV weathering and light stability testing using Xenon arc and UV fluorescent chambers per ISO 4892 and ASTM G154 standards."},
    {"name": "chamber-qualification-calibration", "description": "Qualify and calibrate environmental test chambers including temperature uniformity surveys, humidity verification, and IQ/OQ documentation."},
    {"name": "environmental-test-planning", "description": "Plan environmental test programs including test sequence optimization, sample size selection, and failure criteria definition for product qualification."},
    {"name": "chamber-maintenance-management", "description": "Manage environmental chamber maintenance including refrigeration system service, heating element replacement, and control system updates."},
    {"name": "environmental-test-reporting", "description": "Generate environmental test reports including raw data analysis, failure mode documentation, pass/fail determination, and certification support."},
]

# Domain: Structural Health Monitoring
skills += [
    {"name": "shm-sensor-network-design", "description": "Design structural health monitoring sensor networks including accelerometer placement, strain gauge arrays, and acoustic emission systems for infrastructure."},
    {"name": "bridge-monitoring-ops", "description": "Operate bridge structural monitoring systems including live load assessment, fatigue accumulation tracking, and deterioration alert management."},
    {"name": "building-shm-systems", "description": "Deploy building structural health monitoring including seismic response capture, inter-story drift measurement, and post-event assessment."},
    {"name": "wind-turbine-shm", "description": "Monitor wind turbine structural integrity including blade vibration, tower modal analysis, drivetrain condition, and fatigue damage tracking."},
    {"name": "pipeline-integrity-monitoring", "description": "Manage pipeline integrity monitoring programs including corrosion sensors, acoustic emission leak detection, and in-line inspection data integration."},
    {"name": "shm-data-analytics", "description": "Analyze structural health monitoring data including modal parameter extraction, damage indices, machine learning anomaly detection, and trend reporting."},
    {"name": "corrosion-monitoring-programs", "description": "Implement corrosion monitoring programs including electrochemical probes, ER probes, and coupon programs with data management and inspection integration."},
    {"name": "aerospace-shm-programs", "description": "Manage aerospace structural health monitoring programs including in-service inspection reduction credit, damage tolerance analysis, and certification."},
    {"name": "shm-system-integration", "description": "Integrate SHM systems with asset management platforms including IoT connectivity, cloud data storage, and dashboard visualization for operators."},
    {"name": "shm-standards-compliance", "description": "Navigate SHM standards and guidelines including IABMAS, ISHMII practices, and regulatory requirements for monitored infrastructure assets."},
]

# Domain: Gas Detection & Analysis
skills += [
    {"name": "fixed-gas-detection-design", "description": "Design fixed gas detection systems including sensor technology selection, detector placement, alarm zoning, and safety integrity level compliance."},
    {"name": "portable-gas-detector-programs", "description": "Manage portable gas detector programs including bump test procedures, calibration schedules, gas exposure records, and fleet tracking."},
    {"name": "gas-analyzer-applications", "description": "Apply process gas analyzers including extractive and in-situ types for continuous emissions monitoring, flare gas analysis, and purity verification."},
    {"name": "lel-detection-systems", "description": "Deploy lower explosive limit detection systems including catalytic bead and infrared sensors for flammable gas area classification compliance."},
    {"name": "toxic-gas-monitoring", "description": "Monitor toxic gas levels including H2S, CO, NH3, and chlorine using electrochemical and photoionization detector technologies."},
    {"name": "confined-space-gas-testing", "description": "Execute confined space atmospheric testing programs including pre-entry testing protocols, continuous monitoring, and rescue gas detection systems."},
    {"name": "emission-monitoring-systems", "description": "Operate continuous emission monitoring systems including CEMS installation, QA/QC protocols, data acquisition, and regulatory reporting."},
    {"name": "gas-detection-maintenance", "description": "Maintain gas detection systems including sensor replacement intervals, zero and span calibration, functional testing, and documentation management."},
    {"name": "gas-detection-system-validation", "description": "Validate gas detection systems for process safety including SIL verification, proof testing intervals, and functional safety documentation."},
    {"name": "gas-chromatograph-operations", "description": "Operate industrial gas chromatographs for process gas composition analysis including column selection, carrier gas management, and calibration."},
]

# Domain: Leak Detection Technology
skills += [
    {"name": "helium-leak-testing-ops", "description": "Operate helium leak detection systems including mass spectrometer leak detectors, sniffer probes, and vacuum chamber test procedures."},
    {"name": "pressure-decay-leak-testing", "description": "Execute pressure decay leak testing including test fixture design, pressure measurement accuracy, temperature compensation, and reject limit setting."},
    {"name": "ultrasonic-leak-detection", "description": "Deploy ultrasonic leak detection for compressed air, steam, and gas systems including equipment selection, survey methodology, and repair prioritization."},
    {"name": "tracer-gas-leak-detection", "description": "Apply tracer gas methods for building envelope and HVAC leak detection including 5% H2/N2 mixture testing and refrigerant leak surveys."},
    {"name": "acoustic-emission-leak-detection", "description": "Use acoustic emission techniques for pressurized system leak detection including sensor placement, signal analysis, and leak sizing algorithms."},
    {"name": "water-leak-detection-systems", "description": "Deploy water leak detection systems including flow monitoring, acoustic correlators, and under-floor sensing for facility protection."},
    {"name": "pipeline-leak-detection-ops", "description": "Operate pipeline leak detection systems including mass balance methods, real-time transient modeling, and negative pressure wave detection."},
    {"name": "vacuum-system-leak-testing", "description": "Test vacuum system integrity including gross leak detection, residual gas analysis, and leak localization procedures for process equipment."},
    {"name": "leak-detection-regulatory-mgmt", "description": "Manage leak detection regulatory compliance including LDAR programs, Method 21 monitoring, refrigerant management, and reporting documentation."},
    {"name": "leak-test-equipment-calibration", "description": "Calibrate leak testing equipment including reference leak standards, detector sensitivity verification, and measurement uncertainty documentation."},
]

# Domain: Flame & Fire Detection Systems
skills += [
    {"name": "fire-alarm-system-design", "description": "Design fire alarm systems including detector placement, notification appliance circuits, panel programming, and NFPA 72 code compliance."},
    {"name": "flame-detector-selection", "description": "Select flame detectors including UV, IR, UV/IR, and multi-spectrum IR types for hazardous area classification and response time requirements."},
    {"name": "smoke-detection-systems", "description": "Design smoke detection systems including ionization, photoelectric, aspirating, and video smoke detection for facility protection."},
    {"name": "fire-suppression-systems", "description": "Design and manage fire suppression systems including clean agent, CO2, foam, and water mist systems for hazard area protection."},
    {"name": "fire-alarm-commissioning", "description": "Commission fire alarm and detection systems including device testing, sensitivity verification, panel programming validation, and authority acceptance."},
    {"name": "fire-system-inspection-testing", "description": "Execute fire system inspection and testing programs including annual ITM schedules, deficiency tracking, and certification documentation."},
    {"name": "hazard-area-fire-detection", "description": "Deploy fire detection in hazardous classified areas including ATEX/IECEx certified equipment, barrier design, and installation standards compliance."},
    {"name": "fire-detection-integration", "description": "Integrate fire detection with building automation, access control, and emergency response systems including protocol conversion and logic coordination."},
    {"name": "fire-risk-assessment-support", "description": "Support fire risk assessments including hazard identification, protection gap analysis, and improvement recommendations for facility fire safety."},
    {"name": "fire-detection-maintenance-mgmt", "description": "Manage fire detection maintenance programs including device cleaning intervals, battery replacement, firmware updates, and trouble log management."},
]

# Domain: Radar & Microwave Technology
skills += [
    {"name": "radar-system-engineering", "description": "Engineer radar systems including waveform design, antenna selection, signal processing algorithms, and range/Doppler performance analysis."},
    {"name": "microwave-component-manufacturing", "description": "Manufacture microwave components including waveguides, couplers, isolators, and circulators with RF characterization and hermetic sealing."},
    {"name": "radar-level-measurement", "description": "Apply radar level measurement instruments for process vessels including antenna selection, installation guidelines, and echo curve analysis."},
    {"name": "automotive-radar-ops", "description": "Develop and validate automotive radar systems including FMCW radar design, target detection algorithms, and functional safety compliance."},
    {"name": "weather-radar-operations", "description": "Operate weather radar systems including calibration procedures, clutter suppression, precipitation estimation, and data product generation."},
    {"name": "air-traffic-radar-maintenance", "description": "Maintain air traffic control radar systems including primary surveillance radar, secondary radar transponders, and performance monitoring."},
    {"name": "security-radar-systems", "description": "Deploy security perimeter radar systems including ground surveillance, drone detection, and coastal monitoring with target classification."},
    {"name": "radar-signal-processing-dev", "description": "Develop radar signal processing algorithms including CFAR detection, clutter filtering, tracking algorithms, and waveform optimization."},
    {"name": "rf-propagation-modeling", "description": "Model RF propagation for radar and communication systems including terrain diffraction, atmospheric refraction, and multipath analysis."},
    {"name": "radar-certification-testing", "description": "Manage radar product certification including FCC/ETSI authorization, radar performance standards compliance, and type approval documentation."},
]

# Domain: Satellite Technology
skills += [
    {"name": "satellite-bus-engineering", "description": "Engineer satellite bus systems including power subsystem, attitude control, thermal management, and command and data handling architecture."},
    {"name": "satellite-payload-integration", "description": "Integrate satellite payloads including RF transponders, optical sensors, and scientific instruments with interface control and test verification."},
    {"name": "ground-station-operations", "description": "Operate satellite ground stations including antenna tracking, telemetry processing, command uplink, and link budget management."},
    {"name": "satellite-mission-operations", "description": "Execute satellite mission operations including orbit maintenance maneuvers, payload scheduling, anomaly resolution, and end-of-life planning."},
    {"name": "satellite-communication-services", "description": "Manage satellite communication services including bandwidth allocation, VSAT network management, and service level agreement monitoring."},
    {"name": "earth-observation-data-ops", "description": "Operate earth observation data services including image acquisition tasking, processing pipelines, and geospatial product delivery."},
    {"name": "small-sat-cubesat-development", "description": "Develop small satellite and CubeSat missions including standardized bus selection, rideshare procurement, and miniaturized subsystem integration."},
    {"name": "satellite-frequency-coordination", "description": "Manage satellite frequency coordination including ITU filing procedures, interference analysis, and EPFD compliance for non-geostationary orbits."},
    {"name": "launch-vehicle-coordination", "description": "Coordinate satellite launch vehicle services including manifest negotiation, payload adapter design, launch campaign management, and post-launch status."},
    {"name": "space-debris-compliance", "description": "Manage space debris compliance including orbital lifetime analysis, deorbit propulsion design, and FCC and ITU debris mitigation requirements."},
]

# Domain: Power Quality & Protection
skills += [
    {"name": "power-quality-monitoring", "description": "Monitor power quality parameters including voltage sags, swells, harmonics, flicker, and transients using class A and S instruments."},
    {"name": "harmonic-filter-design", "description": "Design harmonic filters including passive LC filters, active filters, and hybrid configurations for IEEE 519 compliance in industrial facilities."},
    {"name": "power-factor-correction-ops", "description": "Operate power factor correction systems including fixed capacitor banks, automatic regulators, and detuned filter banks for utility penalty avoidance."},
    {"name": "ups-system-management", "description": "Manage UPS system operations including battery testing schedules, bypass procedures, load management, and runtime verification."},
    {"name": "surge-protection-programs", "description": "Design surge protection programs including SPD selection, cascading coordination, and installation requirements for facility and equipment protection."},
    {"name": "grounding-earthing-systems", "description": "Design and verify grounding and earthing systems including ground grid resistance measurement, soil resistivity testing, and arc flash mitigation."},
    {"name": "protective-relay-management", "description": "Manage protective relay programs including settings calculations, coordination studies, testing procedures, and event record analysis."},
    {"name": "arc-flash-hazard-analysis", "description": "Conduct arc flash hazard analyses including incident energy calculation, PPE category assignment, and equipment labeling per NFPA 70E."},
    {"name": "power-monitoring-systems", "description": "Deploy power monitoring systems including energy meters, sub-metering networks, and utility billing verification for facility energy management."},
    {"name": "electrical-power-system-studies", "description": "Perform electrical power system studies including load flow, short circuit, motor starting, and reliability analysis for facility design."},
]

# Domain: Cable & Wire Products Manufacturing
skills += [
    {"name": "wire-cable-product-engineering", "description": "Engineer wire and cable products including conductor sizing, insulation material selection, shielding design, and jacket specification."},
    {"name": "cable-manufacturing-ops", "description": "Manage cable manufacturing operations including extrusion line setup, stranding processes, armoring, and electrical test procedures."},
    {"name": "cable-specification-compliance", "description": "Navigate cable specification compliance including UL, CSA, VDE, and IEC standards for listing, certification, and approval documentation."},
    {"name": "cable-assembly-manufacturing", "description": "Manage cable assembly manufacturing including crimp tooling qualification, connector assembly, continuity testing, and custom harness production."},
    {"name": "specialty-cable-development", "description": "Develop specialty cable products including high-temperature, chemical-resistant, fire-resistant, and subsea cable designs for demanding environments."},
    {"name": "cable-raw-material-sourcing", "description": "Source cable raw materials including copper rod, aluminum, insulation compounds, and jacketing materials with incoming quality verification."},
    {"name": "cable-installation-services", "description": "Manage cable installation services including pulling tension calculations, conduit fill verification, splicing procedures, and acceptance testing."},
    {"name": "fiber-optic-cable-manufacturing", "description": "Manufacture fiber optic cables including draw tower operations, secondary coating, cabling, and OTDR characterization for telecom and industrial use."},
    {"name": "cable-product-lifecycle-mgmt", "description": "Manage cable product lifecycle including new product introductions, material substitutions, RoHS compliance, and obsolescence planning."},
    {"name": "cable-testing-lab-operations", "description": "Operate cable testing laboratories including high voltage, flame propagation, cold bend, and crush resistance testing per industry standards."},
]

# Domain: Electrical Enclosures & Panels
skills += [
    {"name": "enclosure-design-engineering", "description": "Design electrical enclosures including thermal management, IP rating selection, gland plate sizing, and structural integrity for industrial environments."},
    {"name": "control-panel-fabrication", "description": "Fabricate control panels including component layout design, wire management, DIN rail mounting, and UL 508A industrial panel standards compliance."},
    {"name": "enclosure-thermal-management", "description": "Manage enclosure thermal design including heat dissipation calculation, cooling unit selection, air conditioning, and heat exchanger specification."},
    {"name": "hazardous-area-enclosures", "description": "Design hazardous area electrical enclosures including flameproof, purged and pressurized, and increased safety types for ATEX and NEC compliance."},
    {"name": "enclosure-corrosion-protection", "description": "Select enclosure corrosion protection including stainless steel, GRP, and polycarbonate materials with coating systems for harsh environment service."},
    {"name": "panel-wiring-documentation", "description": "Create panel wiring documentation including schematics, terminal strip layouts, bill of materials, and AS-built drawing management."},
    {"name": "switchgear-assembly-ops", "description": "Assemble low and medium voltage switchgear including busbar sizing, breaker coordination, protective relay installation, and factory testing."},
    {"name": "mcc-motor-control-center-ops", "description": "Design and manage motor control centers including starter selection, variable frequency drive coordination, and feeder protection coordination."},
    {"name": "enclosure-product-certification", "description": "Manage enclosure product certifications including UL, NEMA, IEC 60529, and cULus listings with production quality control documentation."},
    {"name": "panel-shop-quality-management", "description": "Implement quality management in panel shops including incoming inspection, in-process checks, final acceptance testing, and customer witness testing."},
]

# Domain: Lifting & Rigging Equipment
skills += [
    {"name": "overhead-crane-operations", "description": "Manage overhead crane operations including operator qualification, pre-use inspections, lift planning, and ASME B30.2 standards compliance."},
    {"name": "below-hook-lifting-devices", "description": "Design and manage below-the-hook lifting devices including spreader bars, lifting beams, and custom fixtures with load testing and certification."},
    {"name": "rigging-equipment-management", "description": "Manage rigging equipment programs including wire rope slings, chain slings, web slings, and shackle inspection, certification, and retirement."},
    {"name": "hoist-selection-maintenance", "description": "Select and maintain hoists including electric chain hoists, wire rope hoists, and manual hoists with load testing and brake inspection programs."},
    {"name": "critical-lift-planning", "description": "Plan critical lifts including lift plan preparation, crane capacity verification, ground bearing assessment, and multi-crane coordination."},
    {"name": "forklift-fleet-management", "description": "Manage forklift fleet operations including operator certification, pre-shift inspections, battery maintenance, and utilization tracking."},
    {"name": "pallet-rack-safety-programs", "description": "Manage pallet rack safety programs including load rating display, damage inspection protocols, repair approval, and seismic anchorage compliance."},
    {"name": "lifting-equipment-inspection", "description": "Conduct lifting equipment inspections including periodic examination, NDT testing, load testing, and documentation per ASME B30 and LEEA standards."},
    {"name": "scissor-lift-boom-lift-mgmt", "description": "Manage aerial work platform programs including operator training, pre-use inspections, fall protection integration, and ANSI A92 standards compliance."},
    {"name": "rigging-training-programs", "description": "Develop rigging and lifting training programs including signal person certification, qualified rigger programs, and practical competency assessment."},
]

# Domain: Pallet Racking & Storage Systems
skills += [
    {"name": "warehouse-storage-design", "description": "Design warehouse storage systems including selective rack, drive-in, push-back, and flow rack configurations for throughput and density optimization."},
    {"name": "automated-storage-retrieval-ops", "description": "Operate automated storage and retrieval systems including unit-load and mini-load ASRS, shuttle systems, and vertical lift modules."},
    {"name": "mezzanine-system-design", "description": "Design mezzanine structures including structural calculations, floor loading, column placement, safety netting, and stair access configuration."},
    {"name": "cantilever-rack-management", "description": "Manage cantilever rack systems for long load storage including arm capacity ratings, column bracing, and row protection requirements."},
    {"name": "shelving-system-operations", "description": "Manage industrial shelving systems including static, mobile, and carton flow configurations with weight capacity and maintenance programs."},
    {"name": "rack-installation-supervision", "description": "Supervise rack installation including anchor bolt installation, frame plumb verification, beam connector engagement, and load capacity labeling."},
    {"name": "rack-inspection-programs", "description": "Conduct periodic rack inspection programs including damage classification, repair authorization, and ANSI MH16.1 standards compliance documentation."},
    {"name": "warehouse-layout-optimization", "description": "Optimize warehouse layout including slotting analysis, travel path simulation, throughput modeling, and SKU velocity segmentation."},
    {"name": "cold-storage-racking-systems", "description": "Design and manage cold storage racking systems including galvanized finishes, thermal movement allowances, and freezer-grade hardware specifications."},
    {"name": "rack-safety-colosseum-programs", "description": "Implement rack safety programs including load signage requirements, forklift operator awareness, collision damage repair procedures, and engineering reviews."},
]

# Domain: Conveyor Accessories & Components
skills += [
    {"name": "conveyor-belt-selection", "description": "Select conveyor belts including rubber, PVC, PU, and fabric types for tensile strength, temperature, chemical compatibility, and food grade requirements."},
    {"name": "conveyor-idler-roller-mgmt", "description": "Manage conveyor idler and roller programs including trough angle selection, CEMA load ratings, bearing replacement, and misalignment correction."},
    {"name": "conveyor-belt-splicing-ops", "description": "Execute conveyor belt splicing operations including mechanical fasteners, vulcanized splices, and endless belt fabrication procedures."},
    {"name": "conveyor-drive-system-ops", "description": "Manage conveyor drive systems including head pulley lagging, gearmotor selection, variable speed drives, and backstop installation."},
    {"name": "conveyor-belt-tracking", "description": "Manage conveyor belt tracking including crowned pulley adjustment, training idler installation, and belt edge monitoring systems."},
    {"name": "conveyor-cleaning-systems", "description": "Design and maintain conveyor cleaning systems including primary and secondary scrapers, wash boxes, and plows for carryback elimination."},
    {"name": "conveyor-weigh-feeding-ops", "description": "Operate conveyor weigh feeders and belt scales including calibration procedures, PID tuning, and rate accuracy verification."},
    {"name": "conveyor-dust-control-systems", "description": "Implement conveyor dust control systems including enclosures, transfer point hoods, wet suppression, and dry fog systems for regulatory compliance."},
    {"name": "conveyor-fire-detection-protection", "description": "Deploy fire detection and protection for conveyor systems including infrared sensors, CO monitoring, water deluge, and automatic shutdown integration."},
    {"name": "conveyor-safety-guarding", "description": "Design conveyor safety guarding including nip point protection, tail pulley guards, emergency stop pull-cord systems, and zero-speed switches."},
]

# Domain: Wire Rope & Chain Products
skills += [
    {"name": "wire-rope-selection-engineering", "description": "Select wire ropes including 6-strand, rotation-resistant, and compacted strand types for breaking strength, fatigue life, and bending requirements."},
    {"name": "wire-rope-inspection-programs", "description": "Conduct wire rope inspection programs including visual examination, magnetic flux leakage testing, and retirement criteria per ASME B30.5."},
    {"name": "wire-rope-termination-ops", "description": "Fabricate wire rope terminations including swaged sockets, spelter sockets, wedge sockets, and mechanical splices with proof load testing."},
    {"name": "chain-sling-management", "description": "Manage chain sling programs including alloy grade verification, link inspection, proof testing, and annual thorough examination documentation."},
    {"name": "mooring-chain-operations", "description": "Manage offshore mooring chain operations including fatigue monitoring, corrosion protection, inspection campaigns, and replacement planning."},
    {"name": "chain-conveyor-maintenance", "description": "Maintain chain conveyor systems including elongation measurement, lubrication programs, sprocket wear monitoring, and replacement scheduling."},
    {"name": "anchor-chain-management", "description": "Manage anchor chain programs including grade verification, end connection inspection, windlass compatibility, and classification society surveys."},
    {"name": "rigging-hardware-management", "description": "Manage rigging hardware programs including shackles, hooks, rings, and turnbuckles with proof load verification and working load limit labeling."},
    {"name": "wire-rope-lubrication-ops", "description": "Execute wire rope lubrication programs including internal and external lubricant application, penetration verification, and corrosion protection assessment."},
    {"name": "synthetic-rope-applications", "description": "Apply high-performance synthetic ropes including HMPE, aramid, and polyester types for lifting, mooring, and traction applications with care guidelines."},
]

# Domain: Eye Bolts, Shackles & Lifting Hardware
skills += [
    {"name": "eyebolt-eye-nut-selection", "description": "Select eyebolts and eye nuts including angular load capacity ratings, swivel designs, and shoulder versus non-shoulder types for lifting compliance."},
    {"name": "shackle-selection-programs", "description": "Select and manage shackles including anchor, chain, and screw pin types with working load limit verification and marking inspection programs."},
    {"name": "turnbuckle-tensioning-ops", "description": "Apply turnbuckles for rigging tension adjustment including load capacity selection, thread engagement verification, and locking safety requirements."},
    {"name": "hoist-ring-applications", "description": "Apply hoist rings and swivel hoist rings including machined hole requirements, angular load ratings, and installation torque specifications."},
    {"name": "lifting-point-engineering", "description": "Engineer lifting point selections for machinery and equipment including load path analysis, structural adequacy verification, and proof testing."},
    {"name": "carabiner-snap-hook-safety", "description": "Manage carabiner and snap hook programs for fall protection including gate strength verification, locking mechanism inspection, and retirement criteria."},
    {"name": "load-securing-hardware-mgmt", "description": "Manage load securing hardware including ratchet straps, load binders, and dunnage systems for transport compliance and cargo protection."},
    {"name": "rigging-hardware-testing", "description": "Conduct rigging hardware proof testing including load application procedures, elongation measurement, and documentation for certification."},
    {"name": "hardware-traceability-programs", "description": "Manage lifting hardware traceability programs including heat number marking, certification documentation, and lot identification for audit compliance."},
    {"name": "hardware-failure-investigation", "description": "Investigate lifting hardware failures including fracture analysis, overload assessment, corrosion evaluation, and corrective action recommendations."},
]

# Domain: Thermal Management Products
skills += [
    {"name": "heat-sink-design-engineering", "description": "Design heat sinks including fin optimization, base thickness analysis, thermal resistance calculation, and manufacturing method selection."},
    {"name": "thermal-interface-material-selection", "description": "Select thermal interface materials including phase change pads, grease, graphite, and gap fillers for thermal resistance and assembly process requirements."},
    {"name": "liquid-cooling-system-design", "description": "Design liquid cooling systems for electronics including cold plate design, pump selection, fluid chemistry, and leak detection integration."},
    {"name": "heat-pipe-vapor-chamber-apps", "description": "Apply heat pipes and vapor chambers for electronics thermal management including orientation sensitivity, power limits, and integration guidelines."},
    {"name": "thermoelectric-cooler-apps", "description": "Apply thermoelectric coolers for precision temperature control including COP optimization, current tuning, and cascade stage design."},
    {"name": "immersion-cooling-ops", "description": "Operate immersion cooling systems for high-density electronics including dielectric fluid management, maintenance procedures, and capacity scaling."},
    {"name": "thermal-simulation-analysis", "description": "Conduct thermal simulations using CFD and FEA tools for electronics cooling design validation, hotspot identification, and design optimization."},
    {"name": "thermal-pad-sheet-manufacturing", "description": "Manage thermal pad and sheet manufacturing including compound mixing, calendering, thickness control, and thermal conductivity testing."},
    {"name": "data-center-cooling-ops", "description": "Operate data center cooling systems including CRAC units, in-row cooling, rear door heat exchangers, and hot aisle/cold aisle containment."},
    {"name": "thermal-management-testing", "description": "Conduct thermal management testing including thermal resistance measurement, junction temperature verification, and accelerated thermal cycling."},
]

# Domain: Adhesive & Bonding Technology
skills += [
    {"name": "structural-adhesive-selection", "description": "Select structural adhesives including epoxy, acrylic, polyurethane, and methyl methacrylate types for substrate compatibility and load requirements."},
    {"name": "adhesive-joint-design", "description": "Design adhesive joints including overlap length optimization, stress concentration reduction, and surface preparation requirements for joint strength."},
    {"name": "pressure-sensitive-adhesive-ops", "description": "Manage pressure-sensitive adhesive applications including tape selection, peel and shear testing, and dispensing system optimization."},
    {"name": "adhesive-dispensing-systems", "description": "Design adhesive dispensing systems including bead dispensing, jet valves, spray systems, and meter-mix dispensers for production applications."},
    {"name": "adhesive-curing-process-dev", "description": "Develop adhesive curing processes including UV curing system design, heat cure oven profiling, and moisture cure environment control."},
    {"name": "surface-preparation-programs", "description": "Manage surface preparation programs for bonding including mechanical abrasion, chemical cleaning, plasma treatment, and primer application."},
    {"name": "adhesive-testing-qualification", "description": "Qualify adhesive materials and processes including lap shear, peel, torsion, and environmental aging tests for production release."},
    {"name": "hot-melt-adhesive-systems", "description": "Operate hot melt adhesive systems including tank temperature management, hose maintenance, nozzle cleaning, and application weight control."},
    {"name": "anaerobic-sealant-applications", "description": "Apply anaerobic thread lockers, pipe sealants, and retaining compounds with cure speed selection, gap filling requirements, and removal procedures."},
    {"name": "adhesive-failure-analysis", "description": "Investigate adhesive bond failures including locus of failure determination, surface contamination analysis, and process root cause investigation."},
]

# Domain: Industrial Cleaning Technology
skills += [
    {"name": "aqueous-cleaning-system-ops", "description": "Operate aqueous parts cleaning systems including detergent chemistry management, rinsing stages, water treatment, and cleanliness verification."},
    {"name": "ultrasonic-cleaning-applications", "description": "Apply ultrasonic cleaning for precision parts including frequency selection, power density optimization, and basket loading for effective cavitation."},
    {"name": "vapor-degreasing-operations", "description": "Operate vapor degreasing systems including solvent management, vapor zone temperature control, and compliant solvent selection for cleaning performance."},
    {"name": "industrial-pressure-washing", "description": "Manage industrial pressure washing programs including equipment selection, detergent mixing ratios, wastewater containment, and operator safety protocols."},
    {"name": "dry-ice-blasting-ops", "description": "Operate dry ice blasting systems for industrial cleaning including blast pressure optimization, nozzle selection, and substrate compatibility assessment."},
    {"name": "industrial-floor-cleaning-ops", "description": "Operate industrial floor cleaning equipment including sweepers, scrubbers, and burnishers with chemical selection and waste water management."},
    {"name": "tank-vessel-cleaning-ops", "description": "Manage tank and vessel cleaning operations including cleaning-in-place systems, confined space procedures, and food grade sanitization protocols."},
    {"name": "clean-room-cleaning-programs", "description": "Execute cleanroom cleaning programs including disinfection procedures, particle monitoring verification, cleaning agent compatibility, and gowning protocols."},
    {"name": "industrial-laundry-ops", "description": "Operate industrial laundry services including workwear contamination management, detergent programs, and garment tracking for hazardous material handling."},
    {"name": "cleaning-validation-programs", "description": "Validate industrial cleaning processes including residue testing methods, acceptance criteria, swabbing procedures, and regulatory documentation."},
]

# Domain: Lubrication Technology Services
skills += [
    {"name": "lubrication-program-design", "description": "Design plant lubrication programs including lubricant standardization, application frequency, quantities, and delivery method specification."},
    {"name": "oil-analysis-programs", "description": "Operate oil analysis programs including sampling frequency, laboratory test panel selection, trend analysis, and actionable alert management."},
    {"name": "lubricant-storage-handling", "description": "Manage lubricant storage and handling including contamination prevention, labeling, FIFO rotation, dispensing equipment, and disposal compliance."},
    {"name": "automatic-lubrication-systems", "description": "Design and maintain automatic lubrication systems including single-line and dual-line systems, pump sizing, and distribution block selection."},
    {"name": "grease-selection-programs", "description": "Select greases for machinery applications including thickener type, consistency, extreme pressure additives, and temperature range requirements."},
    {"name": "lubrication-training-programs", "description": "Develop lubrication training programs including ICML certification preparation, application technique training, and contamination control awareness."},
    {"name": "filtration-kidney-loop-systems", "description": "Design and operate kidney loop filtration systems including filter sizing, flow rate calculation, and target cleanliness level achievement."},
    {"name": "food-grade-lubrication-mgmt", "description": "Manage food-grade lubrication programs including H1 and H2 lubricant selection, documentation requirements, and NSF registration verification."},
    {"name": "synthetic-lubricant-programs", "description": "Implement synthetic lubricant conversion programs including compatibility assessment, flush procedures, extended drain interval validation, and cost justification."},
    {"name": "lubrication-reliability-mgmt", "description": "Manage lubrication as a reliability discipline including contamination control targets, lubricant health monitoring, and program audit procedures."},
]

# Domain: Precision Fasteners Manufacturing
skills += [
    {"name": "fastener-engineering-selection", "description": "Select fasteners including bolts, screws, nuts, and washers with material grade, coating, thread specification, and torque requirement analysis."},
    {"name": "fastener-manufacturing-ops", "description": "Manage fastener manufacturing operations including cold heading, thread rolling, heat treatment, and coating application processes."},
    {"name": "fastener-quality-inspection", "description": "Inspect fasteners including dimensional measurement, mechanical property testing, coating thickness, and hydrogen embrittlement verification."},
    {"name": "torque-tension-management", "description": "Manage bolt torque and tension programs including torque specification development, tool calibration, joint integrity verification, and training."},
    {"name": "fastener-corrosion-protection", "description": "Select fastener corrosion protection including zinc plating, hot-dip galvanizing, stainless steel, and aluminum types for service environment requirements."},
    {"name": "structural-fastener-programs", "description": "Manage structural fastener programs including AISC approved bolts, installation inspection, pretension verification, and documentation for steel construction."},
    {"name": "aerospace-fastener-ops", "description": "Manage aerospace fastener programs including AS9100 quality requirements, traceability, installation tooling calibration, and inspection documentation."},
    {"name": "fastener-distribution-ops", "description": "Operate fastener distribution programs including consignment inventory, vendor-managed inventory, bin stocking, and kitting services."},
    {"name": "threaded-insert-applications", "description": "Apply threaded inserts including coiled wire, key-locking, and pressed-in types for thread repair, soft material reinforcement, and removable joint design."},
    {"name": "fastener-failure-analysis", "description": "Analyze fastener failures including hydrogen embrittlement, stress corrosion, fatigue fracture, and improper installation with corrective action."},
]

# Domain: Sealing Technology Services
skills += [
    {"name": "o-ring-seal-selection", "description": "Select O-rings and seals including material compound, hardness, and size for operating pressure, temperature, and fluid compatibility requirements."},
    {"name": "mechanical-seal-programs", "description": "Manage mechanical seal programs for rotating equipment including seal selection, installation procedures, flush plan implementation, and failure analysis."},
    {"name": "hydraulic-pneumatic-seal-mgmt", "description": "Manage hydraulic and pneumatic seal programs including rod and piston seal selection, groove dimension verification, and replacement scheduling."},
    {"name": "gasket-selection-programs", "description": "Select gaskets including spiral wound, kammprofile, sheet, and ring type joints for flange standards, operating conditions, and leak tightness."},
    {"name": "flange-management-programs", "description": "Manage flange assembly programs including bolt torque specifications, gasket seating stress calculations, and controlled tightening documentation."},
    {"name": "rotary-lip-seal-applications", "description": "Apply rotary shaft lip seals including radial shaft seal selection, shaft speed and surface finish requirements, and housing bore tolerances."},
    {"name": "custom-seal-development", "description": "Develop custom sealing solutions including compound formulation, mold design, prototype testing, and production qualification for specialty applications."},
    {"name": "seal-failure-investigation", "description": "Investigate seal failures including extrusion, spiral failure, chemical attack, and thermal degradation with corrective action recommendations."},
    {"name": "sealing-product-testing", "description": "Conduct seal testing including pressure cycling, extrusion resistance, fluid compatibility, and temperature testing for product qualification."},
    {"name": "pipe-fitting-thread-sealing", "description": "Manage thread sealing programs including PTFE tape application, anaerobic pipe sealant selection, and pressure test verification procedures."},
]

# Domain: Spring Technology Manufacturing
skills += [
    {"name": "compression-spring-design", "description": "Design compression springs including wire diameter, coil diameter, free length, and spring rate calculation with fatigue life analysis."},
    {"name": "extension-spring-engineering", "description": "Engineer extension springs including initial tension, hook stress analysis, and extended length specification for tension application requirements."},
    {"name": "torsion-spring-design", "description": "Design torsion springs including coil winding direction, leg geometry, angular deflection, and torque output for rotational application needs."},
    {"name": "disc-spring-washer-apps", "description": "Apply disc springs and Belleville washers for bolt preload maintenance, overload protection, and precision load applications with stack configuration."},
    {"name": "constant-force-spring-ops", "description": "Apply constant force springs for retraction mechanisms, counterbalancing, and cable management with force output and cycle life requirements."},
    {"name": "spring-material-selection", "description": "Select spring materials including hard drawn wire, oil tempered wire, stainless steel, and exotic alloys for stress, corrosion, and temperature requirements."},
    {"name": "spring-surface-finishing", "description": "Manage spring surface finishing including shot peening, stress relief, passivation, coating, and plating programs for fatigue and corrosion improvement."},
    {"name": "spring-quality-testing", "description": "Test spring quality including rate measurement, free height verification, load testing at specified heights, and fatigue life testing programs."},
    {"name": "custom-spring-development", "description": "Develop custom springs including prototype iterations, material substitution testing, and production tooling qualification for specialty applications."},
    {"name": "spring-inventory-management", "description": "Manage spring inventory programs including standard catalog stocking, custom order tracking, and just-in-time delivery programs."},
]

# Domain: Noise Barriers & Acoustic Products
skills += [
    {"name": "noise-barrier-wall-design", "description": "Design noise barrier walls including material selection, height optimization, insertion loss prediction, and structural foundation requirements."},
    {"name": "acoustic-enclosure-design", "description": "Design acoustic enclosures for machinery noise control including panel transmission loss, access door design, and ventilation noise treatment."},
    {"name": "hvac-duct-silencer-apps", "description": "Apply HVAC duct silencers including splitter, cylindrical, and elbow types with insertion loss and pressure drop selection criteria."},
    {"name": "exhaust-silencer-design", "description": "Design exhaust silencers for generators, compressors, and engines including reactive and absorptive designs with back pressure and attenuation requirements."},
    {"name": "acoustic-foam-applications", "description": "Apply acoustic foams including open cell polyurethane, melamine, and polyimide types for absorption, vibration damping, and barrier applications."},
    {"name": "vibration-isolation-systems", "description": "Design vibration isolation systems including anti-vibration mounts, spring isolators, and inertia bases for machinery noise and vibration control."},
    {"name": "acoustic-panel-manufacturing", "description": "Manufacture acoustic panels including absorber, diffuser, and composite barrier designs with fire rating compliance and aesthetic finish options."},
    {"name": "noise-control-product-testing", "description": "Test noise control products including transmission loss (ASTM E90), absorption (ASTM C423), and vibration isolation efficiency measurements."},
    {"name": "industrial-hearing-protection", "description": "Manage industrial hearing protection programs including NRR rating selection, fit testing, dual protection programs, and worker acceptance improvement."},
    {"name": "acoustic-product-certification", "description": "Navigate acoustic product certifications including UL fire ratings, STC and IIC ratings, and environmental product declarations for sustainable construction."},
]

# Domain: Marking & Labeling Technology
skills += [
    {"name": "industrial-marking-systems", "description": "Manage industrial product marking systems including dot-peen, laser, inkjet, and electrochemical etching for part traceability and identification."},
    {"name": "label-design-management", "description": "Design and manage product labels including material selection, adhesive specification, print quality, and regulatory compliance for diverse environments."},
    {"name": "barcode-label-printing-ops", "description": "Operate barcode label printing systems including thermal transfer printers, ribbon management, media selection, and print quality verification."},
    {"name": "direct-part-marking-programs", "description": "Implement direct part marking programs including 2D data matrix codes, laser parameters, and IAQG OASIS verification for aerospace traceability."},
    {"name": "rfid-label-integration", "description": "Integrate RFID smart labels into labeling operations including inlay selection, encoding verification, and read range validation procedures."},
    {"name": "label-applicator-systems", "description": "Operate label applicator systems including tamp-blow, wipe-on, and wrap-around configurations with sensor feedback and reject management."},
    {"name": "regulatory-label-compliance", "description": "Ensure regulatory label compliance including GHS/SDS hazard communication, REACH substance declarations, and country-specific language requirements."},
    {"name": "color-management-printing", "description": "Manage color in industrial printing operations including ICC profile management, delta-E color measurement, and brand color consistency programs."},
    {"name": "serialized-label-programs", "description": "Manage serialized labeling programs including sequential numbering systems, track-and-trace integration, and anti-counterfeiting feature management."},
    {"name": "label-material-qualification", "description": "Qualify label materials for specific environments including outdoor weathering, chemical resistance, temperature extremes, and adhesion testing programs."},
]

# Domain: Rope Access Technology
skills += [
    {"name": "rope-access-program-management", "description": "Manage rope access work programs including IRATA or SPRAT technician certification, equipment inspection, work planning, and supervisor oversight."},
    {"name": "industrial-rope-access-ops", "description": "Execute industrial rope access operations for maintenance, inspection, and installation work on structures, towers, and vessels at height."},
    {"name": "rope-access-equipment-mgmt", "description": "Manage rope access equipment including harness inspection, rope life tracking, descender service, and anchorage device certification programs."},
    {"name": "rope-access-rescue-planning", "description": "Plan rope access rescue procedures including rescue kit configuration, evacuation route identification, and emergency response drills."},
    {"name": "wind-turbine-rope-access", "description": "Conduct rope access work on wind turbines including blade inspection, nacelle access, tower painting, and component replacement operations."},
    {"name": "bridge-rope-access-inspection", "description": "Perform bridge inspection using rope access including cable stay inspection, deck underside examination, and underwater pier assessment."},
    {"name": "offshore-rope-access-ops", "description": "Execute offshore rope access operations on platforms and vessels including corrosion inspection, coating repair, and structural survey work."},
    {"name": "facade-rope-access-services", "description": "Provide building facade services using rope access including curtain wall inspection, window cleaning, caulking, and remedial repair work."},
    {"name": "rope-access-ndt-inspection", "description": "Conduct non-destructive testing using rope access including ultrasonic thickness measurement, magnetic particle, and visual inspection at height."},
    {"name": "rope-access-contractor-mgmt", "description": "Manage rope access contractor programs including competency verification, method statement review, and safety performance monitoring."},
]

# Domain: Tank & Vessel Services
skills += [
    {"name": "tank-inspection-programs", "description": "Manage storage tank inspection programs including API 653 assessments, floor scanning, shell thickness measurement, and corrosion rate analysis."},
    {"name": "tank-repair-operations", "description": "Execute tank repair operations including floor plate replacement, shell weld repair, roof repair, and nozzle addition procedures."},
    {"name": "tank-lining-coating-ops", "description": "Apply tank linings and coatings including surface preparation, coating system selection, application procedures, and holiday detection testing."},
    {"name": "pressure-vessel-inspection", "description": "Conduct pressure vessel inspections per NBIC and API 510 including internal and external visual, ultrasonic thickness, and NDE examination programs."},
    {"name": "tank-cleaning-degassing-ops", "description": "Execute tank cleaning and degassing operations including entry procedures, vapor monitoring, cleaning methods, and waste disposal coordination."},
    {"name": "tank-calibration-gauging", "description": "Calibrate storage tanks for custody transfer including strapping surveys, capacity tables, and weights and measures certification programs."},
    {"name": "tank-cathodic-protection", "description": "Manage cathodic protection for storage tanks and buried pipelines including impressed current systems, survey procedures, and corrosion engineer oversight."},
    {"name": "vessel-integrity-management", "description": "Manage pressure vessel integrity programs including risk-based inspection scheduling, remaining life assessment, and fitness-for-service evaluation."},
    {"name": "cryogenic-tank-operations", "description": "Operate cryogenic storage tank systems including LN2, LO2, and LNG tanks with boil-off management, safety valve testing, and transfer operations."},
    {"name": "tank-asset-database-mgmt", "description": "Manage tank asset databases including inspection history records, thickness measurement data trending, and regulatory documentation archives."},
]

# Domain: Industrial Filtration Services
skills += [
    {"name": "dust-collector-operations", "description": "Operate industrial dust collection systems including baghouse, cartridge, and cyclone collectors with differential pressure monitoring and bag replacement."},
    {"name": "liquid-filtration-systems", "description": "Design and operate liquid filtration systems including cartridge, bag, and membrane filters for process fluids, cooling water, and waste treatment."},
    {"name": "mist-collector-systems", "description": "Operate mist collection systems for machining and grinding operations including coalescing filters, electrostatic precipitators, and media maintenance."},
    {"name": "air-filtration-hvac-ops", "description": "Manage HVAC air filtration programs including MERV rating selection, filter loading monitoring, replacement scheduling, and indoor air quality verification."},
    {"name": "industrial-vacuum-systems", "description": "Operate industrial vacuum systems including central vacuum, pneumatic conveying, and HEPA-filtered vacuums for material recovery and housekeeping."},
    {"name": "reverse-osmosis-operations", "description": "Operate reverse osmosis water purification systems including membrane cleaning protocols, SDI testing, reject management, and permeate quality monitoring."},
    {"name": "process-filtration-validation", "description": "Validate process filtration systems for pharmaceutical and food applications including integrity testing, extractable studies, and regulatory documentation."},
    {"name": "filter-media-selection", "description": "Select filter media including woven, nonwoven, and membrane types for particle retention rating, flow resistance, and chemical compatibility."},
    {"name": "filtration-cost-optimization", "description": "Optimize filtration system costs including filter life extension programs, alternative media evaluation, and total cost of ownership analysis."},
    {"name": "separator-coalescer-ops", "description": "Operate separator and coalescer systems for oil-water separation, gas-liquid separation, and aerosol removal in process and utility applications."},
]

# Domain: Waste Treatment Technology
skills += [
    {"name": "wastewater-treatment-ops", "description": "Operate industrial wastewater treatment systems including primary, secondary, and tertiary treatment with effluent permit compliance monitoring."},
    {"name": "chemical-treatment-programs", "description": "Manage chemical treatment programs for cooling water, boiler water, and process water including dosing control and chemistry monitoring."},
    {"name": "sludge-dewatering-management", "description": "Manage sludge dewatering operations including centrifuge, filter press, and belt press equipment with polymer dosing and cake quality monitoring."},
    {"name": "hazardous-waste-management", "description": "Manage hazardous waste programs including waste characterization, manifest documentation, approved disposal facility coordination, and RCRA compliance."},
    {"name": "zero-liquid-discharge-ops", "description": "Operate zero liquid discharge systems including evaporator operations, crystallizer management, and solids handling for resource recovery."},
    {"name": "biogas-recovery-operations", "description": "Operate biogas recovery systems including anaerobic digester management, gas treatment, compression, and utilization for combined heat and power."},
    {"name": "landfill-gas-management", "description": "Manage landfill gas collection and control systems including collection header networks, blower operations, flare management, and beneficial use programs."},
    {"name": "water-reuse-programs", "description": "Implement industrial water reuse programs including reclaimed water quality requirements, distribution systems, and end-use application qualification."},
    {"name": "effluent-monitoring-reporting", "description": "Manage effluent monitoring and reporting programs including sampling schedules, analytical methods, DMR preparation, and permit exceedance response."},
    {"name": "industrial-ecology-programs", "description": "Develop industrial ecology programs including waste exchange, by-product synergy identification, and circular economy implementation for waste reduction."},
]

# Domain: Corrosion Engineering Services
skills += [
    {"name": "corrosion-inspection-programs", "description": "Manage corrosion inspection programs including visual examination, ultrasonic testing, radiography, and corrosion mapping for asset integrity."},
    {"name": "corrosion-control-engineering", "description": "Develop corrosion control programs including material selection, coating specifications, cathodic protection, and inhibitor treatment programs."},
    {"name": "internal-corrosion-management", "description": "Manage internal corrosion in pipelines and vessels including risk assessment, coupon programs, inline inspection, and chemical inhibition."},
    {"name": "coating-inspection-services", "description": "Conduct protective coating inspections including surface preparation verification, dry film thickness, holiday detection, and adhesion testing."},
    {"name": "cathodic-protection-engineering", "description": "Engineer cathodic protection systems including galvanic anode design, impressed current systems, interference testing, and criteria verification."},
    {"name": "corrosion-failure-analysis", "description": "Analyze corrosion failures including failure mode determination, metallurgical examination, environmental cause identification, and prevention recommendations."},
    {"name": "materials-selection-consulting", "description": "Provide materials selection consulting for process equipment including corrosion allowance specification, alloy selection, and material qualification testing."},
    {"name": "risk-based-inspection-programs", "description": "Develop risk-based inspection programs for process equipment including consequence of failure analysis, probability assessment, and inspection interval optimization."},
    {"name": "corrosion-monitoring-technology", "description": "Deploy corrosion monitoring technologies including online electrochemical sensors, corrosion probes, and smart coupon systems with data management."},
    {"name": "fitness-for-service-assessment", "description": "Conduct fitness-for-service assessments per API 579 for corroded equipment including remaining strength calculations and repair decision support."},
]

# Domain: NDT / Non-Destructive Testing Services
skills += [
    {"name": "ultrasonic-testing-ops", "description": "Conduct ultrasonic testing including pulse-echo, TOFD, and phased array techniques for weld inspection, thickness measurement, and flaw characterization."},
    {"name": "radiographic-testing-ops", "description": "Manage radiographic testing programs including X-ray and gamma ray procedures, film and digital radiography, and source management compliance."},
    {"name": "magnetic-particle-testing", "description": "Execute magnetic particle testing including continuous and residual methods, wet and dry particle, and UV light inspection for surface and near-surface flaws."},
    {"name": "liquid-penetrant-testing", "description": "Conduct liquid penetrant testing including fluorescent and visible dye procedures, post-emulsifiable and solvent removable methods for surface defect detection."},
    {"name": "eddy-current-testing-ops", "description": "Apply eddy current testing for tube inspection, surface crack detection, and conductivity measurement with signal analysis and reporting."},
    {"name": "phased-array-ultrasonic-ops", "description": "Operate phased array ultrasonic systems for weld inspection, composite testing, and corrosion mapping with S-scan and E-scan data analysis."},
    {"name": "guided-wave-testing-ops", "description": "Deploy guided wave ultrasonic testing for long-range pipe screening including transducer ring setup, signal interpretation, and anomaly investigation."},
    {"name": "acoustic-emission-testing", "description": "Conduct acoustic emission testing for pressure vessel leak and crack detection, active corrosion monitoring, and structural integrity assessment."},
    {"name": "visual-testing-programs", "description": "Manage visual testing programs including remote visual inspection with borescopes and crawler systems, acceptance criteria, and documentation."},
    {"name": "ndt-personnel-qualification", "description": "Manage NDT personnel qualification programs including SNT-TC-1A and NAS 410 certification paths, written practice development, and examination administration."},
]

# Domain: Insulation Technology Services
skills += [
    {"name": "pipe-insulation-programs", "description": "Manage pipe insulation programs including material selection, thickness specification, jacketing selection, and personnel protection compliance."},
    {"name": "industrial-insulation-installation", "description": "Supervise industrial insulation installation including surface preparation, fitting insulation, jacket installation, and weatherproof sealing."},
    {"name": "refractory-lining-management", "description": "Manage refractory lining programs for furnaces, kilns, and reactors including material selection, installation supervision, and hot face inspection."},
    {"name": "cryogenic-insulation-systems", "description": "Design and maintain cryogenic insulation systems including vacuum jacket piping, perlite-filled vessels, and aerogel blanket applications."},
    {"name": "insulation-inspection-programs", "description": "Conduct insulation inspection programs including infrared thermography, visual survey, and moisture survey for insulation system condition assessment."},
    {"name": "insulation-energy-audits", "description": "Conduct industrial insulation energy audits including heat loss calculations, payback analysis, and specification of upgrade projects."},
    {"name": "insulation-maintenance-management", "description": "Manage insulation maintenance programs including damaged section identification, repair specification, and contractor work order management."},
    {"name": "high-temperature-insulation-apps", "description": "Apply high-temperature insulation products including ceramic fiber, microporous, and calcium silicate for furnace and process equipment applications."},
    {"name": "acoustic-insulation-programs", "description": "Implement acoustic insulation programs for pipe and equipment noise control including lagging materials, clip design, and insertion loss verification."},
    {"name": "insulation-specifications-dev", "description": "Develop insulation specifications for EPC projects including material standards, installation workmanship requirements, and quality inspection hold points."},
]

# Domain: Specialty Coatings & Surface Finishing
skills += [
    {"name": "industrial-coating-programs", "description": "Manage industrial protective coating programs including surface preparation standards, coating system specification, application inspection, and QC documentation."},
    {"name": "powder-coating-operations", "description": "Operate powder coating lines including pretreatment chemistry, electrostatic application, cure oven management, and film thickness verification."},
    {"name": "thermal-spray-coating-ops", "description": "Apply thermal spray coatings including plasma spray, HVOF, and arc wire processes for wear protection, thermal barriers, and corrosion resistance."},
    {"name": "electroplating-operations", "description": "Manage electroplating operations including bath chemistry control, current density management, thickness plating, and effluent treatment compliance."},
    {"name": "anodizing-operations", "description": "Operate anodizing processes including sulfuric acid anodize, hard anodize, and chromic acid anodize with sealing and coloring procedures."},
    {"name": "pvd-coating-operations", "description": "Operate physical vapor deposition coating systems including arc ion plating and sputtering for hard coatings on cutting tools and molds."},
    {"name": "ceramic-coating-applications", "description": "Apply ceramic coatings including spray-applied and sol-gel derived types for heat resistance, chemical protection, and dielectric properties."},
    {"name": "coating-testing-qualification", "description": "Conduct coating testing and qualification including adhesion, hardness, salt spray, humidity, and abrasion resistance testing per ASTM and ISO standards."},
    {"name": "surface-finishing-management", "description": "Manage surface finishing operations including shot blasting, vibratory finishing, and belt sanding with roughness specification and process control."},
    {"name": "coating-regulatory-compliance", "description": "Navigate coating regulatory compliance including VOC limits, ROHS restrictions, REACH substance declarations, and environmental permit management."},
]

# Domain: Photovoltaic Component Manufacturing
skills += [
    {"name": "solar-cell-manufacturing-ops", "description": "Manage solar cell manufacturing including silicon wafer processing, diffusion furnace operations, anti-reflective coating, and screen printing."},
    {"name": "pv-module-assembly-ops", "description": "Operate PV module assembly lines including cell stringing, lamination, framing, junction box installation, and I-V curve testing."},
    {"name": "pv-module-quality-testing", "description": "Conduct PV module quality testing including IEC 61215 qualification, thermal cycling, humidity-freeze, and damp heat testing programs."},
    {"name": "solar-inverter-manufacturing", "description": "Manage solar inverter manufacturing including power stage assembly, firmware programming, functional testing, and product certification."},
    {"name": "pv-mounting-structure-mfg", "description": "Manufacture PV mounting structures including rail extrusion, stamped hardware, galvanizing operations, and structural testing for wind and snow loads."},
    {"name": "pv-encapsulant-material-ops", "description": "Manage PV encapsulant material operations including EVA and POE processing, cure cycle development, and delamination resistance testing."},
    {"name": "pv-backsheet-manufacturing", "description": "Manufacture PV backsheets including multilayer film extrusion, damp heat aging, UV resistance testing, and electrical isolation verification."},
    {"name": "pv-junction-box-mfg", "description": "Manufacture PV junction boxes including connector assembly, bypass diode installation, waterproof testing, and IEC certification compliance."},
    {"name": "pv-component-supply-chain", "description": "Manage PV component supply chains including polysilicon procurement, cell sourcing, and module BOM cost optimization with supply security analysis."},
    {"name": "pv-manufacturing-yield-ops", "description": "Optimize PV manufacturing yield including defect classification, SPC control, efficiency distribution management, and scrap reduction programs."},
]

# Domain: Battery Manufacturing Technology
skills += [
    {"name": "lithium-ion-cell-manufacturing", "description": "Manage lithium-ion cell manufacturing including electrode slurry preparation, coating, calendering, slitting, winding, and formation cycling."},
    {"name": "battery-electrode-processing", "description": "Process battery electrodes including active material mixing, slot-die coating, drying oven management, and density/porosity quality control."},
    {"name": "cell-assembly-ops", "description": "Operate battery cell assembly including jellyroll winding, pouch folding, can filling, electrolyte injection, and hermetic sealing processes."},
    {"name": "battery-formation-aging", "description": "Manage battery formation and aging operations including charge-discharge cycling protocols, self-discharge measurement, and capacity grading."},
    {"name": "battery-pack-assembly", "description": "Assemble battery packs including cell module assembly, thermal management integration, BMS installation, and pack-level testing procedures."},
    {"name": "bms-engineering-ops", "description": "Engineer battery management systems including cell balancing algorithms, state-of-charge estimation, thermal runaway detection, and communication protocols."},
    {"name": "battery-safety-testing", "description": "Conduct battery safety testing including nail penetration, overcharge, forced discharge, and thermal abuse per UN 38.3 and IEC 62133 requirements."},
    {"name": "solid-state-battery-dev", "description": "Develop solid-state battery technologies including electrolyte material qualification, electrode interface engineering, and scale-up process development."},
    {"name": "battery-recycling-ops", "description": "Manage battery recycling operations including discharge protocols, disassembly, black mass processing, and critical material recovery programs."},
    {"name": "battery-quality-management", "description": "Manage battery quality programs including process FMEA, control plans, dimensional and performance specifications, and customer quality reporting."},
]

# Domain: Fuel Cell Technology
skills += [
    {"name": "pem-fuel-cell-manufacturing", "description": "Manufacture PEM fuel cells including membrane electrode assembly production, bipolar plate fabrication, stack assembly, and break-in procedures."},
    {"name": "fuel-cell-system-integration", "description": "Integrate fuel cell systems including balance-of-plant design, hydrogen supply management, cooling circuit, and power electronics coordination."},
    {"name": "fuel-cell-testing-ops", "description": "Operate fuel cell testing stations including polarization curve characterization, accelerated stress testing, and electrochemical impedance spectroscopy."},
    {"name": "hydrogen-storage-systems", "description": "Design hydrogen storage systems including compressed gas cylinders, cryogenic liquid tanks, and solid-state storage materials for fuel cell applications."},
    {"name": "fuel-cell-stack-assembly", "description": "Assemble fuel cell stacks including membrane electrode assembly handling, gas diffusion layer placement, clamping force management, and leak testing."},
    {"name": "fuel-cell-materials-mgmt", "description": "Manage fuel cell materials including platinum catalyst procurement, ionomer membrane qualification, and bipolar plate material selection programs."},
    {"name": "stationary-fuel-cell-ops", "description": "Operate stationary fuel cell power systems including combined heat and power applications, grid connection, and performance monitoring."},
    {"name": "mobility-fuel-cell-programs", "description": "Develop fuel cell programs for mobility applications including automotive stack design, hydrogen vehicle refueling, and durability validation."},
    {"name": "fuel-cell-safety-management", "description": "Manage fuel cell safety programs including hydrogen leak detection, purge system design, FMEA, and functional safety standard compliance."},
    {"name": "electrolysis-hydrogen-production", "description": "Operate electrolysis systems for green hydrogen production including PEM electrolyzers, alkaline electrolyzers, and stack maintenance programs."},
]

# Domain: Electronic Manufacturing Services
skills += [
    {"name": "pcb-assembly-operations", "description": "Manage PCB assembly operations including SMT line setup, solder paste printing, component placement, reflow profiling, and inspection programs."},
    {"name": "smt-line-engineering", "description": "Engineer SMT production lines including component feeder management, stencil design, paste inspection, and placement accuracy optimization."},
    {"name": "through-hole-assembly-ops", "description": "Operate through-hole assembly operations including manual and selective soldering, wave solder management, and PTH joint quality inspection."},
    {"name": "electronics-test-engineering", "description": "Develop electronics test strategies including ICT, functional test, flying probe, and boundary scan for PCB assembly quality verification."},
    {"name": "conformal-coating-operations", "description": "Manage conformal coating operations including material selection, selective coating programming, cure verification, and film thickness measurement."},
    {"name": "ems-quality-management", "description": "Manage EMS quality programs including IPC-A-610 workmanship standards, first article inspection, and customer quality system audits."},
    {"name": "bga-rework-operations", "description": "Execute BGA and complex component rework including reballing, solder profile optimization, and x-ray inspection for joint quality verification."},
    {"name": "ems-supply-chain-management", "description": "Manage EMS supply chains including component procurement, approved vendor lists, counterfeit component prevention, and shortage management."},
    {"name": "electronics-cleanliness-testing", "description": "Test electronics cleanliness including ion chromatography, SIR testing, and C3 contamination analysis for ionic residue compliance."},
    {"name": "ems-new-product-introduction", "description": "Lead EMS new product introduction including DFM review, first article build, yield ramp, and production release processes."},
]

# Domain: Semiconductor Packaging Services
skills += [
    {"name": "wirebond-packaging-ops", "description": "Manage wire bond packaging operations including die attach, gold and copper wire bonding, encapsulation, and electrical test coordination."},
    {"name": "flip-chip-packaging-ops", "description": "Operate flip chip packaging processes including underfill dispensing, solder bump reflow, and x-ray inspection for bump joint quality."},
    {"name": "wafer-level-packaging-ops", "description": "Execute wafer-level packaging processes including RDL deposition, solder ball placement, wafer probe, and singulation for WLP and WLCSP products."},
    {"name": "advanced-packaging-dev", "description": "Develop advanced packaging technologies including 2.5D interposers, 3D stacking, system-in-package, and embedded die processes."},
    {"name": "substrate-manufacturing-ops", "description": "Manage package substrate manufacturing including HDI laminate processing, via formation, copper plating, and fine-line patterning operations."},
    {"name": "thermal-management-packaging", "description": "Engineer thermal management in semiconductor packages including thermal resistance modeling, heat slug design, and junction temperature verification."},
    {"name": "package-reliability-testing", "description": "Execute package reliability testing including thermal cycling, moisture sensitivity, electrostatic discharge, and HTOL burn-in test programs."},
    {"name": "package-failure-analysis", "description": "Conduct semiconductor package failure analysis including cross-section preparation, SEM examination, EDX analysis, and corrective action."},
    {"name": "package-process-qualification", "description": "Qualify semiconductor packaging processes including process control monitor tracking, Cpk verification, and AEC-Q006 automotive qualification."},
    {"name": "packaging-design-rules-mgmt", "description": "Manage packaging design rules including DFT requirements, assembly design guidelines, and package drawing control for customer engagement."},
]

# Domain: Printed Circuit Board Manufacturing
skills += [
    {"name": "pcb-design-for-manufacturing", "description": "Provide PCB DFM review services including trace width, via sizing, clearance verification, and stack-up review for fabrication yield optimization."},
    {"name": "pcb-laminate-processing", "description": "Manage PCB laminate processing including inner layer imaging, oxide treatment, lay-up, lamination press operation, and dimensional inspection."},
    {"name": "pcb-drilling-routing-ops", "description": "Operate PCB drilling and routing operations including drill program management, drill file optimization, and hole quality inspection programs."},
    {"name": "pcb-plating-operations", "description": "Manage PCB plating operations including electroless copper, panel plating, pattern plating, and surface finish application processes."},
    {"name": "pcb-imaging-etching-ops", "description": "Execute PCB imaging and etching operations including photoresist application, UV exposure, developing, etching, and stripping process control."},
    {"name": "pcb-surface-finish-mgmt", "description": "Manage PCB surface finishes including HASL, ENIG, OSP, ENEPIG, and immersion silver processes with solderability testing programs."},
    {"name": "pcb-quality-inspection", "description": "Conduct PCB quality inspections including AOI, electrical test, impedance testing, and IPC-6012 acceptance criterion verification."},
    {"name": "high-density-interconnect-ops", "description": "Manufacture high-density interconnect PCBs including microvia drilling, blind and buried via processing, and sequential lamination operations."},
    {"name": "rf-microwave-pcb-mfg", "description": "Manufacture RF and microwave PCBs including PTFE laminate processing, controlled impedance routing, and RF characterization testing."},
    {"name": "pcb-spec-engineering-control", "description": "Manage PCB engineering change orders, revision control, specification documentation, and customer approval processes for production releases."},
]

# Domain: Optical Fiber Manufacturing
skills += [
    {"name": "optical-fiber-draw-ops", "description": "Operate optical fiber draw towers including preform feeding, draw speed control, diameter monitoring, and coating application for single and multimode fiber."},
    {"name": "preform-manufacturing-ops", "description": "Manage optical fiber preform manufacturing including MCVD, OVD, and PCVD deposition processes with geometry and composition characterization."},
    {"name": "fiber-coating-operations", "description": "Manage fiber coating operations including primary and secondary acrylate coating, colored ink application, and cure UV intensity monitoring."},
    {"name": "fiber-characterization-testing", "description": "Characterize optical fibers including attenuation, bandwidth, cut-off wavelength, mode field diameter, and chromatic dispersion measurement."},
    {"name": "fiber-cable-stranding-ops", "description": "Manage optical cable stranding operations including loose tube filling, stranding, core wrapping, armoring, and sheathing operations."},
    {"name": "fiber-connectivity-mfg", "description": "Manufacture fiber optic connectors and adapters including ferrule processing, polishing procedures, endface geometry inspection, and insertion loss testing."},
    {"name": "fiber-ribbon-cable-mfg", "description": "Manufacture fiber ribbon cables including ribbon matrix bonding, mass fusion splicing, and high fiber count cable assembly operations."},
    {"name": "fiber-splice-operations", "description": "Manage fiber splicing operations including fusion splicing machine setup, splice loss measurement, splice tray management, and OTDR acceptance testing."},
    {"name": "fiber-network-testing", "description": "Test fiber optic networks including OTDR trace analysis, optical power budget verification, and reflectance measurement for acceptance and troubleshooting."},
    {"name": "fiber-product-standards-mgmt", "description": "Manage fiber optic product compliance with ITU-T, IEC 60793, and TIA/EIA standards including qualification testing and certification documentation."},
]

# Domain: Telecommunications Equipment Manufacturing
skills += [
    {"name": "network-switch-router-mfg", "description": "Manage network switch and router manufacturing including PCB assembly, software loading, functional test, and product certification programs."},
    {"name": "base-station-manufacturing", "description": "Manufacture wireless base station equipment including RRH assembly, BBU integration, antenna port testing, and 5G NR performance verification."},
    {"name": "optical-transceiver-mfg", "description": "Manufacture optical transceivers including laser diode assembly, receiver module integration, eye diagram testing, and MSA compliance verification."},
    {"name": "telecom-power-supply-mfg", "description": "Manufacture telecom power supplies including DC-DC converter assembly, battery backup integration, and NEBS/ETSI environmental compliance testing."},
    {"name": "antenna-manufacturing-ops", "description": "Manufacture antenna products including element fabrication, impedance matching, VSWR testing, and pattern measurement for wireless applications."},
    {"name": "telecom-equipment-certification", "description": "Manage telecom equipment certification including FCC Part 96 CBRS, PTCRB, GCF, and carrier acceptance testing program management."},
    {"name": "telecom-supply-chain-mgmt", "description": "Manage telecom equipment supply chains including component sourcing, lead time management, allocation during shortages, and NPI coordination."},
    {"name": "cable-assembly-telecom-mfg", "description": "Manufacture telecom cable assemblies including coax, fiber, and hybrid cable assembly with insertion loss, VSWR, and shielding effectiveness testing."},
    {"name": "telecom-equipment-repair-ops", "description": "Operate telecom equipment repair operations including diagnostic testing, board-level repair, firmware recovery, and remanufacturing services."},
    {"name": "telecom-hw-product-lifecycle", "description": "Manage telecom hardware product lifecycle including technology transition planning, obsolescence management, and last-time-buy procurement programs."},
]

# Domain: Consumer Electronics Manufacturing
skills += [
    {"name": "consumer-electronics-ops", "description": "Manage consumer electronics manufacturing operations including SMT assembly, mechanical assembly, functional test, and cosmetic inspection programs."},
    {"name": "smartphone-assembly-ops", "description": "Operate smartphone assembly operations including display bonding, battery integration, RF testing, biometric sensor calibration, and waterproofing."},
    {"name": "consumer-device-compliance", "description": "Navigate consumer electronics compliance including FCC/CE marking, UL/ETL safety, California Prop 65, and country-specific certifications."},
    {"name": "consumer-electronics-packaging", "description": "Manage consumer electronics retail packaging including structural design, insert molding, accessory kit management, and shelf-ready compliance."},
    {"name": "consumer-product-safety-mgmt", "description": "Manage consumer product safety programs including CPSC reporting obligations, product recall readiness, and safety test program management."},
    {"name": "connected-device-operations", "description": "Manage connected device operations including firmware over-the-air update management, cloud service provisioning, and device registration systems."},
    {"name": "electronics-display-mfg", "description": "Manage display module manufacturing including cell assembly, polarizer lamination, backlight integration, and optical performance testing."},
    {"name": "consumer-npi-management", "description": "Lead consumer electronics new product introductions including EVT/DVT/PVT build management, yield improvement, and mass production ramp."},
    {"name": "consumer-repair-refurb-ops", "description": "Operate consumer electronics repair and refurbishment centers including triage, component-level repair, cosmetic restoration, and graded resale."},
    {"name": "consumer-electronics-eol-mgmt", "description": "Manage consumer electronics end-of-life including WEEE compliance, take-back program operations, and material recovery coordination."},
]

# Domain: Automotive Electronics Manufacturing
skills += [
    {"name": "automotive-ecm-manufacturing", "description": "Manufacture automotive ECMs and ECUs including automotive-grade PCB assembly, conformal coating, and AEC-Q100 component qualification."},
    {"name": "adas-sensor-manufacturing", "description": "Manufacture ADAS sensors including radar, camera, LiDAR, and ultrasonic systems with functional safety validation and automotive qualification."},
    {"name": "automotive-wiring-harness-mfg", "description": "Manufacture automotive wiring harnesses including crimping operations, routing design, connector sealing, and 100% electrical continuity testing."},
    {"name": "ev-power-electronics-mfg", "description": "Manufacture EV power electronics including inverter assembly, onboard charger production, and DC-DC converter fabrication with thermal management."},
    {"name": "automotive-display-mfg", "description": "Manufacture automotive displays including IPS/TFT panel integration, sunlight readability testing, and automotive temperature and vibration qualification."},
    {"name": "automotive-connector-mfg", "description": "Manufacture automotive connectors including terminal stamping, insert molding, housing assembly, and IP67/69K weatherseal testing."},
    {"name": "automotive-led-lighting-mfg", "description": "Manufacture automotive LED lighting including module assembly, photometric testing, thermal management, and automotive E-mark homologation."},
    {"name": "automotive-electronics-quality", "description": "Manage automotive electronics quality programs including IATF 16949, PPAP submissions, warranty analysis, and 8D corrective action management."},
    {"name": "functional-safety-iso26262", "description": "Implement ISO 26262 functional safety programs including hazard analysis, ASIL determination, safety concept, and safety case documentation."},
    {"name": "automotive-cybersecurity-mfg", "description": "Manage automotive cybersecurity in manufacturing including UN R155/R156 compliance, secure coding, and penetration testing for ECU products."},
]

# Domain: Industrial IoT Platform Operations
skills += [
    {"name": "iiot-platform-deployment", "description": "Deploy industrial IoT platforms including edge device configuration, cloud connectivity, data ingestion pipelines, and dashboard provisioning."},
    {"name": "iiot-sensor-integration", "description": "Integrate IoT sensors into industrial environments including protocol selection, wireless network design, and data normalization procedures."},
    {"name": "edge-computing-ops", "description": "Operate edge computing systems for industrial IoT including hardware selection, container orchestration, local analytics, and remote management."},
    {"name": "iiot-data-management", "description": "Manage industrial IoT data including historian integration, data lake architecture, time-series database management, and retention policy governance."},
    {"name": "digital-twin-operations", "description": "Operate digital twin systems including asset model creation, real-time data synchronization, simulation execution, and performance prediction."},
    {"name": "iiot-cybersecurity-ops", "description": "Manage IIoT cybersecurity programs including OT network segmentation, device identity management, patch management, and anomaly detection."},
    {"name": "predictive-analytics-ops", "description": "Operate predictive analytics systems for industrial equipment including ML model deployment, feature engineering pipelines, and alert management."},
    {"name": "iiot-connectivity-protocols", "description": "Manage IIoT connectivity protocols including MQTT, OPC-UA, Modbus, DNP3, and cellular connectivity for diverse industrial device integration."},
    {"name": "iiot-platform-vendor-mgmt", "description": "Manage IIoT platform vendor relationships including SLA monitoring, API version management, and multi-vendor integration strategy."},
    {"name": "iiot-roi-measurement", "description": "Measure IIoT program return on investment including energy savings quantification, downtime reduction tracking, and quality improvement attribution."},
]

# Domain: Additive Manufacturing Services
skills += [
    {"name": "fdm-3d-printing-ops", "description": "Operate FDM 3D printing services including material selection, build orientation, support strategy, and post-processing for functional part production."},
    {"name": "slp-sla-3d-printing-ops", "description": "Operate SLA and DLP photopolymer printing services including resin management, post-cure procedures, and surface finish optimization."},
    {"name": "sls-powder-bed-fusion-ops", "description": "Operate SLS powder bed fusion systems including powder management, build parameter optimization, part cleaning, and mechanical property verification."},
    {"name": "metal-additive-manufacturing", "description": "Manage metal additive manufacturing operations including DMLS/SLM parameter development, support design, heat treatment, and HIP densification."},
    {"name": "binder-jetting-operations", "description": "Operate binder jetting systems including powder bed preparation, binder saturation, sintering cycle management, and dimensional inspection."},
    {"name": "additive-design-optimization", "description": "Optimize designs for additive manufacturing including topology optimization, lattice structure design, support minimization, and buildability analysis."},
    {"name": "additive-quality-management", "description": "Manage additive manufacturing quality programs including AM specification standards, in-process monitoring, CT scanning, and destructive sample testing."},
    {"name": "additive-post-processing-ops", "description": "Manage additive manufacturing post-processing including support removal, surface finishing, HIP, machining, and coating for production readiness."},
    {"name": "3d-printing-material-dev", "description": "Develop 3D printing materials including polymer compound development, metal powder characterization, and process parameter qualification."},
    {"name": "additive-production-mgmt", "description": "Manage additive manufacturing production including build scheduling, machine utilization optimization, and order fulfillment for on-demand manufacturing."},
]

# Domain: CNC Machining Services
skills += [
    {"name": "cnc-mill-operations", "description": "Manage CNC milling operations including program development, tooling selection, workholding design, cutting parameter optimization, and inspection."},
    {"name": "cnc-turning-operations", "description": "Manage CNC turning operations including turning program creation, insert grade selection, bar feeder operations, and dimensional quality control."},
    {"name": "multi-axis-machining-ops", "description": "Execute multi-axis CNC machining including 4-axis and 5-axis simultaneous cutting, fixture design, and complex surface inspection."},
    {"name": "edm-operations", "description": "Operate EDM processes including wire EDM, sinker EDM, electrode manufacturing, dielectric management, and surface finish verification."},
    {"name": "grinding-operations-mgmt", "description": "Manage precision grinding operations including cylindrical, surface, and centerless grinding with wheel dressing, coolant management, and form accuracy."},
    {"name": "machining-tool-life-mgmt", "description": "Manage cutting tool life programs including tool change intervals, insert indexing records, tool condition monitoring, and cost-per-part optimization."},
    {"name": "machining-coolant-management", "description": "Manage machining coolant systems including concentration monitoring, biocide treatment, tramp oil removal, and coolant disposal compliance."},
    {"name": "precision-machining-quality", "description": "Manage precision machining quality programs including CMM inspection programs, GD&T verification, SPC control charts, and customer FAI documentation."},
    {"name": "machining-shop-scheduling", "description": "Schedule CNC machine shop production including job routing, machine load balancing, priority management, and on-time delivery performance."},
    {"name": "machining-dnc-cad-cam-ops", "description": "Manage DNC systems and CAD/CAM operations including post processor management, program version control, and simulation-based NC verification."},
]

# Domain: Sheet Metal Fabrication
skills += [
    {"name": "laser-cutting-operations", "description": "Manage laser cutting operations including material nesting optimization, kerf compensation, assist gas selection, and cut quality inspection."},
    {"name": "waterjet-cutting-operations", "description": "Operate waterjet cutting systems including abrasive management, taper compensation, underwater cutting, and multi-head production optimization."},
    {"name": "press-brake-forming-ops", "description": "Manage press brake forming operations including bend allowance calculation, tooling selection, springback compensation, and angular measurement."},
    {"name": "punch-press-operations", "description": "Operate CNC punch press systems including tool library management, nesting programs, die clearance setting, and burr-free quality verification."},
    {"name": "welding-fabrication-ops", "description": "Manage welding fabrication operations including WPS development, welder qualification, distortion control, and weld inspection programs."},
    {"name": "roll-forming-operations", "description": "Manage roll forming production including section profile tooling, strip feeding, straightening, and cutoff operations for continuous profiles."},
    {"name": "sheet-metal-finishing-ops", "description": "Manage sheet metal finishing operations including deburring, grinding, painting, powder coating, and plating coordination for finished assemblies."},
    {"name": "sheet-metal-assembly-ops", "description": "Manage sheet metal assembly operations including hardware insertion, spot welding, fastener installation, and dimensional assembly verification."},
    {"name": "sheet-metal-quality-mgmt", "description": "Manage sheet metal fabrication quality including first article inspection, dimensional compliance, cosmetic standards, and customer PPAP submissions."},
    {"name": "sheet-metal-material-mgmt", "description": "Manage sheet metal material procurement including coil and sheet stock, steel service center sourcing, and incoming mechanical property verification."},
]

# Domain: Injection Molding Services
skills += [
    {"name": "injection-mold-design", "description": "Design injection molds including gate system design, cooling channel layout, ejector system, and draft angle specification for production quality."},
    {"name": "injection-molding-process-dev", "description": "Develop injection molding processes including material selection, mold temperature optimization, fill speed tuning, and pack and hold optimization."},
    {"name": "injection-molding-quality-mgmt", "description": "Manage injection molding quality including dimensional inspection, visual defect classification, process capability studies, and PPAP submissions."},
    {"name": "mold-maintenance-programs", "description": "Manage injection mold maintenance programs including preventive maintenance intervals, cavity polishing, cooling circuit flushing, and repair documentation."},
    {"name": "overmolding-insert-molding-ops", "description": "Execute overmolding and insert molding operations including substrate preparation, insert loading, bond strength testing, and production monitoring."},
    {"name": "molding-material-qualification", "description": "Qualify molding materials including resin lot testing, color matching, regrind ratio management, and moisture content verification programs."},
    {"name": "hot-runner-system-management", "description": "Manage hot runner systems including zone temperature control, manifold maintenance, tip replacement, and gate balance verification programs."},
    {"name": "plastic-part-defect-analysis", "description": "Analyze plastic part defects including sink marks, warpage, short shots, flash, and weld lines with process parameter correction recommendations."},
    {"name": "cleanroom-molding-ops", "description": "Manage cleanroom injection molding operations including particle monitoring, gowning protocols, material handling, and medical grade validation."},
    {"name": "tooling-cost-estimation", "description": "Estimate injection mold tooling costs including cavity count analysis, material costs, machining hours, and lead time for quote preparation."},
]

# Domain: Rubber & Elastomer Products
skills += [
    {"name": "rubber-compound-development", "description": "Develop rubber compounds including polymer selection, carbon black reinforcement, vulcanization system design, and physical property optimization."},
    {"name": "rubber-molding-operations", "description": "Manage rubber molding operations including compression molding, transfer molding, and injection molding with cure time optimization and flash removal."},
    {"name": "extrusion-rubber-products", "description": "Operate rubber extrusion processes including die design, extrudate cooling, vulcanization tunnel management, and profile dimensional control."},
    {"name": "rubber-testing-programs", "description": "Conduct rubber testing including hardness, tensile, elongation, compression set, and fluid resistance per ASTM D standards for product qualification."},
    {"name": "rubber-bonding-to-metal-ops", "description": "Manage rubber-to-metal bonding operations including substrate surface preparation, adhesive application, molding integration, and bond strength testing."},
    {"name": "silicone-product-manufacturing", "description": "Manufacture silicone products including LSR injection molding, HCR compression molding, and room-temperature vulcanizing compound processing."},
    {"name": "rubber-product-design-support", "description": "Provide rubber product design support including geometry optimization for stress distribution, seal groove sizing, and compression load-deflection prediction."},
    {"name": "elastomer-material-selection", "description": "Select elastomer materials including NBR, EPDM, FKM, CR, and ACM types for media compatibility, temperature range, and mechanical property requirements."},
    {"name": "rubber-product-aging-testing", "description": "Conduct rubber aging tests including oven aging, ozone resistance, UV weathering, and fluid immersion for service life prediction."},
    {"name": "custom-rubber-products-dev", "description": "Develop custom rubber products including prototype iteration, material qualification, tooling design, and production process validation."},
]

# Domain: Plastics Recycling Services
skills += [
    {"name": "plastics-sorting-operations", "description": "Operate plastics sorting facilities including NIR spectroscopy sorting, density separation, and manual sorting lines for mixed plastics streams."},
    {"name": "plastics-washing-decontamination", "description": "Manage plastics washing and decontamination operations including hot wash systems, label removal, and contamination level verification."},
    {"name": "plastics-pelletizing-ops", "description": "Operate plastics pelletizing lines including extruder parameter management, melt filtration, pellet size control, and quality testing programs."},
    {"name": "recycled-content-certification", "description": "Manage recycled content certification programs including mass balance accounting, GRS certification, and customer chain of custody documentation."},
    {"name": "chemical-recycling-ops", "description": "Operate chemical recycling processes including pyrolysis, solvolysis, and gasification for difficult-to-recycle plastics with output quality management."},
    {"name": "post-consumer-resin-sourcing", "description": "Source post-consumer recycled resins including material qualification, contaminant testing, and supply agreement management for sustainable production."},
    {"name": "recycling-program-design", "description": "Design industrial recycling programs including collection infrastructure, sortation requirements, contamination reduction, and offtake agreement development."},
    {"name": "extended-producer-responsibility", "description": "Navigate extended producer responsibility programs including packaging fees, take-back obligations, and reporting requirements across jurisdictions."},
    {"name": "recycling-analytics-reporting", "description": "Manage recycling analytics and sustainability reporting including diversion rate tracking, carbon footprint calculations, and ESG disclosure preparation."},
    {"name": "bioplastics-compostables-mgmt", "description": "Manage bioplastics and compostable materials programs including certification verification, industrial composting coordination, and end-of-life claims."},
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
