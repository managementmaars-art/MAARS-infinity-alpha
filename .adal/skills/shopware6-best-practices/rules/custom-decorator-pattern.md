---
title: Use Decorator Pattern for Service Customization
impact: CRITICAL
impactDescription: enables upgrade-safe service modification
tags: decorator, customization, services, upgrade-safe
---

## Use Decorator Pattern for Service Customization

**Impact: CRITICAL (enables upgrade-safe service modification)**

The decorator pattern is the primary way to customize existing Shopware services while maintaining upgrade compatibility. Never modify core files directly.

**Incorrect (breaking customization approaches):**

```php
// Bad: Modifying core files directly
// vendor/shopware/core/Checkout/Cart/CartService.php
// NEVER modify files in vendor/!

// Bad: Extending without proper decoration
class MyCartService extends CartService
{
    public function add(Cart $cart, LineItem $item, SalesChannelContext $context): Cart
    {
        // This won't be used - original service is still registered!
        return parent::add($cart, $item, $context);
    }
}

// Bad: Not implementing getDecorated()
class BrokenDecorator extends AbstractCartService
{
    public function __construct(
        private readonly AbstractCartService $decorated
    ) {}

    // Missing getDecorated() - breaks decoration chain!

    public function add(Cart $cart, LineItem $item, SalesChannelContext $context): Cart
    {
        return $this->decorated->add($cart, $item, $context);
    }
}
```

**Correct (proper decorator implementation):**

```php
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\Core\Checkout\Cart;

use Shopware\Core\Checkout\Cart\Cart;
use Shopware\Core\Checkout\Cart\CartBehavior;
use Shopware\Core\Checkout\Cart\AbstractCartPersister;
use Shopware\Core\Framework\Plugin\Exception\DecorationPatternException;
use Shopware\Core\System\SalesChannel\SalesChannelContext;

class DecoratedCartPersister extends AbstractCartPersister
{
    public function __construct(
        private readonly AbstractCartPersister $decorated,
        private readonly CartAuditService $auditService
    ) {}

    // Good: Always implement getDecorated() for proper chain
    public function getDecorated(): AbstractCartPersister
    {
        return $this->decorated;
    }

    public function load(string $token, SalesChannelContext $context): Cart
    {
        // Add custom logic before
        $this->auditService->logCartAccess($token, $context);

        // Call decorated service
        $cart = $this->decorated->load($token, $context);

        // Add custom logic after
        $this->enrichCartWithCustomData($cart);

        return $cart;
    }

    public function save(Cart $cart, SalesChannelContext $context): void
    {
        // Modify cart before save
        $this->applyCustomRules($cart);

        // Delegate to decorated
        $this->decorated->save($cart, $context);

        // Post-save actions
        $this->auditService->logCartSave($cart, $context);
    }

    public function delete(string $token, SalesChannelContext $context): void
    {
        $this->decorated->delete($token, $context);
    }

    public function replace(string $oldToken, string $newToken, SalesChannelContext $context): void
    {
        $this->decorated->replace($oldToken, $newToken, $context);
    }

    private function enrichCartWithCustomData(Cart $cart): void
    {
        // Custom enrichment logic
    }

    private function applyCustomRules(Cart $cart): void
    {
        // Custom rule application
    }
}
```

```xml
<!-- Good: Service decoration in services.xml -->
<service id="MyVendor\MyPlugin\Core\Checkout\Cart\DecoratedCartPersister"
         decorates="Shopware\Core\Checkout\Cart\CartPersister">
    <!-- .inner suffix refers to the original service -->
    <argument type="service" id="MyVendor\MyPlugin\Core\Checkout\Cart\DecoratedCartPersister.inner"/>
    <argument type="service" id="MyVendor\MyPlugin\Service\CartAuditService"/>
</service>
```

```php
// Good: Decorator for routes (Store API)
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\Core\Content\Product\SalesChannel;

use Shopware\Core\Content\Product\SalesChannel\AbstractProductListRoute;
use Shopware\Core\Content\Product\SalesChannel\ProductListResponse;
use Shopware\Core\Framework\DataAbstractionLayer\Search\Criteria;
use Shopware\Core\System\SalesChannel\SalesChannelContext;
use Symfony\Component\HttpFoundation\Request;

class DecoratedProductListRoute extends AbstractProductListRoute
{
    public function __construct(
        private readonly AbstractProductListRoute $decorated,
        private readonly CustomFilterService $filterService
    ) {}

    public function getDecorated(): AbstractProductListRoute
    {
        return $this->decorated;
    }

    public function load(
        Criteria $criteria,
        SalesChannelContext $context,
        Request $request
    ): ProductListResponse {
        // Modify criteria before loading
        $this->filterService->applyCustomFilters($criteria, $context);

        // Get response from decorated route
        $response = $this->decorated->load($criteria, $context, $request);

        // Optionally modify response
        $this->enrichResponse($response);

        return $response;
    }
}
```

**Decoration priority:**

```xml
<!-- Control decoration order with priority -->
<service id="MyVendor\FirstDecorator" decorates="original.service" decoration-priority="100">
    <argument type="service" id="MyVendor\FirstDecorator.inner"/>
</service>

<service id="MyVendor\SecondDecorator" decorates="original.service" decoration-priority="50">
    <argument type="service" id="MyVendor\SecondDecorator.inner"/>
</service>
<!-- Higher priority decorates first (outermost) -->
```

**When to use decoration:**

| Scenario | Approach |
|----------|----------|
| Modify service behavior | Decorate the abstract class |
| Add pre/post processing | Decorate and call inner |
| Replace entirely | Decorate, don't call inner |
| Add new functionality | Create new service, inject dependencies |

Reference: [Adjusting a Service](https://developer.shopware.com/docs/guides/plugins/plugins/plugin-fundamentals/adjusting-service.html)
