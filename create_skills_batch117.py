import os

base = r"c:\Users\mirza\MAARS-Command\.claude\skills"

# Domain: Industrial Laundry and Linen Services
skills = [
    {"name": "linen-inventory-management", "description": "Manage commercial linen and garment inventories including par level setting, loss tracking, item lifecycle management, and customer allocation."},
    {"name": "industrial-laundry-production", "description": "Operate industrial laundry production lines including wash formula programming, tunnel washer scheduling, and throughput optimization."},
    {"name": "linen-delivery-route-ops", "description": "Manage linen delivery route operations including load sequencing, driver dispatch, on-site exchange procedures, and route efficiency metrics."},
    {"name": "laundry-chemical-management", "description": "Manage laundry chemical programs including product selection, dosing system calibration, wash quality monitoring, and supplier performance."},
    {"name": "linen-repair-restoration", "description": "Operate linen repair and restoration programs including mending workflows, stain classification, garment conditioning, and item retirement criteria."},
    {"name": "healthcare-linen-compliance", "description": "Manage healthcare linen compliance programs including HLAC accreditation, infection control protocols, and hygienically clean textile certification."},
    {"name": "laundry-equipment-maintenance", "description": "Maintain commercial laundry equipment including washer-extractor service, dryer heat management, conveyor system upkeep, and breakdown response."},
    {"name": "laundry-water-energy-mgmt", "description": "Optimize laundry water and energy consumption including heat recovery systems, water reuse programs, and utility cost benchmarking."},
    {"name": "garment-tracking-rfid", "description": "Deploy RFID garment tracking systems including tag programming, reader network installation, scan point management, and reporting dashboards."},
    {"name": "laundry-customer-service-ops", "description": "Manage laundry customer service operations including complaint resolution, service level tracking, account retention, and contract renewal programs."},
]

# Domain: Dry Cleaning and Textile Care Services
skills += [
    {"name": "dry-cleaning-solvent-mgmt", "description": "Manage dry cleaning solvent programs including perc alternative selection, still operation, solvent recovery, and environmental compliance reporting."},
    {"name": "garment-inspection-spotting", "description": "Execute garment inspection and spotting workflows including fabric identification, stain treatment chemistry, and pre-spotting procedures."},
    {"name": "textile-care-labeling-compliance", "description": "Navigate textile care labeling compliance including FTC care label rules, international symbols, and customer communication on care limitations."},
    {"name": "alteration-tailoring-ops", "description": "Manage garment alteration and tailoring operations including work order intake, skilled labor scheduling, fitting appointment coordination, and quality inspection."},
    {"name": "wedding-special-garment-services", "description": "Operate specialty garment services for weddings and formalwear including gown cleaning, preservation packaging, and heirloom storage programs."},
    {"name": "dry-cleaning-pos-operations", "description": "Operate dry cleaning point-of-sale systems including ticket management, barcode tracking, customer notification, and payment processing."},
    {"name": "leather-suede-care-services", "description": "Provide leather and suede care services including cleaning protocols, conditioning treatments, color restoration, and repair services."},
    {"name": "drapery-cleaning-operations", "description": "Manage drapery and soft furnishing cleaning operations including on-site cleaning, take-down coordination, and reinstallation scheduling."},
    {"name": "dry-cleaning-franchise-ops", "description": "Operate dry cleaning franchise locations including brand standard compliance, supply procurement, royalty reporting, and field support coordination."},
    {"name": "textile-restoration-disaster", "description": "Provide textile restoration services for disaster recovery including smoke, water, and mold damage assessment, treatment protocols, and insurance documentation."},
]

# Domain: Automotive Paint and Coatings Manufacturing
skills += [
    {"name": "automotive-oem-coating-dev", "description": "Develop automotive OEM coating systems including primer, basecoat, and clearcoat formulation, adhesion testing, and OEM approval workflows."},
    {"name": "automotive-color-matching", "description": "Manage automotive color matching programs including spectrophotometer analysis, formula databases, and OEM color library maintenance."},
    {"name": "automotive-coating-application", "description": "Optimize automotive coating application processes including spray equipment selection, film build control, and bake cure cycle management."},
    {"name": "automotive-paint-qa-testing", "description": "Execute automotive paint quality testing including gloss, adhesion, chip resistance, weathering, and chemical resistance test programs."},
    {"name": "automotive-voc-compliance", "description": "Manage VOC compliance for automotive coatings including HAP tracking, permit limit management, and reformulation programs for regulatory compliance."},
    {"name": "refinish-coating-product-line", "description": "Manage automotive refinish coating product lines including SKU rationalization, tinter system management, and refinish distributor support programs."},
    {"name": "automotive-coating-supply-chain", "description": "Manage automotive coating supply chains including pigment procurement, resin sourcing, batch traceability, and safety stock management."},
    {"name": "coating-application-training", "description": "Design and deliver coating application training programs for body shop technicians including spray technique, mix ratio certification, and troubleshooting guides."},
    {"name": "automotive-paint-booth-ops", "description": "Operate automotive paint booth facilities including airflow validation, temperature control, contamination management, and regulatory compliance."},
    {"name": "automotive-coating-innovation", "description": "Drive automotive coating innovation programs including self-healing clear coats, antimicrobial coatings, and waterborne technology conversion projects."},
]

# Domain: Printing Ink Manufacturing
skills += [
    {"name": "ink-formulation-management", "description": "Manage printing ink formulation programs including colorant selection, vehicle chemistry, viscosity specification, and formula version control."},
    {"name": "ink-color-standards-mgmt", "description": "Maintain ink color standards programs including Pantone matching, spectral data management, and proof approval workflows."},
    {"name": "ink-manufacturing-ops", "description": "Operate ink manufacturing facilities including mixing and milling operations, filling line management, and batch record documentation."},
    {"name": "ink-substrate-compatibility", "description": "Manage ink-substrate compatibility programs including adhesion testing, printability evaluation, and press trial coordination."},
    {"name": "digital-ink-product-mgmt", "description": "Manage digital printing ink product lines including inkjet fluid development, printhead compatibility testing, and OEM certification management."},
    {"name": "ink-regulatory-compliance", "description": "Navigate printing ink regulatory compliance including food contact migration testing, heavy metal restrictions, and REACH substance reporting."},
    {"name": "ink-raw-material-sourcing", "description": "Manage ink raw material sourcing including pigment procurement, resin qualification, and alternative raw material development programs."},
    {"name": "ink-technical-service", "description": "Provide ink technical service to printing customers including press-side troubleshooting, ink optimization, and new substrate launch support."},
    {"name": "ink-packaging-labeling-ops", "description": "Manage ink packaging and labeling operations including container selection, SDS compliance, hazmat labeling, and fill weight accuracy."},
    {"name": "ink-waste-management", "description": "Manage ink waste and byproduct programs including solvent recovery, waste ink reclaim, and hazardous waste disposal compliance."},
]

# Domain: Adhesive and Sealant Manufacturing
skills += [
    {"name": "adhesive-formulation-dev", "description": "Develop adhesive and sealant formulations including polymer selection, curing agent design, and performance testing against application requirements."},
    {"name": "adhesive-application-engineering", "description": "Provide adhesive application engineering support including dispensing equipment selection, cure process design, and joint design optimization."},
    {"name": "adhesive-testing-qualification", "description": "Execute adhesive testing and qualification programs including peel, shear, and impact testing, environmental aging, and application-specific performance standards."},
    {"name": "sealant-construction-markets", "description": "Manage sealant product programs for construction markets including weatherseal, fire-rated sealant, and structural glazing product lines."},
    {"name": "hot-melt-adhesive-ops", "description": "Manage hot melt adhesive product lines including application temperature profiles, open time optimization, and melt equipment maintenance programs."},
    {"name": "pressure-sensitive-adhesive-mfg", "description": "Operate pressure-sensitive adhesive manufacturing including coating line management, liner selection, and peel force quality control."},
    {"name": "adhesive-regulatory-compliance", "description": "Navigate adhesive regulatory compliance including food contact approval, toy safety standards, medical device biocompatibility, and REACH SVHC management."},
    {"name": "structural-bonding-programs", "description": "Manage structural bonding programs for aerospace, automotive, and industrial assembly applications including bond line quality and certification support."},
    {"name": "adhesive-supply-chain-mgmt", "description": "Manage adhesive supply chains including raw material supplier qualification, inventory management, and global distribution logistics."},
    {"name": "adhesive-market-dev-programs", "description": "Drive adhesive market development programs including application workshops, demonstration labs, and OEM specification programs."},
]

# Domain: Industrial Coatings Application Services
skills += [
    {"name": "industrial-surface-prep-ops", "description": "Manage industrial surface preparation operations including blast cleaning, power tool preparation, and profile measurement for coating applications."},
    {"name": "industrial-coating-inspection", "description": "Conduct industrial coating inspections including DFT measurement, holiday testing, adhesion testing, and NACE/SSPC compliance documentation."},
    {"name": "tank-vessel-lining-services", "description": "Manage tank and vessel lining services including interior coating selection, confined space entry procedures, and cure validation programs."},
    {"name": "structural-steel-coating-ops", "description": "Operate structural steel coating programs including shop prime application, field touch-up coordination, and galvanic protection systems."},
    {"name": "pipeline-coating-services", "description": "Provide pipeline coating services including fusion bonded epoxy application, field joint coating, and cathodic protection system coordination."},
    {"name": "marine-coating-services", "description": "Manage marine coating services including drydock coordination, antifouling application, and underwater hull maintenance programs."},
    {"name": "floor-coating-installation", "description": "Install industrial floor coatings including epoxy, polyurethane, and MMA systems, surface preparation, joint filling, and cure management."},
    {"name": "thermal-spray-coating-ops", "description": "Operate thermal spray coating services including HVOF, arc spray, and plasma spray applications for wear and corrosion protection."},
    {"name": "fireproofing-application-services", "description": "Apply passive fire protection coatings including intumescent paint, cementitious spray, and board systems with fire resistance documentation."},
    {"name": "coating-contractor-safety-mgmt", "description": "Manage safety programs for coating contracting operations including respiratory protection, confined space, and hazmat communication compliance."},
]

# Domain: Corrosion Engineering Services
skills += [
    {"name": "corrosion-risk-assessment", "description": "Conduct corrosion risk assessments including material selection reviews, environment characterization, and corrosion rate prediction modeling."},
    {"name": "cathodic-protection-ops", "description": "Operate cathodic protection systems including impressed current and sacrificial anode systems, potential surveys, and rectifier management."},
    {"name": "corrosion-monitoring-programs", "description": "Deploy corrosion monitoring programs including coupon installation, ER probe networks, and inhibitor injection optimization."},
    {"name": "corrosion-inhibitor-programs", "description": "Manage corrosion inhibitor programs including chemical selection, injection rate optimization, residual monitoring, and performance reporting."},
    {"name": "materials-selection-consulting", "description": "Provide materials selection consulting services including corrosion-resistant alloy recommendations, coating system selection, and failure mode analysis."},
    {"name": "pipeline-integrity-management", "description": "Manage pipeline integrity programs including ILI data analysis, corrosion anomaly assessment, and remaining life calculations."},
    {"name": "atmospheric-corrosion-programs", "description": "Manage atmospheric corrosion programs including ISO corrosivity classification, inspection planning, and protective coating specification."},
    {"name": "microbial-corrosion-control", "description": "Control microbiologically influenced corrosion including biological sampling, biocide treatment programs, and monitoring system deployment."},
    {"name": "corrosion-failure-analysis", "description": "Conduct corrosion failure analysis including specimen examination, root cause determination, metallurgical testing, and corrective action recommendations."},
    {"name": "offshore-corrosion-management", "description": "Manage offshore structure corrosion programs including splash zone protection, subsea cathodic protection, and marine growth management."},
]

# Domain: Heat Treatment Contract Services
skills += [
    {"name": "heat-treat-process-planning", "description": "Develop heat treatment process plans including temperature cycle specification, atmosphere selection, and fixture design for customer parts."},
    {"name": "furnace-operations-management", "description": "Manage heat treatment furnace operations including load scheduling, temperature uniformity surveys, and equipment qualification per AMS2750."},
    {"name": "atmosphere-control-management", "description": "Manage controlled atmosphere heat treatment including endothermic gas generation, carbon potential control, and dew point monitoring."},
    {"name": "quench-system-operations", "description": "Operate quenching systems including oil, water, polymer, and press quench operations with agitation control and quench severity measurement."},
    {"name": "heat-treat-quality-systems", "description": "Implement heat treatment quality systems including Nadcap accreditation, customer approval programs, and metallurgical laboratory management."},
    {"name": "vacuum-heat-treatment-ops", "description": "Operate vacuum heat treatment services including bright annealing, vacuum hardening, and low-pressure carburizing processes."},
    {"name": "induction-heat-treatment-ops", "description": "Manage induction heat treatment operations including coil design, power supply programming, and surface hardness pattern verification."},
    {"name": "carburizing-nitriding-ops", "description": "Operate case hardening services including gas carburizing, nitriding, and ferritic nitrocarburizing with case depth verification programs."},
    {"name": "heat-treat-lab-services", "description": "Provide heat treatment laboratory services including hardness testing, microstructure analysis, case depth measurement, and test certificate generation."},
    {"name": "cryogenic-treatment-services", "description": "Manage cryogenic treatment services for tooling and wear components including temperature cycle specification, dimensional stability assessment, and wear performance tracking."},
]

# Domain: Electroplating and Surface Finishing Services
skills += [
    {"name": "plating-line-operations", "description": "Operate electroplating production lines including rack and barrel plating, current density control, bath chemistry management, and throughput optimization."},
    {"name": "plating-bath-chemistry-mgmt", "description": "Manage electroplating bath chemistry including Hull cell testing, metal concentration analysis, additive dosing, and bath maintenance protocols."},
    {"name": "plating-wastewater-treatment", "description": "Operate plating wastewater treatment systems including metal hydroxide precipitation, hexavalent chrome reduction, and permit compliance reporting."},
    {"name": "anodizing-operations", "description": "Manage anodizing services including sulfuric, hard coat, and chromic acid anodize processes with seal quality and oxide thickness control."},
    {"name": "precious-metal-plating-ops", "description": "Operate precious metal plating services including gold, silver, platinum, and palladium plating with metal drag-out recovery and accountability programs."},
    {"name": "plating-quality-inspection", "description": "Execute plating quality inspection programs including coating thickness measurement, adhesion testing, porosity testing, and customer specification compliance."},
    {"name": "zinc-nickel-plating-programs", "description": "Manage zinc-nickel plating programs for automotive and industrial applications including alloy composition control and corrosion resistance validation."},
    {"name": "electroless-plating-services", "description": "Provide electroless plating services including electroless nickel, copper, and cobalt processes with phosphorus content control and heat treat programs."},
    {"name": "chemical-conversion-coating", "description": "Operate chemical conversion coating services including chromate, trivalent chrome, and phosphate conversion coatings with corrosion testing programs."},
    {"name": "plating-regulatory-compliance", "description": "Navigate electroplating regulatory compliance including OSHA hex chrome standard, EPA effluent guidelines, and hazardous waste generator requirements."},
]

# Domain: Precision Machining Contract Services
skills += [
    {"name": "cnc-job-shop-scheduling", "description": "Schedule CNC job shop production including work order prioritization, machine loading, setup time reduction, and on-time delivery performance."},
    {"name": "machining-process-engineering", "description": "Develop machining process plans including tooling selection, cutting parameter optimization, fixturing design, and first article qualification."},
    {"name": "precision-turning-operations", "description": "Manage precision turning operations including CNC lathe programming, bar feed automation, tolerance control, and surface finish verification."},
    {"name": "precision-milling-operations", "description": "Operate precision milling services including 3-axis and 5-axis machining, high-speed machining, and complex contour verification."},
    {"name": "grinding-honing-services", "description": "Provide grinding and honing services including cylindrical, surface, and centerless grinding with geometric tolerance and surface texture control."},
    {"name": "edm-services-management", "description": "Manage EDM services including wire EDM and sinker EDM operations, electrode fabrication, and micro-machining capability development."},
    {"name": "machining-quality-systems", "description": "Implement machining quality systems including AS9100, IATF16949, and ISO13485 compliance, CMM programming, and SPC deployment."},
    {"name": "machining-material-expertise", "description": "Develop machining expertise for difficult-to-cut materials including titanium, Inconel, hardened steels, and advanced ceramics."},
    {"name": "contract-machining-quoting", "description": "Develop contract machining quotations including cost estimating, material procurement, tooling amortization, and lead time commitments."},
    {"name": "machining-coolant-management", "description": "Manage machining coolant systems including concentration monitoring, tramp oil removal, bacteria control, and disposal compliance."},
]

# Domain: Injection Molding Contract Services
skills += [
    {"name": "injection-molding-scheduling", "description": "Schedule injection molding production including press loading by tonnage, material changeover sequencing, and cavity balancing optimization."},
    {"name": "mold-tooling-management", "description": "Manage injection mold tooling including preventive maintenance schedules, repair workflows, hot runner servicing, and tooling life tracking."},
    {"name": "injection-molding-process-dev", "description": "Develop injection molding processes including gate design, fill analysis, cooling optimization, and Decoupled Molding process documentation."},
    {"name": "plastic-material-management", "description": "Manage plastic resin materials including supplier qualification, incoming inspection, drying protocols, and regrind incorporation programs."},
    {"name": "insert-overmolding-services", "description": "Provide insert and overmolding services including metal insert handling, two-shot process development, and adhesion testing programs."},
    {"name": "clean-room-molding-ops", "description": "Operate clean room injection molding for medical devices including environmental monitoring, gowning protocols, and particle count compliance."},
    {"name": "molding-quality-systems", "description": "Implement injection molding quality systems including PPAP submission, in-process inspection, and cavity identification traceability programs."},
    {"name": "molding-defect-analysis", "description": "Analyze injection molding defects including weld lines, sink marks, warpage, and short shots with systematic root cause and corrective action."},
    {"name": "post-molding-operations", "description": "Manage post-molding operations including degating, assembly, ultrasonic welding, pad printing, and kitting for customer delivery."},
    {"name": "molding-sustainability-programs", "description": "Implement injection molding sustainability programs including regrind optimization, material reduction, energy monitoring, and bio-based material qualification."},
]

# Domain: Die Casting Contract Services
skills += [
    {"name": "die-casting-cell-management", "description": "Manage die casting production cells including machine scheduling, shot parameter control, die temperature management, and cycle time optimization."},
    {"name": "die-casting-tooling-ops", "description": "Manage die casting tooling including die spray systems, vacuum assist maintenance, slide mechanism service, and shot sleeve replacement programs."},
    {"name": "aluminum-die-casting-ops", "description": "Operate aluminum die casting services including alloy chemistry control, porosity reduction programs, and heat treat coordination."},
    {"name": "zinc-die-casting-ops", "description": "Manage zinc die casting operations including alloy management, plunger tip maintenance, and thin-wall capability development programs."},
    {"name": "die-casting-quality-systems", "description": "Implement die casting quality systems including X-ray inspection programs, leak testing, CMM inspection, and IATF16949 compliance."},
    {"name": "die-casting-trim-finish-ops", "description": "Operate die casting trim and finishing operations including degating, shot blast, vibratory deburr, and CNC machining cell coordination."},
    {"name": "die-casting-process-engineering", "description": "Develop die casting processes including fill simulation, gate and runner design, venting system optimization, and intensification pressure control."},
    {"name": "die-casting-cost-estimating", "description": "Develop die casting cost estimates including shot weight calculation, cycle time estimation, secondary operation costing, and tooling amortization."},
    {"name": "high-pressure-vacuum-die-cast", "description": "Manage high-pressure vacuum die casting programs for structural automotive components including process certification and mechanical property verification."},
    {"name": "semi-solid-thixocasting-ops", "description": "Operate semi-solid metal casting services including billet preparation, rheology control, and microstructure qualification programs."},
]

# Domain: Metal Stamping and Forming Services
skills += [
    {"name": "stamping-press-scheduling", "description": "Schedule metal stamping press operations including tonnage matching, die changeover optimization, coil staging, and production run planning."},
    {"name": "progressive-die-operations", "description": "Operate progressive die stamping including strip layout management, die maintenance, lubricant selection, and in-die sensor monitoring."},
    {"name": "stamping-tooling-maintenance", "description": "Maintain stamping tooling including punch and die sharpening, spring replacement, pilot alignment, and shut height verification programs."},
    {"name": "metal-forming-process-dev", "description": "Develop metal forming processes including blank development, draw ratio analysis, springback compensation, and formability simulation."},
    {"name": "fine-blanking-services", "description": "Provide fine blanking services including triple-action press operations, counter pressure control, and flatness and burr-free edge quality management."},
    {"name": "roll-forming-operations", "description": "Operate roll forming production lines including profile tooling setup, straightening adjustment, and cutoff system management."},
    {"name": "stamping-secondary-ops", "description": "Manage stamping secondary operations including tapping, welding, assembly, and hardware insertion within the stamping production cell."},
    {"name": "stamping-material-procurement", "description": "Manage stamping material procurement including coil specification, service center qualification, incoming yield strength tracking, and scrap reconciliation."},
    {"name": "stamping-quality-systems", "description": "Implement stamping quality systems including PPAP approval, first article dimensional reporting, and in-process statistical monitoring programs."},
    {"name": "hydroforming-services", "description": "Provide tube and sheet hydroforming services including pressure sequence development, tool design support, and complex geometry capability qualification."},
]

# Domain: Sheet Metal Fabrication Services
skills += [
    {"name": "sheet-metal-estimating", "description": "Develop sheet metal fabrication estimates including material takeoff, laser nest efficiency, bending sequence planning, and finishing cost inclusion."},
    {"name": "laser-cutting-operations", "description": "Operate laser cutting production including nesting optimization, focus height calibration, assist gas management, and edge quality monitoring."},
    {"name": "waterjet-cutting-services", "description": "Manage waterjet cutting services including abrasive consumption, taper compensation, nozzle maintenance, and multi-material capability."},
    {"name": "press-brake-operations", "description": "Operate press brake forming including CNC back gauge programming, tooling selection, springback compensation, and angle verification."},
    {"name": "sheet-metal-welding-ops", "description": "Manage sheet metal welding operations including MIG, TIG, and spot welding, fixturing design, distortion control, and weld inspection programs."},
    {"name": "sheet-metal-finishing-services", "description": "Manage sheet metal finishing operations including powder coat, wet paint, anodize outsourcing, silk screening, and hardware installation."},
    {"name": "enclosure-fabrication-ops", "description": "Fabricate electrical enclosures and custom cabinets including UL certification compliance, panel cutout machining, and wire way assembly."},
    {"name": "sheet-metal-assembly-services", "description": "Provide sheet metal assembly services including hardware insertion, PEM fastener installation, hinge attachment, and functional testing."},
    {"name": "sheet-metal-quality-programs", "description": "Implement sheet metal quality programs including AS9100 compliance, CMM inspection, flatness verification, and cosmetic inspection criteria."},
    {"name": "sheet-metal-design-for-mfg", "description": "Provide design-for-manufacturability reviews for sheet metal parts including bend radius guidelines, hole sizing, and feature proximity recommendations."},
]

# Domain: Welding and Fabrication Services
skills += [
    {"name": "welding-procedure-qualification", "description": "Qualify welding procedures including WPS development, PQR testing, welder certification management, and code compliance documentation."},
    {"name": "structural-fabrication-ops", "description": "Manage structural steel fabrication operations including fit-up sequencing, overhead crane utilization, and dimensional verification programs."},
    {"name": "pressure-vessel-fabrication", "description": "Fabricate pressure vessels and heat exchangers including ASME code compliance, NDE coordination, and authorized inspection interface."},
    {"name": "pipe-fabrication-services", "description": "Manage pipe fabrication services including isometric drawing interpretation, spool piece assembly, hydrostatic testing, and marking programs."},
    {"name": "aluminum-welding-ops", "description": "Operate aluminum welding fabrication services including oxide removal, filler selection, distortion control, and post-weld heat treat programs."},
    {"name": "welding-nde-coordination", "description": "Coordinate non-destructive examination for welding programs including RT, UT, MT, PT scheduling, film interpretation, and defect disposition."},
    {"name": "robotic-welding-operations", "description": "Manage robotic welding cells including fixture design, program development, tip maintenance, and weld quality monitoring systems."},
    {"name": "field-welding-services", "description": "Provide field welding services including site safety planning, preheat management, joint preparation in restricted access, and in-service weld planning."},
    {"name": "weld-distortion-control", "description": "Manage weld distortion control programs including pre-bend, balanced welding sequences, back-step techniques, and post-weld straightening."},
    {"name": "welding-consumable-mgmt", "description": "Manage welding consumable programs including electrode classification, lot traceability, storage requirements, and low-hydrogen protocols."},
]

# Domain: Mechanical Insulation Contracting
skills += [
    {"name": "insulation-system-specification", "description": "Develop mechanical insulation system specifications including material selection, thickness calculation, jacketing type, and personnel protection design."},
    {"name": "insulation-installation-ops", "description": "Manage insulation installation operations including pipe insulation, equipment lagging, penetration sealing, and weather barrier application."},
    {"name": "insulation-energy-audit-services", "description": "Conduct mechanical insulation energy audits including heat loss surveys, thermal imaging, and insulation upgrade ROI reporting."},
    {"name": "cryogenic-insulation-services", "description": "Provide cryogenic insulation services including perlite vacuum systems, multi-layer insulation, and cold-box installation coordination."},
    {"name": "industrial-acoustic-insulation", "description": "Install industrial acoustic insulation and noise control systems including duct silencers, pipe lagging, and equipment enclosure fabrication."},
    {"name": "insulation-fire-protection-systems", "description": "Apply fire-rated insulation systems including intumescent wrap, calcium silicate block, and endothermic mat for passive fire protection."},
    {"name": "insulation-material-management", "description": "Manage insulation material procurement including fiberglass, mineral wool, calcium silicate, foam glass, and flexible elastomeric product lines."},
    {"name": "insulation-maintenance-programs", "description": "Develop insulation maintenance programs including inspection protocols, damaged insulation repair prioritization, and lifecycle replacement planning."},
    {"name": "hvac-duct-insulation-ops", "description": "Manage HVAC duct insulation operations including thermal and vapor retarder specifications, clean room requirements, and condensation prevention."},
    {"name": "insulation-contract-management", "description": "Manage insulation contracting programs including scope development, labor estimate preparation, subcontractor qualification, and project closeout."},
]

# Domain: Scaffolding and Access Services
skills += [
    {"name": "scaffold-design-engineering", "description": "Design scaffold systems including tube-and-clamp, frame, systems, and suspended scaffold engineering for load capacity and tie-in requirements."},
    {"name": "scaffold-erection-management", "description": "Manage scaffold erection operations including crew scheduling, material staging, erection sequence, and scaffold tag inspection programs."},
    {"name": "scaffold-safety-compliance", "description": "Implement scaffold safety programs including OSHA 1926 Subpart Q compliance, fall protection integration, and scaffold user training."},
    {"name": "industrial-scaffold-planning", "description": "Plan scaffolding for turnarounds and shutdowns including scaffold register development, priority sequencing, and scaffold density management."},
    {"name": "suspended-access-systems", "description": "Manage suspended access and mast climbing systems including building facade maintenance, rigging design, and equipment certification."},
    {"name": "scaffold-material-management", "description": "Manage scaffold material fleets including inventory tracking, inspection programs, repair tagging, and lost or damaged material accounting."},
    {"name": "rope-access-services", "description": "Provide industrial rope access services including IRATA certified technician deployment, fall rescue plans, and inspection documentation."},
    {"name": "scaffold-rental-operations", "description": "Operate scaffold rental programs including rental agreement management, delivery logistics, on-hire inspection, and off-hire reconciliation."},
    {"name": "scaffold-estimating-ops", "description": "Develop scaffold project estimates including material calculation, labor hours, special equipment allowance, and contract pricing strategies."},
    {"name": "scaffold-workforce-management", "description": "Manage scaffold workforce including apprentice and journeyman scaffold builder training, certification tracking, and competency assessment programs."},
]

# Domain: Crane and Heavy Lift Services
skills += [
    {"name": "crane-lift-planning", "description": "Develop engineered lift plans including load path analysis, outrigger pad design, sling angle calculations, and rigging configuration approval."},
    {"name": "crane-fleet-management", "description": "Manage mobile crane fleets including annual inspection programs, load chart compliance, transport permitting, and utilization reporting."},
    {"name": "crane-operator-management", "description": "Manage crane operator programs including NCCCO certification tracking, pre-shift inspection compliance, and operating procedure training."},
    {"name": "heavy-transport-logistics", "description": "Coordinate heavy transport logistics including route surveys, oversize permit acquisition, escort vehicle coordination, and bridge load analysis."},
    {"name": "critical-lift-management", "description": "Manage critical lift programs including tandem lift coordination, near-capacity lift procedures, and third-party engineering review requirements."},
    {"name": "tower-crane-operations", "description": "Manage tower crane operations including foundation design coordination, climbing procedures, wind shutdown protocols, and operator communication systems."},
    {"name": "gantry-and-skidding-ops", "description": "Operate gantry lifting and skidding systems for heavy module installation including hydraulic control, load monitoring, and precision placement."},
    {"name": "rigging-hardware-management", "description": "Manage lifting and rigging hardware programs including sling inventory, load testing, inspection records, and equipment retirement criteria."},
    {"name": "crane-incident-investigation", "description": "Investigate crane incidents including sequence-of-events reconstruction, equipment examination, and corrective action development for crane safety programs."},
    {"name": "crane-site-coordination", "description": "Coordinate crane site operations including laydown planning, overhead hazard identification, exclusion zone management, and customer interface."},
]

# Domain: Equipment Rental Operations
skills += [
    {"name": "rental-fleet-management", "description": "Manage equipment rental fleets including acquisition planning, asset tracking, lifecycle management, and disposal program coordination."},
    {"name": "rental-counter-operations", "description": "Operate rental counter services including contract processing, credit verification, equipment demonstration, and reservation management."},
    {"name": "rental-equipment-maintenance", "description": "Manage rental equipment maintenance programs including return inspection, preventive service, damage assessment, and readiness for re-rental."},
    {"name": "rental-delivery-logistics", "description": "Manage rental equipment delivery and pickup logistics including driver dispatch, route optimization, and customer site coordination."},
    {"name": "rental-pricing-revenue-mgmt", "description": "Optimize rental pricing and revenue management including time utilization, financial utilization targets, and dynamic rate management."},
    {"name": "specialty-equipment-rental-ops", "description": "Operate specialty equipment rental programs including boom lifts, scissor lifts, telehandlers, and compact equipment for industrial and construction markets."},
    {"name": "rental-damage-billing-programs", "description": "Manage rental damage billing programs including damage waiver coverage, equipment inspection documentation, and customer dispute resolution."},
    {"name": "rental-technology-platforms", "description": "Operate rental management technology platforms including online reservations, telematics integration, and digital contract management."},
    {"name": "rental-contractor-support-ops", "description": "Provide rental contractor support operations including jobsite service calls, emergency after-hours response, and on-site fuel delivery programs."},
    {"name": "rental-national-account-mgmt", "description": "Manage national rental account programs including pricing agreements, cross-branch coordination, consolidated invoicing, and account review meetings."},
]

# Domain: Portable Power Generation Rental
skills += [
    {"name": "generator-rental-sizing", "description": "Size temporary power generation systems including load analysis, load bank testing, paralleling configuration, and transfer switch coordination."},
    {"name": "generator-rental-ops", "description": "Operate generator rental programs including fleet sizing by kVA class, mobile deployment logistics, and utility paralleling compliance."},
    {"name": "generator-fuel-management", "description": "Manage generator rental fuel programs including on-site fuel storage, automated refueling scheduling, and generator runtime tracking."},
    {"name": "temp-power-distribution-ops", "description": "Deploy temporary power distribution systems including cable management, panel board rental, and PDU configuration for events and construction."},
    {"name": "generator-preventive-maintenance", "description": "Execute generator preventive maintenance programs including coolant service, load bank testing, oil analysis, and exciter voltage adjustment."},
    {"name": "critical-power-rental-ops", "description": "Manage critical power rental programs for hospitals, data centers, and government facilities including N+1 redundancy, transfer time requirements, and monitoring."},
    {"name": "generator-rental-revenue-ops", "description": "Optimize generator rental revenue including rate management, utilization analysis, fleet rebalancing, and peak demand surge pricing."},
    {"name": "generator-emissions-compliance", "description": "Navigate generator emissions compliance including Tier 4 Final deployment, CARB ATCM requirements, and operating permit management."},
    {"name": "mobile-substation-rental", "description": "Provide mobile substation rental services including transformer specification, switchgear deployment, and utility interconnection coordination."},
    {"name": "event-power-rental-ops", "description": "Manage event power rental programs for concerts, festivals, and outdoor events including cable routing, silent generator selection, and power quality monitoring."},
]

# Domain: Industrial Uniform and Workwear Supply
skills += [
    {"name": "uniform-program-management", "description": "Manage corporate uniform programs including garment selection, size distribution, embellishment coordination, and employee issuance workflows."},
    {"name": "uniform-rental-route-ops", "description": "Operate uniform rental route services including garment pickup, laundering, repair, and weekly delivery to manufacturing and service facilities."},
    {"name": "arc-flash-fr-clothing-programs", "description": "Manage arc flash and flame resistant clothing programs including NFPA 70E compliance, CAL/ARC rating selection, and employee training coordination."},
    {"name": "hi-vis-safety-apparel-programs", "description": "Manage high-visibility safety apparel programs including ANSI 107 class selection, retroreflective tape inspection, and replacement programs."},
    {"name": "uniform-embellishment-ops", "description": "Operate uniform embellishment services including embroidery, screen printing, heat transfer, and brand standard compliance programs."},
    {"name": "workwear-inventory-management", "description": "Manage workwear inventory programs including online company store platforms, vending machine issuance, and reorder automation."},
    {"name": "uniform-sourcing-procurement", "description": "Manage workwear sourcing and procurement including fabric specification, overseas supplier qualification, and ethical sourcing compliance."},
    {"name": "protective-clothing-selection", "description": "Advise on protective clothing selection including chemical splash, welding, cut-resistant, and contamination control apparel for specific hazard profiles."},
    {"name": "uniform-program-analytics", "description": "Analyze uniform program performance including per-employee cost tracking, garment loss rates, utilization reporting, and renewal cycle planning."},
    {"name": "cleanroom-garment-programs", "description": "Manage cleanroom garment programs including laundry service qualification, garment integrity testing, particle shed monitoring, and particle count compliance."},
]

# Domain: Personal Protective Equipment Manufacturing
skills += [
    {"name": "ppe-product-certification-mgmt", "description": "Manage PPE product certification programs including ANSI, EN, and ISO standard testing, third-party certification body management, and label compliance."},
    {"name": "ppe-product-development", "description": "Develop PPE products including hazard analysis, material selection, prototype testing, and usability evaluation with end users."},
    {"name": "ppe-supply-chain-operations", "description": "Manage PPE supply chains including contract manufacturing oversight, incoming quality inspection, and customs compliance for imported goods."},
    {"name": "ppe-distribution-operations", "description": "Manage PPE distribution operations including safety distributor channel management, online direct-to-consumer programs, and emergency stockpile programs."},
    {"name": "ppe-training-programs", "description": "Develop PPE training programs including fit testing, donning and doffing procedures, care and maintenance, and service life management."},
    {"name": "respiratory-protection-programs", "description": "Manage respiratory protection programs including OSHA written program compliance, fit test records, respirator selection for hazard profiles, and medical evaluation coordination."},
    {"name": "hearing-protection-programs", "description": "Manage industrial hearing protection programs including noise level survey integration, NRR selection guidance, and audiometric testing coordination."},
    {"name": "eye-face-protection-mgmt", "description": "Manage eye and face protection programs including ANSI Z87.1 compliance, prescription safety eyewear programs, and anti-fog coating maintenance."},
    {"name": "hand-protection-programs", "description": "Manage industrial hand protection programs including cut level selection, chemical compatibility testing, and task-based glove recommendation systems."},
    {"name": "fall-protection-product-mgmt", "description": "Manage fall protection product programs including harness inspection protocols, anchorage connector selection, and rescue plan integration."},
]

# Domain: Fire Protection System Contracting
skills += [
    {"name": "fire-sprinkler-design", "description": "Design automatic fire sprinkler systems including hydraulic calculations, pipe schedule design, NFPA 13 compliance, and authority having jurisdiction coordination."},
    {"name": "fire-sprinkler-installation", "description": "Manage fire sprinkler installation projects including pipe fabrication, hanger installation, head placement, and hydrostatic test documentation."},
    {"name": "fire-sprinkler-inspection-testing", "description": "Conduct fire sprinkler inspection, testing, and maintenance programs including NFPA 25 compliance, deficiency tracking, and impairment management."},
    {"name": "special-hazard-suppression-ops", "description": "Design and install special hazard suppression systems including clean agent, CO2, foam-water, and dry chemical systems for high-value and hazardous occupancies."},
    {"name": "fire-alarm-system-installation", "description": "Install fire alarm systems including detector placement, pull station layout, control panel programming, and acceptance testing documentation."},
    {"name": "fire-alarm-monitoring-ops", "description": "Manage fire alarm monitoring center operations including signal receipt, dispatch procedures, false alarm reduction programs, and UL listing compliance."},
    {"name": "emergency-lighting-exit-signs", "description": "Install and maintain emergency lighting and exit sign systems including battery backup testing, illumination level verification, and NFPA 101 compliance."},
    {"name": "kitchen-suppression-services", "description": "Install and service commercial kitchen fire suppression systems including ANSUL system maintenance, fuel shut-off coordination, and health department compliance."},
    {"name": "fire-pump-installation-service", "description": "Install and service fire pumps including driver and controller selection, performance testing, weekly churn test programs, and NFPA 20 compliance."},
    {"name": "fire-protection-project-mgmt", "description": "Manage fire protection contracting projects including drawing submittal, inspection coordination, permit close-out, and as-built documentation."},
]

# Domain: Elevator and Escalator Maintenance Services
skills += [
    {"name": "elevator-preventive-maintenance", "description": "Execute elevator preventive maintenance programs including lubrication schedules, safety device testing, code compliance inspections, and performance reporting."},
    {"name": "elevator-modernization-ops", "description": "Manage elevator modernization projects including controller upgrades, door operator replacement, cab renovation, and enhanced accessibility compliance."},
    {"name": "elevator-emergency-service-ops", "description": "Operate elevator emergency service programs including 24/7 callback response, entrapment rescue protocols, and emergency dispatch coordination."},
    {"name": "escalator-moving-walk-service", "description": "Maintain escalator and moving walk systems including step chain lubrication, handrail drive service, comb plate inspection, and safety circuit testing."},
    {"name": "elevator-permit-compliance", "description": "Manage elevator permit and inspection compliance including AHJ inspection scheduling, violation response, and code update tracking."},
    {"name": "elevator-monitoring-connected", "description": "Deploy elevator remote monitoring systems including fault code analysis, predictive maintenance alerts, and elevator performance benchmarking."},
    {"name": "elevator-service-contract-mgmt", "description": "Manage elevator service contracts including full maintenance vs. oil-and-grease agreements, callback response SLAs, and annual rate adjustment programs."},
    {"name": "elevator-installation-ops", "description": "Manage new elevator installation projects including machine room layout, hoistway preparation, rail alignment, and pre-inspection testing."},
    {"name": "elevator-spare-parts-mgmt", "description": "Manage elevator spare parts programs including critical spare stocking, obsolete parts sourcing, and parts exchange program management."},
    {"name": "platform-lift-services", "description": "Provide platform lift and residential elevator services including ADA compliance, limited-use limited-application elevator programs, and lift maintenance."},
]

# Domain: Commercial and Industrial Cleaning Services
skills += [
    {"name": "janitorial-services-management", "description": "Manage commercial janitorial services including task frequency scheduling, chemical program management, quality inspection, and workforce supervision."},
    {"name": "industrial-cleaning-ops", "description": "Operate industrial cleaning services including high-pressure water jetting, vacuum truck services, and chemical cleaning for process equipment."},
    {"name": "cleanroom-cleaning-services", "description": "Provide cleanroom cleaning services including particle count verification, disinfection protocol development, and contamination control compliance."},
    {"name": "floor-care-services", "description": "Manage commercial floor care services including strip-and-wax, carpet extraction, hard floor grinding, and protective coating application programs."},
    {"name": "window-cleaning-services", "description": "Operate commercial window cleaning services including building facade access, water-fed pole systems, and high-rise rope access cleaning."},
    {"name": "pressure-washing-services", "description": "Manage pressure washing and exterior cleaning services including concrete cleaning, building wash-down, and wastewater containment compliance."},
    {"name": "biohazard-decontamination", "description": "Provide biohazard decontamination services including crime scene cleanup, hoarding remediation, and infectious disease decontamination with proper PPE and disposal."},
    {"name": "post-construction-cleaning", "description": "Manage post-construction cleaning services including rough clean, final clean, and punch list cleaning coordination with general contractors."},
    {"name": "cleaning-chemical-programs", "description": "Manage cleaning chemical programs including product selection, dilution control system deployment, green cleaning certification, and SDS compliance."},
    {"name": "cleaning-workforce-management", "description": "Manage cleaning workforce programs including background screening, training certification, labor scheduling, and performance monitoring programs."},
]

# Domain: Hazardous Waste Management Services
skills += [
    {"name": "hazardous-waste-characterization", "description": "Characterize hazardous wastes including RCRA classification, waste profile development, analytical testing coordination, and manifest preparation."},
    {"name": "hazardous-waste-collection-ops", "description": "Manage hazardous waste collection operations including generator site visits, drum consolidation, DOT packaging, and transporter coordination."},
    {"name": "hazmat-transport-compliance", "description": "Navigate hazardous materials transportation compliance including DOT 49 CFR requirements, placard selection, and driver training programs."},
    {"name": "tsdf-operations-management", "description": "Manage treatment, storage, and disposal facility operations including permit compliance, waste receipt procedures, and annual reporting."},
    {"name": "emergency-spill-response-ops", "description": "Operate hazardous spill response services including 24-hour dispatch, containment deployment, remediation, and regulatory notification coordination."},
    {"name": "hazwaste-cost-optimization", "description": "Optimize hazardous waste disposal costs including waste minimization programs, blending for fuel substitution, and alternative technology qualification."},
    {"name": "universal-waste-programs", "description": "Manage universal waste collection programs for lamps, batteries, and thermostats including large quantity handler compliance and recycler qualification."},
    {"name": "contaminated-soil-management", "description": "Manage contaminated soil excavation and disposal programs including sampling plan development, waste characterization, and disposal facility selection."},
    {"name": "hazwaste-generator-compliance", "description": "Maintain hazardous waste generator compliance programs including accumulation time limits, container labeling, and biennial report preparation."},
    {"name": "hazmat-training-programs", "description": "Deliver hazmat training programs including RCRA generator training, DOT hazmat employee training, and first responder awareness level training."},
]

# Domain: Document Shredding and Destruction Services
skills += [
    {"name": "onsite-shredding-services", "description": "Provide on-site document shredding services including mobile shredder scheduling, chain-of-custody documentation, and certificate of destruction issuance."},
    {"name": "offsite-shredding-operations", "description": "Manage off-site shredding plant operations including console pickup routing, inbound volume management, shred process throughput, and bale output."},
    {"name": "hard-drive-destruction-services", "description": "Provide hard drive and electronic media destruction services including degaussing, physical shredding, and NIST-compliant data sanitization documentation."},
    {"name": "shredding-compliance-programs", "description": "Manage shredding compliance programs including HIPAA, FACTA, and state privacy law requirements, audit trail maintenance, and client compliance reporting."},
    {"name": "shredding-recycling-ops", "description": "Manage shredded paper recycling operations including bale marketing, fiber grade separation, and sustainability reporting for client programs."},
    {"name": "shredding-route-optimization", "description": "Optimize shredding service routes including console density planning, pickup frequency adjustment, and driver productivity metrics."},
    {"name": "shredding-plant-operations", "description": "Operate document shredding plant facilities including industrial shredder maintenance, fire suppression systems, and chain-of-custody floor controls."},
    {"name": "product-destruction-services", "description": "Manage secure product destruction services including pharmaceuticals, branded goods, and confidential materials with witness and certificate programs."},
    {"name": "shredding-sales-operations", "description": "Develop shredding service sales programs including recurring service agreements, one-time purge events, and enterprise account management."},
    {"name": "shredding-vendor-management", "description": "Manage shredding subcontractor vendor programs including downstream vendor audits, AAA NAID certification compliance, and chain-of-custody verification."},
]

# Domain: Physical Security Guarding Services
skills += [
    {"name": "security-post-operations", "description": "Manage security guard post operations including access control procedures, patrol scheduling, incident report documentation, and post order compliance."},
    {"name": "security-workforce-management", "description": "Manage contract security workforces including licensing verification, background screening, training certification, and deployment scheduling."},
    {"name": "security-account-management", "description": "Manage physical security account programs including site assessment, post order development, service quality audits, and client relationship management."},
    {"name": "executive-protection-services", "description": "Provide executive protection services including threat assessment, advance work, protective detail coordination, and secure transportation management."},
    {"name": "event-security-services", "description": "Manage event security programs including crowd management, access control, VIP protection, and emergency evacuation coordination."},
    {"name": "retail-security-programs", "description": "Operate retail security programs including loss prevention officer deployment, ORC investigation support, and theft indicator monitoring."},
    {"name": "industrial-security-ops", "description": "Manage industrial facility security operations including vehicle inspection programs, contractor badging, perimeter patrol, and emergency response."},
    {"name": "security-technology-integration", "description": "Integrate security technology with guarding services including CCTV monitoring, access control alarm response, and visitor management system operation."},
    {"name": "security-incident-management", "description": "Manage security incident response programs including on-site response protocols, stakeholder notification, investigation coordination, and after-action reporting."},
    {"name": "security-training-development", "description": "Develop security officer training programs including use of force, active threat response, customer service, and jurisdiction-specific licensing requirements."},
]

# Domain: HVAC Service and Maintenance Contracting
skills += [
    {"name": "hvac-preventive-maintenance", "description": "Execute HVAC preventive maintenance programs including filter replacement, coil cleaning, belt tension, and refrigerant charge verification."},
    {"name": "hvac-service-dispatch-ops", "description": "Manage HVAC service dispatch operations including technician routing, call priority triage, parts van stocking, and customer communication."},
    {"name": "chiller-plant-maintenance", "description": "Maintain chiller plant systems including compressor oil analysis, condenser tube brushing, refrigerant management, and efficiency reporting."},
    {"name": "hvac-controls-programming", "description": "Program HVAC direct digital controls including BAS sequence of operations, alarm limit setting, energy optimization logic, and remote access configuration."},
    {"name": "commercial-refrigeration-service", "description": "Service commercial refrigeration systems including walk-in cooler maintenance, reach-in case repair, refrigerant leak detection, and EPA Section 608 compliance."},
    {"name": "hvac-service-agreement-mgmt", "description": "Manage HVAC service agreement programs including contract coverage tiers, renewal tracking, equipment coverage inventories, and invoice reconciliation."},
    {"name": "indoor-air-quality-services", "description": "Provide indoor air quality services including air sampling, duct cleaning, coil disinfection, and ventilation rate verification per ASHRAE 62.1."},
    {"name": "hvac-installation-commissioning", "description": "Manage HVAC installation and commissioning projects including equipment startup, controls sequence verification, and TAB coordination."},
    {"name": "hvac-refrigerant-management", "description": "Manage refrigerant programs including Section 608 technician certification, refrigerant recovery and reclaim, and HFC phase-down planning."},
    {"name": "hvac-energy-services-ops", "description": "Provide HVAC energy services including equipment efficiency upgrades, retro-commissioning, and guaranteed energy savings program development."},
]

# Domain: Data Center Facilities Management
skills += [
    {"name": "data-center-power-mgmt", "description": "Manage data center power infrastructure including UPS systems, PDU load balancing, generator test programs, and critical power capacity planning."},
    {"name": "data-center-cooling-ops", "description": "Operate data center cooling systems including CRAC/CRAH management, economizer mode optimization, containment strategies, and PUE monitoring."},
    {"name": "data-center-change-management", "description": "Manage data center change control programs including MACD workflows, floor plan updates, power circuit documentation, and impact assessment."},
    {"name": "dcim-platform-operations", "description": "Operate data center infrastructure management platforms including asset tracking, capacity reporting, power monitoring, and thermal modeling."},
    {"name": "data-center-security-ops", "description": "Manage data center physical security including biometric access control, video surveillance, visitor escort procedures, and security audit programs."},
    {"name": "data-center-compliance-mgmt", "description": "Manage data center compliance programs including SOC 2, ISO 27001, and Uptime Institute Tier certification maintenance and evidence collection."},
    {"name": "data-center-maintenance-programs", "description": "Develop data center maintenance programs including critical system preventive maintenance, infrared thermography, and annual generator load bank testing."},
    {"name": "data-center-capacity-planning", "description": "Plan data center capacity including power density trends, space utilization, cooling headroom, and technology refresh cycle management."},
    {"name": "hyperscale-data-center-ops", "description": "Operate hyperscale data center facilities including remote hands coordination, massive infrastructure monitoring, and high-density cooling management."},
    {"name": "data-center-sustainability-ops", "description": "Manage data center sustainability programs including renewable energy procurement, water usage effectiveness, waste heat recovery, and carbon neutrality reporting."},
]

# Domain: Streaming Media Platform Operations
skills += [
    {"name": "video-ingest-transcoding-ops", "description": "Manage video ingest and transcoding operations including encoding ladder management, format normalization, and delivery pipeline monitoring."},
    {"name": "content-delivery-network-ops", "description": "Operate CDN infrastructure for streaming media including edge node management, cache hit ratio optimization, and origin shield configuration."},
    {"name": "streaming-quality-monitoring", "description": "Monitor streaming video quality including rebuffering rate, startup time, bitrate adaptation, and viewer experience score dashboards."},
    {"name": "drm-content-protection-ops", "description": "Manage DRM and content protection systems including Widevine, FairPlay, and PlayReady license server operations and key management."},
    {"name": "live-streaming-ops", "description": "Operate live streaming infrastructure including encoder configuration, low-latency delivery, redundant ingest paths, and real-time monitoring."},
    {"name": "streaming-platform-scaling", "description": "Scale streaming media platforms for peak demand including auto-scaling policies, load test design, and capacity headroom management."},
    {"name": "vod-catalog-management", "description": "Manage VOD content catalogs including metadata ingestion, asset validation, availability windowing, and geographic rights management."},
    {"name": "streaming-ad-insertion-ops", "description": "Operate streaming ad insertion systems including SSAI configuration, ad decision server integration, and ad pod performance monitoring."},
    {"name": "streaming-analytics-ops", "description": "Manage streaming platform analytics including viewer engagement metrics, content performance dashboards, and recommendation engine data pipelines."},
    {"name": "streaming-platform-security", "description": "Secure streaming media platforms including account takeover detection, credential stuffing defense, and piracy monitoring programs."},
]

# Domain: Automotive Aftermarket Parts Distribution
skills += [
    {"name": "auto-parts-warehouse-ops", "description": "Operate automotive aftermarket parts warehouses including bin location management, will-call counter service, and next-day delivery fulfillment."},
    {"name": "auto-parts-catalog-mgmt", "description": "Manage automotive parts catalog data including ACES and PIES data standards, fitment validation, and catalog update workflows."},
    {"name": "auto-parts-pricing-strategy", "description": "Develop automotive aftermarket pricing strategies including competitive benchmarking, margin tier management, and promotional pricing programs."},
    {"name": "auto-parts-supplier-mgmt", "description": "Manage auto parts supplier relationships including vendor-managed inventory programs, drop-ship integration, and fill rate performance tracking."},
    {"name": "auto-parts-return-core-programs", "description": "Manage auto parts return and core deposit programs including core receipt inspection, credit processing, and core remanufacturing coordination."},
    {"name": "auto-parts-ecommerce-ops", "description": "Operate automotive parts ecommerce platforms including fitment-based search, order management integration, and marketplace channel management."},
    {"name": "auto-parts-commercial-sales", "description": "Manage commercial auto parts sales programs including fleet account management, repair shop loyalty programs, and outside sales force coordination."},
    {"name": "auto-parts-inventory-optimization", "description": "Optimize automotive parts inventory using demand classification, safety stock modeling, and supersession chain management for part number lifecycle."},
    {"name": "auto-parts-branch-network-mgmt", "description": "Manage auto parts distribution branch networks including location performance, inter-branch transfer programs, and territory assignment."},
    {"name": "auto-parts-private-label-ops", "description": "Operate private label automotive parts programs including supplier qualification, packaging development, and positioning strategy against national brands."},
]

# Domain: Agricultural Seed Operations
skills += [
    {"name": "seed-production-management", "description": "Manage seed production programs including field selection, isolation requirements, producer contracts, and yield estimation for foundation and certified seed."},
    {"name": "seed-conditioning-operations", "description": "Operate seed conditioning plants including cleaning, sizing, treating, and packaging operations with variety identity preservation protocols."},
    {"name": "seed-quality-assurance", "description": "Execute seed quality assurance programs including germination testing, purity analysis, vigor testing, and AOSCA certified seed program compliance."},
    {"name": "seed-treating-operations", "description": "Manage seed treating operations including fungicide and insecticide application, biological seed treatment programs, and treatment equipment calibration."},
    {"name": "seed-inventory-management", "description": "Manage seed inventories including lot identity preservation, storage condition monitoring, warehouse bin management, and carryover planning."},
    {"name": "seed-dealer-network-mgmt", "description": "Manage seed dealer distribution networks including territory assignments, product allocation, return policy administration, and dealer performance tracking."},
    {"name": "seed-licensing-royalty-mgmt", "description": "Manage seed variety licensing programs including technology fee collection, field use restrictions, and bag-tag compliance enforcement."},
    {"name": "seed-regulatory-compliance", "description": "Navigate seed regulatory compliance including state seed laws, phytosanitary certification, variety registration, and GMO stewardship requirements."},
    {"name": "seed-research-trials-mgmt", "description": "Manage seed research and development trial programs including plot location selection, data collection protocols, and performance data analysis."},
    {"name": "precision-planting-programs", "description": "Support precision planting programs including variable rate seeding prescriptions, planter calibration services, and agronomic data integration."},
]

# Domain: Grain Elevator Operations
skills += [
    {"name": "grain-receiving-operations", "description": "Manage grain receiving operations including truck scale management, moisture and test weight sampling, grade determination, and load ticket processing."},
    {"name": "grain-storage-management", "description": "Manage grain storage operations including bin aeration management, moisture monitoring, temperature cabling, and fumigation programs."},
    {"name": "grain-merchandising-ops", "description": "Execute grain merchandising operations including cash and futures price management, basis tracking, hedge account management, and customer price reporting."},
    {"name": "grain-shipment-operations", "description": "Manage grain shipment operations including rail car ordering, barge loading coordination, truck load-out scheduling, and shipment documentation."},
    {"name": "grain-elevator-safety-mgmt", "description": "Manage grain elevator safety programs including OSHA grain handling standard compliance, confined space entry, and combustible dust management."},
    {"name": "grain-elevator-maintenance", "description": "Maintain grain elevator equipment including leg and conveyor belt inspection, bucket replacement, spouting system maintenance, and scale certification."},
    {"name": "grain-contracts-administration", "description": "Administer grain contracts including deferred pricing agreements, basis contracts, hedge-to-arrive contracts, and contract performance tracking."},
    {"name": "grain-quality-management", "description": "Manage grain quality programs including identity preservation, non-GMO protocols, mycotoxin testing, and specialty grain certification programs."},
    {"name": "feed-grain-blending-ops", "description": "Manage feed grain blending and custom mix operations including formula management, blending equipment calibration, and ingredient traceability."},
    {"name": "grain-elevator-compliance", "description": "Navigate grain elevator regulatory compliance including state licensing, USDA inspection programs, commodity exchange rules, and environmental permits."},
]

# Domain: Aquaculture Operations
skills += [
    {"name": "fish-farm-production-mgmt", "description": "Manage fish farm production operations including stocking density management, feeding programs, growth monitoring, and harvest scheduling."},
    {"name": "aquaculture-water-quality-mgmt", "description": "Manage aquaculture water quality programs including dissolved oxygen monitoring, pH control, ammonia management, and recirculating system biofiltration."},
    {"name": "aquaculture-feed-management", "description": "Manage aquaculture feed programs including feed conversion ratio tracking, automated feeder calibration, and feed supplier qualification."},
    {"name": "aquaculture-health-management", "description": "Manage aquatic animal health programs including disease surveillance, vaccination protocols, biosecurity procedures, and veterinary relationship management."},
    {"name": "shellfish-aquaculture-ops", "description": "Operate shellfish aquaculture facilities including oyster, clam, and mussel production, gear maintenance, harvest compliance, and lease management."},
    {"name": "aquaculture-hatchery-ops", "description": "Manage fish hatchery operations including broodstock management, spawning protocols, larval rearing, and fry/fingerling distribution programs."},
    {"name": "aquaculture-regulatory-compliance", "description": "Navigate aquaculture regulatory compliance including state permits, discharge monitoring, FDA aquaculture drug use compliance, and food safety programs."},
    {"name": "recirculating-aquaculture-systems", "description": "Operate recirculating aquaculture systems including biofilter management, water treatment, solids removal, and energy efficiency optimization."},
    {"name": "aquaculture-harvest-processing", "description": "Manage aquaculture harvest and primary processing operations including slaughter protocols, ice packing, cold chain management, and buyer specification compliance."},
    {"name": "aquaculture-certification-programs", "description": "Manage aquaculture sustainability certifications including ASC, BAP, and Organic aquaculture standards, audit preparation, and chain of custody."},
]

# Domain: Dairy Processing Operations
skills += [
    {"name": "raw-milk-receiving-testing", "description": "Manage raw milk receiving and testing operations including somatic cell count, bacteria testing, antibiotic screening, and tanker weight reconciliation."},
    {"name": "dairy-pasteurization-ops", "description": "Operate dairy pasteurization systems including HTST and UHT process management, temperature chart validation, and regulatory compliance documentation."},
    {"name": "dairy-separation-standardization", "description": "Manage dairy separation and standardization operations including fat content targeting, cream balance management, and protein fortification programs."},
    {"name": "cheese-manufacturing-ops", "description": "Manage cheese manufacturing operations including culture management, coagulant dosing, curd handling, pressing, salting, and aging cave management."},
    {"name": "dairy-packaging-operations", "description": "Operate dairy packaging lines including fill weight control, seal integrity testing, date coding, and line changeover management."},
    {"name": "dairy-quality-assurance", "description": "Execute dairy quality assurance programs including environmental monitoring, finished product testing, and FSMA preventive control documentation."},
    {"name": "dairy-cold-chain-management", "description": "Manage dairy cold chain logistics including refrigerated truck scheduling, temperature monitoring, shelf-life allocation, and customer delivery compliance."},
    {"name": "dairy-byproduct-management", "description": "Manage dairy byproduct programs including whey processing, permeate utilization, cream marketing, and lactose powder production coordination."},
    {"name": "dairy-regulatory-compliance", "description": "Navigate dairy regulatory compliance including Grade A pasteurized milk ordinance, FDA registration, kosher and organic certification programs."},
    {"name": "dairy-cooperative-management", "description": "Manage dairy cooperative operations including member milk pricing, equity distribution, production planning, and capital investment programs."},
]

# Domain: Pharmaceutical Distribution
skills += [
    {"name": "pharma-wholesale-distribution", "description": "Manage pharmaceutical wholesale distribution operations including DSCSA compliance, serialization tracking, and licensed wholesale distributor programs."},
    {"name": "pharma-cold-chain-distribution", "description": "Manage pharmaceutical cold chain distribution including temperature-controlled packaging, refrigerated transport qualification, and excursion response protocols."},
    {"name": "pharma-controlled-substance-dist", "description": "Operate controlled substance distribution programs including DEA Schedule II-V compliance, suspicious order monitoring, and diversion prevention programs."},
    {"name": "specialty-pharma-distribution", "description": "Manage specialty pharmaceutical distribution including hub services, patient assistance programs, limited distribution drug channel management, and REMS compliance."},
    {"name": "pharma-reverse-distribution", "description": "Manage pharmaceutical reverse distribution programs including expired drug return services, DEA reverse distributor compliance, and credit reconciliation."},
    {"name": "pharma-distribution-compliance", "description": "Navigate pharmaceutical distribution compliance including state wholesale distributor licenses, FDA establishment registration, and GDP audit readiness."},
    {"name": "hospital-pharmacy-distribution", "description": "Manage hospital pharmacy distribution services including unit-dose packaging, omnicell replenishment, and formulary management support."},
    {"name": "pharma-340b-program-ops", "description": "Manage 340B drug pricing program operations including covered entity eligibility, split billing, accumulator programs, and audit documentation."},
    {"name": "pharma-distribution-analytics", "description": "Analyze pharmaceutical distribution performance including order fill rates, returns processing, formulary compliance, and gross-to-net revenue reporting."},
    {"name": "pharma-third-party-logistics", "description": "Manage 3PL operations for pharmaceutical manufacturers including 3PL agreement compliance, inventory ownership, quality agreement maintenance, and GDP audits."},
]

# Domain: Defense Electronics Manufacturing
skills += [
    {"name": "military-electronics-production", "description": "Manage military electronics production operations including IPC-A-610 Class 3 standards, conformal coating, and environmental stress screening programs."},
    {"name": "defense-program-management", "description": "Manage defense electronics program delivery including CDRL compliance, DID requirements, earned value management, and DCMA interface."},
    {"name": "mil-spec-material-qualification", "description": "Qualify materials and components for military electronics including QPL management, CAGE code compliance, and counterfeit parts avoidance programs."},
    {"name": "defense-configuration-mgmt", "description": "Manage defense electronics configuration management including baseline control, ECP processing, ICN tracking, and as-built documentation."},
    {"name": "defense-electronics-testing", "description": "Execute defense electronics testing programs including MIL-STD-810 environmental testing, EMI/EMC compliance, and qualification test planning."},
    {"name": "cyber-secure-electronics-mfg", "description": "Manufacture cybersecurity-assured electronics including trusted foundry programs, hardware root-of-trust implementation, and supply chain risk management."},
    {"name": "depot-repair-services", "description": "Manage depot-level electronics repair services including failure analysis, parts provisioning, repair procedures, and return-to-supply documentation."},
    {"name": "defense-export-compliance", "description": "Navigate defense export compliance including ITAR and EAR regulations, export license management, and DSP-5 application coordination."},
    {"name": "defense-quality-systems", "description": "Implement defense quality management systems including AS9100 compliance, first article inspection reports, and government source inspection coordination."},
    {"name": "electronic-warfare-sys-mfg", "description": "Manage electronic warfare system manufacturing including RF component assembly, system integration, and TEMPEST shielding effectiveness testing."},
]

# Domain: Smart Home Device Manufacturing
skills += [
    {"name": "smart-home-product-development", "description": "Develop smart home device products including connectivity protocol selection, voice assistant integration, and mobile app feature specification."},
    {"name": "iot-connectivity-standards", "description": "Manage IoT connectivity standards for smart home devices including Matter, Zigbee, Z-Wave, and Wi-Fi certification programs and interoperability testing."},
    {"name": "smart-home-cloud-platform-ops", "description": "Operate smart home cloud platforms including device provisioning, firmware OTA management, API gateway scaling, and data privacy compliance."},
    {"name": "smart-home-certification-mgmt", "description": "Manage smart home product certifications including FCC, CE, UL, and voice assistant certification programs for Amazon Alexa and Google Home."},
    {"name": "smart-home-manufacturing-ops", "description": "Manage smart home device manufacturing including PCB assembly, firmware flash programming, functional test development, and packaging operations."},
    {"name": "smart-home-supply-chain", "description": "Manage smart home supply chains including electronic component procurement, contract manufacturer oversight, and channel inventory management."},
    {"name": "smart-home-cybersecurity-ops", "description": "Manage smart home device cybersecurity including secure boot implementation, vulnerability disclosure programs, and product security incident response."},
    {"name": "smart-home-data-privacy-mgmt", "description": "Manage smart home data privacy programs including user consent management, data minimization, CCPA and GDPR compliance, and privacy impact assessments."},
    {"name": "smart-home-customer-experience", "description": "Manage smart home customer experience programs including in-app onboarding, device setup simplification, and self-service troubleshooting platforms."},
    {"name": "smart-home-ecosystem-partnerships", "description": "Develop smart home ecosystem partnerships including platform certification, technology licensing, and interoperability marketing program management."},
]

# Domain: Consumer Electronics Repair Services
skills += [
    {"name": "consumer-electronics-diagnostics", "description": "Perform consumer electronics diagnostics including component-level fault isolation, circuit board analysis, and repair feasibility assessment."},
    {"name": "mobile-device-repair-ops", "description": "Operate mobile device repair services including display replacement, battery service, water damage assessment, and genuine parts program management."},
    {"name": "laptop-desktop-repair-services", "description": "Manage laptop and desktop repair services including motherboard diagnosis, data recovery, OS reinstall, and warranty repair authorization programs."},
    {"name": "authorized-service-center-ops", "description": "Operate authorized service center programs including OEM certification maintenance, genuine parts procurement, repair authorization workflows, and warranty claim submission."},
    {"name": "electronics-repair-warranty-mgmt", "description": "Manage electronics repair warranty programs including repair guarantee administration, callback tracking, and OEM warranty claim reconciliation."},
    {"name": "consumer-electronics-parts-mgmt", "description": "Manage consumer electronics repair parts programs including OEM spare parts stocking, third-party part qualification, and parts return core programs."},
    {"name": "electronics-repair-pos-ops", "description": "Operate repair shop point-of-sale and workflow systems including repair ticket management, customer communication, and device check-in/out tracking."},
    {"name": "mail-in-repair-ops", "description": "Manage mail-in electronics repair services including shipping kit programs, device triage centers, repair workflow automation, and return logistics."},
    {"name": "commercial-av-repair-services", "description": "Provide commercial AV equipment repair services including projector lamp service, display calibration, audio amplifier repair, and preventive maintenance programs."},
    {"name": "electronics-refurbishment-ops", "description": "Manage electronics refurbishment operations including device grading, cosmetic restoration, firmware reset, and certified refurbished program certification."},
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
