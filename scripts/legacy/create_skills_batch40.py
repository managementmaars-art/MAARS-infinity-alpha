
import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # AI/ML advanced topics not yet covered
    ('diffusion-models-advanced', 'Diffusion models advanced - DDPM, DDIM, score matching, latent diffusion, classifier guidance'),
    ('flow-matching', 'Flow matching - continuous normalizing flows, optimal transport, rectified flow, Stable Flow'),
    ('world-models', 'World models - RSSM, DreamerV3, model-based RL, latent imagination, video prediction'),
    ('foundation-models', 'Foundation models - pretraining, emergent abilities, scaling laws, in-context learning, alignment'),
    ('llm-pretraining', 'LLM pretraining - data curation, tokenization, Megatron, DeepSpeed, FSDP, MFU, FLOP budget'),
    ('llm-finetuning', 'LLM fine-tuning - SFT, DPO, RLHF, PPO, LoRA, QLoRA, PEFT, alignment taxes, evaluation'),
    ('llm-inference', 'LLM inference - KV cache, speculative decoding, quantization, batching, vLLM, TensorRT-LLM'),
    ('llm-evaluation', 'LLM evaluation - benchmarks, MMLU, HellaSwag, contamination, human eval, model-as-judge'),
    ('multimodal-models', 'Multimodal models - vision-language, audio-language, video, interleaved, grounding, generation'),
    ('reasoning-models', 'Reasoning models - CoT, process reward, tree search, MCTS, OpenAI o1 patterns, verifier'),
    ('agent-frameworks', 'Agent frameworks - LangGraph, CrewAI, AutoGen, Swarm, tool use, planning, memory, grounding'),
    ('rag-advanced', 'RAG advanced - chunking, reranking, hybrid retrieval, HyDE, RAPTOR, agentic RAG, eval'),
    ('prompt-engineering-advanced', 'Prompt engineering advanced - few-shot, CoT, ToT, ReAct, DSPy, structured output, red teaming'),
    ('ai-alignment', 'AI alignment - RLHF, Constitutional AI, scalable oversight, IRL, debate, amplification, safety'),
    ('ai-interpretability', 'AI interpretability - mechanistic, probing, circuits, superposition, steering vectors, SAEs'),
    ('ai-red-teaming', 'AI red teaming - jailbreaks, prompt injection, adversarial, hallucination, bias, evaluation'),
    ('model-compression', 'Model compression - pruning, distillation, quantization, low-rank factorization, NAS, hardware'),
    ('ai-hardware', 'AI hardware - TPUs, H100/B200, AMD MI300, Gaudi, Trainium, interconnects, memory bandwidth'),
    ('mlops-advanced', 'MLOps advanced - feature stores, model registries, A/B testing, shadow mode, canary, drift'),
    ('data-centric-ai', 'Data-centric AI - data quality, labeling, curriculum, active learning, programmatic, SNUBA'),
    # Generative AI specialized
    ('image-generation-advanced', 'Image generation advanced - ComfyUI, A1111, workflow design, IPAdapter, ControlNet, inpainting'),
    ('video-generation-advanced', 'Video generation advanced - Sora architecture, DiT, temporal consistency, training, fine-tuning'),
    ('music-generation-ai', 'Music generation AI - MusicGen, Udio, Suno, audio tokens, conditioning, style transfer'),
    ('3d-generation-ai', '3D generation AI - NeRF, 3D Gaussian splatting, DreamFusion, Zero-1-to-3, mesh generation'),
    ('code-generation-ai', 'Code generation AI - Copilot, Claude for code, codegen, fill-in-middle, repo-level, evaluation'),
    ('ai-agents-advanced', 'AI agents advanced - tool calling, computer use, browser agents, code execution, long-horizon'),
    ('ai-memory-systems', 'AI memory systems - episodic, semantic, working memory, mem0, external stores, compression'),
    # Data engineering advanced
    ('apache-spark-advanced', 'Apache Spark advanced - catalyst optimizer, tungsten, streaming, GraphX, ML pipelines, GPU'),
    ('apache-flink-advanced', 'Apache Flink advanced - stateful functions, streaming SQL, savepoints, watermarks, exactly-once'),
    ('apache-beam-advanced', 'Apache Beam advanced - portable API, splittable DoFn, cross-language, Prism runner, Dataflow'),
    ('dbt-advanced', 'dbt advanced - macros, packages, semantic layer, unit tests, incremental, snapshots, orchestration'),
    ('apache-iceberg', 'Apache Iceberg - table format, hidden partitioning, time travel, schema evolution, catalog, merge-on-read'),
    ('apache-hudi', 'Apache Hudi - copy-on-write, merge-on-read, timeline, index, clustering, MDT, catalog'),
    ('delta-lake-advanced', 'Delta Lake advanced - liquid clustering, uniform, managed tables, row tracking, deletion vectors'),
    ('data-lakehouse', 'Data lakehouse - Unity Catalog, Polaris, table formats, governance, compute, query optimization'),
    ('duckdb-advanced', 'DuckDB advanced - extensions, parallel execution, friendly SQL, WASM, httpfs, spatial, delta'),
    ('polars-advanced', 'Polars advanced - lazy evaluation, streaming, cloud IO, Rust extensions, GPU, interop'),
    ('arrow-advanced', 'Apache Arrow advanced - IPC, Flight, ADBC, compute kernels, ACERO, DataFusion, flight SQL'),
    ('great-expectations', 'Great Expectations - expectations, checkpoints, data docs, custom, Spark, SQL, integrations'),
    ('data-quality-advanced', 'Data quality advanced - validation, monitoring, anomaly detection, lineage, observability'),
    ('data-contracts', 'Data contracts - schema registry, Avro, Protobuf, OpenDataMesh, standards, enforcement, breaking'),
    ('reverse-etl', 'Reverse ETL - Census, Hightouch, Polytomic, segments, syncs, audience builder, activation'),
    ('data-mesh-implementation', 'Data mesh implementation - domain ownership, data products, self-serve, federated governance'),
    # Infrastructure and platform
    ('platform-engineering', 'Platform engineering - IDP, Backstage, golden paths, paved road, developer portal, metrics'),
    ('backstage-advanced', 'Backstage advanced - plugins, software catalog, templates, TechDocs, search, RBAC, proxies'),
    ('crossplane-advanced', 'Crossplane advanced - compositions, composite resources, providers, XRDs, packages, claims'),
    ('flux-gitops', 'Flux GitOps advanced - reconcilers, sources, image automation, notifications, multi-tenancy'),
    ('argocd-advanced', 'ArgoCD advanced - ApplicationSets, sync waves, hooks, RBAC, SSO, notifications, plugin, drift'),
    ('tekton-advanced', 'Tekton advanced - tasks, pipelines, triggers, results, chains, supply chain security, Hub'),
    ('opentelemetry-advanced', 'OpenTelemetry advanced - semantic conventions, collectors, sampling, exporters, auto-instrumentation'),
    ('chaos-engineering', 'Chaos engineering - Chaos Monkey, Litmus, Gremlin, failure injection, game days, resilience'),
    ('finops-advanced', 'FinOps advanced - cloud cost management, allocation, optimization, anomaly detection, forecasting'),
    ('sre-advanced', 'SRE advanced - SLOs, error budgets, toil reduction, postmortems, capacity planning, oncall'),
    ('incident-management', 'Incident management - PagerDuty, Opsgenie, runbooks, severity, comms, blameless culture'),
    ('feature-flags-advanced', 'Feature flags advanced - LaunchDarkly, OpenFeature, targeting, rollouts, experimentation, SDKs'),
    ('api-gateway-advanced', 'API gateway advanced - Kong, Envoy, rate limiting, authentication, circuit breaker, GraphQL'),
    ('service-mesh-advanced', 'Service mesh advanced - Istio, Linkerd, Cilium mesh, mTLS, traffic management, Ambient'),
    ('ebpf-advanced', 'eBPF advanced - maps, helpers, XDP, TC, kprobes, uprobes, LSM, CO-RE, libbpf, bpftool'),
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
