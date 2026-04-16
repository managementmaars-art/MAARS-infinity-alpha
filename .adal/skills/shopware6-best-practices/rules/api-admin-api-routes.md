---
title: Admin API Routes
impact: HIGH
impactDescription: Admin API routes require proper authentication scopes and route configuration to ensure security and correct API behavior
tags: [shopware6, api, admin-api, routes, authentication]
---

## Admin API Routes

Admin API routes must be properly configured with the correct route scope, authentication requirements, and response formatting. These routes are protected and require valid admin authentication.

Reference: https://developer.shopware.com/docs/guides/plugins/plugins/framework/api/add-custom-admin-api-route

### Incorrect

```php
<?php

// Bad: Missing route scope, no authentication handling
namespace MyPlugin\Controller;

use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\Routing\Annotation\Route;

class AdminController extends AbstractController
{
    // Bad: No route scope defined, endpoint exposed without authentication
    #[Route(path: '/api/my-plugin/action', name: 'api.my-plugin.action', methods: ['POST'])]
    public function doAction(): JsonResponse
    {
        // Bad: Direct array response without proper structure
        return new JsonResponse(['success' => true]);
    }
}
```

```php
<?php

// Bad: Wrong scope - using store-api scope for admin endpoint
namespace MyPlugin\Controller;

use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;

#[Route(defaults: ['_routeScope' => ['store-api']])] // Bad: Wrong scope
class AdminController extends AbstractController
{
    #[Route(path: '/api/my-plugin/data', methods: ['GET'])]
    public function getData(): Response
    {
        // Bad: No ACL protection
        return new Response('data');
    }
}
```

### Correct

```php
<?php

// Good: Proper Admin API controller with correct scope and ACL
namespace MyPlugin\Controller\Api;

use Shopware\Core\Framework\Context;
use Shopware\Core\Framework\DataAbstractionLayer\EntityRepository;
use Shopware\Core\Framework\DataAbstractionLayer\Search\Criteria;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;

#[Route(defaults: ['_routeScope' => ['api']])]
class MyPluginApiController extends AbstractController
{
    public function __construct(
        private readonly EntityRepository $productRepository
    ) {
    }

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

        // Process the request
        $criteria = new Criteria([$productId]);
        $product = $this->productRepository->search($criteria, $context)->first();

        if (!$product) {
            return new JsonResponse(
                ['errors' => [['status' => '404', 'detail' => 'Product not found']]],
                Response::HTTP_NOT_FOUND
            );
        }

        return new JsonResponse([
            'data' => [
                'id' => $product->getId(),
                'processed' => true,
            ]
        ]);
    }

    #[Route(
        path: '/api/_action/my-plugin/export',
        name: 'api.action.my-plugin.export',
        methods: ['GET'],
        defaults: ['_acl' => ['my_plugin_export']]
    )]
    public function export(Context $context): JsonResponse
    {
        // Good: Custom ACL privilege for specific functionality
        return new JsonResponse([
            'data' => [
                'type' => 'export',
                'attributes' => [
                    'status' => 'completed',
                    'timestamp' => (new \DateTime())->format(\DateTimeInterface::ATOM),
                ],
            ]
        ]);
    }
}
```

```php
<?php

// Good: Admin API route returning file/binary response
namespace MyPlugin\Controller\Api;

use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\HttpFoundation\StreamedResponse;
use Symfony\Component\Routing\Attribute\Route;

#[Route(defaults: ['_routeScope' => ['api']])]
class ExportController extends AbstractController
{
    #[Route(
        path: '/api/_action/my-plugin/download-report',
        name: 'api.action.my-plugin.download-report',
        methods: ['GET'],
        defaults: ['_acl' => ['my_plugin:read']]
    )]
    public function downloadReport(): StreamedResponse
    {
        $response = new StreamedResponse(function () {
            $handle = fopen('php://output', 'w');
            fputcsv($handle, ['ID', 'Name', 'Value']);
            fputcsv($handle, ['1', 'Example', '100']);
            fclose($handle);
        });

        $response->headers->set('Content-Type', 'text/csv');
        $response->headers->set('Content-Disposition', 'attachment; filename="report.csv"');

        return $response;
    }
}
```

```xml
<!-- Good: Service registration for Admin API controller -->
<service id="MyPlugin\Controller\Api\MyPluginApiController" public="true">
    <argument type="service" id="product.repository"/>
    <tag name="controller.service_arguments"/>
</service>
```
