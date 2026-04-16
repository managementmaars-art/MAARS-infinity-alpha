---
title: Extension API for Apps
impact: MEDIUM
impactDescription: enables headless admin extensions via apps
tags: administration, extension-api, app, iframes, actions
---

## Extension API for Apps

**Impact: MEDIUM (enables headless admin extensions via apps)**

The Extension API allows apps to extend the administration without bundling Vue.js components. Use it for action buttons, custom modules via iframes, and communication between app and admin.

**Incorrect (trying to bundle Vue components in apps):**

```javascript
// Bad: Apps cannot bundle Vue components directly
// This won't work in app context
Vue.component('my-app-component', {
    template: '<div>This will not load</div>'
});
```

**Correct (using Extension API for action buttons):**

```xml
<!-- manifest.xml - Define action buttons -->
<?xml version="1.0" encoding="UTF-8"?>
<manifest xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
          xsi:noNamespaceSchemaLocation="https://raw.githubusercontent.com/shopware/shopware/trunk/src/Core/Framework/App/Manifest/Schema/manifest-2.0.xsd">
    <meta>
        <name>MyApp</name>
        <label>My App</label>
        <!-- ... -->
    </meta>

    <admin>
        <!-- Action button in product detail -->
        <action-button
            action="syncProduct"
            entity="product"
            view="detail"
            url="https://my-app.com/api/sync-product"
        >
            <label>Sync to External System</label>
        </action-button>

        <!-- Action button in order listing -->
        <action-button
            action="exportOrders"
            entity="order"
            view="list"
            url="https://my-app.com/api/export-orders"
        >
            <label>Export Selected</label>
        </action-button>
    </admin>
</manifest>
```

**Correct (handling action button requests):**

```php
// App backend handling the action
class ActionController
{
    #[Route(path: '/api/sync-product', name: 'api.my-app.sync-product', methods: ['POST'])]
    public function syncProduct(Request $request): JsonResponse
    {
        // Shopware sends signed request with entity data
        $payload = json_decode($request->getContent(), true);

        // Verify signature
        $signature = $request->headers->get('shopware-shop-signature');
        if (!$this->verifySignature($payload, $signature)) {
            return new JsonResponse(['error' => 'Invalid signature'], 401);
        }

        // Get entity IDs from payload
        $productIds = $payload['ids'];
        $shopUrl = $payload['source']['url'];

        // Process the action
        foreach ($productIds as $productId) {
            $this->syncService->syncProduct($productId, $shopUrl);
        }

        // Return response (shown as notification in admin)
        return new JsonResponse([
            'actionType' => 'notification',
            'payload' => [
                'status' => 'success',
                'message' => sprintf('Synced %d products', count($productIds))
            ]
        ]);
    }
}
```

**Correct (custom admin module via iframe):**

```xml
<!-- manifest.xml - Register custom module -->
<admin>
    <module
        name="my-app-module"
        source="https://my-app.com/admin/module"
        parent="sw-catalogue"
        position="100"
    >
        <label>My App Module</label>
        <label lang="de-DE">Mein App Modul</label>
    </module>
</admin>
```

**Correct (Extension API in iframe):**

```html
<!-- https://my-app.com/admin/module -->
<!DOCTYPE html>
<html>
<head>
    <title>My App Module</title>
    <!-- Include Shopware Extension SDK -->
    <script src="https://unpkg.com/@shopware-ag/admin-extension-sdk/cdn"></script>
</head>
<body>
    <div id="app">
        <h1>My App Module</h1>
        <button id="load-products">Load Products</button>
        <div id="products"></div>
    </div>

    <script>
        // Initialize SDK
        const { location, data, notification, context } = sw;

        // Get current language
        context.getLanguage().then(language => {
            console.log('Current language:', language.languageId);
        });

        // Load data from Shopware
        document.getElementById('load-products').addEventListener('click', async () => {
            try {
                const products = await data.repository('product').search({
                    limit: 10,
                    associations: {
                        cover: {}
                    }
                });

                renderProducts(products);
            } catch (error) {
                notification.dispatch({
                    title: 'Error',
                    message: error.message,
                    variant: 'error'
                });
            }
        });

        function renderProducts(products) {
            const container = document.getElementById('products');
            container.innerHTML = products.map(p =>
                `<div class="product">
                    <strong>${p.name}</strong>
                    <span>${p.productNumber}</span>
                </div>`
            ).join('');
        }
    </script>
</body>
</html>
```

**Extension SDK methods:**

```javascript
// Data operations
const { data } = sw;

// Search entities
const products = await data.repository('product').search({
    limit: 25,
    filter: [
        { type: 'equals', field: 'active', value: true }
    ],
    associations: {
        manufacturer: {},
        categories: {}
    }
});

// Get single entity
const product = await data.repository('product').get(productId);

// Save entity
await data.repository('product').save({
    id: productId,
    name: 'Updated Name'
});

// Delete entity
await data.repository('product').delete(productId);

// Subscribe to entity changes
data.subscribe('product', ({ id, entity }) => {
    console.log('Product changed:', id, entity);
});
```

```javascript
// UI operations
const { notification, modal, context } = sw;

// Show notification
notification.dispatch({
    title: 'Success',
    message: 'Operation completed',
    variant: 'success' // success, error, warning, info
});

// Open modal
modal.open({
    title: 'Confirm Action',
    message: 'Are you sure?',
    buttons: [
        { label: 'Cancel', variant: 'secondary', action: 'cancel' },
        { label: 'Confirm', variant: 'primary', action: 'confirm' }
    ]
}).then(result => {
    if (result === 'confirm') {
        // User confirmed
    }
});

// Get context info
const language = await context.getLanguage();
const currency = await context.getCurrency();
const environment = await context.getEnvironment(); // production, development
```

```javascript
// Location helpers
const { location } = sw;

// Navigate to Shopware route
location.push({ name: 'sw.product.detail', params: { id: productId } });

// Start full-page loading
location.startLoading();
location.stopLoading();

// Reload current route
location.reload();
```

**Main module vs settings module:**

```xml
<!-- Main navigation module -->
<module name="my-main-module" source="..." parent="sw-catalogue">
    <label>My Module</label>
</module>

<!-- Settings module (appears in Settings area) -->
<module name="my-settings" source="..." parent="sw-settings">
    <label>My App Settings</label>
</module>
```

Reference: [Admin Extension API](https://developer.shopware.com/docs/guides/plugins/apps/administration/add-custom-action-button.html)
