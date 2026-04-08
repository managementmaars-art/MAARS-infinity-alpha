
import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # Personal productivity
    ('pkm-system', 'Personal knowledge management - Obsidian, Notion, Roam, Logseq, Zettelkasten, linked notes'),
    ('time-management', 'Time management - GTD, time blocking, Pomodoro, priority matrix, energy management'),
    ('habit-tracking', 'Habit tracking - streak systems, habit stacking, behavior design, tracking apps'),
    ('journaling-ai', 'AI-assisted journaling - reflection prompts, sentiment analysis, pattern recognition'),
    ('reading-system', 'Reading system - book notes, highlights, spaced repetition, Readwise, Kindle integration'),
    # Content/Media
    ('podcast-production', 'Podcast production - recording, editing, show notes, RSS, distribution, growth'),
    ('video-production', 'Video production - scripting, editing workflow, thumbnails, YouTube SEO, repurposing'),
    ('newsletter-growth', 'Newsletter growth - Substack, Beehiiv, ConvertKit, subject lines, growth tactics'),
    ('content-calendar', 'Content calendar planning - editorial calendar, batch creation, repurposing strategy'),
    ('copywriting-formulas', 'Copywriting formulas - AIDA, PAS, BAB, StoryBrand, direct response, headlines'),
    # E-commerce
    ('shopify-advanced', 'Shopify advanced - Liquid templates, custom apps, checkout extensions, Shopify Functions'),
    ('woocommerce-advanced', 'WooCommerce advanced - custom plugins, hooks, payment gateways, subscriptions'),
    ('amazon-selling', 'Amazon selling - FBA, listing optimization, PPC, inventory management, Brand Registry'),
    ('ecommerce-analytics', 'E-commerce analytics - conversion funnel, cohort analysis, LTV, attribution models'),
    ('dropshipping', 'Dropshipping - supplier integration, automation, pricing strategy, customer service'),
    # Developer experience
    ('documentation-site', 'Documentation site - Docusaurus, GitBook, MkDocs, VitePress, API docs generation'),
    ('developer-portal', 'Developer portal - API catalog, SDK docs, interactive playground, changelog, guides'),
    ('openapi-design', 'OpenAPI design - API-first design, spec validation, mock servers, code generation'),
    ('sdk-development', 'SDK development - multi-language SDKs, versioning, distribution, documentation, testing'),
    ('cli-development', 'CLI development - argument parsing, interactive prompts, config files, auto-complete'),
    # Observability
    ('opentelemetry-setup', 'OpenTelemetry setup - traces, metrics, logs, exporters, instrumentation, sampling'),
    ('datadog-monitoring', 'Datadog monitoring - APM, logs, metrics, synthetics, dashboards, alerts, SLOs'),
    ('new-relic-observability', 'New Relic observability - full-stack observability, NRQL, alerts, synthetic monitoring'),
    ('cloudwatch-monitoring', 'AWS CloudWatch - metrics, alarms, logs, dashboards, Insights, EventBridge'),
    ('elastic-observability', 'Elastic Stack observability - Elasticsearch, Kibana, Beats, APM, log aggregation'),
    # Testing
    ('contract-testing', 'Contract testing - Pact, consumer-driven contracts, API compatibility, CI integration'),
    ('chaos-engineering', 'Chaos engineering - Chaos Monkey, Gremlin, fault injection, resilience testing'),
    ('load-testing-advanced', 'Load testing advanced - k6, Locust, JMeter, performance budgets, SLO validation'),
    ('mutation-testing', 'Mutation testing - Stryker, PIT, mutation score, test quality assessment'),
    ('snapshot-testing', 'Snapshot testing - Jest snapshots, Storybook stories, visual regression, Percy'),
    # API design
    ('rest-api-design-advanced', 'REST API design advanced - HATEOAS, versioning, pagination, filtering, bulk ops'),
    ('grpc-design', 'gRPC design - proto files, streaming, interceptors, reflection, load balancing'),
    ('graphql-design', 'GraphQL schema design - types, resolvers, subscriptions, federation, DataLoader'),
    ('websocket-design', 'WebSocket design - connection management, heartbeat, reconnection, rooms, scaling'),
    ('event-driven-architecture', 'Event-driven architecture - event sourcing, CQRS, outbox pattern, saga pattern'),
    # Architecture patterns
    ('microservices-design', 'Microservices design - service mesh, API gateway, service discovery, circuit breaker'),
    ('serverless-architecture', 'Serverless architecture - Lambda, Step Functions, event-driven, cold starts, patterns'),
    ('hexagonal-architecture', 'Hexagonal architecture - ports and adapters, dependency inversion, clean architecture'),
    ('twelve-factor-app', 'Twelve-factor app - config, logs, processes, concurrency, backing services, dev/prod parity'),
    ('caching-strategies', 'Caching strategies - Redis, CDN, HTTP caching, cache invalidation, write-through, aside'),
    # Database patterns
    ('database-sharding', 'Database sharding - horizontal partitioning, shard keys, consistent hashing, resharding'),
    ('database-replication', 'Database replication - master-replica, multi-master, CDC, logical replication, failover'),
    ('time-series-db', 'Time series databases - InfluxDB, TimescaleDB, Prometheus, OpenTSDB, time series queries'),
    ('graph-database', 'Graph databases - Neo4j, Memgraph, Cypher queries, graph algorithms, knowledge graphs'),
    ('document-database', 'Document databases - MongoDB aggregation, Atlas Search, change streams, transactions'),
    # Platform engineering
    ('internal-developer-platform', 'Internal developer platform - self-service, golden paths, Backstage, templates, CNOE'),
    ('gitops-advanced', 'GitOps advanced - Flux, ArgoCD, multi-env, secrets management, drift detection'),
    ('platform-as-product', 'Platform as product - developer experience, NPS, adoption metrics, documentation'),
    ('policy-as-code', 'Policy as code - OPA, Kyverno, Gatekeeper, Conftest, compliance automation'),
    # AI/ML ops
    ('feature-store', 'Feature store - Feast, Tecton, Hopsworks, online/offline serving, feature versioning'),
    ('model-registry', 'Model registry - MLflow, W&B, DVC, model versioning, metadata, lineage tracking'),
    ('llm-gateway', 'LLM gateway - rate limiting, cost tracking, fallbacks, caching, model routing'),
    ('prompt-management', 'Prompt management - versioning, A/B testing, evaluation, templating, registry'),
    ('ai-cost-optimization', 'AI cost optimization - token reduction, caching, model routing, batching, compression'),
    # Growth/Marketing analytics
    ('attribution-modeling', 'Attribution modeling - multi-touch attribution, MMM, incrementality testing, LTV'),
    ('conversion-rate-optimization', 'Conversion rate optimization - hypothesis framework, testing, heatmaps, sessions'),
    ('product-analytics', 'Product analytics - funnel analysis, retention, cohorts, feature adoption, DAU/MAU'),
    ('customer-data-platform', 'Customer data platform - identity resolution, segment, data unification, activation'),
    ('marketing-automation', 'Marketing automation - lifecycle campaigns, segmentation, personalization, scoring'),
    # Enterprise integration
    ('sap-integration', 'SAP integration - SAP BTP, RFC, BAPI, IDoc, OData, S/4HANA APIs, connectors'),
    ('salesforce-advanced', 'Salesforce advanced - Apex, LWC, Flow, integration patterns, custom objects, SOQL'),
    ('mulesoft-integration', 'MuleSoft integration - Anypoint Platform, flows, connectors, DataWeave, API management'),
    ('boomi-integration', 'Boomi integration - processes, connectors, shapes, map functions, deployment'),
    # Specific industry
    ('healthtech-hl7', 'HL7/FHIR healthcare - resource types, SMART auth, clinical data, interoperability'),
    ('edtech-lms', 'EdTech LMS integration - xAPI, SCORM, LTI, Canvas, Moodle, learning analytics'),
    ('fintech-iso20022', 'FinTech ISO 20022 - payment messages, SWIFT, SEPA, real-time payments, compliance'),
    ('govtech-integration', 'GovTech integration - digital identity, open data APIs, e-government services'),
    # Advanced security
    ('devsecops', 'DevSecOps - SAST, DAST, SCA, secrets scanning, pipeline security, SBOM, zero trust'),
    ('cloud-security', 'Cloud security - CSPM, CWPP, CNAPP, IAM hardening, encryption, network security'),
    ('appsec-program', 'Application security program - threat modeling, secure SDLC, bug bounty, pentest mgmt'),
    ('zero-trust-architecture', 'Zero trust architecture - identity-first, micro-segmentation, BeyondCorp, ZTNA'),
    # Specific tools
    ('dagger-cicd', 'Dagger CI/CD - programmable pipelines, containers, caching, cross-platform, multi-language'),
    ('earthly-builds', 'Earthly builds - reproducible builds, Docker-based, caching, monorepo support'),
    ('buf-protobuf', 'Buf protobuf - schema management, linting, breaking change detection, BSR registry'),
    ('temporal-workflows', 'Temporal workflows - durable execution, activities, signals, queries, scheduling'),
    ('encore-backend', 'Encore backend - infrastructure from code, auto-provision, distributed tracing, local env'),
    ('railway-deploy', 'Railway deployment - one-click deploy, databases, services, networking, environments'),
    ('fly-io-deploy', 'Fly.io deployment - edge compute, global distribution, volumes, private networking, WireGuard'),
    ('coolify-selfhost', 'Coolify self-hosting - open-source Heroku, auto-deploy, domains, SSL, databases'),
    # AI coding tools
    ('cursor-advanced', 'Cursor advanced - AI rules, codebase indexing, multi-file edit, composer, chat modes'),
    ('github-copilot-advanced', 'GitHub Copilot advanced - workspace agents, code review, slash commands, custom models'),
    ('aider-coding', 'Aider AI coding - repo map, model selection, git integration, architect mode, voice'),
    ('continue-dev', 'Continue.dev - IDE extension, model configuration, context providers, slash commands'),
    ('codeium-integration', 'Codeium AI - autocomplete, chat, command, enterprise, context-aware suggestions'),
    # Data formats/protocols
    ('protobuf-patterns', 'Protocol Buffers patterns - schema design, evolution, options, well-known types'),
    ('avro-schema', 'Apache Avro schema - schema evolution, compatibility, generic records, Confluent registry'),
    ('parquet-files', 'Apache Parquet - columnar storage, compression, predicates, partitioning, Python/Spark'),
    ('arrow-format', 'Apache Arrow - in-memory columnar format, Flight RPC, DataFusion, cross-language'),
    # Analytics engineering
    ('dbt-analytics', 'dbt analytics engineering - dimensional modeling, data vault, metrics layer, semantic layer'),
    ('snowflake-advanced', 'Snowflake advanced - Snowpark, Cortex, data sharing, streams, tasks, dynamic tables'),
    ('redshift-optimization', 'Amazon Redshift optimization - distribution keys, sort keys, concurrency scaling, Spectrum'),
    ('clickhouse-advanced', 'ClickHouse advanced - materialized views, engines, merges, tuning, replication, cluster'),
    # Specific AI platforms
    ('google-vertex', 'Google Vertex AI - model garden, Gemini, pipelines, endpoints, feature store, AutoML'),
    ('aws-bedrock', 'AWS Bedrock - foundation models, Titan, Claude on Bedrock, RAG, agents, guardrails'),
    ('azure-openai-service', 'Azure OpenAI Service - deployments, fine-tuning, content filter, virtual network, RBAC'),
    ('together-inference', 'Together AI inference - model catalog, fine-tuning, dedicated endpoints, embeddings'),
    # Misc tools
    ('kafka-connect', 'Kafka Connect - source/sink connectors, SMT, schema registry integration, scaling'),
    ('redis-advanced', 'Redis advanced - clustering, pub/sub, streams, Lua scripts, modules, RedisJSON'),
    ('elasticsearch-advanced', 'Elasticsearch advanced - mappings, analyzers, aggregations, ML, search tuning'),
    ('cassandra-patterns', 'Cassandra patterns - data modeling, partition keys, clustering, tuning, multi-region'),
    ('cockroachdb', 'CockroachDB - distributed SQL, multi-region, geo-partitioning, serializable isolation'),
    ('tidb-patterns', 'TiDB patterns - HTAP, TiFlash, distributed transactions, migration from MySQL'),
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
- Performance optimization

## Models to Use
- Architecture: claude-opus-4-6
- Implementation: claude-sonnet-4-6
- Quick lookups: claude-haiku-4-5-20251001
'''
    with open(os.path.join(d, 'SKILL.md'), 'w') as f:
        f.write(content)

print('Done:', len(skills), 'skills')
