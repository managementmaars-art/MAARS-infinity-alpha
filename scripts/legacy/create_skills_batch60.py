
import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # Advanced data engineering patterns
    ('streaming-data-architecture', 'Streaming data architecture - Lambda, Kappa, CQRS+ES, exactly-once semantics, watermarks'),
    ('data-lakehouse-advanced', 'Data lakehouse advanced - Delta Lake, Iceberg, Hudi comparison, ACID transactions, time travel'),
    ('data-product-engineering', 'Data product engineering - data contracts, semantic layer, data as product, SLAs, discovery'),
    ('real-time-analytics-platform', 'Real-time analytics platform - materialized views, pre-aggregation, OLAP on streaming, ClickHouse'),
    ('reverse-etl-platform', 'Reverse ETL platform - Census, Hightouch, data activation, sync orchestration, audience building'),
    ('data-mesh-advanced', 'Data mesh advanced - domain ownership, self-serve infrastructure, federated governance, data ports'),
    ('ml-feature-platform', 'ML feature platform - feature store design, point-in-time joins, feature versioning, online/offline parity'),
    ('observability-platform-advanced', 'Observability platform advanced - correlation, AIOps, noise reduction, unified telemetry, context'),
    ('data-catalog-advanced', 'Data catalog advanced - automated discovery, lineage, usage analytics, data quality integration'),
    ('streaming-ml-inference', 'Streaming ML inference - online learning, model updates, feature serving, real-time scoring'),
    # API design and management advanced
    ('api-gateway-platform', 'API gateway platform - Kong, Apigee, AWS API Gateway, rate limiting, auth, transform, analytics'),
    ('api-product-management', 'API product management - developer experience, onboarding, docs, monetization, analytics, SDKs'),
    ('api-security-program', 'API security program - OWASP API Top 10, threat modeling, fuzzing, MTLS, rate limiting, BOLA'),
    ('graphql-platform-advanced', 'GraphQL platform advanced - persisted queries, query depth, batching, dataloader, schema stitching'),
    ('event-catalog-platform', 'Event catalog platform - AsyncAPI management, schema evolution, consumer contracts, documentation'),
    ('api-observability-advanced', 'API observability advanced - distributed tracing, API analytics, error budgets, traffic analysis'),
    ('api-testing-platform', 'API testing platform - contract testing, fuzzing, performance testing, security testing automation'),
    ('api-marketplace', 'API marketplace - discovery, monetization, developer portal, usage analytics, billing, SLA management'),
    ('backend-for-frontend-advanced', 'BFF advanced - aggregation layer, mobile/web differences, GraphQL BFF, API composition'),
    ('hypermedia-rest-advanced', 'Hypermedia REST advanced - HATEOAS, HAL, JSON-LD, Siren, collection+JSON, problem+JSON'),
    # Developer experience and tooling
    ('internal-developer-platform-advanced', 'IDP advanced - golden paths, self-service, Backstage plugins, scaffolding, environment provisioning'),
    ('developer-productivity-platform', 'Developer productivity platform - DORA metrics, Space framework, cognitive load, flow metrics'),
    ('local-development-advanced', 'Local development advanced - Tilt, Skaffold, dev containers, Telepresence, local Kubernetes'),
    ('gitops-platform-advanced', 'GitOps platform advanced - multi-cluster, progressive delivery, policy as code, drift detection'),
    ('testing-platform-advanced', 'Testing platform advanced - test intelligence, flake detection, impact analysis, parallelization'),
    ('ci-cd-advanced-platform', 'CI/CD advanced platform - build caching, incremental builds, pipeline as code, artifact management'),
    ('code-intelligence-platform', 'Code intelligence platform - semantic code search, code graph, impact analysis, refactoring at scale'),
    ('engineering-metrics-advanced', 'Engineering metrics advanced - DORA, SPACE, cycle time, deployment frequency, change failure rate'),
    ('feature-flag-platform', 'Feature flag platform - gradual rollouts, targeting rules, experimentation, kill switches, audit log'),
    ('developer-portal-platform', 'Developer portal platform - API catalog, service catalog, documentation, onboarding, search'),
    # Cloud-native advanced patterns
    ('service-mesh-platform', 'Service mesh platform - Istio advanced, Cilium service mesh, L7 policies, observability, mTLS'),
    ('kubernetes-platform-engineering', 'Kubernetes platform engineering - multi-tenancy, cost allocation, security policies, autoscaling'),
    ('cloud-cost-engineering', 'Cloud cost engineering - FinOps practices, commitment planning, waste reduction, unit economics'),
    ('platform-reliability-engineering', 'Platform reliability engineering - SLO tracking, toil reduction, automation, chaos engineering'),
    ('container-platform-advanced', 'Container platform advanced - OCI, BuildKit, multi-arch, registry proxying, vulnerability scanning'),
    ('edge-cloud-architecture', 'Edge cloud architecture - CDN integration, edge functions, geo-routing, latency optimization'),
    ('multi-cloud-workload-portability', 'Multi-cloud workload portability - CNCF standards, abstraction layers, vendor lock-in avoidance'),
    ('infrastructure-as-code-advanced', 'IaC advanced - module design, testing, drift detection, policy, cost estimation, Crossplane'),
    ('cloud-native-data-platform', 'Cloud-native data platform - managed services, serverless analytics, data warehouse modernization'),
    ('serverless-advanced-patterns', 'Serverless advanced patterns - cold start optimization, fan-out/fan-in, saga, workflow, durable'),
    # Web3 and blockchain advanced
    ('smart-contract-security-advanced', 'Smart contract security advanced - reentrancy, integer overflow, access control, formal verification'),
    ('defi-protocol-design', 'DeFi protocol design - tokenomics, liquidity mechanisms, governance, MEV protection, risk management'),
    ('blockchain-infrastructure', 'Blockchain infrastructure - node operation, RPC providers, indexing, event streaming, data availability'),
    ('nft-marketplace-platform', 'NFT marketplace platform - ERC721/1155, royalties, lazy minting, aggregation, trait rarity'),
    ('dao-infrastructure', 'DAO infrastructure - governance contracts, voting mechanisms, treasury management, snapshot, Tally'),
    ('layer2-advanced', 'Layer2 advanced - optimistic rollups, ZK rollups, validity proofs, sequencer, data availability'),
    ('cross-chain-protocols', 'Cross-chain protocols - bridges, atomic swaps, LayerZero, Axelar, IBC, message passing'),
    ('blockchain-analytics', 'Blockchain analytics - on-chain data, graph protocol, Dune Analytics, wallet profiling, MEV analysis'),
    ('web3-identity-advanced', 'Web3 identity advanced - DID, SIWE, ENS, soul-bound tokens, verifiable credentials, reputation'),
    ('tokenization-platform', 'Tokenization platform - RWA tokenization, security tokens, regulatory compliance, custody, transfer agents'),
    # Advanced testing and quality
    ('quality-engineering-platform', 'Quality engineering platform - shift-left, test orchestration, quality gates, reporting, trend analysis'),
    ('performance-engineering-advanced', 'Performance engineering advanced - load modeling, realistic traffic, regression detection, baselines'),
    ('security-testing-automation', 'Security testing automation - DAST integration, SAST tuning, dependency scanning, secret detection'),
    ('observability-driven-testing', 'Observability-driven testing - testing in production, canary analysis, feature flag testing, chaos'),
    ('test-data-factory', 'Test data factory - synthetic data generation, masking, subsetting, provisioning, lifecycle management'),
    ('accessibility-testing-advanced', 'Accessibility testing advanced - automated WCAG, screen reader testing, keyboard navigation, color'),
    ('contract-testing-advanced', 'Contract testing advanced - Pact broker, CDC patterns, schema evolution, consumer-driven'),
    ('visual-regression-testing', 'Visual regression testing - pixel comparison, component testing, cross-browser, Percy, Chromatic'),
    ('mutation-testing-advanced', 'Mutation testing advanced - PITest, Stryker, selective mutation, mutation score, CI integration'),
    ('fuzz-testing-platform', 'Fuzz testing platform - corpus management, coverage tracking, crash triage, security fuzzing CI'),
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
