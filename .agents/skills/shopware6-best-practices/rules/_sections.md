# Sections

This file defines all sections, their ordering, impact levels, and descriptions.
The section ID (in parentheses) is the filename prefix used to group rules.

---

## 1. Plugin Architecture (plugin)

**Impact:** CRITICAL
**Description:** Proper plugin structure, composer configuration, service registration, and lifecycle management are fundamental to maintainable and upgrade-safe Shopware 6 extensions.

## 2. Customization & Extension Patterns (custom)

**Impact:** CRITICAL
**Description:** Using decorators, subscribers, and extension mechanisms instead of core modifications ensures upgrade safety and maintainability.

## 3. Performance & Caching (perf)

**Impact:** CRITICAL
**Description:** HTTP caching, object caching, DAL optimization, and proper use of Elasticsearch directly impact storefront performance and scalability.

## 4. Security (security)

**Impact:** CRITICAL
**Description:** Input validation, authentication, authorization, CSRF protection, and secure coding practices are essential for safe e-commerce applications.

## 5. Data Abstraction Layer (dal)

**Impact:** HIGH
**Description:** Proper use of repositories, Criteria objects, entity definitions, associations, and write operations ensures data integrity and performance.

## 6. API Development (api)

**Impact:** HIGH
**Description:** Store API routes, Admin API endpoints, authentication, response formatting, and API versioning patterns for robust integrations.

## 7. Event System & Subscribers (event)

**Impact:** MEDIUM-HIGH
**Description:** Proper event subscription, business event handling, and flow actions enable extensible and decoupled architectures.

## 8. Message Queue (queue)

**Impact:** MEDIUM
**Description:** Asynchronous message handling, worker configuration, and reliable message processing patterns for background tasks.

## 9. Database & Migrations (db)

**Impact:** MEDIUM-HIGH
**Description:** Migration best practices, schema design, indexing strategies, and database-level optimizations.

## 10. Testing (test)

**Impact:** HIGH
**Description:** Unit testing, integration testing, and test infrastructure patterns ensure code quality and regression prevention.

## 11. Dependency Injection (di)

**Impact:** MEDIUM
**Description:** Service container usage, proper tagging, and dependency management patterns following Symfony conventions.

## 12. Logging & Debugging (logging)

**Impact:** MEDIUM
**Description:** Structured logging, debug practices, and observability patterns for effective troubleshooting.

## 13. Configuration & Settings (config)

**Impact:** MEDIUM
**Description:** Plugin configuration, system config, and feature flags for flexible and configurable extensions.

## 14. Scheduled Tasks (scheduled)

**Impact:** MEDIUM
**Description:** Proper implementation of scheduled tasks, cron jobs, and recurring background operations.

## 15. Storefront Development (storefront)

**Impact:** HIGH
**Description:** Twig template extension, JavaScript plugins, SCSS theming, and storefront controller patterns for customizing the customer-facing shop experience.

## 16. Administration Development (admin)

**Impact:** HIGH
**Description:** Vue.js module development, component patterns, data handling, ACL permissions, and Extension API for customizing the admin interface.

## 17. App System (app)

**Impact:** HIGH
**Description:** App manifest configuration, webhooks, action buttons, payment handlers, custom fields, and app scripts for building Shopware apps without a dedicated server.

## 18. Integration Patterns (integration)

**Impact:** HIGH
**Description:** Payment handlers, shipping methods, CMS elements, import/export profiles, and external API integration patterns.

## 19. CLI Commands (cli)

**Impact:** MEDIUM
**Description:** Custom console commands, command lifecycle, argument/option handling, and progress output for automation and maintenance tasks.

## 20. Multi-Channel & B2B (multichannel)

**Impact:** MEDIUM-HIGH
**Description:** Sales channel awareness, B2B commerce patterns, advanced pricing, and context management for multi-channel shops.

## 21. DevOps & Tooling (devops)

**Impact:** MEDIUM
**Description:** Development environment setup, deployment, static analysis, debugging, and CI/CD pipelines for professional Shopware development.

## 22. Common Patterns (pattern)

**Impact:** HIGH
**Description:** Error handling, translations, media handling, rule builder conditions, and version upgrade patterns that apply across all Shopware development.
