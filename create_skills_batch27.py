
import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # Web frameworks - backend deep coverage
    ('symfony-framework', 'Symfony - components, bundles, DI container, Doctrine, security, forms, API Platform'),
    ('laravel-advanced', 'Laravel advanced - service container, facades, Eloquent, queues, broadcasting, Octane'),
    ('codeigniter', 'CodeIgniter 4 - MVC, shield auth, query builder, migrations, testing, CLI, localization'),
    ('cakephp', 'CakePHP - bake, ORM, routing, middleware, authentication, authorization, plugins'),
    ('yii-framework', 'Yii 2/3 - ActiveRecord, Gii code generator, rbac, caching, widgets, modules'),
    ('zend-laminas', 'Laminas (Zend) - MVC, service manager, event manager, i18n, form, filter, validator'),
    ('slim-php', 'Slim framework - routing, middleware, DI, PSR-7, PSR-15, request/response, testing'),
    ('lumen-microservice', 'Lumen microservice - routing, middleware, service providers, ORM, queues, validation'),
    ('adonisjs', 'AdonisJS - MVC, Lucid ORM, events, middleware, auth, validators, mailer, REPL'),
    ('hapi-nodejs', 'Hapi.js - plugins, authentication, validation, caching, server methods, lifecycle'),
    ('feathersjs', 'Feathers.js - services, hooks, real-time, adapters, authentication, schema, transports'),
    ('sails-js', 'Sails.js - Waterline ORM, blueprints, policies, custom responses, assets, sockets'),
    ('loopback-api', 'LoopBack 4 - decorators, repositories, datasources, interceptors, authentication, CLI'),
    ('strapi-cms', 'Strapi CMS - content types, plugins, middlewares, policies, lifecycle hooks, custom routes'),
    ('directus-api', 'Directus - data engine, extensions, flows, permissions, snapshots, SDK, webhooks'),
    ('keystone-js', 'KeystoneJS - schema, access control, hooks, virtual fields, session, GraphQL, REST'),
    ('payload-advanced', 'Payload CMS advanced - collections, globals, access control, hooks, local API, blocks'),
    # Sinatra/Ruby frameworks
    ('sinatra-ruby', 'Sinatra - routes, helpers, filters, templates, extensions, modular apps, Rack'),
    ('hanami-framework', 'Hanami - actions, views, repositories, entities, slices, persistence, validation'),
    ('roda-ruby', 'Roda - routing tree, plugins, middleware, assets, sessions, mail, testing'),
    # Python web frameworks
    ('tornado-python', 'Tornado - async handlers, IOLoop, websockets, authentication, template, process'),
    ('aiohttp-advanced', 'aiohttp advanced - client, server, middlewares, WebSocket, signals, testing'),
    ('sanic-framework', 'Sanic - routing, middleware, listeners, blueprints, streaming, websockets, workers'),
    ('falcon-api', 'Falcon - WSGI/ASGI, responders, hooks, middleware, media handlers, testing, CORS'),
    ('bottle-python', 'Bottle - single-file, routing, templates, plugins, WSGI, request/response, deployment'),
    ('pyramid-python', 'Pyramid - traversal, URL dispatch, views, events, security, Alchemy, testing'),
    ('cherrypy', 'CherryPy - dispatcher, tools, plugins, WSGI, apps, config, deployment, testing'),
    # Go web frameworks
    ('echo-golang', 'Echo - routing, middleware, data binding, validation, rendering, static files, testing'),
    ('beego-golang', 'Beego - MVC, ORM, cache, session, i18n, validation, swagger, bee tool'),
    ('buffalo-golang', 'Buffalo - generators, middleware, tasks, mailers, workers, auth, testing, deployment'),
    ('gorilla-mux', 'Gorilla toolkit - mux, websocket, sessions, handlers, csrf, schema, reverse proxy'),
    # Java/JVM frameworks
    ('spring-mvc', 'Spring MVC - controllers, REST, data binding, validation, interceptors, exception handling'),
    ('spring-batch', 'Spring Batch - jobs, steps, readers, writers, processors, retry, partitioning, testing'),
    ('spring-cloud-advanced', 'Spring Cloud advanced - gateway, config server, Eureka, circuit breaker, sleuth, stream'),
    ('spring-data-jpa-advanced', 'Spring Data JPA advanced - specifications, projections, auditing, custom repositories'),
    ('jakarta-ee', 'Jakarta EE - CDI, JPA, EJB, JAX-RS, servlet, security, transactions, messaging'),
    ('micronaut-advanced', 'Micronaut advanced - AOT, data, security, OpenAPI, GraalVM native, Kafka, MQTT'),
    ('quarkus-advanced', 'Quarkus advanced - panache, native, dev services, reactive, Camel, Hibernate ORM'),
    ('helidon', 'Helidon - SE reactive, MP microprofile, Nima virtual threads, OCI, tracing, metrics'),
    ('dropwizard', 'Dropwizard - bundles, health checks, commands, resources, hibernate, migrations, testing'),
    ('vert-x', 'Vert.x - event bus, verticles, HTTP, gRPC, reactive, reactive streams, cluster'),
    ('javalin', 'Javalin - lightweight, OpenAPI, WebSocket, plugins, validation, error mapping, roles'),
    ('http4s', 'http4s - purely functional, cats-effect, Ember, Blaze, middleware, testing, streaming'),
    ('play-framework', 'Play Framework - routing, actions, forms, templates, database, caching, testing'),
    # .NET frameworks
    ('aspnet-webapi', 'ASP.NET Web API - controllers, model binding, routing, filters, formatters, versioning'),
    ('grpc-dotnet', 'gRPC .NET - services, interceptors, authentication, streaming, health checks, reflection'),
    ('signalr-advanced', 'SignalR advanced - hubs, groups, backplane, scale out, authentication, streaming, filters'),
    ('orleans-advanced', 'Orleans advanced - grains, persistence, timers, reminders, streaming, cluster, testing'),
    ('dapr-dotnet', 'Dapr .NET SDK - service invocation, pub/sub, state, bindings, actors, secrets, workflows'),
    ('masstransit-advanced', 'MassTransit advanced - consumers, sagas, activities, filters, transport config, testing'),
    ('mediatr-advanced', 'MediatR advanced - handlers, pipelines, notifications, streams, behaviors, validation'),
    # Rust web frameworks
    ('actix-web-patterns', 'Actix-web patterns - app data, guards, error handling, middleware, static files, CORS'),
    ('axum-advanced', 'Axum advanced - state, layers, nested routers, extractors, websockets, server-sent events'),
    ('rocket-advanced', 'Rocket advanced - fairings, guards, catchers, forms, state, databases, testing'),
    ('tide-rust', 'Tide - middleware, state, routing, listener, TLS, testing, sessions, CORS'),
    ('poem-web', 'Poem - OpenAPI, extractors, middleware, WebSocket, SSE, testing, endpoints'),
    # Node.js patterns
    ('express-advanced', 'Express advanced - custom middleware, error handling, proxy, static, security, testing'),
    ('koa-advanced', 'Koa.js advanced - context, middleware composition, error handling, router, body parser'),
    ('fastify-advanced', 'Fastify advanced - plugins, decorators, hooks, schema, serialization, TypeScript, testing'),
    ('hono-advanced', 'Hono advanced - RPC, testing, middleware, JSX, adapter, static, validation, OpenAPI'),
    ('nitro-server', 'Nitro server - universal deployment, API routes, plugins, storage, cache, dev tools'),
    ('h3-framework', 'h3 framework - handlers, utils, events, body, cookies, headers, redirect, proxy'),
    # Elixir/Phoenix patterns
    ('phoenix-channels', 'Phoenix Channels - topics, presence, PubSub, authentication, messages, reconnect'),
    ('absinthe-graphql', 'Absinthe GraphQL - schema, resolvers, subscriptions, middleware, dataloader, relay'),
    ('surface-framework', 'Surface - component framework, data, props, events, slots, LiveView integration'),
    # Frontend frameworks deep
    ('react-advanced', 'React advanced - concurrent mode, transitions, deferred values, external stores, offscreen'),
    ('vue-advanced', 'Vue 3 advanced - Composition API, composables, custom renderers, compile macros, Vapor'),
    ('angular-advanced', 'Angular advanced - standalone components, deferred loading, signals, SSR, hybrid rendering'),
    ('svelte-advanced', 'Svelte advanced - runes, snippets, enhanced stores, compile options, SSR, SvelteKit'),
    ('solid-advanced', 'SolidJS advanced - fine-grained reactivity, stores, context, resources, error boundaries'),
    ('qwik-advanced', 'Qwik advanced - resumability, optimizer, tasks, server functions, Qwik City, loader'),
    ('astro-advanced', 'Astro advanced - view transitions, middleware, actions, content collections, DB, recast'),
    ('nuxt-advanced', 'Nuxt 3 advanced - server routes, nitro, composables, modules, layers, hybrid rendering'),
    ('remix-advanced-patterns', 'Remix advanced - actions, loaders, error boundaries, fetchers, optimistic UI, Vite'),
    ('gatsby-advanced', 'Gatsby 5 - Slice API, Head API, Partial Hydration, DSG, image plugin, sourcing'),
    ('nextjs-advanced', 'Next.js 15 advanced - PPR, Turbopack, server actions, after, form, connection'),
    # CSS frameworks/tools
    ('bootstrap-advanced', 'Bootstrap 5 advanced - utility API, custom properties, Sass, components, JS plugins'),
    ('foundation-css', 'Foundation - grid, flex, components, motion UI, form validation, accessibility'),
    ('bulma-css', 'Bulma CSS - modifiers, columns, components, responsiveness, customization, theming'),
    ('materialize-css', 'Materialize CSS - material design, components, JavaScript plugins, sass customization'),
    ('semantic-ui', 'Semantic UI/Fomantic - theming, modules, behaviors, transitions, collections'),
    ('chakra-ui', 'Chakra UI v2/v3 - theme, component variants, responsive, dark mode, forms, hooks'),
    ('mantine-advanced', 'Mantine advanced - theming, polymorphic, Spotlight, Notifications, Calendar, DnD'),
    ('radix-advanced', 'Radix UI advanced - composition, theming, accessibility, asChild, animation, portal'),
    ('headlessui-advanced', 'Headless UI advanced - composable, transitions, portal, focus management, popover'),
    ('daisyui', 'DaisyUI - Tailwind component library, themes, custom themes, semantic colors, modifier classes'),
    ('shadcn-advanced', 'shadcn/ui advanced - customization, theming, registry, blocks, chart, typography'),
    ('tremor-charts', 'Tremor - React dashboard components, charts, KPIs, tables, forms, theming'),
    # Testing frameworks deep
    ('jest-advanced', 'Jest advanced - mocking, fake timers, async, coverage, transform, custom matchers, expect'),
    ('vitest-advanced', 'Vitest advanced - workspace, browser mode, snapshot, coverage, typed test, bench'),
    ('playwright-advanced', 'Playwright advanced - component testing, API testing, HAR, traces, accessibility'),
    ('cypress-advanced', 'Cypress advanced - commands, queries, intercepts, plugins, network shaping, component'),
    ('testing-library-advanced', 'Testing Library advanced - user-event, custom queries, accessibility, async utilities'),
    ('mocha-advanced', 'Mocha advanced - reporters, interfaces, hooks, parallel, custom runners, browser'),
    ('jasmine-advanced', 'Jasmine - spies, matchers, async, custom equality, reporters, browser testing'),
    ('webdriverio-advanced', 'WebdriverIO advanced - page objects, services, reporters, visual regression, mobile'),
    ('selenium-advanced', 'Selenium advanced - WebDriver, Grid, remote, wait strategies, PageObject, screenshots'),
    ('k6-advanced-testing', 'k6 advanced testing - scenarios, thresholds, custom metrics, extensions, cloud'),
    ('gatling-advanced', 'Gatling advanced - simulations, feeders, checks, protocols, assertions, reports'),
    ('locust-advanced', 'Locust advanced - tasks, users, events, custom clients, shape classes, distributed'),
    # DevOps tools deep
    ('ansible-advanced-patterns', 'Ansible advanced patterns - dynamic inventory, custom modules, callbacks, filters, tests'),
    ('chef-advanced', 'Chef advanced - resources, libraries, custom resources, data bags, environments, testing'),
    ('puppet-advanced', 'Puppet advanced - functions, types, providers, hiera, exported resources, Bolt'),
    ('saltstack-advanced', 'SaltStack advanced - states, grains, pillars, orchestration, runners, execution modules'),
    ('vagrant-advanced', 'Vagrant advanced - providers, provisioners, plugins, multi-machine, synced folders, boxes'),
    ('packer-advanced', 'Packer advanced - builders, provisioners, post-processors, HCL2, plugins, debugging'),
    ('capistrano', 'Capistrano - deployment, tasks, roles, plugins, SCM integration, linked files, rollback'),
    ('fabric-python', 'Fabric - task execution, connections, groups, transfers, sudo, context managers'),
    ('invoke-python', 'Invoke - task runner, namespaces, configuration, pre/post tasks, context, collections'),
    # CI/CD deep
    ('github-actions-advanced', 'GitHub Actions advanced - composite actions, reusable workflows, environments, OIDC'),
    ('gitlab-ci-advanced', 'GitLab CI advanced - parent-child pipelines, dynamic, include, rules, cache, artifacts'),
    ('jenkins-groovy', 'Jenkins Groovy - shared libraries, pipeline DSL, scripted, parallel, stash, credentials'),
    ('circleci-orbs', 'CircleCI orbs - reusable components, parameters, jobs, executors, commands, publishing'),
    ('teamcity-advanced', 'TeamCity advanced - build chains, composite builds, meta-runners, DSL Kotlin, agents'),
    ('bamboo-cicd', 'Bamboo - build plans, stages, deployment projects, agents, specs, triggers, notifications'),
    ('azure-devops-advanced', 'Azure DevOps advanced - YAML pipelines, templates, variable groups, environments, gates'),
    ('travis-ci', 'Travis CI - matrix, stages, deploy, caching, environment, addons, build lifecycle'),
    ('drone-ci-advanced', 'Drone CI advanced - pipelines, steps, services, volumes, clone, secrets, signing'),
    ('buildkite-advanced', 'Buildkite advanced - dynamic pipelines, parallel, artifacts, plugins, agents, triggers'),
    ('woodpecker-ci-advanced', 'Woodpecker CI advanced - pipelines, services, volumes, caching, plugins, secrets'),
    ('concourse-ci', 'Concourse CI - resources, tasks, jobs, pipelines, workers, credentials, fly CLI'),
    ('spinnaker-advanced', 'Spinnaker advanced - pipelines, stages, canary analysis, manual judgment, notifications'),
    ('harness-advanced', 'Harness advanced - pipelines, stages, CV, feature flags, chaos, DAST, SRM'),
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
