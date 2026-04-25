
import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # Specialized networking deep
    ('dpdk-networking', 'DPDK networking - poll-mode drivers, hugepages, mbuf, ring buffers, pipeline, crypto offload'),
    ('xdp-ebpf-networking', 'XDP eBPF networking - packet processing, load balancing, DDoS mitigation, tc BPF programs'),
    ('rdma-infiniband', 'RDMA/InfiniBand - verbs, RoCE, iWARP, memory registration, completion queues, MPI over RDMA'),
    ('optical-networking', 'Optical networking - DWDM, coherent optics, CFP, QSFP, wavelength routing, OTN, ROADM'),
    ('5g-ran-architecture', '5G RAN architecture - gNB, CU/DU split, O-RAN, fronthaul, beamforming, NR protocols, PDCP'),
    ('satellite-communications', 'Satellite communications - LEO constellations, DVB-S2, link budgets, ground stations, handover'),
    ('software-defined-wan', 'SD-WAN implementation - underlay/overlay, vEdge, ZTP, policies, application-aware routing'),
    ('network-programmability', 'Network programmability - NETCONF, YANG, RESTCONF, gNMI, OpenConfig, pyATS, Ansible'),
    ('segment-routing', 'Segment routing - SRv6, MPLS-SR, traffic engineering, TI-LFA, Flex-Algo, PCE, SRTE'),
    ('p4-programming', 'P4 programming - programmable data planes, P4Runtime, PSA, behavioral model, p4c compiler'),
    # Database internals deep
    ('btree-internals', 'B-tree internals - page layout, splits, compaction, LSM trees, write amplification, InnoDB'),
    ('lsm-tree-advanced', 'LSM tree advanced - compaction strategies, bloom filters, leveled vs tiered, RocksDB tuning'),
    ('mvcc-advanced', 'MVCC advanced - snapshot isolation, write skew, SSI, PostgreSQL MVCC, garbage collection'),
    ('write-ahead-log', 'Write-ahead log - WAL design, checkpointing, recovery, replication, Raft log, Paxos log'),
    ('distributed-transactions', 'Distributed transactions - 2PC, 3PC, saga, compensating transactions, TCC, CRDB'),
    ('query-planner-advanced', 'Query planner advanced - cardinality estimation, join ordering, cost models, statistics'),
    ('vector-index-tuning', 'Vector index tuning - HNSW construction, ef_construction, M parameter, IVFPQ, quantization'),
    ('timescaledb-advanced', 'TimescaleDB advanced - hypertables, continuous aggregates, compression, distributed, retention'),
    ('citus-postgres', 'Citus distributed PostgreSQL - sharding, reference tables, columnar, coordinator, workers'),
    ('duckdb-advanced', 'DuckDB advanced - vectorized execution, columnar storage, extensions, ADBC, Parquet scanning'),
    # Specialized industry verticals
    ('aerospace-software', 'Aerospace software - DO-178C, ARINC 429, MIL-STD-1553, simulation, avionics certification'),
    ('nuclear-technology', 'Nuclear technology - reactor simulation, neutronics, safety systems, OpenMC, SCALE, MCNP'),
    ('mining-software', 'Mining software - mine planning, drill & blast simulation, fleet management, grade control'),
    ('maritime-technology', 'Maritime technology - NMEA 2000, AIS, ECDIS, vessel management, cargo tracking, BMS'),
    ('railway-systems', 'Railway systems - ERTMS, signaling, interlocking, ETCS, trackside software, train control'),
    ('electric-grid-advanced', 'Electric grid advanced - SCADA, EMS, PSCAD, PowerWorld, grid stability, protection relay'),
    ('water-infrastructure', 'Water infrastructure - SCADA, hydraulic modeling, EPANET, leak detection, smart meters'),
    ('oil-gas-software', 'Oil and gas software - reservoir simulation, ECLIPSE, petrel, pipeline SCADA, production opt'),
    ('pharmaceutical-manufacturing', 'Pharmaceutical manufacturing - MES, batch records, GMP compliance, PAT, serialization'),
    ('automotive-embedded', 'Automotive embedded - AUTOSAR Classic, Adaptive AUTOSAR, SOME/IP, Ethernet, OBD2, ADAS'),
    # Game development specialized
    ('game-physics-engine', 'Game physics engine - rigid body dynamics, collision detection, constraints, PhysX, Bullet'),
    ('game-graphics-rendering', 'Game graphics rendering - deferred shading, PBR, ray tracing, LOD, occlusion culling'),
    ('game-audio-advanced', 'Game audio advanced - spatial audio, Wwise, FMOD, procedural audio, dynamic mixing'),
    ('game-networking-advanced', 'Game networking advanced - rollback netcode, state synchronization, prediction, lag comp'),
    ('game-ai-behavior-trees', 'Game AI behavior trees - BT nodes, blackboard, decorators, utility AI, GOAP, HTN'),
    ('procedural-content-gen', 'Procedural content generation - noise functions, L-systems, WFC, dungeon gen, terrain'),
    ('game-engine-internals', 'Game engine internals - ECS architecture, scene graphs, render pipelines, job systems'),
    ('vr-haptics', 'VR haptics - force feedback, tactile feedback, haptic APIs, OpenHaptics, OpenXR haptics'),
    ('game-analytics-platform', 'Game analytics platform - event tracking, funnels, A/B tests, LTV, churn prediction'),
    ('live-service-games', 'Live service games - live ops, season passes, content pipeline, telemetry, monetization'),
    # Audio/DSP programming
    ('audio-dsp-advanced', 'Audio DSP advanced - filter design, FFT, convolution, pitch shifting, spectral processing'),
    ('juce-framework', 'JUCE framework - audio plugins, VST3, AU, AAX, MIDI, CLAP, audio processing graph'),
    ('supercollider-advanced', 'SuperCollider advanced - server architecture, UGens, patterns, JITlib, live coding'),
    ('max-msp-advanced', 'Max/MSP advanced - gen~, jitter, MC, RNBO export, external development, polybuffer'),
    ('webrtc-audio', 'WebRTC audio - codec negotiation, Opus, echo cancellation, noise suppression, mixing'),
    ('spatial-audio-advanced', 'Spatial audio advanced - ambisonics, binaural rendering, HRTF, object-based audio, MPEG-H'),
    ('digital-audio-workstation', 'DAW plugin development - ReaScript, Live API, Logic Environment, Ableton Max'),
    ('audio-ml-synthesis', 'Audio ML synthesis - differentiable DSP, DDSP, neural audio, vocoder, timbre transfer'),
    ('midi-advanced', 'MIDI advanced - MPE, MIDI 2.0, sysex, DAWless setup, generative MIDI, clock sync'),
    ('room-acoustics', 'Room acoustics modeling - FEM/BEM acoustic simulation, reverberation, room correction'),
    # Numerical methods and simulation
    ('finite-difference-methods', 'Finite difference methods - explicit/implicit, stability, CFL condition, FDTD, heat equation'),
    ('monte-carlo-simulation', 'Monte Carlo simulation - variance reduction, quasi-Monte Carlo, importance sampling, GPU MC'),
    ('optimization-methods', 'Optimization methods - gradient descent variants, evolutionary algorithms, Bayesian opt, NLP'),
    ('numerical-linear-algebra', 'Numerical linear algebra - factorizations, iterative solvers, preconditioning, sparse methods'),
    ('ordinary-differential-equations', 'ODE solvers - Runge-Kutta, stiff systems, DAE, symplectic integrators, DifferentialEquations.jl'),
    ('partial-differential-equations', 'PDE solvers - FEM, FVM, spectral methods, adaptivity, time stepping, parallel PDE'),
    ('signal-processing-advanced', 'Signal processing advanced - Kalman filter, particle filter, compressive sensing, wavelets'),
    ('graph-algorithms-advanced', 'Graph algorithms advanced - max flow, matching, planarity, spectral clustering, PageRank'),
    ('computational-geometry', 'Computational geometry - convex hull, Delaunay, Voronoi, CGAL, proximity queries, sweep'),
    ('network-simulation', 'Network simulation - ns-3, OMNeT++, GNS3, packet tracing, protocol validation, emulation'),
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
