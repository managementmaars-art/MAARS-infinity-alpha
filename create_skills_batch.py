
import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # MiniMax skills
    ('minimax-frontend', 'MiniMax AI frontend development - React/Next.js UI for MiniMax APIs, chat interfaces'),
    ('minimax-fullstack', 'MiniMax AI fullstack - backend and frontend integration, API routes, streaming responses'),
    ('minimax-android', 'MiniMax AI for Android - mobile SDK integration, Kotlin/Java, voice and chat features'),
    ('minimax-ios', 'MiniMax AI for iOS - Swift SDK, SwiftUI integration, voice chat, streaming responses'),
    ('minimax-shader', 'MiniMax AI shader generation - GLSL/HLSL shaders via AI, visual effects, GPU programming'),
    ('minimax-gif-maker', 'MiniMax GIF maker - animated GIF creation, video-to-GIF, frame extraction and assembly'),
    ('minimax-pdf', 'MiniMax PDF processing - document understanding, extraction, PDF-based Q&A and analysis'),
    ('minimax-pptx', 'MiniMax PowerPoint generation - AI-driven slide creation, presentations from content'),
    # Composio skills
    ('composio-github', 'Composio GitHub integration - issues, PRs, repos, actions via Composio tools and agents'),
    ('composio-slack', 'Composio Slack integration - messages, channels, reactions, file sharing via agents'),
    ('composio-gmail', 'Composio Gmail integration - email send, read, filter, label, draft via AI agents'),
    ('composio-notion', 'Composio Notion integration - pages, databases, blocks, properties via agent actions'),
    ('composio-linear', 'Composio Linear integration - issues, projects, cycles, comments via agent automation'),
    ('composio-jira', 'Composio Jira integration - tickets, sprints, boards, transitions via agent tools'),
    ('composio-salesforce', 'Composio Salesforce integration - leads, contacts, opportunities, CRM via agents'),
    ('composio-hubspot', 'Composio HubSpot integration - contacts, deals, pipelines, emails via agent automation'),
    ('composio-sheets', 'Composio Google Sheets integration - read, write, format, formulas via AI agents'),
    ('composio-zapier', 'Composio Zapier integration - trigger zaps, webhook actions, workflow automation via agents'),
    # OpenAI platform skills
    ('openai-assistants', 'OpenAI Assistants API - create assistants, threads, runs, file search, code interpreter'),
    ('openai-realtime', 'OpenAI Realtime API - WebSocket audio streaming, voice conversations, function calling'),
    ('openai-batch', 'OpenAI Batch API - bulk requests, async processing, cost reduction for large workloads'),
    ('openai-fine-tuning', 'OpenAI fine-tuning - prepare datasets, fine-tune models, evaluate, deploy custom models'),
    ('openai-vision', 'OpenAI Vision - image analysis, GPT-4V, multi-modal inputs, structured image data'),
    ('openai-embeddings', 'OpenAI Embeddings - text-embedding-3, semantic search, RAG, vector similarity'),
    ('openai-moderation', 'OpenAI Moderation API - content filtering, safety classification, policy enforcement'),
    ('openai-structured-output', 'OpenAI Structured Outputs - JSON schema enforcement, guaranteed output format'),
    # Claude official plugin skills
    ('claude-computer-use', 'Claude computer use - desktop automation, screenshot, click, type, browser control'),
    ('claude-code-execution', 'Claude code execution - sandboxed Python, data analysis, chart generation, computation'),
    ('claude-web-search', 'Claude web search - real-time web search, source citation, current events research'),
    ('claude-files-docs', 'Claude files and docs - document upload, PDF analysis, large file processing'),
    ('claude-artifacts', 'Claude Artifacts - interactive HTML/JS/React artifacts, code previews, live demos'),
    ('claude-extended-thinking', 'Claude extended thinking - deep reasoning, chain-of-thought, complex problem solving'),
    ('claude-prompt-caching', 'Claude prompt caching - cache prefixes, reduce costs, speed up repeated context'),
    ('claude-streaming', 'Claude streaming - SSE streaming, token-by-token output, real-time generation'),
    ('claude-tool-use', 'Claude tool use - function calling, tool definitions, parallel tools, result handling'),
    ('claude-vision-analysis', 'Claude vision analysis - image understanding, chart reading, document OCR, screenshots'),
    ('claude-batch-api', 'Claude Batch API - bulk message processing, async jobs, cost-efficient large workloads'),
    ('claude-agents-sdk', 'Claude Agents SDK - build agentic apps, multi-agent orchestration, tool loops'),
    ('claude-mcp-client', 'Claude MCP client - connect to MCP servers, use external tools, resource access'),
    ('claude-system-prompts', 'Claude system prompts - persona, instructions, context, persona shaping, guidelines'),
    ('claude-eval-testing', 'Claude evaluation and testing - model evals, benchmark, prompt testing, red-teaming'),
    ('claude-slack-bot', 'Claude Slack bot - deploy Claude in Slack, slash commands, DM, channel integration'),
    ('claude-github-actions', 'Claude in GitHub Actions - automated code review, PR comments, CI/CD integration'),
    ('claude-notion-integration', 'Claude Notion integration - generate pages, summarize databases, content creation'),
    ('claude-linear-integration', 'Claude Linear integration - create issues, triage bugs, sprint planning with Claude'),
    ('claude-playwright-testing', 'Claude Playwright testing - generate E2E tests, browser automation, test maintenance'),
    ('claude-jupyter-integration', 'Claude in Jupyter - notebook analysis, data science assistance, code cells'),
    ('claude-vscode-extension', 'Claude VS Code extension - code assistance, refactoring, explanation in editor'),
    ('claude-cursor-rules', 'Claude Cursor rules - .cursorrules setup, AI instructions for Cursor IDE integration'),
    ('claude-raycast-extension', 'Claude Raycast extension - macOS launcher integration, quick AI commands'),
    ('claude-zapier-integration', 'Claude Zapier integration - automate workflows, connect apps, trigger Claude actions'),
    # Hugging Face specific
    ('hf-inference', 'Hugging Face Inference API - run models via API, serverless inference, model endpoints'),
    ('hf-transformers', 'HuggingFace Transformers - load models, pipelines, tokenizers, generation configs'),
    ('hf-datasets', 'HuggingFace Datasets - load, stream, process, push datasets to Hub'),
    ('hf-spaces', 'HuggingFace Spaces - deploy Gradio/Streamlit apps, Docker Spaces, GPU Spaces'),
    ('hf-hub', 'HuggingFace Hub - push models, datasets, spaces, versioning, tokens, organizations'),
    ('hf-diffusers', 'HuggingFace Diffusers - stable diffusion, SDXL, ControlNet, image generation pipelines'),
    ('hf-peft', 'HuggingFace PEFT - LoRA, QLoRA, adapter methods, parameter-efficient fine-tuning'),
    ('hf-trl', 'HuggingFace TRL - RLHF, PPO, DPO, reward modeling, SFT trainer for LLMs'),
    # Vector DB skills
    ('pinecone-vectors', 'Pinecone vector database - upsert, query, namespaces, metadata filtering, hybrid search'),
    ('weaviate-db', 'Weaviate vector database - schema, objects, GraphQL, nearText, hybrid search, agents'),
    ('qdrant-db', 'Qdrant vector database - collections, points, payload filtering, sparse vectors, HNSW'),
    ('chroma-db', 'Chroma vector database - collections, embeddings, documents, metadata, persistent storage'),
    ('pgvector-db', 'pgvector PostgreSQL extension - vector columns, similarity search, IVFFlat, HNSW indexes'),
    # Developer productivity skills
    ('cursor-ai-rules', 'Cursor AI rules - .cursorrules configuration, project-specific AI instructions, context'),
    ('windsurf-rules', 'Windsurf AI editor rules - global rules, workspace rules, AI behavior configuration'),
    ('github-copilot-workspace', 'GitHub Copilot Workspace - AI-powered dev environment, task to code, PR automation'),
    ('linear-api-integration', 'Linear API integration - issues, projects, cycles, webhooks, GraphQL queries'),
    ('notion-api-integration', 'Notion API integration - pages, databases, blocks, search, OAuth, webhooks'),
    ('airtable-api', 'Airtable API integration - records, fields, views, formulas, automations, webhooks'),
    ('make-automation', 'Make (Integromat) automation - scenarios, modules, routers, webhooks, data transforms'),
    # Cloud infrastructure skills
    ('pulumi-iac', 'Pulumi infrastructure as code - Python/TypeScript/Go stacks, providers, state, automation API'),
    ('ansible-automation', 'Ansible automation - playbooks, roles, inventory, modules, AWX, Galaxy collections'),
    ('helm-kubernetes', 'Helm Kubernetes package manager - charts, values, templates, hooks, repositories'),
    ('argocd-gitops', 'ArgoCD GitOps - app definitions, sync policies, health checks, RBAC, notifications'),
    ('vault-secrets', 'HashiCorp Vault secrets management - KV, dynamic secrets, policies, auth methods, PKI'),
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
4. Log all API calls for debugging
5. Use environment variables for credentials

## Common Patterns
- Authentication and authorization setup
- Core API operations
- Error handling and retries
- Webhook and event handling
- Monitoring and logging

## Models to Use
- Architecture: claude-opus-4-6
- Implementation: claude-sonnet-4-6
- Quick lookups: claude-haiku-4-5-20251001
'''
    with open(os.path.join(d, 'SKILL.md'), 'w') as f:
        f.write(content)

print('Done:', len(skills), 'skills')
