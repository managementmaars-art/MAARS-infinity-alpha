
import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # AI Safety and Ethics
    ('ai-safety-alignment', 'AI safety alignment - corrigibility, value alignment, robustness, interpretability, oversight'),
    ('ai-ethics-framework', 'AI ethics framework - fairness, accountability, transparency, explainability, bias mitigation'),
    ('responsible-ai-practices', 'Responsible AI practices - impact assessment, governance, documentation, model cards, auditing'),
    ('ai-bias-detection', 'AI bias detection - dataset bias, model bias, fairness metrics, mitigation strategies, monitoring'),
    ('explainable-ai', 'Explainable AI - SHAP, LIME, attention visualization, feature attribution, model cards'),
    ('ai-governance', 'AI governance - policy frameworks, risk management, compliance, EU AI Act, NIST AI RMF'),
    # Quantum Computing
    ('quantum-computing-basics', 'Quantum computing basics - qubits, gates, circuits, superposition, entanglement, measurement'),
    ('qiskit-framework', 'Qiskit - IBM quantum, circuits, algorithms, noise, simulation, transpilation, execution'),
    ('pennylane-framework', 'PennyLane - quantum ML, differentiable programming, devices, templates, optimization'),
    ('quantum-algorithms', 'Quantum algorithms - Grover, Shor, VQE, QAOA, quantum walks, error correction'),
    ('quantum-ml', 'Quantum machine learning - QNN, kernel methods, data encoding, barren plateaus, NISQ'),
    # Bioinformatics
    ('bioinformatics-pipeline', 'Bioinformatics pipeline - sequence alignment, variant calling, annotation, NGS workflows'),
    ('genomics-analysis', 'Genomics analysis - WGS, WES, RNA-seq, ChIP-seq, ATAC-seq, multi-omics integration'),
    ('biopython-toolkit', 'BioPython toolkit - sequence I/O, BLAST, entrez, phylogenetics, structure parsing'),
    ('snakemake-workflow', 'Snakemake - bioinformatics workflow management, rules, wildcards, conda, cluster execution'),
    ('galaxy-platform', 'Galaxy platform - web-based bioinformatics, tools, workflows, shared histories, training'),
    # Research and Academic Tools
    ('latex-advanced', 'LaTeX advanced - custom classes, TikZ, pgfplots, BibTeX, hyperref, cross-references'),
    ('jupyter-advanced', 'Jupyter advanced - widgets, extensions, voila, papermill, nbconvert, JupyterHub, kernels'),
    ('research-reproducibility', 'Research reproducibility - DVC, Git LFS, Docker, environment pinning, data versioning'),
    ('scientific-python', 'Scientific Python - NumPy advanced, SciPy, SymPy, mpmath, numerical methods, optimization'),
    ('data-visualization-advanced', 'Data visualization advanced - D3.js, Vega-Altair, Bokeh, HoloViews, datashader, panel'),
    # Accessibility and Internationalization
    ('wcag-compliance', 'WCAG compliance - perceivable, operable, understandable, robust, testing, remediation'),
    ('aria-implementation', 'ARIA implementation - roles, states, properties, landmarks, live regions, modal dialogs'),
    ('i18n-advanced', 'i18n advanced - ICU message format, plural rules, RTL, bidirectional text, locale data'),
    ('l10n-workflow', 'L10n workflow - translation management, TMS integration, pseudo-localization, QA automation'),
    ('a11y-engineering', 'Accessibility engineering - keyboard navigation, focus management, screen reader support, testing'),
    # Advanced Networking
    ('network-security-advanced', 'Network security advanced - firewall rules, IDS/IPS, network segmentation, DPI, honeypots'),
    ('vpn-implementation', 'VPN implementation - WireGuard, OpenVPN, IPsec, SSL VPN, split tunneling, MFA'),
    ('dns-advanced', 'DNS advanced - DNSSEC, DNS-over-HTTPS, split-horizon, custom resolvers, GeoDNS, anycast'),
    ('bgp-routing', 'BGP routing - autonomous systems, route policies, communities, anycast, peering, filtering'),
    ('sd-wan-architecture', 'SD-WAN architecture - underlay, overlay, policy-based routing, centralized management, security'),
    # Programming Paradigms
    ('category-theory-programming', 'Category theory for programmers - functors, monads, natural transformations, adjunctions'),
    ('type-theory-advanced', 'Type theory advanced - dependent types, linear types, session types, refinement types'),
    ('metaprogramming-advanced', 'Metaprogramming advanced - macros, code generation, reflection, template metaprogramming'),
    ('property-based-testing', 'Property-based testing - Hypothesis, QuickCheck, fast-check, generators, shrinking, stateful'),
    ('formal-methods', 'Formal methods - TLA+, Alloy, model checking, specification, verification, invariants'),
    # Data Mesh and Platform
    ('data-mesh-architecture', 'Data mesh - domain ownership, data products, self-serve platform, federated governance'),
    ('data-product-design', 'Data product design - discoverability, addressability, trustworthiness, self-description, interoperability'),
    ('data-platform-engineering', 'Data platform engineering - lakehouse, data catalog, data quality, orchestration, self-service'),
    ('analytical-engineering', 'Analytical engineering - dbt, semantic modeling, data contracts, testing, documentation'),
    ('data-observability', 'Data observability - freshness, volume, schema, lineage, distribution monitoring, alerting'),
    # Real-time Systems
    ('real-time-computing', 'Real-time computing - RTOS, latency guarantees, scheduling, interrupt handling, determinism'),
    ('stream-processing-advanced', 'Stream processing advanced - exactly-once semantics, state management, late data, reprocessing'),
    ('websocket-patterns', 'WebSocket patterns - connection management, rooms, broadcasts, heartbeats, reconnection, scaling'),
    ('server-sent-events', 'Server-sent events - SSE protocol, retry, event ID, connection management, proxy handling'),
    ('webrtc-advanced', 'WebRTC advanced - signaling, STUN/TURN, ICE, data channels, media streams, SFU/MCU'),
    # Observability Engineering
    ('opentelemetry-advanced', 'OpenTelemetry advanced - custom exporters, sampling, baggage, semantic conventions, collector'),
    ('tracing-advanced', 'Distributed tracing advanced - trace context, sampling strategies, root cause analysis, flamegraphs'),
    ('ebpf-observability', 'eBPF observability - kernel tracing, network monitoring, performance analysis, bcc, bpftrace'),
    ('continuous-profiling', 'Continuous profiling - Pyroscope, Parca, Grafana Pyroscope, flamegraphs, heap analysis'),
    ('observability-pipeline', 'Observability pipeline - Vector, Fluent Bit, Logstash, routing, filtering, sampling, enrichment'),
    # Platform Engineering Advanced
    ('idp-internal-platform', 'Internal developer platform - golden paths, self-service, templates, scaffolding, portal'),
    ('platform-as-product', 'Platform as product - developer experience, NPS, adoption metrics, feedback loops, roadmap'),
    ('paved-road-engineering', 'Paved road engineering - opinionated defaults, guardrails, escape hatches, adoption'),
    ('developer-portal-design', 'Developer portal design - catalog, docs, create, manage, explore, search, analytics'),
    ('cognitive-load-reduction', 'Cognitive load reduction - abstractions, automation, documentation, discovery, onboarding'),
    # Advanced Security Patterns
    ('threat-intelligence', 'Threat intelligence - IOCs, TTPs, MITRE ATT&CK, feeds, STIX/TAXII, threat hunting'),
    ('siem-advanced', 'SIEM advanced - log correlation, detection rules, SOAR integration, threat hunting, Sigma'),
    ('appsec-program', 'AppSec program - OWASP SAMM, security champions, threat modeling, training, metrics'),
    ('bug-bounty-program', 'Bug bounty program design - scope, rewards, triage, disclosure, platform selection'),
    ('security-architecture', 'Security architecture - defense in depth, least privilege, secure defaults, attack surface reduction'),
    # Emerging Platforms
    ('apple-vision-pro', 'Apple Vision Pro - visionOS, RealityKit, SwiftUI 3D, spatial computing, anchors, windows'),
    ('meta-quest-dev', 'Meta Quest development - Unity XR, WebXR, Passthrough, spatial audio, hand tracking'),
    ('spatial-computing', 'Spatial computing - AR/VR/MR, scene understanding, anchors, occlusion, physics, interaction'),
    ('wearable-dev', 'Wearable development - watchOS, Wear OS, sensors, health APIs, complications, glanceable UI'),
    ('automotive-software', 'Automotive software - AUTOSAR, ADAS, CAN bus, ISO 26262, functional safety, OTA updates'),
    # Advanced Cloud Patterns
    ('multi-cloud-strategy', 'Multi-cloud strategy - vendor lock-in avoidance, portability, cost optimization, governance'),
    ('cloud-migration-advanced', 'Cloud migration advanced - 7Rs, migration factory, wave planning, cutover, validation'),
    ('cloud-native-security', 'Cloud native security - CSPM, CWPP, CNAPP, workload protection, posture management'),
    ('serverless-patterns-advanced', 'Serverless patterns advanced - durable execution, saga, fan-out, event-driven, cold starts'),
    ('cloud-cost-governance', 'Cloud cost governance - tagging, showback, chargeback, budgets, anomaly detection, optimization'),
    # Advanced Data Engineering
    ('lakehouse-architecture', 'Lakehouse architecture - Delta, Iceberg, Hudi, table formats, catalog, compute separation'),
    ('streaming-analytics', 'Streaming analytics - real-time dashboards, materialized views, continuous queries, aggregation'),
    ('data-quality-engineering', 'Data quality engineering - Great Expectations, Soda, Monte Carlo, rules, monitoring, remediation'),
    ('data-lineage-advanced', 'Data lineage advanced - column-level lineage, impact analysis, OpenLineage, Marquez, Atlas'),
    ('reverse-etl-advanced', 'Reverse ETL advanced - Census, Hightouch, data activation, audience sync, event forwarding'),
    # Advanced API Patterns
    ('hypermedia-apis', 'Hypermedia APIs - HATEOAS, HAL, JSON:API, Siren, controls, affordances, discoverability'),
    ('event-driven-apis', 'Event-driven APIs - AsyncAPI, webhooks, SSE, WebSocket, CloudEvents, message brokers'),
    ('graphql-federation', 'GraphQL Federation - supergraph, subgraphs, Apollo Federation, Cosmo, schema composition'),
    ('api-versioning-strategies', 'API versioning strategies - URI, header, query param, deprecation, sunset headers, migration'),
    ('async-api-design', 'Async API design - AsyncAPI 3.0, channels, operations, messages, bindings, schema'),
    # Documentation and Knowledge
    ('docs-as-code', 'Docs-as-code - Git-based docs, CI/CD, linting, link checking, search, versioning, preview'),
    ('architecture-decision-records', 'Architecture decision records - ADR format, tooling, linking, superseding, reviewing'),
    ('technical-writing', 'Technical writing - structure, clarity, audience, APIs docs, tutorials, how-tos, reference'),
    ('knowledge-management', 'Knowledge management - second brain, Zettelkasten, evergreen notes, spaced repetition'),
    ('runbook-design', 'Runbook design - incident response, decision trees, automation links, validation, maintenance'),
    # Advanced Testing Patterns
    ('chaos-testing-advanced', 'Chaos testing advanced - ChaosMesh, Litmus, fault injection, blast radius, hypothesis'),
    ('fuzzing-advanced', 'Fuzzing advanced - coverage-guided, libfuzzer, AFL++, structured fuzzing, corpus, triage'),
    ('golden-path-testing', 'Golden path testing - happy path automation, regression suite, smoke tests, release validation'),
    ('shift-left-testing', 'Shift-left testing - developer testing culture, fast feedback, local testing, pre-commit quality'),
    ('test-observability', 'Test observability - flaky test detection, test analytics, coverage trends, failure patterns'),
    # Business Intelligence Advanced
    ('bi-platform-design', 'BI platform design - semantic layer, metrics store, self-service analytics, governance, caching'),
    ('data-storytelling', 'Data storytelling - narrative visualization, annotations, progressive disclosure, interactivity'),
    ('executive-dashboards', 'Executive dashboards - KPIs, scorecards, drill-down, alerting, mobile, embeddable'),
    ('metrics-framework', 'Metrics framework - AARRR, OKRs, north star metric, counter metrics, experimentation'),
    ('self-serve-analytics', 'Self-serve analytics - semantic layer, natural language, drill-down, ad-hoc, governed data'),
    # Regional Cloud Providers
    ('alibaba-cloud', 'Alibaba Cloud - ECS, OSS, RDS, MaxCompute, DataWorks, ACK, global expansion'),
    ('oracle-cloud', 'Oracle Cloud Infrastructure - compute, networking, database, autonomous DB, data lake, OKE'),
    ('ibm-cloud', 'IBM Cloud - watsonx, Cloud Pak, OpenShift, Db2, Event Streams, Functions, Secrets Manager'),
    ('huawei-cloud', 'Huawei Cloud - ECS, OBS, ModelArts, DLI, DWS, CCE, global regions'),
    ('tencent-cloud', 'Tencent Cloud - CVM, COS, TencentDB, TKE, SCF, API Gateway, global CDN'),
    # Advanced Deployment Patterns
    ('progressive-delivery', 'Progressive delivery - feature flags, canary, blue-green, traffic splitting, observability'),
    ('deployment-automation', 'Deployment automation - pipeline design, approval gates, rollback triggers, notifications'),
    ('environment-management', 'Environment management - ephemeral environments, environment parity, promotion workflows'),
    ('release-train', 'Release train - cadence, feature freeze, hardening, versioning, coordination, communication'),
    ('continuous-deployment', 'Continuous deployment - automated testing gates, deployment frequency, lead time, DORA metrics'),
    # Vertical AI Applications
    ('legal-ai', 'Legal AI - contract analysis, case research, due diligence, compliance checking, drafting'),
    ('financial-ai', 'Financial AI - risk assessment, fraud detection, algorithmic trading, portfolio optimization'),
    ('healthcare-ai', 'Healthcare AI - clinical decision support, medical imaging, patient risk, operational efficiency'),
    ('education-ai', 'Education AI - adaptive learning, assessment, content generation, tutoring, accessibility'),
    ('manufacturing-ai', 'Manufacturing AI - predictive maintenance, quality control, supply chain, robotics, scheduling'),
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
