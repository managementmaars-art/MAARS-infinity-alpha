
import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # AI video/audio generation
    ('sora-video', 'Sora video generation - text-to-video, video editing, storyboarding, consistency, prompts'),
    ('stable-video', 'Stable Video Diffusion - video generation, SVD, img2vid, motion, XT, fine-tuning'),
    ('animatediff', 'AnimateDiff - video animation, motion modules, ControlNet video, temporal consistency'),
    ('audioldm', 'AudioLDM - text-to-audio, sound generation, music generation, audio editing, diffusion'),
    ('musicgen', 'MusicGen - text-to-music, melody conditioning, stereo, streaming, fine-tuning patterns'),
    ('bark-tts', 'Bark TTS - text-to-speech, multilingual, music, noise, voice cloning, generation'),
    ('voicebox-meta', 'Voicebox Meta - voice synthesis, audio editing, cross-lingual TTS, zero-shot'),
    # More ML research
    ('attention-mechanisms', 'Attention mechanisms - self-attention, cross-attention, multi-head, grouped query, sliding window'),
    ('positional-encoding', 'Positional encoding - absolute, relative, RoPE, ALiBi, learned, extrapolation'),
    ('normalization-layers', 'Normalization layers - LayerNorm, RMSNorm, GroupNorm, BatchNorm, pre/post norm'),
    ('activation-functions', 'Activation functions - GELU, SiLU, SwiGLU, ReLU variants, activation engineering'),
    ('optimizer-algorithms', 'Optimizer algorithms - AdamW, Lion, Sophia, Muon, Shampoo, schedule-free, warmup'),
    ('gradient-techniques', 'Gradient techniques - gradient clipping, accumulation, checkpointing, mixed precision, DDP'),
    # More code generation
    ('code-generation-eval', 'Code generation evaluation - HumanEval, MBPP, SWE-bench, LiveCodeBench, metrics'),
    ('code-llm-finetune', 'Code LLM fine-tuning - instruction tuning, code datasets, evaluation, OSS Code models'),
    ('copilot-alternatives', 'Copilot alternatives - Tabnine, Codeium, SuperMaven, Qodo, Continue, Sourcegraph Cody'),
    ('devin-alternatives', 'Devin alternatives - SWE-agent, OpenDevin, Cognition, autonomous coding agents'),
    ('code-review-ai', 'AI code review - CodeRabbit, PR-Agent, Graphite, automated review, feedback patterns'),
    # More platforms/infra
    ('modal-advanced', 'Modal advanced - GPU functions, distributed map, parallel, webhooks, volumes, cls'),
    ('vastai-gpu', 'Vast.ai GPU cloud - spot instances, reserved, templates, onstart, CLI, interruptible'),
    ('coreweave-cloud', 'CoreWeave GPU cloud - Kubernetes, Slurm, networking, InfiniBand, storage, on-demand'),
    ('lambda-cloud-gpu', 'Lambda Cloud GPU - on-demand, spot, clusters, file systems, Jupyter, team access'),
    ('lepton-ai', 'Lepton AI - LLM inference API, fine-tuning, photons, workspace, storage, secrets'),
    # More specialized databases
    ('foundationdb', 'FoundationDB - ACID transactions, multi-model, record layer, document, time series'),
    ('riak-kv', 'Riak KV - eventually consistent, CRDT, MapReduce, secondary indexes, multi-datacenter'),
    ('aerospike-db', 'Aerospike - hybrid memory, real-time, namespaces, bins, indexes, UDFs, aggregation'),
    ('scylladb', 'ScyllaDB - Cassandra compatible, C++, shard-per-core, latency, consistency, cloud'),
    ('memcached-advanced', 'Memcached advanced - distributed caching, binary protocol, SASL, connection pooling'),
    # More API patterns
    ('api-versioning', 'API versioning strategies - URL, header, query param, sunset, migration, documentation'),
    ('api-pagination', 'API pagination - cursor, offset, keyset, page tokens, hypermedia links, performance'),
    ('api-rate-limiting', 'API rate limiting - token bucket, sliding window, fixed window, distributed, headers'),
    ('api-idempotency', 'API idempotency - idempotency keys, duplicate detection, retry-safe operations'),
    ('api-webhooks', 'Webhook patterns - delivery, retries, signatures, replay, ordering, fan-out, testing'),
    # More architecture
    ('event-mesh', 'Event mesh - distributed event brokers, event routing, discovery, multi-cloud events'),
    ('data-mesh', 'Data mesh - domain ownership, self-serve, federated governance, data products, tooling'),
    ('service-weaver', 'Google Service Weaver - modular monolith to microservices, RPC, components, weavelet'),
    ('micro-frontends', 'Micro-frontends - module federation, web components, iframe, shell app, routing'),
    ('backend-for-frontend', 'Backend for Frontend (BFF) - client-specific APIs, aggregation, transformation'),
    # More testing strategies
    ('test-pyramid', 'Test pyramid strategy - unit, integration, E2E balance, fast feedback, coverage strategy'),
    ('tdd-advanced', 'TDD advanced - outside-in, classicist vs mockist, test doubles, design pressure'),
    ('bdd-advanced', 'BDD advanced - living documentation, Gherkin, three amigos, scenario design'),
    ('property-based-testing', 'Property-based testing - Hypothesis, QuickCheck, generators, shrinking, model-based'),
    ('fuzzing-advanced', 'Fuzzing advanced - coverage-guided, libFuzzer, AFL++, structured fuzzing, ClusterFuzz'),
    # More automation
    ('n8n-advanced', 'n8n advanced - custom nodes, credential types, community nodes, self-hosted, triggers'),
    ('make-advanced', 'Make (Integromat) advanced - aggregators, iterators, routers, error handling, modules'),
    ('temporal-advanced', 'Temporal advanced - versioning, continue-as-new, batch operations, search attributes'),
    ('conductor-oss', 'Netflix Conductor - workflow orchestration, task workers, polling, metrics, operators'),
    ('zeebe-workflow', 'Zeebe/Camunda 8 - BPMN, workflows, gRPC, job workers, exporters, Tasklist'),
    # More analytics
    ('funnelflux-analytics', 'Funnel analytics - conversion tracking, attribution, cohorts, LTV, A/B analysis'),
    ('google-analytics-4', 'Google Analytics 4 - events, parameters, conversions, audiences, BigQuery export'),
    ('plausible-analytics', 'Plausible analytics - privacy-first, custom events, revenue, goals, self-hosted'),
    ('umami-analytics', 'Umami analytics - open-source, self-hosted, events, funnels, sessions, API'),
    ('posthog-advanced', 'PostHog advanced - session replay, feature flags, experiments, SQL insights, CDPs'),
    # More visualization
    ('d3-advanced', 'D3.js advanced - force simulation, geo projections, transitions, custom layouts, streaming'),
    ('echarts-vis', 'Apache ECharts - charts, maps, 3D, themes, responsive, large data rendering, GL'),
    ('vega-lite', 'Vega-Lite - grammar of graphics, JSON spec, interactive, reactive, Altair binding'),
    ('observable-plot', 'Observable Plot - concise visualization grammar, marks, scales, transforms, faceting'),
    ('recharts', 'Recharts React charts - composable, responsive, animation, custom shapes, synchronization'),
    # More mobile/cross-platform
    ('maui-advanced', '.NET MAUI advanced - handlers, platform views, native embedding, hot reload, testing'),
    ('kotlin-compose', 'Kotlin Jetpack Compose - side effects, custom layouts, performance, animation, state'),
    ('swift-packages', 'Swift Package Manager advanced - targets, conditional deps, XCFramework, plugins'),
    ('flutter-performance', 'Flutter performance - rendering pipeline, jank, repaint, DevTools, profiling, impeller'),
    ('react-native-new-arch', 'React Native new architecture - JSI, Fabric, TurboModules, Bridgeless, codegen'),
    # More DevOps/platform
    ('backstage-advanced', 'Backstage advanced - plugins, custom catalog entities, software templates, TechDocs'),
    ('port-io', 'Port.io IDP - blueprints, relations, scorecard, self-service actions, k8s exporter'),
    ('cortex-io', 'Cortex service catalog - scorecards, service groups, Kubernetes, Git sync, catalog API'),
    ('configure8', 'Configure8 - service catalog, scorecards, governance, integrations, developer portal'),
    ('humanitec', 'Humanitec platform orchestrator - score files, workload, resource definitions, environments'),
    # More niche tech
    ('webrtc-advanced', 'WebRTC advanced - SFU vs MCU, TURN/STUN, signaling, simulcast, DataChannel, e2e encrypt'),
    ('mediasoup', 'mediasoup SFU - selective forwarding, WebRTC, rooms, transports, producers, consumers'),
    ('livekit-platform', 'LiveKit platform - WebRTC SFU, rooms, participants, tracks, agents, cloud hosting'),
    ('janus-gateway', 'Janus Gateway - WebRTC server, plugins, sessions, handles, ICE, audio/video rooms'),
    ('agora-rtc', 'Agora RTC - real-time communications, SDK, channels, streams, recording, AI extensions'),
    # More AI application patterns
    ('rag-advanced', 'RAG advanced - hybrid retrieval, re-ranking, parent-child chunking, knowledge graphs'),
    ('agentic-rag', 'Agentic RAG - query planning, routing, self-reflection, corrective RAG, adaptive RAG'),
    ('multi-modal-rag', 'Multi-modal RAG - images, tables, charts, audio, video understanding in retrieval'),
    ('graph-rag', 'GraphRAG - community summaries, global search, Microsoft GraphRAG, knowledge graph RAG'),
    ('hyde-rag', 'HyDE RAG - hypothetical document embeddings, dense retrieval, Precise Zero-Shot Dense Retrieval'),
    # More blockchain
    ('starknet-cairo', 'StarkNet Cairo - L2, STARK proofs, Cairo language, smart contracts, account abstraction'),
    ('zksync-era', 'zkSync Era - EVM-compatible ZK rollup, native account abstraction, paymasters, L2 native'),
    ('linea-l2', 'Linea L2 - ConsenSys zkEVM, EVM compatibility, bridge, MetaMask integration, developer tools'),
    ('optimism-superchain', 'Optimism Superchain - OP Stack, bedrock, fault proofs, interop, chain ecosystem'),
    ('base-chain', 'Base blockchain - Coinbase L2, OP Stack, onchain apps, smart wallet, Basename'),
    # More enterprise
    ('servicenow-dev', 'ServiceNow development - flows, scripts, REST API, catalog items, custom apps, CMDB'),
    ('sap-abap', 'SAP ABAP - reports, BAPIs, enhancements, SmartForms, ALV, CDS views, RAP model'),
    ('dynamics-365', 'Dynamics 365 - Power Apps, CE, FO, customizations, plugins, workflows, PCF components'),
    ('tibco-integration', 'TIBCO integration - BusinessWorks, Spotfire, EMS, streaming, Mashery API management'),
    ('informatica-etl', 'Informatica ETL - PowerCenter, IDMC, mappings, workflows, transformations, cloud data integration'),
    # More specific tools
    ('netdata-monitoring', 'Netdata monitoring - real-time metrics, eBPF, agents, cloud, alerts, ML anomaly detection'),
    ('checkmk-monitoring', 'Checkmk monitoring - hosts, services, agents, notifications, dashboards, automation'),
    ('zabbix-monitoring', 'Zabbix monitoring - hosts, templates, triggers, macros, proxy, low-level discovery'),
    ('icinga-monitoring', 'Icinga monitoring - checks, notifications, IDO, IcingaDB, director, modules'),
    ('nagios-monitoring', 'Nagios monitoring - hosts, services, plugins, NRPE, NDO, dashboards, check patterns'),
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
