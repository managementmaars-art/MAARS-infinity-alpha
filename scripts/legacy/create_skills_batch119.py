import os

base = r"c:\Users\mirza\MAARS-Command\.claude\skills"

# Domain: Glass and Glazing Contracting
skills = [
    {"name": "glazing-contractor-ops", "description": "Manage glazing contractor operations including storefront installation, curtain wall erection, glass replacement scheduling, and field crew coordination."},
    {"name": "glass-cutting-fabrication-shop", "description": "Operate glass cutting and fabrication shops including CNC cutting, edging, drilling, tempered glass ordering, and insulating unit assembly."},
    {"name": "glazing-project-estimating", "description": "Develop glazing project estimates including material takeoffs, labor hours, equipment costs, and subcontract pricing for commercial and residential projects."},
    {"name": "glass-replacement-services", "description": "Manage glass replacement services including emergency board-up, insurance claim coordination, auto glass, and commercial window replacement."},
    {"name": "glazing-building-code-compliance", "description": "Navigate glazing building code compliance including ANSI Z97.1, safety glazing locations, thermal performance, and energy code requirements."},
    {"name": "structural-glazing-systems", "description": "Manage structural glazing system installation including silicone bonding, point-fixed glass, SSG facades, and engineering coordination."},
    {"name": "glazing-warranty-management", "description": "Administer glazing warranty programs including manufacturer warranties, installation warranties, seal failure claims, and extended protection plans."},
    {"name": "glazing-supply-chain-ops", "description": "Manage glazing supply chain operations including float glass sourcing, IGU procurement, specialty glass ordering, and delivery coordination."},
    {"name": "glass-hardware-distribution", "description": "Operate glass hardware distribution including door hardware, frameless fittings, hinges, patches, and shower door hardware sales."},
    {"name": "glazing-safety-compliance", "description": "Implement glazing safety compliance programs including fall protection for glaziers, glass handling procedures, PPE requirements, and OSHA standards."},
]

# Domain: Specialty Fabrication Shops
skills += [
    {"name": "laser-cutting-job-shop", "description": "Operate laser cutting job shops including quoting, nesting, material procurement, finish operations, and customer order management."},
    {"name": "waterjet-job-shop-ops", "description": "Manage waterjet cutting job shop operations including material scheduling, programming, abrasive management, and precision inspection."},
    {"name": "plasma-cutting-services-ops", "description": "Operate plasma cutting services including bevel cutting, pipe cutting, robotic plasma, nesting software, and structural steel fabrication."},
    {"name": "custom-metal-fabrication-ops", "description": "Manage custom metal fabrication operations including design assistance, welding, forming, finishing, and on-time delivery to specification."},
    {"name": "precision-sheet-metal-fab-ops", "description": "Operate precision sheet metal fabrication including tolerancing, hardware insertion, powder coat coordination, and mil-spec requirements."},
    {"name": "ornamental-iron-fabrication", "description": "Manage ornamental iron and steel fabrication including gates, railings, fences, architectural metalwork design, and installation coordination."},
    {"name": "structural-steel-fab-ops", "description": "Operate structural steel fabrication shops including detailing review, fit-up, welding certification, blast and paint, and shipping logistics."},
    {"name": "machine-shop-job-scheduling", "description": "Schedule machine shop jobs including quoting, router creation, machine loading, subcontract management, and on-time delivery tracking."},
    {"name": "specialty-fab-quoting-platform", "description": "Operate specialty fabrication quoting platforms including instant quoting, DFM feedback, lead time management, and customer portal integration."},
    {"name": "fab-shop-quality-management", "description": "Manage fabrication shop quality programs including first article inspection, in-process checks, final inspection, and customer acceptance criteria."},
]

# Domain: Metal Service Centers and Distribution
skills += [
    {"name": "metals-service-center-ops", "description": "Operate metals service center operations including inventory management, processing services, order fulfillment, and customer service."},
    {"name": "steel-distribution-ops", "description": "Manage steel distribution operations including carbon flat, long products, tube and pipe, plate, and structural steel inventory and sales."},
    {"name": "aluminum-distribution-ops", "description": "Operate aluminum distribution including extrusions, sheet and plate, bar and rod, tread plate, and finished products sales and processing."},
    {"name": "metals-processing-services", "description": "Manage metals processing services including cut-to-length, slitting, leveling, blanking, sawing, and precision shearing operations."},
    {"name": "metals-inventory-management", "description": "Manage metals inventory including heat number traceability, FIFO rotation, aging analysis, and optimal stock level maintenance."},
    {"name": "metals-pricing-strategy", "description": "Develop metals pricing strategies including market index tracking, surcharge management, contract pricing, and spot market pricing."},
    {"name": "metals-supply-chain-management", "description": "Manage metals supply chains including mill relationships, import sourcing, logistics optimization, and supply reliability programs."},
    {"name": "metals-customer-programs", "description": "Develop metals customer programs including consignment inventory, VMI, blanket orders, just-in-time delivery, and toll processing."},
    {"name": "stainless-steel-distribution", "description": "Operate stainless steel distribution including flat-rolled, bar, tubing, fittings, and specialty grades for food processing and chemical markets."},
    {"name": "specialty-metals-distribution", "description": "Manage specialty metals distribution including titanium, nickel alloys, cobalt, and high-performance alloys for aerospace and defense markets."},
]

# Domain: Building Products Distribution
skills += [
    {"name": "building-products-wholesale-ops", "description": "Operate building products wholesale distribution including lumber, panels, drywall, insulation, and roofing products sales and logistics."},
    {"name": "lumber-yard-operations", "description": "Manage lumber yard operations including inventory receiving, grading, remanufacturing, contractor sales, and delivery fleet management."},
    {"name": "millwork-distribution-ops", "description": "Operate millwork distribution including doors, windows, trim, cabinetry, and architectural millwork for residential and commercial markets."},
    {"name": "roofing-supply-distribution", "description": "Manage roofing supply distribution including shingles, underlayment, metal roofing, flat roof systems, and accessories for roofing contractors."},
    {"name": "drywall-insulation-distribution", "description": "Operate drywall and insulation distribution including board, compound, steel framing, glass wool, spray foam, and accessories."},
    {"name": "masonry-supply-distribution", "description": "Manage masonry supply distribution including brick, block, stone, mortar, grout, ties, and masonry accessories for contractors."},
    {"name": "flooring-distribution-ops", "description": "Operate flooring distribution including hardwood, LVP, tile, carpet, underlayment, and adhesives for flooring contractors and retailers."},
    {"name": "hardware-distribution-ops", "description": "Manage hardware distribution including fasteners, anchors, rough hardware, finish hardware, and tools for contractors and retailers."},
    {"name": "building-envelope-distribution", "description": "Distribute building envelope products including housewrap, flashings, caulks, sealants, weather barriers, and drainage planes."},
    {"name": "exterior-products-distribution", "description": "Manage exterior building products distribution including siding, soffit, fascia, trim, and cladding systems for residential and commercial markets."},
]

# Domain: Self-Storage Facility Operations
skills += [
    {"name": "self-storage-facility-management", "description": "Manage self-storage facility operations including unit rentals, tenant management, access control, collections, and facility maintenance."},
    {"name": "self-storage-revenue-management", "description": "Optimize self-storage revenue including dynamic pricing, street rate management, occupancy forecasting, and promotional programs."},
    {"name": "self-storage-digital-marketing", "description": "Execute self-storage digital marketing including SEO, PPC, reputation management, social media, and online booking optimization."},
    {"name": "self-storage-facility-development", "description": "Develop self-storage facilities including site selection, zoning, construction management, lease-up planning, and stabilization."},
    {"name": "self-storage-tenant-management", "description": "Manage self-storage tenants including move-in process, payment management, lien law compliance, and auction management."},
    {"name": "self-storage-access-control-ops", "description": "Operate self-storage access control systems including electronic gates, keypads, smart locks, CCTV monitoring, and alarm management."},
    {"name": "self-storage-software-operations", "description": "Operate self-storage management software including unit inventory, billing automation, online rentals, and reporting dashboards."},
    {"name": "self-storage-portfolio-management", "description": "Manage self-storage facility portfolios including performance benchmarking, operator relationships, acquisition underwriting, and value-add programs."},
    {"name": "climate-controlled-storage-ops", "description": "Operate climate-controlled storage facilities including HVAC management, humidity control, specialty storage, and premium pricing strategies."},
    {"name": "boat-rv-storage-facility-ops", "description": "Manage boat and RV storage facilities including covered storage, outdoor lots, customer service, and seasonal demand management."},
]

# Domain: Document Management and Records Storage
skills += [
    {"name": "records-storage-facility-ops", "description": "Operate records storage facilities including box intake, indexing, retrieval services, document destruction, and chain of custody management."},
    {"name": "records-management-compliance", "description": "Manage records compliance programs including retention schedule development, legal hold management, and regulatory compliance documentation."},
    {"name": "digital-scanning-services", "description": "Operate document scanning and digitization services including high-volume scanning, OCR processing, metadata indexing, and delivery formats."},
    {"name": "document-destruction-compliance", "description": "Manage document destruction compliance including certificate of destruction, NAID certification, hard drive destruction, and audit documentation."},
    {"name": "records-center-software-ops", "description": "Operate records center management software including barcode tracking, retrieval workflows, billing automation, and client portals."},
    {"name": "vault-storage-services", "description": "Manage high-security vault storage services including media vaulting, disaster recovery storage, vital records protection, and access management."},
    {"name": "offsite-document-storage-sales", "description": "Develop offsite document storage sales programs including prospect qualification, contract negotiation, transition planning, and account management."},
    {"name": "healthcare-records-storage", "description": "Manage healthcare records storage including HIPAA compliance, medical records retention, ROI services, and PHI security protocols."},
    {"name": "legal-records-management", "description": "Operate legal records management services including litigation support, e-discovery, court filing management, and attorney file tracking."},
    {"name": "records-center-operations-tech", "description": "Deploy records center technology including warehouse management systems, barcode automation, conveyor integration, and robotic retrieval."},
]

# Domain: Commercial Printing and Mailing Services
skills += [
    {"name": "commercial-print-shop-ops", "description": "Operate commercial print shop operations including job intake, prepress workflow, press scheduling, bindery coordination, and delivery logistics."},
    {"name": "direct-mail-production-ops", "description": "Manage direct mail production operations including list processing, variable data printing, folding, inserting, USPS coordination, and postal optimization."},
    {"name": "print-mailing-client-services", "description": "Manage print and mailing client services including project management, proofing workflows, change management, and account retention."},
    {"name": "commercial-printing-estimating", "description": "Develop commercial printing estimates including paper costs, make-ready, run rates, finishing, and delivery for offset and digital print."},
    {"name": "print-procurement-management", "description": "Manage print procurement programs including supplier selection, specifications management, competitive bidding, and quality auditing."},
    {"name": "mailing-list-management", "description": "Manage mailing list services including NCOA processing, CASS certification, duplicate elimination, list enhancement, and USPS discounts."},
    {"name": "wide-format-print-production", "description": "Operate wide format print production including banners, signage, vehicle wraps, trade show graphics, and large-format digital output."},
    {"name": "print-fulfillment-services", "description": "Manage print fulfillment services including kitting, warehousing, on-demand printing, kit assembly, and drop-shipping to end recipients."},
    {"name": "transactional-print-services", "description": "Operate transactional print services including statement printing, explanation of benefits, insurance documents, and compliance communications."},
    {"name": "sustainable-print-programs", "description": "Implement sustainable printing programs including FSC certification, recycled substrates, soy inks, carbon neutral printing, and waste reduction."},
]

# Domain: Sign and Graphics Manufacturing
skills += [
    {"name": "sign-shop-production-ops", "description": "Operate sign shop production operations including substrate cutting, vinyl application, digital printing, installation scheduling, and permit management."},
    {"name": "vehicle-wrap-production", "description": "Manage vehicle wrap production including design for wrap, print and lamination, installation quality, and fleet wrap programs."},
    {"name": "architectural-signage-systems", "description": "Develop architectural signage systems including wayfinding design, ADA compliance, materials selection, manufacturing, and installation management."},
    {"name": "led-signage-systems", "description": "Manage LED signage systems including display selection, content management, technical installation, remote monitoring, and service contracts."},
    {"name": "outdoor-advertising-structures", "description": "Manage outdoor advertising structures including billboard fabrication, structural engineering, permit compliance, and lighting systems."},
    {"name": "sign-manufacturing-estimating", "description": "Develop sign manufacturing estimates including materials, fabrication labor, electrical components, installation, and permit costs."},
    {"name": "sign-installation-services", "description": "Manage sign installation services including lift equipment, electrical connections, anchor systems, site surveys, and safety compliance."},
    {"name": "retail-signage-programs", "description": "Manage retail signage programs including prototype development, rollout coordination, brand standards, and multi-site installation management."},
    {"name": "interior-graphics-production", "description": "Operate interior graphics production including wall graphics, floor graphics, window films, dimensional letters, and environmental branding."},
    {"name": "sign-permit-management", "description": "Manage sign permit programs including municipal code research, variance applications, permit filing, inspection coordination, and approval tracking."},
]

# Domain: Promotional Products Distribution
skills += [
    {"name": "promo-products-distributor-ops", "description": "Operate promotional products distributor operations including order management, supplier sourcing, imprint coordination, and customer delivery."},
    {"name": "promo-products-sales-programs", "description": "Develop promotional products sales programs including company store management, corporate gifting, event merchandise, and tradeshow programs."},
    {"name": "promo-supplier-relationship-mgmt", "description": "Manage promotional products supplier relationships including preferred vendor programs, artwork requirements, quality audits, and payment terms."},
    {"name": "promo-products-sourcing", "description": "Source promotional products including domestic and import sourcing, product trend analysis, safety compliance, and catalog management."},
    {"name": "branded-merchandise-programs", "description": "Develop branded merchandise programs including product selection, decoration methods, brand standards enforcement, and inventory management."},
    {"name": "promo-products-ecommerce-ops", "description": "Operate promotional products ecommerce including online stores, product configurators, workflow automation, and fulfillment integration."},
    {"name": "promo-products-imprint-management", "description": "Manage promotional products imprint operations including art preparation, screen printing, embroidery, pad printing, and laser engraving."},
    {"name": "corporate-gifting-programs", "description": "Manage corporate gifting programs including gift selection, personalization, fulfillment, kitting, gift wrapping, and executive gifting services."},
    {"name": "recognition-award-programs", "description": "Design employee recognition and award programs including award selection, engraving, milestone programs, service awards, and peer recognition."},
    {"name": "promo-product-safety-compliance", "description": "Manage promotional product safety compliance including Prop 65, CPSC requirements, ASTM standards, country of origin, and testing programs."},
]

# Domain: IT Asset Disposition and Electronic Recycling
skills += [
    {"name": "itad-services-management", "description": "Manage IT asset disposition services including data destruction, asset valuation, remarketing, recycling, and certificate of destruction issuance."},
    {"name": "data-destruction-certification", "description": "Operate certified data destruction services including NIST 800-88 compliance, degaussing, physical destruction, and audit documentation."},
    {"name": "electronics-recycling-operations", "description": "Operate electronics recycling operations including collection, sorting, disassembly, component recovery, and downstream vendor management."},
    {"name": "itad-asset-recovery-programs", "description": "Develop ITAD asset recovery programs including buy-back programs, lease return processing, corporate device collection, and remarketing."},
    {"name": "refurbished-it-equipment-sales", "description": "Manage refurbished IT equipment sales including grading, testing, warranty programs, B2B sales, and online marketplace operations."},
    {"name": "e-waste-compliance-management", "description": "Manage e-waste regulatory compliance including state EPR programs, RIOS and R2 certification, export restrictions, and compliance documentation."},
    {"name": "itad-chain-of-custody-mgmt", "description": "Manage ITAD chain of custody including asset tracking, secure transportation, facility security, processing documentation, and client reporting."},
    {"name": "mobile-device-itad-programs", "description": "Operate mobile device ITAD programs including smartphone buyback, data wiping certification, cosmetic grading, and carrier unlock management."},
    {"name": "corporate-device-recycling-programs", "description": "Develop corporate device recycling programs including trade-in logistics, employee device collection, charitable donation programs, and impact reporting."},
    {"name": "itad-vendor-management", "description": "Manage ITAD vendor programs including downstream vendor audits, certification requirements, material flow tracking, and liability management."},
]

# Domain: Medical Equipment Refurbishment
skills += [
    {"name": "medical-equipment-refurbishment-ops", "description": "Operate medical equipment refurbishment operations including acquisition, cleaning, inspection, parts replacement, and performance testing."},
    {"name": "refurbished-medical-device-sales", "description": "Manage refurbished medical device sales including grading standards, warranty programs, regulatory compliance, and healthcare customer management."},
    {"name": "biomedical-equipment-service-ops", "description": "Operate biomedical equipment service operations including PM scheduling, corrective maintenance, loaner programs, and service contract management."},
    {"name": "medical-imaging-refurbishment", "description": "Manage medical imaging equipment refurbishment including CT, MRI, X-ray, and ultrasound systems refurbishment and performance validation."},
    {"name": "patient-monitoring-refurbishment", "description": "Operate patient monitoring equipment refurbishment including multi-parameter monitors, defibrillators, ventilators, and infusion pumps."},
    {"name": "medical-equipment-parts-sourcing", "description": "Manage medical equipment parts sourcing including OEM and compatible parts procurement, parts interchangeability, and inventory management."},
    {"name": "fda-medical-device-refurbishment", "description": "Navigate FDA regulations for medical device refurbishment including 21 CFR requirements, refurbisher responsibilities, and labeling compliance."},
    {"name": "medical-equipment-trade-in-programs", "description": "Develop medical equipment trade-in programs including valuation methods, logistics coordination, and upgrade pathway management."},
    {"name": "surgical-equipment-refurbishment", "description": "Manage surgical equipment refurbishment including laparoscopic instruments, surgical tables, electrosurgical units, and anesthesia machines."},
    {"name": "dental-equipment-refurbishment", "description": "Operate dental equipment refurbishment including chairs, delivery units, compressors, imaging systems, and sterilization equipment."},
]

# Domain: Tool and Die Shops
skills += [
    {"name": "tool-die-shop-management", "description": "Manage tool and die shop operations including quoting, scheduling, toolmaker management, equipment utilization, and customer delivery."},
    {"name": "injection-mold-tooling-ops", "description": "Operate injection mold tooling operations including design review, tool build, sampling, validation, and ongoing tool maintenance programs."},
    {"name": "stamping-die-build-ops", "description": "Manage stamping die build operations including tryout press scheduling, die spotting, first article approval, and production handoff."},
    {"name": "tool-repair-reconditioning-ops", "description": "Operate tool repair and reconditioning services including damage assessment, component replacement, re-polishing, and performance validation."},
    {"name": "tooling-cost-estimating", "description": "Develop tooling cost estimates including design complexity analysis, machining hours, material costs, and lead time commitment."},
    {"name": "mold-flow-analysis-services", "description": "Provide mold flow analysis services including fill simulation, cooling optimization, warp analysis, and design recommendation reporting."},
    {"name": "progressive-die-build-management", "description": "Manage progressive die build operations including station design review, subcomponent sourcing, assembly, tryout, and customer acceptance."},
    {"name": "tooling-asset-management", "description": "Manage tooling assets including ownership tracking, PM programs, storage, shipping coordination, and end-of-life disposition."},
    {"name": "hot-runner-system-services", "description": "Manage hot runner system services including selection, installation, commissioning, maintenance, and troubleshooting for injection molding operations."},
    {"name": "tool-die-workforce-management", "description": "Manage tool and die workforce including apprenticeship programs, journeyman certification, skills assessment, and recruitment programs."},
]

# Domain: Agricultural Chemical Application Services
skills += [
    {"name": "custom-chemical-applicator-ops", "description": "Manage custom chemical application operations including sprayer fleet management, application records, drift management, and regulatory compliance."},
    {"name": "aerial-application-services", "description": "Operate aerial application services including aircraft scheduling, pilot certification, product mixing, wind monitoring, and buffer zone compliance."},
    {"name": "crop-protection-application-mgmt", "description": "Manage crop protection application programs including herbicide, fungicide, and insecticide application timing, rate management, and efficacy tracking."},
    {"name": "custom-fertilizer-application", "description": "Operate custom fertilizer application services including prescription mapping, variable rate equipment, application verification, and nutrient records."},
    {"name": "application-equipment-maintenance", "description": "Maintain application equipment including sprayer calibration, nozzle management, GPS guidance maintenance, and chemical system maintenance."},
    {"name": "ag-application-compliance-mgmt", "description": "Manage agricultural application regulatory compliance including pesticide licensing, worker protection standards, water quality buffers, and reporting."},
    {"name": "soil-sampling-application-services", "description": "Provide soil sampling and application services including grid sampling, zone management, laboratory coordination, and prescription development."},
    {"name": "biostimulant-application-programs", "description": "Manage biostimulant and biological application programs including timing recommendations, tank mix compatibility, and efficacy monitoring."},
    {"name": "ag-application-data-management", "description": "Manage agricultural application data including as-applied records, GPS logging, compliance reporting, and data sharing with farm management systems."},
    {"name": "custom-application-customer-service", "description": "Manage custom application customer service including scheduling, communication, billing, and agronomic consultation services."},
]

# Domain: Used Restaurant Equipment
skills += [
    {"name": "used-restaurant-equipment-dealer", "description": "Operate used restaurant equipment dealerships including equipment acquisition, inspection, cleaning, pricing, and B2B and online sales."},
    {"name": "restaurant-equipment-auction-ops", "description": "Manage restaurant equipment auction operations including liquidation services, online auctions, bidder management, and settlement processing."},
    {"name": "commercial-kitchen-refurbishment", "description": "Refurbish commercial kitchen equipment including fryers, ranges, dishwashers, refrigeration, and exhaust hoods for resale."},
    {"name": "restaurant-liquidation-services", "description": "Provide restaurant liquidation services including buyouts, on-site sales, consignment programs, and estate settlement coordination."},
    {"name": "food-equipment-parts-sales", "description": "Manage food service equipment parts sales including OEM and compatible parts, parts kits, and tech support for foodservice operators."},
    {"name": "food-equipment-reconditioning", "description": "Operate food equipment reconditioning including cleaning, lubrication, calibration, and cosmetic restoration for resale-ready equipment."},
    {"name": "used-refrigeration-equipment-sales", "description": "Manage used commercial refrigeration sales including walk-in coolers, reach-in refrigerators, ice machines, and display cases."},
    {"name": "restaurant-equipment-export-ops", "description": "Operate restaurant equipment export operations including international buyer sourcing, container loading, export documentation, and compliance."},
    {"name": "ghost-kitchen-equipment-programs", "description": "Develop ghost kitchen equipment programs including modular packages, lease options, turnkey buildouts, and trade-in programs."},
    {"name": "food-truck-equipment-sales", "description": "Manage food truck equipment sales including vehicle-specific configurations, NSF-compliant builds, generator systems, and custom fabrication."},
]

# Domain: Portable Sanitation Services
skills += [
    {"name": "portable-restroom-rental-ops", "description": "Operate portable restroom rental operations including unit routing, cleaning schedules, delivery logistics, and event service management."},
    {"name": "portable-sanitation-fleet-mgmt", "description": "Manage portable sanitation fleet including unit inventory, maintenance scheduling, refurbishment programs, and utilization optimization."},
    {"name": "porta-potty-route-management", "description": "Manage portable restroom service routes including pump truck scheduling, driver management, GPS optimization, and customer communication."},
    {"name": "luxury-restroom-trailer-rental", "description": "Operate luxury restroom trailer rental services including event coordination, setup services, attendant programs, and climate control management."},
    {"name": "portable-sanitation-event-services", "description": "Provide portable sanitation event services including capacity planning, VIP units, ADA compliance, waste collection, and event support."},
    {"name": "construction-sanitation-services", "description": "Manage construction site sanitation services including jobsite placement, OSHA compliance, frequency planning, and contractor account management."},
    {"name": "portable-sanitation-waste-disposal", "description": "Manage portable sanitation waste disposal including pump-out operations, wastewater treatment facility relationships, and disposal compliance."},
    {"name": "handwashing-station-rental", "description": "Manage handwashing and hand sanitizer station rental programs including food event compliance, healthcare site sanitation, and school service."},
    {"name": "portable-sanitation-national-accounts", "description": "Develop portable sanitation national account programs including multi-site pricing, service level agreements, and centralized billing."},
    {"name": "portable-sanitation-sales-ops", "description": "Manage portable sanitation sales operations including quoting, territory management, seasonal pricing, and customer relationship management."},
]

# Domain: Industrial Laundry and Garment Services
skills += [
    {"name": "industrial-laundry-route-management", "description": "Manage industrial laundry service routes including garment pickup and delivery, route optimization, driver management, and customer satisfaction."},
    {"name": "cleanroom-garment-laundry-ops", "description": "Operate cleanroom garment laundering services including ISO classification compliance, particle count testing, and garment tracking systems."},
    {"name": "workwear-rental-program-mgmt", "description": "Manage workwear rental programs including garment selection, employee fitting, garment replacement cycles, and customer account management."},
    {"name": "laundry-plant-operations", "description": "Operate industrial laundry plant operations including tunnel washer management, dryer optimization, repair shop, and production scheduling."},
    {"name": "garment-program-compliance", "description": "Manage garment program compliance including OSHA flame-resistant standards, hi-vis requirements, garment inspection, and replacement protocols."},
    {"name": "linen-service-operations", "description": "Operate commercial linen services including hotel, restaurant, and healthcare linen programs, delivery logistics, and quality management."},
    {"name": "garment-tracking-rfid-ops", "description": "Manage garment tracking systems including RFID tagging, inventory accuracy, customer reporting, lost garment management, and barcode integration."},
    {"name": "laundry-chemical-management-ops", "description": "Manage laundry chemical programs including dosing systems, product selection, water quality management, and cost optimization."},
    {"name": "industrial-laundry-equipment-maint", "description": "Maintain industrial laundry equipment including preventive maintenance, parts management, emergency repair coordination, and equipment lifecycle management."},
    {"name": "direct-purchase-garment-programs", "description": "Manage direct purchase garment programs including apparel sourcing, company store platforms, embellishment coordination, and managed replenishment."},
]

# Domain: Commercial Food Waste Management
skills += [
    {"name": "food-waste-hauling-operations", "description": "Operate commercial food waste hauling services including scheduled collection, container management, routing, and diversion reporting."},
    {"name": "food-waste-composting-programs", "description": "Manage commercial food waste composting programs including collection setup, processor partnerships, diversion verification, and sustainability reporting."},
    {"name": "food-waste-anaerobic-digestion", "description": "Manage food waste anaerobic digestion programs including feedstock sourcing, preprocessing, digester operations, and biogas utilization."},
    {"name": "food-waste-reduction-consulting", "description": "Provide food waste reduction consulting including waste audits, menu engineering guidance, portion optimization, and staff training programs."},
    {"name": "restaurant-grease-trap-services", "description": "Manage restaurant grease trap services including cleaning frequency, waste disposal compliance, FOG ordinance management, and pump-out records."},
    {"name": "food-rescue-program-management", "description": "Manage food rescue programs including donor relationships, volunteer coordination, recipient organizations, and pound-rescued tracking."},
    {"name": "organic-waste-diversion-programs", "description": "Develop organic waste diversion programs for municipalities including commercial generator requirements, hauler programs, and educational outreach."},
    {"name": "food-waste-technology-platform", "description": "Operate food waste technology platforms including smart bin sensors, AI-powered waste tracking, sustainability dashboards, and carbon reporting."},
    {"name": "institutional-food-waste-mgmt", "description": "Manage institutional food waste for schools and hospitals including pre-consumer waste reduction, tray-less programs, and composting contracts."},
    {"name": "grocery-store-food-waste-ops", "description": "Manage grocery store food waste operations including produce waste, bakery surplus, deli waste, donation programs, and diversion metrics."},
]

# Domain: Concrete and Masonry Contracting
skills += [
    {"name": "concrete-contractor-ops", "description": "Manage concrete contractor operations including residential flatwork, commercial slabs, decorative concrete, forming, and finishing crews."},
    {"name": "masonry-contractor-operations", "description": "Operate masonry contractor businesses including brick, block, stone, and tuck-pointing for residential and commercial construction projects."},
    {"name": "concrete-pumping-services", "description": "Manage concrete pumping services including pump selection, boom placement coordination, line cleaning, and hazardous lift planning."},
    {"name": "decorative-concrete-services", "description": "Manage decorative concrete services including stamped concrete, exposed aggregate, staining, polishing, overlays, and epoxy floor systems."},
    {"name": "concrete-cutting-breaking-ops", "description": "Operate concrete cutting and breaking services including diamond saw cutting, core drilling, demolition jackhammers, and GPR scanning."},
    {"name": "masonry-restoration-services", "description": "Provide masonry restoration services including tuck-pointing, brick replacement, waterproofing, stone cleaning, and historic preservation."},
    {"name": "concrete-testing-quality-assurance", "description": "Manage concrete testing and quality assurance including cylinder sampling, slump testing, air content, ACI certification, and mix design compliance."},
    {"name": "concrete-repair-rehabilitation", "description": "Manage concrete repair and rehabilitation services including structural repair, spall repair, joint sealing, carbon fiber reinforcement, and waterproofing."},
    {"name": "precast-concrete-erection", "description": "Manage precast concrete erection services including crane coordination, connection installation, grouting, and tolerancing management."},
    {"name": "concrete-masonry-estimating", "description": "Develop concrete and masonry estimates including material takeoffs, forming labor, equipment costs, and subcontract pricing."},
]

# Domain: Roofing Contracting Services
skills += [
    {"name": "residential-roofing-contractor-ops", "description": "Manage residential roofing contractor operations including shingle installation, insurance claims, sales management, and crew scheduling."},
    {"name": "commercial-roofing-contractor-ops", "description": "Operate commercial roofing contractor businesses including TPO, EPDM, modified bitumen, metal roofing, and rooftop equipment coordination."},
    {"name": "roofing-insurance-claim-management", "description": "Manage roofing insurance claim services including storm damage assessment, adjuster coordination, supplementing, and documentation."},
    {"name": "roofing-sales-program-management", "description": "Develop roofing sales programs including canvassing, storm chasing strategy, referral programs, financing options, and CRM management."},
    {"name": "roofing-materials-procurement", "description": "Manage roofing materials procurement including manufacturer relationships, distributor programs, material scheduling, and delivery logistics."},
    {"name": "low-slope-roofing-systems", "description": "Manage low-slope roofing systems including membrane selection, installation standards, drainage design, and warranty program compliance."},
    {"name": "metal-roofing-installation-ops", "description": "Operate metal roofing installation services including standing seam, metal tile, retrofit systems, and manufacturer certification programs."},
    {"name": "roofing-safety-program-management", "description": "Manage roofing safety programs including fall protection plans, OSHA compliance, heat illness prevention, and contractor safety requirements."},
    {"name": "roof-maintenance-programs", "description": "Develop commercial roof maintenance programs including inspection scheduling, repair prioritization, coating applications, and extended warranty programs."},
    {"name": "solar-roofing-coordination", "description": "Coordinate solar and roofing integration including penetration details, structural loading, flashing systems, and multi-trade scheduling."},
]

# Domain: Pest Control and Extermination Services
skills += [
    {"name": "residential-pest-control-ops", "description": "Operate residential pest control operations including general pest, rodent control, termite treatment, bed bugs, and recurring service programs."},
    {"name": "commercial-pest-management-ops", "description": "Manage commercial pest management programs including food facility compliance, restaurant inspections, healthcare facility protocols, and school programs."},
    {"name": "pest-control-route-management", "description": "Manage pest control service routes including technician scheduling, route optimization, service documentation, and customer communication."},
    {"name": "termite-treatment-programs", "description": "Manage termite treatment and control programs including liquid barrier treatment, baiting systems, wood-destroying organism inspections, and warranties."},
    {"name": "pest-control-wildlife-management", "description": "Manage integrated wildlife management services including nuisance wildlife exclusion, removal, habitat modification, and damage mitigation."},
    {"name": "pest-control-chemical-compliance", "description": "Manage pest control chemical compliance including pesticide licensing, restricted-use documentation, application records, and disposal requirements."},
    {"name": "bed-bug-treatment-operations", "description": "Manage bed bug treatment operations including heat treatment, chemical treatment, monitoring, follow-up protocols, and resident communication."},
    {"name": "pest-control-ipm-programs", "description": "Develop integrated pest management programs including inspection-based treatments, threshold monitoring, sanitation recommendations, and documentation."},
    {"name": "fumigation-service-management", "description": "Manage structural fumigation services including regulatory permits, tenting operations, clearance testing, and customer communication protocols."},
    {"name": "pest-control-franchise-operations", "description": "Manage pest control franchise operations including territory management, quality standards, brand compliance, and franchisee support programs."},
]

# Domain: Flooring Installation Services
skills += [
    {"name": "flooring-installation-contractor-ops", "description": "Manage flooring installation contractor operations including residential and commercial carpet, LVP, hardwood, tile, and crew scheduling."},
    {"name": "commercial-flooring-project-mgmt", "description": "Manage commercial flooring projects including scope development, installer coordination, phasing, punch list, and warranty documentation."},
    {"name": "flooring-estimating-ops", "description": "Develop flooring estimates including material takeoffs, waste factors, labor pricing, substrate preparation, and installation accessories."},
    {"name": "flooring-subcontractor-management", "description": "Manage flooring subcontractor programs including qualification, work authorization, insurance verification, and performance management."},
    {"name": "hardwood-flooring-services", "description": "Manage hardwood flooring installation and refinishing services including sand and finish, glue-down, nail-down, and floating installation methods."},
    {"name": "epoxy-floor-coating-services", "description": "Operate epoxy and floor coating services including surface preparation, coating application, decorative systems, and commercial floor maintenance programs."},
    {"name": "carpet-installation-services", "description": "Manage carpet installation services including commercial broadloom, carpet tile, tackless installation, seam planning, and warranty management."},
    {"name": "tile-installation-services", "description": "Manage tile installation services including ceramic, porcelain, natural stone, large format tile, and shower system installation."},
    {"name": "flooring-moisture-testing", "description": "Manage flooring moisture testing and mitigation including calcium chloride testing, RH testing, vapor barrier installation, and warranty compliance."},
    {"name": "flooring-retail-installation-channel", "description": "Develop flooring retail installation channels including big box partnerships, flooring dealer programs, online retailer integration, and installer networks."},
]

# Domain: Fire and Water Damage Restoration
skills += [
    {"name": "fire-damage-restoration-ops", "description": "Manage fire damage restoration operations including emergency board-up, smoke odor removal, structural drying, contents cleaning, and reconstruction."},
    {"name": "water-damage-mitigation-ops", "description": "Operate water damage mitigation services including extraction, structural drying, moisture monitoring, mold prevention, and insurance documentation."},
    {"name": "restoration-insurance-coordination", "description": "Manage restoration insurance coordination including adjuster relationships, Xactimate estimating, supplement negotiation, and claims management."},
    {"name": "contents-restoration-services", "description": "Manage contents restoration services including pack-out, inventory, cleaning, deodorizing, storage, and pack-back coordination."},
    {"name": "mold-remediation-operations", "description": "Operate mold remediation services including assessment, containment, removal, antimicrobial treatment, clearance testing, and post-remediation verification."},
    {"name": "catastrophe-response-operations", "description": "Manage catastrophe response operations including large loss teams, equipment deployment, subcontractor networks, and client communication."},
    {"name": "restoration-business-development", "description": "Develop restoration business through insurance agent relationships, plumber and roofer referrals, property manager programs, and digital marketing."},
    {"name": "document-drying-restoration", "description": "Manage document and record drying and restoration services including vacuum freeze-drying, emergency stabilization, and archive recovery."},
    {"name": "restoration-franchise-operations", "description": "Manage restoration franchise operations including territory management, certification requirements, marketing programs, and quality standards."},
    {"name": "biohazard-crime-scene-cleanup", "description": "Manage biohazard and crime scene cleanup operations including personal protective equipment, regulated waste disposal, and decontamination protocols."},
]

# Domain: Elevator and Escalator Services
skills += [
    {"name": "elevator-service-contractor-ops", "description": "Manage elevator service contractor operations including maintenance contracts, modernization projects, and new installation project management."},
    {"name": "elevator-maintenance-scheduling", "description": "Schedule elevator and escalator maintenance including compliance inspections, PM frequency, customer notification, and violation response."},
    {"name": "elevator-modernization-project-mgmt", "description": "Manage elevator modernization projects including controls upgrades, cab refurbishment, door operator replacement, and ADA compliance upgrades."},
    {"name": "elevator-new-installation-ops", "description": "Manage elevator new installation operations including pit preparation, machine room design, inspection coordination, and certificate of occupancy."},
    {"name": "elevator-parts-supply-chain", "description": "Manage elevator parts supply chain including OEM and compatible parts procurement, inventory management, and emergency parts availability."},
    {"name": "escalator-maintenance-programs", "description": "Develop escalator maintenance programs including daily inspections, combplate management, handrail inspections, and deep cleaning services."},
    {"name": "vertical-transportation-consulting", "description": "Provide vertical transportation consulting including traffic analysis, equipment selection, code compliance review, and specification development."},
    {"name": "elevator-safety-compliance", "description": "Manage elevator safety compliance including ASME A17.1 compliance, state inspection programs, violation resolution, and safety device testing."},
    {"name": "platform-lift-management-ops", "description": "Manage platform lift and accessibility lift services including residential lifts, commercial platforms, wheelchair lifts, and LULA elevator service."},
    {"name": "elevator-remote-monitoring", "description": "Deploy elevator remote monitoring systems including IoT sensors, predictive maintenance analytics, entrapment notification, and performance reporting."},
]

# Domain: Landscaping and Lawn Care Services
skills += [
    {"name": "commercial-landscaping-ops", "description": "Manage commercial landscaping operations including maintenance contracts, enhancement programs, irrigation management, and seasonal programs."},
    {"name": "residential-lawn-care-ops", "description": "Operate residential lawn care services including mowing routes, fertilization programs, weed control, aeration, overseeding, and customer communication."},
    {"name": "landscape-installation-services", "description": "Manage landscape installation services including planting design, hardscape construction, irrigation installation, and project delivery."},
    {"name": "tree-care-arborist-services", "description": "Provide tree care and arborist services including pruning, removal, cabling, plant health care, and ISA certified arborist programs."},
    {"name": "irrigation-installation-services", "description": "Manage irrigation installation and service including system design, installation, backflow preventer testing, and smart controller programming."},
    {"name": "snow-and-ice-management-ops", "description": "Operate snow and ice management services including plowing, salting, anti-icing, slip and fall liability management, and weather monitoring."},
    {"name": "lawn-care-chemical-applications", "description": "Manage lawn care chemical application programs including fertilization, pesticide licensing, application records, and environmental compliance."},
    {"name": "landscape-maintenance-contracts", "description": "Develop landscape maintenance contracts including scope definition, seasonal pricing, enhancement budgets, and service level agreements."},
    {"name": "outdoor-living-installation", "description": "Manage outdoor living installation services including patios, fire features, outdoor kitchens, pergolas, and lighting systems."},
    {"name": "landscape-business-development", "description": "Develop landscaping business through commercial property manager relationships, HOA programs, referral networks, and digital marketing."},
]

# Domain: Pool and Spa Service Industry
skills += [
    {"name": "pool-service-route-management", "description": "Manage pool service routes including weekly maintenance scheduling, chemical management, equipment checks, and customer communication."},
    {"name": "pool-repair-service-ops", "description": "Operate pool repair services including equipment replacement, plumbing repairs, leak detection, liner replacement, and resurfacing."},
    {"name": "commercial-pool-service-ops", "description": "Manage commercial pool and aquatics facility maintenance including health department compliance, operator certification, and daily chemical testing."},
    {"name": "pool-construction-project-mgmt", "description": "Manage pool and spa construction projects including design coordination, permitting, subcontractor management, and owner acceptance."},
    {"name": "pool-chemical-distribution-ops", "description": "Operate pool chemical distribution including retail and professional channels, seasonal inventory management, and MSDS compliance."},
    {"name": "pool-equipment-sales-service", "description": "Manage pool equipment sales and service including pumps, filters, heaters, automation, cleaners, and warranty programs."},
    {"name": "hot-tub-spa-service-ops", "description": "Operate hot tub and spa service operations including delivery, setup, maintenance, repair, and retail accessory sales."},
    {"name": "pool-renovation-services", "description": "Manage pool renovation services including replastering, tile replacement, deck resurfacing, coping replacement, and equipment upgrades."},
    {"name": "pool-water-testing-programs", "description": "Manage pool water testing programs including in-store water analysis, mobile testing, chemical recommendations, and educational programs."},
    {"name": "pool-service-franchise-ops", "description": "Manage pool service franchise operations including territory development, quality standards, chemical programs, and training systems."},
]

# Domain: Moving and Relocation Services
skills += [
    {"name": "residential-moving-company-ops", "description": "Manage residential moving company operations including estimate processes, crew scheduling, truck management, packing services, and claims handling."},
    {"name": "commercial-moving-services", "description": "Operate commercial moving services including office relocation, modular furniture installation, IT equipment moves, and after-hours operations."},
    {"name": "long-distance-moving-ops", "description": "Manage long-distance moving operations including interstate authority, tariff management, agent networks, and household goods claims."},
    {"name": "specialty-moving-services", "description": "Provide specialty moving services including piano moving, art and antique handling, laboratory equipment, server room relocation, and vault moves."},
    {"name": "corporate-relocation-programs", "description": "Manage corporate relocation programs including policy administration, vendor management, lump sum programs, and relocation management company partnerships."},
    {"name": "moving-storage-operations", "description": "Manage moving and storage operations including warehouse inventory management, access scheduling, climate control, and monthly billing."},
    {"name": "moving-company-claims-management", "description": "Manage moving company claims programs including damage assessment, repair coordination, settlement processing, and customer resolution."},
    {"name": "moving-business-development", "description": "Develop moving company business through real estate agent partnerships, corporate accounts, referral programs, and digital marketing."},
    {"name": "international-moving-services", "description": "Manage international moving services including customs documentation, container booking, origin and destination agent coordination, and duty management."},
    {"name": "college-dormitory-moving-programs", "description": "Develop college and dormitory moving programs including seasonal capacity planning, student pricing, storage partnerships, and campus relationships."},
]

# Domain: Specialty Coatings Application Services
skills += [
    {"name": "industrial-painting-contractor-ops", "description": "Manage industrial painting contractor operations including surface prep, coating application, scaffold coordination, and safety compliance."},
    {"name": "powder-coating-shop-ops", "description": "Operate powder coating shop operations including pretreatment, application, oven scheduling, color management, and quality inspection."},
    {"name": "protective-coating-application", "description": "Apply protective coating systems including epoxy, polyurethane, zinc-rich primers, coatings for immersion service, and abrasion-resistant systems."},
    {"name": "bridge-coating-services", "description": "Manage bridge coating services including lead paint abatement, containment, surface preparation, coating systems, and environmental compliance."},
    {"name": "tank-coating-application-services", "description": "Manage tank lining and coating services including surface preparation, lining materials, application, inspection, and holiday testing."},
    {"name": "floor-coating-industrial-services", "description": "Apply industrial floor coating systems including epoxy, urethane, polyaspartic, broadcast systems, and chemical-resistant systems."},
    {"name": "thermal-spray-coating-services", "description": "Manage thermal spray coating services including arc spray, flame spray, HVOF, and plasma spray for wear and corrosion protection."},
    {"name": "coatings-inspection-management", "description": "Manage coatings inspection services including NACE certified inspectors, mil gauge readings, adhesion testing, and inspection documentation."},
    {"name": "marine-coating-application-ops", "description": "Manage marine coating application services including hull antifouling, topside finishes, tank coatings, and offshore structure maintenance."},
    {"name": "coating-contractor-safety-programs", "description": "Implement coating contractor safety programs including respiratory protection, confined space, hot work permits, and lead and silica exposure programs."},
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
