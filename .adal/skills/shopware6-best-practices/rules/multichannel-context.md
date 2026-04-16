---
title: Context Handling & Scopes
impact: HIGH
impactDescription: proper context usage for correct data access and permissions
tags: context, scope, permissions, api, sales-channel
---

## Context Handling & Scopes

**Impact: HIGH (proper context usage for correct data access and permissions)**

Shopware 6 uses different context types for different scopes. Understanding when to use `Context`, `SalesChannelContext`, or `AdminApiSource` is critical for correct behavior.

**Incorrect (wrong context usage):**

```php
// Bad: Using default context in storefront (loses customer, currency, etc.)
public function handleStorefrontRequest(Request $request): Response
{
    $context = Context::createDefaultContext();
    $products = $this->productRepository->search(new Criteria(), $context);
    // Missing: sales channel visibility, customer prices, currency
}

// Bad: Using SalesChannelContext for admin operations
public function adminAction(SalesChannelContext $context): void
{
    // SalesChannelContext has customer restrictions, wrong for admin
    $this->repository->delete([['id' => $id]], $context->getContext());
}
```

**Correct context usage by scope:**

```php
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\Service;

use Shopware\Core\Framework\Context;
use Shopware\Core\Framework\Api\Context\AdminApiSource;
use Shopware\Core\Framework\Api\Context\SalesChannelApiSource;
use Shopware\Core\Framework\Api\Context\SystemSource;
use Shopware\Core\System\SalesChannel\SalesChannelContext;

class ContextAwareService
{
    /**
     * Storefront: Use SalesChannelContext
     * Automatically available in storefront controllers
     */
    public function storefrontOperation(SalesChannelContext $context): void
    {
        // SalesChannelContext provides:
        $salesChannelId = $context->getSalesChannelId();
        $customer = $context->getCustomer();
        $currencyId = $context->getCurrencyId();
        $languageId = $context->getLanguageId();
        $customerGroupId = $context->getCurrentCustomerGroup()->getId();
        $taxState = $context->getTaxState(); // gross/net

        // For DAL operations, extract the base context
        $dalContext = $context->getContext();

        // Products loaded with SalesChannelContext respect visibility
        $products = $this->productRepository->search(
            new Criteria(),
            $dalContext
        );
    }

    /**
     * Store API: Also uses SalesChannelContext
     */
    public function storeApiOperation(SalesChannelContext $context): void
    {
        // Verify source is Store API
        $source = $context->getContext()->getSource();

        if (!$source instanceof SalesChannelApiSource) {
            throw new \RuntimeException('Store API context required');
        }

        // Access original sales channel ID from source
        $salesChannelId = $source->getSalesChannelId();
    }

    /**
     * Admin API: Use Context with AdminApiSource
     */
    public function adminApiOperation(Context $context): void
    {
        $source = $context->getSource();

        // Verify admin context
        if (!$source instanceof AdminApiSource) {
            throw new AccessDeniedException('Admin API access required');
        }

        // Get admin user ID
        $userId = $source->getUserId();
        $integrationId = $source->getIntegrationId();

        // Check admin permissions
        if (!$source->isAdmin() && !$source->isAllowed('product.editor')) {
            throw new AccessDeniedException('Missing permission: product.editor');
        }

        // Full access to all entities
        $this->productRepository->update([
            ['id' => $productId, 'active' => true]
        ], $context);
    }

    /**
     * Background tasks / CLI: Create system context
     */
    public function backgroundOperation(): void
    {
        // System context with full access
        $context = Context::createDefaultContext();

        // Verify system source
        if (!$context->getSource() instanceof SystemSource) {
            throw new \RuntimeException('System context required');
        }

        // Full access for background processing
        $this->processAllProducts($context);
    }

    /**
     * Create context with specific scope
     */
    public function createScopedContext(string $scope): Context
    {
        $context = Context::createDefaultContext();

        // Add custom context scope for rule evaluation
        return new Context(
            $context->getSource(),
            $context->getRuleIds(),
            $context->getCurrencyId(),
            $context->getLanguageIdChain(),
            $context->getVersionId(),
            $context->getCurrencyFactor(),
            $context->considerInheritance(),
            $context->getTaxState(),
            $context->getRounding()
        );
    }
}
```

**Correct context modification:**

```php
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\Service;

class ContextModificationService
{
    /**
     * Change language in context
     */
    public function withLanguage(Context $context, string $languageId): Context
    {
        return new Context(
            $context->getSource(),
            $context->getRuleIds(),
            $context->getCurrencyId(),
            [$languageId, ...$context->getLanguageIdChain()],
            $context->getVersionId(),
            $context->getCurrencyFactor(),
            $context->considerInheritance(),
            $context->getTaxState(),
            $context->getRounding()
        );
    }

    /**
     * Disable inheritance for a context
     */
    public function withoutInheritance(Context $context): Context
    {
        return new Context(
            $context->getSource(),
            $context->getRuleIds(),
            $context->getCurrencyId(),
            $context->getLanguageIdChain(),
            $context->getVersionId(),
            $context->getCurrencyFactor(),
            false, // Disable inheritance
            $context->getTaxState(),
            $context->getRounding()
        );
    }

    /**
     * Add rules to context for testing
     */
    public function withRules(Context $context, array $ruleIds): Context
    {
        return new Context(
            $context->getSource(),
            array_merge($context->getRuleIds(), $ruleIds),
            $context->getCurrencyId(),
            $context->getLanguageIdChain(),
            $context->getVersionId(),
            $context->getCurrencyFactor(),
            $context->considerInheritance(),
            $context->getTaxState(),
            $context->getRounding()
        );
    }

    /**
     * Skip trigger for performance-critical operations
     */
    public function executeWithoutTriggers(Context $context, callable $operation): void
    {
        $context->scope(Context::SKIP_TRIGGER_FLOW, function (Context $inner) use ($operation) {
            $operation($inner);
        });
    }

    /**
     * Execute in CRUD scope (bypass restrictions)
     */
    public function executeInSystemScope(Context $context, callable $operation): void
    {
        $context->scope(Context::SYSTEM_SCOPE, function (Context $inner) use ($operation) {
            $operation($inner);
        });
    }
}
```

**Correct API controller context handling:**

```php
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\Controller;

// Admin API Controller
#[Route(defaults: ['_routeScope' => ['api']])]
class AdminController extends AbstractController
{
    #[Route(path: '/api/_action/my-plugin/action', methods: ['POST'])]
    public function adminAction(Context $context): JsonResponse
    {
        // Context is injected with AdminApiSource
        $this->service->processAsAdmin($context);
        return new JsonResponse(['success' => true]);
    }
}

// Store API Controller
#[Route(defaults: ['_routeScope' => ['store-api']])]
class StoreApiController extends AbstractController
{
    #[Route(path: '/store-api/my-plugin/data', methods: ['GET'])]
    public function getData(SalesChannelContext $context): JsonResponse
    {
        // SalesChannelContext is injected for store-api routes
        $data = $this->service->getDataForCustomer($context);
        return new JsonResponse($data);
    }
}

// Storefront Controller
#[Route(defaults: ['_routeScope' => ['storefront']])]
class StorefrontController extends AbstractStorefrontController
{
    #[Route(path: '/my-page', name: 'frontend.my.page', methods: ['GET'])]
    public function myPage(SalesChannelContext $context): Response
    {
        // SalesChannelContext for storefront
        return $this->renderStorefront('@MyPlugin/page.html.twig', [
            'customer' => $context->getCustomer()
        ]);
    }
}
```

**Context types and sources:**

| Source | Scope | Use Case |
|--------|-------|----------|
| `SystemSource` | System | CLI, Scheduled Tasks, Message Queue |
| `AdminApiSource` | Admin | Admin API, Administration |
| `SalesChannelApiSource` | Store API | Headless storefront API |
| `SalesChannelContext` | Storefront | Classic storefront |

**Context scope constants:**

| Scope | Description |
|-------|-------------|
| `Context::SYSTEM_SCOPE` | Bypass all restrictions |
| `Context::SKIP_TRIGGER_FLOW` | Skip flow builder triggers |
| `Context::CRUD_API_SCOPE` | API CRUD operations |

Reference: [Context](https://developer.shopware.com/docs/concepts/framework/context.html)
