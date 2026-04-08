
import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # Advanced Monitoring Backends
    ('thanos-advanced', 'Thanos advanced - sidecar, store, query, compactor, rule, multi-tenancy, downsampling'),
    ('cortex-advanced', 'Cortex advanced - microservices, blocks, chunks, sharding, compaction, ruler, alertmanager'),
    ('m3db-advanced', 'M3DB advanced - storage, aggregation, coordinator, multi-zone, compaction, query, retention'),
    ('influxdb-3', 'InfluxDB 3.0 - IOx, SQL, columnar storage, object store, unlimited cardinality, partitioning'),
    ('grafana-mimir', 'Grafana Mimir - long-term Prometheus storage, ruler, alertmanager, compactor, sharding'),
    # Advanced Data Science Libraries
    ('lifelines-survival', 'lifelines survival analysis - Kaplan-Meier, Cox model, log-rank tests, time-varying covariates'),
    ('imbalanced-learn', 'imbalanced-learn - SMOTE, ADASYN, borderline SMOTE, ensemble methods, under-sampling'),
    ('optuna-advanced', 'Optuna advanced - TPE, CMA-ES, pruning, distributed, dashboard, storages, integration'),
    ('shap-advanced', 'SHAP advanced - TreeExplainer, DeepExplainer, KernelExplainer, interaction values, plots'),
    ('yellowbrick-vis', 'Yellowbrick - ML visualization, score visualizers, model selection, text analytics, cluster'),
    # Advanced Web3 Infrastructure
    ('ipfs-advanced', 'IPFS advanced - content addressing, IPLD, libp2p, pinning, gateways, pubsub, IPNS'),
    ('filecoin-storage', 'Filecoin storage - deals, retrieval, sectors, proofs, FVM, data onramp, preservation'),
    ('the-graph-protocol', 'The Graph protocol - subgraphs, indexers, delegators, curators, GRT, Studio, queries'),
    ('chainlink-advanced', 'Chainlink advanced - price feeds, VRF, automation, CCIP, Functions, Data Streams, DECO'),
    ('hardhat-testing', 'Hardhat advanced testing - fixtures, snapshots, custom matchers, coverage, gas reporter'),
    # Advanced Orchestration
    ('nomad-advanced-patterns', 'Nomad advanced patterns - spread scheduling, constraint, affinity, multi-region, namespaces'),
    ('mesos-marathon', 'Apache Mesos/Marathon - resource isolation, frameworks, two-level scheduling, offers'),
    ('swarm-mode', 'Docker Swarm mode - services, replicas, secrets, configs, routing mesh, rolling updates'),
    ('k3s-lightweight', 'k3s lightweight Kubernetes - single binary, SQLite, embedded LB, Traefik, local path'),
    ('rke2-advanced', 'RKE2 - Rancher Kubernetes, CIS hardening, etcd snapshots, agent, server, CNI options'),
    # Advanced Frontend Architecture
    ('micro-frontend-module-fed', 'Micro-frontend module federation - webpack 5, Vite, sharing, dynamic remotes, TypeScript'),
    ('islands-architecture-advanced', 'Islands architecture advanced - Astro, Fresh, Marko, partial hydration strategies'),
    ('resumable-framework', 'Resumable framework - Qwik, fine-grained lazy loading, serialization, SSR, optimizer'),
    ('streaming-ssr', 'Streaming SSR - React 18 Suspense, Next.js app router, Remix defer, edge streaming'),
    ('edge-rendering', 'Edge rendering patterns - Vercel edge, CF Workers, Netlify edge, partial prerendering'),
    # Advanced Database Internals
    ('btree-internals', 'B-tree internals - page layout, splits, merges, WAL, buffer pool, MVCC, lock manager'),
    ('lsm-tree-advanced', 'LSM-tree advanced - memtable, SSTable, compaction strategies, bloom filters, level design'),
    ('mvcc-advanced', 'MVCC advanced - snapshot isolation, version chains, vacuum, visibility, conflict detection'),
    ('write-ahead-log', 'Write-ahead log advanced - WAL format, checkpointing, recovery, replication, archiving'),
    ('query-planner-advanced', 'Query planner advanced - statistics, cardinality estimation, join ordering, hint systems'),
    # Advanced Infrastructure Security
    ('secret-zero-problem', 'Secret zero problem - bootstrapping trust, workload identity, Vault agent, SPIRE, SPIFFE'),
    ('pki-advanced', 'PKI advanced - certificate lifecycle, ACME protocol, OCSP, CT logs, HSM integration'),
    ('mtls-advanced', 'mTLS advanced - certificate pinning, SPIFFE/SPIRE, workload identity, rotation automation'),
    ('network-policy-advanced', 'Network policy advanced - Calico GlobalNetworkPolicy, Cilium NetworkPolicy, egress'),
    ('image-security-advanced', 'Container image security - distroless, scratch, rootless builds, SBOM, attestation'),
    # Advanced Frontend State Management
    ('tanstack-query-advanced', 'TanStack Query v5 advanced - infinite queries, optimistic updates, mutations, SSR'),
    ('swr-advanced', 'SWR advanced - revalidation strategies, middleware, devtools, subscription, useSWRInfinite'),
    ('zustand-advanced', 'Zustand v4 advanced - slices, middlewares, devtools, immer, persist, subscriptions'),
    ('legend-state', 'Legend-State - fine-grained reactivity, computed, persistence, sync, React, React Native'),
    ('nanostores-advanced', 'Nanostores - atomic, computed, lifecycle, router, persistent, React/Vue/Svelte adapters'),
    # Advanced Testing Frameworks
    ('hypothesis-advanced', 'Hypothesis advanced - strategies, composite, deferred, stateful testing, coverage, Django'),
    ('pact-advanced', 'Pact contract testing advanced - provider verification, broker, can-i-deploy, webhooks'),
    ('testcontainers-advanced', 'Testcontainers advanced - custom containers, networks, compose, wait strategies, reuse'),
    ('approval-tests', 'Approval tests - golden master, text/binary comparison, reporters, scrubbers, combination'),
    ('mutation-testing-advanced', 'Mutation testing advanced - Stryker, PITest, mutmut, thresholds, incremental, reporting'),
    # Advanced Platform Engineering
    ('score-workloads', 'Score workloads - platform-agnostic workload spec, Helm, Compose, Humanitec translator'),
    ('radius-platform', 'Radius platform - cloud-agnostic app deployment, recipes, environments, connections, CLI'),
    ('dapr-advanced', 'Dapr advanced - state stores, pub/sub, bindings, workflows, actors, sidecar, resiliency'),
    ('porter-iac', 'Porter - cloud-native application bundles, CNAB, mixins, credentials, parameters, publish'),
    ('waypoint-advanced', 'HashiCorp Waypoint advanced - runners, plugins, URL service, workspace, release mgmt'),
    # Advanced AI Model Serving
    ('torchserve-advanced', 'TorchServe advanced - custom handlers, model archiver, metrics, KFServing, multi-model'),
    ('seldon-advanced', 'Seldon Core/Deploy advanced - inference graphs, custom servers, explainers, drift detection'),
    ('kserve-advanced', 'KServe advanced - InferenceService, canary, custom transformer, predictor, explainer'),
    ('ray-serve-production', 'Ray Serve production - deployments, ingress, streaming, gRPC, autoscaling, GPU'),
    ('triton-model-repo', 'Triton model repository - model configs, dynamic batching, sequence batching, ensembles'),
    # Advanced Distributed Caching
    ('hazelcast-advanced', 'Hazelcast advanced - distributed maps, near-cache, WAN replication, CP subsystem, SQL'),
    ('apache-ignite', 'Apache Ignite advanced - data grid, compute grid, SQL, transactions, ML, persistent store'),
    ('ehcache-advanced', 'Ehcache advanced - tiered storage, clustering, write-behind, caching strategies, JCache'),
    ('caffeine-cache', 'Caffeine cache - W-TinyLFU, advanced refresh, expiry policies, stats, async loading'),
    ('varnish-cache', 'Varnish cache - VCL, ESI, Varnish Modules, grace, saint mode, backend health probes'),
    # Advanced API Development
    ('openapi-code-first', 'OpenAPI code-first - Springdoc, Fastify swagger, NestJS swagger, auto-generation, validation'),
    ('api-design-first', 'API design-first - contract-driven, Spectral linting, mocking, generation, validation'),
    ('graphql-subscriptions', 'GraphQL subscriptions - WebSocket, SSE, Redis pub/sub, auth, scalability, filtering'),
    ('rest-maturity-model', 'REST maturity model - Richardson maturity, HATEOAS implementation, HAL, JSON:API, Siren'),
    ('grpc-best-practices', 'gRPC best practices - error handling, metadata, interceptors, health checking, reflection'),
    # Advanced Infrastructure Patterns
    ('tofu-stacks', 'OpenTofu stacks - stack management, composition, remote state, providers, module reuse'),
    ('atlantis-terraform', 'Atlantis - Terraform pull request automation, workflows, policies, locking, CI/CD'),
    ('env0-iac', 'env0 - infrastructure orchestration, self-service, workflows, cost, RBAC, GitOps'),
    ('spacelift-advanced', 'Spacelift advanced - stacks, modules, policies, worker pools, contexts, triggers'),
    ('scalr-terraform', 'Scalr - Terraform remote operations, workspaces, policy, variable sets, drift detection'),
    # Advanced Cloud Cost
    ('opencost-advanced', 'OpenCost advanced - Kubernetes cost allocation, cloud costs, external costs, API'),
    ('infracost-advanced', 'Infracost advanced - CI/CD integration, policies, actual costs, Terraform, modules'),
    ('cast-ai', 'CAST AI - Kubernetes cost optimization, autoscaler, workload scaling, spot, reserved'),
    ('spot-instances', 'Spot/preemptible instances - interruption handling, diversification, checkpointing, savings'),
    ('rightsizing-automation', 'Rightsizing automation - VPA, Goldilocks, resource recommendations, cost impact'),
    # Advanced Event-Driven Architecture
    ('event-catalog', 'EventCatalog - event documentation, AsyncAPI, visualization, versioning, owners, search'),
    ('event-versioning', 'Event versioning strategies - schema evolution, upcasters, compatibility, registry, routing'),
    ('domain-events', 'Domain events advanced - aggregate roots, event publishing, eventual consistency, saga'),
    ('event-replay', 'Event replay patterns - dead letter queue, replay service, projection rebuild, ordering'),
    ('reactive-manifesto', 'Reactive systems - responsiveness, resilience, elastic, message-driven, Akka, Project Reactor'),
    # Advanced Data Catalog
    ('datahub-advanced', 'DataHub advanced - metadata models, ingestion sources, lineage, search, actions, APIs'),
    ('amundsen-catalog', 'Amundsen data catalog - metadata, search, lineage, table detail, preview, owners'),
    ('apache-atlas-advanced', 'Apache Atlas advanced - type system, entity CRUD, lineage, classification, auditing'),
    ('open-metadata', 'OpenMetadata advanced - data quality, lineage, collaboration, profiling, alerts, API'),
    ('data-catalog-design', 'Data catalog design - business glossary, metadata standards, ownership, search, data quality'),
    # Advanced SRE Practices
    ('error-budget-policy', 'Error budget policy - exhaustion response, freeze triggers, reliability investment, reviews'),
    ('capacity-planning-advanced', 'Capacity planning advanced - load testing, growth modeling, headroom, seasonal peaks'),
    ('on-call-engineering', 'On-call engineering - schedule design, toil reduction, documentation, runbooks, postmortems'),
    ('sli-slo-advanced', 'SLI/SLO advanced - user journey SLOs, composite SLIs, multi-window alerting, burn rates'),
    ('production-readiness', 'Production readiness review - checklist, scorecard, security, reliability, observability'),
    # Advanced AI Safety
    ('red-teaming-llm', 'LLM red teaming - adversarial prompts, jailbreaks, harmfulness evaluation, automated testing'),
    ('constitutional-ai-advanced', 'Constitutional AI advanced - self-critique, revision, RLHF from CAI, principles design'),
    ('model-evaluation-safety', 'Model evaluation for safety - benchmarks, evals, human evaluation, automated assessment'),
    ('output-filtering', 'Output filtering advanced - classifiers, pattern matching, toxicity detection, guardrails'),
    ('ai-incident-management', 'AI incident management - detection, response, remediation, retrospective, prevention'),
    # Advanced Low-Code Platforms
    ('appsmith-advanced', 'Appsmith advanced - custom widgets, datasource plugins, modules, packages, audit logs'),
    ('retool-advanced', 'Retool advanced - custom components, scripting, workflows, modules, embed, staging'),
    ('budibase-advanced', 'Budibase advanced - data providers, custom components, automation, RBAC, self-hosting'),
    ('tooljet-advanced', 'ToolJet advanced - custom components, workflows, datasources, RBAC, multi-env, SSO'),
    ('ui-bakery', 'UI Bakery - app builder, REST, SQL, drag-drop, auth, deployment, white-label'),
    # Advanced Logging
    ('structured-logging-advanced', 'Structured logging advanced - correlation IDs, sampling, redaction, enrichment, sinks'),
    ('log-parsing-advanced', 'Log parsing advanced - grok patterns, dissect, JSON, multiline, extraction, normalization'),
    ('centralized-logging', 'Centralized logging - ELK, Loki, Splunk, aggregation, retention, compliance, search'),
    ('log-based-metrics', 'Log-based metrics - log-to-metric, Prometheus, Datadog, alerting, dashboards, SLIs'),
    ('audit-trail-design', 'Audit trail design - immutability, chain of custody, WORM, search, export, compliance'),
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
