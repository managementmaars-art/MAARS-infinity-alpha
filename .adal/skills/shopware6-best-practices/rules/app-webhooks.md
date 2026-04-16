---
title: Webhook Implementation
impact: HIGH
impactDescription: reliable event handling for real-time integrations
tags: app, webhook, events, async, integration
---

## Webhook Implementation

**Impact: HIGH (reliable event handling for real-time integrations)**

Webhooks enable apps to react to Shopware events in real-time. Implement proper signature verification, idempotent handlers, and error handling for reliable integrations.

**Incorrect (insecure webhook handling):**

```php
// Bad: No signature verification
#[Route(path: '/webhooks/order', methods: ['POST'])]
public function handleOrder(Request $request): Response
{
    $data = json_decode($request->getContent(), true);
    // Processing without verification - anyone can call this!
    $this->processOrder($data);
    return new Response('OK');
}
```

```php
// Bad: Not idempotent - will create duplicates
public function handleProductWritten(array $payload): void
{
    // Creates new record every time webhook is called
    $this->externalApi->createProduct($payload['data']);
}
```

**Correct webhook configuration in manifest:**

```xml
<!-- manifest.xml -->
<webhooks>
    <!-- Order lifecycle events -->
    <webhook name="orderPlaced" url="https://my-app.com/webhooks/order-placed" event="checkout.order.placed"/>
    <webhook name="orderPaid" url="https://my-app.com/webhooks/order-paid" event="checkout.order.paid"/>
    <webhook name="orderStateChanged" url="https://my-app.com/webhooks/order-state" event="state_machine.order.state_changed"/>

    <!-- Product events -->
    <webhook name="productWritten" url="https://my-app.com/webhooks/product-written" event="product.written"/>
    <webhook name="productDeleted" url="https://my-app.com/webhooks/product-deleted" event="product.deleted"/>

    <!-- Customer events -->
    <webhook name="customerRegistered" url="https://my-app.com/webhooks/customer-registered" event="customer.register"/>
    <webhook name="customerLogin" url="https://my-app.com/webhooks/customer-login" event="customer.login"/>

    <!-- Payment events -->
    <webhook name="paymentFinalized" url="https://my-app.com/webhooks/payment-finalized" event="checkout.order.payment_method.paid"/>
</webhooks>
```

**Correct webhook handler with signature verification:**

```php
<?php declare(strict_types=1);

namespace App\Controller;

use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;

class WebhookController
{
    public function __construct(
        private readonly ShopRepository $shopRepository,
        private readonly WebhookProcessor $processor,
        private readonly LoggerInterface $logger
    ) {}

    #[Route(path: '/webhooks/order-placed', methods: ['POST'])]
    public function orderPlaced(Request $request): Response
    {
        try {
            // Good: Verify signature first
            $payload = $this->verifyAndParseRequest($request);

            // Good: Log for debugging
            $this->logger->info('Order webhook received', [
                'shopId' => $payload['source']['shopId'],
                'orderId' => $payload['data']['payload'][0]['id'] ?? null
            ]);

            // Good: Process asynchronously for reliability
            $this->processor->queueOrderProcessing($payload);

            return new Response('', Response::HTTP_OK);

        } catch (SignatureVerificationException $e) {
            $this->logger->warning('Webhook signature verification failed', [
                'error' => $e->getMessage()
            ]);
            return new Response('Unauthorized', Response::HTTP_UNAUTHORIZED);

        } catch (\Throwable $e) {
            $this->logger->error('Webhook processing failed', [
                'error' => $e->getMessage(),
                'trace' => $e->getTraceAsString()
            ]);
            // Return 500 so Shopware retries
            return new Response('Error', Response::HTTP_INTERNAL_SERVER_ERROR);
        }
    }

    private function verifyAndParseRequest(Request $request): array
    {
        $content = $request->getContent();
        $payload = json_decode($content, true);

        if (!$payload) {
            throw new \InvalidArgumentException('Invalid JSON payload');
        }

        // Get shop credentials
        $shopId = $payload['source']['shopId'];
        $shop = $this->shopRepository->findByShopId($shopId);

        if (!$shop) {
            throw new SignatureVerificationException('Unknown shop: ' . $shopId);
        }

        // Verify HMAC signature
        $signature = $request->headers->get('shopware-shop-signature');
        $expectedSignature = hash_hmac('sha256', $content, $shop->getShopSecret());

        if (!hash_equals($expectedSignature, $signature)) {
            throw new SignatureVerificationException('Invalid signature');
        }

        return $payload;
    }
}
```

**Correct idempotent processing:**

```php
class WebhookProcessor
{
    public function __construct(
        private readonly EntityManagerInterface $em,
        private readonly ExternalApiClient $externalApi,
        private readonly LoggerInterface $logger
    ) {}

    public function processProductWritten(array $payload): void
    {
        foreach ($payload['data']['payload'] as $productData) {
            $productId = $productData['id'];

            // Good: Check if already processed (idempotent)
            $existingSync = $this->em->getRepository(ProductSync::class)
                ->findOneBy(['shopwareProductId' => $productId]);

            if ($existingSync && $existingSync->getUpdatedAt() >= new \DateTime($productData['updatedAt'])) {
                $this->logger->info('Product already synced, skipping', ['productId' => $productId]);
                continue;
            }

            // Good: Use upsert pattern
            try {
                $externalId = $this->externalApi->upsertProduct($productData);

                // Track sync state
                $sync = $existingSync ?? new ProductSync();
                $sync->setShopwareProductId($productId);
                $sync->setExternalId($externalId);
                $sync->setUpdatedAt(new \DateTime());
                $sync->setSyncStatus('success');

                $this->em->persist($sync);
                $this->em->flush();

            } catch (\Exception $e) {
                $this->logger->error('Product sync failed', [
                    'productId' => $productId,
                    'error' => $e->getMessage()
                ]);

                // Track failure for retry
                $sync = $existingSync ?? new ProductSync();
                $sync->setShopwareProductId($productId);
                $sync->setSyncStatus('failed');
                $sync->setLastError($e->getMessage());
                $this->em->persist($sync);
                $this->em->flush();
            }
        }
    }
}
```

**Common webhook events:**

| Event | Trigger |
|-------|---------|
| `checkout.order.placed` | New order created |
| `checkout.order.paid` | Order payment completed |
| `state_machine.order.state_changed` | Order state change |
| `product.written` | Product created/updated |
| `product.deleted` | Product deleted |
| `customer.register` | New customer registration |
| `customer.login` | Customer logged in |
| `stock.depleted` | Product stock reached 0 |

**Webhook payload structure:**

```json
{
    "source": {
        "url": "https://shop.example.com",
        "shopId": "hRCw2xo1EDZnLco4",
        "appVersion": "1.0.0"
    },
    "data": {
        "payload": [
            {
                "id": "abc123...",
                "versionId": null,
                "orderNumber": "10001",
                "price": {
                    "netPrice": 100.00,
                    "totalPrice": 119.00
                }
            }
        ],
        "event": "checkout.order.placed"
    },
    "timestamp": 1704067200
}
```

**Retry behavior:**

Shopware retries failed webhooks (5xx responses) with exponential backoff:
- 1st retry: 30 seconds
- 2nd retry: 5 minutes
- 3rd retry: 1 hour
- Maximum 3 retries

**Best practices:**

1. Always verify signatures
2. Return 200 quickly, process async
3. Implement idempotent handlers
4. Track sync state for recovery
5. Log all webhook activities
6. Handle retries gracefully

Reference: [Webhooks](https://developer.shopware.com/docs/guides/plugins/apps/app-webhooks.html)
