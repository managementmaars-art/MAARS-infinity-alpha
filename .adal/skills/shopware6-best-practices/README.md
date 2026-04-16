# Shopware 6 Best Practices

Comprehensive best practices for Shopware 6.6+ backend development, optimized for AI-assisted code generation and review.

## Overview

This skill provides 36 rules across 14 categories for Shopware 6 plugin development. Rules are prioritized by impact from CRITICAL (plugin architecture, security) to MEDIUM (logging, configuration).

## Target Version

- **Shopware 6.6+** (PHP 8.1+, Symfony 6+)
- Uses PHP 8 attributes (`#[Route]`, `#[AsMessageHandler]`)
- Modern DAL patterns and Flow Builder integration

## Focus Areas

This skill focuses on **backend PHP development**:

- Plugin architecture and lifecycle
- Data Abstraction Layer (DAL) usage
- Store API and Admin API development
- Event subscribers and decorators
- Message queue and scheduled tasks
- Security best practices
- Testing patterns

## Quick Start

1. Read `SKILL.md` for the complete rule reference
2. Check individual rules in `rules/` for detailed examples
3. Use `AGENTS.md` for the full compiled guide

## Key Patterns

### Decorator Pattern (Service Customization)
```php
class DecoratedService extends AbstractOriginalService
{
    public function __construct(
        private readonly AbstractOriginalService $decorated
    ) {}

    public function getDecorated(): AbstractOriginalService
    {
        return $this->decorated;
    }
}
```

### Event Subscriber
```php
class MySubscriber implements EventSubscriberInterface
{
    public static function getSubscribedEvents(): array
    {
        return [
            ProductEvents::PRODUCT_LOADED_EVENT => 'onProductLoaded',
        ];
    }
}
```

### DAL Query
```php
$criteria = new Criteria();
$criteria->addFilter(new EqualsFilter('active', true));
$criteria->addAssociation('manufacturer');
$criteria->setLimit(50);

$products = $this->productRepository->search($criteria, $context);
```

## Rule Categories

| Category | Count | Priority |
|----------|-------|----------|
| Plugin Architecture | 2 | CRITICAL |
| Customization | 2 | CRITICAL |
| Performance | 3 | CRITICAL |
| Security | 5 | CRITICAL |
| DAL | 5 | HIGH |
| API | 5 | HIGH |
| Testing | 4 | HIGH |
| Events | 2 | MEDIUM-HIGH |
| Database | 1 | MEDIUM-HIGH |
| Queue | 3 | MEDIUM |
| DI | 1 | MEDIUM |
| Logging | 1 | MEDIUM |
| Config | 1 | MEDIUM |
| Scheduled | 1 | MEDIUM |

## Resources

- [Shopware Developer Documentation](https://developer.shopware.com/docs/)
- [Plugin Base Guide](https://developer.shopware.com/docs/guides/plugins/plugins/plugin-base-guide.html)
- [DAL Documentation](https://developer.shopware.com/docs/concepts/framework/data-abstraction-layer.html)
- [API Concepts](https://developer.shopware.com/docs/concepts/api/)

## License

MIT
