
import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # More SaaS/product areas
    ('subscription-billing', 'Subscription billing systems - Stripe, Recurly, Chargebee, dunning, proration, metered'),
    ('usage-based-pricing', 'Usage-based pricing - metering, aggregate, real-time, billing APIs, customer alerts'),
    ('marketplace-platform', 'Marketplace platform development - multi-vendor, escrow, fees, dispute resolution'),
    ('saas-onboarding', 'SaaS onboarding - activation, time-to-value, checklists, tours, email sequences'),
    ('customer-success', 'Customer success platform - health scores, expansion, at-risk, QBRs, playbooks'),
    ('product-led-growth', 'Product-led growth implementation - self-serve, freemium, virality, activation, expansion'),
    ('revenue-operations', 'Revenue operations - CRM hygiene, pipeline, forecasting, attribution, sales-marketing align'),
    # More specific ML use cases
    ('document-ai', 'Document AI - OCR, layout understanding, form extraction, intelligent document processing'),
    ('table-understanding', 'Table understanding - structure recognition, value extraction, reasoning, multi-table QA'),
    ('chart-understanding', 'Chart understanding - visual QA, data extraction, chart-to-text, derendering'),
    ('video-understanding', 'Video understanding - temporal reasoning, action recognition, captioning, search, QA'),
    ('3d-understanding', '3D scene understanding - point clouds, NeRF, depth estimation, 3D object detection'),
    ('speech-recognition', 'Speech recognition - ASR, Whisper, wav2vec2, streaming, speaker diarization, punctuation'),
    ('text-to-speech', 'Text-to-speech systems - TTS, neural voice, cloning, prosody, SSML, streaming'),
    # More DevOps patterns
    ('gitflow-workflow', 'GitFlow workflow - feature, release, hotfix branches, versioning, CI/CD integration'),
    ('feature-flags-advanced', 'Feature flags advanced - gradual rollout, targeting, experiments, kill switch, SDK'),
    ('deployment-strategies', 'Deployment strategies - blue-green, canary, shadow, rolling, immutable infrastructure'),
    ('infrastructure-testing', 'Infrastructure testing - Terratest, InSpec, serverspec, compliance scanning, drift'),
    ('cost-engineering', 'Cloud cost engineering - FinOps, tagging, right-sizing, savings plans, anomaly detection'),
    # More specific platforms
    ('shopify-hydrogen', 'Shopify Hydrogen - headless commerce, Remix, Oxygen, custom storefront, streaming'),
    ('medusa-commerce', 'Medusa headless commerce - open-source, modules, workflows, admin, payment plugins'),
    ('saleor-commerce', 'Saleor commerce - GraphQL, channels, apps, webhooks, checkout, products, plugins'),
    ('vendure-commerce', 'Vendure commerce - TypeScript, plugins, custom fields, facets, promotions, channels'),
    ('commerce-layer', 'Commerce Layer - API-first, multi-market, promotions, bundles, returns, subscriptions'),
    # More security patterns
    ('secret-rotation', 'Secret rotation - automated rotation, Vault, AWS Secrets Manager, rotation lambdas'),
    ('supply-chain-security', 'Software supply chain security - SBOM, signing, provenance, SLSA framework, GUAC'),
    ('container-security', 'Container security - image scanning, runtime protection, network policies, admission control'),
    ('kubernetes-security', 'Kubernetes security - RBAC, Pod Security, network policies, secrets, image policies'),
    ('api-security-advanced', 'API security advanced - OAuth threats, JWT attacks, broken object level, mass assignment'),
    # More data patterns
    ('data-contracts', 'Data contracts - schema agreements, SLAs, tooling, Soda, Great Expectations, dbt contracts'),
    ('data-catalog', 'Data catalog - Datahub, OpenMetadata, Alation, discovery, lineage, glossary, profiling'),
    ('data-lineage', 'Data lineage - column-level lineage, impact analysis, OpenLineage, Marquez, visualization'),
    ('reverse-etl', 'Reverse ETL - Hightouch, Census, operational analytics, warehouse-to-CRM, audience sync'),
    ('semantic-layer', 'Semantic layer - metrics, dimensions, LookML, dbt metrics, Cube, AtScale, unified API'),
    # More AI/ML patterns
    ('online-learning', 'Online learning - incremental learning, streaming ML, concept drift, model updates'),
    ('multi-task-learning', 'Multi-task learning - shared representations, task weighting, gradient surgery, Meta-learning'),
    ('continual-learning', 'Continual learning - catastrophic forgetting, EWC, progressive networks, replay buffers'),
    ('self-supervised-learning', 'Self-supervised learning - contrastive, masked modeling, MAE, SimCLR, MoCo, BYOL'),
    ('few-shot-learning', 'Few-shot learning - prototypical networks, meta-learning, prompt engineering, in-context'),
    # More tools
    ('temporal-cloud', 'Temporal Cloud - managed workflow, namespaces, export, MTLS, metrics, SLAs'),
    ('inngest-advanced', 'Inngest advanced - functions, events, crons, retries, concurrency, fan-out patterns'),
    ('trigger-dev-advanced', 'Trigger.dev advanced - jobs, events, delays, concurrency, runs, alert on failure'),
    ('restate-dev', 'Restate - durable execution, sagas, handlers, key-value, scheduling, idempotency'),
    ('hatchet-workflow', 'Hatchet workflow engine - tasks, workers, rate limiting, cron, workflows, durable'),
    # More testing
    ('contract-driven-dev', 'Contract-driven development - OpenAPI first, consumer tests, provider tests, mocking'),
    ('test-data-management', 'Test data management - synthetic data, masking, subsetting, environments, seeding'),
    ('golden-file-testing', 'Golden file testing - snapshot files, approval testing, diff review, update workflow'),
    ('approval-testing', 'Approval testing - ApprovalTests, text snapshots, binary diffs, legacy code, TCR'),
    ('exploratory-testing', 'Exploratory testing - session-based, charters, heuristics, mind maps, bug bashing'),
    # More languages
    ('v-lang', 'V language - simple, fast compilation, memory safety, no GC, cross-platform, C-like syntax'),
    ('carbon-lang', 'Carbon language - C++ successor, bidirectional interop, generics, memory safety, Google'),
    ('mojo-lang', 'Mojo language - Python superset, MLIR, SIMD, memory model, systems programming for AI'),
    ('odin-lang', 'Odin language - Go-inspired, data-oriented, C alternative, manual memory, context system'),
    ('beef-lang', 'Beef language - C++-like, high performance, allocator model, interop, real-time safe'),
    # More frameworks
    ('leptos-rust', 'Leptos Rust - full-stack Rust web, signals, server functions, islands, SSR, WASM'),
    ('yew-rust', 'Yew Rust - WASM frontend, components, hooks, agents, trunk bundler, Tailwind'),
    ('dioxus-rust', 'Dioxus Rust - React-like, cross-platform, WASM, desktop, mobile, TUI, server'),
    ('sycamore-rust', 'Sycamore Rust - reactive UI, fine-grained reactivity, isomorphic, SSR, signals'),
    ('perseus-rust', 'Perseus Rust - full-stack web, SSG, SSR, ISR, i18n, plugins, deploy'),
    # More AI research
    ('chain-of-thought', 'Chain of thought prompting - CoT, zero-shot CoT, Tree of Thought, automatic CoT'),
    ('constitutional-prompting', 'Constitutional AI prompting - critique, revision, RLAIF, HHH principles, red-teaming'),
    ('self-consistency', 'Self-consistency decoding - majority vote, diverse CoT, sampling strategies, reliability'),
    ('react-prompting', 'ReAct prompting - reason-act-observe, tool use, grounding, action space, reflection'),
    ('least-to-most', 'Least-to-most prompting - problem decomposition, subproblem solving, compositional'),
    # More productivity tools
    ('obsidian-advanced', 'Obsidian advanced - graph view, templates, dataview, canvas, plugins, publish'),
    ('notion-advanced', 'Notion advanced - databases, relations, rollups, formulas, API, automation, AI'),
    ('roam-advanced', 'Roam Research advanced - block references, queries, filtered views, daily notes, graph'),
    ('logseq-advanced', 'Logseq advanced - org-mode, queries, plugins, whiteboards, namespaces, property'),
    ('capacities-tool', 'Capacities - object-based PKM, daily notes, media, tags, AI integration, export'),
    # More infrastructure
    ('multi-region-deploy', 'Multi-region deployment - active-active, active-passive, data residency, latency routing'),
    ('edge-computing', 'Edge computing - CDN workers, Lambda@Edge, edge functions, geo-routing, caching strategies'),
    ('private-networking', 'Private networking - VPC peering, transit gateway, PrivateLink, VPN, Direct Connect'),
    ('service-accounts', 'Service accounts and workload identity - OIDC, workload federation, least privilege'),
    ('secrets-as-code', 'Secrets as code - SOPS, Sealed Secrets, ESO, Vault Agent, secrets injection patterns'),
    # More compliance/governance
    ('cloud-governance', 'Cloud governance - policy enforcement, tagging, cost allocation, guardrails, config rules'),
    ('shift-left-security', 'Shift-left security - SAST, DAST, SCA in CI, developer security, security champions'),
    ('threat-modeling-stride', 'STRIDE threat modeling - spoofing, tampering, repudiation, info disclosure, DoS, elevation'),
    ('privacy-by-design', 'Privacy by design - data minimization, anonymization, consent, DSAR, privacy reviews'),
    ('accessibility-a11y', 'Accessibility (a11y) - WCAG 2.2, ARIA, keyboard navigation, screen readers, color contrast'),
    # More cloud-native
    ('wasm-serverless', 'WASM serverless - Spin, Wasmtime, WASI, cold start, edge deployment, component model'),
    ('service-catalog', 'Service catalog management - ownership, runbooks, SLOs, dependencies, Backstage, OpsLevel'),
    ('platform-engineering', 'Platform engineering - golden paths, developer portals, paved roads, IDP, DX metrics'),
    ('developer-experience', 'Developer experience (DevEx) - onboarding, tooling, local dev, feedback loops, SPACE'),
    ('golden-path', 'Golden path templates - scaffolding, standards, automation, opinionated tooling, guardrails'),
    # More business intelligence
    ('dbt-semantic-layer', 'dbt Semantic Layer - MetricFlow, semantic models, entities, measures, dimensions, API'),
    ('looker-advanced', 'Looker advanced - LookML, PDTs, explores, native derived tables, JSON params, rendering'),
    ('mode-analytics', 'Mode Analytics - SQL, Python, R, visual builder, linked notebooks, reports, sharing'),
    ('hex-notebooks', 'Hex data notebooks - SQL, Python, R, visual, apps, scheduled reports, sharing'),
    ('streamlit-advanced', 'Streamlit advanced - session state, components, caching, multipage, deployment, custom'),
    # More specific tools/APIs
    ('resend-email', 'Resend email API - transactional email, React Email, domains, webhooks, logs, analytics'),
    ('loops-email', 'Loops email - transactional, marketing, events, contacts, sequences, integrations'),
    ('cal-com-advanced', 'Cal.com advanced - managed users, routing forms, teams, workflows, webhooks, atoms'),
    ('clerk-advanced', 'Clerk advanced - organizations, custom flows, webhooks, JWT templates, sessions, B2B'),
    ('novu-notifications', 'Novu notification infrastructure - channels, templates, digest, subscribers, tenant'),
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
