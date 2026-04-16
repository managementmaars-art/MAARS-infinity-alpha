---
title: Low Priority Message Queue Separation
impact: MEDIUM
impactDescription: Mixing urgent and background tasks in the same queue causes critical operations to wait behind non-essential processing.
tags: [shopware6, message-queue, priority, async, performance]
---

## Use LowPriorityMessageInterface for Background Tasks

Separate urgent messages from background tasks using LowPriorityMessageInterface. This ensures time-sensitive operations like order processing are not delayed by bulk operations like cache warming or statistics calculation.

Reference: https://developer.shopware.com/docs/guides/plugins/plugins/framework/message-queue/add-message-handler

### Incorrect

```php
// Bad: All messages use the same default queue
class CacheWarmupMessage
{
    // Bad: No priority interface, competes with urgent messages
    public function __construct(
        private readonly array $cacheIds
    ) {
    }
}

class OrderConfirmationMessage
{
    // Bad: Same queue as low-priority tasks
    public function __construct(
        private readonly string $orderId
    ) {
    }
}

class StatisticsCalculationMessage
{
    // Bad: Heavy calculation blocks urgent messages
    public function __construct(
        private readonly \DateTimeInterface $date
    ) {
    }
}

// Bad: No transport routing configured
// All messages go to 'async' transport by default
// framework:
//     messenger:
//         transports:
//             async: 'doctrine://default'

// Bad: Single worker processes everything sequentially
// Order confirmations wait behind hours of cache warmup
```

### Correct

```php
// Good: Mark background tasks as low priority
use Shopware\Core\Framework\MessageQueue\LowPriorityMessageInterface;

class CacheWarmupMessage implements LowPriorityMessageInterface
{
    public function __construct(
        private readonly array $cacheIds
    ) {
    }

    public function getCacheIds(): array
    {
        return $this->cacheIds;
    }
}

class StatisticsCalculationMessage implements LowPriorityMessageInterface
{
    public function __construct(
        private readonly \DateTimeInterface $date
    ) {
    }

    public function getDate(): \DateTimeInterface
    {
        return $this->date;
    }
}

// Good: Urgent messages use default async transport (no interface needed)
class OrderConfirmationMessage
{
    public function __construct(
        private readonly string $orderId
    ) {
    }

    public function getOrderId(): string
    {
        return $this->orderId;
    }
}

// Good: Configure separate transports for priority separation
// config/packages/messenger.yaml
/*
framework:
    messenger:
        transports:
            async:
                dsn: '%env(MESSENGER_TRANSPORT_DSN)%'
                options:
                    queue_name: shopware_async

            low_priority:
                dsn: '%env(MESSENGER_TRANSPORT_DSN)%'
                options:
                    queue_name: shopware_low_priority

        routing:
            'Shopware\Core\Framework\MessageQueue\LowPriorityMessageInterface': low_priority
            '*': async
*/

// Good: Run separate workers with appropriate resources
/*
# High priority worker - more processes, faster polling
[program:shopware-worker-async]
command=/usr/bin/php bin/console messenger:consume async --time-limit=300 --memory-limit=512M
numprocs=3

# Low priority worker - fewer resources, can be paused during peak hours
[program:shopware-worker-low-priority]
command=/usr/bin/php bin/console messenger:consume low_priority --time-limit=600 --memory-limit=256M
numprocs=1
*/

// Good: Custom priority interface for your plugin
namespace MyPlugin\MessageQueue;

interface HighPriorityMessageInterface
{
    // Marker interface for critical messages
}

// Good: Route custom priority messages
/*
framework:
    messenger:
        routing:
            'MyPlugin\MessageQueue\HighPriorityMessageInterface': high_priority
            'Shopware\Core\Framework\MessageQueue\LowPriorityMessageInterface': low_priority
            '*': async
*/
```
