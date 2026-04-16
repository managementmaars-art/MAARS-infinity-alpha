---
title: Implement Scheduled Tasks Correctly
impact: MEDIUM
impactDescription: enables reliable background processing
tags: scheduled-tasks, cron, background, automation
---

## Implement Scheduled Tasks Correctly

**Impact: MEDIUM (enables reliable background processing)**

Scheduled tasks run recurring background operations like syncing, cleanup, or report generation. Proper implementation ensures reliability and doesn't block the queue.

**Incorrect (scheduled task anti-patterns):**

```php
// Bad: No interval defined
class BrokenTask extends ScheduledTask
{
    public static function getTaskName(): string
    {
        return 'my_plugin.sync_task';
    }

    // Missing getDefaultInterval() - will fail!
}

// Bad: Handler not registered
class UnregisteredHandler extends ScheduledTaskHandler
{
    // Missing messenger.message_handler tag!
}

// Bad: Long-running task blocking queue
class SlowTaskHandler extends ScheduledTaskHandler
{
    public function run(): void
    {
        // Bad: Processing 100K records in single task blocks queue for hours
        $allProducts = $this->productRepository->search(new Criteria(), $this->context);

        foreach ($allProducts as $product) {
            $this->syncToExternalSystem($product);  // HTTP call for each!
            sleep(1);  // Rate limiting in task = very slow
        }
    }
}

// Bad: No error handling
class FragileTaskHandler extends ScheduledTaskHandler
{
    public function run(): void
    {
        $data = $this->apiClient->fetch();  // Could throw!
        $this->process($data);
        // Any error = task fails and may not reschedule
    }
}

// Bad: Not updating task status
class StatuslessHandler extends ScheduledTaskHandler
{
    public function run(): void
    {
        $this->doWork();
        // Task status never updated - appears stuck
    }
}
```

**Correct (proper scheduled task implementation):**

```php
// Good: Complete scheduled task definition
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\ScheduledTask;

use Shopware\Core\Framework\MessageQueue\ScheduledTask\ScheduledTask;

class ProductSyncTask extends ScheduledTask
{
    public static function getTaskName(): string
    {
        return 'my_plugin.product_sync';
    }

    public static function getDefaultInterval(): int
    {
        return 3600;  // Run every hour (in seconds)
    }
}
```

```php
// Good: Robust task handler
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\ScheduledTask;

use Psr\Log\LoggerInterface;
use Shopware\Core\Framework\Context;
use Shopware\Core\Framework\DataAbstractionLayer\EntityRepository;
use Shopware\Core\Framework\MessageQueue\ScheduledTask\ScheduledTaskHandler;
use Symfony\Component\Messenger\Attribute\AsMessageHandler;

#[AsMessageHandler(handles: ProductSyncTask::class)]
class ProductSyncTaskHandler extends ScheduledTaskHandler
{
    public function __construct(
        EntityRepository $scheduledTaskRepository,
        private readonly ProductSyncService $syncService,
        private readonly LoggerInterface $logger
    ) {
        parent::__construct($scheduledTaskRepository);
    }

    public function run(): void
    {
        $this->logger->info('Starting product sync task');
        $context = Context::createDefaultContext();

        try {
            $result = $this->syncService->syncProducts($context);

            $this->logger->info('Product sync completed', [
                'synced' => $result->getSyncedCount(),
                'failed' => $result->getFailedCount(),
                'duration' => $result->getDuration(),
            ]);

        } catch (\Throwable $e) {
            $this->logger->error('Product sync failed', [
                'exception' => $e,
            ]);

            // Rethrow to mark task as failed
            throw $e;
        }
    }
}
```

```php
// Good: Chunked processing for large datasets
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\Service;

use Shopware\Core\Framework\DataAbstractionLayer\Dbal\Common\RepositoryIterator;

class ProductSyncService
{
    private const BATCH_SIZE = 100;

    public function syncProducts(Context $context): SyncResult
    {
        $criteria = new Criteria();
        $criteria->setLimit(self::BATCH_SIZE);
        $criteria->addFilter(new EqualsFilter('active', true));

        $iterator = new RepositoryIterator($this->productRepository, $context, $criteria);

        $synced = 0;
        $failed = 0;
        $startTime = microtime(true);

        while (($result = $iterator->fetch()) !== null) {
            foreach ($result->getEntities() as $product) {
                try {
                    $this->syncProduct($product);
                    $synced++;
                } catch (\Throwable $e) {
                    $failed++;
                    $this->logger->warning('Failed to sync product', [
                        'productId' => $product->getId(),
                        'error' => $e->getMessage(),
                    ]);
                }
            }

            // Good: Clear memory between batches
            gc_collect_cycles();
        }

        return new SyncResult($synced, $failed, microtime(true) - $startTime);
    }
}
```

```php
// Good: Task that dispatches work to message queue
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\ScheduledTask;

use Symfony\Component\Messenger\MessageBusInterface;

#[AsMessageHandler(handles: BulkExportTask::class)]
class BulkExportTaskHandler extends ScheduledTaskHandler
{
    public function __construct(
        EntityRepository $scheduledTaskRepository,
        private readonly EntityRepository $orderRepository,
        private readonly MessageBusInterface $messageBus
    ) {
        parent::__construct($scheduledTaskRepository);
    }

    public function run(): void
    {
        $context = Context::createDefaultContext();

        // Good: Get IDs only, dispatch individual messages
        $criteria = new Criteria();
        $criteria->addFilter(new RangeFilter('createdAt', [
            'gte' => (new \DateTime('-24 hours'))->format('c'),
        ]));

        $orderIds = $this->orderRepository->searchIds($criteria, $context)->getIds();

        // Good: Dispatch messages for parallel processing
        foreach (array_chunk($orderIds, 50) as $chunk) {
            $this->messageBus->dispatch(new ExportOrdersMessage($chunk));
        }

        $this->logger->info('Dispatched export messages', [
            'orderCount' => count($orderIds),
            'messageCount' => ceil(count($orderIds) / 50),
        ]);
    }
}
```

```xml
<!-- Good: Service registration in services.xml -->
<service id="MyVendor\MyPlugin\ScheduledTask\ProductSyncTask">
    <tag name="shopware.scheduled.task"/>
</service>

<service id="MyVendor\MyPlugin\ScheduledTask\ProductSyncTaskHandler">
    <argument type="service" id="scheduled_task.repository"/>
    <argument type="service" id="MyVendor\MyPlugin\Service\ProductSyncService"/>
    <argument type="service" id="logger"/>
    <tag name="messenger.message_handler"/>
</service>
```

**Task management commands:**

```bash
# List all scheduled tasks
bin/console scheduled-task:list

# Run specific task immediately
bin/console scheduled-task:run my_plugin.product_sync

# Register new tasks after plugin install
bin/console scheduled-task:register
```

**Interval guidelines:**

| Task Type | Recommended Interval |
|-----------|---------------------|
| Real-time sync | 60-300 seconds |
| Hourly reports | 3600 seconds |
| Daily cleanup | 86400 seconds |
| Weekly digest | 604800 seconds |

Reference: [Scheduled Tasks](https://developer.shopware.com/docs/guides/plugins/plugins/plugin-fundamentals/add-scheduled-task.html)
