---
title: Business Events and Flow Integration
impact: MEDIUM-HIGH
impactDescription: Missing business events prevents Flow Builder integration, reduces extensibility, and forces hardcoded business logic that cannot be customized by merchants.
tags: [shopware6, events, flow-builder, business-events, extensibility]
---

## Create Business Events for Flow Builder Integration

Implement FlowEventAware events for significant business actions to enable Flow Builder automation. This allows merchants to configure reactions without code changes and makes your plugin extensible.

Reference: https://developer.shopware.com/docs/guides/plugins/plugins/framework/event/add-flow-builder-trigger

### Incorrect

```php
// Bad: No events dispatched for business logic
class SubscriptionService
{
    public function __construct(
        private readonly EntityRepository $subscriptionRepository,
        private readonly MailService $mailService
    ) {
    }

    public function cancelSubscription(string $subscriptionId, Context $context): void
    {
        $this->subscriptionRepository->update([
            [
                'id' => $subscriptionId,
                'status' => 'cancelled',
                'cancelledAt' => new \DateTime()
            ]
        ], $context);

        // Bad: Hardcoded email sending, not configurable
        $this->mailService->send('subscription_cancelled', $subscriptionId);

        // Bad: Hardcoded webhook call
        $this->webhookService->notify('subscription.cancelled', $subscriptionId);

        // Bad: No way for merchants to add custom actions
        // Bad: No way for other plugins to react
    }
}

// Bad: Event without Flow Builder integration
class SubscriptionCancelledEvent extends Event
{
    // Bad: Not implementing FlowEventAware
    // Bad: Cannot be used in Flow Builder
    public function __construct(
        private readonly string $subscriptionId
    ) {
    }
}
```

### Correct

```php
// Good: Create a proper business event with Flow Builder support
use Shopware\Core\Content\Flow\Dispatching\Aware\ScalarValuesAware;
use Shopware\Core\Framework\Context;
use Shopware\Core\Framework\Event\CustomerAware;
use Shopware\Core\Framework\Event\EventData\EntityType;
use Shopware\Core\Framework\Event\EventData\EventDataCollection;
use Shopware\Core\Framework\Event\EventData\ScalarValueType;
use Shopware\Core\Framework\Event\FlowEventAware;

class SubscriptionCancelledEvent implements FlowEventAware, CustomerAware, ScalarValuesAware
{
    public const EVENT_NAME = 'subscription.cancelled';

    public function __construct(
        private readonly SubscriptionEntity $subscription,
        private readonly Context $context,
        private readonly string $salesChannelId
    ) {
    }

    public static function getAvailableData(): EventDataCollection
    {
        return (new EventDataCollection())
            ->add('subscription', new EntityType(SubscriptionDefinition::class))
            ->add('cancellationReason', new ScalarValueType(ScalarValueType::TYPE_STRING));
    }

    public function getName(): string
    {
        return self::EVENT_NAME;
    }

    public function getContext(): Context
    {
        return $this->context;
    }

    public function getSalesChannelId(): string
    {
        return $this->salesChannelId;
    }

    public function getCustomerId(): string
    {
        return $this->subscription->getCustomerId();
    }

    public function getSubscription(): SubscriptionEntity
    {
        return $this->subscription;
    }

    public function getValues(): array
    {
        return [
            'cancellationReason' => $this->subscription->getCancellationReason(),
        ];
    }
}

// Good: Register the event as a Flow trigger
// src/Resources/config/flow-events.xml
/*
<container>
    <services>
        <service id="MyPlugin\Event\SubscriptionCancelledEvent">
            <tag name="shopware.flow.event"
                 aware="Shopware\Core\Framework\Event\CustomerAware"/>
        </service>
    </services>
</container>
*/

// Good: Service dispatches event, letting Flow Builder handle reactions
class SubscriptionService
{
    public function __construct(
        private readonly EntityRepository $subscriptionRepository,
        private readonly EventDispatcherInterface $eventDispatcher
    ) {
    }

    public function cancelSubscription(string $subscriptionId, SalesChannelContext $context): void
    {
        $subscription = $this->getSubscription($subscriptionId, $context->getContext());

        $this->subscriptionRepository->update([
            [
                'id' => $subscriptionId,
                'status' => 'cancelled',
                'cancelledAt' => new \DateTime()
            ]
        ], $context->getContext());

        // Good: Dispatch event for Flow Builder and other subscribers
        $this->eventDispatcher->dispatch(
            new SubscriptionCancelledEvent(
                $subscription,
                $context->getContext(),
                $context->getSalesChannelId()
            )
        );

        // Good: Merchants configure email, webhooks, tags via Flow Builder
        // Good: Other plugins can subscribe to this event
    }
}

// Good: Add mail template for the event
// src/Resources/config/mail-templates.xml
/*
<mail_template>
    <technical_name>subscription_cancelled</technical_name>
    <available_entities>
        <available_entity>subscription</available_entity>
        <available_entity>customer</available_entity>
    </available_entities>
</mail_template>
*/
```
