import os

base = r"c:\Users\mirza\MAARS-Command\.claude\skills"

# Domain: Print & Publishing
skills = [
    {"name": "print-production-management", "description": "Manage commercial print production workflows including prepress, press, bindery, and fulfillment operations."},
    {"name": "publishing-editorial-workflow", "description": "Coordinate editorial and publishing workflows including manuscript management, copyediting, design, and print-digital release."},
    {"name": "print-procurement-sourcing", "description": "Source and procure print production services including vendor qualification, RFQ management, and print buyer operations."},
    {"name": "magazine-periodical-ops", "description": "Manage magazine and periodical publishing operations including subscription fulfillment, advertising sales, and issue planning."},
    {"name": "book-publishing-operations", "description": "Operate book publishing programs including title acquisition, production scheduling, distribution, and royalty management."},
    {"name": "print-quality-management", "description": "Implement print quality management programs including color management, proof approval, press standards, and defect tracking."},
    {"name": "wide-format-print-ops", "description": "Manage wide-format printing operations including large banner production, signage fulfillment, and installation coordination."},
    {"name": "digital-print-production", "description": "Operate digital print production lines including variable data printing, on-demand fulfillment, and substrate management."},
    {"name": "publication-distribution-mgmt", "description": "Manage publication distribution networks including newsstand allocation, subscription logistics, and returns processing."},
    {"name": "print-media-planning", "description": "Execute print media planning and buying including publication selection, insertion order management, and circulation analysis."},
]

# Domain: Glass Manufacturing
skills += [
    {"name": "flat-glass-production", "description": "Manage flat glass manufacturing operations including float line operations, cutting optimization, and quality inspection."},
    {"name": "glass-tempering-laminating", "description": "Operate glass tempering and laminating production lines including furnace management, safety glass certification, and order fulfillment."},
    {"name": "glass-forming-operations", "description": "Manage glass forming operations including mold design, gob weight control, and annealing lehr management."},
    {"name": "glass-coating-operations", "description": "Operate glass coating lines including CVD and PVD coating processes, optical property verification, and substrate handling."},
    {"name": "glass-fiber-manufacturing", "description": "Manage glass fiber production including bushing operations, sizing application, forming package management, and tensile testing."},
    {"name": "specialty-glass-development", "description": "Develop specialty glass products including borosilicate, aluminosilicate, and optical glass formulations with property verification."},
    {"name": "glass-recycling-cullet-mgmt", "description": "Manage glass recycling and cullet programs including collection logistics, contamination sorting, and furnace feed integration."},
    {"name": "architectural-glass-sales", "description": "Manage architectural glass sales and project coordination including specification work, fabricator networks, and glazing contractor support."},
    {"name": "glass-defect-analysis", "description": "Analyze glass defects using microscopy, chemistry, and process correlation to drive yield improvement programs."},
    {"name": "glass-furnace-management", "description": "Operate glass melting furnaces including refractory management, energy optimization, batch chemistry, and rebuild planning."},
]

# Domain: Ceramics Production
skills += [
    {"name": "technical-ceramics-manufacturing", "description": "Manufacture technical ceramic components including powder processing, forming, sintering, and dimensional finishing operations."},
    {"name": "ceramic-tile-production", "description": "Manage ceramic tile manufacturing including body formulation, pressing, glazing, kiln firing, and surface quality inspection."},
    {"name": "sanitaryware-production", "description": "Operate sanitaryware production lines including slip casting, drying, glaze application, kiln loading, and defect sorting."},
    {"name": "refractories-production", "description": "Manage refractory product manufacturing including shaped and unshaped refractory production, testing, and high-temperature application support."},
    {"name": "ceramic-glaze-development", "description": "Develop ceramic glaze formulations including colorant chemistry, flow testing, kiln atmosphere optimization, and production scale-up."},
    {"name": "ceramic-raw-material-mgmt", "description": "Manage ceramic raw material procurement including clay, feldspar, silica, and alumina sourcing with quality verification."},
    {"name": "kiln-operations-management", "description": "Operate industrial ceramic kilns including firing curve programming, atmosphere control, energy management, and maintenance scheduling."},
    {"name": "ceramic-quality-control", "description": "Execute ceramic quality control programs including physical testing, dimensional inspection, thermal analysis, and customer complaint resolution."},
    {"name": "advanced-ceramics-rd", "description": "Conduct advanced ceramics research and development including ZrO2, Si3N4, SiC, and AlN material systems for high-performance applications."},
    {"name": "ceramic-packaging-logistics", "description": "Manage ceramic product packaging and logistics including fragile goods handling, custom crating, and international export documentation."},
]

# Domain: Textile Manufacturing
skills += [
    {"name": "yarn-spinning-operations", "description": "Manage yarn spinning operations including fiber preparation, ring spinning, open-end spinning, and yarn quality monitoring."},
    {"name": "weaving-operations-management", "description": "Operate weaving mills including loom scheduling, warp preparation, fabric construction design, and loom efficiency optimization."},
    {"name": "knitting-operations-management", "description": "Manage knitting operations including circular and flat knitting machine scheduling, yarn feed management, and fabric inspection."},
    {"name": "textile-dyeing-finishing", "description": "Operate textile dyeing and finishing operations including dye lot management, recipe optimization, and fastness testing."},
    {"name": "textile-quality-assurance", "description": "Implement textile quality assurance programs including fabric testing, pilling resistance, tensile strength, and colorfastness standards."},
    {"name": "textile-product-development", "description": "Develop new textile products from concept through commercialization including fiber selection, construction engineering, and performance validation."},
    {"name": "textile-supply-chain-mgmt", "description": "Manage textile supply chains from fiber sourcing through fabric delivery including lead time management and supplier certification."},
    {"name": "apparel-cut-sew-operations", "description": "Manage apparel cut and sew operations including pattern grading, marker making, cutting room, and assembly line balancing."},
    {"name": "textile-sustainability-programs", "description": "Implement textile sustainability programs including recycled fiber sourcing, waterless dyeing, and bluesign or OEKO-TEX certification."},
    {"name": "fabric-sales-merchandising", "description": "Manage fabric sales and merchandising operations including sample room, colorway management, mill direct sales, and converter relationships."},
]

# Domain: Leather Goods Manufacturing
skills += [
    {"name": "leather-tanning-operations", "description": "Manage leather tanning operations including beamhouse processes, tanning chemistry, retanning, and finishing line management."},
    {"name": "leather-goods-production", "description": "Operate leather goods manufacturing including pattern cutting, stitching, assembly, hardware setting, and quality finishing."},
    {"name": "leather-sourcing-grading", "description": "Source and grade raw hides and skins including supplier qualification, hide grading standards, and traceability program management."},
    {"name": "leather-product-development", "description": "Develop leather product lines including design collaboration, prototype sampling, material testing, and production handover."},
    {"name": "leather-quality-management", "description": "Manage leather quality programs including pull strength, color fastness, grain adhesion, and finished goods inspection."},
    {"name": "exotic-leather-compliance", "description": "Navigate exotic leather compliance programs including CITES permitting, import documentation, species verification, and customs coordination."},
    {"name": "leather-accessories-brand-ops", "description": "Operate leather accessories brand programs including collection planning, luxury positioning, wholesale distribution, and DTC e-commerce."},
    {"name": "leather-repair-restoration", "description": "Manage leather repair and restoration service operations including assessment, cleaning, conditioning, dyeing, and structural repair."},
    {"name": "vegan-leather-alternatives", "description": "Develop and commercialize vegan leather alternative programs including bio-based materials, PU alternatives, and sustainability certification."},
    {"name": "leather-goods-logistics", "description": "Manage leather goods logistics including duty drawback, customs classification, bonded warehouse, and DDP delivery program management."},
]

# Domain: Rubber Manufacturing
skills += [
    {"name": "rubber-compounding-ops", "description": "Manage rubber compounding operations including Banbury mixing, compound development, cure system optimization, and batch traceability."},
    {"name": "rubber-molding-operations", "description": "Operate rubber molding processes including compression, transfer, and injection molding with cure cycle optimization and flash management."},
    {"name": "tire-manufacturing-ops", "description": "Manage tire manufacturing operations including component building, curing, uniformity testing, and final inspection."},
    {"name": "hose-belt-manufacturing", "description": "Manufacture industrial hose and belting products including mandrel building, vulcanization, testing, and pressure certification."},
    {"name": "rubber-raw-material-sourcing", "description": "Source rubber raw materials including natural rubber procurement, synthetic rubber specification, carbon black sourcing, and price hedging."},
    {"name": "rubber-quality-testing", "description": "Execute rubber quality testing programs including hardness, tensile, elongation, compression set, and aging test protocols."},
    {"name": "rubber-product-development", "description": "Develop rubber products from compound formulation through prototype testing, validation, and production launch."},
    {"name": "rubber-recycling-devulcanization", "description": "Manage rubber recycling programs including crumb rubber processing, devulcanization trials, and reclaimed rubber integration."},
    {"name": "elastomer-engineering", "description": "Apply elastomer engineering expertise to select and specify silicone, EPDM, NBR, and specialty rubber materials for industrial applications."},
    {"name": "rubber-plant-maintenance", "description": "Maintain rubber manufacturing equipment including press preventive maintenance, mixer rebuilds, and autoclave qualification."},
]

# Domain: Plastics Manufacturing
skills += [
    {"name": "injection-molding-operations", "description": "Manage injection molding operations including mold setup, process optimization, cycle time reduction, and dimensional quality control."},
    {"name": "extrusion-manufacturing-ops", "description": "Operate plastic extrusion lines including die management, profile tooling, haul-off calibration, and output quality monitoring."},
    {"name": "blow-molding-operations", "description": "Manage blow molding production including HDPE container manufacturing, parison control, and wall thickness optimization."},
    {"name": "thermoforming-operations", "description": "Operate thermoforming lines including sheet forming, trim tooling, stacking automation, and packaging line integration."},
    {"name": "plastic-compounding-ops", "description": "Manage plastic compounding operations including twin-screw extruder operation, additive incorporation, and pellet quality testing."},
    {"name": "plastic-raw-material-mgmt", "description": "Manage plastic resin procurement including commodity and specialty polymer sourcing, supplier qualification, and inventory management."},
    {"name": "plastic-quality-assurance", "description": "Implement plastic quality assurance programs including ASTM testing, dimensional gauging, color matching, and defect classification."},
    {"name": "plastic-tooling-management", "description": "Manage plastic tooling programs including mold design review, toolmaker coordination, qualification, and maintenance scheduling."},
    {"name": "plastic-sustainability-ops", "description": "Lead plastic sustainability programs including PCR content integration, recyclability design, bio-based resin trials, and EPR compliance."},
    {"name": "plastic-product-development", "description": "Develop plastic products from design concepts through material selection, prototyping, and production readiness validation."},
]

# Domain: Paint & Coatings Manufacturing
skills += [
    {"name": "paint-formulation-development", "description": "Develop paint and coating formulations including binder selection, pigment grinding, additive optimization, and performance testing."},
    {"name": "coatings-manufacturing-ops", "description": "Manage coatings manufacturing operations including batch production, dispersion equipment, filling lines, and GMP compliance."},
    {"name": "architectural-coatings-sales", "description": "Manage architectural coatings sales programs including contractor channel, retail sell-through, color marketing, and technical service."},
    {"name": "industrial-coatings-technical", "description": "Provide industrial coatings technical service including specification development, application training, inspection support, and warranty management."},
    {"name": "coatings-raw-material-sourcing", "description": "Source coatings raw materials including TiO2, resins, solvents, and additives with price management and supplier qualification."},
    {"name": "coatings-quality-control", "description": "Execute coatings quality control programs including viscosity, hiding power, adhesion, gloss, and chemical resistance testing."},
    {"name": "powder-coatings-operations", "description": "Manage powder coatings manufacturing and application operations including resin grinding, fluidized bed, and electrostatic spray systems."},
    {"name": "coatings-regulatory-compliance", "description": "Navigate coatings regulatory compliance including VOC limits, HAP content, SDS management, and EPA architectural rule compliance."},
    {"name": "coatings-color-management", "description": "Operate coatings color management programs including spectrophotometer standards, custom tinting systems, and color matching services."},
    {"name": "marine-protective-coatings", "description": "Manage marine and protective coatings programs including surface preparation specifications, application guidelines, and warranty inspection."},
]

# Domain: Adhesives & Sealants Manufacturing
skills += [
    {"name": "adhesive-formulation-development", "description": "Develop adhesive formulations including structural, pressure sensitive, hot melt, and UV-cure systems with performance characterization."},
    {"name": "adhesive-manufacturing-ops", "description": "Manage adhesive manufacturing operations including reaction vessel control, extrusion, drum filling, and hazardous material handling."},
    {"name": "adhesive-technical-service", "description": "Provide adhesive technical service to industrial customers including joint design review, substrate compatibility, and failure analysis."},
    {"name": "sealant-product-development", "description": "Develop sealant products including silicone, polyurethane, and polysulfide formulations for construction and industrial applications."},
    {"name": "adhesive-raw-material-mgmt", "description": "Manage adhesive raw material supply including monomer procurement, tackifier sourcing, and supply chain risk mitigation."},
    {"name": "pressure-sensitive-tape-ops", "description": "Operate pressure sensitive tape manufacturing including release liner coating, lamination, slitting, and converting operations."},
    {"name": "adhesive-quality-testing", "description": "Execute adhesive quality testing including peel, shear, tack, and environmental aging tests per ASTM and PSTC standards."},
    {"name": "construction-sealant-sales", "description": "Manage construction sealant sales programs including specification work, distributor management, and contractor pull-through programs."},
    {"name": "adhesive-regulatory-ops", "description": "Navigate adhesive regulatory compliance including food contact clearances, REACH substance registration, and CONEG heavy metal compliance."},
    {"name": "structural-bonding-applications", "description": "Support structural bonding application development including aerospace, automotive, and electronics assembly process qualification."},
]

# Domain: Cleaning Products Manufacturing
skills += [
    {"name": "cleaning-formula-development", "description": "Develop cleaning product formulations including surfactant systems, builders, enzymes, and fragrance integration for household and industrial use."},
    {"name": "cleaning-products-manufacturing", "description": "Manage cleaning product manufacturing operations including liquid blending, powder dry mix, aerosol filling, and packaging operations."},
    {"name": "cleaning-products-regulatory", "description": "Navigate cleaning product regulatory compliance including EPA DfE, FIFRA registration, SDS compliance, and EU biocide regulation."},
    {"name": "cleaning-raw-material-sourcing", "description": "Source cleaning product raw materials including surfactants, solvents, chelants, and enzymes with supply security and cost management."},
    {"name": "institutional-cleaning-sales", "description": "Manage institutional and industrial cleaning sales including jan-san distributor programs, GPO contracts, and technical demonstrations."},
    {"name": "cleaning-products-quality", "description": "Execute cleaning products quality programs including pH, viscosity, efficacy testing, packaging integrity, and shelf-life validation."},
    {"name": "disinfectant-sanitizer-ops", "description": "Manage disinfectant and sanitizer product programs including EPA label claims, kill efficacy data, and registration maintenance."},
    {"name": "green-cleaning-certification", "description": "Develop green cleaning product programs including EPA Safer Choice, Green Seal, and EcoLogo certification with formulation compliance."},
    {"name": "cleaning-brand-marketing", "description": "Manage cleaning brand marketing programs including retailer promotion, packaging redesign, consumer education, and competitive positioning."},
    {"name": "cleaning-contract-manufacturing", "description": "Manage cleaning product contract manufacturing including toll blending agreements, quality oversight, and private label operations."},
]

# Domain: Personal Care Products Manufacturing
skills += [
    {"name": "personal-care-formula-development", "description": "Develop personal care product formulations including skin care, hair care, and body care with stability and safety testing."},
    {"name": "personal-care-manufacturing-ops", "description": "Manage personal care manufacturing operations including emulsification, homogenization, filling, labeling, and batch release."},
    {"name": "personal-care-regulatory", "description": "Navigate personal care regulatory compliance including FDA cosmetic registration, EU cosmetic notification, and claim substantiation."},
    {"name": "personal-care-raw-material", "description": "Source personal care raw materials including actives, emollients, polymers, and preservatives with INCI compliance and safety dossiers."},
    {"name": "personal-care-stability-testing", "description": "Manage personal care stability testing programs including accelerated aging, microbial challenge, compatibility, and SPF testing."},
    {"name": "personal-care-brand-ops", "description": "Operate personal care brand programs including portfolio architecture, channel strategy, DTC digital marketing, and influencer programs."},
    {"name": "personal-care-sustainability", "description": "Lead personal care sustainability programs including natural and organic certification, microplastic elimination, and packaging reduction."},
    {"name": "personal-care-quality-systems", "description": "Implement personal care quality systems including GMP compliance, batch record review, consumer complaint handling, and audit readiness."},
    {"name": "personal-care-innovation-pipeline", "description": "Manage personal care innovation pipelines from trend scouting through consumer testing, claims development, and commercial launch."},
    {"name": "salon-professional-channel", "description": "Manage salon and professional channel programs including distributor sales, educator training, and back-bar product management."},
]

# Domain: Cosmetics Manufacturing
skills += [
    {"name": "color-cosmetics-formulation", "description": "Develop color cosmetics formulations including foundations, lipsticks, eyeshadow, and mascara with pigment dispersion and texture optimization."},
    {"name": "cosmetics-manufacturing-ops", "description": "Manage cosmetics manufacturing operations including color grinding, lipstick molding, compaction, and primary packaging filling."},
    {"name": "cosmetics-packaging-development", "description": "Develop cosmetics packaging including primary component design, decoration specifications, and tooling qualification with brand alignment."},
    {"name": "cosmetics-trend-forecasting", "description": "Monitor and translate cosmetics trends into product development briefs including color story development and seasonal collection planning."},
    {"name": "cosmetics-regulatory-affairs", "description": "Manage cosmetics regulatory affairs including CPNP notification, FDA registration, ingredient safety assessments, and label compliance."},
    {"name": "luxury-cosmetics-brand-ops", "description": "Operate luxury cosmetics brand programs including counter management, beauty advisor training, gift-with-purchase promotions, and department store relationships."},
    {"name": "cosmetics-contract-manufacturing", "description": "Manage cosmetics contract manufacturing relationships including specification transfer, quality audits, and co-development programs."},
    {"name": "cosmetics-influencer-marketing", "description": "Execute cosmetics influencer and beauty creator marketing programs including seeding, UGC campaigns, and affiliate program management."},
    {"name": "cosmetics-retail-ops", "description": "Manage cosmetics retail operations including planogram compliance, tester management, gondola resets, and beauty advisor staffing."},
    {"name": "cosmetics-ecommerce-ops", "description": "Operate cosmetics e-commerce programs including shoppable content, virtual try-on, subscription beauty boxes, and returns management."},
]

# Domain: Fragrances Industry
skills += [
    {"name": "fragrance-development-ops", "description": "Manage fragrance development programs including brief interpretation, perfumer briefs, evaluation panels, and consumer testing."},
    {"name": "fragrance-raw-material-mgmt", "description": "Manage fragrance raw material supply including naturals sourcing, aroma chemical procurement, and IFRA compliance verification."},
    {"name": "fine-fragrance-brand-ops", "description": "Operate fine fragrance brand programs including flanker development, retailer distribution, sampling strategy, and counter design."},
    {"name": "fragrance-manufacturing-ops", "description": "Manage fragrance compound manufacturing including blending, dilution, quality testing, and drum/bulk filling operations."},
    {"name": "fragrance-regulatory-compliance", "description": "Navigate fragrance regulatory compliance including IFRA standards, EU labeling, allergen declaration, and California Prop 65 management."},
    {"name": "fragrance-licensing-management", "description": "Manage fragrance license agreements including designer brand royalties, minimum guarantees, territory exclusivity, and renewal negotiations."},
    {"name": "scent-marketing-programs", "description": "Develop scent marketing programs for retail and hospitality environments including signature scent development and diffusion system management."},
    {"name": "fragrance-evaluation-programs", "description": "Run fragrance evaluation programs including panel recruitment, odor profiling, consumer preference testing, and hedonic scoring."},
    {"name": "essential-oil-operations", "description": "Manage essential oil operations including botanical sourcing, steam distillation, GC-MS quality analysis, and aromatherapy application support."},
    {"name": "home-fragrance-product-ops", "description": "Manage home fragrance product lines including candles, reed diffusers, room sprays, and air care with seasonal launch planning."},
]

# Domain: Nutritional Supplements Manufacturing
skills += [
    {"name": "supplement-formula-development", "description": "Develop nutritional supplement formulations including dosage form selection, bioavailability optimization, and stability study design."},
    {"name": "supplement-manufacturing-ops", "description": "Manage dietary supplement manufacturing operations including encapsulation, tableting, blending, and cGMP documentation."},
    {"name": "supplement-regulatory-affairs", "description": "Navigate dietary supplement regulatory compliance including DSHEA, NDI notifications, structure-function claims, and FDA label requirements."},
    {"name": "supplement-raw-material-qual", "description": "Qualify dietary supplement raw materials including identity testing, certificate of analysis review, and heavy metal testing programs."},
    {"name": "supplement-quality-systems", "description": "Implement supplement quality systems including batch records, in-process controls, finished product release, and deviation management."},
    {"name": "supplement-brand-marketing", "description": "Manage nutritional supplement brand programs including clinical study marketing, retailer shelf programs, and DTC subscription sales."},
    {"name": "contract-supplement-manufacturing", "description": "Manage contract supplement manufacturing including toll blending, private label production, and turnkey brand development programs."},
    {"name": "supplement-supply-chain", "description": "Manage supplement supply chains including ingredient sourcing, API procurement, botanical extraction coordination, and inventory management."},
    {"name": "supplement-ecommerce-ops", "description": "Operate supplement e-commerce programs including Amazon seller central management, subscription bundle optimization, and review management."},
    {"name": "supplement-clinical-research", "description": "Manage supplement clinical research programs including IRB coordination, clinical investigator agreements, and health claim substantiation."},
]

# Domain: Pet Food Manufacturing
skills += [
    {"name": "pet-food-formula-development", "description": "Develop pet food formulations including AAFCO nutritional adequacy compliance, palatability optimization, and ingredient deck management."},
    {"name": "pet-food-manufacturing-ops", "description": "Manage pet food manufacturing operations including extrusion, retort processing, wet filling, and kibble coating operations."},
    {"name": "pet-food-regulatory-compliance", "description": "Navigate pet food regulatory compliance including FDA FSMA, state feed license registration, AAFCO labeling, and ingredient approval."},
    {"name": "pet-food-raw-material-sourcing", "description": "Source pet food raw materials including meat meals, grains, fats, and specialty ingredients with supplier audit and testing programs."},
    {"name": "pet-food-quality-assurance", "description": "Execute pet food quality assurance programs including microbial testing, moisture, ash, and protein analysis with HACCP management."},
    {"name": "pet-food-brand-innovation", "description": "Drive pet food brand innovation including premium positioning, functional claims, grain-free and raw diet trend adaptation."},
    {"name": "pet-treats-manufacturing", "description": "Manage pet treat manufacturing including baked, extruded, and jerky treat operations with dental claim substantiation and packaging."},
    {"name": "pet-food-retail-ops", "description": "Manage pet food retail operations including pet specialty channel, mass market, and veterinary channel sell-in and activation."},
    {"name": "pet-food-private-label", "description": "Develop and manage pet food private label programs including retailer specification management, quality alignment, and cost negotiation."},
    {"name": "veterinary-diet-management", "description": "Manage veterinary prescription diet programs including clinical nutrition claims, veterinarian detailing, and hospital ordering systems."},
]

# Domain: Aquaculture Technology
skills += [
    {"name": "aquaculture-farm-operations", "description": "Manage aquaculture farm operations including stocking density, feeding management, water quality monitoring, and harvest planning."},
    {"name": "recirculating-aquaculture-systems", "description": "Operate recirculating aquaculture systems including biofilter management, dissolved oxygen control, and water treatment optimization."},
    {"name": "fish-health-management", "description": "Manage fish health programs including disease surveillance, vaccination protocols, biosecurity measures, and veterinary coordination."},
    {"name": "aquaculture-feed-management", "description": "Manage aquaculture feed programs including feed conversion ratio optimization, ingredient specification, and supplier quality audits."},
    {"name": "aquaculture-genetics-programs", "description": "Operate selective breeding and genetics programs for aquaculture species including broodstock management and performance tracking."},
    {"name": "aquaculture-regulatory-compliance", "description": "Navigate aquaculture regulatory compliance including FDA HACCP, state permits, environmental impact monitoring, and antibiotic use policies."},
    {"name": "shellfish-mariculture-ops", "description": "Manage shellfish mariculture operations including oyster, mussel, and clam culture with lease management and harvest certification."},
    {"name": "aquaculture-processing-ops", "description": "Manage aquaculture processing operations including harvest handling, filleting, grading, blast freezing, and export documentation."},
    {"name": "aquaculture-technology-deployment", "description": "Deploy aquaculture technology platforms including sensor networks, automated feeders, underwater cameras, and data analytics dashboards."},
    {"name": "aquaculture-sustainability-cert", "description": "Manage aquaculture sustainability certifications including ASC, BAP, and GlobalG.A.P. with annual audit preparation and corrective actions."},
]

# Domain: Forestry Technology
skills += [
    {"name": "forest-inventory-management", "description": "Conduct and manage forest inventory programs including LiDAR data integration, timber cruising, and stand management planning."},
    {"name": "timber-harvesting-ops", "description": "Plan and execute timber harvesting operations including logging system selection, contractor management, and environmental compliance."},
    {"name": "reforestation-programs", "description": "Manage reforestation and afforestation programs including seedling procurement, site preparation, planting operations, and stocking surveys."},
    {"name": "forest-certification-mgmt", "description": "Manage forest sustainability certifications including FSC and SFI chain-of-custody, annual audit preparation, and claim management."},
    {"name": "wildfire-risk-management", "description": "Assess and mitigate wildfire risk in forest operations including fuel treatment planning, prescribed burn management, and emergency response."},
    {"name": "forest-carbon-programs", "description": "Develop and manage forest carbon sequestration programs including protocol compliance, monitoring, verification, and credit monetization."},
    {"name": "timber-sales-management", "description": "Manage timber sales programs including stumpage appraisal, contract development, scaling agreements, and buyer qualification."},
    {"name": "forest-road-management", "description": "Manage forest road networks including design, construction standards, maintenance scheduling, and stormwater compliance."},
    {"name": "silviculture-program-mgmt", "description": "Manage silvicultural treatment programs including thinning, fertilization, herbicide applications, and treatment effectiveness monitoring."},
    {"name": "urban-forestry-management", "description": "Manage urban forestry programs including tree inventory, canopy assessment, pruning cycles, removal prioritization, and planting programs."},
]

# Domain: Lumber & Wood Products
skills += [
    {"name": "sawmill-operations-management", "description": "Manage sawmill operations including headrig optimization, edger-trimmer lines, kiln drying, and lumber grading operations."},
    {"name": "lumber-grading-quality", "description": "Implement lumber grading quality programs including NHLA rules, machine stress rating, visual grade marking, and customer spec compliance."},
    {"name": "engineered-wood-manufacturing", "description": "Manage engineered wood product manufacturing including LVL, LSL, and I-joist production with adhesive systems and structural testing."},
    {"name": "wood-products-sales-distribution", "description": "Manage wood products sales and distribution including dealer channel management, millwork program development, and price risk hedging."},
    {"name": "plywood-osb-manufacturing", "description": "Operate plywood and OSB manufacturing including veneer peeling, dryer management, lay-up lines, and press operations."},
    {"name": "lumber-kiln-drying-ops", "description": "Manage lumber kiln drying operations including moisture content targets, schedule development, energy optimization, and degrade management."},
    {"name": "wood-treating-operations", "description": "Manage pressure treated wood operations including preservative systems, retention targets, fixation, and APA marking compliance."},
    {"name": "log-procurement-management", "description": "Manage log procurement programs including timber supply agreements, log yard operations, sort yard management, and delivered cost analysis."},
    {"name": "wood-products-logistics", "description": "Manage wood products logistics including rail car management, truck procurement, intermodal optimization, and customer delivery coordination."},
    {"name": "wood-residuals-management", "description": "Manage sawmill residuals including chip sales programs, hog fuel utilization, bark disposal, and sawdust byproduct monetization."},
]

# Domain: Paper & Pulp Manufacturing
skills += [
    {"name": "pulp-mill-operations", "description": "Manage pulp mill operations including kraft cooking, washing, bleaching, and pulp drying operations with chemical recovery integration."},
    {"name": "paper-machine-operations", "description": "Operate paper machine systems including forming, pressing, drying, calendering, and reel operations with basis weight control."},
    {"name": "paper-quality-management", "description": "Manage paper quality programs including brightness, smoothness, tensile strength, and formation testing with customer specification compliance."},
    {"name": "paper-chemical-programs", "description": "Manage paper mill chemical programs including retention aids, sizing agents, strength additives, and biocide programs."},
    {"name": "recycled-fiber-operations", "description": "Manage recycled fiber operations including OCC pulping, de-inking systems, contaminant removal, and recycled content certification."},
    {"name": "paper-product-converting", "description": "Manage paper converting operations including sheeting, slitting, rewinding, folio cutting, and specialty product conversion."},
    {"name": "tissue-manufacturing-ops", "description": "Operate tissue manufacturing including TAD and conventional tissue machines, converting lines, and consumer packaging operations."},
    {"name": "pulp-wood-fiber-sourcing", "description": "Manage fiber sourcing for pulp mills including chip supplier contracts, wood yard operations, and FSC fiber sourcing compliance."},
    {"name": "paper-energy-management", "description": "Manage paper mill energy programs including steam system optimization, power cogeneration, fuel switching, and energy cost reduction."},
    {"name": "packaging-paper-sales", "description": "Manage packaging paper sales programs including containerboard, kraft paper, and specialty paper market development and pricing."},
]

# Domain: Packaging Manufacturing
skills += [
    {"name": "packaging-design-engineering", "description": "Design packaging solutions including structural design, material specification, prototype development, and compression testing."},
    {"name": "packaging-procurement-ops", "description": "Manage packaging procurement including supplier sourcing, tooling ownership, cost negotiation, and supplier performance management."},
    {"name": "flexible-packaging-manufacturing", "description": "Manage flexible packaging manufacturing including extrusion, printing, lamination, and pouch-making operations."},
    {"name": "rigid-packaging-manufacturing", "description": "Manage rigid packaging manufacturing including blow molding, thermoforming, injection molding, and assembly operations."},
    {"name": "packaging-printing-ops", "description": "Operate packaging print operations including flexographic, gravure, offset, and digital printing with color management programs."},
    {"name": "sustainable-packaging-programs", "description": "Lead sustainable packaging programs including recyclability design, PCR content, lightweighting, and EPR compliance management."},
    {"name": "packaging-testing-validation", "description": "Execute packaging testing and validation programs including ISTA protocols, drop testing, leak testing, and transport simulation."},
    {"name": "contract-packaging-ops", "description": "Manage contract packaging operations including co-packing agreements, secondary packaging automation, and fulfillment integration."},
    {"name": "packaging-regulatory-compliance", "description": "Navigate packaging regulatory compliance including FDA indirect food contact, California AB 906, and EU packaging regulation."},
    {"name": "packaging-innovation-pipeline", "description": "Manage packaging innovation pipelines including material substitution projects, active packaging development, and smart packaging programs."},
]

# Domain: Industrial Gases
skills += [
    {"name": "gas-production-operations", "description": "Manage industrial gas production including ASU operations, hydrogen generation, CO2 recovery, and specialty gas cylinder filling."},
    {"name": "gas-distribution-logistics", "description": "Manage industrial gas distribution logistics including cylinder fleet management, bulk delivery routing, and HAZMAT compliance."},
    {"name": "gas-cylinder-management", "description": "Operate cylinder lifecycle programs including hydrostatic testing, valve rebuild, regulatory marking, and customer asset tracking."},
    {"name": "bulk-gas-supply-systems", "description": "Design and manage bulk gas supply systems including tank installation, vaporizer sizing, telemetry monitoring, and top-off scheduling."},
    {"name": "specialty-gas-manufacturing", "description": "Manage specialty gas manufacturing including ultra-high purity cylinder preparation, blend certification, and analytical verification."},
    {"name": "gas-safety-compliance", "description": "Manage industrial gas safety programs including compressed gas handler training, storage compliance, and emergency response procedures."},
    {"name": "gas-applications-technology", "description": "Provide industrial gas application support including welding, cutting, heat treating, food processing, and semiconductor fab applications."},
    {"name": "gas-pricing-contracts", "description": "Manage industrial gas pricing and customer contracts including take-or-pay agreements, indexation clauses, and renewal negotiations."},
    {"name": "gas-plant-engineering", "description": "Support gas plant engineering programs including ASU design, pipeline systems, purity upgrades, and capacity expansion projects."},
    {"name": "cryogenic-liquid-ops", "description": "Manage cryogenic liquid operations including LIN, LOX, LAR, and LCO2 storage, transfer, and delivery operations."},
]

# Domain: Lubricants Manufacturing
skills += [
    {"name": "lubricant-formulation-development", "description": "Develop lubricant formulations including base oil selection, additive chemistry, viscosity grade optimization, and performance testing."},
    {"name": "lubricants-manufacturing-ops", "description": "Manage lubricant manufacturing operations including blending, filtration, filling, and quality release for automotive and industrial products."},
    {"name": "lubricant-base-oil-sourcing", "description": "Source lubricant base oils including API Group I-V selection, refinery procurement, and supply security management."},
    {"name": "lubricant-additive-management", "description": "Manage lubricant additive programs including package sourcing, treat rate optimization, and OEM approval maintenance."},
    {"name": "automotive-lubricant-sales", "description": "Manage automotive lubricant sales programs including DIY retail, DIFM installer channel, and OEM factory fill programs."},
    {"name": "industrial-lubricant-sales", "description": "Manage industrial lubricant sales through distributor and direct channels including MRO accounts, OEM partnerships, and technical service."},
    {"name": "lubricant-quality-testing", "description": "Execute lubricant quality testing programs including viscosity index, flash point, pour point, oxidation stability, and contaminant analysis."},
    {"name": "lubricant-regulatory-compliance", "description": "Navigate lubricant regulatory compliance including REACH registration, SDS authoring, API and ACEA licensing, and EPA VGP compliance."},
    {"name": "used-oil-management", "description": "Manage used oil collection and re-refining programs including collection network, processing operations, and re-refined base oil marketing."},
    {"name": "grease-manufacturing-ops", "description": "Manage grease manufacturing operations including soap thickener production, kettle operations, filling, and NLGI grade certification."},
]

# Domain: Cutting Tools Manufacturing
skills += [
    {"name": "carbide-tooling-manufacturing", "description": "Manage carbide cutting tool manufacturing including powder metallurgy, sintering, grinding, and PVD coating operations."},
    {"name": "cutting-tool-product-development", "description": "Develop cutting tool products including geometry design, substrate selection, coating optimization, and machining application testing."},
    {"name": "cutting-tool-sales-distribution", "description": "Manage cutting tool sales and distribution through industrial distributors, OEM programs, and direct end-user accounts."},
    {"name": "tool-life-management", "description": "Implement tool life management programs including tool wear monitoring, regrind programs, and cost-per-part analysis for manufacturing customers."},
    {"name": "cutting-tool-applications", "description": "Provide cutting tool application engineering support including feeds and speeds optimization, tool path programming, and coolant recommendations."},
    {"name": "drills-endmills-manufacturing", "description": "Manage drill and endmill manufacturing operations including blank production, flute grinding, heat treatment, and tip geometry inspection."},
    {"name": "indexable-insert-manufacturing", "description": "Manage indexable insert manufacturing including press compaction, sintering, CVD/PVD coating, and edge honing operations."},
    {"name": "cutting-tool-raw-materials", "description": "Source cutting tool raw materials including tungsten carbide powder, cobalt binder, high speed steel, and PCD/CBN blanks."},
    {"name": "cutting-tool-quality-assurance", "description": "Execute cutting tool quality programs including dimensional inspection, hardness testing, coating adhesion, and run-out measurement."},
    {"name": "reconditioning-regrind-ops", "description": "Manage cutting tool reconditioning and regrind operations including inspection, geometry restoration, and recoating programs."},
]

# Domain: Advanced Composites Manufacturing
skills += [
    {"name": "composites-layup-operations", "description": "Manage composite layup operations including manual layup, automated fiber placement, tape laying, and vacuum bagging processes."},
    {"name": "composites-curing-operations", "description": "Manage composite curing operations including autoclave cycle development, oven cure programming, and cure monitoring instrumentation."},
    {"name": "composites-raw-material-mgmt", "description": "Manage composite raw materials including prepreg procurement, resin systems, core materials, and out-time/shelf-life tracking."},
    {"name": "composites-ndt-inspection", "description": "Execute composite NDT inspection programs including ultrasonic C-scan, thermography, and X-ray inspection with acceptance criteria."},
    {"name": "composites-tooling-management", "description": "Manage composite tooling programs including mold design, Invar tooling, soft tooling qualification, and thermal survey management."},
    {"name": "composites-design-engineering", "description": "Support composite design engineering including laminate analysis, allowables development, and design-for-manufacture collaboration."},
    {"name": "composites-repair-programs", "description": "Manage composite repair programs including damage assessment, bonded repair qualification, and aircraft regulatory repair approvals."},
    {"name": "composites-process-engineering", "description": "Develop composite manufacturing processes including RTM, VARTM, pultrusion, and filament winding process qualification."},
    {"name": "composites-quality-management", "description": "Implement composite quality management including first article inspection, in-process controls, and AS9100 system compliance."},
    {"name": "composites-market-development", "description": "Drive composites market development in aerospace, automotive, wind energy, and marine applications with application engineering support."},
]

# Domain: Foam Manufacturing
skills += [
    {"name": "polyurethane-foam-manufacturing", "description": "Manage polyurethane foam manufacturing including slab stock production, molded foam, spray foam, and pour-in-place operations."},
    {"name": "foam-formulation-development", "description": "Develop foam formulations including polyol blend development, blowing agent selection, and foam property optimization for target applications."},
    {"name": "foam-converting-operations", "description": "Manage foam converting operations including cutting, laminating, profile contouring, and fabrication for bedding and seating applications."},
    {"name": "polystyrene-foam-manufacturing", "description": "Manage EPS and XPS foam manufacturing including bead expansion, molding, board extrusion, and thermal performance testing."},
    {"name": "technical-foam-sales", "description": "Manage technical foam sales programs including industrial filtration, gasketing, acoustic, and cushioning packaging applications."},
    {"name": "foam-raw-material-sourcing", "description": "Source foam raw materials including MDI, TDI, polyols, and specialty additives with supply security and cost management."},
    {"name": "foam-fire-safety-compliance", "description": "Navigate foam fire safety compliance including CAL TB 117 requirements, flame retardant systems, and GREENGUARD certification."},
    {"name": "mattress-bedding-foam-ops", "description": "Manage mattress and bedding foam operations including comfort layer specification, core support design, and retailer product programs."},
    {"name": "foam-quality-testing", "description": "Execute foam quality testing programs including ILD, density, resilience, compression set, and dimensional stability per ASTM standards."},
    {"name": "spray-foam-insulation-market", "description": "Manage spray polyurethane foam insulation market programs including contractor training, code compliance documentation, and distribution."},
]

# Domain: Nonwoven Fabrics Manufacturing
skills += [
    {"name": "spunbond-meltblown-manufacturing", "description": "Manage spunbond and meltblown nonwoven production including extrusion die management, web formation, bonding, and winding operations."},
    {"name": "needlepunch-nonwoven-ops", "description": "Operate needlepunch nonwoven lines including batt formation, needle loom management, and geotextile and filtration product specifications."},
    {"name": "nonwoven-raw-material-mgmt", "description": "Manage nonwoven raw materials including PP, PET, and bicomponent fiber sourcing with quality verification and supply security programs."},
    {"name": "nonwoven-converting-ops", "description": "Manage nonwoven converting operations including slitting, laminating, embossing, aperturing, and hygiene product component fabrication."},
    {"name": "hygiene-nonwoven-applications", "description": "Develop nonwoven applications for personal care and hygiene including baby diapers, feminine care, and adult incontinence components."},
    {"name": "filtration-nonwoven-applications", "description": "Develop filtration nonwoven applications including HVAC filter media, liquid filtration, and facemask filtration component development."},
    {"name": "nonwoven-quality-testing", "description": "Execute nonwoven quality testing including basis weight, thickness, tensile, air permeability, and liquid strike-through testing."},
    {"name": "geosynthetic-nonwoven-sales", "description": "Manage geosynthetic nonwoven sales programs including specification work, project submittals, and civil engineering contractor channel."},
    {"name": "sustainable-nonwoven-development", "description": "Develop sustainable nonwoven products including bio-based fibers, biodegradable options, and recycled content material programs."},
    {"name": "nonwoven-medical-applications", "description": "Manage nonwoven medical application development including surgical drapes, gowns, and wound care components with FDA compliance."},
]

# Domain: Seals & Gaskets Manufacturing
skills += [
    {"name": "sealing-product-engineering", "description": "Engineer sealing solutions including O-ring selection, custom gasket design, and seal material specification for pressure and temperature conditions."},
    {"name": "gasket-manufacturing-ops", "description": "Manage gasket manufacturing operations including die cutting, spiral wound, ring joint, and custom fabrication operations."},
    {"name": "seal-manufacturing-ops", "description": "Manage seal manufacturing operations including rubber molding, PTFE machining, mechanical seal assembly, and leak testing."},
    {"name": "sealing-material-development", "description": "Develop sealing materials including elastomer compounds, PTFE formulations, and composite gasket materials for application-specific performance."},
    {"name": "sealing-technical-service", "description": "Provide sealing technical service including failure mode analysis, material compatibility guidance, and installation specification support."},
    {"name": "industrial-seals-distribution", "description": "Manage industrial seals and gaskets distribution through MRO channels including stocking programs, order management, and technical support."},
    {"name": "oil-gas-sealing-solutions", "description": "Develop sealing solutions for oil and gas applications including HP/HT seals, blowout preventer seals, and subsea sealing systems."},
    {"name": "sealing-quality-assurance", "description": "Execute sealing quality programs including pressure testing, dimensional inspection, material certification, and third-party approval management."},
    {"name": "dynamic-sealing-applications", "description": "Manage dynamic seal application programs including reciprocating, rotary, and oscillating seals for hydraulic and pneumatic systems."},
    {"name": "sealing-catalog-management", "description": "Manage sealing product catalog programs including standard cross-reference, custom part number management, and ERP data maintenance."},
]

# Domain: Industrial Pumps Manufacturing
skills += [
    {"name": "centrifugal-pump-manufacturing", "description": "Manage centrifugal pump manufacturing operations including casting, machining, assembly, hydrostatic testing, and performance curve validation."},
    {"name": "positive-displacement-pump-ops", "description": "Manage positive displacement pump manufacturing including gear, lobe, diaphragm, and peristaltic pump assembly and testing."},
    {"name": "pump-application-engineering", "description": "Provide pump application engineering support including hydraulic sizing, NPSHa analysis, seal selection, and system curve development."},
    {"name": "pump-aftermarket-service", "description": "Manage pump aftermarket service operations including spare parts, field service dispatch, repair workshop, and predictive maintenance programs."},
    {"name": "pump-raw-material-mgmt", "description": "Manage pump manufacturing raw materials including castings, forgings, and specialty alloy procurement with material certification."},
    {"name": "submersible-pump-manufacturing", "description": "Manage submersible pump manufacturing including hermetic motor assembly, impeller stacking, pressure housing, and submersion testing."},
    {"name": "pump-distribution-channel", "description": "Manage pump distribution channel programs including rep network management, stocking distributor programs, and market development."},
    {"name": "pump-quality-management", "description": "Implement pump quality management programs including ISO 9001 compliance, Hydraulic Institute testing standards, and API 610 certification."},
    {"name": "pump-systems-sales", "description": "Manage pump system sales including skid package design, turnkey supply, and engineered-to-order project management."},
    {"name": "pump-energy-efficiency-programs", "description": "Develop pump energy efficiency programs including IE efficiency class compliance, variable speed drive integration, and lifecycle cost analysis."},
]

# Domain: Heat Exchangers Manufacturing
skills += [
    {"name": "shell-tube-heat-exchanger-mfg", "description": "Manage shell-and-tube heat exchanger manufacturing including TEMA standard compliance, tube bundle assembly, and hydrostatic testing."},
    {"name": "plate-heat-exchanger-manufacturing", "description": "Manage plate heat exchanger manufacturing including plate pressing, gasket assembly, frame machining, and thermal performance testing."},
    {"name": "heat-exchanger-thermal-design", "description": "Perform heat exchanger thermal design including heat transfer calculations, fouling allowances, and pressure drop optimization using HTRI."},
    {"name": "heat-exchanger-materials-mgmt", "description": "Manage heat exchanger materials including carbon steel, stainless, titanium, and exotic alloy procurement with MTR management."},
    {"name": "heat-exchanger-inspection", "description": "Execute heat exchanger inspection programs including eddy current testing, hydroblast cleaning, re-tubing, and fitness-for-service assessment."},
    {"name": "heat-exchanger-aftermarket", "description": "Manage heat exchanger aftermarket programs including spare plate inventory, gasket supply programs, and field service coordination."},
    {"name": "air-cooled-heat-exchanger-ops", "description": "Manage air-cooled heat exchanger manufacturing and maintenance including fan section design, fin tube bundles, and API 661 compliance."},
    {"name": "heat-exchanger-project-mgmt", "description": "Manage heat exchanger project execution including ASME U-stamp certification, inspection coordination, and delivery scheduling."},
    {"name": "heat-exchanger-sales-apps", "description": "Manage heat exchanger sales and application development across HVAC, process industry, and power generation markets."},
    {"name": "heat-exchanger-cleaning-services", "description": "Manage heat exchanger cleaning service operations including hydroblasting, chemical cleaning, and performance verification programs."},
]

# Domain: Filtration Systems Manufacturing
skills += [
    {"name": "liquid-filtration-product-dev", "description": "Develop liquid filtration products including filter media selection, housing design, flow rate optimization, and filtration efficiency validation."},
    {"name": "air-filtration-manufacturing", "description": "Manage air filtration manufacturing operations including pleating, frame assembly, HEPA certification testing, and MERV rating compliance."},
    {"name": "industrial-filter-sales", "description": "Manage industrial filtration sales through OEM and aftermarket channels including service interval programs and replacement filter kits."},
    {"name": "filtration-media-development", "description": "Develop filtration media including fibrous, membrane, granular, and depth filtration materials with particle retention characterization."},
    {"name": "cleanroom-filtration-ops", "description": "Manage cleanroom filtration programs including HEPA and ULPA filter testing, installation qualification, and leak testing procedures."},
    {"name": "water-filtration-systems", "description": "Design and manage water filtration systems including multimedia filtration, cartridge filtration, and membrane system integration."},
    {"name": "filtration-raw-material-mgmt", "description": "Manage filtration raw material supply including filter media, housings, gaskets, and hardware with quality certification programs."},
    {"name": "filtration-quality-testing", "description": "Execute filtration quality testing programs including efficiency rating, pressure drop, burst strength, and compatibility testing."},
    {"name": "hvac-filtration-programs", "description": "Manage HVAC filtration programs including specification compliance, energy efficiency analysis, and preventive replacement scheduling."},
    {"name": "membrane-filtration-technology", "description": "Develop membrane filtration technology programs including MF, UF, NF, and RO membrane qualification and system integration."},
]

# Domain: Conveyor Systems Manufacturing
skills += [
    {"name": "conveyor-systems-engineering", "description": "Engineer conveyor systems including belt conveyor design, chain conveyor specification, load analysis, and power calculation."},
    {"name": "conveyor-manufacturing-ops", "description": "Manage conveyor manufacturing operations including structural fabrication, component assembly, factory acceptance testing, and installation coordination."},
    {"name": "conveyor-belt-management", "description": "Manage conveyor belt programs including belt selection, splice repair, tension monitoring, and predictive replacement scheduling."},
    {"name": "material-handling-automation", "description": "Implement material handling automation including sortation systems, accumulation conveyors, and WCS integration for distribution centers."},
    {"name": "conveyor-maintenance-programs", "description": "Manage conveyor maintenance programs including preventive maintenance schedules, lubrication programs, and emergency repair response."},
    {"name": "mining-conveyor-systems", "description": "Manage mining conveyor systems including overland belt conveyors, underground conveyors, and high-inclination conveyor operations."},
    {"name": "food-grade-conveyor-ops", "description": "Manage food-grade conveyor systems including hygienic design compliance, washdown protocols, and FDA material compliance."},
    {"name": "conveyor-controls-integration", "description": "Manage conveyor control system integration including PLC programming, HMI development, and SCADA connectivity for production lines."},
    {"name": "overhead-conveyor-systems", "description": "Design and manage overhead conveyor systems including power-and-free systems, monorail systems, and automotive assembly applications."},
    {"name": "conveyor-aftermarket-parts", "description": "Manage conveyor aftermarket parts programs including spare parts stocking, OEM sourcing, and field service dispatch operations."},
]

# Domain: Industrial Robotics Integration
skills += [
    {"name": "robot-cell-design-integration", "description": "Design and integrate robotic work cells including robot selection, end-of-arm tooling, safety fencing, and control system integration."},
    {"name": "welding-robot-operations", "description": "Manage welding robot operations including program development, weld parameter optimization, torch maintenance, and quality monitoring."},
    {"name": "palletizing-robot-systems", "description": "Implement and manage robotic palletizing systems including pattern programming, case handling EOAT design, and throughput optimization."},
    {"name": "collaborative-robot-deployment", "description": "Deploy collaborative robot (cobot) applications including risk assessment, payload analysis, application development, and operator training."},
    {"name": "robot-vision-system-integration", "description": "Integrate machine vision with robotic systems including camera calibration, part location algorithms, and quality inspection applications."},
    {"name": "robot-maintenance-programs", "description": "Manage industrial robot maintenance programs including preventive maintenance, battery replacement, axis calibration, and overhaul management."},
    {"name": "assembly-automation-systems", "description": "Design and manage automated assembly systems including pick-and-place robotics, torque-controlled fastening, and in-line testing."},
    {"name": "amr-agv-deployment", "description": "Deploy autonomous mobile robots and AGV systems in manufacturing and warehouse operations including fleet management and WMS integration."},
    {"name": "robot-programming-services", "description": "Provide robot programming services including offline simulation, path optimization, cycle time analysis, and program version management."},
    {"name": "robot-roi-analysis", "description": "Develop robot ROI analysis programs including labor displacement modeling, throughput improvement quantification, and payback calculation."},
]

# Domain: Machine Vision Systems
skills += [
    {"name": "machine-vision-system-design", "description": "Design machine vision inspection systems including camera selection, lens optics, lighting design, and image processing algorithm development."},
    {"name": "vision-quality-inspection", "description": "Implement vision-based quality inspection including surface defect detection, dimensional measurement, and label verification systems."},
    {"name": "vision-system-integration", "description": "Integrate machine vision systems with production lines including PLC interfaces, reject mechanisms, and MES data connectivity."},
    {"name": "deep-learning-vision-apps", "description": "Deploy deep learning vision applications including neural network training, defect classification, and model performance monitoring."},
    {"name": "3d-vision-metrology", "description": "Apply 3D machine vision for metrology applications including structured light scanning, laser triangulation, and point cloud analysis."},
    {"name": "barcode-ocr-verification", "description": "Manage barcode and OCR vision verification systems including print quality grading, 2D code reading, and traceability integration."},
    {"name": "vision-system-maintenance", "description": "Maintain machine vision systems including lens cleaning protocols, illuminator replacement, calibration verification, and software updates."},
    {"name": "vision-system-sales", "description": "Manage machine vision system sales through systems integrators and direct OEM channels including demo programs and technical support."},
    {"name": "pharmaceutical-vision-inspection", "description": "Manage pharmaceutical vision inspection programs including container inspection, fill level verification, and labeling compliance inspection."},
    {"name": "vision-guided-robotics", "description": "Develop vision-guided robotic applications including bin picking, guidance correction, and assembly verification systems."},
]

# Domain: Process Control Systems
skills += [
    {"name": "dcs-system-operations", "description": "Operate distributed control systems including controller configuration, alarm management, control loop tuning, and historian integration."},
    {"name": "plc-automation-programming", "description": "Manage PLC automation programming including ladder logic development, function block design, and communication protocol configuration."},
    {"name": "process-instrumentation-mgmt", "description": "Manage process instrumentation programs including transmitter calibration, control valve maintenance, and instrument loop testing."},
    {"name": "process-control-optimization", "description": "Implement process control optimization including advanced regulatory control, feedforward strategies, and model predictive control."},
    {"name": "alarm-management-systems", "description": "Design and manage alarm management systems including EEMUA 191 compliance, alarm rationalization, and operator interface optimization."},
    {"name": "industrial-cybersecurity-ops", "description": "Manage OT cybersecurity programs including ICS network segmentation, vulnerability management, and NIST CSF compliance."},
    {"name": "control-system-commissioning", "description": "Manage control system commissioning including FAT coordination, SAT execution, loop checking, and startup support."},
    {"name": "batch-control-systems", "description": "Implement batch control systems per ISA-88 standard including recipe management, equipment phase logic, and batch reporting."},
    {"name": "safety-instrumented-systems", "description": "Design and manage safety instrumented systems including SIL assessment, SIS hardware design, and IEC 61511 lifecycle compliance."},
    {"name": "process-analytics-management", "description": "Manage process analytical technology programs including at-line analyzer maintenance, chemometric model updates, and data historian integration."},
]

# Domain: Metrology & Inspection Equipment
skills += [
    {"name": "cmm-operations-management", "description": "Manage coordinate measuring machine operations including fixture design, program development, GR&R studies, and measurement system validation."},
    {"name": "calibration-lab-management", "description": "Operate calibration laboratory programs including ISO 17025 accreditation, calibration scheduling, uncertainty analysis, and NIST traceability."},
    {"name": "surface-metrology-programs", "description": "Manage surface metrology programs including profilometry, interferometry, and texture measurement for machined components."},
    {"name": "dimensional-inspection-ops", "description": "Manage dimensional inspection operations including first article inspection, in-process gauging, and final acceptance measurement."},
    {"name": "metrology-software-management", "description": "Manage metrology software programs including CAD model alignment, GD&T evaluation, and inspection report generation."},
    {"name": "non-contact-measurement-systems", "description": "Deploy non-contact measurement systems including laser trackers, structured light scanners, and photogrammetry for large-scale metrology."},
    {"name": "gauge-management-programs", "description": "Manage gauge and tooling inspection programs including gauge R&R, calibration tracking, and controlled gauge distribution."},
    {"name": "in-process-measurement", "description": "Implement in-process measurement solutions including probing cycles, SPC integration, and closed-loop process feedback."},
    {"name": "metrology-equipment-sales", "description": "Manage metrology equipment sales including CMM, optical comparator, and handheld measurement tool programs with application support."},
    {"name": "measurement-uncertainty-analysis", "description": "Perform measurement uncertainty analysis using GUM methodology for calibration labs and production measurement systems."},
]

# Domain: Laboratory Instruments Manufacturing
skills += [
    {"name": "analytical-instrument-manufacturing", "description": "Manage analytical instrument manufacturing including optical system assembly, detector integration, software calibration, and performance verification."},
    {"name": "lab-instrument-product-development", "description": "Develop laboratory instrument products from concept through validation including user requirements, design verification, and regulatory clearance."},
    {"name": "lab-instrument-sales-ops", "description": "Manage laboratory instrument sales operations including distributor channel, direct sales, demo fleet, and service contract programs."},
    {"name": "spectroscopy-instrument-ops", "description": "Manage spectroscopy instrument operations including UV-Vis, IR, Raman, and NMR instrument deployment, qualification, and maintenance."},
    {"name": "chromatography-systems-mgmt", "description": "Manage chromatography system programs including HPLC, GC, and LC-MS instrument qualification, method transfer, and service management."},
    {"name": "lab-automation-integration", "description": "Integrate laboratory automation systems including liquid handling robots, sample preparation, LIMS connectivity, and workflow automation."},
    {"name": "lab-instrument-service-ops", "description": "Manage laboratory instrument service operations including field service, depot repair, preventive maintenance, and calibration programs."},
    {"name": "iq-oq-pq-management", "description": "Manage IQ/OQ/PQ qualification programs for laboratory instruments in regulated pharmaceutical and biotech environments."},
    {"name": "lab-consumables-management", "description": "Manage laboratory consumables programs including column supply, reagent kits, cuvettes, and reference standard sourcing."},
    {"name": "lab-informatics-systems", "description": "Manage laboratory informatics systems including LIMS, ELN, and CDS implementation with data integrity and 21 CFR Part 11 compliance."},
]

# Domain: Dental Equipment Manufacturing
skills += [
    {"name": "dental-equipment-manufacturing", "description": "Manage dental equipment manufacturing including dental unit assembly, chair mechanics, delivery system integration, and performance testing."},
    {"name": "dental-imaging-systems", "description": "Manage dental imaging system programs including intraoral sensors, panoramic X-ray, and CBCT systems with regulatory clearance."},
    {"name": "dental-cad-cam-systems", "description": "Manage dental CAD/CAM systems including chairside milling units, scanning systems, and digital workflow integration programs."},
    {"name": "dental-equipment-sales", "description": "Manage dental equipment sales through dental dealer channels, DSO group purchasing programs, and direct dental school accounts."},
    {"name": "dental-equipment-service", "description": "Manage dental equipment service operations including field service, repair depot, preventive maintenance contracts, and spare parts."},
    {"name": "infection-control-equipment", "description": "Manage dental infection control equipment programs including autoclave manufacturing, washer disinfector, and unit waterline treatment systems."},
    {"name": "dental-laser-systems", "description": "Manage dental laser system programs including Er:YAG, diode, and CO2 laser product lines with clinical application support."},
    {"name": "dental-equipment-compliance", "description": "Navigate dental equipment regulatory compliance including FDA 510k clearance, IEC 60601 certification, and CE marking processes."},
    {"name": "dental-practice-technology", "description": "Manage dental practice technology programs including practice management software integration, digital impression systems, and workflow consulting."},
    {"name": "dental-consumables-programs", "description": "Manage dental consumable programs including restorative materials, impression materials, and infection control supply bundled with equipment."},
]

# Domain: Photonics & Lasers Industry
skills += [
    {"name": "laser-product-manufacturing", "description": "Manage laser product manufacturing including resonator assembly, beam delivery integration, cooling system, and performance characterization."},
    {"name": "laser-application-development", "description": "Develop laser application solutions including materials processing, medical, and scientific applications with parameter optimization."},
    {"name": "photonic-component-manufacturing", "description": "Manage photonic component manufacturing including optical fiber fabrication, splitter assembly, and wavelength division multiplexing components."},
    {"name": "laser-safety-programs", "description": "Implement laser safety programs including hazard classification, control measures, laser safety officer training, and exposure limit compliance."},
    {"name": "optics-manufacturing-ops", "description": "Manage precision optics manufacturing including grinding, polishing, coating, and interferometric testing for optical components."},
    {"name": "laser-sales-distribution", "description": "Manage laser and photonics sales through direct and distribution channels including application lab demonstrations and technical support."},
    {"name": "lidar-sensor-development", "description": "Develop LiDAR sensor solutions including mechanical spinning, solid-state, and FMCW architectures for automotive and industrial applications."},
    {"name": "fiber-laser-operations", "description": "Manage fiber laser product lines including single-mode, multi-mode, and ultrafast laser platforms with service and calibration programs."},
    {"name": "photonics-rd-management", "description": "Manage photonics research and development programs including PhC waveguides, integrated photonics, and quantum photonics projects."},
    {"name": "laser-regulatory-compliance", "description": "Navigate laser regulatory compliance including FDA CDRH requirements, IEC 60825 laser product standards, and CE technical documentation."},
]

# Domain: Power Electronics Manufacturing
skills += [
    {"name": "power-converter-manufacturing", "description": "Manage power converter manufacturing including PCB assembly, transformer winding, heat sink fabrication, and electrical test operations."},
    {"name": "vfd-drive-manufacturing", "description": "Manage variable frequency drive manufacturing operations including IGBT module mounting, bus bar assembly, gate driver testing, and functional verification."},
    {"name": "power-electronics-design", "description": "Develop power electronics designs including switching topology selection, thermal management, EMI filtering, and control loop compensation."},
    {"name": "power-supply-manufacturing", "description": "Manage power supply manufacturing including SMPS assembly, regulation testing, safety compliance testing, and reliability screening."},
    {"name": "power-electronics-testing", "description": "Execute power electronics testing programs including efficiency characterization, thermal imaging, EMC pre-compliance, and accelerated life testing."},
    {"name": "inverter-solar-manufacturing", "description": "Manage solar inverter manufacturing including MPPT circuit assembly, grid interface testing, and UL 1741 compliance management."},
    {"name": "power-electronics-sales", "description": "Manage power electronics sales through industrial distribution and OEM channels including custom design support and specification programs."},
    {"name": "power-electronics-components", "description": "Manage power electronics component sourcing including IGBTs, MOSFETs, capacitors, and magnetic components with approved vendor lists."},
    {"name": "ev-charging-systems-mfg", "description": "Manage EV charging system manufacturing including Level 2 EVSE, DC fast charger, and bidirectional charger assembly and certification."},
    {"name": "ups-systems-manufacturing", "description": "Manage UPS manufacturing operations including battery module assembly, static bypass integration, and data center certification testing."},
]

# Domain: Motors & Generators Manufacturing
skills += [
    {"name": "electric-motor-manufacturing", "description": "Manage electric motor manufacturing operations including stator winding, rotor assembly, bearing housing, and performance testing."},
    {"name": "generator-manufacturing-ops", "description": "Manage generator manufacturing including alternator winding, prime mover integration, governor systems, and load bank testing."},
    {"name": "motor-rewind-repair-services", "description": "Manage motor rewind and repair service operations including failure diagnosis, rewind engineering, test stand certification, and field service."},
    {"name": "motor-application-engineering", "description": "Provide motor application engineering support including frame selection, efficiency class, VFD compatibility, and thermal derating analysis."},
    {"name": "motor-raw-material-sourcing", "description": "Source motor manufacturing materials including lamination steel, copper wire, insulation materials, and permanent magnets."},
    {"name": "servo-motion-control-systems", "description": "Manage servo motor and motion control system programs including encoder feedback, drive-motor matching, and application commissioning."},
    {"name": "motor-energy-efficiency-mgmt", "description": "Manage motor energy efficiency programs including IE class compliance, DOE regulatory requirements, and EASA rewind standards."},
    {"name": "motor-quality-testing", "description": "Execute motor quality testing programs including IEEE 112 efficiency testing, hipot, surge, and vibration acceptance testing."},
    {"name": "fractional-motor-manufacturing", "description": "Manage fractional horsepower motor manufacturing including HVAC, appliance, and pump motor production with UL compliance."},
    {"name": "permanent-magnet-motor-ops", "description": "Manage permanent magnet motor programs including rare earth magnet sourcing, rotor assembly, demagnetization testing, and EV traction applications."},
]

# Domain: Transformers Manufacturing
skills += [
    {"name": "distribution-transformer-mfg", "description": "Manage distribution transformer manufacturing including core stacking, coil winding, tank fabrication, oil filling, and routine testing."},
    {"name": "power-transformer-manufacturing", "description": "Manage large power transformer manufacturing including HV winding, insulation systems, core assembly, and type testing per IEC 60076."},
    {"name": "transformer-testing-programs", "description": "Execute transformer testing programs including routine, type, and special tests including impedance, losses, and dielectric withstand."},
    {"name": "transformer-oil-management", "description": "Manage transformer insulating oil programs including DGA analysis, oil testing, reclaiming, and oil treatment services."},
    {"name": "transformer-field-service", "description": "Manage transformer field service operations including installation supervision, commissioning, maintenance, and emergency repair programs."},
    {"name": "dry-type-transformer-mfg", "description": "Manage dry-type transformer manufacturing including cast resin and VPI processes, enclosure fabrication, and UL 506 compliance."},
    {"name": "transformer-engineering-design", "description": "Provide transformer engineering design including core flux density, thermal design, short circuit withstand, and noise level optimization."},
    {"name": "transformer-raw-materials", "description": "Manage transformer raw material sourcing including grain-oriented silicon steel, copper, insulation materials, and tankage fabrication."},
    {"name": "transformer-sales-distribution", "description": "Manage transformer sales through utility, OEM, and distribution channels including rental fleet programs and project bid management."},
    {"name": "transformer-condition-monitoring", "description": "Implement transformer condition monitoring programs including online DGA, bushing monitoring, and thermal imaging surveys."},
]

# Domain: Lighting Manufacturing
skills += [
    {"name": "led-lighting-manufacturing", "description": "Manage LED lighting manufacturing operations including LED PCB assembly, driver integration, thermal management, and photometric testing."},
    {"name": "lighting-product-development", "description": "Develop lighting products from concept through commercialization including optical design, thermal simulation, and DLC qualification."},
    {"name": "commercial-lighting-sales", "description": "Manage commercial lighting sales through lighting distributors, rep agencies, and specification-grade channels including agent management."},
    {"name": "lighting-controls-integration", "description": "Manage lighting controls integration programs including DALI, 0-10V dimming, wireless mesh, and building automation system interfaces."},
    {"name": "lighting-fixture-manufacturing", "description": "Manage lighting fixture manufacturing including housing fabrication, reflector forming, driver mounting, and UL 1598 compliance."},
    {"name": "outdoor-lighting-systems", "description": "Manage outdoor lighting programs including roadway, area, and sports lighting with IESNA calculation standards and photometric data."},
    {"name": "lighting-energy-rebate-programs", "description": "Manage lighting energy efficiency rebate programs including utility incentive qualification, pre-approval processes, and measurement verification."},
    {"name": "horticulture-lighting-systems", "description": "Develop horticultural lighting systems including grow light design, PPFD optimization, spectrum selection, and controlled environment applications."},
    {"name": "lighting-quality-photometric", "description": "Execute lighting quality programs including LM-79 photometric testing, LM-80 lumen maintenance, and color consistency management."},
    {"name": "emergency-lighting-systems", "description": "Manage emergency and exit lighting systems including battery backup compliance, UL 924 listing, code compliance, and test management."},
]

# Domain: HVAC Equipment Manufacturing
skills += [
    {"name": "commercial-hvac-manufacturing", "description": "Manage commercial HVAC manufacturing operations including coil assembly, refrigerant circuit fabrication, controls integration, and leak testing."},
    {"name": "residential-hvac-manufacturing", "description": "Manage residential HVAC manufacturing including split system assembly, heat pump integration, efficiency rating testing, and quality release."},
    {"name": "hvac-controls-development", "description": "Develop HVAC controls solutions including thermostat firmware, building automation integration, and smart home protocol compatibility."},
    {"name": "hvac-refrigerant-management", "description": "Manage HVAC refrigerant programs including low-GWP refrigerant transition, EPA Section 608 compliance, and refrigerant inventory management."},
    {"name": "hvac-distribution-channel", "description": "Manage HVAC distribution channel programs including wholesale distributor support, contractor loyalty programs, and co-op advertising."},
    {"name": "hvac-energy-efficiency-mgmt", "description": "Manage HVAC energy efficiency programs including SEER2/EER2 compliance, ENERGY STAR certification, and efficiency test lab management."},
    {"name": "industrial-cooling-systems", "description": "Manage industrial cooling system programs including process chillers, cooling towers, and data center cooling solutions."},
    {"name": "hvac-aftermarket-parts", "description": "Manage HVAC aftermarket parts programs including genuine parts distribution, OEM cross-reference, and field tech support operations."},
    {"name": "hvac-manufacturing-quality", "description": "Implement HVAC manufacturing quality programs including ARI certification testing, refrigerant charge verification, and customer return analysis."},
    {"name": "ductwork-air-distribution", "description": "Manage ductwork and air distribution manufacturing including spiral duct fabrication, diffuser production, and SMACNA standard compliance."},
]

# Domain: Fire Protection Equipment Manufacturing
skills += [
    {"name": "fire-sprinkler-manufacturing", "description": "Manage fire sprinkler head manufacturing including fusible link assembly, orifice plating, UL listed production, and hydrostatic testing."},
    {"name": "fire-detection-systems-mfg", "description": "Manage fire detection system manufacturing including smoke detector assembly, control panel fabrication, and UL 864 compliance."},
    {"name": "fire-suppression-systems", "description": "Manage clean agent and CO2 suppression system manufacturing including cylinder filling, valve assembly, and NFPA 12 compliance."},
    {"name": "fire-extinguisher-manufacturing", "description": "Manage fire extinguisher manufacturing operations including shell hydrotest, dry chemical filling, valve assembly, and UL 711 rating."},
    {"name": "fire-protection-testing", "description": "Execute fire protection product testing programs including UL listing compliance, FM approval, and international CE certification."},
    {"name": "fire-protection-distribution", "description": "Manage fire protection product distribution through fire protection contractors, distributors, and national accounts programs."},
    {"name": "passive-fire-protection", "description": "Manage passive fire protection product programs including firestop systems, intumescent coatings, and fire door hardware products."},
    {"name": "fire-alarm-integration", "description": "Manage fire alarm system integration programs including BACnet connectivity, mass notification, and high-rise system installation."},
    {"name": "fire-protection-engineering", "description": "Provide fire protection engineering support including hydraulic calculations, hazard classification, and NFPA code compliance review."},
    {"name": "marine-fire-protection", "description": "Manage marine fire protection programs including SOLAS compliance, fixed CO2 systems, and IMO type approval processes."},
]

# Domain: Security Systems Manufacturing
skills += [
    {"name": "access-control-manufacturing", "description": "Manage access control system manufacturing including credential reader assembly, controller fabrication, and software integration testing."},
    {"name": "video-surveillance-manufacturing", "description": "Manage video surveillance system manufacturing including IP camera assembly, NVR production, and cybersecurity hardening."},
    {"name": "intrusion-detection-systems", "description": "Manage intrusion detection system manufacturing including PIR sensor assembly, control panel production, and UL 681 compliance."},
    {"name": "security-system-integration", "description": "Manage physical security system integration programs including PSIM platform deployment, enterprise management, and convergence solutions."},
    {"name": "security-system-sales-channel", "description": "Manage security system sales through security dealers, systems integrators, and national installation company programs."},
    {"name": "perimeter-security-systems", "description": "Manage perimeter security product lines including fence detection, microwave sensors, buried cable systems, and LiDAR perimeter management."},
    {"name": "biometric-access-systems", "description": "Develop and manage biometric access systems including fingerprint, iris, and facial recognition product lines with privacy compliance."},
    {"name": "security-system-certification", "description": "Manage security product certification programs including UL listing, FCC Part 15, CE marking, and international compliance."},
    {"name": "smart-lock-manufacturing", "description": "Manage smart lock manufacturing including motorized deadbolt assembly, Bluetooth BLE module integration, and battery life optimization."},
    {"name": "control-room-solutions", "description": "Manage control room solution programs including video wall systems, operator console design, and unified command platform integration."},
]

# Domain: Medical Devices Manufacturing
skills += [
    {"name": "medical-device-manufacturing-ops", "description": "Manage medical device manufacturing operations including clean room assembly, biocompatibility material management, and DHR documentation."},
    {"name": "medical-device-quality-systems", "description": "Implement medical device quality systems including ISO 13485 certification, CAPA programs, and design control procedures."},
    {"name": "medical-device-regulatory-affairs", "description": "Manage medical device regulatory affairs including 510k submissions, PMA applications, CE technical files, and IVDR compliance."},
    {"name": "medical-device-sterilization", "description": "Manage medical device sterilization programs including EO, gamma, and e-beam process validation with SAL assurance programs."},
    {"name": "medical-device-product-dev", "description": "Manage medical device product development from concept through verification, validation, clinical evaluation, and market clearance."},
    {"name": "implantable-device-manufacturing", "description": "Manage implantable device manufacturing including material biocompatibility, clean room operations, and device history record control."},
    {"name": "surgical-instrument-ops", "description": "Manage surgical instrument manufacturing including forging, grinding, polishing, passivation, and set assembly operations."},
    {"name": "medical-device-supply-chain", "description": "Manage medical device supply chains including critical component sourcing, supplier qualification, and supply risk mitigation programs."},
    {"name": "medical-device-post-market", "description": "Manage medical device post-market surveillance including MDR reporting, complaint handling, trend analysis, and field safety actions."},
    {"name": "combination-product-ops", "description": "Manage combination product programs including drug-device primary mode assignment, FDA jurisdiction coordination, and cGMP compliance alignment."},
]

# Domain: Prosthetics & Orthotics Manufacturing
skills += [
    {"name": "prosthetic-device-fabrication", "description": "Manage prosthetic device fabrication including socket design, component fitting, alignment, and patient delivery coordination."},
    {"name": "orthotic-device-manufacturing", "description": "Manage orthotic device manufacturing including custom AFO fabrication, prefabricated stocking, and spinal orthosis production."},
    {"name": "prosthetics-component-sales", "description": "Manage prosthetics and orthotics component sales to practitioners including socket systems, microprocessor knees, and prosthetic feet."},
    {"name": "po-regulatory-compliance", "description": "Navigate prosthetics and orthotics regulatory compliance including HCPCS coding, Medicare coverage policies, and FDA device classification."},
    {"name": "cad-cam-po-fabrication", "description": "Implement CAD/CAM fabrication programs for prosthetics and orthotics including scanning, design software, and CNC carving systems."},
    {"name": "prosthetic-research-development", "description": "Manage prosthetic research and development programs including bionic limb technology, osseointegration systems, and neural interface devices."},
    {"name": "po-practice-management", "description": "Manage prosthetics and orthotics practice operations including patient scheduling, insurance billing, outcomes tracking, and accreditation."},
    {"name": "sports-prosthetics-programs", "description": "Develop sports and activity-specific prosthetic programs including running prostheses, swimming adaptations, and adaptive sports partnerships."},
    {"name": "pediatric-po-programs", "description": "Manage pediatric prosthetics and orthotics programs including growth accommodation, school coordination, and developmental milestone tracking."},
    {"name": "po-digital-workflow", "description": "Implement digital workflow programs for prosthetics and orthotics including 3D scanning, design simulation, and additive manufacturing."},
]

# Domain: Agricultural Equipment Manufacturing
skills += [
    {"name": "tractor-manufacturing-ops", "description": "Manage tractor manufacturing operations including powertrain assembly, hydraulic system integration, ROPS installation, and PDI inspection."},
    {"name": "harvesting-equipment-mfg", "description": "Manage combine harvester and header manufacturing including threshing system assembly, grain handling, and precision farming electronics."},
    {"name": "planting-seeding-equipment", "description": "Manage planting and seeding equipment manufacturing including row unit assembly, meter calibration, seed tube testing, and precision planting."},
    {"name": "sprayer-application-equipment", "description": "Manage sprayer equipment manufacturing including boom fabrication, pump system integration, GPS section control, and NRCS compliance."},
    {"name": "tillage-equipment-manufacturing", "description": "Manage tillage equipment manufacturing including strip-till, disc, and vertical tillage product lines with component sourcing."},
    {"name": "agricultural-equipment-service", "description": "Manage agricultural equipment dealer service operations including field service, warranty administration, and parts depot operations."},
    {"name": "ag-equipment-distribution", "description": "Manage agricultural equipment distribution networks including dealer development, territory management, and equipment display programs."},
    {"name": "ag-precision-technology", "description": "Manage precision agriculture technology integration including GPS guidance, variable rate application, and farm data platform connectivity."},
    {"name": "irrigation-equipment-mfg", "description": "Manage irrigation equipment manufacturing including center pivot fabrication, lateral move systems, drip tape production, and pump stations."},
    {"name": "livestock-equipment-mfg", "description": "Manage livestock handling equipment manufacturing including chutes, panels, waterers, and feeding systems for beef, dairy, and poultry operations."},
]

# Domain: Mining Equipment Manufacturing
skills += [
    {"name": "mining-truck-manufacturing", "description": "Manage mining haul truck manufacturing including chassis fabrication, powertrain integration, body mounting, and commissioning programs."},
    {"name": "mining-drill-manufacturing", "description": "Manage mining drill rig manufacturing including blast hole drill assembly, rotary head systems, and dust suppression integration."},
    {"name": "underground-mining-equipment", "description": "Manage underground mining equipment including load-haul-dump machines, bolter rigs, and continuous miner manufacturing operations."},
    {"name": "mineral-processing-equipment", "description": "Manage mineral processing equipment manufacturing including crushers, mills, flotation cells, and cyclone system fabrication."},
    {"name": "mining-equipment-aftermarket", "description": "Manage mining equipment aftermarket operations including GET programs, wear parts distribution, and component rebuild services."},
    {"name": "mining-automation-systems", "description": "Manage mining automation system programs including autonomous haul trucks, remote dozer operation, and fleet management systems."},
    {"name": "conveyor-mining-systems", "description": "Manage mining conveyor system programs including overland belt conveyors, in-pit crushing conveying, and stacker-reclaimer systems."},
    {"name": "mining-equipment-safety", "description": "Manage mining equipment safety programs including proximity detection, collision avoidance, FOPS/ROPS certification, and MSHA compliance."},
    {"name": "mining-equipment-service", "description": "Manage mining equipment field service operations including exchange component programs, predictive maintenance, and site support contracts."},
    {"name": "hoisting-winding-systems", "description": "Manage mine hoisting and winding system programs including shaft conveyance, hoist drum, and headframe safety compliance."},
]

# Domain: Oil & Gas Equipment Manufacturing
skills += [
    {"name": "wellhead-equipment-manufacturing", "description": "Manage wellhead equipment manufacturing including Christmas tree assembly, casing head fabrication, and API 6A pressure testing."},
    {"name": "blowout-preventer-manufacturing", "description": "Manage blowout preventer manufacturing operations including ram assembly, elastomer qualification, and API 16A load testing."},
    {"name": "downhole-tool-manufacturing", "description": "Manage downhole tool manufacturing including MWD/LWD assembly, completion tool fabrication, and high-pressure testing operations."},
    {"name": "pipeline-equipment-manufacturing", "description": "Manage pipeline equipment manufacturing including pig launcher-receivers, check valves, control valves, and flange management programs."},
    {"name": "subsea-equipment-manufacturing", "description": "Manage subsea equipment manufacturing including ROV tooling, Christmas tree assembly, jumper fabrication, and pressure certification."},
    {"name": "oil-gas-equipment-service", "description": "Manage oil and gas equipment service operations including rental tools, fishing tools, field service dispatch, and equipment reconditioning."},
    {"name": "pressure-vessel-manufacturing", "description": "Manage pressure vessel manufacturing including ASME Sec VIII compliance, nozzle fabrication, NDE inspection, and NBIC registration."},
    {"name": "pumping-unit-manufacturing", "description": "Manage rod pumping unit manufacturing including gear reducer assembly, structural fabrication, dynamic balance, and API 11E compliance."},
    {"name": "oil-gas-valve-manufacturing", "description": "Manage oil and gas valve manufacturing including ball valve, gate valve, and check valve production with API 6D certification."},
    {"name": "oilfield-equipment-distribution", "description": "Manage oilfield equipment distribution including tubular goods, tools, and supplies through pipe yards and supply stores."},
]

# Domain: Power Generation Equipment Manufacturing
skills += [
    {"name": "gas-turbine-manufacturing", "description": "Manage gas turbine manufacturing operations including compressor blade assembly, combustor fabrication, turbine section, and dynamic balancing."},
    {"name": "steam-turbine-manufacturing", "description": "Manage steam turbine manufacturing including rotor forging, blade machining, casing assembly, and performance testing programs."},
    {"name": "reciprocating-engine-manufacturing", "description": "Manage reciprocating engine manufacturing for power generation including block machining, crankshaft assembly, and acceptance testing."},
    {"name": "generator-set-assembly", "description": "Manage generator set assembly operations including base frame fabrication, engine-alternator coupling, enclosure mounting, and load bank testing."},
    {"name": "boiler-manufacturing-ops", "description": "Manage industrial boiler manufacturing including pressure part fabrication, ASME S-stamp compliance, membrane wall assembly, and hydrostatic testing."},
    {"name": "turbine-blade-manufacturing", "description": "Manage turbine blade manufacturing including investment casting, directional solidification, coating application, and tip clearance inspection."},
    {"name": "heat-recovery-steam-generator", "description": "Manage HRSG manufacturing including finned tube fabrication, drum assembly, duct burner integration, and field erection support."},
    {"name": "power-plant-controls", "description": "Manage power plant control system programs including DCS configuration, turbine controls, excitation systems, and grid code compliance."},
    {"name": "power-equipment-service", "description": "Manage power generation equipment service programs including hot section inspections, major overhauls, parts exchange, and performance testing."},
    {"name": "distributed-power-solutions", "description": "Manage distributed power generation solution programs including CHP systems, microgrid integration, and containerized power units."},
]

# Domain: Waste Management Technology
skills += [
    {"name": "waste-collection-optimization", "description": "Optimize waste collection operations using dynamic routing, fill-level IoT sensors, and fleet telematics to reduce collection costs."},
    {"name": "materials-recovery-facility-ops", "description": "Manage materials recovery facility operations including sort line management, commodity quality, bale specification, and market development."},
    {"name": "landfill-operations-management", "description": "Manage landfill operations including cell development, leachate management, gas collection, and regulatory compliance programs."},
    {"name": "waste-to-energy-operations", "description": "Manage waste-to-energy facility operations including combustion systems, air pollution control, ash handling, and energy generation."},
    {"name": "composting-organic-waste-ops", "description": "Manage composting and organic waste processing operations including feedstock management, windrow turning, testing, and end-market sales."},
    {"name": "hazardous-waste-treatment-ops", "description": "Manage hazardous waste treatment facility operations including incineration, stabilization, physical-chemical treatment, and RCRA compliance."},
    {"name": "waste-data-analytics", "description": "Deploy waste management analytics platforms including diversion rate tracking, generator benchmarking, and sustainability reporting."},
    {"name": "circular-economy-programs", "description": "Develop circular economy programs including take-back systems, upcycling partnerships, industrial symbiosis networks, and EPR compliance."},
    {"name": "e-waste-recycling-ops", "description": "Manage e-waste recycling operations including device depopulation, shredding, metal recovery, and R2 or e-Stewards certification."},
    {"name": "waste-contract-management", "description": "Manage waste service contracts including municipal solid waste franchise agreements, industrial service contracts, and disposal manifesting."},
]

# Domain: Water Treatment Technology Manufacturing
skills += [
    {"name": "water-treatment-equipment-mfg", "description": "Manage water treatment equipment manufacturing including pressure vessel fabrication, membrane module assembly, and system skid integration."},
    {"name": "membrane-system-manufacturing", "description": "Manage membrane system manufacturing including RO, UF, and NF element production, module potting, and integrity testing."},
    {"name": "ion-exchange-resin-production", "description": "Manage ion exchange resin production including polymerization, functionalization, bead size control, and capacity testing."},
    {"name": "water-chemical-treatment-ops", "description": "Manage water treatment chemical programs including scale inhibitors, biocides, coagulants, and specialty chemical application support."},
    {"name": "uv-disinfection-systems", "description": "Manage UV disinfection system programs including lamp module manufacturing, dose validation, and bioassay performance verification."},
    {"name": "desalination-plant-equipment", "description": "Manage desalination plant equipment programs including SWRO systems, energy recovery devices, and high-pressure pump systems."},
    {"name": "water-treatment-controls", "description": "Manage water treatment controls integration including SCADA programming, chemical dosing automation, and remote monitoring platforms."},
    {"name": "water-testing-equipment", "description": "Manage water quality testing equipment programs including portable analyzers, online sensors, and laboratory instrument validation."},
    {"name": "industrial-water-treatment-svcs", "description": "Manage industrial water treatment service programs including cooling water treatment, boiler water chemistry, and wastewater treatment."},
    {"name": "water-treatment-engineering-svcs", "description": "Provide water treatment engineering services including pilot testing, full-scale design, treatability studies, and technology selection."},
]

# Domain: Veterinary Equipment Manufacturing
skills += [
    {"name": "veterinary-diagnostic-equipment", "description": "Manage veterinary diagnostic equipment programs including in-clinic analyzers, digital X-ray, and ultrasound systems with regulatory clearance."},
    {"name": "veterinary-surgical-equipment", "description": "Manage veterinary surgical equipment manufacturing including anesthesia machines, surgical tables, and monitoring systems."},
    {"name": "large-animal-equipment-ops", "description": "Manage large animal veterinary equipment programs including portable X-ray, chute-mounted ultrasound, and herd health monitoring systems."},
    {"name": "veterinary-laboratory-equipment", "description": "Manage veterinary laboratory equipment programs including hematology analyzers, urinalysis systems, and PCR diagnostic platforms."},
    {"name": "companion-animal-device-sales", "description": "Manage companion animal device sales programs through veterinary distribution, practice groups, and veterinary schools."},
    {"name": "veterinary-imaging-systems", "description": "Manage veterinary imaging system programs including MRI, CT scanner, and nuclear medicine for specialist referral hospitals."},
    {"name": "aquatic-animal-health-equipment", "description": "Manage aquatic and zoo animal health equipment programs including water quality analyzers, restraint systems, and transport solutions."},
    {"name": "vet-equipment-compliance", "description": "Navigate veterinary equipment regulatory compliance including FDA CDRH oversight, USDA product approvals, and international registration."},
    {"name": "vet-equipment-service-ops", "description": "Manage veterinary equipment service operations including preventive maintenance, repair depot, and field service engineer programs."},
    {"name": "telemedicine-vet-platforms", "description": "Manage veterinary telemedicine platform programs including remote consultation tools, wearable pet monitors, and teleconsultation services."},
]

# Domain: Rehabilitation Equipment Manufacturing
skills += [
    {"name": "physical-therapy-equipment-mfg", "description": "Manage physical therapy equipment manufacturing including electrotherapy devices, ultrasound units, and traction table assembly."},
    {"name": "exercise-rehabilitation-equipment", "description": "Manage rehabilitation exercise equipment programs including functional trainers, balance systems, and isokinetic testing devices."},
    {"name": "mobility-aid-manufacturing", "description": "Manage mobility aid manufacturing including manual and power wheelchair assembly, rollator production, and FDA QSR compliance."},
    {"name": "hospital-bed-manufacturing", "description": "Manage hospital bed and stretcher manufacturing including frame fabrication, motor integration, surface compatibility, and IEC 60601 compliance."},
    {"name": "rehab-robotics-systems", "description": "Manage rehabilitation robotics programs including exoskeleton gait training, upper extremity robotics, and neurofeedback systems."},
    {"name": "hydrotherapy-equipment-ops", "description": "Manage hydrotherapy equipment programs including aquatic therapy pools, whirlpool systems, and underwater treadmill manufacturing."},
    {"name": "respiratory-therapy-devices", "description": "Manage respiratory therapy device programs including ventilators, nebulizers, oxygen concentrators, and CPAP devices."},
    {"name": "patient-lift-transfer-systems", "description": "Manage patient lift and transfer system programs including ceiling lift installation, portable hoyer lift production, and safe patient handling."},
    {"name": "rehab-equipment-distribution", "description": "Manage rehabilitation equipment distribution through DME dealer networks, hospital supply contracts, and HME specialty channels."},
    {"name": "rehab-equipment-reimbursement", "description": "Manage rehabilitation equipment reimbursement programs including HCPCS coding strategy, LCD compliance, and payer policy engagement."},
]

# Domain: Smart Home Devices Manufacturing
skills += [
    {"name": "smart-home-hub-manufacturing", "description": "Manage smart home hub and gateway manufacturing including processor board assembly, RF module integration, and FCC/IC certification."},
    {"name": "smart-thermostat-manufacturing", "description": "Manage smart thermostat manufacturing including sensor assembly, display integration, wireless radio testing, and ENERGY STAR compliance."},
    {"name": "smart-lighting-control-mfg", "description": "Manage smart lighting control device manufacturing including dimmer assembly, wireless protocol integration, and electrical safety testing."},
    {"name": "smart-security-device-mfg", "description": "Manage smart home security device manufacturing including smart lock, video doorbell, and indoor camera assembly and certification."},
    {"name": "smart-appliance-platform", "description": "Manage smart appliance platform programs including connectivity module integration, cloud service API, and voice assistant certification."},
    {"name": "iot-device-firmware-ops", "description": "Manage IoT device firmware programs including OTA update infrastructure, version management, and security patch deployment."},
    {"name": "smart-home-ecosystem-mgmt", "description": "Manage smart home ecosystem integration programs including Matter protocol compliance, platform certification, and interoperability testing."},
    {"name": "smart-home-device-sales", "description": "Manage smart home device sales through retail channels, home builders, and custom installation professional programs."},
    {"name": "smart-home-data-privacy", "description": "Manage smart home device data privacy programs including user consent management, data minimization, and privacy regulation compliance."},
    {"name": "smart-home-customer-support", "description": "Manage smart home device customer support operations including connectivity troubleshooting, app support, and warranty replacement."},
]

# Domain: Wearables Manufacturing
skills += [
    {"name": "fitness-tracker-manufacturing", "description": "Manage fitness tracker manufacturing including optical heart rate sensor assembly, IMU integration, battery management, and wrist band fitting."},
    {"name": "smartwatch-manufacturing-ops", "description": "Manage smartwatch manufacturing operations including display module assembly, crown mechanism, speaker receiver, and water resistance testing."},
    {"name": "wearable-sensor-development", "description": "Develop wearable biosensor solutions including PPG, ECG, SpO2, and EDA sensor integration with algorithm development."},
    {"name": "medical-wearable-manufacturing", "description": "Manage medical-grade wearable device manufacturing including cardiac monitoring patches, CGM devices, and FDA clearance management."},
    {"name": "ar-vr-headset-manufacturing", "description": "Manage AR/VR headset manufacturing including display optic assembly, IMU calibration, and eye tracking integration programs."},
    {"name": "wearable-battery-management", "description": "Manage wearable device battery programs including custom LiPo cell sourcing, charge management IC integration, and safe charging certification."},
    {"name": "wearable-firmware-development", "description": "Manage wearable firmware development programs including real-time OS, sensor fusion algorithms, and low-power mode optimization."},
    {"name": "wearable-device-sales", "description": "Manage wearable device sales through consumer electronics retail, e-commerce, and enterprise wellness program channels."},
    {"name": "smart-textile-wearables", "description": "Develop smart textile wearable programs including conductive yarn integration, embedded sensor washability, and garment connectivity."},
    {"name": "wearable-regulatory-compliance", "description": "Navigate wearable device regulatory compliance including FCC, Bluetooth SIG certification, SAR testing, and EU Radio Equipment Directive."},
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
