
import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # More comprehensive coverage of major domains
    # Sports/Fitness tech
    ('sports-betting-api', 'Sports betting API - odds, lines, game data, sportsbook integration, wagering systems'),
    ('fitness-app', 'Fitness app development - workout tracking, wearables, health data, nutrition logging'),
    ('sports-analytics', 'Sports analytics - player stats, team performance, predictive modeling, visualization'),
    ('esports-platform', 'Esports platform - tournament management, ladders, matchmaking, prize pools, streaming'),
    # Food/Restaurant tech
    ('restaurant-pos', 'Restaurant POS integration - Square, Toast, Clover, menu management, order routing'),
    ('food-delivery', 'Food delivery platform - Uber Eats, DoorDash, delivery tracking, restaurant ops'),
    ('recipe-app', 'Recipe app development - ingredient parsing, nutrition data, meal planning, scaling'),
    # Travel tech
    ('travel-booking', 'Travel booking - flights, hotels, Amadeus, Sabre, GDS integration, availability'),
    ('mapping-sdk', 'Mapping SDK - Google Maps, Mapbox, HERE, routes, geocoding, places, real-time traffic'),
    ('ride-sharing', 'Ride-sharing integration - Uber, Lyft APIs, ride request, pricing, driver matching'),
    # Education tech
    ('lms-development', 'LMS development - course builder, progress tracking, quizzes, certificates, gamification'),
    ('adaptive-learning', 'Adaptive learning - personalized paths, skill assessment, spaced repetition, AI tutoring'),
    ('online-assessment', 'Online assessment - proctoring, question banks, grading, plagiarism detection'),
    # Healthcare tech
    ('telemedicine', 'Telemedicine platform - video consultations, scheduling, prescriptions, EHR integration'),
    ('medical-imaging', 'Medical imaging AI - DICOM, radiograph analysis, segmentation, diagnostic assistance'),
    ('mental-health-app', 'Mental health app - mood tracking, CBT tools, journaling, crisis support, therapist connection'),
    # Real-time systems
    ('real-time-collab', 'Real-time collaboration - OT, CRDTs, operational transform, conflict resolution, sync'),
    ('live-streaming', 'Live streaming - HLS, WebRTC, RTMP, CDN integration, chat, donations, analytics'),
    ('gaming-backend', 'Game backend - matchmaking, leaderboards, achievements, game state sync, anti-cheat'),
    # Productivity tools
    ('task-management', 'Task management - project organization, dependencies, time tracking, team collaboration'),
    ('knowledge-base', 'Knowledge base - Confluence, Notion, GitBook, search, versioning, team wiki'),
    ('meeting-assistant', 'Meeting assistant - transcription, action items, summaries, follow-up automation'),
    # Developer tools
    ('code-search', 'Code search - Sourcegraph, Grep.app, semantic search, code navigation, indexing'),
    ('dependency-analysis', 'Dependency analysis - license compliance, vulnerability scanning, update automation'),
    ('code-quality', 'Code quality - SonarQube, CodeClimate, complexity metrics, technical debt tracking'),
    # Cloud native
    ('service-mesh-istio', 'Istio service mesh - traffic management, mTLS, observability, Envoy configuration'),
    ('opa-policies', 'OPA policies - Rego language, authorization policies, Kubernetes admission, API authz'),
    ('keda-autoscaling', 'KEDA autoscaling - event-driven scaling, ScaledObjects, triggers, Kubernetes HPA'),
    # Data platforms
    ('delta-lake', 'Delta Lake - ACID transactions, time travel, schema evolution, optimizations, merge'),
    ('apache-iceberg', 'Apache Iceberg - table format, partitioning, schema evolution, time travel, catalog'),
    ('duckdb', 'DuckDB - in-process analytics, OLAP SQL, Python integration, columnar storage, performance'),
    # LLM specific
    ('llm-fine-tuning', 'LLM fine-tuning - instruction tuning, RLHF, DPO, dataset prep, evaluation, deployment'),
    ('llm-evaluation', 'LLM evaluation - benchmarks, HELM, BIG-bench, custom evals, hallucination detection'),
    ('llm-agents', 'LLM agents - function calling, tool use, planning, memory, multi-agent, production patterns'),
    ('llm-security', 'LLM security - prompt injection, jailbreaks, output validation, guardrails, red-teaming'),
    ('llm-observability', 'LLM observability - traces, token usage, latency, costs, quality metrics, Langfuse'),
    # Specific APIs/services
    ('stripe-connect', 'Stripe Connect - marketplace payments, platform fees, split payments, onboarding, payouts'),
    ('stripe-subscriptions', 'Stripe subscriptions - plans, trials, metered billing, upgrades, dunning, webhooks'),
    ('stripe-billing-portal', 'Stripe billing portal - customer self-service, plan changes, invoice history, payment methods'),
    ('aws-lambda-advanced', 'AWS Lambda advanced - layers, container images, SnapStart, extensions, power tuning'),
    ('aws-step-functions', 'AWS Step Functions - state machines, parallel, map, wait, error handling, express'),
    ('aws-eventbridge', 'AWS EventBridge - event buses, rules, targets, schema registry, pipes, cross-account'),
    # Auth/Identity
    ('auth0-integration', 'Auth0 integration - SPA, M2M, social login, MFA, Actions, Organizations, tokens'),
    ('okta-integration', 'Okta integration - SSO, MFA, SCIM provisioning, Workflows, OAuth2, OIDC'),
    ('keycloak', 'Keycloak - open source IAM, realms, clients, flows, LDAP sync, extensions, themes'),
    ('jwt-patterns', 'JWT patterns - signing, validation, refresh tokens, revocation, claims design, security'),
    # Monitoring/Alerting
    ('pagerduty-incident', 'PagerDuty incident management - escalation policies, schedules, integrations, runbooks'),
    ('opsgenie-alerting', 'OpsGenie alerting - alert routing, on-call, integrations, automation, reports'),
    ('statuspage-io', 'Statuspage management - incident communication, component status, subscriber notifications'),
    # Search
    ('typesense', 'Typesense search - schema design, typo tolerance, faceting, geo search, synonyms'),
    ('meilisearch', 'Meilisearch - instant search, typo tolerance, filters, ranking rules, multi-search'),
    ('opensearch', 'OpenSearch - index management, query DSL, aggregations, security, ML integration'),
    # API management
    ('kong-api-gateway', 'Kong API Gateway - plugins, routes, services, rate limiting, auth, analytics'),
    ('nginx-advanced', 'NGINX advanced - reverse proxy, load balancing, caching, SSL, Lua scripting, config'),
    ('traefik-proxy', 'Traefik proxy - automatic service discovery, Let\'s Encrypt, middleware, Docker, K8s'),
    # More AI/ML
    ('stable-diffusion-advanced', 'Stable Diffusion advanced - ControlNet, LoRA, IP-Adapter, SDXL, ComfyUI workflows'),
    ('whisper-advanced', 'Whisper advanced - streaming, word timestamps, speaker diarization, fine-tuning'),
    ('llama-advanced', 'Llama advanced - llama.cpp, Ollama, quantization, fine-tuning, deployment patterns'),
    # Business tools
    ('hubspot-crm-advanced', 'HubSpot CRM advanced - custom objects, workflows, sequences, reporting, API, deals'),
    ('salesforce-apex', 'Salesforce Apex - triggers, batch classes, queueable, future methods, test classes'),
    ('zendesk-advanced', 'Zendesk advanced - triggers, automations, macros, custom apps, reporting, Sunshine'),
    # More cloud
    ('cloudflare-r2', 'Cloudflare R2 - S3-compatible storage, Workers integration, Bucket API, public access'),
    ('cloudflare-ai', 'Cloudflare AI - Workers AI, AI Gateway, model catalog, binding, streaming inference'),
    ('cloudflare-d1', 'Cloudflare D1 - edge SQLite database, Workers binding, migrations, backups, global reads'),
    # Specialized domains
    ('automotive-telematics', 'Automotive telematics - OBD-II, CAN bus, fleet tracking, EV data, diagnostics'),
    ('smart-home-iot', 'Smart home IoT - Home Assistant, Matter, Zigbee, Z-Wave, home automation, scenes'),
    ('drone-programming', 'Drone programming - MAVLink, ArduPilot, PX4, mission planning, telemetry, geofencing'),
    # More patterns
    ('event-storming', 'Event Storming - domain modeling, bounded contexts, aggregates, policies, commands'),
    ('domain-storytelling', 'Domain Storytelling - domain knowledge, workflow mapping, ubiquitous language'),
    ('wardley-mapping', 'Wardley Mapping - strategic planning, value chains, evolution, situational awareness'),
    # Testing specialized
    ('accessibility-testing', 'Accessibility testing - axe-core, NVDA, JAWS, keyboard nav, WCAG 2.1 AA compliance'),
    ('performance-testing', 'Performance testing - load, stress, spike, soak testing, SLO validation, profiling'),
    ('security-testing-web', 'Web security testing - OWASP Top 10, API security, auth testing, injection testing'),
    # Build systems
    ('gradle-advanced', 'Gradle advanced - custom plugins, build cache, configuration cache, composite builds'),
    ('maven-advanced', 'Maven advanced - custom plugins, lifecycle, profiles, multi-module, BOM management'),
    ('cmake-advanced', 'CMake advanced - targets, generators, toolchains, CPM, FetchContent, presets'),
    # Low-code/No-code
    ('bubble-development', 'Bubble no-code - database design, workflows, plugins, responsive layout, API connector'),
    ('webflow-advanced', 'Webflow advanced - CMS, e-commerce, custom code, interactions, hosting, SEO'),
    ('retool-apps', 'Retool apps - data sources, components, queries, custom components, workflows, permissions'),
    # Finance specialized
    ('crypto-defi-dev', 'Crypto DeFi development - Uniswap, Aave, Compound, yield strategies, smart contracts'),
    ('cbdc-digital-currency', 'CBDC and digital currency - central bank digital currency, payment rails, compliance'),
    ('insurtech', 'InsurTech - policy management, claims processing, underwriting AI, actuarial models'),
    # More enterprise
    ('sap-btp', 'SAP BTP - cloud platform, Integration Suite, Extension Suite, AI services, CAP framework'),
    ('microsoft-365-dev', 'Microsoft 365 development - Graph API, Teams apps, SPFx, Office Add-ins, Power Platform'),
    ('google-workspace-dev', 'Google Workspace development - Apps Script, Cloud Identity, Marketplace, VIBE'),
    # Emerging tech
    ('web-assembly', 'WebAssembly - WASM modules, Rust/C to WASM, WASI, browser and server-side, WABT'),
    ('htmx-fullstack', 'HTMX fullstack - server-side rendering, hyperscript, Alpine.js, progressive enhancement'),
    ('bun-fullstack', 'Bun fullstack - runtime, bundler, test runner, HTTP server, SQLite, package manager'),
    # Data quality
    ('great-expectations', 'Great Expectations - data validation, expectations, suites, checkpoints, Data Docs'),
    ('deequ-data-quality', 'Amazon Deequ - data quality metrics, constraints, anomaly detection, column profiles'),
    ('monte-carlo-dq', 'Monte Carlo data observability - data quality, lineage, monitoring, incident management'),
    # Privacy/Ethics
    ('differential-privacy', 'Differential privacy - noise addition, epsilon budgets, federated learning, PySyft'),
    ('federated-learning', 'Federated learning - FL frameworks, privacy-preserving ML, model aggregation'),
    ('model-cards', 'Model cards - documentation standards, bias assessment, limitations, usage guidelines'),
    # More languages
    ('scala-spark', 'Scala + Spark - functional patterns, Dataset API, streaming, MLlib, deployment'),
    ('kotlin-multiplatform', 'Kotlin Multiplatform - shared business logic, iOS/Android/web, expect/actual'),
    ('dart-flutter', 'Dart + Flutter - language features, null safety, async, streams, isolates, tooling'),
    ('ocaml-functional', 'OCaml functional programming - types, modules, functors, GADTs, performance'),
    ('clojure-development', 'Clojure development - REPL, macros, data structures, concurrency, Datomic, Pedestal'),
    # More tools
    ('obsidian-plugins', 'Obsidian plugin development - API, views, settings, commands, data access, Templater'),
    ('vscode-extension-dev', 'VS Code extension development - activation, commands, tree views, language server, WebView'),
    ('raycast-extension-dev', 'Raycast extension development - List, Detail, Form, Actions, LaunchContext, preferences'),
    ('alfred-workflow', 'Alfred workflow development - Python, AppleScript, JXA, web objects, file actions'),
    # Specific platforms
    ('twitch-integration', 'Twitch integration - IRC chat, EventSub, Helix API, channel points, subscriptions'),
    ('discord-advanced', 'Discord advanced - sharding, slash commands, modal forms, select menus, threads, forums'),
    ('matrix-protocol', 'Matrix protocol - rooms, events, E2E encryption, bridges, bots, Synapse homeserver'),
    ('fediverse-mastodon', 'Fediverse/Mastodon - ActivityPub, Mastodon API, federated social, account migration'),
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
