---
title: Register Services Correctly
impact: CRITICAL
impactDescription: ensures dependency injection and proper service wiring
tags: plugin, services, dependency-injection, symfony
---

## Register Services Correctly

**Impact: CRITICAL (ensures dependency injection and proper service wiring)**

Shopware 6 uses Symfony's dependency injection container. Services must be properly defined in `services.xml` with correct tags and autowiring configuration.

**Incorrect (broken service registration):**

```xml
<!-- Bad: No services.xml at all - services not registered -->

<!-- Bad: Missing required tags -->
<services>
    <service id="MyVendor\MyPlugin\Subscriber\MySubscriber"/>
    <!-- Missing kernel.event_subscriber tag! -->
</services>

<!-- Bad: Hardcoded dependencies -->
<service id="MyVendor\MyPlugin\Service\MyService">
    <argument>%kernel.project_dir%/custom/plugins/MyPlugin/config.json</argument>
</service>
```

```php
// Bad: Using container directly instead of injection
class MyService
{
    public function doSomething(): void
    {
        $productRepository = Shopware()->getContainer()
            ->get('product.repository');  // Never do this!
    }
}

// Bad: Service locator pattern
class MyController
{
    public function __construct(
        private readonly ContainerInterface $container
    ) {}

    public function index(): Response
    {
        $service = $this->container->get(MyService::class);  // Anti-pattern!
    }
}
```

**Correct (proper service registration):**

```xml
<?xml version="1.0" ?>
<container xmlns="http://symfony.com/schema/dic/services"
           xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
           xsi:schemaLocation="http://symfony.com/schema/dic/services
           https://symfony.com/schema/dic/services/services-1.0.xsd">

    <services>
        <!-- Enable autowiring and autoconfiguration for this namespace -->
        <defaults autowire="true" autoconfigure="true" public="false"/>

        <!-- Event Subscriber - must have tag -->
        <service id="MyVendor\MyPlugin\Subscriber\OrderSubscriber">
            <tag name="kernel.event_subscriber"/>
        </service>

        <!-- Custom service with explicit dependencies -->
        <service id="MyVendor\MyPlugin\Service\CustomPriceService">
            <argument type="service" id="product.repository"/>
            <argument type="service" id="Shopware\Core\System\SystemConfig\SystemConfigService"/>
            <argument type="service" id="logger"/>
        </service>

        <!-- Entity definition - must have tag -->
        <service id="MyVendor\MyPlugin\Core\Content\CustomEntity\CustomEntityDefinition">
            <tag name="shopware.entity.definition" entity="custom_entity"/>
        </service>

        <!-- Scheduled task - must have tag -->
        <service id="MyVendor\MyPlugin\ScheduledTask\SyncTask">
            <tag name="shopware.scheduled.task"/>
        </service>

        <!-- Scheduled task handler -->
        <service id="MyVendor\MyPlugin\ScheduledTask\SyncTaskHandler">
            <argument type="service" id="scheduled_task.repository"/>
            <tag name="messenger.message_handler"/>
        </service>

        <!-- Message handler -->
        <service id="MyVendor\MyPlugin\MessageQueue\MyMessageHandler">
            <tag name="messenger.message_handler"/>
        </service>

        <!-- Decorator pattern -->
        <service id="MyVendor\MyPlugin\Service\DecoratedCartService"
                 decorates="Shopware\Core\Checkout\Cart\CartService">
            <argument type="service" id="MyVendor\MyPlugin\Service\DecoratedCartService.inner"/>
        </service>
    </services>
</container>
```

```php
// Good: Constructor injection
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\Service;

use Psr\Log\LoggerInterface;
use Shopware\Core\Framework\DataAbstractionLayer\EntityRepository;
use Shopware\Core\System\SystemConfig\SystemConfigService;

class CustomPriceService
{
    public function __construct(
        private readonly EntityRepository $productRepository,
        private readonly SystemConfigService $systemConfigService,
        private readonly LoggerInterface $logger
    ) {}

    public function calculateCustomPrice(string $productId): float
    {
        // Use injected dependencies
        $this->logger->info('Calculating custom price', ['productId' => $productId]);

        $multiplier = $this->systemConfigService->get('MyPlugin.config.priceMultiplier');

        // Use repository...
    }
}
```

**Common service tags:**

| Tag | Purpose |
|-----|---------|
| `kernel.event_subscriber` | Event subscribers |
| `shopware.entity.definition` | Entity definitions |
| `shopware.scheduled.task` | Scheduled tasks |
| `messenger.message_handler` | Message queue handlers |
| `shopware.composite_search.definition` | Search definitions |
| `shopware.sales_channel.context.factory.decorator` | Context factory decorators |

Reference: [Plugin Services](https://developer.shopware.com/docs/guides/plugins/plugins/plugin-fundamentals/add-plugin-dependencies.html)
