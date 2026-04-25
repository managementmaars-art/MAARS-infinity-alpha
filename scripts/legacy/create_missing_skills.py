import os

base = 'c:/Users/Yaleena Yara/MAARS-Command/.claude/skills'

skills = [
    ('agent-configuration', 'Agent configuration - configure AI agents, set parameters, manage agent settings and behaviors'),
    ('agent-ui', 'Agent UI - build user interfaces for AI agents, chat interfaces, agent dashboards and controls'),
    ('agentic-development-principles', 'Agentic development principles - best practices for building autonomous AI agent systems'),
    ('agentic-workflow', 'Agentic workflow - design and implement workflows driven by autonomous AI agents'),
    ('ai-automation-workflows', 'AI automation workflows - automate business processes using AI models and orchestration'),
    ('ai-social-media-content', 'AI social media content - generate and manage social media posts, images, captions with AI'),
    ('arrange', 'Arrange - organize, sort, and structure data, files, content, and code systematically'),
    ('audit', 'Audit - review code, systems, security, and processes for issues and compliance'),
    ('authentication-setup', 'Authentication setup - implement auth flows, OAuth, JWT, sessions, multi-factor authentication'),
    ('azure-ai', 'Azure AI - Microsoft Azure AI services, Cognitive Services, OpenAI on Azure, AI Studio'),
    ('azure-enterprise-infra-planner', 'Azure enterprise infrastructure planner - design and plan large-scale Azure infrastructure'),
    ('azure-hosted-copilot-sdk', 'Azure hosted Copilot SDK - build Copilot experiences on Azure, Teams AI library'),
    ('azure-messaging', 'Azure messaging - Service Bus, Event Hub, Event Grid, Queue Storage messaging patterns'),
    ('azure-observability', 'Azure observability - Monitor, App Insights, Log Analytics, dashboards, alerts'),
    ('backend-testing', 'Backend testing - unit tests, integration tests, API tests, mocking, test coverage'),
    ('backlink-analyzer', 'Backlink analyzer - analyze backlinks, domain authority, link building, SEO link profile'),
    ('baoyu-article-illustrator', 'Article illustrator - generate illustrations and images to accompany articles and content'),
    ('baoyu-comic', 'Comic creator - create comic strips, panels, visual storytelling with AI-generated images'),
    ('baoyu-compress-image', 'Image compressor - compress and optimize images for web, reduce file sizes'),
    ('baoyu-cover-image', 'Cover image generator - create cover images for articles, blogs, social media'),
    ('baoyu-danger-gemini-web', 'Gemini web browsing - use Gemini AI for web search and browsing tasks'),
    ('baoyu-danger-x-to-markdown', 'X to markdown - convert X (Twitter) threads and posts to markdown format'),
    ('baoyu-format-markdown', 'Format markdown - clean, format, and improve markdown documents and content'),
    ('baoyu-image-gen', 'Image generation - generate images using AI models from text descriptions'),
    ('baoyu-infographic', 'Infographic creator - design data visualizations and infographics from content'),
    ('baoyu-markdown-to-html', 'Markdown to HTML - convert markdown documents to styled HTML web pages'),
    ('baoyu-post-to-wechat', 'Post to WeChat - format and publish content to WeChat articles and moments'),
    ('baoyu-post-to-x', 'Post to X - create and publish posts to X (Twitter), thread creation'),
    ('baoyu-slide-deck', 'Slide deck creator - generate presentation slide decks from content and outlines'),
    ('baoyu-url-to-markdown', 'URL to markdown - fetch web pages and convert content to clean markdown'),
    ('baoyu-xhs-images', 'Xiaohongshu images - create images optimized for Xiaohongshu (RedNote) platform'),
    ('bmad-orchestrator', 'BMAD orchestrator - orchestrate multi-agent workflows using the BMAD methodology'),
    ('changelog-maintenance', 'Changelog maintenance - write and maintain changelogs, release notes, version history'),
    ('chat-ui', 'Chat UI - build chat interfaces, message components, real-time chat frontend development'),
    ('china-stock-analysis', 'China stock analysis - analyze Chinese stock markets, A-shares, financial reports'),
    ('code-refactoring', 'Code refactoring - restructure existing code, improve quality without changing behavior'),
    ('code-review', 'Code review - review pull requests, provide feedback, identify bugs and improvements'),
    ('codebase-search', 'Codebase search - search and navigate large codebases, find relevant code patterns'),
    ('convex-create-component', 'Convex create component - build reusable Convex components, functions and queries'),
    ('convex-migration-helper', 'Convex migration helper - migrate data and schema in Convex database projects'),
    ('convex-performance-audit', 'Convex performance audit - analyze and optimize Convex query and function performance'),
    ('convex-quickstart', 'Convex quickstart - get started with Convex backend, setup project, deploy functions'),
    ('convex-setup-auth', 'Convex setup auth - configure authentication in Convex with Clerk, Auth0 or custom'),
    ('copilot-coding-agent', 'Copilot coding agent - use GitHub Copilot as an autonomous coding agent'),
    ('create-auth-skill', 'Create auth skill - build authentication skill templates for AI agents and systems'),
    ('database-schema-design', 'Database schema design - design relational and NoSQL database schemas and models'),
    ('debugging', 'Debugging - debug code, trace errors, fix bugs, analyze stack traces and logs'),
    ('deploy-to-vercel', 'Deploy to Vercel - deploy web applications to Vercel, configure builds and domains'),
    ('electron', 'Electron - build cross-platform desktop apps with Electron, IPC, packaging'),
    ('environment-setup', 'Environment setup - configure development environments, dotenv, Docker, tooling'),
    ('file-organization', 'File organization - organize project files, folder structures, naming conventions'),
    ('firebase-ai-logic', 'Firebase AI logic - integrate AI features into Firebase apps, Vertex AI, Genkit'),
    ('firecrawl', 'Firecrawl - web scraping and crawling with Firecrawl API, extract structured data'),
    ('firecrawl-scrape', 'Firecrawl scrape - scrape individual web pages with Firecrawl, extract content'),
    ('flutter-animations', 'Flutter animations - implement animations in Flutter, AnimationController, Tween, curves'),
    ('frontend-design-system', 'Frontend design system - build and maintain design systems, component libraries, tokens'),
    ('genkit', 'Genkit - Firebase Genkit AI framework, flows, models, plugins, deployment'),
    ('git-submodule', 'Git submodule - manage Git submodules, add, update, sync nested repositories'),
    ('github-actions-docs', 'GitHub Actions docs - write and maintain GitHub Actions workflow documentation'),
    ('grill-me', 'Grill me - test knowledge, quiz, challenge understanding of topics and concepts'),
    ('gws-calendar-agenda', 'Google Workspace Calendar agenda - read and summarize Google Calendar events and agenda'),
    ('gws-calendar-insert', 'Google Workspace Calendar insert - create and insert events into Google Calendar'),
    ('gws-drive-upload', 'Google Workspace Drive upload - upload files and documents to Google Drive'),
    ('gws-gmail-send', 'Google Workspace Gmail send - compose and send emails via Gmail API'),
    ('gws-gmail-triage', 'Google Workspace Gmail triage - sort, label, and prioritize Gmail inbox messages'),
    ('gws-gmail-watch', 'Google Workspace Gmail watch - watch Gmail for new messages and trigger actions'),
    ('gws-shared', 'Google Workspace shared - shared utilities and helpers across Google Workspace skills'),
    ('gws-sheets-append', 'Google Workspace Sheets append - append rows and data to Google Sheets'),
    ('gws-sheets-read', 'Google Workspace Sheets read - read data from Google Sheets, parse and process'),
    ('humanizer-zh', 'Chinese humanizer - make AI-generated Chinese text sound more natural and human'),
    ('javascript-sdk', 'JavaScript SDK - build and use JavaScript SDKs, client libraries, API wrappers'),
    ('jeo', 'Jeo - geographic data processing, spatial analysis, map-based visualizations'),
    ('landing-page-design', 'Landing page design - design and build high-converting landing pages'),
    ('lark-base', 'Lark Base - work with Lark/Feishu Base databases, records, views, and fields'),
    ('lark-calendar', 'Lark Calendar - manage Lark/Feishu calendar events, meetings, scheduling'),
    ('lark-contact', 'Lark Contact - manage Lark/Feishu contacts, users, departments, org structure'),
    ('lark-doc', 'Lark Doc - create and edit Lark/Feishu documents, rich text, collaboration'),
    ('lark-drive', 'Lark Drive - manage files in Lark/Feishu Drive, upload, download, organize'),
    ('lark-event', 'Lark Event - Lark/Feishu event subscriptions, webhooks, and real-time triggers'),
    ('lark-im', 'Lark IM - Lark/Feishu instant messaging, bots, send messages, group chats'),
    ('lark-mail', 'Lark Mail - send and manage emails through Lark/Feishu Mail integration'),
    ('lark-minutes', 'Lark Minutes - access and manage Lark/Feishu meeting minutes and transcripts'),
    ('lark-openapi-explorer', 'Lark OpenAPI explorer - explore and test Lark/Feishu OpenAPI endpoints'),
    ('lark-shared', 'Lark shared - shared utilities and authentication helpers for Lark/Feishu skills'),
    ('lark-sheets', 'Lark Sheets - work with Lark/Feishu Sheets spreadsheets, data, formulas'),
    ('lark-skill-maker', 'Lark skill maker - create and publish skills for the Lark/Feishu platform'),
    ('lark-task', 'Lark Task - manage tasks in Lark/Feishu, create, assign, track completion'),
    ('lark-vc', 'Lark VC - Lark/Feishu video conferencing, meetings, rooms, recordings'),
    ('lark-whiteboard', 'Lark Whiteboard - collaborate on Lark/Feishu whiteboards, diagrams, sketches'),
    ('lark-wiki', 'Lark Wiki - manage knowledge base in Lark/Feishu Wiki, pages, spaces'),
    ('lark-workflow-meeting-summary', 'Lark workflow meeting summary - automate meeting summaries in Lark/Feishu workflows'),
    ('lark-workflow-standup-report', 'Lark workflow standup report - automate daily standup reports in Lark/Feishu'),
    ('log-analysis', 'Log analysis - parse, analyze, and extract insights from application and system logs'),
    ('looker-studio-bigquery', 'Looker Studio BigQuery - connect Looker Studio to BigQuery, build reports and dashboards'),
    ('marketing-skills-collection', 'Marketing skills collection - comprehensive collection of marketing skills and frameworks'),
    ('mastra', 'Mastra - build AI agents and workflows with the Mastra TypeScript framework'),
    ('mobile-android-design', 'Mobile Android design - design Android UIs, Material Design, Jetpack Compose patterns'),
    ('mobile-ios-design', 'Mobile iOS design - design iOS UIs, Human Interface Guidelines, SwiftUI patterns'),
    ('monitoring-observability', 'Monitoring and observability - set up metrics, logging, tracing, alerting for systems'),
    ('nestjs-best-practices', 'NestJS best practices - structure NestJS applications, modules, guards, interceptors'),
    ('next-upgrade', 'Next.js upgrade - migrate Next.js applications to newer versions, resolve breaking changes'),
    ('npm-git-install', 'NPM Git install - install npm packages directly from Git repositories and branches'),
    ('nuxt', 'Nuxt - build Vue.js applications with Nuxt framework, SSR, SSG, routing, plugins'),
    ('oh-my-codex', 'Oh My Codex - OpenAI Codex-based coding assistance, code generation patterns'),
    ('ohmg', 'OHMG - Oh My Generative - generative AI art and media creation workflows'),
    ('omc', 'OMC - orchestrate multi-agent coding tasks and development workflows'),
    ('openclaw-secure-linux-cloud', 'OpenClaw secure Linux cloud - deploy secure Linux environments on cloud providers'),
    ('opencontext', 'OpenContext - open context protocols for sharing knowledge across AI tools'),
    ('opensource-guide-coach', 'Open source guide coach - guide contributors through open source project contribution'),
    ('optimize', 'Optimize - optimize code performance, algorithms, database queries, and system efficiency'),
    ('overdrive', 'Overdrive - push systems to maximum performance, aggressive optimization strategies'),
    ('pattern-detection', 'Pattern detection - identify patterns in code, data, behavior, and system design'),
    ('performance-optimization', 'Performance optimization - improve application speed, memory usage, and scalability'),
    ('pexo-agent', 'Pexo agent - Pexo AI agent workflows and automation patterns'),
    ('plannotator', 'Plannotator - annotate and refine plans, add context and structure to project plans'),
    ('playwright-cli', 'Playwright CLI - use Playwright command line tools for browser automation and testing'),
    ('postgresql-table-design', 'PostgreSQL table design - design efficient PostgreSQL tables, indexes, constraints'),
    ('pptx-presentation-builder', 'PPTX presentation builder - build PowerPoint presentations programmatically'),
    ('proactive-agent', 'Proactive agent - build agents that take initiative and act without explicit prompting'),
    ('product-hunt-launch', 'Product Hunt launch - plan and execute a successful Product Hunt launch campaign'),
    ('prompt-repetition', 'Prompt repetition - use repeated prompting patterns for consistent AI outputs'),
    ('python-executor', 'Python executor - execute Python code, sandboxed runtime, script automation'),
    ('python-sdk', 'Python SDK - build and use Python SDKs, client libraries, API integrations'),
    ('ralph', 'Ralph - IT asset management and DCIM with Ralph open source platform'),
    ('react-components', 'React components - build reusable React components, hooks, context, composition patterns'),
    ('react-native-best-practices', 'React Native best practices - structure React Native apps, performance, navigation'),
    ('readme-i18n', 'README i18n - internationalize README files and documentation for multiple languages'),
    ('release-skills', 'Release skills - manage software releases, versioning, changelogs, deployment pipelines'),
    ('remotion-video-production', 'Remotion video production - produce videos programmatically with Remotion React framework'),
    ('responsive-design', 'Responsive design - build layouts that work across all screen sizes and devices'),
    ('running-claude-code-via-litellm-copilot', 'Run Claude Code via LiteLLM Copilot - use Claude Code with LiteLLM proxy'),
    ('secure-linux-web-hosting', 'Secure Linux web hosting - harden Linux servers for secure web hosting'),
    ('seedance2-api', 'Seedance2 API - integrate with Seedance2 video generation and media API'),
    ('skill-standardization', 'Skill standardization - standardize skill formats, naming, and documentation structure'),
    ('skill-vetter', 'Skill vetter - review and validate AI skills for quality and correctness'),
    ('skills-cli', 'Skills CLI - command line interface for managing and installing AI agent skills'),
    ('slack', 'Slack - Slack API integration, bots, slash commands, workflows, Block Kit'),
    ('speech-to-text', 'Speech to text - transcribe audio to text, whisper, voice recognition, STT APIs'),
    ('sprint-retrospective', 'Sprint retrospective - facilitate and document agile sprint retrospectives'),
    ('standup-meeting', 'Standup meeting - run and document daily standup meetings, async standups'),
    ('state-management', 'State management - manage application state, Redux, Zustand, Pinia, context patterns'),
    ('stitch-design', 'Stitch design - Google Stitch design tool integration for UI design workflows'),
    ('summarize', 'Summarize - summarize long documents, articles, meetings, and conversations'),
    ('supabase-postgres-best-practices', 'Supabase PostgreSQL best practices - optimize Supabase with PostgreSQL patterns'),
    ('swiftui-pro', 'SwiftUI pro - advanced SwiftUI development, animations, custom views, performance'),
    ('system-environment-setup', 'System environment setup - configure OS, development tools, environment variables'),
    ('task-estimation', 'Task estimation - estimate development effort, story points, time planning for tasks'),
    ('task-planning', 'Task planning - break down work into tasks, prioritize, create actionable plans'),
    ('tdd', 'TDD - test-driven development, write tests first, red-green-refactor cycle'),
    ('testing-strategies', 'Testing strategies - choose and implement testing approaches for different contexts'),
    ('tools-ui', 'Tools UI - build user interfaces for developer tools, admin panels, dashboards'),
    ('typeset', 'Typeset - format and typeset documents, apply consistent typography and layout'),
    ('tzst', 'TZST - timezone and scheduling tools, time zone conversion and meeting scheduling'),
    ('ui-component-patterns', 'UI component patterns - reusable UI component design patterns and best practices'),
    ('use-dom', 'Use DOM - manipulate the browser DOM, vanilla JavaScript DOM operations'),
    ('use-my-browser', 'Use my browser - control and automate the browser for tasks and automation'),
    ('user-guide-writing', 'User guide writing - write clear user guides, tutorials, onboarding documentation'),
    ('vercel-react-native-skills', 'Vercel React Native skills - deploy React Native web apps on Vercel'),
    ('vibe-kanban', 'Vibe Kanban - Kanban board for vibe coding projects, task tracking'),
    ('videoagent-video-studio', 'Video agent video studio - AI-powered video creation and editing agent'),
    ('vite', 'Vite - build frontend projects with Vite, configure plugins, optimize build'),
    ('vueuse-functions', 'VueUse functions - use VueUse composable library for Vue.js development'),
    ('web-accessibility', 'Web accessibility - implement WCAG guidelines, ARIA, accessible components'),
    ('web-design-guidelines', 'Web design guidelines - apply web design standards, consistency, usability patterns'),
    ('web-search', 'Web search - perform web searches, retrieve and summarize information from the internet'),
    ('widgets-ui', 'Widgets UI - build embeddable widgets, iframe components, shareable UI modules'),
    ('xdrop', 'Xdrop - file sharing and drop upload utility, drag-and-drop file transfers'),
    ('xget', 'Xget - download and fetch content from X (Twitter) posts and media'),
]

created = 0
skipped = 0
for name, desc in skills:
    d = os.path.join(base, name)
    if os.path.exists(d):
        skipped += 1
        continue
    os.makedirs(d, exist_ok=True)
    title = name.replace('-', ' ').title()
    content = f"""---
name: {name}
description: {desc}
---

# {title}

## Overview
{desc}

## Usage
Use this skill to leverage {title.lower()} capabilities in your agent workflows.

## Key Capabilities
- Core {title.lower()} operations
- Integration with related tools and APIs
- Best practice patterns and examples

## Best Practices
1. Follow official documentation and guidelines
2. Handle errors and edge cases gracefully
3. Use environment variables for credentials
4. Test thoroughly before production use
5. Monitor and log for observability
"""
    with open(os.path.join(d, 'SKILL.md'), 'w') as f:
        f.write(content)
    created += 1

print(f'Created: {created} skills')
print(f'Skipped (already exist): {skipped}')
