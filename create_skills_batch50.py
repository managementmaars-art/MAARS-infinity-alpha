
import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # Advanced security techniques
    ('kernel-exploits', 'Kernel exploit techniques - UAF, heap spray, ROP chains, SMEP/SMAP bypass, sandbox escape'),
    ('browser-exploitation', 'Browser exploitation - V8 internals, JIT exploitation, sandbox escape, CVE analysis'),
    ('firmware-analysis-advanced', 'Firmware analysis advanced - QEMU emulation, binwalk, ghidra scripting, CVE research'),
    ('iot-penetration-testing', 'IoT penetration testing - UART, JTAG, I2C, SPI, firmware extraction, radio analysis'),
    ('hardware-hacking', 'Hardware hacking - side-channel attacks, fault injection, power analysis, EM analysis'),
    ('cloud-security-research', 'Cloud security research - IAM privilege escalation, metadata service attacks, SSRF chains'),
    ('active-directory-attacks', 'Active Directory attacks - Kerberoasting, AS-REP roasting, DCSync, Golden Ticket, BloodHound'),
    ('offensive-c2-development', 'Offensive C2 development - custom implants, evasion, staging, encryption, protocol design'),
    ('malware-reverse-engineering', 'Malware reverse engineering - static/dynamic analysis, anti-evasion, IOC extraction'),
    ('binary-exploitation-advanced', 'Binary exploitation advanced - ASLR bypass, heap grooming, format strings, one-gadgets'),
    ('web-cache-poisoning', 'Web cache poisoning - cache keys, Vary header, unkeyed inputs, CDN attacks, DoS'),
    ('oauth-attacks', 'OAuth attacks - implicit flow, CSRF, open redirect, token leakage, mismatch attacks'),
    ('graphql-security-advanced', 'GraphQL security advanced - introspection abuse, batching attacks, field suggestion, DoS'),
    ('kubernetes-security-advanced', 'Kubernetes security advanced - privilege escalation, pod escape, RBAC abuse, etcd attacks'),
    ('devsecops-toolchain', 'DevSecOps toolchain - SAST, DAST, SCA, secrets, IaC scanning, policy gates, ASPM'),
    ('threat-intelligence-advanced', 'Threat intelligence advanced - TTP analysis, diamond model, MITRE ATT&CK, STIX/TAXII'),
    ('dfir-advanced', 'DFIR advanced - memory forensics, timeline analysis, log correlation, artifact collection'),
    ('malware-development-defense', 'Malware development for defense - understanding evasion, AV bypass research, detection'),
    ('purple-team-operations', 'Purple team operations - adversary simulation, detection validation, control testing'),
    ('appsec-architecture', 'AppSec architecture - threat modeling at scale, security champions, paved roads, guardrails'),
    # DevOps and platform engineering advanced
    ('platform-engineering-advanced', 'Platform engineering advanced - IDP design, golden paths, developer portals, metrics'),
    ('developer-productivity-metrics', 'Developer productivity metrics - DORA, SPACE, DevEx, deployment frequency, lead time'),
    ('engineering-effectiveness', 'Engineering effectiveness - toil reduction, cognitive load, workflow optimization, automation'),
    ('feature-flags-advanced-platform', 'Feature flags advanced platform - LaunchDarkly, Unleash, A/B testing, targeting, SDK'),
    ('progressive-delivery-advanced', 'Progressive delivery advanced - canary automation, traffic shaping, rollback triggers'),
    ('gitops-multi-tenant', 'GitOps multi-tenant - namespace isolation, RBAC, tenant onboarding, cost attribution'),
    ('policy-as-code-advanced', 'Policy as code advanced - Rego OPA, Kyverno policies, Conftest, CEL, admission control'),
    ('infrastructure-testing-advanced', 'Infrastructure testing advanced - Terratest, InSpec, LocalStack, kitchen-terraform'),
    ('chaos-gameday', 'Chaos gameday - game day planning, blast radius, hypothesis, readiness checks, observations'),
    ('sre-book-practices', 'SRE book practices - error budgets, SLO-based alerting, toil elimination, oncall rotation'),
    # Business intelligence and analytics
    ('dbt-advanced-patterns', 'dbt advanced patterns - incremental models, snapshots, generic tests, macros, packages'),
    ('looker-lkml-advanced', 'Looker LookML advanced - explores, joins, derived tables, liquid, PDTs, BigQuery DTs'),
    ('tableau-advanced', 'Tableau advanced - LOD expressions, table calcs, spatial analysis, extensions, Hyper API'),
    ('power-bi-advanced', 'Power BI advanced - composite models, aggregations, incremental refresh, RLS, deployment'),
    ('metabase-advanced', 'Metabase advanced - custom questions, native queries, sandboxing, embedding, REST API'),
    ('apache-superset-advanced', 'Apache Superset advanced - custom visualizations, Jinja2 templates, cache, security'),
    ('grafana-advanced-dashboards', 'Grafana advanced dashboards - variables, transformations, annotations, alerting, Scenes'),
    ('redash-analytics', 'Redash analytics - queries, visualizations, dashboards, parameters, scheduled refresh, API'),
    ('sisense-advanced', 'Sisense advanced - Elasticube, BloX, custom widgets, R/Python integration, embedding'),
    ('thoughtspot-analytics', 'ThoughtSpot analytics - SpotIQ, search analytics, liveboards, embedding, REST API v2'),
    # Emerging technology domains
    ('spatial-computing-advanced', 'Spatial computing advanced - Vision Pro, HoloLens, MR, hand tracking, scene understanding'),
    ('brain-computer-interface', 'Brain-computer interface tech - EEG, signal processing, BCI APIs, neurofeedback, SSVEP'),
    ('digital-biology-platform', 'Digital biology platforms - Benchling, LabKey, electronic lab notebooks, LIMS integration'),
    ('longevity-tech', 'Longevity technology - biomarkers, epigenetic clocks, interventions, aging research platforms'),
    ('femtech-platform', 'FemTech platform - reproductive health, cycle tracking, menopause, fertility analytics, privacy'),
    ('mental-health-ai-platform', 'Mental health AI platform - CBT chatbots, mood tracking, crisis detection, safety protocols'),
    ('edtech-ai-platform', 'EdTech AI platform - adaptive learning, AI tutoring, knowledge tracing, curriculum design'),
    ('legaltech-ai-platform', 'LegalTech AI platform - document review, contract analysis, legal research, e-billing'),
    ('proptech-ai-platform', 'PropTech AI platform - AVM, smart search, virtual tours, lease management, predictive'),
    ('climate-tech-platform', 'Climate tech platform - carbon accounting, MRV, emissions analytics, nature-based solutions'),
    ('food-tech-platform', 'Food tech platform - recipe intelligence, nutrition AI, supply chain traceability, labeling'),
    ('mobility-tech-platform', 'Mobility tech platform - GTFS, transit routing, shared mobility APIs, MaaS integration'),
    ('gig-economy-platform', 'Gig economy platform - worker matching, dynamic pricing, payments, compliance, ratings'),
    ('creator-economy-platform', 'Creator economy platform - monetization, subscriptions, tipping, analytics, fan engagement'),
    ('govtech-platform-advanced', 'GovTech platform advanced - digital identity, benefit delivery, permitting, open data'),
    ('edgeai-platform', 'Edge AI platform - model deployment, OTA updates, inference engines, hardware abstraction'),
    ('autonomy-platform', 'Autonomy platform - sensor fusion, HD maps, simulation, safety validation, fleet management'),
    ('robotics-platform-advanced', 'Robotics platform advanced - ROS2, simulation, motion planning, perception, manipulation'),
    ('quantum-software-platform', 'Quantum software platform - circuit compilation, quantum error correction, hybrid algorithms'),
    ('synthetic-biology-platform', 'Synthetic biology platform - DNA design, genetic circuit modeling, lab automation, LIMS'),
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
