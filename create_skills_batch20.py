
import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # Advanced Protocol Design
    ('grpc-gateway', 'gRPC-Gateway - REST/JSON to gRPC transcoding, protobuf annotations, OpenAPI gen, Swagger'),
    ('protocol-buffers-v3', 'Protocol Buffers v3 - message design, field numbers, reserved, oneof, maps, editions'),
    ('thrift-protocol', 'Apache Thrift - IDL, services, types, cross-language, versioning, multiplexing'),
    ('capnproto-protocol', 'Cap n Proto - schema language, zero-copy, streaming, RPC, capabilities, packing'),
    ('msgpack-serialization', 'MessagePack - binary serialization, schema-less, language interop, performance'),
    # Advanced ML Training Techniques
    ('gradient-checkpointing', 'Gradient checkpointing - memory/compute tradeoff, selective, recompute activations'),
    ('mixed-precision-training', 'Mixed precision training - FP16, BF16, AMP, loss scaling, numerical stability'),
    ('zero-redundancy-optimizer', 'ZeRO optimizer - ZeRO-1/2/3, parameter sharding, offloading, DeepSpeed integration'),
    ('curriculum-learning', 'Curriculum learning - difficulty ordering, competence-based, self-paced, data scheduling'),
    ('multitask-learning-advanced', 'Multitask learning advanced - task balancing, gradient surgery, task-specific heads'),
    # Advanced Container Technologies
    ('containerd-advanced', 'containerd advanced - snapshotter, content store, runtime, namespace, gRPC API'),
    ('podman-advanced', 'Podman advanced - rootless, pods, quadlet, systemd integration, compose, play kube'),
    ('buildkit-advanced', 'BuildKit advanced - parallelism, cache mounts, secrets, SSH forwarding, frontend'),
    ('kaniko-images', 'Kaniko - containerized image builds, GKE, EKS, secrets, caching, multi-stage'),
    ('cosign-signing', 'Cosign image signing - keyless signing, SigStore, attestations, policy enforcement'),
    # Advanced Event Systems
    ('event-sourcing-advanced', 'Event sourcing advanced - snapshots, projections, upcasting, multi-stream, event store'),
    ('cqrs-event-sourcing', 'CQRS + Event Sourcing combined - command handlers, event handlers, read models'),
    ('outbox-pattern-advanced', 'Outbox pattern advanced - polling, CDC-based, cleanup, exactly-once, distributed tracing'),
    ('event-schema-registry', 'Event schema registry - Confluent schema registry, Apicurio, compatibility, evolution'),
    ('event-mesh-advanced', 'Event mesh advanced - Solace, multi-protocol, event portal, dynamic routing, topology'),
    # Advanced Testing Infrastructure
    ('test-parallelization', 'Test parallelization - sharding, matrix testing, distributed test runs, result aggregation'),
    ('flaky-test-management', 'Flaky test management - detection, quarantine, retry policies, root cause analysis'),
    ('test-impact-analysis', 'Test impact analysis - coverage mapping, change detection, selective test execution'),
    ('synthetic-test-data', 'Synthetic test data - faker, factory_boy, fishery, data generation, anonymization'),
    ('test-environment-management', 'Test environment management - ephemeral envs, env parity, data seeding, teardown'),
    # Advanced Kubernetes Patterns
    ('k8s-multitenancy', 'Kubernetes multitenancy - namespaces, network policies, resource quotas, RBAC, vcluster'),
    ('k8s-gitops-patterns', 'Kubernetes GitOps patterns - Argo CD app of apps, Flux Kustomization, environments'),
    ('k8s-service-accounts', 'K8s service accounts - IRSA, workload identity, RBAC, least privilege, token binding'),
    ('k8s-cost-management', 'Kubernetes cost management - rightsizing, namespace budgets, Kubecost, optimization'),
    ('k8s-ha-patterns', 'Kubernetes HA patterns - multi-zone, pod disruption budgets, topology spread, anti-affinity'),
    # Advanced Terraform Patterns
    ('terraform-testing', 'Terraform testing - Terratest, checkov, tfsec, OPA, contract testing, mock providers'),
    ('terraform-refactoring', 'Terraform refactoring - moved blocks, import, module extraction, state manipulation'),
    ('terraform-modules-advanced', 'Terraform modules advanced - versioning, composition, interface design, validation'),
    ('terraform-workspaces', 'Terraform workspaces - environment separation, limitations, alternatives, best practices'),
    ('opentofu-migration', 'OpenTofu migration - Terraform to OpenTofu, provider compatibility, state migration'),
    # Advanced API Security
    ('jwt-security', 'JWT security - algorithm confusion, key confusion, none algorithm, expiry, rotation'),
    ('oauth2-security', 'OAuth2 security - PKCE, state parameter, token leakage, confused deputy, SSRF'),
    ('api-rate-limiting-advanced', 'API rate limiting advanced - algorithms, distributed counters, per-user, burst, headers'),
    ('api-dos-prevention', 'API DoS prevention - query complexity limits, depth limits, timeout, circuit breaker'),
    ('api-input-validation', 'API input validation - schema validation, injection prevention, canonicalization, encoding'),
    # Advanced Database Design
    ('schema-design-patterns', 'Schema design patterns - normalization, denormalization, polymorphism, EAV, materialized'),
    ('database-versioning', 'Database versioning - Flyway, Liquibase, atlas, migration testing, rollback strategies'),
    ('multi-model-database', 'Multi-model databases - ArangoDB, OrientDB, SurrealDB, graphs+docs+key-value'),
    ('time-series-design', 'Time series data design - retention, downsampling, partitioning, query patterns, aggregation'),
    ('geospatial-design', 'Geospatial data design - coordinate systems, indexing, proximity queries, boundaries'),
    # Advanced Frontend State
    ('jotai-advanced', 'Jotai advanced - atoms, derived atoms, async atoms, DevTools, abortable, atomWithQuery'),
    ('valtio-state', 'Valtio state management - proxy state, snapshot, derive, watch, DevTools, subscriptions'),
    ('mobx-advanced', 'MobX advanced - observables, computed, reactions, flow, makeAutoObservable, custom stores'),
    ('redux-toolkit-advanced', 'Redux Toolkit advanced - RTK Query, entities, slice patterns, middleware, DevTools'),
    ('recoil-advanced', 'Recoil advanced - atoms, selectors, async selectors, atom family, effects, snapshots'),
    # Advanced DevOps Metrics
    ('dora-metrics', 'DORA metrics - deployment frequency, lead time, MTTR, change failure rate, measurement'),
    ('space-framework', 'SPACE framework - satisfaction, performance, activity, communication, efficiency metrics'),
    ('engineering-effectiveness', 'Engineering effectiveness - velocity, quality, developer satisfaction, toil, investment'),
    ('incident-metrics', 'Incident metrics - MTTD, MTTA, MTTR, MTBF, incident frequency, severity distribution'),
    ('deployment-analytics', 'Deployment analytics - success rate, rollback rate, duration, artifact size, testing coverage'),
    # Advanced Prompt Engineering
    ('meta-prompting', 'Meta-prompting - prompts that generate prompts, self-improving, automated optimization'),
    ('prompt-injection-defense', 'Prompt injection defense - input sanitization, output validation, context isolation'),
    ('system-prompt-design', 'System prompt design - role definition, constraints, examples, output format, safety'),
    ('few-shot-advanced', 'Few-shot prompting advanced - example selection, ordering, coverage, chain-of-thought examples'),
    ('prompt-chaining', 'Prompt chaining - sequential prompts, output passing, conditional branching, error handling'),
    # Advanced AI Infrastructure
    ('vector-search-optimization', 'Vector search optimization - index tuning, quantization, filtering, batch queries, caching'),
    ('embedding-pipeline', 'Embedding pipeline - chunking strategy, models, storage, updates, incremental indexing'),
    ('llm-gateway-patterns', 'LLM gateway patterns - load balancing, fallbacks, retries, cost tracking, logging'),
    ('ai-cache-patterns', 'AI cache patterns - exact match, semantic cache, TTL strategies, invalidation, cost savings'),
    ('model-registry-patterns', 'Model registry patterns - versioning, metadata, lineage, promotion, deprecation'),
    # Advanced System Design
    ('rate-limiting-design', 'Rate limiting system design - token bucket, leaky bucket, sliding window, distributed'),
    ('url-shortener-design', 'URL shortener design - hash generation, collision handling, expiry, analytics, scaling'),
    ('notification-system-design', 'Notification system design - fan-out, push/pull, priority, batching, deduplication'),
    ('search-system-design', 'Search system design - indexing, ranking, typeahead, spell correction, personalization'),
    ('feed-system-design', 'Feed system design - fan-out on write/read, ranking, pagination, real-time updates'),
    # Advanced Programming Concepts
    ('effect-systems', 'Effect systems - algebraic effects, handlers, scoped effects, IO monad, type-level effects'),
    ('dependent-types-practical', 'Dependent types practical - Agda, Lean, Coq patterns, refinement types, liquid types'),
    ('session-types', 'Session types - communication protocols, linearity, duality, multiparty sessions, Scribble'),
    ('actor-model-advanced', 'Actor model advanced - Erlang/OTP, Akka, supervision trees, let it crash, location transparency'),
    ('algebraic-data-types', 'Algebraic data types - sum types, product types, recursive types, pattern matching, GADTs'),
    # Advanced DevEx Tooling
    ('dev-container-advanced', 'Dev containers advanced - features, lifecycle scripts, remote attach, compose, GitHub Codespaces'),
    ('mise-advanced', 'mise (rtx) advanced - tool versions, environments, tasks, plugins, shims, lockfile'),
    ('direnv-advanced', 'direnv advanced - .envrc patterns, stdlib, layout, watch_file, approvals, security'),
    ('lefthook-advanced', 'Lefthook advanced - parallel, sequential, glob, exclude, templates, piped, follow'),
    ('pre-commit-advanced', 'pre-commit advanced - hooks, stages, language, dependencies, local hooks, CI integration'),
    # Advanced Data Formats
    ('apache-orc', 'Apache ORC - columnar storage, ACID, predicate pushdown, schema evolution, compression'),
    ('arrow-flight', 'Apache Arrow Flight - high-throughput data transfer, SQL, authentication, streaming'),
    ('lance-format', 'Lance format - ML data format, random access, vector index, versioning, DuckDB integration'),
    ('zarr-advanced', 'Zarr advanced - hierarchical, chunked, compressed arrays, N5, OME-Zarr, cloud storage'),
    ('hdf5-advanced', 'HDF5 advanced - groups, datasets, attributes, virtual datasets, parallel I/O, filters'),
    # Advanced Edge and CDN
    ('edge-caching-strategies', 'Edge caching strategies - cache headers, surrogate keys, stale-while-revalidate, CDN API'),
    ('edge-compute-patterns', 'Edge compute patterns - A/B testing, personalization, geolocation, rate limiting at edge'),
    ('cdn-security', 'CDN security - DDoS mitigation, bot management, WAF at edge, TLS 1.3, certificate pinning'),
    ('image-cdn', 'Image CDN - format negotiation, responsive images, transformations, Cloudinary, Imgix, Cloudflare'),
    ('multi-cdn-strategy', 'Multi-CDN strategy - provider selection, failover, performance measurement, cost optimization'),
    # Advanced Resilience Patterns
    ('bulkhead-advanced', 'Bulkhead advanced - thread pools, semaphore, process isolation, resource limits, monitoring'),
    ('timeout-patterns', 'Timeout patterns - connection, read, write, overall, cascading, compensation, hedged requests'),
    ('retry-strategies', 'Retry strategies - exponential backoff, jitter, retry budget, idempotency, circuit breaker'),
    ('fallback-patterns', 'Fallback patterns - static fallback, degraded mode, cache fallback, graceful degradation'),
    ('shed-load-patterns', 'Load shedding patterns - admission control, priority queues, backpressure, graceful degradation'),
    # Advanced Agentic Patterns
    ('plan-and-execute', 'Plan and execute agents - planner, executor, replanning, tool selection, task tracking'),
    ('agent-reflection', 'Agent reflection patterns - output critique, self-evaluation, revision, quality gating'),
    ('tool-selection-agents', 'Tool selection optimization - tool descriptions, embeddings, routing, dynamic toolsets'),
    ('agent-collaboration', 'Agent collaboration patterns - role assignment, message passing, consensus, dispute resolution'),
    ('context-window-management', 'Context window management - summarization, memory compression, retrieval, forgetting'),
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
