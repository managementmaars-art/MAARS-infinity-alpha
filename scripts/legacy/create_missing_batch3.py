import os

base = 'c:/Users/Yaleena Yara/MAARS-Command/.claude/skills'

skills = [
    # Vercel AI SDK
    ('add-function-examples', 'Add function examples - add usage examples for AI SDK functions and tools'),
    ('add-provider-package', 'Add provider package - add a new AI provider package to the Vercel AI SDK'),
    ('adr-skill', 'ADR skill - create Architecture Decision Records for technical decisions'),
    ('capture-api-response-test-fixture', 'Capture API response test fixture - capture and store API responses as test fixtures'),
    ('develop-ai-functions-example', 'Develop AI functions example - build example AI function implementations with the AI SDK'),
    ('island-rescue', 'Island rescue - recover and fix isolated or broken code islands in a codebase'),
    ('list-npm-package-content', 'List npm package content - inspect and list the contents of npm packages'),
    ('update-provider-models', 'Update provider models - update AI provider model lists and configurations'),
    # Apify
    ('apify-generate-output-schema', 'Apify generate output schema - generate output schemas for Apify actors'),
    # Auth0
    ('auth0-android', 'Auth0 Android - implement Auth0 authentication in Android apps with Kotlin/Java SDK'),
    ('auth0-angular', 'Auth0 Angular - integrate Auth0 into Angular applications with Auth0 Angular SDK'),
    ('auth0-aspnetcore-api', 'Auth0 ASP.NET Core API - secure ASP.NET Core APIs with Auth0 JWT authentication'),
    ('auth0-express', 'Auth0 Express - add Auth0 authentication to Express.js applications'),
    ('auth0-fastify', 'Auth0 Fastify - integrate Auth0 with Fastify web framework applications'),
    ('auth0-fastify-api', 'Auth0 Fastify API - secure Fastify APIs with Auth0 JWT validation'),
    ('auth0-mfa', 'Auth0 MFA - configure multi-factor authentication with Auth0 platform'),
    ('auth0-migration', 'Auth0 migration - migrate users and auth systems to Auth0 platform'),
    ('auth0-nextjs', 'Auth0 Next.js - integrate Auth0 authentication into Next.js applications'),
    ('auth0-nuxt', 'Auth0 Nuxt - add Auth0 authentication to Nuxt.js Vue applications'),
    ('auth0-quickstart', 'Auth0 quickstart - get started quickly with Auth0 authentication setup'),
    ('auth0-react', 'Auth0 React - implement Auth0 authentication in React applications'),
    ('auth0-react-native', 'Auth0 React Native - add Auth0 authentication to React Native mobile apps'),
    ('auth0-vue', 'Auth0 Vue - integrate Auth0 authentication into Vue.js applications'),
    # Callstack
    ('github-actions', 'GitHub Actions - create and manage GitHub Actions CI/CD workflows'),
    ('react-native-brownfield-migration', 'React Native brownfield migration - migrate existing native apps to include React Native'),
    ('upgrading-react-native', 'Upgrading React Native - upgrade React Native to newer versions with breaking changes'),
    ('validate-skills', 'Validate skills - validate and test AI agent skills for correctness and quality'),
    # ClickHouse
    ('clickhouse-best-practices', 'ClickHouse best practices - optimize ClickHouse queries, schema, and cluster configuration'),
    # Firebase
    ('developing-genkit-dart', 'Developing Genkit Dart - build AI flows with Firebase Genkit in Dart/Flutter'),
    ('developing-genkit-go', 'Developing Genkit Go - build AI flows and agents with Firebase Genkit in Go'),
    ('developing-genkit-js', 'Developing Genkit JS - build AI flows and agents with Firebase Genkit in JavaScript'),
    ('example-command', 'Example command - reference implementation of a Claude Code slash command'),
    ('example-skill', 'Example skill - reference implementation of an AI agent skill'),
    ('firebase-app-hosting-basics', 'Firebase App Hosting basics - deploy Next.js and Angular apps with Firebase App Hosting'),
    ('firebase-auth-basics', 'Firebase Auth basics - implement authentication with Firebase Auth SDK'),
    ('firebase-basics', 'Firebase basics - get started with Firebase project setup and core services'),
    ('firebase-data-connect', 'Firebase Data Connect - build apps with Firebase Data Connect and PostgreSQL'),
    ('firebase-firestore-basics', 'Firebase Firestore basics - read and write data with Cloud Firestore SDK'),
    ('firebase-firestore-enterprise-native-mode', 'Firebase Firestore enterprise native mode - use Firestore in native mode for enterprise scale'),
    ('firebase-firestore-standard', 'Firebase Firestore standard - standard Firestore patterns for web and mobile apps'),
    ('firebase-hosting-basics', 'Firebase Hosting basics - deploy web apps and static sites with Firebase Hosting'),
    ('firebase-local-env-setup', 'Firebase local env setup - set up Firebase Emulator Suite for local development'),
    ('firestore-security-rules-auditor', 'Firestore security rules auditor - audit and improve Firestore security rules'),
    # Misc
    ('from-the-other-side-vega', 'From the other side Vega - Vega visualization library integration and chart generation'),
    ('sync-agents', 'Sync agents - synchronize state and data between multiple AI agents in workflows'),
    # GetSentry
    ('sentry-cocoa-sdk', 'Sentry Cocoa SDK - integrate Sentry error tracking into iOS/macOS apps with Cocoa SDK'),
    ('sentry-create-alert', 'Sentry create alert - create Sentry alert rules for error and performance monitoring'),
    ('sentry-dotnet-sdk', 'Sentry .NET SDK - integrate Sentry into .NET applications for error tracking'),
    ('sentry-fix-issues', 'Sentry fix issues - analyze and fix issues surfaced in Sentry error tracking'),
    ('sentry-go-sdk', 'Sentry Go SDK - add Sentry error tracking and performance monitoring to Go apps'),
    ('sentry-ios-swift-setup', 'Sentry iOS Swift setup - integrate Sentry into iOS Swift applications'),
    ('sentry-nextjs-sdk', 'Sentry Next.js SDK - add Sentry monitoring to Next.js applications'),
    ('sentry-otel-exporter-setup', 'Sentry OpenTelemetry exporter setup - export OpenTelemetry data to Sentry'),
    ('sentry-pr-code-review', 'Sentry PR code review - review pull requests for Sentry SDK quality and correctness'),
    ('sentry-python-sdk', 'Sentry Python SDK - integrate Sentry into Python applications for error tracking'),
    ('sentry-python-setup', 'Sentry Python setup - set up Sentry error monitoring in Python projects'),
    ('sentry-react-native-sdk', 'Sentry React Native SDK - add Sentry to React Native apps for crash reporting'),
    ('sentry-react-native-setup', 'Sentry React Native setup - configure Sentry in React Native projects'),
    ('sentry-react-sdk', 'Sentry React SDK - integrate Sentry into React web applications'),
    ('sentry-react-setup', 'Sentry React setup - set up Sentry monitoring in React applications'),
    ('sentry-ruby-sdk', 'Sentry Ruby SDK - add Sentry error tracking to Ruby and Rails applications'),
    ('sentry-ruby-setup', 'Sentry Ruby setup - configure Sentry in Ruby projects and gems'),
    ('sentry-sdk-skill-creator', 'Sentry SDK skill creator - create new Sentry SDK integration skills'),
    ('sentry-setup-ai-monitoring', 'Sentry setup AI monitoring - monitor AI/LLM applications with Sentry'),
    ('sentry-setup-logging', 'Sentry setup logging - configure structured logging integration with Sentry'),
    ('sentry-setup-metrics', 'Sentry setup metrics - configure custom metrics and measurements in Sentry'),
    ('sentry-setup-tracing', 'Sentry setup tracing - configure distributed tracing and performance monitoring in Sentry'),
    ('sentry-svelte-sdk', 'Sentry Svelte SDK - integrate Sentry into Svelte and SvelteKit applications'),
    # Stripe
    ('stripe-best-practices', 'Stripe best practices - implement Stripe payments securely, webhooks, idempotency, error handling'),
    # GitHub Copilot
    ('suggest-awesome-github-copilot-prompts', 'Suggest awesome GitHub Copilot prompts - discover and share effective Copilot prompts'),
    # Misc
    ('create-oo-component-documentation', 'Create OO component documentation - document object-oriented components with examples'),
    ('create-web-form', 'Create web form - build accessible HTML web forms with validation and submission'),
    ('mcp-configure', 'MCP configure - configure MCP servers, settings, and tool permissions'),
    ('update-oo-component-documentation', 'Update OO component documentation - update and maintain OO component docs'),
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

print(f'Created: {created}')
print(f'Skipped: {skipped}')
