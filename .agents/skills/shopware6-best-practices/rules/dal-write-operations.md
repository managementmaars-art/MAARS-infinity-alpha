---
title: DAL Write Operations
impact: HIGH
impactDescription: Inefficient write patterns cause performance degradation, database locks, and data integrity issues
tags: [shopware6, dal, write, create, update, delete, sync, batch]
---

## DAL Write Operations

The DAL provides create, update, upsert, delete, and sync methods for data manipulation. Using the correct method and batching operations is critical for performance.

Reference: https://developer.shopware.com/docs/guides/plugins/plugins/framework/data-handling/writing-data

### Incorrect

```php
// Bad: Individual writes in a loop
public function updateProductPrices(array $priceUpdates, Context $context): void
{
    foreach ($priceUpdates as $productId => $newPrice) {
        $this->productRepository->update([
            [
                'id' => $productId,
                'price' => [['currencyId' => Defaults::CURRENCY, 'gross' => $newPrice, 'net' => $newPrice / 1.19, 'linked' => true]]
            ]
        ], $context);
    }
}

// Bad: Using update() when upsert() is more appropriate
public function syncProducts(array $externalProducts, Context $context): void
{
    foreach ($externalProducts as $product) {
        $criteria = new Criteria();
        $criteria->addFilter(new EqualsFilter('productNumber', $product['sku']));

        $existing = $this->productRepository->search($criteria, $context)->first();

        if ($existing) {
            $this->productRepository->update([
                ['id' => $existing->getId(), 'stock' => $product['stock']]
            ], $context);
        } else {
            $this->productRepository->create([
                ['productNumber' => $product['sku'], 'stock' => $product['stock'], /* ... */]
            ], $context);
        }
    }
}

// Bad: Not using sync for m:n relations
public function setProductCategories(string $productId, array $categoryIds, Context $context): void
{
    // First delete all existing
    $criteria = new Criteria();
    $criteria->addFilter(new EqualsFilter('productId', $productId));
    $existing = $this->productCategoryRepository->searchIds($criteria, $context);

    foreach ($existing->getIds() as $id) {
        $this->productCategoryRepository->delete([['id' => $id]], $context);
    }

    // Then add new ones
    foreach ($categoryIds as $categoryId) {
        $this->productCategoryRepository->create([
            ['productId' => $productId, 'categoryId' => $categoryId]
        ], $context);
    }
}

// Bad: Missing required fields in create
public function createProduct(array $data, Context $context): string
{
    $this->productRepository->create([
        [
            'name' => $data['name'],
            // Missing: productNumber, stock, taxId, price
        ]
    ], $context);

    return $data['id'];
}

// Bad: Deleting without checking dependencies
public function deleteManufacturer(string $manufacturerId, Context $context): void
{
    // May fail if products reference this manufacturer
    $this->manufacturerRepository->delete([
        ['id' => $manufacturerId]
    ], $context);
}

// Bad: Using delete() in a loop
public function deleteOldOrders(Context $context): void
{
    $criteria = new Criteria();
    $criteria->addFilter(new RangeFilter('createdAt', [
        RangeFilter::LT => (new \DateTime('-2 years'))->format(Defaults::STORAGE_DATE_TIME_FORMAT)
    ]));

    $orders = $this->orderRepository->searchIds($criteria, $context);

    foreach ($orders->getIds() as $orderId) {
        $this->orderRepository->delete([['id' => $orderId]], $context);
    }
}
```

### Correct

```php
// Good: Batch all updates in a single operation
public function updateProductPrices(array $priceUpdates, Context $context): void
{
    $updates = [];

    foreach ($priceUpdates as $productId => $newPrice) {
        $updates[] = [
            'id' => $productId,
            'price' => [[
                'currencyId' => Defaults::CURRENCY,
                'gross' => $newPrice,
                'net' => $newPrice / 1.19,
                'linked' => true
            ]]
        ];
    }

    if (!empty($updates)) {
        $this->productRepository->update($updates, $context);
    }
}

// Good: Using upsert() for sync scenarios
public function syncProducts(array $externalProducts, Context $context): void
{
    $upsertData = [];

    foreach ($externalProducts as $product) {
        $upsertData[] = [
            'id' => $this->getProductIdByNumber($product['sku'], $context) ?? Uuid::randomHex(),
            'productNumber' => $product['sku'],
            'name' => $product['name'],
            'stock' => $product['stock'],
            'price' => [[
                'currencyId' => Defaults::CURRENCY,
                'gross' => $product['price'],
                'net' => $product['price'] / 1.19,
                'linked' => true
            ]],
            'taxId' => $this->getDefaultTaxId($context),
        ];
    }

    if (!empty($upsertData)) {
        $this->productRepository->upsert($upsertData, $context);
    }
}

// Good: Using sync() for m:n relations
public function setProductCategories(string $productId, array $categoryIds, Context $context): void
{
    $payload = array_map(
        fn(string $categoryId) => [
            'productId' => $productId,
            'categoryId' => $categoryId
        ],
        $categoryIds
    );

    $this->productRepository->update([
        [
            'id' => $productId,
            'categories' => $payload
        ]
    ], $context);
}

// Good: Alternative using SyncService for complex sync operations
public function syncProductCategories(string $productId, array $categoryIds, Context $context): void
{
    $this->syncService->sync([
        new SyncOperation(
            'product-category-sync',
            'product_category',
            SyncOperation::ACTION_UPSERT,
            array_map(
                fn(string $categoryId) => [
                    'productId' => $productId,
                    'categoryId' => $categoryId
                ],
                $categoryIds
            )
        )
    ], $context, new SyncBehavior());
}

// Good: Complete product creation with all required fields
public function createProduct(array $data, Context $context): string
{
    $productId = Uuid::randomHex();

    $this->productRepository->create([
        [
            'id' => $productId,
            'name' => $data['name'],
            'productNumber' => $data['productNumber'] ?? Uuid::randomHex(),
            'stock' => $data['stock'] ?? 0,
            'taxId' => $data['taxId'] ?? $this->getDefaultTaxId($context),
            'price' => [[
                'currencyId' => Defaults::CURRENCY,
                'gross' => $data['price'],
                'net' => $data['price'] / 1.19,
                'linked' => true
            ]],
            'active' => $data['active'] ?? false,
        ]
    ], $context);

    return $productId;
}

// Good: Batch delete operation
public function deleteOldOrders(Context $context): void
{
    $criteria = new Criteria();
    $criteria->addFilter(new RangeFilter('createdAt', [
        RangeFilter::LT => (new \DateTime('-2 years'))->format(Defaults::STORAGE_DATE_TIME_FORMAT)
    ]));
    $criteria->setLimit(1000);

    $orderIds = $this->orderRepository->searchIds($criteria, $context);

    if ($orderIds->getTotal() === 0) {
        return;
    }

    $deletePayload = array_map(
        fn(string $id) => ['id' => $id],
        $orderIds->getIds()
    );

    $this->orderRepository->delete($deletePayload, $context);
}

// Good: Handle write results and errors
public function createProducts(array $productsData, Context $context): array
{
    $payload = [];
    $results = ['created' => [], 'errors' => []];

    foreach ($productsData as $data) {
        $productId = Uuid::randomHex();
        $payload[] = [
            'id' => $productId,
            'name' => $data['name'],
            'productNumber' => $data['productNumber'],
            'stock' => $data['stock'],
            'taxId' => $this->getDefaultTaxId($context),
            'price' => [[
                'currencyId' => Defaults::CURRENCY,
                'gross' => $data['price'],
                'net' => $data['price'] / 1.19,
                'linked' => true
            ]]
        ];
        $results['created'][] = $productId;
    }

    try {
        $this->productRepository->create($payload, $context);
    } catch (WriteException $e) {
        $results['errors'] = $e->getErrors();
        $results['created'] = [];
    }

    return $results;
}

// Good: Using clone for duplicating entities
public function duplicateProduct(string $productId, Context $context): string
{
    $behavior = new CloneBehavior([
        'productNumber' => Uuid::randomHex(),
        'active' => false,
    ]);

    $newProductId = $this->productRepository->clone($productId, $context, null, $behavior)->getId();

    return $newProductId;
}

// Good: Transactional write with version
public function updateProductWithVersion(string $productId, array $data, Context $context): void
{
    $versionId = $this->productRepository->createVersion($productId, $context);

    $versionContext = $context->createWithVersionId($versionId);

    try {
        $this->productRepository->update([
            ['id' => $productId, ...$data]
        ], $versionContext);

        $this->productRepository->merge($versionId, $context);
    } catch (\Throwable $e) {
        // Version is automatically discarded if not merged
        throw $e;
    }
}

// Good: Chunk large batch operations
public function importProducts(array $largeDataset, Context $context): void
{
    $chunks = array_chunk($largeDataset, 250);

    foreach ($chunks as $chunk) {
        $payload = array_map(function (array $data) use ($context) {
            return [
                'id' => Uuid::randomHex(),
                'productNumber' => $data['sku'],
                'name' => $data['name'],
                'stock' => $data['stock'],
                'taxId' => $this->getDefaultTaxId($context),
                'price' => [[
                    'currencyId' => Defaults::CURRENCY,
                    'gross' => $data['price'],
                    'net' => $data['price'] / 1.19,
                    'linked' => true
                ]]
            ];
        }, $chunk);

        $this->productRepository->create($payload, $context);
    }
}
```
