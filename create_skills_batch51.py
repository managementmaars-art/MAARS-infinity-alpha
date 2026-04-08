
import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # Compiler and language toolchain internals
    ('llvm-backend-development', 'LLVM backend development - TableGen, instruction selection, register allocation, codegen'),
    ('clang-tooling-advanced', 'Clang tooling advanced - LibTooling, AST matchers, refactoring tools, clang-tidy checks'),
    ('gcc-internals', 'GCC internals - GIMPLE, RTL, tree passes, middle-end optimizations, plugin API'),
    ('cranelift-jit', 'Cranelift JIT - Rust-based codegen, IR, backends, regalloc2, Wasmtime integration'),
    ('mlir-infrastructure', 'MLIR infrastructure - dialects, passes, patterns, conversions, ODS, bufferization'),
    ('graal-truffle', 'GraalVM Truffle - polyglot, AST interpreters, partial evaluation, guest language dev'),
    ('jvm-bytecode', 'JVM bytecode engineering - ASM, Javassist, ByteBuddy, class transformers, agents'),
    ('wasm-toolchain', 'WebAssembly toolchain - wat, wasm-opt, binaryen, wasi-sdk, component model, wit'),
    ('language-server-protocol', 'LSP implementation - server lifecycle, text sync, completion, diagnostics, code actions'),
    ('tree-sitter-grammars', 'Tree-sitter grammars - grammar.js, node types, queries, highlighting, injections'),
    ('antlr4-advanced', 'ANTLR4 advanced - grammar rules, listeners, visitors, error recovery, semantic predicates'),
    ('pratt-parser', 'Pratt parsing - top-down operator precedence, Prolog-style, expression languages, DSLs'),
    ('type-inference-algorithms', 'Type inference algorithms - Hindley-Milner, Algorithm W, bidirectional checking, unification'),
    ('formal-verification-tools', 'Formal verification tools - TLA+, Alloy, Coq, Lean4, Isabelle, model checking'),
    ('program-synthesis', 'Program synthesis - sketch-based, example-guided, LLM-guided, Rosette, SMT-based'),
    ('abstract-interpretation', 'Abstract interpretation - lattices, fixpoints, widening, Frama-C, IKOS, Infer'),
    ('dataflow-analysis', 'Dataflow analysis - SSA form, liveness, dominators, alias analysis, points-to'),
    ('linker-internals', 'Linker internals - ELF, Mach-O, PE, symbol resolution, relocations, LLD, mold'),
    ('debugger-internals', 'Debugger internals - ptrace, DWARF, breakpoints, watchpoints, GDB/LLDB scripting'),
    ('profiler-internals', 'Profiler internals - perf, eBPF, sampling, call graphs, flamegraphs, PMU counters'),
    # Advanced networking and protocols
    ('dpdk-networking', 'DPDK networking - poll-mode drivers, hugepages, mbuf, ring buffers, pipeline, crypto'),
    ('xdp-ebpf-networking', 'XDP eBPF networking - packet processing, load balancing, DDoS mitigation, tc BPF'),
    ('rdma-infiniband', 'RDMA/InfiniBand - verbs, ROCE, iWARP, memory registration, completion queues, MPI over RDMA'),
    ('optical-networking', 'Optical networking - DWDM, coherent optics, CFP, QSFP, wavelength routing, OTN'),
    ('5g-ran-architecture', '5G RAN architecture - gNB, CU/DU split, O-RAN, fronthaul, beamforming, NR protocols'),
    ('satellite-communications', 'Satellite communications - LEO constellations, Starlink API, DVB-S2, link budgets'),
    ('software-defined-wan', 'SD-WAN implementation - underlay/overlay, vEdge, ZTP, policies, application-aware routing'),
    ('network-programmability', 'Network programmability - NETCONF, YANG, RESTCONF, gNMI, OpenConfig, pyATS'),
    ('segment-routing', 'Segment routing - SRv6, MPLS-SR, traffic engineering, TI-LFA, Flex-Algo, PCE'),
    ('p4-programming', 'P4 programming - programmable data planes, P4Runtime, PSA, behavioral model, p4c'),
    # Embedded systems deep
    ('rtos-advanced', 'RTOS advanced - FreeRTOS, Zephyr, RT-Thread, scheduling, priority inversion, IPC'),
    ('embedded-linux-advanced', 'Embedded Linux advanced - Yocto, Buildroot, device tree, kernel modules, BSP'),
    ('microcontroller-hal', 'Microcontroller HAL - embedded-hal (Rust), STM32 HAL, nRF SDK, ESP-IDF, Pico SDK'),
    ('can-bus-automotive', 'CAN bus automotive - CAN FD, DBC files, CANopen, UDS, OBD-II, Vector tools'),
    ('modbus-industrial', 'Modbus industrial - RTU, TCP, function codes, holding registers, coils, Modbus poll'),
    ('opc-ua-advanced', 'OPC UA advanced - information model, address space, subscriptions, security, UA SDK'),
    ('plc-programming', 'PLC programming - IEC 61131-3, ladder logic, structured text, function blocks, SCADA'),
    ('fpga-advanced', 'FPGA advanced - SystemVerilog, timing constraints, IP cores, partial reconfiguration, DMA'),
    ('hls-high-level-synthesis', 'HLS synthesis - Vitis HLS, Vivado, pragma optimization, interface protocols, co-sim'),
    ('embedded-testing-advanced', 'Embedded testing advanced - Hardware-in-loop, JTAG, coverage, MISRA C, PC-lint'),
    # Cryptography and security engineering
    ('cryptography-engineering', 'Cryptography engineering - AES-GCM, RSA, ECC, key management, timing attacks, constant-time'),
    ('zero-knowledge-proofs', 'Zero-knowledge proofs - zk-SNARKs, zk-STARKs, Circom, Halo2, Groth16, PLONK'),
    ('threshold-cryptography', 'Threshold cryptography - multi-party computation, secret sharing, threshold signatures, DKG'),
    ('homomorphic-encryption', 'Homomorphic encryption - CKKS, BFV, TFHE, OpenFHE, HELib, privacy-preserving ML'),
    ('post-quantum-cryptography', 'Post-quantum cryptography - CRYSTALS-Kyber, Dilithium, SPHINCS+, NIST PQC, migration'),
    ('secure-enclaves', 'Secure enclaves - Intel SGX, AMD SEV, ARM TrustZone, remote attestation, sealing'),
    ('hsm-pkcs11', 'HSM PKCS#11 - hardware security modules, key ceremony, PKCS#11 API, softhsm, AWS CloudHSM'),
    ('certificate-transparency', 'Certificate transparency - CT logs, SCT, monitoring, crt.sh, policy enforcement'),
    ('mtls-advanced', 'mTLS advanced - certificate pinning, SPIFFE/SPIRE, Vault PKI, cert-manager, rotation'),
    ('security-protocol-design', 'Security protocol design - Noise protocol, Signal protocol, MLS, key exchange patterns'),
    # Scientific programming advanced
    ('julia-advanced', 'Julia advanced - multiple dispatch, metaprogramming, GPU, parallel, Flux.jl, Turing.jl'),
    ('r-shiny-advanced', 'R Shiny advanced - reactive programming, modules, Shiny server, golem, authentication'),
    ('matlab-simulink', 'MATLAB/Simulink - model-based design, code generation, toolboxes, Stateflow, HIL testing'),
    ('scipy-advanced', 'SciPy advanced - sparse matrices, signal processing, optimization, statistics, interpolation'),
    ('numba-jit', 'Numba JIT - LLVM-based Python JIT, CUDA kernels, nopython mode, parallel, vectorize'),
    ('taichi-graphics', 'Taichi lang - differentiable programming, GPU kernels, sparse data structures, autodiff'),
    ('fenics-fem', 'FEniCS FEM - variational forms, UFL, DOLFIN, mixed problems, mesh refinement, parallel'),
    ('openturns-uncertainty', 'OpenTURNS uncertainty quantification - distributions, reliability, sensitivity, metamodels'),
    ('uncertainpy-uq', 'Uncertainty quantification - Monte Carlo, Sobol indices, polynomial chaos, SALib, Chaospy'),
    ('meshio-formats', 'meshio file formats - mesh conversion, GMSH, VTK, EXODUS, HDF5, Abaqus, Nastran'),
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
