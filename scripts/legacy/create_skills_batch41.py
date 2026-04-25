
import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # From alirezarezvani/claude-skills - engineering-team
    ('senior-qa', 'Senior QA - test strategy, quality gates, automation, coverage, risk-based testing, metrics'),
    ('senior-devops', 'Senior DevOps - platform engineering, CI/CD, SRE, infrastructure, observability, on-call'),
    ('senior-secops', 'Senior SecOps - security operations, SIEM, threat hunting, incident response, blue team'),
    ('senior-security', 'Senior Security - application security, pen testing, architecture review, compliance, zero trust'),
    ('senior-data-scientist', 'Senior Data Scientist - modeling, experimentation, storytelling, stakeholder management, MLOps'),
    ('senior-data-engineer', 'Senior Data Engineer - pipelines, lakehouse, streaming, modeling, orchestration, DataOps'),
    ('senior-ml-engineer', 'Senior ML Engineer - training, inference, optimization, deployment, monitoring, LLMOps'),
    ('senior-prompt-engineer', 'Senior Prompt Engineer - prompt design, evaluation, red teaming, structured output, RAG'),
    ('senior-computer-vision', 'Senior Computer Vision - detection, segmentation, tracking, 3D, edge deployment, datasets'),
    ('a11y-audit', 'Accessibility audit - WCAG 2.2, screen readers, keyboard navigation, color contrast, ARIA, remediation'),
    ('adversarial-reviewer', 'Adversarial reviewer - find flaws, challenge assumptions, red team reasoning, devil advocate'),
    ('ai-security', 'AI security - model attacks, prompt injection, data poisoning, model extraction, hardening'),
    ('email-template-builder', 'Email template builder - responsive HTML email, MJML, ESP compatibility, dark mode, testing'),
    ('epic-design', 'Epic design - user story mapping, acceptance criteria, technical breakdown, estimations, dependencies'),
    ('google-workspace-cli', 'Google Workspace CLI - gam, GAM CLI, domain management, user provisioning, audit, automation'),
    ('incident-commander', 'Incident commander - IC role, comms, timeline, escalation, war room, postmortem, coordination'),
    ('playwright-pro', 'Playwright pro - advanced selectors, parallel, trace viewer, component testing, visual diff'),
    ('security-pen-testing', 'Security pen testing - methodology, recon, exploitation, post-exploitation, reporting, CVSS'),
    ('tdd-guide', 'TDD guide - red-green-refactor, test doubles, coverage, design feedback, outside-in, BDD bridge'),
    ('tech-stack-evaluator', 'Tech stack evaluator - criteria, comparison, POC, risk assessment, migration cost, decision doc'),
    ('threat-detection', 'Threat detection - behavioral analytics, UEBA, anomaly detection, rules, tuning, false positives'),
    ('aws-solution-architect', 'AWS solution architect - Well-Architected, design patterns, cost, security, reliability, DR'),
    ('azure-cloud-architect', 'Azure cloud architect - landing zones, governance, networking, identity, monitoring, CAF'),
    ('gcp-cloud-architect', 'GCP cloud architect - organization, VPC, IAM, data platform, GKE, operations, cost'),
    ('ms365-tenant-manager', 'MS365 tenant manager - admin center, Exchange, Teams, SharePoint, compliance, licensing'),
    # From engineering (non-duplicates)
    ('agent-designer', 'Agent designer - multi-agent systems, tool design, memory, planning, orchestration patterns'),
    ('agent-workflow-designer', 'Agent workflow designer - workflow graphs, state machines, human-in-loop, error recovery'),
    ('agenthub', 'AgentHub - agent registry, versioning, deployment, discovery, composition, monitoring'),
    ('api-design-reviewer', 'API design reviewer - REST consistency, naming, versioning, pagination, errors, OpenAPI audit'),
    ('api-test-suite-builder', 'API test suite builder - contract tests, load tests, mock servers, test data, CI integration'),
    ('autoresearch-agent', 'Autoresearch agent - web research, source synthesis, citation, fact checking, structured output'),
    ('ci-cd-pipeline-builder', 'CI/CD pipeline builder - GitHub Actions/GitLab/Jenkins, stages, caching, security gates'),
    ('codebase-onboarding', 'Codebase onboarding - architecture tour, key patterns, gotchas, runbooks, dev setup guide'),
    ('database-designer', 'Database designer - schema design, normalization, indexing strategy, partitioning, migration'),
    ('database-schema-designer', 'Database schema designer - ERD, data types, constraints, relationships, versioning, docs'),
    ('dependency-auditor', 'Dependency auditor - CVE scanning, license compliance, outdated packages, transitive deps'),
    ('docker-development', 'Docker development - Dockerfile optimization, multi-stage, compose, networking, volumes, security'),
    ('env-secrets-manager', 'Env secrets manager - .env patterns, vault integration, rotation, injection, audit, CI secrets'),
    ('focused-fix', 'Focused fix - surgical bug fixes, minimal diffs, regression prevention, root cause analysis'),
    ('git-worktree-manager', 'Git worktree manager - multiple worktrees, branch strategy, parallel work, merging, cleanup'),
    ('helm-chart-builder', 'Helm chart builder - templates, values, hooks, library charts, testing, packaging, OCI'),
    ('interview-system-designer', 'Interview system designer - system design questions, evaluation rubric, follow-up, scoring'),
    ('llm-cost-optimizer', 'LLM cost optimizer - model selection, prompt compression, caching, batching, routing, monitoring'),
    ('mcp-server-builder', 'MCP server builder - tools, resources, prompts, auth, testing, deployment, Claude integration'),
    ('migration-architect', 'Migration architect - database migration, zero-downtime, rollback, dual-write, cutover planning'),
    ('monorepo-navigator', 'Monorepo navigator - workspace setup, dependency graph, affected builds, caching, ownership'),
    ('observability-designer', 'Observability designer - metrics, logs, traces, SLOs, dashboards, alerting strategy, OTel'),
    ('performance-profiler', 'Performance profiler - CPU, memory, I/O, latency, flamegraphs, bottleneck identification'),
    ('pr-review-expert', 'PR review expert - code quality, security, performance, maintainability, constructive feedback'),
    ('prompt-governance', 'Prompt governance - versioning, testing, approval workflow, rollback, A/B, documentation'),
    ('rag-architect', 'RAG architect - chunking, embedding, indexing, retrieval, reranking, evaluation, hybrid search'),
    ('release-manager', 'Release manager - versioning, changelog, tagging, deploy gates, rollback, comms, branching'),
    ('runbook-generator', 'Runbook generator - operational procedures, step-by-step, troubleshooting, escalation paths'),
    ('secrets-vault-manager', 'Secrets vault manager - HashiCorp Vault, AWS Secrets Manager, rotation, dynamic creds'),
    ('self-eval', 'Self evaluation - code self-review, quality checklist, assumption validation, edge cases, testing'),
    ('skill-security-auditor', 'Skill security auditor - SKILL.md review, prompt injection risk, trust boundaries, sandboxing'),
    ('skill-tester', 'Skill tester - skill evaluation, test cases, coverage, regression, benchmarking, scoring'),
    ('spec-driven-workflow', 'Spec-driven workflow - specification first, implementation tracing, acceptance criteria, sign-off'),
    ('sql-database-assistant', 'SQL database assistant - query writing, optimization, schema advice, index recommendation'),
    ('tech-debt-tracker', 'Tech debt tracker - inventory, prioritization, DORA metrics, refactoring plans, stakeholder comms'),
    # From marketing-skill (new ones)
    ('content-humanizer', 'Content humanizer - remove AI writing patterns, natural voice, vary sentence structure, tone'),
    ('content-production', 'Content production - briefs, drafts, editing, publishing workflow, repurposing, calendar'),
    ('marketing-demand-acquisition', 'Marketing demand acquisition - paid, organic, content, partnerships, attribution, funnel'),
    ('marketing-ops', 'Marketing operations - Martech stack, data quality, automation, attribution, reporting, tooling'),
    ('marketing-strategy-pmm', 'Marketing strategy PMM - positioning, GTM, messaging, sales enablement, competitive'),
    ('social-media-analyzer', 'Social media analyzer - engagement metrics, audience insights, competitor benchmarking'),
    ('social-media-manager', 'Social media manager - content calendar, scheduling, engagement, analytics, community'),
    ('video-content-strategist', 'Video content strategist - YouTube, TikTok, LinkedIn, scripts, hooks, SEO, thumbnails'),
    ('x-twitter-growth', 'X/Twitter growth - viral hooks, threads, engagement, audience building, analytics, strategy'),
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
