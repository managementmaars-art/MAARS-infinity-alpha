
import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # Advanced AI/ML research and architectures
    ('mixture-of-depths', 'Mixture of Depths - dynamic compute allocation, token routing, depth-aware transformers'),
    ('state-space-models', 'State space models - Mamba, S4, RWKV, linear RNNs, selective state spaces, efficiency'),
    ('long-range-attention', 'Long-range attention - linear attention, flash attention variants, sliding window, sparse'),
    ('retrieval-augmented-generation', 'RAG advanced research - multi-hop, agentic RAG, FLARE, SELF-RAG, adaptive retrieval'),
    ('continual-pretraining', 'Continual pretraining - domain adaptation, catastrophic forgetting, replay, EWC'),
    ('model-distillation-research', 'Model distillation research - logit matching, feature distillation, born-again, data-free'),
    ('reward-modeling', 'Reward modeling - RLHF, DPO, SPIN, ORPO, reward hacking, preference datasets, Bradley-Terry'),
    ('constitutional-ai-research', 'Constitutional AI research - RLAIF, AI feedback, red teaming, harmlessness, helpfulness'),
    ('agent-memory-research', 'Agent memory research - episodic, semantic, procedural, working memory, consolidation'),
    ('tool-use-research', 'Tool use research - function calling, code interpreters, web browsers, toolformer'),
    ('multimodal-pretraining', 'Multimodal pretraining - vision-language alignment, CLIP training, LLaVA, Flamingo, GPT-4V'),
    ('protein-structure-prediction', 'Protein structure prediction - AlphaFold2/3, ESMFold, RoseTTAFold, contact maps'),
    ('molecule-generation', 'Molecule generation - graph neural networks, VAE, diffusion models for drug discovery'),
    ('neural-combinatorial-opt', 'Neural combinatorial optimization - attention models, REINFORCE, pointer networks, TSP'),
    ('physical-simulation-ml', 'Physical simulation ML - GNNs, neural ODEs, physics-informed networks, differentiable sim'),
    ('world-model-research', 'World model research - RSSM, DreamerV3, IRIS, TD-MPC, model-based RL, planning'),
    ('offline-rl-research', 'Offline RL research - IQL, TD3+BC, decision transformer, Q-learning constraints'),
    ('multi-agent-rl-research', 'Multi-agent RL research - MAPPO, MADDPG, cooperative, competitive, emergent communication'),
    ('imitation-learning-research', 'Imitation learning research - GAIL, AIRL, BC, DAgger, preference learning, inverse RL'),
    ('causal-representation-learning', 'Causal representation learning - ICA, causal disentanglement, interventions, SCM'),
    # Data engineering and pipelines deep
    ('apache-spark-streaming', 'Apache Spark streaming - DStream, Structured Streaming, watermarks, triggers, state'),
    ('delta-live-tables', 'Delta Live Tables - declarative pipelines, expectations, CDC, streaming, Unity Catalog'),
    ('apache-hudi-advanced', 'Apache Hudi advanced - COW, MOR, clustering, compaction, incremental queries, time travel'),
    ('apache-iceberg-advanced', 'Apache Iceberg advanced - table format, snapshots, hidden partitioning, merge-on-read'),
    ('apache-paimon', 'Apache Paimon - streaming lakehouse, changelog tables, partial updates, lookup tables'),
    ('nessie-catalog', 'Project Nessie - git-like catalog, branching, tagging, multi-table transactions, Iceberg'),
    ('apache-ozone', 'Apache Ozone - object store, SCM, OM, DataNode, replication, ACLs, S3 compatibility'),
    ('trino-advanced', 'Trino advanced - federation, connectors, cost-based optimizer, query analysis, security'),
    ('presto-engineering', 'Presto engineering - cluster setup, connectors, ORC/Parquet, coordinator, workers'),
    ('dremio-platform', 'Dremio data lakehouse - Sonar, Arctic, reflections, semantic layer, governance'),
    ('starburst-galaxy', 'Starburst Galaxy - Trino cloud, data products, policies, metadata discovery, federation'),
    ('databricks-unity-catalog', 'Databricks Unity Catalog - three-level namespace, lineage, access control, sharing'),
    ('apache-ranger', 'Apache Ranger - row-level security, column masking, policies, auditing, Hadoop security'),
    ('apache-atlas-advanced', 'Apache Atlas advanced - business glossary, classifications, lineage, hooks, REST API'),
    ('openlineage', 'OpenLineage - lineage standard, facets, backends, integrations, Marquez, spark plugin'),
    ('great-expectations-advanced', 'Great Expectations advanced - expectation suites, data docs, custom expectations, cloud'),
    ('soda-data-quality', 'Soda data quality - checks, YAML syntax, SodaCL, cloud platform, incidents, alerting'),
    ('monte-carlo-data', 'Monte Carlo data observability - monitors, field health, dimension tracking, lineage'),
    ('datafold-data-diff', 'Datafold data-diff - diff algorithms, profiling, CI integration, cloud discovery'),
    ('recce-data-review', 'Recce data review - dbt diff, PR review, state comparison, data impact analysis'),
    # Web3 and blockchain advanced
    ('solana-program-development', 'Solana program development - Anchor framework, PDAs, CPIs, accounts, instructions'),
    ('ethereum-eips', 'Ethereum EIPs - EIP-1559, EIP-4844, EIP-7702, protocol governance, research, implemention'),
    ('layer2-architecture', 'Layer 2 architecture - optimistic rollups, ZK rollups, data availability, sequencers'),
    ('cosmos-ibc-advanced', 'Cosmos IBC advanced - channels, packets, relayers, acknowledgements, timeouts, clients'),
    ('polkadot-substrate', 'Polkadot Substrate - pallets, runtimes, FRAME, ink! contracts, XCM, parachain'),
    ('aptos-move', 'Aptos Move - resources, modules, abilities, formal verification, signer, Aptos SDK'),
    ('sui-move', 'Sui Move - objects, ownership, shared objects, Sui SDK, Move on Sui, dynamic fields'),
    ('web3-indexing', 'Web3 indexing - The Graph, Ponder, Envio, indexer architecture, subgraph development'),
    ('flashloan-mechanics', 'Flashloan mechanics - arbitrage, liquidations, price manipulation, AAVE, Uniswap V3'),
    ('mev-strategies', 'MEV strategies - frontrunning, sandwich attacks, liquidations, Flashbots, PBS, inclusion'),
    # Mobile advanced
    ('react-native-performance', 'React Native performance - hermes, concurrent features, fabric, turbo modules, profiling'),
    ('flutter-riverpod', 'Flutter Riverpod - providers, notifiers, scoping, testing, code generation, migration'),
    ('ios-swift-concurrency', 'iOS Swift concurrency - async/await, actors, sendable, structured concurrency, tasks'),
    ('android-compose-advanced', 'Android Compose advanced - custom layouts, phases, side effects, state hoisting, testing'),
    ('mobile-ar-development', 'Mobile AR development - ARKit, ARCore, RealityKit, anchors, plane detection, occlusion'),
    ('mobile-ml-on-device', 'Mobile ML on-device - Core ML, TFLite, ONNX Mobile, quantization, model optimization'),
    ('cross-platform-kmp', 'Kotlin Multiplatform - shared business logic, expect/actual, Compose Multiplatform'),
    ('mobile-payment-integration', 'Mobile payment integration - Apple Pay, Google Pay, Stripe mobile, in-app purchases'),
    ('mobile-push-advanced', 'Mobile push advanced - APNs, FCM, rich notifications, delivery receipts, segmentation'),
    ('mobile-testing-advanced', 'Mobile testing advanced - Espresso, XCTest, Detox, device farms, visual regression'),
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
