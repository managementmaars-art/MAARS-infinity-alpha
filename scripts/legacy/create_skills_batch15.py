
import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # Emerging AI models and providers
    ('deepseek-v3', 'DeepSeek V3 - mixture of experts, code generation, reasoning, API integration, fine-tuning'),
    ('qwen-models', 'Qwen models - Qwen2.5, Qwen-VL, Qwen-Code, API usage, fine-tuning, deployment'),
    ('gemma-models', 'Gemma models - Google open weights, Gemma 2, CodeGemma, PaliGemma, fine-tuning'),
    ('phi-models', 'Microsoft Phi models - Phi-3, Phi-4, small language models, edge deployment, fine-tuning'),
    ('llama-3-advanced', 'Llama 3.x - Llama 3.3, 3.2 Vision, tool use, fine-tuning, quantization, deployment'),
    ('mistral-models', 'Mistral models - Mistral Large, Codestral, Pixtral, Ministral, API, fine-tuning'),
    ('command-r-models', 'Cohere Command R+ - RAG-optimized, tool use, structured generation, embedding models'),
    # More AI reasoning and planning
    ('chain-of-draft', 'Chain of Draft - concise reasoning, token efficiency, draft-then-refine, planning'),
    ('tree-of-thought', 'Tree of Thought - deliberate exploration, BFS/DFS reasoning, backtracking, evaluation'),
    ('program-of-thought', 'Program of Thought - code as reasoning, PoT prompting, math, structured problem solving'),
    ('skeleton-of-thought', 'Skeleton of Thought - parallel decoding, answer skeleton, speedup, quality tradeoffs'),
    ('thread-of-thought', 'Thread of Thought prompting - complex context, query resolution, reasoning extraction'),
    # More data science and ML
    ('xgboost-advanced', 'XGBoost advanced - custom objectives, DART, GPU training, feature importance, tuning'),
    ('lightgbm-advanced', 'LightGBM advanced - GOSS, EFB, categorical features, custom metrics, GPU, distributed'),
    ('catboost-advanced', 'CatBoost - categorical features, symmetric trees, ordered boosting, GPU, ONNX export'),
    ('tabpfn', 'TabPFN - prior-fitted networks, tabular meta-learning, zero-shot, few-shot classification'),
    ('autotabular', 'AutoML for tabular - Auto-Sklearn, AutoGluon-Tabular, FLAML, feature selection, ensembles'),
    ('imbalanced-learning', 'Imbalanced learning - SMOTE, ADASYN, class weights, threshold tuning, sampling strategies'),
    # More AI evaluation
    ('benchmarking-llms', 'LLM benchmarking - MMLU, HumanEval, GSM8K, BIG-Bench, custom benchmarks, leaderboards'),
    ('red-teaming-advanced', 'AI red teaming advanced - adversarial prompts, jailbreak taxonomy, automated attacks'),
    ('preference-learning', 'Preference learning - RLHF, DPO, ORPO, SimPO, KTO, preference datasets, reward models'),
    ('alignment-techniques', 'Alignment techniques - constitutional AI, RLAIF, SFT, instruction following, harmlessness'),
    ('llm-as-judge', 'LLM-as-judge evaluation - pairwise comparison, single-turn, multi-turn, calibration, bias'),
    # More Python ecosystem
    ('pydantic-settings', 'Pydantic Settings - environment variables, config files, secrets, validation, nested models'),
    ('fastapi-sqlmodel', 'FastAPI + SQLModel - type-safe ORM, async, relationships, migrations, testing'),
    ('sqlalchemy-advanced', 'SQLAlchemy 2.0 advanced - async ORM, mapped classes, events, custom types, testing'),
    ('celery-advanced', 'Celery advanced - routing, priorities, canvas, error handling, monitoring, testing'),
    ('dramatiq', 'Dramatiq - task processing, brokers, middleware, rate limiting, scheduling, testing'),
    # More TypeScript/JavaScript ecosystem
    ('drizzle-advanced', 'Drizzle ORM advanced - relations, transactions, queries, migrations, testing, Turso'),
    ('prisma-advanced', 'Prisma advanced - schema design, raw SQL, extensions, accelerate, pulse, testing'),
    ('hono-testing', 'Hono testing - testClient, request testing, middleware testing, snapshot, coverage'),
    ('next-auth-advanced', 'NextAuth.js v5 - providers, callbacks, database adapters, JWT, session, middleware'),
    ('lucia-auth', 'Lucia auth - sessions, OAuth, database adapters, framework adapters, security patterns'),
    # More Go ecosystem
    ('go-testing-advanced', 'Go testing advanced - table-driven, subtests, benchmarks, fuzzing, testify, mocking'),
    ('go-grpc-patterns', 'Go gRPC patterns - interceptors, streaming, error handling, metadata, reflection'),
    ('ent-framework', 'Ent ORM framework - schema as code, graph traversal, code generation, hooks, privacy'),
    ('gorm-advanced', 'GORM advanced - associations, hooks, scopes, raw SQL, migrations, performance'),
    ('cobra-cli', 'Cobra CLI framework - commands, flags, persistent flags, completions, help generation'),
    # More Rust ecosystem
    ('axum-advanced', 'Axum advanced - middleware, state, extractors, error handling, WebSocket, testing'),
    ('sea-orm', 'SeaORM - async ORM, entity, relation, migration, mock, Rocket/Axum integration'),
    ('bevy-ui', 'Bevy UI - node bundles, layout, widgets, interaction, theming, responsive design'),
    ('tauri-plugins', 'Tauri plugins - official plugins, custom plugins, capabilities, permissions, testing'),
    ('leptos-advanced', 'Leptos advanced - server functions, islands, suspense, resources, error boundaries'),
    # More Java/Kotlin ecosystem
    ('spring-data-jpa', 'Spring Data JPA - repositories, custom queries, pagination, projections, auditing'),
    ('spring-security', 'Spring Security advanced - OAuth2, JWT, method security, test support, reactive'),
    ('quarkus-framework', 'Quarkus - native compilation, reactive, extensions, dev services, testing, kubernetes'),
    ('micronaut-framework', 'Micronaut - AOT, dependency injection, data, security, test resources, tracing'),
    ('ktor-server', 'Ktor server - routing, plugins, sessions, serialization, testing, deployment'),
    # More .NET ecosystem
    ('minimal-apis', '.NET Minimal APIs - endpoint filters, parameter binding, OpenAPI, versioning, testing'),
    ('efcore-advanced', 'EF Core advanced - raw SQL, compiled queries, shadow properties, value converters, testing'),
    ('signalr-advanced', 'SignalR advanced - hubs, groups, users, connections, horizontal scaling, testing'),
    ('orleans-dotnet', 'Microsoft Orleans - virtual actors, grains, persistence, streaming, reminders, testing'),
    ('mediatr-pattern', 'MediatR - CQRS, pipeline behaviors, notifications, polymorphic dispatch, testing'),
    # More infrastructure as code
    ('terragrunt-advanced', 'Terragrunt advanced - DRY configs, dependencies, run-all, hooks, cache, generators'),
    ('ansible-collections', 'Ansible Collections - roles, modules, plugins, testing with Molecule, Galaxy publishing'),
    ('ansible-awx', 'Ansible AWX/Tower - job templates, inventories, credentials, workflows, RBAC, API'),
    ('chef-infra', 'Chef Infra - cookbooks, recipes, resources, data bags, testing with InSpec, Chef Server'),
    ('saltstack-advanced', 'SaltStack advanced - pillars, grains, states, orchestration, event system, beacons'),
    # More cloud architecture
    ('well-architected-aws', 'AWS Well-Architected Framework - pillars, review process, Lens catalog, tool'),
    ('google-sre-practices', 'Google SRE practices - toil elimination, error budgets, CRE, SLO framework'),
    ('caf-azure', 'Azure Cloud Adoption Framework - landing zones, governance, migration, innovation'),
    ('finops-practices', 'FinOps practices - cost visibility, optimization, culture, forecasting, unit economics'),
    ('carbon-footprint-cloud', 'Cloud carbon footprint - Green Software Foundation, carbon-aware scheduling, tools'),
    # More privacy and compliance
    ('ccpa-compliance', 'CCPA compliance - opt-out, data deletion, disclosure, contractor requirements, audit'),
    ('lgpd-brazil', 'LGPD Brazil - data protection, consent, DPA, rights, international transfers, enforcement'),
    ('pdpa-thailand', 'PDPA Thailand - personal data, consent, rights, controller, processor, enforcement'),
    ('popia-africa', 'POPIA South Africa - information officer, conditions, consent, breach notification'),
    ('data-residency', 'Data residency - geographic restrictions, sovereign cloud, data localization, compliance'),
    # More API monetization and developer experience
    ('api-monetization', 'API monetization - usage-based, freemium tiers, API keys, quota enforcement, analytics'),
    ('developer-portal-advanced', 'Developer portal advanced - Backstage, ReadMe, Redoc, Stoplight, SDK generation'),
    ('api-analytics', 'API analytics - request metrics, error rates, latency, top consumers, funnel analysis'),
    ('openapi-generator', 'OpenAPI Generator - client SDKs, server stubs, 50+ languages, custom templates'),
    ('api-mocking-advanced', 'API mocking advanced - contract mocks, record/playback, chaos testing, dynamic responses'),
    # More edge and distributed computing
    ('cloudflare-durable-objects', 'Cloudflare Durable Objects - stateful serverless, actor model, storage, alarm API'),
    ('cloudflare-r2-patterns', 'Cloudflare R2 advanced - presigned URLs, CORS, large uploads, migration from S3'),
    ('fly-io-advanced', 'Fly.io advanced - volumes, private networking, secrets, machines API, blue-green'),
    ('deno-deploy', 'Deno Deploy - edge functions, KV, queues, cron, GitHub integration, custom domains'),
    ('fastly-compute', 'Fastly Compute@Edge - WebAssembly, Rust/Go/JS, fiddle, CDN integration, testing'),
    # More database technologies
    ('neon-serverless-advanced', 'Neon serverless Postgres - branching, serverless driver, autoscaling, connection pooling'),
    ('planetscale-advanced', 'PlanetScale advanced - branching, deploy requests, schema diff, insights, sharding'),
    ('cockroachdb-advanced', 'CockroachDB advanced - multi-region tables, geo-partitioning, follower reads, CDC'),
    ('tidb-advanced', 'TiDB advanced - HTAP, TiFlash, TiKV, distributed transactions, online DDL, scaling'),
    ('yugabyte-advanced', 'YugabyteDB advanced - YSQL, YCQL, replication, geo-distribution, follower reads'),
    # More AI agent patterns
    ('autonomous-coding', 'Autonomous coding agents - task planning, code generation, debugging, testing loops'),
    ('computer-use-advanced', 'Computer use advanced - GUI automation, screen understanding, keyboard/mouse, safety'),
    ('web-agent-patterns', 'Web agent patterns - browser automation, form filling, navigation, extraction, verification'),
    ('multi-modal-agents', 'Multi-modal agents - vision + language, image understanding, chart reading, UI parsing'),
    ('agent-memory-advanced', 'Agent memory advanced - episodic, semantic, procedural, working memory, compression'),
    # More specialized domains
    ('drug-discovery-ai', 'Drug discovery AI - molecular generation, property prediction, docking, ADMET, optimization'),
    ('materials-science-ai', 'Materials science AI - crystal structure prediction, property prediction, experimental design'),
    ('climate-modeling', 'Climate modeling AI - weather prediction, downscaling, extreme events, carbon modeling'),
    ('protein-language-models', 'Protein language models - ESM, ProtTrans, AlphaFold2, RoseTTAFold, structure prediction'),
    ('single-cell-genomics', 'Single-cell genomics - scRNA-seq, dimensionality reduction, trajectory analysis, integration'),
    # More platform engineering tools
    ('port-backstage', 'Port vs Backstage - developer portal comparison, catalogs, scorecards, self-service, migration'),
    ('roadie-backstage', 'Roadie.io - managed Backstage, plugins, catalog import, scaffolder, TechDocs hosting'),
    ('cortex-scorecards', 'Cortex scorecards - service maturity, ownership, on-call, documentation, automated checks'),
    ('opslevel-platform', 'OpsLevel - service catalog, rubric, checks, reports, integrations, notifications'),
    ('atmos-terraform', 'Atmos - Terraform automation, stacks, components, vendoring, workflow automation'),
    # More niche tools
    ('sqlite-extensions', 'SQLite extensions - FTS5, JSON1, spatialite, SQLite-vec, encryption, cloud sync'),
    ('deno-hono', 'Deno + Hono - full stack Deno, JSX, API routes, KV storage, Deploy integration'),
    ('bun-elysia', 'Bun + Elysia - type-safe routes, validation, documentation, lifecycle hooks, testing'),
    ('fresh-islands', 'Fresh islands architecture - Preact, partial hydration, Deno Deploy, island components'),
    ('solid-start', 'SolidStart - full-stack SolidJS, routing, data loading, server functions, deployment'),
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
