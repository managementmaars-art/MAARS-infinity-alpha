---
title: Test Fixtures
impact: MEDIUM
impactDescription: Well-organized test fixtures reduce code duplication, improve test readability, and make tests easier to maintain.
tags: [testing, fixtures, ids-collection, test-data]
---

## Test Fixtures

Use IdsCollection and reusable fixture methods to create consistent test data without hardcoded IDs or duplicate fixture code across tests.

Reference: https://developer.shopware.com/docs/guides/plugins/plugins/testing/php-integration.html

### Incorrect

```php
// Bad: Hardcoded IDs and duplicate fixture code

namespace MyPlugin\Tests\Integration;

use PHPUnit\Framework\TestCase;

class OrderServiceTest extends TestCase
{
    // Bad: Hardcoded UUIDs scattered throughout tests
    private const PRODUCT_ID = '0192340a-7c54-7dd7-a069-5e0b9d4c37f8';
    private const CUSTOMER_ID = '0192340a-7c54-7dd7-a069-5e0b9d4c37f9';
    private const ORDER_ID = '0192340a-7c54-7dd7-a069-5e0b9d4c37fa';

    public function testCreateOrder(): void
    {
        // Bad: Duplicate product creation code
        $this->getContainer()->get('product.repository')->create([
            [
                'id' => self::PRODUCT_ID,
                'name' => 'Test Product',
                'productNumber' => 'TEST-001',
                'stock' => 10,
                'price' => [[
                    'currencyId' => Defaults::CURRENCY,
                    'gross' => 100,
                    'net' => 84,
                    'linked' => false,
                ]],
                'taxId' => 'some-hardcoded-tax-id',
            ],
        ], Context::createDefaultContext());

        // Test code...
    }

    public function testUpdateOrder(): void
    {
        // Bad: Same product creation duplicated
        $this->getContainer()->get('product.repository')->create([
            [
                'id' => self::PRODUCT_ID,
                'name' => 'Test Product',
                'productNumber' => 'TEST-001',
                'stock' => 10,
                'price' => [[
                    'currencyId' => Defaults::CURRENCY,
                    'gross' => 100,
                    'net' => 84,
                    'linked' => false,
                ]],
                'taxId' => 'some-hardcoded-tax-id',
            ],
        ], Context::createDefaultContext());

        // Test code...
    }
}
```

```php
// Bad: Fixtures with dependencies on execution order

class ProductImportTest extends TestCase
{
    private static string $categoryId;

    // Bad: Fixture created once, reused across tests
    public static function setUpBeforeClass(): void
    {
        // Creates category once - if test modifies it, other tests break
        self::$categoryId = self::createCategory();
    }

    public function testImportWithCategory(): void
    {
        // Depends on category created in setUpBeforeClass
        $this->importProducts(['categoryId' => self::$categoryId]);
    }
}
```

### Correct

```php
// Good: Using IdsCollection for test data management

namespace MyPlugin\Tests\Integration\Service;

use PHPUnit\Framework\TestCase;
use Shopware\Core\Framework\Test\IdsCollection;
use Shopware\Core\Framework\Test\TestCaseBase\IntegrationTestBehaviour;
use Shopware\Core\Defaults;

class OrderServiceTest extends TestCase
{
    use IntegrationTestBehaviour;

    // Good: IdsCollection generates consistent, unique IDs
    private IdsCollection $ids;

    protected function setUp(): void
    {
        parent::setUp();
        // Good: Fresh IdsCollection for each test
        $this->ids = new IdsCollection();
    }

    public function testCreateOrder(): void
    {
        // Good: Create fixtures using IdsCollection
        $this->createProduct();
        $this->createCustomer();

        $orderService = $this->getContainer()->get(OrderService::class);

        // Good: Use ids->get() for consistent ID references
        $order = $orderService->create(
            $this->ids->get('product'),
            $this->ids->get('customer')
        );

        $this->assertNotNull($order);
        $this->assertEquals($this->ids->get('customer'), $order->getOrderCustomer()->getCustomerId());
    }

    public function testCalculateOrderTotal(): void
    {
        // Good: Each test creates its own fixtures
        $this->createProduct();

        $calculator = $this->getContainer()->get(OrderCalculator::class);
        $total = $calculator->calculate($this->ids->get('product'), 2);

        $this->assertEquals(200.0, $total);
    }

    // Good: Reusable fixture method
    private function createProduct(array $overrides = []): void
    {
        $defaults = [
            'id' => $this->ids->get('product'),
            'name' => 'Test Product',
            'productNumber' => 'TEST-' . $this->ids->get('product'),
            'stock' => 100,
            'active' => true,
            'price' => [[
                'currencyId' => Defaults::CURRENCY,
                'gross' => 100.0,
                'net' => 84.03,
                'linked' => false,
            ]],
            'taxId' => $this->getValidTaxId(),
        ];

        // Good: Allow overriding default values
        $data = array_merge($defaults, $overrides);

        $this->getContainer()
            ->get('product.repository')
            ->create([$data], Context::createDefaultContext());
    }

    private function createCustomer(array $overrides = []): void
    {
        $addressId = $this->ids->get('address');

        $defaults = [
            'id' => $this->ids->get('customer'),
            'salesChannelId' => TestDefaults::SALES_CHANNEL,
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
            'email' => 'test-' . $this->ids->get('customer') . '@example.com',
            'password' => 'shopware',
            'firstName' => 'Test',
            'lastName' => 'Customer',
            'groupId' => Defaults::FALLBACK_CUSTOMER_GROUP,
            'customerNumber' => 'CUST-' . $this->ids->get('customer'),
        ];

        $data = array_merge($defaults, $overrides);

        $this->getContainer()
            ->get('customer.repository')
            ->create([$data], Context::createDefaultContext());
    }
}
```

```php
// Good: Shared fixture trait for common test data

namespace MyPlugin\Tests\Integration;

use Shopware\Core\Defaults;
use Shopware\Core\Framework\Context;
use Shopware\Core\Framework\Test\IdsCollection;

trait ProductFixtureTrait
{
    // Good: Centralized fixture creation
    protected function createProductFixture(IdsCollection $ids, array $overrides = []): string
    {
        $productId = $ids->get('product');

        $data = array_merge([
            'id' => $productId,
            'name' => 'Fixture Product',
            'productNumber' => 'FIX-' . $productId,
            'stock' => 50,
            'active' => true,
            'price' => [[
                'currencyId' => Defaults::CURRENCY,
                'gross' => 49.99,
                'net' => 42.01,
                'linked' => false,
            ]],
            'taxId' => $this->getValidTaxId(),
            'visibilities' => [[
                'salesChannelId' => TestDefaults::SALES_CHANNEL,
                'visibility' => ProductVisibilityDefinition::VISIBILITY_ALL,
            ]],
        ], $overrides);

        $this->getContainer()
            ->get('product.repository')
            ->create([$data], Context::createDefaultContext());

        return $productId;
    }

    // Good: Fixture for product with variants
    protected function createProductWithVariants(IdsCollection $ids): string
    {
        $productId = $ids->get('product');

        $this->getContainer()->get('product.repository')->create([
            [
                'id' => $productId,
                'name' => 'Variant Product',
                'productNumber' => 'VAR-' . $productId,
                'stock' => 0,
                'active' => true,
                'configuratorSettings' => [
                    [
                        'optionId' => $ids->get('option-red'),
                    ],
                    [
                        'optionId' => $ids->get('option-blue'),
                    ],
                ],
                'children' => [
                    [
                        'id' => $ids->get('variant-red'),
                        'productNumber' => 'VAR-RED-' . $ids->get('variant-red'),
                        'stock' => 10,
                        'options' => [['id' => $ids->get('option-red')]],
                    ],
                    [
                        'id' => $ids->get('variant-blue'),
                        'productNumber' => 'VAR-BLUE-' . $ids->get('variant-blue'),
                        'stock' => 5,
                        'options' => [['id' => $ids->get('option-blue')]],
                    ],
                ],
                'price' => [[
                    'currencyId' => Defaults::CURRENCY,
                    'gross' => 79.99,
                    'net' => 67.22,
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
// Good: Using fixture trait in tests

namespace MyPlugin\Tests\Integration\Service;

use MyPlugin\Tests\Integration\ProductFixtureTrait;
use PHPUnit\Framework\TestCase;
use Shopware\Core\Framework\Test\IdsCollection;
use Shopware\Core\Framework\Test\TestCaseBase\IntegrationTestBehaviour;

class InventoryServiceTest extends TestCase
{
    use IntegrationTestBehaviour;
    // Good: Import shared fixtures
    use ProductFixtureTrait;

    private IdsCollection $ids;

    protected function setUp(): void
    {
        parent::setUp();
        $this->ids = new IdsCollection();
    }

    public function testReduceStock(): void
    {
        // Good: Use shared fixture method
        $productId = $this->createProductFixture($this->ids, ['stock' => 100]);

        $inventoryService = $this->getContainer()->get(InventoryService::class);
        $inventoryService->reduceStock($productId, 10);

        $product = $this->getContainer()
            ->get('product.repository')
            ->search(new Criteria([$productId]), Context::createDefaultContext())
            ->first();

        $this->assertEquals(90, $product->getStock());
    }

    public function testLowStockAlert(): void
    {
        // Good: Override specific values for test scenario
        $productId = $this->createProductFixture($this->ids, [
            'stock' => 5,
            'minPurchase' => 1,
        ]);

        $alertService = $this->getContainer()->get(StockAlertService::class);
        $alerts = $alertService->checkLowStock();

        $this->assertContains($productId, $alerts);
    }
}
```

```php
// Good: IdsCollection for complex entity relationships

namespace MyPlugin\Tests\Integration;

use Shopware\Core\Framework\Test\IdsCollection;

class OrderFixtureBuilder
{
    private IdsCollection $ids;

    public function __construct(IdsCollection $ids)
    {
        $this->ids = $ids;
    }

    // Good: Builder pattern for complex fixtures
    public function buildOrderData(array $lineItems = []): array
    {
        return [
            'id' => $this->ids->get('order'),
            'orderNumber' => 'ORD-' . $this->ids->get('order'),
            'salesChannelId' => TestDefaults::SALES_CHANNEL,
            'currencyId' => Defaults::CURRENCY,
            'currencyFactor' => 1.0,
            'stateId' => $this->getOrderStateId(),
            'orderDateTime' => (new \DateTime())->format(Defaults::STORAGE_DATE_TIME_FORMAT),
            'price' => new CartPrice(
                100,
                100,
                100,
                new CalculatedTaxCollection(),
                new TaxRuleCollection(),
                CartPrice::TAX_STATE_GROSS
            ),
            'shippingCosts' => new CalculatedPrice(0, 0, new CalculatedTaxCollection(), new TaxRuleCollection()),
            'orderCustomer' => [
                'id' => $this->ids->get('order-customer'),
                'customerId' => $this->ids->get('customer'),
                'email' => 'order@example.com',
                'firstName' => 'Test',
                'lastName' => 'Customer',
            ],
            'billingAddressId' => $this->ids->get('billing-address'),
            'addresses' => [
                [
                    'id' => $this->ids->get('billing-address'),
                    'firstName' => 'Test',
                    'lastName' => 'Customer',
                    'street' => 'Test Street 1',
                    'city' => 'Test City',
                    'zipcode' => '12345',
                    'countryId' => $this->getValidCountryId(),
                ],
            ],
            'lineItems' => $lineItems ?: $this->buildDefaultLineItems(),
            'deliveries' => [],
        ];
    }

    private function buildDefaultLineItems(): array
    {
        return [
            [
                'id' => $this->ids->get('line-item'),
                'productId' => $this->ids->get('product'),
                'identifier' => $this->ids->get('product'),
                'quantity' => 1,
                'type' => LineItem::PRODUCT_LINE_ITEM_TYPE,
                'label' => 'Test Product',
                'price' => new CalculatedPrice(
                    100,
                    100,
                    new CalculatedTaxCollection(),
                    new TaxRuleCollection()
                ),
            ],
        ];
    }
}
```
