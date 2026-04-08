
import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # Advanced AI Infrastructure
    ('nvidia-triton-advanced', 'NVIDIA Triton Inference Server advanced - model ensembles, custom backends, DALI, perf'),
    ('tensorrt-optimization', 'TensorRT optimization - layer fusion, precision calibration, dynamic shapes, profiling'),
    ('onnx-optimization', 'ONNX optimization - graph optimization, quantization, pruning, OnnxRuntime execution providers'),
    ('model-parallelism', 'Model parallelism - tensor parallelism, pipeline parallelism, 3D parallelism, expert parallel'),
    ('flash-attention-impl', 'Flash Attention implementation - memory-efficient attention, fused kernels, sliding window'),
    ('moe-implementation', 'Mixture of Experts implementation - gating, load balancing, expert routing, capacity factors'),
    # Advanced Python Tooling
    ('uv-advanced', 'uv Python package manager - workspace, lockfiles, scripts, tools, publish, virtual envs'),
    ('rye-advanced', 'Rye Python workflow tool - project management, toolchains, publishing, sync, virtual envs'),
    ('pdm-advanced', 'PDM Python package manager - PEP 582, dependency groups, lockfile, scripts, plugins'),
    ('hatch-advanced', 'Hatch - modern Python project management, environments, versioning, build, publish'),
    ('nox-automation', 'Nox - Python test automation, sessions, reuse, parameterize, conda, caching'),
    ('invoke-tasks', 'Invoke - Python task execution tool, tasks, namespaces, parallel, context, configuration'),
    # Advanced TypeScript Patterns
    ('typescript-compiler-api', 'TypeScript Compiler API - AST traversal, transformation, type checking, custom transforms'),
    ('ts-morph-api', 'ts-morph - TypeScript AST manipulation, refactoring tools, code generation, migrations'),
    ('tsd-type-testing', 'tsd - TypeScript type testing, expect-type, type-assertion testing, CI integration'),
    ('effect-ts-advanced', 'Effect-TS advanced - Effect, Fiber, Layer, Schema, runtime, error management, concurrency'),
    ('zod-v4-patterns', 'Zod v4 patterns - schemas, transforms, refinements, branded types, discriminated unions'),
    # Advanced Go Patterns
    ('go-embed-patterns', 'Go embed - filesystem embedding, static assets, templates, configurations, migrations'),
    ('go-plugin-patterns', 'Go plugin system - hashicorp go-plugin, RPC, gRPC transport, versioning, hot-reload'),
    ('go-generics-advanced', 'Go generics advanced - type constraints, type sets, comparable, ordered, generic data structures'),
    ('go-build-constraints', 'Go build constraints - build tags, platform-specific code, feature flags, cross-compilation'),
    ('go-profiling', 'Go profiling - pprof, trace, benchmarks, memory allocation, goroutine analysis, flamegraphs'),
    # Advanced Rust Patterns
    ('rust-macros-advanced', 'Rust macros advanced - proc_macro, syn, quote, derive macros, attribute macros, function macros'),
    ('rust-unsafe-patterns', 'Rust unsafe patterns - raw pointers, extern functions, mutable statics, union, transmute'),
    ('rust-ffi-patterns', 'Rust FFI - C interop, cbindgen, bindgen, wasm-bindgen, foreign functions, callbacks'),
    ('rust-embedded-advanced', 'Rust embedded advanced - HAL traits, RTIC framework, embassy async, peripheral abstractions'),
    ('rust-performance-advanced', 'Rust performance advanced - SIMD, intrinsics, zero-cost abstractions, inlining, cache efficiency'),
    # Advanced Kubernetes
    ('k8s-operator-advanced', 'Kubernetes operator advanced - controller-runtime, reconciliation, finalizers, status subresource'),
    ('k8s-admission-webhooks', 'K8s admission webhooks - validating, mutating, webhook configuration, cert-manager, testing'),
    ('k8s-custom-scheduler', 'Kubernetes custom scheduler - scheduler plugins, extender, binding, filter, score'),
    ('k8s-networking-advanced', 'K8s networking advanced - CNI plugins, network policies, dual-stack, IPv6, eBPF'),
    ('k8s-storage-advanced', 'K8s storage advanced - CSI drivers, volume snapshots, resize, topology, local volumes'),
    # Advanced Cloud Architecture
    ('aws-service-catalog', 'AWS Service Catalog - portfolios, products, constraints, provisioning, self-service'),
    ('aws-control-tower-advanced', 'AWS Control Tower advanced - landing zones, guardrails, AFT, enrollment, customizations'),
    ('azure-arc-advanced', 'Azure Arc advanced - Kubernetes, servers, data services, GitOps, policy, extensions'),
    ('gcp-anthos-advanced', 'GCP Anthos advanced - Config Sync, Policy Controller, Service Mesh, multicloud deployment'),
    ('cloud-foundation-toolkit', 'Cloud Foundation Toolkit - GCP CfT, Terraform modules, blueprint, security foundations'),
    # Advanced Security Operations
    ('soar-platform', 'SOAR platform - playbook automation, case management, threat intelligence, integration, metrics'),
    ('xdr-platform', 'XDR platform - extended detection response, telemetry correlation, investigation, response'),
    ('cloud-siem', 'Cloud SIEM - Chronicle, Microsoft Sentinel, Elastic SIEM, detection rules, UEBA'),
    ('deception-technology', 'Deception technology - honeypots, honeytokens, canary files, deception fabric, alerting'),
    ('threat-hunting-advanced', 'Threat hunting advanced - hypothesis-driven, MITRE ATT&CK, KQL, YARA rules, IOC enrichment'),
    # Advanced MLOps
    ('feast-advanced', 'Feast feature store advanced - feature views, entities, on-demand features, registry, serving'),
    ('zenml-advanced', 'ZenML advanced - stacks, pipelines, steps, artifacts, materializers, deployment, cloud'),
    ('metaflow-advanced', 'Metaflow advanced - parallel steps, foreach, data artifacts, resume, S3 datastore, cards'),
    ('hamilton-advanced', 'Hamilton DAG advanced - drivers, decorators, display, scaling, testing, dataflows'),
    ('evidently-advanced', 'Evidently AI advanced - data drift, model performance, test presets, custom metrics, reports'),
    # Advanced Database Patterns
    ('postgresql-partitioning', 'PostgreSQL partitioning - range, list, hash, declarative, inheritance, pruning, maintenance'),
    ('postgresql-streaming-replication', 'PostgreSQL streaming replication - WAL, hot standby, replication slots, patroni, switchover'),
    ('postgresql-json-advanced', 'PostgreSQL JSON advanced - JSONB operators, GIN indexes, jsonpath, normalization, performance'),
    ('postgresql-full-text', 'PostgreSQL full-text search - tsvector, tsquery, ranking, dictionaries, configurations'),
    ('postgresql-extensions-advanced', 'PostgreSQL extensions advanced - pg_stat, pgaudit, pg_partman, pg_cron, pg_repack'),
    # Advanced Frontend Architecture
    ('partial-hydration-advanced', 'Partial hydration advanced - island architecture, resumability, server components, streaming'),
    ('rendering-strategies', 'Rendering strategies - SSR, SSG, ISR, streaming, PPR, RSC, edge rendering, comparison'),
    ('state-machines-xstate', 'State machines XState v5 - actors, spawning, guards, actions, invoke, context, testing'),
    ('signals-advanced', 'Signals advanced - reactivity fine-grained, solidjs, preact, angular, vue, qwik signals'),
    ('view-transitions-api', 'View Transitions API - SPA transitions, MPA transitions, pseudo-elements, animations, fallback'),
    # Advanced Data Science
    ('causal-ml', 'Causal ML - EconML, DoWhy, CausalPy, heterogeneous treatment effects, uplift modeling'),
    ('synthetic-data-advanced', 'Synthetic data advanced - SDV, Gretel, CTGAN, privacy guarantees, evaluation, augmentation'),
    ('feature-selection', 'Feature selection - filter, wrapper, embedded, SHAP-based, Boruta, recursive elimination'),
    ('class-imbalance', 'Class imbalance handling - SMOTE variants, cost-sensitive learning, ensemble methods, threshold'),
    ('time-series-anomaly', 'Time series anomaly detection - SARIMA residuals, LSTM, prophet, isolation forest, ADTK'),
    # Advanced Distributed Systems
    ('consensus-algorithms', 'Consensus algorithms - Raft, Paxos, Multi-Paxos, Byzantine fault tolerance, Tendermint'),
    ('crdt-implementation', 'CRDT implementation - LWW register, OR-Set, RGA, Automerge, Yjs, Loro, conflict resolution'),
    ('vector-clocks', 'Vector clocks - causality tracking, Lamport timestamps, version vectors, conflict detection'),
    ('distributed-transactions', 'Distributed transactions - 2PC, 3PC, saga pattern, TCC, at-most-once, exactly-once'),
    ('gossip-protocols', 'Gossip protocols - SWIM, Serf, membership, failure detection, anti-entropy, convergence'),
    # Advanced API Patterns
    ('backend-for-frontend-advanced', 'BFF advanced - aggregation, transformation, caching, auth delegation, mobile BFF'),
    ('api-composition-advanced', 'API composition advanced - query aggregation, parallel fetching, waterfall avoidance, caching'),
    ('grpc-web-advanced', 'gRPC-Web advanced - envoy proxy, transcoding, metadata, streaming, browser clients'),
    ('websocket-scaling', 'WebSocket scaling - sticky sessions, pub/sub backend, horizontal scaling, connection limits'),
    ('long-polling-patterns', 'Long polling patterns - comet, SSE vs WebSocket vs polling, timeout, reconnection'),
    # Advanced Compiler and Language Tools
    ('llvm-advanced', 'LLVM advanced - IR, passes, JIT, backends, optimization pipeline, bindings, TableGen'),
    ('antlr4-advanced', 'ANTLR4 advanced - grammar design, visitors, listeners, error recovery, runtime targets'),
    ('treesitter-advanced', 'Tree-sitter advanced - grammar definition, queries, syntax highlighting, code navigation'),
    ('lsp-server-development', 'LSP server development - protocol, diagnostics, completions, hover, references, formatting'),
    ('wasm-component-model', 'WASM component model - WIT interfaces, linking, composition, WASI preview 2, toolchains'),
    # Advanced Infrastructure Automation
    ('crossplane-composition', 'Crossplane composition - XRD, XRC, patch transforms, webhooks, environment configs'),
    ('pulumi-advanced', 'Pulumi advanced - ComponentResource, StackReference, automation API, ESC, policy'),
    ('cdk-advanced', 'AWS CDK advanced - L3 constructs, aspects, context, custom resources, CDK Pipelines'),
    ('bicep-advanced', 'Bicep advanced - modules, loops, conditions, user-defined types, AVM modules, deployment stacks'),
    ('terramate-orchestration', 'Terramate - Terraform orchestration, stacks, globals, change detection, scripts, cloud'),
    # Advanced Monitoring and Alerting
    ('victorops-advanced', 'VictorOps/Splunk On-Call advanced - routing, escalation, scheduling, webhooks, timeline'),
    ('alertmanager-patterns', 'Alertmanager patterns - routing tree, inhibition, silencing, grouping, templates, HA'),
    ('prometheus-advanced', 'Prometheus advanced - remote write, exemplars, native histograms, OTLP, federation, HA'),
    ('grafana-advanced', 'Grafana advanced - data sources, transformations, alerting, library panels, provisioning, plugins'),
    ('openobserve-platform', 'OpenObserve - cloud-native observability, logs, metrics, traces, dashboards, ingestion'),
    # Advanced Edge Computing
    ('wasm-edge-advanced', 'WasmEdge advanced - serverless functions, AI inference, WASI, host functions, plugins'),
    ('cloudflare-analytics-advanced', 'Cloudflare Analytics Engine - write data, query SQL, sampling, retention, metrics'),
    ('fastly-edge-advanced', 'Fastly edge advanced - VCL, Compute@Edge, Image Optimizer, security, observability'),
    ('akamai-edge', 'Akamai EdgeWorkers - functions, API gateway, security, caching, delivery, purge'),
    ('lambda-edge-advanced', 'Lambda@Edge advanced - viewer/origin request/response, CloudFront, streaming, caching'),
    # Advanced AI Reasoning
    ('o1-style-reasoning', 'o1-style reasoning - chain of thought, reflection, self-correction, verification, budgeting'),
    ('process-reward-models', 'Process Reward Models - step-level rewards, math reasoning, verification, search with PRM'),
    ('test-time-compute', 'Test-time compute scaling - self-consistency, revision, beam search, best-of-N, verification'),
    ('world-models', 'World models - model-based RL, latent dynamics, planning, Dreamer, RSSM, SimPLe'),
    ('neurosymbolic-ai', 'Neurosymbolic AI - neural-symbolic integration, logic neural networks, concept learning'),
    # Advanced Authentication and Identity
    ('passkey-advanced', 'Passkeys advanced - WebAuthn, FIDO2, authenticator selection, credential management, attestation'),
    ('oauth2-advanced-flows', 'OAuth2 advanced flows - PKCE, device flow, token exchange, JAR, PAR, DPoP, mTLS'),
    ('oidc-advanced', 'OIDC advanced - claims, scopes, introspection, dynamic client registration, CIBA, FAPI'),
    ('zero-knowledge-auth', 'Zero-knowledge authentication - ZK proofs, anonymous credentials, ZKVM, privacy-preserving'),
    ('decentralized-identity', 'Decentralized identity - DIDs, Verifiable Credentials, DIDComm, agent wallets, trust frameworks'),
    # Advanced Content and Media
    ('video-streaming-advanced', 'Video streaming advanced - adaptive bitrate, HLS, DASH, packaging, DRM, CDN, analytics'),
    ('audio-streaming-advanced', 'Audio streaming advanced - WebRTC audio, Opus codec, noise suppression, spatialization'),
    ('image-optimization-advanced', 'Image optimization advanced - WebP, AVIF, lazy loading, responsive images, CDN, LQIP'),
    ('media-processing-pipeline', 'Media processing pipeline - transcoding, thumbnails, metadata, storage, CDN, delivery'),
    ('content-delivery-advanced', 'Content delivery advanced - multi-CDN, failover, performance monitoring, purging, analytics'),
    # Advanced Developer Experience
    ('dx-metrics', 'Developer experience metrics - DORA, SPACE, DevEx, developer surveys, productivity measurement'),
    ('internal-tooling', 'Internal tooling best practices - CLI tools, scripts, runbooks, dashboard, automation'),
    ('developer-onboarding', 'Developer onboarding - documentation, dev environment setup, tutorials, mentorship, metrics'),
    ('coding-standards', 'Coding standards - style guides, linters, formatters, pre-commit hooks, enforcement'),
    ('pair-programming-advanced', 'Pair programming advanced - remote pairing, mob programming, driver-navigator, mentoring'),
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
