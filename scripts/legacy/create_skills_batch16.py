
import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # More AI infrastructure and tools
    ('ai-inference-optimization', 'AI inference optimization - batching, quantization, caching, speculative decoding, throughput'),
    ('model-fine-tuning-pipeline', 'Model fine-tuning pipeline - data prep, SFT, evaluation, deployment, versioning'),
    ('rag-evaluation', 'RAG evaluation - context recall, faithfulness, answer relevance, RAGAS, DeepEval'),
    ('llm-cost-optimization', 'LLM cost optimization - prompt caching, smaller models, batching, compression, monitoring'),
    ('ai-application-security', 'AI application security - prompt injection, data poisoning, model theft, output sanitization'),
    ('token-counting', 'Token counting - tiktoken, Claude tokenizer, cost estimation, context management, batching'),
    # More JavaScript/TypeScript tools
    ('vitest-advanced', 'Vitest advanced - workspace, browser mode, coverage, mocking, snapshot, UI reporter'),
    ('testing-library-advanced', 'Testing Library advanced - custom queries, render patterns, event simulation, accessibility'),
    ('storybook-7-advanced', 'Storybook 7+ - interaction testing, test runner, a11y addon, docs, autodocs'),
    ('turbo-repo-advanced', 'Turborepo advanced - remote caching, task pipeline, prune, workspace config, linking'),
    ('changesets-advanced', 'Changesets advanced - major/minor/patch, pre-releases, snapshot releases, GitHub Actions'),
    # More Python data and ML tools
    ('polars-streaming', 'Polars streaming - lazy evaluation, out-of-core processing, chunking, parallel IO'),
    ('dask-ml', 'Dask ML - parallel training, model selection, preprocessing, joblib backend, cluster'),
    ('ray-advanced', 'Ray advanced - remote functions, actors, object store, scheduling, named actors, runtime env'),
    ('prefect-advanced', 'Prefect advanced - flows, tasks, deployments, workers, agents, automations, events'),
    ('airflow-advanced', 'Airflow advanced - dynamic tasks, task groups, custom operators, plugins, testing, scaling'),
    # More database tools
    ('pgvector-advanced', 'pgvector advanced - indexing strategies, HNSW, IVF, halfvec, distance operators, tuning'),
    ('redis-streams', 'Redis Streams - consumer groups, XADD, XREAD, XACK, message processing patterns'),
    ('mongodb-atlas-advanced', 'MongoDB Atlas advanced - Atlas Search, Online Archive, Data Federation, App Services'),
    ('cassandra-advanced', 'Cassandra advanced - data modeling, compaction, consistency levels, repair, performance'),
    ('neo4j-advanced', 'Neo4j advanced - Cypher optimization, APOC procedures, GDS algorithms, causal clustering'),
    # More security tools
    ('vault-enterprise', 'HashiCorp Vault Enterprise - namespaces, DR replication, HSM, Sentinel policies, PKI'),
    ('boundary-advanced', 'Boundary access management - targets, workers, credentials, sessions, OIDC, recording'),
    ('consul-advanced', 'Consul advanced - service mesh, intentions, ACL, snapshot, federation, network segments'),
    ('nomad-advanced', 'Nomad advanced - job specs, drivers, variables, ACL, federation, resource quotas'),
    ('packer-advanced', 'Packer advanced - builders, provisioners, post-processors, HCL2, AWS/GCP/Azure images'),
    # More testing and quality tools
    ('cypress-component', 'Cypress component testing - mount, stub, spy, network interception, visual regression'),
    ('playwright-components', 'Playwright component testing - React, Vue, Svelte, experimental, mount, locators'),
    ('k6-browser', 'k6 browser testing - Chromium, page interactions, screenshots, web vitals, hybrid testing'),
    ('artillery-advanced', 'Artillery advanced - plugins, HTTP/WS/gRPC, scenarios, phases, metrics, cloud'),
    ('gatling-advanced', 'Gatling advanced - simulations, scenarios, feeders, checks, assertions, reports'),
    # More DevOps automation
    ('argocd-advanced', 'Argo CD advanced - app of apps, multi-tenancy, RBAC, sync waves, resource hooks'),
    ('flux-gitops', 'Flux GitOps advanced - image automation, helm releases, OCI registries, cross-namespace'),
    ('spinnaker-deploy', 'Spinnaker - CD platform, pipelines, stages, bake, deploy, approval, rollback'),
    ('jenkins-x', 'Jenkins X - cloud-native CI/CD, preview environments, GitOps, quickstarts, tekton'),
    ('harness-cicd', 'Harness CI/CD - pipelines, stages, connectors, feature flags, chaos engineering, RBAC'),
    # More monitoring and alerting
    ('pagerduty-advanced', 'PagerDuty advanced - escalation policies, schedules, services, event orchestration, AIOps'),
    ('opsgenie-advanced', 'OpsGenie advanced - alert policies, on-call, heartbeats, integrations, reporting'),
    ('statuspage-advanced', 'Statuspage advanced - components, incidents, templates, subscribers, API, automation'),
    ('uptime-monitoring', 'Uptime monitoring - Uptime Kuma, Freshping, Better Uptime, status pages, alerting'),
    ('apm-patterns', 'APM patterns - transaction traces, error grouping, performance baselines, alerting, dashboards'),
    # More developer productivity
    ('github-advanced', 'GitHub advanced - Actions marketplace, Packages, Codespaces, advanced search, security'),
    ('gitlab-advanced', 'GitLab advanced - CI/CD, security scanning, container registry, merge trains, auto DevOps'),
    ('bitbucket-advanced', 'Bitbucket advanced - pipelines, Jira integration, code insights, pull request reviews'),
    ('gitea-self-hosted', 'Gitea self-hosted - repos, CI, package registry, webhooks, OAuth, federation'),
    ('forgejo-platform', 'Forgejo - GitHub alternative, git forge, CI, packages, self-hosted, federation'),
    # More edge and serverless
    ('serverless-framework', 'Serverless Framework - functions, events, plugins, offline, multi-cloud, deployment'),
    ('sst-framework', 'SST framework - full-stack serverless, Live Lambda, TypeScript, CDK constructs, console'),
    ('architect-framework', 'Architect framework - AWS Lambda, API Gateway, DynamoDB, S3, SQS, infrastructure'),
    ('nitric-framework', 'Nitric framework - cloud-agnostic, resources, APIs, storage, topics, queues'),
    ('shuttle-rs', 'Shuttle.rs - Rust cloud deployment, infrastructure from code, runtime, annotations'),
    # More data formats and tools
    ('markdown-processing', 'Markdown processing - unified, remark, rehype, MDX, syntax highlighting, plugins'),
    ('email-rendering', 'Email rendering - React Email, MJML, HTML email, dark mode, client compatibility'),
    ('pdf-generation', 'PDF generation - Puppeteer, Playwright, PDFKit, wkhtmltopdf, pdfmake, React-PDF'),
    ('csv-processing', 'CSV processing - Papa Parse, fast-csv, streams, validation, transformation, encoding'),
    ('excel-processing', 'Excel processing - ExcelJS, SheetJS, xlsx, read/write, formulas, styling, streaming'),
    # More AI research and techniques
    ('lora-advanced', 'LoRA advanced - rank selection, alpha, target modules, merged LoRA, LoRA+, DoRA'),
    ('qlora-technique', 'QLoRA technique - 4-bit quantization, NF4, double quantization, memory efficiency'),
    ('dpo-training', 'DPO training - Direct Preference Optimization, reference model, beta, data format, evaluation'),
    ('orpo-training', 'ORPO training - Odds Ratio Preference Optimization, combined SFT+preference, efficiency'),
    ('grpo-technique', 'GRPO technique - Group Relative Policy Optimization, reward models, math reasoning'),
    # More platforms and tools
    ('railway-advanced', 'Railway advanced - services, environments, volumes, networking, cron, deployments'),
    ('render-advanced', 'Render advanced - deploy hooks, environment groups, preview deploys, private services'),
    ('koyeb-platform', 'Koyeb - serverless PaaS, Docker, Git deploy, auto-scaling, global edge, free tier'),
    ('northflank-platform', 'Northflank - PaaS, pipelines, GitOps, preview environments, templates, workloads'),
    ('zeabur-platform', 'Zeabur - one-click deploy, templates, persistent storage, domains, webhooks, billing'),
    # More enterprise patterns
    ('multi-tenancy-advanced', 'Multi-tenancy advanced - tenant isolation, data partitioning, customization, billing'),
    ('white-label-saas', 'White-label SaaS - custom branding, domain mapping, feature toggles, reseller portal'),
    ('audit-logging-advanced', 'Audit logging advanced - immutable logs, compliance trails, search, retention, export'),
    ('data-classification', 'Data classification - tagging, sensitivity levels, access controls, DLP, automated scanning'),
    ('identity-governance', 'Identity governance - access reviews, entitlement management, provisioning, certification'),
    # More specific AI use cases
    ('code-review-automation', 'Code review automation - static analysis, AI review, comment generation, fix suggestions'),
    ('document-processing', 'Document processing pipeline - OCR, extraction, classification, routing, validation'),
    ('meeting-intelligence', 'Meeting intelligence - transcription, summarization, action items, CRM integration'),
    ('support-ai', 'AI customer support - ticket classification, response generation, escalation, knowledge base'),
    ('sales-intelligence-ai', 'Sales intelligence AI - lead scoring, intent signals, call analysis, next best action'),
    # More specialized programming
    ('concurrent-programming', 'Concurrent programming - threads, async, channels, actors, CSP, lock-free, STM'),
    ('distributed-systems-design', 'Distributed systems design - CAP theorem, consensus, CRDT, gossip, partition handling'),
    ('network-programming', 'Network programming - sockets, TCP/UDP, HTTP parsing, proxies, load balancers'),
    ('parser-development', 'Parser development - recursive descent, PEG, operator precedence, error recovery'),
    ('runtime-development', 'Runtime development - garbage collection, JIT compilation, sandboxing, eval, FFI'),
    # More hardware and systems
    ('arm-assembly', 'ARM assembly - AArch64, registers, instructions, NEON SIMD, calling conventions, inline'),
    ('x86-assembly', 'x86-64 assembly - registers, instructions, AVX, calling conventions, optimization, inline'),
    ('risc-v-development', 'RISC-V development - ISA, extensions, embedded, Linux, toolchain, QEMU emulation'),
    ('fpga-development', 'FPGA development - Verilog, VHDL, synthesis, timing, Vivado, Quartus, HLS'),
    ('embedded-linux', 'Embedded Linux - Yocto, Buildroot, device tree, kernel config, initramfs, BSP'),
    # More open source tools
    ('gitops-tools', 'GitOps tooling comparison - Argo CD vs Flux, push vs pull, tooling selection, migration'),
    ('cncf-landscape', 'CNCF landscape navigation - graduated projects, incubating, sandboxed, selection criteria'),
    ('open-source-governance', 'Open source governance - licensing, CLAs, DCO, contribution guides, community'),
    ('innersource-patterns', 'InnerSource patterns - trusted committers, contribution agreements, discovery, portals'),
    ('oss-security-practices', 'OSS security practices - SLSA framework, supply chain, signed releases, CVE management'),
    # More content and creative tools
    ('generative-art-ai', 'Generative art with AI - ComfyUI workflows, ControlNet, img2img, upscaling, consistency'),
    ('ai-video-pipeline', 'AI video pipeline - generation, editing, consistency, style transfer, audio sync'),
    ('audio-processing-ai', 'AI audio processing - speech enhancement, music separation, synthesis, analysis'),
    ('3d-generation-ai', 'AI 3D generation - Point-E, Shap-E, Zero123, text-to-3D, mesh optimization'),
    ('synthetic-media', 'Synthetic media - deepfakes, face swap ethics, detection, watermarking, provenance'),
    # More business tools
    ('crm-automation', 'CRM automation - Salesforce flows, HubSpot sequences, Dynamics plugins, triggers'),
    ('billing-automation', 'Billing automation - invoice generation, dunning, credit notes, tax calculation, ERP sync'),
    ('procurement-automation', 'Procurement automation - PO generation, vendor onboarding, approval workflows, spend'),
    ('hr-automation', 'HR automation - HRIS integrations, onboarding, offboarding, benefits, payroll integration'),
    ('legal-automation', 'Legal automation - contract generation, redlining, e-signature, matter management'),
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
