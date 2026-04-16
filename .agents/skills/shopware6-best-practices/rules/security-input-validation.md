---
title: Validate and Sanitize All Input
impact: CRITICAL
impactDescription: prevents injection attacks and data corruption
tags: security, validation, input, sanitization, request
---

## Validate and Sanitize All Input

**Impact: CRITICAL (prevents injection attacks and data corruption)**

All user input must be validated and sanitized before processing. Shopware 6 provides RequestDataBag for structured request handling and integrates with Symfony's validation system. Never trust raw request data.

**Incorrect (using raw request data without validation):**

```php
// Bad: Directly accessing raw request parameters without validation
class ProductController extends AbstractController
{
    #[Route(path: '/api/product/update', name: 'api.product.update', methods: ['POST'])]
    public function updateProduct(Request $request): Response
    {
        $productId = $request->get('id');
        $price = $request->get('price');
        $description = $request->get('description');

        // Bad: No type checking, no validation, potential XSS and injection
        $this->productRepository->update([
            [
                'id' => $productId,
                'price' => $price,
                'description' => $description,
            ]
        ], Context::createDefaultContext());

        return new JsonResponse(['success' => true]);
    }
}
```

```php
// Bad: Using user input directly in business logic
class OrderService
{
    public function processDiscount(Request $request): void
    {
        // Bad: User can manipulate discount percentage
        $discount = $request->request->get('discount');
        $this->applyDiscount($discount);
    }
}
```

**Correct (using RequestDataBag and proper validation):**

```php
// Good: Using RequestDataBag with proper type handling and validation
use Shopware\Core\Framework\Validation\DataBag\RequestDataBag;
use Shopware\Core\Framework\Validation\DataValidationDefinition;
use Shopware\Core\Framework\Validation\DataValidator;
use Symfony\Component\Validator\Constraints as Assert;

class ProductController extends AbstractController
{
    public function __construct(
        private readonly DataValidator $validator,
        private readonly EntityRepository $productRepository
    ) {
    }

    #[Route(path: '/api/product/update', name: 'api.product.update', methods: ['POST'])]
    public function updateProduct(RequestDataBag $data, Context $context): Response
    {
        // Good: Define validation rules
        $definition = new DataValidationDefinition('product.update');
        $definition
            ->add('id', new Assert\NotBlank(), new Assert\Uuid())
            ->add('price', new Assert\NotBlank(), new Assert\Type('numeric'), new Assert\Positive())
            ->add('description', new Assert\Length(['max' => 5000]));

        // Good: Validate input before processing
        $this->validator->validate($data->all(), $definition);

        // Good: Use typed getters
        $productId = $data->get('id');
        $price = (float) $data->get('price');
        $description = strip_tags($data->get('description', ''));

        $this->productRepository->update([
            [
                'id' => $productId,
                'price' => [['currencyId' => Defaults::CURRENCY, 'gross' => $price, 'net' => $price, 'linked' => false]],
                'description' => htmlspecialchars($description, ENT_QUOTES, 'UTF-8'),
            ]
        ], $context);

        return new JsonResponse(['success' => true]);
    }
}
```

```php
// Good: Using Symfony constraints with custom validation
use Shopware\Core\Framework\Validation\BuildValidationEvent;
use Symfony\Component\EventDispatcher\EventSubscriberInterface;

class ValidationSubscriber implements EventSubscriberInterface
{
    public static function getSubscribedEvents(): array
    {
        return [
            'framework.validation.product.update' => 'onProductUpdate',
        ];
    }

    public function onProductUpdate(BuildValidationEvent $event): void
    {
        $definition = $event->getDefinition();

        // Good: Add custom validation constraints
        $definition->add('price', new Assert\Range(['min' => 0, 'max' => 1000000]));
        $definition->add('stock', new Assert\Type('integer'), new Assert\PositiveOrZero());
    }
}
```

```php
// Good: Type-safe request handling in Storefront controllers
use Shopware\Storefront\Controller\StorefrontController;

class CustomStorefrontController extends StorefrontController
{
    #[Route(path: '/custom/search', name: 'frontend.custom.search', methods: ['GET', 'POST'])]
    public function search(Request $request, SalesChannelContext $context): Response
    {
        // Good: Use typed extraction with defaults
        $term = $request->query->getString('term', '');
        $page = $request->query->getInt('page', 1);
        $limit = min($request->query->getInt('limit', 20), 100); // Enforce max limit

        // Good: Sanitize search term
        $term = trim(strip_tags($term));

        if (mb_strlen($term) < 3) {
            throw new InvalidArgumentException('Search term must be at least 3 characters');
        }

        // Process with validated data
        return $this->renderStorefront('@MyPlugin/search.html.twig', [
            'results' => $this->searchService->search($term, $page, $limit, $context),
        ]);
    }
}
```

**Common validation constraints:**

| Constraint | Purpose |
|------------|---------|
| `Assert\NotBlank()` | Field must have a value |
| `Assert\Uuid()` | Valid UUID format |
| `Assert\Email()` | Valid email address |
| `Assert\Length(['min' => x, 'max' => y])` | String length bounds |
| `Assert\Range(['min' => x, 'max' => y])` | Numeric range |
| `Assert\Choice(['choices' => [...]])` | Value from allowed list |
| `Assert\Type('numeric')` | Type validation |
| `Assert\Regex(['pattern' => '...'])` | Pattern matching |

Reference: [Symfony Validation](https://symfony.com/doc/current/validation.html) | [Shopware DataValidator](https://developer.shopware.com/docs/guides/plugins/plugins/framework/data-handling/data-validation)
