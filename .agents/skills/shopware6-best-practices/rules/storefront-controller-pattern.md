---
title: Storefront Controllers & Page Loading
impact: HIGH
impactDescription: ensures proper page rendering with SEO and caching support
tags: storefront, controller, page, loader, seo, cache
---

## Storefront Controllers & Page Loading

**Impact: HIGH (ensures proper page rendering with SEO and caching support)**

Storefront controllers must extend `StorefrontController` and use the page loader pattern for proper SEO metadata, breadcrumbs, and HTTP caching. Never directly render templates without loading page context.

**Incorrect (rendering template without page context):**

```php
// Bad: Directly rendering template without page loader
class CustomController extends AbstractController
{
    #[Route(path: '/custom/page', name: 'frontend.custom.page', methods: ['GET'])]
    public function showPage(Request $request): Response
    {
        // Bad: No page context, no header/footer, no SEO
        $products = $this->productRepository->search(new Criteria(), Context::createDefaultContext());

        return $this->render('@MyPlugin/storefront/page/custom.html.twig', [
            'products' => $products,
        ]);
    }
}
```

**Correct (using StorefrontController with page loader):**

```php
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\Storefront\Controller;

use Shopware\Storefront\Controller\StorefrontController;
use Shopware\Storefront\Page\GenericPageLoaderInterface;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;

#[Route(defaults: ['_routeScope' => ['storefront']])]
class CustomPageController extends StorefrontController
{
    public function __construct(
        private readonly GenericPageLoaderInterface $genericPageLoader,
        private readonly CustomPageLoader $customPageLoader
    ) {}

    #[Route(
        path: '/custom/page',
        name: 'frontend.custom.page',
        methods: ['GET'],
        defaults: ['_httpCache' => true]
    )]
    public function showPage(Request $request, SalesChannelContext $context): Response
    {
        // Good: Load page with full context (header, footer, SEO)
        $page = $this->customPageLoader->load($request, $context);

        return $this->renderStorefront('@MyPlugin/storefront/page/custom/index.html.twig', [
            'page' => $page,
        ]);
    }

    #[Route(
        path: '/custom/page/{productId}',
        name: 'frontend.custom.detail',
        methods: ['GET'],
        defaults: ['_httpCache' => true]
    )]
    public function detailPage(string $productId, Request $request, SalesChannelContext $context): Response
    {
        $page = $this->customPageLoader->loadDetail($productId, $request, $context);

        // Good: Set meta information for SEO
        $this->addMetaInformation($page);

        return $this->renderStorefront('@MyPlugin/storefront/page/custom/detail.html.twig', [
            'page' => $page,
        ]);
    }
}
```

**Correct page loader implementation:**

```php
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\Storefront\Page;

use Shopware\Core\System\SalesChannel\SalesChannelContext;
use Shopware\Storefront\Page\GenericPageLoaderInterface;
use Shopware\Storefront\Page\MetaInformation;
use Symfony\Component\EventDispatcher\EventDispatcherInterface;
use Symfony\Component\HttpFoundation\Request;

class CustomPageLoader
{
    public function __construct(
        private readonly GenericPageLoaderInterface $genericPageLoader,
        private readonly EntityRepository $productRepository,
        private readonly EventDispatcherInterface $eventDispatcher
    ) {}

    public function load(Request $request, SalesChannelContext $context): CustomPage
    {
        // Good: Start with generic page (includes header, footer, navigation)
        $page = $this->genericPageLoader->load($request, $context);
        $customPage = CustomPage::createFrom($page);

        // Load custom data
        $criteria = new Criteria();
        $criteria->setLimit(20);
        $criteria->addAssociation('cover');

        $products = $this->productRepository->search($criteria, $context->getContext());
        $customPage->setProducts($products);

        // Good: Set SEO meta information
        $meta = new MetaInformation();
        $meta->setMetaTitle('Custom Page Title');
        $meta->setMetaDescription('Description for search engines');
        $customPage->setMetaInformation($meta);

        // Good: Dispatch event for extensibility
        $this->eventDispatcher->dispatch(
            new CustomPageLoadedEvent($customPage, $context, $request)
        );

        return $customPage;
    }
}
```

**Correct page struct:**

```php
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\Storefront\Page;

use Shopware\Core\Framework\DataAbstractionLayer\Search\EntitySearchResult;
use Shopware\Storefront\Page\Page;

class CustomPage extends Page
{
    protected EntitySearchResult $products;

    public function getProducts(): EntitySearchResult
    {
        return $this->products;
    }

    public function setProducts(EntitySearchResult $products): void
    {
        $this->products = $products;
    }
}
```

**Route configuration in routes.xml:**

```xml
<?xml version="1.0" encoding="UTF-8" ?>
<routes xmlns="http://symfony.com/schema/routing"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://symfony.com/schema/routing
        https://symfony.com/schema/routing/routing-1.0.xsd">

    <import resource="../../Storefront/Controller/**/*Controller.php" type="attribute"/>
</routes>
```

**Common route defaults:**

| Default | Purpose |
|---------|---------|
| `_routeScope: ['storefront']` | Required for storefront routes |
| `_httpCache: true` | Enable HTTP caching for page |
| `_loginRequired: true` | Require customer login |
| `_loginRequiredAllowGuest: true` | Allow guest checkout |
| `_noStore: true` | Prevent caching (for dynamic pages) |

Reference: [Storefront Controller](https://developer.shopware.com/docs/guides/plugins/plugins/storefront/add-custom-controller.html)
