---
title: Integration Tests
impact: HIGH
impactDescription: Integration tests verify that components work correctly together with the database and Symfony kernel, catching issues unit tests miss.
tags: [testing, integration, database, kernel]
---

## Integration Tests

Use Shopware's integration test traits to test components with real database interactions and proper test isolation through transaction rollback.

Reference: https://developer.shopware.com/docs/guides/plugins/plugins/testing/php-integration.html

### Incorrect

```php
// Bad: Shared state between tests, no proper cleanup

namespace MyPlugin\Tests\Integration;

use PHPUnit\Framework\TestCase;
use Shopware\Core\Framework\Context;

class ProductServiceTest extends TestCase
{
    private static $productId;

    // Bad: Using static state that persists between tests
    public static function setUpBeforeClass(): void
    {
        $container = require __DIR__ . '/../../var/cache/test/container.php';
        $repository = $container->get('product.repository');

        // Bad: Creating data that persists across all tests
        self::$productId = Uuid::randomHex();
        $repository->create([
            [
                'id' => self::$productId,
                'name' => 'Test Product',
                'productNumber' => 'TEST-001',
                'stock' => 10,
                'price' => [['currencyId' => Defaults::CURRENCY, 'gross' => 100, 'net' => 84, 'linked' => false]],
                'taxId' => $this->getTaxId(),
            ]
        ], Context::createDefaultContext());
    }

    // Bad: Test depends on data from another test
    public function testUpdateProduct(): void
    {
        // This fails if previous test modified the product
        $product = $this->repository->search(
            new Criteria([self::$productId]),
            Context::createDefaultContext()
        )->first();

        $this->assertEquals('Test Product', $product->getName());
    }

    // Bad: No cleanup - data persists in database
    public function testDeleteProduct(): void
    {
        $this->repository->delete([['id' => self::$productId]], Context::createDefaultContext());
        // Other tests now fail because product is gone
    }
}
```

```php
// Bad: Manual kernel bootstrap without traits

class ServiceTest extends TestCase
{
    private $kernel;

    protected function setUp(): void
    {
        // Bad: Manual kernel management
        $this->kernel = new Kernel('test', true);
        $this->kernel->boot();
    }

    protected function tearDown(): void
    {
        // Bad: Forgetting to clean up properly
        $this->kernel->shutdown();
    }
}
```

### Correct

```php
// Good: Using IntegrationTestBehaviour for proper test isolation

namespace MyPlugin\Tests\Integration\Service;

use PHPUnit\Framework\TestCase;
use Shopware\Core\Content\Product\ProductEntity;
use Shopware\Core\Defaults;
use Shopware\Core\Framework\Context;
use Shopware\Core\Framework\DataAbstractionLayer\Search\Criteria;
use Shopware\Core\Framework\Test\TestCaseBase\IntegrationTestBehaviour;
use Shopware\Core\Framework\Uuid\Uuid;

class ProductServiceTest extends TestCase
{
    // Good: Use IntegrationTestBehaviour for kernel and database access
    use IntegrationTestBehaviour;

    public function testCreateProduct(): void
    {
        // Good: Get repository from container
        $repository = $this->getContainer()->get('product.repository');
        $context = Context::createDefaultContext();

        $productId = Uuid::randomHex();

        // Good: Create test data within test method
        $repository->create([
            [
                'id' => $productId,
                'name' => 'Integration Test Product',
                'productNumber' => 'INT-TEST-' . Uuid::randomHex(),
                'stock' => 10,
                'price' => [[
                    'currencyId' => Defaults::CURRENCY,
                    'gross' => 119.99,
                    'net' => 100.83,
                    'linked' => false,
                ]],
                'taxId' => $this->getValidTaxId(),
            ],
        ], $context);

        // Good: Test the actual behavior
        $product = $repository->search(new Criteria([$productId]), $context)->first();

        $this->assertInstanceOf(ProductEntity::class, $product);
        $this->assertEquals('Integration Test Product', $product->getName());

        // Good: Transaction is automatically rolled back after test
    }

    private function getValidTaxId(): string
    {
        return $this->getContainer()
            ->get('tax.repository')
            ->searchIds(new Criteria(), Context::createDefaultContext())
            ->firstId();
    }
}
```

```php
// Good: Using KernelTestBehaviour for Symfony kernel access

namespace MyPlugin\Tests\Integration\Command;

use PHPUnit\Framework\TestCase;
use Shopware\Core\Framework\Test\TestCaseBase\KernelTestBehaviour;
use Symfony\Bundle\FrameworkBundle\Console\Application;
use Symfony\Component\Console\Tester\CommandTester;

class ImportCommandTest extends TestCase
{
    // Good: KernelTestBehaviour provides kernel access without database traits
    use KernelTestBehaviour;

    public function testCommandExecutesSuccessfully(): void
    {
        $application = new Application($this->getKernel());
        $command = $application->find('my-plugin:import');
        $commandTester = new CommandTester($command);

        $commandTester->execute([
            'file' => __DIR__ . '/../_fixtures/import-data.csv',
        ]);

        $this->assertEquals(0, $commandTester->getStatusCode());
        $this->assertStringContainsString('Import completed', $commandTester->getDisplay());
    }
}
```

```php
// Good: Database test with explicit transaction handling

namespace MyPlugin\Tests\Integration\Repository;

use PHPUnit\Framework\TestCase;
use Shopware\Core\Framework\Test\TestCaseBase\IntegrationTestBehaviour;
use Shopware\Core\Framework\Test\TestCaseBase\DatabaseTransactionBehaviour;

class CustomEntityRepositoryTest extends TestCase
{
    use IntegrationTestBehaviour;
    // Good: Explicit transaction behaviour ensures rollback
    use DatabaseTransactionBehaviour;

    public function testRepositoryPersistsEntity(): void
    {
        $repository = $this->getContainer()->get('my_plugin_entity.repository');
        $context = Context::createDefaultContext();

        $id = Uuid::randomHex();

        // Good: All changes are rolled back after test
        $repository->create([
            [
                'id' => $id,
                'name' => 'Test Entity',
                'active' => true,
            ],
        ], $context);

        $entity = $repository->search(new Criteria([$id]), $context)->first();

        $this->assertNotNull($entity);
        $this->assertEquals('Test Entity', $entity->getName());
    }

    public function testAnotherOperation(): void
    {
        // Good: This test starts with clean database state
        $repository = $this->getContainer()->get('my_plugin_entity.repository');

        $result = $repository->search(new Criteria(), Context::createDefaultContext());

        // Good: No data leakage from previous test
        $this->assertEquals(0, $result->getTotal());
    }
}
```

```php
// Good: Testing with queue and async services

namespace MyPlugin\Tests\Integration\MessageHandler;

use PHPUnit\Framework\TestCase;
use Shopware\Core\Framework\Test\TestCaseBase\IntegrationTestBehaviour;
use Shopware\Core\Framework\Test\TestCaseBase\QueueTestBehaviour;

class ProductSyncHandlerTest extends TestCase
{
    use IntegrationTestBehaviour;
    // Good: QueueTestBehaviour for testing message handlers
    use QueueTestBehaviour;

    public function testHandlerProcessesMessage(): void
    {
        $messageBus = $this->getContainer()->get('messenger.bus.shopware');

        $messageBus->dispatch(new ProductSyncMessage('product-id'));

        // Good: Process queued messages synchronously in test
        $this->runWorker();

        // Assert side effects of message handling
    }
}
```
