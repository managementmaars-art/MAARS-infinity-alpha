import os

base = r"c:\Users\mirza\MAARS-Command\.claude\skills"

# Domain: Semiconductor Test Equipment Manufacturing
skills = [
    {"name": "semiconductor-test-equipment-mfg", "description": "Manufacture automatic test equipment for semiconductor devices including ATE platform assembly, probe card integration, and handler qualification."},
    {"name": "wafer-probe-station-manufacturing", "description": "Produce wafer probe stations including chuck manufacturing, positioner assembly, microscope integration, and thermal stage fabrication."},
    {"name": "burn-in-oven-manufacturing", "description": "Manufacture semiconductor burn-in ovens including board slot design, thermal uniformity calibration, and reliability stress chamber production."},
    {"name": "ic-handler-manufacturing", "description": "Produce IC device handlers including pick-and-place assembly, thermal test socket integration, and throughput optimization engineering."},
    {"name": "pcb-test-fixture-manufacturing", "description": "Manufacture PCB in-circuit test fixtures including bed-of-nails design, spring probe selection, and fixture verification procedures."},
    {"name": "semiconductor-metrology-equipment-mfg", "description": "Produce semiconductor metrology instruments including ellipsometers, profilometers, and overlay measurement system manufacturing."},
    {"name": "yield-management-system-manufacturing", "description": "Develop yield management system hardware and software including inline data collection tools, SPC module assembly, and fab integration kits."},
    {"name": "failure-analysis-equipment-mfg", "description": "Manufacture failure analysis instruments including FIB-SEM systems, emission microscopes, and electrical probing station assembly."},
    {"name": "cleanroom-monitoring-equipment-mfg", "description": "Produce cleanroom monitoring instruments including particle counters, molecular contamination monitors, and airflow measurement devices."},
    {"name": "semiconductor-packaging-equipment-mfg", "description": "Manufacture semiconductor packaging equipment including die bonders, wire bonders, flip chip systems, and molding press fabrication."},
]

# Domain: Vacuum Technology Manufacturing
skills += [
    {"name": "vacuum-pump-manufacturing", "description": "Manufacture industrial vacuum pumps including dry screw, turbomolecular, rotary vane, and cryopump assembly and testing."},
    {"name": "vacuum-chamber-fabrication", "description": "Fabricate custom vacuum chambers including weld design, surface treatment, viewport integration, and leak test qualification."},
    {"name": "vacuum-valve-manufacturing", "description": "Produce vacuum isolation and control valves including gate valve assembly, bellows seal fabrication, and leak rate certification."},
    {"name": "vacuum-feedthrough-manufacturing", "description": "Manufacture vacuum feedthrough components including electrical, motion, and fluid feedthrough design and hermetic seal fabrication."},
    {"name": "vacuum-gauge-manufacturing", "description": "Produce vacuum measurement gauges including Pirani, ion gauge, capacitance manometer assembly and calibration workflows."},
    {"name": "vacuum-coating-system-manufacturing", "description": "Manufacture vacuum deposition systems including PVD, CVD, and ALD reactor chamber fabrication and process kit assembly."},
    {"name": "cryogenic-vacuum-system-mfg", "description": "Produce cryogenic vacuum systems including helium compressor integration, cold head assembly, and cryostat fabrication workflows."},
    {"name": "vacuum-robot-transfer-system-mfg", "description": "Manufacture vacuum robot transfer systems including SCARA arm assembly, magnetic coupling design, and throughput qualification."},
    {"name": "load-lock-chamber-manufacturing", "description": "Fabricate load lock chambers for vacuum process equipment including door mechanism assembly, pumping system integration, and cycle time optimization."},
    {"name": "residual-gas-analyzer-manufacturing", "description": "Produce residual gas analyzers including quadrupole mass spectrometer assembly, electron ionizer fabrication, and sensitivity calibration."},
]

# Domain: Metrology and Calibration Equipment Manufacturing
skills += [
    {"name": "coordinate-measuring-machine-mfg", "description": "Manufacture coordinate measuring machines including granite table preparation, axis guide assembly, probe head integration, and volumetric accuracy verification."},
    {"name": "laser-tracker-manufacturing", "description": "Produce laser tracker measurement systems including interferometer assembly, retroreflector target manufacturing, and workspace accuracy certification."},
    {"name": "optical-comparator-manufacturing", "description": "Manufacture optical comparators including projection lens assembly, illumination system fabrication, and overlay accuracy qualification."},
    {"name": "surface-roughness-tester-mfg", "description": "Produce surface roughness measurement instruments including stylus probe assembly, drive unit fabrication, and Ra/Rz calibration standard traceability."},
    {"name": "hardness-tester-manufacturing", "description": "Manufacture hardness testing instruments including Rockwell, Vickers, and Brinell tester frame fabrication and load cell calibration."},
    {"name": "calibration-lab-equipment-mfg", "description": "Produce calibration laboratory reference standards including dead weight testers, precision resistance decades, and voltage reference sources."},
    {"name": "torque-calibration-equipment-mfg", "description": "Manufacture torque calibration equipment including torque reference transducers, calibration bench fabrication, and uncertainty budget documentation."},
    {"name": "dimensional-gage-manufacturing", "description": "Produce precision dimensional gages including micrometer, caliper, and gage block set manufacturing with NIST traceable calibration."},
    {"name": "vision-measurement-system-mfg", "description": "Manufacture machine vision measurement systems including telecentric lens assembly, stage motion integration, and pixel calibration workflows."},
    {"name": "roundness-tester-manufacturing", "description": "Produce roundness and cylindricity measurement instruments including air bearing spindle fabrication, probe arm assembly, and form accuracy verification."},
]

# Domain: Laboratory Automation Equipment Manufacturing
skills += [
    {"name": "liquid-handling-robot-manufacturing", "description": "Manufacture laboratory liquid handling robots including pipette head assembly, deck layout fabrication, and volume accuracy verification."},
    {"name": "microplate-reader-manufacturing", "description": "Produce microplate reader instruments including optical detection assembly, filter wheel fabrication, and assay protocol validation."},
    {"name": "automated-centrifuge-manufacturing", "description": "Manufacture automated centrifuges including rotor fabrication, imbalance detection system assembly, and safety interlock qualification."},
    {"name": "sample-storage-system-manufacturing", "description": "Produce automated sample storage systems including cryogenic rack assembly, pick-and-place robot integration, and barcode tracking setup."},
    {"name": "pcr-instrument-manufacturing", "description": "Manufacture PCR thermal cyclers including Peltier block assembly, optical detection integration, and gradient temperature uniformity validation."},
    {"name": "flow-cytometer-manufacturing", "description": "Produce flow cytometer instruments including fluidic manifold assembly, laser optic alignment, and multicolor panel calibration workflows."},
    {"name": "mass-spectrometer-manufacturing", "description": "Manufacture mass spectrometer systems including ion source assembly, analyzer fabrication, detector integration, and sensitivity calibration."},
    {"name": "hplc-system-manufacturing", "description": "Produce HPLC chromatography systems including pump head assembly, column thermostat fabrication, detector module integration, and pressure qualification."},
    {"name": "lab-automation-scheduler-mfg", "description": "Manufacture laboratory automation scheduler platforms including robotic integration middleware, workcell communication systems, and scheduling software assembly."},
    {"name": "automated-microscopy-system-mfg", "description": "Produce automated microscopy platforms including motorized stage assembly, autofocus system integration, and fluorescence illumination calibration."},
]

# Domain: Industrial Automation Components Manufacturing
skills += [
    {"name": "plc-manufacturing-ops", "description": "Manufacture programmable logic controllers including CPU module fabrication, I/O card assembly, backplane manufacturing, and firmware qualification."},
    {"name": "servo-drive-manufacturing", "description": "Produce servo drive systems including power stage assembly, current feedback integration, encoder interface design, and torque loop tuning."},
    {"name": "variable-frequency-drive-mfg", "description": "Manufacture variable frequency drives including IGBT module assembly, DC bus capacitor installation, heat sink fabrication, and EMC compliance testing."},
    {"name": "industrial-hmi-manufacturing", "description": "Produce industrial HMI panels including touchscreen integration, rugged enclosure fabrication, communication module assembly, and environmental rating certification."},
    {"name": "motion-controller-manufacturing", "description": "Manufacture multi-axis motion controllers including FPGA-based control card assembly, real-time OS integration, and path accuracy qualification."},
    {"name": "industrial-pc-manufacturing", "description": "Produce industrial PCs including ruggedized chassis fabrication, passive cooling design, extended temperature testing, and vibration resistance certification."},
    {"name": "safety-relay-manufacturing", "description": "Manufacture safety relays and safety PLCs including dual-channel input assembly, self-monitoring circuit fabrication, and SIL certification testing."},
    {"name": "industrial-power-supply-mfg", "description": "Produce industrial power supplies including switch-mode topology design, EMC filter assembly, hold-up time testing, and MTBF verification."},
    {"name": "fieldbus-gateway-manufacturing", "description": "Manufacture fieldbus protocol gateways including multi-protocol chip integration, isolation circuit fabrication, and interoperability certification."},
    {"name": "industrial-switch-manufacturing", "description": "Produce managed industrial Ethernet switches including ruggedized port assembly, ring redundancy firmware integration, and harsh environment certification."},
]

# Domain: Robotics Systems Manufacturing
skills += [
    {"name": "industrial-robot-arm-manufacturing", "description": "Manufacture articulated industrial robot arms including gearbox assembly, servo motor integration, wrist mechanism fabrication, and path repeatability verification."},
    {"name": "collaborative-robot-manufacturing", "description": "Produce collaborative robots including torque sensing joint assembly, collision detection calibration, and safety rated stop certification."},
    {"name": "delta-robot-manufacturing", "description": "Manufacture delta parallel robots including carbon fiber arm fabrication, universal joint assembly, and high-speed pick accuracy qualification."},
    {"name": "scara-robot-manufacturing", "description": "Produce SCARA robots including direct drive motor integration, harmonic drive assembly, and Z-axis compliance testing."},
    {"name": "autonomous-mobile-robot-mfg", "description": "Manufacture autonomous mobile robots including LIDAR integration, differential drive assembly, battery management system fabrication, and navigation software qualification."},
    {"name": "robot-end-effector-manufacturing", "description": "Produce robot end effectors including gripper jaw fabrication, force-torque sensor integration, quick-change coupling assembly, and application cycle testing."},
    {"name": "robot-controller-manufacturing", "description": "Manufacture robot controllers including teach pendant assembly, safety I/O board fabrication, trajectory generation processor integration, and cycle time validation."},
    {"name": "exoskeleton-manufacturing", "description": "Produce industrial exoskeleton devices including actuator assembly, ergonomic frame fabrication, control algorithm integration, and biomechanical testing."},
    {"name": "surgical-robot-system-manufacturing", "description": "Manufacture surgical robotic platforms including instrument drive unit assembly, vision cart fabrication, force feedback integration, and sterility validation."},
    {"name": "underwater-robot-manufacturing", "description": "Produce remotely operated underwater vehicles including pressure vessel fabrication, thruster assembly, tether management system manufacturing, and depth rating certification."},
]

# Domain: CNC and Machine Tool Manufacturing
skills += [
    {"name": "cnc-machining-center-manufacturing", "description": "Manufacture CNC machining centers including machine bed casting, linear guide assembly, spindle integration, and geometric accuracy verification."},
    {"name": "cnc-lathe-manufacturing", "description": "Produce CNC turning centers including headstock assembly, turret fabrication, tailstock integration, and cylindricity accuracy qualification."},
    {"name": "grinding-machine-manufacturing", "description": "Manufacture surface and cylindrical grinding machines including hydrostatic spindle assembly, dresser integration, and surface finish qualification."},
    {"name": "edm-machine-manufacturing", "description": "Produce electrical discharge machining systems including dielectric system assembly, wire EDM head fabrication, and surface integrity verification."},
    {"name": "laser-cutting-machine-manufacturing", "description": "Manufacture laser cutting systems including beam delivery optic assembly, gantry drive integration, assist gas management, and cut quality certification."},
    {"name": "waterjet-cutting-machine-mfg", "description": "Produce waterjet cutting machines including high-pressure pump assembly, nozzle fabrication, abrasive feed system integration, and dimensional accuracy testing."},
    {"name": "gear-cutting-machine-manufacturing", "description": "Manufacture hobbing and grinding machines for gear production including hob arbor assembly, indexing drive integration, and tooth profile accuracy verification."},
    {"name": "multi-axis-machining-center-mfg", "description": "Produce 5-axis and multi-tasking machining centers including tilting rotary table assembly, B-axis integration, and volumetric accuracy verification."},
    {"name": "cnc-control-system-manufacturing", "description": "Manufacture CNC control units including real-time processor assembly, drive interface board fabrication, encoder feedback integration, and interpolation accuracy testing."},
    {"name": "tool-presetter-manufacturing", "description": "Produce tool presetter instruments including telecentric optic assembly, Z-axis measurement integration, and tool data management software qualification."},
]

# Domain: SCADA and DCS System Manufacturing
skills += [
    {"name": "dcs-controller-manufacturing", "description": "Manufacture distributed control system controllers including redundant processor assembly, I/O module fabrication, field enclosure integration, and SIL compliance testing."},
    {"name": "scada-server-manufacturing", "description": "Produce SCADA server platforms including historian database integration, real-time kernel assembly, OPC UA server software fabrication, and cybersecurity hardening."},
    {"name": "remote-terminal-unit-manufacturing", "description": "Manufacture remote terminal units including low-power processor integration, analog I/O card assembly, wireless module fabrication, and field protocol certification."},
    {"name": "intelligent-electronic-device-mfg", "description": "Produce intelligent electronic devices for power systems including protection relay assembly, phasor measurement integration, and IEC 61850 compliance testing."},
    {"name": "process-analyser-system-mfg", "description": "Manufacture process analytical systems including sample conditioning panel assembly, analyser shelter fabrication, calibration gas delivery integration, and SIL validation."},
    {"name": "safety-instrumented-system-mfg", "description": "Produce safety instrumented system hardware including logic solver assembly, final element interface fabrication, and SIL-rated proof test documentation."},
    {"name": "turbine-control-system-mfg", "description": "Manufacture turbine control systems including overspeed protection assembly, servo valve interface fabrication, and startup sequence validation."},
    {"name": "substation-automation-system-mfg", "description": "Produce substation automation systems including bay controller assembly, protection relay panel fabrication, and IEC 61850 station bus verification."},
    {"name": "pipeline-control-system-mfg", "description": "Manufacture pipeline SCADA systems including flow computer assembly, RTU field enclosure fabrication, and leak detection algorithm integration."},
    {"name": "building-management-system-mfg", "description": "Produce building management system controllers including room sensor assembly, floor panel fabrication, and BACnet protocol certification."},
]

# Domain: Industrial Sensor and Transducer Manufacturing
skills += [
    {"name": "pressure-transmitter-manufacturing", "description": "Manufacture pressure transmitters including piezoresistive cell fabrication, 4-20mA signal conditioning assembly, and HART protocol certification."},
    {"name": "temperature-sensor-manufacturing", "description": "Produce industrial temperature sensors including RTD element winding, thermocouple junction fabrication, and transmitter head assembly."},
    {"name": "flow-meter-manufacturing", "description": "Manufacture industrial flow meters including Coriolis tube fabrication, electromagnetic coil assembly, vortex shedder body machining, and flow calibration."},
    {"name": "level-sensor-manufacturing", "description": "Produce level measurement instruments including guided wave radar assembly, ultrasonic transducer fabrication, and interface detection calibration."},
    {"name": "gas-detector-manufacturing", "description": "Manufacture gas detection instruments including electrochemical cell fabrication, infrared detector assembly, and cross-sensitivity calibration workflows."},
    {"name": "vibration-sensor-manufacturing", "description": "Produce industrial vibration sensors including piezoelectric crystal mounting, IEPE signal conditioning assembly, and frequency response certification."},
    {"name": "position-encoder-manufacturing", "description": "Manufacture linear and rotary encoders including optical disk fabrication, photodetector array assembly, and interpolation accuracy verification."},
    {"name": "load-cell-manufacturing", "description": "Produce strain gauge load cells including beam element machining, full-bridge circuit bonding, and OIML accuracy class verification."},
    {"name": "proximity-sensor-manufacturing", "description": "Manufacture inductive and capacitive proximity sensors including oscillator coil winding, ASIC integration, and switching distance certification."},
    {"name": "vision-sensor-manufacturing", "description": "Produce smart vision sensors including CMOS imager assembly, embedded processor integration, and field-of-view calibration workflows."},
]

# Domain: Power Electronics and Drive Manufacturing
skills += [
    {"name": "power-inverter-manufacturing", "description": "Manufacture power inverters including IGBT module mounting, DC link capacitor bank assembly, control board integration, and harmonic distortion testing."},
    {"name": "ups-system-manufacturing", "description": "Produce uninterruptible power systems including rectifier assembly, battery cabinet integration, static bypass switch fabrication, and runtime verification."},
    {"name": "solar-inverter-manufacturing", "description": "Manufacture solar PV inverters including MPPT algorithm firmware integration, isolation transformer assembly, and grid-tie interconnection certification."},
    {"name": "motor-starter-manufacturing", "description": "Produce soft starters and direct-on-line starters including thyristor stack assembly, bypass contactor integration, and locked rotor protection testing."},
    {"name": "dc-dc-converter-manufacturing", "description": "Manufacture DC-DC converter modules including transformer winding, synchronous rectifier assembly, and EMI conducted emissions testing."},
    {"name": "power-factor-correction-mfg", "description": "Produce active and passive power factor correction units including filter capacitor assembly, contactor switching stage fabrication, and THD verification."},
    {"name": "regenerative-drive-manufacturing", "description": "Manufacture regenerative variable speed drives including active front end assembly, energy feedback integration, and four-quadrant operation testing."},
    {"name": "medium-voltage-drive-manufacturing", "description": "Produce medium voltage drives including cell bypass assembly, phase-shifting transformer integration, and harmonic compliance testing."},
    {"name": "battery-charger-manufacturing", "description": "Manufacture industrial battery chargers including high-frequency topology assembly, CC/CV charging algorithm integration, and equalizer circuit fabrication."},
    {"name": "traction-inverter-manufacturing", "description": "Produce traction inverters for electric vehicles including SiC module assembly, bus bar lamination fabrication, and EMC shielding qualification."},
]

# Domain: Pharmaceutical API Manufacturing
skills += [
    {"name": "api-synthesis-operations", "description": "Operate active pharmaceutical ingredient synthesis including reaction step scheduling, yield optimization, and impurity profile management."},
    {"name": "api-crystallization-operations", "description": "Manage API crystallization processes including polymorph control, particle size distribution targeting, and mother liquor recycling programs."},
    {"name": "api-isolation-drying-ops", "description": "Operate API isolation and drying operations including centrifuge management, tray dryer scheduling, and residual solvent compliance testing."},
    {"name": "pharmaceutical-solvent-recovery", "description": "Manage pharmaceutical solvent recovery operations including distillation scheduling, solvent quality testing, and material balance reconciliation."},
    {"name": "api-quality-control-lab", "description": "Operate API quality control laboratories including HPLC method execution, dissolution testing, and out-of-specification investigation management."},
    {"name": "api-regulatory-filing-support", "description": "Support API regulatory filings including DMF preparation, ICH Q7 compliance documentation, and agency inspection readiness programs."},
    {"name": "controlled-substance-manufacturing", "description": "Manage controlled substance API manufacturing including DEA quota management, vault security compliance, and chain of custody documentation."},
    {"name": "api-scale-up-tech-transfer", "description": "Execute API scale-up and technology transfer programs including pilot batch execution, process characterization studies, and validation protocol development."},
    {"name": "peptide-manufacturing-ops", "description": "Operate peptide API manufacturing including SPPS coupling cycle management, cleavage and deprotection operations, and purity upgrade chromatography."},
    {"name": "oligonucleotide-manufacturing", "description": "Manage oligonucleotide API production including synthesizer scheduling, purification operations, lyophilization management, and sequence verification."},
]

# Domain: Biologics Manufacturing
skills += [
    {"name": "cell-line-development-ops", "description": "Manage cell line development programs including transfection workflows, clone selection, stability studies, and research cell bank qualification."},
    {"name": "upstream-bioprocessing-ops", "description": "Operate upstream bioprocessing including seed train management, bioreactor feeding strategy, dissolved oxygen control, and harvest trigger decisions."},
    {"name": "downstream-bioprocessing-ops", "description": "Manage downstream purification operations including chromatography column packing, filtration train management, and viral inactivation step execution."},
    {"name": "fill-finish-manufacturing-ops", "description": "Operate biologics fill-finish manufacturing including vial and syringe filling line management, stopper insertion quality, and container closure integrity testing."},
    {"name": "biologics-analytical-development", "description": "Manage biologics analytical development including potency assay qualification, glycan mapping, and forced degradation study execution."},
    {"name": "biosimilar-comparability-programs", "description": "Execute biosimilar comparability programs including head-to-head analytical studies, PK comparability bridging, and regulatory submission support."},
    {"name": "mab-manufacturing-operations", "description": "Operate monoclonal antibody manufacturing including perfusion bioreactor management, Protein A chromatography operations, and in-process control execution."},
    {"name": "gene-therapy-manufacturing", "description": "Manage viral vector manufacturing for gene therapy including transfection optimization, ultracentrifugation operations, and AAV titer determination workflows."},
    {"name": "mrna-manufacturing-operations", "description": "Operate mRNA production including IVT reaction management, LNP formulation operations, encapsulation efficiency testing, and cold chain management."},
    {"name": "cell-therapy-manufacturing", "description": "Manage cell therapy production including leukapheresis coordination, T-cell activation, viral transduction, and product release testing workflows."},
]

# Domain: Clinical Trial Supply Management
skills += [
    {"name": "clinical-supply-planning", "description": "Develop clinical supply plans including demand forecasting, comparator sourcing, packaging design, and global distribution strategy."},
    {"name": "clinical-packaging-labeling", "description": "Manage clinical trial packaging and labeling operations including randomization scheme execution, kit assembly, and multi-lingual label management."},
    {"name": "clinical-depot-operations", "description": "Operate global clinical depot networks including import/export compliance, temperature excursion management, and site resupply automation."},
    {"name": "investigational-drug-accountability", "description": "Manage investigational drug accountability systems including dispensation tracking, return reconciliation, and destruction documentation."},
    {"name": "comparator-drug-sourcing", "description": "Source comparator drugs for clinical trials including market authorization verification, over-labeling compliance, and supply chain qualification."},
    {"name": "clinical-supply-tech-transfer", "description": "Execute clinical supply technology transfers including primary packaging qualification, stability bridging studies, and CMO onboarding workflows."},
    {"name": "adaptive-trial-supply-management", "description": "Manage adaptive clinical trial supply including scenario-based resupply modeling, interim analysis supply triggers, and protocol amendment response."},
    {"name": "clinical-cold-chain-management", "description": "Manage cold chain supply for clinical trials including validated shipper qualification, lane qualification studies, and excursion investigation."},
    {"name": "phase-iii-supply-scale-up", "description": "Scale up clinical supply operations from Phase I to Phase III including CMO capacity booking, QTA negotiation, and regulatory batch records."},
    {"name": "clinical-supply-forecasting", "description": "Generate clinical supply forecasts using enrollment projection models, dropout rate assumptions, and safety stock calculation methodologies."},
]

# Domain: Medical Laboratory Operations
skills += [
    {"name": "clinical-lab-accreditation-mgmt", "description": "Manage clinical laboratory accreditation programs including CAP inspection readiness, proficiency testing enrollment, and corrective action documentation."},
    {"name": "lab-information-system-ops", "description": "Operate laboratory information systems including order entry workflows, result verification queues, and HL7 interface management."},
    {"name": "point-of-care-testing-ops", "description": "Manage point-of-care testing programs including device connectivity, operator competency tracking, and quality control compliance."},
    {"name": "blood-bank-operations", "description": "Operate blood bank services including component inventory management, compatibility testing workflows, and transfusion reaction investigation."},
    {"name": "molecular-diagnostics-ops", "description": "Manage molecular diagnostics laboratory operations including PCR assay management, NGS workflow coordination, and result interpretation workflows."},
    {"name": "histopathology-lab-operations", "description": "Operate histopathology laboratories including tissue processing scheduling, staining protocol management, and digital pathology slide management."},
    {"name": "clinical-chemistry-lab-ops", "description": "Manage clinical chemistry analyzer operations including calibration curve management, reagent inventory, and critical value notification workflows."},
    {"name": "microbiology-lab-operations", "description": "Operate clinical microbiology laboratories including culture workup management, antimicrobial susceptibility reporting, and outbreak investigation support."},
    {"name": "reference-lab-operations", "description": "Manage reference laboratory services including specimen logistics, esoteric test menu, send-out tracking, and result turnaround monitoring."},
    {"name": "lab-revenue-cycle-management", "description": "Manage laboratory revenue cycle operations including CPT code assignment, payer contract management, and denial appeal workflows."},
]

# Domain: Steel Mill Operations
skills += [
    {"name": "blast-furnace-operations", "description": "Operate blast furnace ironmaking including burden material management, hot blast control, cast scheduling, and refractory campaign management."},
    {"name": "electric-arc-furnace-operations", "description": "Manage electric arc furnace steelmaking including scrap charge optimization, electrode consumption tracking, and heat chemistry control."},
    {"name": "basic-oxygen-furnace-operations", "description": "Operate basic oxygen furnace steelmaking including hot metal scheduling, lance blowing practice, and slag management programs."},
    {"name": "continuous-casting-operations", "description": "Manage continuous casting operations including tundish management, mold oscillation control, strand cooling optimization, and surface quality monitoring."},
    {"name": "hot-rolling-mill-operations", "description": "Operate hot strip rolling mills including slab reheating scheduling, rougher and finisher pass design, and coiler temperature control."},
    {"name": "cold-rolling-mill-operations", "description": "Manage cold rolling operations including tension leveling, rolling reduction scheduling, surface finish control, and shape correction programs."},
    {"name": "steel-coating-line-operations", "description": "Operate steel coating lines including galvanizing bath management, annealing furnace control, temper rolling, and zinc weight compliance."},
    {"name": "steelmaking-metallurgy-ops", "description": "Manage steelmaking metallurgical programs including ladle metallurgy operations, alloy addition optimization, and inclusion cleanliness programs."},
    {"name": "steel-quality-assurance-ops", "description": "Operate steel quality assurance programs including mechanical property testing, ultrasonic inspection, and heat treatment compliance tracking."},
    {"name": "steel-plant-energy-management", "description": "Manage energy consumption across steel plant operations including byproduct gas utilization, power demand optimization, and steam balance management."},
]

# Domain: Cement Plant Operations
skills += [
    {"name": "cement-kiln-operations", "description": "Operate cement rotary kilns including preheater management, clinker burning zone control, fuel substitution programs, and refractory inspection scheduling."},
    {"name": "cement-raw-material-management", "description": "Manage cement plant raw material operations including quarry scheduling, blend optimization, pre-homogenization pile management, and quality control."},
    {"name": "cement-grinding-operations", "description": "Operate cement finish grinding systems including ball mill and vertical roller mill management, separator adjustment, and fineness compliance monitoring."},
    {"name": "cement-quality-control-ops", "description": "Manage cement quality control operations including clinker chemistry analysis, cement strength testing, and setting time compliance programs."},
    {"name": "cement-plant-maintenance-ops", "description": "Coordinate cement plant maintenance including planned maintenance programs, kiln tire management, girth gear inspection, and cyclone maintenance."},
    {"name": "cement-alternative-fuels-ops", "description": "Manage alternative fuel programs at cement plants including waste fuel qualification, co-processing permits, and thermal substitution rate optimization."},
    {"name": "cement-packing-dispatch-ops", "description": "Operate cement packing and dispatch operations including rotary packer management, bulk loading terminals, and truck/rail scheduling."},
    {"name": "cement-clinker-trading-ops", "description": "Manage clinker trading operations including import terminal operations, inventory management, quality inspection, and interplant allocation."},
    {"name": "cement-plant-emissions-mgmt", "description": "Manage cement plant emissions compliance including dust collector performance, NOx reduction programs, SO2 monitoring, and reporting to regulators."},
    {"name": "cement-digital-plant-ops", "description": "Deploy digital plant operations for cement manufacturing including advanced process control, digital twin monitoring, and predictive maintenance programs."},
]

# Domain: Paper Mill Operations
skills += [
    {"name": "pulp-mill-operations", "description": "Operate chemical pulp mills including digester management, washing and screening operations, bleaching sequence control, and black liquor recovery."},
    {"name": "paper-machine-operations", "description": "Manage paper machine operations including forming section management, press section nip loading, dryer section steam profiling, and caliper control."},
    {"name": "papermaking-stock-preparation", "description": "Operate paper stock preparation systems including pulper management, refiner energy optimization, filler addition, and broke system management."},
    {"name": "paper-coating-operations", "description": "Manage paper coating operations including coating color preparation, blade and curtain coater management, and gloss/brightness compliance."},
    {"name": "paper-converting-operations", "description": "Operate paper converting operations including sheeter scheduling, slitter-winder management, reel handling, and finished goods inspection."},
    {"name": "pulp-and-paper-quality-control", "description": "Execute pulp and paper quality control programs including tensile and tear testing, formation analysis, and customer complaint investigation."},
    {"name": "recovery-boiler-operations", "description": "Operate recovery boilers for kraft mills including smelt dissolving, black liquor firing management, and recovery boiler inspection scheduling."},
    {"name": "paper-mill-water-management", "description": "Manage water use and treatment at paper mills including effluent treatment operations, white water system management, and water balance optimization."},
    {"name": "paper-mill-energy-management", "description": "Optimize energy use at paper mills including steam balancing, turbine generator operation, compressed air management, and heat recovery programs."},
    {"name": "paper-mill-fiber-sourcing", "description": "Manage pulp and fiber sourcing for paper mills including wood procurement, recovered fiber purchasing, and alternative fiber qualification programs."},
]

# Domain: Aluminum Smelting Operations
skills += [
    {"name": "aluminum-reduction-cell-ops", "description": "Operate aluminum electrolytic reduction cells including anode setting schedules, alumina feeding control, bath chemistry management, and tapping operations."},
    {"name": "aluminum-casthouse-operations", "description": "Manage aluminum casthouse operations including alloying additions, degassing and filtration, casting machine management, and ingot quality control."},
    {"name": "aluminum-anode-plant-ops", "description": "Operate aluminum anode plants including green anode paste preparation, baking furnace management, and anode quality inspection programs."},
    {"name": "aluminum-pot-line-management", "description": "Manage aluminum pot line operations including pot shutdown and restart programs, collector bar maintenance, and cell performance optimization."},
    {"name": "alumina-refinery-operations", "description": "Operate alumina refineries including digestion circuit management, liquor clarification, precipitation crystallization, and calcination kiln operations."},
    {"name": "aluminum-rolling-operations", "description": "Manage aluminum hot and cold rolling operations including homogenization scheduling, gauge control programs, and alloy temper compliance."},
    {"name": "aluminum-extrusion-operations", "description": "Operate aluminum extrusion operations including billet heating management, die qualification, press force optimization, and age hardening scheduling."},
    {"name": "aluminum-scrap-management", "description": "Manage aluminum scrap operations including scrap classification, alloy sorting, delacquering, and secondary melting quality assurance."},
    {"name": "aluminum-plant-emissions-mgmt", "description": "Manage aluminum smelter emissions including fluoride scrubber operations, anode effect monitoring, and perfluorocarbon reporting programs."},
    {"name": "aluminum-quality-systems-ops", "description": "Operate aluminum quality systems including spectrographic analysis, mechanical testing, surface inspection, and customer specification compliance."},
]

# Domain: Copper and Precious Metals Refining
skills += [
    {"name": "copper-smelter-operations", "description": "Operate copper smelter facilities including flash furnace management, converter operations, anode furnace control, and slag processing."},
    {"name": "copper-electrolytic-refinery-ops", "description": "Manage copper electrolytic refining operations including tank house management, anode scrap handling, starter sheet production, and anode slime recovery."},
    {"name": "copper-rod-manufacturing-ops", "description": "Operate continuous copper rod production including shaft furnace management, Properzi casting wheel, rolling train control, and rod quality testing."},
    {"name": "gold-refinery-operations", "description": "Operate gold refinery operations including Wohlwill or Miller process management, assay laboratory, melt and pour operations, and chain of custody."},
    {"name": "silver-refinery-operations", "description": "Manage silver refining operations including electrolytic cell management, crystal washing, melting and casting, and assay compliance programs."},
    {"name": "platinum-group-metal-refinery", "description": "Operate platinum group metal refinery operations including PGM separation chemistry, dissolution circuit management, and precious metal accounting."},
    {"name": "hydrometallurgy-plant-ops", "description": "Manage hydrometallurgical plant operations including heap leach irrigation scheduling, SX-EW circuit management, and solution chemistry control."},
    {"name": "precious-metal-inventory-control", "description": "Control precious metal inventories including in-process metal accounting, vault management, assay reconciliation, and regulatory reporting."},
    {"name": "metal-refinery-safety-programs", "description": "Implement safety programs at metal refineries including hot work permits, acid handling procedures, crane safety, and emergency response planning."},
    {"name": "metal-trading-and-hedging-ops", "description": "Manage metal trading and hedging programs including LME pricing, forward sales, option strategies, and mark-to-market reporting."},
]

# Domain: Foundry Operations
skills += [
    {"name": "iron-foundry-operations", "description": "Operate iron foundries including cupola melting management, sand system control, green sand molding operations, and casting quality inspection."},
    {"name": "steel-foundry-operations", "description": "Manage steel foundry operations including induction melting, lost foam and sand casting, heat treatment scheduling, and dimensional inspection."},
    {"name": "aluminum-die-casting-ops", "description": "Operate aluminum die casting operations including die casting machine management, alloy temperature control, die maintenance, and porosity reduction programs."},
    {"name": "investment-casting-operations", "description": "Manage investment casting operations including wax injection, shell building, dewaxing, mold firing, and dimensional inspection programs."},
    {"name": "sand-casting-operations", "description": "Operate sand casting facilities including no-bake sand system management, pattern maintenance, gating design review, and yield optimization."},
    {"name": "foundry-core-making-ops", "description": "Manage foundry core making operations including cold box and warm box core shooter management, core dip operations, and dimensional compliance."},
    {"name": "foundry-heat-treatment-ops", "description": "Operate foundry heat treatment operations including annealing, normalizing, and aging furnace scheduling with metallurgical compliance documentation."},
    {"name": "foundry-quality-assurance", "description": "Execute foundry quality assurance programs including radiographic inspection, dye penetrant testing, magnetic particle inspection, and mechanical testing."},
    {"name": "foundry-pattern-management", "description": "Manage foundry pattern and tooling programs including pattern maintenance, new tooling procurement, pattern life tracking, and revision control."},
    {"name": "foundry-environmental-compliance", "description": "Manage foundry environmental compliance including VOC emission control, baghouse performance, wastewater treatment, and permit reporting."},
]

# Domain: Waste and Recycling Operations
skills += [
    {"name": "materials-recovery-facility-ops", "description": "Operate materials recovery facilities including sorting line management, bale quality control, commodity market monitoring, and contamination reduction programs."},
    {"name": "waste-to-energy-plant-ops", "description": "Manage waste-to-energy plant operations including MSW feed scheduling, grate combustion control, air emissions compliance, and ash management."},
    {"name": "hazardous-waste-treatment-ops", "description": "Operate hazardous waste treatment facilities including waste characterization, treatment technology selection, destruction efficiency verification, and manifest tracking."},
    {"name": "composting-facility-operations", "description": "Manage composting facility operations including feedstock intake, windrow turning schedules, moisture management, and finished compost quality testing."},
    {"name": "landfill-gas-capture-ops", "description": "Operate landfill gas capture systems including wellfield management, gas collection system maintenance, flare and engine operations, and flow monitoring."},
    {"name": "e-waste-processing-operations", "description": "Manage electronic waste processing operations including device shredding, precious metal recovery, CRT glass segregation, and export compliance."},
    {"name": "plastic-recycling-operations", "description": "Operate plastic recycling facilities including polymer sorting, washing and drying, granulation, and regrind quality testing programs."},
    {"name": "metal-recycling-operations", "description": "Manage metal recycling operations including ferrous and non-ferrous sorting, shredder management, baler operations, and scrap quality grading."},
    {"name": "biogas-anaerobic-digestion-ops", "description": "Operate anaerobic digestion facilities including feedstock mixing, digester temperature control, biogas upgrading, and digestate management programs."},
    {"name": "waste-management-compliance", "description": "Manage waste facility regulatory compliance including permit condition monitoring, groundwater sampling, air quality reporting, and agency inspection response."},
]

# Domain: Water and Wastewater Utility Operations
skills += [
    {"name": "drinking-water-treatment-ops", "description": "Operate drinking water treatment plants including coagulation and flocculation control, filter backwash scheduling, disinfection dosing, and regulatory compliance."},
    {"name": "wastewater-treatment-plant-ops", "description": "Manage wastewater treatment plant operations including biological process control, sludge management, effluent quality monitoring, and permit compliance."},
    {"name": "water-distribution-system-ops", "description": "Operate water distribution systems including pressure zone management, storage tank turnover, booster pump scheduling, and main break response."},
    {"name": "sewer-collection-system-ops", "description": "Manage sewer collection system operations including lift station monitoring, I/I program management, FOG enforcement, and SSO response."},
    {"name": "stormwater-management-ops", "description": "Operate stormwater management systems including detention basin inspection, MS4 permit compliance, illicit discharge detection, and BMP maintenance."},
    {"name": "water-utility-asset-management", "description": "Manage water utility assets including condition assessment programs, pipe replacement prioritization, and capital improvement plan development."},
    {"name": "water-loss-control-programs", "description": "Develop water loss control programs including pressure management, leak detection surveys, meter accuracy testing, and NRW reduction targets."},
    {"name": "desalination-plant-operations", "description": "Operate desalination facilities including RO membrane management, energy recovery integration, concentrate disposal compliance, and product water quality."},
    {"name": "water-utility-scada-ops", "description": "Operate water utility SCADA systems including remote monitoring, alarm management, historian data management, and cybersecurity programs."},
    {"name": "water-utility-customer-service", "description": "Manage water utility customer service operations including billing system management, leak adjustment programs, and meter replacement workflows."},
]

# Domain: Electric Utility Grid Operations
skills += [
    {"name": "transmission-system-operations", "description": "Operate high-voltage transmission systems including load flow management, reactive power control, stability monitoring, and outage coordination."},
    {"name": "distribution-grid-operations", "description": "Manage electric distribution grid operations including switching order management, fault isolation, restoration planning, and reliability tracking."},
    {"name": "energy-management-system-ops", "description": "Operate utility energy management systems including state estimator management, automatic generation control, and contingency analysis."},
    {"name": "substation-operations-mgmt", "description": "Manage substation operations including equipment inspection scheduling, relay testing coordination, transformer oil management, and switching programs."},
    {"name": "grid-modernization-programs", "description": "Lead grid modernization initiatives including AMI deployment, volt-VAR optimization, distribution automation, and grid resilience investments."},
    {"name": "electric-utility-outage-mgmt", "description": "Manage electric utility outage management including OMS operations, storm response coordination, crew dispatch, and customer notification workflows."},
    {"name": "electricity-trading-ops", "description": "Manage electricity market trading operations including day-ahead and real-time bid submission, ancillary service management, and settlement verification."},
    {"name": "power-system-protection-ops", "description": "Manage power system protection programs including relay settings management, protection coordination studies, and misoperation investigation."},
    {"name": "utility-vegetation-management", "description": "Manage utility vegetation management programs including tree trimming contractor management, cycle planning, and right-of-way encroachment programs."},
    {"name": "distributed-energy-resource-mgmt", "description": "Manage distributed energy resource programs including DER interconnection, DERMS platform operations, and aggregated dispatch coordination."},
]

# Domain: Natural Gas Distribution Operations
skills += [
    {"name": "gas-distribution-system-ops", "description": "Operate natural gas distribution systems including pressure regulation, leak survey programs, odorization management, and emergency response."},
    {"name": "gas-metering-operations", "description": "Manage gas meter operations including AMR/AMI meter deployment, meter reading management, meter accuracy testing, and meter exchange programs."},
    {"name": "pipeline-integrity-management", "description": "Implement pipeline integrity management programs including ILI survey scheduling, direct assessment, anomaly investigation, and regulatory reporting."},
    {"name": "gas-storage-field-operations", "description": "Operate gas storage field operations including injection and withdrawal scheduling, wellhead maintenance, and inventory reconciliation."},
    {"name": "liquefied-natural-gas-ops", "description": "Manage LNG facility operations including liquefaction plant management, storage tank operations, regasification scheduling, and truck loading."},
    {"name": "gas-system-planning-ops", "description": "Manage gas distribution system planning including load forecasting, pipe replacement prioritization, and capacity expansion analysis."},
    {"name": "gas-utility-field-operations", "description": "Coordinate gas utility field operations including service line installation, meter set management, emergency locate response, and contractor oversight."},
    {"name": "gas-quality-management", "description": "Manage natural gas quality programs including BTU measurement, gas chromatograph maintenance, interchangeability compliance, and tariff verification."},
    {"name": "gas-supply-portfolio-mgmt", "description": "Manage gas supply portfolios including contract administration, curtailment planning, balancing programs, and market price risk management."},
    {"name": "gas-utility-regulatory-mgmt", "description": "Navigate gas utility regulatory compliance including rate case preparation, commission reporting, safety compliance filings, and tariff management."},
]

# Domain: Mining Operations
skills += [
    {"name": "open-pit-mine-operations", "description": "Manage open pit mining operations including drill and blast design, fleet dispatch optimization, bench advancement planning, and waste dump management."},
    {"name": "underground-mine-operations", "description": "Operate underground mining operations including development advance scheduling, stope sequencing, ventilation management, and ground support programs."},
    {"name": "mine-planning-and-scheduling", "description": "Develop mine production plans including block model scheduling, reserve estimation, equipment fleet planning, and life-of-mine scenario analysis."},
    {"name": "mineral-processing-plant-ops", "description": "Operate mineral processing plants including comminution circuit management, flotation circuit optimization, tailings disposal, and concentrate quality control."},
    {"name": "mine-maintenance-management", "description": "Manage mining equipment maintenance including CMMS operations, component change-out scheduling, planned component replacement, and condition monitoring."},
    {"name": "mine-geotechnical-management", "description": "Manage geotechnical programs at mines including slope stability monitoring, ground movement instrumentation, rock mechanics investigation, and risk assessment."},
    {"name": "mine-water-management", "description": "Manage mine water operations including dewatering pump scheduling, water balance modeling, treatment plant operations, and regulatory compliance."},
    {"name": "mine-environmental-compliance", "description": "Navigate mining environmental compliance including tailings storage facility management, acid drainage monitoring, and closure plan management."},
    {"name": "mine-safety-management", "description": "Implement mine safety management systems including hazard identification, safety observation programs, emergency response planning, and regulator interface."},
    {"name": "mineral-exploration-management", "description": "Manage mineral exploration programs including drill hole management, sampling and assay coordination, resource estimation, and drill program planning."},
]

# Domain: Oil and Gas Upstream Operations
skills += [
    {"name": "drilling-operations-management", "description": "Manage oil and gas well drilling operations including AFE management, rig scheduling, BHA design, and NPT reduction programs."},
    {"name": "well-completion-operations", "description": "Coordinate well completion operations including perforating design, hydraulic fracturing execution, plug milling, and flowback management."},
    {"name": "production-operations-mgmt", "description": "Manage oil and gas production facility operations including separator management, production allocation, export metering, and artificial lift optimization."},
    {"name": "reservoir-management-ops", "description": "Implement reservoir management programs including production surveillance, pressure transient analysis, water injection management, and EOR programs."},
    {"name": "oil-and-gas-hse-management", "description": "Manage upstream oil and gas HSE programs including permit-to-work, H2S safety, emergency response, and major accident hazard management."},
    {"name": "upstream-supply-chain-ops", "description": "Manage upstream oil and gas supply chains including materials procurement, rig supply logistics, vendor management, and inventory optimization."},
    {"name": "well-integrity-management", "description": "Implement well integrity management programs including barrier verification, annulus pressure monitoring, workover planning, and risk ranking."},
    {"name": "oil-and-gas-gas-processing", "description": "Operate oil and gas processing facilities including amine sweetening, glycol dehydration, NGL extraction, and compression management."},
    {"name": "production-geology-operations", "description": "Manage production geology programs including well log correlation, completion interval selection, infill drilling identification, and geological modeling."},
    {"name": "offshore-platform-operations", "description": "Operate offshore platform facilities including topsides management, marine riser monitoring, subsea system operations, and helicopter logistic coordination."},
]

# Domain: Petrochemical Plant Operations
skills += [
    {"name": "ethylene-cracker-operations", "description": "Operate ethylene cracking units including furnace coil management, quench system control, fractionation column management, and decoking scheduling."},
    {"name": "polyethylene-plant-operations", "description": "Manage polyethylene production operations including gas phase reactor control, catalyst management, pelletizing system operations, and product quality transitions."},
    {"name": "polypropylene-plant-operations", "description": "Operate polypropylene production units including bulk slurry loop reactor management, catalyst feed systems, and product grade change execution."},
    {"name": "aromatics-complex-operations", "description": "Manage aromatics complex operations including catalytic reforming, xylene isomerization, paraxylene crystallization, and benzene extraction."},
    {"name": "petrochemical-utilities-ops", "description": "Operate petrochemical plant utility systems including steam and condensate management, cooling water system operations, and nitrogen generation."},
    {"name": "petrochemical-product-blending", "description": "Manage petrochemical product blending operations including in-line and batch blending, quality compliance certification, and blend optimization."},
    {"name": "petrochemical-storage-tank-ops", "description": "Operate petrochemical storage tank farms including inventory management, product segregation, tank gauging, and floating roof inspection programs."},
    {"name": "petrochemical-catalyst-mgmt", "description": "Manage petrochemical catalyst programs including loading and unloading operations, regeneration scheduling, and performance monitoring."},
    {"name": "petrochemical-reliability-programs", "description": "Implement reliability programs at petrochemical plants including RCM analysis, turnaround planning, rotating equipment monitoring, and bad actor management."},
    {"name": "petrochemical-safety-systems", "description": "Manage petrochemical plant safety systems including SIS testing programs, firegas detection maintenance, emergency shutdown valve testing, and PSSR compliance."},
]

# Domain: Refinery Operations
skills += [
    {"name": "crude-distillation-unit-ops", "description": "Operate crude distillation units including crude blend management, atmospheric and vacuum column operations, and heat exchange optimization."},
    {"name": "fluid-catalytic-cracking-ops", "description": "Manage fluid catalytic cracking unit operations including catalyst addition, regenerator air management, riser temperature control, and yield optimization."},
    {"name": "hydroprocessing-unit-ops", "description": "Operate hydrotreating and hydrocracking units including reactor temperature management, hydrogen purity control, and catalyst deactivation monitoring."},
    {"name": "refinery-planning-and-scheduling", "description": "Develop refinery production plans including crude selection optimization, LP model management, tank farm scheduling, and margin maximization."},
    {"name": "refinery-blending-operations", "description": "Manage refinery product blending including gasoline recipe management, cetane improvement blending, and aviation fuel certification workflows."},
    {"name": "refinery-utilities-management", "description": "Manage refinery utility systems including hydrogen plant operations, steam balance optimization, fuel gas system management, and power co-generation."},
    {"name": "refinery-energy-management", "description": "Optimize refinery energy consumption including heat integration programs, fired heater efficiency improvement, and energy audit execution."},
    {"name": "refinery-turnaround-management", "description": "Plan and execute refinery turnarounds including scope freeze, contractor management, critical path scheduling, and startup readiness verification."},
    {"name": "refinery-environmental-compliance", "description": "Manage refinery environmental compliance including flare minimization programs, VOC fugitive emission surveys, and air permit compliance reporting."},
    {"name": "refinery-laboratory-operations", "description": "Operate refinery quality control laboratories including crude assay program, product specification testing, and in-process quality monitoring."},
]

# Domain: Power Plant Operations
skills += [
    {"name": "combined-cycle-plant-ops", "description": "Operate combined cycle power plants including gas turbine management, heat recovery steam generator operations, and steam turbine control."},
    {"name": "coal-power-plant-operations", "description": "Manage coal-fired power plant operations including coal handling, pulverizer management, boiler combustion optimization, and emissions compliance."},
    {"name": "nuclear-power-plant-operations", "description": "Support nuclear power plant operations including reactor operations support, outage management, radiation protection programs, and NRC compliance."},
    {"name": "hydropower-plant-operations", "description": "Operate hydroelectric power plant facilities including unit dispatch, penstock management, tailwater monitoring, and fish passage compliance."},
    {"name": "peaking-power-plant-ops", "description": "Manage peaking power plant operations including fast-start procedures, cold start optimization, ancillary service delivery, and capacity test management."},
    {"name": "power-plant-maintenance-mgmt", "description": "Implement power plant maintenance programs including turbine inspection scheduling, boiler tube management, generator rewind planning, and CMMS operations."},
    {"name": "power-plant-chemistry-program", "description": "Manage power plant water chemistry programs including cycle chemistry monitoring, condensate polisher management, and chemistry excursion response."},
    {"name": "power-plant-outage-planning", "description": "Plan power plant outages including scope development, contractor pre-qualification, critical path scheduling, and return-to-service criteria."},
    {"name": "power-plant-environmental-mgmt", "description": "Manage power plant environmental compliance including air emissions monitoring, cooling water discharge permits, and ash disposal site management."},
    {"name": "power-plant-reliability-programs", "description": "Implement power plant reliability programs including RCM analysis, predictive maintenance, equivalent availability tracking, and NERC compliance."},
]

# Domain: Hydrogen Production and Distribution
skills += [
    {"name": "steam-methane-reforming-ops", "description": "Operate steam methane reforming hydrogen plants including reformer furnace management, WGS reactor control, and PSA unit operations."},
    {"name": "electrolysis-hydrogen-production", "description": "Manage water electrolysis hydrogen production including PEM and alkaline electrolyzer operations, stack performance monitoring, and purification."},
    {"name": "hydrogen-storage-operations", "description": "Operate hydrogen storage facilities including compressed tank management, liquid hydrogen vessel operations, and metal hydride storage systems."},
    {"name": "hydrogen-distribution-logistics", "description": "Manage hydrogen distribution logistics including tube trailer fleet management, pipeline injection operations, and dispensing station maintenance."},
    {"name": "hydrogen-fueling-station-ops", "description": "Operate hydrogen fueling stations including compressor management, pre-cooling system maintenance, dispenser protocol compliance, and safety system testing."},
    {"name": "green-hydrogen-project-ops", "description": "Manage green hydrogen project operations including renewable power integration, electrolyzer performance optimization, and green certificate tracking."},
    {"name": "hydrogen-safety-management", "description": "Implement hydrogen safety programs including leak detection systems, hydrogen specific HAZOP, emergency response planning, and personnel training."},
    {"name": "hydrogen-quality-management", "description": "Manage hydrogen quality assurance programs including SAE J2719 compliance, fuel cell grade purity testing, and contaminant monitoring."},
    {"name": "ammonia-synthesis-operations", "description": "Operate ammonia synthesis plants including Haber-Bosch converter management, synthesis loop pressure control, and refrigeration system operations."},
    {"name": "hydrogen-off-take-management", "description": "Manage hydrogen offtake agreements including delivery scheduling, volume reconciliation, pricing management, and supply reliability reporting."},
]

# Domain: Construction Aggregates and Ready-Mix
skills += [
    {"name": "quarry-operations-management", "description": "Manage quarry extraction operations including drill and blast design, bench management, haul road maintenance, and aggregate quality programs."},
    {"name": "aggregate-processing-plant-ops", "description": "Operate aggregate crushing and screening plants including crusher management, conveyor system maintenance, and product gradation compliance."},
    {"name": "ready-mix-concrete-production", "description": "Manage ready-mix concrete production operations including batch plant operations, mix design management, truck scheduling, and quality control."},
    {"name": "asphalt-plant-operations", "description": "Operate asphalt mixing plants including drum dryer management, aggregate blending, bitumen storage, and mix temperature compliance."},
    {"name": "precast-concrete-manufacturing", "description": "Manage precast concrete manufacturing operations including form management, reinforcement placement, curing program, and structural inspection."},
    {"name": "concrete-testing-laboratory", "description": "Operate concrete testing laboratories including fresh concrete testing, cylinder break programs, and QC reporting for construction projects."},
    {"name": "aggregate-inventory-management", "description": "Manage aggregate stockpile inventories including pile segregation, inventory reconciliation, quality certification, and customer order fulfillment."},
    {"name": "quarry-environmental-compliance", "description": "Manage quarry environmental compliance including stormwater SWPPP management, noise monitoring, reclamation plan execution, and permit reporting."},
    {"name": "concrete-admixture-management", "description": "Manage concrete admixture programs including chemical admixture qualification, dosage optimization, and compatibility testing with local cement sources."},
    {"name": "aggregate-logistics-management", "description": "Manage aggregate distribution logistics including truck and rail shipment coordination, customer delivery scheduling, and weight ticket management."},
]

# Domain: Geotechnical and Environmental Testing Services
skills += [
    {"name": "geotechnical-testing-services", "description": "Operate geotechnical testing laboratories including soil classification, consolidation testing, triaxial strength testing, and compaction standard services."},
    {"name": "environmental-lab-services", "description": "Manage environmental testing laboratory services including soil and water analysis, chain of custody management, and detection limit compliance."},
    {"name": "construction-materials-testing", "description": "Provide construction materials testing services including concrete cylinder testing, asphalt core analysis, and fill compaction inspection."},
    {"name": "nondestructive-testing-services", "description": "Deliver nondestructive testing services including UT thickness measurement, radiographic inspection, magnetic particle testing, and dye penetrant inspection."},
    {"name": "industrial-hygiene-services", "description": "Provide industrial hygiene sampling services including air monitoring, noise dosimetry, wipe sampling, and biological monitoring program execution."},
    {"name": "groundwater-monitoring-services", "description": "Manage groundwater monitoring programs including well sampling logistics, analytical data management, and plume tracking report preparation."},
    {"name": "phase-i-ii-environmental-assessment", "description": "Conduct Phase I and Phase II environmental site assessments including records review, site reconnaissance, soil and groundwater sampling, and report preparation."},
    {"name": "asbestos-lead-testing-services", "description": "Provide asbestos and lead-based paint testing services including bulk sampling, XRF screening, clearance testing, and abatement project oversight."},
    {"name": "geophysical-survey-services", "description": "Conduct geophysical survey programs including GPR, seismic refraction, electrical resistivity, and magnetic surveys for subsurface characterization."},
    {"name": "wetlands-ecological-services", "description": "Deliver wetlands and ecological assessment services including jurisdictional delineation, biological surveys, and mitigation planning support."},
]

# Domain: Fleet and Transportation Management
skills += [
    {"name": "commercial-fleet-management", "description": "Manage commercial vehicle fleets including GPS tracking, driver performance monitoring, preventive maintenance scheduling, and fuel management."},
    {"name": "fleet-maintenance-operations", "description": "Operate fleet maintenance programs including work order management, parts inventory control, warranty claim tracking, and uptime optimization."},
    {"name": "driver-compliance-management", "description": "Manage commercial driver compliance including HOS tracking, CSA score management, drug and alcohol testing program, and MVR monitoring."},
    {"name": "fleet-procurement-management", "description": "Manage fleet procurement programs including vehicle spec development, bid management, lease versus buy analysis, and disposal programs."},
    {"name": "freight-brokerage-operations", "description": "Operate freight brokerage operations including carrier sourcing, load matching, rate negotiation, and carrier performance management."},
    {"name": "dedicated-contract-carriage", "description": "Manage dedicated contract carriage operations including route design, driver management, on-site maintenance coordination, and customer reporting."},
    {"name": "intermodal-operations-mgmt", "description": "Coordinate intermodal transportation operations including container drayage scheduling, rail segment management, and asset utilization tracking."},
    {"name": "cold-chain-transport-ops", "description": "Manage temperature-controlled transportation operations including reefer unit monitoring, pre-cooling protocols, and temperature excursion response."},
    {"name": "fleet-telematics-analytics", "description": "Deploy fleet telematics analytics programs including idle reduction campaigns, route optimization, harsh event reduction, and ROI reporting."},
    {"name": "fleet-sustainability-programs", "description": "Implement fleet sustainability programs including EV transition planning, carbon reporting, alternative fuel adoption, and green fleet certification."},
]

# Domain: Airport and Aviation Ground Operations
skills += [
    {"name": "airport-ground-handling-ops", "description": "Manage airline ground handling operations including ramp coordination, baggage handling, aircraft pushback, and ground support equipment management."},
    {"name": "airport-terminal-operations", "description": "Operate airport terminal facilities including gate assignment optimization, passenger flow management, security checkpoint coordination, and concession oversight."},
    {"name": "air-cargo-operations-mgmt", "description": "Manage air cargo terminal operations including ULD management, hazmat acceptance, x-ray screening, and shipment tracing workflows."},
    {"name": "airport-fueling-operations", "description": "Operate airport aircraft fueling services including fuel farm management, hydrant system maintenance, into-plane fueling operations, and quality control."},
    {"name": "aircraft-line-maintenance-ops", "description": "Coordinate aircraft line maintenance operations including AOG response, MEL management, tech log management, and duty technician scheduling."},
    {"name": "airport-safety-compliance", "description": "Manage airport airside safety programs including FOD programs, wildlife hazard management, runway incursion prevention, and Part 139 compliance."},
    {"name": "airport-capacity-planning", "description": "Develop airport capacity plans including slot management, gate utilization modeling, apron capacity analysis, and terminal expansion coordination."},
    {"name": "aircraft-cabin-cleaning-ops", "description": "Manage aircraft cabin cleaning operations including turnaround cleaning scheduling, deep cleaning programs, and cabin product inventory management."},
    {"name": "airport-it-systems-ops", "description": "Operate airport IT systems including CUTE/CUSS management, FIDS operations, baggage reconciliation system, and biometric passenger facilitation."},
    {"name": "aircraft-deicing-operations", "description": "Manage aircraft deicing operations including glycol inventory management, holdover time compliance, deicing pad scheduling, and fluid recovery."},
]

# Domain: Rail Transportation Operations
skills += [
    {"name": "freight-rail-operations-mgmt", "description": "Manage freight railroad operations including train scheduling, locomotive assignment, crew management, and service reliability tracking."},
    {"name": "passenger-rail-operations-mgmt", "description": "Operate passenger rail services including train operations management, on-time performance tracking, service recovery, and crew assignment."},
    {"name": "rail-track-maintenance-mgmt", "description": "Manage railroad track maintenance programs including surfacing and lining scheduling, rail replacement prioritization, and geometry defect management."},
    {"name": "rail-signal-maintenance-ops", "description": "Operate railroad signal maintenance programs including signal test scheduling, CTC system management, grade crossing equipment maintenance, and FRA compliance."},
    {"name": "rail-equipment-maintenance-ops", "description": "Manage railroad rolling stock maintenance including locomotive shop management, car repair operations, wheel truing scheduling, and warranty administration."},
    {"name": "railway-network-control-ops", "description": "Operate railway network control centers including train movement authority management, delay mitigation, platform sequencing, and incident response."},
    {"name": "rail-intermodal-terminal-ops", "description": "Manage intermodal terminal operations including crane and reach stacker management, yard hostler dispatch, gate management, and dwell time control."},
    {"name": "rail-safety-management", "description": "Implement railroad safety management systems including close call reporting, operating rule compliance, employee safety training, and FRA accident reporting."},
    {"name": "rail-energy-optimization", "description": "Optimize energy consumption for rail operations including regenerative braking energy recovery, eco-driving programs, and idle reduction strategies."},
    {"name": "rail-freight-car-management", "description": "Manage railroad freight car fleet operations including car hire accounting, bad order management, car distribution, and cycle time optimization."},
]

# Domain: Port and Logistics Hub Operations
skills += [
    {"name": "container-terminal-operations", "description": "Manage container terminal operations including vessel berthing, crane productivity, yard block management, and truck appointment systems."},
    {"name": "bulk-terminal-operations", "description": "Operate bulk cargo terminals including shiploading and unloading equipment management, stockpile management, and conveyor system maintenance."},
    {"name": "liquid-bulk-terminal-ops", "description": "Manage liquid bulk terminal operations including tank farm management, marine vapor control, vessel manifold connections, and product quality programs."},
    {"name": "port-customs-operations", "description": "Coordinate port customs operations including manifest submission, cargo examination scheduling, customs bond management, and free trade zone compliance."},
    {"name": "port-security-operations", "description": "Manage port security operations including ISPS compliance, access control systems, container inspection programs, and maritime security committee management."},
    {"name": "port-equipment-maintenance", "description": "Maintain port equipment including ship-to-shore crane inspection, rubber-tired gantry maintenance, reach stacker service scheduling, and spare parts management."},
    {"name": "port-vessel-traffic-services", "description": "Operate vessel traffic services including arrival and departure coordination, anchorage management, pilot coordination, and vessel scheduling systems."},
    {"name": "port-environmental-compliance", "description": "Manage port environmental compliance including cold ironing programs, air emission inventories, stormwater SWPPP management, and spill response."},
    {"name": "port-it-systems-management", "description": "Manage port IT systems including terminal operating system administration, gate OCR management, and EDI gateway operations."},
    {"name": "port-capacity-planning", "description": "Develop port capacity plans including throughput modeling, berth utilization analysis, yard expansion studies, and equipment fleet planning."},
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
