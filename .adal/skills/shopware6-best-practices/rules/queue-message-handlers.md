---
title: Message Queue Handler Implementation
impact: MEDIUM
impactDescription: Improper message handling leads to synchronous bottlenecks, blocking requests, and poor scalability under load.
tags: [shopware6, message-queue, async, handlers, performance]
---

## Use Proper Message Classes and Handlers for Async Processing

Shopware 6 uses Symfony Messenger for asynchronous message processing. Create dedicated message classes and handlers to offload heavy operations from HTTP requests.

Reference: https://developer.shopware.com/docs/guides/plugins/plugins/framework/message-queue/add-message-handler

### Incorrect

```php
// Bad: Processing heavy operations synchronously in a controller
class ProductImportController extends AbstractController
{
    public function __construct(
        private readonly EntityRepository $productRepository,
        private readonly Connection $connection
    ) {
    }

    #[Route(path: '/api/import/products', name: 'api.import.products', methods: ['POST'])]
    public function import(Request $request, Context $context): JsonResponse
    {
        $products = json_decode($request->getContent(), true);

        // Bad: Processing thousands of products in a single HTTP request
        foreach ($products as $productData) {
            $this->productRepository->upsert([$productData], $context);

            // Bad: Heavy image processing blocks the request
            $this->processProductImages($productData);

            // Bad: External API calls during request
            $this->syncToExternalSystem($productData);
        }

        return new JsonResponse(['status' => 'completed']);
    }
}

// Bad: No message class defined for async processing
// Bad: No handler registered for background tasks
```

### Correct

```php
// Good: Define a message class for async processing
// src/MessageQueue/Message/ProductImportMessage.php
class ProductImportMessage
{
    public function __construct(
        private readonly array $productData,
        private readonly string $contextToken
    ) {
    }

    public function getProductData(): array
    {
        return $this->productData;
    }

    public function getContextToken(): string
    {
        return $this->contextToken;
    }
}

// Good: Create a dedicated handler for the message
// src/MessageQueue/Handler/ProductImportHandler.php
#[AsMessageHandler]
class ProductImportHandler
{
    public function __construct(
        private readonly EntityRepository $productRepository,
        private readonly ProductImageProcessor $imageProcessor,
        private readonly ExternalSyncService $syncService,
        private readonly SalesChannelContextFactory $contextFactory
    ) {
    }

    public function __invoke(ProductImportMessage $message): void
    {
        $context = $this->contextFactory->create($message->getContextToken());
        $productData = $message->getProductData();

        // Good: Process in background without blocking HTTP request
        $this->productRepository->upsert([$productData], $context->getContext());
        $this->imageProcessor->process($productData);
        $this->syncService->sync($productData);
    }
}

// Good: Controller dispatches messages for async processing
class ProductImportController extends AbstractController
{
    public function __construct(
        private readonly MessageBusInterface $messageBus
    ) {
    }

    #[Route(path: '/api/import/products', name: 'api.import.products', methods: ['POST'])]
    public function import(Request $request, SalesChannelContext $context): JsonResponse
    {
        $products = json_decode($request->getContent(), true);

        // Good: Dispatch messages for background processing
        foreach ($products as $productData) {
            $this->messageBus->dispatch(
                new ProductImportMessage($productData, $context->getToken())
            );
        }

        // Good: Immediate response, processing happens async
        return new JsonResponse([
            'status' => 'queued',
            'count' => count($products)
        ]);
    }
}

// Good: Register handler in services.xml (automatic with #[AsMessageHandler])
// <service id="MyPlugin\MessageQueue\Handler\ProductImportHandler">
//     <tag name="messenger.message_handler"/>
// </service>
```
