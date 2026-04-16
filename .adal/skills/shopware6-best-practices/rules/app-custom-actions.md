---
title: Action Buttons & Custom Actions
impact: HIGH
impactDescription: enables user-triggered integrations from admin interface
tags: app, action-button, admin, integration, modal
---

## Action Buttons & Custom Actions

**Impact: HIGH (enables user-triggered integrations from admin interface)**

Action buttons allow users to trigger app functionality directly from the administration. They appear in entity detail and list views and can return various response types.

**Incorrect (action without proper response):**

```php
// Bad: No response type - user doesn't know what happened
#[Route(path: '/api/sync', methods: ['POST'])]
public function sync(Request $request): Response
{
    $this->syncService->sync();
    return new Response('OK'); // No actionType - confusing UX
}
```

**Correct action button configuration:**

```xml
<!-- manifest.xml -->
<admin>
    <!-- Single entity action (detail view) -->
    <action-button
        action="syncToErp"
        entity="product"
        view="detail"
        url="https://my-app.com/actions/sync-product"
    >
        <label>Sync to ERP</label>
        <label lang="de-DE">Mit ERP synchronisieren</label>
    </action-button>

    <!-- Bulk action (list view) -->
    <action-button
        action="exportSelected"
        entity="order"
        view="list"
        url="https://my-app.com/actions/export-orders"
    >
        <label>Export to CSV</label>
        <label lang="de-DE">Als CSV exportieren</label>
    </action-button>

    <!-- Action with custom icon -->
    <action-button
        action="generateReport"
        entity="order"
        view="detail"
        url="https://my-app.com/actions/generate-report"
    >
        <label>Generate Report</label>
    </action-button>
</admin>
```

**Correct action handler with notification response:**

```php
<?php declare(strict_types=1);

class ActionController
{
    #[Route(path: '/actions/sync-product', methods: ['POST'])]
    public function syncProduct(Request $request): JsonResponse
    {
        // Verify signature
        $payload = $this->verifyRequest($request);

        $productId = $payload['ids'][0] ?? null;
        $shopId = $payload['source']['shopId'];

        if (!$productId) {
            return $this->notificationResponse('error', 'No product selected');
        }

        try {
            // Load product data from Shopware API
            $shop = $this->shopRepository->findByShopId($shopId);
            $product = $this->shopwareClient->getProduct($shop, $productId);

            // Sync to external system
            $externalId = $this->erpService->syncProduct($product);

            // Good: Return success notification
            return $this->notificationResponse(
                'success',
                sprintf('Product synced successfully (ERP ID: %s)', $externalId)
            );

        } catch (\Exception $e) {
            return $this->notificationResponse(
                'error',
                'Sync failed: ' . $e->getMessage()
            );
        }
    }

    private function notificationResponse(string $status, string $message): JsonResponse
    {
        return new JsonResponse([
            'actionType' => 'notification',
            'payload' => [
                'status' => $status, // success, error, warning, info
                'message' => $message
            ]
        ]);
    }
}
```

**Correct action with modal response:**

```php
#[Route(path: '/actions/show-details', methods: ['POST'])]
public function showDetails(Request $request): JsonResponse
{
    $payload = $this->verifyRequest($request);
    $orderId = $payload['ids'][0];

    // Fetch additional data
    $orderDetails = $this->fetchOrderDetails($orderId);

    // Good: Open modal with custom content
    return new JsonResponse([
        'actionType' => 'openModal',
        'payload' => [
            'iframeUrl' => sprintf(
                'https://my-app.com/modal/order-details?orderId=%s&shopId=%s',
                $orderId,
                $payload['source']['shopId']
            ),
            'size' => 'medium', // small, medium, large, fullscreen
            'expand' => true
        ]
    ]);
}
```

**Correct action with redirect response:**

```php
#[Route(path: '/actions/open-external', methods: ['POST'])]
public function openExternal(Request $request): JsonResponse
{
    $payload = $this->verifyRequest($request);
    $entityId = $payload['ids'][0];

    // Generate external URL
    $externalUrl = $this->generateExternalUrl($entityId);

    // Good: Redirect to external page (opens in new tab)
    return new JsonResponse([
        'actionType' => 'openNewTab',
        'payload' => [
            'redirectUrl' => $externalUrl
        ]
    ]);
}
```

**Correct action with reload response:**

```php
#[Route(path: '/actions/update-status', methods: ['POST'])]
public function updateStatus(Request $request): JsonResponse
{
    $payload = $this->verifyRequest($request);
    $productId = $payload['ids'][0];
    $shopId = $payload['source']['shopId'];

    // Update the product in Shopware
    $shop = $this->shopRepository->findByShopId($shopId);
    $this->shopwareClient->updateProduct($shop, $productId, [
        'customFields' => [
            'my_app_sync_status' => 'synced',
            'my_app_last_sync' => (new \DateTime())->format('c')
        ]
    ]);

    // Good: Reload to show updated data
    return new JsonResponse([
        'actionType' => 'reload',
        'payload' => []
    ]);
}
```

**Correct bulk action handling:**

```php
#[Route(path: '/actions/export-orders', methods: ['POST'])]
public function exportOrders(Request $request): JsonResponse
{
    $payload = $this->verifyRequest($request);

    // Good: Handle multiple selected IDs
    $orderIds = $payload['ids'];

    if (empty($orderIds)) {
        return $this->notificationResponse('warning', 'No orders selected');
    }

    try {
        // Process all selected orders
        $shop = $this->shopRepository->findByShopId($payload['source']['shopId']);

        $exportData = [];
        foreach ($orderIds as $orderId) {
            $order = $this->shopwareClient->getOrder($shop, $orderId);
            $exportData[] = $this->formatOrderForExport($order);
        }

        // Generate export file
        $fileUrl = $this->exportService->generateCsv($exportData);

        // Return with download link
        return new JsonResponse([
            'actionType' => 'openNewTab',
            'payload' => [
                'redirectUrl' => $fileUrl
            ]
        ]);

    } catch (\Exception $e) {
        return $this->notificationResponse('error', 'Export failed: ' . $e->getMessage());
    }
}
```

**Request payload structure:**

```json
{
    "source": {
        "url": "https://shop.example.com",
        "appVersion": "1.0.0",
        "shopId": "hRCw2xo1EDZnLco4"
    },
    "data": {
        "ids": ["abc123...", "def456..."],
        "entity": "product",
        "action": "syncToErp"
    }
}
```

**Response action types:**

| Action Type | Purpose |
|-------------|---------|
| `notification` | Show toast notification |
| `openModal` | Open iframe modal |
| `openNewTab` | Open URL in new browser tab |
| `reload` | Reload current admin page |

Reference: [Action Buttons](https://developer.shopware.com/docs/guides/plugins/apps/administration/add-custom-action-button.html)
