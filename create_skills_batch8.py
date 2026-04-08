
import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # More specialized AI tools
    ('evidently-ai', 'Evidently AI - ML model monitoring, data drift, performance metrics, reports, dashboards'),
    ('whylogs-profiling', 'whylogs data profiling - statistical profiles, data quality, drift detection, constraints'),
    ('deepchecks-testing', 'Deepchecks ML testing - model validation, data integrity, distribution drift, CI checks'),
    ('cleanlab-data', 'Cleanlab data-centric AI - label errors, noisy labels, dataset quality, auto-fix issues'),
    ('label-studio', 'Label Studio - data labeling, annotation, ML-assisted labeling, templates, exports'),
    ('argilla-annotation', 'Argilla annotation - human feedback, RLHF datasets, active learning, evaluation'),
    ('prodigy-annotation', 'Prodigy annotation tool - active learning, custom recipes, NLP annotation, review'),
    ('lilac-datasets', 'Lilac dataset tool - data exploration, semantic search, clustering, quality signals'),
    # More vector/search
    ('hnswlib', 'hnswlib - fast approximate nearest neighbor, HNSW graph, Python bindings, cosine similarity'),
    ('annoy-search', 'Annoy approximate nearest neighbor - trees, dot product, cosine, Euclidean, static index'),
    ('scann-google', 'ScaNN Google search - anisotropic quantization, tree-AH, brute force, streaming'),
    ('usearch-vector', 'USearch vector search - single-header, fast, 8-bit quantization, Matryoshka embeddings'),
    ('voyager-spotify', 'Voyager Spotify ANN - HNSW-based, Python/Java, fast build, exact search fallback'),
    # More runtime platforms
    ('deno-advanced', 'Deno advanced - permissions, built-ins, FFI, Workers, KV, Queues, Cron, Deploy'),
    ('bun-runtime', 'Bun runtime advanced - FFI, native modules, hot reload, macros, WASM, stdin/stdout'),
    ('wasmedge-runtime', 'WasmEdge runtime - server-side WASM, plugins, TensorFlow, image, WASI-NN'),
    ('cloudflare-workers-advanced', 'Cloudflare Workers advanced - bindings, scheduled, queues, analytics engine, AI'),
    ('lagon-runtime', 'Lagon - open-source edge runtime, TypeScript, streaming, env vars, cron, regions'),
    # More dev tools
    ('turbopack', 'Turbopack - Rust-based bundler, incremental builds, Next.js, lazy bundling, performance'),
    ('rspack', 'Rspack - Rust webpack, webpack compatible, fast HMR, module federation, plugins'),
    ('rolldown', 'Rolldown - Rust rollup alternative, ESM, CJS, plugins, tree shaking, fast builds'),
    ('oxlint-linter', 'oxlint linter - Rust-based fast linter, ESLint compatible, rules, auto-fix'),
    ('biome-formatter', 'Biome formatter/linter - fast, Rust-based, JavaScript/TypeScript/JSON, no config'),
    # More Python tooling
    ('mypy-advanced', 'mypy advanced - strict mode, protocols, TypedDicts, overloads, generics, stubs'),
    ('pyright-type', 'Pyright type checker - VS Code, strict, inlay hints, call hierarchy, type narrowing'),
    ('ruff-linter', 'Ruff linter - ultra-fast Python linter, 800+ rules, auto-fix, isort, pyupgrade'),
    ('pydantic-v2', 'Pydantic v2 - model validators, field validators, discriminated unions, model config'),
    ('attrs-python', 'attrs Python - class definitions, validators, converters, slots, frozen, evolution'),
    # More Go tooling
    ('buf-go', 'Buf Go protobuf - module system, lint, breaking detection, managed mode, custom plugins'),
    ('golangci-lint', 'golangci-lint - fast multi-linter, configuration, custom linters, nolint, cache'),
    ('goreleaser', 'GoReleaser - release automation, builds, archives, brew, Docker, GitHub/GitLab releases'),
    ('wire-go', 'Wire Go dependency injection - code generation, providers, injectors, compile-time DI'),
    ('fx-go', 'fx Go dependency injection - runtime DI, lifecycle, decorators, modules, logging'),
    # More Rust tooling
    ('cargo-advanced', 'Cargo advanced - workspaces, features, build scripts, custom registries, CI patterns'),
    ('criterion-bench', 'Criterion Rust benchmarking - statistical analysis, comparison, HTML reports, CI'),
    ('proptest-rust', 'proptest Rust - property-based testing, strategies, shrinking, test cases, derive'),
    ('tokio-advanced', 'Tokio async Rust advanced - runtime config, task scheduling, select!, cancellation, tracing'),
    ('tower-middleware', 'Tower middleware - service, layer, Buffer, Retry, RateLimit, timeout, load shed'),
    # More TypeScript tooling
    ('tsx-runner', 'tsx TypeScript runner - Node.js enhancement, watch mode, tsconfig paths, fast execution'),
    ('ts-node-advanced', 'ts-node advanced - transpile-only, ESM, paths, compiler API, REPL, swc integration'),
    ('zod-advanced', 'Zod advanced - branded types, transform, preprocess, discriminated unions, effects'),
    ('effect-ts', 'Effect TypeScript - functional effects, dependency injection, concurrency, error handling'),
    ('fp-ts-advanced', 'fp-ts advanced - IO, Task, ReaderTaskEither, optics, eq, ord, semigroup, monoid'),
    # More infrastructure
    ('pulumi-advanced', 'Pulumi advanced - automation API, testing, policy packs, Crosswalk, self-hosted'),
    ('cdk8s-constructs', 'cdk8s - Kubernetes manifests in code, constructs, TypeScript/Python/Go, synth'),
    ('helm-advanced', 'Helm advanced - library charts, CRDs, hooks, tests, OCI registries, plugins'),
    ('kustomize-advanced', 'Kustomize advanced - patches, generators, transformers, components, helm charts'),
    ('jsonnet-templating', 'Jsonnet templating - data template language, functions, std library, mixins, imports'),
    # More monitoring
    ('alertmanager-advanced', 'Alertmanager advanced - routing trees, inhibitions, silences, templates, HA setup'),
    ('thanos-metrics', 'Thanos - long-term Prometheus storage, global query, compaction, buckets, ruler'),
    ('cortex-metrics', 'Cortex - horizontally scalable Prometheus, tenant isolation, blocks, query frontend'),
    ('mimir-metrics', 'Grafana Mimir - scalable long-term metrics, blocks, compaction, ruler, alertmanager'),
    ('loki-advanced', 'Loki advanced - label design, LogQL, rulers, bloom filters, TSDB, microservices'),
    # More platforms
    ('supabase-realtime', 'Supabase Realtime - channels, presence, broadcast, postgres changes, RLS filtering'),
    ('convex-advanced', 'Convex advanced - mutations, queries, actions, scheduling, file storage, search'),
    ('appwrite-backend', 'Appwrite - open-source BaaS, auth, databases, storage, functions, realtime, teams'),
    ('pocketbase-advanced', 'PocketBase advanced - collections, rules, hooks, JS migrations, TypeScript SDK'),
    ('payload-cms', 'Payload CMS - headless CMS, access control, hooks, custom fields, REST/GraphQL API'),
    # More AI agents
    ('opendevin', 'OpenDevin - open-source Devin, coding agents, sandbox execution, multi-agent, planning'),
    ('devika-agent', 'Devika AI agent - task understanding, research, code generation, browser interaction'),
    ('agentgpt', 'AgentGPT - browser-based agent, task creation, execution chain, tool use, memory'),
    ('gpt-engineer', 'GPT Engineer - code generation, project scaffolding, clarifying questions, improvement'),
    ('sweep-ai', 'Sweep AI - GitHub issues to code, PR automation, code review, test generation'),
    # More UI frameworks
    ('mantine-ui', 'Mantine UI - React components, hooks, form, dates, charts, notifications, spotlight'),
    ('chakra-ui-v3', 'Chakra UI v3 - design system, theming, accessibility, dark mode, compound components'),
    ('headlessui', 'Headless UI - unstyled accessible components, Tailwind integration, React/Vue, dialogs'),
    ('ariakit', 'Ariakit - accessible React components, headless, composable, WAI-ARIA, test utilities'),
    ('react-aria', 'React Aria - Adobe accessibility, hooks, internationalization, overlays, drag-and-drop'),
    # More mobile
    ('jetpack-compose', 'Jetpack Compose - Android declarative UI, state, layouts, animations, navigation'),
    ('swiftui-advanced', 'SwiftUI advanced - custom layouts, animations, matchedGeometry, environment, preferences'),
    ('uikit-advanced', 'UIKit advanced - custom transitions, collection views, diffable data sources, performance'),
    ('android-architecture', 'Android architecture - MVVM, MVI, clean arch, Hilt DI, coroutines, Flow patterns'),
    ('react-native-reanimated', 'React Native Reanimated - worklets, shared values, gesture handler, layout animations'),
    # More DevOps
    ('earthly-advanced', 'Earthly advanced - remote caching, satellites, auto-skip, secrets, monorepo patterns'),
    ('dagger-advanced', 'Dagger advanced - modules, services, caching, secrets, multi-platform, SDK generation'),
    ('bazel-advanced', 'Bazel advanced - custom rules, macros, providers, aspects, remote execution, cache'),
    ('pants-build', 'Pants build system - Python/Java/Go, fine-grained caching, dependency inference, linting'),
    ('nx-monorepo', 'Nx monorepo advanced - affected, task graph, caching, generators, plugins, self-hosted'),
    # More security tools
    ('syft-sbom', 'Syft SBOM - software bill of materials, container analysis, file system, attestation'),
    ('grype-scanner', 'Grype vulnerability scanner - SBOM-based, OS packages, language ecosystems, CI gate'),
    ('semgrep-advanced', 'Semgrep advanced - pattern syntax, taint mode, join mode, custom rules, autofix'),
    ('bandit-python', 'Bandit Python security - AST analysis, plugins, baselines, CI integration, severity'),
    ('gosec-scanner', 'gosec Go security - AST rules, suppressions, sarif output, CI integration, rules'),
    # More data engineering
    ('hamilton-dag', 'Hamilton DAG - Python functions as data pipelines, lineage, parallelism, plugins'),
    ('zenml-mlops', 'ZenML MLOps - pipelines, stacks, artifacts, steps, integrations, cloud backends'),
    ('clearml-platform', 'ClearML platform - experiment tracking, data versioning, orchestration, serving'),
    ('comet-ml', 'Comet ML - experiment tracking, model registry, production monitoring, LLM evaluation'),
    ('neptune-ai', 'Neptune AI - metadata store, experiment comparison, model registry, team collaboration'),
    # More protocols
    ('grpc-advanced', 'gRPC advanced - deadlines, cancellation, health checking, reflection, load balancing, xDS'),
    ('graphql-federation', 'GraphQL Federation - subgraphs, supergraph, Apollo Router, composition, directives'),
    ('asyncapi-spec', 'AsyncAPI specification - event-driven API docs, channels, messages, bindings, generators'),
    ('cloudevents', 'CloudEvents - event format specification, SDKs, adapters, event routing, discovery'),
    ('opentelemetry-proto', 'OpenTelemetry Protocol - OTLP, gRPC, HTTP, metrics, traces, logs, exporters'),
    # More emerging
    ('mlx-apple', 'MLX Apple framework - ML on Apple Silicon, array operations, neural networks, training'),
    ('coreml-ios', 'Core ML iOS - model conversion, inference, Create ML, Turi Create, on-device training'),
    ('ane-neural', 'Apple Neural Engine - model optimization, ANE targeting, performance, Core ML tools'),
    ('metal-gpu', 'Metal GPU programming - compute shaders, render pipelines, buffers, Swift/Objective-C'),
    ('openvino-intel', 'OpenVINO Intel - model optimization, inference engine, model zoo, NNCF, benchmark'),
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
