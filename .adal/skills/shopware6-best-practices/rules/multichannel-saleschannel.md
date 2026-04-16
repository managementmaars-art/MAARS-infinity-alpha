---
title: Sales Channel Awareness
impact: HIGH
impactDescription: proper multi-channel data separation and configuration
tags: sales-channel, multi-channel, context, isolation
---

## Sales Channel Awareness

**Impact: HIGH (proper multi-channel data separation and configuration)**

Sales channels represent different storefronts (B2C, B2B, marketplaces). Always consider sales channel context in data operations, configuration, and API routes.

**Incorrect (ignoring sales channel context):**

```php
// Bad: Using Context instead of SalesChannelContext
public function getProducts(Context $context): array
{
    // Missing sales channel filters, visibility, pricing
    return $this->productRepository->search(new Criteria(), $context);
}

// Bad: Hardcoded configuration
public function getShippingPrice(): float
{
    return 4.99; // Same for all sales channels
}
```

**Correct sales channel-aware service:**

```php
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\Service;

use Shopware\Core\Content\Product\SalesChannel\AbstractProductListRoute;
use Shopware\Core\Framework\DataAbstractionLayer\Search\Criteria;
use Shopware\Core\System\SalesChannel\SalesChannelContext;
use Shopware\Core\System\SystemConfig\SystemConfigService;

class ProductService
{
    public function __construct(
        private readonly AbstractProductListRoute $productListRoute,
        private readonly EntityRepository $productRepository,
        private readonly SystemConfigService $configService
    ) {}

    /**
     * Good: Use SalesChannelContext for storefront operations
     * This automatically applies visibility, pricing, and stock rules
     */
    public function getProductsForStorefront(
        Criteria $criteria,
        SalesChannelContext $context
    ): ProductListRouteResponse {
        // ProductListRoute respects sales channel visibility
        return $this->productListRoute->load($criteria, $context);
    }

    /**
     * Good: Get sales channel specific configuration
     */
    public function getShippingPrice(SalesChannelContext $context): float
    {
        $salesChannelId = $context->getSalesChannelId();

        // Config can be set per sales channel
        return (float) $this->configService->get(
            'MyPlugin.config.shippingPrice',
            $salesChannelId
        ) ?: 4.99;
    }

    /**
     * Good: Filter by sales channel visibility in admin context
     */
    public function getProductsForAdmin(
        Criteria $criteria,
        Context $context,
        ?string $salesChannelId = null
    ): EntitySearchResult {
        if ($salesChannelId) {
            // Filter to products visible in specific sales channel
            $criteria->addFilter(
                new EqualsFilter('visibilities.salesChannelId', $salesChannelId)
            );
        }

        return $this->productRepository->search($criteria, $context);
    }
}
```

**Correct sales channel-aware Store API route:**

```php
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\Storefront\Controller;

use Shopware\Core\System\SalesChannel\SalesChannelContext;
use Shopware\Storefront\Controller\StorefrontController;

#[Route(defaults: ['_routeScope' => ['storefront']])]
class MyPluginController extends StorefrontController
{
    #[Route(
        path: '/my-plugin/products',
        name: 'frontend.my-plugin.products',
        methods: ['GET']
    )]
    public function listProducts(
        Request $request,
        SalesChannelContext $context
    ): Response {
        $salesChannelId = $context->getSalesChannel()->getId();
        $currencyId = $context->getCurrencyId();
        $customerGroupId = $context->getCurrentCustomerGroup()->getId();

        // All product data is automatically filtered for this sales channel
        $products = $this->productService->getProductsForStorefront(
            new Criteria(),
            $context
        );

        // Get sales channel specific configuration
        $config = [
            'itemsPerPage' => $this->getConfig('itemsPerPage', $salesChannelId),
            'showPrices' => $this->getConfig('showPrices', $salesChannelId),
        ];

        return $this->renderStorefront('@MyPlugin/storefront/page/products.html.twig', [
            'products' => $products,
            'config' => $config,
            'salesChannel' => $context->getSalesChannel()
        ]);
    }
}
```

**Correct sales channel-aware data creation:**

```php
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\Service;

class ProductCreationService
{
    public function createProduct(
        array $data,
        Context $context,
        array $salesChannelIds = []
    ): string {
        $productId = Uuid::randomHex();

        // Build visibilities for each sales channel
        $visibilities = [];
        foreach ($salesChannelIds as $salesChannelId) {
            $visibilities[] = [
                'id' => Uuid::randomHex(),
                'productId' => $productId,
                'salesChannelId' => $salesChannelId,
                'visibility' => ProductVisibilityDefinition::VISIBILITY_ALL
            ];
        }

        $this->productRepository->create([
            [
                'id' => $productId,
                'name' => $data['name'],
                'productNumber' => $data['productNumber'],
                'stock' => $data['stock'],
                'taxId' => $data['taxId'],
                'price' => $this->buildPrices($data['price']),
                // Good: Set visibility per sales channel
                'visibilities' => $visibilities,
                // Good: Sales channel specific categories
                'categories' => $this->getCategoriesForSalesChannels($data['categories'], $salesChannelIds)
            ]
        ], $context);

        return $productId;
    }

    private function buildPrices(array $priceData): array
    {
        $prices = [];

        // Default price (all currencies)
        $prices[] = [
            'currencyId' => Defaults::CURRENCY,
            'gross' => $priceData['gross'],
            'net' => $priceData['net'],
            'linked' => true
        ];

        // Sales channel specific prices (optional)
        foreach ($priceData['channelPrices'] ?? [] as $channelPrice) {
            $prices[] = [
                'currencyId' => $channelPrice['currencyId'],
                'gross' => $channelPrice['gross'],
                'net' => $channelPrice['net'],
                'linked' => false
            ];
        }

        return $prices;
    }
}
```

**Correct scheduled task with sales channel iteration:**

```php
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\ScheduledTask;

class SyncTaskHandler extends ScheduledTaskHandler
{
    public function __construct(
        private readonly EntityRepository $salesChannelRepository,
        private readonly SyncService $syncService
    ) {}

    public function run(): void
    {
        $context = Context::createDefaultContext();

        // Get all active sales channels
        $criteria = new Criteria();
        $criteria->addFilter(new EqualsFilter('active', true));
        $criteria->addFilter(new EqualsFilter('typeId', Defaults::SALES_CHANNEL_TYPE_STOREFRONT));

        $salesChannels = $this->salesChannelRepository->search($criteria, $context);

        foreach ($salesChannels as $salesChannel) {
            $this->logger->info('Syncing sales channel', [
                'salesChannelId' => $salesChannel->getId(),
                'name' => $salesChannel->getName()
            ]);

            try {
                // Create sales channel context for proper data isolation
                $salesChannelContext = $this->createSalesChannelContext($salesChannel);

                $this->syncService->syncForSalesChannel($salesChannelContext);

            } catch (\Exception $e) {
                $this->logger->error('Sync failed for sales channel', [
                    'salesChannelId' => $salesChannel->getId(),
                    'error' => $e->getMessage()
                ]);
            }
        }
    }
}
```

**Product visibility levels:**

| Visibility | Value | Description |
|------------|-------|-------------|
| `VISIBILITY_ALL` | 30 | Visible everywhere |
| `VISIBILITY_SEARCH` | 20 | Only in search results |
| `VISIBILITY_LINK` | 10 | Only via direct link |

**Sales channel context properties:**

| Property | Method | Description |
|----------|--------|-------------|
| Sales Channel ID | `getSalesChannelId()` | Current sales channel |
| Currency | `getCurrencyId()` | Active currency |
| Customer Group | `getCurrentCustomerGroup()` | Customer group |
| Customer | `getCustomer()` | Logged in customer |
| Language | `getLanguageId()` | Current language |
| Tax State | `getTaxState()` | Gross/net display |
| Shipping Method | `getShippingMethod()` | Selected shipping |
| Payment Method | `getPaymentMethod()` | Selected payment |

Reference: [Sales Channel](https://developer.shopware.com/docs/concepts/commerce/core-concepts/sales-channel.html)
