
import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # pbakaus/impeccable collection - writing quality tools
    ('polish', 'Polish writing - refine prose, improve flow, fix grammar, enhance clarity, elevate style'),
    ('critique', 'Critique writing - constructive feedback, structure analysis, argument evaluation, suggestions'),
    ('adapt', 'Adapt content - tone shifting, audience targeting, platform formatting, style transformation'),
    ('animate', 'Animate content - bring text to life, narrative energy, vivid descriptions, dynamic pacing'),
    ('clarify', 'Clarify writing - simplify complex ideas, remove ambiguity, plain language, clear explanations'),
    ('colorize', 'Colorize writing - add vivid detail, sensory language, metaphors, expressive vocabulary'),
    ('normalize', 'Normalize content - standardize formatting, consistent style, canonical form, uniformity'),
    ('teach-impeccable', 'Teaching writing - pedagogy, explanation scaffolding, learning objectives, engagement'),
    ('bolder', 'Make writing bolder - stronger claims, assertive language, confident tone, decisive framing'),
    ('delight', 'Delight in writing - surprise elements, wit, playfulness, memorable moments, reader joy'),
    ('distill', 'Distill content - extract essence, condense meaning, key points, summary, core message'),
    ('extract', 'Extract information - pull key data, structured extraction, entities, facts, relationships'),
    ('onboard', 'Onboard users - first-run experience, guided tutorials, progressive disclosure, welcome flows'),
    ('harden', 'Harden systems - security review, vulnerability scanning, defense in depth, attack surface'),
    ('quieter', 'Quieter writing - reduce noise, concise prose, minimize verbosity, signal over noise'),
    # inferen-sh/skills collection
    ('ai-image-generation', 'AI image generation - text-to-image, DALL-E, Midjourney, Stable Diffusion, prompting, style'),
    ('ai-video-generation', 'AI video generation - text-to-video, Sora, Runway, Pika, prompting, editing, transitions'),
    ('agent-tools', 'Agent tools - tool use patterns, function calling, tool selection, parallel execution, results'),
    ('remotion-render', 'Remotion render - programmatic video, React components, compositions, lambda rendering'),
    ('qwen-image-2', 'Qwen VL image analysis - visual question answering, OCR, chart analysis, multimodal'),
    ('p-video', 'Video processing pipeline - ffmpeg, transcoding, thumbnails, subtitles, compression, streaming'),
    ('p-image', 'Image processing pipeline - Sharp, Pillow, resize, crop, compress, format convert, watermark'),
    ('infsh-cli', 'infsh CLI tools - command-line interface utilities, shell scripting, automation, terminal'),
    ('elevenlabs-music', 'ElevenLabs music - audio generation, voice synthesis, sound effects, music creation API'),
    # browser automation
    ('browser-use', 'Browser use - AI browser automation, web scraping, form filling, navigation, screenshot, tasks'),
    ('agent-browser', 'Agent browser - autonomous web browsing, task completion, web interaction, UI automation'),
    # design
    ('sleek-design-mobile-apps', 'Sleek mobile app design - UI/UX patterns, visual hierarchy, typography, color, animations'),
    # Vercel labs / Next.js
    ('next-best-practices', 'Next.js best practices - app router, server components, data fetching, caching, optimization'),
    ('next-cache-components', 'Next.js caching components - React cache, fetch cache, router cache, revalidation, ISR'),
    # audit / scanning
    ('audit-website', 'Website audit - SEO analysis, performance, accessibility, security headers, broken links'),
    # Azure / Microsoft cloud skills
    ('microsoft-foundry', 'Microsoft AI Foundry - Azure AI Studio, model catalog, fine-tuning, deployment, evaluation'),
    ('azure-compute', 'Azure Compute - VMs, scale sets, AKS, App Service, Functions, Container Apps, sizing'),
    ('azure-quotas', 'Azure quotas management - subscription limits, quota requests, regional availability, tracking'),
    ('azure-upgrade', 'Azure upgrades - SKU migration, service tier changes, VM resizing, deprecation handling'),
    ('azure-cloud-migrate', 'Azure cloud migration - assessment, rehost, refactor, replatform, data migration, cutover'),
    ('azure-postgres', 'Azure Database for PostgreSQL - Flexible Server, HA, read replicas, extensions, migration'),
    # Vercel AI SDK
    ('ai-sdk', 'Vercel AI SDK - useChat, useCompletion, streaming, tool calling, RSC, provider adapters'),
    # Testing
    ('playwright-best-practices', 'Playwright best practices - page objects, fixtures, parallelism, CI, tracing, reporters'),
    # Monorepo
    ('turborepo', 'Turborepo - monorepo build system, caching, pipelines, remote cache, workspaces, pruning'),
    # Vue.js
    ('vue-best-practices', 'Vue 3 best practices - Composition API, Pinia, composables, async components, performance'),
    ('vue', 'Vue.js fundamentals - reactivity, directives, components, slots, router, state, lifecycle'),
    # Tavily search
    ('search', 'AI search integration - Tavily API, web search, RAG, real-time data, search augmentation'),
    # Discovery
    ('find-skills', 'Find skills - skill discovery, capability search, skill registry, matching, recommendations'),
    # Self-improvement agents
    ('self-improving-agent', 'Self-improving agent - reflection loops, skill acquisition, capability expansion, meta-learning'),
    # Prediction markets
    ('grimoire-polymarket', 'Polymarket trading - prediction markets, market making, probability assessment, position sizing'),
    # Simplicity patterns
    ('simple', 'Simple solutions - YAGNI, KISS principle, complexity reduction, minimal viable implementation'),
    # Baoyu skills series (jimliu)
    ('baoyu-translate', 'Translation agent - multilingual, context-aware, cultural adaptation, terminology consistency'),
    ('baoyu-code-review', 'Code review agent - automated review, style checks, logic analysis, security, suggestions'),
    ('baoyu-refactor', 'Refactoring agent - code improvement, design patterns, technical debt, readability, performance'),
    ('baoyu-test-gen', 'Test generation - unit tests, integration tests, edge cases, mocks, coverage improvement'),
    ('baoyu-diagram', 'Diagram generation - Mermaid, PlantUML, architecture diagrams, flowcharts, sequence diagrams'),
    # Dogfood / internal tools
    ('dogfood', 'Dogfooding patterns - internal tool usage, feedback loops, eat your own cooking, iteration'),
    # Supercent-io / template skills
    ('game-monetization', 'Game monetization - IAP, ads, subscriptions, battle pass, live ops, retention, ARPU'),
    ('mobile-game-analytics', 'Mobile game analytics - cohort analysis, funnel analysis, retention curves, LTV, A/B testing'),
    ('hyper-casual-games', 'Hyper-casual game design - core loop, meta, viral mechanics, ad monetization, retention'),
    # Additional skills.sh top skills not yet covered
    ('nano-banana', 'Nano Banana - lightweight agent toolkit, minimal dependencies, composable, fast execution'),
    ('seedance-api', 'Seedance API - dance video generation, motion synthesis, AI choreography, avatar animation'),
    ('elevenlabs-advanced', 'ElevenLabs advanced - voice cloning, multilingual, streaming TTS, projects, dubbing API'),
    ('perplexity-api', 'Perplexity API - online LLM, real-time search, citations, streaming, model selection'),
    ('tavily-api', 'Tavily search API - web search for AI agents, structured results, filtering, topic search'),
    ('firecrawl-api', 'Firecrawl - web scraping API, structured extraction, crawl, map, markdown output'),
    ('e2b-sandboxes', 'E2B code sandboxes - secure code execution, custom environments, filesystems, streams'),
    ('composio-tools', 'Composio tools - 100+ integrations, tool calling, authentication, triggers, actions'),
    ('mem0-memory', 'Mem0 memory - persistent memory for AI agents, user preferences, context retention'),
    ('langfuse-tracing', 'Langfuse tracing - LLM observability, traces, evals, datasets, prompt management'),
    ('helicone-analytics', 'Helicone analytics - LLM usage tracking, cost, latency, errors, gateway, caching'),
    # Additional cross-cutting agent skills
    ('computer-use', 'Computer use - desktop automation, GUI interaction, screenshot analysis, OS control'),
    ('code-interpreter', 'Code interpreter - sandboxed execution, data analysis, visualization, file processing'),
    ('web-research', 'Web research agent - multi-source synthesis, fact-checking, citation, structured output'),
    ('document-analysis', 'Document analysis - PDF parsing, table extraction, OCR, summarization, Q&A'),
    ('data-extraction', 'Data extraction agent - structured output, schema mapping, validation, transformation'),
    # Modern AI platforms
    ('groq-inference', 'Groq inference - ultra-fast LLM inference, LPU, GroqCloud API, streaming, tool use'),
    ('together-ai', 'Together AI - open-source model hosting, fine-tuning, inference API, embedding models'),
    ('replicate-api', 'Replicate API - ML model deployment, predictions, fine-tuning, streaming, webhooks'),
    ('modal-labs', 'Modal Labs - serverless GPU compute, containers, scheduled jobs, web endpoints, volumes'),
    ('runpod-gpu', 'RunPod GPU cloud - pod creation, serverless endpoints, autoscaling, custom containers'),
    # Agent frameworks not yet covered
    ('autogen-advanced', 'AutoGen advanced - multi-agent conversations, group chat, code execution, human-in-loop'),
    ('crewai-advanced', 'CrewAI advanced - crews, agents, tasks, tools, processes, hierarchical, memory'),
    ('phidata-agents', 'Phidata agents - structured agents, tool integration, memory, knowledge, playground'),
    ('smolagents', 'SmolAgents - HuggingFace agents, code agents, tool calling, multi-agent, simple API'),
    ('agno-framework', 'Agno framework - high-performance agents, multimodal, teams, knowledge, reasoning'),
    # Advanced prompt collections
    ('system-prompts-library', 'System prompts library - role definitions, persona design, constraint patterns, examples'),
    ('chain-of-thought-advanced', 'Chain of thought advanced - zero-shot CoT, self-consistency, tree of thought, program of thought'),
    ('structured-output-patterns', 'Structured output patterns - JSON schema, Pydantic, instructor, retry logic, validation'),
    ('tool-use-patterns', 'Tool use patterns - parallel calls, sequential, error handling, result synthesis, chaining'),
    # Infrastructure-as-code tools not yet covered
    ('pulumi-advanced', 'Pulumi advanced - ComponentResource, StackReference, Automation API, Kubernetes, crosswalk'),
    ('crossplane-advanced', 'Crossplane advanced - XRDs, compositions, providers, claims, managed resources'),
    ('argo-workflows-advanced', 'Argo Workflows advanced - DAG, steps, templates, artifacts, parameters, loops, retries'),
    ('tekton-pipelines', 'Tekton pipelines - tasks, pipelines, triggers, workspaces, results, Tekton Hub'),
    # Data engineering tools
    ('dbt-advanced', 'dbt advanced - macros, packages, tests, incremental, seeds, snapshots, metrics, exposures'),
    ('great-expectations-advanced', 'Great Expectations advanced - data docs, checkpoints, custom expectations, suites'),
    ('apache-flink-advanced', 'Apache Flink advanced - DataStream API, Table API, CEP, state backends, checkpointing'),
    ('delta-lake-advanced', 'Delta Lake advanced - ACID transactions, time travel, schema evolution, Z-ordering, liquid'),
    ('iceberg-advanced', 'Apache Iceberg advanced - table spec, partitioning, snapshots, catalog, Flink/Spark integration'),
    # Observability not yet covered
    ('opentelemetry-advanced', 'OpenTelemetry advanced - custom instrumentation, processors, exporters, sampling, OTLP'),
    ('datadog-advanced', 'Datadog advanced - APM, synthetics, logs, dashboards, monitors, SLOs, custom metrics'),
    ('new-relic-advanced', 'New Relic advanced - NRQL, distributed tracing, browser, mobile, NerdGraph, alerts'),
    ('honeycomb-observability', 'Honeycomb observability - high-cardinality, BubbleUp, SLOs, derived columns, traces'),
    ('axiom-logging', 'Axiom logging - serverless logging, APL query, datasets, monitors, streams, webhooks'),
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
