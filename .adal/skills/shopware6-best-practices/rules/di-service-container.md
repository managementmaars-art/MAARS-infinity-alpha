---
title: Use Dependency Injection Correctly
impact: MEDIUM
impactDescription: enables testability and proper service management
tags: dependency-injection, services, symfony, container
---

## Use Dependency Injection Correctly

**Impact: MEDIUM (enables testability and proper service management)**

Shopware uses Symfony's dependency injection container. Proper DI practices enable testability, maintainability, and proper service lifecycle management.

**Incorrect (DI anti-patterns):**

```php
// Bad: Service locator pattern
class MyService
{
    public function __construct(
        private readonly ContainerInterface $container
    ) {}

    public function doSomething(): void
    {
        // Bad: Fetching services at runtime
        $productRepository = $this->container->get('product.repository');
        $logger = $this->container->get('logger');
    }
}

// Bad: Using Shopware() global
class AnotherService
{
    public function doSomething(): void
    {
        // Bad: Global state, untestable
        $repo = Shopware()->getContainer()->get('product.repository');
    }
}

// Bad: Creating instances manually
class OrderProcessor
{
    public function process(OrderEntity $order): void
    {
        // Bad: Manual instantiation bypasses DI
        $validator = new OrderValidator();
        $calculator = new PriceCalculator($this->taxService);
    }
}

// Bad: Circular dependencies
class ServiceA
{
    public function __construct(
        private readonly ServiceB $serviceB  // ServiceB depends on ServiceA!
    ) {}
}

// Bad: Too many dependencies
class GodService
{
    public function __construct(
        private readonly EntityRepository $productRepository,
        private readonly EntityRepository $orderRepository,
        private readonly EntityRepository $customerRepository,
        private readonly EntityRepository $categoryRepository,
        private readonly PriceCalculator $priceCalculator,
        private readonly TaxCalculator $taxCalculator,
        private readonly ShippingCalculator $shippingCalculator,
        private readonly DiscountCalculator $discountCalculator,
        private readonly NotificationService $notificationService,
        private readonly LoggerInterface $logger,
        // ... 10+ more dependencies = code smell!
    ) {}
}
```

**Correct (proper DI usage):**

```php
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\Service;

use Psr\Log\LoggerInterface;
use Shopware\Core\Framework\DataAbstractionLayer\EntityRepository;

// Good: Constructor injection with typed properties
class OrderProcessingService
{
    public function __construct(
        private readonly EntityRepository $orderRepository,
        private readonly PriceCalculationService $priceCalculator,
        private readonly LoggerInterface $logger
    ) {}

    public function processOrder(string $orderId, Context $context): void
    {
        // All dependencies injected and available
        $this->logger->info('Processing order', ['orderId' => $orderId]);

        $order = $this->orderRepository->search(
            new Criteria([$orderId]),
            $context
        )->first();

        $total = $this->priceCalculator->calculate($order);
    }
}
```

```xml
<!-- Good: Proper service registration in services.xml -->
<?xml version="1.0" ?>
<container xmlns="http://symfony.com/schema/dic/services"
           xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
           xsi:schemaLocation="http://symfony.com/schema/dic/services
           https://symfony.com/schema/dic/services/services-1.0.xsd">

    <services>
        <!-- Good: Enable autowiring for cleaner configuration -->
        <defaults autowire="true" autoconfigure="true" public="false"/>

        <!-- Good: Explicit dependency injection -->
        <service id="MyVendor\MyPlugin\Service\OrderProcessingService">
            <argument type="service" id="order.repository"/>
            <argument type="service" id="MyVendor\MyPlugin\Service\PriceCalculationService"/>
            <argument type="service" id="logger"/>
        </service>

        <!-- Good: Using factory for complex instantiation -->
        <service id="MyVendor\MyPlugin\Service\ComplexService">
            <factory service="MyVendor\MyPlugin\Factory\ComplexServiceFactory"
                     method="create"/>
        </service>

        <!-- Good: Lazy loading for expensive services -->
        <service id="MyVendor\MyPlugin\Service\ExpensiveService" lazy="true">
            <argument type="service" id="some.heavy.dependency"/>
        </service>

        <!-- Good: Tagged services for extensibility -->
        <service id="MyVendor\MyPlugin\Processor\ProductProcessor">
            <tag name="my_plugin.processor" priority="100"/>
        </service>

        <service id="MyVendor\MyPlugin\Processor\OrderProcessor">
            <tag name="my_plugin.processor" priority="50"/>
        </service>

        <!-- Good: Collecting tagged services -->
        <service id="MyVendor\MyPlugin\Service\ProcessorRegistry">
            <argument type="tagged_iterator" tag="my_plugin.processor"/>
        </service>
    </services>
</container>
```

```php
// Good: Using tagged services
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\Service;

class ProcessorRegistry
{
    /** @var iterable<ProcessorInterface> */
    private iterable $processors;

    public function __construct(iterable $processors)
    {
        $this->processors = $processors;
    }

    public function process(mixed $data): void
    {
        foreach ($this->processors as $processor) {
            $processor->process($data);
        }
    }
}
```

```php
// Good: Breaking up large services
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\Service;

// Good: Single responsibility - each service does one thing
class OrderValidator
{
    public function __construct(
        private readonly EntityRepository $orderRepository,
        private readonly ValidationRulesProvider $rulesProvider
    ) {}

    public function validate(OrderEntity $order): ValidationResult
    {
        // Only validation logic
    }
}

class OrderPriceCalculator
{
    public function __construct(
        private readonly TaxCalculator $taxCalculator,
        private readonly DiscountService $discountService
    ) {}

    public function calculateTotal(OrderEntity $order): Money
    {
        // Only price calculation
    }
}

// Good: Facade for orchestration if needed
class OrderService
{
    public function __construct(
        private readonly OrderValidator $validator,
        private readonly OrderPriceCalculator $calculator,
        private readonly OrderNotifier $notifier
    ) {}

    public function processOrder(OrderEntity $order): void
    {
        // Orchestrates but doesn't implement
        $this->validator->validate($order);
        $this->calculator->calculateTotal($order);
        $this->notifier->notify($order);
    }
}
```

**Service configuration options:**

| Attribute | Purpose |
|-----------|---------|
| `autowire="true"` | Auto-inject typed dependencies |
| `autoconfigure="true"` | Auto-apply tags based on interfaces |
| `public="false"` | Only inject, don't fetch from container |
| `lazy="true"` | Defer instantiation until first use |
| `shared="false"` | New instance per injection |

Reference: [Add Plugin Dependencies](https://developer.shopware.com/docs/guides/plugins/plugins/plugin-fundamentals/add-plugin-dependencies.html)
