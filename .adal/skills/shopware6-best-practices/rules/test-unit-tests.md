---
title: Unit Tests
impact: HIGH
impactDescription: Unit tests ensure individual components work correctly in isolation, catching bugs early and enabling confident refactoring.
tags: [testing, phpunit, unit-tests, mocking]
---

## Unit Tests

Write unit tests for services, handlers, and business logic using PHPUnit with proper mocking to test components in isolation without database dependencies.

Reference: https://developer.shopware.com/docs/guides/plugins/plugins/testing/php-unit.html

### Incorrect

```php
// Bad: No tests at all, or testing with actual database connections

namespace MyPlugin\Tests;

use MyPlugin\Service\PriceCalculator;
use Shopware\Core\Framework\DataAbstractionLayer\EntityRepository;

class PriceCalculatorTest extends \PHPUnit\Framework\TestCase
{
    // Bad: Using real database connection in unit test
    public function testCalculatePrice(): void
    {
        $container = require __DIR__ . '/../../var/cache/phpunit/container.php';
        $repository = $container->get('product.repository');

        // Bad: Fetching real data from database
        $product = $repository->search(
            new Criteria(['some-hardcoded-id']),
            Context::createDefaultContext()
        )->first();

        $calculator = new PriceCalculator($repository);
        $price = $calculator->calculate($product);

        // Bad: Assertion depends on database state
        $this->assertGreaterThan(0, $price);
    }
}

// Bad: No mocking of dependencies
class OrderProcessorTest extends \PHPUnit\Framework\TestCase
{
    public function testProcess(): void
    {
        // Bad: Creating service without mocking dependencies
        $processor = new OrderProcessor();
        // Test will fail or have side effects
    }
}
```

### Correct

```php
// Good: Proper unit test setup with TestBootstrapper

// tests/TestBootstrap.php
use Shopware\Core\TestBootstrapper;

$loader = (new TestBootstrapper())
    ->addCallingPlugin()
    ->addActivePlugins('MyPlugin')
    ->setForceInstallPlugins(true)
    ->bootstrap()
    ->getClassLoader();

$loader->addPsr4('MyPlugin\\Tests\\', __DIR__);

// phpunit.xml.dist
// <phpunit bootstrap="tests/TestBootstrap.php">
//     <testsuites>
//         <testsuite name="Unit">
//             <directory>tests/Unit</directory>
//         </testsuite>
//     </testsuites>
// </phpunit>
```

```php
// Good: Unit test with proper mocking

namespace MyPlugin\Tests\Unit\Service;

use MyPlugin\Service\PriceCalculator;
use PHPUnit\Framework\TestCase;
use Shopware\Core\Checkout\Cart\Price\Struct\CalculatedPrice;
use Shopware\Core\Content\Product\ProductEntity;
use Shopware\Core\Framework\DataAbstractionLayer\EntityRepository;
use Shopware\Core\Framework\DataAbstractionLayer\Search\EntitySearchResult;

class PriceCalculatorTest extends TestCase
{
    private PriceCalculator $calculator;
    private EntityRepository $productRepository;

    protected function setUp(): void
    {
        // Good: Mock the repository dependency
        $this->productRepository = $this->createMock(EntityRepository::class);
        $this->calculator = new PriceCalculator($this->productRepository);
    }

    public function testCalculatePriceWithDiscount(): void
    {
        // Good: Create mock product with controlled data
        $product = new ProductEntity();
        $product->setId('test-product-id');
        $product->setCalculatedPrice(new CalculatedPrice(
            100.0,
            100.0,
            new CalculatedTaxCollection(),
            new TaxRuleCollection()
        ));

        // Good: Configure mock to return expected data
        $searchResult = $this->createMock(EntitySearchResult::class);
        $searchResult->method('first')->willReturn($product);

        $this->productRepository
            ->expects($this->once())
            ->method('search')
            ->willReturn($searchResult);

        // Good: Test with predictable input and output
        $result = $this->calculator->calculateWithDiscount('test-product-id', 10);

        $this->assertEquals(90.0, $result);
    }

    public function testCalculatePriceWithInvalidProduct(): void
    {
        // Good: Test edge cases
        $searchResult = $this->createMock(EntitySearchResult::class);
        $searchResult->method('first')->willReturn(null);

        $this->productRepository
            ->method('search')
            ->willReturn($searchResult);

        $this->expectException(ProductNotFoundException::class);

        $this->calculator->calculateWithDiscount('non-existent-id', 10);
    }
}
```

```php
// Good: Testing event subscribers with mocked events

namespace MyPlugin\Tests\Unit\Subscriber;

use MyPlugin\Subscriber\OrderPlacedSubscriber;
use PHPUnit\Framework\TestCase;
use Psr\Log\LoggerInterface;
use Shopware\Core\Checkout\Cart\Event\CheckoutOrderPlacedEvent;
use Shopware\Core\Checkout\Order\OrderEntity;

class OrderPlacedSubscriberTest extends TestCase
{
    public function testOnOrderPlacedLogsOrderNumber(): void
    {
        // Good: Mock the logger to verify interactions
        $logger = $this->createMock(LoggerInterface::class);
        $logger->expects($this->once())
            ->method('info')
            ->with($this->stringContains('10001'));

        $subscriber = new OrderPlacedSubscriber($logger);

        // Good: Create mock event with controlled data
        $order = new OrderEntity();
        $order->setId('test-order-id');
        $order->setOrderNumber('10001');

        $event = $this->createMock(CheckoutOrderPlacedEvent::class);
        $event->method('getOrder')->willReturn($order);

        $subscriber->onOrderPlaced($event);
    }
}
```
