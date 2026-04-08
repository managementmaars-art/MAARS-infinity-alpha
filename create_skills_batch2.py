
import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # Fintech/Financial skills
    ('plaid-integration', 'Plaid API integration - bank account linking, transactions, balances, identity verification'),
    ('alpaca-trading', 'Alpaca trading API - stock orders, portfolio management, market data, paper trading'),
    ('polygon-io', 'Polygon.io market data - stocks, options, forex, crypto, real-time and historical data'),
    ('financial-modeling', 'Financial modeling - DCF, LBO, three-statement models, valuation, scenario analysis'),
    ('tax-automation', 'Tax automation - tax calculation, reporting, compliance, API integrations for tax data'),
    ('accounting-api', 'Accounting API integration - QuickBooks, Xero, FreshBooks, chart of accounts, journals'),
    ('payment-reconciliation', 'Payment reconciliation - matching transactions, dispute resolution, ledger reconciliation'),
    ('fraud-detection', 'Fraud detection - transaction scoring, anomaly detection, rule engines, ML-based fraud'),
    ('kyc-aml', 'KYC/AML compliance - identity verification, PEP screening, sanctions checking, documentation'),
    ('options-pricing', 'Options pricing - Black-Scholes, Greeks, volatility surface, strategy payoff diagrams'),
    # Legal/compliance skills
    ('contract-analysis', 'Contract analysis - clause extraction, risk identification, obligation tracking, NLP review'),
    ('privacy-compliance', 'Privacy compliance - GDPR, CCPA, data mapping, DPA, consent management, privacy policy'),
    ('ip-analysis', 'IP analysis - patent search, trademark clearance, copyright review, IP portfolio assessment'),
    ('regulatory-compliance', 'Regulatory compliance - SOX, HIPAA, PCI-DSS, ISO 27001, compliance gap analysis'),
    ('terms-generator', 'Terms generator - ToS, privacy policy, cookie policy, EULA generator with customization'),
    ('nda-review', 'NDA review - mutual NDA, one-way NDA, key clause analysis, redlining, negotiation points'),
    ('legal-research', 'Legal research - case law, statutes, regulations, legal memo, citation verification'),
    # Data science skills
    ('pandas-expert', 'pandas expert - DataFrames, groupby, merge, pivot, time series, advanced operations'),
    ('numpy-patterns', 'NumPy patterns - arrays, broadcasting, vectorization, linear algebra, random operations'),
    ('sklearn-patterns', 'scikit-learn patterns - pipelines, cross-validation, hyperparameter tuning, model selection'),
    ('xgboost-patterns', 'XGBoost patterns - gradient boosting, feature importance, early stopping, custom metrics'),
    ('data-visualization', 'Data visualization - matplotlib, seaborn, plotly, altair, dashboards, chart selection'),
    ('feature-engineering', 'Feature engineering - encoding, scaling, imputation, interaction features, selection'),
    ('time-series-ml', 'Time series ML - ARIMA, Prophet, LSTM, forecasting evaluation, seasonality decomposition'),
    ('nlp-patterns', 'NLP patterns - text preprocessing, TF-IDF, embeddings, classification, entity extraction'),
    ('computer-vision-ml', 'Computer vision ML - CNN, transfer learning, object detection, segmentation, augmentation'),
    ('model-deployment', 'ML model deployment - FastAPI serving, Docker, BentoML, TorchServe, monitoring'),
    # Communication platform skills
    ('twilio-sms', 'Twilio SMS - send/receive SMS, MMS, webhooks, conversation API, messaging service'),
    ('twilio-voice', 'Twilio Voice - make/receive calls, TwiML, conference, recording, IVR, call flows'),
    ('sendgrid-email', 'SendGrid email - transactional email, templates, tracking, suppression, inbound parse'),
    ('mailchimp-marketing', 'Mailchimp marketing - campaigns, audiences, automations, A/B tests, reports'),
    ('discord-bot', 'Discord bot development - slash commands, embeds, interactions, gateway, permissions'),
    ('telegram-bot', 'Telegram bot development - commands, inline keyboards, webhooks, bot API patterns'),
    ('whatsapp-business', 'WhatsApp Business API - messages, templates, media, webhooks, commerce'),
    ('pusher-realtime', 'Pusher realtime - channels, events, presence, webhooks, authentication, socket.io'),
    # DevOps/Kubernetes skills
    ('k8s-advanced', 'Kubernetes advanced - operators, CRDs, admission webhooks, multi-cluster, networking'),
    ('prometheus-alerting', 'Prometheus alerting - alert rules, Alertmanager, routing, inhibition, silences'),
    ('grafana-dashboards-advanced', 'Grafana advanced dashboards - variables, transformations, alerting, provisioning'),
    ('jenkins-pipeline', 'Jenkins pipeline - Jenkinsfile, shared libraries, declarative vs scripted, blue-green'),
    ('tekton-cicd', 'Tekton CI/CD - pipelines, tasks, triggers, workspace, results, Hub catalog'),
    ('crossplane-platform', 'Crossplane platform engineering - managed resources, composite resources, providers'),
    # Security tools
    ('burp-suite-advanced', 'Burp Suite advanced - scanner, extensions, Turbo Intruder, collaborator, macros'),
    ('nmap-scanning', 'Nmap scanning - port scanning, OS detection, NSE scripts, firewall evasion, network map'),
    ('nuclei-templates', 'Nuclei templates - vulnerability templates, custom templates, fuzzing, DAST automation'),
    ('zap-scanning', 'OWASP ZAP scanning - active scan, passive scan, API testing, authentication, CI integration'),
    # Frontend frameworks
    ('solid-js', 'SolidJS framework - reactive primitives, signals, effects, components, routing, stores'),
    ('qwik-framework', 'Qwik framework - resumability, lazy loading, server components, signals, QwikCity'),
    ('htmx-patterns', 'HTMX patterns - hypermedia, AJAX attributes, server-sent events, WebSockets, boosting'),
    ('alpine-js', 'Alpine.js patterns - reactive components, directives, stores, magic properties, plugins'),
    # Backend frameworks
    ('fastify-nodejs', 'Fastify Node.js - schema validation, plugins, decorators, hooks, logging, TypeScript'),
    ('express-patterns', 'Express.js patterns - middleware, routing, error handling, auth, rate limiting'),
    ('koa-framework', 'Koa.js framework - async middleware, context, routing, error handling, middleware stack'),
    ('gin-golang', 'Gin Go framework - routing, middleware, binding, validation, JWT, file upload'),
    ('actix-rust', 'Actix-web Rust - actors, handlers, middleware, extractors, WebSockets, streaming'),
    ('spring-webflux', 'Spring WebFlux - reactive programming, Flux/Mono, functional endpoints, R2DBC'),
    # AI agent patterns
    ('react-agent', 'ReAct agent pattern - reasoning and acting, thought-action-observation loops'),
    ('plan-execute-agent', 'Plan and Execute agent - planning, task decomposition, execution, replanning'),
    ('reflexion-agent', 'Reflexion agent - self-reflection, verbal reinforcement, memory, iterative improvement'),
    ('tooleuse-agent', 'Tool use agent patterns - tool selection, parallel tools, tool chains, error recovery'),
    ('long-term-memory-agent', 'Long-term memory agent - episodic, semantic, procedural memory, retrieval strategies'),
    # Cloud deep-dives
    ('aws-vpc-networking', 'AWS VPC networking - subnets, route tables, security groups, NACLs, Transit Gateway'),
    ('aws-iam-patterns', 'AWS IAM patterns - roles, policies, permission boundaries, SCP, conditions, trust policies'),
    ('gcp-bigquery-advanced', 'GCP BigQuery advanced - partitioning, clustering, BI Engine, slots, ML, data transfer'),
    ('azure-networking', 'Azure networking - VNet, NSG, Load Balancer, Application Gateway, Private Link'),
    ('multi-cloud-identity', 'Multi-cloud identity - federated auth, workload identity, cross-cloud SSO patterns'),
    # Mobile/Game dev
    ('unity-shader-graph', 'Unity Shader Graph - visual shaders, PBR, custom nodes, VFX, material variants'),
    ('unreal-blueprints', 'Unreal Engine Blueprints - visual scripting, event graphs, components, game logic'),
    ('react-native-navigation', 'React Native navigation - React Navigation 6, stack, tab, drawer, deep linking'),
    ('flutter-state', 'Flutter state management - Riverpod, Bloc, Provider, GetX, ValueNotifier'),
    # Blockchain/Web3
    ('ethereum-development', 'Ethereum development - Hardhat, Foundry, Solidity, ERC standards, testing, deployment'),
    ('web3-frontend', 'Web3 frontend - wagmi, viem, ethers.js, RainbowKit, MetaMask, wallet connect'),
    ('solana-development', 'Solana development - Anchor framework, programs, accounts, IDL, Phantom wallet'),
    ('defi-protocols', 'DeFi protocols - AMM, lending, yield farming, flash loans, MEV, protocol integration'),
    # Data engineering
    ('apache-kafka', 'Apache Kafka - producers, consumers, streams, connect, schema registry, ksqlDB'),
    ('apache-spark-advanced', 'Apache Spark advanced - structured streaming, Delta Lake, ML pipelines, tuning'),
    ('dbt-advanced', 'dbt advanced - macros, packages, tests, documentation, snapshots, exposures, models'),
    ('apache-airflow-advanced', 'Apache Airflow advanced - custom operators, hooks, sensors, XCom, dynamic DAGs'),
    ('databricks-platform', 'Databricks platform - Delta Live Tables, Unity Catalog, MLflow, workflows, SQL'),
    # Research/Science
    ('jupyter-advanced', 'Jupyter advanced - ipywidgets, custom kernels, JupyterHub, nbconvert, extensions'),
    ('r-programming', 'R programming - tidyverse, ggplot2, dplyr, Shiny, statistical modeling, caret'),
    ('bioinformatics', 'Bioinformatics - sequence analysis, variant calling, BLAST, genome assembly, pipelines'),
    ('computational-chemistry', 'Computational chemistry - molecular dynamics, DFT, force fields, visualization'),
    # Business ops/Enterprise
    ('erp-integration', 'ERP integration - SAP, Oracle, NetSuite API patterns, data sync, middleware'),
    ('bi-tools', 'BI tools - Tableau, Power BI, Looker, Metabase, dashboard design, data modeling'),
    ('crm-integration', 'CRM integration - Salesforce, HubSpot, data sync, custom objects, workflows, APIs'),
    ('workflow-bpm', 'Workflow BPM - Camunda, Activiti, process modeling, BPMN, decision tables, DMN'),
    # Networking/Geospatial
    ('network-security', 'Network security - firewall rules, IDS/IPS, VPN, zero trust, network segmentation'),
    ('geospatial-analysis', 'Geospatial analysis - PostGIS, GeoPandas, QGIS, spatial queries, map visualization'),
    # Social media/Growth
    ('growth-hacking', 'Growth hacking - viral loops, referral programs, conversion optimization, funnel analysis'),
    ('influencer-marketing', 'Influencer marketing - outreach, campaign management, ROI tracking, creator economy'),
    ('community-building', 'Community building - Discord/Slack communities, moderation, engagement, growth'),
    # Advanced programming
    ('rust-systems', 'Rust systems programming - unsafe code, FFI, embedded, OS development, performance'),
    ('cpp-modern', 'Modern C++ - C++20/23, concepts, ranges, coroutines, modules, performance patterns'),
    ('haskell-functional', 'Haskell functional programming - monads, typeclasses, laziness, GHC optimization'),
    ('elixir-otp', 'Elixir OTP - GenServer, Supervisor, Phoenix, LiveView, Ecto, distributed systems'),
    # Financial markets/Quant
    ('algorithmic-trading', 'Algorithmic trading - backtesting, strategy development, execution, risk management'),
    ('portfolio-optimization', 'Portfolio optimization - modern portfolio theory, factor models, risk parity, rebalancing'),
    ('risk-management-quant', 'Quantitative risk management - VaR, CVaR, stress testing, Monte Carlo, Greeks'),
    # ML frameworks
    ('jax-ml', 'JAX ML framework - automatic differentiation, JIT compilation, vectorization, TPU training'),
    ('keras-ml', 'Keras ML - model building, callbacks, custom layers, mixed precision, distributed training'),
    ('onnx-deployment', 'ONNX model deployment - export, optimize, runtime, cross-framework inference'),
    # AI infrastructure
    ('triton-inference', 'Triton Inference Server - model deployment, concurrent models, dynamic batching, perf'),
    ('ray-cluster', 'Ray cluster - distributed computing, remote functions, actors, datasets, training'),
    ('kubeflow', 'Kubeflow MLOps - pipelines, katib, training operators, serving, notebook controllers'),
    # Real estate/PropTech
    ('real-estate-api', 'Real estate API - Zillow, Redfin, MLS data, property valuation, market analysis'),
    ('proptech-analytics', 'PropTech analytics - rental yield, cap rate, cash flow modeling, comparable analysis'),
    # Transport/Logistics
    ('logistics-api', 'Logistics API - shipping carriers, rate shopping, label generation, tracking, returns'),
    ('fleet-management', 'Fleet management - GPS tracking, route optimization, maintenance, telematics APIs'),
    # HR tech
    ('hr-management', 'HR management - HRIS integration, payroll APIs, benefits administration, onboarding'),
    ('recruiting-automation', 'Recruiting automation - ATS integration, resume parsing, candidate scoring, pipelines'),
    # Telecom/IoT
    ('iot-platform', 'IoT platform - MQTT, device management, OTA updates, time series, edge computing'),
    ('5g-edge', '5G edge computing - MEC, network slicing, latency optimization, edge AI deployment'),
    # AI safety
    ('ai-safety-evaluation', 'AI safety evaluation - red-teaming, adversarial testing, capability assessment, evals'),
    ('constitutional-ai-impl', 'Constitutional AI implementation - RLHF, RLAIF, value alignment, critique methods'),
    # Startup/VC
    ('pitch-deck', 'Pitch deck - problem/solution, market size, traction, team, financials, investor narrative'),
    ('fundraising-strategy', 'Fundraising strategy - SAFE notes, valuation, due diligence prep, investor relations'),
    ('startup-legal', 'Startup legal - incorporation, equity, vesting, IP assignment, employment, compliance'),
    # Quantum/Emerging
    ('quantum-computing', 'Quantum computing - Qiskit, Cirq, quantum gates, algorithms, NISQ, error correction'),
    ('edge-ai', 'Edge AI - TensorFlow Lite, ONNX Runtime, model compression, embedded deployment, NPU'),
    ('ar-vr-development', 'AR/VR development - Unity XR, WebXR, ARKit/ARCore, spatial computing, hand tracking'),
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
2. Test authentication and error handling first
3. Implement rate limiting and retry logic
4. Log all operations for debugging and audit
5. Use environment variables for credentials and config

## Common Patterns
- Setup and configuration
- Core operations
- Error handling and retries
- Authentication and authorization
- Monitoring and observability

## Models to Use
- Architecture: claude-opus-4-6
- Implementation: claude-sonnet-4-6
- Quick lookups: claude-haiku-4-5-20251001
'''
    with open(os.path.join(d, 'SKILL.md'), 'w') as f:
        f.write(content)

print('Done:', len(skills), 'skills')
