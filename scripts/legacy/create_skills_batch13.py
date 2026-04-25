
import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # More specialized ML/AI
    ('automl-advanced', 'AutoML advanced - NAS, HPO, AutoKeras, H2O AutoML, FLAML, AutoGluon, pipeline optimization'),
    ('neural-architecture-search', 'Neural architecture search - DARTS, evolutionary, one-shot, efficient NAS, hardware-aware'),
    ('hyperparameter-optimization', 'Hyperparameter optimization - Optuna, Ray Tune, Hyperopt, Bayesian optimization, Ax'),
    ('federated-learning-advanced', 'Federated learning advanced - differential privacy, secure aggregation, personalization, PySyft'),
    ('knowledge-distillation-advanced', 'Knowledge distillation advanced - teacher-student, feature mimicking, data-free, self-distillation'),
    ('model-watermarking', 'Model watermarking - weight watermarks, backdoor-based, robust watermarks, verification'),
    ('adversarial-robustness', 'Adversarial robustness - adversarial training, certified defenses, PGD, AutoAttack, RobustBench'),
    ('uncertainty-quantification', 'Uncertainty quantification - Bayesian neural networks, Monte Carlo dropout, conformal prediction'),
    # More data science
    ('causal-inference', 'Causal inference - DAGs, do-calculus, propensity scores, instrumental variables, DiD'),
    ('survival-analysis', 'Survival analysis - Kaplan-Meier, Cox model, accelerated failure time, competing risks'),
    ('bayesian-statistics', 'Bayesian statistics - PyMC, Stan, MCMC, variational inference, hierarchical models'),
    ('time-series-forecasting', 'Time series forecasting - ARIMA, Prophet, TFT, N-BEATS, Chronos, foundation models'),
    ('anomaly-detection', 'Anomaly detection - isolation forest, autoencoders, statistical methods, streaming anomalies'),
    ('recommender-systems', 'Recommender systems - collaborative filtering, matrix factorization, neural CF, session-based'),
    # More cloud services
    ('aws-lambda-advanced', 'AWS Lambda advanced - provisioned concurrency, container images, layers, extensions, SnapStart'),
    ('aws-ecs-advanced', 'AWS ECS advanced - Fargate, capacity providers, task networking, service discovery, deployment'),
    ('aws-eks-advanced', 'AWS EKS advanced - managed node groups, Karpenter, addons, EKS Anywhere, IRSA'),
    ('gcp-cloud-run-advanced', 'GCP Cloud Run advanced - min instances, VPC connector, authentication, jobs, sidecars'),
    ('azure-container-apps', 'Azure Container Apps - Dapr, KEDA, revisions, managed identity, scale rules'),
    ('aws-rds-advanced', 'AWS RDS advanced - proxy, Performance Insights, blue/green, Aurora Serverless v2, global'),
    # More DevSecOps
    ('dependency-scanning', 'Dependency scanning - OWASP Dependency-Check, Snyk, Dependabot, npm audit, safety'),
    ('secrets-scanning', 'Secrets scanning - git-secrets, TruffleHog, Gitleaks, detect-secrets, pre-commit hooks'),
    ('sast-tools', 'SAST tools - CodeQL, Semgrep, SonarQube, Checkmarx, Veracode, integration patterns'),
    ('dast-tools', 'DAST tools - OWASP ZAP, Burp Suite automation, API security testing, active scanning'),
    ('container-scanning', 'Container scanning - Trivy, Grype, Snyk, Twistlock, Aqua, admission policies'),
    # More API integration tools
    ('zapier-advanced', 'Zapier advanced - multi-step zaps, paths, code steps, custom webhooks, tables, interfaces'),
    ('make-scenarios', 'Make (Integromat) scenarios - complex routing, data stores, custom functions, error handling'),
    ('pipedream-advanced', 'Pipedream advanced - workflows, event sources, actions, connected accounts, components'),
    ('tray-io', 'Tray.io - enterprise iPaaS, visual workflows, helpers, custom connectors, authentication'),
    ('boomi-platform', 'Boomi AtomSphere - integration platform, processes, trading partners, APIs, flow services'),
    # More developer tools
    ('gh-copilot-cli', 'GitHub Copilot CLI - gh copilot explain, suggest, shell, git, alias, custom agents'),
    ('cline-agent', 'Cline (Claude Dev) - autonomous coding agent, file operations, terminal, browser, MCP'),
    ('aider-tool', 'Aider coding tool - git-aware, architect mode, code context, benchmark, conventions'),
    ('continue-dev-tool', 'Continue.dev - open-source autopilot, model config, context providers, slash commands'),
    ('sourcegraph-cody', 'Sourcegraph Cody - code search, AI context, remote repos, batch changes, code insights'),
    # More monitoring and observability
    ('datadog-advanced', 'Datadog advanced - APM, RUM, logs, synthetics, notebooks, monitors, CI visibility'),
    ('new-relic-advanced', 'New Relic advanced - NRQL, distributed tracing, errors inbox, change tracking, AI monitoring'),
    ('dynatrace-advanced', 'Dynatrace advanced - Davis AI, smartscape, logs, sessions, PurePaths, remote modules'),
    ('splunk-advanced', 'Splunk advanced - SPL, dashboards, alerts, ML toolkit, ITSI, SOAR, Phantom'),
    ('elastic-apm', 'Elastic APM - distributed tracing, service maps, ML anomaly, uptime, logs correlation'),
    # More backend frameworks
    ('django-channels', 'Django Channels - WebSocket, ASGI, consumers, layers, authentication, testing'),
    ('fastapi-advanced', 'FastAPI advanced - dependency injection, middleware, background tasks, lifespan, OpenAPI'),
    ('flask-advanced', 'Flask advanced - blueprints, application factory, extensions, testing, deployment patterns'),
    ('rails-advanced', 'Rails advanced - Active Job, Action Cable, Action Mailbox, Hotwire, Turbo, Stimulus'),
    ('spring-boot-advanced', 'Spring Boot advanced - actuator, circuit breaker, async, batch, scheduling, testing'),
    # More frontend frameworks
    ('react-18-patterns', 'React 18 patterns - concurrent features, Suspense, transitions, useDeferredValue, streaming'),
    ('next-14-patterns', 'Next.js 14 patterns - App Router, server actions, partial prerendering, Turbopack, caching'),
    ('vue-3-advanced', 'Vue 3 advanced - Composition API, teleport, fragments, suspense, reactivity transform'),
    ('svelte-5-runes', 'Svelte 5 runes - $state, $derived, $effect, $props, snippets, legacy interop'),
    ('solid-advanced', 'SolidJS advanced - createResource, suspense boundaries, lazy, error boundary, stores'),
    # More mobile development
    ('ios-swift-advanced', 'iOS Swift advanced - SwiftData, SwiftUI animations, Observation framework, visionOS'),
    ('android-kotlin-advanced', 'Android Kotlin advanced - Compose multiplatform, Room v2, Navigation, WorkManager v2'),
    ('flutter-advanced', 'Flutter advanced - rendering performance, platform channels, isolates, FFI, custom paint'),
    ('react-native-advanced', 'React Native advanced - Hermes, JSI bindings, custom native modules, CI/CD, testing'),
    ('capacitor-advanced', 'Capacitor advanced - custom plugins, live updates, native project customization, CI'),
    # More data engineering tools
    ('spark-streaming', 'Spark Streaming - structured streaming, triggers, watermarking, stateful processing, sinks'),
    ('flink-advanced', 'Flink advanced - state backends, watermarks, windowing, async IO, CEP, table API'),
    ('kafka-advanced', 'Kafka advanced - consumer groups, exactly-once semantics, tiered storage, KRaft mode'),
    ('debezium-cdc', 'Debezium CDC - change data capture, connectors, outbox event router, signal table'),
    ('airbyte-advanced', 'Airbyte advanced - custom connectors, dbt integration, connection testing, Cloud API'),
    # More AI product patterns
    ('llm-product-design', 'LLM product design - UX patterns, latency optimization, feedback loops, trust, fallbacks'),
    ('ai-ux-patterns', 'AI UX patterns - streaming UI, skeleton loaders, optimistic updates, progressive disclosure'),
    ('copilot-experience', 'Copilot experience design - inline suggestions, proactive assistance, context awareness'),
    ('conversational-ui', 'Conversational UI - chat design, conversation design, intent recognition, fallback flows'),
    ('ai-evaluation-framework', 'AI evaluation framework - LLM-as-judge, human eval, automated benchmarks, red teaming'),
    # More specialized programming
    ('webassembly-systems', 'WebAssembly systems programming - component model, WASI preview 2, interfaces, tools'),
    ('gpu-programming', 'GPU programming - CUDA, ROCm, Metal, OpenCL, compute shaders, profiling, optimization'),
    ('systems-programming', 'Systems programming - memory management, concurrency, OS interfaces, performance, safety'),
    ('compiler-design', 'Compiler design - lexing, parsing, AST, IR, code gen, LLVM, optimization passes'),
    ('dsl-design', 'DSL design - internal DSLs, external DSLs, parser combinators, Lark, ANTLR, textX'),
    # More quantitative/finance
    ('quantlib', 'QuantLib - derivatives pricing, yield curves, Monte Carlo, finite differences, calibration'),
    ('backtrader-trading', 'Backtrader - backtesting framework, strategies, indicators, analyzers, live trading'),
    ('zipline-backtest', 'Zipline - Quantopian-style backtesting, factors, pipelines, risk management, Alphalens'),
    ('vectorbt-analysis', 'vectorbt - vectorized backtesting, portfolio analysis, signals, statistics, plotting'),
    ('finrl-deep-rl', 'FinRL - deep reinforcement learning for finance, agents, environments, ensembles'),
    # More web3/blockchain
    ('foundry-advanced', 'Foundry advanced - forge tests, fuzzing, differential testing, cheatcodes, gas snapshots'),
    ('hardhat-advanced', 'Hardhat advanced - plugins, tasks, network forking, ignition deploy, coverage'),
    ('ethers-js-advanced', 'Ethers.js v6 advanced - multicall, ENS, batch requests, ABI encoding, signing'),
    ('wagmi-advanced', 'wagmi v2 advanced - connectors, hooks, SSR, TanStack Query integration, WalletConnect'),
    ('thirdweb-advanced', 'thirdweb advanced - SDK, Engine, embedded wallets, smart accounts, prebuilt contracts'),
    # More infrastructure patterns
    ('zero-downtime-deploy', 'Zero downtime deployment - rolling, blue-green, database migrations, traffic shifting'),
    ('disaster-recovery', 'Disaster recovery - RTO/RPO, runbooks, backup validation, chaos testing, DR drills'),
    ('high-availability', 'High availability - redundancy, failover, split-brain prevention, quorum, health checks'),
    ('load-balancing', 'Load balancing - algorithms, health checks, sticky sessions, L4 vs L7, global LB'),
    ('service-discovery', 'Service discovery - DNS-based, client-side, server-side, Consul, Eureka, Kubernetes DNS'),
    # More observability patterns
    ('sli-slo-design', 'SLI/SLO design - user journeys, measurement, error budgets, alerting strategy, reviews'),
    ('log-aggregation', 'Log aggregation - structured logging, centralized collection, parsing, correlation, retention'),
    ('metrics-design', 'Metrics design - RED method, USE method, four golden signals, cardinality, naming'),
    ('distributed-profiling', 'Distributed profiling - continuous profiling, Pyroscope, Parca, fleet profiling'),
    ('synthetic-monitoring', 'Synthetic monitoring - uptime checks, transaction monitoring, API checks, alerting'),
    # More productivity and tooling
    ('neovim-advanced', 'Neovim advanced - Lua config, LSP, Telescope, lazy.nvim, DAP, treesitter, custom plugins'),
    ('vscode-advanced', 'VS Code advanced - multi-root workspaces, tasks, devcontainers, extensions, debugging'),
    ('tmux-advanced', 'tmux advanced - session management, scripting, plugins, key bindings, status bar, panes'),
    ('dotfiles-management', 'Dotfiles management - chezmoi, stow, Nix home-manager, templating, secrets, bootstrap'),
    ('shell-productivity', 'Shell productivity - zsh/fish, completions, aliases, functions, history, fzf, zoxide'),
    # More testing and quality
    ('test-architecture', 'Test architecture - test doubles, test boundaries, test data, isolation, test suites'),
    ('continuous-testing', 'Continuous testing - shift-left, automated gates, quality metrics, flakiness, reporting'),
    ('security-testing-patterns', 'Security testing patterns - threat modeling to tests, pentest automation, finding patterns'),
    ('performance-profiling', 'Performance profiling - CPU, memory, I/O, network, database, flamegraphs, sampling'),
    ('code-coverage-strategies', 'Code coverage strategies - line, branch, mutation, meaningful coverage, exemptions'),
    # More platform-specific
    ('aws-lambda-functions', 'AWS Lambda functions - event sources, cold starts, layers, extensions, powertools'),
    ('gcp-functions', 'GCP Cloud Functions v2 - triggers, secrets, concurrency, scaling, testing, deployment'),
    ('azure-functions-advanced', 'Azure Functions advanced - durable functions, isolated worker, extensions, managed identity'),
    ('cloudflare-workers-patterns', 'Cloudflare Workers patterns - caching, storage, queues, analytics, AI, routing'),
    ('vercel-functions', 'Vercel Functions - edge, serverless, streaming, cron, environment, middleware, ISR'),
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
