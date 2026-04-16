---
title: DAL Associations
impact: HIGH
impactDescription: Improper association handling causes N+1 query problems, memory issues, and runtime errors from accessing unloaded data
tags: [shopware6, dal, associations, performance, lazy-loading, eager-loading]
---

## DAL Associations

Shopware 6 DAL does not automatically load associations. You must explicitly request associations in your Criteria to avoid N+1 queries and ensure data availability.

Reference: https://developer.shopware.com/docs/guides/plugins/plugins/framework/data-handling/reading-data#associations

### Incorrect

```php
// Bad: Accessing association that wasn't loaded
public function getProductManufacturerName(string $productId, Context $context): ?string
{
    $criteria = new Criteria([$productId]);
    // Missing: $criteria->addAssociation('manufacturer');

    $product = $this->productRepository->search($criteria, $context)->first();

    // This will return null or trigger lazy loading (deprecated behavior)
    return $product?->getManufacturer()?->getName();
}

// Bad: Loading associations in a loop (N+1 problem)
public function getProductsWithManufacturers(Context $context): array
{
    $criteria = new Criteria();
    $criteria->setLimit(100);

    $products = $this->productRepository->search($criteria, $context)->getEntities();

    $result = [];
    foreach ($products as $product) {
        // Each iteration triggers a separate query!
        $manufacturerCriteria = new Criteria([$product->getManufacturerId()]);
        $manufacturer = $this->manufacturerRepository->search($manufacturerCriteria, $context)->first();

        $result[] = [
            'product' => $product,
            'manufacturer' => $manufacturer
        ];
    }

    return $result;
}

// Bad: Loading too many associations at once
public function getProductWithEverything(string $productId, Context $context): ?ProductEntity
{
    $criteria = new Criteria([$productId]);

    // Loading all associations regardless of need - performance killer
    $criteria->addAssociation('manufacturer');
    $criteria->addAssociation('categories');
    $criteria->addAssociation('media');
    $criteria->addAssociation('cover');
    $criteria->addAssociation('prices');
    $criteria->addAssociation('properties');
    $criteria->addAssociation('options');
    $criteria->addAssociation('configuratorSettings');
    $criteria->addAssociation('crossSellings');
    $criteria->addAssociation('reviews');
    $criteria->addAssociation('mainCategories');
    $criteria->addAssociation('seoUrls');
    $criteria->addAssociation('translations');
    $criteria->addAssociation('customFieldSets');

    return $this->productRepository->search($criteria, $context)->first();
}

// Bad: Relying on lazy loading (deprecated in Shopware 6.6+)
public function displayProduct(ProductEntity $product): array
{
    // Assuming associations will load on access - unreliable
    return [
        'name' => $product->getName(),
        'manufacturer' => $product->getManufacturer()->getName(), // May fail
        'categories' => $product->getCategories()->count(), // May fail
    ];
}

// Bad: Not filtering nested associations
public function getProductWithAllMedia(string $productId, Context $context): ?ProductEntity
{
    $criteria = new Criteria([$productId]);
    $criteria->addAssociation('media'); // Loads ALL media without filtering

    return $this->productRepository->search($criteria, $context)->first();
}
```

### Correct

```php
// Good: Explicitly load required associations
public function getProductManufacturerName(string $productId, Context $context): ?string
{
    $criteria = new Criteria([$productId]);
    $criteria->addAssociation('manufacturer');

    $product = $this->productRepository->search($criteria, $context)->first();

    return $product?->getManufacturer()?->getName();
}

// Good: Load associations with the main query
public function getProductsWithManufacturers(Context $context): EntitySearchResult
{
    $criteria = new Criteria();
    $criteria->addAssociation('manufacturer');
    $criteria->setLimit(100);

    // Single query with JOIN - no N+1 problem
    return $this->productRepository->search($criteria, $context);
}

// Good: Load only needed associations for the use case
public function getProductForDetailPage(string $productId, Context $context): ?ProductEntity
{
    $criteria = new Criteria([$productId]);

    // Only load what's needed for the detail page
    $criteria->addAssociation('manufacturer');
    $criteria->addAssociation('cover.media');
    $criteria->addAssociation('media.media');
    $criteria->addAssociation('properties.group');

    return $this->productRepository->search($criteria, $context)->first();
}

// Good: Use addAssociationPath for nested associations
public function getProductWithCategoryTree(string $productId, Context $context): ?ProductEntity
{
    $criteria = new Criteria([$productId]);

    // Load categories and their parent categories
    $criteria->addAssociation('categories.parent.parent');

    return $this->productRepository->search($criteria, $context)->first();
}

// Good: Filter associations with getAssociation()
public function getProductWithActiveMedia(string $productId, Context $context): ?ProductEntity
{
    $criteria = new Criteria([$productId]);

    $criteria->addAssociation('media');
    $criteria->getAssociation('media')
        ->addFilter(new EqualsFilter('media.private', false))
        ->addSorting(new FieldSorting('position', FieldSorting::ASCENDING))
        ->setLimit(10);

    return $this->productRepository->search($criteria, $context)->first();
}

// Good: Limit associations for list views
public function getProductsForListing(Context $context, int $limit = 24): EntitySearchResult
{
    $criteria = new Criteria();
    $criteria->setLimit($limit);

    // Only load minimal associations for listing
    $criteria->addAssociation('cover.media');
    $criteria->addAssociation('manufacturer');

    // Don't load heavy associations like all media, reviews, etc.

    return $this->productRepository->search($criteria, $context);
}

// Good: Use association criteria for complex filtering
public function getProductsWithHighRatedReviews(Context $context): EntitySearchResult
{
    $criteria = new Criteria();
    $criteria->setLimit(50);

    $criteria->addAssociation('reviews');
    $criteria->getAssociation('reviews')
        ->addFilter(new RangeFilter('points', [RangeFilter::GTE => 4]))
        ->addFilter(new EqualsFilter('status', true))
        ->setLimit(5);

    return $this->productRepository->search($criteria, $context);
}

// Good: Separate queries for truly independent data
public function getProductAndRelatedData(string $productId, Context $context): array
{
    // Main product with essential associations
    $productCriteria = new Criteria([$productId]);
    $productCriteria->addAssociation('manufacturer');
    $productCriteria->addAssociation('cover.media');

    $product = $this->productRepository->search($productCriteria, $context)->first();

    if (!$product) {
        return [];
    }

    // Separate query for reviews (potentially large dataset)
    $reviewCriteria = new Criteria();
    $reviewCriteria->addFilter(new EqualsFilter('productId', $productId));
    $reviewCriteria->addFilter(new EqualsFilter('status', true));
    $reviewCriteria->addSorting(new FieldSorting('createdAt', FieldSorting::DESCENDING));
    $reviewCriteria->setLimit(10);

    $reviews = $this->reviewRepository->search($reviewCriteria, $context);

    return [
        'product' => $product,
        'reviews' => $reviews
    ];
}

// Good: Check if association is loaded before accessing
public function safelyAccessManufacturer(ProductEntity $product): ?string
{
    $manufacturer = $product->getManufacturer();

    if ($manufacturer === null) {
        // Association wasn't loaded or doesn't exist
        return null;
    }

    return $manufacturer->getName();
}

// Good: Using addAssociations() for multiple simple associations
public function getOrderWithDetails(string $orderId, Context $context): ?OrderEntity
{
    $criteria = new Criteria([$orderId]);

    $criteria->addAssociations([
        'lineItems.product',
        'lineItems.cover',
        'deliveries.shippingMethod',
        'transactions.paymentMethod',
        'currency',
        'salesChannel'
    ]);

    return $this->orderRepository->search($criteria, $context)->first();
}

// Good: Conditional association loading based on context
public function getProduct(string $productId, Context $context, bool $includeMedia = false): ?ProductEntity
{
    $criteria = new Criteria([$productId]);
    $criteria->addAssociation('manufacturer');

    if ($includeMedia) {
        $criteria->addAssociation('media.media');
        $criteria->addAssociation('cover.media');
    }

    return $this->productRepository->search($criteria, $context)->first();
}
```
