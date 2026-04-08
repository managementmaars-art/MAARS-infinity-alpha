
import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # More comprehensive expansions - aiming for massive coverage
    # Additional AI/LLM tools
    ('langfuse-advanced', 'Langfuse advanced - custom events, scores, datasets, evaluations, prompt management'),
    ('helicone', 'Helicone LLM observability - request logging, caching, rate limiting, cost tracking'),
    ('portkey-ai', 'Portkey AI gateway - LLM routing, fallbacks, virtual keys, caching, observability'),
    ('litellm', 'LiteLLM - unified LLM API, provider switching, streaming, error handling, proxy server'),
    ('guidance-ai', 'Guidance AI - structured generation, constrained decoding, handlebars syntax, generation control'),
    ('outlines-structured', 'Outlines structured generation - JSON, regex, grammar-constrained generation'),
    ('lmql', 'LMQL language - prompt programming, constraints, multi-model, streaming, output control'),
    ('instructor-python', 'Instructor Python - structured outputs, Pydantic validation, OpenAI/Anthropic, retry'),
    ('marvin-ai', 'Marvin AI toolkit - AI functions, classifiers, extractors, transformers, structured data'),
    # More vector/search tools
    ('vespa-search', 'Vespa search engine - approximate nearest neighbor, hybrid ranking, real-time indexing'),
    ('redis-vector', 'Redis Vector - vector similarity search, VSS, Redis Stack, hybrid search, metadata'),
    ('pgembedding', 'pgembedding PostgreSQL extension - vector embeddings, cosine similarity, full-text hybrid'),
    ('lance-db', 'LanceDB - columnar vector store, embedded, serverless, versioning, multimodal search'),
    ('marqo-search', 'Marqo search - multimodal search, text and image, custom models, filtering, tensor store'),
    # More DevOps tools
    ('grafana-alloy', 'Grafana Alloy - OpenTelemetry collector, metrics, logs, traces, pipelines, targets'),
    ('vector-observability', 'Vector observability pipeline - log collection, transformation, routing, sinks'),
    ('fluentbit', 'Fluent Bit - lightweight log processor, multi-input, filter, output, Kubernetes logging'),
    ('promtail-loki', 'Promtail and Loki - log collection, label extraction, LogQL queries, alerting'),
    ('tempo-tracing', 'Grafana Tempo - distributed tracing backend, trace search, exemplars, metrics from traces'),
    # More CI/CD
    ('woodpecker-ci', 'Woodpecker CI - self-hosted CI/CD, YAML pipelines, Docker, Gitea, matrix builds'),
    ('forgejo-actions', 'Forgejo Actions - self-hosted GitHub Actions compatible, runners, workflows'),
    ('gitlab-pipelines', 'GitLab CI pipelines - stages, jobs, artifacts, environments, rules, variables, runners'),
    ('github-actions-advanced', 'GitHub Actions advanced - composite actions, reusable workflows, matrix, OIDC, caching'),
    ('buildkite', 'Buildkite CI/CD - elastic CI, dynamic pipelines, plugins, agents, artifacts, parallel'),
    # Security specialized
    ('owasp-top10', 'OWASP Top 10 - injection, broken auth, XSS, IDOR, SSRF, XXE, security misconfiguration'),
    ('penetration-testing', 'Penetration testing methodology - recon, enumeration, exploitation, post-exploitation, reporting'),
    ('red-team-ops', 'Red team operations - C2 frameworks, persistence, lateral movement, exfiltration, evasion'),
    ('soc-analyst', 'SOC analyst - SIEM, alert triage, incident response, threat hunting, IOC analysis'),
    ('threat-intelligence', 'Threat intelligence - MITRE ATT&CK, CTI platforms, IoC feeds, threat reports, STIX/TAXII'),
    # Cloud-native patterns
    ('sidecar-pattern', 'Sidecar container pattern - service mesh, logging, monitoring, security proxy, ambassador'),
    ('init-container-k8s', 'Kubernetes init containers - setup tasks, dependency waiting, secrets injection, DB migration'),
    ('dapr-runtime', 'Dapr runtime - service invocation, pub/sub, state, bindings, actors, distributed lock'),
    ('knative-serverless', 'Knative serverless - Serving, Eventing, scaling to zero, traffic splitting, revisions'),
    ('cluster-api', 'Cluster API - declarative cluster lifecycle, providers, CAPI controllers, cluster templates'),
    # More data tools
    ('apache-flink', 'Apache Flink - stateful stream processing, windows, watermarks, checkpointing, SQL'),
    ('apache-beam', 'Apache Beam - unified batch/streaming, PCollections, transforms, runners, IO connectors'),
    ('trino-analytics', 'Trino (Presto) - federated query engine, multiple data sources, query optimization'),
    ('superset-bi', 'Apache Superset - BI tool, dashboards, charts, SQL editor, datasets, role-based access'),
    ('metabase-analytics', 'Metabase analytics - questions, dashboards, automated insights, embedding, subscriptions'),
    # More mobile
    ('capacitor-js', 'Capacitor.js - hybrid mobile apps, native plugins, web technology, iOS/Android/PWA'),
    ('ionic-framework', 'Ionic Framework - cross-platform mobile, components, themes, Capacitor, Cordova'),
    ('react-native-expo', 'React Native + Expo - managed workflow, EAS, native modules, OTA updates, testing'),
    ('xamarin-maui', 'Xamarin/.NET MAUI - cross-platform .NET mobile, C#, XAML, native APIs, hot reload'),
    # More game development
    ('phaser-3', 'Phaser 3 - HTML5 game framework, scenes, physics, input, animations, tweens, cameras'),
    ('pixi-js', 'PixiJS - 2D rendering engine, WebGL, sprites, containers, filters, particles, text'),
    ('babylon-js', 'Babylon.js - 3D game engine, physics, materials, animations, VR/AR, gizmos, inspector'),
    ('love2d', 'LOVE2D - Lua game framework, 2D games, physics, audio, networking, cross-platform'),
    ('pygame', 'Pygame - Python game development, sprites, sound, input, collision, surfaces, events'),
    # More blockchain
    ('near-protocol', 'NEAR Protocol - smart contracts, Rust/JavaScript, wallet, NEAR CLI, fungible tokens'),
    ('polygon-zkevm', 'Polygon zkEVM - zero-knowledge proofs, EVM compatible, Layer 2, bridge, CDK'),
    ('arbitrum', 'Arbitrum - Layer 2 Ethereum, Nitro, Orbit chains, bridges, Stylus, smart contracts'),
    ('cosmos-sdk', 'Cosmos SDK - modular blockchain, IBC, modules, keepers, messages, queries, governance'),
    # Enterprise patterns
    ('saga-choreography', 'Saga choreography - distributed transactions, event-driven, compensating transactions'),
    ('outbox-pattern', 'Outbox pattern - reliable messaging, transactional outbox, CDC, at-least-once delivery'),
    ('bulkhead-pattern', 'Bulkhead pattern - fault isolation, thread pools, semaphores, circuit breaker, resilience'),
    ('strangler-fig', 'Strangler Fig pattern - legacy migration, incremental replacement, routing, API facade'),
    ('anti-corruption-layer', 'Anti-corruption layer - domain isolation, translation, adapter, legacy integration'),
    # More productivity
    ('notion-ai', 'Notion AI - writing assistance, summarization, translation, Q&A, database queries'),
    ('obsidian-dataview', 'Obsidian Dataview - SQL-like queries, JavaScript, metadata, tables, task queries'),
    ('logseq-development', 'Logseq development - plugins, queries, templates, graph database, block references'),
    ('roam-research', 'Roam Research - networked thought, block references, queries, filters, daily notes'),
    # More content tools
    ('midjourney-prompts', 'Midjourney prompts - artistic prompts, parameters, aspect ratios, styles, variations'),
    ('dall-e-prompts', 'DALL-E prompts - image generation, editing, variations, inpainting, style transfer'),
    ('runway-ml', 'Runway ML - video generation, Gen-2, image tools, video-to-video, magic eraser'),
    ('kling-ai', 'Kling AI - video generation, image-to-video, text-to-video, motion control, lip sync'),
    # More business tools
    ('notion-databases', 'Notion databases - properties, relations, rollups, filters, views, formulas, templates'),
    ('airtable-bases', 'Airtable bases - tables, fields, views, automations, forms, sharing, API integration'),
    ('coda-docs', 'Coda docs - pages, tables, formulas, buttons, automations, packs, cross-doc references'),
    ('clickup-workspace', 'ClickUp workspace - tasks, docs, goals, whiteboards, views, automations, integrations'),
    # More APIs
    ('openweather-api', 'OpenWeather API - current weather, forecasts, maps, air quality, alerts, historical'),
    ('google-maps-api', 'Google Maps API - places, directions, geocoding, static maps, Street View, routes'),
    ('stripe-climate', 'Stripe Climate - carbon removal, contributions, sustainability, green business'),
    ('telnyx-api', 'Telnyx API - VoIP, SMS, video, fax, networking, IP messaging, call control'),
    # Infrastructure as Code
    ('bicep-azure', 'Azure Bicep - declarative IaC, resource types, modules, conditions, loops, deployment'),
    ('cdk-tf', 'CDK for Terraform - TypeScript/Python IaC, providers, constructs, stacks, testing'),
    ('opentofu', 'OpenTofu - open source Terraform fork, providers, state, modules, workspaces, CLI'),
    ('spacelift', 'Spacelift - Terraform/OpenTofu/Pulumi SaaS, policy as code, drift detection, OPA'),
    # More testing
    ('cypress-advanced', 'Cypress advanced - custom commands, plugins, component testing, network interception'),
    ('vitest', 'Vitest - Vite-native testing, TypeScript, ESM, coverage, mocking, snapshot, browser mode'),
    ('bun-test', 'Bun test runner - built-in testing, expect API, mocking, coverage, lifecycle hooks'),
    ('pact-contract', 'Pact contract testing - consumer-driven, provider verification, Pact broker, CI integration'),
    # More frameworks
    ('fasthtml', 'FastHTML - Python web framework, HTMX-first, Pydantic, minimal dependencies, server-side'),
    ('litestar', 'Litestar - Python ASGI, OpenAPI, DTOs, guards, dependencies, lifecycle hooks, typing'),
    ('quart-async', 'Quart - async Flask, ASGI, WebSockets, Server-Sent Events, async context variables'),
    ('starlette', 'Starlette - ASGI toolkit, routing, middleware, WebSockets, background tasks, testing'),
    # More languages
    ('gleam-lang', 'Gleam language - type-safe functional language, Erlang/JS targets, immutability, OTP'),
    ('roc-lang', 'Roc language - fast, friendly, static types, pure, builtins, platforms, effects'),
    ('zig-lang', 'Zig language - low-level systems, comptime, error handling, memory management, C interop'),
    ('nim-lang', 'Nim language - Python-like syntax, C speed, macros, metaprogramming, garbage collection'),
    ('crystal-lang', 'Crystal language - Ruby-like syntax, compiled, type inference, concurrency, C bindings'),
    # More SaaS tools
    ('hubspot-cms', 'HubSpot CMS - HubL templating, modules, drag-and-drop, CDN, personalization'),
    ('wordpress-gutenberg', 'WordPress Gutenberg - block editor, custom blocks, block patterns, full-site editing'),
    ('ghost-cms', 'Ghost CMS - headless CMS, Handlebars, Ghost API, themes, members, subscriptions'),
    ('contentful-cms', 'Contentful CMS - content model, GraphQL API, webhooks, environments, rich text'),
    ('sanity-advanced', 'Sanity advanced - GROQ, schema design, plugins, portable text, real-time, Studio'),
    ('directus-cms', 'Directus CMS - headless CMS, data studio, extensions, flows, permissions, REST/GraphQL'),
    # More analytics
    ('segment-advanced', 'Segment advanced - Protocols, Personas, Journeys, Connections, Functions, Transformations'),
    ('mixpanel-advanced', 'Mixpanel advanced - cohorts, experiments, impact, signal, predictions, flows'),
    ('amplitude-advanced', 'Amplitude advanced - experiment, recommend, session replay, analytics, personas'),
    ('heap-analytics', 'Heap analytics - auto-capture, retroactive analysis, journeys, dashboards, integrations'),
    ('fullstory', 'FullStory - session recording, digital experience, signals, frustration signals, integrations'),
    # IoT/Embedded
    ('raspberry-pi', 'Raspberry Pi - GPIO, Python, electronics, sensors, servo, camera, network, projects'),
    ('arduino', 'Arduino - microcontroller, C++, sensors, actuators, communication protocols, shields'),
    ('micropython', 'MicroPython - Python for microcontrollers, ESP32, RP2040, peripherals, networking'),
    ('embedded-rust', 'Embedded Rust - no_std, HAL, RTIC, async embedded, memory safety, cross-compilation'),
    ('ros2', 'ROS2 - Robot Operating System, nodes, topics, services, actions, navigation, simulation'),
    # More AI research
    ('mamba-state-space', 'Mamba state space models - selective state spaces, S4, linear attention alternative'),
    ('mixture-of-experts', 'Mixture of Experts - sparse MoE, routing, expert capacity, load balancing, training'),
    ('speculative-decoding-advanced', 'Speculative decoding advanced - draft models, tree attention, medusa, lookahead'),
    ('flash-attention-advanced', 'Flash Attention advanced - FA2, FA3, ring attention, sliding window, variable length'),
    ('rope-embeddings', 'RoPE positional embeddings - rotary position encoding, extended context, YaRN, LongRoPE'),
    # Privacy tech
    ('tor-network', 'Tor network - onion routing, hidden services, anonymity, exit nodes, Tor Browser'),
    ('signal-protocol', 'Signal Protocol - end-to-end encryption, X3DH, Double Ratchet, sealed sender, groups'),
    ('zero-knowledge-proofs', 'Zero-knowledge proofs - zk-SNARKs, zk-STARKs, Groth16, PLONK, privacy applications'),
    ('homomorphic-encryption', 'Homomorphic encryption - FHE, computation on encrypted data, SEAL, OpenFHE, TFHE'),
    # More specific tools
    ('postman-advanced', 'Postman advanced - collections, environments, pre-request scripts, tests, mock servers'),
    ('insomnia-api', 'Insomnia API client - requests, environments, plugins, Git sync, testing, design'),
    ('httpie', 'HTTPie - CLI HTTP client, JSON, sessions, file upload, OAuth, WebSocket, downloads'),
    ('curl-advanced', 'cURL advanced - parallel, cookies, OAuth, proxy, TLS, timing, verbose debugging'),
    # Specific databases
    ('fauna-db', 'Fauna DB - document-relational, FQL, GraphQL, temporal, consistent, globally distributed'),
    ('pocketbase', 'PocketBase - open-source backend, SQLite, real-time, auth, file storage, REST/JS SDK'),
    ('turso-db', 'Turso DB - libSQL, SQLite at the edge, replicas, embedded replicas, branching'),
    ('xata-database', 'Xata database - Postgres-compatible, full-text search, schema migrations, branches, REST'),
    ('neon-serverless', 'Neon serverless Postgres - autoscaling, branching, serverless driver, point-in-time recovery'),
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
