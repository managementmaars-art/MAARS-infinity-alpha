---
title: Custom Flow Actions Implementation
impact: MEDIUM
impactDescription: Hardcoded business logic prevents merchant customization and requires developer intervention for every workflow change.
tags: [shopware6, flow-builder, actions, automation, extensibility]
---

## Create Custom Flow Actions for Configurable Business Logic

Implement FlowAction classes to expose plugin functionality in Flow Builder. This allows merchants to configure automated responses to business events without code changes.

Reference: https://developer.shopware.com/docs/guides/plugins/plugins/framework/event/add-flow-builder-action

### Incorrect

```php
// Bad: Hardcoded logic in event subscriber
class OrderSubscriber implements EventSubscriberInterface
{
    public static function getSubscribedEvents(): array
    {
        return [
            OrderStateMachineStateChangeEvent::class => 'onOrderStateChange'
        ];
    }

    public function onOrderStateChange(OrderStateMachineStateChangeEvent $event): void
    {
        $order = $event->getOrder();

        // Bad: Hardcoded conditions, not configurable by merchant
        if ($order->getAmountTotal() > 1000) {
            // Bad: Always sends to same webhook
            $this->webhookService->send('https://erp.example.com/orders', $order);
        }

        // Bad: Hardcoded Slack notification
        if ($order->getStateMachineState()->getTechnicalName() === 'cancelled') {
            $this->slackService->notify('#orders', 'Order cancelled: ' . $order->getOrderNumber());
        }

        // Bad: No way to modify behavior without code changes
        // Bad: Cannot be reused for other events
    }
}

// Bad: Business logic scattered across subscribers
// Bad: Merchant cannot disable or configure actions
```

### Correct

```php
// Good: Create a configurable Flow Action
use Shopware\Core\Content\Flow\Dispatching\Action\FlowAction;
use Shopware\Core\Content\Flow\Dispatching\StorableFlow;

class SendToWebhookAction extends FlowAction
{
    public static function getName(): string
    {
        return 'action.send_to_webhook';
    }

    public static function getSubscribedEvents(): array
    {
        return [
            self::getName() => 'handle',
        ];
    }

    public function requirements(): array
    {
        return [OrderAware::class];
    }

    public function handleFlow(StorableFlow $flow): void
    {
        // Good: Get configuration from Flow Builder
        $webhookUrl = $flow->getConfig()['webhookUrl'] ?? null;
        $includeLineItems = $flow->getConfig()['includeLineItems'] ?? false;

        if (!$webhookUrl) {
            return;
        }

        $orderId = $flow->getData(OrderAware::ORDER_ID);
        $order = $this->getOrder($orderId, $flow->getContext());

        $payload = $this->buildPayload($order, $includeLineItems);

        $this->httpClient->request('POST', $webhookUrl, [
            'json' => $payload
        ]);
    }
}

// Good: Define the action configuration schema
// src/Resources/config/flow-actions.xml
/*
<flow-actions>
    <flow-action name="action.send_to_webhook">
        <label>Send order to webhook</label>
        <label lang="de-DE">Bestellung an Webhook senden</label>

        <requirements>
            <requirement>Shopware\Core\Framework\Event\OrderAware</requirement>
        </requirements>

        <config>
            <field name="webhookUrl" type="text" required="true">
                <label>Webhook URL</label>
            </field>
            <field name="includeLineItems" type="bool">
                <label>Include line items</label>
                <defaultValue>false</defaultValue>
            </field>
        </config>
    </flow-action>
</flow-actions>
*/

// Good: Register the action service
// src/Resources/config/services.xml
/*
<service id="MyPlugin\Flow\Action\SendToWebhookAction">
    <argument type="service" id="Shopware\Core\Framework\DataAbstractionLayer\EntityRepository"/>
    <argument type="service" id="GuzzleHttp\ClientInterface"/>
    <tag name="flow.action"/>
</service>
*/

// Good: Create action with multiple aware interfaces for flexibility
class AddCustomerTagAction extends FlowAction
{
    public static function getName(): string
    {
        return 'action.add_customer_tag';
    }

    public function requirements(): array
    {
        // Good: Works with any event that provides customer data
        return [CustomerAware::class];
    }

    public function handleFlow(StorableFlow $flow): void
    {
        $tagIds = $flow->getConfig()['tagIds'] ?? [];
        $customerId = $flow->getData(CustomerAware::CUSTOMER_ID);

        if (empty($tagIds) || !$customerId) {
            return;
        }

        $tags = array_map(fn($id) => ['id' => $id], $tagIds);

        $this->customerRepository->update([
            [
                'id' => $customerId,
                'tags' => $tags
            ]
        ], $flow->getContext());
    }
}

// Good: Action with conditional logic exposed to merchant
/*
<flow-action name="action.add_customer_tag">
    <config>
        <field name="tagIds" type="multi-entity-id-select" required="true">
            <label>Tags to add</label>
            <entity>tag</entity>
        </field>
    </config>
</flow-action>
*/
```
