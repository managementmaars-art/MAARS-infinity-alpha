
import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # Biotechnology and life sciences
    ('crispr-technology', 'CRISPR technology - Cas9, prime editing, base editing, delivery, off-targets, screens, therapeutic'),
    ('synthetic-biology', 'Synthetic biology - genetic circuits, BioBricks, iGEM, metabolic engineering, chassis organisms'),
    ('bioinformatics-pipelines', 'Bioinformatics pipelines - Snakemake, Nextflow, CWL, WDL, containers, cloud, benchmarking'),
    ('single-cell-analysis', 'Single cell analysis - scRNA-seq, ATAC-seq, spatial, Seurat, Scanpy, trajectory, cell communication'),
    ('proteomics-advanced', 'Proteomics advanced - DIA, DDA, TMT, IP-MS, structural, cryo-EM data processing, alphafold'),
    ('metabolomics-advanced', 'Metabolomics advanced - untargeted, targeted, NMR, GC-MS, fluxomics, pathway reconstruction'),
    ('epigenomics', 'Epigenomics - ATAC-seq, ChIP-seq, bisulfite, Hi-C, chromatin accessibility, regulatory elements'),
    ('metagenomics', 'Metagenomics - shotgun sequencing, assembly, binning, taxonomic profiling, functional annotation'),
    ('flow-cytometry', 'Flow cytometry - panels, gating, compensation, spectral, mass cytometry, analysis software'),
    ('microscopy-imaging', 'Microscopy imaging - confocal, super-resolution, STORM, PALM, TIRF, light sheet, analysis'),
    ('drug-discovery-informatics', 'Drug discovery informatics - target identification, ADMET, generative chemistry, virtual screening'),
    ('bioprocess-development', 'Bioprocess development - fermentation, cell culture, PAT, scale-up, DOE, bioreactor, control'),
    ('cell-therapy-manufacturing', 'Cell therapy manufacturing - CAR-T, iPSC, cGMP, process development, quality, release testing'),
    ('gene-therapy-vectors', 'Gene therapy vectors - AAV, lentivirus, mRNA, lipid nanoparticles, tropism, immunogenicity'),
    ('organ-chip-technology', 'Organ-on-chip technology - microfluidics, barrier function, co-culture, disease modeling'),
    ('bioprinting', 'Bioprinting - bioinks, hydrogels, extrusion, inkjet, laser-assisted, vascularization, tissue engineering'),
    ('protein-engineering', 'Protein engineering - directed evolution, rational design, computational, antibody engineering'),
    ('synthetic-genomics', 'Synthetic genomics - DNA synthesis, genome assembly, whole-genome synthesis, chromosome design'),
    # Nanotechnology
    ('nanomaterials', 'Nanomaterials - nanoparticles, CNTs, graphene, quantum dots, characterization, synthesis, safety'),
    ('nanofabrication', 'Nanofabrication - electron beam lithography, EUV, self-assembly, soft lithography, atomic layer deposition'),
    ('nanoelectronics', 'Nanoelectronics - transistor scaling, FinFET, GAA, 2D materials, CFET, power delivery'),
    ('quantum-dots-tech', 'Quantum dots technology - synthesis, optical properties, displays, bioimaging, photovoltaics'),
    # Robotics specializations
    ('soft-robotics', 'Soft robotics - pneumatic actuators, shape memory, dielectric elastomers, fabrication, control'),
    ('micro-robotics', 'Micro-robotics - MEMS, micromanipulation, biological propulsion, medical applications, scaling'),
    ('bio-inspired-robotics', 'Bio-inspired robotics - locomotion, tensegrity, swarm, morphological computation, muscles'),
    ('collaborative-robotics', 'Collaborative robotics - cobots, force control, HRI, safety, UR, KUKA, ABB, programming'),
    ('surgical-robotics', 'Surgical robotics - da Vinci, haptics, teleoperation, visualization, miniaturization, registration'),
    ('underwater-robotics', 'Underwater robotics - AUV, ROV, SLAM, acoustic comms, buoyancy, hydrodynamics, manipulation'),
    ('aerial-robotics', 'Aerial robotics - multirotor, fixed-wing, tiltrotor, VTOL, formation flight, fault tolerance'),
    ('legged-robotics', 'Legged robotics - bipedal, quadrupedal, gait, balance, terrain adaptation, Boston Dynamics'),
    ('manipulation-advanced', 'Robot manipulation advanced - grasping, dexterous hands, deformable objects, learning'),
    ('robot-perception', 'Robot perception - SLAM, point clouds, semantic mapping, object recognition, pose estimation'),
    ('robot-learning', 'Robot learning - imitation, RL, sim-to-real, data augmentation, foundation models, RLHF'),
    # Quantum computing frameworks
    ('qiskit-advanced', 'Qiskit advanced - circuits, pulse, runtime, error mitigation, transpiler, backends, algorithms'),
    ('cirq-advanced', 'Cirq advanced - circuits, ops, sweeps, simulators, noise models, cloud, QAOA, VQE'),
    ('pennylane-advanced', 'PennyLane advanced - QML, differentiable, plugins, templates, transforms, hardware'),
    ('q-sharp', 'Q# programming - qubits, operations, functors, libraries, simulators, Azure Quantum, algorithms'),
    ('braket-advanced', 'Amazon Braket advanced - circuits, simulators, hardware, hybrid jobs, Orquestra, noise'),
    ('quantum-algorithms', 'Quantum algorithms - Grover, Shor, QAOA, VQE, QPE, quantum simulation, error correction'),
    ('quantum-error-correction', 'Quantum error correction - surface codes, stabilizer, fault tolerance, threshold, decoders'),
    ('quantum-networking', 'Quantum networking - entanglement distribution, quantum repeaters, QKD, Bell states, routing'),
    ('quantum-simulation', 'Quantum simulation - Hamiltonian simulation, digital, analog, variational, chemistry, physics'),
    ('quantum-optimization', 'Quantum optimization - QUBO, Ising, D-Wave, annealing, QAOA, combinatorial, benchmark'),
    # Digital government and civic tech
    ('digital-government', 'Digital government - service design, agile delivery, GaaS, GDS, cloud.gov, cPaaS, identity'),
    ('open-data-portals', 'Open data portals - CKAN, Socrata, metadata standards, APIs, data quality, licensing'),
    ('e-voting-systems', 'E-voting systems - security, auditability, accessibility, end-to-end verification, risk limiting'),
    ('civic-tech-platforms', 'Civic tech platforms - participatory budgeting, consultation, 311, Fix My Street, Alaveteli'),
    ('public-sector-ai', 'Public sector AI - explainability, fairness, procurement, oversight, automation, risk assessment'),
    ('smart-city-platforms', 'Smart city platforms - data integration, IoT, dashboards, mobility, energy, safety, privacy'),
    ('digital-identity-gov', 'Government digital identity - eIDAS, Login.gov, GSMA, biometrics, PKI, interoperability'),
    ('regulatory-technology', 'RegTech - automated compliance, regulatory reporting, NLP for regulation, sandbox, API'),
    # Personal productivity and knowledge management
    ('obsidian-pkm', 'Obsidian PKM - graph view, plugins, templates, Dataview, Templater, canvas, sync, vault'),
    ('notion-advanced', 'Notion advanced - databases, relations, rollups, formulas, API, automations, AI, templates'),
    ('roam-research', 'Roam Research - block references, queries, graph, CSS, JS extensions, daily notes'),
    ('logseq-advanced', 'Logseq advanced - graph, queries, templates, properties, namespaces, plugins, markdown'),
    ('second-brain-methodology', 'Second Brain methodology - PARA, CODE, capture, organize, distill, express, Tiago Forte'),
    ('zettelkasten-method', 'Zettelkasten method - atomic notes, linking, emergence, evergreen notes, note types'),
    ('task-management-systems', 'Task management systems - GTD, time blocking, Eisenhower, deep work, review cycles'),
    ('personal-crm', 'Personal CRM - contact tracking, follow-up systems, Clay, Monica, relationship mapping'),
    ('life-logging-tech', 'Life logging technology - quantified self, Exist, Nomie, data aggregation, visualization'),
    ('knowledge-base-tools', 'Knowledge base tools - Confluence, Notion, Guru, Tettra, search, governance, adoption'),
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
