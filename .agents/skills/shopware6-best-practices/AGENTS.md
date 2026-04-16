# Shopware 6 Best Practices

**Version:** 2.0.0
**Organization:** Shopware Engineering
**Date:** January 2026

## Abstract

This document provides comprehensive best practices for Shopware 6.6+ development, designed specifically for AI agents and LLMs helping agency developers. It covers plugin architecture, DAL patterns, API development, performance optimization, security, testing, storefront customization, administration modules, app system, integrations, CLI commands, multi-channel commerce, and DevOps. Each rule includes detailed explanations, real-world examples comparing incorrect vs. correct implementations, and specific impact metrics to guide automated refactoring and code generation.

---

## Table of Contents

1. [Plugin Architecture](#1-plugin-architecture) - CRITICAL
2. [Customization & Extension Patterns](#2-customization--extension-patterns) - CRITICAL
3. [Performance & Caching](#3-performance--caching) - CRITICAL
4. [Security](#4-security) - CRITICAL
5. [Data Abstraction Layer](#5-data-abstraction-layer) - HIGH
6. [API Development](#6-api-development) - HIGH
7. [Event System & Subscribers](#7-event-system--subscribers) - MEDIUM-HIGH
8. [Message Queue](#8-message-queue) - MEDIUM
9. [Database & Migrations](#9-database--migrations) - MEDIUM-HIGH
10. [Testing](#10-testing) - HIGH
11. [Dependency Injection](#11-dependency-injection) - MEDIUM
12. [Logging & Debugging](#12-logging--debugging) - MEDIUM
13. [Configuration & Settings](#13-configuration--settings) - MEDIUM
14. [Scheduled Tasks](#14-scheduled-tasks) - MEDIUM
15. [Storefront Development](#15-storefront-development) - HIGH
16. [Administration Development](#16-administration-development) - HIGH
17. [App System](#17-app-system) - HIGH
18. [Integration Patterns](#18-integration-patterns) - HIGH
19. [CLI Commands](#19-cli-commands) - MEDIUM
20. [Multi-Channel & B2B](#20-multi-channel--b2b) - MEDIUM-HIGH
21. [DevOps & Tooling](#21-devops--tooling) - MEDIUM
22. [Common Patterns](#22-common-patterns) - HIGH
23. [References](#references)

---

## 1. Plugin Architecture

**Impact:** CRITICAL
**Description:** Proper plugin structure, composer configuration, service registration, and lifecycle management are fundamental to maintainable and upgrade-safe Shopware 6 extensions.

### 1.1 Follow Proper Plugin Structure

Shopware 6 plugins must follow a specific directory structure and composer configuration to be properly discovered and loaded by the platform.

**Correct plugin structure:**

```
custom/plugins/MyPlugin/
├── composer.json
└── src/
    ├── MyPlugin.php                    # Main plugin class
    ├── Resources/
    │   ├── config/
    │   │   ├── services.xml            # Service definitions
    │   │   ├── routes.xml              # Route registration (optional)
    │   │   └── config.xml              # Plugin configuration (optional)
    │   ├── views/                      # Twig templates
    │   └── app/
    │       └── administration/         # Admin module (optional)
    ├── Controller/
    ├── Subscriber/
    ├── Service/
    ├── Core/                           # Core extensions
    ├── Migration/                      # Database migrations
    └── Entity/                         # Custom entities
```

**Correct composer.json:**

```json
{
    "name": "my-vendor/my-plugin",
    "description": "My Shopware 6 Plugin",
    "version": "1.0.0",
    "type": "shopware-platform-plugin",
    "license": "MIT",
    "require": {
        "shopware/core": "~6.6.0"
    },
    "extra": {
        "shopware-plugin-class": "MyVendor\\MyPlugin\\MyPlugin",
        "label": {
            "de-DE": "Mein Plugin",
            "en-GB": "My Plugin"
        }
    },
    "autoload": {
        "psr-4": {
            "MyVendor\\MyPlugin\\": "src/"
        }
    }
}
```

**Correct plugin class:**

```php
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin;

use Shopware\Core\Framework\Plugin;
use Shopware\Core\Framework\Plugin\Context\InstallContext;
use Shopware\Core\Framework\Plugin\Context\UninstallContext;

class MyPlugin extends Plugin
{
    public function install(InstallContext $installContext): void
    {
        parent::install($installContext);
    }

    public function uninstall(UninstallContext $uninstallContext): void
    {
        parent::uninstall($uninstallContext);
        if ($uninstallContext->keepUserData()) {
            return;
        }
        // Clean up custom data only if user opts out of keeping data
    }
}
```

### 1.2 Register Services Correctly

Services must be properly defined in `services.xml` with correct tags and autowiring configuration.

**Correct service registration:**

```xml
<?xml version="1.0" ?>
<container xmlns="http://symfony.com/schema/dic/services"
           xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
           xsi:schemaLocation="http://symfony.com/schema/dic/services
           https://symfony.com/schema/dic/services/services-1.0.xsd">

    <services>
        <defaults autowire="true" autoconfigure="true" public="false"/>

        <!-- Event Subscriber - must have tag -->
        <service id="MyVendor\MyPlugin\Subscriber\OrderSubscriber">
            <tag name="kernel.event_subscriber"/>
        </service>

        <!-- Entity definition - must have tag -->
        <service id="MyVendor\MyPlugin\Core\Content\CustomEntity\CustomEntityDefinition">
            <tag name="shopware.entity.definition" entity="custom_entity"/>
        </service>

        <!-- Scheduled task - must have tag -->
        <service id="MyVendor\MyPlugin\ScheduledTask\SyncTask">
            <tag name="shopware.scheduled.task"/>
        </service>
    </services>
</container>
```

**Common service tags:**

| Tag | Purpose |
|-----|---------|
| `kernel.event_subscriber` | Event subscribers |
| `shopware.entity.definition` | Entity definitions |
| `shopware.scheduled.task` | Scheduled tasks |
| `messenger.message_handler` | Message queue handlers |
| `shopware.composite_search.definition` | Search definitions |

> See full details: `rules/plugin-structure.md`, `rules/plugin-services.md`

---

## 2. Customization & Extension Patterns

**Impact:** CRITICAL
**Description:** Using decorators, subscribers, and extension mechanisms instead of core modifications ensures upgrade safety and maintainability.

### 2.1 Use Decorator Pattern for Service Customization

The decorator pattern is the primary way to customize existing Shopware services while maintaining upgrade compatibility. Never modify core files directly.

**Correct decorator implementation:**

```php
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\Core\Checkout\Cart;

use Shopware\Core\Checkout\Cart\Cart;
use Shopware\Core\Checkout\Cart\AbstractCartPersister;
use Shopware\Core\Framework\Plugin\Exception\DecorationPatternException;
use Shopware\Core\System\SalesChannel\SalesChannelContext;

class DecoratedCartPersister extends AbstractCartPersister
{
    public function __construct(
        private readonly AbstractCartPersister $decorated,
        private readonly CartAuditService $auditService
    ) {}

    public function getDecorated(): AbstractCartPersister
    {
        return $this->decorated;
    }

    public function load(string $token, SalesChannelContext $context): Cart
    {
        $this->auditService->logCartAccess($token, $context);
        $cart = $this->decorated->load($token, $context);
        $this->enrichCartWithCustomData($cart);
        return $cart;
    }

    public function save(Cart $cart, SalesChannelContext $context): void
    {
        $this->applyCustomRules($cart);
        $this->decorated->save($cart, $context);
    }
}
```

**Service registration for decorator:**

```xml
<service id="MyVendor\MyPlugin\Core\Checkout\Cart\DecoratedCartPersister"
         decorates="Shopware\Core\Checkout\Cart\CartPersister">
    <argument type="service" id="MyVendor\MyPlugin\Core\Checkout\Cart\DecoratedCartPersister.inner"/>
    <argument type="service" id="MyVendor\MyPlugin\Service\CartAuditService"/>
</service>
```

### 2.2 Implement Event Subscribers Correctly

Event subscribers are the primary extension mechanism for reacting to system events without modifying core code.

**Correct event subscriber:**

```php
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\Subscriber;

use Shopware\Core\Content\Product\ProductEvents;
use Shopware\Core\Framework\DataAbstractionLayer\Event\EntityLoadedEvent;
use Shopware\Core\Framework\Struct\ArrayEntity;
use Symfony\Component\EventDispatcher\EventSubscriberInterface;

class ProductSubscriber implements EventSubscriberInterface
{
    public function __construct(
        private readonly CustomDataService $customDataService,
        private readonly MessageBusInterface $messageBus
    ) {}

    public static function getSubscribedEvents(): array
    {
        return [
            ProductEvents::PRODUCT_LOADED_EVENT => 'onProductLoaded',
            ProductEvents::PRODUCT_WRITTEN_EVENT => 'onProductWritten',
        ];
    }

    public function onProductLoaded(EntityLoadedEvent $event): void
    {
        foreach ($event->getEntities() as $product) {
            $customData = $this->customDataService->getCachedData($product->getId());
            if ($customData !== null) {
                $product->addExtension('myCustomData', new ArrayEntity($customData));
            }
        }
    }

    public function onProductWritten(EntityWrittenEvent $event): void
    {
        $ids = [];
        foreach ($event->getWriteResults() as $result) {
            $ids[] = $result->getPrimaryKey();
        }
        // Dispatch async message for heavy processing
        $this->messageBus->dispatch(new ProductSyncMessage($ids));
    }
}
```

> See full details: `rules/custom-decorator-pattern.md`, `rules/custom-event-subscribers.md`

---

## 3. Performance & Caching

**Impact:** CRITICAL
**Description:** HTTP caching, object caching, DAL optimization, and proper use of Elasticsearch directly impact storefront performance and scalability.

### 3.1 Configure HTTP Cache Correctly

HTTP caching is essential for Shopware 6 storefront performance. Proper configuration enables serving cached pages without hitting PHP.

**Correct cache invalidation:**

```php
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\Service;

use Shopware\Core\Framework\Adapter\Cache\CacheInvalidator;

class ProductUpdateService
{
    public function __construct(
        private readonly EntityRepository $productRepository,
        private readonly CacheInvalidator $cacheInvalidator
    ) {}

    public function updateProduct(string $productId, array $data, Context $context): void
    {
        $this->productRepository->update([
            ['id' => $productId, ...$data]
        ], $context);

        // Invalidate related cache tags
        $this->cacheInvalidator->invalidate([
            'product-' . $productId,
            'product-listing',
            CachedProductDetailRoute::buildName($productId),
        ]);
    }
}
```

**ESI for dynamic content:**

```twig
{% block my_cached_page_content %}
    <div class="static-content">{{ staticData.content }}</div>
    <div class="dynamic-content">
        {{ render_esi(url('frontend.my-dynamic-fragment')) }}
    </div>
{% endblock %}
```

### 3.2 Optimize DAL Queries for Performance

Proper query optimization prevents N+1 queries and reduces database load.

**Correct optimized patterns:**

```php
// Single batch query with associations
public function getProductsWithCategories(array $productIds, Context $context): array
{
    $criteria = new Criteria($productIds);
    $criteria->addAssociation('categories');
    return $this->productRepository->search($criteria, $context);
}

// Use aggregations for calculations
public function getAveragePrice(SalesChannelContext $context): float
{
    $criteria = new Criteria();
    $criteria->addAggregation(new AvgAggregation('average_price', 'price'));
    $criteria->setLimit(1);
    $result = $this->productRepository->search($criteria, $context->getContext());
    return $result->getAggregations()->get('average_price')->getAvg();
}

// Use searchIds when only IDs needed
public function getProductIds(Context $context): array
{
    $criteria = new Criteria();
    $criteria->addFilter(new EqualsFilter('active', true));
    return $this->productRepository->searchIds($criteria, $context)->getIds();
}

// Batch processing with chunking
public function processAllProducts(Context $context): void
{
    $criteria = new Criteria();
    $criteria->setLimit(100);
    $criteria->addSorting(new FieldSorting('id'));

    $iterator = new RepositoryIterator($this->productRepository, $context, $criteria);
    while (($result = $iterator->fetch()) !== null) {
        foreach ($result->getEntities() as $product) {
            $this->processProduct($product);
        }
        gc_collect_cycles();
    }
}
```

### 3.3 Use Elasticsearch Correctly for Large Catalogs

For catalogs with 10,000+ products, Elasticsearch offloads search, filtering, and aggregations from MySQL.

**Environment configuration:**

```env
SHOPWARE_ES_ENABLED=1
SHOPWARE_ES_INDEXING_ENABLED=1
SHOPWARE_ES_THROW_EXCEPTION=1
OPENSEARCH_URL=http://elasticsearch:9200
```

**ES-aware search service:**

```php
class ProductSearchService
{
    public function __construct(
        private readonly AbstractProductSearchRoute $searchRoute,
        private readonly AbstractProductListingRoute $listingRoute
    ) {}

    public function search(string $term, SalesChannelContext $context): ProductListingResult
    {
        $request = new Request(['search' => $term]);
        $criteria = new Criteria();
        $criteria->setLimit(24);
        return $this->searchRoute->load($request, $context, $criteria)->getListingResult();
    }
}
```

> See full details: `rules/perf-http-cache.md`, `rules/perf-dal-optimization.md`, `rules/perf-elasticsearch.md`

---

## 4. Security

**Impact:** CRITICAL
**Description:** Input validation, authentication, authorization, CSRF protection, and secure coding practices are essential for safe e-commerce applications.

### 4.1 Validate and Sanitize All Input

All user input must be validated and sanitized before processing.

**Correct validation:**

```php
use Shopware\Core\Framework\Validation\DataBag\RequestDataBag;
use Shopware\Core\Framework\Validation\DataValidationDefinition;
use Shopware\Core\Framework\Validation\DataValidator;
use Symfony\Component\Validator\Constraints as Assert;

class ProductController extends AbstractController
{
    public function __construct(
        private readonly DataValidator $validator,
        private readonly EntityRepository $productRepository
    ) {}

    #[Route(path: '/api/product/update', name: 'api.product.update', methods: ['POST'])]
    public function updateProduct(RequestDataBag $data, Context $context): Response
    {
        $definition = new DataValidationDefinition('product.update');
        $definition
            ->add('id', new Assert\NotBlank(), new Assert\Uuid())
            ->add('price', new Assert\NotBlank(), new Assert\Type('numeric'), new Assert\Positive())
            ->add('description', new Assert\Length(['max' => 5000]));

        $this->validator->validate($data->all(), $definition);

        $productId = $data->get('id');
        $price = (float) $data->get('price');
        $description = strip_tags($data->get('description', ''));

        $this->productRepository->update([
            [
                'id' => $productId,
                'price' => [['currencyId' => Defaults::CURRENCY, 'gross' => $price, 'net' => $price, 'linked' => false]],
                'description' => htmlspecialchars($description, ENT_QUOTES, 'UTF-8'),
            ]
        ], $context);

        return new JsonResponse(['success' => true]);
    }
}
```

### 4.2 Implement Proper Authentication

Every route must be properly scoped, and controllers must validate the SalesChannelContext or AdminContext.

**Correct route scopes and authentication:**

```php
// Store API route with proper authentication
#[Route(defaults: ['_routeScope' => ['store-api']])]
class CustomerOrderController extends AbstractController
{
    #[Route(
        path: '/store-api/customer/orders',
        name: 'store-api.customer.orders',
        methods: ['GET'],
        defaults: ['_loginRequired' => true]
    )]
    public function getCustomerOrders(Request $request, SalesChannelContext $context): Response
    {
        $customer = $context->getCustomer();
        $criteria = new Criteria();
        $criteria->addFilter(new EqualsFilter('orderCustomer.customerId', $customer->getId()));
        return new JsonResponse($this->orderRepository->search($criteria, $context->getContext()));
    }
}

// Admin API route with ACL
#[Route(defaults: ['_routeScope' => ['api']])]
class AdminUserController extends AbstractController
{
    #[Route(path: '/api/admin/users', name: 'api.admin.users', methods: ['GET'])]
    public function getUsers(Context $context): Response
    {
        $users = $this->userRepository->search(new Criteria(), $context);
        return new JsonResponse(['users' => $users->getElements()]);
    }
}
```

### 4.3 Implement Proper Authorization with ACL

Every admin action must verify the user has appropriate privileges.

**Correct ACL implementation:**

```php
use Shopware\Core\Framework\Routing\Annotation\Acl;

#[Route(defaults: ['_routeScope' => ['api']])]
class ProductAdminController extends AbstractController
{
    #[Route(path: '/api/_action/product/bulk-delete', name: 'api.action.product.bulk-delete', methods: ['POST'])]
    #[Acl(['product.deleter'])]
    public function bulkDeleteProducts(RequestDataBag $data, Context $context): Response
    {
        $ids = $data->get('ids')->all();
        $deleteData = array_map(fn(string $id) => ['id' => $id], $ids);
        $this->productRepository->delete($deleteData, $context);
        return new JsonResponse(['success' => true, 'deleted' => count($ids)]);
    }
}
```

### 4.4 Prevent SQL Injection

Always use Shopware's DAL for database operations. When raw SQL is necessary, use parameterized queries with DBAL.

**Correct DAL usage:**

```php
public function searchProducts(string $searchTerm, Context $context): EntitySearchResult
{
    $criteria = new Criteria();
    $criteria->addFilter(new ContainsFilter('name', $searchTerm));
    return $this->productRepository->search($criteria, $context);
}
```

**Correct parameterized DBAL:**

```php
public function getOrdersByStatus(string $status): array
{
    $sql = 'SELECT * FROM `order` WHERE status = :status';
    return $this->connection->fetchAllAssociative($sql, [
        'status' => $status
    ], [
        'status' => \PDO::PARAM_STR
    ]);
}

public function getCustomersByIds(array $ids): array
{
    $sql = 'SELECT * FROM customer WHERE id IN (:ids)';
    return $this->connection->fetchAllAssociative($sql, [
        'ids' => $ids
    ], [
        'ids' => ArrayParameterType::STRING
    ]);
}
```

> See full details: `rules/security-input-validation.md`, `rules/security-authentication.md`, `rules/security-authorization.md`, `rules/security-csrf-protection.md`, `rules/security-sql-injection.md`

---

## 5. Data Abstraction Layer

**Impact:** HIGH
**Description:** Proper use of repositories, Criteria objects, entity definitions, associations, and write operations ensures data integrity and performance.

### 5.1 DAL Criteria Usage

**Correct criteria patterns:**

```php
// Always set appropriate limits
public function getProducts(Context $context, int $limit = 25, int $offset = 0): EntitySearchResult
{
    $criteria = new Criteria();
    $criteria->setLimit($limit);
    $criteria->setOffset($offset);
    $criteria->setTotalCountMode(Criteria::TOTAL_COUNT_MODE_EXACT);
    return $this->productRepository->search($criteria, $context);
}

// Combined filters with MultiFilter
public function findActiveExpensiveProducts(Context $context): EntitySearchResult
{
    $criteria = new Criteria();
    $criteria->addFilter(new MultiFilter(
        MultiFilter::CONNECTION_AND,
        [
            new EqualsFilter('active', true),
            new RangeFilter('price.gross', [RangeFilter::GTE => 100])
        ]
    ));
    $criteria->setLimit(50);
    return $this->productRepository->search($criteria, $context);
}
```

### 5.2 DAL Associations

Shopware 6 DAL does not automatically load associations. You must explicitly request associations.

**Correct association loading:**

```php
public function getProductManufacturerName(string $productId, Context $context): ?string
{
    $criteria = new Criteria([$productId]);
    $criteria->addAssociation('manufacturer');
    $product = $this->productRepository->search($criteria, $context)->first();
    return $product?->getManufacturer()?->getName();
}

// Filter associations
public function getProductWithActiveMedia(string $productId, Context $context): ?ProductEntity
{
    $criteria = new Criteria([$productId]);
    $criteria->addAssociation('media');
    $criteria->getAssociation('media')
        ->addFilter(new EqualsFilter('media.private', false))
        ->addSorting(new FieldSorting('position', FieldSorting::ASCENDING))
        ->setLimit(10);
    return $this->productRepository->search($criteria, $context)->first();
}
```

### 5.3 DAL Write Operations

Use the correct method and batch operations for performance.

**Correct write patterns:**

```php
// Batch all updates
public function updateProductPrices(array $priceUpdates, Context $context): void
{
    $updates = [];
    foreach ($priceUpdates as $productId => $newPrice) {
        $updates[] = [
            'id' => $productId,
            'price' => [[
                'currencyId' => Defaults::CURRENCY,
                'gross' => $newPrice,
                'net' => $newPrice / 1.19,
                'linked' => true
            ]]
        ];
    }
    if (!empty($updates)) {
        $this->productRepository->update($updates, $context);
    }
}

// Use upsert for sync scenarios
public function syncProducts(array $externalProducts, Context $context): void
{
    $upsertData = [];
    foreach ($externalProducts as $product) {
        $upsertData[] = [
            'id' => $this->getProductIdByNumber($product['sku'], $context) ?? Uuid::randomHex(),
            'productNumber' => $product['sku'],
            'name' => $product['name'],
            'stock' => $product['stock'],
            'price' => [[
                'currencyId' => Defaults::CURRENCY,
                'gross' => $product['price'],
                'net' => $product['price'] / 1.19,
                'linked' => true
            ]],
            'taxId' => $this->getDefaultTaxId($context),
        ];
    }
    if (!empty($upsertData)) {
        $this->productRepository->upsert($upsertData, $context);
    }
}
```

> See full details: `rules/dal-criteria-usage.md`, `rules/dal-associations.md`, `rules/dal-write-operations.md`, `rules/dal-entity-extensions.md`, `rules/dal-custom-entities.md`

---

## 6. API Development

**Impact:** HIGH
**Description:** Store API routes, Admin API endpoints, authentication, response formatting, and API versioning patterns for robust integrations.

### 6.1 Store API Routes

Store API routes must follow the abstract class pattern to be decoratable.

**Correct Store API route:**

```php
// Abstract class
abstract class AbstractMyFeatureRoute
{
    abstract public function getDecorated(): AbstractMyFeatureRoute;
    abstract public function load(Criteria $criteria, SalesChannelContext $context): MyFeatureRouteResponse;
}

// Concrete implementation
#[Route(defaults: ['_routeScope' => ['store-api']])]
class MyFeatureRoute extends AbstractMyFeatureRoute
{
    public function __construct(
        private readonly EntityRepository $myFeatureRepository
    ) {}

    public function getDecorated(): AbstractMyFeatureRoute
    {
        throw new DecorationPatternException(self::class);
    }

    #[Route(
        path: '/store-api/my-plugin/feature',
        name: 'store-api.my-plugin.feature.load',
        methods: ['GET', 'POST'],
        defaults: ['_loginRequired' => false]
    )]
    public function load(Criteria $criteria, SalesChannelContext $context): MyFeatureRouteResponse
    {
        $result = $this->myFeatureRepository->search($criteria, $context->getContext());
        return new MyFeatureRouteResponse($result);
    }
}

// Response struct
class MyFeatureRouteResponse extends StoreApiResponse
{
    public function __construct(EntitySearchResult $result)
    {
        parent::__construct(new ArrayStruct([
            'elements' => $result->getElements(),
            'total' => $result->getTotal(),
        ], 'my_feature_result'));
    }
}
```

### 6.2 Admin API Routes

Admin API routes require proper authentication scopes and ACL.

**Correct Admin API route:**

```php
#[Route(defaults: ['_routeScope' => ['api']])]
class MyPluginApiController extends AbstractController
{
    #[Route(
        path: '/api/_action/my-plugin/process',
        name: 'api.action.my-plugin.process',
        methods: ['POST'],
        defaults: ['_acl' => ['product:read', 'product:update']]
    )]
    public function process(Request $request, Context $context): JsonResponse
    {
        $productId = $request->request->get('productId');

        if (!$productId) {
            return new JsonResponse(
                ['errors' => [['status' => '400', 'detail' => 'productId is required']]],
                Response::HTTP_BAD_REQUEST
            );
        }

        return new JsonResponse([
            'data' => ['id' => $productId, 'processed' => true]
        ]);
    }
}
```

> See full details: `rules/api-store-api-routes.md`, `rules/api-admin-api-routes.md`, `rules/api-response-handling.md`, `rules/api-rate-limiting.md`, `rules/api-versioning.md`

---

## 7. Event System & Subscribers

**Impact:** MEDIUM-HIGH
**Description:** Proper event subscription, business event handling, and flow actions enable extensible and decoupled architectures.

### 7.1 Business Events for Flow Builder

Implement FlowEventAware events for significant business actions to enable Flow Builder automation.

**Correct business event:**

```php
use Shopware\Core\Framework\Event\FlowEventAware;
use Shopware\Core\Framework\Event\CustomerAware;

class SubscriptionCancelledEvent implements FlowEventAware, CustomerAware
{
    public const EVENT_NAME = 'subscription.cancelled';

    public function __construct(
        private readonly SubscriptionEntity $subscription,
        private readonly Context $context,
        private readonly string $salesChannelId
    ) {}

    public static function getAvailableData(): EventDataCollection
    {
        return (new EventDataCollection())
            ->add('subscription', new EntityType(SubscriptionDefinition::class));
    }

    public function getName(): string { return self::EVENT_NAME; }
    public function getContext(): Context { return $this->context; }
    public function getSalesChannelId(): string { return $this->salesChannelId; }
    public function getCustomerId(): string { return $this->subscription->getCustomerId(); }
}
```

### 7.2 Custom Flow Actions

Implement FlowAction classes to expose plugin functionality in Flow Builder.

**Correct flow action:**

```php
use Shopware\Core\Content\Flow\Dispatching\Action\FlowAction;
use Shopware\Core\Content\Flow\Dispatching\StorableFlow;

class SendToWebhookAction extends FlowAction
{
    public static function getName(): string
    {
        return 'action.send_to_webhook';
    }

    public function requirements(): array
    {
        return [OrderAware::class];
    }

    public function handleFlow(StorableFlow $flow): void
    {
        $webhookUrl = $flow->getConfig()['webhookUrl'] ?? null;
        if (!$webhookUrl) {
            return;
        }
        $orderId = $flow->getData(OrderAware::ORDER_ID);
        $this->httpClient->request('POST', $webhookUrl, ['json' => ['orderId' => $orderId]]);
    }
}
```

> See full details: `rules/event-business-events.md`, `rules/event-flow-actions.md`

---

## 8. Message Queue

**Impact:** MEDIUM
**Description:** Asynchronous message handling, worker configuration, and reliable message processing patterns for background tasks.

### 8.1 Message Handlers

Create dedicated message classes and handlers to offload heavy operations from HTTP requests.

**Correct message and handler:**

```php
// Message class
class ProductImportMessage
{
    public function __construct(
        private readonly array $productData,
        private readonly string $contextToken
    ) {}

    public function getProductData(): array { return $this->productData; }
    public function getContextToken(): string { return $this->contextToken; }
}

// Handler
#[AsMessageHandler]
class ProductImportHandler
{
    public function __invoke(ProductImportMessage $message): void
    {
        $context = $this->contextFactory->create($message->getContextToken());
        $this->productRepository->upsert([$message->getProductData()], $context->getContext());
    }
}

// Controller dispatches async
class ProductImportController extends AbstractController
{
    #[Route(path: '/api/import/products', methods: ['POST'])]
    public function import(Request $request, SalesChannelContext $context): JsonResponse
    {
        $products = json_decode($request->getContent(), true);
        foreach ($products as $productData) {
            $this->messageBus->dispatch(
                new ProductImportMessage($productData, $context->getToken())
            );
        }
        return new JsonResponse(['status' => 'queued', 'count' => count($products)]);
    }
}
```

### 8.2 Low Priority Message Separation

Use LowPriorityMessageInterface for background tasks to ensure urgent operations are not delayed.

```php
use Shopware\Core\Framework\MessageQueue\LowPriorityMessageInterface;

class CacheWarmupMessage implements LowPriorityMessageInterface
{
    public function __construct(private readonly array $cacheIds) {}
}

class StatisticsCalculationMessage implements LowPriorityMessageInterface
{
    public function __construct(private readonly \DateTimeInterface $date) {}
}
```

> See full details: `rules/queue-message-handlers.md`, `rules/queue-worker-config.md`, `rules/queue-low-priority.md`

---

## 9. Database & Migrations

**Impact:** MEDIUM-HIGH
**Description:** Migration best practices, schema design, indexing strategies, and database-level optimizations.

### 9.1 Implement Migrations Correctly

**Correct migration:**

```php
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\Migration;

use Doctrine\DBAL\Connection;
use Shopware\Core\Framework\Migration\MigrationStep;

class Migration1705123456CreateCustomEntity extends MigrationStep
{
    public function getCreationTimestamp(): int
    {
        return 1705123456;
    }

    public function update(Connection $connection): void
    {
        $tableExists = $connection->executeQuery(
            "SHOW TABLES LIKE 'custom_entity'"
        )->rowCount() > 0;

        if ($tableExists) {
            return;
        }

        $connection->executeStatement('
            CREATE TABLE `custom_entity` (
                `id` BINARY(16) NOT NULL,
                `name` VARCHAR(255) NOT NULL,
                `active` TINYINT(1) NOT NULL DEFAULT 0,
                `created_at` DATETIME(3) NOT NULL,
                `updated_at` DATETIME(3) NULL,
                PRIMARY KEY (`id`),
                INDEX `idx.custom_entity.name` (`name`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        ');
    }

    public function updateDestructive(Connection $connection): void
    {
        // Destructive operations only
    }
}
```

> See full details: `rules/db-migrations.md`

---

## 10. Testing

**Impact:** HIGH
**Description:** Unit testing, integration testing, and test infrastructure patterns ensure code quality and regression prevention.

### 10.1 Unit Tests

Use PHPUnit with proper mocking to test components in isolation.

```php
namespace MyPlugin\Tests\Unit\Service;

use PHPUnit\Framework\TestCase;

class PriceCalculatorTest extends TestCase
{
    private PriceCalculator $calculator;
    private EntityRepository $productRepository;

    protected function setUp(): void
    {
        $this->productRepository = $this->createMock(EntityRepository::class);
        $this->calculator = new PriceCalculator($this->productRepository);
    }

    public function testCalculatePriceWithDiscount(): void
    {
        $product = new ProductEntity();
        $product->setCalculatedPrice(new CalculatedPrice(100.0, 100.0, new CalculatedTaxCollection(), new TaxRuleCollection()));

        $searchResult = $this->createMock(EntitySearchResult::class);
        $searchResult->method('first')->willReturn($product);

        $this->productRepository->expects($this->once())->method('search')->willReturn($searchResult);

        $result = $this->calculator->calculateWithDiscount('test-product-id', 10);
        $this->assertEquals(90.0, $result);
    }
}
```

### 10.2 Integration Tests

Use Shopware's integration test traits for proper test isolation.

```php
namespace MyPlugin\Tests\Integration\Service;

use PHPUnit\Framework\TestCase;
use Shopware\Core\Framework\Test\TestCaseBase\IntegrationTestBehaviour;

class ProductServiceTest extends TestCase
{
    use IntegrationTestBehaviour;

    public function testCreateProduct(): void
    {
        $repository = $this->getContainer()->get('product.repository');
        $context = Context::createDefaultContext();
        $productId = Uuid::randomHex();

        $repository->create([
            [
                'id' => $productId,
                'name' => 'Integration Test Product',
                'productNumber' => 'INT-TEST-' . Uuid::randomHex(),
                'stock' => 10,
                'price' => [['currencyId' => Defaults::CURRENCY, 'gross' => 119.99, 'net' => 100.83, 'linked' => false]],
                'taxId' => $this->getValidTaxId(),
            ],
        ], $context);

        $product = $repository->search(new Criteria([$productId]), $context)->first();
        $this->assertEquals('Integration Test Product', $product->getName());
    }
}
```

### 10.3 Store API Tests

Use SalesChannelApiTestBehaviour for Store API testing.

```php
namespace MyPlugin\Tests\Integration\Api;

use PHPUnit\Framework\TestCase;
use Shopware\Core\Framework\Test\TestCaseBase\IntegrationTestBehaviour;
use Shopware\Core\Framework\Test\TestCaseBase\SalesChannelApiTestBehaviour;

class ProductStoreApiTest extends TestCase
{
    use IntegrationTestBehaviour;
    use SalesChannelApiTestBehaviour;

    public function testGetProductList(): void
    {
        $productId = $this->createTestProduct();
        $browser = $this->getBrowser();

        $browser->request('POST', '/store-api/product', [], [],
            ['CONTENT_TYPE' => 'application/json'],
            json_encode(['includes' => ['product' => ['id', 'name']]])
        );

        $response = $browser->getResponse();
        $this->assertEquals(200, $response->getStatusCode());

        $content = json_decode($response->getContent(), true);
        $this->assertContains($productId, array_column($content['elements'], 'id'));
    }
}
```

> See full details: `rules/test-unit-tests.md`, `rules/test-integration-tests.md`, `rules/test-store-api-tests.md`, `rules/test-fixtures.md`

---

## 11. Dependency Injection

**Impact:** MEDIUM
**Description:** Service container usage, proper tagging, and dependency management patterns following Symfony conventions.

### Key Principles

- Use constructor injection, never service locator pattern
- Enable autowiring and autoconfiguration
- Break up large services with many dependencies
- Use tagged services for extensibility

```xml
<services>
    <defaults autowire="true" autoconfigure="true" public="false"/>

    <service id="MyVendor\MyPlugin\Service\OrderProcessingService">
        <argument type="service" id="order.repository"/>
        <argument type="service" id="MyVendor\MyPlugin\Service\PriceCalculationService"/>
        <argument type="service" id="logger"/>
    </service>

    <!-- Tagged services for extensibility -->
    <service id="MyVendor\MyPlugin\Service\ProcessorRegistry">
        <argument type="tagged_iterator" tag="my_plugin.processor"/>
    </service>
</services>
```

> See full details: `rules/di-service-container.md`

---

## 12. Logging & Debugging

**Impact:** MEDIUM
**Description:** Structured logging, debug practices, and observability patterns for effective troubleshooting.

### Key Principles

- Use PSR-3 LoggerInterface, never echo/print
- Never log sensitive data (cards, passwords)
- Use appropriate log levels
- Include context with all log messages

```php
public function processOrder(string $orderId, Context $context): void
{
    $this->logger->info('Starting order processing', ['orderId' => $orderId]);

    try {
        $order = $this->loadOrder($orderId, $context);
        $this->logger->info('Order processed successfully', [
            'orderId' => $orderId,
            'orderNumber' => $order->getOrderNumber(),
        ]);
    } catch (PaymentException $e) {
        $this->logger->error('Payment processing failed', [
            'orderId' => $orderId,
            'errorCode' => $e->getErrorCode(),
            'exception' => $e,
        ]);
        throw $e;
    }
}
```

> See full details: `rules/logging-best-practices.md`

---

## 13. Configuration & Settings

**Impact:** MEDIUM
**Description:** Plugin configuration, system config, and feature flags for flexible and configurable extensions.

### Key Principles

- Use config.xml for admin UI integration
- Create typed configuration service with sales channel awareness
- Validate config values with sensible defaults

```php
class PluginConfigService
{
    private const CONFIG_PREFIX = 'MyVendorMyPlugin.config.';

    public function __construct(private readonly SystemConfigService $systemConfigService) {}

    public function getApiUrl(?string $salesChannelId = null): string
    {
        $value = $this->systemConfigService->get(self::CONFIG_PREFIX . 'apiUrl', $salesChannelId);
        return is_string($value) && $value !== '' ? $value : 'https://api.example.com';
    }

    public function getTimeout(?string $salesChannelId = null): int
    {
        $value = $this->systemConfigService->get(self::CONFIG_PREFIX . 'timeout', $salesChannelId);
        return is_int($value) && $value > 0 ? $value : 30;
    }
}
```

> See full details: `rules/config-plugin-settings.md`

---

## 14. Scheduled Tasks

**Impact:** MEDIUM
**Description:** Proper implementation of scheduled tasks, cron jobs, and recurring background operations.

### Key Principles

- Define proper interval in task class
- Use chunked processing for large datasets
- Dispatch to message queue for parallel processing
- Handle errors gracefully with logging

```php
class ProductSyncTask extends ScheduledTask
{
    public static function getTaskName(): string { return 'my_plugin.product_sync'; }
    public static function getDefaultInterval(): int { return 3600; }
}

#[AsMessageHandler(handles: ProductSyncTask::class)]
class ProductSyncTaskHandler extends ScheduledTaskHandler
{
    public function run(): void
    {
        $this->logger->info('Starting product sync task');
        try {
            $result = $this->syncService->syncProducts(Context::createDefaultContext());
            $this->logger->info('Product sync completed', [
                'synced' => $result->getSyncedCount(),
                'failed' => $result->getFailedCount(),
            ]);
        } catch (\Throwable $e) {
            $this->logger->error('Product sync failed', ['exception' => $e]);
            throw $e;
        }
    }
}
```

> See full details: `rules/scheduled-tasks.md`

---

## 15. Storefront Development

**Impact:** HIGH
**Description:** Twig template extension, JavaScript plugins, SCSS theming, and storefront controller patterns for customizing the customer-facing shop experience.

### 15.1 Storefront Controller Pattern

Extend StorefrontController with proper page loaders for custom pages.

```php
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\Storefront\Controller;

use Shopware\Storefront\Controller\StorefrontController;
use Shopware\Storefront\Page\GenericPageLoaderInterface;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;

#[Route(defaults: ['_routeScope' => ['storefront']])]
class MyPluginController extends StorefrontController
{
    public function __construct(
        private readonly GenericPageLoaderInterface $pageLoader,
        private readonly MyPluginPageLoader $myPageLoader
    ) {}

    #[Route(
        path: '/my-plugin/overview',
        name: 'frontend.my-plugin.overview',
        methods: ['GET']
    )]
    public function overview(Request $request, SalesChannelContext $context): Response
    {
        $page = $this->myPageLoader->load($request, $context);

        return $this->renderStorefront('@MyPlugin/storefront/page/overview.html.twig', [
            'page' => $page
        ]);
    }
}
```

### 15.2 Twig Template Extension

Use `sw_extends` for template inheritance to properly extend storefront templates.

```twig
{# Resources/views/storefront/page/product-detail/index.html.twig #}
{% sw_extends '@Storefront/storefront/page/product-detail/index.html.twig' %}

{% block page_product_detail_buy %}
    {{ parent() }}

    {% block my_plugin_custom_content %}
        <div class="my-plugin-content">
            {% if page.product.extensions.myPluginData %}
                <div class="custom-badge">
                    {{ page.product.extensions.myPluginData.label }}
                </div>
            {% endif %}
        </div>
    {% endblock %}
{% endblock %}
```

### 15.3 JavaScript Plugin System

Register JavaScript plugins following Shopware's plugin pattern.

```javascript
// Resources/app/storefront/src/my-plugin/my-plugin.plugin.js
import Plugin from 'src/plugin-system/plugin.class';
import HttpClient from 'src/service/http-client.service';

export default class MyPlugin extends Plugin {
    static options = {
        apiUrl: '/store-api/my-plugin/data',
        loadingClass: 'is-loading'
    };

    init() {
        this._client = new HttpClient();
        this._registerEvents();
    }

    _registerEvents() {
        this.el.addEventListener('click', this._onClick.bind(this));
    }

    _onClick(event) {
        event.preventDefault();
        this.el.classList.add(this.options.loadingClass);

        this._client.get(this.options.apiUrl, (response) => {
            this._handleResponse(JSON.parse(response));
            this.el.classList.remove(this.options.loadingClass);
        });
    }
}

// main.js - Registration
import MyPlugin from './my-plugin/my-plugin.plugin';
const PluginManager = window.PluginManager;
PluginManager.register('MyPlugin', MyPlugin, '[data-my-plugin]');
```

> See full details: `rules/storefront-controller-pattern.md`, `rules/storefront-twig-extension.md`, `rules/storefront-js-plugins.md`, `rules/storefront-themes.md`, `rules/storefront-scss-variables.md`, `rules/storefront-http-client.md`

---

## 16. Administration Development

**Impact:** HIGH
**Description:** Vue.js module development, component patterns, data handling, ACL permissions, and Extension API for customizing the admin interface.

### 16.1 Module Registration

Register admin modules with proper routes and navigation.

```javascript
// Resources/app/administration/src/module/my-plugin/index.js
Shopware.Module.register('my-plugin', {
    type: 'plugin',
    name: 'my-plugin',
    title: 'my-plugin.general.title',
    description: 'my-plugin.general.description',
    color: '#ff3d58',
    icon: 'default-shopping-paper-bag-product',

    routes: {
        list: {
            component: 'my-plugin-list',
            path: 'list',
            meta: {
                privilege: 'my_plugin.viewer'
            }
        },
        detail: {
            component: 'my-plugin-detail',
            path: 'detail/:id',
            meta: {
                privilege: 'my_plugin.viewer',
                parentPath: 'my.plugin.list'
            }
        }
    },

    navigation: [{
        id: 'my-plugin',
        label: 'my-plugin.navigation.label',
        path: 'my.plugin.list',
        parent: 'sw-catalogue',
        privilege: 'my_plugin.viewer',
        position: 100
    }]
});
```

### 16.2 Component Pattern

Create Vue components following Shopware's patterns.

```javascript
// Resources/app/administration/src/module/my-plugin/page/my-plugin-list/index.js
const { Component, Mixin } = Shopware;
const { Criteria } = Shopware.Data;

Component.register('my-plugin-list', {
    template,

    inject: ['repositoryFactory', 'acl'],

    mixins: [
        Mixin.getByName('listing'),
        Mixin.getByName('notification')
    ],

    data() {
        return {
            items: null,
            isLoading: false
        };
    },

    computed: {
        repository() {
            return this.repositoryFactory.create('my_plugin_entity');
        },

        columns() {
            return [
                { property: 'name', label: 'Name', primary: true },
                { property: 'active', label: 'Active' },
                { property: 'createdAt', label: 'Created' }
            ];
        }
    },

    methods: {
        async getList() {
            this.isLoading = true;
            const criteria = new Criteria(this.page, this.limit);
            criteria.addSorting(Criteria.sort('createdAt', 'DESC'));

            try {
                const result = await this.repository.search(criteria);
                this.items = result;
                this.total = result.total;
            } catch (error) {
                this.createNotificationError({ message: error.message });
            } finally {
                this.isLoading = false;
            }
        }
    }
});
```

> See full details: `rules/admin-module-structure.md`, `rules/admin-components.md`, `rules/admin-data-handling.md`, `rules/admin-acl-permissions.md`, `rules/admin-mixins-composables.md`, `rules/admin-extension-api.md`

---

## 17. App System

**Impact:** HIGH
**Description:** App manifest configuration, webhooks, action buttons, payment handlers, custom fields, and app scripts for building Shopware apps.

### 17.1 Manifest Configuration

Configure apps with a complete manifest.xml.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<manifest xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
          xsi:noNamespaceSchemaLocation="https://raw.githubusercontent.com/shopware/platform/trunk/src/Core/Framework/App/Manifest/Schema/manifest-2.0.xsd">
    <meta>
        <name>MyApp</name>
        <label>My Awesome App</label>
        <label lang="de-DE">Meine tolle App</label>
        <description>App description</description>
        <author>My Company</author>
        <copyright>(c) My Company</copyright>
        <version>1.0.0</version>
        <license>MIT</license>
    </meta>

    <setup>
        <registrationUrl>https://my-app.example.com/register</registrationUrl>
        <secret>your-app-secret</secret>
    </setup>

    <permissions>
        <read>product</read>
        <read>order</read>
        <update>product</update>
    </permissions>

    <webhooks>
        <webhook name="orderPlaced" url="https://my-app.example.com/webhook/order" event="checkout.order.placed"/>
    </webhooks>

    <admin>
        <action-button action="sync" entity="product" view="detail" url="https://my-app.example.com/action/sync">
            <label>Sync Product</label>
        </action-button>
    </admin>
</manifest>
```

### 17.2 Webhook Handling

Handle webhooks with proper signature verification.

```php
class WebhookController
{
    public function handleWebhook(Request $request): Response
    {
        $shopSignature = $request->headers->get('shopware-shop-signature');
        $body = $request->getContent();

        // Verify signature
        $hmac = hash_hmac('sha256', $body, $this->appSecret);
        if (!hash_equals($hmac, $shopSignature)) {
            return new Response('Invalid signature', 401);
        }

        $payload = json_decode($body, true);
        $eventName = $payload['source']['event'];

        // Process event
        match ($eventName) {
            'checkout.order.placed' => $this->handleOrderPlaced($payload),
            'product.written' => $this->handleProductWritten($payload),
            default => null
        };

        return new Response('', 200);
    }
}
```

> See full details: `rules/app-manifest.md`, `rules/app-webhooks.md`, `rules/app-custom-actions.md`, `rules/app-payment-methods.md`, `rules/app-custom-fields.md`, `rules/app-scripts.md`

---

## 18. Integration Patterns

**Impact:** HIGH
**Description:** Payment handlers, shipping methods, CMS elements, import/export profiles, and external API integration patterns.

### 18.1 Payment Handler

Implement async payment handlers for payment integrations.

```php
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\Checkout\Payment;

use Shopware\Core\Checkout\Payment\Cart\AsyncPaymentTransactionStruct;
use Shopware\Core\Checkout\Payment\Cart\PaymentHandler\AsynchronousPaymentHandlerInterface;
use Shopware\Core\Framework\Validation\DataBag\RequestDataBag;
use Shopware\Core\System\SalesChannel\SalesChannelContext;
use Symfony\Component\HttpFoundation\RedirectResponse;
use Symfony\Component\HttpFoundation\Request;

class MyPaymentHandler implements AsynchronousPaymentHandlerInterface
{
    public function pay(
        AsyncPaymentTransactionStruct $transaction,
        RequestDataBag $dataBag,
        SalesChannelContext $context
    ): RedirectResponse {
        $order = $transaction->getOrder();
        $returnUrl = $transaction->getReturnUrl();

        // Create payment at gateway
        $gatewayResponse = $this->paymentGateway->createPayment([
            'amount' => $order->getAmountTotal(),
            'currency' => $context->getCurrency()->getIsoCode(),
            'reference' => $order->getOrderNumber(),
            'returnUrl' => $returnUrl
        ]);

        // Store transaction ID
        $this->transactionStateHandler->process(
            $transaction->getOrderTransaction()->getId(),
            $context->getContext()
        );

        return new RedirectResponse($gatewayResponse->getRedirectUrl());
    }

    public function finalize(
        AsyncPaymentTransactionStruct $transaction,
        Request $request,
        SalesChannelContext $context
    ): void {
        $paymentId = $request->query->get('payment_id');
        $status = $this->paymentGateway->getStatus($paymentId);

        if ($status === 'paid') {
            $this->transactionStateHandler->paid(
                $transaction->getOrderTransaction()->getId(),
                $context->getContext()
            );
        } else {
            throw PaymentException::asyncFinalizeInterrupted(
                $transaction->getOrderTransaction()->getId(),
                'Payment was not successful'
            );
        }
    }
}
```

### 18.2 CMS Element

Create custom CMS elements with data resolvers.

```php
// Data Resolver
class MyProductSliderCmsElementResolver extends AbstractCmsElementResolver
{
    public function getType(): string
    {
        return 'my-product-slider';
    }

    public function collect(CmsSlotEntity $slot, ResolverContext $resolverContext): ?CriteriaCollection
    {
        $config = $slot->getFieldConfig();
        $productIds = $config->get('products')->getArrayValue();

        $criteria = new Criteria($productIds);
        $criteria->addAssociation('cover');

        $collection = new CriteriaCollection();
        $collection->add('products_' . $slot->getUniqueIdentifier(), ProductDefinition::class, $criteria);

        return $collection;
    }

    public function enrich(CmsSlotEntity $slot, ResolverContext $resolverContext, ElementDataCollection $result): void
    {
        $products = $result->get('products_' . $slot->getUniqueIdentifier());
        $slot->setData($products);
    }
}
```

> See full details: `rules/integration-payment-handler.md`, `rules/integration-shipping-method.md`, `rules/integration-cms-elements.md`, `rules/integration-import-export.md`, `rules/integration-external-api.md`

---

## 19. CLI Commands

**Impact:** MEDIUM
**Description:** Custom console commands, command lifecycle, argument/option handling, and progress output for automation and maintenance tasks.

### 19.1 Custom Command

Create CLI commands following Symfony conventions.

```php
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\Command;

use Symfony\Component\Console\Attribute\AsCommand;
use Symfony\Component\Console\Command\Command;
use Symfony\Component\Console\Input\InputArgument;
use Symfony\Component\Console\Input\InputOption;
use Symfony\Component\Console\Input\InputInterface;
use Symfony\Component\Console\Output\OutputInterface;
use Symfony\Component\Console\Style\SymfonyStyle;

#[AsCommand(
    name: 'my-plugin:sync-products',
    description: 'Synchronize products from external system'
)]
class SyncProductsCommand extends Command
{
    protected function configure(): void
    {
        $this
            ->addArgument('source', InputArgument::REQUIRED, 'Source system identifier')
            ->addOption('limit', 'l', InputOption::VALUE_OPTIONAL, 'Limit number of products', 100)
            ->addOption('dry-run', null, InputOption::VALUE_NONE, 'Simulate without changes');
    }

    protected function execute(InputInterface $input, OutputInterface $output): int
    {
        $io = new SymfonyStyle($input, $output);
        $source = $input->getArgument('source');
        $limit = (int) $input->getOption('limit');
        $dryRun = $input->getOption('dry-run');

        $io->title('Product Synchronization');

        $products = $this->fetchProducts($source, $limit);
        $io->progressStart(count($products));

        foreach ($products as $product) {
            if (!$dryRun) {
                $this->syncProduct($product);
            }
            $io->progressAdvance();
        }

        $io->progressFinish();
        $io->success(sprintf('Synchronized %d products', count($products)));

        return Command::SUCCESS;
    }
}
```

> See full details: `rules/cli-commands.md`, `rules/cli-command-lifecycle.md`, `rules/cli-progress-output.md`

---

## 20. Multi-Channel & B2B

**Impact:** MEDIUM-HIGH
**Description:** Sales channel awareness, B2B commerce patterns, advanced pricing, and context management for multi-channel shops.

### 20.1 Sales Channel Awareness

Always consider sales channel context in services.

```php
class MyService
{
    public function getDataForChannel(SalesChannelContext $context): array
    {
        $criteria = new Criteria();

        // Filter by sales channel visibility
        $criteria->addFilter(new MultiFilter(MultiFilter::CONNECTION_OR, [
            new EqualsFilter('visibilities.salesChannelId', $context->getSalesChannelId()),
            new EqualsFilter('visibilities.visibility', ProductVisibilityDefinition::VISIBILITY_ALL)
        ]));

        // Currency-aware pricing
        $criteria->addFilter(new EqualsFilter('prices.currencyId', $context->getCurrencyId()));

        // Customer group pricing
        if ($context->getCurrentCustomerGroup()) {
            $criteria->addFilter(new EqualsFilter(
                'prices.quantityStart',
                $context->getCurrentCustomerGroup()->getId()
            ));
        }

        return $this->repository->search($criteria, $context->getContext())->getElements();
    }
}
```

### 20.2 B2B Patterns

Handle company accounts and employee roles.

```php
class B2BOrderService
{
    public function placeOrder(Cart $cart, SalesChannelContext $context): string
    {
        $customer = $context->getCustomer();

        // Get company context
        $company = $customer->getExtension('company');
        if (!$company) {
            throw new B2BException('Customer not associated with company');
        }

        // Check employee budget
        $employee = $customer->getExtension('b2bEmployee');
        $budget = $employee->getRemainingBudget();

        if ($cart->getPrice()->getTotalPrice() > $budget) {
            // Route to approval workflow
            return $this->createApprovalRequest($cart, $context);
        }

        return $this->orderService->createOrder($cart, $context);
    }
}
```

> See full details: `rules/multichannel-saleschannel.md`, `rules/multichannel-b2b-patterns.md`, `rules/multichannel-pricing.md`, `rules/multichannel-context.md`

---

## 21. DevOps & Tooling

**Impact:** MEDIUM
**Description:** Development environment setup, deployment, static analysis, debugging, and CI/CD pipelines for professional Shopware development.

### 21.1 Development Setup with Dockware

Use Dockware for consistent development environments.

```yaml
# docker-compose.yml
version: '3.8'
services:
  shopware:
    image: dockware/dev:6.6.0.0
    container_name: shopware
    ports:
      - "80:80"
      - "443:443"
      - "8888:8888"  # Adminer
      - "9998:9998"  # Xdebug
    volumes:
      - ./custom/plugins:/var/www/html/custom/plugins
      - ./config:/var/www/html/config
    environment:
      - XDEBUG_ENABLED=1
      - PHP_VERSION=8.2
```

### 21.2 CI/CD Pipeline

Configure automated testing and deployment.

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup PHP
        uses: shivammathur/setup-php@v2
        with:
          php-version: '8.2'
          tools: composer, cs2pr

      - name: Install dependencies
        run: composer install --no-progress

      - name: PHPStan
        run: vendor/bin/phpstan analyse src --level=8

      - name: PHP-CS-Fixer
        run: vendor/bin/php-cs-fixer fix --dry-run --diff

      - name: PHPUnit
        run: vendor/bin/phpunit --coverage-text
```

> See full details: `rules/devops-development-setup.md`, `rules/devops-deployment.md`, `rules/devops-static-analysis.md`, `rules/devops-debugging.md`, `rules/devops-ci-cd.md`

---

## 22. Common Patterns

**Impact:** HIGH
**Description:** Error handling, translations, media handling, rule builder conditions, and version upgrade patterns that apply across all Shopware development.

### 22.1 Exception Handling

Create custom exceptions extending ShopwareHttpException.

```php
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\Exception;

use Shopware\Core\Framework\ShopwareHttpException;

class ProductSyncException extends ShopwareHttpException
{
    public const PRODUCT_NOT_FOUND = 'MY_PLUGIN__PRODUCT_NOT_FOUND';

    public static function productNotFound(string $productId): self
    {
        return new self(
            Response::HTTP_NOT_FOUND,
            self::PRODUCT_NOT_FOUND,
            'Product with ID "{{ productId }}" not found.',
            ['productId' => $productId]
        );
    }

    public function getErrorCode(): string
    {
        return $this->errorCode;
    }
}
```

### 22.2 Translations

Use snippets for UI and entity translations for data.

```json
// Resources/snippet/en_GB/storefront.en-GB.json
{
    "myPlugin": {
        "product": {
            "syncButton": "Sync Product",
            "syncSuccess": "Product synced successfully.",
            "syncFailed": "Sync failed: %reason%"
        }
    }
}
```

```php
// Entity with translations
class MyEntityDefinition extends EntityDefinition
{
    protected function defineFields(): FieldCollection
    {
        return new FieldCollection([
            (new IdField('id', 'id'))->addFlags(new PrimaryKey(), new Required()),
            (new TranslatedField('name')),
            (new TranslatedField('description')),
            (new TranslationsAssociationField(MyEntityTranslationDefinition::class, 'my_entity_id'))
        ]);
    }
}
```

### 22.3 Media Handling

Use Shopware's media service for uploads.

```php
class MediaUploadService
{
    public function uploadFromUrl(string $url, string $fileName, Context $context): string
    {
        $mediaId = Uuid::randomHex();

        $this->mediaRepository->create([
            ['id' => $mediaId, 'mediaFolderId' => $this->getFolderId($context)]
        ], $context);

        $this->mediaService->saveMediaFile(
            $this->downloadFile($url),
            $fileName,
            $context,
            'my_plugin_media',
            $mediaId
        );

        return $mediaId;
    }
}
```

> See full details: `rules/pattern-error-handling.md`, `rules/pattern-translations.md`, `rules/pattern-media-handling.md`, `rules/pattern-rule-builder.md`, `rules/pattern-upgrade-migration.md`

---

## References

- [Shopware Developer Documentation](https://developer.shopware.com/docs/)
- [Plugin Base Guide](https://developer.shopware.com/docs/guides/plugins/plugins/plugin-base-guide.html)
- [Data Abstraction Layer](https://developer.shopware.com/docs/concepts/framework/data-abstraction-layer.html)
- [API Concepts](https://developer.shopware.com/docs/concepts/api/)
- [Caching Documentation](https://developer.shopware.com/docs/guides/hosting/performance/caches.html)

---

*This document is designed for AI agents and LLMs to understand and apply Shopware 6 best practices for code generation, refactoring, and automated development workflows.*
