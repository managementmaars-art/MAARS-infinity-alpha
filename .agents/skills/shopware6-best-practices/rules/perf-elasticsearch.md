---
title: Use Elasticsearch Correctly for Large Catalogs
impact: CRITICAL
impactDescription: enables scalable search and filtering for 10K+ products
tags: performance, elasticsearch, search, scalability
---

## Use Elasticsearch Correctly for Large Catalogs

**Impact: CRITICAL (enables scalable search and filtering for 10K+ products)**

For catalogs with 10,000+ products, Elasticsearch offloads search, filtering, and aggregations from MySQL. Proper configuration prevents fallback to MySQL under load.

**Incorrect (Elasticsearch anti-patterns):**

```php
// Bad: Not checking if ES is enabled
class ProductSearchService
{
    public function search(string $term, Context $context): EntitySearchResult
    {
        $criteria = new Criteria();
        $criteria->addFilter(new ContainsFilter('name', $term));

        // Always hits MySQL, ignores ES even if configured!
        return $this->productRepository->search($criteria, $context);
    }
}

// Bad: Bypassing ES for complex filters
class ProductFilterService
{
    public function filterProducts(array $filters, Context $context): array
    {
        // Bad: Raw SQL query bypasses ES entirely
        $sql = "SELECT * FROM product WHERE " . $this->buildFilterSql($filters);

        return $this->connection->fetchAllAssociative($sql);
    }
}

// Bad: ES configuration without exception handling
# .env
SHOPWARE_ES_ENABLED=1
SHOPWARE_ES_INDEXING_ENABLED=1
# Missing SHOPWARE_ES_THROW_EXCEPTION - silent fallback to MySQL!
```

```yaml
# Bad: No ES hosts configured
shopware:
    elasticsearch:
        enabled: true
        # Missing hosts configuration!
```

**Correct (proper Elasticsearch usage):**

```env
# Good: Complete ES environment configuration
SHOPWARE_ES_ENABLED=1
SHOPWARE_ES_INDEXING_ENABLED=1
SHOPWARE_ES_THROW_EXCEPTION=1
OPENSEARCH_URL=http://elasticsearch:9200
```

```yaml
# Good: Complete ES configuration in config/packages/shopware.yaml
shopware:
    elasticsearch:
        enabled: true
        indexing_enabled: true
        throw_exception: true
        hosts: "%env(OPENSEARCH_URL)%"
        index_prefix: "sw"
        index_settings:
            number_of_shards: 3
            number_of_replicas: 1
        analysis:
            analyzer:
                custom_analyzer:
                    type: custom
                    tokenizer: standard
                    filter:
                        - lowercase
                        - asciifolding
```

```php
// Good: Using ES-aware product listing
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\Service;

use Shopware\Core\Content\Product\SalesChannel\Listing\AbstractProductListingRoute;
use Shopware\Core\Content\Product\SalesChannel\Listing\ProductListingResult;
use Shopware\Core\Content\Product\SalesChannel\Search\AbstractProductSearchRoute;
use Shopware\Core\Framework\DataAbstractionLayer\Search\Criteria;
use Shopware\Core\System\SalesChannel\SalesChannelContext;
use Symfony\Component\HttpFoundation\Request;

class ProductSearchService
{
    public function __construct(
        private readonly AbstractProductSearchRoute $searchRoute,
        private readonly AbstractProductListingRoute $listingRoute
    ) {}

    // Good: Use the search route which respects ES configuration
    public function search(string $term, SalesChannelContext $context): ProductListingResult
    {
        $request = new Request(['search' => $term]);
        $criteria = new Criteria();
        $criteria->setLimit(24);

        // Good: AbstractProductSearchRoute uses ES when enabled
        return $this->searchRoute->load($request, $context, $criteria)->getListingResult();
    }

    // Good: Use listing route for filtering
    public function filterByCategory(string $categoryId, SalesChannelContext $context): ProductListingResult
    {
        $request = new Request();
        $criteria = new Criteria();

        // Good: Uses ES for aggregations and filtering
        return $this->listingRoute->load($categoryId, $request, $context, $criteria)->getResult();
    }
}
```

```php
// Good: Custom ES-aware product searcher
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\Elasticsearch;

use Shopware\Elasticsearch\Framework\ElasticsearchHelper;
use Shopware\Core\Content\Product\ProductDefinition;
use Shopware\Core\Framework\DataAbstractionLayer\Search\Criteria;
use Shopware\Core\Framework\Context;

class CustomProductSearch
{
    public function __construct(
        private readonly ElasticsearchHelper $elasticsearchHelper,
        private readonly ProductDefinition $productDefinition,
        private readonly EntityRepository $productRepository
    ) {}

    public function search(Criteria $criteria, Context $context): EntitySearchResult
    {
        // Good: Check if ES should be used
        if ($this->elasticsearchHelper->allowSearch($this->productDefinition, $context, $criteria)) {
            // ES will be used automatically
            return $this->productRepository->search($criteria, $context);
        }

        // Fallback handling for when ES is disabled
        $this->logger->warning('Elasticsearch not available, falling back to MySQL');
        return $this->productRepository->search($criteria, $context);
    }
}
```

```php
// Good: Custom field indexing for ES
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\Elasticsearch;

use Shopware\Elasticsearch\Product\AbstractProductSearchQueryBuilder;
use Shopware\Elasticsearch\Product\ProductSearchQueryBuilder;
use OpenSearchDSL\Query\Compound\BoolQuery;
use OpenSearchDSL\Query\FullText\MatchQuery;

class CustomProductSearchQueryBuilder extends AbstractProductSearchQueryBuilder
{
    public function __construct(
        private readonly AbstractProductSearchQueryBuilder $decorated
    ) {}

    public function getDecorated(): AbstractProductSearchQueryBuilder
    {
        return $this->decorated;
    }

    public function build(Criteria $criteria, Context $context): BoolQuery
    {
        $query = $this->decorated->build($criteria, $context);

        // Good: Add custom field to search
        $searchTerm = $criteria->getTerm();
        if ($searchTerm !== null) {
            $query->add(
                new MatchQuery('customFields.my_custom_field', $searchTerm),
                BoolQuery::SHOULD
            );
        }

        return $query;
    }
}
```

```php
// Good: Monitoring ES health
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\Command;

use OpenSearch\Client;
use Symfony\Component\Console\Command\Command;

class ElasticsearchHealthCommand extends Command
{
    protected static $defaultName = 'my-plugin:es-health';

    public function __construct(
        private readonly Client $client
    ) {
        parent::__construct();
    }

    protected function execute(InputInterface $input, OutputInterface $output): int
    {
        $health = $this->client->cluster()->health();

        $output->writeln(sprintf('Cluster: %s', $health['cluster_name']));
        $output->writeln(sprintf('Status: %s', $health['status']));
        $output->writeln(sprintf('Nodes: %d', $health['number_of_nodes']));
        $output->writeln(sprintf('Shards: %d active', $health['active_shards']));

        if ($health['status'] === 'red') {
            $output->writeln('<error>Cluster is in RED status!</error>');
            return Command::FAILURE;
        }

        return Command::SUCCESS;
    }
}
```

**ES configuration checklist:**

| Setting | Production Value | Purpose |
|---------|------------------|---------|
| `SHOPWARE_ES_ENABLED` | `1` | Enable ES for search |
| `SHOPWARE_ES_INDEXING_ENABLED` | `1` | Enable ES indexing |
| `SHOPWARE_ES_THROW_EXCEPTION` | `1` | Fail instead of MySQL fallback |
| `number_of_shards` | 3-5 | Parallelism (can't change later) |
| `number_of_replicas` | 1-2 | Redundancy |

Reference: [Elasticsearch Configuration](https://developer.shopware.com/docs/guides/hosting/infrastructure/elasticsearch/elasticsearch-setup.html)
