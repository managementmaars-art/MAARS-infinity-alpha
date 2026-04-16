---
title: App Manifest Configuration
impact: CRITICAL
impactDescription: proper manifest structure is required for app functionality
tags: app, manifest, configuration, permissions, setup
---

## App Manifest Configuration

**Impact: CRITICAL (proper manifest structure is required for app functionality)**

The manifest.xml is the core configuration file for Shopware apps. It defines metadata, permissions, webhooks, admin extensions, and app lifecycle. A proper manifest is required for the app to install and function correctly.

**Incorrect (incomplete or misconfigured manifest):**

```xml
<!-- Bad: Missing required fields -->
<?xml version="1.0" encoding="UTF-8"?>
<manifest>
    <meta>
        <name>MyApp</name>
        <!-- Missing label, version, author -->
    </meta>
</manifest>
```

```xml
<!-- Bad: Requesting permissions without need -->
<permissions>
    <read>product</read>
    <read>order</read>
    <read>customer</read>
    <create>product</create>
    <update>product</update>
    <delete>product</delete>
    <!-- Requesting all permissions "just in case" -->
</permissions>
```

**Correct app structure:**

```
custom/apps/MyApp/
├── manifest.xml              # Required: App configuration
├── Resources/
│   ├── app/
│   │   └── storefront/       # Optional: Storefront assets
│   │       └── src/
│   ├── views/
│   │   └── storefront/       # Optional: Twig templates
│   ├── config/
│   │   └── config.xml        # Optional: App configuration fields
│   └── scripts/              # Optional: App scripts (Twig)
│       ├── product-page-loaded/
│       └── cart-loaded/
└── .env                      # Optional: Local development config
```

**Correct complete manifest:**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<manifest xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
          xsi:noNamespaceSchemaLocation="https://raw.githubusercontent.com/shopware/shopware/trunk/src/Core/Framework/App/Manifest/Schema/manifest-2.0.xsd">

    <!-- Required: App metadata -->
    <meta>
        <name>MyVendorApp</name>
        <label>My Vendor App</label>
        <label lang="de-DE">Meine Vendor App</label>
        <description>Short description of the app functionality</description>
        <description lang="de-DE">Kurze Beschreibung der App-Funktionalität</description>
        <author>My Vendor Name</author>
        <copyright>(c) by My Vendor</copyright>
        <version>1.0.0</version>
        <icon>icon.png</icon>
        <license>MIT</license>
        <compatibility>~6.6.0</compatibility>
        <privacy>https://my-vendor.com/privacy</privacy>
        <privacyPolicyExtensions>
            This app processes order data for fulfillment purposes.
        </privacyPolicyExtensions>
    </meta>

    <!-- Required for external apps: Setup endpoint -->
    <setup>
        <registrationUrl>https://my-app.com/shopware/register</registrationUrl>
        <secret>myAppSecret123</secret>
    </setup>

    <!-- Required: Declare needed permissions (minimum necessary) -->
    <permissions>
        <read>product</read>
        <read>product_manufacturer</read>
        <read>order</read>
        <read>order_line_item</read>
        <create>order_transaction</create>
        <update>order</update>
    </permissions>

    <!-- Optional: Allow HTTP requests to specific domains -->
    <allowed-hosts>
        <host>my-app.com</host>
        <host>api.external-service.com</host>
    </allowed-hosts>

    <!-- Optional: Webhooks -->
    <webhooks>
        <webhook name="orderPlaced" url="https://my-app.com/webhooks/order-placed" event="checkout.order.placed"/>
        <webhook name="productWritten" url="https://my-app.com/webhooks/product-written" event="product.written"/>
    </webhooks>

    <!-- Optional: Admin extensions -->
    <admin>
        <action-button action="syncProduct" entity="product" view="detail" url="https://my-app.com/api/sync">
            <label>Sync Product</label>
        </action-button>

        <module name="my-app-dashboard" source="https://my-app.com/admin/dashboard" parent="sw-dashboard" position="50">
            <label>My App Dashboard</label>
        </module>
    </admin>

    <!-- Optional: Custom fields -->
    <custom-fields>
        <custom-field-set>
            <name>my_app_product_fields</name>
            <label>My App Fields</label>
            <label lang="de-DE">Meine App Felder</label>
            <related-entities>
                <product/>
            </related-entities>
            <fields>
                <text name="my_app_external_id">
                    <label>External ID</label>
                    <required>false</required>
                </text>
                <bool name="my_app_sync_enabled">
                    <label>Sync Enabled</label>
                    <required>false</required>
                </bool>
            </fields>
        </custom-field-set>
    </custom-fields>

    <!-- Optional: Storefront cookies -->
    <cookies>
        <cookie>
            <snippet-name>my_app.tracking.cookie</snippet-name>
            <cookie>my_app_session</cookie>
            <expiration>30</expiration>
        </cookie>
    </cookies>

    <!-- Optional: Payment methods -->
    <payments>
        <payment-method>
            <identifier>my_app_payment</identifier>
            <name>My App Payment</name>
            <pay-url>https://my-app.com/payment/pay</pay-url>
            <finalize-url>https://my-app.com/payment/finalize</finalize-url>
        </payment-method>
    </payments>

    <!-- Optional: Tax providers -->
    <tax>
        <tax-provider>
            <identifier>my_app_tax</identifier>
            <name>My Tax Service</name>
            <process-url>https://my-app.com/tax/calculate</process-url>
        </tax-provider>
    </tax>
</manifest>
```

**Correct setup handler (app backend):**

```php
// Registration endpoint - called when app is installed
class AppRegistrationController
{
    #[Route(path: '/shopware/register', methods: ['POST'])]
    public function register(Request $request): JsonResponse
    {
        $payload = json_decode($request->getContent(), true);

        // Verify the request signature
        $signature = $request->headers->get('shopware-app-signature');
        $hmac = hash_hmac('sha256', $request->getContent(), $this->appSecret);

        if (!hash_equals($hmac, $signature)) {
            return new JsonResponse(['error' => 'Invalid signature'], 401);
        }

        // Store shop credentials
        $shop = new Shop();
        $shop->setShopId($payload['shop-id']);
        $shop->setShopUrl($payload['shop-url']);
        $shop->setShopSecret($payload['api-key'] ?? null);

        $this->shopRepository->save($shop);

        // Return confirmation URL and keys
        return new JsonResponse([
            'proof' => hash_hmac('sha256', $payload['shop-id'] . $payload['shop-url'] . $this->appName, $this->appSecret),
            'secret' => $shop->getSecret(),
            'confirmation_url' => 'https://my-app.com/shopware/confirm'
        ]);
    }

    #[Route(path: '/shopware/confirm', methods: ['POST'])]
    public function confirm(Request $request): JsonResponse
    {
        $payload = json_decode($request->getContent(), true);

        // Store the API credentials for later use
        $shop = $this->shopRepository->findByShopId($payload['shopId']);
        $shop->setApiKey($payload['apiKey']);
        $shop->setSecretKey($payload['secretKey']);
        $this->shopRepository->save($shop);

        return new JsonResponse(['success' => true]);
    }
}
```

**Permission types:**

| Permission | Description |
|------------|-------------|
| `read` | Read entity data |
| `create` | Create new entities |
| `update` | Update existing entities |
| `delete` | Delete entities |

**Common entity permissions:**

```xml
<permissions>
    <!-- Product management -->
    <read>product</read>
    <read>product_manufacturer</read>
    <read>product_media</read>
    <read>category</read>

    <!-- Order processing -->
    <read>order</read>
    <read>order_line_item</read>
    <read>order_customer</read>
    <update>order</update>
    <update>order_delivery</update>

    <!-- Customer data (requires privacy policy!) -->
    <read>customer</read>
    <read>customer_address</read>
</permissions>
```

Reference: [App Base Guide](https://developer.shopware.com/docs/guides/plugins/apps/app-base-guide.html)
