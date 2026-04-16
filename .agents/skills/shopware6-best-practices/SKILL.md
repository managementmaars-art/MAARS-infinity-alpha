---
name: shopware6-best-practices
description: Comprehensive Shopware 6.6+ development best practices for agency developers. Covers backend PHP, storefront Twig/JS, administration Vue.js, app system, integrations, CLI, multi-channel, and DevOps. Triggers on tasks involving plugin development, storefront customization, admin modules, app creation, payment/shipping integrations, or deployment.
license: MIT
metadata:
  author: shopware-engineering
  version: "2.0.0"
---

# Shopware 6 Best Practices

Comprehensive best practices guide for Shopware 6.6+ development, designed for AI agents and LLMs helping agency developers. Contains 77 rules across 22 categories, prioritized by impact to guide automated refactoring and code generation.

## When to Apply

Reference these guidelines when:
- Developing custom Shopware 6 plugins
- Creating or modifying Store API or Admin API endpoints
- Working with the Data Abstraction Layer (DAL)
- Implementing event subscribers and decorators
- Configuring message queue handlers
- Writing database migrations
- Optimizing performance (caching, Elasticsearch)
- Implementing security measures
- Writing unit and integration tests
- Customizing storefront templates and JavaScript
- Building administration modules and components
- Creating Shopware apps with webhooks and actions
- Implementing payment or shipping integrations
- Building CMS elements and blocks
- Creating CLI commands for automation
- Setting up multi-channel or B2B shops
- Configuring development environments and CI/CD

## Rule Categories by Priority

| Priority | Category | Impact | Prefix |
|----------|----------|--------|--------|
| 1 | Plugin Architecture | CRITICAL | `plugin-` |
| 2 | Customization & Extension | CRITICAL | `custom-` |
| 3 | Performance & Caching | CRITICAL | `perf-` |
| 4 | Security | CRITICAL | `security-` |
| 5 | Data Abstraction Layer | HIGH | `dal-` |
| 6 | API Development | HIGH | `api-` |
| 7 | Testing | HIGH | `test-` |
| 8 | Event System | MEDIUM-HIGH | `event-` |
| 9 | Database & Migrations | MEDIUM-HIGH | `db-` |
| 10 | Message Queue | MEDIUM | `queue-` |
| 11 | Dependency Injection | MEDIUM | `di-` |
| 12 | Logging | MEDIUM | `logging-` |
| 13 | Configuration | MEDIUM | `config-` |
| 14 | Scheduled Tasks | MEDIUM | `scheduled-` |
| 15 | Storefront Development | HIGH | `storefront-` |
| 16 | Administration Development | HIGH | `admin-` |
| 17 | App System | HIGH | `app-` |
| 18 | Integration Patterns | HIGH | `integration-` |
| 19 | CLI Commands | MEDIUM | `cli-` |
| 20 | Multi-Channel & B2B | MEDIUM-HIGH | `multichannel-` |
| 21 | DevOps & Tooling | MEDIUM | `devops-` |
| 22 | Common Patterns | HIGH | `pattern-` |

## Quick Reference

### 1. Plugin Architecture (CRITICAL)

- `plugin-structure` - Follow proper plugin directory structure and composer.json
- `plugin-services` - Register services correctly with proper tags

### 2. Customization & Extension (CRITICAL)

- `custom-decorator-pattern` - Use decorator pattern for upgrade-safe service customization
- `custom-event-subscribers` - Implement event subscribers correctly with proper priorities

### 3. Performance & Caching (CRITICAL)

- `perf-http-cache` - Configure HTTP cache correctly with proper invalidation
- `perf-dal-optimization` - Optimize DAL queries to prevent N+1 problems
- `perf-elasticsearch` - Use Elasticsearch correctly for large catalogs

### 4. Security (CRITICAL)

- `security-input-validation` - Validate all inputs with RequestDataBag and validators
- `security-authentication` - Implement proper route authentication
- `security-authorization` - Use ACL for permission checks
- `security-csrf-protection` - Implement CSRF protection for storefront
- `security-sql-injection` - Use DAL or parameterized queries

### 5. Data Abstraction Layer (HIGH)

- `dal-criteria-usage` - Use Criteria objects correctly with filters and pagination
- `dal-associations` - Load associations explicitly to avoid N+1 queries
- `dal-write-operations` - Use batch operations and proper sync patterns
- `dal-entity-extensions` - Extend entities without modifying core
- `dal-custom-entities` - Create custom entity definitions properly

### 6. API Development (HIGH)

- `api-store-api-routes` - Create decoratable Store API routes
- `api-admin-api-routes` - Create Admin API endpoints with proper ACL
- `api-response-handling` - Handle responses and errors consistently
- `api-rate-limiting` - Configure rate limiting for protection
- `api-versioning` - Version APIs for backwards compatibility

### 7. Testing (HIGH)

- `test-unit-tests` - Write unit tests with proper mocking
- `test-integration-tests` - Use IntegrationTestBehaviour correctly
- `test-store-api-tests` - Test Store API routes with HTTP tests
- `test-fixtures` - Create reusable test fixtures

### 8. Event System (MEDIUM-HIGH)

- `event-business-events` - Create Flow Builder compatible events
- `event-flow-actions` - Implement configurable flow actions

### 9. Database & Migrations (MEDIUM-HIGH)

- `db-migrations` - Implement safe database migrations

### 10. Message Queue (MEDIUM)

- `queue-message-handlers` - Implement async message handling
- `queue-worker-config` - Configure workers for production
- `queue-low-priority` - Separate low-priority background tasks

### 11. Dependency Injection (MEDIUM)

- `di-service-container` - Use Symfony DI correctly

### 12. Logging (MEDIUM)

- `logging-best-practices` - Implement structured logging

### 13. Configuration (MEDIUM)

- `config-plugin-settings` - Implement plugin configuration correctly

### 14. Scheduled Tasks (MEDIUM)

- `scheduled-tasks` - Implement reliable scheduled tasks

### 15. Storefront Development (HIGH)

- `storefront-controller-pattern` - Extend StorefrontController with page loaders
- `storefront-twig-extension` - Template inheritance with sw_extends and blocks
- `storefront-js-plugins` - JavaScript plugin registration and lifecycle
- `storefront-themes` - Theme structure, inheritance, and configuration
- `storefront-scss-variables` - SCSS variables and responsive mixins
- `storefront-http-client` - AJAX requests and Store API calls from JS

### 16. Administration Development (HIGH)

- `admin-module-structure` - Module registration, routes, and navigation
- `admin-components` - Vue component patterns and templates
- `admin-data-handling` - Repository factory and Criteria API in admin
- `admin-acl-permissions` - ACL-based UI visibility and actions
- `admin-mixins-composables` - Mixins, directives, and extensibility
- `admin-extension-api` - App iframe modules and Extension SDK

### 17. App System (HIGH)

- `app-manifest` - Complete manifest.xml configuration
- `app-webhooks` - Webhook handling and signature verification
- `app-custom-actions` - Action buttons with notifications, modals, redirects
- `app-payment-methods` - App payment handlers for pay/finalize/capture/refund
- `app-custom-fields` - Custom field definitions via manifest
- `app-scripts` - Twig-based app scripts and hook points

### 18. Integration Patterns (HIGH)

- `integration-payment-handler` - Sync/async payment handler patterns
- `integration-shipping-method` - Shipping calculators and delivery times
- `integration-cms-elements` - CMS element creation with data resolvers
- `integration-import-export` - Import/export profiles and converters
- `integration-external-api` - HTTP client patterns with retry and caching

### 19. CLI Commands (MEDIUM)

- `cli-commands` - Custom command creation with arguments and options
- `cli-command-lifecycle` - Configure/initialize/interact/execute lifecycle
- `cli-progress-output` - SymfonyStyle, progress bars, and formatting

### 20. Multi-Channel & B2B (MEDIUM-HIGH)

- `multichannel-saleschannel` - Sales channel awareness and visibility
- `multichannel-b2b-patterns` - Company handling, roles, and budgets
- `multichannel-pricing` - Currency, customer groups, and tax handling
- `multichannel-context` - Context types, scopes, and permissions

### 21. DevOps & Tooling (MEDIUM)

- `devops-development-setup` - Dockware, docker-compose, Makefile patterns
- `devops-deployment` - Deployment scripts, builds, and rollbacks
- `devops-static-analysis` - PHPStan, PHP-CS-Fixer, Rector configuration
- `devops-debugging` - Profiler, Xdebug, logging, and data collectors
- `devops-ci-cd` - GitHub Actions and GitLab CI workflows

### 22. Common Patterns (HIGH)

- `pattern-error-handling` - Custom exceptions and error pages
- `pattern-translations` - Snippets and entity translations
- `pattern-media-handling` - Media service, uploads, and thumbnails
- `pattern-rule-builder` - Custom rule conditions for pricing/shipping
- `pattern-upgrade-migration` - Version-aware code and update migrations

## Core Principles

### The Decorator Pattern is Key

Never modify core files. Always use:
- **Decorators** for services
- **Event subscribers** for hooks
- **Entity extensions** for data

### DAL Over Raw SQL

Use Shopware's Data Abstraction Layer instead of raw SQL:
- Type safety and validation
- Automatic association handling
- Built-in versioning and translation

### Performance First

Shopware can be slow if misused:
- Enable HTTP cache in production
- Use Elasticsearch for 10K+ products
- Load only needed associations
- Use message queue for heavy tasks

## How to Use

Read individual rule files for detailed explanations and code examples:

```
rules/plugin-structure.md
rules/custom-decorator-pattern.md
rules/perf-http-cache.md
rules/security-input-validation.md
rules/dal-criteria-usage.md
```

Each rule file contains:
- Brief explanation of why it matters
- Incorrect code example with explanation
- Correct code example with explanation
- Additional context and references

## Full Compiled Document

For the complete guide with all rules expanded: `AGENTS.md`
