
import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # More AI model providers and APIs
    ('groq-inference', 'Groq LPU inference - ultra-fast LLM serving, GroqCloud API, streaming, tool calling, batching'),
    ('together-ai', 'Together AI - open model inference, fine-tuning, embeddings, serverless, dedicated instances'),
    ('mistral-ai-api', 'Mistral AI API - Le Chat, models, function calling, JSON mode, embeddings, enterprise'),
    ('cohere-platform', 'Cohere platform - Command, Rerank, Embed, RAG, fine-tuning, enterprise deployment'),
    ('ai21-studio', 'AI21 Studio - Jamba, Jurassic models, Task-specific APIs, summarize, paraphrase, rewrite'),
    ('amazon-bedrock', 'Amazon Bedrock - managed foundation models, agents, knowledge bases, guardrails, custom models'),
    ('google-vertex-ai', 'Google Vertex AI - Gemini API, Model Garden, fine-tuning, Agent Builder, Vector Search'),
    ('azure-openai', 'Azure OpenAI Service - deployments, fine-tuning, DALL-E, Whisper, embeddings, content filter'),
    # More specialized LLM techniques
    ('function-calling-advanced', 'Function calling advanced - parallel calls, tool choice, streaming, JSON schema, validation'),
    ('structured-outputs', 'Structured outputs - JSON mode, constrained generation, response format, type-safe extraction'),
    ('llm-caching', 'LLM caching - semantic cache, prompt caching, Redis cache, GPTCache, cost reduction'),
    ('context-compression', 'Context compression - LLMLingua, selective compression, summarization, token optimization'),
    ('long-context-llm', 'Long context LLM - 128k+ context, chunking strategies, needle-in-haystack, retrieval'),
    ('llm-routing-advanced', 'LLM routing advanced - cost-quality tradeoff, cascade routing, semantic routing, fallback'),
    # More embedding and retrieval
    ('cohere-embed', 'Cohere Embed - multilingual embeddings, compression, int8, binary, Embed Jobs, evaluation'),
    ('openai-embeddings', 'OpenAI embeddings - text-embedding-3, dimensionality reduction, batch API, use cases'),
    ('voyage-embeddings', 'Voyage AI embeddings - domain-specific, code, finance, law, multimodal, reranker'),
    ('jina-embeddings', 'Jina embeddings - long document, late chunking, ColBERT reranker, reader, segmenter'),
    ('nomic-embeddings', 'Nomic embeddings - nomic-embed-text, open-source, long context, Atlas visualization'),
    # More agent frameworks
    ('llama-index-agents', 'LlamaIndex agents - ReAct, OpenAI, tool use, memory, multi-agent, workflows'),
    ('langchain-agents', 'LangChain agents - LCEL, structured tools, memory, streaming, multi-agent, evaluation'),
    ('openai-assistants', 'OpenAI Assistants API - threads, messages, file search, code interpreter, function calling'),
    ('anthropic-tools', 'Anthropic tool use - tool definition, parallel tools, streaming, computer use, vision'),
    ('gemini-function-calling', 'Gemini function calling - function declarations, automatic calling, parallel, code execution'),
    # More DevOps CI/CD
    ('github-actions-advanced', 'GitHub Actions advanced - reusable workflows, matrix, environments, OIDC, caching, self-hosted'),
    ('gitlab-ci-advanced', 'GitLab CI/CD advanced - DAG, includes, rules, environments, artifacts, security scanning'),
    ('jenkins-advanced', 'Jenkins advanced - shared libraries, Jenkinsfile, agents, Blue Ocean, declarative pipeline'),
    ('circleci-advanced', 'CircleCI advanced - orbs, contexts, dynamic config, resource classes, test splitting, caching'),
    ('drone-ci', 'Drone CI - container-native, plugins, pipelines, secrets, volumes, multi-platform builds'),
    # More SRE/Operations
    ('incident-management', 'Incident management - PagerDuty, OpsGenie, alerting, escalation, runbooks, postmortems'),
    ('chaos-engineering', 'Chaos engineering - steady state, hypotheses, experiments, GameDays, blast radius control'),
    ('capacity-planning', 'Capacity planning - demand forecasting, resource modeling, headroom, cost projection'),
    ('performance-testing', 'Performance testing - load testing, stress testing, soak, spike, artillery, k6, JMeter'),
    ('reliability-patterns', 'Reliability patterns - circuit breaker, retry, timeout, bulkhead, rate limit, health check'),
    # More data processing
    ('apache-arrow', 'Apache Arrow - columnar format, zero-copy, IPC, Flight, compute kernels, ADBC, interop'),
    ('apache-iceberg', 'Apache Iceberg - table format, time travel, schema evolution, partitioning, catalog, compaction'),
    ('apache-hudi', 'Apache Hudi - incremental processing, upserts, CDC, copy-on-write, merge-on-read, timeline'),
    ('delta-lake-advanced', 'Delta Lake advanced - ACID, time travel, optimize, ZORDER, deletion vectors, Liquid clustering'),
    ('apache-parquet', 'Apache Parquet - columnar storage, encoding, compression, row groups, statistics, predicate pushdown'),
    # More API design
    ('openapi-advanced', 'OpenAPI 3.1 advanced - components, discriminators, webhooks, security schemes, code gen'),
    ('graphql-advanced', 'GraphQL advanced - dataloaders, subscriptions, persisted queries, schema design, security'),
    ('grpc-design', 'gRPC API design - proto design patterns, versioning, error handling, streaming patterns'),
    ('rest-api-design', 'REST API design - resource modeling, HATEOAS, versioning, pagination, filtering, standards'),
    ('api-gateway-patterns', 'API gateway patterns - routing, auth, rate limiting, transformation, aggregation, BFF'),
    # More frontend architecture
    ('micro-frontend-advanced', 'Micro-frontend advanced - module federation, shell app, routing, state sharing, testing'),
    ('design-system-build', 'Design system building - tokens, components, documentation, publishing, adoption, governance'),
    ('component-library', 'Component library - Storybook, testing, accessibility, bundling, versioning, distribution'),
    ('frontend-testing', 'Frontend testing strategy - unit, integration, E2E, visual regression, a11y, performance'),
    ('web-performance', 'Web performance - Core Web Vitals, LCP, FID, CLS, INP, optimization techniques, monitoring'),
    # More cloud native patterns
    ('service-mesh-advanced', 'Service mesh advanced - traffic management, mTLS, observability, WASM extensions, ambient'),
    ('gitops-advanced', 'GitOps advanced - declarative infra, drift detection, secrets, multi-tenancy, notifications'),
    ('policy-as-code', 'Policy as code - OPA, Rego, Conftest, Kyverno, validating policies, mutation, audit'),
    ('config-management', 'Configuration management - external config, feature flags, dynamic config, config drift'),
    ('secrets-management', 'Secrets management - Vault, AWS Secrets Manager, Azure Key Vault, rotation, injection'),
    # More ML Ops
    ('mlflow-advanced', 'MLflow advanced - recipes, model registry, projects, plugins, autologging, deployment'),
    ('kubeflow-advanced', 'Kubeflow advanced - pipelines, Katib, KServe, training operators, notebooks, profiles'),
    ('bentoml-serving', 'BentoML serving - runners, services, bentos, cloud deployment, adaptive batching'),
    ('ray-serve-advanced', 'Ray Serve advanced - deployments, ingress, scaling, composition, batching, grading'),
    ('triton-server', 'Triton Inference Server - model repository, backends, dynamic batching, ensemble, perf analyzer'),
    # More specific programming patterns
    ('reactive-programming', 'Reactive programming - RxJS, Project Reactor, RxPY, observables, operators, backpressure'),
    ('functional-programming', 'Functional programming - pure functions, immutability, composition, monads, pattern matching'),
    ('event-driven-architecture', 'Event-driven architecture - event sourcing, CQRS, event store, projections, sagas'),
    ('domain-driven-design', 'Domain-driven design - bounded contexts, aggregates, value objects, domain events, ubiquitous language'),
    ('clean-architecture', 'Clean architecture - use cases, entities, adapters, frameworks, dependency rule, testing'),
    # More auth and identity
    ('auth0-advanced', 'Auth0 advanced - actions, custom domains, Organizations, machine-to-machine, attack protection'),
    ('keycloak-advanced', 'Keycloak advanced - realms, clients, flows, SPI extensions, event listeners, clustering'),
    ('okta-advanced', 'Okta advanced - workflows, lifecycle management, API access management, Hooks, inline hooks'),
    ('ory-stack', 'Ory stack - Hydra, Kratos, Keto, Oathkeeper, open-source identity, self-hosted'),
    ('supertokens-auth', 'SuperTokens - open-source auth, session management, custom UI, multi-tenancy, recipes'),
    # More caching patterns
    ('cache-strategies', 'Cache strategies - aside, read-through, write-through, write-behind, refresh-ahead'),
    ('distributed-caching', 'Distributed caching - Redis, Memcached, Hazelcast, consistency, invalidation, stampede'),
    ('cdn-advanced', 'CDN advanced - purging, custom cache rules, edge logic, Varnish, Nginx caching, stale-while-revalidate'),
    ('browser-caching', 'Browser caching - Cache-Control, ETags, Service Worker cache, IndexedDB, localStorage strategies'),
    ('application-caching', 'Application-level caching - memoization, query caching, ORM caching, fragment caching'),
    # More search
    ('elasticsearch-advanced', 'Elasticsearch advanced - mappings, analyzers, aggregations, cross-cluster, ILM, security'),
    ('opensearch-advanced', 'OpenSearch advanced - k-NN search, neural search, SQL, PPL, anomaly detection, security'),
    ('typesense-search', 'Typesense - fast search, typo tolerance, facets, synonyms, geo, federated search'),
    ('meilisearch-advanced', 'Meilisearch advanced - custom ranking, filters, geosearch, multi-search, Meilisearch Cloud'),
    ('algolia-advanced', 'Algolia advanced - InstantSearch, federated search, NeuralSearch, Recommend, A/B testing'),
    # More workflow and task management
    ('workflow-engines', 'Workflow engine patterns - DAGs, state machines, saga coordination, human tasks, versioning'),
    ('job-scheduling', 'Job scheduling - cron, distributed locks, exactly-once, priorities, retry strategies, dead letters'),
    ('background-jobs', 'Background job patterns - Bull/BullMQ, Sidekiq, Celery, worker pools, job monitoring'),
    ('event-scheduling', 'Event scheduling - delayed events, at-most-once, at-least-once, exactly-once, temporal coupling'),
    ('task-queue-patterns', 'Task queue patterns - priority queues, fan-out, chaining, result storage, monitoring'),
    # More frontend tooling
    ('vite-advanced', 'Vite advanced - plugins, SSR, library mode, env handling, proxy, optimization, preview'),
    ('webpack-advanced', 'Webpack advanced - code splitting, dynamic imports, custom loaders, plugins, module federation'),
    ('esbuild-advanced', 'esbuild advanced - plugins API, transform API, build API, incremental builds, watch mode'),
    ('swc-advanced', 'SWC advanced - custom transforms, plugins, Wasm, Jest integration, Next.js integration'),
    ('parcel-bundler', 'Parcel bundler - zero config, transformers, optimizers, packagers, reporters, resolvers'),
    # More testing
    ('accessibility-testing', 'Accessibility testing - axe-core, WAVE, Pa11y, Deque, Lighthouse a11y, screen reader testing'),
    ('visual-testing', 'Visual regression testing - Chromatic, Percy, Applitools, BackstopJS, screenshot diffing'),
    ('load-testing-advanced', 'Load testing advanced - distributed load, realistic scenarios, think time, assertions, SLOs'),
    ('mutation-testing', 'Mutation testing - Stryker, PiTest, mutant survival, test quality, infection analysis'),
    ('contract-testing', 'Contract testing - Pact, Spring Cloud Contract, provider verification, breaking changes'),
    # More databases
    ('timescaledb', 'TimescaleDB - hypertables, continuous aggregates, compression, retention, PostgreSQL extension'),
    ('influxdb-advanced', 'InfluxDB advanced - Flux, tasks, dashboards, alerts, InfluxDB Cloud, IOx engine'),
    ('clickhouse-advanced', 'ClickHouse advanced - MergeTree, materialized views, dictionaries, sharding, replication'),
    ('duckdb-advanced', 'DuckDB advanced - extensions, httpfs, spatial, WASM, Python/R integration, Motherduck'),
    ('sqlite-patterns', 'SQLite patterns - WAL mode, extensions, SQLite Cloud, Litestream, LibSQL, Turso'),
    # More enterprise integration
    ('kafka-streams', 'Kafka Streams - stateful processing, KTable, GlobalKTable, joins, windowing, interactive queries'),
    ('kafka-connect', 'Kafka Connect - source/sink connectors, SMTs, exactly-once, distributed mode, schema registry'),
    ('spring-integration', 'Spring Integration - message channels, endpoints, adapters, gateways, aggregators, routers'),
    ('apache-camel', 'Apache Camel - EIP patterns, routes, components, data formats, testing, Camel K'),
    ('mulesoft-anypoint', 'MuleSoft Anypoint - flows, connectors, DataWeave, API Manager, Exchange, CloudHub'),
    # More low-code/no-code platforms
    ('retool-advanced', 'Retool advanced - custom components, resource APIs, workflows, staging, multi-branch, SSO'),
    ('appsmith-advanced', 'Appsmith advanced - custom widgets, datasources, audit logs, multi-tenant, Git sync'),
    ('budibase-platform', 'Budibase - open-source low-code, automation, data sources, custom plugins, self-hosted'),
    ('tooljet-advanced', 'ToolJet advanced - custom components, multi-workspace, release versioning, marketplace'),
    ('internal-io', 'Internal.io - workflow automation, integrations, approval flows, audit, enterprise features'),
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
