---
title: External API Integration
impact: MEDIUM
impactDescription: reliable third-party service integration patterns
tags: api, integration, http, external, client
---

## External API Integration

**Impact: MEDIUM (reliable third-party service integration patterns)**

External API integrations require proper error handling, retry logic, and circuit breaker patterns. Use typed clients with configuration and logging.

**Incorrect (unreliable API client):**

```php
// Bad: No error handling, no configuration, no retry
class ExternalApiClient
{
    public function getProducts(): array
    {
        $response = file_get_contents('https://api.example.com/products');
        return json_decode($response, true);
    }
}
```

**Correct API client implementation:**

```php
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\Service;

use GuzzleHttp\Client;
use GuzzleHttp\Exception\GuzzleException;
use GuzzleHttp\HandlerStack;
use GuzzleHttp\Middleware;
use GuzzleHttp\Psr7\Request;
use GuzzleHttp\Psr7\Response;
use Psr\Log\LoggerInterface;
use Shopware\Core\System\SystemConfig\SystemConfigService;

class ExternalApiClient
{
    private Client $client;
    private ?string $accessToken = null;

    public function __construct(
        private readonly SystemConfigService $config,
        private readonly LoggerInterface $logger,
        private readonly CacheInterface $cache
    ) {
        $this->client = $this->createHttpClient();
    }

    private function createHttpClient(): Client
    {
        $stack = HandlerStack::create();

        // Add retry middleware
        $stack->push(Middleware::retry(
            function (int $retries, Request $request, ?Response $response, ?\Exception $exception) {
                if ($retries >= 3) {
                    return false;
                }

                // Retry on network errors
                if ($exception instanceof GuzzleException) {
                    return true;
                }

                // Retry on 5xx errors
                if ($response && $response->getStatusCode() >= 500) {
                    return true;
                }

                // Retry on rate limiting
                if ($response && $response->getStatusCode() === 429) {
                    return true;
                }

                return false;
            },
            function (int $retries) {
                return 1000 * pow(2, $retries); // Exponential backoff
            }
        ));

        // Add logging middleware
        $stack->push(Middleware::log(
            $this->logger,
            new MessageFormatter('{method} {uri} - {code} {phrase} - {res_header_Content-Length}')
        ));

        return new Client([
            'handler' => $stack,
            'base_uri' => $this->config->get('MyPlugin.config.apiBaseUrl'),
            'timeout' => (float) $this->config->get('MyPlugin.config.apiTimeout') ?: 30.0,
            'connect_timeout' => 5.0,
            'http_errors' => false, // Handle errors manually
            'headers' => [
                'Accept' => 'application/json',
                'Content-Type' => 'application/json',
                'User-Agent' => 'MyPlugin/1.0 Shopware/6.6'
            ]
        ]);
    }

    public function getProducts(array $filters = []): array
    {
        return $this->request('GET', '/products', [
            'query' => $filters
        ]);
    }

    public function getProduct(string $externalId): ?array
    {
        $cacheKey = 'my_plugin_product_' . md5($externalId);

        return $this->cache->get($cacheKey, function () use ($externalId) {
            return $this->request('GET', '/products/' . $externalId);
        }, 300); // Cache for 5 minutes
    }

    public function createProduct(array $data): array
    {
        return $this->request('POST', '/products', [
            'json' => $data
        ]);
    }

    public function updateProduct(string $externalId, array $data): array
    {
        return $this->request('PUT', '/products/' . $externalId, [
            'json' => $data
        ]);
    }

    public function deleteProduct(string $externalId): void
    {
        $this->request('DELETE', '/products/' . $externalId);
    }

    private function request(string $method, string $endpoint, array $options = []): mixed
    {
        // Ensure authentication
        $this->ensureAuthenticated();

        $options['headers'] = array_merge(
            $options['headers'] ?? [],
            ['Authorization' => 'Bearer ' . $this->accessToken]
        );

        try {
            $response = $this->client->request($method, $endpoint, $options);
            $statusCode = $response->getStatusCode();

            $this->logger->debug('API request completed', [
                'method' => $method,
                'endpoint' => $endpoint,
                'status' => $statusCode
            ]);

            if ($statusCode >= 400) {
                $this->handleErrorResponse($response, $method, $endpoint);
            }

            $body = $response->getBody()->getContents();

            if (empty($body)) {
                return null;
            }

            return json_decode($body, true, 512, JSON_THROW_ON_ERROR);

        } catch (GuzzleException $e) {
            $this->logger->error('API request failed', [
                'method' => $method,
                'endpoint' => $endpoint,
                'error' => $e->getMessage()
            ]);

            throw new ExternalApiException(
                'External API request failed: ' . $e->getMessage(),
                $e->getCode(),
                $e
            );
        }
    }

    private function ensureAuthenticated(): void
    {
        if ($this->accessToken !== null) {
            return;
        }

        $cacheKey = 'my_plugin_api_token';
        $this->accessToken = $this->cache->get($cacheKey, function () {
            return $this->authenticate();
        }, 3500); // Token valid for ~1 hour, cache for 58 minutes
    }

    private function authenticate(): string
    {
        $response = $this->client->post('/auth/token', [
            'json' => [
                'client_id' => $this->config->get('MyPlugin.config.apiClientId'),
                'client_secret' => $this->config->get('MyPlugin.config.apiClientSecret'),
                'grant_type' => 'client_credentials'
            ],
            'headers' => [] // No auth header for token request
        ]);

        if ($response->getStatusCode() !== 200) {
            throw new ExternalApiException('Authentication failed');
        }

        $data = json_decode($response->getBody()->getContents(), true);

        return $data['access_token'];
    }

    private function handleErrorResponse(Response $response, string $method, string $endpoint): void
    {
        $statusCode = $response->getStatusCode();
        $body = json_decode($response->getBody()->getContents(), true);
        $message = $body['message'] ?? $body['error'] ?? 'Unknown error';

        $this->logger->error('API error response', [
            'method' => $method,
            'endpoint' => $endpoint,
            'status' => $statusCode,
            'message' => $message
        ]);

        match ($statusCode) {
            401 => throw new AuthenticationException('Authentication failed: ' . $message),
            403 => throw new AuthorizationException('Access denied: ' . $message),
            404 => throw new NotFoundException('Resource not found: ' . $endpoint),
            422 => throw new ValidationException('Validation failed: ' . $message),
            429 => throw new RateLimitException('Rate limit exceeded'),
            default => throw new ExternalApiException($message, $statusCode)
        };
    }
}
```

**Correct service registration with configuration:**

```xml
<!-- services.xml -->
<service id="MyVendor\MyPlugin\Service\ExternalApiClient">
    <argument type="service" id="Shopware\Core\System\SystemConfig\SystemConfigService"/>
    <argument type="service" id="monolog.logger.my_plugin"/>
    <argument type="service" id="cache.object"/>
</service>

<!-- Dedicated logger channel -->
<service id="monolog.logger.my_plugin" parent="monolog.logger">
    <argument>my_plugin</argument>
</service>
```

**Correct plugin configuration:**

```xml
<!-- Resources/config/config.xml -->
<?xml version="1.0" encoding="UTF-8"?>
<config xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:noNamespaceSchemaLocation="https://raw.githubusercontent.com/shopware/shopware/trunk/src/Core/System/SystemConfig/Schema/config.xsd">

    <card>
        <title>API Configuration</title>
        <title lang="de-DE">API-Konfiguration</title>

        <input-field type="text">
            <name>apiBaseUrl</name>
            <label>API Base URL</label>
            <placeholder>https://api.example.com</placeholder>
            <required>true</required>
        </input-field>

        <input-field type="password">
            <name>apiClientId</name>
            <label>Client ID</label>
            <required>true</required>
        </input-field>

        <input-field type="password">
            <name>apiClientSecret</name>
            <label>Client Secret</label>
            <required>true</required>
        </input-field>

        <input-field type="int">
            <name>apiTimeout</name>
            <label>Timeout (seconds)</label>
            <defaultValue>30</defaultValue>
        </input-field>
    </card>
</config>
```

**Correct sync service using the API client:**

```php
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\Service;

class ProductSyncService
{
    public function __construct(
        private readonly ExternalApiClient $apiClient,
        private readonly EntityRepository $productRepository,
        private readonly MessageBusInterface $messageBus,
        private readonly LoggerInterface $logger
    ) {}

    public function syncProduct(string $productId, Context $context): void
    {
        $product = $this->productRepository->search(
            new Criteria([$productId]),
            $context
        )->first();

        if (!$product) {
            throw new ProductNotFoundException($productId);
        }

        $externalId = $product->getCustomFields()['my_plugin_external_id'] ?? null;

        $data = $this->mapProductToExternal($product);

        try {
            if ($externalId) {
                $this->apiClient->updateProduct($externalId, $data);
            } else {
                $result = $this->apiClient->createProduct($data);
                $externalId = $result['id'];

                // Store external ID
                $this->productRepository->update([
                    [
                        'id' => $productId,
                        'customFields' => [
                            'my_plugin_external_id' => $externalId,
                            'my_plugin_last_sync' => (new \DateTime())->format('c')
                        ]
                    ]
                ], $context);
            }

            $this->logger->info('Product synced', [
                'productId' => $productId,
                'externalId' => $externalId
            ]);

        } catch (ExternalApiException $e) {
            $this->logger->error('Product sync failed', [
                'productId' => $productId,
                'error' => $e->getMessage()
            ]);

            // Queue for retry
            $this->messageBus->dispatch(new ProductSyncRetryMessage($productId));

            throw $e;
        }
    }

    private function mapProductToExternal(ProductEntity $product): array
    {
        return [
            'sku' => $product->getProductNumber(),
            'name' => $product->getTranslation('name'),
            'description' => $product->getTranslation('description'),
            'price' => $product->getCalculatedPrice()->getUnitPrice(),
            'stock' => $product->getStock(),
            'active' => $product->getActive()
        ];
    }
}
```

Reference: [HTTP Client](https://developer.shopware.com/docs/guides/plugins/plugins/plugin-fundamentals/using-custom-fields.html)
