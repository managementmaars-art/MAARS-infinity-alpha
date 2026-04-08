
import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # Advanced Blockchain and Web3
    ('solidity-advanced', 'Solidity advanced - assembly, yul, storage layout, gas optimization, proxy patterns, EIP standards'),
    ('evm-internals', 'EVM internals - opcodes, stack, memory, storage, gas mechanics, precompiles, ABI encoding'),
    ('defi-protocols-advanced', 'DeFi protocols advanced - AMM math, lending protocols, liquidation, MEV, flash loans'),
    ('zk-proofs-advanced', 'ZK proofs advanced - SNARKs, STARKs, PLONK, Groth16, circom, halo2, proof generation'),
    ('layer2-scaling', 'Layer 2 scaling - optimistic rollups, ZK rollups, state channels, plasma, bridges, sequencers'),
    ('nft-development', 'NFT development - ERC-721, ERC-1155, metadata, royalties, dynamic NFTs, on-chain art'),
    ('dao-governance', 'DAO governance - voting mechanisms, proposal lifecycle, treasury management, Compound Governor'),
    # Advanced AI Agents
    ('agent-workflows', 'Agent workflows - task decomposition, sub-agent spawning, parallel execution, result synthesis'),
    ('long-horizon-planning', 'Long horizon planning - hierarchical planning, task graphs, milestone tracking, replanning'),
    ('reflexion-advanced', 'Reflexion advanced - verbal reinforcement, episodic memory, self-reflection, iterative refinement'),
    ('self-play-agents', 'Self-play agents - RLHF from self-play, constitutional self-critique, debate, red-teaming'),
    ('agent-benchmarking', 'Agent benchmarking - SWE-bench, WebArena, AgentBench, GAIA, evaluation methodology'),
    ('agent-safety-patterns', 'Agent safety patterns - human-in-the-loop, sandboxing, permission models, rollback, audit trails'),
    # Advanced Python Performance
    ('cython-optimization', 'Cython optimization - typed memoryviews, parallelism, C integration, profiling, building'),
    ('numba-advanced', 'Numba advanced - CUDA kernels, parallel, vectorize, AOT compilation, structured arrays'),
    ('cffi-ctypes', 'CFFI/ctypes - C library integration, callbacks, structures, pointers, memory management'),
    ('python-async-advanced', 'Python async advanced - asyncio internals, event loops, protocols, custom executors, cancellation'),
    ('multiprocessing-advanced', 'Python multiprocessing advanced - shared memory, Manager, Pool patterns, process pools'),
    # Advanced JavaScript/TypeScript
    ('javascript-engine-internals', 'JavaScript engine internals - V8, JIT, hidden classes, deoptimization, memory model'),
    ('web-workers-advanced', 'Web Workers advanced - SharedArrayBuffer, Atomics, transfer objects, worker pools'),
    ('webassembly-javascript', 'WebAssembly + JavaScript - calling conventions, memory sharing, WASM debugging, streaming'),
    ('nodejs-performance', 'Node.js performance - libuv, event loop phases, cluster, worker_threads, memory tuning'),
    ('deno-advanced', 'Deno advanced - permissions, FFI, WebGPU, Deploy KV, queues, cron, WASM modules'),
    # Advanced Infrastructure Patterns
    ('multi-region-active-active', 'Multi-region active-active - global load balancing, data replication, conflict resolution'),
    ('chaos-engineering-advanced', 'Chaos engineering advanced - chaos mesh, toxiproxy, fault injection, blast radius control'),
    ('sre-toil-reduction', 'SRE toil reduction - automation opportunities, toil measurement, elimination strategies'),
    ('platform-reliability', 'Platform reliability engineering - SLA tiers, error budgets, reliability roadmap'),
    ('cost-attribution', 'Cost attribution engineering - tagging strategy, showback, chargeback, unit economics'),
    # Advanced Machine Learning
    ('neural-ode', 'Neural ODE - continuous dynamics, adjoint method, latent ODEs, controlled neural ODEs'),
    ('graph-neural-networks', 'Graph neural networks - GCN, GAT, GraphSAGE, message passing, heterogeneous graphs'),
    ('point-cloud-learning', 'Point cloud learning - PointNet, PointNet++, 3D object detection, scene understanding'),
    ('video-understanding', 'Video understanding ML - temporal models, 3D convolutions, transformers, action recognition'),
    ('audio-ml-advanced', 'Audio ML advanced - spectrograms, CTC, wav2vec2, EnCodec, music generation'),
    # Advanced Observability
    ('traces-sampling', 'Traces sampling strategies - head-based, tail-based, probabilistic, adaptive, reservoir'),
    ('slo-error-budgets', 'SLO error budgets - burn rates, alerting strategies, budget policies, reliability forecasting'),
    ('cardinality-management', 'Cardinality management - high-cardinality metrics, label optimization, retention policies'),
    ('k8s-observability', 'Kubernetes observability - kube-state-metrics, cadvisor, control plane metrics, events'),
    ('network-observability', 'Network observability - flow data, latency, packet loss, DNS, bandwidth, eBPF'),
    # Advanced Data Pipelines
    ('data-ingestion-patterns', 'Data ingestion patterns - batch vs streaming, schema evolution, late arrivals, ordering'),
    ('cdc-advanced', 'Change Data Capture advanced - Debezium, outbox, event-driven sync, schema registry'),
    ('data-transformation-patterns', 'Data transformation patterns - push vs pull, materialized views, incremental, backfill'),
    ('data-validation-frameworks', 'Data validation frameworks - Great Expectations, Soda, Deequ, Pandera, schema validation'),
    ('data-pipeline-testing', 'Data pipeline testing - unit tests, integration tests, data quality checks, end-to-end'),
    # Advanced Platform Engineering
    ('golden-paths-implementation', 'Golden paths implementation - opinionated templates, scaffolding, migration guides'),
    ('backstage-plugins', 'Backstage plugin development - frontend, backend, scaffolder actions, entity providers'),
    ('service-maturity-model', 'Service maturity model - production readiness, operational excellence, scorecards'),
    ('tech-radar-creation', 'Technology radar creation - quadrants, rings, entry criteria, governance, communication'),
    ('architectural-governance', 'Architectural governance - decision records, review processes, principles, exceptions'),
    # Advanced Frontend Performance
    ('core-web-vitals-optimization', 'Core Web Vitals optimization - LCP, FID/INP, CLS, TTFB, measurement, attribution'),
    ('javascript-bundle-optimization', 'JS bundle optimization - tree shaking, code splitting, dynamic imports, compression'),
    ('image-performance', 'Image performance - formats, compression, lazy loading, responsive, CDN, priority hints'),
    ('font-performance', 'Font performance - WOFF2, font-display, preload, subsetting, variable fonts, FOIT/FOUT'),
    ('render-performance', 'Render performance - layout thrashing, compositing, paint, requestAnimationFrame, GPU'),
    # Advanced Deployment Strategies
    ('feature-flag-implementation', 'Feature flag implementation - gradual rollout, targeting, kill switches, technical debt'),
    ('dark-launch-patterns', 'Dark launch patterns - shadow mode, traffic mirroring, parallel execution comparison'),
    ('gitops-multi-cluster', 'GitOps multi-cluster - cluster fleet management, environment promotion, sync policies'),
    ('progressive-rollout', 'Progressive rollout - ring-based deployment, automatic rollback, health checks, metrics'),
    ('deployment-validation', 'Deployment validation - smoke tests, synthetic checks, canary metrics, automated gates'),
    # Advanced Search and Retrieval
    ('semantic-search-advanced', 'Semantic search advanced - bi-encoder, cross-encoder, late interaction, RAG fusion'),
    ('hybrid-search-advanced', 'Hybrid search advanced - sparse-dense fusion, RRF, score normalization, query rewriting'),
    ('neural-search', 'Neural search - learned sparse retrieval, neural ranking, SPLADE, ColBERT, PLAID'),
    ('search-personalization', 'Search personalization - user models, click-through rate, implicit feedback, reranking'),
    ('query-understanding', 'Query understanding - intent classification, entity extraction, query expansion, spelling correction'),
    # Advanced Microservices
    ('service-mesh-patterns', 'Service mesh patterns - traffic policies, circuit breaking, retry budgets, canary, A/B'),
    ('api-gateway-advanced', 'API gateway advanced - request/response transformation, rate limiting algorithms, auth delegation'),
    ('event-driven-microservices', 'Event-driven microservices - choreography, orchestration, sagas, event store, projections'),
    ('microservices-testing', 'Microservices testing - contract testing, consumer-driven, wiremock, service virtualization'),
    ('microservices-observability', 'Microservices observability - correlation IDs, distributed tracing, service maps, SLIs'),
    # Advanced Cloud Security
    ('cloud-iam-advanced', 'Cloud IAM advanced - attribute-based access, condition keys, resource policies, SCPs'),
    ('cloud-network-security', 'Cloud network security - VPC security, NACLs, security groups, WAF, DDoS protection'),
    ('cloud-data-protection', 'Cloud data protection - encryption, key management, tokenization, DLP, data classification'),
    ('container-runtime-security', 'Container runtime security - seccomp, apparmor, capabilities, rootless, runtime policies'),
    ('supply-chain-security-advanced', 'Supply chain security advanced - SLSA levels, SBOM, sigstore, attestations, provenance'),
    # Domain-Specific AI Applications
    ('agriculture-ai', 'Agriculture AI - crop disease detection, yield prediction, precision farming, satellite imagery'),
    ('energy-ai-advanced', 'Energy AI advanced - demand forecasting, grid optimization, renewable integration, digital twins'),
    ('retail-ai', 'Retail AI - demand forecasting, visual search, recommendation, dynamic pricing, supply chain'),
    ('logistics-ai', 'Logistics AI - route optimization, demand sensing, warehouse automation, last-mile delivery'),
    ('insurance-ai', 'Insurance AI - risk scoring, claims processing, fraud detection, underwriting automation'),
    # Advanced Data Science Workflows
    ('experiment-design', 'Experiment design - power analysis, sample size, control groups, sequential testing, stopping rules'),
    ('ab-testing-advanced', 'A/B testing advanced - CUPED, SUTVA violations, network effects, switchback experiments'),
    ('statistical-modeling', 'Statistical modeling - GLMs, mixed effects, hierarchical Bayesian, model selection, validation'),
    ('data-science-workflow', 'Data science workflow - problem framing, EDA, feature engineering, modeling, deployment, monitoring'),
    ('decision-intelligence', 'Decision intelligence - decision modeling, AI augmentation, outcome tracking, bias detection'),
    # Advanced Protocols
    ('mqtt-advanced', 'MQTT advanced - QoS levels, retained messages, LWT, broker clustering, security, v5 features'),
    ('amqp-rabbitmq-advanced', 'AMQP/RabbitMQ advanced - exchanges, bindings, dead letters, quorum queues, streams, federations'),
    ('grpc-streaming-advanced', 'gRPC streaming advanced - flow control, backpressure, deadline propagation, health checking'),
    ('http3-quic', 'HTTP/3 and QUIC - connection migration, 0-RTT, multiplexing, congestion control, deployment'),
    ('websocket-protocol', 'WebSocket protocol deep dive - framing, extensions, subprotocols, proxies, security'),
    # Advanced Development Workflows
    ('conventional-commits-advanced', 'Conventional commits advanced - semantic versioning, changelogs, breaking changes, tooling'),
    ('monorepo-tooling', 'Monorepo tooling comparison - Nx, Turborepo, Bazel, Pants, Lerna, affected computation'),
    ('feature-branching', 'Feature branching strategies - trunk-based, gitflow, GitHub flow, environment branches'),
    ('code-review-culture', 'Code review culture - constructive feedback, async review, review checklists, automation'),
    ('documentation-culture', 'Documentation culture - living docs, docs-as-code, just-in-time, evergreen, discoverability'),
    # Advanced SaaS Patterns
    ('tenant-isolation-advanced', 'Tenant isolation advanced - silo, pool, bridge models, data isolation, compute isolation'),
    ('saas-metrics-advanced', 'SaaS metrics advanced - MRR expansion, NRR, CAC payback, LTV:CAC, cohort analysis'),
    ('subscription-management', 'Subscription management - upgrade/downgrade, proration, pause, cancellation flows, dunning'),
    ('usage-metering', 'Usage metering - metering API, aggregation, billing sync, quota enforcement, analytics'),
    ('customer-360', 'Customer 360 view - data unification, CDP integration, identity resolution, journey analytics'),
    # Advanced Low-Level Programming
    ('memory-allocation-patterns', 'Memory allocation patterns - arena, pool, slab, buddy allocators, fragmentation, GC tuning'),
    ('simd-programming', 'SIMD programming - SSE, AVX, NEON, auto-vectorization, intrinsics, portable SIMD'),
    ('lock-free-programming', 'Lock-free programming - CAS, ABA problem, hazard pointers, RCU, memory ordering, barriers'),
    ('cache-optimization', 'Cache optimization - cache lines, false sharing, prefetching, NUMA awareness, memory layout'),
    ('profiling-flamegraphs', 'Profiling and flamegraphs - CPU, memory, I/O flamegraphs, async profiling, continuous profiling'),
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
