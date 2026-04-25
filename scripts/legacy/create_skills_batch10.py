
import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # More specialized AI/ML
    ('colpali-retrieval', 'ColPali visual retrieval - page-level embeddings, PDF retrieval, vision encoders, colbert'),
    ('reranker-models', 'Reranker models - cross-encoders, ColBERT, BGE reranker, Cohere rerank, FlashRank'),
    ('sparse-retrieval', 'Sparse retrieval - BM25, SPLADE, TF-IDF, ElasticSearch, sparse embeddings, hybrid'),
    ('bi-encoder-models', 'Bi-encoder models - sentence transformers, CLIP, dual encoders, contrastive learning'),
    ('late-interaction', 'Late interaction retrieval - ColBERT, token-level interaction, MaxSim, PLAID indexing'),
    ('vision-transformers', 'Vision Transformers - ViT, DINO, DINOv2, EVA, SigLIP, image features, fine-tuning'),
    ('clip-models', 'CLIP models - contrastive pretraining, zero-shot, image-text alignment, OpenCLIP variants'),
    ('multimodal-embeddings', 'Multimodal embeddings - ALIGN, Florence, Flamingo, cross-modal retrieval, alignment'),
    # More AI frameworks
    ('litgpt-training', 'LitGPT training - lightning fabric, pretraining, LoRA, quantization, evaluation, serving'),
    ('nanotron-training', 'Nanotron training - distributed training, 3D parallelism, checkpointing, evaluation'),
    ('olmo-training', 'OLMo training - open language model, training recipes, evaluation, release artifacts'),
    ('pythia-models', 'Pythia model suite - scaling analysis, training dynamics, interpretability, deduplication'),
    ('gpt-neo-training', 'GPT-Neo/GPT-J training - EleutherAI, Mesh Transformer JAX, evaluation, hardware'),
    # More tools/platforms
    ('weaviate-advanced', 'Weaviate advanced - modules, generative, hybrid search, multi-tenancy, cross-references'),
    ('qdrant-advanced', 'Qdrant advanced - payload indexing, sparse vectors, quantization, distributed, Rust client'),
    ('chroma-advanced', 'Chroma advanced - collections, metadata filtering, embedding functions, persistent, hosted'),
    ('milvus-advanced', 'Milvus advanced - partitions, dynamic schema, GPU indexing, consistency, Attu UI'),
    ('zilliz-cloud', 'Zilliz cloud - managed Milvus, vector database, auto-scaling, serverless, pipelines'),
    # More specialized tools
    ('notdiamond-routing', 'NotDiamond LLM routing - model routing, cost optimization, latency, quality metrics'),
    ('unify-ai', 'Unify AI - LLM benchmarking, routing, endpoints, evaluation, cost-quality tradeoffs'),
    ('openrouter-advanced', 'OpenRouter advanced - model routing, fallbacks, provider preferences, cost tracking'),
    ('anyscale-endpoints', 'Anyscale endpoints - LLM inference, fine-tuning, Ray-based, production deployment'),
    ('fireworks-advanced', 'Fireworks AI advanced - function calling, speculative decoding, fine-tuning, compound AI'),
    # More cloud patterns
    ('aws-organizations', 'AWS Organizations - SCPs, account management, OU structure, delegated admin, policies'),
    ('aws-control-tower', 'AWS Control Tower - landing zone, guardrails, account factory, customizations'),
    ('azure-landing-zone', 'Azure Landing Zone - management groups, policies, RBAC, networking, security baseline'),
    ('gcp-organization', 'GCP organization - resource hierarchy, IAM policies, folders, billing accounts, constraints'),
    ('multi-account-aws', 'Multi-account AWS - account vending, cross-account roles, consolidated billing, tagging'),
    # More database patterns
    ('read-replica-patterns', 'Read replica patterns - routing, lag monitoring, failover, consistency, connection pooling'),
    ('connection-pooling', 'Database connection pooling - PgBouncer, ProxySQL, HikariCP, pool sizing, monitoring'),
    ('query-optimization', 'Query optimization - EXPLAIN, indexes, query plans, statistics, hints, partitioning'),
    ('database-backup', 'Database backup strategies - logical, physical, streaming, PITR, cross-region, testing'),
    ('database-observability', 'Database observability - slow queries, locks, connections, replication lag, metrics'),
    # More frontend patterns
    ('server-components', 'React Server Components - RSC, streaming, Suspense, data fetching, serialization'),
    ('islands-architecture', 'Islands architecture - partial hydration, Astro, Fresh, Qwik, performance, static'),
    ('resumability', 'Resumability pattern - Qwik, serialization, lazy execution, no hydration cost, SSR'),
    ('signals-reactivity', 'Signals reactivity - fine-grained reactivity, SolidJS, Preact signals, Vue reactivity'),
    ('partial-hydration', 'Partial hydration - progressive enhancement, islands, deferred, selective hydration'),
    # More protocols
    ('matrix-federation', 'Matrix federation - server-server, event auth, room state, key verification, bridges'),
    ('xmpp-messaging', 'XMPP messaging - stanzas, MUC, OMEMO encryption, pubsub, federation, modern clients'),
    ('activitypub-protocol', 'ActivityPub protocol - actors, objects, activities, inbox/outbox, federation, Mastodon'),
    ('nostr-protocol', 'Nostr protocol - keys, events, relays, NIPs, clients, zaps, content addressable'),
    ('bluesky-atproto', 'Bluesky AT Protocol - DID, PLC, lexicons, firehose, appviews, PDS, handles'),
    # More development methodologies
    ('shape-up-method', 'Shape Up methodology - shaping, betting, building, six-week cycles, cool-down'),
    ('mob-programming', 'Mob programming - ensemble programming, driver/navigator, rotation, techniques, tooling'),
    ('pair-programming', 'Pair programming - styles, driver/navigator, ping-pong, code review, remote pairing'),
    ('trunk-based-dev', 'Trunk-based development - short-lived branches, feature flags, CI/CD, small commits'),
    ('continuous-deployment', 'Continuous deployment - automated testing, progressive delivery, rollback, monitoring'),
    # More specialized tools
    ('localstack-aws', 'LocalStack - local AWS cloud, services, pro features, persistence, CI integration'),
    ('moto-mocking', 'Moto AWS mocking - Python, boto3, servermode, decorator, state machine, all services'),
    ('wiremock', 'WireMock - HTTP mock server, stubs, verification, record/playback, standalone, extensions'),
    ('mockoon', 'Mockoon API mocking - desktop/CLI, scenarios, dynamic rules, response templating, proxy'),
    ('prism-mock', 'Prism API mock - OpenAPI, Postman, request validation, examples, proxy, CLI'),
    # More observability tools
    ('lgtm-stack', 'LGTM stack - Loki, Grafana, Tempo, Mimir, self-hosted observability, open-source'),
    ('o11y-week', 'Observability best practices - SLIs, SLOs, error budget, toil, incident management'),
    ('distributed-tracing-design', 'Distributed tracing design - sampling, instrumentation, span design, baggage, context'),
    ('sre-practices', 'SRE practices - error budgets, toil, blameless postmortems, runbooks, on-call rotation'),
    ('platform-sre', 'Platform SRE - reliability engineering for platforms, SLOs, automation, toil reduction'),
    # More AI safety
    ('llm-guardrails', 'LLM guardrails - input/output filtering, topic restrictions, injection prevention, NeMo'),
    ('content-moderation', 'Content moderation AI - toxicity detection, NSFW, spam, custom models, human review'),
    ('bias-detection', 'AI bias detection - fairness metrics, disparate impact, counterfactual, dataset audit'),
    ('model-explainability', 'Model explainability - SHAP, LIME, integrated gradients, attention, concept probing'),
    ('ai-governance', 'AI governance - policies, risk assessment, audit trails, transparency, compliance'),
    # More game dev
    ('godot-gdnative', 'Godot GDNative/GDExtension - native extensions, C++, Rust, binding, cross-platform'),
    ('unity-urp', 'Unity URP - Universal Render Pipeline, shaders, post-processing, performance, mobile'),
    ('unity-dots', 'Unity DOTS - ECS, Burst compiler, Job system, entities, high performance gaming'),
    ('unreal-niagara', 'Unreal Niagara - particle system, VFX, emitters, modules, GPU particles, events'),
    ('bevy-advanced', 'Bevy advanced - ECS queries, systems, schedules, plugins, assets, scenes, networking'),
    # More blockchain
    ('hyperledger-fabric', 'Hyperledger Fabric - chaincode, channels, MSP, endorsement, private data, CouchDB'),
    ('r3-corda', 'R3 Corda - states, contracts, flows, vaults, CorDapps, notaries, enterprise'),
    ('quorum-eth', 'Quorum/Hyperledger Besu - private Ethereum, Istanbul BFT, QBFT, private transactions'),
    ('stellar-xlm', 'Stellar blockchain - accounts, operations, transactions, anchors, Soroban smart contracts'),
    ('tezos-blockchain', 'Tezos blockchain - Michelson, SmartPy, Ligo, baking, governance, on-chain upgrades'),
    # More developer experience
    ('conventional-commits', 'Conventional commits - spec, types, scopes, breaking changes, changelog generation'),
    ('semantic-versioning', 'Semantic versioning - SemVer, pre-release, build metadata, automation, enforcement'),
    ('changesets-monorepo', 'Changesets for monorepos - versioning, changelogs, publishing, automated CI'),
    ('release-please', 'Release Please - automated releases, conventional commits, GitHub Actions, changelog'),
    ('semantic-release', 'Semantic Release - fully automated, versioning, changelog, npm, GitHub releases'),
    # More specialized domains
    ('geospatial-ml', 'Geospatial ML - satellite imagery, remote sensing, segmentation, object detection, point clouds'),
    ('medical-nlp', 'Medical NLP - clinical NLP, BioBERT, ClinicalBERT, NER, ICD coding, SNOMED'),
    ('legal-nlp', 'Legal NLP - contract NLP, clause extraction, legal BERT, entity recognition, summarization'),
    ('financial-nlp', 'Financial NLP - earnings calls, sentiment, FinBERT, named entity, regulatory filings'),
    ('scientific-nlp', 'Scientific NLP - paper understanding, SciBERT, citation graphs, hypothesis extraction'),
    # More infrastructure patterns
    ('cell-based-architecture', 'Cell-based architecture - blast radius, independence, routing, cell sizing, migration'),
    ('progressive-delivery', 'Progressive delivery - canary, feature flags, blue-green, ring deployment, rollback'),
    ('chaos-mesh', 'Chaos Mesh - chaos engineering Kubernetes, faults, experiments, dashboard, observability'),
    ('litmus-chaos', 'LitmusChaos - chaos engineering, hub, scenarios, probes, Kubernetes, CNCF'),
    ('toxiproxy', 'Toxiproxy - network conditions testing, latency, bandwidth, down, reset, slow close'),
    # More specific AI products
    ('perplexity-build', 'Building Perplexity-like apps - search grounding, citations, real-time, RAG pipeline'),
    ('cursor-build', 'Building Cursor-like apps - code indexing, context retrieval, tree-sitter, embeddings'),
    ('notion-ai-build', 'Building Notion AI features - block context, streaming, slash commands, inline AI'),
    ('copilot-build', 'Building GitHub Copilot alternatives - FIM, code completion, LSP, IDE integration'),
    ('agent-builder', 'Agent builder platforms - AutoGPT style, task decomposition, tool registry, memory'),
    # More compliance
    ('soc2-compliance', 'SOC2 compliance - trust service criteria, controls, evidence, audit preparation'),
    ('iso27001-compliance', 'ISO 27001 compliance - ISMS, risk assessment, controls, certification, documentation'),
    ('gdpr-implementation', 'GDPR implementation - data inventory, consent, DSAR, DPO, breach notification'),
    ('hipaa-technical', 'HIPAA technical safeguards - encryption, access control, audit logs, transmission security'),
    ('fedramp-authorization', 'FedRAMP authorization - ATO, SSP, controls, continuous monitoring, JAB, agency'),
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
