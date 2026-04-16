---
title: Store API Tests
impact: MEDIUM
impactDescription: Store API tests verify that customer-facing API endpoints return correct responses and handle authentication properly.
tags: [testing, store-api, api, http]
---

## Store API Tests

Test Store API routes using SalesChannelApiTestBehaviour to simulate real HTTP requests with proper sales channel context and authentication.

Reference: https://developer.shopware.com/docs/guides/plugins/plugins/testing/php-integration.html

### Incorrect

```php
// Bad: Not testing API responses, only testing controller directly

namespace MyPlugin\Tests;

use MyPlugin\Storefront\Controller\Api\ProductController;
use PHPUnit\Framework\TestCase;

class ProductApiTest extends TestCase
{
    // Bad: Testing controller method directly without HTTP context
    public function testGetProducts(): void
    {
        $controller = new ProductController($this->repository);

        // Bad: Calling method directly bypasses routing, middleware, serialization
        $result = $controller->getProducts();

        // Bad: No real HTTP response testing
        $this->assertNotEmpty($result);
    }

    // Bad: Not testing authentication or sales channel context
    public function testProtectedEndpoint(): void
    {
        $controller = new ProductController($this->repository);

        // Bad: No customer authentication tested
        $result = $controller->getCustomerProducts();
    }
}
```

```php
// Bad: Manual HTTP client without proper test infrastructure

class ApiTest extends TestCase
{
    public function testEndpoint(): void
    {
        // Bad: Using real HTTP client against running server
        $client = new \GuzzleHttp\Client();
        $response = $client->get('http://localhost/store-api/product');

        // Bad: Depends on external server state
        $this->assertEquals(200, $response->getStatusCode());
    }
}
```

### Correct

```php
// Good: Using SalesChannelApiTestBehaviour for Store API tests

namespace MyPlugin\Tests\Integration\Api;

use PHPUnit\Framework\TestCase;
use Shopware\Core\Framework\Test\TestCaseBase\IntegrationTestBehaviour;
use Shopware\Core\Framework\Test\TestCaseBase\SalesChannelApiTestBehaviour;
use Shopware\Core\Framework\Uuid\Uuid;
use Shopware\Core\Defaults;

class ProductStoreApiTest extends TestCase
{
    use IntegrationTestBehaviour;
    // Good: SalesChannelApiTestBehaviour provides API testing utilities
    use SalesChannelApiTestBehaviour;

    public function testGetProductList(): void
    {
        // Good: Create test product
        $productId = $this->createTestProduct();

        // Good: Use getBrowser() for authenticated API requests
        $browser = $this->getBrowser();

        // Good: Make actual HTTP request to Store API
        $browser->request(
            'POST',
            '/store-api/product',
            [],
            [],
            ['CONTENT_TYPE' => 'application/json'],
            json_encode([
                'includes' => [
                    'product' => ['id', 'name', 'productNumber'],
                ],
            ])
        );

        // Good: Assert HTTP response
        $response = $browser->getResponse();
        $this->assertEquals(200, $response->getStatusCode());

        // Good: Decode and validate response structure
        $content = json_decode($response->getContent(), true);

        $this->assertArrayHasKey('elements', $content);
        $this->assertNotEmpty($content['elements']);

        // Good: Verify expected product in response
        $productIds = array_column($content['elements'], 'id');
        $this->assertContains($productId, $productIds);
    }

    public function testGetProductDetail(): void
    {
        $productId = $this->createTestProduct();

        $browser = $this->getBrowser();

        // Good: Test specific product endpoint
        $browser->request(
            'POST',
            '/store-api/product/' . $productId,
            [],
            [],
            ['CONTENT_TYPE' => 'application/json']
        );

        $response = $browser->getResponse();
        $this->assertEquals(200, $response->getStatusCode());

        $content = json_decode($response->getContent(), true);

        // Good: Validate response data
        $this->assertEquals($productId, $content['product']['id']);
        $this->assertEquals('Test Product', $content['product']['name']);
    }

    private function createTestProduct(): string
    {
        $productId = Uuid::randomHex();
        $repository = $this->getContainer()->get('product.repository');

        $repository->create([
            [
                'id' => $productId,
                'name' => 'Test Product',
                'productNumber' => 'API-TEST-' . Uuid::randomHex(),
                'stock' => 100,
                'active' => true,
                'visibilities' => [
                    [
                        'salesChannelId' => $this->getSalesChannelId(),
                        'visibility' => ProductVisibilityDefinition::VISIBILITY_ALL,
                    ],
                ],
                'price' => [[
                    'currencyId' => Defaults::CURRENCY,
                    'gross' => 99.99,
                    'net' => 84.03,
                    'linked' => false,
                ]],
                'taxId' => $this->getValidTaxId(),
            ],
        ], Context::createDefaultContext());

        return $productId;
    }
}
```

```php
// Good: Testing authenticated customer endpoints

namespace MyPlugin\Tests\Integration\Api;

use PHPUnit\Framework\TestCase;
use Shopware\Core\Framework\Test\TestCaseBase\IntegrationTestBehaviour;
use Shopware\Core\Framework\Test\TestCaseBase\SalesChannelApiTestBehaviour;

class CustomerStoreApiTest extends TestCase
{
    use IntegrationTestBehaviour;
    use SalesChannelApiTestBehaviour;

    public function testGetCustomerProfile(): void
    {
        // Good: Create and login customer
        $email = 'test@example.com';
        $password = 'shopware123';
        $this->createCustomer($email, $password);

        $browser = $this->getBrowser();

        // Good: Login to get context token
        $browser->request(
            'POST',
            '/store-api/account/login',
            [],
            [],
            ['CONTENT_TYPE' => 'application/json'],
            json_encode([
                'email' => $email,
                'password' => $password,
            ])
        );

        $this->assertEquals(200, $browser->getResponse()->getStatusCode());

        // Good: Context token is automatically maintained by browser
        $browser->request(
            'POST',
            '/store-api/account/customer',
            [],
            [],
            ['CONTENT_TYPE' => 'application/json']
        );

        $response = $browser->getResponse();
        $this->assertEquals(200, $response->getStatusCode());

        $content = json_decode($response->getContent(), true);
        $this->assertEquals($email, $content['email']);
    }

    public function testUnauthenticatedAccessDenied(): void
    {
        // Good: Test that protected endpoints require authentication
        $browser = $this->getBrowser();

        $browser->request(
            'POST',
            '/store-api/account/customer',
            [],
            [],
            ['CONTENT_TYPE' => 'application/json']
        );

        // Good: Verify 403 for unauthenticated request
        $this->assertEquals(403, $browser->getResponse()->getStatusCode());
    }

    private function createCustomer(string $email, string $password): string
    {
        $customerId = Uuid::randomHex();
        $addressId = Uuid::randomHex();

        $this->getContainer()->get('customer.repository')->create([
            [
                'id' => $customerId,
                'salesChannelId' => $this->getSalesChannelId(),
                'defaultShippingAddress' => [
                    'id' => $addressId,
                    'firstName' => 'Test',
                    'lastName' => 'Customer',
                    'street' => 'Test Street 1',
                    'city' => 'Test City',
                    'zipcode' => '12345',
                    'countryId' => $this->getValidCountryId(),
                ],
                'defaultBillingAddressId' => $addressId,
                'email' => $email,
                'password' => $password,
                'firstName' => 'Test',
                'lastName' => 'Customer',
                'groupId' => Defaults::FALLBACK_CUSTOMER_GROUP,
                'customerNumber' => 'TEST-' . Uuid::randomHex(),
            ],
        ], Context::createDefaultContext());

        return $customerId;
    }
}
```

```php
// Good: Testing custom Store API route

namespace MyPlugin\Tests\Integration\Api;

use PHPUnit\Framework\TestCase;
use Shopware\Core\Framework\Test\TestCaseBase\IntegrationTestBehaviour;
use Shopware\Core\Framework\Test\TestCaseBase\SalesChannelApiTestBehaviour;

class CustomRouteStoreApiTest extends TestCase
{
    use IntegrationTestBehaviour;
    use SalesChannelApiTestBehaviour;

    public function testCustomRouteReturnsExpectedData(): void
    {
        $browser = $this->getBrowser();

        // Good: Test custom plugin route
        $browser->request(
            'GET',
            '/store-api/my-plugin/custom-endpoint',
            [],
            [],
            ['CONTENT_TYPE' => 'application/json']
        );

        $response = $browser->getResponse();

        // Good: Test status code
        $this->assertEquals(200, $response->getStatusCode());

        // Good: Test content type header
        $this->assertEquals(
            'application/json',
            $response->headers->get('Content-Type')
        );

        // Good: Test response structure
        $content = json_decode($response->getContent(), true);

        $this->assertArrayHasKey('data', $content);
        $this->assertArrayHasKey('apiAlias', $content);
        $this->assertEquals('my_plugin_custom_response', $content['apiAlias']);
    }

    public function testCustomRouteValidatesInput(): void
    {
        $browser = $this->getBrowser();

        // Good: Test validation error responses
        $browser->request(
            'POST',
            '/store-api/my-plugin/custom-endpoint',
            [],
            [],
            ['CONTENT_TYPE' => 'application/json'],
            json_encode([
                'invalidField' => 'value',
            ])
        );

        // Good: Expect 400 for invalid input
        $this->assertEquals(400, $browser->getResponse()->getStatusCode());

        $content = json_decode($browser->getResponse()->getContent(), true);
        $this->assertArrayHasKey('errors', $content);
    }
}
```
