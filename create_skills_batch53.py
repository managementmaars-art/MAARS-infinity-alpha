
import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # Bioinformatics and life sciences computing deep
    ('genomics-variant-calling', 'Genomics variant calling - GATK, DeepVariant, bcftools, VCF format, annotation, gnomAD'),
    ('rna-seq-analysis', 'RNA-seq analysis - STAR, salmon, DESeq2, edgeR, WGCNA, differential expression, splicing'),
    ('single-cell-advanced', 'Single-cell advanced - Seurat v5, scVI, SCENIC, trajectory, velocity, spatial omics'),
    ('structural-biology-advanced', 'Structural biology advanced - cryo-EM processing, RELION, cryoSPARC, molecular docking'),
    ('cheminformatics-advanced', 'Cheminformatics advanced - RDKit, reaction prediction, SMARTS, fingerprints, drug-likeness'),
    ('systems-biology-advanced', 'Systems biology advanced - ODE models, flux balance analysis, regulatory networks, SBML'),
    ('metagenomics-advanced', 'Metagenomics advanced - assembly, binning, taxonomic profiling, function annotation, virome'),
    ('epigenomics-analysis', 'Epigenomics analysis - ATAC-seq, ChIP-seq, WGBS, Hi-C, chromatin states, peak calling'),
    ('proteomics-advanced', 'Proteomics advanced - MaxQuant, Perseus, DIA-NN, spectral library, PTM analysis, TMT'),
    ('metabolomics-advanced', 'Metabolomics advanced - MetaboAnalyst, XCMS, HMDB, pathway analysis, NMR, MS/MS'),
    # Quantum computing deep
    ('quantum-error-correction', 'Quantum error correction - surface codes, logical qubits, fault tolerance, syndrome measurement'),
    ('quantum-algorithms-advanced', 'Quantum algorithms advanced - Grover, Shor, VQE, QAOA, amplitude estimation, HHL'),
    ('quantum-simulation-advanced', 'Quantum simulation - Hamiltonian simulation, trotterization, tensor networks, variational'),
    ('quantum-hardware', 'Quantum hardware - superconducting qubits, ion traps, photonic, calibration, decoherence'),
    ('quantum-networking-protocols', 'Quantum networking - entanglement distribution, quantum repeaters, QKD, teleportation'),
    # Financial engineering deep
    ('quantitative-finance-advanced', 'Quantitative finance advanced - stochastic calculus, Ito lemma, Greeks, HJM, CIR, Heston'),
    ('derivatives-pricing', 'Derivatives pricing - Black-Scholes, Monte Carlo, finite difference, exotic options, vol surface'),
    ('algorithmic-trading-advanced', 'Algorithmic trading advanced - market microstructure, order book, alpha generation, backtesting'),
    ('risk-management-quant', 'Risk management quant - VaR, CVaR, stress testing, copulas, credit risk, counterparty'),
    ('fixed-income-advanced', 'Fixed income advanced - yield curves, OIS discounting, swaptions, credit derivatives, MBS'),
    # Machine learning systems deep
    ('distributed-training-advanced', 'Distributed training advanced - pipeline parallelism, ZeRO, FSDP, Megatron-LM, checkpointing'),
    ('inference-optimization-advanced', 'Inference optimization - continuous batching, paged attention, speculative decoding, KV cache'),
    ('model-serving-systems', 'Model serving systems - BentoML, Triton, Ray Serve, TorchServe, canary deployment'),
    ('feature-store-engineering', 'Feature store engineering - online/offline stores, point-in-time joins, Feast, Tecton, Hopsworks'),
    ('ml-data-pipeline', 'ML data pipeline - data versioning, labeling, augmentation, validation, lineage, DVC'),
    ('vector-database-engineering', 'Vector database engineering - indexing strategies, replication, HNSW, compression, benchmarking'),
    ('llm-pretraining-engineering', 'LLM pretraining engineering - tokenizer design, data mixing, curriculum, muP, cooldown'),
    ('rlhf-pipeline', 'RLHF pipeline - preference data collection, reward model training, PPO, GRPO, rejection sampling'),
    ('model-evaluation-advanced', 'Model evaluation advanced - benchmark design, contamination detection, human eval, LLM judges'),
    ('ai-safety-red-teaming', 'AI safety red teaming - adversarial prompts, jailbreaks, RLHF failure modes, interpretability'),
    # Systems programming deep
    ('memory-allocator-design', 'Memory allocator design - slab allocator, jemalloc, tcmalloc, buddy system, GC design'),
    ('concurrent-data-structures', 'Concurrent data structures - lock-free queue, CAS, hazard pointers, epoch-based reclamation'),
    ('operating-system-internals', 'OS internals - process scheduler, virtual memory, page tables, IPC, file system VFS'),
    ('hypervisor-development', 'Hypervisor development - KVM, Xen, Type-1/2, VMCS, shadow paging, virtio, vfio'),
    ('network-stack-internals', 'Network stack internals - socket buffer, TCP state machine, zero-copy, kernel bypass, DPDK'),
    ('file-system-design', 'File system design - journaling, copy-on-write, extent trees, deduplication, ext4, ZFS, Btrfs'),
    ('storage-protocols', 'Storage protocols - NVMe, SCSI, iSCSI, FC, NVMe-oF, SPDK, userspace I/O'),
    ('real-time-systems', 'Real-time systems - deadline scheduling, PREEMPT_RT, latency analysis, jitter, cyclictest'),
    ('container-runtime-internals', 'Container runtime internals - namespaces, cgroups, seccomp, capabilities, runc, containerd'),
    ('kernel-module-development', 'Kernel module development - character devices, proc fs, netfilter hooks, kprobes, eBPF prog'),
    # Programming language theory
    ('type-theory-advanced', 'Type theory advanced - dependent types, linear types, effect types, session types, HoTT'),
    ('category-theory-code', 'Category theory for programmers - functors, monads, natural transformations, adjunctions'),
    ('lambda-calculus', 'Lambda calculus - Church encoding, beta reduction, combinators, simply typed, System F'),
    ('operational-semantics', 'Operational semantics - small-step, big-step, denotational, axiomatic, bisimulation'),
    ('programming-language-design', 'PL design - syntax design, type system, memory model, concurrency primitives, tooling'),
    ('gradual-typing', 'Gradual typing - type consistency, cast insertion, blame calculus, TypeScript gradual'),
    ('effect-handlers', 'Effect handlers - algebraic effects, free monads, extensible effects, Koka, Effekt, Frank'),
    ('ownership-type-systems', 'Ownership type systems - Rust borrow checker, linear types, uniqueness types, regions'),
    ('proof-assistants', 'Proof assistants - Coq tactics, Lean 4 mathlib, Agda patterns, Isabelle, formal proofs'),
    ('metaprogramming-advanced', 'Metaprogramming advanced - Template Haskell, Rust proc macros, macro hygiene, staging'),
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
