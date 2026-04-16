# Shopware 6 Skill Enhancement Plan

## Overview

This plan adds 40+ new rules across 8 new sections to complete the skill for full agency developer coverage.

---

## Phase 1: Storefront & Twig (CRITICAL)

New section prefix: `storefront-`

| Rule File | Title | Impact |
|-----------|-------|--------|
| `storefront-controller-pattern.md` | Storefront Controllers & Page Loading | HIGH |
| `storefront-twig-extension.md` | Twig Template Extension & Override | CRITICAL |
| `storefront-js-plugins.md` | JavaScript Plugin System | HIGH |
| `storefront-themes.md` | Theme Development & Inheritance | HIGH |
| `storefront-scss-variables.md` | SCSS Variables & Theming | MEDIUM |
| `storefront-http-client.md` | AJAX & HttpClient Usage | MEDIUM |

---

## Phase 2: Administration/Vue.js (CRITICAL)

New section prefix: `admin-`

| Rule File | Title | Impact |
|-----------|-------|--------|
| `admin-module-structure.md` | Admin Module Structure & Registration | CRITICAL |
| `admin-components.md` | Vue Component Patterns | HIGH |
| `admin-data-handling.md` | Repository & Data Handling | HIGH |
| `admin-acl-permissions.md` | ACL & Permission Checks | HIGH |
| `admin-mixins-composables.md` | Mixins, Directives & Composition | MEDIUM |
| `admin-extension-api.md` | Extension API for Apps | MEDIUM |

---

## Phase 3: App System (HIGH)

New section prefix: `app-`

| Rule File | Title | Impact |
|-----------|-------|--------|
| `app-manifest.md` | App Manifest Configuration | CRITICAL |
| `app-webhooks.md` | Webhook Implementation | HIGH |
| `app-custom-actions.md` | Action Buttons & Custom Actions | HIGH |
| `app-payment-methods.md` | App Payment Handlers | HIGH |
| `app-custom-fields.md` | Custom Fields via App | MEDIUM |
| `app-scripts.md` | App Scripts (Twig) | MEDIUM |

---

## Phase 4: Integration Patterns (HIGH)

New section prefix: `integration-`

| Rule File | Title | Impact |
|-----------|-------|--------|
| `integration-payment-handler.md` | Payment Handler Implementation | CRITICAL |
| `integration-shipping-method.md` | Shipping Method Provider | HIGH |
| `integration-cms-elements.md` | CMS Elements & Blocks | HIGH |
| `integration-cms-slots.md` | CMS Slot Configuration | MEDIUM |
| `integration-import-export.md` | Import/Export Profiles | HIGH |
| `integration-external-api.md` | External API Integration | MEDIUM |

---

## Phase 5: CLI & Commands (MEDIUM-HIGH)

New section prefix: `cli-`

| Rule File | Title | Impact |
|-----------|-------|--------|
| `cli-commands.md` | Custom Console Commands | HIGH |
| `cli-command-lifecycle.md` | Command Lifecycle & Arguments | MEDIUM |
| `cli-progress-output.md` | Progress Bars & Output Formatting | MEDIUM |

---

## Phase 6: Multi-Channel & B2B (MEDIUM-HIGH)

New section prefix: `multichannel-`

| Rule File | Title | Impact |
|-----------|-------|--------|
| `multichannel-saleschannel.md` | Sales Channel Awareness | HIGH |
| `multichannel-b2b-patterns.md` | B2B Features & Company Handling | MEDIUM |
| `multichannel-pricing.md` | Channel-Specific Pricing | MEDIUM |
| `multichannel-context.md` | Context Handling & Scopes | HIGH |

---

## Phase 7: DevOps & Tooling (MEDIUM)

New section prefix: `devops-`

| Rule File | Title | Impact |
|-----------|-------|--------|
| `devops-development-setup.md` | Dockware & Local Development | HIGH |
| `devops-deployment.md` | Deployment & Build Process | HIGH |
| `devops-ci-cd.md` | CI/CD Pipeline Configuration | MEDIUM |
| `devops-static-analysis.md` | PHPStan & Code Quality | MEDIUM |
| `devops-debugging.md` | Debugging & Profiling Tools | MEDIUM |

---

## Phase 8: Additional Patterns (MEDIUM)

New section prefix: `pattern-`

| Rule File | Title | Impact |
|-----------|-------|--------|
| `pattern-error-handling.md` | Exception Handling & Error Pages | HIGH |
| `pattern-translations.md` | Snippets & Entity Translations | HIGH |
| `pattern-media-handling.md` | Media Upload & Processing | MEDIUM |
| `pattern-rule-builder.md` | Rule Builder Conditions | MEDIUM |
| `pattern-upgrade-migration.md` | Version Upgrade Patterns | HIGH |

---

## Execution Order

1. **Phase 1**: Storefront (6 files) - Most requested by agencies
2. **Phase 2**: Administration (6 files) - Critical for admin work
3. **Phase 3**: App System (6 files) - Modern extension model
4. **Phase 4**: Integration (6 files) - Payment/shipping/CMS
5. **Phase 5**: CLI (3 files) - Developer productivity
6. **Phase 6**: Multi-Channel (4 files) - B2B/B2C patterns
7. **Phase 7**: DevOps (5 files) - Deployment & tooling
8. **Phase 8**: Patterns (5 files) - Common patterns

**Total: 41 new rule files**

---

## Updates Required After Rules

1. Update `_sections.md` with new sections
2. Update `SKILL.md` with new categories
3. Update `AGENTS.md` with compiled content
4. Update `metadata.json` with new version

---

## File Naming Convention

All files follow: `{section-prefix}-{topic}.md`

Example: `storefront-twig-extension.md`
