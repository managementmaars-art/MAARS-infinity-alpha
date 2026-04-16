---
title: Store API Routes
impact: HIGH
impactDescription: Store API routes must follow the abstract class pattern to be decoratable and maintain extensibility for other plugins
tags: [shopware6, api, store-api, routes, decoratable]
---

## Store API Routes

Store API routes in Shopware 6 must follow specific patterns to ensure they are decoratable by other plugins and extensions. Always use abstract classes with concrete implementations and proper response objects.

Reference: https://developer.shopware.com/docs/guides/plugins/plugins/framework/store-api/add-store-api-route

### Incorrect

```php
<?php

// Bad: Non-decoratable route without abstract class pattern
namespace MyPlugin\Storefront\Controller;

use Shopware\Core\Framework\Routing\Annotation\RouteScope;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\Routing\Annotation\Route;

#[Route(defaults: ['_routeScope' => ['store-api']])]
class MyApiController extends AbstractController
{
    // Bad: Direct controller implementation, not decoratable
    #[Route(path: '/store-api/my-plugin/data', name: 'store-api.my-plugin.data', methods: ['GET'])]
    public function getData(): JsonResponse
    {
        // Bad: Returning JsonResponse instead of proper response struct
        return new JsonResponse(['data' => 'value']);
    }
}
```

### Correct

```php
<?php

// Good: Abstract route class for decoratability
namespace MyPlugin\Core\Content\MyFeature\SalesChannel;

use Shopware\Core\Framework\DataAbstractionLayer\Search\Criteria;
use Shopware\Core\System\SalesChannel\SalesChannelContext;

abstract class AbstractMyFeatureRoute
{
    abstract public function getDecorated(): AbstractMyFeatureRoute;

    abstract public function load(Criteria $criteria, SalesChannelContext $context): MyFeatureRouteResponse;
}
```

```php
<?php

// Good: Concrete implementation with proper attributes
namespace MyPlugin\Core\Content\MyFeature\SalesChannel;

use Shopware\Core\Framework\DataAbstractionLayer\EntityRepository;
use Shopware\Core\Framework\DataAbstractionLayer\Search\Criteria;
use Shopware\Core\Framework\Plugin\Exception\DecorationPatternException;
use Shopware\Core\System\SalesChannel\SalesChannelContext;
use Symfony\Component\Routing\Attribute\Route;

#[Route(defaults: ['_routeScope' => ['store-api']])]
class MyFeatureRoute extends AbstractMyFeatureRoute
{
    public function __construct(
        private readonly EntityRepository $myFeatureRepository
    ) {
    }

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
```

```php
<?php

// Good: Proper response struct extending StoreApiResponse
namespace MyPlugin\Core\Content\MyFeature\SalesChannel;

use Shopware\Core\Framework\DataAbstractionLayer\Search\EntitySearchResult;
use Shopware\Core\Framework\Struct\ArrayStruct;
use Shopware\Core\System\SalesChannel\StoreApiResponse;

class MyFeatureRouteResponse extends StoreApiResponse
{
    public function __construct(EntitySearchResult $result)
    {
        parent::__construct(new ArrayStruct([
            'elements' => $result->getElements(),
            'total' => $result->getTotal(),
        ], 'my_feature_result'));
    }

    public function getResult(): ArrayStruct
    {
        return $this->object;
    }
}
```

```xml
<!-- Good: Service registration with abstract class binding -->
<service id="MyPlugin\Core\Content\MyFeature\SalesChannel\MyFeatureRoute">
    <argument type="service" id="my_feature.repository"/>
</service>

<service id="MyPlugin\Core\Content\MyFeature\SalesChannel\AbstractMyFeatureRoute"
         alias="MyPlugin\Core\Content\MyFeature\SalesChannel\MyFeatureRoute"/>
```
