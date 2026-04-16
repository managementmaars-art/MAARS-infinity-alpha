---
title: Exception Handling & Error Pages
impact: HIGH
impactDescription: graceful error handling for better user experience
tags: error, exception, handling, pages, logging
---

## Exception Handling & Error Pages

**Impact: HIGH (graceful error handling for better user experience)**

Implement proper exception handling with custom exceptions, error logging, and user-friendly error pages.

**Incorrect (generic exceptions):**

```php
// Bad: Generic exceptions without context
throw new \Exception('Something went wrong');

// Bad: Catching all exceptions silently
try {
    $this->process();
} catch (\Exception $e) {
    // Silently ignored
}
```

**Correct custom exceptions:**

```php
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\Exception;

use Shopware\Core\Framework\ShopwareHttpException;
use Symfony\Component\HttpFoundation\Response;

class ProductSyncException extends ShopwareHttpException
{
    public const PRODUCT_NOT_FOUND = 'MY_PLUGIN__PRODUCT_NOT_FOUND';
    public const SYNC_FAILED = 'MY_PLUGIN__SYNC_FAILED';
    public const API_ERROR = 'MY_PLUGIN__API_ERROR';

    public static function productNotFound(string $productId): self
    {
        return new self(
            Response::HTTP_NOT_FOUND,
            self::PRODUCT_NOT_FOUND,
            'Product with ID "{{ productId }}" not found.',
            ['productId' => $productId]
        );
    }

    public static function syncFailed(string $productId, string $reason): self
    {
        return new self(
            Response::HTTP_INTERNAL_SERVER_ERROR,
            self::SYNC_FAILED,
            'Failed to sync product "{{ productId }}": {{ reason }}',
            ['productId' => $productId, 'reason' => $reason]
        );
    }

    public static function apiError(string $endpoint, int $statusCode, string $message): self
    {
        return new self(
            Response::HTTP_BAD_GATEWAY,
            self::API_ERROR,
            'External API error for "{{ endpoint }}": {{ message }} ({{ statusCode }})',
            ['endpoint' => $endpoint, 'statusCode' => $statusCode, 'message' => $message]
        );
    }

    public function getErrorCode(): string
    {
        return $this->errorCode;
    }
}
```

**Correct exception handling in services:**

```php
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\Service;

use MyVendor\MyPlugin\Exception\ProductSyncException;
use Psr\Log\LoggerInterface;

class ProductSyncService
{
    public function __construct(
        private readonly ExternalApiClient $apiClient,
        private readonly EntityRepository $productRepository,
        private readonly LoggerInterface $logger
    ) {}

    public function syncProduct(string $productId, Context $context): SyncResult
    {
        $this->logger->info('Starting product sync', ['productId' => $productId]);

        // Load product
        $product = $this->productRepository->search(
            new Criteria([$productId]),
            $context
        )->first();

        if (!$product) {
            throw ProductSyncException::productNotFound($productId);
        }

        try {
            $externalData = $this->apiClient->syncProduct($product);

            $this->logger->info('Product synced successfully', [
                'productId' => $productId,
                'externalId' => $externalData['id']
            ]);

            return new SyncResult(true, $externalData);

        } catch (ApiException $e) {
            $this->logger->error('External API error during sync', [
                'productId' => $productId,
                'error' => $e->getMessage(),
                'code' => $e->getCode()
            ]);

            throw ProductSyncException::apiError(
                '/products/sync',
                $e->getCode(),
                $e->getMessage()
            );

        } catch (\Throwable $e) {
            $this->logger->critical('Unexpected error during product sync', [
                'productId' => $productId,
                'error' => $e->getMessage(),
                'trace' => $e->getTraceAsString()
            ]);

            throw ProductSyncException::syncFailed($productId, $e->getMessage());
        }
    }
}
```

**Correct Store API error handling:**

```php
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\Storefront\Controller;

use MyVendor\MyPlugin\Exception\ProductSyncException;
use Shopware\Core\Framework\Routing\Exception\MissingRequestParameterException;
use Shopware\Storefront\Controller\StorefrontController;

#[Route(defaults: ['_routeScope' => ['storefront']])]
class MyPluginController extends StorefrontController
{
    #[Route(
        path: '/my-plugin/sync/{productId}',
        name: 'frontend.my-plugin.sync',
        methods: ['POST']
    )]
    public function sync(string $productId, SalesChannelContext $context): Response
    {
        try {
            $result = $this->syncService->syncProduct($productId, $context->getContext());

            $this->addFlash(self::SUCCESS, $this->trans('myPlugin.sync.success'));

            return $this->redirectToRoute('frontend.my-plugin.detail', [
                'productId' => $productId
            ]);

        } catch (ProductSyncException $e) {
            $this->logger->warning('Sync failed', [
                'productId' => $productId,
                'error' => $e->getMessage()
            ]);

            $this->addFlash(self::DANGER, $this->trans('myPlugin.sync.failed', [
                '%reason%' => $e->getMessage()
            ]));

            return $this->redirectToRoute('frontend.my-plugin.detail', [
                'productId' => $productId
            ]);

        } catch (\Throwable $e) {
            $this->logger->error('Unexpected error', [
                'error' => $e->getMessage()
            ]);

            throw $e; // Let Shopware error handler deal with it
        }
    }
}
```

**Correct Admin API error response:**

```php
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\Controller\Api;

use Shopware\Core\Framework\Api\Response\JsonApiResponse;

#[Route(defaults: ['_routeScope' => ['api']])]
class AdminApiController extends AbstractController
{
    #[Route(
        path: '/api/_action/my-plugin/process',
        name: 'api.action.my-plugin.process',
        methods: ['POST']
    )]
    public function process(Request $request, Context $context): JsonResponse
    {
        $productId = $request->request->get('productId');

        if (!$productId) {
            return new JsonResponse([
                'errors' => [[
                    'status' => '400',
                    'code' => 'MY_PLUGIN__MISSING_PRODUCT_ID',
                    'title' => 'Bad Request',
                    'detail' => 'The productId parameter is required.'
                ]]
            ], Response::HTTP_BAD_REQUEST);
        }

        try {
            $result = $this->service->process($productId, $context);

            return new JsonResponse([
                'success' => true,
                'data' => $result
            ]);

        } catch (ProductSyncException $e) {
            return new JsonResponse([
                'errors' => [[
                    'status' => (string) $e->getStatusCode(),
                    'code' => $e->getErrorCode(),
                    'title' => 'Sync Error',
                    'detail' => $e->getMessage()
                ]]
            ], $e->getStatusCode());
        }
    }
}
```

**Correct custom error page:**

```twig
{# Resources/views/storefront/page/error/error-std.html.twig #}

{% sw_extends '@Storefront/storefront/page/error/error-std.html.twig' %}

{% block page_content_error %}
    <div class="error-page container">
        <div class="row justify-content-center">
            <div class="col-md-8 text-center">
                {% block error_icon %}
                    <div class="error-icon">
                        {% sw_icon 'warning' style {'size': 'xl'} %}
                    </div>
                {% endblock %}

                {% block error_title %}
                    <h1 class="error-title">
                        {{ "error.title"|trans }}
                    </h1>
                {% endblock %}

                {% block error_message %}
                    <p class="error-message">
                        {{ "error.message"|trans }}
                    </p>
                {% endblock %}

                {% block error_code %}
                    {% if error.code is defined %}
                        <p class="error-code text-muted">
                            {{ "error.code"|trans }}: {{ error.code }}
                        </p>
                    {% endif %}
                {% endblock %}

                {% block error_actions %}
                    <div class="error-actions mt-4">
                        <a href="{{ path('frontend.home.page') }}" class="btn btn-primary">
                            {{ "error.backHome"|trans }}
                        </a>
                        <a href="{{ path('frontend.account.home.page') }}" class="btn btn-secondary">
                            {{ "error.contact"|trans }}
                        </a>
                    </div>
                {% endblock %}
            </div>
        </div>
    </div>
{% endblock %}
```

**Exception types:**

| Exception | Use Case |
|-----------|----------|
| `ShopwareHttpException` | HTTP errors with status codes |
| `InvalidArgumentException` | Invalid input parameters |
| `RuntimeException` | Runtime errors |
| `ConstraintViolationException` | Validation failures |
| `EntityNotFoundException` | Missing entities |

Reference: [Error Handling](https://developer.shopware.com/docs/guides/plugins/plugins/plugin-fundamentals/add-custom-commands.html)
