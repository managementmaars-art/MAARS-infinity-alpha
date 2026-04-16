---
title: Implement Event Subscribers Correctly
impact: CRITICAL
impactDescription: enables extensible and decoupled customizations
tags: events, subscribers, hooks, customization
---

## Implement Event Subscribers Correctly

**Impact: CRITICAL (enables extensible and decoupled customizations)**

Event subscribers are the primary extension mechanism in Shopware 6 for reacting to system events without modifying core code. Proper implementation ensures reliability and performance.

**Incorrect (problematic event handling):**

```php
// Bad: Not implementing EventSubscriberInterface properly
class MySubscriber
{
    public function onProductLoaded($event): void
    {
        // Won't be called - not properly registered!
    }
}

// Bad: Wrong event class or missing type hints
class BrokenSubscriber implements EventSubscriberInterface
{
    public static function getSubscribedEvents(): array
    {
        return [
            'product.loaded' => 'onProductLoaded',  // Wrong! Use class constant
        ];
    }

    public function onProductLoaded($event): void  // Missing type hint!
    {
        // ...
    }
}

// Bad: Blocking operations in synchronous events
class SlowSubscriber implements EventSubscriberInterface
{
    public static function getSubscribedEvents(): array
    {
        return [
            ProductEvents::PRODUCT_LOADED_EVENT => 'onProductLoaded',
        ];
    }

    public function onProductLoaded(EntityLoadedEvent $event): void
    {
        foreach ($event->getEntities() as $product) {
            // Bad: HTTP call in synchronous event blocks response!
            $externalData = $this->httpClient->get('https://api.example.com/product/' . $product->getId());
            $product->addExtension('externalData', new ArrayEntity($externalData));
        }
    }
}

// Bad: Modifying entities outside write events
class DangerousSubscriber implements EventSubscriberInterface
{
    public static function getSubscribedEvents(): array
    {
        return [
            ProductEvents::PRODUCT_LOADED_EVENT => 'onProductLoaded',
        ];
    }

    public function onProductLoaded(EntityLoadedEvent $event): void
    {
        foreach ($event->getEntities() as $product) {
            // Bad: Writing to DB in a loaded event can cause infinite loops!
            $this->productRepository->update([
                ['id' => $product->getId(), 'customField' => 'value']
            ], $event->getContext());
        }
    }
}
```

**Correct (proper event subscriber implementation):**

```php
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\Subscriber;

use Shopware\Core\Content\Product\ProductEvents;
use Shopware\Core\Content\Product\ProductEntity;
use Shopware\Core\Framework\DataAbstractionLayer\Event\EntityLoadedEvent;
use Shopware\Core\Framework\DataAbstractionLayer\Event\EntityWrittenEvent;
use Shopware\Core\Framework\Struct\ArrayEntity;
use Symfony\Component\EventDispatcher\EventSubscriberInterface;

class ProductSubscriber implements EventSubscriberInterface
{
    public function __construct(
        private readonly CustomDataService $customDataService,
        private readonly MessageBusInterface $messageBus
    ) {}

    // Good: Use class constants for event names
    public static function getSubscribedEvents(): array
    {
        return [
            ProductEvents::PRODUCT_LOADED_EVENT => 'onProductLoaded',
            ProductEvents::PRODUCT_WRITTEN_EVENT => 'onProductWritten',
        ];
    }

    // Good: Proper type hints
    public function onProductLoaded(EntityLoadedEvent $event): void
    {
        /** @var ProductEntity $product */
        foreach ($event->getEntities() as $product) {
            // Good: Use cached/local data, not external calls
            $customData = $this->customDataService->getCachedData($product->getId());

            if ($customData !== null) {
                // Good: Use extensions for additional data
                $product->addExtension('myCustomData', new ArrayEntity($customData));
            }
        }
    }

    public function onProductWritten(EntityWrittenEvent $event): void
    {
        $ids = [];
        foreach ($event->getWriteResults() as $result) {
            $ids[] = $result->getPrimaryKey();
        }

        // Good: Dispatch async message for heavy processing
        $this->messageBus->dispatch(new ProductSyncMessage($ids));
    }
}
```

```php
// Good: Subscriber with priority control
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\Subscriber;

use Shopware\Core\Checkout\Cart\Event\CartBeforeSerializationEvent;
use Shopware\Core\Checkout\Cart\Event\CartLoadedEvent;
use Symfony\Component\EventDispatcher\EventSubscriberInterface;

class CartSubscriber implements EventSubscriberInterface
{
    public static function getSubscribedEvents(): array
    {
        return [
            // Good: Use priority to control execution order
            // Higher priority = runs first
            CartLoadedEvent::class => ['onCartLoaded', 100],

            // Multiple handlers for same event
            CartBeforeSerializationEvent::class => [
                ['addCustomData', 200],
                ['validateCart', 100],
            ],
        ];
    }

    public function onCartLoaded(CartLoadedEvent $event): void
    {
        $cart = $event->getCart();
        // Enrich cart data
    }

    public function addCustomData(CartBeforeSerializationEvent $event): void
    {
        // Add custom data before serialization
    }

    public function validateCart(CartBeforeSerializationEvent $event): void
    {
        // Validate cart state
    }
}
```

```php
// Good: Subscriber that modifies write operations
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\Subscriber;

use Shopware\Core\Content\Product\ProductEvents;
use Shopware\Core\Framework\DataAbstractionLayer\Event\BeforeDeleteEvent;
use Shopware\Core\Framework\DataAbstractionLayer\Event\EntityWriteEvent;
use Shopware\Core\Framework\DataAbstractionLayer\Write\Command\DeleteCommand;
use Shopware\Core\Framework\DataAbstractionLayer\Write\Validation\PreWriteValidationEvent;
use Symfony\Component\EventDispatcher\EventSubscriberInterface;

class ProductWriteSubscriber implements EventSubscriberInterface
{
    public static function getSubscribedEvents(): array
    {
        return [
            PreWriteValidationEvent::class => 'onPreWriteValidation',
            BeforeDeleteEvent::class => 'onBeforeDelete',
        ];
    }

    // Good: Validate before write
    public function onPreWriteValidation(PreWriteValidationEvent $event): void
    {
        foreach ($event->getCommands() as $command) {
            if ($command->getEntityName() !== 'product') {
                continue;
            }

            $payload = $command->getPayload();

            if (isset($payload['price']) && $payload['price'] < 0) {
                $event->getExceptions()->add(
                    new InvalidPriceException('Price cannot be negative')
                );
            }
        }
    }

    // Good: Handle cascading deletes
    public function onBeforeDelete(BeforeDeleteEvent $event): void
    {
        $ids = $event->getIds('product');

        if (empty($ids)) {
            return;
        }

        // Clean up related custom data before product deletion
        $this->customDataRepository->delete(
            array_map(fn($id) => ['productId' => $id], $ids),
            $event->getContext()
        );
    }
}
```

**Event execution order:**

| Priority | When to Use |
|----------|-------------|
| 500+ | Critical validation, security checks |
| 100-500 | Normal business logic |
| 0 | Default priority |
| -100 to 0 | Post-processing, cleanup |
| < -100 | Final handlers, logging |

Reference: [Listening to Events](https://developer.shopware.com/docs/guides/plugins/plugins/plugin-fundamentals/listening-to-events.html)
