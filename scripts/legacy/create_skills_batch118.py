import os

base = r"c:\Users\mirza\MAARS-Command\.claude\skills"

# Domain: Dry Bulk and Liquid Bulk Terminal Operations
skills = [
    {"name": "dry-bulk-terminal-ops", "description": "Manage dry bulk terminal operations including vessel discharge scheduling, stockpile management, conveyor systems, and dust suppression compliance."},
    {"name": "dry-bulk-commodity-handling", "description": "Handle dry bulk commodities including grain, coal, fertilizer, and minerals with proper segregation, sampling, and inventory reconciliation."},
    {"name": "bulk-terminal-equipment-mgmt", "description": "Maintain bulk terminal equipment including ship unloaders, stackers, reclaimers, and conveyor belts with predictive maintenance programs."},
    {"name": "bulk-terminal-safety-programs", "description": "Implement bulk terminal safety programs including confined space entry, dust explosion prevention, and bulk materials hazard management."},
    {"name": "bulk-terminal-environmental-compliance", "description": "Manage environmental compliance at bulk terminals including air quality permits, stormwater management, and spill prevention plans."},
    {"name": "bulk-terminal-throughput-optimization", "description": "Optimize bulk terminal throughput using demurrage minimization, berth scheduling, stockpile blending, and equipment utilization analytics."},
    {"name": "liquid-bulk-terminal-operations", "description": "Operate liquid bulk terminals including tank farm management, pipeline manifolds, product transfer metering, and vapor recovery systems."},
    {"name": "liquid-terminal-product-segregation", "description": "Manage liquid terminal product segregation including compatibility matrices, line flushing procedures, and contamination prevention protocols."},
    {"name": "terminal-vessel-interface-ops", "description": "Coordinate terminal-vessel interface operations including berth preparation, hose connections, ship-shore safety checklists, and cargo documentation."},
    {"name": "bulk-terminal-commercial-ops", "description": "Manage bulk terminal commercial operations including throughput agreements, storage contracts, handling rate tariffs, and customer billing."},
]

# Domain: Tank Farm Management
skills += [
    {"name": "tank-farm-asset-management", "description": "Manage tank farm assets including inspection programs, integrity management, cathodic protection, and tank bottom assessment planning."},
    {"name": "tank-farm-safety-management", "description": "Implement tank farm safety management including hot work permits, tank entry procedures, overfill prevention, and firefighting systems."},
    {"name": "tank-farm-environmental-management", "description": "Manage tank farm environmental compliance including secondary containment, groundwater monitoring, leak detection, and SPCC plan administration."},
    {"name": "tank-farm-inventory-management", "description": "Manage tank farm inventory using automated tank gauging, product reconciliation, custody transfer metering, and inventory reporting."},
    {"name": "tank-farm-product-blending", "description": "Operate tank farm product blending including blend recipe management, in-line and in-tank blending, quality verification, and blend certification."},
    {"name": "tank-farm-maintenance-programs", "description": "Execute tank farm maintenance programs including cleaning operations, inspection coordination, repair scheduling, and return-to-service testing."},
    {"name": "tank-farm-pipeline-operations", "description": "Manage tank farm pipeline operations including valve sequencing, pig launching and receiving, pressure testing, and pipeline integrity programs."},
    {"name": "tank-farm-terminal-automation", "description": "Operate tank farm terminal automation including SCADA integration, remote valve control, automated truck loading, and alarm management."},
    {"name": "tank-farm-emergency-response", "description": "Plan and execute tank farm emergency response including spill containment, fire response procedures, evacuation plans, and regulatory notification."},
    {"name": "tank-farm-permit-compliance", "description": "Manage tank farm regulatory permit compliance including air emission controls, wastewater discharge permits, and operating license renewal."},
]

# Domain: Specialty Gas Distribution
skills += [
    {"name": "specialty-gas-cylinder-distribution", "description": "Manage specialty gas cylinder distribution including fill plant operations, cylinder tracking, asset management, and customer delivery logistics."},
    {"name": "specialty-gas-quality-assurance", "description": "Ensure specialty gas quality assurance including analytical testing, certificate of analysis issuance, traceability management, and customer specification compliance."},
    {"name": "specialty-gas-blend-manufacturing", "description": "Manufacture specialty gas blends including gravimetric preparation, certified reference gas production, and mixture traceability documentation."},
    {"name": "specialty-gas-customer-service", "description": "Manage specialty gas customer service including technical support, gas selection guidance, safety data sheet provision, and emergency response coordination."},
    {"name": "specialty-gas-regulatory-compliance", "description": "Navigate specialty gas regulatory compliance including DOT cylinder qualification, hazmat shipping requirements, and compressed gas safety standards."},
    {"name": "specialty-gas-cryogenic-distribution", "description": "Operate specialty cryogenic gas distribution including liquid nitrogen, oxygen, and argon delivery, Dewar management, and cryogenic safety programs."},
    {"name": "specialty-gas-asset-management", "description": "Manage specialty gas asset management including cylinder inventory tracking, rental billing, asset recovery, and maintenance scheduling."},
    {"name": "specialty-gas-application-support", "description": "Provide specialty gas application support including process gas recommendations, purity specifications, analytical instrument gases, and calibration gas selection."},
    {"name": "specialty-gas-supply-contracts", "description": "Administer specialty gas supply contracts including pricing agreements, take-or-pay provisions, volume commitments, and contract performance monitoring."},
    {"name": "specialty-gas-safety-programs", "description": "Implement specialty gas safety programs including handler training, leak detection protocols, gas detector calibration, and emergency procedures."},
]

# Domain: MRO Industrial Supply Distribution
skills += [
    {"name": "mro-inventory-management", "description": "Manage MRO inventory including vending machine restocking, consignment programs, min-max replenishment, and obsolescence reduction."},
    {"name": "mro-supplier-consolidation", "description": "Execute MRO supplier consolidation programs including spend analysis, supplier rationalization, contract negotiation, and performance tracking."},
    {"name": "mro-cataloging-standardization", "description": "Manage MRO cataloging and standardization including product normalization, duplicate elimination, attribute enrichment, and procurement taxonomy."},
    {"name": "mro-customer-service-ops", "description": "Operate MRO customer service including counter sales, will-call fulfillment, emergency sourcing, and technical application support."},
    {"name": "mro-vendor-managed-inventory", "description": "Deploy MRO vendor-managed inventory programs including on-site stocking, automated replenishment, usage analytics, and customer cost reporting."},
    {"name": "mro-ecommerce-operations", "description": "Manage MRO ecommerce operations including product content, search optimization, punchout catalog integration, and online order management."},
    {"name": "mro-pricing-margin-management", "description": "Manage MRO pricing and margin including cost-plus and market-based pricing, customer-specific contracts, and margin analysis reporting."},
    {"name": "mro-warehouse-operations", "description": "Operate MRO warehouse operations including receiving, putaway, pick-pack-ship, will-call counter, and returns processing workflows."},
    {"name": "mro-technical-sales", "description": "Support MRO technical sales including product application engineering, cross-sell and up-sell programs, and national account management."},
    {"name": "mro-private-label-programs", "description": "Develop MRO private label programs including product sourcing, specification development, branding, and margin enhancement strategy."},
]

# Domain: Electrical and HVAC Wholesale Distribution
skills += [
    {"name": "electrical-wholesale-counter-ops", "description": "Operate electrical wholesale counter operations including contractor service, quote preparation, emergency order fulfillment, and technical assistance."},
    {"name": "electrical-wholesale-project-sales", "description": "Manage electrical wholesale project sales including bid coordination, job tracking, material delivery scheduling, and project account management."},
    {"name": "electrical-wholesale-inventory-ops", "description": "Manage electrical wholesale inventory operations including demand forecasting, stock replenishment, slow-moving inventory management, and returns handling."},
    {"name": "electrical-wholesale-vendor-programs", "description": "Administer electrical wholesale vendor programs including rebate management, co-op advertising, promotional pricing, and agency line management."},
    {"name": "hvac-wholesale-distributor-ops", "description": "Operate HVAC wholesale distribution including equipment sales, parts distribution, contractor training programs, and warranty claim processing."},
    {"name": "hvac-wholesale-branch-management", "description": "Manage HVAC wholesale branch operations including staffing, inventory planning, contractor relationships, and branch financial performance."},
    {"name": "hvac-wholesale-technical-training", "description": "Deliver HVAC wholesale technical training programs including product installation courses, troubleshooting seminars, and certification preparation."},
    {"name": "hvac-wholesale-equipment-programs", "description": "Manage HVAC wholesale equipment programs including new product launches, competitive replacements, and energy efficiency rebate programs."},
    {"name": "hvac-distributor-service-capabilities", "description": "Develop HVAC distributor service capabilities including in-house service technicians, loaner equipment programs, and expedited warranty service."},
    {"name": "electrical-hvac-ecommerce-platform", "description": "Operate electrical and HVAC wholesale ecommerce platforms including product catalog management, contractor portal features, and online ordering tools."},
]

# Domain: Foodservice Equipment Distribution
skills += [
    {"name": "foodservice-equipment-dealer-ops", "description": "Manage foodservice equipment dealer operations including showroom sales, design services, equipment procurement, and project installation coordination."},
    {"name": "foodservice-equipment-service-ops", "description": "Operate foodservice equipment service operations including preventive maintenance contracts, emergency repair dispatch, and parts inventory management."},
    {"name": "foodservice-equipment-project-mgmt", "description": "Manage foodservice equipment projects including kitchen design, equipment specification, fabrication coordination, installation, and startup commissioning."},
    {"name": "foodservice-equipment-parts-distribution", "description": "Distribute foodservice equipment parts including factory-authorized parts programs, same-day fulfillment, and reverse logistics management."},
    {"name": "foodservice-equipment-sales-programs", "description": "Develop foodservice equipment sales programs including chain account management, factory representative coordination, and foodservice operator targeting."},
    {"name": "foodservice-equipment-financing", "description": "Manage foodservice equipment financing including lease programs, equipment financing agreements, and rent-to-own arrangements for operators."},
    {"name": "foodservice-equipment-training", "description": "Deliver foodservice equipment training programs including operator certification, service technician training, and food safety compliance courses."},
    {"name": "foodservice-equipment-warranty-mgmt", "description": "Administer foodservice equipment warranty management including factory-authorized warranty claims, extended warranty programs, and performance data analysis."},
    {"name": "foodservice-distribution-channel", "description": "Manage foodservice distribution channels including dealer networks, manufacturer representative relations, and national account program administration."},
    {"name": "foodservice-equipment-energy-programs", "description": "Support foodservice equipment energy efficiency programs including utility rebate qualification, ENERGY STAR certification, and payback analysis."},
]

# Domain: Modular Space and Portable Storage
skills += [
    {"name": "modular-space-fleet-management", "description": "Manage modular space fleet operations including asset acquisition, refurbishment, dispatch, installation, and dismantling services."},
    {"name": "modular-space-sales-operations", "description": "Operate modular space sales including rental and lease pricing, customer needs assessment, site feasibility, and contract administration."},
    {"name": "modular-space-installation-services", "description": "Deliver modular space installation services including site preparation, blocking and leveling, utility connections, and ADA compliance compliance."},
    {"name": "modular-space-permit-compliance", "description": "Manage modular space permit compliance including building permits, fire marshal approvals, electrical inspections, and occupancy certificates."},
    {"name": "portable-storage-container-ops", "description": "Manage portable storage container operations including container fleet tracking, delivery scheduling, placement coordination, and retrieval logistics."},
    {"name": "portable-storage-rental-ops", "description": "Operate portable storage rental operations including pricing management, rental agreement administration, customer service, and damage assessment."},
    {"name": "modular-building-construction-mgmt", "description": "Manage modular building construction projects including module fabrication coordination, site civil work, crane placement, and MEP connections."},
    {"name": "modular-fleet-maintenance-programs", "description": "Maintain modular space fleet including scheduled refurbishment, damage repairs, interior upgrades, and quality inspection programs."},
    {"name": "modular-space-national-account-mgmt", "description": "Manage modular space national accounts including volume agreements, fleet allocation, multi-site coordination, and consolidated invoicing."},
    {"name": "portable-storage-commercial-sales", "description": "Support portable storage commercial sales programs including construction site storage, retail overflow, disaster relief deployment, and military contracts."},
]

# Domain: Environmental and Specialty Contractor Services
skills += [
    {"name": "dewatering-services-management", "description": "Manage construction dewatering services including pump selection, discharge permit compliance, groundwater monitoring, and dewatering system design."},
    {"name": "hydrovac-excavation-operations", "description": "Operate hydrovac excavation services including utility locate coordination, vacuum excavation safety, spoil disposal logistics, and customer project management."},
    {"name": "ground-penetrating-radar-services", "description": "Deliver ground penetrating radar inspection services including subsurface investigation, utility mapping, void detection, and reporting documentation."},
    {"name": "concrete-cutting-drilling-services", "description": "Manage concrete cutting and core drilling services including saw cutting, diamond drilling, flat sawing, wire sawing, and dust control compliance."},
    {"name": "environmental-drilling-services", "description": "Provide environmental drilling services including soil boring programs, monitoring well installation, soil vapor extraction, and regulatory sampling."},
    {"name": "contaminated-soil-remediation-ops", "description": "Manage contaminated soil remediation operations including excavation management, soil classification, transportation, treatment, and disposal documentation."},
    {"name": "brownfield-remediation-services", "description": "Deliver brownfield remediation services including site investigation, remedy selection, regulatory liaison, cost-to-close analysis, and closure reporting."},
    {"name": "asbestos-lead-abatement-ops", "description": "Operate asbestos and lead abatement services including hazmat survey coordination, abatement work plans, air monitoring, and regulatory compliance documentation."},
    {"name": "mold-remediation-operations", "description": "Manage mold remediation operations including moisture investigation, containment setup, remediation procedures, post-remediation verification, and clearance testing."},
    {"name": "demolition-contractor-ops", "description": "Manage demolition contractor operations including structural assessment, hazmat abatement coordination, debris recycling, and site clearing for redevelopment."},
]

# Domain: Restoration and Cleaning Services
skills += [
    {"name": "water-damage-restoration-ops", "description": "Operate water damage restoration services including moisture mapping, drying equipment deployment, contents management, and insurance claim coordination."},
    {"name": "fire-smoke-restoration-ops", "description": "Manage fire and smoke restoration services including damage assessment, soot removal, odor neutralization, content cleaning, and structural drying."},
    {"name": "content-restoration-services", "description": "Deliver content restoration services including contents inventory, pack-out logistics, cleaning and deodorization, storage, and return delivery coordination."},
    {"name": "biohazard-cleanup-operations", "description": "Operate biohazard cleanup services including scene assessment, personal protective equipment programs, regulated waste disposal, and decontamination verification."},
    {"name": "disaster-restoration-project-mgmt", "description": "Manage disaster restoration projects including emergency response mobilization, project scoping, subcontractor coordination, and progress billing."},
    {"name": "carpet-upholstery-cleaning-ops", "description": "Operate carpet and upholstery cleaning services including chemical selection, hot water extraction, low-moisture methods, and stain treatment programs."},
    {"name": "hard-floor-care-services", "description": "Manage hard floor care services including stripping, refinishing, concrete polishing, stone honing, and maintenance program design."},
    {"name": "pressure-washing-services-ops", "description": "Operate pressure washing and exterior cleaning services including surface preparation, chemical application, hot water systems, and environmental compliance."},
    {"name": "roof-exterior-cleaning-services", "description": "Manage roof and exterior cleaning services including soft wash applications, chemical treatment, algae and moss removal, and gutter cleaning programs."},
    {"name": "window-cleaning-commercial-ops", "description": "Operate commercial window cleaning services including rope descent, aerial lift operations, water-fed pole systems, and high-rise safety programs."},
]

# Domain: Chimney, Fireplace, and Duct Services
skills += [
    {"name": "chimney-sweep-operations", "description": "Manage chimney sweep operations including Level I and II inspection programs, creosote removal, firebox repair, and liner installation services."},
    {"name": "fireplace-hearth-services", "description": "Operate fireplace and hearth services including gas fireplace installation, wood-burning insert service, pellet stove maintenance, and showroom sales."},
    {"name": "air-duct-cleaning-operations", "description": "Manage air duct cleaning operations including system inspection, source removal technique, NADCA standard compliance, and dryer vent cleaning services."},
    {"name": "chimney-liner-installation", "description": "Deliver chimney liner installation services including stainless steel liner systems, cast-in-place liner applications, and chimney cap and crown repair."},
    {"name": "chimney-masonry-restoration", "description": "Provide chimney masonry restoration including tuckpointing, brick replacement, waterproofing applications, and chimney rebuild coordination."},
    {"name": "gutter-installation-services", "description": "Operate gutter installation and cleaning services including seamless gutter fabrication, downspout routing, gutter guard installation, and maintenance contracts."},
    {"name": "dryer-vent-cleaning-ops", "description": "Manage dryer vent cleaning operations including blockage inspection, cleaning equipment operation, lint trap maintenance, and fire risk documentation."},
    {"name": "indoor-air-quality-services", "description": "Deliver indoor air quality services including air sampling, allergen testing, HVAC hygiene inspection, UV germicidal installation, and remediation recommendations."},
    {"name": "duct-sealing-insulation-services", "description": "Provide duct sealing and insulation services including aerosol duct sealing, mastic application, duct insulation installation, and blower door testing."},
    {"name": "ventilation-inspection-services", "description": "Conduct ventilation inspection services including exhaust fan assessment, kitchen hood performance testing, makeup air evaluation, and code compliance reporting."},
]

# Domain: Pest Control and Wildlife Management
skills += [
    {"name": "pest-control-operations-mgmt", "description": "Manage pest control operations including route management, technician scheduling, chemical inventory, regulatory compliance, and customer communication."},
    {"name": "termite-wood-destroying-organism-services", "description": "Deliver termite and wood-destroying organism services including comprehensive inspection, treatment plan design, monitoring program management, and damage repair coordination."},
    {"name": "bed-bug-treatment-operations", "description": "Operate bed bug treatment services including canine inspection teams, heat treatment programs, chemical treatment protocols, and follow-up monitoring."},
    {"name": "wildlife-removal-relocation-ops", "description": "Manage wildlife removal and relocation services including species identification, humane trapping, exclusion installation, and post-removal damage repair."},
    {"name": "rodent-exclusion-services", "description": "Provide rodent exclusion services including entry point identification, exclusion material installation, sanitation consulting, and ongoing monitoring programs."},
    {"name": "mosquito-tick-control-programs", "description": "Manage mosquito and tick control programs including barrier treatment applications, larvicide programs, source reduction consulting, and treatment scheduling."},
    {"name": "commercial-pest-management-programs", "description": "Design commercial pest management programs including IPM plans, HACCP compliance support, audit preparation, and documentation for food service facilities."},
    {"name": "fumigation-services-management", "description": "Manage fumigation services including structural fumigation for stored product pests, commodity fumigation, tent installation coordination, and clearance certification."},
    {"name": "pest-control-chemical-management", "description": "Manage pest control chemical programs including pesticide storage compliance, applicator licensing, label compliance, and disposal of expired products."},
    {"name": "pest-control-technology-programs", "description": "Implement pest control technology programs including remote monitoring devices, digital reporting platforms, and customer portal service history access."},
]

# Domain: Estate Sale, Auction, and Resale Services
skills += [
    {"name": "estate-sale-operations-mgmt", "description": "Manage estate sale operations including estate assessment, pricing research, staging, advertising, sale execution, and post-sale cleanup coordination."},
    {"name": "estate-sale-online-platform-ops", "description": "Operate estate sale online platforms including item photography, catalog creation, bidding management, payment processing, and buyer pickup coordination."},
    {"name": "auction-house-consignment-ops", "description": "Manage auction house consignment operations including consignor intake, property assessment, cataloging, presale marketing, and post-sale settlement."},
    {"name": "auction-bidding-platform-ops", "description": "Operate auction bidding platforms including live auction streaming, absentee bidding management, buyer registration, and payment and shipping fulfillment."},
    {"name": "pawn-and-loan-operations", "description": "Manage pawn and loan operations including item appraisal, loan origination, storage management, redemption processing, and forfeiture inventory sales."},
    {"name": "consignment-shop-operations", "description": "Operate consignment shop operations including consignor intake, pricing, inventory display, split payout processing, and unsold item return management."},
    {"name": "thrift-store-donation-processing", "description": "Manage thrift store donation processing including intake sorting, quality grading, pricing, display merchandising, and donation tax receipt issuance."},
    {"name": "online-resale-marketplace-ops", "description": "Operate online resale marketplace operations including listing creation, pricing optimization, cross-platform selling, shipping management, and returns handling."},
    {"name": "liquidation-merchandise-sourcing", "description": "Manage liquidation merchandise sourcing including retailer overstock purchasing, pallet bidding, manifest management, and resale channel optimization."},
    {"name": "estate-liquidation-business-mgmt", "description": "Manage estate liquidation business operations including client acquisition, estimating, contract management, crew scheduling, and profitability analysis."},
]

# Domain: E-Commerce Fulfillment and Last-Mile
skills += [
    {"name": "ecommerce-fulfillment-center-ops", "description": "Operate ecommerce fulfillment centers including receiving, putaway, pick-pack-ship, returns processing, and multi-channel order management."},
    {"name": "last-mile-delivery-management", "description": "Manage last-mile delivery operations including route optimization, driver dispatching, proof of delivery, and customer notification workflows."},
    {"name": "parcel-carrier-management", "description": "Manage parcel carrier relationships including rate negotiation, service level monitoring, claims management, and multi-carrier rate shopping."},
    {"name": "returns-reverse-logistics-ops", "description": "Operate returns and reverse logistics programs including returns authorization, inspection, refurbishment, restocking, and disposition management."},
    {"name": "same-day-delivery-operations", "description": "Manage same-day delivery operations including zone-based routing, driver sourcing, real-time tracking, and customer communication platforms."},
    {"name": "local-courier-messenger-services", "description": "Operate local courier and messenger services including on-demand routing, medical specimen transport, legal document delivery, and route planning."},
    {"name": "fulfillment-client-onboarding", "description": "Manage 3PL fulfillment client onboarding including system integration, SKU setup, inbound receiving protocols, and SLA agreement configuration."},
    {"name": "fulfillment-kitting-assembly-ops", "description": "Operate fulfillment kitting and assembly services including kit bill of materials management, work order execution, quality inspection, and throughput tracking."},
    {"name": "cold-chain-fulfillment-ops", "description": "Manage cold chain fulfillment operations including temperature-controlled receiving, storage zone management, pack-out protocols, and carrier compliance."},
    {"name": "fulfillment-analytics-performance", "description": "Analyze fulfillment center performance including order accuracy, on-time shipping, labor productivity, dock-to-stock time, and cost-per-order metrics."},
]

# Domain: Parking, Towing, and Roadside Services
skills += [
    {"name": "parking-facility-management-ops", "description": "Manage parking facility operations including access control, revenue control equipment, rate management, violation enforcement, and customer service."},
    {"name": "parking-technology-integration", "description": "Integrate parking technology systems including license plate recognition, contactless payment, mobile payment apps, and parking guidance systems."},
    {"name": "valet-parking-service-ops", "description": "Operate valet parking services including key control systems, vehicle inspection documentation, staging logistics, and event staffing management."},
    {"name": "towing-recovery-dispatch-ops", "description": "Manage towing and recovery dispatch operations including call intake, driver assignment, motor club billing, impound lot management, and vehicle release."},
    {"name": "roadside-assistance-program-ops", "description": "Operate roadside assistance programs including jump start, tire change, fuel delivery, lockout service, and winch-out services with ETA management."},
    {"name": "parking-revenue-management", "description": "Manage parking revenue optimization including dynamic pricing models, event rate management, occupancy-based pricing, and revenue reporting analytics."},
    {"name": "impound-lot-management", "description": "Manage impound lot operations including vehicle intake documentation, storage fee accrual, lien notification, vehicle auction, and compliance reporting."},
    {"name": "parking-enforcement-services", "description": "Operate parking enforcement services including citation issuance, boot and tow operations, permit program management, and violation adjudication."},
    {"name": "fleet-towing-contract-management", "description": "Manage fleet towing contracts including fleet account billing, priority service agreements, vehicle condition reporting, and performance SLA tracking."},
    {"name": "vehicle-storage-facility-ops", "description": "Operate vehicle storage facilities including indoor and outdoor storage, climate-controlled units, long-term storage contracts, and vehicle preservation services."},
]

# Domain: Mobile Auto Services
skills += [
    {"name": "mobile-auto-detailing-ops", "description": "Manage mobile auto detailing operations including route scheduling, chemical supply management, van fleet maintenance, and quality control programs."},
    {"name": "auto-glass-repair-replacement", "description": "Operate auto glass repair and replacement services including mobile installation, OEM vs aftermarket glass sourcing, insurance direct billing, and ADAS recalibration."},
    {"name": "mobile-tire-service-operations", "description": "Manage mobile tire services including roadside tire change, flat repair, new tire installation at customer locations, and tire disposal logistics."},
    {"name": "fleet-washing-reconditioning", "description": "Manage fleet washing and reconditioning services including mobile wash units, chemical programs, fleet account contracts, and appearance standard compliance."},
    {"name": "mobile-oil-change-operations", "description": "Operate mobile oil change and preventive maintenance services including technician routing, oil waste disposal compliance, and fleet account management."},
    {"name": "auto-locksmith-services", "description": "Manage automotive locksmith services including key cutting and programming, vehicle entry, transponder key services, and ignition repair."},
    {"name": "paintless-dent-removal-ops", "description": "Operate paintless dent removal services including hail damage assessment, repair technique training, fleet and dealership contracts, and insurance billing."},
    {"name": "mobile-detailing-franchise-ops", "description": "Manage mobile detailing franchise operations including territory management, franchisee training, quality audits, and marketing support programs."},
    {"name": "auto-reconditioning-services", "description": "Manage automotive reconditioning services including paint touch-up, interior repair, plastic restoration, odor elimination, and auction pre-sale preparation."},
    {"name": "detailing-chemical-program-mgmt", "description": "Manage detailing chemical programs including product selection, dilution control systems, chemical safety training, and brand-preferred product programs."},
]

# Domain: Motorcycle, RV, and Marine Service
skills += [
    {"name": "motorcycle-service-repair-ops", "description": "Manage motorcycle service and repair operations including diagnostics, scheduled maintenance, customization installations, and dealer warranty service."},
    {"name": "motorcycle-parts-accessories-sales", "description": "Operate motorcycle parts and accessories sales including counter sales, catalog management, online ordering, and performance parts programs."},
    {"name": "rv-camper-service-operations", "description": "Manage RV and camper service operations including systems inspection, slide-out repair, roof maintenance, appliance service, and seasonal prep programs."},
    {"name": "rv-dealer-service-department", "description": "Operate RV dealer service departments including pre-delivery inspection, warranty claim management, technician productivity, and customer satisfaction programs."},
    {"name": "marine-engine-service-ops", "description": "Manage marine engine service operations including outboard and inboard engine repair, winterization, propeller service, and boat systems diagnostics."},
    {"name": "marina-and-boatyard-ops", "description": "Operate marinas and boatyards including slip rental management, haul and launch operations, dry stack storage, and customer service programs."},
    {"name": "boat-storage-management", "description": "Manage boat storage operations including indoor and outdoor storage, shrink wrap services, vessel inspection, and insurance compliance documentation."},
    {"name": "powersports-dealership-service", "description": "Manage powersports dealership service departments including scheduling, flat rate management, parts counter integration, and OEM warranty compliance."},
    {"name": "marine-fiberglass-repair-services", "description": "Operate marine fiberglass repair services including osmotic blister repair, gelcoat restoration, structural repair, and antifouling paint application."},
    {"name": "rv-solar-and-upgrade-services", "description": "Deliver RV solar and electrical upgrade services including solar panel installation, lithium battery systems, inverter installation, and connectivity upgrades."},
]

# Domain: Residential Exterior and Specialty Services
skills += [
    {"name": "deck-fence-construction-ops", "description": "Manage deck and fence construction operations including design consultation, material selection, permit management, installation, and post-installation maintenance."},
    {"name": "concrete-masonry-contractor-ops", "description": "Operate concrete and masonry contracting businesses including driveway installation, patio construction, retaining walls, and decorative concrete services."},
    {"name": "asphalt-paving-services", "description": "Manage asphalt paving and sealcoating services including residential driveways, parking lots, crack filling, and line striping programs."},
    {"name": "siding-exterior-cladding-services", "description": "Manage siding and exterior cladding services including vinyl, fiber cement, engineered wood, and metal siding installation, repair, and maintenance."},
    {"name": "window-door-replacement-services", "description": "Operate window and door replacement services including energy efficiency consultations, product sourcing, installation, and warranty fulfillment programs."},
    {"name": "insulation-contractor-residential", "description": "Manage residential insulation contracting including attic insulation, spray foam applications, weatherization, and energy efficiency rebate programs."},
    {"name": "garage-door-installation-services", "description": "Operate garage door installation and service businesses including door and opener installation, spring replacement, repair dispatch, and maintenance contracts."},
    {"name": "pool-and-spa-construction-ops", "description": "Manage pool and spa construction operations including design, excavation coordination, equipment selection, plumbing, electrical, and startup commissioning."},
    {"name": "home-security-installation-services", "description": "Manage home security system installation services including system design, equipment installation, monitoring service setup, and customer training."},
    {"name": "residential-generator-installation", "description": "Operate residential standby generator installation services including load calculation, permits, installation, utility coordination, and maintenance agreements."},
]

# Domain: Interior Specialty Contractor Services
skills += [
    {"name": "flooring-installation-contractor", "description": "Manage flooring installation contracting including hardwood, carpet, LVP, tile, and specialty flooring installation, subfloor preparation, and floor care programs."},
    {"name": "cabinet-countertop-installation", "description": "Operate cabinet and countertop installation services including fabrication coordination, templating, installation, and post-installation punchlist resolution."},
    {"name": "tile-setting-contractor-ops", "description": "Manage tile setting contracting operations including substrate preparation, tile layout, grouting, sealing, and specialty mosaic and natural stone work."},
    {"name": "painting-contractor-residential", "description": "Operate residential painting contracting businesses including interior and exterior painting, surface preparation, color consultation, and pressure washing prep."},
    {"name": "wallcovering-specialty-finish-services", "description": "Manage wallcovering and specialty finish services including wallpaper installation, plaster finishes, Venetian plaster, and decorative painting techniques."},
    {"name": "caulking-waterproofing-services", "description": "Provide caulking and waterproofing services including joint sealant replacement, wet area caulking, deck waterproofing, and exterior sealant programs."},
    {"name": "crawl-space-encapsulation-services", "description": "Manage crawl space encapsulation services including moisture barrier installation, dehumidifier placement, vent sealing, and structural pest treatment."},
    {"name": "basement-waterproofing-services", "description": "Operate basement waterproofing services including interior drainage systems, sump pump installation, exterior waterproofing, and wall crack injection."},
    {"name": "foundation-repair-services", "description": "Manage foundation repair services including pier and beam repair, carbon fiber wall reinforcement, piering installation, and structural warranty programs."},
    {"name": "home-renovation-project-mgmt", "description": "Manage home renovation project management including scope development, subcontractor coordination, permit management, schedule tracking, and client communication."},
]

# Domain: Septic, Drain, and Utility Services
skills += [
    {"name": "septic-system-services", "description": "Manage septic system services including pumping and cleaning, inspection, repair, system replacement, and permit compliance documentation."},
    {"name": "drain-sewer-cleaning-services", "description": "Operate drain and sewer cleaning services including hydrojetting, mechanical snaking, camera inspection, and pipe lining installation programs."},
    {"name": "septic-system-inspection-services", "description": "Provide septic system inspection services including real estate transaction inspections, dye testing, distribution box inspection, and repair recommendations."},
    {"name": "grease-trap-service-operations", "description": "Manage grease trap and interceptor service operations including pumping schedules, waste manifest management, regulatory compliance, and capacity optimization."},
    {"name": "portable-restroom-services", "description": "Operate portable restroom rental services including unit placement, service route management, special event delivery, and sanitation compliance."},
    {"name": "vacuum-truck-services-management", "description": "Manage vacuum truck services including liquid waste collection, non-hazardous industrial vacuum, and hydrovac excavation service dispatch and billing."},
    {"name": "plumbing-contractor-operations", "description": "Manage plumbing contracting operations including service dispatch, new construction plumbing, remodeling, commercial service agreements, and apprentice training."},
    {"name": "drain-lining-rehabilitation-services", "description": "Deliver drain lining and rehabilitation services including CIPP lining installation, point repair, pipe coating, and post-rehabilitation inspection."},
    {"name": "utility-locating-services", "description": "Manage utility locating services including ground penetrating radar, electromagnetic locating, vacuum exposure, and as-built mapping documentation."},
    {"name": "sewer-inspection-services", "description": "Operate sewer inspection services including CCTV camera inspection, condition assessment, defect coding, and infrastructure management reporting."},
]

# Domain: Chimney, Roof, and Waterproofing Services (continuation)
skills += [
    {"name": "roofing-contractor-residential", "description": "Manage residential roofing contracting operations including storm damage assessment, insurance claim support, shingle and flat roof installation, and maintenance."},
    {"name": "roofing-commercial-contractor", "description": "Operate commercial roofing contracting including low-slope membrane systems, metal roofing, roof restoration coatings, and preventive maintenance programs."},
    {"name": "waterproofing-construction-services", "description": "Deliver construction waterproofing services including below-grade waterproofing, balcony and plaza deck waterproofing, and expansion joint systems."},
    {"name": "flat-roof-restoration-services", "description": "Manage flat roof restoration services including coating applications, silicone roof systems, infrared moisture surveys, and extended warranty programs."},
    {"name": "roofing-inspection-services", "description": "Provide roofing inspection services including infrared thermal imaging, core sampling, condition reporting, and remaining service life estimates."},
    {"name": "solar-roofing-integration-services", "description": "Manage solar roofing integration services including roof certification, penetration flashing, integrated solar roofing products, and warranty coordination."},
    {"name": "snow-ice-removal-services", "description": "Manage snow and ice removal services including residential and commercial plowing, deicing applications, sidewalk clearing, and seasonal service contracts."},
    {"name": "exterior-painting-contractor", "description": "Operate exterior painting contracting operations including surface preparation, paint selection, commercial repaint programs, and multi-year maintenance agreements."},
    {"name": "landscaping-lawn-care-services", "description": "Manage landscaping and lawn care service businesses including design installation, turf programs, irrigation management, and seasonal cleanup services."},
    {"name": "tree-service-arboriculture-ops", "description": "Operate tree service and arboriculture businesses including tree removal, pruning, cabling, plant health care programs, and storm damage response."},
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
