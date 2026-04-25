
import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # Advanced Bioinformatics Tools
    ('cellranger-analysis', 'Cell Ranger analysis - 10x Genomics, scRNA-seq, ATAC-seq, multi-ome, aggr, pipelines'),
    ('seurat-advanced', 'Seurat advanced - clustering, dimensionality reduction, integration, spatial, multi-modal'),
    ('deseq2-advanced', 'DESeq2 advanced - differential expression, GLM, size factors, shrinkage, batch effects'),
    ('alphafold-proteins', 'AlphaFold protein structure - structure prediction, MSA, templates, ColabFold, distillation'),
    ('bioconductor-workflows', 'Bioconductor workflows - R/Bioc, GenomicRanges, SummarizedExperiment, annotation'),
    # Advanced Quantum Frameworks
    ('qiskit-nature', 'Qiskit Nature - molecular simulations, VQE, quantum chemistry, excited states, protein'),
    ('cirq-advanced', 'Cirq advanced - circuits, devices, simulators, noise models, QAOA, compilation'),
    ('pennylane-advanced', 'PennyLane advanced - hardware backends, quantum gradients, circuit compilation, noise'),
    ('cuda-quantum', 'CUDA Quantum - GPU-accelerated quantum simulation, Nvidia cuQuantum, hybrid execution'),
    ('qasm-programming', 'OpenQASM programming - quantum assembly language, gates, classical control, QASM 3.0'),
    # Advanced Numerical Computing
    ('julia-hpc', 'Julia HPC - MPI, distributed computing, GPU programming, SIMD, performance profiling'),
    ('fortran-advanced', 'Modern Fortran - coarrays, do concurrent, GPU offloading, interoperability, HPC'),
    ('opencl-programming', 'OpenCL programming - kernels, memory model, work groups, SPIR-V, portability'),
    ('cuda-advanced', 'CUDA advanced - shared memory, streams, cooperative groups, NCCL, custom kernels'),
    ('openmp-advanced', 'OpenMP advanced - tasking, target offload, SIMD, cancellation, nested parallelism'),
    # Advanced AI Research Frameworks
    ('jax-advanced', 'JAX advanced - jit, grad, vmap, pmap, custom derivatives, PRNG, device mesh'),
    ('flax-advanced', 'Flax NNX advanced - modules, training, checkpointing, optimization, multi-device'),
    ('equinox-ml', 'Equinox JAX - functional neural networks, JIT-compatible, filtering, serialization'),
    ('haiku-deepmind', 'Haiku DeepMind - functional Sonnet, transform, lift, stateful, checkpointing'),
    ('trax-framework', 'Trax framework - layers, models, training, data pipeline, fast attention, RL'),
    # Advanced Simulation and Modeling
    ('openfoam-cfd', 'OpenFOAM CFD - mesh generation, solvers, post-processing, turbulence, multiphase'),
    ('ansys-simulation', 'ANSYS simulation - FEA, CFD, structural, thermal, electromagnetics, Python scripting'),
    ('gromacs-md', 'GROMACS molecular dynamics - force fields, topology, MDP files, analysis, GPU'),
    ('lammps-md', 'LAMMPS molecular dynamics - input scripts, pair styles, fixes, computes, parallel'),
    ('simnibs-fem', 'SimNIBS brain FEM - TMS modeling, tDCS, electrode placement, neuronavigation'),
    # Advanced Hardware Programming
    ('verilator-simulation', 'Verilator - RTL simulation, C++/SystemC, coverage, linting, waveforms, optimization'),
    ('systemverilog-advanced', 'SystemVerilog advanced - interfaces, classes, assertions, coverage, random constraints'),
    ('chisel-hdl', 'Chisel HDL - Scala-based hardware, generators, bundles, modules, testers, FIRRTL'),
    ('hls-synthesis', 'HLS synthesis - Vivado HLS, Intel HLS, C++ to RTL, pragmas, pipelines, interfaces'),
    ('risc-v-processor', 'RISC-V processor design - ISA extensions, RVFI, verification, implementation, FPGA'),
    # Advanced Climate and Earth Science
    ('era5-climate', 'ERA5 climate data - CDS API, xarray, Zarr, regridding, climatology, extreme events'),
    ('cmip6-models', 'CMIP6 climate models - intake-esm, ESGF, model comparison, projection, downscaling'),
    ('xarray-advanced', 'xarray advanced - dask integration, custom backends, indexing, broadcasting, CF conventions'),
    ('cartopy-mapping', 'Cartopy mapping - projections, features, gridlines, rasterio, satellite imagery, GRIB'),
    ('metpy-analysis', 'MetPy meteorological analysis - thermodynamics, kinematics, cross-sections, BUFR, METAR'),
    # Advanced Space and Astronomy
    ('astropy-advanced', 'Astropy advanced - FITS, WCS, coordinates, photometry, spectroscopy, cosmology'),
    ('sunpy-solar', 'SunPy solar physics - FITS, coordinates, maps, timeseries, SOHO, SDO, Hinode'),
    ('gammapy-analysis', 'Gammapy - gamma-ray astronomy, data reduction, spectral/spatial/temporal analysis'),
    ('healpy-sphere', 'HEALPix/healpy - spherical pixelization, power spectra, CMB analysis, alm coefficients'),
    ('skyfield-ephemeris', 'Skyfield ephemeris - star positions, planet orbits, earth satellites, time systems'),
    # Advanced Materials Science
    ('ase-materials', 'ASE materials - atoms objects, calculators, DFT, NEB, MD, optimizers, databases'),
    ('pymatgen-advanced', 'pymatgen advanced - structure manipulation, phase diagrams, electronic structure, MP'),
    ('atomistic-sim', 'Atomistic simulation - VASP, Quantum ESPRESSO, CP2K, ABINIT workflow integration'),
    ('crystal-analysis', 'Crystal structure analysis - CIF files, symmetry operations, diffraction, Rietveld'),
    ('ml-potentials', 'ML interatomic potentials - MLIP, GAP, NNP, ACE, MACE, training, validation, MD'),
    # Advanced Economics and Social Science
    ('econometrics-advanced', 'Econometrics advanced - IV estimation, DID, RDD, synthetic control, panel data'),
    ('agent-based-modeling', 'Agent-based modeling - Mesa, NetLogo, SimPy, emergence, calibration, validation'),
    ('causal-discovery', 'Causal discovery - PC algorithm, FCI, LiNGAM, GES, NOTEARS, causal graphs'),
    ('network-analysis', 'Network analysis - NetworkX advanced, community detection, centrality, temporal networks'),
    ('text-mining-social', 'Text mining social science - NLP for surveys, discourse analysis, topic modeling'),
    # Advanced Healthcare Informatics
    ('fhir-advanced', 'FHIR advanced - R4/R5, SMART on FHIR, subscriptions, CQL, quality measures, bulk'),
    ('clinical-nlp', 'Clinical NLP - named entity recognition, de-identification, ICD coding, SNOMED, UMLS'),
    ('ehr-analytics', 'EHR analytics - OMOP CDM, OHDSI tools, phenotyping, cohort definitions, population'),
    ('medical-imaging-ml', 'Medical imaging ML - DICOM, nnU-Net, segmentation, classification, registration'),
    ('pharma-informatics', 'Pharmaceutical informatics - ADMET prediction, virtual screening, docking, KNIME'),
    # Advanced Legal Technology
    ('contract-nlp', 'Contract NLP - clause extraction, obligation detection, risk scoring, comparison, LLM'),
    ('legal-knowledge-graph', 'Legal knowledge graph - statute linking, case citation, regulatory mapping, ontology'),
    ('ediscovery-ml', 'eDiscovery ML - document review, relevance prediction, privilege detection, clustering'),
    ('regulatory-text-analysis', 'Regulatory text analysis - requirement extraction, change detection, compliance mapping'),
    ('ip-analytics', 'IP analytics - patent claim parsing, prior art search, freedom to operate, portfolio'),
    # Advanced Supply Chain Technology
    ('demand-forecasting-advanced', 'Demand forecasting advanced - hierarchical, probabilistic, ML, deep learning, M5'),
    ('supply-chain-optimization', 'Supply chain optimization - MILP, stochastic, robust, multi-echelon, JIT'),
    ('route-optimization', 'Route optimization - VRP, CVRP, TSP, OR-Tools, multi-depot, time windows, real-time'),
    ('inventory-optimization', 'Inventory optimization - safety stock, EOQ, newsvendor, multi-item, stochastic'),
    ('warehouse-automation', 'Warehouse automation - robotics, WMS integration, path planning, bin picking, RFID'),
    # Advanced Energy Systems
    ('grid-optimization', 'Grid optimization - OPF, unit commitment, economic dispatch, DER integration, storage'),
    ('renewable-energy-ml', 'Renewable energy ML - solar irradiance, wind power, load forecasting, digital twins'),
    ('energy-storage-systems', 'Energy storage systems - battery management, state of charge, thermal, degradation'),
    ('smart-grid-iot', 'Smart grid IoT - AMI, PMU data, SCADA integration, demand response, grid edge'),
    ('carbon-credit-systems', 'Carbon credit systems - monitoring, reporting, verification, tokenization, registry'),
    # Advanced Agriculture Technology
    ('precision-farming', 'Precision farming - satellite imagery, soil sensors, variable rate, NDVI, drone mapping'),
    ('crop-disease-detection', 'Crop disease detection - computer vision, multispectral, early warning, treatment'),
    ('agri-iot', 'Agricultural IoT - sensor networks, weather stations, irrigation control, livestock tracking'),
    ('food-traceability', 'Food traceability - blockchain, GS1 standards, farm-to-fork, recall management'),
    ('climate-smart-agriculture', 'Climate-smart agriculture - adaptation models, carbon sequestration, water use'),
    # Advanced Media and Entertainment Technology
    ('video-game-ai', 'Video game AI - behavior trees, GOAP, navigation mesh, procedural content, ML agents'),
    ('vfx-pipeline', 'VFX pipeline - USD, OpenEXR, render farm, color management, shot tracking, review'),
    ('music-production-ai', 'Music production AI - stem separation, generative composition, mixing, mastering'),
    ('broadcast-technology', 'Broadcast technology - SMPTE, live production, streaming, NDI, SDI, playout'),
    ('metaverse-architecture', 'Metaverse architecture - virtual worlds, avatar systems, economy, governance, physics'),
    # Advanced Transportation Technology
    ('autonomous-vehicles', 'Autonomous vehicles - sensor fusion, path planning, SLAM, safety, simulation, HD maps'),
    ('traffic-management-ai', 'Traffic management AI - signal control, incident detection, flow optimization, V2X'),
    ('fleet-telematics', 'Fleet telematics - GPS tracking, driver behavior, predictive maintenance, fuel optimization'),
    ('aviation-systems', 'Aviation systems - FMS, ATC automation, predictive maintenance, fuel optimization'),
    ('maritime-technology', 'Maritime technology - vessel tracking, route optimization, port logistics, emissions'),
    # Advanced Insurance Technology
    ('actuarial-modeling', 'Actuarial modeling - mortality tables, claims reserving, pricing models, risk aggregation'),
    ('claims-automation', 'Claims automation - OCR, damage assessment, fraud detection, straight-through processing'),
    ('underwriting-ai', 'Underwriting AI - risk scoring, document analysis, data enrichment, pricing optimization'),
    ('insurtech-platform', 'InsurTech platform - policy management, billing, reinsurance, regulatory, embedded'),
    ('catastrophe-modeling', 'Catastrophe modeling - natural hazard, exposure, vulnerability, financial impact, RMS'),
    # Advanced Telecommunications
    ('5g-network-slicing', '5G network slicing - RAN slicing, core network, QoS, NSSF, isolation, orchestration'),
    ('network-function-virtualization', 'NFV advanced - VNF lifecycle, MANO, ETSI, OpenStack, performance, testing'),
    ('telecom-data-analytics', 'Telecom data analytics - CDR analysis, network KPIs, customer analytics, churn'),
    ('oran-architecture', 'O-RAN architecture - RIC, xApps, rApps, fronthaul, open interfaces, cloudRAN'),
    ('isp-automation', 'ISP automation - network provisioning, fault management, performance, YANG, NETCONF'),
    # Advanced Defense and Government Technology
    ('c2-systems', 'Command and control systems - messaging, situational awareness, decision support, resilience'),
    ('geoint-analysis', 'GEOINT analysis - satellite imagery, change detection, object classification, 3D modeling'),
    ('cyber-defense-advanced', 'Cyber defense advanced - threat intelligence, attribution, hunting, deception, resilience'),
    ('secure-communications', 'Secure communications - end-to-end encryption, key management, side-channel, TEMPEST'),
    ('critical-infrastructure', 'Critical infrastructure protection - ICS/SCADA, OT security, resilience, recovery'),
    # Advanced Urban Technology
    ('smart-city-platform', 'Smart city platform - data platform, IoT integration, digital twin, citizen services'),
    ('gis-urban-planning', 'GIS for urban planning - zoning analysis, 3D city models, accessibility, simulation'),
    ('mobility-as-a-service', 'Mobility as a service - multimodal journey planning, ticketing, data sharing, API'),
    ('building-automation', 'Building automation systems - BACnet, HVAC, access control, energy management, BIM'),
    ('digital-twin-cities', 'Digital twin cities - CityGML, IFC, simulation, visualization, data fusion, analytics'),
    # Advanced Robotics Applications
    ('surgical-robotics', 'Surgical robotics - kinematics, force control, registration, tracking, safety, haptics'),
    ('collaborative-robots', 'Collaborative robots - force/torque sensing, compliance, safety, programming, vision'),
    ('drone-swarms', 'Drone swarm systems - formation control, task allocation, communication, safety, simulation'),
    ('underwater-robotics', 'Underwater robotics - AUV, ROV, sonar, acoustic communication, navigation, pressure'),
    ('space-robotics', 'Space robotics - teleoperation, manipulation, SLAM in space, fault tolerance, testing'),
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
