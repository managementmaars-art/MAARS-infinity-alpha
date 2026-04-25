
import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # Specific AI/LLM infrastructure
    ('vllm-advanced', 'vLLM advanced - PagedAttention, continuous batching, tensor parallelism, quantization, lora'),
    ('sglang-advanced', 'SGLang advanced - RadixAttention, constraint decoding, multi-modal, batch inference, CUDA graphs'),
    ('tensorrt-advanced', 'TensorRT advanced - FP8, graph optimization, custom plugins, dynamic shapes, profiling'),
    ('onnxruntime-advanced', 'ONNX Runtime advanced - execution providers, optimizations, quantization, custom ops'),
    ('mlc-llm', 'MLC LLM - machine learning compilation, mobile deployment, WebGPU, iOS/Android, optimization'),
    ('exllamav2', 'ExLlamaV2 - fast GPTQ inference, speculative decoding, EXL2 quantization, continuous batching'),
    ('llamacpp-server', 'llama.cpp server - REST API, context management, grammar constraints, multimodal, batching'),
    ('mistral-finetune', 'Mistral fine-tuning - LoRA, instruction tuning, data formatting, evaluation, deployment'),
    # More LLM frameworks
    ('smolagents-hf', 'SmolAgents Hugging Face - lightweight agents, code agents, tool-calling, multi-agent'),
    ('agno-framework', 'Agno agent framework - agentic workflows, memory, tools, knowledge, multi-modal agents'),
    ('pydantic-ai-advanced', 'Pydantic AI advanced - type-safe agents, dependencies, result validators, streaming'),
    ('controlflow-agents', 'ControlFlow agents - task-based AI workflows, flow control, human-in-loop, typed results'),
    ('mirascope-llm', 'Mirascope LLM library - functional approach, type hints, multi-provider, extraction, streaming'),
    ('ell-framework', 'ELL language model framework - prompts as programs, versioning, tracing, optimization'),
    # More data tools
    ('polars-advanced', 'Polars advanced - lazy evaluation, expressions, plugins, streaming, Arrow integration'),
    ('ibis-framework', 'Ibis framework - portable SQL, multiple backends, lazy evaluation, pandas-like API'),
    ('datafusion-rust', 'Apache DataFusion - embeddable query engine, Arrow, SQL, streaming, custom datasources'),
    ('ballista-distributed', 'Apache Ballista - distributed compute, Arrow Flight, DataFusion, query federation'),
    ('lakeformation', 'AWS Lake Formation - data lake governance, fine-grained access, blueprints, transactions'),
    ('unity-catalog', 'Unity Catalog - open data+AI governance, Delta sharing, fine-grained ACLs, Databricks'),
    # More frontend
    ('remix-advanced', 'Remix advanced - loaders, actions, nested routes, optimistic UI, streaming, error boundaries'),
    ('astro-advanced', 'Astro advanced - islands, content collections, SSR, view transitions, integrations, db'),
    ('nuxt-advanced', 'Nuxt 3 advanced - server components, Nitro, layers, modules, auto-imports, hybrid rendering'),
    ('sveltekit-advanced', 'SvelteKit advanced - load functions, form actions, streaming, hooks, error handling, adapter'),
    ('angular-signals', 'Angular signals - reactivity, computed, effects, resource API, deferred loading'),
    ('tanstack-router', 'TanStack Router - type-safe routing, search params, loaders, code splitting, devtools'),
    ('tanstack-start', 'TanStack Start - full-stack React, SSR, server functions, type-safe API, Vinxi'),
    # More backend
    ('hono-advanced', 'Hono advanced - middleware, RPC, testing, OpenAPI, rate limiting, WebSocket, Cloudflare'),
    ('bun-server', 'Bun HTTP server - native fetch, WebSocket, streaming, file serving, hot reload, performance'),
    ('uv-python', 'uv Python package manager - ultra-fast pip, lockfiles, workspaces, toolchains, build'),
    ('rye-python', 'Rye Python toolchain - project management, virtual envs, lockfiles, scripts, global tools'),
    ('poetry-advanced', 'Poetry advanced - groups, extras, plugins, local dependencies, private repos, CI patterns'),
    # More cloud
    ('cloudflare-tunnels', 'Cloudflare Tunnels - secure access, zero trust, private networks, SSH, RDP, kubectl'),
    ('cloudflare-zero-trust', 'Cloudflare Zero Trust - Access, Gateway, WARP, Browser Isolation, CASB, DLP'),
    ('cloudflare-pages', 'Cloudflare Pages - JAMstack, Git integration, preview deployments, Functions, redirects'),
    ('vercel-edge', 'Vercel Edge Functions - edge runtime, geo-routing, A/B testing, caching, middleware'),
    ('netlify-edge', 'Netlify Edge Functions - Deno-based, geolocation, A/B testing, personalization, caching'),
    ('fly-machines', 'Fly Machines API - fast boot VMs, ephemeral machines, regions, GPU, Tigris storage'),
    # More Kubernetes
    ('gateway-api-k8s', 'Kubernetes Gateway API - HTTPRoute, GRPCRoute, TLSRoute, gateway classes, traffic management'),
    ('crossplane-advanced', 'Crossplane advanced - compositions, XRDs, functions, pipeline mode, external secrets'),
    ('flux-advanced', 'Flux CD advanced - multi-tenancy, Helm releases, image automation, notifications, alerts'),
    ('argo-workflows', 'Argo Workflows - DAG, steps, artifacts, templates, inputs/outputs, parameterization'),
    ('tekton-advanced', 'Tekton advanced - custom tasks, Tekton Chains, supply chain security, triggers, catalog'),
    # More messaging
    ('nats-messaging', 'NATS messaging - pub/sub, request/reply, JetStream, streaming, KV, object store, clusters'),
    ('rabbitmq-advanced', 'RabbitMQ advanced - exchanges, routing, dead letters, priority queues, shovel, federation'),
    ('activemq-patterns', 'ActiveMQ patterns - topics, queues, durable subscribers, virtual topics, clustering'),
    ('pulsar-messaging', 'Apache Pulsar - multi-tenancy, geo-replication, tiered storage, functions, connectors'),
    ('redpanda', 'Redpanda - Kafka-compatible, no ZK, transactions, Wasm transforms, shadow indexing'),
    # More observability
    ('otel-advanced', 'OpenTelemetry advanced - custom exporters, sampling strategies, baggage, context propagation'),
    ('signoz-observability', 'SigNoz observability - open-source APM, logs, metrics, traces, dashboards, alerts'),
    ('coroot-monitoring', 'Coroot monitoring - eBPF-based, service maps, SLOs, cost monitoring, deployment tracking'),
    ('ground-x-observability', 'Groundcover observability - eBPF sensors, cloud-native APM, Kubernetes-native'),
    ('axiom-logging', 'Axiom logging - structured logs, APM, real-time streaming, OpenTelemetry, Vercel logs'),
    # More security
    ('wazuh-siem', 'Wazuh SIEM - threat detection, compliance, vulnerability detection, incident response, agents'),
    ('graylog-siem', 'Graylog SIEM - log management, threat detection, dashboards, pipelines, correlation'),
    ('thehive-soar', 'TheHive SOAR - incident response, case management, observables, alerts, Cortex analyzers'),
    ('shuffle-soar', 'Shuffle SOAR - open-source automation, apps, workflows, triggers, case management'),
    ('misp-threat-intel', 'MISP threat intelligence - IoCs, threat sharing, galaxies, correlation, APIs, feeds'),
    # More networking
    ('wireguard-vpn', 'WireGuard VPN - modern VPN, kernel module, peers, keys, routing, performance'),
    ('cilium-networking', 'Cilium networking - eBPF, network policy, Hubble observability, service mesh, BGP'),
    ('calico-network', 'Project Calico - network policy, BGP routing, eBPF, WireGuard encryption, IPAM'),
    ('metallb-lb', 'MetalLB load balancer - BGP, Layer 2, address pools, Kubernetes LoadBalancer'),
    ('cert-manager', 'cert-manager - automatic TLS, ACME, Let\'s Encrypt, Vault, certificates, issuers'),
    # More databases
    ('redis-cluster', 'Redis Cluster - data sharding, replication, failover, slots, CLUSTER commands, clients'),
    ('valkey-db', 'Valkey database - Redis fork, open-source, compatible, clustering, modules, performance'),
    ('garnet-cache', 'Microsoft Garnet - cache store, Redis protocol, RESP3, storage, checkpoint, cluster'),
    ('dragonfly-cache', 'Dragonfly DB - Redis-compatible, multi-threaded, vertical scaling, commands, replication'),
    ('keydb-cache', 'KeyDB - multithreaded Redis, active replication, flash storage, subkey expiry'),
    # More analytics
    ('apache-druid', 'Apache Druid - real-time analytics, columnar storage, OLAP, ingestion, sub-second queries'),
    ('apache-pinot', 'Apache Pinot - real-time OLAP, upserts, deduplication, multi-stage query, star-tree index'),
    ('risingwave', 'RisingWave - streaming SQL database, materialized views, PostgreSQL compatible, CDC'),
    ('materialize-db', 'Materialize - streaming SQL, incremental computation, dbt compatible, CDC, sources, sinks'),
    ('questdb', 'QuestDB - time series, high-throughput ingestion, SQL, ILP, REST API, Grafana integration'),
    # More API tools
    ('hoppscotch', 'Hoppscotch API client - open-source, REST, GraphQL, WebSocket, SSE, gRPC, collections'),
    ('bruno-api', 'Bruno API client - open-source Postman alternative, Git-friendly, collections, scripting'),
    ('stepci-testing', 'Step CI API testing - YAML workflows, assertions, chaining, load testing, OpenAPI'),
    ('schemathesis', 'Schemathesis property-based testing - OpenAPI/GraphQL, fuzzing, stateful testing, CI'),
    ('dredd-api', 'Dredd API testing - contract testing, OpenAPI/Blueprint, hooks, CI integration'),
    # More DevEx
    ('mise-tooling', 'mise dev tools - asdf-compatible, fast, lockfiles, task runner, env vars, hooks'),
    ('devbox-nix', 'Devbox - isolated dev environments, Nix, project isolation, scripts, services'),
    ('nix-flakes', 'Nix flakes - reproducible builds, dev shells, packages, NixOS modules, remote builders'),
    ('direnv-setup', 'direnv - per-directory env vars, nix integration, .envrc, layout functions, hooks'),
    ('lefthook-hooks', 'Lefthook Git hooks - fast parallel hooks, multi-language, scripts, interactive, CI skip'),
    # More testing frameworks
    ('gauge-testing', 'Gauge test automation - specification-based, markdown, plugins, data tables, reports'),
    ('robot-framework', 'Robot Framework - keyword-driven, Selenium, REST API, acceptance testing, reports'),
    ('cucumber-advanced', 'Cucumber BDD advanced - custom parameter types, data tables, hooks, world, parallel'),
    ('behave-python', 'Behave Python BDD - feature files, steps, fixtures, context, allure reports'),
    ('testcontainers', 'Testcontainers - real dependencies in tests, Docker, Ryuk cleanup, compose, reuse'),
    # More emerging tech
    ('webgpu-compute', 'WebGPU compute shaders - GPU computation in browser, WGSL, workgroups, buffers'),
    ('tauri-v2', 'Tauri v2 - Rust desktop apps, plugins, iOS/Android, commands, events, IPC, updater'),
    ('neutralinojs', 'NeutralinoJS - lightweight desktop apps, native OS APIs, Chrome runtime, extensions'),
    ('wasm-bindgen', 'wasm-bindgen Rust - Rust to WASM, JS interop, web APIs, async, worker threads'),
    ('wasmtime-runtime', 'Wasmtime runtime - WASM/WASI, embedding, component model, fuel, security sandboxing'),
    # More AI safety/alignment
    ('interpretability-tools', 'ML interpretability tools - SHAP, LIME, Captum, attention visualization, probing'),
    ('robustness-testing', 'ML robustness testing - adversarial attacks, distribution shift, calibration, evals'),
    ('ai-red-teaming', 'AI red teaming - jailbreaks, prompt injection, data extraction, misuse, evaluation'),
    ('llm-watermarking', 'LLM watermarking - text watermarking, detection, robustness, semantic watermarks'),
    ('synthetic-data-gen', 'Synthetic data generation - privacy-preserving, augmentation, evaluation, GAN, diffusion'),
    # More niche domains
    ('legal-tech-contracts', 'Legal tech contracts - clause libraries, negotiation automation, e-signature, workflow'),
    ('regulatory-reporting', 'Regulatory reporting - XBRL, Basel III, Dodd-Frank, MiFID II, automated filing'),
    ('carbon-accounting', 'Carbon accounting - scope 1/2/3 emissions, carbon credits, offset markets, reporting'),
    ('supply-chain-visibility', 'Supply chain visibility - real-time tracking, predictive analytics, digital twin, risk'),
    ('digital-twin-platform', 'Digital twin platform - IoT integration, simulation, 3D visualization, asset management'),
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
