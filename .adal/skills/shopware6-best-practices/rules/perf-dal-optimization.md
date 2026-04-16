---
title: Optimize DAL Queries for Performance
impact: CRITICAL
impactDescription: prevents N+1 queries and reduces database load
tags: performance, dal, queries, optimization
---

## Optimize DAL Queries for Performance

**Impact: CRITICAL (prevents N+1 queries and reduces database load)**

Shopware's Data Abstraction Layer is powerful but can cause performance issues if misused. Proper query optimization is essential for scalable applications.

**Incorrect (performance anti-patterns):**

```php
// Bad: N+1 query problem - each iteration queries the database
public function getProductsWithCategories(array $productIds, Context $context): array
{
    $result = [];

    foreach ($productIds as $productId) {
        // Bad: One query per product!
        $product = $this->productRepository->search(
            new Criteria([$productId]),
            $context
        )->first();

        // Bad: Another query for each product's categories!
        $categories = $this->categoryRepository->search(
            new Criteria($product->getCategoryIds()),
            $context
        );

        $result[] = ['product' => $product, 'categories' => $categories];
    }

    return $result;  // 2N queries for N products!
}

// Bad: Loading all fields when only few are needed
public function getProductNames(array $productIds, Context $context): array
{
    $criteria = new Criteria($productIds);
    // Loads ALL product fields including large descriptions, media, etc.

    return $this->productRepository->search($criteria, $context);
}

// Bad: Not using aggregations
public function getAveragePrice(Context $context): float
{
    $criteria = new Criteria();
    // Bad: Loads ALL products into memory!
    $products = $this->productRepository->search($criteria, $context);

    $total = 0;
    foreach ($products as $product) {
        $total += $product->getPrice()->first()->getGross();
    }

    return $total / $products->count();
}

// Bad: Loading associations you don't need
public function getProductIds(Context $context): array
{
    $criteria = new Criteria();
    $criteria->addAssociation('manufacturer');
    $criteria->addAssociation('categories');
    $criteria->addAssociation('media');
    $criteria->addAssociation('properties');
    // Loading all these just to get IDs!

    $products = $this->productRepository->search($criteria, $context);

    return $products->getIds();
}
```

**Correct (optimized patterns):**

```php
// Good: Single batch query with associations
public function getProductsWithCategories(array $productIds, Context $context): array
{
    $criteria = new Criteria($productIds);
    // Good: Load categories in single JOIN query
    $criteria->addAssociation('categories');

    // Good: One query for all products with categories
    return $this->productRepository->search($criteria, $context);
}

// Good: Use partial loading when possible
public function getProductNames(array $productIds, Context $context): array
{
    $criteria = new Criteria($productIds);

    // Good: Only load needed fields
    $criteria->addFields(['id', 'name', 'productNumber']);

    return $this->productRepository->search($criteria, $context);
}

// Good: Use aggregations for calculations
public function getAveragePrice(SalesChannelContext $context): float
{
    $criteria = new Criteria();
    $criteria->addAggregation(
        new AvgAggregation('average_price', 'price')
    );
    $criteria->setLimit(1);  // Don't load entities

    $result = $this->productRepository->search($criteria, $context->getContext());

    /** @var AvgResult $avgResult */
    $avgResult = $result->getAggregations()->get('average_price');

    return $avgResult->getAvg();
}

// Good: Use searchIds when only IDs needed
public function getProductIds(Context $context): array
{
    $criteria = new Criteria();
    $criteria->addFilter(new EqualsFilter('active', true));

    // Good: searchIds returns only IDs, no entity hydration
    return $this->productRepository->searchIds($criteria, $context)->getIds();
}

// Good: Batch processing with proper chunking
public function processAllProducts(Context $context): void
{
    $criteria = new Criteria();
    $criteria->setLimit(100);
    $criteria->addSorting(new FieldSorting('id'));

    $iterator = new RepositoryIterator($this->productRepository, $context, $criteria);

    while (($result = $iterator->fetch()) !== null) {
        foreach ($result->getEntities() as $product) {
            $this->processProduct($product);
        }

        // Good: Clear memory between batches
        gc_collect_cycles();
    }
}

// Good: Conditional association loading
public function getProducts(Criteria $criteria, bool $includeMedia, Context $context): EntitySearchResult
{
    // Good: Only load associations when actually needed
    if ($includeMedia) {
        $criteria->addAssociation('media');
        $criteria->addAssociation('cover');
    }

    return $this->productRepository->search($criteria, $context);
}

// Good: Use total count modes appropriately
public function getProductCount(Context $context): int
{
    $criteria = new Criteria();
    $criteria->addFilter(new EqualsFilter('active', true));

    // Good: Only count, don't load data
    $criteria->setTotalCountMode(Criteria::TOTAL_COUNT_MODE_EXACT);
    $criteria->setLimit(1);

    return $this->productRepository->search($criteria, $context)->getTotal();
}

// Good: Indexed fields for filtering
public function getProductsByManufacturer(string $manufacturerId, Context $context): EntitySearchResult
{
    $criteria = new Criteria();

    // Good: manufacturerId is indexed, efficient query
    $criteria->addFilter(new EqualsFilter('manufacturerId', $manufacturerId));

    // Good: Limit results for pagination
    $criteria->setLimit(50);
    $criteria->setOffset(0);

    return $this->productRepository->search($criteria, $context);
}
```

**Query optimization checklist:**

| Pattern | Use Case |
|---------|----------|
| `searchIds()` | When only IDs are needed |
| `addFields()` | Partial entity loading |
| Aggregations | Calculations (SUM, AVG, COUNT) |
| `RepositoryIterator` | Processing large datasets |
| `setLimit()` | Always paginate, never load all |
| `addAssociation()` | Only when association data is used |

Reference: [Reading Data](https://developer.shopware.com/docs/guides/plugins/plugins/framework/data-handling/reading-data.html)
