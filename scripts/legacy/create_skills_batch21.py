
import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # Game Development Advanced
    ('unity-advanced', 'Unity advanced - DOTS, ECS, Job System, Burst compiler, URP/HDRP, Shader Graph, addressables'),
    ('unreal-engine-advanced', 'Unreal Engine advanced - Blueprints, C++ gameplay, Nanite, Lumen, MetaHuman, mass entity'),
    ('godot-advanced', 'Godot 4 advanced - GDScript, C#, shaders, multiplayer, physics, animation tree, navigation'),
    ('game-networking', 'Game networking - client-side prediction, lag compensation, rollback netcode, lockstep, relay'),
    ('game-physics', 'Game physics - rigid body dynamics, collision detection, constraint solving, soft bodies, particles'),
    ('procedural-generation', 'Procedural generation - noise functions, wave function collapse, L-systems, dungeon gen, terrain'),
    ('shader-programming', 'Shader programming - GLSL, HLSL, vertex/fragment, compute shaders, raytracing, post-processing'),
    ('game-audio', 'Game audio - FMOD, Wwise, procedural audio, spatialization, music systems, adaptive audio'),
    # Financial Engineering
    ('quantitative-finance', 'Quantitative finance - options pricing, Black-Scholes, Monte Carlo, volatility surfaces, Greeks'),
    ('algorithmic-trading', 'Algorithmic trading - backtesting, execution algorithms, market microstructure, latency, slippage'),
    ('risk-management-quant', 'Quantitative risk management - VaR, CVaR, stress testing, factor models, correlation'),
    ('fixed-income-analytics', 'Fixed income analytics - bond pricing, duration, convexity, yield curves, swap valuation'),
    ('portfolio-optimization', 'Portfolio optimization - Markowitz, Black-Litterman, factor investing, risk parity, constraints'),
    # Advanced Robotics
    ('ros2-advanced', 'ROS 2 advanced - lifecycle nodes, executors, DDS, QoS, Nav2, MoveIt2, micro-ROS'),
    ('robot-kinematics', 'Robot kinematics - forward/inverse kinematics, Jacobian, workspace analysis, trajectory planning'),
    ('slam-algorithms', 'SLAM algorithms - EKF SLAM, particle filter, graph SLAM, ORB-SLAM3, LiDAR SLAM, loop closure'),
    ('motion-planning', 'Motion planning - RRT, RRT*, PRM, potential fields, trajectory optimization, MPC'),
    ('computer-vision-robotics', 'Computer vision for robotics - object detection, 6DoF pose estimation, depth sensing, grasping'),
    # Advanced Compilers
    ('mlir-framework', 'MLIR framework - dialects, transforms, passes, canonicalization, lowering, affine, LLVM'),
    ('gcc-internals', 'GCC internals - gimple, RTL, middle-end, backend, plugins, attributes, built-ins'),
    ('jvm-internals', 'JVM internals - bytecode, class loading, JIT, GC algorithms, memory model, agents'),
    ('clr-internals', '.NET CLR internals - IL, JIT, GC, interop, native AOT, R2R, tiered compilation'),
    ('v8-internals', 'V8 internals - Ignition, Turbofan, hidden classes, inline caches, GC, heap snapshots'),
    # Advanced Cryptography
    ('cryptography-advanced', 'Advanced cryptography - elliptic curves, pairings, lattice-based, post-quantum, threshold sig'),
    ('tls-internals', 'TLS internals - handshake, cipher suites, certificates, session resumption, TLS 1.3 details'),
    ('secure-multiparty-computation', 'Secure multi-party computation - secret sharing, garbled circuits, oblivious transfer, SPDZ'),
    ('homomorphic-encryption', 'Homomorphic encryption - CKKS, BFV, BGV, TFHE, applications, Microsoft SEAL, OpenFHE'),
    ('key-management-advanced', 'Key management advanced - HSM, KMS, key ceremony, rotation automation, escrow, lifecycle'),
    # Advanced Mobile
    ('react-native-advanced', 'React Native advanced - New Architecture, Fabric, JSI, Hermes, turbo modules, codegen'),
    ('flutter-advanced', 'Flutter advanced - Impeller, custom render, platform channels, isolates, DevTools, multi-window'),
    ('swift-advanced', 'Swift advanced - actors, structured concurrency, macros, observation, Swift data, distributed'),
    ('kotlin-advanced', 'Kotlin advanced - coroutines advanced, K2 compiler, KMP, context receivers, contracts'),
    ('mobile-ci-cd', 'Mobile CI/CD - Fastlane, Bitrise, App Center, code signing, TestFlight, Play deployment'),
    # Advanced Haskell and Functional
    ('haskell-advanced', 'Haskell advanced - type classes, GHC extensions, STM, lens, servant, streaming, profiling'),
    ('scala-advanced', 'Scala 3 advanced - given/using, opaque types, type lambdas, macros, ZIO, Cats Effect'),
    ('clojure-advanced', 'Clojure advanced - transducers, core.async, spec, Datomic, ClojureScript, macros, protocols'),
    ('elixir-advanced', 'Elixir advanced - GenServer, Supervisor, OTP patterns, Phoenix LiveView, Nx, livebook'),
    ('erlang-otp', 'Erlang/OTP advanced - behaviours, release handling, hot code reload, mnesia, distribution'),
    # Advanced Data Warehousing
    ('snowflake-advanced', 'Snowflake advanced - dynamic tables, Snowpark, Cortex AI, data sharing, Marketplace, Unistore'),
    ('bigquery-advanced', 'BigQuery advanced - BI Engine, BQML, capacity slots, materialized views, remote functions'),
    ('redshift-advanced', 'Redshift advanced - AQUA, RA3, data sharing, Redshift ML, streaming ingestion, Spectrum'),
    ('databricks-advanced', 'Databricks advanced - Unity Catalog, Delta Live Tables, Feature Store, MLflow, Mosaic AI'),
    ('duckdb-advanced', 'DuckDB advanced - extensions, spatial, iceberg, delta, httpfs, JSON, parquet, arrow'),
    # Advanced API Frameworks
    ('fastapi-advanced', 'FastAPI advanced - dependency injection, background tasks, WebSocket, OpenAPI customization'),
    ('nestjs-advanced', 'NestJS advanced - custom decorators, interceptors, guards, microservices, CQRS, event sourcing'),
    ('actix-web-advanced', 'Actix-web advanced - extractors, middleware, WebSocket, actors, database pools, testing'),
    ('axum-framework', 'Axum framework - extractors, routing, middleware, WebSocket, testing, Tower integration'),
    ('gin-advanced', 'Gin framework advanced - middleware chains, custom validators, templating, graceful shutdown'),
    # Advanced LLM Applications
    ('multimodal-llm-apps', 'Multimodal LLM applications - vision, audio, video understanding, cross-modal retrieval'),
    ('llm-structured-output', 'LLM structured output - function calling, JSON mode, instructor, outlines, constrained gen'),
    ('llm-evaluation-advanced', 'LLM evaluation advanced - LLM-as-judge, evals frameworks, benchmarks, human eval, RLHF'),
    ('long-context-handling', 'Long context handling - document chunking, sliding window, hierarchical, compression, RAPTOR'),
    ('agentic-rag', 'Agentic RAG - corrective RAG, self-RAG, adaptive retrieval, routing, query transformation'),
    # Advanced Elixir/Phoenix
    ('phoenix-liveview-advanced', 'Phoenix LiveView advanced - live components, streams, JS hooks, uploads, testing'),
    ('ecto-advanced', 'Ecto advanced - custom types, dynamic queries, multi, repo patterns, telemetry, testing'),
    ('broadway-pipeline', 'Broadway - Elixir data processing, producers, consumers, concurrency, batching, rate limiting'),
    # Niche Programming Languages
    ('nim-language', 'Nim programming - pragmas, macros, templates, memory management, C FFI, compilation targets'),
    ('crystal-language', 'Crystal language - fibers, channels, macros, C bindings, web (Lucky/Kemal), shards'),
    ('zig-language', 'Zig language - comptime, allocators, error handling, C interop, build system, embedded'),
    ('v-language', 'V language - autofree, modules, concurrency, cross-compilation, web framework, C interop'),
    ('odin-language', 'Odin language - packages, allocators, context, intrinsics, core library, foreign import'),
    # Advanced Observability Tools
    ('clickhouse-advanced', 'ClickHouse advanced - MergeTree engines, materialized views, cluster setup, query optimization'),
    ('apache-pinot', 'Apache Pinot - real-time OLAP, segments, ingestion, upsert, star-tree index, Startree'),
    ('apache-druid', 'Apache Druid - real-time analytics, ingestion, segments, native queries, SQL, clustering'),
    ('loki-advanced', 'Grafana Loki advanced - LogQL, chunk cache, ruler, multi-tenancy, compactor, ingester'),
    ('tempo-advanced', 'Grafana Tempo advanced - TraceQL, parquet storage, metrics generation, search, integration'),
    # Advanced Identity Platforms
    ('keycloak-advanced', 'Keycloak advanced - custom SPIs, event listeners, user federation, themes, clustering'),
    ('auth0-advanced', 'Auth0 advanced - custom actions, post-login flows, organizations, fine-grained auth, logs'),
    ('okta-advanced', 'Okta advanced - universal directory, lifecycle mgmt, API Access Mgmt, inline hooks, Workflows'),
    ('authentik-platform', 'authentik - open-source IdP, flows, stages, policies, providers, outposts, LDAP'),
    ('zitadel-platform', 'ZITADEL - cloud-native IAM, organizations, projects, grants, audit log, event sourcing'),
    # Advanced Message Queues
    ('nats-advanced', 'NATS advanced - JetStream, key-value, object store, service pattern, leaf nodes, clustering'),
    ('pulsar-advanced', 'Apache Pulsar advanced - topics, subscriptions, functions, IO connectors, geo-replication'),
    ('activemq-artemis', 'ActiveMQ Artemis - virtual topics, diverts, bridges, clustering, JDBC, protocol support'),
    ('zeromq-patterns', 'ZeroMQ patterns - PUB/SUB, PUSH/PULL, REQ/REP, dealer/router, inproc, high water mark'),
    ('redpanda-advanced', 'Redpanda advanced - Kafka-compatible, WASM transforms, tiered storage, schema registry'),
    # Advanced Storage Systems
    ('ceph-advanced', 'Ceph advanced - RADOS, RBD, CephFS, RGW, CRUSH maps, BlueStore, Rook operator'),
    ('minio-advanced', 'MinIO advanced - erasure coding, distributed mode, lifecycle, replication, encryption, WORM'),
    ('longhorn-storage', 'Longhorn - Kubernetes distributed block storage, snapshots, backup, disaster recovery'),
    ('openebs-advanced', 'OpenEBS advanced - cStor, Jiva, LocalPV, MayaStor, data protection, performance'),
    ('rook-ceph-k8s', 'Rook-Ceph on Kubernetes - StorageClass, PVC, snapshots, toolbox, monitoring, upgrades'),
    # Advanced Service Mesh
    ('istio-advanced', 'Istio advanced - traffic management, authorization policies, telemetry, Ambient mesh, WASM'),
    ('linkerd-advanced', 'Linkerd advanced - SMI, multicluster, authorization policy, extensions, enterprise features'),
    ('cilium-advanced', 'Cilium advanced - eBPF, network policies, BGP, Hubble, Mesh, SPIFFE, gateway API'),
    ('kuma-advanced', 'Kuma service mesh advanced - MeshTrafficPermission, policies, multizone, ZoneIngress'),
    ('consul-connect-advanced', 'Consul Connect advanced - intentions, sidecar proxy, terminating gateways, ingress'),
    # Advanced Workflow Engines
    ('temporal-advanced', 'Temporal advanced - workflows, activities, schedules, versioning, signals, queries, testing'),
    ('conductor-advanced', 'Netflix Conductor advanced - workflow definition, workers, task types, sub-workflows'),
    ('cadence-workflow', 'Cadence workflow - domain isolation, task lists, signals, queries, archival, cross-DC'),
    ('apache-camel-advanced', 'Apache Camel advanced - EIP patterns, component catalog, Camel K, Quarkus, testing'),
    ('zeebe-camunda', 'Zeebe/Camunda 8 - BPMN, DMN, feel expressions, workers, tasklist, operate, Connectors'),
    # Advanced AI Ops
    ('mlflow-advanced', 'MLflow advanced - model registry, autologging, recipes, deployments, plugins, tracking server'),
    ('weights-biases-advanced', 'W&B advanced - sweeps, artifacts, tables, reports, launch, model registry, prompts'),
    ('neptune-mlops', 'Neptune.ai advanced - runs, models, experiments, metadata, queries, integrations'),
    ('comet-ml', 'Comet ML advanced - experiment tracking, model registry, MPM, LLM monitoring, panels'),
    ('dvc-advanced', 'DVC advanced - pipelines, experiments, studio, plots, cloud storage, remote cache'),
    # Advanced Frontend Tooling
    ('vite-advanced', 'Vite advanced - plugins, SSR, library mode, environment API, module federation, performance'),
    ('webpack-advanced', 'Webpack 5 advanced - module federation, asset modules, persistent cache, optimization'),
    ('esbuild-advanced', 'esbuild advanced - plugins, loaders, transforms, bundling, serve mode, metafile analysis'),
    ('rollup-advanced', 'Rollup advanced - plugins, tree shaking, code splitting, output formats, virtual modules'),
    ('parcel-advanced', 'Parcel advanced - plugins, macros, optimizers, resolvers, transformers, reporters'),
    # Advanced CSS and Design Systems
    ('css-advanced', 'CSS advanced - container queries, cascade layers, scope, nesting, custom properties, houdini'),
    ('design-tokens-advanced', 'Design tokens advanced - Style Dictionary, Token Transformer, multi-platform, theming'),
    ('tailwind-advanced', 'Tailwind CSS advanced - plugins, themes, JIT, component extraction, dark mode strategies'),
    ('css-in-js-advanced', 'CSS-in-JS advanced - zero-runtime, Linaria, vanilla-extract, Panda CSS, StyleX'),
    ('animation-systems', 'Animation systems - GSAP, Framer Motion, CSS animations, spring physics, gesture handling'),
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
