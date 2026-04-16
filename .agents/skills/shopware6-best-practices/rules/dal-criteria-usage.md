---
title: DAL Criteria Usage
impact: HIGH
impactDescription: Improper criteria usage leads to performance issues, memory exhaustion, and incomplete query results
tags: [shopware6, dal, criteria, filters, performance, database]
---

## DAL Criteria Usage

The Criteria object is the foundation for all DAL queries in Shopware 6. Proper usage ensures efficient database queries, appropriate data loading, and predictable results.

Reference: https://developer.shopware.com/docs/guides/plugins/plugins/framework/data-handling/reading-data

### Incorrect

```php
// Bad: No limit - loads entire table into memory
public function getAllProducts(Context $context): EntityCollection
{
    $criteria = new Criteria();
    return $this->productRepository->search($criteria, $context)->getEntities();
}

// Bad: Using array syntax instead of Filter objects
public function findByName(string $name, Context $context): EntityCollection
{
    $criteria = new Criteria();
    $criteria->addFilter(['name' => $name]); // Wrong - this doesn't work
    return $this->productRepository->search($criteria, $context)->getEntities();
}

// Bad: Multiple separate queries instead of combined filters
public function findActiveExpensiveProducts(Context $context): EntityCollection
{
    $criteria = new Criteria();
    $criteria->addFilter(new EqualsFilter('active', true));
    $activeProducts = $this->productRepository->search($criteria, $context)->getEntities();

    $expensiveProducts = [];
    foreach ($activeProducts as $product) {
        if ($product->getPrice()->first()->getGross() > 100) {
            $expensiveProducts[] = $product;
        }
    }
    return $expensiveProducts;
}

// Bad: No pagination for large result sets
public function getProductsForExport(Context $context): array
{
    $criteria = new Criteria();
    $criteria->addFilter(new EqualsFilter('active', true));
    // Missing setLimit() and setOffset() - will load everything
    return $this->productRepository->search($criteria, $context)->getEntities()->getElements();
}

// Bad: Hardcoded IDs in queries
public function getSpecificProducts(Context $context): EntityCollection
{
    $criteria = new Criteria([
        'abc123',
        'def456',
        'ghi789'
    ]);
    return $this->productRepository->search($criteria, $context)->getEntities();
}
```

### Correct

```php
// Good: Always set appropriate limits
public function getProducts(Context $context, int $limit = 25, int $offset = 0): EntitySearchResult
{
    $criteria = new Criteria();
    $criteria->setLimit($limit);
    $criteria->setOffset($offset);
    $criteria->setTotalCountMode(Criteria::TOTAL_COUNT_MODE_EXACT);

    return $this->productRepository->search($criteria, $context);
}

// Good: Using proper Filter objects
public function findByName(string $name, Context $context): EntitySearchResult
{
    $criteria = new Criteria();
    $criteria->addFilter(new EqualsFilter('name', $name));
    $criteria->setLimit(25);

    return $this->productRepository->search($criteria, $context);
}

// Good: Using ContainsFilter for partial matches
public function searchByName(string $searchTerm, Context $context): EntitySearchResult
{
    $criteria = new Criteria();
    $criteria->addFilter(new ContainsFilter('name', $searchTerm));
    $criteria->setLimit(25);

    return $this->productRepository->search($criteria, $context);
}

// Good: Combined filters with MultiFilter
public function findActiveExpensiveProducts(Context $context): EntitySearchResult
{
    $criteria = new Criteria();
    $criteria->addFilter(new MultiFilter(
        MultiFilter::CONNECTION_AND,
        [
            new EqualsFilter('active', true),
            new RangeFilter('price.gross', [
                RangeFilter::GTE => 100
            ])
        ]
    ));
    $criteria->setLimit(50);

    return $this->productRepository->search($criteria, $context);
}

// Good: Using NotFilter for exclusions
public function findNonDigitalProducts(Context $context): EntitySearchResult
{
    $criteria = new Criteria();
    $criteria->addFilter(new NotFilter(
        NotFilter::CONNECTION_AND,
        [
            new EqualsFilter('isDownload', true)
        ]
    ));
    $criteria->setLimit(25);

    return $this->productRepository->search($criteria, $context);
}

// Good: Proper sorting
public function getNewestProducts(Context $context, int $limit = 10): EntitySearchResult
{
    $criteria = new Criteria();
    $criteria->addSorting(new FieldSorting('createdAt', FieldSorting::DESCENDING));
    $criteria->setLimit($limit);

    return $this->productRepository->search($criteria, $context);
}

// Good: Multiple sort criteria
public function getProductsSortedByPriceAndName(Context $context): EntitySearchResult
{
    $criteria = new Criteria();
    $criteria->addSorting(
        new FieldSorting('price.gross', FieldSorting::ASCENDING),
        new FieldSorting('name', FieldSorting::ASCENDING)
    );
    $criteria->setLimit(50);

    return $this->productRepository->search($criteria, $context);
}

// Good: Paginated iteration for large datasets
public function processAllActiveProducts(Context $context, callable $processor): void
{
    $criteria = new Criteria();
    $criteria->addFilter(new EqualsFilter('active', true));
    $criteria->setLimit(100);

    $offset = 0;
    do {
        $criteria->setOffset($offset);
        $result = $this->productRepository->search($criteria, $context);

        foreach ($result->getEntities() as $product) {
            $processor($product);
        }

        $offset += 100;
    } while ($result->getTotal() > $offset);
}

// Good: Using IDs from configuration or database
public function getProductsByIds(array $productIds, Context $context): EntitySearchResult
{
    $criteria = new Criteria($productIds);
    $criteria->setLimit(count($productIds));

    return $this->productRepository->search($criteria, $context);
}

// Good: Using aggregations
public function getProductPriceStatistics(Context $context): AggregationResultCollection
{
    $criteria = new Criteria();
    $criteria->addFilter(new EqualsFilter('active', true));
    $criteria->addAggregation(new AvgAggregation('avg-price', 'price.gross'));
    $criteria->addAggregation(new MaxAggregation('max-price', 'price.gross'));
    $criteria->addAggregation(new MinAggregation('min-price', 'price.gross'));
    $criteria->addAggregation(new CountAggregation('total', 'id'));
    $criteria->setLimit(1); // We only need aggregations

    return $this->productRepository->search($criteria, $context)->getAggregations();
}

// Good: Using PrefixFilter for efficient prefix searches
public function findProductsByProductNumber(string $prefix, Context $context): EntitySearchResult
{
    $criteria = new Criteria();
    $criteria->addFilter(new PrefixFilter('productNumber', $prefix));
    $criteria->setLimit(25);

    return $this->productRepository->search($criteria, $context);
}

// Good: Date range filtering
public function getRecentlyCreatedProducts(Context $context, int $days = 7): EntitySearchResult
{
    $criteria = new Criteria();
    $criteria->addFilter(new RangeFilter('createdAt', [
        RangeFilter::GTE => (new \DateTime())->modify("-{$days} days")->format(Defaults::STORAGE_DATE_TIME_FORMAT)
    ]));
    $criteria->addSorting(new FieldSorting('createdAt', FieldSorting::DESCENDING));
    $criteria->setLimit(50);

    return $this->productRepository->search($criteria, $context);
}
```
