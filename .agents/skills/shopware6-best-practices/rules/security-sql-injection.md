---
title: Prevent SQL Injection
impact: CRITICAL
impactDescription: prevents database compromise and data theft
tags: security, sql, injection, dal, database, dbal
---

## Prevent SQL Injection

**Impact: CRITICAL (prevents database compromise and data theft)**

SQL injection is one of the most severe security vulnerabilities. Always use Shopware's Data Abstraction Layer (DAL) for database operations. When raw SQL is necessary, use parameterized queries with DBAL. Never concatenate user input into SQL strings.

**Incorrect (vulnerable to SQL injection):**

```php
// Bad: String concatenation in SQL query
class ProductSearchService
{
    public function __construct(
        private readonly Connection $connection
    ) {
    }

    public function searchProducts(string $searchTerm): array
    {
        // Bad: Direct string concatenation - SQL injection vulnerability!
        $sql = "SELECT * FROM product WHERE name LIKE '%" . $searchTerm . "%'";
        return $this->connection->fetchAllAssociative($sql);
    }
}
```

```php
// Bad: User input in ORDER BY without validation
class ProductListService
{
    public function getProducts(string $sortField, string $sortDirection): array
    {
        // Bad: Unvalidated input in ORDER BY clause
        $sql = "SELECT * FROM product ORDER BY " . $sortField . " " . $sortDirection;
        return $this->connection->fetchAllAssociative($sql);
    }
}
```

```php
// Bad: Using sprintf or string interpolation
class OrderService
{
    public function getOrdersByStatus(string $status): array
    {
        // Bad: sprintf is just as dangerous as concatenation
        $sql = sprintf("SELECT * FROM `order` WHERE status = '%s'", $status);
        return $this->connection->fetchAllAssociative($sql);

        // Also bad: string interpolation
        $sql = "SELECT * FROM `order` WHERE status = '$status'";
    }
}
```

```php
// Bad: Building IN clause unsafely
class CustomerService
{
    public function getCustomersByIds(array $ids): array
    {
        // Bad: Imploding user input directly
        $idList = implode("','", $ids);
        $sql = "SELECT * FROM customer WHERE id IN ('$idList')";
        return $this->connection->fetchAllAssociative($sql);
    }
}
```

**Correct (using DAL and parameterized queries):**

```php
// Good: Using Shopware DAL (recommended approach)
use Shopware\Core\Framework\DataAbstractionLayer\EntityRepository;
use Shopware\Core\Framework\DataAbstractionLayer\Search\Criteria;
use Shopware\Core\Framework\DataAbstractionLayer\Search\Filter\ContainsFilter;
use Shopware\Core\Framework\DataAbstractionLayer\Search\Filter\EqualsFilter;
use Shopware\Core\Framework\DataAbstractionLayer\Search\Filter\EqualsAnyFilter;
use Shopware\Core\Framework\DataAbstractionLayer\Search\Sorting\FieldSorting;

class ProductSearchService
{
    public function __construct(
        private readonly EntityRepository $productRepository
    ) {
    }

    public function searchProducts(string $searchTerm, Context $context): EntitySearchResult
    {
        // Good: DAL handles all escaping and parameterization
        $criteria = new Criteria();
        $criteria->addFilter(new ContainsFilter('name', $searchTerm));

        return $this->productRepository->search($criteria, $context);
    }
}
```

```php
// Good: DAL with validated sorting
class ProductListService
{
    private const ALLOWED_SORT_FIELDS = ['name', 'price', 'stock', 'createdAt'];
    private const ALLOWED_SORT_DIRECTIONS = [FieldSorting::ASCENDING, FieldSorting::DESCENDING];

    public function __construct(
        private readonly EntityRepository $productRepository
    ) {
    }

    public function getProducts(string $sortField, string $sortDirection, Context $context): EntitySearchResult
    {
        // Good: Whitelist validation for dynamic fields
        if (!in_array($sortField, self::ALLOWED_SORT_FIELDS, true)) {
            $sortField = 'name';
        }

        if (!in_array($sortDirection, self::ALLOWED_SORT_DIRECTIONS, true)) {
            $sortDirection = FieldSorting::ASCENDING;
        }

        $criteria = new Criteria();
        $criteria->addSorting(new FieldSorting($sortField, $sortDirection));

        return $this->productRepository->search($criteria, $context);
    }
}
```

```php
// Good: Parameterized DBAL queries when raw SQL is necessary
use Doctrine\DBAL\Connection;
use Doctrine\DBAL\ArrayParameterType;

class ReportService
{
    public function __construct(
        private readonly Connection $connection
    ) {
    }

    public function getOrdersByStatus(string $status): array
    {
        // Good: Named parameter with explicit type
        $sql = 'SELECT * FROM `order` WHERE status = :status';

        return $this->connection->fetchAllAssociative($sql, [
            'status' => $status
        ], [
            'status' => \PDO::PARAM_STR
        ]);
    }

    public function getCustomersByIds(array $ids): array
    {
        // Good: Using DBAL's ArrayParameterType for IN clauses
        $sql = 'SELECT * FROM customer WHERE id IN (:ids)';

        return $this->connection->fetchAllAssociative($sql, [
            'ids' => $ids
        ], [
            'ids' => ArrayParameterType::STRING
        ]);
    }

    public function getOrdersInDateRange(\DateTimeInterface $start, \DateTimeInterface $end): array
    {
        // Good: Proper parameter binding for dates
        $sql = 'SELECT * FROM `order` WHERE created_at BETWEEN :start AND :end';

        return $this->connection->fetchAllAssociative($sql, [
            'start' => $start->format('Y-m-d H:i:s'),
            'end' => $end->format('Y-m-d H:i:s'),
        ]);
    }
}
```

```php
// Good: Using QueryBuilder for complex queries
use Doctrine\DBAL\Connection;

class AnalyticsService
{
    public function __construct(
        private readonly Connection $connection
    ) {
    }

    public function getProductSalesReport(array $productIds, string $status): array
    {
        // Good: QueryBuilder with proper parameter binding
        $qb = $this->connection->createQueryBuilder();

        $qb->select('p.id', 'p.name', 'SUM(oli.quantity) as total_sold')
           ->from('product', 'p')
           ->innerJoin('p', 'order_line_item', 'oli', 'p.id = oli.product_id')
           ->innerJoin('oli', '`order`', 'o', 'oli.order_id = o.id')
           ->where($qb->expr()->in('p.id', ':productIds'))
           ->andWhere('o.status = :status')
           ->groupBy('p.id', 'p.name')
           ->setParameter('productIds', $productIds, ArrayParameterType::STRING)
           ->setParameter('status', $status);

        return $qb->executeQuery()->fetchAllAssociative();
    }
}
```

```php
// Good: Safe LIKE queries with proper escaping
class SearchService
{
    public function __construct(
        private readonly Connection $connection
    ) {
    }

    public function searchByName(string $term): array
    {
        // Good: Escape LIKE wildcards and use parameters
        $escapedTerm = addcslashes($term, '%_');

        $sql = 'SELECT * FROM product WHERE name LIKE :term';

        return $this->connection->fetchAllAssociative($sql, [
            'term' => '%' . $escapedTerm . '%'
        ]);
    }
}
```

```php
// Good: Using DAL aggregations instead of raw SQL
use Shopware\Core\Framework\DataAbstractionLayer\Search\Aggregation\Metric\SumAggregation;
use Shopware\Core\Framework\DataAbstractionLayer\Search\Aggregation\Bucket\TermsAggregation;

class SalesReportService
{
    public function __construct(
        private readonly EntityRepository $orderLineItemRepository
    ) {
    }

    public function getProductSales(Context $context): array
    {
        // Good: DAL aggregations are safe and performant
        $criteria = new Criteria();
        $criteria->addAggregation(
            new TermsAggregation(
                'products',
                'productId',
                null,
                null,
                new SumAggregation('total', 'quantity')
            )
        );

        $result = $this->orderLineItemRepository->search($criteria, $context);

        return $result->getAggregations()->get('products')->getBuckets();
    }
}
```

**Safe database query patterns:**

| Approach | When to Use | Safety Level |
|----------|-------------|--------------|
| DAL Criteria | Standard CRUD operations | Highest |
| DAL Aggregations | Reporting and analytics | Highest |
| QueryBuilder | Complex joins, custom SQL | High (with params) |
| Parameterized DBAL | Performance-critical raw SQL | High |
| Raw SQL | Never with user input | Avoid |

Reference: [Data Abstraction Layer](https://developer.shopware.com/docs/guides/plugins/plugins/framework/data-handling/reading-data) | [OWASP SQL Injection Prevention](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)
