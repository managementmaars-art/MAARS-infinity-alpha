---
title: API Versioning
impact: MEDIUM
impactDescription: Proper API versioning ensures backwards compatibility and allows consumers to migrate to new versions gracefully
tags: [shopware6, api, versioning, backwards-compatibility, deprecation]
---

## API Versioning

Shopware 6 APIs should follow versioning best practices to maintain backwards compatibility. Use deprecation notices, version-aware routes, and gradual migration paths for API changes.

Reference: https://developer.shopware.com/docs/guides/plugins/plugins/framework/api/

### Incorrect

```php
<?php

// Bad: Breaking changes without version handling
namespace MyPlugin\Controller\Api;

use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\Routing\Attribute\Route;

#[Route(defaults: ['_routeScope' => ['api']])]
class BadVersioningController extends AbstractController
{
    // Bad: Changing response structure without versioning
    #[Route(path: '/api/_action/my-plugin/data', methods: ['GET'])]
    public function getData(): JsonResponse
    {
        // Bad: Response structure changed from v1, breaking existing integrations
        // Was: ['items' => [...]] - Now: ['data' => ['items' => [...]]]
        return new JsonResponse([
            'data' => [
                'items' => $this->getItems(),
            ]
        ]);
    }

    // Bad: Removing endpoint without deprecation period
    // Previously: /api/_action/my-plugin/legacy was removed without notice
}
```

```php
<?php

// Bad: Parameter changes without backwards compatibility
namespace MyPlugin\Controller\Api;

use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\Routing\Attribute\Route;

#[Route(defaults: ['_routeScope' => ['api']])]
class BadParameterController extends AbstractController
{
    // Bad: Required parameter changed from 'id' to 'entityId' without support for old name
    #[Route(path: '/api/_action/my-plugin/process', methods: ['POST'])]
    public function process(Request $request): JsonResponse
    {
        $entityId = $request->request->get('entityId'); // Bad: 'id' no longer works

        return new JsonResponse(['processed' => $entityId]);
    }
}
```

### Correct

```php
<?php

// Good: Version-aware controller with deprecation handling
namespace MyPlugin\Controller\Api;

use Shopware\Core\Framework\Context;
use Shopware\Core\Framework\Log\Package;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;

#[Route(defaults: ['_routeScope' => ['api']])]
#[Package('my-plugin')]
class VersionedApiController extends AbstractController
{
    // Good: Maintain old endpoint with deprecation notice
    #[Route(
        path: '/api/_action/my-plugin/v1/data',
        name: 'api.action.my-plugin.v1.data',
        methods: ['GET'],
        defaults: ['_acl' => ['my_plugin:read']]
    )]
    public function getDataV1(Context $context): JsonResponse
    {
        // Good: Log deprecation for monitoring
        trigger_deprecation(
            'my-plugin',
            '2.0.0',
            'Route /api/_action/my-plugin/v1/data is deprecated, use /api/_action/my-plugin/v2/data instead'
        );

        $items = $this->getItems($context);

        // Good: Maintain old response structure for v1
        $response = new JsonResponse(['items' => $items]);

        // Good: Add deprecation headers
        $response->headers->set('X-Deprecated', 'true');
        $response->headers->set('X-Deprecated-Since', '2.0.0');
        $response->headers->set('X-Sunset', '2025-12-31');
        $response->headers->set('Link', '</api/_action/my-plugin/v2/data>; rel="successor-version"');

        return $response;
    }

    // Good: New version with improved structure
    #[Route(
        path: '/api/_action/my-plugin/v2/data',
        name: 'api.action.my-plugin.v2.data',
        methods: ['GET'],
        defaults: ['_acl' => ['my_plugin:read']]
    )]
    public function getDataV2(Context $context): JsonResponse
    {
        $items = $this->getItems($context);

        // Good: New response structure with metadata
        return new JsonResponse([
            'data' => [
                'type' => 'item_collection',
                'items' => $items,
            ],
            'meta' => [
                'total' => count($items),
                'apiVersion' => '2',
            ],
        ]);
    }

    // Good: Parameter backwards compatibility
    #[Route(
        path: '/api/_action/my-plugin/process',
        name: 'api.action.my-plugin.process',
        methods: ['POST'],
        defaults: ['_acl' => ['my_plugin:update']]
    )]
    public function process(Request $request, Context $context): JsonResponse
    {
        // Good: Support both old and new parameter names
        $entityId = $request->request->get('entityId') ?? $request->request->get('id');

        // Good: Log when deprecated parameter is used
        if ($request->request->has('id') && !$request->request->has('entityId')) {
            trigger_deprecation(
                'my-plugin',
                '2.0.0',
                'Parameter "id" is deprecated, use "entityId" instead'
            );
        }

        if (!$entityId) {
            return new JsonResponse(
                ['errors' => [['detail' => 'entityId is required']]],
                Response::HTTP_BAD_REQUEST
            );
        }

        return new JsonResponse(['processed' => $entityId]);
    }
}
```

```php
<?php

// Good: Abstract route with version support for Store API
namespace MyPlugin\Core\Content\MyFeature\SalesChannel;

use Shopware\Core\Framework\DataAbstractionLayer\Search\Criteria;
use Shopware\Core\System\SalesChannel\SalesChannelContext;

abstract class AbstractMyFeatureRoute
{
    abstract public function getDecorated(): AbstractMyFeatureRoute;

    // Good: Default implementation for new version
    public function load(Criteria $criteria, SalesChannelContext $context): MyFeatureRouteResponse
    {
        return $this->loadV2($criteria, $context);
    }

    // Good: Explicit version methods
    abstract public function loadV1(Criteria $criteria, SalesChannelContext $context): MyFeatureRouteResponseV1;

    abstract public function loadV2(Criteria $criteria, SalesChannelContext $context): MyFeatureRouteResponse;
}
```

```php
<?php

// Good: Subscriber for API version detection and handling
namespace MyPlugin\Subscriber;

use Symfony\Component\EventDispatcher\EventSubscriberInterface;
use Symfony\Component\HttpKernel\Event\RequestEvent;
use Symfony\Component\HttpKernel\Event\ResponseEvent;
use Symfony\Component\HttpKernel\KernelEvents;

class ApiVersionSubscriber implements EventSubscriberInterface
{
    public static function getSubscribedEvents(): array
    {
        return [
            KernelEvents::REQUEST => 'onRequest',
            KernelEvents::RESPONSE => 'onResponse',
        ];
    }

    public function onRequest(RequestEvent $event): void
    {
        $request = $event->getRequest();

        // Good: Detect API version from header
        $apiVersion = $request->headers->get('X-Api-Version', '2');
        $request->attributes->set('_api_version', $apiVersion);
    }

    public function onResponse(ResponseEvent $event): void
    {
        $response = $event->getResponse();

        // Good: Always include API version in response
        $apiVersion = $event->getRequest()->attributes->get('_api_version', '2');
        $response->headers->set('X-Api-Version', $apiVersion);
    }
}
```

```yaml
# Good: Document deprecations in UPGRADE.md or changelog
# UPGRADE-2.0.md example content:
#
# ## API Changes
#
# ### Deprecated
# - `GET /api/_action/my-plugin/v1/data` - Use v2 endpoint instead (sunset: 2025-12-31)
# - Parameter `id` in process endpoint - Use `entityId` instead
#
# ### Migration Guide
# 1. Update all calls from v1 to v2 endpoints
# 2. Replace `id` parameter with `entityId` in request bodies
# 3. Update response parsing for new data structure
```
