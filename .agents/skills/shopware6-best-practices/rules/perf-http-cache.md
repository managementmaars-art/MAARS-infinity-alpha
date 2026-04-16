---
title: Configure HTTP Cache Correctly
impact: CRITICAL
impactDescription: enables high-performance storefront with reduced server load
tags: performance, cache, http, varnish, reverse-proxy
---

## Configure HTTP Cache Correctly

**Impact: CRITICAL (enables high-performance storefront with reduced server load)**

HTTP caching is essential for Shopware 6 storefront performance. Proper configuration enables serving cached pages without hitting PHP, dramatically reducing server load.

**Incorrect (cache-breaking patterns):**

```php
// Bad: Not invalidating cache after data changes
class ProductUpdateService
{
    public function updateProduct(string $productId, array $data): void
    {
        $this->productRepository->update([
            ['id' => $productId, ...$data]
        ], $this->context);
        // Missing cache invalidation!
    }
}

// Bad: Using session data in cached responses
class ProductController extends StorefrontController
{
    #[Route(path: '/products/{id}', name: 'frontend.product.detail')]
    public function detail(string $id, Request $request): Response
    {
        // Bad: This varies by session, breaking cache
        $lastViewed = $request->getSession()->get('last_viewed_products');

        return $this->renderStorefront('@MyPlugin/page/product.html.twig', [
            'product' => $product,
            'lastViewed' => $lastViewed,  // Cache varies for every user!
        ]);
    }
}

// Bad: Setting no-cache headers unnecessarily
class MyController extends StorefrontController
{
    #[Route(path: '/my-page', name: 'frontend.my-page')]
    public function index(): Response
    {
        $response = $this->renderStorefront('@MyPlugin/page/my-page.html.twig');

        // Bad: Completely disables caching
        $response->headers->set('Cache-Control', 'no-store, no-cache, must-revalidate');

        return $response;
    }
}
```

**Correct (cache-optimized implementation):**

```php
// Good: Proper cache invalidation
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\Service;

use Shopware\Core\Framework\Adapter\Cache\CacheInvalidator;
use Shopware\Core\Content\Product\ProductDefinition;

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

        // Good: Invalidate related cache tags
        $this->cacheInvalidator->invalidate([
            'product-' . $productId,
            'product-listing',
            CachedProductDetailRoute::buildName($productId),
        ]);
    }
}
```

```php
// Good: Using ESI for dynamic content in cached pages
// In controller - mark response as cacheable
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\Controller;

use Shopware\Storefront\Controller\StorefrontController;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Annotation\Route;

class CachedPageController extends StorefrontController
{
    #[Route(path: '/my-cached-page', name: 'frontend.my-cached-page', defaults: ['_httpCache' => true])]
    public function index(): Response
    {
        return $this->renderStorefront('@MyPlugin/page/cached-page.html.twig', [
            'staticData' => $this->staticDataService->getData(),
        ]);
    }

    // Good: Separate route for dynamic fragment (ESI)
    #[Route(path: '/my-dynamic-fragment', name: 'frontend.my-dynamic-fragment', defaults: ['_httpCache' => false])]
    public function dynamicFragment(SalesChannelContext $context): Response
    {
        return $this->renderStorefront('@MyPlugin/component/dynamic-fragment.html.twig', [
            'userData' => $this->getUserData($context),
        ]);
    }
}
```

```twig
{# Good: Use ESI for dynamic content in cached pages #}
{% block my_cached_page_content %}
    <div class="static-content">
        {{ staticData.content }}
    </div>

    {# Dynamic content loaded via ESI #}
    <div class="dynamic-content">
        {{ render_esi(url('frontend.my-dynamic-fragment')) }}
    </div>
{% endblock %}
```

```php
// Good: Custom cache tags for fine-grained invalidation
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\Core\Content\CustomEntity;

use Shopware\Core\Framework\Adapter\Cache\CacheValueCompressor;
use Shopware\Core\Framework\DataAbstractionLayer\Cache\EntityCacheKeyGenerator;
use Symfony\Contracts\Cache\CacheInterface;
use Symfony\Contracts\Cache\ItemInterface;

class CachedCustomEntityLoader
{
    public function __construct(
        private readonly CacheInterface $cache,
        private readonly CustomEntityLoader $loader,
        private readonly EntityCacheKeyGenerator $keyGenerator
    ) {}

    public function load(string $entityId, Context $context): ?CustomEntity
    {
        $cacheKey = $this->keyGenerator->getEntityContextCacheKey(
            $entityId,
            'custom_entity',
            $context
        );

        return $this->cache->get($cacheKey, function (ItemInterface $item) use ($entityId, $context) {
            // Good: Tag cache entries for targeted invalidation
            $item->tag([
                'custom-entity-' . $entityId,
                'custom-entity-list',
            ]);

            // Set TTL
            $item->expiresAfter(3600);

            return CacheValueCompressor::compress(
                $this->loader->load($entityId, $context)
            );
        });
    }
}
```

```yaml
# Good: HTTP cache configuration in config/packages/shopware.yaml
shopware:
    http_cache:
        enabled: true
        default_ttl: 7200
        stale_while_revalidate: 3600
        stale_if_error: 86400
        ignored_url_parameters:
            - 'pk_campaign'
            - 'utm_source'
            - 'utm_medium'
            - 'gclid'
```

```php
// Good: Conditional caching based on context
#[Route(path: '/products', name: 'frontend.products', defaults: ['_httpCache' => true])]
public function list(Request $request, SalesChannelContext $context): Response
{
    $response = $this->renderStorefront('@Storefront/page/product-list.html.twig', [
        'products' => $products,
    ]);

    // Good: Vary cache by customer group
    $response->headers->set('X-Shopware-Cache-Tags', 'product-listing,customer-group-' . $context->getCurrentCustomerGroup()->getId());

    // Good: Reduce TTL for frequently changing content
    if ($this->hasFlashSale($products)) {
        $response->setSharedMaxAge(300);  // 5 minutes for flash sales
    }

    return $response;
}
```

**Cache configuration checklist:**

| Setting | Production Value | Purpose |
|---------|------------------|---------|
| `SHOPWARE_HTTP_CACHE_ENABLED` | `1` | Enable HTTP cache |
| `default_ttl` | 7200+ | Default cache lifetime |
| `stale_while_revalidate` | 3600 | Serve stale while refreshing |
| `stale_if_error` | 86400 | Serve stale on backend errors |

Reference: [Caching Documentation](https://developer.shopware.com/docs/guides/hosting/performance/caches.html)
