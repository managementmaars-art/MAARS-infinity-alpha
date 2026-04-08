
import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # Energy and environment technology
    ('solar-energy-advanced', 'Solar energy advanced - PVsyst, bifacial modeling, string inverters, MPPT, grid-tied, BMS'),
    ('wind-energy-advanced', 'Wind energy advanced - turbine SCADA, wake modeling, OpenFAST, power curve, O&M analytics'),
    ('battery-management-systems', 'Battery management systems - SOC estimation, SOP, equalization, thermal management, BMS firmware'),
    ('grid-scale-storage', 'Grid scale storage - BESS, ancillary services, frequency regulation, virtual power plant'),
    ('energy-management-systems', 'Energy management systems - EMS, DERMS, microgrid control, demand response, VPP'),
    ('carbon-capture-tech', 'Carbon capture technology - DAC systems, CCS modeling, sorbent selection, techno-economic'),
    ('hydrogen-production', 'Hydrogen production - electrolyzer modeling, green H2, PEM, alkaline, techno-economic analysis'),
    ('building-energy-advanced', 'Building energy advanced - EnergyPlus, OpenStudio, calibration, demand flexibility, HVAC ML'),
    ('environmental-monitoring-advanced', 'Environmental monitoring advanced - IoT sensors, air quality, water quality, noise, AQI'),
    ('digital-twin-energy', 'Digital twin energy - grid modeling, DER integration, Gridlab-D, OpenDSS, simulation'),
    # Education technology deep
    ('adaptive-learning-advanced', 'Adaptive learning advanced - knowledge tracing, BKT, DKT, mastery-based progression'),
    ('learning-analytics-platform', 'Learning analytics platform - xAPI, Learning Record Store, dashboards, early warning'),
    ('educational-game-design', 'Educational game design - gamification, serious games, stealth assessment, narrative'),
    ('ai-tutoring-systems', 'AI tutoring systems - ITS architecture, hint generation, misconception detection, Socratic'),
    ('assessment-technology', 'Assessment technology - IRT, CAT, psychometrics, item banking, automated scoring'),
    ('stem-simulation-tools', 'STEM simulation tools - PhET, NetLogo, Scratch backends, visual programming, lab simulation'),
    ('mooc-platform-engineering', 'MOOC platform engineering - video delivery, discussion forums, peer assessment, certificates'),
    ('accessibility-education', 'Accessibility in education - screen readers, captioning, alt text, WCAG, universal design'),
    ('student-information-advanced', 'Student information systems advanced - SIS integrations, Powerschool, Canvas, Clever, Rostering'),
    ('research-data-management', 'Research data management - DMP, FAIR principles, institutional repositories, data citation'),
    # Developer tools and productivity deep
    ('code-search-advanced', 'Code search advanced - AST-based search, semantic code search, Sourcegraph, grep.app'),
    ('static-analysis-advanced', 'Static analysis advanced - dataflow, taint analysis, SMT solvers, abstract interpretation'),
    ('fuzzing-advanced', 'Fuzzing advanced - coverage-guided, AFL++, LibFuzzer, grammar-based, structure-aware'),
    ('symbolic-execution', 'Symbolic execution - KLEE, angr, path explosion, constraint solving, vulnerability discovery'),
    ('program-analysis-tools', 'Program analysis tools - sanitizers, ASan, TSan, UBSan, Valgrind, Helgrind, DRD'),
    ('code-refactoring-tools', 'Code refactoring tools - jscodeshift, ts-morph, Rope, Comby, LibCST, OpenRewrite'),
    ('documentation-automation', 'Documentation automation - autodoc, docstring generation, API documentation, changelog'),
    ('development-metrics', 'Development metrics - cycle time, code churn, complexity trends, PR size, review time'),
    ('pair-programming-advanced', 'Pair programming advanced - driver-navigator, mob programming, async pair, AI pair'),
    ('code-review-automation', 'Code review automation - static analysis gates, AI review, size limits, coverage gates'),
    # Emerging protocols and standards
    ('openapi-v31', 'OpenAPI 3.1 - JSON Schema alignment, webhooks, discriminators, overlays, Arazzo workflows'),
    ('asyncapi-advanced', 'AsyncAPI advanced - Kafka bindings, MQTT bindings, AMQP, WebSocket, message schemas'),
    ('grpc-ecosystem', 'gRPC ecosystem - Envoy proxy, gRPC-web, transcoding, reflection, health, server streaming'),
    ('graphql-federation-advanced', 'GraphQL federation advanced - Apollo Federation 2, subgraphs, directives, entity resolving'),
    ('event-driven-standards', 'Event-driven standards - CloudEvents, EventCatalog, Schema Registry, event governance'),
    ('opentelemetry-advanced', 'OpenTelemetry advanced - semantic conventions, SDK instrumentation, OTLP, Collector pipelines'),
    ('ebpf-advanced-programs', 'eBPF advanced programs - CO-RE, BTF, libbpf, BCC, bpftrace, kernel tracing, networking'),
    ('webassembly-components', 'WebAssembly Component Model - WIT, WASI, Wasmtime, composition, canonical ABI'),
    ('oauth-oidc-advanced', 'OAuth/OIDC advanced - PKCE, DPoP, PAR, RAR, CIBA, FedCM, device flow, mTLS'),
    ('zero-trust-implementation', 'Zero trust implementation - BeyondCorp, SPIFFE, identity proxy, microsegmentation, SASE'),
    # No-code/low-code platforms deep
    ('retool-advanced', 'Retool advanced - custom components, JS queries, workflows, Retool AI, embedding, REST API'),
    ('appsmith-advanced', 'Appsmith advanced - datasources, widgets, JS objects, git integration, workflows, embedding'),
    ('budibase-advanced', 'Budibase advanced - custom datasources, automations, RBAC, self-hosting, plugins, embed'),
    ('n8n-advanced', 'n8n advanced - custom nodes, community nodes, expressions, workflows, AI nodes, self-hosting'),
    ('make-advanced', 'Make (Integromat) advanced - routers, iterators, aggregators, custom webhooks, data stores'),
    ('power-platform-advanced', 'Power Platform advanced - PCF controls, connectors, dataverse APIs, ALM, governance'),
    ('airtable-scripting-advanced', 'Airtable scripting advanced - scripting block, automations, extensions, sync, API'),
    ('notion-api-advanced', 'Notion API advanced - databases, blocks, comments, authentication, webhooks, sync'),
    ('zapier-advanced', 'Zapier advanced - Paths, Code steps, Formatter, webhooks, Zapier Tables, Interfaces'),
    ('glide-apps', 'Glide apps advanced - computed columns, user-specific, actions, templates, publishing, teams'),
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
