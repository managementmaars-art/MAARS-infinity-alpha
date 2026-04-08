
import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # More programming languages
    ('f-sharp-dotnet', 'F# .NET functional programming - type providers, computation expressions, async, domain modeling'),
    ('erlang-otp', 'Erlang OTP - processes, supervisors, gen_server, distributed Erlang, hot code reload'),
    ('julia-scientific', 'Julia scientific computing - multiple dispatch, GPU, parallel, differential equations, optimization'),
    ('fortran-hpc', 'Fortran HPC - array operations, parallel computing, OpenMP, MPI, scientific libraries'),
    ('cobol-modernization', 'COBOL modernization - legacy systems, mainframe, micro Focus, GnuCOBOL, integration'),
    ('ada-safety', 'Ada safety-critical - SPARK, contracts, tasking, real-time, DO-178C, certification'),
    ('prolog-logic', 'Prolog logic programming - facts, rules, queries, constraint solving, natural language'),
    ('smalltalk-oop', 'Smalltalk/Pharo OOP - message passing, reflection, live coding, image-based, Squeak'),
    # More web frameworks
    ('fresh-deno', 'Fresh Deno framework - island architecture, JSX, server-side rendering, edge functions'),
    ('hono-framework', 'Hono web framework - ultra-fast, edge-first, TypeScript, Bun/Deno/Node/Cloudflare Workers'),
    ('elysia-bun', 'Elysia Bun framework - type-safe, end-to-end type safety, Eden Treaty, validation, plugins'),
    ('encore-go', 'Encore Go framework - cloud-native Go, auto-infrastructure, distributed tracing, local env'),
    ('chi-router', 'Chi router Go - lightweight middleware, composable, context-aware, idiomatic Go'),
    ('fiber-go', 'Fiber Go framework - Express-inspired, fast HTTP, middleware, routing, WebSocket, template'),
    ('axum-rust', 'Axum Rust web - tower middleware, type-safe extractors, routing, WebSocket, async'),
    ('warp-rust', 'Warp Rust web framework - filter-based, composable, async, WebSocket, TLS, compression'),
    # More databases
    ('yugabyte-db', 'YugabyteDB - distributed SQL, PostgreSQL compatible, YSQL, YCQL, geo-distribution'),
    ('vitess-mysql', 'Vitess MySQL sharding - horizontal scaling, VSchema, VTAdmin, connection pooling, backups'),
    ('spanner-google', 'Google Cloud Spanner - globally distributed, ACID, SQL, interleaving, change streams'),
    ('bigtable-nosql', 'Google Cloud Bigtable - wide-column, HBase API, time series, IoT, ML feature serving'),
    ('firestore-db', 'Cloud Firestore - document DB, real-time sync, offline, security rules, composite indexes'),
    ('supabase-advanced', 'Supabase advanced - Row Level Security, Edge Functions, Realtime, Storage, Auth'),
    ('planetscale-db', 'PlanetScale database - MySQL branching, non-blocking schema changes, query insights'),
    ('singlestore-db', 'SingleStoreDB - HTAP, in-memory, vector search, pipelines, notebooks, universal storage'),
    # More AI/ML
    ('autogen-framework', 'AutoGen multi-agent - conversable agents, group chat, code execution, human-in-loop'),
    ('crewai-agents', 'CrewAI agents - role-based agents, tasks, tools, process flows, hierarchical, sequential'),
    ('phidata-agents', 'Phidata agents - agentic systems, memory, knowledge, tools, reasoning, structured outputs'),
    ('dspy-framework', 'DSPy framework - declarative LLM programming, optimizers, signatures, modules, evaluation'),
    ('semantic-kernel', 'Semantic Kernel - AI orchestration, plugins, planners, memory, .NET/Python/Java SDKs'),
    ('haystack-pipeline', 'Haystack NLP pipelines - document stores, retrievers, readers, generators, evaluation'),
    ('llamaindex-advanced', 'LlamaIndex advanced - multi-modal, agents, workflows, sub-question, knowledge graphs'),
    ('langchain-advanced', 'LangChain advanced - LCEL, graphs, complex chains, memory, retrieval, evaluation'),
    # More cloud services
    ('aws-sagemaker', 'AWS SageMaker - training, inference, Feature Store, Model Registry, Pipelines, Studio'),
    ('aws-glue', 'AWS Glue - ETL, Data Catalog, Crawlers, DynamicFrames, Spark, streaming'),
    ('aws-athena', 'AWS Athena - serverless SQL, S3 queries, partitioning, Iceberg tables, federated queries'),
    ('aws-kinesis', 'AWS Kinesis - Data Streams, Firehose, Analytics, enhanced fan-out, partition keys'),
    ('gcp-dataflow', 'GCP Dataflow - Apache Beam runner, streaming, batch, Flex Templates, SQL, windowing'),
    ('gcp-pubsub', 'GCP Pub/Sub - topics, subscriptions, push/pull, ordering, dead-letter, Lite, schemas'),
    ('azure-functions', 'Azure Functions - triggers, bindings, Durable Functions, KEDA, Flex Consumption, isolated'),
    ('azure-service-bus', 'Azure Service Bus - queues, topics, subscriptions, sessions, dead-letter, transactions'),
    # More DevOps
    ('packer-images', 'HashiCorp Packer - machine images, builders, provisioners, HCL2, AMIs, Vagrant boxes'),
    ('vagrant-dev', 'Vagrant development environments - Vagrantfile, providers, provisioners, boxes, networking'),
    ('nomad-orchestration', 'HashiCorp Nomad - job scheduling, task groups, drivers, service discovery, Consul integration'),
    ('consul-service-mesh', 'HashiCorp Consul - service discovery, health checks, KV store, Connect service mesh'),
    ('boundary-access', 'HashiCorp Boundary - identity-based access, sessions, targets, credential brokering'),
    ('waypoint-deploy', 'HashiCorp Waypoint - deploy, release, destroy, URL service, logs, exec'),
    # More frontend
    ('react-query-advanced', 'React Query (TanStack Query) advanced - optimistic updates, infinite queries, prefetching'),
    ('zustand-state', 'Zustand state management - stores, slices, middleware, devtools, immer, subscriptions'),
    ('jotai-state', 'Jotai atomic state - atoms, derived atoms, async atoms, React Suspense, persistence'),
    ('xstate-machines', 'XState state machines - actors, states, transitions, guards, actions, services, Stately'),
    ('radix-ui', 'Radix UI primitives - unstyled accessible components, Headless UI, shadcn integration'),
    ('shadcn-ui', 'shadcn/ui - copy-paste components, Tailwind, Radix primitives, theming, CLI, registry'),
    ('framer-motion', 'Framer Motion - animation library, layout animations, gestures, exit animations, spring'),
    ('react-spring', 'React Spring physics - spring-based animations, hooks, interpolation, trails, parallax'),
    # More testing
    ('playwright-advanced', 'Playwright advanced - parallel tests, fixtures, page object model, API testing, tracing'),
    ('jest-advanced', 'Jest advanced - custom matchers, module mocking, fake timers, coverage thresholds, setup'),
    ('testing-library', 'Testing Library - user-event, queries, async utils, custom renders, accessibility queries'),
    ('storybook-advanced', 'Storybook advanced - addons, controls, interactions, play functions, chromatic, a11y'),
    ('k6-advanced', 'k6 advanced - custom metrics, browser testing, scenarios, threshold, extensions, cloud'),
    # More security
    ('vault-advanced', 'Vault advanced - dynamic secrets, PKI, database credentials, transit encryption, namespaces'),
    ('falco-runtime', 'Falco runtime security - rules, alerts, eBPF, syscall monitoring, cloud detection'),
    ('trivy-scanning', 'Trivy vulnerability scanning - containers, filesystems, repos, SBOMs, Kubernetes, cloud'),
    ('cosign-supply-chain', 'Cosign supply chain - container signing, attestations, policy enforcement, Sigstore'),
    ('gvisor-sandbox', 'gVisor container sandbox - runsc, kernel interception, security isolation, Kubernetes'),
    # More data engineering
    ('great-expectations-advanced', 'Great Expectations advanced - custom expectations, data docs, checkpoints, profilers'),
    ('data-build-tool', 'dbt Core advanced - packages, macros, Jinja, hooks, sources, exposures, semantic models'),
    ('apache-nifi', 'Apache NiFi - data flow, processors, provenance, clustering, templates, REST API'),
    ('mage-ai', 'Mage AI - modern data pipeline, streaming, dbt integration, ML pipelines, orchestration'),
    ('prefect-workflow', 'Prefect workflow - flows, tasks, deployments, work pools, blocks, schedules, observability'),
    ('dagster-assets', 'Dagster - software-defined assets, jobs, ops, resources, sensors, schedules, Dagster Cloud'),
    # More AI platforms
    ('replicate-api', 'Replicate API - run open-source models, predictions, streaming, fine-tuning, deployments'),
    ('modal-compute', 'Modal compute - serverless GPU, web endpoints, scheduled functions, sandboxes, volumes'),
    ('runpod-inference', 'RunPod - GPU cloud, serverless inference, pods, templates, network volumes, OpenAI compat'),
    ('banana-dev', 'Banana.dev - serverless ML inference, cold start optimization, scaling, GPU inference'),
    ('deepinfra-inference', 'DeepInfra inference - open-source model hosting, OpenAI-compatible API, fine-tuning'),
    # More protocols/standards
    ('oauth2-advanced', 'OAuth2/OIDC advanced - PKCE, device flow, pushed authorization, DPoP, PAR, RAR'),
    ('saml-sso', 'SAML 2.0 SSO - assertions, metadata, SP/IdP setup, attribute mapping, encryption'),
    ('ldap-directory', 'LDAP directory - schema, filters, operations, Active Directory, OpenLDAP, authentication'),
    ('webauthn-passkeys', 'WebAuthn/Passkeys - FIDO2, credential creation, assertion, resident keys, attestation'),
    ('mtls-certificates', 'mTLS certificates - mutual TLS, PKI, certificate rotation, SPIFFE/SPIRE, service identity'),
    # More AI research
    ('diffusion-models', 'Diffusion models - DDPM, DDIM, score matching, CFG, latent diffusion, conditioning'),
    ('llm-pretraining', 'LLM pretraining - data curation, tokenization, distributed training, checkpointing, eval'),
    ('rlhf-alignment', 'RLHF alignment - reward modeling, PPO, GRPO, DPO, constitutional AI, preference data'),
    ('multimodal-models', 'Multimodal models - vision-language, audio-language, video understanding, interleaved'),
    ('model-compression', 'Model compression - pruning, quantization, knowledge distillation, sparsity, GPTQ, AWQ'),
    # More tools
    ('terraform-advanced', 'Terraform advanced - modules, workspaces, state management, providers, testing, CDK'),
    ('ansible-advanced', 'Ansible advanced - roles, collections, AWX, dynamic inventory, vault, callback plugins'),
    ('puppet-automation', 'Puppet automation - manifests, classes, resources, modules, Hiera, PuppetDB, PE'),
    ('chef-automation', 'Chef automation - cookbooks, recipes, attributes, resources, Test Kitchen, Chef Infra'),
    ('saltstack', 'SaltStack - states, pillars, grains, modules, reactors, beacons, Salt SSH, orchestration'),
    # More observability
    ('jaeger-tracing', 'Jaeger distributed tracing - traces, spans, sampling, storage backends, UI, operator'),
    ('zipkin-tracing', 'Zipkin tracing - instrumentation, storage, dependencies, trace search, brave library'),
    ('pyroscope-profiling', 'Pyroscope continuous profiling - flamegraphs, eBPF, language SDKs, Grafana integration'),
    ('ebpf-observability', 'eBPF observability - Cilium, Pixie, Hubble, BCC, bpftrace, kernel tracing'),
    ('victoria-metrics', 'VictoriaMetrics - high-performance TSDB, MetricsQL, cluster mode, alerting, Grafana'),
    # More specific domains
    ('geospatial-gis', 'Geospatial GIS - GDAL, Shapely, Fiona, PostGIS, tile servers, vector tiles, analysis'),
    ('graph-algorithms', 'Graph algorithms - NetworkX, Gephi, PageRank, shortest path, community detection, Neo4j'),
    ('scientific-computing', 'Scientific computing - SciPy, NumPy, symbolic math, ODEs, optimization, linear algebra'),
    ('signal-processing', 'Signal processing - FFT, filters, wavelets, spectral analysis, audio processing, SciPy'),
    ('image-processing', 'Image processing - OpenCV, PIL/Pillow, scikit-image, morphology, segmentation, features'),
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
