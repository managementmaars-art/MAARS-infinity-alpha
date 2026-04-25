
import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # Identity and access management deep
    ('iam-zero-trust-architecture', 'IAM zero trust architecture - SPIFFE, SPIRE, workload identity, mTLS, SVID, mesh auth'),
    ('privileged-access-workstations', 'Privileged access workstations - PAW design, jump hosts, bastion hardening, session recording'),
    ('identity-threat-detection', 'Identity threat detection - anomalous login, credential stuffing detection, UEBA, impossible travel'),
    ('access-certification-advanced', 'Access certification advanced - periodic review automation, orphan accounts, SoD enforcement'),
    ('directory-services-advanced', 'Directory services advanced - AD schema, LDAP optimization, cross-forest trusts, Azure AD DS'),
    ('pki-certificate-lifecycle', 'PKI certificate lifecycle management - ACME protocol, EJBCA, Vault PKI, auto-rotation, revocation'),
    ('federated-identity-advanced', 'Federated identity advanced - SAML 2.0 deep, OAuth device flow, CIBA, BFF pattern'),
    ('customer-iam-advanced', 'Customer IAM advanced - Auth0 Actions, Cognito Lambdas, self-registration, MFA enrollment'),
    ('service-account-governance', 'Service account governance - non-human identities, workload identity federation, lifecycle mgmt'),
    ('identity-data-fabric', 'Identity data fabric - identity graph, unified identity store, correlation, deduplication, MDM'),
    # Security operations deep
    ('threat-intelligence-platform', 'Threat intelligence platform - MISP, OpenCTI, STIX/TAXII, enrichment, hunting workflows'),
    ('deception-technology-advanced', 'Deception technology advanced - honeypots, honeytokens, canary tokens, breadcrumbs, canarytrap'),
    ('incident-response-orchestration', 'Incident response orchestration - SOAR playbooks, automated triage, evidence collection, IR SLA'),
    ('vulnerability-management-program', 'Vulnerability management program - CVSS prioritization, SLA tracking, patch orchestration, risk score'),
    ('penetration-testing-methodology', 'Penetration testing methodology - scoping, recon, exploitation, post-exploitation, reporting'),
    ('red-team-purple-team', 'Red team/purple team - TIBER-EU, CREST, adversary simulation, MITRE ATT&CK mapping'),
    ('security-champions-program', 'Security champions program - training, secure coding, threat modeling facilitation, metrics'),
    ('cloud-security-posture-management', 'CSPM advanced - Prisma Cloud, Wiz, misconfiguration detection, compliance drift, remediation'),
    ('application-security-testing', 'Application security testing - SAST, DAST, IAST, SCA, secret scanning, pipeline integration'),
    ('security-data-lake', 'Security data lake - Athena for security, Snowflake security analytics, OpenSearch Security, UEBA'),
    # GRC and compliance technology
    ('grc-platform-advanced', 'GRC platform advanced - Archer, ServiceNow GRC, MetricStream, risk registry, control mapping'),
    ('iso27001-program-management', 'ISO 27001 program management - ISMS scope, risk assessment, controls, certification audit'),
    ('soc2-automation', 'SOC 2 automation - Vanta, Drata, Secureframe, evidence collection, continuous control monitoring'),
    ('privacy-program-management', 'Privacy program management - GDPR accountability, DPIA automation, consent management, DSR workflow'),
    ('third-party-risk-management', 'Third-party risk management - vendor assessment automation, questionnaire, tiering, continuous monitoring'),
    ('policy-management-platform', 'Policy management platform - policy lifecycle, acknowledgment tracking, version control, distribution'),
    ('regulatory-change-management', 'Regulatory change management - horizon scanning, impact assessment, obligation tracking'),
    ('business-continuity-planning-tech', 'Business continuity planning tech - BIA automation, RTO/RPO tracking, exercise management, DR orchestration'),
    ('audit-management-platform', 'Audit management platform - audit planning, fieldwork, findings, ISACA standards, CAB integration'),
    ('financial-risk-management-platform', 'Financial risk management platform - market risk, credit risk, operational risk, Basel III'),
    # Chaos and reliability engineering
    ('chaos-engineering-maturity', 'Chaos engineering maturity - GameDay design, hypothesis-driven, steady state, blast radius control'),
    ('resilience-engineering-advanced', 'Resilience engineering advanced - failure modes, degraded modes, load shedding, adaptive capacity'),
    ('reliability-testing-advanced', 'Reliability testing advanced - fault injection, network partitioning, latency injection, resource exhaustion'),
    ('sre-toil-automation', 'SRE toil automation - runbook automation, alert deduplication, auto-remediation, postmortem'),
    ('error-budget-advanced', 'Error budget advanced - multi-window SLOs, burn rate alerts, alerting policies, error budget policies'),
    ('capacity-forecasting', 'Capacity forecasting - growth modeling, seasonality, resource rightsizing, reservation planning'),
    ('distributed-system-debugging', 'Distributed system debugging - correlation IDs, causality tracking, timeline reconstruction, chaos replays'),
    ('production-excellence', 'Production excellence - change management, dark launches, feature flags, canary deployments, kill switches'),
    ('incident-learning-platform', 'Incident learning platform - blameless postmortems, learning review, action tracking, org learning'),
    ('on-call-platform-design', 'On-call platform design - escalation policies, alert routing, schedule management, cognitive load'),
    # Concurrent and parallel programming
    ('concurrency-models', 'Concurrency models - CSP, actors, STM, coroutines, cooperative vs preemptive, green threads'),
    ('parallel-algorithms-advanced', 'Parallel algorithms advanced - work-stealing, fork-join, MapReduce, parallel sorting, GPU kernels'),
    ('memory-model-advanced', 'Memory model advanced - acquire/release semantics, happens-before, DRF, C++ memory model, Java MM'),
    ('lock-free-programming-advanced', 'Lock-free programming advanced - compare-and-swap, ABA problem, hazard pointers, DCAS'),
    ('async-runtime-internals', 'Async runtime internals - event loop, poll model, wakers, executors, Tokio internals, async I/O'),
    ('data-parallelism', 'Data parallelism - SIMD programming, vectorization, OpenMP, AVX, Neon, data layout optimization'),
    ('task-parallelism-advanced', 'Task parallelism advanced - Cilk, TBB, Rayon, async tasks, continuation-stealing, work-first'),
    ('concurrent-testing', 'Concurrent testing - thread sanitizer, model checking, systematic testing, jcstress, Lincheck'),
    ('reactive-systems-advanced', 'Reactive systems advanced - backpressure, reactive streams, Project Reactor, RxJava, Akka Streams'),
    ('gpu-parallel-programming', 'GPU parallel programming - CUDA kernels, warp divergence, shared memory, atomic ops, thrust'),
    # Distributed systems algorithms
    ('consensus-protocols-advanced', 'Consensus protocols advanced - Multi-Paxos, Raft optimizations, EPaxos, Viewstamped Replication'),
    ('distributed-clock-algorithms', 'Distributed clock algorithms - Lamport clocks, vector clocks, hybrid logical clocks, TrueTime'),
    ('crdt-advanced-patterns', 'CRDT advanced patterns - Yjs internals, Automerge, RGA, LSEQ, fractional indexing, delta CRDTs'),
    ('gossip-protocol-advanced', 'Gossip protocol advanced - SWIM, Serf, membership, failure detection, infection-style dissemination'),
    ('distributed-snapshots', 'Distributed snapshots - Chandy-Lamport, consistent cuts, message logging, checkpointing protocols'),
    ('leader-election-advanced', 'Leader election advanced - bully algorithm, ZooKeeper ZAB, etcd Raft, leader leases, failover'),
    ('cap-theorem-practical', 'CAP theorem practical - partition handling strategies, PACELC, eventual consistency, convergence'),
    ('geo-distributed-databases', 'Geo-distributed databases - CockroachDB, Spanner, YugabyteDB, global tables, latency tradeoffs'),
    ('distributed-rate-limiting', 'Distributed rate limiting - token bucket across nodes, GCRA, Redis-based, Envoy rate limit service'),
    ('distributed-locking-advanced', 'Distributed locking advanced - Redlock, fencing tokens, lease-based, DLOCK, ZooKeeper locks'),
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
